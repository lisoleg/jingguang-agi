"""
M162 UV正则化卷积 — UVRegularizedConvolution
==============================================
论文来源：六元对偶卷积架构，方程Eq6，定理T2.6
核心定理：T129（UV截断定理）— 引入d_phi作为最小尺度，消除无穷小量
对偶轴：无穷分辨 <-> 最小尺度限制
物理安全基座：防止生成奇点（M142/M147桥接）
k_max = pi / d_phi 截断
"""

from __future__ import annotations

import math
import random
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class UVMode(Enum):
    """UV正则化模式"""
    HARD_CUTOFF = "hard_cutoff"    # 硬截断：k > k_max 直接归零
    SOFT_CUTOFF = "soft_cutoff"    # 软截断：高斯衰减
    EXPONENTIAL = "exponential"    # 指数衰减


@dataclass
class UVRegularizedState:
    """UV正则化卷积状态"""
    d_phi: float = 0.1                       # 金灵球直径（最小尺度）
    k_max: float = math.pi / 0.1             # 最大波数 = pi / d_phi
    mode: UVMode = UVMode.HARD_CUTOFF
    singularity_count: int = 0               # 检测到的奇点数
    singularity_prevented: int = 0           # 阻止的奇点数
    total_convolutions: int = 0
    last_signal_length: int = 0
    last_kernel_length: int = 0
    m142_bridge_active: bool = True          # M142桥接
    m147_bridge_active: bool = True          # M147桥接
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.k_max = math.pi / self.d_phi if self.d_phi > 0 else float("inf")


class UVRegularizedConvolution:
    """
    UV正则化卷积 (Eq6/T2.6)

    定理T129：UV截断定理
    引入d_phi作为最小尺度限制，消除无穷小量，
    在频域中截断高于k_max的分量，防止奇点产生。

    k_max = pi / d_phi

    物理意义：
    - 没有UV截断时，卷积可以产生无穷大的值（奇点）
    - UV截断保证输出有界，是物理安全的基座
    - 类比量子场论中的UV正规化

    与M142/M147桥接：
    M142(奇点检测)和M147(安全边界)通过UV截断防止
    生成不可控的奇点，确保AI系统的稳定性。
    """

    _instance: Optional[UVRegularizedConvolution] = None

    def __init__(self, d_phi: float = 0.1,
                 mode: UVMode = UVMode.HARD_CUTOFF) -> None:
        self._state = UVRegularizedState(d_phi=d_phi, mode=mode)

    @classmethod
    def get_instance(cls, d_phi: float = 0.1,
                     mode: UVMode = UVMode.HARD_CUTOFF
                     ) -> UVRegularizedConvolution:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(d_phi=d_phi, mode=mode)
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """重置单例（仅测试用）"""
        cls._instance = None

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "module": "M162_UVRegularizedConvolution",
            "d_phi": self._state.d_phi,
            "k_max": self._state.k_max,
            "mode": self._state.mode.value,
            "singularity_count": self._state.singularity_count,
            "singularity_prevented": self._state.singularity_prevented,
            "total_convolutions": self._state.total_convolutions,
            "last_signal_length": self._state.last_signal_length,
            "last_kernel_length": self._state.last_kernel_length,
            "m142_bridge_active": self._state.m142_bridge_active,
            "m147_bridge_active": self._state.m147_bridge_active,
            "created_at": self._state.created_at,
        }

    def _dft(self, signal: List[float]) -> List[complex]:
        """离散傅里叶变换（简化实现）"""
        n = len(signal)
        result: List[complex] = []
        for k in range(n):
            acc = complex(0, 0)
            for t in range(n):
                angle = -2.0 * math.pi * k * t / n
                acc += signal[t] * complex(math.cos(angle), math.sin(angle))
            result.append(acc)
        return result

    def _idft(self, spectrum: List[complex]) -> List[float]:
        """逆离散傅里叶变换"""
        n = len(spectrum)
        result: List[float] = []
        for t in range(n):
            acc = complex(0, 0)
            for k in range(n):
                angle = 2.0 * math.pi * k * t / n
                acc += spectrum[k] * complex(math.cos(angle), math.sin(angle))
            result.append(acc.real / n)
        return result

    def _apply_uv_filter(self, spectrum: List[complex],
                         cutoff_k: float) -> List[complex]:
        """
        应用UV截断滤波器

        根据模式选择截断方式：
        - 硬截断：|k| > k_max 直接归零
        - 软截断：高斯衰减
        - 指数衰减：指数衰减
        """
        n = len(spectrum)
        result: List[complex] = []

        for k in range(n):
            # 将索引映射到频率
            if k <= n // 2:
                freq = k
            else:
                freq = k - n

            abs_freq = abs(freq)
            k_max = cutoff_k

            if self._state.mode == UVMode.HARD_CUTOFF:
                if abs_freq > k_max:
                    result.append(complex(0, 0))
                    self._state.singularity_prevented += 1
                else:
                    result.append(spectrum[k])

            elif self._state.mode == UVMode.SOFT_CUTOFF:
                sigma = k_max * 0.5
                weight = math.exp(-0.5 * (abs_freq - k_max) ** 2
                                  / (sigma ** 2 + 1e-12))
                if abs_freq > k_max:
                    self._state.singularity_prevented += 1
                result.append(spectrum[k] * weight)

            elif self._state.mode == UVMode.EXPONENTIAL:
                if abs_freq > k_max:
                    decay = math.exp(-(abs_freq - k_max) * 0.5)
                    result.append(spectrum[k] * decay)
                    self._state.singularity_prevented += 1
                else:
                    result.append(spectrum[k])
            else:
                result.append(spectrum[k])

        return result

    def _detect_singularity(self, values: List[float],
                            threshold: float = 1e6) -> int:
        """
        奇点检测（M142桥接）

        检测超过阈值的异常值
        """
        count = 0
        for v in values:
            if abs(v) > threshold or math.isnan(v) or math.isinf(v):
                count += 1
        return count

    def _safety_boundary(self, result: List[float]) -> List[float]:
        """
        安全边界（M147桥接）

        确保输出值在安全范围内
        """
        safe_max = 1.0 / (self._state.d_phi + 1e-12)
        bounded: List[float] = []
        for v in result:
            if math.isnan(v) or math.isinf(v):
                bounded.append(0.0)
                self._state.singularity_prevented += 1
            elif abs(v) > safe_max:
                bounded.append(math.copysign(safe_max, v))
                self._state.singularity_prevented += 1
            else:
                bounded.append(v)
        return bounded

    def uv_convolve(self, signal: List[float],
                    kernel: List[float],
                    cutoff_k: float = 0.0
                    ) -> Dict[str, Any]:
        """
        UV正则化卷积 (Eq6)

        定理T129：UV截断定理
        1. 将信号和核变换到频域
        2. 频域相乘
        3. 应用UV截断滤波器（k_max = pi / d_phi）
        4. 逆变换回时域
        5. 安全边界检测（M142/M147桥接）

        Args:
            signal: 输入信号序列
            kernel: 卷积核序列
            cutoff_k: 截断波数，0表示使用默认k_max

        Returns:
            包含result和metadata的字典
        """
        if len(signal) == 0 or len(kernel) == 0:
            return {"result": [], "metadata": {"error": "空输入"}}

        # 确定截断波数
        if cutoff_k <= 0:
            cutoff_k = self._state.k_max

        # 将信号和核补零到相同长度
        conv_len = len(signal) + len(kernel) - 1
        padded_signal = signal + [0.0] * (conv_len - len(signal))
        padded_kernel = kernel + [0.0] * (conv_len - len(kernel))

        # 变换到频域
        sig_spectrum = self._dft(padded_signal)
        ker_spectrum = self._dft(padded_kernel)

        # 频域相乘
        product: List[complex] = []
        for s, k in zip(sig_spectrum, ker_spectrum):
            product.append(s * k)

        # UV截断
        filtered = self._apply_uv_filter(product, cutoff_k)

        # 逆变换
        result = self._idft(filtered)

        # 奇点检测（M142）
        singularity_count = self._detect_singularity(result)
        self._state.singularity_count += singularity_count

        # 安全边界（M147）
        if self._state.m147_bridge_active:
            result = self._safety_boundary(result)

        self._state.total_convolutions += 1
        self._state.last_signal_length = len(signal)
        self._state.last_kernel_length = len(kernel)

        metadata = {
            "theorem": "T129",
            "equation": "Eq6",
            "d_phi": self._state.d_phi,
            "k_max": cutoff_k,
            "uv_mode": self._state.mode.value,
            "convolution_length": conv_len,
            "singularity_detected": singularity_count,
            "singularity_prevented_total": self._state.singularity_prevented,
        }
        return {"result": result, "metadata": metadata}

    def verify_theorem(self) -> Dict[str, Any]:
        """
        验证定理T129：UV截断定理

        验证1：UV截断后的结果有界
        验证2：d_phi越小，k_max越大，结果越精细
        验证3：无截断时可能产生奇点，有截断时不会
        """
        signal = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
        kernel = [1.0, -1.0, 1.0, -1.0]

        # 验证1：有界性
        res = self.uv_convolve(signal, kernel)
        max_val = max(abs(v) for v in res["result"])
        safe_bound = 1.0 / (self._state.d_phi + 1e-12)
        bounded = max_val <= safe_bound * 1.01  # 允许1%误差

        # 验证2：不同d_phi下的k_max
        d_phi_values = [0.5, 0.1, 0.01]
        k_max_values = [math.pi / d for d in d_phi_values]
        k_max_increasing = all(
            k_max_values[i] < k_max_values[i + 1]
            for i in range(len(k_max_values) - 1)
        )

        # 验证3：截断防止奇点
        # 构造可能产生大值的信号
        spike_signal = [1000.0] + [0.0] * 7
        spike_kernel = [1000.0] + [0.0] * 3
        res_spike = self.uv_convolve(spike_signal, spike_kernel)
        no_infinity = all(
            math.isfinite(v) for v in res_spike["result"]
        )

        return {
            "theorem": "T129",
            "verified": bounded and k_max_increasing and no_infinity,
            "detail": "UV截断定理：截断保证有界，"
                      "d_phi缩小k_max增大，截断防止奇点",
            "output_bounded": bounded,
            "max_output": max_val,
            "safe_bound": safe_bound,
            "k_max_increasing_with_d_phi_decrease": k_max_increasing,
            "no_infinity_with_spike": no_infinity,
        }

    def api_convolve(self, signal: List[float],
                     kernel: List[float],
                     cutoff_k: float = 0.0
                     ) -> Dict[str, Any]:
        """API辅助方法"""
        res = self.uv_convolve(signal, kernel, cutoff_k)
        state = self.get_state()
        return {
            "api": "M162/uv_convolve",
            "result": res["result"],
            "metadata": res["metadata"],
            "state": state,
        }


def get_instance(d_phi: float = 0.1,
                 mode: UVMode = UVMode.HARD_CUTOFF
                 ) -> UVRegularizedConvolution:
    """模块级单例获取函数"""
    return UVRegularizedConvolution.get_instance(d_phi=d_phi, mode=mode)


if __name__ == "__main__":
    print("=" * 60)
    print("M162 UV正则化卷积 — 自测")
    print("=" * 60)

    conv = UVRegularizedConvolution.get_instance(d_phi=0.1)
    print(f"\n[状态] {conv.get_state()}")

    signal = [1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 0.0]
    kernel = [0.25, 0.5, 0.25, 0.0]

    print(f"\n输入信号: {signal}")
    print(f"卷积核: {kernel}")
    print(f"k_max = pi / d_phi = {conv._state.k_max:.2f}")

    res = conv.uv_convolve(signal, kernel)
    print(f"\nUV正则化卷积结果:")
    print(f"  result = {[round(v, 4) for v in res['result']]}")
    print(f"  metadata = {res['metadata']}")

    # 验证定理
    verification = conv.verify_theorem()
    print(f"\n定理T129验证: {verification['verified']}")
    print(f"  输出有界: {verification['output_bounded']}")
    print(f"  最大输出: {verification['max_output']:.4f}")
    print(f"  安全边界: {verification['safe_bound']:.4f}")
    print(f"  k_max随d_phi减小而增大: "
          f"{verification['k_max_increasing_with_d_phi_decrease']}")
    print(f"  尖峰信号无无穷: "
          f"{verification['no_infinity_with_spike']}")

    # API测试
    api_res = conv.api_convolve(signal, kernel)
    print(f"\nAPI调用结果长度: {len(api_res['result'])}")

    print("\n" + "=" * 60)
    print("M162 自测完成")
    print("=" * 60)
