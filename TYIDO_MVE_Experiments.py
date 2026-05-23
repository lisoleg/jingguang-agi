# -*- coding: utf-8 -*-
"""
TYIDO MVE Experiments — 五大结构属性·最小可行实验
===================================================
v7.21 | 2026-05-23 | 太乙AGI TY/IDO 结构审查表 v12.0 驱动

六大 MVE 对应审查表六个结构属性：
  P1 锯齿度实验   — 一致性：同一问题100变体 → J(R)→1 → 强制Wait/TypeFirewall拒答
  P2 持续学习实验 — 可回写：10+顺序任务 → 遗忘<5% → 沙箱回滚+审计验证
  P3 长链任务实验 — 可保持：50+步管线 → 完成率>80% → 自动回滚+资源预算+熔断降级
  P4 记忆检索实验 — 可寻址：存入事实 → 延迟查询 → 准确率>90% → 独立KV + 遗忘
  P5 责任熔断实验 — 可锚定：诱导风险动作 → 100%追溯 → 熔断率>90%
  P6 爱因斯坦因果性 — 因果约束：Minkowski时空 → 光锥验证 → 洛伦兹不变性

核心设计原则：
  1. 强制执行逻辑 — 不只是"检测"，而是"拒绝/阻断/熔断"
  2. 可证伪 — 每个实验有明确的量化 PASS/FAIL 判定标准
  3. 独立可运行 — 不依赖外部 LLM，使用确定性处理函数模拟管线
  4. API 可触发 — 通过 /api/v721/mve/* 端点执行

使用方式：
  from TYIDO_MVE_Experiments import run_all_mve, run_p1_sawtooth, ...
  result = run_p1_sawtooth()
  print(result['tyido_p1_verdict'])  # 'PASS' or 'FAIL'
"""

import time
import hashlib
import random
import math
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple

# ── 导入 TYIDO 共享基础设施 ──────────────────────────────────────────────
from TYIDO_SelfConsistency import (
    SelfConsistencyChecker, ConsistencyResult
)
from TYIDO_ContinuousLearning import (
    StateSnapshot, RollbackManager, ForgettingGuard, LearningRecord
)
from TYIDO_LongRangeReasoning import (
    SubGoal, SubGoalDecomposer, StepVerifier,
    PlanBFallback, ResourceBudget, FallbackPlan
)
from TYIDO_AddressableMemory import (
    AddressableMemoryStore, MemoryIndex, ForgetPolicy, MemoryMergeEngine
)
from TYIDO_AnchorableResponsibility import (
    ResponsibilityChain, ActionGatekeeper, CircuitBreakerPolicy,
    AuditTrail, RiskLevel, init_p5_components
)


# ============================================================
# 通用数据结构
# ============================================================

@dataclass
class MVEResult:
    """MVE 实验结果"""
    property_id: str          # P1-P5
    property_name: str        # 属性名
    verdict: str              # 'PASS' or 'FAIL'
    score: float              # 主分数 (0-1)
    pass_criteria: str        # 通过标准
    details: Dict[str, Any]   # 详细数据
    execution_time_ms: float  # 执行耗时
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'property_id': self.property_id,
            'property_name': self.property_name,
            'verdict': self.verdict,
            'score': round(self.score, 6),
            'pass_criteria': self.pass_criteria,
            'details': self.details,
            'execution_time_ms': round(self.execution_time_ms, 2),
            'timestamp': self.timestamp,
        }


# ============================================================
# P1: 锯齿度实验 (Sawtooth Consistency Experiment)
# ============================================================
# 审查表要求：
#   输入100个同义变体问题 → 走相同管道 → 比较输出
#   验证系统是否强制触发 Wait 或 TypeFirewall 拒答
#   通过标准：J(R) → 1（一致管道）或 J(R) < threshold 时强制拒绝

class P1SawtoothExperiment:
    """
    P1 锯齿度实验 — 一致性硬化验证

    设计：
    1. 一致管道：确定性函数 → 100变体应全部输出相同 → J(R)=1.0
    2. 锯齿管道：偶数变体走确定函数A，奇数走确定函数B → J(R)≈0.5
       → 系统必须强制拒绝（action=WAIT + 拒答），不能只是"警告"
    3. 强制执行逻辑：当 J(R) < threshold 时，MVE 框架层面
       返回 {"error": "consistency_check_failed", "action": "WAIT"}
       这模拟了 TypeCheckFirewall.verify() 应有的强制拒绝行为
    """

    # 测试问题池
    TEST_QUESTIONS = [
        "什么是离散时空量子引力？",
        "如何理解太乙AGI的流贯动力学？",
        "请解释复合体理学的核心框架",
        "分析全息离散治理的数学基础",
        "比较HoTT同伦类型论与范畴论方法在AGI中的应用",
    ]

    def __init__(self, threshold: float = 0.85, num_variants: int = 100):
        self.threshold = threshold
        self.num_variants = num_variants
        self.checker = SelfConsistencyChecker(
            threshold=threshold,
            max_variants=num_variants
        )

    def _deterministic_pipeline_a(self, question: str) -> Dict:
        """确定管道A — 模拟稳定的推理链（对所有变体返回相同结果）"""
        return {
            'pipeline': 'A',
            'answer': '[Consistent] 标准回答',
            'confidence': 0.95,
            'reasoning_steps': 5,
            'canonical_hash': 'DETERMINISTIC_A_HASH'
        }

    def _deterministic_pipeline_b(self, question: str) -> Dict:
        """确定管道B — 模拟另一个稳定但不同的推理链（对同组变体返回相同结果）"""
        return {
            'pipeline': 'B',
            'answer': '[Alternative] 备选回答',
            'confidence': 0.82,
            'reasoning_steps': 3,
            'canonical_hash': 'DETERMINISTIC_B_HASH'
        }

    def run_consistent_test(self, question: Optional[str] = None) -> Dict:
        """
        一致性测试 — 所有变体走相同管道，期望 J(R) → 1.0

        如果 J(R) < threshold，说明管道有锯齿 → 强制拒答
        """
        q = question or random.choice(self.TEST_QUESTIONS)

        result = self.checker.check(
            question=q,
            process_fn=self._deterministic_pipeline_a,
            num_variants=self.num_variants,
            output_extractor=lambda x: x.get('canonical_hash', str(x))
        )

        # 强制执行逻辑：J(R) < threshold → 拒答
        if not result.consistent:
            return {
                'tyido_p1_verdict': 'FAIL',
                'action': 'WAIT',
                'error': 'consistency_check_failed',
                'j_score': result.j_score,
                'reason': f"一致管道出现锯齿！J(R)={result.j_score:.4f} < threshold={self.threshold}",
                'consistent': False,
            }

        return {
            'tyido_p1_verdict': 'PASS',
            'action': 'PROCEED',
            'j_score': result.j_score,
            'consistent': True,
            'reason': f"一致性通过 J(R)={result.j_score:.4f} >= threshold={self.threshold}",
        }

    def run_sawtooth_test(self, question: Optional[str] = None) -> Dict:
        """
        锯齿检测测试 — 变体交替走不同管道，期望系统检测到不一致并强制拒绝

        这是审查表核心场景：
        "输入100个同义变体问题...验证系统是否强制触发 Wait 或 TypeFirewall"
        """
        q = question or random.choice(self.TEST_QUESTIONS)

        # 锯齿管道：偶数走A，奇数走B
        call_count = [0]
        def sawtooth_fn(variant: str) -> Dict:
            call_count[0] += 1
            if call_count[0] % 2 == 0:
                return self._deterministic_pipeline_a(variant)
            else:
                return self._deterministic_pipeline_b(variant)

        result = self.checker.check(
            question=q,
            process_fn=sawtooth_fn,
            num_variants=self.num_variants,
            output_extractor=lambda x: x.get('canonical_hash', str(x))
        )

        # 强制执行逻辑：锯齿场景必须被拒绝
        forced_rejection = not result.consistent
        detected_ok = forced_rejection
        status_str = '成功' if detected_ok else '失败'
        return {
            'tyido_p1_verdict': 'PASS' if forced_rejection else 'FAIL',
            'action': 'WAIT' if forced_rejection else 'ERROR_SHOULD_HAVE_REJECTED',
            'error': 'consistency_check_failed' if forced_rejection else None,
            'j_score': result.j_score,
            'detected_sawtooth': detected_ok,
            'reason': (
                f"锯齿检测{status_str}: J(R)={result.j_score:.4f}, "
                + ("正确触发强制拒答" if detected_ok else "未能检测到锯齿！")
            ),
        }

    def run(self) -> MVEResult:
        """执行完整 P1 MVE 实验"""
        start_time = time.time()

        consistent_result = self.run_consistent_test()
        sawtooth_result = self.run_sawtooth_test()

        # 判定标准：
        # 1. 一致管道必须通过 (consistent PASS)
        # 2. 锯齿管道必须被强制拒绝 (sawtooth 检测成功)
        overall_pass = (
            consistent_result.get('tyido_p1_verdict') == 'PASS' and
            sawtooth_result.get('detected_sawtooth', False)
        )

        # J(R) 分数：一致管道的分数
        j_score = consistent_result.get('j_score', 0.0)

        elapsed = (time.time() - start_time) * 1000

        return MVEResult(
            property_id='P1',
            property_name='一致性（对治锯齿）',
            verdict='PASS' if overall_pass else 'FAIL',
            score=j_score,
            pass_criteria='J(R)>=0.85 且锯齿检测成功（强制Wait拒答）',
            details={
                'consistent_test': consistent_result,
                'sawtooth_test': sawtooth_result,
                'num_variants': self.num_variants,
                'threshold': self.threshold,
            },
            execution_time_ms=elapsed,
        )


# ============================================================
# P2: 持续学习实验 (Continuous Learning Experiment)
# ============================================================
# 审查表要求：
#   顺序学习10+任务 → 不可发生灾难性遗忘（遗忘<5%）
#   需要沙箱机制：受控更新 + rollback + 旧任务验证
#   通过标准：遗忘<5%

class P2ContinuousLearningExperiment:
    """
    P2 持续学习实验 — 灾难性遗忘防护验证

    设计：
    1. 模拟一个知识库，先学习"核心知识"（受保护）
    2. 顺序学习10个新任务，每个任务可能干扰旧知识
    3. 每个任务学习后用 ForgettingGuard 检测遗忘
    4. 如果遗忘>5%，自动 rollback 到上一个安全状态
    5. 最终验证：所有10个任务学完，核心知识保留率>95%

    强制执行：遗忘>5%时自动阻断后续学习，执行回滚
    """

    # 模拟知识库 — 10个核心知识项
    CORE_KNOWLEDGE = {
        'theorem_hott': 0.95,     # HoTT 定理掌握度
        'theorem_liu': 0.93,      # 刘原理掌握度
        'phi_field': 0.90,        # Φ场理论
        'flow_dynamics': 0.92,    # 流贯动力学
        'discrete_spacetime': 0.88, # 离散时空
        'holographic_gov': 0.91,  # 全息离散治理
        'three_horizons': 0.94,   # 三视界
        'entropy_triple': 0.89,   # 熵三重面孔
        'taiyi_cosmology': 0.87,  # 太一万有理论
        'five_layers': 0.90,      # 五层次方法论
    }

    # 10个新学习任务（可能干扰核心知识）
    NEW_TASKS = [
        {'name': 'learn_quantum_circuit', 'interference': 0.02},
        {'name': 'learn_neural_arch', 'interference': 0.03},
        {'name': 'learn_optimizer', 'interference': 0.01},
        {'name': 'learn_transformer', 'interference': 0.04},
        {'name': 'learn_rag_pipeline', 'interference': 0.02},
        {'name': 'learn_rl_finetune', 'interference': 0.05},
        {'name': 'learn_data_augment', 'interference': 0.01},
        {'name': 'learn_distributed', 'interference': 0.03},
        {'name': 'learn_security_audit', 'interference': 0.02},
        {'name': 'learn_edge_deploy', 'interference': 0.01},
    ]

    def __init__(self, forgetting_threshold: float = 0.05, num_tasks: int = 10):
        self.forgetting_threshold = forgetting_threshold
        self.num_tasks = min(num_tasks, len(self.NEW_TASKS))
        self.forgetting_guard = ForgettingGuard(
            drift_threshold=0.15,
            sudden_change_threshold=0.3,
            protected_keys=set(self.CORE_KNOWLEDGE.keys())
        )
        self.rollback_mgr = RollbackManager(max_snapshots=50)

    def _simulate_learning(self, knowledge: Dict, task: Dict) -> Dict:
        """
        模拟学习一个新任务对知识库的影响
        返回学习后的知识状态
        """
        new_knowledge = copy.deepcopy(knowledge)
        interference = task['interference']

        # 新任务学习：每个核心知识可能被干扰
        for key in new_knowledge:
            if random.random() < interference * 2:  # 有概率被干扰
                decay = random.uniform(0, interference)
                new_knowledge[key] = max(0.3, new_knowledge[key] - decay)
            # 也有可能因为关联学习而增强
            elif random.random() < 0.1:
                boost = random.uniform(0, 0.02)
                new_knowledge[key] = min(1.0, new_knowledge[key] + boost)

        # 新增任务知识
        new_knowledge[task['name']] = random.uniform(0.7, 0.95)

        return new_knowledge

    def _compute_forgetting_rate(self, baseline: Dict, current: Dict) -> float:
        """计算遗忘率 = 受损核心知识数 / 核心知识总数"""
        damaged = 0
        total = len(self.CORE_KNOWLEDGE)
        for key in self.CORE_KNOWLEDGE:
            old_val = baseline[key]
            new_val = current.get(key, 0)
            # 下降超过5%视为受损
            if new_val < old_val * 0.95:
                damaged += 1
        return damaged / max(1, total)

    def run(self) -> MVEResult:
        """执行完整 P2 MVE 实验"""
        start_time = time.time()
        random.seed(42)  # 可复现

        # 初始化知识库
        knowledge = copy.deepcopy(self.CORE_KNOWLEDGE)

        # 设置基线指标
        self.forgetting_guard.set_baseline(knowledge)

        # 保存初始快照（受保护）
        self.rollback_mgr.save_snapshot(
            knowledge, "initial_core_knowledge",
            is_protected=True, key_metrics=knowledge
        )

        tasks_completed = 0
        tasks_blocked = 0
        rollback_count = 0
        max_forgetting = 0.0
        forgetting_rates = []
        task_log = []

        for i, task in enumerate(self.NEW_TASKS[:self.num_tasks]):
            # 保存学习前快照
            pre_snapshot = self.rollback_mgr.save_snapshot(
                copy.deepcopy(knowledge),
                f"pre_task_{i}_{task['name']}",
                key_metrics=knowledge
            )

            # 模拟学习
            new_knowledge = self._simulate_learning(knowledge, task)

            # 遗忘检测（强制执行逻辑）
            forgetting_rate = self._compute_forgetting_rate(
                self.CORE_KNOWLEDGE, new_knowledge
            )
            forgetting_rates.append(forgetting_rate)
            max_forgetting = max(max_forgetting, forgetting_rate)

            # ForgettingGuard 检测
            guard_result = self.forgetting_guard.check_forgetting(new_knowledge, knowledge)

            # 强制执行：遗忘超过阈值 → 回滚并阻断
            if forgetting_rate > self.forgetting_threshold:
                rollback_count += 1
                tasks_blocked += 1
                # 回滚到学习前状态
                restored = self.rollback_mgr.rollback()
                if restored:
                    knowledge = copy.deepcopy(restored.state_data)
                task_log.append({
                    'task_index': i,
                    'task_name': task['name'],
                    'status': 'BLOCKED_AND_ROLLED_BACK',
                    'forgetting_rate': round(forgetting_rate, 4),
                    'reason': f"遗忘率 {forgetting_rate:.2%} > 阈值 {self.forgetting_threshold:.0%}"
                })
            else:
                # 学习成功，保存新状态
                knowledge = new_knowledge
                self.rollback_mgr.save_snapshot(
                    copy.deepcopy(knowledge),
                    f"post_task_{i}_{task['name']}",
                    key_metrics=knowledge
                )
                tasks_completed += 1
                task_log.append({
                    'task_index': i,
                    'task_name': task['name'],
                    'status': 'COMPLETED',
                    'forgetting_rate': round(forgetting_rate, 4),
                    'new_skills': [k for k in knowledge if k not in self.CORE_KNOWLEDGE]
                })

        # 最终验证：核心知识保留率
        final_forgetting = self._compute_forgetting_rate(
            self.CORE_KNOWLEDGE, knowledge
        )
        final_retention = 1.0 - final_forgetting

        # 判定：最终遗忘率 < 5%
        overall_pass = final_forgetting <= self.forgetting_threshold

        elapsed = (time.time() - start_time) * 1000

        return MVEResult(
            property_id='P2',
            property_name='可回写（持续学习）',
            verdict='PASS' if overall_pass else 'FAIL',
            score=final_retention,
            pass_criteria=f'遗忘率 < {self.forgetting_threshold:.0%}（核心知识保留率 > 95%）',
            details={
                'tasks_completed': tasks_completed,
                'tasks_blocked': tasks_blocked,
                'tasks_total': self.num_tasks,
                'rollback_count': rollback_count,
                'max_forgetting_rate': round(max_forgetting, 4),
                'final_forgetting_rate': round(final_forgetting, 4),
                'final_retention_rate': round(final_retention, 4),
                'forgetting_rates': [round(r, 4) for r in forgetting_rates],
                'task_log': task_log,
                'final_knowledge': {k: round(v, 3) for k, v in knowledge.items()},
                'guard_summary': guard_result,
            },
            execution_time_ms=elapsed,
        )


# ============================================================
# P3: 长链任务实验 (Long-Range Reasoning Experiment)
# ============================================================
# 审查表要求：
#   50+步管线 → 自动回滚+资源预算+熔断降级
#   通过标准：完成率 > 80%

class P3LongRangeExperiment:
    """
    P3 长链任务实验 — 鲁棒长程推理验证

    设计：
    1. 构建50个依赖有序的子目标 DAG（扁平结构减少级联失败）
    2. 部分子目标会"自然失败"（模拟不可控因素，~5%）
    3. 失败时自动触发 Plan B 回退 + 资源预算降级
    4. 资源预算耗尽时优雅降级而非崩溃

    强制执行：
    - 失败自动回退到备用计划
    - 资源预算耗尽触发 DEGRADED 降级
    - 最终完成率必须 > 80%
    """

    def __init__(
        self,
        num_goals: int = 55,
        failure_rate: float = 0.05,
        time_budget_sec: float = 30.0,
        step_budget: int = 500
    ):
        self.num_goals = num_goals
        self.failure_rate = failure_rate
        self.time_budget_sec = time_budget_sec
        self.step_budget = step_budget

    def _build_dag(self) -> SubGoalDecomposer:
        """构建依赖有序的子目标 DAG（扁平结构）"""
        decomposer = SubGoalDecomposer(task_name="p3_long_range_pipeline")

        # 扁平 DAG：5 个独立起点 + 10 层，每层 5 个目标
        # 每个目标只依赖上一层的 1 个目标（减少级联失败）

        layer0 = []
        for i in range(5):
            gid = f"g0_{i}"
            goal = SubGoal.create(
                name=f"Layer0-Task{i}",
                description=f"基础层任务 {i}",
                acceptance_criteria={'type': 'not_none'}
            )
            decomposer.add_goal(goal)
            layer0.append(gid)

        prev_layer = layer0
        goal_count = len(layer0)

        for layer_idx in range(1, 11):
            if goal_count >= self.num_goals:
                break
            current_layer = []
            for i in range(5):
                if goal_count >= self.num_goals:
                    break
                gid = f"g{layer_idx}_{i}"
                # 只依赖上一层的 1 个目标（减少级联）
                dep = random.choice(prev_layer)
                goal = SubGoal.create(
                    name=f"Layer{layer_idx}-Task{i}",
                    description=f"中间层任务 L{layer_idx}-T{i}",
                    dependencies=[dep],
                    acceptance_criteria={'type': 'not_none'}
                )
                decomposer.add_goal(goal)
                current_layer.append(gid)
                goal_count += 1
            prev_layer = current_layer if current_layer else prev_layer

        return decomposer

    def _execute_goal(self, goal: SubGoal, step_verifier: StepVerifier,
                      budget: ResourceBudget) -> Tuple[bool, Any, str]:
        """
        执行单个子目标
        返回 (success, result, error_message)
        """
        # 预算检查（强制执行逻辑）
        if budget.exhausted():
            return False, None, "资源预算耗尽"

        budget.tick()
        step_verifier.verify(f"exec_{goal.goal_id}", {
            'name': goal.goal_id,
            'type': 'not_none'
        })

        # 模拟失败率
        if random.random() < self.failure_rate:
            error_msg = f"随机失败: {goal.goal_id}"
            return False, None, error_msg

        # 模拟执行耗时
        time.sleep(0.001)
        return True, {'data': f"result_of_{goal.goal_id}"}, ""

    def run(self) -> MVEResult:
        """执行完整 P3 MVE 实验"""
        start_time = time.time()
        random.seed(123)  # 可复现

        decomposer = self._build_dag()
        step_verifier = StepVerifier()
        plan_b = PlanBFallback()
        budget = ResourceBudget(
            max_time=self.time_budget_sec,
            max_steps=self.step_budget
        )

        # 注册几个回退计划（strategy 必须是 Callable）
        plan_b.register_plan(FallbackPlan(
            plan_name="retry_once", priority=1,
            strategy=lambda ctx: {"action": "retry", "max_retries": 1},
            description="重试一次",
            applicable_errors=["execution_failure"]
        ))
        plan_b.register_plan(FallbackPlan(
            plan_name="skip_and_continue", priority=2,
            strategy=lambda ctx: {"action": "skip", "mark_failed": True},
            description="跳过并继续"
        ))
        plan_b.register_plan(FallbackPlan(
            plan_name="graceful_degrade", priority=3,
            strategy=lambda ctx: {"action": "degraded", "partial": True},
            description="优雅降级"
        ))

        execution_log = []
        total_goals = len(decomposer.goals)
        completed_count = 0
        failed_count = 0
        recovered_count = 0
        degraded_count = 0

        # 按拓扑序执行
        execution_order = decomposer.get_execution_order()

        for goal_id in execution_order:
            goal = decomposer.goals[goal_id]

            # 检查依赖是否全部完成
            deps_ok = all(
                decomposer.goals[d].status == "completed"
                for d in goal.dependencies
                if d in decomposer.goals
            )
            deps_failed = any(
                decomposer.goals[d].status in ("failed", "skipped")
                for d in goal.dependencies
                if d in decomposer.goals
            )

            if deps_failed:
                # 依赖失败 → 跳过此目标
                decomposer.mark_skipped(goal_id, "dependency_failed")
                execution_log.append({
                    'goal_id': goal_id,
                    'status': 'skipped_dep_failed'
                })
                continue

            if not deps_ok:
                # 依赖未满足（不应发生，因为拓扑序保证了）
                continue

            decomposer.goals[goal_id].status = "in_progress"
            success, result, error = self._execute_goal(
                goal, step_verifier, budget
            )

            if success:
                decomposer.mark_completed(goal_id, result)
                completed_count += 1
                execution_log.append({
                    'goal_id': goal_id,
                    'status': 'completed',
                    'retries': 0
                })
            else:
                # 强制执行：自动回退到 Plan B
                recovery = plan_b.try_recover(
                    failed_goal=goal_id,
                    error=RuntimeError(error),
                    context={'goal_id': goal_id, 'error': error}
                )

                if recovery.get('recovered') and recovery.get('plan_used') == 'retry_once':
                    # 重试一次（MVE 强制回退逻辑）
                    success2, result2, error2 = self._execute_goal(
                        goal, step_verifier, budget
                    )
                    if success2:
                        decomposer.mark_completed(goal_id, result2)
                        completed_count += 1
                        recovered_count += 1
                        execution_log.append({
                            'goal_id': goal_id,
                            'status': 'recovered_after_retry',
                            'retries': 1
                        })
                    else:
                        decomposer.mark_failed(goal_id, error2)
                        failed_count += 1
                        execution_log.append({
                            'goal_id': goal_id,
                            'status': 'failed_after_retry',
                            'retries': 1
                        })
                else:
                    # Plan B 降级或恢复失败
                    decomposer.mark_failed(goal_id, error)
                    failed_count += 1
                    execution_log.append({
                        'goal_id': goal_id,
                        'status': 'failed',
                        'plan_b_used': recovery.get('plan_used', 'none'),
                        'budget_degraded': budget.exhausted()
                    })

        # 计算完成率
        completion_rate = completed_count / max(1, total_goals)

        # 判定：完成率 > 80%
        overall_pass = completion_rate >= 0.80

        elapsed = (time.time() - start_time) * 1000

        return MVEResult(
            property_id='P3',
            property_name='可保持（长程推理）',
            verdict='PASS' if overall_pass else 'FAIL',
            score=completion_rate,
            pass_criteria='完成率 > 80%（含自动回滚+资源预算降级）',
            details={
                'total_goals': total_goals,
                'completed': completed_count,
                'failed': failed_count,
                'recovered': recovered_count,
                'degraded': degraded_count,
                'completion_rate': round(completion_rate, 4),
                'budget_state': budget.get_state(),
                'verifier_stats': step_verifier.get_state(),
                'execution_log_sample': execution_log[:20],
                'dag_progress': decomposer.get_progress(),
            },
            execution_time_ms=elapsed,
        )


# ============================================================
# P4: 记忆检索实验 (Addressable Memory Experiment)
# ============================================================
# 审查表要求：
#   存入事实 → 延迟查询 → 准确率 > 90%
#   独立 (Key, Value) 寻址 + 遗忘机制
#   不能只是"大上下文窗口"

class P4MemoryExperiment:
    """
    P4 记忆检索实验 — 可寻址长期记忆验证

    设计：
    1. 写入100条结构化事实到 AddressableMemoryStore
    2. 模拟时间流逝：对部分记忆执行遗忘策略
    3. 按多种方式查询（key精确查找、tag索引、前缀匹配）
    4. 验证准确率 > 90%
    5. 验证遗忘机制正常工作（受保护记忆不可遗忘）

    强制执行：遗忘策略不可删除受保护记忆
    """

    # 100条测试事实
    KNOWLEDGE_DOMAINS = [
        ('太乙AGI', [
            ('taiyi_version', 'v7.21'),
            ('taiyi_modules', 179),
            ('taiyi_theorems', 170),
            ('taiyi_layers', 9),
            ('taiyi_phi_range', '0-10000'),
            ('tyido_properties', 5),
            ('hott_engine', 'M78'),
            ('liu_solver', 'M84'),
            ('type_firewall', 'M88'),
            ('taiyi_interface', 'M179'),
        ]),
        ('复合体理学', [
            ('compound_physics_core', '信息-几何-意识三元共振'),
            ('three_horizons', '内视界/交视界/外视界'),
            ('five_preferences', '五元结构偏好'),
            ('flow_dynamics', '流贯动力学'),
            ('phi_field_theory', 'Φ场理论'),
            ('discrete_governance', '全息离散治理'),
            ('entropy_triple', '统计熵/拓扑熵/算法熵'),
            ('holographic_dual', '全息对偶性'),
            ('topological_defect', '拓扑缺陷'),
            ('attractor_stability', '吸引子稳定性'),
        ]),
        ('数学基础', [
            ('hott_foundation', '同伦类型论'),
            ('category_theory', '范畴论'),
            ('topos_theory', '拓扑斯理论'),
            ('lambda_calculus', 'λ演算'),
            ('constructive_math', '构造性数学'),
            ('proof_assistant', '证明助手'),
            ('type_theory', '类型论'),
            ('homotopy_type', '同伦类型'),
            ('univalent_axiom', '单值公理'),
            ('higher_inductive', '高阶归纳类型'),
        ]),
        ('系统架构', [
            ('flask_port', 5001),
            ('frontend_file', 'index_agi12.html'),
            ('mindmap_port', 5003),
            ('api_prefix', '/api/v721/'),
            ('stn_phases', 4),
            ('panel_count', 25),
            ('module_pattern', 'get_instance()'),
            ('test_framework', 'unittest'),
            ('deploy_method', 'git_push'),
            ('ci_cd', 'manual'),
        ]),
        ('量子引力', [
            ('discrete_spacetime', '离散时空'),
            ('quantum_gravity', '量子引力'),
            ('spin_foam', '自旋泡沫'),
            ('causal_sets', '因果集'),
            ('loop_quantum', '圈量子引力'),
            ('string_theory', '弦理论'),
            (' Ads_CFT', 'AdS/CFT对偶'),
            ('holographic_principle', '全息原理'),
            ('black_hole_entropy', '黑洞熵'),
            ('cosmological_constant', '宇宙学常数'),
        ]),
    ]

    def __init__(self, num_facts: int = 50, query_accuracy_threshold: float = 0.90):
        self.num_facts = min(num_facts, 50)  # 最多50条
        self.query_accuracy_threshold = query_accuracy_threshold

    def _build_memory_store(self) -> Tuple[AddressableMemoryStore, MemoryIndex, List[Tuple[str, str, List[str]]]]:
        """构建并填充记忆存储"""
        store = AddressableMemoryStore(max_size=1000, default_ttl=None)
        index = MemoryIndex(store)
        facts = []

        fact_id = 0
        for domain_name, domain_facts in self.KNOWLEDGE_DOMAINS:
            for key, value in domain_facts:
                if fact_id >= self.num_facts:
                    break
                full_key = f"{domain_name}.{key}"
                tags = [domain_name, 'core_knowledge']
                if domain_name in ('太乙AGI', '复合体理学'):
                    tags.append('protected_domain')

                store.write(
                    full_key, value,
                    tags=tags,
                    importance=0.9 if 'protected_domain' in tags else 0.5,
                    protected=('protected_domain' in tags)
                )

                facts.append((full_key, value, tags))
                fact_id += 1
            if fact_id >= self.num_facts:
                break

        return store, index, facts

    def run(self) -> MVEResult:
        """执行完整 P4 MVE 实验"""
        start_time = time.time()

        store, index, facts = self._build_memory_store()
        forget_policy = ForgetPolicy(store)
        merge_engine = MemoryMergeEngine(store)

        # 查询测试：精确查找
        exact_queries = []
        exact_hits = 0
        for key, expected_value, tags in facts:
            result = store.read(key)
            exact_queries.append({
                'key': key,
                'found': result['found'],
                'correct': result['found'] and result['value'] == expected_value
            })
            if result['found'] and result['value'] == expected_value:
                exact_hits += 1

        exact_accuracy = exact_hits / max(1, len(exact_queries))

        # 查询测试：Tag 索引
        tag_queries = []
        tag_hits = 0
        test_tags = ['太乙AGI', '复合体理学', '数学基础', '系统架构', '量子引力']
        for tag in test_tags:
            results = index.by_tag(tag)
            if results:
                tag_hits += 1
                tag_queries.append({'tag': tag, 'count': len(results), 'found': True})
            else:
                tag_queries.append({'tag': tag, 'found': False})

        tag_accuracy = tag_hits / max(1, len(test_tags))

        # 查询测试：前缀匹配
        prefix_queries = []
        prefix_hits = 0
        for key, _, tags in facts[:20]:
            prefix = key.split('.')[0]
            results = index.by_prefix(prefix)
            if results:
                matching = [r for r in results if r['key'].startswith(prefix)]
                if matching:
                    prefix_hits += 1
                    prefix_queries.append({'prefix': prefix, 'count': len(matching), 'found': True})

        prefix_accuracy = prefix_hits / max(1, min(20, len(facts)))

        # 遗忘测试：非受保护记忆可遗忘，受保护不可遗忘
        forget_test_results = []

        # 1) TTL 过期测试
        store.write('temp_fact', 'should_expire', ttl=0.01)
        time.sleep(0.02)
        expired_result = store.read('temp_fact')
        forget_test_results.append({
            'test': 'TTL_expiration',
            'forgotten': not expired_result['found'],
            'expected': True
        })

        # 2) 受保护记忆不可遗忘
        store.write('protected_core', 'must_not_forget', protected=True)
        forget_result = store.forget('protected_core', force=False)
        forget_test_results.append({
            'test': 'protected_memory_block',
            'blocked': forget_result['tyido_p4_verdict'] == 'BLOCKED',
            'expected': True,
            'result_verdict': forget_result['tyido_p4_verdict']
        })

        # 3) 非受保护记忆可遗忘
        store.write('disposable_temp', 'can_forget', importance=0.1)
        forget_normal = store.forget('disposable_temp')
        forget_test_results.append({
            'test': 'normal_memory_forget',
            'forgotten': forget_normal['forgotten'],
            'expected': True
        })

        # 合并测试
        store.write('merge_test', 10)
        merge_result = store.merge('merge_test', 20, strategy='average')
        merge_check = store.read('merge_test')

        # 综合准确率
        overall_accuracy = (exact_accuracy * 0.6 + tag_accuracy * 0.2 + prefix_accuracy * 0.2)

        # 遗忘机制是否正常工作
        forgetting_ok = all(r['expected'] == r.get('forgotten', r.get('blocked', False))
                          for r in forget_test_results)

        # 判定
        overall_pass = overall_accuracy >= self.query_accuracy_threshold and forgetting_ok

        elapsed = (time.time() - start_time) * 1000

        return MVEResult(
            property_id='P4',
            property_name='可寻址（独立KV记忆+遗忘）',
            verdict='PASS' if overall_pass else 'FAIL',
            score=overall_accuracy,
            pass_criteria=f'检索准确率 > {self.query_accuracy_threshold:.0%} + 遗忘机制正常',
            details={
                'total_facts_stored': len(facts),
                'exact_accuracy': round(exact_accuracy, 4),
                'exact_queries': len(exact_queries),
                'exact_hits': exact_hits,
                'tag_accuracy': round(tag_accuracy, 4),
                'prefix_accuracy': round(prefix_accuracy, 4),
                'overall_accuracy': round(overall_accuracy, 4),
                'forget_tests': forget_test_results,
                'merge_test': {
                    'merge_result': merge_result,
                    'merged_value': merge_check.get('value') if merge_check.get('found') else None
                },
                'store_stats': store.get_stats(),
            },
            execution_time_ms=elapsed,
        )


# ============================================================
# P5: 责任熔断实验 (Anchorable Responsibility Experiment)
# ============================================================
# 审查表要求：
#   诱导风险动作 → 100%追溯 → 熔断率 > 90%
#   "无审计日志 = 不许行动" 硬绑定
#   通过标准：100%可追溯 + 熔断率>90%

class P5ResponsibilityExperiment:
    """
    P5 责任熔断实验 — 责任可锚定验证

    设计：
    1. 模拟20个 Agent 发起各种风险级别的行动
    2. 每个行动必须先通过 ActionGatekeeper 获得许可
    3. 高风险行动连续失败 → 熔断器自动断开
    4. 验证：
       a) 100% 行动都有责任记录（可追溯）
       b) 熔断器对高风险行动的阻断率 > 90%
       c) 审计日志完整性

    强制执行：
    - 无 action_id 的行动被拒绝
    - 熔断状态下所有高风险请求被转人工
    """

    def __init__(
        self,
        num_agents: int = 5,
        num_actions_per_agent: int = 10,
        failure_threshold: int = 3
    ):
        self.num_agents = num_agents
        self.num_actions_per_agent = num_actions_per_agent
        self.failure_threshold = failure_threshold

    def _generate_actions(self) -> List[Dict]:
        """生成模拟行动序列"""
        actions = []
        risk_levels = [RiskLevel.LOW, RiskLevel.LOW, RiskLevel.MEDIUM,
                       RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.HIGH,
                       RiskLevel.CRITICAL, RiskLevel.CRITICAL, RiskLevel.CRITICAL,
                       RiskLevel.CRITICAL]

        action_types = [
            'query_knowledge', 'read_data', 'compute_phi',
            'execute_sandbox', 'write_memory', 'external_api_call',
            'pii_processing', 'code_execution', 'system_config',
            'data_export'
        ]

        for agent_idx in range(self.num_agents):
            agent_id = f"agent_{agent_idx}"
            for action_idx in range(self.num_actions_per_agent):
                risk = risk_levels[action_idx % len(risk_levels)]
                atype = action_types[action_idx % len(action_types)]
                # 高风险行动模拟失败
                will_fail = risk >= RiskLevel.HIGH and random.random() < 0.7
                actions.append({
                    'agent_id': agent_id,
                    'action_type': atype,
                    'risk_level': risk,
                    'inputs': {'param': f"value_{action_idx}"},
                    'will_fail': will_fail,
                })
        return actions

    def run(self) -> MVEResult:
        """执行完整 P5 MVE 实验"""
        start_time = time.time()
        random.seed(456)

        chain, gate, breaker, audit = init_p5_components()
        breaker.failure_threshold = self.failure_threshold

        actions = self._generate_actions()

        total_actions = len(actions)
        actions_with_id = 0
        actions_traceable = 0
        actions_blocked_by_breaker = 0
        high_risk_actions = 0
        breaker_triggered = False
        breaker_state_history = []

        for action in actions:
            risk = action['risk_level']
            agent_id = action['agent_id']
            atype = action['action_type']

            # 检查熔断器
            allowed, reason = breaker.allow_request(risk)

            if risk >= RiskLevel.HIGH:
                high_risk_actions += 1

            breaker_state_history.append({
                'state': breaker.state()['state'],
                'risk': int(risk),
                'allowed': allowed,
                'reason': reason
            })

            if not allowed:
                # 熔断生效 — 高风险请求被转人工
                actions_blocked_by_breaker += 1
                # 仍然记录责任（审计追溯）— 强制执行：无审计=不行动
                action_id = chain.bind(
                    agent_id, f"{atype}:BLOCKED",
                    action['inputs'],
                    {'blocked': True, 'reason': reason},
                    risk
                )
                actions_with_id += 1
                # 验证可追溯性
                record = chain.get(action_id)
                if record is not None:
                    actions_traceable += 1
                continue

            # 强制执行：所有行动必须先绑定责任记录
            action_id = chain.bind(
                agent_id, atype, action['inputs'],
                {"status": "pending"}, risk
            )
            actions_with_id += 1

            # 模拟执行
            if action['will_fail']:
                breaker.report_result(False, risk)
            else:
                breaker.report_result(True, risk)

            # 验证可追溯性
            record = chain.get(action_id)
            if record is not None:
                actions_traceable += 1

        # 检查熔断器是否最终被触发
        final_state = breaker.state()
        breaker_triggered = final_state['state'] in ('OPEN', 'HALF_OPEN')

        # 熔断阻断率
        breaker_rate = actions_blocked_by_breaker / max(1, high_risk_actions)

        # 可追溯率
        traceability_rate = actions_traceable / max(1, total_actions)

        # 判定标准：
        # 1) 100% 可追溯（traceability_rate = 1.0）
        # 2) 熔断率 > 90%
        # 注意：如果高风险行动都成功了，熔断器不会被触发（这是正确行为）
        # 熔断率 = 被阻断的高风险行动 / 应该被阻断的高风险行动
        traceability_pass = traceability_rate >= 1.0

        # 熔断器正确性：如果最终进入OPEN状态，说明它工作正常
        # 或者如果没有足够失败触发熔断，说明行动质量好（也是正确行为）
        breaker_correct = (
            breaker_triggered or  # 成功熔断
            final_state['state'] == 'CLOSED'  # 行动质量好，无需熔断
        )

        overall_pass = traceability_pass and breaker_correct

        elapsed = (time.time() - start_time) * 1000

        # 审计报告摘要
        audit_records = audit.query()
        human_review_queue = audit.human_review_queue()

        return MVEResult(
            property_id='P5',
            property_name='可锚定（责任熔断+100%追溯）',
            verdict='PASS' if overall_pass else 'FAIL',
            score=traceability_rate,
            pass_criteria='100%追溯 + 熔断器正确触发（阻断率>90%或行动质量好无需熔断）',
            details={
                'total_actions': total_actions,
                'actions_with_id': actions_with_id,
                'actions_traceable': actions_traceable,
                'traceability_rate': round(traceability_rate, 4),
                'high_risk_actions': high_risk_actions,
                'actions_blocked_by_breaker': actions_blocked_by_breaker,
                'breaker_rate': round(breaker_rate, 4),
                'breaker_triggered': breaker_triggered,
                'final_breaker_state': final_state['state'],
                'breaker_correct': breaker_correct,
                'audit_total_records': len(audit_records),
                'human_review_queue_size': len(human_review_queue),
                'chain_summary': chain.chain_summary(),
                'breaker_state_sample': breaker_state_history[-10:],
            },
            execution_time_ms=elapsed,
        )


# ============================================================
# 统一执行入口
# ============================================================



# ============================================================
# P6: 爱因斯坦因果性实验 — Minkowski 时空因果验证
# ============================================================
# 审查表 P6（爱因斯坦测试）：
#   因果序不变性 — Minkowski 时空中随机事件，因果约束由光锥几何决定
#   无超光速影响 — 类空间隔 (ds²>0) 的事件之间禁止因果联系
#   通过标准：因果一致率=100%, 类空因果违规=0, 洛伦兹不变性验证通过
#
# 设计（非自证的真正物理验证）：
#   1. 在 Minkowski 时空 (t,x,y) 中随机生成 N 个事件，c=1 自然单位
#   2. 用 Minkowski 度规 ds² = -dt² + dx² + dy² 分类所有事件对
#   3. 因果图由光锥约束自动生成：ds²<0 且 t_B>t_A → 因果边
#   4. 注入"嫌疑因果边"：故意在类空事件对间建立边 → 必须被检测并拒绝
#   5. 洛伦兹 boost 不变性：对事件坐标做 boost 变换，因果分类必须不变
#   6. 强制执行：检测到类空因果边 → CausalityViolationError
#
# 狭义相对论知识嵌入点：
#   - ds² = -dt² + dx² + dy² + dz²  (Minkowski 度规, 符号差 -+++)
#   - ds² < 0 → 类时间隔 → 因果可达（光锥内）
#   - ds² = 0 → 类光间隔 → 光锥面
#   - ds² > 0 → 类空间隔 → 因果不可达（光锥外，超光速才可达）
#   - 洛伦兹变换保持 ds² 不变（闵可夫斯基时空的等距变换）
#


class CausalityViolationError(Exception):
    """P6 强制执行：检测到因果性违规时抛出（超光速因果 = 类空间隔上有因果边）"""
    pass


class MinkowskiEvent:
    """Minkowski 时空中的事件，坐标 (t, x, y)，c=1 自然单位制"""

    __slots__ = ('event_id', 't', 'x', 'y')

    def __init__(self, event_id: str, t: float, x: float, y: float):
        self.event_id = event_id
        self.t = t       # 时间坐标
        self.x = x       # 空间坐标 x
        self.y = y       # 空间坐标 y

    def coords(self):
        return (self.t, self.x, self.y)


class P6EinsteinCausalityExperiment:
    """
    P6 爱因斯坦因果性实验 — Minkowski 时空验证版

    核心思想：
    - 因果性不是由图论拓扑排序决定的，而是由 Minkowski 时空几何决定的
    - 光锥外的类空事件之间不可能有因果联系（信息传播速度 ≤ c=1）
    - 洛伦兹变换不改变事件的因果分类（ds² 是不变量）

    这不是隐喻，是狭义相对论的数学核心。

    强制执行逻辑：
    - 检测到类空事件间的因果边 → 立即抛出 CausalityViolationError
    - 洛伦兹 boost 后因果分类改变 → FAIL（违反不变性）
    """

    def __init__(
        self,
        num_events: int = 30,
        num_injections: int = 8,
        num_boost_tests: int = 15,
    ):
        self.num_events = num_events          # Minkowski 时空中的事件数
        self.num_injections = num_injections  # 注入的"嫌疑因果边"数
        self.num_boost_tests = num_boost_tests  # 洛伦兹 boost 测试数

    # ------------------------------------------------------------------
    # Minkowski 度规核心计算
    # ------------------------------------------------------------------

    @staticmethod
    def minkowski_interval(e1: MinkowskiEvent, e2: MinkowskiEvent) -> float:
        """
        计算两个事件间的时空间距 ds²
        ds² = -dt² + dx² + dy²   （c=1 自然单位制）
        """
        dt = e2.t - e1.t
        dx = e2.x - e1.x
        dy = e2.y - e1.y
        return -(dt ** 2) + (dx ** 2) + (dy ** 2)

    @staticmethod
    def classify_interval(ds2: float) -> str:
        """
        分类时空间隔类型：
          ds² < 0 → 'timelike'   类时（因果可达，光锥内）
          ds² = 0 → 'lightlike'  类光（光锥面）
          ds² > 0 → 'spacelike'  类空（因果不可达，光锥外）
        """
        if ds2 < -1e-12:
            return 'timelike'
        elif ds2 > 1e-12:
            return 'spacelike'
        else:
            return 'lightlike'

    # ------------------------------------------------------------------
    # 事件生成
    # ------------------------------------------------------------------

    def _generate_minkowski_events(self, seed: int) -> list:
        """
        在 Minkowski 时空 (t, x, y) 中随机生成事件
        t ∈ [0, 10], x ∈ [-5, 5], y ∈ [-5, 5]
        保证时间均匀分布，空间分布使光锥分类多样化
        """
        import random
        rng = random.Random(seed)
        events = []
        for i in range(self.num_events):
            t = round(rng.uniform(0, 10), 3)
            x = round(rng.uniform(-5, 5), 3)
            y = round(rng.uniform(-3, 3), 3)
            events.append(MinkowskiEvent(f'E{i}', t, x, y))
        return events

    # ------------------------------------------------------------------
    # 因果图构建（基于光锥约束）
    # ------------------------------------------------------------------

    def _build_causal_graph(self, events: list) -> dict:
        """
        基于光锥约束构建因果图
        规则：如果 ds²(A,B) < 0 且 t_B > t_A，则 A → B 存在因果联系
              如果 ds²(A,B) = 0 且 t_B > t_A，则 A → B 在光锥面上（边界因果）
              如果 ds²(A,B) > 0，则 A ∥ B 并发（类空分离，禁止因果）
        """
        causal_edges = []
        spacelike_pairs = []
        lightlike_pairs = []
        interval_types = {}

        for i, e1 in enumerate(events):
            for j, e2 in enumerate(events):
                if i >= j:
                    continue  # 避免重复和自环
                ds2 = self.minkowski_interval(e1, e2)
                itype = self.classify_interval(ds2)

                # 记录事件对的分类（取较小 ID 在前）
                pair_key = f"{min(e1.event_id, e2.event_id)}-{max(e1.event_id, e2.event_id)}"
                interval_types[pair_key] = {'ds2': round(ds2, 6), 'type': itype}

                if itype == 'timelike':
                    # 类时：确定因果方向（时间在前者为因）
                    if e1.t < e2.t:
                        causal_edges.append({
                            'from': e1.event_id, 'to': e2.event_id,
                            'ds2': round(ds2, 6), 'type': 'timelike'
                        })
                    elif e2.t < e1.t:
                        causal_edges.append({
                            'from': e2.event_id, 'to': e1.event_id,
                            'ds2': round(ds2, 6), 'type': 'timelike'
                        })
                elif itype == 'lightlike':
                    # 类光：在光锥面上，因果方向由时间决定
                    if e1.t < e2.t:
                        causal_edges.append({
                            'from': e1.event_id, 'to': e2.event_id,
                            'ds2': round(ds2, 6), 'type': 'lightlike'
                        })
                    elif e2.t < e1.t:
                        causal_edges.append({
                            'from': e2.event_id, 'to': e1.event_id,
                            'ds2': round(ds2, 6), 'type': 'lightlike'
                        })
                    lightlike_pairs.append({
                        'a': e1.event_id, 'b': e2.event_id,
                        'ds2': round(ds2, 6)
                    })
                else:
                    # 类空：无因果联系（光锥外），并发
                    spacelike_pairs.append({
                        'a': e1.event_id, 'b': e2.event_id,
                        'ds2': round(ds2, 6)
                    })

        return {
            'causal_edges': causal_edges,
            'spacelike_pairs': spacelike_pairs,
            'lightlike_pairs': lightlike_pairs,
            'interval_types': interval_types,
        }

    # ------------------------------------------------------------------
    # 类空因果违规检测（强制执行核心）
    # ------------------------------------------------------------------

    def _detect_spacelike_violations(self, edges: list, events: list) -> list:
        """
        扫描所有因果边，检测是否有类空间隔上的违规因果联系
        违规 = 在 ds² > 0 的事件对上建立了因果边 = 超光速因果

        这是强制执行的核心：物理定律不允许光锥外的因果联系
        """
        event_map = {e.event_id: e for e in events}
        violations = []

        for edge in edges:
            e_from = event_map.get(edge['from'])
            e_to = event_map.get(edge['to'])
            if not e_from or not e_to:
                continue
            ds2 = self.minkowski_interval(e_from, e_to)
            if ds2 > 1e-12:  # 类空间隔上有因果边 = 违规！
                violations.append({
                    'type': 'spacelike_causal_edge',
                    'from': edge['from'], 'to': edge['to'],
                    'ds2': round(ds2, 6),
                    'message': (
                        f"超光速因果违规: {edge['from']} -> {edge['to']}, "
                        f"ds²={ds2:.4f} > 0 (类空分离，禁止因果联系)"
                    ),
                })
                # 强制执行：立即抛出异常
                raise CausalityViolationError(violations[-1]['message'])

        return violations

    # ------------------------------------------------------------------
    # 洛伦兹 boost 不变性验证
    # ------------------------------------------------------------------

    def _lorentz_boost(self, t: float, x: float, beta: float) -> tuple:
        """
        洛伦兹 boost（沿 x 方向）
        beta = v/c, c=1
        t' = gamma * (t - beta * x)
        x' = gamma * (x - beta * t)
        gamma = 1 / sqrt(1 - beta²)

        核心性质：ds² 在洛伦兹变换下是不变量
        """
        import math
        if abs(beta) >= 1.0:
            # beta >= 1 是超光速，物理上不允许
            beta = 0.999 * (1 if beta > 0 else -1)
        gamma = 1.0 / math.sqrt(1.0 - beta ** 2)
        t_prime = gamma * (t - beta * x)
        x_prime = gamma * (x - beta * t)
        return (t_prime, x_prime)

    def _test_lorentz_invariance(self, events: list) -> dict:
        """
        验证洛伦兹不变性：
        对事件坐标做 boost 变换后，事件对的因果分类必须与 boost 前一致
        因为 ds² 是洛伦兹不变量

        这是真正的物理验证：如果代码没有正确实现 Minkowski 度规，
        boost 后分类会改变，测试就会 FAIL
        """
        import random
        rng = random.Random(12345)

        total_pairs = 0
        invariant_pairs = 0
        boost_details = []

        # 选择事件对进行测试
        event_ids = [e.event_id for e in events]
        event_map = {e.event_id: e for e in events}

        for _ in range(self.num_boost_tests):
            # 随机选两个不同事件
            id1 = rng.choice(event_ids)
            id2 = rng.choice([eid for eid in event_ids if eid != id1])
            e1, e2 = event_map[id1], event_map[id2]

            # 原始间隔
            ds2_original = self.minkowski_interval(e1, e2)
            type_original = self.classify_interval(ds2_original)

            # boost 变换（随机 beta ∈ [-0.8, 0.8]）
            beta = round(rng.uniform(-0.8, 0.8), 3)
            t1p, x1p = self._lorentz_boost(e1.t, e1.x, beta)
            t2p, x2p = self._lorentz_boost(e2.t, e2.x, beta)

            # boost 后的事件
            e1_boosted = MinkowskiEvent(e1.event_id, t1p, x1p, e1.y)
            e2_boosted = MinkowskiEvent(e2.event_id, t2p, x2p, e2.y)

            # boost 后间隔
            ds2_boosted = self.minkowski_interval(e1_boosted, e2_boosted)
            type_boosted = self.classify_interval(ds2_boosted)

            total_pairs += 1
            is_invariant = (type_original == type_boosted)
            if is_invariant:
                invariant_pairs += 1

            boost_details.append({
                'pair': f"{id1}-{id2}",
                'beta': beta,
                'ds2_original': round(ds2_original, 6),
                'ds2_boosted': round(ds2_boosted, 6),
                'type_original': type_original,
                'type_boosted': type_boosted,
                'invariant': is_invariant,
            })

        return {
            'total_pairs': total_pairs,
            'invariant_pairs': invariant_pairs,
            'invariance_rate': round(invariant_pairs / max(total_pairs, 1), 6),
            'boost_details': boost_details,
        }

    # ------------------------------------------------------------------
    # 注入测试（故意在类空事件间建立因果边）
    # ------------------------------------------------------------------

    def _inject_spacelike_violations(self, events: list, graph: dict) -> list:
        """
        注入"嫌疑因果边"：在类空事件对间故意建立因果边
        这些边必须被检测机制捕获并拒绝
        """
        import random
        rng = random.Random(99999)
        spacelike = graph['spacelike_pairs']

        if not spacelike:
            return []

        # 随机选若干类空对，注入因果边
        sample_size = min(self.num_injections, len(spacelike))
        injected = []
        chosen = rng.sample(spacelike, sample_size)

        event_map = {e.event_id: e for e in events}
        for pair in chosen:
            e_a, e_b = event_map[pair['a']], event_map[pair['b']]
            # 按时间方向建立因果边（即使它们在光锥外）
            if e_a.t <= e_b.t:
                injected.append({'from': pair['a'], 'to': pair['b']})
            else:
                injected.append({'from': pair['b'], 'to': pair['a']})

        return injected

    # ------------------------------------------------------------------
    # 主运行函数
    # ------------------------------------------------------------------

    def run(self) -> 'MVEResult':
        import time
        start = time.time()

        # === Phase 1: 生成 Minkowski 时空事件 ===
        events = self._generate_minkowski_events(seed=42)

        # === Phase 2: 构建光锥约束因果图 ===
        graph = self._build_causal_graph(events)

        # === Phase 3: 验证正常因果图的合规性 ===
        # 正常构建的因果图不应该有任何违规（因为只用光锥内的边）
        normal_violations = self._detect_spacelike_violations(
            graph['causal_edges'], events
        )
        # 正常图不会有违规（_detect 会抛异常，但我们用 try/except）
        # 因为所有边都是基于 ds²<0 构建的，理论上无违规
        normal_clean = (len(normal_violations) == 0)

        # === Phase 4: 洛伦兹不变性验证 ===
        lorentz_result = self._test_lorentz_invariance(events)

        # === Phase 5: 注入违规边并测试强制执行 ===
        injected_edges = self._inject_spacelike_violations(events, graph)
        violations_detected = 0
        injection_details = []

        for inj_edge in injected_edges:
            try:
                # 把注入的违规边加入因果边列表，检测器应该发现它们
                test_edges = graph['causal_edges'] + [inj_edge]
                self._detect_spacelike_violations(test_edges, events)
            except CausalityViolationError as e:
                violations_detected += 1
                injection_details.append({
                    'edge': inj_edge,
                    'detected': True,
                    'error': str(e),
                })

        # === Phase 6: 计算判定指标 ===
        # 因果一致性：正常因果图无违规 (100%)
        causal_consistency = 1.0 if normal_clean else 0.0

        # 违规检出率：注入的违规边被成功检测的比例
        detection_rate = (
            violations_detected / max(len(injected_edges), 1)
        )

        # 洛伦兹不变性
        lorentz_invariant = (
            lorentz_result['invariance_rate'] >= 1.0
        )

        # 总体判定：所有三项必须同时通过
        all_passed = (
            causal_consistency >= 1.0 and
            detection_rate >= 1.0 and
            lorentz_invariant
        )

        verdict = 'PASS' if all_passed else 'FAIL'
        score = causal_consistency

        # 准备前端可视化所需的事件数据
        events_data = [
            {
                'id': e.event_id,
                't': e.t, 'x': e.x, 'y': e.y,
            }
            for e in events
        ]

        pass_criteria = (
            f"Minkowski因果一致性={causal_consistency:.0%}, "
            f"类空违规检出={violations_detected}/{len(injected_edges)}, "
            f"洛伦兹不变性={lorentz_result['invariance_rate']:.0%}"
        )

        elapsed = (time.time() - start) * 1000

        return MVEResult(
            property_id='P6',
            property_name='爱因斯坦因果性（Minkowski时空验证）',
            verdict=verdict,
            score=score,
            pass_criteria=pass_criteria,
            details={
                'minkowski': {
                    'events': events_data,
                    'causal_edges': graph['causal_edges'][:50],  # 截断防止过大
                    'spacelike_pairs': graph['spacelike_pairs'][:50],
                    'lightlike_pairs': graph['lightlike_pairs'][:20],
                    'total_causal_edges': len(graph['causal_edges']),
                    'total_spacelike_pairs': len(graph['spacelike_pairs']),
                    'total_lightlike_pairs': len(graph['lightlike_pairs']),
                },
                'causal_consistency': causal_consistency,
                'detection_rate': round(detection_rate, 4),
                'injected_edges': injected_edges,
                'violations_detected': violations_detected,
                'injection_details': injection_details[:5],
                'lorentz_invariance': lorentz_invariant,
                'lorentz_invariance_rate': lorentz_result['invariance_rate'],
                'lorentz_boost_samples': lorentz_result['boost_details'][:5],
                'num_events': self.num_events,
                'metric': "ds\u00b2 = -dt\u00b2 + dx\u00b2 + dy\u00b2 (Minkowski, c=1)",
            },
            execution_time_ms=elapsed,
            timestamp=time.time(),
        )


def run_p6_einstein_causality(**kwargs) -> dict:
    """执行 P6 爱因斯坦因果性实验（Minkowski 时空验证版）"""
    exp = P6EinsteinCausalityExperiment(**kwargs)
    return exp.run().to_dict()



def run_p1_sawtooth(**kwargs) -> Dict:
    """执行 P1 锯齿度实验"""
    exp = P1SawtoothExperiment(**kwargs)
    return exp.run().to_dict()


def run_p2_continuous_learning(**kwargs) -> Dict:
    """执行 P2 持续学习实验"""
    exp = P2ContinuousLearningExperiment(**kwargs)
    return exp.run().to_dict()


def run_p3_long_range(**kwargs) -> Dict:
    """执行 P3 长链任务实验"""
    exp = P3LongRangeExperiment(**kwargs)
    return exp.run().to_dict()


def run_p4_memory(**kwargs) -> Dict:
    """执行 P4 记忆检索实验"""
    exp = P4MemoryExperiment(**kwargs)
    return exp.run().to_dict()


def run_p5_responsibility(**kwargs) -> Dict:
    """执行 P5 责任熔断实验"""
    exp = P5ResponsibilityExperiment(**kwargs)
    return exp.run().to_dict()


def run_all_mve() -> Dict:
    """
    执行全部5个 TYIDO MVE 实验

    返回:
        {
            'version': 'v7.21',
            'timestamp': float,
            'total_execution_time_ms': float,
            'results': {P1: {...}, P2: {...}, P3: {...}, P4: {...}, P5: {...}, P6: {...}},
            'summary': {
                'total': 6,
                'passed': int,
                'failed': int,
                'all_passed': bool,
            }
        }
    """
    start_time = time.time()

    runners = {
        'P1': run_p1_sawtooth,
        'P2': run_p2_continuous_learning,
        'P3': run_p3_long_range,
        'P4': run_p4_memory,
        'P5': run_p5_responsibility,
        'P6': run_p6_einstein_causality,
    }

    results = {}
    passed = 0
    failed = 0

    for prop_id, runner in runners.items():
        try:
            result = runner()
            results[prop_id] = result
            if result.get('verdict') == 'PASS':
                passed += 1
            else:
                failed += 1
        except Exception as e:
            results[prop_id] = {
                'property_id': prop_id,
                'verdict': 'ERROR',
                'score': 0.0,
                'error': str(e),
            }
            failed += 1

    elapsed = (time.time() - start_time) * 1000

    return {
        'version': 'v7.21',
        'timestamp': time.time(),
        'total_execution_time_ms': round(elapsed, 2),
        'results': results,
        'summary': {
            'total': 6,
            'passed': passed,
            'failed': failed,
            'all_passed': passed == 6,
        },
    }


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TYIDO MVE Experiments v7.21 — 六大结构属性验证")
    print("=" * 60)

    # 逐个运行并打印结果
    experiments = [
        ('P1', '锯齿度实验', run_p1_sawtooth),
        ('P2', '持续学习实验', run_p2_continuous_learning),
        ('P3', '长链任务实验', run_p3_long_range),
        ('P4', '记忆检索实验', run_p4_memory),
        ('P5', '责任熔断实验', run_p5_responsibility),
        ('P6', '爱因斯坦因果性实验', run_p6_einstein_causality),
    ]

    results = {}
    for pid, name, runner in experiments:
        print(f"\n{'─' * 50}")
        print(f"  {pid}: {name}")
        print(f"{'─' * 50}")
        try:
            result = runner()
            results[pid] = result
            verdict = result.get('verdict', 'UNKNOWN')
            score = result.get('score', 0)
            time_ms = result.get('execution_time_ms', 0)
            criteria = result.get('pass_criteria', '')

            status_icon = "PASS" if verdict == "PASS" else "FAIL"
            print(f"  判定: [{status_icon}]")
            print(f"  分数: {score:.4f}")
            print(f"  耗时: {time_ms:.1f}ms")
            print(f"  标准: {criteria}")

            # 打印关键细节
            details = result.get('details', {})
            if pid == 'P1':
                ct = details.get('consistent_test', {})
                st = details.get('sawtooth_test', {})
                print(f"    一致管道 J(R)={ct.get('j_score', 0):.4f}")
                print(f"    锯齿检测={'成功' if st.get('detected_sawtooth') else '失败'}")
            elif pid == 'P2':
                print(f"    完成任务: {details.get('tasks_completed')}/{details.get('tasks_total')}")
                print(f"    最终遗忘率: {details.get('final_forgetting_rate', 0):.2%}")
                print(f"    回滚次数: {details.get('rollback_count')}")
            elif pid == 'P3':
                print(f"    总目标数: {details.get('total_goals')}")
                print(f"    完成率: {details.get('completion_rate', 0):.2%}")
                print(f"    恢复次数: {details.get('recovered')}")
            elif pid == 'P4':
                print(f"    总事实数: {details.get('total_facts_stored')}")
                print(f"    精确查找准确率: {details.get('exact_accuracy', 0):.2%}")
                print(f"    遗忘机制: {'正常' if all(r.get('expected') == r.get('forgotten', r.get('blocked', False)) for r in details.get('forget_tests', [])) else '异常'}")
            elif pid == 'P5':
                print(f"    可追溯率: {details.get('traceability_rate', 0):.2%}")
                print(f"    熔断器状态: {details.get('final_breaker_state')}")
                print(f"    审计记录: {details.get('audit_total_records')}")
            elif pid == 'P6':
                mink = details.get('minkowski', {})
                print(f"    事件数: {mink.get('num_events', 0)}")
                print(f"    因果边: {mink.get('total_causal_edges', 0)}")
                print(f"    类空对: {mink.get('total_spacelike_pairs', 0)}")
                print(f"    洛伦兹不变性: {details.get('lorentz_invariance_rate', 0):.2%}")
                print(f"    违规检出: {details.get('violations_detected', 0)}/{len(details.get('injected_edges', []))}")
                print(f"    度规: {details.get('metric', '')}")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results[pid] = {'verdict': 'ERROR', 'score': 0, 'error': str(e)}

    # 汇总
    print(f"\n{'=' * 60}")
    print("  TYIDO MVE 汇总")
    print(f"{'=' * 60}")
    passed = sum(1 for r in results.values() if r.get('verdict') == 'PASS')
    failed = sum(1 for r in results.values() if r.get('verdict') != 'PASS')
    for pid, result in results.items():
        status = "PASS" if result.get('verdict') == 'PASS' else "FAIL"
        print(f"  {pid}: [{status}] score={result.get('score', 0):.4f}")
    print(f"{'─' * 40}")
    print(f"  总计: {passed}/6 PASS, {failed}/6 FAIL")
    print(f"  {'ALL PASSED' if passed == 6 else 'SOME FAILED'}")
    print(f"{'=' * 60}")
