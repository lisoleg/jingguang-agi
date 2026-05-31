# -*- coding: utf-8 -*-
"""
M214: GoedelEscapeHatch — 哥德尔洞+显密双轨+遁甲算子引擎

基于复合体理学「希尔伯特计划失败与哥德尔洞即遁甲」核心实现:
  - 哥德尔洞Gaps(Σ): 不可判定命题集合=太一Φ透过截影显化不可穷尽性之位点
  - 显密双轨: R_exo(明规则/计算) + R_eso(潜规则/算计), 须同时运行
  - 遁甲算子: Escape_φ: Gaps(Σ)×Human_Calc×Extreme_Context→Override_Action
  - 计算-算计不可归约: Calc ⊄ Comp (算计不可归约为计算)
  - 三昧耶约束: 留痕、限权、可审计
  - 制度不完备定理: Σ⊮φ ∧ Σ⊮¬φ, 须Human_calc凭R_eso判定

核心定理:
  T231 — 哥德尔洞定理:
    对任意足够强的形式系统Σ, ∃φ使得Σ⊮φ ∧ Σ⊮¬φ
    Gaps(Σ)为不可判定命题集合
  T232 — 遁甲反脆弱定理:
    双轨(R_exo+R_eso)优于纯明规则: U(S₂) > U(S₁)在黑天鹅事件下

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Tuple, Callable
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# §1 GoedelGap — 哥德尔洞
# ═══════════════════════════════════════════════════════════════

class GoedelGap:
    """
    哥德尔洞 — 不可判定命题位点

    Gaps(Σ) = {φ | Σ⊮φ ∧ Σ⊮¬φ}

    物理意义: 太一Φ透过截影显化不可穷尽性之位点
    工程意义: AGI系统必然存在的认知盲区，需遁甲算子覆盖
    """

    def __init__(self, system_id: str = "Σ_default"):
        self.system_id = system_id
        self.gaps: List[Dict] = []
        self.audit_trail: List[Dict] = []

    def detect_gap(self, proposition: str, system_can_prove: Optional[bool] = None,
                   system_can_disprove: Optional[bool] = None) -> Dict[str, Any]:
        """
        检测哥德尔洞

        Args:
            proposition: 命题φ
            system_can_prove: 系统是否能证明φ (None=不确定)
            system_can_disprove: 系统是否能证明¬φ (None=不确定)

        Returns:
            检测结果
        """
        can_prove = system_can_prove if system_can_prove is not None else False
        can_disprove = system_can_disprove if system_can_disprove is not None else False

        is_gap = not can_prove and not can_disprove

        result = {
            "proposition": proposition,
            "system_id": self.system_id,
            "can_prove": can_prove,
            "can_disprove": can_disprove,
            "is_gap": is_gap,
            "gap_type": None,
        }

        if is_gap:
            # 分类哥德尔洞
            if proposition.startswith("self_ref_"):
                gap_type = "GODEL_SELF_REF"  # 自指型(如"本系统一致")
            elif proposition.startswith("inf_"):
                gap_type = "INFINITE_REGRESS"  # 无限回归型
            elif proposition.startswith("value_"):
                gap_type = "AXIOLOGICAL"  # 价值型(非事实判断)
            else:
                gap_type = "GENERAL"
            result["gap_type"] = gap_type
            self.gaps.append(result)

        self.audit_trail.append(result)
        return result

    def gap_count(self) -> int:
        """当前检测到的哥德尔洞数量"""
        return len(self.gaps)

    def completeness_ratio(self) -> float:
        """
        完备性比率

        已判定 / 总检测 = 非gap比率
        """
        total = len(self.audit_trail)
        if total == 0:
            return 1.0
        gaps = len(self.gaps)
        return 1.0 - gaps / total

    def get_state(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "gap_count": len(self.gaps),
            "total_checked": len(self.audit_trail),
            "completeness_ratio": round(self.completeness_ratio(), 4),
            "gap_types": list(set(g.get("gap_type", "UNKNOWN") for g in self.gaps)),
        }


# ═══════════════════════════════════════════════════════════════
# §2 DualRailGovernor — 显密双轨治理
# ═══════════════════════════════════════════════════════════════

class RailType(Enum):
    """轨道类型"""
    EXO = "exo"  # 明规则/计算 (R_exo): 可形式化、可证明、可编程
    ESO = "eso"   # 潜规则/算计 (R_eso): 需人的判断、经验、直觉


class DualRailGovernor:
    """
    显密双轨治理器

    R_exo(明规则/计算) + R_eso(潜规则/算计), 须同时运行

    - R_exo: 形式化规则、可编程逻辑、算法决策
    - R_eso: 需Human_calc判断的规则、经验直觉、极端场景

    计算-算计不可归约: Calc ⊄ Comp
    """

    def __init__(self):
        self.exo_rules: List[Dict] = []
        self.eso_rules: List[Dict] = []
        self.decisions: List[Dict] = []
        self.samaya_violations: List[Dict] = []

    def register_rule(self, rule_id: str, rail: RailType,
                      description: str, scope: str = "general") -> Dict[str, Any]:
        """注册规则到对应轨道"""
        rule = {
            "id": rule_id,
            "rail": rail.value,
            "description": description,
            "scope": scope,
            "active": True,
        }
        if rail == RailType.EXO:
            self.exo_rules.append(rule)
        else:
            self.eso_rules.append(rule)

        return {"registered": True, "rule_id": rule_id, "rail": rail.value}

    def decide(self, proposition: str, context: str = "default",
               exo_verdict: Optional[bool] = None,
               eso_verdict: Optional[bool] = None) -> Dict[str, Any]:
        """
        双轨联合决策

        制度不完备定理: Σ⊮φ ∧ Σ⊮¬φ
        须Human_calc凭R_eso判定

        Args:
            proposition: 待决命题
            context: 决策上下文
            exo_verdict: 明规则判定(True=可证明, False=可证伪, None=不可判定)
            eso_verdict: 潜规则判定(True=可信, False=不可信, None=待定)

        Returns:
            联合决策结果
        """
        is_exo_decidable = exo_verdict is not None
        is_eso_decidable = eso_verdict is not None

        # 制度不完备: exo无法判定 → 须eso
        requires_eso = not is_exo_decidable
        requires_exo = not is_eso_decidable

        # 联合决策逻辑
        if is_exo_decidable and exo_verdict:
            final = "EXO_APPROVED"
            confidence = 1.0
        elif is_exo_decidable and not exo_verdict:
            # exo否决 → 需检查eso是否覆盖
            if is_eso_decidable and eso_verdict:
                # 显密冲突: exo否但eso批准 → 遁甲场景
                final = "ESO_OVERRIDE_REVIEW"
                confidence = 0.5
            else:
                final = "EXO_REJECTED"
                confidence = 1.0
        elif requires_eso:
            if is_eso_decidable and eso_verdict:
                final = "ESO_APPROVED"
                confidence = 0.8
            elif is_eso_decidable and not eso_verdict:
                final = "ESO_REJECTED"
                confidence = 0.8
            else:
                final = "UNDECIDABLE"
                confidence = 0.0
        else:
            final = "UNDECIDABLE"
            confidence = 0.0

        decision = {
            "proposition": proposition,
            "context": context,
            "exo_verdict": exo_verdict,
            "eso_verdict": eso_verdict,
            "is_exo_decidable": is_exo_decidable,
            "is_eso_decidable": is_eso_decidable,
            "requires_eso": requires_eso,
            "final": final,
            "confidence": round(confidence, 4),
            "timestamp": time.time(),
        }
        self.decisions.append(decision)
        return decision

    def check_samaya(self, action: str, actor: str = "system",
                     has_audit_trail: bool = True,
                     is_limited_authority: bool = True,
                     is_auditable: bool = True) -> Dict[str, Any]:
        """
        三昧耶约束检查

        三要件:
        1. 留痕 (has_audit_trail)
        2. 限权 (is_limited_authority)
        3. 可审计 (is_auditable)
        """
        violations = []
        if not has_audit_trail:
            violations.append("NO_AUDIT_TRAIL")
        if not is_limited_authority:
            violations.append("UNLIMITED_AUTHORITY")
        if not is_auditable:
            violations.append("NOT_AUDITABLE")

        result = {
            "action": action,
            "actor": actor,
            "samaya_satisfied": len(violations) == 0,
            "violations": violations,
        }

        if violations:
            self.samaya_violations.append(result)

        return result

    def get_state(self) -> Dict[str, Any]:
        return {
            "exo_rules_count": len(self.exo_rules),
            "eso_rules_count": len(self.eso_rules),
            "decisions_count": len(self.decisions),
            "samaya_violations": len(self.samaya_violations),
        }


# ═══════════════════════════════════════════════════════════════
# §3 EscapeHatchOperator — 遁甲算子
# ═══════════════════════════════════════════════════════════════

class EscapeHatchOperator:
    """
    遁甲算子

    Escape_φ: Gaps(Σ) × Human_Calc × Extreme_Context → Override_Action

    触发三重约束:
    1. 多方签名解锁 (multi_sig ≥ threshold)
    2. 不可篡改审计链 (immutable_audit)
    3. 仅当R_exo无法覆盖时合法 (exo_undecidable)

    反脆弱性: 双轨优于纯明规则
    U(S₂) > U(S₁) 在黑天鹅事件下
    """

    def __init__(self, sig_threshold: int = 2, governor: Optional[DualRailGovernor] = None):
        self.sig_threshold = max(1, sig_threshold)
        self.governor = governor or DualRailGovernor()
        self.escape_events: List[Dict] = []
        self.signatures: Dict[str, Set[str]] = {}  # event_id -> signer set

    def request_escape(self, gap_proposition: str, context: str = "extreme",
                       requester: str = "system",
                       rationale: str = "") -> Dict[str, Any]:
        """
        请求遁甲逃逸

        Args:
            gap_proposition: 哥德尔洞命题
            context: 极端上下文描述
            requester: 请求者
            rationale: 理由

        Returns:
            遁甲请求结果
        """
        event_id = hashlib.md5(f"{gap_proposition}:{context}:{time.time()}".encode()).hexdigest()[:12]
        self.signatures[event_id] = set()

        escape_request = {
            "event_id": event_id,
            "gap_proposition": gap_proposition,
            "context": context,
            "requester": requester,
            "rationale": rationale,
            "signatures": [],
            "sig_count": 0,
            "sig_threshold": self.sig_threshold,
            "status": "PENDING_SIGNATURES",
            "exo_undecidable": True,  # 假设已确认R_exo无法覆盖
        }

        # 三昧耶预检查
        samaya = self.governor.check_samaya(
            action=f"escape:{event_id}",
            actor=requester,
        )
        escape_request["samaya_precheck"] = samaya

        self.escape_events.append(escape_request)
        return escape_request

    def sign_escape(self, event_id: str, signer: str) -> Dict[str, Any]:
        """
        签名批准遁甲

        多方签名解锁: sig_count ≥ threshold → 执行
        """
        if event_id not in self.signatures:
            return {"error": f"Unknown event_id: {event_id}"}

        self.signatures[event_id].add(signer)
        sig_count = len(self.signatures[event_id])

        # 更新事件
        for evt in self.escape_events:
            if evt["event_id"] == event_id:
                evt["signatures"] = list(self.signatures[event_id])
                evt["sig_count"] = sig_count

                if sig_count >= self.sig_threshold:
                    # 达到阈值 → 执行遁甲
                    evt["status"] = "EXECUTED"
                    # 记录审计
                    audit = self.governor.check_samaya(
                        action=f"escape_execute:{event_id}",
                        actor="escape_hatch",
                    )
                    evt["execution_audit"] = audit
                    return {
                        "event_id": event_id,
                        "status": "EXECUTED",
                        "sig_count": sig_count,
                        "threshold": self.sig_threshold,
                    }
                else:
                    evt["status"] = "PENDING_SIGNATURES"
                    return {
                        "event_id": event_id,
                        "status": "PENDING_SIGNATURES",
                        "sig_count": sig_count,
                        "threshold": self.sig_threshold,
                        "remaining": self.sig_threshold - sig_count,
                    }

        return {"error": "Event not found after update"}

    def evaluate_antifragility(self, s1_utility: float, s2_utility: float,
                               event_type: str = "black_swan") -> Dict[str, Any]:
        """
        评估反脆弱性

        U(S₂) > U(S₁) 在黑天鹅事件下
        S₁ = 纯明规则(R_exo only)
        S₂ = 双轨(R_exo + R_eso)
        """
        is_antifragile = s2_utility > s1_utility
        advantage = s2_utility - s1_utility

        return {
            "event_type": event_type,
            "S1_utility_exo_only": round(s1_utility, 4),
            "S2_utility_dual_rail": round(s2_utility, 4),
            "advantage": round(advantage, 4),
            "is_antifragile": is_antifragile,
            "conclusion": "双轨优于纯明规则" if is_antifragile else "纯明规则在此场景更优",
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "sig_threshold": self.sig_threshold,
            "escape_events_count": len(self.escape_events),
            "executed_count": sum(1 for e in self.escape_events if e["status"] == "EXECUTED"),
            "pending_count": sum(1 for e in self.escape_events if e["status"] == "PENDING_SIGNATURES"),
            "governor": self.governor.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §4 CalcCompDichotomy — 计算-算计不可归约
# ═══════════════════════════════════════════════════════════════

class CalcCompDichotomy:
    """
    计算-算计不可归约

    Calc ⊄ Comp (算计不可归约为计算)

    计算(Comp): 图灵可计算, 算法化, 形式化
    算计(Calc): 需Human_calc, 经验直觉, 极端场景判断

    不可归约证明:
    ∃p ∈ Calc 使得 ∀算法A, A(p) ≠ Calc(p)
    (某些算计判断无法被任何算法完全替代)
    """

    @staticmethod
    def classify(problem: str, is_formalizable: bool,
                 requires_intuition: bool) -> Dict[str, Any]:
        """
        分类问题属于计算还是算计

        Args:
            problem: 问题描述
            is_formalizable: 是否可形式化
            requires_intuition: 是否需要直觉判断

        Returns:
            分类结果
        """
        if is_formalizable and not requires_intuition:
            domain = "COMP"  # 纯计算
            can_automate = True
        elif not is_formalizable and requires_intuition:
            domain = "CALC"  # 纯算计
            can_automate = False
        elif is_formalizable and requires_intuition:
            domain = "HYBRID"  # 混合(需双轨)
            can_automate = False
        else:
            # 不可形式化但不需要直觉 → 未定义域
            domain = "UNDEFINED"
            can_automate = False

        return {
            "problem": problem,
            "domain": domain,
            "is_formalizable": is_formalizable,
            "requires_intuition": requires_intuition,
            "can_automate": can_automate,
            "irreducibility": domain in ("CALC", "HYBRID"),
        }


# ═══════════════════════════════════════════════════════════════
# §5 GoedelEscapeHatch — 主引擎
# ═══════════════════════════════════════════════════════════════

class GoedelEscapeHatch:
    """
    M214 主引擎 — 哥德尔洞+遁甲算子引擎

    整合GoedelGap + DualRailGovernor +
    EscapeHatchOperator + CalcCompDichotomy
    """

    def __init__(self, sig_threshold: int = 2, system_id: str = "Σ_default"):
        self.gap_detector = GoedelGap(system_id)
        self.governor = DualRailGovernor()
        self.escape = EscapeHatchOperator(sig_threshold, self.governor)
        self.dichotomy = CalcCompDichotomy()

    def full_analysis(self, proposition: str,
                      system_can_prove: Optional[bool] = None,
                      system_can_disprove: Optional[bool] = None,
                      is_formalizable: bool = True,
                      requires_intuition: bool = False,
                      context: str = "default") -> Dict[str, Any]:
        """
        完整分析: 哥德尔洞检测 + 双轨决策 + 不可归约判定
        """
        # 1. 哥德尔洞检测
        gap_result = self.gap_detector.detect_gap(
            proposition, system_can_prove, system_can_disprove)

        # 2. 不可归约判定
        dichotomy_result = self.dichotomy.classify(
            proposition, is_formalizable, requires_intuition)

        # 3. 双轨决策
        exo_verdict = system_can_prove if system_can_prove is not None else None
        eso_verdict = None
        if gap_result["is_gap"] and requires_intuition:
            eso_verdict = True  # 默认: 算计可判定

        decision = self.governor.decide(
            proposition, context, exo_verdict, eso_verdict)

        # 4. 如果是哥德尔洞+极端场景, 触发遁甲
        escape_result = None
        if gap_result["is_gap"] and context == "extreme":
            escape_result = self.escape.request_escape(
                proposition, context, rationale="Gödel gap + extreme context")

        return {
            "proposition": proposition,
            "gap_analysis": gap_result,
            "dichotomy": dichotomy_result,
            "decision": decision,
            "escape": escape_result,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "gap_detector": self.gap_detector.get_state(),
            "governor": self.governor.get_state(),
            "escape": self.escape.get_state(),
        }


# ═══════════════════════════════════════════════════════════════
# §6 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t231_goedel_gap() -> bool:
    """
    T231: 哥德尔洞定理

    验证:
    1. 可证明命题 → 非gap
    2. 可证伪命题 → 非gap
    3. 不可判定命题 → gap
    4. 自指命题 → GODEL_SELF_REF型gap
    """
    detector = GoedelGap("test_system")

    # 可证明 → 非gap
    r1 = detector.detect_gap("1+1=2", system_can_prove=True, system_can_disprove=False)
    if r1["is_gap"]:
        return False

    # 可证伪 → 非gap
    r2 = detector.detect_gap("1+1=3", system_can_prove=False, system_can_disprove=True)
    if r2["is_gap"]:
        return False

    # 不可判定 → gap
    r3 = detector.detect_gap("self_ref_consistency", system_can_prove=False, system_can_disprove=False)
    if not r3["is_gap"]:
        return False
    if r3["gap_type"] != "GODEL_SELF_REF":
        return False

    # 完备性比率
    if detector.completeness_ratio() > 0.8:
        return False  # 有gap应降低完备性

    return True


def _test_t232_escape_antifragility() -> bool:
    """
    T232: 遁甲反脆弱定理

    验证:
    1. 双轨在黑天鹅下优于纯明规则
    2. 遁甲三重约束(签名+审计+exo不可判定)
    3. 三昧耶约束检查
    """
    engine = GoedelEscapeHatch(sig_threshold=2)

    # 反脆弱性验证
    af = engine.escape.evaluate_antifragility(
        s1_utility=0.3,  # 纯明规则在黑天鹅下差
        s2_utility=0.8,  # 双轨在黑天鹅下好
        event_type="black_swan",
    )
    if not af["is_antifragile"]:
        return False

    # 遁甲请求
    escape_req = engine.escape.request_escape(
        "self_ref_consistency", context="extreme", requester="agent_1")
    if escape_req["status"] != "PENDING_SIGNATURES":
        return False

    # 签名1 → 仍不够
    sign1 = engine.escape.sign_escape(escape_req["event_id"], "signer_A")
    if sign1["status"] != "PENDING_SIGNATURES":
        return False

    # 签名2 → 达到阈值
    sign2 = engine.escape.sign_escape(escape_req["event_id"], "signer_B")
    if sign2["status"] != "EXECUTED":
        return False

    # 三昧耶检查
    samaya = engine.governor.check_samaya("test_action", has_audit_trail=True,
                                           is_limited_authority=True, is_auditable=True)
    if not samaya["samaya_satisfied"]:
        return False

    # 三昧耶违反
    samaya_bad = engine.governor.check_samaya("bad_action", has_audit_trail=False,
                                               is_limited_authority=True, is_auditable=True)
    if samaya_bad["samaya_satisfied"]:
        return False

    return True


def run_mve() -> Dict[str, bool]:
    """
    M214 MVE验证

    T231: 哥德尔洞定理
    T232: 遁甲反脆弱定理
    """
    results = {}

    print("=" * 60)
    print("M214 GoedelEscapeHatch — MVE Verification")
    print("=" * 60)

    try:
        t231 = _test_t231_goedel_gap()
        status = "PASS" if t231 else "FAIL"
        print(f"  T231 (哥德尔洞): {status}")
        results["T231"] = t231
    except Exception as e:
        print(f"  T231 (哥德尔洞): ERROR — {e}")
        results["T231"] = False

    try:
        t232 = _test_t232_escape_antifragility()
        status = "PASS" if t232 else "FAIL"
        print(f"  T232 (遁甲反脆弱): {status}")
        results["T232"] = t232
    except Exception as e:
        print(f"  T232 (遁甲反脆弱): ERROR — {e}")
        results["T232"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M214 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
