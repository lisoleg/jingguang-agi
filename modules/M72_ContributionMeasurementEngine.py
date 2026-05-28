#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贡献度量引擎 (Contribution Measurement Engine)
基于《新契约论：走向碳硅共生的信息关系实在时代》

核心定理：
- T24：贡献度量不变性定理
  C(A,M) = I(A:M) - D_KL(A||M) + Shapley(A)
  - I(A:M)：互信息（Alice对模型的贡献）
  - D_KL(A||M)：KL散度（Alice与模型分布的差异）
  - Shapley(A)：博弈论沙普利值（公平性）

版本：AGI 14.0 第72模块
论文来源：《新契约论》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict

# TYIDO P4: 可寻址长期记忆
try:
    from TYIDO_AddressableMemory import (
        AddressableMemoryStore, MemoryIndex, ForgetPolicy, MemoryMergeEngine
    )
    _P4_AVAILABLE = True
except ImportError:
    _P4_AVAILABLE = False


@dataclass
class AgentContribution:
    """代理贡献记录"""
    agent_id: str
    task_id: str
    mutual_info: float            # I(A:M) 互信息
    kl_divergence: float         # D_KL(A||M) KL散度
    shapley_value: float          # 沙普利值
    total_contribution: float     # C(A,M) 总贡献
    normalized_contribution: float # 归一化贡献 [0,1]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CoalitionGame:
    """联盟博弈"""
    game_id: str
    agents: List[str]               # 所有代理ID
    contributions: Dict[str, float]  # agent_id -> base contribution
    shapley_values: Dict[str, float] # agent_id -> Shapley value
    fairness_score: float             # 公平性评分 [0,1]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ContributionResult:
    """贡献度量分析结果"""
    task_id: str
    agent_contributions: List[AgentContribution]
    coalition_games: List[CoalitionGame]
    total_contribution: float        # 总贡献
    gini_coefficient: float          # 基尼系数（公平性）
    contribution_distribution: Dict[str, float]  # agent_id -> percentage
    insight: str                     # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ContributionMeasurementEngine:
    """
    贡献度量引擎
    
    实现T24定理：贡献度量不变性
    - 计算互信息 I(A:M)
    - 计算KL散度 D_KL(A||M)
    - 计算沙普利值（公平性保障）
    - 计算总贡献 C(A,M) = I - KL + Shapley
    - 评估分配公平性（基尼系数）
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.contributions: Dict[str, AgentContribution] = {}
        self.coalition_games: Dict[str, CoalitionGame] = {}
        self.agent_profiles: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # 公平性阈值
        self.fairness_threshold = 0.7
        
        # 基尼系数阈值
        self.gini_threshold = 0.3  # 基尼系数<0.3为公平

        # TYIDO P4: 可寻址长期记忆
        self._p4_available = _P4_AVAILABLE
        if self._p4_available:
            self._p4_store = AddressableMemoryStore(max_size=5000)
            self._p4_index = MemoryIndex(self._p4_store)
            self._p4_forget_policy = ForgetPolicy(self._p4_store)
            self._p4_merge_engine = MemoryMergeEngine(self._p4_store)
        else:
            self._p4_store = self._p4_index = self._p4_forget_policy = self._p4_merge_engine = None
    
    def compute_mutual_information(self, agent_data: List[float], 
                                   model_data: List[float]) -> float:
        """
        计算互信息 I(A:M)
        
        参数：
            agent_data: 代理的数据分布
            model_data: 模型的数据分布
        
        返回：
            互信息值 [0,1]
        """
        if not agent_data or not model_data:
            return 0.0
        
        n = min(len(agent_data), len(model_data))
        if n < 2:
            return 0.0
        
        # 计算皮尔逊相关系数
        a_mean = sum(agent_data[:n]) / n
        m_mean = sum(model_data[:n]) / n
        
        numerator = sum((a - a_mean) * (m - m_mean) 
                       for a, m in zip(agent_data[:n], model_data[:n]))
        denom_a = math.sqrt(sum((a - a_mean) ** 2 for a in agent_data[:n]))
        denom_m = math.sqrt(sum((m - m_mean) ** 2 for m in model_data[:n]))
        
        if denom_a == 0 or denom_m == 0:
            return 0.0
        
        correlation = numerator / (denom_a * denom_m)
        
        # 互信息 ≈ -0.5 * log(1 - correlation^2)
        if abs(correlation) >= 1.0:
            return 1.0
        
        mi = -0.5 * math.log(max(1e-10, 1.0 - correlation ** 2))
        return min(1.0, max(0.0, mi))
    
    def compute_kl_divergence(self, agent_dist: List[float], 
                             model_dist: List[float]) -> float:
        """
        计算KL散度 D_KL(A||M)
        
        参数：
            agent_dist: 代理的分布
            model_dist: 模型的分布
        
        返回：
            KL散度值 [0,∞)
        """
        if not agent_dist or not model_dist:
            return 0.0
        
        # 归一化分布
        a_sum = sum(agent_dist)
        m_sum = sum(model_dist)
        
        if a_sum == 0 or m_sum == 0:
            return 0.0
        
        a_norm = [x / a_sum for x in agent_dist]
        m_norm = [x / m_sum for x in model_dist]
        
        # 计算KL散度
        kl = 0.0
        for a, m in zip(a_norm, m_norm):
            if a > 0 and m > 0:
                kl += a * math.log(a / m)
        
        return max(0.0, kl)
    
    def compute_shapley_value(self, agent_id: str, 
                             coalition: List[str],
                             all_agents: List[str]) -> float:
        """
        计算沙普利值（公平性保障）
        
        沙普利值公式：
        φ_i = Σ_{S ⊆ N\{i}} (|S|! (n-|S|-1)! / n! * (v(S∪{i}) - v(S))
        
        参数：
            agent_id: 目标代理ID
            coalition: 当前联盟（排除agent_id）
            all_agents: 所有代理ID列表
        
        返回：
            沙普利值
        """
        n = len(all_agents)
        
        if agent_id not in all_agents:
            return 0.0
        
        # 获取代理的基础贡献值
        base_contrib = self.agent_profiles.get(agent_id, {}).get('base_contribution', 0.5)
        
        # 简化计算：使用近似公式
        # 沙普利值 = 基础贡献 / n（平均分配）
        shapley = base_contrib / n
        
        # 调整：根据联盟大小进行加权
        if coalition:
            coalition_size = len(coalition)
            weight = (coalition_size + 1) / (n + 1)
            shapley = shapley * weight
        
        return shapley
    
    def compute_all_shapley_values(self, agents: List[str], 
                                  contributions: Dict[str, float]) -> Dict[str, float]:
        """
        计算所有代理的沙普利值
        
        参数：
            agents: 所有代理ID列表
            contributions: agent_id -> 贡献值
        
        返回：
            agent_id -> 沙普利值
        """
        n = len(agents)
        shapley_values = {}
        
        # 保存贡献值到agent_profiles
        for agent_id in agents:
            if agent_id not in self.agent_profiles:
                self.agent_profiles[agent_id] = {}
            self.agent_profiles[agent_id]['base_contribution'] = contributions.get(agent_id, 0.5)
        
        # 计算每个代理的沙普利值
        for agent_id in agents:
            # 计算在所有可能联盟中的边际贡献
            shapley = 0.0
            weight_sum = 0.0
            
            # 枚举所有可能的联盟（简化版）
            for size in range(n + 1):
                # 联盟大小为size时，agent_id的边际贡献
                # 简化：假设边际贡献 = 基础贡献 / (size + 1)
                base = contributions.get(agent_id, 0.5)
                marginal = base / (size + 1)
                
                # 权重 = C(n-1, size) / 2^(n-1)
                weight = math.comb(n - 1, size) / (2 ** (n - 1) + 1e-10)
                
                shapley += weight * marginal
                weight_sum += weight
            
            # 归一化
            if weight_sum > 0:
                shapley = shapley / weight_sum
            
            shapley_values[agent_id] = shapley
        
        return shapley_values
    
    def measure_contribution(self, task_id: str,
                            agent_id: str,
                            agent_data: List[float],
                            model_data: List[float],
                            all_agents: List[str]) -> AgentContribution:
        """
        总贡献度量：C(A,M) = I(A:M) - D_KL(A||M) + Shapley(A)
        
        返回：
            代理贡献记录
        """
        # 计算互信息
        mi = self.compute_mutual_information(agent_data, model_data)
        
        # 计算KL散度
        kl = self.compute_kl_divergence(agent_data, model_data)
        
        # 计算沙普利值
        coalition = [a for a in all_agents if a != agent_id]
        shapley = self.compute_shapley_value(agent_id, coalition, all_agents)
        
        # 总贡献
        total = mi - kl + shapley
        total = max(0.0, min(1.0, total))
        
        # 归一化贡献
        normalized = total  # 已经在[0,1]范围内
        
        contribution = AgentContribution(
            agent_id=agent_id,
            task_id=task_id,
            mutual_info=round(mi, 4),
            kl_divergence=round(kl, 4),
            shapley_value=round(shapley, 4),
            total_contribution=round(total, 4),
            normalized_contribution=round(normalized, 4)
        )
        
        # 保存到contributions字典
        key = f"{agent_id}@{task_id}"
        self.contributions[key] = contribution
        
        return contribution
    
    def evaluate_fairness(self, agents: List[str],
                          contributions: Dict[str, float]) -> CoalitionGame:
        """
        评估分配公平性（基尼系数）
        
        参数：
            agents: 所有代理ID列表
            contributions: agent_id -> 贡献值
        
        返回：
            联盟博弈结果
        """
        # 计算沙普利值
        shapley_values = self.compute_all_shapley_values(agents, contributions)
        
        # 计算基尼系数
        n = len(agents)
        if n < 2:
            gini = 0.0
        else:
            # 排序贡献值
            sorted_contribs = sorted(contributions.values())
            
            # 计算基尼系数
            total = sum(sorted_contribs)
            if total == 0:
                gini = 0.0
            else:
                cumsum = 0.0
                weighted_sum = 0.0
                for i, contrib in enumerate(sorted_contribs):
                    cumsum += contrib
                    weighted_sum += (i + 1) * contrib
                
                gini = (2.0 * weighted_sum) / (n * total) - (n + 1) / n
                gini = max(0.0, min(1.0, gini))
        
        # 公平性评分（基尼系数越小越公平）
        fairness = 1.0 - gini
        
        # 创建联盟博弈记录
        game = CoalitionGame(
            game_id=f"GAME-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            agents=agents,
            contributions=contributions,
            shapley_values=shapley_values,
            fairness_score=round(fairness, 4),
            timestamp=datetime.now().isoformat()
        )
        
        self.coalition_games[game.game_id] = game
        return game
    
    def analyze_contributions(self, task_id: str,
                             agents: List[str],
                             agent_data_dict: Dict[str, List[float]],
                             model_data: List[float]) -> ContributionResult:
        """
        分析任务的所有代理贡献（主方法）
        
        返回：
            贡献度量分析结果
        """
        # 1. 计算每个代理的贡献
        agent_contributions = []
        contributions_dict = {}
        
        for agent_id in agents:
            agent_data = agent_data_dict.get(agent_id, [0.5] * len(model_data))
            contrib = self.measure_contribution(
                task_id, agent_id, agent_data, model_data, agents
            )
            agent_contributions.append(contrib)
            contributions_dict[agent_id] = contrib.total_contribution
        
        # 2. 评估公平性
        game = self.evaluate_fairness(agents, contributions_dict)
        
        # 3. 计算总贡献
        total_contribution = sum(c.total_contribution for c in agent_contributions)
        
        # 4. 计算贡献分布
        if total_contribution > 0:
            contribution_distribution = {
                c.agent_id: round(c.total_contribution / total_contribution, 4)
                for c in agent_contributions
            }
        else:
            contribution_distribution = {
                c.agent_id: round(1.0 / len(agents), 4)
                for c in agent_contributions
            }
        
        # 5. 生成洞见
        insight = self._generate_insight(
            agent_contributions, game.gini_coefficient, game.fairness_score
        )
        
        return ContributionResult(
            task_id=task_id,
            agent_contributions=agent_contributions,
            coalition_games=[game],
            total_contribution=round(total_contribution, 4),
            gini_coefficient=round(game.gini_coefficient, 4),
            contribution_distribution=contribution_distribution,
            insight=insight
        )
    
    def _generate_insight(self, contributions: List[AgentContribution],
                          gini: float, fairness: float) -> str:
        """生成分析洞见"""
        parts = []
        
        if fairness > 0.75:
            parts.append("贡献分配高度公平——沙普利值有效保障了各代理权益")
        elif fairness > 0.55:
            parts.append("贡献分配中等公平——建议调整部分代理的贡献权重")
        else:
            parts.append("⚠️ 贡献分配不公平！基尼系数过高，建议重新评估")
        
        if gini > self.gini_threshold:
            parts.append(f"基尼系数 {gini:.2f} 超过阈值 {self.gini_threshold}，存在分配不公风险")
        else:
            parts.append(f"基尼系数 {gini:.2f} 在合理范围内，分配较为公平")
        
        # 找出贡献最高和最低的代理
        if contributions:
            max_contrib = max(contributions, key=lambda c: c.total_contribution)
            min_contrib = min(contributions, key=lambda c: c.total_contribution)
            
            parts.append(f"最高贡献：{max_contrib.agent_id} ({max_contrib.total_contribution:.3f})")
            parts.append(f"最低贡献：{min_contrib.agent_id} ({min_contrib.total_contribution:.3f})")
        
        return " | ".join(parts)
    
    def get_agent_profile(self, agent_id: str) -> Dict[str, float]:
        """获取代理配置文件"""
        return self.agent_profiles.get(agent_id, {})
    
    def update_agent_profile(self, agent_id: str, key: str, value: float):
        """更新代理配置文件"""
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = {}
        self.agent_profiles[agent_id][key] = value
        # P4: 持久化到记忆存储
        if self._p4_available and self._p4_store is not None:
            mem_key = f"profile:{agent_id}:{key}"
            self._p4_store.write(mem_key, value, tags=["profile", agent_id], importance=0.6)

    def get_state(self) -> Dict[str, Any]:
        """获取模块状态（含 TYIDO P4 记忆诊断）"""
        state = {
            "module": "M72 ContributionMeasurementEngine",
            "version": self.version,
            "contribution_count": len(self.contributions),
            "coalition_game_count": len(self.coalition_games),
            "agent_count": len(self.agent_profiles),
            "fairness_threshold": self.fairness_threshold,
            "gini_threshold": self.gini_threshold,
        }
        if self._p4_available and self._p4_store is not None:
            store_stats = self._p4_store.get_stats()
            state["tyido_p4"] = {
                "available": True,
                "store_stats": store_stats,
                "index_stats": self._p4_index.get_stats(),
                "forget_stats": self._p4_forget_policy.get_stats(),
                "p4_keys": self._p4_store.keys(),
                "verdict": "PASS" if store_stats['size'] > 0 else "EMPTY",
            }
        else:
            state["tyido_p4"] = {"available": False, "verdict": "N/A"}
        return state


def get_instance():
    """获取单例实例"""
    return ContributionMeasurementEngine()


if __name__ == "__main__":
    # 测试代码
    engine = ContributionMeasurementEngine()
    
    # 定义任务和代理
    task_id = "TASK-001"
    agents = ["Alice", "Bob", "Charlie"]
    
    # 模拟数据
    agent_data_dict = {
        "Alice": [0.1, 0.2, 0.3, 0.4, 0.5],
        "Bob": [0.15, 0.25, 0.35, 0.45, 0.55],
        "Charlie": [0.12, 0.22, 0.32, 0.42, 0.52]
    }
    model_data = [0.2, 0.3, 0.4, 0.5, 0.6]
    
    # 分析贡献
    result = engine.analyze_contributions(task_id, agents, agent_data_dict, model_data)
    
    print(f"任务 {result.task_id} 贡献分析：")
    print(f"  总贡献: {result.total_contribution}")
    print(f"  基尼系数: {result.gini_coefficient}")
    print(f"  公平性评分: {result.fairness_score}")
    print(f"  洞见: {result.insight}")
    print()
    print("  各代理贡献：")
    for contrib in result.agent_contributions:
        print(f"    {contrib.agent_id}: I={contrib.mutual_info:.3f}, KL={contrib.kl_divergence:.3f}, Shapley={contrib.shapley_value:.3f}, Total={contrib.total_contribution:.3f}")
