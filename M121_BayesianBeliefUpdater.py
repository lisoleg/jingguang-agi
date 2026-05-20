# -*- coding: utf-8 -*-
"""
M121: 贝叶斯信念更新器 (Bayesian Belief Updater)
基于《荣枯鉴》贝叶斯博弈+声誉博弈

核心概念：先验信念、似然函数、后验信念、信念收敛
公式：P(H|E) = P(E|H)·P(H) / P(E)

定理T81（信念收敛定理）：在充分观测条件下，后验信念收敛到真实参数θ*

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


# ==================== 数据结构 ====================

@dataclass
class BeliefState:
    """
    信念状态 — 单个假设的贝叶斯信念

    hypothesis: 假设描述
    prior: 先验概率P(H)
    posterior: 后验概率P(H|E)
    likelihood: 似然函数P(E|H)
    evidence: 证据描述
    confidence: 信念置信度
    """
    hypothesis: str = ''
    prior: float = 0.5
    posterior: float = 0.5
    likelihood: float = 0.5
    evidence: str = ''
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['prior'] = round(self.prior, 6)
        d['posterior'] = round(self.posterior, 6)
        d['likelihood'] = round(self.likelihood, 6)
        d['confidence'] = round(self.confidence, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'BeliefState':
        """从字典构建BeliefState"""
        return cls(**d)


@dataclass
class BeliefNetwork:
    """
    信念网络 — 所有假设信念的综合状态

    hypotheses: 假设列表（每个含名称和概率）
    total_updates: 总更新次数
    convergence_rate: 收敛速率
    entropy: 信念熵
    """
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    total_updates: int = 0
    convergence_rate: float = 0.0
    entropy: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['convergence_rate'] = round(self.convergence_rate, 6)
        d['entropy'] = round(self.entropy, 6)
        return d


# ==================== 核心类 ====================

class BayesianBeliefUpdater:
    """
    M121: 贝叶斯信念更新器

    基于《荣枯鉴》贝叶斯博弈与声誉博弈，实现：
    - 贝叶斯信念更新 P(H|E) = P(E|H)·P(H) / P(E)
    - 批量贝叶斯更新
    - 信念熵计算 H = -Σ p_i log(p_i)
    - 信念收敛检测
    - 声誉博弈更新

    定理T81（信念收敛定理）：
    在充分观测条件下，后验信念收敛到真实参数θ*。
    即当观测数据量n→∞时，P(θ*|E_1,...,E_n)→1。

    核心方法：
    1. update_belief — 单个假设的贝叶斯更新
    2. batch_update — 批量贝叶斯更新
    3. compute_entropy — 信念熵计算
    4. check_convergence — 信念收敛检测
    5. reputation_update — 声誉博弈更新
    """

    def __init__(self):
        """初始化贝叶斯信念更新器"""
        # 信念表 {hypothesis: BeliefState}
        self.beliefs: Dict[str, BeliefState] = {}

        # 信念更新历史（用于收敛检测）
        self.update_history: Dict[str, List[float]] = {}

        # 声誉表 {player: reputation_score}
        self.reputations: Dict[str, float] = {}

        # 统计
        self.total_updates: int = 0
        self.total_batch_updates: int = 0
        self.total_entropy_computations: int = 0
        self.total_convergence_checks: int = 0
        self.total_reputation_updates: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def update_belief(self, hypothesis: str, evidence: str,
                      likelihood: float = 0.8) -> BeliefState:
        """
        贝叶斯信念更新 P(H|E)

        P(H|E) = P(E|H)·P(H) / P(E)

        其中：
        - P(H): 先验概率
        - P(E|H): 似然函数
        - P(E): 证据概率 = P(E|H)·P(H) + P(E|¬H)·P(¬H)
        - P(H|E): 后验概率

        定理T81保证：充分观测下后验收敛到真值。

        Args:
            hypothesis: 假设描述
            evidence: 证据描述
            likelihood: 似然P(E|H)

        Returns:
            BeliefState: 更新后的信念状态
        """
        # 获取先验（已存在则用后验作为新先验，否则默认0.5）
        if hypothesis in self.beliefs:
            prior = self.beliefs[hypothesis].posterior
        else:
            prior = 0.5

        # 边界保护
        prior = max(0.001, min(0.999, prior))
        likelihood = max(0.001, min(1.0, likelihood))

        # P(E|¬H): 非假设下观测到证据的概率
        # 简化假设：P(E|¬H) = 1 - likelihood（互补关系）
        likelihood_not_h = 1.0 - likelihood

        # P(E) = P(E|H)·P(H) + P(E|¬H)·P(¬H)
        p_e = likelihood * prior + likelihood_not_h * (1.0 - prior)
        p_e = max(0.001, p_e)

        # P(H|E) = P(E|H)·P(H) / P(E)
        posterior = (likelihood * prior) / p_e
        posterior = max(0.0, min(1.0, posterior))

        # 置信度：后验与先验的差距
        confidence = abs(posterior - prior)

        # 创建信念状态
        belief = BeliefState(
            hypothesis=hypothesis,
            prior=round(prior, 6),
            posterior=round(posterior, 6),
            likelihood=round(likelihood, 6),
            evidence=evidence,
            confidence=round(confidence, 6)
        )

        self.beliefs[hypothesis] = belief

        # 记录更新历史
        if hypothesis not in self.update_history:
            self.update_history[hypothesis] = []
        self.update_history[hypothesis].append(posterior)
        # 保留最近100次更新
        if len(self.update_history[hypothesis]) > 100:
            self.update_history[hypothesis] = self.update_history[hypothesis][-100:]

        self.total_updates += 1
        self.last_update = time.time()

        return belief

    def batch_update(self, hypotheses: List[str],
                     evidence_list: List[str]) -> List[BeliefState]:
        """
        批量贝叶斯更新

        对多个假设同时进行贝叶斯更新。
        每个假设与对应的证据配对更新。

        Args:
            hypotheses: 假设列表
            evidence_list: 证据列表

        Returns:
            更新后的信念状态列表
        """
        self.total_batch_updates += 1

        results = []
        for i, hyp in enumerate(hypotheses):
            ev = evidence_list[i] if i < len(evidence_list) else ''
            # 简化：每个假设的似然基于其在信念表中的历史
            if hyp in self.beliefs:
                likelihood = min(0.95, self.beliefs[hyp].likelihood * 1.1)
            else:
                likelihood = 0.7

            result = self.update_belief(hyp, ev, likelihood)
            results.append(result)

        self.last_update = time.time()
        return results

    def compute_entropy(self) -> float:
        """
        计算信念熵

        H = -Σ p_i log(p_i)

        信念熵衡量信念系统的不确定性：
        - H=0: 完全确定（某个假设概率为1）
        - H=log(n): 完全不确定（所有假设等概率）

        熵越低→信念越确定→知识状态越好

        Returns:
            信念熵值
        """
        self.total_entropy_computations += 1

        if not self.beliefs:
            return 0.0

        # 收集所有假设的后验概率
        probs = [b.posterior for b in self.beliefs.values()]
        # 归一化
        total = sum(probs)
        if total < 1e-10:
            return 0.0
        probs_norm = [p / total for p in probs]

        # H = -Σ p_i log2(p_i)
        entropy = 0.0
        for p in probs_norm:
            if p > 1e-10:
                entropy -= p * math.log2(p)

        entropy = round(max(0.0, entropy), 6)
        self.last_update = time.time()

        return entropy

    def check_convergence(self, threshold: float = 0.05) -> Dict[str, Any]:
        """
        检查信念是否收敛

        定理T81（信念收敛定理）：
        在充分观测条件下，后验信念收敛到真实参数θ*。

        收敛判定：最近N次更新的后验变化量 < threshold

        Args:
            threshold: 收敛阈值

        Returns:
            收敛检测结果字典
        """
        self.total_convergence_checks += 1

        convergence_results = {}
        overall_converged = True
        convergence_count = 0

        for hyp, history in self.update_history.items():
            if len(history) < 3:
                convergence_results[hyp] = {
                    'converged': False,
                    'reason': 'insufficient_data',
                    'variation': 1.0
                }
                overall_converged = False
                continue

            # 计算最近5次更新的变化量
            recent = history[-5:] if len(history) >= 5 else history
            if len(recent) >= 2:
                variation = max(recent) - min(recent)
            else:
                variation = 1.0

            converged = variation < threshold
            if converged:
                convergence_count += 1

            convergence_results[hyp] = {
                'converged': converged,
                'variation': round(variation, 6),
                'current_posterior': round(history[-1], 6),
                'updates': len(history)
            }

            if not converged:
                overall_converged = False

        # 收敛速率
        total_hypotheses = max(len(self.update_history), 1)
        convergence_rate = round(convergence_count / total_hypotheses, 6)

        self.last_update = time.time()

        return {
            'converged': overall_converged,
            'threshold': threshold,
            'convergence_rate': convergence_rate,
            'hypotheses_checked': len(convergence_results),
            'hypotheses_converged': convergence_count,
            'details': convergence_results,
            'theorem_T81': '信念收敛: 充分观测 ⟹ 后验→θ*'
        }

    def reputation_update(self, player: str, action: str,
                          observed: str = '') -> Dict[str, Any]:
        """
        声誉博弈更新

        基于行动观察的声誉推断：
        - 合作行为 → 声誉上升
        - 背叛行为 → 声誉下降
        - 声誉影响未来博弈中对手的策略选择

        声誉更新规则（简化贝叶斯）：
        - 观察到合作: rep_new = rep_old + α·(1-rep_old)
        - 观察到背叛: rep_new = rep_old - β·rep_old

        Args:
            player: 参与者名称
            action: 观察到的行动（cooperate/defect）
            observed: 观察描述

        Returns:
            声誉更新结果字典
        """
        self.total_reputation_updates += 1

        # 获取当前声誉
        current_rep = self.reputations.get(player, 0.5)

        # 声誉更新参数
        alpha = 0.3  # 合作带来的声誉增益
        beta = 0.5   # 背叛带来的声誉损失

        # 根据行动更新声誉
        if action == 'cooperate':
            new_rep = current_rep + alpha * (1.0 - current_rep)
        elif action == 'defect':
            new_rep = current_rep - beta * current_rep
        else:
            # 未知行动，小幅衰减
            new_rep = current_rep * 0.95

        new_rep = round(max(0.0, min(1.0, new_rep)), 6)
        self.reputations[player] = new_rep

        # 基于声誉推断类型
        if new_rep > 0.7:
            inferred_type = 'cooperative'
        elif new_rep > 0.4:
            inferred_type = 'conditional'
        else:
            inferred_type = 'uncooperative'

        # 声誉变化量
        rep_change = round(new_rep - current_rep, 6)

        self.last_update = time.time()

        return {
            'player': player,
            'action': action,
            'observed': observed,
            'previous_reputation': round(current_rep, 6),
            'new_reputation': new_rep,
            'reputation_change': rep_change,
            'inferred_type': inferred_type,
            'total_reputation_updates': self.total_reputation_updates
        }

    def get_state(self) -> Dict[str, Any]:
        """
        获取贝叶斯信念更新器状态

        Returns:
            状态字典
        """
        entropy = self.compute_entropy()

        # 构建信念网络状态
        hyp_list = []
        for name, belief in self.beliefs.items():
            hyp_list.append({
                'hypothesis': name,
                'prior': belief.prior,
                'posterior': belief.posterior,
                'confidence': belief.confidence
            })

        network = BeliefNetwork(
            hypotheses=hyp_list,
            total_updates=self.total_updates,
            convergence_rate=0.0,  # 需要check_convergence计算
            entropy=entropy
        )

        # 声誉汇总
        rep_summary = {k: round(v, 6) for k, v in self.reputations.items()}

        return {
            'beliefs': {k: v.to_dict() for k, v in self.beliefs.items()},
            'belief_network': network.to_dict(),
            'entropy': entropy,
            'reputations': rep_summary,
            'total_updates': self.total_updates,
            'total_batch_updates': self.total_batch_updates,
            'total_entropy_computations': self.total_entropy_computations,
            'total_convergence_checks': self.total_convergence_checks,
            'total_reputation_updates': self.total_reputation_updates,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T81': '信念收敛: 充分观测 ⟹ 后验→θ*'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新贝叶斯信念更新器状态

        Args:
            data: 可选更新数据，支持：
                - belief: 更新信念 {hypothesis, evidence, likelihood}
                - batch: 批量更新 {hypotheses, evidence_list}
                - reputation: 声誉更新 {player, action, observed}
                - convergence: 收敛检查 {threshold}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'belief' or 'belief' in data:
                b = data.get('belief', data)
                self.update_belief(
                    hypothesis=b.get('hypothesis', ''),
                    evidence=b.get('evidence', ''),
                    likelihood=float(b.get('likelihood', 0.8))
                )
            elif action == 'batch' or 'batch' in data:
                bt = data.get('batch', data)
                self.batch_update(
                    hypotheses=bt.get('hypotheses', []),
                    evidence_list=bt.get('evidence_list', [])
                )
            elif action == 'reputation' or 'reputation' in data:
                r = data.get('reputation', data)
                self.reputation_update(
                    player=r.get('player', ''),
                    action=r.get('action', ''),
                    observed=r.get('observed', '')
                )
            elif action == 'convergence' or 'convergence' in data:
                c = data.get('convergence', data)
                self.check_convergence(
                    threshold=float(c.get('threshold', 0.05))
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示贝叶斯信念更新器的核心功能"""
        # 1. 单个信念更新
        b1 = self.update_belief('市场上涨', '利好政策发布', 0.9)
        b2 = self.update_belief('市场上涨', '连续三天上涨', 0.85)

        # 2. 批量更新
        batch = self.batch_update(
            ['经济复苏', '通胀上升', '利率下调'],
            ['GDP增长超预期', 'CPI数据发布', '央行决议']
        )

        # 3. 熵计算
        entropy = self.compute_entropy()

        # 4. 收敛检查
        convergence = self.check_convergence(0.05)

        # 5. 声誉更新
        rep1 = self.reputation_update('player_A', 'cooperate', '第一轮合作')
        rep2 = self.reputation_update('player_A', 'cooperate', '第二轮合作')
        rep3 = self.reputation_update('player_B', 'defect', '背叛行为')

        return {
            'belief_updates': {
                'first': b1.to_dict(),
                'second': b2.to_dict()
            },
            'batch_update': [b.to_dict() for b in batch],
            'entropy': entropy,
            'convergence_T81': convergence,
            'reputation_updates': [rep1, rep2, rep3],
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[BayesianBeliefUpdater] = None


def get_instance() -> BayesianBeliefUpdater:
    """
    获取BayesianBeliefUpdater单例实例

    Returns:
        BayesianBeliefUpdater全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = BayesianBeliefUpdater()
    return _instance


def update_belief(hypothesis: str, evidence: str,
                  likelihood: float = 0.8) -> BeliefState:
    """贝叶斯信念更新（快捷接口）"""
    return get_instance().update_belief(hypothesis, evidence, likelihood)


def batch_update(hypotheses: List[str],
                 evidence_list: List[str]) -> List[BeliefState]:
    """批量贝叶斯更新（快捷接口）"""
    return get_instance().batch_update(hypotheses, evidence_list)


def compute_entropy() -> float:
    """计算信念熵（快捷接口）"""
    return get_instance().compute_entropy()


def check_convergence(threshold: float = 0.05) -> Dict[str, Any]:
    """检查信念收敛（快捷接口）"""
    return get_instance().check_convergence(threshold)


def reputation_update(player: str, action: str,
                      observed: str = '') -> Dict[str, Any]:
    """声誉博弈更新（快捷接口）"""
    return get_instance().reputation_update(player, action, observed)


def get_state() -> Dict[str, Any]:
    """获取贝叶斯信念更新器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新贝叶斯信念更新器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
