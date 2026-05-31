# -*- coding: utf-8 -*-
"""
M209: AmbiguityEngine — 歧义保留+延迟坍缩+L5投影引擎

基于复合体理学「歧义即显化」核心实现:
  - G_ambig 歧义自同构群: 保Rel结构但交换解读朝向
  - L5投影多值性定理 (Thm4.1): |Im(O_L5)| >= |G_ambig| >= 2
  - 歧义非缺陷推论 (Cor4.1): 歧义!=缺陷, 需外源L4才可坍缩
  - 延迟坍缩: 保留歧义不急于消歧, 仅当θ_context给定时经Π̂_φ锁定

核心定理:
  Thm4.1 — L5投影多值性定理:
    G_ambig非平凡 ∧ P(θ_obs)非δ函数 → |Im(O_L5)| >= |G_ambig| >= 2
  Cor4.1 — 歧义非缺陷推论:
    歧义图多值读!=图像信息不足 → 本质是Rel含G_ambig且观测者参与未完成

依赖: M208 TianxingPhaseLock (天行相位选择)

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
import random
import sys
import os
# 确保项目根目录在sys.path中（直接运行时）
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Callable, Tuple
from enum import Enum

from modules.M208_TianxingPhaseLock import (
    PhaseSelector, PhaseLockResult, UndeterminedState, WaveParticleState
)


# ═══════════════════════════════════════════════════════════════
# §1 歧义自同构群 G_ambig
# ═══════════════════════════════════════════════════════════════

class AmbiguityKind(Enum):
    """歧义类型"""
    SPATIAL = "spatial"         # 空间歧义(如Necker立方体)
    DIRECTIONAL = "directional"  # 方向歧义(如猫台阶上楼/下楼)
    SEMANTIC = "semantic"        # 语义歧义(如多义词)
    FIGURAL = "figural"         # 图底歧义(如Rubin花瓶)
    TEMPORAL = "temporal"        # 时序歧义(如因果方向)


@dataclass
class AmbiguityAutomorphism:
    """
    歧义自同构 g ∈ G_ambig

    保Rel结构但交换解读朝向
    实例: 猫台阶图 G_ambig = {id, r_vert} ≅ Z_2
    """
    name: str                          # 自同构名称(如'vertical_flip')
    source_reading: str                # 原始解读(如'up')
    target_reading: str                # 交换后解读(如'down')
    kind: AmbiguityKind = AmbiguityKind.DIRECTIONAL
    phase_shift: float = 0.0           # 对应的相位偏移(θ→θ+π等)

    def apply(self, reading: str) -> str:
        """应用自同构: 如果reading匹配source, 返回target"""
        if reading == self.source_reading:
            return self.target_reading
        return reading

    def inverse(self) -> 'AmbiguityAutomorphism':
        """逆自同构"""
        return AmbiguityAutomorphism(
            name=f"{self.name}_inv",
            source_reading=self.target_reading,
            target_reading=self.source_reading,
            kind=self.kind,
            phase_shift=-self.phase_shift,
        )


class AmbiguityGroup:
    """
    歧义自同构群 G_ambig ⊂ Aut(Rel)

    性质:
      - |G_ambig| > 1 → L5多值(歧义)
      - |G_ambig| = 1 → L5单值(无歧义)
      - 猫台阶图: G_ambig = {id, r_vert} ≅ Z_2, |G|=2

    由Thm4.1:
      G_ambig保Rel结构 → ∀g∈G_ambig, Γ(Rel,θ) = Γ(Rel,g·θ)结构同
      π_L5丢失G_ambig内部区别 → 同Rel可投影为多L5像
    """

    def __init__(self, name: str = "G_ambig"):
        self.name = name
        self.elements: List[AmbiguityAutomorphism] = []
        self._identity_added = False

    def add_identity(self):
        """添加恒等自同构"""
        if not self._identity_added:
            self.elements.insert(0, AmbiguityAutomorphism(
                name="id", source_reading="*", target_reading="*",
                phase_shift=0.0
            ))
            self._identity_added = True

    def add_automorphism(self, auto: AmbiguityAutomorphism):
        """添加歧义自同构"""
        if not self._identity_added:
            self.add_identity()
        self.elements.append(auto)

    @property
    def order(self) -> int:
        """群的阶 |G_ambig|"""
        return len(self.elements)

    @property
    def is_trivial(self) -> bool:
        """是否平凡群(|G|=1)"""
        return self.order <= 1

    @property
    def is_nontrivial(self) -> bool:
        """是否非平凡群(|G|>1) — L5多值的必要条件"""
        return self.order > 1

    def orbit(self, reading: str) -> Set[str]:
        """计算reading在G_ambig作用下的轨道"""
        orbit_set = {reading}
        for g in self.elements:
            orbit_set.add(g.apply(reading))
        return orbit_set

    def l5_projection_cardinality(self) -> int:
        """
        L5投影多值性 (Thm4.1推论):
          |Im(O_L5)| >= |G_ambig| >= 2 (当G_ambig非平凡)
        """
        if self.is_nontrivial:
            return max(2, self.order)
        return 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "order": self.order,
            "is_nontrivial": self.is_nontrivial,
            "l5_cardinality": self.l5_projection_cardinality(),
            "elements": [{"name": e.name, "src": e.source_reading, "tgt": e.target_reading}
                         for e in self.elements],
        }


# ═══════════════════════════════════════════════════════════════
# §2 L5投影多值性
# ═══════════════════════════════════════════════════════════════

@dataclass
class L5Projection:
    """
    L5观测量 O_L5 = π_L5 ∘ Γ(Rel, θ_obs)

    Thm4.1: 若G_ambig非平凡且P(θ_obs)非δ函数 → |Im(O_L5)| >= 2

    五层次定义:
      L1: 全关系未剖分自指(含所有可能解读叠加)
      L2: EML相位锁定(选透视但留G_ambig)
      L3: β-归约步(像素矩阵逐行扫描)
      L4: 观测者参与(θ_obs, 文化图式, 文字暗示)
      L5: 显化现象(主观报告, 可测输出)
    """
    rel_id: str                            # 关系实在标识
    g_ambig: AmbiguityGroup = field(default_factory=AmbiguityGroup)
    theta_obs: float = 0.0                 # 观测者相位
    is_delta_locked: bool = False          # P(θ_obs)是否δ函数(预先单锁定)
    readings: List[str] = field(default_factory=list)

    def compute_projection(self) -> Dict[str, Any]:
        """
        计算L5投影

        逻辑:
          1. 检查G_ambig是否非平凡
          2. 检查P(θ_obs)是否δ函数
          3. 若G非平凡且非δ锁定 → 多值投影
          4. 若δ锁定 → 单值坍缩
        """
        if self.g_ambig.is_trivial:
            # 平凡群: 单值读
            return {
                "rel_id": self.rel_id,
                "cardinality": 1,
                "readings": self.readings[:1] if self.readings else ["unique"],
                "is_multivalued": False,
                "reason": "G_ambig trivial",
            }

        if self.is_delta_locked:
            # δ锁定: 单值坍缩(外源L4已完成相位选择)
            return {
                "rel_id": self.rel_id,
                "cardinality": 1,
                "readings": self.readings[:1] if self.readings else ["locked"],
                "is_multivalued": False,
                "reason": "delta-locked (L4 completed)",
            }

        # 多值投影: |Im(O_L5)| >= |G_ambig| >= 2
        cardinality = self.g_ambig.l5_projection_cardinality()
        orbit = self.g_ambig.orbit(self.readings[0] if self.readings else "default")
        readings = list(orbit) if orbit else self.readings

        return {
            "rel_id": self.rel_id,
            "cardinality": cardinality,
            "readings": readings[:cardinality],
            "is_multivalued": True,
            "reason": "G_ambig nontrivial + P(θ_obs) not delta",
        }


# ═══════════════════════════════════════════════════════════════
# §3 歧义引擎主类
# ═══════════════════════════════════════════════════════════════

class AmbiguityEngine:
    """
    歧义引擎 — M209主类

    核心原则: 歧义不是缺陷, 而是Rel含G_ambig的显化
    延迟坍缩: 保留歧义不急于消歧, 仅当θ_context给定时经Π̂_φ锁定

    Cor4.1 (歧义非缺陷推论):
      "图中必有唯一正确答案"是朴素实体实在论误判(L5→L1错误溯因)
      歧义图多值读≠图像信息不足 → 本质是Rel含G_ambig且观测者参与未完成

    对接M191 BetaRewireEngine:
      歧义检测→ΔPsi→β-rewire审计链
    """

    def __init__(self, noise_level: float = 0.05):
        self.phase_selector = PhaseSelector(noise_level)
        self.ambiguity_groups: Dict[str, AmbiguityGroup] = {}
        self.projections: List[L5Projection] = []
        self.collapse_log: List[Dict] = []

    def register_ambiguity(self, rel_id: str,
                           automorphisms: List[AmbiguityAutomorphism]) -> AmbiguityGroup:
        """
        注册歧义关系

        Args:
            rel_id: 关系实在标识
            automorphisms: 歧义自同构列表

        Returns:
            AmbiguityGroup: 构建的歧义群
        """
        group = AmbiguityGroup(name=f"G_ambig_{rel_id}")
        for auto in automorphisms:
            group.add_automorphism(auto)
        self.ambiguity_groups[rel_id] = group
        return group

    def retain_ambiguity(self, rel_id: str,
                         readings: List[str]) -> L5Projection:
        """
        保留歧义 — 延迟坍缩

        不急于消歧, 显式保留G_ambig,
        仅当任务上下文给θ_context才经Π̂_φ锁定

        Args:
            rel_id: 关系实在标识
            readings: 可能的解读列表

        Returns:
            L5Projection: 多值投影结果
        """
        group = self.ambiguity_groups.get(rel_id, AmbiguityGroup())
        proj = L5Projection(
            rel_id=rel_id,
            g_ambig=group,
            theta_obs=0.0,
            is_delta_locked=False,
            readings=readings,
        )
        self.projections.append(proj)
        return proj

    def collapse_with_context(self, rel_id: str,
                              theta_context: float) -> Dict[str, Any]:
        """
        上下文坍缩 — 经Π̂_φ锁定

        仅当任务上下文给出θ_context时:
          1. 构建未判读态 |ψ_undetermined⟩
          2. 应用Π̂_φ(θ_context) → |locked⟩
          3. 记录坍缩结果

        Args:
            rel_id: 关系实在标识
            theta_context: L4上下文相位
                0 → 暗示'上楼'
                π → 暗示'下楼'

        Returns:
            坍缩结果字典
        """
        group = self.ambiguity_groups.get(rel_id, AmbiguityGroup())

        # 构建未判读态
        state = UndeterminedState(theta_expect=theta_context)

        # 应用相位选择
        result = self.phase_selector.wave_to_particle(state, theta_context)

        # 记录坍缩
        collapse_entry = {
            "rel_id": rel_id,
            "theta_context": round(theta_context, 4),
            "result": result.value,
            "g_ambig_order": group.order,
            "was_multivalued": group.is_nontrivial,
        }
        self.collapse_log.append(collapse_entry)

        return collapse_entry

    def l5_projection_cardinality(self, rel_id: str) -> int:
        """
        L5投影多值性 (Thm4.1)

        |Im(O_L5)| >= |G_ambig| >= 2 (当G_ambig非平凡)
        """
        group = self.ambiguity_groups.get(rel_id)
        if group is None:
            return 1
        return group.l5_projection_cardinality()

    def is_ambiguity_not_flaw(self, rel_id: str) -> bool:
        """
        歧义非缺陷判定 (Cor4.1)

        歧义图多值读≠缺陷 → 本质是Rel含G_ambig且观测者参与未完成
        """
        group = self.ambiguity_groups.get(rel_id)
        if group is None:
            return False
        return group.is_nontrivial

    def get_state(self) -> Dict[str, Any]:
        """返回引擎状态"""
        return {
            "registered_rels": len(self.ambiguity_groups),
            "projections_count": len(self.projections),
            "collapse_count": len(self.collapse_log),
            "ambiguity_groups": {
                rid: g.to_dict() for rid, g in self.ambiguity_groups.items()
            },
        }


# ═══════════════════════════════════════════════════════════════
# §4 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t209_l5_multivaluedness() -> bool:
    """
    T209: L5投影多值性定理 (Thm4.1)

    验证: G_ambig非平凡 → Im(O_L5) >= 2
    """
    engine = AmbiguityEngine()

    # 注册猫台阶图歧义
    engine.register_ambiguity("cat_stair", [
        AmbiguityAutomorphism("vertical_flip", "up", "down",
                             AmbiguityKind.DIRECTIONAL, math.pi),
    ])

    # 保留歧义(延迟坍缩)
    proj = engine.retain_ambiguity("cat_stair", ["up", "down"])

    # L5投影应多值
    l5_result = proj.compute_projection()

    # 验证: |Im(O_L5)| >= 2
    if not l5_result["is_multivalued"]:
        return False
    if l5_result["cardinality"] < 2:
        return False

    # 验证: card = l5_projection_cardinality
    card = engine.l5_projection_cardinality("cat_stair")
    if card < 2:
        return False

    # 对比: 无歧义的情况(平凡G_ambig)
    engine.register_ambiguity("stop_sign", [])  # 无自同构
    proj_unique = engine.retain_ambiguity("stop_sign", ["stop"])
    l5_unique = proj_unique.compute_projection()
    if l5_unique["is_multivalued"]:
        return False  # 平凡群不应多值

    return True


def _test_t210_ambiguity_not_flaw() -> bool:
    """
    T210: 歧义非缺陷推论 (Cor4.1)

    验证: 歧义≠缺陷, 需外源L4才可坍缩
    """
    engine = AmbiguityEngine()

    # 注册歧义关系
    engine.register_ambiguity("necker_cube", [
        AmbiguityAutomorphism("orientation_flip", "front_up", "front_down",
                             AmbiguityKind.SPATIAL, math.pi),
    ])

    # 歧义非缺陷判定
    if not engine.is_ambiguity_not_flaw("necker_cube"):
        return False

    # 无上下文时: 歧义保留(延迟坍缩)
    proj = engine.retain_ambiguity("necker_cube", ["front_up", "front_down"])
    l5 = proj.compute_projection()
    if not l5["is_multivalued"]:
        return False  # 应保留歧义

    # 有上下文(θ=0): 坍缩到|up⟩
    collapse_up = engine.collapse_with_context("necker_cube", 0.0)
    # 应偏向up
    up_collapses = sum(1 for c in engine.collapse_log if c["result"] == "up")

    # 有上下文(θ=π): 坍缩到|down⟩
    engine.collapse_with_context("necker_cube", math.pi)
    down_collapses = sum(1 for c in engine.collapse_log if c["result"] == "down")

    # 至少有一种坍缩结果
    return (up_collapses > 0 or down_collapses > 0) and engine.is_ambiguity_not_flaw("necker_cube")


def run_mve() -> Dict[str, bool]:
    """
    M209 MVE验证

    T209: L5投影多值性定理(Thm4.1)
    T210: 歧义非缺陷推论(Cor4.1)
    """
    results = {}

    print("=" * 60)
    print("M209 AmbiguityEngine — MVE Verification")
    print("=" * 60)

    # T209
    try:
        t209 = _test_t209_l5_multivaluedness()
        status = "PASS" if t209 else "FAIL"
        print(f"  T209 (L5投影多值性): {status}")
        results["T209"] = t209
    except Exception as e:
        print(f"  T209 (L5投影多值性): ERROR — {e}")
        results["T209"] = False

    # T210
    try:
        t210 = _test_t210_ambiguity_not_flaw()
        status = "PASS" if t210 else "FAIL"
        print(f"  T210 (歧义非缺陷): {status}")
        results["T210"] = t210
    except Exception as e:
        print(f"  T210 (歧义非缺陷): ERROR — {e}")
        results["T210"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M209 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
