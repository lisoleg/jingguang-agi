#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五行Token动力学耦合器 (Five Element Token Dynamics Coupler)
基于《五行作为五元变换算子：太一螺旋分形自指嵌入破缺对称的范畴—同伦重构与构造型Taiji-AGI的超越》

核心概念：
- Token生成 = 五行变换序列
- 水（信息蓄积）：上下文编码
- 火（流贯执行）：EML相位耦合
- 木（递归生长）：自回归生成
- 金（熵减收敛）：选择最低熵的Token
- 土（稳态锚定）：输出稳定Token

版本：AGI 14.0 第80模块
论文来源：《五行作为五元变换算子》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Element(Enum):
    """五行元素"""
    WATER = "Σ"      # 水（信息蓄积）
    FIRE = "F"       # 火（流贯执行）
    WOOD = "R"       # 木（递归生长）
    METAL = "E"      # 金（熵减收敛）
    EARTH = "B"      # 土（稳态锚定）
    
    @property
    def chinese(self) -> str:
        return {"Σ": "水", "F": "火", "R": "木", "E": "金", "B": "土"}.get(self.value, self.value)
    
    @property
    def description(self) -> str:
        return {
            "Σ": "信息蓄积（上下文编码）",
            "F": "流贯执行（EML相位耦合）",
            "R": "递归生长（自回归生成）",
            "E": "熵减收敛（选择最低熵）",
            "B": "稳态锚定（输出稳定）"
        }.get(self.value, "")


@dataclass
class Token:
    """Token"""
    token_id: str
    text: str
    element: Element         # 生成该Token的元素
    entropy: float          # 熵值
    probability: float      # 生成概率
    phase: float            # 相位
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TokenSequence:
    """Token序列"""
    tokens: List[Token]
    sequence_entropy: float  # 序列熵
    coherence: float         # 相干性
    stability: float        # 稳定性
    is_balanced: bool       # 五行是否平衡
    insight: str = ""


@dataclass
class GenerationResult:
    """生成结果"""
    context: str
    tokens: List[Token]
    element_sequence: List[Element]
    final_token: Optional[Token]
    sequence_result: TokenSequence
    is_valid: bool
    confidence: float
    insight: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class WuxingTokenDynamicsCoupler:
    """
    五行Token动力学耦合器
    
    将Token生成视为五行变换序列：
    - Σ（水）：信息蓄积 - 上下文编码
    - F（火）：流贯执行 - EML相位耦合
    - R（木）：递归生长 - 自回归生成
    - E（金）：熵减收敛 - 选择最低熵Token
    - B（土）：稳态锚定 - 输出稳定Token
    """
    
    def __init__(self):
        self.version = "1.0.0"
        
        # 五行循环顺序
        self.cycle = [
            Element.WATER, Element.FIRE, Element.WOOD,
            Element.METAL, Element.EARTH
        ]
        
        # 五行映射表（简化）
        self.element_mapping = {
            "水": Element.WATER,
            "火": Element.FIRE,
            "木": Element.WOOD,
            "金": Element.METAL,
            "土": Element.EARTH,
        }
        
        # 词汇表（简化）
        self.vocabulary = [
            "的", "是", "在", "有", "和", "了", "我", "你", "他", "她",
            "这", "那", "大", "小", "好", "坏", "高", "低", "多", "少",
            "上", "下", "左", "右", "前", "后", "中", "内", "外", "里"
        ]
        
        # 生成历史
        self.history: List[GenerationResult] = []
    
    def water_accumulate(self, context: str) -> Dict[str, Any]:
        """
        Σ（水）：信息蓄积 - 上下文编码
        
        参数：
            context: 上下文
        
        返回：
            水状态
        """
        # 编码上下文
        encoded = {
            "context_length": len(context),
            "semantic_density": min(1.0, len(context) / 100.0),
            "info_content": len(set(context)) / max(1, len(context))
        }
        return encoded
    
    def fire_execute(self, water_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        F（火）：流贯执行 - EML相位耦合
        
        参数：
            water_state: 水状态
        
        返回：
            火状态
        """
        # EML相位耦合
        semantic_density = water_state.get("semantic_density", 0.5)
        phase = semantic_density * 2 * math.pi
        
        state = {
            "phase": phase,
            "coupling_strength": min(1.0, semantic_density + 0.2),
            "flow_intensity": semantic_density * 1.5
        }
        return state
    
    def wood_grow(self, fire_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        R（木）：递归生长 - 自回归生成
        
        参数：
            fire_state: 火状态
        
        返回：
            木状态
        """
        # 自回归增长
        flow_intensity = fire_state.get("flow_intensity", 0.5)
        growth_rate = flow_intensity * 0.8
        
        state = {
            "growth_rate": growth_rate,
            "recursion_depth": int(growth_rate * 10),
            "token_candidates": int(growth_rate * len(self.vocabulary))
        }
        return state
    
    def metal_reduce(self, wood_state: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        E（金）：熵减收敛 - 选择最低熵的Token
        
        参数：
            wood_state: 木状态
        
        返回：
            候选Token列表（按熵排序）
        """
        candidates = wood_state.get("token_candidates", 10)
        
        # 生成候选Token及其熵值
        token_entropy_pairs = []
        for i in range(min(candidates, len(self.vocabulary))):
            word = self.vocabulary[i]
            # 简化：随机生成熵值
            entropy = random.uniform(0.1, 0.9)
            token_entropy_pairs.append((word, entropy))
        
        # 按熵排序（选择最低熵的）
        token_entropy_pairs.sort(key=lambda x: x[1])
        
        return token_entropy_pairs
    
    def earth_anchor(self, metal_state: List[Tuple[str, float]]) -> Token:
        """
        B（土）：稳态锚定 - 输出稳定Token
        
        参数：
            metal_state: 金属状态（候选Token列表）
        
        返回：
            稳定的Token
        """
        if not metal_state:
            word = self.vocabulary[0]
        else:
            # 选择最低熵的Token
            word, entropy = metal_state[0]
        
        # 创建Token
        token = Token(
            token_id=f"T-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            text=word,
            element=Element.EARTH,
            entropy=entropy if metal_state else 0.5,
            probability=0.8,
            phase=0.0
        )
        
        return token
    
    def token_generation_as_wuxing(self, context: str) -> GenerationResult:
        """
        Token生成 = 五行变换序列（主方法）
        
        参数：
            context: 上下文
        
        返回：
            生成结果
        """
        # 1. 水（信息蓄积）
        water_state = self.water_accumulate(context)
        
        # 2. 火（流贯执行）
        fire_state = self.fire_execute(water_state)
        
        # 3. 木（递归生长）
        wood_state = self.wood_grow(fire_state)
        
        # 4. 金（熵减收敛）
        metal_state = self.metal_reduce(wood_state)
        
        # 5. 土（稳态锚定）
        final_token = self.earth_anchor(metal_state)
        
        # 记录元素序列
        element_sequence = [Element.WATER, Element.FIRE, Element.WOOD, 
                          Element.METAL, Element.EARTH]
        
        # 生成Token序列
        tokens = []
        sequence_entropy = 0.0
        
        # 简化：每个元素生成一个中间Token
        for element in element_sequence:
            word_idx = random.randint(0, len(self.vocabulary) - 1)
            word = self.vocabulary[word_idx]
            
            token = Token(
                token_id=f"T-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{element.value}",
                text=word,
                element=element,
                entropy=random.uniform(0.2, 0.8),
                probability=random.uniform(0.5, 1.0),
                phase=element.value == "Σ" and 0.0 or 2*math.pi/5
            )
            tokens.append(token)
            sequence_entropy += token.entropy
        
        # 添加最终Token
        tokens.append(final_token)
        
        # 计算序列指标
        avg_entropy = sequence_entropy / len(tokens)
        coherence = 1.0 - avg_entropy  # 熵低则相干性高
        stability = 1.0 - (max(t.entropy for t in tokens) - min(t.entropy for t in tokens))
        
        # 五行是否平衡（简化：检查每个元素是否都有代表）
        elements_present = set(t.element for t in tokens)
        is_balanced = len(elements_present) == 5
        
        # 创建序列结果
        sequence_result = TokenSequence(
            tokens=tokens,
            sequence_entropy=round(sequence_entropy, 4),
            coherence=round(coherence, 4),
            stability=round(stability, 4),
            is_balanced=is_balanced,
            insight=f"序列包含{len(tokens)}个Token，熵{avg_entropy:.2f}，相干性{coherence:.2f}"
        )
        
        # 判断是否有效（所有五行变换都成功）
        is_valid = is_balanced and coherence > 0.5
        
        # 计算置信度
        confidence = coherence if is_valid else coherence * 0.5
        
        # 生成洞见
        insight = self._generate_insight(
            context, tokens, element_sequence, final_token,
            sequence_result, is_valid
        )
        
        result = GenerationResult(
            context=context,
            tokens=tokens,
            element_sequence=element_sequence,
            final_token=final_token,
            sequence_result=sequence_result,
            is_valid=is_valid,
            confidence=round(confidence, 4),
            insight=insight
        )
        
        # 记录历史
        self.history.append(result)
        
        return result
    
    def _generate_insight(self, context: str, tokens: List[Token],
                         element_seq: List[Element], final_token: Token,
                         seq_result: TokenSequence,
                         is_valid: bool) -> str:
        """生成分析洞见"""
        parts = []
        
        parts.append(f"上下文长度：{len(context)}")
        parts.append(f"五行变换序列：{'→'.join(e.chinese for e in element_seq)}")
        
        if is_valid:
            parts.append("✅ 五行Token生成有效——变换序列完整")
        else:
            parts.append("⚠️ 五行Token生成不稳定")
        
        parts.append(f"生成Token：{final_token.text}")
        parts.append(f"Token熵：{final_token.entropy:.3f}")
        
        if seq_result.is_balanced:
            parts.append("✅ 五行平衡——各元素协同良好")
        else:
            parts.append("⚠️ 五行不平衡")
        
        parts.append(f"序列相干性：{seq_result.coherence:.2f}")
        parts.append(f"序列稳定性：{seq_result.stability:.2f}")
        
        return " | ".join(parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.history:
            return {
                "total_generations": 0,
                "valid_rate": 0.0,
                "avg_coherence": 0.0,
                "avg_stability": 0.0
            }
        
        valid_count = sum(1 for r in self.history if r.is_valid)
        avg_coherence = sum(r.sequence_result.coherence for r in self.history) / len(self.history)
        avg_stability = sum(r.sequence_result.stability for r in self.history) / len(self.history)
        
        return {
            "total_generations": len(self.history),
            "valid_rate": valid_count / len(self.history),
            "avg_coherence": round(avg_coherence, 4),
            "avg_stability": round(avg_stability, 4)
        }


def get_instance():
    """获取单例实例"""
    return WuxingTokenDynamicsCoupler()


if __name__ == "__main__":
    # 测试代码
    coupler = WuxingTokenDynamicsCoupler()
    
    # 测试生成
    contexts = [
        "这是一个测试上下文",
        "关于人工智能的讨论",
        "数学证明需要逻辑推理"
    ]
    
    for context in contexts:
        result = coupler.token_generation_as_wuxing(context)
        
        print(f"上下文：{context}")
        print(f"  五行序列：{' → '.join(e.chinese for e in result.element_sequence)}")
        print(f"  生成Token：{result.final_token.text}")
        print(f"  Token熵：{result.final_token.entropy:.3f}")
        print(f"  有效：{result.is_valid}")
        print(f"  置信度：{result.confidence}")
        print(f"  洞见：{result.insight}")
        print()
    
    # 统计
    stats = coupler.get_statistics()
    print("统计：")
    print(f"  总生成数：{stats['total_generations']}")
    print(f"  有效率：{stats['valid_rate']:.2%}")
    print(f"  平均相干性：{stats['avg_coherence']:.4f}")
    print(f"  平均稳定性：{stats['avg_stability']:.4f}")
