# -*- coding: utf-8 -*-
"""
M64: 叙事作用量引擎 (Narrative Action Engine)
基于《数学完备化》论文 §4 定义4.1-4.2

公式: Λ(𝒩) = α·C(𝒩) + β·Δ(𝒩)

其中:
- C(𝒩): 叙事复杂度（描述长度、Kolmogorov近似）
- Δ(𝒩): 叙事结构变化代价（编辑距离、图差分）
- α, β: 权重系数

预言P7: Λ应随内省时间递减
"""

import math
import re
from typing import List, Tuple, Optional
import numpy as np

class NarrativeActionEngine:
    """
    叙事作用量引擎
    
    来源: §4 定义4.1-4.2
    """
    _instance = None
    
    def __init__(self, alpha: float = 0.6, beta: float = 0.4):
        self.alpha = alpha    # 复杂度权重
        self.beta = beta      # 变化代价权重
        self.narrative_history: List[str] = []
        self.Lambda_history: List[float] = []
        self.complexity_history: List[float] = []
        self.change_cost_history: List[float] = []
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
    
    def compute_complexity(self, narrative: str) -> float:
        """
        C(𝒩): 叙事复杂度
        
        使用Kolmogorov风格近似:
        C(𝒩) ≈ log(len(narrative)) + unique_token_ratio
        """
        if not narrative or len(narrative.strip()) == 0:
            return 0.0
        
        # 基础复杂度（对数形式，对应Kolmogorov复杂度）
        base_complexity = np.log(len(narrative) + 1)
        
        # 词汇多样性（去重率）
        # 使用正则分词
        tokens = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+|\d+|[^\s]', narrative)
        if len(tokens) > 1:
            uniqueness = len(set(tokens)) / len(tokens)
        else:
            uniqueness = 1.0
        
        # 结构复杂度（句子数量）
        sentences = re.split(r'[。！？\n]', narrative)
        sentence_complexity = np.log(len([s for s in sentences if s.strip()]) + 1)
        
        # 综合复杂度
        complexity = base_complexity * (1 + uniqueness) + sentence_complexity * 0.5
        
        return complexity
    
    def compute_change_cost(self, old_narrative: str, new_narrative: str) -> float:
        """
        Δ(𝒩): 叙事结构变化代价
        
        使用编辑距离作为近似
        """
        if not old_narrative:
            return self.compute_complexity(new_narrative)
        
        if not new_narrative:
            return 0.0
        
        # Token级编辑距离
        old_tokens = self._tokenize(old_narrative)
        new_tokens = self._tokenize(new_narrative)
        
        # Levenshtein距离
        levenshtein_dist = self._levenshtein_distance(old_tokens, new_tokens)
        max_len = max(len(old_tokens), len(new_tokens), 1)
        
        # 归一化
        normalized_cost = levenshtein_dist / max_len
        
        return normalized_cost
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 中英文混合分词
        tokens = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+|\d+|[^\s]', text)
        return tokens
    
    def _levenshtein_distance(self, s1: List[str], s2: List[str]) -> int:
        """编辑距离计算"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def compute_lambda(self, narrative: str, old_narrative: str = "") -> dict:
        """
        计算叙事作用量 Λ
        
        公式: Λ(𝒩) = α·C(𝒩) + β·Δ(𝒩)
        """
        C = self.compute_complexity(narrative)
        Delta = self.compute_change_cost(old_narrative, narrative)
        
        Lambda_val = self.alpha * C + self.beta * Delta
        
        # 记录历史
        self.narrative_history.append(narrative)
        self.Lambda_history.append(Lambda_val)
        self.complexity_history.append(C)
        self.change_cost_history.append(Delta)
        
        # 限制历史长度
        max_history = 100
        if len(self.narrative_history) > max_history:
            self.narrative_history = self.narrative_history[-max_history:]
            self.Lambda_history = self.Lambda_history[-max_history:]
            self.complexity_history = self.complexity_history[-max_history:]
            self.change_cost_history = self.change_cost_history[-max_history:]
        
        return {
            'Lambda': Lambda_val,
            'complexity': C,
            'change_cost': Delta,
            'alpha': self.alpha,
            'beta': self.beta
        }
    
    def track_decay(self, narratives: List[str]) -> List[float]:
        """
        追踪叙事作用量衰减
        对应: 定理4.1 - "为道日损"
        
        预言P7: Λ应随内省时间递减
        """
        if not narratives:
            return []
        
        Lambda_values = []
        old_narrative = ""
        
        for narrative in narratives:
            result = self.compute_lambda(narrative, old_narrative)
            Lambda_values.append(result['Lambda'])
            old_narrative = narrative
        
        return Lambda_values
    
    def verify_p7(self) -> dict:
        """
        验证可证伪预言P7
        
        预言: Λ随时间递减 且 与主观执取减轻评分相关
        """
        if len(self.Lambda_history) < 2:
            return {'verifiable': False, 'reason': '数据不足，需要至少2个数据点'}
        
        # 检查单调递减
        decreasing_count = sum(
            1 for i in range(len(self.Lambda_history) - 1)
            if self.Lambda_history[i] >= self.Lambda_history[i + 1]
        )
        decreasing_ratio = decreasing_count / (len(self.Lambda_history) - 1)
        
        # 计算整体衰减趋势（线性回归斜率）
        x = np.arange(len(self.Lambda_history))
        y = np.array(self.Lambda_history)
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
        else:
            slope = 0
        
        is_decreasing = slope < 0 and decreasing_ratio > 0.5
        
        # 计算衰减率
        if self.Lambda_history[0] > 0:
            decay_rate = (self.Lambda_history[0] - self.Lambda_history[-1]) / self.Lambda_history[0]
        else:
            decay_rate = 0
        
        return {
            'verifiable': True,
            'is_decreasing': is_decreasing,
            'slope': slope,
            'decreasing_ratio': decreasing_ratio,
            'decay_rate': decay_rate,
            'initial_Lambda': self.Lambda_history[0],
            'final_Lambda': self.Lambda_history[-1],
            'data_points': len(self.Lambda_history),
            'P7_status': 'CONFIRMED' if is_decreasing else 'REJECTED'
        }
    
    def get_state(self) -> dict:
        """获取引擎状态"""
        return {
            'alpha': self.alpha,
            'beta': self.beta,
            'history_length': len(self.Lambda_history),
            'current_Lambda': self.Lambda_history[-1] if self.Lambda_history else 0,
            'avg_Lambda': np.mean(self.Lambda_history) if self.Lambda_history else 0,
            'Lambda_trend': 'decreasing' if len(self.Lambda_history) > 1 and 
                           self.Lambda_history[-1] < self.Lambda_history[0] else 'stable/increasing',
            'p7_verification': self.verify_p7()
        }
    
    def reset(self):
        """重置引擎"""
        self.narrative_history = []
        self.Lambda_history = []
        self.complexity_history = []
        self.change_cost_history = []


_instance = None

def get_instance() -> NarrativeActionEngine:
    """获取NarrativeActionEngine单例"""
    global _instance
    if _instance is None:
        _instance = NarrativeActionEngine()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M64 叙事作用量引擎 测试")
    print("=" * 60)
    
    engine = NarrativeActionEngine(alpha=0.6, beta=0.4)
    
    # 模拟内省过程（叙事作用量递减）
    narratives = [
        "今天遇到了一个非常困难的问题，感觉很焦虑和困惑，需要找到解决方案。",
        "问题似乎与系统架构有关，需要从更高的层面来理解。",
        "通过分析发现，核心问题其实是信息流的设计。",
        "理解了信息流的本质后，问题变得清晰了。",
        "找到了最优解，问题已经完全解决。",
    ]
    
    print("\n追踪叙事作用量衰减:")
    Lambda_values = engine.track_decay(narratives)
    
    for i, (n, l) in enumerate(zip(narratives, Lambda_values)):
        print(f"  叙事{i+1}: Λ={l:.4f} | {n[:20]}...")
    
    # 验证P7
    p7_result = engine.verify_p7()
    print(f"\nP7验证结果: {p7_result}")
    
    # 当前状态
    state = engine.get_state()
    print(f"\n引擎状态: {state}")
    
    print("\n" + "=" * 60)
    print("✅ M64 测试完成")
    print("=" * 60)
