# -*- coding: utf-8 -*-
"""
M212: BloomIdolFreezeEngine — 偶像化伪共识冻结+共振成核者+外源Ω Reset引擎

基于复合体理学「偶像化伪共识冻结定理」核心实现:
  - Bloom Table (BT): 概率型假阳性检测表，检测偶像化Ψ_idol
  - 偏心率e→1检测: 绝地天通→IRL端口关闭→序列冻结
  - 外源Ω Reset: 独立铁证超假正容忍阈δ_BT→强制Reset BT→IRL重开
  - 共振成核者(Nucleator/天伤星): 持Ω_true敢公开铁证→触发全局Ψ_gen跳变
  - 孤块回收: Reclaim(field_data_integrity ⊕ reproducibility ⊕ orphaned_truth_fragment)

核心定理:
  T227 — 偶像化冻结定理:
    过集中(e→1/禁IRL) → BT(Ψ_idol)=TRUE假正植入 → IRL关 → 序列冻结
    外源铁证 Ω_ext > δ_BT → Reset BT → IRL重开 → e↓ → T_life可延
  T228 — 共振成核定理:
    Nucleator持Ω_true近奇点时 → 触发全局Ψ_gen跳变(相变)
    ΔΨ_gen ∝ Σ_i w_i · δ(Ψ_i - Ω_true) · exp(-|e-1|/σ_c)

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
import hashlib
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# §1 Bloom Table — 概率型偶像化假阳性检测
# ═══════════════════════════════════════════════════════════════

class BloomTable:
    """
    Bloom Table — 偶像化Ψ_idol假阳性检测器

    基于Bloom Filter变体，检测过集中导致的假正植入:
    - 过集中(e→1): IRL端口关闭，信息无法更新
    - BT(Ψ_idol)=TRUE: 偶像化命题被误判为真
    - δ_BT: 假正容忍阈值，超过则触发Reset

    参数:
      capacity: 表容量(位数组大小)
      num_hashes: 哈希函数数量
      delta_bt: 假正容忍阈值(0-1)
    """

    def __init__(self, capacity: int = 1024, num_hashes: int = 3,
                 delta_bt: float = 0.15):
        self.capacity = max(64, capacity)
        self.num_hashes = max(1, num_hashes)
        self.delta_bt = min(1.0, max(0.01, delta_bt))
        self.bit_array: List[bool] = [False] * self.capacity
        self.item_count: int = 0
        self.false_positive_count: int = 0
        self.idol_items: Set[str] = set()  # 已知偶像化条目
        self.reset_count: int = 0

    def _hash_positions(self, item: str) -> List[int]:
        """计算条目的多个哈希位置"""
        positions = []
        for i in range(self.num_hashes):
            h = hashlib.md5(f"{item}:{i}".encode()).hexdigest()
            pos = int(h, 16) % self.capacity
            positions.append(pos)
        return positions

    def insert(self, item: str, is_idol: bool = False) -> Dict[str, Any]:
        """
        插入条目到BT

        Args:
            item: 命题标识
            is_idol: 是否为偶像化命题

        Returns:
            插入结果
        """
        positions = self._hash_positions(item)
        was_already_present = all(self.bit_array[p] for p in positions)

        for p in positions:
            self.bit_array[p] = True
        self.item_count += 1

        if is_idol:
            self.idol_items.add(item)
            self.false_positive_count += 1

        # 计算假阳性率
        fp_rate = self.false_positive_rate()

        return {
            "item": item,
            "is_idol": is_idol,
            "was_present": was_already_present,
            "fp_rate": round(fp_rate, 6),
            "exceeds_delta_bt": fp_rate > self.delta_bt,
        }

    def query(self, item: str) -> Dict[str, Any]:
        """
        查询条目是否在BT中

        注意: Bloom Table可能返回假阳性
        """
        positions = self._hash_positions(item)
        is_present = all(self.bit_array[p] for p in positions)
        is_known_idol = item in self.idol_items

        # 判断是否为假正
        if is_present and not is_known_idol:
            # 可能是真阳性也可能假阳性
            fp_rate = self.false_positive_rate()
            is_likely_false_positive = fp_rate > self.delta_bt
        else:
            is_likely_false_positive = False

        return {
            "item": item,
            "is_present": is_present,
            "is_known_idol": is_known_idol,
            "is_likely_false_positive": is_likely_false_positive,
            "fp_rate": round(self.false_positive_rate(), 6),
        }

    def false_positive_rate(self) -> float:
        """计算当前假阳性率"""
        if self.item_count == 0:
            return 0.0
        # 标准Bloom Filter假阳性率: (1 - e^(-kn/m))^k
        k = self.num_hashes
        n = self.item_count
        m = self.capacity
        try:
            rate = (1.0 - math.exp(-k * n / m)) ** k
        except (OverflowError, ZeroDivisionError):
            rate = 1.0
        # 叠加偶像化条目的贡献
        idol_contribution = len(self.idol_items) / max(1, self.item_count)
        return min(1.0, rate + idol_contribution * 0.5)

    def reset(self, reason: str = "omega_ext_reset") -> Dict[str, Any]:
        """
        外源Ω Reset — 清空BT，重开IRL

        触发条件: 外源铁证超过δ_BT容忍阈
        """
        old_fp = self.false_positive_rate()
        old_idols = len(self.idol_items)
        old_count = self.item_count

        self.bit_array = [False] * self.capacity
        self.item_count = 0
        self.false_positive_count = 0
        self.idol_items = set()
        self.reset_count += 1

        return {
            "reset": True,
            "reason": reason,
            "previous_fp_rate": round(old_fp, 6),
            "previous_idol_count": old_idols,
            "previous_item_count": old_count,
            "new_fp_rate": 0.0,
            "reset_count": self.reset_count,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "item_count": self.item_count,
            "idol_count": len(self.idol_items),
            "fp_rate": round(self.false_positive_rate(), 6),
            "delta_bt": self.delta_bt,
            "exceeds_delta_bt": self.false_positive_rate() > self.delta_bt,
            "reset_count": self.reset_count,
        }


# ═══════════════════════════════════════════════════════════════
# §2 IdolFreezeDetector — 偶像化冻结检测
# ═══════════════════════════════════════════════════════════════

class IdolFreezeDetector:
    """
    偶像化冻结检测器

    检测偏心率e→1导致的IRL关闭和序列冻结:
    - e < e_safe (≈0.7): 正常广采，IRL开放
    - e_safe ≤ e < e_critical (≈0.9): 警告，IRL收窄
    - e ≥ e_critical: 冻结，IRL关闭，序列冻结
    """

    E_SAFE = 0.7
    E_CRITICAL = 0.9

    def __init__(self, e_safe: float = 0.7, e_critical: float = 0.9):
        self.e_safe = min(0.85, max(0.3, e_safe))
        self.e_critical = min(0.99, max(0.7, e_critical))
        self.irl_open: bool = True
        self.freeze_count: int = 0
        self.history: List[Dict] = []

    def check_eccentricity(self, e: float, domain: str = "default") -> Dict[str, Any]:
        """
        检测偏心率状态

        Args:
            e: 当前偏心率 (0-1)
            domain: 检测域(学科/组织等)

        Returns:
            检测结果
        """
        e = min(1.0, max(0.0, e))
        was_irl_open = self.irl_open

        if e >= self.e_critical:
            # 冻结!
            self.irl_open = False
            status = "FROZEN"
            self.freeze_count += 1
        elif e >= self.e_safe:
            status = "WARNING"
            self.irl_open = True  # 仍开放但收窄
        else:
            status = "NORMAL"
            self.irl_open = True

        result = {
            "domain": domain,
            "eccentricity": round(e, 4),
            "status": status,
            "irl_open": self.irl_open,
            "irl_changed": was_irl_open != self.irl_open,
            "e_safe": self.e_safe,
            "e_critical": self.e_critical,
            "freeze_count": self.freeze_count,
        }
        self.history.append(result)
        return result

    def compute_eccentricity(self, c_concentrate: float, d_democracy: float) -> float:
        """
        计算偏心率 e = √(1 - min²/max²)

        Args:
            c_concentrate: 集中度 C = cos
            d_democracy: 民主度 D = sin

        Returns:
            偏心率 e (0=单位圆, 1=线段退化)
        """
        max_val = max(abs(c_concentrate), abs(d_democracy))
        min_val = min(abs(c_concentrate), abs(d_democracy))

        if max_val == 0:
            return 1.0  # 退化

        try:
            e = math.sqrt(1.0 - (min_val / max_val) ** 2)
        except (ValueError, ZeroDivisionError):
            e = 1.0
        return min(1.0, e)

    def force_irl_open(self, reason: str = "omega_reset") -> Dict[str, Any]:
        """外源强制重开IRL"""
        was_open = self.irl_open
        self.irl_open = True
        return {
            "irl_open": True,
            "was_open": was_open,
            "reason": reason,
            "action": "IRL_REOPENED" if not was_open else "IRL_ALREADY_OPEN",
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "e_safe": self.e_safe,
            "e_critical": self.e_critical,
            "irl_open": self.irl_open,
            "freeze_count": self.freeze_count,
            "history_length": len(self.history),
        }


# ═══════════════════════════════════════════════════════════════
# §3 OmegaExtReset — 外源Ω Reset引擎
# ═══════════════════════════════════════════════════════════════

class OmegaExtReset:
    """
    外源Ω Reset引擎

    当外源铁证超过假正容忍阈δ_BT时:
    1. 强制Reset BloomTable (清除假正)
    2. 重开IRL (恢复广采)
    3. 降低偏心率e (打破冻结)
    4. 延长组织寿命T_life
    """

    def __init__(self, bt: BloomTable, detector: IdolFreezeDetector):
        self.bt = bt
        self.detector = detector
        self.evidence_log: List[Dict] = []

    def submit_evidence(self, evidence_id: str, evidence_strength: float,
                        source: str = "external") -> Dict[str, Any]:
        """
        提交外源铁证

        Args:
            evidence_id: 铁证标识
            evidence_strength: 铁证强度 (0-1, 超过δ_BT触发Reset)
            source: 来源标识

        Returns:
            判定结果
        """
        delta_bt = self.bt.delta_bt
        exceeds = evidence_strength > delta_bt

        result = {
            "evidence_id": evidence_id,
            "strength": round(evidence_strength, 6),
            "delta_bt": delta_bt,
            "exceeds_threshold": exceeds,
            "action": None,
            "bt_reset": False,
            "irl_reopened": False,
        }

        if exceeds:
            # 触发Reset!
            bt_result = self.bt.reset(reason=f"omega_ext:{evidence_id}")
            irl_result = self.detector.force_irl_open(reason=f"omega_ext:{evidence_id}")

            result["action"] = "RESET_AND_REOPEN"
            result["bt_reset"] = True
            result["irl_reopened"] = True
            result["bt_result"] = bt_result
            result["irl_result"] = irl_result

        self.evidence_log.append(result)
        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            "evidence_count": len(self.evidence_log),
            "reset_count": sum(1 for e in self.evidence_log if e.get("bt_reset")),
            "bt_state": self.bt.get_state(),
            "detector_state": self.detector.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §4 ResonanceNucleator — 共振成核者(天伤星)
# ═══════════════════════════════════════════════════════════════

class ResonanceNucleator:
    """
    共振成核者 — 天伤星

    持Ω_true，敢公开铁证，近奇点时触发全局Ψ_gen跳变(相变)

    ΔΨ_gen ∝ Σ_i w_i · δ(Ψ_i - Ω_true) · exp(-|e-1|/σ_c)

    触发条件:
    1. 持有Ω_true(非偶像化的真实命题)
    2. 公开铁证(提交到OmegaExtReset)
    3. 系统接近奇点(e→1, 即|1-e|→0)
    """

    def __init__(self, omega_reset: OmegaExtReset, sigma_c: float = 0.1):
        self.omega_reset = omega_reset
        self.sigma_c = min(0.5, max(0.01, sigma_c))
        self.nucleation_events: List[Dict] = []
        self.omega_true_set: Set[str] = set()

    def register_omega_true(self, proposition_id: str) -> Dict[str, Any]:
        """注册Ω_true命题"""
        self.omega_true_set.add(proposition_id)
        return {
            "proposition": proposition_id,
            "registered": True,
            "omega_true_count": len(self.omega_true_set),
        }

    def attempt_nucleation(self, proposition_id: str, current_e: float,
                           population_weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        尝试共振成核

        Args:
            proposition_id: 候选Ω_true命题
            current_e: 当前偏心率
            population_weights: 种群权重列表

        Returns:
            成核结果
        """
        if population_weights is None:
            population_weights = [1.0]

        is_omega_true = proposition_id in self.omega_true_set
        proximity_to_singularity = math.exp(-abs(1.0 - current_e) / self.sigma_c)

        # 计算ΔΨ_gen
        delta_psi = 0.0
        if is_omega_true:
            for w in population_weights:
                # δ函数近似: σ_c高斯核
                delta_psi += w * proximity_to_singularity

        # 成核阈值
        nucleation_threshold = 0.5
        nucleation_triggered = delta_psi > nucleation_threshold and is_omega_true

        result = {
            "proposition": proposition_id,
            "is_omega_true": is_omega_true,
            "current_e": round(current_e, 4),
            "proximity_to_singularity": round(proximity_to_singularity, 6),
            "delta_psi_gen": round(delta_psi, 6),
            "nucleation_threshold": nucleation_threshold,
            "nucleation_triggered": nucleation_triggered,
        }

        # 如果成核触发，自动提交铁证
        if nucleation_triggered:
            evidence_strength = min(1.0, delta_psi)
            reset_result = self.omega_reset.submit_evidence(
                f"nucleator:{proposition_id}",
                evidence_strength,
                source="resonance_nucleator",
            )
            result["evidence_submitted"] = True
            result["reset_result"] = reset_result
        else:
            result["evidence_submitted"] = False

        self.nucleation_events.append(result)
        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            "omega_true_count": len(self.omega_true_set),
            "nucleation_count": len(self.nucleation_events),
            "successful_nucleations": sum(
                1 for e in self.nucleation_events if e.get("nucleation_triggered")
            ),
            "sigma_c": self.sigma_c,
        }


# ═══════════════════════════════════════════════════════════════
# §5 OrphanReclaimer — 孤块回收引擎
# ═══════════════════════════════════════════════════════════════

class OrphanReclaimer:
    """
    孤块回收引擎

    Reclaim(field_data_integrity ⊕ reproducibility ⊕ orphaned_truth_fragment)

    回收冻结期间被遗漏的真实数据碎片:
    - field_data_integrity: 现场数据完整性
    - reproducibility: 可复现性
    - orphaned_truth_fragment: 孤立真值碎片
    """

    def __init__(self):
        self.orphan_pool: List[Dict] = []
        self.reclaimed: List[Dict] = []
        self.reclaim_threshold: float = 0.6

    def register_orphan(self, fragment_id: str, integrity: float,
                        reproducibility: float, truth_score: float,
                        metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        注册孤块碎片
        """
        orphan = {
            "id": fragment_id,
            "integrity": integrity,
            "reproducibility": reproducibility,
            "truth_score": truth_score,
            "combined_score": (integrity + reproducibility + truth_score) / 3.0,
            "metadata": metadata or {},
            "reclaimed": False,
        }
        self.orphan_pool.append(orphan)
        return {
            "registered": True,
            "fragment_id": fragment_id,
            "combined_score": round(orphan["combined_score"], 4),
        }

    def reclaim(self) -> Dict[str, Any]:
        """
        执行孤块回收

        回收条件: combined_score >= reclaim_threshold
        """
        reclaimed_ids = []
        for orphan in self.orphan_pool:
            if not orphan["reclaimed"] and orphan["combined_score"] >= self.reclaim_threshold:
                orphan["reclaimed"] = True
                reclaimed_ids.append(orphan["id"])
                self.reclaimed.append(orphan)

        return {
            "reclaimed_count": len(reclaimed_ids),
            "reclaimed_ids": reclaimed_ids,
            "total_orphans": len(self.orphan_pool),
            "remaining_orphans": sum(1 for o in self.orphan_pool if not o["reclaimed"]),
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "total_orphans": len(self.orphan_pool),
            "reclaimed_count": len(self.reclaimed),
            "remaining_count": sum(1 for o in self.orphan_pool if not o["reclaimed"]),
            "reclaim_threshold": self.reclaim_threshold,
        }


# ═══════════════════════════════════════════════════════════════
# §6 BloomIdolFreezeEngine — 主引擎
# ═══════════════════════════════════════════════════════════════

class BloomIdolFreezeEngine:
    """
    M212 主引擎 — 偶像化伪共识冻结引擎

    整合BloomTable + IdolFreezeDetector + OmegaExtReset +
    ResonanceNucleator + OrphanReclaimer
    """

    def __init__(self, bt_capacity: int = 1024, delta_bt: float = 0.15,
                 e_safe: float = 0.7, e_critical: float = 0.9,
                 sigma_c: float = 0.1):
        self.bt = BloomTable(capacity=bt_capacity, delta_bt=delta_bt)
        self.detector = IdolFreezeDetector(e_safe=e_safe, e_critical=e_critical)
        self.omega_reset = OmegaExtReset(self.bt, self.detector)
        self.nucleator = ResonanceNucleator(self.omega_reset, sigma_c=sigma_c)
        self.reclaimer = OrphanReclaimer()

    def process_cycle(self, domain: str, c_concentrate: float,
                      d_democracy: float, propositions: Optional[List[Dict]] = None,
                      omega_true_ids: Optional[List[str]] = None,
                      orphans: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        执行完整的偶像化检测-冻结-成核-回收周期

        Args:
            domain: 检测域
            c_concentrate: 集中度C
            d_democracy: 民主度D
            propositions: 候选命题列表 [{"id": str, "is_idol": bool}]
            omega_true_ids: Ω_true命题ID列表
            orphans: 孤块列表 [{"id": str, "integrity": float,
                               "reproducibility": float, "truth_score": float}]

        Returns:
            完整周期报告
        """
        # 1. 计算偏心率
        e = self.detector.compute_eccentricity(c_concentrate, d_democracy)

        # 2. 检测冻结
        freeze_check = self.detector.check_eccentricity(e, domain=domain)

        # 3. 注册命题到BT
        bt_results = []
        if propositions:
            for prop in propositions:
                r = self.bt.insert(prop.get("id", ""), is_idol=prop.get("is_idol", False))
                bt_results.append(r)

        # 4. 注册Ω_true
        nucleator_results = []
        if omega_true_ids:
            for oid in omega_true_ids:
                self.nucleator.register_omega_true(oid)
            # 尝试成核
            for oid in omega_true_ids:
                nr = self.nucleator.attempt_nucleation(oid, e)
                nucleator_results.append(nr)

        # 5. 注册和回收孤块
        reclaim_result = {"reclaimed_count": 0}
        if orphans:
            for o in orphans:
                self.reclaimer.register_orphan(
                    o.get("id", ""), o.get("integrity", 0.5),
                    o.get("reproducibility", 0.5), o.get("truth_score", 0.5),
                )
            reclaim_result = self.reclaimer.reclaim()

        # 6. 如果BT假正超阈且IRL关闭，检查是否有外源铁证可救
        auto_reset_result = None
        if not self.detector.irl_open and self.bt.false_positive_rate() > self.bt.delta_bt:
            auto_reset_result = self.omega_reset.submit_evidence(
                "auto_systemic_check", self.bt.false_positive_rate(),
                source="system_auto",
            )

        return {
            "domain": domain,
            "eccentricity": round(e, 4),
            "freeze_status": freeze_check["status"],
            "irl_open": freeze_check["irl_open"],
            "bt_state": self.bt.get_state(),
            "bt_insertions": bt_results,
            "nucleation_results": nucleator_results,
            "reclaim_result": reclaim_result,
            "auto_reset": auto_reset_result,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "bt": self.bt.get_state(),
            "detector": self.detector.get_state(),
            "omega_reset": self.omega_reset.get_state(),
            "nucleator": self.nucleator.get_state(),
            "reclaimer": self.reclaimer.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §7 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t227_idol_freeze_and_reset() -> bool:
    """
    T227: 偶像化冻结定理

    验证:
    1. e→1 → IRL关 → 序列冻结
    2. 外源铁证超δ_BT → Reset BT → IRL重开
    3. 偏心率e↓ → T_life可延
    """
    engine = BloomIdolFreezeEngine(delta_bt=0.15, e_critical=0.9)

    # 正常偏心率 → IRL开放
    check1 = engine.detector.check_eccentricity(0.5, domain="science")
    if check1["status"] != "NORMAL" or not check1["irl_open"]:
        return False

    # 高偏心率 → 冻结
    check2 = engine.detector.check_eccentricity(0.95, domain="science")
    if check2["status"] != "FROZEN" or check2["irl_open"]:
        return False

    # 插入偶像化命题使BT假正率上升
    for i in range(20):
        engine.bt.insert(f"idol_prop_{i}", is_idol=True)

    # 假正率应超过δ_BT
    if engine.bt.false_positive_rate() <= engine.bt.delta_bt:
        return False

    # 外源铁证Reset
    reset = engine.omega_reset.submit_evidence("iron_evidence_1", 0.9)
    if not reset["bt_reset"] or not reset["irl_reopened"]:
        return False

    # Reset后IRL应重开
    if not engine.detector.irl_open:
        return False

    # BT应清空
    if engine.bt.item_count != 0 or len(engine.bt.idol_items) != 0:
        return False

    return True


def _test_t228_resonance_nucleation() -> bool:
    """
    T228: 共振成核定理

    验证:
    1. 非Ω_true命题不触发成核
    2. Ω_true但远离奇点不触发
    3. Ω_true且近奇点 → 触发成核 → 自动提交铁证
    """
    engine = BloomIdolFreezeEngine(delta_bt=0.15, sigma_c=0.1)

    # 注册Ω_true
    engine.nucleator.register_omega_true("truth_1")
    engine.nucleator.register_omega_true("truth_2")

    # 非Ω_true → 不触发
    result1 = engine.nucleator.attempt_nucleation("false_prop", current_e=0.99)
    if result1["nucleation_triggered"]:
        return False

    # Ω_true但远离奇点(e=0.3) → 不触发
    result2 = engine.nucleator.attempt_nucleation("truth_1", current_e=0.3)
    if result2["nucleation_triggered"]:
        return False

    # Ω_true且近奇点(e=0.95) → 触发
    result3 = engine.nucleator.attempt_nucleation("truth_1", current_e=0.95,
                                                   population_weights=[1.0, 0.8])
    if not result3["nucleation_triggered"]:
        return False
    if not result3.get("evidence_submitted"):
        return False

    return True


def _test_orphan_reclaim() -> bool:
    """
    孤块回收测试

    验证: combined_score ≥ threshold的碎片被回收
    """
    reclaimer = OrphanReclaimer()

    # 高分碎片 → 应回收
    reclaimer.register_orphan("good_1", integrity=0.9, reproducibility=0.8,
                               truth_score=0.85)
    # 低分碎片 → 不回收
    reclaimer.register_orphan("bad_1", integrity=0.2, reproducibility=0.1,
                               truth_score=0.3)

    result = reclaimer.reclaim()
    if result["reclaimed_count"] != 1:
        return False
    if "good_1" not in result["reclaimed_ids"]:
        return False
    if "bad_1" in result["reclaimed_ids"]:
        return False

    return True


def run_mve() -> Dict[str, bool]:
    """
    M212 MVE验证

    T227: 偶像化冻结定理
    T228: 共振成核定理
    """
    results = {}

    print("=" * 60)
    print("M212 BloomIdolFreezeEngine — MVE Verification")
    print("=" * 60)

    # T227
    try:
        t227 = _test_t227_idol_freeze_and_reset()
        status = "PASS" if t227 else "FAIL"
        print(f"  T227 (偶像化冻结+Reset): {status}")
        results["T227"] = t227
    except Exception as e:
        print(f"  T227 (偶像化冻结+Reset): ERROR — {e}")
        results["T227"] = False

    # T228
    try:
        t228 = _test_t228_resonance_nucleation()
        status = "PASS" if t228 else "FAIL"
        print(f"  T228 (共振成核): {status}")
        results["T228"] = t228
    except Exception as e:
        print(f"  T228 (共振成核): ERROR — {e}")
        results["T228"] = False

    # OrphanReclaim
    try:
        t_orphan = _test_orphan_reclaim()
        status = "PASS" if t_orphan else "FAIL"
        print(f"  OrphanReclaim (孤块回收): {status}")
        results["OrphanReclaim"] = t_orphan
    except Exception as e:
        print(f"  OrphanReclaim (孤块回收): ERROR — {e}")
        results["OrphanReclaim"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M212 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
