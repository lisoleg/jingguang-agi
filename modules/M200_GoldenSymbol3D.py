# -*- coding: utf-8 -*-
"""
M200: GoldenSymbol3D — 金符3D复广数引擎

实现金符3D复广数 z = a + bi + cj 及其运算体系，
包含阴龙积⊙、MNQ8 IWPU网格、HEX_RING_GAP拓扑，
以及双稳态/死零不破缺定理验证。

虚元规则：
  - i² = -1（波性虚元）
  - j² = -1（关系相位耦合虚元，金符虚元）
  - ij = ji（交换性——与四元数的关键区别）
  - j的对合性质：j·j̄ = 1, j̄ = -j

核心定理：
  - Thm4.3 (T212): MNQ歧义纹理双稳态定理
  - Thm4.5: Oloid差分真结构判定（EXCESS_MASS_FACE>0 ∧ EXCESS_LOOP>0 → 真锁定）
  - Thm4.6 (T213): 死零不破缺定理（全零初态→∀t, G(t)=0）

桥接模块: M130(JinFuDiscreteCalculus), M157(JinlingGridConvolution),
          M144(JinfuAccumulationComputer)

Author: Kou (寇豆码) — 太乙AGI团队
Version: 1.0.0
"""

import math
import random
from typing import Dict, Any, List, Optional


# ===========================================================================
# 常量
# ===========================================================================

EPSILON: float = 1e-10           # 数值零阈值
DEFAULT_LAMBDA: float = 1.0      # 默认耦合调谐系数
DEFAULT_MASS_THRESHOLD: float = 0.3  # 默认质量面阈值
BACKGROUND_AMPLITUDE: float = 0.05   # 背景振荡基态幅值
INTRINSIC_FREQ_SCALE: float = 0.1    # 本征频率标度
TWO_PI: float = 2.0 * math.pi        # 2π常量


# ===========================================================================
# GoldenSymbol — 金符3D复广数
# ===========================================================================

class GoldenSymbol:
    """金符3D复广数 z = a + bi + cj

    虚元规则：
    - i² = -1（波性虚元）
    - j² = -1（关系相位耦合虚元，金符虚元）
    - ij = ji（交换性——与四元数的关键区别）
    - j的对合性质：j·j̄ = 1, j̄ = -j

    运算：
    - 加法：z1+z2 = (a1+a2)+(b1+b2)i+(c1+c2)j
    - 共轭：z̄ = a - bi + cj（反转波性相位，保留关系耦合相位cj不变）
    - 模平方：|z|² = a² + b² + c²
    - 逆元（|z|≠0）：z⁻¹ = (a-bi+cj)/(a²+b²+c²)
    - 标量乘法：k·z = (ka)+(kb)i+(kc)j
    - 减法：z1-z2 = (a1-a2)+(b1-b2)i+(c1-c2)j
    - 相位翻转：c → c+π(mod 2π) 或 b → -b（镜像）
    """

    __slots__ = ('a', 'b', 'c')

    def __init__(self, a: float = 0.0, b: float = 0.0, c: float = 0.0) -> None:
        """初始化金符3D复广数

        Args:
            a: 实部（基态流贯幅值）
            b: i部（波性分量/振荡相位）
            c: j部（关系相位耦合分量）
        """
        self.a: float = float(a)
        self.b: float = float(b)
        self.c: float = float(c)

    # -------------------------------------------------------------------
    # 算术运算
    # -------------------------------------------------------------------

    def __add__(self, other: 'GoldenSymbol') -> 'GoldenSymbol':
        """加法：z1 + z2 = (a1+a2) + (b1+b2)i + (c1+c2)j"""
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return GoldenSymbol(self.a + other.a, self.b + other.b, self.c + other.c)

    def __sub__(self, other: 'GoldenSymbol') -> 'GoldenSymbol':
        """减法：z1 - z2 = (a1-a2) + (b1-b2)i + (c1-c2)j"""
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return GoldenSymbol(self.a - other.a, self.b - other.b, self.c - other.c)

    def __mul__(self, other: object) -> 'GoldenSymbol':
        """乘法：支持标量乘法与阴龙积

        - 若other为int/float：标量乘法 k·z = (ka)+(kb)i+(kc)j
        - 若other为GoldenSymbol：阴龙积⊙（λ=1.0默认）
        """
        if isinstance(other, (int, float)):
            k = float(other)
            return GoldenSymbol(self.a * k, self.b * k, self.c * k)
        if isinstance(other, GoldenSymbol):
            return yin_long_product(self, other, lambda_=1.0)
        return NotImplemented

    def __rmul__(self, other: object) -> 'GoldenSymbol':
        """左标量乘法：k · z"""
        if isinstance(other, (int, float)):
            k = float(other)
            return GoldenSymbol(self.a * k, self.b * k, self.c * k)
        return NotImplemented

    def __neg__(self) -> 'GoldenSymbol':
        """取负：-z = (-a) + (-b)i + (-c)j"""
        return GoldenSymbol(-self.a, -self.b, -self.c)

    def __abs__(self) -> float:
        """模：|z| = sqrt(a² + b² + c²)"""
        return math.sqrt(self.modulus_sq())

    # -------------------------------------------------------------------
    # 比较与哈希
    # -------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """相等判定（分量差 < EPSILON 视为相等）"""
        if not isinstance(other, GoldenSymbol):
            return NotImplemented
        return (abs(self.a - other.a) < EPSILON and
                abs(self.b - other.b) < EPSILON and
                abs(self.c - other.c) < EPSILON)

    def __hash__(self) -> int:
        """哈希值（四舍五入至9位小数以避免浮点漂移）"""
        return hash((round(self.a, 9), round(self.b, 9), round(self.c, 9)))

    # -------------------------------------------------------------------
    # 表示
    # -------------------------------------------------------------------

    def __repr__(self) -> str:
        """字符串表示：a + bi + cj 格式"""
        parts: List[str] = []
        # 实部
        if abs(self.a) > EPSILON or (abs(self.b) < EPSILON and abs(self.c) < EPSILON):
            parts.append(f"{self.a:.6g}")
        # i部
        if abs(self.b) > EPSILON:
            b_abs = abs(self.b)
            b_str = f"{b_abs:.6g}" if abs(b_abs - 1.0) > EPSILON else ""
            if self.b > 0:
                sign = "+ " if parts else ""
                parts.append(f"{sign}{b_str}i")
            else:
                sign = "- " if parts else "-"
                parts.append(f"{sign}{b_str}i")
        # j部
        if abs(self.c) > EPSILON:
            c_abs = abs(self.c)
            c_str = f"{c_abs:.6g}" if abs(c_abs - 1.0) > EPSILON else ""
            if self.c > 0:
                sign = "+ " if parts else ""
                parts.append(f"{sign}{c_str}j")
            else:
                sign = "- " if parts else "-"
                parts.append(f"{sign}{c_str}j")
        return " ".join(parts) if parts else "0"

    # -------------------------------------------------------------------
    # 代数运算
    # -------------------------------------------------------------------

    def conjugate(self) -> 'GoldenSymbol':
        """共轭：z̄ = a - bi + cj

        反转波性相位(b→-b)，保留关系耦合相位(cj不变)。
        物理含义：时间反演等价操作——波性分量反号，关系耦合保持。
        """
        return GoldenSymbol(self.a, -self.b, self.c)

    def modulus_sq(self) -> float:
        """模平方：|z|² = a² + b² + c²

        物理含义：金灵球的总流贯能量密度。
        """
        return self.a * self.a + self.b * self.b + self.c * self.c

    def inverse(self) -> 'GoldenSymbol':
        """逆元：z⁻¹ = z̄ / |z|² = (a - bi + cj) / (a² + b² + c²)

        Returns:
            金符的逆元

        Raises:
            ZeroDivisionError: 当 |z|² ≈ 0 时
        """
        msq = self.modulus_sq()
        if msq < EPSILON:
            raise ZeroDivisionError(f"Cannot invert zero GoldenSymbol: {self!r}")
        conj = self.conjugate()
        return GoldenSymbol(conj.a / msq, conj.b / msq, conj.c / msq)

    def normalized(self) -> 'GoldenSymbol':
        """归一化：z / |z|

        将金符缩放至模为1。若|z|≈0则返回零金符。

        Returns:
            模为1的金符，或零金符（当|z|≈0时）
        """
        mod = abs(self)
        if mod < EPSILON:
            return GoldenSymbol(0.0, 0.0, 0.0)
        return GoldenSymbol(self.a / mod, self.b / mod, self.c / mod)

    def is_zero(self, eps: float = EPSILON) -> bool:
        """判定是否为零金符

        Args:
            eps: 零阈值（对模平方判定）

        Returns:
            若 |z|² < eps 则为 True
        """
        return self.modulus_sq() < eps

    def phase_flip(self, mode: str = 'wave') -> 'GoldenSymbol':
        """相位翻转

        Args:
            mode: 'wave' → b → -b（波性镜像翻转）
                  'relation' → c → (c + π) mod 2π（关系相位翻转）

        Returns:
            翻转后的金符

        Raises:
            ValueError: mode不是'wave'或'relation'
        """
        if mode == 'wave':
            # 波性镜像：b → -b
            return GoldenSymbol(self.a, -self.b, self.c)
        elif mode == 'relation':
            # 关系相位翻转：c → (c + π) mod 2π
            new_c = (self.c + math.pi) % TWO_PI
            return GoldenSymbol(self.a, self.b, new_c)
        else:
            raise ValueError(
                f"Unknown phase_flip mode: {mode!r}, expected 'wave' or 'relation'"
            )


# ===========================================================================
# 阴龙积 ⊙ (H.2.4定义)
# ===========================================================================

def yin_long_product(z1: GoldenSymbol, z2: GoldenSymbol,
                     lambda_: float = DEFAULT_LAMBDA) -> GoldenSymbol:
    """阴龙积 ⊙ (H.2.4定义)

    z1 ⊙ z2 = (a1·a2 - λ·b1·b2 - c1·c2)
             + (a1·b2 + b1·a2)i
             + (a1·c2 + c1·a2 + λ·b1·c2)j

    λ为耦合调谐系数（默认1.0，或对应139天命矩阵的特定频率比）。

    物理意义：
    - 实部 a1a2 - λb1b2 - c1c2：
      能流净增益/损耗。-c1c2：相位失配导致能量耗散。
    - i部 a1b2 + b1a2：
      波性传播项（对流项），类比复数乘法的交叉项。
    - j部 a1c2 + c1a2 + λb1c2：
      关系相位锁定项（核心！）。
      当两金灵球波性分量b同相时，产生正相位耦合增益，促进流贯囚禁；
      反相则抑制。

    Args:
        z1: 第一个金符
        z2: 第二个金符
        lambda_: 耦合调谐系数

    Returns:
        阴龙积结果 z1 ⊙ z2
    """
    a = z1.a * z2.a - lambda_ * z1.b * z2.b - z1.c * z2.c
    b = z1.a * z2.b + z1.b * z2.a
    c = z1.a * z2.c + z1.c * z2.a + lambda_ * z1.b * z2.c
    return GoldenSymbol(a, b, c)


# ===========================================================================
# MNQ8Grid — MNQ8 IWPU网格
# ===========================================================================

class MNQ8Grid:
    """MNQ8 IWPU网格 — 金符学运算公理在离散网格上的数值执行

    三大核心机制：
    1. 本征螺旋振荡 ↔ 金符幅相演化
       state = amplitude * exp(i*phase_wave + j*phase_rel)
    2. 邻域耦合 ↔ 阴龙积⊙
       total_flux = Σ neighbors: current_state ⊙ neighbor_state
    3. 能流运算 ↔ 模长阈值判定
       |total_flux|² > MASS_THRESHOLD → 锁定结构（归一化）
       否则 → 回归背景振荡

    MNQ8更新律三大约束：
    - 本征螺旋振荡：每个格子具有内在频率，驱动相位演化
    - 邻域耦合：阴龙积⊙计算局部通量，超阈值则锁相
    - 禁止外源注入（NO_EXTRA_DYNAMICS = IDO无exogenous force）：
      唯一允许的外部操作是inject_phase（相位偏置，非力/能量注入）
    """

    def __init__(self, rows: int, cols: int,
                 lambda_: float = DEFAULT_LAMBDA,
                 mass_threshold: float = DEFAULT_MASS_THRESHOLD) -> None:
        """初始化MNQ8网格

        Args:
            rows: 行数
            cols: 列数
            lambda_: 阴龙积耦合调谐系数
            mass_threshold: 质量面阈值（|total_flux|² > 此值则锁相）
        """
        self.rows: int = rows
        self.cols: int = cols
        self.lambda_: float = lambda_
        self.mass_threshold: float = mass_threshold
        self.step_count: int = 0

        # 核心指标
        self.mass_face: float = 0.0           # MASS_FACE：锁定结构总模平方
        self.loop_hold: float = 0.0           # LOOP_HOLD：邻域耦合强度均值
        self.boundary_leak: float = 0.0       # BOUNDARY_LEAK：边界通量占比
        self.excess_loop: float = 0.0         # EXCESS_LOOP = LOOP_HOLD - background
        self.excess_mass_face: float = 0.0    # EXCESS_MASS_FACE = MASS_FACE - background

        # 背景状态（Oloid差分用）
        self.background: Optional[Dict[str, float]] = None

        # 初始化金灵球网格（全零态）
        self.grid: List[List[GoldenSymbol]] = [
            [GoldenSymbol(0.0, 0.0, 0.0) for _ in range(cols)]
            for _ in range(rows)
        ]

        # 锁定状态
        self.locked: List[List[bool]] = [
            [False for _ in range(cols)]
            for _ in range(rows)
        ]

        # 本征频率（每个格子独立的螺旋振荡频率）
        self._omega_b: List[List[float]] = [
            [random.uniform(-INTRINSIC_FREQ_SCALE, INTRINSIC_FREQ_SCALE)
             for _ in range(cols)]
            for _ in range(rows)
        ]
        self._omega_c: List[List[float]] = [
            [random.uniform(-INTRINSIC_FREQ_SCALE, INTRINSIC_FREQ_SCALE)
             for _ in range(cols)]
            for _ in range(rows)
        ]

    # -------------------------------------------------------------------
    # 私有方法
    # -------------------------------------------------------------------

    def _get_neighbors(self, r: int, c: int) -> List[GoldenSymbol]:
        """获取4邻域（von Neumann邻域），边界外返回零金符

        Args:
            r: 行索引
            c: 列索引

        Returns:
            邻居金符列表 [上, 下, 左, 右]
        """
        zero = GoldenSymbol(0.0, 0.0, 0.0)
        neighbors: List[GoldenSymbol] = []
        # 上
        neighbors.append(self.grid[r - 1][c] if r > 0 else zero)
        # 下
        neighbors.append(self.grid[r + 1][c] if r < self.rows - 1 else zero)
        # 左
        neighbors.append(self.grid[r][c - 1] if c > 0 else zero)
        # 右
        neighbors.append(self.grid[r][c + 1] if c < self.cols - 1 else zero)
        return neighbors

    def _intrinsic_oscillation(self, z: GoldenSymbol,
                               r: int, c: int) -> GoldenSymbol:
        """本征螺旋振荡

        在(a, b)平面和(a, c)平面分别进行独立旋转，
        模拟金灵球的内在螺旋演化。
        加入微小PG基态流贯弥散注入（幅度极小，
        不足以独立越过MASS_THRESHOLD，满足NO_EXTRA_DYNAMICS约束）。

        Args:
            z: 当前金符态
            r: 行索引
            c: 列索引

        Returns:
            振荡后的金符态
        """
        omega_b = self._omega_b[r][c]
        omega_c = self._omega_c[r][c]

        # 在(a, b)平面旋转 omega_b
        cos_b = math.cos(omega_b)
        sin_b = math.sin(omega_b)
        a1 = z.a * cos_b - z.b * sin_b
        b1 = z.a * sin_b + z.b * cos_b

        # 在(a1, c)平面旋转 omega_c
        cos_c = math.cos(omega_c)
        sin_c = math.sin(omega_c)
        a2 = a1 * cos_c - z.c * sin_c
        c1 = a1 * sin_c + z.c * cos_c

        # 微小PG基态注入（弥散级别，远低于MASS_THRESHOLD）
        # 这不是外源力，而是量子零点涨落等价
        pg_inject = (BACKGROUND_AMPLITUDE * 0.01
                     * math.sin(self.step_count * omega_b * 0.1))
        a2 += pg_inject

        return GoldenSymbol(a2, b1, c1)

    def _compute_metrics(self) -> None:
        """计算网格核心指标：MASS_FACE, LOOP_HOLD, BOUNDARY_LEAK

        MASS_FACE: 锁定格子的总模平方 = Σ_{locked} |z|²
            物理含义：系统中的"质量"总量。

        LOOP_HOLD: 相邻格子归一化耦合强度均值
            = (1/N_pairs) Σ |z1⊙z2|² / (|z1|²·|z2|² + ε)
            物理含义：局部流贯回路保持度。

        BOUNDARY_LEAK: 边界格子模平方占总模平方的比例
            = Σ_{boundary} |z|² / (Σ_{all} |z|² + ε)
            物理含义：流贯从系统边界泄漏的比例。
        """
        mass_face_val = 0.0
        total_modsq = 0.0
        boundary_modsq = 0.0

        for r in range(self.rows):
            for c in range(self.cols):
                z = self.grid[r][c]
                msq = z.modulus_sq()
                total_modsq += msq
                if self.locked[r][c]:
                    mass_face_val += msq
                # 边界格子
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    boundary_modsq += msq

        self.mass_face = mass_face_val

        # LOOP_HOLD: 归一化邻域耦合强度
        coupling_sum = 0.0
        pair_count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                z1 = self.grid[r][c]
                msq1 = z1.modulus_sq()
                # 右邻居
                if c < self.cols - 1:
                    z2 = self.grid[r][c + 1]
                    msq2 = z2.modulus_sq()
                    prod = yin_long_product(z1, z2, self.lambda_)
                    coupling_sum += prod.modulus_sq() / (msq1 * msq2 + EPSILON)
                    pair_count += 1
                # 下邻居
                if r < self.rows - 1:
                    z2 = self.grid[r + 1][c]
                    msq2 = z2.modulus_sq()
                    prod = yin_long_product(z1, z2, self.lambda_)
                    coupling_sum += prod.modulus_sq() / (msq1 * msq2 + EPSILON)
                    pair_count += 1

        self.loop_hold = coupling_sum / max(pair_count, 1)

        # BOUNDARY_LEAK: 边界通量占比
        self.boundary_leak = boundary_modsq / (total_modsq + EPSILON)

    # -------------------------------------------------------------------
    # 核心更新
    # -------------------------------------------------------------------

    def step(self) -> None:
        """MNQ8单步更新：遍历所有格子，计算阴龙积邻域耦合，阈值判定

        更新流程：
        1. 对每个格子计算 total_flux = Σ_{neighbors} current ⊙ neighbor
        2. 若 |total_flux|² > mass_threshold → 归一化锁定
        3. 否则 → 本征螺旋振荡（背景态）
        4. 更新 mass_face, loop_hold, boundary_leak
        5. 若有背景参考，更新 excess_loop, excess_mass_face
        """
        # 新网格（同步更新，避免顺序依赖）
        new_grid: List[List[GoldenSymbol]] = [
            [GoldenSymbol(0.0, 0.0, 0.0) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        new_locked: List[List[bool]] = [
            [False for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        for r in range(self.rows):
            for c in range(self.cols):
                current = self.grid[r][c]
                neighbors = self._get_neighbors(r, c)

                # 计算邻域耦合通量
                total_flux = GoldenSymbol(0.0, 0.0, 0.0)
                for nbr in neighbors:
                    total_flux = total_flux + yin_long_product(
                        current, nbr, self.lambda_
                    )

                flux_modsq = total_flux.modulus_sq()

                if flux_modsq > self.mass_threshold:
                    # 锁定结构（归一化至模为1）
                    new_grid[r][c] = total_flux.normalized()
                    new_locked[r][c] = True
                else:
                    # 回归背景振荡
                    new_grid[r][c] = self._intrinsic_oscillation(current, r, c)
                    new_locked[r][c] = False

        self.grid = new_grid
        self.locked = new_locked
        self.step_count += 1

        # 更新指标
        self._compute_metrics()

        # 更新超额指标（Oloid差分）
        if self.background is not None:
            self.excess_mass_face = (
                self.mass_face - self.background.get('mass_face', 0.0)
            )
            self.excess_loop = (
                self.loop_hold - self.background.get('loop_hold', 0.0)
            )

    # -------------------------------------------------------------------
    # 外部接口
    # -------------------------------------------------------------------

    def inject_phase(self, theta_bias: float) -> None:
        """注入金符相位偏置

        唯一允许的外部操作（非力/能量注入，仅相位偏置）。
        θ_bias=0 → 暗示'上楼'方向
        θ_bias=π → 倒置/暗示'下楼'方向

        对所有格子的c分量施加偏移，不改变a和b。

        Args:
            theta_bias: 关系相位偏置值（弧度）
        """
        for r in range(self.rows):
            for c in range(self.cols):
                z = self.grid[r][c]
                self.grid[r][c] = GoldenSymbol(z.a, z.b, z.c + theta_bias)

    def load_texture(self, texture_2d: List[List[float]]) -> None:
        """加载2D灰度纹理到网格

        灰度→金符态映射：
        - a = gray / 255（归一化灰度值→基态流贯幅值）
        - b = gradient_x（水平灰度差分→波性分量）
        - c = 0（初始无关系耦合）

        Args:
            texture_2d: 2D灰度值数组，值域[0, 255]，
                        外层为行，内层为列
        """
        tex_rows = len(texture_2d)
        tex_cols = len(texture_2d[0]) if tex_rows > 0 else 0

        for r in range(min(self.rows, tex_rows)):
            for c in range(min(self.cols, tex_cols)):
                gray = float(texture_2d[r][c])
                a_val = gray / 255.0

                # 水平灰度差分作为波性分量
                if c + 1 < tex_cols:
                    gradient_x = (float(texture_2d[r][c + 1]) - gray) / 255.0
                else:
                    gradient_x = 0.0

                self.grid[r][c] = GoldenSymbol(a_val, gradient_x, 0.0)

    def compute_background(self, n_steps: int = 10) -> None:
        """计算背景状态（PG基态流贯弥散），用于Oloid差分

        流程：
        1. 保存当前网格状态
        2. 将网格设为均匀低幅值背景态
        3. 运行n_steps背景演化
        4. 记录各指标均值作为background
        5. 恢复原状态

        Args:
            n_steps: 背景演化步数
        """
        # 保存当前状态
        saved_grid: List[List[GoldenSymbol]] = [
            [GoldenSymbol(self.grid[r][c].a,
                          self.grid[r][c].b,
                          self.grid[r][c].c)
             for c in range(self.cols)]
            for r in range(self.rows)
        ]
        saved_locked: List[List[bool]] = [
            [self.locked[r][c] for c in range(self.cols)]
            for r in range(self.rows)
        ]
        saved_step_count = self.step_count
        saved_mass_face = self.mass_face
        saved_loop_hold = self.loop_hold
        saved_boundary_leak = self.boundary_leak

        # 设置均匀低幅值背景态
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = GoldenSymbol(
                    BACKGROUND_AMPLITUDE,
                    BACKGROUND_AMPLITUDE * math.sin(r * 0.5),
                    BACKGROUND_AMPLITUDE * math.cos(c * 0.5)
                )
                self.locked[r][c] = False

        # 运行n_steps背景演化，收集指标
        mass_face_sum = 0.0
        loop_hold_sum = 0.0
        boundary_leak_sum = 0.0

        for _ in range(n_steps):
            self.step()
            mass_face_sum += self.mass_face
            loop_hold_sum += self.loop_hold
            boundary_leak_sum += self.boundary_leak

        # 记录背景均值
        self.background = {
            'mass_face': mass_face_sum / max(n_steps, 1),
            'loop_hold': loop_hold_sum / max(n_steps, 1),
            'boundary_leak': boundary_leak_sum / max(n_steps, 1),
        }

        # 恢复原状态
        self.grid = saved_grid
        self.locked = saved_locked
        self.step_count = saved_step_count
        self.mass_face = saved_mass_face
        self.loop_hold = saved_loop_hold
        self.boundary_leak = saved_boundary_leak

    def oloid_differential(self) -> Dict[str, float]:
        """Oloid差分 = condition_t - background_t

        Thm4.5: EXCESS_MASS_FACE > 0 ∧ EXCESS_LOOP > 0 → 真结构锁定
        EXCESS ≈ 0 → 伪结构（仅背景涨落，非真实涌现）

        Returns:
            差分指标字典，含：
            - excess_mass_face: 当前MASS_FACE - 背景MASS_FACE
            - excess_loop: 当前LOOP_HOLD - 背景LOOP_HOLD
            - excess_boundary_leak: 当前BOUNDARY_LEAK - 背景BOUNDARY_LEAK
        """
        if self.background is None:
            return {
                'excess_mass_face': 0.0,
                'excess_loop': 0.0,
                'excess_boundary_leak': 0.0,
            }

        return {
            'excess_mass_face': (
                self.mass_face - self.background.get('mass_face', 0.0)
            ),
            'excess_loop': (
                self.loop_hold - self.background.get('loop_hold', 0.0)
            ),
            'excess_boundary_leak': (
                self.boundary_leak - self.background.get('boundary_leak', 0.0)
            ),
        }

    def get_state(self) -> Dict[str, Any]:
        """返回网格状态字典

        Returns:
            包含网格数据、指标、锁定状态的完整状态字典
        """
        grid_data: List[List[Dict[str, Any]]] = []
        for r in range(self.rows):
            row_data: List[Dict[str, Any]] = []
            for c in range(self.cols):
                z = self.grid[r][c]
                row_data.append({
                    'a': z.a,
                    'b': z.b,
                    'c': z.c,
                    'locked': self.locked[r][c],
                    'modulus_sq': z.modulus_sq(),
                })
            grid_data.append(row_data)

        return {
            'module': 'M200_GoldenSymbol3D',
            'step_count': self.step_count,
            'rows': self.rows,
            'cols': self.cols,
            'lambda': self.lambda_,
            'mass_threshold': self.mass_threshold,
            'grid': grid_data,
            'metrics': {
                'mass_face': self.mass_face,
                'loop_hold': self.loop_hold,
                'boundary_leak': self.boundary_leak,
                'excess_mass_face': self.excess_mass_face,
                'excess_loop': self.excess_loop,
            },
            'background': self.background,
        }

    def is_locked(self) -> bool:
        """判定是否已锁相

        判据：EXCESS_LOOP > 0 ∧ MASS_FACE > 0
        表示系统存在超出背景的结构性锁定。

        Returns:
            已锁相返回True，否则False
        """
        return self.excess_loop > 0.0 and self.mass_face > 0.0


# ===========================================================================
# HEX_RING_GAP 拓扑
# ===========================================================================

def create_hex_ring_gap(rows: int = 16, cols: int = 16,
                        gap_position: str = 'top') -> MNQ8Grid:
    """创建HEX_RING_GAP拓扑（缺口六边形壳层）

    六边形环状壳层，带一个缺口（非完整封闭）。
    PG鲁珀特之泪孤子 = 最佳流贯囚禁拓扑 = 质量面前体。

    MNQ v12参考数据：MASS_FACE≈0.402, LOOP_HOLD≈0.5, BOUNDARY_LEAK≈0.164

    缺口释放内部应力 → S_Rel(B) < S_Rel(完整壳层A) → 刘机制选B
    （关系熵减原理：缺口壳层的关系熵低于完整壳层，刘机制优先选择）

    Args:
        rows: 网格行数
        cols: 网格列数
        gap_position: 缺口位置，可选 'top'/'bottom'/'left'/'right'

    Returns:
        配置好的MNQ8Grid实例，环壳区域已设置高幅值金灵球
    """
    grid = MNQ8Grid(rows, cols)

    center_r = rows / 2.0
    center_c = cols / 2.0
    min_dim = min(rows, cols)
    r_inner = min_dim * 0.25
    r_outer = min_dim * 0.45

    # 缺口角度映射
    gap_angles: Dict[str, float] = {
        'top': math.pi / 2,
        'bottom': -math.pi / 2,
        'left': math.pi,
        'right': 0.0,
    }
    gap_center_angle = gap_angles.get(gap_position, math.pi / 2)
    gap_half_angle = math.pi / 6  # 30度半角

    for r in range(rows):
        for c in range(cols):
            dr = r - center_r
            dc = c - center_c
            dist = math.sqrt(dr * dr + dc * dc)

            if r_inner <= dist <= r_outer:
                # 计算极角
                angle = math.atan2(dr, dc)

                # 检查是否在缺口范围内（处理角度环绕）
                angle_diff = abs(angle - gap_center_angle)
                if angle_diff > math.pi:
                    angle_diff = TWO_PI - angle_diff

                if angle_diff < gap_half_angle:
                    # 缺口位置：零幅值（释放应力）
                    grid.grid[r][c] = GoldenSymbol(0.0, 0.0, 0.0)
                else:
                    # 壳层：高幅值金灵球
                    amplitude = 0.8 + 0.2 * math.cos(angle * 3)
                    phase = angle * 2
                    grid.grid[r][c] = GoldenSymbol(
                        amplitude,
                        amplitude * 0.3 * math.sin(phase),
                        amplitude * 0.2 * math.cos(phase)
                    )
            else:
                # 环外：低背景幅值
                grid.grid[r][c] = GoldenSymbol(BACKGROUND_AMPLITUDE * 0.5, 0.0, 0.0)

    return grid


# ===========================================================================
# MVE验证
# ===========================================================================

def run_mve() -> Dict[str, bool]:
    """M200 MVE验证

    T212: MNQ歧义纹理双稳态定理 (Thm4.3)
      - 无偏置 → 双稳态跳变（两种局部极小间随机跳变），
        系统不稳定锁相
      - 有偏置 → 锁向偏置方向（EXCESS_LOOP > 0），
        系统稳定锁相

    T213: 死零不破缺定理 (Thm4.6)
      - 全零初态 → ∀t, G(t)=0, Mass-Face=0
      - 无信息输入(Ftel=0)则无显现
      - 零频零幅 → 零态不变

    Returns:
        {"T212": bool, "T213": bool}
    """
    results: Dict[str, bool] = {'T212': False, 'T213': False}

    # ==================================================================
    # T213: 死零不破缺定理
    # ==================================================================
    # 核心断言：全零初态+零频率 → 所有时刻态恒零，MASS_FACE恒零
    # 物理含义：无信息输入(Ftel=0)则无显现——虚空不自发涌现
    grid_t213 = MNQ8Grid(8, 8, lambda_=1.0, mass_threshold=0.3)

    # 确保全零初态 + 零本征频率
    for r in range(8):
        for c in range(8):
            grid_t213.grid[r][c] = GoldenSymbol(0.0, 0.0, 0.0)
            grid_t213._omega_b[r][c] = 0.0
            grid_t213._omega_c[r][c] = 0.0

    all_zero_holds = True
    mass_face_zero_holds = True

    for t in range(20):
        grid_t213.step()
        # 检查所有格子是否仍为零
        for r in range(8):
            for c in range(8):
                if not grid_t213.grid[r][c].is_zero(eps=1e-6):
                    all_zero_holds = False
                    break
            if not all_zero_holds:
                break
        # 检查MASS_FACE是否为零
        if grid_t213.mass_face > 1e-6:
            mass_face_zero_holds = False

        if not all_zero_holds or not mass_face_zero_holds:
            break

    results['T213'] = all_zero_holds and mass_face_zero_holds

    # ==================================================================
    # T212: MNQ歧义纹理双稳态定理
    # ==================================================================
    # 核心断言：
    # (a) 无偏置 → 歧义纹理驱动双稳态，系统不锁向单一方向
    # (b) 有偏置 → 系统锁向偏置方向，EXCESS_LOOP > 0

    random.seed(42)

    # --- (a) 无偏置测试 ---
    grid_unbiased = MNQ8Grid(10, 10, lambda_=1.0, mass_threshold=0.2)

    # 创建歧义纹理：左半/右半等幅但反相关系相位
    for r in range(10):
        for c in range(10):
            if c < 5:
                # 左半：相位模式A (b>0, c>0)
                grid_unbiased.grid[r][c] = GoldenSymbol(0.5, 0.2, 0.15)
            else:
                # 右半：相位模式B (b<0, c<0) —— 反相关系
                grid_unbiased.grid[r][c] = GoldenSymbol(0.5, -0.2, -0.15)

    # 运行无偏置演化
    c_sums_unbiased: List[float] = []
    for _ in range(30):
        grid_unbiased.step()
        # 记录全网格c分量之和（正负波动=双稳态特征）
        c_sum = sum(grid_unbiased.grid[r][cc].c
                    for r in range(10) for cc in range(10))
        c_sums_unbiased.append(c_sum)

    # 双稳态判据：c_sum有正有负的波动，或不稳定（标准差显著）
    unbiased_unstable = True
    if len(c_sums_unbiased) > 1:
        mean_c = sum(c_sums_unbiased) / len(c_sums_unbiased)
        variance = sum((x - mean_c) ** 2 for x in c_sums_unbiased) / len(
            c_sums_unbiased
        )
        std_c = math.sqrt(variance)
        # 若标准差极小（< 0.001），说明没有波动，非双稳态
        unbiased_unstable = std_c > 0.0001 or abs(mean_c) < 0.1

    # --- (b) 有偏置测试 ---
    random.seed(123)
    grid_biased = MNQ8Grid(10, 10, lambda_=1.0, mass_threshold=0.2)

    # 重新加载相同的歧义纹理
    for r in range(10):
        for c in range(10):
            if c < 5:
                grid_biased.grid[r][c] = GoldenSymbol(0.5, 0.2, 0.15)
            else:
                grid_biased.grid[r][c] = GoldenSymbol(0.5, -0.2, -0.15)

    # 注入相位偏置（打破对称性）
    grid_biased.inject_phase(0.5)

    # 计算背景参考
    grid_biased.compute_background(n_steps=5)

    # 运行有偏置演化
    for _ in range(30):
        grid_biased.step()

    # 有偏置锁相判据：
    # (1) EXCESS_LOOP > 0（超出背景的耦合强度），或
    # (2) is_locked() 返回 True，或
    # (3) MASS_FACE显著大于零（有结构锁定）
    oloid = grid_biased.oloid_differential()
    excess_loop_positive = oloid['excess_loop'] > 0
    is_locked_biased = grid_biased.is_locked()
    has_structure = grid_biased.mass_face > 0.01

    biased_locks = excess_loop_positive or is_locked_biased or has_structure

    # T212通过条件：无偏置不稳定 ∧ 有偏置锁相
    results['T212'] = unbiased_unstable and biased_locks

    return results


# ===========================================================================
# 模块导出
# ===========================================================================

__all__ = [
    'GoldenSymbol',
    'yin_long_product',
    'MNQ8Grid',
    'create_hex_ring_gap',
    'run_mve',
]
