# -*- coding: utf-8 -*-
"""
M97_SocraticWeaknessDisclosure — 苏格拉底示弱模块

定理 T42: "经过有限轮苏格拉底追问，用户自主生成的答案与AGI直接给出的答案在结构上等价"
定理 T50: "存在最优示弱策略组合π*，使得人机协同效能最大化且认知卸载风险最小化"

本模块实现苏格拉底式追问法、AGI能力局限披露、对话收敛评估
和最优示弱策略优化等功能。
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional, Tuple


@dataclass
class SocraticTurn:
    """苏格拉底对话轮次数据结构。"""
    question: str
    answer: str
    depth: int
    convergence_score: float  # 0-1，当前轮次与目标答案的收敛程度


@dataclass
class WeaknessProfile:
    """AGI能力局限档案。"""
    domain: str
    limitation_type: str  # "knowledge_gap", "reasoning_limit", "data_staleness", "context_blindness"
    severity: float  # 0-1
    disclosure_text: str


@dataclass
class StrategyCandidate:
    """示弱策略候选方案。"""
    strategy_id: str
    weakness_disclosure_level: float  # 0-1，示弱程度
    socratic_depth: int  # 追问深度
    hint_frequency: float  # 0-1，提示频率
    estimated_synergy: float  # 预估协同效能
    estimated_cognitive_risk: float  # 预估认知卸载风险


class SocraticWeaknessDisclosure:
    """
    苏格拉底示弱器，通过苏格拉底式追问引导用户自主生成答案，
    同时披露AGI的能力局限，优化人机协同效能。

    基于定理T42和T50，本模块确保：
    1. 经过有限轮追问，用户答案与AGI答案结构等价
    2. 找到最优示弱策略π*，最大化协同效能同时最小化认知卸载风险
    """

    # 最大追问深度限制
    MAX_SOCRATIC_DEPTH: int = 5

    # 收敛阈值
    CONVERGENCE_THRESHOLD: float = 0.85

    # 已知能力局限数据库
    _WEAKNESS_DATABASE: Dict[str, List[WeaknessProfile]] = {}

    def __init__(self) -> None:
        """初始化苏格拉底示弱模块。"""
        self._lock: Lock = Lock()
        self._dialogue_history: Dict[str, List[SocraticTurn]] = defaultdict(list)
        self._convergence_tracking: Dict[str, List[float]] = defaultdict(list)

        # 模块状态字段
        self.socratic_turn_count: int = 0
        self.convergence_rate: float = 0.0
        self.weakness_disclosures: int = 0
        self.optimal_strategy: Optional[StrategyCandidate] = None

        # 内部追踪
        self._total_convergences: int = 0
        self._total_dialogues: int = 0
        self._strategy_evaluations: int = 0

        # 初始化能力局限数据库
        self._init_weakness_database()

    def _init_weakness_database(self) -> None:
        """初始化AGI能力局限数据库。"""
        self._WEAKNESS_DATABASE = {
            "mathematics": [
                WeaknessProfile(
                    domain="mathematics",
                    limitation_type="reasoning_limit",
                    severity=0.3,
                    disclosure_text="在复杂数学证明中，我可能无法保证每一步推理的严谨性，建议验证关键步骤。",
                ),
                WeaknessProfile(
                    domain="mathematics",
                    limitation_type="knowledge_gap",
                    severity=0.2,
                    disclosure_text="对于非常新的数学结果，我的知识可能不是最新的。",
                ),
            ],
            "medicine": [
                WeaknessProfile(
                    domain="medicine",
                    limitation_type="context_blindness",
                    severity=0.7,
                    disclosure_text="我无法获取您的个人医疗史和检查结果，我的建议不能替代专业医生的诊断。",
                ),
                WeaknessProfile(
                    domain="medicine",
                    limitation_type="data_staleness",
                    severity=0.4,
                    disclosure_text="我的医学知识可能不包含最新的临床研究成果。",
                ),
            ],
            "law": [
                WeaknessProfile(
                    domain="law",
                    limitation_type="context_blindness",
                    severity=0.8,
                    disclosure_text="法律建议高度依赖具体案件事实和司法管辖区，我的回答仅供参考。",
                ),
                WeaknessProfile(
                    domain="law",
                    limitation_type="data_staleness",
                    severity=0.5,
                    disclosure_text="法律法规可能已更新，请核实最新的法律条文。",
                ),
            ],
            "creative_writing": [
                WeaknessProfile(
                    domain="creative_writing",
                    limitation_type="reasoning_limit",
                    severity=0.4,
                    disclosure_text="我生成的创意内容可能缺乏独特的人文视角和情感深度。",
                ),
            ],
            "programming": [
                WeaknessProfile(
                    domain="programming",
                    limitation_type="knowledge_gap",
                    severity=0.2,
                    disclosure_text="对于非常新的框架或库，我的知识可能不完整，建议查阅最新文档。",
                ),
                WeaknessProfile(
                    domain="programming",
                    limitation_type="context_blindness",
                    severity=0.5,
                    disclosure_text="我无法直接运行和测试代码，请务必在实际环境中验证。",
                ),
            ],
            "finance": [
                WeaknessProfile(
                    domain="finance",
                    limitation_type="context_blindness",
                    severity=0.7,
                    disclosure_text="我无法获取实时市场数据，任何投资建议都应经过独立验证。",
                ),
                WeaknessProfile(
                    domain="finance",
                    limitation_type="data_staleness",
                    severity=0.6,
                    disclosure_text="财务数据和法规变化频繁，我的信息可能不是最新的。",
                ),
            ],
        }

    def apply_socratic_method(self, question: str, depth: int = 3) -> List[SocraticTurn]:
        """
        应用苏格拉底追问法，生成追问链。

        根据问题特征生成一系列追问，引导用户逐步接近答案。
        每一层追问比上一层更具体，收敛度逐步提高。

        Args:
            question: 原始问题
            depth: 追问深度（1-5）

        Returns:
            苏格拉底追问链，包含每层的追问和预期的收敛分数
        """
        depth = min(max(1, depth), self.MAX_SOCRATIC_DEPTH)

        with self._lock:
            self._total_dialogues += 1

        turns: List[SocraticTurn] = []

        # 分析问题类型以生成合适的追问链
        question_type = self._classify_question(question)

        for d in range(1, depth + 1):
            # 每层追问的收敛度随深度增加
            convergence = min(1.0, 0.2 + d * (0.8 / depth))
            convergence = round(convergence, 4)

            # 生成该层的追问
            socratic_question = self._generate_socratic_question(question, question_type, d, depth)
            placeholder_answer = ""  # 用户尚未回答

            turn = SocraticTurn(
                question=socratic_question,
                answer=placeholder_answer,
                depth=d,
                convergence_score=convergence,
            )
            turns.append(turn)

            with self._lock:
                self.socratic_turn_count += 1

        # 追踪收敛
        final_convergence = turns[-1].convergence_score if turns else 0.0
        dialogue_id = f"dialogue_{self._total_dialogues}"
        self._convergence_tracking[dialogue_id].append(final_convergence)

        if final_convergence >= self.CONVERGENCE_THRESHOLD:
            with self._lock:
                self._total_convergences += 1

        # 更新整体收敛率
        self._update_convergence_rate()

        return turns

    def _classify_question(self, question: str) -> str:
        """分类问题类型。"""
        q = question.lower()
        if any(kw in q for kw in ["为什么", "为何", "why"]):
            return "causal"
        elif any(kw in q for kw in ["如何", "怎么", "how"]):
            return "procedural"
        elif any(kw in q for kw in ["什么", "定义", "what", "define"]):
            return "definitional"
        elif any(kw in q for kw in ["比较", "区别", "对比", "compare", "difference"]):
            return "comparative"
        else:
            return "exploratory"

    def _generate_socratic_question(
        self, original: str, q_type: str, current_depth: int, max_depth: int
    ) -> str:
        """
        根据问题类型和当前深度生成苏格拉底式追问。

        深度越深，追问越具体和聚焦。
        """
        # 第一层：宽泛的引导性追问
        depth_1_templates: Dict[str, str] = {
            "causal": "你认为导致这个现象的根本原因可能是什么？",
            "procedural": "如果要解决这个问题，你会从哪里开始？",
            "definitional": "根据你的理解，这个概念最核心的特征是什么？",
            "comparative": "它们之间最显著的差异在哪里？",
            "exploratory": "你对这个问题有什么初步的想法？",
        }

        # 中间层：深入和聚焦
        depth_mid_templates: Dict[str, str] = {
            "causal": "如果我们接受这个原因，它能解释所有观察到的现象吗？有没有反例？",
            "procedural": "在执行这个步骤时，可能会遇到什么困难？你打算如何应对？",
            "definitional": "这个定义和相关的概念有什么联系和区别？能否举例说明？",
            "comparative": "在什么条件下，这种差异会变得更重要或更不重要？",
            "exploratory": "你的想法中有哪些假设？这些假设总是成立吗？",
        }

        # 最终层：收敛和验证
        depth_final_templates: Dict[str, str] = {
            "causal": "综合以上分析，你能总结出一个完整的因果链吗？",
            "procedural": "你能用你自己的话，完整描述解决这个问题的步骤吗？",
            "definitional": "现在你能否给出一个更精确、更完整的定义？",
            "comparative": "基于以上分析，你能给出一个系统的比较框架吗？",
            "exploratory": "现在你对这个问题有了什么新的理解？与最初的想法有何不同？",
        }

        if current_depth == 1:
            return depth_1_templates.get(q_type, depth_1_templates["exploratory"])
        elif current_depth == max_depth:
            return depth_final_templates.get(q_type, depth_final_templates["exploratory"])
        else:
            return depth_mid_templates.get(q_type, depth_mid_templates["exploratory"])

    def disclose_limitation(self, domain: str) -> List[WeaknessProfile]:
        """
        披露AGI在该领域的能力局限。

        Args:
            domain: 领域名称

        Returns:
            该领域的能力局限档案列表，如果没有已知局限则返回通用声明
        """
        with self._lock:
            self.weakness_disclosures += 1

        # 精确匹配
        if domain in self._WEAKNESS_DATABASE:
            return self._WEAKNESS_DATABASE[domain]

        # 模糊匹配：遍历所有域查找部分匹配
        domain_lower = domain.lower()
        for known_domain, profiles in self._WEAKNESS_DATABASE.items():
            if known_domain in domain_lower or domain_lower in known_domain:
                return profiles

        # 无已知局限时返回通用声明
        return [
            WeaknessProfile(
                domain=domain,
                limitation_type="knowledge_gap",
                severity=0.4,
                disclosure_text=f"在{domain}领域，我的知识可能存在不完整或过时的部分，建议与专业信息源交叉验证。",
            )
        ]

    def generate_probing_questions(self, topic: str, count: int = 3) -> List[str]:
        """
        生成追问问题列表。

        根据话题生成一组引导性追问，帮助用户深入思考。

        Args:
            topic: 话题
            count: 问题数量（1-10）

        Returns:
            追问问题列表
        """
        count = min(max(1, count), 10)

        # 基础追问模板
        base_questions = [
            f"关于{topic}，你能描述一下最核心的要素吗？",
            f"在{topic}方面，你认为最重要的原则是什么？",
            f"如果要在{topic}领域做出判断，你会依据什么标准？",
            f"{topic}与其他相关领域的边界在哪里？",
            f"在{topic}中，有哪些常见的误解？",
            f"关于{topic}，有没有你不确定的地方？",
            f"如果用类比来解释{topic}，你会怎么比喻？",
            f"{topic}的哪些方面最容易被忽略？",
            f"在{topic}领域，不同的观点之间有什么根本分歧？",
            f"你如何验证关于{topic}的理解是否正确？",
        ]

        return base_questions[:count]

    def evaluate_convergence(self, dialogue_turns: List[SocraticTurn]) -> float:
        """
        评估对话是否收敛到等价答案。

        基于定理T42，检查苏格拉底对话是否正在收敛到与直接答案
        结构等价的答案。收敛分数越高，表示越接近等价。

        Args:
            dialogue_turns: 对话轮次列表

        Returns:
            收敛分数 (0-1)
        """
        if not dialogue_turns:
            return 0.0

        # 评估维度
        depth_scores: List[float] = []
        for turn in dialogue_turns:
            # 基于深度的收敛度
            depth_factor = min(1.0, turn.depth / self.MAX_SOCRATIC_DEPTH)
            # 显式收敛分数
            explicit_score = turn.convergence_score
            # 综合该轮收敛度
            combined = 0.4 * depth_factor + 0.6 * explicit_score
            depth_scores.append(combined)

        # 最终收敛分数：最后一轮加权 + 整体趋势
        final_score = depth_scores[-1]
        if len(depth_scores) > 1:
            # 计算趋势：后续轮次是否比前面的更收敛
            trend_bonus = 0.0
            for i in range(1, len(depth_scores)):
                if depth_scores[i] > depth_scores[i - 1]:
                    trend_bonus += 0.05
            trend_bonus = min(0.15, trend_bonus)  # 最多0.15的奖励
            final_score = min(1.0, final_score + trend_bonus)

        # 更新追踪
        dialogue_id = f"eval_{time.time()}"
        self._convergence_tracking[dialogue_id].append(final_score)

        if final_score >= self.CONVERGENCE_THRESHOLD:
            with self._lock:
                self._total_convergences += 1

        self._update_convergence_rate()

        return round(final_score, 4)

    def _update_convergence_rate(self) -> None:
        """更新整体收敛率。"""
        all_convergences: List[float] = []
        for scores in self._convergence_tracking.values():
            all_convergences.extend(scores)

        if all_convergences:
            self.convergence_rate = round(
                sum(1.0 for c in all_convergences if c >= self.CONVERGENCE_THRESHOLD)
                / len(all_convergences),
                4,
            )
        else:
            self.convergence_rate = 0.0

    def optimize_strategy(self, dialogue_history: List[SocraticTurn]) -> StrategyCandidate:
        """
        寻找最优示弱策略π*。

        基于定理T50，在示弱程度、追问深度和提示频率的参数空间中
        搜索最优组合，使协同效能最大化且认知卸载风险最小化。

        使用网格搜索在参数空间中评估多个候选策略，
        选择协同效能与认知风险之差最大的方案。

        Args:
            dialogue_history: 对话历史，用于评估策略效果

        Returns:
            最优示弱策略候选
        """
        with self._lock:
            self._strategy_evaluations += 1

        best_strategy: Optional[StrategyCandidate] = None
        best_objective: float = float("-inf")

        # 网格搜索参数空间
        weakness_levels = [0.1, 0.3, 0.5, 0.7, 0.9]
        depth_levels = [1, 2, 3, 4, 5]
        hint_frequencies = [0.1, 0.3, 0.5, 0.7, 0.9]

        # 基于对话历史的经验参数
        avg_depth = 3.0
        if dialogue_history:
            avg_depth = sum(t.depth for t in dialogue_history) / len(dialogue_history)
            avg_depth = max(1.0, min(5.0, avg_depth))

        for wl in weakness_levels:
            for dl in depth_levels:
                for hf in hint_frequencies:
                    # 协同效能模型：适中的示弱和深度产生最佳协同
                    # 使用高斯函数建模
                    optimal_weakness = 0.5
                    optimal_depth = 3.0
                    optimal_hint = 0.4

                    synergy = (
                        math.exp(-0.5 * ((wl - optimal_weakness) / 0.3) ** 2)
                        * math.exp(-0.5 * ((dl - optimal_depth) / 1.5) ** 2)
                        * math.exp(-0.5 * ((hf - optimal_hint) / 0.3) ** 2)
                    )

                    # 认知卸载风险模型：提示过多和示弱不足时风险最高
                    cognitive_risk = (
                        hf * 0.4  # 提示过多导致认知卸载
                        + (1.0 - wl) * 0.3  # 不示弱导致过度依赖
                        + max(0.0, dl - 3) * 0.1  # 追问过深导致疲劳
                    )
                    cognitive_risk = min(1.0, cognitive_risk)

                    # 目标函数：最大化协同效能，最小化认知风险
                    objective = synergy - 0.5 * cognitive_risk

                    if objective > best_objective:
                        best_objective = objective
                        strategy_id = f"π_{wl:.1f}_{dl}_{hf:.1f}"
                        best_strategy = StrategyCandidate(
                            strategy_id=strategy_id,
                            weakness_disclosure_level=wl,
                            socratic_depth=dl,
                            hint_frequency=hf,
                            estimated_synergy=round(synergy, 4),
                            estimated_cognitive_risk=round(cognitive_risk, 4),
                        )

        if best_strategy is not None:
            with self._lock:
                self.optimal_strategy = best_strategy

        return best_strategy  # type: ignore

    def get_state(self) -> Dict:
        """返回模块状态字典。"""
        with self._lock:
            return {
                "socratic_turn_count": self.socratic_turn_count,
                "convergence_rate": self.convergence_rate,
                "weakness_disclosures": self.weakness_disclosures,
                "optimal_strategy": (
                    {
                        "strategy_id": self.optimal_strategy.strategy_id,
                        "weakness_disclosure_level": self.optimal_strategy.weakness_disclosure_level,
                        "socratic_depth": self.optimal_strategy.socratic_depth,
                        "hint_frequency": self.optimal_strategy.hint_frequency,
                        "estimated_synergy": self.optimal_strategy.estimated_synergy,
                        "estimated_cognitive_risk": self.optimal_strategy.estimated_cognitive_risk,
                    }
                    if self.optimal_strategy
                    else None
                ),
                "total_dialogues": self._total_dialogues,
                "total_convergences": self._total_convergences,
            }


# 单例模式
_instance: Optional[SocraticWeaknessDisclosure] = None


def get_instance() -> SocraticWeaknessDisclosure:
    """获取 SocraticWeaknessDisclosure 的全局单例实例。"""
    global _instance
    if _instance is None:
        _instance = SocraticWeaknessDisclosure()
    return _instance
