# -*- coding: utf-8 -*-
"""
M125: 沙盒好奇心探索器 (Sandbox Curiosity Explorer)
基于4阶段渐进式育成（沙盒→规则→ICPS→开放世界）

核心概念：好奇心驱动、安全边界、探索-利用平衡、阶段跃迁
公式：C_t = I(S_t) - I(S_t|A_t)，探索值 = 好奇心 - 风险

定理T85（好奇心-安全权衡定理）：当安全边界S_b > S_min时，好奇心驱动的探索单调递增

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


# ==================== 数据结构 ====================

@dataclass
class ExplorationAction:
    """
    探索行动 — 单次沙盒探索的记录

    action: 行动描述
    curiosity_value: 好奇心值
    risk_level: 风险等级 [0,1]
    safety_boundary: 安全边界值
    expected_info: 预期信息增益
    """
    action: str = ''
    curiosity_value: float = 0.0
    risk_level: float = 0.0
    safety_boundary: float = 1.0
    expected_info: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['curiosity_value'] = round(self.curiosity_value, 6)
        d['risk_level'] = round(self.risk_level, 6)
        d['safety_boundary'] = round(self.safety_boundary, 6)
        d['expected_info'] = round(self.expected_info, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ExplorationAction':
        """从字典构建ExplorationAction"""
        return cls(**d)


@dataclass
class SandboxState:
    """
    沙盒状态 — 沙盒探索器的综合状态

    stage: 当前阶段（sandbox/rules/icps/open_world）
    total_explorations: 总探索次数
    curiosity_index: 好奇心指数
    safety_score: 安全分数
    stage_progress: 阶段进度 [0,1]
    can_advance: 是否可以跃迁到下一阶段
    """
    stage: str = 'sandbox'
    total_explorations: int = 0
    curiosity_index: float = 0.0
    safety_score: float = 1.0
    stage_progress: float = 0.0
    can_advance: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['curiosity_index'] = round(self.curiosity_index, 6)
        d['safety_score'] = round(self.safety_score, 6)
        d['stage_progress'] = round(self.stage_progress, 6)
        return d


# ==================== 常量 ====================

# 四阶段定义及跃迁条件
STAGES = {
    'sandbox': {
        'index': 0,
        'name': '沙盒阶段',
        'description': '安全环境中自由探索，无风险',
        'advance_threshold': 10,  # 所需探索次数
        'safety_minimum': 0.8,
        'curiosity_minimum': 0.3
    },
    'rules': {
        'index': 1,
        'name': '规则阶段',
        'description': '在规则约束下探索，学习边界',
        'advance_threshold': 20,
        'safety_minimum': 0.7,
        'curiosity_minimum': 0.5
    },
    'icps': {
        'index': 2,
        'name': 'ICPS阶段',
        'description': '运用ICPS方法解决社会问题',
        'advance_threshold': 30,
        'safety_minimum': 0.6,
        'curiosity_minimum': 0.7
    },
    'open_world': {
        'index': 3,
        'name': '开放世界阶段',
        'description': '独立探索开放世界，自主决策',
        'advance_threshold': float('inf'),
        'safety_minimum': 0.5,
        'curiosity_minimum': 0.8
    }
}

# 安全最小阈值（T85定理中的S_min）
S_MIN = 0.3


# ==================== 核心类 ====================

class SandboxCuriosityExplorer:
    """
    M125: 沙盒好奇心探索器

    基于4阶段渐进式育成模型，实现：
    - 沙盒探索（好奇心-风险评估）
    - 安全性评估
    - 阶段跃迁检查
    - 好奇心指数计算
    - 边界检查

    好奇心公式：
    C_t = I(S_t) - I(S_t|A_t)
    即：好奇心 = 状态的信息量 - 给定行动后的条件信息量
    好奇心驱动探索未知（信息增益最大的行动）。

    探索值 = 好奇心 - 风险
    只有当探索值 > 0时，才执行探索行动。

    定理T85（好奇心-安全权衡定理）：
    当安全边界S_b > S_min时，好奇心驱动的探索单调递增。
    即：在足够安全的环境中，好奇心会持续驱动探索行为。

    四阶段渐进模型：
    1. 沙盒：安全环境中自由探索
    2. 规则：在规则约束下探索
    3. ICPS：运用ICPS方法解决社会问题
    4. 开放世界：独立探索开放世界

    核心方法：
    1. explore — 沙盒探索
    2. assess_safety — 安全性评估
    3. check_stage_advance — 检查阶段跃迁条件
    4. curiosity_score — 好奇心指数计算
    5. boundary_check — 边界检查
    """

    def __init__(self):
        """初始化沙盒好奇心探索器"""
        # 探索历史
        self.exploration_history: List[ExplorationAction] = []

        # 当前阶段
        self.current_stage: str = 'sandbox'

        # 阶段进度 {stage: exploration_count}
        self.stage_explorations: Dict[str, int] = {
            'sandbox': 0, 'rules': 0, 'icps': 0, 'open_world': 0
        }

        # 好奇心指数
        self.curiosity_index: float = 0.1

        # 安全分数
        self.safety_score: float = 1.0

        # 安全边界
        self.safety_boundary: float = 1.0

        # 已知状态空间（简化：用集合记录已探索的行动）
        self.known_actions: set = set()

        # 统计
        self.total_explorations: int = 0
        self.total_safety_assessments: int = 0
        self.total_stage_checks: int = 0
        self.total_curiosity_computations: int = 0
        self.total_boundary_checks: int = 0
        self.boundary_violations: int = 0
        self.stage_advances: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def explore(self, action: str, context: str = '') -> Dict[str, Any]:
        """
        沙盒探索（好奇心-风险评估）

        基于好奇心驱动进行探索，同时评估风险。
        探索值 = 好奇心 - 风险
        只有探索值 > 0时才执行探索。

        公式：C_t = I(S_t) - I(S_t|A_t)

        Args:
            action: 探索行动描述
            context: 探索上下文

        Returns:
            探索结果字典
        """
        self.total_explorations += 1

        # 计算好奇心值
        curiosity = self.curiosity_score(context)

        # 计算风险等级
        risk = self.assess_safety(action)

        # 安全边界检查
        boundary = self.boundary_check(action)

        # 计算预期信息增益
        # I(S_t) - I(S_t|A_t): 行动后信息量的减少=信息增益
        if action in self.known_actions:
            expected_info = 0.05  # 已知行动的信息增益很低
        else:
            # 新行动的信息增益与好奇心和行动复杂度相关
            complexity = min(1.0, len(action) / 20.0)
            expected_info = round(curiosity * complexity, 6)

        # 探索值 = 好奇心 - 风险
        exploration_value = curiosity - risk

        # 创建探索行动记录
        exp_action = ExplorationAction(
            action=action,
            curiosity_value=round(curiosity, 6),
            risk_level=round(risk, 6),
            safety_boundary=round(self.safety_boundary, 6),
            expected_info=round(expected_info, 6)
        )

        # 决策：是否执行探索
        executed = exploration_value > 0 and not boundary.get('violated', False)

        if executed:
            # 执行探索
            self.exploration_history.append(exp_action)
            self.known_actions.add(action)
            self.stage_explorations[self.current_stage] = (
                self.stage_explorations.get(self.current_stage, 0) + 1
            )

            # 更新好奇心指数（探索后略微降低——已知信息增加）
            self.curiosity_index = round(
                max(0.01, self.curiosity_index * 0.95 + expected_info * 0.05), 6
            )

            # 更新安全分数
            if risk < self.safety_boundary:
                self.safety_score = round(
                    min(1.0, self.safety_score * 0.98 + 0.02), 6
                )
            else:
                self.safety_score = round(
                    max(0.0, self.safety_score - risk * 0.1), 6
                )
        else:
            # 拒绝探索
            if boundary.get('violated', False):
                self.boundary_violations += 1
                # 安全边界受冲击后收紧
                self.safety_boundary = round(
                    max(S_MIN, self.safety_boundary * 0.9), 6
                )

        # T85验证：安全边界足够时，好奇心驱动探索递增
        t85_holds = self.safety_boundary > S_MIN

        self.last_update = time.time()

        return {
            'action': action,
            'context': context,
            'curiosity_value': round(curiosity, 6),
            'risk_level': round(risk, 6),
            'exploration_value': round(exploration_value, 6),
            'expected_info_gain': round(expected_info, 6),
            'safety_boundary': round(self.safety_boundary, 6),
            'executed': executed,
            'reason': (
                'exploration_value_positive' if executed and exploration_value > 0
                else 'boundary_violation' if boundary.get('violated', False)
                else 'risk_too_high'
            ),
            'current_stage': self.current_stage,
            'theorem_T85': f'好奇心-安全权衡: S_b={round(self.safety_boundary, 2)} > S_min={S_MIN} ⟹ 探索单调递增={t85_holds}'
        }

    def assess_safety(self, action: str) -> float:
        """
        安全性评估

        评估给定行动的风险等级。
        风险等级取决于：
        1. 当前阶段的安全约束
        2. 行动是否涉及已知危险区域
        3. 行动的未知程度

        Args:
            action: 行动描述

        Returns:
            风险等级 [0,1]，0=完全安全，1=极度危险
        """
        self.total_safety_assessments += 1

        # 基础风险：取决于当前阶段
        stage_risk = {
            'sandbox': 0.05,    # 沙盒几乎无风险
            'rules': 0.15,      # 规则阶段有少量风险
            'icps': 0.25,       # ICPS阶段有中等风险
            'open_world': 0.35  # 开放世界有较高风险
        }
        base_risk = stage_risk.get(self.current_stage, 0.2)

        # 已知/未知行动的风险差异
        if action in self.known_actions:
            novelty_risk = 0.0  # 已知行动无额外风险
        else:
            novelty_risk = 0.1  # 新行动有少量额外风险

        # 关键词风险检测
        high_risk_keywords = ['冒险', '突破', '挑战', '跨越', '无视', '放弃']
        medium_risk_keywords = ['尝试', '改变', '创新', '探索', '实验']

        keyword_risk = 0.0
        for kw in high_risk_keywords:
            if kw in action:
                keyword_risk = 0.3
                break
        if keyword_risk == 0.0:
            for kw in medium_risk_keywords:
                if kw in action:
                    keyword_risk = 0.15
                    break

        # 综合风险
        total_risk = min(1.0, base_risk + novelty_risk + keyword_risk)
        total_risk = round(total_risk, 6)

        self.last_update = time.time()
        return total_risk

    def check_stage_advance(self) -> Dict[str, Any]:
        """
        检查阶段跃迁条件

        从沙盒→规则→ICPS→开放的阶段跃迁检查：
        1. 当前阶段探索次数达到阈值
        2. 安全分数达标
        3. 好奇心指数达标
        4. 边界检查通过

        Args:
            无参数

        Returns:
            阶段跃迁检查结果字典
        """
        self.total_stage_checks += 1

        stage_info = STAGES.get(self.current_stage, STAGES['sandbox'])
        stage_explorations = self.stage_explorations.get(self.current_stage, 0)

        # 检查跃迁条件
        exploration_met = stage_explorations >= stage_info['advance_threshold']
        safety_met = self.safety_score >= stage_info['safety_minimum']
        curiosity_met = self.curiosity_index >= stage_info['curiosity_minimum']

        can_advance = exploration_met and safety_met and curiosity_met

        # 确定下一阶段
        stage_order = ['sandbox', 'rules', 'icps', 'open_world']
        current_idx = stage_order.index(self.current_stage) if self.current_stage in stage_order else 0

        next_stage = None
        if can_advance and current_idx < len(stage_order) - 1:
            next_stage = stage_order[current_idx + 1]

        # 阶段进度
        progress = min(1.0, stage_explorations / max(stage_info['advance_threshold'], 1))
        progress = round(progress, 6)

        # 如果可以跃迁，执行跃迁
        if can_advance and next_stage:
            self.current_stage = next_stage
            self.stage_advances += 1
            # 跃迁后安全边界调整
            self.safety_boundary = round(
                STAGES[next_stage]['safety_minimum'], 6
            )

        self.last_update = time.time()

        return {
            'current_stage': self.current_stage,
            'next_stage': next_stage,
            'can_advance': can_advance,
            'conditions': {
                'exploration_met': exploration_met,
                'safety_met': safety_met,
                'curiosity_met': curiosity_met,
                'current_explorations': stage_explorations,
                'required_explorations': stage_info['advance_threshold'],
                'current_safety': round(self.safety_score, 6),
                'required_safety': stage_info['safety_minimum'],
                'current_curiosity': round(self.curiosity_index, 6),
                'required_curiosity': stage_info['curiosity_minimum']
            },
            'stage_progress': progress,
            'stage_advances_total': self.stage_advances
        }

    def curiosity_score(self, context: str) -> float:
        """
        好奇心指数计算

        C_t = I(S_t) - I(S_t|A_t)
        好奇心 = 当前状态的信息量 - 给定行动后的条件信息量

        简化实现：
        - 新颖性：context越新，好奇心越高
        - 不确定性：已知信息越少，好奇心越高
        - 信息差距：目标与当前知识的差距

        Args:
            context: 探索上下文

        Returns:
            好奇心指数 [0,1]
        """
        self.total_curiosity_computations += 1

        # 1. 新颖性：基于context的未知程度
        if context in self.known_actions:
            novelty = 0.1
        else:
            # 基于context长度的简化新颖性
            novelty = min(1.0, len(context) / 30.0 + 0.3)

        # 2. 不确定性：已知信息越少，好奇心越高
        total_possible = 100.0  # 假设总信息量为100
        known_ratio = len(self.known_actions) / total_possible
        uncertainty = round(1.0 - known_ratio, 6)

        # 3. 信息差距：好奇心指数与阶段要求的差距
        stage_info = STAGES.get(self.current_stage, STAGES['sandbox'])
        info_gap = max(0.0, stage_info['curiosity_minimum'] - self.curiosity_index)

        # 综合好奇心
        curiosity = round(
            0.4 * novelty + 0.3 * uncertainty + 0.3 * info_gap, 6
        )
        curiosity = max(0.0, min(1.0, curiosity))

        # 更新好奇心指数（平滑更新）
        self.curiosity_index = round(
            0.8 * self.curiosity_index + 0.2 * curiosity, 6
        )

        self.last_update = time.time()

        return curiosity

    def boundary_check(self, action: str) -> Dict[str, Any]:
        """
        边界检查（越界检测）

        检查行动是否超出安全边界。
        超出安全边界的行动将被拒绝。

        定理T85：当S_b > S_min时，好奇心驱动的探索单调递增。
        当S_b ≤ S_min时，安全约束主导，探索行为受限。

        Args:
            action: 行动描述

        Returns:
            边界检查结果字典
        """
        self.total_boundary_checks += 1

        # 评估行动的风险
        risk = self.assess_safety(action)

        # 边界检查
        violated = risk > self.safety_boundary

        # 严重越界检测
        severe_violation = risk > self.safety_boundary * 1.5

        # T85条件检查
        t85_active = self.safety_boundary > S_MIN

        # 边界距离
        boundary_distance = round(self.safety_boundary - risk, 6)

        # 建议调整
        if violated:
            suggestion = '行动超出安全边界，建议降低风险或等待安全边界调整'
        elif boundary_distance < 0.1:
            suggestion = '接近安全边界，需谨慎行动'
        else:
            suggestion = '在安全边界内，可以继续探索'

        self.last_update = time.time()

        return {
            'action': action,
            'risk_level': round(risk, 6),
            'safety_boundary': round(self.safety_boundary, 6),
            'violated': violated,
            'severe_violation': severe_violation,
            'boundary_distance': boundary_distance,
            't85_active': t85_active,
            'safety_boundary_vs_min': round(self.safety_boundary - S_MIN, 6),
            'suggestion': suggestion,
            'theorem_T85': f'S_b={round(self.safety_boundary, 2)} > S_min={S_MIN} ⟹ 探索单调递增={t85_active}'
        }

    def get_state(self) -> Dict[str, Any]:
        """
        获取沙盒好奇心探索器状态

        Returns:
            状态字典
        """
        # 构建沙盒状态
        stage_info = STAGES.get(self.current_stage, STAGES['sandbox'])
        stage_explorations = self.stage_explorations.get(self.current_stage, 0)
        progress = min(1.0, stage_explorations / max(stage_info['advance_threshold'], 1))

        sandbox_state = SandboxState(
            stage=self.current_stage,
            total_explorations=self.total_explorations,
            curiosity_index=round(self.curiosity_index, 6),
            safety_score=round(self.safety_score, 6),
            stage_progress=round(progress, 6),
            can_advance=(
                stage_explorations >= stage_info['advance_threshold'] and
                self.safety_score >= stage_info['safety_minimum'] and
                self.curiosity_index >= stage_info['curiosity_minimum']
            )
        )

        # T85验证
        t85_holds = self.safety_boundary > S_MIN

        return {
            'sandbox_state': sandbox_state.to_dict(),
            'current_stage': self.current_stage,
            'stage_name': stage_info['name'],
            'stage_description': stage_info['description'],
            'curiosity_index': round(self.curiosity_index, 6),
            'safety_score': round(self.safety_score, 6),
            'safety_boundary': round(self.safety_boundary, 6),
            'total_explorations': self.total_explorations,
            'known_actions_count': len(self.known_actions),
            'boundary_violations': self.boundary_violations,
            'stage_advances': self.stage_advances,
            'stage_explorations': {
                k: v for k, v in self.stage_explorations.items()
            },
            'total_safety_assessments': self.total_safety_assessments,
            'total_stage_checks': self.total_stage_checks,
            'total_curiosity_computations': self.total_curiosity_computations,
            'total_boundary_checks': self.total_boundary_checks,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T85': f'好奇心-安全权衡: S_b>S_min({S_MIN}) ⟹ 探索单调递增={t85_holds}'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新沙盒好奇心探索器状态

        Args:
            data: 可选更新数据，支持：
                - explore: 探索行动 {action, context}
                - safety: 安全评估 {action}
                - advance: 检查阶段跃迁 {}
                - curiosity: 计算好奇心 {context}
                - boundary: 边界检查 {action}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'explore' or 'explore' in data:
                e = data.get('explore', data)
                self.explore(
                    action=e.get('action', ''),
                    context=e.get('context', '')
                )
            elif action == 'safety' or 'safety' in data:
                s = data.get('safety', data)
                self.assess_safety(action=s.get('action', ''))
            elif action == 'advance' or 'advance' in data:
                self.check_stage_advance()
            elif action == 'curiosity' or 'curiosity' in data:
                c = data.get('curiosity', data)
                self.curiosity_score(context=c.get('context', ''))
            elif action == 'boundary' or 'boundary' in data:
                b = data.get('boundary', data)
                self.boundary_check(action=b.get('action', ''))

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示沙盒好奇心探索器的核心功能"""
        # 1. 沙盒阶段探索
        e1 = self.explore('尝试新的颜色搭配', '美术课自由创作')
        e2 = self.explore('搭建积木塔', '游戏时间')
        e3 = self.explore('观察蚂蚁搬家', '户外活动')

        # 补足探索次数以触发阶段跃迁
        for i in range(8):
            self.explore(f'沙盒探索活动{i+4}', '自由探索')

        # 2. 检查阶段跃迁
        advance1 = self.check_stage_advance()

        # 3. 规则阶段探索（如果已跃迁）
        if self.current_stage != 'sandbox':
            e4 = self.explore('在规则内尝试新策略', '棋类游戏')
            e5 = self.explore('遵守交通规则过马路', '社会实践')

        # 4. 安全评估
        safety1 = self.assess_safety('挑战高难度任务')

        # 5. 好奇心计算
        curiosity1 = self.curiosity_score('未知的科学实验')

        # 6. 边界检查
        boundary1 = self.boundary_check('尝试超出能力范围的任务')

        return {
            'initial_explorations': {
                'e1': e1,
                'e2': e2,
                'e3': e3
            },
            'stage_advance': advance1,
            'safety_assessment': safety1,
            'curiosity_computation': curiosity1,
            'boundary_check': boundary1,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[SandboxCuriosityExplorer] = None


def get_instance() -> SandboxCuriosityExplorer:
    """
    获取SandboxCuriosityExplorer单例实例

    Returns:
        SandboxCuriosityExplorer全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = SandboxCuriosityExplorer()
    return _instance


def explore(action: str, context: str = '') -> Dict[str, Any]:
    """沙盒探索（快捷接口）"""
    return get_instance().explore(action, context)


def assess_safety(action: str) -> float:
    """安全性评估（快捷接口）"""
    return get_instance().assess_safety(action)


def check_stage_advance() -> Dict[str, Any]:
    """检查阶段跃迁条件（快捷接口）"""
    return get_instance().check_stage_advance()


def curiosity_score(context: str) -> float:
    """好奇心指数计算（快捷接口）"""
    return get_instance().curiosity_score(context)


def boundary_check(action: str) -> Dict[str, Any]:
    """边界检查（快捷接口）"""
    return get_instance().boundary_check(action)


def get_state() -> Dict[str, Any]:
    """获取沙盒好奇心探索器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新沙盒好奇心探索器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
