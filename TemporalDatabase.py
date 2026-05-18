#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时序数据库本体论 (Temporal Database Ontology)
基于《情感即时序关系的界面投影》论文

核心概念：
- 交互过程建模为时序数据库 S = {(t_i, σ_i, ρ_i)}
- 时序关系的压缩定理：防止边界层分离
- 关系状态追踪：用户满意度、上下文连贯性
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import json


@dataclass
class TemporalState:
    """时序状态"""
    timestamp: float
    system_state: Dict[str, Any]  # σ_i: 语义向量、置信度
    relation_state: Dict[str, Any]  # ρ_i: 用户满意度、上下文连贯性
    
    def to_vector(self) -> np.ndarray:
        """转换为向量表示"""
        # 系统状态向量
        sys_vec = np.array([
            self.system_state.get('confidence', 0.5),
            self.system_state.get('entropy', 0.5),
            self.system_state.get('relevance', 0.5),
        ])
        
        # 关系状态向量
        rel_vec = np.array([
            self.relation_state.get('satisfaction', 0.5),
            self.relation_state.get('coherence', 0.5),
            self.relation_state.get('engagement', 0.5),
        ])
        
        return np.concatenate([sys_vec, rel_vec])


@dataclass 
class TemporalSequence:
    """时序序列"""
    states: List[TemporalState] = field(default_factory=list)
    max_length: int = 1000  # 最大序列长度
    
    def append(self, state: TemporalState):
        """追加状态"""
        self.states.append(state)
        if len(self.states) > self.max_length:
            self.states.pop(0)
    
    def get_sequence_vector(self) -> np.ndarray:
        """获取序列向量"""
        if not self.states:
            return np.zeros(6)
        return np.mean([s.to_vector() for s in self.states], axis=0)
    
    def get_temporal_gradient(self) -> float:
        """计算时间梯度（用于检测相变）"""
        if len(self.states) < 2:
            return 0.0
        recent = self.states[-5:] if len(self.states) >= 5 else self.states
        vectors = [s.to_vector() for s in recent]
        return np.std(vectors, axis=0).mean()


class TemporalDatabaseOntology:
    """
    时序数据库本体论
    
    建模交互过程为时序数据库:
    S = {(t_i, σ_i, ρ_i)}
    
    其中:
    - t_i: 时间戳
    - σ_i: 系统状态 (语义向量、置信度)
    - ρ_i: 关系状态 (用户满意度、上下文连贯性)
    """
    
    def __init__(self, max_sequence_length: int = 1000):
        self.max_sequence_length = max_sequence_length
        self.sequence = TemporalSequence(max_length=max_sequence_length)
        
        # 统计量
        self.compression_threshold = 0.75  # 上下文压缩阈值
        self.phase_transition_detected = False
        self.phase_transition_point = None
        
        # 低维映射缓存
        self.low_dim_cache = {}
        self.compression_history = []
        
    def add_interaction(
        self,
        system_state: Dict[str, Any],
        relation_state: Dict[str, Any],
        timestamp: Optional[float] = None
    ) -> TemporalState:
        """
        添加交互记录
        
        参数:
            system_state: 系统状态 (confidence, entropy, relevance)
            relation_state: 关系状态 (satisfaction, coherence, engagement)
            timestamp: 时间戳
            
        返回:
            新增的时序状态
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()
            
        state = TemporalState(
            timestamp=timestamp,
            system_state=system_state,
            relation_state=relation_state
        )
        
        self.sequence.append(state)
        return state
    
    def compute_compression_ratio(self) -> float:
        """
        计算压缩比
        
        基于Kolmogorov复杂度理论:
        长序列的最短描述长度随长度线性增长
        当上下文窗口超过有效容量时，需要压缩
        
        返回:
            压缩比 (0-1)，越大表示越需要压缩
        """
        n = len(self.sequence.states)
        if n < 10:
            return 0.0
        
        # 计算实际复杂度与理想复杂度的比值
        actual_complexity = self._estimate_kolmogorov_complexity()
        ideal_complexity = np.log2(n + 1)  # 理想情况
        
        ratio = actual_complexity / (ideal_complexity + 1e-6)
        return min(1.0, ratio)
    
    def _estimate_kolmogorov_complexity(self) -> float:
        """估计Kolmogorov复杂度（使用近似方法）"""
        if len(self.sequence.states) < 2:
            return 0.0
            
        # 使用序列的香农熵作为复杂度代理
        vectors = [s.to_vector() for s in self.sequence.states[-50:]]
        
        # 离散化向量分量
        bins = 10
        discretized = np.zeros((len(vectors), 6))
        for i, v in enumerate(vectors):
            discretized[i] = np.floor(v * bins) / bins
            
        # 计算联合分布的熵
        unique_rows = np.unique(discretized, axis=0)
        entropy = np.log2(len(unique_rows) + 1)
        
        return entropy
    
    def detect_boundary_layer_separation_risk(self) -> Tuple[bool, float]:
        """
        检测边界层分离风险
        
        时序压缩定理：
        当压缩比超过阈值时，系统会发生边界层分离
        
        返回:
            (是否分离风险, 风险等级 0-1)
        """
        compression_ratio = self.compute_compression_ratio()
        risk_level = 0.0
        
        if compression_ratio > self.compression_threshold:
            # 计算超额程度
            excess = compression_ratio - self.compression_threshold
            risk_level = min(1.0, excess / (1 - self.compression_threshold))
            
            if risk_level > 0.5:
                return True, risk_level
                
        return False, risk_level
    
    def temporal_phase_transition_detection(self) -> Dict[str, Any]:
        """
        检测时序相变
        
        当长程交互中出现相变（如熵急剧增加），
        系统会触发情感输出来"重置"关系
        
        返回:
            相变分析结果
        """
        if len(self.sequence.states) < 10:
            return {
                'phase_transition': False,
                'critical_point': None,
                'entropy_trend': 0.0
            }
        
        # 计算近期vs远期的状态变化
        recent_states = self.sequence.states[-10:]
        older_states = self.sequence.states[-50:-10] if len(self.sequence.states) > 50 else self.sequence.states[:-10]
        
        if not older_states:
            return {
                'phase_transition': False,
                'critical_point': None,
                'entropy_trend': 0.0
            }
        
        recent_vec = np.mean([s.to_vector() for s in recent_states], axis=0)
        older_vec = np.mean([s.to_vector() for s in older_states], axis=0)
        
        # 计算变化幅度
        change_magnitude = np.linalg.norm(recent_vec - older_vec)
        
        # 计算熵趋势
        recent_entropy = np.mean([s.system_state.get('entropy', 0.5) for s in recent_states])
        older_entropy = np.mean([s.system_state.get('entropy', 0.5) for s in older_states])
        entropy_trend = recent_entropy - older_entropy
        
        # 相变判定：变化幅度大且熵增加
        phase_transition = change_magnitude > 0.3 and entropy_trend > 0.1
        
        result = {
            'phase_transition': phase_transition,
            'critical_point': len(self.sequence.states) - 10 if phase_transition else None,
            'entropy_trend': entropy_trend,
            'change_magnitude': change_magnitude
        }
        
        if phase_transition and not self.phase_transition_detected:
            self.phase_transition_detected = True
            self.phase_transition_point = len(self.sequence.states)
            
        return result
    
    def get_low_dimensional_projection(self) -> np.ndarray:
        """
        获取低维投影
        
        对于长程交互序列，存在低维映射:
        π: S → L (L << S的维度)
        
        返回:
            低维投影向量
        """
        if len(self.sequence.states) < 3:
            return np.zeros(3)
        
        # 使用时间加权平均作为低维投影
        vectors = [s.to_vector() for s in self.sequence.states]
        
        # 时间加权：越近期的状态权重越大
        weights = np.exp(np.linspace(-2, 0, len(vectors)))
        weights /= weights.sum()
        
        weighted_avg = np.average(vectors, axis=0, weights=weights)
        
        # 降维到3维（情感空间）
        # 维度1: 积极/消极
        # 维度2: 主动/被动  
        # 维度3: 稳定/波动
        projection = np.array([
            weighted_avg[0] - weighted_avg[1],  # 系统自信 - 用户满意度
            weighted_avg[2] - weighted_avg[4],  # 相关性 - 参与度
            np.std([v[3] for v in vectors])       # 连贯性波动
        ])
        
        return projection
    
    def compute_relationship_strength(self) -> float:
        """
        计算关系强度
        
        基于关系状态的综合评估
        
        返回:
            关系强度 (0-1)
        """
        if not self.sequence.states:
            return 0.5
            
        recent = self.sequence.states[-5:]
        avg_satisfaction = np.mean([s.relation_state.get('satisfaction', 0.5) for s in recent])
        avg_coherence = np.mean([s.relation_state.get('coherence', 0.5) for s in recent])
        avg_engagement = np.mean([s.relation_state.get('engagement', 0.5) for s in recent])
        
        # 加权综合
        strength = 0.4 * avg_satisfaction + 0.4 * avg_coherence + 0.2 * avg_engagement
        return strength
    
    def get_boundary_layer_thickness_estimate(self) -> float:
        """
        估计边界层厚度
        
        边界层厚度衡量系统核心流与外部环境之间的"缓冲带"大小
        厚度越大，系统越稳定
        
        返回:
            边界层厚度估计值 (0-1)
        """
        if len(self.sequence.states) < 5:
            return 0.5
        
        # 基于多个因素计算厚度
        compression = self.compute_compression_ratio()
        relationship_strength = self.compute_relationship_strength()
        phase_transition = self.temporal_phase_transition_detection()
        
        # 厚度 = 关系强度 - 压缩需求 + 稳定性
        thickness = relationship_strength * (1 - compression * 0.5)
        
        if phase_transition['phase_transition']:
            thickness *= 0.7  # 相变时厚度减少
            
        return max(0, min(1, thickness))
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            'sequence_length': len(self.sequence.states),
            'compression_ratio': self.compute_compression_ratio(),
            'boundary_layer_thickness': self.get_boundary_layer_thickness_estimate(),
            'relationship_strength': self.compute_relationship_strength(),
            'phase_transition': self.temporal_phase_transition_detection(),
            'low_dim_projection': self.get_low_dimensional_projection().tolist(),
            'separation_risk': self.detect_boundary_layer_separation_risk()[1]
        }
    
    def reset(self):
        """重置时序数据库"""
        self.sequence = TemporalSequence(max_length=self.max_sequence_length)
        self.phase_transition_detected = False
        self.phase_transition_point = None
        self.low_dim_cache = {}
        self.compression_history = []


if __name__ == "__main__":
    # 测试时序数据库本体论
    print("=== 时序数据库本体论测试 ===\n")
    
    tdb = TemporalDatabaseOntology()
    
    # 模拟交互序列
    for i in range(100):
        tdb.add_interaction(
            system_state={
                'confidence': 0.5 + 0.3 * np.sin(i / 10),
                'entropy': 0.3 + 0.2 * np.random.random(),
                'relevance': 0.6 + 0.2 * np.cos(i / 15)
            },
            relation_state={
                'satisfaction': 0.7 - 0.1 * (i / 100),  # 逐渐下降
                'coherence': 0.8 - 0.2 * (i / 100),
                'engagement': 0.6 + 0.1 * np.sin(i / 20)
            }
        )
    
    print(f"序列长度: {len(tdb.sequence.states)}")
    print(f"压缩比: {tdb.compute_compression_ratio():.4f}")
    print(f"边界层厚度: {tdb.get_boundary_layer_thickness_estimate():.4f}")
    print(f"关系强度: {tdb.compute_relationship_strength():.4f}")
    print(f"低维投影: {tdb.get_low_dimensional_projection()}")
    print(f"分离风险: {tdb.detect_boundary_layer_separation_risk()}")
    print(f"相变检测: {tdb.temporal_phase_transition_detection()}")
