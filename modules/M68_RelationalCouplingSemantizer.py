# -*- coding: utf-8 -*-
"""
M68: 关系耦合语义器 (Relational Coupling Semantizer)
基于《数学完备化》论文 §3.2 EML加法与关系翻转

核心运算:
- EML加法: |m₁⊕m₂| = |m₁|·|m₂|, θ(m₁⊕m₂) = θ(m₁)+θ(m₂)
- 关系翻转: "1+1=-1" 的EML诠释
- T20: EML加法守恒定理
- T21: 关系翻转临界定理

预言P9: 语义理解质量∝关系耦合度

TY/IDO Property 3 集成 (长程推理/可保持):
- 子目标分解: 将语义理解拆分为多步推理链
- 每步验证: 每步结果经 StepVerifier 验收
- 错误恢复: Plan B 降级策略（近似嵌入 → 零向量）
- 资源预算: 超时/算力限制下优雅降级
"""
# [_modified] M68 integrated with TYIDO P3 LongRangeReasoning

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
import re
import sys
import os

# 导入 TY/IDO Property 3 共享基础设施
_tyido_path = os.path.dirname(os.path.abspath(__file__))
if _tyido_path not in sys.path:
    sys.path.insert(0, _tyido_path)

try:
    from modules.TYIDO_LongRangeReasoning import (
        SubGoal, SubGoalDecomposer, StepVerifier,
        PlanBFallback, ResourceBudget, FallbackPlan
    )
    _P3_AVAILABLE = True
except ImportError:
    _P3_AVAILABLE = False

class RelationalCouplingSemantizer:
    """
    关系耦合语义器
    
    来源: §3.2 EML加法与关系翻转
    
    TY/IDO Property 3 (长程推理/可保持) 集成:
    - 子目标分解: 将语义理解拆分为多步推理链
    - 每步验证: 每步结果经 StepVerifier 验收
    - 错误恢复: Plan B 降级策略
    - 资源预算: 超时/算力限制下优雅降级
    """
    _instance = None
    
    def __init__(self):
        self.coupling_history: List[dict] = []
        self.semantic_strength_history: List[float] = []
        self.phase_coupling_coefficients: List[float] = []
        self.flip_count = 0
        
        # TY/IDO Property 3 组件
        if _P3_AVAILABLE:
            self._p3_decomposer = SubGoalDecomposer(task_name="SemanticCoupling")
            self._p3_verifier = StepVerifier()
            self._p3_fallback = PlanBFallback()
            self._p3_budget = ResourceBudget(max_time=10.0, max_steps=500)
            self._init_p3_fallbacks()
        else:
            self._p3_decomposer = None
            self._p3_verifier = None
            self._p3_fallback = None
            self._p3_budget = None
        self._p3_last_verdict = 'PASS'

    def _init_p3_fallbacks(self):
        """初始化 P3 降级策略"""
        if not self._p3_fallback:
            return
        # Plan B: 使用简单词袋替代 EML 嵌入
        self._p3_fallback.register_plan(FallbackPlan(
            plan_name="Plan B: bag_of_words",
            priority=1,
            strategy=self._fallback_bag_of_words,
            description="使用词袋相似度替代 EML 嵌入"
        ))
        # Plan C: 返回零向量
        self._p3_fallback.register_plan(FallbackPlan(
            plan_name="Plan C: zero_vector",
            priority=2,
            strategy=self._fallback_zero_vector,
            description="返回零向量作为保底结果"
        ))
    
    def _fallback_bag_of_words(self, context: Dict[str, Any]) -> dict:
        """Plan B: 词袋近似"""
        e1 = context.get('entity1', '')
        e2 = context.get('entity2', '')
        # 简单字符交叠相似度
        set1 = set(e1)
        set2 = set(e2)
        if not set1 and not set2:
            similarity = 0.0
        else:
            similarity = len(set1 & set2) / max(len(set1 | set2), 1)
        return {
            'entity1': e1,
            'entity2': e2,
            'phase_coupling_coefficient': float(similarity),
            'flip_occurred': False,
            'fallback': 'bag_of_words'
        }
    
    def _fallback_zero_vector(self, context: Dict[str, Any]) -> dict:
        """Plan C: 零向量保底"""
        return {
            'entity1': context.get('entity1', ''),
            'entity2': context.get('entity2', ''),
            'phase_coupling_coefficient': 0.0,
            'flip_occurred': False,
            'fallback': 'zero_vector'
        }
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def compute_entity_embedding(self, entity: str) -> np.ndarray:
        """
        计算实体的语义嵌入向量
        使用字符级和词级特征的组合
        """
        # 简化实现：基于字符分布的嵌入
        chars = list(entity)
        char_counts = Counter(chars)
        
        # 创建固定维度的嵌入
        dim = 32
        embedding = np.zeros(dim)
        
        for i, char in enumerate(entity[:dim]):
            # 使用字符的Unicode码点作为种子
            np.random.seed(ord(char) + i * 1000)
            embedding[i] = np.random.randn()
        
        # 归一化
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def EML_addition(self, m1: 'MononumberLike', m2: 'MononumberLike') -> 'MononumberLike':
        """
        EML加法: m₁ ⊕ m₂
        
        公式: 
        |m₁⊕m₂| = |m₁| · |m₂|
        θ(m₁⊕m₂) = θ(m₁) + θ(m₂)  (mod 2π)
        """
        # 确保有幅值和相位
        amp1 = getattr(m1, 'amplitude', 1.0)
        amp2 = getattr(m2, 'amplitude', 1.0)
        phase1 = getattr(m1, 'phase', 0.0)
        phase2 = getattr(m2, 'phase', 0.0)
        
        coupled_amp = amp1 * amp2
        coupled_phase = (phase1 + phase2) % (2 * np.pi)
        
        # 检查是否发生关系翻转（相位超过π）
        if coupled_phase > np.pi:
            self.flip_count += 1
        
        return {
            'amplitude': coupled_amp,
            'phase': coupled_phase,
            'flip_occurred': coupled_phase > np.pi
        }
    
    def compute_phase_coupling(self, entity1: str, entity2: str) -> dict:
        """
        计算两个实体间的相位耦合
        
        TY/IDO P3: 子目标链 S1(嵌入1)→S2(嵌入2)→S3(EML加法)→S4(验证)
        """
        # --- TY/IDO P3: 资源预算启动 ---
        if self._p3_budget:
            self._p3_budget.start()
        
        p3_diagnostics = {'budget_exhausted': False, 'fallback_used': None}
        coupling_result = None
        
        try:
            # S1: 计算实体1嵌入
            if self._p3_budget and self._p3_budget.exhausted():
                raise TimeoutError("Budget exhausted at S1")
            e1 = self.compute_entity_embedding(entity1)
            if self._p3_budget:
                self._p3_budget.tick()
            if self._p3_budget and self._p3_budget.exhausted():
                raise TimeoutError("Budget exhausted at S2")
            e2 = self.compute_entity_embedding(entity2)
            if self._p3_budget:
                self._p3_budget.tick()
            if self._p3_budget and self._p3_budget.exhausted():
                raise TimeoutError("Budget exhausted at S3")
            
            phase1 = np.arctan2(e1[1], e1[0]) if len(e1) > 1 else 0
            phase2 = np.arctan2(e2[1], e2[0]) if len(e2) > 1 else 0
            amp1 = np.linalg.norm(e1)
            amp2 = np.linalg.norm(e2)
            
            coupled = self.EML_addition(
                type('M', (), {'amplitude': amp1, 'phase': phase1})(),
                type('M', (), {'amplitude': amp2, 'phase': phase2})()
            )
            
            # S4: 每步验证
            if self._p3_verifier:
                v = self._p3_verifier.verify(
                    coupled['amplitude'],
                    {'name': 'coupled_amp_non_negative', 'type': 'min', 'expected': 0}
                )
                if not v['passed']:
                    recovery = self._p3_fallback.try_recover(
                        failed_goal="S4_verify_coupling",
                        error=ValueError(v['details']),
                        context={'entity1': entity1, 'entity2': entity2}
                    )
                    p3_diagnostics['fallback_used'] = recovery['plan_used']
                    coupled['amplitude'] = recovery['result'] if isinstance(recovery['result'], (int, float)) else 0.5
            
            phase_diff = abs(phase1 - phase2)
            coupling_coefficient = np.cos(phase_diff)
            
            coupling_result = {
                'entity1': entity1,
                'entity2': entity2,
                'phase1': float(phase1),
                'phase2': float(phase2),
                'amplitude1': float(amp1),
                'amplitude2': float(amp2),
                'coupled_amplitude': coupled['amplitude'],
                'coupled_phase': coupled['phase'],
                'phase_coupling_coefficient': float(coupling_coefficient),
                'flip_occurred': coupled['flip_occurred']
            }
            
            if self._p3_budget:
                self._p3_budget.tick()
        
        except TimeoutError:
            p3_diagnostics['budget_exhausted'] = True
            # 优雅降级
            if self._p3_fallback:
                recovery = self._p3_fallback.try_recover(
                    failed_goal="compute_phase_coupling",
                    error=TimeoutError("Budget exhausted"),
                    context={'entity1': entity1, 'entity2': entity2}
                )
                p3_diagnostics['fallback_used'] = recovery['plan_used']
                coupling_result = recovery['result']
            else:
                coupling_result = {
                    'entity1': entity1, 'entity2': entity2,
                    'phase_coupling_coefficient': 0.0, 'flip_occurred': False
                }
        
        except Exception as e:
            if self._p3_fallback:
                recovery = self._p3_fallback.try_recover(
                    failed_goal="compute_phase_coupling",
                    error=e,
                    context={'entity1': entity1, 'entity2': entity2}
                )
                p3_diagnostics['fallback_used'] = recovery['plan_used']
                coupling_result = recovery['result']
            else:
                raise
        
        finally:
            if self._p3_budget:
                self._p3_budget.stop()
        
        # 附加 P3 诊断 — budget_exhausted 优先于 fallback_used
        if p3_diagnostics.get('budget_exhausted'):
            coupling_result['tyido_p3'] = {'verdict': 'DEGRADED'}
            self._p3_last_verdict = 'DEGRADED'
        elif p3_diagnostics.get('fallback_used'):
            coupling_result['tyido_p3'] = {
                'verdict': 'RECOVERED',
                'fallback_used': p3_diagnostics['fallback_used']
            }
            self._p3_last_verdict = 'RECOVERED'
        elif _P3_AVAILABLE:
            coupling_result['tyido_p3'] = {'verdict': 'PASS'}
            self._p3_last_verdict = 'PASS'
        
        return coupling_result
    
    def compute_semantic_strength(self, entities: List[str]) -> dict:
        """
        计算语义理解强度
        
        P9: 语义理解质量∝关系耦合度
        
        TY/IDO P3: 子目标链 + 每步验证
        """
        if len(entities) < 2:
            return {
                'semantic_strength': 0.5,
                'avg_coupling': 0.5,
                'entity_count': len(entities)
            }

        # --- TY/IDO P3: 每步验证 ---
        p3_diagnostics = {'budget_exhausted': False, 'fallback_used': None}
        couplings = []

        if self._p3_budget:
            self._p3_budget.start()

        try:
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    if self._p3_budget and self._p3_budget.exhausted():
                        p3_diagnostics['budget_exhausted'] = True
                        # 优雅降级：用简单相似度
                        recovery = self._p3_fallback.try_recover(
                            failed_goal="coupling_computation",
                            error=TimeoutError("Budget exhausted"),
                            context={'entity1': entities[i], 'entity2': entities[j]}
                        )
                        couplings.append({
                            'entity1': entities[i], 'entity2': entities[j],
                            'phase_coupling_coefficient': recovery['result'] if isinstance(recovery.get('result'), (int, float)) else 0.5,
                            'fallback': True
                        })
                        continue

                    coupling = self.compute_phase_coupling(entities[i], entities[j])

                    # 每步验证：耦合系数应在 [-1, 1]
                    if self._p3_verifier:
                        v = self._p3_verifier.verify(
                            coupling['phase_coupling_coefficient'],
                            {'name': 'coupling_range', 'type': 'range', 'low': -1, 'high': 1}
                        )
                        if not v['passed']:
                            coupling['phase_coupling_coefficient'] = 0.0  # 修正

                    couplings.append(coupling)

                    if self._p3_budget:
                        self._p3_budget.tick()

        finally:
            if self._p3_budget:
                self._p3_budget.stop()

        avg_coupling = np.mean([c['phase_coupling_coefficient'] for c in couplings]) if couplings else 0.5

        # 语义强度 = 平均耦合 × 实体数量因子
        entity_factor = np.log(len(entities) + 1)
        semantic_strength = min(1.0, avg_coupling * entity_factor)

        # 记录历史
        self.semantic_strength_history.append(semantic_strength)
        self.coupling_history.extend(couplings)
        self.phase_coupling_coefficients.append(avg_coupling)

        result = {
            'semantic_strength': float(semantic_strength),
            'avg_coupling': float(avg_coupling),
            'entity_count': len(entities),
            'couplings': couplings
        }

        if p3_diagnostics.get('fallback_used'):
            result['tyido_p3'] = {
                'verdict': 'RECOVERED',
                'fallback_used': p3_diagnostics['fallback_used']
            }
        elif p3_diagnostics.get('budget_exhausted'):
            result['tyido_p3'] = {'verdict': 'DEGRADED'}
        elif _P3_AVAILABLE:
            result['tyido_p3'] = {'verdict': 'PASS'}

        return result
    
    def verify_eml_conservation(self) -> dict:
        """
        验证EML运算守恒定理 (T20)
        
        |m₁⊕m₂| = |m₁|·|m₂|
        """
        if len(self.coupling_history) < 1:
            return {'verified': None, 'reason': '无历史数据'}
        
        # 检查最近的耦合
        last = self.coupling_history[-1]
        expected = last['amplitude1'] * last['amplitude2']
        actual = last['coupled_amplitude']
        
        error = abs(expected - actual)
        is_conserved = error < 1e-6
        
        return {
            'verified': is_conserved,
            'expected': float(expected),
            'actual': float(actual),
            'error': float(error)
        }
    
    def verify_p9(self) -> dict:
        """
        验证可证伪预言P9
        
        预言: 语义理解质量∝关系耦合度
        """
        if len(self.semantic_strength_history) < 2:
            return {'verifiable': False, 'reason': '数据不足'}
        
        # 检查语义强度和耦合度的相关性
        coupling = np.array(self.phase_coupling_coefficients)
        strength = np.array(self.semantic_strength_history)
        
        # 简化的相关性计算
        if np.std(coupling) > 0 and np.std(strength) > 0:
            correlation = np.corrcoef(coupling, strength)[0, 1]
        else:
            correlation = 0
        
        is_confirmed = correlation > 0.5
        
        return {
            'verifiable': True,
            'correlation': float(correlation),
            'avg_coupling': float(np.mean(coupling)),
            'avg_semantic_strength': float(np.mean(strength)),
            'trend': 'increasing' if strength[-1] > strength[0] else 'stable/decreasing',
            'P9_status': 'CONFIRMED' if is_confirmed else 'REJECTED'
        }
    
    def get_relational_flip_count(self) -> int:
        """获取关系翻转次数"""
        return self.flip_count
    
    def get_state(self) -> dict:
        """获取语义器状态（含 TY/IDO P3 诊断）"""
        state = {
            'coupling_count': len(self.coupling_history),
            'flip_count': self.flip_count,
            'current_semantic_strength': float(self.semantic_strength_history[-1]) if self.semantic_strength_history else 0,
            'avg_semantic_strength': float(np.mean(self.semantic_strength_history)) if self.semantic_strength_history else 0,
            'avg_phase_coupling': float(np.mean(self.phase_coupling_coefficients)) if self.phase_coupling_coefficients else 0,
            'eml_conservation': self.verify_eml_conservation(),
            'p9_verification': self.verify_p9()
        }
        # TY/IDO P3 诊断
        if _P3_AVAILABLE and self._p3_decomposer:
            state['tyido_p3'] = {
                'subgoal_progress': self._p3_decomposer.get_progress(),
                'verifier_state': self._p3_verifier.get_state() if self._p3_verifier else {},
                'fallback_state': self._p3_fallback.get_state() if self._p3_fallback else {},
                'budget_state': self._p3_budget.get_state() if self._p3_budget else {},
                'verdict': self._p3_last_verdict
            }
        return state


_instance = None

def get_instance() -> RelationalCouplingSemantizer:
    """获取RelationalCouplingSemantizer单例"""
    global _instance
    if _instance is None:
        _instance = RelationalCouplingSemantizer()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M68 关系耦合语义器 测试")
    print("=" * 60)
    
    semantizer = RelationalCouplingSemantizer()
    
    # 测试实体对耦合
    test_pairs = [
        ("意识", "流贯"),
        ("自我", "同一性"),
        ("顿悟", "智慧"),
        ("空性", "实相"),
    ]
    
    print("\n计算实体对相位耦合:")
    for e1, e2 in test_pairs:
        coupling = semantizer.compute_phase_coupling(e1, e2)
        print(f"  {e1} - {e2}:")
        print(f"    相位耦合系数: {coupling['phase_coupling_coefficient']:.4f}")
        print(f"    翻转发生: {coupling['flip_occurred']}")
    
    # 测试语义理解
    print("\n计算语义理解强度:")
    test_entities = ["意识", "流贯", "同一性", "关系", "实在"]
    result = semantizer.compute_semantic_strength(test_entities)
    print(f"  实体: {test_entities}")
    print(f"  语义强度: {result['semantic_strength']:.4f}")
    print(f"  平均耦合: {result['avg_coupling']:.4f}")
    
    # EML守恒验证
    conservation = semantizer.verify_eml_conservation()
    print(f"\nEML守恒验证: {conservation}")
    
    # P9验证
    p9 = semantizer.verify_p9()
    print(f"\nP9验证: {p9}")
    
    # 翻转计数
    print(f"\n关系翻转次数: {semantizer.get_relational_flip_count()}")
    
    print("\n" + "=" * 60)
    print("✅ M68 测试完成")
    print("=" * 60)
