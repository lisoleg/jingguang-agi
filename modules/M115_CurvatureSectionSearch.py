# -*- coding: utf-8 -*-
"""
M115: 曲率截面搜索 (Curvature-Guided Section Search)
基于§7.3 HoTT视角的截面搜索理论

核心概念：LLM推理 = 截面搜索 s:B→E in Universe U
- Prompt = Base Space B
- 曲率R引导搜索方向
- 无截面 → 返回Wait

定理:
  T73 曲率收敛定理 — section_search收敛 ⟺ Σ_i R_i < ∞
  截面搜索收敛当且仅当沿搜索路径的曲率级数收敛

作者: 太乙AGI团队
日期: 2026-05-19
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

from modules.M114_UniverseTypeSpace import UniverseTypeSpace, get_instance as get_m114_instance


# ==================== 数据结构 ====================

@dataclass
class SearchStep:
    """
    搜索步骤 — 截面搜索中的单步导航

    每一步表示从from_type沿某个方向导航到to_type，
    curvature_delta记录该步的曲率增量，
    direction表示导航方向（'forward'|'lateral'|'backward'）。
    """
    from_type: str                     # 起始类型
    to_type: str                       # 目标类型
    curvature_delta: float = 0.0      # 曲率增量
    direction: str = 'forward'         # 导航方向: 'forward' | 'lateral' | 'backward'

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class SearchPath:
    """
    搜索路径 — 截面搜索的完整导航路径

    由一系列SearchStep组成，记录从起始类型到目标类型的导航过程。
    曲率级数 Σ_i R_i 用于判定搜索是否收敛（定理T73）。
    """
    steps: List[SearchStep] = field(default_factory=list)

    def total_curvature(self) -> float:
        """计算路径的总曲率（曲率级数 Σ_i R_i）"""
        return round(sum(s.curvature_delta for s in self.steps), 4)

    def curvature_series_converges(self, threshold: float = 1.0) -> bool:
        """
        判断曲率级数是否收敛 — 定理T73

        截面搜索收敛 ⟺ Σ_i R_i < ∞
        在实际实现中，使用threshold作为收敛判据：
        如果总曲率 < threshold，则认为级数收敛。

        Args:
            threshold: 收敛阈值（默认1.0）

        Returns:
            True如果曲率级数收敛
        """
        return self.total_curvature() < threshold

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'steps': [s.to_dict() for s in self.steps],
            'total_curvature': self.total_curvature(),
            'step_count': len(self.steps)
        }


@dataclass
class SectionSearchRequest:
    """
    截面搜索请求

    封装截面搜索的输入参数：
    - base_space: 底空间B（Prompt对应的类型）
    - total_space: 全空间E（目标类型）
    - max_curvature: 允许的最大曲率
    - prompt_context: Prompt上下文信息
    """
    base_space: str                    # 底空间B类型
    total_space: str                    # 全空间E类型
    max_curvature: float = 0.75       # 允许的最大曲率
    prompt_context: str = ''          # Prompt上下文

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class SectionSearchResult:
    """
    截面搜索结果

    封装截面搜索的输出：
    - found: 是否找到截面
    - section: 截面信息（类型映射字符串）
    - curvature_R: 搜索路径的总曲率
    - search_path: 完整搜索路径
    - status: 搜索状态 ('found' | 'wait' | 'diverged' | 'no_type')
    """
    found: bool                        # 是否找到截面
    section: str                       # 截面信息
    curvature_R: float = 0.0         # 总曲率
    search_path: SearchPath = field(default_factory=SearchPath)
    status: str = 'unknown'           # 搜索状态

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'found': self.found,
            'section': self.section,
            'curvature_R': self.curvature_R,
            'search_path': self.search_path.to_dict(),
            'status': self.status
        }


# ==================== 核心类 ====================

class CurvatureSectionSearch:
    """
    M115: 曲率截面搜索 — Curvature-Guided Section Search

    LLM推理建模为截面搜索 s:B→E in Universe U：
    - Prompt = Base Space B（底空间）
    - 目标回答 = Total Space E（全空间）
    - 曲率R引导搜索方向（沿低曲率路径导航）
    - 无截面 → 返回Wait（不幻觉）

    核心算法 search_section:
    1. 检查截面存在性（调用M114的check_section_existence, T72）
    2. 计算曲率R，确定搜索方向
    3. 沿低曲率路径构造性导航
    4. 若到达E → 返回section
    5. 若无法到达 → 返回Wait状态

    定理T73（曲率收敛定理）:
    section_search收敛 ⟺ Σ_i R_i < ∞ (曲率级数收敛)
    """

    def __init__(self, universe: Optional[UniverseTypeSpace] = None):
        """
        初始化曲率截面搜索

        Args:
            universe: UniverseTypeSpace引用（默认使用M114全局单例）
        """
        # 引用M114的类型空间
        self.universe: UniverseTypeSpace = universe or get_m114_instance()

        # 搜索历史
        self.search_history: List[SectionSearchResult] = []

        # 收敛阈值（T73: Σ_i R_i < threshold ⟹ 收敛）
        self.convergence_threshold: float = 1.0

        # 最大搜索深度
        self.default_max_depth: int = 10

        # 统计
        self.total_searches: int = 0
        self.found_count: int = 0
        self.wait_count: int = 0
        self.diverged_count: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def search_section(self, base_type: str, total_type: str,
                       max_depth: int = 10) -> SectionSearchResult:
        """
        核心截面搜索算法

        在Universe U中搜索从base_type(B)到total_type(E)的截面s:B→E。

        算法步骤:
        1. 检查截面存在性（T72: curvature_R < threshold）
        2. 计算曲率R，确定搜索方向
        3. 沿低曲率路径构造性导航
        4. 若到达E → 返回section
        5. 若无法到达 → 返回Wait状态

        Args:
            base_type: 底空间B类型名称
            total_type: 全空间E类型名称
            max_depth: 最大搜索深度（默认10）

        Returns:
            SectionSearchResult: 搜索结果，包含found, section, curvature_R, search_path, status
        """
        self.total_searches += 1
        search_path = SearchPath()

        # 步骤1: 检查截面存在性（T72）
        section_exists = self.universe.check_section_existence(base_type, total_type)

        if not section_exists:
            # 截面不存在 → 返回Wait
            curvature = self.compute_curvature(base_type, total_type)
            result = SectionSearchResult(
                found=False,
                section='',
                curvature_R=curvature,
                search_path=search_path,
                status='wait'
            )
            self.wait_count += 1
            self.search_history.append(result)
            self.last_update = time.time()
            return result

        # 步骤2: 计算曲率R，确定搜索方向
        curvature = self.compute_curvature(base_type, total_type)

        # 步骤3: 沿低曲率路径构造性导航
        current_type = base_type
        visited: set = {base_type}
        depth = 0

        while depth < max_depth and current_type != total_type:
            # 沿纤维导航
            step = self.navigate_along_fiber(current_type, total_type, curvature)

            # 防止循环
            if step.to_type in visited:
                # 尝试横向导航
                lateral_type = self._find_lateral_type(current_type, total_type, visited)
                if lateral_type:
                    step = SearchStep(
                        from_type=current_type,
                        to_type=lateral_type,
                        curvature_delta=self.compute_curvature(current_type, lateral_type),
                        direction='lateral'
                    )
                else:
                    # 无法继续导航 → Wait
                    break

            search_path.steps.append(step)
            visited.add(step.to_type)
            current_type = step.to_type
            depth += 1

            # 更新曲率
            curvature = self.compute_curvature(current_type, total_type)

        # 步骤4/5: 判定搜索结果
        if current_type == total_type:
            # 到达E → 返回section
            result = SectionSearchResult(
                found=True,
                section=f's:{base_type}→{total_type}',
                curvature_R=search_path.total_curvature(),
                search_path=search_path,
                status='found'
            )
            self.found_count += 1
        elif search_path.curvature_series_converges(self.convergence_threshold):
            # 曲率级数收敛但未到达 → Wait（可能需要更多步骤）
            result = SectionSearchResult(
                found=False,
                section='',
                curvature_R=search_path.total_curvature(),
                search_path=search_path,
                status='wait'
            )
            self.wait_count += 1
        else:
            # 曲率级数发散 → Diverged
            result = SectionSearchResult(
                found=False,
                section='',
                curvature_R=search_path.total_curvature(),
                search_path=search_path,
                status='diverged'
            )
            self.diverged_count += 1

        self.search_history.append(result)
        if len(self.search_history) > 200:
            self.search_history.pop(0)

        self.last_update = time.time()
        return result

    def compute_curvature(self, base_type: str, total_type: str) -> float:
        """
        计算B→E的曲率

        曲率R衡量从base_type到total_type的逻辑路径弯曲程度：
        - R ≈ 0: 路径平坦，推理直接
        - R → 1: 路径高度弯曲，推理困难

        基于：
        1. M114中的纤维曲率
        2. 类型距离
        3. 居住性差异

        Args:
            base_type: 底空间B类型
            total_type: 全空间E类型

        Returns:
            曲率R值，范围[0, 1]
        """
        # 获取或构造纤维
        fiber_key = (base_type, total_type)
        if fiber_key in self.universe.fibers:
            fiber = self.universe.fibers[fiber_key]
            return fiber.curvature_R

        # 动态计算
        type_distance = self.universe.compute_type_distance(base_type, total_type)

        # 获取类型曲率
        base_curvature = self.universe.get_curvature(base_type)
        total_curvature = self.universe.get_curvature(total_type)

        # 综合曲率 = 类型距离*0.5 + 源目标曲率平均*0.5
        curvature_R = round(
            type_distance * 0.5 + (base_curvature + total_curvature) * 0.25, 4
        )

        return min(1.0, max(0.0, curvature_R))

    def navigate_along_fiber(self, current_type: str, target_type: str,
                             curvature: float) -> SearchStep:
        """
        沿纤维导航 — 曲率引导的方向选择

        根据当前曲率R确定导航方向：
        - curvature < 0.3: forward（低曲率，直接前进）
        - 0.3 ≤ curvature < 0.6: lateral（中等曲率，横向搜索更优路径）
        - curvature ≥ 0.6: backward（高曲率，后退寻找替代路径）

        Args:
            current_type: 当前类型
            target_type: 目标类型
            curvature: 当前曲率R

        Returns:
            SearchStep: 导航步骤
        """
        # 确定导航方向
        if curvature < 0.3:
            direction = 'forward'
        elif curvature < 0.6:
            direction = 'lateral'
        else:
            direction = 'backward'

        # 寻找下一个类型
        next_type = self._find_next_type(current_type, target_type, direction)

        # 计算曲率增量
        curvature_delta = self.compute_curvature(current_type, next_type)

        return SearchStep(
            from_type=current_type,
            to_type=next_type,
            curvature_delta=curvature_delta,
            direction=direction
        )

    def detect_wait_condition(self, result: SectionSearchResult) -> bool:
        """
        检测是否应该返回Wait

        Wait条件（截面不存在，不应幻觉）：
        1. 截面不存在（T72: curvature_R ≥ threshold）
        2. 搜索路径发散（T73: 曲率级数不收敛）
        3. 搜索到达最大深度但未找到目标

        当检测到Wait条件时，系统必须返回Wait而非幻觉。
        这是诚实拒绝机制的核心。

        Args:
            result: 截面搜索结果

        Returns:
            True如果应返回Wait
        """
        # 截面不存在 → Wait
        if result.status == 'wait':
            return True

        # 搜索发散 → Wait
        if result.status == 'diverged':
            return True

        # 曲率超过阈值 → Wait
        if result.curvature_R >= self.universe.section_threshold:
            return True

        # 曲率级数不收敛 → Wait
        if not result.search_path.curvature_series_converges(self.convergence_threshold):
            return True

        return False

    def check_convergence(self, search_path: SearchPath) -> bool:
        """
        检查曲率级数收敛性 — 定理T73

        定理T73（曲率收敛定理）:
        section_search收敛 ⟺ Σ_i R_i < ∞

        在实际实现中，如果搜索路径的总曲率小于收敛阈值，
        则认为曲率级数收敛，搜索过程有效。

        Args:
            search_path: 搜索路径

        Returns:
            True如果曲率级数收敛
        """
        return search_path.curvature_series_converges(self.convergence_threshold)

    def _find_next_type(self, current_type: str, target_type: str,
                        direction: str) -> str:
        """
        寻找下一个导航目标类型

        根据导航方向在Universe U中选择下一个类型：
        - forward: 选择距离target更近的类型
        - lateral: 选择曲率相似的类型
        - backward: 选择距离root更近的类型

        Args:
            current_type: 当前类型
            target_type: 目标类型
            direction: 导航方向

        Returns:
            下一个类型的名称
        """
        all_types = list(self.universe.types.keys())

        if current_type in all_types:
            all_types.remove(current_type)
        if not all_types:
            return current_type

        if direction == 'forward':
            # 前进：选择距离target最近的类型
            candidates = sorted(
                all_types,
                key=lambda t: self.universe.compute_type_distance(t, target_type)
            )
            return candidates[0] if candidates else current_type

        elif direction == 'lateral':
            # 横向：选择曲率与当前类型最接近的类型
            current_curvature = self.universe.get_curvature(current_type)
            candidates = sorted(
                all_types,
                key=lambda t: abs(self.universe.get_curvature(t) - current_curvature)
            )
            return candidates[0] if candidates else current_type

        elif direction == 'backward':
            # 后退：选择距离root最近的类型
            candidates = sorted(
                all_types,
                key=lambda t: self.universe.types.get(t, self.universe.types.get('Nat')).distance_to_root
                if t in self.universe.types else 1.0
            )
            return candidates[0] if candidates else current_type

        return current_type

    def _find_lateral_type(self, current_type: str, target_type: str,
                           visited: set) -> Optional[str]:
        """
        寻找横向替代类型（避免循环）

        在已访问类型之外寻找曲率相似的替代类型。

        Args:
            current_type: 当前类型
            target_type: 目标类型
            visited: 已访问类型集合

        Returns:
            替代类型名称，或None
        """
        all_types = list(self.universe.types.keys())
        unvisited = [t for t in all_types if t not in visited and t != current_type]

        if not unvisited:
            return None

        # 优先选择距离target更近的未访问类型
        candidates = sorted(
            unvisited,
            key=lambda t: self.universe.compute_type_distance(t, target_type)
        )
        return candidates[0]

    def get_state(self) -> Dict[str, Any]:
        """
        获取截面搜索状态

        Returns:
            搜索状态字典
        """
        total = max(1, self.total_searches)
        return {
            'total_searches': self.total_searches,
            'found_count': self.found_count,
            'wait_count': self.wait_count,
            'diverged_count': self.diverged_count,
            'found_rate': round(self.found_count / total, 4),
            'wait_rate': round(self.wait_count / total, 4),
            'convergence_threshold': self.convergence_threshold,
            'default_max_depth': self.default_max_depth,
            'has_universe': self.universe is not None,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T73': '曲率收敛: Σ_i R_i < ∞ ⟹ 搜索收敛'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新截面搜索状态

        Args:
            data: 可选更新数据，支持：
                - search: 执行截面搜索 {base_type, total_type, max_depth}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')
            if action == 'search' or 'search' in data:
                sch = data.get('search', data)
                self.search_section(
                    base_type=sch.get('base_type', ''),
                    total_type=sch.get('total_type', ''),
                    max_depth=sch.get('max_depth', self.default_max_depth)
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示截面搜索的核心功能"""
        results = {}

        # 1. 测试存在截面的搜索（Nat → Bool，两者都有构造子）
        r1 = self.search_section('Nat', 'Bool')
        results['Nat→Bool'] = r1.to_dict()

        # 2. 测试不存在截面的搜索（Nat → Empty，Empty无人居住）
        r2 = self.search_section('Nat', 'Empty')
        results['Nat→Empty'] = r2.to_dict()

        # 3. 测试Bool → Nat
        r3 = self.search_section('Bool', 'Nat')
        results['Bool→Nat'] = r3.to_dict()

        # 4. 测试Prop → Nat
        r4 = self.search_section('Prop', 'Nat')
        results['Prop→Nat'] = r4.to_dict()

        # 5. Wait条件检测
        wait_checks = {
            'Nat→Bool': self.detect_wait_condition(r1),
            'Nat→Empty': self.detect_wait_condition(r2),
            'Bool→Nat': self.detect_wait_condition(r3),
            'Prop→Nat': self.detect_wait_condition(r4),
        }

        # 6. 收敛性检查（T73）
        convergence = {
            'Nat→Bool': self.check_convergence(r1.search_path),
            'Nat→Empty': self.check_convergence(r2.search_path),
        }

        return {
            'search_results': results,
            'wait_conditions': wait_checks,
            'convergence_T73': convergence,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[CurvatureSectionSearch] = None


def get_instance(universe: Optional[UniverseTypeSpace] = None) -> CurvatureSectionSearch:
    """
    获取CurvatureSectionSearch单例实例

    Args:
        universe: UniverseTypeSpace引用（首次创建时传入）

    Returns:
        CurvatureSectionSearch全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = CurvatureSectionSearch(universe)
    return _instance


def search_section(base_type: str, total_type: str, max_depth: int = 10) -> SectionSearchResult:
    """截面搜索（快捷接口）"""
    return get_instance().search_section(base_type, total_type, max_depth)


def compute_curvature(base_type: str, total_type: str) -> float:
    """计算B→E的曲率（快捷接口）"""
    return get_instance().compute_curvature(base_type, total_type)


def navigate_along_fiber(current_type: str, target_type: str,
                         curvature: float) -> SearchStep:
    """沿纤维导航（快捷接口）"""
    return get_instance().navigate_along_fiber(current_type, target_type, curvature)


def detect_wait_condition(result: SectionSearchResult) -> bool:
    """检测Wait条件（快捷接口）"""
    return get_instance().detect_wait_condition(result)


def check_convergence(search_path: SearchPath) -> bool:
    """检查曲率级数收敛性 — T73（快捷接口）"""
    return get_instance().check_convergence(search_path)


def get_state() -> Dict[str, Any]:
    """获取截面搜索状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新截面搜索状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
