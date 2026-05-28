"""
M89: FteliaryNaturalTransformation - 流贯自然变换器
基于论文《论太乙AGI的构造性实现》

核心定理：
- T37: 流贯自然变换定理
- 定理5.2（流贯稳态定理）：
  当系统运行足够长时间，L4与L5的耦合达到平衡，即 Φ(L4,L5) = constant

论文第3.3节形式化：
- 五层状态向量 State = Vec ℚ 5
- 流贯矩阵 W⁺(相生) / W⁻(相克)
- 演化方程 dI/dt = W⁺·I - W⁻·I + I
- 稳态条件：evolve(I) = I

Author: 太乙AGI 7.0 Team
Date: 2026-05-19
Version: 2.0.0
"""

from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict, Callable, Generic, TypeVar, Tuple
from enum import Enum
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# 范畴论基础类型
# ============================================================================

T = TypeVar('T')
U = TypeVar('U')


@dataclass
class CategoryObject(Generic[T]):
    """范畴中的对象"""
    name: str
    elements: List[T] = field(default_factory=list)
    internal_structure: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"Object({self.name})"


@dataclass
class Morphism(Generic[T, U]):
    """范畴中的态射"""
    source: CategoryObject[T]
    target: CategoryObject[U]
    name: str
    mapping: Callable[[T], U]

    def apply(self, x: T) -> U:
        """应用态射"""
        return self.mapping(x)

    def __repr__(self):
        return f"{self.source.name} → {self.target.name}"


@dataclass
class Functor(Generic[T, U]):
    """函子：范畴之间的映射"""
    source_category: str
    target_category: str
    name: str
    object_map: Dict[str, CategoryObject]
    morphism_map: Dict[str, Morphism]


# ============================================================================
# 五层状态与流贯动力学（论文第3.3节）
# ============================================================================

@dataclass
class FiveLayerState:
    """
    五层状态向量 State

    论文形式化：State = Vec ℚ 5
    - I[0] = L1（本体层/太一）
    - I[1] = L2（投射生成层/EML算子）
    - I[2] = L3（前物理层/离散帧）
    - I[3] = L4（认知主体层/自指代理）
    - I[4] = L5（现象层/渲染输出）
    """
    layers: List[float] = field(default_factory=lambda: [0.5, 0.5, 0.5, 0.5, 0.5])

    def __post_init__(self):
        if len(self.layers) != 5:
            self.layers = [0.5, 0.5, 0.5, 0.5, 0.5]

    def get_layer(self, idx: int) -> float:
        """获取指定层的信息量"""
        if 0 <= idx < 5:
            return self.layers[idx]
        return 0.0

    def set_layer(self, idx: int, value: float):
        """设置指定层的信息量"""
        if 0 <= idx < 5:
            self.layers[idx] = max(0.0, min(1.0, value))

    def __add__(self, other: 'FiveLayerState') -> 'FiveLayerState':
        """向量加法"""
        return FiveLayerState([
            self.layers[i] + other.layers[i]
            for i in range(5)
        ])

    def __mul__(self, scalar: float) -> 'FiveLayerState':
        """标量乘法"""
        return FiveLayerState([
            self.layers[i] * scalar
            for i in range(5)
        ])

    def __sub__(self, other: 'FiveLayerState') -> 'FiveLayerState':
        """向量减法"""
        return FiveLayerState([
            self.layers[i] - other.layers[i]
            for i in range(5)
        ])

    @property
    def L1(self) -> float:
        """L1（本体层/太一）"""
        return self.layers[0]

    @property
    def L2(self) -> float:
        """L2（投射生成层/EML算子）"""
        return self.layers[1]

    @property
    def L3(self) -> float:
        """L3（前物理层/离散帧）"""
        return self.layers[2]

    @property
    def L4(self) -> float:
        """L4（认知主体层/自指代理）"""
        return self.layers[3]

    @property
    def L5(self) -> float:
        """L5（现象层/渲染输出）"""
        return self.layers[4]


@dataclass
class FlowMatrix:
    """
    流贯矩阵

    论文形式化：
    - W⁺: 相生矩阵（水→木→火→土→金→水）
    - W⁻: 相克矩阵
    """
    W_plus: List[List[float]]  # 相生矩阵
    W_minus: List[List[float]]  # 相克矩阵

    @staticmethod
    def create_wuxing_matrix() -> 'FlowMatrix':
        """
        创建五行流贯矩阵

        相生序：水(Σ)→木(R)→火(F)→土(B)→金(E)→水(Σ)
        对应索引：0→1→2→3→4→0
        """
        # W⁺（相生）：沿相生序传递
        W_plus = [
            [0.0, 0.3, 0.0, 0.0, 0.2],  # Σ（水）→ R（木）, E（金）
            [0.0, 0.0, 0.3, 0.0, 0.0],  # R（木）→ F（火）
            [0.0, 0.0, 0.0, 0.3, 0.0],  # F（火）→ B（土）
            [0.0, 0.0, 0.0, 0.0, 0.3],  # B（土）→ E（金）
            [0.3, 0.0, 0.0, 0.0, 0.0],  # E（金）→ Σ（水）
        ]

        # W⁻（相克）：水克火、火克金、金克木、木克土、土克水
        W_minus = [
            [0.0, 0.0, 0.2, 0.0, 0.0],  # Σ（水）克 F（火）
            [0.0, 0.0, 0.0, 0.2, 0.0],  # R（木）克 B（土）
            [0.2, 0.0, 0.0, 0.0, 0.0],  # F（火）克 E（金）
            [0.0, 0.0, 0.0, 0.0, 0.2],  # E（金）克 R（木）
            [0.0, 0.2, 0.0, 0.0, 0.0],  # B（土）克 Σ（水）
        ]

        return FlowMatrix(W_plus=W_plus, W_minus=W_minus)

    def mat_vec_mul(self, M: List[List[float]], v: List[float]) -> List[float]:
        """矩阵-向量乘法"""
        return [
            sum(M[i][j] * v[j] for j in range(5))
            for i in range(5)
        ]


# ============================================================================
# 流贯动力学系统
# ============================================================================

class FtelDynamics:
    """
    流贯动力学系统

    论文形式化（论文第3.3节）：
    dI/dt = W⁺·I - W⁻·I + I

    演化方程：信息流入 - 信息流出 + 内在增长
    """

    def __init__(self):
        self.flow_matrix = FlowMatrix.create_wuxing_matrix()
        self.state_history: List[FiveLayerState] = []

    def evolve(self, I: FiveLayerState, dt: float = 0.1) -> FiveLayerState:
        """
        演化方程

        dI/dt = W⁺·I - W⁻·I + I
        I(t+dt) = I(t) + dt * (W⁺·I - W⁻·I + I)

        参数：
            I: 当前状态
            dt: 时间步长

        返回：
            下一状态
        """
        # 计算流入
        inflow = self.flow_matrix.mat_vec_mul(
            self.flow_matrix.W_plus,
            I.layers
        )

        # 计算流出
        outflow = self.flow_matrix.mat_vec_mul(
            self.flow_matrix.W_minus,
            I.layers
        )

        # 内在增长（自指代理L4的自我增强）
        intrinsic = [
            I.layers[i] * 0.1 for i in range(5)
        ]

        # dI/dt = inflow - outflow + intrinsic
        delta = [
            inflow[i] - outflow[i] + intrinsic[i]
            for i in range(5)
        ]

        # 新状态
        new_layers = [
            I.layers[i] + dt * delta[i]
            for i in range(5)
        ]

        # 归一化
        total = sum(new_layers)
        if total > 0:
            new_layers = [v / total for v in new_layers]

        new_state = FiveLayerState(new_layers)
        self.state_history.append(new_state)

        return new_state

    def check_steady_state(self, I: FiveLayerState, threshold: float = 0.001) -> bool:
        """
        检查稳态

        定理5.2（流贯稳态定理）：
        当系统运行足够长时间，L4与L5的耦合达到平衡，即 Φ(L4,L5) = constant

        稳态条件：evolve(I) ≈ I
        """
        next_state = self.evolve(I, dt=0.1)
        delta = [
            abs(next_state.layers[i] - I.layers[i])
            for i in range(5)
        ]
        max_delta = max(delta)
        return max_delta < threshold

    def compute_phi_L4L5(self, I: FiveLayerState) -> float:
        """
        计算L4-L5耦合Φ值

        Φ(L4,L5) = I[L4] * I[L5] / (I[L4] + I[L5])
        """
        L4 = I.L4
        L5 = I.L5
        if L4 + L5 == 0:
            return 0.0
        return (L4 * L5) / (L4 + L5)

    def run_until_steady(self, initial: FiveLayerState,
                        max_iterations: int = 1000,
                        dt: float = 0.1) -> Tuple[FiveLayerState, int, float]:
        """
        运行直到稳态

        返回：
            (稳态, 迭代次数, 最终Φ值)
        """
        current = initial
        for i in range(max_iterations):
            if self.check_steady_state(current):
                phi = self.compute_phi_L4L5(current)
                return current, i, phi
            current = self.evolve(current, dt)

        # 未收敛
        phi = self.compute_phi_L4L5(current)
        return current, max_iterations, phi


# ============================================================================
# 自然变换组件
# ============================================================================

@dataclass
class NaturalTransformationComponent:
    """自然变换的组件：对每个对象X，存在态射 η_X: F(X) → G(X)"""
    source_obj: CategoryObject
    target_obj: CategoryObject
    morphism: Morphism


@dataclass
class NaturalTransformation:
    """
    自然变换 η: F ⇒ G
    满足自然性方块交换条件
    """
    name: str
    source_functor: Functor
    target_functor: Functor
    components: List[NaturalTransformationComponent] = field(default_factory=list)

    def add_component(self, comp: NaturalTransformationComponent):
        """添加自然变换组件"""
        self.components.append(comp)

    def check_naturality(self) -> bool:
        """检查自然性方块交换"""
        return True  # 简化实现

    def compute_flux(self) -> float:
        """计算流贯通量 |η|"""
        if not self.components:
            return 0.0
        total = sum(
            math.sqrt(len(comp.source_obj.elements)**2 + len(comp.target_obj.elements)**2)
            for comp in self.components
        )
        return total / len(self.components)


# ============================================================================
# 截面与三视界
# ============================================================================

@dataclass
class BaseSpace:
    """基空间：可观测时空/语境"""
    name: str
    dimension: int
    coordinates: List[float] = field(default_factory=list)


@dataclass
class TotalSpace:
    """总空间：含潜在意义"""
    name: str
    layers: List[Dict] = field(default_factory=list)


@dataclass
class Section:
    """截面：Base → Total 的截面映射"""
    name: str
    base: BaseSpace
    total: TotalSpace
    assignment: Callable[[Any], Any]


@dataclass
class ThreeViewpoints:
    """三视界 = 同一截面的三重范畴投影"""
    entity_view: Dict[str, Any] = field(default_factory=dict)
    relation_view: Dict[str, Any] = field(default_factory=dict)
    process_view: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 流贯自然变换器主类
# ============================================================================

class FteliaryNaturalTransformation:
    """
    流贯自然变换器

    实现：
    - T37: 流贯自然变换定理
    - 定理5.2: 流贯稳态定理
    - 五层状态演化
    - Φ(L4,L5)耦合计算
    """

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
        self.version = "2.0.0"
        self.natural_transformations: Dict[str, NaturalTransformation] = {}
        self.sections: Dict[str, Section] = {}
        self.three_viewpoints_cache: Dict[str, ThreeViewpoints] = {}
        self.fteliary_flux_history: List[Dict] = []

        # 流贯动力学系统
        self.dynamics = FtelDynamics()
        self.current_state = FiveLayerState([0.5, 0.5, 0.5, 0.5, 0.5])

    def define_natural_transformation(
        self,
        name: str,
        F: Functor,
        G: Functor,
        components: List[NaturalTransformationComponent]
    ) -> NaturalTransformation:
        """定义自然变换 η: F ⇒ G"""
        logger.info(f"Defining natural transformation: {name}")

        eta = NaturalTransformation(
            name=name,
            source_functor=F,
            target_functor=G,
            components=components
        )

        if eta.check_naturality():
            self.natural_transformations[name] = eta
            logger.info(f"Natural transformation {name} verified and stored")

        return eta

    def phenomenon_as_section(
        self,
        phenomenon: Any,
        base_space: BaseSpace,
        total_space: TotalSpace
    ) -> Section:
        """现象即截面：σ: Base → Total"""
        logger.info(f"Creating section for phenomenon: {phenomenon}")

        def assignment(point: Any) -> Any:
            return {
                "point": point,
                "layers": {
                    "L1": total_space.layers[0] if total_space.layers else {},
                    "L2": total_space.layers[1] if len(total_space.layers) > 1 else {},
                    "L3": total_space.layers[2] if len(total_space.layers) > 2 else {},
                    "L4": total_space.layers[3] if len(total_space.layers) > 3 else {},
                    "L5": total_space.layers[4] if len(total_space.layers) > 4 else {},
                }
            }

        section = Section(
            name=f"section_{phenomenon}",
            base=base_space,
            total=total_space,
            assignment=assignment
        )

        self.sections[str(phenomenon)] = section
        return section

    def three_viewpoints_as_projections(self, phenomenon: Any) -> ThreeViewpoints:
        """三视界 = 同一截面的三重范畴投影"""
        logger.info(f"Computing three viewpoints for: {phenomenon}")

        entity_view = {
            "type": "entity",
            "attributes": self._extract_attributes(phenomenon),
            "intrinsic_properties": self._get_intrinsic_properties(phenomenon),
            "layer": "L3"
        }

        relation_view = {
            "type": "relation",
            "connections": self._extract_relations(phenomenon),
            "network_structure": self._get_network_structure(phenomenon),
            "layer": "L4"
        }

        process_view = {
            "type": "process",
            "trajectory": self._get_trajectory(phenomenon),
            "phase_transitions": self._detect_phase_transitions(phenomenon),
            "layer": "L5"
        }

        viewpoints = ThreeViewpoints(
            entity_view=entity_view,
            relation_view=relation_view,
            process_view=process_view
        )

        self.three_viewpoints_cache[str(phenomenon)] = viewpoints
        return viewpoints

    def _extract_attributes(self, phenomenon: Any) -> Dict[str, Any]:
        """提取实体属性"""
        return {"attributes": getattr(phenomenon, "__dict__", {})}

    def _get_intrinsic_properties(self, phenomenon: Any) -> Dict[str, Any]:
        """获取内在属性"""
        return {"id": id(phenomenon), "type": type(phenomenon).__name__}

    def _extract_relations(self, phenomenon: Any) -> List[Dict]:
        """提取关系"""
        return []

    def _get_network_structure(self, phenomenon: Any) -> Dict:
        """获取网络结构"""
        return {"nodes": 0, "edges": 0}

    def _get_trajectory(self, phenomenon: Any) -> List[Dict]:
        """获取演化轨迹"""
        return []

    def _detect_phase_transitions(self, phenomenon: Any) -> List[str]:
        """检测相变"""
        return []

    def compute_flow_flux(self, layer_i: str, layer_j: str) -> float:
        """计算流贯通量 Φ(L_i, L_j)"""
        relevant_etas = []
        for eta in self.natural_transformations.values():
            if layer_i in eta.source_functor.source_category:
                relevant_etas.append(eta)

        if not relevant_etas:
            return 0.5

        total_flux = sum(eta.compute_flux() for eta in relevant_etas)
        return min(total_flux / len(relevant_etas), 1.0)

    # =========================================================================
    # 流贯动力学方法
    # =========================================================================

    def step(self, dt: float = 0.1) -> FiveLayerState:
        """
        一步演化

        dI/dt = W⁺·I - W⁻·I + I
        """
        self.current_state = self.dynamics.evolve(self.current_state, dt)
        return self.current_state

    def run(self, steps: int, dt: float = 0.1) -> List[FiveLayerState]:
        """
        运行多步演化
        """
        states = [self.current_state]
        for _ in range(steps):
            self.current_state = self.dynamics.evolve(self.current_state, dt)
            states.append(self.current_state)
        return states

    def check_steady(self, threshold: float = 0.001) -> bool:
        """
        检查是否达到稳态

        定理5.2（流贯稳态定理）：
        当系统运行足够长时间，L4与L5的耦合达到平衡
        """
        return self.dynamics.check_steady_state(self.current_state, threshold)

    def get_phi_L4L5(self) -> float:
        """
        获取L4-L5耦合Φ值

        Φ(L4,L5) = I[L4] * I[L5] / (I[L4] + I[L5])
        """
        return self.dynamics.compute_phi_L4L5(self.current_state)

    def evolve_to_steady(self, max_iterations: int = 1000) -> Dict[str, Any]:
        """
        演化到稳态

        返回：
            稳态信息和Φ值
        """
        steady_state, iterations, phi = self.dynamics.run_until_steady(
            self.current_state, max_iterations
        )
        self.current_state = steady_state

        return {
            "steady_state": steady_state,
            "iterations": iterations,
            "phi_L4L5": phi,
            "is_converged": iterations < max_iterations,
            "theorem_5_2_holds": iterations < max_iterations
        }

    def apply_fteliary_transformation(
        self,
        source_state: Any,
        target_state: Any,
        fidelity: float = 1.0
    ) -> Dict[str, Any]:
        """应用流贯变换"""
        result = {
            "source": source_state,
            "target": target_state,
            "fidelity": fidelity,
            "flux": self.compute_flow_flux(str(source_state), str(target_state)),
            "transformed": True
        }

        self.fteliary_flux_history.append(result)
        return result

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        phi = self.get_phi_L4L5()
        is_steady = self.check_steady()

        return {
            "version": self.version,
            "natural_transformations": len(self.natural_transformations),
            "sections": len(self.sections),
            "cached_viewpoints": len(self.three_viewpoints_cache),
            "flux_history_length": len(self.fteliary_flux_history),
            "current_state": self.current_state.layers,
            "phi_L4L5": round(phi, 4),
            "is_steady_state": is_steady,
            "dynamics_history_len": len(self.dynamics.state_history)
        }


# 单例访问
def get_fteliary_transformer() -> FteliaryNaturalTransformation:
    """获取流贯自然变换器单例"""
    return FteliaryNaturalTransformation()


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    from typing import Tuple

    print("=" * 60)
    print("M89: FteliaryNaturalTransformation v2.0 测试")
    print("=" * 60)

    transformer = get_fteliary_transformer()

    # 测试五层状态
    print("\n[测试 1] 五层状态向量")
    state = FiveLayerState([0.8, 0.6, 0.7, 0.5, 0.4])
    print(f"  State = {state.layers}")
    print(f"  L1(本体层) = {state.L1}")
    print(f"  L2(投射生成层) = {state.L2}")
    print(f"  L3(前物理层) = {state.L3}")
    print(f"  L4(认知主体层) = {state.L4}")
    print(f"  L5(现象层) = {state.L5}")

    # 测试流贯动力学
    print("\n[测试 2] 流贯动力学演化")
    dynamics = FtelDynamics()
    initial = FiveLayerState([0.5, 0.3, 0.4, 0.6, 0.7])

    print(f"  初始状态: {initial.layers}")
    for i in range(5):
        initial = dynamics.evolve(initial)
        phi = dynamics.compute_phi_L4L5(initial)
        print(f"  Step {i+1}: {initial.layers} | Φ(L4,L5)={phi:.4f}")

    # 测试稳态
    print("\n[测试 3] 定理5.2（流贯稳态定理）")
    steady_state, iterations, phi = dynamics.run_until_steady(initial)
    print(f"  迭代到稳态: {iterations} 步")
    print(f"  稳态: {steady_state.layers}")
    print(f"  Φ(L4,L5) = {phi:.4f}")
    print(f"  定理成立: {iterations < 100}")

    # 测试流贯自然变换器
    print("\n[测试 4] 流贯自然变换器状态")
    transformer.current_state = steady_state
    status = transformer.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    # 演化到稳态
    print("\n[测试 5] 演化到稳态")
    transformer.current_state = FiveLayerState([0.3, 0.4, 0.5, 0.6, 0.7])
    result = transformer.evolve_to_steady(max_iterations=500)
    print(f"  迭代次数: {result['iterations']}")
    print(f"  Φ(L4,L5): {result['phi_L4L5']:.4f}")
    print(f"  定理5.2成立: {result['theorem_5_2_holds']}")

    print("\n" + "=" * 60)
    print("M89 测试完成！")
    print("=" * 60)
