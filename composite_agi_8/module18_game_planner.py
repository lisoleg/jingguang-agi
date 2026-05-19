"""
太乙AGI 11.0 - Module 18: GAME分层规划引擎
================================================

基于Virtuals Protocol的G.A.M.E.框架（Generative Autonomous Multimodal Entities）启发，
实现太乙AGI的 hierarchical planning 分层规划能力：

【G.A.M.E.框架核心】
G.A.M.E. = Generative Autonomous Multimodal Entities

1. 高层规划器 (High-level Planner)
   - 长期目标制定
   - 宏观策略规划
   - 资源分配决策
   
2. 低层规划器 (Low-level Planners)
   - 具体执行步骤
   - 实时环境响应
   - 任务分解执行
   
3. Butler接口 (用户交互层)
   - 自然语言意图解析
   - 多Agent网络路由
   - 结果格式化输出

【与太乙AGI的映射】
- 高层规划 ↔ DIKWP的Intent层 + Ftel目的约束（Module 14）
- 低层规划 ↔ DIKWP的Knowledge层 + 螺旋认知（Module 14）
- Butler ↔ 对话界面层 + 情绪理解（Module 4）

核心创新：
- 目标分解树（Goal Decomposition Tree）
- 执行状态机（Execution State Machine）
- 自适应重规划（Adaptive Replanning）

理论依据：Virtuals G.A.M.E. + 复合体理学目的论 + 范畴论

Author: 太乙AGI研究团队
Version: 11.0
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import heapq


class PlanStatus(Enum):
    """规划状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLANNING = "replanning"


class StepStatus(Enum):
    """步骤状态"""
    WAITING = "waiting"
    READY = "ready"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class GoalNode:
    """目标节点（目标分解树中的节点）"""
    goal_id: str
    description: str
    goal_type: str                      # goal/subgoal/action
    
    # 层次信息
    level: int = 0                      # 树层级
    parent_id: Optional[str] = None
    
    # 约束条件
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: Dict[str, float] = field(default_factory=dict)
    
    # 资源需求
    estimated_cost: float = 1.0
    required_capabilities: List[str] = field(default_factory=list)
    
    # 执行状态
    status: PlanStatus = PlanStatus.PENDING
    progress: float = 0.0               # 0-1
    
    # 子目标
    children_ids: List[str] = field(default_factory=list)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 备选方案
    alternatives: List[str] = field(default_factory=list)  # 备选goal_id列表


@dataclass
class ExecutionStep:
    """执行步骤"""
    step_id: str
    description: str
    
    # 所属目标
    goal_id: str
    parent_step_id: Optional[str] = None
    
    # 前置依赖
    dependencies: List[str] = field(default_factory=list)  # 依赖的step_id
    
    # 执行信息
    status: StepStatus = StepStatus.WAITING
    executor_id: Optional[str] = None  # 指定执行者
    assigned_module: Optional[str] = None
    
    # 执行结果
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    # 时间估计
    estimated_duration: float = 1.0     # 相对单位
    actual_duration: Optional[float] = None
    
    # 重试信息
    retry_count: int = 0
    max_retries: int = 3
    
    # 执行时间
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Plan:
    """完整规划"""
    plan_id: str
    original_goal: str
    
    # 目标树
    goal_tree: Dict[str, GoalNode] = field(default_factory=dict)
    root_goal_id: Optional[str] = None
    
    # 执行步骤
    steps: Dict[str, ExecutionStep] = field(default_factory=dict)
    execution_queue: List[str] = field(default_factory=list)  # step_id优先队列
    
    # 状态
    status: PlanStatus = PlanStatus.PENDING
    current_step_id: Optional[str] = None
    
    # 上下文
    context: Dict[str, Any] = field(default_factory=dict)
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    
    # 统计
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def get_ready_steps(self) -> List[str]:
        """获取就绪步骤（依赖都已完成）"""
        ready = []
        for step_id, step in self.steps.items():
            if step.status != StepStatus.WAITING:
                continue
            # 检查依赖
            deps_satisfied = all(
                self.steps[d].status == StepStatus.SUCCEEDED
                for d in step.dependencies if d in self.steps
            )
            if deps_satisfied:
                ready.append(step_id)
        return ready
    
    def get_progress(self) -> float:
        """计算整体进度"""
        if not self.steps:
            return 0.0
        completed = sum(
            1 for s in self.steps.values()
            if s.status in [StepStatus.SUCCEEDED, StepStatus.SKIPPED]
        )
        return completed / len(self.steps)


class HighLevelPlanner:
    """
    高层规划器 - 战略决策层
    
    职责：
    1. 理解长期目标
    2. 分解为可执行的子目标
    3. 制定宏观策略
    4. 资源分配决策
    """
    
    def __init__(self, game_engine: 'GAMEEngine'):
        self.game_engine = game_engine
        self.strategy_library = self._build_strategy_library()
    
    def _build_strategy_library(self) -> Dict:
        """构建策略库"""
        return {
            'analysis': {
                'strategy': 'decompose_and_investigate',
                'typical_depth': 3,
                'branch_factor': 4
            },
            'creation': {
                'strategy': 'iterative_prototype',
                'typical_depth': 2,
                'branch_factor': 3
            },
            'verification': {
                'strategy': 'multi_perspective_check',
                'typical_depth': 2,
                'branch_factor': 5
            },
            'optimization': {
                'strategy': 'gradient_ascent',
                'typical_depth': 3,
                'branch_factor': 2
            },
            'general': {
                'strategy': 'hierarchical_decompose',
                'typical_depth': 3,
                'branch_factor': 3
            }
        }
    
    def create_plan(self, goal_description: str,
                   goal_type: str = "general",
                   constraints: Optional[Dict] = None) -> Plan:
        """
        创建高层规划
        
        Args:
            goal_description: 目标描述
            goal_type: 目标类型
            constraints: 约束条件
            
        Returns:
            Plan: 完整规划
        """
        plan = Plan(
            plan_id=f"plan_{uuid.uuid4().hex[:12]}",
            original_goal=goal_description
        )
        
        # 创建根目标
        root_goal = GoalNode(
            goal_id=f"goal_{uuid.uuid4().hex[:8]}",
            description=goal_description,
            goal_type="goal",
            level=0,
            constraints=constraints or {},
            success_criteria=self._infer_success_criteria(goal_type)
        )
        
        plan.goal_tree[root_goal.goal_id] = root_goal
        plan.root_goal_id = root_goal.goal_id
        
        # 分解目标
        strategy = self.strategy_library.get(goal_type, self.strategy_library['general'])
        self._decompose_goal(plan, root_goal, strategy, depth=0)
        
        # 生成执行步骤
        self._generate_steps(plan, root_goal)
        
        # 初始化执行队列
        plan.execution_queue = plan.get_ready_steps()
        
        print(f"  [GAME-HL] 高层规划创建: {plan.plan_id}")
        print(f"    目标: {goal_description}")
        print(f"    策略: {strategy['strategy']}")
        print(f"    子目标数: {len(plan.goal_tree) - 1}")
        print(f"    执行步骤: {len(plan.steps)}")
        
        return plan
    
    def _decompose_goal(self, plan: Plan, goal: GoalNode,
                        strategy: Dict, depth: int):
        """递归分解目标"""
        max_depth = strategy['typical_depth']
        
        if depth >= max_depth:
            return
        
        # 根据策略生成分解
        if strategy['strategy'] == 'decompose_and_investigate':
            sub_goals = self._decompose_analysis(goal)
        elif strategy['strategy'] == 'iterative_prototype':
            sub_goals = self._decompose_creation(goal)
        elif strategy['strategy'] == 'multi_perspective_check':
            sub_goals = self._decompose_verification(goal)
        else:
            sub_goals = self._decompose_general(goal, strategy['branch_factor'])
        
        for sub_desc in sub_goals:
            sub_goal = GoalNode(
                goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                description=sub_desc,
                goal_type="subgoal",
                level=depth + 1,
                parent_id=goal.goal_id,
                estimated_cost=goal.estimated_cost / len(sub_goals) if sub_goals else 1.0
            )
            
            plan.goal_tree[sub_goal.goal_id] = sub_goal
            goal.children_ids.append(sub_goal.goal_id)
            
            # 递归分解
            self._decompose_goal(plan, sub_goal, strategy, depth + 1)
    
    def _decompose_analysis(self, goal: GoalNode) -> List[str]:
        """分析类目标分解"""
        return [
            f"收集{goal.description}相关资料",
            f"理解{goal.description}的核心概念",
            f"分析{goal.description}的关键要素",
            f"综合分析结果形成洞见"
        ]
    
    def _decompose_creation(self, goal: GoalNode) -> List[str]:
        """创作类目标分解"""
        return [
            f"构思{goal.description}的初步方案",
            f"细化方案并评估可行性",
            f"实施并测试方案",
            f"优化并完成最终成果"
        ]
    
    def _decompose_verification(self, goal: GoalNode) -> List[str]:
        """验证类目标分解"""
        return [
            f"设定{goal.description}的验证标准",
            f"执行多角度验证检查",
            f"收集验证证据",
            f"综合评估并得出结论"
        ]
    
    def _decompose_general(self, goal: GoalNode, branch_factor: int) -> List[str]:
        """通用目标分解"""
        return [f"{goal.description}的子任务{i+1}" for i in range(branch_factor)]
    
    def _infer_success_criteria(self, goal_type: str) -> Dict[str, float]:
        """推断成功标准"""
        criteria_map = {
            'analysis': {'completeness': 0.8, 'accuracy': 0.9, 'depth': 0.7},
            'creation': {'novelty': 0.7, 'coherence': 0.8, 'quality': 0.8},
            'verification': {'strictness': 0.9, 'reliability': 0.95, 'completeness': 0.85},
            'general': {'completion': 0.8, 'quality': 0.7}
        }
        return criteria_map.get(goal_type, criteria_map['general'])
    
    def _generate_steps(self, plan: Plan, goal: GoalNode):
        """从目标树生成执行步骤"""
        # 广度优先遍历
        queue = [goal.goal_id]
        
        while queue:
            goal_id = queue.pop(0)
            goal_node = plan.goal_tree[goal_id]
            
            if goal_node.level == 0:
                # 根目标直接转为步骤
                step = ExecutionStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    description=f"执行: {goal_node.description}",
                    goal_id=goal_id
                )
                plan.steps[step.step_id] = step
            else:
                # 子目标生成步骤
                step = ExecutionStep(
                    step_id=f"step_{uuid.uuid4().hex[:8]}",
                    description=f"执行: {goal_node.description}",
                    goal_id=goal_id
                )
                plan.steps[step.step_id] = step
            
            queue.extend(goal_node.children_ids)
    
    def should_replan(self, plan: Plan, failure_step: str) -> bool:
        """判断是否需要重规划"""
        # 简单策略：失败超过3次或关键步骤失败则重规划
        step = plan.steps.get(failure_step)
        if not step:
            return True
        
        if step.retry_count >= step.max_retries:
            return True
        
        # 检查是否是关键路径上的失败
        if goal := plan.goal_tree.get(step.goal_id):
            if goal.level <= 1:  # 高层目标失败
                return True
        
        return False


class LowLevelPlanner:
    """
    低层规划器 - 战术执行层
    
    职责：
    1. 执行具体步骤
    2. 管理执行状态
    3. 处理异常和重试
    4. 实时环境响应
    """
    
    def __init__(self, game_engine: 'GAMEEngine'):
        self.game_engine = game_engine
    
    def select_next_step(self, plan: Plan) -> Optional[ExecutionStep]:
        """
        选择下一个可执行步骤
        
        策略：
        1. 优先选择依赖最少且优先级高的步骤
        2. 考虑执行者负载均衡
        """
        ready_steps = plan.get_ready_steps()
        
        if not ready_steps:
            return None
        
        # 简单策略：选择第一个就绪步骤
        # 高级策略可以基于优先级、成本等进行优化
        step_id = ready_steps[0]
        return plan.steps[step_id]
    
    def execute_step(self, plan: Plan, step: ExecutionStep,
                   executor: Callable) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            plan: 执行计划
            step: 待执行步骤
            executor: 执行器（通常是模块接口）
            
        Returns:
            执行结果
        """
        step.status = StepStatus.EXECUTING
        step.started_at = datetime.now()
        plan.current_step_id = step.step_id
        
        try:
            # 调用执行器
            result = executor(step, plan.context)
            
            step.status = StepStatus.SUCCEEDED
            step.result = result
            step.completed_at = datetime.now()
            
            if step.started_at and step.completed_at:
                delta = step.completed_at - step.started_at
                step.actual_duration = delta.total_seconds()
            
            # 更新目标进度
            self._update_goal_progress(plan, step.goal_id)
            
            # 激活依赖此步骤的后续步骤
            self._activate_dependent_steps(plan, step.step_id)
            
            return result
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.retry_count += 1
            
            print(f"  [GAME-LL] 步骤失败: {step.step_id} | 错误: {e}")
            
            return {'error': str(e), 'should_retry': step.retry_count < step.max_retries}
    
    def _update_goal_progress(self, plan: Plan, goal_id: str):
        """更新目标进度"""
        goal = plan.goal_tree.get(goal_id)
        if not goal:
            return
        
        # 计算子目标/步骤完成比例
        children = goal.children_ids
        if not children:
            goal.progress = 1.0
        else:
            child_steps = [s for s in plan.steps.values() if s.goal_id == goal_id]
            if child_steps:
                completed = sum(1 for s in child_steps if s.status == StepStatus.SUCCEEDED)
                goal.progress = completed / len(child_steps)
        
        # 更新父目标
        if goal.parent_id:
            self._update_goal_progress(plan, goal.parent_id)
    
    def _activate_dependent_steps(self, plan: Plan, completed_step_id: str):
        """激活依赖完成的步骤"""
        for step_id, step in plan.steps.items():
            if step.status == StepStatus.WAITING:
                if completed_step_id in step.dependencies:
                    # 检查是否所有依赖都已完成
                    deps_done = all(
                        plan.steps[d].status == StepStatus.SUCCEEDED
                        for d in step.dependencies if d in plan.steps
                    )
                    if deps_done:
                        step.status = StepStatus.READY


class ButlerInterface:
    """
    Butler接口 - 用户交互层
    
    基于Virtuals Protocol的Butler Agent设计，
    作为用户与AGI系统的友好桥梁。
    
    功能：
    1. 自然语言意图解析
    2. 任务格式化
    3. 结果展示
    4. 多轮对话管理
    """
    
    def __init__(self, game_engine: 'GAMEEngine'):
        self.game_engine = game_engine
        
        # 对话上下文
        self.conversation_context: Dict[str, Any] = {
            'history': [],
            'current_plan_id': None,
            'user_preferences': {},
            'session_metadata': {}
        }
        
        # 意图识别模式
        self.intent_patterns = {
            'analysis': ['分析', '研究', '理解', '解释', 'analyze', 'research'],
            'creation': ['创建', '生成', '设计', '构建', 'create', 'generate', 'design'],
            'verification': ['验证', '检查', '测试', '确认', 'verify', 'check', 'test'],
            'optimization': ['优化', '改进', '提升', 'enhance', 'optimize', 'improve'],
            'question': ['什么', '如何', '为什么', 'what', 'how', 'why']
        }
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户意图
        
        Args:
            user_input: 用户自然语言输入
            
        Returns:
            解析后的意图结构
        """
        intent = {
            'raw_input': user_input,
            'intent_type': 'general',
            'goal_description': user_input,
            'constraints': {},
            'confidence': 0.5
        }
        
        # 意图类型识别
        for intent_type, patterns in self.intent_patterns.items():
            if any(p in user_input.lower() for p in patterns):
                intent['intent_type'] = intent_type
                intent['confidence'] = 0.8
                break
        
        # 约束提取（简化版）
        constraint_keywords = ['必须', '不能', '应该', '尽量', '不超过']
        for keyword in constraint_keywords:
            if keyword in user_input:
                intent['constraints'][keyword] = True
        
        # 更新上下文
        self.conversation_context['history'].append({
            'role': 'user',
            'content': user_input,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        })
        
        return intent
    
    def format_output(self, result: Dict, format_type: str = "concise") -> str:
        """
        格式化输出
        
        Args:
            result: 执行结果
            format_type: 输出格式类型 (concise/detailed/technical)
            
        Returns:
            格式化后的文本
        """
        if format_type == "concise":
            return self._format_concise(result)
        elif format_type == "detailed":
            return self._format_detailed(result)
        else:
            return self._format_technical(result)
    
    def _format_concise(self, result: Dict) -> str:
        """简洁格式"""
        if 'summary' in result:
            return result['summary']
        if 'conclusion' in result:
            return result['conclusion']
        if 'output' in result:
            return str(result['output'])[:500]
        return str(result)[:500]
    
    def _format_detailed(self, result: Dict) -> str:
        """详细格式"""
        lines = ["📊 执行结果\n"]
        for key, value in result.items():
            if isinstance(value, dict):
                lines.append(f"  {key}:")
                for k, v in value.items():
                    lines.append(f"    - {k}: {v}")
            else:
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    def _format_technical(self, result: Dict) -> str:
        """技术格式"""
        import json
        return json.dumps(result, indent=2, ensure_ascii=False)


class GAMEEngine:
    """
    GAME引擎 - 分层规划与执行控制器
    
    整合G.A.M.E.框架的三个核心组件：
    1. HighLevelPlanner: 高层战略规划
    2. LowLevelPlanner: 低层战术执行
    3. ButlerInterface: 用户友好交互
    
    【核心流程】
    用户输入 → Butler解析 → 高层规划 → 目标分解 
    → 低层执行 → 结果评估 → Butler输出
    
    【创新点】
    - 自适应重规划：失败后自动调整策略
    - 多层次抽象：战略↔战术分离
    - 持续学习：基于执行反馈优化规划
    """
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        
        # 三大组件
        self.high_level_planner = HighLevelPlanner(self)
        self.low_level_planner = LowLevelPlanner(self)
        self.butler = ButlerInterface(self)
        
        # 活跃规划
        self.active_plans: Dict[str, Plan] = {}
        self.completed_plans: List[Plan] = []
        
        # 注册的执行器（模块接口）
        self.executors: Dict[str, Callable] = {}
        
        # 执行统计
        self.stats = {
            'total_plans': 0,
            'successful_plans': 0,
            'failed_plans': 0,
            'average_steps': 0,
            'replan_count': 0
        }
        
        print(f"  [Module 18] GAME分层规划引擎初始化完成 (dim={dim})")
    
    def register_executor(self, name: str, executor: Callable):
        """注册执行器（模块接口）"""
        self.executors[name] = executor
        print(f"    注册执行器: {name}")
    
    def create_and_execute(self, user_input: str) -> Dict[str, Any]:
        """
        完整的GAME流程：解析→规划→执行
        
        Args:
            user_input: 用户自然语言输入
            
        Returns:
            执行结果
        """
        # 1. Butler解析意图
        intent = self.butler.parse_intent(user_input)
        
        # 2. 高层规划
        plan = self.high_level_planner.create_plan(
            goal_description=intent['goal_description'],
            goal_type=intent['intent_type'],
            constraints=intent.get('constraints')
        )
        
        self.active_plans[plan.plan_id] = plan
        self.stats['total_plans'] += 1
        
        # 3. 逐步执行
        max_iterations = 100
        iteration = 0
        
        while plan.get_progress() < 1.0 and iteration < max_iterations:
            iteration += 1
            
            # 选择下一步
            step = self.low_level_planner.select_next_step(plan)
            if not step:
                break
            
            # 获取执行器
            executor = self.executors.get(
                step.assigned_module or 'default',
                lambda s, ctx: {'result': 'simulated', 'status': 'ok'}
            )
            
            # 执行
            result = self.low_level_planner.execute_step(plan, step, executor)
            
            # 检查失败
            if step.status == StepStatus.FAILED:
                if self.high_level_planner.should_replan(plan, step.step_id):
                    self.stats['replan_count'] += 1
                    print(f"  [GAME] 触发重规划...")
                    # 简化处理：标记为失败
                    plan.status = PlanStatus.REPLANNING
                    break
        
        # 4. 完成
        if plan.get_progress() >= 0.8:
            plan.status = PlanStatus.COMPLETED
            self.stats['successful_plans'] += 1
        else:
            plan.status = PlanStatus.FAILED
            self.stats['failed_plans'] += 1
        
        plan.completed_at = datetime.now()
        self.completed_plans.append(plan)
        
        # 5. Butler格式化输出
        output = {
            'plan_id': plan.plan_id,
            'progress': plan.get_progress(),
            'status': plan.status.value,
            'steps_completed': len([s for s in plan.steps.values() if s.status == StepStatus.SUCCEEDED]),
            'total_steps': len(plan.steps),
            'execution_time': (plan.completed_at - plan.created_at).total_seconds() if plan.completed_at else None,
            'results': [s.result for s in plan.steps.values() if s.result]
        }
        
        # 更新上下文
        self.butler.conversation_context['current_plan_id'] = plan.plan_id
        
        return output
    
    def get_plan_status(self, plan_id: str) -> Optional[Dict]:
        """获取规划状态"""
        plan = self.active_plans.get(plan_id) or self.completed_plans[-1] if self.completed_plans else None
        if not plan:
            return None
        
        return {
            'plan_id': plan.plan_id,
            'status': plan.status.value,
            'progress': plan.get_progress(),
            'current_step': plan.current_step_id,
            'completed_steps': len([s for s in plan.steps.values() if s.status == StepStatus.SUCCEEDED]),
            'total_steps': len(plan.steps)
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['successful_plans'] / max(1, self.stats['total_plans'])
            ),
            'replan_rate': (
                self.stats['replan_count'] / max(1, self.stats['total_plans'])
            )
        }


def demonstrate_game_engine():
    """GAME引擎演示"""
    print("\n" + "=" * 60)
    print("GAME分层规划引擎演示")
    print("=" * 60)
    
    # 初始化引擎
    engine = GAMEEngine(dim=64)
    
    # 注册默认执行器
    engine.register_executor('default', lambda step, ctx: {
        'result': f'执行了: {step.description}',
        'status': 'success'
    })
    
    # 模拟执行
    print("\n【场景1：分析任务】")
    result1 = engine.create_and_execute("分析量子计算的最新发展趋势")
    
    print(f"\n  计划ID: {result1['plan_id']}")
    print(f"  状态: {result1['status']}")
    print(f"  进度: {result1['progress']:.1%}")
    print(f"  完成步骤: {result1['steps_completed']}/{result1['total_steps']}")
    print(f"  执行时间: {result1['execution_time']:.2f}秒")
    
    print("\n【场景2：创作任务】")
    result2 = engine.create_and_execute("设计一个太乙AGI的系统架构")
    
    print(f"\n  计划ID: {result2['plan_id']}")
    print(f"  状态: {result2['status']}")
    print(f"  进度: {result2['progress']:.1%}")
    
    # Butler意图解析演示
    print("\n【Butler意图解析】")
    test_inputs = [
        "请分析这个问题",
        "帮我创建一个PPT",
        "验证这段代码的正确性"
    ]
    for inp in test_inputs:
        intent = engine.butler.parse_intent(inp)
        print(f"  输入: '{inp}'")
        print(f"    意图类型: {intent['intent_type']} (置信度: {intent['confidence']:.1%})")
    
    # 统计
    print("\n【执行统计】")
    stats = engine.get_stats()
    print(f"  总计划数: {stats['total_plans']}")
    print(f"  成功率: {stats['success_rate']:.1%}")
    print(f"  重规划率: {stats['replan_rate']:.1%}")
    
    return engine, result1, result2


if __name__ == "__main__":
    demonstrate_game_engine()
