# -*- coding: utf-8 -*-
"""
模块35：DIKWP信息层（I层）
实体关系提取 + 协同创造研究空间（7类节点 + 5类边）

来源：复合体AGI 6.0升级方案（基于12文档深度分析）
      协同创造研究空间方案
作者：基于高见远指令实现
日期：2026-05-13
"""

import hashlib
import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Set
from enum import Enum


@dataclass
class InfoNode:
    """
    I层：信息节点（实体+关系+上下文）
    
    集成协同创造研究空间节点类型：
    - _P: Phenomenon（现象/场节点）
    - _Q: Problem（问题/视界节点）
    - _S: Structure（代数/几何结构）
    - _T: Tool（算子/工具节点）
    - _D: Dharma（法则/原理节点）
    - _Th: Theorem（定理/断言节点）
    - _M: Manifestation（显化/实例节点）
    """
    id: str
    entity: str
    node_type: str          # _P/_Q/_S/_T/_D/_Th/_M
    relations: List[Dict] = field(default_factory=list)  # [{target, edge_type, weight}]
    context_boundary: str = ""   # 适用的上下文范围
    parent_data_ids: List[str] = field(default_factory=list)  # 来源D层记录
    embedding: Optional[List[float]] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    active: bool = True
    
    def add_relation(self, target_id: str, edge_type: str, weight: float = 1.0):
        """添加关系边"""
        self.relations.append({
            "target": target_id,
            "edge_type": edge_type,
            "weight": weight
        })
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity": self.entity,
            "node_type": self.node_type,
            "relations": self.relations,
            "context_boundary": self.context_boundary,
            "parent_data_ids": self.parent_data_ids,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "active": self.active
        }


class DIKWPInfoLayer:
    """
    模块35：DIKWP I层 - 语义图谱 + 协同创造研究空间
    
    集成协同创造研究空间方案：7类节点 + 5类边
    弹簧虫对应：弹簧（Φ场耦合器）的相位关系网络
    IGCTR对应：微视界PhaseField语义图
    
    核心功能：
    1. add_node() - 添加信息节点
    2. add_relation() - 添加关系边
    3. find_isomorphisms() - 同构扫描（跨域联想核心）
    4. find_paths() - 路径发现
    5. get_subgraph() - 子图提取
    """
    
    # 协同创造研究空间节点类型
    NODE_TYPES = {
        "_P": "Phenomenon（现象/场节点）",
        "_Q": "Problem（问题/视界节点）",
        "_S": "Structure（代数/几何结构）",
        "_T": "Tool（算子/工具节点）",
        "_D": "Dharma（法则/原理节点）",
        "_Th": "Theorem（定理/断言节点）",
        "_M": "Manifestation（显化/实例节点）"
    }
    
    # 协同创造研究空间边类型
    EDGE_TYPES = {
        "_Isomorphic": "同构（跨域联想）",
        "_FlowsTo": "流贯（演化）",
        "_Proves": "证明（蕴含）",
        "_Embodies": "具身（实现）",
        "_Resonates": "共振（纠缠）"
    }
    
    def __init__(self):
        self.nodes: Dict[str, InfoNode] = {}
        self.isomorphism_cache: List[Dict] = []
        self._counter = 0
        self._edges: List[Dict] = []  # 全局边列表
    
    def add_node(self, 
                 entity: str, 
                 node_type: str = "_P",
                 context: str = "",
                 parent_data_ids: List[str] = None,
                 metadata: Dict = None) -> InfoNode:
        """
        添加信息节点（自动分配全局唯一编号）
        
        Args:
            entity: 实体名称/描述
            node_type: 节点类型（_P/_Q/_S/_T/_D/_Th/_M）
            context: 上下文边界
            parent_data_ids: 来源D层记录ID列表
            metadata: 额外元数据
        
        Returns:
            InfoNode: 创建的节点
        """
        self._counter += 1
        node_id = f"N{self._counter:04d}{node_type}"
        
        node = InfoNode(
            id=node_id,
            entity=entity,
            node_type=node_type,
            context_boundary=context,
            parent_data_ids=parent_data_ids or [],
            metadata=metadata or {}
        )
        
        self.nodes[node_id] = node
        
        # 同构扫描：新节点加入时自动检测可能的同构
        self._auto_scan_isomorphisms(node)
        
        return node
    
    def add_relation(self, 
                     source_id: str, 
                     target_id: str,
                     edge_type: str, 
                     weight: float = 1.0) -> bool:
        """
        添加关系边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            edge_type: 边类型
            weight: 权重
        
        Returns:
            bool: 是否添加成功
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return False
        
        # 添加到源节点的关系列表
        self.nodes[source_id].add_relation(target_id, edge_type, weight)
        
        # 添加到全局边列表
        self._edges.append({
            "source": source_id,
            "target": target_id,
            "edge_type": edge_type,
            "weight": weight,
            "timestamp": time.time()
        })
        
        return True
    
    def find_isomorphisms(self, 
                          node_id: str,
                          min_confidence: float = 0.5) -> List[Dict]:
        """
        同构扫描：找到与指定节点可能同构的其他节点
        复合体理学核心功能：跨域联想
        
        Args:
            node_id: 目标节点ID
            min_confidence: 最低置信度阈值
        
        Returns:
            List[Dict]: 同构候选列表
        """
        if node_id not in self.nodes:
            return []
        
        target = self.nodes[node_id]
        results = []
        
        for nid, node in self.nodes.items():
            if nid == node_id or not node.active:
                continue
            
            # 计算同构得分
            score = self._compute_isomorphism_score(target, node)
            
            if score >= min_confidence:
                results.append({
                    "node_id": nid,
                    "entity": node.entity,
                    "node_type": node.node_type,
                    "edge_type": "_Isomorphic",
                    "confidence": score
                })
        
        return sorted(results, key=lambda x: x["confidence"], reverse=True)
    
    def _compute_isomorphism_score(self, node1: InfoNode, node2: InfoNode) -> float:
        """
        计算两个节点之间的同构得分
        
        同构判断标准（简化版，实际可用embedding余弦相似度）：
        1. 节点类型相同 → 基础分0.5
        2. 关系结构相似 → 加0.2
        3. 上下文重叠 → 加0.15
        4. 元数据相似 → 加0.15
        """
        score = 0.0
        
        # 1. 节点类型相同
        if node1.node_type == node2.node_type:
            score += 0.5
        
        # 2. 关系数量相似（结构同构）
        if abs(len(node1.relations) - len(node2.relations)) <= 2:
            score += 0.2
        
        # 3. 上下文重叠
        if node1.context_boundary and node2.context_boundary:
            if node1.context_boundary == node2.context_boundary:
                score += 0.15
        
        # 4. 元数据相似
        common_keys = set(node1.metadata.keys()) & set(node2.metadata.keys())
        if common_keys:
            score += 0.15
        
        return min(score, 1.0)
    
    def _auto_scan_isomorphisms(self, new_node: InfoNode):
        """新节点加入时自动同构扫描（后台任务）"""
        candidates = self.find_isomorphisms(new_node.id)
        if candidates:
            self.isomorphism_cache.append({
                "new_node": new_node.id,
                "candidates": candidates[:3],
                "pending_confirmation": True,
                "timestamp": time.time()
            })
    
    def find_paths(self, 
                   source_id: str, 
                   target_id: str,
                   max_depth: int = 3) -> List[List[str]]:
        """
        路径发现：从源节点到目标节点的所有路径
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            max_depth: 最大深度
        
        Returns:
            List[List[str]]: 路径列表，每条路径是节点ID序列
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
        
        paths = []
        visited = set()
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            if current == target_id:
                paths.append(path.copy())
                return
            
            visited.add(current)
            for relation in self.nodes[current].relations:
                next_node = relation["target"]
                if next_node not in visited:
                    path.append(next_node)
                    dfs(next_node, path, depth + 1)
                    path.pop()
            visited.remove(current)
        
        dfs(source_id, [source_id], 0)
        return paths
    
    def get_subgraph(self, 
                     node_ids: List[str],
                     include_edges: bool = True) -> Dict:
        """
        子图提取：获取指定节点的子图
        
        Args:
            node_ids: 节点ID列表
            include_edges: 是否包含边
        
        Returns:
            Dict: {"nodes": [...], "edges": [...]}
        """
        subgraph = {"nodes": [], "edges": []}
        
        for nid in node_ids:
            if nid in self.nodes:
                subgraph["nodes"].append(self.nodes[nid].to_dict())
        
        if include_edges:
            for edge in self._edges:
                if edge["source"] in node_ids and edge["target"] in node_ids:
                    subgraph["edges"].append(edge)
        
        return subgraph
    
    def get_neighbors(self, 
                      node_id: str,
                      edge_type: str = None,
                      direction: str = "out") -> List[Dict]:
        """
        获取节点的邻居
        
        Args:
            node_id: 节点ID
            edge_type: 边类型过滤
            direction: "out"(出边), "in"(入边), "both"
        
        Returns:
            List[Dict]: 邻居节点列表
        """
        if node_id not in self.nodes:
            return []
        
        neighbors = []
        node = self.nodes[node_id]
        
        # 出边邻居
        if direction in ("out", "both"):
            for relation in node.relations:
                if edge_type is None or relation["edge_type"] == edge_type:
                    neighbors.append({
                        "node_id": relation["target"],
                        "edge_type": relation["edge_type"],
                        "weight": relation["weight"]
                    })
        
        # 入边邻居
        if direction in ("in", "both"):
            for edge in self._edges:
                if edge["target"] == node_id:
                    if edge_type is None or edge["edge_type"] == edge_type:
                        neighbors.append({
                            "node_id": edge["source"],
                            "edge_type": edge["edge_type"],
                            "weight": edge["weight"]
                        })
        
        return neighbors
    
    def query_by_type(self, node_type: str) -> List[InfoNode]:
        """按类型查询节点"""
        return [n for n in self.nodes.values() if n.node_type == node_type and n.active]
    
    def query_by_entity(self, keyword: str) -> List[InfoNode]:
        """按实体名称模糊查询"""
        return [
            n for n in self.nodes.values() 
            if keyword.lower() in n.entity.lower() and n.active
        ]
    
    def get_statistics(self) -> Dict:
        """获取信息层统计信息"""
        active_nodes = [n for n in self.nodes.values() if n.active]
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": len(active_nodes),
            "by_type": self._group_by_type(active_nodes),
            "total_edges": len(self._edges),
            "by_edge_type": self._group_by_edge_type(),
            "pending_isomorphisms": len(self.isomorphism_cache),
            "avg_relations_per_node": sum(len(n.relations) for n in active_nodes) / max(len(active_nodes), 1)
        }
    
    def _group_by_type(self, nodes: List[InfoNode]) -> Dict[str, int]:
        types = {}
        for n in nodes:
            types[n.node_type] = types.get(n.node_type, 0) + 1
        return types
    
    def _group_by_edge_type(self) -> Dict[str, int]:
        types = {}
        for e in self._edges:
            types[e["edge_type"]] = types.get(e["edge_type"], 0) + 1
        return types
    
    def export_graph(self, filepath: str):
        """导出图为JSON"""
        data = {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": self._edges,
            "isomorphism_cache": self.isomorphism_cache,
            "metadata": {
                "export_time": time.time(),
                "total_nodes": len(self.nodes),
                "total_edges": len(self._edges)
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def __len__(self) -> int:
        return len([n for n in self.nodes.values() if n.active])
    
    def __repr__(self) -> str:
        return f"DIKWPInfoLayer(nodes={len(self)}, edges={len(self._edges)})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块35：DIKWP信息层（I层）测试")
    print("=" * 60)
    
    # 1. 创建信息层实例
    info_layer = DIKWPInfoLayer()
    print(f"\n✓ 创建信息层: {info_layer}")
    
    # 2. 添加节点（协同创造研究空间7类节点）
    nodes = {
        "phenomenon": info_layer.add_node(
            "弹簧虫Φ场耦合现象", "_P", 
            context="多主体协调"
        ),
        "problem": info_layer.add_node(
            "AGI意图对齐问题", "_Q",
            context="AI安全"
        ),
        "structure": info_layer.add_node(
            "DIKWP六层架构", "_S",
            context="认知架构"
        ),
        "tool": info_layer.add_node(
            "Lean 4证明器", "_T",
            context="形式化验证"
        ),
        "dharma": info_layer.add_node(
            "刘原理（最小作用量）", "_D",
            context="物理原理"
        ),
        "theorem": info_layer.add_node(
            "弹簧虫质心守恒定理", "_Th",
            context="协调理论"
        ),
        "manifestation": info_layer.add_node(
            "CompositeAGI系统", "_M",
            context="AGI实现"
        )
    }
    print(f"\n✓ 添加7类节点:")
    for name, node in nodes.items():
        print(f"  - {name}: {node.id} ({node.node_type})")
    
    # 3. 添加边（协同创造研究空间5类边）
    relations = [
        ("phenomenon", "theorem", "_Proves"),
        ("dharma", "theorem", "_Embodies"),
        ("structure", "problem", "_FlowsTo"),
        ("tool", "structure", "_Resonates"),
        ("problem", "manifestation", "_FlowsTo"),
    ]
    
    print(f"\n✓ 添加边关系:")
    for src, tgt, edge_type in relations:
        success = info_layer.add_relation(
            nodes[src].id, 
            nodes[tgt].id, 
            edge_type,
            weight=0.9
        )
        print(f"  - {nodes[src].id} --[{edge_type}]--> {nodes[tgt].id}: {success}")
    
    # 4. 同构扫描
    print(f"\n✓ 同构扫描 (节点: {nodes['structure'].id}):")
    isomorphisms = info_layer.find_isomorphisms(nodes['structure'].id)
    for iso in isomorphisms[:3]:
        print(f"  - {iso['node_id']} ({iso['node_type']}): {iso['confidence']:.2f}")
    
    # 5. 路径发现
    print(f"\n✓ 路径发现 ({nodes['phenomenon'].id} --> {nodes['manifestation'].id}):")
    paths = info_layer.find_paths(nodes['phenomenon'].id, nodes['manifestation'].id)
    for path in paths:
        path_names = [info_layer.nodes[n].entity[:10] for n in path]
        print(f"  - {' -> '.join(path_names)}")
    
    # 6. 邻居查询
    print(f"\n✓ 邻居查询 ({nodes['problem'].id}):")
    neighbors = info_layer.get_neighbors(nodes['problem'].id)
    for n in neighbors:
        print(f"  - {n['node_id']} --[{n['edge_type']}]")
    
    # 7. 统计信息
    stats = info_layer.get_statistics()
    print(f"\n✓ 统计信息:")
    print(f"  - 活跃节点: {stats['active_nodes']}")
    print(f"  - 总边数: {stats['total_edges']}")
    print(f"  - 按类型: {stats['by_type']}")
    print(f"  - 按边类型: {stats['by_edge_type']}")
    
    # 8. 同构缓存
    print(f"\n✓ 同构缓存: {len(info_layer.isomorphism_cache)} 条待确认")
    
    print("\n" + "=" * 60)
    print("模块35测试完成 ✓")
    print("=" * 60)
