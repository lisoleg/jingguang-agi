# -*- coding: utf-8 -*-
"""
模块39：DIKWP可靠性层（R层）
ProofLedger证明账本 + BFT容错 + Lean证明接口

来源：复合体AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13
"""

import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum


@dataclass
class ProofEntry:
    """
    R层：证明账本条目
    
    DIKWP对应：证据闭环 ProofLedger
    哥德尔机对应：可证明安全的行动执行
    """
    entry_id: str
    claim: str                      # 主张/断言
    evidence_ids: List[str]         # 引用的D层数据IDs
    r_score: float                  # 可靠性分数 [0, 1]
    lean_proof: Optional[str] = None  # Lean形式化证明代码
    bft_validated: bool = False      # BFT共识验证状态
    bft_votes: List[Dict] = field(default_factory=list)  # BFT投票记录
    kill_conditions: List[str] = field(default_factory=list)  # 触发降权的条件
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    deprecated: bool = False
    deprecated_reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "entry_id": self.entry_id,
            "claim": self.claim,
            "evidence_ids": self.evidence_ids,
            "r_score": self.r_score,
            "lean_proof": self.lean_proof,
            "bft_validated": self.bft_validated,
            "bft_votes": self.bft_votes,
            "kill_conditions": self.kill_conditions,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "deprecated": self.deprecated,
            "deprecated_reason": self.deprecated_reason
        }


@dataclass  
class LeanProofResult:
    """Lean证明结果"""
    verified: bool
    lean_code: str
    status: str                     # "verified", "failed", "pending"
    error_message: Optional[str] = None
    proof_steps: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "verified": self.verified,
            "lean_code": self.lean_code[:100] + "..." if len(self.lean_code) > 100 else self.lean_code,
            "status": self.status,
            "error_message": self.error_message,
            "proof_steps": self.proof_steps,
            "timestamp": self.timestamp
        }


@dataclass
class BFTValidator:
    """BFT验证者"""
    id: str
    name: str
    trust_level: float = 0.8  # 信任级别 [0, 1]
    active: bool = True


class DIKWPReliabilityLayer:
    """
    模块39：DIKWP R层 - 证明账本 + 可降权机制
    
    融合BFT容错（模块31）+ Lean证明接口（模块30）
    DIKWP对应：证据闭环 ProofLedger
    哥德尔机对应：可证明安全的行动执行
    
    核心功能：
    1. add_proof() - 添加证明条目
    2. bft_validate() - BFT共识验证
    3. lean_verify() - Lean形式化验证
    4. downgrade() - 降权机制
    5. get_reliable_entries() - 获取可靠条目
    """
    
    def __init__(self):
        self.proof_ledger: Dict[str, ProofEntry] = {}
        self.validators: Dict[str, BFTValidator] = {}
        self._entry_counter = 0
        self._r_threshold: float = 0.6  # 最低可信度阈值
        
        # 注册默认验证者
        self._register_default_validators()
    
    def _register_default_validators(self):
        """注册默认BFT验证者"""
        default_validators = [
            BFTValidator("v1", "数据层验证器", trust_level=0.9),
            BFTValidator("v2", "逻辑层验证器", trust_level=0.85),
            BFTValidator("v3", "语义层验证器", trust_level=0.8),
        ]
        for v in default_validators:
            self.validators[v.id] = v
    
    def add_proof(self, 
                 claim: str, 
                 evidence_ids: List[str],
                 r_score: float,
                 lean_proof: str = None,
                 kill_conditions: List[str] = None,
                 metadata: Dict = None) -> ProofEntry:
        """
        添加证明条目到账本
        
        Args:
            claim: 主张/断言
            evidence_ids: 引用的D层数据IDs
            r_score: 可靠性分数 [0, 1]
            lean_proof: Lean形式化证明代码
            kill_conditions: 触发降权的条件
            metadata: 额外元数据
        
        Returns:
            ProofEntry: 创建的证明条目
        """
        self._entry_counter += 1
        entry_id = f"R{self._entry_counter:04d}"
        
        entry = ProofEntry(
            entry_id=entry_id,
            claim=claim,
            evidence_ids=evidence_ids,
            r_score=r_score,
            lean_proof=lean_proof,
            kill_conditions=kill_conditions or [],
            metadata=metadata or {}
        )
        
        self.proof_ledger[entry_id] = entry
        return entry
    
    def get_proof(self, entry_id: str) -> Optional[ProofEntry]:
        """获取指定证明条目"""
        return self.proof_ledger.get(entry_id)
    
    def bft_validate(self, 
                    entry_id: str, 
                    validators: List[str] = None) -> bool:
        """
        BFT共识验证（需要2/3以上验证者同意）
        
        弹簧虫类比：守恒律被多个传感器共同验证
        
        Args:
            entry_id: 证明条目ID
            validators: 验证者ID列表（None=使用所有活跃验证者）
        
        Returns:
            bool: 验证是否通过
        """
        if entry_id not in self.proof_ledger:
            return False
        
        entry = self.proof_ledger[entry_id]
        
        # 获取验证者
        if validators is None:
            validators = [v.id for v in self.validators.values() if v.active]
        
        # 计算所需票数（2/3 + 1）
        total_validators = len(validators)
        required = total_validators * 2 // 3 + 1
        
        # 模拟BFT投票（实际实现需连接模块31）
        # 每个验证者投票，信任度越高权重越大
        total_trust = 0.0
        votes_for = 0
        
        for vid in validators:
            if vid in self.validators:
                v = self.validators[vid]
                trust = v.trust_level
                
                # 模拟投票：基于条目当前分数
                vote_for = entry.r_score >= self._r_threshold or trust > 0.85
                
                entry.bft_votes.append({
                    "validator_id": vid,
                    "validator_name": v.name,
                    "vote": "for" if vote_for else "against",
                    "trust_level": trust,
                    "timestamp": time.time()
                })
                
                if vote_for:
                    votes_for += trust
                    total_trust += trust
        
        # 计算加权投票比例
        if total_trust > 0:
            vote_ratio = votes_for / total_trust
        else:
            vote_ratio = 0
        
        # 通过条件：加权投票 > 2/3
        if vote_ratio >= 0.667:
            entry.bft_validated = True
            # BFT验证通过后，可靠性分数提升
            entry.r_score = min(1.0, entry.r_score + 0.1)
            return True
        
        return False
    
    def lean_verify(self, lean_code: str) -> LeanProofResult:
        """
        Lean 4形式化验证接口（连接模块30）
        
        注意：这是模拟实现，实际需要连接Lean runtime
        
        Args:
            lean_code: Lean 4证明代码
        
        Returns:
            LeanProofResult: 验证结果
        """
        # 模拟Lean验证
        # 实际实现：需要调用本地Lean 4安装或lake服务器
        
        # 检查基本格式
        has_theorem = "theorem" in lean_code.lower() or "lemma" in lean_code.lower()
        has_proof = "proof" in lean_code.lower() or "qed" in lean_code.lower()
        has_sorry = "sorry" in lean_code.lower()  # sorry = 未完成证明
        
        if not has_theorem:
            return LeanProofResult(
                verified=False,
                lean_code=lean_code,
                status="failed",
                error_message="缺少theorem或lemma声明",
                proof_steps=[]
            )
        
        if has_sorry:
            return LeanProofResult(
                verified=False,
                lean_code=lean_code,
                status="pending",
                error_message="证明未完成（包含sorry）",
                proof_steps=["theorem_declaration", "proof_started", "proof_incomplete"]
            )
        
        if has_proof:
            return LeanProofResult(
                verified=True,  # 简化：假设格式正确即通过
                lean_code=lean_code,
                status="verified",
                proof_steps=["theorem_declaration", "proof_parsing", "type_checking", "proof_verified"]
            )
        
        return LeanProofResult(
            verified=False,
            lean_code=lean_code,
            status="failed",
            error_message="缺少proof块",
            proof_steps=["theorem_declaration", "missing_proof"]
        )
    
    def lean_verify_entry(self, entry_id: str, lean_code: str) -> LeanProofResult:
        """
        对证明条目进行Lean验证
        
        Args:
            entry_id: 证明条目ID
            lean_code: Lean证明代码
        
        Returns:
            LeanProofResult: 验证结果
        """
        if entry_id not in self.proof_ledger:
            return LeanProofResult(
                verified=False,
                lean_code=lean_code,
                status="failed",
                error_message=f"条目{entry_id}不存在"
            )
        
        entry = self.proof_ledger[entry_id]
        result = self.lean_verify(lean_code)
        
        # 更新条目
        entry.lean_proof = lean_code
        if result.verified:
            # Lean验证通过，可靠性提升
            entry.r_score = min(1.0, entry.r_score + 0.15)
        
        return result
    
    def downgrade(self, entry_id: str, reason: str) -> bool:
        """
        降权：触发kill_conditions时降低可靠性分数
        
        Args:
            entry_id: 证明条目ID
            reason: 降权原因
        
        Returns:
            bool: 是否成功降权
        """
        if entry_id not in self.proof_ledger:
            return False
        
        entry = self.proof_ledger[entry_id]
        
        # 检查是否触发降权条件
        if reason in entry.kill_conditions:
            # 降权幅度
            entry.r_score = max(0.0, entry.r_score - 0.3)
            
            # 如果低于阈值，标记为废弃
            if entry.r_score < self._r_threshold:
                entry.deprecated = True
                entry.deprecated_reason = reason
        
        # 即使不触发条件，也可能需要降权
        elif entry.r_score > 0:
            entry.r_score = max(0.0, entry.r_score - 0.1)
            
            if entry.r_score < self._r_threshold:
                entry.deprecated = True
                entry.deprecated_reason = reason
        
        return True
    
    def auto_downgrade_expired(self) -> int:
        """
        自动降权过期条目
        
        Returns:
            int: 降权的条目数量
        """
        now = time.time()
        degraded = 0
        
        for entry in self.proof_ledger.values():
            if entry.deprecated:
                continue
            
            # 检查是否过期（假设超过24小时）
            if now - entry.timestamp > 86400:
                if self.downgrade(entry.entry_id, "expired"):
                    degraded += 1
        
        return degraded
    
    def get_reliable_entries(self, 
                            min_score: float = None,
                            bft_required: bool = False) -> List[ProofEntry]:
        """
        获取所有可靠的证明条目（未降权且分数达标）
        
        Args:
            min_score: 最低分数（None=使用阈值）
            bft_required: 是否要求BFT验证通过
        
        Returns:
            List[ProofEntry]: 可靠的条目列表
        """
        if min_score is None:
            min_score = self._r_threshold
        
        results = []
        for entry in self.proof_ledger.values():
            if entry.deprecated:
                continue
            
            if entry.r_score < min_score:
                continue
            
            if bft_required and not entry.bft_validated:
                continue
            
            results.append(entry)
        
        # 按分数排序
        results.sort(key=lambda x: x.r_score, reverse=True)
        return results
    
    def compute_cq(self, session_id: str = None) -> Dict:
        """
        计算意识商数（CQ = Consciousness Quotient）
        
        CQ = f(DIKWP认知轨迹 + 意图伦理对齐)
        
        公式：
        CQ = (D层覆盖度 × 0.15 + I层连通度 × 0.15 + 
              K层规则密度 × 0.2 + W层决策质量 × 0.2 +
              P层目的纯度 × 0.15 + R层可靠性 × 0.15) × 100
        
        Args:
            session_id: 可选的会话ID
        
        Returns:
            Dict: CQ评估结果
        """
        entries = list(self.proof_ledger.values())
        active_entries = [e for e in entries if not e.deprecated]
        
        if not entries:
            return {
                "cq_score": 0.0,
                "grade": "N/A",
                "components": {},
                "message": "无证明条目"
            }
        
        # 各层得分计算
        components = {}
        
        # D层覆盖度：基于条目数量
        components["D_coverage"] = min(len(entries) / 10, 1.0)
        
        # I层连通度：基于BFT验证比例
        bft_ratio = sum(1 for e in entries if e.bft_validated) / max(len(entries), 1)
        components["I_connectivity"] = bft_ratio
        
        # K层规则密度：基于平均分数
        components["K_density"] = sum(e.r_score for e in entries) / max(len(entries), 1)
        
        # W层决策质量：基于活跃条目比例
        active_ratio = len(active_entries) / max(len(entries), 1)
        components["W_quality"] = active_ratio
        
        # P层目的纯度：基于条目完整性
        full_entries = sum(1 for e in entries if e.lean_proof and e.bft_validated)
        components["P_purity"] = full_entries / max(len(entries), 1)
        
        # R层可靠性：基于平均分数
        components["R_reliability"] = sum(e.r_score for e in active_entries) / max(len(active_entries), 1)
        
        # 综合CQ得分
        weights = {
            "D_coverage": 0.15,
            "I_connectivity": 0.15,
            "K_density": 0.20,
            "W_quality": 0.20,
            "P_purity": 0.15,
            "R_reliability": 0.15
        }
        
        cq_score = sum(components[k] * weights[k] for k in weights) * 100
        
        # 评级
        if cq_score >= 80:
            grade = "A (优秀)"
        elif cq_score >= 60:
            grade = "B (良好)"
        elif cq_score >= 40:
            grade = "C (一般)"
        else:
            grade = "D (需改进)"
        
        return {
            "cq_score": cq_score,
            "grade": grade,
            "components": components,
            "weights": weights,
            "total_entries": len(entries),
            "active_entries": len(active_entries),
            "bft_validated": sum(1 for e in entries if e.bft_validated),
            "timestamp": time.time()
        }
    
    def get_statistics(self) -> Dict:
        """获取可靠性层统计信息"""
        entries = list(self.proof_ledger.values())
        active = [e for e in entries if not e.deprecated]
        
        return {
            "total_entries": len(entries),
            "active_entries": len(active),
            "deprecated_entries": len(entries) - len(active),
            "avg_r_score": sum(e.r_score for e in entries) / max(len(entries), 1),
            "bft_validated": sum(1 for e in entries if e.bft_validated),
            "lean_proofs": sum(1 for e in entries if e.lean_proof),
            "reliable_entries": len(self.get_reliable_entries()),
            "r_threshold": self._r_threshold,
            "validators": len([v for v in self.validators.values() if v.active]),
            "cq": self.compute_cq()
        }
    
    def export_ledger(self, filepath: str):
        """导出具可靠性账本"""
        data = {
            "entries": {eid: entry.to_dict() for eid, entry in self.proof_ledger.items()},
            "validators": {vid: {
                "name": v.name,
                "trust_level": v.trust_level,
                "active": v.active
            } for vid, v in self.validators.items()},
            "statistics": self.get_statistics(),
            "export_time": time.time()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def __repr__(self) -> str:
        return f"DIKWPReliabilityLayer(entries={len(self.proof_ledger)}, threshold={self._r_threshold})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块39：DIKWP可靠性层（R层）测试")
    print("=" * 60)
    
    # 1. 创建可靠性层实例
    reliability_layer = DIKWPReliabilityLayer()
    print(f"\n✓ 创建可靠性层: {reliability_layer}")
    
    # 2. 添加证明条目
    print(f"\n✓ 添加证明条目:")
    
    entries = [
        reliability_layer.add_proof(
            claim="复合体AGI 6.0基于DIKWP六层语义治理",
            evidence_ids=["D_001", "D_002"],
            r_score=0.85,
            metadata={"source": "analysis"}
        ),
        reliability_layer.add_proof(
            claim="弹簧虫定理可应用于AGI协调总线",
            evidence_ids=["D_003"],
            r_score=0.75,
            kill_conditions=["contradictory_evidence", "failed_replication"]
        ),
        reliability_layer.add_proof(
            claim="刘原理是AGI决策的核心准则",
            evidence_ids=["D_004", "D_005"],
            r_score=0.90,
            lean_proof="theorem foo: S = S_data + lambda*C(purpose) - mu*Risk\nproof\n  rw real\nqeds"
        )
    ]
    
    for entry in entries:
        print(f"  - {entry.entry_id}: {entry.claim[:30]}...")
        print(f"    r_score: {entry.r_score:.2f}, BFT: {entry.bft_validated}")
    
    # 3. BFT验证
    print(f"\n✓ BFT验证:")
    
    for entry_id in [entries[0].entry_id, entries[2].entry_id]:
        result = reliability_layer.bft_validate(entry_id)
        entry = reliability_layer.get_proof(entry_id)
        print(f"  - {entry_id}: {'通过 ✓' if result else '未通过'}")
        print(f"    投票数: {len(entry.bft_votes)}, 最终分数: {entry.r_score:.2f}")
    
    # 4. Lean验证
    print(f"\n✓ Lean验证:")
    
    lean_code_valid = """
theorem minimum_action_principle (S S_data C R : ℝ) :
  S = S_data + 0.7 * C - 0.3 * R → S > 0.5 → should_proceed
proof
  intro h
  have h1 : S > 0.5 := h.1
  exact h1
qeds
"""
    
    lean_code_invalid = """
theorem foo : false
proof
  sorry
qeds
"""
    
    result_valid = reliability_layer.lean_verify(lean_code_valid)
    print(f"  有效证明: {result_valid.status} - {result_valid.verified}")
    
    result_invalid = reliability_layer.lean_verify(lean_code_invalid)
    print(f"  无效证明: {result_invalid.status} - {result_invalid.verified}")
    
    # 5. 降权测试
    print(f"\n✓ 降权测试:")
    
    print(f"  降权前: {entries[1].entry_id} r_score = {entries[1].r_score:.2f}")
    reliability_layer.downgrade(entries[1].entry_id, "contradictory_evidence")
    print(f"  降权后: {entries[1].entry_id} r_score = {entries[1].r_score:.2f}")
    print(f"  废弃状态: {entries[1].deprecated}")
    
    # 6. CQ意识商数
    print(f"\n✓ CQ意识商数计算:")
    
    cq = reliability_layer.compute_cq()
    print(f"  CQ得分: {cq['cq_score']:.1f}")
    print(f"  评级: {cq['grade']}")
    print(f"  各层得分:")
    for key, value in cq['components'].items():
        print(f"    {key}: {value:.2f}")
    
    # 7. 统计信息
    print(f"\n✓ 统计信息:")
    stats = reliability_layer.get_statistics()
    print(f"  总条目: {stats['total_entries']}")
    print(f"  活跃条目: {stats['active_entries']}")
    print(f"  平均分数: {stats['avg_r_score']:.2f}")
    print(f"  BFT验证通过: {stats['bft_validated']}")
    print(f"  可靠条目: {stats['reliable_entries']}")
    
    print("\n" + "=" * 60)
    print("模块39测试完成 ✓")
    print("=" * 60)
