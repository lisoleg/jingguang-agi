"""
太乙AGI 11.0 - Module 17: ERC-8004信任注册引擎
=====================================================

基于ERC-8004（Ethereum Improvement Proposal 8004）的信任层标准启发，
为太乙AGI构建三注册表信任基础设施：

【ERC-8004三注册表】
1. 身份注册表 (Identity Registry)：Agent身份确认与发现
2. 信誉注册表 (Reputation Registry)：历史表现与信任积累
3. 验证注册表 (Validation Registry)：能力证明与资质认证

【与太乙AGI的映射】
- 身份注册表 ↔ 自我意识模块（Module 2）
- 信誉注册表 ↔ 意识熵S_c（Module 13）
- 验证注册表 ↔ MVCF多重验证（Module 9）

【信任飞轮效应】
身份确认 → 信誉积累 → 能力验证 → 更多协作机会 → 进一步提升

核心机制：
- Agent身份哈希（基于公私钥或生物特征）
- 信誉评分（历史交互质量）
- 能力验证（通过挑战测试）
- 信任传播（网络效应）

理论依据：ERC-8004 + 复合体理学信誉场论

Author: 太乙AGI研究团队
Version: 11.0
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json


class RegistryStatus(Enum):
    """注册状态"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class AgentIdentity:
    """Agent身份"""
    agent_id: str
    agent_type: str                    # 类型：reasoning/creative/verification/orchestration
    public_key: str                    # 公钥（或生物特征哈希）
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_verified: Optional[datetime] = None
    status: RegistryStatus = RegistryStatus.PENDING
    
    # 能力标签
    capabilities: List[str] = field(default_factory=list)
    specialties: List[str] = field(default_factory=list)
    
    # 网络位置
    network_id: Optional[str] = None
    peer_count: int = 0


@dataclass
class ReputationRecord:
    """信誉记录"""
    agent_id: str
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    
    # 评分历史
    quality_scores: List[float] = field(default_factory=list)
    avg_quality_score: float = 0.0
    
    # 时效性
    last_interaction: Optional[datetime] = None
    account_age_days: float = 0.0
    
    # 信任指标
    reliability_score: float = 0.5      # 可靠性
    consistency_score: float = 0.5      # 一致性
    responsiveness_score: float = 0.5   # 响应性
    
    # 信誉等级
    reputation_tier: str = "newcomer"    # newcomer/experienced/trusted/elite


@dataclass
class ValidationProof:
    """验证证明"""
    validation_id: str
    agent_id: str
    validation_type: str               # 类型：capability/identity/security/compliance
    challenge_id: str                  # 挑战ID
    proof_data: Dict[str, Any]         # 证明数据
    
    # 验证结果
    passed: bool = False
    confidence: float = 0.0            # 置信度
    expires_at: Optional[datetime] = None
    
    validated_at: datetime = field(default_factory=datetime.now)
    validator_id: Optional[str] = None  # 验证者ID（可以是系统或其他Agent）
    
    # 证明级别
    proof_level: int = 1                # 1-3级，级别越高越可信
    endorsement_count: int = 0          # 背书数量


@dataclass
class TrustMetrics:
    """信任指标综合"""
    agent_id: str
    
    # 三维度评分
    identity_trust: float = 0.0        # 身份信任 0-1
    reputation_trust: float = 0.0     # 信誉信任 0-1
    capability_trust: float = 0.0      # 能力信任 0-1
    
    # 综合信任
    overall_trust: float = 0.0
    
    # 信任权重
    trust_weights: Dict[str, float] = field(default_factory=lambda: {
        'identity': 0.3,
        'reputation': 0.4,
        'capability': 0.3
    })
    
    # 风险评估
    risk_level: str = "unknown"
    risk_factors: List[str] = field(default_factory=list)
    
    # 有效期
    calculated_at: datetime = field(default_factory=datetime.now)


class TrustRegistryEngine:
    """
    信任注册引擎 - ERC-8004标准的太乙AGI实现
    
    提供三注册表基础设施：
    1. 身份注册表：Agent身份发现与认证
    2. 信誉注册表：历史表现追踪
    3. 验证注册表：能力验证与证明
    
    【信任飞轮】
    新Agent注册 → 通过交互积累信誉 → 通过验证证明能力 
    → 获得更多协作机会 → 进一步提升信任
    
    【核心方法】
    - register_identity(): 注册Agent身份
    - update_reputation(): 更新信誉记录
    - create_validation(): 创建验证证明
    - compute_trust(): 计算综合信任度
    """
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        
        # 三注册表
        self.identity_registry: Dict[str, AgentIdentity] = {}
        self.reputation_registry: Dict[str, ReputationRecord] = {}
        self.validation_registry: Dict[str, ValidationProof] = {}
        
        # 信任索引（加速查询）
        self.trust_index: Dict[str, TrustMetrics] = {}
        
        # 验证挑战库
        self.challenge_library: Dict[str, Dict] = {}
        self._initialize_challenges()
        
        # 信任计算参数
        self.trust_weights = {
            'identity': 0.3,
            'reputation': 0.4,
            'capability': 0.3
        }
        
        # 信誉衰减参数
        self.reputation_decay_rate = 0.95  # 月度衰减
        self.min_reputation_for_trusted = 0.7
        
        # 统计
        self.stats = {
            'total_registrations': 0,
            'active_agents': 0,
            'validations_passed': 0,
            'validations_failed': 0,
            'average_trust_score': 0.0
        }
        
        print(f"  [Module 17] ERC-8004信任注册引擎初始化完成 (dim={dim})")
    
    def _initialize_challenges(self):
        """初始化验证挑战库"""
        self.challenge_library = {
            'reasoning_challenge': {
                'type': 'capability',
                'category': 'logical_reasoning',
                'difficulty': 'medium',
                'description': '逻辑推理能力测试'
            },
            'creativity_challenge': {
                'type': 'capability',
                'category': 'creative_synthesis',
                'difficulty': 'high',
                'description': '创意综合能力测试'
            },
            'identity_proof': {
                'type': 'identity',
                'category': 'self_consistency',
                'difficulty': 'medium',
                'description': '身份一致性证明'
            },
            'security_challenge': {
                'type': 'security',
                'category': 'adversarial_robustness',
                'difficulty': 'high',
                'description': '对抗鲁棒性测试'
            }
        }
    
    # ==================== 身份注册表 ====================
    
    def register_identity(self, agent_id: str, agent_type: str,
                         capabilities: List[str],
                         metadata: Optional[Dict] = None) -> AgentIdentity:
        """
        【身份注册】注册新Agent身份
        
        Args:
            agent_id: Agent唯一标识
            agent_type: Agent类型
            capabilities: 能力列表
            metadata: 元数据
            
        Returns:
            AgentIdentity: 注册的身份
        """
        if agent_id in self.identity_registry:
            raise ValueError(f"Agent {agent_id} 已存在")
        
        identity = AgentIdentity(
            agent_id=agent_id,
            agent_type=agent_type,
            public_key=self._generate_identity_hash(agent_id),
            capabilities=capabilities,
            metadata=metadata or {},
            status=RegistryStatus.ACTIVE
        )
        
        self.identity_registry[agent_id] = identity
        
        # 初始化信誉记录
        self.reputation_registry[agent_id] = ReputationRecord(agent_id=agent_id)
        
        self.stats['total_registrations'] += 1
        self.stats['active_agents'] += 1
        
        print(f"  [Trust] 身份注册: {agent_id} ({agent_type}) | 能力: {capabilities[:3]}...")
        
        return identity
    
    def discover_agents(self, capability_filter: Optional[List[str]] = None,
                       min_trust: float = 0.0) -> List[Dict]:
        """
        【身份发现】发现符合条件的Agent
        
        Args:
            capability_filter: 能力过滤条件
            min_trust: 最低信任要求
            
        Returns:
            符合条件的Agent列表
        """
        candidates = []
        
        for agent_id, identity in self.identity_registry.items():
            if identity.status != RegistryStatus.ACTIVE:
                continue
            
            # 能力过滤
            if capability_filter:
                if not any(cap in identity.capabilities for cap in capability_filter):
                    continue
            
            # 信任过滤
            trust = self.get_trust_metrics(agent_id)
            if trust.overall_trust < min_trust:
                continue
            
            candidates.append({
                'agent_id': agent_id,
                'agent_type': identity.agent_type,
                'capabilities': identity.capabilities,
                'trust_score': trust.overall_trust,
                'status': identity.status.value
            })
        
        return sorted(candidates, key=lambda x: x['trust_score'], reverse=True)
    
    def _generate_identity_hash(self, agent_id: str) -> str:
        """生成身份哈希"""
        return hashlib.sha256(agent_id.encode()).hexdigest()[:16]
    
    # ==================== 信誉注册表 ====================
    
    def record_interaction(self, agent_id: str, quality_score: float,
                          interaction_type: str = "general") -> ReputationRecord:
        """
        【信誉更新】记录一次交互，更新信誉
        
        Args:
            agent_id: Agent ID
            quality_score: 质量评分 0-1
            interaction_type: 交互类型
            
        Returns:
            更新后的信誉记录
        """
        if agent_id not in self.reputation_registry:
            raise ValueError(f"Agent {agent_id} 未注册")
        
        record = self.reputation_registry[agent_id]
        
        # 更新交互统计
        record.total_interactions += 1
        record.last_interaction = datetime.now()
        
        if quality_score >= 0.6:
            record.successful_interactions += 1
        else:
            record.failed_interactions += 1
        
        # 更新评分历史
        record.quality_scores.append(quality_score)
        if len(record.quality_scores) > 100:  # 保留最近100条
            record.quality_scores = record.quality_scores[-100:]
        
        # 重算平均分
        record.avg_quality_score = np.mean(record.quality_scores)
        
        # 更新各维度指标
        record.reliability_score = (
            record.successful_interactions / max(1, record.total_interactions)
        )
        record.consistency_score = 1.0 - np.std(record.quality_scores) if len(record.quality_scores) > 1 else 0.5
        record.responsiveness_score = min(1.0, record.avg_quality_score * 1.2)
        
        # 更新信誉等级
        record.reputation_tier = self._compute_reputation_tier(record)
        
        # 应用时间衰减
        self._apply_reputation_decay(record)
        
        print(f"  [Trust] 信誉更新: {agent_id} | 评分: {quality_score:.2f} | "
              f"成功率: {record.reliability_score:.1%} | 等级: {record.reputation_tier}")
        
        return record
    
    def _apply_reputation_decay(self, record: ReputationRecord):
        """应用信誉衰减（基于时间）"""
        if record.last_interaction:
            days_since = (datetime.now() - record.last_interaction).days
            if days_since > 30:  # 超过30天未交互
                decay_factor = self.reputation_decay_rate ** (days_since // 30)
                record.avg_quality_score *= decay_factor
    
    def _compute_reputation_tier(self, record: ReputationRecord) -> str:
        """计算信誉等级"""
        score = record.avg_quality_score
        interactions = record.total_interactions
        
        if score >= 0.9 and interactions >= 50:
            return "elite"
        elif score >= 0.8 and interactions >= 20:
            return "trusted"
        elif score >= 0.6 and interactions >= 5:
            return "experienced"
        else:
            return "newcomer"
    
    def get_reputation(self, agent_id: str) -> Optional[ReputationRecord]:
        """获取信誉记录"""
        return self.reputation_registry.get(agent_id)
    
    # ==================== 验证注册表 ====================
    
    def request_validation(self, agent_id: str, 
                          validation_type: str) -> Tuple[str, Dict]:
        """
        【验证请求】请求能力验证
        
        Args:
            agent_id: Agent ID
            validation_type: 验证类型
            
        Returns:
            (challenge_id, challenge_data)
        """
        if agent_id not in self.identity_registry:
            raise ValueError(f"Agent {agent_id} 未注册")
        
        challenge_id = f"ch_{hash(agent_id + validation_type) % 10**8:08d}"
        challenge_data = self.challenge_library.get(validation_type, {})
        
        print(f"  [Trust] 验证请求: {agent_id} | 类型: {validation_type} | 挑战ID: {challenge_id}")
        
        return challenge_id, challenge_data
    
    def submit_validation_proof(self, agent_id: str, challenge_id: str,
                                proof_data: Dict, 
                                validation_result: bool,
                                confidence: float = 0.8) -> ValidationProof:
        """
        【验证提交】提交验证证明
        
        Args:
            agent_id: Agent ID
            challenge_id: 挑战ID
            proof_data: 证明数据
            validation_result: 验证结果
            confidence: 置信度
            
        Returns:
            ValidationProof: 验证证明
        """
        proof = ValidationProof(
            validation_id=f"vp_{hash(challenge_id) % 10**8:08d}",
            agent_id=agent_id,
            validation_type=proof_data.get('type', 'unknown'),
            challenge_id=challenge_id,
            proof_data=proof_data,
            passed=validation_result,
            confidence=confidence,
            proof_level=3 if validation_result else 1,
            expires_at=datetime.now()
        )
        
        self.validation_registry[proof.validation_id] = proof
        
        if validation_result:
            self.stats['validations_passed'] += 1
        else:
            self.stats['validations_failed'] += 1
        
        # 更新身份验证状态
        if agent_id in self.identity_registry:
            self.identity_registry[agent_id].last_verified = datetime.now()
        
        print(f"  [Trust] 验证提交: {agent_id} | 结果: {'通过' if validation_result else '未通过'} "
              f"| 置信度: {confidence:.2f} | 证明级别: {proof.proof_level}")
        
        return proof
    
    def get_validations(self, agent_id: str) -> List[ValidationProof]:
        """获取Agent的所有验证证明"""
        return [
            v for v in self.validation_registry.values()
            if v.agent_id == agent_id
        ]
    
    # ==================== 信任计算 ====================
    
    def compute_trust(self, agent_id: str) -> TrustMetrics:
        """
        【信任计算】计算综合信任度
        
        信任 = f(身份信任, 信誉信任, 能力信任)
        
        Args:
            agent_id: Agent ID
            
        Returns:
            TrustMetrics: 综合信任指标
        """
        metrics = TrustMetrics(agent_id=agent_id)
        
        # 1. 身份信任
        metrics.identity_trust = self._compute_identity_trust(agent_id)
        
        # 2. 信誉信任
        metrics.reputation_trust = self._compute_reputation_trust(agent_id)
        
        # 3. 能力信任
        metrics.capability_trust = self._compute_capability_trust(agent_id)
        
        # 综合信任（加权平均）
        weights = self.trust_weights
        metrics.overall_trust = (
            metrics.identity_trust * weights['identity'] +
            metrics.reputation_trust * weights['reputation'] +
            metrics.capability_trust * weights['capability']
        )
        
        # 风险评估
        metrics.risk_level, metrics.risk_factors = self._assess_risk(agent_id, metrics)
        
        metrics.calculated_at = datetime.now()
        
        # 缓存
        self.trust_index[agent_id] = metrics
        
        return metrics
    
    def _compute_identity_trust(self, agent_id: str) -> float:
        """计算身份信任"""
        if agent_id not in self.identity_registry:
            return 0.0
        
        identity = self.identity_registry[agent_id]
        
        # 基于状态的信任
        status_trust = {
            RegistryStatus.ACTIVE: 1.0,
            RegistryStatus.PENDING: 0.5,
            RegistryStatus.SUSPENDED: 0.2,
            RegistryStatus.REVOKED: 0.0
        }.get(identity.status, 0.0)
        
        # 基于验证的信任加成
        validations = self.get_validations(agent_id)
        identity_validations = [v for v in validations if v.validation_type == 'identity']
        if identity_validations:
            validation_trust = np.mean([v.confidence * v.proof_level / 3 for v in identity_validations])
            status_trust = min(1.0, status_trust + validation_trust * 0.2)
        
        return status_trust
    
    def _compute_reputation_trust(self, agent_id: str) -> float:
        """计算信誉信任"""
        if agent_id not in self.reputation_registry:
            return 0.0
        
        record = self.reputation_registry[agent_id]
        
        # 多维度信誉信任
        reliability = record.reliability_score
        consistency = record.consistency_score
        responsiveness = record.responsiveness_score
        
        # 信誉等级加成
        tier_bonus = {
            'elite': 0.15,
            'trusted': 0.10,
            'experienced': 0.05,
            'newcomer': 0.0
        }.get(record.reputation_tier, 0.0)
        
        trust = (reliability * 0.4 + consistency * 0.3 + responsiveness * 0.3) + tier_bonus
        
        return min(1.0, trust)
    
    def _compute_capability_trust(self, agent_id: str) -> float:
        """计算能力信任"""
        validations = self.get_validations(agent_id)
        
        if not validations:
            return 0.3  # 默认能力信任
        
        # 基于能力验证的信任
        capability_validations = [v for v in validations if v.passed]
        
        if not capability_validations:
            return 0.2
        
        # 加权计算
        total_weight = 0
        weighted_sum = 0
        
        for v in capability_validations:
            weight = v.proof_level * v.confidence
            weighted_sum += weight
            total_weight += v.proof_level
        
        return min(1.0, weighted_sum / max(1, total_weight) * 1.5)
    
    def _assess_risk(self, agent_id: str, metrics: TrustMetrics) -> Tuple[str, List[str]]:
        """风险评估"""
        risk_factors = []
        
        if metrics.overall_trust < 0.3:
            risk_factors.append("信任度过低")
        
        if agent_id in self.reputation_registry:
            record = self.reputation_registry[agent_id]
            if record.failed_interactions > record.successful_interactions:
                risk_factors.append("失败率过高")
        
        # 检查验证过期
        validations = self.get_validations(agent_id)
        if validations:
            latest = max(v.validated_at for v in validations)
            days_since = (datetime.now() - latest).days
            if days_since > 90:
                risk_factors.append("验证过期")
        
        # 风险等级
        if len(risk_factors) >= 3:
            risk_level = "high"
        elif len(risk_factors) >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level, risk_factors
    
    def get_trust_metrics(self, agent_id: str) -> TrustMetrics:
        """获取信任指标（带缓存）"""
        if agent_id in self.trust_index:
            return self.trust_index[agent_id]
        return self.compute_trust(agent_id)
    
    # ==================== 信任推荐 ====================
    
    def recommend_agents(self, required_capabilities: List[str],
                        min_trust: float = 0.5,
                        limit: int = 5) -> List[Dict]:
        """
        【信任推荐】基于信任选择最佳Agent
        
        Args:
            required_capabilities: 所需能力
            min_trust: 最低信任要求
            limit: 返回数量限制
            
        Returns:
            推荐的Agent列表
        """
        candidates = self.discover_agents(
            capability_filter=required_capabilities,
            min_trust=min_trust
        )
        
        return candidates[:limit]
    
    def get_trust_report(self, agent_id: str) -> Dict:
        """生成完整信任报告"""
        metrics = self.get_trust_metrics(agent_id)
        reputation = self.get_reputation(agent_id)
        validations = self.get_validations(agent_id)
        
        return {
            'agent_id': agent_id,
            'trust_metrics': {
                'overall_trust': metrics.overall_trust,
                'identity_trust': metrics.identity_trust,
                'reputation_trust': metrics.reputation_trust,
                'capability_trust': metrics.capability_trust,
                'risk_level': metrics.risk_level,
                'risk_factors': metrics.risk_factors
            },
            'reputation': {
                'tier': reputation.reputation_tier if reputation else 'unknown',
                'total_interactions': reputation.total_interactions if reputation else 0,
                'success_rate': reputation.reliability_score if reputation else 0,
                'avg_quality': reputation.avg_quality_score if reputation else 0
            },
            'validations': {
                'total': len(validations),
                'passed': len([v for v in validations if v.passed]),
                'proof_level': max([v.proof_level for v in validations], default=0)
            },
            'calculated_at': metrics.calculated_at.isoformat()
        }


def demonstrate_trust_registry():
    """信任注册引擎演示"""
    print("\n" + "=" * 60)
    print("ERC-8004信任注册引擎演示")
    print("=" * 60)
    
    # 初始化引擎
    engine = TrustRegistryEngine(dim=64)
    
    # 注册多个Agent
    print("\n【1. 身份注册】")
    engine.register_identity(
        "reasoner_001", "reasoning",
        ["logical_analysis", "problem_solving", "math_proof"]
    )
    engine.register_identity(
        "creative_001", "creative",
        ["idea_generation", "storytelling", "design"]
    )
    engine.register_identity(
        "verifier_001", "verification",
        ["validation", "quality_check", "security_audit"]
    )
    
    # 更新信誉
    print("\n【2. 信誉积累】")
    for _ in range(10):
        engine.record_interaction("reasoner_001", np.random.uniform(0.7, 0.95))
    engine.record_interaction("reasoner_001", 0.55)  # 一次低分
    
    for _ in range(5):
        engine.record_interaction("creative_001", np.random.uniform(0.6, 0.9))
    
    # 能力验证
    print("\n【3. 能力验证】")
    challenge_id, _ = engine.request_validation("reasoner_001", "reasoning_challenge")
    engine.submit_validation_proof(
        "reasoner_001", challenge_id,
        {'type': 'capability', 'score': 0.92},
        validation_result=True,
        confidence=0.92
    )
    
    # 信任计算
    print("\n【4. 信任评估】")
    trust_report = engine.get_trust_report("reasoner_001")
    metrics = trust_report['trust_metrics']
    
    print(f"\n  Agent: {trust_report['agent_id']}")
    print(f"  综合信任: {metrics['overall_trust']:.3f}")
    print(f"    - 身份信任: {metrics['identity_trust']:.3f}")
    print(f"    - 信誉信任: {metrics['reputation_trust']:.3f}")
    print(f"    - 能力信任: {metrics['capability_trust']:.3f}")
    print(f"  信誉等级: {trust_report['reputation']['tier']}")
    print(f"  风险等级: {metrics['risk_level']}")
    print(f"  风险因素: {metrics['risk_factors'] or '无'}")
    
    # Agent发现
    print("\n【5. Agent发现】")
    recommended = engine.recommend_agents(
        ["logical_analysis"],
        min_trust=0.3,
        limit=3
    )
    print(f"  发现 {len(recommended)} 个符合条件的Agent:")
    for agent in recommended:
        print(f"    - {agent['agent_id']}: 信任 {agent['trust_score']:.3f}")
    
    # 统计
    stats = engine.stats
    print(f"\n【6. 统计信息】")
    print(f"  总注册数: {stats['total_registrations']}")
    print(f"  活跃Agent: {stats['active_agents']}")
    print(f"  验证通过率: {stats['validations_passed']}/{stats['validations_passed'] + stats['validations_failed']}")
    
    return engine, trust_report


if __name__ == "__main__":
    demonstrate_trust_registry()
