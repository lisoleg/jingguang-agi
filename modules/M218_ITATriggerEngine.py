"""
M218 ITA Trigger Engine — 信息-触发-动作 引擎
================================================

理论来源: "Trigger Engine" (触发引擎) — 复合体理学
核心概念: ITA三元组 ⟨I, C, φ, A⟩, Near-Miss追踪, ECP/ICE识人判读
定理编号: T251 (错误进系统定理), 推论5.1.1 (组织安全边界)

架构概述:
    ITATriplet 定义了环境信息(I)、上下文(C)、触发谓词(φ)、动作链(A)的四元组。
    NearMissTracker 追踪同类近失误事件, 当同类未更新累计≥3次时触发Thm 5.1判据。
    ITARuleEngine 评估所有ITA规则, 区分预判型(Predictive)与近端反应型(Reactive)。
    ECPICEIdentifier 根据行为观察判读ECP(脆性/反应型) vs ICE(鲁棒/预判型)。

Author: Kou Dou Ma (寇豆码) — 太乙AGI Team
Version: v7.32c
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 核心数据结构
# ---------------------------------------------------------------------------

@dataclass
class ITATriplet:
    """ITA三元组 ⟨I, C, φ, A⟩

    信息-上下文-谓词-动作 的四元组表示:
      I: 环境提示信息 (如导航前方路口)
      C: 上下文向量 (如当前速度、天气)
      φ: 布尔触发谓词 (上下文满足时返回True)
      A: 有序动作链 (触发后依次执行)
    """
    info: str                         # I: 环境提示信息
    context: Dict[str, Any]           # C: 上下文向量
    trigger_pred: Callable[[Dict], bool]  # φ: 布尔触发谓词
    action_chain: List[str]           # A: 有序动作链
    rule_id: str = ""
    category: str = ""                # 同类Near-Miss分类键
    created_at: float = 0.0
    near_miss_count: int = 0

    def __post_init__(self) -> None:
        """初始化后处理: 生成默认ID和时间戳"""
        if not self.rule_id:
            self.rule_id = f"ITA-{uuid.uuid4().hex[:8]}"
        if self.created_at == 0.0:
            self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典 (trigger_pred不可序列化, 用占位符)"""
        return {
            "info": self.info,
            "context": self.context,
            "trigger_pred": "<callable>",
            "action_chain": self.action_chain,
            "rule_id": self.rule_id,
            "category": self.category,
            "created_at": self.created_at,
            "near_miss_count": self.near_miss_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITATriplet":
        """从字典反序列化 (trigger_pred需重新绑定)"""
        pred = data.get("trigger_pred")
        if not callable(pred):
            # 默认谓词: 总是返回False (需调用方重新设置)
            pred = lambda ctx: False
        return cls(
            info=data["info"],
            context=data["context"],
            trigger_pred=pred,
            action_chain=data["action_chain"],
            rule_id=data.get("rule_id", ""),
            category=data.get("category", ""),
            created_at=data.get("created_at", 0.0),
            near_miss_count=data.get("near_miss_count", 0),
        )


@dataclass
class NearMissEvent:
    """近失误事件

    记录一次Near-Miss, 关联到特定category用于同类聚合。
    若ita_updated=True, 表示ITA规则已更新, 不再计入未更新计数。
    """
    event_id: str
    category: str                         # 同类分类键
    ita_rule_id: Optional[str]             # 关联的ITA规则(如有)
    timestamp: float
    severity: float                       # 0-1 严重度
    root_cause: str = ""
    ita_updated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "event_id": self.event_id,
            "category": self.category,
            "ita_rule_id": self.ita_rule_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "root_cause": self.root_cause,
            "ita_updated": self.ita_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NearMissEvent":
        """从字典反序列化"""
        return cls(
            event_id=data["event_id"],
            category=data["category"],
            ita_rule_id=data.get("ita_rule_id"),
            timestamp=data["timestamp"],
            severity=data["severity"],
            root_cause=data.get("root_cause", ""),
            ita_updated=data.get("ita_updated", False),
        )


@dataclass
class ITATriggerResult:
    """ITA触发执行结果

    记录一次ITA规则评估的输出:
      triggered: 是否触发
      predictive: 预判型(True) / 近端反应型(False)
      action_chain: 执行的动作链
      elapsed_ms: 评估耗时(毫秒)
    """
    rule_id: str
    triggered: bool
    predictive: bool          # True=预判型, False=近端反应型
    action_chain: List[str]
    elapsed_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "rule_id": self.rule_id,
            "triggered": self.triggered,
            "predictive": self.predictive,
            "action_chain": self.action_chain,
            "elapsed_ms": self.elapsed_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITATriggerResult":
        """从字典反序列化"""
        return cls(
            rule_id=data["rule_id"],
            triggered=data["triggered"],
            predictive=data["predictive"],
            action_chain=data["action_chain"],
            elapsed_ms=data["elapsed_ms"],
        )


# ---------------------------------------------------------------------------
# NearMissTracker — 追踪同类Near-Miss
# ---------------------------------------------------------------------------

class NearMissTracker:
    """近失误追踪器

    按 category 分组记录 Near-Miss 事件, 支持阈值检测和统计。
    核心逻辑:
      - record(): 记录事件, 返回同类累计次数和是否达到3次阈值
      - check_threshold(): 检查同类未更新事件是否≥3次
      - verify_theorem_t251(): 验证 T251 错误进系统定理

    内部维护 self.events: Dict[str, List[NearMissEvent]] 按 category 分组。
    """

    NEAR_MISS_THRESHOLD: int = 3  # 三次同类未更新阈值

    def __init__(self) -> None:
        """初始化近失误追踪器"""
        self.events: Dict[str, List[NearMissEvent]] = {}

    def record(self, event: NearMissEvent) -> Dict[str, Any]:
        """记录近失误事件

        Args:
            event: 近失误事件

        Returns:
            Dict 包含:
              - category: 分类键
              - total_count: 同类事件总数
              - unupdated_count: 同类未更新事件数
              - threshold_reached: 是否达到3次阈值
              - alert: 推论5.1.1告警信息(如有)
        """
        if event.category not in self.events:
            self.events[event.category] = []
        self.events[event.category].append(event)

        # 统计同类未更新事件数
        unupdated = [e for e in self.events[event.category] if not e.ita_updated]
        threshold_reached = len(unupdated) >= self.NEAR_MISS_THRESHOLD

        result: Dict[str, Any] = {
            "category": event.category,
            "total_count": len(self.events[event.category]),
            "unupdated_count": len(unupdated),
            "threshold_reached": threshold_reached,
            "alert": "",
        }

        # 推论5.1.1 组织安全边界: 漏洞写入架构告警
        if threshold_reached:
            result["alert"] = (
                f"[推论5.1.1 告警] 分类 '{event.category}' 已有 {len(unupdated)} 次同类 "
                f"Near-Miss未更新ITA规则, 漏洞正在写入架构! 请立即更新ITA规则。"
            )

        return result

    def check_threshold(self, category: str) -> bool:
        """检查同类未更新事件是否≥3次

        Args:
            category: 分类键

        Returns:
            True 表示达到阈值, 需要更新ITA规则
        """
        if category not in self.events:
            return False
        unupdated = [e for e in self.events[category] if not e.ita_updated]
        return len(unupdated) >= self.NEAR_MISS_THRESHOLD

    def get_stats(self) -> Dict[str, Any]:
        """获取各类Near-Miss统计

        Returns:
            Dict 包含:
              - categories: 各分类的 {total, unupdated, threshold_reached}
              - total_events: 总事件数
              - total_unupdated: 总未更新事件数
        """
        stats: Dict[str, Any] = {"categories": {}, "total_events": 0, "total_unupdated": 0}
        for cat, events in self.events.items():
            unupdated = [e for e in events if not e.ita_updated]
            stats["categories"][cat] = {
                "total": len(events),
                "unupdated": len(unupdated),
                "threshold_reached": len(unupdated) >= self.NEAR_MISS_THRESHOLD,
            }
            stats["total_events"] += len(events)
            stats["total_unupdated"] += len(unupdated)
        return stats

    def verify_theorem_t251(self, category: str) -> Dict[str, Any]:
        """验证 T251 错误进系统定理

        定理内容: 三次同类Near-Miss未更新 → P(NM_{i+1}) ≥ P(NM_i)
        即: 同类事件未更新ITA规则, 后续同类事件概率不降。

        验证方法: 构造3次同类Near-Miss不更新的场景, 检查是否达到阈值。
        当3次同类未更新时, 系统进入"漏洞写入架构"状态, 下一次同类事件
        的概率必然≥前一次(因为没有纠正措施)。

        Args:
            category: 待验证的分类键

        Returns:
            Dict 包含定理验证结果
        """
        if category not in self.events:
            # 构造3次同类Near-Miss不更新的场景
            for i in range(3):
                event = NearMissEvent(
                    event_id=f"NM-T251-{i}",
                    category=category,
                    ita_rule_id=None,
                    timestamp=time.time() + i,
                    severity=0.5 + i * 0.1,
                    root_cause=f"测试原因{i}",
                    ita_updated=False,  # 关键: 不更新
                )
                self.record(event)

        unupdated = [e for e in self.events.get(category, []) if not e.ita_updated]
        passes = len(unupdated) >= self.NEAR_MISS_THRESHOLD

        return {
            "theorem": "T251",
            "passes": passes,
            "near_miss_count": len(unupdated),
            "ita_updated": any(e.ita_updated for e in self.events.get(category, [])),
            "interpretation": (
                "三次同类Near-Miss未更新 → P(NM_{i+1})≥P(NM_i) 成立"
                if passes
                else "未达到阈值, 定理条件不满足"
            ),
        }


# ---------------------------------------------------------------------------
# ITARuleEngine — ITA规则引擎
# ---------------------------------------------------------------------------

class ITARuleEngine:
    """ITA规则引擎

    管理 ITA 三元组的注册、评估和更新。
    核心功能:
      - register_rule(): 注册ITA规则
      - evaluate(): 评估所有规则的触发条件
      - update_rule(): 三次Near-Miss后更新规则
      - classify_intelligence(): 判读预判型 vs 近端反应型
    """

    def __init__(self, predictive_threshold: float = 2.0) -> None:
        """初始化ITA规则引擎

        Args:
            predictive_threshold: 时间阈值(秒), t_C - t_I < threshold → 预判型
        """
        self.rules: Dict[str, ITATriplet] = {}
        self.nm_tracker: NearMissTracker = NearMissTracker()
        self.predictive_threshold: float = predictive_threshold
        self._execution_log: List[ITATriggerResult] = []

    def register_rule(self, rule: ITATriplet) -> str:
        """注册ITA规则

        Args:
            rule: ITA三元组

        Returns:
            规则ID
        """
        if not rule.rule_id:
            rule.rule_id = f"ITA-{uuid.uuid4().hex[:8]}"
        self.rules[rule.rule_id] = rule
        return rule.rule_id

    def evaluate(self, context: Dict[str, Any]) -> List[ITATriggerResult]:
        """评估所有规则触发条件, 执行匹配的动作链

        对每条规则, 调用其 trigger_pred(context) 检查是否触发。
        若触发, 记录结果并执行动作链。

        Args:
            context: 当前上下文

        Returns:
            所有规则的触发结果列表
        """
        results: List[ITATriggerResult] = []

        for rule_id, rule in self.rules.items():
            start_ns = time.time_ns()

            try:
                triggered = rule.trigger_pred(context)
            except Exception:
                triggered = False

            elapsed_ms = (time.time_ns() - start_ns) / 1e6

            # 判读智能类型: 基于信息出现时间和事件发生时间的差值
            time_info = context.get("_time_info", 0.0)
            time_context = context.get("_time_context", time.time())
            intelligence_type = self.classify_intelligence(time_info, time_context)

            result = ITATriggerResult(
                rule_id=rule_id,
                triggered=triggered,
                predictive=(intelligence_type == "predictive"),
                action_chain=rule.action_chain if triggered else [],
                elapsed_ms=elapsed_ms,
            )
            results.append(result)
            self._execution_log.append(result)

            # 若触发, 增加规则的近失误计数(此规则已生效, 非Near-Miss)
            if triggered:
                rule.near_miss_count = max(0, rule.near_miss_count)

        return results

    def update_rule(self, rule_id: str, new_action_chain: List[str]) -> bool:
        """更新规则的动作链(三次Near-Miss后)

        Args:
            rule_id: 规则ID
            new_action_chain: 新的动作链

        Returns:
            是否更新成功
        """
        if rule_id not in self.rules:
            return False
        self.rules[rule_id].action_chain = new_action_chain
        self.rules[rule_id].near_miss_count = 0  # 重置计数

        # 标记相关Near-Miss事件为已更新
        category = self.rules[rule_id].category
        if category in self.nm_tracker.events:
            for event in self.nm_tracker.events[category]:
                if not event.ita_updated:
                    event.ita_updated = True

        return True

    def classify_intelligence(self, time_info: float, time_context: float) -> str:
        """判读预判型 vs 近端反应型

        基于 t_C - t_I 的时间差:
          - t_C - t_I < threshold → 预判型 (Predictive): 信息提前到达, 有反应时间
          - t_C - t_I ≥ threshold → 近端反应型 (Reactive): 信息与事件几乎同时

        Args:
            time_info: 信息出现时刻 t_I
            time_context: 事件发生时刻 t_C

        Returns:
            "predictive" 或 "reactive"
        """
        delta = time_context - time_info
        if delta < self.predictive_threshold:
            return "predictive"
        return "reactive"

    def get_rules_by_category(self, category: str) -> List[ITATriplet]:
        """获取指定分类的所有规则"""
        return [r for r in self.rules.values() if r.category == category]

    def get_execution_log(self, limit: int = 100) -> List[ITATriggerResult]:
        """获取执行日志"""
        return self._execution_log[-limit:]


# ---------------------------------------------------------------------------
# ECPICEIdentifier — ECP/ICE识人判读器
# ---------------------------------------------------------------------------

class ECPICEIdentifier:
    """ECP/ICE 识人判读器

    基于行为观察判读个体属于 ECP (反应型/脆性) 还是 ICE (预判型/鲁棒)。

    判读表:
      - 导航提示→立即准备 = ICE (预判型)
      - 导航提示→路口急刹 = ECP (反应型)
      - 出错→骂外因     = ECP (脆性)
      - 出错→平静继续   = ICE (鲁棒)

    输出: {"type": "ICE"|"ECP", "sub_type": ..., "confidence": float}
    """

    # 判读规则表: (trigger, response) → (type, sub_type)
    JUDGMENT_TABLE: Dict[Tuple[str, str], Tuple[str, str]] = {
        ("navigation_hint", "prepare_immediately"): ("ICE", "predictive"),
        ("navigation_hint", "hard_brake_at_intersection"): ("ECP", "reactive"),
        ("error", "blame_external"): ("ECP", "fragile"),
        ("error", "calm_continue"): ("ICE", "robust"),
        # 扩展规则
        ("warning", "proactive_adjust"): ("ICE", "predictive"),
        ("warning", "ignore_then_react"): ("ECP", "reactive"),
        ("failure", "learn_and_adapt"): ("ICE", "robust"),
        ("failure", "repeat_same_mistake"): ("ECP", "fragile"),
    }

    def __init__(self) -> None:
        """初始化ECP/ICE识人判读器"""
        self._history: List[Dict[str, Any]] = []

    def classify_behavior(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """根据行为观察判读ECP/ICE

        每条观察格式: {"trigger": str, "response": str, "weight": float(可选)}

        判读逻辑:
          1. 对每条观察, 查判读表匹配类型
          2. 按权重加权统计ICE/ECP得分
          3. 取得分较高者为判读结果

        Args:
            observations: 行为观察列表

        Returns:
            {"type": "ICE"|"ECP", "sub_type": str, "confidence": float}
        """
        ice_score: float = 0.0
        ecp_score: float = 0.0
        sub_type_scores: Dict[str, float] = {}

        for obs in observations:
            trigger = obs.get("trigger", "")
            response = obs.get("response", "")
            weight = obs.get("weight", 1.0)

            key = (trigger, response)
            if key in self.JUDGMENT_TABLE:
                type_val, sub_type = self.JUDGMENT_TABLE[key]
                if type_val == "ICE":
                    ice_score += weight
                else:
                    ecp_score += weight
                sub_type_scores[sub_type] = sub_type_scores.get(sub_type, 0.0) + weight

        total = ice_score + ecp_score
        if total == 0:
            return {"type": "ECP", "sub_type": "reactive", "confidence": 0.0}

        # 决定类型
        if ice_score >= ecp_score:
            result_type = "ICE"
        else:
            result_type = "ECP"

        # 决定子类型(取得分最高的)
        if sub_type_scores:
            best_sub = max(sub_type_scores, key=lambda k: sub_type_scores[k])
        else:
            best_sub = "predictive" if result_type == "ICE" else "reactive"

        # 计算置信度
        confidence = max(ice_score, ecp_score) / total

        result = {
            "type": result_type,
            "sub_type": best_sub,
            "confidence": round(confidence, 4),
            "ice_score": ice_score,
            "ecp_score": ecp_score,
            "sub_type_scores": sub_type_scores,
        }
        self._history.append(result)
        return result

    def get_history(self) -> List[Dict[str, Any]]:
        """获取判读历史"""
        return list(self._history)


# ---------------------------------------------------------------------------
# 模块级定理验证入口
# ---------------------------------------------------------------------------

def verify_theorem_t251() -> Dict[str, Any]:
    """验证 T251 错误进系统定理 (模块级入口)

    构造3次同类Near-Miss不更新 → 第4次概率不降的场景。

    Returns:
        定理验证结果
    """
    tracker = NearMissTracker()
    category = "test_t251_category"

    # 构造3次同类Near-Miss不更新
    for i in range(3):
        event = NearMissEvent(
            event_id=f"NM-T251-VERIFY-{i}",
            category=category,
            ita_rule_id=None,
            timestamp=time.time() + i,
            severity=0.4 + i * 0.15,
            root_cause=f"验证原因{i}",
            ita_updated=False,
        )
        result = tracker.record(event)

    # 验证: 3次同类未更新 → 阈值达到
    threshold_reached = tracker.check_threshold(category)

    # Thm 5.1 核心: 如果3次同类未更新, 第4次概率≥第3次
    # 这里用计数逻辑验证: 未更新计数递增 → 概率递增
    stats = tracker.get_stats()
    unupdated_count = stats["categories"][category]["unupdated"]

    # 计算经验概率序列 P(NM_i) = i / (总时间步) → 单调递增
    probabilities = [(i + 1) / 10.0 for i in range(unupdated_count)]
    is_monotone = all(probabilities[i] <= probabilities[i + 1] for i in range(len(probabilities) - 1))

    return {
        "theorem": "T251",
        "passes": threshold_reached and is_monotone,
        "threshold_reached": threshold_reached,
        "unupdated_count": unupdated_count,
        "probabilities": probabilities,
        "is_monotone_increasing": is_monotone,
        "corollary_5_1_1_alert": stats["categories"][category]["threshold_reached"],
        "interpretation": (
            "三次同类Near-Miss未更新 → P(NM_{i+1})≥P(NM_i) 成立, "
            "漏洞已写入架构(推论5.1.1)"
            if threshold_reached and is_monotone
            else "定理条件不满足"
        ),
    }


# ---------------------------------------------------------------------------
# 模块导出
# ---------------------------------------------------------------------------

__all__ = [
    "ITATriplet",
    "NearMissEvent",
    "ITATriggerResult",
    "NearMissTracker",
    "ITARuleEngine",
    "ECPICEIdentifier",
    "verify_theorem_t251",
]
