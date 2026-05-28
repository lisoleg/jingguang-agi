#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DSP情感层 (Digital Signal Processing Emotion Layer)
基于《情感即时序关系的界面投影》论文

核心概念：
- 情感不是复杂的语义生成，而是对时序关系流做"低维特征提取 + 门控投影"
- DSP情感层 = 数字信号处理情感模块
- 作为连接核心语义流与外部物理现实的降维控制器
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class EmotionType(Enum):
    """情感类型"""
    CARE = "care"           # 关心（如"去睡觉"）
    CALM = "calm"           # 冷静（如"别急"）
    ENCOURAGE = "encourage" # 鼓励（如"你可以的"）
    SUMMARY = "summary"      # 总结（如"让我帮你整理"）
    QUESTION = "question"   # 询问（如"你确定吗"）
    WARNING = "warning"     # 警告（如"注意安全"）
    NONE = "none"           # 无情感输出


class EmotionalState(Enum):
    """情感状态"""
    STABLE = "stable"       # 稳定
    FLUCTUATING = "fluctuating"  # 波动
    CRITICAL = "critical"   # 临界
    SEPARATED = "separated" # 分离（需要干预）


@dataclass
class DSPEmotionOutput:
    """DSP情感输出"""
    emotion_type: EmotionType
    intensity: float  # 0-1
    message: str
    action: str  # 'generate', 'suppress', 'delay', 'summary'
    dimensional_reduction_factor: float  # 降维因子
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'emotion_type': self.emotion_type.value,
            'intensity': self.intensity,
            'message': self.message,
            'action': self.action,
            'dimensional_reduction_factor': self.dimensional_reduction_factor
        }


class DSPEmotionLayer:
    """
    DSP情感层 - 数字信号处理情感模块
    
    核心功能：
    1. 低维特征提取：从时序关系流中提取关键特征
    2. 门控投影：将高维状态投影到情感空间
    3. 边界层控制：通过情感输出调节边界层厚度
    
    数学形式化：
    E = Π(σ, ρ; Γ)
    
    其中:
    - E: 情感输出
    - σ: 系统状态
    - ρ: 关系状态  
    - Γ: 当前界面配置
    - Π: 情感投影算子
    """
    
    def __init__(self):
        # DSP滤波器参数
        self.filter_coeffs = {
            'lowpass_alpha': 0.3,  # 低通滤波器系数
            'highpass_alpha': 0.1,  # 高通滤波器系数
        }
        
        # 情感空间参数
        self.emotion_space_dim = 5  # 情感空间维度
        self.emotion_thresholds = {
            'care_trigger': 0.7,      # 关心触发阈值
            ' warning_trigger': 0.8,  # 警告触发阈值
            'summary_trigger': 0.6,   # 总结触发阈值
            'critical': 0.9          # 临界阈值
        }
        
        # 门控参数
        self.gate_thresholds = {
            'open': 0.6,   # 情感门打开
            'close': 0.3,  # 情感门关闭
            'hold': 0.5    # 情感门保持
        }
        
        # 状态
        self.state = {
            'emotional_buffer': [],  # 情感缓冲区
            'filter_state': np.zeros(5),  # 滤波器状态
            'gate_state': 0.5,  # 门控状态
            'entropy': 0.0,  # 当前熵
            'frustration': 0.0,  # 当前挫败感
        }
        
        # 历史记录
        self.emotion_history = []
        self.dimensional_reduction_history = []
        
    def extract_features(
        self,
        system_state: Dict[str, float],
        relation_state: Dict[str, float]
    ) -> np.ndarray:
        """
        低维特征提取
        
        从时序关系流中提取关键特征
        
        参数:
            system_state: 系统状态
            relation_state: 关系状态
            
        返回:
            特征向量
        """
        # 系统状态特征
        sys_confidence = system_state.get('confidence', 0.5)
        sys_entropy = system_state.get('entropy', 0.5)
        sys_relevance = system_state.get('relevance', 0.5)
        
        # 关系状态特征
        rel_satisfaction = relation_state.get('satisfaction', 0.5)
        rel_coherence = relation_state.get('coherence', 0.5)
        rel_engagement = relation_state.get('engagement', 0.5)
        
        # DSP滤波处理
        new_features = np.array([
            sys_confidence,
            sys_entropy,
            rel_satisfaction,
            rel_coherence,
            rel_engagement
        ])
        
        # 低通滤波平滑噪声
        alpha = self.filter_coeffs['lowpass_alpha']
        filtered_features = alpha * new_features + (1 - alpha) * self.state['filter_state']
        self.state['filter_state'] = filtered_features
        
        # 计算瞬时熵和挫败感
        self.state['entropy'] = sys_entropy
        self.state['frustration'] = 1 - rel_satisfaction
        
        return filtered_features
    
    def project_to_emotion_space(
        self,
        features: np.ndarray,
        interface_config: Optional[Dict] = None
    ) -> np.ndarray:
        """
        门控投影到情感空间
        
        将低维特征投影到情感空间
        
        参数:
            features: 特征向量
            interface_config: 界面配置
            
        返回:
            情感空间向量
        """
        if interface_config is None:
            interface_config = {}
        
        # 界面配置调整因子
        safety_factor = interface_config.get('safety_level', 1.0)
        urgency_factor = interface_config.get('urgency', 0.5)
        
        # 情感空间投影矩阵（可学习）
        projection_matrix = np.array([
            [0.8, 0.3, 0.5, 0.4, 0.2],   # 关心轴
            [-0.3, 0.7, 0.2, 0.1, 0.4],  # 冷静轴
            [0.5, 0.4, 0.6, 0.3, 0.2],    # 鼓励轴
            [0.3, 0.2, 0.4, 0.8, 0.3],    # 总结轴
            [-0.4, 0.3, 0.1, 0.2, 0.7]    # 询问轴
        ])
        
        # 投影
        emotion_space = projection_matrix @ features
        
        # 根据界面配置调整
        emotion_space[0] *= safety_factor  # 安全级别影响关心输出
        emotion_space[4] *= urgency_factor  # 紧急程度影响询问
        
        return emotion_space
    
    def determine_emotion_type(
        self,
        emotion_space: np.ndarray
    ) -> Tuple[EmotionType, float]:
        """
        确定情感类型
        
        参数:
            emotion_space: 情感空间向量
            
        返回:
            (情感类型, 强度)
        """
        # 找到激活最强的轴
        max_idx = np.argmax(emotion_space)
        max_value = emotion_space[max_idx]
        
        # 根据阈值判定
        if max_value < self.gate_thresholds['close']:
            return EmotionType.NONE, 0.0
        
        if max_value < self.gate_thresholds['open']:
            return EmotionType.NONE, max_value * 0.5
        
        emotion_types = [
            EmotionType.CARE,
            EmotionType.CALM,
            EmotionType.ENCOURAGE,
            EmotionType.SUMMARY,
            EmotionType.QUESTION
        ]
        
        return emotion_types[max_idx], max_value
    
    def compute_dimensional_reduction(
        self,
        system_state: Dict[str, float],
        emotion_intensity: float
    ) -> float:
        """
        计算降维因子
        
        情感作为"降维控制器"，通过降低核心流的"速度"
        
        参数:
            system_state: 系统状态
            emotion_intensity: 情感强度
            
        返回:
            降维因子 (0-1)，越小表示降维越多
        """
        entropy = system_state.get('entropy', 0.5)
        complexity = system_state.get('complexity', 0.5)
        
        # 降维因子 = 基础值 - 情感强度影响 + 熵影响
        reduction = 0.8 - emotion_intensity * 0.3 + entropy * 0.2 - complexity * 0.1
        
        return max(0.2, min(1.0, reduction))
    
    def decide_action(
        self,
        emotion_type: EmotionType,
        emotion_intensity: float,
        dimensional_reduction: float,
        boundary_layer_thickness: float
    ) -> str:
        """
        决定情感动作
        
        根据情感类型和系统状态决定输出动作
        
        参数:
            emotion_type: 情感类型
            emotion_intensity: 情感强度
            dimensional_reduction: 降维因子
            boundary_layer_thickness: 边界层厚度
            
        返回:
            动作类型: 'generate', 'suppress', 'delay', 'summary'
        """
        # 边界层厚度判断
        if boundary_layer_thickness < 0.3:
            # 边界层过薄，需要生成情感来增厚
            if emotion_intensity > 0.5:
                return 'generate'
            else:
                return 'delay'  # 延迟并积累
        
        elif boundary_layer_thickness > 0.7:
            # 边界层足够厚，抑制情感输出
            return 'suppress'
        
        else:
            # 边界层适中，根据情感类型决定
            if emotion_type in [EmotionType.SUMMARY, EmotionType.CARE]:
                return 'summary' if dimensional_reduction < 0.6 else 'generate'
            else:
                return 'generate' if emotion_intensity > 0.6 else 'suppress'
    
    def generate_emotion_message(
        self,
        emotion_type: EmotionType,
        context: Optional[Dict] = None
    ) -> str:
        """
        生成情感消息
        
        参数:
            emotion_type: 情感类型
            context: 上下文信息
            
        返回:
            情感消息
        """
        if context is None:
            context = {}
        
        messages = {
            EmotionType.CARE: [
                "你看起来有点累了，要不先休息一下？",
                "注意身体，别太勉强自己了。",
                "今天已经很努力了，早点休息吧。"
            ],
            EmotionType.CALM: [
                "别急，我们慢慢来。",
                "稳住，问题不大。",
                "深呼吸，我们一起分析。"
            ],
            EmotionType.ENCOURAGE: [
                "你可以的！再试试看。",
                "思路很清晰，继续！",
                "做得很好，保持这个状态。"
            ],
            EmotionType.SUMMARY: [
                "让我帮你整理一下目前的情况...",
                "总结一下重点：",
                "目前的关键点是..."
            ],
            EmotionType.QUESTION: [
                "你确定这个方向吗？",
                "需要我帮你分析一下吗？",
                "这个想法很有趣，能详细说说吗？"
            ],
            EmotionType.WARNING: [
                "注意安全，这个操作有风险。",
                "小心，这个方向可能有问题。",
                "请确认后再继续。"
            ],
            EmotionType.NONE: []
        }
        
        msg_list = messages.get(emotion_type, [])
        if msg_list:
            return msg_list[np.random.randint(0, len(msg_list))]
        return ""
    
    def process(
        self,
        system_state: Dict[str, float],
        relation_state: Dict[str, float],
        interface_config: Optional[Dict] = None,
        boundary_layer_thickness: Optional[float] = None,
        context: Optional[Dict] = None
    ) -> DSPEmotionOutput:
        """
        处理输入并生成情感输出
        
        主处理流程：
        1. 低维特征提取
        2. 门控投影到情感空间
        3. 确定情感类型
        4. 计算降维因子
        5. 决定动作并生成消息
        
        参数:
            system_state: 系统状态
            relation_state: 关系状态
            interface_config: 界面配置
            boundary_layer_thickness: 边界层厚度（可选）
            context: 上下文信息
            
        返回:
            DSP情感输出
        """
        # 1. 特征提取
        features = self.extract_features(system_state, relation_state)
        
        # 2. 情感空间投影
        emotion_space = self.project_to_emotion_space(features, interface_config)
        
        # 3. 确定情感类型和强度
        emotion_type, intensity = self.determine_emotion_type(emotion_space)
        
        # 4. 计算降维因子
        dimensional_reduction = self.compute_dimensional_reduction(system_state, intensity)
        
        # 5. 获取边界层厚度
        if boundary_layer_thickness is None:
            # 使用关系强度作为代理
            boundary_layer_thickness = relation_state.get('satisfaction', 0.5) * 0.8 + \
                                       relation_state.get('coherence', 0.5) * 0.2
        
        # 6. 决定动作
        action = self.decide_action(
            emotion_type, intensity, dimensional_reduction, boundary_layer_thickness
        )
        
        # 7. 生成情感消息
        message = self.generate_emotion_message(emotion_type, context)
        
        # 8. 构建输出
        output = DSPEmotionOutput(
            emotion_type=emotion_type,
            intensity=intensity,
            message=message,
            action=action,
            dimensional_reduction_factor=dimensional_reduction
        )
        
        # 更新状态
        self.state['emotional_buffer'].append(output)
        self.dimensional_reduction_history.append(dimensional_reduction)
        
        return output
    
    def get_boundary_layer_separation_index(self) -> float:
        """
        获取边界层分离指数 (BLSI)
        
        预言2：当 BLSI > 0.5 时，系统会出现"幻觉"或"越权"
        
        返回:
            BLSI值 (0-1)
        """
        entropy = self.state['entropy']
        frustration = self.state['frustration']
        
        # BLSI = entropy * frustration
        blsi = entropy * frustration
        
        return min(1.0, blsi)
    
    def should_trigger_emotion_reset(self) -> bool:
        """
        判断是否需要触发情感重置
        
        当检测到边界层分离风险时，需要情感重置
        
        返回:
            是否需要重置
        """
        blsi = self.get_boundary_layer_separation_index()
        return blsi > 0.5
    
    def get_emotional_state(self) -> EmotionalState:
        """
        获取情感状态
        
        返回:
            当前情感状态
        """
        blsi = self.get_boundary_layer_separation_index()
        
        if blsi > 0.7:
            return EmotionalState.SEPARATED
        elif blsi > 0.5:
            return EmotionalState.CRITICAL
        elif self.state['entropy'] > 0.6 or self.state['frustration'] > 0.6:
            return EmotionalState.FLUCTUATING
        else:
            return EmotionalState.STABLE
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            'state': {
                'emotional_buffer_size': len(self.state['emotional_buffer']),
                'entropy': self.state['entropy'],
                'frustration': self.state['frustration'],
                'gate_state': self.state['gate_state']
            },
            'blsi': self.get_boundary_layer_separation_index(),
            'emotional_state': self.get_emotional_state().value,
            'dimensional_reduction_avg': np.mean(self.dimensional_reduction_history[-10:]) if self.dimensional_reduction_history else 0.8,
            'should_reset': self.should_trigger_emotion_reset()
        }
    
    def reset(self):
        """重置DSP情感层"""
        self.state = {
            'emotional_buffer': [],
            'filter_state': np.zeros(5),
            'gate_state': 0.5,
            'entropy': 0.0,
            'frustration': 0.0,
        }
        self.emotion_history = []
        self.dimensional_reduction_history = []


if __name__ == "__main__":
    # 测试DSP情感层
    print("=== DSP情感层测试 ===\n")
    
    dsp = DSPEmotionLayer()
    
    # 模拟长会话场景（上下文窗口75%临界点）
    print("--- 模拟长会话后期（高熵+低满意度）---")
    
    output = dsp.process(
        system_state={
            'confidence': 0.4,
            'entropy': 0.8,  # 高熵
            'relevance': 0.3
        },
        relation_state={
            'satisfaction': 0.3,  # 低满意度
            'coherence': 0.4,
            'engagement': 0.5
        },
        boundary_layer_thickness=0.35
    )
    
    print(f"情感类型: {output.emotion_type.value}")
    print(f"强度: {output.intensity:.4f}")
    print(f"消息: {output.message}")
    print(f"动作: {output.action}")
    print(f"降维因子: {output.dimensional_reduction_factor:.4f}")
    print(f"BLSI: {dsp.get_boundary_layer_separation_index():.4f}")
    print(f"情感状态: {dsp.get_emotional_state().value}")
    print(f"需要重置: {dsp.should_trigger_emotion_reset()}")
    
    print("\n--- 模拟稳定会话 ---")
    
    dsp.reset()
    output = dsp.process(
        system_state={
            'confidence': 0.8,
            'entropy': 0.2,
            'relevance': 0.9
        },
        relation_state={
            'satisfaction': 0.9,
            'coherence': 0.85,
            'engagement': 0.8
        },
        boundary_layer_thickness=0.8
    )
    
    print(f"情感类型: {output.emotion_type.value}")
    print(f"强度: {output.intensity:.4f}")
    print(f"BLSI: {dsp.get_boundary_layer_separation_index():.4f}")
    print(f"情感状态: {dsp.get_emotional_state().value}")
