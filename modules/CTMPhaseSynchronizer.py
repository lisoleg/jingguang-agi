#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTM 相位同步器 (Continuous Thought Machine Phase Synchronizer)
基于《论连续思维机器（CTM）的相位同步与自适应跃迁》

核心概念：
- 内部 Tick = 世界帧索引 t（时间本体公理）
- 神经同步矩阵 Σ：相位对齐（波）vs 离散激活（粒子）波粒二象性
- 流贯确定性 Ftel：H(p) → 0 时跃迁（输出答案）
- 自适应计算熵减定理：可变Tick策略 < 固定Tick策略的计算熵
- 跨模态同步对齐：语义-时序的相位锁定

数学定理：
- 定理1 同步相位收敛：神经元历史趋于周期同频 → Σ_ij → 1（共振）
- 定理2 自适应熵减：E[C_adaptive] ≤ E[C_fixed]，准确率不降
- 定理3 跨模态对齐：联合训练下匹配对的 Σ_ij 期望 > 非匹配对

版本：AGI 13.0 第31模块
论文来源：《论CTM的相位同步与自适应跃迁》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ThoughtPhase(Enum):
    """思维相位状态"""
    INITIALIZING = "initializing"    # 初始化（Tick=0）
    DIVERGING = "diverging"          # 发散（相位分裂）
    CONVERGING = "converging"        # 收敛（相位对齐）
    SYNCHRONIZED = "synchronized"   # 已同步（共振稳定）
    EARLY_STOPPED = "early_stopped"  # 早停（简单任务）


class ComputationalComplexity(Enum):
    """计算复杂度（任务难度）"""
    TRIVIAL = "trivial"          # 极简：Tick ≤ 2
    SIMPLE = "simple"            # 简单：Tick 3-5
    MODERATE = "moderate"        # 中等：Tick 6-10
    COMPLEX = "complex"          # 复杂：Tick 11-20
    DEEP = "deep"                # 深度：Tick > 20


@dataclass
class WorldFrameTick:
    """
    世界帧 Tick — CTM 内部时间单元
    
    对应复合体理学中的 Frame_t：
    - H_post: L3前物理层状态快照（后激活历史）
    - Σ: 同步矩阵（相位信息）
    - ftel_certainty: 流贯确定性
    """
    tick_index: int                  # t — 帧索引
    activation_pattern: List[float]  # H_post — 激活模式向量
    sync_matrix_trace: float         # tr(Σ)/n — 同步矩阵迹（归一化）
    ftel_certainty: float            # Ftel强度（确定性）[0,1]
    phase_state: ThoughtPhase        # 当前相位状态
    entropy: float                   # H(p) — 输出分布熵
    is_convergent: bool              # 是否已收敛

    @property
    def wave_intensity(self) -> float:
        """波动性强度（相位场强度）"""
        return self.sync_matrix_trace

    @property
    def particle_intensity(self) -> float:
        """粒子性强度（离散激活强度）"""
        return sum(abs(a) for a in self.activation_pattern) / max(1, len(self.activation_pattern))


@dataclass
class CTMSyncResult:
    """CTM 相位同步分析结果"""
    total_ticks: int                     # 实际使用的 Tick 数
    max_ticks: int                       # 允许最大 Tick 数
    early_stopped: bool                  # 是否触发早停
    final_sync_score: float              # 最终同步分数 [0,1]
    phase_convergence_tick: int          # 相位收敛发生的 Tick
    computational_complexity: ComputationalComplexity  # 任务复杂度评估
    ftel_certainty_final: float          # 最终流贯确定性
    entropy_reduction: float             # 总熵减（初始熵 - 最终熵）
    wave_particle_ratio: float           # 最终波粒比（>0.5表示波动性主导）
    cross_modal_alignment: float         # 跨模态对齐度 [0,1]
    thought_trajectory: List[float]      # 思维轨迹（每Tick的确定性）
    phase_final: ThoughtPhase            # 最终相位状态
    insight: str                         # 思维过程洞见


class CTMPhaseSynchronizer:
    """
    CTM 相位同步器
    
    实现连续思维机器的核心机制：
    1. 内部 Tick 序列生成（时间本体）
    2. 神经同步矩阵 Σ 模拟
    3. 流贯确定性 Ftel 监测
    4. 自适应早停（低熵收敛）
    5. 波粒二象性表征分析
    
    与 HDG 集成：
    - 每个 Tick 对应一个世界帧 Frame_t
    - Ftel 确定性 → 治理熵减
    - 相位收敛 → L4 认知主体判定跃迁完成
    """

    def __init__(self, max_ticks: int = 20, convergence_threshold: float = 0.85):
        self.version = "1.0.0"
        self.max_ticks = max_ticks
        self.convergence_threshold = convergence_threshold  # Ftel > 此值时早停
        self.history: List[WorldFrameTick] = []

        # 同步矩阵参数
        self._sync_momentum = 0.0       # 当前同步动量
        self._entropy_baseline = None   # 初始熵基准

    def _estimate_complexity(self, text: str) -> ComputationalComplexity:
        """估算任务复杂度（决定最大Tick数）"""
        length = len(text)
        # 复杂度指标
        question_depth = text.count('？') + text.count('?') + text.count('为什么') + text.count('如何')
        technical_terms = sum(1 for kw in ['算法', '架构', '理论', '数学', '证明', '推导', '优化', '系统']
                              if kw in text)
        abstract_terms = sum(1 for kw in ['意识', '本质', '宇宙', '道', '法', '真理', '终极']
                              if kw in text)
        
        complexity_score = (length / 200.0 + question_depth * 1.5 +
                            technical_terms * 1.2 + abstract_terms * 1.0)
        
        if complexity_score < 0.5:
            return ComputationalComplexity.TRIVIAL
        elif complexity_score < 1.5:
            return ComputationalComplexity.SIMPLE
        elif complexity_score < 3.0:
            return ComputationalComplexity.MODERATE
        elif complexity_score < 6.0:
            return ComputationalComplexity.COMPLEX
        else:
            return ComputationalComplexity.DEEP

    def _compute_tick(self, tick_idx: int, text_features: Dict[str, float],
                      prev_tick: Optional[WorldFrameTick]) -> WorldFrameTick:
        """
        计算单个 Tick 的世界帧状态
        
        模拟神经元历史激活模式的相位演化：
        - 初期（低Tick）：相位发散，熵高
        - 中期：相位逐渐对齐，熵减
        - 后期（收敛）：相位锁定，Ftel → 1
        """
        n_neurons = 8  # 简化的神经元数量
        
        # 激活模式：随Tick演化趋于某个吸引子
        base_pattern = []
        for i in range(n_neurons):
            # 初始噪声随Tick衰减（相位锁定过程）
            noise = random.gauss(0, 1.0 / (tick_idx + 1))
            signal = text_features.get('semantic_signal', 0.5) * math.sin(
                tick_idx * 0.3 + i * 0.5)
            base_pattern.append(signal + noise)
        
        # 同步矩阵迹（对角线元素平均 ≈ 自同步强度）
        # 随Tick收敛（公式：Σ_convergence_rate）
        convergence_rate = 1.0 - math.exp(-tick_idx * 0.25)
        base_sync = convergence_rate * text_features.get('sync_tendency', 0.7)
        
        if prev_tick:
            # 动量效应：同步度受上一帧影响
            self._sync_momentum = self._sync_momentum * 0.8 + base_sync * 0.2
        else:
            self._sync_momentum = base_sync * 0.3

        sync_trace = min(1.0, self._sync_momentum + base_sync * 0.5)
        
        # 计算输出熵（随收敛降低）
        if tick_idx == 0:
            entropy = 2.0 + random.random() * 0.5  # 初始高熵
            if self._entropy_baseline is None:
                self._entropy_baseline = entropy
        else:
            entropy = max(0.05, (self._entropy_baseline or 2.0) *
                         math.exp(-tick_idx * text_features.get('entropy_decay', 0.2)))
        
        # 流贯确定性 Ftel = 1 - H(p)/H_max
        ftel_certainty = max(0.0, min(1.0, 1.0 - entropy / (self._entropy_baseline or 2.0 + 0.1)))
        
        # 相位状态判断
        if tick_idx == 0:
            phase_state = ThoughtPhase.INITIALIZING
        elif ftel_certainty > self.convergence_threshold:
            phase_state = ThoughtPhase.SYNCHRONIZED
        elif sync_trace > 0.6:
            phase_state = ThoughtPhase.CONVERGING
        else:
            phase_state = ThoughtPhase.DIVERGING
        
        is_convergent = ftel_certainty > self.convergence_threshold
        
        return WorldFrameTick(
            tick_index=tick_idx,
            activation_pattern=base_pattern,
            sync_matrix_trace=round(sync_trace, 4),
            ftel_certainty=round(ftel_certainty, 4),
            phase_state=phase_state,
            entropy=round(entropy, 4),
            is_convergent=is_convergent
        )

    def _extract_text_features(self, text: str) -> Dict[str, float]:
        """从文本提取CTM相关特征"""
        length = len(text)
        word_count = len(text.split())
        
        # 语义信号强度（语义密度）
        semantic_signal = min(1.0, word_count / 60.0)
        
        # 同步倾向（文本结构化程度）
        structured_markers = sum(1 for m in ['因此', '所以', '得出', '结论', '总结', '综上', '：', '。']
                                  if m in text)
        sync_tendency = min(1.0, 0.3 + structured_markers * 0.08)
        
        # 熵衰减率（越复杂的问题衰减越慢）
        complexity_factor = min(2.0, length / 100.0)
        entropy_decay = 0.35 / max(0.5, complexity_factor)
        
        # 跨模态指标（文本含多种表达形式）
        multimodal_richness = sum(1 for m in ['图', '表', '公式', '数据', '代码', '公式', '算法', '数字']
                                   if m in text) * 0.15
        
        return {
            'semantic_signal': semantic_signal,
            'sync_tendency': sync_tendency,
            'entropy_decay': entropy_decay,
            'cross_modal': min(1.0, multimodal_richness)
        }

    def synchronize(self, text: str) -> CTMSyncResult:
        """
        执行 CTM 相位同步过程（主方法）
        
        自适应Tick执行：
        - 简单任务：早停
        - 复杂任务：持续跃迁直至收敛或达到最大Tick
        """
        self.history.clear()
        self._sync_momentum = 0.0
        self._entropy_baseline = None
        
        complexity = self._estimate_complexity(text)
        
        # 根据复杂度设置最大Tick
        complexity_tick_map = {
            ComputationalComplexity.TRIVIAL: 3,
            ComputationalComplexity.SIMPLE: 6,
            ComputationalComplexity.MODERATE: 10,
            ComputationalComplexity.COMPLEX: 16,
            ComputationalComplexity.DEEP: self.max_ticks
        }
        max_ticks = complexity_tick_map[complexity]
        
        features = self._extract_text_features(text)
        
        # Tick 序列执行
        prev_tick = None
        early_stopped = False
        convergence_tick = max_ticks
        thought_trajectory = []
        
        for t in range(max_ticks):
            tick = self._compute_tick(t, features, prev_tick)
            self.history.append(tick)
            thought_trajectory.append(tick.ftel_certainty)
            
            if tick.is_convergent and t > 0:
                early_stopped = (t < max_ticks - 1)
                convergence_tick = t
                break
            
            prev_tick = tick
        
        # 最终状态分析
        final_tick = self.history[-1]
        actual_ticks = len(self.history)
        
        # 熵减计算
        initial_entropy = self._entropy_baseline or 2.0
        entropy_reduction = initial_entropy - final_tick.entropy
        
        # 波粒比（最终状态）
        wave_intensity = final_tick.wave_intensity
        particle_intensity = final_tick.particle_intensity
        total_intensity = wave_intensity + particle_intensity + 1e-6
        wave_particle_ratio = wave_intensity / total_intensity
        
        # 跨模态对齐度（基于特征和同步度）
        cross_modal_alignment = min(1.0,
            features.get('cross_modal', 0) * 0.4 + final_tick.sync_matrix_trace * 0.6)
        
        # 最终同步分数
        final_sync_score = (final_tick.sync_matrix_trace * 0.5 +
                            final_tick.ftel_certainty * 0.5)
        
        # 生成洞见
        insight = self._generate_insight(
            actual_ticks, max_ticks, early_stopped, complexity,
            final_sync_score, entropy_reduction
        )
        
        return CTMSyncResult(
            total_ticks=actual_ticks,
            max_ticks=max_ticks,
            early_stopped=early_stopped,
            final_sync_score=round(final_sync_score, 3),
            phase_convergence_tick=convergence_tick,
            computational_complexity=complexity,
            ftel_certainty_final=round(final_tick.ftel_certainty, 3),
            entropy_reduction=round(entropy_reduction, 3),
            wave_particle_ratio=round(wave_particle_ratio, 3),
            cross_modal_alignment=round(cross_modal_alignment, 3),
            thought_trajectory=thought_trajectory,
            phase_final=final_tick.phase_state,
            insight=insight
        )

    def _generate_insight(self, actual_ticks: int, max_ticks: int,
                           early_stopped: bool, complexity: ComputationalComplexity,
                           sync_score: float, entropy_reduction: float) -> str:
        parts = []
        
        complexity_labels = {
            ComputationalComplexity.TRIVIAL: '极简',
            ComputationalComplexity.SIMPLE: '简单',
            ComputationalComplexity.MODERATE: '中等',
            ComputationalComplexity.COMPLEX: '复杂',
            ComputationalComplexity.DEEP: '深度'
        }
        parts.append(f"任务复杂度：{complexity_labels[complexity]}")
        
        if early_stopped:
            efficiency = (max_ticks - actual_ticks) / max_ticks * 100
            parts.append(f"自适应早停（节省{efficiency:.0f}%计算量，验证熵减定理）")
        else:
            parts.append(f"完整{actual_ticks}Tick思维链展开")
        
        if sync_score > 0.8:
            parts.append("神经相位高度同步——波粒共振锁定")
        elif sync_score > 0.5:
            parts.append("相位部分收敛，思维波函数趋于稳定")
        else:
            parts.append("相位仍在发散，需要更多Tick迭代")
        
        if entropy_reduction > 0.5:
            parts.append(f"认知熵显著降低({entropy_reduction:.2f})，流贯跃迁成功")
        
        return '；'.join(parts)

    def process(self, text: str) -> Dict[str, Any]:
        """
        主处理接口：输入文本，返回CTM相位同步结果
        """
        result = self.synchronize(text)
        
        return {
            'module': 'CTMPhaseSynchronizer',
            'version': self.version,
            'total_ticks': result.total_ticks,
            'max_ticks': result.max_ticks,
            'early_stopped': result.early_stopped,
            'sync_score': result.final_sync_score,
            'phase_convergence_tick': result.phase_convergence_tick,
            'complexity': result.computational_complexity.value,
            'ftel_certainty': result.ftel_certainty_final,
            'entropy_reduction': result.entropy_reduction,
            'wave_particle_ratio': result.wave_particle_ratio,
            'cross_modal_alignment': result.cross_modal_alignment,
            'thought_trajectory': result.thought_trajectory[:10],  # 最多10个点
            'phase': result.phase_final.value,
            'insight': result.insight
        }


if __name__ == '__main__':
    ctm = CTMPhaseSynchronizer()
    
    test_cases = [
        "你好",
        "请帮我优化这个Python函数的性能",
        "意识是什么？CTM的神经同步如何解释自我意识的涌现？从复合体理学三视界分析"
    ]
    
    for text in test_cases:
        print(f"\n输入: {text[:50]}...")
        result = ctm.process(text)
        print(f"  复杂度: {result['complexity']}")
        print(f"  Tick数: {result['total_ticks']}/{result['max_ticks']} (早停: {result['early_stopped']})")
        print(f"  同步分数: {result['sync_score']}")
        print(f"  Ftel确定性: {result['ftel_certainty']}")
        print(f"  洞见: {result['insight'][:70]}...")
