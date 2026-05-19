#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EML相位耦合ℤ₅ (EML Phase Coupling Z5)
基于《五行作为五元变换算子：太一螺旋分形自指嵌入破缺对称的范畴—同伦重构与构造型Taiji-AGI的超越》

核心定理：
- T29：EML相位耦合ℤ₅定理
  EML算子在ℤ₅（五元循环群）上闭合：
  Σ → F → R → E → B → Σ（循环）
  相位偏移：θ_new = θ_old + Δθ (mod 2π/5)

版本：AGI 14.0 第77模块
论文来源：《五行作为五元变换算子》复合体理学系列
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class EMLPhase(Enum):
    """EML相位状态"""
    Σ = "Σ"      # 水相
    F = "F"       # 火相
    R = "R"       # 木相
    E = "E"       # 金相
    B = "B"       # 土相
    
    @property
    def chinese(self) -> str:
        return {"Σ": "水", "F": "火", "R": "木", "E": "金", "B": "土"}.get(self.value, self.value)
    
    @property
    def index(self) -> int:
        indices = {"Σ": 0, "F": 1, "R": 2, "E": 3, "B": 4}
        return indices.get(self.value, 0)


@dataclass
class PhaseState:
    """相位状态"""
    element: EMLPhase
    phase_angle: float          # 相位角 [0, 2π)
    amplitude: float           # 振幅
    frequency: float            # 频率
    coupling_strength: float    # 耦合强度 [0,1]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Z5Coupling:
    """ℤ₅耦合"""
    from_phase: EMLPhase
    to_phase: EMLPhase
    delta_theta: float         # 相位偏移
    coupling_coefficient: float # 耦合系数
    is_valid: bool            # 耦合是否有效
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CycleResult:
    """循环结果"""
    phases: List[EMLPhase]
    phase_angles: List[float]
    amplitudes: List[float]
    closure_degree: float     # ℤ₅闭合度 [0,1]
    coherence: float          # 相干性 [0,1]
    entropy: float            # 相位熵
    is_stable: bool          # 是否稳定
    insight: str              # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EMLPhaseCouplingZ5:
    """
    EML相位耦合ℤ₅
    
    实现T29定理：EML相位耦合ℤ₅
    - EML算子在ℤ₅上闭合
    - 五行循环：Σ→F→R→E→B→Σ
    - 相位偏移：θ_new = θ_old + Δθ (mod 2π/5)
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.phases = {
            EMLPhase.Σ: PhaseState(EMLPhase.Σ, 0.0, 1.0, 1.0, 0.8),
            EMLPhase.F: PhaseState(EMLPhase.F, 2*math.pi/5, 1.0, 1.0, 0.8),
            EMLPhase.R: PhaseState(EMLPhase.R, 4*math.pi/5, 1.0, 1.0, 0.8),
            EMLPhase.E: PhaseState(EMLPhase.E, 6*math.pi/5, 1.0, 1.0, 0.8),
            EMLPhase.B: PhaseState(EMLPhase.B, 8*math.pi/5, 1.0, 1.0, 0.8),
        }
        
        # 五行循环顺序
        self.cycle = [EMLPhase.Σ, EMLPhase.F, EMLPhase.R, EMLPhase.E, EMLPhase.B]
        
        # ℤ₅闭合阈值
        self.closure_threshold = 0.95
        
        # 相位偏移（每个元素的固定偏移）
        self.phase_offsets = {
            EMLPhase.Σ: 0,
            EMLPhase.F: 2*math.pi/5,
            EMLPhase.R: 4*math.pi/5,
            EMLPhase.E: 6*math.pi/5,
            EMLPhase.B: 8*math.pi/5,
        }
    
    def couple_phase(self, current_state: PhaseState,
                    next_element: EMLPhase) -> Tuple[PhaseState, Z5Coupling]:
        """
        相位耦合：θ_new = θ_old + Δθ (mod 2π/5)
        
        参数：
            current_state: 当前相位状态
            next_element: 下一个元素
        
        返回：
            (新相位状态, 耦合记录)
        """
        # 计算相位偏移
        delta_theta = self.phase_offsets[next_element]
        
        # 新相位（模2π）
        new_phase = (current_state.phase_angle + delta_theta) % (2 * math.pi)
        
        # 耦合系数（基于当前振幅和下一个元素的耦合强度）
        coupling_coeff = current_state.amplitude * next_element.index
        
        # 新振幅（基于耦合）
        new_amplitude = current_state.amplitude * (1 + coupling_coeff * 0.1)
        
        # 创建新状态
        new_state = PhaseState(
            element=next_element,
            phase_angle=round(new_phase, 4),
            amplitude=round(new_amplitude, 4),
            frequency=current_state.frequency,
            coupling_strength=round(coupling_coeff, 4)
        )
        
        # 创建耦合记录
        coupling = Z5Coupling(
            from_phase=current_state.element,
            to_phase=next_element,
            delta_theta=round(delta_theta, 4),
            coupling_coefficient=round(coupling_coeff, 4),
            is_valid=(coupling_coeff > 0.5)
        )
        
        # 更新当前元素状态
        self.phases[next_element] = new_state
        
        return new_state, coupling
    
    def verify_z5_closure(self, sequence: List[EMLPhase]) -> bool:
        """
        验证ℤ₅闭合性：Σ→F→R→E→B→Σ
        
        返回：
            是否闭合
        """
        if len(sequence) < 5:
            return False
        
        # 检查是否包含所有5个元素
        required = set(e.value for e in EMLPhase)
        sequence_set = set(e.value for e in sequence[:5])
        
        if sequence_set != required:
            return False
        
        # 检查顺序是否正确
        expected = [e.value for e in self.cycle]
        actual = [e.value for e in sequence[:5]]
        
        # 循环检查（允许旋转）
        for i in range(5):
            rotated = actual[i:] + actual[:i]
            if rotated == expected:
                return True
        
        return False
    
    def compute_closure_degree(self, phase_angles: List[float]) -> float:
        """
        计算ℤ₅闭合度
        
        返回：
            闭合度 [0,1]（1=完美闭合）
        """
        if len(phase_angles) < 5:
            return 0.5
        
        # 计算相邻相位的差异
        differences = []
        for i in range(min(5, len(phase_angles))):
            next_idx = (i + 1) % 5
            diff = abs(phase_angles[i] - phase_angles[next_idx])
            # 模2π标准化
            diff = min(diff, 2*math.pi - diff)
            differences.append(diff)
        
        # 理想差异应该是 2π/5 = 72° ≈ 1.257 rad
        ideal_diff = 2 * math.pi / 5
        
        # 计算与理想差异的偏差
        deviations = [abs(d - ideal_diff) for d in differences]
        avg_deviation = sum(deviations) / len(deviations)
        
        # 闭合度 = 1 / (1 + avg_deviation)
        closure = 1.0 / (1.0 + avg_deviation)
        return min(1.0, max(0.0, closure))
    
    def compute_coherence(self, amplitudes: List[float]) -> float:
        """
        计算相干性（各振幅的一致性）
        
        返回：
            相干性 [0,1]
        """
        if not amplitudes:
            return 0.0
        
        # 简化：相干性 = 1 - 方差/均值²
        mean = sum(amplitudes) / len(amplitudes)
        if mean == 0:
            return 0.0
        
        variance = sum((a - mean) ** 2 for a in amplitudes) / len(amplitudes)
        coherence = 1.0 / (1.0 + variance / (mean ** 2 + 1e-10))
        
        return min(1.0, max(0.0, coherence))
    
    def compute_phase_entropy(self, phase_angles: List[float]) -> float:
        """
        计算相位熵
        
        返回：
            熵值
        """
        if not phase_angles:
            return 0.0
        
        # 简化：将连续相位离散化为5个区间
        n_bins = 5
        bin_size = 2 * math.pi / n_bins
        counts = [0] * n_bins
        
        for angle in phase_angles:
            bin_idx = int(angle / bin_size) % n_bins
            counts[bin_idx] += 1
        
        # 计算熵
        total = sum(counts)
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log(p + 1e-10)
        
        return min(2.0, max(0.0, entropy))
    
    def apply_cycle(self, num_cycles: int = 1,
                   initial_phase: Optional[EMLPhase] = None) -> CycleResult:
        """
        应用五行循环（主方法）
        
        参数：
            num_cycles: 循环次数
            initial_phase: 初始相位
        
        返回：
            循环结果
        """
        if initial_phase is None:
            initial_phase = EMLPhase.Σ
        
        phases = []
        phase_angles = []
        amplitudes = []
        
        current_state = self.phases[initial_phase]
        
        for cycle_idx in range(num_cycles):
            for element in self.cycle:
                # 相位耦合
                new_state, coupling = self.couple_phase(current_state, element)
                
                phases.append(element)
                phase_angles.append(new_state.phase_angle)
                amplitudes.append(new_state.amplitude)
                
                current_state = new_state
        
        # 计算指标
        closure = self.compute_closure_degree(phase_angles)
        coherence = self.compute_coherence(amplitudes)
        entropy = self.compute_phase_entropy(phase_angles)
        
        # 判断是否稳定（闭合度高、相干性高、熵低）
        is_stable = (closure >= self.closure_threshold 
                     and coherence > 0.7 
                     and entropy < 1.5)
        
        # 生成洞见
        insight = self._generate_insight(closure, coherence, entropy, is_stable)
        
        return CycleResult(
            phases=phases,
            phase_angles=phase_angles,
            amplitudes=amplitudes,
            closure_degree=round(closure, 4),
            coherence=round(coherence, 4),
            entropy=round(entropy, 4),
            is_stable=is_stable,
            insight=insight
        )
    
    def get_phase_state(self, element: EMLPhase) -> PhaseState:
        """获取元素相位状态"""
        return self.phases.get(element)
    
    def set_phase_state(self, element: EMLPhase, state: PhaseState):
        """设置元素相位状态"""
        self.phases[element] = state
    
    def _generate_insight(self, closure: float, coherence: float,
                           entropy: float, is_stable: bool) -> str:
        """生成分析洞见"""
        parts = []
        
        if closure >= self.closure_threshold:
            parts.append("✅ ℤ₅闭合性满足——EML相位耦合稳定")
        else:
            parts.append(f"⚠️ ℤ₅闭合性不足（{closure:.2f}）——相位需要调整")
        
        if coherence > 0.8:
            parts.append(f"相干性优秀（{coherence:.2f}）——各元素同步良好")
        elif coherence > 0.6:
            parts.append(f"相干性良好（{coherence:.2f}）")
        else:
            parts.append(f"⚠️ 相干性较低（{coherence:.2f}）——元素间同步不足")
        
        if entropy < 1.0:
            parts.append(f"相位熵低（{entropy:.2f}）——系统有序")
        elif entropy < 1.5:
            parts.append(f"相位熵中等（{entropy:.2f}）")
        else:
            parts.append(f"⚠️ 相位熵较高（{entropy:.2f}）——系统较混乱")
        
        if is_stable:
            parts.append("✅ 系统稳定——五行相位耦合处于平衡态")
        else:
            parts.append("⚠️ 系统不稳定——需要调整相位耦合参数")
        
        return " | ".join(parts)


def get_instance():
    """获取单例实例"""
    return EMLPhaseCouplingZ5()


if __name__ == "__main__":
    # 测试代码
    coupler = EMLPhaseCouplingZ5()
    
    # 应用五行循环
    result = coupler.apply_cycle(num_cycles=2)
    
    print("EML相位耦合ℤ₅分析：")
    print(f"  相位数量: {len(result.phases)}")
    print(f"  ℤ₅闭合度: {result.closure_degree}")
    print(f"  相干性: {result.coherence}")
    print(f"  相位熵: {result.entropy}")
    print(f"  稳定状态: {result.is_stable}")
    print(f"  洞见: {result.insight}")
    print()
    
    # 验证ℤ₅闭合
    is_closed = coupler.verify_z5_closure(result.phases)
    print(f"ℤ₅闭合验证: {is_closed}")
