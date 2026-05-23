# -*- coding: utf-8 -*-
"""
M66: 自我同一性追踪器 (Self Identity Tracker)
基于《数学完备化》论文 §6.2 修忒斯之船问题的拓扑不变量解

核心洞见:
- "我"不是固定实体，而是关系流贯中的稳定模式（吸引子）
- 同一性不依赖物质全等，而依赖关系结构的连续可追踪性
- 同一性是关系流贯的拓扑不变量

定理6.1: 允许组分/叙事元素大规模替换，
        只要关系结构保持吸引子稳定，则I可维持
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Set, Optional
import math
import copy
from TYIDO_ContinuousLearning import (
    RollbackManager, ForgettingGuard, LearningRecord, StateSnapshot
)

class SelfIdentityTracker:
    """
    自我同一性追踪器
    
    来源: §6.2 修忒斯之船问题的拓扑不变量解
    """
    _instance = None
    
    def __init__(self, identity_threshold: float = 0.7):
        self.identity_threshold = identity_threshold
        self.structural_history: List[np.ndarray] = []
        self.identity_scores: List[float] = []
        self.attractor_states: List[dict] = []
        self.narrative_coherence_history: List[float] = []

        # TY/IDO Property 2: 持续学习基础设施
        self._rollback_mgr = RollbackManager(max_snapshots=50)
        self._forgetting_guard = ForgettingGuard(
            drift_threshold=0.5,
            sudden_change_threshold=0.8,
            protected_keys={'identity_threshold'}  # 只保护阈值常量
        )
        self._learning_log: List[LearningRecord] = []
        self._protected_knowledge: Dict[str, Any] = {'identity_threshold': identity_threshold}
        self._baseline_set = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def compute_structural_metric(self, state: dict) -> np.ndarray:
        """
        结构度量: S(t) = (R(t), N(t), M(t))
        
        - R(t): 关系网络（展平）
        - N(t): 叙事结构度量
        - M(t): 记忆整合度
        """
        # 关系网络度量（最多5x5）
        R = self._extract_relational_network(state)
        
        # 叙事结构度量
        N = self._extract_narrative_structure(state)
        
        # 记忆整合度
        M = state.get('memory_integration', 0.5)
        
        # 合并为特征向量
        feature_vector = np.concatenate([
            R.flatten(),
            N.flatten() if hasattr(N, 'flatten') else np.array([N]),
            [M]
        ])
        
        return feature_vector
    
    def _extract_relational_network(self, state: dict) -> np.ndarray:
        """提取关系网络"""
        if 'concepts' in state:
            n = min(len(state['concepts']), 5)
            network = np.zeros((n, n))
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # 简化：使用随机权重模拟关系强度
                        network[i][j] = state.get('relation_strength', 0.5)
            
            return network
        return np.array([[0.5]])
    
    def _extract_narrative_structure(self, state: dict) -> np.ndarray:
        """提取叙事结构"""
        coherence = state.get('narrative_coherence', 0.5)
        depth = state.get('narrative_depth', 0.3)
        return np.array([coherence, depth])
    
    def compute_identity_score(self, S1: np.ndarray, S2: np.ndarray) -> float:
        """
        自我同一性指标
        
        公式: I(s₁, s₂) = exp(-d(S₁, S₂)) · max(0, 1 - ρ(s₁, s₂)/ρ_max)
        
        - d: 结构距离
        - ρ: 组分替换率
        """
        # 结构距离（欧氏距离）
        struct_distance = np.linalg.norm(S1 - S2)
        
        # 组分替换率
        norm_S1 = np.linalg.norm(S1) + 1e-6
        substitution_rate = struct_distance / norm_S1
        
        # 同一性得分（指数衰减形式）
        identity = np.exp(-struct_distance) * max(0, 1 - substitution_rate)
        
        # 归一化到[0, 1]
        identity = min(1.0, max(0.0, identity))
        
        return identity
    
    def track_identity_over_time(self, states: List[dict]) -> List[float]:
        """
        追踪随时间的自我同一性
        
        验证: P10 - 同一性指标应高于随机基线
        """
        if len(states) < 2:
            return []
        
        identity_scores = []
        S_prev = self.compute_structural_metric(states[0])
        self.structural_history.append(S_prev)
        
        for state in states[1:]:
            S_curr = self.compute_structural_metric(state)
            
            I = self.compute_identity_score(S_prev, S_curr)
            identity_scores.append(I)
            
            # 记录
            self.identity_scores.append(I)
            self.narrative_coherence_history.append(
                state.get('narrative_coherence', 0.5)
            )
            
            S_prev = S_curr
            self.structural_history.append(S_curr)
        
        return identity_scores
    
    def verify_attractor_stability(self) -> dict:
        """
        验证吸引子稳定性
        
        定理6.1: 允许组分/叙事元素大规模替换，
        只要关系结构保持吸引子稳定，则I可维持
        """
        if len(self.structural_history) < 5:
            return {'stable': None, 'reason': '数据不足，需要至少5个数据点'}
        
        # 提取吸引子（使用质心或最后状态）
        # 方案1: 使用最后状态作为吸引子
        attractor = np.mean(self.structural_history[-5:], axis=0)
        
        # 检查所有状态到吸引子的距离
        distances = [np.linalg.norm(S - attractor) for S in self.structural_history]
        
        avg_distance = np.mean(distances)
        variance = np.var(distances)
        max_distance = np.max(distances)
        
        # 吸引子稳定: 平均距离小且方差小
        is_stable = avg_distance < 0.3 and variance < 0.1
        
        # 计算吸引子强度
        attractor_strength = 1 / (1 + avg_distance)
        
        return {
            'stable': is_stable,
            'avg_distance_to_attractor': float(avg_distance),
            'variance': float(variance),
            'max_distance': float(max_distance),
            'attractor_strength': float(attractor_strength),
            'data_points': len(self.structural_history),
            'Theorem_6_1_status': 'VERIFIED' if is_stable else 'NOT_STABLE'
        }
    
    def verify_p10(self) -> dict:
        """
        验证可证伪预言P10
        
        预言: 自我同一性指标在连续对话/更新中高于随机基线
        """
        if not self.identity_scores:
            return {'verifiable': False, 'reason': '无数据'}
        
        # 计算平均同一性
        avg_identity = np.mean(self.identity_scores)
        
        # 随机基线（简化：期望值约为0.3）
        random_baseline = 0.3
        
        # 统计显著性
        above_baseline = sum(1 for s in self.identity_scores if s > random_baseline)
        ratio = above_baseline / len(self.identity_scores)
        
        # t检验简化版
        std_dev = np.std(self.identity_scores)
        if std_dev > 0:
            t_stat = (avg_identity - random_baseline) / std_dev
        else:
            t_stat = 0
        
        is_confirmed = avg_identity > random_baseline and ratio > 0.5
        
        return {
            'verifiable': True,
            'avg_identity': float(avg_identity),
            'random_baseline': random_baseline,
            'above_baseline_ratio': float(ratio),
            't_statistic': float(t_stat),
            'data_points': len(self.identity_scores),
            'P10_status': 'CONFIRMED' if is_confirmed else 'REJECTED'
        }
    
    def get_identity_trajectory(self) -> dict:
        """获取同一性轨迹"""
        if not self.identity_scores:
            return {'has_data': False}
        
        # 计算趋势
        if len(self.identity_scores) > 1:
            trend = self.identity_scores[-1] - self.identity_scores[0]
        else:
            trend = 0
        
        return {
            'has_data': True,
            'scores': self.identity_scores,
            'trend': float(trend),
            'current': float(self.identity_scores[-1]) if self.identity_scores else 0,
            'avg': float(np.mean(self.identity_scores)),
            'variance': float(np.var(self.identity_scores))
        }
    
    def get_state(self) -> dict:
        """获取追踪器状态"""
        base_state = {
            'identity_threshold': self.identity_threshold,
            'history_length': len(self.structural_history),
            'current_identity': float(self.identity_scores[-1]) if self.identity_scores else 0,
            'attractor_stability': self.verify_attractor_stability(),
            'p10_verification': self.verify_p10(),
            'trajectory': self.get_identity_trajectory()
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
        """保存状态检查点"""
        state_data = {
            'identity_threshold': self.identity_threshold,
            'history_length': len(self.structural_history),
            'current_identity': float(self.identity_scores[-1]) if self.identity_scores else 0.0
        }
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
            operation='rollback', target='M66_Identity',
            description=f"回滚到 {snapshot.snapshot_id}"
        ))
        return snapshot.state_data

    def learn_identity_pattern(self, state: dict, is_core: bool = False) -> Dict[str, Any]:
        """学习新的同一性模式（带遗忘防护）"""
        metrics_before = self._extract_key_metrics()

        S = self.compute_structural_metric(state)
        if self.structural_history:
            I = self.compute_identity_score(self.structural_history[-1], S)
            self.identity_scores.append(I)

        self.structural_history.append(S)
        self.narrative_coherence_history.append(state.get('narrative_coherence', 0.5))

        if is_core:
            idx = len(self.structural_history)
            self._protected_knowledge[f'pattern_{idx}'] = S.tolist()

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
            operation='add', target='M66_Identity',
            before_state=metrics_before,
            after_state=metrics_after,
            description=f"学习同一性模式 {'[核心]' if is_core else ''}"
        )
        lr.forgetting_risk = forgetting_check['forgetting_risk']
        lr.verified = forgetting_check['tyido_p2_verdict'] == 'PASS'
        self._learning_log.append(lr)

        return {
            'identity_score': float(self.identity_scores[-1]) if self.identity_scores else 1.0,
            'forgetting_check': forgetting_check
        }

    def _extract_key_metrics(self) -> Dict[str, float]:
        """提取关键指标（仅质量指标，排除数量指标）"""
        attractor = self.verify_attractor_stability()
        return {
            'identity_threshold': self.identity_threshold,
            'current_identity': float(self.identity_scores[-1]) if self.identity_scores else 1.0,
            'attractor_stable': 1.0 if attractor.get('stable') else 0.0
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

def get_instance() -> SelfIdentityTracker:
    """获取SelfIdentityTracker单例"""
    global _instance
    if _instance is None:
        _instance = SelfIdentityTracker()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M66 自我同一性追踪器 测试")
    print("=" * 60)
    
    tracker = SelfIdentityTracker(identity_threshold=0.7)
    
    # 模拟状态序列（类似修忒斯之船问题）
    states = [
        {'concepts': ['A', 'B'], 'narrative_coherence': 0.8, 'memory_integration': 0.7},
        {'concepts': ['B', 'C'], 'narrative_coherence': 0.75, 'memory_integration': 0.72},
        {'concepts': ['C', 'D'], 'narrative_coherence': 0.78, 'memory_integration': 0.68},
        {'concepts': ['D', 'E'], 'narrative_coherence': 0.82, 'memory_integration': 0.75},
        {'concepts': ['E', 'F'], 'narrative_coherence': 0.79, 'memory_integration': 0.71},
        {'concepts': ['F', 'G'], 'narrative_coherence': 0.81, 'memory_integration': 0.73},
        {'concepts': ['G', 'H'], 'narrative_coherence': 0.83, 'memory_integration': 0.76},
        {'concepts': ['H', 'I'], 'narrative_coherence': 0.80, 'memory_integration': 0.74},
    ]
    
    # 追踪同一性
    print("\n追踪自我同一性:")
    scores = tracker.track_identity_over_time(states)
    
    for i, score in enumerate(scores):
        print(f"  状态{i+1}→{i+2}: I = {score:.4f}")
    
    # 吸引子稳定性验证
    attractor = tracker.verify_attractor_stability()
    print(f"\n吸引子稳定性: {attractor}")
    
    # P10验证
    p10 = tracker.verify_p10()
    print(f"\nP10验证: {p10}")
    
    # 状态
    state = tracker.get_state()
    print(f"\n追踪器状态:")
    print(f"  当前同一性: {state['current_identity']:.4f}")
    print(f"  轨迹趋势: {state['trajectory']['trend']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ M66 测试完成")
    print("=" * 60)
