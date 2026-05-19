# -*- coding: utf-8 -*-
"""
BFTToleranceModule - 拜占庭容错执行层
太乙AGI 5.0 核心模块

基于章锋论文《摘取皇冠上的明珠》中的BFT容错理论：
- 拜占庭将军问题：N ≥ 3f + 1
- 多数派仲裁确保物理可靠性
- 确保AGI在硬件故障/宇宙射线下"不跑偏"
- Lean（逻辑）+ BFT（物理）= 高可靠AGI
"""

import asyncio
import hashlib
import time
import random
from typing import Optional, Dict, Any, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import numpy as np


class NodeState(Enum):
    """节点状态"""
    CORRECT = "correct"           # 正常
    BYZANTINE = "byzantine"        # 恶意/故障
    SUSPECTED = "suspected"        # 可疑
    UNKNOWN = "unknown"            # 未知


@dataclass
class ConsensusMessage:
    """共识消息"""
    msg_type: str                  # 'pre-prepare', 'prepare', 'commit'
    view: int                      # 视图编号
    sequence: int                  # 序列号
    digest: str                    # 消息摘要
    sender: int                    # 发送者ID
    timestamp: float = field(default_factory=time.time)


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: int
    address: str
    state: NodeState = NodeState.UNKNOWN
    is_byzantine: bool = False     # 是否是模拟的恶意节点
    Byzantine_fault_rate: float = 0.0  # 故障率（用于模拟）


@dataclass
class ConsensusResult:
    """共识结果"""
    reached: bool
    value: Any = None
    quorum_size: int = 0
    dissenting_nodes: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BFTToleranceModule:
    """
    拜占庭容错执行模块
    
    核心定理（N ≥ 3f + 1）：
    - N: 总节点数
    - f: 可容忍的拜占庭（恶意/故障）节点数
    
    简化PBFT协议流程：
    1. Pre-prepare: 主节点广播提案
    2. Prepare: 所有节点相互通信，确认提案
    3. Commit: 达到2f+1准备后提交
    
    AGI应用场景：
    1. 多节点推理共识
    2. 硬件故障下的可靠执行
    3. 防止宇宙射线导致比特翻转
    4. 关键决策的分布式验证
    """
    
    def __init__(self, 
                 total_nodes: int = 7,
                 max_byzantine: Optional[int] = None,
                 consensus_threshold: float = 0.66):
        """
        初始化BFT模块
        
        Args:
            total_nodes: 总节点数N
            max_byzantine: 最大可容忍故障数f（如果为None则自动计算）
            consensus_threshold: 共识阈值
        """
        # 验证N ≥ 3f + 1
        if max_byzantine is None:
            max_byzantine = (total_nodes - 1) // 3
        
        self.N = total_nodes
        self.f = max_byzantine
        
        assert total_nodes >= 3 * max_byzantine + 1, \
            f"N={total_nodes} must satisfy N >= 3f+1={3*max_byzantine+1}"
        
        self.consensus_threshold = consensus_threshold
        self.view = 0
        self.sequence_number = 0
        
        # 初始化节点
        self.nodes: Dict[int, NodeInfo] = {}
        
        # 消息历史 - 在_init_nodes之前定义
        self.message_history: Dict[int, List[ConsensusMessage]] = {}
        self._init_nodes()
        
        # 当前主节点（通常为节点0）
        self.primary_node = 0
        
    def _init_nodes(self):
        """初始化所有节点"""
        for i in range(self.N):
            self.nodes[i] = NodeInfo(
                node_id=i,
                address=f"node_{i}:50051",
                state=NodeState.UNKNOWN
            )
            self.message_history[i] = []
    
    def set_byzantine_nodes(self, byzantine_ids: List[int]):
        """
        设置恶意节点（用于测试）
        
        Args:
            byzantine_ids: 恶意节点ID列表
        """
        for nid in byzantine_ids:
            if nid in self.nodes:
                self.nodes[nid].is_byzantine = True
                self.nodes[nid].state = NodeState.BYZANTINE
    
    async def distributed_inference(self,
                                     query: Any,
                                     inference_func: Callable,
                                     return_distribution: bool = False
                                     ) -> ConsensusResult:
        """
        分布式推理：多节点执行，多数派共识
        
        Args:
            query: 查询/输入
            inference_func: 推理函数（每个节点执行此函数）
            return_distribution: 是否返回结果分布
            
        Returns:
            ConsensusResult对象
        """
        self.sequence_number += 1
        seq = self.sequence_number
        
        # 1. 主节点准备提案
        if self.view == 0:  # 简化：始终使用视图0
            pre_prepare = await self._pre_prepare(query, seq)
        else:
            # 视图变更处理（简化实现）
            pre_prepare = await self._pre_prepare(query, seq)
        
        # 2. 所有节点执行推理
        execution_tasks = []
        for node_id in self.nodes:
            task = self._execute_on_node(node_id, query, inference_func, seq)
            execution_tasks.append(task)
        
        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # 3. 提取有效结果
        valid_results = []
        for node_id, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            valid_results.append((node_id, result))
        
        # 4. 多数派共识
        consensus = self._byzantine_consensus(valid_results)
        
        if return_distribution:
            consensus.metadata['distribution'] = {
                node_id: str(result)[:50] 
                for node_id, result in valid_results
            }
        
        return consensus
    
    async def _pre_prepare(self, query: Any, sequence: int) -> Dict[str, Any]:
        """
        Pre-prepare阶段：主节点广播提案
        
        Args:
            query: 查询
            sequence: 序列号
            
        Returns:
            Pre-prepare消息
        """
        digest = self._compute_digest(query)
        
        msg = ConsensusMessage(
            msg_type='pre-prepare',
            view=self.view,
            sequence=sequence,
            digest=digest,
            sender=self.primary_node
        )
        
        # 主节点记录消息
        self.message_history[self.primary_node].append(msg)
        
        return {
            'query': query,
            'sequence': sequence,
            'digest': digest,
            'view': self.view
        }
    
    async def _execute_on_node(self,
                                node_id: int,
                                query: Any,
                                inference_func: Callable,
                                sequence: int) -> Any:
        """
        在单个节点上执行推理
        
        Args:
            node_id: 节点ID
            query: 查询
            inference_func: 推理函数
            sequence: 序列号
            
        Returns:
            执行结果
        """
        node = self.nodes[node_id]
        
        # 模拟网络延迟
        await asyncio.sleep(random.uniform(0.001, 0.01))
        
        # 恶意节点行为
        if node.is_byzantine:
            # 返回错误/随机结果
            if random.random() < 0.7:  # 70%概率返回错误结果
                return f"BYZANTINE_RESULT_{node_id}"
            else:
                # 有时也返回正确结果以增加混乱
                pass
        
        # 正常执行
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, inference_func, query
            )
            return result
        except Exception as e:
            # 节点执行失败
            raise e
    
    def _byzantine_consensus(self, 
                              results: List[Tuple[int, Any]]) -> ConsensusResult:
        """
        拜占庭容错共识
        
        基于结果分布找出多数派
        
        Args:
            results: (node_id, result)列表
            
        Returns:
            ConsensusResult对象
        """
        if not results:
            return ConsensusResult(
                reached=False,
                error="No valid results"
            )
        
        # 将结果哈希化以便比较
        result_hashes = [(node_id, self._compute_digest(result)) 
                          for node_id, result in results]
        
        # 统计哈希分布
        hash_counts = Counter(h for _, h in result_hashes)
        
        # 找出多数派（≥ 2f + 1）
        quorum_size = 2 * self.f + 1
        
        for result_hash, count in hash_counts.most_common():
            if count >= quorum_size:
                # 找到多数派
                majority_result = None
                dissenting_nodes = []
                
                for node_id, h in result_hashes:
                    if h == result_hash:
                        if majority_result is None:
                            # 找到对应的原始结果
                            for nid, result in results:
                                if nid == node_id:
                                    majority_result = result
                                    break
                    else:
                        dissenting_nodes.append(node_id)
                
                return ConsensusResult(
                    reached=True,
                    value=majority_result,
                    quorum_size=count,
                    dissenting_nodes=dissenting_nodes,
                    metadata={
                        'total_nodes': self.N,
                        'valid_responses': len(results),
                        'quorum_required': quorum_size,
                        'byzantine_tolerance': self.f
                    }
                )
        
        # 无共识
        return ConsensusResult(
            reached=False,
            value=None,
            quorum_size=0,
            dissenting_nodes=[nid for nid, _ in results],
            metadata={
                'total_nodes': self.N,
                'valid_responses': len(results),
                'quorum_required': quorum_size,
                'reason': 'No majority reached'
            }
        )
    
    async def fault_tolerant_vote(self,
                                   proposal: Any,
                                   vote_func: Callable[[Any], bool]
                                   ) -> Dict[int, bool]:
        """
        容错投票
        
        每个节点对提案投票，返回投票结果
        
        Args:
            proposal: 提案
            vote_func: 投票函数
            
        Returns:
            投票结果字典
        """
        votes = {}
        
        vote_tasks = []
        for node_id in self.nodes:
            task = self._node_vote(node_id, proposal, vote_func)
            vote_tasks.append(task)
        
        vote_results = await asyncio.gather(*vote_tasks, return_exceptions=True)
        
        for node_id, vote_result in enumerate(vote_results):
            if isinstance(vote_result, Exception):
                votes[node_id] = False  # 失败视为反对
            else:
                votes[node_id] = vote_result
        
        return votes
    
    async def _node_vote(self,
                         node_id: int,
                         proposal: Any,
                         vote_func: Callable) -> bool:
        """节点投票"""
        await asyncio.sleep(random.uniform(0.001, 0.005))
        
        node = self.nodes[node_id]
        
        # 恶意节点随机投票
        if node.is_byzantine:
            return random.choice([True, False])
        
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, vote_func, proposal
            )
        except:
            return False
    
    def check_agreement(self, values: List[Any]) -> bool:
        """
        检查多个节点是否达成一致
        
        Args:
            values: 各节点的值
            
        Returns:
            是否一致
        """
        if len(values) < self.N - self.f:
            return False
        
        value_hashes = [self._compute_digest(v) for v in values]
        hash_counts = Counter(value_hashes)
        
        return any(count >= 2 * self.f + 1 for count in hash_counts.values())
    
    def simulate_radiation_fault(self,
                                 bit_flip_rate: float = 0.01) -> np.ndarray:
        """
        模拟宇宙射线导致的比特翻转
        
        用于测试BFT容错能力
        
        Args:
            bit_flip_rate: 比特翻转率
            
        Returns:
            模拟的数据数组
        """
        # 模拟一个32位整数
        data = np.array([0xFFFFFFFF], dtype=np.uint32)
        
        # 随机翻转一些位
        for _ in range(int(bit_flip_rate * 32)):
            flip_bit = random.randint(0, 31)
            data[0] ^= (1 << flip_bit)
        
        return data
    
    def majority_vote_recovery(self,
                                 samples: List[Any]) -> Any:
        """
        简单多数投票恢复
        
        当数据被宇宙射线破坏时，使用多数投票恢复
        
        Args:
            samples: 多个样本（来自不同节点）
            
        Returns:
            恢复后的值
        """
        if not samples:
            return None
        
        counts = Counter(samples)
        
        # 返回出现最多的值
        return counts.most_common(1)[0][0]
    
    def _compute_digest(self, data: Any) -> str:
        """计算数据摘要"""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def get_bft_diagnostics(self) -> Dict[str, Any]:
        """获取BFT系统诊断信息"""
        byzantine_count = sum(1 for n in self.nodes.values() if n.is_byzantine)
        
        return {
            'total_nodes': self.N,
            'max_byzantine_tolerance': self.f,
            'actual_byzantine': byzantine_count,
            'consensus_threshold': self.consensus_threshold,
            'quorum_size': 2 * self.f + 1,
            'safety_margin': self.N - 3 * self.f,
            'current_view': self.view,
            'sequence_number': self.sequence_number
        }
    
    def reset_consensus_state(self):
        """重置共识状态"""
        self.view = 0
        self.sequence_number = 0
        self.message_history = {i: [] for i in self.nodes}


# 工厂函数
def create_bft_module(total_nodes: int = 7, 
                      max_byzantine: Optional[int] = None) -> BFTToleranceModule:
    """
    创建BFT容错模块
    
    Args:
        total_nodes: 总节点数（建议使用7 = 3*2+1）
        max_byzantine: 最大故障数
        
    Returns:
        BFTToleranceModule实例
    """
    return BFTToleranceModule(total_nodes=total_nodes, max_byzantine=max_byzantine)


if __name__ == "__main__":
    print("=" * 60)
    print("BFT拜占庭容错模块 - 测试")
    print("=" * 60)
    
    # 创建模块（7节点，容忍2个故障）
    bft = create_bft_module(total_nodes=7, max_byzantine=2)
    
    print(f"\nBFT配置验证:")
    diag = bft.get_bft_diagnostics()
    for k, v in diag.items():
        print(f"   {k}: {v}")
    
    # 测试分布式推理
    print("\n1. 分布式推理共识测试")
    
    def mock_inference(query):
        """模拟推理函数"""
        return f"Result for '{query}': {len(query)} chars"
    
    async def run_test():
        result = await bft.distributed_inference(
            query="测试查询",
            inference_func=mock_inference
        )
        return result
    
    result = asyncio.run(run_test())
    print(f"   共识达成: {result.reached}")
    print(f"   结果值: {str(result.value)[:50]}")
    print(f"   多数派规模: {result.quorum_size}")
    print(f"   异议节点: {result.dissenting_nodes}")
    
    # 测试有恶意节点的场景
    print("\n2. 恶意节点场景测试")
    
    bft2 = create_bft_module(total_nodes=7, max_byzantine=2)
    bft2.set_byzantine_nodes([3, 4])  # 设置2个恶意节点
    
    async def run_byzantine_test():
        result = await bft2.distributed_inference(
            query="恶意测试",
            inference_func=mock_inference
        )
        return result
    
    result2 = asyncio.run(run_byzantine_test())
    print(f"   共识达成: {result2.reached}")
    print(f"   容忍恶意节点: {bft2.f}")
    print(f"   有效响应数: {result2.metadata.get('valid_responses', 'N/A')}")
    
    # 测试多数投票恢复
    print("\n3. 多数投票恢复测试")
    samples = ["A", "A", "B", "A", "A"]  # 多数是A
    recovered = bft.majority_vote_recovery(samples)
    print(f"   样本: {samples}")
    print(f"   恢复结果: {recovered}")
    
    # 模拟比特翻转
    print("\n4. 宇宙射线比特翻转模拟")
    original = 0xDEADBEEF
    flipped = bft.simulate_radiation_fault(bit_flip_rate=0.05)
    print(f"   原始: 0x{original:08X}")
    print(f"   翻转后: 0x{int(flipped[0]):08X}")
    
    print("\n" + "=" * 60)
    print("BFT模块测试完成")
    print("=" * 60)
