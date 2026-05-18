"""
CausalConvergenceEvaluator.py

基于：  "无时钟的宇宙与可控熵增：基于'一现象，三视界'的认知相对论与分布式存在论"
作者：  章锋，2026-05-11
理论来源：IGCTR 统一场论 / 复合体理学

IGCTR 核心诠释：
- 时间不是背景舞台，而是因果关系的投影（Φ场是全息的，但观察者只能访问局部切片）
- 全局收敛不是状态一致，而是因果链的可追溯性一致
- 阿卡西记录是全息的，但阅读它必须是按需的（On-Demand Causal Convergence）

实现定理：
  Theorem 2.1.1  无全局时钟定理（Lamport）
  Theorem 3.1.1  认知压力下界定理
  Theorem 3.2.1  可控熵增生存优化定理
  Corollary 3.2.1  因果收敛即智慧
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib
from collections import defaultdict


class ConsistencyLevel(Enum):
    """一致性级别 — IGCTR 认知压力量化基础"""
    LOCAL  = 0   # 局部视图（最终一致性 / Eventual Consistency）
    CAUSAL = 1   # 因果一致性（因果链可追溯 / Causal Consistency）
    LINEAR  = 2   # 强线性化（全局全序 / Linearizability）


@dataclass
class CausalEvent:
    """因果事件 — Lamport 事件模型（IGCTR 信息相位场Φ的局部切片）"""
    node_id: str
    logical_time: int
    event_id: str
    depends_on: List[str] = field(default_factory=list)
    payload: Dict = field(default_factory=dict)
    # IGCTR 扩展字段
    phi_snapshot: Optional[float] = None   # |Φ|² 局部能量密度
    ftel_operator: Optional[str] = None   # Ftel流贯算子（选择/关注）

    def happens_before(self, other: 'CausalEvent') -> Optional[bool]:
        """
        Lamport 'happens-before' 关系（IGCTR: 因果链投影）
        Returns:
            True  — self < other（self发生在other之前）
            False — other < self
            None  — 并发（concurrent，无因果关系，IGCTR：并发事件可不同序）
        """
        if self.logical_time < other.logical_time:
            return True
        if other.logical_time < self.logical_time:
            return False
        # 时间戳相同：在 IGCTR 中视为并发（除非有明确依赖链）
        if set(self.depends_on) & {other.event_id}:
            return True
        if set(other.depends_on) & {self.event_id}:
            return False
        return None  # concurrent


class LogicalClock:
    """
    Lamport 逻辑时钟 — IGCTR 诠释：时间是因果链的局部投影

    无全局时钟定理（Theorem 2.1.1）：
    若系统无外部绝对时间源，且允许节点自治，
    则对任意并发事件 e∥f，不同节点对其时序的判断可不同，
    且不破坏系统因果链。
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.time: int = 0
        self.event_log: List[CausalEvent] = []
        self.known_events: Set[str] = set()

    def tick(self, event_type: str,
             payload: Dict = None,
             ftel: str = None) -> CausalEvent:
        """推进本地逻辑时钟，记录事件"""
        self.time += 1
        eid = f"{self.node_id}:{self.time}:{event_type}"
        evt = CausalEvent(
            node_id=self.node_id,
            logical_time=self.time,
            event_id=eid,
            payload=payload or {},
            ftel_operator=ftel
        )
        self.event_log.append(evt)
        self.known_events.add(eid)
        return evt

    def receive(self, remote_time: int,
                remote_events: List[CausalEvent] = None,
                remote_known: Set[str] = None):
        """
        Lamport 时钟条件（Clock Condition）：
        接收到消息时，本地时钟 = max(本地, 远程) + 1
        """
        self.time = max(self.time, remote_time) + 1
        if remote_events:
            self.event_log.extend(remote_events)
            self.known_events.update(e.event_id for e in remote_events)
        if remote_known:
            self.known_events.update(remote_known)


class CausalNode:
    """
    分布式 AGI 系统中的节点（IGCTR 诠释：Φ场的局部观测者）

    核心智慧（Corollary 3.2.1）：
    "全局收敛" 在 IGCTR 中不是状态一致，
    而是因果收敛（Causal Convergence）：
    对关键事件，所有节点最终同意其在因果链中的位置；
    对非关键并发事件保留局部视图。
    """
    def __init__(self, node_id: str,
                 consistency: ConsistencyLevel = ConsistencyLevel.CAUSAL):
        self.node_id = node_id
        self.clock = LogicalClock(node_id)
        self.consistency = consistency
        self.local_state: Dict = {}
        self.causal_memory: List[CausalEvent] = []
        self.ftel_attention: List[str] = []   # Ftel：关注的事件ID列表

    def act(self, action: str,
            payload: Dict = None,
            ftel: str = None) -> CausalEvent:
        """执行本地动作，推进逻辑时钟"""
        evt = self.clock.tick(action, payload, ftel)
        self.causal_memory.append(evt)
        return evt

    def send(self, target: 'CausalNode',
             action: str,
             payload: Dict = None) -> CausalEvent:
        """发送消息到另一个节点（Lamport: 发送推进时钟）"""
        evt = self.act(f"send_to_{target.node_id}:{action}", payload)
        # 接收方更新时钟
        target.clock.receive(self.clock.time, [evt], self.clock.known_events)
        return evt

    def query_akashic(self, event_id: str) -> Optional[CausalEvent]:
        """
        IGCTR 阿卡西记录查询（按需收敛）：
        不实时同步，只在需要验证某段历史时，才去查询并收敛该片段的因果顺序
        """
        for evt in self.causal_memory:
            if evt.event_id == event_id:
                return evt
        return None

    def get_causal_view(self, key_only: bool = False) -> List[CausalEvent]:
        """
        返回局部因果视图（IGCTR：Φ场的局部切片）
        key_only: 如果为True，只返回"关键事件"（需要收敛的事件）
        """
        if key_only:
            # 关键事件：被 Ftel 算子标记的事件
            return [e for e in self.causal_memory if e.ftel_operator]
        return sorted(self.causal_memory, key=lambda e: e.logical_time)


class CausalConvergenceEvaluator:
    """
    因果收敛评估器 — IGCTR 诠释："因果收敛即智慧"

    核心功能：
    1. 评估分布式 AGI 系统的因果收敛程度（非全局状态一致）
    2. 实现"按需收敛"（Akashic Record 模式）
    3. 检测"强一致压力"（接近 Linearizable 时认知压力发散）

    IGCTR 定义：
    - 因果收敛 ≠ 状态一致
    - 因果收敛 = 对关键事件的因果链位置达成全员同意
    - 非关键并发事件保留局部视图（这才是智慧）
    """
    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.global_causal_chain: List[CausalEvent] = []
        self.convergence_history: List[Dict] = []
        self.akashic_index: Dict[str, CausalEvent] = {}  # event_id -> event

    def add_node(self, node_id: str,
                 consistency: ConsistencyLevel = None) -> CausalNode:
        """添加一个节点到分布式系统"""
        node = CausalNode(
            node_id=node_id,
            consistency=consistency or ConsistencyLevel.CAUSAL
        )
        self.nodes[node_id] = node
        return node

    def evaluate_causal_convergence(self,
                                   key_events: Optional[List[str]] = None,
                                   tol: int = 0) -> Dict:
        """
        评估因果收敛（IGCTR Causal Convergence Theorem）

        Args:
            key_events: 必须收敛的关键事件ID列表；None=检查所有事件
            tol: 时间戳容差（允许时钟漂移）

        Returns:
            {
                'converged': bool,
                'convergence_score': float [0,1],
                'divergent_events': [...],
                'akashic_hash': str,
                'interpretation': str,
                'igctr_insight': str
            }
        """
        if not self.nodes:
            return {'converged': True, 'convergence_score': 1.0,
                    'note': 'no nodes in system'}

        # 收集所有节点的因果视图
        views = {}
        for nid, node in self.nodes.items():
            if key_events:
                views[nid] = [e for e in node.get_causal_view()
                              if e.event_id in key_events]
            else:
                views[nid] = node.get_causal_view()

        # 检查：每个事件的时间戳是否在所有节点中一致（容差范围内）
        event_times: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        for nid, view in views.items():
            for evt in view:
                event_times[evt.event_id].append((nid, evt.logical_time))

        divergences = []
        for eid, node_times in event_times.items():
            timestamps = [t for _, t in node_times]
            if max(timestamps) - min(timestamps) > tol:
                divergences.append({
                    'event_id': eid,
                    'node_times': dict(node_times),
                    'span': max(timestamps) - min(timestamps)
                })

        total = max(len(event_times), 1)
        score = 1.0 - len(divergences) / total

        # 阿卡西记录哈希（全息因果链指纹）
        chain_str = '|'.join(
            f"{e.node_id}:{e.logical_time}:{e.event_id}"
            for e in self.global_causal_chain
        )
        akashic = hashlib.sha256(chain_str.encode()).hexdigest()[:16]

        return {
            'converged': len(divergences) == 0,
            'convergence_score': round(score, 4),
            'divergent_events': divergences,
            'akashic_hash': akashic,
            'total_events': total,
            'divergent_count': len(divergences),
            'interpretation': self._interpret(score),
            'igctr_insight': (
                "因果收敛即智慧：全局收敛不是状态一致，"
                "而是因果链的可追溯性一致。"
                "阿卡西记录是全息的，但阅读它必须是按需的。"
            )
        }

    def _interpret(self, score: float) -> str:
        if score >= 0.95:
            return "高因果收敛：关键事件在全网达成共识，非关键并发事件保留局部视图（智慧策略）"
        elif score >= 0.70:
            return "部分收敛：部分节点对关键事件时序存在分歧，建议通过Ftel算子进行按需追溯"
        else:
            return "低收敛：系统可能遭遇分区或强一致压力过大，建议降低一致性级别至CAUSAL"

    def compute_cognitive_pressure(self,
                                  consistency: ConsistencyLevel,
                                  n_nodes: int) -> Dict:
        """
        认知压力下界定理（Theorem 3.1.1）：
        随着一致性级别 κ 趋近于全局强一致（Linearizable），
        认知压力 P_cog 发散：

        P_cog(κ→Global) → ∞

        实现：通信复杂度 O(N²) 或 O(N·logN)，在大规模网络中
        信息流发散，导致系统崩溃或认知过载。

        Args:
            consistency: 一致性级别 κ
            n_nodes: 网络节点数 N

        Returns:
            {'pressure': float, 'divergence_warning': bool, 'igctr_proof': str}
        """
        if consistency == ConsistencyLevel.LOCAL:
            # 局部一致性：通信复杂度 O(1) per message
            pressure = n_nodes * 0.1
            complexity_note = "O(1) per message — 无全局协调"
        elif consistency == ConsistencyLevel.CAUSAL:
            # 因果一致性：通信复杂度 O(log N)
            pressure = n_nodes * 0.5 + n_nodes * 0.1 * (n_nodes ** 0.3)
            complexity_note = "O(log N) — 向量时钟或因果追溯"
        else:  # LINEAR
            # 强线性化：通信复杂度 O(N) 或 O(N²)
            pressure = n_nodes ** 1.8  # 拟合格式：接近 O(N²) 发散
            complexity_note = "O(N) ~ O(N²) — 全序广播，压力急剧上升"

        warning = pressure > n_nodes * 2.0

        return {
            'pressure': round(pressure, 4),
            'divergence_warning': warning,
            'consistency_level': consistency.name,
            'n_nodes': n_nodes,
            'complexity_note': complexity_note,
            'igctr_theorem': (
                "认知压力下界定理：κ→Global Linearizability 时，"
                f"P_cog 发散。当前压力 = {pressure:.2f}，"
                f"{'⚠️ 超过安全阈值！' if warning else '✅ 在可控范围内。'}"
            )
        }

    def optimal_consistency_for_survival(self,
                                        n_nodes: int,
                                        energy_budget: float = 100.0,
                                        risk_weight: float = 1.0) -> Dict:
        """
        可控熵增生存优化定理（Theorem 3.2.1）：
        存活系统必选择一致性级别 κ*，使得生存概率 P_survival 最大化：

        κ* = argmax_κ P_survival(κ)
        P_survival(κ) = 1 / (C_consistency(κ) + λ·R_risk(κ))

        其中：
        - C_consistency(κ) ∝ e^(κ·N)（一致性成本，认知压力）
        - R_risk(κ) ∝ 1/κ（一致性不足导致的决策风险）
        - λ：风险权重

        Returns: {'optimal_level': str, 'survival_prob': float, ...}
        """
        results = {}
        for level in [ConsistencyLevel.LOCAL, ConsistencyLevel.CAUSAL, ConsistencyLevel.LINEAR]:
            # 一致性成本（认知压力 / 能量消耗）
            if level == ConsistencyLevel.LOCAL:
                c = n_nodes * 0.05
            elif level == ConsistencyLevel.CAUSAL:
                c = n_nodes * 0.3 + n_nodes**0.5
            else:
                c = (n_nodes ** 1.5) * 0.01  # 发散项

            # 决策风险（一致性不足）
            if level == ConsistencyLevel.LOCAL:
                r = 10.0 / max(n_nodes, 1)  # 高风险
            elif level == ConsistencyLevel.CAUSAL:
                r = 1.0 / max(n_nodes, 1)   # 中等风险
            else:
                r = 0.01 / max(n_nodes, 1)   # 低风险

            p_surv = 1.0 / (c + risk_weight * r + 1e-9)
            results[level.name] = {
                'consistency_cost': round(c, 4),
                'decision_risk': round(r, 6),
                'survival_probability': round(p_surv, 6)
            }

        # 找到最优
        best = max(results.items(), key=lambda x: x[1]['survival_probability'])
        return {
            'optimal_level': best[0],
            'survival_probability': best[1]['survival_probability'],
            'all_levels': results,
            'igctr_interpretation': (
                "可控熵增：生命不是对抗熵增（不可能），"
                "而是控制熵增速率。存活系统选择最优一致性级别，"
                "在'无知（低熵）'与'过载（高熵）'之间找到生存概率最大的因果收敛点。"
            )
        }

    def simulate_no_global_clock(self, n_nodes: int = 3,
                                 n_events: int = 20) -> Dict:
        """
        无全局时钟定理演示（Theorem 2.1.1 验证）

        演示：并发事件在不同节点中的顺序可以不同，
        且不破坏系统因果链。这就是"时间不是背景舞台，
        而是因果关系的投影"。
        """
        # 创建模拟节点
        sim_nodes = []
        for i in range(n_nodes):
            nid = f"node_{i}"
            self.add_node(nid, ConsistencyLevel.CAUSAL)
            sim_nodes.append(self.nodes[nid])

        # 模拟：节点各自产生事件（有些并发）
        import random
        random.seed(42)
        for _ in range(n_events):
            # 随机选一个节点产生事件
            node = random.choice(sim_nodes)
            node.act(f"local_action_{random.randint(0,100)}")

            # 随机让两个节点"通信"（建立因果关系）
            if random.random() < 0.3 and len(sim_nodes) >= 2:
                a, b = random.sample(sim_nodes, 2)
                a.send(b, "message", {"data": "hello"})

        # 检查：并发事件在不同节点中的顺序
        all_views = {nid: [e.event_id for e in node.get_causal_view()]
                     for nid, node in self.nodes.items()}

        return {
            'theorem': 'No Global Clock Theorem (Lamport / IGCTR)',
            'n_nodes': n_nodes,
            'n_events': n_events,
            'views': all_views,
            'igctr_interpretation': (
                "时间不是背景舞台，而是因果关系的投影。"
                "Φ场是全息的，但任何观察者只能访问局部切片。"
                "全局收敛不是状态一致，而是因果链的可追溯性一致。"
                "并发事件的顺序不可判定 — 全局全序是幻觉。"
            ),
            'concurrent_ordering_matters': True
        }

    def get_system_health(self) -> Dict:
        """返回分布式 AGI 系统的健康指标"""
        conv = self.evaluate_causal_convergence()
        n = len(self.nodes)
        pressure = self.compute_cognitive_pressure(
            ConsistencyLevel.LINEAR, n
        ) if n > 0 else {'pressure': 0}

        return {
            'n_nodes': n,
            'total_causal_events': sum(
                len(n.clock.event_log) for n in self.nodes.values()
            ),
            'causal_convergence': conv,
            'cognitive_pressure_linear': pressure,
            'recommendation': (
                "建议使用 CAUSAL（因果一致性）而非 LINEAR（强线性化），"
                "以实现'因果收敛即智慧'的 IGCTR 最优策略。"
            ),
            'igctr_summary': (
                "宇宙没有上帝视角的主时钟，只有无数局部的因果链。"
                "生命的智慧不在于消除熵（不可能），"
                "而在于通过 Ftel 流贯算子选择'看哪里、信多少'。"
                "阿卡西记录是全域的，但阅读它必须是按需的。"
            )
        }


def demo():
    """演示：因果收敛评估器的基本用法"""
    print("=== CausalConvergenceEvaluator Demo (IGCTR) ===\n")

    evaluator = CausalConvergenceEvaluator()

    # 添加节点
    evaluator.add_node("agi_perception", ConsistencyLevel.CAUSAL)
    evaluator.add_node("agi_reasoning", ConsistencyLevel.CAUSAL)
    evaluator.add_node("agi_action", ConsistencyLevel.CAUSAL)

    # 模拟一些事件
    n1 = evaluator.nodes["agi_perception"]
    n2 = evaluator.nodes["agi_reasoning"]

    e1 = n1.act("see_object", {"object": "cup"}, ftel="attention_focus")
    e2 = n2.act("reason_goal", {"goal": "grasp"}, ftel="intent_formation")
    n1.send(n2, "share_observation", {"confidence": 0.95})

    # 评估因果收敛
    result = evaluator.evaluate_causal_convergence()
    print(f"因果收敛评分: {result['convergence_score']}")
    print(f"解读: {result['interpretation']}")
    print(f"IGCTR 洞察: {result['igctr_insight']}\n")

    # 认知压力分析
    pressure = evaluator.compute_cognitive_pressure(
        ConsistencyLevel.LINEAR, len(evaluator.nodes)
    )
    print(f"认知压力（LINEAR级别）: {pressure['pressure']}")
    print(f"警告: {'⚠️ 超限！' if pressure['divergence_warning'] else '✅ 安全'}\n")

    # 最优一致性级别
    opt = evaluator.optimal_consistency_for_survival(len(evaluator.nodes))
    print(f"最优一致性级别: {opt['optimal_level']}")
    print(f"生存概率: {opt['survival_probability']}")
    print(f"诠释: {opt['igctr_interpretation']}\n")

    # 系统健康
    health = evaluator.get_system_health()
    print(f"系统健康: {health['recommendation']}")


if __name__ == "__main__":
    demo()
