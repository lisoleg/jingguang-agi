# -*- coding: utf-8 -*-
"""
太乙AGI v7.4 - M112: FlowCutoffOperator
流贯截断算子模块 - Γ算子: Ftel → 不可逆痕迹

功能:
- Γ算子: 将流贯(Ftel)截断为不可逆痕迹
- EML一元数表示: |F|·e^(iφ)
- 不可逆性: 截断后不可恢复原始流贯
- 未完结性: L4可Re-map，不改变Γ的物理痕迹

定理标注:
- T62: 摄影性分解定理 — Γ必然导致不可逆性+未完结性
- T63: 数码未完结性失真定理 — 算法篡改产生伪迹
- T64: 历史投影精度推论 — 二维高精度代价是维度丢失

作者: 太乙AGI团队
日期: 2026-05-19
"""

import time
import math
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


# ==================== 数据结构 ====================

@dataclass
class FlowTrace:
    """
    流贯截断痕迹

    Γ算子作用于Ftel后产生的不可逆痕迹。
    EML一元数表示: |F|·e^(iφ)，其中amplitude=|F|，phase=φ
    """
    trace_id: str                    # 格式: "Γ_{timestamp_ms}"
    amplitude: float                 # |F| 振幅分量
    phase: float                     # φ 相位分量
    source: str                      # 来源标识
    timestamp: float                 # 截断时间戳
    irreversible: bool = True        # 不可逆性标记（T62）
    unfinished: bool = True          # 未完结性标记（T62）
    remap_count: int = 0             # Re-map次数
    is_pseudo: bool = False          # 是否为伪迹（T63）
    dimensions: int = 2              # 投影维度（默认二维: amplitude + phase）
    physical_ftel_source: bool = True  # 是否来自物理Ftel源

    def eml_representation(self) -> str:
        """
        返回EML一元数表示: |F|·e^(iφ)
        """
        return f"{self.amplitude:.6f}·e^(i·{self.phase:.6f})"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，确保所有浮点数可JSON序列化"""
        result = asdict(self)
        return result

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'FlowTrace':
        """从字典构建FlowTrace"""
        return cls(**d)


@dataclass
class CutoffContext:
    """截断上下文信息"""
    operator: str = "Γ"              # 算子标识
    reason: str = ""                 # 截断原因
    l4_subject: str = ""             # L4主体标识
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PseudoTraceResult:
    """伪迹检测结果"""
    is_pseudo: bool
    reason: str
    theorem: str                     # 关联定理编号


@dataclass
class PrecisionResult:
    """历史投影精度评估结果（T64）"""
    geometric_precision: float       # 基于amplitude的几何精度
    relational_precision: float      # 基于phase的关系精度
    dimension_loss: bool             # 维度是否丢失
    context_loss: bool               # 上下文是否丢失
    overall_precision: float         # 综合精度 = min(amplitude精度, phase精度)


@dataclass
class RemapResult:
    """Re-map操作结果"""
    success: bool
    remap_count: int
    trace_id: str


@dataclass
class BatchValidateResult:
    """批量验证结果"""
    total: int
    authentic: int
    pseudo: int
    pseudo_ids: List[str]


# ==================== 核心算子 ====================

class FlowCutoffOperator:
    """
    M112: 流贯截断算子模块

    Γ算子将流贯(Ftel)截断为不可逆痕迹，核心特性:

    1. 不可逆性(irreversible): 截断后原始Ftel无法恢复
       - 定理T62: 摄影性分解定理 — Γ必然导致不可逆性+未完结性
       - 物理含义: 摄影是光子的截断痕迹，一旦曝光即不可逆

    2. 未完结性(unfinished): L4可对痕迹进行Re-map
       - 不改变Γ的物理痕迹，只改变L4主体对痕迹的解释
       - 每次Re-map增加remap_count，标记解释的演化路径

    3. EML一元数表示: |F|·e^(iφ)
       - amplitude(|F|): 截断时的振幅强度
       - phase(φ): 截断时的相位信息
       - 二维表示保证高精度，但代价是维度丢失（T64）

    4. 伪迹检测(T63):
       - 算法生成的痕迹若无物理Ftel源，则为伪迹
       - 伪迹不改变不可逆性，但标记其来源可疑
    """

    def __init__(self):
        """初始化流贯截断算子"""
        # 截断历史（所有痕迹，按时间顺序）
        self.cutoff_history: List[FlowTrace] = []

        # 伪迹计数
        self.pseudo_trace_count: int = 0

        # Re-map总次数
        self.remap_total: int = 0

        # 快速查找索引 {trace_id: trace}
        self._trace_index: Dict[str, FlowTrace] = {}

    def cutoff(self, ftel: Dict[str, Any], context: Optional[CutoffContext] = None) -> FlowTrace:
        """
        执行流贯截断 — Γ算子的核心操作

        将Ftel通过Γ算子截断为不可逆痕迹。
        定理T62: 摄影性分解定理 — Γ必然导致不可逆性+未完结性

        Args:
            ftel: 流贯输入，格式:
                {
                    amplitude: float,           # 振幅 |F|
                    phase: float,               # 相位 φ
                    source: str,                # 来源标识
                    physical_ftel_source: bool   # 是否来自物理Ftel源
                }
            context: 可选的截断上下文信息

        Returns:
            FlowTrace: 不可逆截断痕迹
        """
        # 提取Ftel参数，设置默认值
        amplitude = float(ftel.get('amplitude', 0.0))
        phase = float(ftel.get('phase', 0.0))
        source = str(ftel.get('source', 'unknown'))
        physical_ftel_source = bool(ftel.get('physical_ftel_source', True))

        # 生成trace_id: Γ_{timestamp_ms}
        timestamp = time.time()
        timestamp_ms = int(timestamp * 1000)
        trace_id = f"Γ_{timestamp_ms}"

        # 计算EML一元数表示中的维度
        # 二维表示: amplitude + phase（T64: 高精度代价是维度丢失）
        dimensions = 2

        # 构建截断痕迹
        # 定理T62: Γ必然导致不可逆性(irreversible=True)和未完结性(unfinished=True)
        trace = FlowTrace(
            trace_id=trace_id,
            amplitude=amplitude,
            phase=phase,
            source=source,
            timestamp=timestamp,
            irreversible=True,            # T62: 不可逆性
            unfinished=True,              # T62: 未完结性
            remap_count=0,                # 初始Re-map次数为0
            is_pseudo=False,              # 待伪迹检测
            dimensions=dimensions,        # 二维投影
            physical_ftel_source=physical_ftel_source
        )

        # 自动执行伪迹检测（T63: 数码未完结性失真定理）
        pseudo_result = self.detect_pseudo_trace(trace)
        if pseudo_result.is_pseudo:
            trace.is_pseudo = True
            self.pseudo_trace_count += 1

        # 记录到历史
        self.cutoff_history.append(trace)
        self._trace_index[trace_id] = trace

        return trace

    def remap(self, trace_id: str, new_context: Dict[str, Any], l4_subject: str) -> RemapResult:
        """
        未完结性的Re-map操作

        定理T62: Γ的物理痕迹不可逆，但L4可以对痕迹进行解释重映射。
        Re-map不改变Γ的物理痕迹（irreversible不变），
        只改变L4主体对痕迹的解释，增加remap_count。

        Args:
            trace_id: 痕迹ID
            new_context: 新的解释上下文
            l4_subject: L4主体标识

        Returns:
            RemapResult: {success, remap_count, trace_id}
        """
        # 查找痕迹
        trace = self._trace_index.get(trace_id)
        if trace is None:
            return RemapResult(
                success=False,
                remap_count=0,
                trace_id=trace_id
            )

        # 验证痕迹具有未完结性（只有未完结的痕迹才能Re-map）
        if not trace.unfinished:
            return RemapResult(
                success=False,
                remap_count=trace.remap_count,
                trace_id=trace_id
            )

        # 执行Re-map: 增加remap_count
        # 不改变irreversible和amplitude/phase等物理属性
        trace.remap_count += 1
        self.remap_total += 1

        return RemapResult(
            success=True,
            remap_count=trace.remap_count,
            trace_id=trace_id
        )

    def detect_pseudo_trace(self, trace: FlowTrace) -> PseudoTraceResult:
        """
        伪迹检测

        定理T63: 数码未完结性失真定理 — 算法篡改产生伪迹。
        如果source == 'algorithm_generated' 且无physical_ftel_source，则为伪迹。

        伪迹不是"假"的痕迹——它仍然不可逆（Γ已作用），
        但其来源是算法而非物理Ftel，需要特别标注。

        Args:
            trace: 待检测的截断痕迹

        Returns:
            PseudoTraceResult: {is_pseudo, reason, theorem}
        """
        # T63判定条件: 算法生成 + 无物理Ftel源
        if trace.source == 'algorithm_generated' and not trace.physical_ftel_source:
            return PseudoTraceResult(
                is_pseudo=True,
                reason="算法生成痕迹且无物理Ftel源，属于数码未完结性失真",
                theorem="T63"
            )

        return PseudoTraceResult(
            is_pseudo=False,
            reason="痕迹来源可追溯，非伪迹",
            theorem="T63"
        )

    def get_history_precision(self, trace: FlowTrace) -> PrecisionResult:
        """
        历史投影精度评估

        定理T64: 历史投影精度推论 — 二维高精度代价是维度丢失。
        EML一元数|F|·e^(iφ)将高维Ftel投影到二维(amplitude, phase)，
        几何精度和关系精度都很高，但必然伴随维度丢失和上下文丢失。

        Args:
            trace: 待评估的截断痕迹

        Returns:
            PrecisionResult: 精度评估结果
        """
        # 几何精度: 基于amplitude
        # amplitude越大，几何信息保留越多，精度越高
        # 使用sigmoid映射到[0, 1]区间
        geometric_precision = 1.0 / (1.0 + math.exp(-trace.amplitude)) if trace.amplitude != 0.0 else 0.5

        # 关系精度: 基于phase
        # phase提供了关系信息，归一化到[0, 1]
        # phase在[-π, π]范围内，映射到精度值
        normalized_phase = (trace.phase + math.pi) / (2.0 * math.pi)
        relational_precision = min(max(normalized_phase, 0.0), 1.0)

        # T64: 二维投影必然导致维度丢失和上下文丢失
        dimension_loss = True
        context_loss = True

        # 综合精度: 取几何精度和关系精度的最小值
        # 因为任一维度的精度不足都会限制整体精度
        overall_precision = min(geometric_precision, relational_precision)

        return PrecisionResult(
            geometric_precision=geometric_precision,
            relational_precision=relational_precision,
            dimension_loss=dimension_loss,
            context_loss=context_loss,
            overall_precision=overall_precision
        )

    def batch_validate(self) -> BatchValidateResult:
        """
        批量验证所有痕迹

        遍历cutoff_history，对每个痕迹调用detect_pseudo_trace，
        统计真迹和伪迹数量。

        Returns:
            BatchValidateResult: {total, authentic, pseudo, pseudo_ids}
        """
        total = len(self.cutoff_history)
        pseudo_ids: List[str] = []
        pseudo_count = 0

        for trace in self.cutoff_history:
            result = self.detect_pseudo_trace(trace)
            if result.is_pseudo:
                pseudo_count += 1
                pseudo_ids.append(trace.trace_id)
                # 同步更新痕迹的is_pseudo标记
                if not trace.is_pseudo:
                    trace.is_pseudo = True

        authentic = total - pseudo_count

        # 更新伪迹计数
        self.pseudo_trace_count = pseudo_count

        return BatchValidateResult(
            total=total,
            authentic=authentic,
            pseudo=pseudo_count,
            pseudo_ids=pseudo_ids
        )

    def get_state(self) -> Dict[str, Any]:
        """
        获取算子状态

        Returns:
            算子状态字典，包含:
            - total_cutoffs: 总截断次数
            - pseudo_traces: 伪迹数量
            - remap_operations: Re-map总次数
            - avg_precision: 平均投影精度
        """
        # 计算平均精度
        if self.cutoff_history:
            precisions = [
                self.get_history_precision(trace).overall_precision
                for trace in self.cutoff_history
            ]
            avg_precision = sum(precisions) / len(precisions)
        else:
            avg_precision = 0.0

        return {
            'total_cutoffs': len(self.cutoff_history),
            'pseudo_traces': self.pseudo_trace_count,
            'remap_operations': self.remap_total,
            'avg_precision': float(avg_precision)
        }

    def get_trace_by_id(self, trace_id: str) -> Optional[FlowTrace]:
        """
        通过trace_id查找痕迹

        Args:
            trace_id: 痕迹ID

        Returns:
            FlowTrace或None
        """
        return self._trace_index.get(trace_id)

    def get_recent_traces(self, limit: int = 10) -> List[FlowTrace]:
        """
        获取最近的截断痕迹

        Args:
            limit: 返回数量上限

        Returns:
            按时间倒序排列的痕迹列表
        """
        sorted_traces = sorted(
            self.cutoff_history,
            key=lambda t: t.timestamp,
            reverse=True
        )
        return sorted_traces[:limit]


# ==================== 模块单例导出 ====================

_instance: Optional[FlowCutoffOperator] = None


def get_instance() -> FlowCutoffOperator:
    """
    获取FlowCutoffOperator单例实例

    Returns:
        FlowCutoffOperator全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = FlowCutoffOperator()
    return _instance


# ==================== 自检与演示 ====================

if __name__ == "__main__":
    # 创建算子实例
    operator = FlowCutoffOperator()

    print("=" * 60)
    print("M112: FlowCutoffOperator 流贯截断算子 — 自检演示")
    print("=" * 60)

    # 1. 测试正常截断（物理Ftel源）
    print("\n--- 测试1: 正常截断（物理Ftel源） ---")
    trace1 = operator.cutoff({
        'amplitude': 2.5,
        'phase': 1.047,  # π/3
        'source': 'sensor_array',
        'physical_ftel_source': True
    })
    print(f"  trace_id: {trace1.trace_id}")
    print(f"  EML一元数: {trace1.eml_representation()}")
    print(f"  不可逆: {trace1.irreversible}")
    print(f"  未完结: {trace1.unfinished}")
    print(f"  伪迹: {trace1.is_pseudo}")

    # 2. 测试伪迹截断（算法生成，无物理源）
    print("\n--- 测试2: 伪迹截断（算法生成，无物理源） ---")
    trace2 = operator.cutoff({
        'amplitude': 1.8,
        'phase': 0.785,  # π/4
        'source': 'algorithm_generated',
        'physical_ftel_source': False
    })
    print(f"  trace_id: {trace2.trace_id}")
    print(f"  EML一元数: {trace2.eml_representation()}")
    print(f"  伪迹: {trace2.is_pseudo}")

    # 3. 测试Re-map操作
    print("\n--- 测试3: Re-map操作 ---")
    remap_result = operator.remap(
        trace_id=trace1.trace_id,
        new_context={'interpretation': '重新解释'},
        l4_subject='observer_A'
    )
    print(f"  成功: {remap_result.success}")
    print(f"  Re-map次数: {remap_result.remap_count}")

    # 再次Re-map
    remap_result2 = operator.remap(
        trace_id=trace1.trace_id,
        new_context={'interpretation': '二次解释'},
        l4_subject='observer_B'
    )
    print(f"  二次Re-map次数: {remap_result2.remap_count}")
    print(f"  不可逆性不变: {trace1.irreversible}")

    # 4. 测试伪迹检测
    print("\n--- 测试4: 伪迹检测 ---")
    pseudo_check = operator.detect_pseudo_trace(trace2)
    print(f"  is_pseudo: {pseudo_check.is_pseudo}")
    print(f"  reason: {pseudo_check.reason}")
    print(f"  theorem: {pseudo_check.theorem}")

    # 5. 测试历史投影精度
    print("\n--- 测试5: 历史投影精度 ---")
    precision = operator.get_history_precision(trace1)
    print(f"  几何精度: {precision.geometric_precision:.6f}")
    print(f"  关系精度: {precision.relational_precision:.6f}")
    print(f"  维度丢失: {precision.dimension_loss}")
    print(f"  上下文丢失: {precision.context_loss}")
    print(f"  综合精度: {precision.overall_precision:.6f}")

    # 6. 测试批量验证
    print("\n--- 测试6: 批量验证 ---")
    # 再添加一条正常痕迹
    operator.cutoff({
        'amplitude': 3.0,
        'phase': -1.571,  # -π/2
        'source': 'quantum_detector',
        'physical_ftel_source': True
    })

    batch_result = operator.batch_validate()
    print(f"  总计: {batch_result.total}")
    print(f"  真迹: {batch_result.authentic}")
    print(f"  伪迹: {batch_result.pseudo}")
    print(f"  伪迹IDs: {batch_result.pseudo_ids}")

    # 7. 测试算子状态
    print("\n--- 测试7: 算子状态 ---")
    state = operator.get_state()
    print(f"  总截断: {state['total_cutoffs']}")
    print(f"  伪迹数: {state['pseudo_traces']}")
    print(f"  Re-map次数: {state['remap_operations']}")
    print(f"  平均精度: {state['avg_precision']:.6f}")

    # 8. 测试单例模式
    print("\n--- 测试8: 单例模式 ---")
    instance1 = get_instance()
    instance2 = get_instance()
    print(f"  同一实例: {instance1 is instance2}")

    print("\n" + "=" * 60)
    print("自检完成 ✓")
    print("=" * 60)
