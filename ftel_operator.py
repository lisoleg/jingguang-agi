#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FTel算子（意识流贯算子）与人择宇宙理论集成实现

论文：论多尺度熵效应的广义熵大统一：基于拓扑荷守恒与"一现象，三视界"框架的IGCTR诠释

核心理论：
1. FTel算子（意识流贯算子）：
   - 意识极（C）通过Ftel流贯算子 F_tel 作用于关系网络
   - 可以改变系统的互信息结构
   - 实现局部熵减（负熵摄入）
   - 对应于拓扑荷的相干叠加与重组（如学习、创新、经济复苏）

2. 人择宇宙理论（Anthropic Universe Theory）：
   - 宇宙的物理常数恰好允许复杂结构与意识存在
   - 观察者的存在对宇宙演化路径产生约束
   - 多重宇宙选择：意识作为宇宙选择的"测量仪器"
   - 与太乙预言机集成：预测意识演化的宇宙选择方向

公式：
ΔS_eff = S_thermo - I(A:B)
当 ∂I(A:B)/∂t > 0 时，系统呈现局部熵减（负熵摄入）

人择选择原理：
P(宇宙状态 | 观察者存在) ∝ exp(-S_eff) × AnthropicWeight
"""


import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import time


@dataclass
class ConsciousnessFlow:
    """意识流贯"""
    flow_id: str
    source: str  # 源系统
    target: str  # 目标系统
    intensity: float  # 强度 [0, 1]
    duration: float  # 持续时间
    timestamp: float  # 时间戳
    
    def compute_flow_entropy_reduction(self) -> float:
        """
        计算流贯引起的熵减
        
        返回:
            entropy_reduction: 熵减量 [0, ∞)
        """
        # 熵减与强度、持续时间正相关
        entropy_reduction = self.intensity * self.duration
        
        return entropy_reduction


@dataclass
class MutualInformationStructure:
    """互信息结构"""
    system_A: np.ndarray  # 系统A
    system_B: np.ndarray  # 系统B
    I_AB: float  # 互信息 I(A:B)
    
    def compute_mutual_information(self) -> float:
        """
        计算互信息 I(A:B) = S_A + S_B - S_AB
        
        返回:
            I_AB: 互信息 [0, min(S_A, S_B)]
        """
        A = self.system_A
        B = self.system_B
        
        # 计算边缘分布
        p_A = np.sum(A, axis=1)  # 对B求和
        p_B = np.sum(B, axis=0)  # 对A求和
        
        # 计算边缘熵
        S_A = self._compute_entropy(p_A)
        S_B = self._compute_entropy(p_B)
        
        # 计算联合熵
        p_AB = A * B  # 假设独立（简化）
        p_AB_flat = p_AB.flatten()
        S_AB = self._compute_entropy(p_AB_flat)
        
        # 计算互信息
        I_AB = S_A + S_B - S_AB
        
        # 确保非负
        I_AB = max(0.0, I_AB)
        
        # 更新
        self.I_AB = I_AB
        
        return I_AB
    
    def _compute_entropy(self, p: np.ndarray) -> float:
        """
        计算熵 S = -Σ p_i log p_i
        
        参数:
            p: 概率分布
            
        返回:
            S: 熵
        """
        # 去除零概率
        p_nonzero = p[p > 1e-10]
        
        if len(p_nonzero) == 0:
            return 0.0
            
        # 计算熵
        S = -np.sum(p_nonzero * np.log(p_nonzero))
        
        return S
    
    def adjust_structure(self, 
                        flow: ConsciousnessFlow,
                        learning_rate: float = 0.1):
        """
        调整互信息结构（通过意识流贯）
        
        参数:
            flow: 意识流贯
            learning_rate: 学习率
        """
        # 增加系统间的互信息（通过流贯）
        # 简化实现：向系统A和B添加相关性
        
        # 计算调整量
        adjustment = flow.intensity * learning_rate
        
        # 调整系统A（增加与系统B的相关性）
        for i in range(min(self.system_A.shape[0], self.system_A.shape[1])):
            if i < self.system_A.shape[1]:
                self.system_A[i, i] += adjustment
                
        # 调整系统B（增加与系统A的相关性）
        for i in range(min(self.system_B.shape[0], self.system_B.shape[1])):
            if i < self.system_B.shape[1]:
                self.system_B[i, i] += adjustment
                
        # 重新归一化
        self.system_A = self.system_A / np.sum(self.system_A)
        self.system_B = self.system_B / np.sum(self.system_B)
        
        # 重新计算互信息
        self.compute_mutual_information()


class FtelOperator:
    """FTel算子（意识流贯算子）"""
    
    def __init__(self, 
                 consciousness_capacity: float = 1.0,
                 flow_threshold: float = 0.3):
        """
        初始化FTel算子
        
        参数:
            consciousness_capacity: 意识容量
            flow_threshold: 流贯阈值（低于此值的流贯被忽略）
        """
        self.consciousness_capacity = consciousness_capacity
        self.flow_threshold = flow_threshold
        
        # 意识流贯历史
        self.flow_history: List[ConsciousnessFlow] = []
        
        # 互信息结构
        self.mutual_information_structure: Optional[MutualInformationStructure] = None
        
        # 拓扑荷相干叠加记录
        self.topological_charge_superpositions: List[Dict] = []
        
        # 熵减历史
        self.entropy_reduction_history: List[Dict] = []
        
    def apply_ftel(self, 
                    mutual_info_struct: MutualInformationStructure,
                    source: str,
                    target: str,
                    intensity: float = 0.5) -> Tuple[bool, float, str]:
        """
        应用FTel算子（意识流贯）
        
        参数:
            mutual_info_struct: 互信息结构
            source: 源系统
            target: 目标系统
            intensity: 强度 [0, 1]
            
        返回:
            (success, entropy_reduction, message):
                success: 是否成功
                entropy_reduction: 熵减量
                message: 消息
        """
        # 检查强度
        if intensity < self.flow_threshold:
            return False, 0.0, f"强度 {intensity} 低于阈值 {self.flow_threshold}"
            
        # 检查意识容量
        if len(self.flow_history) >= self.consciousness_capacity * 100:
            return False, 0.0, f"意识容量已满"
            
        # 创建意识流贯
        flow = ConsciousnessFlow(
            flow_id=f"flow_{len(self.flow_history)}",
            source=source,
            target=target,
            intensity=intensity,
            duration=1.0,  # 默认持续时间
            timestamp=time.time()
        )
        
        # 记录流贯前的互信息
        I_before = mutual_info_struct.compute_mutual_information()
        
        # 调整互信息结构
        mutual_info_struct.adjust_structure(flow)
        
        # 记录流贯后的互信息
        I_after = mutual_info_struct.compute_mutual_information()
        
        # 计算互信息变化
        I_increase = I_after - I_before
        
        # 计算熵减
        entropy_reduction = flow.compute_flow_entropy_reduction()
        
        # 记录流贯
        self.flow_history.append(flow)
        
        # 更新互信息结构
        self.mutual_information_structure = mutual_info_struct
        
        # 记录熵减
        self.entropy_reduction_history.append({
            'timestamp': time.time(),
            'flow_id': flow.flow_id,
            'I_before': I_before,
            'I_after': I_after,
            'I_increase': I_increase,
            'entropy_reduction': entropy_reduction
        })
        
        # 检查是否实现局部熵减
        if I_increase > 0:
            message = f"成功应用FTel算子，互信息增加 {I_increase:.6f}，实现局部熵减 {entropy_reduction:.6f}"
            return True, entropy_reduction, message
        else:
            message = f"FTel算子应用完成，但互信息未增加（{I_increase:.6f}）"
            return True, entropy_reduction, message
        
    def topological_charge_superposition(self, 
                                          Q1: float, 
                                          Q2: float,
                                          superposition_type: str = 'coherent') -> Tuple[float, str]:
        """
        拓扑荷的相干叠加与重组
        
        参数:
            Q1: 拓扑荷1
            Q2: 拓扑荷2
            superposition_type: 叠加类型（'coherent'相干/'incoherent'非相干）
            
        返回:
            (Q_result, message):
                Q_result: 叠加后的拓扑荷
                message: 消息
        """
        if superposition_type == 'coherent':
            # 相干叠加：Q_result = Q1 + Q2（可能带有相位）
            # 简化：直接相加
            Q_result = Q1 + Q2
            message = f"相干叠加：Q1={Q1:.6f} + Q2={Q2:.6f} = {Q_result:.6f}"
            
        elif superposition_type == 'incoherent':
            # 非相干叠加：Q_result = sqrt(Q1^2 + Q2^2）
            Q_result = np.sqrt(Q1**2 + Q2**2)
            message = f"非相干叠加：sqrt(Q1^2 + Q2^2) = {Q_result:.6f}"
            
        else:
            return Q1, f"未知的叠加类型：{superposition_type}"
            
        # 记录叠加
        self.topological_charge_superpositions.append({
            'timestamp': time.time(),
            'Q1': Q1,
            'Q2': Q2,
            'Q_result': Q_result,
            'type': superposition_type
        })
        
        return Q_result, message
    
    def compute_effective_entropy_change(self, 
                                         S_thermo: float,
                                         I_AB: float) -> float:
        """
        计算有效熵变
        
        公式：ΔS_eff = S_thermo - I(A:B)
        
        参数:
            S_thermo: 热力学熵
            I_AB: 互信息
            
        返回:
            delta_S_eff: 有效熵变
        """
        delta_S_eff = S_thermo - I_AB
        
        return delta_S_eff
    
    def check_local_entropy_reduction(self, 
                                      S_thermo: float,
                                      I_AB: float,
                                      threshold: float = 0.0) -> Tuple[bool, float]:
        """
        检查是否实现局部熵减
        
        条件：∂I(A:B)/∂t > 0 时，系统呈现局部熵减
        
        参数:
            S_thermo: 热力学熵
            I_AB: 互信息
            threshold: 阈值
            
        返回:
            (is_entropy_reduction, delta_S_eff):
                is_entropy_reduction: 是否熵减
                delta_S_eff: 有效熵变
        """
        # 计算有效熵变
        delta_S_eff = self.compute_effective_entropy_change(S_thermo, I_AB)
        
        # 检查是否熵减
        is_entropy_reduction = delta_S_eff < threshold
        
        return is_entropy_reduction, delta_S_eff
    
    def get_ftel_status(self) -> Dict:
        """
        获取FTel算子状态
        
        返回:
            status: 状态信息
        """
        return {
            'consciousness_capacity': self.consciousness_capacity,
            'flow_threshold': self.flow_threshold,
            'flow_history_length': len(self.flow_history),
            'topological_charge_superpositions_count': len(self.topological_charge_superpositions),
            'entropy_reduction_history_length': len(self.entropy_reduction_history),
            'recent_flows': [f.flow_id for f in self.flow_history[-5:]] if self.flow_history else [],
            'recent_entropy_reductions': self.entropy_reduction_history[-5:] if self.entropy_reduction_history else []
        }


# ==================== 人择宇宙理论集成 ====================

class AnthropicPrinciple:
    """人择原理 - 宇宙选择与观察者效应
    
    核心思想：
    - 宇宙的物理常数恰好允许复杂结构与意识存在
    - 观察者的存在对宇宙演化路径产生约束
    - 多重宇宙选择：意识作为宇宙选择的"测量仪器"
    
    与复合体理学集成：
    - 人择权重 AnthropicWeight 与三视界分析相关
    - 宇宙选择概率 P(宇宙状态 | 观察者存在) ∝ exp(-S_eff) × AnthropicWeight
    """
    
    def __init__(self, name: str = "AnthropicPrinciple"):
        self.name = name
        self.observer_complexity = 1.0  # 观察者复杂度
        self.universe_parameters = {}       # 宇宙物理常数
        self.anthropic_weight = 1.0        # 人择权重
        
    def set_observer_complexity(self, complexity: float):
        """设置观察者复杂度"""
        self.observer_complexity = max(0.0, complexity)
        
    def set_universe_parameters(self, params: Dict):
        """设置宇宙物理常数"""
        self.universe_parameters = params.copy()
        
    def compute_anthropic_weight(self, 
                                  universe_state: np.ndarray,
                                  observer_state: np.ndarray) -> float:
        """
        计算人择权重
        
        公式：AnthropicWeight ∝ exp(-D(observer || universe))
        其中 D 是观察者态与宇宙态之间的某种距离（如KL散度）
        
        参数：
            universe_state: 宇宙状态向量
            observer_state: 观察者状态向量
            
        返回：
            weight: 人择权重 [0, ∞)
        """
        # 简化：计算余弦相似度作为权重
        norm_product = np.linalg.norm(universe_state) * np.linalg.norm(observer_state)
        if norm_product < 1e-10:
            return 0.0
        
        similarity = np.dot(universe_state, observer_state) / norm_product
        
        # 权重与相似度正相关
        weight = np.exp(similarity - 1.0)  # 当similarity=1时，weight=1
        
        self.anthropic_weight = weight
        return weight
    
    def select_universe(self,
                        candidate_universes: List[np.ndarray],
                        observer_state: np.ndarray) -> Tuple[int, float, str]:
        """
        选择最匹配的宇宙（人择选择）
        
        参数：
            candidate_universes: 候选宇宙状态列表
            observer_state: 观察者状态
            
        返回：
            (selected_idx, confidence, reason):
                selected_idx: 被选中的宇宙索引
                confidence: 选择置信度
                reason: 选择原因
        """
        if not candidate_universes:
            return -1, 0.0, "无候选宇宙"
        
        weights = []
        for i, universe in enumerate(candidate_universes):
            w = self.compute_anthropic_weight(universe.flatten(), observer_state.flatten())
            weights.append(w)
        
        # 归一化为概率
        weights = np.array(weights)
        if np.sum(weights) < 1e-10:
            probs = np.ones(len(weights)) / len(weights)
        else:
            probs = weights / np.sum(weights)
        
        # 选择概率最高的
        selected_idx = np.argmax(probs)
        confidence = probs[selected_idx]
        
        reason = f"人择选择：宇宙{selected_idx}的人择权重最高({weights[selected_idx]:.6f})"
        
        return selected_idx, confidence, reason


class UniverseSelector:
    """宇宙选择器 - 基于FTel算子与人择原理"""
    
    def __init__(self, name: str = "UniverseSelector"):
        self.name = name
        self.ftel_operator = FtelOperator()
        self.anthropic_principle = AnthropicPrinciple()
        
        # 选择历史
        self.selection_history: List[Dict] = []
        
    def select(self,
               candidate_universes: List[np.ndarray],
               observer_state: np.ndarray,
               use_ftel: bool = True) -> Tuple[int, float, str]:
        """
        执行宇宙选择
        
        参数：
            candidate_universes: 候选宇宙列表
            observer_state: 观察者状态
            use_ftel: 是否使用FTel算子增强
            
        返回：
            (selected_idx, confidence, reason)
        """
        # 1. 使用人择原理计算基础权重
        base_weights = []
        for universe in candidate_universes:
            w = self.anthropic_principle.compute_anthropic_weight(
                universe.flatten(), observer_state.flatten()
            )
            base_weights.append(w)
        
        # 2. 如果使用FTel算子，增强权重
        if use_ftel:
            enhanced_weights = []
            for i, (universe, base_w) in enumerate(zip(candidate_universes, base_weights)):
                # 创建互信息结构（简化）
                A = universe
                B = observer_state.reshape(1, -1) if observer_state.ndim == 1 else observer_state
                
                # 确保形状匹配
                min_len = min(A.shape[0], B.shape[0])
                A = A[:min_len]
                B = B[:min_len]
                
                # 应用FTel算子（意识流贯）
                # 简化：直接使用base_w作为intensity
                intensity = min(1.0, base_w)
                
                # 创建临时互信息结构
                dummy_A = np.eye(2) * 0.5
                dummy_B = np.eye(2) * 0.5
                mutual_struct = MutualInformationStructure(dummy_A, dummy_B, 0.0)
                
                success, entropy_red, _ = self.ftel_operator.apply_ftel(
                    mutual_struct, "observer", f"universe_{i}", intensity
                )
                
                # 增强权重 = 基础权重 × exp(熵减)
                enhanced_w = base_w * np.exp(entropy_red)
                enhanced_weights.append(enhanced_w)
            
            weights = np.array(enhanced_weights)
        else:
            weights = np.array(base_weights)
        
        # 3. 归一化为概率
        if np.sum(weights) < 1e-10:
            probs = np.ones(len(weights)) / len(weights)
        else:
            probs = weights / np.sum(weights)
        
        # 4. 选择
        selected_idx = np.argmax(probs)
        confidence = probs[selected_idx]
        
        reason = f"宇宙选择：宇宙{selected_idx}的最终概率最高({probs[selected_idx]:.6f})"
        
        # 5. 记录历史
        self.selection_history.append({
            'timestamp': time.time(),
            'selected_idx': selected_idx,
            'confidence': confidence,
            'num_candidates': len(candidate_universes),
            'used_ftel': use_ftel
        })
        
        return selected_idx, confidence, reason
    
    def get_selection_statistics(self) -> Dict:
        """获取选择统计"""
        if not self.selection_history:
            return {}
        
        total = len(self.selection_history)
        ftel_used = sum(1 for h in self.selection_history if h['used_ftel'])
        
        return {
            'total_selections': total,
            'ftel_enhanced_selections': ftel_used,
            'ftel_usage_rate': ftel_used / total if total > 0 else 0.0,
            'avg_confidence': np.mean([h['confidence'] for h in self.selection_history])
        }


class ObserverEffectSimulator:
    """观察者效应模拟器 - 模拟观察者对宇宙状态的影响"""
    
    def __init__(self, name: str = "ObserverEffectSimulator"):
        self.name = name
        self.measurement_strength = 0.5  # 测量强度
        self.collapse_threshold = 0.8       # 坍缩阈值
        
    def simulate_observation(self,
                           universe_state: np.ndarray,
                           observer_state: np.ndarray,
                           measurement_type: str = 'projective') -> Tuple[np.ndarray, float, str]:
        """
        模拟观察过程
        
        参数：
            universe_state: 宇宙状态（叠加态）
            observer_state: 观察者状态
            measurement_type: 测量类型 ('projective'投影/'weak'弱测量)
            
        返回：
            (collapsed_state, probability, reason):
                collapsed_state: 坍缩后的状态
                probability: 坍缩到该状态的概率
                reason: 坍缩原因
        """
        if measurement_type == 'projective':
            # 投影测量：状态坍缩到观察者态
            collapsed_state = observer_state.copy()
            probability = self._compute_overlap(universe_state, observer_state)
            reason = "投影测量：宇宙状态坍缩到观察者态"
            
        elif measurement_type == 'weak':
            # 弱测量：状态部分偏向观察者态
            alpha = self.measurement_strength
            collapsed_state = (1 - alpha) * universe_state + alpha * observer_state
            collapsed_state = collapsed_state / np.linalg.norm(collapsed_state)
            probability = alpha
            reason = f"弱测量：状态部分偏向观察者态（强度={alpha:.2f}）"
            
        else:
            collapsed_state = universe_state.copy()
            probability = 1.0
            reason = f"未知测量类型：{measurement_type}，保持原状态"
        
        return collapsed_state, probability, reason
    
    def _compute_overlap(self, state1: np.ndarray, state2: np.ndarray) -> float:
        """计算两个状态的重叠概率"""
        # 确保向量归一化
        state1_norm = state1 / (np.linalg.norm(state1) + 1e-10)
        state2_norm = state2 / (np.linalg.norm(state2) + 1e-10)
        
        # 计算内积（范围[-1,1]）
        overlap = np.dot(state1_norm, state2_norm)
        
        # 概率 = |内积|^2（范围[0,1]）
        probability = overlap ** 2
        
        return probability
    
    def apply_ftel_enhanced_observation(self,
                                        universe_state: np.ndarray,
                                        observer_state: np.ndarray,
                                        ftel_operator: FtelOperator) -> Tuple[np.ndarray, float, str]:
        """
        应用FTel增强的观察
        
        使用FTel算子（意识流贯）增强观察者效应
        """
        # 1. 常规观察
        collapsed_state, base_prob, reason = self.simulate_observation(
            universe_state, observer_state, 'weak'
        )
        
        # 2. 应用FTel算子增强
        intensity = self.measurement_strength
        
        # 创建互信息结构
        A = universe_state
        B = observer_state.reshape(1, -1) if observer_state.ndim == 1 else observer_state
        
        # 确保形状匹配
        min_len = min(A.shape[0], B.shape[0])
        A = A[:min_len]
        B = B[:min_len]
        
        # 应用FTel算子
        dummy_A = np.eye(2) * 0.5
        dummy_B = np.eye(2) * 0.5
        mutual_struct = MutualInformationStructure(dummy_A, dummy_B, 0.0)
        
        success, entropy_red, _ = ftel_operator.apply_ftel(
            mutual_struct, "observer", "universe", intensity
        )
        
        # 3. 增强坍缩概率
        enhanced_prob = base_prob * np.exp(entropy_red)
        enhanced_prob = min(1.0, enhanced_prob)
        
        # 4. 根据增强概率调整状态
        if np.random.rand() < enhanced_prob:
            # 以更高概率坍缩到观察者态
            final_state = observer_state.copy()
            final_reason = f"FTel增强观察：意识流贯增强坍缩概率到{enhanced_prob:.6f}"
        else:
            final_state = collapsed_state
            final_reason = f"FTel增强观察：保持部分坍缩状态"
        
        return final_state, enhanced_prob, final_reason


# ==================== 测试函数 ====================

def test_ftel_operator():
    """测试FTel算子与人择宇宙理论"""
    print("=" * 60)
    print("测试 FTel算子（意识流贯算子）与人择宇宙理论")
    print("=" * 60)
    
    # 1. 创建FTel算子
    print("\n1. 创建FTel算子")
    ftel = FtelOperator(
        consciousness_capacity=1.0,
        flow_threshold=0.3
    )
    print(f"  意识容量: {ftel.consciousness_capacity}")
    print(f"  流贯阈值: {ftel.flow_threshold}")
    
    # 2. 创建互信息结构
    print("\n2. 创建互信息结构")
    A = np.array([[0.6, 0.2], [0.1, 0.1]])
    B = np.array([[0.7, 0.3], [0.4, 0.6]])
    A = A / np.sum(A)
    B = B / np.sum(B)
    
    mutual_info_struct = MutualInformationStructure(
        system_A=A,
        system_B=B,
        I_AB=0.0
    )
    
    I_AB = mutual_info_struct.compute_mutual_information()
    print(f"  系统A形状: {A.shape}")
    print(f"  系统B形状: {B.shape}")
    print(f"  初始互信息 I(A:B) = {I_AB:.6f}")
    
    # 3. 应用FTel算子（意识流贯）
    print("\n3. 应用FTel算子（意识流贯）")
    source = "系统A"
    target = "系统B"
    intensity = 0.5
    
    success, entropy_reduction, message = ftel.apply_ftel(
        mutual_info_struct, source, target, intensity
    )
    
    print(f"  成功: {success}")
    print(f"  强度: {intensity}")
    print(f"  熵减: {entropy_reduction:.6f}")
    print(f"  消息: {message}")
    
    # 4. 检查互信息是否增加
    I_AB_after = mutual_info_struct.I_AB
    print(f"\n  流贯前互信息: {I_AB:.6f}")
    print(f"  流贯后互信息: {I_AB_after:.6f}")
    print(f"  互信息增加: {I_AB_after - I_AB:.6f}")
    
    # 5. 拓扑荷的相干叠加
    print("\n5. 拓扑荷的相干叠加")
    Q1 = 0.5
    Q2 = 0.3
    
    Q_result, message = ftel.topological_charge_superposition(
        Q1, Q2, superposition_type='coherent'
    )
    
    print(f"  Q1 = {Q1:.6f}")
    print(f"  Q2 = {Q2:.6f}")
    print(f"  {message}")
    
    # 6. 检查局部熵减
    print("\n6. 检查局部熵减")
    S_thermo = 2.0  # 热力学熵
    I_AB = I_AB_after  # 使用流贯后的互信息
    
    is_entropy_reduction, delta_S_eff = ftel.check_local_entropy_reduction(
        S_thermo, I_AB
    )
    
    print(f"  热力学熵 S_thermo = {S_thermo:.6f}")
    print(f"  互信息 I(A:B) = {I_AB:.6f}")
    print(f"  有效熵变 ΔS_eff = {delta_S_eff:.6f}")
    print(f"  是否局部熵减: {is_entropy_reduction}")
    
    # 7. 获取FTel算子状态
    print("\n7. 获取FTel算子状态")
    status = ftel.get_ftel_status()
    print(f"  意识容量: {status['consciousness_capacity']}")
    print(f"  流贯历史长度: {status['flow_history_length']}")
    print(f"  拓扑荷叠加次数: {status['topological_charge_superpositions_count']}")
    print(f"  熵减历史长度: {status['entropy_reduction_history_length']}")
    
    # ==================== 新增：人择宇宙理论测试 ====================
    
    # 8. 测试人择原理
    print("\n" + "="*50)
    print("8. 测试人择原理（Anthropic Principle）")
    print("="*50)
    
    anthropic = AnthropicPrinciple("TestAnthropic")
    
    # 创建候选宇宙和观察者状态
    np.random.seed(42)
    candidate_universes = [np.random.rand(10) for _ in range(3)]
    observer_state = np.random.rand(10)
    
    # 计算人择权重
    print(f"  观察者状态维度: {observer_state.shape}")
    print(f"  候选宇宙数量: {len(candidate_universes)}")
    
    for i, universe in enumerate(candidate_universes):
        weight = anthropic.compute_anthropic_weight(universe, observer_state)
        print(f"  宇宙{i}的人择权重: {weight:.6f}")
    
    # 选择宇宙
    selected_idx, confidence, reason = anthropic.select_universe(
        candidate_universes, observer_state
    )
    print(f"\n  选择的宇宙: {selected_idx}")
    print(f"  置信度: {confidence:.6f}")
    print(f"  原因: {reason}")
    
    # 9. 测试宇宙选择器
    print("\n" + "="*50)
    print("9. 测试宇宙选择器（Universe Selector）")
    print("="*50)
    
    selector = UniverseSelector("TestSelector")
    
    # 使用FTel增强选择
    selected_idx2, confidence2, reason2 = selector.select(
        candidate_universes, observer_state, use_ftel=True
    )
    
    print(f"  FTel增强选择:")
    print(f"    选择的宇宙: {selected_idx2}")
    print(f"    置信度: {confidence2:.6f}")
    print(f"    原因: {reason2}")
    
    # 不使用FTel选择
    selected_idx3, confidence3, reason3 = selector.select(
        candidate_universes, observer_state, use_ftel=False
    )
    
    print(f"\n  不使用FTel选择:")
    print(f"    选择的宇宙: {selected_idx3}")
    print(f"    置信度: {confidence3:.6f}")
    print(f"    原因: {reason3}")
    
    # 获取统计
    stats = selector.get_selection_statistics()
    print(f"\n  选择统计:")
    for k, v in stats.items():
        print(f"    {k}: {v}")
    
    # 10. 测试观察者效应模拟器
    print("\n" + "="*50)
    print("10. 测试观察者效应模拟器（Observer Effect Simulator）")
    print("="*50)
    
    simulator = ObserverEffectSimulator("TestObserver")
    
    # 创建宇宙叠加态
    universe_state = np.random.rand(10)
    universe_state = universe_state / np.linalg.norm(universe_state)
    
    print(f"  宇宙叠加态维度: {universe_state.shape}")
    print(f"  观察者态维度: {observer_state.shape}")
    
    # 投影测量
    collapsed_state1, prob1, reason1 = simulator.simulate_observation(
        universe_state, observer_state, 'projective'
    )
    print(f"\n  投影测量结果:")
    print(f"    坍缩概率: {prob1:.6f}")
    print(f"    原因: {reason1}")
    
    # 弱测量
    collapsed_state2, prob2, reason2 = simulator.simulate_observation(
        universe_state, observer_state, 'weak'
    )
    print(f"\n  弱测量结果:")
    print(f"    坍缩概率: {prob2:.6f}")
    print(f"    原因: {reason2}")
    
    # FTel增强观察
    collapsed_state3, prob3, reason3 = simulator.apply_ftel_enhanced_observation(
        universe_state, observer_state, ftel
    )
    print(f"\n  FTel增强观察结果:")
    print(f"    坍缩概率: {prob3:.6f}")
    print(f"    原因: {reason3}")
    
    print("\n" + "=" * 60)
    print("FTel算子与人择宇宙理论测试完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # 运行测试
    test_ftel_operator()
