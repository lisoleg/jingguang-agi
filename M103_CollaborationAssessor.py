# -*- coding: utf-8 -*-
"""
M103: 协作评估 (Collaboration Assessor)
配合T46/T50使用的协作效能评估模块

功能：
- 评估人机协作效能
- 计算协同增效分数
- 识别协作瓶颈
- 建议改进方案
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class CollaborationSession:
    """协作会话"""
    session_id: str
    human_tasks: int
    ai_tasks: int
    shared_tasks: int
    duration: float  # 秒


@dataclass
class SynergyMetrics:
    """协同指标"""
    efficiency: float  # 效率 [0,1]
    satisfaction: float  # 满意度 [0,1]
    quality: float  # 质量 [0,1]
    synergy_score: float  # 协同增效 [0,1+]


class CollaborationAssessor:
    """
    M103: 协作评估模块

    配合T46/T50：
    - 评估E = E_human + E_AI + E_collab的总效能
    - 识别协同瓶颈
    - 量化协同增效（1+1>2的程度）
    """

    def __init__(self):
        self.total_sessions: int = 0
        self.avg_synergy: float = 0.5
        self.bottleneck_count: int = 0
        self.improvement_suggestions: int = 0

        self._session_history: List[CollaborationSession] = []
        self._synergy_history: List[float] = []

    def assess_collaboration(self, session_data: Dict) -> Dict[str, Any]:
        """
        评估人机协作效能

        参数:
            session_data: {
                'session_id': str,
                'human_tasks': int,
                'ai_tasks': int,
                'shared_tasks': int,
                'duration': float,
                'quality_score': float,
                'satisfaction_score': float
            }

        返回:
            dict: 评估结果
        """
        session = CollaborationSession(
            session_id=session_data.get('session_id', f's_{self.total_sessions}'),
            human_tasks=session_data.get('human_tasks', 0),
            ai_tasks=session_data.get('ai_tasks', 0),
            shared_tasks=session_data.get('shared_tasks', 0),
            duration=session_data.get('duration', 0.0)
        )

        self._session_history.append(session)
        self.total_sessions += 1

        # 计算协同指标
        metrics = self.compute_synergy_score(
            human_contrib=session.human_tasks + session.shared_tasks * 0.5,
            ai_contrib=session.ai_tasks + session.shared_tasks * 0.5
        )

        # 质量和满意度修正
        quality = session_data.get('quality_score', 0.7)
        satisfaction = session_data.get('satisfaction_score', 0.7)

        # 更新平均协同
        self._synergy_history.append(metrics.synergy_score)
        self.avg_synergy = sum(self._synergy_history) / len(self._synergy_history)

        return {
            'session_id': session.session_id,
            'synergy_metrics': {
                'efficiency': round(metrics.efficiency, 4),
                'satisfaction': round(satisfaction, 4),
                'quality': round(quality, 4),
                'synergy_score': round(metrics.synergy_score, 4)
            },
            'task_distribution': {
                'human_tasks': session.human_tasks,
                'ai_tasks': session.ai_tasks,
                'shared_tasks': session.shared_tasks
            },
            'assessment': self._generate_assessment(metrics.synergy_score),
            'avg_synergy': round(self.avg_synergy, 4)
        }

    def compute_synergy_score(self, human_contrib: float, ai_contrib: float) -> SynergyMetrics:
        """
        计算协同增效分数

        参数:
            human_contrib: 人类贡献度
            ai_contrib: AI贡献度

        返回:
            SynergyMetrics
        """
        total = human_contrib + ai_contrib
        if total <= 0:
            return SynergyMetrics(0, 0, 0, 0)

        # 效率 = 产出/时间（简化）
        efficiency = min(1.0, total / max(1, total * 0.8))

        # 满意度 = 贡献平衡度
        balance = 1.0 - abs(human_contrib - ai_contrib) / max(1, total)
        satisfaction = 0.5 + 0.5 * balance

        # 质量 = 协作深度
        min_contrib = min(human_contrib, ai_contrib)
        quality = min(1.0, min_contrib / max(1, total) * 2)

        # 协同增效 = 实际产出 > 独立产出之和
        # 1+1>2的度量
        individual_sum = human_contrib + ai_contrib
        collaboration_bonus = min_contrib * 0.3  # 协作加成
        synergy_score = (individual_sum + collaboration_bonus) / max(1, individual_sum)

        return SynergyMetrics(
            efficiency=efficiency,
            satisfaction=satisfaction,
            quality=quality,
            synergy_score=synergy_score
        )

    def identify_bottlenecks(self, workflow_data: Dict) -> Dict[str, Any]:
        """
        识别协作瓶颈

        参数:
            workflow_data: {
                'steps': [{'name': str, 'type': str, 'duration': float, 'waiting': bool}]
            }

        返回:
            dict: 瓶颈分析
        """
        steps = workflow_data.get('steps', [])
        bottlenecks = []

        for i, step in enumerate(steps):
            duration = step.get('duration', 0)
            is_waiting = step.get('waiting', False)

            # 长时间等待 = 瓶颈
            if is_waiting or duration > sum(s.get('duration', 0) for s in steps) / max(1, len(steps)) * 2:
                bottlenecks.append({
                    'step_index': i,
                    'step_name': step.get('name', f'step_{i}'),
                    'type': step.get('type', 'unknown'),
                    'duration': duration,
                    'is_waiting': is_waiting,
                    'severity': 'high' if is_waiting else 'medium'
                })
                self.bottleneck_count += 1

        return {
            'total_steps': len(steps),
            'bottlenecks_found': len(bottlenecks),
            'bottlenecks': bottlenecks,
            'recommendation': '增加AI预计算能力减少等待时间' if any(b['is_waiting'] for b in bottlenecks) else '工作流效率良好'
        }

    def suggest_improvement(self, assessment_result: Dict) -> Dict[str, Any]:
        """
        建议改进方案

        参数:
            assessment_result: 评估结果

        返回:
            dict: 改进建议
        """
        self.improvement_suggestions += 1

        metrics = assessment_result.get('synergy_metrics', {})
        synergy = metrics.get('synergy_score', 0.5)

        suggestions = []
        if synergy < 0.5:
            suggestions.append({
                'priority': 'high',
                'area': '协作模式',
                'suggestion': '重新评估任务分配，增加协作任务比例',
                'expected_improvement': '+20% 协同增效'
            })
        if metrics.get('efficiency', 0.5) < 0.5:
            suggestions.append({
                'priority': 'medium',
                'area': '效率',
                'suggestion': '优化并行任务调度，减少串行等待',
                'expected_improvement': '+15% 效率'
            })
        if metrics.get('satisfaction', 0.5) < 0.5:
            suggestions.append({
                'priority': 'medium',
                'area': '满意度',
                'suggestion': '改善人机交互界面，增加反馈机制',
                'expected_improvement': '+25% 满意度'
            })

        if not suggestions:
            suggestions.append({
                'priority': 'low',
                'area': '持续优化',
                'suggestion': '当前协作模式良好，持续微调即可',
                'expected_improvement': '+5% 整体效能'
            })

        return {
            'assessment_based_on': assessment_result.get('session_id', 'current'),
            'suggestions': suggestions,
            'total_suggestions_made': self.improvement_suggestions
        }

    def _generate_assessment(self, synergy_score: float) -> str:
        """生成评估文字"""
        if synergy_score >= 0.8:
            return '优秀：人机协同效应显著，1+1>2'
        elif synergy_score >= 0.6:
            return '良好：协作有效，但仍有优化空间'
        elif synergy_score >= 0.4:
            return '一般：协作模式需要调整'
        else:
            return '待改进：协同效果不足，建议重新设计协作流程'

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态"""
        return {
            'total_sessions': self.total_sessions,
            'avg_synergy': round(self.avg_synergy, 4),
            'bottleneck_count': self.bottleneck_count,
            'improvement_suggestions': self.improvement_suggestions
        }


# 单例模式
_instance = None

def get_instance():
    """获取模块单例"""
    global _instance
    if _instance is None:
        _instance = CollaborationAssessor()
    return _instance
