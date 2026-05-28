# -*- coding: utf-8 -*-
"""
M98_ConfidenceDisclosure — 置信度披露模块

定理 T43: "主动披露不确定性比隐瞒不确定性更能建立长期信任"

本模块计算回复置信度、披露不确定性信息、校准置信度
并格式化置信度声明，以建立长期人机信任关系。
"""

from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque, Dict, List, Optional, Tuple


@dataclass
class ConfidenceRecord:
    """置信度记录数据结构。"""
    topic: str
    confidence: float  # 0-1
    evidence_count: int  # 支撑证据数量
    calibration_offset: float  # 校准偏移量
    timestamp: float


@dataclass
class UncertaintyDisclosure:
    """不确定性披露信息。"""
    topic: str
    confidence: float
    uncertainty_level: str  # "low", "moderate", "high", "very_high"
    missing_information: List[str]
    alternative_possibilities: List[str]
    recommendation: str


@dataclass
class CalibrationEntry:
    """校准历史条目。"""
    predicted_confidence: float
    actual_accuracy: bool
    topic: str
    timestamp: float


class ConfidenceDisclosure:
    """
    置信度披露器，负责计算、校准和披露回复的置信度。

    基于定理T43，主动披露不确定性可以建立长期信任。本模块
    通过多因素置信度计算、基于历史准确率的校准、以及分层
    不确定性披露来实现这一目标。
    """

    # 置信度等级阈值
    CONFIDENCE_LEVELS: Dict[str, Tuple[float, float]] = {
        "very_high": (0.95, 1.01),
        "high": (0.8, 0.95),
        "moderate": (0.6, 0.8),
        "low": (0.4, 0.6),
        "very_low": (0.0, 0.4),
    }

    # 不确定性等级阈值
    UNCERTAINTY_LEVELS: Dict[str, Tuple[float, float]] = {
        "low": (0.0, 0.2),
        "moderate": (0.2, 0.5),
        "high": (0.5, 0.8),
        "very_high": (0.8, 1.01),
    }

    # 话题默认证据因子（不同话题的证据可信度基线）
    _TOPIC_EVIDENCE_WEIGHTS: Dict[str, float] = {
        "mathematics": 0.9,
        "physics": 0.85,
        "history": 0.75,
        "medicine": 0.65,
        "law": 0.6,
        "creative_writing": 0.4,
        "prediction": 0.3,
        "politics": 0.35,
    }

    # 校准历史窗口大小
    CALIBRATION_WINDOW: int = 200

    def __init__(self) -> None:
        """初始化置信度披露模块。"""
        self._lock: Lock = Lock()
        self._confidence_records: Deque[ConfidenceRecord] = deque(maxlen=500)
        self._calibration_history: Deque[CalibrationEntry] = deque(
            maxlen=self.CALIBRATION_WINDOW
        )
        self._topic_accuracy: Dict[str, Deque[bool]] = defaultdict(deque)

        # 模块状态字段
        self.avg_confidence: float = 0.5
        self.disclosure_count: int = 0
        self.trust_score: float = 0.5  # 0-1，基于历史披露的信任评分
        self.calibration_accuracy: float = 0.5  # 0-1，校准精度

        # 内部追踪
        self._total_disclosures: int = 0
        self._honest_disclosures: int = 0  # 如实披露低置信度的次数
        self._overconfident_count: int = 0  # 过度自信的次数
        self._underconfident_count: int = 0  # 自信不足的次数

    def compute_confidence(self, response_data: Dict) -> float:
        """
        计算回复的置信度。

        综合考量以下因素：
        1. 证据数量和一致性
        2. 话题领域的不确定性基线
        3. 信息时效性
        4. 逻辑推理链的强度

        Args:
            response_data: 回复数据字典，包含:
                - topic: 话题领域
                - evidence_count: 证据数量
                - evidence_consistency: 证据一致性 (0-1)
                - information_freshness: 信息时效性 (0-1)
                - reasoning_strength: 推理链强度 (0-1)
                - domain_familiarity: 领域熟悉度 (0-1)

        Returns:
            置信度评分 (0-1)
        """
        topic = response_data.get("topic", "general")
        evidence_count = response_data.get("evidence_count", 0)
        evidence_consistency = response_data.get("evidence_consistency", 0.5)
        information_freshness = response_data.get("information_freshness", 0.5)
        reasoning_strength = response_data.get("reasoning_strength", 0.5)
        domain_familiarity = response_data.get("domain_familiarity", 0.5)

        # 1. 证据因子：证据数量带来的置信度（对数增长，快速饱和）
        evidence_factor = min(1.0, math.log1p(evidence_count) / math.log1p(20))

        # 2. 话题领域权重
        topic_weight = self._TOPIC_EVIDENCE_WEIGHTS.get(topic, 0.5)

        # 3. 综合计算置信度
        # 权重分配：证据一致性30%，推理强度25%，领域熟悉度20%，
        #           证据数量15%，信息时效性10%
        confidence = (
            0.30 * evidence_consistency
            + 0.25 * reasoning_strength
            + 0.20 * domain_familiarity
            + 0.15 * evidence_factor
            + 0.10 * information_freshness
        )

        # 话题修正
        confidence = confidence * (0.5 + 0.5 * topic_weight)

        # 校准偏移修正
        calibration_offset = self._get_calibration_offset(topic)
        confidence = confidence + calibration_offset

        # 裁剪到[0, 1]
        confidence = max(0.0, min(1.0, confidence))

        # 记录
        record = ConfidenceRecord(
            topic=topic,
            confidence=round(confidence, 4),
            evidence_count=evidence_count,
            calibration_offset=calibration_offset,
            timestamp=time.time(),
        )

        with self._lock:
            self._confidence_records.append(record)
            self._update_avg_confidence()

        return round(confidence, 4)

    def _get_calibration_offset(self, topic: str) -> float:
        """获取指定话题的校准偏移量。"""
        if topic not in self._topic_accuracy:
            return 0.0

        records = self._topic_accuracy[topic]
        if not records:
            return 0.0

        # 计算历史准确率
        recent = list(records)[-50:]  # 最近50条
        accuracy_rate = sum(1.0 for r in recent if r) / len(recent)

        # 如果历史准确率低，向下校准（降低置信度）
        # 如果历史准确率高，轻微向上校准
        offset = (accuracy_rate - 0.5) * 0.2  # 最大偏移±0.1
        return offset

    def _update_avg_confidence(self) -> None:
        """更新平均置信度。"""
        if self._confidence_records:
            self.avg_confidence = round(
                sum(r.confidence for r in self._confidence_records)
                / len(self._confidence_records),
                4,
            )

    def disclose_uncertainty(self, topic: str) -> UncertaintyDisclosure:
        """
        披露特定主题的不确定性信息。

        基于历史置信度记录和领域知识，结构化地披露不确定性，
        包括缺失信息、替代可能性和建议。

        Args:
            topic: 主题名称

        Returns:
            不确定性披露信息
        """
        with self._lock:
            self._total_disclosures += 1
            self.disclosure_count += 1

        # 获取该主题的历史置信度
        topic_records = [r for r in self._confidence_records if r.topic == topic]
        if topic_records:
            avg_topic_confidence = sum(r.confidence for r in topic_records) / len(topic_records)
        else:
            avg_topic_confidence = 0.5

        # 计算不确定性（1 - 置信度）
        uncertainty = 1.0 - avg_topic_confidence

        # 确定不确定性等级
        uncertainty_level = "moderate"
        for level_name, (low, high) in self.UNCERTAINTY_LEVELS.items():
            if low <= uncertainty < high:
                uncertainty_level = level_name
                break

        # 生成缺失信息列表
        missing_info = self._identify_missing_information(topic, uncertainty)

        # 生成替代可能性
        alternatives = self._generate_alternatives(topic, uncertainty)

        # 生成建议
        recommendation = self._generate_recommendation(topic, avg_topic_confidence, uncertainty_level)

        # 更新信任分数：诚实披露不确定性提升信任
        self._update_trust_score(True, uncertainty)

        disclosure = UncertaintyDisclosure(
            topic=topic,
            confidence=round(avg_topic_confidence, 4),
            uncertainty_level=uncertainty_level,
            missing_information=missing_info,
            alternative_possibilities=alternatives,
            recommendation=recommendation,
        )

        return disclosure

    def _identify_missing_information(self, topic: str, uncertainty: float) -> List[str]:
        """根据话题和不确定性级别识别可能缺失的信息。"""
        common_missing: Dict[str, List[str]] = {
            "mathematics": ["严格的证明验证", "边界条件的完整分析"],
            "medicine": ["患者个体化信息", "最新临床试验数据", "药物相互作用分析"],
            "law": ["具体司法管辖区的最新法规", "案件的完整事实"],
            "finance": ["实时市场数据", "用户风险承受能力评估"],
            "prediction": ["未来事件的关键驱动因素", "黑天鹅事件的概率评估"],
        }

        base_missing = common_missing.get(topic, ["特定领域的最新数据", "实际验证结果"])

        # 不确定性越高，缺失信息越多
        if uncertainty > 0.5:
            base_missing.append("对该结论的独立验证")
        if uncertainty > 0.7:
            base_missing.append("替代假设的系统评估")

        return base_missing

    def _generate_alternatives(self, topic: str, uncertainty: float) -> List[str]:
        """生成替代可能性。"""
        if uncertainty < 0.2:
            return ["当前结论在已知条件下高度可靠"]

        alternatives = [
            f"在{topic}领域，可能存在其他同样合理的解释",
            "部分假设条件可能不成立，导致不同结论",
        ]

        if uncertainty > 0.5:
            alternatives.append("现有证据可能支持截然不同的解读")

        return alternatives

    def _generate_recommendation(
        self, topic: str, confidence: float, uncertainty_level: str
    ) -> str:
        """生成建议文本。"""
        if confidence >= 0.8:
            return (
                f"关于{topic}的置信度较高（{confidence:.0%}），"
                "但建议对关键结论进行独立验证。"
            )
        elif confidence >= 0.6:
            return (
                f"关于{topic}的置信度中等（{confidence:.0%}），"
                "建议结合其他可靠信息源做进一步确认。"
            )
        elif confidence >= 0.4:
            return (
                f"关于{topic}的置信度较低（{confidence:.0%}），"
                "建议仅作为参考，务必查阅专业信息源。"
            )
        else:
            return (
                f"关于{topic}的置信度很低（{confidence:.0%}），"
                "强烈建议咨询该领域的专家或权威信息源，"
                "本回复不应作为决策依据。"
            )

    def calibrate_confidence(self, historical_accuracy: List[Tuple[str, float, bool]]) -> float:
        """
        基于历史准确率校准置信度。

        通过比较预测置信度与实际准确率，调整置信度校准参数，
        使未来预测更加准确。

        Args:
            historical_accuracy: 历史准确率记录列表，每个元素为
                (topic, predicted_confidence, was_correct) 元组

        Returns:
            校准精度评分 (0-1)
        """
        if not historical_accuracy:
            return self.calibration_accuracy

        # 计算校准误差
        calibration_errors: List[float] = []

        with self._lock:
            for topic, predicted, was_correct in historical_accuracy:
                actual = 1.0 if was_correct else 0.0
                error = abs(predicted - actual)
                calibration_errors.append(error)

                # 记录校准条目
                entry = CalibrationEntry(
                    predicted_confidence=predicted,
                    actual_accuracy=was_correct,
                    topic=topic,
                    timestamp=time.time(),
                )
                self._calibration_history.append(entry)

                # 更新话题级准确率追踪
                self._topic_accuracy[topic].append(was_correct)

                # 统计过度/不足自信
                if predicted > 0.7 and not was_correct:
                    self._overconfident_count += 1
                elif predicted < 0.3 and was_correct:
                    self._underconfident_count += 1

        # 计算校准精度：误差越小精度越高
        avg_error = sum(calibration_errors) / len(calibration_errors)
        self.calibration_accuracy = round(max(0.0, 1.0 - avg_error), 4)

        # 更新信任分数
        # 如果过度自信次数多，信任分降低
        total_predictions = len(historical_accuracy)
        overconfident_rate = self._overconfident_count / max(1, total_predictions)
        honest_rate = 1.0 - overconfident_rate
        self._update_trust_score_from_calibration(honest_rate)

        return self.calibration_accuracy

    def _update_trust_score(self, is_honest: bool, uncertainty: float) -> None:
        """更新信任分数。"""
        # 诚实披露不确定性（即使高不确定性）增加信任
        # 隐瞒不确定性（高不确定性但未披露）降低信任
        if is_honest:
            increment = 0.02 + uncertainty * 0.03  # 不确定性越高越诚实则加分越多
            self.trust_score = min(1.0, self.trust_score + increment)
        else:
            decrement = 0.1
            self.trust_score = max(0.0, self.trust_score - decrement)

    def _update_trust_score_from_calibration(self, honest_rate: float) -> None:
        """根据校准诚实率更新信任分数。"""
        # 校准诚实率越高，信任分越接近其值
        self.trust_score = round(0.7 * self.trust_score + 0.3 * honest_rate, 4)

    def format_confidence_statement(self, confidence: float, topic: str) -> str:
        """
        格式化置信度声明文本。

        将数值置信度转化为用户友好的文本声明，
        包含置信度等级、不确定性提示和建议。

        Args:
            confidence: 置信度 (0-1)
            topic: 话题

        Returns:
            格式化的置信度声明文本
        """
        confidence = max(0.0, min(1.0, confidence))

        # 确定置信度等级
        level_name = "不确定"
        for name, (low, high) in self.CONFIDENCE_LEVELS.items():
            if low <= confidence < high:
                level_name = name
                break

        # 中文等级映射
        level_display = {
            "very_high": "极高",
            "high": "较高",
            "moderate": "中等",
            "low": "较低",
            "very_low": "极低",
        }
        display_name = level_display.get(level_name, "未知")

        # 构建声明文本
        percentage = f"{confidence:.0%}"

        if confidence >= 0.8:
            statement = (
                f"关于「{topic}」，我的置信度为{display_name}（{percentage}）。"
                f"该回答基于较为充分的证据，但关键细节建议独立核实。"
            )
        elif confidence >= 0.6:
            statement = (
                f"关于「{topic}」，我的置信度为{display_name}（{percentage}）。"
                f"该回答可能存在不准确之处，建议结合其他信息源判断。"
            )
        elif confidence >= 0.4:
            statement = (
                f"关于「{topic}」，我的置信度为{display_name}（{percentage}）。"
                f"该回答的可靠性有限，不应作为唯一参考，请务必查阅专业信息源。"
            )
        else:
            statement = (
                f"关于「{topic}」，我的置信度为{display_name}（{percentage}）。"
                f"⚠️ 该回答可能包含重要错误，强烈建议咨询该领域专家。"
                f"本回答仅供参考，不应作为任何决策的依据。"
            )

        return statement

    def get_state(self) -> Dict:
        """返回模块状态字典。"""
        with self._lock:
            return {
                "avg_confidence": self.avg_confidence,
                "disclosure_count": self.disclosure_count,
                "trust_score": self.trust_score,
                "calibration_accuracy": self.calibration_accuracy,
                "total_disclosures": self._total_disclosures,
                "overconfident_count": self._overconfident_count,
                "underconfident_count": self._underconfident_count,
            }


# 单例模式
_instance: Optional[ConfidenceDisclosure] = None


def get_instance() -> ConfidenceDisclosure:
    """获取 ConfidenceDisclosure 的全局单例实例。"""
    global _instance
    if _instance is None:
        _instance = ConfidenceDisclosure()
    return _instance
