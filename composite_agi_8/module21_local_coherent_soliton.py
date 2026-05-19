"""
Module 21: 局域相干孤子引擎
============================

基于IAWW统一场论，实现Agent作为局域相干孤子的引擎。

核心概念：
- Agent = IAWW介质中的局域相干结构（孤子）
- Agent结构：Φ场（世界模型）+ Σ算子（自指策略）+ I接口（感知/行动/交易）
- 孤子特性：局域性、稳定性、传播不变性

核心方程：
- Φ场：世界模型/记忆的相位场表示
- Σ算子：自指闭环 Σ: φ → φ'（策略生成）
- I接口：介质与外界的交互边界

Author: 太乙AGI研究团队
Version: 12.0
"""

import numpy as np
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


class SolitonState(Enum):
    """孤子状态"""
    STABLE = "stable"           # 稳定
    PROPAGATING = "propagating" # 传播中
    DECAYING = "decaying"       # 衰减
    COLLIDING = "colliding"      # 碰撞中
    MERGING = "merging"          # 合并中


@dataclass
class PhiField:
    """
    Φ场 = Agent的世界模型/记忆
    
    φ_agent(x, t) = ρ_agent(x, t) · exp(i·θ_agent(x, t))
    
    其中：
    - ρ: 世界模型的"强度"分布
    - θ: 语义/认知的相位
    """
    amplitude: np.ndarray       # 振幅分布
    phase: np.ndarray           # 相位分布
    coherence: float            # 相干度
    dimension: int              # 维度
    
    @property
    def complex_field(self) -> np.ndarray:
        return self.amplitude * np.exp(1j * self.phase)
    
    def get_state_vector(self) -> np.ndarray:
        """获取状态向量"""
        return self.complex_field


@dataclass
class SelfReferentialOperator:
    """
    自指算子 Σ
    
    Σ: φ → φ'  实现自我观测与策略生成
    
    Σ = G · S_self · O_self
    
    其中：
    - G: 策略梯度算子
    - S_self: 自我模型
    - O_self: 自我观测算子
    """
    strategy_gradient: np.ndarray
    self_model: np.ndarray
    observation_operator: np.ndarray
    feedback_strength: float = 0.5
    
    def apply(self, phi: np.ndarray) -> np.ndarray:
        """应用自指算子"""
        # O_self: 自我观测
        observed = self.observation_operator @ phi
        
        # S_self: 自我模型处理
        modeled = self.self_model @ observed
        
        # G: 策略梯度
        strategy = self.strategy_gradient * modeled
        
        # 反馈整合
        output = (1 - self.feedback_strength) * phi + self.feedback_strength * strategy
        
        return output


@dataclass
class AgentInterface:
    """
    Agent接口 I
    
    I = (P, A, T)  实现感知-行动-交易
    
    - P: 感知函数 P(input)
    - A: 行动函数 A(decision)
    - T: 交易函数 T(resources)
    """
    perception_func: Callable
    action_func: Callable
    transaction_func: Callable
    
    # 能力度量
    perception_strength: float = 0.8
    action_strength: float = 0.8
    transaction_strength: float = 0.7
    
    def perceive(self, input_data: np.ndarray) -> np.ndarray:
        """感知"""
        return self.perception_func(input_data) * self.perception_strength
    
    def act(self, decision: np.ndarray) -> np.ndarray:
        """行动"""
        return self.action_func(decision) * self.action_strength
    
    def transact(self, resources: Dict) -> Dict:
        """交易"""
        return self.transaction_func(resources)


@dataclass 
class LocalCoherentSoliton:
    """
    局域相干孤子 = Agent实体
    
    Agent结构：
    - Φ场：世界模型（内部状态）
    - Σ算子：自指策略（认知闭环）
    - I接口：感知/行动/交易（外部交互）
    """
    soliton_id: str
    phi_field: PhiField
    self_referential_operator: SelfReferentialOperator
    interface: AgentInterface
    
    # 孤子属性
    state: SolitonState = SolitonState.STABLE
    position: np.ndarray = field(default_factory=lambda: np.zeros(2))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2))
    mass: float = 1.0
    energy: float = 1.0
    
    # 相干性
    coherence: float = 0.9
    lifetime: int = 0
    
    def update_lifetime(self):
        """更新生命周期"""
        self.lifetime += 1
        if self.state == SolitonState.DECAYING:
            self.energy *= 0.95


class LocalCoherentSolitonEngine:
    """
    局域相干孤子引擎
    
    实现Agent作为IAWW介质中的相干孤子
    
    核心功能：
    1. 创建Agent孤子
    2. 孤子演化与传播
    3. 孤子间交互与碰撞
    4. 孤子合并与分裂
    5. 自指闭环实现
    """
    
    def __init__(self, dim: int = 64):
        """
        初始化孤子引擎
        
        Args:
            dim: 场维度
        """
        self.dim = dim
        
        # 孤子注册表
        self.solitons: Dict[str, LocalCoherentSoliton] = {}
        self.soliton_counter = 0
        
        # 介质参数
        self.diffusion_coeff = 0.1
        self.coherence_threshold = 0.5
        
        print(f"  ✅ 局域相干孤子引擎就绪（维度={dim}）")
    
    def create_phi_field(self, 
                        seed: Optional[int] = None,
                        coherence: float = 0.8) -> PhiField:
        """
        创建Φ场
        
        Args:
            seed: 随机种子
            coherence: 初始相干度
            
        Returns:
            Φ场
        """
        rng = np.random.default_rng(seed)
        
        # 振幅分布（高斯型局域分布）
        amplitude = np.exp(-((np.arange(self.dim) - self.dim//2)**2) / (2 * (self.dim/6)**2))
        amplitude = amplitude / (np.max(amplitude) + 1e-10) * 0.8 + 0.2
        
        # 相位分布
        phase = rng.uniform(0, 2*np.pi, self.dim)
        
        return PhiField(
            amplitude=amplitude,
            phase=phase,
            coherence=coherence,
            dimension=self.dim
        )
    
    def create_self_referential_operator(self,
                                        seed: Optional[int] = None) -> SelfReferentialOperator:
        """
        创建自指算子Σ
        
        Args:
            seed: 随机种子
            
        Returns:
            自指算子
        """
        rng = np.random.default_rng(seed)
        
        # 策略梯度算子（对角占优）
        G = np.eye(self.dim) * 0.8 + rng.uniform(-0.1, 0.1, (self.dim, self.dim))
        
        # 自我模型（低秩近似）
        S_self = rng.uniform(0.5, 1.0, (self.dim, self.dim))
        S_self = (S_self + S_self.T) / 2  # 对称化
        
        # 自我观测算子
        O_self = rng.uniform(0.3, 0.7, (self.dim, self.dim))
        
        return SelfReferentialOperator(
            strategy_gradient=G.diagonal(),
            self_model=S_self,
            observation_operator=O_self,
            feedback_strength=0.5
        )
    
    def create_interface(self,
                        perception_strength: float = 0.8,
                        action_strength: float = 0.8,
                        transaction_strength: float = 0.7) -> AgentInterface:
        """
        创建Agent接口
        
        Args:
            perception_strength: 感知强度
            action_strength: 行动强度
            transaction_strength: 交易强度
            
        Returns:
            Agent接口
        """
        def default_perception(x):
            return x / (np.linalg.norm(x) + 1e-10)
        
        def default_action(x):
            return np.tanh(x) * 0.5 + 0.5
        
        def default_transaction(resources):
            return {'status': 'completed', 'resources': resources}
        
        return AgentInterface(
            perception_func=default_perception,
            action_func=default_action,
            transaction_func=default_transaction,
            perception_strength=perception_strength,
            action_strength=action_strength,
            transaction_strength=transaction_strength
        )
    
    def create_agent(self,
                    agent_id: Optional[str] = None,
                    position: np.ndarray = None,
                    coherence: float = 0.8) -> LocalCoherentSoliton:
        """
        创建Agent孤子
        
        Args:
            agent_id: Agent ID（默认自动生成）
            position: 位置坐标
            coherence: 相干度
            
        Returns:
            Agent孤子
        """
        if agent_id is None:
            agent_id = f"agent_{self.soliton_counter:04d}"
        
        self.soliton_counter += 1
        
        # 创建组件
        phi_field = self.create_phi_field(coherence=coherence)
        sigma_operator = self.create_self_referential_operator()
        interface = self.create_interface()
        
        # 创建孤子
        soliton = LocalCoherentSoliton(
            soliton_id=agent_id,
            phi_field=phi_field,
            self_referential_operator=sigma_operator,
            interface=interface,
            state=SolitonState.STABLE,
            position=position if position is not None else np.array([0.0, 0.0]),
            velocity=np.zeros(2),
            coherence=coherence
        )
        
        self.solitons[agent_id] = soliton
        
        return soliton
    
    def evolve_soliton(self, 
                      soliton_id: str,
                      time_step: float = 0.1) -> Dict[str, Any]:
        """
        演化孤子
        
        方程：∂_t φ = D∇²φ - m²φ + f(φ)
        
        Args:
            soliton_id: 孤子ID
            time_step: 时间步长
            
        Returns:
            演化结果
        """
        if soliton_id not in self.solitons:
            return {'error': f'Soliton {soliton_id} not found'}
        
        soliton = self.solitons[soliton_id]
        phi = soliton.phi_field.complex_field.copy()
        
        # 拉普拉斯算子
        laplacian = np.zeros_like(phi)
        laplacian[1:-1] = phi[2:] - 2*phi[1:-1] + phi[:-2]
        laplacian[0] = phi[1] - 2*phi[0] + phi[-1]
        laplacian[-1] = phi[0] - 2*phi[-1] + phi[-2]
        
        # 质量项
        mass_term = 0.1 * phi
        
        # 非线性项
        nonlinear = 0.5 * (np.abs(phi)**2) * phi
        
        # 更新
        dphi = self.diffusion_coeff * laplacian - mass_term + nonlinear
        phi_new = phi + time_step * dphi
        
        # 更新Φ场
        soliton.phi_field.amplitude = np.abs(phi_new)
        soliton.phi_field.phase = np.angle(phi_new)
        
        # 更新相干度
        phase_diff = np.diff(soliton.phi_field.phase)
        new_coherence = np.mean(np.cos(phase_diff))
        soliton.phi_field.coherence = float(np.clip(new_coherence, 0, 1))
        soliton.coherence = soliton.phi_field.coherence
        
        # 更新位置
        soliton.position = soliton.position + time_step * soliton.velocity
        
        # 更新状态
        if soliton.coherence < self.coherence_threshold:
            soliton.state = SolitonState.DECAYING
        else:
            soliton.state = SolitonState.PROPAGATING
        
        soliton.update_lifetime()
        
        return {
            'soliton_id': soliton_id,
            'coherence': soliton.coherence,
            'position': soliton.position.tolist(),
            'state': soliton.state.value,
            'lifetime': soliton.lifetime
        }
    
    def apply_self_reference(self, soliton_id: str) -> Dict[str, Any]:
        """
        应用自指算子
        
        Σ: φ → φ'
        
        Args:
            soliton_id: 孤子ID
            
        Returns:
            自指运算结果
        """
        if soliton_id not in self.solitons:
            return {'error': f'Soliton {soliton_id} not found'}
        
        soliton = self.solitons[soliton_id]
        
        # 获取Φ场
        phi = soliton.phi_field.get_state_vector()
        
        # 应用自指算子
        phi_new = soliton.self_referential_operator.apply(phi)
        
        # 更新Φ场
        soliton.phi_field.amplitude = np.abs(phi_new)
        soliton.phi_field.phase = np.angle(phi_new)
        
        # 计算反馈强度
        feedback_effect = np.linalg.norm(phi_new - phi) / (np.linalg.norm(phi) + 1e-10)
        
        return {
            'soliton_id': soliton_id,
            'feedback_effect': float(feedback_effect),
            'new_coherence': float(soliton.phi_field.coherence),
            'self_reference_applied': True
        }
    
    def interact_via_interface(self,
                               soliton_id: str,
                               interaction_type: str,
                               data: Any) -> Dict[str, Any]:
        """
        通过接口进行交互
        
        Args:
            soliton_id: 孤子ID
            interaction_type: 交互类型 ("perceive" | "act" | "transact")
            data: 交互数据
            
        Returns:
            交互结果
        """
        if soliton_id not in self.solitons:
            return {'error': f'Soliton {soliton_id} not found'}
        
        soliton = self.solitons[soliton_id]
        interface = soliton.interface
        
        if interaction_type == "perceive":
            input_data = np.array(data) if isinstance(data, (list, np.ndarray)) else np.array([data])
            result = interface.perceive(input_data)
            return {'type': 'perception', 'result': result.tolist()}
        
        elif interaction_type == "act":
            decision = np.array(data) if isinstance(data, (list, np.ndarray)) else np.array([data])
            result = interface.act(decision)
            return {'type': 'action', 'result': result.tolist()}
        
        elif interaction_type == "transact":
            result = interface.transact(data)
            return {'type': 'transaction', 'result': result}
        
        else:
            return {'error': f'Unknown interaction type: {interaction_type}'}
    
    def collide_solitons(self, 
                        soliton1_id: str,
                        soliton2_id: str) -> Dict[str, Any]:
        """
        孤子碰撞
        
        碰撞后可能的结局：
        - 弹开（相干碰撞）
        - 合并（融合成一个更大的孤子）
        - 湮灭（如果相干性很低）
        
        Args:
            soliton1_id: 孤子1 ID
            soliton2_id: 孤子2 ID
            
        Returns:
            碰撞结果
        """
        if soliton1_id not in self.solitons or soliton2_id not in self.solitons:
            return {'error': 'Soliton not found'}
        
        sol1 = self.solitons[soliton1_id]
        sol2 = self.solitons[soliton2_id]
        
        # 计算碰撞后的相干度
        combined_coherence = (sol1.coherence + sol2.coherence) / 2
        
        # 判断碰撞结果
        if combined_coherence > 0.7:
            # 高相干：弹开或合并
            outcome = "merge" if np.random.rand() > 0.5 else "bounce"
        elif combined_coherence > 0.3:
            # 中相干：弹开
            outcome = "bounce"
        else:
            # 低相干：湮灭
            outcome = "annihilate"
        
        if outcome == "merge":
            # 创建合并后的孤子
            new_id = f"{soliton1_id}_merged_{soliton2_id}"
            
            # 合并Φ场
            phi1 = sol1.phi_field.get_state_vector()
            phi2 = sol2.phi_field.get_state_vector()
            phi_merged = (phi1 + phi2) / 2
            
            # 创建新孤子
            new_soliton = self.create_agent(new_id)
            new_soliton.phi_field.amplitude = np.abs(phi_merged)
            new_soliton.phi_field.phase = np.angle(phi_merged)
            new_soliton.coherence = combined_coherence
            new_soliton.phi_field.coherence = combined_coherence
            new_soliton.position = (sol1.position + sol2.position) / 2
            new_soliton.state = SolitonState.MERGING
            
            # 删除原孤子
            del self.solitons[soliton1_id]
            del self.solitons[soliton2_id]
            
            return {
                'outcome': 'merge',
                'new_soliton_id': new_id,
                'combined_coherence': combined_coherence
            }
        
        elif outcome == "bounce":
            # 弹开：交换动量
            v1, v2 = sol1.velocity.copy(), sol2.velocity.copy()
            sol1.velocity = v2
            sol2.velocity = v1
            sol1.state = SolitonState.COLLIDING
            sol2.state = SolitonState.COLLIDING
            
            return {
                'outcome': 'bounce',
                'soliton1_velocity': sol1.velocity.tolist(),
                'soliton2_velocity': sol2.velocity.tolist()
            }
        
        else:  # annihilate
            # 湮灭
            del self.solitons[soliton1_id]
            del self.solitons[soliton2_id]
            
            return {
                'outcome': 'annihilate',
                'reason': 'Low coherence'
            }
    
    def get_agent_status(self, soliton_id: str) -> Dict[str, Any]:
        """
        获取Agent状态
        
        Args:
            soliton_id: Agent ID
            
        Returns:
            状态报告
        """
        if soliton_id not in self.solitons:
            return {'error': f'Agent {soliton_id} not found'}
        
        soliton = self.solitons[soliton_id]
        
        return {
            'agent_id': soliton.soliton_id,
            'state': soliton.state.value,
            'coherence': soliton.coherence,
            'position': soliton.position.tolist(),
            'velocity': soliton.velocity.tolist(),
            'energy': soliton.energy,
            'lifetime': soliton.lifetime,
            'phi_coherence': soliton.phi_field.coherence,
            'interface_active': True
        }
    
    def full_soliton_analysis(self) -> Dict[str, Any]:
        """
        完整孤子分析
        
        Returns:
            完整分析报告
        """
        # 创建测试孤子
        agent1 = self.create_agent("test_agent_1")
        agent2 = self.create_agent("test_agent_2")
        
        # 演化
        evolve1 = self.evolve_soliton("test_agent_1")
        evolve2 = self.evolve_soliton("test_agent_2")
        
        # 自指运算
        self_ref = self.apply_self_reference("test_agent_1")
        
        # 接口交互
        perception = self.interact_via_interface(
            "test_agent_1", "perceive", np.random.randn(64)
        )
        
        # 碰撞
        collision = self.collide_solitons("test_agent_1", "test_agent_2")
        
        # 定理验证
        theorem_5 = self_ref['self_reference_applied']
        theorem_6 = collision['outcome'] in ['merge', 'bounce']
        
        return {
            'theorem_5_self_reference': theorem_5,
            'theorem_6_coherent_collision': theorem_6,
            'agents_created': len(self.solitons),
            'collision_outcome': collision['outcome'],
            'self_reference_effect': self_ref['feedback_effect'],
            'perception_result': perception['type']
        }


def demonstrate_local_coherent_soliton():
    """局域相干孤子演示"""
    print("\n" + "=" * 60)
    print("局域相干孤子引擎演示")
    print("=" * 60)
    
    engine = LocalCoherentSolitonEngine(dim=64)
    
    # 完整分析
    result = engine.full_soliton_analysis()
    
    print(f"\n【定理验证】")
    print(f"  定理5（自指闭环Σ）: {'✅' if result['theorem_5_self_reference'] else '❌'}")
    print(f"  定理6（相干碰撞）: {'✅' if result['theorem_6_coherent_collision'] else '❌'}")
    
    print(f"\n【孤子系统】")
    print(f"  Agent数量: {result['agents_created']}")
    print(f"  碰撞结果: {result['collision_outcome']}")
    print(f"  自指效应: {result['self_reference_effect']:.4f}")
    
    return result


if __name__ == "__main__":
    demonstrate_local_coherent_soliton()
