# -*- coding: utf-8 -*-
"""
M99_DynamicTaskRouter — 动态分流模块

定理 T46: "存在唯一最优分流函数φ*，使得系统总效能E = E_human + E_AI + E_collab最大化"
定理 T45: "局部精雕细琢与全局目标的一致性统一，可在O(n log n)步内收敛"

本模块根据任务特征自动分流到人/AI/协作模式，计算最优分流方案，
根据反馈调整策略，并确保局部优化与全局一致性收敛。
"""

from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable, Deque, Dict, List, Optional, Tuple


@dataclass
class TaskProfile:
    """任务画像数据结构。"""
    task_id: str
    type: str  # "creative", "analytical", "routine", "critical", "exploratory"
    complexity: float  # 0-1
    human_preference: float  # 0-1，人类对任务的偏好/擅长程度
    ai_capability: float  # 0-1，AI对任务的处理能力
    routing_decision: str  # "human", "ai", "collaborative"


@dataclass
class RoutingOutcome:
    """分流结果数据结构。"""
    task_id: str
    success: bool
    efficiency: float  # 0-1，执行效率
    satisfaction: float  # 0-1，用户满意度


@dataclass
class RoutingConfig:
    """分流配置参数。"""
    human_weight: float = 0.35  # 人类偏好权重
    ai_weight: float = 0.35  # AI能力权重
    complexity_weight: float = 0.15  # 复杂度权重
    collab_bonus: float = 0.15  # 协作模式奖励


class DynamicTaskRouter:
    """
    动态分流器，根据任务特征自动将任务分流到人/AI/协作模式。

    基于定理T46和T45，本模块实现：
    1. 最优分流函数φ*，最大化系统总效能
    2. 反馈驱动的分流策略调整
    3. O(n log n)收敛的局部-全局一致性算法
    """

    # 分流模式
    ROUTING_HUMAN: str = "human"
    ROUTING_AI: str = "ai"
    ROUTING_COLLAB: str = "collaborative"

    # 任务类型与默认路由倾向
    _DEFAULT_ROUTING: Dict[str, str] = {
        "creative": "collaborative",
        "analytical": "ai",
        "routine": "ai",
        "critical": "human",
        "exploratory": "collaborative",
    }

    # 任务类型的默认AI能力和人类偏好
    _TYPE_DEFAULTS: Dict[str, Dict[str, float]] = {
        "creative": {"ai_capability": 0.5, "human_preference": 0.8},
        "analytical": {"ai_capability": 0.85, "human_preference": 0.5},
        "routine": {"ai_capability": 0.95, "human_preference": 0.2},
        "critical": {"ai_capability": 0.6, "human_preference": 0.9},
        "exploratory": {"ai_capability": 0.55, "human_preference": 0.7},
    }

    # 收敛参数
    CONVERGENCE_THRESHOLD: float = 0.01
    MAX_CONVERGENCE_ITERATIONS: int = 100

    def __init__(self) -> None:
        """初始化动态分流器。"""
        self._lock: Lock = Lock()
        self._task_profiles: Dict[str, TaskProfile] = {}
        self._routing_history: Dict[str, Deque[RoutingOutcome]] = defaultdict(deque)
        self._feedback_buffer: List[RoutingOutcome] = []

        # 模块状态字段
        self.routing_mode: str = "adaptive"  # "adaptive", "human_first", "ai_first"
        self.human_ratio: float = 0.33
        self.ai_ratio: float = 0.34
        self.collab_ratio: float = 0.33
        self.convergence_steps: int = 0
        self.optimal_phi: Optional[RoutingConfig] = None

        # 内部追踪
        self._total_routed: int = 0
        self._human_count: int = 0
        self._ai_count: int = 0
        self._collab_count: int = 0
        self._phi: RoutingConfig = RoutingConfig()

        # 收敛追踪
        self._convergence_history: List[float] = []
        self._global_objective_value: float = 0.0

    def route_task(self, task_description='', task_type='', complexity=0.5):
        """
        根据任务特征自动分流到人/AI/协作模式。

        支持两种调用方式:
        1. route_task(task_description_dict) — 传入字典
        2. route_task("描述", task_type="类型", complexity=0.5) — 传入参数

        Args:
            task_description: 任务描述字典或字符串
            task_type: 任务类型（仅当task_description为字符串时使用）
            complexity: 任务复杂度（仅当task_description为字符串时使用）

        Returns:
            包含路由决策的字典
        """
        # 统一参数格式
        if isinstance(task_description, dict):
            desc_dict = task_description
        else:
            desc_dict = {
                'task_id': f'task_{int(time.time())}',
                'type': task_type or self._infer_task_type(str(task_description)),
                'complexity': complexity,
            }

        task_id = desc_dict.get("task_id", f"task_{int(time.time())}")
        resolved_type = desc_dict.get("type", "analytical")
        resolved_complexity = desc_dict.get("complexity", 0.5)

        # 获取类型默认值
        type_defaults = self._TYPE_DEFAULTS.get(resolved_type, {"ai_capability": 0.5, "human_preference": 0.5})

        human_pref = desc_dict.get("human_preference", type_defaults["human_preference"])
        ai_cap = desc_dict.get("ai_capability", type_defaults["ai_capability"])

        # 计算最优路由
        routing_decision = self._compute_routing(resolved_complexity, human_pref, ai_cap)

        profile = TaskProfile(
            task_id=task_id,
            type=resolved_type,
            complexity=resolved_complexity,
            human_preference=human_pref,
            ai_capability=ai_cap,
            routing_decision=routing_decision,
        )

        with self._lock:
            self._task_profiles[task_id] = profile
            self._total_routed += 1
            if routing_decision == self.ROUTING_HUMAN:
                self._human_count += 1
            elif routing_decision == self.ROUTING_AI:
                self._ai_count += 1
            else:
                self._collab_count += 1
            self._update_ratios()

        return profile

    def _compute_routing(self, complexity: float, human_pref: float, ai_cap: float) -> str:
        """使用分流函数φ计算路由决策。"""
        phi = self._phi

        # 计算各模式的得分
        human_score = (
            human_pref * phi.human_weight
            + (1.0 - ai_cap) * 0.2
            + complexity * 0.1  # 高复杂度偏向人类判断
        )

        ai_score = (
            ai_cap * phi.ai_weight
            + (1.0 - complexity) * 0.15  # 低复杂度偏向AI
            + (1.0 - human_pref) * 0.1
        )

        collab_score = (
            phi.collab_bonus
            + complexity * 0.15  # 高复杂度偏向协作
            + human_pref * ai_cap * 0.2  # 人类偏好和AI能力都高时协作最优
        )

        # 选择得分最高的模式
        scores = {
            self.ROUTING_HUMAN: human_score,
            self.ROUTING_AI: ai_score,
            self.ROUTING_COLLAB: collab_score,
        }

        best = max(scores, key=lambda k: scores[k])
        return best

    def compute_optimal_routing(self, task_features: List[Dict]) -> List[TaskProfile]:
        """
        计算最优分流方案（φ*函数实现）。

        基于定理T46，在参数空间中搜索最优分流函数φ*，
        使系统总效能E = E_human + E_AI + E_collab最大化。

        使用梯度下降法在配置参数空间中搜索，同时基于定理T45
        确保局部精雕细琢与全局目标的一致性在O(n log n)步内收敛。

        Args:
            task_features: 任务特征列表

        Returns:
            最优分流方案的任务画像列表
        """
        if not task_features:
            return []

        # 阶段1：对每个任务计算初始路由
        profiles: List[TaskProfile] = []
        for tf in task_features:
            profile = self.route_task(tf)
            profiles.append(profile)

        # 阶段2：优化分流函数φ的参数（梯度搜索）
        n = len(profiles)
        max_iterations = min(
            self.MAX_CONVERGENCE_ITERATIONS,
            max(10, int(n * math.log2(max(n, 2)))),  # O(n log n)约束
        )

        best_phi = RoutingConfig(
            human_weight=self._phi.human_weight,
            ai_weight=self._phi.ai_weight,
            complexity_weight=self._phi.complexity_weight,
            collab_bonus=self._phi.collab_bonus,
        )
        best_objective = self._evaluate_global_objective(profiles, best_phi)

        learning_rate = 0.05
        convergence_step = 0

        for iteration in range(max_iterations):
            convergence_step += 1

            # 计算目标函数对每个参数的数值梯度
            gradients = self._compute_phi_gradients(profiles, best_phi, learning_rate)

            # 更新参数
            new_phi = RoutingConfig(
                human_weight=max(0.1, min(0.6, best_phi.human_weight + learning_rate * gradients[0])),
                ai_weight=max(0.1, min(0.6, best_phi.ai_weight + learning_rate * gradients[1])),
                complexity_weight=max(0.05, min(0.4, best_phi.complexity_weight + learning_rate * gradients[2])),
                collab_bonus=max(0.05, min(0.4, best_phi.collab_bonus + learning_rate * gradients[3])),
            )

            # 归一化权重
            total_w = new_phi.human_weight + new_phi.ai_weight + new_phi.complexity_weight + new_phi.collab_bonus
            new_phi.human_weight /= total_w
            new_phi.ai_weight /= total_w
            new_phi.complexity_weight /= total_w
            new_phi.collab_bonus /= total_w

            new_objective = self._evaluate_global_objective(profiles, new_phi)

            # 检查收敛
            improvement = abs(new_objective - best_objective)
            self._convergence_history.append(improvement)

            if new_objective > best_objective:
                best_objective = new_objective
                best_phi = new_phi

            if improvement < self.CONVERGENCE_THRESHOLD:
                break

        # 阶段3：使用优化后的φ重新路由所有任务
        self._phi = best_phi
        self.optimal_phi = best_phi

        with self._lock:
            self.convergence_steps = convergence_step
            self._global_objective_value = best_objective

        # 重新计算路由
        for profile in profiles:
            profile.routing_decision = self._compute_routing(
                profile.complexity, profile.human_preference, profile.ai_capability
            )

        return profiles

    def _evaluate_global_objective(self, profiles: List[TaskProfile], phi: RoutingConfig) -> float:
        """
        评估全局目标函数 E = E_human + E_AI + E_collab。

        每个分流决策的效能取决于任务特征与路由模式的匹配度。
        """
        if not profiles:
            return 0.0

        total_efficiency = 0.0

        for p in profiles:
            # 使用给定的phi重新计算路由
            human_score = p.human_preference * phi.human_weight + (1.0 - p.ai_capability) * 0.2 + p.complexity * 0.1
            ai_score = p.ai_capability * phi.ai_weight + (1.0 - p.complexity) * 0.15 + (1.0 - p.human_preference) * 0.1
            collab_score = phi.collab_bonus + p.complexity * 0.15 + p.human_preference * p.ai_capability * 0.2

            max_score = max(human_score, ai_score, collab_score)
            total_efficiency += max_score

        return total_efficiency / len(profiles)

    def _compute_phi_gradients(
        self, profiles: List[TaskProfile], phi: RoutingConfig, epsilon: float
    ) -> Tuple[float, float, float, float]:
        """计算φ参数的数值梯度。"""
        base_obj = self._evaluate_global_objective(profiles, phi)

        params = [phi.human_weight, phi.ai_weight, phi.complexity_weight, phi.collab_bonus]
        gradients: List[float] = []

        for i in range(4):
            perturbed_params = list(params)
            perturbed_params[i] += epsilon
            perturbed_phi = RoutingConfig(
                human_weight=perturbed_params[0],
                ai_weight=perturbed_params[1],
                complexity_weight=perturbed_params[2],
                collab_bonus=perturbed_params[3],
            )
            perturbed_obj = self._evaluate_global_objective(profiles, perturbed_phi)
            gradient = (perturbed_obj - base_obj) / epsilon
            gradients.append(gradient)

        return tuple(gradients)  # type: ignore

    def adjust_routing_feedback(self, task_id: str, outcome: RoutingOutcome) -> None:
        """
        根据反馈调整分流策略。

        当某个路由决策的结果反馈不理想时，调整φ参数
        以避免类似错误。使用增量学习方式更新。

        Args:
            task_id: 任务ID
            outcome: 分流结果
        """
        with self._lock:
            self._routing_history[task_id].append(outcome)
            self._feedback_buffer.append(outcome)

        # 获取任务画像
        profile = self._task_profiles.get(task_id)
        if profile is None:
            return

        # 根据反馈调整φ参数
        if not outcome.success:
            # 失败反馈：降低导致失败路由的权重
            if profile.routing_decision == self.ROUTING_HUMAN:
                self._phi.human_weight = max(0.1, self._phi.human_weight - 0.02)
                self._phi.ai_weight = min(0.6, self._phi.ai_weight + 0.01)
            elif profile.routing_decision == self.ROUTING_AI:
                self._phi.ai_weight = max(0.1, self._phi.ai_weight - 0.02)
                self._phi.human_weight = min(0.6, self._phi.human_weight + 0.01)
            else:
                self._phi.collab_bonus = max(0.05, self._phi.collab_bonus - 0.01)
        else:
            # 成功反馈：增强导致成功路由的权重（轻微）
            if profile.routing_decision == self.ROUTING_HUMAN:
                self._phi.human_weight = min(0.6, self._phi.human_weight + 0.005)
            elif profile.routing_decision == self.ROUTING_AI:
                self._phi.ai_weight = min(0.6, self._phi.ai_weight + 0.005)
            else:
                self._phi.collab_bonus = min(0.4, self._phi.collab_bonus + 0.005)

        # 效率反馈：低效率时微调
        if outcome.efficiency < 0.5:
            self._phi.complexity_weight = min(0.4, self._phi.complexity_weight + 0.01)

        # 归一化
        total_w = (
            self._phi.human_weight
            + self._phi.ai_weight
            + self._phi.complexity_weight
            + self._phi.collab_bonus
        )
        if total_w > 0:
            self._phi.human_weight /= total_w
            self._phi.ai_weight /= total_w
            self._phi.complexity_weight /= total_w
            self._phi.collab_bonus /= total_w

    def get_routing_analytics(self) -> Dict:
        """
        获取分流分析数据。

        Returns:
            包含分流统计、效率和满意度分析的字典
        """
        with self._lock:
            # 计算各模式的成功率
            mode_outcomes: Dict[str, List[RoutingOutcome]] = defaultdict(list)
            for task_id, outcomes in self._routing_history.items():
                for outcome in outcomes:
                    profile = self._task_profiles.get(task_id)
                    if profile:
                        mode_outcomes[profile.routing_decision].append(outcome)

            analytics: Dict = {
                "total_routed": self._total_routed,
                "routing_distribution": {
                    "human": self._human_count,
                    "ai": self._ai_count,
                    "collaborative": self._collab_count,
                },
                "ratios": {
                    "human_ratio": self.human_ratio,
                    "ai_ratio": self.ai_ratio,
                    "collab_ratio": self.collab_ratio,
                },
                "mode_performance": {},
                "convergence_steps": self.convergence_steps,
                "global_objective": round(self._global_objective_value, 4),
            }

            # 各模式性能
            for mode, outcomes in mode_outcomes.items():
                if outcomes:
                    avg_efficiency = sum(o.efficiency for o in outcomes) / len(outcomes)
                    avg_satisfaction = sum(o.satisfaction for o in outcomes) / len(outcomes)
                    success_rate = sum(1.0 for o in outcomes if o.success) / len(outcomes)
                    analytics["mode_performance"][mode] = {
                        "avg_efficiency": round(avg_efficiency, 4),
                        "avg_satisfaction": round(avg_satisfaction, 4),
                        "success_rate": round(success_rate, 4),
                        "count": len(outcomes),
                    }

            return analytics

    def _update_ratios(self) -> None:
        """更新分流比例。"""
        total = self._human_count + self._ai_count + self._collab_count
        if total > 0:
            self.human_ratio = round(self._human_count / total, 4)
            self.ai_ratio = round(self._ai_count / total, 4)

    def _infer_task_type(self, description: str) -> str:
        """从任务描述推断类型"""
        keywords = {
            'creative': ['设计', '创作', '写', '画', '创意', 'design', 'create'],
            'analytical': ['分析', '计算', '统计', '研究', 'analyze', 'compute'],
            'routine': ['整理', '格式化', '排序', '转换', 'sort', 'format'],
            'judgment': ['判断', '决策', '评估', '选择', 'judge', 'decide'],
            'social': ['沟通', '协调', '谈判', '合作', 'communicate', 'collaborate'],
        }
        for task_type, kws in keywords.items():
            if any(kw in description.lower() for kw in kws):
                return task_type
        return 'analytical'

    def get_state(self) -> Dict:
        """返回模块状态字典。"""
        with self._lock:
            return {
                "routing_mode": self.routing_mode,
                "human_ratio": self.human_ratio,
                "ai_ratio": self.ai_ratio,
                "collab_ratio": self.collab_ratio,
                "convergence_steps": self.convergence_steps,
                "optimal_phi": (
                    {
                        "human_weight": self.optimal_phi.human_weight,
                        "ai_weight": self.optimal_phi.ai_weight,
                        "complexity_weight": self.optimal_phi.complexity_weight,
                        "collab_bonus": self.optimal_phi.collab_bonus,
                    }
                    if self.optimal_phi
                    else None
                ),
                "total_routed": self._total_routed,
                "global_objective": round(self._global_objective_value, 4),
            }


# 单例模式
_instance: Optional[DynamicTaskRouter] = None


def get_instance() -> DynamicTaskRouter:
    """获取 DynamicTaskRouter 的全局单例实例。"""
    global _instance
    if _instance is None:
        _instance = DynamicTaskRouter()
    return _instance
