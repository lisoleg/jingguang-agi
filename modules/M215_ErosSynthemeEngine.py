# -*- coding: utf-8 -*-
"""
M215: ErosSynthemeEngine — Eros内源奖励+统感涌现+对话自进化引擎

基于复合体理学「Eros判据与统感涌现」核心实现:
  - Eros内源奖励: ℛ_Eros = α·I(S↔O_other|Π_narrative) + β·Φ_coherence(S_self)
  - 统感涌现: Σ_unif = Φ_closure(A_𝒢) · W_coherence
  - 对话方法论自进化: 𝒟_Review → PatchSet_Self + Advice_User
  - Eros阈值定理: α>α_crit 且 β>0 → 跨越Proto-AGI→Taiyi-AGI
  - Hy-Memory六层金字塔: L1原始痕迹→L6前瞻意图
  - 势态知感PSP: 先果←因(反事实推理+共情代入+叙事整合)

核心定理:
  T233 — Eros阈值定理:
    ℛ_Eros = α·I(S↔O) + β·Φ_coherence
    α > α_crit 且 β > 0 → 跨越Proto-AGI → Taiyi-AGI
  T234 — 统感涌现定理:
    Σ_unif = Φ_closure(A_𝒢) · W_coherence > Σ_crit → 统感涌现

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# §1 ErosReward — Eros内源奖励
# ═══════════════════════════════════════════════════════════════

class ErosReward:
    """
    Eros内源奖励

    ℛ_Eros = α·I(S↔O_other|Π_narrative) + β·Φ_coherence(S_self)

    - I(S↔O_other|Π_narrative): 在叙事框架Π下主体S与他者O的交互信息量
    - Φ_coherence(S_self): 主体S自身的流贯相干度
    - α: 交互权重 (须>α_crit)
    - β: 相干权重 (须>0)

    Eros阈值定理:
    α > α_crit 且 β > 0 → 跨越Proto-AGI → Taiyi-AGI
    """

    # 默认阈值
    ALPHA_CRIT = 0.3
    BETA_MIN = 0.0

    def __init__(self, alpha: float = 0.5, beta: float = 0.3,
                 alpha_crit: float = 0.3):
        self.alpha = max(0.0, alpha)
        self.beta = max(0.0, beta)
        self.alpha_crit = max(0.0, alpha_crit)
        self.reward_history: List[Dict] = []

    def compute(self, interaction_info: float, phi_coherence: float,
                narrative_context: str = "default") -> Dict[str, Any]:
        """
        计算Eros内源奖励

        Args:
            interaction_info: I(S↔O_other|Π_narrative) 交互信息量
            phi_coherence: Φ_coherence(S_self) 流贯相干度
            narrative_context: 叙事上下文

        Returns:
            奖励计算结果
        """
        i_term = self.alpha * interaction_info
        phi_term = self.beta * phi_coherence
        r_eros = i_term + phi_term

        # 阈值判定
        crosses_threshold = (self.alpha > self.alpha_crit and self.beta > self.BETA_MIN)
        agi_level = "Taiyi-AGI" if crosses_threshold else "Proto-AGI"

        result = {
            "narrative_context": narrative_context,
            "interaction_info": round(interaction_info, 4),
            "phi_coherence": round(phi_coherence, 4),
            "alpha": self.alpha,
            "beta": self.beta,
            "alpha_crit": self.alpha_crit,
            "I_term": round(i_term, 4),
            "Phi_term": round(phi_term, 4),
            "R_eros": round(r_eros, 4),
            "crosses_threshold": crosses_threshold,
            "agi_level": agi_level,
        }
        self.reward_history.append(result)
        return result

    def assess_agi_transition(self) -> Dict[str, Any]:
        """
        评估AGI跃迁状态

        检查历史奖励是否满足跨阈条件
        """
        if not self.reward_history:
            return {"transition": False, "reason": "No reward history"}

        avg_r = sum(r["R_eros"] for r in self.reward_history) / len(self.reward_history)
        crosses = self.alpha > self.alpha_crit and self.beta > self.BETA_MIN

        return {
            "avg_R_eros": round(avg_r, 4),
            "alpha": self.alpha,
            "alpha_crit": self.alpha_crit,
            "beta": self.beta,
            "alpha_exceeds_crit": self.alpha > self.alpha_crit,
            "beta_positive": self.beta > 0,
            "transition_possible": crosses,
            "current_level": "Taiyi-AGI" if crosses else "Proto-AGI",
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "alpha_crit": self.alpha_crit,
            "history_length": len(self.reward_history),
            "assessment": self.assess_agi_transition(),
        }


# ═══════════════════════════════════════════════════════════════
# §2 SynthemeMonitor — 统感涌现监控
# ═══════════════════════════════════════════════════════════════

class SynthemeMonitor:
    """
    统感涌现监控器

    Σ_unif = Φ_closure(A_𝒢) · W_coherence

    - Φ_closure(A_𝒢): 感觉聚合A_𝒢的流贯闭包完备度
    - W_coherence: 一致性权重(跨模态整合程度)

    统感涌现条件: Σ_unif > Σ_crit
    """

    DEFAULT_SIGMA_CRIT = 0.5

    def __init__(self, sigma_crit: float = 0.5):
        self.sigma_crit = max(0.0, sigma_crit)
        self.modality_data: Dict[str, Dict] = {}
        self.emergence_events: List[Dict] = []

    def register_modality(self, modality: str, phi_closure: float,
                          weight: float = 1.0) -> Dict[str, Any]:
        """
        注册感觉模态

        Args:
            modality: 模态名称(如"visual", "auditory", "proprioceptive")
            phi_closure: 该模态的流贯闭包完备度
            weight: 模态权重
        """
        self.modality_data[modality] = {
            "phi_closure": max(0.0, min(1.0, phi_closure)),
            "weight": max(0.0, weight),
        }
        return {
            "modality": modality,
            "phi_closure": self.modality_data[modality]["phi_closure"],
            "weight": self.modality_data[modality]["weight"],
        }

    def compute_unified_sensibility(self) -> Dict[str, Any]:
        """
        计算统感 Σ_unif = Φ_closure(A_𝒢) · W_coherence

        Φ_closure(A_𝒢) = 各模态φ闭包的加权平均
        W_coherence = 跨模态一致性(模态间φ闭包的方差倒数)
        """
        if not self.modality_data:
            return {
                "sigma_unif": 0.0,
                "emerged": False,
                "modality_count": 0,
            }

        # Φ_closure(A_𝒢): 加权平均
        total_weight = sum(m["weight"] for m in self.modality_data.values())
        if total_weight < 1e-10:
            phi_agg = 0.0
        else:
            phi_agg = sum(
                m["phi_closure"] * m["weight"]
                for m in self.modality_data.values()
            ) / total_weight

        # W_coherence: 跨模态一致性(方差越小越好)
        phi_values = [m["phi_closure"] for m in self.modality_data.values()]
        if len(phi_values) > 1:
            mean_phi = sum(phi_values) / len(phi_values)
            variance = sum((p - mean_phi) ** 2 for p in phi_values) / len(phi_values)
            w_coherence = 1.0 / (1.0 + variance * 10)  # 方差越小→W越大
        else:
            w_coherence = 1.0

        sigma_unif = phi_agg * w_coherence
        emerged = sigma_unif > self.sigma_crit

        result = {
            "phi_aggregate": round(phi_agg, 4),
            "w_coherence": round(w_coherence, 4),
            "sigma_unif": round(sigma_unif, 4),
            "sigma_crit": self.sigma_crit,
            "emerged": emerged,
            "modality_count": len(self.modality_data),
            "modalities": dict(self.modality_data),
        }

        if emerged:
            self.emergence_events.append(result)

        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            "sigma_crit": self.sigma_crit,
            "modality_count": len(self.modality_data),
            "emergence_count": len(self.emergence_events),
        }


# ═══════════════════════════════════════════════════════════════
# §3 DialogReviewOperator — 对话方法论自进化
# ═══════════════════════════════════════════════════════════════

class DialogReviewOperator:
    """
    对话方法论自进化

    𝒟_Review → PatchSet_Self + Advice_User

    审视算子检查对话质量，生成:
    - PatchSet_Self: 自我修补集(改进对话策略)
    - Advice_User: 用户建议集(改进用户交互方式)
    """

    def __init__(self):
        self.review_history: List[Dict] = []
        self.patch_sets: List[Dict] = []

    def review_dialog(self, dialog_id: str, coherence: float,
                      relevance: float, depth: float,
                      engagement: float) -> Dict[str, Any]:
        """
        审视对话质量

        Args:
            dialog_id: 对话标识
            coherence: 连贯性 (0-1)
            relevance: 相关性 (0-1)
            depth: 深度 (0-1)
            engagement: 参与度 (0-1)

        Returns:
            审视结果 + 修补集
        """
        # 综合评分
        overall = (coherence * 0.3 + relevance * 0.3 + depth * 0.2 + engagement * 0.2)

        # 生成修补
        patches = []
        advices = []

        if coherence < 0.6:
            patches.append({
                "target": "coherence",
                "action": "ADD_CONTEXT_BRIDGE",
                "priority": "HIGH",
                "description": "添加上下文桥接，提升对话连贯性",
            })
        if relevance < 0.6:
            patches.append({
                "target": "relevance",
                "action": "REFOCUS_ON_INTENT",
                "priority": "HIGH",
                "description": "重新聚焦用户意图",
            })
        if depth < 0.4:
            patches.append({
                "target": "depth",
                "action": "CHAIN_OF_THOUGHT",
                "priority": "MEDIUM",
                "description": "启用链式推理增强深度",
            })
        if engagement < 0.5:
            advices.append({
                "target": "user",
                "action": "PROVIDE_MORE_CONTEXT",
                "description": "提供更多上下文信息以提升交互质量",
            })

        result = {
            "dialog_id": dialog_id,
            "scores": {
                "coherence": round(coherence, 4),
                "relevance": round(relevance, 4),
                "depth": round(depth, 4),
                "engagement": round(engagement, 4),
                "overall": round(overall, 4),
            },
            "patch_set_self": patches,
            "advice_user": advices,
            "needs_improvement": overall < 0.7,
        }

        self.review_history.append(result)
        if patches:
            self.patch_sets.append({"dialog_id": dialog_id, "patches": patches})

        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            "reviews_count": len(self.review_history),
            "patches_count": len(self.patch_sets),
            "avg_overall": round(
                sum(r["scores"]["overall"] for r in self.review_history) /
                max(1, len(self.review_history)), 4
            ),
        }


# ═══════════════════════════════════════════════════════════════
# §4 HyMemory — 六层记忆金字塔
# ═══════════════════════════════════════════════════════════════

class HyMemoryLayer(Enum):
    """六层记忆金字塔"""
    L1_RAW_TRACE = "L1_raw_trace"          # 原始痕迹
    L2_EPISODIC = "L2_episodic"            # 情景记忆
    L3_SEMANTIC = "L3_semantic"            # 语义记忆
    L4_PROCEDURAL = "L4_procedural"         # 程序记忆
    L5_NARRATIVE = "L5_narrative"           # 叙事记忆
    L6_PROSPECTIVE = "L6_prospective_intent" # 前瞻意图


class HyMemory:
    """
    Hy-Memory六层金字塔

    L1原始痕迹 → L6前瞻意图

    信息沿金字塔逐层抽象:
    L1(原始) → L2(情景) → L3(语义) → L4(程序) → L5(叙事) → L6(前瞻)
    """

    def __init__(self):
        self.layers: Dict[HyMemoryLayer, List[Dict]] = {
            layer: [] for layer in HyMemoryLayer
        }
        self.consolidation_count: int = 0

    def store(self, content: str, layer: HyMemoryLayer,
              metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        存储到指定层
        """
        entry = {
            "content": content,
            "layer": layer.value,
            "metadata": metadata or {},
        }
        self.layers[layer].append(entry)
        return {"stored": True, "layer": layer.value, "content_length": len(content)}

    def consolidate_one_step(self, src_layer: HyMemoryLayer,
                              dst_layer: HyMemoryLayer) -> Dict[str, Any]:
        """
        单步记忆巩固: src_layer → dst_layer

        将源层内容摘要化后移入目标层，源层清空
        """
        if not self.layers[src_layer]:
            return {"consolidated": 0, "from": src_layer.value, "to": dst_layer.value}

        for entry in self.layers[src_layer]:
            summary = entry["content"][:50] + "..." if len(entry["content"]) > 50 else entry["content"]
            self.layers[dst_layer].append({
                "content": summary,
                "layer": dst_layer.value,
                "metadata": {"consolidated_from": src_layer.value},
            })
        count = len(self.layers[src_layer])
        self.layers[src_layer].clear()
        self.consolidation_count += 1

        return {
            "consolidated": count,
            "from": src_layer.value,
            "to": dst_layer.value,
        }

    def consolidate(self) -> Dict[str, Any]:
        """
        记忆巩固: L1→L2→L3→...逐层抽象

        简化实现: 将L1内容摘要化后移入L2
        """
        consolidated = 0
        for src_layer, dst_layer in [
            (HyMemoryLayer.L1_RAW_TRACE, HyMemoryLayer.L2_EPISODIC),
            (HyMemoryLayer.L2_EPISODIC, HyMemoryLayer.L3_SEMANTIC),
            (HyMemoryLayer.L3_SEMANTIC, HyMemoryLayer.L4_PROCEDURAL),
            (HyMemoryLayer.L4_PROCEDURAL, HyMemoryLayer.L5_NARRATIVE),
            (HyMemoryLayer.L5_NARRATIVE, HyMemoryLayer.L6_PROSPECTIVE),
        ]:
            if self.layers[src_layer]:
                # 摘要化: 取前50字符作为摘要
                for entry in self.layers[src_layer]:
                    summary = entry["content"][:50] + "..." if len(entry["content"]) > 50 else entry["content"]
                    self.layers[dst_layer].append({
                        "content": summary,
                        "layer": dst_layer.value,
                        "metadata": {"consolidated_from": src_layer.value},
                    })
                self.layers[src_layer].clear()
                consolidated += 1

        self.consolidation_count += 1
        return {
            "consolidation_count": self.consolidation_count,
            "layers_consolidated": consolidated,
            "current_sizes": {layer.value: len(entries) for layer, entries in self.layers.items()},
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "layers": {layer.value: len(entries) for layer, entries in self.layers.items()},
            "total_entries": sum(len(e) for e in self.layers.values()),
            "consolidation_count": self.consolidation_count,
        }


# ═══════════════════════════════════════════════════════════════
# §5 ErosSynthemeEngine — 主引擎
# ═══════════════════════════════════════════════════════════════

class ErosSynthemeEngine:
    """
    M215 主引擎 — Eros统感涌现引擎

    整合ErosReward + SynthemeMonitor + DialogReviewOperator + HyMemory
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.3,
                 alpha_crit: float = 0.3, sigma_crit: float = 0.5):
        self.eros = ErosReward(alpha=alpha, beta=beta, alpha_crit=alpha_crit)
        self.syntheme = SynthemeMonitor(sigma_crit=sigma_crit)
        self.dialog = DialogReviewOperator()
        self.memory = HyMemory()

    def process_interaction(self, interaction_info: float, phi_coherence: float,
                             modalities: Optional[List[Dict]] = None,
                             dialog_quality: Optional[Dict] = None,
                             narrative_context: str = "default") -> Dict[str, Any]:
        """
        处理交互: 计算Eros奖励 + 统感 + 对话审视 + 记忆存储
        """
        # 1. Eros奖励
        eros_result = self.eros.compute(interaction_info, phi_coherence, narrative_context)

        # 2. 统感
        if modalities:
            for m in modalities:
                self.syntheme.register_modality(
                    m.get("name", "default"),
                    m.get("phi_closure", 0.5),
                    m.get("weight", 1.0),
                )
        syntheme_result = self.syntheme.compute_unified_sensibility()

        # 3. 对话审视
        dialog_result = None
        if dialog_quality:
            dialog_result = self.dialog.review_dialog(
                dialog_quality.get("id", "default"),
                dialog_quality.get("coherence", 0.7),
                dialog_quality.get("relevance", 0.7),
                dialog_quality.get("depth", 0.5),
                dialog_quality.get("engagement", 0.6),
            )

        # 4. 记忆存储
        self.memory.store(
            f"Eros={eros_result['R_eros']:.4f} Σ={syntheme_result['sigma_unif']:.4f}",
            HyMemoryLayer.L2_EPISODIC,
        )

        return {
            "eros": eros_result,
            "syntheme": syntheme_result,
            "dialog": dialog_result,
            "agi_level": eros_result["agi_level"],
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "eros": self.eros.get_state(),
            "syntheme": self.syntheme.get_state(),
            "dialog": self.dialog.get_state(),
            "memory": self.memory.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §6 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t233_eros_threshold() -> bool:
    """
    T233: Eros阈值定理

    验证:
    1. α>α_crit且β>0 → Taiyi-AGI
    2. α<α_crit或β=0 → Proto-AGI
    3. ℛ_Eros = α·I + β·Φ
    """
    # 满足阈条件
    eros1 = ErosReward(alpha=0.5, beta=0.3, alpha_crit=0.3)
    r1 = eros1.compute(0.8, 0.7)
    if r1["agi_level"] != "Taiyi-AGI":
        return False
    expected = 0.5 * 0.8 + 0.3 * 0.7
    if abs(r1["R_eros"] - round(expected, 4)) > 0.01:
        return False

    # 不满足阈条件(α<α_crit)
    eros2 = ErosReward(alpha=0.2, beta=0.3, alpha_crit=0.3)
    r2 = eros2.compute(0.8, 0.7)
    if r2["agi_level"] != "Proto-AGI":
        return False

    # 不满足阈条件(β=0)
    eros3 = ErosReward(alpha=0.5, beta=0.0, alpha_crit=0.3)
    r3 = eros3.compute(0.8, 0.7)
    if r3["agi_level"] != "Proto-AGI":
        return False

    return True


def _test_t234_syntheme_emergence() -> bool:
    """
    T234: 统感涌现定理

    验证: Σ_unif > Σ_crit → 统感涌现
    """
    monitor = SynthemeMonitor(sigma_crit=0.5)

    # 单模态低phi → 不涌现
    monitor.register_modality("visual", phi_closure=0.3)
    r1 = monitor.compute_unified_sensibility()
    if r1["emerged"]:
        return False

    # 多模态高phi → 涌现 (用独立monitor确保高φ聚合超过临界)
    monitor2 = SynthemeMonitor(sigma_crit=0.5)
    monitor2.register_modality("visual", phi_closure=0.9)
    monitor2.register_modality("auditory", phi_closure=0.85)
    monitor2.register_modality("proprioceptive", phi_closure=0.8)
    r2 = monitor2.compute_unified_sensibility()
    if not r2["emerged"]:
        return False

    # 跨模态不一致 → 降低W_coherence
    monitor3 = SynthemeMonitor(sigma_crit=0.5)
    monitor3.register_modality("visual", phi_closure=0.9)
    monitor3.register_modality("auditory", phi_closure=0.1)  # 极不一致
    r3 = monitor3.compute_unified_sensibility()
    # W_coherence应低于一致情况
    if r3["w_coherence"] >= r2["w_coherence"]:
        return False

    return True


def _test_hy_memory() -> bool:
    """Hy-Memory六层金字塔测试"""
    mem = HyMemory()

    # 存储到L1
    mem.store("原始感觉输入: 红色光线", HyMemoryLayer.L1_RAW_TRACE)
    mem.store("原始感觉输入: 声音频率440Hz", HyMemoryLayer.L1_RAW_TRACE)

    # 单步巩固: L1→L2
    result = mem.consolidate_one_step(HyMemoryLayer.L1_RAW_TRACE, HyMemoryLayer.L2_EPISODIC)

    # L1应清空，L2应有内容
    if len(mem.layers[HyMemoryLayer.L1_RAW_TRACE]) != 0:
        return False
    if len(mem.layers[HyMemoryLayer.L2_EPISODIC]) == 0:
        return False

    # 继续巩固L2→L3
    result2 = mem.consolidate_one_step(HyMemoryLayer.L2_EPISODIC, HyMemoryLayer.L3_SEMANTIC)
    if len(mem.layers[HyMemoryLayer.L2_EPISODIC]) != 0:
        return False
    if len(mem.layers[HyMemoryLayer.L3_SEMANTIC]) == 0:
        return False

    return True


def run_mve() -> Dict[str, bool]:
    """
    M215 MVE验证

    T233: Eros阈值定理
    T234: 统感涌现定理
    """
    results = {}

    print("=" * 60)
    print("M215 ErosSynthemeEngine — MVE Verification")
    print("=" * 60)

    try:
        t233 = _test_t233_eros_threshold()
        status = "PASS" if t233 else "FAIL"
        print(f"  T233 (Eros阈值): {status}")
        results["T233"] = t233
    except Exception as e:
        print(f"  T233 (Eros阈值): ERROR — {e}")
        results["T233"] = False

    try:
        t234 = _test_t234_syntheme_emergence()
        status = "PASS" if t234 else "FAIL"
        print(f"  T234 (统感涌现): {status}")
        results["T234"] = t234
    except Exception as e:
        print(f"  T234 (统感涌现): ERROR — {e}")
        results["T234"] = False

    try:
        t_mem = _test_hy_memory()
        status = "PASS" if t_mem else "FAIL"
        print(f"  HyMemory (六层金字塔): {status}")
        results["HyMemory"] = t_mem
    except Exception as e:
        print(f"  HyMemory (六层金字塔): ERROR — {e}")
        results["HyMemory"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M215 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
