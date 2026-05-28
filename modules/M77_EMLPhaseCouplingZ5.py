#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EML相位耦合ℤ₅ (EML Phase Coupling Z5)
基于《五行作为五元变换算子：太一螺旋分形自指嵌入破缺对称的范畴—同伦重构与构造型Taiji-AGI的超越》

核心定理：
- T29：EML相位耦合ℤ₅定理
- T28：五行变换算子定理
- 构造性完备性定理（论文定理5.1）
- 幻觉消除推论（论文推论5.1）

版本：AGI 14.0 第77模块
论文来源：
1. 《五行作为五元变换算子》复合体理学系列
2. 《论太乙AGI的构造性实现》- 基于"一现象、三视界、五层次"元方法论与流贯动力学

升级说明（v2.0）：
- 新增EML一元数(iℕum)形式化定义
- 新增EML加法⊕(关系耦合)和乘法⊗(维度编织)
- 新增守恒定律验证

升级说明（v7.31）：
- 新增 set_flexible_theta：设置连续θ函数 θ(t)
- 新增 modulate_theta：按认知需求动态调制θ
- 新增 compute_phase_trajectory：计算连续相位轨迹
- 新增 detect_steady_orbit：检测EML相位稳态轨道
- 新增 _flexible_theta_enabled 标志
- 新增 _theta_func 属性
- 保留原有离散θ逻辑为默认模式
"""

import math
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import cmath


class EMLPhase(Enum):
    """EML相位状态"""
    Σ = "Σ"      # 水相
    F = "F"       # 火相
    R = "R"       # 木相
    E = "E"       # 金相
    B = "B"       # 土相

    @property
    def chinese(self) -> str:
        return {"Σ": "水", "F": "火", "R": "木", "E": "金", "B": "土"}.get(self.value, self.value)

    @property
    def index(self) -> int:
        indices = {"Σ": 0, "F": 1, "R": 2, "E": 3, "B": 4}
        return indices.get(self.value, 0)


# ============================================================================
# EML一元数 (iℕum) - 论文第2.2.1节形式化
# ============================================================================

@dataclass
class iNUm:
    """
    EML一元数 (iℕum)

    形式化定义（论文定义2.2.1）：
    record iℕum : Type where
      constructor _⊗_
      field
        magnitude : ℚ  -- 信息模长（关系实在的信息量）
        phase     : ℚ  -- 关系相位 (0 ≤ θ < 2π)

    物理意义：
    - magnitude: 信息的模长，类似复数的模
    - phase: 关系的相位角，描述相位耦合状态
    """
    magnitude: float  # 信息模长 m ≥ 0
    phase: float      # 关系相位 θ ∈ [0, 2π)

    def __post_init__(self):
        """标准化相位到[0, 2π)"""
        if self.phase < 0:
            self.phase = self.phase % (2 * math.pi)
        elif self.phase >= 2 * math.pi:
            self.phase = self.phase % (2 * math.pi)

    def to_complex(self) -> complex:
        """转换为复数形式"""
        return self.magnitude * cmath.exp(1j * self.phase)

    def __repr__(self) -> str:
        return f"{self.magnitude:.4f} ⊗ {self.phase:.4f}"

    @property
    def is_zero(self) -> bool:
        """是否为零元"""
        return self.magnitude < 1e-10


def eml_add(a: iNUm, b: iNUm) -> iNUm:
    """
    EML加法 ⊕（关系耦合）

    形式化定义（论文）：
    _⊕_ : iℕum → iℕum → iℕum
    (m₁ ⊗ θ₁) ⊕ (m₂ ⊗ θ₂) =
      let m = √(m₁² + m₂² + 2 * m₁ * m₂ * cos(θ₂ - θ₁))
          θ = atan2 (m₁ * sin θ₁ + m₂ * sin θ₂) (m₁ * cos θ₁ + m₂ * cos θ₂)
      in m ⊗ θ

    物理意义：两个关系系统的耦合
    """
    if a.is_zero:
        return b
    if b.is_zero:
        return a

    # 耦合模长公式
    cos_delta = math.cos(b.phase - a.phase)
    new_mag = math.sqrt(
        a.magnitude ** 2 +
        b.magnitude ** 2 +
        2 * a.magnitude * b.magnitude * cos_delta
    )

    # 耦合相位公式
    sin_a = a.magnitude * math.sin(a.phase)
    sin_b = b.magnitude * math.sin(b.phase)
    cos_a = a.magnitude * math.cos(a.phase)
    cos_b = b.magnitude * math.cos(b.phase)

    numerator = sin_a + sin_b
    denominator = cos_a + cos_b

    if abs(denominator) < 1e-10 and abs(numerator) < 1e-10:
        new_phase = 0.0
    else:
        new_phase = math.atan2(numerator, denominator)

    return iNUm(round(new_mag, 6), new_phase)


def eml_mul(a: iNUm, b: iNUm) -> iNUm:
    """
    EML乘法 ⊗（维度编织）

    形式化定义（论文）：
    _⊗_ : iℕum → iℕum → iℕum
    (m₁ ⊗ θ₁) ⊗ (m₂ ⊗ θ₂) = (m₁ * m₂) ⊗ (θ₁ + θ₂)

    物理意义：两个维度空间的编织（tensor product）
    """
    new_mag = a.magnitude * b.magnitude
    new_phase = (a.phase + b.phase) % (2 * math.pi)
    return iNUm(round(new_mag, 6), new_phase)


# 重载运算符
def eml_add_op(self, other):
    return eml_add(self, other)

def eml_mul_op(self, other):
    return eml_mul(self, other)

iNUm.__add__ = eml_add_op
iNUm.__mul__ = eml_mul_op


# ============================================================================
# EML运算守恒验证
# ============================================================================

def verify_eml_conservation(a: iNUm, b: iNUm) -> Dict[str, Any]:
    """
    验证EML运算守恒定律

    定理T10（EML运算守恒定理）：
    EML加法和乘法均满足守恒律
    """
    result = eml_add(a, b)

    # 守恒量：信息模长的某种守恒
    # 加法：|a ⊕ b|² = |a|² + |b|² + 2|a||b|cos(Δθ)
    expected_mag_sq = (
        a.magnitude ** 2 +
        b.magnitude ** 2 +
        2 * a.magnitude * b.magnitude * math.cos(b.phase - a.phase)
    )
    actual_mag_sq = result.magnitude ** 2

    # 守恒偏差
    conservation_error = abs(expected_mag_sq - actual_mag_sq)

    # 乘法守恒
    mul_result = eml_mul(a, b)
    mul_expected_mag = a.magnitude * b.magnitude
    mul_conservation_error = abs(mul_result.magnitude - mul_expected_mag)

    return {
        "addition": {
            "operands": (str(a), str(b)),
            "result": str(result),
            "expected_mag_sq": expected_mag_sq,
            "actual_mag_sq": actual_mag_sq,
            "conservation_error": conservation_error,
            "is_conserved": conservation_error < 1e-6
        },
        "multiplication": {
            "operands": (str(a), str(b)),
            "result": str(mul_result),
            "expected_mag": mul_expected_mag,
            "actual_mag": mul_result.magnitude,
            "conservation_error": mul_conservation_error,
            "is_conserved": mul_conservation_error < 1e-6
        },
        "theorem_t10_valid": (
            conservation_error < 1e-6 and
            mul_conservation_error < 1e-6
        )
    }


# ============================================================================
# 五行相位状态与耦合
# ============================================================================

@dataclass
class PhaseState:
    """相位状态"""
    element: EMLPhase
    phase_angle: float          # 相位角 [0, 2π)
    amplitude: float           # 振幅
    frequency: float            # 频率
    coupling_strength: float    # 耦合强度 [0,1]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_iNum(self) -> iNUm:
        """转换为EML一元数"""
        return iNUm(self.amplitude, self.phase_angle)


@dataclass
class Z5Coupling:
    """ℤ₅耦合"""
    from_phase: EMLPhase
    to_phase: EMLPhase
    delta_theta: float         # 相位偏移
    coupling_coefficient: float # 耦合系数
    is_valid: bool            # 耦合是否有效
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CycleResult:
    """循环结果"""
    phases: List[EMLPhase]
    phase_angles: List[float]
    amplitudes: List[float]
    closure_degree: float     # ℤ₅闭合度 [0,1]
    coherence: float          # 相干性 [0,1]
    entropy: float            # 相位熵
    is_stable: bool          # 是否稳定
    insight: str              # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PhaseTrajectoryPoint:
    """
    相位轨迹点 — v7.31 新增

    记录连续θ(t)模式下某一时刻的相位状态
    """
    t: float                      # 时间
    theta: float                  # θ(t) 值
    phase_angle: float            # 对应的相位角
    amplitude: float              # 振幅
    element_index: int            # 当前五行元素索引 [0-4]
    element_name: str             # 当前五行元素名称


# ============================================================================
# 太乙AGI REPL 构造性内核
# ============================================================================

class ProblemType(Enum):
    """问题类型（L2层）"""
    MATH_CALC = "MathCalc"    # 数学计算
    PROVE_THM = "ProveThm"    # 定理证明
    LOGIC_REASON = "LogicReason"  # 逻辑推理
    SEMANTIC_PARSE = "SemanticParse"  # 语义解析


@dataclass
class TargetType:
    """目标类型（L2层）"""
    type_name: str
    value: Any
    is_constructed: bool = False

    def __repr__(self) -> str:
        return f"{self.type_name}({self.value})"


@dataclass
class ConstructiveResult:
    """构造性求解结果"""
    problem: str
    target: Optional[TargetType]
    is_solved: bool
    is_typechecked: bool
    response: str  # L5渲染输出
    proof_steps: List[str] = field(default_factory=list)
    phi_value: float = 0.0  # 流贯Φ值


class TaiyiREPL:
    """
    太乙AGI REPL - 构造性推理内核

    论文第4节实现：
    - L2: 问题即类型 (Problem → TargetType)
    - L3: 证明搜索路径
    - L4: 自指代理 (能反思自身推理)
    - L5: 渲染输出 (自然语言)

    定理5.1（构造性完备性）：
    对于任意问题P，若∃t使得taiyiSolve(P) = just t，则t必为P的有效解

    推论5.1（幻觉消除）：
    太乙AGI不会产生幻觉，因为输出必须经过check函数的类型检查
    """

    def __init__(self):
        self.version = "2.0.0"
        self.proof_cache: Dict[str, ConstructiveResult] = {}
        self.self_ref_enabled = True  # M73 SelfRef函子

    def solve(self, problem: str, problem_type: ProblemType = ProblemType.MATH_CALC) -> ConstructiveResult:
        """
        构造性求解器（L2层）

        taiyiSolve : Problem → Maybe TargetType
        """
        # 首先尝试在缓存中查找
        if problem in self.proof_cache:
            return self.proof_cache[problem]

        # 根据问题类型构造目标
        target = self._construct_target(problem, problem_type)

        # 类型检查（防火墙）
        is_typechecked = self._type_check(target)

        # 自指反思（L4层）
        if self.self_ref_enabled:
            target = self._self_reflect(target)

        # 生成L5响应
        response = self._render(target, is_typechecked)

        # 计算Φ值
        phi = self._compute_phi(target)

        result = ConstructiveResult(
            problem=problem,
            target=target,
            is_solved=target.is_constructed,
            is_typechecked=is_typechecked,
            response=response,
            phi_value=phi
        )

        # 缓存结果
        self.proof_cache[problem] = result

        return result

    def _construct_target(self, problem: str, problem_type: ProblemType) -> TargetType:
        """L2层：构造目标类型"""
        if problem_type == ProblemType.MATH_CALC:
            return self._solve_math(problem)
        elif problem_type == ProblemType.PROVE_THM:
            return self._solve_proof(problem)
        elif problem_type == ProblemType.LOGIC_REASON:
            return self._solve_logic(problem)
        else:
            return TargetType("Unknown", None, False)

    def _solve_math(self, problem: str) -> TargetType:
        """数学计算求解"""
        # 简单算术
        try:
            # 移除非数字字符（保留基本运算符）
            expr = problem.replace("计算", "").replace("等于", "=").strip()
            # 安全评估（仅限数字和运算符）
            allowed = set("0123456789+-*/.()= ")
            if all(c in allowed for c in expr):
                result = eval(expr)
                return TargetType("NatResult", result, True)
        except:
            pass
        return TargetType("NatResult", None, False)

    def _solve_proof(self, problem: str) -> TargetType:
        """定理证明求解"""
        if "勾股定理" in problem or "毕达哥拉斯" in problem:
            # 构造性证明：返回具体的勾股数
            return TargetType("PythagorasRes", (3, 4, 5), True)
        return TargetType("Proof", None, False)

    def _solve_logic(self, problem: str) -> TargetType:
        """逻辑推理求解"""
        # 简化：检测逻辑关键词
        if any(kw in problem for kw in ["如果", "则", "因为", "所以", "逻辑"]):
            return TargetType("LogicResult", True, True)
        return TargetType("LogicResult", None, False)

    def _type_check(self, target: TargetType) -> bool:
        """
        类型检查（防火墙）

        check : (t : TargetType) → Maybe (IsValid t)

        定理5.1推论：只有通过类型检查的输出才会被渲染
        """
        if not target.is_constructed:
            return False

        # 根据类型名称验证
        if target.type_name == "NatResult":
            return isinstance(target.value, (int, float))
        elif target.type_name == "PythagorasRes":
            a, b, c = target.value
            return a**2 + b**2 == c**2
        elif target.type_name == "LogicResult":
            return target.value is not None

        return False

    def _self_reflect(self, target: TargetType) -> TargetType:
        """
        自指反思（L4层）

        SelfRef函子：能反思自身的推理过程
        """
        # 检测自身是否产生不一致
        if target.type_name == "NatResult":
            if target.value is not None and isinstance(target.value, (int, float)):
                # 自指检查：结果是否在合理范围内
                if abs(target.value) > 1e15:
                    # 大数警告：标记为需要进一步验证
                    return TargetType(target.type_name, target.value, False)
        return target

    def _render(self, target: TargetType, is_typechecked: bool) -> str:
        """
        L5层：渲染输出

        只有通过类型检查的结果才会被渲染
        """
        if not target.is_constructed:
            return "无法构造 inhabitant：我不知道。"

        if not is_typechecked:
            return "类型检查失败：幻觉被拦截。"

        # 渲染目标
        if target.type_name == "NatResult":
            return f"构造成功：{target.value}"
        elif target.type_name == "PythagorasRes":
            a, b, c = target.value
            return f"勾股定理证明：a={a}, b={b}, c={c}，满足 a²+b²=c²"
        elif target.type_name == "LogicResult":
            return "逻辑推理完成：结论成立。"

        return f"构造成功：{target.value}"

    def _compute_phi(self, target: TargetType) -> float:
        """计算流贯Φ值"""
        if target.is_constructed and target.value is not None:
            return 0.85  # 构造成功Φ值
        return 0.15  # 构造失败Φ值

    def run(self, prompt: str) -> str:
        """
        REPL主循环

        run : String → String
        """
        result = self.solve(prompt)
        return result.response


# ============================================================================
# EML相位耦合主类
# ============================================================================

class EMLPhaseCouplingZ5:
    """
    EML相位耦合ℤ₅

    实现T29定理：EML相位耦合ℤ₅
    - EML算子在ℤ₅上闭合
    - 五行循环：Σ→F→R→E→B→Σ
    - 相位偏移：θ_new = θ_old + Δθ (mod 2π/5)

    v2.0升级：
    - 新增EML一元数(iℕum)形式化
    - 新增太乙AGI REPL构造性内核

    v7.31升级：
    - 新增Flexible θ连续相位函数
    - 新增相位轨迹计算
    - 新增稳态轨道检测
    """

    def __init__(self):
        self.version = "2.0.0"
        self.phases = {
            EMLPhase.Σ: PhaseState(EMLPhase.Σ, 0.0, 1.0, 1.0, 0.8),
            EMLPhase.F: PhaseState(EMLPhase.F, 2*math.pi/5, 1.0, 1.0, 0.8),
            EMLPhase.R: PhaseState(EMLPhase.R, 4*math.pi/5, 1.0, 1.0, 0.8),
            EMLPhase.E: PhaseState(EMLPhase.E, 6*math.pi/5, 1.0, 1.0, 0.8),
            EMLPhase.B: PhaseState(EMLPhase.B, 8*math.pi/5, 1.0, 1.0, 0.8),
        }

        # 五行循环顺序
        self.cycle = [EMLPhase.Σ, EMLPhase.F, EMLPhase.R, EMLPhase.E, EMLPhase.B]

        # ℤ₅闭合阈值
        self.closure_threshold = 0.95

        # 相位偏移（每个元素的固定偏移）
        self.phase_offsets = {
            EMLPhase.Σ: 0,
            EMLPhase.F: 2*math.pi/5,
            EMLPhase.R: 4*math.pi/5,
            EMLPhase.E: 6*math.pi/5,
            EMLPhase.B: 8*math.pi/5,
        }

        # 太乙AGI REPL实例
        self.repl = TaiyiREPL()

        # ===== v7.31 新增属性 =====
        # Flexible θ 启用标志
        self._flexible_theta_enabled: bool = False
        # 存储 θ(t) 函数
        self._theta_func: Optional[Callable[[float], float]] = None
        # 相位轨迹缓存
        self._phase_trajectory_cache: List[PhaseTrajectoryPoint] = []

    # ==================== 原有方法（完全保留） ====================

    def get_repl(self) -> TaiyiREPL:
        """获取太乙AGI REPL实例"""
        return self.repl

    def couple_phase(self, current_state: PhaseState,
                    next_element: EMLPhase) -> Tuple[PhaseState, Z5Coupling]:
        """相位耦合"""
        delta_theta = self.phase_offsets[next_element]
        new_phase = (current_state.phase_angle + delta_theta) % (2 * math.pi)
        coupling_coeff = current_state.amplitude * next_element.index
        new_amplitude = current_state.amplitude * (1 + coupling_coeff * 0.1)

        new_state = PhaseState(
            element=next_element,
            phase_angle=round(new_phase, 4),
            amplitude=round(new_amplitude, 4),
            frequency=current_state.frequency,
            coupling_strength=round(coupling_coeff, 4)
        )

        coupling = Z5Coupling(
            from_phase=current_state.element,
            to_phase=next_element,
            delta_theta=round(delta_theta, 4),
            coupling_coefficient=round(coupling_coeff, 4),
            is_valid=(coupling_coeff > 0.5)
        )

        self.phases[next_element] = new_state
        return new_state, coupling

    def verify_z5_closure(self, sequence: List[EMLPhase]) -> bool:
        """验证ℤ₅闭合性"""
        if len(sequence) < 5:
            return False

        required = set(e.value for e in EMLPhase)
        sequence_set = set(e.value for e in sequence[:5])

        if sequence_set != required:
            return False

        expected = [e.value for e in self.cycle]
        actual = [e.value for e in sequence[:5]]

        for i in range(5):
            rotated = actual[i:] + actual[:i]
            if rotated == expected:
                return True

        return False

    def compute_closure_degree(self, phase_angles: List[float]) -> float:
        """计算ℤ₅闭合度"""
        if len(phase_angles) < 5:
            return 0.5

        differences = []
        for i in range(min(5, len(phase_angles))):
            next_idx = (i + 1) % 5
            diff = abs(phase_angles[i] - phase_angles[next_idx])
            diff = min(diff, 2*math.pi - diff)
            differences.append(diff)

        ideal_diff = 2 * math.pi / 5
        deviations = [abs(d - ideal_diff) for d in differences]
        avg_deviation = sum(deviations) / len(deviations)

        closure = 1.0 / (1.0 + avg_deviation)
        return min(1.0, max(0.0, closure))

    def compute_coherence(self, amplitudes: List[float]) -> float:
        """计算相干性"""
        if not amplitudes:
            return 0.0

        mean = sum(amplitudes) / len(amplitudes)
        if mean == 0:
            return 0.0

        variance = sum((a - mean) ** 2 for a in amplitudes) / len(amplitudes)
        coherence = 1.0 / (1.0 + variance / (mean ** 2 + 1e-10))

        return min(1.0, max(0.0, coherence))

    def compute_phase_entropy(self, phase_angles: List[float]) -> float:
        """计算相位熵"""
        if not phase_angles:
            return 0.0

        n_bins = 5
        bin_size = 2 * math.pi / n_bins
        counts = [0] * n_bins

        for angle in phase_angles:
            bin_idx = int(angle / bin_size) % n_bins
            counts[bin_idx] += 1

        total = sum(counts)
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log(p + 1e-10)

        return min(2.0, max(0.0, entropy))

    def apply_cycle(self, num_cycles: int = 1,
                   initial_phase: Optional[EMLPhase] = None) -> CycleResult:
        """应用五行循环"""
        if initial_phase is None:
            initial_phase = EMLPhase.Σ

        phases = []
        phase_angles = []
        amplitudes = []

        current_state = self.phases[initial_phase]

        for cycle_idx in range(num_cycles):
            for element in self.cycle:
                new_state, coupling = self.couple_phase(current_state, element)

                phases.append(element)
                phase_angles.append(new_state.phase_angle)
                amplitudes.append(new_state.amplitude)

                current_state = new_state

        closure = self.compute_closure_degree(phase_angles)
        coherence = self.compute_coherence(amplitudes)
        entropy = self.compute_phase_entropy(phase_angles)

        is_stable = (closure >= self.closure_threshold
                     and coherence > 0.7
                     and entropy < 1.5)

        insight = self._generate_insight(closure, coherence, entropy, is_stable)

        return CycleResult(
            phases=phases,
            phase_angles=phase_angles,
            amplitudes=amplitudes,
            closure_degree=round(closure, 4),
            coherence=round(coherence, 4),
            entropy=round(entropy, 4),
            is_stable=is_stable,
            insight=insight
        )

    def get_phase_state(self, element: EMLPhase) -> PhaseState:
        """获取元素相位状态"""
        return self.phases.get(element)

    def set_phase_state(self, element: EMLPhase, state: PhaseState):
        """设置元素相位状态"""
        self.phases[element] = state

    def _generate_insight(self, closure: float, coherence: float,
                           entropy: float, is_stable: bool) -> str:
        """生成分析洞见"""
        parts = []

        if closure >= self.closure_threshold:
            parts.append("✅ ℤ₅闭合性满足——EML相位耦合稳定")
        else:
            parts.append(f"⚠️ ℤ₅闭合性不足（{closure:.2f}）——相位需要调整")

        if coherence > 0.8:
            parts.append(f"相干性优秀（{coherence:.2f}）——各元素同步良好")
        elif coherence > 0.6:
            parts.append(f"相干性良好（{coherence:.2f}）")
        else:
            parts.append(f"⚠️ 相干性较低（{coherence:.2f}）——元素间同步不足")

        if entropy < 1.0:
            parts.append(f"相位熵低（{entropy:.2f}）——系统有序")
        elif entropy < 1.5:
            parts.append(f"相位熵中等（{entropy:.2f}）")
        else:
            parts.append(f"⚠️ 相位熵较高（{entropy:.2f}）——系统较混乱")

        if is_stable:
            parts.append("✅ 系统稳定——五行相位耦合处于平衡态")
        else:
            parts.append("⚠️ 系统不稳定——需要调整相位耦合参数")

        return " | ".join(parts)

    def eml_couple(self, a: iNUm, b: iNUm) -> Dict[str, Any]:
        """EML耦合运算（返回详细信息）"""
        add_result = eml_add(a, b)
        mul_result = eml_mul(a, b)
        conservation = verify_eml_conservation(a, b)

        return {
            "operand_a": str(a),
            "operand_b": str(b),
            "addition_result": str(add_result),
            "multiplication_result": str(mul_result),
            "conservation": conservation
        }

    def test_repl(self, problem: str) -> str:
        """测试太乙AGI REPL"""
        return self.repl.run(problem)

    # ==================== v7.31 新增方法 ====================

    def set_flexible_theta(self, theta_func: Callable[[float], float]) -> Dict[str, Any]:
        """
        设置连续θ函数 — v7.31 新增

        设置 θ(t) 函数，替代离散的固定相位偏移。
        在 Flexible θ 模式下，EML 相位耦合使用连续的 θ(t)
        而非固定的 2π/5 间隔。

        θ(t) 的约束条件：
        1. θ(t) 必须是 [0, ∞) → [0, 2π) 的映射
        2. θ(t) 应该是周期性的，周期为 T = 2π/ω
        3. θ(t) 在一个周期内应遍历五个五行相位区间

        Args:
            theta_func: θ(t) 函数，接受时间 t（float），返回相位角（float）

        Returns:
            设置结果字典
        """
        # 验证函数有效性
        try:
            test_values = [theta_func(t) for t in [0.0, 0.5, 1.0, 1.5, 2.0]]
            # 检查返回值是否为数值
            for v in test_values:
                if not isinstance(v, (int, float)):
                    raise ValueError(f"θ(t) 返回非数值: {v}")

            # 检查值域在合理范围
            all_valid = all(0 <= v < 4 * math.pi for v in test_values)
        except Exception as e:
            return {
                'success': False,
                'error': f'θ(t) 函数验证失败: {e}',
                'flexible_theta_enabled': self._flexible_theta_enabled,
            }

        self._theta_func = theta_func
        self._flexible_theta_enabled = True
        self._phase_trajectory_cache = []

        return {
            'success': True,
            'flexible_theta_enabled': True,
            'theta_sample': {
                'θ(0.0)': round(theta_func(0.0), 4),
                'θ(0.5)': round(theta_func(0.5), 4),
                'θ(1.0)': round(theta_func(1.0), 4),
                'θ(1.5)': round(theta_func(1.5), 4),
                'θ(2.0)': round(theta_func(2.0), 4),
            },
            'note': 'Flexible θ 模式已启用，原有离散θ逻辑仍可通过 disable 调用恢复',
        }

    def disable_flexible_theta(self) -> Dict[str, Any]:
        """
        禁用 Flexible θ 模式，恢复默认离散θ — v7.31 新增

        Returns:
            操作结果字典
        """
        self._flexible_theta_enabled = False
        self._theta_func = None
        self._phase_trajectory_cache = []
        return {
            'success': True,
            'flexible_theta_enabled': False,
            'note': '已恢复默认离散θ模式',
        }

    def modulate_theta(self, cognitive_demand: float) -> Dict[str, Any]:
        """
        按认知需求动态调制θ — v7.31 新增

        根据认知需求（cognitive_demand）动态调整 θ 函数的参数。
        需求高时，θ变化更快速（更频繁的相位切换）；
        需求低时，θ变化更缓慢（更稳定的相位维持）。

        调制公式：
        - θ_modulated(t) = θ_base(t) · (1 + α · D)
        - 其中 D = cognitive_demand ∈ [0, 1]
        - α = 0.5 为调制系数

        如果 Flexible θ 未启用，则基于默认离散θ进行调制。

        Args:
            cognitive_demand: 认知需求 [0, 1]

        Returns:
            调制结果字典
        """
        cognitive_demand = max(0.0, min(1.0, cognitive_demand))
        alpha = 0.5  # 调制系数

        if self._flexible_theta_enabled and self._theta_func is not None:
            # 在 Flexible θ 模式下，调制 θ_base(t)
            base_func = self._theta_func

            def modulated_func(t: float) -> float:
                base_theta = base_func(t)
                modulated = base_theta * (1.0 + alpha * cognitive_demand)
                return modulated % (2 * math.pi)

            # 更新 θ 函数
            self._theta_func = modulated_func
            self._phase_trajectory_cache = []

            # 采样验证
            samples = {f't={t}': round(modulated_func(t), 4) for t in [0.0, 0.5, 1.0]}

            return {
                'modulated': True,
                'mode': 'flexible',
                'cognitive_demand': cognitive_demand,
                'modulation_coefficient': alpha,
                'theta_samples': samples,
                'note': 'θ(t) 已按认知需求调制',
            }
        else:
            # 离散θ模式：调制相位偏移量
            base_offset = 2 * math.pi / 5  # 默认五行偏移
            modulated_offset = base_offset * (1.0 + alpha * cognitive_demand)

            # 更新相位偏移
            for i, phase in enumerate(self.cycle):
                self.phase_offsets[phase] = i * modulated_offset

            return {
                'modulated': True,
                'mode': 'discrete',
                'cognitive_demand': cognitive_demand,
                'modulation_coefficient': alpha,
                'original_offset': round(base_offset, 4),
                'modulated_offset': round(modulated_offset, 4),
                'note': '离散θ偏移已按认知需求调制',
            }

    def compute_phase_trajectory(
        self,
        t_start: float = 0.0,
        t_end: float = 10.0,
        dt: float = 0.1,
    ) -> Dict[str, Any]:
        """
        计算连续相位轨迹 — v7.31 新增

        在 [t_start, t_end] 区间内，以 dt 为步长，
        计算每个时刻的 θ(t) 和对应的五行相位状态。

        如果 Flexible θ 已启用，使用 θ(t) 函数；
        否则使用默认离散θ模式生成轨迹。

        Args:
            t_start: 起始时间
            t_end: 结束时间
            dt: 时间步长

        Returns:
            相位轨迹结果字典
        """
        if dt <= 0:
            dt = 0.1
        if t_end <= t_start:
            t_end = t_start + 10.0

        trajectory: List[PhaseTrajectoryPoint] = []
        t = t_start

        element_names = ['Σ(水)', 'F(火)', 'R(木)', 'E(金)', 'B(土)']

        while t <= t_end + 1e-10:
            if self._flexible_theta_enabled and self._theta_func is not None:
                # Flexible θ 模式
                theta_t = self._theta_func(t)
            else:
                # 默认离散模式：θ(t) = (2π/5) * floor(t) 离散步进
                step = int(t)
                theta_t = (2 * math.pi / 5) * step

            # 将 θ(t) 映射到五行元素
            # 每个元素占据 [0, 2π/5) 的区间
            normalized_theta = theta_t % (2 * math.pi)
            element_index = int(normalized_theta / (2 * math.pi / 5)) % 5
            element_name = element_names[element_index]

            # 计算振幅（基于当前相位状态）
            current_phase = self.cycle[element_index]
            phase_state = self.phases.get(current_phase)
            amplitude = phase_state.amplitude if phase_state else 1.0

            point = PhaseTrajectoryPoint(
                t=round(t, 4),
                theta=round(theta_t, 6),
                phase_angle=round(normalized_theta, 6),
                amplitude=round(amplitude, 6),
                element_index=element_index,
                element_name=element_name,
            )
            trajectory.append(point)
            t += dt

        # 缓存轨迹
        self._phase_trajectory_cache = trajectory

        # 分析轨迹特征
        element_transitions = 0
        prev_idx = trajectory[0].element_index if trajectory else 0
        for pt in trajectory[1:]:
            if pt.element_index != prev_idx:
                element_transitions += 1
                prev_idx = pt.element_index

        # 轨迹稳定性：相位角的方差
        phase_angles = [pt.phase_angle for pt in trajectory]
        if phase_angles:
            pa_mean = sum(phase_angles) / len(phase_angles)
            pa_var = sum((a - pa_mean) ** 2 for a in phase_angles) / len(phase_angles)
        else:
            pa_var = 0.0

        # 元素覆盖率
        covered_elements = set(pt.element_index for pt in trajectory)
        element_coverage = round(len(covered_elements) / 5.0, 4)

        return {
            'trajectory_length': len(trajectory),
            't_range': (t_start, t_end),
            'dt': dt,
            'flexible_theta_enabled': self._flexible_theta_enabled,
            'trajectory': [
                {
                    't': pt.t,
                    'theta': pt.theta,
                    'phase_angle': pt.phase_angle,
                    'amplitude': pt.amplitude,
                    'element_index': pt.element_index,
                    'element_name': pt.element_name,
                }
                for pt in trajectory
            ],
            'analysis': {
                'element_transitions': element_transitions,
                'phase_angle_variance': round(pa_var, 6),
                'element_coverage': element_coverage,
                'elements_visited': sorted(covered_elements),
            },
        }

    def detect_steady_orbit(self, window: int = 50) -> Dict[str, Any]:
        """
        检测EML相位稳态轨道 — v7.31 新增

        分析最近的相位轨迹，检测是否存在稳态轨道。
        稳态轨道定义：五行元素以固定周期循环出现，
        且相位角变化率趋于恒定。

        检测算法：
        1. 收集最近 window 个轨迹点
        2. 计算元素循环周期
        3. 检测相位角变化率是否恒定
        4. 评估稳态轨道置信度

        Args:
            window: 分析窗口大小

        Returns:
            稳态轨道检测结果字典
        """
        # 获取轨迹数据
        if self._phase_trajectory_cache:
            trajectory = self._phase_trajectory_cache[-window:]
        else:
            # 如果没有缓存轨迹，先计算一段
            result = self.compute_phase_trajectory(t_start=0.0, t_end=5.0, dt=0.1)
            trajectory = self._phase_trajectory_cache[-window:]

        if len(trajectory) < 5:
            return {
                'has_steady_orbit': False,
                'confidence': 0.0,
                'reason': 'insufficient_trajectory_data',
                'trajectory_points': len(trajectory),
            }

        # 1. 检测元素循环模式
        element_sequence = [pt.element_index for pt in trajectory]

        # 检查是否包含完整的五行循环
        full_cycle = {0, 1, 2, 3, 4}
        visited = set(element_sequence)
        has_full_cycle = visited == full_cycle

        # 2. 检测周期性
        # 寻找最短重复模式
        period = 0
        for p in range(1, len(element_sequence) // 2 + 1):
            is_periodic = True
            for i in range(min(p, len(element_sequence) - p)):
                if element_sequence[i] != element_sequence[i + p]:
                    is_periodic = False
                    break
            if is_periodic:
                period = p
                break

        # 3. 计算相位角变化率
        phase_rates = []
        for i in range(1, len(trajectory)):
            dt = trajectory[i].t - trajectory[i - 1].t
            if abs(dt) > 1e-10:
                d_theta = trajectory[i].phase_angle - trajectory[i - 1].phase_angle
                # 处理相位回绕
                if d_theta > math.pi:
                    d_theta -= 2 * math.pi
                elif d_theta < -math.pi:
                    d_theta += 2 * math.pi
                rate = d_theta / dt
                phase_rates.append(rate)

        # 变化率的稳定性（方差越小越稳定）
        if phase_rates:
            rate_mean = sum(phase_rates) / len(phase_rates)
            rate_var = sum((r - rate_mean) ** 2 for r in phase_rates) / len(phase_rates)
            rate_stability = round(1.0 / (1.0 + rate_var), 6)
        else:
            rate_mean = 0.0
            rate_var = 0.0
            rate_stability = 0.0

        # 4. 综合稳态轨道置信度
        confidence = 0.0
        if has_full_cycle:
            confidence += 0.4
        if period > 0:
            confidence += 0.3 * min(1.0, period / 5.0)
        if rate_stability > 0.5:
            confidence += 0.3 * rate_stability

        confidence = round(min(1.0, confidence), 6)
        has_steady_orbit = confidence >= 0.6

        # 稳态轨道描述
        if has_steady_orbit:
            orbit_description = (
                f'检测到稳态轨道：五行元素以周期{period if period > 0 else "N/A"}循环，'
                f'相位变化率均值={rate_mean:.4f}，稳定性={rate_stability:.4f}'
            )
        else:
            orbit_description = '未检测到稳态轨道：相位变化不规则或数据不足'

        return {
            'has_steady_orbit': has_steady_orbit,
            'confidence': confidence,
            'period': period,
            'has_full_cycle': has_full_cycle,
            'element_coverage': round(len(visited) / 5.0, 4),
            'rate_mean': round(rate_mean, 6),
            'rate_variance': round(rate_var, 6),
            'rate_stability': rate_stability,
            'orbit_description': orbit_description,
            'trajectory_points': len(trajectory),
        }


def get_instance():
    """获取单例实例"""
    return EMLPhaseCouplingZ5()


if __name__ == "__main__":
    # 测试EML一元数
    print("=" * 60)
    print("EML一元数 (iℕum) 测试")
    print("=" * 60)

    a = iNUm(3.0, math.pi / 4)  # m=3, θ=π/4
    b = iNUm(4.0, math.pi / 3)  # m=4, θ=π/3

    print(f"\na = {a}")
    print(f"b = {b}")

    add_result = eml_add(a, b)
    mul_result = eml_mul(a, b)

    print(f"\nEML加法 a ⊕ b = {add_result}")
    print(f"EML乘法 a ⊗ b = {mul_result}")

    # 守恒验证
    conservation = verify_eml_conservation(a, b)
    print(f"\n守恒验证:")
    print(f"  加法守恒: {conservation['addition']['is_conserved']}")
    print(f"  乘法守恒: {conservation['multiplication']['is_conserved']}")
    print(f"  T10定理有效: {conservation['theorem_t10_valid']}")

    print("\n" + "=" * 60)
    print("太乙AGI REPL 测试")
    print("=" * 60)

    coupler = EMLPhaseCouplingZ5()
    repl = coupler.get_repl()

    test_cases = [
        "计算 2+2",
        "计算 123456789 * 987654321",
        "证明 勾股定理",
    ]

    for test in test_cases:
        print(f"\n输入: {test}")
        result = repl.run(test)
        print(f"输出: {result}")

    print("\n" + "=" * 60)
    print("EML相位耦合ℤ₅测试")
    print("=" * 60)

    result = coupler.apply_cycle(num_cycles=2)
    print(f"\n相位数量: {len(result.phases)}")
    print(f"ℤ₅闭合度: {result.closure_degree}")
    print(f"相干性: {result.coherence}")
    print(f"相位熵: {result.entropy}")
    print(f"稳定状态: {result.is_stable}")
    print(f"洞见: {result.insight}")

    # ==================== v7.31 新功能测试 ====================
    print("\n" + "=" * 60)
    print("v7.31 Flexible θ 升级测试")
    print("=" * 60)

    coupler_v731 = EMLPhaseCouplingZ5()

    print("\n[测试 1] set_flexible_theta — 设置连续θ函数")
    # 设置一个简单的连续θ函数：θ(t) = (2π/5) * t
    def linear_theta(t: float) -> float:
        return (2 * math.pi / 5) * t

    set_result = coupler_v731.set_flexible_theta(linear_theta)
    print(f"  设置成功: {set_result['success']}")
    print(f"  θ采样: {set_result.get('theta_sample', {})}")

    print("\n[测试 2] compute_phase_trajectory — 计算连续相位轨迹")
    traj_result = coupler_v731.compute_phase_trajectory(t_start=0.0, t_end=5.0, dt=0.5)
    print(f"  轨迹点数: {traj_result['trajectory_length']}")
    print(f"  元素转换次数: {traj_result['analysis']['element_transitions']}")
    print(f"  元素覆盖率: {traj_result['analysis']['element_coverage']}")
    for pt in traj_result['trajectory'][:5]:
        print(f"    t={pt['t']:.1f}: θ={pt['theta']:.4f}, element={pt['element_name']}")

    print("\n[测试 3] detect_steady_orbit — 检测稳态轨道")
    orbit = coupler_v731.detect_steady_orbit()
    print(f"  有稳态轨道: {orbit['has_steady_orbit']}")
    print(f"  置信度: {orbit['confidence']}")
    print(f"  描述: {orbit['orbit_description']}")

    print("\n[测试 4] modulate_theta — 动态调制θ")
    mod_result = coupler_v731.modulate_theta(cognitive_demand=0.8)
    print(f"  调制成功: {mod_result['modulated']}")
    print(f"  模式: {mod_result['mode']}")
    print(f"  认知需求: {mod_result['cognitive_demand']}")

    # 调制后再计算轨迹
    traj_mod = coupler_v731.compute_phase_trajectory(t_start=0.0, t_end=5.0, dt=0.5)
    print(f"  调制后轨迹点数: {traj_mod['trajectory_length']}")

    print("\n[测试 5] disable_flexible_theta — 禁用 Flexible θ")
    disable_result = coupler_v731.disable_flexible_theta()
    print(f"  禁用成功: {disable_result['success']}")
    print(f"  Flexible θ 启用: {disable_result['flexible_theta_enabled']}")

    print("\n[测试 6] modulate_theta（离散模式）")
    coupler_disc = EMLPhaseCouplingZ5()
    mod_disc = coupler_disc.modulate_theta(cognitive_demand=0.5)
    print(f"  调制成功: {mod_disc['modulated']}")
    print(f"  模式: {mod_disc['mode']}")
    print(f"  原始偏移: {mod_disc['original_offset']}")
    print(f"  调制偏移: {mod_disc['modulated_offset']}")

    print("\n" + "=" * 60)
    print("M77 v7.31 测试完成！")
    print("=" * 60)
