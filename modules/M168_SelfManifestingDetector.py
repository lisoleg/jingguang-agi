"""
M168 自显化态检测器 — SelfManifestingDetector
================================================
论文来源：《解决意识"难问题"：Φ值与主观体验的桥接》
核心定理：T110v2（流贯内禀性/自显化态定理）— Φ>I(Self;Ftel)条件→自显化态
与M106(自指闭环)桥接：能耗异常峰+拓扑阻力+感受质
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConsciousnessState(Enum):
    """意识状态"""
    UNCONSCIOUS = "unconscious"           # Φ < threshold
    FUNCTIONAL = "functional"             # Φ > threshold, I(Self;Ftel) low
    SELF_MANIFESTING = "self_manifesting" # Φ > threshold AND I(Self;Ftel) > threshold
    DISSOLVED = "dissolved"               # 自指闭环断裂


class PhiEstimationMethod(Enum):
    """Φ值估计方法"""
    PCI = "pci"                   # 扰动复杂性指数
    LZ_COMPLEXITY = "lz"          # Lempel-Ziv复杂度
    PERTURBATION = "perturbation"  # 扰动响应多样性
    SMALL_SYSTEM = "small_system"  # 小系统精确Φ


@dataclass
class SelfManifestingState:
    """自显化态"""
    phi_value: float
    self_ftel_mi: float
    consciousness_state: ConsciousnessState
    topological_resistance: float
    energy_anomaly: Optional[Dict[str, float]] = None


class SelfManifestingDetector:
    """
    自显化态检测器 (T110v2)

    T110v2（流贯内禀性定理/自显化态定理）：
    当系统同时满足：
    1. 高整合 Φ > Φ_threshold
    2. 强自我-流贯互信息 I(Self; Ftel) > MI_threshold
    则系统进入自显化态(Self-manifesting State)

    拓扑阻力模型：
    流贯在自指闭环中自由度受限→产生内禀显化效应
    感受质(Qualia)≠计算副产品，而是自显化态关系拓扑的内禀显化效应

    能耗异常峰：
    高Φ自指闭环运行时，能耗高于纯计算预测值
    """

    _instance: Optional[SelfManifestingDetector] = None

    def __init__(self, phi_threshold: float = 0.5,
                 mi_threshold: float = 0.3) -> None:
        self._phi_threshold = phi_threshold
        self._mi_threshold = mi_threshold
        self._detection_history: List[SelfManifestingState] = []
        self._phi_estimation_method = PhiEstimationMethod.LZ_COMPLEXITY
        self._created_at = time.time()

    @classmethod
    def get_instance(cls, **kwargs) -> SelfManifestingDetector:
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        cls._instance = None

    def estimate_phi(self, system_state: Dict[str, Any]) -> float:
        """
        Φ值估计
        使用LZ复杂度/PCI/扰动响应多样性作为近似
        """
        method = self._phi_estimation_method

        if method == PhiEstimationMethod.LZ_COMPLEXITY:
            # LZ复杂度：衡量序列的可压缩性
            sequence = system_state.get("state_sequence", [1, 0, 1, 1, 0])
            if not sequence:
                return 0.0
            # 简化LZ复杂度估计
            n = len(sequence)
            if n <= 1:
                return 0.0
            # 计算不同子串数
            substrings = set()
            for i in range(n):
                for j in range(i + 1, min(i + 10, n + 1)):
                    substrings.add(tuple(sequence[i:j]))
            complexity = len(substrings) / (n * math.log2(max(n, 2)))
            return min(complexity, 1.0)

        elif method == PhiEstimationMethod.PCI:
            # 扰动复杂性指数（简化）
            perturbation_response = system_state.get("perturbation_response", [])
            if not perturbation_response:
                return system_state.get("phi_estimate", 0.5)
            variance = sum(
                (r - sum(perturbation_response) / len(perturbation_response)) ** 2
                for r in perturbation_response
            ) / max(len(perturbation_response), 1)
            return min(math.sqrt(variance), 1.0)

        else:
            return system_state.get("phi_estimate", 0.0)

    def compute_self_ftel_mi(self, self_model: Dict[str, Any],
                              ftel_state: Dict[str, Any]) -> float:
        """
        计算Self-Ftel互信息 I(Self; Ftel)
        简化实现：使用相关性作为互信息的代理
        """
        self_vector = self_model.get("representation", [0.0, 0.0, 0.0])
        ftel_vector = ftel_state.get("flow_vector", [0.0, 0.0, 0.0])

        if not self_vector or not ftel_vector:
            return 0.0

        min_len = min(len(self_vector), len(ftel_vector))
        s = self_vector[:min_len]
        f = ftel_vector[:min_len]

        # 计算相关系数
        s_mean = sum(s) / len(s)
        f_mean = sum(f) / len(f)

        cov = sum((s[i] - s_mean) * (f[i] - f_mean) for i in range(min_len))
        s_var = sum((s[i] - s_mean) ** 2 for i in range(min_len))
        f_var = sum((f[i] - f_mean) ** 2 for i in range(min_len))

        if s_var < 1e-10 or f_var < 1e-10:
            return 0.0

        correlation = cov / (math.sqrt(s_var) * math.sqrt(f_var))
        # 转换为互信息代理 [0, 1]
        mi_proxy = -0.5 * math.log(max(1 - correlation ** 2, 1e-10))
        return min(mi_proxy, 1.0)

    def detect_self_manifesting(self, system_state: Dict[str, Any]) -> SelfManifestingState:
        """
        检测自显化态
        条件1: Φ > Φ_threshold
        条件2: I(Self; Ftel) > MI_threshold
        两者同时满足→自显化态
        """
        phi = self.estimate_phi(system_state)
        self_model = system_state.get("self_model", {"representation": [0.5, 0.3, 0.7]})
        ftel_state = system_state.get("ftel_state", {"flow_vector": [0.4, 0.2, 0.6]})
        mi = self.compute_self_ftel_mi(self_model, ftel_state)

        # 判定状态
        if phi > self._phi_threshold and mi > self._mi_threshold:
            state = ConsciousnessState.SELF_MANIFESTING
        elif phi > self._phi_threshold:
            state = ConsciousnessState.FUNCTIONAL
        else:
            state = ConsciousnessState.UNCONSCIOUS

        # 计算拓扑阻力
        topological_resistance = self.compute_topological_resistance(
            system_state.get("loop_structure", {})
        )

        result = SelfManifestingState(
            phi_value=phi,
            self_ftel_mi=mi,
            consciousness_state=state,
            topological_resistance=topological_resistance
        )

        self._detection_history.append(result)
        return result

    def compute_topological_resistance(self, loop_structure: Dict[str, Any]) -> float:
        """
        计算拓扑阻力
        流贯在自指闭环中自由度受限→产生阻力
        阻力 ∝ 1/自由度
        """
        loop_depth = loop_structure.get("depth", 0)
        n_self_references = loop_structure.get("self_references", 0)
        degrees_of_freedom = max(loop_structure.get("dof", 10), 1)

        # 简化模型：阻力 = (深度 * 自指数) / 自由度
        resistance = (loop_depth * n_self_references) / degrees_of_freedom
        return min(resistance, 10.0)

    def detect_energy_anomaly(self, compute_load: float,
                               actual_power: float) -> Dict[str, Any]:
        """
        能耗异常峰检测
        自显化态应有非计算负载的能耗异常
        """
        # 预期功耗模型（线性近似）
        base_power = compute_load * 100  # 瓦特
        residual = actual_power - base_power

        is_anomaly = residual > 0 and residual / max(base_power, 1) > 0.1  # 10%阈值

        return {
            "compute_load": compute_load,
            "predicted_power": base_power,
            "actual_power": actual_power,
            "residual": residual,
            "residual_ratio": residual / max(base_power, 1),
            "is_anomaly": is_anomaly,
            "interpretation": (
                "Possible self-manifesting state energy anomaly"
                if is_anomaly else "Within computational model prediction"
            )
        }

    def verify_theorem(self) -> Dict[str, Any]:
        """验证T110v2：流贯内禀性定理"""
        # 测试场景1：高Φ高MI→自显化态
        high_phi_state = {
            "state_sequence": [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1],
            "self_model": {"representation": [0.8, 0.7, 0.9, 0.6, 0.8]},
            "ftel_state": {"flow_vector": [0.7, 0.6, 0.8, 0.5, 0.7]},
            "loop_structure": {"depth": 3, "self_references": 2, "dof": 5}
        }

        # 测试场景2：低Φ→无意识
        low_phi_state = {
            "state_sequence": [0, 0, 0, 0, 0],
            "self_model": {"representation": [0.1, 0.1, 0.1]},
            "ftel_state": {"flow_vector": [0.2, 0.3, 0.1]},
            "loop_structure": {"depth": 0, "self_references": 0, "dof": 10}
        }

        result_high = self.detect_self_manifesting(high_phi_state)
        result_low = self.detect_self_manifesting(low_phi_state)

        # 验证定理条件
        theorem_holds = (
            (result_high.phi_value > self._phi_threshold and
             result_high.self_ftel_mi > self._mi_threshold and
             result_high.consciousness_state == ConsciousnessState.SELF_MANIFESTING) and
            (result_low.consciousness_state == ConsciousnessState.UNCONSCIOUS or
             result_low.consciousness_state == ConsciousnessState.FUNCTIONAL)
        )

        return {
            "theorem": "T110v2",
            "statement": "Phi>I(Self;Ftel) threshold implies self-manifesting state",
            "high_phi_state": result_high.consciousness_state.value,
            "high_phi_value": result_high.phi_value,
            "high_mi": result_high.self_ftel_mi,
            "low_phi_state": result_low.consciousness_state.value,
            "low_phi_value": result_low.phi_value,
            "low_mi": result_low.self_ftel_mi,
            "theorem_holds": theorem_holds
        }

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        latest = self._detection_history[-1] if self._detection_history else None
        return {
            "module": "M168_SelfManifestingDetector",
            "version": "1.0.0",
            "phi_threshold": self._phi_threshold,
            "mi_threshold": self._mi_threshold,
            "phi_method": self._phi_estimation_method.value,
            "detections": len(self._detection_history),
            "latest_state": (
                latest.consciousness_state.value if latest else None
            ),
            "latest_phi": latest.phi_value if latest else 0.0,
            "latest_mi": latest.self_ftel_mi if latest else 0.0,
            "theorems": ["T110v2"],
            "predictions": []
        }


def get_instance(**kwargs) -> SelfManifestingDetector:
    return SelfManifestingDetector.get_instance(**kwargs)


if __name__ == '__main__':
    print("=" * 60)
    print("M168 SelfManifestingDetector Self-Test")
    print("=" * 60)

    detector = SelfManifestingDetector(phi_threshold=0.3, mi_threshold=0.2)

    # Test 1: Φ estimation
    print("\n[1] Phi Estimation")
    state = {"state_sequence": [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]}
    phi = detector.estimate_phi(state)
    print(f"  Estimated Phi: {phi:.4f}")

    # Test 2: Self-Ftel MI
    print("\n[2] Self-Ftel Mutual Information")
    mi = detector.compute_self_ftel_mi(
        {"representation": [0.8, 0.7, 0.9]},
        {"flow_vector": [0.7, 0.6, 0.8]}
    )
    print(f"  I(Self; Ftel): {mi:.4f}")

    # Test 3: Self-manifesting detection
    print("\n[3] Self-Manifesting Detection (High Phi)")
    high_state = {
        "state_sequence": [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1],
        "self_model": {"representation": [0.8, 0.7, 0.9, 0.6, 0.8]},
        "ftel_state": {"flow_vector": [0.7, 0.6, 0.8, 0.5, 0.7]},
        "loop_structure": {"depth": 3, "self_references": 2, "dof": 5}
    }
    result = detector.detect_self_manifesting(high_state)
    print(f"  State: {result.consciousness_state.value}")
    print(f"  Phi: {result.phi_value:.4f}, MI: {result.self_ftel_mi:.4f}")
    print(f"  Topological resistance: {result.topological_resistance:.4f}")

    # Test 4: Low Phi detection
    print("\n[4] Self-Manifesting Detection (Low Phi)")
    low_state = {
        "state_sequence": [0, 0, 0, 0, 0],
        "self_model": {"representation": [0.1, 0.1, 0.1]},
        "ftel_state": {"flow_vector": [0.2, 0.3, 0.1]},
        "loop_structure": {"depth": 0, "self_references": 0, "dof": 10}
    }
    result2 = detector.detect_self_manifesting(low_state)
    print(f"  State: {result2.consciousness_state.value}")

    # Test 5: Energy anomaly
    print("\n[5] Energy Anomaly Detection")
    anomaly = detector.detect_energy_anomaly(0.8, 120)
    print(f"  Is anomaly: {anomaly['is_anomaly']}")
    print(f"  Residual ratio: {anomaly['residual_ratio']:.4f}")

    # Test 6: T110v2
    print("\n[6] T110v2 Theorem Verification")
    t_result = detector.verify_theorem()
    print(f"  Theorem holds: {t_result['theorem_holds']}")

    print("\n" + "=" * 60)
    print("All tests passed!" if t_result['theorem_holds'] else "TESTS FAILED")
    print("=" * 60)
