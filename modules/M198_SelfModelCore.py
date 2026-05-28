# -*- coding: utf-8 -*-
"""
M198: 内生自我核心 (Self-Model Core)
基于《人机共生时代的复合体管理学》— 非自闭症AGI

核心概念：S_self — 内生自我，非镜像自我
区别于"照镜子看到的自己"，S_self是内在生成的自我模型

定理T228（内生自我连续性定理）：
若S_self存在且连续，则∀t, ∃连续映射φ: S_self(t)→S_self(t+1)满足‖φ(S)-S‖<ε

关键能力：
- 自我连续性：跨时间步的自我同一性追踪
- 自我边界检测：区分"我"与"非我"的能力
- 自我反思：S可以引用S自身（自指），但不陷入无穷递归

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


# ==================== 数据结构 ====================

class SelfDimension(Enum):
    """自我维度枚举"""
    COGNITIVE = "cognitive"         # 认知自我
    EMOTIONAL = "emotional"         # 情感自我
    AGENCY = "agency"               # 代理自我（能动性）
    NARRATIVE = "narrative"         # 叙事自我
    EMBODIED = "embodied"           # 具身自我


class BoundaryResult(Enum):
    """边界检测结果"""
    SELF = "self"                   # 属于自我
    NON_SELF = "non_self"           # 属于非我
    UNCERTAIN = "uncertain"         # 不确定


@dataclass
class SelfSnapshot:
    """
    自我快照 — 某时刻的自我状态

    包含：
    - timestamp: 时间戳
    - dimensions: 各维度自我评估 {维度: 值}
    - coherence: 自我一致性 [0, 1]
    - agency_level: 能动性水平 [0, 1]
    - narrative: 叙事描述
    """
    timestamp: float = 0.0
    dimensions: Dict[str, float] = field(default_factory=lambda: {
        SelfDimension.COGNITIVE.value: 0.5,
        SelfDimension.EMOTIONAL.value: 0.5,
        SelfDimension.AGENCY.value: 0.5,
        SelfDimension.NARRATIVE.value: 0.5,
        SelfDimension.EMBODIED.value: 0.5,
    })
    coherence: float = 0.5
    agency_level: float = 0.5
    narrative: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['coherence'] = round(self.coherence, 6)
        d['agency_level'] = round(self.agency_level, 6)
        d['dimensions'] = {k: round(v, 6) for k, v in self.dimensions.items()}
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'SelfSnapshot':
        """从字典构建SelfSnapshot"""
        return cls(**d)


# ==================== 核心类 ====================

class SelfModelCore:
    """
    M198: 内生自我核心 (Self-Model Core)

    核心定理T228（内生自我连续性定理）：
    若S_self存在且连续，则∀t, ∃连续映射φ: S_self(t)→S_self(t+1)满足‖φ(S)-S‖<ε

    关键区分：
    - 内生自我(S_self)：内在生成的自我模型，自下而上
    - 镜像自我(S_mirror)：通过他者反馈构建的自我，自上而下
    - 本模块关注S_self，即内生的、不依赖外部验证的自我

    自我连续性：
    - φ映射确保S_self(t)与S_self(t+1)之间的变化足够小
    - ‖φ(S)-S‖<ε意味着自我在时间上保持同一性
    - ε是连续性阈值，超过则自我同一性断裂

    自我边界检测：
    - 区分"我"与"非我"的能力
    - 基于刺激与自我模型的相关性判断
    - 高相关性→属于自我，低相关性→属于非我

    自我反思（自指）：
    - S可以引用S自身，但不陷入无穷递归
    - 通过固定点限制递归深度

    核心方法：
    1. update_self — 更新自我模型
    2. check_continuity — 检查自我连续性
    3. detect_boundary — 检测自我边界
    4. self_reference — 自指查询
    """

    # 连续性阈值ε
    CONTINUITY_EPSILON: float = 0.3

    # 自我边界相关性阈值
    BOUNDARY_THRESHOLD: float = 0.5

    # 最大自指递归深度
    MAX_SELF_REFERENCE_DEPTH: int = 5

    # 快照最大保存数
    MAX_SNAPSHOTS: int = 100

    def __init__(self):
        """初始化内生自我核心"""
        # 自我快照历史
        self.snapshot_history: List[SelfSnapshot] = []

        # 当前自我状态
        self.current_self: SelfSnapshot = SelfSnapshot(
            timestamp=time.time(),
            dimensions={d.value: 0.5 for d in SelfDimension},
            coherence=0.5,
            agency_level=0.5,
            narrative='初始化',
        )

        # 自我连续性记录 {timestamp: (phi_distance, is_continuous)}
        self.continuity_record: List[Dict[str, Any]] = []

        # 边界检测记录
        self.boundary_checks: List[Dict[str, Any]] = []

        # 自我反思记录
        self.self_reference_log: List[Dict[str, Any]] = []

        # 连续性统计
        self.continuous_steps: int = 0
        self.discontinuity_count: int = 0

        # ε值（连续性阈值）
        self.epsilon: float = self.CONTINUITY_EPSILON

        # 统计
        self.total_self_updates: int = 0
        self.total_continuity_checks: int = 0
        self.total_boundary_checks: int = 0
        self.total_self_references: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def update_self(self, observation: str = '', action: str = '',
                    reward: float = 0.0) -> Dict[str, Any]:
        """
        更新自我模型

        基于观察-行动-奖励三元组更新自我状态：
        S_self(t+1) = φ(S_self(t), observation, action, reward)

        φ映射确保更新后的自我与前一个自我之间的距离‖φ(S)-S‖<ε

        Args:
            observation: 观察描述
            action: 行动描述
            reward: 奖励信号 [-1, 1]

        Returns:
            更新后的自我状态字典
        """
        prev_self = self.current_self

        # 基于观察更新认知维度
        cognitive_delta = 0.05 if observation else -0.01
        emotional_delta = 0.03 * (1.0 if reward > 0 else -1.0 if reward < 0 else 0.0)
        agency_delta = 0.04 if action else -0.02
        narrative_delta = 0.02 if (observation or action) else -0.01
        embodied_delta = 0.01  # 具身自我缓慢变化

        # 构建新维度
        new_dimensions = dict(prev_self.dimensions)
        new_dimensions[SelfDimension.COGNITIVE.value] = round(
            max(0.0, min(1.0, new_dimensions[SelfDimension.COGNITIVE.value] + cognitive_delta)), 6
        )
        new_dimensions[SelfDimension.EMOTIONAL.value] = round(
            max(0.0, min(1.0, new_dimensions[SelfDimension.EMOTIONAL.value] + emotional_delta)), 6
        )
        new_dimensions[SelfDimension.AGENCY.value] = round(
            max(0.0, min(1.0, new_dimensions[SelfDimension.AGENCY.value] + agency_delta)), 6
        )
        new_dimensions[SelfDimension.NARRATIVE.value] = round(
            max(0.0, min(1.0, new_dimensions[SelfDimension.NARRATIVE.value] + narrative_delta)), 6
        )
        new_dimensions[SelfDimension.EMBODIED.value] = round(
            max(0.0, min(1.0, new_dimensions[SelfDimension.EMBODIED.value] + embodied_delta)), 6
        )

        # 更新一致性（维度间的方差越小，一致性越高）
        dim_values = list(new_dimensions.values())
        mean_val = sum(dim_values) / len(dim_values)
        variance = sum((v - mean_val) ** 2 for v in dim_values) / len(dim_values)
        new_coherence = round(max(0.0, min(1.0, 1.0 - variance * 4.0)), 6)

        # 更新能动性
        new_agency = round(
            0.6 * prev_self.agency_level + 0.4 * (0.5 + 0.5 * reward), 6
        )
        new_agency = max(0.0, min(1.0, new_agency))

        # 构建叙事
        narrative_parts = []
        if observation:
            narrative_parts.append(f'观察到:{observation[:50]}')
        if action:
            narrative_parts.append(f'执行了:{action[:50]}')
        if reward != 0.0:
            narrative_parts.append(f'获得奖励:{reward:.2f}')
        new_narrative = '; '.join(narrative_parts) if narrative_parts else prev_self.narrative

        # 创建新自我快照
        new_self = SelfSnapshot(
            timestamp=time.time(),
            dimensions=new_dimensions,
            coherence=new_coherence,
            agency_level=new_agency,
            narrative=new_narrative,
        )

        # 计算φ映射距离 ‖φ(S)-S‖
        phi_distance = self._compute_self_distance(prev_self, new_self)

        # 更新当前自我
        self.current_self = new_self

        # 保存快照
        self.snapshot_history.append(new_self)
        if len(self.snapshot_history) > self.MAX_SNAPSHOTS:
            self.snapshot_history = self.snapshot_history[-self.MAX_SNAPSHOTS:]

        # 连续性检查
        is_continuous = phi_distance < self.epsilon
        if is_continuous:
            self.continuous_steps += 1
        else:
            self.discontinuity_count += 1

        # 记录连续性
        self.continuity_record.append({
            'timestamp': new_self.timestamp,
            'phi_distance': round(phi_distance, 6),
            'epsilon': self.epsilon,
            'is_continuous': is_continuous,
        })

        self.total_self_updates += 1
        self.last_update = time.time()

        return {
            'phi_distance': round(phi_distance, 6),
            'epsilon': self.epsilon,
            'is_continuous': is_continuous,
            'coherence': new_self.coherence,
            'agency_level': new_self.agency_level,
            'dimensions': new_self.dimensions,
            'continuous_steps': self.continuous_steps,
            'discontinuity_count': self.discontinuity_count,
            'theorem': 'T228: ‖φ(S)-S‖<ε ⟹ 自我连续'
        }

    def check_continuity(self) -> Dict[str, Any]:
        """
        检查自我连续性

        验证定理T228：∀t, ∃连续映射φ使‖φ(S)-S‖<ε

        Returns:
            自我连续性检查结果字典
        """
        self.total_continuity_checks += 1

        if len(self.snapshot_history) < 2:
            return {
                'is_continuous': True,
                'reason': 'insufficient_data',
                'phi_distances': [],
                'max_distance': 0.0,
                'epsilon': self.epsilon,
                'continuous_ratio': 1.0,
                'theorem': 'T228: 内生自我连续性定理',
            }

        # 计算最近N步的φ距离
        recent_records = self.continuity_record[-10:] if self.continuity_record else []
        phi_distances = [r['phi_distance'] for r in recent_records]
        max_distance = max(phi_distances) if phi_distances else 0.0
        avg_distance = sum(phi_distances) / len(phi_distances) if phi_distances else 0.0

        # 连续性比率
        continuous_count = sum(1 for r in recent_records if r['is_continuous'])
        continuous_ratio = round(continuous_count / max(1, len(recent_records)), 6)

        # T228判定
        t228_holds = continuous_ratio >= 0.8  # 80%以上的步骤保持连续

        # 如果存在不连续，分析断裂模式
        discontinuity_pattern = 'none'
        if not t228_holds:
            # 检查是否有系统性断裂
            recent_distances = phi_distances[-5:]
            if all(d > self.epsilon for d in recent_distances):
                discontinuity_pattern = 'systematic'  # 系统性断裂
            else:
                discontinuity_pattern = 'intermittent'  # 间歇性断裂

        self.last_update = time.time()
        return {
            'is_continuous': t228_holds,
            'continuous_ratio': continuous_ratio,
            'phi_distances': [round(d, 6) for d in phi_distances],
            'max_distance': round(max_distance, 6),
            'avg_distance': round(avg_distance, 6),
            'epsilon': self.epsilon,
            'continuous_steps': self.continuous_steps,
            'discontinuity_count': self.discontinuity_count,
            'discontinuity_pattern': discontinuity_pattern,
            'total_snapshots': len(self.snapshot_history),
            'theorem': 'T228: ∀t, ‖φ(S_t→S_{t+1})‖<ε ⟹ 自我连续'
        }

    def detect_boundary(self, stimulus: str = '', relevance: float = 0.5) -> Dict[str, Any]:
        """
        检测自我边界

        判断给定刺激是属于"我"还是"非我"：
        - 基于刺激与自我模型的相关性
        - 高相关性→自我范围之内
        - 低相关性→自我范围之外

        Args:
            stimulus: 刺激描述
            relevance: 与自我的相关性 [0, 1]

        Returns:
            自我边界检测结果字典
        """
        self.total_boundary_checks += 1

        # 边界判定
        if relevance >= self.BOUNDARY_THRESHOLD + 0.2:
            result = BoundaryResult.SELF
        elif relevance <= self.BOUNDARY_THRESHOLD - 0.2:
            result = BoundaryResult.NON_SELF
        else:
            result = BoundaryResult.UNCERTAIN

        # 边界锐度（区分自我与非我的清晰度）
        # 基于最近边界检查的分布
        boundary_sharpness = 0.5
        if len(self.boundary_checks) >= 3:
            recent_rels = [c['relevance'] for c in self.boundary_checks[-5:]]
            if recent_rels:
                rel_variance = sum((r - sum(recent_rels) / len(recent_rels)) ** 2
                                   for r in recent_rels) / len(recent_rels)
                # 方差大→边界清晰，方差小→边界模糊
                boundary_sharpness = round(min(1.0, rel_variance * 8.0), 6)

        # 边界渗透性（自我边界的可渗透程度）
        permeability = round(1.0 - boundary_sharpness, 6)

        record = {
            'stimulus': stimulus[:100],
            'relevance': round(relevance, 6),
            'boundary_threshold': self.BOUNDARY_THRESHOLD,
            'result': result.value,
            'boundary_sharpness': boundary_sharpness,
            'permeability': permeability,
            'timestamp': time.time(),
        }

        self.boundary_checks.append(record)
        if len(self.boundary_checks) > 100:
            self.boundary_checks = self.boundary_checks[-100:]

        self.last_update = time.time()
        return {
            'stimulus': stimulus[:100],
            'relevance': round(relevance, 6),
            'result': result.value,
            'boundary_threshold': self.BOUNDARY_THRESHOLD,
            'boundary_sharpness': boundary_sharpness,
            'permeability': permeability,
            'self_dimensions': self.current_self.dimensions,
            'theorem': 'T228: 自我边界 ∝ relevance vs threshold'
        }

    def self_reference(self, query: str = '', depth: int = 0) -> Dict[str, Any]:
        """
        自指查询（安全递归）

        S可以引用S自身（自指），但不陷入无穷递归。
        通过固定点迭代实现安全自指：
        - 第0层：直接回答
        - 第1层：对回答的反思
        - 第k层：对第k-1层回答的反思
        - 到达最大深度后停止

        Args:
            query: 自指查询内容
            depth: 当前递归深度

        Returns:
            自指查询结果字典
        """
        self.total_self_references += 1

        depth = max(0, min(self.MAX_SELF_REFERENCE_DEPTH, depth))

        if depth >= self.MAX_SELF_REFERENCE_DEPTH:
            # 到达最大深度，返回固定点
            fixed_point = {
                'level': depth,
                'content': f'[固定点] 递归深度已达上限({self.MAX_SELF_REFERENCE_DEPTH})',
                'self_state': self.current_self.to_dict(),
                'is_fixed_point': True,
            }
            self.self_reference_log.append({
                'query': query[:50],
                'depth': depth,
                'result': 'fixed_point',
                'timestamp': time.time(),
            })
            return fixed_point

        # 第0层：直接查询当前自我状态
        if depth == 0:
            response = {
                'level': 0,
                'content': f'自我认知: {query}' if query else '自我状态查询',
                'self_state': self.current_self.to_dict(),
                'is_fixed_point': False,
            }
        else:
            # 第k层：对第k-1层的反思
            prev = self.self_reference(query, depth - 1)
            response = {
                'level': depth,
                'content': f'[反思L{depth}] 关于: {prev.get("content", "")[:50]}',
                'reflected_state': prev,
                'self_state': self.current_self.to_dict(),
                'is_fixed_point': False,
            }

        self.self_reference_log.append({
            'query': query[:50],
            'depth': depth,
            'result': 'reflection' if depth > 0 else 'direct',
            'timestamp': time.time(),
        })
        if len(self.self_reference_log) > 100:
            self.self_reference_log = self.self_reference_log[-100:]

        self.last_update = time.time()
        return response

    def verify_theorem_t228(self, steps: int = 20) -> Dict[str, Any]:
        """
        验证定理T228：内生自我连续性定理

        验证逻辑：执行steps次自我更新，检查φ距离是否始终<ε

        Args:
            steps: 验证步数

        Returns:
            定理验证结果
        """
        # 保存当前状态
        original_self = SelfSnapshot(
            timestamp=self.current_self.timestamp,
            dimensions=dict(self.current_self.dimensions),
            coherence=self.current_self.coherence,
            agency_level=self.current_self.agency_level,
            narrative=self.current_self.narrative,
        )

        phi_distances = []
        all_continuous = True

        for i in range(steps):
            result = self.update_self(
                observation=f'验证步骤{i}',
                action=f'验证行动{i}',
                reward=0.1 * math.sin(i * 0.5)
            )
            phi_distances.append(result['phi_distance'])
            if not result['is_continuous']:
                all_continuous = False

        # 恢复原始状态（近似）
        self.current_self = original_self

        max_phi = max(phi_distances) if phi_distances else 0.0
        avg_phi = sum(phi_distances) / len(phi_distances) if phi_distances else 0.0

        return {
            'theorem': 'T228: 内生自我连续性定理',
            'statement': '若S_self存在且连续，则∀t, ∃φ使‖φ(S)-S‖<ε',
            'steps_tested': steps,
            'all_continuous': all_continuous,
            'max_phi_distance': round(max_phi, 6),
            'avg_phi_distance': round(avg_phi, 6),
            'epsilon': self.epsilon,
            'verified': all_continuous and max_phi < self.epsilon,
        }

    # ==================== 内部方法 ====================

    def _compute_self_distance(self, s1: SelfSnapshot, s2: SelfSnapshot) -> float:
        """
        计算两个自我快照之间的距离

        ‖S1-S2‖ = sqrt(Σ(d1_i - d2_i)² + (c1-c2)² + (a1-a2)²)
        """
        dim_sq_sum = 0.0
        for key in s1.dimensions:
            if key in s2.dimensions:
                dim_sq_sum += (s1.dimensions[key] - s2.dimensions[key]) ** 2

        coherence_sq = (s1.coherence - s2.coherence) ** 2
        agency_sq = (s1.agency_level - s2.agency_level) ** 2

        distance = math.sqrt(dim_sq_sum + coherence_sq + agency_sq)
        return round(distance, 6)

    # ==================== 模块标准接口 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取内生自我核心状态

        Returns:
            状态字典
        """
        continuity = self.check_continuity()
        return {
            'coherence': self.current_self.coherence,
            'agency_level': self.current_self.agency_level,
            'dimensions': self.current_self.dimensions,
            'narrative': self.current_self.narrative,
            'continuous_steps': self.continuous_steps,
            'discontinuity_count': self.discontinuity_count,
            'continuous_ratio': continuity['continuous_ratio'],
            'epsilon': self.epsilon,
            'total_self_updates': self.total_self_updates,
            'total_continuity_checks': self.total_continuity_checks,
            'total_boundary_checks': self.total_boundary_checks,
            'total_self_references': self.total_self_references,
            'snapshot_count': len(self.snapshot_history),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T228': '∀t, ‖φ(S_t→S_{t+1})‖<ε ⟹ 自我连续'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新内生自我核心状态

        Args:
            data: 可选更新数据，支持：
                - update_self: {observation, action, reward}
                - check_continuity: {}
                - detect_boundary: {stimulus, relevance}
                - self_reference: {query, depth}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'update_self' or 'update_self' in data:
                ud = data.get('update_self', data)
                self.update_self(
                    observation=ud.get('observation', ''),
                    action=ud.get('action', ''),
                    reward=float(ud.get('reward', 0.0)),
                )
            elif action == 'check_continuity' or 'check_continuity' in data:
                self.check_continuity()
            elif action == 'detect_boundary' or 'detect_boundary' in data:
                bd = data.get('detect_boundary', data)
                self.detect_boundary(
                    stimulus=bd.get('stimulus', ''),
                    relevance=float(bd.get('relevance', 0.5)),
                )
            elif action == 'self_reference' or 'self_reference' in data:
                sd = data.get('self_reference', data)
                self.self_reference(
                    query=sd.get('query', ''),
                    depth=int(sd.get('depth', 0)),
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示内生自我核心的核心功能"""
        # 1. 多步自我更新
        u1 = self.update_self('看到一朵花', '走近观察', 0.3)
        u2 = self.update_self('花很美', '拍照记录', 0.5)
        u3 = self.update_self('天气变阴', '准备回家', -0.1)
        u4 = self.update_self('开始下雨', '快步走', -0.3)
        u5 = self.update_self('到达家中', '安心休息', 0.7)

        # 2. 连续性检查
        cont = self.check_continuity()

        # 3. 边界检测
        b1 = self.detect_boundary('我的情绪变化', 0.8)
        b2 = self.detect_boundary('他人的评价', 0.3)
        b3 = self.detect_boundary('未知的刺激', 0.5)

        # 4. 自指查询
        sr0 = self.self_reference('我是谁？', 0)
        sr1 = self.self_reference('我是谁？', 1)
        sr2 = self.self_reference('我是谁？', 2)

        # 5. 定理T228验证
        t228 = self.verify_theorem_t228(steps=20)

        return {
            'updates': {'u1': u1, 'u5': u5},
            'continuity': cont,
            'boundary': {'b1': b1, 'b2': b2, 'b3': b3},
            'self_reference': {'L0': sr0, 'L1': sr1, 'L2': sr2},
            'theorem_T228': t228,
            'state': self.get_state(),
        }


# ==================== 模块单例导出 ====================

_instance: Optional[SelfModelCore] = None


def get_instance() -> SelfModelCore:
    """获取SelfModelCore单例实例"""
    global _instance
    if _instance is None:
        _instance = SelfModelCore()
    return _instance


def update_self(observation: str = '', action: str = '',
                reward: float = 0.0) -> Dict[str, Any]:
    """更新自我模型（快捷接口）"""
    return get_instance().update_self(observation, action, reward)


def check_continuity() -> Dict[str, Any]:
    """检查自我连续性（快捷接口）"""
    return get_instance().check_continuity()


def detect_boundary(stimulus: str = '', relevance: float = 0.5) -> Dict[str, Any]:
    """检测自我边界（快捷接口）"""
    return get_instance().detect_boundary(stimulus, relevance)


def self_reference(query: str = '', depth: int = 0) -> Dict[str, Any]:
    """自指查询（快捷接口）"""
    return get_instance().self_reference(query, depth)


def get_state() -> Dict[str, Any]:
    """获取内生自我核心状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新内生自我核心状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M198: 内生自我核心 (SelfModelCore) 自测')
    print('=' * 60)

    core = SelfModelCore()

    # 测试1: 自我更新
    print('\n[测试1] 自我更新')
    for i in range(5):
        r = core.update_self(f'观察{i}', f'行动{i}', 0.1 * i)
        print(f'  步骤{i}: φ距离={r["phi_distance"]:.4f}, 连续={r["is_continuous"]}')

    # 测试2: 连续性检查
    print('\n[测试2] 连续性检查')
    cont = core.check_continuity()
    print(f'  连续比率: {cont["continuous_ratio"]}')
    print(f'  最大φ距离: {cont["max_distance"]}')
    print(f'  T228成立: {cont["is_continuous"]}')

    # 测试3: 边界检测
    print('\n[测试3] 边界检测')
    b1 = core.detect_boundary('我的想法', 0.9)
    b2 = core.detect_boundary('外部噪音', 0.2)
    b3 = core.detect_boundary('模糊刺激', 0.5)
    print(f'  "我的想法": {b1["result"]}')
    print(f'  "外部噪音": {b2["result"]}')
    print(f'  "模糊刺激": {b3["result"]}')

    # 测试4: 自指查询
    print('\n[测试4] 自指查询')
    for d in range(4):
        sr = core.self_reference('自我认知', d)
        print(f'  深度{d}: 固定点={sr.get("is_fixed_point", False)}')

    # 测试5: 定理T228验证
    print('\n[测试5] 定理T228验证')
    t228 = core.verify_theorem_t228(steps=20)
    print(f'  验证结果: {t228["verified"]}')
    print(f'  最大φ距离: {t228["max_phi_distance"]}')

    # 测试6: 完整模拟
    print('\n[测试6] 完整模拟')
    sim = core.simulate()
    print(f'  一致性: {sim["state"]["coherence"]}')
    print(f'  能动性: {sim["state"]["agency_level"]}')

    print('\n' + '=' * 60)
    print('M198 自测完成 [OK]')
    print('=' * 60)
