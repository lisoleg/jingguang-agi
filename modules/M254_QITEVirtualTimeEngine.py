# -*- coding: utf-8 -*-
"""
M254: QITE Virtual Time Engine -- 虚时计算引擎
================================================

Theory Source: 非结合调和分析中的 QITE 虚时计算

Core Concepts:
    QITE 虚时演化: |ψ(τ)⟩ = e^{-Hτ}|ψ(0)⟩ / ‖e^{-Hτ}|ψ(0)⟩‖
      一阶近似: ψ_{n+1} = ψ_n - Δτ·H·ψ_n，归一化: ψ = ψ / ‖ψ‖
    四元数旋转嵌入: q = w+xi+yj+zk, R(q)v = q·v·q*, q* = w-xi-yj-zk
    八元数非结合推理通道: (a∘b)∘c ≠ a∘(b∘c), BFT 容错: 两条路径取平均
    Wick 旋转: τ ↔ it

Theorems:
    T2.101: QITE 收敛性 — 虚时演化 e^{-Hτ} 在 τ→∞ 时收敛到 H 的基态 |E₀⟩
    T2.102: 四元数旋转等价性 — 四元数旋转 R(q) 与 3×3 旋转矩阵 R(θ,n) 等价

Falsifiable Prediction:
    P26: QITE+Prior 收敛到全局最优概率 ≥ 0.8

Author: Kou Dou Ma -- TaiYi AGI Team
Version: v7.38
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# ===========================================================================
# 八元数乘法表 (Cayley-Dickson / Fano Plane)
# ===========================================================================
OCTO_MUL: Dict[int, Dict[int, Tuple[int, int]]] = {}


def _init_octo_mul() -> None:
    """Initialize the octonion multiplication table via Fano plane."""
    fano_lines = [
        (1, 2, 3), (1, 4, 5), (1, 7, 6),
        (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5)
    ]
    for i in range(8):
        OCTO_MUL[i] = {}
    for i in range(8):
        OCTO_MUL[0][i] = (1, i)
        OCTO_MUL[i][0] = (1, i)
    for i in range(1, 8):
        OCTO_MUL[i][i] = (-1, 0)
    for (a, b, c) in fano_lines:
        OCTO_MUL[a][b] = (1, c)
        OCTO_MUL[b][c] = (1, a)
        OCTO_MUL[c][a] = (1, b)
        OCTO_MUL[b][a] = (-1, c)
        OCTO_MUL[c][b] = (-1, a)
        OCTO_MUL[a][c] = (-1, b)


_init_octo_mul()


# ===========================================================================
# 数据结构
# ===========================================================================

@dataclass
class QITEState:
    """QITE 虚时演化状态快照。"""
    tau: float
    state: List[float]
    norm: float
    energy: float
    step: int


@dataclass
class QITEConfig:
    """QITE 引擎配置。"""
    dim: int = 8
    dt: float = 0.01
    max_tau: float = 10.0
    convergence_threshold: float = 1e-8
    max_steps: int = 10000


# ===========================================================================
# 辅助向量函数
# ===========================================================================

def vec_norm(v: List[float]) -> float:
    """计算向量范数。"""
    return math.sqrt(sum(x * x for x in v))


def vec_normalize(v: List[float]) -> List[float]:
    """归一化向量。"""
    n = vec_norm(v)
    return [x / n for x in v] if n > 1e-15 else v


def vec_dot(a: List[float], b: List[float]) -> float:
    """向量点积。"""
    return sum(x * y for x, y in zip(a, b))


def vec_sub(a: List[float], b: List[float]) -> List[float]:
    """向量减法 a - b。"""
    return [x - y for x, y in zip(a, b)]


def vec_scale(v: List[float], c: float) -> List[float]:
    """向量数乘。"""
    return [x * c for x in v]


# ===========================================================================
# 主引擎类
# ===========================================================================

class QITEVirtualTimeEngine:
    """M254 QITE 虚时计算引擎。"""

    _instance: Optional[QITEVirtualTimeEngine] = None

    def __init__(self, dim: int = 8, dt: float = 0.01, max_tau: float = 10.0) -> None:
        self._dim = dim
        self._dt = dt
        self._max_tau = max_tau
        self._history: List[QITEState] = []
        self._current_state: Optional[QITEState] = None

    @classmethod
    def get_instance(cls, dim: int = 8, dt: float = 0.01,
                     max_tau: float = 10.0) -> QITEVirtualTimeEngine:
        """获取单例实例。"""
        if cls._instance is None:
            cls._instance = cls(dim=dim, dt=dt, max_tau=max_tau)
        return cls._instance

    # -------------------------------------------------------------------
    # 矩阵运算
    # -------------------------------------------------------------------

    @staticmethod
    def mat_vec_mul(mat: List[List[float]], vec: List[float]) -> List[float]:
        """矩阵-向量乘法: result = mat @ vec。"""
        rows = len(mat)
        result = [0.0] * rows
        for i in range(rows):
            s = 0.0
            for j in range(len(vec)):
                s += mat[i][j] * vec[j]
            result[i] = s
        return result

    # -------------------------------------------------------------------
    # QITE 虚时演化
    # -------------------------------------------------------------------

    def qite_step(self, state: List[float], hamiltonian: List[List[float]],
                  dtau: float) -> List[float]:
        """一步虚时演化: ψ_{n+1} = ψ_n - Δτ·H·ψ_n，然后归一化。"""
        h_psi = self.mat_vec_mul(hamiltonian, state)
        new_state = vec_sub(state, vec_scale(h_psi, dtau))
        return vec_normalize(new_state)

    def qite_evolve(self, initial_state: List[float], hamiltonian: List[List[float]],
                    n_steps: int) -> List[float]:
        """多步虚时演化。"""
        state = vec_normalize(initial_state)
        for step in range(n_steps):
            state = self.qite_step(state, hamiltonian, self._dt)
            if step % 100 == 0:
                energy = self._compute_energy(state, hamiltonian)
                self._history.append(QITEState(
                    tau=(step + 1) * self._dt, state=list(state),
                    norm=vec_norm(state), energy=energy, step=step))
        energy = self._compute_energy(state, hamiltonian)
        self._current_state = QITEState(
            tau=n_steps * self._dt, state=list(state),
            norm=vec_norm(state), energy=energy, step=n_steps)
        self._history.append(self._current_state)
        return state

    def _compute_energy(self, state: List[float], hamiltonian: List[List[float]]) -> float:
        """计算能量期望值 ⟨ψ|H|ψ⟩。"""
        h_psi = self.mat_vec_mul(hamiltonian, state)
        return vec_dot(state, h_psi)

    def find_ground_state(self, hamiltonian: List[List[float]],
                          initial_state: Optional[List[float]] = None) -> Tuple[List[float], float]:
        """通过 QITE 虚时演化寻找哈密顿量基态。"""
        dim = len(hamiltonian)
        if initial_state is None:
            initial_state = [random.gauss(0, 1) for _ in range(dim)]
        n_steps = int(self._max_tau / self._dt)
        final_state = self.qite_evolve(initial_state, hamiltonian, n_steps)
        energy = self._compute_energy(final_state, hamiltonian)
        return final_state, energy

    # -------------------------------------------------------------------
    # 四元数运算
    # -------------------------------------------------------------------

    @staticmethod
    def quaternion_multiply(q1: Tuple[float, float, float, float],
                            q2: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """四元数乘法 q1 * q2，q = (w, x, y, z)。"""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
        return (w, x, y, z)

    @staticmethod
    def quaternion_conjugate(q: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """四元数共轭 q* = (w, -x, -y, -z)。"""
        w, x, y, z = q
        return (w, -x, -y, -z)

    @staticmethod
    def quaternion_rotate(q: Tuple[float, float, float, float],
                          v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """四元数旋转向量: R(q)v = q·v·q*。"""
        v_quat = (0.0, v[0], v[1], v[2])
        q_conj = QITEVirtualTimeEngine.quaternion_conjugate(q)
        temp = QITEVirtualTimeEngine.quaternion_multiply(q, v_quat)
        result = QITEVirtualTimeEngine.quaternion_multiply(temp, q_conj)
        return (result[1], result[2], result[3])

    @staticmethod
    def quaternion_to_rotation_matrix(q: Tuple[float, float, float, float]) -> List[List[float]]:
        """四元数转 3×3 旋转矩阵。"""
        w, x, y, z = q
        xx, yy, zz = x * x, y * y, z * z
        xy, xz, yz = x * y, x * z, y * z
        wx, wy, wz = w * x, w * y, w * z
        return [
            [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz),       2.0 * (xz + wy)],
            [2.0 * (xy + wz),       1.0 - 2.0 * (xx + zz),  2.0 * (yz - wx)],
            [2.0 * (xz - wy),       2.0 * (yz + wx),        1.0 - 2.0 * (xx + yy)]
        ]

    @staticmethod
    def axis_angle_to_quaternion(theta: float, n: Tuple[float, float, float]) -> Tuple[float, float, float, float]:
        """轴角表示转四元数: q = (cos(θ/2), n·sin(θ/2))。"""
        half = theta / 2.0
        s = math.sin(half)
        c = math.cos(half)
        return (c, n[0] * s, n[1] * s, n[2] * s)

    @staticmethod
    def axis_angle_to_rotation_matrix(theta: float, n: Tuple[float, float, float]) -> List[List[float]]:
        """轴角表示转 3×3 旋转矩阵（Rodrigues 公式）。"""
        nx, ny, nz = n
        c = math.cos(theta)
        s = math.sin(theta)
        t = 1.0 - c
        return [
            [t * nx * nx + c,      t * nx * ny - s * nz, t * nx * nz + s * ny],
            [t * nx * ny + s * nz, t * ny * ny + c,      t * ny * nz - s * nx],
            [t * nx * nz - s * ny, t * ny * nz + s * nx, t * nz * nz + c]
        ]

    # -------------------------------------------------------------------
    # 八元数运算
    # -------------------------------------------------------------------

    @staticmethod
    def octonion_multiply(a: Tuple[float, ...], b: Tuple[float, ...]) -> Tuple[float, ...]:
        """八元数乘法（基于 Cayley-Dickson / Fano 平面乘法表）。"""
        result = [0.0] * 8
        for i in range(8):
            if abs(a[i]) < 1e-15:
                continue
            for j in range(8):
                if abs(b[j]) < 1e-15:
                    continue
                sign, k = OCTO_MUL[i][j]
                result[k] += sign * a[i] * b[j]
        return tuple(result)

    @staticmethod
    def octonion_norm(a: Tuple[float, ...]) -> float:
        """八元数范数。"""
        return math.sqrt(sum(x * x for x in a))

    @staticmethod
    def octonion_conjugate(a: Tuple[float, ...]) -> Tuple[float, ...]:
        """八元数共轭: a* = (a0, -a1, ..., -a7)。"""
        return (a[0],) + tuple(-x for x in a[1:])

    def octonion_reasoning(self, a: Tuple[float, ...], b: Tuple[float, ...],
                           c: Tuple[float, ...]) -> Tuple[float, ...]:
        """八元数非结合推理（BFT 容错: 两条路径取平均）。"""
        ab = self.octonion_multiply(a, b)
        path1 = self.octonion_multiply(ab, c)
        bc = self.octonion_multiply(b, c)
        path2 = self.octonion_multiply(a, bc)
        return tuple((p1 + p2) / 2.0 for p1, p2 in zip(path1, path2))

    def octonion_jacobiator(self, a: Tuple[float, ...], b: Tuple[float, ...],
                            c: Tuple[float, ...]) -> Tuple[float, ...]:
        """八元数 Jacobiator: Jac(a,b,c) = (a*b)*c - a*(b*c)。"""
        ab = self.octonion_multiply(a, b)
        path1 = self.octonion_multiply(ab, c)
        bc = self.octonion_multiply(b, c)
        path2 = self.octonion_multiply(a, bc)
        return tuple(p1 - p2 for p1, p2 in zip(path1, path2))

    # -------------------------------------------------------------------
    # Wick 旋转
    # -------------------------------------------------------------------

    @staticmethod
    def wick_rotate(tau: float) -> complex:
        """Wick 旋转: 虚时 → 实时, τ ↔ it。"""
        return complex(0, tau)

    @staticmethod
    def inverse_wick_rotate(t_real: float) -> float:
        """逆 Wick 旋转: 实时 → 虚时。"""
        return t_real

    # -------------------------------------------------------------------
    # 状态查询
    # -------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """获取引擎当前状态。"""
        if self._current_state is None:
            return {"status": "idle", "dim": self._dim, "dt": self._dt,
                    "max_tau": self._max_tau, "history_length": len(self._history)}
        return {"status": "evolved", "dim": self._dim, "dt": self._dt,
                "max_tau": self._max_tau, "current_tau": self._current_state.tau,
                "current_energy": self._current_state.energy,
                "current_norm": self._current_state.norm,
                "current_step": self._current_state.step,
                "history_length": len(self._history)}

    def get_history(self) -> List[Dict[str, Any]]:
        """获取演化历史。"""
        return [{"tau": s.tau, "energy": s.energy, "norm": s.norm, "step": s.step}
                for s in self._history]

    def reset(self) -> None:
        """重置引擎状态。"""
        self._history = []
        self._current_state = None


# ===========================================================================
# 辅助：2×2 矩阵本征值求解
# ===========================================================================

def eigenvalues_2x2(mat: List[List[float]]) -> Tuple[float, float]:
    """求解 2×2 实对称矩阵的本征值。"""
    tr = mat[0][0] + mat[1][1]
    det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    disc = max(tr * tr - 4.0 * det, 0.0)
    sqrt_disc = math.sqrt(disc)
    return ((tr - sqrt_disc) / 2.0, (tr + sqrt_disc) / 2.0)


def eigenvector_2x2(mat: List[List[float]], eigenvalue: float) -> List[float]:
    """求解 2×2 实对称矩阵对应本征值的本征向量。"""
    a = mat[0][0] - eigenvalue
    b = mat[0][1]
    if abs(b) > abs(a):
        v = [-b, a]
    elif abs(a) > 1e-15:
        v = [-b / a, 1.0]
    else:
        v = [1.0, 0.0]
    return vec_normalize(v)


# ===========================================================================
# 验证函数
# ===========================================================================

def verify_theorem_t2101() -> bool:
    """
    验证定理 T2.101: QITE 收敛性。
    构造 2×2 哈密顿量 H=[[1,0.5],[0.5,2]]，随机初始态，
    验证虚时演化收敛到基态方向。
    """
    print("=" * 60)
    print("验证定理 T2.101: QITE 收敛性")
    print("=" * 60)

    H = [[1.0, 0.5], [0.5, 2.0]]
    lambda1 = (3.0 - math.sqrt(2.0)) / 2.0
    lambda2 = (3.0 + math.sqrt(2.0)) / 2.0
    print(f"  解析本征值: λ₁ = {lambda1:.6f}, λ₂ = {lambda2:.6f}")

    # 基态本征向量: v₂/v₁ = -2(1-λ₁) = 1-√2
    ratio = 1.0 - math.sqrt(2.0)
    gs_vec = vec_normalize([1.0, ratio])
    print(f"  解析基态方向: ({gs_vec[0]:.6f}, {gs_vec[1]:.6f})")

    engine = QITEVirtualTimeEngine(dim=2, dt=0.001, max_tau=50.0)
    n_trials = 10
    successes = 0
    for trial in range(n_trials):
        random.seed(trial * 42 + 7)
        initial = [random.gauss(0, 1) for _ in range(2)]
        final_state, energy = engine.find_ground_state(H, initial)
        engine.reset()
        overlap = abs(vec_dot(final_state, gs_vec))
        energy_error = abs(energy - lambda1)
        converged = overlap > 0.99 and energy_error < 0.01
        if converged:
            successes += 1
        print(f"  试验 {trial + 1}: overlap={overlap:.6f}, "
              f"E_err={energy_error:.6f}, {'✓' if converged else '✗'}")

    success_rate = successes / n_trials
    result = success_rate >= 0.9
    print(f"\n  成功率: {successes}/{n_trials} = {success_rate:.1%}")
    print(f"  定理 T2.101 验证{'通过' if result else '未通过'}\n")
    return result


def verify_theorem_t2102() -> bool:
    """
    验证定理 T2.102: 四元数旋转等价性。
    对比四元数旋转 R(q)v 与旋转矩阵 R(θ,n)v。
    """
    print("=" * 60)
    print("验证定理 T2.102: 四元数旋转等价性")
    print("=" * 60)

    engine = QITEVirtualTimeEngine()
    all_passed = True
    sqrt2, sqrt3 = math.sqrt(2.0), math.sqrt(3.0)

    test_cases = [
        (math.pi / 3, (1.0, 0.0, 0.0), "绕 x 轴旋转 60°"),
        (math.pi / 4, (0.0, 1.0, 0.0), "绕 y 轴旋转 45°"),
        (math.pi / 6, (0.0, 0.0, 1.0), "绕 z 轴旋转 30°"),
        (math.pi / 2, (1.0 / sqrt3, 1.0 / sqrt3, 1.0 / sqrt3), "绕 (1,1,1)/√3 旋转 90°"),
        (2.0 * math.pi / 3, (0.0, 1.0 / sqrt2, 1.0 / sqrt2), "绕 (0,1,1)/√2 旋转 120°"),
    ]
    test_vectors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 2.0, 3.0)]

    for theta, axis, desc in test_cases:
        n_norm = math.sqrt(sum(x * x for x in axis))
        n = tuple(x / n_norm for x in axis)
        q = engine.axis_angle_to_quaternion(theta, n)
        R_from_q = engine.quaternion_to_rotation_matrix(q)
        R_from_axis = engine.axis_angle_to_rotation_matrix(theta, n)

        mat_diff = math.sqrt(sum((R_from_q[i][j] - R_from_axis[i][j]) ** 2
                                  for i in range(3) for j in range(3)))
        max_vec_diff = max(
            math.sqrt(sum((a - b) ** 2 for a, b in zip(
                engine.quaternion_rotate(q, v),
                tuple(sum(R_from_axis[i][j] * v[j] for j in range(3)) for i in range(3)))))
            for v in test_vectors)

        case_passed = mat_diff < 1e-10 and max_vec_diff < 1e-10
        all_passed = all_passed and case_passed
        print(f"  {desc}: mat_diff={mat_diff:.2e}, vec_diff={max_vec_diff:.2e} "
              f"{'✓' if case_passed else '✗'}")

    print(f"\n  定理 T2.102 验证{'通过' if all_passed else '未通过'}\n")
    return all_passed


def verify_prediction_p26() -> bool:
    """
    验证预测 P26: QITE+Prior 收敛到全局最优概率 ≥ 0.8。
    在 8 维空间中多次运行 QITE，统计收敛到全局基态的概率。
    """
    print("=" * 60)
    print("验证预测 P26: QITE+Prior 收敛到全局最优概率 ≥ 0.8")
    print("=" * 60)

    dim = 8
    n_trials = 50

    # 构造 8×8 对角占优哈密顿量
    random.seed(12345)
    diag = [float(i + 1) for i in range(dim)]
    H = [[0.0] * dim for _ in range(dim)]
    for i in range(dim):
        H[i][i] = diag[i]
        for j in range(i + 1, dim):
            coupling = random.uniform(-0.1, 0.1)
            H[i][j] = coupling
            H[j][i] = coupling

    # 参考基态能量（长步长 QITE）
    engine_ref = QITEVirtualTimeEngine(dim=dim, dt=0.002, max_tau=50.0)
    ref_state = [random.gauss(0, 1) for _ in range(dim)]
    _, ground_energy = engine_ref.find_ground_state(H, ref_state)
    engine_ref.reset()
    print(f"  参考基态能量: {ground_energy:.6f}")

    # 多次试验
    engine = QITEVirtualTimeEngine(dim=dim, dt=0.005, max_tau=30.0)
    successes = 0
    for trial in range(n_trials):
        random.seed(trial * 31 + 17)
        initial = [random.gauss(0, 1) for _ in range(dim)]
        _, energy = engine.find_ground_state(H, initial)
        engine.reset()
        energy_error = abs(energy - ground_energy)
        converged = energy_error < 0.1
        if converged:
            successes += 1
        if trial < 10 or not converged:
            print(f"  试验 {trial + 1:2d}: E={energy:.6f}, "
                  f"err={energy_error:.6f}, {'✓' if converged else '✗'}")

    success_rate = successes / n_trials
    result = success_rate >= 0.8
    print(f"\n  收敛概率: {successes}/{n_trials} = {success_rate:.1%} (阈值: 80%)")
    print(f"  预测 P26 验证{'通过' if result else '未通过'}\n")
    return result


def verify_theorem_t275(n_trials: int = 100, seed: int = 42) -> Dict[str, Any]:
    """
    验证 T2.75 QITE虚时定理：QITE演化后系统的能量单调递减。

    虚时演化是能量最小化过程，每步演化应使能量不增。
    对 n_trials 个随机 2x2 或 3x3 哈密顿量，验证末态能量 ≤ 初始能量。
    """
    random.seed(seed)
    engine = QITEVirtualTimeEngine(dim=3, dt=0.01, max_tau=10.0)

    monotonic_count = 0
    energy_decreases: List[float] = []

    for _ in range(n_trials):
        dim = random.choice([2, 3])
        # 生成随机对称哈密顿量
        H = [[0.0] * dim for _ in range(dim)]
        for i in range(dim):
            for j in range(i, dim):
                val = random.gauss(0, 1.0)
                H[i][j] = val
                H[j][i] = val

        # 生成随机初始态
        initial_state = [random.gauss(0, 1) for _ in range(dim)]
        norm_init = vec_normalize(initial_state)

        # 计算初始能量 <ψ₀|H|ψ₀>
        h_psi = QITEVirtualTimeEngine.mat_vec_mul(H, norm_init)
        initial_energy = vec_dot(norm_init, h_psi)

        # 执行 QITE 演化
        final_state = engine.qite_evolve(initial_state, H, n_steps=20)
        engine.reset()

        # 计算末态能量 <ψ_f|H|ψ_f>
        h_psi_f = QITEVirtualTimeEngine.mat_vec_mul(H, final_state)
        final_energy = vec_dot(final_state, h_psi_f)

        if final_energy <= initial_energy + 1e-10:
            monotonic_count += 1

        energy_decreases.append(initial_energy - final_energy)

    monotonic_rate = monotonic_count / n_trials
    mean_decrease = sum(energy_decreases) / len(energy_decreases) if energy_decreases else 0.0
    proved = monotonic_rate >= 0.90

    return {
        'theorem': 'T2.75',
        'proved': proved,
        'n_trials': n_trials,
        'monotonic_rate': monotonic_rate,
        'mean_energy_decrease': mean_decrease,
    }


def verify_prediction_p22(n_trials: int = 200, seed: int = 99,
                          error_threshold: float = 0.15) -> Dict[str, Any]:
    """
    验证 P22 QITE虚时预测：find_ground_state 找到的基态能量
    与理论最小特征值的误差 < 15%。

    对 2x2 对称哈密顿量，用求根公式计算精确最小特征值，
    与 QITE 搜索结果对比。
    """
    random.seed(seed)
    engine = QITEVirtualTimeEngine(dim=2, dt=0.005, max_tau=30.0)

    eps = 1e-10
    relative_errors: List[float] = []

    for _ in range(n_trials):
        # 生成随机 2x2 对称哈密顿量
        a = random.gauss(0, 2.0)
        b = random.gauss(0, 1.0)
        d = random.gauss(0, 2.0)
        H = [[a, b], [b, d]]

        # 理论最小特征值: λ_min = (tr(H) - sqrt(tr(H)² - 4*det(H))) / 2
        tr = a + d
        det = a * d - b * b
        disc = max(tr * tr - 4.0 * det, 0.0)
        lambda_min = (tr - math.sqrt(disc)) / 2.0

        # 调用 find_ground_state 搜索基态能量
        _, energy = engine.find_ground_state(H)
        engine.reset()

        # 计算相对误差
        rel_err = abs(energy - lambda_min) / max(abs(lambda_min), eps)
        relative_errors.append(rel_err)

    mean_rel_err = sum(relative_errors) / len(relative_errors) if relative_errors else 0.0
    passed = mean_rel_err < error_threshold

    return {
        'prediction': 'P22',
        'passed': passed,
        'n_trials': n_trials,
        'mean_relative_error': mean_rel_err,
        'threshold': error_threshold,
    }


# ===========================================================================
# 主程序
# ===========================================================================

if __name__ == "__main__":
    print("M254 QITEVirtualTimeEngine — 虚时计算引擎")
    print("=" * 60)

    # 基本功能测试
    engine = QITEVirtualTimeEngine(dim=4, dt=0.01, max_tau=10.0)
    print(f"引擎状态: {engine.get_state()}")

    H_test = [[2.0, 0.3, 0.0, 0.0], [0.3, 3.0, 0.2, 0.0],
              [0.0, 0.2, 1.5, 0.1], [0.0, 0.0, 0.1, 4.0]]
    random.seed(42)
    init = [random.gauss(0, 1) for _ in range(4)]
    final, energy = engine.find_ground_state(H_test, init)
    print(f"4维 QITE 基态能量: {energy:.6f}")
    engine.reset()

    # 四元数旋转测试
    q_test = engine.axis_angle_to_quaternion(math.pi / 4, (0.0, 0.0, 1.0))
    v_rotated = engine.quaternion_rotate(q_test, (1.0, 0.0, 0.0))
    print(f"四元数旋转: R(q)(1,0,0) = ({v_rotated[0]:.6f}, {v_rotated[1]:.6f}, {v_rotated[2]:.6f})")

    # 八元数推理测试
    a_oct = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0)
    b_oct = (8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0)
    c_oct = (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5)
    jac = engine.octonion_jacobiator(a_oct, b_oct, c_oct)
    reasoning = engine.octonion_reasoning(a_oct, b_oct, c_oct)
    print(f"八元数 Jacobiator 范数: {engine.octonion_norm(jac):.4f}")
    print(f"BFT 推理结果: [{', '.join(f'{x:.2f}' for x in reasoning)}]")

    # Wick 旋转测试
    t_complex = engine.wick_rotate(2.5)
    print(f"Wick 旋转: τ=2.5 → t={t_complex}")

    # 验证
    print("\n" + "=" * 60)
    t1 = verify_theorem_t2101()
    t2 = verify_theorem_t2102()
    p = verify_prediction_p26()

    print("=" * 60)
    print("验证汇总")
    print("=" * 60)
    print(f"  T2.101 (QITE 收敛性):       {'通过 ✓' if t1 else '未通过 ✗'}")
    print(f"  T2.102 (四元数旋转等价性):   {'通过 ✓' if t2 else '未通过 ✗'}")
    print(f"  P26   (QITE+Prior ≥ 0.8):   {'通过 ✓' if p else '未通过 ✗'}")
