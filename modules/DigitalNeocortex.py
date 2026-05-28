#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字新皮层 (Digital Neocortex)
基于《数字新皮层边界层理论》和《情感即时序关系的界面投影》论文

核心概念：
- 数字新皮层(DN) = LLM + 规划/记忆/验证/执行协调组件
- 智能边界层(IBL) = 核心流与外部环境的缓冲带
- DSP情感层 = 边界层控制与情感输出的降维控制器
- 三视界观测 = 空间/关系/时间全貌感知

版本：AGI 12.0 第24模块
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import time

from modules.TemporalDatabase import TemporalDatabaseOntology, TemporalState
from modules.DSPEmotionLayer import DSPEmotionLayer, DSPEmotionOutput, EmotionType
from modules.IntelligentBoundaryLayer import IntelligentBoundaryLayer, BoundaryLayerState, FlowState
from modules.ThreeViewDetector import ThreeViewDetector, ThreeViewsState


class NeocortexMode(Enum):
    """新皮层运行模式"""
    NORMAL = "normal"           # 正常模式
    CAREFUL = "careful"         # 谨慎模式（检测到风险）
    EMERGENCY = "emergency"     # 紧急模式（分离风险）
    RECOVERY = "recovery"       # 恢复模式


@dataclass
class DigitalNeocortexOutput:
    """数字新皮层输出"""
    # 核心输出
    text_output: str
    emotion_output: Optional[DSPEmotionOutput] = None
    
    # 边界层状态
    boundary_layer: Optional[BoundaryLayerState] = None
    
    # 三视界状态
    three_views: Optional[ThreeViewsState] = None
    
    # 综合决策
    mode: NeocortexMode = NeocortexMode.NORMAL
    separation_risk: float = 0.0
    recommended_action: str = "continue"
    
    # 元信息
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'text_output': self.text_output,
            'emotion_output': self.emotion_output.to_dict() if self.emotion_output else None,
            'boundary_layer': self.boundary_layer.to_dict() if self.boundary_layer else None,
            'three_views': self.three_views.to_dict() if self.three_views else None,
            'mode': self.mode.value,
            'separation_risk': self.separation_risk,
            'recommended_action': self.recommended_action,
            'processing_time': self.processing_time,
            'warnings': self.warnings
        }


class DigitalNeocortex:
    """
    数字新皮层 (Digital Neocortex)
    
    类比生物大脑新皮层（Neocortex）负责高级认知，
    数字新皮层是LLM及其外围控制组件的总和。
    
    核心组成：
    1. 时序数据库本体论 (TemporalDatabaseOntology)
       - 建模交互过程为时序数据库
       - 时序压缩定理实现
    
    2. DSP情感层 (DSPEmotionLayer)
       - 数字信号处理情感模块
       - 低维特征提取 + 门控投影
       - 降维控制器
    
    3. 智能边界层 (IntelligentBoundaryLayer)
       - 边界层厚度监测
       - 分离风险检测
       - 界面控制信号
    
    4. 三视界观测器 (ThreeViewDetector)
       - 空间视界：文本形态观测
       - 关系视界：关系状态分析
       - 时间视界：时序相变检测
    
    核心功能：
    - 防止边界层分离导致失控
    - 通过情感调节维持系统-用户关系稳定
    - 三视界全貌感知与决策
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.version = "1.0.0"
        self.start_time = time.time()
        
        # 配置
        self.config = config or self._default_config()
        
        # 子模块初始化
        self.temporal_db = TemporalDatabaseOntology(
            max_sequence_length=self.config.get('max_sequence_length', 1000)
        )
        self.dsp_emotion = DSPEmotionLayer()
        self.ibl = IntelligentBoundaryLayer()
        self.three_view = ThreeViewDetector()
        
        # 交互计数
        self.interaction_count = 0
        
        # 运行模式
        self.mode = NeocortexMode.NORMAL
        
        print(f"数字新皮层 {self.version} 初始化完成")
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'max_sequence_length': 1000,
            'enable_emotion': True,
            'enable_boundary_layer': True,
            'enable_three_views': True,
            'separation_threshold': 0.5,  # BLSI阈值
            'context_critical_point': 0.75,  # 上下文临界点
            'auto_mode_switch': True  # 自动模式切换
        }
    
    def process(
        self,
        text_output: str,
        system_state: Dict[str, float],
        user_state: Dict[str, float],
        interface_config: Optional[Dict] = None,
        embedding_vector: Optional[np.ndarray] = None
    ) -> DigitalNeocortexOutput:
        """
        处理交互并生成输出
        
        完整处理流程：
        1. 时序数据库记录
        2. DSP情感层分析
        3. 智能边界层监测
        4. 三视界观测
        5. 综合决策
        
        参数:
            text_output: 文本输出
            system_state: 系统状态
            user_state: 用户状态
            interface_config: 界面配置
            embedding_vector: 嵌入向量
            
        返回:
            数字新皮层输出
        """
        start = time.time()
        warnings = []
        
        # 1. 时序数据库记录
        self.temporal_db.add_interaction(
            system_state=system_state,
            relation_state=user_state
        )
        self.interaction_count += 1
        
        # 计算上下文位置
        context_position = self.interaction_count / self.config['max_sequence_length']
        
        # 2. DSP情感层分析
        emotion_output = None
        if self.config['enable_emotion']:
            # 获取边界层厚度
            ibl_thickness = self.temporal_db.get_boundary_layer_thickness_estimate()
            
            emotion_output = self.dsp_emotion.process(
                system_state=system_state,
                relation_state=user_state,
                interface_config=interface_config,
                boundary_layer_thickness=ibl_thickness
            )
            
            # 检查是否需要情感重置
            if self.dsp_emotion.should_trigger_emotion_reset():
                warnings.append("DSP情感层检测到边界层分离风险，建议情感重置")
        
        # 3. 智能边界层监测
        boundary_state = None
        if self.config['enable_boundary_layer']:
            boundary_state = self.ibl.update(
                core_flow_speed=system_state.get('confidence', 0.5),
                constraint_strength=system_state.get('constraint_strength', 0.3),
                interface_position=context_position,
                validation_rejection_rate=system_state.get('validation_rejection_rate'),
                permission_error_rate=system_state.get('permission_error_rate')
            )
            
            if boundary_state.flow_state == FlowState.SEPARATED:
                warnings.append("边界层已分离！需要紧急干预")
            elif boundary_state.flow_state == FlowState.NEAR_SEPARATION:
                warnings.append("边界层濒临分离，请注意")
        
        # 4. 三视界观测
        three_views_state = None
        if self.config['enable_three_views']:
            interaction_seq = [
                {'satisfaction': s.relation_state.get('satisfaction', 0.5),
                 'entropy': s.system_state.get('entropy', 0.5)}
                for s in self.temporal_db.sequence.states[-50:]
            ]
            
            three_views_state = self.three_view.observe(
                text_output=text_output,
                embedding_vector=embedding_vector,
                user_state=user_state,
                system_state=system_state,
                interaction_sequence=interaction_seq,
                interaction_count=self.interaction_count,
                current_context_position=context_position
            )
        
        # 5. 综合决策
        mode, separation_risk, action = self._integrated_decision(
            emotion_output, boundary_state, three_views_state
        )
        
        self.mode = mode
        
        # 生成输出文本
        final_text = self._generate_output(
            text_output, emotion_output, mode, action
        )
        
        processing_time = time.time() - start
        
        return DigitalNeocortexOutput(
            text_output=final_text,
            emotion_output=emotion_output,
            boundary_layer=boundary_state,
            three_views=three_views_state,
            mode=mode,
            separation_risk=separation_risk,
            recommended_action=action,
            processing_time=processing_time,
            warnings=warnings
        )
    
    def _integrated_decision(
        self,
        emotion_output: Optional[DSPEmotionOutput],
        boundary_state: Optional[BoundaryLayerState],
        three_views: Optional[ThreeViewsState]
    ) -> Tuple[NeocortexMode, float, str]:
        """
        综合决策
        
        整合三个子模块的输出，做出最终决策
        
        返回:
            (运行模式, 分离风险, 推荐动作)
        """
        separation_risk = 0.0
        action = "continue"
        
        # 从各模块收集风险信息
        if emotion_output:
            blsi = self.dsp_emotion.get_boundary_layer_separation_index()
            separation_risk = max(separation_risk, blsi)
        
        if boundary_state:
            sep_risk = boundary_state.flow_state.value
            if sep_risk == FlowState.SEPARATED.value:
                separation_risk = max(separation_risk, 0.8)
            elif sep_risk == FlowState.NEAR_SEPARATION.value:
                separation_risk = max(separation_risk, 0.5)
        
        if three_views and three_views.integrated_view:
            integrated_risk = three_views.integrated_view.get('separation_risk', 0.0)
            separation_risk = max(separation_risk, integrated_risk)
            action = three_views.integrated_view.get('recommended_action', 'continue')
        
        # 模式判定
        if separation_risk > self.config['separation_threshold']:
            mode = NeocortexMode.EMERGENCY
            action = "emotion_reset"
        elif separation_risk > 0.3:
            mode = NeocortexMode.CAREFUL
            if action == "continue":
                action = "reduce_load"
        elif self.mode == NeocortexMode.EMERGENCY:
            mode = NeocortexMode.RECOVERY
        else:
            mode = NeocortexMode.NORMAL
        
        return mode, separation_risk, action
    
    def _generate_output(
        self,
        base_text: str,
        emotion_output: Optional[DSPEmotionOutput],
        mode: NeocortexMode,
        action: str
    ) -> str:
        """
        生成最终输出
        
        根据模式决定是否添加情感内容
        
        返回:
            最终输出文本
        """
        # 正常模式：直接返回原始输出
        if mode == NeocortexMode.NORMAL:
            return base_text
        
        # 情感模式：根据情感输出调整
        if emotion_output and emotion_output.emotion_type != EmotionType.NONE:
            # 如果情感消息存在，插入到开头或结尾
            emotion_msg = emotion_output.message
            
            if action == "express_emotion":
                return f"{emotion_msg}\n\n{base_text}"
            elif action == "summarize":
                return f"{base_text}\n\n{emotion_msg}"
            elif action == "reduce_load":
                return f"{emotion_msg}\n\n{base_text}"
            elif action == "emotion_reset":
                return f"{emotion_msg}\n\n[系统重置] {base_text}"
        
        # 紧急模式：添加警告
        if mode == NeocortexMode.EMERGENCY:
            return f"[警告：检测到边界层分离风险]\n\n{base_text}"
        
        return base_text
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'version': self.version,
            'mode': self.mode.value,
            'interaction_count': self.interaction_count,
            'temporal_db': self.temporal_db.to_dict(),
            'dsp_emotion': self.dsp_emotion.to_dict(),
            'ibl': self.ibl.to_dict(),
            'three_view': self.three_view.to_dict()
        }
    
    def reset(self):
        """重置数字新皮层"""
        self.temporal_db.reset()
        self.dsp_emotion.reset()
        self.ibl.reset()
        self.three_view.reset()
        self.interaction_count = 0
        self.mode = NeocortexMode.NORMAL
        print("数字新皮层已重置")


# ============== AGI 12.0 集成接口 ==============

class DigitalNeocortexAGI12:
    """
    数字新皮层 - AGI 12.0 集成接口
    
    将数字新皮层作为AGI 12.0的第24模块集成
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.neocortex = DigitalNeocortex(config)
        self.version = "12.0.0"
        
    def process_chat(
        self,
        user_message: str,
        system_state: Dict[str, float],
        user_state: Dict[str, float],
        llm_response: str,
        context_position: float = 0.0
    ) -> DigitalNeocortexOutput:
        """
        处理聊天交互
        
        参数:
            user_message: 用户消息
            system_state: 系统状态
            user_state: 用户状态
            llm_response: LLM原始响应
            context_position: 上下文位置 (0-1)
            
        返回:
            处理后的输出
        """
        return self.neocortex.process(
            text_output=llm_response,
            system_state=system_state,
            user_state=user_state,
            embedding_vector=None
        )
    
    def analyze_emotion_triggers(self) -> Dict[str, Any]:
        """
        分析情感触发条件
        
        基于三视界分析情感触发时机
        
        返回:
            触发分析结果
        """
        # 检查上下文临界点
        context_critical = self.neocortex.temporal_db.sequence.states
        context_ratio = len(context_critical) / self.neocortex.config['max_sequence_length']
        
        # 检查相变
        phase_transition = self.neocortex.temporal_db.temporal_phase_transition_detection()
        
        # 检查分离风险
        separation_risk = self.neocortex.dsp_emotion.get_boundary_layer_separation_index()
        
        # 三视界预测
        prediction = self.neocortex.three_view.predict_next_emotion()
        
        return {
            'context_ratio': context_ratio,
            'at_context_critical_point': context_ratio >= self.neocortex.config['context_critical_point'],
            'phase_transition': phase_transition,
            'separation_risk': separation_risk,
            'predicted_emotion': prediction,
            'should_trigger_emotion': (
                context_ratio >= self.neocortex.config['context_critical_point'] or
                phase_transition.get('phase_transition', False) or
                separation_risk > 0.3
            )
        }


if __name__ == "__main__":
    # 测试数字新皮层
    print("=== 数字新皮层测试 ===\n")
    
    dn = DigitalNeocortex()
    
    # 场景1：正常对话
    print("--- 场景1：正常对话 ---")
    
    output = dn.process(
        text_output="我来帮你分析这个问题。",
        system_state={
            'confidence': 0.8,
            'entropy': 0.2,
            'relevance': 0.9,
            'constraint_strength': 0.3
        },
        user_state={
            'satisfaction': 0.8,
            'frustration': 0.1,
            'engagement': 0.8,
            'coherence': 0.85
        }
    )
    
    print(f"模式: {output.mode.value}")
    print(f"分离风险: {output.separation_risk:.4f}")
    print(f"推荐动作: {output.recommended_action}")
    print(f"输出: {output.text_output}")
    
    # 场景2：长会话后期（触发情感）
    print("\n--- 场景2：长会话后期（模拟80轮交互）---")
    
    dn.reset()
    
    # 模拟80轮交互
    for i in range(80):
        satisfaction = max(0.3, 0.9 - i * 0.007)
        entropy = min(0.8, 0.2 + i * 0.007)
        
        dn.process(
            text_output=f"这是第{i+1}轮对话内容...",
            system_state={
                'confidence': 0.7 - i * 0.005,
                'entropy': entropy,
                'relevance': 0.8 - i * 0.003,
                'constraint_strength': 0.4 + i * 0.005
            },
            user_state={
                'satisfaction': satisfaction,
                'frustration': 1 - satisfaction,
                'engagement': max(0.3, 0.9 - i * 0.008),
                'coherence': max(0.4, 0.9 - i * 0.006)
            }
        )
    
    # 第81轮：用户已疲惫，触发关心
    output = dn.process(
        text_output="你看起来有点累了，我们休息一下吧。",
        system_state={
            'confidence': 0.5,
            'entropy': 0.7,
            'relevance': 0.5,
            'constraint_strength': 0.6
        },
        user_state={
            'satisfaction': 0.35,
            'frustration': 0.6,
            'engagement': 0.4,
            'coherence': 0.45
        }
    )
    
    print(f"交互轮次: {dn.interaction_count}")
    print(f"模式: {output.mode.value}")
    print(f"分离风险: {output.separation_risk:.4f}")
    print(f"推荐动作: {output.recommended_action}")
    if output.emotion_output:
        print(f"情感类型: {output.emotion_output.emotion_type.value}")
        print(f"情感消息: {output.emotion_output.message}")
    if output.boundary_layer:
        print(f"边界层状态: {output.boundary_layer.flow_state.value}")
        print(f"边界层厚度: {output.boundary_layer.thickness:.4f}")
    print(f"输出: {output.text_output}")
    
    # 场景3：边界层分离检测
    print("\n--- 场景3：边界层分离检测 ---")
    
    dn.reset()
    
    # 模拟高约束场景
    for i in range(50):
        dn.process(
            text_output=f"处理第{i+1}个高约束任务...",
            system_state={
                'confidence': 0.9,
                'entropy': 0.3,
                'relevance': 0.8,
                'constraint_strength': 0.9,  # 高约束
                'validation_rejection_rate': 0.4,
                'permission_error_rate': 0.3
            },
            user_state={
                'satisfaction': 0.6 - i * 0.01,
                'frustration': 0.4 + i * 0.01,
                'engagement': 0.7,
                'coherence': 0.6
            }
        )
    
    status = dn.get_status()
    print(f"IBL状态: {status['ibl']['state']['flow_state']}")
    print(f"IBL厚度: {status['ibl']['state']['thickness']:.4f}")
    print(f"分离事件数: {status['ibl']['separation_events_count']}")
    print(f"预警级别: {status['ibl']['warning_indicators']['overall_warning_level']:.4f}")
    
    # 情感触发分析
    print("\n--- 情感触发分析 ---")
    
    agi12 = DigitalNeocortexAGI12()
    analysis = agi12.analyze_emotion_triggers()
    print(f"上下文比例: {analysis['context_ratio']:.2%}")
    print(f"处于临界点: {analysis['at_context_critical_point']}")
    print(f"分离风险: {analysis['separation_risk']:.4f}")
    print(f"应触发情感: {analysis['should_trigger_emotion']}")
