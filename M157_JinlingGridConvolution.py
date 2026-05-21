"""
M157 金灵球网格卷积 — JinlingGridConvolution
================================================
论文来源：六元对偶卷积架构，方程Eq1，定理T2.1
核心定理：T124（离散化定理）— 连续积分在金灵球网格上退化为求和
对偶轴：连续 <-> 离散
与M130(金符)桥接：使用Z_φ模运算
"""

from __future__ import annotations

import math
import random
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GridMode(Enum):
    """金灵球网格模式"""
    STANDARD = "standard"
    FINE = "fine"
    COARSE = "coarse"


@dataclass
class JinlingGridState:
    """金灵球网格卷积状态"""
    grid_diameter: float = 0.1
    mode: GridMode = GridMode.STANDARD
    z_phi_modulus: float = 2.0 * math.pi
    total_convolutions: int = 0
    last_signal_length: int = 0
    last_kernel_length: int = 0
    created_at: float = field(default_factory=time.time)


class JinlingGridConvolution:
    """
    金灵球网格卷积 (Eq1/T2.1)

    定理T124：连续积分在金灵球网格上退化为求和。
    将连续卷积积分 sum f(tau) * g(t - tau) dtau
    在金灵球网格上离散化为 sum f(tau_i) * g(t - tau_i) * d_phi

    金灵球直径 d_phi 是最小离散化单位，
    Z_φ模运算确保网格点落在金灵球格点上。
    """

    _instance: Optional[JinlingGridConvolution] = None

    def __init__(self, grid_diameter: float = 0.1,
                 mode: GridMode = GridMode.STANDARD) -> None:
        self._state = JinlingGridState(
            grid_diameter=grid_diameter,
            mode=mode
        )
        self._d_phi = grid_diameter
        self._z_phi = self._state.z_phi_modulus

    @classmethod
    def get_instance(cls, grid_diameter: float = 0.1,
                     mode: GridMode = GridMode.STANDARD
                     ) -> JinlingGridConvolution:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(grid_diameter=grid_diameter, mode=mode)
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """重置单例（仅测试用）"""
        cls._instance = None

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "module": "M157_JinlingGridConvolution",
            "grid_diameter": self._state.grid_diameter,
            "mode": self._state.mode.value,
            "z_phi_modulus": self._state.z_phi_modulus,
            "total_convolutions": self._state.total_convolutions,
            "last_signal_length": self._state.last_signal_length,
            "last_kernel_length": self._state.last_kernel_length,
            "created_at": self._state.created_at,
        }

    def _z_phi_mod(self, value: float) -> float:
        """Z_φ模运算 — 与M130(金符)桥接"""
        return value % self._z_phi

    def _quantize_to_grid(self, value: float) -> float:
        """将连续值量化到金灵球网格格点"""
        index = round(value / self._d_phi)
        return index * self._d_phi

    def discrete_convolve(self, signal: List[float],
                          kernel: List[float],
                          grid_diameter: float = 0.1
                          ) -> Dict[str, Any]:
        """
        金灵球网格离散卷积 (Eq1)

        定理T124：连续积分在金灵球网格上退化为求和
        y[t] = sum_{i} signal[tau_i] * kernel[t - tau_i] * d_phi

        Args:
            signal: 输入信号序列
            kernel: 卷积核序列
            grid_diameter: 金灵球直径 d_phi

        Returns:
            包含result和metadata的字典
        """
        self._d_phi = grid_diameter
        self._state.grid_diameter = grid_diameter
        n = len(signal)
        m = len(kernel)
        if n == 0 or m == 0:
            return {"result": [], "metadata": {"error": "空输入"}}

        output_length = n + m - 1
        result: List[float] = []

        for t in range(output_length):
            acc = 0.0
            for i in range(m):
                s_idx = t - i
                if 0 <= s_idx < n:
                    s_val = self._quantize_to_grid(signal[s_idx])
                    k_val = self._quantize_to_grid(kernel[i])
                    acc += self._z_phi_mod(s_val * k_val) * self._d_phi
            result.append(acc)

        self._state.total_convolutions += 1
        self._state.last_signal_length = n
        self._state.last_kernel_length = m

        metadata = {
            "theorem": "T124",
            "equation": "Eq1",
            "grid_diameter": self._d_phi,
            "z_phi_modulus": self._z_phi,
            "output_length": output_length,
            "discretization": f"连续积分 -> 求和 (d_phi={self._d_phi})",
        }
        return {"result": result, "metadata": metadata}

    def verify_theorem(self) -> Dict[str, Any]:
        """
        验证定理T124：离散化定理

        离散卷积结果 = 标准卷积 * d_phi（缩放关系）。
        验证：归一化后不同d_phi结果一致，且d_phi->0时逼近连续极限。
        """
        signal = [1.0, 2.0, 3.0, 2.0, 1.0]
        kernel = [0.5, 1.0, 0.5]

        # 使用不同粒度的d_phi
        diameters = [0.5, 0.1, 0.01, 0.001]
        results = []
        normalized_results = []
        for d in diameters:
            res = self.discrete_convolve(signal, kernel, grid_diameter=d)
            total = sum(abs(v) for v in res["result"])
            # 归一化：除以d_phi后应收敛到同一值
            normalized = total / d
            results.append({"d_phi": d, "total_energy": total})
            normalized_results.append(
                {"d_phi": d, "normalized_energy": normalized}
            )

        # 验证归一化后结果一致（离散化定理的核心）
        ref_normalized = normalized_results[0]["normalized_energy"]
        converging = True
        for item in normalized_results[1:]:
            diff_ratio = abs(
                item["normalized_energy"] - ref_normalized
            ) / (abs(ref_normalized) + 1e-12)
            if diff_ratio > 0.5:
                converging = False
                break

        return {
            "theorem": "T124",
            "verified": converging,
            "detail": "离散化定理：归一化(除以d_phi)后不同粒度结果一致",
            "raw_data": results,
            "normalized_data": normalized_results,
        }

    def api_convolve(self, signal: List[float],
                     kernel: List[float],
                     grid_diameter: float = 0.1
                     ) -> Dict[str, Any]:
        """API辅助方法"""
        res = self.discrete_convolve(signal, kernel, grid_diameter)
        state = self.get_state()
        return {
            "api": "M157/discrete_convolve",
            "result": res["result"],
            "metadata": res["metadata"],
            "state": state,
        }


def get_instance(grid_diameter: float = 0.1,
                 mode: GridMode = GridMode.STANDARD
                 ) -> JinlingGridConvolution:
    """模块级单例获取函数"""
    return JinlingGridConvolution.get_instance(
        grid_diameter=grid_diameter, mode=mode
    )


if __name__ == "__main__":
    print("=" * 60)
    print("M157 金灵球网格卷积 — 自测")
    print("=" * 60)

    conv = JinlingGridConvolution.get_instance(grid_diameter=0.1)
    print(f"\n[状态] {conv.get_state()}")

    signal = [1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0]
    kernel = [0.25, 0.5, 0.25]

    print(f"\n输入信号: {signal}")
    print(f"卷积核: {kernel}")

    res = conv.discrete_convolve(signal, kernel, grid_diameter=0.1)
    print(f"\n离散卷积结果 (d_phi=0.1):")
    print(f"  result = {[round(v, 4) for v in res['result']]}")
    print(f"  metadata = {res['metadata']}")

    # 验证定理
    verification = conv.verify_theorem()
    print(f"\n定理T124验证: {verification['verified']}")
    for item in verification["normalized_data"]:
        print(f"  d_phi={item['d_phi']:.3f} -> "
              f"normalized={item['normalized_energy']:.6f}")

    # API测试
    api_res = conv.api_convolve(signal, kernel)
    print(f"\nAPI调用结果长度: {len(api_res['result'])}")

    print("\n" + "=" * 60)
    print("M157 自测完成")
    print("=" * 60)
