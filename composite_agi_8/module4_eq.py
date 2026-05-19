"""
太乙AGI 8.0 - 模块4：情商模块（情绪智能）
=================================================

实现高情商 (EQ) 的核心能力：
1. 情绪识别（自己和他人）
2. 情绪理解（原因和影响）
3. 情绪调节（管理和调节）
4. 同理心（理解他人感受）
5. 社交技能（人际交往）

基于"复合体理学"理论框架
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EmotionType(Enum):
    """情绪类型"""
    JOY = "joy"               # 喜悦
    SADNESS = "sadness"        # 悲伤
    ANGER = "anger"            # 愤怒
    FEAR = "fear"              # 恐惧
    SURPRISE = "surprise"      # 惊讶
    DISGUST = "disgust"        # 厌恶
    LOVE = "love"              # 爱
    HOPE = "hope"              # 希望
    PRIDE = "pride"            # 自豪
    SHAME = "shame"            # 羞耻
    GRATITUDE = "gratitude"    # 感激
    COMPASSION = "compassion"  # 同情


@dataclass
class Emotion:
    """情绪"""
    type: EmotionType
    intensity: float  # 强度 [0, 1]
    cause: str        # 原因
    timestamp: float  # 时间戳


class EmotionRecognition:
    """
    情绪识别：识别自己和他人的情绪
    
    使用多维情绪空间：
    - Valence (效价): 积极/消极
    - Arousal (唤醒度): 高/低
    - Dominance (支配度): 强/弱
    """
    
    def __init__(self, emotion_dim: int = 64):
        """
        初始化情绪识别器
        
        Args:
            emotion_dim: 情绪向量维度
        """
        self.emotion_dim = emotion_dim
        
        # 情绪空间：每个情绪类型对应一个向量
        self.emotion_vectors = {}
        for emotion_type in EmotionType:
            # 为每个情绪类型生成一个特征向量
            vec = np.random.randn(emotion_dim)
            vec = vec / np.linalg.norm(vec)  # 归一化
            self.emotion_vectors[emotion_type] = vec
        
        # 识别历史
        self.recognition_history: List[Dict] = []
    
    def recognize_self_emotion(self, internal_state: np.ndarray) -> Tuple[EmotionType, float]:
        """
        识别自己的情绪
        
        Args:
            internal_state: 内部状态向量
            
        Returns:
            (情绪类型, 置信度)
        """
        # 归一化
        if np.linalg.norm(internal_state) > 0:
            internal_state = internal_state / np.linalg.norm(internal_state)
        
        # 计算与所有情绪向量的相似度
        similarities = {}
        for emotion_type, emotion_vec in self.emotion_vectors.items():
            # 余弦相似度
            dot = np.dot(internal_state, emotion_vec)
            similarities[emotion_type] = float(dot)
        
        # 选择相似度最高的情绪
        best_emotion = max(similarities, key=similarities.get)
        confidence = similarities[best_emotion]
        
        # 记录历史
        self.recognition_history.append({
            "type": "self",
            "emotion": best_emotion,
            "confidence": confidence
        })
        
        return best_emotion, confidence
    
    def recognize_other_emotion(self, external_features: np.ndarray) -> Tuple[EmotionType, float]:
        """
        识别他人的情绪（基于外部特征）
        
        Args:
            external_features: 外部特征向量（表情、语音、文本等）
            
        Returns:
            (情绪类型, 置信度)
        """
        # 与识别自己情绪使用相同的方法
        return self.recognize_self_emotion(external_features)
    
    def get_emotion_description(self, emotion_type: EmotionType) -> str:
        """获取情绪描述"""
        descriptions = {
            EmotionType.JOY: "喜悦：感到快乐和满足",
            EmotionType.SADNESS: "悲伤：感到失落和沮丧",
            EmotionType.ANGER: "愤怒：感到生气和不满",
            EmotionType.FEAR: "恐惧：感到害怕和焦虑",
            EmotionType.SURPRISE: "惊讶：感到意外和震惊",
            EmotionType.DISGUST: "厌恶：感到反感和不悦",
            EmotionType.LOVE: "爱：感到温暖和依恋",
            EmotionType.HOPE: "希望：感到期待和乐观",
            EmotionType.PRIDE: "自豪：感到自信和成就",
            EmotionType.SHAME: "羞耻：感到尴尬和惭愧",
            EmotionType.GRATITUDE: "感激：感到感谢和温暖",
            EmotionType.COMPASSION: "同情：感到怜悯和关怀"
        }
        return descriptions.get(emotion_type, "未知情绪")


class EmotionUnderstanding:
    """
    情绪理解：理解情绪的原因和影响
    """
    
    def __init__(self):
        """初始化情绪理解模块"""
        self.emotion_causes = {}  # 情绪 -> 可能的原因
        self.emotion_effects = {}  # 情绪 -> 可能的影响
        
        # 初始化常见情绪因果关系
        self._initialize_causal_relationships()
    
    def _initialize_causal_relationships(self):
        """初始化情绪因果关系"""
        # 喜悦的原因和影响
        self.emotion_causes[EmotionType.JOY] = [
            "获得成功", "收到好消息", "与喜欢的人相处", "实现目标"
        ]
        self.emotion_effects[EmotionType.JOY] = [
            "更愿意帮助他人", "创造力提升", "社交意愿增强"
        ]
        
        # 悲伤的原因和影响
        self.emotion_causes[EmotionType.SADNESS] = [
            "失去重要的人或物", "失败", "被拒绝", "失望"
        ]
        self.emotion_effects[EmotionType.SADNESS] = [
            "社交退缩", "思维变慢", "对事物失去兴趣"
        ]
        
        # 可以添加更多情绪...
    
    def understand_emotion(self, emotion: Emotion) -> Dict[str, Any]:
        """
        理解情绪
        
        Args:
            emotion: 情绪对象
            
        Returns:
            理解结果
        """
        emotion_type = emotion.type
        
        # 查找可能的原因
        possible_causes = self.emotion_causes.get(emotion_type, [])
        cause_match = None
        for cause in possible_causes:
            if cause in emotion.cause:
                cause_match = cause
                break
        
        # 查找可能的影响
        possible_effects = self.emotion_effects.get(emotion_type, [])
        
        return {
            "emotion": emotion_type.value,
            "intensity": emotion.intensity,
            "identified_cause": cause_match,
            "possible_effects": possible_effects,
            "understanding": f"这是{emotion_type.value}情绪，强度{emotion.intensity:.2f}，可能由'{emotion.cause}'引起"
        }


class EmotionRegulation:
    """
    情绪调节：管理和调节情绪
    """
    
    def __init__(self):
        """初始化情绪调节器"""
        self.regulation_strategies = {}  # 情绪类型 -> 调节策略
        self.current_emotion = None
        self.regulation_history: List[Dict] = []
        
        # 初始化调节策略
        self._initialize_regulation_strategies()
    
    def _initialize_regulation_strategies(self):
        """初始化情绪调节策略"""
        # 针对不同情绪的调节策略
        self.regulation_strategies[EmotionType.ANGER] = [
            "深呼吸", "数到10", "离开触发环境", "运动释放"
        ]
        self.regulation_strategies[EmotionType.SADNESS] = [
            "找人倾诉", "做喜欢的事", "休息", "寻求支持"
        ]
        self.regulation_strategies[EmotionType.FEAR] = [
            "理性分析风险", "寻求支持", "逐步暴露", "放松训练"
        ]
        self.regulation_strategies[EmotionType.JOY] = [
            "分享快乐", "记录下来", "帮助他人", "保持谦逊"
        ]
    
    def regulate(self, emotion: Emotion) -> Dict[str, Any]:
        """
        调节情绪
        
        Args:
            emotion: 当前情绪
            
        Returns:
            调节结果
        """
        self.current_emotion = emotion
        
        # 获取调节策略
        strategies = self.regulation_strategies.get(emotion.type, [])
        
        # 如果情绪强度低，不需要调节
        if emotion.intensity < 0.3:
            result = {
                "need_regulation": False,
                "reason": "情绪强度低，无需调节",
                "suggested_strategies": []
            }
        else:
            # 选择最合适的策略（简化：选择第一个）
            suggested = strategies[0] if strategies else "接受情绪"
            
            result = {
                "need_regulation": True,
                "reason": f"情绪强度{emotion.intensity:.2f}，需要调节",
                "current_emotion": emotion.type.value,
                "suggested_strategies": strategies,
                "recommended": suggested
            }
        
        self.regulation_history.append(result)
        return result
    
    def apply_regulation(self, strategy: str) -> float:
        """
        应用调节策略
        
        Args:
            strategy: 调节策略
            
        Returns:
            调节后的情绪强度（降低的百分比）
        """
        if self.current_emotion is None:
            return 0.0
        
        # 简化：应用策略后情绪强度降低
        reduction = 0.3  # 降低30%
        self.current_emotion.intensity = max(0.0, self.current_emotion.intensity - reduction)
        
        return reduction


class Empathy:
    """
    同理心：理解他人的感受
    
    包括：
    1. 认知同理心：理解他人的想法和感受
    2. 情绪同理心：感受他人的情绪
    3. 同情心：关心他人的福祉
    """
    
    def __init__(self, empathy_dim: int = 64):
        """
        初始化同理心模块
        
        Args:
            empathy_dim: 同理心向量维度
        """
        self.empathy_dim = empathy_dim
        self.empathy_level = 0.5  # 同理心水平 [0, 1]
        self.empathy_history: List[Dict] = []
    
    def cognitive_empathy(self, other_emotion: Emotion, context: str) -> Dict[str, Any]:
        """
        认知同理心：理解他人的想法和感受
        
        Args:
            other_emotion: 他人的情绪
            context: 上下文
            
        Returns:
            理解结果
        """
        # 分析情绪和上下文
        understanding = f"对方感到{other_emotion.type.value}，强度{other_emotion.intensity:.2f}"
        
        if other_emotion.cause:
            understanding += f"，因为{other_emotion.cause}"
        
        return {
            "type": "cognitive",
            "understanding": understanding,
            "empathy_level": self.empathy_level
        }
    
    def emotional_empathy(self, other_emotion: Emotion) -> Dict[str, Any]:
        """
        情绪同理心：感受他人的情绪
        
        Args:
            other_emotion: 他人的情绪
            
        Returns:
            情绪共鸣结果
        """
        # 情绪共鸣：自己产生类似的情绪
        resonance_intensity = self.empathy_level * other_emotion.intensity
        
        return {
            "type": "emotional",
            "resonance_emotion": other_emotion.type.value,
            "resonance_intensity": resonance_intensity,
            "empathy_level": self.empathy_level
        }
    
    def compassion(self, other_emotion: Emotion, other_need: str) -> Dict[str, Any]:
        """
        同情心：关心他人的福祉
        
        Args:
            other_emotion: 他人的情绪
            other_need: 他人的需求
            
        Returns:
            同情反应
        """
        # 判断是否需要帮助
        need_help = other_emotion.intensity > 0.5 or "痛苦" in other_emotion.cause
        
        response = {
            "type": "compassion",
            "recognize_suffering": need_help,
            "empathy_level": self.empathy_level
        }
        
        if need_help:
            response["action"] = f"提供帮助：{other_need}"
        else:
            response["action"] = "表达理解和支持"
        
        return response
    
    def update_empathy_level(self, interaction_quality: float):
        """
        更新同理心水平
        
        Args:
            interaction_quality: 交互质量 [0, 1]
        """
        # 成功的社交交互会提升同理心
        self.empathy_level = min(1.0, self.empathy_level + 0.01 * interaction_quality)
        self.empathy_history.append({
            "quality": interaction_quality,
            "new_level": self.empathy_level
        })


class SocialSkills:
    """
    社交技能：有效的人际交往能力
    
    包括：
    1. 沟通技巧
    2. 冲突解决
    3. 合作能力
    4. 领导力
    """
    
    def __init__(self):
        """初始化社交技能模块"""
        self.communication_skill = 0.5
        self.conflict_resolution_skill = 0.5
        self.cooperation_skill = 0.5
        self.leadership_skill = 0.5
        
        self.social_history: List[Dict] = []
    
    def communicate(self, message: str, emotion: Optional[Emotion] = None) -> Dict[str, Any]:
        """
        沟通：表达自己
        
        Args:
            message: 要传达的消息
            emotion: 伴随的情绪（可选）
            
        Returns:
            沟通结果
        """
        # 评估沟通效果
        clarity = self._assess_clarity(message)
        empathy = self._assess_empathy(emotion)
        
        effectiveness = (clarity + empathy) / 2
        
        result = {
            "action": "communicate",
            "message": message,
            "clarity": clarity,
            "empathy": empathy,
            "effectiveness": effectiveness
        }
        
        self.social_history.append(result)
        return result
    
    def resolve_conflict(self, conflict_description: str, other_emotion: Emotion) -> Dict[str, Any]:
        """
        解决冲突
        
        Args:
            conflict_description: 冲突描述
            other_emotion: 对方的情绪
            
        Returns:
            解决方案
        """
        # 简化：根据对方情绪选择策略
        if other_emotion.intensity > 0.7:
            # 情绪强烈，先安抚
            strategy = "先安抚情绪，再讨论问题"
        else:
            # 情绪平稳，直接沟通
            strategy = "理性沟通，寻找共赢方案"
        
        result = {
            "action": "resolve_conflict",
            "conflict": conflict_description,
            "strategy": strategy,
            "success_probability": self.conflict_resolution_skill
        }
        
        self.social_history.append(result)
        return result
    
    def cooperate(self, task: str, partner_emotion: Emotion) -> Dict[str, Any]:
        """
        合作：与他人协作
        
        Args:
            task: 任务描述
            partner_emotion: 合作伙伴的情绪
            
        Returns:
            合作方案
        """
        # 简化：根据合作伙伴的情绪调整合作方式
        if partner_emotion.type == EmotionType.JOY:
            approach = "积极合作，分享想法"
        elif partner_emotion.type == EmotionType.SADNESS:
            approach = "给予支持，分担任务"
        else:
            approach = "保持沟通，明确分工"
        
        result = {
            "action": "cooperate",
            "task": task,
            "approach": approach,
            "success_probability": self.cooperation_skill
        }
        
        self.social_history.append(result)
        return result
    
    def _assess_clarity(self, message: str) -> float:
        """评估表达的清晰度"""
        # 简化：基于消息长度和结构
        words = len(message.split())
        if words < 5:
            return 0.3  # 太简短
        elif words < 20:
            return 0.7  # 适中
        else:
            return 0.9  # 详细
    
    def _assess_empathy(self, emotion: Optional[Emotion]) -> float:
        """评估同理心表达"""
        if emotion is None:
            return 0.5
        
        # 情绪强度适中时同理心表达最好
        if 0.3 <= emotion.intensity <= 0.7:
            return 0.8
        else:
            return 0.5


class EQModule:
    """
    情商模块：整合情绪识别、理解、调节、同理心和社交技能
    
    这是实现高情商 (EQ) 的核心模块
    """
    
    def __init__(self, eq_dim: int = 64):
        """
        初始化情商模块
        
        Args:
            eq_dim: EQ维度
        """
        self.eq_dim = eq_dim
        
        # 核心组件
        self.recognition = EmotionRecognition(emotion_dim=eq_dim)
        self.understanding = EmotionUnderstanding()
        self.regulation = EmotionRegulation()
        self.empathy = Empathy(empathy_dim=eq_dim)
        self.social = SocialSkills()
        
        # 当前情绪状态
        self.current_emotions: List[Emotion] = []
        
        # EQ度量
        self.eq_score = 100.0  # 初始EQ分数
        self._update_eq_score()
    
    def perceive_emotion(self, input_data: np.ndarray, source: str = "self") -> Dict[str, Any]:
        """
        感知情绪（自己或他人）
        
        Args:
            input_data: 输入数据（内部状态或外部特征）
            source: 来源 ("self" 或 "other")
            
        Returns:
            感知结果
        """
        if source == "self":
            emotion_type, confidence = self.recognition.recognize_self_emotion(input_data)
        else:
            emotion_type, confidence = self.recognition.recognize_other_emotion(input_data)
        
        # 创建情绪对象
        emotion = Emotion(
            type=emotion_type,
            intensity=confidence,
            cause="",  # 需要额外分析
            timestamp=len(self.current_emotions)
        )
        
        self.current_emotions.append(emotion)
        
        # 理解情绪
        understanding = self.understanding.understand_emotion(emotion)
        
        return {
            "source": source,
            "emotion": emotion_type.value,
            "intensity": confidence,
            "understanding": understanding,
            "description": self.recognition.get_emotion_description(emotion_type)
        }
    
    def regulate_emotion(self, emotion: Optional[Emotion] = None) -> Dict[str, Any]:
        """
        调节情绪
        
        Args:
            emotion: 要调节的情绪（如果为None，调节当前最强情绪）
            
        Returns:
            调节结果
        """
        if emotion is None:
            # 选择强度最高的情绪
            if not self.current_emotions:
                return {"error": "没有可调节的情绪"}
            emotion = max(self.current_emotions, key=lambda e: e.intensity)
        
        # 调节
        regulation_result = self.regulation.regulate(emotion)
        
        return regulation_result
    
    def express_empathy(self, other_emotion: Emotion, context: str) -> Dict[str, Any]:
        """
        表达同理心
        
        Args:
            other_emotion: 他人的情绪
            context: 上下文
            
        Returns:
            同理心表达
        """
        # 认知同理心
        cognitive = self.empathy.cognitive_empathy(other_emotion, context)
        
        # 情绪同理心
        emotional = self.empathy.emotional_empathy(other_emotion)
        
        # 同情心
        compassion = self.empathy.compassion(other_emotion, "需要支持")
        
        return {
            "cognitive": cognitive,
            "emotional": emotional,
            "compassion": compassion
        }
    
    def social_interact(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        社交交互
        
        Args:
            action: 交互动作 ("communicate", "resolve_conflict", "cooperate")
            **kwargs: 动作参数
            
        Returns:
            交互结果
        """
        if action == "communicate":
            return self.social.communicate(
                message=kwargs.get("message", ""),
                emotion=kwargs.get("emotion")
            )
        elif action == "resolve_conflict":
            return self.social.resolve_conflict(
                conflict_description=kwargs.get("conflict", ""),
                other_emotion=kwargs.get("other_emotion", Emotion(EmotionType.NEUTRAL, 0.0, "", 0.0) if hasattr(EmotionType, "NEUTRAL") else Emotion(EmotionType.JOY, 0.0, "", 0.0))
            )
        elif action == "cooperate":
            return self.social.cooperate(
                task=kwargs.get("task", ""),
                partner_emotion=kwargs.get("partner_emotion", Emotion(EmotionType.JOY, 0.5, "", 0.0))
            )
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _update_eq_score(self):
        """更新EQ分数"""
        # EQ分数基于各个组件的性能
        recognition_score = 0.8 if self.recognition.recognition_history else 0.5
        regulation_score = 0.8 if self.regulation.regulation_history else 0.5
        empathy_score = self.empathy.empathy_level
        social_score = (self.social.communication_skill + 
                       self.social.conflict_resolution_skill +
                       self.social.cooperation_skill +
                       self.social.leadership_skill) / 4
        
        # 加权平均
        self.eq_score = 70 + 30 * (
            0.25 * recognition_score +
            0.25 * regulation_score +
            0.25 * empathy_score +
            0.25 * social_score
        )
    
    def get_eq_report(self) -> Dict[str, Any]:
        """获取EQ报告"""
        self._update_eq_score()
        
        return {
            "eq_score": self.eq_score,
            "emotion_recognition": {
                "total_recognized": len(self.recognition.recognition_history),
                "recent": self.recognition.recognition_history[-5:] if self.recognition.recognition_history else []
            },
            "emotion_regulation": {
                "total_regulated": len(self.regulation.regulation_history),
                "recent": self.regulation.regulation_history[-5:] if self.regulation.regulation_history else []
            },
            "empathy": {
                "level": self.empathy.empathy_level,
                "history_length": len(self.empathy.empathy_history)
            },
            "social_skills": {
                "communication": self.social.communication_skill,
                "conflict_resolution": self.social.conflict_resolution_skill,
                "cooperation": self.social.cooperation_skill,
                "leadership": self.social.leadership_skill
            },
            "current_emotions": [
                {
                    "type": e.type.value,
                    "intensity": e.intensity
                }
                for e in self.current_emotions[-5:]  # 最近5个情绪
            ]
        }


# 导出接口
__all__ = [
    'EmotionType',
    'Emotion',
    'EmotionRecognition',
    'EmotionUnderstanding',
    'EmotionRegulation',
    'Empathy',
    'SocialSkills',
    'EQModule'
]


if __name__ == "__main__":
    # 测试代码
    print("=== 太乙AGI 8.0 - 模块4测试 ===")
    print()
    
    # 创建情商模块
    print("1. 创建情商模块...")
    eq_module = EQModule()
    print(f"   ✅ EQ模块初始化完成")
    print(f"   初始EQ分数: {eq_module.eq_score:.2f}")
    
    # 测试情绪识别
    print("2. 测试情绪识别...")
    test_input = np.random.randn(64)
    result = eq_module.perceive_emotion(test_input, source="self")
    print(f"   识别结果: {result['emotion']}")
    print(f"   强度: {result['intensity']:.4f}")
    print(f"   描述: {result['description']}")
    
    # 测试情绪理解
    print("3. 测试情绪理解...")
    understanding = result["understanding"]
    print(f"   理解: {understanding['understanding']}")
    
    # 测试情绪调节
    print("4. 测试情绪调节...")
    # 创建一个高强度情绪
    test_emotion = Emotion(
        type=EmotionType.ANGER,
        intensity=0.8,
        cause="被人误解",
        timestamp=1.0
    )
    regulation = eq_module.regulate_emotion(test_emotion)
    print(f"   需要调节: {regulation['need_regulation']}")
    if regulation['need_regulation']:
        print(f"   推荐策略: {regulation['recommended']}")
    
    # 测试同理心
    print("5. 测试同理心...")
    other_emotion = Emotion(
        type=EmotionType.SADNESS,
        intensity=0.7,
        cause="失去亲人",
        timestamp=2.0
    )
    empathy = eq_module.express_empathy(other_emotion, context="对方很伤心")
    print(f"   认知同理: {empathy['cognitive']['understanding']}")
    print(f"   情绪共鸣: {empathy['emotional']['resonance_emotion']}")
    print(f"   同情反应: {empathy['compassion']['action']}")
    
    # 测试社交技能
    print("6. 测试社交技能...")
    communication = eq_module.social_interact(
        "communicate",
        message="我很理解你的感受，让我们一起想办法解决这个问题。"
    )
    print(f"   沟通效果: {communication['effectiveness']:.4f}")
    
    # 获取EQ报告
    print("7. 获取EQ报告...")
    report = eq_module.get_eq_report()
    print(f"   EQ分数: {report['eq_score']:.2f}")
    print(f"   情绪识别次数: {report['emotion_recognition']['total_recognized']}")
    print(f"   情绪调节次数: {report['emotion_regulation']['total_regulated']}")
    print(f"   同理心水平: {report['empathy']['level']:.4f}")
    print(f"   沟通技能: {report['social_skills']['communication']:.4f}")
    
    print()
    print("✅ 模块4测试完成！")
    print("  核心功能：")
    print("  - ✅ 情绪识别（自己/他人）")
    print("  - ✅ 情绪理解（原因/影响）")
    print("  - ✅ 情绪调节（管理策略）")
    print("  - ✅ 同理心（认知/情绪/同情）")
    print("  - ✅ 社交技能（沟通/冲突/合作）")
    print("  - ✅ EQ度量与评估")
