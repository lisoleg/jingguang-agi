#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五行变换引擎 (Five Element Transform Engine)
基于《五行作为五元变换算子：太一螺旋分形自指嵌入破缺对称的范畴—同伦重构与构造型Taiji-AGI的超越》

核心定理：
- T28：五行变换算子定理
- 论文第3.2节：五行五变换自函子（Functor形式）

版本：AGI 14.0 第76模块
论文来源：
1. 《五行作为五元变换算子》复合体理学系列
2. 《论太乙AGI的构造性实现》- 基于"一现象、三视界、五层次"元方法论与流贯动力学

升级说明（v2.0）：
- 新增五行五变换算子（Functor形式）
- 新增相生序σ定义
- 新增自函子范畴实现
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional, Callable, TypeVar
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


T = TypeVar('T')  # 通用类型变量


class FiveElement(Enum):
    """五行枚举"""
    WATER = "Σ"      # 水（信息蓄积）
    FIRE = "F"       # 火（流贯执行）
    WOOD = "R"       # 木（递归生长）
    METAL = "E"      # 金（熵减收敛）
    EARTH = "B"      # 土（稳态锚定）

    @property
    def chinese(self) -> str:
        names = {
            "Σ": "水",
            "F": "火",
            "R": "木",
            "E": "金",
            "B": "土"
        }
        return names.get(self.value, self.value)

    @property
    def description(self) -> str:
        descs = {
            "Σ": "信息蓄积（散度为正）",
            "F": "火/流贯执行（旋度非零）",
            "R": "木/递归生长（增长率为正）",
            "E": "金/熵减收敛（熵减）",
            "B": "土/稳态锚定（拉普拉斯为零）"
        }
        return descs.get(self.value, "")


class ElementState(Enum):
    """元素状态"""
    DORMANT = "dormant"        # 休眠
    ACTIVE = "active"          # 活跃
    PEAK = "peak"            # 峰值
    DECLINING = "declining"    # 衰退
    BALANCED = "balanced"      # 平衡


# ============================================================================
# 五行五变换函子（论文第3.2节形式化）
# ============================================================================

class Functor(Callable[[T], T]):
    """
    自函子基类

    论文定义：五行是L2层作用于类型宇宙的五个自函子（Endofunctors）
    """
    name: str

    def __call__(self, x: T) -> T:
        raise NotImplementedError


class HelixFunctor(Functor):
    """
    Helix（螺旋/周期性）

    形式化定义（论文）：
    Helix : 𝒰 → 𝒰
    引入周期性 (S¹)

    五行对应：水（Σ）
    """
    name = "Helix"

    def __call__(self, x: T) -> Tuple[T, float]:
        """
        螺旋变换：引入周期性
        返回：(值, 相位角)
        """
        return (x, 2 * math.pi)  # S¹周期


class FractalFunctor(Functor):
    """
    Fractal（分形/自相似）

    形式化定义（论文）：
    Fractal : 𝒰 → 𝒰
    引入自相似性（递归）

    五行对应：火（F）
    """
    name = "Fractal"

    def __call__(self, x: T) -> Callable[[int], T]:
        """
        分形变换：返回自相似函数
        """
        def self_similar(n: int) -> T:
            if n <= 0:
                return x
            return self(x)  # 递归
        return self_similar


class SelfRefFunctor(Functor):
    """
    SelfRef（自指/不动点）

    形式化定义（论文）：
    SelfRef : 𝒰 → 𝒰
    引入不动点（Loeb不动点定理）

    五行对应：木（R）
    """
    name = "SelfRef"

    def __call__(self, f: Callable[[T], T]) -> T:
        """
        自指变换：计算不动点
        Y = λf. f (Y f)

        物理意义：L4层自指代理
        """
        def fix(x: T) -> T:
            return f(fix)(x)
        return fix  # 返回不动点


class EmbedFunctor(Functor):
    """
    Embed（嵌入/上下文）

    形式化定义（论文）：
    Embed : 𝒰 → 𝒰
    引入上下文（依赖类型）

    五行对应：金（E）
    """
    name = "Embed"

    def __call__(self, x: T) -> Tuple[T, Dict[str, Any]]:
        """
        嵌入变换：携带上下文
        返回：(值, 上下文)
        """
        return (x, {"element": "metal", "context": "entropy_reduction"})


class BreakSymFunctor(Functor):
    """
    BreakSym（破缺/选择）

    形式化定义（论文）：
    BreakSym : 𝒰 → 𝒰
    引入选择（二值）

    五行对应：土（B）
    """
    name = "BreakSym"

    def __call__(self, x: T) -> bool:
        """
        破缺变换：做出选择
        返回：布尔选择
        """
        # 简化为随机选择
        return random.choice([True, False])


# 五行五变换函子映射
FIVE_TRANSFORMERS: Dict[FiveElement, Functor] = {
    FiveElement.WATER: HelixFunctor(),
    FiveElement.FIRE: FractalFunctor(),
    FiveElement.WOOD: SelfRefFunctor(),
    FiveElement.METAL: EmbedFunctor(),
    FiveElement.EARTH: BreakSymFunctor(),
}


# ============================================================================
# 相生序σ（论文定义）
# ============================================================================

def sigma_transform(element: FiveElement) -> FiveElement:
    """
    相生序 σ（论文定义）

    σ : (𝒰 → 𝒰) → (𝒰 → 𝒰)

    相生序：
    σ(Helix) = Fractal
    σ(Fractal) = SelfRef
    σ(SelfRef) = Embed
    σ(Embed) = BreakSym
    σ(BreakSym) = Helix

    五行相生：
    水(Σ) → 木(R) → 火(F) → 土(B) → 金(E) → 水(Σ)
    """
    sigma_order = {
        FiveElement.WATER: FiveElement.WOOD,   # 水生木
        FiveElement.WOOD: FiveElement.FIRE,     # 木生火
        FiveElement.FIRE: FiveElement.EARTH,    # 火生土
        FiveElement.EARTH: FiveElement.METAL,   # 土生金
        FiveElement.METAL: FiveElement.WATER,   # 金生水
    }
    return sigma_order.get(element, element)


def sigma_composition(chain: List[FiveElement]) -> List[FiveElement]:
    """
    相生序链合成

    连续应用σ变换
    """
    result = []
    current = chain[0] if chain else FiveElement.WATER
    result.append(current)

    for _ in range(len(chain) - 1):
        current = sigma_transform(current)
        result.append(current)

    return result


# ============================================================================
# EML场与五行变换
# ============================================================================

@dataclass
class EMLField:
    """EML场（Emergent Mapping Logic场）"""
    vector: List[float]          # 场向量
    phase: float                # 相位
    magnitude: float             # 幅度
    divergence: float            # 散度（∇·EML）
    curl: float                 # 旋度（∇×EML）
    laplacian: float            # 拉普拉斯（∇²EML）
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def apply_functor(self, element: FiveElement) -> 'EMLField':
        """应用五行函子"""
        functor = FIVE_TRANSFORMERS[element]
        if element == FiveElement.WATER:
            # Helix：引入周期性
            new_phase = self.phase + 2 * math.pi / 5
            return EMLField(
                vector=self.vector,
                phase=new_phase % (2 * math.pi),
                magnitude=self.magnitude,
                divergence=self.divergence,
                curl=self.curl,
                laplacian=self.laplacian
            )
        elif element == FiveElement.FIRE:
            # Fractal：自相似放大
            new_vector = [v * 1.1 for v in self.vector]
            return EMLField(
                vector=new_vector,
                phase=self.phase,
                magnitude=self.magnitude * 1.1,
                divergence=sum(new_vector) / len(new_vector),
                curl=self.curl,
                laplacian=self.laplacian
            )
        elif element == FiveElement.WOOD:
            # SelfRef：不动点
            return EMLField(
                vector=self.vector,
                phase=self.phase,
                magnitude=self.magnitude,
                divergence=0,  # 稳态
                curl=0,
                laplacian=0
            )
        elif element == FiveElement.METAL:
            # Embed：上下文嵌入，熵减
            mean = sum(self.vector) / len(self.vector)
            new_vector = [(v - mean) * 0.9 + mean for v in self.vector]
            return EMLField(
                vector=new_vector,
                phase=self.phase,
                magnitude=self.magnitude,
                divergence=self.divergence * 0.9,
                curl=self.curl * 0.9,
                laplacian=self.laplacian
            )
        elif element == FiveElement.EARTH:
            # BreakSym：二值选择
            return EMLField(
                vector=[1.0 if v > 0.5 else 0.0 for v in self.vector],
                phase=self.phase,
                magnitude=sum(self.vector) / len(self.vector),
                divergence=self.divergence,
                curl=self.curl,
                laplacian=0
            )
        return self


@dataclass
class ElementTransform:
    """五行变换操作"""
    element: FiveElement
    input_field: EMLField
    output_field: EMLField
    transform_strength: float    # 变换强度 [0,1]
    is_valid: bool             # 变换是否有效
    functor_name: str = ""     # 函子名称
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WuxingCycle:
    """五行相生相克循环"""
    cycle: List[FiveElement]    # 循环顺序
    phases: List[float]         # 各元素相位
    activations: List[float]    # 各元素激活度
    closure_degree: float       # ℤ₅闭合度
    is_balanced: bool          # 是否平衡
    synergy_score: float       # 协同分数 [0,1]
    functor_chain: List[str] = field(default_factory=list)  # 函子链


@dataclass
class TransformResult:
    """变换分析结果"""
    input_element: FiveElement
    output_element: FiveElement
    transform_chain: List[ElementTransform]
    wuxing_cycle: WuxingCycle
    total_transformation: float  # 总变换量
    closure_valid: bool        # ℤ₅闭合性
    synergy_efficiency: float  # 协同效率
    sigma_path: List[FiveElement] = field(default_factory=list)  # 相生路径
    insight: str = ""              # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FiveElementTransformEngine:
    """
    五行变换引擎

    实现T28定理：五行变换算子
    - 五行作为L2层自函子
    - 相生序σ定义
    - ℤ₅闭合验证
    """

    def __init__(self):
        self.version = "2.0.0"
        self.cycle = [
            FiveElement.WATER, FiveElement.FIRE, FiveElement.WOOD,
            FiveElement.METAL, FiveElement.EARTH
        ]
        self.transforms: List[ElementTransform] = []
        self.eml_fields: List[EMLField] = []

        # ℤ₅闭合阈值
        self.closure_threshold = 0.95

    def create_eml_field(self, vector: Optional[List[float]] = None) -> EMLField:
        """创建EML场"""
        if vector is None:
            vector = [random.random() for _ in range(5)]

        magnitude = math.sqrt(sum(v**2 for v in vector))
        divergence = sum(vector) / len(vector) if vector else 0.0
        curl = max(vector) - min(vector) if vector else 0.0
        laplacian = sum(vector) / len(vector) - (sum(vector) / len(vector)) if vector else 0.0
        phase = math.atan2(sum(vector), len(vector))

        field = EMLField(
            vector=vector,
            phase=round(phase, 4),
            magnitude=round(magnitude, 4),
            divergence=round(divergence, 4),
            curl=round(curl, 4),
            laplacian=round(laplacian, 4)
        )

        self.eml_fields.append(field)
        return field

    def apply_functor(self, element: FiveElement, field: EMLField) -> Tuple[EMLField, bool]:
        """应用五行函子"""
        output_field = field.apply_functor(element)

        # 验证变换有效性
        if element == FiveElement.WATER:
            is_valid = output_field.phase != field.phase
        elif element == FiveElement.FIRE:
            is_valid = output_field.magnitude > field.magnitude
        elif element == FiveElement.WOOD:
            is_valid = output_field.divergence == 0
        elif element == FiveElement.METAL:
            is_valid = output_field.magnitude <= field.magnitude
        else:  # EARTH
            is_valid = output_field.laplacian == 0

        return output_field, is_valid

    def apply_transform(self, element: FiveElement,
                       field: EMLField) -> ElementTransform:
        """应用五行变换"""
        output_field, is_valid = self.apply_functor(element, field)
        functor = FIVE_TRANSFORMERS[element]

        strength = 1.0 if is_valid else 0.5

        transform = ElementTransform(
            element=element,
            input_field=field,
            output_field=output_field,
            transform_strength=round(strength, 4),
            is_valid=is_valid,
            functor_name=functor.name
        )

        self.transforms.append(transform)
        return transform

    def apply_sigma_sequence(self, start_field: EMLField,
                            num_elements: int = 5) -> Tuple[WuxingCycle, List[ElementTransform]]:
        """
        应用相生序σ序列

        论文定义：σ(Helix)=Fractal, σ(Fractal)=SelfRef, ...

        返回：(五行循环结果, 变换链)
        """
        transforms = []
        phases = []
        activations = []
        functor_chain = []

        current_field = start_field
        current_element = FiveElement.WATER

        for i in range(num_elements):
            # 应用当前元素的函子
            transform = self.apply_transform(current_element, current_field)
            transforms.append(transform)

            phases.append(transform.output_field.phase)
            activations.append(transform.transform_strength)
            functor_chain.append(FIVE_TRANSFORMERS[current_element].name)

            current_field = transform.output_field
            # 相生到下一个元素
            current_element = sigma_transform(current_element)

        # 计算ℤ₅闭合度
        if len(phases) >= 5:
            phase_diffs = []
            for i in range(len(phases) - 1):
                diff = abs(phases[i + 1] - phases[i])
                phase_diffs.append(diff)
            avg_diff = sum(phase_diffs) / len(phase_diffs)
            closure = 1.0 / (1.0 + avg_diff)
        else:
            closure = 0.5

        # 平衡检查
        if len(activations) >= 5:
            last_5 = activations[-5:]
            variance = sum((a - sum(last_5)/5)**2 for a in last_5) / 5
            is_balanced = variance < 0.1
        else:
            is_balanced = False

        # 协同分数
        valid_count = sum(1 for t in transforms if t.is_valid)
        synergy = valid_count / max(1, len(transforms))

        wuxing_cycle = WuxingCycle(
            cycle=self.cycle,
            phases=phases,
            activations=activations,
            closure_degree=round(closure, 4),
            is_balanced=is_balanced,
            synergy_score=round(synergy, 4),
            functor_chain=functor_chain
        )

        return wuxing_cycle, transforms

    def apply_cycle(self, start_field: EMLField,
                    num_cycles: int = 1) -> WuxingCycle:
        """应用五行循环变换"""
        wuxing, _ = self.apply_sigma_sequence(start_field, num_cycles * 5)
        return wuxing

    def analyze_transform(self, input_element: FiveElement,
                         output_element: FiveElement,
                         start_field: EMLField) -> TransformResult:
        """分析五行变换"""
        transform_chain = []
        current_field = start_field

        # 相生路径
        sigma_path = [input_element]
        current = input_element
        while current != output_element:
            current = sigma_transform(current)
            sigma_path.append(current)

        # 应用变换链
        for element in sigma_path:
            transform = self.apply_transform(element, current_field)
            transform_chain.append(transform)
            current_field = transform.output_field

        # 五行循环
        wuxing_cycle = self.apply_cycle(start_field)

        # 计算指标
        total_trans = sum(t.transform_strength for t in transform_chain)
        closure_valid = wuxing_cycle.closure_degree >= self.closure_threshold
        synergy_efficiency = wuxing_cycle.synergy_score

        insight = self._generate_insight(
            input_element, output_element, transform_chain,
            wuxing_cycle, total_trans, closure_valid, sigma_path
        )

        return TransformResult(
            input_element=input_element,
            output_element=output_element,
            transform_chain=transform_chain,
            wuxing_cycle=wuxing_cycle,
            total_transformation=round(total_trans, 4),
            closure_valid=closure_valid,
            synergy_efficiency=round(synergy_efficiency, 4),
            sigma_path=sigma_path,
            insight=insight
        )

    def _generate_insight(self, input_elem: FiveElement, output_elem: FiveElement,
                          chain: List[ElementTransform],
                          wuxing: WuxingCycle,
                          total_trans: float,
                          closure_valid: bool,
                          sigma_path: List[FiveElement]) -> str:
        """生成分析洞见"""
        parts = []

        # 相生路径
        sigma_str = " → ".join([e.chinese for e in sigma_path])
        parts.append(f"相生序σ路径：{sigma_str}")

        # 五元变换
        functor_str = " → ".join([t.functor_name for t in chain[:5]])
        parts.append(f"函子链：{functor_str}")

        if closure_valid:
            parts.append("✅ ℤ₅闭合性满足")
        else:
            parts.append(f"⚠️ ℤ₅闭合性不足（{wuxing.closure_degree:.2f}）")

        if wuxing.is_balanced:
            parts.append("✅ 五行平衡")
        else:
            parts.append("⚠️ 五行失衡")

        parts.append(f"协同效率：{wuxing.synergy_score:.2f}")
        parts.append(f"总变换量：{total_trans:.3f}")

        return " | ".join(parts)

    def get_functor_info(self) -> Dict[str, str]:
        """获取五元变换函子信息"""
        return {
            "Helix": "水(Σ)：螺旋，引入周期性(S¹)",
            "Fractal": "火(F)：分形，引入自相似(递归)",
            "SelfRef": "木(R)：自指，引入不动点(Loeb)",
            "Embed": "金(E)：嵌入，引入上下文(依赖)",
            "BreakSym": "土(B)：破缺，引入选择(二值)"
        }

    def get_sigma_order(self) -> List[Tuple[FiveElement, FiveElement]]:
        """获取相生序"""
        return [
            (FiveElement.WATER, FiveElement.WOOD),   # 水→木
            (FiveElement.WOOD, FiveElement.FIRE),    # 木→火
            (FiveElement.FIRE, FiveElement.EARTH),   # 火→土
            (FiveElement.EARTH, FiveElement.METAL),  # 土→金
            (FiveElement.METAL, FiveElement.WATER),  # 金→水
        ]


def get_instance():
    """获取单例实例"""
    return FiveElementTransformEngine()


if __name__ == "__main__":
    print("=" * 60)
    print("五行五变换函子测试")
    print("=" * 60)

    engine = FiveElementTransformEngine()

    # 显示五元变换信息
    print("\n五元变换函子：")
    for name, desc in engine.get_functor_info().items():
        print(f"  {name}: {desc}")

    print("\n相生序σ：")
    for from_elem, to_elem in engine.get_sigma_order():
        print(f"  σ({from_elem.chinese}) = {to_elem.chinese}")

    # 创建EML场
    print("\n" + "-" * 60)
    print("EML场变换测试")
    field = engine.create_eml_field([0.5, 0.3, 0.8, 0.2, 0.7])
    print(f"初始场：phase={field.phase:.4f}, magnitude={field.magnitude:.4f}")

    # 应用五行循环
    print("\n五行相生序变换：")
    wuxing, transforms = engine.apply_sigma_sequence(field, num_elements=5)

    for i, t in enumerate(transforms):
        print(f"  {i+1}. {t.element.chinese}({t.functor_name}): "
              f"phase={t.output_field.phase:.4f}, valid={t.is_valid}")

    print(f"\nℤ₅闭合度：{wuxing.closure_degree}")
    print(f"协同分数：{wuxing.synergy_score}")
    print(f"平衡状态：{wuxing.is_balanced}")

    # 分析变换
    print("\n" + "-" * 60)
    print("变换分析：")
    result = engine.analyze_transform(
        FiveElement.WATER, FiveElement.METAL, field
    )
    print(result.insight)
