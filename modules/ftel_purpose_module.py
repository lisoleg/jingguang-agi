# -*- coding: utf-8 -*-
"""
FtelPurposeModule - 目的约束算子模块
复合体AGI 5.0 核心模块

基于章锋论文《经络作为△上的持久同调1-圈》中的Ftel算子理论：
- 目的约束算子（Teleological Constraint Operator）
- 将目标作为约束场投影至生成空间
- 实现从"相关性"到"目的性"的跃迁
"""

import numpy as np
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field


@dataclass
class FtelConfig:
    """Ftel配置参数"""
    lambda_weight: float = 0.3  # 目的权重 (0-1)
    min_goal_similarity: float = 0.5  # 最小目标相似度
    convergence_threshold: float = 1e-4  # 收敛阈值
    max_iterations: int = 100  # 最大迭代次数
    learning_rate: float = 0.01  # 学习率


class FtelPurposeModule:
    """
    Ftel目的约束算子模块
    
    核心功能：
    1. 将用户意图/目标转化为约束向量
    2. 在作用量泛函中引入目的项
    3. 引导系统沿最小作用量路径演化
    4. 实现从"相关性"到"目的性"的跃迁
    
    数学形式化：
    - 目标向量: g (telos/goal)
    - 约束场: C(g) = ||θ - projection_on_g(θ)||²
    - 作用量: S = S_data + λ·C(g)
    - 最小化S → 沿目的方向的最优解
    
    与Attention的关系：
    - Attention: "从已有信息里选什么" (相关性)
    - Ftel: "我们为什么要选、选来干什么" (目的性)
    """
    
    def __init__(self, config: Optional[FtelConfig] = None):
        self.config = config or FtelConfig()
        self.goal_vector: Optional[np.ndarray] = None
        self.goal_description: str = ""
        self.purpose_history: list = []
        self.alignment_scores: list = []
        
    def set_goal(self, goal_description: str, goal_vector: Optional[np.ndarray] = None):
        """
        设置目标（目的）
        
        Args:
            goal_description: 自然语言描述的目标
            goal_vector: 可选的预编码目标向量
        """
        self.goal_description = goal_description
        
        if goal_vector is not None:
            self.goal_vector = goal_vector
        else:
            # 需要外部embedding模型编码
            # 这里使用简单的随机初始化作为占位符
            self.goal_vector = self._create_goal_vector(goal_description)
        
        self.purpose_history.append({
            'description': goal_description,
            'vector': self.goal_vector.copy(),
            'timestamp': len(self.purpose_history)
        })
        
        return self
    
    def _create_goal_vector(self, description: str, dim: int = 512) -> np.ndarray:
        """
        创建目标向量（占位实现）
        
        实际应用中应使用embedding模型（如OpenAI text-embedding, BERT等）
        这里使用基于描述的确定性随机种子
        """
        # 基于描述的哈希创建确定性向量
        np.random.seed(hash(description) % (2**32))
        vector = np.random.randn(dim)
        vector = vector / (np.linalg.norm(vector) + 1e-10)
        return vector
    
    def compute_purpose_field(self, state_vector: np.ndarray) -> float:
        """
        计算目的势场
        
        目的势场 C(g) 衡量当前状态与目标的偏离程度
        C(g) = 1 - alignment(state, goal)
        
        Args:
            state_vector: 当前状态向量
            
        Returns:
            目的势场值 (越小越接近目标)
        """
        if self.goal_vector is None:
            return 1.0  # 无目标时返回最大值
        
        # 计算余弦相似度
        alignment = self._cosine_similarity(state_vector, self.goal_vector)
        
        # 目的势场 = 1 - 对齐度
        purpose_field = 1.0 - alignment
        
        return max(0.0, purpose_field)
    
    def compute_purpose_gradient(self, state_vector: np.ndarray) -> np.ndarray:
        """
        计算目的梯度 ∇C(g)
        
        梯度指向目的势场下降最快的方向
        
        Args:
            state_vector: 当前状态向量
            
        Returns:
            目的梯度向量
        """
        if self.goal_vector is None:
            return np.zeros_like(state_vector)
        
        # 简化的梯度计算：state - goal的投影
        diff = state_vector - self.goal_vector
        
        # 投影到与state正交的方向
        projection_scalar = np.dot(diff, state_vector) / (np.dot(state_vector, state_vector) + 1e-10)
        gradient = diff - projection_scalar * state_vector
        
        return gradient
    
    def guided_gradient(self, 
                        data_gradient: np.ndarray, 
                        purpose_gradient: Optional[np.ndarray] = None) -> np.ndarray:
        """
        目的引导的梯度
        
        S' = S_data + λ·C(g)
        ∇S' = (1-λ)·∇S_data + λ·∇C(g)
        
        Args:
            data_gradient: 数据驱动的梯度
            purpose_gradient: 可选的目的梯度（如果为None则自动计算）
            
        Returns:
            目的引导后的梯度
        """
        if purpose_gradient is None:
            # 使用当前状态计算目的梯度
            if hasattr(self, '_current_state'):
                purpose_gradient = self.compute_purpose_gradient(self._current_state)
            else:
                purpose_gradient = np.zeros_like(data_gradient)
        
        λ = self.config.lambda_weight
        
        # 组合梯度
        guided = (1 - λ) * data_gradient + λ * purpose_gradient
        
        return guided
    
    def purpose_directed_update(self, 
                                current_state: np.ndarray,
                                data_gradient: np.ndarray,
                                update_scale: float = 1.0) -> np.ndarray:
        """
        目的导向的状态更新
        
        执行一步目的引导的梯度下降
        
        Args:
            current_state: 当前状态
            data_gradient: 数据梯度
            update_scale: 更新幅度缩放
            
        Returns:
            更新后的状态
        """
        self._current_state = current_state
        
        # 计算目的引导梯度
        guided_grad = self.guided_gradient(data_gradient)
        
        # 梯度下降更新
        new_state = current_state - self.config.learning_rate * update_scale * guided_grad
        
        # 记录对齐分数
        alignment = 1.0 - self.compute_purpose_field(new_state)
        self.alignment_scores.append(alignment)
        
        return new_state
    
    def purpose_guided_attention(self,
                                  query: np.ndarray,
                                  keys: np.ndarray,
                                  values: np.ndarray,
                                  purpose_vector: Optional[np.ndarray] = None) -> np.ndarray:
        """
        目的引导的Attention
        
        在标准Attention基础上引入目的偏置
        
        标准Attention: attention_weights = softmax(query @ keys.T)
        目的Attention: attention_weights = softmax(query @ keys.T + β·purpose_field)
        
        Args:
            query: 查询向量 [d]
            keys: 键向量矩阵 [n, d]
            values: 值向量矩阵 [n, d]
            purpose_vector: 目的向量（如果为None则使用当前goal_vector）
            
        Returns:
            聚合后的值向量
        """
        if purpose_vector is None:
            purpose_vector = self.goal_vector
            
        # 标准Attention权重
        attention_logits = query @ keys.T
        attention_weights = self._softmax(attention_logits)
        
        if purpose_vector is not None:
            # 计算目的势场对每个key的偏置
            purpose_fields = np.array([
                1.0 - self._cosine_similarity(k, purpose_vector) 
                for k in keys
            ])
            
            # 目的偏置：降低远离目标的注意力
            purpose_bias = self.config.lambda_weight * purpose_fields
            attention_weights = attention_weights * (1 - purpose_bias)
            attention_weights = attention_weights / (attention_weights.sum() + 1e-10)
        
        # 加权聚合
        output = attention_weights @ values
        
        return output
    
    def multi_objective_optimization(self,
                                       objectives: list,
                                       weights: Optional[list] = None) -> np.ndarray:
        """
        多目标目的优化
        
        当存在多个目标时，进行帕累托优化
        
        Args:
            objectives: 目标函数列表，每个函数接受state返回标量
            weights: 目标权重列表
            
        Returns:
            近似帕累托最优解
        """
        if weights is None:
            weights = [1.0 / len(objectives)] * len(objectives)
        
        # 简化的加权求和法
        def combined_objective(state):
            return sum(w * obj(state) for w, obj in zip(weights, objectives))
        
        # 使用梯度下降找到最优
        state = np.random.randn(512)
        state = state / np.linalg.norm(state)
        
        for _ in range(self.config.max_iterations):
            grad = self._numerical_gradient(combined_objective, state)
            state = state - self.config.learning_rate * grad
            
            if np.linalg.norm(grad) < self.config.convergence_threshold:
                break
        
        return state
    
    def goal_decomposition(self, 
                           high_level_goal: str,
                           sub_goals: list) -> Dict[str, Any]:
        """
        目标分解
        
        将高层目标分解为子目标
        
        Args:
            high_level_goal: 高层目标描述
            sub_goals: 子目标列表
            
        Returns:
            分解后的子目标结构
        """
        decomposition = {
            'high_level': high_level_goal,
            'sub_goals': [],
            'dependencies': [],
            'purpose_chain': []
        }
        
        for i, sub_goal in enumerate(sub_goals):
            decomposition['sub_goals'].append({
                'id': i,
                'description': sub_goal,
                'weight': 1.0 / len(sub_goals),  # 平均权重
                'achieved': False,
                'partial_progress': 0.0
            })
            
            decomposition['purpose_chain'].append({
                'from': high_level_goal,
                'to': sub_goal,
                'purpose': f"为了实现 {high_level_goal}，需要先完成：{sub_goal}"
            })
        
        return decomposition
    
    def purpose_alignment_check(self, 
                                 action: np.ndarray,
                                 expected_outcome: np.ndarray) -> Dict[str, float]:
        """
        目的对齐检查
        
        检查动作是否朝向预期结果
        
        Args:
            action: 执行的动作向量
            expected_outcome: 预期结果向量
            
        Returns:
            对齐检查结果
        """
        if self.goal_vector is None:
            return {'aligned': True, 'alignment_score': 0.0, 'warning': 'No goal set'}
        
        # 计算动作方向与目标方向的对齐度
        action_direction = action / (np.linalg.norm(action) + 1e-10)
        alignment_score = self._cosine_similarity(action_direction, self.goal_vector)
        
        # 计算与预期结果的偏差
        outcome_deviation = np.linalg.norm(action - expected_outcome)
        
        return {
            'aligned': alignment_score > self.config.min_goal_similarity,
            'alignment_score': alignment_score,
            'outcome_deviation': outcome_deviation,
            'recommendation': 'Continue' if alignment_score > 0.7 else 'Adjust direction'
        }
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax函数"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / (exp_x.sum() + 1e-10)
    
    def _numerical_gradient(self, f: Callable, x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        """数值梯度计算"""
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad
    
    def get_purpose_diagnostics(self) -> Dict[str, Any]:
        """
        获取目的诊断信息
        
        Returns:
            包含目的系统状态的诊断信息
        """
        return {
            'goal_set': self.goal_vector is not None,
            'goal_description': self.goal_description,
            'lambda_weight': self.config.lambda_weight,
            'purpose_history_length': len(self.purpose_history),
            'alignment_trend': self.alignment_scores[-10:] if self.alignment_scores else [],
            'convergence_status': 'converged' if len(self.alignment_scores) > 10 and 
                                   np.std(self.alignment_scores[-10:]) < 0.01 else 'optimizing'
        }
    
    def reset(self):
        """重置模块状态"""
        self.goal_vector = None
        self.goal_description = ""
        self.purpose_history = []
        self.alignment_scores = []
        if hasattr(self, '_current_state'):
            del self._current_state


# 工厂函数
def create_ftel_module(lambda_weight: float = 0.3) -> FtelPurposeModule:
    """
    创建Ftel目的约束模块
    
    Args:
        lambda_weight: 目的权重
        
    Returns:
        FtelPurposeModule实例
    """
    config = FtelConfig(lambda_weight=lambda_weight)
    return FtelPurposeModule(config)


if __name__ == "__main__":
    # 简单测试
    print("=" * 60)
    print("Ftel目的约束模块 - 简单测试")
    print("=" * 60)
    
    # 创建模块
    ftel = create_ftel_module(lambda_weight=0.4)
    
    # 设置目标
    ftel.set_goal("实现人工智能的安全对齐")
    
    # 模拟状态
    state = np.random.randn(512)
    state = state / np.linalg.norm(state)
    
    # 计算目的势场
    purpose_field = ftel.compute_purpose_field(state)
    print(f"\n目的势场值: {purpose_field:.4f}")
    
    # 计算目的梯度
    purpose_grad = ftel.compute_purpose_gradient(state)
    print(f"目的梯度范数: {np.linalg.norm(purpose_grad):.4f}")
    
    # 目的引导的更新
    data_grad = np.random.randn(512) * 0.1
    new_state = ftel.purpose_directed_update(state, data_grad)
    print(f"状态更新后对齐度: {ftel.alignment_scores[-1]:.4f}")
    
    # 诊断信息
    diagnostics = ftel.get_purpose_diagnostics()
    print(f"\n诊断信息:")
    for k, v in diagnostics.items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("Ftel模块测试完成")
    print("=" * 60)
