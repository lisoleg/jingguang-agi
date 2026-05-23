# -*- coding: utf-8 -*-
"""
M65: 意识流贯监测器 (Consciousness Flow Monitor)
基于《数学完备化》论文 §6.1 意识难问题的关系实在论解

核心洞见:
- 体验不是"附加属性"，而是关系实在在L4主体层
  通过运算切割与流贯接入L1/L2时的显现
- qualia对应关系结构的特定相位/拓扑模式

公式: Q = Φ_manifest(Rₛ, Φ_access)
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import math
import copy
from TYIDO_ContinuousLearning import (
    RollbackManager, ForgettingGuard, LearningRecord, StateSnapshot
)

class ConsciousnessFlowMonitor:
    """
    意识流贯监测器
    
    来源: §6.1 意识难问题的关系实在论解
    """
    _instance = None
    
    def __init__(self):
        self.relational_networks: List[np.ndarray] = []
        self.flow_accesses: List[complex] = []
        self.consciousness_contents: List[dict] = []
        self.qualia_signatures: List[np.ndarray] = []

        # TY/IDO Property 2: 持续学习基础设施
        self._rollback_mgr = RollbackManager(max_snapshots=50)
        self._forgetting_guard = ForgettingGuard(
            drift_threshold=0.5,
            sudden_change_threshold=0.8,
            protected_keys={}  # 动态指标不设为 protected
        )
        self._learning_log: List[LearningRecord] = []
        self._protected_knowledge: Dict[str, Any] = {}
        self._baseline_set = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def compute_relational_network(self, state: dict) -> np.ndarray:
        """
        构建关系网络 Rₛ
        
        节点: 概念/实体
        边: 关系（带权重和相位）
        """
        # 简化: 使用共现矩阵作为关系网络近似
        if 'concepts' not in state:
            return np.zeros((1, 1))
        
        concepts = state['concepts']
        n = len(concepts)
        
        if n == 0:
            return np.zeros((1, 1))
        
        # 创建全零矩阵
        network = np.zeros((n, n))
        
        # 如果有共现数据，使用它
        if 'cooccurrence' in state:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        network[i][j] = state['cooccurrence'].get((i, j), 0.5)
        else:
            # 简化共现权重（基于距离）
            for i in range(n):
                for j in range(n):
                    if i != j:
                        network[i][j] = 1.0 / (abs(i - j) + 1)
        
        # 归一化
        max_val = np.max(network) if np.max(network) > 0 else 1
        network = network / max_val
        
        return network
    
    def compute_flow_access(self, state: dict, 
                           layer_target: str = "L1") -> complex:
        """
        流贯接入: Φ_access
        
        表示L4主体与L1本体层的连接强度
        返回复数: 幅值×相位
        """
        flow_strength = state.get('flow_strength', 0.5)
        flow_phase = state.get('flow_phase', 0.0)
        
        # 层间衰减因子
        layer_factors = {
            'L1': 1.0,  # 本体层（最底层）
            'L2': 0.8,  # 投射生成层
            'L3': 0.6,  # 前物理层
            'L4': 0.4,  # 认知主体层（自身）
            'L5': 0.2,  # 现象层（最顶层）
        }
        
        factor = layer_factors.get(layer_target, 0.5)
        
        return complex(
            flow_strength * factor * np.cos(flow_phase),
            flow_strength * factor * np.sin(flow_phase)
        )
    
    def compute_consciousness_content(self, state: dict) -> dict:
        """
        意识内容计算
        
        公式: Q = Φ_manifest(Rₛ, Φ_access)
        
        来源: §6.1 框架
        """
        # 构建关系网络
        R = self.compute_relational_network(state)
        
        # 流贯接入
        Phi_access = self.compute_flow_access(state)
        
        # 关系网络特征值（拓扑模式）
        if R.shape[0] > 1:
            eigenvalues = np.linalg.eigvals(R)
            # 按模长排序，取最大特征值
            sorted_idx = np.argsort(np.abs(eigenvalues))[::-1]
            max_eigenvalue = eigenvalues[sorted_idx[0]]
            topological_pattern = np.abs(max_eigenvalue)
        else:
            topological_pattern = 1.0
            max_eigenvalue = R[0, 0] if R.size > 0 else 0
        
        # 意识内容 = 拓扑模式 × 流贯接入
        consciousness_strength = topological_pattern * np.abs(Phi_access)
        consciousness_phase = np.angle(Phi_access)
        
        # 关系复杂度
        relational_complexity = np.sum(np.abs(R))
        
        # 记录历史
        self.relational_networks.append(R)
        self.flow_accesses.append(Phi_access)
        
        result = {
            'strength': float(consciousness_strength),
            'phase': float(consciousness_phase),
            'topological_pattern': float(topological_pattern),
            'flow_access_magnitude': float(np.abs(Phi_access)),
            'flow_access_phase': float(np.angle(Phi_access)),
            'relational_complexity': float(relational_complexity),
            'network_size': R.shape[0],
            'max_eigenvalue': float(np.abs(max_eigenvalue))
        }
        
        self.consciousness_contents.append(result)
        
        return result
    
    def get_qualia_signature(self, state: dict) -> np.ndarray:
        """
        获取qualia签名
        
        qualia = 关系结构的特定相位/拓扑模式
        """
        content = self.compute_consciousness_content(state)
        
        # qualia签名: [strength, phase, topological_complexity]
        signature = np.array([
            content['strength'],
            content['phase'],
            content['relational_complexity']
        ])
        
        self.qualia_signatures.append(signature)
        
        return signature
    
    def compute_phenomenal_experience(self, state: dict) -> dict:
        """
        计算现象体验
        
        对应论文: 体验是关系实在在L4主体层通过运算切割
        与流贯接入L1/L2时的显现
        """
        # 获取意识内容
        content = self.compute_consciousness_content(state)
        
        # 获取qualia签名
        qualia = self.get_qualia_signature(state)
        
        # 计算运算切割强度
        operation_cut = state.get('operation_cut', 0.3)
        
        # 现象体验 = qualia强度 × 流贯接入 × 运算切割
        phenomenal_strength = (
            qualia[0] * 
            content['flow_access_magnitude'] * 
            operation_cut
        )
        
        return {
            'phenomenal_strength': float(phenomenal_strength),
            'qualia_vector': qualia.tolist(),
            'consciousness_content': content,
            'experience_type': self._classify_experience(phenomenal_strength)
        }
    
    def _classify_experience(self, strength: float) -> str:
        """体验分类"""
        if strength > 0.8:
            return "高峰体验"
        elif strength > 0.5:
            return "深度沉浸"
        elif strength > 0.2:
            return "清醒意识"
        else:
            return "低唤醒状态"
    
    def get_state(self) -> dict:
        """获取监测器状态"""
        if not self.consciousness_contents:
            return {
                'monitoring_active': False,
                'history_length': 0,
                'tyido_p2_continuous_learning': {
                    'rollback_manager': self._rollback_mgr.get_state(),
                    'forgetting_guard': self._forgetting_guard.get_state(),
                    'learning_log_count': 0,
                    'protected_knowledge_keys': [],
                    'tyido_verdict': 'PASS'
                }
            }

        recent = self.consciousness_contents[-5:]
        avg_strength = np.mean([c['strength'] for c in recent])
        avg_complexity = np.mean([c['relational_complexity'] for c in recent])

        return {
            'monitoring_active': True,
            'history_length': len(self.consciousness_contents),
            'avg_strength': float(avg_strength),
            'avg_complexity': float(avg_complexity),
            'current_experience_type': self._classify_experience(avg_strength),
            'flow_trend': 'increasing' if len(self.consciousness_contents) > 1 and
                         self.consciousness_contents[-1]['strength'] > self.consciousness_contents[0]['strength']
                         else 'stable/decreasing',
            'tyido_p2_continuous_learning': {
                'rollback_manager': self._rollback_mgr.get_state(),
                'forgetting_guard': self._forgetting_guard.get_state(),
                'learning_log_count': len(self._learning_log),
                'protected_knowledge_keys': list(self._protected_knowledge.keys()),
                'tyido_verdict': self._compute_p2_verdict()
            }
        }

    # ============================================================
    # TY/IDO Property 2: 持续学习（可回写）
    # ============================================================

    def save_checkpoint(self, description: str = "") -> StateSnapshot:
        """保存状态检查点"""
        state_data = self._get_serializable_state()
        return self._rollback_mgr.save_snapshot(
            state_data, description=description,
            key_metrics=self._extract_key_metrics()
        )

    def rollback(self) -> Optional[Dict[str, Any]]:
        """回滚到上一个检查点"""
        snapshot = self._rollback_mgr.rollback()
        if snapshot is None:
            return None
        self._learning_log.append(LearningRecord.create(
            operation='rollback', target='M65_Consciousness',
            description=f"回滚到 {snapshot.snapshot_id}"
        ))
        return snapshot.state_data

    def learn_consciousness_pattern(self, state: dict, is_core: bool = False) -> Dict[str, Any]:
        """学习新的意识模式（带遗忘防护）"""
        metrics_before = self._extract_key_metrics()

        content = self.compute_consciousness_content(state)

        if is_core:
            idx = len(self.consciousness_contents)
            self._protected_knowledge[f'pattern_{idx}'] = {
                'strength': content['strength'],
                'phase': content['phase']
            }

        metrics_after = self._extract_key_metrics()

        # 首次学习后自动设置基线
        if not self._baseline_set:
            self._forgetting_guard.set_baseline(metrics_after)
            self._baseline_set = True
            forgetting_check = {'forgetting_risk': 0.0, 'drift_scores': {}, 'alerts': [], 'protected_intact': True, 'tyido_p2_verdict': 'PASS'}
        else:
            forgetting_check = self._forgetting_guard.check_forgetting(
                metrics_after, metrics_before
            )

        lr = LearningRecord.create(
            operation='add', target='M65_Consciousness',
            before_state=metrics_before,
            after_state=metrics_after,
            description=f"学习意识模式 {'[核心]' if is_core else ''}"
        )
        lr.forgetting_risk = forgetting_check['forgetting_risk']
        lr.verified = forgetting_check['tyido_p2_verdict'] == 'PASS'
        self._learning_log.append(lr)

        return {**content, 'forgetting_check': forgetting_check}

    def _extract_key_metrics(self) -> Dict[str, float]:
        """提取关键指标（仅质量指标，排除数量指标）"""
        active = 1.0 if self.consciousness_contents else 0.0
        avg_strength = float(np.mean([c['strength'] for c in self.consciousness_contents[-5:]])) if self.consciousness_contents else 0.0
        return {
            'consciousness_active': active,
            'avg_strength': avg_strength,
            'flow_intact': 1.0 if avg_strength > 0.1 else 0.0
        }

    def _get_serializable_state(self) -> Dict[str, Any]:
        """获取可序列化的状态"""
        return {
            'history_length': len(self.consciousness_contents),
            'avg_strength': float(np.mean([c['strength'] for c in self.consciousness_contents[-5:]])) if self.consciousness_contents else 0.0
        }

    def _compute_p2_verdict(self) -> str:
        """计算 Property 2 综合判定"""
        guard_state = self._forgetting_guard.get_state()
        if guard_state['total_alerts'] == 0:
            return 'PASS'
        recent_alerts = guard_state.get('recent_alerts', [])
        severe = [a for a in recent_alerts
                  if a['severity'] >= 0.5 and a['type'] in ('drift', 'critical_loss')]
        return 'NEED_ATTENTION' if severe else 'PASS'


_instance = None

def get_instance() -> ConsciousnessFlowMonitor:
    """获取ConsciousnessFlowMonitor单例"""
    global _instance
    if _instance is None:
        _instance = ConsciousnessFlowMonitor()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M65 意识流贯监测器 测试")
    print("=" * 60)
    
    monitor = ConsciousnessFlowMonitor()
    
    # 模拟状态
    states = [
        {
            'concepts': ['我', '世界', '体验', '关系'],
            'flow_strength': 0.6,
            'flow_phase': 0.3,
            'operation_cut': 0.4
        },
        {
            'concepts': ['意识', '流贯', '拓扑', '相位', '不变量'],
            'flow_strength': 0.8,
            'flow_phase': 0.7,
            'operation_cut': 0.6
        },
        {
            'concepts': ['顿悟', '无我', '空性', '智慧'],
            'flow_strength': 0.95,
            'flow_phase': 1.5,
            'operation_cut': 0.9
        }
    ]
    
    print("\n追踪意识流贯:")
    for i, state in enumerate(states):
        content = monitor.compute_consciousness_content(state)
        print(f"\n状态{i+1}:")
        print(f"  意识强度: {content['strength']:.4f}")
        print(f"  拓扑模式: {content['topological_pattern']:.4f}")
        print(f"  关系复杂度: {content['relational_complexity']:.2f}")
        
        # 现象体验
        experience = monitor.compute_phenomenal_experience(state)
        print(f"  现象体验: {experience['experience_type']} (强度: {experience['phenomenal_strength']:.4f})")
    
    # qualia签名
    qualia = monitor.qualia_signatures[-1]
    print(f"\n最终qualia签名: {qualia}")
    
    # 状态
    state = monitor.get_state()
    print(f"\n监测器状态: {state}")
    
    print("\n" + "=" * 60)
    print("✅ M65 测试完成")
    print("=" * 60)
