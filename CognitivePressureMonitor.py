"""
CognitivePressureMonitor.py

基于：  "无时钟的宇宙与可控熵增：基于'一现象，三视界'的认知相对论与分布式存在论"
作者：  章锋，2026-05-11
理论来源：IGCTR 统一场论 / 复合体理学

IGCTR 核心诠释：
- 认知压力 ∝ 信息作用量梯度 ∇S_info
- 强迫所有人看同一个"全貌"，就是强迫所有人进入同一个惯性系，
  这需要无限大的能量（认知压力发散）
- 生命不是对抗熵增（不可能），而是控制熵增的速率

实现定理：
  Theorem 3.1.1  认知压力下界定理（κ→Global 时 P_cog → ∞）
  Theorem 3.2.1  可控熵增生存优化定理（∃κ* 使 P_survial 最大）
  Corollary 3.2.1  因果收敛即智慧
"""

from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
import math


class ConsistencyLevel(Enum):
    """一致性级别 — IGCTR 认知压力量化基础（复用自 CausalConvergenceEvaluator）"""
    LOCAL  = 0   # 局部视图（Eventual Consistency / 最终一致性）
    CAUSAL = 1   # 因果一致性（Causal Consistency / 因果链可追溯）
    LINEAR = 2   # 强线性化（Linearizability / 全局全序）


@dataclass
class CognitiveLoad:
    """认知负荷 — 单个节点/模块的认知压力快照"""
    node_id: str
    consistency_level: int           # 0=LOCAL, 1=CAUSAL, 2=LINEAR
    n_peers: int                    # 通信对等节点数
    info_rate: float = 1.0         # 信息到达率（事件/秒）
    processing_power: float = 1.0   # 处理能力（事件/秒）
    entropy_rate: float = 0.0       # 当前熵增速率
    timestamp: float = field(default_factory=lambda: __import__('time').time())

    def pressure(self) -> float:
        """
        认知压力计算公式（IGCTR Theorem 3.1.1）：

        P_cog(κ, N) ∝ C(κ, N)

        其中 C(κ, N) 为通信复杂度：
        - LOCAL:   O(1)     per message
        - CAUSAL:  O(log N) or O(N·log N)
        - LINEAR:  O(N)     or O(N²)

        认知压力下界：κ → Linearizable 时，P_cog → ∞
        """
        k = self.consistency_level
        n = max(self.n_peers, 1)
        rate = self.info_rate
        power = max(self.processing_power, 0.01)

        if k == 0:       # LOCAL: O(1)
            complexity = 1.0 * n**0.1
        elif k == 1:     # CAUSAL: O(log N)
            complexity = math.log(max(n, 2)) * n**0.3
        else:               # LINEAR: O(N) ~ O(N²) 发散
            # 关键：此处模拟"认知压力发散"
            # 当 N 大时，复杂度急剧上升
            complexity = (n ** 1.8) * 0.005 + n * 0.5

        # 压力 = 复杂度 × (信息到达率 / 处理能力)
        p = complexity * (rate / power)
        return round(p, 6)

    def is_overloaded(self, threshold: float = 1.0) -> bool:
        """是否认知过载（IGCTR：P_cog 超过处理能力）"""
        return self.pressure() > threshold

    def entropy_contribution(self) -> float:
        """
        对系统总熵增的贡献：
        认知过载导致决策质量下降 → 系统熵增
        """
        p = self.pressure()
        if p < 0.5:
            return 0.1   # 低压力：低熵增（有序）
        elif p < 1.0:
            return 0.3   # 中等压力：最优范围
        else:
            return 0.8   # 高压力：高熵增（紊乱）


class CognitivePressureMonitor:
    """
    认知压力监测器 — IGCTR 诠释："可控熵增即智慧"

    功能：
    1. 实时监测各节点的认知压力 P_cog
    2. 预警"认知压力发散"（接近强一致时）
    3. 推荐最优一致性级别 κ*（最大化生存概率）
    4. 实现"可控熵增"策略：在无知与过载之间找到最优平衡点

    IGCTR 核心：
    存活系统必选择 κ ∈ {LOCAL, CAUSAL}（而非 LINEAR），
    使得生存概率 P_survival 最大化。

    P_survival(κ) = 1 / [C_consistency(κ) + λ·R_risk(κ)]

    C_consistency(κ) = 一致性成本（认知压力 / 能量消耗）
    R_risk(κ)        = 一致性不足导致的决策风险
    λ                  = 风险权重
    """

    def __init__(self,
                 entropy_budget: float = 100.0,
                 risk_weight: float = 1.0,
                 overload_threshold: float = 1.0):
        self.nodes: Dict[str, CognitiveLoad] = {}
        self.entropy_budget = entropy_budget
        self.risk_weight = risk_weight
        self.overload_threshold = overload_threshold
        self.pressure_history: List[Dict] = []
        self.intervention_log: List[str] = []

    def register_node(self,
                      node_id: str,
                      consistency: int = 1,
                      n_peers: int = 1,
                      info_rate: float = 1.0,
                      processing_power: float = 1.0) -> CognitiveLoad:
        """注册一个节点到监测系统"""
        load = CognitiveLoad(
            node_id=node_id,
            consistency_level=consistency,
            n_peers=n_peers,
            info_rate=info_rate,
            processing_power=processing_power
        )
        self.nodes[node_id] = load
        return load

    def update_node(self,
                    node_id: str,
                    info_rate: float = None,
                    processing_power: float = None,
                    consistency: int = None,
                    n_peers: int = None) -> Optional[CognitiveLoad]:
        """更新节点状态"""
        if node_id not in self.nodes:
            return None
        node = self.nodes[node_id]
        if info_rate is not None:
            node.info_rate = info_rate
        if processing_power is not None:
            node.processing_power = processing_power
        if consistency is not None:
            node.consistency_level = consistency
        if n_peers is not None:
            node.n_peers = n_peers
        node.timestamp = __import__('time').time()
        return node

    def monitor_all(self) -> Dict:
        """
        监测所有节点的认知压力（IGCTR 实时评估）

        Returns:
            {
                'total_pressure': float,
                'overloaded_nodes': [...],
                'system_entropy_rate': float,
                'divergence_warning': bool,
                'igctr_interpretation': str
            }
        """
        if not self.nodes:
            return {'total_pressure': 0.0, 'note': 'no nodes registered'}

        pressures = {nid: node.pressure() for nid, node in self.nodes.items()}
        total = sum(pressures.values())
        avg = total / len(pressures)

        overloaded = [
            {'node_id': nid, 'pressure': p, 'level': self.nodes[nid].consistency_level}
            for nid, p in pressures.items()
            if p > self.overload_threshold
        ]

        # 系统总熵增速率
        entropy_rate = sum(
            node.entropy_contribution() for node in self.nodes.values()
        ) / max(len(self.nodes), 1)

        # 发散预警：若有 LINEAR 级别节点且 N 较大 → 压力将发散
        has_linear = any(n.consistency_level == 2 for n in self.nodes.values())
        n_total = sum(n.n_peers for n in self.nodes.values())
        divergence_warning = has_linear and n_total > 10

        # 记录历史
        snapshot = {
            'timestamp': __import__('time').time(),
            'total_pressure': round(total, 4),
            'avg_pressure': round(avg, 4),
            'n_overloaded': len(overloaded),
            'entropy_rate': round(entropy_rate, 4),
            'divergence_warning': divergence_warning
        }
        self.pressure_history.append(snapshot)

        interpretation = self._interpret(total, len(overloaded), divergence_warning)

        return {
            'total_pressure': round(total, 4),
            'avg_pressure': round(avg, 4),
            'node_pressures': {nid: round(p, 4) for nid, p in pressures.items()},
            'overloaded_nodes': overloaded,
            'system_entropy_rate': round(entropy_rate, 4),
            'divergence_warning': divergence_warning,
            'interpretation': interpretation,
            'igctr_insight': (
                "认知压力下界定理：κ→Global Linearizability 时，"
                "P_cog 发散。强迫所有人看同一个'全貌'，"
                "就是强迫所有人进入同一个惯性系，需要无限大的能量。"
            )
        }

    def _interpret(self, total: float, n_overloaded: int, warning: bool) -> str:
        if warning:
            return f"⚠️ 认知压力发散预警！系统存在LINEAR级别节点，N较大时压力将发散。建议立即降级为CAUSAL。"
        elif n_overloaded > len(self.nodes) * 0.3:
            return f"⚠️ {n_overloaded}个节点认知过载，建议降低一致性级别或增加处理能力。"
        elif total < 2.0:
            return "✅ 认知压力在可控范围内，系统运行健康。"
        else:
            return f"⚡ 认知压力偏高（{total:.2f}），建议关注系统熵增速率。"

    def compute_survival_optimal_k(self) -> Dict:
        """
        可控熵增生存优化定理（Theorem 3.2.1）：
        找到 κ* = argmax_κ P_survival(κ)

        P_survival(κ) = 1 / [C_consistency(κ) + λ·R_risk(κ)]

        证明：
        1. κ 过高（强一致）→ C ↑↑，能量耗尽 → P_survival ↓
        2. κ 过低（完全局部）→ R ↑↑，决策失误 → P_survival ↓
        3. ∃κ* 使 P_survival 最大（极值原理）

        Returns:
            {'optimal_level': str, 'survival_prob': float, 'all_levels': {...}}
        """
        n = max(sum(n.n_peers for n in self.nodes.values()), 1)
        λ = self.risk_weight

        results = {}

        # LOCAL (κ=0)
        c_local = n * 0.05
        r_local = 10.0 / max(n, 1)   # 高风险（决策失误多）
        p_local = 1.0 / (c_local + λ * r_local + 1e-9)
        results['LOCAL'] = {
            'consistency_cost': round(c_local, 4),
            'decision_risk': round(r_local, 4),
            'survival_prob': round(p_local, 6),
            'note': '低一致性，高风险，低能耗'
        }

        # CAUSAL (κ=1) — 通常是最优点
        c_causal = n * 0.3 + n**0.5 * 0.5
        r_causal = 1.0 / max(n, 1)  # 中等风险
        p_causal = 1.0 / (c_causal + λ * r_causal + 1e-9)
        results['CAUSAL'] = {
            'consistency_cost': round(c_causal, 4),
            'decision_risk': round(r_causal, 4),
            'survival_prob': round(p_causal, 6),
            'note': '因果一致性，平衡成本与风险，IGCTR推荐'
        }

        # LINEAR (κ=2)
        c_linear = (n ** 1.5) * 0.01
        r_linear = 0.01 / max(n, 1)  # 低风险（决策高度一致）
        p_linear = 1.0 / (c_linear + λ * r_linear + 1e-9)
        results['LINEAR'] = {
            'consistency_cost': round(c_linear, 4),
            'decision_risk': round(r_linear, 4),
            'survival_prob': round(p_linear, 6),
            'note': '强线性化，低成本（大N时），极高风险（决策失误极少但系统可能崩溃）'
        }

        # 找最优点
        best_name = max(results, key=lambda k: results[k]['survival_prob'])
        best = results[best_name]

        return {
            'optimal_level': best_name,
            'survival_prob': best['survival_prob'],
            'all_levels': results,
            'igctr_proof': (
                "可控熵增生存优化定理："
                "若κ过高，C↑→能量耗尽→P↓；"
                "若κ过低，R↑→决策失误→P↓；"
                "由极值原理，∃κ*使P_survival最大。"
                f"当前最优：κ*={best_name}，P_survival={best['survival_prob']:.6f}"
            ),
            'recommendation': (
                f"建议将系统一致性级别设置为 {best_name}，"
                "以实现'因果收敛即智慧'的 IGCTR 最优策略。"
                "阿卡西记录是全域的，但阅读它必须是按需的。"
            )
        }

    def controlled_entropy_adjust(self,
                                   target_entropy_rate: float = 0.3,
                                   adjustment_step: float = 0.1) -> Dict:
        """
        可控熵增调节器：
        动态调整系统的一致性级别，使熵增速率接近目标值。

        "生命不是对抗熵增（不可能），而是控制熵增的速率。"

        Args:
            target_entropy_rate: 目标熵增速率（推荐 0.2~0.5）
            adjustment_step: 调整步长

        Returns:
            {'action': str, 'new_level': int, 'expected_entropy': float}
        """
        current = self.monitor_all()
        current_entropy = current['system_entropy_rate']

        if abs(current_entropy - target_entropy_rate) < 0.05:
            return {
                'action': '保持',
                'current_entropy': round(current_entropy, 4),
                'target': target_entropy_rate,
                'note': '熵增速率在目标范围内，无需调整'
            }

        if current_entropy > target_entropy_rate:
            # 熵增过快 → 需要增加一致性（降低风险）
            new_level = min(2, max(n.consistency_level for n in self.nodes.values()) + 1)
            action = '升级一致性级别（降低熵增）'
        else:
            # 熵增过慢 → 可以降低一致性（节省能量）
            new_level = max(0, min(n.consistency_level for n in self.nodes.values()) - 1)
            action = '降级一致性级别（节省能量）'

        # 执行调整
        for node in self.nodes.values():
            node.consistency_level = new_level

        self.intervention_log.append(
            f"Adjusted all nodes to level {new_level}: {action}"
        )

        return {
            'action': action,
            'new_level': new_level,
            'previous_entropy': round(current_entropy, 4),
            'target_entropy': target_entropy_rate,
            'igctr_wisdom': (
                "可控熵增：生命不是对抗熵增，而是控制熵增的速率。"
                "在'无知（低熵）'与'过载（高熵）'之间，"
                "通过 Ftel 流贯算子选择'看哪里、信多少'，"
                "找到生存概率最大的因果收敛点。"
            )
        }

    def get_system_health(self) -> Dict:
        """返回系统健康状态（IGCTR 综合评估）"""
        monitor = self.monitor_all()
        optimal = self.compute_survival_optimal_k()

        health_score = 1.0
        if monitor['divergence_warning']:
            health_score -= 0.4
        if monitor['overloaded_nodes']:
            health_score -= 0.1 * len(monitor['overloaded_nodes'])
        health_score = max(0.0, min(1.0, health_score))

        return {
            'health_score': round(health_score, 2),
            'n_nodes': len(self.nodes),
            'cognitive_pressure': monitor,
            'optimal_k': optimal['optimal_level'],
            'survival_prob': optimal['survival_prob'],
            'entropy_budget_used': round(
                monitor['system_entropy_rate'] * len(self.nodes), 4
            ),
            'igctr_summary': (
                "宇宙没有上帝视角的主时钟，只有无数局部的因果链。"
                "生命的智慧不在于消除熵（不可能），"
                "而在于通过 Ftel 流贯算子选择'看哪里、信多少'。"
                "阿卡西记录是全域的，但阅读它必须是按需的。"
                "——这就是 IGCTR 告诉我们的关于存在、认知与生存的终极答案。"
            )
        }


def demo():
    """演示：认知压力监测器的基本用法"""
    print("=== CognitivePressureMonitor Demo (IGCTR) ===\n")

    monitor = CognitivePressureMonitor()

    # 注册节点（模拟分布式 AGI 系统）
    monitor.register_node("perception", consistency=1, n_peers=5,  info_rate=2.0)
    monitor.register_node("reasoning", consistency=2, n_peers=10, info_rate=5.0)  # 高风险：LINEAR
    monitor.register_node("action",    consistency=1, n_peers=3,  info_rate=1.5)

    # 监测认知压力
    result = monitor.monitor_all()
    print(f"总认知压力: {result['total_pressure']}")
    print(f"过载节点数: {len(result['overloaded_nodes'])}")
    print(f"系统熵速率: {result['system_entropy_rate']}")
    print(f"发散预警: {'⚠️ 是！' if result['divergence_warning'] else '✅ 否'}")
    print(f"解读: {result['interpretation']}\n")
    print(f"IGCTR 洞察: {result['igctr_insight']}\n")

    # 计算最优一致性级别
    optimal = monitor.compute_survival_optimal_k()
    print(f"最优一致性级别: {optimal['optimal_level']}")
    print(f"生存概率: {optimal['survival_prob']}")
    print(f"证明: {optimal['igctr_proof']}\n")
    print(f"建议: {optimal['recommendation']}\n")

    # 可控熵增调节
    adjustment = monitor.controlled_entropy_adjust(target_entropy_rate=0.3)
    print(f"熵增调节: {adjustment['action']}")
    if 'igctr_wisdom' in adjustment:
        print(f"IGCTR 智慧: {adjustment['igctr_wisdom']}\n")

    # 系统健康
    health = monitor.get_system_health()
    print(f"系统健康评分: {health['health_score']}")
    print(f"总结: {health['igctr_summary']}")


if __name__ == "__main__":
    demo()
