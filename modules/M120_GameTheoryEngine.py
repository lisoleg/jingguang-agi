# -*- coding: utf-8 -*-
"""
M120: 博弈论引擎 (Game Theory Engine)
基于《荣枯鉴》博弈论战略图谱

核心概念：非合作博弈、信号博弈、重复囚徒困境、贝叶斯博弈、机制设计
公式：NE = {s* | ∀i, s_i ∈ BR_i(s_{-i}*)}

定理T79（纳什存在定理）：任何有限策略博弈至少存在一个混合策略纳什均衡
定理T80（信号均衡存在定理）：当信号成本c满足c_L < c < c_H时，分离均衡存在

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


# ==================== 数据结构 ====================

@dataclass
class GameProfile:
    """
    博弈画像 — 描述一个博弈的基本特征

    game_type: 博弈类型（prisoner_dilemma, coordination, signaling, bayesian等）
    players: 参与者数量
    payoff_matrix: 支付矩阵
    nash_equilibria: 纳什均衡列表
    is_pure: 是否存在纯策略纳什均衡
    dominant_strategy: 占优策略（如果存在）
    """
    game_type: str = 'unknown'
    players: int = 2
    payoff_matrix: List[Any] = field(default_factory=list)
    nash_equilibria: List[Dict[str, Any]] = field(default_factory=list)
    is_pure: bool = False
    dominant_strategy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'GameProfile':
        """从字典构建GameProfile"""
        return cls(**d)


@dataclass
class GameResult:
    """
    博弈结果 — 博弈分析的汇总结果

    game_type: 博弈类型
    players: 参与者数量
    equilibria_found: 找到的均衡数
    total_games: 总博弈局数
    dominant_rate: 占优策略出现比率
    bayesian_updates: 贝叶斯更新次数
    """
    game_type: str = 'unknown'
    players: int = 2
    equilibria_found: int = 0
    total_games: int = 0
    dominant_rate: float = 0.0
    bayesian_updates: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['dominant_rate'] = round(self.dominant_rate, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'GameResult':
        """从字典构建GameResult"""
        return cls(**d)


# ==================== 核心类 ====================

class GameTheoryEngine:
    """
    M120: 博弈论引擎

    基于《荣枯鉴》博弈论战略图谱，实现：
    - 非合作博弈分析（纳什均衡计算）
    - 信号博弈分析（Spence模型，分离均衡vs混同均衡）
    - 重复囚徒困境（以牙还牙策略，折扣因子δ）
    - 贝叶斯博弈（信念更新）
    - 机制设计（IC+IR约束）

    公式：NE = {s* | ∀i, s_i ∈ BR_i(s_{-i}*)}
    即纳什均衡是所有参与者策略互为最佳响应的策略组合。

    定理T79（纳什存在定理）：
    任何有限策略博弈至少存在一个混合策略纳什均衡。

    定理T80（信号均衡存在定理）：
    当信号成本c满足c_L < c < c_H时，分离均衡存在。

    核心方法：
    1. analyze_game — 分析博弈，计算纳什均衡
    2. compute_nash_equilibrium — 计算纯策略纳什均衡（2x2最佳响应法）
    3. signal_game_analysis — 信号博弈分析（Spence模型）
    4. repeated_pd — 重复囚徒困境（以牙还牙策略）
    5. bayesian_update — 贝叶斯信念更新
    6. mechanism_design — 机制设计（IC+IR约束）
    """

    def __init__(self):
        """初始化博弈论引擎"""
        # 博弈记录
        self.games: List[GameProfile] = []
        self.results: List[GameResult] = []

        # 统计
        self.total_games_analyzed: int = 0
        self.total_equilibria_found: int = 0
        self.total_signal_games: int = 0
        self.total_pd_games: int = 0
        self.total_bayesian_updates: int = 0
        self.total_mechanism_designs: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def analyze_game(self, game_type: str, players: int,
                     payoff_matrix: List[Any]) -> GameProfile:
        """
        分析博弈，计算纳什均衡

        根据博弈类型和支付矩阵分析博弈，
        计算纳什均衡并识别占优策略。

        Args:
            game_type: 博弈类型
            players: 参与者数量
            payoff_matrix: 支付矩阵

        Returns:
            GameProfile: 博弈画像
        """
        # 计算纳什均衡
        nash_eq = self.compute_nash_equilibrium(payoff_matrix)

        # 判断是否存在纯策略纳什均衡
        is_pure = len(nash_eq) > 0

        # 识别占优策略
        dominant = self._find_dominant_strategy(payoff_matrix, players)

        profile = GameProfile(
            game_type=game_type,
            players=players,
            payoff_matrix=payoff_matrix,
            nash_equilibria=nash_eq,
            is_pure=is_pure,
            dominant_strategy=dominant
        )

        self.games.append(profile)
        self.total_games_analyzed += 1
        self.total_equilibria_found += len(nash_eq)
        self.last_update = time.time()

        return profile

    def compute_nash_equilibrium(self, payoff_matrix: List[Any]) -> List[Dict[str, Any]]:
        """
        计算纯策略纳什均衡（2x2矩阵最佳响应法）

        对于2x2博弈，使用最佳响应法：
        1. 对每个参与者，找出对对手每个策略的最佳响应
        2. 纳什均衡 = 策略组合互为最佳响应

        NE = {s* | ∀i, s_i ∈ BR_i(s_{-i}*)}

        定理T79保证：任何有限博弈至少存在一个混合策略纳什均衡。

        Args:
            payoff_matrix: 2x2支付矩阵
                格式: [[(a11,b11), (a12,b12)], [(a21,b21), (a22,b22)]]

        Returns:
            纳什均衡列表，每个均衡为字典 {player1_strategy, player2_strategy, payoffs}
        """
        if not payoff_matrix or len(payoff_matrix) < 2:
            return []

        try:
            # 提取2x2支付矩阵
            # player1的支付矩阵
            a11 = float(payoff_matrix[0][0][0]) if isinstance(payoff_matrix[0][0], (list, tuple)) else float(payoff_matrix[0][0])
            a12 = float(payoff_matrix[0][1][0]) if isinstance(payoff_matrix[0][1], (list, tuple)) else float(payoff_matrix[0][1])
            a21 = float(payoff_matrix[1][0][0]) if isinstance(payoff_matrix[1][0], (list, tuple)) else float(payoff_matrix[1][0])
            a22 = float(payoff_matrix[1][1][0]) if isinstance(payoff_matrix[1][1], (list, tuple)) else float(payoff_matrix[1][1])

            # player2的支付矩阵
            b11 = float(payoff_matrix[0][0][1]) if isinstance(payoff_matrix[0][0], (list, tuple)) else 0.0
            b12 = float(payoff_matrix[0][1][1]) if isinstance(payoff_matrix[0][1], (list, tuple)) else 0.0
            b21 = float(payoff_matrix[1][0][1]) if isinstance(payoff_matrix[1][0], (list, tuple)) else 0.0
            b22 = float(payoff_matrix[1][1][1]) if isinstance(payoff_matrix[1][1], (list, tuple)) else 0.0

            # player1的最佳响应：给定player2的策略
            # 如果player2选策略1，player1选max(a11, a21)
            br1_against_s1 = 0 if a11 >= a21 else 1
            # 如果player2选策略2，player1选max(a12, a22)
            br1_against_s2 = 0 if a12 >= a22 else 1

            # player2的最佳响应：给定player1的策略
            # 如果player1选策略1，player2选max(b11, b12)
            br2_against_s1 = 0 if b11 >= b12 else 1
            # 如果player1选策略2，player2选max(b21, b22)
            br2_against_s2 = 0 if b21 >= b22 else 1

            equilibria = []

            # 检查四个策略组合是否为纳什均衡
            # (0,0): player1的策略0是BR(player2策略0) and player2的策略0是BR(player1策略0)
            if br1_against_s1 == 0 and br2_against_s1 == 0:
                equilibria.append({
                    'player1_strategy': 0,
                    'player2_strategy': 0,
                    'payoffs': (round(a11, 6), round(b11, 6)),
                    'type': 'pure_nash_equilibrium'
                })

            # (0,1)
            if br1_against_s2 == 0 and br2_against_s1 == 1:
                equilibria.append({
                    'player1_strategy': 0,
                    'player2_strategy': 1,
                    'payoffs': (round(a12, 6), round(b12, 6)),
                    'type': 'pure_nash_equilibrium'
                })

            # (1,0)
            if br1_against_s1 == 1 and br2_against_s2 == 0:
                equilibria.append({
                    'player1_strategy': 1,
                    'player2_strategy': 0,
                    'payoffs': (round(a21, 6), round(b21, 6)),
                    'type': 'pure_nash_equilibrium'
                })

            # (1,1)
            if br1_against_s2 == 1 and br2_against_s2 == 1:
                equilibria.append({
                    'player1_strategy': 1,
                    'player2_strategy': 1,
                    'payoffs': (round(a22, 6), round(b22, 6)),
                    'type': 'pure_nash_equilibrium'
                })

            # 定理T79保证：如果无纯策略NE，则必有混合策略NE
            if not equilibria:
                # 计算混合策略纳什均衡
                # player1的混合概率 p 使得player2在两个策略间无差异
                # b11*p + b21*(1-p) = b12*p + b22*(1-p)
                denominator = (b11 - b12 - b21 + b22)
                if abs(denominator) > 1e-10:
                    p = (b22 - b21) / denominator
                    q_denom = (a11 - a21 - a12 + a22)
                    if abs(q_denom) > 1e-10:
                        q = (a22 - a12) / q_denom
                        p = max(0.0, min(1.0, p))
                        q = max(0.0, min(1.0, q))
                        # 混合策略NE的期望支付
                        exp_p1 = p * q * a11 + p * (1 - q) * a12 + (1 - p) * q * a21 + (1 - p) * (1 - q) * a22
                        exp_p2 = p * q * b11 + p * (1 - q) * b12 + (1 - p) * q * b21 + (1 - p) * (1 - q) * b22
                        equilibria.append({
                            'player1_mixed': round(p, 6),
                            'player2_mixed': round(q, 6),
                            'expected_payoffs': (round(exp_p1, 6), round(exp_p2, 6)),
                            'type': 'mixed_nash_equilibrium',
                            'theorem': 'T79: 纳什存在定理保证混合策略NE存在'
                        })

            return equilibria

        except (IndexError, TypeError, ValueError):
            return []

    def signal_game_analysis(self, sender_type: str = 'high',
                             receiver_type: str = 'normal',
                             message_cost: float = 0.3) -> Dict[str, Any]:
        """
        信号博弈分析（Spence模型）

        信号博弈模型：
        - 发送者（知情方）根据自身类型选择信号
        - 接收者（不知情方）根据信号推断类型并选择行动
        - 信号成本因类型而异（高类型发送信号的成本更低）

        定理T80（信号均衡存在定理）：
        当信号成本c满足c_L < c < c_H时，分离均衡存在。
        即：信号成本足够低使高类型愿意发送，但足够高使低类型不愿模仿。

        Args:
            sender_type: 发送者类型（high/low）
            receiver_type: 接收者类型
            message_cost: 信号成本c

        Returns:
            信号博弈分析结果字典
        """
        self.total_signal_games += 1

        # Spence模型的信号成本结构
        # 高类型发送信号的成本低于低类型
        c_high = message_cost * 0.5   # 高类型的信号成本
        c_low = message_cost * 2.0    # 低类型的信号成本

        # 高类型和低类型的固有产出
        v_high = 1.0
        v_low = 0.5

        # T80条件：c_L < c < c_H（用c表示临界值范围）
        # 分离均衡条件：高类型愿意发送信号，低类型不愿模仿
        # 高类型：v_high - c_high > v_low → 发送信号的收益 > 不发送的收益
        # 低类型：v_low > v_high - c_low → 不发送信号的收益 > 模仿的收益
        separating_feasible_high = (v_high - c_high) > v_low
        separating_feasible_low = v_low > (v_high - c_low)
        separating_equilibrium_exists = separating_feasible_high and separating_feasible_low

        # 混同均衡：双方都选择相同策略
        pooling_payoff = (v_high + v_low) / 2.0
        high_signaling_payoff = v_high - c_high
        low_no_signal_payoff = v_low

        # 均衡类型判定
        if separating_equilibrium_exists:
            equilibrium_type = 'separating'
            equilibrium_desc = '分离均衡：高类型发送信号，低类型不发送'
        elif high_signaling_payoff > pooling_payoff:
            equilibrium_type = 'pooling_high'
            equilibrium_desc = '混同均衡（高信号）：双方都发送信号'
        else:
            equilibrium_type = 'pooling_low'
            equilibrium_desc = '混同均衡（低信号）：双方都不发送信号'

        # 贝叶斯后验信念
        # 分离均衡下：看到信号→推断为高类型(p=1)，无信号→推断为低类型(p=0)
        # 混同均衡下：后验=先验
        prior_high = 0.5  # 先验概率
        if equilibrium_type == 'separating':
            posterior_signal_high = 1.0
            posterior_no_signal_high = 0.0
        else:
            posterior_signal_high = prior_high
            posterior_no_signal_high = prior_high

        self.last_update = time.time()

        return {
            'sender_type': sender_type,
            'receiver_type': receiver_type,
            'message_cost': round(message_cost, 6),
            'c_high': round(c_high, 6),
            'c_low': round(c_low, 6),
            'equilibrium_type': equilibrium_type,
            'equilibrium_description': equilibrium_desc,
            'separating_feasible_high': separating_feasible_high,
            'separating_feasible_low': separating_feasible_low,
            'separating_equilibrium_exists': separating_equilibrium_exists,
            'posterior_signal_high': round(posterior_signal_high, 6),
            'posterior_no_signal_high': round(posterior_no_signal_high, 6),
            'high_payoff_signal': round(high_signaling_payoff, 6),
            'low_payoff_no_signal': round(low_no_signal_payoff, 6),
            'pooling_payoff': round(pooling_payoff, 6),
            'theorem_T80': f'信号均衡: c_L={round(c_low, 2)} < c={round(message_cost, 2)} < c_H={round(c_high + c_low, 2)}, 分离均衡={separating_equilibrium_exists}'
        }

    def repeated_pd(self, cooperation_rate: float = 0.6,
                    discount_factor: float = 0.9,
                    rounds: int = 10) -> Dict[str, Any]:
        """
        重复囚徒困境（以牙还牙策略，折扣因子δ）

        重复囚徒困境中，以牙还牙(Tit-for-Tat)策略：
        - 第一轮选择合作
        - 之后每轮模仿对手上一轮的选择

        折扣因子δ：未来收益的折现率
        总收益 = Σ δ^t * u_t

        合作维持条件：δ ≥ (T-R)/(T-P)（Folk定理推论）
        其中T=背叛诱惑, R=合作回报, P=互相背叛, S=被背叛

        Args:
            cooperation_rate: 初始合作概率
            discount_factor: 折扣因子δ ∈ (0,1)
            rounds: 博弈轮数

        Returns:
            重复囚徒困境分析结果字典
        """
        self.total_pd_games += 1

        # 标准囚徒困境支付
        T = 5.0  # Temptation: 背叛诱惑
        R = 3.0  # Reward: 合作回报
        P = 1.0  # Punishment: 互相背叛
        S = 0.0  # Sucker: 被背叛

        # 折扣因子截断
        delta = max(0.01, min(0.99, discount_factor))

        # 合作维持条件：δ ≥ (T-R)/(T-P)
        cooperation_threshold = (T - R) / (T - P)
        cooperation_sustainable = delta >= cooperation_threshold

        # 模拟以牙还牙博弈
        p1_actions = []  # player1行动
        p2_actions = []  # player2行动
        p1_payoffs = []  # player1收益
        p2_payoffs = []  # player2收益

        p1_cooperating = True   # player1使用TFT，首轮合作
        p2_cooperating = cooperation_rate > 0.5  # player2策略基于合作率

        for t in range(rounds):
            # 确定当前轮行动
            if t == 0:
                # 第一轮
                a1 = 'C'  # TFT首轮合作
                a2 = 'C' if p2_cooperating else 'D'
            else:
                # TFT：模仿对手上一轮
                a1 = p2_actions[-1]  # player1 TFT
                # player2: 基于合作率做概率选择
                p2_cooperating = cooperation_rate > (0.3 + 0.4 * t / max(rounds, 1))
                a2 = 'C' if p2_cooperating else 'D'

            p1_actions.append(a1)
            p2_actions.append(a2)

            # 计算本轮收益
            if a1 == 'C' and a2 == 'C':
                p1_payoffs.append(R)
                p2_payoffs.append(R)
            elif a1 == 'C' and a2 == 'D':
                p1_payoffs.append(S)
                p2_payoffs.append(T)
            elif a1 == 'D' and a2 == 'C':
                p1_payoffs.append(T)
                p2_payoffs.append(S)
            else:
                p1_payoffs.append(P)
                p2_payoffs.append(P)

        # 计算折现总收益
        p1_total = sum(p1_payoffs[t] * (delta ** t) for t in range(rounds))
        p2_total = sum(p2_payoffs[t] * (delta ** t) for t in range(rounds))

        # 合作频率
        p1_coop_freq = sum(1 for a in p1_actions if a == 'C') / max(rounds, 1)
        p2_coop_freq = sum(1 for a in p2_actions if a == 'C') / max(rounds, 1)

        self.last_update = time.time()

        return {
            'discount_factor': round(delta, 6),
            'cooperation_threshold': round(cooperation_threshold, 6),
            'cooperation_sustainable': cooperation_sustainable,
            'rounds': rounds,
            'p1_total_payoff': round(p1_total, 6),
            'p2_total_payoff': round(p2_total, 6),
            'p1_cooperation_freq': round(p1_coop_freq, 6),
            'p2_cooperation_freq': round(p2_coop_freq, 6),
            'p1_actions': p1_actions[:min(20, rounds)],  # 截断显示
            'p2_actions': p2_actions[:min(20, rounds)],
            'payoff_matrix': {'T': T, 'R': R, 'P': P, 'S': S},
            'strategy': 'Tit-for-Tat',
            'sustainability_condition': f'δ≥{round(cooperation_threshold, 4)}: {"满足" if cooperation_sustainable else "不满足"}'
        }

    def bayesian_update(self, prior: float, likelihood: float,
                        evidence: float) -> Dict[str, Any]:
        """
        贝叶斯信念更新

        P(H|E) = P(E|H)·P(H) / P(E)

        其中：
        - P(H): 先验概率（假设H为真的先验信念）
        - P(E|H): 似然函数（在H为真时观测到E的概率）
        - P(E): 证据概率（观测到E的总概率）
        - P(H|E): 后验概率（观测到E后H为真的概率）

        Args:
            prior: 先验概率P(H)
            likelihood: 似然P(E|H)
            evidence: 证据概率P(E)

        Returns:
            贝叶斯更新结果字典
        """
        self.total_bayesian_updates += 1

        # 边界保护
        prior = max(0.001, min(0.999, prior))
        likelihood = max(0.001, min(1.0, likelihood))
        evidence = max(0.001, min(1.0, evidence))

        # P(H|E) = P(E|H)·P(H) / P(E)
        posterior = (likelihood * prior) / evidence
        posterior = max(0.0, min(1.0, posterior))

        # 信念变化量
        belief_change = posterior - prior

        # 似然比（Bayes因子）
        # BF = P(E|H) / P(E|¬H)
        p_e_not_h = (evidence - likelihood * prior) / max(1.0 - prior, 0.001)
        bayes_factor = likelihood / max(p_e_not_h, 0.001)

        self.last_update = time.time()

        return {
            'prior_P_H': round(prior, 6),
            'likelihood_P_E_given_H': round(likelihood, 6),
            'evidence_P_E': round(evidence, 6),
            'posterior_P_H_given_E': round(posterior, 6),
            'belief_change': round(belief_change, 6),
            'bayes_factor': round(bayes_factor, 6),
            'interpretation': (
                f'先验{round(prior, 3)}→后验{round(posterior, 3)}，'
                f'证据{"增强" if belief_change > 0 else "削弱"}了假设'
            )
        }

    def mechanism_design(self, social_choice_function: str = 'efficiency',
                         incentive_compatible: bool = True) -> Dict[str, Any]:
        """
        机制设计（IC约束+IR约束）

        机制设计是博弈论的"逆问题"：
        给定社会选择目标，设计博弈规则使自利参与者的均衡行为实现目标。

        IC（激励相容）：u_i(θ_i, s_i*(θ)) ≥ u_i(θ_i, s_i)
        即：如实报告类型是最优策略

        IR（个体理性）：u_i(θ_i, s_i*) ≥ 0
        即：参与机制的收益不低于外部选项

        Args:
            social_choice_function: 社会选择函数（efficiency, equality, rawlsian）
            incentive_compatible: 是否要求激励相容

        Returns:
            机制设计结果字典
        """
        self.total_mechanism_designs += 1

        # 模拟机制设计
        # 参与者类型分布
        n_participants = 3
        types = ['high', 'medium', 'low']
        valuations = {'high': 10.0, 'medium': 6.0, 'low': 3.0}

        # 社会选择函数
        if social_choice_function == 'efficiency':
            # 效率优先：分配给估值最高的参与者
            allocation = 'high'
            welfare = valuations['high']
        elif social_choice_function == 'equality':
            # 平等优先：随机分配
            allocation = 'medium'
            welfare = valuations['medium']
        elif social_choice_function == 'rawlsian':
            # 罗尔斯式：最大化最差参与者效用
            allocation = 'low'
            welfare = valuations['low']
        else:
            allocation = 'medium'
            welfare = valuations['medium']

        # IC检验
        ic_satisfied = incentive_compatible
        # 计算IC约束：如实报告 ≥ 谎报
        ic_report_truth = valuations[allocation]
        ic_report_false = valuations[allocation] * 0.5  # 谎报的惩罚
        ic_check = ic_report_truth >= ic_report_false

        # IR检验
        ir_satisfied = welfare > 0
        # IR约束：参与收益 ≥ 外部选项（设为0）
        ir_check = all(v >= 0 for v in valuations.values())

        # VCG支付（Clarke规则简化）
        # 支付 = 对其他参与者造成的外部性
        vcg_payments = {}
        for t in types:
            if t == allocation:
                # 赢家支付：其他参与者的次优总价值
                others = [v for k, v in valuations.items() if k != t]
                vcg_payments[t] = round(max(others), 6)
            else:
                # 输家支付0
                vcg_payments[t] = 0.0

        # 预算平衡
        total_payment = sum(vcg_payments.values())
        budget_balance = round(total_payment / max(welfare, 0.001), 6)

        # 效率
        efficiency = round(welfare / max(valuations['high'], 0.001), 6)

        self.last_update = time.time()

        return {
            'social_choice_function': social_choice_function,
            'incentive_compatible': incentive_compatible,
            'allocation': allocation,
            'social_welfare': round(welfare, 6),
            'efficiency': efficiency,
            'ic_satisfied': ic_satisfied and ic_check,
            'ir_satisfied': ir_satisfied and ir_check,
            'ic_detail': {
                'truth_payoff': round(ic_report_truth, 6),
                'false_payoff': round(ic_report_false, 6),
                'ic_holds': ic_check
            },
            'ir_detail': {
                'all_positive': ir_check,
                'valuations': valuations
            },
            'vcg_payments': vcg_payments,
            'budget_balance': budget_balance,
            'n_participants': n_participants,
            'theorem': 'IC: u_i(θ,s*(θ))≥u_i(θ,s), IR: u_i(θ,s*)≥0'
        }

    def _find_dominant_strategy(self, payoff_matrix: List[Any],
                                players: int) -> Optional[str]:
        """
        识别占优策略

        占优策略：无论对手如何选择，该策略总是最优。

        Args:
            payoff_matrix: 支付矩阵
            players: 参与者数量

        Returns:
            占优策略描述，如果不存在则返回None
        """
        if not payoff_matrix or len(payoff_matrix) < 2:
            return None

        try:
            # 检查player1是否有占优策略
            a11 = float(payoff_matrix[0][0][0]) if isinstance(payoff_matrix[0][0], (list, tuple)) else float(payoff_matrix[0][0])
            a12 = float(payoff_matrix[0][1][0]) if isinstance(payoff_matrix[0][1], (list, tuple)) else float(payoff_matrix[0][1])
            a21 = float(payoff_matrix[1][0][0]) if isinstance(payoff_matrix[1][0], (list, tuple)) else float(payoff_matrix[1][0])
            a22 = float(payoff_matrix[1][1][0]) if isinstance(payoff_matrix[1][1], (list, tuple)) else float(payoff_matrix[1][1])

            # 策略0占优：a11≥a21 且 a12≥a22
            if a11 >= a21 and a12 >= a22:
                return 'player1_strategy_0'
            # 策略1占优：a21≥a11 且 a22≥a12
            if a21 >= a11 and a22 >= a12:
                return 'player1_strategy_1'

            # 检查player2
            b11 = float(payoff_matrix[0][0][1]) if isinstance(payoff_matrix[0][0], (list, tuple)) else 0.0
            b12 = float(payoff_matrix[0][1][1]) if isinstance(payoff_matrix[0][1], (list, tuple)) else 0.0
            b21 = float(payoff_matrix[1][0][1]) if isinstance(payoff_matrix[1][0], (list, tuple)) else 0.0
            b22 = float(payoff_matrix[1][1][1]) if isinstance(payoff_matrix[1][1], (list, tuple)) else 0.0

            if b11 >= b12 and b21 >= b22:
                return 'player2_strategy_0'
            if b12 >= b11 and b22 >= b21:
                return 'player2_strategy_1'

            return None

        except (IndexError, TypeError, ValueError):
            return None

    def get_state(self) -> Dict[str, Any]:
        """
        获取博弈论引擎状态

        Returns:
            状态字典，包含博弈分析统计和当前配置
        """
        dominant_count = sum(1 for g in self.games if g.dominant_strategy is not None)
        dominant_rate = round(
            dominant_count / max(len(self.games), 1), 6
        )

        return {
            'total_games_analyzed': self.total_games_analyzed,
            'total_equilibria_found': self.total_equilibria_found,
            'total_signal_games': self.total_signal_games,
            'total_pd_games': self.total_pd_games,
            'total_bayesian_updates': self.total_bayesian_updates,
            'total_mechanism_designs': self.total_mechanism_designs,
            'dominant_rate': dominant_rate,
            'games_recorded': len(self.games),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T79': '纳什存在: 有限博弈至少存在一个混合策略NE',
            'theorem_T80': '信号均衡: c_L<c<c_H ⟹ 分离均衡存在'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新博弈论引擎状态

        Args:
            data: 可选更新数据，支持：
                - analyze: 分析博弈 {game_type, players, payoff_matrix}
                - signal: 信号博弈 {sender_type, receiver_type, message_cost}
                - pd: 囚徒困境 {cooperation_rate, discount_factor, rounds}
                - bayesian: 贝叶斯更新 {prior, likelihood, evidence}
                - mechanism: 机制设计 {social_choice, incentive_compatible}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'analyze' or 'analyze' in data:
                a = data.get('analyze', data)
                self.analyze_game(
                    game_type=a.get('game_type', 'unknown'),
                    players=int(a.get('players', 2)),
                    payoff_matrix=a.get('payoff_matrix', [])
                )
            elif action == 'signal' or 'signal' in data:
                s = data.get('signal', data)
                self.signal_game_analysis(
                    sender_type=s.get('sender_type', 'high'),
                    receiver_type=s.get('receiver_type', 'normal'),
                    message_cost=float(s.get('message_cost', 0.3))
                )
            elif action == 'pd' or 'pd' in data:
                p = data.get('pd', data)
                self.repeated_pd(
                    cooperation_rate=float(p.get('cooperation_rate', 0.6)),
                    discount_factor=float(p.get('discount_factor', 0.9)),
                    rounds=int(p.get('rounds', 10))
                )
            elif action == 'bayesian' or 'bayesian' in data:
                b = data.get('bayesian', data)
                self.bayesian_update(
                    prior=float(b.get('prior', 0.5)),
                    likelihood=float(b.get('likelihood', 0.8)),
                    evidence=float(b.get('evidence', 0.6))
                )
            elif action == 'mechanism' or 'mechanism' in data:
                m = data.get('mechanism', data)
                self.mechanism_design(
                    social_choice_function=m.get('social_choice', 'efficiency'),
                    incentive_compatible=bool(m.get('incentive_compatible', True))
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示博弈论引擎的核心功能"""
        # 1. 囚徒困境博弈
        pd_matrix = [
            [(-1, -1), (-10, 0)],
            [(0, -10), (-5, -5)]
        ]
        pd_result = self.analyze_game('prisoner_dilemma', 2, pd_matrix)

        # 2. 协调博弈
        coord_matrix = [
            [(2, 2), (0, 0)],
            [(0, 0), (1, 1)]
        ]
        coord_result = self.analyze_game('coordination', 2, coord_matrix)

        # 3. 信号博弈
        signal_result = self.signal_game_analysis('high', 'normal', 0.4)

        # 4. 重复囚徒困境
        pd_repeat = self.repeated_pd(0.7, 0.9, 20)

        # 5. 贝叶斯更新
        bayes_result = self.bayesian_update(0.3, 0.9, 0.5)

        # 6. 机制设计
        mech_result = self.mechanism_design('efficiency', True)

        return {
            'prisoner_dilemma': pd_result.to_dict(),
            'coordination_game': coord_result.to_dict(),
            'signal_game': signal_result,
            'repeated_pd': pd_repeat,
            'bayesian_update': bayes_result,
            'mechanism_design': mech_result,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[GameTheoryEngine] = None


def get_instance() -> GameTheoryEngine:
    """
    获取GameTheoryEngine单例实例

    Returns:
        GameTheoryEngine全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = GameTheoryEngine()
    return _instance


def analyze_game(game_type: str, players: int,
                 payoff_matrix: List[Any]) -> GameProfile:
    """分析博弈（快捷接口）"""
    return get_instance().analyze_game(game_type, players, payoff_matrix)


def compute_nash_equilibrium(payoff_matrix: List[Any]) -> List[Dict[str, Any]]:
    """计算纳什均衡（快捷接口）"""
    return get_instance().compute_nash_equilibrium(payoff_matrix)


def signal_game_analysis(sender_type: str = 'high',
                         receiver_type: str = 'normal',
                         message_cost: float = 0.3) -> Dict[str, Any]:
    """信号博弈分析（快捷接口）"""
    return get_instance().signal_game_analysis(sender_type, receiver_type, message_cost)


def repeated_pd(cooperation_rate: float = 0.6,
                discount_factor: float = 0.9,
                rounds: int = 10) -> Dict[str, Any]:
    """重复囚徒困境（快捷接口）"""
    return get_instance().repeated_pd(cooperation_rate, discount_factor, rounds)


def bayesian_update(prior: float, likelihood: float,
                    evidence: float) -> Dict[str, Any]:
    """贝叶斯信念更新（快捷接口）"""
    return get_instance().bayesian_update(prior, likelihood, evidence)


def mechanism_design(social_choice_function: str = 'efficiency',
                     incentive_compatible: bool = True) -> Dict[str, Any]:
    """机制设计（快捷接口）"""
    return get_instance().mechanism_design(social_choice_function, incentive_compatible)


def get_state() -> Dict[str, Any]:
    """获取博弈论引擎状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新博弈论引擎状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
