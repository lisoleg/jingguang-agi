# -*- coding: utf-8 -*-
"""
M96_CognitiveOffloadGuard — 认知卸载防范模块

定理 T41: "AGI提供的直接答案量与人类认知退化风险成正比，引导式交互可逆转该风险"

本模块评估人机交互中的认知卸载风险，建议引导式回复策略，
追踪用户认知负荷变化，并根据风险等级提供干预方案。
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional, Tuple


@dataclass
class InteractionRecord:
    """交互记录数据结构，记录单次人机交互的关键信息。"""
    timestamp: float
    is_direct_answer: bool
    cognitive_effort: float  # 0.0-1.0，用户在交互中的认知努力程度
    topic: str


@dataclass
class GuidedResponse:
    """引导式回复策略结构。"""
    strategy_type: str  # "socratic", "hint", "scaffold", "counter_question"
    guiding_questions: List[str]
    hint_level: int  # 1-5，提示级别
    expected_effort: float  # 预期用户认知努力度
    rationale: str  # 策略选择理由


@dataclass
class CognitiveLoadTrend:
    """认知负荷趋势数据。"""
    user_id: str
    current_load: float
    load_history: List[float]
    trend_direction: str  # "increasing", "decreasing", "stable"
    slope: float  # 线性回归斜率


@dataclass
class InterventionStrategy:
    """干预策略数据结构。"""
    risk_level: str  # "low", "medium", "high"
    description: str
    actions: List[str]
    guided_ratio_target: float  # 目标引导式交互比例
    max_direct_answers_per_session: int
    monitoring_frequency: float  # 监控频率（秒）


class CognitiveOffloadGuard:
    """
    认知卸载防范器，监控和防范AGI交互中人类认知退化的风险。

    基于定理T41，本模块通过评估直接答案比例、认知努力度等指标，
    实时监测认知卸载风险，并建议引导式交互策略以逆转风险。
    """

    # 风险等级阈值
    LOW_RISK_THRESHOLD: float = 0.3
    MEDIUM_RISK_THRESHOLD: float = 0.6

    # 历史窗口大小
    HISTORY_WINDOW_SIZE: int = 100

    def __init__(self) -> None:
        """初始化认知卸载防范器。"""
        self._lock: Lock = Lock()
        self._interaction_history: Dict[str, deque] = {}  # user_id -> deque of InteractionRecord
        self._cognitive_load_cache: Dict[str, CognitiveLoadTrend] = {}

        # 模块状态字段
        self.offload_risk_score: float = 0.0
        self.direct_answer_ratio: float = 0.0
        self.guided_ratio: float = 1.0
        self.intervention_count: int = 0
        self.cognitive_trend: str = "stable"

        # 话题认知努力度基线（不同话题的基线认知需求）
        self._topic_effort_baselines: Dict[str, float] = {}
        self._total_interactions: int = 0
        self._total_direct_answers: int = 0
        self._total_guided: int = 0

    def assess_offload_risk(self, interaction_history: List[InteractionRecord]) -> float:
        """
        评估当前交互的认知卸载风险。

        综合考量直接答案比例、用户认知努力度均值、努力度变化趋势等指标，
        输出0-1之间的风险评分。

        Args:
            interaction_history: 交互历史记录列表

        Returns:
            认知卸载风险评分，0.0表示无风险，1.0表示极高风险
        """
        if not interaction_history:
            return 0.0

        with self._lock:
            # 计算直接答案比例
            direct_count = sum(1 for r in interaction_history if r.is_direct_answer)
            total = len(interaction_history)
            direct_ratio = direct_count / total if total > 0 else 0.0

            # 计算平均认知努力度
            avg_effort = sum(r.cognitive_effort for r in interaction_history) / total

            # 计算认知努力度趋势（后半段 vs 前半段）
            mid = total // 2
            if mid > 0:
                first_half_effort = sum(r.cognitive_effort for r in interaction_history[:mid]) / mid
                second_half_effort = sum(r.cognitive_effort for r in interaction_history[mid:]) / (total - mid)
                effort_decline = max(0.0, first_half_effort - second_half_effort)
            else:
                effort_decline = 0.0

            # 综合风险评分：直接答案占比越高风险越大，认知努力越低风险越大，努力下降越多风险越大
            # 权重：直接答案比例40%，低认知努力30%，认知努力下降30%
            risk_from_direct = direct_ratio * 0.4
            risk_from_low_effort = (1.0 - avg_effort) * 0.3
            risk_from_decline = effort_decline * 0.3

            raw_risk = risk_from_direct + risk_from_low_effort + risk_from_decline

            # 应用sigmoid归一化到0-1范围
            risk_score = 1.0 / (1.0 + math.exp(-10.0 * (raw_risk - 0.5)))

            # 更新模块状态
            self.offload_risk_score = round(risk_score, 4)
            self.direct_answer_ratio = round(direct_ratio, 4)
            self.guided_ratio = round(1.0 - direct_ratio, 4)

            # 追踪统计
            self._total_interactions += total
            self._total_direct_answers += direct_count
            self._total_guided += total - direct_count

            return self.offload_risk_score

    def suggest_guided_response(self, query: str) -> GuidedResponse:
        """
        建议引导式回复策略，替代直接答案。

        基于当前风险等级和查询话题，选择最优的引导策略：
        - 苏格拉底式追问（socratic）：适合概念理解类问题
        - 提示引导（hint）：适合操作性/步骤类问题
        - 脚手架引导（scaffold）：适合复杂问题
        - 反问引导（counter_question）：适合假设性/推理性问题

        Args:
            query: 用户的查询文本

        Returns:
            引导式回复策略结构体
        """
        with self._lock:
            # 根据查询特征判断策略类型
            query_lower = query.lower()
            strategy_type = self._classify_query_strategy(query_lower)

            # 生成引导问题
            guiding_questions = self._generate_guiding_questions(query, strategy_type)

            # 根据当前风险等级调整提示级别
            if self.offload_risk_score < self.LOW_RISK_THRESHOLD:
                hint_level = 1  # 低风险，少提示
            elif self.offload_risk_score < self.MEDIUM_RISK_THRESHOLD:
                hint_level = 3  # 中风险，适度提示
            else:
                hint_level = 5  # 高风险，充分提示但避免直接答案

            # 预期认知努力度：高风险时期望更高努力
            expected_effort = min(1.0, 0.3 + self.offload_risk_score * 0.5)

            rationale = (
                f"当前风险评分={self.offload_risk_score:.2f}，"
                f"直接答案比例={self.direct_answer_ratio:.2f}，"
                f"策略类型={strategy_type}，"
                f"提示级别={hint_level}"
            )

            return GuidedResponse(
                strategy_type=strategy_type,
                guiding_questions=guiding_questions,
                hint_level=hint_level,
                expected_effort=expected_effort,
                rationale=rationale,
            )

    def _classify_query_strategy(self, query_lower: str) -> str:
        """根据查询文本特征分类策略类型。"""
        concept_keywords = ["为什么", "什么", "定义", "原理", "概念", "why", "what", "define"]
        procedural_keywords = ["如何", "怎么做", "步骤", "方法", "how", "step", "method"]
        complex_keywords = ["分析", "比较", "评估", "设计", "analyze", "compare", "evaluate"]
        hypothesis_keywords = ["如果", "假设", "假如", "推测", "if", "suppose", "assume"]

        if any(kw in query_lower for kw in concept_keywords):
            return "socratic"
        elif any(kw in query_lower for kw in procedural_keywords):
            return "hint"
        elif any(kw in query_lower for kw in complex_keywords):
            return "scaffold"
        elif any(kw in query_lower for kw in hypothesis_keywords):
            return "counter_question"
        else:
            # 默认使用苏格拉底式
            return "socratic"

    def _generate_guiding_questions(self, query: str, strategy_type: str) -> List[str]:
        """根据策略类型生成引导问题列表。"""
        templates: Dict[str, List[str]] = {
            "socratic": [
                f"关于这个问题，你目前有什么想法？",
                f"你能回忆起相关的哪些知识？",
                f"如果我们从另一个角度看，会有什么不同？",
            ],
            "hint": [
                f"可以先从最基础的部分开始思考",
                f"有没有类似的经验可以参考？",
                f"试试把问题分解成更小的步骤",
            ],
            "scaffold": [
                f"让我们先把问题的框架理清楚",
                f"你能列出关键的影响因素吗？",
                f"在这些因素中，哪个最重要？",
            ],
            "counter_question": [
                f"如果反过来想，结论会有什么变化？",
                f"有没有可能存在其他解释？",
                f"你的假设基础是什么？可以验证吗？",
            ],
        }
        return templates.get(strategy_type, templates["socratic"])

    def track_cognitive_load(self, user_id: str) -> CognitiveLoadTrend:
        """
        追踪用户认知负荷变化趋势。

        通过分析用户历史交互中的认知努力度变化，判断其认知负荷是
        增加还是减少，并计算趋势斜率。

        Args:
            user_id: 用户标识

        Returns:
            认知负荷趋势数据
        """
        with self._lock:
            if user_id not in self._interaction_history:
                # 初始化用户历史
                return CognitiveLoadTrend(
                    user_id=user_id,
                    current_load=0.5,
                    load_history=[],
                    trend_direction="stable",
                    slope=0.0,
                )

            records = list(self._interaction_history[user_id])
            if not records:
                return CognitiveLoadTrend(
                    user_id=user_id,
                    current_load=0.5,
                    load_history=[],
                    trend_direction="stable",
                    slope=0.0,
                )

            # 提取认知努力度序列
            efforts = [r.cognitive_effort for r in records]
            current_load = efforts[-1] if efforts else 0.5

            # 线性回归计算趋势斜率
            n = len(efforts)
            if n < 2:
                slope = 0.0
            else:
                x_mean = (n - 1) / 2.0
                y_mean = sum(efforts) / n
                numerator = sum((i - x_mean) * (efforts[i] - y_mean) for i in range(n))
                denominator = sum((i - x_mean) ** 2 for i in range(n))
                slope = numerator / denominator if denominator != 0 else 0.0

            # 判断趋势方向
            if slope > 0.01:
                trend_direction = "increasing"
            elif slope < -0.01:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"

            self.cognitive_trend = trend_direction

            trend = CognitiveLoadTrend(
                user_id=user_id,
                current_load=round(current_load, 4),
                load_history=[round(e, 4) for e in efforts[-20:]],  # 保留最近20条
                trend_direction=trend_direction,
                slope=round(slope, 6),
            )

            self._cognitive_load_cache[user_id] = trend
            return trend

    def get_intervention_strategy(self, risk_level: str) -> InterventionStrategy:
        """
        根据风险等级返回干预策略。

        提供低、中、高三档干预策略，分别对应不同的干预强度和
        引导式交互比例目标。

        Args:
            risk_level: 风险等级，"low"/"medium"/"high"

        Returns:
            干预策略数据结构

        Raises:
            ValueError: 当风险等级不是有效值时
        """
        valid_levels = ("low", "medium", "high")
        if risk_level not in valid_levels:
            raise ValueError(f"风险等级必须为 {valid_levels} 之一，收到: {risk_level}")

        with self._lock:
            self.intervention_count += 1

        strategies: Dict[str, InterventionStrategy] = {
            "low": InterventionStrategy(
                risk_level="low",
                description="低风险：继续当前交互模式，保持关注",
                actions=[
                    "维持当前引导式交互比例",
                    "定期检查认知努力度变化",
                    "在自然对话中穿插启发性问题",
                ],
                guided_ratio_target=0.5,
                max_direct_answers_per_session=20,
                monitoring_frequency=300.0,
            ),
            "medium": InterventionStrategy(
                risk_level="medium",
                description="中风险：增加引导式交互，减少直接答案",
                actions=[
                    "将引导式交互比例提升至目标水平",
                    "对每3次交互至少1次使用苏格拉底式追问",
                    "减少直接给出完整答案的频率",
                    "追踪认知努力度恢复情况",
                ],
                guided_ratio_target=0.7,
                max_direct_answers_per_session=10,
                monitoring_frequency=120.0,
            ),
            "high": InterventionStrategy(
                risk_level="high",
                description="高风险：强烈干预，暂停直接答案，强制引导式交互",
                actions=[
                    "暂停提供任何直接完整答案",
                    "所有回复均采用引导式策略",
                    "每次交互必须包含追问环节",
                    "记录认知努力度恢复情况",
                    "建议用户主动思考并验证理解",
                ],
                guided_ratio_target=0.95,
                max_direct_answers_per_session=3,
                monitoring_frequency=30.0,
            ),
        }

        return strategies[risk_level]

    def record_interaction(self, user_id: str, record: InteractionRecord) -> None:
        """
        记录一次交互，用于后续风险分析。

        Args:
            user_id: 用户标识
            record: 交互记录
        """
        with self._lock:
            if user_id not in self._interaction_history:
                self._interaction_history[user_id] = deque(
                    maxlen=self.HISTORY_WINDOW_SIZE
                )
            self._interaction_history[user_id].append(record)

    def get_state(self) -> Dict:
        """返回模块状态字典。"""
        with self._lock:
            return {
                "offload_risk_score": self.offload_risk_score,
                "direct_answer_ratio": self.direct_answer_ratio,
                "guided_ratio": self.guided_ratio,
                "intervention_count": self.intervention_count,
                "cognitive_trend": self.cognitive_trend,
                "total_interactions": self._total_interactions,
                "total_direct_answers": self._total_direct_answers,
                "total_guided": self._total_guided,
            }


# 单例模式
_instance: Optional[CognitiveOffloadGuard] = None


def get_instance() -> CognitiveOffloadGuard:
    """获取 CognitiveOffloadGuard 的全局单例实例。"""
    global _instance
    if _instance is None:
        _instance = CognitiveOffloadGuard()
    return _instance
