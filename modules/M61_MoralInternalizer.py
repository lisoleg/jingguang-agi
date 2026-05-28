# -*- coding: utf-8 -*-
"""
M61: 道德内化器 (Moral Internalizer)
基于《论〈道德经〉的复合体重构》论文
实现"神灵"(他律)+"慎独"(自律)双锁机制
定理: T22道德双锁收敛定理
"""

import random
from typing import Dict, Any, List

class MoralInternalizer:
    """道德内化器 - 实现道德双锁机制"""

    def __init__(self):
        # 双锁状态
        self.negation_lock = {  # 否定锁（神灵/他律）
            'status': 'active',
            'strength': 0.75,      # 锁定强度
            'activation_rate': 0.82,  # 激活率
            'cost': 0.25           # 监管成本
        }

        self.affirmation_lock = {  # 肯定锁（慎独/自律）
            'status': 'active',
            'strength': 0.68,      # 锁定强度
            'internalization': 0.72,  # 内化程度
            'cost': 0.30           # 监管成本
        }

        # 道德演化状态
        self.moral_action = 0.35    # 道德作用量 (目标: 递减→0)
        self.moral_integrity = 0.78  # 道德完整性

        # 双锁统合状态
        self.lock_integration = 0.65
        self.total_regulation_cost = self.negation_lock['cost'] + self.affirmation_lock['cost']

        # 历史
        self.moral_history = []

    def update(self, moral_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        更新道德内化状态
        T22道德双锁收敛定理:
        L_lock ∩ P_lock ≠ ∅ → 道德监管成本 C → 0
        """
        if moral_data:
            # 基于道德数据更新
            action_quality = moral_data.get('action_quality', 0.8)

            # 更新否定锁
            self.negation_lock['strength'] = (
                self.negation_lock['strength'] * 0.95 +
                action_quality * 0.1
            )

            # 更新肯定锁
            self.affirmation_lock['internalization'] = (
                self.affirmation_lock['internalization'] * 0.95 +
                action_quality * 0.1
            )

            # 道德完整性提升
            if action_quality > 0.8:
                self.moral_integrity = min(1.0, self.moral_integrity * 1.02 + 0.01)

            # 道德作用量递减
            self.moral_action = max(0, self.moral_action * 0.97 - 0.01)
        else:
            # 自然演化
            self.moral_action *= 0.99
            self.moral_integrity = min(1.0, self.moral_integrity * 1.005 + 0.001)

        # 计算双锁统合度
        self._calculate_lock_integration()

        # 更新总监管成本
        self.total_regulation_cost = self._calculate_regulation_cost()

        # 记录历史
        self.moral_history.append({
            'action': self.moral_action,
            'integrity': self.moral_integrity,
            'integration': self.lock_integration,
            'cost': self.total_regulation_cost
        })

        if len(self.moral_history) > 50:
            self.moral_history.pop(0)

        return self.get_state()

    def _calculate_lock_integration(self):
        """
        计算双锁统合度
        L_lock ∩ P_lock ≠ ∅ 时统合度增加
        """
        # 否定锁与肯定锁的交集程度
        negation_active = self.negation_lock['activation_rate'] if self.negation_lock['status'] == 'active' else 0
        affirmation_active = self.affirmation_lock['internalization'] if self.affirmation_lock['status'] == 'active' else 0

        # 统合度 = 交集/并集
        intersection = min(negation_active, affirmation_active)
        union = max(negation_active, affirmation_active)

        self.lock_integration = intersection / union if union > 0 else 0

    def _calculate_regulation_cost(self) -> float:
        """
        计算道德监管成本
        T22: 双锁统合 → 成本 C → 0
        """
        base_cost = 0.1

        # 否定锁成本（随统合度降低）
        negation_cost = self.negation_lock['cost'] * (1 - self.lock_integration)

        # 肯定锁成本（随内化程度降低）
        affirmation_cost = self.affirmation_lock['cost'] * (1 - self.affirmation_lock['internalization'])

        return base_cost + negation_cost + affirmation_cost

    def check_moral_violation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查道德违规
        返回违规检测结果
        """
        action_type = action.get('type', 'normal')
        action_value = action.get('value', 0.5)

        # 否定锁检查（他律）
        negation_violated = action_value < 0.3

        # 肯定锁检查（自律）
        affirmation_violated = action_type == 'selfish' or action_value < 0.4

        violated = negation_violated or affirmation_violated

        return {
            'violated': violated,
            'negation_lock': {
                'triggered': negation_violated,
                'type': '神灵(他律)'
            },
            'affirmation_lock': {
                'triggered': affirmation_violated,
                'type': '慎独(自律)'
            },
            'action_blocked': violated
        }

    def get_state(self) -> Dict[str, Any]:
        """获取当前道德内化状态"""
        # 双锁状态文本
        negation_status = '激活' if self.negation_lock['status'] == 'active' else '休眠'
        affirmation_status = '激活' if self.affirmation_lock['status'] == 'active' else '休眠'

        # 成本状态
        if self.total_regulation_cost < 0.15:
            cost_status = '极低 ✓'
        elif self.total_regulation_cost < 0.3:
            cost_status = '较低'
        else:
            cost_status = '较高'

        # 道德演化趋势
        if len(self.moral_history) >= 5:
            action_trend = '下降' if self.moral_history[-1]['action'] < self.moral_history[-5]['action'] else '上升'
        else:
            action_trend = '平稳'

        return {
            'negation_lock': {
                'status': negation_status,
                'strength': round(self.negation_lock['strength'], 4),
                'activation_rate': round(self.negation_lock['activation_rate'], 4),
                'type': '神灵(他律)',
                'blocked': self.negation_lock['strength'] < 0.3
            },
            'affirmation_lock': {
                'status': affirmation_status,
                'strength': round(self.affirmation_lock['strength'], 4),
                'internalization': round(self.affirmation_lock['internalization'], 4),
                'type': '慎独(自律)',
                'blocked': self.affirmation_lock['internalization'] < 0.3
            },
            'lock_integration': round(self.lock_integration, 4),
            'integration_status': '统合' if self.lock_integration > 0.7 else '独立',
            'total_regulation_cost': round(self.total_regulation_cost, 4),
            'cost_status': cost_status,
            'moral_action': round(self.moral_action, 4),
            'moral_integrity': round(self.moral_integrity, 4),
            'action_trend': action_trend,
            # T22定理可视化
            'theorem_viz': {
                'title': 'T22 道德双锁收敛定理',
                'condition': 'L_lock ∩ P_lock ≠ ∅',
                'convergence': {
                    'regulation_cost': f'C → {round(self.total_regulation_cost, 3)}',
                    'moral_action': f'S_moral → {round(self.moral_action, 3)}',
                },
                'corollary': '神灵+慎独统合 → 监管成本趋零'
            }
        }

    def simulate(self) -> Dict[str, Any]:
        """模拟道德演化 (用于测试)"""
        # 否定锁自然衰减
        self.negation_lock['strength'] = min(1.0, self.negation_lock['strength'] + random.uniform(-0.02, 0.03))

        # 肯定锁内化提升
        self.affirmation_lock['internalization'] = min(1.0, self.affirmation_lock['internalization'] + random.uniform(-0.01, 0.02))

        # 道德作用量递减
        self.moral_action = max(0, self.moral_action - random.uniform(0.01, 0.03))

        # 完整性提升
        self.moral_integrity = min(1.0, self.moral_integrity + random.uniform(-0.01, 0.02))

        self._calculate_lock_integration()
        self.total_regulation_cost = self._calculate_regulation_cost()

        return self.get_state()


# 全局实例
_moral_internalizer = None

def get_instance():
    global _moral_internalizer
    if _moral_internalizer is None:
        _moral_internalizer = MoralInternalizer()
    return _moral_internalizer

def update(moral_data: Dict[str, Any] = None) -> Dict[str, Any]:
    return get_instance().update(moral_data)

def get_state() -> Dict[str, Any]:
    return get_instance().get_state()

def check_moral_violation(action: Dict[str, Any]) -> Dict[str, Any]:
    return get_instance().check_moral_violation(action)

def simulate() -> Dict[str, Any]:
    return get_instance().simulate()
