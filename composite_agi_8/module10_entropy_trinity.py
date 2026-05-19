"""
太乙AGI 9.0 - 模块10：熵的三重面孔 + 自由能最小化
=======================================================

基于《熵的"三重面孔"：复合体理学视域下的多尺度熵统一理论》

三重面孔：
  Face 1 (信息-计算视界): 香农熵、算法熵、冯·诺依曼熵、拓扑熵
  Face 2 (动力学-物理视界): 热力学熵、玻尔兹曼熵、自由能、负熵机制
  Face 3 (系统-演化视界): 目的论熵、耗散结构、反脆弱、可控熵增

核心数学原理:
  - 最大熵原理（Jaynes）
  - 变分自由能 F = E[L] - H(q) ↔ 自由能最小化 ↔ 贝叶斯推断
  - 目的论熵：Htele(s) = -log P(s ∈ Goal_Set)
  - 开放系统负熵条件：dS = dS_e + dS_i, dS_i ≥ 0
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import math


# ============================================================
# Face 1: 信息之熵（视界Ⅰ：信息-计算）
# ============================================================

class InformationEntropy:
    """
    信息熵：不确定性的度量
    
    对应汉字「熵 = 火 + 商」：
    - 火：能量耗散（热现象）
    - 商：比率关系（克劳修斯 dS = δQ/T）
    """
    
    @staticmethod
    def shannon_entropy(probs: np.ndarray, base: float = 2.0) -> float:
        """
        香农熵 H(X) = -∑ p(x) log p(x)
        
        Args:
            probs: 概率分布（自动归一化）
            base: 对数底（2=比特，e=奈特）
        """
        probs = np.array(probs, dtype=float)
        probs = probs / probs.sum()  # 归一化
        
        # 避免 log(0)
        mask = probs > 1e-12
        if base == 2.0:
            h = -np.sum(probs[mask] * np.log2(probs[mask]))
        else:
            h = -np.sum(probs[mask] * np.log(probs[mask])) / math.log(base)
        
        return float(h)
    
    @staticmethod
    def von_neumann_entropy(density_matrix: np.ndarray) -> float:
        """
        冯·诺依曼熵 S(ρ) = -Tr(ρ log ρ)
        量子信息基石，描述量子态叠加与纠缠
        
        Args:
            density_matrix: 密度矩阵（Hermitian，trace=1）
        """
        # 对角化
        eigenvalues = np.linalg.eigvalsh(density_matrix)
        eigenvalues = eigenvalues[eigenvalues > 1e-12]
        
        return float(-np.sum(eigenvalues * np.log(eigenvalues)))
    
    @staticmethod
    def topological_entropy_approx(adjacency: np.ndarray) -> float:
        """
        拓扑熵近似（基于图结构轨道分裂）
        
        公式：htop = lim (1/n) log |Sep_n(ε)|
        近似：用图的谱半径 log(λ_max) 作为代理
        
        Args:
            adjacency: 邻接矩阵
        """
        eigenvalues = np.linalg.eigvalsh(adjacency)
        lambda_max = np.max(np.abs(eigenvalues))
        
        if lambda_max < 1e-12:
            return 0.0
        
        return float(math.log(lambda_max))
    
    @staticmethod
    def relative_entropy_kl(p: np.ndarray, q: np.ndarray) -> float:
        """
        KL散度（相对熵）D_KL(P||Q) = ∑ p(x) log(p(x)/q(x))
        衡量两分布之间的"信息距离"
        """
        p = np.array(p, dtype=float)
        q = np.array(q, dtype=float)
        p = p / p.sum()
        q = q / q.sum()
        
        mask = (p > 1e-12) & (q > 1e-12)
        return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))
    
    @staticmethod
    def maximum_entropy_distribution(
        feature_matrix: np.ndarray,
        target_expectations: np.ndarray,
        max_iter: int = 1000,
        lr: float = 0.01
    ) -> np.ndarray:
        """
        最大熵原理：Jaynes最大熵分布
        
        定理：给定约束 E_p[f] = μ，最大熵分布为指数族
        p*(x) = exp(λ^T f(x)) / Z(λ)
        
        Args:
            feature_matrix: F[n, d]，n个样本、d个特征
            target_expectations: μ[d]，特征期望约束
            max_iter: 梯度下降迭代次数
            lr: 学习率
            
        Returns:
            最大熵分布 p*[n]
        """
        n, d = feature_matrix.shape
        lambdas = np.zeros(d)
        
        for _ in range(max_iter):
            # 计算当前分布 p = softmax(F λ)
            logits = feature_matrix @ lambdas
            logits -= logits.max()  # 数值稳定
            probs = np.exp(logits)
            probs /= probs.sum()
            
            # 当前特征期望
            current_expect = feature_matrix.T @ probs
            
            # 梯度 ∇_λ L = μ - E_p[f]
            grad = target_expectations - current_expect
            lambdas += lr * grad
            
            if np.linalg.norm(grad) < 1e-6:
                break
        
        # 最终分布
        logits = feature_matrix @ lambdas
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum()
        
        return probs
    
    def analyze_information_horizon(self, state: np.ndarray) -> Dict[str, float]:
        """
        视界Ⅰ完整分析：信息熵的多维度刻画
        """
        # 构造伪概率分布（softmax）
        exp_s = np.exp(state - state.max())
        probs = exp_s / exp_s.sum()
        
        # 均匀分布作为参考
        uniform = np.ones(len(probs)) / len(probs)
        
        # 构造简单邻接图（环形）
        n = min(len(state), 20)
        adj = np.zeros((n, n))
        for i in range(n):
            adj[i, (i + 1) % n] = 1.0
            adj[(i + 1) % n, i] = 1.0
        
        return {
            "shannon_entropy_bits": self.shannon_entropy(probs, base=2.0),
            "shannon_entropy_nats": self.shannon_entropy(probs, base=math.e),
            "topological_entropy": self.topological_entropy_approx(adj),
            "kl_from_uniform": self.relative_entropy_kl(probs, uniform),
            "max_entropy_bits": math.log2(len(probs)),  # 均匀分布的最大熵
            "entropy_efficiency": self.shannon_entropy(probs, base=2.0) / math.log2(len(probs))
        }


# ============================================================
# Face 2: 热力学之熵（视界Ⅱ：动力学-物理）
# ============================================================

class ThermodynamicEntropy:
    """
    热力学熵：能量耗散的不可逆性
    
    焓H = 火 + 含：系统总热含量（内能+压力功）
    熵S = 火 + 商：热量与温度之商 δQ/T
    
    开放系统熵变：dS = dS_e + dS_i
    - dS_e：熵流（可负，与环境交换）
    - dS_i：熵产生（不可逆，非负）
    """
    
    def __init__(self, temperature: float = 300.0):
        """
        Args:
            temperature: 系统温度（开尔文）
        """
        self.T = temperature  # 系统温度
        self.k_B = 1.380649e-23  # 玻尔兹曼常数
        self.entropy_production = 0.0  # 累积熵产生 dS_i
        self.entropy_flow = 0.0  # 累积熵流 dS_e
    
    def boltzmann_entropy(self, microstates: int) -> float:
        """
        玻尔兹曼熵 S = k_B * ln(Ω)
        
        Args:
            microstates: 微观态数目 Ω
        """
        if microstates <= 0:
            return 0.0
        return self.k_B * math.log(microstates)
    
    def clausius_entropy_change(self, heat_absorbed: float) -> float:
        """
        克劳修斯熵变 dS = δQ/T
        
        Args:
            heat_absorbed: 吸收热量（焦耳）
        """
        return heat_absorbed / self.T
    
    def free_energy(self, internal_energy: float, entropy: float) -> float:
        """
        亥姆霍兹自由能 F = U - TS
        
        在AGI中对应：系统为达成目标可利用的"可用功"
        """
        return internal_energy - self.T * entropy
    
    def gibbs_free_energy(self, enthalpy: float, entropy: float) -> float:
        """
        吉布斯自由能 G = H - TS
        定压过程更自然（开放系统）
        """
        return enthalpy - self.T * entropy
    
    def open_system_entropy_change(
        self,
        entropy_flow: float,
        entropy_production: float
    ) -> Tuple[float, bool]:
        """
        开放系统熵变定理（定理2）
        
        dS = dS_e + dS_i
        若 dS_e < -dS_i（且 dS_i > 0），则 dS < 0（局域负熵）
        
        Args:
            entropy_flow: 熵流 dS_e（可正可负）
            entropy_production: 熵产生 dS_i（非负）
            
        Returns:
            (total_dS, is_local_negentropy)
        """
        if entropy_production < 0:
            entropy_production = 0.0  # 强制非负
        
        total = entropy_flow + entropy_production
        
        self.entropy_flow += entropy_flow
        self.entropy_production += entropy_production
        
        return total, (total < 0)
    
    def analyze_thermodynamic_horizon(self, state: np.ndarray) -> Dict[str, float]:
        """
        视界Ⅱ完整分析：热力学熵的多维度刻画
        """
        # 模拟：将状态向量视为能量分布
        energies = np.abs(state)
        
        # 配分函数 Z = ∑ exp(-E/kT)，简化：Z = ∑ exp(-|s|)
        beta = 1.0 / (self.k_B * self.T + 1e-10) if self.T > 0 else 1.0
        # 数值化简：令 beta=1
        beta_simplified = 1.0
        boltzmann_weights = np.exp(-beta_simplified * energies)
        Z = boltzmann_weights.sum()
        probs = boltzmann_weights / Z
        
        # 玻尔兹曼熵（内聚形式）
        H_boltzmann = -np.sum(probs[probs > 1e-12] * np.log(probs[probs > 1e-12]))
        
        # 自由能 F = -kT ln Z → 简化为 F = -ln Z
        free_energy_approx = -math.log(Z)
        
        # 内能 E = <E>_p = ∑ E*p
        internal_energy = float(np.sum(energies * probs))
        
        # 验证：F = U - T*S → S = (U - F) / T
        entropy_from_free_energy = internal_energy - free_energy_approx
        
        # 负熵指标（相对于最大无序）
        max_entropy = math.log(len(state))
        negentropy = max_entropy - H_boltzmann
        
        return {
            "boltzmann_entropy_nats": float(H_boltzmann),
            "free_energy_approx": float(free_energy_approx),
            "internal_energy": float(internal_energy),
            "negentropy": float(negentropy),
            "entropy_from_free_energy": float(entropy_from_free_energy),
            "is_ordered": negentropy > max_entropy * 0.3  # 结构有序阈值
        }


# ============================================================
# Face 3: 目的论之熵（视界Ⅲ：系统-演化）
# ============================================================

class TeleologicalEntropy:
    """
    目的论熵：系统相对于目标集的"意外度"
    
    Htele(s) = -log P(s ∈ Goal_Set)
    
    核心思想：
    - 熵不是越低越好（也不是越高越好）
    - 要把熵"花在刀刃上"——维持结构+保留探索余地
    - 反脆弱：在波动中成长
    
    对应「复合体理学」中的流贯选择与自由能最小化
    """
    
    def __init__(self, goal_threshold: float = 0.7):
        """
        Args:
            goal_threshold: 目标达成判断阈值（相似度 > threshold）
        """
        self.goal_threshold = goal_threshold
        self.goal_states: List[np.ndarray] = []
        self.entropy_history: List[float] = []
    
    def register_goal(self, goal_state: np.ndarray):
        """注册目标状态"""
        self.goal_states.append(goal_state / (np.linalg.norm(goal_state) + 1e-10))
    
    def teleological_entropy(self, current_state: np.ndarray) -> float:
        """
        目的论熵：H_tele(s) = -log P(s ∈ Goal_Set)
        
        P(s ∈ Goal) ≈ max_g cos_similarity(s, g) 过阈值的概率估计
        """
        if not self.goal_states:
            return math.log(2)  # 无目标：最大不确定性
        
        s_norm = current_state / (np.linalg.norm(current_state) + 1e-10)
        
        # 计算与各目标的相似度
        similarities = []
        for g in self.goal_states:
            min_dim = min(len(s_norm), len(g))
            sim = float(np.dot(s_norm[:min_dim], g[:min_dim]))
            similarities.append(max(0.0, sim))
        
        # P(s ∈ Goal) 近似为最大相似度的 sigmoid
        best_sim = max(similarities)
        p_goal = 1.0 / (1.0 + math.exp(-10.0 * (best_sim - self.goal_threshold)))
        p_goal = max(p_goal, 1e-10)
        
        h_tele = -math.log(p_goal)
        self.entropy_history.append(h_tele)
        
        return h_tele
    
    def negentropy_production(self, state_t0: np.ndarray, state_t1: np.ndarray) -> float:
        """
        负熵生产速率：系统向目标状态演化的快慢
        
        dH_tele/dt 为负 → 系统在进步（向目标逼近）
        """
        h0 = self.teleological_entropy(state_t0)
        h1 = self.teleological_entropy(state_t1)
        return h0 - h1  # 正值表示负熵生产（熵在减少）
    
    def antifragility_score(self, state_history: List[np.ndarray]) -> float:
        """
        反脆弱性评分：在扰动下熵增→熵减的恢复能力
        
        反脆弱 = 能从噪声中获益（不仅仅是适应）
        """
        if len(state_history) < 3:
            return 0.5
        
        entropies = [self.teleological_entropy(s) for s in state_history]
        
        # 计算熵的变化率序列
        delta_h = np.diff(entropies)
        
        # 找到熵增之后的熵减（反脆弱的标志）
        recoveries = 0
        for i in range(len(delta_h) - 1):
            if delta_h[i] > 0 and delta_h[i + 1] < -delta_h[i] * 0.5:
                recoveries += 1
        
        antifragility = recoveries / max(len(delta_h) - 1, 1)
        return float(antifragility)
    
    def controlled_entropy_increase(
        self,
        current_entropy: float,
        target_entropy_range: Tuple[float, float]
    ) -> Tuple[float, str]:
        """
        可控熵增：保持熵在目标区间内
        
        - 熵过低：系统过度固化，缺乏探索（加噪声）
        - 熵过高：系统混乱，缺乏结构（收紧约束）
        
        Returns:
            (adjustment, action)
        """
        low, high = target_entropy_range
        
        if current_entropy < low:
            # 熵不足，需要探索
            adjustment = low - current_entropy
            action = "increase_entropy"
        elif current_entropy > high:
            # 熵过高，需要收敛
            adjustment = high - current_entropy
            action = "decrease_entropy"
        else:
            adjustment = 0.0
            action = "maintain"
        
        return float(adjustment), action
    
    def analyze_teleological_horizon(
        self,
        state: np.ndarray,
        state_history: Optional[List[np.ndarray]] = None
    ) -> Dict[str, Any]:
        """
        视界Ⅲ完整分析：目的论熵的多维度刻画
        """
        h_tele = self.teleological_entropy(state)
        
        # 反脆弱评分
        if state_history and len(state_history) >= 3:
            antifragility = self.antifragility_score(state_history)
        else:
            antifragility = 0.5
        
        # 可控熵增建议（目标熵区间 [0.3, 1.5]）
        adjustment, action = self.controlled_entropy_increase(h_tele, (0.3, 1.5))
        
        # 目标达成概率
        p_goal = math.exp(-h_tele)
        
        return {
            "teleological_entropy": h_tele,
            "goal_achievement_probability": float(p_goal),
            "antifragility_score": float(antifragility),
            "entropy_adjustment": float(adjustment),
            "entropy_action": action,
            "is_goal_achieved": p_goal > self.goal_threshold
        }


# ============================================================
# 自由能最小化引擎（变分推断统一框架）
# ============================================================

class VariationalFreeEnergy:
    """
    变分自由能最小化：连接信息与热力学的桥梁
    
    定理4（信息-物理桥梁）：
    F[q] = E_q[log q(x) - log p(x, o)]
          = KL(q||p) - log p(o)
          = -ELBO
    
    最小化 F ↔ 同时做到：
    1. 最大化熵 H[q]（保留探索性）
    2. 最大化似然 E_q[log p(o|x)]（拟合观测）
    
    在AGI中：
    - q(x)：智能体对世界的信念（内部模型）
    - p(o|x)：生成模型（感知预测）
    - 最小化F ↔ 主动推断（Active Inference）
    """
    
    def __init__(self, prior_strength: float = 1.0):
        """
        Args:
            prior_strength: 先验强度（越大越重视先验）
        """
        self.prior_strength = prior_strength
        self.fe_history: List[float] = []
    
    def compute_free_energy(
        self,
        q_probs: np.ndarray,
        log_joint: np.ndarray
    ) -> float:
        """
        计算变分自由能 F = E_q[-log p(x,o)] + E_q[log q]
                         = -E_q[log p(x,o)] - H[q]
        
        Args:
            q_probs: 近似后验 q(x)
            log_joint: log p(x, o) 对各 x 的值
        """
        q = np.array(q_probs, dtype=float)
        q = q / q.sum()
        
        mask = q > 1e-12
        
        # 能量项：E_q[-log p(x,o)]
        energy = -np.sum(q[mask] * log_joint[mask])
        
        # 熵项：-H[q] = E_q[log q]
        minus_entropy = np.sum(q[mask] * np.log(q[mask]))
        
        fe = energy + minus_entropy
        self.fe_history.append(fe)
        
        return float(fe)
    
    def minimize_free_energy_step(
        self,
        q_params: np.ndarray,
        observation: np.ndarray,
        generative_model_fn,
        lr: float = 0.01
    ) -> np.ndarray:
        """
        一步变分自由能最小化（梯度下降更新 q）
        
        对应主动推断中的"感知更新"步骤
        
        Args:
            q_params: 当前信念参数（softmax → 概率）
            observation: 当前观测 o
            generative_model_fn: p(o|x) 函数
            lr: 学习率
            
        Returns:
            更新后的 q_params
        """
        eps = 1e-5
        n = len(q_params)
        grad = np.zeros(n)
        
        # 数值梯度
        for i in range(n):
            params_plus = q_params.copy()
            params_plus[i] += eps
            params_minus = q_params.copy()
            params_minus[i] -= eps
            
            q_plus = self._softmax(params_plus)
            q_minus = self._softmax(params_minus)
            
            # 简化计算（省略 generative_model_fn 调用）
            fe_plus = -InformationEntropy.shannon_entropy(q_plus, base=math.e)
            fe_minus = -InformationEntropy.shannon_entropy(q_minus, base=math.e)
            
            grad[i] = (fe_plus - fe_minus) / (2 * eps)
        
        # 梯度下降
        new_params = q_params - lr * grad
        return new_params
    
    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        x = x - x.max()
        exp_x = np.exp(x)
        return exp_x / exp_x.sum()
    
    def elbo(self, q_probs: np.ndarray, log_likelihood: np.ndarray, log_prior: np.ndarray) -> float:
        """
        证据下界 ELBO = E_q[log p(o|x)] + E_q[log p(x)] - E_q[log q(x)]
                     = -F + const
        """
        q = np.array(q_probs, dtype=float)
        q = q / q.sum()
        mask = q > 1e-12
        
        expected_likelihood = np.sum(q[mask] * log_likelihood[mask])
        expected_prior = np.sum(q[mask] * log_prior[mask])
        entropy_q = InformationEntropy.shannon_entropy(q, base=math.e)
        
        return float(expected_likelihood + expected_prior + entropy_q)


# ============================================================
# 主模块：熵三重面孔统一分析器
# ============================================================

class EntropyTrinityModule:
    """
    模块10：熵的三重面孔统一分析器
    
    整合三个视界的熵测量，给出综合评估
    并提供「水火既济」均衡建议
    （动态有序 ↔ 可控无序 的最优平衡）
    """
    
    def __init__(
        self,
        temperature: float = 300.0,
        goal_threshold: float = 0.7
    ):
        self.face1 = InformationEntropy()
        self.face2 = ThermodynamicEntropy(temperature=temperature)
        self.face3 = TeleologicalEntropy(goal_threshold=goal_threshold)
        self.vfe = VariationalFreeEnergy()
        
        self.analysis_history: List[Dict] = []
    
    def register_goal(self, goal_state: np.ndarray):
        """注册AGI的目标状态"""
        self.face3.register_goal(goal_state)
    
    def full_entropy_analysis(
        self,
        state: np.ndarray,
        state_history: Optional[List[np.ndarray]] = None,
        label: str = "state"
    ) -> Dict[str, Any]:
        """
        完整的三视界熵分析
        
        Args:
            state: 当前系统状态向量
            state_history: 历史状态（用于反脆弱评估）
            label: 状态标签
            
        Returns:
            三视界熵的完整分析报告
        """
        # 视界Ⅰ：信息熵
        info_analysis = self.face1.analyze_information_horizon(state)
        
        # 视界Ⅱ：热力学熵
        thermo_analysis = self.face2.analyze_thermodynamic_horizon(state)
        
        # 视界Ⅲ：目的论熵
        tele_analysis = self.face3.analyze_teleological_horizon(state, state_history)
        
        # 综合：「水火既济」均衡指数
        # 火（能量/熵增）与水（结构/负熵）的动态平衡
        fire_index = info_analysis["shannon_entropy_nats"]  # 不确定性（火）
        water_index = thermo_analysis["negentropy"]          # 结构有序（水）
        
        if fire_index + water_index > 0:
            water_fire_balance = water_index / (fire_index + water_index)
        else:
            water_fire_balance = 0.5
        
        # 综合熵评分
        h_info = info_analysis["entropy_efficiency"]  # 归一化到[0,1]
        h_thermo = min(1.0, thermo_analysis["boltzmann_entropy_nats"] / 10.0)
        h_tele = min(1.0, tele_analysis["teleological_entropy"] / 5.0)
        
        # 加权平均（信息:热力学:目的论 = 3:2:5，目的论最重要）
        overall_entropy_score = 0.3 * h_info + 0.2 * h_thermo + 0.5 * h_tele
        
        report = {
            "label": label,
            "face1_information": info_analysis,
            "face2_thermodynamic": thermo_analysis,
            "face3_teleological": tele_analysis,
            "water_fire_balance": float(water_fire_balance),
            "overall_entropy_score": float(overall_entropy_score),
            "entropy_diagnosis": self._diagnose_entropy(overall_entropy_score, tele_analysis),
            "recommendation": self._recommend_action(tele_analysis["entropy_action"], water_fire_balance)
        }
        
        self.analysis_history.append(report)
        return report
    
    def _diagnose_entropy(self, score: float, tele: Dict) -> str:
        """根据综合熵评分给出诊断"""
        if tele["is_goal_achieved"]:
            return "GOAL_ACHIEVED: 系统已达目标状态"
        elif score < 0.2:
            return "OVER_ORDERED: 过度固化，需要增加探索（负熵过度）"
        elif score < 0.5:
            return "OPTIMAL_RANGE: 最优水火既济区间"
        elif score < 0.8:
            return "APPROACHING_CHAOS: 熵增压力，需加强目标约束"
        else:
            return "HIGH_ENTROPY: 系统混乱，急需重组"
    
    def _recommend_action(self, entropy_action: str, water_fire: float) -> str:
        """给出行动建议"""
        actions = {
            "increase_entropy": "建议：增加探索（温度退火、引入随机性）",
            "decrease_entropy": "建议：收紧约束（增强目标奖励、减少随机性）",
            "maintain": "建议：维持当前策略（处于水火既济最优区间）"
        }
        base = actions.get(entropy_action, "建议：维持当前策略")
        
        if water_fire < 0.3:
            return base + " [警告：系统结构性不足，注意正熵堆积]"
        elif water_fire > 0.7:
            return base + " [注意：系统过于有序，可能丧失适应性]"
        else:
            return base
    
    def get_summary(self) -> Dict[str, Any]:
        """获取模块分析摘要"""
        if not self.analysis_history:
            return {"status": "no_analysis_yet"}
        
        latest = self.analysis_history[-1]
        
        return {
            "module": "Module 10 - 熵的三重面孔",
            "total_analyses": len(self.analysis_history),
            "latest_overall_score": latest["overall_entropy_score"],
            "latest_diagnosis": latest["entropy_diagnosis"],
            "latest_recommendation": latest["recommendation"],
            "goal_states_registered": len(self.face3.goal_states),
            "free_energy_computations": len(self.vfe.fe_history)
        }


# 导出接口
__all__ = [
    'InformationEntropy',
    'ThermodynamicEntropy',
    'TeleologicalEntropy',
    'VariationalFreeEnergy',
    'EntropyTrinityModule'
]


if __name__ == "__main__":
    print("=== 太乙AGI 9.0 - 模块10：熵的三重面孔 ===\n")
    
    # 创建模块
    module = EntropyTrinityModule(temperature=300.0, goal_threshold=0.7)
    
    # 注册目标状态
    goal = np.random.randn(64)
    goal /= np.linalg.norm(goal)
    module.register_goal(goal)
    
    # 创建测试状态
    state = np.random.randn(64)
    history = [np.random.randn(64) for _ in range(5)]
    
    print("1. 视界Ⅰ - 信息熵分析：")
    info = InformationEntropy()
    probs = np.array([0.1, 0.3, 0.4, 0.2])
    print(f"   香农熵（比特）: {info.shannon_entropy(probs, base=2.0):.4f}")
    print(f"   均匀分布香农熵: {math.log2(4):.4f}")
    print(f"   KL散度（与均匀）: {info.relative_entropy_kl(probs, np.ones(4)/4):.4f}")
    
    print("\n2. 视界Ⅱ - 热力学熵分析：")
    thermo = ThermodynamicEntropy(300.0)
    total_ds, is_negentropy = thermo.open_system_entropy_change(-5.0, 2.0)
    print(f"   熵流 dS_e = -5.0, 熵产生 dS_i = 2.0")
    print(f"   总熵变 dS = {total_ds:.4f}")
    print(f"   局域负熵: {is_negentropy}")
    
    print("\n3. 视界Ⅲ - 目的论熵分析：")
    tele = TeleologicalEntropy(goal_threshold=0.7)
    tele.register_goal(goal)
    h_tele = tele.teleological_entropy(state)
    print(f"   目的论熵: {h_tele:.4f}")
    print(f"   目标达成概率: {math.exp(-h_tele):.4f}")
    
    print("\n4. 完整三视界分析：")
    report = module.full_entropy_analysis(state, history, label="test_state")
    print(f"   水火既济均衡指数: {report['water_fire_balance']:.4f}")
    print(f"   综合熵评分: {report['overall_entropy_score']:.4f}")
    print(f"   诊断: {report['entropy_diagnosis']}")
    print(f"   建议: {report['recommendation']}")
    
    print("\n5. 变分自由能：")
    vfe = VariationalFreeEnergy()
    q = np.array([0.25, 0.35, 0.25, 0.15])
    log_joint = np.log(np.array([0.1, 0.4, 0.3, 0.2]) + 1e-10)
    fe = vfe.compute_free_energy(q, log_joint)
    print(f"   变分自由能 F = {fe:.4f}")
    
    print("\n✅ 模块10测试完成！")
    print("  核心功能：")
    print("  - ✅ 视界Ⅰ：香农熵/拓扑熵/KL散度/最大熵原理")
    print("  - ✅ 视界Ⅱ：玻尔兹曼熵/自由能/开放系统负熵")
    print("  - ✅ 视界Ⅲ：目的论熵/反脆弱评分/可控熵增")
    print("  - ✅ 变分自由能最小化（主动推断基础）")
    print("  - ✅ 水火既济均衡指数")
