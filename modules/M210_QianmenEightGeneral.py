# -*- coding: utf-8 -*-
"""
M210: QianmenEightGeneral — 千门八将+ΔS策略偏离审查引擎

基于复合体理学「新诸子百家+千门八将TY重释」核心实现:
  - 八将EML RuleID偏离: 正/提/反/脱/病/死/惊/开
  - ΔS量化: ΔS = S_Rel(θ_deviate) - S_Rel(θ_*) > 0
  - 审查制: 强制公开S_Rel估算+latent/selected标注+ΔS
  - 一元数拣选公理: 保"1"不破缺, 拣选ArgMin S_Rel且具自指单位元的解
  - 显隐互转定理 (Thm4.4): 环境/Phase变化→ArgMin切换→latent升显化

核心定理:
  一元数拣选公理: 刘机制拣选=保"1"不破缺, ArgMin S_Rel且具自指单位元
  Thm4.4 — 显隐互转定理:
    环境/Phase变化 → RG-flow粗粒化微变 → ArgMin切换

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# §1 千门八将 EML RuleID
# ═══════════════════════════════════════════════════════════════

class GeneralType(Enum):
    """千门八将类型"""
    ZHENG = "zheng"      # 正将: 建ρ>ρ_c使对象入局
    TI = "ti"            # 提将: 锁对象已投入不可逆
    FAN = "fan"           # 反将: 引对象离原路径
    TUO = "tuo"           # 脱将: 布局者自保
    BING = "bing"         # 病将: 长时腐化对象Φ_const
    SI = "si"             # 死将: 终结关系/击溃
    JING = "jing"         # 惊将: 破执/促重估
    KAI = "kai"           # 开将: 披露隐藏ΔS/真θ_*


@dataclass
class EightGeneralRule:
    """
    千门八将规则

    本质: L4主体故意选择非ArgMin的θ(即θ_deviate≠θ_*),
    引入ΔS进行策略性操控

    ΔS = S_Rel(θ_deviate) - S_Rel(θ_*) > 0
    """
    general_type: GeneralType
    rule_id: str           # EML RuleID偏离类型
    purpose: str           # 操控目的
    delta_s_level: str    # ΔS水平: zero/micro/small/medium/large
    is_reversible: bool    # 是否可逆
    description: str = ""

    def compute_delta_s(self, s_deviate: float, s_optimal: float) -> float:
        """
        计算ΔS = S_Rel(θ_deviate) - S_Rel(θ_*)

        Returns:
            ΔS > 0 (偏离总是增加S_Rel)
        """
        return s_deviate - s_optimal


# 八将规则预定义
EIGHT_GENERALS: Dict[GeneralType, EightGeneralRule] = {
    GeneralType.ZHENG: EightGeneralRule(
        general_type=GeneralType.ZHENG,
        rule_id="theta_consensus_build",
        purpose="建ρ_Rel>ρ_c使对象入局(加边↑ρ/Hebbian↑w/叙事认同)",
        delta_s_level="zero",
        is_reversible=True,
        description="初ΔS≈0(建信不偏), 加边增密度使对象进入关系网络"
    ),
    GeneralType.TI: EightGeneralRule(
        general_type=GeneralType.TI,
        rule_id="theta_commit_point",
        purpose="锁对象已投入不可逆(限时决策压力/锚定效应)",
        delta_s_level="micro",
        is_reversible=False,
        description="微ΔS↑(锚定偏), 使对象产生沉没成本"
    ),
    GeneralType.FAN: EightGeneralRule(
        general_type=GeneralType.FAN,
        rule_id="theta_cast_doubt",
        purpose="引对象离原路径(微降w_e某边/引入备选矛盾)",
        delta_s_level="small",
        is_reversible=True,
        description="ΔS中小↑, 在对象关系网络中制造怀疑"
    ),
    GeneralType.TUO: EightGeneralRule(
        general_type=GeneralType.TUO,
        rule_id="theta_exit_path",
        purpose="布局者自保(保Φ_inj不全断/暗留backdoor边)",
        delta_s_level="medium",
        is_reversible=True,
        description="ΔS对对象↑但布局者限损, 保留退路"
    ),
    GeneralType.BING: EightGeneralRule(
        general_type=GeneralType.BING,
        rule_id="theta_slow_poison",
        purpose="长时腐化对象Φ_const(持续微偏θ→S_Rel渐增)",
        delta_s_level="medium",
        is_reversible=False,
        description="ΔS累积↑(隐蔽危险), 象温水煮蛙"
    ),
    GeneralType.SI: EightGeneralRule(
        general_type=GeneralType.SI,
        rule_id="theta_cut_Ftel",
        purpose="终结关系/击溃(删边E/停Φ_inj)",
        delta_s_level="large",
        is_reversible=False,
        description="ΔS→大(对象衰), 切断流贯输入"
    ),
    GeneralType.JING: EightGeneralRule(
        general_type=GeneralType.JING,
        rule_id="theta_shock_reframe",
        purpose="破执/促重估(瞬间给反例¬T_i→迫CRD重启)",
        delta_s_level="large",
        is_reversible=True,
        description="瞬ΔS↑(重算)后可能回ArgMin, 打破旧框架"
    ),
    GeneralType.KAI: EightGeneralRule(
        general_type=GeneralType.KAI,
        rule_id="theta_reveal_timing",
        purpose="结束布局透明收网(披露隐藏ΔS/真θ_*)",
        delta_s_level="medium",
        is_reversible=True,
        description="ΔS显化(对象知偏程度), 策略透明化"
    ),
}


# ═══════════════════════════════════════════════════════════════
# §2 S_Rel 估算与审查
# ═══════════════════════════════════════════════════════════════

@dataclass
class SRelEstimate:
    """
    S_Rel估算

    S_Rel(T_i) = α·M + β·H[Θ] + γ·Penalty

    - M = 参与金灵球数(关系复杂度)
    - H[Θ] = 相位混乱度(信息熵)
    - Penalty = 非自指惩罚(破缺"1"的代价)
    """
    m_count: int = 0           # M: 参与金灵球数
    phase_entropy: float = 0.0  # H[Θ]: 相位混乱度
    penalty: float = 0.0        # γ·Penalty
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 2.0          # 非自指惩罚权重更高

    def compute(self) -> float:
        """计算S_Rel = α·M + β·H[Θ] + γ·Penalty"""
        return self.alpha * self.m_count + self.beta * self.phase_entropy + self.gamma * self.penalty

    def to_dict(self) -> Dict[str, Any]:
        return {
            "M": self.m_count,
            "H_theta": round(self.phase_entropy, 4),
            "penalty": round(self.penalty, 4),
            "S_Rel": round(self.compute(), 4),
        }


@dataclass
class ManifestationStatus:
    """显化状态: selected(显化主轴) / latent(潜化保留)"""
    is_selected: bool = False
    is_latent: bool = True
    s_rel: float = float('inf')
    has_self_reference_unit: bool = False  # 是否具自指单位元(一元数拣选)
    delta_s: float = 0.0  # ΔS偏离度


# ═══════════════════════════════════════════════════════════════
# §3 千门八将审查引擎
# ═══════════════════════════════════════════════════════════════

class QianmenCensorEngine:
    """
    千门八将审查引擎 — M210主类

    审查制核心:
      任何提案须公开:
        (a) Rel草图(V节点, E_pot潜在边, 初估ρ₀, w₀, θ₀, Φ_est)
        (b) S_Rel估算
        (c) latent/selected标注
        (d) 若含千门手法, 明示ΔS估算

    审查结论:
        接收(latent归档) / 推荐显化主轴(需复验) / 退回(缺S_Rel/不可证伪/隐匿ΔS)
    """

    def __init__(self):
        self.proposals: List[Dict] = []
        self.censor_log: List[Dict] = []
        self.manifestation_map: Dict[str, ManifestationStatus] = {}

    def submit_proposal(self, proposal_id: str, s_rel_est: SRelEstimate,
                        has_self_ref: bool = True,
                        general_used: Optional[GeneralType] = None,
                        delta_s_explicit: Optional[float] = None) -> Dict[str, Any]:
        """
        提交审查提案

        Args:
            proposal_id: 提案标识
            s_rel_est: S_Rel估算
            has_self_ref: 是否具自指单位元
            general_used: 是否使用了千门手法(如有, 需明示ΔS)
            delta_s_explicit: ΔS显式估算(如果用了千门手法必须提供)
        """
        s_rel = s_rel_est.compute()

        # 一元数拣选公理: 保"1"不破缺
        # 刘机制拣选 = ArgMin S_Rel且具自指单位元
        # 与已有selected比较: 只有比当前最优S_Rel更低才能SELECTED
        current_min_selected = float('inf')
        for pid, st in self.manifestation_map.items():
            if st.is_selected:
                current_min_selected = min(current_min_selected, st.s_rel)

        is_argmin_candidate = (has_self_ref and s_rel_est.penalty == 0
                                and s_rel < current_min_selected)

        # 检查千门手法
        general_info = None
        if general_used is not None:
            rule = EIGHT_GENERALS[general_used]
            if delta_s_explicit is None:
                # 未明示ΔS → 退回!
                result = {
                    "proposal_id": proposal_id,
                    "verdict": "REJECTED",
                    "reason": "千门手法未明示ΔS(审查制要求d)",
                    "s_rel": round(s_rel, 4),
                    "has_self_ref": has_self_ref,
                }
                self.censor_log.append(result)
                return result
            general_info = {
                "general": general_used.value,
                "rule_id": rule.rule_id,
                "delta_s": delta_s_explicit,
                "purpose": rule.purpose,
            }

        # S_Rel估算检查
        if s_rel == float('inf'):
            result = {
                "proposal_id": proposal_id,
                "verdict": "REJECTED",
                "reason": "缺S_Rel估算(审查制要求b)",
                "s_rel": round(s_rel, 4),
                "has_self_ref": has_self_ref,
            }
            self.censor_log.append(result)
            return result

        # 一元数拣选: 无自指单位元 → 非ArgMin候选
        if not has_self_ref:
            status = ManifestationStatus(
                is_selected=False, is_latent=True,
                s_rel=s_rel, has_self_reference_unit=False,
                delta_s=0.0,
            )
            self.manifestation_map[proposal_id] = status
            result = {
                "proposal_id": proposal_id,
                "verdict": "LATENT",
                "reason": "无自指单位元(一元数拣选不通过), 归latent",
                "s_rel": round(s_rel, 4),
                "has_self_ref": False,
                "general": general_info,
                "manifestation": "latent",
            }
        elif is_argmin_candidate:
            status = ManifestationStatus(
                is_selected=True, is_latent=False,
                s_rel=s_rel, has_self_reference_unit=True,
                delta_s=delta_s_explicit or 0.0,
            )
            self.manifestation_map[proposal_id] = status
            result = {
                "proposal_id": proposal_id,
                "verdict": "SELECTED",
                "reason": "ArgMin S_Rel且具自指单位元(一元数拣选通过)",
                "s_rel": round(s_rel, 4),
                "has_self_ref": True,
                "general": general_info,
                "manifestation": "selected",
            }
        else:
            status = ManifestationStatus(
                is_selected=False, is_latent=True,
                s_rel=s_rel, has_self_reference_unit=True,
                delta_s=delta_s_explicit or 0.0,
            )
            self.manifestation_map[proposal_id] = status
            result = {
                "proposal_id": proposal_id,
                "verdict": "LATENT",
                "reason": "S_Rel非ArgMin(含Penalty), 归latent待议",
                "s_rel": round(s_rel, 4),
                "has_self_ref": True,
                "general": general_info,
                "manifestation": "latent",
            }

        self.censor_log.append(result)
        return result

    def manifest_latent_exchange(self, environment_change: str = "default") -> Dict[str, Any]:
        """
        显隐互转 (Thm4.4)

        环境/Phase变化 → RG-flow粗粒化微变 → ArgMin切换 → latent升显化

        条件:
          1. 环境/Phase发生改变
          2. S_Rel因环境变化导致RG-flow微变
          3. 原latent的Rel_j的S_Rel相对降最多
          4. 经L4集体CRD迭代

        结论:
          ArgMin S_Rel简并分支可能切换 → latent升显化
        """
        # 找到当前所有latent提案
        latent = {pid: s for pid, s in self.manifestation_map.items()
                  if s.is_latent}

        # 找到当前selected
        selected = {pid: s for pid, s in self.manifestation_map.items()
                    if s.is_selected}

        if not latent:
            return {"exchanged": False, "reason": "No latent proposals"}

        # 环境变化后重新评估: 找latent中S_Rel最小的
        best_latent_id = min(latent.keys(), key=lambda pid: latent[pid].s_rel)
        best_latent = latent[best_latent_id]

        # 如果latent中最优有自指单位元且S_Rel比当前selected更优
        exchange_occurred = False
        if best_latent.has_self_reference_unit:
            for sel_id, sel_status in selected.items():
                if best_latent.s_rel < sel_status.s_rel:
                    # 显隐互转!
                    sel_status.is_selected = False
                    sel_status.is_latent = True
                    best_latent.is_selected = True
                    best_latent.is_latent = False
                    exchange_occurred = True
                    break

        return {
            "exchanged": exchange_occurred,
            "environment_change": environment_change,
            "new_selected": best_latent_id if exchange_occurred else None,
            "latent_count": len([s for s in self.manifestation_map.values() if s.is_latent]),
            "selected_count": len([s for s in self.manifestation_map.values() if s.is_selected]),
        }

    def apply_general(self, general_type: GeneralType,
                      s_deviate: float, s_optimal: float) -> Dict[str, Any]:
        """
        应用千门八将手法

        Args:
            general_type: 八将类型
            s_deviate: 偏离后的S_Rel
            s_optimal: ArgMin最优S_Rel

        Returns:
            应用结果(含ΔS量化)
        """
        rule = EIGHT_GENERALS[general_type]
        delta_s = rule.compute_delta_s(s_deviate, s_optimal)

        return {
            "general": general_type.value,
            "rule_id": rule.rule_id,
            "purpose": rule.purpose,
            "delta_s": round(delta_s, 4),
            "delta_s_level": rule.delta_s_level,
            "is_reversible": rule.is_reversible,
            "s_deviate": round(s_deviate, 4),
            "s_optimal": round(s_optimal, 4),
            "is_strategic_deviation": delta_s > 0,
        }

    def get_state(self) -> Dict[str, Any]:
        """返回引擎状态"""
        return {
            "proposals_count": len(self.censor_log),
            "manifestation_map": {
                pid: {
                    "selected": s.is_selected,
                    "latent": s.is_latent,
                    "s_rel": round(s.s_rel, 4),
                    "has_self_ref": s.has_self_reference_unit,
                    "delta_s": round(s.delta_s, 4),
                }
                for pid, s in self.manifestation_map.items()
            },
        }


# ═══════════════════════════════════════════════════════════════
# §4 MVE验证
# ═══════════════════════════════════════════════════════════════

def _test_t215_unitary_selection() -> bool:
    """
    T215: 一元数拣选公理

    验证: ΔS>0→策略偏离; ΔS=0→ArgMin
    刘机制拣选 = 保"1"不破缺, ArgMin S_Rel且具自指单位元
    """
    engine = QianmenCensorEngine()

    # 提案A: 具自指单位元, S_Rel低 → 应SELECTED
    est_a = SRelEstimate(m_count=5, phase_entropy=0.3, penalty=0.0)
    result_a = engine.submit_proposal("theory_A", est_a, has_self_ref=True)

    # 提案B: 具自指单位元, S_Rel高 → 应LATENT
    est_b = SRelEstimate(m_count=8, phase_entropy=0.6, penalty=0.0)
    result_b = engine.submit_proposal("theory_B", est_b, has_self_ref=True)

    # 提案C: 无自指单位元 → 应LATENT(一元数拣选不通过)
    est_c = SRelEstimate(m_count=3, phase_entropy=0.2, penalty=0.0)
    result_c = engine.submit_proposal("theory_C", est_c, has_self_ref=False)

    # 验证A被选中
    if result_a["verdict"] != "SELECTED":
        return False
    # 验证B为latent
    if result_b["verdict"] != "LATENT":
        return False
    # 验证C为latent(无自指单位元)
    if result_c["verdict"] != "LATENT":
        return False

    # 千门手法测试: 使用正将但未明示ΔS → REJECTED
    est_d = SRelEstimate(m_count=5, phase_entropy=0.3, penalty=0.1)
    result_d = engine.submit_proposal("theory_D", est_d, has_self_ref=True,
                                       general_used=GeneralType.ZHENG,
                                       delta_s_explicit=None)
    if result_d["verdict"] != "REJECTED":
        return False

    # 千门手法测试: 使用正将且明示ΔS → 通过审查
    result_e = engine.submit_proposal("theory_E", est_d, has_self_ref=True,
                                       general_used=GeneralType.ZHENG,
                                       delta_s_explicit=0.0)
    # 应至少不是REJECTED(可能LATENT)
    if result_e["verdict"] == "REJECTED":
        return False

    # ΔS计算测试
    delta = EIGHT_GENERALS[GeneralType.SI].compute_delta_s(10.0, 5.0)
    if delta != 5.0:
        return False

    return True


def _test_t216_manifest_latent_exchange() -> bool:
    """
    T216: 显隐互转定理 (Thm4.4)

    验证: 环境变化→ArgMin切换→latent升显化
    """
    engine = QianmenCensorEngine()

    # 提案A: S_Rel=5.0, 具自指 → selected
    est_a = SRelEstimate(m_count=3, phase_entropy=0.5, penalty=0.0)
    result_a = engine.submit_proposal("theory_A", est_a, has_self_ref=True)

    # 提案B: S_Rel=8.0, 具自指 → latent
    est_b = SRelEstimate(m_count=5, phase_entropy=1.0, penalty=0.0)
    result_b = engine.submit_proposal("theory_B", est_b, has_self_ref=True)

    # 验证初始状态
    if result_a["verdict"] != "SELECTED":
        return False
    if result_b["verdict"] != "LATENT":
        return False

    # 环境变化: 降低B的S_Rel(模拟新数据使B更优)
    engine.manifestation_map["theory_B"].s_rel = 3.0  # B现在比A更优

    # 执行显隐互转
    exchange = engine.manifest_latent_exchange("new_evidence")

    # 应发生交换
    if not exchange["exchanged"]:
        return False
    if exchange["new_selected"] != "theory_B":
        return False

    # 验证B现在是selected, A变成latent
    if not engine.manifestation_map["theory_B"].is_selected:
        return False
    if not engine.manifestation_map["theory_A"].is_latent:
        return False

    return True


def run_mve() -> Dict[str, bool]:
    """
    M210 MVE验证

    T215: 一元数拣选公理
    T216: 显隐互转定理(Thm4.4)
    """
    results = {}

    print("=" * 60)
    print("M210 QianmenEightGeneral — MVE Verification")
    print("=" * 60)

    # T215
    try:
        t215 = _test_t215_unitary_selection()
        status = "PASS" if t215 else "FAIL"
        print(f"  T215 (一元数拣选): {status}")
        results["T215"] = t215
    except Exception as e:
        print(f"  T215 (一元数拣选): ERROR — {e}")
        results["T215"] = False

    # T216
    try:
        t216 = _test_t216_manifest_latent_exchange()
        status = "PASS" if t216 else "FAIL"
        print(f"  T216 (显隐互转): {status}")
        results["T216"] = t216
    except Exception as e:
        print(f"  T216 (显隐互转): ERROR — {e}")
        results["T216"] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"M210 MVE: {passed}/{len(results)} PASSED")
    print(f"{'=' * 60}")

    return results


if __name__ == "__main__":
    run_mve()
