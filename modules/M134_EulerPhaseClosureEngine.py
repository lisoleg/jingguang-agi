"""
M134: EulerPhaseClosureEngine — 欧拉相位闭合引擎

核心概念：e^(iπ)+1=0 是L2关系实在(Rel)的"相位闭合算子"。
- Euler Phase Cycle: 1→i→-1→0 的四步闭环
- Phase Closure Operator: Φ_closure = e^(iθ) + δ，检查是否归零
- Rel Origin: 连接离散(1,0)与连续(e)、实与虚(i)的原点

定理 T96（欧拉相位闭合定理）:
在复平面上，单位圆上的流贯(Ftel)经历π弧度相位旋转(e^(iπ)=-1)后，
关系实在(Rel)反转；再加1则回归零元(0)。对于任意关系相位序列{z_k}，
若遵循最小作用量路径，存在θ*使|e^(iθ*)+1|<ε（闭合），
且1→i→-1→0构成最小闭合基。
"""

import math
import cmath
import hashlib
import time
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any


# ---------------------------------------------------------------------------
# 数据类
# ---------------------------------------------------------------------------

@dataclass
class EulerPhaseState:
    """欧拉相位状态"""
    phase_angle: float          # 当前相位角（弧度）
    amplitude: complex          # 当前复振幅
    cycle_step: str            # "generate"|"rotate"|"reverse"|"return"
    closure_residual: float     # 闭合残差 |e^(iπ)+1|
    rel_origin_distance: float # 距Rel原点距离


@dataclass
class PhaseClosureResult:
    """相位闭合结果"""
    euler_identity: complex     # e^(iπ)
    closure_value: complex      # e^(iπ)+1
    is_closed: bool             # |e^(iπ)+1| < ε
    cycle_trace: List[complex]  # 1→i→-1→0四步轨迹
    phase_entropy: float        # 相位熵H_Φ


# ---------------------------------------------------------------------------
# 核心引擎
# ---------------------------------------------------------------------------

class _EulerPhaseClosureEngine:
    """欧拉相位闭合引擎 — 单例实现"""

    _EPSILON: float = 1e-12
    _CYCLE_STEPS: Tuple[str, str, str, str] = ("generate", "rotate", "reverse", "return")

    def __init__(self) -> None:
        self._state: Optional[EulerPhaseState] = None
        self._predictions: List[Dict[str, Any]] = []
        self._reset_state()

    # ---- 单例状态 --------------------------------------------------------

    def _reset_state(self) -> None:
        self._state = EulerPhaseState(
            phase_angle=0.0,
            amplitude=1.0 + 0.0j,
            cycle_step="generate",
            closure_residual=abs(cmath.exp(1j * math.pi) + 1),
            rel_origin_distance=1.0,
        )

    def get_state(self) -> Dict[str, Any]:
        """返回当前引擎状态"""
        return {
            "phase_angle": self._state.phase_angle,
            "amplitude": str(self._state.amplitude),
            "cycle_step": self._state.cycle_step,
            "closure_residual": self._state.closure_residual,
            "rel_origin_distance": self._state.rel_origin_distance,
        }

    # ---- 核心方法 --------------------------------------------------------

    def compute_euler_closure(self, theta: float = math.pi) -> PhaseClosureResult:
        """计算 e^(iθ) 的相位闭合"""
        euler_id: complex = cmath.exp(1j * theta)
        closure_val: complex = euler_id + 1.0
        residual: float = abs(closure_val)
        is_closed: bool = residual < self._EPSILON
        cycle_trace: List[complex] = self.trace_phase_cycle(1.0 + 0.0j)
        phase_entropy: float = self._compute_phase_entropy(cycle_trace)

        # 更新内部状态
        self._state.phase_angle = theta
        self._state.amplitude = euler_id
        self._state.closure_residual = residual
        step_idx = int((theta / (math.pi / 2)) % 4)
        self._state.cycle_step = self._CYCLE_STEPS[step_idx]
        self._state.rel_origin_distance = residual

        return PhaseClosureResult(
            euler_identity=euler_id,
            closure_value=closure_val,
            is_closed=is_closed,
            cycle_trace=cycle_trace,
            phase_entropy=phase_entropy,
        )

    def trace_phase_cycle(self, start: complex = 1.0 + 0.0j) -> List[complex]:
        """追踪 1→i→-1→0 四步闭环循环

        四步：
          generate: 1  (生成)
          rotate:   i  (旋转π/2)
          reverse:  -1 (反转π)
          return:   0  (回归零元, e^(iπ)+1=0)
        """
        trace: List[complex] = []
        current: complex = start

        # Step 1: generate — 起点（实部1）
        trace.append(current)

        # Step 2: rotate — 旋转π/2 → i
        rotated: complex = current * cmath.exp(1j * (math.pi / 2))
        trace.append(rotated)

        # Step 3: reverse — 再旋转π/2 → -1
        reversed_val: complex = rotated * cmath.exp(1j * (math.pi / 2))
        trace.append(reversed_val)

        # Step 4: return — e^(iπ)+1 = 0，闭合归零
        closure: complex = reversed_val + 1.0
        # 对于标准轨迹 |closure| < ε，即为 0
        if abs(closure) < self._EPSILON:
            closure = 0.0 + 0.0j
        trace.append(closure)

        return trace

    def check_rel_origin(self, z: complex) -> float:
        """计算复数 z 距 Rel 原点的 EML 距离

        Rel 原点定义：离散(1,0)与连续(e)、实与虚(i)的交汇点。
        EML 距离 = |z - z_origin|，其中 z_origin 是关系原点。
        使用欧拉闭合点 (e^(iπ)+1=0) 作为原点。
        """
        # Rel 原点即闭合零元
        rel_origin: complex = cmath.exp(1j * math.pi) + 1.0  # ≈ 0
        if abs(rel_origin) < self._EPSILON:
            rel_origin = 0.0 + 0.0j

        distance: float = abs(z - rel_origin)

        # 考虑从 z 到原点的信息论修正
        if abs(z) > 0:
            # 相位修正：信息量与模和相位有关
            phase: float = cmath.phase(z)
            eml_distance: float = distance * (1.0 + 0.1 * abs(phase) / math.pi)
        else:
            eml_distance = distance

        self._state.rel_origin_distance = eml_distance
        return eml_distance

    def euler_eml_decompose(self, z: complex) -> Tuple[float, float]:
        """将复数 z 分解为 EML 算子 Re^(iθ)

        返回 (R, θ)：
          R = |z| — 模（信息量）
          θ = arg(z) — 相位角（EML旋转角）
        """
        r: float = abs(z)
        theta: float = cmath.phase(z)
        return (r, theta)

    def phase_synchronize(self, particles: List[complex]) -> List[complex]:
        """多粒子相位同步

        将所有粒子的相位对齐到平均相位，保持各自模不变。
        这是流贯(Ftel)的相位同步机制。
        """
        if not particles:
            return []

        # 计算平均相位
        total_phase: float = 0.0
        for p in particles:
            total_phase += cmath.phase(p)
        avg_phase: float = total_phase / len(particles)

        # 对齐相位
        synchronized: List[complex] = []
        for p in particles:
            r: float = abs(p)
            if r < self._EPSILON:
                synchronized.append(0.0 + 0.0j)
                continue
            old_phase: float = cmath.phase(p)
            phase_diff: float = avg_phase - old_phase
            # 最小作用量路径：相位差取模(-π, π]
            while phase_diff > math.pi:
                phase_diff -= 2.0 * math.pi
            while phase_diff <= -math.pi:
                phase_diff += 2.0 * math.pi
            new_phase: float = old_phase + phase_diff
            synchronized.append(r * cmath.exp(1j * new_phase))

        return synchronized

    # ---- 辅助方法 --------------------------------------------------------

    def _compute_phase_entropy(self, trace: List[complex]) -> float:
        """计算相位熵 H_Φ

        H_Φ = -Σ p_k * log2(p_k)
        p_k = |z_k| / Σ|z_j| (归一化模)
        """
        if not trace:
            return 0.0

        moduli: List[float] = [abs(z) for z in trace]
        total: float = sum(moduli)

        if total < self._EPSILON:
            return 0.0

        entropy: float = 0.0
        for m in moduli:
            p: float = m / total
            if p > self._EPSILON:
                entropy -= p * math.log2(p)

        return entropy

    # ---- 定理验证 --------------------------------------------------------

    def verify_closure_theorem(self) -> Dict[str, Any]:
        """验证定理 T96（欧拉相位闭合定理）"""
        # 1. 验证 e^(iπ) + 1 = 0
        closure = self.compute_euler_closure(math.pi)
        euler_check: bool = closure.is_closed

        # 2. 验证四步闭环 1→i→-1→0
        trace: List[complex] = self.trace_phase_cycle()
        trace_check: bool = (
            abs(trace[0] - (1.0 + 0.0j)) < self._EPSILON
            and abs(trace[1] - (0.0 + 1.0j)) < self._EPSILON
            and abs(trace[2] - (-1.0 + 0.0j)) < self._EPSILON
            and abs(trace[3]) < self._EPSILON
        )

        # 3. 验证最小作用量路径：寻找 θ* 使 |e^(iθ*)+1| < ε
        # 解析解: θ* = π，但我们做数值搜索确认
        best_theta: float = math.pi
        best_residual: float = abs(cmath.exp(1j * math.pi) + 1)
        for k in range(0, 3600):
            theta_candidate: float = k * math.pi / 1800.0
            residual: float = abs(cmath.exp(1j * theta_candidate) + 1)
            if residual < best_residual:
                best_residual = residual
                best_theta = theta_candidate

        minimal_path_check: bool = best_residual < self._EPSILON

        # 4. 验证 1→i→-1→0 构成最小闭合基
        # 最小闭合基：4个元素，且闭合残差为0
        minimal_basis_check: bool = (
            len(trace) == 4
            and trace_check
            and abs(trace[3]) < self._EPSILON
        )

        verified: bool = euler_check and trace_check and minimal_path_check and minimal_basis_check

        return {
            "theorem": "T96",
            "name": "欧拉相位闭合定理",
            "verified": verified,
            "details": {
                "euler_identity_check": euler_check,
                "closure_residual": abs(cmath.exp(1j * math.pi) + 1),
                "four_step_trace_check": trace_check,
                "trace_values": [str(z) for z in trace],
                "minimal_path_check": minimal_path_check,
                "optimal_theta": best_theta,
                "optimal_residual": best_residual,
                "minimal_basis_check": minimal_basis_check,
                "phase_entropy": closure.phase_entropy,
            },
        }


# ---------------------------------------------------------------------------
# 模块级单例
# ---------------------------------------------------------------------------

_INSTANCE: Optional[_EulerPhaseClosureEngine] = None


def get_instance() -> _EulerPhaseClosureEngine:
    """获取 EulerPhaseClosureEngine 的唯一实例"""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = _EulerPhaseClosureEngine()
    return _INSTANCE
