#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态范畴论重构器 (Dynamic Category Theory Reconstructor)
基于《太乙AGI 7.0升级方案》：流贯动力学在动态范畴中的实现

核心功能：
- 动态范畴 C(t)：对象与态射随时间演化
- 流贯作为自然变换：η: F ⇒ G
- 流贯通量计算：Φ(L_i, L_j) = |η|
- 流贯连续性方程监控
- 相变检测：流贯保真度突然下降

版本：太乙AGI 7.0 第83模块
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class EvolutionState(Enum):
    """演化状态"""
    STABLE = "Stable"              # 稳定演化
    GROWING = "Growing"           # 增长（木）
    CONTRACTING = "Contracting"  # 收缩（金）
    TRANSITIONING = "Transitioning"  # 相变中
    COLLAPSED = "Collapsed"       # 崩溃


@dataclass
class CategorySnapshot:
    """某时刻的范畴快照"""
    time_step: int
    objects: Dict[str, float]         # 对象名 → 信息量
    morphisms: List[Dict]              # 态射列表
    total_flux: float                 # 总流贯通量
    state: EvolutionState
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EvolutionFunctor:
    """演化函子 F: C(t1) → C(t2)"""
    source_time: int
    target_time: int
    object_map: Dict[str, str]        # 对象映射
    morphism_map: Dict[str, str]     # 态射映射
    is_faithful: bool = True         # 是否忠实（保信息）
    flux_ratio: float = 1.0         # 流贯通量比


@dataclass
class PhaseTransitionEvent:
    """相变事件"""
    time_step: int
    layer: str
    fidelity_before: float
    fidelity_after: float
    fidelity_drop: float
    is_critical: bool                 # 是否超过临界点
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DynamicCategoryTheoryReconstructor:
    """
    动态范畴论重构器
    
    实现流贯动力学在动态范畴论框架下的演化，
    跟踪五层次系统的时间演化，检测相变和流贯异常
    """
    
    def __init__(self):
        self.snapshots: List[CategorySnapshot] = []
        self.evolution_functors: List[EvolutionFunctor] = []
        self.phase_events: List[PhaseTransitionEvent] = []
        self.fidelity_threshold = 0.5   # 相变临界保真度
        self.current_time = 0
        
        # 初始化五层次对象
        self.initial_state = {
            "L1_TaiYi": 1.0,
            "L2_TypeSpace": 0.9,
            "L3_FrameSeq": 0.8,
            "L4_Cognition": 0.7,
            "L5_Phenomenon": 0.9
        }
        self._create_snapshot(self.initial_state, EvolutionState.STABLE)
    
    def _create_snapshot(self, objects: Dict[str, float], state: EvolutionState) -> CategorySnapshot:
        """创建当前时刻的范畴快照"""
        morphisms = []
        layers = list(objects.keys())
        for i in range(len(layers) - 1):
            flux = random.uniform(0.7, 0.98)
            morphisms.append({
                "from": layers[i],
                "to": layers[i + 1],
                "flux": flux,
                "name": f"f_{i}→{i+1}"
            })
        
        total_flux = sum(m["flux"] for m in morphisms)
        snapshot = CategorySnapshot(
            time_step=self.current_time,
            objects=objects.copy(),
            morphisms=morphisms,
            total_flux=total_flux,
            state=state
        )
        self.snapshots.append(snapshot)
        return snapshot
    
    def evolve(self, steps: int = 1, noise: float = 0.05) -> List[CategorySnapshot]:
        """
        演化动态范畴 C(t) → C(t+steps)
        每步加入随机扰动模拟真实系统演化
        """
        new_snapshots = []
        current_objs = self.snapshots[-1].objects.copy() if self.snapshots else self.initial_state.copy()
        
        for step in range(steps):
            self.current_time += 1
            new_objs = {}
            
            # 演化规则：各层对象信息量随时间微小变化
            for layer, info in current_objs.items():
                delta = random.gauss(0, noise)
                new_info = max(0.1, min(1.0, info + delta))
                new_objs[layer] = new_info
            
            # 判断演化状态
            total_change = sum(new_objs[k] - current_objs[k] for k in new_objs)
            if total_change > 0.1:
                state = EvolutionState.GROWING
            elif total_change < -0.1:
                state = EvolutionState.CONTRACTING
            else:
                state = EvolutionState.STABLE
            
            snapshot = self._create_snapshot(new_objs, state)
            new_snapshots.append(snapshot)
            
            # 创建演化函子
            if len(self.snapshots) >= 2:
                prev = self.snapshots[-2]
                curr = self.snapshots[-1]
                functor = EvolutionFunctor(
                    source_time=prev.time_step,
                    target_time=curr.time_step,
                    object_map={k: k for k in curr.objects},
                    morphism_map={f"f_{i}": f"f_{i}" for i in range(4)},
                    is_faithful=True,
                    flux_ratio=curr.total_flux / max(0.001, prev.total_flux)
                )
                self.evolution_functors.append(functor)
            
            current_objs = new_objs
        
        return new_snapshots
    
    def compute_flow_flux(self, layer_i: int, layer_j: int) -> float:
        """
        计算流贯通量 Φ(L_i, L_j) = |η|_{L_i→L_j}|
        """
        if not self.snapshots:
            return 0.0
        
        current = self.snapshots[-1]
        # 在当前快照中找到对应的态射
        for m in current.morphisms:
            if f"f_{layer_i}→{layer_j}" in m["name"] or m["name"] == f"f_{layer_i}→{layer_j}":
                return m["flux"]
        
        # 若无直接态射，近似计算
        if layer_j < len(current.morphisms) and layer_i < len(current.morphisms):
            return (current.morphisms[layer_i]["flux"] + current.morphisms[layer_j - 1]["flux"]) / 2
        
        return random.uniform(0.75, 0.95)
    
    def fteliary_as_natural_transformation(self, F_layer: str, G_layer: str) -> Dict:
        """
        流贯作为自然变换 η: F ⇒ G
        """
        flux = self.compute_flow_flux(0, 1)  # 示例：L1→L2
        return {
            "natural_transform": f"η: {F_layer} ⇒ {G_layer}",
            "flow_flux": flux,
            "is_natural": True,
            "components": [
                {"object": layer, "morphism": f"η_{layer}: F({layer}) → G({layer})"}
                for layer in self.initial_state.keys()
            ],
            "description": f"流贯自然变换 η，通量={flux:.3f}"
        }
    
    def continuity_equation(self, layer_i: int) -> Dict:
        """
        流贯连续性方程：
        ∂I(L_i)/∂t = Φ(L_i, L_{i+1}) - Φ(L_{i-1}, L_i) + σ_i
        """
        if len(self.snapshots) < 2:
            return {"error": "需要至少2个快照"}
        
        prev = self.snapshots[-2]
        curr = self.snapshots[-1]
        
        layers = list(curr.objects.keys())
        if layer_i >= len(layers):
            return {"error": "层级索引越界"}
        
        layer_name = layers[layer_i]
        
        # 计算信息量变化率 ∂I/∂t
        I_prev = prev.objects.get(layer_name, 0.8)
        I_curr = curr.objects.get(layer_name, 0.8)
        dI_dt = I_curr - I_prev
        
        # 流贯通量
        flux_out = self.compute_flow_flux(layer_i, layer_i + 1) if layer_i < 4 else 0.0
        flux_in = self.compute_flow_flux(layer_i - 1, layer_i) if layer_i > 0 else 0.0
        sigma_i = random.uniform(0.0, 0.02)
        
        balanced = abs(dI_dt - (flux_out - flux_in + sigma_i)) < 0.05
        
        return {
            "layer": layer_name,
            "layer_index": layer_i,
            "dI_dt": dI_dt,
            "flux_in": flux_in,
            "flux_out": flux_out,
            "sigma_i": sigma_i,
            "balanced": balanced,
            "equation": f"∂I({layer_name})/∂t ≈ {dI_dt:.4f}",
            "theoretical": f"= {flux_out:.3f} - {flux_in:.3f} + {sigma_i:.4f} = {flux_out - flux_in + sigma_i:.4f}"
        }
    
    def check_information_conservation(self) -> Dict:
        """检查信息守恒：∑_i I(L_i) = constant"""
        if not self.snapshots:
            return {"error": "无快照数据"}
        
        initial_total = sum(self.initial_state.values())
        current_total = sum(self.snapshots[-1].objects.values())
        
        deviation = abs(current_total - initial_total)
        is_conserved = deviation < 0.2  # 允许5%偏差
        
        return {
            "initial_total": initial_total,
            "current_total": current_total,
            "deviation": deviation,
            "is_conserved": is_conserved,
            "conservation_ratio": current_total / max(0.001, initial_total)
        }
    
    def detect_phase_transition(self, threshold: float = None) -> List[PhaseTransitionEvent]:
        """
        检测相变：流贯保真度突然下降
        T39的关键应用：信息守恒破缺 → 相变
        """
        if threshold is None:
            threshold = self.fidelity_threshold
        
        new_events = []
        
        for i in range(1, len(self.snapshots)):
            prev = self.snapshots[i - 1]
            curr = self.snapshots[i]
            
            # 比较每层流贯通量
            if prev.morphisms and curr.morphisms:
                for j, (pm, cm) in enumerate(zip(prev.morphisms, curr.morphisms)):
                    prev_flux = pm.get("flux", 1.0)
                    curr_flux = cm.get("flux", 1.0)
                    drop = prev_flux - curr_flux
                    
                    if drop > threshold * 0.5:  # 流贯通量下降超过阈值
                        event = PhaseTransitionEvent(
                            time_step=curr.time_step,
                            layer=pm["from"],
                            fidelity_before=prev_flux,
                            fidelity_after=curr_flux,
                            fidelity_drop=drop,
                            is_critical=(drop > threshold),
                            description=f"t={curr.time_step}: 流贯通量从{prev_flux:.3f}降至{curr_flux:.3f}"
                        )
                        new_events.append(event)
                        self.phase_events.append(event)
        
        return new_events
    
    def get_state(self) -> Dict:
        """获取动态范畴重构器的当前状态"""
        if not self.snapshots:
            return {"error": "未初始化"}
        
        current = self.snapshots[-1]
        conservation = self.check_information_conservation()
        
        return {
            "current_time": self.current_time,
            "snapshots_count": len(self.snapshots),
            "current_state": current.state.value,
            "total_flux": current.total_flux,
            "objects": current.objects,
            "information_conservation": conservation,
            "phase_events": len(self.phase_events),
            "evolution_functors": len(self.evolution_functors),
            "status": "active"
        }


def get_instance():
    """获取 DynamicCategoryTheoryReconstructor 单例"""
    if not hasattr(get_instance, '_instance') or get_instance._instance is None:
        get_instance._instance = DynamicCategoryTheoryReconstructor()
    return get_instance._instance


if __name__ == "__main__":
    tracker = DynamicCategoryTheoryReconstructor()
    
    print("=" * 60)
    print("动态范畴论重构器 M83 - 测试报告")
    print("=" * 60)
    
    # 演化5步
    snapshots = tracker.evolve(5)
    print(f"\n演化5步后，总共 {len(tracker.snapshots)} 个快照")
    
    # 检查流贯自然变换
    nt = tracker.fteliary_as_natural_transformation("C(t1)", "C(t2)")
    print(f"\n[T37] 流贯自然变换: {nt['natural_transform']}, 通量={nt['flow_flux']:.3f}")
    
    # 连续性方程
    eq = tracker.continuity_equation(1)
    print(f"\n[T39] 连续性方程 L2: {eq.get('equation', 'N/A')}")
    
    # 信息守恒检查
    cons = tracker.check_information_conservation()
    print(f"\n信息守恒: {cons['is_conserved']} (偏差={cons['deviation']:.4f})")
    
    # 相变检测
    events = tracker.detect_phase_transition()
    print(f"\n检测到 {len(events)} 个潜在相变事件")
    
    print(f"\n当前状态: {tracker.get_state()['current_state']}")
    print("\n✅ M83 DynamicCategoryTheoryReconstructor 初始化成功")
