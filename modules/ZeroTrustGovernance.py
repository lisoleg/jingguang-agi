#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
零信任分层治理模块 (Zero-Trust Governance)
基于《零信任分布式指挥控制：RBAC分层授权与边缘自治执行》

核心概念：
- ZTA三组件：PEP(策略执行点)、PDP(策略决策点)、PAP(策略管理点)
- 持续验证：永不信任，始终验证
- 分层授权：L1-L5 五层结构对应的权限隔离
- 边缘自治：在边缘节点执行局部决策，降低中心依赖
- 动态风险评估：实时计算访问风险分数

版本：AGI 13.0 第32模块
论文来源：《零信任分布式指挥控制》复合体理学系列
"""

import hashlib
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class TrustLevel(Enum):
    """信任等级"""
    ZERO_TRUST = "zero_trust"        # 零信任（完全不信任）
    MINIMAL_TRUST = "minimal_trust"  # 最小信任
    CONDITIONAL_TRUST = "conditional" # 条件信任
    FULL_TRUST = "full_trust"        # 完全信任（仅限核心层）
    BLOCKED = "blocked"              # 阻断


class AuthorizationScope(Enum):
    """授权范围"""
    EXECUTION = "execution"          # 执行权
    READ = "read"                    # 读取权
    WRITE = "write"                  # 写入权
    DELETE = "delete"                # 删除权
    ADMIN = "admin"                 # 管理权
    SOVEREIGN = "sovereign"          # 主权（最高权限）


class PolicyDecision(Enum):
    """策略决策结果"""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"          # 需要二次验证
    ESCALATE = "escalate"           # 升级到更高层


@dataclass
class AccessRequest:
    """访问请求"""
    request_id: str
    subject_id: str                  # 请求主体ID
    resource_id: str                 # 目标资源ID
    action: AuthorizationScope       # 请求的操作类型
    context: Dict[str, Any]          # 上下文信息（时间、地点、设备等）
    risk_factors: Dict[str, float] = field(default_factory=dict)
    trust_score: float = 0.5         # 当前信任分数 [0,1]
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class PolicyRule:
    """策略规则"""
    rule_id: str
    name: str
    description: str
    
    # 触发条件
    subject_pattern: str             # 主体匹配模式
    resource_pattern: str            # 资源匹配模式
    action_pattern: str              # 操作匹配模式
    
    # 层间关联（必须放在有默认值的字段前面）
    applicable_layers: List[int]     # 适用的层（1-5）
    
    # 决策参数（有默认值，必须放在后面）
    required_trust_level: TrustLevel
    required_trust_score: float     # 最低信任分数
    require_mfa: bool = False        # 是否需要多因素验证
    risk_threshold: float = 0.7     # 风险阈值
    priority: int = 0                # 优先级（数字越大优先级越高）
    
    def matches(self, request: AccessRequest, resource_layer: int) -> bool:
        """检查规则是否匹配请求"""
        if resource_layer not in self.applicable_layers:
            return False
        
        # 简化的模式匹配
        if self.subject_pattern not in ["*", request.subject_id]:
            return False
        if self.resource_pattern not in ["*", request.resource_id]:
            return False
        if self.action_pattern not in ["*", request.action.value]:
            return False
        
        return True


@dataclass
class GovernanceAudit:
    """治理审计记录"""
    audit_id: str
    timestamp: float
    request_id: str
    decision: PolicyDecision
    trust_level: TrustLevel
    risk_score: float
    policy_applied: str
    reason: str


@dataclass
class ZeroTrustResult:
    """零信任治理分析结果"""
    request_id: str
    decision: PolicyDecision
    trust_level: TrustLevel
    trust_score: float
    risk_score: float
    applied_policy: Optional[str]
    mfa_required: bool
    escalation_needed: bool
    layer_accessible: List[int]
    audit_id: str
    reason: str
    insight: str


class ZeroTrustGovernance:
    """
    零信任分层治理引擎
    
    核心功能：
    1. 持续验证：每次访问都进行身份和权限验证
    2. 最小权限：仅授予完成任务所需的最小权限
    3. 分层授权：L1-L5 对应不同的权限隔离级别
    4. 动态风险评估：实时计算访问风险
    5. 边缘自治：在边缘节点执行局部决策
    6. 审计追溯：完整的访问审计日志
    
    ZTA三组件：
    - PEP (Policy Enforcement Point): 策略执行点
    - PDP (Policy Decision Point): 策略决策点
    - PAP (Policy Administration Point): 策略管理点
    """

    def __init__(self):
        self.version = "1.0.0"
        
        # 信任等级阈值
        self.trust_thresholds = {
            TrustLevel.ZERO_TRUST: 0.0,
            TrustLevel.MINIMAL_TRUST: 0.2,
            TrustLevel.CONDITIONAL_TRUST: 0.5,
            TrustLevel.FULL_TRUST: 0.9
        }
        
        # 默认策略规则
        self.policy_rules: List[PolicyRule] = self._init_default_policies()
        
        # 审计日志
        self.audit_log: List[GovernanceAudit] = []
        
        # 资源层映射
        self.resource_layer_map: Dict[str, int] = {}
        
        # PEP/PDP/PAP 组件状态
        self.pep_active = True
        self.pdp_active = True
        self.pap_active = True

    def _init_default_policies(self) -> List[PolicyRule]:
        """初始化默认策略规则"""
        return [
            # L1 本体层 - 最高安全级别
            PolicyRule(
                rule_id="pol_l1_sovereign",
                name="L1主权访问",
                description="L1本体层主权操作需要最高信任",
                subject_pattern="*",
                resource_pattern="l1_*",
                action_pattern="*",
                required_trust_level=TrustLevel.FULL_TRUST,
                required_trust_score=0.95,
                require_mfa=True,
                risk_threshold=0.3,
                applicable_layers=[1],
                priority=100
            ),
            # L2 投射生成层 - 高安全
            PolicyRule(
                rule_id="pol_l2_admin",
                name="L2管理访问",
                description="L2投射层管理操作需要高信任",
                subject_pattern="*",
                resource_pattern="l2_*",
                action_pattern="admin",
                required_trust_level=TrustLevel.CONDITIONAL_TRUST,
                required_trust_score=0.7,
                require_mfa=True,
                risk_threshold=0.5,
                applicable_layers=[2],
                priority=80
            ),
            # L3 前物理层 - 中等安全
            PolicyRule(
                rule_id="pol_l3_execution",
                name="L3执行访问",
                description="L3世界帧执行操作",
                subject_pattern="*",
                resource_pattern="l3_*",
                action_pattern="execution",
                required_trust_level=TrustLevel.MINIMAL_TRUST,
                required_trust_score=0.4,
                require_mfa=False,
                risk_threshold=0.6,
                applicable_layers=[3],
                priority=60
            ),
            # L4 认知主体层 - 读取为主
            PolicyRule(
                rule_id="pol_l4_read",
                name="L4读取访问",
                description="L4认知层读取操作",
                subject_pattern="*",
                resource_pattern="l4_*",
                action_pattern="read",
                required_trust_level=TrustLevel.MINIMAL_TRUST,
                required_trust_score=0.3,
                require_mfa=False,
                risk_threshold=0.7,
                applicable_layers=[4],
                priority=40
            ),
            # L5 现象层 - 开放访问
            PolicyRule(
                rule_id="pol_l5_open",
                name="L5开放访问",
                description="L5现象层开放访问",
                subject_pattern="*",
                resource_pattern="l5_*",
                action_pattern="*",
                required_trust_level=TrustLevel.ZERO_TRUST,
                required_trust_score=0.1,
                require_mfa=False,
                risk_threshold=0.9,
                applicable_layers=[5],
                priority=20
            ),
            # 危险操作全局规则
            PolicyRule(
                rule_id="pol_delete_high",
                name="高危删除操作",
                description="删除操作需要额外验证",
                subject_pattern="*",
                resource_pattern="*",
                action_pattern="delete",
                required_trust_level=TrustLevel.CONDITIONAL_TRUST,
                required_trust_score=0.6,
                require_mfa=True,
                risk_threshold=0.4,
                applicable_layers=[1, 2, 3, 4, 5],
                priority=90
            )
        ]

    def _generate_request_id(self, subject: str, resource: str) -> str:
        """生成请求ID"""
        data = f"{subject}:{resource}:{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def _generate_audit_id(self, request_id: str) -> str:
        """生成审计ID"""
        return f"audit_{request_id}"

    def _calculate_risk_score(self, request: AccessRequest) -> float:
        """
        计算风险分数
        基于上下文、信任分数、风险因素综合评估
        """
        risk = 0.0
        
        # 1. 信任分数风险（信任越低风险越高）
        trust_risk = 1.0 - request.trust_score
        risk += trust_risk * 0.4
        
        # 2. 操作类型风险
        action_risks = {
            AuthorizationScope.DELETE: 0.3,
            AuthorizationScope.ADMIN: 0.25,
            AuthorizationScope.WRITE: 0.15,
            AuthorizationScope.EXECUTION: 0.1,
            AuthorizationScope.READ: 0.05,
            AuthorizationScope.SOVEREIGN: 0.4
        }
        risk += action_risks.get(request.action, 0.1)
        
        # 3. 上下文风险因素
        context_risks = request.context.get('risk_factors', {})
        for factor, weight in context_risks.items():
            risk += weight * 0.1
        
        # 4. 时间风险（非工作时间风险增加）
        if request.context.get('is_work_hours', True) is False:
            risk += 0.1
        
        # 5. 设备风险（未知设备风险增加）
        if request.context.get('device_known', True) is False:
            risk += 0.15
        
        return min(1.0, max(0.0, risk))

    def _evaluate_trust_level(self, score: float) -> TrustLevel:
        """根据信任分数确定信任等级"""
        if score >= 0.9:
            return TrustLevel.FULL_TRUST
        elif score >= 0.5:
            return TrustLevel.CONDITIONAL_TRUST
        elif score >= 0.2:
            return TrustLevel.MINIMAL_TRUST
        elif score > 0.0:
            return TrustLevel.ZERO_TRUST
        else:
            return TrustLevel.BLOCKED

    def _pep_enforce(self, request: AccessRequest, decision: PolicyDecision) -> bool:
        """
        PEP: 策略执行点
        执行PDP的决策，阻止或放行请求
        """
        if decision == PolicyDecision.ALLOW:
            return True
        elif decision == PolicyDecision.DENY:
            return False
        elif decision == PolicyDecision.CHALLENGE:
            # 需要MFA验证后才能放行
            return request.context.get('mfa_verified', False)
        elif decision == PolicyDecision.ESCALATE:
            # 升级请求，暂不执行
            return False
        return False

    def _pdp_decide(self, request: AccessRequest) -> Tuple[PolicyDecision, Optional[PolicyRule], str]:
        """
        PDP: 策略决策点
        核心决策逻辑：评估请求并做出允许/拒绝/挑战/升级决定
        """
        # 1. 获取资源对应的层
        resource_id = request.resource_id
        layer = self.resource_layer_map.get(resource_id, 3)  # 默认L3
        
        # 2. 收集匹配规则（按优先级排序）
        matched_rules = [r for r in self.policy_rules if r.matches(request, layer)]
        matched_rules.sort(key=lambda x: x.priority, reverse=True)
        
        if not matched_rules:
            # 无匹配规则，默认允许L5，阻断L1-L2
            if layer >= 4:
                return PolicyDecision.ALLOW, None, "默认允许（无匹配规则）"
            else:
                return PolicyDecision.DENY, None, "默认阻断（高层无规则）"
        
        # 3. 应用最高优先级规则
        best_rule = matched_rules[0]
        
        # 4. 信任分数检查
        if request.trust_score < best_rule.required_trust_score:
            reason = f"信任分数不足：当前{request.trust_score:.2f}，需要{best_rule.required_trust_score:.2f}"
            if layer <= 2:
                return PolicyDecision.DENY, best_rule, reason
            else:
                return PolicyDecision.CHALLENGE, best_rule, reason
        
        # 5. 风险分数检查
        risk_score = self._calculate_risk_score(request)
        if risk_score > best_rule.risk_threshold:
            reason = f"风险过高：{risk_score:.2f} > 阈值{best_rule.risk_threshold:.2f}"
            return PolicyDecision.ESCALATE, best_rule, reason
        
        # 6. MFA检查
        if best_rule.require_mfa and not request.context.get('mfa_verified', False):
            return PolicyDecision.CHALLENGE, best_rule, "需要多因素验证"
        
        # 7. 全部通过，允许访问
        return PolicyDecision.ALLOW, best_rule, "通过零信任验证"

    def _pap_manage(self, request: AccessRequest, decision: PolicyDecision, 
                   rule: Optional[PolicyRule]) -> Dict[str, Any]:
        """
        PAP: 策略管理点
        管理策略更新和权限授予
        """
        resource_id = request.resource_id
        layer = self.resource_layer_map.get(resource_id, 3)
        
        # 计算可访问的层级
        accessible_layers = []
        for l in range(1, 6):
            if l <= layer:
                # 信任分数决定能访问多高层
                access_depth = int(request.trust_score * l)
                if l <= access_depth + 1:
                    accessible_layers.append(l)
        
        return {
            'granted_scopes': [request.action],
            'accessible_layers': accessible_layers,
            'session_timeout': 300 * (1 - request.trust_score * 0.5),  # 低信任短会话
            'requires_revalidation': decision == PolicyDecision.CHALLENGE
        }

    def evaluate_access(self, subject_id: str, resource_id: str, 
                      action: str, context: Dict[str, Any] = None) -> ZeroTrustResult:
        """
        评估访问请求（PEP入口）
        
        参数：
            subject_id: 请求主体ID
            resource_id: 目标资源ID
            action: 操作类型 (read/write/execute/delete/admin/sovereign)
            context: 上下文信息
        
        返回：
            ZeroTrustResult 包含决策、信任等级、风险分数等
        """
        if context is None:
            context = {}
        
        # 解析操作类型
        action_enum = AuthorizationScope(action) if action in [a.value for a in AuthorizationScope] else AuthorizationScope.READ
        
        # 创建访问请求
        request = AccessRequest(
            request_id=self._generate_request_id(subject_id, resource_id),
            subject_id=subject_id,
            resource_id=resource_id,
            action=action_enum,
            context=context,
            trust_score=context.get('trust_score', 0.5)
        )
        
        # PDP决策
        decision, policy, reason = self._pdp_decide(request)
        
        # 计算风险和信任
        risk_score = self._calculate_risk_score(request)
        trust_level = self._evaluate_trust_level(request.trust_score)
        
        # PEP执行
        enforced = self._pep_enforce(request, decision)
        if enforced:
            final_decision = PolicyDecision.ALLOW
        else:
            final_decision = decision
        
        # PAP管理
        pap_result = self._pap_manage(request, decision, policy)
        
        # 生成审计记录
        audit_id = self._generate_audit_id(request.request_id)
        audit = GovernanceAudit(
            audit_id=audit_id,
            timestamp=time.time(),
            request_id=request.request_id,
            decision=final_decision,
            trust_level=trust_level,
            risk_score=risk_score,
            policy_applied=policy.rule_id if policy else "default",
            reason=reason
        )
        self.audit_log.append(audit)
        
        # 生成洞察
        insight = self._generate_insight(trust_level, risk_score, decision, policy)
        
        return ZeroTrustResult(
            request_id=request.request_id,
            decision=final_decision,
            trust_level=trust_level,
            trust_score=request.trust_score,
            risk_score=risk_score,
            applied_policy=policy.rule_id if policy else None,
            mfa_required=policy.require_mfa if policy else False,
            escalation_needed=decision == PolicyDecision.ESCALATE,
            layer_accessible=pap_result['accessible_layers'],
            audit_id=audit_id,
            reason=reason,
            insight=insight
        )

    def _generate_insight(self, trust_level: TrustLevel, risk_score: float,
                         decision: PolicyDecision, policy: Optional[PolicyRule]) -> str:
        """生成治理洞察"""
        parts = []
        
        # 信任状态
        trust_map = {
            TrustLevel.FULL_TRUST: "完全信任（核心层认证）",
            TrustLevel.CONDITIONAL_TRUST: "条件信任（持续监控中）",
            TrustLevel.MINIMAL_TRUST: "最小信任（限制访问）",
            TrustLevel.ZERO_TRUST: "零信任（每次验证）",
            TrustLevel.BLOCKED: "已阻断"
        }
        parts.append(f"当前信任状态：{trust_map.get(trust_level, '未知')}")
        
        # 风险评估
        if risk_score < 0.3:
            parts.append("风险等级：低（操作安全）")
        elif risk_score < 0.6:
            parts.append("风险等级：中（建议监控）")
        else:
            parts.append("风险等级：高（需严格验证）")
        
        # 决策结果
        decision_map = {
            PolicyDecision.ALLOW: "决策：允许（已通过零信任验证）",
            PolicyDecision.DENY: "决策：拒绝（安全策略阻断）",
            PolicyDecision.CHALLENGE: "决策：挑战（需MFA验证）",
            PolicyDecision.ESCALATE: "决策：升级（需人工审批）"
        }
        parts.append(decision_map.get(decision, ""))
        
        # 策略建议
        if policy:
            if policy.require_mfa:
                parts.append("建议：启用多因素认证增强安全")
        
        return "；".join(parts)

    def register_resource_layer(self, resource_id: str, layer: int):
        """注册资源所属层级"""
        if 1 <= layer <= 5:
            self.resource_layer_map[resource_id] = layer

    def add_policy_rule(self, rule: PolicyRule):
        """添加策略规则"""
        self.policy_rules.append(rule)
        self.policy_rules.sort(key=lambda x: x.priority, reverse=True)

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取审计轨迹"""
        return [
            {
                'audit_id': a.audit_id,
                'timestamp': a.timestamp,
                'request_id': a.request_id,
                'decision': a.decision.value,
                'trust_level': a.trust_level.value,
                'risk_score': a.risk_score,
                'policy': a.policy_applied,
                'reason': a.reason
            }
            for a in self.audit_log[-limit:]
        ]

    def process(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        简化的处理接口（用于AGI集成）
        从文本中提取治理相关信息并评估
        
        参数：
            text: 输入文本
            context: 额外的上下文信息
        
        返回：
            dict 包含治理分析结果
        """
        if context is None:
            context = {}
        
        # 从文本中推断资源、操作和信任分数
        resource_id = context.get('resource_id', self._infer_resource(text))
        action = context.get('action', self._infer_action(text))
        trust_score = context.get('trust_score', self._infer_trust(text))
        
        # 注册资源层级
        self.register_resource_layer(resource_id, context.get('layer', 3))
        
        # 评估访问
        result = self.evaluate_access(
            subject_id=context.get('subject_id', 'agi_core'),
            resource_id=resource_id,
            action=action,
            context={**context, 'trust_score': trust_score}
        )
        
        return {
            'module': 'ZeroTrustGovernance',
            'version': self.version,
            'request_id': result.request_id,
            'decision': result.decision.value,
            'trust_level': result.trust_level.value,
            'trust_score': result.trust_score,
            'risk_score': result.risk_score,
            'applied_policy': result.applied_policy,
            'mfa_required': result.mfa_required,
            'escalation_needed': result.escalation_needed,
            'accessible_layers': result.layer_accessible,
            'audit_id': result.audit_id,
            'reason': result.reason,
            'insight': result.insight
        }

    def _infer_resource(self, text: str) -> str:
        """从文本推断资源ID"""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['本体', 'ontology', 'l1']):
            return 'l1_ontology_core'
        elif any(kw in text_lower for kw in ['投射', 'project', 'l2']):
            return 'l2_projective_genesis'
        elif any(kw in text_lower for kw in ['物理', 'physical', 'world', 'l3']):
            return 'l3_world_frame'
        elif any(kw in text_lower for kw in ['认知', 'cognitive', 'l4']):
            return 'l4_cognitive_agent'
        else:
            return 'l5_phenomenal_layer'

    def _infer_action(self, text: str) -> str:
        """从文本推断操作类型"""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['删除', 'delete', '移除']):
            return 'delete'
        elif any(kw in text_lower for kw in ['管理', 'admin', '配置']):
            return 'admin'
        elif any(kw in text_lower for kw in ['写入', 'write', '修改', '更新']):
            return 'write'
        elif any(kw in text_lower for kw in ['执行', 'execute', 'run', '运行']):
            return 'execution'
        else:
            return 'read'

    def _infer_trust(self, text: str) -> float:
        """从文本推断信任分数"""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['核心', '主权', 'sovereign', '绝对']):
            return 0.3  # 核心操作默认低信任
        elif any(kw in text_lower for kw in ['敏感', '危险', '删除']):
            return 0.4
        else:
            return 0.6  # 普通操作中等信任


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("零信任分层治理模块测试 (Zero-Trust Governance)")
    print("=" * 60)
    
    engine = ZeroTrustGovernance()
    
    # 测试场景
    test_cases = [
        {
            'name': '测试1: L5普通读取（低信任）',
            'subject': 'user_001',
            'resource': 'l5_phenomenal_layer',
            'action': 'read',
            'context': {
                'trust_score': 0.6,
                'device_known': True,
                'is_work_hours': True
            }
        },
        {
            'name': '测试2: L2管理操作（高信任+MFA）',
            'subject': 'admin_001',
            'resource': 'l2_projective_genesis',
            'action': 'admin',
            'context': {
                'trust_score': 0.7,
                'device_known': True,
                'mfa_verified': True
            }
        },
        {
            'name': '测试3: L1危险删除（信任不足）',
            'subject': 'user_001',
            'resource': 'l1_ontology_core',
            'action': 'delete',
            'context': {
                'trust_score': 0.5,
                'device_known': False
            }
        },
        {
            'name': '测试4: L3执行操作（中等信任）',
            'subject': 'executor_001',
            'resource': 'l3_world_frame',
            'action': 'execution',
            'context': {
                'trust_score': 0.4,
                'device_known': True,
                'is_work_hours': True
            }
        }
    ]
    
    # 执行测试
    for i, case in enumerate(test_cases, 1):
        print(f"\n{case['name']}")
        print("-" * 60)
        
        result = engine.evaluate_access(
            case['subject'],
            case['resource'],
            case['action'],
            case['context']
        )
        
        print(f"  请求ID: {result.request_id}")
        print(f"  决策: {result.decision.value}")
        print(f"  信任等级: {result.trust_level.value}")
        print(f"  信任分数: {result.trust_score:.3f}")
        print(f"  风险分数: {result.risk_score:.3f}")
        print(f"  应用策略: {result.applied_policy}")
        print(f"  需要MFA: {result.mfa_required}")
        print(f"  需要升级: {result.escalation_needed}")
        print(f"  可访问层: {result.layer_accessible}")
        print(f"  原因: {result.reason}")
        print(f"  洞察: {result.insight}")
    
    # 测试 process 接口
    print("\n" + "=" * 60)
    print("测试 process 接口（从文本推断）")
    print("=" * 60)
    
    test_texts = [
        "请读取L5现象层的数据",
        "我要删除L1本体层的配置",
        "执行L3世界帧的更新操作"
    ]
    
    for text in test_texts:
        print(f"\n输入文本: {text}")
        result = engine.process(text)
        print(f"  决策: {result['decision']}")
        print(f"  信任等级: {result['trust_level']}")
        print(f"  风险分数: {result['risk_score']:.3f}")
        print(f"  洞察: {result['insight'][:50]}...")
    
    # 显示审计日志
    print("\n" + "=" * 60)
    print("审计日志（最近5条）")
    print("=" * 60)
    audit_trail = engine.get_audit_trail(limit=5)
    for audit in audit_trail:
        print(f"  {audit['audit_id']}: {audit['decision']} - {audit['reason'][:30]}...")
    
    print("\n✅ 零信任分层治理模块测试完成！")
