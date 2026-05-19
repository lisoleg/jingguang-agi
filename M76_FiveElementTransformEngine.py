#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五行变换引擎 (Five Element Transform Engine)
基于《五行作为五元变换算子：太一螺旋分形自指嵌入破缺对称的范畴—同伦重构与构造型Taiji-AGI的超越》

核心定理：
- T28：五行变换算子定理
  五行作为五元变换算子作用于EML场：
  Σ（水/信息蓄积）：∇·EML > 0（散度为正）
  F（火/流贯执行）：∇×EML ≠ 0（旋度非零）
  R（木/递归生长）：∂EML/∂t > 0（增长率为正）
  E（金/熵减收敛）：∂S/∂t < 0（熵减）
  B（土/稳态锚定）：∇²EML = 0（拉普拉斯为零）

版本：AGI 14.0 第76模块
论文来源：《五行作为五元变换算子》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


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
            "F": "流贯执行（旋度非零）",
            "R": "递归生长（增长率为正）",
            "E": "熵减收敛（熵减）",
            "B": "稳态锚定（拉普拉斯为零）"
        }
        return descs.get(self.value, "")


class ElementState(Enum):
    """元素状态"""
    DORMANT = "dormant"        # 休眠
    ACTIVE = "active"          # 活跃
    PEAK = "peak"            # 峰值
    DECLINING = "declining"    # 衰退
    BALANCED = "balanced"      # 平衡


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


@dataclass
class ElementTransform:
    """五行变换操作"""
    element: FiveElement
    input_field: EMLField
    output_field: EMLField
    transform_strength: float    # 变换强度 [0,1]
    is_valid: bool             # 变换是否有效
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
    insight: str              # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FiveElementTransformEngine:
    """
    五行变换引擎
    
    实现T28定理：五行变换算子
    - Σ（水/信息蓄积）：∇·EML > 0
    - F（火/流贯执行）：∇×EML ≠ 0
    - R（木/递归生长）：∂EML/∂t > 0
    - E（金/熵减收敛）：∂S/∂t < 0
    - B（土/稳态锚定）：∇²EML = 0
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.cycle = [
            FiveElement.WATER, FiveElement.FIRE, FiveElement.WOOD,
            FiveElement.METAL, FiveElement.EARTH
        ]  # 五行循环顺序
        self.transforms: List[ElementTransform] = []
        self.eml_fields: List[EMLField] = []
        
        # ℤ₅闭合阈值
        self.closure_threshold = 0.95
    
    def create_eml_field(self, vector: Optional[List[float]] = None) -> EMLField:
        """创建EML场"""
        if vector is None:
            vector = [random.random() for _ in range(5)]
        
        # 计算场属性
        magnitude = math.sqrt(sum(v**2 for v in vector))
        
        # 简化：计算散度、旋度、拉普拉斯
        divergence = sum(vector) / len(vector) if vector else 0.0
        curl = max(vector) - min(vector) if vector else 0.0
        laplacian = sum(vector) / len(vector) - (sum(vector) / len(vector)) if vector else 0.0
        
        # 相位（基于向量方向）
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
    
    def water_transform(self, field: EMLField) -> Tuple[EMLField, bool]:
        """
        Σ（水/信息蓄积）：∇·EML > 0（散度为正）
        
        水元素：将信息蓄积到EML场中
        """
        # 输入场的散度
        div = field.divergence
        
        # 如果散度>0，变换有效
        is_valid = div > 0
        
        # 创建新场（信息蓄积）
        new_vector = [v * 1.1 for v in field.vector]  # 放大
        new_field = self.create_eml_field(new_vector)
        
        return new_field, is_valid
    
    def fire_transform(self, field: EMLField) -> Tuple[EMLField, bool]:
        """
        F（火/流贯执行）：∇×EML ≠ 0（旋度非零）
        
        火元素：驱动EML场流贯执行
        """
        curl = field.curl
        
        # 如果旋度≠0，变换有效
        is_valid = curl != 0
        
        # 创建新场（增加旋度）
        new_vector = [v * (1 + abs(curl)) for v in field.vector]
        new_field = self.create_eml_field(new_vector)
        
        return new_field, is_valid
    
    def wood_transform(self, field: EMLField) -> Tuple[EMLField, bool]:
        """
        R（木/递归生长）：∂EML/∂t > 0（增长率为正）
        
        木元素：促进EML场递归生长
        """
        # 简化：增长率基于向量元素数量
        growth_rate = len(field.vector) / 10.0
        
        # 如果增长率>0，变换有效
        is_valid = growth_rate > 0
        
        # 创建新场（增长）
        new_vector = [v * (1 + growth_rate) for v in field.vector]
        new_field = self.create_eml_field(new_vector)
        
        return new_field, is_valid
    
    def metal_transform(self, field: EMLField) -> Tuple[EMLField, bool]:
        """
        E（金/熵减收敛）：∂S/∂t < 0（熵减）
        
        金元素：使EML场熵减收敛
        """
        # 简化：计算"熵"（基于向量方差）
        mean = sum(field.vector) / len(field.vector)
        entropy = sum((v - mean)**2 for v in field.vector) / len(field.vector)
        
        # 金元素减少熵（使向量更集中）
        new_vector = [(v - mean) * 0.8 + mean for v in field.vector]
        new_field = self.create_eml_field(new_vector)
        
        # 新场熵减？ΔS < 0
        new_mean = sum(new_vector) / len(new_vector)
        new_entropy = sum((v - new_mean)**2 for v in new_vector) / len(new_vector)
        is_valid = new_entropy < entropy
        
        return new_field, is_valid
    
    def earth_transform(self, field: EMLField) -> Tuple[EMLField, bool]:
        """
        B（土/稳态锚定）：∇²EML = 0（拉普拉斯为零）
        
        土元素：使EML场稳态锚定
        """
        lap = field.laplacian
        
        # 如果拉普拉斯≈0，变换有效（稳态）
        is_valid = abs(lap) < 0.01
        
        # 创建新场（使拉普拉斯趋近于0）
        mean = sum(field.vector) / len(field.vector)
        new_vector = [mean + (v - mean) * 0.95 for v in field.vector]
        new_field = self.create_eml_field(new_vector)
        
        return new_field, is_valid
    
    def apply_transform(self, element: FiveElement, 
                       field: EMLField) -> ElementTransform:
        """
        应用五行变换
        
        返回：
            变换操作结果
        """
        if element == FiveElement.WATER:
            output_field, is_valid = self.water_transform(field)
        elif element == FiveElement.FIRE:
            output_field, is_valid = self.fire_transform(field)
        elif element == FiveElement.WOOD:
            output_field, is_valid = self.wood_transform(field)
        elif element == FiveElement.METAL:
            output_field, is_valid = self.metal_transform(field)
        elif element == FiveElement.EARTH:
            output_field, is_valid = self.earth_transform(field)
        else:
            output_field = field
            is_valid = False
        
        # 计算变换强度
        strength = 1.0 if is_valid else 0.5
        
        transform = ElementTransform(
            element=element,
            input_field=field,
            output_field=output_field,
            transform_strength=round(strength, 4),
            is_valid=is_valid
        )
        
        self.transforms.append(transform)
        return transform
    
    def apply_cycle(self, start_field: EMLField,
                    num_cycles: int = 1) -> WuxingCycle:
        """
        应用五行循环变换
        
        参数：
            start_field: 起始场
            num_cycles: 循环次数
        
        返回：
            五行循环结果
        """
        current_field = start_field
        phases = []
        activations = []
        
        for cycle_idx in range(num_cycles):
            for element in self.cycle:
                transform = self.apply_transform(element, current_field)
                current_field = transform.output_field
                phases.append(transform.output_field.phase)
                activations.append(transform.transform_strength)
        
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
        
        # 检查是否平衡（各元素激活度相近）
        if len(activations) >= 5:
            last_5 = activations[-5:]
            variance = sum((a - sum(last_5)/5)**2 for a in last_5) / 5
            is_balanced = variance < 0.1
        else:
            is_balanced = False
        
        # 计算协同分数
        valid_count = sum(1 for t in self.transforms[-25:] if t.is_valid)
        synergy = valid_count / max(1, len(self.transforms[-25:]))
        
        return WuxingCycle(
            cycle=self.cycle,
            phases=phases,
            activations=activations,
            closure_degree=round(closure, 4),
            is_balanced=is_balanced,
            synergy_score=round(synergy, 4)
        )
    
    def analyze_transform(self, input_element: FiveElement,
                         output_element: FiveElement,
                         start_field: EMLField) -> TransformResult:
        """
        分析五行变换（主方法）
        
        返回：
            变换分析结果
        """
        # 找到变换链
        transform_chain = []
        current_field = start_field
        
        # 从输入到输出的变换链
        input_idx = self.cycle.index(input_element)
        output_idx = self.cycle.index(output_element)
        
        # 遍历从输入到输出的元素
        idx = input_idx
        while idx != output_idx:
            element = self.cycle[idx]
            transform = self.apply_transform(element, current_field)
            transform_chain.append(transform)
            current_field = transform.output_field
            idx = (idx + 1) % 5
        
        # 应用完整的五行循环
        wuxing_cycle = self.apply_cycle(start_field)
        
        # 计算总变换量
        total_trans = sum(t.transform_strength for t in transform_chain)
        
        # 检查ℤ₅闭合性
        closure_valid = wuxing_cycle.closure_degree >= self.closure_threshold
        
        # 协同效率
        synergy_efficiency = wuxing_cycle.synergy_score
        
        # 生成洞见
        insight = self._generate_insight(
            input_element, output_element, transform_chain,
            wuxing_cycle, total_trans, closure_valid
        )
        
        return TransformResult(
            input_element=input_element,
            output_element=output_element,
            transform_chain=transform_chain,
            wuxing_cycle=wuxing_cycle,
            total_transformation=round(total_trans, 4),
            closure_valid=closure_valid,
            synergy_efficiency=round(synergy_efficiency, 4),
            insight=insight
        )
    
    def _generate_insight(self, input_elem: FiveElement, output_elem: FiveElement,
                          chain: List[ElementTransform],
                          wuxing: WuxingCycle,
                          total_trans: float,
                          closure_valid: bool) -> str:
        """生成分析洞见"""
        parts = []
        
        parts.append(f"五行变换：{input_elem.chinese} → {output_elem.chinese}")
        
        if closure_valid:
            parts.append("✅ ℤ₅闭合性满足——五行循环稳定")
        else:
            parts.append("⚠️ ℤ₅闭合性不足——建议调整变换序列")
        
        if wuxing.is_balanced:
            parts.append("✅ 五行平衡——各元素协同良好")
        else:
            parts.append("⚠️ 五行失衡——部分元素过于活跃或休眠")
        
        if wuxing.synergy_score > 0.8:
            parts.append(f"协同效率 {wuxing.synergy_score:.2f} 优秀")
        elif wuxing.synergy_score > 0.6:
            parts.append(f"协同效率 {wuxing.synergy_score:.2f} 良好")
        else:
            parts.append(f"协同效率 {wuxing.synergy_score:.2f} 较低")
        
        parts.append(f"变换链长度：{len(chain)}")
        parts.append(f"总变换量：{total_trans:.3f}")
        
        return " | ".join(parts)


def get_instance():
    """获取单例实例"""
    return FiveElementTransformEngine()


if __name__ == "__main__":
    # 测试代码
    engine = FiveElementTransformEngine()
    
    # 创建EML场
    field = engine.create_eml_field([0.5, 0.3, 0.8, 0.2, 0.7])
    
    print(f"EML场：")
    print(f"  向量: {field.vector}")
    print(f"  散度: {field.divergence}")
    print(f"  旋度: {field.curl}")
    print(f"  拉普拉斯: {field.laplacian}")
    print()
    
    # 应用五行变换
    result = engine.analyze_transform(
        FiveElement.WATER, FiveElement.METAL, field
    )
    
    print(f"五行变换分析：")
    print(f"  {result.input_element.chinese} → {result.output_element.chinese}")
    print(f"  ℤ₅闭合: {result.closure_valid}")
    print(f"  协同效率: {result.synergy_efficiency}")
    print(f"  总变换量: {result.total_transformation}")
    print(f"  洞见: {result.insight}")
    print()
    
    # 五行循环
    wuxing = engine.apply_cycle(field)
    print(f"五行循环：")
    print(f"  闭合度: {wuxing.closure_degree}")
    print(f"  平衡状态: {wuxing.is_balanced}")
    print(f"  协同分数: {wuxing.synergy_score}")
