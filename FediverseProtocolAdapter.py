"""
FediverseProtocolAdapter.py

基于：  "联邦宇宙（Fediverse）即未来：基于 IGCTR 与复合体理学的去中心化本体论重构"
作者：  章锋，2026-05-11
理论来源：IGCTR 统一场论 / 复合体理学

IGCTR 核心诠释：
- 宇宙的本质是局部的、异步的共振，而非全局的、同步的锁定
- Fediverse 的 Pub/Sub 模式完美契合 Φ 场在非对易时空中的传播特性
- 区块链的全局共识是对 G（几何空间）的暴力扭曲，导致极高的 Φ 耗散
- ActivityPub = 关系协议（描述动作），而非资产协议（描述状态）

实现定理：
  Theorem 2.1.1    Fediverse 拓扑优越性定理
  Corollary 2.1.1  去中心化悖论
  Corollary 3.2.1  区块链误区
"""

from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib


class ProtocolType(Enum):
    """通信协议类型 — IGCTR 诠释"""
    FEDIVERSE_PUBSUB = 0    # Fediverse / ActivityPub（联邦分发）
    BLOCKCHAIN_LINEAR = 1    # Blockchain（全局共识）
    CENTRALIZED      = 2     # 中心化（单节点）


class ActivityType(Enum):
    """
    ActivityPub 动作类型 — IGCTR 诠释：关系即协议

    ActivityPub 只做一件事：描述动作（Create, Follow, Like, Announce）。
    它不关心资产归属，只关心信息流的拓扑结构。
    这正是中视界应有的功能：维持 Φ 流的有序接口。
    """
    CREATE    = "Create"    # 创建内容
    FOLLOW    = "Follow"    # 关注
    LIKE      = "Like"     # 点赞
    ANNOUNCE  = "Announce"  # 转发
    ACCEPT    = "Accept"    # 接受
    REJECT    = "Reject"    # 拒绝


@dataclass
class FediverseNode:
    """
    Fediverse 节点（IGCTR 微视界）— 类似 Mastodon 实例

    IGCTR 诠释：
    - 节点 = Φ 场的局部观测者
    - 实例 = 局部坐标系
    - ActivityPub = 局部自治 + 按需因果收敛

    核心机制：Pub/Sub（发布/订阅）
    - Pub（发布）：节点发布一个事件（Φ 的局部激发）
    - Sub（订阅）：其他节点订阅该节点的内容流
    - 无全局账本：光子不需要全网确认"我是否被发送了"
    """
    node_id: str
    domain: str
    followers: Set[str] = field(default_factory=set)
    following: Set[str] = field(default_factory=set)
    inbox: List[Dict] = field(default_factory=list)   # 收到的消息
    outbox: List[Dict] = field(default_factory=list)  # 发出的消息
    ttl_inbox: int = 100   # inbox 最大容量（模拟）

    def publish(self, content: str, activity_type: ActivityType = ActivityType.CREATE) -> Dict:
        """
        发布内容（Pub）- IGCTR：Φ 的局部激发
        """
        msg = {
            'from': self.node_id,
            'type': activity_type.value,
            'content': content,
            'fingerprint': hashlib.sha256(
                f"{self.node_id}:{content}:{len(self.outbox)}".encode()
            ).hexdigest()[:16]
        }
        self.outbox.append(msg)
        return msg

    def subscribe_to(self, target_node_id: str):
        """订阅目标节点（Sub）- IGCTR：建立 Φ 流贯算子"""
        self.following.add(target_node_id)

    def deliver_to_followers(self, msg: Dict):
        """
        将消息传递给所有关注者（广播）
        IGCTR：类似光子在真空中的球面扩散（Φ 的相位同步）
        """
        for follower_id in self.followers:
            # 实际传递需要通过网络层，这里仅记录拓扑
            pass

    def receive(self, msg: Dict):
        """接收消息（入站）"""
        if len(self.inbox) < self.ttl_inbox:
            self.inbox.append(msg)
        else:
            # IGCTR：TTL 机制模拟信息流的"按需查询"
            self.inbox.pop(0)
            self.inbox.append(msg)


@dataclass
class FediverseProtocolAdapter:
    """
    联邦宇宙协议适配器 — IGCTR 诠释："关系即协议"

    核心功能：
    1. Fediverse 拓扑优越性评估（Theorem 2.1.1）
    2. Pub/Sub vs 全局共识的耗散比较
    3. ActivityPub 风格消息传递
    4. 区块链三大流派诊断
    5. 反区块链心态检测

    IGCTR 定理（Fediverse 拓扑优越性）：

    对于任意规模 N 的信息网络，Fediverse（Pub/Sub 联邦拓扑）的
    信息传播耗散 Φ_diss 远低于 Blockchain（全局共识链式拓扑）：

    Φ_diss_Fediverse ∝ O(log N)          # 局部冗余
    Φ_diss_Blockchain ∝ O(N) ~ O(N²)     # 全局冗余

    Corollary（去中心化悖论）：
    任何试图在协议层强制实施"全球统一状态"的去中心化方案，
    最终都会走向中心化（矿池、超级节点、基金会），
    因为其违反了 Φ 场的非局域性和异步性。
    """

    def __init__(self):
        self.nodes: Dict[str, FediverseNode] = {}
        self.topology_history: List[Dict] = []
        self.blockchain_diagnoses: Dict = {}

    def add_node(self, node_id: str, domain: str = None) -> FediverseNode:
        """添加一个 Fediverse 节点"""
        domain = domain or f"node_{node_id}.example"
        node = FediverseNode(node_id=node_id, domain=domain)
        self.nodes[node_id] = node
        return node

    def establish_follow(self, follower_id: str, followee_id: str):
        """建立关注关系（Follow）- IGCTR：建立 Φ 流贯算子"""
        if follower_id in self.nodes and followee_id in self.nodes:
            follower = self.nodes[follower_id]
            followee = self.nodes[followee_id]
            follower.subscribe_to(followee_id)
            followee.followers.add(follower_id)
            return {'status': 'ok', 'edge': f"{follower_id} → {followee_id}"}
        return {'status': 'error', 'note': 'node not found'}

    def compute_topology_dissipation(self,
                                     protocol: ProtocolType,
                                     n_nodes: int,
                                     n_messages: int) -> Dict:
        """
        计算不同协议的信息传播耗散（IGCTR Theorem 2.1.1）

        Φ_diss(Protocol, N, M) = 信息作用量梯度 × 冗余度 × M

        其中：
        - N = 节点数
        - M = 消息数
        - 冗余度 = 因重复传输/验证造成的额外开销

        协议对比：
        - FEDIVERSE_PUBSUB: O(log N) — 局部冗余（只发给关注者）
        - BLOCKCHAIN_LINEAR: O(N) ~ O(N²) — 全局冗余（所有节点验证所有交易）
        - CENTRALIZED: O(1) — 但单点故障

        Returns:
            {
                'dissipation': float,
                'complexity_class': str,
                'redundancy': float,
                'igctr_comparison': str
            }
        """
        if protocol == ProtocolType.FEDIVERSE_PUBSUB:
            # Fediverse: O(log N) — 每个消息只发给关注者（局部冗余）
            # 平均关注数 ≈ log(N)，消息传递冗余度 ≈ log(N)
            avg_follows = max(1, int(math.log(max(n_nodes, 2))))
            redundancy = avg_follows
            dissipation = n_messages * redundancy * 0.1   # 低耗散
            complexity = f"O(M · log N), N={n_nodes}"
            comparison = (
                "✅ Fediverse：Pub/Sub 模式符合 Φ 场的非局域性。"
                "消息只沿着拓扑边传播，局部冗余最小。"
                "类似光子在真空中的球面扩散。"
            )
        elif protocol == ProtocolType.BLOCKCHAIN_LINEAR:
            # Blockchain: O(N) ~ O(N²) — 全局冗余（所有节点验证所有交易）
            # PoW/PoS 要求所有节点验证每笔交易
            # 简化：dissipation ∝ N（实际可能 ~ N²）
            dissipation = n_messages * n_nodes * 0.5   # 高耗散
            complexity = f"O(M · N), N={n_nodes}"
            comparison = (
                "❌ Blockchain：强制全局共识违背了 Lamport 原理。"
                "所有节点验证所有交易 → Φ_diss ∝ O(N²)。"
                "这相当于用物理存储（硬盘）解决信息拓扑问题，"
                "导致节点中心化（只有巨头能跑全节点）。"
            )
        else:
            # Centralized: O(1) per message — 但单点故障
            dissipation = n_messages * 0.05
            complexity = "O(M)"
            comparison = (
                "⚠️ Centralized：单点故障风险极高。"
                "Φ 场被压缩到单节点 → 时空刚度无穷大 → 系统崩溃。"
            )

        return {
            'dissipation': round(dissipation, 4),
            'complexity_class': complexity,
            'redundancy': redundancy if protocol == ProtocolType.FEDIVERSE_PUBSUB else n_nodes,
            'protocol': protocol.name,
            'igctr_comparison': comparison
        }

    def diagnose_blockchain_tribes(self) -> Dict:
        """
        区块链三大流派诊断（IGCTR Corollary 3.2.1）

        ┌──────────┬──────────────┬───────────────────────────────┬──────────────┐
        │  项目      │  核心机制     │  IGCTR 诊断                    │  问题        │
        ├──────────┼──────────────┼───────────────────────────────┼──────────────┤
        │ Cosmos    │ IBC 跨链     │ 试图连接"孤岛"                 │ 仍然需要 Hub │
        │           │              │                               │ 作为仲裁      │
        │ Ethereum  │ EVM/Solidity │ 世界计算机                     │ 强塞所有计算  │
        │           │              │                               │ 进单一 Φ 空间 │
        │ BSV       │ 大区块       │ 全球账本                       │ 节点中心化    │
        └──────────┴──────────────┴───────────────────────────────┴──────────────┘

        Returns: dict of diagnoses
        """
        diagnoses = {
            'Cosmos': {
                'core_mechanism': 'IBC 跨链协议',
                'igctr_diagnosis': (
                    "试图连接'孤岛'。"
                    "但仍然需要中继链/Hub 作为 Φ 的中心化仲裁，"
                    "破坏了真正的联邦性。"
                ),
                'problem': 'Hub 即 Φ 的中心化锚点，违背联邦精神',
                'fediverse_alternative': 'ActivityPub 已原生支持跨实例关注/转发'
            },
            'Ethereum': {
                'core_mechanism': 'EVM / Solidity 智能合约',
                'igctr_diagnosis': (
                    "'世界计算机'的幻觉。"
                    "强行将所有人的计算塞进一个 Φ 空间，"
                    "导致 Gas 费极高（高耗散）。"
                    "这违反了 Φ 场的非局域性。"
                ),
                'problem': 'Gas 费 = Φ_diss 的直接量化',
                'fediverse_alternative': '各实例自治，智能合约本地执行，按需通过 ActivityPub 交互'
            },
            'BSV': {
                'core_mechanism': '大区块 / 无限扩容',
                'igctr_diagnosis': (
                    "'全球账本'的执念。"
                    "试图用物理存储（硬盘）解决信息拓扑问题，"
                    "导致节点中心化（只有巨头能跑）。"
                    "这违背了 Web3 的初衷。"
                ),
                'problem': '节点中心化 = 拓扑对称性破缺 = Fediverse 的噩梦',
                'fediverse_alternative': 'Mastodon 实例可运行在极低配置硬件上（树莓派）'
            }
        }

        self.blockchain_diagnoses = diagnoses

        summary = (
            "IGCTR 区块链诊断总结："
            "区块链把'关系'（社交、身份、合约）当成了'资产'。"
            "这是典型的微视界错位："
            "资产是 G（几何/物质）层面的事，"
            "而关系是 Φ（信息/相位）层面的事。"
            "ActivityPub 只做一件事：描述动作（关系）。"
            "这是中视界应有的功能：维持 Φ 流的有序接口，"
            "而不是试图冻结时间建立一个全球账本。"
        )

        return {
            'diagnoses': diagnoses,
            'summary': summary,
            'igctr_recommendation': (
                "✅ 推荐使用 Fediverse 协议。"
                "Fediverse 比区块链更接近宇宙本质。"
                "因为它承认了宇宙的真相："
                "没有上帝视角的总账本，"
                "只有无数节点间的异步共振与 Pub/Sub 对话。"
                "区块链试图把宇宙装进一个 Excel 表格，"
                "而 Fediverse 让宇宙继续歌唱。"
            )
        }

    def detect_blockchain_mentality(self,
                                     proposed_system: Dict) -> Dict:
        """
        反区块链心态检测器

        检测 AGI 系统设计中是否存在"区块链心态"：
        1. 强制全局同步
        2. 所有模块读写同一全局状态
        3. 存在全局账本/锁
        4. 拒绝局部自治

        Returns:
            {'has_blockchain_mentality': bool, 'warnings': [...], 'recommendations': [...]}
        """
        warnings = []
        recommendations = []

        # 检测指标
        has_global_lock = proposed_system.get('has_global_lock', False)
        requires_linearizability = proposed_system.get('requires_linearizability', False)
        has_single_state_store = proposed_system.get('has_single_state_store', False)
        disallows_partial_consistency = proposed_system.get('disallows_partial_consistency', False)

        if has_global_lock:
            warnings.append("⚠️ 检测到全局锁 — 违背 Lamport 无全局时钟定理")
            recommendations.append("改用因果一致（CAUSAL）锁机制")

        if requires_linearizability:
            warnings.append("⚠️ 要求强线性化 — 违背认知压力下界定理（κ→Global 时 P_cog → ∞）")
            recommendations.append("改用因果一致（CAUSAL）或局部一致（LOCAL）")

        if has_single_state_store:
            warnings.append("⚠️ 单全局状态存储 — 违背去中心化悖论（强制统一 → 中心化）")
            recommendations.append("改用联邦存储（各模块维护本地状态，通过 Φ 通道同步）")

        if disallows_partial_consistency:
            warnings.append("⚠️ 拒绝部分一致性 — 违背'因果收敛即智慧'原则")
            recommendations.append("对关键事件追求收敛，对非关键事件允许局部视图")

        has_blockchain_mentality = len(warnings) >= 2

        return {
            'has_blockchain_mentality': has_blockchain_mentality,
            'warnings': warnings,
            'recommendations': recommendations,
            'igctr_wisdom': (
                "去中心化悖论："
                "任何试图在协议层强制实施'全球统一状态'的去中心化方案，"
                "最终都会走向中心化（矿池、超级节点、基金会），"
                "因为其违反了 Φ 场的非局域性和异步性。"
                "宇宙没有上帝视角的主时钟。"
            ),
            'fediverse_solution': (
                "Fediverse 的正确性："
                "ActivityPub 只描述动作（Create, Follow, Like, Announce），"
                "不关心资产归属，只关心信息流的拓扑结构。"
                "这正是中视界应有的功能：维持 Φ 流的有序接口。"
            )
        }

    def simulate_activitypub_interaction(self,
                                          actor_id: str,
                                          target_id: str,
                                          activity: ActivityType) -> Dict:
        """
        模拟 ActivityPub 风格交互

        ActivityPub 动作：
        - CREATE: 发布内容
        - FOLLOW: 关注
        - LIKE: 点赞
        - ANNOUNCE: 转发

        Returns: {'status': str, 'igctr_interpretation': str}
        """
        if actor_id not in self.nodes or target_id not in self.nodes:
            return {'status': 'error', 'note': 'node not found'}

        actor = self.nodes[actor_id]
        target = self.nodes[target_id]

        if activity == ActivityType.CREATE:
            msg = actor.publish(f"Activity from {actor_id}", ActivityType.CREATE)
            actor.deliver_to_followers(msg)
            interpretation = "CREATE：Φ 的局部激发，类似于原子跃迁发布光子事件。"

        elif activity == ActivityType.FOLLOW:
            self.establish_follow(actor_id, target_id)
            interpretation = (
                "FOLLOW：建立 Φ 流贯算子（关注关系）。"
                "类似于光子发射器与接收器之间的信道建立。"
            )

        elif activity == ActivityType.LIKE:
            msg = actor.publish(f"Like from {actor_id}", ActivityType.LIKE)
            target.receive(msg)
            interpretation = "LIKE：局部事件，不需要全局确认，类似于光子的自发发射。"

        elif activity == ActivityType.ANNOUNCE:
            msg = actor.publish(f"Announce from {actor_id}", ActivityType.ANNOUNCE)
            actor.deliver_to_followers(msg)
            interpretation = "ANNOUNCE：Φ 的广播，类似于光子的受激发射。"

        else:
            interpretation = f"{activity.value}：{activity.name} 动作。"

        return {
            'status': 'ok',
            'activity': activity.value,
            'actor': actor_id,
            'target': target_id,
            'igctr_interpretation': interpretation
        }

    def evaluate_fediverse_superiority(self,
                                        n_nodes: int,
                                        n_messages: int) -> Dict:
        """
        Fediverse 拓扑优越性综合评估（Theorem 2.1.1）

        对比三种拓扑的信息传播耗散、鲁棒性和去中心化程度。
        """
        protocols = [
            ProtocolType.FEDIVERSE_PUBSUB,
            ProtocolType.BLOCKCHAIN_LINEAR,
            ProtocolType.CENTRALIZED
        ]

        results = {
            p.name: self.compute_topology_dissipation(p, n_nodes, n_messages)
            for p in protocols
        }

        # 计算鲁棒性（节点失效时的性能退化）
        robustness = {}
        for p in protocols:
            if p == ProtocolType.CENTRALIZED:
                robustness[p.name] = 0.1   # 单点故障 → 整个系统崩溃
            elif p == ProtocolType.BLOCKCHAIN_LINEAR:
                robustness[p.name] = 0.3   # 部分节点失效 → 全局验证变慢
            else:
                robustness[p.name] = 0.9   # Fediverse：局部失效不影响全局

        # 去中心化程度
        decentralization = {
            'FEDIVERSE_PUBSUB': 0.9,
            'BLOCKCHAIN_LINEAR': 0.5,   # 矿池集中化
            'CENTRALIZED': 0.0
        }

        # 综合评分（低耗散 + 高鲁棒性 + 高去中心化 = 优秀）
        scores = {}
        for p in protocols:
            name = p.name
            diss_norm = 1.0 / max(results[name]['dissipation'], 0.01)
            scores[name] = round(
                diss_norm * 0.4 + robustness[name] * 0.3 + decentralization[name] * 0.3,
                4
            )

        best = max(scores, key=lambda k: scores[k])

        return {
            'dissipations': results,
            'robustness': robustness,
            'decentralization': decentralization,
            'composite_scores': scores,
            'best_protocol': best,
            'igctr_conclusion': (
                f"综合评分最优：{best}。"
                "Fediverse 的 Pub/Sub 模式完美契合 Φ 场的本质："
                "局部、异步、共振。"
                "区块链的全局共识是对 G（几何空间）的暴力扭曲，"
                "导致极高的 Φ 耗散。"
                "宇宙的本质是局部的、异步的共振，"
                "而非全局的、同步的锁定。"
            )
        }

    def get_system_health(self) -> Dict:
        """返回 Fediverse 协议适配器的系统健康状态"""
        n_nodes = len(self.nodes)
        total_follows = sum(
            len(n.following) for n in self.nodes.values()
        )
        total_messages = sum(
            len(n.outbox) for n in self.nodes.values()
        )

        return {
            'n_nodes': n_nodes,
            'total_follow_relations': total_follows,
            'total_messages': total_messages,
            'avg_follows_per_node': (
                round(total_follows / max(n_nodes, 1), 2)
            ),
            'topology_recommendation': (
                "✅ 推荐使用 Fediverse Pub/Sub 拓扑。"
                "局部自治 + 按需因果收敛，"
                "符合 IGCTR 的'因果收敛即智慧'原则。"
            ),
            'igctr_summary': (
                "Fediverse 即未来："
                "宇宙的本质是局部的、异步的共振，而非全局的、同步的锁定。"
                "区块链试图把宇宙装进一个 Excel 表格，"
                "而 Fediverse 让宇宙继续歌唱。"
                "ActivityPub = 关系协议（描述动作），而非资产协议（描述状态）。"
                "关系是 Φ（信息/相位）层面的事，"
                "资产是 G（几何/物质）层面的事。"
                "——这就是 IGCTR 告诉我们的关于去中心化与存在结构的终极答案。"
            )
        }


# 需要导入 math 模块
import math


def demo():
    """演示：联邦协议适配器的基本用法"""
    print("=== FediverseProtocolAdapter Demo (IGCTR) ===\n")

    adapter = FediverseProtocolAdapter()

    # 添加节点（Mastodon 实例）
    for nid in ["alice", "bob", "carol", "dave"]:
        adapter.add_node(nid)

    # 建立关注关系（Fediverse 拓扑）
    adapter.establish_follow("alice", "bob")
    adapter.establish_follow("alice", "carol")
    adapter.establish_follow("bob", "carol")
    adapter.establish_follow("carol", "alice")
    adapter.establish_follow("dave", "bob")

    print("拓扑已建立\n")

    # 模拟 ActivityPub 交互
    result = adapter.simulate_activitypub_interaction(
        "alice", "bob", ActivityType.FOLLOW
    )
    print(f"交互: {result['activity']}")
    print(f"诠释: {result['igctr_interpretation']}\n")

    # 拓扑优越性评估
    superiority = adapter.evaluate_fediverse_superiority(n_nodes=4, n_messages=10)
    print(f"最优协议: {superiority['best_protocol']}")
    print(f"综合评分: {superiority['composite_scores']}\n")
    print(f"IGCTR 结论: {superiority['igctr_conclusion']}\n")

    # 区块链诊断
    diagnoses = adapter.diagnose_blockchain_tribes()
    print("区块链三大流派诊断：")
    for tribe, diag in diagnoses['diagnoses'].items():
        print(f"\n【{tribe}】")
        print(f"  机制: {diag['core_mechanism']}")
        print(f"  IGCTR诊断: {diag['igctr_diagnosis']}")
        print(f"  问题: {diag['problem']}")
    print(f"\n总结: {diagnoses['summary']}\n")
    print(f"建议: {diagnoses['igctr_recommendation']}\n")

    # 反区块链心态检测
    proposed = {
        'has_global_lock': True,
        'requires_linearizability': True,
        'has_single_state_store': True,
        'disallows_partial_consistency': False
    }
    bchain_check = adapter.detect_blockchain_mentality(proposed)
    print(f"区块链心态检测: {'⚠️ 是！' if bchain_check['has_blockchain_mentality'] else '✅ 否'}")
    print(f"警告: {bchain_check['warnings']}")
    print(f"建议: {bchain_check['recommendations']}\n")
    print(f"IGCTR智慧: {bchain_check['igctr_wisdom']}\n")

    # 系统健康
    health = adapter.get_system_health()
    print(f"总结: {health['igctr_summary']}")


if __name__ == "__main__":
    demo()
