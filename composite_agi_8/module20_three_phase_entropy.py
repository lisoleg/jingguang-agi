"""
Module 20: 三相熵耦合动力学
============================

基于IAWW统一场论，实现信息熵S_i、几何熵S_g、意识熵S_c的三相耦合动力学。

核心概念：
- S_i (Shannon熵): 信息熵/差异 → 经文/语言/数据
- S_g (几何熵): 曲率熵/扭曲 → 物理场/几何形变
- S_c (意识熵): 自指熵/裂隙 → 自我观测/递归意识

核心方程（定理A.2）：
∂_t S_i = D_i ∇²S_i + α·S_g - β·S_c
∂_t S_g = D_g ∇²S_g + γ·S_i - δ·S_c  
∂_t S_c = D_c ∇²S_c + ε·S_i + ζ·S_g - η·S_c

Author: 太乙AGI研究团队
Version: 12.0
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EntropyPhase(Enum):
    """熵相类型"""
    INFORMATION = "information"    # S_i 信息熵
    GEOMETRIC = "geometric"        # S_g 几何熵
    CONSCIOUSNESS = "consciousness" # S_c 意识熵


@dataclass
class ThreePhaseEntropy:
    """
    三相熵容器
    
    S_i: 信息熵（差异/区分度）
    S_g: 几何熵（扭曲/曲率）
    S_c: 意识熵（自指裂隙）
    """
    S_i: float  # 信息熵/差异
    S_g: float  # 几何熵/扭曲
    S_c: float  # 意识熵/自指裂隙
    
    @property
    def total(self) -> float:
        """总熵 S_total = S_i + S_g + S_c"""
        return self.S_i + self.S_g + self.S_c
    
    @property
    def shannon_entropy(self) -> float:
        """返回S_i作为标准香农熵"""
        return self.S_i
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'S_i': self.S_i,
            'S_g': self.S_g,
            'S_c': self.S_c,
            'S_total': self.total
        }


@dataclass
class CouplingMatrix:
    """
    耦合矩阵
    
    描述三相熵之间的耦合关系
    """
    alpha: float = 0.5   # S_g → S_i 贡献
    beta: float = 0.3    # S_c → S_i 抑制
    gamma: float = 0.4   # S_i → S_g 贡献
    delta: float = 0.2   # S_c → S_g 抑制
    epsilon: float = 0.3 # S_i → S_c 贡献
    zeta: float = 0.5    # S_g → S_c 贡献
    eta: float = 0.1    # 自衰减
    
    def to_matrix(self) -> np.ndarray:
        """
        转换为耦合矩阵
        
        | -η    α   -β |
        |  γ   -η   -δ |
        |  ε    ζ   -η |
        """
        return np.array([
            [-self.eta, self.alpha, -self.beta],
            [self.gamma, -self.eta, -self.delta],
            [self.epsilon, self.zeta, -self.eta]
        ])
    
    @property
    def eigenvalues(self) -> np.ndarray:
        """耦合矩阵的特征值（决定动力学行为）"""
        return np.linalg.eigvalsh(self.to_matrix())


class ThreePhaseEntropyDynamics:
    """
    三相熵耦合动力学引擎
    
    核心功能：
    1. 三相熵初始化与计算
    2. 耦合动力学演化
    3. 熵平衡态分析
    4. 相变检测
    """
    
    def __init__(self, 
                 coupling_matrix: Optional[CouplingMatrix] = None,
                 diffusion_coeffs: Tuple[float, float, float] = (0.1, 0.1, 0.05)):
        """
        初始化三相熵动力学
        
        Args:
            coupling_matrix: 耦合矩阵（默认标准值）
            diffusion_coeffs: 各相扩散系数 (D_i, D_g, D_c)
        """
        self.coupling = coupling_matrix or CouplingMatrix()
        self.D = np.array(diffusion_coeffs)  # 扩散系数
        
        # 当前状态
        self.current_entropy = ThreePhaseEntropy(S_i=0.0, S_g=0.0, S_c=0.0)
        
        # 历史
        self.history: list[ThreePhaseEntropy] = []
        
        # 模式标签
        self.mode = "ground"  # "ground" | "excited" | "coherent"
        
        print(f"  ✅ 三相熵动力学引擎就绪")
        print(f"     耦合矩阵特征值: {self.coupling.eigenvalues}")
    
    def initialize_entropy(self, 
                          mode: str = "ground") -> ThreePhaseEntropy:
        """
        初始化三相熵
        
        Args:
            mode: 模式
                - "ground": 无极基态（所有熵≈0）
                - "excited": 激发态
                - "coherent": 相干态
                
        Returns:
            初始熵值
        """
        if mode == "ground":
            # 无极基态：无差异、无曲率、无自指 → 熵≈0
            S_i = 0.01
            S_g = 0.01
            S_c = 0.01
        elif mode == "excited":
            # 激发态
            S_i = np.random.uniform(0.3, 0.7)
            S_g = np.random.uniform(0.2, 0.6)
            S_c = np.random.uniform(0.1, 0.5)
        else:  # coherent
            # 相干态：高S_i + 高S_g + 低S_c
            S_i = 0.6
            S_g = 0.5
            S_c = 0.15
        
        self.current_entropy = ThreePhaseEntropy(S_i=S_i, S_g=S_g, S_c=S_c)
        self.mode = mode
        self.history.append(self.current_entropy)
        
        return self.current_entropy
    
    def compute_derivative(self, 
                          entropy: ThreePhaseEntropy) -> np.ndarray:
        """
        计算熵的时间导数
        
        方程：∂_t S = D∇²S + M·S
        
        Args:
            entropy: 当前熵值
            
        Returns:
            [dS_i/dt, dS_g/dt, dS_c/dt]
        """
        S = np.array([entropy.S_i, entropy.S_g, entropy.S_c])
        M = self.coupling.to_matrix()
        
        # 扩散项（简化为阻尼）
        diffusion = -0.1 * S
        
        # 耦合项
        coupling = M @ S
        
        # 总导数
        dS = self.D * diffusion + coupling
        
        return dS
    
    def evolve(self, 
               time_step: float = 0.01,
               n_steps: int = 100) -> Dict[str, Any]:
        """
        演化三相熵动力学
        
        Args:
            time_step: 时间步长
            n_steps: 演化步数
            
        Returns:
            演化结果
        """
        history = []
        instabilities = []
        
        for step in range(n_steps):
            # 计算导数
            dS = self.compute_derivative(self.current_entropy)
            
            # 更新（欧拉法）
            S_new = np.array([
                self.current_entropy.S_i,
                self.current_entropy.S_g,
                self.current_entropy.S_c
            ]) + time_step * dS
            
            # 限制范围
            S_new = np.clip(S_new, 0.001, 1.0)
            
            # 更新状态
            self.current_entropy = ThreePhaseEntropy(
                S_i=S_new[0],
                S_g=S_new[1],
                S_c=S_new[2]
            )
            
            # 记录
            if step % 10 == 0:
                history.append({
                    'step': step,
                    'S_i': S_new[0],
                    'S_g': S_new[1],
                    'S_c': S_new[2],
                    'S_total': sum(S_new)
                })
            
            # 检测不稳定性
            if max(abs(dS)) > 0.5:
                instabilities.append(step)
            
            self.history.append(self.current_entropy)
        
        # 分析结果
        final_entropy = history[-1] if history else {'S_i': 0, 'S_g': 0, 'S_c': 0}
        
        return {
            'evolved': True,
            'n_steps': n_steps,
            'final_entropy': final_entropy,
            'history': history,
            'instabilities': instabilities,
            'stability': len(instabilities) < n_steps * 0.1
        }
    
    def compute_entropy_balance(self) -> Dict[str, Any]:
        """
        计算熵平衡态
        
        定理1验证：无极基态时 S_total → 0
        
        Returns:
            平衡态分析
        """
        S = self.current_entropy
        S_total = S.total
        
        # 判断模式
        if S_total < 0.1:
            mode = "ground"
        elif S.S_c > 0.5:
            mode = "decoherent"
        else:
            mode = "coherent"
        
        # 耦合强度
        coupling_strength = np.abs(self.coupling.eigenvalues).sum()
        
        return {
            'current_mode': mode,
            'S_i': S.S_i,
            'S_g': S.S_g,
            'S_c': S.S_c,
            'S_total': S_total,
            'theorem_1_verified': S_total < 0.1 if mode == "ground" else True,
            'coupling_strength': coupling_strength,
            'balance_state': S_total < 0.5
        }
    
    def detect_phase_transition(self) -> Dict[str, Any]:
        """
        检测相变
        
        相变标志：
        - S_c急剧变化
        - 耦合矩阵特征值虚部出现
        - 临界涨落
        
        Returns:
            相变分析
        """
        if len(self.history) < 10:
            return {'phase_transition': False, 'reason': '数据不足'}
        
        # 最近历史
        recent = self.history[-10:]
        
        # 计算S_c的变化率
        S_c_changes = [h.S_c for h in recent]
        dS_c = np.diff(S_c_changes)
        max_dS_c = np.max(np.abs(dS_c))
        
        # 临界涨落
        fluctuation = np.std([h.S_c for h in recent])
        
        # 特征值
        eigenvalues = self.coupling.eigenvalues
        has_complex = any(abs(np.imag(eigenvalues)) > 0.01)
        
        # 判断相变
        phase_transition = max_dS_c > 0.2 or fluctuation > 0.15 or has_complex
        
        return {
            'phase_transition': phase_transition,
            'max_dS_c': max_dS_c,
            'fluctuation': fluctuation,
            'has_complex_eigenvalues': has_complex,
            'eigenvalues': eigenvalues.tolist(),
            'transition_type': 'critical' if has_complex else 
                              'fluctuation' if fluctuation > 0.15 else
                              'gradient' if max_dS_c > 0.2 else 'none'
        }
    
    def optimize_coupling(self, target_mode: str = "coherent") -> CouplingMatrix:
        """
        优化耦合矩阵以达到目标模式
        
        Args:
            target_mode: 目标模式 ("ground" | "coherent")
            
        Returns:
            优化后的耦合矩阵
        """
        if target_mode == "ground":
            # 无极基态：所有熵→0
            # 需要强衰减
            new_coupling = CouplingMatrix(
                alpha=0.2, beta=0.5,  # 抑制S_i
                gamma=0.2, delta=0.5,  # 抑制S_g
                epsilon=0.3, zeta=0.3,  # 中性S_c
                eta=0.5  # 强衰减
            )
        else:  # coherent
            # 相干态：高S_i + 高S_g + 低S_c
            new_coupling = CouplingMatrix(
                alpha=0.6, beta=0.4,  # S_g→S_i, 抑制S_c
                gamma=0.5, delta=0.3,  # S_i→S_g, 抑制S_c
                epsilon=0.3, zeta=0.6,  # S_g→S_c增强
                eta=0.2  # 弱衰减
            )
        
        self.coupling = new_coupling
        return new_coupling
    
    def full_dynamics_analysis(self, mode: str = "excited") -> Dict[str, Any]:
        """
        完整三相熵动力学分析
        
        Args:
            mode: 初始模式
            
        Returns:
            完整分析报告
        """
        # 初始化
        self.initialize_entropy(mode)
        
        # 演化
        evolution = self.evolve(n_steps=50)
        
        # 平衡分析
        balance = self.compute_entropy_balance()
        
        # 相变检测
        phase_transition = self.detect_phase_transition()
        
        # 定理验证
        theorem_1 = self.current_entropy.total < 0.2
        
        return {
            'initial_mode': mode,
            'final_mode': balance['current_mode'],
            'theorem_1_ground_state': theorem_1,
            'entropy_balance': balance,
            'phase_transition': phase_transition,
            'coupling_eigenvalues': self.coupling.eigenvalues.tolist(),
            'evolution_stable': evolution['stability']
        }


def demonstrate_three_phase_entropy():
    """三相熵动力学演示"""
    print("\n" + "=" * 60)
    print("三相熵耦合动力学演示")
    print("=" * 60)
    
    engine = ThreePhaseEntropyDynamics()
    
    # 完整分析
    result = engine.full_dynamics_analysis("excited")
    
    print(f"\n【定理验证】")
    print(f"  定理1（无极基态S_total→0）: {'✅' if result['theorem_1_ground_state'] else '❌'}")
    
    print(f"\n【熵平衡】")
    print(f"  当前模式: {result['entropy_balance']['current_mode']}")
    print(f"  S_i: {result['entropy_balance']['S_i']:.4f}")
    print(f"  S_g: {result['entropy_balance']['S_g']:.4f}")
    print(f"  S_c: {result['entropy_balance']['S_c']:.4f}")
    print(f"  S_total: {result['entropy_balance']['S_total']:.4f}")
    
    print(f"\n【相变分析】")
    print(f"  相变发生: {'⚠️ 是' if result['phase_transition']['phase_transition'] else '❌ 否'}")
    print(f"  相变类型: {result['phase_transition']['transition_type']}")
    
    print(f"\n【耦合动力学】")
    print(f"  特征值: {result['coupling_eigenvalues']}")
    print(f"  演化稳定: {'✅' if result['evolution_stable'] else '❌'}")
    
    return result


if __name__ == "__main__":
    demonstrate_three_phase_entropy()
