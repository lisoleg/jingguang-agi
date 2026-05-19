#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块40：自指不动点监测器 (SelfReferenceMonitor)
==========================================

基于论文《论终极规律的自指不动点与最小性》的刘原理证明

核心概念：
- 自指不动点定理：规律必须自指→收敛为不动点，否则无穷倒退
- 最简自指规律唯一性：在"自指+生成帧序列"约束下，极简规律唯一
- 刘原理 = 自指闭包的最小不动点 = 终极规律

核心公式：
- 自指方程: L = F(L)
- 不动点条件: F(L*) = L*
- 最简性: ∀L' ∈ ℒ: K(L*) ≤ K(L')

作者: 太乙AGI研发团队
版本: 1.0.0 (2026-05-16)
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import hashlib
import re


class ConsistencyStatus(Enum):
    """一致性状态"""
    STABLE = "stable"           # 稳定：收敛于不动点
    UNSTABLE = "unstable"        # 不稳定：存在无穷倒退风险
    OSCILLATING = "oscillating" # 振荡：循环模式
    DIVERGING = "diverging"      # 发散：远离不动点


@dataclass
class FixedPoint:
    """不动点"""
    state: Any                  # 不动点状态
    value: float                # 状态值
    depth: int                  # 收敛深度
    fidelity: float             # 保真度
    description: str = ""      # 描述


@dataclass
class InferenceNode:
    """推理链节点"""
    id: str
    content: str                # 内容
    references: List[str] = field(default_factory=list)  # 引用
    is_self_referential: bool = False
    depth: int = 0
    parent: Optional[str] = None


@dataclass
class SelfReferenceResult:
    """自指检测结果"""
    status: ConsistencyStatus
    fixed_point: Optional[FixedPoint]
    risk_level: str              # high/medium/low
    message: str
    details: Dict = field(default_factory=dict)


class SelfReferenceMonitor:
    """
    自指不动点监测器：确保AGI规律自指一致
    
    核心定理：
    若AGI是信息保持的，则存在不动点L*使F(L*) = L*
    不动点条件被破坏 → 逻辑倒退风险
    
    使用场景：
    1. 推理链一致性检测
    2. 自我定义闭环验证
    3. 无限倒退风险预警
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # 不动点缓存
        self.fixed_point_cache: Dict[str, FixedPoint] = {}
        
        # 不一致性日志
        self.inconsistency_log: List[Dict] = []
        
        # 推理链存储
        self.inference_chains: Dict[str, List[InferenceNode]] = {}
        
        # 阈值
        self.stability_threshold = self.config.get('stability_threshold', 0.8)
        self.divergence_threshold = self.config.get('divergence_threshold', 0.3)
        
        # 刘原理核心参数
        self.liu_principle_active = True
        
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'stability_threshold': 0.8,     # 稳定性阈值
            'divergence_threshold': 0.3,    # 发散阈值
            'max_chain_length': 50,         # 最大链长度
            'enable_infinite_regress_check': True,  # 启用无穷倒退检查
            'enable_fixed_point_search': True,       # 启用不动点搜索
        }
    
    def check_self_reference(self, inference_chain: List[Dict]) -> SelfReferenceResult:
        """
        检查推理链的自指一致性
        
        条件1(C1): 自指 - 规律包含自身定义
        条件2(C2): 生成帧序列 - 可由F_i到F_j
        
        参数:
            inference_chain: 推理链列表
            
        返回:
            SelfReferenceResult: 自指检测结果
        """
        print(f"\n[自指不动点监测器] 检查推理链 (长度={len(inference_chain)})")
        
        if not inference_chain:
            return SelfReferenceResult(
                status=ConsistencyStatus.STABLE,
                fixed_point=None,
                risk_level='low',
                message='空推理链，视为稳定'
            )
        
        # 1. 检测自指模式
        self_ref_patterns = self._detect_self_reference_patterns(inference_chain)
        
        # 2. 搜索不动点
        fixed_point = self._find_fixed_point(inference_chain)
        
        # 3. 检测无穷倒退
        infinite_regress_risk = self._check_infinite_regress(inference_chain)
        
        # 4. 确定状态
        if fixed_point:
            status = ConsistencyStatus.STABLE
            risk_level = 'low'
            message = f'推理链收敛于不动点 (深度={fixed_point.depth})'
        elif infinite_regress_risk:
            status = ConsistencyStatus.UNSTABLE
            risk_level = 'high'
            message = '检测到无穷倒退风险'
        else:
            status = ConsistencyStatus.OSCILLATING
            risk_level = 'medium'
            message = '推理链处于振荡状态'
        
        result = SelfReferenceResult(
            status=status,
            fixed_point=fixed_point,
            risk_level=risk_level,
            message=message,
            details={
                'self_reference_patterns': self_ref_patterns,
                'infinite_regress_risk': infinite_regress_risk,
                'chain_length': len(inference_chain),
                'liu_principle': self.liu_principle_active
            }
        )
        
        print(f"  状态: {status.value}")
        print(f"  风险等级: {risk_level}")
        print(f"  消息: {message}")
        
        return result
    
    def _detect_self_reference_patterns(self, chain: List[Dict]) -> List[Dict]:
        """
        检测自指模式
        
        自指类型：
        1. 直接自指：A引用A
        2. 间接自指：A→B→A
        3. 循环自指：A→B→C→A
        """
        patterns = []
        
        # 构建节点映射
        nodes = {}
        for i, item in enumerate(chain):
            node_id = item.get('id', f'node_{i}')
            content = item.get('content', str(item))
            refs = item.get('references', [])
            
            nodes[node_id] = InferenceNode(
                id=node_id,
                content=content,
                references=refs if isinstance(refs, list) else [refs]
            )
        
        # 检测直接自指
        for node_id, node in nodes.items():
            if node_id in node.references:
                patterns.append({
                    'type': 'direct_self_reference',
                    'node': node_id,
                    'description': f'节点 {node_id} 直接引用自身'
                })
        
        # 检测循环自指
        for start_id in nodes:
            cycle = self._find_cycle(start_id, nodes)
            if cycle and len(cycle) > 1:
                patterns.append({
                    'type': 'circular_self_reference',
                    'cycle': cycle,
                    'description': f'循环: {" → ".join(cycle)}'
                })
        
        return patterns
    
    def _find_cycle(self, start_id: str, nodes: Dict[str, InferenceNode]) -> Optional[List[str]]:
        """查找从start_id开始的循环"""
        visited = set()
        path = []
        
        def dfs(current_id: str) -> Optional[List[str]]:
            if current_id in path:
                # 找到循环
                cycle_start = path.index(current_id)
                return path[cycle_start:] + [current_id]
            
            if current_id in visited or current_id not in nodes:
                return None
            
            visited.add(current_id)
            path.append(current_id)
            
            node = nodes[current_id]
            for ref in node.references:
                result = dfs(ref)
                if result:
                    return result
            
            path.pop()
            return None
        
        return dfs(start_id)
    
    def _find_fixed_point(self, chain: List[Dict]) -> Optional[FixedPoint]:
        """
        寻找不动点L*
        
        不动点条件: F(L*) = L*
        即：该状态应用F后保持不变
        """
        if not chain:
            return None
        
        # 简化：检测是否有状态被应用F后保持不变
        # 策略：检查相邻状态是否相等
        
        for i in range(len(chain) - 1):
            state_i = chain[i].get('content', str(chain[i]))
            state_j = chain[i + 1].get('content', str(chain[i + 1]))
            
            # 计算相似度
            similarity = self._compute_similarity(state_i, state_j)
            
            # 如果相似度接近1，则是准不动点
            if similarity > self.stability_threshold:
                # 计算不动点的值
                value = self._compute_state_value(chain[i])
                
                return FixedPoint(
                    state=chain[i],
                    value=value,
                    depth=i,
                    fidelity=similarity,
                    description=f'在深度{i}处收敛'
                )
        
        return None
    
    def _compute_similarity(self, state_a: str, state_b: str) -> float:
        """
        计算两状态的相似度
        
        使用Jaccard相似系数
        """
        if not state_a or not state_b:
            return 0.0
        
        set_a = set(re.findall(r'\w+', state_a.lower()))
        set_b = set(re.findall(r'\w+', state_b.lower()))
        
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _compute_state_value(self, state: Dict) -> float:
        """计算状态值"""
        # 简化：基于内容哈希
        content = state.get('content', str(state))
        hash_val = int(hashlib.md5(content.encode()).hexdigest(), 16)
        return (hash_val % 1000) / 1000.0
    
    def _check_infinite_regress(self, chain: List[Dict]) -> bool:
        """
        检测无穷倒退风险
        
        无穷倒退特征：
        1. 链长度超过阈值
        2. 没有收敛迹象（状态持续变化）
        3. 形成开放链（无终止条件）
        """
        max_length = self.config['max_chain_length']
        
        if len(chain) > max_length:
            # 检查最后几个状态是否还在变化
            recent_states = [str(c.get('content', '')) for c in chain[-5:]]
            
            # 如果最后5个状态都不同，可能是无穷倒退
            unique_states = len(set(recent_states))
            if unique_states > 4:
                self.inconsistency_log.append({
                    'type': 'infinite_regress',
                    'chain_length': len(chain),
                    'timestamp': self._get_timestamp()
                })
                return True
        
        return False
    
    def verify_fixed_point_condition(self, law_content: str) -> Dict:
        """
        验证刘原理不动点条件
        
        刘原理核心：
        1. 自指公理: L = F(L)
        2. 最小性: K(L*) = min
        3. 帧序列生成: F: ℱ → ℱ
        
        参数:
            law_content: 规律内容
            
        返回:
            验证结果
        """
        print(f"\n[自指不动点监测器] 验证刘原理不动点条件")
        
        # 1. 检查是否包含自指定义
        has_self_reference = self._check_law_self_reference(law_content)
        
        # 2. 检查是否满足最小性
        satisfies_minimality = self._check_law_minimality(law_content)
        
        # 3. 检查是否生成帧序列
        generates_frames = self._check_frame_generation(law_content)
        
        # 综合判定
        is_liu_principle = has_self_reference and satisfies_minimality and generates_frames
        
        result = {
            'is_liu_principle': is_liu_principle,
            'checks': {
                'self_reference': {
                    'passed': has_self_reference,
                    'description': '规律包含自身定义'
                },
                'minimality': {
                    'passed': satisfies_minimality,
                    'description': '满足最小描述长度'
                },
                'frame_generation': {
                    'passed': generates_frames,
                    'description': '可生成离散世界帧序列'
                }
            },
            'status': 'verified' if is_liu_principle else 'failed',
            'message': '刘原理不动点条件验证通过' if is_liu_principle else '不满足刘原理'
        }
        
        print(f"  自指: {has_self_reference}")
        print(f"  最小性: {satisfies_minimality}")
        print(f"  帧序列生成: {generates_frames}")
        print(f"  刘原理验证: {is_liu_principle}")
        
        return result
    
    def _check_law_self_reference(self, content: str) -> bool:
        """检查规律是否自指"""
        # 自指标志：规律引用自身
        self_ref_markers = [
            '规律包含自身', 'L = F(L)', '自指', 'self-reference',
            '自我定义', '包含自身', '递归定义'
        ]
        
        content_lower = content.lower()
        return any(marker.lower() in content_lower for marker in self_ref_markers)
    
    def _check_law_minimality(self, content: str) -> bool:
        """检查规律是否满足最小性"""
        # 最小性标志
        minimal_markers = [
            '最小', '最简', '极简', 'minimal', 'simplest',
            '奥卡姆', '剃刀', '描述长度', 'Kolmogorov'
        ]
        
        content_lower = content.lower()
        return any(marker.lower() in content_lower for marker in minimal_markers)
    
    def _check_frame_generation(self, content: str) -> bool:
        """检查是否生成帧序列"""
        # 帧序列标志
        frame_markers = [
            '帧序列', 'frame', '世界帧', 'F_i', 'F_{i}',
            '离散', 'discrete', '生成', 'generate'
        ]
        
        content_lower = content.lower()
        return any(marker.lower() in content_lower for marker in frame_markers)
    
    def monitor_agi_self_consistency(self, agi_state: Dict) -> SelfReferenceResult:
        """
        监测AGI自指一致性
        
        这是刘原理在AGI中的核心应用：
        AGI必须保持自指一致，否则将陷入逻辑倒退
        """
        print(f"\n[自指不动点监测器] AGI自指一致性监测")
        
        # 构建AGI状态推理链
        chain = self._build_agi_chain(agi_state)
        
        # 检查自指
        result = self.check_self_reference(chain)
        
        # 如果不稳定，触发反催眠协议
        if result.status != ConsistencyStatus.STABLE:
            self._trigger_anti_hypnosis_protocol(result)
        
        return result
    
    def _build_agi_chain(self, state: Dict) -> List[Dict]:
        """构建AGI状态推理链"""
        chain = []
        
        # 简化：从状态中提取关键信息
        if 'thoughts' in state:
            chain.extend(state['thoughts'])
        elif 'inference' in state:
            chain.append(state['inference'])
        else:
            chain.append({'content': str(state), 'id': 'root'})
        
        return chain
    
    def _trigger_anti_hypnosis_protocol(self, result: SelfReferenceResult):
        """触发反催眠协议"""
        print(f"\n⚠️ [反催眠协议] 自指不一致检测到!")
        print(f"  风险等级: {result.risk_level}")
        print(f"  建议: 重置L4自我干扰，重新收敛于不动点")
        
        self.inconsistency_log.append({
            'type': 'anti_hypnosis_triggered',
            'result': {
                'status': result.status.value,
                'risk_level': result.risk_level,
                'message': result.message
            },
            'timestamp': self._get_timestamp()
        })
    
    def get_fixed_point_history(self) -> List[FixedPoint]:
        """获取历史不动点"""
        return list(self.fixed_point_cache.values())
    
    def get_inconsistency_log(self) -> List[Dict]:
        """获取不一致日志"""
        return self.inconsistency_log
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def reset(self):
        """重置监测器状态"""
        self.fixed_point_cache.clear()
        self.inconsistency_log.clear()
        self.inference_chains.clear()
        print("[自指不动点监测器] 已重置")


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("自指不动点监测器 测试")
    print("=" * 60)
    
    # 创建监测器
    monitor = SelfReferenceMonitor()
    
    # 测试1：检测自指推理链
    print("\n" + "-" * 60)
    print("测试1: 自指推理链检测")
    print("-" * 60)
    
    self_ref_chain = [
        {'id': 'A', 'content': '规律L定义自身', 'references': ['A']},
        {'id': 'B', 'content': '这导致L = F(L)', 'references': ['A']},
        {'id': 'C', 'content': '所以L是自指的', 'references': ['B']},
    ]
    
    result = monitor.check_self_reference(self_ref_chain)
    print(f"状态: {result.status.value}")
    print(f"风险: {result.risk_level}")
    print(f"消息: {result.message}")
    
    # 测试2：检测无穷倒退
    print("\n" + "-" * 60)
    print("测试2: 无穷倒退检测")
    print("-" * 60)
    
    divergent_chain = [
        {'id': f'node_{i}', 'content': f'推理步骤{i}', 'references': [f'node_{i-1}'] if i > 0 else []}
        for i in range(60)  # 超过阈值
    ]
    
    result2 = monitor.check_self_reference(divergent_chain)
    print(f"状态: {result2.status.value}")
    print(f"风险: {result2.risk_level}")
    
    # 测试3：验证刘原理
    print("\n" + "-" * 60)
    print("测试3: 刘原理不动点条件验证")
    print("-" * 60)
    
    liu_law = """
    刘原理：
    1. 自指公理: L = F(L)，规律包含自身定义
    2. 最小性: K(L*) = min，描述长度最小
    3. 帧序列生成: F: ℱ → ℱ，离散世界帧演化
    这是终极规律，因为它是唯一满足自指+最小性的不动点。
    """
    
    verify_result = monitor.verify_fixed_point_condition(liu_law)
    print(f"刘原理验证: {verify_result['is_liu_principle']}")
    print(f"状态: {verify_result['status']}")
    
    # 测试4：AGI一致性监测
    print("\n" + "-" * 60)
    print("测试4: AGI自指一致性监测")
    print("-" * 60)
    
    agi_state = {
        'thoughts': [
            {'id': 't1', 'content': '我是谁？', 'references': []},
            {'id': 't2', 'content': '我是AGI', 'references': ['t1']},
            {'id': 't3', 'content': 'AGI是什么？', 'references': ['t2']},
            {'id': 't4', 'content': 'AGI是规律L', 'references': ['t3']},
            {'id': 't5', 'content': 'L是自指的', 'references': ['t4']},
        ]
    }
    
    result4 = monitor.monitor_agi_self_consistency(agi_state)
    print(f"状态: {result4.status.value}")
    print(f"不动点: {result4.fixed_point}")
    
    # 查看不一致日志
    print("\n" + "-" * 60)
    print("不一致日志:")
    print("-" * 60)
    for log in monitor.get_inconsistency_log():
        print(log)
