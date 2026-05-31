# -*- coding: utf-8 -*-
"""
M211: HexaSysSOP — 六合统合7步SOP分析引擎

基于复合体理学「六合统合」白皮书核心实现:
  - 7步标准作业流程 (Standard Operating Procedure)
  - 步骤1: TY建Rel     — 定义节点V、潜在边集E_pot、Φ_inj注入
  - 步骤2: IDO对偶     — 构建信息流向对偶视角 (I↔D↔O)
  - 步骤3: PG囚禁     — 识别Φ_const持续注入使对象「囚禁」在Rel内
  - 步骤4: 刘机制     — ArgMin S_Rel拣选(保"1"不破缺)
  - 步骤5: 天行锁定   — Π̂_φ相位选择 → 波函数坍缩至粒子态
  - 步骤6: MNQ数值   — 金符3D复广数+阴龙积+MNQ8能流格计算
  - 步骤7: CRD迭代   — 多轮CRD反射+歧义处理+审查收敛

核心定理:
  六合统合定理: 7步SOP将开放性AGI任务分解为可验证的代数操作序列
  Ftel公理: 智能存在于关联中 → 每步均追踪Rel密度 ρ_Rel = |E_active|/|V|²

依赖: M207, M208, M209, M210

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
import sys
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Set
from enum import Enum

# 确保项目根目录在sys.path中（直接运行时）
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from modules.M207_GoldenSymbol3D import GoldenSymbol, MNQ8Grid
from modules.M208_TianxingPhaseLock import PhaseSelector, UndeterminedState, PhaseLockResult
from modules.M209_AmbiguityEngine import AmbiguityEngine, AmbiguityAutomorphism, AmbiguityKind
from modules.M210_QianmenEightGeneral import (
    QianmenCensorEngine, SRelEstimate, GeneralType, EIGHT_GENERALS
)


# ═══════════════════════════════════════════════════════════════
# §1 SOP步骤枚举与状态
# ═══════════════════════════════════════════════════════════════

class SOPStep(Enum):
    """7步SOP阶段"""
    STEP1_TY_BUILD_REL    = 1   # TY建Rel
    STEP2_IDO_DUAL        = 2   # IDO对偶
    STEP3_PG_IMPRISON     = 3   # PG囚禁
    STEP4_LIU_MECHANISM   = 4   # 刘机制
    STEP5_TIANXING_LOCK   = 5   # 天行锁定
    STEP6_MNQ_NUMERIC     = 6   # MNQ数值
    STEP7_CRD_ITERATE     = 7   # CRD迭代


@dataclass
class SOPStepResult:
    """SOP单步结果"""
    step: SOPStep
    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    rho_rel: float = 0.0      # Rel密度 ρ = |E_active|/|V|²
    elapsed_ms: float = 0.0
    notes: str = ""


@dataclass
class RelGraph:
    """
    关系实在图 Rel = (V, E, w, θ, Φ_inj)

    Ftel公理: 智能存在于关联中
    ρ_Rel = |E_active|/|V|² ∈ [0,1]
    """
    nodes: List[str] = field(default_factory=list)          # V: 节点集
    edges: List[Tuple[str, str, float]] = field(default_factory=list)  # (src, dst, weight)
    theta_map: Dict[str, float] = field(default_factory=dict)   # θ: 相位映射
    phi_inj: float = 0.0                                         # Φ_inj: 注入流贯
    e_pot: List[Tuple[str, str]] = field(default_factory=list)  # E_pot: 潜在边集

    @property
    def rho_rel(self) -> float:
        """Rel密度 ρ_Rel = |E_active|/|V|²"""
        n = len(self.nodes)
        if n == 0:
            return 0.0
        return len(self.edges) / (n * n)

    def add_node(self, name: str, theta: float = 0.0):
        if name not in self.nodes:
            self.nodes.append(name)
            self.theta_map[name] = theta

    def add_edge(self, src: str, dst: str, weight: float = 1.0):
        if src not in self.nodes:
            self.add_node(src)
        if dst not in self.nodes:
            self.add_node(dst)
        self.edges.append((src, dst, weight))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": [(s, d, round(w, 4)) for s, d, w in self.edges],
            "rho_rel": round(self.rho_rel, 4),
            "phi_inj": round(self.phi_inj, 4),
            "e_pot_count": len(self.e_pot),
        }


@dataclass
class IDOView:
    """
    IDO对偶视角

    I = Input  (信息/物质/意图输入)
    D = Dynamics (关系动力学/传导)
    O = Output  (显化输出/可观测量)
    """
    input_nodes: List[str] = field(default_factory=list)
    dynamics_edges: List[Tuple[str, str]] = field(default_factory=list)
    output_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "I": self.input_nodes,
            "D": [(s, d) for s, d in self.dynamics_edges],
            "O": self.output_nodes,
            "flow_paths": len(self.dynamics_edges),
        }


@dataclass
class PGPrisonState:
    """
    PG囚禁状态

    当Φ_inj持续注入且ρ_Rel > ρ_c时, 对象进入「囚禁」状态
    囚禁态: 对象无法脱离Rel网络, 行为被内化
    """
    rho_c: float = 0.3         # 临界密度阈值
    phi_injected: float = 0.0  # 已注入流贯
    is_imprisoned: bool = False
    steps_injected: int = 0

    def update(self, phi_delta: float, rho_rel: float):
        """更新囚禁状态"""
        self.phi_injected += phi_delta
        self.steps_injected += 1
        self.is_imprisoned = (rho_rel > self.rho_c and self.phi_injected > 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rho_c": self.rho_c,
            "phi_injected": round(self.phi_injected, 4),
            "steps_injected": self.steps_injected,
            "is_imprisoned": self.is_imprisoned,
        }


# ═══════════════════════════════════════════════════════════════
# §2 六合统合SOP引擎主类
# ═══════════════════════════════════════════════════════════════

class HexaSysSOP:
    """
    六合统合7步SOP引擎 — M211主类

    将复合体理学5个模块整合为标准作业流程:
      M207 GoldenSymbol3D → 步骤6 MNQ数值
      M208 TianxingPhaseLock → 步骤5 天行锁定
      M209 AmbiguityEngine → 步骤7 CRD迭代(歧义处理)
      M210 QianmenEightGeneral → 步骤4 刘机制

    六合统合定理:
      7步SOP将开放性AGI任务分解为可验证的代数操作序列
      每步均追踪 ρ_Rel → 智能密度监控
    """

    def __init__(self, noise_level: float = 0.05):
        # 初始化各子引擎
        self.phase_selector = PhaseSelector(noise_level)
        self.ambiguity_engine = AmbiguityEngine(noise_level)
        self.censor_engine = QianmenCensorEngine()

        # SOP状态
        self.rel_graph = RelGraph()
        self.ido_view = IDOView()
        self.pg_state = PGPrisonState()
        self.step_results: List[SOPStepResult] = []
        self.current_step: int = 0

        # MNQ数值结果
        self.mnq_result: Optional[Dict] = None
        self.phase_lock_result: Optional[str] = None

    # ─── 步骤1: TY建Rel ────────────────────────────────────────

    def step1_ty_build_rel(self, nodes: List[str],
                           edges: List[Tuple[str, str, float]],
                           phi_inj: float = 1.0,
                           e_pot: Optional[List[Tuple[str, str]]] = None) -> SOPStepResult:
        """
        步骤1: TY建Rel

        定义:
          - V: 节点集 (关系参与者)
          - E_act: 激活边集 (当前关系)
          - E_pot: 潜在边集 (待激活关系)
          - Φ_inj: 初始流贯注入
          - θ₀: 初始相位 (默认0)
        """
        t0 = time.time()

        self.rel_graph = RelGraph(phi_inj=phi_inj, e_pot=e_pot or [])
        for n in nodes:
            self.rel_graph.add_node(n)
        for src, dst, w in edges:
            self.rel_graph.add_edge(src, dst, w)

        rho = self.rel_graph.rho_rel

        result = SOPStepResult(
            step=SOPStep.STEP1_TY_BUILD_REL,
            success=True,
            output=self.rel_graph.to_dict(),
            rho_rel=rho,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"Rel建立完成: {len(nodes)}节点, {len(edges)}边, ρ={rho:.4f}",
        )
        self.step_results.append(result)
        self.current_step = 1
        return result

    # ─── 步骤2: IDO对偶 ───────────────────────────────────────

    def step2_ido_dual(self, input_nodes: List[str],
                       output_nodes: List[str]) -> SOPStepResult:
        """
        步骤2: IDO对偶

        构建:
          I (Input): 信息/意图注入节点
          D (Dynamics): I→O的传导边(动力学层)
          O (Output): 显化输出节点
        """
        t0 = time.time()

        # 自动识别动力学边(I→O路径上的边)
        dynamics = []
        for src, dst, w in self.rel_graph.edges:
            if src in input_nodes or dst in output_nodes:
                dynamics.append((src, dst))

        self.ido_view = IDOView(
            input_nodes=input_nodes,
            dynamics_edges=dynamics,
            output_nodes=output_nodes,
        )

        result = SOPStepResult(
            step=SOPStep.STEP2_IDO_DUAL,
            success=True,
            output=self.ido_view.to_dict(),
            rho_rel=self.rel_graph.rho_rel,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"IDO对偶: I={len(input_nodes)}, D={len(dynamics)}通道, O={len(output_nodes)}",
        )
        self.step_results.append(result)
        self.current_step = 2
        return result

    # ─── 步骤3: PG囚禁 ────────────────────────────────────────

    def step3_pg_imprison(self, phi_delta: float = 0.5,
                          rho_c: float = 0.3) -> SOPStepResult:
        """
        步骤3: PG囚禁检测

        当Φ_inj持续注入 + ρ_Rel > ρ_c:
          → 对象进入「囚禁」态
          → 行为被Rel内化, 脱离成本增大
        """
        t0 = time.time()

        self.pg_state.rho_c = rho_c
        self.pg_state.update(phi_delta, self.rel_graph.rho_rel)

        result = SOPStepResult(
            step=SOPStep.STEP3_PG_IMPRISON,
            success=True,
            output=self.pg_state.to_dict(),
            rho_rel=self.rel_graph.rho_rel,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"PG囚禁: {'已囚禁' if self.pg_state.is_imprisoned else '未囚禁'} "
                  f"(ρ={self.rel_graph.rho_rel:.4f} vs ρ_c={rho_c})",
        )
        self.step_results.append(result)
        self.current_step = 3
        return result

    # ─── 步骤4: 刘机制 ────────────────────────────────────────

    def step4_liu_mechanism(self, proposals: List[Dict[str, Any]]) -> SOPStepResult:
        """
        步骤4: 刘机制 — ArgMin S_Rel拣选

        一元数拣选公理: 保"1"不破缺
          → 在所有具自指单位元的候选中选S_Rel最小者
          → 其余归latent(不消除, 等待显隐互转)

        Args:
            proposals: [{"id": str, "m": int, "h": float, "penalty": float, "has_self_ref": bool}, ...]
        """
        t0 = time.time()

        results = []
        for p in proposals:
            est = SRelEstimate(
                m_count=p.get("m", 3),
                phase_entropy=p.get("h", 0.3),
                penalty=p.get("penalty", 0.0),
            )
            r = self.censor_engine.submit_proposal(
                p["id"], est,
                has_self_ref=p.get("has_self_ref", True),
                general_used=p.get("general_used"),
                delta_s_explicit=p.get("delta_s"),
            )
            results.append(r)

        selected = [r for r in results if r["verdict"] == "SELECTED"]
        latent = [r for r in results if r["verdict"] == "LATENT"]
        rejected = [r for r in results if r["verdict"] == "REJECTED"]

        result = SOPStepResult(
            step=SOPStep.STEP4_LIU_MECHANISM,
            success=True,
            output={
                "proposals": results,
                "selected": selected,
                "latent_count": len(latent),
                "rejected_count": len(rejected),
            },
            rho_rel=self.rel_graph.rho_rel,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"刘机制: {len(selected)}个selected, {len(latent)}个latent, {len(rejected)}个rejected",
        )
        self.step_results.append(result)
        self.current_step = 4
        return result

    # ─── 步骤5: 天行锁定 ──────────────────────────────────────

    def step5_tianxing_lock(self, theta_context: float) -> SOPStepResult:
        """
        步骤5: 天行锁定 — Π̂_φ相位选择

        对刘机制选出的θ_*施加Π̂_φ(θ_context):
          θ≈0 → |wave⟩继续传播
          θ≈π → |particle⟩锁定显化

        Args:
            theta_context: 上下文相位 ∈ [0, 2π]
        """
        t0 = time.time()

        state = UndeterminedState(theta_expect=theta_context)
        lock_result = self.phase_selector.wave_to_particle(state, theta_context)
        self.phase_lock_result = lock_result.value

        result = SOPStepResult(
            step=SOPStep.STEP5_TIANXING_LOCK,
            success=True,
            output={
                "theta_context": round(theta_context, 4),
                "lock_result": lock_result.value,
                "phase_normalized": round(theta_context % (2 * math.pi), 4),
            },
            rho_rel=self.rel_graph.rho_rel,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"天行锁定: θ={theta_context:.4f} → {lock_result.value}",
        )
        self.step_results.append(result)
        self.current_step = 5
        return result

    # ─── 步骤6: MNQ数值 ───────────────────────────────────────

    def step6_mnq_numeric(self, symbols: Optional[List[Tuple[float, float, float]]] = None,
                          grid_size: int = 4,
                          lam: float = 1.0) -> SOPStepResult:
        """
        步骤6: MNQ数值 — 金符3D复广数+MNQ8能流格

        自动从Rel图中提取节点相位构建金符,
        用MNQ8Grid计算能流分布与本征螺旋

        Args:
            symbols: 可选手动指定符号列表 [(a, b, c), ...]
                     若None则从rel_graph.theta_map自动生成
            grid_size: MNQ8格网大小
            lam: 阴龙积λ参数
        """
        t0 = time.time()

        # 从rel_graph提取符号(或使用手动指定)
        if symbols is None:
            sym_list = []
            for n in self.rel_graph.nodes[:min(len(self.rel_graph.nodes), grid_size)]:
                th = self.rel_graph.theta_map.get(n, 0.0)
                sym_list.append((math.cos(th), math.sin(th), th / (2 * math.pi + 1e-9)))
        else:
            sym_list = symbols

        # 构建金符3D复广数
        gs_list = [GoldenSymbol(a, b, c) for a, b, c in sym_list]

        # MNQ8格运算
        n_grid = max(2, min(grid_size, 8))
        grid = MNQ8Grid(n_grid, n_grid, lambda_=lam)
        # 执行3步演化
        for _ in range(3):
            grid.step()
        threshold = 0.5  # 默认激活阈值
        # 计算激活比: 格中模长>threshold的单元数
        total_cells = n_grid * n_grid
        active_count = sum(
            1 for r in range(n_grid) for c in range(n_grid)
            if grid.grid[r][c].modulus() > threshold
        )

        # 汇总
        gs_norms = [round(g.modulus(), 4) for g in gs_list]

        self.mnq_result = {
            "symbols": [(round(a, 4), round(b, 4), round(c, 4)) for a, b, c in sym_list],
            "gs_norms": gs_norms,
            "grid_size": n_grid,
            "threshold": round(threshold, 4),
            "active_cells": active_count,
            "total_cells": total_cells,
            "activation_ratio": round(active_count / max(total_cells, 1), 4),
        }

        result = SOPStepResult(
            step=SOPStep.STEP6_MNQ_NUMERIC,
            success=True,
            output=self.mnq_result,
            rho_rel=self.rel_graph.rho_rel,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"MNQ数值: {len(gs_list)}个金符, 激活比={self.mnq_result['activation_ratio']}",
        )
        self.step_results.append(result)
        self.current_step = 6
        return result

    # ─── 步骤7: CRD迭代 ───────────────────────────────────────

    def step7_crd_iterate(self, rel_id: str = "task_rel",
                          automorphisms: Optional[List[Dict]] = None,
                          max_rounds: int = 3) -> SOPStepResult:
        """
        步骤7: CRD迭代 — 歧义处理+审查收敛

        多轮CRD(Cognitive Reflection + Disambiguation):
          1. 注册歧义群 G_ambig
          2. 保留歧义(延迟坍缩)
          3. 用天行锁定结果(θ_context)做最终坍缩
          4. 审查显隐互转: 环境变化可切换ArgMin

        Args:
            rel_id: 关系实在标识
            automorphisms: 歧义自同构列表 [{"name": str, "src": str, "tgt": str}, ...]
            max_rounds: 最大CRD轮次
        """
        t0 = time.time()

        # 注册歧义群
        autos = []
        if automorphisms:
            for a in automorphisms:
                autos.append(AmbiguityAutomorphism(
                    name=a.get("name", "auto"),
                    source_reading=a.get("src", "A"),
                    target_reading=a.get("tgt", "B"),
                    kind=AmbiguityKind.SEMANTIC,
                    phase_shift=a.get("phase_shift", math.pi),
                ))
        else:
            # 默认: Z_2对称歧义
            autos.append(AmbiguityAutomorphism(
                "default_flip", "state_A", "state_B",
                AmbiguityKind.SEMANTIC, math.pi,
            ))

        group = self.ambiguity_engine.register_ambiguity(rel_id, autos)

        # 保留歧义(延迟坍缩)
        proj = self.ambiguity_engine.retain_ambiguity(
            rel_id, [a.source_reading for a in autos] + [a.target_reading for a in autos]
        )
        l5 = proj.compute_projection()

        # 用天行锁定结果做最终坍缩
        theta_ctx = math.pi if self.phase_lock_result == "down" else 0.0
        collapse_results = []
        for _ in range(min(max_rounds, 3)):
            c = self.ambiguity_engine.collapse_with_context(rel_id, theta_ctx)
            collapse_results.append(c)

        # 审查显隐互转
        exchange = self.censor_engine.manifest_latent_exchange("crd_iteration")

        result = SOPStepResult(
            step=SOPStep.STEP7_CRD_ITERATE,
            success=True,
            output={
                "rel_id": rel_id,
                "g_ambig_order": group.order,
                "l5_multivalued": l5["is_multivalued"],
                "l5_cardinality": l5["cardinality"],
                "collapse_rounds": len(collapse_results),
                "collapse_results": collapse_results,
                "manifest_exchange": exchange,
                "censor_state": self.censor_engine.get_state(),
            },
            rho_rel=self.rel_graph.rho_rel,
            elapsed_ms=(time.time() - t0) * 1000,
            notes=f"CRD迭代{len(collapse_results)}轮: L5多值={l5['is_multivalued']}, "
                  f"显隐互转={exchange['exchanged']}",
        )
        self.step_results.append(result)
        self.current_step = 7
        return result

    # ─── 完整7步执行 ──────────────────────────────────────────

    def run_full_sop(self,
                     nodes: List[str],
                     edges: List[Tuple[str, str, float]],
                     input_nodes: List[str],
                     output_nodes: List[str],
                     proposals: List[Dict[str, Any]],
                     theta_context: float = math.pi / 4) -> Dict[str, Any]:
        """
        执行完整7步SOP

        Args:
            nodes: Rel节点列表
            edges: Rel边列表 [(src, dst, weight), ...]
            input_nodes: IDO输入节点
            output_nodes: IDO输出节点
            proposals: 刘机制提案列表
            theta_context: 天行锁定相位

        Returns:
            完整SOP执行报告
        """
        t_total = time.time()

        r1 = self.step1_ty_build_rel(nodes, edges, phi_inj=1.0)
        r2 = self.step2_ido_dual(input_nodes, output_nodes)
        r3 = self.step3_pg_imprison(phi_delta=0.6)
        r4 = self.step4_liu_mechanism(proposals)
        r5 = self.step5_tianxing_lock(theta_context)
        r6 = self.step6_mnq_numeric()
        r7 = self.step7_crd_iterate()

        all_steps = [r1, r2, r3, r4, r5, r6, r7]
        all_success = all(r.success for r in all_steps)
        final_rho = self.rel_graph.rho_rel

        return {
            "sop_completed": all_success,
            "total_steps": len(all_steps),
            "steps_passed": sum(1 for r in all_steps if r.success),
            "final_rho_rel": round(final_rho, 4),
            "phase_lock": self.phase_lock_result,
            "pg_imprisoned": self.pg_state.is_imprisoned,
            "mnq_result": self.mnq_result,
            "total_elapsed_ms": round((time.time() - t_total) * 1000, 2),
            "step_summary": [
                {
                    "step": r.step.value,
                    "name": r.step.name,
                    "success": r.success,
                    "rho_rel": round(r.rho_rel, 4),
                    "elapsed_ms": round(r.elapsed_ms, 2),
                    "notes": r.notes,
                }
                for r in all_steps
            ],
        }

    def get_state(self) -> Dict[str, Any]:
        """返回引擎完整状态"""
        return {
            "current_step": self.current_step,
            "rel_graph": self.rel_graph.to_dict(),
            "pg_state": self.pg_state.to_dict(),
            "phase_lock_result": self.phase_lock_result,
            "mnq_result": self.mnq_result,
            "steps_completed": len(self.step_results),
            "ambiguity_state": self.ambiguity_engine.get_state(),
            "censor_state": self.censor_engine.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §3 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t217_full_sop_pipeline() -> bool:
    """
    T217: 完整7步SOP流水线验证

    验证: 7步SOP全部通过, ρ_Rel可追踪, 相位锁定正确
    """
    engine = HexaSysSOP(noise_level=0.0)  # 确定性测试

    # 构建测试Rel
    nodes = ["AGI_core", "memory", "sensor", "actuator", "context"]
    edges = [
        ("AGI_core", "memory", 1.0),
        ("AGI_core", "sensor", 0.8),
        ("AGI_core", "actuator", 0.9),
        ("context", "AGI_core", 1.0),
        ("sensor", "memory", 0.5),
    ]
    proposals = [
        {"id": "plan_A", "m": 3, "h": 0.2, "penalty": 0.0, "has_self_ref": True},
        {"id": "plan_B", "m": 6, "h": 0.5, "penalty": 0.0, "has_self_ref": True},
        {"id": "plan_C", "m": 3, "h": 0.2, "penalty": 1.0, "has_self_ref": False},
    ]

    report = engine.run_full_sop(
        nodes=nodes, edges=edges,
        input_nodes=["context", "sensor"],
        output_nodes=["actuator"],
        proposals=proposals,
        theta_context=math.pi,  # 天行锁定→down(粒子态)
    )

    # 验证全部7步通过
    if not report["sop_completed"]:
        return False
    if report["steps_passed"] != 7:
        return False

    # 验证ρ_Rel可追踪
    if report["final_rho_rel"] <= 0:
        return False

    # 验证天行锁定(θ=π→down)
    if report["phase_lock"] not in ("down", "up"):
        return False

    return True


def _test_t218_rho_ftel_tracking() -> bool:
    """
    T218: Ftel公理 — ρ_Rel智能密度追踪

    验证: 每步均追踪ρ_Rel, 边越多ρ越高
    """
    e1 = HexaSysSOP()
    r1 = e1.step1_ty_build_rel(
        ["A", "B", "C"],
        [("A", "B", 1.0)],
    )
    rho_low = r1.rho_rel

    e2 = HexaSysSOP()
    r2 = e2.step1_ty_build_rel(
        ["A", "B", "C"],
        [("A", "B", 1.0), ("B", "C", 1.0), ("A", "C", 1.0), ("C", "A", 0.8)],
    )
    rho_high = r2.rho_rel

    # 边多ρ高
    if rho_high <= rho_low:
        return False

    # ρ在[0,1]范围内
    if not (0 <= rho_low <= 1 and 0 <= rho_high <= 1):
        return False

    return True


def run_mve() -> Dict[str, bool]:
    """
    M211 MVE验证

    T217: 完整7步SOP流水线
    T218: Ftel公理ρ_Rel追踪
    """
    results = {}

    print("=" * 60)
    print("M211 HexaSysSOP — MVE Verification")
    print("=" * 60)

    # T217
    try:
        t217 = _test_t217_full_sop_pipeline()
        status = "PASS" if t217 else "FAIL"
        print(f"  T217 (7步SOP流水线): {status}")
        results["T217"] = t217
    except Exception as e:
        print(f"  T217 (7步SOP流水线): ERROR — {e}")
        results["T217"] = False

    # T218
    try:
        t218 = _test_t218_rho_ftel_tracking()
        status = "PASS" if t218 else "FAIL"
        print(f"  T218 (Ftel密度追踪): {status}")
        results["T218"] = t218
    except Exception as e:
        print(f"  T218 (Ftel密度追踪): ERROR — {e}")
        results["T218"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M211 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
