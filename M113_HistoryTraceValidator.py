# -*- coding: utf-8 -*-
"""M113: 历史痕迹验证器 (History Trace Validator)
基于Γ算子验证痕迹的物理来源
核心定理：T63 数码未完结性失真定理
     数码痕迹若缺失未完结性，则为伪迹（算法生成的虚假历史投影）
关联：Γ算子流贯截断, 历史投影精度评估
四规则验证：物理源、不可逆性、未完结性、维度完整性
"""

import time
from typing import Dict, Any, List, Optional


class HistoryTraceValidator:
    """M113: 历史痕迹验证器
    - 基于Γ算子验证痕迹的物理来源
    - 检测数码未完结性失真（伪迹）
    - 评估历史投影精度
    - 四规则验证：物理源、不可逆性、未完结性、维度完整性
    """

    def __init__(self, cutoff_op: Optional[Any] = None):
        """初始化历史痕迹验证器

        Args:
            cutoff_op: FlowCutoffOperator 引用（可选，用于Γ算子流贯截断）
        """
        # 外部依赖
        self.cutoff_op: Optional[Any] = cutoff_op

        # 四条验证规则
        self.validation_rules: List[str] = [
            'physical_source',       # 物理流贯源检查
            'irreversibility',       # 不可逆性检查
            'unfinishedness',        # 未完结性检查
            'dimension_integrity'    # 维度完整性检查
        ]

        # 验证历史记录
        self.validation_history: List[Dict[str, Any]] = []

        # 统计计数
        self.authentic_count: int = 0    # 验证通过数
        self.pseudo_count: int = 0       # 伪迹数

        # 帧计数与时间戳
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def _check_physical_source(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """规则1: 检查是否有物理流贯源

        痕迹必须源自物理F_tel流贯，而非纯算法生成。

        Args:
            trace: 待验证的痕迹数据

        Returns:
            包含 passed 和 reason 字段的验证结果
        """
        has_source = bool(trace.get('physical_ftel_source'))
        return {
            'rule': 'physical_source',
            'passed': has_source,
            'reason': '痕迹存在物理流贯源' if has_source else '痕迹缺失物理流贯源（可能为算法生成）'
        }

    def _check_irreversibility(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """规则2: 检查不可逆性是否被破坏

        真实痕迹具有时间不可逆性；若被算法篡改则不可逆性被破坏。

        Args:
            trace: 待验证的痕迹数据

        Returns:
            包含 passed 和 reason 字段的验证结果
        """
        is_irreversible = trace.get('irreversible', False)
        is_tampered = trace.get('algorithm_tampered', False)
        passed = is_irreversible and not is_tampered
        reason_parts = []
        if not is_irreversible:
            reason_parts.append('不可逆性缺失')
        if is_tampered:
            reason_parts.append('痕迹被算法篡改')
        return {
            'rule': 'irreversibility',
            'passed': passed,
            'reason': '不可逆性完整' if passed else '；'.join(reason_parts)
        }

    def _check_unfinishedness(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """规则3: 检查未完结性是否保留

        T63 数码未完结性失真定理：数码痕迹若缺失未完结性，则为伪迹。
        真实物理痕迹永远处于未完结状态。

        Args:
            trace: 待验证的痕迹数据

        Returns:
            包含 passed 和 reason 字段的验证结果
        """
        is_unfinished = trace.get('unfinished', False)
        return {
            'rule': 'unfinishedness',
            'passed': is_unfinished,
            'reason': '未完结性保留（T63通过）' if is_unfinished else '未完结性缺失 — 数码失真伪迹（T63不通过）'
        }

    def _check_dimension_integrity(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """规则4: 检查维度完整性

        真实痕迹至少应包含2个维度（时间+至少一个空间维度）。

        Args:
            trace: 待验证的痕迹数据

        Returns:
            包含 passed 和 reason 字段的验证结果
        """
        dimensions = trace.get('dimensions', 0)
        passed = dimensions >= 2
        return {
            'rule': 'dimension_integrity',
            'passed': passed,
            'reason': f'维度完整（{dimensions}维）' if passed else f'维度不完整（仅{dimensions}维，需≥2）'
        }

    def validate(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """验证痕迹的真实性

        对trace执行4条规则验证，计算真实性评分。

        判定标准：
        - authenticity_score >= 0.75 → is_authentic = True
        - authenticity_score < 0.5 → is_pseudo = True

        Args:
            trace: 待验证的痕迹数据，需包含：
                - trace_id: 痕迹标识
                - physical_ftel_source: 物理流贯源标记
                - irreversible: 不可逆性标记
                - algorithm_tampered: 算法篡改标记
                - unfinished: 未完结性标记
                - dimensions: 维度数

        Returns:
            验证结果字典，包含 trace_id, authenticity_score, is_authentic, is_pseudo, details, theorem_basis
        """
        trace_id = trace.get('trace_id', 'unknown')

        # 执行四条规则验证
        details: List[Dict[str, Any]] = [
            self._check_physical_source(trace),
            self._check_irreversibility(trace),
            self._check_unfinishedness(trace),
            self._check_dimension_integrity(trace)
        ]

        # 计算真实性评分 = 通过数 / 总数
        passed_count = sum(1 for d in details if d['passed'])
        total_count = len(details)
        authenticity_score = round(passed_count / total_count, 4)

        # 判定真实性
        is_authentic = authenticity_score >= 0.75
        is_pseudo = authenticity_score < 0.5

        # 更新统计计数
        if is_authentic:
            self.authentic_count += 1
        elif is_pseudo:
            self.pseudo_count += 1

        # 构建验证结果
        result: Dict[str, Any] = {
            'trace_id': trace_id,
            'authenticity_score': authenticity_score,
            'passed_rules': passed_count,
            'total_rules': total_count,
            'is_authentic': is_authentic,
            'is_pseudo': is_pseudo,
            'details': details,
            'theorem_basis': 'T63: 数码未完结性失真定理 — 数码痕迹若缺失未完结性，则为伪迹'
        }

        # 记录验证历史
        self.validation_history.append(result)
        self.validation_history = self.validation_history[-100:]  # 保留最近100条

        return result

    def audit_all(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """审计所有痕迹

        批量验证痕迹，统计通过率。

        Args:
            traces: 待审计的痕迹列表

        Returns:
            审计结果字典，包含 total, authentic, pseudo, uncertain, pass_rate, pseudo_ids
        """
        if not traces:
            return {
                'total': 0,
                'authentic': 0,
                'pseudo': 0,
                'uncertain': 0,
                'pass_rate': 0.0,
                'pseudo_ids': []
            }

        authentic = 0
        pseudo = 0
        uncertain = 0
        pseudo_ids: List[str] = []

        for trace in traces:
            result = self.validate(trace)
            if result['is_authentic']:
                authentic += 1
            elif result['is_pseudo']:
                pseudo += 1
                pseudo_ids.append(result['trace_id'])
            else:
                uncertain += 1

        total = len(traces)
        pass_rate = round(authentic / total, 4)

        return {
            'total': total,
            'authentic': authentic,
            'pseudo': pseudo,
            'uncertain': uncertain,
            'pass_rate': pass_rate,
            'pseudo_ids': pseudo_ids
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """更新验证器状态

        Args:
            data: 可选更新数据，支持：
                - trace: 单条痕迹验证
                - traces: 批量审计

        Returns:
            验证器当前状态
        """
        if data:
            if 'trace' in data:
                self.validate(data['trace'])
            if 'traces' in data:
                self.audit_all(data['traces'])

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """获取验证器状态

        Returns:
            验证器状态字典
        """
        total_validations = self.authentic_count + self.pseudo_count
        # 注意：uncertain的痕迹不计入authentic或pseudo，需从history中推算
        history_total = len(self.validation_history)
        if history_total > 0:
            uncertain_count = history_total - self.authentic_count - self.pseudo_count
            total_validations = history_total
        else:
            uncertain_count = 0

        pass_rate = round(self.authentic_count / max(1, total_validations), 4)

        return {
            'total_validations': total_validations,
            'authentic_count': self.authentic_count,
            'pseudo_count': self.pseudo_count,
            'uncertain_count': uncertain_count,
            'pass_rate': pass_rate,
            'validation_rules': self.validation_rules,
            'has_cutoff_op': self.cutoff_op is not None,
            'frame_count': self.frame_count,
            'status': 'active',
            'last_update': self.last_update
        }

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 用样例数据演示验证流程"""
        # 模拟4条痕迹
        sample_traces: List[Dict[str, Any]] = [
            {
                'trace_id': 'T-物理真迹',
                'physical_ftel_source': True,
                'irreversible': True,
                'algorithm_tampered': False,
                'unfinished': True,
                'dimensions': 3
            },
            {
                'trace_id': 'T-纯算法伪迹',
                'physical_ftel_source': False,
                'irreversible': False,
                'algorithm_tampered': True,
                'unfinished': False,
                'dimensions': 1
            },
            {
                'trace_id': 'T-部分失真',
                'physical_ftel_source': True,
                'irreversible': False,
                'algorithm_tampered': False,
                'unfinished': False,
                'dimensions': 2
            },
            {
                'trace_id': 'T-弱伪迹',
                'physical_ftel_source': False,
                'irreversible': True,
                'algorithm_tampered': False,
                'unfinished': True,
                'dimensions': 3
            }
        ]

        audit_result = self.audit_all(sample_traces)
        return self.update({'traces': sample_traces})


# 全局单例
_instance: Optional[HistoryTraceValidator] = None


def get_instance(cutoff_op: Optional[Any] = None) -> HistoryTraceValidator:
    """获取全局单例

    Args:
        cutoff_op: FlowCutoffOperator 引用（首次创建时传入）

    Returns:
        HistoryTraceValidator 单例实例
    """
    global _instance
    if _instance is None:
        _instance = HistoryTraceValidator(cutoff_op)
    return _instance


def validate(trace: Dict[str, Any]) -> Dict[str, Any]:
    """验证单条痕迹（快捷接口）"""
    return get_instance().validate(trace)


def audit_all(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量审计痕迹（快捷接口）"""
    return get_instance().audit_all(traces)


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新验证器状态（快捷接口）"""
    return get_instance().update(data)


def get_state() -> Dict[str, Any]:
    """获取验证器状态（快捷接口）"""
    return get_instance().get_state()


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
