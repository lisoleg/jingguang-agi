# -*- coding: utf-8 -*-
"""
M104: 协作诊断 (Collaboration Diagnostics)
配合T44/T47使用的协作问题诊断模块

功能：
- 诊断协作问题
- 检测人机目标不对齐
- 分析沟通模式
- 生成修复计划
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class DiagnosisResult:
    """诊断结果"""
    severity: str  # 'low' | 'medium' | 'high' | 'critical'
    category: str  # 'misalignment' | 'communication' | 'trust' | 'efficiency'
    description: str
    root_cause: str


@dataclass
class MisalignmentRecord:
    """不对齐记录"""
    type: str  # 'goal' | 'value' | 'priority' | 'expectation'
    degree: float  # [0, 1]
    affected_areas: List[str] = field(default_factory=list)


class CollaborationDiagnostics:
    """
    M104: 协作诊断模块

    配合T44/T47：
    - 诊断协作中的对齐问题
    - 检测人机目标偏差
    - 分析沟通模式效率
    - 生成修复计划
    """

    def __init__(self):
        self.diagnosis_count: int = 0
        self.misalignment_rate: float = 0.0
        self.avg_severity: float = 0.0
        self.repair_success_rate: float = 0.0

        self._diagnoses: List[DiagnosisResult] = []
        self._misalignments: List[MisalignmentRecord] = []
        self._repair_history: List[Dict] = []

    def diagnose_session(self, session_data: Dict) -> Dict[str, Any]:
        """
        诊断协作问题

        参数:
            session_data: {
                'interactions': int,
                'conflicts': int,
                'human_satisfaction': float,
                'ai_accuracy': float,
                'goal_achievement': float,
                'communication_quality': float
            }

        返回:
            dict: 诊断结果
        """
        self.diagnosis_count += 1

        interactions = session_data.get('interactions', 0)
        conflicts = session_data.get('conflicts', 0)
        satisfaction = session_data.get('human_satisfaction', 0.5)
        accuracy = session_data.get('ai_accuracy', 0.7)
        goal_achievement = session_data.get('goal_achievement', 0.5)
        comm_quality = session_data.get('communication_quality', 0.6)

        # 综合诊断
        diagnoses = []

        # 冲突率检查
        conflict_rate = conflicts / max(1, interactions)
        if conflict_rate > 0.3:
            diagnoses.append(DiagnosisResult(
                severity='high',
                category='communication',
                description=f'冲突率过高({conflict_rate:.0%})，人机沟通存在障碍',
                root_cause='交互模式不匹配或期望不一致'
            ))

        # 满意度检查
        if satisfaction < 0.4:
            diagnoses.append(DiagnosisResult(
                severity='high',
                category='trust',
                description=f'人类满意度低({satisfaction:.1f})，信任缺失',
                root_cause='AI行为不符合人类期望或透明度不足'
            ))

        # 目标达成检查
        if goal_achievement < 0.5:
            diagnoses.append(DiagnosisResult(
                severity='medium',
                category='misalignment',
                description=f'目标达成率低({goal_achievement:.1f})，可能存在目标不对齐',
                root_cause='目标定义不清晰或人机理解有偏差'
            ))

        # 沟通质量
        if comm_quality < 0.4:
            diagnoses.append(DiagnosisResult(
                severity='medium',
                category='communication',
                description=f'沟通质量差({comm_quality:.1f})，信息传递效率低',
                root_cause='信息表述方式不当或反馈机制不完善'
            ))

        # 效率检查
        if accuracy > 0.8 and satisfaction < 0.5:
            diagnoses.append(DiagnosisResult(
                severity='medium',
                category='efficiency',
                description='AI准确但人类不满意，可能是交互方式问题',
                root_cause='过度关注准确率而忽视用户体验'
            ))

        if not diagnoses:
            diagnoses.append(DiagnosisResult(
                severity='low',
                category='efficiency',
                description='协作状态健康，未发现明显问题',
                root_cause='无'
            ))

        self._diagnoses.extend(diagnoses)

        # 更新指标
        self.misalignment_rate = sum(1 for d in self._diagnoses if d.category == 'misalignment') / max(1, len(self._diagnoses))
        severity_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'critical': 1.0}
        self.avg_severity = sum(severity_map.get(d.severity, 0.5) for d in self._diagnoses) / max(1, len(self._diagnoses))

        return {
            'diagnosis_id': self.diagnosis_count,
            'issues_found': len([d for d in diagnoses if d.severity != 'low']),
            'diagnoses': [
                {
                    'severity': d.severity,
                    'category': d.category,
                    'description': d.description,
                    'root_cause': d.root_cause
                } for d in diagnoses
            ],
            'overall_health': round(1.0 - self.avg_severity, 4),
            'misalignment_rate': round(self.misalignment_rate, 4)
        }

    def detect_misalignment(self, interaction_log: List[Dict]) -> Dict[str, Any]:
        """
        检测人机目标不对齐

        参数:
            interaction_log: 交互日志 [{'human_intent': str, 'ai_action': str, 'alignment': float}]

        返回:
            dict: 不对齐检测结果
        """
        misalignments = []

        for entry in interaction_log:
            alignment = entry.get('alignment', 1.0)
            if alignment < 0.5:
                record = MisalignmentRecord(
                    type=self._classify_misalignment(entry),
                    degree=1.0 - alignment,
                    affected_areas=[entry.get('human_intent', '')[:30], entry.get('ai_action', '')[:30]]
                )
                misalignments.append(record)
                self._misalignments.append(record)

        # 更新不对齐率
        if interaction_log:
            self.misalignment_rate = len(misalignments) / len(interaction_log)

        return {
            'total_interactions': len(interaction_log),
            'misalignments_found': len(misalignments),
            'misalignment_rate': round(self.misalignment_rate, 4),
            'details': [
                {
                    'type': m.type,
                    'degree': round(m.degree, 4),
                    'affected_areas': m.affected_areas
                } for m in misalignments
            ]
        }

    def _classify_misalignment(self, entry: Dict) -> str:
        """分类不对齐类型"""
        human = entry.get('human_intent', '').lower()
        ai = entry.get('ai_action', '').lower()

        if '创意' in human and '模板' in ai:
            return 'value'
        elif '紧急' in human and '排队' in ai:
            return 'priority'
        elif '详细' in human and '简略' in ai:
            return 'expectation'
        return 'goal'

    def analyze_communication_pattern(self, messages: List[Dict]) -> Dict[str, Any]:
        """
        分析沟通模式

        参数:
            messages: 消息列表 [{'sender': str, 'type': str, 'length': int, 'response_time': float}]

        返回:
            dict: 沟通模式分析
        """
        if not messages:
            return {'pattern': 'no_data', 'quality': 0.0}

        human_msgs = [m for m in messages if m.get('sender') == 'human']
        ai_msgs = [m for m in messages if m.get('sender') == 'ai']

        # 对称性分析
        symmetry = 1.0 - abs(len(human_msgs) - len(ai_msgs)) / max(1, len(messages))

        # 响应时间分析
        response_times = [m.get('response_time', 1.0) for m in ai_msgs]
        avg_response = sum(response_times) / max(1, len(response_times))

        # 消息长度分析
        human_avg_len = sum(m.get('length', 0) for m in human_msgs) / max(1, len(human_msgs))
        ai_avg_len = sum(m.get('length', 0) for m in ai_msgs) / max(1, len(ai_msgs))

        quality = 0.4 * symmetry + 0.3 * (1 - min(1, avg_response / 5)) + 0.3 * min(1, (human_avg_len + ai_avg_len) / 200)

        return {
            'total_messages': len(messages),
            'human_messages': len(human_msgs),
            'ai_messages': len(ai_msgs),
            'symmetry': round(symmetry, 4),
            'avg_response_time': round(avg_response, 4),
            'human_avg_length': round(human_avg_len, 1),
            'ai_avg_length': round(ai_avg_len, 1),
            'quality': round(quality, 4),
            'pattern': 'balanced' if symmetry > 0.7 else 'asymmetric'
        }

    def generate_repair_plan(self, diagnosis: Dict) -> Dict[str, Any]:
        """
        生成修复计划

        参数:
            diagnosis: 诊断结果

        返回:
            dict: 修复计划
        """
        diagnoses = diagnosis.get('diagnoses', [])

        repair_steps = []
        for d in diagnoses:
            category = d.get('category', 'efficiency')
            severity = d.get('severity', 'low')

            steps = self._get_repair_steps(category, severity)
            repair_steps.extend(steps)

        # 去重
        seen = set()
        unique_steps = []
        for step in repair_steps:
            if step['step'] not in seen:
                seen.add(step['step'])
                unique_steps.append(step)

        return {
            'repair_plan': unique_steps,
            'estimated_duration': f'{len(unique_steps) * 2} 工作日',
            'priority_order': sorted(unique_steps, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['priority'], 3)),
            'total_steps': len(unique_steps)
        }

    def _get_repair_steps(self, category: str, severity: str) -> List[Dict]:
        """获取修复步骤"""
        repair_db = {
            'misalignment': [
                {'step': '重新对齐人机目标定义', 'priority': severity, 'category': 'misalignment'},
                {'step': '增加目标确认检查点', 'priority': severity, 'category': 'misalignment'},
            ],
            'communication': [
                {'step': '优化交互模式匹配', 'priority': severity, 'category': 'communication'},
                {'step': '增加双向反馈机制', 'priority': severity, 'category': 'communication'},
            ],
            'trust': [
                {'step': '增强透明度和可解释性', 'priority': severity, 'category': 'trust'},
                {'step': '主动披露不确定性', 'priority': severity, 'category': 'trust'},
            ],
            'efficiency': [
                {'step': '优化任务分配策略', 'priority': severity, 'category': 'efficiency'},
                {'step': '减少不必要的交互轮次', 'priority': severity, 'category': 'efficiency'},
            ]
        }
        return repair_db.get(category, [])

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态"""
        return {
            'diagnosis_count': self.diagnosis_count,
            'misalignment_rate': round(self.misalignment_rate, 4),
            'avg_severity': round(self.avg_severity, 4),
            'repair_success_rate': round(self.repair_success_rate, 4)
        }


# 单例模式
_instance = None

def get_instance():
    """获取模块单例"""
    global _instance
    if _instance is None:
        _instance = CollaborationDiagnostics()
    return _instance
