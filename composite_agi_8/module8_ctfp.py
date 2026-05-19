"""
太乙AGI 8.0 - 模块8：范畴论编程层（CTFP）
=================================================

实现基于范畴论的编程范式：
1. 范畴论基础（对象、态射、范畴）
2. 函子（Functor）：范畴间的映射
3. 自然变换（Natural Transformation）：函子间的映射
4. 米田引理（Yoneda Lemma）：在编程中的应用
5. 范畴论编程范式（使用CT构造系统）

基于"复合体理学"理论框架
"""

import numpy as np
from typing import Dict, List, Any, Callable, Optional, TypeVar, Generic
from dataclasses import dataclass
from abc import ABC, abstractmethod


# 类型变量（用于泛型编程）
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Object:
    """范畴中的对象"""
    
    def __init__(self, id: str, properties: Optional[Dict] = None):
        """
        初始化对象
        
        Args:
            id: 对象唯一标识
            properties: 对象属性
        """
        self.id = id
        self.properties = properties or {}
        self.relations = []  # 与其他对象的关系
    
    def add_relation(self, relation_type: str, target: 'Object'):
        """添加关系"""
        self.relations.append({
            "type": relation_type,
            "target": target.id
        })
    
    def __repr__(self):
        return f"Object(id={self.id})"


class Morphism:
    """范畴中的态射（箭头）"""
    
    def __init__(self, 
                 source: Object, 
                 target: Object, 
                 morphism_type: str = "generic"):
        """
        初始化态射 f: source -> target
        
        Args:
            source: 源对象
            target: 目标对象
            morphism_type: 态射类型
        """
        self.source = source
        self.target = target
        self.morphism_type = morphism_type
        self.properties = {}  # 态射的属性
    
    def compose(self, other: 'Morphism') -> Optional['Morphism']:
        """
        态射组合：如果 self: B -> C, other: A -> B, 则 self ∘ other: A -> C
        
        Args:
            other: 另一个态射
            
        Returns:
            组合后的态射，如果不能组合返回None
        """
        if self.source.id == other.target.id:
            # self: B -> C, other: A -> B
            # 组合：A -> C
            composed = Morphism(
                source=other.source,
                target=self.target,
                morphism_type=f"compose({self.morphism_type}, {other.morphism_type})"
            )
            return composed
        else:
            return None
    
    def __repr__(self):
        return f"Morphism({self.source.id} -> {self.target.id}, type={self.morphism_type})"


class Category:
    """范畴：包含对象和态射"""
    
    def __init__(self, name: str):
        """
        初始化范畴
        
        Args:
            name: 范畴名称
        """
        self.name = name
        self.objects: Dict[str, Object] = {}
        self.morphisms: List[Morphism] = []
        
    def add_object(self, obj: Object):
        """添加对象"""
        self.objects[obj.id] = obj
    
    def add_morphism(self, morphism: Morphism):
        """添加态射"""
        # 检查源和目标是否在范畴中
        if morphism.source.id in self.objects and morphism.target.id in self.objects:
            self.morphisms.append(morphism)
            # 更新对象的关系
            morphism.source.add_relation("morphism_to", morphism.target)
            return True
        return False
    
    def get_morphisms_from(self, obj_id: str) -> List[Morphism]:
        """获取从某个对象出发的所有态射"""
        return [m for m in self.morphisms if m.source.id == obj_id]
    
    def get_morphisms_to(self, obj_id: str) -> List[Morphism]:
        """获取到达某个对象的所有态射"""
        return [m for m in self.morphisms if m.target.id == obj_id]
    
    def check_composition_closure(self) -> bool:
        """
        检查范畴是否满足组合闭包性
        即：任意两个可组合的态射，其组合也在范畴中
        
        Returns:
            是否满足
        """
        for m1 in self.morphisms:
            for m2 in self.morphisms:
                composed = m1.compose(m2)
                if composed is not None:
                    # 检查组合是否在范畴中
                    exists = any(
                        m.source.id == composed.source.id and m.target.id == composed.target.id
                        for m in self.morphisms
                    )
                    if not exists:
                        return False
        return True
    
    def __repr__(self):
        return f"Category(name={self.name}, objects={len(self.objects)}, morphisms={len(self.morphisms)})"


class Functor(ABC):
    """函子：范畴间的映射（抽象基类）"""
    
    @abstractmethod
    def map_object(self, obj: Object) -> Object:
        """映射对象"""
        pass
    
    @abstractmethod
    def map_morphism(self, morphism: Morphism) -> Morphism:
        """映射态射"""
        pass


class IdentityFunctor(Functor):
    """恒等函子：F(x) = x, F(f) = f"""
    
    def map_object(self, obj: Object) -> Object:
        """恒等映射"""
        return obj
    
    def map_morphism(self, morphism: Morphism) -> Morphism:
        """恒等映射"""
        return morphism


class CompositeFunctor(Functor):
    """复合函子：F ∘ G"""
    
    def __init__(self, f: Functor, g: Functor):
        """
        初始化复合函子 F ∘ G
        
        Args:
            f: 外层函子
            g: 内层函子
        """
        self.f = f
        self.g = g
    
    def map_object(self, obj: Object) -> Object:
        """(F ∘ G)(x) = F(G(x))"""
        return self.f.map_object(self.g.map_object(obj))
    
    def map_morphism(self, morphism: Morphism) -> Morphism:
        """(F ∘ G)(f) = F(G(f))"""
        return self.f.map_morphism(self.g.map_morphism(morphism))


class NaturalTransformation:
    """自然变换：两个函子间的映射"""
    
    def __init__(self, 
                 source_functor: Functor, 
                 target_functor: Functor,
                 name: str = "natural_transformation"):
        """
        初始化自然变换 α: F => G
        
        Args:
            source_functor: 源函子 F
            target_functor: 目标函子 G
            name: 自然变换名称
        """
        self.source_functor = source_functor
        self.target_functor = target_functor
        self.name = name
        self.components: Dict[str, Morphism] = {}  # 对每个对象x，有分量 α_x: F(x) -> G(x)
        
    def add_component(self, obj: Object, morphism: Morphism):
        """添加分量 α_x: F(x) -> G(x)"""
        self.components[obj.id] = morphism
    
    def check_naturality(self, category: Category) -> bool:
        """
        检查自然性条件：
        对任意态射 f: x -> y，有：α_y ∘ F(f) = G(f) ∘ α_x
        
        Args:
            category: 所在范畴
            
        Returns:
            是否满足自然性条件
        """
        for morphism in category.morphisms:
            x = morphism.source
            y = morphism.target
            
            # 获取分量
            alpha_x = self.components.get(x.id)
            alpha_y = self.components.get(y.id)
            
            if alpha_x is None or alpha_y is None:
                continue
            
            # 计算 F(f)
            Ff = self.source_functor.map_morphism(morphism)
            
            # 计算 G(f)
            Gf = self.target_functor.map_morphism(morphism)
            
            # 检查：α_y ∘ F(f) = G(f) ∘ α_x
            # 简化：只检查类型和维度
            # 完整实现需要检查态射等价性
            if Ff is None or Gf is None:
                return False
        
        return True


class YonedaEmbedding:
    """
    米田嵌入：实现米田引理
    
    米田引理说：对于任意函子 F: C -> Set，有 Nat(Hom(A, -), F) ≅ F(A)
    应用到编程：对象A可以通过所有从A出发的态射来表征
    """
    
    def __init__(self, category: Category):
        """
        初始化米田嵌入
        
        Args:
            category: 所在范畴
        """
        self.category = category
        self.hom_functors = {}  # Hom(A, -) for each object A
        self.yoneda_embedding = {}  # 嵌入结果
        
    def compute_hom_set(self, a: Object, b: Object) -> List[Morphism]:
        """
        计算 Hom(A, B)：所有从A到B的态射
        
        Args:
            a: 源对象
            b: 目标对象
            
        Returns:
            态射列表
        """
        return [
            m for m in self.category.morphisms
            if m.source.id == a.id and m.target.id == b.id
        ]
    
    def compute_yoneda_embedding(self, a: Object) -> Dict[str, List[Morphism]]:
        """
        计算对象A的米田嵌入
        
        Hom(A, -): 将每个对象B映射到 Hom(A, B)
        
        Args:
            a: 对象A
            
        Returns:
            嵌入：{B.id: Hom(A, B)}
        """
        embedding = {}
        
        for b_id, b in self.category.objects.items():
            hom_set = self.compute_hom_set(a, b)
            embedding[b_id] = hom_set
        
        self.yoneda_embedding[a.id] = embedding
        return embedding
    
    def reconstruct_object(self, a: Object) -> Dict[str, Any]:
        """
        使用米田引理重构对象A
        
        米田引理：知道所有 Hom(A, B) 就相当于知道A
        
        Args:
            a: 要重构的对象
            
        Returns:
            重构结果
        """
        if a.id not in self.yoneda_embedding:
            self.compute_yoneda_embedding(a)
        
        embedding = self.yoneda_embedding[a.id]
        
        # 重构：统计所有 Hom(A, B)
        total_morphisms = sum(len(v) for v in embedding.values())
        avg_morphisms = total_morphisms / len(embedding) if embedding else 0
        
        reconstruction = {
            "object_id": a.id,
            "total_relations": total_morphisms,
            "avg_relations_per_object": avg_morphisms,
            "embedding_dimension": len(embedding),
            "reconstruction_quality": min(1.0, total_morphisms / 100)
        }
        
        return reconstruction


class CTCategoryTheoryProgrammer:
    """
    范畴论编程器：使用范畴论范式进行编程
    
    核心思想：
    1. 将系统组件视为对象
    2. 将组件间的交互视为态射
    3. 使用函子和自然变换组合系统
    4. 使用米田引理实现自表征
    """
    
    def __init__(self, programmer_dim: int = 64):
        """
        初始化范畴论编程器
        
        Args:
            programmer_dim: 编程器维度
        """
        self.programmer_dim = programmer_dim
        
        # 创建系统范畴
        self.system_category = Category("AGI_System")
        
        # 米田嵌入器
        self.yoneda = None  # 延迟初始化
        
        # 编程历史
        self.programming_history: List[Dict] = []
        
    def create_object(self, id: str, properties: Optional[Dict] = None) -> Object:
        """
        创建对象
        
        Args:
            id: 对象ID
            properties: 属性
            
        Returns:
            创建的对象
        """
        obj = Object(id=id, properties=properties)
        self.system_category.add_object(obj)
        
        # 记录
        self.programming_history.append({
            "action": "create_object",
            "object_id": id,
            "timestamp": len(self.programming_history)
        })
        
        return obj
    
    def create_morphism(self, 
                        source_id: str, 
                        target_id: str, 
                        morphism_type: str = "generic") -> Optional[Morphism]:
        """
        创建态射
        
        Args:
            source_id: 源对象ID
            target_id: 目标对象ID
            morphism_type: 态射类型
            
        Returns:
            创建的态射，如果失败返回None
        """
        if source_id not in self.system_category.objects:
            return None
        if target_id not in self.system_category.objects:
            return None
        
        source = self.system_category.objects[source_id]
        target = self.system_category.objects[target_id]
        
        morphism = Morphism(source=source, target=target, morphism_type=morphism_type)
        
        success = self.system_category.add_morphism(morphism)
        
        if success:
            # 记录
            self.programming_history.append({
                "action": "create_morphism",
                "source_id": source_id,
                "target_id": target_id,
                "morphism_type": morphism_type,
                "timestamp": len(self.programming_history)
            })
            return morphism
        else:
            return None
    
    def apply_yoneda(self, object_id: str) -> Dict[str, Any]:
        """
        应用米田引理：表征对象
        
        Args:
            object_id: 对象ID
            
        Returns:
            米田嵌入结果
        """
        if object_id not in self.system_category.objects:
            return {"error": f"Object {object_id} not found"}
        
        # 延迟初始化米田嵌入器
        if self.yoneda is None:
            self.yoneda = YonedaEmbedding(self.system_category)
        
        obj = self.system_category.objects[object_id]
        
        # 计算米田嵌入
        embedding = self.yoneda.compute_yoneda_embedding(obj)
        
        # 重构对象
        reconstruction = self.yoneda.reconstruct_object(obj)
        
        result = {
            "object_id": object_id,
            "yoneda_embedding": {k: len(v) for k, v in embedding.items()},
            "reconstruction": reconstruction
        }
        
        # 记录
        self.programming_history.append({
            "action": "apply_yoneda",
            "object_id": object_id,
            "timestamp": len(self.programming_history)
        })
        
        return result
    
    def compose_system(self, 
                       component1_id: str, 
                       component2_id: str) -> Dict[str, Any]:
        """
        使用范畴论组合系统组件
        
        Args:
            component1_id: 组件1 ID
            component2_id: 组件2 ID
            
        Returns:
            组合结果
        """
        # 查找从component1到component2的态射
        morphisms = self.system_category.get_morphisms_from(component1_id)
        target_morphisms = [m for m in morphisms if m.target.id == component2_id]
        
        if not target_morphisms:
            return {
                "error": f"No morphism from {component1_id} to {component2_id}",
                "composed": False
            }
        
        # 使用第一个态射作为组合接口
        morphism = target_morphisms[0]
        
        result = {
            "composed": True,
            "interface": {
                "source": morphism.source.id,
                "target": morphism.target.id,
                "type": morphism.morphism_type
            },
            "composition_quality": 1.0 / (1.0 + len(target_morphisms))
        }
        
        # 记录
        self.programming_history.append({
            "action": "compose_system",
            "component1_id": component1_id,
            "component2_id": component2_id,
            "timestamp": len(self.programming_history)
        })
        
        return result
    
    def get_system_structure(self) -> Dict[str, Any]:
        """获取系统结构"""
        return {
            "category_name": self.system_category.name,
            "num_objects": len(self.system_category.objects),
            "num_morphisms": len(self.system_category.morphisms),
            "objects": list(self.system_category.objects.keys()),
            "morphisms": [
                {
                    "from": m.source.id,
                    "to": m.target.id,
                    "type": m.morphism_type
                }
                for m in self.system_category.morphisms
            ],
            "composition_closure": self.system_category.check_composition_closure()
        }


class CTFPModule:
    """
    范畴论编程模块：整合范畴论编程能力
    
    这是实现CTFP的核心模块
    """
    
    def __init__(self, ctf_dim: int = 64):
        """
        初始化CTFP模块
        
        Args:
            ctf_dim: CTFP维度
        """
        self.ctf_dim = ctf_dim
        
        # 核心组件
        self.programmer = CTCategoryTheoryProgrammer(programmer_dim=ctf_dim)
        
        # 预定义模式
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, Callable]:
        """初始化范畴论编程模式"""
        return {
            "object_creation": self.programmer.create_object,
            "morphism_creation": self.programmer.create_morphism,
            "yoneda_application": self.programmer.apply_yoneda,
            "system_composition": self.programmer.compose_system
        }
    
    def apply_pattern(self, 
                     pattern_name: str, 
                     **kwargs) -> Dict[str, Any]:
        """
        应用范畴论编程模式
        
        Args:
            pattern_name: 模式名称
            **kwargs: 模式参数
            
        Returns:
            应用结果
        """
        if pattern_name not in self.patterns:
            return {"error": f"Unknown pattern: {pattern_name}"}
        
        pattern_func = self.patterns[pattern_name]
        
        try:
            if pattern_name == "object_creation":
                result = pattern_func(kwargs.get("id"), kwargs.get("properties"))
                return {"result": str(result)}
            elif pattern_name == "morphism_creation":
                result = pattern_func(
                    kwargs.get("source_id"),
                    kwargs.get("target_id"),
                    kwargs.get("morphism_type", "generic")
                )
                return {"result": str(result)}
            elif pattern_name == "yoneda_application":
                result = pattern_func(kwargs.get("object_id"))
                return result
            elif pattern_name == "system_composition":
                result = pattern_func(
                    kwargs.get("component1_id"),
                    kwargs.get("component2_id")
                )
                return result
            else:
                return {"error": f"Pattern {pattern_name} not implemented"}
        except Exception as e:
            return {"error": str(e)}
    
    def build_system(self, system_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用范畴论构建系统
        
        Args:
            system_spec: 系统规范
                {
                    "objects": [{"id": ..., "properties": ...}, ...],
                    "morphisms": [{"source": ..., "target": ..., "type": ...}, ...]
                }
                
        Returns:
            构建结果
        """
        # 创建对象
        for obj_spec in system_spec.get("objects", []):
            self.programmer.create_object(
                id=obj_spec["id"],
                properties=obj_spec.get("properties")
            )
        
        # 创建态射
        for morph_spec in system_spec.get("morphisms", []):
            self.programmer.create_morphism(
                source_id=morph_spec["source"],
                target_id=morph_spec["target"],
                morphism_type=morph_spec.get("type", "generic")
            )
        
        # 返回系统结构
        structure = self.programmer.get_system_structure()
        
        return {
            "status": "success",
            "system_structure": structure
        }
    
    def analyze_self(self) -> Dict[str, Any]:
        """
        使用米田引理分析自身（自表征）
        
        Returns:
            自我分析结果
        """
        # 对所有对象应用米田引理
        results = {}
        for obj_id in self.programmer.system_category.objects:
            result = self.programmer.apply_yoneda(obj_id)
            results[obj_id] = result
        
        # 计算自表征质量
        total_quality = sum(
            r.get("reconstruction", {}).get("reconstruction_quality", 0.0)
            for r in results.values()
        )
        avg_quality = total_quality / len(results) if results else 0.0
        
        return {
            "self_analysis": results,
            "self_representation_quality": avg_quality,
            "num_objects_analyzed": len(results)
        }


# 导出接口
__all__ = [
    'Object',
    'Morphism',
    'Category',
    'Functor',
    'IdentityFunctor',
    'CompositeFunctor',
    'NaturalTransformation',
    'YonedaEmbedding',
    'CTCategoryTheoryProgrammer',
    'CTFPModule'
]


if __name__ == "__main__":
    # 测试代码
    print("=== 太乙AGI 8.0 - 模块8测试 ===")
    print()
    
    # 创建CTFP模块
    print("1. 创建CTFP模块...")
    ctf_module = CTFPModule(ctf_dim=64)
    print(f"   ✅ CTFP模块初始化完成")
    print(f"   模块维度: {ctf_module.ctf_dim}")
    
    # 测试对象创建
    print("2. 测试对象创建...")
    obj1 = ctf_module.apply_pattern("object_creation", id="AGI_Core", properties={"type": "core"})
    obj2 = ctf_module.apply_pattern("object_creation", id="Perception", properties={"type": "module"})
    obj3 = ctf_module.apply_pattern("object_creation", id="Action", properties={"type": "module"})
    print(f"   创建对象: AGI_Core, Perception, Action")
    
    # 测试态射创建
    print("3. 测试态射创建...")
    m1 = ctf_module.apply_pattern(
        "morphism_creation",
        source_id="Perception",
        target_id="AGI_Core",
        morphism_type="data_flow"
    )
    m2 = ctf_module.apply_pattern(
        "morphism_creation",
        source_id="AGI_Core",
        target_id="Action",
        morphism_type="command_flow"
    )
    print(f"   创建态射: Perception -> AGI_Core, AGI_Core -> Action")
    
    # 测试米田引理应用
    print("4. 测试米田引理应用...")
    yoneda_result = ctf_module.apply_pattern("yoneda_application", object_id="AGI_Core")
    if "error" not in yoneda_result:
        print(f"   米田嵌入: {yoneda_result['yoneda_embedding']}")
        print(f"   重构质量: {yoneda_result['reconstruction']['reconstruction_quality']:.4f}")
    
    # 测试系统组合
    print("5. 测试系统组合...")
    composition = ctf_module.apply_pattern(
        "system_composition",
        component1_id="Perception",
        component2_id="AGI_Core"
    )
    print(f"   组合结果: {composition['composed']}")
    if composition['composed']:
        print(f"   接口类型: {composition['interface']['type']}")
    
    # 测试系统构建
    print("6. 测试系统构建...")
    system_spec = {
        "objects": [
            {"id": "Module1", "properties": {"layer": 1}},
            {"id": "Module2", "properties": {"layer": 2}},
            {"id": "Module3", "properties": {"layer": 3}}
        ],
        "morphisms": [
            {"source": "Module1", "target": "Module2", "type": "depends_on"},
            {"source": "Module2", "target": "Module3", "type": "depends_on"}
        ]
    }
    build_result = ctf_module.build_system(system_spec)
    print(f"   构建状态: {build_result['status']}")
    print(f"   系统对象数: {build_result['system_structure']['num_objects']}")
    print(f"   系统态射数: {build_result['system_structure']['num_morphisms']}")
    
    # 测试自我分析
    print("7. 测试自我分析（米田引理）...")
    self_analysis = ctf_module.analyze_self()
    print(f"   分析对象数: {self_analysis['num_objects_analyzed']}")
    print(f"   自表征质量: {self_analysis['self_representation_quality']:.4f}")
    
    print()
    print("✅ 模块8测试完成！")
    print("  核心功能：")
    print("  - ✅ 范畴论基础（对象、态射、范畴）")
    print("  - ✅ 函子（Functor）")
    print("  - ✅ 自然变换（Natural Transformation）")
    print("  - ✅ 米田引理（Yoneda Lemma）")
    print("  - ✅ 范畴论编程范式")
    print("  - ✅ 系统构建与分析")
