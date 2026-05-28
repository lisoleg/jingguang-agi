"""
TYIDO Property 3: 长程推理（可保持）基础设施
================================================

提供所有模块共享的鲁棒长程推理能力，补足审查表指出的缺陷：
- 缺"错误恢复"（Plan B）
- 缺"资源预算"（超时/算力限制下的降级）

4 个核心组件：

1. SubGoalDecomposer: 子目标分解器
   - 将长程任务分解为依赖有序的子目标 DAG
   - 支持 topological sort 确定执行顺序
   - 每个子目标绑定验收标准

2. StepVerifier: 每步验证器
   - 对推理链的每一步进行验证
   - 支持 min/max/range/exact/func 五种验收标准
   - 验证失败时返回详细诊断信息

3. PlanBFallback: 错误恢复（Plan B）管理器
   - 主计划失败时自动切换备选策略
   - 支持多级降级（Plan B → Plan C → ...）
   - 记录失败原因与切换决策

4. ResourceBudget: 资源预算管理器
   - 跟踪时间/计算步骤预算
   - 预算耗尽时触发优雅降级
   - 返回降级结果而非崩溃

设计原则：
- 零外部依赖（仅用 Python 标准库）
- 与 TYIDO_SelfConsistency (P1) / TYIDO_ContinuousLearning (P2) 同级模式
- 每个组件可独立使用，也可组合使用
- 所有结果包含 tyido_p3_verdict 字段用于审计
"""

from __future__ import annotations

import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set


# ============================================================
# 子目标分解器
# ============================================================

@dataclass
class SubGoal:
    """
    子目标 — 长程推理链中的一个原子步骤

    属性:
        goal_id: 唯一子目标ID
        name: 子目标名称
        description: 描述
        dependencies: 依赖的 goal_id 列表
        acceptance_criteria: 验收标准 (StepVerifier 用)
        status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped'
        result: 执行结果
        error: 错误信息
    """
    goal_id: str
    name: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None

    @staticmethod
    def create(
        name: str,
        description: str = "",
        dependencies: Optional[List[str]] = None,
        acceptance_criteria: Optional[Dict[str, Any]] = None
    ) -> "SubGoal":
        """创建子目标（自动生成ID）"""
        id_raw = f"{time.time()}_{name}"
        goal_id = hashlib.sha256(id_raw.encode()).hexdigest()[:8]
        return SubGoal(
            goal_id=goal_id,
            name=name,
            description=description,
            dependencies=dependencies or [],
            acceptance_criteria=acceptance_criteria or {}
        )


class SubGoalDecomposer:
    """
    子目标分解器 — 将长程任务分解为依赖有序的子目标 DAG

    核心能力:
        - add_goal(): 添加子目标及其依赖
        - get_execution_order(): 拓扑排序，返回可执行顺序
        - get_ready_goals(): 获取当前可执行的子目标（依赖已满足）
        - mark_completed() / mark_failed(): 更新子目标状态
        - get_progress(): 获取整体进度
    """

    def __init__(self, task_name: str = "long_range_task"):
        self.task_name = task_name
        self.goals: Dict[str, SubGoal] = {}
        self._execution_log: List[Dict[str, Any]] = []

    def add_goal(self, goal: SubGoal) -> SubGoal:
        """
        添加子目标

        参数:
            goal: SubGoal 实例（可用 SubGoal.create() 创建）

        返回:
            SubGoal: 已添加的子目标
        """
        self.goals[goal.goal_id] = goal
        return goal

    def get_execution_order(self) -> List[str]:
        """
        拓扑排序，返回子目标执行顺序

        返回:
            List[str]: 按依赖顺序排列的 goal_id 列表

        异常:
            如果存在循环依赖，返回空列表
        """
        # Kahn's algorithm
        in_degree: Dict[str, int] = {gid: 0 for gid in self.goals}
        dependents: Dict[str, List[str]] = {gid: [] for gid in self.goals}

        for gid, goal in self.goals.items():
            for dep_id in goal.dependencies:
                if dep_id in self.goals:
                    dependents[dep_id].append(gid)
                    in_degree[gid] += 1

        # 从入度为0的节点开始
        queue = [gid for gid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            current = queue.pop(0)
            order.append(current)
            for dependent in dependents[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # 检测循环依赖
        if len(order) != len(self.goals):
            return []  # 存在循环

        return order

    def get_ready_goals(self) -> List[SubGoal]:
        """
        获取当前可执行的子目标（所有依赖已完成）

        返回:
            List[SubGoal]: 就绪的子目标列表
        """
        completed_ids = {gid for gid, g in self.goals.items() if g.status == "completed"}
        ready = []
        for gid, goal in self.goals.items():
            if goal.status == "pending":
                deps_met = all(dep in completed_ids for dep in goal.dependencies)
                if deps_met:
                    ready.append(goal)
        return ready

    def mark_completed(self, goal_id: str, result: Any = None):
        """标记子目标为已完成"""
        if goal_id in self.goals:
            self.goals[goal_id].status = "completed"
            self.goals[goal_id].result = result
            self._execution_log.append({
                'goal_id': goal_id,
                'action': 'completed',
                'timestamp': time.time()
            })

    def mark_failed(self, goal_id: str, error: str = ""):
        """标记子目标为失败"""
        if goal_id in self.goals:
            self.goals[goal_id].status = "failed"
            self.goals[goal_id].error = error
            self._execution_log.append({
                'goal_id': goal_id,
                'action': 'failed',
                'error': error,
                'timestamp': time.time()
            })

    def mark_skipped(self, goal_id: str, reason: str = ""):
        """标记子目标为跳过（因依赖失败等）"""
        if goal_id in self.goals:
            self.goals[goal_id].status = "skipped"
            self.goals[goal_id].error = reason
            self._execution_log.append({
                'goal_id': goal_id,
                'action': 'skipped',
                'reason': reason,
                'timestamp': time.time()
            })

    def get_progress(self) -> Dict[str, Any]:
        """获取分解器进度"""
        total = len(self.goals)
        completed = sum(1 for g in self.goals.values() if g.status == "completed")
        failed = sum(1 for g in self.goals.values() if g.status == "failed")
        skipped = sum(1 for g in self.goals.values() if g.status == "skipped")
        pending = sum(1 for g in self.goals.values() if g.status == "pending")
        in_progress = sum(1 for g in self.goals.values() if g.status == "in_progress")

        progress_ratio = completed / total if total > 0 else 0.0

        return {
            'task_name': self.task_name,
            'total_goals': total,
            'completed': completed,
            'failed': failed,
            'skipped': skipped,
            'pending': pending,
            'in_progress': in_progress,
            'progress_ratio': round(progress_ratio, 4),
            'execution_order': self.get_execution_order(),
            'log': self._execution_log[-20:]
        }

    def reset(self):
        """重置所有子目标状态"""
        for goal in self.goals.values():
            goal.status = "pending"
            goal.result = None
            goal.error = None
        self._execution_log.clear()


# ============================================================
# 每步验证器
# ============================================================

@dataclass
class VerificationResult:
    """
    验证结果
    """
    passed: bool
    criterion_name: str
    expected: Any
    actual: Any
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'passed': self.passed,
            'criterion': self.criterion_name,
            'expected': str(self.expected),
            'actual': str(self.actual),
            'error': self.error_message
        }


class StepVerifier:
    """
    每步验证器 — 对推理链的每一步进行验收

    支持的验收标准类型:
        - 'min': actual >= threshold
        - 'max': actual <= threshold
        - 'range': low <= actual <= high
        - 'exact': actual == expected
        - 'func': callable(expected)(actual) == True
        - 'not_none': actual is not None
        - 'type': isinstance(actual, expected)
    """

    def __init__(self):
        self._verification_history: List[Dict[str, Any]] = []
        self._total_verifications: int = 0
        self._pass_count: int = 0

    def verify(self, actual: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行验证

        参数:
            actual: 实际结果
            criteria: 验收标准字典，格式:
                {
                    'name': str,         # 标准名称
                    'type': str,         # 'min'|'max'|'range'|'exact'|'func'|'not_none'|'type'
                    'expected': Any,     # 期望值（type 为 min/max/range/exact/type 时）
                    'low': float,        # range 下界（type 为 range 时）
                    'high': float,       # range 上界（type 为 range 时）
                }

        返回:
            dict: {
                'passed': bool,
                'tyido_p3_verdict': str,
                'results': list[VerificationResult],
                'details': str
            }
        """
        self._total_verifications += 1

        # 支持单个 criteria 或多个 criteria list
        if isinstance(criteria, list):
            criteria_list = criteria
        else:
            criteria_list = [criteria]

        results = []
        all_passed = True

        for c in criteria_list:
            result = self._check_one(actual, c)
            results.append(result)
            if not result.passed:
                all_passed = False

        if all_passed:
            self._pass_count += 1

        verification = {
            'passed': all_passed,
            'tyido_p3_verdict': 'PASS' if all_passed else 'FAIL',
            'results': [r.to_dict() for r in results],
            'details': self._summarize(results)
        }

        self._verification_history.append({
            'timestamp': time.time(),
            'passed': all_passed,
            'results': [r.to_dict() for r in results]
        })

        return verification

    def _check_one(self, actual: Any, criteria: Dict[str, Any]) -> VerificationResult:
        """检查单个验收标准"""
        ctype = criteria.get('type', 'exact')
        expected = criteria.get('expected', None)
        name = criteria.get('name', ctype)

        try:
            if ctype == 'min':
                passed = actual >= expected
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected=f">= {expected}", actual=actual,
                    error_message="" if passed else f"{actual} < {expected}"
                )

            elif ctype == 'max':
                passed = actual <= expected
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected=f"<= {expected}", actual=actual,
                    error_message="" if passed else f"{actual} > {expected}"
                )

            elif ctype == 'range':
                low = criteria.get('low', 0)
                high = criteria.get('high', 1)
                passed = low <= actual <= high
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected=f"[{low}, {high}]", actual=actual,
                    error_message="" if passed else f"{actual} not in [{low}, {high}]"
                )

            elif ctype == 'exact':
                passed = actual == expected
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected=expected, actual=actual,
                    error_message="" if passed else f"{actual} != {expected}"
                )

            elif ctype == 'func':
                assert callable(expected), "'expected' must be callable for type='func'"
                passed = bool(expected(actual))
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected="callable_check", actual=actual,
                    error_message="" if passed else "Function returned False"
                )

            elif ctype == 'not_none':
                passed = actual is not None
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected="not None", actual=actual,
                    error_message="" if passed else "Result is None"
                )

            elif ctype == 'type':
                passed = isinstance(actual, expected)
                return VerificationResult(
                    passed=passed, criterion_name=name,
                    expected=f"isinstance(x, {expected})", actual=type(actual).__name__,
                    error_message="" if passed else f"{type(actual).__name__} is not {expected}"
                )

            else:
                return VerificationResult(
                    passed=False, criterion_name=name,
                    expected="unknown_type", actual=actual,
                    error_message=f"Unknown criterion type: {ctype}"
                )

        except Exception as e:
            return VerificationResult(
                passed=False, criterion_name=name,
                expected=str(expected), actual=str(actual),
                error_message=f"Verification error: {str(e)}"
            )

    def _summarize(self, results: List[VerificationResult]) -> str:
        """生成验证摘要"""
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        failed_details = [r.error_message for r in results if not r.passed and r.error_message]
        summary = f"{passed}/{total} criteria passed"
        if failed_details:
            summary += f"; failures: {'; '.join(failed_details[:3])}"
        return summary

    def get_state(self) -> Dict[str, Any]:
        """获取验证器状态"""
        return {
            'total_verifications': self._total_verifications,
            'pass_count': self._pass_count,
            'pass_rate': round(self._pass_count / max(self._total_verifications, 1), 4),
            'recent_results': self._verification_history[-10:]
        }


# ============================================================
# 错误恢复（Plan B）管理器
# ============================================================

@dataclass
class FallbackPlan:
    """
    降级计划 — 主计划失败时的备选策略
    """
    plan_name: str           # 如 'Plan B', 'Plan C'
    priority: int            # 数字越小优先级越高（Plan B = 1）
    strategy: Callable       # 降级策略函数
    description: str = ""
    applicable_errors: List[str] = field(default_factory=list)  # 适用错误类型


@dataclass
class RecoveryRecord:
    """
    恢复记录
    """
    timestamp: float
    original_plan: str
    failed_goal: str
    error_type: str
    error_message: str
    fallback_plan: str
    fallback_result: str     # 'success' | 'failed' | 'skipped'
    description: str = ""


class PlanBFallback:
    """
    错误恢复管理器 — 主计划失败时自动切换备选策略

    核心能力:
        - register_plan(): 注册降级计划
        - try_recover(): 当主计划失败时尝试恢复
        - get_recovery_history(): 获取恢复历史
        - get_state(): 获取管理器状态
    """

    def __init__(self):
        self._plans: Dict[str, FallbackPlan] = {}
        self._recovery_history: List[RecoveryRecord] = []
        self._total_recoveries: int = 0
        self._successful_recoveries: int = 0

    def register_plan(self, plan: FallbackPlan) -> FallbackPlan:
        """
        注册降级计划

        参数:
            plan: FallbackPlan 实例

        返回:
            FallbackPlan: 已注册的计划
        """
        self._plans[plan.plan_name] = plan
        return plan

    def try_recover(
        self,
        failed_goal: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        尝试从失败中恢复

        按优先级尝试所有适用降级计划：
        1. 筛选 applicable_errors 匹配的计划
        2. 如果无匹配，尝试所有计划（按 priority 排序）
        3. 返回第一个成功的降级结果

        参数:
            failed_goal: 失败的子目标名称
            error: 原始异常
            context: 传递给降级策略的上下文

        返回:
            dict: {
                'recovered': bool,
                'tyido_p3_verdict': str,
                'plan_used': str,
                'result': Any,
                'details': str
            }
        """
        error_type = type(error).__name__
        error_message = str(error)

        # 按优先级排序
        sorted_plans = sorted(self._plans.values(), key=lambda p: p.priority)

        # 先尝试匹配错误类型的计划
        matching = [p for p in sorted_plans
                    if not p.applicable_errors or error_type in p.applicable_errors
                    or any(e in error_message for e in p.applicable_errors)]

        # 如果无匹配，尝试所有计划
        candidates = matching if matching else sorted_plans

        ctx = context or {}
        last_error = ""

        for plan in candidates:
            self._total_recoveries += 1
            try:
                result = plan.strategy(ctx)
                self._successful_recoveries += 1

                record = RecoveryRecord(
                    timestamp=time.time(),
                    original_plan="main",
                    failed_goal=failed_goal,
                    error_type=error_type,
                    error_message=error_message,
                    fallback_plan=plan.plan_name,
                    fallback_result='success',
                    description=f"Recovered via {plan.plan_name}"
                )
                self._recovery_history.append(record)

                return {
                    'recovered': True,
                    'tyido_p3_verdict': 'PASS',
                    'plan_used': plan.plan_name,
                    'result': result,
                    'details': f"Recovered via {plan.plan_name}: {plan.description}"
                }

            except Exception as fallback_error:
                last_error = str(fallback_error)
                record = RecoveryRecord(
                    timestamp=time.time(),
                    original_plan="main",
                    failed_goal=failed_goal,
                    error_type=error_type,
                    error_message=error_message,
                    fallback_plan=plan.plan_name,
                    fallback_result='failed',
                    description=f"{plan.plan_name} also failed: {last_error}"
                )
                self._recovery_history.append(record)

        # 所有降级计划都失败
        return {
            'recovered': False,
            'tyido_p3_verdict': 'FAIL',
            'plan_used': 'none',
            'result': None,
            'details': f"All fallback plans failed. Last error: {last_error}"
        }

    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """获取恢复历史"""
        return [
            {
                'timestamp': r.timestamp,
                'failed_goal': r.failed_goal,
                'error_type': r.error_type,
                'plan_used': r.fallback_plan,
                'result': r.fallback_result,
                'description': r.description
            }
            for r in self._recovery_history[-20:]
        ]

    def get_state(self) -> Dict[str, Any]:
        """获取恢复管理器状态"""
        return {
            'registered_plans': list(self._plans.keys()),
            'total_recoveries': self._total_recoveries,
            'successful_recoveries': self._successful_recoveries,
            'recovery_rate': round(
                self._successful_recoveries / max(self._total_recoveries, 1), 4
            ),
            'recent_history': self.get_recovery_history()[-5:]
        }


# ============================================================
# 资源预算管理器
# ============================================================

class ResourceBudget:
    """
    资源预算管理器 — 跟踪时间/计算预算，预算耗尽时优雅降级

    核心能力:
        - start(): 开始计时
        - check(): 检查预算是否耗尽
        - tick(): 消耗一个计算步骤
        - get_remaining(): 获取剩余资源
        - graceful_degrade(): 优雅降级，返回可用的部分结果
        - get_state(): 获取管理器状态

    使用模式:
        budget = ResourceBudget(max_time=5.0, max_steps=1000)
        budget.start()
        for step in execution_order:
            if budget.exhausted():
                # 优雅降级：返回已完成的子目标结果
                partial = budget.graceful_degrade(completed_results)
                break
            budget.tick()
            # ... 执行步骤 ...
    """

    def __init__(
        self,
        max_time: float = 30.0,
        max_steps: int = 1000,
        warn_threshold: float = 0.8
    ):
        """
        参数:
            max_time: 最大执行时间（秒）
            max_steps: 最大计算步骤数
            warn_threshold: 告警阈值（资源使用到此比例时触发告警）
        """
        self.max_time = max_time
        self.max_steps = max_steps
        self.warn_threshold = warn_threshold

        self._start_time: Optional[float] = None
        self._steps_used: int = 0
        self._is_running: bool = False
        self._warnings: List[Dict[str, Any]] = []
        self._degradation_history: List[Dict[str, Any]] = []

    def start(self):
        """开始计时"""
        self._start_time = time.time()
        self._steps_used = 0
        self._is_running = True
        self._warnings.clear()

    def stop(self):
        """停止计时"""
        self._is_running = False

    def tick(self) -> Dict[str, Any]:
        """
        消耗一个计算步骤

        返回:
            dict: {'exhausted': bool, 'remaining_steps': int, 'warning': Optional[str]}
        """
        if not self._is_running:
            return {'exhausted': False, 'remaining_steps': self.max_steps, 'warning': None}

        self._steps_used += 1
        remaining_steps = max(0, self.max_steps - self._steps_used)
        exhausted = self.exhausted()

        warning = None
        if not exhausted:
            # 检查是否接近阈值
            time_ratio = self._time_ratio()
            step_ratio = self._step_ratio()
            overall_ratio = max(time_ratio, step_ratio)

            if overall_ratio >= self.warn_threshold:
                warning = self._generate_warning(time_ratio, step_ratio)
                if not self._warnings or self._warnings[-1].get('ratio', 0) < overall_ratio - 0.05:
                    self._warnings.append({
                        'timestamp': time.time(),
                        'time_ratio': round(time_ratio, 4),
                        'step_ratio': round(step_ratio, 4),
                        'warning': warning
                    })

        return {
            'exhausted': exhausted,
            'remaining_steps': remaining_steps,
            'warning': warning
        }

    def exhausted(self) -> bool:
        """检查资源是否耗尽"""
        if not self._is_running:
            return False
        return self._time_ratio() >= 1.0 or self._step_ratio() >= 1.0

    def _time_ratio(self) -> float:
        """已使用时间比例"""
        if not self._start_time or self.max_time <= 0:
            return 0.0
        elapsed = time.time() - self._start_time
        return min(1.0, elapsed / self.max_time)

    def _step_ratio(self) -> float:
        """已使用步骤比例"""
        if self.max_steps <= 0:
            return 1.0
        return min(1.0, self._steps_used / self.max_steps)

    def _generate_warning(self, time_ratio: float, step_ratio: float) -> str:
        """生成告警信息"""
        parts = []
        if time_ratio >= self.warn_threshold:
            parts.append(f"time {time_ratio:.0%}")
        if step_ratio >= self.warn_threshold:
            parts.append(f"steps {step_ratio:.0%}")
        return f"Resource budget warning: {', '.join(parts)} used"

    def get_remaining(self) -> Dict[str, Any]:
        """
        获取剩余资源

        返回:
            dict: {'time_remaining': float, 'steps_remaining': int, 'ratio': float}
        """
        if not self._is_running or not self._start_time:
            return {
                'time_remaining': self.max_time,
                'steps_remaining': self.max_steps,
                'overall_ratio': 0.0
            }

        time_remaining = max(0, self.max_time - (time.time() - self._start_time))
        steps_remaining = max(0, self.max_steps - self._steps_used)
        overall_ratio = max(self._time_ratio(), self._step_ratio())

        return {
            'time_remaining': round(time_remaining, 3),
            'steps_remaining': steps_remaining,
            'overall_ratio': round(overall_ratio, 4)
        }

    def graceful_degrade(self, partial_results: Any) -> Dict[str, Any]:
        """
        优雅降级 — 预算耗尽时返回可用的部分结果

        参数:
            partial_results: 已完成的部分结果

        返回:
            dict: {
                'degraded': True,
                'tyido_p3_verdict': 'DEGRADED',
                'partial_results': Any,
                'resources_used': dict,
                'completion_ratio': float,
                'details': str
            }
        """
        # 先停止计时，确保 get_remaining() 返回准确值
        self._is_running = False
        resources = self.get_remaining()
        # completion_ratio = 已使用的资源比例（即牺牲的那部分之外的保留比例）
        # 这里用 1 - max_ratio 表示"已完成的比例"
        # 但如果外部传入 partial_results 有自己的进度，应优先用外部计算值
        completion_ratio = 1.0 - resources['overall_ratio']
        completion_ratio = max(0.0, min(1.0, completion_ratio))

        degradation = {
            'degraded': True,
            'tyido_p3_verdict': 'DEGRADED',
            'partial_results': partial_results,
            'resources_used': {
                'time_ratio': round(self._time_ratio(), 4),
                'steps_ratio': round(self._step_ratio(), 4),
                'steps_used': self._steps_used,
                'max_steps': self.max_steps
            },
            'completion_ratio': round(completion_ratio, 4),
            'details': f"Gracefully degraded at {completion_ratio:.0%} completion"
        }

        self._degradation_history.append({
            'timestamp': time.time(),
            'completion_ratio': completion_ratio,
            'steps_used': self._steps_used
        })

        return degradation

    def get_state(self) -> Dict[str, Any]:
        """获取预算管理器状态"""
        return {
            'is_running': self._is_running,
            'max_time': self.max_time,
            'max_steps': self.max_steps,
            'remaining': self.get_remaining(),
            'warnings': self._warnings[-5:],
            'degradation_count': len(self._degradation_history),
            'recent_degradations': self._degradation_history[-5:]
        }


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TYIDO Property 3: 长程推理基础设施 自测")
    print("=" * 60)

    # 1. SubGoalDecomposer
    print("\n--- SubGoalDecomposer ---")
    decomposer = SubGoalDecomposer(task_name="test_reasoning_chain")
    g1 = SubGoal.create("normalize_inputs", "归一化输入", acceptance_criteria={'type': 'not_none'})
    g2 = SubGoal.create("compute_lamda", "计算叙事作用量", dependencies=[g1.goal_id],
                         acceptance_criteria={'type': 'range', 'low': 0, 'high': 1})
    g3 = SubGoal.create("compute_impedance", "计算阻抗", dependencies=[g1.goal_id],
                         acceptance_criteria={'type': 'range', 'low': 0, 'high': 1})
    g4 = SubGoal.create("compute_B", "计算顿悟准备度", dependencies=[g2.goal_id, g3.goal_id],
                         acceptance_criteria={'type': 'range', 'low': 0, 'high': 1})

    for g in [g1, g2, g3, g4]:
        decomposer.add_goal(g)

    order = decomposer.get_execution_order()
    print(f"Execution order: {[decomposer.goals[gid].name for gid in order]}")
    print(f"Ready goals: {[g.name for g in decomposer.get_ready_goals()]}")

    decomposer.mark_completed(g1.goal_id, "normalized")
    print(f"After g1 done, ready: {[g.name for g in decomposer.get_ready_goals()]}")
    print(f"Progress: {decomposer.get_progress()['progress_ratio']:.0%}")

    # 2. StepVerifier
    print("\n--- StepVerifier ---")
    verifier = StepVerifier()

    # 通过的验证
    result1 = verifier.verify(0.85, [
        {'name': 'B_in_range', 'type': 'range', 'low': 0, 'high': 1},
        {'name': 'B_above_threshold', 'type': 'min', 'expected': 0.8}
    ])
    print(f"Pass case: verdict={result1['tyido_p3_verdict']}, details={result1['details']}")

    # 失败的验证
    result2 = verifier.verify(-0.1, {'name': 'non_negative', 'type': 'min', 'expected': 0})
    print(f"Fail case: verdict={result2['tyido_p3_verdict']}, details={result2['details']}")

    # 类型验证
    result3 = verifier.verify([1, 2, 3], {'name': 'is_list', 'type': 'type', 'expected': list})
    print(f"Type check: verdict={result3['tyido_p3_verdict']}")

    # 函数验证
    result4 = verifier.verify(0.5, {'name': 'custom_check', 'type': 'func', 'expected': lambda x: 0 <= x <= 1})
    print(f"Func check: verdict={result4['tyido_p3_verdict']}")

    print(f"Verifier state: {verifier.get_state()}")

    # 3. PlanBFallback
    print("\n--- PlanBFallback ---")
    fallback = PlanBFallback()

    fallback.register_plan(FallbackPlan(
        plan_name="Plan B: approximate",
        priority=1,
        strategy=lambda ctx: ctx.get('input', 0) * 0.9,  # 近似计算
        description="使用近似算法"
    ))

    fallback.register_plan(FallbackPlan(
        plan_name="Plan C: default",
        priority=2,
        strategy=lambda ctx: 0.5,  # 返回默认值
        description="返回保守默认值"
    ))

    # 主计划失败 → 自动降级
    recovery = fallback.try_recover(
        failed_goal="compute_B",
        error=ValueError("Division by zero"),
        context={'input': 0.85}
    )
    print(f"Recovery: verdict={recovery['tyido_p3_verdict']}, plan={recovery['plan_used']}, "
          f"result={recovery['result']}")
    print(f"Fallback state: {fallback.get_state()}")

    # 4. ResourceBudget
    print("\n--- ResourceBudget ---")
    budget = ResourceBudget(max_time=2.0, max_steps=5, warn_threshold=0.6)
    budget.start()

    for i in range(7):
        tick_result = budget.tick()
        remaining = budget.get_remaining()
        print(f"  Step {i+1}: exhausted={tick_result['exhausted']}, "
              f"remaining_steps={remaining['steps_remaining']}, "
              f"warning={tick_result['warning']}")

        if tick_result['exhausted']:
            degrade = budget.graceful_degrade(partial_results={"completed": i})
            print(f"  Degraded: {degrade['tyido_p3_verdict']}, "
                  f"completion={degrade['completion_ratio']:.0%}")
            break

    budget.stop()
    print(f"Budget state: warnings={len(budget._warnings)}, "
          f"degradations={budget.get_state()['degradation_count']}")

    print("\n" + "=" * 60)
    print("TYIDO Property 3 基础设施 自测完成")
    print("=" * 60)
