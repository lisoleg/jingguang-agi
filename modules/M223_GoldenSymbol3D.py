"""
M223 GoldenSymbol3D Engine — 金符学3D复广数 + MNQ8能流引擎
==========================================================

理论来源: 《太一万有理论六合统合白皮书》— 金符学(韩贵林) + MNQ8能流更新律
核心概念:
    - 金符3D复广数: z = a + b·i + c·j, i²=-1, j²=-1, i·j=j·i (交换性公理)
    - 阴龙积⊙: 邻域能流耦合运算 (App H 定义 H.2.4)
    - MNQ8更新律: 本征螺旋振荡 + 邻域耦合(阴龙积) + 囚禁判据(MASS_FACE > THRESHOLD)
    - HEX_RING_GAP: 强耦合囚禁态 (Locked=True, PG鲁珀特之泪孤子)
    - BACKGROUND_OSC: 弥散基态 (Locked=False, PG流贯弥散)
定理编号: T2.32 (金符交换性公理), T2.33 (阴龙积结合律), T2.34 (MNQ8囚禁判据)

架构概述:
    GoldenSymbol — 3D复广数核心数据类型 (a, b, c) + 运算
    yin_long_product — 阴龙积⊙ (邻域能流耦合)
    mnq8_update — MNQ8单步更新 (含HEX_RING_GAP/BACKGROUND_OSC判据)
    MNQ8Grid — 仿真网格 (1D/2D/3D拓扑)
    MNQ8Simulation — 完整仿真引擎 (多步迭代 + 统计)

Author: Kou Dou Ma (寇豆码) — 太乙AGI Team
Version: v7.33
"""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 枚举与常量
# ---------------------------------------------------------------------------

class MNQ8State(Enum):
    """MNQ8 节点状态枚举"""
    BACKGROUND_OSC = "BACKGROUND_OSC"   # 弥散基态 (Locked=False)
    HEX_RING_GAP = "HEX_RING_GAP"      # 强耦合囚禁态 (Locked=True)


# ---------------------------------------------------------------------------
# 核心数据结构: 金符3D复广数
# ---------------------------------------------------------------------------

class GoldenSymbol:
    """金符 3D 复广数: z = a + b·i + c·j

    公理体系 (对齐白皮书 App H):
        i² = -1   (波性虚单位)
        j² = -1   (关系相位虚单位)
        i·j = j·i  (交换性公理, 区别于四元数)
        j̄ = j     (关系相位取反保留, 区别于共轭)

    三个分量的物理语义:
        a — 流贯幅值 (构成势投影)
        b — 波性相位 (i 方向)
        c — 关系相位耦合 (j 方向)
    """

    __slots__ = ('a', 'b', 'c')

    def __init__(self, a: float, b: float, c: float):
        self.a = a   # 流贯幅值
        self.b = b   # 波性相位 (i)
        self.c = c   # 关系相位耦合 (j)

    def __add__(self, other: "GoldenSymbol") -> "GoldenSymbol":
        return GoldenSymbol(self.a + other.a, self.b + other.b, self.c + other.c)

    def __sub__(self, other: "GoldenSymbol") -> "GoldenSymbol":
        return GoldenSymbol(self.a - other.a, self.b - other.b, self.c - other.c)

    def __neg__(self) -> "GoldenSymbol":
        return GoldenSymbol(-self.a, -self.b, -self.c)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return (abs(self.a - other.a) < 1e-10 and
                abs(self.b - other.b) < 1e-10 and
                abs(self.c - other.c) < 1e-10)

    def __repr__(self) -> str:
        return f"{self.a:.3f} + {self.b:.3f}i + {self.c:.3f}j"

    def __hash__(self) -> int:
        return hash((round(self.a, 6), round(self.b, 6), round(self.c, 6)))

    def conjugate(self) -> "GoldenSymbol":
        """信息对偶 I <-> Ī (反转波性, 保留关系相位)

        与四元数共轭不同: j̄ = j (关系相位取反保留)
        体现 IDO 信息对偶场: 顺行 Ftel <-> 逆行 Ftel
        """
        return GoldenSymbol(self.a, -self.b, self.c)

    def norm_sq(self) -> float:
        """|z|² = a² + b² + c² (构成势投影)

        对应 MNQ8 中的 MASS_FACE 量度
        """
        return self.a ** 2 + self.b ** 2 + self.c ** 2

    def norm(self) -> float:
        """|z| = sqrt(a² + b² + c²)"""
        return math.sqrt(self.norm_sq())

    def normalized(self) -> "GoldenSymbol":
        """归一化为单位金符 (囚禁锁定后的状态)"""
        n = self.norm()
        if n < 1e-12:
            return GoldenSymbol(0.0, 0.0, 0.0)
        return GoldenSymbol(self.a / n, self.b / n, self.c / n)

    def scale(self, factor: float) -> "GoldenSymbol":
        """标量乘法"""
        return GoldenSymbol(self.a * factor, self.b * factor, self.c * factor)

    def to_dict(self) -> Dict[str, float]:
        """序列化为字典"""
        return {"a": self.a, "b": self.b, "c": self.c}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "GoldenSymbol":
        """从字典反序列化"""
        return cls(data["a"], data["b"], data["c"])

    @classmethod
    def zero(cls) -> "GoldenSymbol":
        """零元素"""
        return cls(0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# 阴龙积 ⊙ (核心: 邻域能流耦合)
# ---------------------------------------------------------------------------

def yin_long_product(z1: GoldenSymbol, z2: GoldenSymbol, lam: float = 1.0) -> GoldenSymbol:
    """阴龙积 ⊙ (App H 定义 H.2.4)

    z1 ⊙ z2 = λ [ (a1*a2 - b1*b2 - c1*c2)
                + i(a1*b2 + b1*a2)
                + j(a1*c2 + c1*a2) ]

    物理语义: 邻域能流耦合 = MNQ8 能流运算的代数抽象
    λ 参数: 139天命矩阵中的耦合强度 (默认1.0)

    定理 T2.32: 交换性公理 — z1 ⊙ z2 = z2 ⊙ z1
        证明: i·j = j·i (公设), 故 a1*b2 + b1*a2 = a2*b1 + b1*a2

    定理 T2.33: 阴龙积结合律 — (z1 ⊙ z2) ⊙ z3 ≠ z1 ⊙ (z2 ⊙ z3) 一般不成立
        注: 阴龙积非结合, 类比八元数; 需刘机制优选(δS_rel=0)约束路径
    """
    real_part = z1.a * z2.a - z1.b * z2.b - z1.c * z2.c
    i_part = z1.a * z2.b + z1.b * z2.a
    j_part = z1.a * z2.c + z1.c * z2.a
    return GoldenSymbol(lam * real_part, lam * i_part, lam * j_part)


# ---------------------------------------------------------------------------
# MNQ8 单步更新律
# ---------------------------------------------------------------------------

def mnq8_update(
    grid: List[GoldenSymbol],
    pos: int,
    neighbors: List[int],
    MASS_THRESHOLD: float = 1.0,
    lam: float = 1.0
) -> Tuple[GoldenSymbol, bool]:
    """MNQ8 能流更新 (白皮书 §3.6 + App H.3.2)

    算法:
        1. 对当前位置的每个邻居, 计算阴龙积(当前, 邻居)
        2. 累加总通量 total_flux
        3. 计算 MASS_FACE = |total_flux|²
        4. 如果 MASS_FACE > THRESHOLD → 囚禁锁定 (HEX_RING_GAP)
           否则 → 回归基态 (BACKGROUND_OSC)

    返回:
        (updated_state, locked_flag)
        locked_flag=True: HEX_RING_GAP (PG鲁珀特之泪孤子)
        locked_flag=False: BACKGROUND_OSC (PG流贯弥散)

    定理 T2.34: MNQ8囚禁判据 —
        若 MASS_FACE > THRESHOLD, 则系统进入囚禁态, 产生PG鲁珀特之泪孤子;
        否则回归背景振荡, 流贯弥散。
    """
    current = grid[pos]
    total_flux = GoldenSymbol.zero()

    for nb in neighbors:
        if 0 <= nb < len(grid):
            total_flux = total_flux + yin_long_product(current, grid[nb], lam=lam)

    mass_face = total_flux.norm_sq()

    if mass_face > MASS_THRESHOLD:
        # HEX_RING_GAP: 囚禁锁定 (PG鲁珀特之泪孤子)
        locked = total_flux.normalized()
        return locked, True
    else:
        # BACKGROUND_OSC: 回归基态 (PG流贯弥散)
        return current, False


# ---------------------------------------------------------------------------
# MNQ8 仿真网格
# ---------------------------------------------------------------------------

class MNQ8Grid:
    """MNQ8 仿真网格

    支持1D/2D/3D拓扑, 预计算邻接关系。
    对应白皮书中的流贯网络离散化表示。
    """

    def __init__(self, topology: str = "1d", size: int = 10):
        """
        Args:
            topology: 网格拓扑 ("1d", "2d", "3d")
            size: 每个维度的节点数 (1D: size, 2D: size×size, 3D: size³)
        """
        self.topology = topology
        self.size = size
        self.grid: List[GoldenSymbol] = []
        self.adjacency: Dict[int, List[int]] = {}
        self._build_grid()
        self._build_adjacency()

    def _build_grid(self):
        """初始化网格节点 (全部弥散基态)"""
        n = self.node_count
        self.grid = [GoldenSymbol(0.1, 0.0, 0.0) for _ in range(n)]

    def _build_adjacency(self):
        """构建邻接关系 (根据拓扑)"""
        if self.topology == "1d":
            for i in range(self.size):
                nbs = []
                if i > 0:
                    nbs.append(i - 1)
                if i < self.size - 1:
                    nbs.append(i + 1)
                self.adjacency[i] = nbs
        elif self.topology == "2d":
            s = self.size
            for r in range(s):
                for c in range(s):
                    idx = r * s + c
                    nbs = []
                    if r > 0: nbs.append((r - 1) * s + c)
                    if r < s - 1: nbs.append((r + 1) * s + c)
                    if c > 0: nbs.append(r * s + (c - 1))
                    if c < s - 1: nbs.append(r * s + (c + 1))
                    self.adjacency[idx] = nbs
        elif self.topology == "3d":
            s = self.size
            for x in range(s):
                for y in range(s):
                    for z in range(s):
                        idx = x * s * s + y * s + z
                        nbs = []
                        if x > 0: nbs.append((x - 1) * s * s + y * s + z)
                        if x < s - 1: nbs.append((x + 1) * s * s + y * s + z)
                        if y > 0: nbs.append(x * s * s + (y - 1) * s + z)
                        if y < s - 1: nbs.append(x * s * s + (y + 1) * s + z)
                        if z > 0: nbs.append(x * s * s + y * s + (z - 1))
                        if z < s - 1: nbs.append(x * s * s + y * s + (z + 1))
                        self.adjacency[idx] = nbs

    @property
    def node_count(self) -> int:
        if self.topology == "1d":
            return self.size
        elif self.topology == "2d":
            return self.size * self.size
        elif self.topology == "3d":
            return self.size ** 3
        return self.size

    def set_node(self, idx: int, gs: GoldenSymbol):
        """设置指定节点的金符值"""
        if 0 <= idx < len(self.grid):
            self.grid[idx] = gs

    def inject_hex_ring_gap(self, center_idx: int, radius: int = 1):
        """在指定位置注入HEX_RING_GAP囚禁候选

        对应白皮书: 缺口六边形类拓扑, 高构成势 + 强关系耦合
        """
        gs_strong = GoldenSymbol(0.9, 0.0, 0.8)
        if 0 <= center_idx < len(self.grid):
            self.grid[center_idx] = gs_strong
        # 邻居也注入较强耦合
        for nb in self.adjacency.get(center_idx, []):
            self.grid[nb] = GoldenSymbol(0.6, 0.0, 0.5)

    def to_dict(self) -> Dict[str, Any]:
        """序列化网格状态"""
        states = []
        for i, gs in enumerate(self.grid):
            state_dict = gs.to_dict()
            state_dict["idx"] = i
            state_dict["neighbors"] = self.adjacency.get(i, [])
            states.append(state_dict)
        return {
            "topology": self.topology,
            "size": self.size,
            "node_count": self.node_count,
            "states": states,
        }


# ---------------------------------------------------------------------------
# MNQ8 仿真引擎
# ---------------------------------------------------------------------------

@dataclass
class MNQ8StepResult:
    """MNQ8 单步更新结果"""
    step: int
    locked_count: int = 0
    dispersed_count: int = 0
    max_mass_face: float = 0.0
    avg_mass_face: float = 0.0
    hex_ring_gap_nodes: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "locked_count": self.locked_count,
            "dispersed_count": self.dispersed_count,
            "max_mass_face": round(self.max_mass_face, 6),
            "avg_mass_face": round(self.avg_mass_face, 6),
            "hex_ring_gap_nodes": self.hex_ring_gap_nodes,
        }


class MNQ8Simulation:
    """MNQ8 完整仿真引擎

    多步迭代 + 统计分析, 对应白皮书 §3.6 的 MNQ v12/v13 数值验证。

    核心能力:
        - 多步MNQ8更新 (β-归约迭代)
        - HEX_RING_GAP / BACKGROUND_OSC 自动分类
        - MASS_FACE / EXCESS_LOOP 统计
        - 仿真结果序列化
    """

    def __init__(self, grid: MNQ8Grid, mass_threshold: float = 1.0, lam: float = 1.0):
        self.grid = grid
        self.mass_threshold = mass_threshold
        self.lam = lam
        self.history: List[MNQ8StepResult] = []
        self.locked_map: Dict[int, bool] = {}  # idx -> is_locked

    def step(self) -> MNQ8StepResult:
        """执行一次MNQ8更新 (全部节点同步更新)"""
        new_grid = list(self.grid.grid)  # 浅拷贝
        locked_count = 0
        dispersed_count = 0
        mass_faces = []
        hex_ring_gap_nodes = []

        for idx in range(len(self.grid.grid)):
            neighbors = self.grid.adjacency.get(idx, [])
            new_state, locked = mnq8_update(
                self.grid.grid, idx, neighbors,
                MASS_THRESHOLD=self.mass_threshold,
                lam=self.lam
            )
            new_grid[idx] = new_state
            self.locked_map[idx] = locked

            # 计算MASS_FACE (用于统计)
            current = self.grid.grid[idx]
            total_flux = GoldenSymbol.zero()
            for nb in neighbors:
                if 0 <= nb < len(self.grid.grid):
                    total_flux = total_flux + yin_long_product(current, self.grid.grid[nb], lam=self.lam)
            mf = total_flux.norm_sq()
            mass_faces.append(mf)

            if locked:
                locked_count += 1
                hex_ring_gap_nodes.append(idx)
            else:
                dispersed_count += 1

        self.grid.grid = new_grid

        result = MNQ8StepResult(
            step=len(self.history) + 1,
            locked_count=locked_count,
            dispersed_count=dispersed_count,
            max_mass_face=max(mass_faces) if mass_faces else 0.0,
            avg_mass_face=sum(mass_faces) / len(mass_faces) if mass_faces else 0.0,
            hex_ring_gap_nodes=hex_ring_gap_nodes,
        )
        self.history.append(result)
        return result

    def run(self, steps: int = 100) -> List[MNQ8StepResult]:
        """运行多步仿真"""
        results = []
        for _ in range(steps):
            result = self.step()
            results.append(result)
        return results

    def get_excess_loop(self) -> float:
        """计算 EXCESS_LOOP (锁定节点占比)

        对应白皮书: EXCESS_LOOP > 0 意味着存在囚禁孤子
        """
        if not self.locked_map:
            return 0.0
        locked = sum(1 for v in self.locked_map.values() if v)
        return locked / len(self.locked_map)

    def get_statistics(self) -> Dict[str, Any]:
        """获取仿真统计信息"""
        last = self.history[-1] if self.history else None
        return {
            "total_steps": len(self.history),
            "node_count": self.grid.node_count,
            "mass_threshold": self.mass_threshold,
            "lam": self.lam,
            "excess_loop": round(self.get_excess_loop(), 6),
            "last_step": last.to_dict() if last else None,
            "locked_ratio": round(self.get_excess_loop(), 4),
        }

    def to_dict(self) -> Dict[str, Any]:
        """完整序列化"""
        return {
            "grid": self.grid.to_dict(),
            "statistics": self.get_statistics(),
            "history": [h.to_dict() for h in self.history[-10:]],  # 最近10步
        }


# ---------------------------------------------------------------------------
# 对照实验: HEX_RING_GAP vs BACKGROUND_OSC
# ---------------------------------------------------------------------------

def run_comparison_experiment(mass_threshold: float = 1.0) -> Dict[str, Any]:
    """运行 HEX_RING_GAP vs BACKGROUND_OSC 对照实验

    对应白皮书 §3.6 的 MNQ v12/v13 数值验证实验。

    实验设计:
        1. HEX_RING_GAP: 中心强耦合 (高构成势 + 强关系耦合) → 囚禁锁定
        2. BACKGROUND_OSC: 全部弥散基态 → 回归弥散

    预期结果 (对齐白皮书):
        HEX_RING_GAP: Locked=True, |z|²≈1.0
        BACKGROUND_OSC: Locked=False, |z|²≈0.01
    """

    # === HEX_RING_GAP 实验 ===
    grid_hex = MNQ8Grid(topology="1d", size=4)
    grid_hex.set_node(1, GoldenSymbol(0.9, 0.0, 0.8))  # 高构成势 + 强关系耦合
    grid_hex.set_node(2, GoldenSymbol(0.9, 0.0, 0.8))

    state_hex, locked_hex = mnq8_update(grid_hex.grid, 1, [0, 2], MASS_THRESHOLD=mass_threshold)

    # === BACKGROUND_OSC 实验 ===
    grid_bg = MNQ8Grid(topology="1d", size=3)
    # 默认全是 0.1 + 0i + 0j

    state_bg, locked_bg = mnq8_update(grid_bg.grid, 1, [0, 2], MASS_THRESHOLD=mass_threshold)

    return {
        "hex_ring_gap": {
            "state": str(state_hex),
            "norm_sq": round(state_hex.norm_sq(), 6),
            "locked": locked_hex,
            "classification": MNQ8State.HEX_RING_GAP.value if locked_hex else MNQ8State.BACKGROUND_OSC.value,
        },
        "background_osc": {
            "state": str(state_bg),
            "norm_sq": round(state_bg.norm_sq(), 6),
            "locked": locked_bg,
            "classification": MNQ8State.HEX_RING_GAP.value if locked_bg else MNQ8State.BACKGROUND_OSC.value,
        },
        "mass_threshold": mass_threshold,
        "consistent_with_whitepaper": locked_hex and not locked_bg,
    }


# ---------------------------------------------------------------------------
# 定理验证
# ---------------------------------------------------------------------------

def verify_theorem_t232() -> Dict[str, Any]:
    """验证定理 T2.32: 金符交换性公理 — z1 ⊙ z2 = z2 ⊙ z1

    证明: 阴龙积定义中 i·j = j·i (公设),
    因此 a1*b2 + b1*a2 = a2*b1 + b1*a2 (交换律成立)
    """
    z1 = GoldenSymbol(0.7, 0.3, 0.5)
    z2 = GoldenSymbol(0.4, 0.6, 0.2)
    p12 = yin_long_product(z1, z2)
    p21 = yin_long_product(z2, z1)
    passed = p12 == p21
    return {
        "theorem": "T2.32",
        "name": "金符交换性公理",
        "z1": str(z1),
        "z2": str(z2),
        "z1⊙z2": str(p12),
        "z2⊙z1": str(p21),
        "passed": passed,
    }


def verify_theorem_t233() -> Dict[str, Any]:
    """验证定理 T2.33: 阴龙积结合律 — (z1⊙z2)⊙z3 ≠ z1⊙(z2⊙z3) 一般不成立

    注: 阴龙积非结合, 类比八元数; 需刘机制优选(δS_rel=0)约束路径
    """
    z1 = GoldenSymbol(1.0, 0.5, 0.3)
    z2 = GoldenSymbol(0.8, 0.2, 0.6)
    z3 = GoldenSymbol(0.3, 0.7, 0.4)
    p12_3 = yin_long_product(yin_long_product(z1, z2), z3)
    p1_23 = yin_long_product(z1, yin_long_product(z2, z3))
    not_associative = p12_3 != p1_23
    return {
        "theorem": "T2.33",
        "name": "阴龙积非结合性",
        "(z1⊙z2)⊙z3": str(p12_3),
        "z1⊙(z2⊙z3)": str(p1_23),
        "not_associative": not_associative,
        "passed": not_associative,  # 预期: 非结合
    }


def verify_theorem_t234(mass_threshold: float = 1.0) -> Dict[str, Any]:
    """验证定理 T2.34: MNQ8囚禁判据

    若 MASS_FACE > THRESHOLD, 系统进入囚禁态(HEX_RING_GAP);
    否则回归背景振荡(BACKGROUND_OSC)。
    """
    exp = run_comparison_experiment(mass_threshold=mass_threshold)
    passed = exp["consistent_with_whitepaper"]
    return {
        "theorem": "T2.34",
        "name": "MNQ8囚禁判据",
        "hex_ring_gap_locked": exp["hex_ring_gap"]["locked"],
        "background_osc_locked": exp["background_osc"]["locked"],
        "consistent_with_whitepaper": passed,
        "passed": passed,
    }


def verify_all_theorems() -> Dict[str, Any]:
    """运行全部定理验证"""
    t232 = verify_theorem_t232()
    t233 = verify_theorem_t233()
    t234 = verify_theorem_t234()
    all_pass = t232["passed"] and t233["passed"] and t234["passed"]
    return {
        "T2.32": t232,
        "T2.33": t233,
        "T2.34": t234,
        "all_passed": all_pass,
        "summary": f"{'✅ ALL PASS' if all_pass else '❌ SOME FAILED'}: T2.32={t232['passed']}, T2.33={t233['passed']}, T2.34={t234['passed']}",
    }


# ---------------------------------------------------------------------------
# 模块状态接口 (供Blueprint调用)
# ---------------------------------------------------------------------------

_instance: Optional["M223State"] = None


class M223State:
    """模块级状态容器"""

    def __init__(self):
        self.grid: Optional[MNQ8Grid] = None
        self.simulation: Optional[MNQ8Simulation] = None
        self.theorem_results: Dict[str, Any] = {}

    def get_state(self) -> Dict[str, Any]:
        return {
            "module": "M223_GoldenSymbol3D",
            "version": "v7.33",
            "grid_active": self.grid is not None,
            "simulation_active": self.simulation is not None,
            "theorem_results": self.theorem_results,
        }


def get_instance() -> M223State:
    """获取模块单例"""
    global _instance
    if _instance is None:
        _instance = M223State()
    return _instance
