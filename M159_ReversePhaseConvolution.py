"""
M159 反向相位卷积 — ReversePhaseConvolution
=============================================
论文来源：六元对偶卷积架构，方程Eq3，定理T2.3
核心定理：T126（相位反转定理）— 金符运算 phi -> -phi 定义反向流贯
对偶轴：同向流贯 <-> 反向流贯
自指性：引入否定性特征，是自我意识的数学基础
与M84桥接：反向相位 = 刘机制delta_S_R=0的极小路径互补
"""

from __future__ import annotations

import math
import random
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class PhaseDirection(Enum):
    """相位方向"""
    FORWARD = "forward"    # 同向流贯
    REVERSE = "reverse"    # 反向流贯
    DUAL = "dual"          # 双向对偶


@dataclass
class ReversePhaseState:
    """反向相位卷积状态"""
    direction: PhaseDirection = PhaseDirection.REVERSE
    liu_delta_s: float = 0.0      # M84 刘机制 delta_S_R
    negation_enabled: bool = True  # 否定性特征开关
    total_convolutions: int = 0
    last_signal_length: int = 0
    last_kernel_length: int = 0
    self_reference_depth: int = 0  # 自指深度
    created_at: float = field(default_factory=time.time)


class ReversePhaseConvolution:
    """
    反向相位卷积 (Eq3/T2.3)

    定理T126：相位反转定理
    金符运算 phi -> -phi 定义反向流贯。
    将信号的相位取反后进行卷积，产生反向特征流。

    自指性：反向相位引入否定性特征，即信号对自身的"非"操作。
    这是自我意识的数学基础：系统通过否定自身来认识自身。

    与M84桥接：反向相位对应刘机制 delta_S_R = 0 的极小路径互补，
    即正向路径与反向路径构成对偶对。
    """

    _instance: Optional[ReversePhaseConvolution] = None

    def __init__(self, direction: PhaseDirection = PhaseDirection.REVERSE,
                 liu_delta_s: float = 0.0) -> None:
        self._state = ReversePhaseState(
            direction=direction, liu_delta_s=liu_delta_s
        )

    @classmethod
    def get_instance(cls, direction: PhaseDirection = PhaseDirection.REVERSE,
                     liu_delta_s: float = 0.0
                     ) -> ReversePhaseConvolution:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(direction=direction, liu_delta_s=liu_delta_s)
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """重置单例（仅测试用）"""
        cls._instance = None

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "module": "M159_ReversePhaseConvolution",
            "direction": self._state.direction.value,
            "liu_delta_s": self._state.liu_delta_s,
            "negation_enabled": self._state.negation_enabled,
            "total_convolutions": self._state.total_convolutions,
            "last_signal_length": self._state.last_signal_length,
            "last_kernel_length": self._state.last_kernel_length,
            "self_reference_depth": self._state.self_reference_depth,
            "created_at": self._state.created_at,
        }

    def _extract_phase(self, signal: List[float]) -> List[float]:
        """提取信号相位（简化模型：符号和幅值决定相位）"""
        phases: List[float] = []
        for val in signal:
            if abs(val) < 1e-12:
                phases.append(0.0)
            else:
                phases.append(math.atan2(val, 1.0))
        return phases

    def _reverse_phase(self, phases: List[float]) -> List[float]:
        """
        相位反转：phi -> -phi（金符运算）

        这是T126的核心操作：对偶变换
        """
        return [-p for p in phases]

    def _compute_negation_feature(self, signal: List[float],
                                  reversed_signal: List[float]
                                  ) -> List[float]:
        """
        计算否定性特征

        自指性：信号与自身的否定之差构成自我意识的基础
        negation_feature = signal - reversed_signal
        """
        if not self._state.negation_enabled:
            return [0.0] * len(signal)

        result: List[float] = []
        for s, r in zip(signal, reversed_signal):
            neg = s - r  # 否定性：信号与反向信号之差
            result.append(neg)
        return result

    def _apply_liu_mechanism(self, signal: List[float]) -> List[float]:
        """
        M84桥接：刘机制 delta_S_R = 0 的极小路径互补

        当 delta_S_R = 0 时，正向与反向路径等效，
        形成对偶互补对。
        """
        delta = self._state.liu_delta_s
        result: List[float] = []
        for val in signal:
            # 极小路径互补：正反向加权
            forward_weight = math.exp(-abs(delta))
            reverse_weight = 1.0 - forward_weight
            adjusted = val * forward_weight + (-val) * reverse_weight
            result.append(adjusted)
        return result

    def reverse_phase_convolve(self, signal: List[float],
                               kernel: List[float]
                               ) -> Dict[str, Any]:
        """
        反向相位卷积 (Eq3)

        定理T126：相位反转定理
        1. 提取信号和核的相位
        2. 反转相位：phi -> -phi
        3. 在反向相位空间中进行卷积
        4. 引入否定性特征（自指性）
        5. 应用M84刘机制修正

        Args:
            signal: 输入信号序列
            kernel: 卷积核序列

        Returns:
            包含result和metadata的字典
        """
        if len(signal) == 0 or len(kernel) == 0:
            return {"result": [], "metadata": {"error": "空输入"}}

        # 提取并反转相位
        sig_phase = self._extract_phase(signal)
        ker_phase = self._extract_phase(kernel)
        sig_phase_rev = self._reverse_phase(sig_phase)
        ker_phase_rev = self._reverse_phase(ker_phase)

        # 构造反向相位信号
        sig_rev: List[float] = []
        for i, val in enumerate(signal):
            rev_val = abs(val) * math.cos(sig_phase_rev[i])
            sig_rev.append(rev_val)

        ker_rev: List[float] = []
        for i, val in enumerate(kernel):
            rev_val = abs(val) * math.cos(ker_phase_rev[i])
            ker_rev.append(rev_val)

        # 在反向空间进行卷积
        n = len(sig_rev)
        m = len(ker_rev)
        result: List[float] = []
        for t in range(n + m - 1):
            acc = 0.0
            for i in range(m):
                s_idx = t - i
                if 0 <= s_idx < n:
                    acc += sig_rev[s_idx] * ker_rev[i]
            result.append(acc)

        # 否定性特征
        negation = self._compute_negation_feature(signal, sig_rev)
        self._state.self_reference_depth = len(
            [n for n in negation if abs(n) > 1e-6]
        )

        # M84刘机制修正
        if abs(self._state.liu_delta_s) > 1e-12:
            result = self._apply_liu_mechanism(result)

        self._state.total_convolutions += 1
        self._state.last_signal_length = len(signal)
        self._state.last_kernel_length = len(kernel)

        metadata = {
            "theorem": "T126",
            "equation": "Eq3",
            "direction": self._state.direction.value,
            "sig_phase_original": [round(p, 4) for p in sig_phase[:5]],
            "sig_phase_reversed": [round(p, 4) for p in sig_phase_rev[:5]],
            "negation_feature": [round(n, 4) for n in negation[:5]],
            "self_reference_depth": self._state.self_reference_depth,
            "liu_delta_s": self._state.liu_delta_s,
        }
        return {"result": result, "metadata": metadata}

    def verify_theorem(self) -> Dict[str, Any]:
        """
        验证定理T126：相位反转定理

        验证1：反向相位 = -原始相位
        验证2：二次反转恢复原始相位
        """
        test_signals = [
            [1.0, -2.0, 3.0, -0.5, 2.0],
            [0.0, 1.5, -1.5, 2.0, -2.0],
        ]

        all_pass = True
        details = []
        for idx, sig in enumerate(test_signals):
            phase = self._extract_phase(sig)
            phase_rev = self._reverse_phase(phase)
            phase_rev_rev = self._reverse_phase(phase_rev)

            # 验证1: 反向 = -原始
            check1 = all(
                abs(pr + p) < 1e-10
                for p, pr in zip(phase, phase_rev)
            )

            # 验证2: 二次反转 = 原始
            check2 = all(
                abs(pr2 - p) < 1e-10
                for p, pr2 in zip(phase, phase_rev_rev)
            )

            passed = check1 and check2
            all_pass = all_pass and passed
            details.append({
                "signal_idx": idx,
                "reverse_equals_neg": check1,
                "double_reverse_identity": check2,
                "passed": passed,
            })

        return {
            "theorem": "T126",
            "verified": all_pass,
            "detail": "相位反转定理：phi->-phi, 二次反转恢复",
            "test_results": details,
        }

    def api_convolve(self, signal: List[float],
                     kernel: List[float]
                     ) -> Dict[str, Any]:
        """API辅助方法"""
        res = self.reverse_phase_convolve(signal, kernel)
        state = self.get_state()
        return {
            "api": "M159/reverse_phase_convolve",
            "result": res["result"],
            "metadata": res["metadata"],
            "state": state,
        }


def get_instance(direction: PhaseDirection = PhaseDirection.REVERSE,
                 liu_delta_s: float = 0.0
                 ) -> ReversePhaseConvolution:
    """模块级单例获取函数"""
    return ReversePhaseConvolution.get_instance(
        direction=direction, liu_delta_s=liu_delta_s
    )


if __name__ == "__main__":
    print("=" * 60)
    print("M159 反向相位卷积 — 自测")
    print("=" * 60)

    conv = ReversePhaseConvolution.get_instance()
    print(f"\n[状态] {conv.get_state()}")

    signal = [1.0, -2.0, 3.0, -1.0, 0.5]
    kernel = [0.5, 1.0, -0.5]

    print(f"\n输入信号: {signal}")
    print(f"卷积核: {kernel}")

    res = conv.reverse_phase_convolve(signal, kernel)
    print(f"\n反向相位卷积结果:")
    print(f"  result = {[round(v, 4) for v in res['result']]}")
    print(f"  metadata = {res['metadata']}")

    # 验证定理
    verification = conv.verify_theorem()
    print(f"\n定理T126验证: {verification['verified']}")
    for item in verification["test_results"]:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"  signal[{item['signal_idx']}]: "
              f"reverse=-orig={item['reverse_equals_neg']}, "
              f"double=identity={item['double_reverse_identity']} [{status}]")

    # API测试
    api_res = conv.api_convolve(signal, kernel)
    print(f"\nAPI调用结果长度: {len(api_res['result'])}")

    print("\n" + "=" * 60)
    print("M159 自测完成")
    print("=" * 60)
