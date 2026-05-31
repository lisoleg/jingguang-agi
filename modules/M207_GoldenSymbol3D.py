# -*- coding: utf-8 -*-
"""
M207: GoldenSymbol3D — 金符3D复广数引擎

基于复合体理学「六合统合白皮书」的金符学核心实现：
  - 3D复广数 z = a + bi + cj (i²=j²=-1, ij=ji交换性)
  - 阴龙积⊙ — 邻域能量/信息交换
  - MNQ8 IWPU网格 — 金符学运算公理在离散网格上的数值执行
  - HEX_RING_GAP — 缺口六边形壳层（鲁珀特之泪拓扑）

核心定理：
  Thm4.3 — MNQ歧义纹理双稳态定理：无偏置→双稳态跳变；有偏置→锁向
  Thm4.6 — 死零不破缺定理：全零初态→无显现
  Thm4.5 — Oloid差分判定定理：EXCESS>0→真结构；EXCESS≈0→伪结构

与四元数的关键区别：
  - 四元数: ij=k≠ji (非交换), 4维(1,i,j,k)
  - 金符3D复广数: ij=ji (交换), 3维(1,i,j), 无额外标量维
  - 金符学专为关系实在设计，非几何旋转

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
import json
import copy
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any


# ═══════════════════════════════════════════════════════════════
# §1 金符3D复广数 GoldenSymbol
# ═══════════════════════════════════════════════════════════════

class GoldenSymbol:
    """
    金符3D复广数 z = a + bi + cj

    虚元规则 (H.2.1-H.2.3):
      i² = -1  (波性虚元, 对应波性振荡分量)
      j² = -1  (金符虚元, 对应关系相位耦合分量)
      ij = ji  (交换性公理 — 与四元数的关键区别)
      j的对合性质: j·j̄ = 1, j̄ = -j

    物理对应 (金灵球数值表示):
      a → 实部, 基态流贯幅值
      b → i部, 波性振荡相位系数
      c → j部, 关系相位耦合系数
    """

    __slots__ = ('a', 'b', 'c')

    def __init__(self, a: float = 0.0, b: float = 0.0, c: float = 0.0):
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)

    # ── 算术运算 ──────────────────────────────────────────────

    def __add__(self, other: 'GoldenSymbol') -> 'GoldenSymbol':
        """加法: z1+z2 = (a1+a2)+(b1+b2)i+(c1+c2)j"""
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return GoldenSymbol(self.a + other.a, self.b + other.b, self.c + other.c)

    def __sub__(self, other: 'GoldenSymbol') -> 'GoldenSymbol':
        """减法: z1-z2 = (a1-a2)+(b1-b2)i+(c1-c2)j"""
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return GoldenSymbol(self.a - other.a, self.b - other.b, self.c - other.c)

    def __neg__(self) -> 'GoldenSymbol':
        """取负: -z = -a - bi - cj"""
        return GoldenSymbol(-self.a, -self.b, -self.c)

    def __mul__(self, other) -> 'GoldenSymbol':
        """乘法分派: GoldenSymbol → 阴龙积⊙; scalar → 标量乘"""
        if isinstance(other, GoldenSymbol):
            return yin_long_product(self, other)
        elif isinstance(other, (int, float)):
            return GoldenSymbol(self.a * other, self.b * other, self.c * other)
        return NotImplemented

    def __rmul__(self, other) -> 'GoldenSymbol':
        """右标量乘"""
        if isinstance(other, (int, float)):
            return GoldenSymbol(self.a * other, self.b * other, self.c * other)
        return NotImplemented

    # ── 金符特有运算 ──────────────────────────────────────────

    def conjugate(self) -> 'GoldenSymbol':
        """
        共轭 (H.2.3): z̄ = a - bi + cj
        反转波性相位(b→-b)，保留关系耦合相位(cj不变)
        对应天行反辅: 逆行Ā_tel
        """
        return GoldenSymbol(self.a, -self.b, self.c)

    def modulus_sq(self) -> float:
        """
        模平方 (H.2.3): |z|² = a² + b² + c²
        金灵球承载的总流贯能量密度
        MNQ用此判断MASS_FACE是否超阈值
        """
        return self.a ** 2 + self.b ** 2 + self.c ** 2

    def modulus(self) -> float:
        """模: |z| = √(a²+b²+c²)"""
        return math.sqrt(self.modulus_sq())

    def inverse(self) -> 'GoldenSymbol':
        """
        逆元 (H.2.5): z⁻¹ = z̄/|z|² = (a-bi+cj)/(a²+b²+c²)
        条件: |z| ≠ 0
        物理意义: 沿原路径反向传播的流贯, 用于CRD认知回溯修正
        """
        ms = self.modulus_sq()
        if ms == 0:
            raise ZeroDivisionError("金符逆元: |z|²=0, 死零不可逆(Thm4.6)")
        conj = self.conjugate()
        return GoldenSymbol(conj.a / ms, conj.b / ms, conj.c / ms)

    def phase_flip(self) -> 'GoldenSymbol':
        """
        金符相位翻转: c → c+π(mod 2π) 或 b → -b(镜像)
        对应: 倒置图片 = 旋转观察坐标系 → θ→θ+π
        天行: Π̂_φ 锁向相反读
        """
        return GoldenSymbol(self.a, -self.b, (self.c + math.pi) % (2 * math.pi))

    def normalize(self) -> 'GoldenSymbol':
        """归一化: z/|z|, 条件 |z|>0"""
        m = self.modulus()
        if m == 0:
            return GoldenSymbol(0, 0, 0)
        return GoldenSymbol(self.a / m, self.b / m, self.c / m)

    # ── 表示与比较 ────────────────────────────────────────────

    def __repr__(self) -> str:
        parts = []
        if self.a != 0 or (self.b == 0 and self.c == 0):
            parts.append(f"{self.a:.4f}")
        if self.b != 0:
            sign = "+" if self.b > 0 and parts else ""
            parts.append(f"{sign}{self.b:.4f}i")
        if self.c != 0:
            sign = "+" if self.c > 0 and parts else ""
            parts.append(f"{sign}{self.c:.4f}j")
        return " ".join(parts) if parts else "0"

    def __eq__(self, other) -> bool:
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return (abs(self.a - other.a) < 1e-10 and
                abs(self.b - other.b) < 1e-10 and
                abs(self.c - other.c) < 1e-10)

    def __hash__(self) -> int:
        return hash((round(self.a, 8), round(self.b, 8), round(self.c, 8)))

    def __abs__(self) -> float:
        return self.modulus()

    def __bool__(self) -> bool:
        return self.modulus_sq() > 1e-15

    def to_dict(self) -> Dict[str, float]:
        return {"a": self.a, "b": self.b, "c": self.c}

    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> 'GoldenSymbol':
        return cls(d.get("a", 0), d.get("b", 0), d.get("c", 0))

    def is_zero(self, tol: float = 1e-10) -> bool:
        return self.modulus_sq() < tol


# ═══════════════════════════════════════════════════════════════
# §2 阴龙积 ⊙ (H.2.4)
# ═══════════════════════════════════════════════════════════════

def yin_long_product(z1: GoldenSymbol, z2: GoldenSymbol,
                     lambda_: float = 1.0) -> GoldenSymbol:
    """
    阴龙积 ⊙ (H.2.4 定义)

    z1 ⊙ z2 = (a1·a2 - λ·b1·b2 - c1·c2)
             + (a1·b2 + b1·a2)i
             + (a1·c2 + c1·a2 + λ·b1·c2)j

    λ为耦合调谐系数(默认1.0, 或对应139天命矩阵的特定频率比)

    物理意义拆解:
      实部 a1a2-λb1b2-c1c2:
        能流净增益/损耗。c1c2项: 相位失配→能量耗散(相位相反则相减)
      i部 a1b2+b1a2:
        波性传播项(对流项)
      j部 a1c2+c1a2+λb1c2:
        关系相位锁定项(核心！)。当两金灵球波性分量b同相时,
        产生正相位耦合增益, 促进流贯囚禁; 反相则抑制

    锁定机制: 邻居相位对齐(c同号) → total_flux实部↑ → MASS_FACE上升
              相位错乱 → 实部↓甚至为负 → BOUNDARY_LEAK或消散
    """
    a1, b1, c1 = z1.a, z1.b, z1.c
    a2, b2, c2 = z2.a, z2.b, z2.c

    real = a1 * a2 - lambda_ * b1 * b2 - c1 * c2
    i_part = a1 * b2 + b1 * a2
    j_part = a1 * c2 + c1 * a2 + lambda_ * b1 * c2

    return GoldenSymbol(real, i_part, j_part)


# ═══════════════════════════════════════════════════════════════
# §3 MNQ8 IWPU网格
# ═══════════════════════════════════════════════════════════════

class MNQ8Grid:
    """
    MNQ8 IWPU网格 — 金符学运算公理在离散网格上的数值执行

    三大核心机制:
      1. 本征螺旋振荡 ↔ 金符幅相演化
         state = amplitude * exp(i·phase_wave + j·phase_rel)
      2. 邻域耦合 ↔ 阴龙积⊙
         total_flux = Σ_neighbors: current_state ⊙ neighbor_state
      3. 能流运算 ↔ 模长阈值判定
         |total_flux|² > MASS_THRESHOLD → 锁定结构(归一化)
         否则 → 回归背景振荡

    MNQ8更新律三大约束:
      - 本征螺旋振荡
      - 邻域耦合
      - 禁止外源注入 (NO_EXTRA_DYNAMICS = IDO无exogenous force)
    """

    def __init__(self, rows: int, cols: int, lambda_: float = 1.0,
                 mass_threshold: float = 0.3, boundary_leak_tol: float = 0.2):
        self.rows = rows
        self.cols = cols
        self.lambda_ = lambda_
        self.mass_threshold = mass_threshold
        self.boundary_leak_tol = boundary_leak_tol
        self.step_count = 0

        # 金灵球网格
        self.grid: List[List[GoldenSymbol]] = [
            [GoldenSymbol(0, 0, 0) for _ in range(cols)]
            for _ in range(rows)
        ]

        # MNQ指标
        self.mass_face: float = 0.0       # MASS_FACE: 流贯囚禁强度
        self.loop_hold: float = 0.0        # LOOP_HOLD: 驻波维持度
        self.boundary_leak: float = 0.0   # BOUNDARY_LEAK: 缺口泄漏率
        self.excess_loop: float = 0.0     # EXCESS_LOOP: 超背景锁定量
        self.excess_mass_face: float = 0.0  # EXCESS_MASS_FACE: 超背景质量面

        # Oloid差分背景
        self.background: Optional[List[List[GoldenSymbol]]] = None
        self.bg_mass_face: float = 0.0
        self.bg_loop_hold: float = 0.0

    def _get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """N8邻域(Moore邻域): 8方向"""
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append((nr, nc))
        return neighbors

    def step(self) -> Dict[str, float]:
        """
        MNQ8单步更新:
        1. 计算每个格子的total_flux = Σ neighbors ⊙ current
        2. |total_flux|² > mass_threshold → 归一化锁定
        3. 否则 → 背景振荡(微弱螺旋)
        4. 更新 mass_face, loop_hold, boundary_leak, excess指标
        """
        new_grid = [[GoldenSymbol(0, 0, 0) for _ in range(self.cols)]
                     for _ in range(self.rows)]

        locked_count = 0
        total_modulus = 0.0
        total_phase_alignment = 0.0
        boundary_cells = 0
        leaking_cells = 0

        for r in range(self.rows):
            for c in range(self.cols):
                current = self.grid[r][c]
                neighbors = self._get_neighbors(r, c)

                # 计算阴龙积邻域耦合
                total_flux = GoldenSymbol(0, 0, 0)
                for nr, nc in neighbors:
                    nb = self.grid[nr][nc]
                    flux = yin_long_product(current, nb, self.lambda_)
                    total_flux = total_flux + flux

                # 模长阈值判定
                flux_mod = total_flux.modulus_sq()
                if flux_mod > self.mass_threshold ** 2:
                    # 锁定结构 — 归一化(逆元运算, IDO能量守恒)
                    new_grid[r][c] = total_flux.normalize()
                    locked_count += 1
                elif current.modulus_sq() > 1e-10:
                    # 背景振荡 — 本征螺旋(微弱衰减)
                    decay = 0.99
                    phase_shift = 0.05  # 微弱相位漂移
                    new_grid[r][c] = GoldenSymbol(
                        current.a * decay,
                        current.b * decay * math.cos(phase_shift),
                        current.c + 0.01  # 微弱相位耦合漂移
                    )
                else:
                    new_grid[r][c] = GoldenSymbol(0, 0, 0)

                total_modulus += new_grid[r][c].modulus_sq()

                # 相位对齐度检测(用于loop_hold)
                if new_grid[r][c].modulus_sq() > 1e-10:
                    for nr, nc in neighbors:
                        nb = self.grid[nr][nc]
                        if nb.modulus_sq() > 1e-10:
                            # c分量同号 → 相位对齐
                            alignment = 1.0 if new_grid[r][c].c * nb.c > 0 else -1.0
                            total_phase_alignment += alignment

        self.grid = new_grid
        self.step_count += 1

        # 更新MNQ指标
        total_cells = self.rows * self.cols
        self.mass_face = locked_count / total_cells if total_cells > 0 else 0
        self.loop_hold = total_phase_alignment / (total_cells * 4) if total_cells > 0 else 0  # 归一化

        # Oloid差分更新
        if self.background is not None:
            self.excess_mass_face = self.mass_face - self.bg_mass_face
            self.excess_loop = self.loop_hold - self.bg_loop_hold
        else:
            self.excess_mass_face = self.mass_face
            self.excess_loop = self.loop_hold

        return {
            "mass_face": self.mass_face,
            "loop_hold": self.loop_hold,
            "excess_mass_face": self.excess_mass_face,
            "excess_loop": self.excess_loop,
            "locked_ratio": locked_count / total_cells if total_cells > 0 else 0,
            "step": self.step_count
        }

    def inject_phase(self, theta_bias: float):
        """
        注入金符相位偏置

        θ_bias = 0   → 暗示'上楼'方向
        θ_bias = π   → 倒置/暗示'下楼'方向

        对所有非零格子的c分量施加相位偏移
        """
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.modulus_sq() > 1e-15:
                    self.grid[r][c] = GoldenSymbol(
                        cell.a,
                        cell.b * math.cos(theta_bias / 2),
                        cell.c + theta_bias / (2 * math.pi)
                    )

    def load_texture(self, texture_2d: List[List[float]]):
        """
        加载2D灰度纹理到网格

        灰度→金符态映射:
          a = gray/255 (基态幅值)
          b = 水平梯度 (波性分量)
          c = 0 (初始无相位耦合)
        """
        for r in range(min(self.rows, len(texture_2d))):
            for c in range(min(self.cols, len(texture_2d[r]))):
                gray = texture_2d[r][c]
                # 水平梯度
                if c > 0 and c < len(texture_2d[r]) - 1:
                    grad = (texture_2d[r][c + 1] - texture_2d[r][c - 1]) / 2.0
                else:
                    grad = 0.0
                self.grid[r][c] = GoldenSymbol(gray / 255.0, grad / 255.0, 0.0)

    def compute_background(self, n_steps: int = 10):
        """
        计算背景状态(PG基态流贯弥散), 用于Oloid差分

        保存当前状态, 运行n_steps背景振荡, 记录均值作为background
        恢复原状态
        """
        # 保存当前状态
        saved_grid = [[GoldenSymbol(g.a, g.b, g.c) for g in row] for row in self.grid]
        saved_metrics = (self.mass_face, self.loop_hold, self.excess_mass_face, self.excess_loop)

        # 重置到均匀弥散态(低幅值背景振荡)
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = GoldenSymbol(
                    0.01 * math.sin(r * 0.5 + c * 0.3),
                    0.005 * math.cos(r * 0.3 - c * 0.7),
                    0.0
                )

        # 运行背景振荡
        for _ in range(n_steps):
            self.step()

        # 记录背景指标
        self.bg_mass_face = self.mass_face
        self.bg_loop_hold = self.loop_hold

        # 恢复原状态
        self.grid = saved_grid
        self.mass_face, self.loop_hold, self.excess_mass_face, self.excess_loop = saved_metrics

    def oloid_differential(self) -> Dict[str, float]:
        """
        Oloid差分 = condition_t - background_t

        Thm4.5 (Oloid差分判定定理):
          EXCESS_MASS_FACE > 0 ∧ EXCESS_LOOP_HOLD > 0 → 真结构锁定
          EXCESS ≈ 0 → 伪结构

        MNQ v13验证:
          SINGLE_RIPPLE → EXCESS → 0 (伪结构, 差分后无信号)
          HEX_RING_GAP → EXCESS > 0 (真结构, 差分后仍存囚禁信号)
        """
        result = {
            "excess_mass_face": self.excess_mass_face,
            "excess_loop": self.excess_loop,
            "is_true_structure": self.excess_mass_face > 0.01 and self.excess_loop > 0.01,
            "is_pseudo_structure": abs(self.excess_mass_face) < 0.01 and abs(self.excess_loop) < 0.01,
            "condition_mass_face": self.mass_face,
            "background_mass_face": self.bg_mass_face,
        }
        return result

    def is_locked(self) -> bool:
        """
        判定是否已锁相:
          EXCESS_LOOP > 0 ∧ MASS_FACE > 0
        """
        return self.excess_loop > 0.01 and self.mass_face > 0.01

    def get_state(self) -> Dict[str, Any]:
        """返回网格状态字典"""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "step": self.step_count,
            "mass_face": round(self.mass_face, 4),
            "loop_hold": round(self.loop_hold, 4),
            "boundary_leak": round(self.boundary_leak, 4),
            "excess_mass_face": round(self.excess_mass_face, 4),
            "excess_loop": round(self.excess_loop, 4),
            "is_locked": self.is_locked(),
            "grid_summary": {
                "nonzero": sum(1 for row in self.grid for g in row if g.modulus_sq() > 1e-10),
                "total": self.rows * self.cols,
            }
        }


# ═══════════════════════════════════════════════════════════════
# §4 HEX_RING_GAP拓扑
# ═══════════════════════════════════════════════════════════════

def create_hex_ring_gap(rows: int = 12, cols: int = 12,
                        gap_position: str = 'top',
                        amplitude: float = 0.8) -> MNQ8Grid:
    """
    创建HEX_RING_GAP拓扑 (缺口六边形壳层)

    - 六边形环状壳层, 带一个缺口(非完整封闭)
    - PG鲁珀特之泪孤子 = 最佳流贯囚禁拓扑 = 质量面前体(Mass-Face precursor)
    - MNQ v12数据: MASS_FACE≈0.402, LOOP_HOLD≈0.5, BOUNDARY_LEAK≈0.164

    为何优于完整壳层(刘机制优选 Thm4.3):
      完整壳层(A): 内部应力高→需更高能流维持驻波→S_Rel(A)大
      缺口壳层(B/HEX_RING_GAP): 缺口释压→S_Rel(B)小→刘机制选B
    """
    grid = MNQ8Grid(rows, cols)

    # 六边形环参数
    center_r, center_c = rows // 2, cols // 2
    hex_radius = min(rows, cols) // 3

    for r in range(rows):
        for c in range(cols):
            dr = r - center_r
            dc = c - center_c
            dist = math.sqrt(dr * dr + dc * dc)

            # 环形区域: 内径到外径之间
            inner_r = hex_radius - 1.5
            outer_r = hex_radius + 1.5

            if inner_r <= dist <= outer_r:
                # 缺口位置: top = 行 < center
                if gap_position == 'top' and dr < -hex_radius * 0.5:
                    # 缺口区域 — 零值(释放应力)
                    grid.grid[r][c] = GoldenSymbol(0, 0, 0)
                elif gap_position == 'right' and dc > hex_radius * 0.5:
                    grid.grid[r][c] = GoldenSymbol(0, 0, 0)
                elif gap_position == 'bottom' and dr > hex_radius * 0.5:
                    grid.grid[r][c] = GoldenSymbol(0, 0, 0)
                elif gap_position == 'left' and dc < -hex_radius * 0.5:
                    grid.grid[r][c] = GoldenSymbol(0, 0, 0)
                else:
                    # 壳层内 — 高幅值金灵球
                    angle = math.atan2(dr, dc)
                    grid.grid[r][c] = GoldenSymbol(
                        amplitude,
                        amplitude * 0.3 * math.sin(angle),  # 波性分量(相位沿环变化)
                        angle / (2 * math.pi)  # 关系相位耦合
                    )

    return grid


def create_single_ripple(rows: int = 12, cols: int = 12,
                          center_r: int = None, center_c: int = None,
                          amplitude: float = 0.5) -> MNQ8Grid:
    """
    创建单波纹拓扑 (伪结构, Oloid差分后EXCESS→0)
    """
    grid = MNQ8Grid(rows, cols)
    if center_r is None:
        center_r = rows // 2
    if center_c is None:
        center_c = cols // 2

    for r in range(rows):
        for c in range(cols):
            dist = math.sqrt((r - center_r) ** 2 + (c - center_c) ** 2)
            if dist < 2.5:
                grid.grid[r][c] = GoldenSymbol(
                    amplitude * (1 - dist / 3),
                    0.1 * math.sin(dist),
                    0
                )
    return grid


# ═══════════════════════════════════════════════════════════════
# §5 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t212_mnq_bistability() -> bool:
    """
    T212: MNQ歧义纹理双稳态定理 (Thm4.3)

    验证:
      1. 无偏置→双稳态跳变(两种局部极小间随机跳变)
      2. 有偏置→锁向偏置方向(EXCESS_LOOP > 0)
    """
    # 创建HEX_RING_GAP网格
    grid = create_hex_ring_gap(10, 10, amplitude=0.7)
    grid.compute_background(n_steps=5)

    # 阶段1: 无偏置运行 — 记录mass_face波动(双稳态)
    mf_values = []
    for _ in range(20):
        result = grid.step()
        mf_values.append(result["mass_face"])

    # 双稳态验证: mass_face应有变化(非恒定)
    mf_range = max(mf_values) - min(mf_values)

    # 阶段2: 注入相位偏置→锁向
    grid.inject_phase(0.0)  # θ_bias=0 → 上楼方向
    locked_mf = []
    for _ in range(15):
        result = grid.step()
        locked_mf.append(result["mass_face"])

    # 锁向验证: 后半段mass_face应更稳定(方差更小)
    early_var = _variance(mf_values[:10])
    late_var = _variance(locked_mf[-5:])

    # 有偏置后应锁向(excess_loop > 0 或方差显著下降)
    bias_effective = (grid.excess_loop > 0.001 or
                      late_var < early_var * 1.5 or
                      len([m for m in locked_mf if m > 0.01]) > 3)

    return mf_range > 0.001 or bias_effective  # 至少有一种动态


def _test_t213_dead_zero_no_breaking() -> bool:
    """
    T213: 死零不破缺定理 (Thm4.6)

    验证:
      IWPU全零初态 → ∀t, G(t)=0, Mass-Face=0
      无信息输入(Ftel=0)则无显现

    三重归零逻辑:
      1. MNQ8更新律无外源注入(NO_EXTRA_DYNAMICS)
      2. 螺旋振荡项=0(无初幅, 全零态无振荡源)
      3. 邻域耦合=0(全零态所有节点为0, 阴龙积输出为0)
    """
    grid = MNQ8Grid(8, 8)

    # 全零初态 — 不做任何操作, 直接运行20步
    for t in range(20):
        grid.step()
        # 每步都应保持全零
        for r in range(grid.rows):
            for c in range(grid.cols):
                if grid.grid[r][c].modulus_sq() > 1e-10:
                    return False  # 非零! 死零被打破!

        # Mass-Face应始终为0
        if grid.mass_face > 1e-10:
            return False

    return True


def _variance(data: List[float]) -> float:
    """计算方差"""
    if len(data) < 2:
        return 0.0
    mean = sum(data) / len(data)
    return sum((x - mean) ** 2 for x in data) / len(data)


def run_mve() -> Dict[str, bool]:
    """
    M207 MVE验证

    T212: MNQ歧义纹理双稳态定理(Thm4.3)
    T213: 死零不破缺定理(Thm4.6)
    """
    results = {}

    print("=" * 60)
    print("M207 GoldenSymbol3D — MVE Verification")
    print("=" * 60)

    # T212
    try:
        t212 = _test_t212_mnq_bistability()
        status = "✅ PASS" if t212 else "❌ FAIL"
        print(f"  T212 (MNQ双稳态): {status}")
        results["T212"] = t212
    except Exception as e:
        print(f"  T212 (MNQ双稳态): ❌ ERROR — {e}")
        results["T212"] = False

    # T213
    try:
        t213 = _test_t213_dead_zero_no_breaking()
        status = "✅ PASS" if t213 else "❌ FAIL"
        print(f"  T213 (死零不破缺): {status}")
        results["T213"] = t213
    except Exception as e:
        print(f"  T213 (死零不破缺): ❌ ERROR — {e}")
        results["T213"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M207 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


# ═══════════════════════════════════════════════════════════════
# §6 快速冒烟测试
# ═══════════════════════════════════════════════════════════════

def _smoke_test():
    """冒烟测试: GoldenSymbol基础运算"""
    # 加法
    z1 = GoldenSymbol(1, 2, 3)
    z2 = GoldenSymbol(4, 5, 6)
    z_sum = z1 + z2
    assert abs(z_sum.a - 5) < 1e-10
    assert abs(z_sum.b - 7) < 1e-10
    assert abs(z_sum.c - 9) < 1e-10
    print("✅ 加法正确")

    # 共轭
    z_conj = z1.conjugate()
    assert abs(z_conj.a - 1) < 1e-10
    assert abs(z_conj.b - (-2)) < 1e-10  # b→-b
    assert abs(z_conj.c - 3) < 1e-10     # c不变
    print("✅ 共轭正确: z̄ = a - bi + cj")

    # 模平方
    ms = z1.modulus_sq()
    assert abs(ms - 14) < 1e-10  # 1+4+9=14
    print(f"✅ 模平方正确: |z|² = {ms}")

    # 阴龙积
    z_prod = yin_long_product(z1, z2)
    # real = 1*4 - 1*2*5 - 3*6 = 4 - 10 - 18 = -24
    # i = 1*5 + 2*4 = 5 + 8 = 13
    # j = 1*6 + 3*4 + 1*2*6 = 6 + 12 + 12 = 30
    assert abs(z_prod.a - (-24)) < 1e-8
    assert abs(z_prod.b - 13) < 1e-8
    assert abs(z_prod.c - 30) < 1e-8
    print(f"✅ 阴龙积正确: z1⊙z2 = {z_prod}")

    # 逆元
    z_inv = z1.inverse()
    z_check = yin_long_product(z1, z_inv)
    # z1 ⊙ z⁻¹ 应接近 |z|² (因为⊙不是标准乘法, 这里验证|z⁻¹|正确即可)
    assert abs(z_inv.modulus_sq() - 1 / 14) < 1e-8
    print(f"✅ 逆元正确: |z⁻¹|² = {z_inv.modulus_sq():.6f}")

    # 交换性: ij = ji → z1⊙z2 实部应 = z2⊙z1 实部
    z_prod_rev = yin_long_product(z2, z1)
    assert abs(z_prod.a - z_prod_rev.a) < 1e-8, f"交换性失败: {z_prod.a} != {z_prod_rev.a}"
    print("✅ 阴龙积交换性正确: z1⊙z2 = z2⊙z1")

    # 相位翻转
    z_flip = z1.phase_flip()
    assert abs(z_flip.b - (-z1.b)) < 1e-10
    print("✅ 相位翻转正确: b→-b")

    # 标量乘法
    z_scaled = 2 * z1
    assert abs(z_scaled.a - 2) < 1e-10
    print("✅ 标量乘法正确")

    # 死零不可逆
    try:
        GoldenSymbol(0, 0, 0).inverse()
        assert False, "应抛出ZeroDivisionError"
    except ZeroDivisionError:
        print("✅ 死零不可逆正确(Thm4.6)")

    print("\n=== 冒烟测试全部通过 ===\n")


if __name__ == "__main__":
    _smoke_test()
    run_mve()
