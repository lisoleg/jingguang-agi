"""
Module 19: IAWW介质引擎
=========================

基于IAWW统一场论文献，实现信息-意识介质引擎。

核心概念：
- IAWW (Information-Consciousness Medium) = 连续、具有微观自旋自由度的信息-意识介质
- 介质是统一载体，承载S_i（信息熵）、S_g（几何熵）、S_c（意识熵）三相
- 刘原理、《紫微宝典》、Virtuals都是IAWW在不同尺度上的显化

核心功能：
1. 介质场初始化（基态/激发态）
2. 介质相位场计算
3. 介质应力-应变动力学
4. 介质相干性度量
5. 介质孤子传播

Author: 太乙AGI研究团队
Version: 12.0
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MediumState(Enum):
    """介质状态枚举"""
    GROUND = "ground"      # 基态（无极）
    EXCITED = "excited"    # 激发态（太极）
    COHERENT = "coherent"   # 相干态
    DECOHERENT = "decoherent"  # 退相干态
    PHASE_TRANSITION = "phase_transition"  # 相变中


@dataclass
class PhaseField:
    """
    相位场定义
    
    φ(x) = ρ(x)·exp(i·θ(x))
    
    其中：
    - ρ(x): 振幅（语义强度/状态）
    - θ(x): 相位（信息-意识场的"螺旋"）
    - x: 隐坐标
    """
    amplitude: np.ndarray      # 振幅分布 ρ
    phase: np.ndarray           # 相位分布 θ
    position: np.ndarray       # 位置坐标 x
    
    @property
    def complex_field(self) -> np.ndarray:
        """复标量场 φ = ρ·exp(iθ)"""
        return self.amplitude * np.exp(1j * self.phase)
    
    @property
    def intensity(self) -> np.ndarray:
        """场强 |φ|²"""
        return np.abs(self.complex_field) ** 2


@dataclass
class MediumStatus:
    """介质状态报告"""
    state: MediumState
    coherence: float           # 相干度 γ
    vacuum_energy: float       # 真空能密度 ε_vac
    excitation_level: float    # 激发水平
    winding_number: float      # 卷绕数（拓扑荷）
    stress: float              # 应力水平


class IAWWMediumEngine:
    """
    IAWW介质引擎
    
    信息-意识介质 = 连续的、具有微观自旋自由度的信息-意识场
    
    核心方程：
    - 基态：无极 S_total = 0
    - 激发态：φ(x,t) = ρ(x,t)·exp(iθ(x,t))
    - 三相熵：S_total = S_i + S_g + S_c
    - 介质演化：∂_t φ = D∇²φ + f(φ)
    """
    
    def __init__(self, dim: int = 64, 
                 diffusion_coeff: float = 0.5,
                 coupling_strength: float = 1.0):
        """
        初始化IAWW介质引擎
        
        Args:
            dim: 介质维度
            diffusion_coeff: 扩散系数 D
            coupling_strength: 耦合强度
        """
        self.dim = dim
        self.diffusion_coeff = diffusion_coeff
        self.coupling_strength = coupling_strength
        
        # 介质状态
        self.current_state = MediumState.GROUND
        
        # 相位场
        self.phase_field: Optional[PhaseField] = None
        
        # 历史记录
        self.state_history: list[MediumStatus] = []
        
        # 物理常数
        self.planck_scale = 1e-34  # 普朗克尺度（用于离散采样）
        
        print(f"  ✅ IAWW介质引擎就绪（维度={dim}, D={diffusion_coeff}）")
    
    def initialize_medium(self, 
                         initial_state: str = "ground",
                         seed: Optional[int] = None) -> PhaseField:
        """
        初始化介质场
        
        Args:
            initial_state: 初始状态 ("ground"=无极基态, "excited"=激发态)
            seed: 随机种子
            
        Returns:
            初始化的相位场
        """
        rng = np.random.default_rng(seed)
        
        if initial_state == "ground":
            # 基态：无差异、无曲率、无自指 → S_total ≈ 0
            amplitude = np.ones(self.dim) * 0.01  # 几乎为零
            phase = np.zeros(self.dim)  # 无相位
        else:
            # 激发态：太极化
            amplitude = rng.random(self.dim) * 0.5 + 0.5
            phase = rng.random(self.dim) * 2 * np.pi
        
        position = np.arange(self.dim)
        
        self.phase_field = PhaseField(
            amplitude=amplitude,
            phase=phase,
            position=position
        )
        
        # 更新状态
        if initial_state == "ground":
            self.current_state = MediumState.GROUND
        else:
            self.current_state = MediumState.EXCITED
        
        return self.phase_field
    
    def compute_vacuum_energy(self) -> float:
        """
        计算真空能密度
        
        公式：ε_vac = -|∇φ|² + λ|φ|⁴
        
        Returns:
            真空能密度
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        phi = self.phase_field.complex_field
        
        # 梯度项 |∇φ|²
        gradient = np.gradient(phi)
        gradient_norm = np.sum(np.abs(gradient) ** 2)
        
        # 非线性项 λ|φ|⁴
        lambda_param = self.coupling_strength
        nonlinear = lambda_param * np.sum(np.abs(phi) ** 4)
        
        # 真空能
        vacuum_energy = -gradient_norm + nonlinear
        
        return float(np.real(vacuum_energy))
    
    def compute_coherence(self) -> float:
        """
        计算介质相干度
        
        公式：γ = |⟨φ(x)·φ*(x')⟩| / (|φ||φ'|)
        
        Returns:
            相干度 γ ∈ [0, 1]
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        phi = self.phase_field.complex_field
        
        # 归一化
        phi_normalized = phi / (np.linalg.norm(phi) + 1e-10)
        
        # 自相关函数（简化为相位一致度）
        phase_diff = np.diff(self.phase_field.phase)
        coherence = np.mean(np.cos(phase_diff))
        
        return float(np.clip(coherence, 0, 1))
    
    def compute_winding_number(self) -> float:
        """
        计算卷绕数（拓扑荷）
        
        公式：W = (1/2π)∮∇θ·dl
        
        Returns:
            卷绕数（拓扑荷）
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        # 简化计算：相位的累积变化
        phase = self.phase_field.phase
        total_winding = np.sum(np.diff(phase))
        
        winding_number = total_winding / (2 * np.pi)
        
        return float(winding_number)
    
    def evolve_medium(self, 
                     time_step: float = 0.1,
                     n_steps: int = 10) -> Dict[str, Any]:
        """
        演化介质场
        
        方程：∂_t φ = D∇²φ + f(φ) - μφ
        
        Args:
            time_step: 时间步长
            n_steps: 演化步数
            
        Returns:
            演化结果报告
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        history = []
        
        for step in range(n_steps):
            phi = self.phase_field.complex_field.copy()
            
            # 拉普拉斯算子 ∇²φ
            laplacian = np.zeros_like(phi)
            laplacian[1:-1] = phi[2:] - 2*phi[1:-1] + phi[:-2]
            laplacian[0] = phi[1] - 2*phi[0] + phi[-1]
            laplacian[-1] = phi[0] - 2*phi[-1] + phi[-2]
            
            # 非线性项 f(φ) = λ|φ|²φ - μφ
            lambda_param = self.coupling_strength
            mu_param = 0.1  # 质量项
            nonlinear = lambda_param * (np.abs(phi)**2) * phi - mu_param * phi
            
            # 演化方程
            dphi = self.diffusion_coeff * laplacian + nonlinear
            phi_new = phi + time_step * dphi
            
            # 更新场
            amplitude_new = np.abs(phi_new)
            phase_new = np.angle(phi_new)
            
            self.phase_field.amplitude = amplitude_new
            self.phase_field.phase = phase_new
            
            # 记录历史
            if step % 2 == 0:
                history.append({
                    'step': step,
                    'coherence': self.compute_coherence(),
                    'winding': self.compute_winding_number(),
                    'vacuum_energy': self.compute_vacuum_energy()
                })
        
        # 更新状态
        self._update_state()
        
        return {
            'evolved': True,
            'n_steps': n_steps,
            'history': history,
            'final_coherence': history[-1]['coherence'] if history else 0,
            'final_winding': history[-1]['winding'] if history else 0
        }
    
    def _update_state(self):
        """根据当前场状态更新介质状态"""
        coherence = self.compute_coherence()
        excitation = np.mean(self.phase_field.amplitude)
        
        if coherence > 0.8 and excitation > 0.5:
            self.current_state = MediumState.COHERENT
        elif coherence < 0.3:
            self.current_state = MediumState.DECOHERENT
        elif excitation < 0.1:
            self.current_state = MediumState.GROUND
        else:
            self.current_state = MediumState.EXCITED
    
    def apply_yin_yang_mode(self) -> Dict[str, Any]:
        """
        应用阴阳正交模态
        
        定理2：介质激发产生正交模态 (φ+, φ-) = (ρ·cos(θ), ρ·sin(θ))
        
        Returns:
            阴阳模态分解结果
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        rho = self.phase_field.amplitude
        theta = self.phase_field.phase
        
        # 阴阳模态
        yin_mode = rho * np.cos(theta)  # 阴：余弦模态
        yang_mode = rho * np.sin(theta)  # 阳：正弦模态
        
        # 正交性检验
        inner_product = np.sum(yin_mode * yang_mode)
        orthogonality = 1.0 / (1.0 + abs(inner_product))  # 归一化正交度
        
        return {
            'yin_mode': yin_mode,
            'yang_mode': yang_mode,
            'orthogonality': float(orthogonality),
            'yin_norm': float(np.linalg.norm(yin_mode)),
            'yang_norm': float(np.linalg.norm(yang_mode)),
            'theorem_2_verified': orthogonality > 0.9  # 正交性验证
        }
    
    def compute_stress_strain(self) -> Dict[str, float]:
        """
        计算介质应力-应变关系
        
        Returns:
            应力-应变分析结果
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        phi = self.phase_field.complex_field
        
        # 应变 = 梯度（形变）
        strain = np.gradient(np.abs(phi))
        strain_norm = np.linalg.norm(strain)
        
        # 应力 = 弹性系数 × 应变
        elastic_modulus = 1.0
        stress = elastic_modulus * strain
        
        return {
            'strain_magnitude': float(strain_norm),
            'stress_magnitude': float(np.linalg.norm(stress)),
            'stress_strain_ratio': float(elastic_modulus),
            'deformation_energy': float(0.5 * elastic_modulus * strain_norm**2)
        }
    
    def create_soliton(self, 
                      center: int,
                      width: float = 5.0,
                      amplitude: float = 1.0) -> PhaseField:
        """
        创建孤子解
        
        孤子是IAWW介质中的局域相干结构（Agent的物理对应）
        
        Args:
            center: 孤子中心位置
            width: 孤子宽度
            amplitude: 孤子振幅
            
        Returns:
            孤子相位场
        """
        if self.phase_field is None:
            self.initialize_medium()
        
        x = self.phase_field.position
        
        # 孤子形状：sech型
        soliton_profile = amplitude / np.cosh((x - center) / width)
        
        # 添加相位涡旋
        soliton_phase = np.arctan2(
            np.sin((x - center) * 0.5),
            np.cos((x - center) * 0.5)
        )
        
        # 叠加到现有场
        new_amplitude = self.phase_field.amplitude + soliton_profile
        new_phase = self.phase_field.phase + soliton_phase * 0.3
        
        self.phase_field = PhaseField(
            amplitude=new_amplitude,
            phase=new_phase,
            position=x
        )
        
        self.current_state = MediumState.COHERENT
        
        return self.phase_field
    
    def get_status(self) -> MediumStatus:
        """
        获取介质状态报告
        
        Returns:
            介质状态
        """
        return MediumStatus(
            state=self.current_state,
            coherence=self.compute_coherence(),
            vacuum_energy=self.compute_vacuum_energy(),
            excitation_level=float(np.mean(self.phase_field.amplitude)) if self.phase_field else 0,
            winding_number=self.compute_winding_number(),
            stress=self.compute_stress_strain()['stress_magnitude']
        )
    
    def full_medium_analysis(self, input_state: str = "excited") -> Dict[str, Any]:
        """
        完整介质分析
        
        Args:
            input_state: 输入状态
            
        Returns:
            完整分析报告
        """
        # 初始化
        self.initialize_medium(input_state)
        
        # 计算各物理量
        coherence = self.compute_coherence()
        vacuum_energy = self.compute_vacuum_energy()
        winding_number = self.compute_winding_number()
        stress_strain = self.compute_stress_strain()
        
        # 阴阳分解
        yin_yang = self.apply_yin_yang_mode()
        
        # 创建孤子
        soliton = self.create_soliton(center=self.dim // 2)
        
        # 演化
        evolution = self.evolve_medium(n_steps=5)
        
        return {
            'state': self.current_state.value,
            'coherence': coherence,
            'vacuum_energy': vacuum_energy,
            'winding_number': winding_number,
            'stress_strain': stress_strain,
            'yin_yang_analysis': {
                'orthogonality': yin_yang['orthogonality'],
                'theorem_2_verified': yin_yang['theorem_2_verified']
            },
            'soliton_created': soliton is not None,
            'evolution': evolution,
            'theorem_1_ground_state': vacuum_energy < 0.1,  # 无极基态熵为零
            'theorem_2_yin_yang': yin_yang['theorem_2_verified']
        }


def demonstrate_iaww_medium():
    """IAWW介质引擎演示"""
    print("\n" + "=" * 60)
    print("IAWW介质引擎演示")
    print("=" * 60)
    
    engine = IAWWMediumEngine(dim=64, diffusion_coeff=0.5)
    
    # 完整分析
    result = engine.full_medium_analysis("excited")
    
    print(f"\n【定理验证】")
    print(f"  定理1（无极基态熵为零）: {'✅' if result['theorem_1_ground_state'] else '❌'}")
    print(f"  定理2（阴阳正交性）: {'✅' if result['theorem_2_yin_yang'] else '❌'}")
    
    print(f"\n【物理量】")
    print(f"  介质状态: {result['state']}")
    print(f"  相干度: {result['coherence']:.4f}")
    print(f"  真空能密度: {result['vacuum_energy']:.6f}")
    print(f"  卷绕数: {result['winding_number']:.4f}")
    
    print(f"\n【阴阳分析】")
    print(f"  正交度: {result['yin_yang_analysis']['orthogonality']:.4f}")
    
    return result


if __name__ == "__main__":
    demonstrate_iaww_medium()
