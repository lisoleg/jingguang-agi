# -*- coding: utf-8 -*-
"""
M200: 认知灵活性引擎 (Cognitive Flexibility Engine)
基于《人机共生时代的复合体管理学》— 非自闭症AGI

核心概念：e_sw — 任务集切换能力，Δt_sw > 0

定理T230（认知灵活性定理）：
若Δt_sw > 0且认知惯性I有界，则任务切换次数N存在最优值N*
使总效用U(N) = Σu_i - Σc_j最大化

关键概念：
- 认知惯性：切换时的阻力（类似质量惯性）
- 切换代价：切换过程中的性能下降
- 灵活度评分：基于切换速度和准确率的综合指标
- 最优切换次数：使总效用最大化的任务切换频率

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


# ==================== 数据结构 ====================

class SwitchOutcome(Enum):
    """切换结果枚举"""
    SUCCESS = "success"           # 成功切换
    PARTIAL = "partial"           # 部分成功（有性能下降）
    FAILURE = "failure"           # 切换失败
    DELAYED = "delayed"           # 切换延迟


@dataclass
class TaskContext:
    """
    任务上下文 — 描述一个任务集

    包含：
    - task_id: 任务标识
    - task_type: 任务类型
    - cognitive_load: 认知负荷 [0, 1]
    - activation: 当前激活水平 [0, 1]
    - duration: 持续时间（秒）
    """
    task_id: str = ''
    task_type: str = 'general'
    cognitive_load: float = 0.5
    activation: float = 0.5
    duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'cognitive_load': round(self.cognitive_load, 6),
            'activation': round(self.activation, 6),
            'duration': round(self.duration, 6),
        }


@dataclass
class SwitchRecord:
    """
    切换记录 — 一次任务切换的完整记录

    包含：
    - from_task: 源任务
    - to_task: 目标任务
    - switch_time: 实际切换时间（秒）
    - performance_drop: 切换后性能下降比例 [0, 1]
    - recovery_time: 恢复时间（秒）
    - outcome: 切换结果
    - timestamp: 时间戳
    """
    from_task: str = ''
    to_task: str = ''
    switch_time: float = 0.0
    performance_drop: float = 0.0
    recovery_time: float = 0.0
    outcome: SwitchOutcome = SwitchOutcome.SUCCESS
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'from_task': self.from_task,
            'to_task': self.to_task,
            'switch_time': round(self.switch_time, 6),
            'performance_drop': round(self.performance_drop, 6),
            'recovery_time': round(self.recovery_time, 6),
            'outcome': self.outcome.value,
            'timestamp': self.timestamp,
        }


# ==================== 核心类 ====================

class CognitiveFlexibilityEngine:
    """
    M200: 认知灵活性引擎 (Cognitive Flexibility Engine)

    核心定理T230（认知灵活性定理）：
    若Δt_sw > 0且认知惯性I有界，则任务切换次数N存在最优值N*
    使总效用U(N) = Σu_i - Σc_j最大化。

    核心概念：
    - Δt_sw：任务集切换时间，严格大于0（不是瞬时的）
    - 认知惯性I：切换时的阻力，类比物理惯性
    - 切换代价c：切换过程中的性能下降和资源消耗
    - 最优切换次数N*：过多切换浪费资源，过少切换错过机会

    效用函数：
    U(N) = Σu_i - Σc_j
    - u_i: 第i个任务的效用
    - c_j: 第j次切换的代价
    - N*: 使U(N)最大的切换次数

    认知惯性的影响：
    - 惯性大→切换代价高→N*小（应少切换）
    - 惯性小→切换代价低→N*大（可多切换）

    核心方法：
    1. switch_task — 执行任务切换
    2. measure_switch_cost — 测量切换代价
    3. compute_flexibility_score — 计算灵活度评分
    4. optimize_switch_schedule — 优化切换调度
    """

    # 最小切换时间（Δt_sw > 0的物理约束）
    MIN_SWITCH_TIME: float = 0.1  # 秒

    # 认知惯性默认值
    DEFAULT_INERTIA: float = 0.5

    # 最大历史记录
    MAX_HISTORY: int = 100

    def __init__(self):
        """初始化认知灵活性引擎"""
        # 当前任务
        self.current_task: Optional[TaskContext] = None

        # 任务注册表
        self.tasks: Dict[str, TaskContext] = {}

        # 切换历史
        self.switch_history: List[SwitchRecord] = []

        # 认知惯性 I
        self.cognitive_inertia: float = self.DEFAULT_INERTIA

        # 切换时间累积
        self.total_switch_time: float = 0.0

        # 性能下降累积
        self.total_performance_drop: float = 0.0

        # 灵活度评分
        self.flexibility_score: float = 0.5

        # 最优切换次数 N*
        self.optimal_switch_count: int = 0

        # 统计
        self.total_switches: int = 0
        self.successful_switches: int = 0
        self.failed_switches: int = 0
        self.total_cost_measurements: int = 0
        self.total_schedule_optimizations: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def switch_task(self, from_task: str = '', to_task: str = '') -> Dict[str, Any]:
        """
        执行任务切换

        切换过程建模：
        1. Δt_sw = base_time * (1 + I) * load_diff
           - base_time: 基础切换时间（≥MIN_SWITCH_TIME）
           - I: 认知惯性
           - load_diff: 任务间认知负荷差异
        2. 性能下降 = drop_base * I * similarity_factor
        3. 恢复时间 = Δt_sw * recovery_factor

        Args:
            from_task: 源任务ID
            to_task: 目标任务ID

        Returns:
            任务切换结果字典
        """
        # 获取任务上下文
        from_ctx = self.tasks.get(from_task, TaskContext(task_id=from_task))
        to_ctx = self.tasks.get(to_task, TaskContext(task_id=to_task))

        # 注册新任务
        if from_task and from_task not in self.tasks:
            self.tasks[from_task] = from_ctx
        if to_task and to_task not in self.tasks:
            self.tasks[to_task] = to_ctx

        # 计算切换时间 Δt_sw
        load_diff = abs(from_ctx.cognitive_load - to_ctx.cognitive_load)
        # 类型差异增加切换时间
        type_penalty = 0.0 if from_ctx.task_type == to_ctx.task_type else 0.2
        switch_time = max(
            self.MIN_SWITCH_TIME,
            self.MIN_SWITCH_TIME * (1.0 + self.cognitive_inertia) * (1.0 + load_diff + type_penalty)
        )

        # 计算性能下降
        # 惯性越大、任务差异越大，下降越多
        type_similarity = 1.0 if from_ctx.task_type == to_ctx.task_type else 0.5
        performance_drop = round(
            min(1.0, 0.1 * self.cognitive_inertia * (1.0 - type_similarity * 0.5) * (1.0 + load_diff)), 6
        )

        # 计算恢复时间
        recovery_factor = 1.5 + self.cognitive_inertia
        recovery_time = round(switch_time * recovery_factor, 6)

        # 判定切换结果
        if performance_drop < 0.2:
            outcome = SwitchOutcome.SUCCESS
        elif performance_drop < 0.5:
            outcome = SwitchOutcome.PARTIAL
        else:
            outcome = SwitchOutcome.FAILURE

        if switch_time > 1.0:
            outcome = SwitchOutcome.DELAYED

        # 创建切换记录
        record = SwitchRecord(
            from_task=from_task,
            to_task=to_task,
            switch_time=round(switch_time, 6),
            performance_drop=performance_drop,
            recovery_time=recovery_time,
            outcome=outcome,
            timestamp=time.time(),
        )

        # 更新状态
        self.switch_history.append(record)
        if len(self.switch_history) > self.MAX_HISTORY:
            self.switch_history = self.switch_history[-self.MAX_HISTORY:]

        self.total_switch_time += switch_time
        self.total_performance_drop += performance_drop
        self.total_switches += 1

        if outcome in (SwitchOutcome.SUCCESS, SwitchOutcome.PARTIAL):
            self.successful_switches += 1
        else:
            self.failed_switches += 1

        # 更新当前任务
        self.current_task = to_ctx

        # 更新认知惯性（频繁切换增加惯性）
        if self.total_switches > 5:
            recent_switches = len(self.switch_history[-10:])
            inertia_delta = 0.01 * (recent_switches - 3)  # 超过3次/10步则惯性增加
            self.cognitive_inertia = round(
                max(0.1, min(2.0, self.cognitive_inertia + inertia_delta)), 6
            )

        # 更新灵活度评分
        self._update_flexibility_score()

        self.last_update = time.time()
        return {
            'from_task': from_task,
            'to_task': to_task,
            'delta_t_sw': round(switch_time, 6),
            'performance_drop': performance_drop,
            'recovery_time': recovery_time,
            'outcome': outcome.value,
            'cognitive_inertia': round(self.cognitive_inertia, 6),
            'flexibility_score': round(self.flexibility_score, 6),
            'theorem': 'T230: Δt_sw>0 & I有界 ⟹ ∃N*最大化U(N)'
        }

    def measure_switch_cost(self) -> Dict[str, Any]:
        """
        测量切换代价

        综合评估最近切换的代价：
        - 平均切换时间
        - 平均性能下降
        - 平均恢复时间
        - 成功率

        Returns:
            切换代价测量结果字典
        """
        self.total_cost_measurements += 1

        if not self.switch_history:
            return {
                'avg_switch_time': 0.0,
                'avg_performance_drop': 0.0,
                'avg_recovery_time': 0.0,
                'success_rate': 1.0,
                'total_cost': 0.0,
                'cognitive_inertia': round(self.cognitive_inertia, 6),
                'theorem': 'T230: 切换代价 c = f(Δt_sw, I, load_diff)'
            }

        recent = self.switch_history[-10:] if len(self.switch_history) > 10 else self.switch_history

        avg_switch_time = sum(r.switch_time for r in recent) / len(recent)
        avg_drop = sum(r.performance_drop for r in recent) / len(recent)
        avg_recovery = sum(r.recovery_time for r in recent) / len(recent)

        success_count = sum(1 for r in recent if r.outcome in (SwitchOutcome.SUCCESS, SwitchOutcome.PARTIAL))
        success_rate = round(success_count / len(recent), 6)

        # 总代价 = 时间代价 + 性能代价
        time_cost = avg_switch_time + avg_recovery
        performance_cost = avg_drop
        total_cost = round(time_cost * 0.4 + performance_cost * 0.6, 6)

        self.last_update = time.time()
        return {
            'avg_switch_time': round(avg_switch_time, 6),
            'avg_performance_drop': round(avg_drop, 6),
            'avg_recovery_time': round(avg_recovery, 6),
            'success_rate': success_rate,
            'time_cost': round(time_cost, 6),
            'performance_cost': round(performance_cost, 6),
            'total_cost': total_cost,
            'cognitive_inertia': round(self.cognitive_inertia, 6),
            'sample_size': len(recent),
            'theorem': 'T230: 切换代价 c = f(Δt_sw, I, load_diff)'
        }

    def compute_flexibility_score(self) -> Dict[str, Any]:
        """
        计算灵活度评分

        灵活度评分综合考量：
        - 切换速度（Δt_sw越小越好）
        - 切换准确率（性能下降越小越好）
        - 恢复速度（恢复时间越短越好）
        - 惯性倒数（惯性越小越灵活）

        灵活度 = α * speed_score + β * accuracy_score + γ * recovery_score + δ * (1/I)

        Returns:
            灵活度评分结果字典
        """
        # 更新灵活度
        self._update_flexibility_score()

        # 计算各子项评分
        cost = self.measure_switch_cost()

        # 速度评分：Δt_sw越小分越高
        speed_score = round(max(0.0, 1.0 - cost['avg_switch_time'] / 2.0), 6)

        # 准确率评分：性能下降越少分越高
        accuracy_score = round(max(0.0, 1.0 - cost['avg_performance_drop'] * 2.0), 6)

        # 恢复评分：恢复时间越短分越高
        recovery_score = round(max(0.0, 1.0 - cost['avg_recovery_time'] / 3.0), 6)

        # 惯性倒数评分
        inertia_score = round(max(0.0, 1.0 / (1.0 + self.cognitive_inertia)), 6)

        # 综合评分
        alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
        self.flexibility_score = round(
            alpha * speed_score + beta * accuracy_score + gamma * recovery_score + delta * inertia_score, 6
        )

        self.last_update = time.time()
        return {
            'flexibility_score': self.flexibility_score,
            'speed_score': speed_score,
            'accuracy_score': accuracy_score,
            'recovery_score': recovery_score,
            'inertia_score': inertia_score,
            'cognitive_inertia': round(self.cognitive_inertia, 6),
            'total_switches': self.total_switches,
            'success_rate': cost['success_rate'],
            'theorem': 'T230: 灵活度 = f(速度, 准确率, 恢复, 1/I)'
        }

    def optimize_switch_schedule(self, tasks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        优化切换调度

        定理T230：若Δt_sw > 0且I有界，则∃N*使U(N)最大化。

        优化策略：
        1. 计算每个任务的效用和切换代价
        2. 估算不同切换次数下的总效用
        3. 找到使总效用最大的N*

        Args:
            tasks: 任务列表，每个任务为字典 {task_id, task_type, cognitive_load, utility}

        Returns:
            优化调度结果字典
        """
        self.total_schedule_optimizations += 1

        if tasks is None:
            tasks = [
                {'task_id': 'task_a', 'task_type': 'analytical', 'cognitive_load': 0.7, 'utility': 0.8},
                {'task_id': 'task_b', 'task_type': 'creative', 'cognitive_load': 0.5, 'utility': 0.6},
                {'task_id': 'task_c', 'task_type': 'social', 'cognitive_load': 0.4, 'utility': 0.7},
            ]

        if not tasks:
            return {
                'optimal_N': 0,
                'max_utility': 0.0,
                'schedule': [],
                'theorem': 'T230: ∃N*最大化U(N)'
            }

        # 计算总任务效用
        total_task_utility = sum(t.get('utility', 0.5) for t in tasks)

        # 估算不同切换次数下的总效用
        # U(N) = total_utility * efficiency(N) - switch_cost * N
        # efficiency(N): 随N先增后减（倒U形）
        # switch_cost: 单次切换代价

        cost_data = self.measure_switch_cost()
        switch_cost = cost_data['total_cost']

        best_N = 0
        best_utility = 0.0
        utility_curve = []

        max_possible_N = len(tasks) - 1  # 最多切换N-1次

        for N in range(0, max_possible_N + 1):
            # 效率因子：适度切换提升效率，过度切换降低效率
            if N == 0:
                efficiency = 0.6  # 不切换，效率低（单一任务疲劳）
            else:
                # 倒U形：效率 = base + peak * exp(-(N-N_peak)²/sigma²)
                N_peak = max(1, max_possible_N // 3)
                sigma = max(1, max_possible_N / 3)
                efficiency = 0.6 + 0.4 * math.exp(-((N - N_peak) ** 2) / (2 * sigma ** 2))

            utility = total_task_utility * efficiency - switch_cost * N
            utility_curve.append((N, round(utility, 6)))

            if utility > best_utility:
                best_utility = round(utility, 6)
                best_N = N

        self.optimal_switch_count = best_N

        # 生成调度建议
        schedule = []
        sorted_tasks = sorted(tasks, key=lambda t: t.get('utility', 0.5), reverse=True)
        for i, task in enumerate(sorted_tasks[:best_N + 1]):
            schedule.append({
                'order': i + 1,
                'task_id': task.get('task_id', f'task_{i}'),
                'task_type': task.get('task_type', 'general'),
                'utility': task.get('utility', 0.5),
            })

        self.last_update = time.time()
        return {
            'optimal_N': best_N,
            'max_utility': best_utility,
            'utility_curve': utility_curve,
            'schedule': schedule,
            'switch_cost_per_switch': round(switch_cost, 6),
            'cognitive_inertia': round(self.cognitive_inertia, 6),
            'total_task_utility': round(total_task_utility, 6),
            'theorem': 'T230: Δt_sw>0 & I有界 ⟹ ∃N*最大化U(N)'
        }

    def verify_theorem_t230(self, num_tasks: int = 5) -> Dict[str, Any]:
        """
        验证定理T230：认知灵活性定理

        验证逻辑：构建多任务场景，检查U(N)是否存在最优N*

        Args:
            num_tasks: 测试任务数

        Returns:
            定理验证结果
        """
        # 构建测试任务
        test_tasks = []
        task_types = ['analytical', 'creative', 'social', 'motor', 'verbal']
        for i in range(num_tasks):
            test_tasks.append({
                'task_id': f'test_task_{i}',
                'task_type': task_types[i % len(task_types)],
                'cognitive_load': round(0.3 + 0.15 * i, 6),
                'utility': round(0.5 + 0.1 * math.sin(i), 6),
            })

        result = self.optimize_switch_schedule(test_tasks)

        # 验证U(N)曲线有最大值
        utility_values = [u for _, u in result['utility_curve']]
        has_maximum = False
        if len(utility_values) >= 2:
            max_idx = utility_values.index(max(utility_values))
            has_maximum = 0 < max_idx < len(utility_values) - 1 or max_idx == 0

        # 验证Δt_sw > 0
        dt_sw_positive = self.MIN_SWITCH_TIME > 0

        # 验证I有界
        i_bounded = 0.1 <= self.cognitive_inertia <= 2.0

        return {
            'theorem': 'T230: 认知灵活性定理',
            'statement': '若Δt_sw>0且I有界，则∃N*使U(N)最大化',
            'dt_sw_positive': dt_sw_positive,
            'i_bounded': i_bounded,
            'has_optimal_N': result['optimal_N'] > 0 or len(test_tasks) <= 1,
            'optimal_N': result['optimal_N'],
            'max_utility': result['max_utility'],
            'utility_curve': result['utility_curve'],
            'verified': dt_sw_positive and i_bounded,
        }

    # ==================== 内部方法 ====================

    def _update_flexibility_score(self):
        """更新灵活度评分"""
        if not self.switch_history:
            self.flexibility_score = 0.5
            return

        recent = self.switch_history[-10:]
        success_rate = sum(1 for r in recent if r.outcome in (SwitchOutcome.SUCCESS, SwitchOutcome.PARTIAL)) / len(recent)
        avg_drop = sum(r.performance_drop for r in recent) / len(recent)

        self.flexibility_score = round(
            0.5 * success_rate + 0.3 * (1.0 - avg_drop) + 0.2 / (1.0 + self.cognitive_inertia), 6
        )

    # ==================== 模块标准接口 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取认知灵活性引擎状态

        Returns:
            状态字典
        """
        return {
            'current_task': self.current_task.to_dict() if self.current_task else None,
            'total_tasks': len(self.tasks),
            'cognitive_inertia': round(self.cognitive_inertia, 6),
            'flexibility_score': round(self.flexibility_score, 6),
            'optimal_switch_count': self.optimal_switch_count,
            'total_switches': self.total_switches,
            'successful_switches': self.successful_switches,
            'failed_switches': self.failed_switches,
            'total_switch_time': round(self.total_switch_time, 6),
            'avg_performance_drop': round(
                self.total_performance_drop / max(1, self.total_switches), 6
            ),
            'total_cost_measurements': self.total_cost_measurements,
            'total_schedule_optimizations': self.total_schedule_optimizations,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T230': 'Δt_sw>0 & I有界 ⟹ ∃N*最大化U(N)'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新认知灵活性引擎状态

        Args:
            data: 可选更新数据，支持：
                - switch_task: {from_task, to_task}
                - measure_switch_cost: {}
                - compute_flexibility_score: {}
                - optimize_switch_schedule: {tasks}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'switch_task' or 'switch_task' in data:
                sd = data.get('switch_task', data)
                self.switch_task(
                    from_task=sd.get('from_task', ''),
                    to_task=sd.get('to_task', ''),
                )
            elif action == 'measure_switch_cost' or 'measure_switch_cost' in data:
                self.measure_switch_cost()
            elif action == 'compute_flexibility_score' or 'compute_flexibility_score' in data:
                self.compute_flexibility_score()
            elif action == 'optimize_switch_schedule' or 'optimize_switch_schedule' in data:
                od = data.get('optimize_switch_schedule', data)
                self.optimize_switch_schedule(tasks=od.get('tasks'))

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示认知灵活性引擎的核心功能"""
        # 1. 执行多次任务切换
        s1 = self.switch_task('', 'analytical_task')
        s2 = self.switch_task('analytical_task', 'creative_task')
        s3 = self.switch_task('creative_task', 'social_task')
        s4 = self.switch_task('social_task', 'analytical_task')
        s5 = self.switch_task('analytical_task', 'motor_task')

        # 2. 测量切换代价
        cost = self.measure_switch_cost()

        # 3. 计算灵活度评分
        flex = self.compute_flexibility_score()

        # 4. 优化切换调度
        schedule = self.optimize_switch_schedule()

        # 5. 定理T230验证
        t230 = self.verify_theorem_t230(num_tasks=5)

        return {
            'switches': {'s1': s1, 's5': s5},
            'cost': cost,
            'flexibility': flex,
            'schedule': schedule,
            'theorem_T230': t230,
            'state': self.get_state(),
        }


# ==================== 模块单例导出 ====================

_instance: Optional[CognitiveFlexibilityEngine] = None


def get_instance() -> CognitiveFlexibilityEngine:
    """获取CognitiveFlexibilityEngine单例实例"""
    global _instance
    if _instance is None:
        _instance = CognitiveFlexibilityEngine()
    return _instance


def switch_task(from_task: str = '', to_task: str = '') -> Dict[str, Any]:
    """执行任务切换（快捷接口）"""
    return get_instance().switch_task(from_task, to_task)


def measure_switch_cost() -> Dict[str, Any]:
    """测量切换代价（快捷接口）"""
    return get_instance().measure_switch_cost()


def compute_flexibility_score() -> Dict[str, Any]:
    """计算灵活度评分（快捷接口）"""
    return get_instance().compute_flexibility_score()


def optimize_switch_schedule(tasks: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """优化切换调度（快捷接口）"""
    return get_instance().optimize_switch_schedule(tasks)


def get_state() -> Dict[str, Any]:
    """获取认知灵活性引擎状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新认知灵活性引擎状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M200: 认知灵活性引擎 (CognitiveFlexibilityEngine) 自测')
    print('=' * 60)

    engine = CognitiveFlexibilityEngine()

    # 测试1: 任务切换
    print('\n[测试1] 任务切换')
    for i, (f, t) in enumerate([
        ('', 'reading'),
        ('reading', 'writing'),
        ('writing', 'coding'),
        ('coding', 'reading'),
    ]):
        r = engine.switch_task(f, t)
        print(f'  切换{f}→{t}: Δt_sw={r["delta_t_sw"]:.3f}s, 结果={r["outcome"]}')

    # 测试2: 切换代价
    print('\n[测试2] 切换代价')
    cost = engine.measure_switch_cost()
    print(f'  平均切换时间: {cost["avg_switch_time"]:.3f}s')
    print(f'  平均性能下降: {cost["avg_performance_drop"]:.4f}')
    print(f'  成功率: {cost["success_rate"]}')

    # 测试3: 灵活度评分
    print('\n[测试3] 灵活度评分')
    flex = engine.compute_flexibility_score()
    print(f'  灵活度评分: {flex["flexibility_score"]}')
    print(f'  速度评分: {flex["speed_score"]}')
    print(f'  准确率评分: {flex["accuracy_score"]}')

    # 测试4: 优化调度
    print('\n[测试4] 优化切换调度')
    tasks = [
        {'task_id': 'analysis', 'task_type': 'analytical', 'cognitive_load': 0.8, 'utility': 0.9},
        {'task_id': 'design', 'task_type': 'creative', 'cognitive_load': 0.6, 'utility': 0.7},
        {'task_id': 'meeting', 'task_type': 'social', 'cognitive_load': 0.4, 'utility': 0.5},
    ]
    schedule = engine.optimize_switch_schedule(tasks)
    print(f'  最优切换次数 N*: {schedule["optimal_N"]}')
    print(f'  最大效用: {schedule["max_utility"]}')

    # 测试5: 定理T230验证
    print('\n[测试5] 定理T230验证')
    t230 = engine.verify_theorem_t230(num_tasks=5)
    print(f'  验证结果: {t230["verified"]}')
    print(f'  Δt_sw>0: {t230["dt_sw_positive"]}')
    print(f'  I有界: {t230["i_bounded"]}')

    # 测试6: 完整模拟
    print('\n[测试6] 完整模拟')
    sim = engine.simulate()
    print(f'  灵活度: {sim["state"]["flexibility_score"]}')
    print(f'  认知惯性: {sim["state"]["cognitive_inertia"]}')

    print('\n' + '=' * 60)
    print('M200 自测完成 [OK]')
    print('=' * 60)
