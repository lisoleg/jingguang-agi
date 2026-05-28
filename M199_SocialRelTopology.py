# -*- coding: utf-8 -*-
"""
M199: 社会关系拓扑 (Social Relation Topology)
基于《人机共生时代的复合体管理学》— 非自闭症AGI

核心概念：Rel_soc — 社会关系拓扑，关系的网络结构

定理T229（社会关系拓扑不变性定理）：
若Rel_soc在拓扑等价下不变，则社会推理可通过图同构映射完成

关键能力：
- 角色推理：推断社会角色和位置
- 群体动力学：群体行为建模
- 关系类型：合作/竞争/从属/对等
- 图同构检测：社会结构等价性判断

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum


# ==================== 数据结构 ====================

class RelationType(Enum):
    """关系类型枚举"""
    COOPERATION = "cooperation"     # 合作
    COMPETITION = "competition"     # 竞争
    SUBORDINATION = "subordination" # 从属
    EQUALITY = "equality"           # 对等
    UNKNOWN = "unknown"             # 未知


class SocialRole(Enum):
    """社会角色枚举"""
    LEADER = "leader"           # 领导者
    FOLLOWER = "follower"        # 跟随者
    MEDIATOR = "mediator"        # 调停者
    ISOLATE = "isolate"          # 孤立者
    BRIDGE = "bridge"            # 桥接者
    UNKNOWN = "unknown"          # 未知


@dataclass
class SocialRelation:
    """
    社会关系 — 两个agent之间的有向/无向关系

    包含：
    - agent_a: 关系一方
    - agent_b: 关系另一方
    - rel_type: 关系类型
    - strength: 关系强度 [0, 1]
    - directed: 是否有向
    - timestamp: 建立时间
    """
    agent_a: str = ''
    agent_b: str = ''
    rel_type: RelationType = RelationType.UNKNOWN
    strength: float = 0.5
    directed: bool = False
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'agent_a': self.agent_a,
            'agent_b': self.agent_b,
            'rel_type': self.rel_type.value,
            'strength': round(self.strength, 6),
            'directed': self.directed,
            'timestamp': self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'SocialRelation':
        """从字典构建SocialRelation"""
        if 'rel_type' in d and isinstance(d['rel_type'], str):
            d['rel_type'] = RelationType(d['rel_type'])
        return cls(**d)


# ==================== 核心类 ====================

class SocialRelTopology:
    """
    M199: 社会关系拓扑 (Social Relation Topology)

    核心定理T229（社会关系拓扑不变性定理）：
    若Rel_soc在拓扑等价下不变，则社会推理可通过图同构映射完成。

    社会关系拓扑Rel_soc将社会结构建模为图：
    - 节点 = 社会agent
    - 边 = 社会关系（带类型和权重）
    - 拓扑性质 = 连通性、中心性、社区结构

    拓扑不变性：
    两个社会结构如果拓扑等价（图同构），则社会推理结果相同。
    这意味着社会推理可以在保持拓扑结构的变换下进行。

    角色推理：
    基于agent在社会图中的位置推断其社会角色：
    - 高度数→领导者/桥接者
    - 低度数→孤立者
    - 连接不同社区→桥接者/调停者

    群体动力学：
    分析群体的内聚力、分裂倾向、影响力分布。

    核心方法：
    1. add_relation — 添加社会关系
    2. infer_role — 推断社会角色
    3. group_dynamics — 群体动力学分析
    4. find_isomorphism — 图同构检测
    """

    # 关系强度衰减率
    STRENGTH_DECAY: float = 0.98

    # 角色推断阈值
    LEADER_DEGREE_THRESHOLD: int = 3
    BRIDGE_BETWEENNESS_THRESHOLD: float = 0.3

    def __init__(self):
        """初始化社会关系拓扑"""
        # 关系列表
        self.relations: List[SocialRelation] = []

        # 邻接表 {agent_id: [(neighbor_id, relation)]}
        self.adjacency: Dict[str, List[Tuple[str, SocialRelation]]] = {}

        # 角色缓存 {agent_id: SocialRole}
        self.role_cache: Dict[str, SocialRole] = {}

        # 度数缓存 {agent_id: int}
        self.degree_cache: Dict[str, int] = {}

        # 拓扑指纹（用于快速同构检测）
        self.topology_fingerprint: Dict[str, int] = {}

        # 统计
        self.total_relations_added: int = 0
        self.total_role_inferences: int = 0
        self.total_group_analyses: int = 0
        self.total_isomorphism_checks: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def add_relation(self, agent_a: str, agent_b: str,
                     rel_type: str = 'equality', strength: float = 0.5,
                     directed: bool = False) -> Dict[str, Any]:
        """
        添加社会关系

        在社会拓扑中添加一条边，并更新邻接表和度数。

        Args:
            agent_a: 关系一方
            agent_b: 关系另一方
            rel_type: 关系类型（cooperation/competition/subordination/equality）
            strength: 关系强度 [0, 1]
            directed: 是否有向

        Returns:
            添加结果字典
        """
        # 参数标准化
        try:
            rt = RelationType(rel_type)
        except ValueError:
            rt = RelationType.UNKNOWN

        strength = max(0.0, min(1.0, strength))

        # 创建关系
        relation = SocialRelation(
            agent_a=agent_a,
            agent_b=agent_b,
            rel_type=rt,
            strength=round(strength, 6),
            directed=directed,
            timestamp=time.time(),
        )

        # 检查是否已存在同类关系
        existing_idx = None
        for i, r in enumerate(self.relations):
            if ((r.agent_a == agent_a and r.agent_b == agent_b) or
                    (not directed and r.agent_a == agent_b and r.agent_b == agent_a)):
                if r.rel_type == rt:
                    existing_idx = i
                    break

        # 更新或添加
        if existing_idx is not None:
            self.relations[existing_idx] = relation
        else:
            self.relations.append(relation)

        # 更新邻接表
        self._update_adjacency(agent_a, agent_b, relation)
        if not directed:
            self._update_adjacency(agent_b, agent_a, relation)

        # 更新度数
        self.degree_cache[agent_a] = self.degree_cache.get(agent_a, 0) + (0 if existing_idx is not None else 1)
        if not directed:
            self.degree_cache[agent_b] = self.degree_cache.get(agent_b, 0) + (0 if existing_idx is not None else 1)
        elif agent_b not in self.degree_cache:
            self.degree_cache[agent_b] = 0

        # 清除角色缓存（图结构变化）
        self.role_cache.clear()

        # 更新拓扑指纹
        self._update_topology_fingerprint()

        self.total_relations_added += 1
        self.last_update = time.time()

        return {
            'agent_a': agent_a,
            'agent_b': agent_b,
            'rel_type': rt.value,
            'strength': round(strength, 6),
            'directed': directed,
            'total_relations': len(self.relations),
            'total_agents': len(self.degree_cache),
            'theorem': 'T229: Rel_soc拓扑不变性'
        }

    def infer_role(self, agent_id: str) -> Dict[str, Any]:
        """
        推断社会角色

        基于agent在社会图中的拓扑位置推断其角色：
        - 高度数（连接很多agent）→ 领导者
        - 低度数 → 孤立者
        - 连接不同社区 → 桥接者/调停者
        - 居间中心性高 → 调停者
        - 度数1 → 跟随者

        Args:
            agent_id: 目标agent

        Returns:
            角色推断结果字典
        """
        self.total_role_inferences += 1

        # 检查缓存
        if agent_id in self.role_cache:
            cached_role = self.role_cache[agent_id]
        else:
            cached_role = SocialRole.UNKNOWN

        # 计算度数
        degree = self.degree_cache.get(agent_id, 0)

        # 计算居间中心性（简化版）
        betweenness = self._compute_betweenness(agent_id)

        # 推断角色
        if degree >= self.LEADER_DEGREE_THRESHOLD and betweenness > 0.2:
            role = SocialRole.LEADER
            confidence = round(min(1.0, degree / 6.0 + betweenness * 0.3), 6)
            reason = 'high_degree_and_betweenness'
        elif degree >= self.LEADER_DEGREE_THRESHOLD:
            role = SocialRole.BRIDGE
            confidence = round(min(1.0, degree / 5.0), 6)
            reason = 'high_degree_bridge'
        elif betweenness > self.BRIDGE_BETWEENNESS_THRESHOLD:
            role = SocialRole.MEDIATOR
            confidence = round(min(1.0, betweenness), 6)
            reason = 'high_betweenness_mediator'
        elif degree <= 1:
            role = SocialRole.FOLLOWER if degree == 1 else SocialRole.ISOLATE
            confidence = round(max(0.3, 1.0 - degree * 0.3), 6)
            reason = 'low_degree_follower_or_isolate'
        else:
            role = SocialRole.UNKNOWN
            confidence = 0.3
            reason = 'insufficient_topological_evidence'

        # 更新缓存
        self.role_cache[agent_id] = role

        # 获取邻居
        neighbors = [n for n, _ in self.adjacency.get(agent_id, [])]

        self.last_update = time.time()
        return {
            'agent_id': agent_id,
            'inferred_role': role.value,
            'confidence': round(confidence, 6),
            'reason': reason,
            'degree': degree,
            'betweenness': round(betweenness, 6),
            'neighbors': neighbors,
            'total_agents': len(self.degree_cache),
            'theorem': 'T229: 角色推理基于拓扑位置'
        }

    def group_dynamics(self, group_members: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        群体动力学分析

        分析群体的：
        - 内聚力：群体内部的连接密度
        - 分裂倾向：群体内子群的存在
        - 影响力分布：基于度数的权力分布
        - 关系类型分布：合作/竞争/从属/对等的比例

        Args:
            group_members: 群体成员列表（默认为全部agent）

        Returns:
            群体动力学分析结果字典
        """
        self.total_group_analyses += 1

        if group_members is None:
            group_members = list(self.degree_cache.keys())

        if not group_members:
            return {
                'group_size': 0,
                'cohesion': 0.0,
                'split_tendency': 0.0,
                'relation_distribution': {},
                'theorem': 'T229: 群体动力学'
            }

        # 计算群体内的关系
        intra_relations = []
        for r in self.relations:
            if r.agent_a in group_members and r.agent_b in group_members:
                intra_relations.append(r)

        # 内聚力 = 实际边数 / 最大可能边数
        n = len(group_members)
        max_edges = n * (n - 1) / 2
        cohesion = round(len(intra_relations) / max(1, max_edges), 6)

        # 关系类型分布
        rel_dist = {rt.value: 0 for rt in RelationType}
        for r in intra_relations:
            rel_dist[r.rel_type.value] = rel_dist.get(r.rel_type.value, 0) + 1

        # 归一化
        total_rels = max(1, len(intra_relations))
        rel_dist_normalized = {k: round(v / total_rels, 6) for k, v in rel_dist.items()}

        # 分裂倾向：如果竞争关系比例高，则分裂倾向高
        competition_ratio = rel_dist.get(RelationType.COMPETITION.value, 0) / total_rels
        split_tendency = round(min(1.0, competition_ratio * 2.0), 6)

        # 影响力分布（基于度数的基尼系数）
        degrees = [self.degree_cache.get(m, 0) for m in group_members]
        gini = self._compute_gini(degrees)
        influence_concentration = round(gini, 6)

        # 平均关系强度
        avg_strength = (
            sum(r.strength for r in intra_relations) / len(intra_relations)
            if intra_relations else 0.0
        )

        self.last_update = time.time()
        return {
            'group_size': n,
            'intra_relations': len(intra_relations),
            'cohesion': cohesion,
            'split_tendency': split_tendency,
            'influence_concentration': influence_concentration,
            'avg_relation_strength': round(avg_strength, 6),
            'relation_distribution': rel_dist_normalized,
            'cooperation_ratio': rel_dist_normalized.get(RelationType.COOPERATION.value, 0.0),
            'competition_ratio': round(competition_ratio, 6),
            'theorem': 'T229: 群体动力学基于拓扑性质'
        }

    def find_isomorphism(self, topology_a: Optional[Dict] = None,
                         topology_b: Optional[Dict] = None) -> Dict[str, Any]:
        """
        图同构检测

        定理T229验证：若Rel_soc拓扑等价，则社会推理可通过图同构映射完成。

        使用拓扑指纹进行快速检测：
        1. 比较节点数、边数
        2. 比较度数序列
        3. 比较关系类型分布

        Args:
            topology_a: 拓扑A（None=当前拓扑）
            topology_b: 拓扑B（None=当前拓扑）

        Returns:
            图同构检测结果字典
        """
        self.total_isomorphism_checks += 1

        # 获取拓扑指纹
        if topology_a is None:
            fp_a = self._compute_current_fingerprint()
        else:
            fp_a = topology_a

        if topology_b is None:
            fp_b = self._compute_current_fingerprint()
        else:
            fp_b = topology_b

        # 快速检测：节点数和边数
        same_node_count = fp_a.get('node_count', 0) == fp_b.get('node_count', 0)
        same_edge_count = fp_a.get('edge_count', 0) == fp_b.get('edge_count', 0)

        # 度数序列比较
        deg_seq_a = sorted(fp_a.get('degree_sequence', []))
        deg_seq_b = sorted(fp_b.get('degree_sequence', []))
        same_degree_sequence = deg_seq_a == deg_seq_b

        # 关系类型分布比较
        rel_dist_a = fp_a.get('relation_distribution', {})
        rel_dist_b = fp_b.get('relation_distribution', {})
        same_rel_distribution = rel_dist_a == rel_dist_b

        # 同构判定（必要条件，非充分条件）
        is_isomorphic = (same_node_count and same_edge_count and
                         same_degree_sequence and same_rel_distribution)

        # 置信度评估
        evidence_count = sum([same_node_count, same_edge_count,
                              same_degree_sequence, same_rel_distribution])
        confidence = round(evidence_count / 4.0, 6)

        self.last_update = time.time()
        return {
            'is_isomorphic': is_isomorphic,
            'confidence': confidence,
            'same_node_count': same_node_count,
            'same_edge_count': same_edge_count,
            'same_degree_sequence': same_degree_sequence,
            'same_rel_distribution': same_rel_distribution,
            'topology_a_summary': {
                'nodes': fp_a.get('node_count', 0),
                'edges': fp_a.get('edge_count', 0),
            },
            'topology_b_summary': {
                'nodes': fp_b.get('node_count', 0),
                'edges': fp_b.get('edge_count', 0),
            },
            'theorem': 'T229: 拓扑等价 ⟹ 图同构映射 ⟹ 社会推理等价'
        }

    def verify_theorem_t229(self) -> Dict[str, Any]:
        """
        验证定理T229：社会关系拓扑不变性定理

        验证逻辑：构建两个同构的社会拓扑，检查推理结果是否相同

        Returns:
            定理验证结果
        """
        # 保存当前拓扑
        original_relations = list(self.relations)

        # 构建拓扑A
        self.relations = []
        self.adjacency = {}
        self.degree_cache = {}
        self.role_cache = {}

        self.add_relation('a1', 'a2', 'cooperation', 0.8)
        self.add_relation('a1', 'a3', 'cooperation', 0.7)
        self.add_relation('a2', 'a3', 'equality', 0.5)
        self.add_relation('a3', 'a4', 'subordination', 0.6)

        fp_a = self._compute_current_fingerprint()
        role_a1 = self.infer_role('a1')

        # 构建拓扑B（同构：相同结构，不同标签）
        self.relations = []
        self.adjacency = {}
        self.degree_cache = {}
        self.role_cache = {}

        self.add_relation('b1', 'b2', 'cooperation', 0.8)
        self.add_relation('b1', 'b3', 'cooperation', 0.7)
        self.add_relation('b2', 'b3', 'equality', 0.5)
        self.add_relation('b3', 'b4', 'subordination', 0.6)

        fp_b = self._compute_current_fingerprint()
        role_b1 = self.infer_role('b1')

        # 检查同构
        iso_result = self.find_isomorphism(fp_a, fp_b)

        # 检查推理等价性（同构拓扑应产生相同角色推断）
        same_role = role_a1['inferred_role'] == role_b1['inferred_role']

        # 恢复原始拓扑
        self.relations = original_relations
        self.adjacency = {}
        self.degree_cache = {}
        self.role_cache = {}
        for r in self.relations:
            self._update_adjacency(r.agent_a, r.agent_b, r)
            if not r.directed:
                self._update_adjacency(r.agent_b, r.agent_a, r)
            self.degree_cache[r.agent_a] = self.degree_cache.get(r.agent_a, 0) + 1
            if not r.directed:
                self.degree_cache[r.agent_b] = self.degree_cache.get(r.agent_b, 0) + 1

        return {
            'theorem': 'T229: 社会关系拓扑不变性定理',
            'statement': '若Rel_soc拓扑等价，则社会推理可通过图同构映射完成',
            'isomorphic': iso_result['is_isomorphic'],
            'same_role_inference': same_role,
            'verified': iso_result['is_isomorphic'] and same_role,
        }

    # ==================== 内部方法 ====================

    def _update_adjacency(self, agent: str, neighbor: str,
                          relation: SocialRelation):
        """更新邻接表"""
        if agent not in self.adjacency:
            self.adjacency[agent] = []
        # 移除旧关系
        self.adjacency[agent] = [(n, r) for n, r in self.adjacency[agent] if n != neighbor]
        self.adjacency[agent].append((neighbor, relation))

    def _compute_betweenness(self, agent_id: str) -> float:
        """
        计算简化版居间中心性

        基于agent是否出现在其他agent之间的最短路径上
        简化：使用2-hop邻居的重叠度作为近似
        """
        if agent_id not in self.adjacency:
            return 0.0

        neighbors = [n for n, _ in self.adjacency.get(agent_id, [])]
        if len(neighbors) < 2:
            return 0.0

        # 简化：邻居之间的非直接连接数/总可能连接数
        non_connected_pairs = 0
        total_pairs = len(neighbors) * (len(neighbors) - 1) / 2

        neighbor_sets = {n: set(nn for nn, _ in self.adjacency.get(n, [])) for n in neighbors}

        for i, n1 in enumerate(neighbors):
            for n2 in neighbors[i + 1:]:
                if n2 not in neighbor_sets.get(n1, set()):
                    non_connected_pairs += 1

        betweenness = round(non_connected_pairs / max(1, total_pairs), 6)
        return betweenness

    def _compute_gini(self, values: List[float]) -> float:
        """计算基尼系数"""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        cumsum = 0.0
        weighted_sum = 0.0
        for i, v in enumerate(sorted_vals):
            cumsum += v
            weighted_sum += (i + 1) * v
        if cumsum == 0:
            return 0.0
        return round(2.0 * weighted_sum / (n * cumsum) - (n + 1) / n, 6)

    def _compute_current_fingerprint(self) -> Dict[str, Any]:
        """计算当前拓扑的指纹"""
        agents = list(self.degree_cache.keys())
        degree_sequence = sorted([self.degree_cache.get(a, 0) for a in agents], reverse=True)

        rel_dist = {}
        for r in self.relations:
            key = r.rel_type.value
            rel_dist[key] = rel_dist.get(key, 0) + 1

        return {
            'node_count': len(agents),
            'edge_count': len(self.relations),
            'degree_sequence': degree_sequence,
            'relation_distribution': rel_dist,
        }

    def _update_topology_fingerprint(self):
        """更新拓扑指纹缓存"""
        self.topology_fingerprint = self._compute_current_fingerprint()

    # ==================== 模块标准接口 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取社会关系拓扑状态

        Returns:
            状态字典
        """
        dynamics = self.group_dynamics()
        return {
            'total_agents': len(self.degree_cache),
            'total_relations': len(self.relations),
            'cohesion': dynamics['cohesion'],
            'split_tendency': dynamics['split_tendency'],
            'relation_distribution': dynamics['relation_distribution'],
            'total_relations_added': self.total_relations_added,
            'total_role_inferences': self.total_role_inferences,
            'total_group_analyses': self.total_group_analyses,
            'total_isomorphism_checks': self.total_isomorphism_checks,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T229': '拓扑等价 ⟹ 图同构 ⟹ 推理等价'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新社会关系拓扑状态

        Args:
            data: 可选更新数据，支持：
                - add_relation: {agent_a, agent_b, rel_type, strength, directed}
                - infer_role: {agent_id}
                - group_dynamics: {group_members}
                - find_isomorphism: {topology_a, topology_b}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'add_relation' or 'add_relation' in data:
                rd = data.get('add_relation', data)
                self.add_relation(
                    agent_a=rd.get('agent_a', ''),
                    agent_b=rd.get('agent_b', ''),
                    rel_type=rd.get('rel_type', 'equality'),
                    strength=float(rd.get('strength', 0.5)),
                    directed=bool(rd.get('directed', False)),
                )
            elif action == 'infer_role' or 'infer_role' in data:
                idata = data.get('infer_role', data)
                self.infer_role(agent_id=idata.get('agent_id', ''))
            elif action == 'group_dynamics' or 'group_dynamics' in data:
                gdata = data.get('group_dynamics', data)
                self.group_dynamics(group_members=gdata.get('group_members'))
            elif action == 'find_isomorphism' or 'find_isomorphism' in data:
                fdata = data.get('find_isomorphism', data)
                self.find_isomorphism(
                    topology_a=fdata.get('topology_a'),
                    topology_b=fdata.get('topology_b'),
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示社会关系拓扑的核心功能"""
        # 1. 构建社会网络
        self.add_relation('alice', 'bob', 'cooperation', 0.8)
        self.add_relation('alice', 'carol', 'cooperation', 0.7)
        self.add_relation('bob', 'carol', 'equality', 0.5)
        self.add_relation('carol', 'dave', 'subordination', 0.6)
        self.add_relation('dave', 'eve', 'competition', 0.4)
        self.add_relation('alice', 'eve', 'cooperation', 0.3)

        # 2. 角色推断
        role_alice = self.infer_role('alice')
        role_dave = self.infer_role('dave')
        role_eve = self.infer_role('eve')

        # 3. 群体动力学
        dynamics = self.group_dynamics(['alice', 'bob', 'carol'])

        # 4. 图同构检测
        iso = self.find_isomorphism()

        # 5. 定理T229验证
        t229 = self.verify_theorem_t229()

        return {
            'roles': {'alice': role_alice, 'dave': role_dave, 'eve': role_eve},
            'group_dynamics': dynamics,
            'isomorphism': iso,
            'theorem_T229': t229,
            'state': self.get_state(),
        }


# ==================== 模块单例导出 ====================

_instance: Optional[SocialRelTopology] = None


def get_instance() -> SocialRelTopology:
    """获取SocialRelTopology单例实例"""
    global _instance
    if _instance is None:
        _instance = SocialRelTopology()
    return _instance


def add_relation(agent_a: str, agent_b: str, rel_type: str = 'equality',
                 strength: float = 0.5, directed: bool = False) -> Dict[str, Any]:
    """添加社会关系（快捷接口）"""
    return get_instance().add_relation(agent_a, agent_b, rel_type, strength, directed)


def infer_role(agent_id: str) -> Dict[str, Any]:
    """推断社会角色（快捷接口）"""
    return get_instance().infer_role(agent_id)


def group_dynamics(group_members: Optional[List[str]] = None) -> Dict[str, Any]:
    """群体动力学分析（快捷接口）"""
    return get_instance().group_dynamics(group_members)


def find_isomorphism(topology_a: Optional[Dict] = None,
                     topology_b: Optional[Dict] = None) -> Dict[str, Any]:
    """图同构检测（快捷接口）"""
    return get_instance().find_isomorphism(topology_a, topology_b)


def get_state() -> Dict[str, Any]:
    """获取社会关系拓扑状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新社会关系拓扑状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M199: 社会关系拓扑 (SocialRelTopology) 自测')
    print('=' * 60)

    topo = SocialRelTopology()

    # 测试1: 添加关系
    print('\n[测试1] 添加社会关系')
    r1 = topo.add_relation('a', 'b', 'cooperation', 0.8)
    r2 = topo.add_relation('a', 'c', 'competition', 0.5)
    r3 = topo.add_relation('b', 'c', 'equality', 0.6)
    print(f'  关系数: {r1["total_relations"]}')
    print(f'  Agent数: {r1["total_agents"]}')

    # 测试2: 角色推断
    print('\n[测试2] 角色推断')
    ra = topo.infer_role('a')
    rb = topo.infer_role('b')
    rc = topo.infer_role('c')
    print(f'  a角色: {ra["inferred_role"]} (置信度={ra["confidence"]})')
    print(f'  b角色: {rb["inferred_role"]} (置信度={rb["confidence"]})')
    print(f'  c角色: {rc["inferred_role"]} (置信度={rc["confidence"]})')

    # 测试3: 群体动力学
    print('\n[测试3] 群体动力学')
    dyn = topo.group_dynamics(['a', 'b', 'c'])
    print(f'  内聚力: {dyn["cohesion"]}')
    print(f'  分裂倾向: {dyn["split_tendency"]}')
    print(f'  合作比例: {dyn["cooperation_ratio"]}')

    # 测试4: 图同构
    print('\n[测试4] 图同构检测')
    iso = topo.find_isomorphism()
    print(f'  自同构: {iso["is_isomorphic"]}')
    print(f'  置信度: {iso["confidence"]}')

    # 测试5: 定理T229验证
    print('\n[测试5] 定理T229验证')
    t229 = topo.verify_theorem_t229()
    print(f'  验证结果: {t229["verified"]}')

    # 测试6: 完整模拟
    print('\n[测试6] 完整模拟')
    sim = topo.simulate()
    print(f'  总Agent数: {sim["state"]["total_agents"]}')
    print(f'  总关系数: {sim["state"]["total_relations"]}')

    print('\n' + '=' * 60)
    print('M199 自测完成 [OK]')
    print('=' * 60)
