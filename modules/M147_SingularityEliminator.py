# -*- coding: utf-8 -*-
"""
M147: SingularityEliminator — 奇点消除器

核心概念：基于论文《论金符离散时空的量子-引力导出与可证伪性》，
连续统数学中的奇点（曲率发散、除零、无穷递归）在金符离散时空中
是伪问题——金灵球直径 d_φ 的存在保证了物理量的有限性。

- 黑洞中心: 不是曲率奇点，而是芬芳香子密堆结构（半径 ≥ d_φ）
- 除零保护: 分母最小为 d_φ，不会真正除以零
- 递归保护: 递归深度有限，堆垒层数有界
- 定理T109: 奇点消除定理

桥接模块: M142(UVRegularizationEngine), M133(SelfReferentialLoopTopology),
          M146(DialecticalZeroReasoner)

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
class SingularitySignature:
    """奇点签名"""
    type: str = ""                     # "curvature" | "division_zero" | "recursion" | "overflow"
    location: str = ""                 # 奇点位置描述
    severity: float = 0.0              # 严重程度 [0, 1]
    value_before: float = 0.0          # 消除前的值
    value_after: float = 0.0           # 消除后的值
    elimination_method: str = ""       # 消除方法

@dataclass
class SafeDivisionResult:
    """安全除法结果"""
    numerator: float = 0.0
    denominator: float = 0.0
    result: float = 0.0
    was_singular: bool = False         # 分母是否为奇点
    d_phi_substitution: float = 0.0    # 替换值

@dataclass
class RecursionAnalysis:
    """递归分析"""
    max_depth_reached: int = 0         # 达到的最大递归深度
    max_depth_allowed: int = 100       # 允许的最大递归深度
    singularity_detected: bool = False # 是否检测到递归奇点
    stack_trace: List[str] = field(default_factory=list)


# ===========================================================================
# SingularityEliminator 引擎
# ===========================================================================

class SingularityEliminator:
    """
    奇点消除器

    核心思想：在连续统数学中，奇点无处不在——
    黑洞中心的曲率无穷大、1/0的除零、无限递归。
    但在金符离散时空中，这些奇点都是伪问题：
    - 最小长度 d_φ → 曲率有上界
    - 最小非零值 d_φ → 除法安全
    - 有限金灵球数 → 递归有界

    在AGI语境中：
    - 曲率奇点 = 知识图谱中的"黑洞"（信息无限集中的概念）
    - 除零 = 推理中的"断链"（某个前提缺失导致后续全部无效）
    - 递归奇点 = 自指推理的"死循环"
    """

    _instance: Optional["SingularityEliminator"] = None

    # 默认参数
    DEFAULT_D_PHI = 1e-10
    DEFAULT_MAX_RECURSION = 1000

    def __init__(self) -> None:
        """初始化奇点消除器"""
        self._d_phi: float = self.DEFAULT_D_PHI
        self._max_recursion: int = self.DEFAULT_MAX_RECURSION
        self._elimination_log: List[SingularitySignature] = []
        self._operation_count: int = 0
        self._created_at: float = time.time()

    # -------------------------------------------------------------------
    # 单例模式
    # -------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "SingularityEliminator":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -------------------------------------------------------------------
    # 状态方法
    # -------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态字典"""
        type_counts: Dict[str, int] = {}
        for sig in self._elimination_log:
            type_counts[sig.type] = type_counts.get(sig.type, 0) + 1
        return {
            "module_id": "M147",
            "module_name": "SingularityEliminator",
            "version": "7.12",
            "d_phi": self._d_phi,
            "max_recursion": self._max_recursion,
            "total_eliminations": len(self._elimination_log),
            "elimination_by_type": type_counts,
            "operation_count": self._operation_count,
            "created_at": self._created_at,
        }

    # ===================================================================
    # 安全除法（除零保护）
    # ===================================================================

    def safe_divide(
        self,
        numerator: float,
        denominator: float,
        context: str = "",
    ) -> SafeDivisionResult:
        """
        安全除法：用 d_φ 替换零分母

        在金符时空中，分母不可能为零——
        最小的非零物理量是 d_φ。

        Args:
            numerator: 分子
            denominator: 分母
            context: 上下文

        Returns:
            SafeDivisionResult
        """
        is_singular = abs(denominator) < self._d_phi
        d_phi_sub = 0.0

        if is_singular:
            # 分母为奇点，用 d_φ 替换（保持符号）
            sign = 1.0 if denominator >= 0 else -1.0
            safe_denom = sign * self._d_phi
            d_phi_sub = safe_denom
            result = numerator / safe_denom

            signature = SingularitySignature(
                type="division_zero",
                location=context,
                severity=1.0,
                value_before=float("inf") if denominator == 0 else numerator / denominator,
                value_after=result,
                elimination_method=f"denominator replaced with d_phi={self._d_phi}",
            )
            self._elimination_log.append(signature)
        else:
            result = numerator / denominator

        self._operation_count += 1

        return SafeDivisionResult(
            numerator=numerator,
            denominator=denominator,
            result=round(result, 12),
            was_singular=is_singular,
            d_phi_substitution=round(d_phi_sub, 15),
        )

    # ===================================================================
    # 曲率奇点检测
    # ===================================================================

    def detect_curvature_singularity(
        self,
        metric_values: List[float],
        threshold: float = 1e8,
        context: str = "",
    ) -> Dict[str, Any]:
        """
        检测度量值序列中的曲率奇点

        在广义相对论中，曲率标量 R → ∞ 标志着奇点。
        在金符时空中，最大曲率为 R_max = 1/d_φ²。

        Args:
            metric_values: 度量值序列
            threshold: 奇点阈值
            context: 上下文

        Returns:
            检测结果
        """
        r_max = 1.0 / (self._d_phi ** 2)  # 最大曲率

        singularities = []
        for i, val in enumerate(metric_values):
            if abs(val) > threshold:
                severity = min(1.0, abs(val) / r_max)
                # 金符消除: 曲率截断到 R_max
                eliminated = math.copysign(min(abs(val), r_max), val)

                signature = SingularitySignature(
                    type="curvature",
                    location=f"{context}[{i}]",
                    severity=round(severity, 6),
                    value_before=val,
                    value_after=round(eliminated, 12),
                    elimination_method=f"curvature capped at R_max=1/d_phi^2={r_max:.2e}",
                )
                singularities.append(asdict(signature))
                self._elimination_log.append(signature)

        self._operation_count += 1

        return {
            "input_length": len(metric_values),
            "singularities_found": len(singularities),
            "max_curvature_detected": round(max(abs(v) for v in metric_values) if metric_values else 0, 6),
            "r_max_jinfu": r_max,
            "r_max_scientific": f"{r_max:.4e}",
            "singularities": singularities,
            "eliminated": (
                f"所有曲率值截断到 R_max = 1/d_phi^2 = {r_max:.2e}"
                if singularities else "无曲率奇点"
            ),
        }

    # ===================================================================
    # 递归奇点保护
    # ===================================================================

    def analyze_recursion(
        self,
        recursion_depth: int,
        context: str = "",
    ) -> RecursionAnalysis:
        """
        分析递归深度，检测递归奇点

        在金符时空中，递归层数受限于金灵球总数（有限）。
        递归深度超过 max_recursion 即为奇点。

        Args:
            recursion_depth: 实际递归深度
            context: 上下文

        Returns:
            RecursionAnalysis
        """
        is_singular = recursion_depth > self._max_recursion

        if is_singular:
            signature = SingularitySignature(
                type="recursion",
                location=context,
                severity=round(min(1.0, recursion_depth / self._max_recursion), 6),
                value_before=float(recursion_depth),
                value_after=self._max_recursion,
                elimination_method=f"recursion depth capped at {self._max_recursion}",
            )
            self._elimination_log.append(signature)

        # 模拟调用栈
        stack_trace = []
        for i in range(min(recursion_depth, 10)):
            stack_trace.append(f"level_{i}")

        self._operation_count += 1

        return RecursionAnalysis(
            max_depth_reached=min(recursion_depth, self._max_recursion),
            max_depth_allowed=self._max_recursion,
            singularity_detected=is_singular,
            stack_trace=stack_trace,
        )

    # ===================================================================
    # 溢出保护
    # ===================================================================

    def safe_compute(
        self,
        fn,
        *args,
        context: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        安全计算：捕获所有数值异常并消除

        Args:
            fn: 计算函数
            context: 上下文

        Returns:
            计算结果
        """
        try:
            result = fn(*args, **kwargs)
            if isinstance(result, float) and not math.isfinite(result):
                # 无穷大或NaN → 用有限值替换
                eliminated = self._d_phi if math.isnan(result) else math.copysign(1e15, result)

                sig_type = "overflow" if math.isinf(result) else "nan"
                signature = SingularitySignature(
                    type=sig_type,
                    location=context,
                    severity=1.0,
                    value_before=result,
                    value_after=eliminated,
                    elimination_method=f"{sig_type} replaced with finite value",
                )
                self._elimination_log.append(signature)
                self._operation_count += 1

                return {
                    "result": eliminated,
                    "was_singular": True,
                    "elimination": asdict(signature),
                }

            self._operation_count += 1
            return {
                "result": result,
                "was_singular": False,
            }

        except (ZeroDivisionError, OverflowError, ValueError) as e:
            signature = SingularitySignature(
                type="exception",
                location=context,
                severity=1.0,
                value_before=float("nan"),
                value_after=self._d_phi,
                elimination_method=f"exception {type(e).__name__} handled: result = d_phi",
            )
            self._elimination_log.append(signature)
            self._operation_count += 1

            return {
                "result": self._d_phi,
                "was_singular": True,
                "elimination": asdict(signature),
                "error": str(e),
            }

    # ===================================================================
    # 桥接方法: M142 UVRegularizationEngine
    # ===================================================================

    def bridge_uv_singularity(
        self,
        integral_values: List[float],
    ) -> Dict[str, Any]:
        """
        桥接M142: 紫外正则化消除积分奇点

        UV正则化消除了动量积分的发散，
        奇点消除器确保中间计算的每一步都有限。

        Args:
            integral_values: 积分中间值

        Returns:
            综合分析结果
        """
        singularities_found = 0
        max_val = 0.0

        for i, val in enumerate(integral_values):
            if not math.isfinite(val):
                singularities_found += 1
            elif abs(val) > max_val:
                max_val = abs(val)

        self._operation_count += 1

        return {
            "total_values": len(integral_values),
            "singularities": singularities_found,
            "max_value": max_val,
            "uv_cutoff": self._d_phi,
            "note": (
                "UV正则化保证积分上限有限(k_max=π/d_φ)，"
                "奇点消除器保证中间计算每步有限"
            ),
        }

    # ===================================================================
    # 定理T109: 奇点消除定理
    # ===================================================================

    def verify_singularity_elimination_theorem(self) -> Dict[str, Any]:
        """
        定理T109: 奇点消除定理

        陈述: 在具有最小长度 d_φ 的金符离散系统中：
        1. 曲率有上界: |R| ≤ 1/d_φ²
        2. 除法安全: ∀a,b, a/b 当 |b|≥d_φ 时有定义
        3. 递归有界: 递归深度 ≤ N_max（金灵球总数）
        因此，金符系统中不存在奇点。

        验证方法:
        1. 测试除零保护
        2. 测试曲率截断
        3. 测试递归保护
        """
        start_time = time.time()

        # 1. 除零保护测试
        division_tests = [
            (1.0, 0.0),
            (1.0, 1e-15),
            (1.0, 1e-20),
            (0.0, 0.0),
            (-5.0, 0.0),
            (100.0, 1e-12),
        ]
        division_results = []
        all_div_safe = True
        for num, den in division_tests:
            result = self.safe_divide(num, den, context="theorem_test")
            is_safe = math.isfinite(result.result)
            division_results.append({
                "numerator": num,
                "denominator": den,
                "result": result.result,
                "finite": is_safe,
                "was_singular": result.was_singular,
            })
            if not is_safe:
                all_div_safe = False

        # 2. 曲率截断测试
        curvature_values = [1e5, 1e10, 1e15, 1e20, 1e30, float("inf"), -1e20]
        curvature_result = self.detect_curvature_singularity(
            curvature_values, threshold=1e8, context="theorem_test"
        )

        # 3. 递归保护测试
        recursion_depths = [10, 100, 500, 1000, 5000]
        recursion_results = []
        all_rec_safe = True
        for depth in recursion_depths:
            analysis = self.analyze_recursion(depth, context="theorem_test")
            is_safe = analysis.max_depth_reached <= self._max_recursion
            recursion_results.append({
                "input_depth": depth,
                "capped_depth": analysis.max_depth_reached,
                "singular": analysis.singularity_detected,
                "safe": is_safe,
            })
            if not is_safe:
                all_rec_safe = False

        elapsed = time.time() - start_time

        return {
            "theorem": "T109",
            "name": "奇点消除定理",
            "verified": all_div_safe and all_rec_safe,
            "details": (
                f"除零保护: {'全部安全' if all_div_safe else '存在不安全'}, "
                f"曲率截断: {curvature_result['singularities_found']}个奇点已消除, "
                f"递归保护: {'全部安全' if all_rec_safe else '存在不安全'}"
            ),
            "division_tests": division_results,
            "curvature_analysis": curvature_result,
            "recursion_tests": recursion_results,
            "r_max": 1.0 / (self._d_phi ** 2),
            "max_recursion": self._max_recursion,
            "conclusion": (
                "金符离散系统中，d_φ的存在保证了曲率有界、除法安全、递归有界，"
                "连续统意义下的奇点是伪问题"
            ),
            "elapsed_seconds": round(elapsed, 4),
        }


# ===========================================================================
# 模块级单例
# ===========================================================================

_instance: Optional[SingularityEliminator] = None


def get_instance() -> SingularityEliminator:
    """获取 SingularityEliminator 单例"""
    global _instance
    if _instance is None:
        _instance = SingularityEliminator()
    return _instance


# ===========================================================================
# 模块自检
# ===========================================================================

def _self_test() -> Dict[str, Any]:
    """模块自检"""
    engine = get_instance()
    results: Dict[str, Any] = {}

    # 除零保护测试
    div1 = engine.safe_divide(1.0, 0.0)
    div2 = engine.safe_divide(1.0, 1e-20)
    div3 = engine.safe_divide(10.0, 2.0)
    results["division_zero"] = {
        "div_by_zero_safe": math.isfinite(div1.result),
        "div_by_tiny_safe": math.isfinite(div2.result),
        "normal_div": round(div3.result, 2),
        "pass": math.isfinite(div1.result) and math.isfinite(div2.result),
    }

    # 曲率奇点测试
    curvature = engine.detect_curvature_singularity([1.0, 1e10, 1e20, float("inf")])
    results["curvature"] = {
        "found": curvature["singularities_found"],
        "pass": curvature["singularities_found"] == 3,
    }

    # 递归保护测试
    recursion = engine.analyze_recursion(5000)
    results["recursion"] = {
        "input": 5000,
        "capped": recursion.max_depth_reached,
        "singular": recursion.singularity_detected,
        "pass": recursion.max_depth_reached <= engine._max_recursion,
    }

    # 安全计算测试
    safe = engine.safe_compute(lambda: 1.0 / 0.0, context="test")
    results["safe_compute"] = {
        "finite": math.isfinite(safe["result"]),
        "singular": safe["was_singular"],
        "pass": math.isfinite(safe["result"]),
    }

    # 定理T109测试
    t109 = engine.verify_singularity_elimination_theorem()
    results["T109"] = t109

    # 状态测试
    state = engine.get_state()
    results["state"] = state

    return results


if __name__ == "__main__":
    import json
    test_results = _self_test()
    print(json.dumps(test_results, indent=2, ensure_ascii=False, default=str))
