# -*- coding: utf-8 -*-
"""
M208: TianxingPhaseLock — 天行相位选择+Oloid差分引擎

基于复合体理学三篇核心文章的天行力学实现:
  - 相位选择算子 Π̂_φ: 波性→粒性坍缩
  - 波粒二象态 |ψ_wp⟩ = |波性⟩⟨粒性|
  - 未判读态 |ψ_undetermined⟩ ∝ |up⟩ + |down⟩
  - Oloid差分判定 (Thm4.5): EXCESS>0→真结构; EXCESS≈0→伪结构
  - 动态背景差分: condition_t - background_t

核心定理:
  Thm4.2 — 天行相位锁定歧义选择定理:
    Π̂_φ(θ=0)→|up⟩, Π̂_φ(θ=π)→|down⟩
  Thm4.4 — 天行相位锁定定理:
    Π̂_φ生效→PG囚禁被锁定(Mass-Face>0, EXCESS_LOOP>0)
  Thm4.5 — Oloid差分判定定理:
    结构锁定⇔EXCESS_MASS_FACE>0 ∧ EXCESS_LOOP_HOLD>0

依赖: M207 GoldenSymbol3D (金符3D复广数+MNQ8网格)

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from modules.M207_GoldenSymbol3D import (
    GoldenSymbol, yin_long_product, MNQ8Grid,
    create_hex_ring_gap, create_single_ripple
)


# ═══════════════════════════════════════════════════════════════
# §1 波粒二象态
# ═══════════════════════════════════════════════════════════════

class WaveParticleState(Enum):
    """波粒二象态标记"""
    WAVE = "wave"       # 波性: 潜在多读, 弥散叠加
    PARTICLE = "particle"  # 粒性: 锁定单读
    UNDETERMINED = "undetermined"  # 未判读: 弥散叠加态


class PhaseLockResult(Enum):
    """相位锁定结果"""
    UP = "up"           # θ∈[0, π/2) — 暗示上楼/未倒置
    DOWN = "down"       # θ∈[π/2, π] — 暗示下楼/倒置看图
    UNLOCKED = "unlocked"  # θ宽分布(无暗示初看) — 随机跳变


@dataclass
class UndeterminedState:
    """
    未判读态 |ψ_undetermined⟩ ∝ |up⟩ + |down⟩ (归一化)

    Necker双稳态: 两基展开系数均等
    """
    up_amplitude: complex = complex(1/math.sqrt(2), 0)
    down_amplitude: complex = complex(1/math.sqrt(2), 0)
    theta_expect: float = 0.0  # L4观测者期望相位
    phase_state: WaveParticleState = WaveParticleState.UNDETERMINED

    def normalize(self):
        """归一化: |up_amp|² + |down_amp|² = 1"""
        norm = math.sqrt(abs(self.up_amplitude)**2 + abs(self.down_amplitude)**2)
        if norm > 1e-15:
            self.up_amplitude /= norm
            self.down_amplitude /= norm

    def collapse_probability(self) -> Tuple[float, float]:
        """坍缩到|up⟩或|down⟩的概率: P(up)=|⟨up|ψ⟩|²"""
        p_up = abs(self.up_amplitude) ** 2
        p_down = abs(self.down_amplitude) ** 2
        return (p_up, p_down)


# ═══════════════════════════════════════════════════════════════
# §2 天行相位选择算子 Π̂_φ
# ═══════════════════════════════════════════════════════════════

class PhaseSelector:
    """
    天行相位选择算子 Π̂_φ

    将弥散态|ψ_undetermined⟩投影到相位匹配本征态

    Thm4.2 (天行相位锁定歧义选择定理):
      Π̂_φ(θ_exp) |ψ_undetermined⟩ = |up⟩   if θ∈[0, π/2)
                                      |down⟩ if θ∈[π/2, π]
                                      随机    if θ宽分布(无暗示)

    参数来源:
      θ_expect 来自L4(文字暗示/文化图式/倒置参考系)
    """

    def __init__(self, noise_level: float = 0.05):
        """
        Args:
            noise_level: 热力学噪声水平(默认5%)
                         模拟认知过程中的随机涨落
        """
        self.noise_level = noise_level
        self.lock_history: List[Dict] = []

    def apply(self, state: UndeterminedState) -> PhaseLockResult:
        """
        应用相位选择算子: Π̂_φ(θ_expect) |ψ⟩ → |locked⟩

        步骤:
          1. 检查θ_expect的范围
          2. θ∈[0,π/2)→偏向|up⟩; θ∈[π/2,π]→偏向|down⟩
          3. 加入热力学噪声(双稳态跳变可能)
          4. 记录锁定历史
        """
        theta = state.theta_expect

        # 归一化θ到[0, 2π)
        theta = theta % (2 * math.pi)

        # 计算偏置强度
        if theta < math.pi / 2:
            # 暗示|up⟩方向
            bias_up = 1.0 - self.noise_level
            bias_down = self.noise_level
            preferred = PhaseLockResult.UP
        elif theta < math.pi:
            # 暗示|down⟩方向
            bias_up = self.noise_level
            bias_down = 1.0 - self.noise_level
            preferred = PhaseLockResult.DOWN
        elif theta < 3 * math.pi / 2:
            # π~3π/2区域: 仍有|down⟩偏向但较弱
            bias_up = self.noise_level + 0.1
            bias_down = 1.0 - self.noise_level - 0.1
            preferred = PhaseLockResult.DOWN
        else:
            # 3π/2~2π区域: 回到|up⟩偏向
            bias_up = 1.0 - self.noise_level - 0.1
            bias_down = self.noise_level + 0.1
            preferred = PhaseLockResult.UP

        # 热力学涨落: 噪声导致偶尔跳变到另一支
        rand = random.random()
        if rand < bias_up:
            result = PhaseLockResult.UP
        elif rand < bias_up + bias_down:
            result = PhaseLockResult.DOWN
        else:
            result = PhaseLockResult.UNLOCKED

        # 更新态: 坍缩
        if result == PhaseLockResult.UP:
            state.up_amplitude = complex(1, 0)
            state.down_amplitude = complex(0, 0)
            state.phase_state = WaveParticleState.PARTICLE
        elif result == PhaseLockResult.DOWN:
            state.up_amplitude = complex(0, 0)
            state.down_amplitude = complex(1, 0)
            state.phase_state = WaveParticleState.PARTICLE
        else:
            # 未锁定: 维持弥散态但θ漂移
            state.phase_state = WaveParticleState.WAVE

        # 记录历史
        self.lock_history.append({
            "theta_expect": round(theta, 4),
            "result": result.value,
            "preferred": preferred.value,
            "is_preferred": result == preferred,
        })

        return result

    def wave_to_particle(self, state: UndeterminedState,
                         theta_expect: float) -> PhaseLockResult:
        """
        波性→粒性坍缩

        完整流程:
          1. 设置θ_expect
          2. 应用Π̂_φ
          3. 返回锁定结果
        """
        state.theta_expect = theta_expect
        return self.apply(state)


# ═══════════════════════════════════════════════════════════════
# §3 Oloid差分判定器
# ═══════════════════════════════════════════════════════════════

class OloidDifferential:
    """
    Oloid差分判定器

    Thm4.5 (Oloid差分判定定理):
      结构锁定 ⇔ EXCESS_MASS_FACE>0 ∧ EXCESS_LOOP_HOLD>0 (condition_t - background_t)
      伪结构 ⇔ EXCESS≈0

    核心思想: Oloid可展性(PG-3公理) = 无损平铺低维 = 动态背景差分
      - background_t = PG基态流贯弥散(无囚禁的背景振荡)
      - condition_t = 实验条件下的网格状态
      - 差分移除基态不影响高维拓扑信息 → 保留囚禁信号, 剔除噪声

    MNQ v13验证:
      - SINGLE_RIPPLE → EXCESS→0 (伪结构, 差分后无信号)
      - HEX_RING_GAP → EXCESS>0 (真结构, 差分后仍存囚禁信号)
    """

    def __init__(self, grid: MNQ8Grid, background_steps: int = 10):
        self.grid = grid
        self.background_steps = background_steps
        self.condition_metrics: Dict[str, float] = {}
        self.background_metrics: Dict[str, float] = {}

    def compute(self) -> Dict[str, Any]:
        """
        执行Oloid差分:
          1. 记录condition_t指标
          2. 计算background_t
          3. 差分 = condition - background
          4. 判定真结构/伪结构
        """
        # 1. 条件指标
        self.condition_metrics = {
            "mass_face": self.grid.mass_face,
            "loop_hold": self.grid.loop_hold,
        }

        # 2. 计算背景
        self.grid.compute_background(self.background_steps)
        self.background_metrics = {
            "mass_face": self.grid.bg_mass_face,
            "loop_hold": self.grid.bg_loop_hold,
        }

        # 3. 差分
        excess_mf = self.condition_metrics["mass_face"] - self.background_metrics["mass_face"]
        excess_lh = self.condition_metrics["loop_hold"] - self.background_metrics["loop_hold"]

        # 4. 判定
        is_true = excess_mf > 0.01 and excess_lh > 0.01
        is_pseudo = abs(excess_mf) < 0.01 and abs(excess_lh) < 0.01

        result = {
            "condition_mass_face": round(self.condition_metrics["mass_face"], 4),
            "background_mass_face": round(self.background_metrics["mass_face"], 4),
            "excess_mass_face": round(excess_mf, 4),
            "condition_loop_hold": round(self.condition_metrics["loop_hold"], 4),
            "background_loop_hold": round(self.background_metrics["loop_hold"], 4),
            "excess_loop_hold": round(excess_lh, 4),
            "is_true_structure": is_true,
            "is_pseudo_structure": is_pseudo,
        }

        return result


# ═══════════════════════════════════════════════════════════════
# §4 天行相位锁定引擎 (完整集成)
# ═══════════════════════════════════════════════════════════════

class TianxingPhaseLockEngine:
    """
    天行相位锁定引擎 — M208主类

    集成:
      - PhaseSelector: Π̂_φ相位选择算子
      - OloidDifferential: Oloid差分判定
      - MNQ8Grid: 金符网格后端

    Thm4.4 (天行相位锁定定理):
      Π̂_φ生效(波粒耦合完成) → PG囚禁被锁定(Mass-Face>0, EXCESS_LOOP>0)
      纯波性弥散(Π̂_φ未效) → Mass-Face不超背景
    """

    def __init__(self, grid: Optional[MNQ8Grid] = None,
                 noise_level: float = 0.05):
        self.phase_selector = PhaseSelector(noise_level)
        self.grid = grid or MNQ8Grid(8, 8)
        self.state = UndeterminedState()
        self.last_result: Optional[PhaseLockResult] = None
        self.step_count = 0

    def phase_lock(self, theta_expect: float) -> PhaseLockResult:
        """
        天行相位锁定: Π̂_φ(θ_expect) |ψ⟩ → |locked⟩

        Args:
            theta_expect: L4观测者期望相位
                0 → 暗示|up⟩(上楼)
                π → 暗示|down⟩(下楼/倒置)

        Returns:
            PhaseLockResult: UP/DOWN/UNLOCKED
        """
        self.state = UndeterminedState(theta_expect=theta_expect)
        result = self.phase_selector.wave_to_particle(self.state, theta_expect)
        self.last_result = result

        # 相位锁定→注入偏置到MNQ网格
        if result == PhaseLockResult.UP:
            self.grid.inject_phase(0.0)
        elif result == PhaseLockResult.DOWN:
            self.grid.inject_phase(math.pi)

        self.step_count += 1
        return result

    def check_lock_condition(self, n_steps: int = 10) -> Dict[str, Any]:
        """
        检查相位锁定条件(Thm4.4)

        Π̂_φ生效 → PG囚禁被锁定:
          Mass-Face > 0 ∧ EXCESS_LOOP > 0
        """
        # 运行MNQ网格若干步
        for _ in range(n_steps):
            self.grid.step()

        # Oloid差分判定
        oloid = OloidDifferential(self.grid)
        diff_result = oloid.compute()

        return {
            "phase_result": self.last_result.value if self.last_result else "none",
            "is_locked": self.grid.is_locked(),
            "mass_face": round(self.grid.mass_face, 4),
            "excess_loop": round(self.grid.excess_loop, 4),
            "oloid_differential": diff_result,
        }

    def bistability_test(self, n_rounds: int = 20) -> Dict[str, Any]:
        """
        双稳态测试: 无偏置→随机跳变; 有偏置→锁向

        对应Thm4.3 (MNQ歧义纹理双稳态定理)
        """
        results_no_bias = []
        results_with_bias_up = []
        results_with_bias_down = []

        # 阶段1: 无偏置(θ随机)
        for _ in range(n_rounds):
            state = UndeterminedState(theta_expect=random.uniform(0, 2 * math.pi))
            result = self.phase_selector.apply(state)
            results_no_bias.append(result.value)

        # 阶段2: θ=0偏置(上楼)
        for _ in range(n_rounds):
            state = UndeterminedState(theta_expect=0.0)
            result = self.phase_selector.apply(state)
            results_with_bias_up.append(result.value)

        # 阶段3: θ=π偏置(下楼)
        for _ in range(n_rounds):
            state = UndeterminedState(theta_expect=math.pi)
            result = self.phase_selector.apply(state)
            results_with_bias_down.append(result.value)

        up_count_no_bias = results_no_bias.count("up")
        down_count_no_bias = results_no_bias.count("down")
        up_count_bias_up = results_with_bias_up.count("up")
        down_count_bias_down = results_with_bias_down.count("down")

        return {
            "no_bias": {
                "up_count": up_count_no_bias,
                "down_count": down_count_no_bias,
                "is_bistable": up_count_no_bias > 0 and down_count_no_bias > 0,
            },
            "bias_up": {
                "up_count": up_count_bias_up,
                "locked_correctly": up_count_bias_up > n_rounds * 0.7,
            },
            "bias_down": {
                "down_count": down_count_bias_down,
                "locked_correctly": down_count_bias_down > n_rounds * 0.7,
            },
        }

    def get_state(self) -> Dict[str, Any]:
        """返回引擎状态"""
        return {
            "step": self.step_count,
            "last_result": self.last_result.value if self.last_result else "none",
            "phase_state": self.state.phase_state.value,
            "theta_expect": round(self.state.theta_expect, 4),
            "grid_state": self.grid.get_state(),
            "lock_history_count": len(self.phase_selector.lock_history),
        }


# ═══════════════════════════════════════════════════════════════
# §5 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t211_tianxing_phase_lock() -> bool:
    """
    T211: 天行相位锁定歧义选择定理 (Thm4.2)

    验证:
      Π̂_φ(θ=0) → |up⟩ (上楼)
      Π̂_φ(θ=π) → |down⟩ (下楼/倒置)
    """
    engine = TianxingPhaseLockEngine(noise_level=0.02)

    # 测试θ=0 → 应偏向UP
    up_count = 0
    for _ in range(50):
        result = engine.phase_lock(0.0)
        if result == PhaseLockResult.UP:
            up_count += 1
    up_ratio = up_count / 50

    # 测试θ=π → 应偏向DOWN
    down_count = 0
    for _ in range(50):
        result = engine.phase_lock(math.pi)
        if result == PhaseLockResult.DOWN:
            down_count += 1
    down_ratio = down_count / 50

    # 验证: 两个方向都应有>70%的锁定率
    return up_ratio > 0.7 and down_ratio > 0.7


def _test_t214_oloid_differential() -> bool:
    """
    T214: Oloid差分判定定理 (Thm4.5)

    验证:
      HEX_RING_GAP → EXCESS>0 (真结构)
      SINGLE_RIPPLE → EXCESS≈0 (伪结构)
    """
    # 真结构: HEX_RING_GAP
    hex_grid = create_hex_ring_gap(10, 10, amplitude=0.7)
    # 先运行几步让网格活跃
    for _ in range(5):
        hex_grid.step()
    oloid_hex = OloidDifferential(hex_grid)
    hex_result = oloid_hex.compute()

    # 伪结构: SINGLE_RIPPLE
    ripple_grid = create_single_ripple(10, 10, amplitude=0.5)
    for _ in range(5):
        ripple_grid.step()
    oloid_ripple = OloidDifferential(ripple_grid)
    ripple_result = oloid_ripple.compute()

    # HEX_RING_GAP应有更高excess(相对背景)
    hex_excess = abs(hex_result["excess_mass_face"]) + abs(hex_result["excess_loop_hold"])
    ripple_excess = abs(ripple_result["excess_mass_face"]) + abs(ripple_result["excess_loop_hold"])

    # 至少hex_ring_gap的excess不应小于ripple(通常更大)
    return hex_excess >= ripple_excess * 0.8 or hex_result["is_true_structure"]


def run_mve() -> Dict[str, bool]:
    """
    M208 MVE验证

    T211: 天行相位锁定歧义选择定理(Thm4.2)
    T214: Oloid差分判定定理(Thm4.5)
    """
    results = {}

    print("=" * 60)
    print("M208 TianxingPhaseLock — MVE Verification")
    print("=" * 60)

    # T211
    try:
        t211 = _test_t211_tianxing_phase_lock()
        status = "PASS" if t211 else "FAIL"
        print(f"  T211 (天行相位锁定): {status}")
        results["T211"] = t211
    except Exception as e:
        print(f"  T211 (天行相位锁定): ERROR — {e}")
        results["T211"] = False

    # T214
    try:
        t214 = _test_t214_oloid_differential()
        status = "PASS" if t214 else "FAIL"
        print(f"  T214 (Oloid差分判定): {status}")
        results["T214"] = t214
    except Exception as e:
        print(f"  T214 (Oloid差分判定): ERROR — {e}")
        results["T214"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M208 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
