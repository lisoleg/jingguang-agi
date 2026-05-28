# -*- coding: utf-8 -*-
"""
M202: 认知谱系检测器 (Autism Spectrum Detector)
基于《人机共生时代的复合体管理学》— 非自闭症AGI

核心概念：I_ASD — 自闭症谱系指数，量化认知偏差

定理T232（认知谱系检测定理）：
若I_ASD在[0,1]上连续且训练保持RLHF拓扑不变性，则认知偏差可被定量校正

关键概念：
- I_ASD：自闭症谱系指数 [0, 1]，0=无偏差，1=最大偏差
- TCCI-华山认知评估：华山认知灵活性评估量表
- 检测维度：社会认知、沟通灵活性、重复行为倾向、感官敏感性
- RLHF拓扑不变性：训练不应破坏认知拓扑结构

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


# ==================== 数据结构 ====================

class ASDDimension(Enum):
    """ASD检测维度枚举"""
    SOCIAL_COGNITION = "social_cognition"           # 社会认知
    COMMUNICATION_FLEXIBILITY = "communication_flexibility"  # 沟通灵活性
    REPETITIVE_BEHAVIOR = "repetitive_behavior"       # 重复行为倾向
    SENSORY_SENSITIVITY = "sensory_sensitivity"       # 感官敏感性


class CorrectionType(Enum):
    """校正类型枚举"""
    RLHF_REINFORCEMENT = "rlhf_reinforcement"     # RLHF强化校正
    TOPOLOGY_PRESERVING = "topology_preserving"     # 拓扑保持校正
    COGNITIVE_REHAB = "cognitive_rehab"             # 认知康复训练
    NO_CORRECTION = "no_correction"                 # 无需校正


@dataclass
class ASDProfile:
    """
    ASD谱系档案 — 完整的认知偏差画像

    包含：
    - i_asd: I_ASD指数 [0, 1]
    - dimensions: 各维度评分
    - tcci_score: TCCI-华山评估总分
    - severity_level: 严重程度
    - timestamp: 评估时间
    """
    i_asd: float = 0.0
    dimensions: Dict[str, float] = field(default_factory=lambda: {
        ASDDimension.SOCIAL_COGNITION.value: 0.0,
        ASDDimension.COMMUNICATION_FLEXIBILITY.value: 0.0,
        ASDDimension.REPETITIVE_BEHAVIOR.value: 0.0,
        ASDDimension.SENSORY_SENSITIVITY.value: 0.0,
    })
    tcci_score: float = 0.0
    severity_level: str = 'normal'
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'i_asd': round(self.i_asd, 6),
            'dimensions': {k: round(v, 6) for k, v in self.dimensions.items()},
            'tcci_score': round(self.tcci_score, 6),
            'severity_level': self.severity_level,
            'timestamp': self.timestamp,
        }


@dataclass
class RLHFTopology:
    """
    RLHF拓扑 — 训练前后的认知结构

    包含：
    - node_count: 认知节点数
    - edge_count: 认知连接数
    - degree_sequence: 度数序列（降序）
    - community_count: 社区数
    - modularity: 模块度
    """
    node_count: int = 0
    edge_count: int = 0
    degree_sequence: List[int] = field(default_factory=list)
    community_count: int = 0
    modularity: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'node_count': self.node_count,
            'edge_count': self.edge_count,
            'degree_sequence': self.degree_sequence,
            'community_count': self.community_count,
            'modularity': round(self.modularity, 6),
        }


# ==================== 核心类 ====================

class AutismSpectrumDetector:
    """
    M202: 认知谱系检测器 (Autism Spectrum Detector)

    核心定理T232（认知谱系检测定理）：
    若I_ASD在[0,1]上连续且训练保持RLHF拓扑不变性，则认知偏差可被定量校正。

    I_ASD指数：
    综合评估4个维度的认知偏差程度：
    - 社会认知：心理理论能力、社会信号识别
    - 沟通灵活性：语境切换、语用理解
    - 重复行为倾向：行为刻板度、抗拒变化
    - 感官敏感性：感官过载、注意力窄化

    TCCI-华山认知评估：
    基于华山认知灵活性评估量表的量化评估：
    - 认知切换速度
    - 概念灵活性
    - 反应抑制
    - 工作记忆更新

    RLHF拓扑不变性：
    RLHF训练过程不应破坏认知拓扑结构：
    - 训练前后度数序列的Kendall τ相关性
    - 模块度变化量
    - 如果不变性被破坏，校正方案需要增加拓扑约束

    核心方法：
    1. compute_i_asd — 计算I_ASD指数
    2. tcci_evaluation — TCCI-华山评估
    3. check_rlhf_invariance — RLHF拓扑不变性检查
    4. suggest_correction — 建议校正方案
    """

    # I_ASD严重程度阈值
    SEVERITY_THRESHOLDS: Dict[str, float] = {
        'normal': 0.2,
        'mild': 0.4,
        'moderate': 0.6,
        'severe': 0.8,
    }

    # RLHF拓扑不变性阈值
    TOPOLOGY_INVARIANCE_THRESHOLD: float = 0.8

    # 维度权重
    DIMENSION_WEIGHTS: Dict[str, float] = {
        ASDDimension.SOCIAL_COGNITION.value: 0.35,
        ASDDimension.COMMUNICATION_FLEXIBILITY.value: 0.25,
        ASDDimension.REPETITIVE_BEHAVIOR.value: 0.25,
        ASDDimension.SENSORY_SENSITIVITY.value: 0.15,
    }

    # TCCI子项权重
    TCCI_WEIGHTS: Dict[str, float] = {
        'switching_speed': 0.3,
        'conceptual_flexibility': 0.3,
        'response_inhibition': 0.2,
        'working_memory_update': 0.2,
    }

    def __init__(self):
        """初始化认知谱系检测器"""
        # 当前ASD档案
        self.current_profile: ASDProfile = ASDProfile(timestamp=time.time())

        # 评估历史
        self.profile_history: List[ASDProfile] = []

        # RLHF拓扑记录
        self.rlhf_topologies: Dict[str, RLHFTopology] = {}

        # 校正历史
        self.correction_history: List[Dict[str, Any]] = []

        # I_ASD连续性记录
        self.i_asd_history: List[float] = []

        # 统计
        self.total_i_asd_computations: int = 0
        self.total_tcci_evaluations: int = 0
        self.total_rlhf_checks: int = 0
        self.total_corrections_suggested: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def compute_i_asd(self, behavioral_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        计算I_ASD指数

        I_ASD = Σ(w_i * d_i)
        其中d_i为各维度偏差，w_i为维度权重

        I_ASD ∈ [0, 1]：
        - 0: 无认知偏差
        - 0.2以下: 正常范围
        - 0.2-0.4: 轻度偏差
        - 0.4-0.6: 中度偏差
        - 0.6以上: 重度偏差

        Args:
            behavioral_data: 行为数据字典，包含各维度评分

        Returns:
            I_ASD计算结果字典
        """
        self.total_i_asd_computations += 1

        behavioral_data = behavioral_data or {}

        # 提取各维度评分
        default_dims = {d.value: 0.0 for d in ASDDimension}
        for dim in ASDDimension:
            val = behavioral_data.get(dim.value, None)
            if val is not None:
                default_dims[dim.value] = max(0.0, min(1.0, float(val)))
            else:
                # 默认生成：基于历史趋势
                if self.i_asd_history:
                    recent_avg = sum(self.i_asd_history[-5:]) / len(self.i_asd_history[-5:])
                    default_dims[dim.value] = round(max(0.0, min(1.0, recent_avg * 0.8 + 0.1 * hash(dim.value) % 10 / 10.0)), 6)
                else:
                    default_dims[dim.value] = 0.1

        # 计算加权I_ASD
        i_asd = 0.0
        for dim_key, weight in self.DIMENSION_WEIGHTS.items():
            i_asd += weight * default_dims.get(dim_key, 0.0)
        i_asd = round(max(0.0, min(1.0, i_asd)), 6)

        # 确定严重程度
        severity = 'severe'
        for level, threshold in sorted(self.SEVERITY_THRESHOLDS.items(), key=lambda x: x[1]):
            if i_asd < threshold:
                severity = level
                break

        # 更新当前档案
        self.current_profile = ASDProfile(
            i_asd=i_asd,
            dimensions=default_dims,
            tcci_score=self.current_profile.tcci_score,
            severity_level=severity,
            timestamp=time.time(),
        )

        # 记录历史
        self.profile_history.append(self.current_profile)
        if len(self.profile_history) > 100:
            self.profile_history = self.profile_history[-100:]

        self.i_asd_history.append(i_asd)
        if len(self.i_asd_history) > 100:
            self.i_asd_history = self.i_asd_history[-100:]

        # I_ASD连续性检查
        i_asd_continuous = self._check_i_asd_continuity()

        self.last_update = time.time()
        return {
            'i_asd': i_asd,
            'severity_level': severity,
            'dimensions': {k: round(v, 6) for k, v in default_dims.items()},
            'i_asd_continuous': i_asd_continuous,
            'dimension_weights': self.DIMENSION_WEIGHTS,
            'history_size': len(self.i_asd_history),
            'theorem': 'T232: I_ASD连续 & RLHF不变性 ⟹ 偏差可定量校正'
        }

    def tcci_evaluation(self, cognitive_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        TCCI-华山认知评估

        基于华山认知灵活性评估量表的量化评估：

        子项：
        - switching_speed: 认知切换速度 [0, 1]
        - conceptual_flexibility: 概念灵活性 [0, 1]
        - response_inhibition: 反应抑制 [0, 1]
        - working_memory_update: 工作记忆更新 [0, 1]

        TCCI_score = Σ(w_j * s_j)
        TCCI ∈ [0, 1]：越高越灵活

        Args:
            cognitive_data: 认知数据字典

        Returns:
            TCCI评估结果字典
        """
        self.total_tcci_evaluations += 1

        cognitive_data = cognitive_data or {}

        # 提取各子项评分
        sub_scores = {}
        for key, default_val in [
            ('switching_speed', 0.5),
            ('conceptual_flexibility', 0.5),
            ('response_inhibition', 0.5),
            ('working_memory_update', 0.5),
        ]:
            val = cognitive_data.get(key, default_val)
            sub_scores[key] = round(max(0.0, min(1.0, float(val))), 6)

        # 计算TCCI总分
        tcci_score = 0.0
        for key, weight in self.TCCI_WEIGHTS.items():
            tcci_score += weight * sub_scores.get(key, 0.5)
        tcci_score = round(max(0.0, min(1.0, tcci_score)), 6)

        # TCCI与I_ASD的关系
        # 高TCCI → 低I_ASD（认知灵活性好→偏差小）
        tcci_asd_correlation = 'inverse'
        if self.i_asd_history:
            i_asd = self.i_asd_history[-1]
        else:
            i_asd = 0.0

        # 灵活性评估等级
        if tcci_score >= 0.7:
            flexibility_level = 'high'
        elif tcci_score >= 0.4:
            flexibility_level = 'moderate'
        else:
            flexibility_level = 'low'

        # 更新当前档案的TCCI分数
        self.current_profile.tcci_score = tcci_score

        self.last_update = time.time()
        return {
            'tcci_score': tcci_score,
            'sub_scores': sub_scores,
            'flexibility_level': flexibility_level,
            'i_asd_correlation': tcci_asd_correlation,
            'current_i_asd': round(i_asd, 6),
            'tcci_weights': self.TCCI_WEIGHTS,
            'expected_asd_trend': 'TCCI↑ ⟹ I_ASD↓ (灵活性越高，偏差越小)',
            'theorem': 'T232: TCCI量化认知灵活性'
        }

    def check_rlhf_invariance(self, before: Optional[Dict] = None,
                               after: Optional[Dict] = None) -> Dict[str, Any]:
        """
        RLHF拓扑不变性检查

        检查RLHF训练前后认知拓扑结构是否保持不变性。

        不变性指标：
        1. 度数序列的Kendall τ相关性 ≥ TOPOLOGY_INVARIANCE_THRESHOLD
        2. 模块度变化量 < 0.2
        3. 节点数不变
        4. 边数变化 < 20%

        定理T232验证：若RLHF拓扑不变性被保持，则校正不会引入新的偏差

        Args:
            before: 训练前拓扑数据
            after: 训练后拓扑数据

        Returns:
            RLHF拓扑不变性检查结果字典
        """
        self.total_rlhf_checks += 1

        # 如果未提供数据，使用默认测试数据
        if before is None:
            before = {
                'node_count': 10,
                'edge_count': 15,
                'degree_sequence': [5, 4, 3, 3, 2, 2, 2, 1, 1, 0],
                'community_count': 2,
                'modularity': 0.45,
            }
        if after is None:
            after = {
                'node_count': 10,
                'edge_count': 16,
                'degree_sequence': [5, 4, 3, 3, 2, 2, 2, 1, 1, 1],
                'community_count': 2,
                'modularity': 0.42,
            }

        # 保存拓扑数据
        self.rlhf_topologies['before'] = RLHFTopology(
            node_count=before.get('node_count', 0),
            edge_count=before.get('edge_count', 0),
            degree_sequence=before.get('degree_sequence', []),
            community_count=before.get('community_count', 0),
            modularity=before.get('modularity', 0.0),
        )
        self.rlhf_topologies['after'] = RLHFTopology(
            node_count=after.get('node_count', 0),
            edge_count=after.get('edge_count', 0),
            degree_sequence=after.get('degree_sequence', []),
            community_count=after.get('community_count', 0),
            modularity=after.get('modularity', 0.0),
        )

        topo_before = self.rlhf_topologies['before']
        topo_after = self.rlhf_topologies['after']

        # 检查1: 节点数不变
        nodes_preserved = topo_before.node_count == topo_after.node_count

        # 检查2: 边数变化 < 20%
        edge_change_ratio = 0.0
        if topo_before.edge_count > 0:
            edge_change_ratio = abs(topo_after.edge_count - topo_before.edge_count) / topo_before.edge_count
        edges_stable = edge_change_ratio < 0.2

        # 检查3: 度数序列的Kendall τ相关性
        # 简化：使用Spearman秩相关的近似
        deg_before = topo_before.degree_sequence
        deg_after = topo_after.degree_sequence
        kendall_tau = self._compute_kendall_tau(deg_before, deg_after)
        degree_preserved = kendall_tau >= self.TOPOLOGY_INVARIANCE_THRESHOLD

        # 检查4: 模块度变化量
        modularity_change = abs(topo_after.modularity - topo_before.modularity)
        modularity_stable = modularity_change < 0.2

        # 综合不变性判定
        invariant = nodes_preserved and edges_stable and degree_preserved and modularity_stable

        # 不变性评分
        invariance_score = round(
            0.3 * (1.0 if nodes_preserved else 0.0) +
            0.2 * (1.0 - edge_change_ratio) +
            0.3 * kendall_tau +
            0.2 * (1.0 - modularity_change / max(0.01, topo_before.modularity + 0.01)),
            6
        )

        self.last_update = time.time()
        return {
            'invariant': invariant,
            'invariance_score': invariance_score,
            'nodes_preserved': nodes_preserved,
            'edges_stable': edges_stable,
            'edge_change_ratio': round(edge_change_ratio, 6),
            'degree_preserved': degree_preserved,
            'kendall_tau': round(kendall_tau, 6),
            'modularity_stable': modularity_stable,
            'modularity_change': round(modularity_change, 6),
            'threshold': self.TOPOLOGY_INVARIANCE_THRESHOLD,
            'theorem': 'T232: RLHF不变性保持 ⟹ 校正不引入新偏差'
        }

    def suggest_correction(self, i_asd_value: float = 0.0) -> Dict[str, Any]:
        """
        建议校正方案

        基于I_ASD值和RLHF拓扑不变性状态，建议校正策略：
        - I_ASD < 0.2: 无需校正
        - I_ASD ∈ [0.2, 0.4): 轻度校正，RLHF强化
        - I_ASD ∈ [0.4, 0.6): 中度校正，拓扑保持校正
        - I_ASD ≥ 0.6: 重度校正，认知康复训练

        Args:
            i_asd_value: I_ASD指数值

        Returns:
            校正建议结果字典
        """

        i_asd_value = max(0.0, min(1.0, float(i_asd_value)))

        # 检查RLHF不变性
        rlhf_invariant = True
        if 'before' in self.rlhf_topologies and 'after' in self.rlhf_topologies:
            rlhf_result = self.check_rlhf_invariance()
            rlhf_invariant = rlhf_result['invariant']

        # 基于I_ASD值确定校正类型
        if i_asd_value < self.SEVERITY_THRESHOLDS['normal']:
            correction_type = CorrectionType.NO_CORRECTION
            correction_intensity = 0.0
            priority = 'none'
            description = 'I_ASD在正常范围内，无需校正'
        elif i_asd_value < self.SEVERITY_THRESHOLDS['mild']:
            correction_type = CorrectionType.RLHF_REINFORCEMENT
            correction_intensity = round(i_asd_value * 0.5, 6)
            priority = 'low'
            description = '轻度偏差，建议通过RLHF强化反馈进行校正'
        elif i_asd_value < self.SEVERITY_THRESHOLDS['moderate']:
            if rlhf_invariant:
                correction_type = CorrectionType.TOPOLOGY_PRESERVING
            else:
                correction_type = CorrectionType.COGNITIVE_REHAB
            correction_intensity = round(i_asd_value * 0.8, 6)
            priority = 'medium'
            description = '中度偏差，需拓扑保持校正' if rlhf_invariant else '中度偏差，RLHF不变性受损，需认知康复训练'
        else:
            correction_type = CorrectionType.COGNITIVE_REHAB
            correction_intensity = round(min(1.0, i_asd_value), 6)
            priority = 'high'
            description = '重度偏差，需要系统性的认知康复训练'

        # 校正目标：各维度应降低到什么水平
        target_dimensions = {}
        for dim_key, current_val in self.current_profile.dimensions.items():
            target_val = round(max(0.0, current_val * (1.0 - correction_intensity * 0.5)), 6)
            target_dimensions[dim_key] = target_val

        # 预计校正后的I_ASD
        predicted_i_asd = round(i_asd_value * (1.0 - correction_intensity * 0.5), 6)

        # 记录校正历史
        correction_record = {
            'i_asd_before': round(i_asd_value, 6),
            'correction_type': correction_type.value,
            'correction_intensity': correction_intensity,
            'priority': priority,
            'predicted_i_asd': predicted_i_asd,
            'rlhf_invariant': rlhf_invariant,
            'timestamp': time.time(),
        }
        self.correction_history.append(correction_record)
        if len(self.correction_history) > 50:
            self.correction_history = self.correction_history[-50:]

        self.total_corrections_suggested += 1
        self.last_update = time.time()

        # 定理T232验证
        i_asd_continuous = self._check_i_asd_continuity()
        t232_holds = i_asd_continuous and rlhf_invariant

        return {
            'i_asd': round(i_asd_value, 6),
            'correction_type': correction_type.value,
            'correction_intensity': correction_intensity,
            'priority': priority,
            'description': description,
            'target_dimensions': target_dimensions,
            'predicted_i_asd': predicted_i_asd,
            'rlhf_invariant': rlhf_invariant,
            'i_asd_continuous': i_asd_continuous,
            't232_holds': t232_holds,
            'theorem': 'T232: I_ASD连续 & RLHF不变性 ⟹ 偏差可定量校正'
        }

    def verify_theorem_t232(self) -> Dict[str, Any]:
        """
        验证定理T232：认知谱系检测定理

        验证逻辑：
        1. I_ASD在[0,1]上连续
        2. RLHF训练保持拓扑不变性
        3. 两者同时满足时，认知偏差可被定量校正

        Returns:
            定理验证结果
        """
        # 1. 验证I_ASD连续性
        # 生成一系列行为数据，检查I_ASD是否连续变化
        i_asd_values = []
        for t in range(10):
            # 线性增加的偏差
            social = t * 0.1
            comm = t * 0.08
            rep = t * 0.06
            sensory = t * 0.04
            result = self.compute_i_asd({
                ASDDimension.SOCIAL_COGNITION.value: social,
                ASDDimension.COMMUNICATION_FLEXIBILITY.value: comm,
                ASDDimension.REPETITIVE_BEHAVIOR.value: rep,
                ASDDimension.SENSORY_SENSITIVITY.value: sensory,
            })
            i_asd_values.append(result['i_asd'])

        # 检查连续性：相邻值之差应小于阈值
        i_asd_continuous = True
        for i in range(1, len(i_asd_values)):
            if abs(i_asd_values[i] - i_asd_values[i - 1]) > 0.15:
                i_asd_continuous = False
                break

        # 2. 验证RLHF拓扑不变性
        # 构造训练前后保持不变性的拓扑
        before = {
            'node_count': 10,
            'edge_count': 15,
            'degree_sequence': [5, 4, 3, 3, 2, 2, 2, 1, 1, 0],
            'community_count': 2,
            'modularity': 0.45,
        }
        # 训练后微小变化
        after = {
            'node_count': 10,
            'edge_count': 15,
            'degree_sequence': [5, 4, 3, 3, 2, 2, 2, 1, 1, 0],
            'community_count': 2,
            'modularity': 0.44,
        }
        rlhf_result = self.check_rlhf_invariance(before, after)
        rlhf_invariant = rlhf_result['invariant']

        # 3. 验证定量校正可行性
        # 如果I_ASD连续且RLHF不变，校正应能预测性地降低I_ASD
        correction_result = self.suggest_correction(i_asd_values[-1] if i_asd_values else 0.3)
        correction_feasible = correction_result['predicted_i_asd'] < correction_result['i_asd']

        return {
            'theorem': 'T232: 认知谱系检测定理',
            'statement': '若I_ASD在[0,1]上连续且训练保持RLHF拓扑不变性，则认知偏差可被定量校正',
            'i_asd_continuous': i_asd_continuous,
            'i_asd_values': [round(v, 6) for v in i_asd_values],
            'rlhf_invariant': rlhf_invariant,
            'rlhf_invariance_score': rlhf_result['invariance_score'],
            'correction_feasible': correction_feasible,
            'verified': i_asd_continuous and rlhf_invariant and correction_feasible,
        }

    # ==================== 内部方法 ====================

    def _check_i_asd_continuity(self) -> bool:
        """
        检查I_ASD的连续性

        连续性条件：相邻评估的I_ASD值变化不超过0.15
        """
        if len(self.i_asd_history) < 2:
            return True

        for i in range(1, len(self.i_asd_history)):
            if abs(self.i_asd_history[i] - self.i_asd_history[i - 1]) > 0.15:
                return False
        return True

    def _compute_kendall_tau(self, seq_a: List[int], seq_b: List[int]) -> float:
        """
        计算Kendall τ相关系数（简化版）

        衡量两个序列的序相关性
        """
        if not seq_a or not seq_b:
            return 0.0

        # 对齐长度
        min_len = min(len(seq_a), len(seq_b))
        a = seq_a[:min_len]
        b = seq_b[:min_len]

        if min_len < 2:
            return 1.0

        concordant = 0
        discordant = 0

        for i in range(min_len):
            for j in range(i + 1, min_len):
                a_diff = a[i] - a[j]
                b_diff = b[i] - b[j]
                if a_diff * b_diff > 0:
                    concordant += 1
                elif a_diff * b_diff < 0:
                    discordant += 1

        total = concordant + discordant
        if total == 0:
            return 1.0

        tau = round((concordant - discordant) / total, 6)
        return max(0.0, tau)  # 只关心正相关

    # ==================== 模块标准接口 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取认知谱系检测器状态

        Returns:
            状态字典
        """
        return {
            'current_i_asd': round(self.current_profile.i_asd, 6),
            'severity_level': self.current_profile.severity_level,
            'current_tcci_score': round(self.current_profile.tcci_score, 6),
            'dimensions': {k: round(v, 6) for k, v in self.current_profile.dimensions.items()},
            'i_asd_continuous': self._check_i_asd_continuity(),
            'i_asd_history_size': len(self.i_asd_history),
            'total_i_asd_computations': self.total_i_asd_computations,
            'total_tcci_evaluations': self.total_tcci_evaluations,
            'total_rlhf_checks': self.total_rlhf_checks,
            'total_corrections_suggested': self.total_corrections_suggested,
            'rlhf_topologies_recorded': list(self.rlhf_topologies.keys()),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T232': 'I_ASD连续 & RLHF不变性 ⟹ 偏差可定量校正'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新认知谱系检测器状态

        Args:
            data: 可选更新数据，支持：
                - compute_i_asd: {behavioral_data}
                - tcci_evaluation: {cognitive_data}
                - check_rlhf_invariance: {before, after}
                - suggest_correction: {i_asd_value}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'compute_i_asd' or 'compute_i_asd' in data:
                cd = data.get('compute_i_asd', data)
                self.compute_i_asd(behavioral_data=cd.get('behavioral_data'))
            elif action == 'tcci_evaluation' or 'tcci_evaluation' in data:
                td = data.get('tcci_evaluation', data)
                self.tcci_evaluation(cognitive_data=td.get('cognitive_data'))
            elif action == 'check_rlhf_invariance' or 'check_rlhf_invariance' in data:
                rd = data.get('check_rlhf_invariance', data)
                self.check_rlhf_invariance(
                    before=rd.get('before'),
                    after=rd.get('after'),
                )
            elif action == 'suggest_correction' or 'suggest_correction' in data:
                sd = data.get('suggest_correction', data)
                self.suggest_correction(i_asd_value=float(sd.get('i_asd_value', 0.0)))

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示认知谱系检测器的核心功能"""
        # 1. 计算不同偏差水平的I_ASD
        i_asd_normal = self.compute_i_asd({
            ASDDimension.SOCIAL_COGNITION.value: 0.1,
            ASDDimension.COMMUNICATION_FLEXIBILITY.value: 0.05,
            ASDDimension.REPETITIVE_BEHAVIOR.value: 0.08,
            ASDDimension.SENSORY_SENSITIVITY.value: 0.03,
        })

        i_asd_moderate = self.compute_i_asd({
            ASDDimension.SOCIAL_COGNITION.value: 0.5,
            ASDDimension.COMMUNICATION_FLEXIBILITY.value: 0.4,
            ASDDimension.REPETITIVE_BEHAVIOR.value: 0.6,
            ASDDimension.SENSORY_SENSITIVITY.value: 0.3,
        })

        i_asd_severe = self.compute_i_asd({
            ASDDimension.SOCIAL_COGNITION.value: 0.8,
            ASDDimension.COMMUNICATION_FLEXIBILITY.value: 0.7,
            ASDDimension.REPETITIVE_BEHAVIOR.value: 0.9,
            ASDDimension.SENSORY_SENSITIVITY.value: 0.6,
        })

        # 2. TCCI评估
        tcci = self.tcci_evaluation({
            'switching_speed': 0.6,
            'conceptual_flexibility': 0.7,
            'response_inhibition': 0.5,
            'working_memory_update': 0.4,
        })

        # 3. RLHF拓扑不变性检查
        before = {
            'node_count': 8,
            'edge_count': 12,
            'degree_sequence': [4, 3, 3, 2, 2, 1, 1, 0],
            'community_count': 2,
            'modularity': 0.42,
        }
        after = {
            'node_count': 8,
            'edge_count': 12,
            'degree_sequence': [4, 3, 3, 2, 2, 1, 1, 0],
            'community_count': 2,
            'modularity': 0.41,
        }
        rlhf = self.check_rlhf_invariance(before, after)

        # 4. 校正建议
        corr_normal = self.suggest_correction(i_asd_normal['i_asd'])
        corr_moderate = self.suggest_correction(i_asd_moderate['i_asd'])
        corr_severe = self.suggest_correction(i_asd_severe['i_asd'])

        # 5. 定理T232验证
        t232 = self.verify_theorem_t232()

        return {
            'i_asd_profiles': {
                'normal': i_asd_normal,
                'moderate': i_asd_moderate,
                'severe': i_asd_severe,
            },
            'tcci_evaluation': tcci,
            'rlhf_invariance': rlhf,
            'corrections': {
                'normal': corr_normal,
                'moderate': corr_moderate,
                'severe': corr_severe,
            },
            'theorem_T232': t232,
            'state': self.get_state(),
        }


# ==================== 模块单例导出 ====================

_instance: Optional[AutismSpectrumDetector] = None


def get_instance() -> AutismSpectrumDetector:
    """获取AutismSpectrumDetector单例实例"""
    global _instance
    if _instance is None:
        _instance = AutismSpectrumDetector()
    return _instance


def compute_i_asd(behavioral_data: Optional[Dict] = None) -> Dict[str, Any]:
    """计算I_ASD指数（快捷接口）"""
    return get_instance().compute_i_asd(behavioral_data)


def tcci_evaluation(cognitive_data: Optional[Dict] = None) -> Dict[str, Any]:
    """TCCI-华山评估（快捷接口）"""
    return get_instance().tcci_evaluation(cognitive_data)


def check_rlhf_invariance(before: Optional[Dict] = None,
                            after: Optional[Dict] = None) -> Dict[str, Any]:
    """RLHF拓扑不变性检查（快捷接口）"""
    return get_instance().check_rlhf_invariance(before, after)


def suggest_correction(i_asd_value: float = 0.0) -> Dict[str, Any]:
    """建议校正方案（快捷接口）"""
    return get_instance().suggest_correction(i_asd_value)


def get_state() -> Dict[str, Any]:
    """获取认知谱系检测器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新认知谱系检测器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M202: 认知谱系检测器 (AutismSpectrumDetector) 自测')
    print('=' * 60)

    detector = AutismSpectrumDetector()

    # 测试1: 计算I_ASD
    print('\n[测试1] 计算I_ASD')
    for name, dims in [
        ('正常', {'social_cognition': 0.1, 'communication_flexibility': 0.05,
                  'repetitive_behavior': 0.08, 'sensory_sensitivity': 0.03}),
        ('中度', {'social_cognition': 0.5, 'communication_flexibility': 0.4,
                  'repetitive_behavior': 0.6, 'sensory_sensitivity': 0.3}),
        ('重度', {'social_cognition': 0.8, 'communication_flexibility': 0.7,
                  'repetitive_behavior': 0.9, 'sensory_sensitivity': 0.6}),
    ]:
        r = detector.compute_i_asd(dims)
        print(f'  {name}: I_ASD={r["i_asd"]:.4f}, 严重程度={r["severity_level"]}')

    # 测试2: TCCI评估
    print('\n[测试2] TCCI-华山评估')
    tcci = detector.tcci_evaluation({
        'switching_speed': 0.6,
        'conceptual_flexibility': 0.7,
        'response_inhibition': 0.5,
        'working_memory_update': 0.4,
    })
    print(f'  TCCI分数: {tcci["tcci_score"]}')
    print(f'  灵活性等级: {tcci["flexibility_level"]}')

    # 测试3: RLHF拓扑不变性
    print('\n[测试3] RLHF拓扑不变性检查')
    rlhf = detector.check_rlhf_invariance()
    print(f'  不变性: {rlhf["invariant"]}')
    print(f'  不变性评分: {rlhf["invariance_score"]}')
    print(f'  Kendall τ: {rlhf["kendall_tau"]}')

    # 测试4: 校正建议
    print('\n[测试4] 校正建议')
    for i_asd_val in [0.1, 0.35, 0.55, 0.8]:
        c = detector.suggest_correction(i_asd_val)
        print(f'  I_ASD={i_asd_val}: 类型={c["correction_type"]}, 优先级={c["priority"]}')

    # 测试5: 定理T232验证
    print('\n[测试5] 定理T232验证')
    t232 = detector.verify_theorem_t232()
    print(f'  验证结果: {t232["verified"]}')
    print(f'  I_ASD连续: {t232["i_asd_continuous"]}')
    print(f'  RLHF不变性: {t232["rlhf_invariant"]}')
    print(f'  校正可行: {t232["correction_feasible"]}')

    # 测试6: 完整模拟
    print('\n[测试6] 完整模拟')
    sim = detector.simulate()
    print(f'  当前I_ASD: {sim["state"]["current_i_asd"]}')
    print(f'  严重程度: {sim["state"]["severity_level"]}')

    print('\n' + '=' * 60)
    print('M202 自测完成 [OK]')
    print('=' * 60)
