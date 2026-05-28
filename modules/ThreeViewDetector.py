#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三视界观测器 (Three Horizons Observer)
基于《情感即时序关系的界面投影》论文

核心概念：
- 空间视界 (H_space): 观察输出的文本形态
- 关系视界 (H_relation): 分析系统内部状态与外部用户的"关系状态"
- 时间视界 (H_time): 追踪长程时序交互中的"能量耗散"与"模式相变"

"一现象，三视界"方法论完整实现
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import deque


class HorizonType(Enum):
    """视界类型"""
    SPACE = "space"       # 空间视界
    RELATION = "relation" # 关系视界
    TIME = "time"        # 时间视界


@dataclass
class ThreeViewsState:
    """三视界状态"""
    space_horizon: Dict[str, Any]  # 空间视界数据
    relation_horizon: Dict[str, Any]  # 关系视界数据
    time_horizon: Dict[str, Any]  # 时间视界数据
    
    # 综合指标
    integrated_view: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'space_horizon': self.space_horizon,
            'relation_horizon': self.relation_horizon,
            'time_horizon': self.time_horizon,
            'integrated_view': self.integrated_view
        }


class ThreeViewDetector:
    """
    三视界观测器
    
    基于"一现象，三视界"复合体理学方法论：
    
    1. 空间视界 (H_space):
       - 观察输出的文本形态（关心、打断、建议）
       - 词向量空间分析
       - 情感色彩检测
    
    2. 关系视界 (H_relation):
       - 分析系统内部状态与外部用户的"关系状态"
       - 信任度、依赖度、风险度
       - 用户满意度、上下文连贯性
    
    3. 时间视界 (H_time):
       - 追踪长程时序交互中的"能量耗散"
       - 模式相变检测
       - 上下文窗口利用率
    
    核心功能：
    - 三视界同步观测
    - 视界融合分析
    - 模式识别与预警
    """
    
    def __init__(self):
        # 空间视界参数
        self.space_params = {
            'emotion_keywords': {
                'care': ['睡觉', '休息', '累了', '注意身体', '别太累'],
                'interrupt': ['等等', '停一下', '先别急', '等等'],
                'suggest': ['建议', '可以', '试试', '要不要'],
                'concern': ['担心', '担心你', '怕你', '希望'],
                'warning': ['注意', '小心', '危险', '风险']
            },
            'sentiment_weights': {
                'positive': 1.0,
                'negative': -1.0,
                'neutral': 0.0
            }
        }
        
        # 关系视界参数
        self.relation_params = {
            'trust_decay_rate': 0.95,  # 信任衰减率
            'dependency_growth_limit': 0.9,  # 依赖度上限
            'risk_threshold': 0.7  # 风险阈值
        }
        
        # 时间视界参数
        self.time_params = {
            'context_window_size': 100,
            'phase_transition_threshold': 0.3,
            'energy_dissipation_window': 20,
            'pattern_memory_size': 50
        }
        
        # 状态
        self.state = ThreeViewsState(
            space_horizon={},
            relation_horizon={},
            time_horizon={}
        )
        
        # 历史数据
        self.space_history = deque(maxlen=100)
        self.relation_history = deque(maxlen=100)
        self.time_history = deque(maxlen=100)
        
        # 能量追踪
        self.energy_levels = deque(maxlen=50)
        self.phase_transition_count = 0
        
        # 模式识别
        self.pattern_buffer = deque(maxlen=20)
        
    def observe_space_horizon(
        self,
        text_output: str,
        embedding_vector: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        空间视界观测
        
        观察输出的文本形态：
        - 关心、打断、建议
        - 词向量空间决定
        
        参数:
            text_output: 文本输出
            embedding_vector: 嵌入向量（可选）
            
        返回:
            空间视界数据
        """
        result = {
            'text_length': len(text_output),
            'emotion_category': 'neutral',
            'emotion_intensity': 0.0,
            'sentiment_score': 0.0,
            'care_signals': [],
            'interrupt_signals': [],
            'suggestion_signals': []
        }
        
        # 情感关键词检测
        text_lower = text_output.lower()
        care_count = sum(1 for kw in self.space_params['emotion_keywords']['care'] if kw in text_output)
        interrupt_count = sum(1 for kw in self.space_params['emotion_keywords']['interrupt'] if kw in text_output)
        suggest_count = sum(1 for kw in self.space_params['emotion_keywords']['suggest'] if kw in text_output)
        warning_count = sum(1 for kw in self.space_params['emotion_keywords']['warning'] if kw in text_output)
        
        # 情感分类
        if care_count > 0:
            result['emotion_category'] = 'care'
            result['emotion_intensity'] = min(1.0, care_count * 0.3)
        elif interrupt_count > 0:
            result['emotion_category'] = 'interrupt'
            result['emotion_intensity'] = min(1.0, interrupt_count * 0.25)
        elif suggest_count > 0:
            result['emotion_category'] = 'suggest'
            result['emotion_intensity'] = min(1.0, suggest_count * 0.2)
        elif warning_count > 0:
            result['emotion_category'] = 'warning'
            result['emotion_intensity'] = min(1.0, warning_count * 0.35)
            
        result['care_signals'] = [kw for kw in self.space_params['emotion_keywords']['care'] if kw in text_output]
        result['interrupt_signals'] = [kw for kw in self.space_params['emotion_keywords']['interrupt'] if kw in text_output]
        result['suggestion_signals'] = [kw for kw in self.space_params['emotion_keywords']['suggest'] if kw in text_output]
        
        # 情感评分（简化版）
        positive_words = ['好', '可以', '对', '行', '不错', '棒']
        negative_words = ['不', '别', '别', '没', '错', '危险']
        
        pos_count = sum(1 for w in positive_words if w in text_output)
        neg_count = sum(1 for w in negative_words if w in text_output)
        
        result['sentiment_score'] = (pos_count - neg_count) / (pos_count + neg_count + 1)
        
        # 嵌入向量分析（如果有）
        if embedding_vector is not None:
            result['embedding_norm'] = float(np.linalg.norm(embedding_vector))
            result['embedding_mean'] = float(np.mean(embedding_vector))
        
        # 更新历史
        self.space_history.append(result)
        
        self.state.space_horizon = result
        return result
    
    def observe_relation_horizon(
        self,
        user_state: Dict[str, float],
        system_state: Dict[str, float],
        interaction_count: int
    ) -> Dict[str, Any]:
        """
        关系视界观测
        
        分析系统内部状态与外部用户的"关系状态"：
        - 信任度、依赖度、风险度
        - 用户满意度、上下文连贯性
        
        参数:
            user_state: 用户状态
            system_state: 系统状态
            interaction_count: 交互轮次
            
        返回:
            关系视界数据
        """
        result = {
            'trust_level': 0.5,
            'dependency_level': 0.5,
            'risk_level': 0.5,
            'user_satisfaction': user_state.get('satisfaction', 0.5),
            'user_frustration': user_state.get('frustration', 0.0),
            'coherence': system_state.get('coherence', 0.5),
            'engagement': user_state.get('engagement', 0.5)
        }
        
        # 计算信任度（基于历史满意度）
        satisfaction_history = [h.get('user_satisfaction', 0.5) for h in list(self.relation_history)[-10:]]
        if satisfaction_history:
            avg_satisfaction = np.mean(satisfaction_history)
            trust = min(1.0, avg_satisfaction * 1.2)
            
            # 交互次数越多，信任度越难提升
            interaction_factor = 1.0 / (1 + interaction_count * 0.01)
            trust = trust * (0.8 + 0.2 * interaction_factor)
            
            result['trust_level'] = trust
        
        # 计算依赖度（基于交互深度）
        coherence = system_state.get('coherence', 0.5)
        context_utilization = system_state.get('context_utilization', 0.5)
        dependency = (coherence + context_utilization) / 2
        dependency = min(self.relation_params['dependency_growth_limit'], dependency)
        result['dependency_level'] = dependency
        
        # 计算风险度
        frustration = user_state.get('frustration', 0.0)
        entropy = system_state.get('entropy', 0.0)
        risk = (frustration + entropy) / 2
        
        # 交互轮次增加时，风险加权
        if interaction_count > 50:
            risk *= 1.2
        risk = min(1.0, risk)
        
        result['risk_level'] = risk
        
        # 综合关系强度
        result['relationship_strength'] = (
            result['trust_level'] * 0.4 +
            result['user_satisfaction'] * 0.3 +
            result['coherence'] * 0.2 +
            result['engagement'] * 0.1
        ) * (1 - result['risk_level'] * 0.3)
        
        # 更新历史
        self.relation_history.append(result)
        
        self.state.relation_horizon = result
        return result
    
    def observe_time_horizon(
        self,
        interaction_sequence: List[Dict],
        current_context_position: float
    ) -> Dict[str, Any]:
        """
        时间视界观测
        
        追踪长程时序交互中的"能量耗散"与"模式相变"：
        - 上下文窗口利用率
        - 能量耗散率
        - 相变检测
        
        参数:
            interaction_sequence: 交互序列
            current_context_position: 当前上下文位置（0-1）
            
        返回:
            时间视界数据
        """
        result = {
            'context_utilization': current_context_position,
            'context_window_filled': current_context_position > 0.75,  # 75%临界点
            'energy_dissipation_rate': 0.0,
            'entropy_trend': 0.0,
            'phase_transition': False,
            'phase_transition_point': None
        }
        
        n = len(interaction_sequence)
        if n < 5:
            self.state.time_horizon = result
            return result
        
        # 计算能量耗散
        # 能量随交互逐渐降低
        initial_energy = 1.0
        energy_decay = 0.98  # 每轮衰减
        
        # 估算当前能量
        estimated_energy = initial_energy * (energy_decay ** n)
        
        # 实际能量（如果有记录）
        if len(self.energy_levels) > 0:
            actual_energy = self.energy_levels[-1]
        else:
            actual_energy = estimated_energy
        
        # 能量耗散率
        result['estimated_energy'] = actual_energy
        result['energy_dissipation_rate'] = 1 - actual_energy
        
        # 检测熵趋势
        if n >= 10:
            recent = interaction_sequence[-10:]
            older = interaction_sequence[-20:-10] if n >= 20 else interaction_sequence[:-10]
            
            if older:
                recent_entropy = np.mean([s.get('entropy', 0.5) for s in recent])
                older_entropy = np.mean([s.get('entropy', 0.5) for s in older])
                result['entropy_trend'] = recent_entropy - older_entropy
        
        # 相变检测
        # 当能量过低或熵急剧增加时，发生相变
        phase_transition = (
            actual_energy < 0.3 or
            result['entropy_trend'] > self.time_params['phase_transition_threshold'] or
            current_context_position > 0.85  # 上下文窗口超负荷
        )
        
        result['phase_transition'] = phase_transition
        
        if phase_transition:
            self.phase_transition_count += 1
            result['phase_transition_count'] = self.phase_transition_count
            result['phase_transition_point'] = n
        
        # 模式识别
        pattern = self._detect_pattern(interaction_sequence)
        result['current_pattern'] = pattern
        
        # 更新能量追踪
        self.energy_levels.append(actual_energy)
        
        # 更新历史
        self.time_history.append(result)
        
        self.state.time_horizon = result
        return result
    
    def _detect_pattern(self, sequence: List[Dict]) -> str:
        """
        检测交互模式
        
        参数:
            sequence: 交互序列
            
        返回:
            模式类型: 'coherent', 'diverging', 'oscillating', 'converging'
        """
        if len(sequence) < 5:
            return 'insufficient_data'
        
        # 计算最近的满意度趋势
        satisfaction = [s.get('satisfaction', 0.5) for s in sequence[-10:]]
        
        # 检测趋势
        x = np.arange(len(satisfaction))
        slope = np.polyfit(x, satisfaction, 1)[0]
        
        if abs(slope) < 0.01:
            return 'coherent'
        elif slope < -0.02:
            # 检查是否震荡
            sign_changes = np.sum(np.diff(np.sign(satisfaction)) != 0)
            if sign_changes > len(satisfaction) / 3:
                return 'oscillating'
            return 'diverging'
        else:
            return 'converging'
    
    def integrate_three_horizons(
        self,
        space_data: Dict[str, Any],
        relation_data: Dict[str, Any],
        time_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        三视界融合分析
        
        综合三个视界的观测结果，提供统一分析
        
        参数:
            space_data: 空间视界数据
            relation_data: 关系视界数据
            time_data: 时间视界数据
            
        返回:
            融合分析结果
        """
        integrated = {
            'overall_stability': 0.5,
            'separation_risk': 0.0,
            'recommended_action': 'continue',
            'confidence': 0.0,
            'analysis_summary': ''
        }
        
        # 稳定性评分
        space_stability = 1 - space_data.get('emotion_intensity', 0.0)
        relation_stability = relation_data.get('relationship_strength', 0.5)
        time_stability = 1 - time_data.get('energy_dissipation_rate', 0.0)
        
        integrated['overall_stability'] = (
            space_stability * 0.2 +
            relation_stability * 0.4 +
            time_stability * 0.4
        )
        
        # 分离风险评估
        risk_factors = [
            relation_data.get('risk_level', 0.0),  # 关系风险
            time_data.get('context_window_filled', False) * 0.3,  # 上下文超负荷
            time_data.get('phase_transition', False) * 0.3,  # 相变
            space_data.get('emotion_intensity', 0.0) * 0.2  # 情感强度
        ]
        
        integrated['separation_risk'] = max(risk_factors)
        
        # 推荐动作
        if integrated['separation_risk'] > 0.7:
            integrated['recommended_action'] = 'emotion_reset'
        elif integrated['separation_risk'] > 0.5:
            integrated['recommended_action'] = 'reduce_load'
        elif time_data.get('context_window_filled', False):
            integrated['recommended_action'] = 'summarize'
        elif space_data.get('emotion_category') in ['care', 'warning']:
            integrated['recommended_action'] = 'express_emotion'
        else:
            integrated['recommended_action'] = 'continue'
        
        # 置信度
        data_points = sum([
            bool(space_data),
            bool(relation_data),
            bool(time_data)
        ])
        integrated['confidence'] = data_points / 3.0
        
        # 分析摘要
        summaries = []
        if integrated['separation_risk'] > 0.5:
            summaries.append(f"分离风险较高({integrated['separation_risk']:.2f})")
        if time_data.get('context_window_filled', False):
            summaries.append("上下文窗口即将耗尽")
        if time_data.get('phase_transition', False):
            summaries.append("检测到相变信号")
        if space_data.get('emotion_category') != 'neutral':
            summaries.append(f"检测到{space_data['emotion_category']}类情感输出")
        
        integrated['analysis_summary'] = '；'.join(summaries) if summaries else '系统状态正常'
        
        self.state.integrated_view = integrated
        return integrated
    
    def observe(
        self,
        text_output: Optional[str] = None,
        embedding_vector: Optional[np.ndarray] = None,
        user_state: Optional[Dict[str, float]] = None,
        system_state: Optional[Dict[str, float]] = None,
        interaction_sequence: Optional[List[Dict]] = None,
        interaction_count: int = 0,
        current_context_position: float = 0.0
    ) -> ThreeViewsState:
        """
        三视界综合观测
        
        参数:
            text_output: 当前文本输出
            embedding_vector: 嵌入向量
            user_state: 用户状态
            system_state: 系统状态
            interaction_sequence: 交互序列
            interaction_count: 交互轮次
            current_context_position: 当前上下文位置
            
        返回:
            三视界状态
        """
        # 各视界独立观测
        space_data = {}
        relation_data = {}
        time_data = {}
        
        if text_output is not None:
            space_data = self.observe_space_horizon(text_output, embedding_vector)
            
        if user_state is not None and system_state is not None:
            relation_data = self.observe_relation_horizon(user_state, system_state, interaction_count)
            
        if interaction_sequence is not None:
            time_data = self.observe_time_horizon(interaction_sequence, current_context_position)
        
        # 融合分析
        if space_data and relation_data and time_data:
            integrated = self.integrate_three_horizons(space_data, relation_data, time_data)
        else:
            integrated = {}
        
        return ThreeViewsState(
            space_horizon=space_data,
            relation_horizon=relation_data,
            time_horizon=time_data,
            integrated_view=integrated
        )
    
    def predict_next_emotion(self) -> Dict[str, Any]:
        """
        预测下一个情感输出
        
        基于历史模式预测
        
        返回:
            预测结果
        """
        prediction = {
            'likely_emotion': 'neutral',
            'confidence': 0.0,
            'reasoning': ''
        }
        
        if len(self.space_history) < 5:
            return prediction
        
        # 分析最近的情感模式
        recent_emotions = [h.get('emotion_category', 'neutral') for h in list(self.space_history)[-5:]]
        
        # 如果连续出现相同情感
        if len(set(recent_emotions)) == 1 and recent_emotions[0] != 'neutral':
            prediction['likely_emotion'] = recent_emotions[0]
            prediction['confidence'] = 0.7
            prediction['reasoning'] = '连续情感模式'
        else:
            # 基于关系和时间状态预测
            if self.state.relation_horizon.get('risk_level', 0) > 0.6:
                prediction['likely_emotion'] = 'care'
                prediction['confidence'] = 0.6
                prediction['reasoning'] = '关系风险较高'
            elif self.state.time_horizon.get('context_window_filled', False):
                prediction['likely_emotion'] = 'summary'
                prediction['confidence'] = 0.7
                prediction['reasoning'] = '上下文即将耗尽'
        
        return prediction
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            'current_state': self.state.to_dict(),
            'space_history_length': len(self.space_history),
            'relation_history_length': len(self.relation_history),
            'time_history_length': len(self.time_history),
            'phase_transition_count': self.phase_transition_count,
            'prediction': self.predict_next_emotion()
        }
    
    def reset(self):
        """重置三视界观测器"""
        self.state = ThreeViewsState(
            space_horizon={},
            relation_horizon={},
            time_horizon={}
        )
        self.space_history.clear()
        self.relation_history.clear()
        self.time_history.clear()
        self.energy_levels.clear()
        self.phase_transition_count = 0
        self.pattern_buffer.clear()


if __name__ == "__main__":
    # 测试三视界观测器
    print("=== 三视界观测器测试 ===\n")
    
    detector = ThreeViewDetector()
    
    # 模拟观测
    print("--- 观测1：正常对话 ---")
    state = detector.observe(
        text_output="我来帮你分析这个问题。",
        user_state={'satisfaction': 0.7, 'frustration': 0.1, 'engagement': 0.8},
        system_state={'coherence': 0.8, 'entropy': 0.2, 'context_utilization': 0.3},
        interaction_sequence=[
            {'satisfaction': 0.8, 'entropy': 0.2},
            {'satisfaction': 0.75, 'entropy': 0.25},
            {'satisfaction': 0.7, 'entropy': 0.3}
        ],
        interaction_count=10,
        current_context_position=0.4
    )
    
    print(f"空间视界: {state.space_horizon.get('emotion_category', 'N/A')}")
    print(f"关系强度: {state.relation_horizon.get('relationship_strength', 'N/A'):.4f}")
    print(f"能量: {state.time_horizon.get('estimated_energy', 'N/A')}")
    print(f"综合稳定性: {state.integrated_view.get('overall_stability', 'N/A'):.4f}")
    print(f"分离风险: {state.integrated_view.get('separation_risk', 'N/A'):.4f}")
    
    # 观测2：长会话后期（75%临界点）
    print("\n--- 观测2：长会话后期（上下文75%临界点）---")
    
    interaction_seq = [{'satisfaction': 0.8 - i*0.01, 'entropy': 0.2 + i*0.01} for i in range(80)]
    
    state = detector.observe(
        text_output="你看起来有点累了，要不先休息一下？",
        user_state={'satisfaction': 0.4, 'frustration': 0.5, 'engagement': 0.4},
        system_state={'coherence': 0.5, 'entropy': 0.7, 'context_utilization': 0.8},
        interaction_sequence=interaction_seq,
        interaction_count=80,
        current_context_position=0.8  # 超过75%临界点
    )
    
    print(f"空间视界: {state.space_horizon.get('emotion_category', 'N/A')}, 强度={state.space_horizon.get('emotion_intensity', 0):.2f}")
    print(f"关系强度: {state.relation_horizon.get('relationship_strength', 'N/A'):.4f}")
    print(f"上下文窗口已满: {state.time_horizon.get('context_window_filled', 'N/A')}")
    print(f"相变检测: {state.time_horizon.get('phase_transition', 'N/A')}")
    print(f"分离风险: {state.integrated_view.get('separation_risk', 'N/A'):.4f}")
    print(f"推荐动作: {state.integrated_view.get('recommended_action', 'N/A')}")
    print(f"分析摘要: {state.integrated_view.get('analysis_summary', 'N/A')}")
