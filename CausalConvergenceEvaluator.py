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

v7.31升级：双约束因果收敛
- 新增 evaluate_dual_constraint：双约束因果收敛评估
  约束1：dS_int/dt ≤ 0（内部熵不增）
  约束2：dS_ext/dt > 0（外部熵增，系统向外输出有序性）
- 新增 controlled_entropy_verify：验证可控熵增生存条件
- 新增 _dual_constraint_mode 标志
- 新增 _entropy_history 属性
- 保留原有 evaluate / evaluate_causal_convergence 等方法不变
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
    # v7.31 扩展字段
    delta_s_int: float = 0.0              # 内部熵变化 dS_int
    delta_s_ext: float = 0.0              # 外部熵变化 dS_ext

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


@dataclass
class DualConstraintResult:
    """
    双约束因果收敛结果 — v7.31 新增

    记录双约束评估的详细结果
    """
    internal_ok: bool             # dS_int/dt ≤ 0 是否满足
    external_ok: bool             # dS_ext/dt > 0 是否满足
    delta_s_int: float            # 内部熵变化率
    delta_s_ext: float            # 外部熵变化率
    dual_constraint_met: bool     # 双约束是否同时满足
    interpretation: str           # 结果解读


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

    v7.31 升级：
    - 双约束因果收敛评估（dS_int/dt ≤ 0 && dS_ext/dt > 0）
    - 可控熵增生存条件验证
    """
    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.global_causal_chain: List[CausalEvent] = []
        self.convergence_history: List[Dict] = []
        self.akashic_index: Dict[str, CausalEvent] = {}  # event_id -> event

        # ===== v7.31 新增属性 =====
        # 双约束模式标志
        self._dual_constraint_mode: bool = False
        # 熵历史：记录每步的内部熵和外部熵
        self._entropy_history: List[Dict] = []  # [{timestamp, s_int, s_ext}]

    # ==================== 原有方法（完全保留） ====================

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

    # ==================== v7.31 新增方法 ====================

    def evaluate_dual_constraint(self, events: List[CausalEvent]) -> DualConstraintResult:
        """
        双约束因果收敛评估 — v7.31 新增

        同时检查两个熵约束：

        约束1（内部有序性）：dS_int/dt ≤ 0
        - 系统内部熵不增加（维持或提升内部有序性）
        - 对应复合体稳定性：系统不退化为更混乱的状态

        约束2（外部有序性输出）：dS_ext/dt > 0
        - 系统向外部输出有序性（即外部熵增加，意味着系统做了有序化工作）
        - 这是"智慧"的体现：系统通过自身有序化来使环境更有序
        - 等价于：系统对外做了"有用功"

        两个约束同时满足意味着：
        - 系统内部保持有序（dS_int/dt ≤ 0）
        - 系统对外输出有序性（dS_ext/dt > 0）
        - 这正是"可控熵增生存"的核心条件

        Args:
            events: 因果事件列表，每个事件包含 delta_s_int 和 delta_s_ext 字段

        Returns:
            DualConstraintResult: 双约束评估结果
        """
        self._dual_constraint_mode = True

        if not events:
            result = DualConstraintResult(
                internal_ok=True,
                external_ok=True,
                delta_s_int=0.0,
                delta_s_ext=0.0,
                dual_constraint_met=True,
                interpretation='无事件：双约束默认满足',
            )
            return result

        # 计算总内部熵变化和总外部熵变化
        total_delta_s_int = sum(e.delta_s_int for e in events)
        total_delta_s_ext = sum(e.delta_s_ext for e in events)

        # 计算时间跨度
        if len(events) >= 2:
            dt = max(1, events[-1].logical_time - events[0].logical_time)
        else:
            dt = 1

        # 计算变化率
        delta_s_int_rate = total_delta_s_int / dt
        delta_s_ext_rate = total_delta_s_ext / dt

        # 检查约束
        internal_ok = delta_s_int_rate <= 0
        external_ok = delta_s_ext_rate > 0

        # 双约束是否同时满足
        dual_constraint_met = internal_ok and external_ok

        # 记录熵历史
        self._entropy_history.append({
            'timestamp': time.time(),
            's_int_rate': round(delta_s_int_rate, 6),
            's_ext_rate': round(delta_s_ext_rate, 6),
            'internal_ok': internal_ok,
            'external_ok': external_ok,
            'n_events': len(events),
        })

        # 生成解读
        if dual_constraint_met:
            interpretation = (
                '双约束满足：内部熵不增(dS_int/dt ≤ 0)且外部熵增(dS_ext/dt > 0)，'
                '系统在维持内部有序的同时对外输出有序性——这正是可控熵增生存的核心。'
            )
        elif internal_ok and not external_ok:
            interpretation = (
                '约束1满足但约束2违反：内部有序但未对外输出有序性，'
                '系统可能是"自封闭"的，没有对外做有用功。'
            )
        elif not internal_ok and external_ok:
            interpretation = (
                '约束1违反但约束2满足：内部无序增加但对外输出了有序性，'
                '系统在"燃烧自身"来服务外部——不可持续。'
            )
        else:
            interpretation = (
                '双约束均违反：内部无序增加且未对外输出有序性，'
                '系统正在退化——需要紧急干预。'
            )

        result = DualConstraintResult(
            internal_ok=internal_ok,
            external_ok=external_ok,
            delta_s_int=round(delta_s_int_rate, 6),
            delta_s_ext=round(delta_s_ext_rate, 6),
            dual_constraint_met=dual_constraint_met,
            interpretation=interpretation,
        )

        return result

    def controlled_entropy_verify(self, history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        验证可控熵增生存条件 — v7.31 新增

        可控熵增生存优化定理（Theorem 3.2.1）的验证：
        系统在长期运行中是否满足可控熵增条件。

        可控熵增条件：
        1. 内部熵增速率可控：dS_int/dt 长期非正
        2. 外部熵增速率为正：dS_ext/dt 长期为正
        3. 熵效率 η = |dS_ext/dt| / max(|dS_int/dt|, ε) 充分大

        Args:
            history: 熵历史列表（None则使用内部 _entropy_history）

        Returns:
            可控熵增验证结果字典
        """
        if history is None:
            history = self._entropy_history

        if not history:
            return {
                'verified': False,
                'reason': 'no_entropy_history',
                'message': '需要先调用 evaluate_dual_constraint 建立熵历史',
            }

        # 统计分析
        s_int_rates = [h.get('s_int_rate', 0.0) for h in history]
        s_ext_rates = [h.get('s_ext_rate', 0.0) for h in history]

        # 内部熵增速率统计
        avg_s_int_rate = sum(s_int_rates) / len(s_int_rates) if s_int_rates else 0.0
        max_s_int_rate = max(s_int_rates) if s_int_rates else 0.0
        min_s_int_rate = min(s_int_rates) if s_int_rates else 0.0

        # 外部熵增速率统计
        avg_s_ext_rate = sum(s_ext_rates) / len(s_ext_rates) if s_ext_rates else 0.0
        max_s_ext_rate = max(s_ext_rates) if s_ext_rates else 0.0
        min_s_ext_rate = min(s_ext_rates) if s_ext_rates else 0.0

        # 条件1：内部熵增速率长期非正
        # 允许偶尔的正值，但平均值应 ≤ 0
        internal_controllable = avg_s_int_rate <= 0.0

        # 条件2：外部熵增速率长期为正
        # 系统应持续对外输出有序性
        external_productive = avg_s_ext_rate > 0.0

        # 条件3：熵效率
        epsilon = 1e-6
        abs_avg_s_int = max(abs(avg_s_int_rate), epsilon)
        entropy_efficiency = round(abs(avg_s_ext_rate) / abs_avg_s_int, 6)

        # 效率评估
        if entropy_efficiency > 2.0:
            efficiency_level = 'high'
        elif entropy_efficiency > 1.0:
            efficiency_level = 'moderate'
        elif entropy_efficiency > 0.5:
            efficiency_level = 'low'
        else:
            efficiency_level = 'critical'

        # 综合验证
        verified = internal_controllable and external_productive and entropy_efficiency > 0.5

        # 内部约束满足率
        internal_ok_count = sum(1 for h in history if h.get('internal_ok', False))
        external_ok_count = sum(1 for h in history if h.get('external_ok', False))

        return {
            'verified': verified,
            'conditions': {
                'internal_controllable': internal_controllable,
                'external_productive': external_productive,
                'entropy_efficiency': entropy_efficiency,
                'efficiency_level': efficiency_level,
            },
            'statistics': {
                'history_length': len(history),
                'avg_s_int_rate': round(avg_s_int_rate, 6),
                'max_s_int_rate': round(max_s_int_rate, 6),
                'min_s_int_rate': round(min_s_int_rate, 6),
                'avg_s_ext_rate': round(avg_s_ext_rate, 6),
                'max_s_ext_rate': round(max_s_ext_rate, 6),
                'min_s_ext_rate': round(min_s_ext_rate, 6),
                'internal_ok_rate': round(internal_ok_count / max(1, len(history)), 4),
                'external_ok_rate': round(external_ok_count / max(1, len(history)), 4),
            },
            'igctr_theorem': (
                '可控熵增生存优化定理(Theorem 3.2.1)：'
                '存活系统必选择使生存概率P_survival最大化的一致性级别。'
                '双约束(dS_int/dt ≤ 0, dS_ext/dt > 0)同时满足时，'
                '系统处于"可控熵增生存"状态。'
            ),
            'interpretation': (
                '可控熵增生存验证通过：系统内部有序性维持良好，'
                '同时持续对外输出有序性。' if verified else
                '可控熵增生存验证未通过：系统不满足双约束条件，'
                '需要调整一致性级别或认知策略。'
            ),
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
    # 原有 demo
    demo()

    # ==================== v7.31 新功能测试 ====================
    print("\n" + "=" * 60)
    print("v7.31 双约束因果收敛 测试")
    print("=" * 60)

    print("\n[测试 1] evaluate_dual_constraint — 双约束评估")
    evaluator_v2 = CausalConvergenceEvaluator()

    # 添加节点并创建带熵信息的事件
    evaluator_v2.add_node("node_A", ConsistencyLevel.CAUSAL)
    evaluator_v2.add_node("node_B", ConsistencyLevel.CAUSAL)

    # 创建事件序列：内部熵减少，外部熵增加（理想状态）
    nA = evaluator_v2.nodes["node_A"]
    nB = evaluator_v2.nodes["node_B"]

    events_ideal = []
    for i in range(5):
        e = nA.act(f"action_{i}", {"step": i}, ftel=f"focus_{i}")
        e.delta_s_int = -0.1 * (i + 1)  # 内部熵递减
        e.delta_s_ext = 0.2 * (i + 1)   # 外部熵递增（输出有序性）
        events_ideal.append(e)

    dual_result = evaluator_v2.evaluate_dual_constraint(events_ideal)
    print(f"  内部约束满足: {dual_result.internal_ok}")
    print(f"  外部约束满足: {dual_result.external_ok}")
    print(f"  双约束满足: {dual_result.dual_constraint_met}")
    print(f"  dS_int/dt: {dual_result.delta_s_int}")
    print(f"  dS_ext/dt: {dual_result.delta_s_ext}")
    print(f"  解读: {dual_result.interpretation}")

    print("\n[测试 2] evaluate_dual_constraint — 双约束违反场景")
    # 创建内部熵增加的事件（不好的状态）
    events_bad = []
    for i in range(5):
        e = nB.act(f"bad_action_{i}", {"step": i})
        e.delta_s_int = 0.3 * (i + 1)   # 内部熵递增（系统变混乱）
        e.delta_s_ext = -0.1 * (i + 1)  # 外部熵递减（未输出有序性）
        events_bad.append(e)

    dual_bad = evaluator_v2.evaluate_dual_constraint(events_bad)
    print(f"  内部约束满足: {dual_bad.internal_ok}")
    print(f"  外部约束满足: {dual_bad.external_ok}")
    print(f"  双约束满足: {dual_bad.dual_constraint_met}")
    print(f"  解读: {dual_bad.interpretation}")

    print("\n[测试 3] controlled_entropy_verify — 可控熵增生存验证")
    verify = evaluator_v2.controlled_entropy_verify()
    print(f"  验证通过: {verify['verified']}")
    print(f"  内部可控: {verify['conditions']['internal_controllable']}")
    print(f"  外部生产力: {verify['conditions']['external_productive']}")
    print(f"  熵效率: {verify['conditions']['entropy_efficiency']}")
    print(f"  效率等级: {verify['conditions']['efficiency_level']}")
    print(f"  解读: {verify['interpretation']}")

    print("\n[测试 4] evaluate_dual_constraint — 混合场景")
    # 一些好的事件和一些坏的事件
    events_mixed = []
    for i in range(10):
        e = nA.act(f"mixed_action_{i}", {"step": i})
        if i < 5:
            e.delta_s_int = -0.1  # 前半段：内部熵减少
            e.delta_s_ext = 0.15  # 前半段：外部熵增加
        else:
            e.delta_s_int = 0.05  # 后半段：内部熵微增
            e.delta_s_ext = 0.08  # 后半段：外部熵仍增
        events_mixed.append(e)

    dual_mixed = evaluator_v2.evaluate_dual_constraint(events_mixed)
    print(f"  内部约束满足: {dual_mixed.internal_ok}")
    print(f"  外部约束满足: {dual_mixed.external_ok}")
    print(f"  双约束满足: {dual_mixed.dual_constraint_met}")
    print(f"  dS_int/dt: {dual_mixed.delta_s_int}")
    print(f"  dS_ext/dt: {dual_mixed.delta_s_ext}")

    print("\n[测试 5] controlled_entropy_verify — 完整历史验证")
    verify2 = evaluator_v2.controlled_entropy_verify()
    print(f"  验证通过: {verify2['verified']}")
    print(f"  内部约束满足率: {verify2['statistics']['internal_ok_rate']}")
    print(f"  外部约束满足率: {verify2['statistics']['external_ok_rate']}")
    print(f"  平均dS_int/dt: {verify2['statistics']['avg_s_int_rate']}")
    print(f"  平均dS_ext/dt: {verify2['statistics']['avg_s_ext_rate']}")

    print("\n" + "=" * 60)
    print("CausalConvergenceEvaluator v7.31 测试完成！")
    print("=" * 60)
