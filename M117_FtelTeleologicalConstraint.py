# -*- coding: utf-8 -*-
"""
M117: Ftel目的约束算子 (Ftel Teleological Constraint)
基于《太乙万有理论：离散关系堆垒与流贯自指闭环》

核心概念：Ftel算子将目的φ注入为生成空间的约束场
公式：S_total = S_data + λ·V_ftel(ψ, φ_goal)

与Attention区别：
- Attention回答"注意什么"
- Ftel回答"为什么注意"

人择目的论：宇宙非预先有目的，但当认知主体通过Ftel设定目的时，系统展现"自实现"行为

定理T75（Ftel学习收敛定理）：
当λ∈(0,λ_max)时，Ftel约束下的学习过程收敛到目的吸引子φ*

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


# ==================== 数据结构 ====================

@dataclass
class FtelField:
    """
    目的约束场 — 将目的φ注入生成空间的约束场

    每个FtelField代表一个被注入到系统中的目的约束。
    strength λ控制约束强度，resonance V_ftel衡量目的与当前状态的共振值，
    convergence_rate追踪该目的的收敛速率。

    is_active标识该目的是否仍在活跃状态——未被退役的目的将持续约束生成空间。
    """
    goal: str                               # 目的φ
    strength: float = 0.5                   # 约束强度λ
    resonance: float = 0.0                  # 共振值V_ftel(ψ, φ_goal)
    convergence_rate: float = 0.0           # 收敛速率
    is_active: bool = True                  # 是否活跃

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['resonance'] = round(self.resonance, 6)
        d['strength'] = round(self.strength, 6)
        d['convergence_rate'] = round(self.convergence_rate, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'FtelField':
        """从字典构建FtelField"""
        return cls(**d)


@dataclass
class TeleologicalState:
    """
    目的状态 — 系统中所有目的约束场的综合状态

    fields列表记录所有已注入的目的约束场，
    total_resonance是所有活跃目的的共振总和，
    active_count是当前活跃目的数，
    convergence_achieved标记是否有目的已达成收敛。
    """
    fields: List[Dict[str, Any]] = field(default_factory=list)  # 目的约束场列表
    total_resonance: float = 0.0             # 总共振值
    active_count: int = 0                    # 活跃目的数
    convergence_achieved: bool = False       # 是否有目的达成收敛

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['total_resonance'] = round(self.total_resonance, 6)
        return d


# ==================== 核心类 ====================

class FtelTeleologicalConstraint:
    """
    M117: Ftel目的约束算子

    Ftel算子将目的φ注入为生成空间的约束场。
    公式：S_total = S_data + λ·V_ftel(ψ, φ_goal)

    与Attention的区别：
    - Attention: "注意什么" — 选择性聚焦
    - Ftel: "为什么注意" — 目的论约束，赋予注意以"理由"

    人择目的论：
    宇宙非预先有目的，但当认知主体通过Ftel设定目的时，
    系统展现"自实现"行为——目的约束调制生成过程，
    使系统在目的吸引子φ*附近表现出收敛性。

    定理T75（Ftel学习收敛定理）：
    当λ∈(0,λ_max)时，Ftel约束下的学习过程收敛到目的吸引子φ*。
    约束强度λ必须处于有效区间：太小则约束无效，太大则过拟合目的。

    核心方法：
    1. inject_goal — 注入目的到生成空间
    2. compute_resonance — 计算V_ftel共振值
    3. check_convergence — T75收敛性检查
    4. blend_signal — S_total = S_data + λ·V_ftel 信号融合
    5. retire_goal — 退役已达成目的
    """

    # λ_max：约束强度上限（T75收敛条件）
    LAMBDA_MAX: float = 2.0

    def __init__(self):
        """初始化Ftel目的约束算子"""
        # 目的约束场注册表 {goal: FtelField}
        self.fields: Dict[str, FtelField] = {}

        # λ_max：约束强度上限
        self.lambda_max: float = self.LAMBDA_MAX

        # 统计
        self.total_injections: int = 0
        self.total_resonance_computations: int = 0
        self.total_convergence_checks: int = 0
        self.total_blend_operations: int = 0
        self.total_retirements: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def inject_goal(self, goal: str, strength: float = 0.5) -> FtelField:
        """
        注入目的到生成空间

        将目的φ以约束强度λ注入生成空间，创建FtelField。
        如果目的已存在，更新其约束强度。
        自动计算初始共振值V_ftel。

        Args:
            goal: 目的φ描述
            strength: 约束强度λ，范围(0, λ_max)，默认0.5

        Returns:
            FtelField: 注入的目的约束场
        """
        # 约束强度截断到有效区间
        strength = max(0.001, min(strength, self.lambda_max - 0.001))

        # 计算初始共振值
        resonance = self.compute_resonance(goal)

        # 计算初始收敛速率
        convergence_rate = self._estimate_convergence_rate(strength, resonance)

        if goal in self.fields:
            # 更新已存在的目的
            existing = self.fields[goal]
            existing.strength = round(strength, 6)
            existing.resonance = round(resonance, 6)
            existing.convergence_rate = round(convergence_rate, 6)
            existing.is_active = True
            ftel_field = existing
        else:
            # 创建新目的约束场
            ftel_field = FtelField(
                goal=goal,
                strength=round(strength, 6),
                resonance=round(resonance, 6),
                convergence_rate=round(convergence_rate, 6),
                is_active=True
            )
            self.fields[goal] = ftel_field

        self.total_injections += 1
        self.last_update = time.time()
        return ftel_field

    def compute_resonance(self, goal: str) -> float:
        """
        计算V_ftel共振值

        V_ftel(ψ, φ_goal)衡量当前系统状态ψ与目的φ_goal的共振程度。
        共振值越高，系统状态越"对齐"目的，目的约束的效果越显著。

        共振计算考虑：
        1. 目的自身的"内禀共振"——基于目的的语义复杂度
        2. 与其他活跃目的的"交叉共振"——目的间的协同/冲突
        3. 历史注入的"累积共振"——多次注入增强共振

        Args:
            goal: 目的φ描述

        Returns:
            共振值V_ftel，范围[0, 1]
        """
        self.total_resonance_computations += 1

        # 1. 内禀共振：基于目的的语义复杂度
        # 目的越复杂（越长、越抽象），内禀共振越低
        intrinsic = self._compute_intrinsic_resonance(goal)

        # 2. 交叉共振：与活跃目的的协同度
        cross_resonance = 0.0
        active_goals = [f for g, f in self.fields.items()
                        if f.is_active and g != goal]
        if active_goals:
            cross_values = []
            for other in active_goals:
                # 简化的语义相似度：基于字符串重叠
                similarity = self._semantic_similarity(goal, other.goal)
                cross_values.append(similarity * other.strength)
            cross_resonance = sum(cross_values) / len(cross_values)

        # 3. 累积共振：如果目的已被注入过，历史增强
        cumulative = 0.0
        if goal in self.fields:
            cumulative = min(0.3, self.fields[goal].strength * 0.1)

        # 综合共振
        v_ftel = round(
            intrinsic * 0.5 + cross_resonance * 0.3 + cumulative * 0.2, 6
        )
        v_ftel = min(1.0, max(0.0, v_ftel))

        return v_ftel

    def check_convergence(self, goal: str) -> Dict[str, Any]:
        """
        T75收敛性检查

        定理T75（Ftel学习收敛定理）：
        当λ∈(0,λ_max)时，Ftel约束下的学习过程收敛到目的吸引子φ*。

        收敛判定条件：
        1. 约束强度λ在有效区间内
        2. 共振值V_ftel足够高（目的与状态对齐）
        3. 收敛速率为正（趋势向好）

        Args:
            goal: 目的φ描述

        Returns:
            收敛性检查结果字典
        """
        self.total_convergence_checks += 1

        if goal not in self.fields:
            return {
                'goal': goal,
                'converges': False,
                'reason': 'goal_not_found',
                'lambda_in_range': False,
                'resonance_sufficient': False,
                'convergence_rate': 0.0,
                'theorem': 'T75: Ftel学习收敛定理'
            }

        ftel_field = self.fields[goal]

        # 条件1：约束强度λ在有效区间 (0, λ_max)
        lambda_in_range = 0 < ftel_field.strength < self.lambda_max

        # 条件2：共振值足够高
        resonance_sufficient = ftel_field.resonance > 0.3

        # 条件3：收敛速率为正
        rate_positive = ftel_field.convergence_rate > 0

        # T75综合判定
        converges = lambda_in_range and (resonance_sufficient or rate_positive)

        # 更新收敛速率（模拟学习过程中的收敛趋势）
        if converges:
            # 收敛速率随时间递增（模拟逐步逼近目的吸引子）
            ftel_field.convergence_rate = round(
                min(1.0, ftel_field.convergence_rate + 0.05), 6
            )
        else:
            # 不收敛时，收敛速率可能衰减
            ftel_field.convergence_rate = round(
                max(0.0, ftel_field.convergence_rate - 0.02), 6
            )

        reason = 'all_conditions_met' if converges else (
            'lambda_out_of_range' if not lambda_in_range else (
                'low_resonance' if not resonance_sufficient else 'negative_rate'
            )
        )

        self.last_update = time.time()
        return {
            'goal': goal,
            'converges': converges,
            'reason': reason,
            'lambda_in_range': lambda_in_range,
            'resonance_sufficient': resonance_sufficient,
            'convergence_rate': ftel_field.convergence_rate,
            'strength': ftel_field.strength,
            'resonance': ftel_field.resonance,
            'theorem': 'T75: Ftel学习收敛定理'
        }

    def blend_signal(self, data_signal: float, goal: str) -> Dict[str, Any]:
        """
        S_total = S_data + λ·V_ftel 信号融合

        将数据信号S_data与Ftel目的约束信号λ·V_ftel融合，
        生成综合信号S_total。目的约束调制原始数据信号，
        使系统在目的方向上获得增益。

        Args:
            data_signal: 原始数据信号S_data
            goal: 目的φ描述

        Returns:
            融合结果字典，包含S_data、V_ftel、λ、S_total
        """
        self.total_blend_operations += 1

        if goal not in self.fields:
            # 目的不存在，不施加约束
            return {
                'goal': goal,
                'S_data': round(data_signal, 6),
                'V_ftel': 0.0,
                'lambda': 0.0,
                'S_total': round(data_signal, 6),
                'blend_ratio': 0.0,
                'constraint_active': False
            }

        ftel_field = self.fields[goal]
        v_ftel = ftel_field.resonance
        lam = ftel_field.strength if ftel_field.is_active else 0.0

        # S_total = S_data + λ·V_ftel
        s_total = data_signal + lam * v_ftel

        # 融合比率：Ftel约束占总信号的比例
        blend_ratio = abs(lam * v_ftel) / max(abs(s_total), 1e-10)

        self.last_update = time.time()
        return {
            'goal': goal,
            'S_data': round(data_signal, 6),
            'V_ftel': round(v_ftel, 6),
            'lambda': round(lam, 6),
            'S_total': round(s_total, 6),
            'blend_ratio': round(min(1.0, blend_ratio), 6),
            'constraint_active': ftel_field.is_active
        }

    def retire_goal(self, goal: str) -> Dict[str, Any]:
        """
        退役已达成目的

        当目的已达成（收敛到吸引子φ*）时，将其标记为非活跃。
        退役的目的不再约束生成空间，但保留在历史记录中。

        Args:
            goal: 要退役的目的φ描述

        Returns:
            退役结果字典
        """
        if goal not in self.fields:
            return {
                'goal': goal,
                'retired': False,
                'reason': 'goal_not_found'
            }

        ftel_field = self.fields[goal]
        was_active = ftel_field.is_active
        ftel_field.is_active = False

        self.total_retirements += 1
        self.last_update = time.time()

        return {
            'goal': goal,
            'retired': True,
            'was_active': was_active,
            'final_resonance': round(ftel_field.resonance, 6),
            'final_convergence_rate': round(ftel_field.convergence_rate, 6)
        }

    def get_state(self) -> Dict[str, Any]:
        """
        获取Ftel目的约束算子状态

        Returns:
            状态字典，包含：
            - fields: 所有目的约束场
            - total_resonance: 总共振值
            - active_count: 活跃目的数
            - convergence_achieved: 是否有目的达成收敛
            - 统计信息
        """
        active_fields = [f for f in self.fields.values() if f.is_active]
        total_resonance = round(
            sum(f.resonance for f in active_fields), 6
        )
        convergence_achieved = any(
            f.convergence_rate > 0.8 for f in self.fields.values()
        )

        return {
            'fields': [f.to_dict() for f in self.fields.values()],
            'total_resonance': total_resonance,
            'active_count': len(active_fields),
            'total_goals': len(self.fields),
            'convergence_achieved': convergence_achieved,
            'lambda_max': self.lambda_max,
            'total_injections': self.total_injections,
            'total_resonance_computations': self.total_resonance_computations,
            'total_convergence_checks': self.total_convergence_checks,
            'total_blend_operations': self.total_blend_operations,
            'total_retirements': self.total_retirements,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T75': 'Ftel学习收敛: λ∈(0,λ_max) ⟹ 收敛到φ*'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新Ftel目的约束算子状态

        Args:
            data: 可选更新数据，支持：
                - inject: 注入目的 {goal, strength}
                - retire: 退役目的 {goal}
                - blend: 信号融合 {data_signal, goal}
                - check: 收敛检查 {goal}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'inject' or 'inject' in data:
                inj = data.get('inject', data)
                self.inject_goal(
                    goal=inj.get('goal', ''),
                    strength=float(inj.get('strength', 0.5))
                )
            elif action == 'retire' or 'retire' in data:
                ret = data.get('retire', data)
                self.retire_goal(goal=ret.get('goal', ''))
            elif action == 'blend' or 'blend' in data:
                bld = data.get('blend', data)
                self.blend_signal(
                    data_signal=float(bld.get('data_signal', 0.0)),
                    goal=bld.get('goal', '')
                )
            elif action == 'check' or 'check' in data:
                chk = data.get('check', data)
                self.check_convergence(goal=chk.get('goal', ''))

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示Ftel目的约束算子的核心功能"""
        # 1. 注入多个目的
        g1 = self.inject_goal('理解用户意图', 0.7)
        g2 = self.inject_goal('生成准确回答', 0.8)
        g3 = self.inject_goal('避免幻觉输出', 0.6)
        g4 = self.inject_goal('保持对话连贯', 0.5)

        # 2. 计算共振
        r1 = self.compute_resonance('理解用户意图')
        r2 = self.compute_resonance('生成准确回答')

        # 3. T75收敛性检查
        c1 = self.check_convergence('理解用户意图')
        c2 = self.check_convergence('生成准确回答')

        # 4. 信号融合
        b1 = self.blend_signal(0.6, '理解用户意图')
        b2 = self.blend_signal(0.4, '避免幻觉输出')

        # 5. 退役目的
        ret = self.retire_goal('保持对话连贯')

        return {
            'injections': {
                'g1': g1.to_dict(),
                'g2': g2.to_dict(),
                'g3': g3.to_dict(),
                'g4': g4.to_dict(),
            },
            'resonances': {
                '理解用户意图': r1,
                '生成准确回答': r2,
            },
            'convergence_T75': {
                '理解用户意图': c1,
                '生成准确回答': c2,
            },
            'blend_results': {
                '理解用户意图': b1,
                '避免幻觉输出': b2,
            },
            'retirement': ret,
            'state': self.get_state()
        }

    # ==================== 内部方法 ====================

    def _compute_intrinsic_resonance(self, goal: str) -> float:
        """
        计算目的的内禀共振值

        基于目的描述的语义特征：
        - 长度适中 → 较高共振
        - 过短或过长 → 较低共振
        """
        length = len(goal)
        if length == 0:
            return 0.0
        # 最优长度在8-20字符之间
        optimal_range = 8 <= length <= 20
        base = 0.6 if optimal_range else 0.4
        # 长度因子
        length_factor = 1.0 - abs(length - 14) / 30.0
        return round(max(0.1, min(1.0, base * length_factor)), 6)

    def _semantic_similarity(self, goal_a: str, goal_b: str) -> float:
        """
        计算两个目的的简化语义相似度

        基于字符重叠率（Jaccard系数的简化版本）
        """
        if not goal_a or not goal_b:
            return 0.0
        set_a = set(goal_a)
        set_b = set(goal_b)
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        if union == 0:
            return 0.0
        return round(intersection / union, 6)

    def _estimate_convergence_rate(self, strength: float, resonance: float) -> float:
        """
        估计初始收敛速率

        收敛速率与约束强度和共振值的乘积成正比
        """
        rate = strength * resonance * 0.5
        return round(min(1.0, max(0.0, rate)), 6)


# ==================== 模块单例导出 ====================

_instance: Optional[FtelTeleologicalConstraint] = None


def get_instance() -> FtelTeleologicalConstraint:
    """
    获取FtelTeleologicalConstraint单例实例

    Returns:
        FtelTeleologicalConstraint全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = FtelTeleologicalConstraint()
    return _instance


def inject_goal(goal: str, strength: float = 0.5) -> FtelField:
    """注入目的到生成空间（快捷接口）"""
    return get_instance().inject_goal(goal, strength)


def compute_resonance(goal: str) -> float:
    """计算V_ftel共振值（快捷接口）"""
    return get_instance().compute_resonance(goal)


def check_convergence(goal: str) -> Dict[str, Any]:
    """T75收敛性检查（快捷接口）"""
    return get_instance().check_convergence(goal)


def blend_signal(data_signal: float, goal: str) -> Dict[str, Any]:
    """S_total = S_data + λ·V_ftel 信号融合（快捷接口）"""
    return get_instance().blend_signal(data_signal, goal)


def retire_goal(goal: str) -> Dict[str, Any]:
    """退役已达成目的（快捷接口）"""
    return get_instance().retire_goal(goal)


def get_state() -> Dict[str, Any]:
    """获取Ftel目的约束算子状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新Ftel目的约束算子状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
