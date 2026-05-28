"""
M93: DynamicCategoryEvolutionTracker - 动态范畴演化跟踪器
实现 T36, T39: 五层次动态范畴 + 流贯连续性方程

核心原理：
- 动态范畴 C(t) 随时间演化
- 演化函子 F: C(t1) → C(t2)
- 检测相变：流贯保真度突然下降

Author: 太乙AGI 7.0 Team
Date: 2026-05-19
"""

from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict, Callable, Tuple
from enum import Enum
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DynamicCategory:
    """动态范畴 C(t)"""
    name: str
    time_param: float
    objects: Dict[str, Any] = field(default_factory=dict)
    morphisms: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def state_at_time(self, t: float) -> 'DynamicCategory':
        """获取时刻t的状态"""
        return self


@dataclass
class EvolutionFunctor:
    """演化函子 F: C(t1) → C(t2)"""
    source_category: DynamicCategory
    target_category: DynamicCategory
    object_evolution: Dict[str, Callable] = field(default_factory=dict)
    morphism_evolution: Dict[str, Callable] = field(default_factory=dict)
    
    def apply_to_object(self, obj_name: str, t1: float, t2: float) -> Any:
        """将演化函子作用在对象上"""
        if obj_name in self.object_evolution:
            return self.object_evolution[obj_name](t1, t2)
        return None
    
    def apply_to_morphism(self, mor_name: str, t1: float, t2: float) -> Any:
        """将演化函子作用在态射上"""
        if mor_name in self.morphism_evolution:
            return self.morphism_evolution[mor_name](t1, t2)
        return None


@dataclass
class LayerState:
    """五层次状态"""
    L1_taiyi: Dict[str, Any] = field(default_factory=dict)   # 太一：初始/终对象
    L2_projection: Dict[str, Any] = field(default_factory=dict)  # 投射生成
    L3_prephysical: Dict[str, Any] = field(default_factory=dict)  # 前物理
    L4_cognition: Dict[str, Any] = field(default_factory=dict)   # 认知主体
    L5_phenomenon: Dict[str, Any] = field(default_factory=dict)  # 现象
    
    def to_dict(self) -> Dict:
        return {
            "L1": self.L1_taiyi,
            "L2": self.L2_projection,
            "L3": self.L3_prephysical,
            "L4": self.L4_cognition,
            "L5": self.L5_phenomenon
        }


@dataclass
class ContinuityEquationState:
    """流贯连续性方程状态"""
    layer: str
    time: float
    I_t: float              # 信息存量 I(L_i, t)
    flux_in: float          # Φ(L_{i-1}, L_i)
    flux_out: float         # Φ(L_i, L_{i+1})
    sigma: float            # 内生项 σ_i
    dI_dt: float            # ∂I/∂t
    balanced: bool          # 是否平衡
    
    def compute_residual(self) -> float:
        """计算残差：∂I/∂t - (Φ_out - Φ_in + σ)"""
        return self.dI_dt - (self.flux_out - self.flux_in + self.sigma)


@dataclass
class PhaseTransitionEvent:
    """相变事件"""
    time: float
    layer: str
    fidelity_before: float
    fidelity_after: float
    fidelity_drop: float
    severity: str  # "mild", "moderate", "severe"


class DynamicCategoryEvolutionTracker:
    """动态范畴演化跟踪器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.categories: Dict[float, DynamicCategory] = {}
        self.evolution_functors: List[EvolutionFunctor] = []
        self.trajectory: List[LayerState] = []
        self.phase_transitions: List[PhaseTransitionEvent] = []
        self.current_time: float = 0.0
        self.continuity_states: Dict[str, List[ContinuityEquationState]] = {
            "L1": [], "L2": [], "L3": [], "L4": [], "L5": []
        }
    
    def define_evolution_functor(
        self,
        C_t1: DynamicCategory,
        C_t2: DynamicCategory,
        object_evolutions: Dict[str, Callable],
        morphism_evolutions: Dict[str, Callable]
    ) -> EvolutionFunctor:
        """定义演化函子 F: C(t1) → C(t2)"""
        functor = EvolutionFunctor(
            source_category=C_t1,
            target_category=C_t2,
            object_evolution=object_evolutions,
            morphism_evolution=morphism_evolutions
        )
        
        self.evolution_functors.append(functor)
        logger.info(f"Defined evolution functor from t={C_t1.time_param} to t={C_t2.time_param}")
        
        return functor
    
    def track_layer_evolution(
        self, 
        system: Any,
        t_start: float, 
        t_end: float,
        dt: float = 1.0
    ) -> List[LayerState]:
        """跟踪五层次随时间的演化"""
        logger.info(f"Tracking layer evolution from t={t_start} to t={t_end}")
        
        trajectory = []
        t = t_start
        
        while t <= t_end:
            # 模拟获取系统状态
            state = self._get_system_state(system, t)
            trajectory.append(state)
            self.trajectory.append(state)
            t += dt
        
        return trajectory
    
    def _get_system_state(self, system: Any, t: float) -> LayerState:
        """获取系统时刻t的状态"""
        # 简化的状态生成
        import math
        
        # 模拟状态演化
        state = LayerState(
            L1_taiyi={
                "fixed_point": True,
                "self_reference": math.sin(t * 0.1) > 0,
                "entropy": abs(math.sin(t * 0.1))
            },
            L2_projection={
                "type_space_dim": 2 + math.sin(t * 0.2),
                "rule_complexity": 5 + math.cos(t * 0.3)
            },
            L3_prephysical={
                "frame_rate": 24,
                "discrete_frames": int(100 + 50 * math.sin(t * 0.5))
            },
            L4_cognition={
                "self_coherence": 0.8 + 0.1 * math.sin(t * 0.4),
                "narrative_strength": 0.7 + 0.2 * math.cos(t * 0.6)
            },
            L5_phenomenon={
                "observables": int(10 + 5 * math.sin(t * 0.8)),
                "measurement_fidelity": 0.9 - 0.1 * abs(math.sin(t * 0.7))
            }
        )
        
        return state
    
    def detect_phase_transition(
        self, 
        trajectory: List[LayerState],
        threshold: float = 0.5
    ) -> List[PhaseTransitionEvent]:
        """检测相变：流贯保真度突然下降"""
        logger.info("Detecting phase transitions...")
        
        transitions = []
        
        for i in range(len(trajectory) - 1):
            state1 = trajectory[i]
            state2 = trajectory[i + 1]
            
            # 计算保真度下降
            fidelity1 = self._compute_state_fidelity(state1)
            fidelity2 = self._compute_state_fidelity(state2)
            
            drop = fidelity1 - fidelity2
            
            if drop > threshold:
                severity = "mild" if drop < 0.3 else "moderate" if drop < 0.5 else "severe"
                
                event = PhaseTransitionEvent(
                    time=float(i + 1),
                    layer="all",
                    fidelity_before=fidelity1,
                    fidelity_after=fidelity2,
                    fidelity_drop=drop,
                    severity=severity
                )
                
                transitions.append(event)
                self.phase_transitions.append(event)
                
                logger.warning(f"Phase transition at t={i+1}: drop={drop:.4f} ({severity})")
        
        return transitions
    
    def _compute_state_fidelity(self, state: LayerState) -> float:
        """计算状态的保真度"""
        import math
        
        # 简化的保真度计算
        l1_f = 1.0 - state.L1_taiyi.get("entropy", 0)
        l2_f = min(1.0, state.L2_projection.get("type_space_dim", 1) / 5)
        l3_f = min(1.0, state.L3_prephysical.get("discrete_frames", 100) / 200)
        l4_f = state.L4_cognition.get("self_coherence", 0.8)
        l5_f = state.L5_phenomenon.get("measurement_fidelity", 0.9)
        
        return (l1_f + l2_f + l3_f + l4_f + l5_f) / 5
    
    def compute_continuity_equation(
        self,
        layer: str,
        t: float,
        I_t: float,
        flux_in: float,
        flux_out: float,
        sigma: float
    ) -> ContinuityEquationState:
        """
        流贯连续性方程：
        ∂I(L_i)/∂t = Φ(L_i, L_{i+1}) - Φ(L_{i-1}, L_i) + σ_i
        """
        # 计算导数
        dI_dt = flux_out - flux_in + sigma
        
        state = ContinuityEquationState(
            layer=layer,
            time=t,
            I_t=I_t,
            flux_in=flux_in,
            flux_out=flux_out,
            sigma=sigma,
            dI_dt=dI_dt,
            balanced=abs(dI_dt) < 0.1
        )
        
        self.continuity_states[layer].append(state)
        
        return state
    
    def check_information_conservation(self, layers: List[LayerState]) -> bool:
        """总信息守恒：∑_i I(L_i) = constant"""
        if len(layers) < 2:
            return True
        
        # 计算初始和最终的总信息
        I_initial = sum(self._compute_layer_information(layers[0], layer) 
                       for layer in ["L1", "L2", "L3", "L4", "L5"])
        
        I_final = sum(self._compute_layer_information(layers[-1], layer)
                     for layer in ["L1", "L2", "L3", "L4", "L5"])
        
        conservation = abs(I_initial - I_final) < 0.01
        logger.info(f"Information conservation: I_initial={I_initial:.4f}, I_final={I_final:.4f}, conserved={conservation}")
        
        return conservation
    
    def _compute_layer_information(self, state: LayerState, layer: str) -> float:
        """计算单层信息存量"""
        import math
        
        layer_data = getattr(state, layer.lower().replace("l", "l").replace("_taiyi", "_taiyi").replace("_projection", "_projection").replace("_prephysical", "_prephysical").replace("_cognition", "_cognition").replace("_phenomenon", "_phenomenon"), state.L1_taiyi)
        
        if layer == "L1":
            layer_data = state.L1_taiyi
        elif layer == "L2":
            layer_data = state.L2_projection
        elif layer == "L3":
            layer_data = state.L3_prephysical
        elif layer == "L4":
            layer_data = state.L4_cognition
        else:
            layer_data = state.L5_phenomenon
        
        # 简化的信息计算
        if layer == "L1":
            return 1.0 / (1 + layer_data.get("entropy", 0))
        elif layer == "L2":
            return layer_data.get("type_space_dim", 1)
        elif layer == "L3":
            return layer_data.get("discrete_frames", 100) / 100
        elif layer == "L4":
            return layer_data.get("self_coherence", 0.8)
        else:
            return layer_data.get("measurement_fidelity", 0.9)
    
    def evolve_category(self, category: DynamicCategory, dt: float) -> DynamicCategory:
        """演化范畴"""
        new_time = category.time_param + dt
        
        # 简化的范畴演化
        evolved = DynamicCategory(
            name=category.name,
            time_param=new_time,
            objects=category.objects.copy(),
            morphisms=category.morphisms.copy(),
            metadata=category.metadata.copy()
        )
        
        # 更新对象
        for obj_name, obj_data in evolved.objects.items():
            if isinstance(obj_data, dict) and "value" in obj_data:
                obj_data["value"] = obj_data.get("value", 0) * 1.01  # 简化增长
        
        self.categories[new_time] = evolved
        self.current_time = new_time
        
        return evolved
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """获取演化摘要"""
        return {
            "tracked_states": len(self.trajectory),
            "evolution_functors": len(self.evolution_functors),
            "phase_transitions": len(self.phase_transitions),
            "current_time": self.current_time,
            "continuity_equations": {
                layer: len(states) 
                for layer, states in self.continuity_states.items()
            }
        }


# 单例访问
def get_evolution_tracker() -> DynamicCategoryEvolutionTracker:
    """获取动态范畴演化跟踪器单例"""
    return DynamicCategoryEvolutionTracker()


if __name__ == "__main__":
    # 测试动态范畴演化跟踪器
    print("=" * 60)
    print("M93: DynamicCategoryEvolutionTracker - 动态范畴演化跟踪器测试")
    print("=" * 60)
    
    tracker = get_evolution_tracker()
    
    # 测试用例 1: 范畴演化跟踪
    print("\n[测试 1] 跟踪范畴演化")
    trajectory = tracker.track_layer_evolution(None, t_start=0, t_end=10, dt=2)
    print(f"  跟踪了 {len(trajectory)} 个状态点")
    for i, state in enumerate(trajectory):
        fidelity = tracker._compute_state_fidelity(state)
        print(f"  t={i*2}: L1熵={state.L1_taiyi.get('entropy', 0):.3f}, 保真度={fidelity:.4f}")
    
    # 测试用例 2: 相变检测
    print("\n[测试 2] 相变检测")
    # 模拟一个有意产生相变的轨迹
    import math
    artificial_traj = []
    for t in range(10):
        state = tracker._get_system_state(None, t + (5 if t > 5 else 0))  # t>5时产生变化
        artificial_traj.append(state)
    
    transitions = tracker.detect_phase_transition(artificial_traj, threshold=0.1)
    print(f"  检测到 {len(transitions)} 个相变事件")
    for event in transitions:
        print(f"    t={event.time}: {event.severity} drop={event.fidelity_drop:.4f}")
    
    # 测试用例 3: 连续性方程
    print("\n[测试 3] 流贯连续性方程")
    for layer in ["L1", "L2", "L3", "L4", "L5"]:
        eq_state = tracker.compute_continuity_equation(
            layer=layer,
            t=5.0,
            I_t=1.0,
            flux_in=0.8,
            flux_out=0.7,
            sigma=0.1
        )
        print(f"  {layer}: dI/dt={eq_state.dI_dt:.4f}, 平衡={eq_state.balanced}")
    
    # 测试用例 4: 信息守恒检查
    print("\n[测试 4] 信息守恒检查")
    conserved = tracker.check_information_conservation(trajectory)
    print(f"  信息守恒: {conserved}")
    
    # 测试用例 5: 演化摘要
    print("\n[测试 5] 演化摘要")
    summary = tracker.get_evolution_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("M93 测试完成！")
    print("=" * 60)
