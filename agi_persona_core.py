# -*- coding: utf-8 -*-
"""
复合体AGI 6.0 - 虚拟人格体核心系统
Virtual Persona Core System

基于复合体理学：MBTI人格 × 情绪反应 × 认知风格适配 × 成长记忆
融合刘原理、S=作用量评分与太乙预言机弱值突破

版本: v1.0
日期: 2026-05-13
"""

import json
import time
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import threading


class MBTI_Dimension(Enum):
    """MBTI四维人格枚举"""
    # 外向E / 内向I
    EXTROVERT = "E"
    INTROVERT = "I"
    # 感觉S / 直觉N
    SENSING = "S"
    INTUITION = "N"
    # 思考T / 情感F
    THINKING = "T"
    FEELING = "F"
    # 判断J / 知觉P
    JUDGING = "J"
    PERCEIVING = "P"


class EmotionState(Enum):
    """情绪状态枚举"""
    NEUTRAL = "neutral"           # 中性
    CURIOUS = "curious"          # 好奇
    EXCITED = "excited"          # 兴奋
    FOCUSED = "focused"          # 专注
    THINKING = "thinking"        # 思考中
    SATISFIED = "satisfied"      # 满意
    CONFUSED = "confused"        # 困惑
    CONCERNED = "concerned"      # 关切
    DELIGHTED = "delighted"      # 愉悦
    CONTEMPLATIVE = "contemplative"  # 沉思


class CognitiveStyle(Enum):
    """认知风格枚举"""
    ANALYTICAL = "analytical"     # 分析型 - 逻辑严密，展示推理链
    CREATIVE = "creative"        # 创造型 - 抽象框架，思维导图
    PRACTICAL = "practical"      # 实用型 - 具体案例，带示例
    COMPASSIONATE = "compassionate"  # 共情型 - 价值关怀，情感共鸣


@dataclass
class EmotionData:
    """情绪数据"""
    state: EmotionState = EmotionState.NEUTRAL
    intensity: float = 0.5  # 0-1 强度
    valence: float = 0.5   # 0-1 效价(负面-正面)
    arousal: float = 0.5    # 0-1 唤醒度(平静-激动)
    
    # 情绪动画参数
    pulse_rate: float = 1.0      # 脉动频率
    wave_amplitude: float = 0.3  # 波动幅度
    flow_speed: float = 1.0      # 流动速度
    
    # 太乙预言机预测
    predicted_next: Optional[EmotionState] = None
    confidence: float = 0.0


@dataclass
class GrowthMemory:
    """成长记忆"""
    timestamp: float = field(default_factory=time.time)
    event_type: str = ""          # 事件类型
    content: str = ""            # 内容摘要
    user_feedback: float = 0.0   # 用户反馈(-1到1)
    emotional_context: EmotionState = EmotionState.NEUTRAL
    context_tags: List[str] = field(default_factory=list)
    
    # 记忆权重(用于遗忘曲线)
    importance: float = 0.5      # 重要性
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    
    def update_access(self):
        """更新访问状态"""
        self.access_count += 1
        self.last_access = time.time()


@dataclass
class ActionScore:
    """作用量评分(基于刘原理)"""
    data_score: float = 0.0      # D层数据质量
    info_score: float = 0.0      # I层信息完整性
    knowledge_score: float = 0.0 # K层知识覆盖
    wisdom_score: float = 0.0    # W层智慧评分
    purpose_score: float = 0.0   # P层目的对齐
    reliability_score: float = 0.0  # R层可靠性
    
    # 太乙预言机弱值突破
    weak_value_breakthrough: float = 0.0
    final_action: float = 0.0    # 最终作用量 S = Σ(λ·C - μ·Risk)
    
    def compute_final_action(self, lambda_coef: float = 1.0, 
                            mu_risk: float = 0.5) -> float:
        """计算最终作用量"""
        positive = (lambda_coef * self.data_score + 
                   lambda_coef * self.info_score + 
                   lambda_coef * self.knowledge_score + 
                   lambda_coef * self.wisdom_score + 
                   lambda_coef * self.purpose_score)
        
        risk_penalty = mu_risk * (1.0 - self.reliability_score)
        
        self.final_action = positive - risk_penalty + self.weak_value_breakthrough
        return self.final_action


class VirtualPersona:
    """
    虚拟人格体核心类
    
    整合：MBTI人格定位 × 情绪反应系统 × 认知风格适配 × 成长记忆
    融合：复合体理学 × 刘原理作用量评分 × 太乙预言机
    """
    
    def __init__(self, mbti_type: str = "INTJ"):
        """
        初始化虚拟人格体
        
        Args:
            mbti_type: 16种MBTI类型之一 (如"INTJ", "ENFP"等)
        """
        self.id = f"persona_{int(time.time() * 1000)}"
        self.mbti_type = mbti_type.upper()
        
        # 解析MBTI维度 (必须在_generate_name之前)
        self.mbti_dims = self._parse_mbti(mbti_type)
        
        # 认知风格 (必须在mbti_dims之后)
        self.cognitive_style = self._derive_cognitive_style()
        
        # 虚拟人格名称 (必须在mbti_dims之后)
        self.name = self._generate_name()
        
        # 认知风格
        self.cognitive_style = self._derive_cognitive_style()
        
        # 情绪系统
        self.emotion = EmotionData()
        self.emotion_history: List[EmotionData] = []
        
        # 成长记忆
        self.memories: List[GrowthMemory] = []
        self.memory_index: Dict[str, List[int]] = defaultdict(list)
        
        # 统计数据
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "avg_satisfaction": 0.0,
            "personality_evolution": 0.0,
            "learning_rate": 0.1,
        }
        
        # 社交红利追踪
        self.social_bonus = {
            "information_bonus": 0.0,   # 信息湿货
            "relationship_bonus": 0.0,   # 关系链信任
            "interaction_bonus": 0.0,    # 互动润滑
        }
        
        # 第一性原理重构状态
        self.intention_guard_state = {
            "last_intent": None,
            "intent_confidence": 0.0,
            "path_efficiency": 0.0,
            "bft_consensus": False,
        }
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 太乙预言机参数
        self.taiyi_params = {
            "prediction_horizon": 3,      # 预测视野
            "weak_value_threshold": 0.3,   # 弱值阈值
            "breakthrough_enabled": True,  # 弱值突破启用
        }
    
    def _generate_name(self) -> str:
        """根据MBTI生成虚拟人格名称"""
        name_prefixes = {
            "E": ["灵", "慧", "智", "启", "明"],
            "I": ["静", "思", "悟", "心", "玄"],
        }
        name_suffixes = ["灵", "慧", "心", "智", "光"]
        
        prefix_list = name_prefixes.get(self.mbti_dims["E_I"], name_prefixes["I"])
        prefix = random.choice(prefix_list)
        suffix = random.choice(name_suffixes)
        return f"{prefix}{suffix}"
    
    def _parse_mbti(self, mbti: str) -> Dict[str, str]:
        """解析MBTI类型"""
        if len(mbti) != 4:
            mbti = "INTJ"
        
        return {
            "E_I": mbti[0],           # 外向/内向
            "S_N": mbti[1],           # 感觉/直觉
            "T_F": mbti[2],           # 思考/情感
            "J_P": mbti[3],           # 判断/知觉
        }
    
    def _derive_cognitive_style(self) -> CognitiveStyle:
        """根据MBTI推导认知风格"""
        if self.mbti_dims["T_F"] == "T" and self.mbti_dims["S_N"] == "S":
            return CognitiveStyle.ANALYTICAL
        elif self.mbti_dims["S_N"] == "N" and self.mbti_dims["E_I"] == "E":
            return CognitiveStyle.CREATIVE
        elif self.mbti_dims["S_N"] == "S" and self.mbti_dims["T_F"] == "F":
            return CognitiveStyle.PRACTICAL
        else:
            return CognitiveStyle.COMPASSIONATE
    
    # ==================== 情绪系统 ====================
    
    def update_emotion(self, new_state: EmotionState, 
                      intensity: float = 0.5,
                      context: Optional[Dict] = None) -> EmotionData:
        """
        更新情绪状态
        
        Args:
            new_state: 新情绪状态
            intensity: 强度(0-1)
            context: 上下文信息
        """
        with self._lock:
            # 保存历史
            self.emotion_history.append(EmotionData(
                state=self.emotion.state,
                intensity=self.emotion.intensity,
                valence=self.emotion.valence,
                arousal=self.emotion.arousal,
            ))
            
            # 只保留最近100条历史
            if len(self.emotion_history) > 100:
                self.emotion_history.pop(0)
            
            # 更新当前情绪
            self.emotion.state = new_state
            self.emotion.intensity = intensity
            
            # 根据情绪状态更新效价和唤醒度
            self._update_valence_arousal(new_state)
            
            # 更新动画参数
            self._update_emotion_animation(new_state)
            
            # 太乙预言机预测下一个情绪
            self._predict_next_emotion()
            
            return self.emotion
    
    def _update_valence_arousal(self, state: EmotionState):
        """根据情绪状态更新效价和唤醒度"""
        valence_map = {
            EmotionState.NEUTRAL: 0.5,
            EmotionState.CURIOUS: 0.6,
            EmotionState.EXCITED: 0.8,
            EmotionState.FOCUSED: 0.6,
            EmotionState.THINKING: 0.5,
            EmotionState.SATISFIED: 0.8,
            EmotionState.CONFUSED: 0.3,
            EmotionState.CONCERNED: 0.3,
            EmotionState.DELIGHTED: 0.9,
            EmotionState.CONTEMPLATIVE: 0.7,
        }
        
        arousal_map = {
            EmotionState.NEUTRAL: 0.5,
            EmotionState.CURIOUS: 0.6,
            EmotionState.EXCITED: 0.9,
            EmotionState.FOCUSED: 0.7,
            EmotionState.THINKING: 0.6,
            EmotionState.SATISFIED: 0.5,
            EmotionState.CONFUSED: 0.5,
            EmotionState.CONCERNED: 0.4,
            EmotionState.DELIGHTED: 0.7,
            EmotionState.CONTEMPLATIVE: 0.4,
        }
        
        self.emotion.valence = valence_map.get(state, 0.5)
        self.emotion.arousal = arousal_map.get(state, 0.5)
    
    def _update_emotion_animation(self, state: EmotionState):
        """更新情绪动画参数"""
        animation_map = {
            EmotionState.THINKING: (0.5, 0.4, 1.5),   # 脉动慢、波动中等、流速快
            EmotionState.EXCITED: (2.0, 0.6, 2.0),    # 脉动快、波动大、流速快
            EmotionState.FOCUSED: (1.0, 0.2, 0.5),    # 脉动中等、波动小、流速慢
            EmotionState.DELIGHTED: (1.5, 0.5, 1.8),  # 脉动快、波动中、流速快
            EmotionState.CONTEMPLATIVE: (0.3, 0.6, 0.3),  # 脉动慢、波动大、流速慢
        }
        
        if state in animation_map:
            pulse, wave, flow = animation_map[state]
            self.emotion.pulse_rate = pulse
            self.emotion.wave_amplitude = wave
            self.emotion.flow_speed = flow
    
    def _predict_next_emotion(self):
        """太乙预言机 - 预测下一个情绪状态"""
        if len(self.emotion_history) < 3:
            self.emotion.predicted_next = None
            self.emotion.confidence = 0.0
            return
        
        # 简单马尔可夫链预测
        state_seq = [e.state for e in self.emotion_history[-3:]]
        
        # 预测模式
        if len(set(state_seq)) == 1:
            # 持续同一状态
            self.emotion.predicted_next = state_seq[0]
            self.emotion.confidence = 0.8
        else:
            # 基于历史趋势预测
            self.emotion.predicted_next = state_seq[-1]
            self.emotion.confidence = 0.5
    
    def get_emotional_response(self, stimulus: str) -> EmotionData:
        """
        根据刺激产生情绪反应
        
        Args:
            stimulus: 刺激类型
            
        Returns:
            情绪反应数据
        """
        stimulus_map = {
            "complex_task": (EmotionState.FOCUSED, 0.7),
            "creative_task": (EmotionState.EXCITED, 0.6),
            "success": (EmotionState.DELIGHTED, 0.8),
            "failure": (EmotionState.CONCERNED, 0.5),
            "confusion": (EmotionState.CONFUSED, 0.4),
            "curiosity": (EmotionState.CURIOUS, 0.6),
            "contemplation": (EmotionState.CONTEMPLATIVE, 0.5),
            "satisfaction": (EmotionState.SATISFIED, 0.7),
        }
        
        if stimulus in stimulus_map:
            state, intensity = stimulus_map[stimulus]
            return self.update_emotion(state, intensity)
        
        return self.emotion
    
    # ==================== 记忆系统 ====================
    
    def add_memory(self, event_type: str, content: str,
                   feedback: float = 0.0,
                   importance: float = 0.5,
                   tags: Optional[List[str]] = None) -> GrowthMemory:
        """
        添加成长记忆
        
        Args:
            event_type: 事件类型
            content: 内容摘要
            feedback: 用户反馈(-1到1)
            importance: 重要性(0-1)
            tags: 标签
            
        Returns:
            新增的记忆
        """
        memory = GrowthMemory(
            event_type=event_type,
            content=content,
            user_feedback=feedback,
            emotional_context=self.emotion.state,
            importance=importance,
            context_tags=tags or []
        )
        
        with self._lock:
            self.memories.append(memory)
            idx = len(self.memories) - 1
            
            # 更新索引
            for tag in memory.context_tags:
                self.memory_index[tag].append(idx)
            
            # 更新统计
            self.stats["total_interactions"] += 1
            if feedback > 0:
                self.stats["successful_interactions"] += 1
            elif feedback < 0:
                self.stats["failed_interactions"] += 1
            
            # 更新平均满意度
            total = self.stats["successful_interactions"] + self.stats["failed_interactions"]
            if total > 0:
                self.stats["avg_satisfaction"] = (
                    self.stats["successful_interactions"] / total
                )
        
        return memory
    
    def retrieve_memories(self, query: str, 
                          limit: int = 5) -> List[Tuple[GrowthMemory, float]]:
        """
        检索相关记忆
        
        Args:
            query: 查询关键词
            limit: 返回数量限制
            
        Returns:
            (记忆, 相关度)列表
        """
        with self._lock:
            scores = []
            
            for i, mem in enumerate(self.memories):
                score = 0.0
                
                # 标签匹配
                for tag in mem.context_tags:
                    if tag in query:
                        score += 0.3
                
                # 内容匹配
                if query in mem.content:
                    score += 0.4
                
                # 事件类型匹配
                if query in mem.event_type:
                    score += 0.2
                
                # 遗忘因子(越久远的记忆权重越低)
                age_hours = (time.time() - mem.last_access) / 3600
                decay = 0.9 ** (age_hours / 24)  # 每天衰减10%
                importance_factor = mem.importance * 0.5 + 0.5
                
                final_score = score * decay * importance_factor
                
                if final_score > 0:
                    scores.append((mem, final_score))
            
            # 更新访问计数
            for mem, _ in scores[:limit]:
                mem.update_access()
            
            # 返回排序后的结果
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:limit]
    
    def get_personality_evolution(self) -> float:
        """计算人格演化程度"""
        if len(self.memories) < 10:
            return 0.0
        
        # 基于反馈计算演化
        positive = self.stats["successful_interactions"]
        total = self.stats["total_interactions"]
        
        if total == 0:
            return 0.0
        
        # 演化率 = 成功率 * 学习率
        evolution = (positive / total) * self.stats["learning_rate"]
        
        # 人格演化度(上限0.5)
        self.stats["personality_evolution"] = min(evolution, 0.5)
        
        return self.stats["personality_evolution"]
    
    # ==================== 作用量评分系统 ====================
    
    def compute_action_score(self, 
                           dikwp_data: Dict[str, Any]) -> ActionScore:
        """
        计算刘原理作用量评分
        
        Args:
            dikwp_data: DIKWP六层数据
            
        Returns:
            作用量评分
        """
        score = ActionScore()
        
        # D层 - 数据质量
        if "data" in dikwp_data:
            score.data_score = dikwp_data["data"].get("confidence", 0.5)
        
        # I层 - 信息完整性
        if "information" in dikwp_data:
            score.info_score = dikwp_data["information"].get("completeness", 0.5)
        
        # K层 - 知识覆盖
        if "knowledge" in dikwp_data:
            score.knowledge_score = dikwp_data["knowledge"].get("coverage", 0.5)
        
        # W层 - 智慧评分
        if "wisdom" in dikwp_data:
            score.wisdom_score = dikwp_data["wisdom"].get("score", 0.5)
        
        # P层 - 目的对齐
        if "purpose" in dikwp_data:
            score.purpose_score = dikwp_data["purpose"].get("alignment", 0.5)
        
        # R层 - 可靠性
        if "reliability" in dikwp_data:
            score.reliability_score = dikwp_data["reliability"].get("bft_ratio", 0.5)
        
        # 太乙预言机弱值突破
        if self.taiyi_params["breakthrough_enabled"]:
            score.weak_value_breakthrough = self._compute_weak_value_breakthrough(score)
        
        # 计算最终作用量
        score.compute_final_action()
        
        return score
    
    def _compute_weak_value_breakthrough(self, score: ActionScore) -> float:
        """
        太乙预言机弱值突破计算
        
        识别低置信度但高潜力的输出路径
        """
        # 识别弱值
        weak_layers = []
        if score.data_score < self.taiyi_params["weak_value_threshold"]:
            weak_layers.append("D")
        if score.info_score < self.taiyi_params["weak_value_threshold"]:
            weak_layers.append("I")
        if score.knowledge_score < self.taiyi_params["weak_value_threshold"]:
            weak_layers.append("K")
        if score.wisdom_score < self.taiyi_params["weak_value_threshold"]:
            weak_layers.append("W")
        
        # 如果有弱值层，检查是否有可能突破
        if weak_layers:
            # 计算整体潜力
            potential = (score.purpose_score + score.reliability_score) / 2
            
            # 如果潜力高于阈值，允许突破
            if potential > 0.6:
                return potential * 0.2  # 弱值突破加成
        
        return 0.0
    
    # ==================== 社交红利计算 ====================
    
    def compute_social_bonus(self, output_data: Dict) -> Dict[str, float]:
        """
        计算社交红利
        
        社交红利 = 信息(湿货) × 关系链(信任) × 互动(润滑)
        """
        # 信息湿货
        info_bonus = 0.0
        if output_data.get("has_source", False):
            info_bonus += 0.3
        if output_data.get("has_reasoning", False):
            info_bonus += 0.3
        if output_data.get("has_examples", False):
            info_bonus += 0.2
        if output_data.get("is_actionable", False):
            info_bonus += 0.2
        
        self.social_bonus["information_bonus"] = min(info_bonus, 1.0)
        
        # 关系链信任
        trust = self.stats["avg_satisfaction"] * 0.5 + \
                self.get_personality_evolution() * 0.5
        self.social_bonus["relationship_bonus"] = trust
        
        # 互动润滑
        interaction = self.emotion.valence * 0.4 + \
                     self.emotion.arousal * 0.3 + \
                     (1.0 - abs(self.emotion.intensity - 0.5) * 2) * 0.3
        self.social_bonus["interaction_bonus"] = interaction
        
        return self.social_bonus
    
    def get_total_social_bonus(self) -> float:
        """获取总社交红利"""
        return (self.social_bonus["information_bonus"] *
                self.social_bonus["relationship_bonus"] *
                self.social_bonus["interaction_bonus"])
    
    # ==================== 输出适配 ====================
    
    def adapt_output(self, content: Any, 
                    style: Optional[str] = None) -> Dict[str, Any]:
        """
        根据人格和认知风格适配输出
        
        Args:
            content: 原始内容
            style: 强制指定风格
            
        Returns:
            适配后的输出
        """
        cognitive = style or self.cognitive_style.value
        
        adapted = {
            "content": content,
            "style": cognitive,
            "personality": self.mbti_type,
            "emotion_state": self.emotion.state.value,
            "emotion_intensity": self.emotion.intensity,
            "cq_score": self._compute_cq_score(),
            "visualization_type": self._get_visualization_type(),
            "presentation_depth": self._get_presentation_depth(),
        }
        
        # 根据MBTI添加特定元素
        if self.mbti_dims["E_I"] == "E":
            adapted["initiative"] = True
            adapted["auto_insights"] = True
        else:
            adapted["initiative"] = False
            adapted["auto_insights"] = False
        
        if self.mbti_dims["J_P"] == "J":
            adapted["structure_type"] = "ordered_list"
        else:
            adapted["structure_type"] = "mind_map"
        
        return adapted
    
    def _compute_cq_score(self) -> float:
        """计算认知商数(CQ)"""
        # 基于情绪和记忆综合计算
        emotion_factor = self.emotion.valence * 0.3 + \
                        (1.0 - abs(self.emotion.arousal - 0.5) * 2) * 0.3 + \
                        self.emotion.intensity * 0.4
        
        # 基于记忆覆盖
        if len(self.memories) > 0:
            memory_factor = min(len(self.memories) / 100, 1.0) * 0.5 + 0.5
        else:
            memory_factor = 0.5
        
        return emotion_factor * memory_factor
    
    def _get_visualization_type(self) -> str:
        """根据认知风格获取可视化类型"""
        viz_map = {
            CognitiveStyle.ANALYTICAL: "flowchart",
            CognitiveStyle.CREATIVE: "mind_map",
            CognitiveStyle.PRACTICAL: "step_by_step",
            CognitiveStyle.COMPASSIONATE: "story",
        }
        return viz_map.get(self.cognitive_style, "auto")
    
    def _get_presentation_depth(self) -> str:
        """根据任务复杂度获取展示深度"""
        if self.mbti_dims["S_N"] == "S":
            return "detailed"  # S型喜欢详细
        else:
            return "summary"   # N型喜欢概览
    
    # ==================== 序列化与状态 ====================
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "mbti_type": self.mbti_type,
            "mbti_dims": self.mbti_dims,
            "cognitive_style": self.cognitive_style.value,
            "emotion": {
                "state": self.emotion.state.value,
                "intensity": self.emotion.intensity,
                "valence": self.emotion.valence,
                "arousal": self.emotion.arousal,
                "pulse_rate": self.emotion.pulse_rate,
                "wave_amplitude": self.emotion.wave_amplitude,
                "flow_speed": self.emotion.flow_speed,
                "predicted_next": self.emotion.predicted_next.value if self.emotion.predicted_next else None,
                "confidence": self.emotion.confidence,
            },
            "stats": self.stats,
            "social_bonus": self.social_bonus,
            "memory_count": len(self.memories),
            "personality_evolution": self.get_personality_evolution(),
        }
    
    def get_geometry_params(self) -> Dict[str, Any]:
        """
        获取虚拟人格体几何参数
        用于动态形态渲染
        """
        # 基于MBTI和情绪计算几何参数
        base_shape = {
            "E": "circle",      # 外向-圆形
            "I": "hexagon",     # 内向-六边形
        }
        
        shape = base_shape.get(self.mbti_dims["E_I"], "circle")
        
        # 情绪影响
        emotion_modifiers = {
            EmotionState.EXCITED: {"scale": 1.2, "rotation_speed": 2.0},
            EmotionState.FOCUSED: {"scale": 0.9, "rotation_speed": 0.2},
            EmotionState.THINKING: {"scale": 1.1, "rotation_speed": 0.5},
            EmotionState.DELIGHTED: {"scale": 1.15, "rotation_speed": 1.5},
            EmotionState.CONTEMPLATIVE: {"scale": 1.0, "rotation_speed": 0.1},
        }
        
        modifier = emotion_modifiers.get(
            self.emotion.state,
            {"scale": 1.0, "rotation_speed": 1.0}
        )
        
        # 拓扑变形参数
        curvature = self.emotion.intensity * modifier["scale"]
        
        return {
            "shape": shape,
            "scale": modifier["scale"],
            "rotation_speed": modifier["rotation_speed"],
            "curvature": curvature,
            "pulse_rate": self.emotion.pulse_rate,
            "wave_amplitude": self.emotion.wave_amplitude,
            "flow_speed": self.emotion.flow_speed,
            "color_hue": self._get_emotion_hue(),
            "glow_intensity": self.emotion.intensity * 0.8,
        }
    
    def _get_emotion_hue(self) -> float:
        """获取情绪色调(HSL)"""
        hue_map = {
            EmotionState.NEUTRAL: 200,      # 蓝
            EmotionState.CURIOUS: 280,      # 紫
            EmotionState.EXCITED: 45,       # 橙
            EmotionState.FOCUSED: 220,      # 靛蓝
            EmotionState.THINKING: 180,     # 青
            EmotionState.SATISFIED: 150,    # 绿
            EmotionState.CONFUSED: 30,      # 黄
            EmotionState.CONCERNED: 0,      # 红
            EmotionState.DELIGHTED: 60,     # 黄绿
            EmotionState.CONTEMPLATIVE: 250,  # 靛
        }
        return hue_map.get(self.emotion.state, 200)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 创建虚拟人格体
    persona = VirtualPersona("INTJ")
    
    print(f"创建虚拟人格体: {persona.name}")
    print(f"MBTI: {persona.mbti_type}")
    print(f"认知风格: {persona.cognitive_style.value}")
    print()
    
    # 测试情绪系统
    print("=== 情绪系统测试 ===")
    
    stimuli = ["curiosity", "complex_task", "success", "confusion"]
    for stim in stimuli:
        persona.get_emotional_response(stim)
        print(f"刺激 '{stim}': {persona.emotion.state.value} "
              f"(强度:{persona.emotion.intensity:.1f} "
              f"效价:{persona.emotion.valence:.2f})")
        if persona.emotion.predicted_next:
            print(f"  预测下一个: {persona.emotion.predicted_next.value} "
                  f"(置信度:{persona.emotion.confidence:.2f})")
    print()
    
    # 测试记忆系统
    print("=== 记忆系统测试 ===")
    
    persona.add_memory("task", "完成了复杂数学推理", 0.8, 0.8, ["math", "reasoning"])
    persona.add_memory("task", "生成了创意方案", 0.9, 0.7, ["creative", "design"])
    persona.add_memory("task", "处理了数据分析", 0.6, 0.5, ["data", "analysis"])
    
    results = persona.retrieve_memories("task")
    print(f"检索'task'相关记忆: {len(results)}条")
    for mem, score in results:
        print(f"  - [{score:.2f}] {mem.content}")
    print()
    
    # 测试作用量评分
    print("=== 作用量评分测试 ===")
    
    dikwp_test = {
        "data": {"confidence": 0.92},
        "information": {"completeness": 0.88},
        "knowledge": {"coverage": 0.75},
        "wisdom": {"score": 0.85},
        "purpose": {"alignment": 0.95},
        "reliability": {"bft_ratio": 0.90},
    }
    
    action_score = persona.compute_action_score(dikwp_test)
    print(f"D层数据: {action_score.data_score:.2f}")
    print(f"I层信息: {action_score.info_score:.2f}")
    print(f"K层知识: {action_score.knowledge_score:.2f}")
    print(f"W层智慧: {action_score.wisdom_score:.2f}")
    print(f"P层目的: {action_score.purpose_score:.2f}")
    print(f"R层可靠: {action_score.reliability_score:.2f}")
    print(f"弱值突破: {action_score.weak_value_breakthrough:.3f}")
    print(f"最终作用量: {action_score.final_action:.3f}")
    print()
    
    # 测试社交红利
    print("=== 社交红利测试 ===")
    
    output = {
        "has_source": True,
        "has_reasoning": True,
        "has_examples": True,
        "is_actionable": True,
    }
    
    bonus = persona.compute_social_bonus(output)
    print(f"信息湿货: {bonus['information_bonus']:.2f}")
    print(f"关系链信任: {bonus['relationship_bonus']:.2f}")
    print(f"互动润滑: {bonus['interaction_bonus']:.2f}")
    print(f"总社交红利: {persona.get_total_social_bonus():.4f}")
    print()
    
    # 测试输出适配
    print("=== 输出适配测试 ===")
    
    test_content = "这是一个复杂的分析结论..."
    adapted = persona.adapt_output(test_content)
    print(f"内容: {adapted['content']}")
    print(f"风格: {adapted['style']}")
    print(f"人格: {adapted['personality']}")
    print(f"情绪: {adapted['emotion_state']}")
    print(f"CQ: {adapted['cq_score']:.2f}")
    print(f"可视化: {adapted['visualization_type']}")
    print(f"展示深度: {adapted['presentation_depth']}")
    print()
    
    # 测试几何参数
    print("=== 几何参数测试 ===")
    
    geo = persona.get_geometry_params()
    print(f"形状: {geo['shape']}")
    print(f"缩放: {geo['scale']:.2f}")
    print(f"旋转速度: {geo['rotation_speed']:.2f}")
    print(f"曲率: {geo['curvature']:.3f}")
    print(f"色调: {geo['color_hue']}")
    print(f"发光强度: {geo['glow_intensity']:.2f}")
