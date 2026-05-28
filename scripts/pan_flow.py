#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
泛系流贯算子（Pan-System Flow Operator）实现
基于复合体理学v3.42+Ω范式

核心概念：
1. 关系集合 R - 万物之间的关系
2. 泛系流贯算子 Φ - 驱动关系网络演化的终极算子
3. 刘原理 - 作用量极值约束
4. 非线性演化 - 结构创生与反熵流
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Callable, Any
from dataclasses import dataclass
from enum import Enum
import math

# ==================== 关系集合（Relation Set）====================

@dataclass
class Relation:
    """关系 - 泛权关系"""
    source: str  # 源节点
    target: str  # 目标节点
    weight: float  # 泛权（权重、相干度、拓扑电荷等）
    relation_type: str  # 关系类型（因果、相似、包含等）
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def __repr__(self):
        return f"Relation({self.source} -> {self.target}, w={self.weight:.3f}, type={self.relation_type})"

class RelationSet:
    """关系集合 R - 宇宙中所有异质组分的泛权关系集合"""
    def __init__(self, name: str = "DefaultRelationSet"):
        self.name = name
        self.nodes: Dict[str, Dict] = {}  # 节点：{id: {attributes}}
        self.relations: List[Relation] = []  # 关系列表
        self.time_frame: int = 0  # 时间帧
        
    def add_node(self, node_id: str, attributes: Dict = None):
        """添加节点"""
        if node_id not in self.nodes:
            self.nodes[node_id] = attributes or {}
        else:
            self.nodes[node_id].update(attributes or {})
    
    def add_relation(self, source: str, target: str, 
                   weight: float = 1.0, relation_type: str = "default"):
        """添加关系"""
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)
        
        relation = Relation(source, target, weight, relation_type)
        self.relations.append(relation)
        return relation
    
    def get_neighbors(self, node_id: str) -> List[Relation]:
        """获取节点的邻居关系"""
        return [r for r in self.relations if r.source == node_id or r.target == node_id]
    
    def compute_topology_charge(self, node_id: str) -> float:
        """计算节点的拓扑电荷（关系网络的曲率）"""
        neighbors = self.get_neighbors(node_id)
        if not neighbors:
            return 0.0
        
        # 拓扑电荷 = 关系权重的和
        total_charge = sum(r.weight for r in neighbors)
        return total_charge
    
    def __repr__(self):
        return f"RelationSet({self.name}, nodes={len(self.nodes)}, relations={len(self.relations)})"

# ==================== 泛系流贯算子（Pan-System Flow Operator）====================

class PanSystemFlow:
    """泛系流贯算子 Φ - 驱动关系网络演化的终极算子
    
    演化方程：
    ∂R/∂t = Φ(R, t) = D[R] + N[R] + F[R]
    
    其中：
    - D[R]：线性扩散/退相干项（信息弥散、熵增倾向）
    - N[R]：非线性相互作用项（结的形成、结构创生、反熵流）
    - F[R]：外部驱动（环境输入、观测者介入、刘原理的极值约束力）
    """
    def __init__(self, name: str = "DefaultPanFlow"):
        self.name = name
        self.diffusion_coefficient: float = 0.1  # D：扩散系数
        self.interaction_strength: float = 0.5  # N：相互作用强度
        self.external_force: Callable = None  # F：外部驱动力
        
    def linear_diffusion(self, relation_set: RelationSet, dt: float = 0.01) -> RelationSet:
        """线性扩散项 D[R] - 信息弥散、熵增倾向
        
        模拟关系权重的扩散和平滑
        """
        new_relations = []
        
        for relation in relation_set.relations:
            # 扩散：权重趋向平均
            neighbors = relation_set.get_neighbors(relation.source)
            if neighbors:
                avg_weight = np.mean([r.weight for r in neighbors])
                # 扩散使权重趋向平均
                new_weight = relation.weight + self.diffusion_coefficient * dt * (avg_weight - relation.weight)
            else:
                new_weight = relation.weight
            
            new_rel = Relation(
                relation.source, relation.target,
                new_weight, relation.relation_type, relation.metadata.copy()
            )
            new_relations.append(new_rel)
        
        # 创建新的关系集合
        new_set = RelationSet(f"{relation_set.name}_diffused")
        new_set.nodes = relation_set.nodes.copy()
        new_set.relations = new_relations
        new_set.time_frame = relation_set.time_frame + 1
        
        return new_set
    
    def nonlinear_interaction(self, relation_set: RelationSet, dt: float = 0.01) -> RelationSet:
        """非线性相互作用项 N[R] - 结构创生、反熵流、孤子打结
        
        模拟关系的非线性耦合和结构形成
        """
        new_relations = []
        
        # 计算每个节点的拓扑电荷
        topology_charges = {}
        for node_id in relation_set.nodes:
            charge = relation_set.compute_topology_charge(node_id)
            topology_charges[node_id] = charge
        
        for relation in relation_set.relations:
            # 非线性项：基于拓扑电荷的相互作用
            source_charge = topology_charges.get(relation.source, 0.0)
            target_charge = topology_charges.get(relation.target, 0.0)
            
            # 孤子形成：当拓扑电荷达到一定阈值时，形成稳定的关系结
            charge_product = source_charge * target_charge
            
            if abs(charge_product) > 1.0:  # 阈值
                # 反熵流：权重增强（负熵）
                new_weight = relation.weight + self.interaction_strength * dt * math.exp(-abs(relation.weight))
            else:
                # 熵增：权重衰减
                new_weight = relation.weight - self.interaction_strength * dt * relation.weight
            
            new_rel = Relation(
                relation.source, relation.target,
                new_weight, relation.relation_type, relation.metadata.copy()
            )
            new_relations.append(new_rel)
        
        # 创建新的关系集合
        new_set = RelationSet(f"{relation_set.name}_interacted")
        new_set.nodes = relation_set.nodes.copy()
        new_set.relations = new_relations
        new_set.time_frame = relation_set.time_frame + 1
        
        return new_set
    
    def set_external_force(self, force_fn: Callable):
        """设置外部驱动力函数"""
        self.external_force = force_fn
        
    def external_drive(self, relation_set: RelationSet, 
                     dt: float = 0.01) -> RelationSet:
        """外部驱动 F[R] - 环境输入、观测者介入、刘原理的极值约束力"""
        # 确定使用哪个驱动力函数
        if callable(self.external_force):
            force_fn = self.external_force
        else:
            # 默认：刘原理的极值约束
            force_fn = self._liu_principle_force
        
        new_relations = []
        
        for relation in relation_set.relations:
            # 计算外部驱动力
            force = force_fn(relation_set, relation)
            new_weight = relation.weight + dt * force
            
            new_rel = Relation(
                relation.source, relation.target,
                new_weight, relation.relation_type, relation.metadata.copy()
            )
            new_relations.append(new_rel)
        
        # 创建新的关系集合
        new_set = RelationSet(f"{relation_set.name}_driven")
        new_set.nodes = relation_set.nodes.copy()
        new_set.relations = new_relations
        new_set.time_frame = relation_set.time_frame + 1
        
        return new_set
    
    def _liu_principle_force(self, relation_set: RelationSet, relation: Relation) -> float:
        """刘原理的极值约束力
        
        刘原理：宇宙的本真形态是离散的世界帧序列
        演化趋向作用量最小的方向
        """
        # 简化：作用量 = 权重的平方和
        action = relation.weight ** 2
        
        # 极值约束：趋向作用量减小的方向
        force = -2.0 * relation.weight  # -dL/dw
        return force
    
    def evolve(self, relation_set: RelationSet, dt: float = 0.01, 
              steps: int = 1) -> RelationSet:
        """完整的泛系流贯演化 ∂R/∂t = Φ(R, t) = D[R] + N[R] + F[R]
        
        Args:
            relation_set: 初始关系集合
            dt: 时间步长
            steps: 演化步数
            
        Returns:
            演化后的关系集合
        """
        current = relation_set
        
        for step in range(steps):
            # D[R]：线性扩散
            current = self.linear_diffusion(current, dt)
            
            # N[R]：非线性相互作用
            current = self.nonlinear_interaction(current, dt)
            
            # F[R]：外部驱动（刘原理）
            current = self.external_drive(current, dt)
            
            print(f"  Step {step+1}/{steps}: time_frame={current.time_frame}, "
                  f"relations={len(current.relations)}")
        
        return current

# ==================== 刘原理（Liu's Principle）====================

class LiuPrinciple:
    """刘原理（Liu's Principle）- 作用量极值约束
    
    公理：宇宙的本真形态是离散的世界帧序列
    时间仅是这些帧的索引
    本体源头（刘机制）一次性、无时间性地锁定全域作用量最小的最优跃迁链
    """
    def __init__(self, name: str = "DefaultLiuPrinciple"):
        self.name = name
        self.action_history = []  # 作用量历史
        self.optimal_chain = []  # 最优跃迁链
        
    def compute_action(self, relation_set: RelationSet) -> float:
        """计算作用量 S = ∫L dt
        
        简化：作用量 = 所有关系权重的平方和
        """
        total_action = 0.0
        for relation in relation_set.relations:
            total_action += relation.weight ** 2
        return total_action
    
    def find_optimal_transition(self, current_set: RelationSet, 
                                candidate_sets: List[RelationSet]) -> RelationSet:
        """找到作用量最小的跃迁
        
        刘原理：系统趋向作用量最小的演化方向
        """
        current_action = self.compute_action(current_set)
        
        optimal_set = current_set
        optimal_action = current_action
        
        for candidate in candidate_sets:
            candidate_action = self.compute_action(candidate)
            if candidate_action < optimal_action:
                optimal_action = candidate_action
                optimal_set = candidate
        
        # 记录跃迁
        self.optimal_chain.append({
            'from': current_set.name,
            'to': optimal_set.name,
            'action_change': optimal_action - current_action
        })
        
        return optimal_set
    
    def verify_extremal_principle(self, relation_set: RelationSet, 
                                   tolerance: float = 1e-6) -> bool:
        """验证极值原理：检查当前状态是否接近作用量极值"""
        action = self.compute_action(relation_set)
        
        # 简化：检查作用量是否小于某个阈值
        is_extremal = action < tolerance
        
        print(f"  刘原理验证：action={action:.6f}, is_extremal={is_extremal}")
        return is_extremal

# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("泛系流贯算子（Pan-System Flow）测试")
    print("=" * 60)
    
    # 创建关系集合
    print("\n1. 创建关系集合 R:")
    R = RelationSet("TestRelationSet")
    R.add_node("A", {"type": "concept"})
    R.add_node("B", {"type": "concept"})
    R.add_node("C", {"type": "concept"})
    R.add_relation("A", "B", weight=0.8, relation_type="causal")
    R.add_relation("B", "C", weight=0.5, relation_type="similarity")
    R.add_relation("A", "C", weight=0.3, relation_type="correlation")
    print(f"   {R}")
    print(f"   拓扑电荷 A: {R.compute_topology_charge('A'):.3f}")
    print(f"   拓扑电荷 B: {R.compute_topology_charge('B'):.3f}")
    print(f"   拓扑电荷 C: {R.compute_topology_charge('C'):.3f}")
    
    # 创建泛系流贯算子
    print("\n2. 创建泛系流贯算子 Φ:")
    phi = PanSystemFlow("TestFlow")
    phi.diffusion_coefficient = 0.1
    phi.interaction_strength = 0.3
    print(f"   {phi.name}: D={phi.diffusion_coefficient}, N={phi.interaction_strength}")
    
    # 演化测试
    print("\n3. 泛系流贯演化测试:")
    print("   演化方程：∂R/∂t = D[R] + N[R] + F[R]")
    R_evolved = phi.evolve(R, dt=0.01, steps=10)
    print(f"   演化完成：{R_evolved}")
    
    # 刘原理测试
    print("\n4. 刘原理（Liu's Principle）测试:")
    liu = LiuPrinciple("TestLiu")
    action = liu.compute_action(R_evolved)
    print(f"   作用量 S = {action:.6f}")
    is_extremal = liu.verify_extremal_principle(R_evolved, tolerance=1.0)
    print(f"   极值验证：{is_extremal}")
    
    print("\n" + "=" * 60)
    print("泛系流贯算子测试完成！")
    print("=" * 60)
