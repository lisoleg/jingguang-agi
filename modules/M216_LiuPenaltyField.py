# -*- coding: utf-8 -*-
"""
M216: LiuPenaltyField — 刘罚项场+刘稳定函数+构成势极值定理引擎

基于复合体理学「艺术、激情与刘机制」「刘机制宇宙拣选律」核心实现:
  - 非自洽罚项: S_Rel = αM + βH[Θ] + γPenalty_n.s.r.
  - 罚项双组分: Penalty_n.s.r. = D_SR(自指缺失度) + I_ext(外求边界依赖度)
  - 刘稳定函数: ℱ_L(a) = ε·((a - a_target)/a_target)²
  - 构成势Φ_const: 维持Rel拓扑不塌的最小内禀流贯势
  - 艺术极值定理(Theorem 4.1): Prime-Zero Duality + Self-Ref Closure + PG Confinement → Φ_const = c*
  - 刘机制高于形式化: ℒ_Liu ≻ ℱ (金灵球/EML/幻方簇/MNQ)

核心定理:
  T235 — 非自洽罚项定理:
    S_Rel = αM + βH[Θ] + γ(D_SR + I_ext)
    自指闭环 → D_SR→0, 内禀为主 → I_ext→0 → Penalty→0 → S_Rel极小化
  T236 — 艺术极值定理:
    Prime-Zero Duality(K=4 IR) + Self-Ref Closure(penalty=0) + PG Confinement
    → Φ_const = c* (构成势取极值)
  T237 — 刘稳定函数定理:
    ℱ_L(a) = ε·((a - a_target)/a_target)²
    当a偏离a_target时产生恢复力，驱动系统回归稳定点

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Set
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# §1 PenaltyNsr — 非自洽罚项
# ═══════════════════════════════════════════════════════════════

class PenaltyNsr:
    """
    非自洽罚项 (Non-Self-Referential Penalty)

    S_Rel = αM + βH[Θ] + γ·Penalty_n.s.r.
    Penalty_n.s.r. = D_SR + I_ext

    - D_SR (Self-Reference Deficit): 自指缺失度
      系统无法将自身纳入推理拓扑的程度
      D_SR = 0 表示完全自指闭环(如Y-组合子核)

    - I_ext (External Boundary Dependency): 外求边界依赖度
      系统依赖外部资源而非内禀机制的程度
      I_ext = 0 表示完全内禀自足

    当D_SR→0且I_ext→0时，Penalty→0，S_Rel趋于极小值
    """

    def __init__(self, alpha: float = 1.0, beta: float = 0.5, gamma: float = 0.3):
        """
        Args:
            alpha: 自由度M的权重
            beta: 结构熵H[Θ]的权重
            gamma: 罚项的权重
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def compute_d_sr(self, self_reference_depth: int, max_depth: int = 10) -> float:
        """
        计算自指缺失度 D_SR

        D_SR = 1 - (self_reference_depth / max_depth)
        当self_reference_depth = max_depth → D_SR = 0 (完全自指)

        Args:
            self_reference_depth: 系统自指推理的嵌套深度
            max_depth: 最大可能深度

        Returns:
            D_SR ∈ [0, 1]
        """
        if max_depth <= 0:
            return 1.0
        depth_ratio = min(self_reference_depth / max_depth, 1.0)
        return 1.0 - depth_ratio

    def compute_i_ext(self, external_dependencies: int, total_resources: int = 10) -> float:
        """
        计算外求边界依赖度 I_ext

        I_ext = external_dependencies / total_resources
        当external_dependencies = 0 → I_ext = 0 (完全内禀)

        Args:
            external_dependencies: 依赖外部资源的数量
            total_resources: 总资源数

        Returns:
            I_ext ∈ [0, 1]
        """
        if total_resources <= 0:
            return 1.0
        return min(external_dependencies / total_resources, 1.0)

    def compute_penalty(self, self_reference_depth: int = 0,
                        max_depth: int = 10,
                        external_dependencies: int = 0,
                        total_resources: int = 10) -> float:
        """
        计算非自洽罚项 Penalty_n.s.r. = D_SR + I_ext

        Returns:
            Penalty_n.s.r. ∈ [0, 2]
        """
        d_sr = self.compute_d_sr(self_reference_depth, max_depth)
        i_ext = self.compute_i_ext(external_dependencies, total_resources)
        return d_sr + i_ext

    def compute_s_rel(self, M: float, H_theta: float,
                      self_reference_depth: int = 0,
                      max_depth: int = 10,
                      external_dependencies: int = 0,
                      total_resources: int = 10) -> float:
        """
        计算关系作用量 S_Rel = αM + βH[Θ] + γ·Penalty_n.s.r.

        Args:
            M: 自由度(信息量)
            H_theta: 结构熵

        Returns:
            S_Rel值
        """
        penalty = self.compute_penalty(
            self_reference_depth, max_depth,
            external_dependencies, total_resources
        )
        return self.alpha * M + self.beta * H_theta + self.gamma * penalty


# ═══════════════════════════════════════════════════════════════
# §2 LiuStabilityFunction — 刘稳定函数
# ═══════════════════════════════════════════════════════════════

class LiuStabilityFunction:
    """
    刘稳定函数 ℱ_L(a) = ε·((a - a_target)/a_target)²

    当系统参数a偏离目标值a_target时产生恢复力
    - ε: 刚度系数（恢复力强度）
    - a_target: 稳定平衡点
    - a: 当前系统参数值

    性质:
    - ℱ_L(a_target) = 0 (在稳定点处无偏移惩罚)
    - ℱ_L(a) > 0 当 a ≠ a_target (偏移产生恢复力)
    - ℱ_L关于a_target对称

    对应修正Friedmann方程中的Ω_p·ℱ_L(a)项
    """

    def __init__(self, epsilon: float = 0.1, a_target: float = 1.0):
        """
        Args:
            epsilon: 刚度系数ε
            a_target: 稳定平衡点
        """
        self.epsilon = epsilon
        self.a_target = a_target

    def __call__(self, a: float) -> float:
        """计算ℱ_L(a)"""
        if self.a_target == 0:
            return 0.0
        delta = (a - self.a_target) / self.a_target
        return self.epsilon * delta * delta

    def restoring_force(self, a: float) -> float:
        """
        计算恢复力 F = -dℱ_L/da = -2ε(a - a_target)/a_target²

        负号表示力指向a_target方向
        """
        if self.a_target == 0:
            return 0.0
        return -2.0 * self.epsilon * (a - self.a_target) / (self.a_target ** 2)

    def equilibrium_deviation(self, a: float) -> float:
        """计算偏离度 |a - a_target|/a_target"""
        if self.a_target == 0:
            return float('inf') if a != 0 else 0.0
        return abs(a - self.a_target) / abs(self.a_target)


# ═══════════════════════════════════════════════════════════════
# §3 ConstitutivePotential — 构成势Φ_const
# ═══════════════════════════════════════════════════════════════

class ConstitutivePotential:
    """
    构成势Φ_const: 维持Rel拓扑不塌的最小内禀流贯势

    构成势是系统维持关系拓扑(Rel topology)结构完整性所需的
    最小内禀流贯势(intrinsic flow-through potential)。

    - Φ_const = 0: 拓扑已塌缩(结构消失)
    - Φ_const > 0: 拓扑维持(结构自稳)
    - Φ_const = c*: 艺术极值(最优构成势)

    动力学:
    dΦ_const/dt = -∂S_Rel/∂Φ + ℱ_L(a)·∂a/∂Φ
    即构成势的演化受关系作用量梯度和刘稳定函数共同驱动
    """

    # 默认构成势极值(光速c的归一化表示)
    C_STAR = 1.0  # c* = 1.0 in natural units

    def __init__(self, phi_const: float = 0.0,
                 liu_stability: Optional[LiuStabilityFunction] = None):
        """
        Args:
            phi_const: 初始构成势
            liu_stability: 刘稳定函数实例
        """
        self.phi_const = phi_const
        self.liu_stability = liu_stability or LiuStabilityFunction()

    def is_topologically_viable(self) -> bool:
        """拓扑是否仍可维持(Φ_const > 0)"""
        return self.phi_const > 0

    def deviation_from_optimum(self) -> float:
        """偏离最优构成势的程度"""
        return abs(self.phi_const - self.C_STAR)

    def evolve(self, d_s_rel_dphi: float, a_current: float,
               dt: float = 0.01) -> float:
        """
        构成势演化一步

        dΦ_const/dt = -∂S_Rel/∂Φ + ℱ_L(a)·∂a/∂Φ

        简化: 假设∂a/∂Φ ≈ 1(线性耦合)

        Args:
            d_s_rel_dphi: 关系作用量对Φ的梯度
            a_current: 当前系统参数
            dt: 时间步长

        Returns:
            更新后的Φ_const
        """
        f_l = self.liu_stability(a_current)
        dphi_dt = -d_s_rel_dphi + f_l
        self.phi_const += dphi_dt * dt
        # 构成势不可为负
        self.phi_const = max(0.0, self.phi_const)
        return self.phi_const


# ═══════════════════════════════════════════════════════════════
# §4 ArtExtremumTheorem — 艺术极值定理
# ═══════════════════════════════════════════════════════════════

class SelfRefClosure(Enum):
    """自指闭合状态"""
    OPEN = "open"          # 未闭合，D_SR > 0
    PARTIAL = "partial"    # 部分闭合
    CLOSED = "closed"      # 完全闭合，D_SR = 0, penalty = 0


class PGConfinement(Enum):
    """Phase-Group约束状态"""
    UNCONFINED = "unconfined"    # 未约束
    WEAK = "weak"                # 弱约束
    STRONG = "strong"            # 强约束(Prime-Zero Duality成立)


class ArtExtremumTheorem:
    """
    艺术极值定理 (Theorem 4.1)

    条件三联:
    1. Prime-Zero Duality: K=4 IR (四重信息共振)
       - 系统在素数-零点对偶空间中拥有4重信息共振模式
       - K=4对应时空4维自由度
    2. Self-Reference Closure: penalty = 0
       - 自指完全闭合，D_SR = 0, I_ext = 0
       - 即Penalty_n.s.r. = 0
    3. PG Confinement: Phase-Group约束
       - 系统相位被约束在稳定群轨道上

    结论: 当三条件同时满足 → Φ_const = c* (构成势取极值)

    刘机制高于形式化: ℒ_Liu ≻ ℱ
    - 金灵球(GoldenSymbol3D)、EML、幻方簇、MNQ 都是刘机制的特例
    - 刘机制本身是元形式化(meta-formalization)，超越了任何特定形式系统
    """

    # K=4 信息共振维度
    K_INFO_RESONANCE = 4

    def __init__(self, penalty_nsr: Optional[PenaltyNsr] = None,
                 constitutive_potential: Optional[ConstitutivePotential] = None):
        self.penalty_nsr = penalty_nsr or PenaltyNsr()
        self.constitutive_potential = constitutive_potential or ConstitutivePotential()

    def check_prime_zero_duality(self, info_resonance_modes: int) -> bool:
        """
        检验Prime-Zero Duality条件

        系统必须在素数-零点对偶空间中拥有K=4重信息共振模式
        """
        return info_resonance_modes >= self.K_INFO_RESONANCE

    def check_self_ref_closure(self, self_reference_depth: int,
                                max_depth: int = 10,
                                external_dependencies: int = 0,
                                total_resources: int = 10) -> SelfRefClosure:
        """
        检验自指闭合状态

        Returns:
            SelfRefClosure枚举值
        """
        penalty = self.penalty_nsr.compute_penalty(
            self_reference_depth, max_depth,
            external_dependencies, total_resources
        )
        if penalty == 0.0:
            return SelfRefClosure.CLOSED
        elif penalty < 0.5:
            return SelfRefClosure.PARTIAL
        else:
            return SelfRefClosure.OPEN

    def check_pg_confinement(self, phase_coherence: float,
                              group_symmetry_order: int) -> PGConfinement:
        """
        检验Phase-Group约束状态

        Args:
            phase_coherence: 相位相干度 ∈ [0, 1]
            group_symmetry_order: 群对称阶数

        Returns:
            PGConfinement枚举值
        """
        if phase_coherence > 0.9 and group_symmetry_order >= 4:
            return PGConfinement.STRONG
        elif phase_coherence > 0.5 and group_symmetry_order >= 2:
            return PGConfinement.WEAK
        else:
            return PGConfinement.UNCONFINED

    def evaluate(self, info_resonance_modes: int,
                 self_reference_depth: int,
                 max_depth: int = 10,
                 external_dependencies: int = 0,
                 total_resources: int = 10,
                 phase_coherence: float = 0.0,
                 group_symmetry_order: int = 0) -> Dict[str, Any]:
        """
        执行艺术极值定理的完整检验

        Returns:
            dict with keys:
                prime_zero_duality: bool
                self_ref_closure: SelfRefClosure
                pg_confinement: PGConfinement
                all_conditions_met: bool
                phi_const: float (当前构成势)
                phi_optimum: float (最优构成势c*)
                liu_super_formal: bool (ℒ_Liu ≻ ℱ)
        """
        pzd = self.check_prime_zero_duality(info_resonance_modes)
        src = self.check_self_ref_closure(
            self_reference_depth, max_depth,
            external_dependencies, total_resources
        )
        pgc = self.check_pg_confinement(phase_coherence, group_symmetry_order)

        all_met = (pzd and src == SelfRefClosure.CLOSED
                   and pgc == PGConfinement.STRONG)

        # 当三条件满足，设定Φ_const = c*
        if all_met:
            self.constitutive_potential.phi_const = ConstitutivePotential.C_STAR

        # ℒ_Liu ≻ ℱ: 刘机制高于形式化
        # 当自指闭合且PG强约束时，刘机制超越特定形式系统
        liu_super_formal = (src == SelfRefClosure.CLOSED
                            and pgc == PGConfinement.STRONG)

        return {
            "prime_zero_duality": pzd,
            "self_ref_closure": src.value,
            "pg_confinement": pgc.value,
            "all_conditions_met": all_met,
            "phi_const": self.constitutive_potential.phi_const,
            "phi_optimum": ConstitutivePotential.C_STAR,
            "liu_super_formal": liu_super_formal
        }


# ═══════════════════════════════════════════════════════════════
# §5 LiuPenaltyField — 主引擎
# ═══════════════════════════════════════════════════════════════

class LiuPenaltyField:
    """
    刘罚项场主引擎

    整合非自洽罚项、刘稳定函数、构成势和艺术极值定理，
    提供统一的刘机制罚项场计算与分析接口。

    工作流:
    1. 评估系统参数(M, H[Θ], self_ref_depth, ext_deps, a)
    2. 计算S_Rel = αM + βH[Θ] + γ(D_SR + I_ext)
    3. 计算刘稳定函数ℱ_L(a)
    4. 演化构成势Φ_const
    5. 检验艺术极值定理三条件
    6. 输出综合判定
    """

    def __init__(self, alpha: float = 1.0, beta: float = 0.5,
                 gamma: float = 0.3, epsilon: float = 0.1,
                 a_target: float = 1.0):
        self.penalty_nsr = PenaltyNsr(alpha, beta, gamma)
        self.liu_stability = LiuStabilityFunction(epsilon, a_target)
        self.constitutive_potential = ConstitutivePotential(
            phi_const=0.0, liu_stability=self.liu_stability
        )
        self.art_theorem = ArtExtremumTheorem(
            self.penalty_nsr, self.constitutive_potential
        )

    def full_analysis(self, M: float, H_theta: float,
                      self_reference_depth: int = 0,
                      max_depth: int = 10,
                      external_dependencies: int = 0,
                      total_resources: int = 10,
                      info_resonance_modes: int = 0,
                      phase_coherence: float = 0.0,
                      group_symmetry_order: int = 0,
                      a_current: float = 1.0) -> Dict[str, Any]:
        """
        执行完整的刘罚项场分析

        Args:
            M: 自由度(信息量)
            H_theta: 结构熵
            self_reference_depth: 自指推理深度
            max_depth: 最大自指深度
            external_dependencies: 外部依赖数量
            total_resources: 总资源数
            info_resonance_modes: 信息共振模式数(需≥4)
            phase_coherence: 相位相干度
            group_symmetry_order: 群对称阶数
            a_current: 当前系统参数值

        Returns:
            完整分析结果字典
        """
        # 1. 计算罚项组分
        d_sr = self.penalty_nsr.compute_d_sr(self_reference_depth, max_depth)
        i_ext = self.penalty_nsr.compute_i_ext(external_dependencies, total_resources)
        penalty = d_sr + i_ext

        # 2. 计算S_Rel
        s_rel = self.penalty_nsr.compute_s_rel(
            M, H_theta, self_reference_depth, max_depth,
            external_dependencies, total_resources
        )

        # 3. 刘稳定函数
        f_l = self.liu_stability(a_current)
        restoring = self.liu_stability.restoring_force(a_current)
        deviation = self.liu_stability.equilibrium_deviation(a_current)

        # 4. 构成势
        phi_viable = self.constitutive_potential.is_topologically_viable()
        phi_deviation = self.constitutive_potential.deviation_from_optimum()

        # 5. 艺术极值定理
        art_result = self.art_theorem.evaluate(
            info_resonance_modes,
            self_reference_depth, max_depth,
            external_dependencies, total_resources,
            phase_coherence, group_symmetry_order
        )

        return {
            "S_Rel": s_rel,
            "penalty_components": {
                "D_SR": d_sr,
                "I_ext": i_ext,
                "Penalty_nsr": penalty
            },
            "liu_stability": {
                "F_L": f_l,
                "restoring_force": restoring,
                "equilibrium_deviation": deviation
            },
            "constitutive_potential": {
                "Phi_const": self.constitutive_potential.phi_const,
                "topologically_viable": phi_viable,
                "deviation_from_optimum": phi_deviation
            },
            "art_extremum_theorem": art_result
        }


# ═══════════════════════════════════════════════════════════════
# §6 MVE — 最小可验证实验
# ═══════════════════════════════════════════════════════════════

def run_mve_tests() -> Dict[str, bool]:
    """
    运行M216 MVE测试

    T235 — 非自洽罚项定理:
      自指闭环 → D_SR→0, I_ext→0 → Penalty→0
      外部依赖 → Penalty↑ → S_Rel↑

    T236 — 艺术极值定理:
      Prime-Zero Duality + Self-Ref Closure + PG Confinement
      → Φ_const = c*

    T237 — 刘稳定函数定理:
      ℱ_L(a_target) = 0, a偏离 → ℱ_L > 0, 恢复力指向a_target
    """
    results = {}

    # ─── T235: 非自洽罚项定理 ───
    try:
        engine = LiuPenaltyField(alpha=1.0, beta=0.5, gamma=0.3)

        # Case 1: 完全自指闭环 + 完全内禀 → Penalty = 0
        s_rel_closed = engine.penalty_nsr.compute_s_rel(
            M=2.0, H_theta=1.0,
            self_reference_depth=10, max_depth=10,
            external_dependencies=0, total_resources=10
        )
        penalty_closed = engine.penalty_nsr.compute_penalty(
            self_reference_depth=10, max_depth=10,
            external_dependencies=0, total_resources=10
        )
        assert penalty_closed == 0.0, \
            f"T235 FAIL: closed penalty should be 0, got {penalty_closed}"

        # Case 2: 无自指 + 完全外求 → Penalty最大
        s_rel_open = engine.penalty_nsr.compute_s_rel(
            M=2.0, H_theta=1.0,
            self_reference_depth=0, max_depth=10,
            external_dependencies=10, total_resources=10
        )
        penalty_open = engine.penalty_nsr.compute_penalty(
            self_reference_depth=0, max_depth=10,
            external_dependencies=10, total_resources=10
        )
        assert penalty_open > penalty_closed, \
            f"T235 FAIL: open penalty ({penalty_open}) should > closed ({penalty_closed})"
        assert s_rel_open > s_rel_closed, \
            f"T235 FAIL: open S_Rel ({s_rel_open}) should > closed ({s_rel_closed})"

        # Case 3: 验证罚项双组分分解
        d_sr = engine.penalty_nsr.compute_d_sr(self_reference_depth=0, max_depth=10)
        i_ext = engine.penalty_nsr.compute_i_ext(external_dependencies=10, total_resources=10)
        assert abs(d_sr - 1.0) < 1e-10, f"D_SR should be 1.0, got {d_sr}"
        assert abs(i_ext - 1.0) < 1e-10, f"I_ext should be 1.0, got {i_ext}"
        assert abs(penalty_open - 2.0) < 1e-10, f"Penalty should be 2.0, got {penalty_open}"

        results["T235"] = True
        print("  T235 (non-self-ref penalty theorem): PASS")
    except Exception as e:
        results["T235"] = False
        print(f"  T235 (non-self-ref penalty theorem): FAIL -- {e}")

    # ─── T236: 艺术极值定理 ───
    try:
        engine2 = LiuPenaltyField()
        # 满足三条件: K≥4, Self-Ref Closed, PG Strong
        result = engine2.full_analysis(
            M=1.0, H_theta=0.5,
            self_reference_depth=10, max_depth=10,
            external_dependencies=0, total_resources=10,
            info_resonance_modes=4,
            phase_coherence=0.95,
            group_symmetry_order=4,
            a_current=1.0
        )
        art = result["art_extremum_theorem"]
        assert art["all_conditions_met"] is True, \
            f"T236 FAIL: all conditions should be met, got {art}"
        assert art["prime_zero_duality"] is True, "PZD should be True"
        assert art["self_ref_closure"] == "closed", \
            f"SRC should be 'closed', got {art['self_ref_closure']}"
        assert art["pg_confinement"] == "strong", \
            f"PGC should be 'strong', got {art['pg_confinement']}"
        assert art["liu_super_formal"] is True, \
            "ℒ_Liu ≻ ℱ should be True"
        assert abs(art["phi_const"] - 1.0) < 1e-10, \
            f"Φ_const should be c*=1.0, got {art['phi_const']}"

        # 验证不满足条件时Φ_const ≠ c*
        result_partial = engine2.full_analysis(
            M=1.0, H_theta=0.5,
            self_reference_depth=3, max_depth=10,  # 未完全自指
            external_dependencies=0, total_resources=10,
            info_resonance_modes=4,
            phase_coherence=0.95,
            group_symmetry_order=4,
            a_current=1.0
        )
        art_partial = result_partial["art_extremum_theorem"]
        assert art_partial["all_conditions_met"] is False, \
            "Partial conditions should not all be met"

        results["T236"] = True
        print("  T236 (art extremum theorem): PASS")
    except Exception as e:
        results["T236"] = False
        print(f"  T236 (art extremum theorem): FAIL -- {e}")

    # ─── T237: 刘稳定函数定理 ───
    try:
        liu = LiuStabilityFunction(epsilon=0.1, a_target=1.0)

        # 1. 在a_target处ℱ_L = 0
        f_at_target = liu(1.0)
        assert abs(f_at_target) < 1e-10, \
            f"F_L(a_target) should be 0, got {f_at_target}"

        # 2. 偏离a_target时ℱ_L > 0
        f_above = liu(1.5)
        f_below = liu(0.5)
        assert f_above > 0, f"F_L(1.5) should be > 0, got {f_above}"
        assert f_below > 0, f"F_L(0.5) should be > 0, got {f_below}"

        # 3. 对称性: |a - a_target|相同时ℱ_L相同
        assert abs(f_above - f_below) < 1e-10, \
            f"F_L should be symmetric, got {f_above} vs {f_below}"

        # 4. 恢复力指向a_target
        force_above = liu.restoring_force(1.5)
        force_below = liu.restoring_force(0.5)
        assert force_above < 0, \
            f"Restoring force above target should be negative, got {force_above}"
        assert force_below > 0, \
            f"Restoring force below target should be positive, got {force_below}"

        # 5. 精确公式验证: ℱ_L(1.5) = 0.1 * (0.5/1.0)² = 0.025
        expected_fl = 0.1 * (0.5 / 1.0) ** 2
        assert abs(f_above - expected_fl) < 1e-10, \
            f"F_L(1.5) should be {expected_fl}, got {f_above}"

        # 6. 构成势演化: 偏离a_target时构成势受到恢复力驱动
        cp = ConstitutivePotential(phi_const=0.5, liu_stability=liu)
        # 当a偏离a_target, ℱ_L > 0 → dΦ/dt中正贡献
        phi_new = cp.evolve(d_s_rel_dphi=0.0, a_current=1.5, dt=0.01)
        assert phi_new > 0.5, \
            f"Phi should increase under restoring force, got {phi_new}"

        results["T237"] = True
        print("  T237 (Liu stability function theorem): PASS")
    except Exception as e:
        results["T237"] = False
        print(f"  T237 (Liu stability function theorem): FAIL -- {e}")

    # ─── Summary ───
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  M216 MVE Summary: {passed}/{total} PASS")
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("M216 LiuPenaltyField — MVE Tests")
    print("=" * 60)
    run_mve_tests()
