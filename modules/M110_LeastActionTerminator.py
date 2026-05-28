# -*- coding: utf-8 -*-
"""M110: 最小作用量终止器 (Least Action Terminator)
基于论文1: 自指=最小阻力推理终止
核心定理：T60 最小作用量自指定理
     Action_total = Action_几何 + Action_物质 + λ·NonSelfRef
     自指解 ∝ e^(-λ/NonSelfRef)
关联：T59 自指闭环统一定理, T64 流贯扭转定理
"""

import math
import time
from typing import Dict, Any, List, Optional

class LeastActionTerminator:
    """最小作用量终止器 — 自指=最小阻力推理终止"""

    def __init__(self):
        # 作用量分量
        self.action_geometric: float = 1.0    # 几何作用量
        self.action_material: float = 0.5     # 物质作用量
        self.action_self_ref: float = 0.0     # 自指作用量
        self.action_total: float = 1.5        # 总作用量

        # 自指参数
        self.lambda_param: float = 1.0        # λ参数
        self.non_self_ref: float = 1.0       # NonSelfRef 非自指度
        self.self_ref_solution: float = 0.0   # 自指解 ∝ e^(-λ/NonSelfRef)

        # 终止条件
        self.is_terminated: bool = False
        self.termination_reason: str = 'running'
        self.action_gradient: float = 0.0    # 作用量梯度
        self.convergence_rate: float = 0.0    # 收敛速率

        # 推理路径
        self.reasoning_steps: int = 0
        self.min_action_path: List[Dict] = []
        self.current_action: float = 0.0

        # 自指-最小阻力映射
        self.self_ref_strength: float = 0.0
        self.min_resistance: float = 0.0

        # 统计
        self.total_terminations: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def compute_action(self, geometric: float = 0.0, material: float = 0.0,
                        lambda_val: float = 0.0, non_self_ref: float = 0.0) -> Dict[str, Any]:
        """计算总作用量 (T60)"""
        # 更新参数
        if geometric > 0:
            self.action_geometric = geometric
        if material > 0:
            self.action_material = material
        if lambda_val > 0:
            self.lambda_param = lambda_val
        if non_self_ref > 0:
            self.non_self_ref = non_self_ref

        # T60: Action_total = Action_几何 + Action_物质 + λ·NonSelfRef
        self.action_self_ref = self.lambda_param * self.non_self_ref
        self.action_total = self.action_geometric + self.action_material + self.action_self_ref

        # 自指解 ∝ e^(-λ/NonSelfRef)
        if self.non_self_ref > 1e-9:
            self.self_ref_solution = round(math.exp(-self.lambda_param / self.non_self_ref), 6)
        else:
            self.self_ref_solution = 0.0

        return {
            'action_geometric': round(self.action_geometric, 4),
            'action_material': round(self.action_material, 4),
            'action_self_ref': round(self.action_self_ref, 4),
            'action_total': round(self.action_total, 4),
            'self_ref_solution': self.self_ref_solution,
            'theorem': 'T60: Action = A_几何 + A_物质 + λ·NonSelfRef'
        }

    def check_termination(self) -> Dict[str, Any]:
        """检查推理终止条件 — 自指=最小阻力"""
        # 终止条件：作用量梯度趋近于零
        self.action_gradient = round(
            abs(self.action_geometric * 0.1 + self.action_material * 0.05 -
                self.self_ref_solution * self.lambda_param), 6
        )

        # 收敛速率
        if len(self.min_action_path) >= 2:
            prev = self.min_action_path[-2].get('action_total', self.action_total)
            curr = self.action_total
            self.convergence_rate = round(abs(curr - prev) / max(0.001, abs(prev)), 6)
        else:
            self.convergence_rate = 1.0

        # 自指=最小阻力
        self.self_ref_strength = self.self_ref_solution
        self.min_resistance = round(1.0 - self.self_ref_strength, 4)

        # 终止判定
        if self.action_gradient < 0.01:
            self.is_terminated = True
            self.termination_reason = 'min_action_reached'
        elif self.convergence_rate < 0.001:
            self.is_terminated = True
            self.termination_reason = 'converged'
        elif self.self_ref_solution > 0.9:
            self.is_terminated = True
            self.termination_reason = 'self_ref_dominant'
        else:
            self.is_terminated = False
            self.termination_reason = 'running'

        if self.is_terminated:
            self.total_terminations += 1

        return {
            'is_terminated': self.is_terminated,
            'termination_reason': self.termination_reason,
            'action_gradient': self.action_gradient,
            'convergence_rate': self.convergence_rate,
            'self_ref_strength': self.self_ref_strength,
            'min_resistance': self.min_resistance
        }

    def step_reasoning(self, step_data: Optional[Dict] = None) -> Dict[str, Any]:
        """执行一步推理，更新最小作用量路径"""
        if step_data:
            self.compute_action(
                geometric=step_data.get('geometric', self.action_geometric),
                material=step_data.get('material', self.action_material),
                lambda_val=step_data.get('lambda', self.lambda_param),
                non_self_ref=step_data.get('non_self_ref', self.non_self_ref)
            )

        self.reasoning_steps += 1
        self.current_action = self.action_total

        path_entry = {
            'step': self.reasoning_steps,
            'action_total': round(self.action_total, 4),
            'self_ref_solution': self.self_ref_solution,
            'gradient': self.action_gradient
        }
        self.min_action_path.append(path_entry)
        self.min_action_path = self.min_action_path[-50:]  # keep last 50

        self.check_termination()

        return {
            'step': self.reasoning_steps,
            'action_total': round(self.action_total, 4),
            'terminated': self.is_terminated,
            'reason': self.termination_reason
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """更新状态"""
        if data:
            self.step_reasoning(data)
        else:
            self.check_termination()

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            'action_geometric': round(self.action_geometric, 4),
            'action_material': round(self.action_material, 4),
            'action_self_ref': round(self.action_self_ref, 4),
            'action_total': round(self.action_total, 4),
            'self_ref_solution': self.self_ref_solution,
            'lambda_param': self.lambda_param,
            'non_self_ref': round(self.non_self_ref, 4),
            'is_terminated': self.is_terminated,
            'termination_reason': self.termination_reason,
            'action_gradient': self.action_gradient,
            'convergence_rate': self.convergence_rate,
            'self_ref_strength': self.self_ref_strength,
            'min_resistance': self.min_resistance,
            'reasoning_steps': self.reasoning_steps,
            'total_terminations': self.total_terminations,
            'frame_count': self.frame_count,
            'status': 'terminated' if self.is_terminated else 'reasoning',
            'last_update': self.last_update
        }

    def simulate(self) -> Dict[str, Any]:
        """模拟运行"""
        # 模拟5步推理
        for i in range(5):
            self.step_reasoning({
                'geometric': 1.0 - i * 0.15,
                'material': 0.5 + i * 0.05,
                'lambda': 1.0 + i * 0.2,
                'non_self_ref': max(0.1, 1.0 - i * 0.2)
            })
        return self.update()


# 全局单例
_leaction_instance: Optional[LeastActionTerminator] = None

def get_instance() -> LeastActionTerminator:
    global _leaction_instance
    if _leaction_instance is None:
        _leaction_instance = LeastActionTerminator()
    return _leaction_instance

def update(data=None): return get_instance().update(data)
def get_state(): return get_instance().get_state()
def simulate(): return get_instance().simulate()
