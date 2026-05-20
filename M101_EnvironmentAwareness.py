# -*- coding: utf-8 -*-
"""
M101: 环境感知 (Environment Awareness)
基于T48环境智能耦合定理："智能表现不是Agent的内在属性，而是Agent-Environment耦合系统的涌现属性"

功能：
- 感知当前环境上下文
- 计算Agent-Environment耦合分数
- 根据环境变化自适应调整策略
- 获取环境画像
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class EnvironmentContext:
    """环境上下文"""
    platform: str = 'web'
    user_state: str = 'active'  # 'active' | 'idle' | 'stressed' | 'focused'
    task_complexity: float = 0.5
    available_tools: List[str] = field(default_factory=list)
    noise_level: float = 0.2
    time_pressure: float = 0.0


@dataclass
class CouplingScore:
    """耦合分数"""
    agent_capability: float
    env_affordance: float  # 环境供给度
    coupling: float  # 耦合度 [0,1]
    emergent_intelligence: float  # 涌现智能


class EnvironmentAwareness:
    """
    M101: 环境感知模块

    T48 环境智能耦合定理:
    I = f(Agent, Environment, Coupling)
    智能 ≠ Agent内在属性
    智能 = Agent-Env耦合的涌现

    核心机制：
    1. 环境感知 — 持续监测环境状态变化
    2. 耦合评估 — 计算Agent-Environment耦合质量
    3. 自适应 — 根据环境变化调整策略
    4. 涌现追踪 — 量化耦合系统中的涌现智能
    """

    def __init__(self):
        self.coupling_score: float = 0.5
        self.env_complexity: float = 0.5
        self.adaptation_count: int = 0
        self.last_env_type: str = 'web'
        self.emergent_iq: float = 0.5

        # 内部状态
        self._current_env: Optional[EnvironmentContext] = None
        self._env_history: List[EnvironmentContext] = []
        self._adaptation_strategies: Dict[str, Dict] = {
            'high_noise': {'strategy': 'increase_redundancy', 'confidence_dampening': 0.7},
            'low_resources': {'strategy': 'simplify_output', 'detail_reduction': 0.5},
            'high_pressure': {'strategy': 'prioritize_critical', 'focus_ratio': 0.8},
            'idle_user': {'strategy': 'wait_for_engagement', 'proactivity': 0.2},
        }

    def sense_environment(self, context_data: Dict) -> Dict[str, Any]:
        """
        感知当前环境上下文

        参数:
            context_data: {
                'platform': str,
                'user_state': str,
                'task_complexity': float,
                'available_tools': list,
                'noise_level': float,
                'time_pressure': float
            }

        返回:
            dict: 环境感知结果
        """
        env = EnvironmentContext(
            platform=context_data.get('platform', 'web'),
            user_state=context_data.get('user_state', 'active'),
            task_complexity=context_data.get('task_complexity', 0.5),
            available_tools=context_data.get('available_tools', []),
            noise_level=context_data.get('noise_level', 0.2),
            time_pressure=context_data.get('time_pressure', 0.0)
        )

        self._current_env = env
        self._env_history.append(env)
        self.last_env_type = env.platform

        # 更新环境复杂度
        self.env_complexity = self._compute_env_complexity(env)

        # 计算耦合分数
        coupling = self.compute_coupling_score(0.7, self._env_affordance(env))

        return {
            'environment': {
                'platform': env.platform,
                'user_state': env.user_state,
                'complexity': round(self.env_complexity, 4),
                'noise_level': env.noise_level,
                'time_pressure': env.time_pressure,
                'available_tools_count': len(env.available_tools)
            },
            'coupling_score': round(coupling.coupling, 4),
            'emergent_iq': round(coupling.emergent_intelligence, 4),
            'adaptation_suggested': self._suggest_adaptation(env)
        }

    def _env_affordance(self, env: EnvironmentContext) -> float:
        """计算环境供给度"""
        # 工具丰富度 + 用户活跃度 - 噪声 - 时间压力
        tool_affordance = min(1.0, len(env.available_tools) / 10)
        state_score = {'active': 1.0, 'focused': 0.9, 'idle': 0.3, 'stressed': 0.5}
        user_affordance = state_score.get(env.user_state, 0.5)

        affordance = (
            0.3 * tool_affordance +
            0.3 * user_affordance +
            0.2 * (1 - env.noise_level) +
            0.2 * (1 - env.time_pressure)
        )
        return max(0.0, min(1.0, affordance))

    def _compute_env_complexity(self, env: EnvironmentContext) -> float:
        """计算环境复杂度"""
        return (
            0.3 * env.task_complexity +
            0.2 * env.noise_level +
            0.2 * env.time_pressure +
            0.15 * min(1.0, len(env.available_tools) / 20) +
            0.15 * (0.5 if env.user_state == 'active' else 0.3)
        )

    def _suggest_adaptation(self, env: EnvironmentContext) -> str:
        """建议自适应策略"""
        if env.noise_level > 0.6:
            return 'high_noise'
        elif env.time_pressure > 0.7:
            return 'high_pressure'
        elif env.user_state == 'idle':
            return 'idle_user'
        elif len(env.available_tools) < 3:
            return 'low_resources'
        return 'balanced'

    def compute_coupling_score(self, agent_capability: float, env_affordance: float) -> CouplingScore:
        """
        计算Agent-Environment耦合分数（T48核心）

        参数:
            agent_capability: Agent能力 [0,1]
            env_affordance: 环境供给度 [0,1]

        返回:
            CouplingScore: 耦合评估
        """
        # 耦合度 = 协同效应
        coupling = math.sqrt(agent_capability * env_affordance) * 2
        coupling = min(1.0, coupling)

        # 涌现智能 > max(Agent, Env) → 证明智能是耦合涌现
        emergent = coupling * (1 + 0.3 * abs(agent_capability - env_affordance))
        emergent = min(1.0, max(agent_capability, env_affordance) * (1 + coupling * 0.2))
        emergent = min(1.0, emergent)

        self.coupling_score = coupling
        self.emergent_iq = emergent

        return CouplingScore(
            agent_capability=agent_capability,
            env_affordance=env_affordance,
            coupling=coupling,
            emergent_intelligence=emergent
        )

    def adapt_to_environment(self, env_changes: Dict) -> Dict[str, Any]:
        """
        根据环境变化自适应调整策略

        参数:
            env_changes: 环境变化描述

        返回:
            dict: 调整策略
        """
        self.adaptation_count += 1

        # 感知变化
        env = self.sense_environment(env_changes)

        # 选择适应策略
        adaptation_key = env.get('adaptation_suggested', 'balanced')
        strategy = self._adaptation_strategies.get(adaptation_key, {})

        return {
            'adaptation_id': self.adaptation_count,
            'environment_change': env_changes,
            'detected_state': adaptation_key,
            'strategy': strategy,
            'new_coupling_score': round(self.coupling_score, 4),
            'new_emergent_iq': round(self.emergent_iq, 4),
            't48_status': f'智能={self.emergent_iq:.2f} (Agent×Env耦合涌现)'
        }

    def get_environment_profile(self) -> Dict[str, Any]:
        """获取当前环境画像"""
        if self._current_env is None:
            return {
                'status': 'no_data',
                'message': '尚未感知环境'
            }

        env = self._current_env
        return {
            'platform': env.platform,
            'user_state': env.user_state,
            'task_complexity': env.task_complexity,
            'noise_level': env.noise_level,
            'time_pressure': env.time_pressure,
            'tools_available': len(env.available_tools),
            'coupling_score': round(self.coupling_score, 4),
            'emergent_iq': round(self.emergent_iq, 4),
            'env_complexity': round(self.env_complexity, 4)
        }

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态"""
        return {
            'coupling_score': round(self.coupling_score, 4),
            'env_complexity': round(self.env_complexity, 4),
            'adaptation_count': self.adaptation_count,
            'last_env_type': self.last_env_type,
            'emergent_iq': round(self.emergent_iq, 4)
        }


# 单例模式
_instance = None

def get_instance():
    """获取模块单例"""
    global _instance
    if _instance is None:
        _instance = EnvironmentAwareness()
    return _instance
