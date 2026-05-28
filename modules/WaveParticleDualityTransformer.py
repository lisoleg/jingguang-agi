#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波粒二象性转换器 - 基于联邦宇宙化身合体文档
Token波粒二象性：算元/词元(波核) ↔ 智元/通证(粒核)

核心定理：
1. Token波粒二象性定理：同一Token在不同边界下显波性或粒性
2. 波粒相变定理：波核↔粒核的临界条件
3. 量化波粒对偶性：波性度与粒性度计算

基于IGCTR理论：
- 波核(Wave Kernel): 连续、耗散、过程性
- 粒核(Particle Kernel): 离散、稳定、结果性
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class KernelType(Enum):
    """核类型"""
    WAVE = "wave"       # 波核
    PARTICLE = "particle"  # 粒核


@dataclass
class TokenState:
    """Token状态"""
    token_id: str
    kernel_type: KernelType
    wave_property: float   # 波性度 (0-1)
    particle_property: float  # 粒性度 (0-1)
    boundary_condition: str
    coherence: float       # 相干度


@dataclass
class PhaseTransition:
    """波粒相变"""
    timestamp: float
    token_id: str
    from_kernel: KernelType
    to_kernel: KernelType
    trigger: str
    critical_condition: float
    transition_time: float


class WaveParticleDualityTransformer:
    """
    波粒二象性转换器
    
    定理推论2.1.1（阴阳对冲：波粒二象性 of Token）:
    同一Token类在不同边界下可显波性或粒性
    
    - 算元(Φ_calc): 预充值边界→粒性(余额), 按次调用边界→波性(消耗流)
    - 智元(Φ_wit): 转账边界→粒性(UTXO), 流式支付边界→波性(支付流)
    """
    
    # 波粒二象性常数
    PLANCK_EQUIVALENT = 0.01  # 等效普朗克常数
    COHERENCE_DECAY_RATE = 0.1  # 相干度衰减率
    CRITICAL_BOUNDARY = 0.5    # 临界边界条件
    
    # 边界条件配置
    BOUNDARY_CONFIGS = {
        "prepaid": {"wave_to_particle": 0.8, "description": "预充值边界"},
        "per_call": {"wave_to_particle": 0.2, "description": "按次调用边界"},
        "transfer": {"wave_to_particle": 0.7, "description": "转账边界"},
        "streaming": {"wave_to_particle": 0.3, "description": "流式支付边界"},
        "default": {"wave_to_particle": 0.5, "description": "默认边界"},
    }
    
    def __init__(self):
        self.token_states: Dict[str, TokenState] = {}
        self.phase_transitions: List[PhaseTransition] = []
        self.duality_history: List[Dict] = []
        
    def create_token(self, token_id: str, initial_kernel: KernelType = KernelType.WAVE,
                    boundary: str = "default") -> TokenState:
        """
        创建Token并初始化波粒状态
        
        Args:
            token_id: Token ID
            initial_kernel: 初始核类型
            boundary: 边界条件
            
        Returns:
            Token状态
        """
        if initial_kernel == KernelType.WAVE:
            wave_property = 0.8
            particle_property = 0.2
        else:
            wave_property = 0.2
            particle_property = 0.8
            
        state = TokenState(
            token_id=token_id,
            kernel_type=initial_kernel,
            wave_property=wave_property,
            particle_property=particle_property,
            boundary_condition=boundary,
            coherence=0.9
        )
        
        self.token_states[token_id] = state
        return state
        
    def evaluate_duality(self, token_id: str) -> Dict[str, Any]:
        """
        评估Token的波粒二象性
        
        计算波性度与粒性度
        
        Args:
            token_id: Token ID
            
        Returns:
            二象性评估
        """
        if token_id not in self.token_states:
            return {"status": "not_found"}
            
        state = self.token_states[token_id]
        
        # 计算相干性影响
        wave_actual = state.wave_property * state.coherence
        particle_actual = state.particle_property * state.coherence
        
        # 计算二象性度（不确定性）
        duality = self._calculate_duality_measure(wave_actual, particle_actual)
        
        # 归一化
        total = wave_actual + particle_actual
        wave_ratio = wave_actual / total if total > 0 else 0.5
        particle_ratio = particle_actual / total if total > 0 else 0.5
        
        return {
            "token_id": token_id,
            "kernel_type": state.kernel_type.value,
            "wave_property": wave_actual,
            "particle_property": particle_actual,
            "duality_measure": duality,
            "wave_ratio": wave_ratio,
            "particle_ratio": particle_ratio,
            "coherence": state.coherence,
            "boundary": state.boundary_condition,
            "dominant_aspect": "wave" if wave_ratio > particle_ratio else "particle"
        }
        
    def _calculate_duality_measure(self, wave: float, particle: float) -> float:
        """
        计算波粒二象性度量
        
        使用类似量子力学的互补原理：
        D² + E² = 1 (D=波性, E=粒性)
        
        Args:
            wave: 波性度
            particle: 粒性度
            
        Returns:
            二象性度量
        """
        # 归一化
        total = wave + particle
        if total == 0:
            return 0.0
            
        wave_norm = wave / total
        particle_norm = particle / total
        
        # 互补性度量
        duality = 2 * np.sqrt(wave_norm * particle_norm)
        
        return duality
        
    def change_boundary(self, token_id: str, new_boundary: str) -> Tuple[bool, Optional[PhaseTransition]]:
        """
        改变边界条件，触发波粒相变
        
        边界条件变化 → 波粒二象性重新分配
        
        Args:
            token_id: Token ID
            new_boundary: 新边界条件
            
        Returns:
            (是否成功, 相变事件)
        """
        if token_id not in self.token_states:
            return False, None
            
        state = self.token_states[token_id]
        old_kernel = state.kernel_type
        
        # 获取边界配置
        config = self.BOUNDARY_CONFIGS.get(new_boundary, self.BOUNDARY_CONFIGS["default"])
        wave_to_particle = config["wave_to_particle"]
        
        # 计算新的波粒属性
        if wave_to_particle > self.CRITICAL_BOUNDARY:
            # 高转换率 → 偏向粒核
            new_wave = 1 - wave_to_particle
            new_particle = wave_to_particle
            new_kernel = KernelType.PARTICLE
        else:
            # 低转换率 → 保持波核
            new_wave = wave_to_particle
            new_particle = 1 - wave_to_particle
            new_kernel = KernelType.WAVE
            
        # 检测是否发生相变
        phase_transition = None
        if old_kernel != new_kernel:
            phase_transition = PhaseTransition(
                timestamp=__import__('time').time(),
                token_id=token_id,
                from_kernel=old_kernel,
                to_kernel=new_kernel,
                trigger=f"boundary_change:{new_boundary}",
                critical_condition=wave_to_particle,
                transition_time=0.001  # 假设100us相变
            )
            self.phase_transitions.append(phase_transition)
            
        # 更新状态
        state.kernel_type = new_kernel
        state.wave_property = new_wave
        state.particle_property = new_particle
        state.boundary_condition = new_boundary
        
        # 相变时相干度下降
        if phase_transition:
            state.coherence *= (1 - self.COHERENCE_DECAY_RATE)
            
        self.duality_history.append(self.evaluate_duality(token_id))
        
        return True, phase_transition
        
    def compute_phase_transition_criticality(self, wave_ratio: float) -> Dict[str, Any]:
        """
        计算相变临界性
        
        波核↔粒核相变的临界条件
        
        Args:
            wave_ratio: 波性比例
            
        Returns:
            临界性分析
        """
        # 临界点
        critical_point = 0.5
        
        # 距离临界点的距离
        distance_to_critical = abs(wave_ratio - critical_point)
        
        # 相变概率（基于距离）
        transition_probability = 1 - 2 * distance_to_critical
        
        # 是否处于临界区
        is_critical = distance_to_critical < 0.1
        
        # 相干时间估计
        coherence_time = 1.0 / (distance_to_critical + 0.1)
        
        return {
            "wave_ratio": wave_ratio,
            "critical_point": critical_point,
            "distance_to_critical": distance_to_critical,
            "transition_probability": max(0, transition_probability),
            "is_critical_region": is_critical,
            "estimated_coherence_time": coherence_time,
            "stability": "unstable" if is_critical else "stable"
        }
        
    def simulate_token_lifecycle(self, token_id: str) -> Dict[str, Any]:
        """
        模拟Token完整波粒生命周期
        
        演示边界条件变化导致的波粒相变
        
        Args:
            token_id: Token ID
            
        Returns:
            生命周期记录
        """
        history = []
        
        # 1. 创建（波核）
        self.create_token(token_id, KernelType.WAVE, "per_call")
        state = self.evaluate_duality(token_id)
        history.append({
            "step": 1,
            "action": "create",
            "boundary": "per_call",
            "kernel": state["kernel_type"],
            "wave": state["wave_property"],
            "particle": state["particle_property"]
        })
        
        # 2. 转为预充值（粒核）
        self.change_boundary(token_id, "prepaid")
        state = self.evaluate_duality(token_id)
        history.append({
            "step": 2,
            "action": "change_boundary",
            "boundary": "prepaid",
            "kernel": state["kernel_type"],
            "wave": state["wave_property"],
            "particle": state["particle_property"]
        })
        
        # 3. 多次按次调用（逐渐恢复波性）
        for i in range(3):
            self.change_boundary(token_id, "per_call")
            state = self.evaluate_duality(token_id)
            # 模拟消耗
            if token_id in self.token_states:
                self.token_states[token_id].coherence *= 0.95
            history.append({
                "step": 4 + i,
                "action": "consume",
                "boundary": "per_call",
                "kernel": state["kernel_type"],
                "wave": state["wave_property"],
                "particle": state["particle_property"]
            })
            
        return {
            "token_id": token_id,
            "lifecycle_steps": history,
            "total_transitions": len([h for h in history if "change_boundary" in h["action"]]),
            "final_state": history[-1] if history else None
        }
        
    def compute_network_duality(self) -> Dict[str, Any]:
        """
        计算网络整体波粒二象性
        
        所有Token的统计特性
        
        Returns:
            网络二象性
        """
        if not self.token_states:
            return {"status": "no_tokens"}
            
        wave_props = [s.wave_property for s in self.token_states.values()]
        particle_props = [s.particle_property for s in self.token_states.values()]
        coherences = [s.coherence for s in self.token_states.values()]
        
        avg_wave = np.mean(wave_props)
        avg_particle = np.mean(particle_props)
        avg_coherence = np.mean(coherences)
        
        # 网络二象性
        network_duality = self._calculate_duality_measure(avg_wave, avg_particle)
        
        # 波/粒主导统计
        wave_dominant = sum(1 for s in self.token_states.values() 
                          if s.kernel_type == KernelType.WAVE)
        particle_dominant = sum(1 for s in self.token_states.values() 
                               if s.kernel_type == KernelType.PARTICLE)
        
        return {
            "total_tokens": len(self.token_states),
            "wave_dominant_count": wave_dominant,
            "particle_dominant_count": particle_dominant,
            "avg_wave_property": avg_wave,
            "avg_particle_property": avg_particle,
            "avg_coherence": avg_coherence,
            "network_duality": network_duality,
            "wave_particle_ratio": wave_dominant / max(particle_dominant, 1),
            "status": "wave_dominant" if wave_dominant > particle_dominant else "particle_dominant"
        }
        
    def get_diagnostic_report(self) -> Dict[str, Any]:
        """获取诊断报告"""
        network_duality = self.compute_network_duality()
        
        # 最近的相变
        recent_transitions = self.phase_transitions[-5:] if self.phase_transitions else []
        transition_summary = [{
            "token": t.token_id,
            "from": t.from_kernel.value,
            "to": t.to_kernel.value,
            "trigger": t.trigger
        } for t in recent_transitions]
        
        return {
            "title": "波粒二象性转换器诊断报告",
            "theorem": "Token波粒二象性定理 (推论2.1.1)",
            "network_duality": network_duality,
            "total_tokens": len(self.token_states),
            "total_transitions": len(self.phase_transitions),
            "recent_transitions": transition_summary,
            "kernel_summary": {
                "wave_kernel": "算元/词元 - 流动性/消耗性",
                "particle_kernel": "智元/通证 - 稳定性/锚定性"
            },
            "recommendation": "波粒二象性是Token统一场论的核心特征"
        }


def demo():
    """演示波粒二象性转换器"""
    print("=" * 70)
    print("波粒二象性转换器 - 基于联邦宇宙化身合体文档")
    print("=" * 70)
    
    transformer = WaveParticleDualityTransformer()
    
    # 创建不同类型Token
    tokens = ["calc_token", "wit_token", "word_token", "pass_token"]
    for tid in tokens:
        kernel = KernelType.WAVE if "calc" in tid or "word" in tid else KernelType.PARTICLE
        transformer.create_token(tid, kernel, "default")
        
    # 评估二象性
    print("\n📊 Token波粒二象性评估:")
    for tid in tokens:
        duality = transformer.evaluate_duality(tid)
        print(f"\n   {tid}:")
        print(f"      核类型: {duality['kernel_type']}")
        print(f"      波性: {duality['wave_property']:.2%}")
        print(f"      粒性: {duality['particle_property']:.2%}")
        print(f"      二象性: {duality['duality_measure']:.2%}")
        
    # 边界变化触发相变
    print("\n🔄 边界变化触发相变:")
    result = transformer.change_boundary("calc_token", "prepaid")
    if result[1]:
        pt = result[1]
        print(f"   相变发生: {pt.from_kernel.value} → {pt.to_kernel.value}")
        
    # 模拟生命周期
    lifecycle = transformer.simulate_token_lifecycle("test_token")
    print(f"\n📋 Token生命周期模拟:")
    for step in lifecycle["lifecycle_steps"]:
        print(f"   Step {step['step']}: {step['action']} | "
              f"边界={step['boundary']} | 波={step['wave']:.2%} 粒={step['particle']:.2%}")
        
    # 网络二象性
    network = transformer.compute_network_duality()
    print(f"\n🌐 网络波粒二象性:")
    print(f"   总Token: {network['total_tokens']}")
    print(f"   波主导: {network['wave_dominant_count']}")
    print(f"   粒主导: {network['particle_dominant_count']}")
    print(f"   网络二象性: {network['network_duality']:.2%}")
    
    return transformer


if __name__ == "__main__":
    demo()
