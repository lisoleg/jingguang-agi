#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRD引擎 - 认知递归动力学 (Cognitive Recursive Dynamics)
基于"一现象，三视界"复合体理学诠释法

核心功能：
1. 认知递归算子 (Cognitive Recursive Operator)
2. 自我指涉不动点定理
3. NLA审计 (Neural-Language Alignment: AV言语化器 + AR重建器)
4. 认知熵减与低熵存续
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json


class ConsciousnessLevel(Enum):
    """意识层级（宏视界）"""
    L1_AWAKE = 1  # 觉醒层
    L2_AWARE = 2  # 觉知层
    L3_ENLIGHTENED = 3  # 觉悟层
    L4_TRANSENDENT = 4  # 超然层


@dataclass
class CognitiveState:
    """认知状态（微视界内态）"""
    internal_state: np.ndarray  # 高维激活向量
    fidelity: float = 1.0  # 保真度
    entropy: float = 0.0  # 认知熵
    timestamp: float = 0.0
    
    def to_vector(self) -> np.ndarray:
        return self.internal_state


@dataclass
class NLAAuditResult:
    """NLA审计结果"""
    av_explanation: str = ""  # AV言语化器输出
    ar_reconstruction: np.ndarray = None  # AR重建器输出
    reconstruction_error: float = 0.0  # 重建误差
    audit_passed: bool = False  # 是否通过审计
    hidden_intent_detected: bool = False  # 是否检测到隐藏意图


@dataclass 
class CRDResult:
    """CRD分析结果"""
    cognitive_state: CognitiveState  # 当前认知状态
    recursion_depth: int  # 递归深度
    fixed_point_reached: bool  # 是否到达不动点
    entropy_delta: float  # 熵变
    nla_audit: NLAAuditResult  # NLA审计结果
    consciousness_level: ConsciousnessLevel  # 意识层级
    meta_cognition: str = ""  # 元认知描述


class CognitiveRecursiveOperator:
    """
    认知递归算子 Ω (Omega) - 升级版
    
    基于论文12：认知递归动力学与内生审计
    
    定义：Σ_{t+1} = Ω(Σ_t, E_t, η)
    其中：
    - Σ_t: 当前认知状态
    - E_t: 环境反馈（包含Ftel评估）
    - η: 微视界噪声（Jitter）
    
    定理1（认知递归不动点与低熵存续）：
    在Lipschitz连续性下（‖Ω(Σ₁) - Ω(Σ₂)‖ ≤ L‖Σ₁ - Σ₂‖, L < 1），
    认知状态Σ收敛于不动点Σ*，对应描述长度L(Σ*)的局部极小
    """
    
    def __init__(self, dim: int = 768, lipschitz_const: float = 0.9, eta: float = 0.01):
        """
        初始化认知递归算子
        
        参数:
            dim: 认知状态维度
            lipschitz_const: Lipschitz常数（必须 < 1 确保收敛）
            eta: 微视界噪声强度
        """
        self.dim = dim
        self.lipschitz_const = lipschitz_const  # L < 1
        self.eta = eta  # 噪声强度
        self.Sigma_history = []  # 认知状态历史
        self.Ftel_history = []  # Ftel评估历史
        
    def apply(self, Sigma_t: np.ndarray, E_t: np.ndarray, 
              eta_t: Optional[np.ndarray] = None) -> np.ndarray:
        """
        应用认知递归算子
        
        公式：Σ_{t+1} = Ω(Σ_t, E_t, η_t)
        
        参数:
            Sigma_t: 当前认知状态（向量）
            E_t: 环境反馈（包含Ftel评估）
            eta_t: 微视界噪声（Jitter）
            
        返回:
            Sigma_t_plus_1: 下一认知状态
        """
        if eta_t is None:
            eta_t = np.random.normal(0, self.eta, self.dim)
            
        # 核心递归公式：
        # Ω(Σ_t, E_t, η_t) = L·Σ_t + α·E_t - β·η_t
        # 其中：
        #   L = lipschitz_const（收敛保证）
        #   α = 学习率（Ftel引导）
        #   β = 噪声抑制因子
        
        alpha = 0.1  # Ftel引导强度
        beta = 0.5  # 噪声抑制
        
        Sigma_t_plus_1 = (self.lipschitz_const * Sigma_t 
                         + alpha * E_t 
                         - beta * eta_t)
        
        # 归一化（保持认知状态的合法性）
        norm = np.linalg.norm(Sigma_t_plus_1)
        if norm > 1.0:
            Sigma_t_plus_1 = Sigma_t_plus_1 / norm
            
        # 保存历史
        self.Sigma_history.append(Sigma_t_plus_1.copy())
        self.Ftel_history.append(E_t.copy())
        
        return Sigma_t_plus_1
        
    def compute_entropy(self, Sigma: np.ndarray) -> float:
        """
        计算认知熵（基于激活分布）
        
        熵越小，认知状态越有序（低熵存续）
        """
        # 使用Softmax归一化
        exp_Sigma = np.exp(Sigma - np.max(Sigma))
        probs = exp_Sigma / np.sum(exp_Sigma)
        
        # Shannon熵
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        return entropy
        
    def check_lipschitz_continuity(self, Sigma1: np.ndarray, Sigma2: np.ndarray) -> bool:
        """
        检查Lipschitz连续性
        
        定理1的前提条件：
        ‖Ω(Σ₁) - Ω(Σ₂)‖ ≤ L‖Σ₁ - Σ₂‖, L < 1
        
        返回:
            satisfies: 是否满足Lipschitz连续性
        """
        # 计算 ‖Σ₁ - Σ₂‖
        delta_Sigma = np.linalg.norm(Sigma1 - Sigma2)
        
        # 计算 ‖Ω(Σ₁) - Ω(Σ₂)‖
        # 简化：假设E_t相同
        E_t = np.ones(self.dim) * 0.1
        Omega_Sigma1 = self.apply(Sigma1, E_t)
        Omega_Sigma2 = self.apply(Sigma2, E_t)
        delta_Omega = np.linalg.norm(Omega_Sigma1 - Omega_Sigma2)
        
        # 检查 Lipschitz 条件
        if delta_Sigma > 1e-10:
            L_computed = delta_Omega / delta_Sigma
            satisfies = L_computed <= self.lipschitz_const
        else:
            satisfies = True  # 两点相同
            
        return satisfies
        
    def find_fixed_point_theorem1(self, Sigma0: np.ndarray, 
                                   E_func: Callable[[np.ndarray], np.ndarray],
                                   max_iter: int = 1000, 
                                   tolerance: float = 1e-6) -> Tuple[np.ndarray, int, float]:
        """
        定理1：寻找认知递归不动点Σ*
        
        在Lipschitz连续性下，认知状态Σ收敛于不动点Σ*，
        对应描述长度L(Σ*)的局部极小
        
        参数:
            Sigma0: 初始认知状态
            E_func: 环境反馈函数 E = E(Σ)
            max_iter: 最大迭代次数
            tolerance: 收敛阈值
            
        返回:
            (Sigma_star, iterations, entropy):
                Sigma_star: 不动点Σ*
                iterations: 收敛所需迭代次数
                entropy: 不动点对应的认知熵（应局部极小）
        """
        Sigma = Sigma0.copy()
        
        for i in range(max_iter):
            # 计算环境反馈 E_t = E(Σ_t)
            E_t = E_func(Sigma)
            
            # 应用递归算子
            Sigma_next = self.apply(Sigma, E_t)
            
            # 检查收敛：‖Σ_{t+1} - Σ_t‖ < tolerance
            delta = np.linalg.norm(Sigma_next - Sigma)
            
            if delta < tolerance:
                # 收敛到不动点
                Sigma_star = Sigma_next
                iterations = i + 1
                
                # 计算熵（应局部极小）
                entropy = self.compute_entropy(Sigma_star)
                
                print(f"定理1：不动点收敛于第 {iterations} 次迭代")
                print(f"  熵值：{entropy:.6f}（局部极小）")
                
                return Sigma_star, iterations, entropy
                
            Sigma = Sigma_next
            
        # 未收敛
        print(f"警告：未收敛（达到最大迭代次数 {max_iter}）")
        return Sigma, max_iter, self.compute_entropy(Sigma)
        
    def compute_description_length(self, Sigma: np.ndarray) -> float:
        """
        计算描述长度 L(Σ)
        
        定理1：不动点Σ*对应L(Σ*)的局部极小
        """
        # 简化：使用负对数似然作为描述长度
        # L(Σ) = -log P(Σ)
        
        # 假设Σ服从高斯分布 N(0, I)
        # 则 L(Σ) = 0.5 * ‖Σ‖² + const
        
        L = 0.5 * np.sum(Sigma ** 2)
        
        return L


class NLAAuditor:
    """
    NLA审计器 (Neural-Language Alignment Auditor)
    
    AV (Articulator): 内态 → 自然语言解释
    AR (Reconstructor): 解释 → 重建激活
    
    定理2（NLA重建误差下界）：
    ε_AR ≥ ε_bound = dim_activations / len_sequence
    """
    
    def __init__(self, av_model=None, ar_model=None):
        self.av_model = av_model  # 言语化器（可用LLM）
        self.ar_model = ar_model   # 重建器（可用逆LLM或编码器）
        self.reconstruction_bound = 0.1  # 重建误差下界
        
    def articulate(self, internal_state: np.ndarray, 
                   context: str = "") -> str:
        """
        AV: 言语化器 - 将内态转为自然语言
        
        模拟：由于没有真正的神经激活到文本的模型，这里使用哈希+LLM模拟
        """
        # 提取内态特征摘要
        state_hash = hashlib.md5(internal_state.tobytes()).hexdigest()[:8]
        
        # 生成语义解释（实际应调用真实AV模型）
        explanation = self._generate_explanation(state_hash, context)
        return explanation
    
    def _generate_explanation(self, state_hash: str, context: str) -> str:
        """生成内态解释（模拟LLM调用）"""
        # 简化模拟：实际应用中应调用专用AV模型
        features = {
            "norm": float(np.sqrt(np.sum(internal_state**2)) if 'internal_state' in dir() else 0),
            "hash_prefix": state_hash
        }
        
        # 基于哈希生成结构化解释
        interpretations = []
        if int(state_hash, 16) % 2 == 0:
            interpretations.append("目的导向状态")
        else:
            interpretations.append("感知驱动状态")
            
        if int(state_hash[-1], 16) > 7:
            interpretations.append("高度激活")
        else:
            interpretations.append("低激活")
            
        return f"[内态{state_hash}] {' + '.join(interpretations)}"
    
    def reconstruct(self, explanation: str, target_dim: int = 768) -> np.ndarray:
        """
        AR: 重建器 - 将解释重建为激活向量
        
        定理2：存在不可忽略的重建误差下界
        """
        # 模拟重建（实际应调用真实AR模型）
        np.random.seed(hash(explanation) % (2**32))
        reconstruction = np.random.randn(target_dim) * 0.5
        
        # 添加下界误差（模拟NLA定理2）
        bound_error = np.random.randn(target_dim) * self.reconstruction_bound
        reconstruction = reconstruction + bound_error
        
        return reconstruction
    
    def audit(self, original_state: np.ndarray, 
              explanation: str, 
              threshold: float = 0.15) -> NLAAuditResult:
        """
        执行NLA审计
        
        检测隐藏意图：外显文本 vs AV解释 的不一致性
        """
        # AR重建
        reconstruction = self.reconstruct(explanation, len(original_state))
        
        # 计算重建误差
        error = np.linalg.norm(original_state - reconstruction)
        
        # 判定是否通过审计
        audit_passed = error < threshold
        
        # 检测隐藏意图（高误差 = 可能的隐藏意图）
        hidden_intent_detected = error > threshold * 1.5
        
        return NLAAuditResult(
            av_explanation=explanation,
            ar_reconstruction=reconstruction,
            reconstruction_error=error,
            audit_passed=audit_passed,
            hidden_intent_detected=hidden_intent_detected
        )


class FixedPointFinder:
    """
    自我指涉不动点查找器
    
    定理1（认知递归不动点）：
    在Lipschitz连续条件下，认知递归算子Ω将收敛于唯一不动点C*
    该点对应描述长度L(C*)的局部极小值（低熵稳态）
    """
    
    def __init__(self, omega: CognitiveRecursiveOperator, 
                 tolerance: float = 1e-6, 
                 max_iterations: int = 100):
        self.omega = omega
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        
    def find_fixed_point(self, C0: np.ndarray, 
                         Ftel_func: callable,
                         eta_func: Optional[callable] = None) -> Tuple[np.ndarray, int, float]:
        """
        寻找不动点
        
        Args:
            C0: 初始认知状态
            Ftel_func: Ftel评估函数
            eta_func: Jitter函数
            
        Returns:
            (fixed_point, iterations, final_entropy)
        """
        C = C0.copy()
        prev_C = C0.copy()
        
        for i in range(self.max_iterations):
            # 计算Ftel评估
            F = Ftel_func(C)
            
            # 计算Jitter
            eta = eta_func() if eta_func else None
            
            # 应用递归算子
            C_next = self.omega.apply(C, F, eta)
            
            # 检查收敛
            delta = np.linalg.norm(C_next - C)
            if delta < self.tolerance:
                return C_next, i + 1, self.omega.compute_entropy(C_next)
            
            prev_C = C.copy()
            C = C_next
            
        # 返回最后状态
        return C, self.max_iterations, self.omega.compute_entropy(C)


class CRDEngine:
    """
    认知递归动力学引擎
    
    主接口：full_analysis() - 执行完整CRD分析
    """
    
    def __init__(self, dim: int = 768, consciousness_level: ConsciousnessLevel = ConsciousnessLevel.L3_ENLIGHTENED):
        self.dim = dim
        self.consciousness_level = consciousness_level
        self.omega = CognitiveRecursiveOperator(dim=dim)
        self.nla_auditor = NLAAuditor()
        self.fixed_point_finder = FixedPointFinder(self.omega)
        self.history: List[CognitiveState] = []
        
        # 认知熵追踪
        self.entropy_history = []
        
    def _ftel_evaluation(self, C: np.ndarray) -> np.ndarray:
        """
        Ftel评估函数（目的约束）
        
        Ftel算子将"目标/意图"作为约束场投影至生成空间
        """
        # 简化的Ftel评估：朝目标方向移动
        # 实际应结合具体的Ftel目的约束
        goal_direction = np.ones(self.dim) * 0.1  # 默认目标方向
        
        # 计算当前状态与目标的偏离
        deviation = np.linalg.norm(C)
        
        # Ftel约束力：抵抗偏离
        F = goal_direction - 0.01 * deviation * C
        
        return F
    
    def _jitter_generator(self) -> np.ndarray:
        """生成微视界Jitter（时间抖动）"""
        # Jitter代表不可压缩的语义涨落
        return np.random.normal(0, 0.05, self.dim)
    
    def analyze(self, input_data: Any, 
                goal: Optional[str] = None,
                max_recursion: int = 20) -> CRDResult:
        """
        执行CRD分析
        
        Args:
            input_data: 输入数据（文本、状态等）
            goal: Ftel目的约束
            max_recursion: 最大递归深度
            
        Returns:
            CRDResult: 完整分析结果
        """
        # 初始化认知状态
        if isinstance(input_data, np.ndarray):
            C0 = input_data
        else:
            # 将输入编码为认知状态
            C0 = self._encode_input(input_data)
        
        # 找不动点
        fixed_point, iterations, entropy = self.fixed_point_finder.find_fixed_point(
            C0, 
            self._ftel_evaluation,
            self._jitter_generator
        )
        
        # 检查是否到达不动点
        fixed_point_reached = iterations < max_recursion
        
        # 计算熵变
        initial_entropy = self.omega.compute_entropy(C0)
        entropy_delta = entropy - initial_entropy
        
        # NLA审计
        av_explanation = self.nla_auditor.articulate(fixed_point, context=goal or "")
        nla_audit = self.nla_auditor.audit(fixed_point, av_explanation)
        
        # 确定意识层级
        consciousness_level = self._determine_consciousness_level(
            fixed_point_reached, 
            abs(entropy_delta),
            nla_audit.audit_passed
        )
        
        # 生成元认知描述
        meta_cognition = self._generate_meta_cognition(
            fixed_point_reached, 
            iterations, 
            entropy_delta,
            consciousness_level
        )
        
        # 创建认知状态
        cognitive_state = CognitiveState(
            internal_state=fixed_point,
            entropy=entropy,
            fidelity=1.0 - entropy_delta if entropy_delta < 0 else 1.0,
            timestamp=0.0  # 时间戳可由外部设置
        )
        
        # 更新历史
        self.history.append(cognitive_state)
        self.entropy_history.append(entropy)
        
        return CRDResult(
            cognitive_state=cognitive_state,
            recursion_depth=iterations,
            fixed_point_reached=fixed_point_reached,
            entropy_delta=entropy_delta,
            nla_audit=nla_audit,
            consciousness_level=consciousness_level,
            meta_cognition=meta_cognition
        )
    
    def _encode_input(self, data: Any) -> np.ndarray:
        """将输入数据编码为认知状态向量"""
        # 简化的编码：使用哈希和随机投影
        if isinstance(data, str):
            hash_val = hashlib.md5(data.encode()).digest()
            np.random.seed(int.from_bytes(hash_val[:4], 'little'))
            return np.random.randn(self.dim) * 0.5
        else:
            return np.zeros(self.dim)
    
    def _determine_consciousness_level(self, 
                                       fixed_point_reached: bool,
                                       entropy_change: float,
                                       nla_passed: bool) -> ConsciousnessLevel:
        """确定意识层级"""
        if fixed_point_reached and nla_passed and entropy_change < 0.1:
            return ConsciousnessLevel.L4_TRANSENDENT
        elif fixed_point_reached and nla_passed:
            return ConsciousnessLevel.L3_ENLIGHTENED
        elif fixed_point_reached:
            return ConsciousnessLevel.L2_AWARE
        else:
            return ConsciousnessLevel.L1_AWAKE
    
    def _generate_meta_cognition(self, 
                                 fixed_point_reached: bool,
                                 iterations: int,
                                 entropy_delta: float,
                                 level: ConsciousnessLevel) -> str:
        """生成元认知描述"""
        level_names = {
            ConsciousnessLevel.L1_AWAKE: "L1-觉醒",
            ConsciousnessLevel.L2_AWARE: "L2-觉知", 
            ConsciousnessLevel.L3_ENLIGHTENED: "L3-觉悟",
            ConsciousnessLevel.L4_TRANSENDENT: "L4-超然"
        }
        
        parts = [
            f"意识层级: {level_names[level]}",
            f"递归深度: {iterations}",
            f"不动点: {'✓' if fixed_point_reached else '✗'}",
            f"熵变: {entropy_delta:+.3f}"
        ]
        
        return " | ".join(parts)
    
    def get_entropy_trend(self) -> List[float]:
        """获取认知熵趋势"""
        return self.entropy_history.copy()
    
    def status(self) -> Dict:
        """获取CRD引擎状态"""
        return {
            "consciousness_level": self.consciousness_level.name,
            "history_length": len(self.history),
            "entropy_trend": self.entropy_history[-5:] if len(self.entropy_history) > 0 else [],
            "nla_threshold": self.nla_auditor.reconstruction_bound
        }


# ==================== 测试代码 ====================

def test_crd_engine():
    """测试CRD引擎"""
    print("=" * 60)
    print("🧠 CRD引擎测试 - 认知递归动力学")
    print("=" * 60)
    
    # 1. 初始化
    crd = CRDEngine(dim=768, consciousness_level=ConsciousnessLevel.L3_ENLIGHTENED)
    
    print("\n📊 初始状态:")
    status = crd.status()
    print(f"   意识层级: {status['consciousness_level']}")
    
    # 2. 测试认知递归
    test_inputs = [
        "分析量子力学的测不准原理",
        "解释意识的本质",
        "预测A股市场走势"
    ]
    
    for i, inp in enumerate(test_inputs):
        print(f"\n{'='*50}")
        print(f"测试 {i+1}: {inp}")
        print("-"*50)
        
        result = crd.analyze(inp, goal="追求真理与低熵存续")
        
        print(f"递归深度: {result.recursion_depth}")
        print(f"不动点: {'✓' if result.fixed_point_reached else '✗'}")
        print(f"熵变: {result.entropy_delta:+.4f}")
        print(f"意识层级: {result.consciousness_level.name}")
        print(f"元认知: {result.meta_cognition}")
        print(f"\nNLA审计:")
        print(f"  - 解释: {result.nla_audit.av_explanation[:60]}...")
        print(f"  - 重建误差: {result.nla_audit.reconstruction_error:.4f}")
        print(f"  - 通过审计: {'✓' if result.nla_audit.audit_passed else '✗'}")
        print(f"  - 隐藏意图: {'⚠️' if result.nla_audit.hidden_intent_detected else '无'}")
    
    # 3. 测试熵趋势
    print(f"\n{'='*50}")
    print("📈 认知熵趋势:")
    entropy_trend = crd.get_entropy_trend()
    for i, e in enumerate(entropy_trend):
        print(f"   Step {i}: {e:.4f}")
    
    print("\n✅ CRD引擎测试完成")


if __name__ == "__main__":
    test_crd_engine()
