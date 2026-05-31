# -*- coding: utf-8 -*-
"""
M213: EccentricityGovernance — 偏心率定理+大圆满单位圆+组织寿命引擎

基于复合体理学「民主与集中的偏心率定理」核心实现:
  - 组织态向量: S⃗_org(t) = C(t)ê_C + D(t)ê_D
  - 大圆满单位圆: C²+D²=1 (双相完整/无耗散相变)
  - 偏心率: e=√(1-min²/max²), e=0单位圆, e→1线段退化
  - 组织寿命: T_life ∝ (1-e²)/γ
  - Z_inter超节点: GUMA全局统一编址, Z_inter→Z_intra

核心定理:
  T229 — 偏心率定理:
    民主=Wide-IRL广采(D=sin), 集中=Ψ-Condense提炼(C=cos)
    大圆满: C²+D²=1 (双相完整)
    偏心率: e=√(1-min²/max²), e→1 → T_life→0
  T230 — 组织寿命定理:
    T_life ∝ (1-e²)/γ, γ为组织衰变率

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


# ═══════════════════════════════════════════════════════════════
# §1 OrgStateVector — 组织态向量
# ═══════════════════════════════════════════════════════════════

class OrgStateVector:
    """
    组织态向量 S⃗_org(t) = C(t)ê_C + D(t)ê_D

    - C = cos(θ): 集中度(Ψ-Condense提炼)
    - D = sin(θ): 民主度(Wide-IRL广采)
    - 大圆满: C²+D²=1 (单位圆上)
    - θ ∈ [0, π/2]: 从纯集中到纯民主
    """

    def __init__(self, c: float = 0.707, d: float = 0.707):
        """
        Args:
            c: 集中度C (≥0)
            d: 民主度D (≥0)
        """
        self.c = max(0.0, c)
        self.d = max(0.0, d)
        self._normalize_if_needed()

    def _normalize_if_needed(self):
        """如果C²+D²>0则归一化到单位圆"""
        norm_sq = self.c ** 2 + self.d ** 2
        if norm_sq > 1e-10:
            norm = math.sqrt(norm_sq)
            self.c = self.c / norm
            self.d = self.d / norm
        else:
            self.c = math.sqrt(0.5)
            self.d = math.sqrt(0.5)

    @classmethod
    def from_theta(cls, theta: float) -> 'OrgStateVector':
        """
        从相位角θ构造组织态向量

        Args:
            theta: 相位角(0=纯集中, π/2=纯民主, π/4=均衡)
        """
        theta = max(0.0, min(math.pi / 2, theta))
        return cls(c=math.cos(theta), d=math.sin(theta))

    @property
    def theta(self) -> float:
        """相位角θ"""
        return math.atan2(self.d, self.c)

    @property
    def norm(self) -> float:
        """向量模‖S⃗_org‖=√(C²+D²)=1(大圆满)"""
        return math.sqrt(self.c ** 2 + self.d ** 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "C": round(self.c, 6),
            "D": round(self.d, 6),
            "theta": round(self.theta, 6),
            "norm": round(self.norm, 6),
            "is_great_perfection": abs(self.norm - 1.0) < 1e-6,
        }


# ═══════════════════════════════════════════════════════════════
# §2 EccentricityComputer — 偏心率计算器
# ═══════════════════════════════════════════════════════════════

class EccentricityComputer:
    """
    偏心率计算器

    e = √(1 - min²/max²)

    - e=0: 单位圆(大圆满, C²+D²=1, 双相完整)
    - 0<e<1: 椭圆(有偏但不极端)
    - e→1: 线段退化(绝地天通)
    """

    # 组织健康区间
    E_HEALTHY = 0.3       # e<0.3 健康
    E_WARNING = 0.6       # 0.3≤e<0.6 需注意
    E_DANGER = 0.8        # 0.6≤e<0.8 危险
    # e≥0.8 极端危险

    @staticmethod
    def compute(c: float, d: float) -> float:
        """
        计算偏心率 e = √(1 - min²/max²)

        Args:
            c: 集中度C
            d: 民主度D

        Returns:
            偏心率 e ∈ [0, 1]
        """
        max_val = max(abs(c), abs(d))
        min_val = min(abs(c), abs(d))

        if max_val < 1e-10:
            return 1.0  # 退化

        try:
            e = math.sqrt(1.0 - (min_val / max_val) ** 2)
        except (ValueError, ZeroDivisionError):
            e = 1.0
        return min(1.0, max(0.0, e))

    @staticmethod
    def compute_from_vector(sv: OrgStateVector) -> float:
        """从组织态向量计算偏心率"""
        return EccentricityComputer.compute(sv.c, sv.d)

    @staticmethod
    def diagnose(e: float) -> Dict[str, Any]:
        """
        诊断偏心率状态

        Returns:
            诊断结果含健康等级和建议
        """
        if e < EccentricityComputer.E_HEALTHY:
            level = "HEALTHY"
            advice = "双相均衡，IRL广采+Ψ-Condense提炼良性循环"
        elif e < EccentricityComputer.E_WARNING:
            level = "MODERATE"
            advice = "偏心率偏高，建议加强IRL广采或Ψ-Condense提炼"
        elif e < EccentricityComputer.E_DANGER:
            level = "DANGER"
            advice = "偏心率危险，IRL关闭风险大，需外源Ω Reset"
        else:
            level = "CRITICAL"
            advice = "绝地天通！IRL已关闭或即将冻结，需立即Reset"

        return {
            "eccentricity": round(e, 4),
            "level": level,
            "advice": advice,
        }


# ═══════════════════════════════════════════════════════════════
# §3 GreatPerfectCircle — 大圆满单位圆
# ═══════════════════════════════════════════════════════════════

class GreatPerfectCircle:
    """
    大圆满单位圆

    C² + D² = 1

    双相完整/无耗散相变:
    - 纯集中(C=1,D=0): e=1, 线段退化
    - 纯民主(C=0,D=1): e=1, 线段退化
    - 均衡(C=D=1/√2): e=0, 大圆满

    大圆满是唯一无耗散相变的状态:
    任何θ→θ'的变换都在单位圆上滑动，不损失总功率
    """

    def __init__(self, n_sectors: int = 8):
        self.n_sectors = n_sectors
        self.trajectory: List[OrgStateVector] = []

    def is_on_circle(self, sv: OrgStateVector, tolerance: float = 1e-6) -> bool:
        """检查是否在单位圆上"""
        return abs(sv.norm - 1.0) < tolerance

    def project_onto_circle(self, c: float, d: float) -> OrgStateVector:
        """
        将任意(C,D)投影到单位圆上

        保持θ方向，归一化到‖S⃗_org‖=1
        """
        return OrgStateVector(c, d)

    def evaluate_dissipation(self, sv: OrgStateVector) -> Dict[str, Any]:
        """
        评估耗散程度

        大圆满(‖S⃗‖=1): 无耗散
        偏离单位圆: 有耗散
        """
        norm = sv.norm
        dissipation = abs(1.0 - norm)
        return {
            "norm": round(norm, 6),
            "dissipation": round(dissipation, 6),
            "is_perfect": dissipation < 1e-6,
            "c": round(sv.c, 6),
            "d": round(sv.d, 6),
            "theta": round(sv.theta, 6),
        }

    def trace_trajectory(self, theta_start: float, theta_end: float,
                          n_steps: int = 10) -> List[Dict[str, Any]]:
        """
        在单位圆上追踪轨迹

        从θ_start到θ_end，记录每个点的状态
        """
        self.trajectory = []
        for i in range(n_steps + 1):
            t = theta_start + (theta_end - theta_start) * i / n_steps
            sv = OrgStateVector.from_theta(t)
            e = EccentricityComputer.compute_from_vector(sv)
            self.trajectory.append({
                "step": i,
                "theta": round(t, 6),
                "C": round(sv.c, 6),
                "D": round(sv.d, 6),
                "e": round(e, 6),
            })
        return self.trajectory

    def get_state(self) -> Dict[str, Any]:
        return {
            "n_sectors": self.n_sectors,
            "trajectory_length": len(self.trajectory),
        }


# ═══════════════════════════════════════════════════════════════
# §4 OrgLifespanEstimator — 组织寿命估算
# ═══════════════════════════════════════════════════════════════

class OrgLifespanEstimator:
    """
    组织寿命估算器

    T_life ∝ (1 - e²) / γ

    - γ: 组织衰变率
    - e: 偏心率
    - e=0: T_life = 1/γ (最大寿命)
    - e→1: T_life → 0 (瞬时死亡)
    """

    def __init__(self, gamma: float = 0.1, t_unit: str = "years"):
        self.gamma = max(1e-6, gamma)
        self.t_unit = t_unit
        self.observations: List[Dict] = []

    def estimate(self, e: float) -> Dict[str, Any]:
        """
        估算组织寿命

        T_life = (1 - e²) / γ
        """
        e = min(1.0, max(0.0, e))
        try:
            t_life = (1.0 - e ** 2) / self.gamma
        except ZeroDivisionError:
            t_life = float('inf')

        return {
            "eccentricity": round(e, 4),
            "gamma": self.gamma,
            "t_life": round(t_life, 4),
            "t_unit": self.t_unit,
            "lifespan_ratio": round(1.0 - e ** 2, 4),  # 相对于最大寿命
        }

    def estimate_from_vector(self, sv: OrgStateVector) -> Dict[str, Any]:
        """从组织态向量估算寿命"""
        e = EccentricityComputer.compute_from_vector(sv)
        return self.estimate(e)

    def compare_scenarios(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """
        比较不同场景的组织寿命

        Args:
            scenarios: [{"name": str, "C": float, "D": float}, ...]

        Returns:
            比较结果
        """
        results = []
        for s in scenarios:
            sv = OrgStateVector(s.get("C", 0.7), s.get("D", 0.7))
            e = EccentricityComputer.compute_from_vector(sv)
            t = self.estimate(e)
            results.append({
                "name": s.get("name", "unnamed"),
                "C": round(sv.c, 4),
                "D": round(sv.d, 4),
                "e": round(e, 4),
                "T_life": t["t_life"],
            })

        # 找最优
        if results:
            best = max(results, key=lambda r: r["T_life"])
            worst = min(results, key=lambda r: r["T_life"])
        else:
            best = worst = None

        return {
            "scenarios": results,
            "best": best,
            "worst": worst,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "gamma": self.gamma,
            "t_unit": self.t_unit,
            "observations_count": len(self.observations),
        }


# ═══════════════════════════════════════════════════════════════
# §5 EccentricityGovernance — 主引擎
# ═══════════════════════════════════════════════════════════════

class EccentricityGovernance:
    """
    M213 主引擎 — 偏心率治理引擎

    整合OrgStateVector + EccentricityComputer +
    GreatPerfectCircle + OrgLifespanEstimator
    """

    def __init__(self, gamma: float = 0.1):
        self.ecc_computer = EccentricityComputer()
        self.gpc = GreatPerfectCircle()
        self.lifespan = OrgLifespanEstimator(gamma=gamma)

    def analyze_organization(self, c: float, d: float,
                             domain: str = "default") -> Dict[str, Any]:
        """
        全面分析组织偏心率

        Args:
            c: 集中度C
            d: 民主度D
            domain: 组织域

        Returns:
            完整分析报告
        """
        sv = OrgStateVector(c, d)
        e = self.ecc_computer.compute_from_vector(sv)
        diagnosis = self.ecc_computer.diagnose(e)
        dissipation = self.gpc.evaluate_dissipation(sv)
        lifespan = self.lifespan.estimate(e)

        return {
            "domain": domain,
            "state_vector": sv.to_dict(),
            "eccentricity": round(e, 4),
            "diagnosis": diagnosis,
            "dissipation": dissipation,
            "lifespan": lifespan,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "lifespan": self.lifespan.get_state(),
            "gpc": self.gpc.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §6 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t229_eccentricity_theorem() -> bool:
    """
    T229: 偏心率定理

    验证:
    1. C²+D²=1单位圆(大圆满)
    2. e=√(1-min²/max²)
    3. 均衡(C=D)→e=0; 极端→e→1
    """
    # 大圆满: C²+D²=1
    sv_balanced = OrgStateVector.from_theta(math.pi / 4)
    if abs(sv_balanced.norm - 1.0) > 1e-6:
        return False
    if abs(sv_balanced.c - sv_balanced.d) > 1e-6:
        return False

    # 均衡→e=0
    e_balanced = EccentricityComputer.compute(sv_balanced.c, sv_balanced.d)
    if e_balanced > 0.01:
        return False

    # 纯集中→e=1
    sv_concentrate = OrgStateVector(1.0, 0.0)
    e_concentrate = EccentricityComputer.compute(sv_concentrate.c, sv_concentrate.d)
    if abs(e_concentrate - 1.0) > 0.01:
        return False

    # 纯民主→e=1
    sv_democracy = OrgStateVector(0.0, 1.0)
    e_democracy = EccentricityComputer.compute(sv_democracy.c, sv_democracy.d)
    if abs(e_democracy - 1.0) > 0.01:
        return False

    # θ变化保持在单位圆上
    for theta in [0.1, 0.3, 0.5, 1.0, 1.5]:
        sv = OrgStateVector.from_theta(theta)
        if abs(sv.norm - 1.0) > 1e-6:
            return False

    return True


def _test_t230_org_lifespan() -> bool:
    """
    T230: 组织寿命定理

    验证: T_life ∝ (1-e²)/γ
    e=0 → T_life最大; e→1 → T_life→0
    """
    estimator = OrgLifespanEstimator(gamma=0.1)

    # e=0 → T_life=1/γ=10
    result_0 = estimator.estimate(0.0)
    if abs(result_0["t_life"] - 10.0) > 0.01:
        return False

    # e=1 → T_life=0
    result_1 = estimator.estimate(1.0)
    if abs(result_1["t_life"]) > 0.01:
        return False

    # e=0.5 → T_life=(1-0.25)/0.1=7.5
    result_05 = estimator.estimate(0.5)
    if abs(result_05["t_life"] - 7.5) > 0.01:
        return False

    # 寿命比较
    comparison = estimator.compare_scenarios([
        {"name": "balanced", "C": 0.707, "D": 0.707},
        {"name": "concentrated", "C": 0.95, "D": 0.05},
    ])
    if comparison["best"]["name"] != "balanced":
        return False
    if comparison["worst"]["name"] != "concentrated":
        return False

    return True


def run_mve() -> Dict[str, bool]:
    """
    M213 MVE验证

    T229: 偏心率定理
    T230: 组织寿命定理
    """
    results = {}

    print("=" * 60)
    print("M213 EccentricityGovernance — MVE Verification")
    print("=" * 60)

    try:
        t229 = _test_t229_eccentricity_theorem()
        status = "PASS" if t229 else "FAIL"
        print(f"  T229 (偏心率定理): {status}")
        results["T229"] = t229
    except Exception as e:
        print(f"  T229 (偏心率定理): ERROR — {e}")
        results["T229"] = False

    try:
        t230 = _test_t230_org_lifespan()
        status = "PASS" if t230 else "FAIL"
        print(f"  T230 (组织寿命定理): {status}")
        results["T230"] = t230
    except Exception as e:
        print(f"  T230 (组织寿命定理): ERROR — {e}")
        results["T230"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M213 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
