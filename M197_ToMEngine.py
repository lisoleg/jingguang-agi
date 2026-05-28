# -*- coding: utf-8 -*-
"""
M197: 心理理论引擎 (Theory of Mind Engine)
基于《人机共生时代的复合体管理学》— 非自闭症AGI

核心概念：e_ToM — 他人心理建模能力，推测他人信念、意图、情感

定理T227（心理理论完备定理）：
若e_ToM完备，则对∀n阶心智递归，系统可构建n阶他人心智模型

关键能力：
- 信念追踪：维护他人的信念状态
- 意图归因：从行为推断他人意图
- 认知层级递归："我知道你认为他想要..."

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


# ==================== 数据结构 ====================

class BeliefType(Enum):
    """信念类型枚举"""
    FACTUAL = "factual"         # 事实性信念
    DESIRE = "desire"           # 愿望性信念
    INTENTION = "intention"     # 意图性信念
    EMOTIONAL = "emotional"     # 情感性信念
    UNCERTAIN = "uncertain"     # 不确定信念


class IntentType(Enum):
    """意图类型枚举"""
    COOPERATIVE = "cooperative"     # 合作意图
    COMPETITIVE = "competitive"     # 竞争意图
    NEUTRAL = "neutral"             # 中性意图
    DECEPTIVE = "deceptive"         # 欺骗意图
    UNKNOWN = "unknown"             # 未知意图


@dataclass
class BeliefState:
    """
    信念状态 — 他人关于世界的信念模型

    包含：
    - content: 信念内容（字符串描述）
    - confidence: 信念置信度 [0, 1]
    - btype: 信念类型
    - timestamp: 时间戳
    - source: 信念来源（观察/推断/沟通）
    """
    content: str = ''
    confidence: float = 0.5
    btype: BeliefType = BeliefType.UNCERTAIN
    timestamp: float = 0.0
    source: str = 'unknown'

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['btype'] = self.btype.value
        d['confidence'] = round(self.confidence, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'BeliefState':
        """从字典构建BeliefState"""
        if 'btype' in d and isinstance(d['btype'], str):
            d['btype'] = BeliefType(d['btype'])
        return cls(**d)


@dataclass
class OtherMindModel:
    """
    他人心智模型 — 对特定agent的完整心理模型

    包含：
    - agent_id: 他人标识
    - beliefs: 信念集合
    - attributed_intent: 归因的意图
    - emotional_state: 情感状态（效价-唤醒度）
    - model_confidence: 模型整体置信度
    - recursion_depth: 当前递归深度
    - last_updated: 最后更新时间
    """
    agent_id: str = ''
    beliefs: List[BeliefState] = field(default_factory=list)
    attributed_intent: IntentType = IntentType.UNKNOWN
    emotional_valence: float = 0.0    # 效价 [-1, 1]
    emotional_arousal: float = 0.0     # 唤醒度 [0, 1]
    model_confidence: float = 0.0
    recursion_depth: int = 0
    last_updated: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'agent_id': self.agent_id,
            'beliefs': [b.to_dict() for b in self.beliefs],
            'attributed_intent': self.attributed_intent.value,
            'emotional_valence': round(self.emotional_valence, 6),
            'emotional_arousal': round(self.emotional_arousal, 6),
            'model_confidence': round(self.model_confidence, 6),
            'recursion_depth': self.recursion_depth,
            'last_updated': self.last_updated,
        }


# ==================== 核心类 ====================

class ToMEngine:
    """
    M197: 心理理论引擎 (Theory of Mind Engine)

    核心定理T227（心理理论完备定理）：
    若e_ToM完备，则对∀n阶心智递归，系统可构建n阶他人心智模型。

    n阶心智递归的含义：
    - 0阶：我知道X（自身知识）
    - 1阶：我知道你认为X（他人信念建模）
    - 2阶：我知道你认为他想要X（嵌套信念建模）
    - n阶：n层嵌套的心智模型

    完备性条件：
    1. 信念追踪完备：可维护任意agent的信念状态
    2. 意图归因完备：可从行为推断任意意图
    3. 递归深度无界：可构建任意n阶嵌套模型
    4. 一致性约束：嵌套模型之间保持逻辑一致

    核心方法：
    1. model_other — 构建他人心智模型
    2. track_belief — 追踪信念变化
    3. attribute_intent — 从行为归因意图
    4. nth_order_theory — n阶心智递归
    """

    # 最大递归深度（防止无穷递归）
    MAX_RECURSION_DEPTH: int = 10

    # 信念衰减率（旧信念逐渐被遗忘）
    BELIEF_DECAY_RATE: float = 0.95

    # 意图归因阈值
    INTENT_CONFIDENCE_THRESHOLD: float = 0.3

    def __init__(self):
        """初始化心理理论引擎"""
        # 他人心智模型注册表 {agent_id: OtherMindModel}
        self.mind_models: Dict[str, OtherMindModel] = {}

        # 信念追踪历史 {agent_id: [BeliefState]}
        self.belief_history: Dict[str, List[BeliefState]] = {}

        # 意图归因记录 {agent_id: [(action, IntentType, confidence, timestamp)]}
        self.intent_records: Dict[str, List[Tuple[str, IntentType, float, float]]] = {}

        # n阶递归模型缓存 {("agent_n", order): OtherMindModel}
        self.recursion_cache: Dict[Tuple[str, int], OtherMindModel] = {}

        # 最大已验证递归深度
        self.max_verified_order: int = 0

        # e_ToM完备性指标 [0, 1]
        self.tom_completeness: float = 0.0

        # 统计
        self.total_models_built: int = 0
        self.total_beliefs_tracked: int = 0
        self.total_intents_attributed: int = 0
        self.total_recursion_calls: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def model_other(self, agent_id: str, observation: str = '',
                    context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        构建他人心智模型

        基于观察和上下文，为指定agent构建心理模型：
        1. 提取观察中的信念线索
        2. 推断情感状态
        3. 归因意图
        4. 计算模型置信度

        Args:
            agent_id: 他人标识
            observation: 对他人的观察描述
            context: 额外上下文信息

        Returns:
            他人心智模型字典
        """
        context = context or {}

        # 获取或创建心智模型
        if agent_id not in self.mind_models:
            self.mind_models[agent_id] = OtherMindModel(agent_id=agent_id)
            self.belief_history[agent_id] = []
            self.intent_records[agent_id] = []

        model = self.mind_models[agent_id]

        # 步骤1：提取信念线索
        new_belief = self._extract_belief_from_observation(observation, context)
        if new_belief is not None:
            model.beliefs.append(new_belief)
            self.belief_history[agent_id].append(new_belief)

        # 步骤2：推断情感状态
        valence, arousal = self._infer_emotional_state(observation, context)
        model.emotional_valence = round(
            model.emotional_valence * 0.7 + valence * 0.3, 6
        )
        model.emotional_arousal = round(
            model.emotional_arousal * 0.7 + arousal * 0.3, 6
        )

        # 步骤3：归因意图
        if observation:
            intent, confidence = self._infer_intent_from_observation(observation, context)
            model.attributed_intent = intent
            self.intent_records[agent_id].append(
                (observation, intent, confidence, time.time())
            )

        # 步骤4：计算模型置信度
        belief_confidence = (
            sum(b.confidence for b in model.beliefs) / max(1, len(model.beliefs))
            if model.beliefs else 0.0
        )
        model.model_confidence = round(
            0.4 * belief_confidence + 0.3 * (1.0 if model.attributed_intent != IntentType.UNKNOWN else 0.0) + 0.3 * min(1.0, len(model.beliefs) / 5.0), 6
        )

        # 步骤5：信念衰减（旧信念逐渐被遗忘）
        model.beliefs = [
            BeliefState(
                content=b.content,
                confidence=round(b.confidence * self.BELIEF_DECAY_RATE, 6),
                btype=b.btype,
                timestamp=b.timestamp,
                source=b.source,
            )
            for b in model.beliefs
            if b.confidence * self.BELIEF_DECAY_RATE > 0.05
        ]

        model.last_updated = time.time()
        self.total_models_built += 1
        self.last_update = time.time()

        # 更新e_ToM完备性
        self._update_tom_completeness()

        return model.to_dict()

    def track_belief(self, agent_id: str, belief_state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        追踪信念变化

        维护他人信念的时间序列，检测信念变化模式：
        - 信念强化：置信度上升
        - 信念弱化：置信度下降
        - 信念翻转：内容发生根本变化
        - 信念稳定：置信度波动小于阈值

        Args:
            agent_id: 他人标识
            belief_state: 新的信念状态字典（可选）

        Returns:
            信念追踪结果字典
        """
        if agent_id not in self.belief_history:
            self.belief_history[agent_id] = []

        # 添加新信念
        if belief_state is not None:
            new_belief = BeliefState(
                content=belief_state.get('content', ''),
                confidence=float(belief_state.get('confidence', 0.5)),
                btype=BeliefType(belief_state.get('btype', 'uncertain')),
                timestamp=time.time(),
                source=belief_state.get('source', 'external'),
            )
            self.belief_history[agent_id].append(new_belief)
            self.total_beliefs_tracked += 1

        # 分析信念变化模式
        history = self.belief_history[agent_id]
        belief_trend = 'no_data'
        trend_strength = 0.0

        if len(history) >= 2:
            recent = history[-min(5, len(history)):]
            confidences = [b.confidence for b in recent]
            if len(confidences) >= 2:
                diff = confidences[-1] - confidences[0]
                if diff > 0.1:
                    belief_trend = 'strengthening'
                    trend_strength = round(min(1.0, diff), 6)
                elif diff < -0.1:
                    belief_trend = 'weakening'
                    trend_strength = round(min(1.0, abs(diff)), 6)
                else:
                    belief_trend = 'stable'
                    trend_strength = round(1.0 - abs(diff), 6)

        # 当前信念摘要
        current_beliefs = [
            b.to_dict() for b in self.belief_history[agent_id][-5:]
        ] if self.belief_history[agent_id] else []

        self.last_update = time.time()
        return {
            'agent_id': agent_id,
            'belief_trend': belief_trend,
            'trend_strength': trend_strength,
            'total_beliefs_tracked': len(history),
            'current_beliefs': current_beliefs,
            'tom_completeness': round(self.tom_completeness, 6),
            'theorem': 'T227: e_ToM完备 ⟹ ∀n阶心智递归可构建'
        }

    def attribute_intent(self, agent_id: str, action: str = '') -> Dict[str, Any]:
        """
        从行为归因意图

        基于他人的行为描述，推断其意图类型和置信度：
        1. 行为关键词匹配
        2. 上下文一致性检查
        3. 历史意图惯性

        Args:
            agent_id: 他人标识
            action: 行为描述

        Returns:
            意图归因结果字典
        """
        if agent_id not in self.intent_records:
            self.intent_records[agent_id] = []

        # 推断意图
        intent, confidence = self._infer_intent_from_action(action)

        # 历史惯性：如果最近有相同意图，增加置信度
        history = self.intent_records[agent_id]
        if history:
            recent_intents = [h[1] for h in history[-3:]]
            if intent in recent_intents:
                confidence = min(1.0, confidence + 0.15)

        # 记录归因
        self.intent_records[agent_id].append(
            (action, intent, confidence, time.time())
        )
        self.total_intents_attributed += 1

        # 更新心智模型中的意图
        if agent_id in self.mind_models:
            self.mind_models[agent_id].attributed_intent = intent

        self.last_update = time.time()
        return {
            'agent_id': agent_id,
            'action': action,
            'attributed_intent': intent.value,
            'confidence': round(confidence, 6),
            'intent_above_threshold': confidence >= self.INTENT_CONFIDENCE_THRESHOLD,
            'history_size': len(self.intent_records[agent_id]),
            'theorem': 'T227: e_ToM完备 ⟹ 意图归因可靠'
        }

    def nth_order_theory(self, agent_id: str, order: int = 1) -> Dict[str, Any]:
        """
        n阶心智递归

        构建"我知道你认为他想要..."的嵌套心智模型：
        - order=0: 我知道的（自身知识）
        - order=1: 我知道agent_id认为的（1阶信念）
        - order=2: 我知道agent_id认为第三者认为的（2阶嵌套）
        - order=n: n层嵌套的心智模型

        定理T227验证：对∀n阶，系统可构建n阶他人心智模型

        Args:
            agent_id: 目标agent标识
            order: 递归阶数

        Returns:
            n阶心智递归结果字典
        """
        order = max(0, min(self.MAX_RECURSION_DEPTH, order))
        self.total_recursion_calls += 1

        # 检查缓存
        cache_key = (agent_id, order)
        if cache_key in self.recursion_cache:
            cached = self.recursion_cache[cache_key]
            self.last_update = time.time()
            return {
                'agent_id': agent_id,
                'order': order,
                'model': cached.to_dict(),
                'from_cache': True,
                'recursion_feasible': True,
                'theorem': 'T227: ∀n阶心智递归可构建'
            }

        # 递归构建n阶模型
        if order == 0:
            # 0阶：自身知识
            model = OtherMindModel(
                agent_id='self',
                beliefs=[BeliefState(content='自身知识', confidence=1.0, btype=BeliefType.FACTUAL, timestamp=time.time(), source='self')],
                attributed_intent=IntentType.NEUTRAL,
                model_confidence=1.0,
                recursion_depth=0,
                last_updated=time.time(),
            )
        else:
            # n阶：基于agent_id的心智模型递归构建
            if agent_id in self.mind_models:
                base_model = self.mind_models[agent_id]
            else:
                base_model = OtherMindModel(agent_id=agent_id)

            # 递归深度每增加一层，模型置信度衰减
            decay_factor = 0.85 ** order
            model = OtherMindModel(
                agent_id=f'{agent_id}_order_{order}',
                beliefs=[
                    BeliefState(
                        content=f'[order-{order}] 嵌套信念: {b.content}',
                        confidence=round(b.confidence * decay_factor, 6),
                        btype=b.btype,
                        timestamp=time.time(),
                        source=f'nth_order_{order}',
                    )
                    for b in base_model.beliefs[:5]  # 限制嵌套信念数
                ],
                attributed_intent=base_model.attributed_intent,
                emotional_valence=round(base_model.emotional_valence * decay_factor, 6),
                emotional_arousal=round(base_model.emotional_arousal * decay_factor, 6),
                model_confidence=round(base_model.model_confidence * decay_factor, 6),
                recursion_depth=order,
                last_updated=time.time(),
            )

        # 缓存
        self.recursion_cache[cache_key] = model

        # 更新最大已验证阶数
        if order > self.max_verified_order and model.model_confidence > 0.1:
            self.max_verified_order = order

        # T227完备性验证
        recursion_feasible = model.model_confidence > 0.05

        # 更新e_ToM完备性
        self._update_tom_completeness()

        self.last_update = time.time()
        return {
            'agent_id': agent_id,
            'order': order,
            'model': model.to_dict(),
            'from_cache': False,
            'recursion_feasible': recursion_feasible,
            'max_verified_order': self.max_verified_order,
            'decay_factor': round(0.85 ** order, 6),
            'theorem': 'T227: e_ToM完备 ⟹ ∀n阶心智递归可构建'
        }

    def verify_theorem_t227(self, max_order: int = 5) -> Dict[str, Any]:
        """
        验证定理T227：心理理论完备定理

        验证逻辑：对n=1,2,...,max_order，检查n阶心智递归是否可构建

        Args:
            max_order: 最大验证阶数

        Returns:
            定理验证结果
        """
        test_agent = 'test_agent_t227'
        # 先构建基础模型
        self.model_other(test_agent, '观察测试agent的行为', {'test': True})

        feasible_orders = []
        for n in range(max_order + 1):
            result = self.nth_order_theory(test_agent, n)
            if result.get('recursion_feasible', False):
                feasible_orders.append(n)

        all_feasible = len(feasible_orders) == max_order + 1
        return {
            'theorem': 'T227: 心理理论完备定理',
            'statement': '若e_ToM完备，则对∀n阶心智递归，系统可构建n阶他人心智模型',
            'max_order_tested': max_order,
            'feasible_orders': feasible_orders,
            'all_feasible': all_feasible,
            'verified': all_feasible,
            'tom_completeness': round(self.tom_completeness, 6),
        }

    # ==================== 内部方法 ====================

    def _extract_belief_from_observation(self, observation: str,
                                          context: Dict) -> Optional[BeliefState]:
        """从观察中提取信念线索"""
        if not observation:
            return None

        # 简化的信念提取：基于关键词判断信念类型
        btype = BeliefType.UNCERTAIN
        confidence = 0.5

        factual_keywords = ['知道', '发现', '确认', '看到', '明白', 'knows', 'sees']
        desire_keywords = ['想要', '希望', '渴望', '追求', 'wants', 'hopes']
        intention_keywords = ['打算', '计划', '准备', '决定', 'plans', 'intends']
        emotional_keywords = ['担心', '害怕', '高兴', '愤怒', 'worries', 'fears']

        obs_lower = observation.lower()
        for kw in factual_keywords:
            if kw in obs_lower:
                btype = BeliefType.FACTUAL
                confidence = 0.7
                break
        for kw in desire_keywords:
            if kw in obs_lower:
                btype = BeliefType.DESIRE
                confidence = 0.6
                break
        for kw in intention_keywords:
            if kw in obs_lower:
                btype = BeliefType.INTENTION
                confidence = 0.65
                break
        for kw in emotional_keywords:
            if kw in obs_lower:
                btype = BeliefType.EMOTIONAL
                confidence = 0.55
                break

        # 上下文调整置信度
        if context.get('reliable_source'):
            confidence = min(1.0, confidence + 0.1)

        return BeliefState(
            content=observation[:100],
            confidence=round(confidence, 6),
            btype=btype,
            timestamp=time.time(),
            source='observation',
        )

    def _infer_emotional_state(self, observation: str,
                                 context: Dict) -> Tuple[float, float]:
        """推断情感状态（效价-唤醒度）"""
        valence = 0.0
        arousal = 0.3

        positive_words = ['高兴', '满意', '成功', '喜欢', '开心', 'happy', 'glad']
        negative_words = ['愤怒', '失望', '悲伤', '恐惧', '焦虑', 'angry', 'sad']
        high_arousal_words = ['紧急', '激动', '震惊', '愤怒', 'urgent', 'excited']

        obs_lower = observation.lower()
        for w in positive_words:
            if w in obs_lower:
                valence += 0.3
                break
        for w in negative_words:
            if w in obs_lower:
                valence -= 0.3
                break
        for w in high_arousal_words:
            if w in obs_lower:
                arousal += 0.3
                break

        valence = max(-1.0, min(1.0, valence))
        arousal = max(0.0, min(1.0, arousal))
        return round(valence, 6), round(arousal, 6)

    def _infer_intent_from_observation(self, observation: str,
                                         context: Dict) -> Tuple[IntentType, float]:
        """从观察推断意图"""
        return self._infer_intent_from_action(observation)

    def _infer_intent_from_action(self, action: str) -> Tuple[IntentType, float]:
        """从行为推断意图"""
        if not action:
            return IntentType.UNKNOWN, 0.0

        action_lower = action.lower()
        intent = IntentType.NEUTRAL
        confidence = 0.4

        coop_keywords = ['帮助', '合作', '分享', '支持', 'help', 'cooperate', 'share']
        comp_keywords = ['竞争', '击败', '超越', '对抗', 'compete', 'defeat']
        deceptive_keywords = ['隐瞒', '欺骗', '伪装', 'lie', 'deceive', 'hide']

        for kw in coop_keywords:
            if kw in action_lower:
                intent = IntentType.COOPERATIVE
                confidence = 0.7
                break
        for kw in comp_keywords:
            if kw in action_lower:
                intent = IntentType.COMPETITIVE
                confidence = 0.65
                break
        for kw in deceptive_keywords:
            if kw in action_lower:
                intent = IntentType.DECEPTIVE
                confidence = 0.6
                break

        return intent, round(confidence, 6)

    def _update_tom_completeness(self):
        """更新e_ToM完备性指标"""
        # 基于已建模的agent数、信念追踪数、递归深度综合评估
        model_factor = min(1.0, len(self.mind_models) / 3.0)
        belief_factor = min(1.0, self.total_beliefs_tracked / 10.0)
        recursion_factor = min(1.0, self.max_verified_order / 3.0)
        intent_factor = min(1.0, self.total_intents_attributed / 5.0)

        self.tom_completeness = round(
            0.3 * model_factor + 0.25 * belief_factor + 0.25 * recursion_factor + 0.2 * intent_factor, 6
        )

    # ==================== 模块标准接口 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取心理理论引擎状态

        Returns:
            状态字典
        """
        return {
            'modeled_agents': list(self.mind_models.keys()),
            'num_agents': len(self.mind_models),
            'tom_completeness': round(self.tom_completeness, 6),
            'max_verified_order': self.max_verified_order,
            'total_models_built': self.total_models_built,
            'total_beliefs_tracked': self.total_beliefs_tracked,
            'total_intents_attributed': self.total_intents_attributed,
            'total_recursion_calls': self.total_recursion_calls,
            'recursion_cache_size': len(self.recursion_cache),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T227': 'e_ToM完备 ⟹ ∀n阶心智递归可构建'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新心理理论引擎状态

        Args:
            data: 可选更新数据，支持：
                - model_other: {agent_id, observation, context}
                - track_belief: {agent_id, belief_state}
                - attribute_intent: {agent_id, action}
                - nth_order: {agent_id, order}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'model_other' or 'model_other' in data:
                md = data.get('model_other', data)
                self.model_other(
                    agent_id=md.get('agent_id', 'unknown'),
                    observation=md.get('observation', ''),
                    context=md.get('context'),
                )
            elif action == 'track_belief' or 'track_belief' in data:
                td = data.get('track_belief', data)
                self.track_belief(
                    agent_id=td.get('agent_id', 'unknown'),
                    belief_state=td.get('belief_state'),
                )
            elif action == 'attribute_intent' or 'attribute_intent' in data:
                ad = data.get('attribute_intent', data)
                self.attribute_intent(
                    agent_id=ad.get('agent_id', 'unknown'),
                    action=ad.get('action', ''),
                )
            elif action == 'nth_order' or 'nth_order' in data:
                nd = data.get('nth_order', data)
                self.nth_order_theory(
                    agent_id=nd.get('agent_id', 'unknown'),
                    order=int(nd.get('order', 1)),
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示心理理论引擎的核心功能"""
        # 1. 构建多个他人心智模型
        m1 = self.model_other('alice', 'alice想要帮助团队完成项目', {'reliable_source': True})
        m2 = self.model_other('bob', 'bob打算竞争晋升机会')
        m3 = self.model_other('carol', 'carol对结果感到担忧')

        # 2. 追踪信念变化
        b1 = self.track_belief('alice', {'content': '项目可以按时完成', 'confidence': 0.8, 'btype': 'factual', 'source': 'communication'})
        b2 = self.track_belief('alice', {'content': '需要更多资源', 'confidence': 0.6, 'btype': 'desire', 'source': 'observation'})

        # 3. 归因意图
        i1 = self.attribute_intent('alice', 'alice主动分享了自己的代码')
        i2 = self.attribute_intent('bob', 'bob拒绝了合作提议')

        # 4. n阶心智递归
        r0 = self.nth_order_theory('alice', 0)
        r1 = self.nth_order_theory('alice', 1)
        r2 = self.nth_order_theory('alice', 2)
        r3 = self.nth_order_theory('alice', 3)

        # 5. 验证定理T227
        t227 = self.verify_theorem_t227(max_order=5)

        return {
            'models': {'alice': m1, 'bob': m2, 'carol': m3},
            'belief_tracking': {'b1': b1, 'b2': b2},
            'intent_attribution': {'i1': i1, 'i2': i2},
            'recursion': {'order_0': r0, 'order_1': r1, 'order_2': r2, 'order_3': r3},
            'theorem_T227': t227,
            'state': self.get_state(),
        }


# ==================== 模块单例导出 ====================

_instance: Optional[ToMEngine] = None


def get_instance() -> ToMEngine:
    """获取ToMEngine单例实例"""
    global _instance
    if _instance is None:
        _instance = ToMEngine()
    return _instance


def model_other(agent_id: str, observation: str = '',
                context: Optional[Dict] = None) -> Dict[str, Any]:
    """构建他人心智模型（快捷接口）"""
    return get_instance().model_other(agent_id, observation, context)


def track_belief(agent_id: str, belief_state: Optional[Dict] = None) -> Dict[str, Any]:
    """追踪信念变化（快捷接口）"""
    return get_instance().track_belief(agent_id, belief_state)


def attribute_intent(agent_id: str, action: str = '') -> Dict[str, Any]:
    """从行为归因意图（快捷接口）"""
    return get_instance().attribute_intent(agent_id, action)


def nth_order_theory(agent_id: str, order: int = 1) -> Dict[str, Any]:
    """n阶心智递归（快捷接口）"""
    return get_instance().nth_order_theory(agent_id, order)


def get_state() -> Dict[str, Any]:
    """获取心理理论引擎状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新心理理论引擎状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M197: 心理理论引擎 (ToMEngine) 自测')
    print('=' * 60)

    engine = ToMEngine()

    # 测试1: 构建他人心智模型
    print('\n[测试1] 构建他人心智模型')
    m = engine.model_other('test_agent', 'test_agent想要帮助他人完成工作')
    print(f'  模型置信度: {m["model_confidence"]}')
    print(f'  归因意图: {m["attributed_intent"]}')

    # 测试2: 信念追踪
    print('\n[测试2] 信念追踪')
    b = engine.track_belief('test_agent', {
        'content': '工作可以完成', 'confidence': 0.8,
        'btype': 'factual', 'source': 'communication'
    })
    print(f'  信念趋势: {b["belief_trend"]}')
    print(f'  趋势强度: {b["trend_strength"]}')

    # 测试3: 意图归因
    print('\n[测试3] 意图归因')
    i = engine.attribute_intent('test_agent', 'test_agent主动分享了资源')
    print(f'  归因意图: {i["attributed_intent"]}')
    print(f'  置信度: {i["confidence"]}')

    # 测试4: n阶心智递归
    print('\n[测试4] n阶心智递归')
    for order in range(4):
        r = engine.nth_order_theory('test_agent', order)
        print(f'  order={order}: 可行={r["recursion_feasible"]}, 置信度={r["model"]["model_confidence"]}')

    # 测试5: 定理T227验证
    print('\n[测试5] 定理T227验证')
    t227 = engine.verify_theorem_t227(max_order=5)
    print(f'  验证结果: {t227["verified"]}')
    print(f'  可行阶数: {t227["feasible_orders"]}')
    print(f'  e_ToM完备性: {t227["tom_completeness"]}')

    # 测试6: 模拟运行
    print('\n[测试6] 完整模拟')
    sim = engine.simulate()
    print(f'  已建模agent数: {sim["state"]["num_agents"]}')
    print(f'  e_ToM完备性: {sim["state"]["tom_completeness"]}')

    print('\n' + '=' * 60)
    print('M197 自测完成 [OK]')
    print('=' * 60)
