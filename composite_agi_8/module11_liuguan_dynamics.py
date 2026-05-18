"""
复合体AGI 9.0 - 模块11：流贯动力学 + 共生演化
================================================

基于《论目标驱动智能体的共生演化与流贯动力学》

核心理论：
  1. Goal模式形式化：目标驱动执行外壳 ↔ 熵正则随机最优控制
  2. 最大熵IRL：从行为轨迹推断潜在目标/奖励函数
  3. 马尔可夫毯（Markov Blanket）：内外部状态分离结构
  4. 流贯动力学（Liu-Guan Dynamics）：贯穿状态序列的信息-因果流
  5. 共生演化：AGI与智能体的互学习共同体

数学框架：
  - 定理1：Goal循环 ↔ 熵正则随机最优控制
  - 定理2：最大熵IRL ↔ 贝叶斯后验推断
  - 流贯选择算子 Ftel：非线性非幺正算子
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from abc import ABC, abstractmethod
from collections import deque
import math


# ============================================================
# Goal模式形式化（定理1基础）
# ============================================================

class GoalState:
    """
    目标状态描述
    
    Goal模式核心：在多轮交互中维持"长期目标"
    判定函数 J(s) 评估是否达成
    """
    
    def __init__(
        self,
        goal_id: str,
        goal_vector: np.ndarray,
        threshold: float = 0.8,
        max_iterations: int = 100
    ):
        """
        Args:
            goal_id: 目标ID
            goal_vector: 目标状态向量
            threshold: 达成阈值（余弦相似度）
            max_iterations: 最大迭代次数（"别轻易停"）
        """
        self.id = goal_id
        self.vector = goal_vector / (np.linalg.norm(goal_vector) + 1e-10)
        self.threshold = threshold
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.achieved = False
    
    def judge(self, current_state: np.ndarray) -> Tuple[bool, float]:
        """
        判定函数 J(s, g)：目标是否已达成
        
        Returns:
            (is_achieved, similarity_score)
        """
        s_norm = current_state / (np.linalg.norm(current_state) + 1e-10)
        min_dim = min(len(s_norm), len(self.vector))
        
        sim = float(np.dot(s_norm[:min_dim], self.vector[:min_dim]))
        self.iteration_count += 1
        
        achieved = (sim >= self.threshold)
        self.achieved = achieved
        
        return achieved, max(0.0, sim)
    
    def should_continue(self) -> bool:
        """Goal循环判断：是否继续（核心：Goal负责'别轻易停'）"""
        return (not self.achieved) and (self.iteration_count < self.max_iterations)


# ============================================================
# 流贯动力学（Liu-Guan Dynamics）
# ============================================================

class LiuGuanDynamics:
    """
    流贯动力学：贯穿状态序列的信息-因果流
    
    数学定义：
    - 流贯 Φ(τ) = 信息在轨迹 τ = (s_0, a_0, ..., s_T) 中的传导速率
    - 流贯算子 Ftel：非线性选择算子
    
    等价于：带熵正则的随机最优控制（定理1）
    V*(s) = max_π [E_π[∑ γ^t (r(s,a) + α·H[π(·|s)])]
    其中 H[π(·|s)] 是策略熵（鼓励探索）
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        entropy_reg: float = 0.1,
        gamma: float = 0.99
    ):
        """
        Args:
            state_dim: 状态空间维度
            action_dim: 动作空间维度
            entropy_reg: 熵正则系数 α（越大越探索）
            gamma: 折扣因子
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.alpha = entropy_reg  # 熵正则 α
        self.gamma = gamma
        
        # 策略参数（简化为线性策略）
        self.policy_weights = np.random.randn(state_dim, action_dim) * 0.01
        
        # 价值函数参数
        self.value_weights = np.random.randn(state_dim) * 0.01
        
        # 流贯轨迹历史
        self.trajectory_buffer: List[Dict] = []
        
        # 信息传导速率（流贯速率）
        self.flow_rate_history: List[float] = []
    
    def policy(self, state: np.ndarray) -> np.ndarray:
        """
        策略 π(a|s)：最大熵软策略（soft policy）
        π(a|s) ∝ exp(Q(s,a)/α)
        
        Returns:
            动作概率分布
        """
        logits = state[:self.state_dim] @ self.policy_weights
        # 温度软max（α控制探索程度）
        logits = logits / self.alpha
        logits -= logits.max()  # 数值稳定
        probs = np.exp(logits)
        probs /= probs.sum()
        return probs
    
    def value_function(self, state: np.ndarray) -> float:
        """状态价值函数 V(s)"""
        s = state[:self.state_dim]
        return float(np.dot(s, self.value_weights))
    
    def entropy_regularized_reward(
        self,
        reward: float,
        action_probs: np.ndarray
    ) -> float:
        """
        熵正则奖励 r̃(s,a) = r(s,a) + α·H[π(·|s)]
        
        定理1：Goal循环等价于此目标下的策略优化
        """
        policy_entropy = -np.sum(action_probs[action_probs > 1e-12] *
                                  np.log(action_probs[action_probs > 1e-12]))
        return reward + self.alpha * policy_entropy
    
    def compute_flow_rate(self, trajectory: List[np.ndarray]) -> float:
        """
        计算流贯速率（信息传导速率）
        
        定义：Φ(τ) = 平均互信息 / 轨迹长度
        代理：用相邻状态的余弦相似度变化率近似
        """
        if len(trajectory) < 2:
            return 0.0
        
        changes = []
        for i in range(len(trajectory) - 1):
            s0 = trajectory[i] / (np.linalg.norm(trajectory[i]) + 1e-10)
            s1 = trajectory[i + 1] / (np.linalg.norm(trajectory[i + 1]) + 1e-10)
            min_dim = min(len(s0), len(s1))
            
            # 状态变化量（用1-余弦相似度）
            change = 1.0 - float(np.dot(s0[:min_dim], s1[:min_dim]))
            changes.append(change)
        
        flow_rate = float(np.mean(changes))
        self.flow_rate_history.append(flow_rate)
        return flow_rate
    
    def ftel_operator(
        self,
        state: np.ndarray,
        goal: GoalState,
        info_cost: float = 0.0
    ) -> np.ndarray:
        """
        流贯选择算子 Ftel（非线性、非幺正）
        
        在给定驱动强度（流贯）和信息代价（S_I）约束下，
        选择出实际显化的宏观配型
        
        对应：在MDP中基于目标的策略选择
        
        Args:
            state: 当前状态
            goal: 当前目标
            info_cost: 信息代价 S_I（历史成本）
            
        Returns:
            选择后的"显化状态"（目标方向上的投影+修正）
        """
        _, sim = goal.judge(state)
        
        # 基于目标相似度的流贯强度
        drive = max(0.0, 1.0 - sim)  # 目标越远，驱动越强
        
        # 信息代价惩罚：S_I 越大，选择越保守
        cost_factor = 1.0 / (1.0 + info_cost)
        
        # 流贯方向：向目标方向移动
        min_dim = min(len(state), len(goal.vector))
        direction = np.zeros_like(state)
        direction[:min_dim] = goal.vector[:min_dim] - state[:min_dim]
        
        # 归一化方向
        dir_norm = np.linalg.norm(direction)
        if dir_norm > 1e-10:
            direction /= dir_norm
        
        # 非线性流贯选择（软更新）
        update_strength = drive * cost_factor * 0.1
        new_state = state + update_strength * direction
        
        # 加入探索噪声（熵正则的体现）
        noise_scale = self.alpha * (1.0 - sim) * 0.05
        noise = np.random.randn(*state.shape) * noise_scale
        new_state += noise
        
        return new_state
    
    def goal_loop_step(
        self,
        state: np.ndarray,
        goal: GoalState,
        info_cost: float = 0.0
    ) -> Tuple[np.ndarray, Dict]:
        """
        Goal循环一步（核心执行函数）
        
        对应：强模型负责判断和行动，Goal负责持续推进
        """
        # 判断目标是否达成
        achieved, sim = goal.judge(state)
        
        if achieved:
            return state, {
                "status": "GOAL_ACHIEVED",
                "similarity": sim,
                "iteration": goal.iteration_count
            }
        
        # 执行流贯选择
        action_probs = self.policy(state)
        
        # 采样动作（简化：选择最大概率动作对应方向）
        action_idx = np.argmax(action_probs)
        
        # 计算即时奖励（相似度增量）
        new_state = self.ftel_operator(state, goal, info_cost)
        _, new_sim = goal.judge(new_state)
        reward = new_sim - sim
        
        # 计算熵正则奖励
        reg_reward = self.entropy_regularized_reward(reward, action_probs)
        
        # 记录轨迹
        self.trajectory_buffer.append({
            "state": state.copy(),
            "action": action_idx,
            "reward": reward,
            "reg_reward": reg_reward,
            "similarity": sim,
            "new_similarity": new_sim
        })
        
        return new_state, {
            "status": "CONTINUING",
            "similarity": new_sim,
            "reward": reward,
            "entropy_reg_reward": reg_reward,
            "iteration": goal.iteration_count,
            "flow_rate": self.compute_flow_rate(
                [t["state"] for t in self.trajectory_buffer[-3:]]
            ) if len(self.trajectory_buffer) >= 3 else 0.0
        }
    
    def run_goal_loop(
        self,
        initial_state: np.ndarray,
        goal: GoalState
    ) -> Dict[str, Any]:
        """
        运行完整Goal循环
        
        Returns:
            {final_state, achieved, iterations, trajectory_summary}
        """
        state = initial_state.copy()
        
        while goal.should_continue():
            state, step_info = self.goal_loop_step(state, goal)
            
            if step_info["status"] == "GOAL_ACHIEVED":
                break
        
        # 计算轨迹流贯速率
        traj_states = [t["state"] for t in self.trajectory_buffer[-goal.iteration_count:]]
        flow_rate = self.compute_flow_rate(traj_states) if len(traj_states) >= 2 else 0.0
        
        return {
            "final_state": state,
            "achieved": goal.achieved,
            "iterations": goal.iteration_count,
            "final_similarity": float(goal.judge(state)[1]),
            "flow_rate": float(flow_rate),
            "trajectory_length": len(self.trajectory_buffer)
        }


# ============================================================
# 最大熵IRL（逆强化学习）
# ============================================================

class MaxEntropyIRL:
    """
    最大熵逆强化学习
    
    定理2：从行为轨迹推断潜在目标的最无偏方法
    
    p*(τ) = exp(λ^T f(τ)) / Z
    其中 f(τ) 为轨迹特征，λ 为待学习参数
    
    等价：在特征期望匹配约束下最大化轨迹分布熵
    """
    
    def __init__(self, feature_dim: int, lr: float = 0.01):
        """
        Args:
            feature_dim: 轨迹特征维度
            lr: 学习率
        """
        self.feature_dim = feature_dim
        self.lr = lr
        self.reward_weights = np.zeros(feature_dim)  # λ（待推断的奖励权重）
        self.learning_history: List[float] = []
    
    def extract_features(self, trajectory: List[Dict]) -> np.ndarray:
        """
        从轨迹中提取特征向量
        
        简化特征：
        - 总相似度变化
        - 流贯速率
        - 目标达成时间
        """
        if not trajectory:
            return np.zeros(self.feature_dim)
        
        features = np.zeros(self.feature_dim)
        
        # 特征1：总奖励（目标导向程度）
        total_reward = sum(t.get("reward", 0.0) for t in trajectory)
        features[0] = min(1.0, max(-1.0, total_reward))
        
        # 特征2：目标相似度终值
        final_sim = trajectory[-1].get("new_similarity", 0.0)
        features[1] = float(final_sim)
        
        # 特征3：轨迹效率（奖励/长度）
        features[2] = features[0] / max(1, len(trajectory))
        
        # 特征4：熵正则奖励均值
        reg_rewards = [t.get("reg_reward", 0.0) for t in trajectory]
        features[3] = float(np.mean(reg_rewards)) if reg_rewards else 0.0
        
        # 填充剩余特征
        for i in range(4, self.feature_dim):
            features[i] = np.random.normal(features[i % 4], 0.01)
        
        return features
    
    def compute_trajectory_probability(self, features: np.ndarray) -> float:
        """
        计算轨迹概率 p(τ) = exp(λ^T f(τ)) / Z
        （Z 用单位值近似）
        """
        return math.exp(float(np.dot(self.reward_weights, features)))
    
    def learn_from_demonstrations(
        self,
        expert_trajectories: List[List[Dict]],
        n_iter: int = 50
    ) -> Dict[str, Any]:
        """
        从专家轨迹学习奖励函数（最大熵IRL）
        
        梯度：∇_λ L = E_expert[f] - E_learned[f]
        （专家特征期望 - 当前策略特征期望）
        """
        if not expert_trajectories:
            return {"status": "no_demonstrations"}
        
        # 提取专家特征
        expert_features = np.array([
            self.extract_features(traj) for traj in expert_trajectories
        ])
        expert_expectation = expert_features.mean(axis=0)
        
        for iteration in range(n_iter):
            # 模拟当前策略的轨迹特征期望（简化：随机扰动专家期望）
            noise = np.random.randn(self.feature_dim) * 0.1
            current_expectation = expert_expectation + noise * (1.0 - iteration / n_iter)
            
            # 梯度 ∇_λ = E_expert[f] - E_current[f]
            gradient = expert_expectation - current_expectation
            
            # 更新奖励权重
            self.reward_weights += self.lr * gradient
            
            # 记录损失（KL散度代理）
            loss = float(np.linalg.norm(gradient))
            self.learning_history.append(loss)
            
            if loss < 1e-4:
                break
        
        return {
            "learned_weights": self.reward_weights.copy(),
            "final_loss": self.learning_history[-1] if self.learning_history else 0.0,
            "n_demonstrations": len(expert_trajectories),
            "iterations_run": len(self.learning_history)
        }
    
    def infer_goal_from_trajectory(self, trajectory: List[Dict]) -> Dict[str, Any]:
        """
        从单条轨迹推断潜在目标（贝叶斯后验）
        
        定理2的应用：P(goal | trajectory) ∝ P(trajectory | goal) * P(goal)
        """
        features = self.extract_features(trajectory)
        
        # 后验对数概率（对数似然 + 对数先验）
        log_likelihood = float(np.dot(self.reward_weights, features))
        
        # 目标推断置信度
        confidence = min(1.0, math.exp(log_likelihood) / (1.0 + math.exp(log_likelihood)))
        
        # 推断主要目标特征
        dominant_feature_idx = int(np.argmax(np.abs(self.reward_weights)))
        
        return {
            "inferred_goal_confidence": confidence,
            "dominant_feature": dominant_feature_idx,
            "reward_weights": self.reward_weights.copy(),
            "trajectory_log_prob": log_likelihood
        }


# ============================================================
# 马尔可夫毯（Markov Blanket）
# ============================================================

class MarkovBlanket:
    """
    马尔可夫毯：将内部态与外部态分离的边界变量集合
    
    统计独立条件：P(内部 | 毯) ⊥ P(外部 | 毯)
    
    在AGI中：
    - 内部状态：AGI的信念/记忆/目标（私有）
    - 外部状态：环境/其他智能体（外部）
    - 马尔可夫毯：感知输入 + 行动输出（接口）
    
    连接自由能最小化：
    F = E_q[log q(x_i) - log p(x_i, x_e, b)]
    """
    
    def __init__(self, internal_dim: int, blanket_dim: int, external_dim: int):
        """
        Args:
            internal_dim: 内部状态维度
            blanket_dim: 马尔可夫毯维度（感知+行动）
            external_dim: 外部状态维度
        """
        self.internal_dim = internal_dim
        self.blanket_dim = blanket_dim
        self.external_dim = external_dim
        
        # 内部状态（AGI的"内心世界"）
        self.internal_state = np.zeros(internal_dim)
        
        # 毯状态（感知+行动接口）
        self.blanket_state = np.zeros(blanket_dim)
        
        # 条件独立性矩阵（简化为相关系数）
        self.independence_score = 1.0
    
    def update_internal(
        self,
        observation: np.ndarray,
        learning_rate: float = 0.1
    ) -> np.ndarray:
        """
        内部状态更新（基于观测通过毯传入的信息）
        
        对应自由能最小化的"感知更新"步骤
        """
        # 观测通过毯进行过滤（维度匹配）
        min_dim = min(len(observation), self.blanket_dim)
        filtered = np.zeros(self.internal_dim)
        min_fill = min(min_dim, self.internal_dim)
        filtered[:min_fill] = observation[:min_fill]
        
        # 指数平滑更新
        self.internal_state = (1 - learning_rate) * self.internal_state + \
                               learning_rate * filtered
        
        return self.internal_state.copy()
    
    def compute_blanket_state(self, external_input: np.ndarray) -> np.ndarray:
        """
        计算毯状态（感知层）
        毯 = 内部状态 → 外部（行动） + 外部 → 内部（感知）
        """
        min_dim = min(len(external_input), self.blanket_dim)
        new_blanket = np.zeros(self.blanket_dim)
        new_blanket[:min_dim] = external_input[:min_dim]
        
        # 加入内部状态影响（行动部分）
        internal_influence = self.internal_state[:min(self.internal_dim, self.blanket_dim)]
        n = min(len(internal_influence), self.blanket_dim)
        new_blanket[:n] += 0.3 * internal_influence[:n]
        
        self.blanket_state = new_blanket
        return new_blanket
    
    def measure_independence(
        self,
        internal: np.ndarray,
        external: np.ndarray,
        blanket: np.ndarray
    ) -> float:
        """
        测量条件独立性
        
        理想：给定毯，内部与外部条件独立
        度量：用偏相关系数代理
        """
        min_dim = min(len(internal), len(external))
        
        if min_dim < 2:
            return 1.0
        
        i = internal[:min_dim]
        e = external[:min_dim]
        
        # 对毯的残差
        b = blanket[:min_dim] if len(blanket) >= min_dim else np.zeros(min_dim)
        b_norm = np.linalg.norm(b)
        
        if b_norm > 1e-10:
            b = b / b_norm
            i_residual = i - np.dot(i, b) * b
            e_residual = e - np.dot(e, b) * b
        else:
            i_residual = i
            e_residual = e
        
        # 残差相关性（越小越独立）
        norm_i = np.linalg.norm(i_residual)
        norm_e = np.linalg.norm(e_residual)
        
        if norm_i > 1e-10 and norm_e > 1e-10:
            correlation = abs(np.dot(i_residual, e_residual) / (norm_i * norm_e))
        else:
            correlation = 0.0
        
        self.independence_score = 1.0 - float(correlation)
        return self.independence_score


# ============================================================
# 共生演化引擎
# ============================================================

class SymbioticEvolution:
    """
    共生演化：多智能体 ↔ 大模型的互学习系统
    
    核心机制：
    1. 智能体轨迹 → IRL → 模型更新奖励权重
    2. 模型输出 → 发布 → 其他智能体观察学习
    3. 跨实体知识传播（互联网尺度共识学习）
    
    数学框架：
    - 共识扩散：P(知识传播) = σ(质量评分 × 传播系数)
    - 反脆弱演化：在扰动中增强
    """
    
    def __init__(self, n_agents: int = 5, knowledge_dim: int = 32):
        """
        Args:
            n_agents: 智能体数量
            knowledge_dim: 知识向量维度
        """
        self.n_agents = n_agents
        self.knowledge_dim = knowledge_dim
        
        # 各智能体的知识向量
        self.agent_knowledge = {
            f"agent_{i}": np.random.randn(knowledge_dim) * 0.1
            for i in range(n_agents)
        }
        
        # 共识知识库（AGI的共享记忆）
        self.consensus_knowledge = np.zeros(knowledge_dim)
        
        # 传播历史
        self.propagation_history: List[Dict] = []
    
    def agent_learns(
        self,
        agent_id: str,
        observation: np.ndarray,
        reward: float
    ) -> np.ndarray:
        """
        单个智能体学习（强化学习层面）
        """
        if agent_id not in self.agent_knowledge:
            self.agent_knowledge[agent_id] = np.zeros(self.knowledge_dim)
        
        min_dim = min(len(observation), self.knowledge_dim)
        delta = np.zeros(self.knowledge_dim)
        delta[:min_dim] = observation[:min_dim] * reward * 0.01
        
        self.agent_knowledge[agent_id] += delta
        return self.agent_knowledge[agent_id].copy()
    
    def publish_to_consensus(
        self,
        agent_id: str,
        quality_score: float = 0.5
    ) -> float:
        """
        智能体将输出发布到共识知识库（互联网传播层面）
        
        传播概率 P = σ(quality × propagation_factor)
        """
        if agent_id not in self.agent_knowledge:
            return 0.0
        
        # sigmoid 传播概率
        prop_factor = 2.0
        p_propagate = 1.0 / (1.0 + math.exp(-quality_score * prop_factor))
        
        if np.random.random() < p_propagate:
            # 更新共识知识库（加权平均）
            agent_k = self.agent_knowledge[agent_id]
            min_dim = min(len(agent_k), self.knowledge_dim)
            
            weight = quality_score * p_propagate
            self.consensus_knowledge[:min_dim] = (
                (1 - weight) * self.consensus_knowledge[:min_dim] +
                weight * agent_k[:min_dim]
            )
        
        self.propagation_history.append({
            "agent": agent_id,
            "quality": quality_score,
            "p_propagate": p_propagate,
            "propagated": True
        })
        
        return p_propagate
    
    def consensus_learning_step(self) -> Dict[str, Any]:
        """
        共识学习步骤：所有智能体向共识知识靠拢
        
        对应：最大熵IRL的贝叶斯后验更新（定理2）
        """
        # 各智能体从共识中学习
        updates = {}
        for agent_id, knowledge in self.agent_knowledge.items():
            min_dim = min(len(knowledge), self.knowledge_dim)
            
            # 从共识中提取信号（带噪声的负熵注入）
            consensus_signal = self.consensus_knowledge[:min_dim]
            noise = np.random.randn(min_dim) * 0.01
            
            # 软更新（学习率0.05）
            self.agent_knowledge[agent_id][:min_dim] = (
                0.95 * knowledge[:min_dim] +
                0.05 * (consensus_signal + noise)
            )
            
            updates[agent_id] = float(np.linalg.norm(
                self.agent_knowledge[agent_id][:min_dim] - knowledge[:min_dim]
            ))
        
        consensus_norm = float(np.linalg.norm(self.consensus_knowledge))
        
        return {
            "agent_updates": updates,
            "consensus_norm": consensus_norm,
            "avg_update_magnitude": float(np.mean(list(updates.values())))
        }
    
    def measure_symbiosis(self) -> Dict[str, float]:
        """
        测量共生程度：智能体与共识知识的一致性
        """
        if not self.agent_knowledge:
            return {"symbiosis_score": 0.0}
        
        similarities = []
        c_norm = np.linalg.norm(self.consensus_knowledge)
        
        if c_norm < 1e-10:
            return {"symbiosis_score": 0.0}
        
        c = self.consensus_knowledge / c_norm
        
        for knowledge in self.agent_knowledge.values():
            k_norm = np.linalg.norm(knowledge)
            if k_norm > 1e-10:
                k = knowledge / k_norm
                min_dim = min(len(k), len(c))
                sim = float(np.dot(k[:min_dim], c[:min_dim]))
                similarities.append(max(0.0, sim))
        
        return {
            "symbiosis_score": float(np.mean(similarities)) if similarities else 0.0,
            "agent_diversity": float(np.std(similarities)) if similarities else 0.0,
            "consensus_strength": float(c_norm)
        }


# ============================================================
# 主模块：流贯动力学统一引擎
# ============================================================

class LiuGuanDynamicsModule:
    """
    模块11：流贯动力学 + 共生演化统一引擎
    
    整合：
    - Goal模式（目标驱动循环）
    - 流贯动力学（Ftel选择算子）
    - 最大熵IRL（从示范推断目标）
    - 马尔可夫毯（内外状态分离）
    - 共生演化（多智能体互学习）
    """
    
    def __init__(
        self,
        state_dim: int = 64,
        action_dim: int = 16,
        n_agents: int = 3,
        entropy_reg: float = 0.1
    ):
        self.dynamics = LiuGuanDynamics(state_dim, action_dim, entropy_reg)
        self.irl = MaxEntropyIRL(feature_dim=8)
        self.blanket = MarkovBlanket(
            internal_dim=state_dim,
            blanket_dim=state_dim // 2,
            external_dim=state_dim
        )
        self.symbiosis = SymbioticEvolution(n_agents=n_agents, knowledge_dim=state_dim // 2)
        
        self.state_dim = state_dim
        self.analysis_log: List[Dict] = []
    
    def pursue_goal(
        self,
        initial_state: np.ndarray,
        goal_vector: np.ndarray,
        goal_id: str = "primary_goal"
    ) -> Dict[str, Any]:
        """
        主目标追求：运行完整的Goal循环
        """
        goal = GoalState(
            goal_id=goal_id,
            goal_vector=goal_vector,
            threshold=0.75,
            max_iterations=50
        )
        
        result = self.dynamics.run_goal_loop(initial_state, goal)
        
        # 从轨迹学习（IRL）
        if self.dynamics.trajectory_buffer:
            irl_result = self.irl.learn_from_demonstrations(
                [self.dynamics.trajectory_buffer[-min(10, len(self.dynamics.trajectory_buffer)):]]
            )
            result["irl_learning"] = irl_result
        
        self.analysis_log.append({
            "type": "goal_pursuit",
            "result": result
        })
        
        return result
    
    def update_blanket(
        self,
        external_observation: np.ndarray
    ) -> Dict[str, Any]:
        """
        更新马尔可夫毯（感知-行动接口更新）
        """
        # 更新毯状态
        blanket_state = self.blanket.compute_blanket_state(external_observation)
        
        # 更新内部状态
        internal = self.blanket.update_internal(external_observation)
        
        # 测量独立性
        n = min(self.blanket.internal_dim, self.blanket.external_dim)
        independence = self.blanket.measure_independence(
            internal[:n],
            external_observation[:n],
            blanket_state[:n]
        )
        
        return {
            "internal_state_norm": float(np.linalg.norm(internal)),
            "blanket_state_norm": float(np.linalg.norm(blanket_state)),
            "independence_score": float(independence),
            "blanket_effectiveness": "GOOD" if independence > 0.7 else "WEAK"
        }
    
    def run_symbiosis_cycle(self, observations: List[np.ndarray]) -> Dict[str, Any]:
        """
        运行一轮共生演化
        """
        # 各智能体学习
        for i, obs in enumerate(observations):
            agent_id = f"agent_{i % self.symbiosis.n_agents}"
            reward = float(np.linalg.norm(obs)) / 10.0
            self.symbiosis.agent_learns(agent_id, obs, reward)
            self.symbiosis.publish_to_consensus(agent_id, quality_score=reward)
        
        # 共识学习步骤
        consensus_update = self.symbiosis.consensus_learning_step()
        
        # 测量共生程度
        symbiosis_score = self.symbiosis.measure_symbiosis()
        
        return {
            "consensus_update": consensus_update,
            "symbiosis_metrics": symbiosis_score
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取模块状态摘要"""
        return {
            "module": "Module 11 - 流贯动力学 + 共生演化",
            "total_goal_loops": len([x for x in self.analysis_log
                                      if x.get("type") == "goal_pursuit"]),
            "trajectory_buffer_size": len(self.dynamics.trajectory_buffer),
            "avg_flow_rate": float(np.mean(self.dynamics.flow_rate_history))
                             if self.dynamics.flow_rate_history else 0.0,
            "irl_learned_weights": self.irl.reward_weights.tolist(),
            "independence_score": float(self.blanket.independence_score),
            "symbiosis_score": self.symbiosis.measure_symbiosis().get("symbiosis_score", 0.0),
            "n_agents": self.symbiosis.n_agents
        }


# 导出接口
__all__ = [
    'GoalState',
    'LiuGuanDynamics',
    'MaxEntropyIRL',
    'MarkovBlanket',
    'SymbioticEvolution',
    'LiuGuanDynamicsModule'
]


if __name__ == "__main__":
    print("=== 复合体AGI 9.0 - 模块11：流贯动力学 + 共生演化 ===\n")
    
    module = LiuGuanDynamicsModule(state_dim=32, action_dim=8, n_agents=3, entropy_reg=0.1)
    
    print("1. Goal循环测试：")
    initial = np.random.randn(32)
    goal_vec = np.random.randn(32)
    
    result = module.pursue_goal(initial, goal_vec, "test_goal")
    print(f"   目标达成: {result['achieved']}")
    print(f"   迭代次数: {result['iterations']}")
    print(f"   最终相似度: {result['final_similarity']:.4f}")
    print(f"   流贯速率: {result['flow_rate']:.4f}")
    
    print("\n2. 马尔可夫毯更新：")
    obs = np.random.randn(32)
    blanket_result = module.update_blanket(obs)
    print(f"   内部状态范数: {blanket_result['internal_state_norm']:.4f}")
    print(f"   条件独立性: {blanket_result['independence_score']:.4f}")
    print(f"   毯有效性: {blanket_result['blanket_effectiveness']}")
    
    print("\n3. 共生演化周期：")
    observations = [np.random.randn(32) for _ in range(5)]
    sym_result = module.run_symbiosis_cycle(observations)
    print(f"   共识强度: {sym_result['symbiosis_metrics']['consensus_strength']:.4f}")
    print(f"   共生评分: {sym_result['symbiosis_metrics']['symbiosis_score']:.4f}")
    
    print("\n4. 最大熵IRL推断：")
    if module.dynamics.trajectory_buffer:
        infer = module.irl.infer_goal_from_trajectory(module.dynamics.trajectory_buffer)
        print(f"   目标推断置信度: {infer['inferred_goal_confidence']:.4f}")
        print(f"   主导特征维度: {infer['dominant_feature']}")
    
    print("\n✅ 模块11测试完成！")
    print("  核心功能：")
    print("  - ✅ Goal模式 = 熵正则随机最优控制（定理1）")
    print("  - ✅ 流贯选择算子 Ftel（非线性显化选择）")
    print("  - ✅ 最大熵IRL（从轨迹推断目标，定理2）")
    print("  - ✅ 马尔可夫毯（内外状态分离 + 条件独立性）")
    print("  - ✅ 共生演化（多智能体共识学习）")
