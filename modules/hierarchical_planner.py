#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hierarchical Planner - 层次化任务分解器

核心功能：
1. 将复杂任务分解为层次化的子任务
2. 确定子任务之间的依赖关系
3. 生成可执行的任务计划
4. 支持任务优先级和资源约束

与 ReActAgent 的关系：
- HierarchicalPlanner：做高层任务规划（what to do）
- ReActAgent：执行具体的工具调用循环（how to do）
- 两者可组合：HierarchicalPlanner 生成的子任务可以由 ReActAgent 执行
"""

import sys
import os
import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


# ==================== 数据结构 ====================

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"      # 依赖已满足
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # 依赖无法满足


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """任务节点"""
    id: str
    name: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    subtasks: List['Task'] = field(default_factory=list)    # 子任务
    result: Optional[Any] = None
    error: Optional[str] = None
    estimated_duration: int = 0  # 秒
    metadata: Dict = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)


@dataclass
class Plan:
    """执行计划"""
    id: str
    root_task: Task
    all_tasks: List[Task] = field(default_factory=list)
    ready_tasks: List[Task] = field(default_factory=list)   # 可立即执行的任务
    execution_order: List[str] = field(default_factory=list)  # 计划执行顺序
    created_at: float = field(default_factory=time.time)

    def get_task(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.all_tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """获取当前可执行的任务（依赖已满足）"""
        ready = []
        for task in self.all_tasks:
            if task.status == TaskStatus.READY:
                ready.append(task)
        return sorted(ready, key=lambda t: t.priority.value, reverse=True)


# ==================== LLM 辅助函数 ====================

class TaskParser:
    """任务解析器 - 使用LLM辅助解析自然语言任务"""

    DECOMPOSE_PROMPT = """你是一个任务分解专家。请将用户的复杂任务分解为层次化的子任务。

要求：
1. 分解为3-8个子任务
2. 每个子任务应该是原子性的（不可再分）或具有清晰的执行步骤
3. 明确子任务之间的依赖关系
4. 为每个子任务指定合适的优先级

请按以下JSON格式输出（不要包含其他内容）：
{{
    "goal": "高层目标描述",
    "tasks": [
        {{
            "id": "task_1",
            "name": "任务名称",
            "description": "任务详细描述",
            "priority": "normal|high|critical",
            "dependencies": ["task_0"],  // 依赖的其他任务ID
            "estimated_duration": 30  // 预计执行时间（秒）
        }}
    ]
}}

用户任务：{query}
"""

    @classmethod
    def decompose(cls, query: str, llm_backend=None) -> Dict:
        """分解任务"""
        if llm_backend is None:
            try:
                from modules.local_llm import get_llm
                llm_backend = get_llm()
            except Exception:
                return cls._fallback_decompose(query)

        try:
            prompt = cls.DECOMPOSE_PROMPT.format(query=query)
            response = llm_backend.generate(prompt, max_tokens=2048, temperature=0.3)
            return cls._parse_llm_response(response)
        except Exception as e:
            print(f"LLM分解失败: {e}，使用fallback")
            return cls._fallback_decompose(query)

    @classmethod
    def _fallback_decompose(cls, query: str) -> Dict:
        """简单任务分解（无LLM时）"""
        # 简单策略：按关键词拆分
        keywords = ["首先", "然后", "接着", "最后", "第一步", "第二步", "第三步"]
        sentences = [query]

        for kw in keywords:
            new_sentences = []
            for s in sentences:
                parts = s.split(kw)
                for i, part in enumerate(parts):
                    if part.strip():
                        new_sentences.append(part.strip())
                    if i < len(parts) - 1:
                        new_sentences.append(kw)
            if len(new_sentences) > len(sentences):
                sentences = new_sentences

        tasks = []
        for i, s in enumerate(sentences[:8]):  # 最多8个
            if not s.strip():
                continue
            tasks.append({
                "id": f"task_{i}",
                "name": f"步骤{i+1}",
                "description": s.strip(),
                "priority": "normal",
                "dependencies": [f"task_{i-1}"] if i > 0 else [],
                "estimated_duration": 60
            })

        if not tasks:
            tasks = [{
                "id": "task_0",
                "name": query[:50],
                "description": query,
                "priority": "normal",
                "dependencies": [],
                "estimated_duration": 120
            }]

        return {"goal": query, "tasks": tasks}

    @classmethod
    def _parse_llm_response(cls, response: str) -> Dict:
        """解析LLM输出"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

        # 尝试简单解析
        return cls._fallback_decompose(response.split("用户任务")[0] if "用户任务" in response else response)


# ==================== 依赖图分析 ====================

class DependencyGraph:
    """依赖图分析器"""

    @staticmethod
    def build_graph(tasks: List[Dict]) -> Dict[str, Set[str]]:
        """构建依赖图（邻接表）"""
        graph = defaultdict(set)
        for task in tasks:
            task_id = task["id"]
            for dep in task.get("dependencies", []):
                graph[dep].add(task_id)  # dep -> task (task depends on dep)
        return graph

    @staticmethod
    def topological_sort(tasks: List[Dict]) -> List[List[str]]:
        """
        拓扑排序，返回分层执行顺序
        每层内的任务可以并行执行
        """
        # 构建图
        task_ids = {t["id"] for t in tasks}
        in_degree = {t["id"]: 0 for t in tasks}
        graph = defaultdict(list)

        for task in tasks:
            task_id = task["id"]
            for dep in task.get("dependencies", []):
                if dep in task_ids:  # 只考虑有效依赖
                    graph[dep].append(task_id)
                    in_degree[task_id] += 1

        # Kahn算法
        layers = []
        current = [tid for tid, deg in in_degree.items() if deg == 0]

        while current:
            layers.append(sorted(current))
            next_layer = []
            for tid in current:
                for neighbor in graph[tid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_layer.append(neighbor)
            current = next_layer

        return layers

    @staticmethod
    def detect_cycles(tasks: List[Dict]) -> bool:
        """检测循环依赖"""
        task_ids = {t["id"] for t in tasks}
        visited = set()
        rec_stack = set()

        def dfs(tid: str) -> bool:
            visited.add(tid)
            rec_stack.add(tid)

            for task in tasks:
                if task["id"] == tid:
                    for dep in task.get("dependencies", []):
                        if dep not in task_ids:
                            continue
                        if dep not in visited:
                            if dfs(dep):
                                return True
                        elif dep in rec_stack:
                            return True

            rec_stack.remove(tid)
            return False

        for task in tasks:
            if task["id"] not in visited:
                if dfs(task["id"]):
                    return True
        return False


# ==================== 层次化规划器 ====================

class HierarchicalPlanner:
    """
    层次化任务规划器

    工作流程：
    1. 解析用户任务（LLM辅助）
    2. 构建任务依赖图
    3. 检测循环依赖
    4. 拓扑排序确定执行顺序
    5. 生成可执行计划

    特点：
    - 支持多层级任务（任务可以有子任务）
    - 自动处理依赖关系
    - 支持任务优先级调度
    """

    def __init__(self, llm_backend=None):
        self.llm = llm_backend
        self._llm_initialized = False

    def _ensure_llm(self):
        """延迟加载LLM"""
        if not self._llm_initialized:
            try:
                from modules.local_llm import get_llm
                self.llm = get_llm()
                self._llm_initialized = True
            except Exception:
                pass

    def plan(self, query: str) -> Plan:
        """
        生成任务执行计划

        Args:
            query: 用户任务描述

        Returns:
            Plan: 可执行计划
        """
        self._ensure_llm()

        # 1. 任务分解
        decomposition = TaskParser.decompose(query, self.llm)

        # 2. 构建任务对象
        tasks = []
        for task_dict in decomposition.get("tasks", []):
            task = Task(
                id=task_dict["id"],
                name=task_dict["name"],
                description=task_dict.get("description", ""),
                priority=TaskPriority[task_dict.get("priority", "NORMAL").upper()],
                dependencies=task_dict.get("dependencies", []),
                estimated_duration=task_dict.get("estimated_duration", 60)
            )
            tasks.append(task)

        # 3. 构建根任务
        root = Task(
            id="root",
            name=decomposition.get("goal", query[:50]),
            description=query,
            subtasks=tasks
        )

        # 4. 创建计划
        plan = Plan(
            id=f"plan_{int(time.time())}",
            root_task=root,
            all_tasks=tasks + [root]
        )

        # 5. 拓扑排序
        layers = DependencyGraph.topological_sort(decomposition.get("tasks", []))
        for layer in layers:
            plan.execution_order.extend(layer)

        # 6. 检测循环依赖
        if DependencyGraph.detect_cycles(decomposition.get("tasks", [])):
            print("⚠️ 警告：检测到循环依赖")

        # 7. 标记READY状态的任务
        ready_ids = set()
        for layer in layers:
            if layer:  # 第一层
                ready_ids.update(layer)

        for task in tasks:
            if not task.dependencies or all(d in ready_ids for d in task.dependencies):
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.READY

        plan.ready_tasks = [t for t in tasks if t.status == TaskStatus.READY]

        return plan

    def update_plan(self, plan: Plan, completed_task_id: str, result: Any = None, error: str = None) -> Plan:
        """
        更新计划状态

        Args:
            plan: 当前计划
            completed_task_id: 已完成任务ID
            result: 任务结果
            error: 任务错误

        Returns:
            更新后的计划
        """
        task = plan.get_task(completed_task_id)
        if not task:
            return plan

        if error:
            task.status = TaskStatus.FAILED
            task.error = error
        else:
            task.status = TaskStatus.COMPLETED
            task.result = result

        # 更新依赖此任务的其他任务
        for t in plan.all_tasks:
            if completed_task_id in t.dependencies:
                # 检查是否所有依赖都已完成
                all_deps_done = all(
                    plan.get_task(dep).status == TaskStatus.COMPLETED
                    for dep in t.dependencies
                    if plan.get_task(dep)
                )
                if all_deps_done and t.status == TaskStatus.PENDING:
                    t.status = TaskStatus.READY

        # 重新计算ready_tasks
        plan.ready_tasks = [t for t in plan.all_tasks if t.status == TaskStatus.READY]

        return plan

    def format_plan(self, plan: Plan) -> str:
        """格式化计划为可读文本"""
        lines = ["=" * 60, "📋 任务执行计划", "=" * 60]
        lines.append(f"\n🎯 目标: {plan.root_task.name}")
        lines.append(f"📊 任务总数: {len(plan.all_tasks) - 1}")

        layers = DependencyGraph.topological_sort([
            {"id": t.id, "dependencies": t.dependencies}
            for t in plan.all_tasks if t.id != "root"
        ])

        for i, layer in enumerate(layers):
            lines.append(f"\n{'─' * 40}")
            lines.append(f"📦 层级 {i + 1}（可并行执行）:")
            for tid in layer:
                task = plan.get_task(tid)
                if task:
                    status_icon = {
                        TaskStatus.PENDING: "⏳",
                        TaskStatus.READY: "✅",
                        TaskStatus.RUNNING: "🔄",
                        TaskStatus.COMPLETED: "✅",
                        TaskStatus.FAILED: "❌",
                        TaskStatus.BLOCKED: "🚫",
                    }.get(task.status, "❓")

                    priority_icon = {
                        TaskPriority.LOW: "🔽",
                        TaskPriority.NORMAL: "▫️",
                        TaskPriority.HIGH: "🔼",
                        TaskPriority.CRITICAL: "🔥",
                    }.get(task.priority, "▫️")

                    deps_str = f" (依赖: {', '.join(task.dependencies)})" if task.dependencies else ""
                    lines.append(f"  {status_icon} {priority_icon} [{task.id}] {task.name}{deps_str}")

        lines.append(f"\n{'=' * 60}")
        lines.append(f"总预计时间: {sum(t.estimated_duration for t in plan.all_tasks if t.id != 'root') // 60} 分钟")
        return "\n".join(lines)


# ==================== 测试 ====================

def test_hierarchical_planner():
    """测试层次化规划器"""
    print("\n" + "=" * 60)
    print("测试：Hierarchical Planner（层次化任务分解）")
    print("=" * 60)

    planner = HierarchicalPlanner()

    test_queries = [
        "帮我分析一下腾讯最近的财务状况，包括收入、利润和用户增长数据",
        "写一个Python程序，实现快速排序算法，并测试其性能",
        "调查一下特斯拉股票的近期走势，预测下周的表现"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print(f"{'='*60}")

        plan = planner.plan(query)
        print(planner.format_plan(plan))


if __name__ == "__main__":
    test_hierarchical_planner()
