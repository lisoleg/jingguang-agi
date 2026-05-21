"""
M158 相位-模长对偶卷积 — PhaseModulusDualConvolution
====================================================
论文来源：六元对偶卷积架构，方程Eq2，定理T2.2
核心定理：T125（EML分解定理）— 特征与核分解为EML算子形式 f = |f|*e^{i*phi}
对偶轴：标量值 <-> 关系矢量（模长+相位）
与M117(Ftel)桥接：EML算子 f = Ftel * e^{i*phi}
"""

from __future__ import annotations

import math
import random
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class EMLMode(Enum):
    """EML分解模式"""
    FULL = "full"           # 完整模长+相位分解
    MODULUS_ONLY = "modulus"  # 仅模长
    PHASE_ONLY = "phase"    # 仅相位


@dataclass
class PhaseModulusState:
    """相位-模长对偶卷积状态"""
    mode: EMLMode = EMLMode.FULL
    ftel_base: float = 1.0  # M117 Ftel桥接基准
    total_convolutions: int = 0
    last_signal_length: int = 0
    last_kernel_length: int = 0
    phase_range: Tuple[float, float] = (-math.pi, math.pi)
    created_at: float = field(default_factory=time.time)


class PhaseModulusDualConvolution:
    """
    相位-模长对偶卷积 (Eq2/T2.2)

    定理T125：EML分解定理
    任何实值信号 f 可以分解为 EML 算子形式:
        f = |f| * e^{i*phi}
    其中 |f| 为模长（标量值），phi 为相位（关系矢量）。

    卷积在EML分解下:
        (f * g)(t) = (|f| * |g|)(t) * e^{i*(phi_f + phi_g)(t)}

    与M117(Ftel)桥接: f = Ftel * e^{i*phi}
    """

    _instance: Optional[PhaseModulusDualConvolution] = None

    def __init__(self, mode: EMLMode = EMLMode.FULL,
                 ftel_base: float = 1.0) -> None:
        self._state = PhaseModulusState(mode=mode, ftel_base=ftel_base)
        self._ftel_base = ftel_base

    @classmethod
    def get_instance(cls, mode: EMLMode = EMLMode.FULL,
                     ftel_base: float = 1.0
                     ) -> PhaseModulusDualConvolution:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(mode=mode, ftel_base=ftel_base)
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """重置单例（仅测试用）"""
        cls._instance = None

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "module": "M158_PhaseModulusDualConvolution",
            "mode": self._state.mode.value,
            "ftel_base": self._state.ftel_base,
            "total_convolutions": self._state.total_convolutions,
            "last_signal_length": self._state.last_signal_length,
            "last_kernel_length": self._state.last_kernel_length,
            "phase_range": list(self._state.phase_range),
            "created_at": self._state.created_at,
        }

    def _eml_decompose(self, signal: List[float]
                       ) -> Tuple[List[float], List[float]]:
        """
        EML分解：将实信号分解为模长和相位

        f = |f| * e^{i*phi}
        |f| = abs(f)
        phi = 0 (正数) 或 pi (负数)

        与M117(Ftel)桥接: Ftel = |f| / ftel_base
        """
        moduli: List[float] = []
        phases: List[float] = []
        for val in signal:
            modulus = abs(val) * self._ftel_base
            if abs(val) < 1e-12:
                phase = 0.0
            elif val > 0:
                phase = 0.0
            else:
                phase = math.pi
            moduli.append(modulus)
            phases.append(phase)
        return moduli, phases

    def _eml_reconstruct(self, moduli: List[float],
                         phases: List[float]
                         ) -> List[float]:
        """
        从模长和相位重构信号

        f = |f| * e^{i*phi} 的实部 = |f| * cos(phi)
        """
        result: List[float] = []
        for m, p in zip(moduli, phases):
            val = m * math.cos(p)
            result.append(val)
        return result

    def _simple_convolve(self, a: List[float],
                         b: List[float]) -> List[float]:
        """标准离散卷积"""
        n = len(a)
        m = len(b)
        output: List[float] = []
        for t in range(n + m - 1):
            acc = 0.0
            for i in range(m):
                a_idx = t - i
                if 0 <= a_idx < n:
                    acc += a[a_idx] * b[i]
            output.append(acc)
        return output

    def eml_convolve(self, signal: List[float],
                     kernel: List[float]
                     ) -> Dict[str, Any]:
        """
        相位-模长对偶卷积 (Eq2)

        定理T125：EML分解定理
        1. 分解: f = |f|*e^{i*phi_f}, g = |g|*e^{i*phi_g}
        2. 模长卷积: |f| * |g|
        3. 相位卷积: phi_f + phi_g (按卷积索引求和)
        4. 重构: result = (|f|*|g|) * e^{i*(phi_f+phi_g)}

        Args:
            signal: 输入信号序列
            kernel: 卷积核序列

        Returns:
            包含result和metadata的字典
        """
        if len(signal) == 0 or len(kernel) == 0:
            return {"result": [], "metadata": {"error": "空输入"}}

        # EML分解
        sig_mod, sig_phase = self._eml_decompose(signal)
        ker_mod, ker_phase = self._eml_decompose(kernel)

        # 模长卷积
        modulus_conv = self._simple_convolve(sig_mod, ker_mod)

        # 相位卷积（加权平均）
        phase_conv = self._simple_convolve(sig_phase, ker_phase)

        # 重构
        output_length = min(len(modulus_conv), len(phase_conv))
        result: List[float] = []
        for i in range(output_length):
            if abs(modulus_conv[i]) < 1e-12:
                result.append(0.0)
            else:
                val = modulus_conv[i] * math.cos(phase_conv[i])
                result.append(val)

        self._state.total_convolutions += 1
        self._state.last_signal_length = len(signal)
        self._state.last_kernel_length = len(kernel)

        metadata = {
            "theorem": "T125",
            "equation": "Eq2",
            "eml_mode": self._state.mode.value,
            "ftel_base": self._ftel_base,
            "signal_modulus": [round(v, 4) for v in sig_mod[:5]],
            "signal_phase": [round(v, 4) for v in sig_phase[:5]],
            "kernel_modulus": [round(v, 4) for v in ker_mod[:5]],
            "kernel_phase": [round(v, 4) for v in ker_phase[:5]],
            "output_length": output_length,
        }
        return {"result": result, "metadata": metadata}

    def verify_theorem(self) -> Dict[str, Any]:
        """
        验证定理T125：EML分解定理

        验证：f = EML_reconstruct(EML_decompose(f))
        即分解后重构应恢复原信号
        """
        test_signals = [
            [1.0, -2.0, 3.0, -0.5, 2.0],
            [0.0, 1.0, 0.0, -1.0, 0.0],
            [3.14, -1.57, 6.28, 0.0, -3.14],
        ]

        all_pass = True
        details = []
        for idx, sig in enumerate(test_signals):
            moduli, phases = self._eml_decompose(sig)
            reconstructed = self._eml_reconstruct(moduli, phases)
            max_err = max(abs(a - b) for a, b in zip(sig, reconstructed))
            passed = max_err < 1e-6
            all_pass = all_pass and passed
            details.append({
                "signal_idx": idx,
                "max_error": max_err,
                "passed": passed,
            })

        return {
            "theorem": "T125",
            "verified": all_pass,
            "detail": "EML分解定理：分解->重构恢复原信号",
            "test_results": details,
        }

    def api_convolve(self, signal: List[float],
                     kernel: List[float]
                     ) -> Dict[str, Any]:
        """API辅助方法"""
        res = self.eml_convolve(signal, kernel)
        state = self.get_state()
        return {
            "api": "M158/eml_convolve",
            "result": res["result"],
            "metadata": res["metadata"],
            "state": state,
        }


def get_instance(mode: EMLMode = EMLMode.FULL,
                 ftel_base: float = 1.0
                 ) -> PhaseModulusDualConvolution:
    """模块级单例获取函数"""
    return PhaseModulusDualConvolution.get_instance(
        mode=mode, ftel_base=ftel_base
    )


if __name__ == "__main__":
    print("=" * 60)
    print("M158 相位-模长对偶卷积 — 自测")
    print("=" * 60)

    conv = PhaseModulusDualConvolution.get_instance()
    print(f"\n[状态] {conv.get_state()}")

    signal = [1.0, -2.0, 3.0, -1.0, 0.5]
    kernel = [0.5, 1.0, -0.5]

    print(f"\n输入信号: {signal}")
    print(f"卷积核: {kernel}")

    res = conv.eml_convolve(signal, kernel)
    print(f"\nEML对偶卷积结果:")
    print(f"  result = {[round(v, 4) for v in res['result']]}")
    print(f"  metadata = {res['metadata']}")

    # 验证定理
    verification = conv.verify_theorem()
    print(f"\n定理T125验证: {verification['verified']}")
    for item in verification["test_results"]:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"  signal[{item['signal_idx']}]: "
              f"max_error={item['max_error']:.8f} [{status}]")

    # API测试
    api_res = conv.api_convolve(signal, kernel)
    print(f"\nAPI调用结果长度: {len(api_res['result'])}")

    print("\n" + "=" * 60)
    print("M158 自测完成")
    print("=" * 60)
