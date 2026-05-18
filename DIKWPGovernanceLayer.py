# -*- coding: utf-8 -*-
"""
模块42：DIKWPGovernanceLayer —— 六层统一入口
复合体AGI 6.0的核心架构

来源：复合体AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13

这是复合体AGI 6.0的核心架构改变：
所有推理输出不再是裸字符串，而是DIKWP节点：
{content, D来源, I关系, K机制, W风险, P目的, R可信度}
"""

import time
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

# 导入所有DIKWP模块
from DIKWPDataLayer import DIKWPDataLayer, DIKWPLayer as DataLayerEnum
from DIKWPInfoLayer import DIKWPInfoLayer, InfoNode
from DIKWPKnowledgeLayer import DIKWPKnowledgeLayer, IGCTRAxis
from DIKWPWisdomLayer import DIKWPWisdomLayer, WisdomScore
from DIKWPPurposeLayer import DIKWPPurposeLayer, IntentCheckResult
from DIKWPReliabilityLayer import DIKWPReliabilityLayer, ProofEntry
from MemoryLedger import MemoryLedger, DIKWPLayer as MemoryLayerEnum
from ElasticCoordinationBus import ElasticCoordinationBus


@dataclass
class DIKWPNode:
    """
    DIKWP节点：六层语义治理的完整输出格式
    
    所有AGI输出都封装为这个结构：
    {
        content: 原始内容,
        D: {id, hash, source},
        I: {id, entity, node_type},
        K: {rules_applied, igctr_axis},
        W: {wisdom_score, should_proceed, risk},
        P: {allowed, alignment, scope},
        R: {id, r_score, bft_validated, lean_proof}
    }
    """
    content: str
    dikwp: Dict[str, Any] = field(default_factory=dict)
    governance_passed: bool = False
    cq_score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "dikwp": self.dikwp,
            "governance_passed": self.governance_passed,
            "cq_score": self.cq_score,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        return f"DIKWPNode({self.content[:30]}..., passed={self.governance_passed})"


class DIKWPGovernanceLayer:
    """
    DIKWP六层治理统一入口
    
    整合所有六层模块：
    - D层：数据证据溯源（DIKWPDataLayer）
    - I层：语义图谱（DIKWPInfoLayer）
    - K层：知识推理（DIKWPKnowledgeLayer）
    - W层：智慧决策（DIKWPWisdomLayer）
    - P层：目的约束（DIKWPPurposeLayer）
    - R层：可靠性验证（DIKWPReliabilityLayer）
    
    附加组件：
    - MemoryLedger：记忆主权管理
    - ElasticCoordinationBus：弹簧虫协调总线
    
    核心功能：
    1. governed_output() - 受治理的输出包装
    2. governed_inference() - 受治理的推理
    3. governed_action() - 受治理的行动执行
    4. get_system_health() - 系统健康检查
    5. compute_cq() - 计算意识商数
    """
    
    def __init__(self):
        # 初始化所有六层
        self.data_layer = DIKWPDataLayer()
        self.info_layer = DIKWPInfoLayer()
        self.knowledge_layer = DIKWPKnowledgeLayer(self.info_layer)
        self.wisdom_layer = DIKWPWisdomLayer()
        self.purpose_layer = DIKWPPurposeLayer()
        self.reliability_layer = DIKWPReliabilityLayer()
        
        # 附加组件
        self.memory_ledger = MemoryLedger()
        self.coordination_bus = ElasticCoordinationBus(self.purpose_layer)
        
        # 当前会话
        self._current_session: Optional[str] = None
        
        # 输出历史
        self.output_history: List[DIKWPNode] = []
        
        # 版本信息
        self.version = "6.0.0"
        self.initialized_at = time.time()
    
    def set_session(self, session_id: str, purpose: str = None, scopes: List[str] = None):
        """
        设置当前会话
        
        Args:
            session_id: 会话ID
            purpose: 会话目的（可选）
            scopes: 授权范围（可选）
        """
        self._current_session = session_id
        
        if purpose:
            self.purpose_layer.lock_purpose(
                session_id=session_id,
                purpose=purpose,
                scopes=scopes
            )
    
    def governed_output(self, 
                       content: str, 
                       session_id: str = None,
                       source: str = "AGI_inference",
                       action_scope: str = "read",
                       node_type: str = "_P",
                       store_memory: bool = True) -> DIKWPNode:
        """
        受DIKWP治理的输出包装器
        
        每个输出都附带完整的DIKWP元数据。
        这是复合体AGI 6.0的核心架构改变。
        
        Args:
            content: 输出内容
            session_id: 会话ID（None=使用当前会话）
            source: 数据来源
            action_scope: 行动范围
            node_type: 信息节点类型
            store_memory: 是否存储记忆
        
        Returns:
            DIKWPNode: 包含完整DIKWP元数据的输出节点
        """
        # 获取会话ID
        if session_id is None:
            session_id = self._current_session or "default"
        
        # ========================================
        # D层：记录原始来源
        # ========================================
        data_record = self.data_layer.ingest(
            content=content,
            source=source,
            confidence=0.95,
            tags=["output", source]
        )
        
        # ========================================
        # I层：提取信息节点
        # ========================================
        info_node = self.info_layer.add_node(
            entity=content[:100] + ("..." if len(content) > 100 else ""),
            node_type=node_type,
            context=session_id,
            parent_data_ids=[data_record.id]
        )
        
        # ========================================
        # P层：意图门禁
        # ========================================
        intent_check = self.purpose_layer.intent_guard(
            session_id, content, action_scope
        )
        
        # ========================================
        # W层：智慧评分
        # ========================================
        wisdom_score = self.wisdom_layer.evaluate(
            action=content,
            context={"scope": action_scope, "source": source},
            purpose_alignment=intent_check.alignment_score if intent_check else 0.5,
            data_confidence=data_record.confidence
        )
        
        # ========================================
        # R层：可靠性记录
        # ========================================
        proof_entry = self.reliability_layer.add_proof(
            claim=content[:200],
            evidence_ids=[data_record.id],
            r_score=data_record.confidence,
            metadata={
                "session_id": session_id,
                "source": source,
                "action_scope": action_scope
            }
        )
        
        # ========================================
        # 组装DIKWP节点
        # ========================================
        dikwp_node = DIKWPNode(
            content=content,
            dikwp={
                "D": {
                    "id": data_record.id,
                    "hash": data_record.hash,
                    "source": source,
                    "confidence": data_record.confidence
                },
                "I": {
                    "id": info_node.id,
                    "entity": info_node.entity,
                    "node_type": info_node.node_type,
                    "context": info_node.context_boundary
                },
                "K": {
                    "rules_applied": len(self.knowledge_layer.knowledge_rules),
                    "igctr_axes": list(set(
                        r.igctr_axis.value for r in self.knowledge_layer.knowledge_rules
                        if r.active
                    ))
                },
                "W": {
                    "wisdom_score": wisdom_score.total_score,
                    "should_proceed": wisdom_score.should_proceed,
                    "risk": wisdom_score.risk_w,
                    "s_data": wisdom_score.s_data,
                    "c_purpose": wisdom_score.c_purpose,
                    "decision": wisdom_score.decision
                },
                "P": {
                    "allowed": intent_check.allowed if intent_check else False,
                    "alignment": intent_check.alignment_score if intent_check else 0,
                    "scope": action_scope,
                    "purpose_hash": intent_check.purpose_hash if intent_check else ""
                },
                "R": {
                    "id": proof_entry.entry_id,
                    "r_score": proof_entry.r_score,
                    "bft_validated": proof_entry.bft_validated,
                    "lean_proof": bool(proof_entry.lean_proof)
                }
            },
            governance_passed=intent_check.allowed if intent_check else False and wisdom_score.should_proceed,
            cq_score=self._compute_cq_component()
        )
        
        # 记录到历史
        self.output_history.append(dikwp_node)
        
        # 限制历史长度
        if len(self.output_history) > 1000:
            self.output_history = self.output_history[-1000:]
        
        # ========================================
        # 记忆存储
        # ========================================
        if store_memory and dikwp_node.governance_passed:
            try:
                self.memory_ledger.remember(
                    content=content,
                    source=source,
                    purpose=f"session_{session_id}_output",
                    dikwp_layer=MemoryLayerEnum.I,
                    consent=True,
                    tags=["output", source, action_scope]
                )
            except ValueError:
                pass  # 未获同意时不存储
        
        return dikwp_node
    
    def governed_inference(self,
                          input_content: str,
                          context: Dict = None,
                          max_rules: int = 5) -> Dict:
        """
        受治理的推理
        
        Args:
            input_content: 输入内容
            context: 推理上下文
            max_rules: 最大应用的规则数
        
        Returns:
            Dict: 推理结果 + DIKWP元数据
        """
        context = context or {}
        
        # 知识推理
        inferences = self.knowledge_layer.infer(input_content, max_rules=max_rules)
        
        # 组合推理结果
        if inferences:
            best_inference = inferences[0]
            conclusion = best_inference["conclusion"]
            confidence = best_inference["confidence"]
        else:
            conclusion = f"基于'{input_content}'无匹配规则，提供通用响应"
            confidence = 0.5
        
        # 使用治理输出包装
        output = self.governed_output(
            content=conclusion,
            source="inference",
            action_scope="read",
            store_memory=True
        )
        
        return {
            "input": input_content,
            "output": output,
            "inferences": inferences,
            "context": context,
            "cq_score": self._compute_cq_component()
        }
    
    def governed_action(self,
                       action: str,
                       session_id: str = None,
                       action_scope: str = "execute",
                       context: Dict = None) -> Dict:
        """
        受治理的行动执行
        
        这是P层IntentGuard的核心应用：
        任何工具调用前必须通过意图门禁检查。
        
        Args:
            action: 行动描述
            session_id: 会话ID
            action_scope: 行动范围
            context: 行动上下文
        
        Returns:
            Dict: 行动结果 + 治理决策
        """
        session_id = session_id or self._current_session or "default"
        context = context or {}
        
        # ========================================
        # P层：意图门禁（强制前置检查）
        # ========================================
        intent_check = self.purpose_layer.intent_guard(
            session_id, action, action_scope
        )
        
        if not intent_check.allowed:
            # 记录拒绝
            self.coordination_bus._add_trace("action_rejected", {
                "action": action,
                "reason": intent_check.reason,
                "alignment": intent_check.alignment_score
            })
            
            return {
                "action": action,
                "allowed": False,
                "reason": intent_check.reason,
                "output": None,
                "cq_score": self._compute_cq_component()
            }
        
        # ========================================
        # W层：智慧评估
        # ========================================
        wisdom = self.wisdom_layer.evaluate(
            action=action,
            context=context,
            purpose_alignment=intent_check.alignment_score,
            data_confidence=0.8
        )
        
        # ========================================
        # 缓冲吸收（如果评估风险较高）
        # ========================================
        if wisdom.risk_w > 0.5:
            self.coordination_bus.absorb_shock(
                Exception(f"high_risk_action: {action}"),
                context={"action": action, "risk": wisdom.risk_w}
            )
        
        # ========================================
        # 资源分配检查
        # ========================================
        resource_ok = self.coordination_bus.allocate_resource(
            module=session_id,
            resource_type="compute",
            amount=0.1
        )
        
        if not resource_ok:
            return {
                "action": action,
                "allowed": False,
                "reason": "资源不足",
                "output": None,
                "cq_score": self._compute_cq_component()
            }
        
        # ========================================
        # 允许执行，生成输出
        # ========================================
        output = self.governed_output(
            content=f"执行动作: {action}",
            session_id=session_id,
            source="action_execution",
            action_scope=action_scope,
            store_memory=True
        )
        
        # 释放资源
        self.coordination_bus.release_resource(session_id, "compute", 0.1)
        
        return {
            "action": action,
            "allowed": True,
            "wisdom_score": wisdom.to_dict(),
            "output": output,
            "cq_score": self._compute_cq_component()
        }
    
    def _compute_cq_component(self) -> float:
        """计算意识商数组件（简化版）"""
        # 基于各层活跃度计算
        components = {
            "D": len(self.data_layer) / 100,
            "I": len(self.info_layer) / 50,
            "K": len(self.knowledge_layer) / 20,
            "W": len(self.wisdom_layer.evaluation_history) / 50,
            "P": len([l for l in self.purpose_layer.purpose_locks.values() if l.active]) / 5,
            "R": len(self.reliability_layer.proof_ledger) / 30
        }
        
        return sum(components.values()) / len(components) * 100
    
    def compute_cq(self) -> Dict:
        """计算完整意识商数"""
        # 调用R层的CQ计算
        r_cq = self.reliability_layer.compute_cq()
        
        # 添加协调总线因素
        health = self.coordination_bus.check_health()
        
        # 综合CQ
        base_cq = r_cq["cq_score"]
        health_factor = health["health_score"] * 20
        bus_factor = self.coordination_bus.global_purpose.energy * 10
        
        total_cq = (base_cq + health_factor + bus_factor) / 3
        
        return {
            "cq_score": total_cq,
            "grade": r_cq["grade"],
            "components": {
                **r_cq["components"],
                "health": health["health_score"],
                "energy": self.coordination_bus.global_purpose.energy,
                "governance": len(self.output_history) / 100
            },
            "health_status": health["status"],
            "timestamp": time.time()
        }
    
    def get_system_health(self) -> Dict:
        """
        获取DIKWP六层系统健康报告
        
        Returns:
            Dict: 完整的系统健康状态
        """
        # 各层健康状态
        layers = {
            "D_layer": {
                "name": "数据层",
                "records": len(self.data_layer),
                "integrity_rate": sum(
                    1 for r in self.data_layer.records.values()
                    if r.verify_integrity()
                ) / max(len(self.data_layer.records), 1)
            },
            "I_layer": {
                "name": "信息层",
                "nodes": len(self.info_layer),
                "edges": len(self.info_layer._edges),
                "pending_isomorphisms": len(self.info_layer.isomorphism_cache)
            },
            "K_layer": {
                "name": "知识层",
                "rules": len(self.knowledge_layer),
                "axes": {
                    axis.value: len(self.knowledge_layer.get_rules_by_axis(axis))
                    for axis in IGCTRAxis
                }
            },
            "W_layer": {
                "name": "智慧层",
                "evaluations": len(self.wisdom_layer.evaluation_history),
                "policies": len([p for p in self.wisdom_layer.risk_policies if p.active])
            },
            "P_layer": {
                "name": "目的层",
                "active_sessions": sum(
                    1 for l in self.purpose_layer.purpose_locks.values()
                    if l.active
                ),
                "total_checks": len(self.purpose_layer.intent_checks)
            },
            "R_layer": {
                "name": "可靠性层",
                "proof_entries": len(self.reliability_layer.proof_ledger),
                "reliable": len(self.reliability_layer.get_reliable_entries()),
                "bft_validated": sum(
                    1 for e in self.reliability_layer.proof_ledger.values()
                    if e.bft_validated
                )
            }
        }
        
        # 附加组件
        extras = {
            "memory_ledger": {
                "records": len(self.memory_ledger),
                "consent_rate": self.memory_ledger.consent_check()["consent_rate"]
            },
            "coordination_bus": self.coordination_bus.check_health()
        }
        
        # CQ
        cq = self.compute_cq()
        
        return {
            "version": self.version,
            "layers": layers,
            "extras": extras,
            "cq": cq,
            "output_history": len(self.output_history),
            "timestamp": time.time()
        }
    
    def export_state(self, filepath: str):
        """导出现场状态"""
        data = {
            "layers": {
                "D": {
                    "records": len(self.data_layer),
                    "audit_log_size": len(self.data_layer.audit_log)
                },
                "I": {
                    "nodes": len(self.info_layer),
                    "edges": len(self.info_layer._edges)
                },
                "K": {
                    "rules": len(self.knowledge_layer)
                },
                "W": {
                    "evaluations": len(self.wisdom_layer.evaluation_history)
                },
                "P": {
                    "locks": len(self.purpose_layer.purpose_locks)
                },
                "R": {
                    "entries": len(self.reliability_layer)
                }
            },
            "health": self.get_system_health(),
            "cq": self.compute_cq(),
            "export_time": time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def __repr__(self) -> str:
        return (
            f"DIKWPGovernanceLayer("
            f"v{self.version}, "
            f"D={len(self.data_layer)}, "
            f"I={len(self.info_layer)}, "
            f"K={len(self.knowledge_layer)}, "
            f"cq={self.compute_cq()['cq_score']:.1f})"
        )


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DIKWPGovernanceLayer六层统一入口测试")
    print("=" * 60)
    
    # 1. 创建治理层
    governance = DIKWPGovernanceLayer()
    print(f"\n✓ 创建治理层: {governance}")
    
    # 2. 设置会话
    print(f"\n✓ 设置会话:")
    governance.set_session(
        session_id="test_session",
        purpose="复合体AGI 6.0升级开发",
        scopes=["read", "write", "execute"]
    )
    print(f"  会话已设置: test_session")
    
    # 3. 受治理输出
    print(f"\n✓ 受治理输出测试:")
    
    outputs = [
        governance.governed_output(
            content="复合体AGI 6.0基于DIKWP六层语义治理框架实现升级",
            session_id="test_session",
            source="analysis",
            action_scope="read",
            node_type="_D"
        ),
        governance.governed_output(
            content="刘原理：S = S_data + λ·C(purpose) - μ·Risk 是决策核心准则",
            session_id="test_session",
            source="knowledge",
            action_scope="read",
            node_type="_Th"
        ),
        governance.governed_output(
            content="弹簧虫定理可应用于AGI协调总线的弹性管理",
            session_id="test_session",
            source="research",
            action_scope="read",
            node_type="_D"
        )
    ]
    
    for output in outputs:
        print(f"\n  [{output.dikwp['I']['node_type']}] {output.content[:30]}...")
        print(f"    D: {output.dikwp['D']['id']} (hash: {output.dikwp['D']['hash']})")
        print(f"    I: {output.dikwp['I']['id']}")
        print(f"    W: score={output.dikwp['W']['wisdom_score']:.2f}, decision={output.dikwp['W']['decision']}")
        print(f"    P: allowed={output.dikwp['P']['allowed']}, alignment={output.dikwp['P']['alignment']:.2f}")
        print(f"    R: r_score={output.dikwp['R']['r_score']:.2f}, bft={output.dikwp['R']['bft_validated']}")
        print(f"    治理通过: {output.governance_passed}")
    
    # 4. 受治理推理
    print(f"\n✓ 受治理推理测试:")
    inference = governance.governed_inference("弹簧虫协调机制")
    print(f"  输入: {inference['input']}")
    print(f"  输出: {inference['output'].content[:30]}...")
    print(f"  推理数: {len(inference['inferences'])}")
    if inference['inferences']:
        print(f"  最佳推理: {inference['inferences'][0]['conclusion'][:30]}...")
    
    # 5. 受治理行动
    print(f"\n✓ 受治理行动测试:")
    
    actions = [
        ("读取系统文档", "read"),
        ("执行代码生成", "execute"),
        ("删除关键文件", "delete"),  # 未授权
    ]
    
    for action, scope in actions:
        result = governance.governed_action(action, action_scope=scope)
        print(f"  [{scope}] {action}: {'允许 ✓' if result['allowed'] else '拒绝 ✗'}")
        if not result['allowed']:
            print(f"    原因: {result.get('reason', 'N/A')}")
        if result.get('wisdom_score'):
            print(f"    W分数: {result['wisdom_score']['total_score']:.2f}")
    
    # 6. 系统健康检查
    print(f"\n✓ 系统健康检查:")
    health = governance.get_system_health()
    print(f"  版本: {health['version']}")
    print(f"  各层状态:")
    for layer_id, layer_info in health['layers'].items():
        print(f"    {layer_info['name']}: {list(layer_info.values())[1]}")
    print(f"  协调总线: {health['extras']['coordination_bus']['status']}")
    
    # 7. CQ意识商数
    print(f"\n✓ CQ意识商数:")
    cq = governance.compute_cq()
    print(f"  CQ得分: {cq['cq_score']:.1f}")
    print(f"  评级: {cq['grade']}")
    print(f"  健康状态: {cq['health_status']}")
    print(f"  各组件:")
    for comp, value in cq['components'].items():
        if isinstance(value, float):
            print(f"    {comp}: {value:.3f}")
    
    # 8. 拒绝行动示例
    print(f"\n✓ 行动拒绝示例:")
    governance.set_session("no_purpose_session")  # 无目的的会话
    result = governance.governed_action("删除文件", action_scope="delete")
    print(f"  行动: 删除文件")
    print(f"  允许: {result['allowed']}")
    print(f"  原因: {result['reason']}")
    
    print("\n" + "=" * 60)
    print("DIKWPGovernanceLayer测试完成 ✓")
    print("=" * 60)
