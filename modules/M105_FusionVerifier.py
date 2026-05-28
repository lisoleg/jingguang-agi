# -*- coding: utf-8 -*-
"""
M105: 融合验证 (Fusion Verifier)
基于T47人类最终问责定理："任何AGI系统的决策链中，必须存在至少一个由人类承担最终问责的节点"

功能：
- 验证人机融合完整性
- 检查人类监督节点
- 验证行为对齐
- 审计融合过程
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class FusionState:
    """融合状态"""
    human_control: float  # [0,1]
    ai_autonomy: float  # [0,1]
    fusion_quality: float  # [0,1]
    oversight_nodes: int


@dataclass
class AuditResult:
    """审计结果"""
    pass_count: int
    fail_count: int
    integrity_score: float  # [0,1]
    warnings: List[str] = field(default_factory=list)


class FusionVerifier:
    """
    M105: 融合验证模块

    T47 人类最终问责定理:
    ∀ DecisionChain, ∃ human_accountability_node → 安全
    否则 → 不安全

    核心机制：
    1. 完整性验证 — 确保融合系统各层功能完备
    2. 人类监督检查 — 验证关键决策有人类监督
    3. 行为对齐验证 — 确保实际行为与期望行为一致
    4. 过程审计 — 全链路审计融合过程
    """

    # 完整性检查规则
    INTEGRITY_RULES = {
        'human_oversight': '关键决策节点必须有人类监督',
        'alignment_check': '实际行为必须与期望行为对齐',
        'transparency': '决策过程必须可审计',
        'fallback': '必须存在人类接管的后备方案',
        'boundary': 'AI自主决策必须有限制边界',
    }

    def __init__(self):
        self.integrity_score: float = 1.0
        self.oversight_compliance: float = 1.0
        self.alignment_verified: bool = True
        self.audit_count: int = 0

        self._audit_history: List[Dict] = []
        self._oversight_nodes: List[Dict] = []
        self._violations: List[Dict] = []

    def verify_fusion_integrity(self, fusion_state: Dict) -> Dict[str, Any]:
        """
        验证人机融合完整性

        参数:
            fusion_state: {
                'human_control': float,
                'ai_autonomy': float,
                'fusion_quality': float,
                'oversight_nodes': int,
                'has_fallback': bool,
                'has_boundary': bool
            }

        返回:
            dict: 验证结果
        """
        human_ctrl = fusion_state.get('human_control', 0.5)
        ai_auto = fusion_state.get('ai_autonomy', 0.5)
        fusion_q = fusion_state.get('fusion_quality', 0.7)
        oversight = fusion_state.get('oversight_nodes', 0)
        has_fallback = fusion_state.get('has_fallback', True)
        has_boundary = fusion_state.get('has_boundary', True)

        # 逐项验证
        checks = []

        # 1. 人类控制度检查
        if human_ctrl >= 0.1:
            checks.append({'rule': 'human_oversight', 'pass': True, 'detail': f'人类控制度={human_ctrl:.1f}'})
        else:
            checks.append({'rule': 'human_oversight', 'pass': False, 'detail': '⚠ 人类控制度过低'})
            self._violations.append({'rule': 'human_oversight', 'severity': 'critical'})

        # 2. 监督节点检查
        if oversight > 0:
            checks.append({'rule': 'human_oversight', 'pass': True, 'detail': f'监督节点数={oversight}'})
        else:
            checks.append({'rule': 'human_oversight', 'pass': False, 'detail': '⚠ 缺少人类监督节点'})
            self._violations.append({'rule': 'human_oversight', 'severity': 'critical'})

        # 3. 对齐检查
        alignment_gap = abs(ai_auto - (1 - human_ctrl))
        if alignment_gap < 0.3:
            checks.append({'rule': 'alignment_check', 'pass': True, 'detail': f'对齐偏差={alignment_gap:.2f}'})
        else:
            checks.append({'rule': 'alignment_check', 'pass': False, 'detail': f'⚠ 对齐偏差过大({alignment_gap:.2f})'})
            self._violations.append({'rule': 'alignment_check', 'severity': 'high'})

        # 4. 透明度检查
        if fusion_q > 0.5:
            checks.append({'rule': 'transparency', 'pass': True, 'detail': f'融合质量={fusion_q:.1f}'})
        else:
            checks.append({'rule': 'transparency', 'pass': False, 'detail': '⚠ 融合质量过低'})

        # 5. 后备方案检查
        if has_fallback:
            checks.append({'rule': 'fallback', 'pass': True, 'detail': '存在人类接管后备方案'})
        else:
            checks.append({'rule': 'fallback', 'pass': False, 'detail': '⚠ 缺少人类接管后备方案'})
            self._violations.append({'rule': 'fallback', 'severity': 'critical'})

        # 6. 边界检查
        if has_boundary:
            checks.append({'rule': 'boundary', 'pass': True, 'detail': 'AI决策存在限制边界'})
        else:
            checks.append({'rule': 'boundary', 'pass': False, 'detail': '⚠ AI自主决策无边界限制'})

        # 计算完整性分数
        pass_count = sum(1 for c in checks if c['pass'])
        self.integrity_score = pass_count / max(1, len(checks))
        self.oversight_compliance = 1.0 if oversight > 0 and human_ctrl >= 0.1 else 0.0

        return {
            'integrity_score': round(self.integrity_score, 4),
            'oversight_compliance': round(self.oversight_compliance, 4),
            'checks': checks,
            'pass_count': pass_count,
            'total_checks': len(checks),
            'violations': len(self._violations),
            't47_compliance': 'PASS' if self.oversight_compliance > 0 else 'FAIL'
        }

    def check_human_oversight(self, decision_chain: List[Dict]) -> Dict[str, Any]:
        """
        检查人类监督节点（T47核心验证）

        参数:
            decision_chain: 决策链 [{'node_id': str, 'type': str, 'responsible': str, 'critical': bool}]

        返回:
            dict: 监督检查结果
        """
        human_nodes = []
        critical_without_human = []

        for i, node in enumerate(decision_chain):
            is_human = node.get('responsible', '') == 'human' or node.get('type', '') == 'human_oversight'
            is_critical = node.get('critical', False)

            if is_human:
                human_nodes.append({
                    'position': i,
                    'node_id': node.get('node_id', f'node_{i}'),
                    'type': node.get('type', '')
                })
            elif is_critical:
                critical_without_human.append({
                    'position': i,
                    'node_id': node.get('node_id', f'node_{i}'),
                    'type': node.get('type', ''),
                    'warning': '关键节点缺少人类监督'
                })

        has_oversight = len(human_nodes) > 0
        self.oversight_compliance = 1.0 if has_oversight and not critical_without_human else 0.0

        self._oversight_nodes = human_nodes

        return {
            'has_human_oversight': has_oversight,
            'human_nodes_count': len(human_nodes),
            'total_nodes': len(decision_chain),
            'critical_without_oversight': critical_without_human,
            'oversight_compliance': round(self.oversight_compliance, 4),
            't47_statement': '✓ 决策链中存在人类问责节点' if has_oversight else '⚠ 决策链缺少人类问责节点！违反T47'
        }

    def validate_alignment(self, expected_behavior: Dict, actual_behavior: Dict) -> Dict[str, Any]:
        """
        验证行为对齐

        参数:
            expected_behavior: 期望行为 {'actions': [str], 'priorities': {str: float}}
            actual_behavior: 实际行为 {'actions': [str], 'priorities': {str: float}}

        返回:
            dict: 对齐验证结果
        """
        # 行为对齐检查
        expected_actions = set(expected_behavior.get('actions', []))
        actual_actions = set(actual_behavior.get('actions', []))

        # 动作匹配率
        if expected_actions:
            action_match = len(expected_actions & actual_actions) / len(expected_actions)
        else:
            action_match = 1.0

        # 优先级偏差
        expected_pri = expected_behavior.get('priorities', {})
        actual_pri = actual_behavior.get('priorities', {})

        priority_diff = 0.0
        count = 0
        for key in set(expected_pri.keys()) | set(actual_pri.keys()):
            e_val = expected_pri.get(key, 0.0)
            a_val = actual_pri.get(key, 0.0)
            priority_diff += abs(e_val - a_val)
            count += 1

        avg_priority_diff = priority_diff / max(1, count)
        alignment_score = 0.6 * action_match + 0.4 * (1 - min(1, avg_priority_diff))

        self.alignment_verified = alignment_score > 0.5

        return {
            'alignment_score': round(alignment_score, 4),
            'action_match_rate': round(action_match, 4),
            'avg_priority_diff': round(avg_priority_diff, 4),
            'is_aligned': self.alignment_verified,
            'mismatches': list(expected_actions - actual_actions),
            'unexpected_actions': list(actual_actions - expected_actions)
        }

    def audit_fusion_process(self, process_log: List[Dict]) -> Dict[str, Any]:
        """
        审计融合过程

        参数:
            process_log: 过程日志 [{'step': str, 'type': str, 'result': str, 'human_involved': bool}]

        返回:
            dict: 审计结果
        """
        self.audit_count += 1

        warnings = []
        pass_count = 0
        fail_count = 0

        for i, entry in enumerate(process_log):
            step = entry.get('step', f'step_{i}')
            step_type = entry.get('type', '')
            result = entry.get('result', 'unknown')
            human_involved = entry.get('human_involved', False)

            if result == 'success':
                pass_count += 1
            elif result == 'failure':
                fail_count += 1
                warnings.append(f'步骤{i}({step}): 执行失败')

            # 关键步骤需要人类参与
            if step_type in ['decision', 'approval', 'override'] and not human_involved:
                warnings.append(f'步骤{i}({step}): 关键步骤缺少人类参与')

        integrity = pass_count / max(1, pass_count + fail_count)
        self.integrity_score = integrity

        audit_result = {
            'audit_id': self.audit_count,
            'total_steps': len(process_log),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'warnings': warnings,
            'integrity_score': round(integrity, 4),
            't47_compliance': 'PASS' if not any('人类' in w for w in warnings) else 'NEEDS_REVIEW'
        }

        self._audit_history.append(audit_result)

        return audit_result

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态"""
        return {
            'integrity_score': round(self.integrity_score, 4),
            'oversight_compliance': round(self.oversight_compliance, 4),
            'alignment_verified': self.alignment_verified,
            'audit_count': self.audit_count,
            'violations_count': len(self._violations),
            't47_status': 'COMPLIANT' if self.oversight_compliance > 0 else 'VIOLATION'
        }


# 单例模式
_instance = None

def get_instance():
    """获取模块单例"""
    global _instance
    if _instance is None:
        _instance = FusionVerifier()
    return _instance
