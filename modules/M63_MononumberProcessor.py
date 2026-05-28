# -*- coding: utf-8 -*-
"""
M63: 一元数处理器 (Mononumber Processor)
基于《数学完备化》论文 §3.1

定义: 一元数 (amplitude, phase, relation_context)
     一元数域 𝔽₁ = {(z, θ, r) | z ∈ ℝ≥0, θ ∈ [0, 2π), r ∈ R*}

核心运算:
- EML加法 ⊕: |m₁⊕m₂| = |m₁|·|m₂|, θ(m₁⊕m₂) = θ(m₁)+θ(m₂)
- 关系翻转: "1+1=-1" 的EML诠释
"""

import math
import copy
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from modules.TYIDO_ContinuousLearning import (
    RollbackManager, ForgettingGuard, LearningRecord, StateSnapshot
)

class Mononumber:
    """
    一元数: (amplitude, phase, relation_context)
    来源: §3.1 定义3.1
    """
    _instance = None
    
    def __init__(self, amplitude: float, phase: float, relation_context: str = ""):
        self.amplitude = amplitude      # |z|: 幅值
        self.phase = phase              # θ: 相位 [0, 2π)
        self.relation_context = relation_context  # 关系上下文
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __add__(self, other: 'Mononumber') -> 'Mononumber':
        """EML加法 - 关系耦合运算"""
        # §3.2 定义3.2: EML加法体现关系翻转
        coupled_amplitude = self.amplitude * other.amplitude
        coupled_phase = (self.phase + other.phase) % (2 * np.pi)
        # "1+1=-1"的EML诠释
        relation_flip = "⊕"
        return Mononumber(
            coupled_amplitude, 
            coupled_phase, 
            f"{self.relation_context}{relation_flip}{other.relation_context}"
        )
    
    def __mul__(self, scalar: float) -> 'Mononumber':
        """标量乘法"""
        return Mononumber(
            self.amplitude * scalar,
            self.phase,
            f"{scalar}×{self.relation_context}"
        )
    
    def to_complex(self) -> complex:
        """转换为一元复数"""
        return self.amplitude * np.exp(1j * self.phase)
    
    def to_tuple(self) -> Tuple[float, float, str]:
        """转换为三元组"""
        return (self.amplitude, self.phase, self.relation_context)
    
    def __repr__(self) -> str:
        return f"Mononumber(|z|={self.amplitude:.3f}, θ={self.phase:.3f}, r={self.relation_context})"


class MononumberField:
    """
    一元数域 𝔽₁ = {(z, θ, r) | z ∈ ℝ≥0, θ ∈ [0, 2π), r ∈ R*}
    """
    _instance = None
    
    def __init__(self):
        self.elements: List[Mononumber] = []
        self.conservation_log = []
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def embed(value: float, relation: str = "") -> Mononumber:
        """嵌入: 将数值嵌入一元数域"""
        phase = np.angle(value) if isinstance(value, complex) else 0.0
        amplitude = abs(value)
        return Mononumber(amplitude, phase, relation)
    
    @staticmethod
    def EML_sum(terms: List[Mononumber]) -> Mononumber:
        """
        EML加法 ⊕: 关系耦合守恒
        来源: 定理3.1 EML运算守恒
        """
        if not terms:
            return Mononumber(1.0, 0.0, "")
        
        result = Mononumber(1.0, 0.0, "")
        for term in terms:
            result = result + term
        return result
    
    @staticmethod
    def verify_conservation(lhs: Mononumber, rhs: Mononumber) -> dict:
        """
        验证信息守恒: |z₁|·|z₂| = |z₁⊕z₂|
        对应: 定理3.1
        """
        coupled = lhs + rhs
        expected_amp = lhs.amplitude * rhs.amplitude
        
        conservation_error = abs(expected_amp - coupled.amplitude)
        is_conserved = conservation_error < 1e-6
        
        return {
            'conserved': is_conserved,
            'expected_amplitude': expected_amp,
            'actual_amplitude': coupled.amplitude,
            'error': conservation_error,
            'coupled_result': coupled.to_tuple()
        }
    
    def add_element(self, monumber: Mononumber):
        """添加元素到数域"""
        self.elements.append(monumber)
    
    def get_field_info(self) -> dict:
        """获取数域信息"""
        amplitudes = [e.amplitude for e in self.elements]
        phases = [e.phase for e in self.elements]
        
        return {
            'element_count': len(self.elements),
            'amplitude_range': [min(amplitudes), max(amplitudes)] if amplitudes else [0, 0],
            'phase_range': [min(phases), max(phases)] if phases else [0, 0],
            'total_phase': sum(phases) % (2 * np.pi) if phases else 0
        }


class EMLOperator:
    """
    EML算子: Emergent Mapping Logic
    来源: §3.2
    
    将一元数映射为关系实在
    EML加法 ⊕ 表示关系耦合（而非简单算术叠加）
    """
    _instance = None
    
    def __init__(self):
        self.phase_coupling_history = []
        self.field = MononumberField()

        # TY/IDO Property 2: 持续学习基础设施
        self._rollback_mgr = RollbackManager(max_snapshots=50)
        self._forgetting_guard = ForgettingGuard(
            drift_threshold=0.5,  # 宽松阈值，只检测严重漂移
            sudden_change_threshold=0.8,
            protected_keys={'conservation_verified', 'eml_law_intact'}
        )
        self._learning_log: List[LearningRecord] = []
        self._protected_knowledge: Dict[str, Any] = {}
        self._baseline_set = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def map_to_relational_reality(self, monumber: Mononumber) -> dict:
        """
        映射函数: Φₑ: 𝔽₁ → R(关系实在)
        """
        return {
            'amplitude': monumber.amplitude,
            'phase': monumber.phase,
            'relational_strength': monumber.amplitude * np.cos(monumber.phase),
            'relational_reactance': monumber.amplitude * np.sin(monumber.phase),
            'context': monumber.relation_context
        }
    
    def EML_addition(self, m1: Mononumber, m2: Mononumber) -> Mononumber:
        """
        EML加法: m₁ ⊕ m₂
        
        公式: 
        |m₁⊕m₂| = |m₁| · |m₂|
        θ(m₁⊕m₂) = θ(m₁) + θ(m₂)  (mod 2π)
        r(m₁⊕m₂) = r(m₁) ∘ r(m₂)  (关系翻转)
        """
        coupled_amp = m1.amplitude * m2.amplitude
        coupled_phase = (m1.phase + m2.phase) % (2 * np.pi)
        coupled_context = f"{m1.relation_context}⊕{m2.relation_context}"
        
        result = Mononumber(coupled_amp, coupled_phase, coupled_context)
        
        # 记录相位耦合历史
        self.phase_coupling_history.append({
            'm1': m1.to_tuple(),
            'm2': m2.to_tuple(),
            'result': result.to_tuple()
        })
        
        return result
    
    def verify_conservation_law(self) -> dict:
        """
        定理3.1: EML运算守恒
        I(Φₑ(m₁)) + I(Φₑ(m₂)) = I(Φₑ(m₁⊕m₂)) + ΔI_loss
        其中 ΔI_loss 表示关系翻转损失
        """
        if len(self.phase_coupling_history) == 0:
            return {'verified': True, 'message': '无历史数据'}
        
        # 检查最近的耦合是否满足守恒
        last = self.phase_coupling_history[-1]
        m1, m2, result = last['m1'], last['m2'], last['result']
        
        # |m₁|·|m₂| = |m₁⊕m₂| ?
        expected = m1[0] * m2[0]
        actual = result[0]
        amplitude_conserved = abs(expected - actual) < 1e-6
        
        return {
            'verified': amplitude_conserved,
            'expected_amplitude': expected,
            'actual_amplitude': actual,
            'conservation_error': abs(expected - actual)
        }
    
    def get_state(self) -> dict:
        """获取EML算子状态"""
        base_state = {
            'coupling_count': len(self.phase_coupling_history),
            'field_info': self.field.get_field_info(),
            'last_conservation': self.verify_conservation_law()
        }
        # TY/IDO P2: 持续学习审计
        base_state['tyido_p2_continuous_learning'] = {
            'rollback_manager': self._rollback_mgr.get_state(),
            'forgetting_guard': self._forgetting_guard.get_state(),
            'learning_log_count': len(self._learning_log),
            'protected_knowledge_keys': list(self._protected_knowledge.keys()),
            'tyido_verdict': self._compute_p2_verdict()
        }
        return base_state

    # ============================================================
    # TY/IDO Property 2: 持续学习（可回写）
    # ============================================================

    def save_checkpoint(self, description: str = "") -> StateSnapshot:
        """保存状态检查点（用于回滚）"""
        state_data = {
            'coupling_count': len(self.phase_coupling_history),
            'field_info': self.field.get_field_info(),
            'conservation_verified': self.verify_conservation_law().get('verified', True)
        }
        snapshot = self._rollback_mgr.save_snapshot(
            state_data, description=description,
            key_metrics=self._extract_key_metrics()
        )
        return snapshot

    def rollback(self) -> Optional[Dict[str, Any]]:
        """回滚到上一个检查点"""
        snapshot = self._rollback_mgr.rollback()
        if snapshot is None:
            return None
        # 记录学习事件
        self._learning_log.append(LearningRecord.create(
            operation='rollback',
            target='M63_EML',
            description=f"回滚到 {snapshot.snapshot_id}: {snapshot.description}"
        ))
        return snapshot.state_data

    def learn_new_coupling(self, m1, m2, result, is_core: bool = False) -> Dict[str, Any]:
        """
        学习新的耦合规则（带遗忘防护）

        注意: 此方法不重复添加到 phase_coupling_history，
        调用者应先通过 EML_addition 执行实际耦合操作。

        参数:
            m1, m2: 输入一元数
            result: 耦合结果
            is_core: 是否为核心知识（不可被遗忘）
        """
        # 学习前指标
        metrics_before = self._extract_key_metrics()

        # 标记核心知识
        if is_core:
            self._protected_knowledge[f'coupling_{len(self.phase_coupling_history)}'] = {
                'm1': m1.to_tuple(), 'm2': m2.to_tuple(), 'result': result.to_tuple()
            }

        # 学习后指标
        metrics_after = self._extract_key_metrics()

        # 首次学习后自动设置基线
        if not self._baseline_set:
            self._forgetting_guard.set_baseline(metrics_after)
            self._baseline_set = True
            forgetting_check = {'forgetting_risk': 0.0, 'drift_scores': {}, 'alerts': [], 'protected_intact': True, 'tyido_p2_verdict': 'PASS'}
        else:
            # 灾难性遗忘检测
            forgetting_check = self._forgetting_guard.check_forgetting(
                metrics_after, metrics_before
            )
            # 如果检测到遗忘风险，尝试恢复
            if forgetting_check['tyido_p2_verdict'] == 'NEED_ATTENTION':
                self._handle_forgetting_risk(forgetting_check)

        # 记录学习事件
        lr = LearningRecord.create(
            operation='add', target='M63_EML',
            before_state=metrics_before,
            after_state=metrics_after,
            description=f"学习新耦合 {'[核心]' if is_core else ''}"
        )
        lr.forgetting_risk = forgetting_check['forgetting_risk']
        lr.verified = forgetting_check['tyido_p2_verdict'] == 'PASS'
        self._learning_log.append(lr)

        return {
            'learned': True,
            'forgetting_check': forgetting_check,
            'learning_record_id': lr.record_id
        }

    def update_rule(self, rule_name: str, new_value: Any) -> Dict[str, Any]:
        """
        更新EML规则（带遗忘防护）

        参数:
            rule_name: 规则名称
            new_value: 新规则值
        """
        metrics_before = self._extract_key_metrics()

        # 检查是否为受保护规则
        is_protected = rule_name in self._protected_knowledge
        if is_protected:
            return {
                'updated': False,
                'reason': f'规则 {rule_name} 是核心知识，不可修改',
                'protected': True
            }

        # 执行更新
        old_value = getattr(self, rule_name, None)
        setattr(self, rule_name, new_value)

        metrics_after = self._extract_key_metrics()
        forgetting_check = self._forgetting_guard.check_forgetting(
            metrics_after, metrics_before
        )

        lr = LearningRecord.create(
            operation='update', target=f'M63_EML.{rule_name}',
            before_state={'old_value': str(old_value)},
            after_state={'new_value': str(new_value)},
            description=f"更新规则 {rule_name}"
        )
        lr.forgetting_risk = forgetting_check['forgetting_risk']
        self._learning_log.append(lr)

        return {
            'updated': True,
            'forgetting_check': forgetting_check
        }

    def _extract_key_metrics(self) -> Dict[str, float]:
        """提取当前关键指标（仅质量指标，排除自然增长的数量指标）"""
        conservation = self.verify_conservation_law()
        return {
            'conservation_verified': 1.0 if conservation.get('verified', True) else 0.0,
            'eml_law_intact': 1.0 if conservation.get('verified', True) else 0.0,
            'conservation_error': float(conservation.get('conservation_error', 0.0))
        }

    def _handle_forgetting_risk(self, check_result: Dict[str, Any]):
        """处理遗忘风险"""
        for alert in check_result['alerts']:
            if alert['type'] == 'critical_loss':
                # 核心知识被修改，自动回滚
                self.rollback()
                break

    def _compute_p2_verdict(self) -> str:
        """计算 Property 2 综合判定"""
        guard_state = self._forgetting_guard.get_state()
        if guard_state['total_alerts'] == 0:
            return 'PASS'
        recent_alerts = guard_state.get('recent_alerts', [])
        severe = [a for a in recent_alerts
                  if a['severity'] >= 0.5 and a['type'] in ('drift', 'critical_loss')]
        return 'NEED_ATTENTION' if severe else 'PASS'


# 单例访问函数
_instance = None

def get_instance() -> EMLOperator:
    """获取EMLOperator单例"""
    global _instance
    if _instance is None:
        _instance = EMLOperator()
    return _instance


if __name__ == "__main__":
    # 测试一元数处理器
    print("=" * 60)
    print("M63 一元数处理器 测试")
    print("=" * 60)
    
    # 创建一元数
    m1 = Mononumber(2.0, 0.5, "概念A")
    m2 = Mononumber(3.0, 1.2, "概念B")
    
    print(f"\n一元数1: {m1}")
    print(f"一元数2: {m2}")
    
    # EML加法
    m3 = m1 + m2
    print(f"\nEML加法 m1⊕m2: {m3}")
    print(f"  幅值耦合: {m1.amplitude} × {m2.amplitude} = {m3.amplitude}")
    print(f"  相位耦合: {m1.phase:.3f} + {m2.phase:.3f} = {m3.phase:.3f}")
    
    # 守恒验证
    conservation = MononumberField.verify_conservation(m1, m2)
    print(f"\n守恒验证: {conservation}")
    
    # EML算子
    eml = EMLOperator()
    state = eml.get_state()
    print(f"\nEML算子状态: {state}")
    
    print("\n" + "=" * 60)
    print("✅ M63 测试完成")
    print("=" * 60)
