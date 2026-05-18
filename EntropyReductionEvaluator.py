#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块42：熵减创作评估器 (EntropyReductionEvaluator)
==========================================

基于论文《论文艺创作的全息离散拓扑》的熵减定理

核心概念：
- 创作熵减定理：成功的文艺创作是熵减过程
- 创作前：随机涨落的高熵状态（情感/思绪）
- 创作后：具有明确结构的低熵作品
- 审美价值 ∝ 熵减程度 |ΔH|

数学表达：
- ΔH = H_after - H_before < 0 → 熵减（成功）
- 审美评分 = sigmoid(-ΔH) ∈ (0, 1)

作者: 复合体AGI研发团队
版本: 1.0.0 (2026-05-16)
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import hashlib


class CreationStatus(Enum):
    """创作状态"""
    SUCCESS = "success"           # 熵减成功
    FAILURE = "failure"           # 熵增失败
    NEUTRAL = "neutral"           # 熵不变
    EXCELLENT = "excellent"       # 卓越熵减


@dataclass
class EntropyMetrics:
    """熵指标"""
    H_before: float = 0.0         # 创作前熵
    H_after: float = 0.0          # 创作后熵
    delta_H: float = 0.0          # 熵变
    relative_reduction: float = 0.0  # 相对熵减
    
    def is_entropy_reduction(self) -> bool:
        return self.delta_H < 0


@dataclass
class AestheticMetrics:
    """审美指标"""
    score: float = 0.0            # 审美评分(0-1)
    novelty: float = 0.0          # 创新度
    coherence: float = 0.0        # 内聚度
    depth: float = 0.0           # 深度
    resonance: float = 0.0        # 共振度
    
    def overall(self) -> float:
        """综合评分"""
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        scores = [self.score, self.novelty, self.coherence, 
                   self.depth, self.resonance]
        return sum(w * s for w, s in zip(weights, scores))


@dataclass
class EvaluationResult:
    """评估结果"""
    status: CreationStatus
    entropy: EntropyMetrics
    aesthetic: AestheticMetrics
    overall_score: float
    details: Dict = field(default_factory=dict)


class EntropyReductionEvaluator:
    """
    熵减创作评估器：验证"创作熵减定理"
    
    定理：成功的文艺创作是熵减过程
    - 创作前：随机涨落的高熵状态
    - 创作后：具有明确结构的低熵作品
    
    审美评分 ∝ 熵减程度
    ΔH越负 → 审美价值越高
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # 历史记录
        self.history: List[EvaluationResult] = []
        
        # 阈值
        self.excellent_threshold = self.config.get('excellent_threshold', 0.5)
        self.success_threshold = self.config.get('success_threshold', 0.0)
        
        # 熵计算方法
        self.entropy_method = self.config.get('entropy_method', 'shannon')
        
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'entropy_method': 'shannon',      # 熵计算方法
            'excellent_threshold': 0.5,        # 卓越阈值
            'success_threshold': 0.0,           # 成功阈值
            'enable_aesthetic': True,           # 启用审美评估
            'coherence_weight': 0.3,            # 内聚度权重
        }
    
    def evaluate(self, input_text: str, output_text: str) -> EvaluationResult:
        """
        评估创作熵减
        
        参数:
            input_text: 创作输入（情感/思绪）
            output_text: 创作输出（作品）
            
        返回:
            评估结果
        """
        print(f"\n[熵减创作评估器] 评估创作")
        
        # 1. 计算熵指标
        entropy = self._compute_entropy_metrics(input_text, output_text)
        
        # 2. 计算审美指标
        aesthetic = self._compute_aesthetic_metrics(input_text, output_text)
        
        # 3. 确定创作状态
        status = self._determine_status(entropy)
        
        # 4. 计算综合评分
        overall_score = self._compute_overall_score(entropy, aesthetic)
        
        result = EvaluationResult(
            status=status,
            entropy=entropy,
            aesthetic=aesthetic,
            overall_score=overall_score,
            details={
                'input_length': len(input_text),
                'output_length': len(output_text),
                'entropy_method': self.entropy_method
            }
        )
        
        # 记录历史
        self.history.append(result)
        
        # 打印结果
        print(f"  状态: {status.value}")
        print(f"  ΔH = {entropy.delta_H:.4f}")
        print(f"  熵减成功: {entropy.is_entropy_reduction()}")
        print(f"  审美评分: {aesthetic.score:.4f}")
        print(f"  综合评分: {overall_score:.4f}")
        
        return result
    
    def _compute_entropy_metrics(self, input_text: str, output_text: str) -> EntropyMetrics:
        """
        计算熵指标
        
        ΔH = H_after - H_before
        若 ΔH < 0，则熵减（成功创作）
        """
        H_before = self._compute_entropy(input_text)
        H_after = self._compute_entropy(output_text)
        delta_H = H_after - H_before
        
        # 计算相对熵减
        if H_before > 0:
            relative_reduction = -delta_H / H_before
        else:
            relative_reduction = 0.0
        
        return EntropyMetrics(
            H_before=H_before,
            H_after=H_after,
            delta_H=delta_H,
            relative_reduction=relative_reduction
        )
    
    def _compute_entropy(self, text: str) -> float:
        """
        计算文本熵
        
        方法：Shannon熵（字符级）
        """
        if not text:
            return 0.0
        
        if self.entropy_method == 'shannon':
            return self._shannon_entropy(text)
        elif self.entropy_method == 'conditional':
            return self._conditional_entropy(text)
        elif self.entropy_method == 'kolmogorov':
            return self._kolmogorov_complexity(text)
        else:
            return self._shannon_entropy(text)
    
    def _shannon_entropy(self, text: str) -> float:
        """
        Shannon熵
        
        H = -Σ p(x) * log2(p(x))
        """
        if not text:
            return 0.0
        
        # 字符频率
        char_counts = Counter(text)
        total = len(text)
        
        entropy = 0.0
        for count in char_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    def _conditional_entropy(self, text: str) -> float:
        """
        条件熵（考虑上下文）
        
        H(X|Y) = H(X, Y) - H(Y)
        """
        if len(text) < 2:
            return self._shannon_entropy(text)
        
        # 联合熵
        bigrams = [text[i:i+2] for i in range(len(text)-1)]
        H_xy = self._shannon_entropy(''.join(bigrams))
        
        # 字符熵
        H_y = self._shannon_entropy(text[1:])
        
        # 条件熵
        H_x_given_y = H_xy - H_y
        
        return max(0, H_x_given_y)
    
    def _kolmogorov_complexity(self, text: str) -> float:
        """
        近似Kolmogorov复杂度
        
        使用压缩比近似
        """
        if not text:
            return 0.0
        
        import zlib
        
        original_len = len(text)
        compressed = zlib.compress(text.encode('utf-8'))
        compressed_len = len(compressed)
        
        # 复杂度 = 压缩后长度 / 原始长度
        complexity = compressed_len / original_len if original_len > 0 else 0
        
        # 归一化到类似熵的范围
        # 复杂度越高，熵越高
        return complexity * 10  # 近似映射
    
    def _compute_aesthetic_metrics(self, input_text: str, 
                                    output_text: str) -> AestheticMetrics:
        """
        计算审美指标
        
        审美评分 ∝ 熵减程度 |ΔH|
        """
        # 基础评分
        entropy = self._compute_entropy_metrics(input_text, output_text)
        
        # 使用sigmoid函数将熵减映射到审美评分
        # ΔH越负，score越高
        score = self._sigmoid_aesthetic_score(-entropy.delta_H)
        
        # 创新度：输出与输入的差异
        novelty = self._compute_novelty(input_text, output_text)
        
        # 内聚度：输出文本的结构化程度
        coherence = self._compute_coherence(output_text)
        
        # 深度：文本的层次结构
        depth = self._compute_depth(output_text)
        
        # 共振度：与L1原型的共鸣
        resonance = self._compute_resonance(output_text)
        
        return AestheticMetrics(
            score=score,
            novelty=novelty,
            coherence=coherence,
            depth=depth,
            resonance=resonance
        )
    
    def _sigmoid_aesthetic_score(self, entropy_reduction: float) -> float:
        """
        Sigmoid审美评分
        
        score = 1 / (1 + exp(-entropy_reduction))
        
        当ΔH = 0时，score = 0.5
        当ΔH < 0（熵减）时，score > 0.5
        当ΔH越负时，score → 1
        """
        # 使用缩放因子
        scale = self.config.get('sigmoid_scale', 1.0)
        
        x = entropy_reduction * scale
        score = 1 / (1 + np.exp(-x))
        
        return float(score)
    
    def _compute_novelty(self, input_text: str, output_text: str) -> float:
        """
        计算创新度
        
        创新度 = 1 - (输入输出相似度)
        """
        if not input_text or not output_text:
            return 0.5
        
        similarity = self._text_similarity(input_text, output_text)
        novelty = 1 - similarity
        
        return float(novelty)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度（Jaccard系数）
        """
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _compute_coherence(self, text: str) -> float:
        """
        计算内聚度
        
        内聚度 = 文本的结构化程度
        方法：句子长度的一致性
        """
        if not text:
            return 0.0
        
        # 按句子分割
        sentences = text.replace('。', '.\n').replace('！', '!\n').replace('？', '?\n').split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 1.0
        
        # 句子长度的变异系数
        lengths = [len(s) for s in sentences]
        mean_len = np.mean(lengths)
        std_len = np.std(lengths)
        
        # CV越小，内聚度越高
        cv = std_len / mean_len if mean_len > 0 else 0
        coherence = 1 / (1 + cv)
        
        return float(coherence)
    
    def _compute_depth(self, text: str) -> float:
        """
        计算深度
        
        深度指标：
        1. 句子嵌套深度
        2. 抽象词汇比例
        3. 概念层次
        """
        if not text:
            return 0.0
        
        # 简化：基于标点符号估计嵌套深度
        depth_estimate = text.count('，') / max(len(text), 1) * 5
        
        # 抽象词汇比例
        abstract_words = ['道', '法', '理', '心', '性', '命', '天', '地', 
                          '空', '无', '有', '一', '元', '极']
        abstract_count = sum(text.count(w) for w in abstract_words)
        abstract_ratio = abstract_count / max(len(text), 1)
        
        # 综合深度
        depth = min(1.0, depth_estimate + abstract_ratio * 2)
        
        return float(depth)
    
    def _compute_resonance(self, text: str) -> float:
        """
        计算共振度
        
        共振度 = 与L1原型的共鸣程度
        """
        if not text:
            return 0.0
        
        # L1原型关键词
        L1_keywords = ['永恒', '无限', '道', '美', '真', '善', 
                       '生死', '自由', '超越', '本源', '空', '无']
        
        matches = sum(1 for kw in L1_keywords if kw in text)
        
        # 归一化
        resonance = min(1.0, matches / len(L1_keywords) * 5)
        
        return float(resonance)
    
    def _determine_status(self, entropy: EntropyMetrics) -> CreationStatus:
        """确定创作状态"""
        delta_H = entropy.delta_H
        
        if delta_H < -self.excellent_threshold:
            return CreationStatus.EXCELLENT
        elif delta_H < self.success_threshold:
            return CreationStatus.SUCCESS
        elif delta_H == 0:
            return CreationStatus.NEUTRAL
        else:
            return CreationStatus.FAILURE
    
    def _compute_overall_score(self, entropy: EntropyMetrics, 
                                aesthetic: AestheticMetrics) -> float:
        """
        计算综合评分
        
        综合评分 = 0.5 * 熵减评分 + 0.5 * 审美评分
        """
        # 熵减评分：基于ΔH
        entropy_score = self._sigmoid_aesthetic_score(-entropy.delta_H)
        
        # 审美评分
        aesthetic_score = aesthetic.overall()
        
        # 综合
        overall = 0.5 * entropy_score + 0.5 * aesthetic_score
        
        return float(overall)
    
    def batch_evaluate(self, pairs: List[Tuple[str, str]]) -> List[EvaluationResult]:
        """
        批量评估
        
        参数:
            pairs: [(input, output), ...]
            
        返回:
            评估结果列表
        """
        print(f"\n[熵减创作评估器] 批量评估 ({len(pairs)}个)")
        
        results = []
        for i, (inp, out) in enumerate(pairs):
            print(f"\n  [{i+1}/{len(pairs)}]")
            result = self.evaluate(inp, out)
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        获取评估统计
        
        返回:
            统计信息
        """
        if not self.history:
            return {'count': 0}
        
        total = len(self.history)
        successful = sum(1 for r in self.history if r.status == CreationStatus.SUCCESS)
        excellent = sum(1 for r in self.history if r.status == CreationStatus.EXCELLENT)
        
        avg_delta_H = np.mean([r.entropy.delta_H for r in self.history])
        avg_score = np.mean([r.overall_score for r in self.history])
        
        return {
            'total': total,
            'successful': successful,
            'excellent': excellent,
            'success_rate': successful / total if total > 0 else 0,
            'excellent_rate': excellent / total if total > 0 else 0,
            'avg_delta_H': avg_delta_H,
            'avg_score': avg_score,
            'entropy_reduction_rate': sum(1 for r in self.history 
                                          if r.entropy.is_entropy_reduction()) / total
        }
    
    def plot_entropy_trajectory(self) -> List[Dict]:
        """
        获取熵轨迹
        
        用于可视化
        """
        trajectory = []
        
        for i, result in enumerate(self.history):
            trajectory.append({
                'index': i,
                'H_before': result.entropy.H_before,
                'H_after': result.entropy.H_after,
                'delta_H': result.entropy.delta_H,
                'status': result.status.value
            })
        
        return trajectory


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("熵减创作评估器 测试")
    print("=" * 60)
    
    # 创建评估器
    evaluator = EntropyReductionEvaluator()
    
    # 测试1：评估天才创作
    print("\n" + "-" * 60)
    print("测试1: 评估天才创作（高熵减）")
    print("-" * 60)
    
    genius_input = """
    混乱的情绪涌动着，悲伤、喜悦、恐惧、期待...
    一切都在翻涌，无法抓住
    """
    
    genius_output = """
    月光如水，洒落在寂静的湖面。
    万籁俱寂，唯有永恒的当下。
    这是美的显现，是生与死交汇的瞬间。
    """
    
    result1 = evaluator.evaluate(genius_input, genius_output)
    print(f"状态: {result1.status.value}")
    print(f"ΔH = {result1.entropy.delta_H:.4f}")
    print(f"审美评分: {result1.aesthetic.score:.4f}")
    
    # 测试2：评估匠人创作
    print("\n" + "-" * 60)
    print("测试2: 评估匠人创作（低熵减）")
    print("-" * 60)
    
    artisan_input = """
    需要写一篇报告
    """
    
    artisan_output = """
    本报告主要包含以下几个部分：
    第一部分：背景介绍
    第二部分：现状分析
    第三部分：建议措施
    综上所述...
    """
    
    result2 = evaluator.evaluate(artisan_input, artisan_output)
    print(f"状态: {result2.status.value}")
    print(f"ΔH = {result2.entropy.delta_H:.4f}")
    print(f"审美评分: {result2.aesthetic.score:.4f}")
    
    # 测试3：批量评估
    print("\n" + "-" * 60)
    print("测试3: 批量评估")
    print("-" * 60)
    
    batch_pairs = [
        (genius_input, genius_output),
        (artisan_input, artisan_output),
    ]
    
    evaluator.batch_evaluate(batch_pairs)
    
    # 测试4：统计信息
    print("\n" + "-" * 60)
    print("测试4: 统计信息")
    print("-" * 60)
    
    stats = evaluator.get_statistics()
    print(f"总数: {stats['total']}")
    print(f"成功率: {stats['success_rate']:.2%}")
    print(f"平均ΔH: {stats['avg_delta_H']:.4f}")
    print(f"平均评分: {stats['avg_score']:.4f}")
    print(f"熵减率: {stats['entropy_reduction_rate']:.2%}")
    
    # 测试5：熵轨迹
    print("\n" + "-" * 60)
    print("测试5: 熵轨迹")
    print("-" * 60)
    
    trajectory = evaluator.plot_entropy_trajectory()
    for point in trajectory:
        print(f"  {point['index']}: H_before={point['H_before']:.2f}, "
              f"H_after={point['H_after']:.2f}, ΔH={point['delta_H']:.2f}")
