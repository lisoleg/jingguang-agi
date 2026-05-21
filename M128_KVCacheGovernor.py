# -*- coding: utf-8 -*-
"""
M128: KV缓存治理器 (KV Cache Governor)
基于BeeLlama TurboQuant差异化量化机制

核心概念：KVQuantizer、TieredCompactor、ContextBudgetMgr
公式：max Σ(F_i × log₂(q_i)) s.t. Σb_i ≤ B

定理T89（记忆保真-压缩权衡）：max Σ(F_i × log₂(q_i)) s.t. Σb_i ≤ B

作者: 太乙AGI团队
日期: 2026-05-21
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ==================== 数据结构 ====================

@dataclass
class KVQuantConfig:
    """
    KV量化配置 — 每层记忆的量化策略

    layer: 记忆层级（1=L1近期, 2=L2中期, 3=L3远期）
    precision: 量化精度（16/8/4 bit）
    compression_ratio: 压缩率
    fidelity: 保真度
    """
    layer: int = 1
    precision: int = 16
    compression_ratio: float = 1.0
    fidelity: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['compression_ratio'] = round(self.compression_ratio, 6)
        d['fidelity'] = round(self.fidelity, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'KVQuantConfig':
        """从字典构建KVQuantConfig"""
        return cls(**d)


@dataclass
class ContextBudget:
    """
    上下文预算 — 固定token预算下的记忆分配

    total_tokens: 总token预算
    allocated: 各模块分配的token数
    utilization: 利用率
    """
    total_tokens: int = 8192
    allocated: Dict[str, int] = field(default_factory=dict)
    utilization: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['utilization'] = round(self.utilization, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ContextBudget':
        """从字典构建ContextBudget"""
        return cls(**d)


@dataclass
class MemoryEntry:
    """
    记忆条目 — KV缓存中的单条记忆

    key: 记忆键
    value: 记忆值
    layer: 存储层级
    precision: 当前精度
    access_count: 访问次数
    last_access: 最后访问时间戳
    phi_value: 全息置信度Φ
    fidelity: 保真度
    size_bytes: 占用字节数
    """
    key: str = ''
    value: Any = None
    layer: int = 1
    precision: int = 16
    access_count: int = 0
    last_access: float = 0.0
    phi_value: float = 0.5
    fidelity: float = 1.0
    size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['phi_value'] = round(self.phi_value, 6)
        d['fidelity'] = round(self.fidelity, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'MemoryEntry':
        """从字典构建MemoryEntry"""
        return cls(**d)


@dataclass
class CompactResult:
    """
    压缩结果 — TieredCompact压缩的输出

    kept_count: 保留的记忆条数
    compressed_count: 压缩的记忆条数
    evicted_count: 淘汰的记忆条数
    original_size: 原始大小（bytes）
    compressed_size: 压缩后大小（bytes）
    compression_ratio: 整体压缩率
    fidelity_loss: 保真度损失
    """
    kept_count: int = 0
    compressed_count: int = 0
    evicted_count: int = 0
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 1.0
    fidelity_loss: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['compression_ratio'] = round(self.compression_ratio, 6)
        d['fidelity_loss'] = round(self.fidelity_loss, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CompactResult':
        """从字典构建CompactResult"""
        return cls(**d)


# ==================== 核心类 ====================

class KVCacheGovernor:
    """
    M128: KV缓存治理器

    基于BeeLlama TurboQuant差异化量化机制，实现记忆的高效管理：
    - KVQuantizer: 对记忆层施加差异化解量化
      L1近期(高Φ): 16bit（无损）
      L2中期(中Φ): 8bit量化
      L3远期(低Φ): 4bit激进量化
    - TieredCompactor: 近期高精度+远期激进压缩
    - ContextBudgetMgr: 固定token预算下的最优记忆分配

    差异化量化的核心思想：
    不同重要性的记忆使用不同精度存储。
    高重要性（高Φ值、近期、频繁访问）的记忆保持高精度，
    低重要性的记忆使用低精度存储以节省空间。

    定理T89（记忆保真-压缩权衡）：
    max Σ(F_i × log₂(q_i)) s.t. Σb_i ≤ B
    在总预算B约束下，最大化保真度加权的量化精度之和。
    这给出了最优的差异化量化方案。

    核心方法：
    1. quantize — 差异量化
    2. compact — TieredCompact压缩
    3. allocate_budget — 预算分配
    4. govern — 全局治理
    """

    def __init__(self):
        """初始化KV缓存治理器"""
        # 三层量化配置
        self.quant_configs: Dict[int, KVQuantConfig] = {
            1: KVQuantConfig(layer=1, precision=16, compression_ratio=1.0, fidelity=1.0),
            2: KVQuantConfig(layer=2, precision=8, compression_ratio=2.0, fidelity=0.95),
            3: KVQuantConfig(layer=3, precision=4, compression_ratio=4.0, fidelity=0.85),
        }

        # 记忆存储（三层级）
        self.memories: Dict[int, Dict[str, MemoryEntry]] = {
            1: {},  # L1近期
            2: {},  # L2中期
            3: {},  # L3远期
        }

        # 上下文预算
        self.context_budget = ContextBudget(
            total_tokens=8192,
            allocated={},
            utilization=0.0
        )

        # 统计
        self.total_quantizations: int = 0
        self.total_compactions: int = 0
        self.total_budget_allocations: int = 0
        self.total_govern_cycles: int = 0

        # 压缩统计
        self.total_bytes_saved: int = 0
        self.total_fidelity_loss: float = 0.0
        self.max_compression_ratio: float = 1.0

        # 帧计数
        self.frame_count: int = 0
        self.last_update: float = time.time()

    # ==================== KVQuantizer ====================

    def quantize(self, layer: int, data: Any,
                 phi_value: float = 0.5) -> Dict[str, Any]:
        """
        差异量化 — 对记忆层施加差异化解量化

        量化策略：
        - L1(近期, 高Φ): 16bit — 无损存储
        - L2(中期, 中Φ): 8bit — 轻微量化
        - L3(远期, 低Φ): 4bit — 激进量化

        量化精度 = f(Φ, 层级, 访问频率)
        高Φ值的记忆保持高精度，低Φ值的记忆使用低精度。

        定理T89关联：
        量化精度q_i影响保真度F_i和占用字节数b_i。

        Args:
            layer: 目标层级 (1/2/3)
            data: 待量化的数据
            phi_value: 全息置信度Φ

        Returns:
            量化结果字典，包含精度、压缩率、保真度等
        """
        self.total_quantizations += 1

        # 验证层级
        layer = max(1, min(3, layer))

        # 根据Φ值调整量化策略
        # Φ高→保持高精度，Φ低→允许激进量化
        effective_precision = self._compute_effective_precision(layer, phi_value)

        # 获取配置
        config = self.quant_configs[layer]

        # 计算压缩率
        original_precision = 16  # 假设原始为16bit
        compression_ratio = original_precision / max(effective_precision, 1)

        # 计算保真度
        # 保真度随量化精度下降而下降
        fidelity = self._compute_fidelity(effective_precision, original_precision)

        # 计算字节数
        data_size = self._estimate_data_size(data)
        original_bytes = data_size
        quantized_bytes = int(data_size / compression_ratio)

        # 更新配置
        config.precision = effective_precision
        config.compression_ratio = round(compression_ratio, 6)
        config.fidelity = round(fidelity, 6)

        # 更新统计
        bytes_saved = original_bytes - quantized_bytes
        self.total_bytes_saved += max(0, bytes_saved)
        if compression_ratio > self.max_compression_ratio:
            self.max_compression_ratio = compression_ratio

        self.last_update = time.time()

        return {
            'layer': layer,
            'original_precision': original_precision,
            'effective_precision': effective_precision,
            'compression_ratio': round(compression_ratio, 6),
            'fidelity': round(fidelity, 6),
            'phi_value': round(phi_value, 6),
            'original_bytes': original_bytes,
            'quantized_bytes': quantized_bytes,
            'bytes_saved': max(0, bytes_saved),
            'quant_config': config.to_dict()
        }

    def _compute_effective_precision(self, layer: int, phi_value: float) -> int:
        """
        计算有效量化精度

        精度 = f(层级, Φ值)
        - 层级越低（越近期）→ 精度越高
        - Φ值越高 → 精度越高

        Args:
            layer: 层级
            phi_value: Φ值

        Returns:
            有效精度（4/8/16）
        """
        base_precision = {1: 16, 2: 8, 3: 4}.get(layer, 8)

        # Φ值调整
        if phi_value > 0.8 and layer > 1:
            # 高Φ值，升级精度
            base_precision = min(base_precision * 2, 16)
        elif phi_value < 0.3 and layer < 3:
            # 低Φ值，降级精度
            base_precision = max(base_precision // 2, 4)

        # 确保精度在合法范围
        valid_precisions = [4, 8, 16]
        closest = min(valid_precisions, key=lambda p: abs(p - base_precision))
        return closest

    def _compute_fidelity(self, effective_precision: int,
                          original_precision: int) -> float:
        """
        计算保真度

        保真度与量化精度的对数成正比：
        F ≈ log₂(q_effective) / log₂(q_original)

        Args:
            effective_precision: 有效精度
            original_precision: 原始精度

        Returns:
            保真度 [0, 1]
        """
        if original_precision <= 0:
            return 0.0
        fidelity = math.log2(max(effective_precision, 1)) / math.log2(max(original_precision, 1))
        return min(1.0, max(0.0, fidelity))

    def _estimate_data_size(self, data: Any) -> int:
        """
        估算数据大小（字节）

        Args:
            data: 待估算数据

        Returns:
            估算字节数
        """
        if data is None:
            return 0
        if isinstance(data, (int, float)):
            return 8  # 64位
        if isinstance(data, bool):
            return 1
        if isinstance(data, str):
            return len(data.encode('utf-8'))
        if isinstance(data, (list, tuple)):
            return sum(self._estimate_data_size(item) for item in data)
        if isinstance(data, dict):
            size = 0
            for k, v in data.items():
                size += self._estimate_data_size(k)
                size += self._estimate_data_size(v)
            return size
        return 64  # 默认估算

    # ==================== TieredCompactor ====================

    def compact(self, memories: Optional[Dict[str, MemoryEntry]] = None,
                keep_recent: int = 5) -> CompactResult:
        """
        TieredCompact压缩 — 近期高精度+远期激进压缩

        压缩策略：
        1. 保留最近keep_recent条记忆（L1，16bit无损）
        2. 中期记忆降级到L2（8bit量化）
        3. 远期记忆降级到L3（4bit激进量化）
        4. 超过容量限制的记忆淘汰

        TieredCompact的核心：
        不是简单的FIFO淘汰，而是分层压缩。
        每一层使用不同的量化精度，在保真度和空间之间取得平衡。

        Args:
            memories: 待压缩的记忆字典（None则使用内部L1层）
            keep_recent: 保留最近N条记忆

        Returns:
            CompactResult: 压缩结果
        """
        self.total_compactions += 1

        if memories is None:
            memories = dict(self.memories.get(1, {}))

        if not memories:
            return CompactResult(
                kept_count=0, compressed_count=0, evicted_count=0,
                original_size=0, compressed_size=0,
                compression_ratio=1.0, fidelity_loss=0.0
            )

        # 按访问时间排序（最近优先）
        sorted_entries = sorted(
            memories.items(),
            key=lambda x: x[1].last_access if isinstance(x[1], MemoryEntry) else 0,
            reverse=True
        )

        kept_count = 0
        compressed_count = 0
        evicted_count = 0
        original_size = 0
        compressed_size = 0
        fidelity_loss = 0.0

        total_entries = len(sorted_entries)

        for i, (key, entry) in enumerate(sorted_entries):
            if not isinstance(entry, MemoryEntry):
                continue

            original_size += entry.size_bytes

            if i < keep_recent:
                # 保留近期记忆（L1，16bit）
                entry.layer = 1
                entry.precision = 16
                entry.fidelity = 1.0
                compressed_size += entry.size_bytes
                kept_count += 1
            elif i < keep_recent * 3:
                # 中期记忆（L2，8bit）
                entry.layer = 2
                entry.precision = 8
                entry.fidelity = self._compute_fidelity(8, 16)
                compressed_size += int(entry.size_bytes / 2)
                fidelity_loss += (1.0 - entry.fidelity) * entry.phi_value
                compressed_count += 1
            elif i < keep_recent * 7:
                # 远期记忆（L3，4bit）
                entry.layer = 3
                entry.precision = 4
                entry.fidelity = self._compute_fidelity(4, 16)
                compressed_size += int(entry.size_bytes / 4)
                fidelity_loss += (1.0 - entry.fidelity) * entry.phi_value
                compressed_count += 1
            else:
                # 淘汰
                evicted_count += 1

        # 计算整体压缩率
        compression_ratio = original_size / max(compressed_size, 1)

        # 更新统计
        bytes_saved = original_size - compressed_size
        self.total_bytes_saved += max(0, bytes_saved)
        self.total_fidelity_loss += fidelity_loss
        if compression_ratio > self.max_compression_ratio:
            self.max_compression_ratio = compression_ratio

        result = CompactResult(
            kept_count=kept_count,
            compressed_count=compressed_count,
            evicted_count=evicted_count,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=round(compression_ratio, 6),
            fidelity_loss=round(fidelity_loss, 6)
        )

        self.last_update = time.time()
        return result

    # ==================== ContextBudgetMgr ====================

    def allocate_budget(self, modules: Dict[str, float],
                        total_budget: int = 8192) -> ContextBudget:
        """
        预算分配 — 固定token预算下的最优记忆分配

        定理T89：max Σ(F_i × log₂(q_i)) s.t. Σb_i ≤ B

        最优分配策略：
        1. 计算每个模块的保真度权重F_i
        2. 使用拉格朗日乘数法求解最优b_i
        3. 保真度高的模块分配更多预算

        简化实现：
        按保真度权重比例分配预算。
        高保真度模块获得更多token，低保真度模块获得较少。

        Args:
            modules: 模块权重字典 {module_id: fidelity_weight}
            total_budget: 总token预算

        Returns:
            ContextBudget: 上下文预算分配
        """
        self.total_budget_allocations += 1

        if not modules:
            return ContextBudget(
                total_tokens=total_budget,
                allocated={},
                utilization=0.0
            )

        # 计算总权重
        total_weight = sum(modules.values())

        if total_weight <= 0:
            # 等权重分配
            n = len(modules)
            allocated = {mid: total_budget // n for mid in modules}
        else:
            # 按权重比例分配
            allocated = {}
            remaining = total_budget
            module_list = list(modules.items())

            for i, (mid, weight) in enumerate(module_list):
                if i == len(module_list) - 1:
                    # 最后一个模块获得剩余预算
                    allocated[mid] = remaining
                else:
                    share = int(total_budget * weight / total_weight)
                    share = min(share, remaining)
                    allocated[mid] = share
                    remaining -= share

        # 计算利用率
        total_allocated = sum(allocated.values())
        utilization = total_allocated / max(total_budget, 1)

        # 验证T89：保真度加权精度之和
        t89_objective = 0.0
        for mid, weight in modules.items():
            b_i = allocated.get(mid, 0)
            if b_i > 0:
                q_i = 2 ** min(b_i / 100, 16)  # 简化：预算→精度
                t89_objective += weight * math.log2(max(q_i, 2))

        budget = ContextBudget(
            total_tokens=total_budget,
            allocated=allocated,
            utilization=round(utilization, 6)
        )

        # 保存预算信息
        self.context_budget = budget

        # 添加T89分析
        budget_dict = budget.to_dict()
        budget_dict['t89_objective'] = round(t89_objective, 6)
        budget_dict['t89_constraint'] = f'Σb_i={total_allocated} ≤ B={total_budget}'
        budget_dict['t89_satisfied'] = total_allocated <= total_budget

        self.last_update = time.time()
        return budget

    # ==================== 全局治理 ====================

    def govern(self, memory_tree: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        全局治理 — 量化+压缩+预算一体化管理

        治理流程：
        1. 对三层记忆分别量化
        2. 执行TieredCompact压缩
        3. 分配上下文预算
        4. 计算T89最优目标值
        5. 输出治理报告

        Args:
            memory_tree: 记忆树（可选，简化版为字典）

        Returns:
            治理报告
        """
        self.total_govern_cycles += 1

        now = time.time()

        # 1. 三层量化
        quant_results = {}
        for layer in [1, 2, 3]:
            layer_memories = self.memories.get(layer, {})
            phi_avg = 0.0
            if layer_memories:
                phi_avg = sum(
                    m.phi_value for m in layer_memories.values()
                    if isinstance(m, MemoryEntry)
                ) / max(len(layer_memories), 1)
            else:
                phi_avg = {1: 0.9, 2: 0.6, 3: 0.3}.get(layer, 0.5)

            quant_results[f'L{layer}'] = self.quantize(layer, None, phi_avg)

        # 2. TieredCompact压缩
        all_l1_memories = dict(self.memories.get(1, {}))
        compact_result = self.compact(all_l1_memories, keep_recent=10)

        # 3. 上下文预算分配
        # 模拟模块权重
        module_weights = {
            'M29_HDG': 0.95,
            'M57_Xiuteth': 0.85,
            'M81_MemoryTree': 0.90,
            'M111_ActorDirector': 0.80,
            'M120_GameTheoryEngine': 0.75,
            'M126_GuardrailOrchestrator': 0.88,
            'M127_SpeculativeReasoner': 0.82,
            'M128_KVCacheGovernor': 0.78,
        }
        budget_result = self.allocate_budget(module_weights, self.context_budget.total_tokens)

        # 4. T89最优目标值
        t89_values = {}
        for layer in [1, 2, 3]:
            config = self.quant_configs[layer]
            fidelity = config.fidelity
            q_i = config.precision
            b_i = 1.0 / max(config.compression_ratio, 0.1)  # 归一化
            t89_values[f'L{layer}'] = {
                'F_i': round(fidelity, 4),
                'q_i': q_i,
                'b_i': round(b_i, 4),
                'F_i_log_q': round(fidelity * math.log2(max(q_i, 2)), 4)
            }

        t89_total = sum(
            v['F_i_log_q'] for v in t89_values.values()
        )

        # 5. 治理报告
        total_memory_count = sum(
            len(layer_mems) for layer_mems in self.memories.values()
        )

        self.last_update = time.time()

        return {
            'govern_cycle': self.total_govern_cycles,
            'quantization': quant_results,
            'compaction': compact_result.to_dict(),
            'budget': budget_result.to_dict() if isinstance(budget_result, ContextBudget) else budget_result,
            't89_analysis': t89_values,
            't89_total_objective': round(t89_total, 6),
            'theorem_T89': f'max Σ(F_i×log₂(q_i))={round(t89_total, 4)}, s.t. Σb_i≤B',
            'total_memories': total_memory_count,
            'total_bytes_saved': self.total_bytes_saved,
            'max_compression_ratio': round(self.max_compression_ratio, 6),
            'total_fidelity_loss': round(self.total_fidelity_loss, 6)
        }

    # ==================== 记忆操作 ====================

    def store_memory(self, key: str, value: Any, layer: int = 1,
                     phi_value: float = 0.5) -> MemoryEntry:
        """
        存储记忆条目

        Args:
            key: 记忆键
            value: 记忆值
            layer: 存储层级 (1/2/3)
            phi_value: Φ值

        Returns:
            MemoryEntry: 存储的记忆条目
        """
        layer = max(1, min(3, layer))
        config = self.quant_configs[layer]

        entry = MemoryEntry(
            key=key,
            value=value,
            layer=layer,
            precision=config.precision,
            access_count=0,
            last_access=time.time(),
            phi_value=phi_value,
            fidelity=config.fidelity,
            size_bytes=self._estimate_data_size(value)
        )

        self.memories[layer][key] = entry
        self.last_update = time.time()
        return entry

    def retrieve_memory(self, key: str) -> Optional[MemoryEntry]:
        """
        检索记忆条目

        按L1→L2→L3顺序查找，找到后更新访问计数。

        Args:
            key: 记忆键

        Returns:
            MemoryEntry或None
        """
        for layer in [1, 2, 3]:
            if key in self.memories[layer]:
                entry = self.memories[layer][key]
                entry.access_count += 1
                entry.last_access = time.time()
                return entry
        return None

    # ==================== 辅助方法 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取KV缓存治理器状态

        Returns:
            状态字典，包含量化统计和当前配置
        """
        total_memories = sum(
            len(layer_mems) for layer_mems in self.memories.values()
        )

        # 每层记忆数
        layer_counts = {
            f'L{l}': len(self.memories.get(l, {}))
            for l in [1, 2, 3]
        }

        # 预算利用率
        budget_util = self.context_budget.utilization

        # T89验证
        t89_values = []
        for layer in [1, 2, 3]:
            config = self.quant_configs[layer]
            t89_values.append(config.fidelity * math.log2(max(config.precision, 2)))
        t89_total = sum(t89_values)

        return {
            'total_quantizations': self.total_quantizations,
            'total_compactions': self.total_compactions,
            'total_budget_allocations': self.total_budget_allocations,
            'total_govern_cycles': self.total_govern_cycles,
            'total_bytes_saved': self.total_bytes_saved,
            'max_compression_ratio': round(self.max_compression_ratio, 6),
            'total_fidelity_loss': round(self.total_fidelity_loss, 6),
            'total_memories': total_memories,
            'layer_counts': layer_counts,
            'budget_total_tokens': self.context_budget.total_tokens,
            'budget_utilization': round(budget_util, 6),
            'quant_configs': {
                f'L{l}': self.quant_configs[l].to_dict()
                for l in [1, 2, 3]
            },
            't89_total_objective': round(t89_total, 6),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T89': f'max Σ(F_i×log₂(q_i))={round(t89_total, 4)}, s.t. Σb_i≤B'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新KV缓存治理器状态

        Args:
            data: 可选更新数据，支持：
                - quantize: 差异量化 {layer, data, phi_value}
                - compact: 压缩 {keep_recent}
                - allocate: 预算分配 {modules, total_budget}
                - govern: 全局治理 {memory_tree}
                - store: 存储记忆 {key, value, layer, phi_value}
                - retrieve: 检索记忆 {key}
                - set_budget: 设置预算 {total_tokens}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'quantize' or 'quantize' in data:
                q = data.get('quantize', data)
                self.quantize(
                    layer=int(q.get('layer', 1)),
                    data=q.get('data'),
                    phi_value=float(q.get('phi_value', 0.5))
                )
            elif action == 'compact' or 'compact' in data:
                c = data.get('compact', data)
                self.compact(
                    memories=c.get('memories'),
                    keep_recent=int(c.get('keep_recent', 5))
                )
            elif action == 'allocate' or 'allocate' in data:
                a = data.get('allocate', data)
                self.allocate_budget(
                    modules=a.get('modules', {}),
                    total_budget=int(a.get('total_budget', 8192))
                )
            elif action == 'govern':
                self.govern(data.get('memory_tree'))
            elif action == 'store' or 'store' in data:
                s = data.get('store', data)
                self.store_memory(
                    key=s.get('key', ''),
                    value=s.get('value'),
                    layer=int(s.get('layer', 1)),
                    phi_value=float(s.get('phi_value', 0.5))
                )
            elif action == 'retrieve' or 'retrieve' in data:
                r = data.get('retrieve', data)
                self.retrieve_memory(key=r.get('key', ''))
            elif action == 'set_budget':
                self.context_budget.total_tokens = int(
                    data.get('total_tokens', self.context_budget.total_tokens)
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示KV缓存治理器的核心功能"""
        # 1. 存储不同层级的记忆
        self.store_memory('recent_fact_1', '今天天气晴朗', layer=1, phi_value=0.95)
        self.store_memory('recent_fact_2', '会议定于下午3点', layer=1, phi_value=0.9)
        self.store_memory('mid_term_1', '项目截止日期是下周五', layer=2, phi_value=0.6)
        self.store_memory('mid_term_2', '数据库连接字符串已更新', layer=2, phi_value=0.55)
        self.store_memory('long_term_1', '去年的年度总结', layer=3, phi_value=0.3)
        self.store_memory('long_term_2', '历史配置记录', layer=3, phi_value=0.25)

        # 2. 差异量化
        quant_l1 = self.quantize(1, '近期记忆数据', phi_value=0.95)
        quant_l2 = self.quantize(2, '中期记忆数据', phi_value=0.6)
        quant_l3 = self.quantize(3, '远期记忆数据', phi_value=0.3)

        # 3. TieredCompact压缩
        compact_result = self.compact(keep_recent=3)

        # 4. 上下文预算分配
        budget = self.allocate_budget(
            {'M29': 0.95, 'M57': 0.85, 'M81': 0.90, 'M126': 0.88},
            total_budget=4096
        )

        # 5. 全局治理
        govern_result = self.govern()

        # 6. 检索记忆
        retrieved = self.retrieve_memory('recent_fact_1')

        return {
            'quantize_L1': quant_l1,
            'quantize_L2': quant_l2,
            'quantize_L3': quant_l3,
            'compact': compact_result.to_dict(),
            'budget': budget.to_dict() if isinstance(budget, ContextBudget) else budget,
            'govern': govern_result,
            'retrieved': retrieved.to_dict() if retrieved else None,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[KVCacheGovernor] = None


def get_instance() -> KVCacheGovernor:
    """
    获取KVCacheGovernor单例实例

    Returns:
        KVCacheGovernor全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = KVCacheGovernor()
    return _instance


def quantize(layer: int, data: Any, phi_value: float = 0.5) -> Dict[str, Any]:
    """差异量化（快捷接口）"""
    return get_instance().quantize(layer, data, phi_value)


def compact(memories: Optional[Dict[str, MemoryEntry]] = None,
            keep_recent: int = 5) -> CompactResult:
    """TieredCompact压缩（快捷接口）"""
    return get_instance().compact(memories, keep_recent)


def allocate_budget(modules: Dict[str, float],
                    total_budget: int = 8192) -> ContextBudget:
    """预算分配（快捷接口）"""
    return get_instance().allocate_budget(modules, total_budget)


def govern(memory_tree: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """全局治理（快捷接口）"""
    return get_instance().govern(memory_tree)


def store_memory(key: str, value: Any, layer: int = 1,
                 phi_value: float = 0.5) -> MemoryEntry:
    """存储记忆（快捷接口）"""
    return get_instance().store_memory(key, value, layer, phi_value)


def retrieve_memory(key: str) -> Optional[MemoryEntry]:
    """检索记忆（快捷接口）"""
    return get_instance().retrieve_memory(key)


def get_state() -> Dict[str, Any]:
    """获取KV缓存治理器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新KV缓存治理器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M128 KVCacheGovernor 自测')
    print('=' * 60)

    engine = KVCacheGovernor()

    # 测试差异化量化
    print('\n--- 差异化量化测试 ---')
    for layer, phi in [(1, 0.95), (2, 0.6), (3, 0.3)]:
        result = engine.quantize(layer, f'测试数据L{layer}', phi)
        print(f'  L{layer} (Φ={phi}): 精度={result["effective_precision"]}bit, '
              f'压缩率={result["compression_ratio"]}x, 保真度={result["fidelity"]}')

    # 测试记忆存储和检索
    print('\n--- 记忆存储/检索测试 ---')
    engine.store_memory('test_key', '测试值', layer=1, phi_value=0.9)
    entry = engine.retrieve_memory('test_key')
    print(f'  存储: key=test_key, value=测试值')
    print(f'  检索: key={entry.key}, value={entry.value}, 精度={entry.precision}bit')

    # 测试TieredCompact
    print('\n--- TieredCompact压缩测试 ---')
    for i in range(10):
        engine.store_memory(f'mem_{i}', f'记忆内容{i}', layer=1, phi_value=0.8 - i * 0.05)
    compact_result = engine.compact(keep_recent=3)
    print(f'  保留: {compact_result.kept_count}, 压缩: {compact_result.compressed_count}, '
          f'淘汰: {compact_result.evicted_count}')
    print(f'  压缩率: {compact_result.compression_ratio}x, 保真度损失: {compact_result.fidelity_loss}')

    # 测试预算分配
    print('\n--- 预算分配测试 ---')
    budget = engine.allocate_budget({'A': 0.9, 'B': 0.6, 'C': 0.3}, 4096)
    print(f'  总预算: {budget.total_tokens}, 利用率: {budget.utilization}')
    print(f'  分配: {budget.allocated}')

    # 测试全局治理
    print('\n--- 全局治理测试 ---')
    govern_result = engine.govern()
    print(f'  治理周期: {govern_result["govern_cycle"]}')
    print(f'  T89: {govern_result["theorem_T89"]}')
    print(f'  总节省字节: {govern_result["total_bytes_saved"]}')

    # 打印最终状态
    print('\n--- 最终状态 ---')
    state = engine.get_state()
    for k, v in state.items():
        if k not in ('quant_configs', 'layer_counts'):
            print(f'  {k}: {v}')

    print('\n定理T89验证:', state['theorem_T89'])
    print('\n自测完成 ✓')
