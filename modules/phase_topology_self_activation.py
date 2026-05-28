#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
相位拓扑自激模型 - Phase Topology Self-activation (PTS) Model

基于论文05：相位拓扑自激与QED涌现
基于论文06：相位拓扑自激与波粒二象性

核心理论：
1. 波粒二象性 = 同一ψ场的两种拓扑态
   - 波核W：相干延展（干涉/衍射）
   - 粒核P：拓扑孤子（局域化、自旋源于拓扑荷）

2. "阴极阳生"数学化：
   - 当ψ场沿闭合路径C的缠绕数 Winding Number = 2π
   - 相位场自指性迫使拓扑相变
   - 从波态"自我完成"为粒态（无需外部观测者）

3. 太极算符 T：实现阴阳翻转，对应相位π旋转

4. QED作为PTS弱耦合极限：
   - 电子 = ψ场的拓扑孤子（拓扑荷Q=±1）
   - 光子 = ψ场的相干延展模（拓扑荷Q=0）
   - 精细结构常数 α = g²/(4π) 在g→0时的涌现
   - 自然紫外截断：由ψ场拓扑尺度Λ_φ提供
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from scipy.ndimage import laplace


@dataclass
class PTSField:
    """
    PTS场（相位拓扑自激场）
    
    定义了ψ场及其拓扑性质
    """
    psi: np.ndarray  # 复数值场 ψ: ℝ² → ℂ
    grid_size: int  # 网格大小
    dx: float = 0.1  # 空间步长
    
    def __post_init__(self):
        """初始化后处理"""
        if self.psi is None:
            # 默认：高斯波包
            self.psi = self._default_psi()
            
    def _default_psi(self) -> np.ndarray:
        """默认ψ场：高斯波包"""
        x = np.linspace(-5, 5, self.grid_size)
        y = np.linspace(-5, 5, self.grid_size)
        X, Y = np.meshgrid(x, y)
        
        # 高斯波包
        psi = np.exp(-(X**2 + Y**2) / 2) * np.exp(1j * (X + Y))
        
        # 归一化
        norm = np.sqrt(np.sum(np.abs(psi)**2))
        psi = psi / (norm + 1e-10)
        
        return psi
        
    def compute_winding_number(self, contour: List[Tuple[int, int]]) -> float:
        """
        计算缠绕数 Winding Number
        
        参数:
            contour: 闭合路径C的点列表 [(i1, j1), (i2, j2), ...]
            
        返回:
            winding_number: 缠绕数（当=2π时触发"阴极阳生"）
        """
        # 计算相位沿路径的累积变化
        phase_sum = 0.0
        
        for k in range(len(contour)):
            # 当前点
            i1, j1 = contour[k]
            # 下一点（闭合路径）
            i2, j2 = contour[(k+1) % len(contour)]
            
            # 获取相位
            phase1 = np.angle(self.psi[i1, j1])
            phase2 = np.angle(self.psi[i2, j2])
            
            # 相位差（处理2π跳跃）
            delta_phase = phase2 - phase1
            if delta_phase > np.pi:
                delta_phase -= 2 * np.pi
            elif delta_phase < -np.pi:
                delta_phase += 2 * np.pi
                
            phase_sum += delta_phase
        
        # 缠绕数 = 总相位变化 / 2π
        winding_number = phase_sum / (2 * np.pi)
        
        return winding_number
        
    def compute_topological_charge(self) -> np.ndarray:
        """
        计算拓扑荷 Q
        
        拓扑荷密度：ρ_Q = (1/2π) ∇ × ∇θ
        其中 θ = arg(ψ) 是相位场
        
        返回:
            Q_density: 拓扑荷密度场
        """
        # 计算相位场 θ = arg(ψ)
        theta = np.angle(self.psi)
        
        # 计算梯度 ∇θ
        grad_theta_y, grad_theta_x = np.gradient(theta, self.dx)
        
        # 计算旋度 ∇ × ∇θ（在2D中，旋度是标量）
        # ∇ × ∇θ = ∂(∇θ)_y/∂x - ∂(∇θ)_x/∂y
        curl_x = np.gradient(grad_theta_y, self.dx, axis=1)
        curl_y = np.gradient(grad_theta_x, self.dx, axis=0)
        curl = curl_x - curl_y
        
        # 拓扑荷密度
        Q_density = curl / (2 * np.pi)
        
        return Q_density
        
    def detect_vortex(self) -> List[Tuple[int, int]]:
        """
        检测涡旋（拓扑缺陷）
        
        涡旋是拓扑荷非零的点
        
        返回:
            vortices: 涡旋位置列表 [(i, j), ...]
        """
        Q_density = self.compute_topological_charge()
        
        # 检测拓扑荷非零的点
        vortices = []
        threshold = 0.1
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if abs(Q_density[i, j]) > threshold:
                    vortices.append((i, j))
                    
        return vortices


class WaveParticleDuality:
    """
    波粒二象性：同一ψ场的两种拓扑态
    
    基于论文06：相位拓扑自激与波粒二象性
    """
    
    def __init__(self, psi_field: PTSField):
        """
        初始化波粒二象性模型
        
        参数:
            psi_field: PTS场
        """
        self.psi_field = psi_field
        
    def decompose_wave_particle(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        波粒二象性分解：同一ψ场的两种拓扑态
        
        返回:
            W: 波核（相干延展）
            P: 粒核（拓扑孤子）
        """
        psi = self.psi_field.psi
        
        # 方法1：基于拓扑荷分解
        Q_density = self.psi_field.compute_topological_charge()
        
        # 波核W：相干延展部分（拓扑荷接近0）
        W = psi.copy()
        W[np.abs(Q_density) > 0.1] = 0  # 去除拓扑荷非零的点
        
        # 粒核P：拓扑孤子（拓扑荷非零）
        P = psi.copy()
        P[np.abs(Q_density) <= 0.1] = 0  # 去除拓扑荷为零的点
        
        # 归一化
        norm_W = np.sqrt(np.sum(np.abs(W)**2))
        norm_P = np.sqrt(np.sum(np.abs(P)**2))
        
        if norm_W > 1e-10:
            W = W / norm_W
        if norm_P > 1e-10:
            P = P / norm_P
            
        return W, P
        
    def compute_interference(self, W: np.ndarray) -> np.ndarray:
        """
        计算干涉图样（波核的相干延展）
        
        参数:
            W: 波核
            
        返回:
            interference: 干涉强度分布
        """
        # 强度 = |ψ|²
        interference = np.abs(W)**2
        
        return interference
        
    def compute_localization(self, P: np.ndarray) -> Dict[str, Any]:
        """
        计算局域化性质（粒核的拓扑孤子）
        
        参数:
            P: 粒核
            
        返回:
            localization: 局域化信息
                - center: 中心位置
                - size: 尺寸
                - topological_charge: 拓扑荷
        """
        # 计算概率分布
        prob = np.abs(P)**2
        
        # 计算质心（中心位置）
        indices = np.indices(P.shape)
        total_prob = np.sum(prob)
        
        if total_prob < 1e-10:
            return {'center': None, 'size': 0, 'topological_charge': 0}
            
        center_x = np.sum(indices[0] * prob) / total_prob
        center_y = np.sum(indices[1] * prob) / total_prob
        
        # 计算尺寸（标准差）
        var_x = np.sum((indices[0] - center_x)**2 * prob) / total_prob
        var_y = np.sum((indices[1] - center_y)**2 * prob) / total_prob
        size = np.sqrt(var_x + var_y)
        
        # 计算拓扑荷
        Q_density = self.psi_field.compute_topological_charge()
        topological_charge = np.sum(Q_density * prob) / total_prob
        
        return {
            'center': (center_x, center_y),
            'size': size,
            'topological_charge': topological_charge
        }


class TaijiOperator:
    """
    太极算符 T：实现阴阳翻转
    
    数学：ψ → e^(iπ) * ψ = -ψ
    对应相位π旋转
    """
    
    def __init__(self):
        pass
        
    def apply(self, psi: np.ndarray) -> np.ndarray:
        """
        应用太极算符 T
        
        数学：T(ψ) = -ψ （相位旋转π）
        
        参数:
            psi: 输入场
            
        返回:
            psi_transformed: 变换后的场
        """
        return -psi
        
    def yin_yang_flip(self, psi: np.ndarray) -> np.ndarray:
        """
        阴阳翻转（太极算符的别名）
        
        参数:
            psi: 输入场
            
        返回:
            psi_flipped: 翻转后的场
        """
        return self.apply(psi)


class CathodeYangBirth:
    """
    "阴极阳生"临界条件检测器
    
    当ψ场沿闭合路径C的缠绕数 Winding Number = 2π时，
    相位场自指性迫使拓扑相变，从波态"自我完成"为粒态
    """
    
    def __init__(self, threshold: float = 1e-6):
        """
        初始化阴极阳生检测器
        
        参数:
            threshold: 阈值（判断缠绕数是否接近2π）
        """
        self.threshold = threshold
        
    def check_critical_condition(self, psi_field: PTSField, 
                                contour: List[Tuple[int, int]]) -> Tuple[bool, float]:
        """
        检查"阴极阳生"临界条件
        
        条件: Winding Number = 2π
        
        参数:
            psi_field: PTS场
            contour: 闭合路径C
            
        返回:
            (trigger, winding_number):
                trigger: 是否触发阴极阳生
                winding_number: 缠绕数
        """
        # 计算缠绕数
        winding_number = psi_field.compute_winding_number(contour)
        
        # 检查是否接近2π（注意：winding_number是绕数，不是弧度）
        # 绕数 = 整数，表示绕原点多少圈
        # 当绕数 ≠ 0时，表示相位场有拓扑缺陷
        trigger = abs(winding_number - round(winding_number)) < self.threshold
        
        return trigger, winding_number
        
    def induce_topological_phase_transition(self, 
                                            psi_field: PTSField,
                                            contour: List[Tuple[int, int]]) -> np.ndarray:
        """
        诱导拓扑相变（从波态到粒态）
        
        当触发"阴极阳生"时，ψ场从波态"自我完成"为粒态
        
        参数:
            psi_field: PTS场
            contour: 闭合路径C
            
        返回:
            psi_new: 相变后的ψ场
        """
        # 检查是否触发
        trigger, winding_number = self.check_critical_condition(psi_field, contour)
        
        if not trigger:
            print(f"未触发阴极阳生（缠绕数 = {winding_number}）")
            return psi_field.psi
            
        print(f"🔄 触发阴极阳生！（缠绕数 = {winding_number}）")
        
        # 拓扑相变：从波态到粒态
        # 方法：在涡旋位置创建局域化模
        vortices = psi_field.detect_vortex()
        
        psi_new = psi_field.psi.copy()
        
        for (i, j) in vortices:
            # 在涡旋位置创建高斯孤子
            x0, y0 = i, j
            x = np.arange(psi_field.grid_size)
            y = np.arange(psi_field.grid_size)
            X, Y = np.meshgrid(x, y)
            
            # 高斯孤子
            soliton = np.exp(-((X - x0)**2 + (Y - y0)**2) / 2)
            
            # 添加到ψ场
            psi_new = psi_new + soliton * np.exp(1j * np.angle(psi_new[i, j]))
            
        # 归一化
        norm = np.sqrt(np.sum(np.abs(psi_new)**2))
        psi_new = psi_new / (norm + 1e-10)
        
        return psi_new


class QEDEmergence:
    """
    QED作为PTS弱耦合极限
    
    基于论文05：相位拓扑自激与QED涌现
    
    核心思想：
    - 电子 = ψ场的拓扑孤子（拓扑荷Q=±1）
    - 光子 = ψ场的相干延展模（拓扑荷Q=0）
    - 精细结构常数 α = g²/(4π) 在g→0时的涌现
    - 自然紫外截断：由ψ场拓扑尺度Λ_φ提供
    """
    
    def __init__(self, g: float = 0.1):
        """
        初始化QED涌现模型
        
        参数:
            g: 自耦合常数（表征波核与粒核之间的内在自指性相互作用）
        """
        self.g = g
        self.lambda_phi = 1.0  # ψ场拓扑尺度（自然紫外截断）
        
    def compute_fine_structure_constant(self) -> float:
        """
        计算精细结构常数 α
        
        公式：α = g²/(4π) 在g→0时的涌现
        
        返回:
            alpha: 精细结构常数
        """
        alpha = self.g**2 / (4 * np.pi)
        return alpha
        
    def uv_cutoff(self) -> float:
        """
        自然紫外截断
        
        由ψ场拓扑尺度Λ_φ提供
        
        返回:
            Lambda: 紫外截断尺度
        """
        return self.lambda_phi
        
    def create_electron(self, psi_field: PTSField) -> Dict[str, Any]:
        """
        创建电子（ψ场的拓扑孤子，拓扑荷Q=±1）
        
        参数:
            psi_field: PTS场
            
        返回:
            electron: 电子信息
                - field: 电子场（拓扑孤子）
                - charge: 拓扑荷（±1）
                - mass: 质量（与拓扑尺度相关）
        """
        # 检测涡旋（拓扑荷非零）
        vortices = psi_field.detect_vortex()
        
        if len(vortices) == 0:
            return {'error': '未检测到拓扑孤子（电子）'}
            
        # 创建电子场（高斯孤子）
        psi = psi_field.psi
        electron_field = np.zeros_like(psi)
        
        for (i, j) in vortices:
            # 高斯孤子
            x0, y0 = i, j
            x = np.arange(psi_field.grid_size)
            y = np.arange(psi_field.grid_size)
            X, Y = np.meshgrid(x, y)
            
            soliton = np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * self.lambda_phi**2))
            electron_field = electron_field + soliton
            
        # 归一化
        norm = np.sqrt(np.sum(np.abs(electron_field)**2))
        if norm > 1e-10:
            electron_field = electron_field / norm
            
        # 计算拓扑荷
        Q_density = psi_field.compute_topological_charge()
        charge = np.sum(Q_density)  # 总拓扑荷
        
        # 质量（与拓扑尺度相关）
        mass = 1.0 / self.lambda_phi  # 简化模型
        
        return {
            'field': electron_field,
            'charge': charge,
            'mass': mass,
            'vortices': vortices
        }
        
    def create_photon(self, psi_field: PTSField) -> Dict[str, Any]:
        """
        创建光子（ψ场的相干延展模，拓扑荷Q=0）
        
        参数:
            psi_field: PTS场
            
        返回:
            photon: 光子信息
                - field: 光子场（相干延展模）
                - charge: 拓扑荷（0）
                - polarization: 极化（相位梯度方向）
        """
        psi = psi_field.psi
        
        # 光子是相干延展模（拓扑荷为0）
        # 这里简化为平面波
        x = np.linspace(-5, 5, psi_field.grid_size)
        y = np.linspace(-5, 5, psi_field.grid_size)
        X, Y = np.meshgrid(x, y)
        
        # 平面波
        k_x, k_y = 1.0, 1.0  # 波矢
        photon_field = np.exp(1j * (k_x * X + k_y * Y))
        
        # 归一化
        norm = np.sqrt(np.sum(np.abs(photon_field)**2))
        photon_field = photon_field / (norm + 1e-10)
        
        # 拓扑荷（应为0）
        Q_density = psi_field.compute_topological_charge()
        charge = np.sum(Q_density)
        
        # 极化（相位梯度方向）
        phase = np.angle(photon_field)
        grad_phase_y, grad_phase_x = np.gradient(phase, psi_field.dx)
        polarization = np.arctan2(grad_phase_y, grad_phase_x)
        
        return {
            'field': photon_field,
            'charge': charge,
            'polarization': polarization
        }


class PhaseTopologySelfActivation:
    """
    相位拓扑自激模型 - 主控制器
    
    集成所有组件：
    1. PTS场
    2. 波粒二象性
    3. 太极算符
    4. 阴极阳生
    5. QED涌现
    """
    
    def __init__(self, grid_size: int = 100, g: float = 0.1):
        """
        初始化PTS模型
        
        参数:
            grid_size: 网格大小
            g: 自耦合常数
        """
        # 创建PTS场
        self.psi_field = PTSField(grid_size=grid_size)
        
        # 创建组件
        self.wave_particle = WaveParticleDuality(self.psi_field)
        self.taiji = TaijiOperator()
        self.cathode_yang = CathodeYangBirth()
        self.qed = QEDEmergence(g=g)
        
    def simulate_evolution(self, steps: int = 100, dt: float = 0.01) -> List[np.ndarray]:
        """
        模拟ψ场演化
        
        参数:
            steps: 演化步数
            dt: 时间步长
            
        返回:
            trajectory: 演化轨迹（ψ场序列）
        """
        trajectory = [self.psi_field.psi.copy()]
        
        for t in range(steps):
            # 当前ψ场
            psi = self.psi_field.psi
            
            # 演化方程：非线性薛定谔方程（简化）
            # ∂ψ/∂t = -i ∇²ψ + g |ψ|² ψ
            laplacian = laplace(psi)
            nonlinear = self.qed.g * np.abs(psi)**2 * psi
            
            dpsi_dt = -1j * laplacian + nonlinear
            
            # 更新
            psi_new = psi + dpsi_dt * dt
            
            # 归一化
            norm = np.sqrt(np.sum(np.abs(psi_new)**2))
            psi_new = psi_new / (norm + 1e-10)
            
            # 保存
            self.psi_field.psi = psi_new
            trajectory.append(psi_new.copy())
            
        return trajectory
        
    def full_analysis(self) -> Dict[str, Any]:
        """
        完整分析：PTS模型的所有方面
        
        返回:
            analysis: 分析结果
        """
        # 1. 波粒二象性分解
        W, P = self.wave_particle.decompose_wave_particle()
        
        # 2. 干涉图样
        interference = self.wave_particle.compute_interference(W)
        
        # 3. 局域化性质
        localization = self.wave_particle.compute_localization(P)
        
        # 4. 拓扑荷
        Q_density = self.psi_field.compute_topological_charge()
        
        # 5. 涡旋检测
        vortices = self.psi_field.detect_vortex()
        
        # 6. QED涌现
        alpha = self.qed.compute_fine_structure_constant()
        uv_cutoff = self.qed.uv_cutoff()
        
        # 7. 电子和光子
        electron = self.qed.create_electron(self.psi_field)
        photon = self.qed.create_photon(self.psi_field)
        
        analysis = {
            'wave_kernel': W,
            'particle_kernel': P,
            'interference': interference,
            'localization': localization,
            'topological_charge_density': Q_density,
            'vortices': vortices,
            'fine_structure_constant': alpha,
            'uv_cutoff': uv_cutoff,
            'electron': electron,
            'photon': photon
        }
        
        return analysis


# ==================== 测试代码 ====================

def test_phase_topology_self_activation():
    """测试相位拓扑自激模型"""
    print("=" * 60)
    print("🌊 相位拓扑自激模型测试")
    print("=" * 60)
    
    # 1. 初始化
    pts = PhaseTopologySelfActivation(grid_size=50, g=0.1)
    print(f"\n📊 初始化完成")
    print(f"   网格大小: {pts.psi_field.grid_size}")
    print(f"   自耦合常数 g: {pts.qed.g}")
    
    # 2. 波粒二象性分析
    print(f"\n{'='*50}")
    print("波粒二象性分析:")
    print("-" * 50)
    
    analysis = pts.full_analysis()
    
    print(f"   涡旋数量: {len(analysis['vortices'])}")
    print(f"   精细结构常数 α: {analysis['fine_structure_constant']:.6f}")
    print(f"   紫外截断 Λ_φ: {analysis['uv_cutoff']:.4f}")
    
    # 3. 阴极阳生测试
    print(f"\n{'='*50}")
    print("阴极阳生测试:")
    print("-" * 50)
    
    # 创建闭合路径
    contour = [(i, 25) for i in range(20, 30)] + \
              [(30, j) for j in range(25, 35)] + \
              [(i, 35) for i in range(30, 20, -1)] + \
              [(20, j) for j in range(35, 25, -1)]
    
    trigger, winding = pts.cathode_yang.check_critical_condition(
        pts.psi_field, contour
    )
    
    print(f"   缠绕数: {winding:.4f}")
    print(f"   是否触发阴极阳生: {trigger}")
    
    # 4. 太极算符测试
    print(f"\n{'='*50}")
    print("太极算符测试:")
    print("-" * 50)
    
    psi_original = pts.psi_field.psi.copy()
    psi_flipped = pts.taiji.apply(psi_original)
    
    # 检查相位是否旋转了π
    phase_original = np.angle(psi_original[25, 25])
    phase_flipped = np.angle(psi_flipped[25, 25])
    phase_diff = phase_flipped - phase_original
    
    print(f"   原始相位: {phase_original:.4f}")
    print(f"   翻转后相位: {phase_flipped:.4f}")
    print(f"   相位差: {phase_diff:.4f} (期望: {np.pi:.4f})")
    
    # 5. QED涌现测试
    print(f"\n{'='*50}")
    print("QED涌现测试:")
    print("-" * 50)
    
    electron = analysis['electron']
    photon = analysis['photon']
    
    if 'error' not in electron:
        print(f"   电子拓扑荷: {electron['charge']:.4f}")
        print(f"   电子质量: {electron['mass']:.4f}")
        
    print(f"   光子拓扑荷: {photon['charge']:.4f}")
    
    print(f"\n✅ 相位拓扑自激模型测试完成")


if __name__ == "__main__":
    test_phase_topology_self_activation()
