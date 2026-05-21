"""
M161 后向流贯卷积 — BackwardFlowConvolution
=============================================
论文来源：六元对偶卷积架构，方程Eq5，定理T2.5
核心定理：T128（流贯方向定理）— 反转卷积索引方向，模拟反馈与记忆
对偶轴：前馈(Feed-forward) <-> 反馈(Feedback)
时间反演：引入自指闭环，是递归智能的核心
与M131(关系作用量)桥接
"""

from __future__ import annotations

import math
import random
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class FlowDirection(Enum):
    """流贯方向"""
    FORWARD = "forward"    # 前馈：标准卷积方向
    BACKWARD = "backward"  # 反馈：反转索引方向
    BIDIRECTIONAL = "bidirectional"  # 双向：前馈+反馈


@dataclass
class FlowMemory:
    """流贯记忆状态"""
    history: List[float] = field(default_factory=list)
    max_depth: int = 10
    decay_rate: float = 0.9  # 记忆衰减率


@dataclass
class BackwardFlowState:
    """后向流贯卷积状态"""
    direction: FlowDirection = FlowDirection.BACKWARD
    memory: FlowMemory = field(default_factory=FlowMemory)
    recursion_depth: int = 0        # 递归深度
    self_reference_active: bool = True  # 自指闭环开关
    relation_action: float = 0.0    # M131 关系作用量
    total_convolutions: int = 0
    last_signal_length: int = 0
    last_kernel_length: int = 0
    created_at: float = field(default_factory=time.time)


class BackwardFlowConvolution:
    """
    后向流贯卷积 (Eq5/T2.5)

    定理T128：流贯方向定理
    反转卷积索引方向，从"未来"向"过去"流动，
    模拟反馈与记忆机制。

    标准卷积：y[t] = sum_i x[t-i] * k[i]  (前馈)
    后向卷积：y[t] = sum_i x[t+i] * k[i]  (反馈)

    时间反演引入自指闭环：
    输出不仅依赖过去，还依赖"未来"的预测，
    构成递归智能的核心回路。

    与M131(关系作用量)桥接：
    流贯方向影响作用量的符号，反向流贯对应负作用量。
    """

    _instance: Optional[BackwardFlowConvolution] = None

    def __init__(self, direction: FlowDirection = FlowDirection.BACKWARD,
                 relation_action: float = 0.0) -> None:
        self._state = BackwardFlowState(
            direction=direction,
            relation_action=relation_action,
        )

    @classmethod
    def get_instance(cls, direction: FlowDirection = FlowDirection.BACKWARD,
                     relation_action: float = 0.0
                     ) -> BackwardFlowConvolution:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(
                direction=direction, relation_action=relation_action
            )
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """重置单例（仅测试用）"""
        cls._instance = None

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        mem = self._state.memory
        return {
            "module": "M161_BackwardFlowConvolution",
            "direction": self._state.direction.value,
            "recursion_depth": self._state.recursion_depth,
            "self_reference_active": self._state.self_reference_active,
            "relation_action": self._state.relation_action,
            "memory_depth": len(mem.history),
            "memory_decay": mem.decay_rate,
            "total_convolutions": self._state.total_convolutions,
            "last_signal_length": self._state.last_signal_length,
            "last_kernel_length": self._state.last_kernel_length,
            "created_at": self._state.created_at,
        }

    def _forward_convolve(self, signal: List[float],
                          kernel: List[float]) -> List[float]:
        """标准前馈卷积：y[t] = sum_i x[t-i] * k[i]"""
        n = len(signal)
        m = len(kernel)
        result: List[float] = []
        for t in range(n + m - 1):
            acc = 0.0
            for i in range(m):
                s_idx = t - i
                if 0 <= s_idx < n:
                    acc += signal[s_idx] * kernel[i]
            result.append(acc)
        return result

    def _backward_convolve_core(self, signal: List[float],
                                kernel: List[float]) -> List[float]:
        """
        后向卷积核心：y[t] = sum_i x[t+i] * k[i]

        索引方向反转：不是从过去采样，而是从"未来"采样
        """
        n = len(signal)
        m = len(kernel)
        result: List[float] = []
        for t in range(n):
            acc = 0.0
            for i in range(m):
                s_idx = t + i
                if 0 <= s_idx < n:
                    acc += signal[s_idx] * kernel[i]
            result.append(acc)
        return result

    def _apply_memory_feedback(self, signal: List[float],
                               conv_result: List[float]
                               ) -> List[float]:
        """
        记忆反馈：将历史结果加权反馈到当前输出

        自指闭环：y[t] += decay * history[t]
        """
        mem = self._state.memory
        if not self._state.self_reference_active:
            return conv_result

        result: List[float] = []
        for i, val in enumerate(conv_result):
            feedback = 0.0
            if i < len(mem.history):
                feedback = mem.history[i] * mem.decay_rate
            result.append(val + feedback)

        # 更新记忆
        mem.history = conv_result[:mem.max_depth]
        return result

    def _apply_relation_action(self, result: List[float]
                               ) -> List[float]:
        """
        M131桥接：关系作用量修正

        反向流贯对应负作用量方向，
        修正卷积结果的梯度传播。
        """
        s = self._state.relation_action
        if abs(s) < 1e-12:
            return result

        correction: List[float] = []
        for val in result:
            # 作用量修正：指数衰减
            adjusted = val * math.exp(-abs(s) * 0.01)
            correction.append(adjusted)
        return correction

    def backward_convolve(self, signal: List[float],
                          kernel: List[float]
                          ) -> Dict[str, Any]:
        """
        后向流贯卷积 (Eq5)

        定理T128：流贯方向定理
        1. 反转卷积索引方向（前馈 -> 反馈）
        2. 引入记忆反馈（自指闭环）
        3. 应用M131关系作用量修正

        Args:
            signal: 输入信号序列
            kernel: 卷积核序列

        Returns:
            包含result和metadata的字典
        """
        if len(signal) == 0 or len(kernel) == 0:
            return {"result": [], "metadata": {"error": "空输入"}}

        # 后向卷积
        backward_result = self._backward_convolve_core(signal, kernel)

        # 记忆反馈
        feedback_result = self._apply_memory_feedback(
            signal, backward_result
        )

        # M131关系作用量修正
        final_result = self._apply_relation_action(feedback_result)

        # 计算前馈结果（用于对比）
        forward_result = self._forward_convolve(signal, kernel)

        self._state.recursion_depth = len(
            [v for v in self._state.memory.history if abs(v) > 1e-6]
        )
        self._state.total_convolutions += 1
        self._state.last_signal_length = len(signal)
        self._state.last_kernel_length = len(kernel)

        metadata = {
            "theorem": "T128",
            "equation": "Eq5",
            "direction": self._state.direction.value,
            "forward_result": [round(v, 4) for v in forward_result[:5]],
            "backward_result": [round(v, 4) for v in backward_result[:5]],
            "recursion_depth": self._state.recursion_depth,
            "self_reference_active": self._state.self_reference_active,
            "relation_action": self._state.relation_action,
        }
        return {"result": final_result, "metadata": metadata}

    def verify_theorem(self) -> Dict[str, Any]:
        """
        验证定理T128：流贯方向定理

        验证1：后向卷积不等于前馈卷积
        验证2：后向卷积结果的时间对称性
        """
        signal = [1.0, 2.0, 3.0, 4.0, 5.0]
        kernel = [1.0, 0.5, 0.25]

        forward = self._forward_convolve(signal, kernel)
        backward = self._backward_convolve_core(signal, kernel)

        # 验证1：后向不等于前馈
        different = any(
            abs(a - b) > 1e-6 for a, b in zip(forward, backward)
        )

        # 验证2：后向卷积的时间反转性
        # backward(signal)[t] = forward(signal_reversed)[n-1-t]
        signal_rev = signal[::-1]
        forward_rev = self._forward_convolve(signal_rev, kernel)
        n = len(signal)
        time_reverse_match = all(
            abs(backward[t] - forward_rev[n - 1 - t]) < 1e-6
            for t in range(min(len(backward), n))
        )

        return {
            "theorem": "T128",
            "verified": different,
            "detail": "流贯方向定理：后向卷积方向反转，"
                      "不等于前馈卷积",
            "backward_differs_from_forward": different,
            "time_reverse_symmetry": time_reverse_match,
            "forward_sample": [round(v, 4) for v in forward[:5]],
            "backward_sample": [round(v, 4) for v in backward[:5]],
        }

    def api_convolve(self, signal: List[float],
                     kernel: List[float]
                     ) -> Dict[str, Any]:
        """API辅助方法"""
        res = self.backward_convolve(signal, kernel)
        state = self.get_state()
        return {
            "api": "M161/backward_convolve",
            "result": res["result"],
            "metadata": res["metadata"],
            "state": state,
        }


def get_instance(direction: FlowDirection = FlowDirection.BACKWARD,
                 relation_action: float = 0.0
                 ) -> BackwardFlowConvolution:
    """模块级单例获取函数"""
    return BackwardFlowConvolution.get_instance(
        direction=direction, relation_action=relation_action
    )


if __name__ == "__main__":
    print("=" * 60)
    print("M161 后向流贯卷积 — 自测")
    print("=" * 60)

    conv = BackwardFlowConvolution.get_instance()
    print(f"\n[状态] {conv.get_state()}")

    signal = [1.0, 2.0, 3.0, 4.0, 5.0]
    kernel = [1.0, 0.5, 0.25]

    print(f"\n输入信号: {signal}")
    print(f"卷积核: {kernel}")

    res = conv.backward_convolve(signal, kernel)
    print(f"\n后向流贯卷积结果:")
    print(f"  result = {[round(v, 4) for v in res['result']]}")
    print(f"  metadata = {res['metadata']}")

    # 验证定理
    verification = conv.verify_theorem()
    print(f"\n定理T128验证: {verification['verified']}")
    print(f"  后向!=前馈: {verification['backward_differs_from_forward']}")
    print(f"  时间反转对称: {verification['time_reverse_symmetry']}")
    print(f"  前馈样本: {verification['forward_sample']}")
    print(f"  后向样本: {verification['backward_sample']}")

    # API测试
    api_res = conv.api_convolve(signal, kernel)
    print(f"\nAPI调用结果长度: {len(api_res['result'])}")

    print("\n" + "=" * 60)
    print("M161 自测完成")
    print("=" * 60)
