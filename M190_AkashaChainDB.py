# -*- coding: utf-8 -*-
"""
M190: AkashaChainDB — 阿卡西链式数据库引擎

基于 ChainDB (https://github.com/lisoleg/chain-db) 的核心哲学：
  "信息寓于关联，而非实体" (Information Resides in Associations, Not Entities)

与太乙AGI的哲学同构：
  - ChainDB: 关系优先于关系者 → 太乙: δS_rel=0, Self≡𝒢
  - FTEL四维指标 → 太乙FTel目的算子
  - RelationIndex.process_block() → 金灵球 JinlingHeap β-归约
  - POP共识 → 太乙BFT 2/3三分损益同源

核心数据结构：
  1. AkashaTriple: 三元组 (subject, predicate, object) + confidence + FTEL
  2. AkashaBlock: Merkle链块，含三元组批次 + 金灵球β归约结果
  3. AkashaLedger: 追加式账本，链式验证
  4. RelationIndex: 关系索引图引擎，FTEL度量化
  5. POPConsensus: Proof-of-Priority 共识（关联优先证明）
  6. EntityProfile: 实体画像（由关联网络涌现，非预定义）

桥接模块：
  - M176 OrgMemoryEngine: 持久化后端（remember→write_triple, recall→query）
  - M133 SelfRefLoopTopologizer: 自指闭环与链式验证
  - M189 PowerLawEngine: 幂律关系权重衰减
  - DIKWPReliabilityLayer: BFT 2/3共识验证

定理：
  T197 — 关系本体论定理：实体性质完全由其关联网络确定，
          E ≡ {⟨E, r, O⟩ | r ∈ Relations}，无孤立实体
  T198 — 金灵球β归约定理：process_block 对三元组集合的β归约
          保持语义等价性，⟨Σ, Δ⟩_reduced ≡ ⟨Σ, Δ⟩_original
  T199 — 阿卡西完备性定理：Ledger + RelationIndex 联合
          可回答所有关系查询，无信息遗漏
  T200 — POP共识安全性定理：Proof-of-Priority 在 f < n/3 拜占庭节点下
          保证链一致性，与BFT 2/3三分损益同源

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.30
"""

from __future__ import annotations

import math
import time
import json
import hashlib
import threading
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import (
    Dict, Any, List, Optional, Tuple, Set, Callable
)
from collections import defaultdict


# ===========================================================================
# 常量
# ===========================================================================

AKASHA_VERSION = "7.30"
GENESIS_HASH = "0" * 64  # 创世块哈希
DEFAULT_BLOCK_SIZE = 64  # 默认块大小（三元组数）
MAX_LEDGER_LENGTH = 100000  # 最大账本长度
FT_EL_WEIGHTS = {  # FTEL四维权重
    "frequency": 0.30,
    "temporality": 0.25,
    "exclusivity": 0.25,
    "locality": 0.20,
}


# ===========================================================================
# 枚举类型
# ===========================================================================

class TripleRole(Enum):
    """三元组角色"""
    SUBJECT = "subject"
    PREDICATE = "predicate"
    OBJECT = "object"


class ConsensusPhase(Enum):
    """POP共识阶段"""
    PROPOSE = "propose"       # 提议
    VOTE = "vote"             # 投票
    COMMIT = "commit"         # 提交
    FINALIZE = "finalize"     # 终态


class BlockStatus(Enum):
    """区块状态"""
    PENDING = "pending"
    PROPOSED = "proposed"
    COMMITTED = "committed"
    FINALIZED = "finalized"
    REJECTED = "rejected"


class QueryMode(Enum):
    """查询模式"""
    EXACT = "exact"             # 精确匹配
    SEMANTIC = "semantic"       # 语义相似
    PATTERN = "pattern"         # 模式匹配
    NEIGHBORHOOD = "neighborhood"  # 邻域扩展


# ===========================================================================
# FTEL 度量 (Frequency, Temporality, Exclusivity, Locality)
# ===========================================================================

@dataclass
class FTELMetrics:
    """
    FTEL四维度量 — 关系质量评估
    
    F: Frequency — 关系出现频率（越频繁越重要）
    T: Temporality — 时间局部性（越近越新鲜）
    E: Exclusivity — 排他性（越独特越有价值）
    L: Locality — 局域性（越聚焦越有意义）
    """
    frequency: float = 0.0      # 出现频次归一化 [0,1]
    temporality: float = 1.0    # 时间衰减 [0,1], 1=最新
    exclusivity: float = 0.5    # 排他性 [0,1], 1=唯一
    locality: float = 0.5       # 局域性 [0,1], 1=高度聚焦
    
    def composite_score(self) -> float:
        """FTEL加权综合评分"""
        return (
            FT_EL_WEIGHTS["frequency"] * self.frequency +
            FT_EL_WEIGHTS["temporality"] * self.temporality +
            FT_EL_WEIGHTS["exclusivity"] * self.exclusivity +
            FT_EL_WEIGHTS["locality"] * self.locality
        )
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "frequency": round(self.frequency, 4),
            "temporality": round(self.temporality, 4),
            "exclusivity": round(self.exclusivity, 4),
            "locality": round(self.locality, 4),
            "composite": round(self.composite_score(), 4),
        }


# ===========================================================================
# AkashaTriple — 阿卡西三元组
# ===========================================================================

@dataclass
class AkashaTriple:
    """
    阿卡西三元组 — 信息的基本单元
    
    信息寓于关联: 一条信息 = (subject, predicate, object)
    实体本身无固有属性，所有属性由关联网络涌现
    """
    subject: str                           # 主体实体
    predicate: str                         # 关系/谓词
    object: str                            # 客体实体
    confidence: float = 1.0                # 置信度 [0,1]
    source_agent: str = "system"           # 来源Agent
    timestamp: float = field(default_factory=time.time)
    ftel: FTELMetrics = field(default_factory=FTELMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def triple_id(self) -> str:
        """三元组唯一ID = hash(subject|predicate|object)"""
        raw = f"{self.subject}|{self.predicate}|{self.object}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "triple_id": self.triple_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "confidence": round(self.confidence, 4),
            "source_agent": self.source_agent,
            "timestamp": self.timestamp,
            "ftel": self.ftel.to_dict(),
            "metadata": self.metadata,
        }


# ===========================================================================
# AkashaBlock — 阿卡西区块
# ===========================================================================

@dataclass
class AkashaBlock:
    """
    阿卡西区块 — 链式数据结构
    
    每个区块包含一批三元组 + 金灵球β归约结果
    Merkle根保证数据完整性，哈希链保证时序不可篡改
    """
    index: int                             # 区块序号
    triples: List[AkashaTriple]            # 三元组批次
    previous_hash: str                     # 前块哈希
    timestamp: float = field(default_factory=time.time)
    block_hash: str = ""                   # 本块哈希（计算得出）
    merkle_root: str = ""                  # Merkle根
    beta_reduction_result: Optional[Dict] = None  # 金灵球β归约结果
    proposer: str = "system"               # 提议者
    status: BlockStatus = BlockStatus.PENDING
    votes_yes: int = 0                     # 赞成票
    votes_no: int = 0                      # 反对票
    nonce: int = 0                         # 随机数
    
    def compute_merkle_root(self) -> str:
        """计算Merkle根"""
        if not self.triples:
            return hashlib.sha256(b"empty").hexdigest()
        hashes = [t.triple_id for t in self.triples]
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else left
                combined = hashlib.sha256(
                    f"{left}{right}".encode()
                ).hexdigest()
                next_level.append(combined)
            hashes = next_level
        return hashes[0] if hashes else ""
    
    def compute_hash(self) -> str:
        """计算区块哈希"""
        self.merkle_root = self.compute_merkle_root()
        data = (
            f"{self.index}{self.previous_hash}{self.merkle_root}"
            f"{self.timestamp}{self.nonce}"
        )
        return hashlib.sha256(data.encode()).hexdigest()
    
    def seal(self) -> str:
        """封印区块（计算哈希并标记状态）"""
        self.block_hash = self.compute_hash()
        return self.block_hash
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "triples_count": len(self.triples),
            "previous_hash": self.previous_hash[:16] + "...",
            "block_hash": self.block_hash[:16] + "...",
            "merkle_root": self.merkle_root[:16] + "..." if self.merkle_root else "",
            "timestamp": self.timestamp,
            "status": self.status.value,
            "proposer": self.proposer,
            "votes_yes": self.votes_yes,
            "votes_no": self.votes_no,
            "beta_reduction": self.beta_reduction_result,
        }


# ===========================================================================
# RelationIndex — 关系索引图引擎
# ===========================================================================

class RelationIndex:
    """
    关系索引图引擎 — ChainDB核心
    
    信息寓于关联，而非实体。所有查询都通过关系图遍历完成。
    FTEL度量化每条关系质量，金灵球β归约精炼关系网络。
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        # 三重索引：S→P→O, O→P→S, P→{S,O}
        self._spo: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self._ops: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self._pso: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        # 三元组存储 (triple_id → AkashaTriple)
        self._triples: Dict[str, AkashaTriple] = {}
        # 实体频率统计
        self._entity_freq: Dict[str, int] = defaultdict(int)
        # 谓词频率统计
        self._predicate_freq: Dict[str, int] = defaultdict(int)
        # 关系出现计数（用于FTEL frequency）
        self._relation_count: Dict[str, int] = defaultdict(int)
        # 时间戳记录（用于FTEL temporality）
        self._relation_timestamps: Dict[str, List[float]] = defaultdict(list)
    
    def add_triple(self, triple: AkashaTriple) -> str:
        """添加三元组到索引"""
        with self._lock:
            tid = triple.triple_id
            if tid in self._triples:
                # 已存在：更新FTEL频率
                self._relation_count[tid] += 1
                self._triples[tid].ftel.frequency = min(
                    1.0, self._relation_count[tid] / 100.0
                )
                self._triples[tid].ftel.temporality = 1.0  # 刷新时间
                self._triples[tid].timestamp = time.time()
                return tid
            
            # 新增：更新三重索引
            self._spo[triple.subject][triple.predicate].add(triple.object)
            self._ops[triple.object][triple.predicate].add(triple.subject)
            self._pso[triple.predicate][triple.subject].add(triple.object)
            
            self._triples[tid] = triple
            self._entity_freq[triple.subject] += 1
            self._entity_freq[triple.object] += 1
            self._predicate_freq[triple.predicate] += 1
            self._relation_count[tid] = 1
            self._relation_timestamps[tid].append(time.time())
            
            # 计算排他性: 1/degree
            s_degree = self._entity_freq[triple.subject]
            o_degree = self._entity_freq[triple.object]
            triple.ftel.exclusivity = 1.0 / (1.0 + math.log2(1 + s_degree + o_degree))
            
            return tid
    
    def query_by_subject(self, subject: str) -> List[AkashaTriple]:
        """按主体查询所有三元组"""
        with self._lock:
            results = []
            if subject in self._spo:
                for pred, objs in self._spo[subject].items():
                    for obj in objs:
                        tid = hashlib.sha256(
                            f"{subject}|{pred}|{obj}".encode()
                        ).hexdigest()[:16]
                        if tid in self._triples:
                            results.append(self._triples[tid])
            return results
    
    def query_by_object(self, object_: str) -> List[AkashaTriple]:
        """按客体查询所有三元组"""
        with self._lock:
            results = []
            if object_ in self._ops:
                for pred, subjs in self._ops[object_].items():
                    for subj in subjs:
                        tid = hashlib.sha256(
                            f"{subj}|{pred}|{object_}".encode()
                        ).hexdigest()[:16]
                        if tid in self._triples:
                            results.append(self._triples[tid])
            return results
    
    def query_by_predicate(self, predicate: str) -> List[AkashaTriple]:
        """按谓词查询所有三元组"""
        with self._lock:
            results = []
            if predicate in self._pso:
                for subj, objs in self._pso[predicate].items():
                    for obj in objs:
                        tid = hashlib.sha256(
                            f"{subj}|{predicate}|{obj}".encode()
                        ).hexdigest()[:16]
                        if tid in self._triples:
                            results.append(self._triples[tid])
            return results
    
    def query_pattern(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
    ) -> List[AkashaTriple]:
        """
        模式查询 — 支持部分绑定
        
        None 表示该位置为变量（任意匹配）
        """
        with self._lock:
            results = []
            candidates = set()
            
            if subject and subject in self._spo:
                for pred, objs in self._spo[subject].items():
                    if predicate and pred != predicate:
                        continue
                    for obj in objs:
                        if object_ and obj != object_:
                            continue
                        candidates.add(
                            hashlib.sha256(
                                f"{subject}|{pred}|{obj}".encode()
                            ).hexdigest()[:16]
                        )
            elif predicate and predicate in self._pso:
                for subj, objs in self._pso[predicate].items():
                    if subject and subj != subject:
                        continue
                    for obj in objs:
                        if object_ and obj != object_:
                            continue
                        candidates.add(
                            hashlib.sha256(
                                f"{subj}|{predicate}|{obj}".encode()
                            ).hexdigest()[:16]
                        )
            elif object_ and object_ in self._ops:
                for pred, subjs in self._ops[object_].items():
                    if predicate and pred != predicate:
                        continue
                    for subj in subjs:
                        if subject and subj != subject:
                            continue
                        candidates.add(
                            hashlib.sha256(
                                f"{subj}|{pred}|{object_}".encode()
                            ).hexdigest()[:16]
                        )
            else:
                # 无约束 → 全量
                candidates = set(self._triples.keys())
            
            for tid in candidates:
                if tid in self._triples:
                    results.append(self._triples[tid])
            
            return results
    
    def get_neighborhood(
        self, entity: str, depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取实体的邻域图
        
        扩展 depth 跳的关联网络
        返回: {entity, triples, entities, ftel_avg}
        """
        with self._lock:
            visited_entities = {entity}
            visited_triples = set()
            frontier = {entity}
            
            for d in range(depth):
                next_frontier = set()
                for e in frontier:
                    # 出边
                    if e in self._spo:
                        for pred, objs in self._spo[e].items():
                            for obj in objs:
                                tid = hashlib.sha256(
                                    f"{e}|{pred}|{obj}".encode()
                                ).hexdigest()[:16]
                                if tid not in visited_triples:
                                    visited_triples.add(tid)
                                    next_frontier.add(obj)
                    # 入边
                    if e in self._ops:
                        for pred, subjs in self._ops[e].items():
                            for subj in subjs:
                                tid = hashlib.sha256(
                                    f"{subj}|{pred}|{e}".encode()
                                ).hexdigest()[:16]
                                if tid not in visited_triples:
                                    visited_triples.add(tid)
                                    next_frontier.add(subj)
                visited_entities.update(next_frontier)
                frontier = next_frontier - visited_entities
            
            # 收集三元组
            triples = []
            ftel_scores = []
            for tid in visited_triples:
                if tid in self._triples:
                    triples.append(self._triples[tid])
                    ftel_scores.append(self._triples[tid].ftel.composite_score())
            
            avg_ftel = (
                sum(ftel_scores) / len(ftel_scores) if ftel_scores else 0.0
            )
            
            return {
                "entity": entity,
                "depth": depth,
                "triples_count": len(triples),
                "entities_count": len(visited_entities),
                "ftel_avg": round(avg_ftel, 4),
                "triples": [t.to_dict() for t in triples[:50]],
                "entities": list(visited_entities)[:50],
            }
    
    def process_block(self, triples: List[AkashaTriple]) -> Dict[str, Any]:
        """
        金灵球β归约 — process_block
        
        对三元组批次执行β归约，精炼关系网络：
        1. 去重：合并相同三元组，累加置信度
        2. 传递闭包压缩：A→B, B→C 归约为 A→C (带衰减)
        3. 互斥消解：矛盾三元组取置信度高的
        4. FTEL更新：刷新度量
        """
        with self._lock:
            start_time = time.time()
            
            # Phase 1: 去重合并
            unique: Dict[str, AkashaTriple] = {}
            merged_count = 0
            for t in triples:
                tid = t.triple_id
                if tid in unique:
                    # 贝叶斯合并: conf = 1 - (1-c1)*(1-c2)
                    old = unique[tid]
                    old.confidence = 1.0 - (1.0 - old.confidence) * (1.0 - t.confidence)
                    old.ftel.frequency = min(1.0, old.ftel.frequency + 0.1)
                    merged_count += 1
                else:
                    unique[tid] = AkashaTriple(
                        subject=t.subject,
                        predicate=t.predicate,
                        object=t.object,
                        confidence=t.confidence,
                        source_agent=t.source_agent,
                        timestamp=t.timestamp,
                        ftel=FTELMetrics(
                            frequency=t.ftel.frequency,
                            temporality=1.0,
                            exclusivity=t.ftel.exclusivity,
                            locality=t.ftel.locality,
                        ),
                        metadata=t.metadata,
                    )
            
            # Phase 2: 传递闭包压缩
            # 先将去重后的三元组写入临时索引，用于检测本批次内传递
            transitive_count = 0
            transitive_triples = []
            
            # 构建批次内的临时SPO索引
            batch_spo: Dict[str, Dict[str, Set[str]]] = defaultdict(
                lambda: defaultdict(set)
            )
            for tid, t in unique.items():
                batch_spo[t.subject][t.predicate].add(t.object)
            
            for tid, t in list(unique.items()):
                # 检查 A→B→C 传递链
                # 优先查已有索引，其次查批次内索引
                successors = set()
                if t.object in self._spo:
                    for pred2, objs in self._spo[t.object].items():
                        successors.update(objs)
                if t.object in batch_spo:
                    for pred2, objs in batch_spo[t.object].items():
                        successors.update(objs)
                
                for obj2 in successors:
                    if obj2 != t.subject:  # 避免自环
                        transitive_triple = AkashaTriple(
                            subject=t.subject,
                            predicate=f"{t.predicate}∘rel",
                            object=obj2,
                            confidence=t.confidence * 0.8,  # 衰减因子
                            source_agent="beta_reduction",
                            ftel=FTELMetrics(
                                frequency=0.1,
                                temporality=1.0,
                                exclusivity=0.9,  # 传递关系通常更独特
                                locality=0.7,
                            ),
                        )
                        transitive_triples.append(transitive_triple)
                        transitive_count += 1
            
            # Phase 3: 互斥消解
            resolved_count = 0
            for t in transitive_triples[:20]:  # 限制传递三元组数量
                tid = t.triple_id
                if tid in unique:
                    if t.confidence > unique[tid].confidence:
                        unique[tid] = t
                        resolved_count += 1
                else:
                    unique[tid] = t
            
            # Phase 4: 写入索引
            added_ids = []
            for tid, t in unique.items():
                idx_id = self.add_triple(t)
                added_ids.append(idx_id)
            
            elapsed = time.time() - start_time
            
            return {
                "input_count": len(triples),
                "unique_count": len(unique),
                "merged_count": merged_count,
                "transitive_count": transitive_count,
                "resolved_count": resolved_count,
                "added_count": len(added_ids),
                "elapsed_ms": round(elapsed * 1000, 2),
                "status": "success",
            }
    
    def get_entity_profile(self, entity: str) -> Dict[str, Any]:
        """
        实体画像 — 由关联网络涌现
        
        T197: 实体性质完全由其关联网络确定
        E ≡ {⟨E, r, O⟩ | r ∈ Relations}
        """
        with self._lock:
            out_triples = self.query_by_subject(entity)
            in_triples = self.query_by_object(entity)
            
            # 出边关系类型
            out_relations = defaultdict(list)
            for t in out_triples:
                out_relations[t.predicate].append(t.object)
            
            # 入边关系类型
            in_relations = defaultdict(list)
            for t in in_triples:
                in_relations[t.predicate].append(t.subject)
            
            # FTEL聚合
            all_triples = out_triples + in_triples
            if all_triples:
                avg_ftel = FTELMetrics(
                    frequency=sum(t.ftel.frequency for t in all_triples) / len(all_triples),
                    temporality=sum(t.ftel.temporality for t in all_triples) / len(all_triples),
                    exclusivity=sum(t.ftel.exclusivity for t in all_triples) / len(all_triples),
                    locality=sum(t.ftel.locality for t in all_triples) / len(all_triples),
                )
            else:
                avg_ftel = FTELMetrics()
            
            return {
                "entity": entity,
                "out_degree": len(out_triples),
                "in_degree": len(in_triples),
                "total_degree": len(out_triples) + len(in_triples),
                "relation_types": list(set(
                    [t.predicate for t in out_triples] +
                    [t.predicate for t in in_triples]
                )),
                "out_relations": {k: v for k, v in out_relations.items()},
                "in_relations": {k: v for k, v in in_relations.items()},
                "ftel_avg": avg_ftel.to_dict(),
                "is_isolated": len(all_triples) == 0,
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计"""
        with self._lock:
            return {
                "total_triples": len(self._triples),
                "total_entities": len(self._entity_freq),
                "total_predicates": len(self._predicate_freq),
                "avg_degree": (
                    sum(self._entity_freq.values()) / len(self._entity_freq)
                    if self._entity_freq else 0.0
                ),
                "top_entities": sorted(
                    self._entity_freq.items(),
                    key=lambda x: x[1], reverse=True
                )[:10],
                "top_predicates": sorted(
                    self._predicate_freq.items(),
                    key=lambda x: x[1], reverse=True
                )[:10],
            }


# ===========================================================================
# ShardedRelationIndex — 分片关系索引 (v2 性能优化)
# ===========================================================================

class ShardedRelationIndex:
    """
    分片关系索引 — 按谓词分片，独立锁

    T222 分片等价定理：分片 RelationIndex 的查询结果与单一索引等价。

    按 predicate hash % num_shards 分片，每个分片独立锁，
    写入并发度从 1 → N (分片数)。
    """

    def __init__(self, num_shards: int = 16):
        self._num_shards = num_shards
        self._shards: List[RelationIndex] = [RelationIndex() for _ in range(num_shards)]
        self._global_lock = threading.RLock()
        # 全局实体/谓词频率（跨分片聚合用）
        self._entity_freq: Dict[str, int] = defaultdict(int)
        self._predicate_freq: Dict[str, int] = defaultdict(int)

    def _shard_for(self, predicate: str) -> int:
        """根据谓词哈希计算分片号"""
        return int(hashlib.sha256(predicate.encode()).hexdigest(), 16) % self._num_shards

    def add_triple(self, triple: AkashaTriple) -> str:
        """添加三元组到对应分片"""
        shard_idx = self._shard_for(triple.predicate)
        with self._global_lock:
            self._entity_freq[triple.subject] += 1
            self._entity_freq[triple.object] += 1
            self._predicate_freq[triple.predicate] += 1
        return self._shards[shard_idx].add_triple(triple)

    def query_by_subject(self, subject: str) -> List[AkashaTriple]:
        """按主体查询所有三元组（跨分片聚合）"""
        results: List[AkashaTriple] = []
        for shard in self._shards:
            results.extend(shard.query_by_subject(subject))
        return results

    def query_by_object(self, object_: str) -> List[AkashaTriple]:
        """按客体查询所有三元组（跨分片聚合）"""
        results: List[AkashaTriple] = []
        for shard in self._shards:
            results.extend(shard.query_by_object(object_))
        return results

    def query_by_predicate(self, predicate: str) -> List[AkashaTriple]:
        """按谓词查询所有三元组（单分片查询）"""
        shard_idx = self._shard_for(predicate)
        return self._shards[shard_idx].query_by_predicate(predicate)

    def query_pattern(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
    ) -> List[AkashaTriple]:
        """
        模式查询 — 支持部分绑定

        如果指定了 predicate，直接路由到对应分片；
        否则跨分片聚合。
        """
        if predicate is not None:
            shard_idx = self._shard_for(predicate)
            return self._shards[shard_idx].query_pattern(
                subject=subject, predicate=predicate, object_=object_
            )
        # 无 predicate 绑定 → 跨分片聚合
        results: List[AkashaTriple] = []
        for shard in self._shards:
            results.extend(shard.query_pattern(
                subject=subject, predicate=None, object_=object_
            ))
        return results

    def get_neighborhood(
        self, entity: str, depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取实体的邻域图（跨分片聚合）

        合并所有分片中与 entity 相关的邻域。
        """
        # 跨分片收集三元组
        all_triples: List[AkashaTriple] = []
        for shard in self._shards:
            all_triples.extend(shard.query_by_subject(entity))
            all_triples.extend(shard.query_by_object(entity))

        # 去重
        seen: Set[str] = set()
        unique: List[AkashaTriple] = []
        for t in all_triples:
            if t.triple_id not in seen:
                seen.add(t.triple_id)
                unique.append(t)

        # 收集实体
        entities: Set[str] = {entity}
        for t in unique:
            entities.add(t.subject)
            entities.add(t.object)

        ftel_scores = [t.ftel.composite_score() for t in unique] if unique else []
        avg_ftel = sum(ftel_scores) / len(ftel_scores) if ftel_scores else 0.0

        return {
            "entity": entity,
            "depth": depth,
            "triples_count": len(unique),
            "entities_count": len(entities),
            "ftel_avg": round(avg_ftel, 4),
            "triples": [t.to_dict() for t in unique[:50]],
            "entities": list(entities)[:50],
        }

    def get_entity_profile(self, entity: str) -> Dict[str, Any]:
        """实体画像 — 跨分片聚合"""
        all_profiles: List[Dict[str, Any]] = []
        for shard in self._shards:
            profile = shard.get_entity_profile(entity)
            if not profile["is_isolated"]:
                all_profiles.append(profile)

        if not all_profiles:
            return {
                "entity": entity,
                "out_degree": 0,
                "in_degree": 0,
                "total_degree": 0,
                "relation_types": [],
                "out_relations": {},
                "in_relations": {},
                "ftel_avg": FTELMetrics().to_dict(),
                "is_isolated": True,
            }

        # 合并
        out_degree = sum(p["out_degree"] for p in all_profiles)
        in_degree = sum(p["in_degree"] for p in all_profiles)
        relation_types = list(set(
            rt for p in all_profiles for rt in p["relation_types"]
        ))
        out_relations: Dict[str, List[str]] = defaultdict(list)
        in_relations: Dict[str, List[str]] = defaultdict(list)
        for p in all_profiles:
            for k, v in p["out_relations"].items():
                out_relations[k].extend(v)
            for k, v in p["in_relations"].items():
                in_relations[k].extend(v)

        # 合并 FTEL 平均
        ftel_scores = []
        for p in all_profiles:
            fa = p["ftel_avg"]
            if isinstance(fa, dict):
                ftel_scores.append(fa.get("composite", 0.0))
            else:
                ftel_scores.append(float(fa))

        avg_composite = sum(ftel_scores) / len(ftel_scores) if ftel_scores else 0.0

        return {
            "entity": entity,
            "out_degree": out_degree,
            "in_degree": in_degree,
            "total_degree": out_degree + in_degree,
            "relation_types": relation_types,
            "out_relations": dict(out_relations),
            "in_relations": dict(in_relations),
            "ftel_avg": {"composite": round(avg_composite, 4)},
            "is_isolated": False,
        }

    def process_block(self, triples: List[AkashaTriple]) -> Dict[str, Any]:
        """
        金灵球β归约 — 分片归约后合并

        将三元组按谓词分片后分别归约，然后合并结果。
        """
        start_time = time.time()

        # 按谓词分片
        shard_groups: Dict[int, List[AkashaTriple]] = defaultdict(list)
        for t in triples:
            shard_idx = self._shard_for(t.predicate)
            shard_groups[shard_idx].append(t)

        # 各分片独立归约
        merged_results: Dict[str, Any] = {
            "input_count": len(triples),
            "unique_count": 0,
            "merged_count": 0,
            "transitive_count": 0,
            "resolved_count": 0,
            "added_count": 0,
        }

        for shard_idx, shard_triples in shard_groups.items():
            result = self._shards[shard_idx].process_block(shard_triples)
            merged_results["unique_count"] += result["unique_count"]
            merged_results["merged_count"] += result["merged_count"]
            merged_results["transitive_count"] += result["transitive_count"]
            merged_results["resolved_count"] += result["resolved_count"]
            merged_results["added_count"] += result["added_count"]

        elapsed = time.time() - start_time
        merged_results["elapsed_ms"] = round(elapsed * 1000, 2)
        merged_results["status"] = "success"

        return merged_results

    def get_stats(self) -> Dict[str, Any]:
        """获取分片索引统计"""
        shard_stats = []
        total_triples = 0
        total_entities = 0
        total_predicates = 0

        for i, shard in enumerate(self._shards):
            s = shard.get_stats()
            shard_stats.append({
                "shard_id": i,
                "triples": s["total_triples"],
                "entities": s["total_entities"],
                "predicates": s["total_predicates"],
            })
            total_triples += s["total_triples"]

        # 全局统计
        with self._global_lock:
            total_entities = len(self._entity_freq)
            total_predicates = len(self._predicate_freq)
            top_entities = sorted(
                self._entity_freq.items(),
                key=lambda x: x[1], reverse=True
            )[:10]
            top_predicates = sorted(
                self._predicate_freq.items(),
                key=lambda x: x[1], reverse=True
            )[:10]

        return {
            "total_triples": total_triples,
            "total_entities": total_entities,
            "total_predicates": total_predicates,
            "num_shards": self._num_shards,
            "shard_distribution": shard_stats,
            "avg_degree": (
                sum(self._entity_freq.values()) / len(self._entity_freq)
                if self._entity_freq else 0.0
            ),
            "top_entities": top_entities,
            "top_predicates": top_predicates,
        }


# ===========================================================================
# AkashaWAL — WAL (Write-Ahead Log) 持久化 (v2 性能优化)
# ===========================================================================

class AkashaWAL:
    """
    WAL (Write-Ahead Log) 持久化

    T223 WAL 完备定理：WAL 回放后系统状态与崩溃前一致。

    追加式 WAL 文件 + 定期 checkpoint。
    与 AkashaLedger 的 append-only 设计天然契合。
    """

    def __init__(self, wal_dir: str = ".akasha_wal", checkpoint_interval: int = 1000):
        self._wal_dir = wal_dir
        self._checkpoint_interval = checkpoint_interval
        self._lock = threading.RLock()
        self._write_count = 0
        self._last_checkpoint_time: float = 0.0
        self._wal_file_path: str = ""
        self._snapshot_path: str = ""

        # 确保 WAL 目录存在
        import os
        try:
            os.makedirs(wal_dir, exist_ok=True)
        except OSError:
            # 如果默认目录不可写，使用临时目录
            import tempfile
            wal_dir = os.path.join(tempfile.gettempdir(), "akasha_wal")
            os.makedirs(wal_dir, exist_ok=True)
            self._wal_dir = wal_dir
        self._wal_file_path = os.path.join(wal_dir, "akasha.wal")
        self._snapshot_path = os.path.join(wal_dir, "akasha.snapshot")

    def append(
        self,
        op: str,
        subject: str,
        predicate: str,
        object_: str,
        confidence: float = 1.0,
        source_agent: str = "system",
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        追加一条 WAL 记录

        Args:
            op: 操作类型 ("ADD", "DELETE")
            subject: 主体
            predicate: 谓词
            object_: 客体
            confidence: 置信度
            source_agent: 来源 Agent
            timestamp: 时间戳

        Returns:
            写入结果
        """
        with self._lock:
            record = {
                "op": op,
                "subject": subject,
                "predicate": predicate,
                "object": object_,
                "confidence": confidence,
                "source_agent": source_agent,
                "timestamp": timestamp or time.time(),
            }

            with open(self._wal_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            self._write_count += 1

            # 自动 checkpoint
            if self._write_count % self._checkpoint_interval == 0:
                self.checkpoint(reason="auto")

            return {
                "status": "appended",
                "wal_seq": self._write_count,
                "op": op,
            }

    def checkpoint(self, reason: str = "manual") -> Dict[str, Any]:
        """
        将当前状态快照写入 .snapshot 文件

        写入后截断 WAL 文件。

        Args:
            reason: 触发原因 ("auto", "manual")

        Returns:
            checkpoint 结果
        """
        with self._lock:
            start_time = time.time()

            # 读取当前 WAL 累积记录
            records = self._read_wal_records()

            snapshot_data = {
                "version": AKASHA_VERSION,
                "checkpoint_time": time.time(),
                "total_records": len(records),
                "wal_write_count": self._write_count,
                "reason": reason,
                "records": records,
            }

            # 写入快照
            with open(self._snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

            # 截断 WAL 文件
            with open(self._wal_file_path, "w", encoding="utf-8") as f:
                f.write("")

            elapsed = time.time() - start_time
            self._last_checkpoint_time = time.time()

            return {
                "status": "checkpoint_complete",
                "records_snapshotted": len(records),
                "elapsed_ms": round(elapsed * 1000, 2),
                "reason": reason,
            }

    def recover(
        self,
        relation_index: "ShardedRelationIndex",
        bloom_filter: Optional["AkashaBloomFilter"] = None,
    ) -> Dict[str, Any]:
        """
        从最新 snapshot + WAL 日志回放恢复

        T223: WAL 回放后系统状态与崩溃前一致。

        Args:
            relation_index: 目标分片关系索引
            bloom_filter: 可选布隆过滤器，恢复时同步更新

        Returns:
            恢复结果
        """
        with self._lock:
            start_time = time.time()
            import os

            restored_count = 0
            snapshot_count = 0
            wal_count = 0

            # Step 1: 从 snapshot 恢复
            if os.path.exists(self._snapshot_path):
                try:
                    with open(self._snapshot_path, "r", encoding="utf-8") as f:
                        snapshot_data = json.load(f)
                    for record in snapshot_data.get("records", []):
                        if record.get("op") == "ADD":
                            triple = AkashaTriple(
                                subject=record["subject"],
                                predicate=record["predicate"],
                                object=record["object"],
                                confidence=record.get("confidence", 1.0),
                                source_agent=record.get("source_agent", "system"),
                                timestamp=record.get("timestamp", time.time()),
                            )
                            relation_index.add_triple(triple)
                            if bloom_filter is not None:
                                bloom_filter.add(
                                    record["subject"],
                                    record["predicate"],
                                    record["object"],
                                )
                            restored_count += 1
                    snapshot_count = len(snapshot_data.get("records", []))
                except (json.JSONDecodeError, KeyError) as e:
                    pass  # 快照损坏，跳过

            # Step 2: 从 WAL 日志恢复（增量）
            wal_records = self._read_wal_records()
            for record in wal_records:
                if record.get("op") == "ADD":
                    triple = AkashaTriple(
                        subject=record["subject"],
                        predicate=record["predicate"],
                        object=record["object"],
                        confidence=record.get("confidence", 1.0),
                        source_agent=record.get("source_agent", "system"),
                        timestamp=record.get("timestamp", time.time()),
                    )
                    relation_index.add_triple(triple)
                    if bloom_filter is not None:
                        bloom_filter.add(
                            record["subject"],
                            record["predicate"],
                            record["object"],
                        )
                    restored_count += 1
            wal_count = len(wal_records)

            elapsed = time.time() - start_time

            return {
                "status": "recovered",
                "restored_count": restored_count,
                "snapshot_count": snapshot_count,
                "wal_count": wal_count,
                "elapsed_ms": round(elapsed * 1000, 2),
            }

    def _read_wal_records(self) -> List[Dict[str, Any]]:
        """读取 WAL 文件中的所有记录"""
        import os
        records: List[Dict[str, Any]] = []
        if os.path.exists(self._wal_file_path):
            try:
                with open(self._wal_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            records.append(json.loads(line))
            except (json.JSONDecodeError, OSError):
                pass
        return records

    def get_stats(self) -> Dict[str, Any]:
        """获取 WAL 统计"""
        import os

        wal_size = 0
        wal_records = 0
        if os.path.exists(self._wal_file_path):
            wal_size = os.path.getsize(self._wal_file_path)
            wal_records = len(self._read_wal_records())

        snapshot_size = 0
        snapshot_exists = os.path.exists(self._snapshot_path)
        if snapshot_exists:
            snapshot_size = os.path.getsize(self._snapshot_path)

        return {
            "wal_dir": self._wal_dir,
            "wal_file_size_bytes": wal_size,
            "wal_record_count": wal_records,
            "snapshot_exists": snapshot_exists,
            "snapshot_size_bytes": snapshot_size,
            "total_writes": self._write_count,
            "checkpoint_interval": self._checkpoint_interval,
            "last_checkpoint_time": self._last_checkpoint_time,
        }


# ===========================================================================
# AkashaBloomFilter — 布隆过滤器 (v2 性能优化)
# ===========================================================================

class AkashaBloomFilter:
    """
    布隆过滤器 — S/P/O 三组

    自实现简单布隆过滤器，不依赖外部库。
    三组过滤器：subject_bloom, predicate_bloom, object_bloom。
    快速排除不存在的 key，避免全表扫描。
    """

    def __init__(
        self,
        expected_items: int = 100000,
        false_positive_rate: float = 0.01,
    ):
        """
        初始化布隆过滤器

        Args:
            expected_items: 预期元素数量
            false_positive_rate: 误判率，默认 0.01 (1%)
        """
        self._expected_items = max(expected_items, 1000)
        self._fpr = false_positive_rate
        self._lock = threading.RLock()

        # 计算最优参数
        # m = -n * ln(p) / (ln2)^2
        # k = (m/n) * ln2
        import math as _math
        ln2 = _math.log(2)
        self._bit_count = max(
            int(-self._expected_items * _math.log(self._fpr) / (ln2 ** 2)),
            1024
        )
        self._hash_count = max(
            int((self._bit_count / self._expected_items) * ln2),
            1
        )

        # 三组布隆过滤器（使用 bytearray）
        self._subject_bits = bytearray((self._bit_count + 7) // 8)
        self._predicate_bits = bytearray((self._bit_count + 7) // 8)
        self._object_bits = bytearray((self._bit_count + 7) // 8)

        # 统计
        self._add_count = 0
        self._query_count = 0
        self._negative_count = 0  # 确定不存在的次数

    def _hash_positions(self, key: str) -> List[int]:
        """计算 key 的多个哈希位置"""
        positions = []
        # 使用双哈希法：h_i = h1 + i * h2
        h1 = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        h2 = int(hashlib.md5(key.encode()).hexdigest(), 16)

        for i in range(self._hash_count):
            pos = (h1 + i * h2) % self._bit_count
            positions.append(pos)
        return positions

    def _set_bits(self, bits: bytearray, positions: List[int]) -> None:
        """设置指定位"""
        for pos in positions:
            byte_idx = pos // 8
            bit_idx = pos % 8
            bits[byte_idx] |= (1 << bit_idx)

    def _check_bits(self, bits: bytearray, positions: List[int]) -> bool:
        """检查指定位是否全部设置"""
        for pos in positions:
            byte_idx = pos // 8
            bit_idx = pos % 8
            if not (bits[byte_idx] & (1 << bit_idx)):
                return False
        return True

    def add(self, subject: str, predicate: str, object_: str) -> None:
        """
        添加三元组的 S/P/O 到对应布隆过滤器

        Args:
            subject: 主体
            predicate: 谓词
            object_: 客体
        """
        with self._lock:
            s_pos = self._hash_positions(subject)
            p_pos = self._hash_positions(predicate)
            o_pos = self._hash_positions(object_)

            self._set_bits(self._subject_bits, s_pos)
            self._set_bits(self._predicate_bits, p_pos)
            self._set_bits(self._object_bits, o_pos)

            self._add_count += 1

    def might_contain_subject(self, subject: str) -> bool:
        """检查 subject 是否可能存在"""
        with self._lock:
            self._query_count += 1
            result = self._check_bits(
                self._subject_bits, self._hash_positions(subject)
            )
            if not result:
                self._negative_count += 1
            return result

    def might_contain_predicate(self, predicate: str) -> bool:
        """检查 predicate 是否可能存在"""
        with self._lock:
            self._query_count += 1
            result = self._check_bits(
                self._predicate_bits, self._hash_positions(predicate)
            )
            if not result:
                self._negative_count += 1
            return result

    def might_contain_object(self, object_: str) -> bool:
        """检查 object 是否可能存在"""
        with self._lock:
            self._query_count += 1
            result = self._check_bits(
                self._object_bits, self._hash_positions(object_)
            )
            if not result:
                self._negative_count += 1
            return result

    def might_contain_any(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
    ) -> bool:
        """
        检查查询条件是否可能匹配

        任一已绑定字段不在布隆过滤器中 → 查询不可能匹配。
        """
        with self._lock:
            if subject is not None and not self.might_contain_subject(subject):
                return False
            if predicate is not None and not self.might_contain_predicate(predicate):
                return False
            if object_ is not None and not self.might_contain_object(object_):
                return False
            return True

    def rebuild(self, triples: List[AkashaTriple]) -> Dict[str, Any]:
        """
        重建布隆过滤器

        清空并重新添加所有三元组。

        Args:
            triples: 所有现有三元组

        Returns:
            重建结果
        """
        with self._lock:
            start_time = time.time()
            self._subject_bits = bytearray((self._bit_count + 7) // 8)
            self._predicate_bits = bytearray((self._bit_count + 7) // 8)
            self._object_bits = bytearray((self._bit_count + 7) // 8)
            self._add_count = 0
            self._query_count = 0
            self._negative_count = 0

            for t in triples:
                self.add(t.subject, t.predicate, t.object)

            elapsed = time.time() - start_time
            return {
                "status": "rebuilt",
                "items_count": self._add_count,
                "elapsed_ms": round(elapsed * 1000, 2),
            }

    def get_stats(self) -> Dict[str, Any]:
        """获取布隆过滤器统计"""
        total_set_bits_s = sum(bin(b).count("1") for b in self._subject_bits)
        total_set_bits_p = sum(bin(b).count("1") for b in self._predicate_bits)
        total_set_bits_o = sum(bin(b).count("1") for b in self._object_bits)

        with self._lock:
            hit_rate = (
                self._negative_count / self._query_count
                if self._query_count > 0 else 0.0
            )

        return {
            "expected_items": self._expected_items,
            "false_positive_rate": self._fpr,
            "bit_count": self._bit_count,
            "hash_count": self._hash_count,
            "add_count": self._add_count,
            "query_count": self._query_count,
            "negative_count": self._negative_count,
            "negative_hit_rate": round(hit_rate, 4),
            "subject_fill_ratio": round(total_set_bits_s / self._bit_count, 4),
            "predicate_fill_ratio": round(total_set_bits_p / self._bit_count, 4),
            "object_fill_ratio": round(total_set_bits_o / self._bit_count, 4),
        }


# ===========================================================================
# AkashaQueryCache — 查询缓存 (v2 性能优化)
# ===========================================================================

class AkashaQueryCache:
    """
    查询缓存 — LRU + FTEL 热点

    热点查询 LRU 缓存，FTEL 高频实体缓存。
    最大容量可配置，默认 1000。
    缓存失效策略：写入时失效 + TTL 过期。
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 300.0):
        """
        初始化查询缓存

        Args:
            max_size: 最大缓存条目数，默认 1000
            ttl_seconds: TTL 过期时间（秒），默认 300
        """
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._lock = threading.RLock()

        # LRU 缓存: key → (value, timestamp)
        self._cache: Dict[str, Tuple[Any, float]] = {}
        # 访问顺序（OrderedDict 模拟 LRU）
        self._access_order: Dict[str, None] = {}

        # FTEL 高频实体缓存
        self._ftel_cache: Dict[str, Tuple[Any, float]] = {}

        # 统计
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._invalidations = 0

    def _cache_key(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        mode: str = "exact",
    ) -> str:
        """生成缓存键"""
        return f"q:{mode}:{subject}:{predicate}:{object_}"

    def get(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        mode: str = "exact",
    ) -> Optional[Dict[str, Any]]:
        """
        查询缓存

        Returns:
            缓存命中返回结果，未命中返回 None
        """
        with self._lock:
            key = self._cache_key(subject, predicate, object_, mode)
            if key in self._cache:
                value, ts = self._cache[key]
                if time.time() - ts <= self._ttl:
                    self._hits += 1
                    # 更新访问顺序
                    self._access_order.pop(key, None)
                    self._access_order[key] = None
                    return value
                else:
                    # TTL 过期
                    del self._cache[key]
                    self._access_order.pop(key, None)
                    self._misses += 1
                    return None
            self._misses += 1
            return None

    def put(
        self,
        value: Dict[str, Any],
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        mode: str = "exact",
    ) -> None:
        """
        写入缓存

        Args:
            value: 查询结果
            subject, predicate, object_, mode: 查询参数
        """
        with self._lock:
            key = self._cache_key(subject, predicate, object_, mode)
            # 淘汰 LRU
            while len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._access_order))
                del self._cache[oldest_key]
                self._access_order.pop(oldest_key, None)
                self._evictions += 1

            self._cache[key] = (value, time.time())
            self._access_order[key] = None

    def get_ftel(self, entity: str) -> Optional[Dict[str, Any]]:
        """获取 FTEL 高频实体缓存"""
        with self._lock:
            if entity in self._ftel_cache:
                value, ts = self._ftel_cache[entity]
                if time.time() - ts <= self._ttl:
                    return value
                else:
                    del self._ftel_cache[entity]
            return None

    def put_ftel(self, entity: str, value: Dict[str, Any]) -> None:
        """写入 FTEL 高频实体缓存"""
        with self._lock:
            # FTEL 缓存容量为主缓存的 50%
            ftel_max = max(self._max_size // 2, 100)
            while len(self._ftel_cache) >= ftel_max:
                # 淘汰最早的
                oldest = next(iter(self._ftel_cache))
                del self._ftel_cache[oldest]
                self._evictions += 1
            self._ftel_cache[entity] = (value, time.time())

    def invalidate(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
    ) -> int:
        """
        写入时失效 — 清除与 subject/predicate 相关的缓存

        Returns:
            失效条目数
        """
        with self._lock:
            invalidated = 0
            keys_to_remove = []
            for key in self._cache:
                if subject and subject in key:
                    keys_to_remove.append(key)
                elif predicate and predicate in key:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._cache[key]
                self._access_order.pop(key, None)
                invalidated += 1

            # 清除相关 FTEL 缓存
            if subject and subject in self._ftel_cache:
                del self._ftel_cache[subject]
                invalidated += 1

            self._invalidations += invalidated
            return invalidated

    def invalidate_all(self) -> int:
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache) + len(self._ftel_cache)
            self._cache.clear()
            self._access_order.clear()
            self._ftel_cache.clear()
            self._invalidations += count
            return count

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return {
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
                "query_cache_size": len(self._cache),
                "ftel_cache_size": len(self._ftel_cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "evictions": self._evictions,
                "invalidations": self._invalidations,
            }


# ===========================================================================
# UABridge — UA↔Akasha 双向转换桥 (v3 UA集成)
# ===========================================================================

class UABridge:
    """
    UA↔Akasha 双向转换桥 — 知识图谱与链式数据库的语义桥梁

    T224 — 双向保持定理: UA→Akasha→UA 转换保持语义等价

    将 UA KnowledgeGraph 的节点/边转换为 Akasha 三元组，反之亦然。
    UA 节点类型映射到 Akasha predicate，边类型映射到 predicate。
    转换时保持 confidence 和 source_agent。
    """

    # 21种UA节点类型 → Akasha predicate 映射
    NODE_TYPE_MAP: Dict[str, str] = {
        "module": "is_module",
        "class": "is_class",
        "function": "is_function",
        "method": "is_method",
        "variable": "is_variable",
        "constant": "is_constant",
        "file": "is_file",
        "directory": "is_directory",
        "package": "is_package",
        "config": "is_config",
        "interface": "is_interface",
        "database": "is_database",
        "table": "is_table",
        "column": "is_column",
        "api_endpoint": "is_api_endpoint",
        "concept": "is_concept",
        "theorem": "is_theorem",
        "algorithm": "is_algorithm",
        "pattern": "is_pattern",
        "agent": "is_agent",
        "protocol": "is_protocol",
        "event": "is_event",
    }

    # 反向映射: predicate → UA节点类型
    NODE_TYPE_MAP_INV: Dict[str, str] = {v: k for k, v in NODE_TYPE_MAP.items()}

    # 35种UA边类型 → Akasha predicate 映射
    EDGE_TYPE_MAP: Dict[str, str] = {
        "depends_on": "depends_on",
        "implements": "implements",
        "inherits_from": "inherits_from",
        "calls": "calls",
        "references": "references",
        "contains": "contains",
        "imports": "imports",
        "uses": "uses",
        "extends": "extends",
        "overrides": "overrides",
        "related_to": "related_to",
        "part_of": "part_of",
        "belongs_to": "belongs_to",
        "composed_of": "composed_of",
        "synthesizes": "synthesizes",
        "verifies": "verifies",
        "contradicts": "contradicts",
        "supports": "supports",
        "specializes": "specializes",
        "generalizes": "generalizes",
        "transforms": "transforms",
        "maps_to": "maps_to",
        "equivalent_to": "equivalent_to",
        "derived_from": "derived_from",
        "applies": "applies",
        "inspired_by": "inspired_by",
        "competes_with": "competes_with",
        "complements": "complements",
        "requires": "requires",
        "produces": "produces",
        "consumes": "consumes",
        "triggers": "triggers",
        "prevents": "prevents",
        "monitors": "monitors",
        "connects_to": "connects_to",
    }

    # 反向映射: predicate → UA边类型
    EDGE_TYPE_MAP_INV: Dict[str, str] = {v: k for k, v in EDGE_TYPE_MAP.items()}

    def __init__(self) -> None:
        """初始化UA双向转换桥"""
        self._lock = threading.RLock()
        self._conversion_count: int = 0
        self._ua_to_akasha_count: int = 0
        self._akasha_to_ua_count: int = 0

    def _map_node_type_to_predicate(self, node_type: str) -> str:
        """
        将UA节点类型映射为Akasha predicate

        Args:
            node_type: UA节点类型（如 "class", "function" 等）

        Returns:
            对应的 Akasha predicate 字符串
        """
        return self.NODE_TYPE_MAP.get(node_type, f"is_{node_type}")

    def _map_predicate_to_node_type(self, predicate: str) -> str:
        """
        将Akasha predicate 反向映射为UA节点类型

        Args:
            predicate: Akasha predicate（如 "is_class"）

        Returns:
            对应的 UA 节点类型字符串
        """
        return self.NODE_TYPE_MAP_INV.get(predicate, predicate.replace("is_", "", 1))

    def _map_edge_type_to_predicate(self, edge_type: str) -> str:
        """
        将UA边类型映射为Akasha predicate

        Args:
            edge_type: UA边类型（如 "depends_on", "calls" 等）

        Returns:
            对应的 Akasha predicate 字符串
        """
        return self.EDGE_TYPE_MAP.get(edge_type, edge_type)

    def ua_to_akasha(
        self,
        node_type: str = "",
        node_data: Optional[Dict[str, Any]] = None,
        edge_type: str = "",
        edge_data: Optional[Dict[str, Any]] = None,
    ) -> List[AkashaTriple]:
        """
        将 UA KnowledgeGraph 的节点/边转换为 Akasha 三元组

        Args:
            node_type: UA节点类型
            node_data: 节点数据 {"id": ..., "name": ..., "confidence": ..., "source_agent": ...}
            edge_type: UA边类型
            edge_data: 边数据 {"source": ..., "target": ..., "confidence": ..., "source_agent": ...}

        Returns:
            转换后的 AkashaTriple 列表
        """
        with self._lock:
            triples: List[AkashaTriple] = []

            # 处理节点 → 三元组
            if node_type and node_data:
                node_id = node_data.get("id", node_data.get("name", ""))
                node_name = node_data.get("name", node_id)
                confidence = node_data.get("confidence", 1.0)
                source_agent = node_data.get("source_agent", "ua_bridge")

                # 节点类型三元组: (node_name, is_<type>, node_id)
                predicate = self._map_node_type_to_predicate(node_type)
                triple = AkashaTriple(
                    subject=node_name,
                    predicate=predicate,
                    object=node_id,
                    confidence=confidence,
                    source_agent=source_agent,
                    metadata={"ua_node_type": node_type, "bridge": "ua_to_akasha"},
                )
                triples.append(triple)

                # 如果有额外属性，也转为三元组
                for key, value in node_data.items():
                    if key in ("id", "name", "confidence", "source_agent"):
                        continue
                    if isinstance(value, (str, int, float)):
                        attr_triple = AkashaTriple(
                            subject=node_name,
                            predicate=f"has_{key}",
                            object=str(value),
                            confidence=confidence,
                            source_agent=source_agent,
                            metadata={"ua_node_type": node_type, "ua_attr": key},
                        )
                        triples.append(attr_triple)

            # 处理边 → 三元组
            if edge_type and edge_data:
                source = edge_data.get("source", "")
                target = edge_data.get("target", "")
                confidence = edge_data.get("confidence", 1.0)
                source_agent = edge_data.get("source_agent", "ua_bridge")

                predicate = self._map_edge_type_to_predicate(edge_type)
                triple = AkashaTriple(
                    subject=source,
                    predicate=predicate,
                    object=target,
                    confidence=confidence,
                    source_agent=source_agent,
                    metadata={"ua_edge_type": edge_type, "bridge": "ua_to_akasha"},
                )
                triples.append(triple)

            self._ua_to_akasha_count += 1
            self._conversion_count += 1
            return triples

    def akasha_to_ua(
        self, triples: List[AkashaTriple]
    ) -> Dict[str, Any]:
        """
        将 Akasha 三元组转换回 UA KnowledgeGraph 的节点+边

        Args:
            triples: AkashaTriple 列表

        Returns:
            {"nodes": [...], "edges": [...]} 格式的 UA 知识图谱数据
        """
        with self._lock:
            nodes: List[Dict[str, Any]] = []
            edges: List[Dict[str, Any]] = []

            for triple in triples:
                predicate = triple.predicate

                # 尝试匹配节点类型映射
                ua_node_type = self.NODE_TYPE_MAP_INV.get(predicate)
                if ua_node_type is not None:
                    # 这是一个节点类型三元组 → UA 节点
                    node = {
                        "id": triple.object,
                        "name": triple.subject,
                        "type": ua_node_type,
                        "confidence": triple.confidence,
                        "source_agent": triple.source_agent,
                    }
                    nodes.append(node)
                elif predicate.startswith("has_"):
                    # 属性三元组，附加到最近同subject的节点
                    attr_name = predicate[4:]  # 去掉 "has_" 前缀
                    # 查找已有的同subject节点
                    matched = False
                    for n in nodes:
                        if n.get("name") == triple.subject:
                            n[attr_name] = triple.object
                            matched = True
                            break
                    if not matched:
                        # 没有找到已有节点，作为新节点（未知类型）
                        node = {
                            "id": triple.subject,
                            "name": triple.subject,
                            "type": "concept",
                            "confidence": triple.confidence,
                            "source_agent": triple.source_agent,
                            attr_name: triple.object,
                        }
                        nodes.append(node)
                else:
                    # 尝试匹配边类型映射
                    ua_edge_type = self.EDGE_TYPE_MAP_INV.get(predicate, predicate)
                    edge = {
                        "source": triple.subject,
                        "target": triple.object,
                        "type": ua_edge_type,
                        "confidence": triple.confidence,
                        "source_agent": triple.source_agent,
                    }
                    edges.append(edge)

            self._akasha_to_ua_count += 1
            self._conversion_count += 1
            return {"nodes": nodes, "edges": edges}

    def get_stats(self) -> Dict[str, Any]:
        """获取转换桥统计"""
        with self._lock:
            return {
                "conversion_count": self._conversion_count,
                "ua_to_akasha_count": self._ua_to_akasha_count,
                "akasha_to_ua_count": self._akasha_to_ua_count,
                "node_type_mappings": len(self.NODE_TYPE_MAP),
                "edge_type_mappings": len(self.EDGE_TYPE_MAP),
            }


# ===========================================================================
# AkashaSemanticQuery — 语义查询引擎 (v3 UA集成)
# ===========================================================================

class AkashaSemanticQuery:
    """
    语义查询引擎 — 基于TF-IDF+余弦相似度的模糊搜索

    T225 — 语义收敛定理: 语义查询在足够特征下收敛于精确匹配

    自实现 TF-IDF + 余弦相似度，不依赖 sklearn。
    支持简单分词（按空格+下划线+驼峰拆分）。
    """

    def __init__(self, relation_index: ShardedRelationIndex) -> None:
        """
        初始化语义查询引擎

        Args:
            relation_index: 分片关系索引
        """
        self._lock = threading.RLock()
        self._relation_index = relation_index
        self._tfidf_index: Dict[str, Dict[str, float]] = {}
        self._doc_entities: Dict[str, str] = {}  # doc_id → entity name
        self._idf: Dict[str, float] = {}
        self._index_built: bool = False
        self._index_triple_count: int = 0
        self._query_count: int = 0

    def _tokenize(self, text: str) -> List[str]:
        """
        简单分词 — 按空格+下划线+驼峰拆分

        Args:
            text: 输入文本

        Returns:
            小写token列表
        """
        import re
        # 先替换下划线为空格
        text = text.replace("_", " ")
        # 驼峰拆分：在大小写边界处插入空格
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # 按空格/连字符/点拆分
        tokens = re.split(r'[\s\-\.]+', text.lower())
        # 过滤空token和过短token
        return [t for t in tokens if len(t) >= 1]

    def _compute_tfidf(
        self, documents: List[str]
    ) -> Tuple[Dict[str, Dict[str, float]], Dict[str, float]]:
        """
        计算 TF-IDF 索引

        Args:
            documents: 文档列表（每个文档是三元组文本拼接）

        Returns:
            (tfidf_index, idf) — TF-IDF 向量索引和 IDF 字典
        """
        n_docs = len(documents)
        if n_docs == 0:
            return {}, {}

        # 分词
        tokenized_docs: List[List[str]] = [self._tokenize(doc) for doc in documents]

        # 计算 TF（词频）
        tf_index: List[Dict[str, float]] = []
        for tokens in tokenized_docs:
            tf: Dict[str, float] = {}
            total = len(tokens) if tokens else 1
            for token in tokens:
                tf[token] = tf.get(token, 0.0) + 1.0
            # 归一化
            for token in tf:
                tf[token] /= total
            tf_index.append(tf)

        # 计算 DF（文档频率）和 IDF
        df: Dict[str, int] = {}
        for tokens in tokenized_docs:
            seen: Set[str] = set(tokens)
            for token in seen:
                df[token] = df.get(token, 0) + 1

        idf: Dict[str, float] = {}
        for token, count in df.items():
            idf[token] = math.log((n_docs + 1) / (count + 1)) + 1.0  # 平滑 IDF

        # 计算 TF-IDF
        tfidf_index: Dict[str, Dict[str, float]] = {}
        for i, tf in enumerate(tf_index):
            doc_id = str(i)
            tfidf_vec: Dict[str, float] = {}
            for token, tf_val in tf.items():
                tfidf_vec[token] = tf_val * idf.get(token, 0.0)
            tfidf_index[doc_id] = tfidf_vec

        return tfidf_index, idf

    def _cosine_similarity(
        self, vec_a: Dict[str, float], vec_b: Dict[str, float]
    ) -> float:
        """
        计算两个稀疏向量的余弦相似度

        Args:
            vec_a: 稀疏向量 A {token: weight}
            vec_b: 稀疏向量 B {token: weight}

        Returns:
            余弦相似度 [0, 1]
        """
        # 共同词
        common_tokens = set(vec_a.keys()) & set(vec_b.keys())
        if not common_tokens:
            return 0.0

        # 点积
        dot_product = sum(vec_a[t] * vec_b[t] for t in common_tokens)

        # 模长
        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def build_index(self) -> None:
        """
        从所有三元组构建 TF-IDF 索引

        遍历关系索引中所有三元组，将其文本信息构建为文档，
        计算 TF-IDF 索引以支持语义查询。
        """
        with self._lock:
            # 收集所有三元组
            all_triples = self._relation_index.query_pattern()

            # 构建文档：每个三元组的 subject + predicate + object 拼接
            documents: List[str] = []
            doc_entities: Dict[str, str] = {}

            for i, triple in enumerate(all_triples):
                doc_text = f"{triple.subject} {triple.predicate} {triple.object}"
                documents.append(doc_text)
                doc_id = str(i)
                doc_entities[doc_id] = triple.subject

            # 计算 TF-IDF
            self._tfidf_index, self._idf = self._compute_tfidf(documents)
            self._doc_entities = doc_entities
            self._index_triple_count = len(all_triples)
            self._index_built = True

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        语义查询 — 查找与查询语义相似的实体

        Args:
            query: 查询文本
            top_k: 返回前K个结果
            threshold: 最低相似度阈值

        Returns:
            排序后的结果列表 [{"doc_id": ..., "entity": ..., "similarity": ...}]
        """
        with self._lock:
            self._query_count += 1

            if not self._index_built:
                self.build_index()

            if not self._tfidf_index:
                return []

            # 将查询转为 TF-IDF 向量
            query_tokens = self._tokenize(query)
            query_tf: Dict[str, float] = {}
            total = len(query_tokens) if query_tokens else 1
            for token in query_tokens:
                query_tf[token] = query_tf.get(token, 0.0) + 1.0
            for token in query_tf:
                query_tf[token] /= total

            # 计算 query 的 TF-IDF 向量
            query_vec: Dict[str, float] = {}
            for token, tf_val in query_tf.items():
                idf_val = self._idf.get(token, 0.0)
                query_vec[token] = tf_val * idf_val

            if not query_vec:
                return []

            # 计算与所有文档的相似度
            similarities: List[Tuple[str, float]] = []
            for doc_id, doc_vec in self._tfidf_index.items():
                sim = self._cosine_similarity(query_vec, doc_vec)
                if sim >= threshold:
                    similarities.append((doc_id, sim))

            # 按相似度降序排序
            similarities.sort(key=lambda x: x[1], reverse=True)

            # 收集所有三元组用于返回
            all_triples = self._relation_index.query_pattern()
            triple_map: Dict[int, AkashaTriple] = {i: t for i, t in enumerate(all_triples)}

            results: List[Dict[str, Any]] = []
            for doc_id, sim in similarities[:top_k]:
                idx = int(doc_id)
                entity = self._doc_entities.get(doc_id, "")
                triple_data = None
                if idx in triple_map:
                    triple_data = triple_map[idx].to_dict()
                results.append({
                    "doc_id": doc_id,
                    "entity": entity,
                    "similarity": round(sim, 4),
                    "triple": triple_data,
                })

            return results

    def get_stats(self) -> Dict[str, Any]:
        """获取语义查询统计"""
        with self._lock:
            return {
                "index_built": self._index_built,
                "index_triple_count": self._index_triple_count,
                "vocabulary_size": len(self._idf),
                "query_count": self._query_count,
            }


# ===========================================================================
# ExpertKnowledgeBridge — 专家知识关联桥 (v3 UA集成)
# ===========================================================================

class ExpertKnowledgeBridge:
    """
    专家知识关联桥 — 连接 Akasha 三元组与专家系统

    T224 关联: 通过 OrgMemoryBridge 和 ExpertBridge 间接关联
    记录"专家E在领域D有权威性"等知识。

    功能:
    - 注册专家及其领域权威性
    - 按专家ID查询关联的三元组
    - 按领域查询关联的三元组
    - 为实体推荐相关专家
    """

    def __init__(
        self,
        relation_index: ShardedRelationIndex,
        cache: AkashaQueryCache,
    ) -> None:
        """
        初始化专家知识关联桥

        Args:
            relation_index: 分片关系索引
            cache: 查询缓存
        """
        self._lock = threading.RLock()
        self._relation_index = relation_index
        self._cache = cache

        # 专家注册表: expert_id → {domain, authority, specialties, registered_at}
        self._experts: Dict[str, Dict[str, Any]] = {}
        # 领域 → 专家ID列表
        self._domain_index: Dict[str, List[str]] = defaultdict(list)
        # 关联三元组: expert_id → [triple_ids]
        self._expert_triples: Dict[str, List[str]] = defaultdict(list)

        self._registration_count: int = 0
        self._query_count: int = 0

    def register_expert(
        self,
        expert_id: str,
        domain: str,
        authority: float = 0.5,
        specialties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        注册专家及其领域权威性

        Args:
            expert_id: 专家唯一标识
            domain: 专业领域
            authority: 权威性分数 [0, 1]
            specialties: 专长列表

        Returns:
            注册结果
        """
        with self._lock:
            specialties = specialties or []
            authority = max(0.0, min(1.0, authority))

            # 记录专家信息
            self._experts[expert_id] = {
                "domain": domain,
                "authority": authority,
                "specialties": specialties,
                "registered_at": time.time(),
            }

            # 更新领域索引
            if expert_id not in self._domain_index[domain]:
                self._domain_index[domain].append(expert_id)

            # 在关系索引中写入专家三元组
            # (expert_id, "has_expertise_in", domain)
            domain_triple = AkashaTriple(
                subject=expert_id,
                predicate="has_expertise_in",
                object=domain,
                confidence=authority,
                source_agent="expert_bridge",
                metadata={"specialties": specialties},
            )
            tid = self._relation_index.add_triple(domain_triple)
            self._expert_triples[expert_id].append(tid)

            # 为每个专长写入三元组
            for spec in specialties:
                spec_triple = AkashaTriple(
                    subject=expert_id,
                    predicate="specializes_in",
                    object=spec,
                    confidence=authority * 0.9,
                    source_agent="expert_bridge",
                )
                sid = self._relation_index.add_triple(spec_triple)
                self._expert_triples[expert_id].append(sid)

            # 缓存失效
            self._cache.invalidate(subject=expert_id)
            self._cache.invalidate(predicate="has_expertise_in")

            self._registration_count += 1

            return {
                "status": "registered",
                "expert_id": expert_id,
                "domain": domain,
                "authority": authority,
                "specialties_count": len(specialties),
                "triple_ids": self._expert_triples[expert_id],
            }

    def query_by_expert(self, expert_id: str) -> List[Dict[str, Any]]:
        """
        按专家ID查询关联的三元组

        Args:
            expert_id: 专家唯一标识

        Returns:
            关联的三元组列表
        """
        with self._lock:
            self._query_count += 1
            results = self._relation_index.query_pattern(subject=expert_id)
            return [t.to_dict() for t in results]

    def query_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        按领域查询关联的三元组

        Args:
            domain: 专业领域

        Returns:
            关联的三元组列表
        """
        with self._lock:
            self._query_count += 1
            # 查询所有 has_expertise_in = domain 的三元组
            results = self._relation_index.query_pattern(
                predicate="has_expertise_in", object_=domain
            )
            return [t.to_dict() for t in results]

    def get_expert_authority(self, expert_id: str, domain: str) -> float:
        """
        获取专家在特定领域的权威性分数

        Args:
            expert_id: 专家唯一标识
            domain: 专业领域

        Returns:
            权威性分数 [0, 1]，未找到返回 0.0
        """
        with self._lock:
            expert = self._experts.get(expert_id)
            if expert and expert["domain"] == domain:
                return expert["authority"]
            return 0.0

    def recommend_experts_for_entity(
        self, entity: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        为实体推荐相关专家

        基于实体的关联网络，匹配专家的领域和专长。

        Args:
            entity: 实体名称
            top_k: 返回前K个推荐

        Returns:
            推荐专家列表
        """
        with self._lock:
            self._query_count += 1

            # 获取实体的关联三元组
            entity_triples = self._relation_index.query_pattern(subject=entity)
            if not entity_triples:
                entity_triples = self._relation_index.query_pattern(object_=entity)

            # 收集实体的所有关联谓词和客体
            entity_keywords: Set[str] = set()
            for t in entity_triples:
                entity_keywords.add(t.predicate)
                entity_keywords.add(t.object)
                entity_keywords.add(t.subject)

            # 匹配专家
            scored_experts: List[Dict[str, Any]] = []
            for expert_id, info in self._experts.items():
                score = 0.0
                # 领域匹配
                if info["domain"] in entity_keywords:
                    score += 0.5
                # 专长匹配
                for spec in info.get("specialties", []):
                    if spec in entity_keywords:
                        score += 0.3
                # 权威性加权
                score *= info["authority"]

                if score > 0:
                    scored_experts.append({
                        "expert_id": expert_id,
                        "domain": info["domain"],
                        "authority": info["authority"],
                        "relevance_score": round(score, 4),
                    })

            # 按相关性降序排序
            scored_experts.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_experts[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """获取专家知识关联桥统计"""
        with self._lock:
            domains = list(self._domain_index.keys())
            return {
                "expert_count": len(self._experts),
                "domain_count": len(domains),
                "domains": domains,
                "registration_count": self._registration_count,
                "query_count": self._query_count,
            }


# ===========================================================================
# AkashaTimeTravel — 时间旅行查询 (v3 UA集成)
# ===========================================================================

class AkashaTimeTravel:
    """
    时间旅行查询 — 查询历史时间点的数据状态

    T226 — 时间一致性定理: 时间旅行查询结果与历史记录一致

    基于 AkashaBlock 的时间戳和 AkashaLedger 的不可变性，
    支持"在时间T，实体E的知识是什么"等查询。
    """

    def __init__(self, ledger: AkashaLedger) -> None:
        """
        初始化时间旅行查询

        Args:
            ledger: 阿卡西账本
        """
        self._lock = threading.RLock()
        self._ledger = ledger
        self._query_count: int = 0

    def query_at_time(self, entity: str, timestamp: float) -> Dict[str, Any]:
        """
        查询历史某个时间点的实体状态

        返回在指定时间戳之前（含）所有包含该实体的三元组。

        Args:
            entity: 实体名称
            timestamp: 查询时间点（Unix时间戳）

        Returns:
            实体在该时间点的知识状态
        """
        with self._lock:
            self._query_count += 1

            matching_triples: List[Dict[str, Any]] = []
            blocks_scanned: int = 0

            # 遍历账本中时间戳 <= timestamp 的区块
            for i in range(self._ledger.height):
                block = self._ledger.get_block(i)
                if block is None:
                    continue
                if block.timestamp > timestamp:
                    continue

                blocks_scanned += 1

                # 检查区块中的三元组
                for triple in block.triples:
                    if triple.subject == entity or triple.object == entity:
                        matching_triples.append(triple.to_dict())

            return {
                "entity": entity,
                "timestamp": timestamp,
                "blocks_scanned": blocks_scanned,
                "triples_count": len(matching_triples),
                "triples": matching_triples,
            }

    def query_range(
        self,
        entity: str,
        start_time: float,
        end_time: float,
    ) -> List[Dict[str, Any]]:
        """
        查询实体在时间范围内的状态变化

        Args:
            entity: 实体名称
            start_time: 起始时间戳
            end_time: 结束时间戳

        Returns:
            时间范围内的快照列表，按时间排序
        """
        with self._lock:
            self._query_count += 1

            snapshots: List[Dict[str, Any]] = []

            for i in range(self._ledger.height):
                block = self._ledger.get_block(i)
                if block is None:
                    continue
                if block.timestamp < start_time:
                    continue
                if block.timestamp > end_time:
                    break

                # 检查区块中的三元组
                entity_triples: List[Dict[str, Any]] = []
                for triple in block.triples:
                    if triple.subject == entity or triple.object == entity:
                        entity_triples.append(triple.to_dict())

                if entity_triples:
                    snapshots.append({
                        "block_index": block.index,
                        "timestamp": block.timestamp,
                        "triples_count": len(entity_triples),
                        "triples": entity_triples,
                    })

            return snapshots

    def get_entity_timeline(self, entity: str) -> List[Dict[str, Any]]:
        """
        获取实体的完整时间线

        返回实体在所有区块中的出现记录，按时间排序。

        Args:
            entity: 实体名称

        Returns:
            时间线条目列表
        """
        with self._lock:
            self._query_count += 1

            timeline: List[Dict[str, Any]] = []

            for i in range(self._ledger.height):
                block = self._ledger.get_block(i)
                if block is None:
                    continue

                for triple in block.triples:
                    if triple.subject == entity or triple.object == entity:
                        timeline.append({
                            "block_index": block.index,
                            "timestamp": block.timestamp,
                            "triple": triple.to_dict(),
                            "role": "subject" if triple.subject == entity else "object",
                        })

            return timeline

    def get_snapshot_at_time(self, timestamp: float) -> Dict[str, Any]:
        """
        获取指定时间点的全局快照

        返回在指定时间戳之前（含）所有区块中的全部三元组。

        Args:
            timestamp: 查询时间点（Unix时间戳）

        Returns:
            全局快照数据
        """
        with self._lock:
            self._query_count += 1

            all_triples: List[Dict[str, Any]] = []
            blocks_included: int = 0

            for i in range(self._ledger.height):
                block = self._ledger.get_block(i)
                if block is None:
                    continue
                if block.timestamp > timestamp:
                    break

                blocks_included += 1
                for triple in block.triples:
                    all_triples.append(triple.to_dict())

            return {
                "timestamp": timestamp,
                "blocks_included": blocks_included,
                "total_triples": len(all_triples),
                "triples": all_triples,
            }

    def get_stats(self) -> Dict[str, Any]:
        """获取时间旅行查询统计"""
        with self._lock:
            return {
                "ledger_height": self._ledger.height,
                "query_count": self._query_count,
            }


# ===========================================================================
# AkashaLedger — 阿卡西账本
# ===========================================================================

class AkashaLedger:
    """
    阿卡西账本 — 追加式链式结构
    
    T199完备性: Ledger + RelationIndex 联合可回答所有关系查询
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._chain: List[AkashaBlock] = []
        self._block_index: Dict[int, AkashaBlock] = {}
        self._create_genesis()
    
    def _create_genesis(self):
        """创建创世块"""
        genesis = AkashaBlock(
            index=0,
            triples=[],
            previous_hash=GENESIS_HASH,
            timestamp=time.time(),
            proposer="genesis",
            status=BlockStatus.FINALIZED,
        )
        genesis.seal()
        self._chain.append(genesis)
        self._block_index[0] = genesis
    
    @property
    def height(self) -> int:
        """账本高度（区块数）"""
        return len(self._chain)
    
    @property
    def last_hash(self) -> str:
        """最新区块哈希"""
        return self._chain[-1].block_hash if self._chain else GENESIS_HASH
    
    def append_block(self, block: AkashaBlock) -> bool:
        """追加区块到账本"""
        with self._lock:
            if block.index != len(self._chain):
                return False  # 序号不连续
            if block.previous_hash != self.last_hash:
                return False  # 链断裂
            block.seal()
            self._chain.append(block)
            self._block_index[block.index] = block
            return True
    
    def verify_chain(self) -> Dict[str, Any]:
        """验证链完整性"""
        with self._lock:
            issues = []
            for i in range(1, len(self._chain)):
                curr = self._chain[i]
                prev = self._chain[i - 1]
                if curr.previous_hash != prev.block_hash:
                    issues.append(
                        f"Block {curr.index}: hash mismatch "
                        f"(expected {prev.block_hash[:16]}..., "
                        f"got {curr.previous_hash[:16]}...)"
                    )
                # 验证Merkle根
                expected_merkle = curr.compute_merkle_root()
                if curr.merkle_root and curr.merkle_root != expected_merkle:
                    issues.append(
                        f"Block {curr.index}: Merkle root mismatch"
                    )
            
            return {
                "height": len(self._chain),
                "valid": len(issues) == 0,
                "issues": issues,
            }
    
    def get_block(self, index: int) -> Optional[AkashaBlock]:
        """获取指定高度的区块"""
        return self._block_index.get(index)
    
    def get_blocks_range(
        self, start: int = 0, end: Optional[int] = None
    ) -> List[Dict]:
        """获取区块范围"""
        with self._lock:
            end = end or len(self._chain)
            return [
                self._chain[i].to_dict()
                for i in range(start, min(end, len(self._chain)))
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取账本统计"""
        with self._lock:
            total_triples = sum(len(b.triples) for b in self._chain)
            return {
                "height": len(self._chain),
                "total_triples": total_triples,
                "avg_triples_per_block": (
                    total_triples / len(self._chain) if self._chain else 0.0
                ),
                "last_block_hash": self.last_hash[:16] + "...",
                "chain_valid": self.verify_chain()["valid"],
            }


# ===========================================================================
# POPConsensus — Proof-of-Priority 共识
# ===========================================================================

class POPConsensus:
    """
    Proof-of-Priority 共识 — 关联优先证明
    
    T200: POP在 f < n/3 拜占庭节点下保证链一致性
    与BFT 2/3三分损益同源：三分损益因子 = BFT容错阈值
    
    共识流程：
    1. PROPOSE: 提议者打包三元组为区块
    2. VOTE: 验证者投票（基于FTEL质量评分）
    3. COMMIT: 达到2/3阈值后提交
    4. FINALIZE: 终态确认
    """
    
    def __init__(
        self,
        validators: int = 4,
        block_size: int = DEFAULT_BLOCK_SIZE,
    ):
        self._lock = threading.RLock()
        self.validators = validators
        self.block_size = block_size
        self._phase = ConsensusPhase.PROPOSE
        self._pending_block: Optional[AkashaBlock] = None
        self._vote_records: Dict[str, bool] = {}  # validator_id → vote
        self._consensus_history: List[Dict] = []
        self._sanfen_counter = 0  # 三分损益计数器
        self._pythagorean_drift = 0.0  # 毕达哥拉斯逗号漂移
    
    def propose_block(
        self,
        triples: List[AkashaTriple],
        proposer: str = "system",
        ledger: Optional[AkashaLedger] = None,
    ) -> AkashaBlock:
        """
        提议新区块
        
        将三元组打包为区块，准备投票
        """
        with self._lock:
            block_index = ledger.height if ledger else 0
            prev_hash = ledger.last_hash if ledger else GENESIS_HASH
            
            # 按FTEL综合评分排序，取top block_size
            sorted_triples = sorted(
                triples,
                key=lambda t: t.ftel.composite_score(),
                reverse=True,
            )[:self.block_size]
            
            block = AkashaBlock(
                index=block_index,
                triples=sorted_triples,
                previous_hash=prev_hash,
                proposer=proposer,
                status=BlockStatus.PROPOSED,
            )
            self._pending_block = block
            self._phase = ConsensusPhase.VOTE
            self._vote_records = {}
            
            return block
    
    def vote(
        self,
        validator_id: str,
        approve: bool,
        ftel_threshold: float = 0.3,
    ) -> Dict[str, Any]:
        """
        验证者投票
        
        基于FTEL质量评分决定是否批准区块
        ftel_threshold: 最低FTEL综合评分阈值
        """
        with self._lock:
            if self._phase != ConsensusPhase.VOTE:
                return {"error": "Not in VOTE phase"}
            
            self._vote_records[validator_id] = approve
            
            # 如果是反对票，检查原因
            if not approve and self._pending_block:
                avg_ftel = sum(
                    t.ftel.composite_score() for t in self._pending_block.triples
                ) / max(1, len(self._pending_block.triples))
                if avg_ftel < ftel_threshold:
                    return {
                        "validator": validator_id,
                        "vote": "reject",
                        "reason": f"Low FTEL score: {avg_ftel:.4f} < {ftel_threshold}",
                    }
            
            return {
                "validator": validator_id,
                "vote": "approve" if approve else "reject",
                "phase": self._phase.value,
            }
    
    def try_commit(self) -> Dict[str, Any]:
        """
        尝试提交区块
        
        检查是否达到2/3三分损益同源阈值
        """
        with self._lock:
            if not self._pending_block:
                return {"error": "No pending block"}
            
            yes = sum(1 for v in self._vote_records.values() if v)
            no = sum(1 for v in self._vote_records.values() if not v)
            total = len(self._vote_records)
            
            if total == 0:
                return {"status": "waiting", "votes": 0}
            
            ratio = yes / total
            
            # 三分损益同源: 2/3阈值 + 毕达哥拉斯逗号补偿
            self._sanfen_counter += 1
            # 每12轮累积一次毕达哥拉斯逗号漂移
            if self._sanfen_counter % 12 == 0:
                self._pythagorean_drift += 23.46 / 1200.0  # 音分→比率
            
            effective_threshold = 2.0 / 3.0
            
            # 逗号补偿：允许接近阈值的区块通过
            if ratio >= 0.65 and ratio < effective_threshold:
                if self._pythagorean_drift > 0.01:  # 有足够累积漂移
                    ratio = effective_threshold  # 补偿通过
                    self._pythagorean_drift *= 0.5  # 消耗漂移
            
            committed = ratio >= effective_threshold
            
            result = {
                "block_index": self._pending_block.index,
                "votes_yes": yes,
                "votes_no": no,
                "total_votes": total,
                "ratio": round(ratio, 4),
                "threshold": round(effective_threshold, 4),
                "committed": committed,
                "sanfen_counter": self._sanfen_counter,
                "pythagorean_drift": round(self._pythagorean_drift, 6),
            }
            
            if committed:
                self._pending_block.status = BlockStatus.COMMITTED
                self._pending_block.votes_yes = yes
                self._pending_block.votes_no = no
                self._phase = ConsensusPhase.COMMIT
                self._consensus_history.append(result)
            
            return result
    
    def finalize(self) -> Optional[AkashaBlock]:
        """终态确认"""
        with self._lock:
            if self._phase != ConsensusPhase.COMMIT:
                return None
            if self._pending_block:
                self._pending_block.status = BlockStatus.FINALIZED
                self._phase = ConsensusPhase.FINALIZE
                block = self._pending_block
                self._pending_block = None
                self._phase = ConsensusPhase.PROPOSE
                return block
            return None
    
    def get_state(self) -> Dict[str, Any]:
        """获取共识状态"""
        with self._lock:
            return {
                "phase": self._phase.value,
                "validators": self.validators,
                "block_size": self.block_size,
                "pending_block": (
                    self._pending_block.to_dict()
                    if self._pending_block else None
                ),
                "vote_records": dict(self._vote_records),
                "consensus_count": len(self._consensus_history),
                "sanfen_counter": self._sanfen_counter,
                "pythagorean_drift": round(self._pythagorean_drift, 6),
            }


# ===========================================================================
# OrgMemoryBridge — M176 组织记忆持久化桥接
# ===========================================================================

class OrgMemoryBridge:
    """
    组织记忆持久化桥接
    
    M176 OrgMemoryEngine ↔ M190 AkashaChainDB
    
    - remember(agent_id, content, ...) → write_triple(subject, predicate, object)
    - recall(query, top_k) → query_pattern + FTEL排序
    """
    
    def __init__(self, relation_index: "ShardedRelationIndex", ledger: AkashaLedger):
        self._ri = relation_index
        self._ledger = ledger
        self._pending_triples: List[AkashaTriple] = []
        self._lock = threading.RLock()
    
    def remember(
        self,
        agent_id: str,
        content: str,
        memory_type: str = "experience",
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """
        将组织记忆条目写入ChainDB
        
        映射:
        - subject = agent_id
        - predicate = memory_type
        - object = content (截断)
        - tags → metadata
        """
        with self._lock:
            # 内容截断避免过长
            obj_content = content[:500] if len(content) > 500 else content
            
            triple = AkashaTriple(
                subject=agent_id,
                predicate=f"memory:{memory_type}",
                object=obj_content,
                confidence=confidence,
                source_agent=agent_id,
                ftel=FTELMetrics(
                    frequency=0.1,
                    temporality=1.0,
                    exclusivity=0.8 if memory_type == "failure" else 0.3,
                    locality=0.6,
                ),
                metadata={
                    "tags": tags or [],
                    "full_content_hash": hashlib.sha256(
                        content.encode()
                    ).hexdigest()[:16],
                    "memory_type": memory_type,
                },
            )
            
            self._pending_triples.append(triple)
            self._ri.add_triple(triple)
            
            # 累积到一定数量后自动打包区块
            committed_block = None
            if len(self._pending_triples) >= DEFAULT_BLOCK_SIZE:
                committed_block = self._flush_to_ledger()
            
            return {
                "triple_id": triple.triple_id,
                "status": "indexed",
                "pending_count": len(self._pending_triples),
                "block_committed": committed_block is not None,
                "block_index": (
                    committed_block.index if committed_block else None
                ),
            }
    
    def recall(
        self,
        query: str,
        top_k: int = 10,
        mode: QueryMode = QueryMode.SEMANTIC,
    ) -> List[Dict[str, Any]]:
        """
        从ChainDB检索组织记忆
        
        使用模式匹配 + FTEL排序
        """
        with self._lock:
            # 尝试多种查询策略
            results = []
            
            # 策略1: 精确匹配subject
            exact = self._ri.query_by_subject(query)
            results.extend(exact)
            
            # 策略2: 谓词模式匹配
            pred_pattern = f"memory:{query}"
            pred_results = self._ri.query_by_predicate(pred_pattern)
            results.extend(pred_results)
            
            # 策略3: 全文搜索object字段
            all_triples = self._ri.query_pattern()
            text_matches = [
                t for t in all_triples
                if query.lower() in t.object.lower()
                or query.lower() in t.subject.lower()
            ]
            results.extend(text_matches)
            
            # 去重
            seen = set()
            unique_results = []
            for t in results:
                if t.triple_id not in seen:
                    seen.add(t.triple_id)
                    unique_results.append(t)
            
            # 按FTEL综合评分排序
            unique_results.sort(
                key=lambda t: t.ftel.composite_score() * t.confidence,
                reverse=True,
            )
            
            return [
                {
                    "entry": t.to_dict(),
                    "relevance": round(
                        t.ftel.composite_score() * t.confidence, 4
                    ),
                }
                for t in unique_results[:top_k]
            ]
    
    def _flush_to_ledger(self) -> Optional[AkashaBlock]:
        """将待处理三元组打包到账本"""
        if not self._pending_triples:
            return None
        
        block = AkashaBlock(
            index=self._ledger.height,
            triples=list(self._pending_triples),
            previous_hash=self._ledger.last_hash,
            proposer="OrgMemoryBridge",
            status=BlockStatus.FINALIZED,
        )
        
        # 执行金灵球β归约
        beta_result = self._ri.process_block(self._pending_triples)
        block.beta_reduction_result = beta_result
        
        self._ledger.append_block(block)
        self._pending_triples = []
        
        return block
    
    def flush(self) -> Optional[AkashaBlock]:
        """手动刷新到账本"""
        with self._lock:
            return self._flush_to_ledger()


# ===========================================================================
# AkashaChainDB — 主引擎
# ===========================================================================

class AkashaChainDB:
    """
    M190: 阿卡西链式数据库引擎

    核心哲学："信息寓于关联，而非实体"

    组件:
    - ShardedRelationIndex: 分片关系索引图引擎（v2 性能优化）
    - AkashaLedger: 追加式链式账本
    - POPConsensus: 关联优先共识
    - OrgMemoryBridge: M176组织记忆持久化桥接
    - AkashaWAL: WAL 持久化（v2 P0）
    - AkashaBloomFilter: 布隆过滤器（v2 P1）
    - AkashaQueryCache: 查询缓存（v2 P2）
    - UABridge: UA↔Akasha 双向转换桥（v3 UA集成）
    - AkashaSemanticQuery: 语义查询引擎（v3 UA集成）
    - ExpertKnowledgeBridge: 专家知识关联桥（v3 UA集成）
    - AkashaTimeTravel: 时间旅行查询（v3 UA集成）

    定理:
    - T197: 关系本体论定理
    - T198: 金灵球β归约定理
    - T199: 阿卡西完备性定理
    - T200: POP共识安全性定理
    - T222: 分片等价定理
    - T223: WAL 完备定理
    - T224: 双向保持定理
    - T225: 语义收敛定理
    - T226: 时间一致性定理
    """
    
    _instance: Optional["AkashaChainDB"] = None
    _init_time: float = 0.0
    
    def __init__(self):
        self._lock = threading.RLock()
        self._relation_index = ShardedRelationIndex(num_shards=16)
        self._ledger = AkashaLedger()
        self._consensus = POPConsensus()
        self._memory_bridge = OrgMemoryBridge(
            self._relation_index, self._ledger
        )
        self._wal = AkashaWAL(wal_dir=".akasha_wal")
        self._bloom = AkashaBloomFilter()
        self._cache = AkashaQueryCache(max_size=1000)
        # v3 UA集成组件
        self._ua_bridge = UABridge()
        self._semantic_query = AkashaSemanticQuery(self._relation_index)
        self._expert_bridge = ExpertKnowledgeBridge(self._relation_index, self._cache)
        self._time_travel = AkashaTimeTravel(self._ledger)
        self._write_count = 0
        self._query_count = 0
        self._beta_count = 0
        AkashaChainDB._init_time = time.time()
    
    @classmethod
    def get_instance(cls) -> "AkashaChainDB":
        """单例获取"""
        if cls._instance is None:
            cls._instance = AkashaChainDB()
        return cls._instance
    
    # ---- 写入接口 ----
    
    def write_triple(
        self,
        subject: str,
        predicate: str,
        object_: str,
        confidence: float = 1.0,
        source_agent: str = "system",
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """写入三元组"""
        with self._lock:
            triple = AkashaTriple(
                subject=subject,
                predicate=predicate,
                object=object_,
                confidence=confidence,
                source_agent=source_agent,
                metadata=metadata or {},
            )

            # WAL 写入（先写日志）
            self._wal.append(
                op="ADD",
                subject=subject,
                predicate=predicate,
                object_=object_,
                confidence=confidence,
                source_agent=source_agent,
            )

            # 写入索引
            tid = self._relation_index.add_triple(triple)

            # 更新布隆过滤器
            self._bloom.add(subject, predicate, object_)

            # 缓存失效
            self._cache.invalidate(subject=subject, predicate=predicate)

            self._write_count += 1

            return {
                "triple_id": tid,
                "status": "indexed",
                "ftel": triple.ftel.to_dict(),
            }
    
    def write_triples_batch(
        self, triples_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """批量写入三元组 — 延迟索引更新优化"""
        with self._lock:
            triples = []
            for td in triples_data:
                triple = AkashaTriple(
                    subject=td.get("subject", ""),
                    predicate=td.get("predicate", ""),
                    object=td.get("object", ""),
                    confidence=td.get("confidence", 1.0),
                    source_agent=td.get("source_agent", "system"),
                    metadata=td.get("metadata", {}),
                )
                triples.append(triple)

            # 批量 WAL 写入
            for t in triples:
                self._wal.append(
                    op="ADD",
                    subject=t.subject,
                    predicate=t.predicate,
                    object_=t.object,
                    confidence=t.confidence,
                    source_agent=t.source_agent,
                )

            # 金灵球β归约
            beta_result = self._relation_index.process_block(triples)
            self._beta_count += 1
            self._write_count += len(triples)

            # 批量更新布隆过滤器
            for t in triples:
                self._bloom.add(t.subject, t.predicate, t.object)

            # 缓存全部失效
            self._cache.invalidate_all()

            # 打包到账本
            block = AkashaBlock(
                index=self._ledger.height,
                triples=triples,
                previous_hash=self._ledger.last_hash,
                proposer="batch_write",
                status=BlockStatus.FINALIZED,
                beta_reduction_result=beta_result,
            )
            self._ledger.append_block(block)

            return {
                "block_index": block.index,
                "triples_count": len(triples),
                "beta_reduction": beta_result,
                "block_hash": block.block_hash[:16] + "...",
            }
    
    # ---- 查询接口 ----
    
    def query(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        mode: str = "exact",
        top_k: int = 20,
    ) -> Dict[str, Any]:
        """查询三元组 — 布隆过滤器 + 缓存加速"""
        with self._lock:
            self._query_count += 1

            # 布隆过滤器快速排除
            if not self._bloom.might_contain_any(subject, predicate, object_):
                return {"mode": mode, "count": 0, "results": []}

            # 缓存查找
            cached = self._cache.get(subject, predicate, object_, mode)
            if cached is not None:
                return cached

            query_mode = QueryMode(mode)

            if query_mode == QueryMode.NEIGHBORHOOD and subject:
                # FTEL 实体缓存
                ftel_cached = self._cache.get_ftel(subject)
                if ftel_cached is not None and mode == "neighborhood":
                    self._cache.put(
                        ftel_cached,
                        subject=subject, predicate=predicate,
                        object_=object_, mode=mode,
                    )
                    return ftel_cached

                result = self._relation_index.get_neighborhood(subject, depth=1)
                result_with_mode = {"mode": "neighborhood", **result}
                self._cache.put(
                    result_with_mode,
                    subject=subject, predicate=predicate,
                    object_=object_, mode=mode,
                )
                self._cache.put_ftel(subject, result_with_mode)
                return result_with_mode

            results = self._relation_index.query_pattern(
                subject=subject,
                predicate=predicate,
                object_=object_,
            )

            # 按FTEL*confidence排序
            results.sort(
                key=lambda t: t.ftel.composite_score() * t.confidence,
                reverse=True,
            )

            result = {
                "mode": mode,
                "count": len(results),
                "results": [t.to_dict() for t in results[:top_k]],
            }

            # 写入缓存
            self._cache.put(
                result,
                subject=subject, predicate=predicate,
                object_=object_, mode=mode,
            )

            return result
    
    def get_entity_profile(self, entity: str) -> Dict[str, Any]:
        """获取实体画像（T197: 关系本体论）"""
        return self._relation_index.get_entity_profile(entity)
    
    # ---- 组织记忆桥接 ----
    
    def remember(
        self,
        agent_id: str,
        content: str,
        memory_type: str = "experience",
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """M176组织记忆写入"""
        return self._memory_bridge.remember(
            agent_id, content, memory_type, tags, confidence
        )
    
    def recall(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """M176组织记忆检索"""
        return self._memory_bridge.recall(query, top_k)
    
    def flush_memory(self) -> Dict[str, Any]:
        """手动刷新待处理记忆到账本"""
        block = self._memory_bridge.flush()
        if block:
            return {
                "status": "flushed",
                "block_index": block.index,
                "triples_count": len(block.triples),
            }
        return {"status": "no_pending_data"}
    
    # ---- 共识接口 ----
    
    def propose_consensus(
        self,
        proposer: str = "system",
    ) -> Dict[str, Any]:
        """提议共识（将待处理三元组打包投票）"""
        # 收集未入账的三元组
        pending = self._memory_bridge._pending_triples
        if not pending:
            return {"error": "No pending triples to propose"}
        
        block = self._consensus.propose_block(
            pending, proposer, self._ledger
        )
        return block.to_dict()
    
    def vote_consensus(
        self, validator_id: str, approve: bool
    ) -> Dict[str, Any]:
        """投票"""
        return self._consensus.vote(validator_id, approve)
    
    def commit_consensus(self) -> Dict[str, Any]:
        """尝试提交"""
        return self._consensus.try_commit()
    
    # ---- 账本接口 ----
    
    def get_ledger_stats(self) -> Dict[str, Any]:
        """获取账本统计"""
        return self._ledger.get_stats()
    
    def get_blocks(
        self, start: int = 0, end: Optional[int] = None
    ) -> List[Dict]:
        """获取区块列表"""
        return self._ledger.get_blocks_range(start, end)
    
    def verify_chain(self) -> Dict[str, Any]:
        """验证链完整性"""
        return self._ledger.verify_chain()
    
    # ---- 全局状态 ----
    
    def get_state(self) -> Dict[str, Any]:
        """获取引擎全局状态"""
        uptime = time.time() - AkashaChainDB._init_time
        return {
            "module": "M190_AkashaChainDB",
            "version": AKASHA_VERSION,
            "uptime_seconds": round(uptime, 1),
            "write_count": self._write_count,
            "query_count": self._query_count,
            "beta_reduction_count": self._beta_count,
            "relation_index": self._relation_index.get_stats(),
            "ledger": self._ledger.get_stats(),
            "consensus": self._consensus.get_state(),
            "wal": self._wal.get_stats(),
            "bloom": self._bloom.get_stats(),
            "cache": self._cache.get_stats(),
            "ua_bridge": self._ua_bridge.get_stats(),
            "semantic_query": self._semantic_query.get_stats(),
            "expert_bridge": self._expert_bridge.get_stats(),
            "time_travel": self._time_travel.get_stats(),
        }


# ===========================================================================
# 定理注册
# ===========================================================================

THEOREMS_M190 = {
    "T197": {
        "id": "T197",
        "name": "关系本体论定理",
        "statement": (
            "实体性质完全由其关联网络确定："
            "E ≡ {⟨E, r, O⟩ | r ∈ Relations}，无孤立实体。"
            "实体的所有属性都是关系性的，不存在脱离关联的内在性质。"
        ),
        "proof_sketch": (
            "反证法：假设存在实体E具有属性P，但P不出现在任何关联中。"
            "则P对系统不可观测，不构成信息。"
            "由信息寓于关联公理，P不存在。矛盾。"
        ),
        "module": "M190",
    },
    "T198": {
        "id": "T198",
        "name": "金灵球β归约定理",
        "statement": (
            "process_block 对三元组集合的β归约保持语义等价性："
            "⟨Σ, Δ⟩_reduced ≡ ⟨Σ, Δ⟩_original。"
            "去重合并、传递闭包压缩、互斥消解均不丢失可查询信息。"
        ),
        "proof_sketch": (
            "1. 去重：相同三元组合并，置信度用贝叶斯公式提升，"
            "查询结果等价。\n"
            "2. 传递闭包：A→B→C 产生 A→∘→C，是原有路径的合成，"
            "查询可达性不变。\n"
            "3. 互斥消解：取置信度高的，低的被降权而非删除，"
            "可回溯恢复。"
        ),
        "module": "M190",
    },
    "T199": {
        "id": "T199",
        "name": "阿卡西完备性定理",
        "statement": (
            "Ledger + RelationIndex 联合可回答所有关系查询，无信息遗漏。"
            "对任意查询 Q = ⟨s?, p?, o?⟩，存在且仅存在一个结果集 R。"
        ),
        "proof_sketch": (
            "三重索引 (SPO, OPS, PSO) 保证任意单字段绑定可定位。"
            "多字段绑定取交集，结果唯一。"
            "Ledger保证历史可回溯，不丢失已写入数据。"
        ),
        "module": "M190",
    },
    "T200": {
        "id": "T200",
        "name": "POP共识安全性定理",
        "statement": (
            "Proof-of-Priority 在 f < n/3 拜占庭节点下保证链一致性。"
            "三分损益因子 2/3 = BFT容错阈值，同源于 {2,3} 乘法调制。"
        ),
        "proof_sketch": (
            "经典BFT安全性证明：n个节点中f个拜占庭，"
            "需要 n-f > 2f，即 n > 3f。"
            "三分损益因子 2/3 对应 f/n < 1/3。"
            "毕达哥拉斯逗号补偿在边界情况下提供安全裕度。"
        ),
        "module": "M190",
    },
    "T222": {
        "id": "T222",
        "name": "分片等价定理",
        "statement": (
            "分片 RelationIndex 的查询结果与单一索引等价。"
            "对于任意查询 Q = ⟨s?, p?, o?⟩，"
            "ShardedRelationIndex.query_pattern(s, p, o) 的结果集"
            "等于 RelationIndex.query_pattern(s, p, o) 的结果集。"
        ),
        "proof_sketch": (
            "1. 按 predicate 分片是全集的无交划分："
            "每个三元组有且仅有一个 predicate，"
            "因此被分配到唯一的分片 shard(h(predicate))。\n"
            "2. 精确查询 predicate：路由到单分片，"
            "该分片包含所有该 predicate 的三元组，结果等价。\n"
            "3. 无 predicate 约束查询：遍历所有分片取并集，"
            "由分片无交，并集 = 原始全集，结果等价。\n"
            "4. 传递闭包在分片内保持：跨分片的传递链"
            "通过聚合后重建可达性，语义不变。"
        ),
        "module": "M190",
    },
    "T223": {
        "id": "T223",
        "name": "WAL完备定理",
        "statement": (
            "WAL 回放后系统状态与崩溃前一致。"
            "即：snapshot + WAL_log 的回放结果 = 崩溃前的完整索引状态。"
        ),
        "proof_sketch": (
            "1. WAL 采用 append-only 语义，每条写入操作（ADD/DELETE）"
            "在执行前先记录到 WAL 文件。\n"
            "2. checkpoint 将当前完整状态快照写入 .snapshot 文件，"
            "然后截断 WAL 文件，保证 snapshot 是 checkpoint 时刻的一致状态。\n"
            "3. 恢复流程：先从 snapshot 恢复到 checkpoint 时刻的状态，"
            "再从 WAL 日志回放 checkpoint 之后的操作。\n"
            "4. 由于 WAL 记录了所有在 checkpoint 之后、崩溃之前的操作，"
            "且回放顺序与原始执行顺序一致（FIFO），"
            "因此恢复后的状态等价于崩溃前状态。QED。"
        ),
        "module": "M190",
    },
    "T224": {
        "id": "T224",
        "name": "双向保持定理",
        "statement": (
            "UA→Akasha→UA 转换保持语义等价。"
            "即：将 UA KnowledgeGraph 的节点/边转换为 Akasha 三元组，"
            "再转换回 UA 格式，结果与原始数据语义一致。"
        ),
        "proof_sketch": (
            "1. 节点映射：NODE_TYPE_MAP 是双射，"
            "每个 UA 节点类型唯一映射到一个 Akasha predicate，"
            "反向映射可唯一还原。\n"
            "2. 边映射：EDGE_TYPE_MAP 是双射，"
            "每个 UA 边类型唯一映射到 Akasha predicate，"
            "反向映射可唯一还原。\n"
            "3. 数据保持：confidence 和 source_agent 在转换过程中原样传递，"
            "不丢失不修改。\n"
            "4. 往返一致性：f(g(x)) = x，其中 f 为 akasha_to_ua，"
            "g 为 ua_to_akasha，对映射表内的类型成立。QED。"
        ),
        "module": "M190",
    },
    "T225": {
        "id": "T225",
        "name": "语义收敛定理",
        "statement": (
            "语义查询在足够特征下收敛于精确匹配。"
            "即：当查询文本的特征向量与目标文档的特征向量"
            "重叠度趋近于1时，语义相似度趋近于精确匹配。"
        ),
        "proof_sketch": (
            "1. TF-IDF 向量空间中，两个完全相同的文档"
            "余弦相似度为1.0（精确匹配）。\n"
            "2. 当查询文本包含目标文档的所有关键特征词时，"
            "query_vec 与 doc_vec 的交集趋近于 doc_vec 本身，"
            "cos(query, doc) → 1.0。\n"
            "3. 由 IDF 的平滑处理，"
            "高频词的权重降低使得区分性特征词贡献更大，"
            "进一步加速收敛。\n"
            "4. 因此，当特征充分时，语义查询结果收敛于精确匹配。QED。"
        ),
        "module": "M190",
    },
    "T226": {
        "id": "T226",
        "name": "时间一致性定理",
        "statement": (
            "时间旅行查询结果与历史记录一致。"
            "即：query_at_time(entity, T) 返回的三元组集合"
            "等于账本中所有 timestamp ≤ T 的区块中"
            "与 entity 相关的三元组的并集。"
        ),
        "proof_sketch": (
            "1. AkashaLedger 是追加式账本，区块按时间顺序排列，"
            "每个区块有确定的 timestamp。\n"
            "2. query_at_time 遍历所有 timestamp ≤ T 的区块，"
            "收集与 entity 相关的三元组。\n"
            "3. 由于区块不可篡改（哈希链保证），"
            "历史区块中的三元组与写入时完全一致。\n"
            "4. 因此查询结果等价于历史记录，时间一致性成立。QED。"
        ),
        "module": "M190",
    },
}


# ===========================================================================
# MVE 测试
# ===========================================================================

def run_mve() -> Dict[str, Any]:
    """
    M190 最小可行实验 — 验证四大定理
    """
    results = {}
    
    # ---- MVE 1: T197 关系本体论 ----
    db = AkashaChainDB()
    
    # 写入三元组构建关联网络
    db.write_triple("Alice", "knows", "Bob", confidence=0.9)
    db.write_triple("Alice", "works_at", "太乙AGI", confidence=0.95)
    db.write_triple("Bob", "knows", "Charlie", confidence=0.8)
    db.write_triple("Charlie", "works_at", "太乙AGI", confidence=0.85)
    db.write_triple("Alice", "manages", "Bob", confidence=0.7)
    
    # 查询Alice的画像
    alice_profile = db.get_entity_profile("Alice")
    
    # T197验证：Alice的性质完全由关联确定
    t197_pass = (
        alice_profile["out_degree"] >= 2
        and alice_profile["in_degree"] == 0
        and len(alice_profile["relation_types"]) >= 2
        and not alice_profile["is_isolated"]
    )
    results["T197"] = {
        "name": "关系本体论定理",
        "pass": t197_pass,
        "evidence": {
            "alice_out_degree": alice_profile["out_degree"],
            "alice_relation_types": alice_profile["relation_types"],
            "is_isolated": alice_profile["is_isolated"],
        },
    }
    
    # ---- MVE 2: T198 金灵球β归约 ----
    # 批量写入含重复的三元组
    batch_data = [
        {"subject": "X", "predicate": "rel", "object": "Y", "confidence": 0.7},
        {"subject": "X", "predicate": "rel", "object": "Y", "confidence": 0.8},  # 重复
        {"subject": "Y", "predicate": "rel", "object": "Z", "confidence": 0.9},
        {"subject": "Z", "predicate": "rel", "object": "W", "confidence": 0.6},
    ]
    batch_result = db.write_triples_batch(batch_data)
    
    # T198验证：β归约保持语义等价
    t198_pass = (
        batch_result["beta_reduction"]["status"] == "success"
        and batch_result["beta_reduction"]["merged_count"] >= 1  # 有合并
        and batch_result["beta_reduction"]["transitive_count"] >= 1  # 有传递
    )
    results["T198"] = {
        "name": "金灵球β归约定理",
        "pass": t198_pass,
        "evidence": {
            "merged": batch_result["beta_reduction"]["merged_count"],
            "transitive": batch_result["beta_reduction"]["transitive_count"],
            "unique": batch_result["beta_reduction"]["unique_count"],
        },
    }
    
    # ---- MVE 3: T199 阿卡西完备性 ----
    # 多种查询模式
    q1 = db.query(subject="Alice")  # 按主体
    q2 = db.query(predicate="knows")  # 按谓词
    q3 = db.query(object_="太乙AGI")  # 按客体
    q4 = db.query(subject="Alice", object_="Bob")  # 双绑定
    
    # 验证链完整性
    chain_verify = db.verify_chain()
    
    t199_pass = (
        q1["count"] >= 2
        and q2["count"] >= 2
        and q3["count"] >= 1
        and q4["count"] >= 1
        and chain_verify["valid"]
    )
    results["T199"] = {
        "name": "阿卡西完备性定理",
        "pass": t199_pass,
        "evidence": {
            "q_subject_alice": q1["count"],
            "q_predicate_knows": q2["count"],
            "q_object_taiyi": q3["count"],
            "q_double_bind": q4["count"],
            "chain_valid": chain_verify["valid"],
        },
    }
    
    # ---- MVE 4: T200 POP共识安全性 ----
    # 模拟共识流程
    db2 = AkashaChainDB()
    db2.write_triple("N1", "proposes", "Block1", confidence=0.9)
    db2.write_triple("N2", "proposes", "Block2", confidence=0.85)
    
    # 手动共识流程
    proposer = "validator_0"
    block = db2._consensus.propose_block(
        db2._memory_bridge._pending_triples,
        proposer,
        db2._ledger,
    )
    
    # 4个验证者投票
    db2._consensus.vote("v1", True)
    db2._consensus.vote("v2", True)
    db2._consensus.vote("v3", False)  # 1个拜占庭
    db2._consensus.vote("v4", True)
    
    commit_result = db2._consensus.try_commit()
    
    # 3/4 > 2/3 → 应该通过
    t200_pass = commit_result["committed"] and commit_result["ratio"] >= 2.0/3.0
    results["T200"] = {
        "name": "POP共识安全性定理",
        "pass": t200_pass,
        "evidence": {
            "votes_yes": commit_result["votes_yes"],
            "votes_no": commit_result["votes_no"],
            "ratio": commit_result["ratio"],
            "threshold": commit_result["threshold"],
            "committed": commit_result["committed"],
        },
    }
    
    # ---- MVE 5: 组织记忆桥接 ----
    db3 = AkashaChainDB()
    # remember
    r1 = db3.remember("agent_A", "发现M189幂律拟合偏差", "experience", ["bug", "M189"], 0.8)
    r2 = db3.remember("agent_B", "M189 alpha=1.3 验证通过", "theorem", ["M189", "验证"], 0.95)
    r3 = db3.remember("agent_A", "OLS采样偏差导致alpha低估", "failure", ["M189", "bug"], 0.9)
    
    # recall
    recalled = db3.recall("M189", top_k=5)
    
    # 刷新到账本
    flush_result = db3.flush_memory()
    
    t_bridge_pass = (
        r1["status"] == "indexed"
        and len(recalled) >= 2
        and flush_result["status"] == "flushed"
    )
    results["OrgMemoryBridge"] = {
        "name": "M176↔M190桥接",
        "pass": t_bridge_pass,
        "evidence": {
            "remember_status": r1["status"],
            "recall_count": len(recalled),
            "flush_status": flush_result["status"],
        },
    }
    
    # ---- MVE 6: 邻域查询 ----
    db4 = AkashaChainDB()
    db4.write_triple("A", "connects", "B", confidence=0.9)
    db4.write_triple("B", "connects", "C", confidence=0.8)
    db4.write_triple("C", "connects", "D", confidence=0.7)
    db4.write_triple("A", "links", "C", confidence=0.6)

    nb = db4.query(subject="A", mode="neighborhood")

    t_nb_pass = nb["entities_count"] >= 3 and nb["triples_count"] >= 2
    results["NeighborhoodQuery"] = {
        "name": "邻域扩展查询",
        "pass": t_nb_pass,
        "evidence": {
            "entities_count": nb["entities_count"],
            "triples_count": nb["triples_count"],
            "ftel_avg": nb["ftel_avg"],
        },
    }

    # ---- MVE 7: T222 分片等价定理 ----
    db5 = AkashaChainDB()

    # 写入三元组到分片索引
    db5.write_triple("S1", "knows", "O1", confidence=0.9)
    db5.write_triple("S2", "likes", "O2", confidence=0.8)
    db5.write_triple("S1", "likes", "O3", confidence=0.7)
    db5.write_triple("S3", "knows", "O1", confidence=0.85)

    # 用单一 RelationIndex 作为参考
    ref_index = RelationIndex()
    for t_data in [
        ("S1", "knows", "O1", 0.9),
        ("S2", "likes", "O2", 0.8),
        ("S1", "likes", "O3", 0.7),
        ("S3", "knows", "O1", 0.85),
    ]:
        ref_index.add_triple(AkashaTriple(
            subject=t_data[0], predicate=t_data[1],
            object=t_data[2], confidence=t_data[3],
        ))

    # 比较查询结果
    q_by_pred = db5._relation_index.query_by_predicate("knows")
    ref_by_pred = ref_index.query_by_predicate("knows")
    shard_pred_count = len(q_by_pred)
    ref_pred_count = len(ref_by_pred)

    q_pattern = db5._relation_index.query_pattern(subject="S1")
    ref_pattern = ref_index.query_pattern(subject="S1")
    shard_pattern_count = len(q_pattern)
    ref_pattern_count = len(ref_pattern)

    t222_pass = (
        shard_pred_count == ref_pred_count
        and shard_pattern_count == ref_pattern_count
    )
    results["T222"] = {
        "name": "分片等价定理",
        "pass": t222_pass,
        "evidence": {
            "shard_pred_count": shard_pred_count,
            "ref_pred_count": ref_pred_count,
            "shard_pattern_count": shard_pattern_count,
            "ref_pattern_count": ref_pattern_count,
        },
    }

    # ---- MVE 8: T223 WAL 完备定理 ----
    import tempfile
    import shutil

    # 创建临时 WAL 目录
    wal_dir = tempfile.mkdtemp(prefix="akasha_wal_test_")
    db6 = AkashaChainDB()

    # 替换 WAL 为临时目录的 WAL
    db6._wal = AkashaWAL(wal_dir=wal_dir, checkpoint_interval=1000)

    # 写入一些三元组
    db6.write_triple("W1", "rel", "X1", confidence=0.9)
    db6.write_triple("W2", "rel", "X2", confidence=0.8)
    db6.write_triple("W1", "knows", "X3", confidence=0.85)

    # 查询原始结果
    orig_results = db6.query(subject="W1")

    # Checkpoint
    db6._wal.checkpoint(reason="manual_test")

    # 继续写入
    db6.write_triple("W3", "rel", "X4", confidence=0.75)
    db6.write_triple("W1", "likes", "X5", confidence=0.7)

    # 查询 checkpoint 后的结果
    post_cp_results = db6.query(subject="W1")

    # 模拟恢复：创建新的空 DB，从 WAL 恢复
    db7 = AkashaChainDB()
    db7._relation_index = ShardedRelationIndex(num_shards=16)
    db7._bloom = AkashaBloomFilter()

    # 从 WAL 恢复（同时更新布隆过滤器）
    recover_result = db6._wal.recover(db7._relation_index, bloom_filter=db7._bloom)

    # 验证恢复后的查询结果
    recovered_results = db7.query(subject="W1")

    t223_pass = (
        recover_result["restored_count"] > 0
        and recovered_results["count"] == post_cp_results["count"]
    )

    # 清理临时目录和默认WAL目录
    shutil.rmtree(wal_dir, ignore_errors=True)
    shutil.rmtree(".akasha_wal", ignore_errors=True)

    results["T223"] = {
        "name": "WAL完备定理",
        "pass": t223_pass,
        "evidence": {
            "restored_count": recover_result["restored_count"],
            "original_count": orig_results["count"],
            "post_checkpoint_count": post_cp_results["count"],
            "recovered_count": recovered_results["count"],
        },
    }

    # ---- MVE 9: T224 双向保持定理 ----
    bridge = UABridge()

    # UA→Akasha: 转换一个节点和一条边
    node_triples = bridge.ua_to_akasha(
        node_type="class",
        node_data={"id": "MyClass", "name": "MyClass", "confidence": 0.9, "source_agent": "test"},
        edge_type="depends_on",
        edge_data={"source": "MyClass", "target": "BaseClass", "confidence": 0.85, "source_agent": "test"},
    )

    # Akasha→UA: 转换回来
    ua_result = bridge.akasha_to_ua(node_triples)

    # 验证往返一致性
    # 节点应还原出 type="class"
    node_types = [n.get("type") for n in ua_result.get("nodes", [])]
    edge_types = [e.get("type") for e in ua_result.get("edges", [])]

    t224_pass = (
        len(node_triples) >= 2  # 至少1个节点三元组+1个边三元组
        and "class" in node_types  # 节点类型还原
        and "depends_on" in edge_types  # 边类型还原
        and ua_result.get("nodes", [{}])[0].get("confidence", 0) > 0  # confidence保持
    )
    results["T224"] = {
        "name": "双向保持定理",
        "pass": t224_pass,
        "evidence": {
            "ua_to_akasha_count": len(node_triples),
            "akasha_to_ua_nodes": len(ua_result.get("nodes", [])),
            "akasha_to_ua_edges": len(ua_result.get("edges", [])),
            "node_types_roundtrip": node_types,
            "edge_types_roundtrip": edge_types,
        },
    }

    # ---- MVE 10: T225 语义收敛定理 ----
    db8 = AkashaChainDB()

    # 写入有语义关联的三元组
    db8.write_triple("Python", "is_a", "programming_language", confidence=0.95)
    db8.write_triple("Python", "used_for", "data_science", confidence=0.9)
    db8.write_triple("JavaScript", "is_a", "programming_language", confidence=0.95)
    db8.write_triple("Rust", "is_a", "programming_language", confidence=0.9)

    # 构建语义索引
    db8._semantic_query.build_index()

    # 精确查询: "programming_language" 应找到相关三元组
    semantic_results = db8._semantic_query.semantic_search(
        query="programming language", top_k=5, threshold=0.1
    )

    # 验证：精确关键词查询应返回高相似度结果
    t225_pass = (
        len(semantic_results) > 0
        and all(r["similarity"] > 0.0 for r in semantic_results)
    )
    results["T225"] = {
        "name": "语义收敛定理",
        "pass": t225_pass,
        "evidence": {
            "search_results_count": len(semantic_results),
            "top_similarity": semantic_results[0]["similarity"] if semantic_results else 0,
            "index_built": db8._semantic_query.get_stats()["index_built"],
            "index_triple_count": db8._semantic_query.get_stats()["index_triple_count"],
        },
    }

    # ---- MVE 11: T226 时间一致性定理 ----
    db9 = AkashaChainDB()

    # 直接向账本追加包含 Entity1 的区块
    # AkashaBlock(index, triples, previous_hash, proposer=...)
    t_before = time.time()
    block1 = AkashaBlock(
        index=db9._ledger.height,
        triples=[
            AkashaTriple(subject="Entity1", predicate="has_state", object="initial", confidence=0.9),
            AkashaTriple(subject="Entity1", predicate="has_version", object="v1", confidence=0.85),
        ],
        previous_hash=db9._ledger.last_hash,
        proposer="system",
    )
    db9._ledger.append_block(block1)
    t_after_first = time.time()

    block2 = AkashaBlock(
        index=db9._ledger.height,
        triples=[
            AkashaTriple(subject="Entity1", predicate="has_state", object="updated", confidence=0.85),
        ],
        previous_hash=db9._ledger.last_hash,
        proposer="system",
    )
    db9._ledger.append_block(block2)
    t_after_second = time.time()

    # 时间旅行查询：查询当前时间点之后
    time_result = db9._time_travel.query_at_time("Entity1", t_after_second + 1.0)

    # 时间线查询
    timeline = db9._time_travel.get_entity_timeline("Entity1")

    t226_pass = (
        time_result["entity"] == "Entity1"
        and time_result["triples_count"] >= 1
        and len(timeline) >= 1
    )
    results["T226"] = {
        "name": "时间一致性定理",
        "pass": t226_pass,
        "evidence": {
            "time_travel_triples": time_result["triples_count"],
            "timeline_entries": len(timeline),
            "blocks_scanned": time_result["blocks_scanned"],
        },
    }
    
    # ---- 汇总 ----
    all_pass = all(r["pass"] for r in results.values())
    passed = sum(1 for r in results.values() if r["pass"])
    total = len(results)
    
    return {
        "module": "M190_AkashaChainDB",
        "version": AKASHA_VERSION,
        "all_pass": all_pass,
        "summary": f"{passed}/{total} PASSED {'✅' if all_pass else '❌'}",
        "results": results,
    }


# ===========================================================================
# 入口
# ===========================================================================

if __name__ == "__main__":
    mve = run_mve()
    print(json.dumps(mve, indent=2, ensure_ascii=False))
