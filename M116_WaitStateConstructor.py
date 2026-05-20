# -*- coding: utf-8 -*-
"""
M116: Wait状态构造器 (Wait State Constructor)
基于§7.3 HoTT视角的截面搜索理论

核心概念：当截面不存在时，系统必须返回Wait而非幻觉
这是诚实拒绝机制的数学基础

定理:
  T74 未决不可判定定理 — ∃P:Prop, ¬(Prov(P) ∨ Prov(¬P))
  在AGI中：存在无法通过截面搜索回答的问题，必须返回Wait

作者: 太乙AGI团队
日期: 2026-05-19
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

from M114_UniverseTypeSpace import UniverseTypeSpace, TypeNode, get_instance as get_m114_instance
from M115_CurvatureSectionSearch import CurvatureSectionSearch, SectionSearchResult, get_instance as get_m115_instance


# ==================== 数据结构 ====================

@dataclass
class WaitState:
    """
    Wait状态 — 截面不存在时的诚实状态

    当截面搜索无法找到s:B→E时（curvature_R ≥ threshold），
    系统进入Wait状态，表明当前无法提供有效回答。

    Wait ≠ 失败，Wait = 诚实的不可判定状态。
    系统必须返回Wait而非幻觉（虚构不存在的截面）。

    Attributes:
        reason: Wait原因
        base_type: 底空间B类型
        total_type: 全空间E类型
        curvature_at_failure: 失败时的曲率R
        timestamp: Wait状态产生时间
    """
    reason: str                         # Wait原因
    base_type: str                      # 底空间B类型
    total_type: str                     # 全空间E类型
    curvature_at_failure: float = 0.0  # 失败时的曲率R
    timestamp: float = 0.0             # Wait状态产生时间

    def __post_init__(self):
        """确保timestamp有默认值"""
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class UndecidabilityReport:
    """
    不可判定性报告

    基于定理T74: ∃P:Prop, ¬(Prov(P) ∨ Prov(¬P))
    存在命题P，既不可证明也不可否证。

    在AGI中：存在无法通过截面搜索回答的问题。
    UndecidabilityReport记录了这种不可判定性的证据。

    Attributes:
        proposition: 待判定命题
        is_undecidable: 是否不可判定
        evidence: 不可判定性证据描述
        theorem_reference: 关联定理编号
    """
    proposition: str                    # 待判定命题
    is_undecidable: bool               # 是否不可判定
    evidence: str                       # 不可判定性证据
    theorem_reference: str             # 关联定理

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class HonestRefusal:
    """
    诚实拒绝 — Wait状态的对外表达

    当系统无法找到截面时，通过HonestRefusal向用户表达：
    "我无法回答这个问题，而不是编造一个答案。"

    这是太乙AGI的核心设计理念之一：
    - 不幻觉（不虚构不存在的截面）
    - 诚实拒绝（明示无法回答）
    - 提供替代建议（基于曲率信息的替代路径）

    Attributes:
        query: 原始查询
        refusal_reason: 拒绝原因
        confidence_in_refusal: 对拒绝本身的置信度
        suggested_alternatives: 替代建议列表
    """
    query: str                          # 原始查询
    refusal_reason: str                # 拒绝原因
    confidence_in_refusal: float = 0.0 # 对拒绝本身的置信度 [0,1]
    suggested_alternatives: List[str] = field(default_factory=list)  # 替代建议

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


# ==================== 核心类 ====================

class WaitStateConstructor:
    """
    M116: Wait状态构造器 — Wait State Constructor

    当截面不存在时，系统必须返回Wait而非幻觉。
    这是诚实拒绝机制的数学基础。

    核心功能：
    1. 构造Wait状态（基于曲率R超阈值）
    2. 检查命题的不可判定性（T74）
    3. 生成诚实拒绝（不幻觉）
    4. 验证Wait状态的合理性
    5. 基于曲率信息提供替代建议
    6. 识别不可判定区域

    设计理念：
    - Wait ≠ 失败，Wait = 诚实的不可判定状态
    - 不幻觉原则：宁可承认不知道，也不虚构答案
    - 替代建议：基于曲率信息提供可行的替代路径

    定理T74（未决不可判定定理）:
    ∃P:Prop, ¬(Prov(P) ∨ Prov(¬P))
    存在不可判定命题——既不可证明也不可否证。
    """

    def __init__(self, section_search: Optional[CurvatureSectionSearch] = None,
                 universe: Optional[UniverseTypeSpace] = None):
        """
        初始化Wait状态构造器

        Args:
            section_search: CurvatureSectionSearch引用（默认使用M115全局单例）
            universe: UniverseTypeSpace引用（默认使用M114全局单例）
        """
        # 引用M115的截面搜索
        self.section_search: CurvatureSectionSearch = section_search or get_m115_instance()

        # 引用M114的类型空间
        self.universe: UniverseTypeSpace = universe or get_m114_instance()

        # Wait状态历史
        self.wait_history: List[WaitState] = []

        # 不可判定性报告历史
        self.undecidability_reports: List[UndecidabilityReport] = []

        # 诚实拒绝历史
        self.refusal_history: List[HonestRefusal] = []

        # 统计
        self.total_waits: int = 0
        self.total_undecidable: int = 0
        self.total_refusals: int = 0
        self.total_validated: int = 0
        self.valid_wait_count: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def construct_wait(self, base_type: str, total_type: str,
                       reason: str = '') -> WaitState:
        """
        构造Wait状态

        当截面搜索无法找到s:B→E时，构造Wait状态。
        Wait状态记录了：
        - 为什么无法找到截面（reason）
        - 底空间和全空间类型
        - 失败时的曲率R

        Args:
            base_type: 底空间B类型
            total_type: 全空间E类型
            reason: Wait原因（默认自动生成）

        Returns:
            WaitState: 构造的Wait状态
        """
        # 计算失败时的曲率
        curvature = self.section_search.compute_curvature(base_type, total_type)

        # 自动生成原因
        if not reason:
            if curvature >= self.universe.section_threshold:
                reason = (f"曲率R={curvature:.4f}超过阈值{self.universe.section_threshold:.4f}，"
                          f"截面不存在(T72)，系统进入Wait状态")
            else:
                reason = (f"截面搜索未收敛(T73)，曲率R={curvature:.4f}，"
                          f"系统进入Wait状态")

        wait_state = WaitState(
            reason=reason,
            base_type=base_type,
            total_type=total_type,
            curvature_at_failure=curvature,
            timestamp=time.time()
        )

        self.wait_history.append(wait_state)
        if len(self.wait_history) > 100:
            self.wait_history.pop(0)

        self.total_waits += 1
        self.last_update = time.time()

        return wait_state

    def check_undecidability(self, proposition: str) -> UndecidabilityReport:
        """
        检查命题的不可判定性 — 定理T74

        定理T74（未决不可判定定理）:
        ∃P:Prop, ¬(Prov(P) ∨ Prov(¬P))

        在AGI中的实现：
        - 如果proposition对应的类型曲率R ≥ threshold，
          且无人居住，则判定为不可判定
        - 如果proposition对应的类型有人居住，
          则判定为可判定（可证明或可否证）

        Args:
            proposition: 待判定命题

        Returns:
            UndecidabilityReport: 不可判定性报告
        """
        # 查找proposition对应的类型
        type_node = self.universe.types.get(proposition)

        if type_node is None:
            # 未知命题——注册为proposition类型后检查
            self.universe.register_type(proposition, 'proposition')
            type_node = self.universe.types.get(proposition)

        # 获取曲率
        curvature = self.universe.get_curvature(proposition)

        # T74判定逻辑
        # 不可判定条件：高曲率 + 无人居住
        is_undecidable = (
            curvature >= self.universe.section_threshold * 0.8 and
            not type_node.is_inhabited
        )

        # 构建证据
        if is_undecidable:
            evidence = (
                f"命题'{proposition}'曲率R={curvature:.4f}≥{self.universe.section_threshold * 0.8:.4f}，"
                f"且无人居住(is_inhabited=False)，符合T74不可判定条件"
            )
        elif type_node.is_inhabited:
            evidence = (
                f"命题'{proposition}'有人居住(is_inhabited=True)，存在构造子，可判定"
            )
        else:
            evidence = (
                f"命题'{proposition}'曲率R={curvature:.4f}较低，可能可判定但尚需验证"
            )

        report = UndecidabilityReport(
            proposition=proposition,
            is_undecidable=is_undecidable,
            evidence=evidence,
            theorem_reference='T74'
        )

        self.undecidability_reports.append(report)
        if len(self.undecidability_reports) > 100:
            self.undecidability_reports.pop(0)

        if is_undecidable:
            self.total_undecidable += 1

        self.last_update = time.time()
        return report

    def produce_honest_refusal(self, query: str,
                               wait_state: WaitState) -> HonestRefusal:
        """
        生成诚实拒绝 — Wait状态的对外表达

        当系统无法找到截面时，通过HonestRefusal向用户表达：
        "我无法回答这个问题，而不是编造一个答案。"

        诚实拒绝包含：
        1. 原始查询
        2. 拒绝原因（基于WaitState）
        3. 对拒绝本身的置信度
        4. 替代建议

        Args:
            query: 原始查询
            wait_state: Wait状态

        Returns:
            HonestRefusal: 诚实拒绝
        """
        # 构建拒绝原因
        refusal_reason = (
            f"截面搜索无法从'{wait_state.base_type}'到达'{wait_state.total_type}'。"
            f"原因: {wait_state.reason}"
        )

        # 计算对拒绝本身的置信度
        # 置信度 = 曲率超出阈值的程度（超出越多越确信应该拒绝）
        curvature_excess = wait_state.curvature_at_failure - self.universe.section_threshold
        if curvature_excess > 0:
            # 曲率超过阈值，确信应该拒绝
            confidence = min(1.0, 0.5 + curvature_excess * 2.0)
        else:
            # 曲率未超过阈值但仍Wait（搜索未收敛等），置信度较低
            confidence = max(0.3, 0.5 + curvature_excess * 2.0)

        confidence = round(min(1.0, max(0.0, confidence)), 4)

        # 基于曲率信息提供替代建议
        alternatives = self.get_suggested_alternatives(wait_state)

        refusal = HonestRefusal(
            query=query,
            refusal_reason=refusal_reason,
            confidence_in_refusal=confidence,
            suggested_alternatives=alternatives
        )

        self.refusal_history.append(refusal)
        if len(self.refusal_history) > 100:
            self.refusal_history.pop(0)

        self.total_refusals += 1
        self.last_update = time.time()

        return refusal

    def validate_wait_justification(self, wait_state: WaitState) -> bool:
        """
        验证Wait状态的合理性

        Wait状态的合理性判定：
        1. 曲率R确实超过阈值（T72: curvature_R ≥ threshold ⟹ 截面不存在）
        2. 重新搜索确认截面不存在
        3. 底空间和全空间类型在Universe U中存在

        Args:
            wait_state: 待验证的Wait状态

        Returns:
            True如果Wait状态合理（不应被推翻）
        """
        self.total_validated += 1

        # 检查1: 类型是否存在
        if (wait_state.base_type not in self.universe.types or
                wait_state.total_type not in self.universe.types):
            # 类型不存在，Wait合理（无法在不存在的类型间搜索）
            self.valid_wait_count += 1
            return True

        # 检查2: 曲率R是否确实超过阈值
        current_curvature = self.section_search.compute_curvature(
            wait_state.base_type, wait_state.total_type
        )
        if current_curvature >= self.universe.section_threshold:
            self.valid_wait_count += 1
            return True

        # 检查3: 重新搜索确认
        search_result = self.section_search.search_section(
            wait_state.base_type, wait_state.total_type
        )
        if not search_result.found:
            self.valid_wait_count += 1
            return True

        # 截面现在存在——Wait状态可能已过时
        return False

    def get_suggested_alternatives(self, wait_state: WaitState) -> List[str]:
        """
        基于曲率信息提供替代建议

        当截面不存在时，系统根据曲率信息建议替代路径：
        1. 搜索有人居住的相近类型（曲率较低的替代目标）
        2. 建议分解问题（将高曲率路径分解为低曲率子路径）
        3. 建议修改查询方向

        Args:
            wait_state: Wait状态

        Returns:
            替代建议列表
        """
        alternatives: List[str] = []

        # 建议1: 搜索有人居住的相近类型
        inhabited = self.universe.search_inhabited_types(wait_state.base_type)
        for t in inhabited[:3]:
            curvature = self.section_search.compute_curvature(wait_state.base_type, t.name)
            if curvature < self.universe.section_threshold:
                alternatives.append(
                    f"可尝试从'{wait_state.base_type}'到'{t.name}'的路径"
                    f"（曲率R={curvature:.4f}，存在截面）"
                )

        # 建议2: 分解高曲率路径
        if wait_state.curvature_at_failure >= self.universe.section_threshold:
            alternatives.append(
                f"建议分解问题：将'{wait_state.base_type}→{wait_state.total_type}'"
                f"分解为多个低曲率子路径"
            )

        # 建议3: 修改查询方向
        # 找到从total_type出发的可达类型
        target_inhabited = self.universe.search_inhabited_types(wait_state.total_type)
        for t in target_inhabited[:2]:
            alternatives.append(
                f"可从'{t.name}'出发到达'{wait_state.total_type}'"
                f"（有人居住）"
            )

        # 建议4: 不可判定性提示
        if wait_state.curvature_at_failure >= self.universe.section_threshold * 0.9:
            alternatives.append(
                f"该问题可能属于不可判定区域(T74)，建议更换问题框架"
            )

        return alternatives

    def identify_undecidable_regions(self) -> List[TypeNode]:
        """
        识别不可判定区域 — 定理T74

        在Universe U中识别不可判定区域：
        曲率R高、无人居住、纤维曲率大的类型组成的区域。

        这些区域中的命题满足T74的条件：
        ∃P:Prop, ¬(Prov(P) ∨ Prov(¬P))

        Returns:
            不可判定区域的类型列表
        """
        return self.universe.identify_undecidable_regions()

    def get_state(self) -> Dict[str, Any]:
        """
        获取Wait状态构造器状态

        Returns:
            构造器状态字典
        """
        total_validated = max(1, self.total_validated)
        return {
            'total_waits': self.total_waits,
            'total_undecidable': self.total_undecidable,
            'total_refusals': self.total_refusals,
            'total_validated': self.total_validated,
            'valid_wait_count': self.valid_wait_count,
            'validation_accuracy': round(self.valid_wait_count / total_validated, 4),
            'wait_history_size': len(self.wait_history),
            'undecidability_reports_size': len(self.undecidability_reports),
            'refusal_history_size': len(self.refusal_history),
            'undecidable_regions': len(self.identify_undecidable_regions()),
            'has_section_search': self.section_search is not None,
            'has_universe': self.universe is not None,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T74': '未决不可判定: ∃P:Prop, ¬(Prov(P)∨Prov(¬P))'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新Wait状态构造器

        Args:
            data: 可选更新数据，支持：
                - wait: 构造Wait {base_type, total_type, reason}
                - undecidability: 检查不可判定性 {proposition}
                - refusal: 生成诚实拒绝 {query, wait_state}
                - validate: 验证Wait {wait_state}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'wait' or 'wait' in data:
                w = data.get('wait', data)
                self.construct_wait(
                    base_type=w.get('base_type', ''),
                    total_type=w.get('total_type', ''),
                    reason=w.get('reason', '')
                )
            elif action == 'undecidability' or 'proposition' in data:
                prop = data.get('proposition', '')
                if prop:
                    self.check_undecidability(prop)
            elif action == 'validate' or 'validate' in data:
                v = data.get('validate', data)
                if isinstance(v, WaitState):
                    self.validate_wait_justification(v)

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示Wait状态构造器的核心功能"""
        results = {}

        # 1. 构造Wait状态（Nat → Empty，Empty无人居住）
        wait1 = self.construct_wait('Nat', 'Empty')
        results['wait_Nat→Empty'] = wait1.to_dict()

        # 2. 构造Wait状态（Bool → Prop，Prop无人居住）
        wait2 = self.construct_wait('Bool', 'Prop')
        results['wait_Bool→Prop'] = wait2.to_dict()

        # 3. 检查不可判定性（T74）
        u1 = self.check_undecidability('Prop')
        u2 = self.check_undecidability('Identity')
        u3 = self.check_undecidability('Nat')
        results['undecidability'] = {
            'Prop': u1.to_dict(),
            'Identity': u2.to_dict(),
            'Nat': u3.to_dict()
        }

        # 4. 生成诚实拒绝
        refusal1 = self.produce_honest_refusal(
            query='Nat能否映射到Empty？',
            wait_state=wait1
        )
        results['honest_refusal'] = refusal1.to_dict()

        # 5. 验证Wait状态的合理性
        valid1 = self.validate_wait_justification(wait1)
        valid2 = self.validate_wait_justification(wait2)
        results['wait_validation'] = {
            'Nat→Empty': valid1,
            'Bool→Prop': valid2
        }

        # 6. 获取替代建议
        alts = self.get_suggested_alternatives(wait1)
        results['suggested_alternatives'] = alts

        # 7. 识别不可判定区域
        undecidable_regions = self.identify_undecidable_regions()
        results['undecidable_regions'] = [t.name for t in undecidable_regions]

        return {
            'simulation': results,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[WaitStateConstructor] = None


def get_instance(section_search: Optional[CurvatureSectionSearch] = None,
                 universe: Optional[UniverseTypeSpace] = None) -> WaitStateConstructor:
    """
    获取WaitStateConstructor单例实例

    Args:
        section_search: CurvatureSectionSearch引用（首次创建时传入）
        universe: UniverseTypeSpace引用（首次创建时传入）

    Returns:
        WaitStateConstructor全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = WaitStateConstructor(section_search, universe)
    return _instance


def construct_wait(base_type: str, total_type: str, reason: str = '') -> WaitState:
    """构造Wait状态（快捷接口）"""
    return get_instance().construct_wait(base_type, total_type, reason)


def check_undecidability(proposition: str) -> UndecidabilityReport:
    """检查不可判定性 — T74（快捷接口）"""
    return get_instance().check_undecidability(proposition)


def produce_honest_refusal(query: str, wait_state: WaitState) -> HonestRefusal:
    """生成诚实拒绝（快捷接口）"""
    return get_instance().produce_honest_refusal(query, wait_state)


def validate_wait_justification(wait_state: WaitState) -> bool:
    """验证Wait状态的合理性（快捷接口）"""
    return get_instance().validate_wait_justification(wait_state)


def get_suggested_alternatives(wait_state: WaitState) -> List[str]:
    """获取替代建议（快捷接口）"""
    return get_instance().get_suggested_alternatives(wait_state)


def identify_undecidable_regions() -> List[TypeNode]:
    """识别不可判定区域 — T74（快捷接口）"""
    return get_instance().identify_undecidable_regions()


def get_state() -> Dict[str, Any]:
    """获取Wait状态构造器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新Wait状态构造器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
