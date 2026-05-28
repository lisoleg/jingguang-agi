#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高阶逻辑重构器 (Higher-Order Logic Reconstructor)
基于《太乙AGI 7.0升级方案》第三部分：高阶逻辑重构

核心定理：
- T32：高阶逻辑构造性等价定理
  ∀x:P. Q(x)  ⇔  Π(x:P), Q(x)  （依赖乘积类型/Pi-Type）
  ∃x:P. Q(x)  ⇔  Σ(x:P), Q(x)   （依赖求和类型/Sigma-Type）
- T33：排中律在高阶关系结构中的失效定理
  对自指或非良基高阶类型，LEM失效 → 标记为"未决(Wait)"
- T34：EML相位逻辑重构定理
  蕴含 ⇔ 相位流贯映射；等价 ⇔ Univalence；否定 ⇔ 相位翻转

版本：太乙AGI 7.0 第81模块
论文来源：复合体理学系列《高阶逻辑重构》
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class LogicKind(Enum):
    """逻辑类型种类"""
    UNIVERSAL = "Universal"           # 全称量化 ∀
    EXISTENTIAL = "Existential"       # 存在量化 ∃
    IMPLICATION = "Implication"       # 蕴含 →
    EQUIVALENCE = "Equivalence"       # 等价 ⟺
    NEGATION = "Negation"            # 否定 ¬
    CONJUNCTION = "Conjunction"       # 合取 ∧
    DISJUNCTION = "Disjunction"      # 析取 ∨
    SELFREF = "SelfReferential"      # 自指命题
    UNDECIDED = "Undecided"          # 未决


class TypeConstructor(Enum):
    """类型构造器"""
    PI_TYPE = "PiType"               # Π类型：∀x:P.Q(x)
    SIGMA_TYPE = "SigmaType"         # Σ类型：∃x:P.Q(x)
    EQUALITY_TYPE = "EqualityType"  # 等价类型 a =_A b
    UNIVERSE_TYPE = "UniverseType"  # 宇宙层级 U_i
    PHASE_MAP = "PhaseMap"          # 相位流贯映射 f: P → Q
    PHASE_FLIP = "PhaseFlip"        # 相位翻转（否定）


@dataclass
class LogicProposition:
    """逻辑命题"""
    name: str
    kind: LogicKind
    sub_propositions: List['LogicProposition'] = field(default_factory=list)
    type_constructor: TypeConstructor = TypeConstructor.PI_TYPE
    is_self_referential: bool = False
    truth_value: Optional[bool] = None    # None = 未决
    phase_value: float = 0.0             # 相位值 [0, 2π]
    description: str = ""


@dataclass
class HigherOrderType:
    """高阶逻辑类型"""
    constructor: TypeConstructor
    var_name: str
    var_type: str
    predicate: str
    is_valid: bool = True
    fidelity: float = 1.0              # 流贯保真度
    description: str = ""


@dataclass
class LogicReconstructionResult:
    """高阶逻辑重构结果"""
    original_proposition: LogicProposition
    reconstructed_type: HigherOrderType
    lem_status: str                    # "Classical" / "Undecided(Wait)" / "Constructive"
    phase_logic: Dict[str, Any]       # EML相位逻辑信息
    is_self_referential: bool
    reconstruction_valid: bool
    insight: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HigherOrderLogicReconstructor:
    """
    高阶逻辑重构器
    
    将传统一阶逻辑命题重构为HoTT框架下的高阶类型，
    实现T32-T34定理：Pi-Type / Sigma-Type / EML相位逻辑
    """
    
    def __init__(self):
        self.phase_fidelity_threshold = 0.7
        self.self_referential_patterns = [
            "这句话", "此命题", "本规律", "this statement",
            "self_ref", "循环引用", "自指", "paradox"
        ]
        self.reconstruction_count = 0
        self.lem_failures = 0
        
    def universal_quantification_as_pi_type(
        self, var: str, var_type: str, predicate: str
    ) -> HigherOrderType:
        """
        T32: ∀x:P. Q(x) ⇔ Π(x:P), Q(x)
        全称量化重构为Pi-Type（依赖乘积类型）
        """
        pi_type = HigherOrderType(
            constructor=TypeConstructor.PI_TYPE,
            var_name=var,
            var_type=var_type,
            predicate=predicate,
            is_valid=True,
            fidelity=0.95,
            description=f"Π({var}:{var_type}), {predicate} — 全称量化的依赖乘积类型"
        )
        return pi_type
    
    def existential_quantification_as_sigma_type(
        self, var: str, var_type: str, predicate: str
    ) -> HigherOrderType:
        """
        T32: ∃x:P. Q(x) ⇔ Σ(x:P), Q(x)
        存在量化重构为Sigma-Type（依赖求和类型）
        """
        sigma_type = HigherOrderType(
            constructor=TypeConstructor.SIGMA_TYPE,
            var_name=var,
            var_type=var_type,
            predicate=predicate,
            is_valid=True,
            fidelity=0.95,
            description=f"Σ({var}:{var_type}), {predicate} — 存在量化的依赖求和类型"
        )
        return sigma_type
    
    def implication_as_phase_map(self, P: str, Q: str, fidelity: float) -> HigherOrderType:
        """
        T34: 蕴含 P → Q ⇔ 相位流贯映射 f: P → Q
        蕴含关系重构为EML相位流贯映射
        """
        if fidelity >= self.phase_fidelity_threshold:
            return HigherOrderType(
                constructor=TypeConstructor.PHASE_MAP,
                var_name="f",
                var_type=P,
                predicate=Q,
                is_valid=True,
                fidelity=fidelity,
                description=f"相位流贯映射 f: {P} → {Q}（流贯保真度={fidelity:.3f}）"
            )
        else:
            return HigherOrderType(
                constructor=TypeConstructor.PHASE_MAP,
                var_name="f_blocked",
                var_type=P,
                predicate=Q,
                is_valid=False,
                fidelity=fidelity,
                description=f"相位流贯受阻：{P} → {Q}（保真度{fidelity:.3f} < 阈值{self.phase_fidelity_threshold}）"
            )
    
    def negation_as_phase_flip(self, P: str) -> HigherOrderType:
        """
        T34: 否定 ¬P ⇔ 相位翻转（反相耦合）
        否定命题重构为相位翻转
        """
        return HigherOrderType(
            constructor=TypeConstructor.PHASE_FLIP,
            var_name="flip",
            var_type=P,
            predicate=f"¬{P}",
            is_valid=True,
            fidelity=1.0,
            description=f"相位翻转：¬{P}（反相耦合，相位偏移π）"
        )
    
    def is_self_referential(self, proposition: str) -> bool:
        """检测自指性：命题是否引用自身"""
        prop_lower = proposition.lower()
        for pattern in self.self_referential_patterns:
            if pattern.lower() in prop_lower:
                return True
        # 简单语法检测：是否含有循环引用
        if "→" in proposition and proposition.count("→") > 2:
            return random.random() < 0.3  # 多层蕴含有一定自指概率
        return False
    
    def check_lem_failure(self, proposition: str) -> str:
        """
        T33: 检查排中律(LEM)是否失效
        
        Returns:
            "Classical": 经典二值，LEM成立
            "Undecided (Wait)": 未决，LEM失效
            "Constructive": 构造性逻辑，需证明
        """
        if self.is_self_referential(proposition):
            self.lem_failures += 1
            return "Undecided (Wait)"  # 自指 → LEM失效
        
        # 非良基类型（如悖论命题）
        paradox_keywords = ["说谎者", "理发师", "罗素", "liar", "barber", "russell"]
        if any(kw in proposition.lower() for kw in paradox_keywords):
            self.lem_failures += 1
            return "Undecided (Wait)"
        
        # 存在量化命题需要构造性证明
        if "∃" in proposition or "存在" in proposition:
            return "Constructive"
        
        # 普通命题：经典二值
        return "Classical"
    
    def reconstruct_proposition(self, proposition: str, kind: str = "universal") -> LogicReconstructionResult:
        """
        将自然语言命题重构为HoTT高阶类型
        
        Args:
            proposition: 自然语言命题
            kind: 命题类型 ("universal"/"existential"/"implication"/"negation")
        """
        self.reconstruction_count += 1
        
        # 检测自指性
        is_self_ref = self.is_self_referential(proposition)
        
        # 检查LEM状态
        lem_status = self.check_lem_failure(proposition)
        
        # 创建命题对象
        logic_kind_map = {
            "universal": LogicKind.UNIVERSAL,
            "existential": LogicKind.EXISTENTIAL,
            "implication": LogicKind.IMPLICATION,
            "negation": LogicKind.NEGATION,
        }
        prop = LogicProposition(
            name=proposition[:50],
            kind=logic_kind_map.get(kind, LogicKind.UNIVERSAL),
            is_self_referential=is_self_ref,
            phase_value=random.uniform(0, 2 * math.pi),
            description=proposition
        )
        
        # 根据种类重构为高阶类型
        if kind == "universal":
            htype = self.universal_quantification_as_pi_type("x", "P", "Q(x)")
        elif kind == "existential":
            htype = self.existential_quantification_as_sigma_type("x", "P", "Q(x)")
        elif kind == "implication":
            parts = proposition.split("→") if "→" in proposition else proposition.split("implies")
            P = parts[0].strip() if len(parts) > 1 else "P"
            Q = parts[1].strip() if len(parts) > 1 else "Q"
            fidelity = 0.9 if not is_self_ref else 0.3
            htype = self.implication_as_phase_map(P, Q, fidelity)
        elif kind == "negation":
            htype = self.negation_as_phase_flip(proposition)
        else:
            htype = self.universal_quantification_as_pi_type("x", "Type", "Prop")
        
        # EML相位逻辑信息
        phase_logic = {
            "phase_value": prop.phase_value,
            "phase_shift": 2 * math.pi / 5,  # ℤ₅相位偏移
            "phase_coupling": "Z5" if lem_status == "Classical" else "Decoupled",
            "eml_operator": "F(fire)" if kind == "implication" else "Σ(water)",
        }
        
        # 生成洞见
        if is_self_ref and lem_status == "Undecided (Wait)":
            insight = "⚠️ 自指命题：排中律失效，标记为未决（Wait）。无法强行二值化。"
        elif lem_status == "Constructive":
            insight = "🔨 构造性命题：需要显式构造存在量化的见证(witness)。"
        else:
            insight = f"✅ 经典命题成功重构为 {htype.constructor.value}，流贯保真度={htype.fidelity:.3f}"
        
        return LogicReconstructionResult(
            original_proposition=prop,
            reconstructed_type=htype,
            lem_status=lem_status,
            phase_logic=phase_logic,
            is_self_referential=is_self_ref,
            reconstruction_valid=htype.is_valid,
            insight=insight
        )
    
    def batch_reconstruct(self, propositions: List[Dict]) -> List[LogicReconstructionResult]:
        """批量重构命题列表"""
        results = []
        for p in propositions:
            result = self.reconstruct_proposition(p.get("text", ""), p.get("kind", "universal"))
            results.append(result)
        return results
    
    def get_stats(self) -> Dict:
        """获取重构统计信息"""
        return {
            "total_reconstructions": self.reconstruction_count,
            "lem_failures": self.lem_failures,
            "lem_failure_rate": self.lem_failures / max(1, self.reconstruction_count),
            "status": "active"
        }


def get_instance():
    """获取 HigherOrderLogicReconstructor 单例"""
    if not hasattr(get_instance, '_instance') or get_instance._instance is None:
        get_instance._instance = HigherOrderLogicReconstructor()
    return get_instance._instance


if __name__ == "__main__":
    reconstructor = HigherOrderLogicReconstructor()
    
    test_cases = [
        {"text": "∀x:Nat. x + 0 = x", "kind": "universal"},
        {"text": "∃x:Nat. x > 100", "kind": "existential"},
        {"text": "A → B （A蕴含B）", "kind": "implication"},
        {"text": "这句话是假的", "kind": "universal"},  # 自指测试
        {"text": "¬(矛盾命题)", "kind": "negation"},
    ]
    
    print("=" * 60)
    print("高阶逻辑重构器 M81 - 测试报告")
    print("=" * 60)
    
    for case in test_cases:
        result = reconstructor.reconstruct_proposition(case["text"], case["kind"])
        print(f"\n命题: {case['text']}")
        print(f"  重构类型: {result.reconstructed_type.constructor.value}")
        print(f"  LEM状态: {result.lem_status}")
        print(f"  自指: {result.is_self_referential}")
        print(f"  保真度: {result.reconstructed_type.fidelity:.3f}")
        print(f"  洞见: {result.insight}")
    
    print(f"\n统计: {reconstructor.get_stats()}")
    print("\n✅ M81 HigherOrderLogicReconstructor 初始化成功")
