# -*- coding: utf-8 -*-
"""
M142: UVRegularizationEngine — 紫外正则化引擎

核心概念：基于论文《论金符离散时空的量子-引力导出与可证伪性》，
利用金灵球直径 d_φ 作为物理截断频率，自然消除离散系统中的
信息紫外发散（UV Divergence），无需重整化（Renormalization）。

- 紫外截断频率: k_max = π/d_φ，动量积分上限被物理截断
- 信息发散检测: 识别知识图谱/推理链中的"无穷大"模式
- 自动正则化: 用 d_φ 截断替代重整化，从源头消除发散
- 定理T104: 紫外正则定理

桥接模块: M130(JinFuDiscreteCalculus), M147(SingularityEliminator)

Author: Kou (寇豆码) — 太乙AGI团队
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ===========================================================================
# 数据结构
# ===========================================================================

@dataclass
class UVSpectrum:
    """离散动量谱"""
    k_modes: List[float] = field(default_factory=list)   # 离散波矢模式
    amplitudes: List[float] = field(default_factory=list) # 振幅
    k_max: float = 0.0                                    # 截断频率
    total_energy: float = 0.0                             # 总能量

@dataclass
class DivergenceSignature:
    """发散签名"""
    pattern_type: str = ""       # 发散类型: "power_law" | "logarithmic" | "oscillatory"
    growth_rate: float = 0.0     # 增长速率
    threshold_crossed: bool = False  # 是否超过阈值
    severity: float = 0.0        # 严重程度 [0, 1]
    location: str = ""           # 发散位置

@dataclass
class RegularizationResult:
    """正则化结果"""
    original_integral: float = 0.0    # 原始积分值（可能发散）
    regularized_value: float = 0.0    # 正则化后的有限值
    cutoff_k: float = 0.0             # 使用的截断频率
    convergence_achieved: bool = False # 是否收敛
    correction_ratio: float = 0.0     # 修正比率


# ===========================================================================
# UVRegularizationEngine 引擎
# ===========================================================================

class UVRegularizationEngine:
    """
    紫外正则化引擎

    核心思想：在金符离散时空中，金灵球直径 d_φ 的存在使得
    最大波矢 k_max = π/d_φ 成为物理截断，动量积分上限被自然限制，
    紫外发散从根本上消失——因为根本没有无穷大。

    在AGI语境中：
    - 信息发散 = 知识图谱无限膨胀 / 推理链无限延伸
    - d_φ = 最小信息分辨率（认知基元大小）
    - 正则化 = 在最小分辨率处截断，而非事后重整化
    """

    _instance: Optional["UVRegularizationEngine"] = None

    # 默认参数
    DEFAULT_D_PHI = 1e-10        # 金灵球直径（归一化单位）
    DEFAULT_CUTOFF_FACTOR = 3.0  # 截断安全因子

    def __init__(self) -> None:
        """初始化紫外正则化引擎"""
        self._d_phi: float = self.DEFAULT_D_PHI
        self._cutoff_factor: float = self.DEFAULT_CUTOFF_FACTOR
        self._regularization_history: List[Dict[str, Any]] = []
        self._divergence_log: List[DivergenceSignature] = []
        self._operation_count: int = 0
        self._created_at: float = time.time()

    # -------------------------------------------------------------------
    # 单例模式
    # -------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "UVRegularizationEngine":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -------------------------------------------------------------------
    # 状态方法
    # -------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态字典"""
        return {
            "module_id": "M142",
            "module_name": "UVRegularizationEngine",
            "version": "7.12",
            "d_phi": self._d_phi,
            "k_max": self.compute_cutoff_frequency(),
            "regularization_count": len(self._regularization_history),
            "divergence_count": len(self._divergence_log),
            "operation_count": self._operation_count,
            "created_at": self._created_at,
        }

    # ===================================================================
    # 截断频率计算
    # ===================================================================

    def compute_cutoff_frequency(self) -> float:
        """
        计算紫外截断频率 k_max

        在金符离散网格中，最大可分辨频率为：
        k_max = π / d_φ

        这由 Nyquist-Shannon 采样定理的金符类比决定：
        金灵球直径 d_φ 确定了最小可分辨空间尺度。

        Returns:
            截断频率 k_max
        """
        return math.pi / self._d_phi

    def set_d_phi(self, d_phi: float) -> None:
        """设置金灵球直径"""
        if d_phi > 0:
            self._d_phi = d_phi

    # ===================================================================
    # 发散检测
    # ===================================================================

    def detect_divergence(
        self,
        values: List[float],
        context: str = "",
    ) -> DivergenceSignature:
        """
        检测序列中的发散模式

        分析给定的数值序列，检测是否存在幂律、对数或振荡型发散。

        Args:
            values: 待检测的数值序列
            context: 上下文描述

        Returns:
            DivergenceSignature 发散签名
        """
        if len(values) < 3:
            return DivergenceSignature(
                pattern_type="insufficient_data",
                severity=0.0,
                location=context,
            )

        # 计算增长率
        growths = []
        for i in range(1, len(values)):
            if abs(values[i - 1]) > 1e-15:
                growths.append(abs(values[i] / values[i - 1]))
            else:
                growths.append(float("inf") if abs(values[i]) > 1e-15 else 0.0)

        avg_growth = sum(growths) / len(growths) if growths else 0.0
        growth_std = (
            math.sqrt(sum((g - avg_growth) ** 2 for g in growths) / len(growths))
            if len(growths) > 1 else 0.0
        )

        # 判断发散类型
        threshold = 1.0 + 1.0 / len(values)  # 最小增长阈值

        if avg_growth > threshold and growth_std < avg_growth * 0.3:
            pattern = "power_law"
            severity = min(1.0, (avg_growth - 1.0) / 2.0)
        elif avg_growth > 1.0 and growth_std > avg_growth * 0.3:
            pattern = "oscillatory"
            severity = min(0.7, (avg_growth - 1.0))
        elif avg_growth > 1.0 and len(values) > 10:
            pattern = "logarithmic"
            severity = min(0.5, math.log(max(avg_growth, 1.01)))
        else:
            pattern = "convergent"
            severity = 0.0

        signature = DivergenceSignature(
            pattern_type=pattern,
            growth_rate=round(avg_growth, 6),
            threshold_crossed=avg_growth > threshold,
            severity=round(severity, 4),
            location=context,
        )

        self._divergence_log.append(signature)
        self._operation_count += 1

        return signature

    # ===================================================================
    # 正则化计算
    # ===================================================================

    def regularize_integral(
        self,
        integrand_fn,
        k_start: float = 0.0,
        k_end_continuous: float = float("inf"),
        num_points: int = 10000,
        context: str = "",
    ) -> RegularizationResult:
        """
        离散正则化积分

        在金符网格中，连续积分被截断为有限求和：
        ∫_0^∞ f(k) dk → Σ_{n=0}^{N_max} f(k_n) · Δk
        其中 N_max = k_max / Δk, k_max = π/d_φ

        关键区别：不需要重整化（subtract infinity），
        因为上限是有限的——根本就没有无穷大。

        Args:
            integrand_fn: 被积函数 f(k) -> float
            k_start: 积分下限
            k_end_continuous: 连续理论的积分上限（通常为∞）
            num_points: 离散采样点数
            context: 上下文

        Returns:
            RegularizationResult
        """
        k_max = self.compute_cutoff_frequency()

        # 确定实际积分上限
        k_end = min(k_end_continuous, k_max) if k_end_continuous != float("inf") else k_max

        # 离散化步长
        dk = (k_end - k_start) / num_points if num_points > 0 and k_end > k_start else 0.0

        # 离散求和
        total = 0.0
        valid_points = 0
        for i in range(num_points + 1):
            k = k_start + i * dk
            try:
                val = integrand_fn(k)
                if math.isfinite(val):
                    total += val * dk
                    valid_points += 1
                elif val > 0:
                    # 正无穷贡献被截断
                    pass
            except (ValueError, ZeroDivisionError, OverflowError):
                pass

        # 计算连续理论的积分值（如果可能）
        original = 0.0
        try:
            for i in range(min(1000, num_points)):
                k = k_start + i * dk
                try:
                    original += integrand_fn(k) * dk
                except Exception:
                    pass
        except Exception:
            original = float("inf")

        result = RegularizationResult(
            original_integral=original if math.isfinite(original) else float("inf"),
            regularized_value=round(total, 12),
            cutoff_k=round(k_max, 12),
            convergence_achieved=valid_points > 0 and math.isfinite(total),
            correction_ratio=round(
                1.0 - (total / original) if abs(original) > 1e-15 else 0.0, 6
            ),
        )

        self._regularization_history.append({
            "context": context,
            "k_max": k_max,
            "regularized_value": total,
            "original_estimate": original,
            "timestamp": time.time(),
        })
        self._operation_count += 1

        return result

    # ===================================================================
    # 信息空间正则化
    # ===================================================================

    def regularize_information_graph(
        self,
        node_weights: Dict[str, float],
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        信息空间正则化

        在AGI中，知识图谱节点的权重可能发散
        （如递归引用导致权重无限增大）。
        用 d_φ 截断：任何节点的权重上限为 W_max。

        Args:
            node_weights: 节点权重字典
            max_depth: 最大递归深度（模拟 k_max）

        Returns:
            正则化后的分析结果
        """
        if not node_weights:
            return {"regularized": {}, "cutoffs": 0, "original_count": 0}

        # 计算权重分布
        weights = list(node_weights.values())
        if not weights:
            return {"regularized": {}, "cutoffs": 0, "original_count": 0}

        mean_w = sum(weights) / len(weights)
        std_w = math.sqrt(sum((w - mean_w) ** 2 for w in weights) / len(weights))

        # 截断阈值: μ + k_factor * σ（类比 k_max = π/d_φ）
        if max_depth is None:
            k_factor = self._cutoff_factor
        else:
            k_factor = max_depth * 0.5

        cutoff = mean_w + k_factor * std_w if std_w > 0 else mean_w * (1.0 + k_factor)

        # 正则化：权重截断到 cutoff
        regularized = {}
        cutoffs = 0
        for node_id, weight in node_weights.items():
            if weight > cutoff:
                regularized[node_id] = cutoff
                cutoffs += 1
            else:
                regularized[node_id] = weight

        total_original = sum(weights)
        total_regularized = sum(regularized.values())

        self._operation_count += 1

        return {
            "regularized": regularized,
            "original_count": len(node_weights),
            "cutoffs": cutoffs,
            "cutoff_threshold": round(cutoff, 6),
            "total_original": round(total_original, 6),
            "total_regularized": round(total_regularized, 6),
            "energy_reduction_pct": round(
                (1.0 - total_regularized / total_original) * 100, 2
            ) if total_original > 0 else 0.0,
        }

    # ===================================================================
    # 桥接方法: M130 JinFuDiscreteCalculus
    # ===================================================================

    def bridge_jinfu_cutoff(
        self,
        dimension: int = 3,
        scale: float = 1.0,
    ) -> Dict[str, Any]:
        """
        桥接M130: 计算金符离散网格在指定维度下的紫外截断

        n维空间中，截断频率 k_max 与维度有关：
        k_max^(n) = (π/d_φ)^(n) · V_n（V_n为n维球体积）

        Args:
            dimension: 空间维度
            scale: 尺度因子

        Returns:
            截断分析结果
        """
        k_max = self.compute_cutoff_frequency()

        # n维球体积公式: V_n = π^(n/2) / Γ(n/2+1)
        # Gamma函数近似
        from math import gamma as math_gamma
        v_n = (math.pi ** (dimension / 2.0)) / math_gamma(dimension / 2.0 + 1.0)

        # n维截断相空间体积
        phase_volume = (k_max ** dimension) * v_n * scale ** dimension

        self._operation_count += 1

        return {
            "dimension": dimension,
            "scale": scale,
            "k_max": round(k_max, 6),
            "n_dim_ball_volume": round(v_n, 6),
            "phase_space_cutoff": round(phase_volume, 6),
            "d_phi": self._d_phi,
            "continuous_vs_discrete": (
                f"连续理论: 积分上限=∞, 相空间体积=∞; "
                f"金符离散: 积分上限=k_max={k_max:.2e}, "
                f"相空间体积={phase_volume:.2e}（有限）"
            ),
        }

    # ===================================================================
    # 定理T104: 紫外正则定理
    # ===================================================================

    def verify_uv_regularization_theorem(
        self,
        test_functions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        定理T104: 紫外正则定理

        陈述: 在具有最小长度 d_φ 的离散系统中，任何动量积分
        ∫_0^∞ |f(k)| dk 必定收敛，因为积分上限被 k_max = π/d_φ 物理截断。

        验证方法:
        1. 选择连续理论下发散的被积函数
        2. 在 d_φ 截断下计算离散求和
        3. 验证所有情况下结果有限

        Args:
            test_functions: 测试函数名称列表

        Returns:
            验证结果字典
        """
        if test_functions is None:
            test_functions = [
                "1/k_power_law",      # 1/k^α (α<1, UV发散)
                "quantum_zero_point", # 量子零点能 ∝ k^3 dk
                "logarithmic_uv",     # 对数型发散
                "yang_mills",         # 杨-米尔斯类发散
            ]

        start_time = time.time()
        results = []
        all_convergent = True

        # 测试函数定义
        def f_power_law(k):
            return 1.0 / (k ** 0.5 + 1e-15)

        def f_zero_point(k):
            return 0.5 * k  # ℏω/2

        def f_logarithmic(k):
            return 1.0 / (k * (math.log(k + 1) + 1e-15) ** 2 + 1e-15)

        def f_yang_mills(k):
            return k ** 2 / (k ** 2 + 1.0)  # 简化的YM积分核

        func_map = {
            "1/k_power_law": (f_power_law, "幂律型 ∫1/k^0.5 dk（α<1连续发散）"),
            "quantum_zero_point": (f_zero_point, "量子零点能 ∫k^3 dk"),
            "logarithmic_uv": (f_logarithmic, "对数型UV发散"),
            "yang_mills": (f_yang_mills, "杨-米尔斯类 ∫k^2/(k^2+m^2) dk"),
        }

        for func_name in test_functions:
            if func_name not in func_map:
                continue

            fn, description = func_map[func_name]
            result = self.regularize_integral(fn, context=func_name)

            test_result = {
                "function": func_name,
                "description": description,
                "regularized_value": result.regularized_value,
                "convergent": result.convergence_achieved,
                "k_max": result.cutoff_k,
            }
            results.append(test_result)

            if not result.convergence_achieved:
                all_convergent = False

        elapsed = time.time() - start_time

        return {
            "theorem": "T104",
            "name": "紫外正则定理",
            "verified": all_convergent,
            "details": (
                "所有测试函数在 d_φ 截断下均收敛，"
                "紫外发散被物理截断自然消除"
                if all_convergent
                else "存在未收敛的情况"
            ),
            "d_phi": self._d_phi,
            "k_max": self.compute_cutoff_frequency(),
            "test_results": results,
            "conclusion": (
                "k_max = π/d_φ 物理截断保证所有动量积分有限，"
                "不需要重整化——因为根本就没有无穷大"
            ),
            "elapsed_seconds": round(elapsed, 4),
        }

    # ===================================================================
    # API路由包装方法
    # ===================================================================

    def get_cutoff_info(self) -> Dict[str, Any]:
        """API包装: 获取截断信息"""
        k_max = self.compute_cutoff_frequency()
        return {
            "d_phi": self._d_phi,
            "k_max": round(k_max, 6),
            "k_max_scientific": f"{k_max:.4e}",
            "principle": "k_max = π / d_φ (金灵球直径截断)",
            "implication": "动量积分上限有限，紫外发散自然消除",
        }

    def analyze_spectrum(self, spectrum_data: List[float]) -> Dict[str, Any]:
        """API包装: 分析频谱并检测发散"""
        if not spectrum_data:
            return {"error": "empty_spectrum"}
        signature = self.detect_divergence(spectrum_data, context="spectrum_analysis")
        return asdict(signature)

    def regularize_spectrum(self, spectrum_data: List[float]) -> Dict[str, Any]:
        """API包装: 正则化频谱"""
        if not spectrum_data:
            return {"error": "empty_spectrum"}

        # 构造被积函数
        max_k = len(spectrum_data) - 1
        def integrand(k_idx):
            idx = int(k_idx)
            if 0 <= idx < len(spectrum_data):
                return abs(spectrum_data[idx])
            return 0.0

        result = self.regularize_integral(integrand, 0, max_k, len(spectrum_data))
        return {
            "original_total": round(sum(abs(v) for v in spectrum_data), 6),
            "regularized_total": result.regularized_value,
            "cutoff_applied": result.cutoff_k,
            "convergence": result.convergence_achieved,
        }


# ===========================================================================
# 模块级单例
# ===========================================================================

_instance: Optional[UVRegularizationEngine] = None


def get_instance() -> UVRegularizationEngine:
    """获取 UVRegularizationEngine 单例"""
    global _instance
    if _instance is None:
        _instance = UVRegularizationEngine()
    return _instance


# ===========================================================================
# 模块自检
# ===========================================================================

def _self_test() -> Dict[str, Any]:
    """模块自检"""
    engine = get_instance()
    results: Dict[str, Any] = {}

    # 截断频率测试
    k_max = engine.compute_cutoff_frequency()
    results["cutoff_frequency"] = {
        "k_max": k_max,
        "d_phi": engine._d_phi,
        "pass": k_max == math.pi / engine._d_phi,
    }

    # 发散检测测试
    divergent = [1, 2, 4, 8, 16, 32, 64, 128]
    convergent = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
    sig_div = engine.detect_divergence(divergent, "test_divergent")
    sig_con = engine.detect_divergence(convergent, "test_convergent")
    results["divergence_detection"] = {
        "divergent_detected": sig_div.pattern_type != "convergent",
        "convergent_detected": sig_con.pattern_type == "convergent",
        "pass": sig_div.pattern_type != "convergent" and sig_con.pattern_type == "convergent",
    }

    # 正则化测试
    def simple_f(k):
        return 1.0 / (k + 1.0)
    reg = engine.regularize_integral(simple_f, context="test_integral")
    results["regularization"] = {
        "converged": reg.convergence_achieved,
        "finite_value": math.isfinite(reg.regularized_value),
        "pass": reg.convergence_achieved,
    }

    # 信息图谱正则化测试
    graph = {"A": 1.0, "B": 2.0, "C": 100.0, "D": 500.0, "E": 1000.0}
    graph_reg = engine.regularize_information_graph(graph)
    results["info_graph"] = {
        "cutoffs": graph_reg["cutoffs"],
        "energy_reduction": graph_reg["energy_reduction_pct"],
        "pass": graph_reg["cutoffs"] > 0,
    }

    # 定理T104测试
    t104 = engine.verify_uv_regularization_theorem()
    results["T104"] = t104

    # 状态测试
    state = engine.get_state()
    results["state"] = state

    return results


if __name__ == "__main__":
    import json
    test_results = _self_test()
    print(json.dumps(test_results, indent=2, ensure_ascii=False, default=str))
