#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System 2 逻辑推演模块 - Neuro-Symbolic Reasoning Engine
基于复合体理学框架，实现慢速、串行、可解释的逻辑推理

核心组件：
1. SymbolicReasoningEngine: 符号推理引擎
2. RuleBase: 规则库（可扩展）
3. InferenceChain: 推理链（可解释）
4. MetaCognitiveMonitor: 元认知监控器
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json


class LogicType(Enum):
    """逻辑类型"""
    PROPOSITIONAL = "propositional"  # 命题逻辑
    FIRST_ORDER = "first_order"        # 一阶逻辑
    FUZZY = "fuzzy"                  # 模糊逻辑
    TEMPORAL = "temporal"            # 时序逻辑
    CAUSAL = "causal"                # 因果逻辑（基于HTCE）


class InferenceRule(Enum):
    """推理规则"""
    MODUS_PONENS = "modus_ponens"          # 肯定前件
    MODUS_TOLLENS = "modus_tollens"        # 否定后件
    HYPOTHETICAL_SYLLOGISM = "hs"         # 假言三段论
    DISJUNCTIVE_SYLLOGISM = "ds"         # 选言三段论
    RESOLUTION = "resolution"              # 归结原理
    INDUCTION = "induction"                # 归纳推理
    ABDUCTION = "abduction"                # 溯因推理
    ANALOGY = "analogy"                    # 类比推理


@dataclass
class Symbol:
    """符号 - 逻辑推理的基本单元"""
    name: str
    symbol_type: str  # 'constant' | 'variable' | 'predicate' | 'function'
    value: Any = None
    metadata: Dict = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name
        return False
    
    def __repr__(self):
        return f"Symbol({self.name}, {self.symbol_type})"


@dataclass
class Formula:
    """公式 - 逻辑表达式"""
    operator: Optional[str]  # None表示原子命题
    operands: List[Any] = field(default_factory=list)  # 子公式或符号
    truth_value: Optional[float] = None  # 真值（三值逻辑：True/False/Nil）
    
    def is_atom(self) -> bool:
        return self.operator is None
    
    def __repr__(self):
        if self.is_atom():
            return str(self.operands[0])
        return f"({self.operator} {', '.join(str(op) for op in self.operands)})"


@dataclass
class InferenceStep:
    """推理步骤 - 可解释的中间步骤"""
    step_id: str
    rule: InferenceRule
    premises: List[Formula]
    conclusion: Formula
    confidence: float  # 置信度 [0, 1]
    explanation: str  # 自然语言解释
    timestamp: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'step_id': self.step_id,
            'rule': self.rule.value,
            'premises': [str(p) for p in self.premises],
            'conclusion': str(self.conclusion),
            'confidence': self.confidence,
            'explanation': self.explanation
        }


class RuleBase:
    """规则库 - 存储和检索推理规则"""
    
    def __init__(self, name: str = "DefaultRuleBase"):
        self.name = name
        self.rules: Dict[InferenceRule, List[Dict]] = {}
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认规则"""
        # 1. 肯定前件：如果 P→Q 且 P，则 Q
        self.rules[InferenceRule.MODUS_PONENS] = [
            {
                'name': 'modus_ponens',
                'match': self._match_modus_ponens,
                'apply': lambda match: match['Q']
            }
        ]
        
        # 2. 否定后件：如果 P→Q 且 ¬Q，则 ¬P
        self.rules[InferenceRule.MODUS_TOLLENS] = [
            {
                'name': 'modus_tollens',
                'match': self._match_modus_tollens,
                'apply': lambda match: match['not_P']
            }
        ]
        
        # 3. 假言三段论：如果 P→Q 且 Q→R，则 P→R
        self.rules[InferenceRule.HYPOTHETICAL_SYLLOGISM] = [
            {
                'name': 'hypothetical_syllogism',
                'match': self._match_hypothetical_syllogism,
                'apply': lambda match: match['P_implies_R']
            }
        ]
        
        # 4. 选言三段论：如果 P∨Q 且 ¬P，则 Q
        self.rules[InferenceRule.DISJUNCTIVE_SYLLOGISM] = [
            {
                'name': 'disjunctive_syllogism',
                'match': self._match_disjunctive_syllogism,
                'apply': lambda match: match['Q']
            }
        ]
        
        # 5. 归结原理（简化）
        self.rules[InferenceRule.RESOLUTION] = [
            {
                'name': 'resolution',
                'match': self._match_resolution,
                'apply': lambda match: match['resolvent']
            }
        ]
        
        # 6. 归纳推理（简化：从特殊到一般）
        self.rules[InferenceRule.INDUCTION] = [
            {
                'name': 'induction',
                'match': self._match_induction,
                'apply': lambda match: match['general']
            }
        ]
        
        # 7. 溯因推理（简化：最佳解释推理）
        self.rules[InferenceRule.ABDUCTION] = [
            {
                'name': 'abduction',
                'match': self._match_abduction,
                'apply': lambda match: match['best_explanation']
            }
        ]
        
        # 8. 类比推理（简化）
        self.rules[InferenceRule.ANALOGY] = [
            {
                'name': 'analogy',
                'match': self._match_analogy,
                'apply': lambda match: match['analogy_conclusion']
            }
        ]
    
    def _match_modus_ponens(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配肯定前件
        
        如果 formulas 包含 (P→Q) 和 P，则返回 {'P': P, 'Q': Q}
        """
        if len(formulas) < 2:
            return None
        
        # 查找蕴含式和原子命题
        implies_formula = None
        atom_formula = None
        
        for f in formulas:
            if f.operator == 'implies' and len(f.operands) == 2:
                implies_formula = f
            elif f.is_atom():
                atom_formula = f
        
        if implies_formula and atom_formula:
            # 检查 atom_formula 是否匹配 P
            # 直接比较 name
            if implies_formula.operands[0].operands[0].name == atom_formula.operands[0].name:
                return {
                    'P': implies_formula.operands[0],
                    'Q': implies_formula.operands[1]
                }
        
        return None
    
    def _match_modus_tollens(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配否定后件
        
        如果 formulas 包含 (P→Q) 和 ¬Q，则返回 {'P': P, 'Q': Q, 'not_Q': ¬Q}
        """
        if len(formulas) < 2:
            return None
        
        implies_formula = None
        not_q_formula = None
        
        for f in formulas:
            if f.operator == 'implies' and len(f.operands) == 2:
                implies_formula = f
            elif f.operator == 'not' and len(f.operands) == 1:
                # 检查是否是 ¬Q
                not_q_formula = f
        
        if implies_formula and not_q_formula:
            # 检查 not_q_formula 是否匹配 ¬Q
            Q = implies_formula.operands[1]
            not_Q = not_q_formula.operands[0]
            
            # 如果 not_Q 与 Q 相同，则匹配
            if self._formula_match(not_Q, Q):
                return {
                    'P': implies_formula.operands[0],
                    'Q': Q,
                    'not_P': Formula(operator='not', operands=[implies_formula.operands[0]])
                }
        
        return None
    
    def _match_hypothetical_syllogism(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配假言三段论
        
        如果 formulas 包含 (P→Q) 和 (Q→R)，则返回 {'P_implies_R': P→R}
        """
        if len(formulas) < 2:
            return None
        
        implies_formulas = [f for f in formulas if f.operator == 'implies' and len(f.operands) == 2]
        
        for i in range(len(implies_formulas)):
            for j in range(len(implies_formulas)):
                if i == j:
                    continue
                
                f1 = implies_formulas[i]
                f2 = implies_formulas[j]
                
                # 检查 f1 的结论是否等于 f2 的前提
                if self._formula_match(f1.operands[1], f2.operands[0]):
                    # 创建 P→R
                    P_implies_R = Formula(
                        operator='implies',
                        operands=[f1.operands[0], f2.operands[1]]
                    )
                    
                    return {
                        'P_implies_R': P_implies_R
                    }
        
        return None
    
    def _match_disjunctive_syllogism(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配选言三段论
        
        如果 formulas 包含 (P∨Q) 和 ¬P，则返回 {'Q': Q}
        """
        if len(formulas) < 2:
            return None
        
        or_formula = None
        not_p_formula = None
        
        for f in formulas:
            if f.operator == 'or' and len(f.operands) == 2:
                or_formula = f
            elif f.operator == 'not' and len(f.operands) == 1:
                not_p_formula = f
        
        if or_formula and not_p_formula:
            # 检查 not_p_formula 是否匹配 ¬P
            P = not_p_formula.operands[0]
            
            # 如果 P 是 or_formula 的第一个操作数，则返回第二个操作数
            if self._formula_match(P, or_formula.operands[0]):
                return {
                    'Q': or_formula.operands[1]
                }
            # 如果 P 是 or_formula 的第二个操作数，则返回第一个操作数
            elif self._formula_match(P, or_formula.operands[1]):
                return {
                    'Q': or_formula.operands[0]
                }
        
        return None
    
    def _match_resolution(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配归结原理（简化）
        
        如果 formulas 包含 (P∨Q) 和 (¬P∨R)，则返回 {'resolvent': Q∨R}
        """
        if len(formulas) < 2:
            return None
        
        or_formulas = [f for f in formulas if f.operator == 'or' and len(f.operands) == 2]
        
        for i in range(len(or_formulas)):
            for j in range(len(or_formulas)):
                if i == j:
                    continue
                
                f1 = or_formulas[i]
                f2 = or_formulas[j]
                
                # 检查 f1 的一个文字是否是 f2 的一个文字的否定
                for op1 in f1.operands:
                    for op2 in f2.operands:
                        # 如果 op1 = ¬op2 或 ¬op1 = op2
                        condition1 = (op1.operator == 'not' and 
                                     self._formula_match(op1.operands[0], op2))
                        condition2 = (op2.operator == 'not' and 
                                     self._formula_match(op2.operands[0], op1))
                        
                        if condition1 or condition2:
                            # 创建归结式
                            other_ops = []
                            for op in f1.operands + f2.operands:
                                if (not self._formula_match(op, op1) and 
                                    not self._formula_match(op, op2)):
                                    other_ops.append(op)
                            
                            if not other_ops:
                                resolvent = Formula(operator=None, operands=[Symbol('contradiction', 'constant')])
                            else:
                                resolvent = Formula(operator='or', operands=other_ops)
                            
                            return {
                                'resolvent': resolvent
                            }
        
        return None
    
    def _match_induction(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配归纳推理（简化：从特殊到一般）
        
        如果 formulas 包含多个特殊实例，则归纳出一般规则
        """
        if len(formulas) < 2:
            return None
        
        # 简化：假设所有公式都是原子命题，归纳出它们的析取
        atoms = [f for f in formulas if f.is_atom()]
        
        if len(atoms) < 2:
            return None
        
        # 创建一般规则（析取）
        general_rule = atoms[0]
        for atom in atoms[1:]:
            general_rule = Formula(operator='or', operands=[general_rule, atom])
        
        return {
            'general': general_rule
        }
    
    def _match_abduction(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配溯因推理（简化：最佳解释推理）
        
        如果 formulas 包含观察 O 和假设 H→O，则推断 H
        """
        if len(formulas) < 2:
            return None
        
        # 简化：随机选择一个新的假设作为最佳解释
        import random
        
        # 创建最佳解释（新假设）
        best_explanation = Formula(
            operator=None,
            operands=[Symbol(f"abduced_{random.randint(1, 1000)}", 'hypothesis')]
        )
        
        return {
            'best_explanation': best_explanation
        }
    
    def _match_analogy(self, formulas: List[Formula]) -> Optional[Dict]:
        """匹配类比推理（简化）
        
        如果 formulas 包含 A 和 B 相似，且 A 有属性 P，则推断 B 也有属性 P
        """
        if len(formulas) < 2:
            return None
        
        # 简化：创建一个类比结论
        analogy_conclusion = Formula(
            operator=None,
            operands=[Symbol('analogy_conclusion', 'constant')]
        )
        
        return {
            'analogy_conclusion': analogy_conclusion
        }
    
    def _formula_match(self, f1: Formula, f2: Formula) -> bool:
        """检查两个公式是否匹配（辅助函数）"""
        if f1.is_atom() and f2.is_atom():
            return f1.operands[0].name == f2.operands[0].name
        if f1.operator == f2.operator and len(f1.operands) == len(f2.operands):
            for op1, op2 in zip(f1.operands, f2.operands):
                if isinstance(op1, Formula) and isinstance(op2, Formula):
                    if not self._formula_match(op1, op2):
                        return False
                elif op1 != op2:
                    return False
            return True
        return False
    
    def query(self, rule_type: InferenceRule, formulas: List[Formula]) -> List[Formula]:
        """查询可应用的规则，返回结论列表"""
        results = []
        
        if rule_type not in self.rules:
            return results
        
        for rule_def in self.rules[rule_type]:
            match = rule_def['match'](formulas)
            if match:
                conclusion = rule_def['apply'](match)
                if conclusion:
                    results.append(conclusion)
        
        return results
    
    def add_rule(self, rule_type: InferenceRule, pattern: List[str], 
                 match_fn: callable, apply_fn: callable):
        """添加自定义规则"""
        if rule_type not in self.rules:
            self.rules[rule_type] = []
        
        self.rules[rule_type].append({
            'pattern': pattern,
            'match': match_fn,
            'apply': apply_fn
        })


class SymbolicReasoningEngine:
    """符号推理引擎 - System 2的核心"""
    
    def __init__(self, name: str = "SymbolicReasoningEngine"):
        self.name = name
        self.rule_base = RuleBase(f"{name}_RuleBase")
        self.knowledge_base: List[Formula] = []
        self.inference_history: List[InferenceStep] = []
        self.max_inference_steps = 100
        
    def add_knowledge(self, formula: Formula):
        """向知识库添加公式"""
        self.knowledge_base.append(formula)
    
    def infer(self, goal: Formula, 
              max_steps: int = None) -> Tuple[Optional[Formula], List[InferenceStep]]:
        """
        推理：从知识库推导目标
        
        参数：
            goal: 目标公式
            max_steps: 最大推理步骤
            
        返回：
            (结论, 推理链)
        """
        max_steps = max_steps or self.max_inference_steps
        steps = []
        
        # 简化实现：前向推理
        current_knowledge = self.knowledge_base.copy()
        
        for step_num in range(max_steps):
            # 尝试应用规则
            new_formulas = []
            
            for rule_type in InferenceRule:
                # 尝试所有规则组合
                for i, f1 in enumerate(current_knowledge):
                    for j, f2 in enumerate(current_knowledge):
                        if i >= j:
                            continue
                        
                        conclusions = self.rule_base.query(rule_type, [f1, f2])
                        
                        for conclusion in conclusions:
                            # 检查是否已存在
                            if not self._formula_exists(conclusion, current_knowledge + new_formulas):
                                # 创建推理步骤
                                step = InferenceStep(
                                    step_id=f"step_{step_num}",
                                    rule=rule_type,
                                    premises=[f1, f2],
                                    conclusion=conclusion,
                                    confidence=0.9,  # 简化：固定置信度
                                    explanation=f"Applied {rule_type.value}: {f1} and {f2} → {conclusion}"
                                )
                                
                                new_formulas.append(conclusion)
                                steps.append(step)
                                
                                # 检查是否达到目标
                                if self._formula_match(conclusion, goal):
                                    return conclusion, steps
            
            if not new_formulas:
                break  # 无法继续推理
            
            current_knowledge.extend(new_formulas)
        
        return None, steps
    
    def _formula_exists(self, formula: Formula, formulas: List[Formula]) -> bool:
        """检查公式是否已存在"""
        for f in formulas:
            if self._formula_match(f, formula):
                return True
        return False
    
    def _formula_match(self, f1: Formula, f2: Formula) -> bool:
        """检查两个公式是否匹配"""
        if f1.is_atom() and f2.is_atom():
            return f1.operands[0].name == f2.operands[0].name
        if f1.operator == f2.operator and len(f1.operands) == len(f2.operands):
            for op1, op2 in zip(f1.operands, f2.operands):
                if isinstance(op1, Formula) and isinstance(op2, Formula):
                    if not self._formula_match(op1, op2):
                        return False
                elif op1 != op2:
                    return False
            return True
        return False
    
    def explain_inference_chain(self, steps: List[InferenceStep]) -> str:
        """解释推理链"""
        if not steps:
            return "No inference steps."
        
        explanation = "推理链：\n"
        for step in steps:
            explanation += f"  {step.step_id}: {step.explanation} (置信度: {step.confidence:.2f})\n"
        
        return explanation


class MetaCognitiveMonitor:
    """元认知监控器 - 监控推理过程"""
    
    def __init__(self, name: str = "MetaCognitiveMonitor"):
        self.name = name
        self.error_history: List[Dict] = []
        self.confidence_threshold = 0.7
        
    def monitor_inference(self, 
                         inference_steps: List[InferenceStep],
                         conclusion: Optional[Formula]) -> Dict:
        """
        监控推理过程
        
        返回：
            monitor_result: 监控结果
                - 'is_valid': 推理是否有效
                - 'errors': 检测到的错误
                - 'suggestions': 改进建议
                - 'confidence': 整体置信度
        """
        errors = []
        suggestions = []
        total_confidence = 0.0
        
        # 检查1：推理步骤是否为空
        if not inference_steps:
            errors.append("推理步骤为空")
            suggestions.append("检查知识库是否包含相关规则")
        
        # 检查2：置信度是否低于阈值
        low_confidence_steps = []
        for step in inference_steps:
            total_confidence += step.confidence
            if step.confidence < self.confidence_threshold:
                low_confidence_steps.append(step.step_id)
        
        if low_confidence_steps:
            errors.append(f"低置信度步骤: {', '.join(low_confidence_steps)}")
            suggestions.append("考虑添加更多知识或规则")
        
        # 检查3：推理链是否过长
        if len(inference_steps) > 50:
            suggestions.append("推理链过长，考虑简化问题")
        
        # 计算整体置信度
        avg_confidence = total_confidence / max(len(inference_steps), 1)
        
        result = {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'confidence': avg_confidence,
            'num_steps': len(inference_steps)
        }
        
        return result
    
    def detect_contradiction(self, 
                            knowledge_base: List[Formula]) -> List[Tuple[Formula, Formula]]:
        """检测知识库中的矛盾"""
        contradictions = []
        
        for i in range(len(knowledge_base)):
            for j in range(i + 1, len(knowledge_base)):
                f1 = knowledge_base[i]
                f2 = knowledge_base[j]
                
                # 简化：检查是否存在 P 和 ¬P
                if (f1.is_atom() and f2.is_atom() and
                    f"¬{f1.operands[0].name}" == f2.operands[0].name):
                    contradictions.append((f1, f2))
        
        return contradictions


class System2Reasoning:
    """System 2 - 逻辑推理系统"""
    
    def __init__(self, name: str = "System2Reasoning"):
        self.name = name
        self.reasoning_engine = SymbolicReasoningEngine(f"{name}_Engine")
        self.monitor = MetaCognitiveMonitor(f"{name}_Monitor")
        
        # 推理统计
        self.stats = {
            'total_inferences': 0,
            'successful_inferences': 0,
            'failed_inferences': 0,
            'avg_confidence': 0.0
        }
    
    def reason(self, 
              premises: List[str], 
              goal: str) -> Dict:
        """
        执行System 2推理
        
        参数：
            premises: 前提（字符串列表）
            goal: 目标（字符串）
            
        返回：
            result: 推理结果
                - 'success': 是否成功
                - 'conclusion': 结论
                - 'inference_chain': 推理链
                - 'explanation': 解释
                - 'monitor_result': 监控结果
        """
        # 1. 解析前提和目标（简化：假设前提和目标是简单的命题）
        premise_formulas = [self._parse_formula(p) for p in premises]
        goal_formula = self._parse_formula(goal)
        
        # 2. 添加到知识库
        for pf in premise_formulas:
            self.reasoning_engine.add_knowledge(pf)
        
        # 3. 执行推理
        conclusion, inference_chain = self.reasoning_engine.infer(goal_formula)
        
        # 4. 监控推理过程
        monitor_result = self.monitor.monitor_inference(
            inference_chain, 
            conclusion
        )
        
        # 5. 更新统计
        self.stats['total_inferences'] += 1
        if conclusion is not None:
            self.stats['successful_inferences'] += 1
        else:
            self.stats['failed_inferences'] += 1
        
        if monitor_result['confidence'] > 0:
            n = self.stats['total_inferences']
            old_avg = self.stats['avg_confidence']
            self.stats['avg_confidence'] = (old_avg * (n - 1) + monitor_result['confidence']) / n
        
        # 6. 构建结果
        result = {
            'success': conclusion is not None,
            'conclusion': str(conclusion) if conclusion else None,
            'inference_chain': [step.to_dict() for step in inference_chain],
            'explanation': self.reasoning_engine.explain_inference_chain(inference_chain),
            'monitor_result': monitor_result
        }
        
        return result
    
    def _parse_formula(self, formula_str: str) -> Formula:
        """解析公式字符串（简化实现）"""
        # 支持多种格式：
        # - "P → Q" (使用箭头符号)
        # - "P implies Q" (使用英文)
        # - "P ∧ Q" (合取)
        # - "P ∨ Q" (析取)
        # - "P" (原子命题)
        
        formula_str = formula_str.strip()
        
        # 检查蕴含（支持 → 和 implies）
        if '→' in formula_str or 'implies' in formula_str.lower():
            # 分割前提
            if '→' in formula_str:
                parts = formula_str.split('→')
            else:
                parts = formula_str.split('implies')
            
            return Formula(
                operator='implies',
                operands=[self._parse_formula(p) for p in parts]
            )
        
        # 检查合取
        elif '∧' in formula_str or 'and' in formula_str.lower():
            if '∧' in formula_str:
                parts = formula_str.split('∧')
            else:
                parts = formula_str.split('and')
            return Formula(
                operator='and',
                operands=[self._parse_formula(p) for p in parts]
            )
        
        # 检查析取
        elif '∨' in formula_str or 'or' in formula_str.lower():
            if '∨' in formula_str:
                parts = formula_str.split('∨')
            else:
                parts = formula_str.split('or')
            return Formula(
                operator='or',
                operands=[self._parse_formula(p) for p in parts]
            )
        
        # 检查否定
        elif formula_str.startswith('¬') or formula_str.lower().startswith('not '):
            if formula_str.startswith('¬'):
                inner = formula_str[1:]
            else:
                inner = formula_str[4:]
            return Formula(
                operator='not',
                operands=[self._parse_formula(inner)]
            )
        
        else:
            # 原子命题
            return Formula(
                operator=None,
                operands=[Symbol(formula_str, 'constant')]
            )
    
    def get_stats(self) -> Dict:
        """获取推理统计"""
        return self.stats.copy()


# ==================== 测试代码 ====================

def test_system2_reasoning():
    """测试System 2推理"""
    print("\n" + "="*60)
    print("测试 System 2 逻辑推演")
    print("="*60)
    
    # 1. 创建System 2
    system2 = System2Reasoning("TestSystem2")
    
    # 2. 定义前提和目标
    premises = [
        "P→Q",
        "P"
    ]
    goal = "Q"
    
    print(f"\n前提: {premises}")
    print(f"目标: {goal}")
    
    # 3. 执行推理
    result = system2.reason(premises, goal)
    
    print(f"\n推理结果:")
    print(f"  成功: {result['success']}")
    print(f"  结论: {result['conclusion']}")
    print(f"  置信度: {result['monitor_result']['confidence']:.2f}")
    print(f"\n推理链:")
    print(result['explanation'])
    
    # 4. 打印监控结果
    print(f"\n监控结果:")
    print(f"  有效: {result['monitor_result']['is_valid']}")
    if result['monitor_result']['errors']:
        print(f"  错误: {result['monitor_result']['errors']}")
    if result['monitor_result']['suggestions']:
        print(f"  建议: {result['monitor_result']['suggestions']}")
    
    # 5. 打印统计
    print(f"\n推理统计:")
    stats = system2.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n✅ System 2 逻辑推演测试完成")


if __name__ == "__main__":
    test_system2_reasoning()
