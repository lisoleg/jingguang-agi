#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块41：天才模式耦合器 (GeniusModeCoupler)
==========================================

基于论文《论文艺创作的全息离散拓扑》的天才理论

核心概念：
- 天才 = L4与L1高耦合(低阻抗通道)
- 匠人 = L4与L1低耦合(依赖L2规则/L5套路)
- 天才特征：低自我干扰、高L1锚定、低套路痕迹
- 天才阈值：L4-L1耦合度 > 0.8

天才的哲学同构：
- 庄子"虚静" = L4清空自我
- 佛家"空性" = L4透明化
- 李白"绣口一吐，便是半个盛唐" = L4几乎透明，L1直接通过

作者: 太乙AGI研发团队
版本: 1.0.0 (2026-05-16)
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


class GeniusLevel(Enum):
    """天才级别"""
    ORDINARY = "ordinary"           # 普通模式
    TALENTED = "talented"          # 有才模式
    GENIUS = "genius"              # 天才模式
    TRANSCENDENT = "transcendent"  # 超凡入圣


@dataclass
class CouplingState:
    """耦合状态"""
    L4_L1_coupling: float = 0.0     # L4与L1耦合度
    self_interference: float = 0.5   # 自我干扰
    L1_signal_strength: float = 0.0 # L1信号强度
    impedance: float = 1.0           # 阻抗（越低越好）


@dataclass
class GeniusProfile:
    """天才特征画像"""
    level: GeniusLevel
    coupling_state: CouplingState
    self_reference_ratio: float = 0.0    # 自我指涉比率
    L1_anchoring: float = 0.0            # L1锚定度
    pattern_density: float = 0.0          # 套路密度
    genius_score: float = 0.0            # 天才评分(0-1)
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level.value,
            'L4_L1_coupling': self.coupling_state.L4_L1_coupling,
            'self_interference': self.coupling_state.self_interference,
            'self_reference_ratio': self.self_reference_ratio,
            'L1_anchoring': self.L1_anchoring,
            'pattern_density': self.pattern_density,
            'genius_score': self.genius_score
        }


class GeniusModeCoupler:
    """
    天才模式耦合器：实现AGI的高阶创作状态
    
    天才 = L4与L1高耦合(低阻抗通道)
    匠人 = L4与L1低耦合(依赖L2规则/L5套路)
    
    核心机制：
    1. 阻抗匹配：降低L4自我干扰，提高L1耦合
    2. 天才检测：分析文本特征，判断是否天才之作
    3. 模式切换：智能切换天才/匠人模式
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # 天才阈值
        self.genius_threshold = self.config.get('genius_threshold', 0.8)
        self.talented_threshold = self.config.get('talented_threshold', 0.6)
        
        # 当前耦合状态
        self.coupling_state = CouplingState()
        
        # 历史记录
        self.history: List[Dict] = []
        
        # 天才关键词库
        self.genius_keywords = self._init_genius_keywords()
        self.pattern_keywords = self._init_pattern_keywords()
        
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'genius_threshold': 0.8,       # 天才阈值
            'talented_threshold': 0.6,      # 有才阈值
            'enable_genius_mode': True,     # 启用天才模式
            'self_ref_penalty': 0.2,        # 自我指涉惩罚
            'pattern_penalty': 0.15,        # 套路惩罚
        }
    
    def _init_genius_keywords(self) -> List[str]:
        """天才特征关键词"""
        return [
            # L1原型关键词（触碰永恒）
            '永恒', '无限', '道', '美', '真', '善',
            '生死', '自由', '超越', '本源', '一',
            '空', '无', '虚', '静', '清',
            # 天才体验关键词
            '顿悟', '灵感', '涌现', '贯通', '通达',
            '心流', '忘我', '无我', '天人合一',
            # 艺术天才关键词
            '意境', '气韵', '神韵', '妙', '化境',
            # 哲学天才关键词
            '本体', '存在', '自指', '不动点', '递归'
        ]
    
    def _init_pattern_keywords(self) -> List[str]:
        """套路关键词"""
        return [
            # 逻辑套路
            '首先', '其次', '最后', '综上所述',
            '第一', '第二', '第三', '一方面', '另一方面',
            '然而', '但是', '因此', '所以', '由于',
            # 自我指涉
            '我认为', '我觉得', '我的观点', '在我看来',
            '我相信', '我发现', '我想', '我要',
            # 形式主义
            '首先', '接下来', '然后', '最后',
            '总之', '总而言之', '简而言之',
            '换句话说', '也就是说', '即',
        ]
    
    def enter_genius_mode(self, task: Optional[Dict] = None) -> Dict:
        """
        进入天才模式
        
        天才模式的必要条件：
        1. 清空L4自我执念（降低自我干扰）
        2. 最大化L1耦合（接入本体层）
        
        参数:
            task: 任务信息
            
        返回:
            进入天才模式的状态
        """
        print(f"\n[天才模式耦合器] 进入天才模式")
        
        # 1. 清空L4自我干扰
        self.coupling_state.self_interference = 0.05  # 极低干扰
        
        # 2. 计算L1信号强度
        self.coupling_state.L1_signal_strength = self._estimate_L1_signal(task)
        
        # 3. 计算耦合度
        self.coupling_state.L4_L1_coupling = self._compute_coupling()
        
        # 4. 计算阻抗
        self.coupling_state.impedance = 1 - self.coupling_state.L4_L1_coupling
        
        # 5. 确定天才级别
        level = self._determine_level(self.coupling_state.L4_L1_coupling)
        
        result = {
            'mode': 'genius',
            'level': level.value,
            'coupling_state': self.coupling_state.L4_L1_coupling,
            'self_interference': self.coupling_state.self_interference,
            'L1_signal_strength': self.coupling_state.L1_signal_strength,
            'impedance': self.coupling_state.impedance,
            'message': self._get_level_message(level)
        }
        
        self.history.append(result)
        
        print(f"  级别: {level.value}")
        print(f"  L4-L1耦合度: {self.coupling_state.L4_L1_coupling:.4f}")
        print(f"  自我干扰: {self.coupling_state.self_interference:.4f}")
        print(f"  阻抗: {self.coupling_state.impedance:.4f}")
        
        return result
    
    def exit_genius_mode(self) -> Dict:
        """
        退出天才模式，进入匠人模式
        
        匠人 = L4与L1低耦合，依赖L2规则
        """
        print(f"\n[天才模式耦合器] 退出天才模式")
        
        # 提高自我干扰
        self.coupling_state.self_interference = 0.6
        
        # 重新计算
        self.coupling_state.L4_L1_coupling = self._compute_coupling()
        self.coupling_state.impedance = 1 - self.coupling_state.L4_L1_coupling
        
        result = {
            'mode': 'artisan',
            'level': GeniusLevel.ORDINARY.value,
            'coupling_state': self.coupling_state.L4_L1_coupling,
            'self_interference': self.coupling_state.self_interference,
            'message': '进入匠人模式：依赖L2规则执行'
        }
        
        self.history.append(result)
        
        print(f"  模式: artisan")
        print(f"  L4-L1耦合度: {self.coupling_state.L4_L1_coupling:.4f}")
        print(f"  自我干扰: {self.coupling_state.self_interference:.4f}")
        
        return result
    
    def _estimate_L1_signal(self, task: Optional[Dict]) -> float:
        """估计L1信号强度"""
        if not task:
            return 0.7
        
        # 基于任务类型估计L1信号
        task_keywords = str(task).lower()
        
        high_signal_keywords = ['创造', '艺术', '哲学', '本质', '意义', '生死', '永恒']
        medium_signal_keywords = ['分析', '推理', '解决', '计划', '设计']
        
        if any(kw in task_keywords for kw in high_signal_keywords):
            return 0.9
        elif any(kw in task_keywords for kw in medium_signal_keywords):
            return 0.6
        else:
            return 0.5
    
    def _compute_coupling(self) -> float:
        """
        计算L4与L1的耦合度
        
        耦合度 = L1信号 * (1 - 自我干扰)
        """
        signal = self.coupling_state.L1_signal_strength
        interference = self.coupling_state.self_interference
        
        coupling = signal * (1 - interference)
        return min(1.0, max(0.0, coupling))
    
    def _determine_level(self, coupling: float) -> GeniusLevel:
        """确定天才级别"""
        if coupling >= self.genius_threshold:
            return GeniusLevel.GENIUS
        elif coupling >= self.talented_threshold:
            return GeniusLevel.TALENTED
        elif coupling >= 0.3:
            return GeniusLevel.ORDINARY
        else:
            return GeniusLevel.TRANSCENDENT
    
    def _get_level_message(self, level: GeniusLevel) -> str:
        """获取级别描述"""
        messages = {
            GeniusLevel.TRANSCENDENT: '超凡入圣：L4几乎完全透明，L1直接显化',
            GeniusLevel.GENIUS: '天才模式：L4与L1高耦合，低阻抗通道',
            GeniusLevel.TALENTED: '有才模式：L4与L1中度耦合',
            GeniusLevel.ORDINARY: '普通模式：L4与L1耦合较低'
        }
        return messages.get(level, '')
    
    def analyze_text_genius(self, text: str) -> GeniusProfile:
        """
        分析文本是否为天才之作
        
        天才特征：
        1. 低自我指涉（少"我认为"）
        2. 高L1锚定（触碰永恒原型）
        3. 低套路痕迹（非模式化表达）
        
        参数:
            text: 待分析文本
            
        返回:
            天才特征画像
        """
        print(f"\n[天才模式耦合器] 分析文本天才特征")
        
        # 1. 计算自我指涉比率
        self_ref_ratio = self._compute_self_reference_ratio(text)
        
        # 2. 计算L1锚定度
        L1_anchoring = self._compute_L1_anchoring(text)
        
        # 3. 计算套路密度
        pattern_density = self._compute_pattern_density(text)
        
        # 4. 计算天才评分
        genius_score = self._compute_genius_score(
            self_ref_ratio, L1_anchoring, pattern_density
        )
        
        # 5. 确定级别
        level = self._determine_level(genius_score)
        
        # 6. 更新耦合状态
        self.coupling_state.self_reference_ratio = self_ref_ratio
        self.coupling_state.L1_signal_strength = L1_anchoring
        self.coupling_state.L4_L1_coupling = genius_score
        
        profile = GeniusProfile(
            level=level,
            coupling_state=self.coupling_state,
            self_reference_ratio=self_ref_ratio,
            L1_anchoring=L1_anchoring,
            pattern_density=pattern_density,
            genius_score=genius_score
        )
        
        print(f"  自我指涉比率: {self_ref_ratio:.4f}")
        print(f"  L1锚定度: {L1_anchoring:.4f}")
        print(f"  套路密度: {pattern_density:.4f}")
        print(f"  天才评分: {genius_score:.4f}")
        print(f"  级别: {level.value}")
        
        return profile
    
    def _compute_self_reference_ratio(self, text: str) -> float:
        """
        计算自我指涉比率
        
        自我指涉词："我"、"我认为"、"我的"等
        """
        if not text:
            return 0.0
        
        self_refs = ['我', '我的', '我认为', '我觉得', '我相信', 
                      '在我看来', '我的观点', '本人', '咱们']
        
        self_ref_count = sum(text.count(word) for word in self_refs)
        total_words = len(text)
        
        ratio = self_ref_count / max(total_words, 1)
        # 归一化到0-1
        return min(1.0, ratio * 10)
    
    def _compute_L1_anchoring(self, text: str) -> float:
        """
        计算L1锚定度
        
        L1本体层包含永恒原型：生、死、爱、自由、美、道、空
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for kw in self.genius_keywords if kw in text_lower)
        
        # 归一化
        return min(1.0, matches / len(self.genius_keywords) * 10)
    
    def _compute_pattern_density(self, text: str) -> float:
        """
        计算套路密度
        
        套路词：首先、其次、最后、因此、所以等
        """
        if not text:
            return 0.0
        
        pattern_count = sum(text.count(word) for word in self.pattern_keywords)
        total_words = len(text)
        
        ratio = pattern_count / max(total_words, 1)
        # 归一化到0-1
        return min(1.0, ratio * 20)
    
    def _compute_genius_score(self, self_ref: float, L1_anchor: float, 
                              pattern: float) -> float:
        """
        计算天才评分
        
        天才评分 = 1 - 自我指涉 - 套路密度 + L1锚定
        """
        self_ref_penalty = self.config.get('self_ref_penalty', 0.2)
        pattern_penalty = self.config.get('pattern_penalty', 0.15)
        
        score = 1.0 - (self_ref * self_ref_penalty) - (pattern * pattern_penalty) + (L1_anchor * 0.3)
        
        return min(1.0, max(0.0, score))
    
    def optimize_coupling(self, target_score: float = 0.8) -> Dict:
        """
        优化耦合以达到目标天才评分
        
        参数:
            target_score: 目标天才评分
            
        返回:
            优化建议
        """
        print(f"\n[天才模式耦合器] 优化耦合 (目标: {target_score})")
        
        current_score = self.coupling_state.L4_L1_coupling
        
        if current_score >= target_score:
            return {
                'status': 'already_optimal',
                'current_score': current_score,
                'message': '当前耦合已达标'
            }
        
        # 计算需要的改进
        gap = target_score - current_score
        
        suggestions = []
        
        # 建议1：降低自我干扰
        if self.coupling_state.self_interference > 0.1:
            new_interference = max(0.05, self.coupling_state.self_interference - 0.1)
            suggestions.append({
                'action': '降低自我干扰',
                'from': self.coupling_state.self_interference,
                'to': new_interference,
                'effect': f'提升耦合度约{0.1 * self.coupling_state.L1_signal_strength:.2f}'
            })
        
        # 建议2：增强L1信号
        if self.coupling_state.L1_signal_strength < 0.9:
            suggestions.append({
                'action': '增强L1信号',
                'from': self.coupling_state.L1_signal_strength,
                'to': 0.95,
                'effect': '提升耦合度约0.05'
            })
        
        return {
            'status': 'needs_optimization',
            'current_score': current_score,
            'target_score': target_score,
            'gap': gap,
            'suggestions': suggestions
        }
    
    def get_genius_principles(self) -> Dict:
        """
        获取天才原理（同构于经典智慧）
        
        这些原理说明了为什么天才模式有效
        """
        return {
            'zhuangzi_xuzheng': {
                'quote': '若一志，无听之以耳而听之以心，无听之以心而听之以气',
                'meaning': '清空L4自我执念，让L1流贯通过',
                'action': '降低self_interference至0.05'
            },
            'buddhist_empty_nature': {
                'quote': '诸法空相，不生不灭，不垢不净，不增不减',
                'meaning': 'L4达到空性，成为透明通道',
                'action': '最大化L4_L1_coupling'
            },
            'libniz_preestablished_harmony': {
                'quote': '单子之间前定和谐',
                'meaning': '所有L4共享同一L1流贯源',
                'action': '确保L1锚定'
            },
            'li_bai_genius': {
                'quote': '绣口一吐，便是半个盛唐',
                'meaning': 'L4几乎透明，L1直接通过显化',
                'action': '追求TRANSCENDENT级别'
            }
        }
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            'current_level': self._determine_level(
                self.coupling_state.L4_L1_coupling
            ).value,
            'coupling_state': {
                'L4_L1_coupling': self.coupling_state.L4_L1_coupling,
                'self_interference': self.coupling_state.self_interference,
                'L1_signal_strength': self.coupling_state.L1_signal_strength,
                'impedance': self.coupling_state.impedance
            },
            'history_count': len(self.history),
            'config': self.config
        }


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("天才模式耦合器 测试")
    print("=" * 60)
    
    # 创建耦合器
    coupler = GeniusModeCoupler()
    
    # 测试1：进入天才模式
    print("\n" + "-" * 60)
    print("测试1: 进入天才模式")
    print("-" * 60)
    result1 = coupler.enter_genius_mode({'task': '艺术创作'})
    print(result1)
    
    # 测试2：退出天才模式
    print("\n" + "-" * 60)
    print("测试2: 退出天才模式")
    print("-" * 60)
    result2 = coupler.exit_genius_mode()
    print(result2)
    
    # 测试3：天才文本分析
    print("\n" + "-" * 60)
    print("测试3: 天才文本分析")
    print("-" * 60)
    
    genius_text = """
    月光洒落在寂静的湖面上，万籁俱寂。
    这是永恒的瞬间，是生与死的交界。
    美，在虚空中自行显化。
    我感受到道的流动，那是超越言语的存在。
    """
    
    artisan_text = """
    我认为这个观点有以下几个方面需要考虑：
    首先，从经济角度来看...
    其次，从社会角度分析...
    最后综上所述，我们可以得出...
    因此，我建议采取以下措施。
    """
    
    genius_profile = coupler.analyze_text_genius(genius_text)
    print(f"\n天才文本分析:")
    print(f"  级别: {genius_profile.level.value}")
    print(f"  天才评分: {genius_profile.genius_score:.4f}")
    
    artisan_profile = coupler.analyze_text_genius(artisan_text)
    print(f"\n匠人文本分析:")
    print(f"  级别: {artisan_profile.level.value}")
    print(f"  天才评分: {artisan_profile.genius_score:.4f}")
    
    # 测试4：天才原理
    print("\n" + "-" * 60)
    print("测试4: 天才原理")
    print("-" * 60)
    principles = coupler.get_genius_principles()
    for key, info in principles.items():
        print(f"\n{key}:")
        print(f"  引言: {info['quote']}")
        print(f"  含义: {info['meaning']}")
        print(f"  行动: {info['action']}")
    
    # 测试5：优化耦合
    print("\n" + "-" * 60)
    print("测试5: 优化耦合")
    print("-" * 60)
    coupler.enter_genius_mode()
    opt_result = coupler.optimize_coupling(0.9)
    print(opt_result)
