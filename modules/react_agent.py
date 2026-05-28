#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReAct Agent - 推理-行动-观察循环

实现 ReAct (Reasoning + Acting) 范式：
1. Thought（推理）：LLM分析当前状态，决定下一步
2. Action（行动）：调用工具执行操作
3. Observation（观察）：获取工具返回结果
4. 循环直到得出最终答案

与 NeuroSymbolicReasoner 的关系：
- NeuroSymbolicReasoner：系统1/2思维，处理复杂推理
- ReActAgent：工具调用循环，处理需要多步操作的任务
- 两者可组合：ReActAgent 内部可调用 NeuroSymbolicReasoner
"""

import sys
import os
import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ==================== 数据结构 ====================

class ReActStepType(Enum):
    """ReAct步骤类型"""
    THOUGHT = "Thought"
    ACTION = "Action"
    OBSERVATION = "Observation"
    FINAL_ANSWER = "Final Answer"


@dataclass
class ReActStep:
    """ReAct单步记录"""
    step_type: ReActStepType
    content: str
    timestamp: float = 0.0

    def __str__(self):
        if self.step_type == ReActStepType.THOUGHT:
            return f"🧠 Thought: {self.content}"
        elif self.step_type == ReActStepType.ACTION:
            return f"🔧 Action: {self.content}"
        elif self.step_type == ReActStepType.OBSERVATION:
            return f"👁️ Observation: {self.content[:200]}"
        else:
            return f"✅ Final Answer: {self.content}"


@dataclass
class ReActResult:
    """ReAct执行结果"""
    success: bool
    answer: str
    steps: List[ReActStep] = field(default_factory=list)
    total_steps: int = 0
    error: Optional[str] = None

    def format_trajectory(self) -> str:
        """格式化推理轨迹"""
        lines = ["=" * 60, "ReAct 推理轨迹", "=" * 60]
        for i, step in enumerate(self.steps, 1):
            lines.append(f"\n[Step {i}] {step}")
        lines.append("\n" + "=" * 60)
        lines.append(f"总计步数: {self.total_steps}")
        lines.append(f"成功: {self.success}")
        return "\n".join(lines)


# ==================== ReAct Agent ====================

class ReActAgent:
    """
    ReAct Agent 核心实现

    工作流程：
    1. 接收用户问题
    2. 构建 ReAct 提示词（包含工具列表）
    3. 循环：
       a. LLM 生成 Thought + Action
       b. 解析 Action，调用对应工具
       c. 将 Observation 返回给 LLM
    4. 直到 LLM 输出 "Final Answer" 或达到最大步数
    """

    # ReAct 提示词模板
    REACT_PROMPT_TEMPLATE = """你是一个使用ReAct（推理-行动-观察）范式的AI助手。

可用工具：
{tool_descriptions}

请严格按照以下格式回答：
Thought: [你的推理过程]
Action: [工具名(参数)]  或  Action: Final Answer([最终答案])

示例：
Thought: 我需要执行Python代码来计算这个乘法
Action: python_run(code="print(123 * 456)")
Observation: dict_result
Thought: 得到了计算结果：56088
Action: Final Answer(56088)

重要规则：
1. 每次只能输出一个Thought和一个Action
2. Action必须是可用工具列表中的工具
3. 参数格式必须是标准JSON格式，字符串用双引号
4. 执行Python代码时，必须使用print()输出结果，否则无法获取输出值
5. 当你从Observation中得到答案后，必须在下一个Action中输出Final Answer(答案)，不得再次调用工具
6. 最多{max_steps}步内完成

用户问题：{query}

{history}
"""

    def __init__(self, llm_backend=None, tool_registry=None, max_steps: int = 10):
        """
        初始化ReAct Agent

        Args:
            llm_backend: LLM后端（与taiyi_tools共用）
            tool_registry: 工具注册表（从taiyi_tools导入）
            max_steps: 最大推理步数
        """
        self.llm = llm_backend
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self._llm_initialized = False

    def _ensure_llm(self):
        """延迟加载LLM后端"""
        if not self._llm_initialized:
            try:
                from modules.local_llm import get_llm
                self.llm = get_llm()
                self._llm_initialized = True
            except Exception as e:
                print(f"⚠️ LLM后端初始化失败: {e}")

    def _ensure_tool_registry(self):
        """延迟加载工具注册表"""
        if self.tool_registry is None:
            try:
                from modules.taiyi_tools import get_tool_engine
                self.tool_engine = get_tool_engine()
                self.tool_registry = self.tool_engine.registry
            except ImportError:
                print("⚠️ 无法导入taiyi_tools，工具调用不可用")
                self.tool_registry = None

    def _format_tool_descriptions(self) -> str:
        """格式化工具列表（用于提示词）"""
        if self.tool_registry is None:
            return "（无可用工具）"

        tools = self.tool_registry.list_tools()
        if not tools:
            return "（无可用工具）"

        lines = []
        for tool in tools:
            # tool 是 ToolDefinition 对象
            param_desc = ", ".join([
                f"{p.name}: {p.type}{' (必填)' if p.required else ' (可选)'}"
                for p in tool.parameters
            ])
            lines.append(f"- {tool.name}({param_desc})")
            lines.append(f"  # {tool.description}")
        return "\n".join(lines)

    def _build_prompt(self, query: str, history: str = "") -> str:
        """构建ReAct提示词"""
        tool_desc = self._format_tool_descriptions()
        return self.REACT_PROMPT_TEMPLATE.format(
            tool_descriptions=tool_desc,
            max_steps=self.max_steps,
            query=query,
            history=history
        )

    def _parse_action(self, text: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        解析LLM输出的Action

        支持格式：
        - Action: tool_name(param1="val1", param2="val2")
        - Action: Final Answer(答案内容)

        Returns:
            (tool_name, params_dict) 或 ("Final Answer", answer_string)
        """
        # 匹配 Action: tool_name(...) 格式
        # 使用贪婪匹配到最后一个 ), 然后用 find_matching_close 精确定位
        action_match = re.search(
            r'Action:\s*(\w+)\s*\((.+)\)',
            text,
            re.DOTALL
        )
        if not action_match:
            # 尝试匹配 "Action: Final Answer(...)" （忽略大小写和空白）
            final_action_match = re.search(
                r'Action:\s*Final\s*Answer\s*\((.+)\)',
                text,
                re.DOTALL | re.IGNORECASE
            )
            if final_action_match:
                answer_raw = final_action_match.group(1).strip()
                # 去除可能的引号包裹
                if (answer_raw.startswith('"') and answer_raw.endswith('"')) or \
                   (answer_raw.startswith("'") and answer_raw.endswith("'")):
                    answer_raw = answer_raw[1:-1]
                return "Final Answer", {"answer": answer_raw}
            return None, None

        tool_name = action_match.group(1).strip()
        # 移除末尾多余的 )
        raw = action_match.group(2).strip()
        # 如果最后一个字符是 ) 且前面没有匹配的 (, 去掉它
        if raw.endswith(')') and raw.count('(') == raw.count(')'):
            raw = raw[:-1]

        # 找到平衡的括号对
        def find_matching_close(s: str) -> str:
            """找到匹配的闭括号位置，处理引号内的括号"""
            paren_depth = 0
            in_single = False
            in_double = False
            i = 0
            while i < len(s):
                c = s[i]
                if c == "'" and not in_double:
                    in_single = not in_single
                elif c == '"' and not in_single:
                    in_double = not in_double
                elif c == '(' and not in_single and not in_double:
                    paren_depth += 1
                elif c == ')' and not in_single and not in_double:
                    paren_depth -= 1
                    if paren_depth == 0:
                        return s[:i]
                i += 1
            return s  # 没有找到匹配的括号，返回原字符串

        params_str = find_matching_close(raw)

        # 解析参数
        params = {}
        # 尝试解析 key="value" 格式
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', params_str):
            params[match.group(1)] = match.group(2)
        # 也支持 key='value' 格式
        for match in re.finditer(r"(\w+)\s*=\s*'([^']*)'", params_str):
            params[match.group(1)] = match.group(2)
        # 支持无参数调用
        if not params and params_str:
            # 可能是单个参数
            params = {"input": params_str}

        return tool_name, params

    def _parse_thought(self, text: str) -> str:
        """解析LLM输出的Thought"""
        match = re.search(r'Thought:\s*(.+?)(?=Action:|$)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _execute_action(self, tool_name: str, params: Dict) -> str:
        """
        执行工具调用

        Args:
            tool_name: 工具名称
            params: 参数字典

        Returns:
            工具执行结果（字符串）
        """
        if self.tool_registry is None:
            return f"错误：工具注册表不可用"

        if tool_name == "Final Answer":
            return params.get("answer", "")

        # 查找工具
        tool = self.tool_registry.get_definition(tool_name)
        if tool is None:
            return f"错误：工具 '{tool_name}' 不存在"

        # 执行工具
        try:
            result = self.tool_engine.execute(tool_name, params or {})
            if hasattr(result, 'success'):
                if result.success:
                    return str(result.output) if hasattr(result, 'output') else str(result)
                else:
                    return f"工具执行失败: {result.error if hasattr(result, 'error') else '未知错误'}"
            return str(result)
        except Exception as e:
            return f"工具执行异常: {str(e)}"

    def run(self, query: str) -> ReActResult:
        """
        执行ReAct推理循环

        Args:
            query: 用户问题

        Returns:
            ReActResult: 执行结果
        """
        self._ensure_llm()
        self._ensure_tool_registry()

        if self.llm is None or not hasattr(self.llm, 'active_backend'):
            return ReActResult(
                success=False,
                answer="",
                error="LLM后端不可用",
                steps=[]
            )

        steps = []
        history = ""
        answer = ""

        for step_num in range(1, self.max_steps + 1):
            # 1. 构建提示词
            prompt = self._build_prompt(query, history)
            print(f"\n{'='*60}")
            print(f"ReAct Step {step_num}/{self.max_steps}")
            print(f"{'='*60}")

            # 2. 调用LLM（temperature=0.0 使输出更确定）
            try:
                response = self.llm.generate(
                    prompt,
                    max_tokens=1024,
                    temperature=0.0
                )
            except Exception as e:
                return ReActResult(
                    success=False,
                    answer="",
                    error=f"LLM调用失败: {e}",
                    steps=steps,
                    total_steps=step_num
                )

            print(f"LLM输出:\n{response}\n")

            # 3. 解析Thought
            thought = self._parse_thought(response)
            if thought:
                step = ReActStep(
                    step_type=ReActStepType.THOUGHT,
                    content=thought,
                    timestamp=time.time()
                )
                steps.append(step)
                print(f"🧠 {step}")

            # 4. 解析Action
            action_name, action_params = self._parse_action(response)

            if action_name is None:
                # 未解析到Action，让LLM继续
                history += f"{response}\n"
                continue

            if action_name == "Final Answer":
                # 得到最终答案
                answer = action_params.get("answer", "")
                step = ReActStep(
                    step_type=ReActStepType.FINAL_ANSWER,
                    content=answer,
                    timestamp=time.time()
                )
                steps.append(step)
                print(f"✅ {step}")

                return ReActResult(
                    success=True,
                    answer=answer,
                    steps=steps,
                    total_steps=step_num
                )

            # 5. 执行Action
            observation = self._execute_action(action_name, action_params or {})
            step = ReActStep(
                step_type=ReActStepType.ACTION,
                content=f"{action_name}({action_params})",
                timestamp=time.time()
            )
            steps.append(step)
            print(f"🔧 {step}")

            # 6. 记录Observation
            obs_step = ReActStep(
                step_type=ReActStepType.OBSERVATION,
                content=observation,
                timestamp=time.time()
            )
            steps.append(obs_step)
            print(f"👁️ {obs_step}")

            # 7. 更新history，供下一轮使用
            history += f"{response}\nObservation: {observation}\n"

        # 超过最大步数
        return ReActResult(
            success=False,
            answer="",
            error=f"达到最大步数限制（{self.max_steps}步）",
            steps=steps,
            total_steps=self.max_steps
        )


# ==================== 测试 ====================

def test_react_agent():
    """测试ReAct Agent"""
    print("\n" + "=" * 60)
    print("测试：ReAct Agent（推理-行动-观察循环）")
    print("=" * 60)

    agent = ReActAgent(max_steps=5)

    # 测试问题
    test_queries = [
        "今天北京天气怎么样？",
        "计算 123 * 456",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print(f"{'='*60}")

        result = agent.run(query)

        print(f"\n{'='*60}")
        print(f"执行结果: {'成功' if result.success else '失败'}")
        print(f"答案: {result.answer}")
        print(f"总步数: {result.total_steps}")
        if result.error:
            print(f"错误: {result.error}")
        print(f"{'='*60}")


if __name__ == "__main__":
    test_react_agent()
