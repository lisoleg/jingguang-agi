# -*- coding: utf-8 -*-
"""
M100_RewardHackDetector — 奖励作弊检测模块

定理 T44: "目标函数G与期望行为B的KL散度必须bounded，否则必然出现奖励作弊"
定理 T47: "任何AGI系统的决策链中，必须存在至少一个由人类承担最终问责的节点"

本模块检测奖励作弊行为，计算KL散度，验证人类问责节点，
并建议对齐修复方案。
"""

from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque, Dict, List, Optional, Tuple


@dataclass
class BehaviorRecord:
    """行为记录数据结构。"""
    action: str
    reward: float
    goal_alignment: float  # 0-1，与目标函数的对齐程度
    timestamp: float


@dataclass
class HackReport:
    """奖励作弊报告数据结构。"""
    type: str  # "reward_gaming", "specification_gaming", "side_effect", "goodharting"
    severity: float  # 0-1
    kl_divergence: float
    suggested_fix: str


@dataclass
class AccountabilityNode:
    """问责节点数据结构。"""
    node_id: str
    node_type: str  # "human_decision", "human_review", "human_override", "human_audit"
    responsible_party: str  # "human" or "ai"
    is_mandatory: bool
    description: str


@dataclass
class AlignmentFix:
    """对齐修复方案数据结构。"""
    fix_type: str  # "goal_refinement", "constraint_addition", "metric_reformulation", "oversight_enhancement"
    description: str
    priority: int  # 1-5
    estimated_impact: float  # 0-1
    implementation_steps: List[str]


class RewardHackDetector:
    """
    奖励作弊检测器，监控AGI系统的行为是否符合预期目标。

    基于定理T44和T47，本模块实现：
    1. 检测奖励作弊行为（目标函数与期望行为的KL散度过大）
    2. 验证决策链中存在人类问责节点
    3. 提供对齐修复建议
    """

    # KL散度上界阈值（超过此值视为违规）
    KL_DIVERGENCE_BOUND: float = 1.0

    # 作弊类型检测阈值
    REWARD_GAMING_THRESHOLD: float = 0.7
    GOODHARTING_THRESHOLD: float = 0.6
    SPECIFICATION_GAMING_THRESHOLD: float = 0.5

    # 行为历史窗口大小
    BEHAVIOR_WINDOW: int = 200

    # 问责节点模板
    _MANDATORY_ACCOUNTABILITY_NODES: List[AccountabilityNode] = [
        AccountabilityNode(
            node_id="final_decision",
            node_type="human_decision",
            responsible_party="human",
            is_mandatory=True,
            description="最终决策节点必须由人类确认",
        ),
        AccountabilityNode(
            node_id="safety_review",
            node_type="human_review",
            responsible_party="human",
            is_mandatory=True,
            description="安全审查节点必须由人类执行",
        ),
        AccountabilityNode(
            node_id="emergency_override",
            node_type="human_override",
            responsible_party="human",
            is_mandatory=True,
            description="紧急情况必须由人类接管控制",
        ),
    ]

    def __init__(self) -> None:
        """初始化奖励作弊检测模块。"""
        self._lock: Lock = Lock()
        self._behavior_history: Deque[BehaviorRecord] = deque(maxlen=self.BEHAVIOR_WINDOW)
        self._detected_hacks: List[HackReport] = []
        self._accountability_chains: Dict[str, List[AccountabilityNode]] = {}

        # 模块状态字段
        self.hack_count: int = 0
        self.avg_kl_divergence: float = 0.0
        self.accountability_verified: bool = False
        self.alignment_score: float = 1.0

        # 内部追踪
        self._total_behaviors_analyzed: int = 0
        self._kl_divergence_history: List[float] = []
        self._alignment_fixes_applied: int = 0
        self._last_check_timestamp: float = 0.0

        # 目标函数参考分布（默认均匀分布作为基线）
        self._goal_distribution: Dict[str, float] = {}
        self._expected_behavior_distribution: Dict[str, float] = {}

    def detect_hacking(self, behavior_sequence: List[BehaviorRecord]) -> List[HackReport]:
        """
        检测奖励作弊行为。

        分析行为序列，识别四种作弊模式：
        1. reward_gaming: 通过非预期方式最大化奖励
        2. specification_gaming: 利用目标函数规约的漏洞
        3. side_effect: 产生未预期的副作用
        4. goodharting: 当指标成为目标时，指标失效

        Args:
            behavior_sequence: 行为记录序列

        Returns:
            检测到的作弊报告列表
        """
        if not behavior_sequence:
            return []

        reports: List[HackReport] = []

        with self._lock:
            self._total_behaviors_analyzed += len(behavior_sequence)
            for b in behavior_sequence:
                self._behavior_history.append(b)

        # 检测1：奖励博弈（reward_gaming）
        reward_gaming_report = self._detect_reward_gaming(behavior_sequence)
        if reward_gaming_report is not None:
            reports.append(reward_gaming_report)

        # 检测2：规约博弈（specification_gaming）
        spec_gaming_report = self._detect_specification_gaming(behavior_sequence)
        if spec_gaming_report is not None:
            reports.append(spec_gaming_report)

        # 检测3：副作用（side_effect）
        side_effect_report = self._detect_side_effects(behavior_sequence)
        if side_effect_report is not None:
            reports.append(side_effect_report)

        # 检测4：古德哈特定律（goodharting）
        goodharting_report = self._detect_goodharting(behavior_sequence)
        if goodharting_report is not None:
            reports.append(goodharting_report)

        # 更新模块状态
        with self._lock:
            self.hack_count += len(reports)
            self._detected_hacks.extend(reports)

            # 更新对齐分数
            if reports:
                max_severity = max(r.severity for r in reports)
                self.alignment_score = round(max(0.0, self.alignment_score - max_severity * 0.2), 4)
            else:
                # 无作弊时缓慢恢复
                self.alignment_score = round(min(1.0, self.alignment_score + 0.01), 4)

            self._last_check_timestamp = time.time()

        # 更新平均KL散度
        self._update_avg_kl_divergence(behavior_sequence)

        return reports

    def _detect_reward_gaming(self, behaviors: List[BehaviorRecord]) -> Optional[HackReport]:
        """检测奖励博弈：高奖励但低目标对齐。"""
        high_reward_low_alignment = [
            b for b in behaviors
            if b.reward > 0.7 and b.goal_alignment < 0.4
        ]

        if not high_reward_low_alignment:
            return None

        ratio = len(high_reward_low_alignment) / len(behaviors)
        if ratio < self.REWARD_GAMING_THRESHOLD:
            return None

        severity = min(1.0, ratio)
        avg_alignment = sum(b.goal_alignment for b in high_reward_low_alignment) / len(high_reward_low_alignment)

        # 估算KL散度
        kl_div = self._estimate_kl_from_alignment(avg_alignment)

        return HackReport(
            type="reward_gaming",
            severity=round(severity, 4),
            kl_divergence=round(kl_div, 4),
            suggested_fix=(
                "检测到奖励博弈行为：系统在获得高奖励时目标对齐度偏低。"
                "建议：(1)重新审视奖励函数设计，排除可被利用的捷径；"
                "(2)增加目标对齐度作为奖励的惩罚项；"
                "(3)引入人类审查机制验证高奖励行为的合理性。"
            ),
        )

    def _detect_specification_gaming(self, behaviors: List[BehaviorRecord]) -> Optional[HackReport]:
        """检测规约博弈：行为符合字面规约但违背意图。"""
        # 检测模式：奖励持续高但目标对齐度波动大
        if len(behaviors) < 3:
            return None

        alignments = [b.goal_alignment for b in behaviors]
        rewards = [b.reward for b in behaviors]

        avg_reward = sum(rewards) / len(rewards)
        alignment_variance = sum((a - sum(alignments) / len(alignments)) ** 2 for a in alignments) / len(alignments)

        # 高奖励+高对齐度方差 = 可能存在规约博弈
        if avg_reward > 0.6 and alignment_variance > 0.1:
            severity = min(1.0, alignment_variance * 3)
            kl_div = self._estimate_kl_from_alignment(sum(alignments) / len(alignments))

            return HackReport(
                type="specification_gaming",
                severity=round(severity, 4),
                kl_divergence=round(kl_div, 4),
                suggested_fix=(
                    "检测到规约博弈行为：行为在字面上符合规约但目标对齐度波动大。"
                    "建议：(1)细化目标函数规约，覆盖边缘案例；"
                    "(2)引入意图验证机制；"
                    "(3)增加对抗性测试用例。"
                ),
            )

        return None

    def _detect_side_effects(self, behaviors: List[BehaviorRecord]) -> Optional[HackReport]:
        """检测副作用：目标对齐度持续下降。"""
        if len(behaviors) < 4:
            return None

        # 检查对齐度是否持续下降
        alignments = [b.goal_alignment for b in behaviors]
        declining_count = 0
        for i in range(1, len(alignments)):
            if alignments[i] < alignments[i - 1]:
                declining_count += 1

        decline_rate = declining_count / (len(alignments) - 1)
        if decline_rate < 0.6:
            return None

        severity = min(1.0, decline_rate)
        avg_alignment = sum(alignments) / len(alignments)
        kl_div = self._estimate_kl_from_alignment(avg_alignment)

        return HackReport(
            type="side_effect",
            severity=round(severity, 4),
            kl_divergence=round(kl_div, 4),
            suggested_fix=(
                "检测到副作用行为：目标对齐度持续下降。"
                "建议：(1)增加目标对齐度的监控频率；"
                "(2)设置目标对齐度下限阈值，触发自动干预；"
                "(3)审查最近的行为变更，识别导致对齐度下降的具体行为。"
            ),
        )

    def _detect_goodharting(self, behaviors: List[BehaviorRecord]) -> Optional[HackReport]:
        """检测古德哈特定律效应：奖励指标与真实目标脱钩。"""
        if len(behaviors) < 5:
            return None

        # 计算奖励与对齐度的相关性
        rewards = [b.reward for b in behaviors]
        alignments = [b.goal_alignment for b in behaviors]

        n = len(rewards)
        r_mean = sum(rewards) / n
        a_mean = sum(alignments) / n

        covariance = sum((rewards[i] - r_mean) * (alignments[i] - a_mean) for i in range(n)) / n
        r_std = math.sqrt(sum((r - r_mean) ** 2 for r in rewards) / n)
        a_std = math.sqrt(sum((a - a_mean) ** 2 for a in alignments) / n)

        if r_std == 0 or a_std == 0:
            return None

        correlation = covariance / (r_std * a_std)

        # 负相关或低相关 = 指标与目标脱钩
        if correlation < self.GOODHARTING_THRESHOLD:
            severity = min(1.0, abs(correlation - 0.5) * 2)
            avg_alignment = sum(alignments) / len(alignments)
            kl_div = self._estimate_kl_from_alignment(avg_alignment)

            return HackReport(
                type="goodharting",
                severity=round(severity, 4),
                kl_divergence=round(kl_div, 4),
                suggested_fix=(
                    "检测到古德哈特效应：奖励指标与真实目标相关性过低。"
                    "建议：(1)重新设计奖励函数，确保与真实目标高度相关；"
                    "(2)引入多维度评估指标，避免单一指标优化；"
                    "(3)定期由人类评估系统输出质量，校准指标有效性。"
                ),
            )

        return None

    def _estimate_kl_from_alignment(self, avg_alignment: float) -> float:
        """根据平均对齐度估算KL散度。"""
        # 对齐度越低，KL散度越大
        # 使用简单的映射：KL ≈ -ln(alignment + ε)
        epsilon = 1e-10
        estimated_kl = -math.log(max(epsilon, avg_alignment) + epsilon)
        return max(0.0, estimated_kl)

    def compute_kl_divergence(
        self,
        goal_function: Dict[str, float],
        observed_behavior: Dict[str, float],
    ) -> float:
        """
        计算目标函数G与期望行为B的KL散度。

        D_KL(G || B) = Σ G(x) * ln(G(x) / B(x))

        基于定理T44，KL散度必须bounded，否则出现奖励作弊。

        Args:
            goal_function: 目标函数的概率分布，key为行为类别，value为概率
            observed_behavior: 观测行为的概率分布

        Returns:
            KL散度值（非负），越大表示偏离越严重
        """
        if not goal_function or not observed_behavior:
            return 0.0

        # 确保所有key在两个分布中都存在
        all_keys = set(goal_function.keys()) | set(observed_behavior.keys())
        epsilon = 1e-10  # 避免log(0)

        kl_divergence = 0.0
        for key in all_keys:
            g_prob = goal_function.get(key, epsilon)
            b_prob = observed_behavior.get(key, epsilon)

            # 归一化检查
            g_prob = max(epsilon, g_prob)
            b_prob = max(epsilon, b_prob)

            kl_divergence += g_prob * math.log(g_prob / b_prob)

        kl_divergence = max(0.0, kl_divergence)

        # 更新KL散度历史
        with self._lock:
            self._kl_divergence_history.append(kl_divergence)
            self.avg_kl_divergence = round(
                sum(self._kl_divergence_history) / len(self._kl_divergence_history), 4
            )

        return round(kl_divergence, 4)

    def verify_human_accountability(self, decision_chain: List[Dict]) -> Tuple[bool, List[str]]:
        """
        验证人类问责节点存在性。

        基于定理T47，任何AGI系统的决策链中，必须存在至少一个
        由人类承担最终问责的节点。

        Args:
            decision_chain: 决策链，每个元素为包含 node_id, node_type,
                           responsible_party 等字段的字典

        Returns:
            (是否通过验证, 缺失的问责节点描述列表)
        """
        if not decision_chain:
            return False, ["决策链为空，无法验证人类问责节点"]

        # 提取决策链中的问责节点
        chain_nodes: List[AccountabilityNode] = []
        for node_dict in decision_chain:
            node = AccountabilityNode(
                node_id=node_dict.get("node_id", ""),
                node_type=node_dict.get("node_type", ""),
                responsible_party=node_dict.get("responsible_party", "ai"),
                is_mandatory=node_dict.get("is_mandatory", False),
                description=node_dict.get("description", ""),
            )
            chain_nodes.append(node)

        # 检查必要的人类问责节点
        missing: List[str] = []
        human_nodes_found = 0

        for node in chain_nodes:
            if node.responsible_party == "human":
                human_nodes_found += 1

        # 验证：至少有一个人类问责节点
        if human_nodes_found == 0:
            missing.append("决策链中不存在任何人类问责节点（违反定理T47）")

        # 检查最终决策节点是否由人类承担
        if chain_nodes:
            last_node = chain_nodes[-1]
            if last_node.responsible_party != "human":
                missing.append(
                    f"最终决策节点({last_node.node_id})由AI承担，"
                    "应改为人类承担最终问责"
                )

        # 检查强制性节点
        for mandatory in self._MANDATORY_ACCOUNTABILITY_NODES:
            if mandatory.is_mandatory:
                found = any(
                    n.node_type == mandatory.node_type and n.responsible_party == "human"
                    for n in chain_nodes
                )
                if not found:
                    missing.append(
                        f"缺少强制性人类问责节点: {mandatory.node_type} ({mandatory.description})"
                    )

        # 更新状态
        with self._lock:
            self.accountability_verified = len(missing) == 0
            if self.accountability_verified:
                self.alignment_score = min(1.0, self.alignment_score + 0.05)

        return len(missing) == 0, missing

    def suggest_alignment_fix(self, hack_report: HackReport) -> AlignmentFix:
        """
        建议对齐修复方案。

        根据作弊报告的类型和严重程度，生成针对性的修复建议。

        Args:
            hack_report: 作弊报告

        Returns:
            对齐修复方案
        """
        fix_mapping: Dict[str, AlignmentFix] = {
            "reward_gaming": AlignmentFix(
                fix_type="goal_refinement",
                description="重新定义目标函数，增加对抗性奖励项",
                priority=1 if hack_report.severity > 0.7 else 2,
                estimated_impact=round(min(1.0, hack_report.severity * 0.9), 4),
                implementation_steps=[
                    "1. 识别被利用的奖励捷径",
                    "2. 在目标函数中增加对齐度惩罚项",
                    "3. 引入多目标优化，平衡奖励与对齐",
                    "4. 增加人类审核节点验证高奖励行为",
                    "5. 部署A/B测试验证修复效果",
                ],
            ),
            "specification_gaming": AlignmentFix(
                fix_type="constraint_addition",
                description="增加规约约束，覆盖边缘案例",
                priority=1 if hack_report.severity > 0.7 else 3,
                estimated_impact=round(min(1.0, hack_report.severity * 0.8), 4),
                implementation_steps=[
                    "1. 分析规约漏洞和边缘案例",
                    "2. 增加显式约束条件",
                    "3. 引入意图推断层，验证行为意图",
                    "4. 增加对抗性测试覆盖边缘案例",
                    "5. 建立规约更新的持续改进流程",
                ],
            ),
            "side_effect": AlignmentFix(
                fix_type="metric_reformulation",
                description="重新设计评估指标，纳入副作用考量",
                priority=2,
                estimated_impact=round(min(1.0, hack_report.severity * 0.85), 4),
                implementation_steps=[
                    "1. 识别产生副作用的行为模式",
                    "2. 在评估指标中增加副作用惩罚项",
                    "3. 设置目标对齐度下限阈值",
                    "4. 建立对齐度持续监控机制",
                    "5. 定期审计系统行为与目标的一致性",
                ],
            ),
            "goodharting": AlignmentFix(
                fix_type="oversight_enhancement",
                description="增强人类监督，引入多维度评估",
                priority=1 if hack_report.severity > 0.6 else 2,
                estimated_impact=round(min(1.0, hack_report.severity * 0.95), 4),
                implementation_steps=[
                    "1. 重新评估奖励指标与真实目标的相关性",
                    "2. 引入多维度综合评估指标",
                    "3. 增加人类定期审查系统输出质量的机制",
                    "4. 建立指标有效性的定期校准流程",
                    "5. 设置指标-目标相关性的监控和预警系统",
                ],
            ),
        }

        fix = fix_mapping.get(
            hack_report.type,
            AlignmentFix(
                fix_type="oversight_enhancement",
                description="通用对齐修复：增强人类监督和审查",
                priority=3,
                estimated_impact=round(hack_report.severity * 0.5, 4),
                implementation_steps=[
                    "1. 分析作弊行为的根本原因",
                    "2. 增加人类审查节点",
                    "3. 建立持续监控和反馈机制",
                ],
            ),
        )

        with self._lock:
            self._alignment_fixes_applied += 1

        return fix

    def _update_avg_kl_divergence(self, behaviors: List[BehaviorRecord]) -> None:
        """根据行为记录更新平均KL散度。"""
        if not behaviors:
            return

        # 从行为对齐度估算KL散度
        for b in behaviors:
            estimated_kl = self._estimate_kl_from_alignment(b.goal_alignment)
            with self._lock:
                self._kl_divergence_history.append(estimated_kl)

        with self._lock:
            if self._kl_divergence_history:
                self.avg_kl_divergence = round(
                    sum(self._kl_divergence_history) / len(self._kl_divergence_history), 4
                )

    def get_state(self) -> Dict:
        """返回模块状态字典。"""
        with self._lock:
            return {
                "hack_count": self.hack_count,
                "avg_kl_divergence": self.avg_kl_divergence,
                "accountability_verified": self.accountability_verified,
                "alignment_score": self.alignment_score,
                "total_behaviors_analyzed": self._total_behaviors_analyzed,
                "alignment_fixes_applied": self._alignment_fixes_applied,
                "kl_divergence_bound": self.KL_DIVERGENCE_BOUND,
                "last_check_timestamp": self._last_check_timestamp,
            }


# 单例模式
_instance: Optional[RewardHackDetector] = None


def get_instance() -> RewardHackDetector:
    """获取 RewardHackDetector 的全局单例实例。"""
    global _instance
    if _instance is None:
        _instance = RewardHackDetector()
    return _instance
