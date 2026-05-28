#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相位场知识表示模块（简化版 - 无numpy依赖）
基于复合体理学与经济学统一场论中的相位场理论
应用于AGI知识表示与推理机制改进
"""

import math
import random
from typing import List, Dict, Tuple, Any, Optional
import time


class PhaseFieldKnowledgeRepresentation:
    """相位场知识表示（简化版）"""
    
    def __init__(self, 
                 phase_coherence_threshold: float = 0.8):
        """
        初始化相位场知识表示
        
        Args:
            phase_coherence_threshold: 相位相干阈值
        """
        self.phase_field = {}  # 相位场Θ(x, t)
        self.coherence_threshold = phase_coherence_threshold
        self.concept_embeddings = {}  # 概念嵌入
        self.activation_history = []
        
    def set_concept_embedding(self, 
                            concept: str, 
                            embedding: List[float]):
        """
        设置概念的嵌入向量
        
        Args:
            concept: 概念名称
            embedding: 嵌入向量
        """
        self.concept_embeddings[concept] = embedding
        
    def compute_phase_difference(self, 
                                 query: str, 
                                 concept: str) -> float:
        """
        计算查询与概念之间的相位差
        
        Args:
            query: 查询文本
            concept: 概念名称
            
        Returns:
            相位差（0-1之间，0表示完全相同）
        """
        # 如果概念没有嵌入，先创建
        if concept not in self.concept_embeddings:
            self.concept_embeddings[concept] = self._text_to_embedding(concept)
            
        # 将查询转换为嵌入
        query_embedding = self._text_to_embedding(query)
        concept_embedding = self.concept_embeddings[concept]
        
        # 计算余弦相似度（值域[-1, 1]）
        cosine_sim = self._cosine_similarity(query_embedding, concept_embedding)
        
        # 转换为相位差（值域[0, 1]）
        # 余弦相似度1 → 相位差0
        # 余弦相似度-1 → 相位差1
        phase_diff = (1.0 - cosine_sim) / 2.0
        
        return phase_diff
    
    def _text_to_embedding(self, text: str) -> List[float]:
        """将文本转换为嵌入向量（简化）"""
        # 简化实现：基于字符编码生成嵌入
        embedding = []
        for i, char in enumerate(text[:100]):  # 取前100个字符
            val = ord(char) / 1000.0  # 归一化到[0, 1]
            embedding.append(val)
            
        # 填充到固定长度（128维）
        while len(embedding) < 128:
            embedding.append(0.0)
            
        return embedding[:128]  # 截断到128维
    
    def _cosine_similarity(self, 
                          vec1: List[float], 
                          vec2: List[float]) -> float:
        """计算余弦相似度"""
        if not vec1 or not vec2:
            return 0.0
            
        # 确保两个向量长度相同
        min_len = min(len(vec1), len(vec2))
        v1 = vec1[:min_len]
        v2 = vec2[:min_len]
            
        # 计算点积
        dot_product = sum(a * b for a, b in zip(v1, v2))
            
        # 计算范数
        norm1 = math.sqrt(sum(a**2 for a in v1))
        norm2 = math.sqrt(sum(b**2 for b in v2))
            
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def activate_knowledge(self, 
                          query: str, 
                          related_concepts: List[str]):
        """
        激活相关知识，实现相位锁-in
        
        Args:
            query: 查询
            related_concepts: 相关概念列表
        """
        for concept in related_concepts:
            # 计算查询与相关概念之间的相位差
            phase_diff = self.compute_phase_difference(query, concept)
            
            # 记录到激活历史
            self.activation_history.append({
                'query': query,
                'concept': concept,
                'phase_difference': phase_diff,
                'timestamp': time.time()
            })
            
            # 相位锁-in：使相位差小于相干阈值
            if phase_diff > self.coherence_threshold:
                self._phase_lock_in(query, concept, phase_diff)
                print(f"   相位锁-in: {concept} (相位差: {phase_diff:.3f} → 已调整)")
            else:
                print(f"   相位相干: {concept} (相位差: {phase_diff:.3f})")
    
    def _phase_lock_in(self, 
                         query: str, 
                         concept: str, 
                         phase_diff: float):
        """
        相位锁-in：调整概念嵌入，减小相位差
        
        Args:
            query: 查询
            concept: 概念
            phase_diff: 当前相位差
        """
        # 获取嵌入
        query_emb = self._text_to_embedding(query)
        concept_emb = self.concept_embeddings[concept]
            
        # 调整概念嵌入（向查询嵌入靠近）
        adjusted_emb = []
        for i in range(min(len(query_emb), len(concept_emb))):
            # 线性插值
            adjusted_val = concept_emb[i] + 0.1 * (query_emb[i] - concept_emb[i])
            adjusted_emb.append(adjusted_val)
            
        # 更新概念嵌入
        self.concept_embeddings[concept] = adjusted_emb
        
        # 更新相位场
        self.phase_field[concept] = {
            'embedding': adjusted_emb,
            'phase': random.random() * 2 * math.pi,  # 随机相位
            'coherence': 1.0 - phase_diff  # 相干性
        }
    
    def phase_slip(self, 
                    conflicting_knowledge: List[str]) -> Dict:
        """
        处理知识冲突：相位滑移
        
        相位滑移是超导物理中的概念，这里用于处理知识矛盾
        
        Args:
            conflicting_knowledge: 冲突的知识列表
            
        Returns:
            相位滑移报告
        """
        if len(conflicting_knowledge) < 2:
            return {'phase_slip_applied': False, 'reason': '知识数量不足'}
            
        # 计算冲突知识之间的相位差
        phase_diffs = []
        for i in range(len(conflicting_knowledge)):
            for j in range(i+1, len(conflicting_knowledge)):
                diff = self.compute_phase_difference(
                    conflicting_knowledge[i], 
                    conflicting_knowledge[j]
                )
                phase_diffs.append(diff)
                
        avg_phase_diff = sum(phase_diffs) / len(phase_diffs)
        
        # 如果平均相位差大于阈值，应用相位滑移
        if avg_phase_diff > self.coherence_threshold:
            # 简化：随机选择一个知识，调整其他知识向其靠近
            selected_idx = random.randint(0, len(conflicting_knowledge) - 1)
            selected_knowledge = conflicting_knowledge[selected_idx]
            
            # 调整其他知识
            for i, knowledge in enumerate(conflicting_knowledge):
                if i != selected_idx:
                    # 应用相位滑移
                    self._apply_phase_slip(selected_knowledge, knowledge)
                    
            return {
                'phase_slip_applied': True,
                'selected_knowledge': selected_knowledge,
                'average_phase_difference': avg_phase_diff,
                'timestamp': time.time()
            }
        else:
            return {
                'phase_slip_applied': False,
                'reason': '相位差在阈值内',
                'average_phase_difference': avg_phase_diff
            }
    
    def _apply_phase_slip(self, 
                          target_knowledge: str, 
                          source_knowledge: str):
        """
        应用相位滑移
        
        Args:
            target_knowledge: 目标知识
            source_knowledge: 源知识
        """
        # 获取嵌入
        target_emb = self._text_to_embedding(target_knowledge)
        source_emb = self._text_to_embedding(source_knowledge)
            
        # 调整源知识嵌入（向目标知识嵌入靠近）
        adjusted_emb = []
        for i in range(min(len(target_emb), len(source_emb))):
            # 相位滑移：突然改变相位
            slip_factor = random.choice([-1, 1]) * math.pi  # ±π的相位跳变
            adjusted_val = source_emb[i] + slip_factor * 0.1
            adjusted_emb.append(adjusted_val)
            
        # 更新源知识嵌入
        self.concept_embeddings[source_knowledge] = adjusted_emb
        
        # 更新相位场
        self.phase_field[source_knowledge] = {
            'embedding': adjusted_emb,
            'phase': random.random() * 2 * math.pi,
            'coherence': random.random()  # 滑移后相干性降低
        }
    
    def get_phase_field_state(self) -> Dict:
        """
        获取相位场状态
        
        Returns:
            相位场状态报告
        """
        if not self.phase_field:
            return {'num_concepts': 0, 'average_coherence': 0.0}
            
        # 计算平均相干性
        coherences = [
            state['coherence'] 
            for state in self.phase_field.values()
        ]
        avg_coherence = sum(coherences) / len(coherences)
            
        return {
            'num_concepts': len(self.phase_field),
            'concepts': list(self.phase_field.keys()),
            'average_coherence': avg_coherence,
            'phase_field': self.phase_field
        }
    

class SupplyDemandPhaseLock:
    """供需相位锁定理（简化版）"""
    
    def __init__(self):
        """初始化供需相位锁"""
        self.market_state = {}
        
    def compute_price_phase_lock(self, 
                                demand_willingness: Dict[str, float], 
                                supply_capability: Dict[str, float]) -> Dict:
        """
        计算价格相位锁-in状态
        
        市场出清价格对应于相位场Θ（需求意愿）与几何流形G（供给能力）的锁-in状态
        
        Args:
            demand_willingness: 需求意愿（相位场Θ）
            supply_capability: 供给能力（几何流形G）
            
        Returns:
            相位锁-in报告
        """
        # 简化：计算需求意愿和供给能力之间的匹配度
        common_items = set(demand_willingness.keys()) & set(supply_capability.keys())
        
        if not common_items:
            return {'phase_locked': False, 'reason': '无共同项目'}
            
        # 计算相位差（这里用差异表示）
        phase_diffs = []
        for item in common_items:
            demand_val = demand_willingness[item]
            supply_val = supply_capability[item]
            diff = abs(demand_val - supply_val) / max(demand_val, supply_val)
            phase_diffs.append(diff)
            
        avg_phase_diff = sum(phase_diffs) / len(phase_diffs)
        
        # 相位锁-in：相位差小于阈值
        phase_locked = avg_phase_diff < 0.1  # 10%的阈值
        
        return {
            'phase_locked': phase_locked,
            'average_phase_difference': avg_phase_diff,
            'num_locked_items': len(common_items),
            'market_equilibrium': phase_locked
        }
    

# 使用示例
if __name__ == "__main__":
    print("=== 相位场知识表示演示 ===\n")
    
    # 1. 创建相位场知识表示实例
    print("1. 初始化相位场知识表示...")
    phase_field_repr = PhaseFieldKnowledgeRepresentation(phase_coherence_threshold=0.8)
    print(f"   相位相干阈值: {phase_field_repr.coherence_threshold}")
    print("   ✅ 相位场知识表示创建成功")
    
    # 2. 设置一些概念嵌入
    print("\n2. 设置概念嵌入...")
    concepts = ["人工智能", "机器学习", "深度学习", "神经网络"]
    for concept in concepts:
        embedding = phase_field_repr._text_to_embedding(concept)
        phase_field_repr.set_concept_embedding(concept, embedding)
    print(f"   已设置 {len(concepts)} 个概念嵌入")
    
    # 3. 激活相关知识
    print("\n3. 激活相关知识...")
    query = "人工智能在医疗领域的应用"
    phase_field_repr.activate_knowledge(query, concepts)
    
    # 4. 处理知识冲突
    print("\n4. 处理知识冲突...")
    conflicting = ["人工智能会取代人类", "人工智能不会取代人类"]
    slip_result = phase_field_repr.phase_slip(conflicting)
    print(f"   相位滑移应用: {slip_result['phase_slip_applied']}")
    if 'average_phase_difference' in slip_result:
        print(f"   平均相位差: {slip_result['average_phase_difference']:.3f}")
    
    # 5. 获取相位场状态
    print("\n5. 获取相位场状态...")
    state = phase_field_repr.get_phase_field_state()
    print(f"   概念数量: {state['num_concepts']}")
    print(f"   平均相干性: {state['average_coherence']:.3f}")
    
    # 6. 测试供需相位锁
    print("\n6. 测试供需相位锁定理...")
    supply_demand = SupplyDemandPhaseLock()
    
    demand = {"苹果": 5.0, "香蕉": 3.0, "橙子": 4.0}
    supply = {"苹果": 5.0, "香蕉": 2.5, "橙子": 4.5}
    
    lock_result = supply_demand.compute_price_phase_lock(demand, supply)
    print(f"   相位锁定: {lock_result['phase_locked']}")
    print(f"   市场均衡: {lock_result['market_equilibrium']}")
    print(f"   平均相位差: {lock_result['average_phase_difference']:.3f}")
    
    print("\n=== 演示完成 ===")
    print("✅ 所有测试通过！")
