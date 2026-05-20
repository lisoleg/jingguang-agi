# -*- coding: utf-8 -*-
"""
M119: 层间保真度监控 (Layer Fidelity Monitor)
基于《人机共生时代的复合体管理学》

核心概念：α = α₁₂ × α₂₃ × α₃₄ × α₄₅ — 五层信息保真度乘积
五层架构：L1(数据)→L2(特征)→L3(语义)→L4(决策)→L5(行动)
保真度崩溃 = AI幻觉：当某层α_ij << 1时，下游全部失真

定理:
  T77 保真度乘积定理 — α_total = ∏α_ij，任一环节失真→整体崩溃

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ==================== 常量 ====================

# 五层架构定义
LAYERS = {
    1: 'L1-数据',
    2: 'L2-特征',
    3: 'L3-语义',
    4: 'L4-决策',
    5: 'L5-行动'
}

# 层对映射（相邻层）
LAYER_PAIRS = [(1, 2), (2, 3), (3, 4), (4, 5)]


# ==================== 数据结构 ====================

@dataclass
class LayerPair:
    """
    层对保真度 — 两个相邻层之间的信息传递保真度

    source_layer: 源层（L1-L4）
    target_layer: 目标层（L2-L5）
    fidelity: 保真度α_ij ∈ [0,1]
    distortion: 失真度 = 1 - fidelity
    """
    source_layer: int = 1
    target_layer: int = 2
    fidelity: float = 1.0
    distortion: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'LayerPair':
        return cls(**d)


@dataclass
class FidelityReport:
    """
    保真度报告 — 全部层对保真度的综合报告

    layer_pairs: 各层对保真度
    total_fidelity: 总保真度乘积α = ∏α_ij
    critical_layers: 保真度低于阈值的层对
    collapse_risk: 崩溃风险等级
    """
    layer_pairs: List[Dict[str, Any]] = field(default_factory=list)
    total_fidelity: float = 1.0
    critical_layers: List[str] = field(default_factory=list)
    collapse_risk: str = 'low'       # low | medium | high | critical

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==================== 核心类 ====================

class LayerFidelityMonitor:
    """
    M119: 层间保真度监控

    监控五层架构中相邻层的信息传递保真度：
    α = α₁₂ × α₂₃ × α₃₄ × α₄₅

    五层架构：
    - L1 数据层：原始数据输入
    - L2 特征层：特征提取与表示
    - L3 语义层：语义理解与推理
    - L4 决策层：决策生成与评估
    - L5 行动层：行动执行与反馈

    保真度崩溃 = AI幻觉：
    当某层α_ij << 1时，该层以下的所有层都会受到失真影响，
    最终导致输出与真实意图严重偏离——即AI幻觉。

    定理T77（保真度乘积定理）:
    α_total = ∏α_ij，任一α_ij→0 ⟹ 整体保真度崩溃。
    单一环节的失真可导致全局幻觉——保真度不是取最弱环，
    而是乘积关系：任何一环崩溃即整体崩溃。
    """

    def __init__(self):
        """初始化层间保真度监控"""
        # 层对保真度 {(source, target): LayerPair}
        self.layer_pairs: Dict[Tuple[int, int], LayerPair] = {}

        # 系统参数
        self.critical_threshold: float = 0.5    # 临界保真度阈值
        self.collapse_threshold: float = 0.2    # 崩溃保真度阈值
        self.decay_rate: float = 0.01           # 自然衰减率

        # 统计
        self.total_measurements: int = 0
        self.collapse_detected_count: int = 0
        self.critical_alerts: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

        # 初始化层对
        self._init_layer_pairs()

    def _init_layer_pairs(self):
        """初始化四对相邻层的保真度（默认满保真）"""
        for source, target in LAYER_PAIRS:
            self.layer_pairs[(source, target)] = LayerPair(
                source_layer=source,
                target_layer=target,
                fidelity=1.0,
                distortion=0.0
            )

    def measure_fidelity(self, source_layer: int, target_layer: int,
                         fidelity: Optional[float] = None) -> LayerPair:
        """
        测量层间保真度

        测量从source_layer到target_layer的信息传递保真度。
        如果不提供fidelity参数，则基于系统状态自动估算。

        Args:
            source_layer: 源层编号（L1-L4）
            target_layer: 目标层编号（L2-L5）
            fidelity: 保真度值（可选，不提供则自动估算）

        Returns:
            LayerPair: 层对保真度
        """
        # 验证层对有效性
        key = (source_layer, target_layer)
        if key not in self.layer_pairs:
            if 1 <= source_layer <= 5 and 1 <= target_layer <= 5 and source_layer < target_layer:
                self.layer_pairs[key] = LayerPair(
                    source_layer=source_layer,
                    target_layer=target_layer,
                    fidelity=1.0,
                    distortion=0.0
                )
            else:
                # 无效层对，返回默认
                return LayerPair(
                    source_layer=source_layer,
                    target_layer=target_layer,
                    fidelity=0.5,
                    distortion=0.5
                )

        pair = self.layer_pairs[key]

        if fidelity is not None:
            # 使用提供的保真度值
            pair.fidelity = round(max(0.0, min(1.0, fidelity)), 6)
        else:
            # 自动估算：基于当前状态的微扰动
            current = pair.fidelity
            # 自然衰减 + 随机波动
            decay = self.decay_rate * (1.0 - current + 0.1)
            fluctuation = 0.02 * (hash(str(time.time())) % 100) / 100.0
            pair.fidelity = round(max(0.0, min(1.0, current - decay + fluctuation)), 6)

        pair.distortion = round(1.0 - pair.fidelity, 6)

        self.total_measurements += 1
        self.last_update = time.time()

        return pair

    def compute_total_fidelity(self) -> Dict[str, Any]:
        """
        T77计算总保真度乘积

        α_total = α₁₂ × α₂₃ × α₃₄ × α₄₅

        定理T77（保真度乘积定理）:
        任一α_ij→0 ⟹ 整体保真度崩溃。
        保真度是乘积关系而非取最弱环：
        即使只有一个环节失真，整体保真度也会大幅下降。

        Returns:
            总保真度计算结果
        """
        # 收集四对核心层对的保真度
        core_fidelities = []
        pair_details = []

        for source, target in LAYER_PAIRS:
            pair = self.layer_pairs.get((source, target))
            if pair:
                f = pair.fidelity
                core_fidelities.append(f)
                pair_details.append({
                    'pair': f'L{source}→L{target}',
                    'fidelity': f,
                    'distortion': pair.distortion
                })

        # T77: α_total = ∏α_ij
        total_fidelity = 1.0
        for f in core_fidelities:
            total_fidelity *= f

        total_fidelity = round(total_fidelity, 6)

        # 识别关键层对（保真度最低的）
        critical = [p for p in pair_details if p['fidelity'] < self.critical_threshold]

        # 崩溃风险评估
        if total_fidelity < self.collapse_threshold:
            collapse_risk = 'critical'
            self.collapse_detected_count += 1
        elif total_fidelity < self.critical_threshold:
            collapse_risk = 'high'
            self.critical_alerts += 1
        elif any(p['fidelity'] < self.critical_threshold for p in pair_details):
            collapse_risk = 'medium'
        else:
            collapse_risk = 'low'

        self.last_update = time.time()

        return {
            'total_fidelity_alpha': total_fidelity,
            'pair_details': pair_details,
            'critical_pairs': critical,
            'collapse_risk': collapse_risk,
            'theorem': 'T77: 保真度乘积定理',
            'interpretation': (
                f'总保真度α={total_fidelity:.4f}，'
                f'风险等级={collapse_risk}'
            )
        }

    def detect_collapse(self) -> Dict[str, Any]:
        """
        检测保真度崩溃

        当某层α_ij << 1时，该层以下的所有层都会受到失真影响，
        最终导致输出与真实意图严重偏离——即AI幻觉。

        Returns:
            崩溃检测结果
        """
        report = self.compute_total_fidelity()

        # 定位最薄弱的层对
        weakest_pair = None
        min_fidelity = 1.0
        for source, target in LAYER_PAIRS:
            pair = self.layer_pairs.get((source, target))
            if pair and pair.fidelity < min_fidelity:
                min_fidelity = pair.fidelity
                weakest_pair = pair

        # 崩溃传播分析
        collapse_propagation = []
        for source, target in LAYER_PAIRS:
            pair = self.layer_pairs.get((source, target))
            if pair and pair.fidelity < self.critical_threshold:
                # 失真从该层向下传播
                downstream_layers = [
                    f'L{t}' for s, t in LAYER_PAIRS
                    if s >= source and self.layer_pairs.get((s, t)) is not None
                ]
                collapse_propagation.append({
                    'source': f'L{source}',
                    'target': f'L{target}',
                    'fidelity': pair.fidelity,
                    'downstream_impact': downstream_layers
                })

        is_collapsed = report['collapse_risk'] in ('critical', 'high')

        self.last_update = time.time()

        return {
            'is_collapsed': is_collapsed,
            'total_fidelity': report['total_fidelity_alpha'],
            'weakest_pair': (
                f'L{weakest_pair.source_layer}→L{weakest_pair.target_layer}'
                if weakest_pair else 'N/A'
            ),
            'weakest_fidelity': min_fidelity,
            'collapse_propagation': collapse_propagation,
            'collapse_risk': report['collapse_risk'],
            'hallucination_warning': is_collapsed,
            'theorem': 'T77: 保真度乘积定理'
        }

    def locate_distortion(self) -> Dict[str, Any]:
        """
        定位失真源

        在五层架构中定位保真度最低的层对，
        即最可能导致AI幻觉的失真来源。

        Returns:
            失真源定位结果
        """
        # 收集所有层对的失真度
        distortions = []
        for source, target in LAYER_PAIRS:
            pair = self.layer_pairs.get((source, target))
            if pair:
                distortions.append({
                    'pair': f'L{source}→L{target}',
                    'source_layer': LAYERS.get(source, f'L{source}'),
                    'target_layer': LAYERS.get(target, f'L{target}'),
                    'fidelity': pair.fidelity,
                    'distortion': pair.distortion
                })

        # 按失真度降序排列
        distortions.sort(key=lambda x: x['distortion'], reverse=True)

        # 识别失真源
        if distortions:
            primary_source = distortions[0]
        else:
            primary_source = None

        # 修复建议
        recommendations = []
        for d in distortions:
            if d['distortion'] > 0.3:
                recommendations.append(
                    f"{d['pair']}: 保真度{d['fidelity']:.2f}过低，"
                    f"建议检查{d['source_layer']}到{d['target_layer']}的映射"
                )

        self.last_update = time.time()

        return {
            'distortions': distortions,
            'primary_source': primary_source,
            'recommendations': recommendations,
            'total_layers_monitored': len(distortions)
        }

    def get_state(self) -> Dict[str, Any]:
        """获取层间保真度监控状态"""
        report = self.compute_total_fidelity()

        # 各层对保真度摘要
        pair_summary = {}
        for source, target in LAYER_PAIRS:
            pair = self.layer_pairs.get((source, target))
            if pair:
                pair_summary[f'L{source}_L{target}'] = pair.fidelity

        return {
            'total_fidelity_alpha': report['total_fidelity_alpha'],
            'collapse_risk': report['collapse_risk'],
            'pair_summary': pair_summary,
            'critical_threshold': self.critical_threshold,
            'collapse_threshold': self.collapse_threshold,
            'total_measurements': self.total_measurements,
            'collapse_detected_count': self.collapse_detected_count,
            'critical_alerts': self.critical_alerts,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T77': '保真度乘积: α=∏α_ij, 任一→0 ⟹ 整体崩溃'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """更新层间保真度监控状态"""
        if data:
            action = data.get('action', '')
            if action == 'measure':
                self.measure_fidelity(
                    source_layer=data.get('source_layer', 1),
                    target_layer=data.get('target_layer', 2),
                    fidelity=data.get('fidelity')
                )
            elif action == 'set_fidelity':
                source = data.get('source_layer', 1)
                target = data.get('target_layer', 2)
                fid = data.get('fidelity', 1.0)
                pair = self.layer_pairs.get((source, target))
                if pair:
                    pair.fidelity = max(0.0, min(1.0, fid))
                    pair.distortion = round(1.0 - pair.fidelity, 6)

        # 自然衰减
        for key, pair in self.layer_pairs.items():
            if key in [(s, t) for s, t in LAYER_PAIRS]:
                pair.fidelity = max(0.0, pair.fidelity - self.decay_rate * 0.01)
                pair.distortion = round(1.0 - pair.fidelity, 6)

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示层间保真度监控的核心功能"""
        # 1. 初始全保真状态
        self._init_layer_pairs()

        # 2. 测量正常保真度
        self.measure_fidelity(1, 2, 0.95)
        self.measure_fidelity(2, 3, 0.90)
        self.measure_fidelity(3, 4, 0.85)
        self.measure_fidelity(4, 5, 0.88)

        normal_report = self.compute_total_fidelity()

        # 3. 模拟L2→L3保真度崩溃（AI幻觉场景）
        self.measure_fidelity(2, 3, 0.15)  # 特征→语义严重失真

        collapse_report = self.compute_total_fidelity()
        collapse_detection = self.detect_collapse()
        distortion_location = self.locate_distortion()

        return {
            'normal_state': normal_report,
            'after_collapse_L2L3': collapse_report,
            'collapse_detection': collapse_detection,
            'distortion_location': distortion_location,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[LayerFidelityMonitor] = None


def get_instance() -> LayerFidelityMonitor:
    """获取LayerFidelityMonitor单例实例"""
    global _instance
    if _instance is None:
        _instance = LayerFidelityMonitor()
    return _instance


def measure_fidelity(source_layer: int, target_layer: int,
                     fidelity: Optional[float] = None) -> LayerPair:
    """测量层间保真度（快捷接口）"""
    return get_instance().measure_fidelity(source_layer, target_layer, fidelity)


def compute_total_fidelity() -> Dict[str, Any]:
    """T77计算总保真度乘积（快捷接口）"""
    return get_instance().compute_total_fidelity()


def detect_collapse() -> Dict[str, Any]:
    """检测保真度崩溃（快捷接口）"""
    return get_instance().detect_collapse()


def locate_distortion() -> Dict[str, Any]:
    """定位失真源（快捷接口）"""
    return get_instance().locate_distortion()


def get_state() -> Dict[str, Any]:
    """获取层间保真度监控状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新层间保真度监控状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
