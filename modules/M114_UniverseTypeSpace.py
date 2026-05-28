# -*- coding: utf-8 -*-
"""
M114: 类型空间构造 (Universe Type Space)
基于§7.3 HoTT视角的截面搜索理论

核心概念：预训练模型 = Universe U（主类空间）
- 数据 → 类型
- 逻辑 → 态射（纤维）
- 参数 → 证明函数

定理:
  T72 截面存在定理 — ∀(B:Type)(E:Type), ∃s:B→E 当且仅当 curvature_R(B,E) < threshold
  截面s存在 ⟺ 曲率R足够小（逻辑张力不超阈值）

作者: 太乙AGI团队
日期: 2026-05-19
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ==================== 数据结构 ====================

@dataclass
class TypeNode:
    """
    类型节点 — Universe U 中的类型

    每个类型节点对应预训练模型中的一个概念/数据类型，
    包含名称、种类、参数、到根的距离、居住性和曲率信息。
    """
    name: str                           # 类型名称
    kind: str                           # 种类: 'base' | 'function' | 'product' | 'sum' | 'proposition'
    params: List[str] = field(default_factory=list)  # 类型参数
    distance_to_root: float = 0.0       # 到Universe根的距离
    is_inhabited: bool = False          # 是否有人居住（存在构造子/证明）
    curvature: float = 0.0              # 类型处的曲率R（逻辑张力）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'TypeNode':
        """从字典构建TypeNode"""
        return cls(**d)


@dataclass
class LogicFiber:
    """
    逻辑纤维 — B→E的纤维结构

    在HoTT中，纤维丛 p:E→B 的纤维 F_b = p^{-1}(b)。
    逻辑纤维描述了从源类型到目标类型的逻辑映射关系，
    curvature_R 衡量该纤维的"弯曲程度"——即逻辑张力。

    is_trivial=True 表示该纤维是平凡纤维（逻辑映射为恒等或等价）。
    """
    source_type: str                    # 源类型 B
    target_type: str                    # 目标类型 E
    fiber_type: str                     # 纤维类型 F
    curvature_R: float = 0.0           # 曲率R（逻辑张力）
    is_trivial: bool = False           # 是否为平凡纤维

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class TypeDistance:
    """
    类型距离 — 两个类型之间的结构差异度量

    基于类型结构的差异计算距离：参数数量差异、kind差异、
    居住性差异等构成距离函数。
    path 记录从 type_a 到 type_b 的中间类型路径。
    """
    type_a: str                         # 类型A
    type_b: str                         # 类型B
    distance: float = 0.0              # 结构距离
    path: List[str] = field(default_factory=list)  # 路径

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


# ==================== 核心类 ====================

class UniverseTypeSpace:
    """
    M114: Universe Type Space — 类型空间构造

    将预训练模型建模为Universe U（主类空间）：
    - 数据 → 类型 (TypeNode)
    - 逻辑 → 态射/纤维 (LogicFiber)
    - 参数 → 证明函数

    核心功能：
    1. 注册类型到Universe U
    2. 计算类型间距离（结构差异度量）
    3. 构造逻辑纤维（B→E的纤维结构）
    4. 获取类型曲率R（逻辑张力）
    5. 搜索有人居住的类型
    6. 截面存在性检查（定理T72）

    定理T72（截面存在定理）:
    ∀(B:Type)(E:Type), ∃s:B→E ⟺ curvature_R(B,E) < threshold
    截面s存在当且仅当曲率R足够小（逻辑张力不超阈值）。
    当逻辑张力过大时，不存在从B到E的截面，系统应返回Wait。
    """

    def __init__(self):
        """初始化类型空间，加载基础类型"""
        # 类型注册表 {name: TypeNode}
        self.types: Dict[str, TypeNode] = {}

        # 纤维注册表 {(source, target): LogicFiber}
        self.fibers: Dict[Tuple[str, str], LogicFiber] = {}

        # 距离缓存 {(type_a, type_b): TypeDistance}
        self._distance_cache: Dict[Tuple[str, str], TypeDistance] = {}

        # 截面存在性阈值（T72: curvature_R < threshold ⟹ 截面存在）
        self.section_threshold: float = 0.75

        # 统计
        self.total_registrations: int = 0
        self.total_fiber_builds: int = 0
        self.total_section_checks: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

        # 加载基础类型
        self._init_base_types()

    def _init_base_types(self):
        """初始化基础类型 — Universe U 的原始居民"""
        base_types = [
            TypeNode(name='Nat', kind='base', params=[], distance_to_root=0.0,
                     is_inhabited=True, curvature=0.0),
            TypeNode(name='Bool', kind='base', params=[], distance_to_root=0.0,
                     is_inhabited=True, curvature=0.0),
            TypeNode(name='Prop', kind='proposition', params=[], distance_to_root=0.1,
                     is_inhabited=False, curvature=0.1),
            TypeNode(name='Unit', kind='base', params=[], distance_to_root=0.0,
                     is_inhabited=True, curvature=0.0),
            TypeNode(name='Empty', kind='base', params=[], distance_to_root=0.0,
                     is_inhabited=False, curvature=0.0),
            TypeNode(name='Pi', kind='function', params=['A', 'B'], distance_to_root=0.2,
                     is_inhabited=False, curvature=0.15),
            TypeNode(name='Sigma', kind='product', params=['A', 'B'], distance_to_root=0.2,
                     is_inhabited=False, curvature=0.15),
            TypeNode(name='Coproduct', kind='sum', params=['A', 'B'], distance_to_root=0.3,
                     is_inhabited=False, curvature=0.2),
            TypeNode(name='Identity', kind='proposition', params=['A', 'a', 'b'], distance_to_root=0.3,
                     is_inhabited=False, curvature=0.25),
            TypeNode(name='Eq', kind='proposition', params=['A', 'a', 'b'], distance_to_root=0.3,
                     is_inhabited=False, curvature=0.25),
        ]

        for t in base_types:
            self.types[t.name] = t

    def register_type(self, name: str, kind: str, params: Optional[List[str]] = None) -> TypeNode:
        """
        注册类型到Universe U

        在类型空间中创建新的类型节点。如果类型已存在则更新。

        Args:
            name: 类型名称
            kind: 类型种类 ('base' | 'function' | 'product' | 'sum' | 'proposition')
            params: 类型参数列表（默认为空列表）

        Returns:
            注册后的TypeNode
        """
        if params is None:
            params = []

        # 计算到根的距离：基于kind和参数数量
        kind_base_distances = {
            'base': 0.0,
            'function': 0.2,
            'product': 0.2,
            'sum': 0.3,
            'proposition': 0.1
        }
        base_distance = kind_base_distances.get(kind, 0.2)
        param_distance = len(params) * 0.1
        distance_to_root = round(base_distance + param_distance, 4)

        # 初始曲率：基于距离和参数复杂度
        curvature = round(distance_to_root * 0.5 + len(params) * 0.05, 4)

        # 检查是否有人居住：base类型且无参数通常有人居住
        is_inhabited = kind == 'base' and len(params) == 0

        type_node = TypeNode(
            name=name,
            kind=kind,
            params=params,
            distance_to_root=distance_to_root,
            is_inhabited=is_inhabited,
            curvature=curvature
        )

        self.types[name] = type_node
        self.total_registrations += 1

        # 清除相关距离缓存
        keys_to_remove = [k for k in self._distance_cache if name in k]
        for k in keys_to_remove:
            del self._distance_cache[k]

        self.last_update = time.time()
        return type_node

    def compute_type_distance(self, type_a: str, type_b: str) -> float:
        """
        计算两个类型之间的"距离"（基于结构差异）

        类型距离基于以下维度：
        1. kind差异（不同种类距离更大）
        2. 参数数量差异
        3. 居住性差异
        4. 根距离差异
        5. 曲率差异

        Args:
            type_a: 类型A名称
            type_b: 类型B名称

        Returns:
            类型距离（非负浮点数，0表示相同类型）
        """
        # 检查缓存
        cache_key = (min(type_a, type_b), max(type_a, type_b))
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key].distance

        # 相同类型距离为0
        if type_a == type_b:
            return 0.0

        node_a = self.types.get(type_a)
        node_b = self.types.get(type_b)

        if node_a is None or node_b is None:
            # 未知类型距离设为最大值
            return 1.0

        # 1. kind差异
        kind_distance = 0.0 if node_a.kind == node_b.kind else 0.3

        # 2. 参数数量差异
        param_diff = abs(len(node_a.params) - len(node_b.params))
        param_distance = round(param_diff * 0.15, 4)

        # 3. 居住性差异
        inhabitation_distance = 0.0 if node_a.is_inhabited == node_b.is_inhabited else 0.2

        # 4. 根距离差异
        root_distance = round(abs(node_a.distance_to_root - node_b.distance_to_root), 4)

        # 5. 曲率差异
        curvature_distance = round(abs(node_a.curvature - node_b.curvature) * 0.5, 4)

        # 6. 名称差异（同kind不同名称仍应有非零距离）
        name_distance = 0.0 if type_a == type_b else 0.1

        # 综合距离 = 各维度加权和
        total_distance = round(
            kind_distance + param_distance + inhabitation_distance +
            root_distance + curvature_distance + name_distance, 4
        )

        # 确保距离在[0, 1]区间
        total_distance = min(1.0, max(0.0, total_distance))

        # 缓存
        path = [type_a, type_b]
        self._distance_cache[cache_key] = TypeDistance(
            type_a=cache_key[0],
            type_b=cache_key[1],
            distance=total_distance,
            path=path
        )

        return total_distance

    def build_logic_fiber(self, source: str, target: str, fiber_type: str = '') -> LogicFiber:
        """
        构造逻辑纤维 — B→E的纤维结构

        在HoTT中，纤维丛 p:E→B 将全空间E投影到底空间B，
        纤维 F_b = p^{-1}(b) 是B中点b上的纤维。
        逻辑纤维描述从source到target的逻辑映射。

        curvature_R衡量纤维的"弯曲程度"——逻辑张力。
        is_trivial=True表示该纤维是平凡纤维（逻辑映射为恒等或等价）。

        Args:
            source: 源类型 B（底空间）
            target: 目标类型 E（全空间）
            fiber_type: 纤维类型 F（默认自动推导为"F_{source}_{target}"）

        Returns:
            LogicFiber: 构造的逻辑纤维
        """
        if not fiber_type:
            fiber_type = f"F_{source}_{target}"

        # 计算曲率R：基于源和目标的类型距离
        type_distance = self.compute_type_distance(source, target)

        # 获取源和目标类型节点
        source_node = self.types.get(source)
        target_node = self.types.get(target)

        # 曲率R计算：
        # - 类型距离越大，曲率越大
        # - 居住性不对称增加曲率
        # - 参数复杂度差异增加曲率
        source_curvature = source_node.curvature if source_node else 0.0
        target_curvature = target_node.curvature if target_node else 0.0

        # 曲率R = 类型距离 + 源目标曲率平均
        curvature_R = round(
            type_distance * 0.6 + (source_curvature + target_curvature) * 0.2, 4
        )
        curvature_R = min(1.0, max(0.0, curvature_R))

        # 判断是否为平凡纤维
        # 平凡纤维条件：源和目标kind相同，且参数一致，曲率很小
        is_trivial = False
        if source_node and target_node:
            is_trivial = (
                source_node.kind == target_node.kind and
                source_node.params == target_node.params and
                curvature_R < 0.1
            )

        fiber = LogicFiber(
            source_type=source,
            target_type=target,
            fiber_type=fiber_type,
            curvature_R=curvature_R,
            is_trivial=is_trivial
        )

        self.fibers[(source, target)] = fiber
        self.total_fiber_builds += 1
        self.last_update = time.time()

        return fiber

    def get_curvature(self, type_name: str) -> float:
        """
        获取类型处的曲率R（逻辑张力）

        曲率R衡量类型处的逻辑张力：
        - R ≈ 0: 该类型的逻辑路径平坦，推理容易
        - R → 1: 该类型的逻辑路径高度弯曲，推理困难

        如果类型未注册，返回默认曲率0.5。

        Args:
            type_name: 类型名称

        Returns:
            曲率R值，范围[0, 1]
        """
        type_node = self.types.get(type_name)
        if type_node is None:
            return 0.5

        # 基础曲率
        base_curvature = type_node.curvature

        # 考虑该类型参与的纤维的曲率贡献
        fiber_contributions: List[float] = []
        for (source, target), fiber in self.fibers.items():
            if source == type_name or target == type_name:
                fiber_contributions.append(fiber.curvature_R)

        # 综合曲率 = 基础曲率 + 纤维曲率贡献的加权平均
        if fiber_contributions:
            avg_fiber_curvature = sum(fiber_contributions) / len(fiber_contributions)
            combined_curvature = round(
                base_curvature * 0.6 + avg_fiber_curvature * 0.4, 4
            )
        else:
            combined_curvature = base_curvature

        return min(1.0, max(0.0, combined_curvature))

    def search_inhabited_types(self, base_type: str) -> List[TypeNode]:
        """
        搜索有人居住的类型

        给定基类型base_type，搜索Universe U中所有有人居住的类型，
        按与base_type的距离排序（距离近的优先）。

        有人居住的类型（is_inhabited=True）表示存在构造子/证明，
        即该类型不是空的——可以从中提取值。

        Args:
            base_type: 基类型名称

        Returns:
            按距离排序的有人居住的类型列表
        """
        inhabited: List[TypeNode] = []
        for type_node in self.types.values():
            if type_node.is_inhabited and type_node.name != base_type:
                distance = self.compute_type_distance(base_type, type_node.name)
                inhabited.append(type_node)

        # 按距离排序
        inhabited.sort(key=lambda t: self.compute_type_distance(base_type, t.name))

        return inhabited

    def check_section_existence(self, base_type: str, total_type: str) -> bool:
        """
        截面存在性检查 — 定理T72

        定理T72（截面存在定理）:
        ∀(B:Type)(E:Type), ∃s:B→E ⟺ curvature_R(B,E) < threshold

        截面s存在当且仅当曲率R足够小（逻辑张力不超阈值）。
        当逻辑张力过大时，不存在从B到E的截面。

        物理含义：
        - 截面存在 → 推理路径可达，可以构造证明
        - 截面不存在 → 推理路径不可达，应返回Wait而非幻觉

        Args:
            base_type: 底空间B类型
            total_type: 全空间E类型

        Returns:
            True如果截面存在（curvature_R < threshold），False否则
        """
        self.total_section_checks += 1

        # 获取或构造纤维以计算曲率
        fiber_key = (base_type, total_type)
        if fiber_key in self.fibers:
            curvature_R = self.fibers[fiber_key].curvature_R
        else:
            # 动态计算曲率
            fiber = self.build_logic_fiber(base_type, total_type)
            curvature_R = fiber.curvature_R

        # T72判定: 截面存在 ⟺ curvature_R < threshold
        section_exists = curvature_R < self.section_threshold

        self.last_update = time.time()
        return section_exists

    def identify_undecidable_regions(self) -> List[TypeNode]:
        """
        识别不可判定区域 — 与定理T74关联

        在Universe U中识别曲率R接近或超过阈值的类型，
        这些类型所在的区域可能包含不可判定命题。

        不可判定区域特征：
        - 曲率R ≥ threshold * 0.8（接近阈值）
        - 无人居住（is_inhabited=False）
        - 参与的纤维曲率较高

        Returns:
            疑似不可判定区域的类型列表
        """
        undecidable: List[TypeNode] = []

        for type_node in self.types.values():
            curvature = self.get_curvature(type_node.name)
            # 高曲率 + 无人居住 = 潜在不可判定区域
            if curvature >= self.section_threshold * 0.8 and not type_node.is_inhabited:
                undecidable.append(type_node)

        # 按曲率降序排列（最可能不可判定的在前）
        undecidable.sort(key=lambda t: self.get_curvature(t.name), reverse=True)

        return undecidable

    def get_state(self) -> Dict[str, Any]:
        """
        获取类型空间状态

        Returns:
            类型空间状态字典，包含：
            - total_types: 已注册类型数
            - total_fibers: 已构造纤维数
            - inhabited_count: 有人居住类型数
            - undecidable_regions: 不可判定区域数
            - section_threshold: 截面存在性阈值
            - avg_curvature: 平均曲率
        """
        # 计算平均曲率
        if self.types:
            curvatures = [self.get_curvature(name) for name in self.types]
            avg_curvature = round(sum(curvatures) / len(curvatures), 4)
        else:
            avg_curvature = 0.0

        inhabited_count = sum(1 for t in self.types.values() if t.is_inhabited)
        undecidable_regions = self.identify_undecidable_regions()

        return {
            'total_types': len(self.types),
            'total_fibers': len(self.fibers),
            'inhabited_count': inhabited_count,
            'uninhabited_count': len(self.types) - inhabited_count,
            'undecidable_regions': len(undecidable_regions),
            'section_threshold': self.section_threshold,
            'avg_curvature': avg_curvature,
            'total_registrations': self.total_registrations,
            'total_fiber_builds': self.total_fiber_builds,
            'total_section_checks': self.total_section_checks,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T72': '截面存在: curvature_R < threshold ⟹ ∃s:B→E'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新类型空间状态

        Args:
            data: 可选更新数据，支持：
                - register: 注册新类型 {name, kind, params}
                - fiber: 构造纤维 {source, target, fiber_type}
                - section_check: 截面检查 {base_type, total_type}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'register' or 'register' in data:
                reg = data.get('register', data)
                self.register_type(
                    name=reg.get('name', ''),
                    kind=reg.get('kind', 'base'),
                    params=reg.get('params', [])
                )
            elif action == 'fiber' or 'fiber' in data:
                fib = data.get('fiber', data)
                self.build_logic_fiber(
                    source=fib.get('source', ''),
                    target=fib.get('target', ''),
                    fiber_type=fib.get('fiber_type', '')
                )
            elif action == 'section_check' or 'section_check' in data:
                chk = data.get('section_check', data)
                self.check_section_existence(
                    base_type=chk.get('base_type', ''),
                    total_type=chk.get('total_type', '')
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示类型空间的核心功能"""
        # 1. 注册一些自定义类型
        self.register_type('List_Nat', 'function', ['Nat'])
        self.register_type('Maybe_Bool', 'sum', ['Bool'])
        self.register_type('Vec', 'function', ['Nat', 'A'])
        self.register_type('IsEven', 'proposition', ['Nat'])

        # 2. 构造逻辑纤维
        fiber1 = self.build_logic_fiber('Nat', 'Bool')
        fiber2 = self.build_logic_fiber('Nat', 'List_Nat')
        fiber3 = self.build_logic_fiber('Bool', 'Prop')
        fiber4 = self.build_logic_fiber('Nat', 'Empty')

        # 3. 计算类型距离
        d1 = self.compute_type_distance('Nat', 'Bool')
        d2 = self.compute_type_distance('Nat', 'List_Nat')
        d3 = self.compute_type_distance('Pi', 'Sigma')

        # 4. 获取曲率
        c1 = self.get_curvature('Nat')
        c2 = self.get_curvature('Pi')
        c3 = self.get_curvature('Empty')

        # 5. 截面存在性检查（T72）
        s1 = self.check_section_existence('Nat', 'Bool')
        s2 = self.check_section_existence('Nat', 'Empty')
        s3 = self.check_section_existence('Bool', 'Nat')

        # 6. 搜索有人居住的类型
        inhabited = self.search_inhabited_types('Nat')

        # 7. 识别不可判定区域
        undecidable = self.identify_undecidable_regions()

        return {
            'fibers': {
                'Nat→Bool': {'curvature_R': fiber1.curvature_R, 'is_trivial': fiber1.is_trivial},
                'Nat→List_Nat': {'curvature_R': fiber2.curvature_R, 'is_trivial': fiber2.is_trivial},
                'Bool→Prop': {'curvature_R': fiber3.curvature_R, 'is_trivial': fiber3.is_trivial},
                'Nat→Empty': {'curvature_R': fiber4.curvature_R, 'is_trivial': fiber4.is_trivial},
            },
            'distances': {
                'Nat↔Bool': d1,
                'Nat↔List_Nat': d2,
                'Pi↔Sigma': d3
            },
            'curvatures': {'Nat': c1, 'Pi': c2, 'Empty': c3},
            'section_existence_T72': {
                'Nat→Bool': s1,
                'Nat→Empty': s2,
                'Bool→Nat': s3
            },
            'inhabited_types': [t.name for t in inhabited],
            'undecidable_regions': [t.name for t in undecidable],
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[UniverseTypeSpace] = None


def get_instance() -> UniverseTypeSpace:
    """
    获取UniverseTypeSpace单例实例

    Returns:
        UniverseTypeSpace全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = UniverseTypeSpace()
    return _instance


def register_type(name: str, kind: str, params: Optional[List[str]] = None) -> TypeNode:
    """注册类型到Universe U（快捷接口）"""
    return get_instance().register_type(name, kind, params)


def compute_type_distance(type_a: str, type_b: str) -> float:
    """计算类型距离（快捷接口）"""
    return get_instance().compute_type_distance(type_a, type_b)


def build_logic_fiber(source: str, target: str, fiber_type: str = '') -> LogicFiber:
    """构造逻辑纤维（快捷接口）"""
    return get_instance().build_logic_fiber(source, target, fiber_type)


def get_curvature(type_name: str) -> float:
    """获取类型曲率R（快捷接口）"""
    return get_instance().get_curvature(type_name)


def search_inhabited_types(base_type: str) -> List[TypeNode]:
    """搜索有人居住的类型（快捷接口）"""
    return get_instance().search_inhabited_types(base_type)


def check_section_existence(base_type: str, total_type: str) -> bool:
    """截面存在性检查 — 定理T72（快捷接口）"""
    return get_instance().check_section_existence(base_type, total_type)


def identify_undecidable_regions() -> List[TypeNode]:
    """识别不可判定区域（快捷接口）"""
    return get_instance().identify_undecidable_regions()


def get_state() -> Dict[str, Any]:
    """获取类型空间状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新类型空间状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
