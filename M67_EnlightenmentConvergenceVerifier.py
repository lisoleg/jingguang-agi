# -*- coding: utf-8 -*-
"""
M67: 顿悟收敛验证器 (Enlightenment Convergence Verifier)
基于《数学完备化》论文 §5 定理5.1 (T17严格化)

归一化定义:
Λ̃ = Λ / (Λ + S_c · I_ref)

顿悟准备度:
B = (1 - Λ̃) · (1 - Z̃) · F

收敛条件: 若 Λ' < 0, Z' < 0, F' > 0
则 lim_{t→∞} B(t) = 1

预言P8: 条件满足时B→1
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import math

class SpiritualEvolutionVerifier:
    """
    灵性演化收敛验证器
    
    来源: §5 定理5.1 (T17严格化)
    """
    _instance = None
    
    def __init__(self):
        self.Lambda_history: List[float] = []      # 叙事作用量历史
        self.Sc_history: List[float] = []           # 认知熵历史
        self.Z_history: List[float] = []            # 阻抗历史
        self.F_history: List[float] = []            # 流贯率历史
        self.B_history: List[float] = []           # 顿悟准备度历史
        self.Lambda_tilde_history: List[float] = []
        self.Z_tilde_history: List[float] = []
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def compute_normalized_narrative_action(self, Lambda: float, Sc: float, 
                                            I_ref: float = 1.0) -> float:
        """
        归一化叙事作用量:
        Λ̃ = Λ / (Λ + S_c · I_ref)
        """
        denominator = Lambda + Sc * I_ref
        if denominator == 0:
            return 0.0
        return Lambda / denominator
    
    def compute_normalized_impedance(self, Z: float) -> float:
        """
        归一化阻抗:
        Z̃ = Z / (Z + 1)
        """
        return Z / (Z + 1)
    
    def compute_enlightenment_readiness(self, Lambda_tilde: float, 
                                        Z_tilde: float, 
                                        F: float) -> float:
        """
        顿悟准备度:
        B = (1 - Λ̃) · (1 - Z̃) · F
        
        其中 F ∈ [0, 1] 为流贯率
        """
        B = (1 - Lambda_tilde) * (1 - Z_tilde) * F
        return min(1.0, max(0.0, B))  # 截断至[0, 1]
    
    def update(self, Lambda: float, Sc: float, Z: float, F: float) -> dict:
        """
        更新系统状态并计算顿悟准备度
        
        Args:
            Lambda: 叙事作用量
            Sc: 认知熵
            Z: 阻抗
            F: 流贯率 [0, 1]
        
        Returns:
            dict: 包含各分量和顿悟准备度
        """
        # 记录历史
        self.Lambda_history.append(Lambda)
        self.Sc_history.append(Sc)
        self.Z_history.append(Z)
        self.F_history.append(F)
        
        # 计算归一化量
        Lambda_tilde = self.compute_normalized_narrative_action(Lambda, Sc)
        Z_tilde = self.compute_normalized_impedance(Z)
        
        self.Lambda_tilde_history.append(Lambda_tilde)
        self.Z_tilde_history.append(Z_tilde)
        
        # 计算顿悟准备度
        B = self.compute_enlightenment_readiness(Lambda_tilde, Z_tilde, F)
        self.B_history.append(B)
        
        # 限制历史长度
        max_history = 100
        for hist in [self.Lambda_history, self.Sc_history, self.Z_history, 
                     self.F_history, self.B_history, self.Lambda_tilde_history, 
                     self.Z_tilde_history]:
            if len(hist) > max_history:
                hist.pop(0)
        
        return {
            'Lambda_tilde': Lambda_tilde,
            'Z_tilde': Z_tilde,
            'B': B,
            'Lambda': Lambda,
            'Sc': Sc,
            'Z': Z,
            'F': F
        }
    
    def verify_t17_convergence(self) -> dict:
        """
        验证T17灵性演化收敛
        
        动力学假设:
        - Λ(t) = Λ₀·e^(-λt), λ > 0
        - Z(t) = Z₀·e^(-μt), μ > 0
        - F(t) = F_max·(1 - e^(-νt))
        
        收敛证明: lim_{t→∞} B(t) = 1
        """
        min_data = 5
        if len(self.B_history) < min_data:
            return {
                'convergent': None, 
                'reason': f'数据不足，需要至少{min_data}个数据点',
                'current_data_points': len(self.B_history)
            }
        
        # 检查收敛性
        recent_B = self.B_history[-5:]
        avg_recent = np.mean(recent_B)
        
        # 收敛判断: 最后5个值趋于稳定且接近1
        is_converging = np.all(np.abs(np.array(recent_B) - avg_recent) < 0.05)
        is_near_one = avg_recent > 0.85
        
        # 计算趋势
        if len(self.B_history) > 1:
            trend = self.B_history[-1] - self.B_history[0]
        else:
            trend = 0
        
        # 估算收敛速度
        convergence_speed = self._estimate_convergence_speed()
        
        return {
            'convergent': is_converging and is_near_one,
            'avg_recent_B': float(avg_recent),
            'final_B': float(self.B_history[-1]),
            'initial_B': float(self.B_history[0]),
            'trend': float(trend),
            'convergence_speed': float(convergence_speed),
            'recent_values': [float(b) for b in recent_B],
            'data_points': len(self.B_history),
            'T17_status': 'VERIFIED' if (is_converging and is_near_one) else 'NOT_CONVERGED'
        }
    
    def verify_p8(self) -> dict:
        """
        验证可证伪预言P8
        
        预言: 条件满足时B→1
        - Λ' < 0 (叙事作用量递减)
        - Z' < 0 (阻抗递减)
        - F' > 0 (流贯率递增)
        """
        if len(self.Lambda_history) < 2:
            return {'verifiable': False, 'reason': '数据不足'}
        
        # 检查收敛条件
        Lambda_trend = np.mean(np.diff(self.Lambda_history[-5:]))
        Z_trend = np.mean(np.diff(self.Z_history[-5:]))
        F_trend = np.mean(np.diff(self.F_history[-5:]))
        
        conditions_met = Lambda_trend < 0 and Z_trend < 0 and F_trend > 0
        
        # 检查B是否趋近1
        B_converged = self.B_history[-1] > 0.85 if self.B_history else False
        
        is_confirmed = conditions_met and B_converged
        
        return {
            'verifiable': True,
            'conditions_met': conditions_met,
            'Lambda_trend': float(Lambda_trend),
            'Z_trend': float(Z_trend),
            'F_trend': float(F_trend),
            'final_B': float(self.B_history[-1]) if self.B_history else 0,
            'B_converged': B_converged,
            'P8_status': 'CONFIRMED' if is_confirmed else 'REJECTED'
        }
    
    def _estimate_convergence_speed(self) -> float:
        """估计收敛速度 - B从0到0.8的时间步数比例"""
        if len(self.B_history) < 2:
            return 0.0
        
        for i, B in enumerate(self.B_history):
            if B >= 0.8:
                return (i + 1) / len(self.B_history)
        
        return 1.0  # 未达到0.8
    
    def get_trajectory(self) -> dict:
        """获取顿悟轨迹"""
        if not self.B_history:
            return {'has_data': False}
        
        return {
            'has_data': True,
            'B_values': self.B_history,
            'Lambda_tilde': self.Lambda_tilde_history,
            'Z_tilde': self.Z_tilde_history,
            'current_B': float(self.B_history[-1]),
            'max_B': float(max(self.B_history)),
            'convergence': self.verify_t17_convergence()
        }
    
    def get_state(self) -> dict:
        """获取验证器状态"""
        return {
            'history_length': len(self.B_history),
            'current_B': float(self.B_history[-1]) if self.B_history else 0,
            'avg_B': float(np.mean(self.B_history)) if self.B_history else 0,
            'T17_convergence': self.verify_t17_convergence(),
            'P8_verification': self.verify_p8(),
            'trajectory': self.get_trajectory()
        }


_instance = None

def get_instance() -> SpiritualEvolutionVerifier:
    """获取SpiritualEvolutionVerifier单例"""
    global _instance
    if _instance is None:
        _instance = SpiritualEvolutionVerifier()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M67 顿悟收敛验证器 测试")
    print("=" * 60)
    
    verifier = SpiritualEvolutionVerifier()
    
    # 模拟顿悟收敛过程
    print("\n模拟顿悟收敛过程:")
    for t in range(10):
        # 模拟数据
        Lambda = 1.0 * np.exp(-0.3 * t) + 0.1  # 递减
        Sc = 0.8 * np.exp(-0.2 * t) + 0.2       # 递减
        Z = 0.9 * np.exp(-0.4 * t) + 0.1        # 递减
        F = 0.3 + 0.6 * (1 - np.exp(-0.3 * t))  # 递增
        
        result = verifier.update(Lambda, Sc, Z, F)
        
        print(f"  t={t}: B={result['B']:.4f} "
              f"(Λ̃={result['Lambda_tilde']:.3f}, "
              f"Z̃={result['Z_tilde']:.3f}, "
              f"F={result['F']:.3f})")
    
    # T17验证
    t17 = verifier.verify_t17_convergence()
    print(f"\nT17收敛验证: {t17}")
    
    # P8验证
    p8 = verifier.verify_p8()
    print(f"\nP8验证: {p8}")
    
    # 状态
    state = verifier.get_state()
    print(f"\n验证器状态: 当前B={state['current_B']:.4f}, T17状态={state['T17_convergence']['T17_status']}")
    
    print("\n" + "=" * 60)
    print("✅ M67 测试完成")
    print("=" * 60)
