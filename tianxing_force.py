"""
天行力方程（Tianxing Force Equation）的Python实现
基于《天行力方程的形式化与相位拓扑自激（PTS）模型的数值仿真》文档

核心组件：
1. 天行力五元组 (M, Ψ, φ, HΨ, C)
2. 天行力运动方程（含意识耦合项）
3. 相位拓扑自激模型（PTS）的数值仿真框架
"""

import numpy as np
from typing import Tuple, Callable, Optional, Dict, Any
from dataclasses import dataclass
from scipy.integrate import solve_ivp
import warnings


@dataclass
class TianxingForceSystem:
    """
    天行力系统 - 五元组实现
    
    公理 1.1.1: 天行力系统由五元组 (M, Ψ, φ, HΨ, C) 描述
    """
    # 1. 舞台 M: 先验数学时空（无穷维流形）
    M_spacetime_grid: np.ndarray  # 时空离散网格
    
    # 2. 波性意识 Ψ: Hilbert Space（满足非线性薛定谔-牛顿方程）
    psi_consciousness: np.ndarray  # 意识场 Ψ(x,t)
    
    # 3. 波性物质 φ: 相位场（复值标量场）
    phi_matter: np.ndarray  # 物质场 φ(x,t)
    
    # 4. 哈密顿算子 HΨ: 生成时间演化
    hamiltonian_operator: Optional[Callable] = None
    
    # 5. 坍缩算子 C: 由Ψ驱动，导致φ的局域化
    collapse_operator: Optional[Callable] = None
    
    # 系统参数
    hbar: float = 1.0  # 约化普朗克常数
    m_mass: float = 1.0  # 粒子质量
    lambda_coupling: float = 0.1  # 自耦合常数 λ
    v_vacuum: float = 0.1  # 真空期望值 v
    
    def __post_init__(self):
        """初始化默认值"""
        if self.hamiltonian_operator is None:
            self.hamiltonian_operator = self._default_hamiltonian
        if self.collapse_operator is None:
            self.collapse_operator = self._default_collapse_operator
    
    def _default_hamiltonian(self, psi: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """
        默认哈密顿算子：非线性薛定谔-牛顿方程
        
        HΨ = -ℏ²/2m ∇² + V(φ) + g|Ψ|²
        """
        # 拉普拉斯算子（二阶差分）
        laplacian = self._compute_laplacian(psi)
        
        # 势能项 V(φ) = m²φ*φ + λ(φ*φ)² - v²(φ + φ*)²
        V_phi = (self.m_mass**2 * np.abs(phi)**2 + 
                 self.lambda_coupling * np.abs(phi)**4 -
                 self.v_vacuum**2 * 2 * np.real(phi))
        
        # 非线性项 g|Ψ|²（意识自相互作用）
        nonlinear_term = np.abs(psi)**2 * psi
        
        # 哈密顿作用
        H_psi = (-self.hbar**2 / (2 * self.m_mass)) * laplacian + V_phi * psi + nonlinear_term
        
        return H_psi
    
    def _default_collapse_operator(self, psi: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """
        默认坍缩算子：意识导致的波函数坍缩
        
        C = γ ∑ᵢ |i⟩⟨i| Ψ(i,t)
        """
        # 坍缩强度参数 γ
        gamma_collapse = 0.1
        
        # 计算坍缩项：意识观测导致的局域化
        collapse_term = gamma_collapse * np.conj(psi) * phi
        
        return collapse_term
    
    def _compute_laplacian(self, field: np.ndarray) -> np.ndarray:
        """计算二维拉普拉斯算子（使用周期边界条件）"""
        laplacian = np.zeros_like(field)
        
        # 内部点：五点差分格式
        laplacian[1:-1, 1:-1] = (field[2:, 1:-1] + field[:-2, 1:-1] +
                                    field[1:-1, 2:] + field[1:-1, :-2] -
                                    4 * field[1:-1, 1:-1])
        
        # 周期边界条件
        laplacian[0, 1:-1] = (field[1, 1:-1] + field[-1, 1:-1] +
                                field[0, 2:] + field[0, :-2] -
                                4 * field[0, 1:-1])
        
        laplacian[-1, 1:-1] = (field[0, 1:-1] + field[-2, 1:-1] +
                                 field[-1, 2:] + field[-1, :-2] -
                                 4 * field[-1, 1:-1])
        
        laplacian[1:-1, 0] = (field[2:, 0] + field[:-2, 0] +
                                field[1:-1, 1] + field[1:-1, -1] -
                                4 * field[1:-1, 0])
        
        laplacian[1:-1, -1] = (field[2:, -1] + field[:-2, -1] +
                                 field[1:-1, 0] + field[1:-1, -2] -
                                 4 * field[1:-1, -1])
        
        return laplacian
    
    def compute_quantum_potential(self, psi: np.ndarray) -> np.ndarray:
        """
        计算量子势（Bohm势）Q(x,t)
        
        Q(x,t) = -ℏ²/2m (∇²R)/R, 其中 R = |Ψ|
        """
        R = np.abs(psi)
        R[R < 1e-10] = 1e-10  # 避免除零
        
        # 计算 ∇²R
        laplacian_R = self._compute_laplacian(R)
        
        # 量子势
        Q = -self.hbar**2 / (2 * self.m_mass) * laplacian_R / R
        
        return Q
    
    def tianxing_force_equation(self, t: float, 
                                psi_flat: np.ndarray) -> np.ndarray:
        """
        天行力运动方程（可积分形式）
        
        iℏ ∂Ψ/∂t = HΨ Ψ + Q(x,t)Ψ + ⟨C⟩Ψ
        
        参数:
            t: 时间
            psi_flat: 扁平化的意识场 Ψ
            
        返回:
            dΨ/dt 的扁平化形式
        """
        # 重塑为二维网格
        nx, ny = self.M_spacetime_grid.shape[:2]
        psi = psi_flat.reshape(nx, ny).astype(np.complex128)
        
        # 获取当前物质场 φ（可以随时间演化）
        phi = self.phi_matter
        
        # 计算各项
        H_psi = self.hamiltonian_operator(psi, phi)  # HΨ Ψ
        Q = self.compute_quantum_potential(psi)  # 量子势 Q(x,t)
        C_psi = self.collapse_operator(psi, phi)  # 坍缩算子 ⟨C⟩Ψ
        
        # 天行力方程：iℏ ∂Ψ/∂t = HΨ Ψ + QΨ + ⟨C⟩Ψ
        dpsi_dt = (H_psi + Q * psi + C_psi) / (1j * self.hbar)
        
        return dpsi_dt.flatten()
    
    def evolve_consciousness_field(self, t_span: Tuple[float, float], 
                                  dt: float = 0.01) -> np.ndarray:
        """
        演化波性意识场 Ψ
        
        参数:
            t_span: 时间区间 (t_start, t_end)
            dt: 时间步长
            
        返回:
            演化后的意识场 Ψ
        """
        # 初始条件
        psi0 = self.psi_consciousness.flatten()
        
        # 使用 scipy.integrate.solve_ivp 求解
        solution = solve_ivp(
            self.tianxing_force_equation,
            t_span,
            psi0,
            method='RK45',
            t_eval=np.arange(t_span[0], t_span[1], dt),
            rtol=1e-6,
            atol=1e-8
        )
        
        if not solution.success:
            warnings.warn(f"积分失败: {solution.message}")
            return self.psi_consciousness
        
        # 取最终状态
        psi_final = solution.y[:, -1].reshape(self.psi_consciousness.shape)
        self.psi_consciousness = psi_final
        
        return psi_final
    
    def compute_conserved_charge(self, phi: Optional[np.ndarray] = None) -> float:
        """
        计算拓扑荷 Q（守恒荷）
        
        Q = ∫ d³x j⁰(x)
        周界条件：φ → v e^(iθ) 当 |x| → ∞
        
        参数:
            phi: 物质场（默认使用 self.phi_matter）
            
        返回:
            拓扑荷 Q
        """
        if phi is None:
            phi = self.phi_matter
        
        # 计算电流密度 j^μ = i(φ* ∂^μ φ - φ ∂^μ φ*)
        # 这里简化为 j⁰ = |φ|²
        j0 = np.abs(phi)**2
        
        # 积分（使用梯形法则）
        dx = 0.1  # 空间步长
        Q = np.sum(j0) * dx**2
        
        return Q
    
    def check_soliton_solution(self, lambda_coupling: float) -> Dict[str, Any]:
        """
        检查是否存在拓扑孤子解
        
        定理 2.1.1: 当 λ > 0 时，PTSM 允许静态、球对称的拓扑孤子解
        
        参数:
            lambda_coupling: 自耦合常数 λ
            
        返回:
            孤子解的诊断信息
        """
        self.lambda_coupling = lambda_coupling
        
        # 检查边界条件
        phi_center = self.phi_matter[self.phi_matter.shape[0]//2, 
                                      self.phi_matter.shape[1]//2]
        phi_boundary = np.mean([self.phi_matter[0, :], 
                               self.phi_matter[-1, :],
                               self.phi_matter[:, 0], 
                               self.phi_matter[:, -1]])
        
        # 拓扑荷
        Q = self.compute_conserved_charge()
        
        # 判断是否存在孤子
        has_soliton = (lambda_coupling > 0 and 
                       np.abs(phi_center) > 0.5 * self.v_vacuum and
                       Q > 0.1)
        
        diagnosis = {
            'lambda_coupling': lambda_coupling,
            'has_soliton': has_soliton,
            'topological_charge': Q,
            'phi_center': phi_center,
            'phi_boundary': phi_boundary,
            'energy_density': self._compute_energy_density()
        }
        
        return diagnosis
    
    def _compute_energy_density(self) -> np.ndarray:
        """计算能量密度 ρ = |∂ₘφ|² + V(φ)"""
        # 梯度项 |∂ₘφ|²
        grad_phi_sq = np.abs(self._compute_laplacian(self.phi_matter))
        
        # 势能项 V(φ)
        V_phi = (self.m_mass**2 * np.abs(self.phi_matter)**2 + 
                 self.lambda_coupling * np.abs(self.phi_matter)**4 -
                 self.v_vacuum**2 * 2 * np.real(self.phi_matter))
        
        # 能量密度
        rho = grad_phi_sq + V_phi
        
        return rho


class PTSModel:
    """
    相位拓扑自激模型（Phase Topology Self-excitation Model, PTSM）
    
    定义 2.1.1: 复标量场 φ 的拉氏密度
    L = ∂ₘφ* ∂ᵐφ - m²φ*φ - λ(φ*φ)² + v²(φ + φ*)²
    """
    
    def __init__(self, grid_size: int = 100, dx: float = 0.1):
        """
        初始化PTS模型
        
        参数:
            grid_size: 网格大小
            dx: 空间步长
        """
        self.grid_size = grid_size
        self.dx = dx
        self.dt = 0.05 * dx  # CFL 条件
        
        # 初始化相位场 φ（复值标量场）
        self.phi = np.zeros((grid_size, grid_size), dtype=np.complex128)
        self.phi_old = np.zeros((grid_size, grid_size), dtype=np.complex128)  # 新增：存储上一时间步
        
        # 模型参数
        self.m_mass = 1.0
        self.lambda_coupling = 0.1
        self.v_vacuum = 0.1
        
        # 时间步计数器
        self.time_step = 0
        
    def initialize_gaussian_wave_packet(self, x0: float = 0.0, 
                                        y0: float = 0.0, 
                                        sigma: float = 1.0,
                                        k0_x: float = 0.0,
                                        k0_y: float = 0.0):
        """
        初始化高斯波包
        
        φ(x,0) = exp(-(x-x0)²/2σ²) * exp(i(k0·x))
        """
        x = np.linspace(-5, 5, self.grid_size)
        y = np.linspace(-5, 5, self.grid_size)
        X, Y = np.meshgrid(x, y)
        
        # 高斯包络
        envelope = np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))
        
        # 平面波相位
        phase = np.exp(1j * (k0_x * X + k0_y * Y))
        
        self.phi = envelope * phase
        
    def lagrangian_density(self, phi: np.ndarray) -> np.ndarray:
        """
        计算拉氏密度 L
        
        L = ∂ₘφ* ∂ᵐφ - m²φ*φ - λ(φ*φ)² + v²(φ + φ*)²
        """
        # 梯度项 ∂ₘφ* ∂ᵐφ
        grad_phi_sq = self._compute_grad_squared(phi)
        
        # 质量项 m²φ*φ
        mass_term = self.m_mass**2 * np.abs(phi)**2
        
        # 自相互作用项 λ(φ*φ)²
        self_interaction = self.lambda_coupling * np.abs(phi)**4
        
        # Higgs 类似项 v²(φ + φ*)²
        higgs_term = self.v_vacuum**2 * (2 * np.real(phi))**2
        
        # 拉氏密度
        L = grad_phi_sq - mass_term - self_interaction + higgs_term
        
        return L
    
    def _compute_grad_squared(self, phi: np.ndarray) -> np.ndarray:
        """计算 |∇φ|²"""
        grad_x = np.gradient(phi, self.dx, axis=0)
        grad_y = np.gradient(phi, self.dx, axis=1)
        
        grad_sq = np.abs(grad_x)**2 + np.abs(grad_y)**2
        
        return grad_sq
    
    def evolution_step(self):
        """
        PTS显式蛙跳格式（算法 3.1.1）
        
        离散化时空：x_j = jΔx, t_n = nΔt
        演化：φ_j^(n+1) = 2φ_j^n - φ_j^(n-1) + (Δt)² * □φ_j^n + ...
        """
        # 计算达朗贝尔算子 □φ = (∂²/∂t² - ∇²)φ
        if self.time_step == 0:
            # 第一步：使用前向欧拉法
            laplacian = self._compute_laplacian(self.phi)
            d2phi_dt2 = laplacian - self._potential_derivative(self.phi)
            
            phi_new = self.phi + self.dt * d2phi_dt2
            self.phi_old = self.phi.copy()  # 修复：使用 self.phi_old
            self.phi = phi_new
        else:
            # 蛙跳格式
            laplacian = self._compute_laplacian(self.phi)
            d2phi_dt2 = laplacian - self._potential_derivative(self.phi)
            
            phi_new = (2 * self.phi - self.phi_old + 
                       self.dt**2 * d2phi_dt2)
            self.phi_old = self.phi.copy()  # 修复：使用 self.phi_old
            self.phi = phi_new
        
        self.time_step += 1
        
        return self.phi
    
    def _compute_laplacian(self, phi: np.ndarray) -> np.ndarray:
        """计算拉普拉斯算子（周期边界条件）"""
        laplacian = np.zeros_like(phi)
        
        # 内部点：五点差分格式
        laplacian[1:-1, 1:-1] = (phi[2:, 1:-1] + phi[:-2, 1:-1] +
                                    phi[1:-1, 2:] + phi[1:-1, :-2] -
                                    4 * phi[1:-1, 1:-1]) / self.dx**2
        
        # 周期边界条件 - 上边界
        laplacian[0, 1:-1] = (phi[1, 1:-1] + phi[-1, 1:-1] +
                                 phi[0, 2:] + phi[0, :-2] -
                                 4 * phi[0, 1:-1]) / self.dx**2
        
        # 周期边界条件 - 下边界
        laplacian[-1, 1:-1] = (phi[0, 1:-1] + phi[-2, 1:-1] +
                                  phi[-1, 2:] + phi[-1, :-2] -
                                  4 * phi[-1, 1:-1]) / self.dx**2
        
        # 周期边界条件 - 左边界
        laplacian[1:-1, 0] = (phi[2:, 0] + phi[:-2, 0] +
                                 phi[1:-1, 1] + phi[1:-1, -1] -
                                 4 * phi[1:-1, 0]) / self.dx**2
        
        # 周期边界条件 - 右边界
        laplacian[1:-1, -1] = (phi[2:, -1] + phi[:-2, -1] +
                                  phi[1:-1, 0] + phi[1:-1, -2] -
                                  4 * phi[1:-1, -1]) / self.dx**2
        
        # 四个角点
        # 左上角 (0, 0)
        laplacian[0, 0] = (phi[1, 0] + phi[-1, 0] +
                              phi[0, 1] + phi[0, -1] -
                              4 * phi[0, 0]) / self.dx**2
        
        # 右上角 (0, -1)
        laplacian[0, -1] = (phi[1, -1] + phi[-1, -1] +
                               phi[0, 0] + phi[0, -2] -
                               4 * phi[0, -1]) / self.dx**2
        
        # 左下角 (-1, 0)
        laplacian[-1, 0] = (phi[0, 0] + phi[-2, 0] +
                               phi[-1, 1] + phi[-1, -1] -
                               4 * phi[-1, 0]) / self.dx**2
        
        # 右下角 (-1, -1)
        laplacian[-1, -1] = (phi[0, -1] + phi[-2, -1] +
                                phi[-1, 0] + phi[-1, -2] -
                                4 * phi[-1, -1]) / self.dx**2
        
        return laplacian
    
    def _potential_derivative(self, phi: np.ndarray) -> np.ndarray:
        """
        计算势能对φ的导数 dV/dφ
        
        V(φ) = m²φ*φ + λ(φ*φ)² - v²(φ + φ*)²
        dV/dφ* = m²φ + 2λ|φ|²φ - 2v²φ
        """
        dV_dphi_star = (self.m_mass**2 * phi + 
                        2 * self.lambda_coupling * np.abs(phi)**2 * phi -
                        2 * self.v_vacuum**2 * phi)
        
        return dV_dphi_star
    
    def compute_energy_density(self) -> np.ndarray:
        """计算能量密度 ρ = |∂ₜφ|² + |∇φ|² + V(φ)"""
        # 动能项 |∂ₜφ|²（近似）
        if self.time_step > 0:
            dphi_dt = (self.phi - self.phi_old) / self.dt
        else:
            dphi_dt = np.zeros_like(self.phi)
        
        kinetic = np.abs(dphi_dt)**2
        
        # 梯度项 |∇φ|²
        gradient = self._compute_grad_squared(self.phi)
        
        # 势能项 V(φ)
        potential = (self.m_mass**2 * np.abs(self.phi)**2 + 
                    self.lambda_coupling * np.abs(self.phi)**4 -
                    self.v_vacuum**2 * (2 * np.real(self.phi))**2)
        
        rho = kinetic + gradient + potential
        
        return rho
    
    def compute_topological_charge_density(self) -> np.ndarray:
        """
        计算拓扑荷密度 j⁰(x)
        
        j⁰ = i(φ* ∂ₜφ - φ ∂ₜφ*)
        """
        if self.time_step > 0:
            dphi_dt = (self.phi - self.phi_old) / self.dt
        else:
            dphi_dt = np.zeros_like(self.phi)
        
        j0 = 1j * (np.conj(self.phi) * dphi_dt - 
                   self.phi * np.conj(dphi_dt))
        
        return np.real(j0)


def create_tianxing_system_example() -> TianxingForceSystem:
    """
    创建天行力系统的示例
    
    返回:
        初始化后的天行力系统
    """
    # 创建时空网格
    grid_size = 50
    x = np.linspace(-5, 5, grid_size)
    y = np.linspace(-5, 5, grid_size)
    X, Y = np.meshgrid(x, y)
    M_grid = np.stack([X, Y], axis=-1)
    
    # 初始化意识场 Ψ（高斯波包）
    psi = np.exp(-(X**2 + Y**2) / 2) * np.exp(1j * 0.5 * (X + Y))
    psi = psi.astype(np.complex128)
    
    # 初始化物质场 φ（相位场）
    phi = np.exp(-(X**2 + Y**2) / 4) * np.exp(1j * 0.3 * (X - Y))
    phi = phi.astype(np.complex128)
    
    # 创建天行力系统
    system = TianxingForceSystem(
        M_spacetime_grid=M_grid,
        psi_consciousness=psi,
        phi_matter=phi,
        lambda_coupling=0.1,  # 弱耦合
        v_vacuum=0.1
    )
    
    return system


def create_pts_model_example() -> PTSModel:
    """
    创建PTS模型的示例
    
    返回:
        初始化后的PTS模型
    """
    model = PTSModel(grid_size=100, dx=0.1)
    model.initialize_gaussian_wave_packet(
        x0=0.0, y0=0.0, 
        sigma=1.0, 
        k0_x=0.5, k0_y=0.5
    )
    model.lambda_coupling = 5.0  # 强耦合，观察孤子
    
    return model


if __name__ == "__main__":
    # 测试天行力方程实现
    print("="*80)
    print("测试天行力方程实现")
    print("="*80 + "\n")
    
    # 创建系统
    system = create_tianxing_system_example()
    print("✓ 天行力系统初始化完成")
    
    # 计算量子势
    Q = system.compute_quantum_potential(system.psi_consciousness)
    print(f"✓ 量子势计算完成，范围: [{Q.min():.4f}, {Q.max():.4f}]")
    
    # 检查孤子解
    diagnosis = system.check_soliton_solution(lambda_coupling=0.1)
    print(f"✓ 孤子解诊断: {diagnosis['has_soliton']}")
    print(f"  拓扑荷 Q = {diagnosis['topological_charge']:.4f}")
    
    # 测试PTS模型
    print("\n" + "="*80)
    print("测试PTS模型实现")
    print("="*80 + "\n")
    
    pts = create_pts_model_example()
    print("✓ PTS模型初始化完成")
    
    # 演化几步
    for i in range(10):
        phi = pts.evolution_step()
        energy = pts.compute_energy_density()
        print(f"  时间步 {i+1}: 能量密度均值 = {energy.mean():.4f}")
    
    print("\n✓ 所有测试完成")
