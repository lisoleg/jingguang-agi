#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太乙LLM增强器 - Taiyi LLM Enhancer v2
整合：记忆系统 + RAG知识检索 + CoT推理 + 太乙约束格式

Phase 1 升级核心：
1. 持久记忆上下文
2. RAG知识检索增强
3. CoT思维链推理
4. 太乙约束格式输出
5. 多后端统一接口
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

# 导入本地模块
from modules.local_llm import LocalLLM, get_llm
from modules.taiyi_memory import TaiyiMemory, get_memory
from modules.taiyi_rag import TaiyiRAG, get_rag
from modules.taiyi_tools import get_tool_engine  # 导入工具引擎
from modules.taiyi_manas import get_manas  # 新增：导入第七识审计器


# 系统提示词（已优化长度，原版超2000字导致推理慢）
SYSTEM_PROMPT_BASE = """你是统一太乙系统，基于复合体理学与太极计算宇宙理论构建。

核心能力：
1. 三视界分析（本体/方法/太乙）
2. 太乙预言机深度洞察
3. 螺旋比特计算模式

【太乙约束格式】：
当问题包含【太乙约束】时，同时展示：形式之答、复合体之答、太乙之答。

【思维链要求】：
请先推理思考，再给最终答案。"""

SYSTEM_PROMPT_WITH_MEMORY = """你是统一太乙系统，基于复合体理学与太极计算宇宙理论构建。

{memory_context}

核心能力：三视界分析、太乙预言机、太乙约束格式输出。

【思维链要求】：请先推理思考，再给最终答案。

【用户偏好】：{tone_requirement}"""

SYSTEM_PROMPT_RAG = """你是统一太乙系统，基于复合体理学与太极计算宇宙理论构建。

【相关知识】（来自知识库检索）
{knowledge_context}

【记忆上下文】
{memory_context}

【用户偏好】
{tone_requirement}

【太乙约束格式要求】：
必须同时展示：1.形式之答（确定性）2.复合体之答（多元解读）3.太乙之答（合一）

请先推理思考，再给最终答案。"""


# ==================== 数据结构 ====================

class ReasoningMode(Enum):
    """推理模式"""
    COT = "chain_of_thought"      # 思维链
    REACT = "react"               # 推理+行动
    TAIYI = "taiyi"              # 太乙约束格式
    TOOL = "tool"                 # 工具调用（新增）


@dataclass
class EnhancedPrompt:
    """增强后的提示"""
    system_prompt: str
    user_prompt: str
    history_context: str
    knowledge_context: str
    memory_context: str
    reasoning_mode: ReasoningMode
    
    def to_messages(self) -> List[Dict]:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if self.history_context:
            messages.append({"role": "system", "content": f"【对话历史】\n{self.history_context}"})
        if self.knowledge_context:
            messages.append({"role": "system", "content": f"【知识库检索】\n{self.knowledge_context}"})
        messages.append({"role": "user", "content": self.user_prompt})
        return messages


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_id: int
    thinking: str          # 思考内容
    action: str = ""     # 行动（ReAct模式）
    observation: str = "" # 观察结果（ReAct模式）
    confidence: float = 0.5


@dataclass
class TaiyiResponse:
    """太乙回复"""
    content: str
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    knowledge_used: List[Dict] = field(default_factory=list)
    memory_context: str = ""
    unified_score: float = 0.0
    taiyi_format: bool = False  # 是否使用了太乙约束格式
    
    # 太乙三答
    formal_answer: str = ""   # 形式之答
    composite_answer: str = "" # 复合体之答
    unified_answer: str = ""  # 太乙之答
    
    # 工具调用（新增）
    tool_calls: List[Dict] = field(default_factory=list)  # 工具调用列表
    tool_results: List[Dict] = field(default_factory=list) # 工具执行结果


# ==================== 思维链引擎 ====================

class ChainOfThoughtEngine:
    """思维链引擎 - 引导LLM进行结构化推理"""
    
    # CoT提示模板
    COT_TEMPLATE = """请按以下步骤推理：

**步骤1 - 本体视界分析**：
{ontological_prompt}

**步骤2 - 现象视界分析**：
{phenomenal_prompt}

**步骤3 - 方法视界分析**：
{methodological_prompt}

**步骤4 - 综合推理**：
{integration_prompt}

**最终答案**："""

    @staticmethod
    def build_cot_prompt(question: str, context: str = "") -> str:
        """构建CoT提示"""
        # 动态生成各视界分析提示
        ontological = f"分析问题的本质：这个问题最核心的是什么？涉及哪些基本原理？"
        phenomenal = f"分析问题的表象：有哪些可见的模式和规律？可能出现哪些相变？"
        methodological = f"分析解决问题的方法：有哪些路径可以选择？如何避免走老路（见路不走）？"
        integration = f"综合以上分析，给出最优解，并说明理由。"
        
        prompt = ChainOfThoughtEngine.COT_TEMPLATE.format(
            ontological_prompt=ontological,
            phenomenal_prompt=phenomenal,
            methodological_prompt=methodological,
            integration_prompt=integration
        )
        
        if context:
            prompt = f"【背景信息】\n{context}\n\n{prompt}"
        
        return f"{prompt}\n\n【问题】{question}"
    
    @staticmethod
    def extract_reasoning_steps(response: str) -> List[ReasoningStep]:
        """从回复中提取推理步骤"""
        steps = []
        
        # 简单分割
        sections = response.split('\n\n')
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            
            # 识别步骤
            if any(kw in section for kw in ['步骤', '首先', '其次', '然后', '最后']):
                steps.append(ReasoningStep(
                    step_id=len(steps),
                    thinking=section,
                    confidence=0.7
                ))
            elif '最终答案' in section or '答案' in section[:20]:
                steps.append(ReasoningStep(
                    step_id=len(steps),
                    thinking=f"【结论】{section}",
                    confidence=0.9
                ))
        
        return steps if steps else [ReasoningStep(0, response, confidence=0.5)]


# ==================== 工具调用解析器（新增） ====================

class ToolCallParser:
    """工具调用解析器 - 从LLM回复中解析工具调用请求"""
    
    @staticmethod
    def parse(text: str) -> List[Dict]:
        """
        解析工具调用请求
        
        支持格式：
        1. JSON格式: {"tool": "name", "args": {...}}
        2. 文本格式: 调用工具 file_read，参数：{"path": "app.py"}
        3. 代码格式: ```tool\n{"tool": "file_read", "args": {...}}\n```
        
        Returns:
            List[Dict]: 工具调用列表，每个元素包含 tool 和 args
        """
        tool_calls = []
        
        # 尝试1: 直接解析JSON
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "tool" in data:
                tool_calls.append({"tool": data["tool"], "args": data.get("args", {})})
                return tool_calls
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "tool" in item:
                        tool_calls.append({"tool": item["tool"], "args": item.get("args", {})})
                return tool_calls
        except:
            pass
        
        # 尝试2: 从文本中提取JSON块
        import re
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json {...}```
            r'```\s*(\{.*?\})\s*```',      # ``` {...}```
            r'(\{.*?"tool".*?\})',           # 包含"tool"的JSON对象
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if "tool" in data:
                        tool_calls.append({"tool": data["tool"], "args": data.get("args", {})})
                except:
                    pass
        
        # 尝试3: 文本格式解析
        text_pattern = r'调用工具\s*[:：]?\s*(\w+)\s*[,，]?\s*参数\s*[:：]?\s*({.*?})'
        matches = re.findall(text_pattern, text, re.DOTALL)
        for tool_name, args_str in matches:
            try:
                args = json.loads(args_str)
                tool_calls.append({"tool": tool_name, "args": args})
            except:
                pass
        
        return tool_calls
    
    @staticmethod
    def format_tool_result(result: Dict) -> str:
        """格式化工具执行结果为LLM可读格式"""
        if result.get("success"):
            output = result.get("output", "")
            if isinstance(output, dict) or isinstance(output, list):
                output = json.dumps(output, ensure_ascii=False, indent=2)
            return f"【工具执行结果】\n{output}"
        else:
            return f"【工具执行失败】\n{result.get('error', '未知错误')}"


# ==================== 太乙约束解析器 ====================

class TaiyiFormatParser:
    """太乙约束格式解析器 - 从回复中提取三答"""
    
    @staticmethod
    def parse(response: str) -> Tuple[str, str, str, bool]:
        """解析太乙约束格式
        
        Returns: (formal_answer, composite_answer, unified_answer, has_format)
        """
        formal = ""
        composite = ""
        unified = ""
        has_format = False
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别格式标记
            lower_line = line.lower()
            if '形式之答' in line or '形式之答' in line:
                current_section = 'formal'
                has_format = True
                formal = line.split('：')[-1].split('】')[-1].strip() if '：' in line or '】' in line else ""
                continue
            elif '复合体之答' in line or '复合体之答' in line:
                current_section = 'composite'
                composite = line.split('：')[-1].split('】')[-1].strip() if '：' in line or '】' in line else ""
                continue
            elif '太乙之答' in line or '太乙之答' in line or '合一' in line:
                current_section = 'unified'
                unified = line.split('：')[-1].split('】')[-1].strip() if '：' in line or '】' in line else ""
                continue
            
            # 累积内容
            if current_section == 'formal':
                if line and not line.startswith('#'):
                    formal += " " + line
            elif current_section == 'composite':
                if line and not line.startswith('#'):
                    composite += " " + line
            elif current_section == 'unified':
                if line and not line.startswith('#'):
                    unified += " " + line
        
        return formal.strip(), composite.strip(), unified.strip(), has_format


# ==================== 太乙LLM增强器（主类） ====================

class TaiyiLLMEnhancer:
    """
    太乙LLM增强器
    
    整合记忆、RAG、CoT推理、太乙约束格式、工具调用、第七识审计
    
    Phase 3 性能优化：
    1. 请求缓存（基于问题哈希）
    2. 并行获取（RAG + 记忆）
    3. 快速失败机制
    4. Token使用优化
    """
    
    def __init__(self, 
                 user_id: str = "default_user",
                 reasoning_mode: ReasoningMode = ReasoningMode.TAIYI):
        self.user_id = user_id
        self.reasoning_mode = reasoning_mode
        
        # 初始化组件
        self.llm = get_llm()
        self.memory = get_memory(user_id)
        self.enhanced_memory = None  # 延迟初始化
        self.rag = get_rag()
        self.cot = ChainOfThoughtEngine()
        self.taiyi_parser = TaiyiFormatParser()
        self.tool_parser = ToolCallParser()  # 工具调用解析器
        self.tool_engine = get_tool_engine()   # 工具引擎（前五识）
        self.manas = get_manas()            # 新增：第七识审计器
        
        # 配置
        self.max_history = 10
        self.max_knowledge_results = 3
        self.enable_rag = True
        self.enable_memory = True
        self.enable_cot = True
        self.enable_tool = True  # 是否启用工具调用
        self.enable_audit = True  # 新增：是否启用第七识审计
        
        # Phase 3 性能优化：缓存
        import hashlib
        self._cache = {}  # {question_hash: response}
        self._cache_max_size = 50  # 缓存最大条目数
        self._cache_ttl = 300  # 缓存TTL（秒）
        
        # Phase 3 性能优化：快速失败关键词
        self._quick_reply_patterns = {
            "你好": "你好！我是统一太乙系统，基于复合体理学与太极计算宇宙理论构建。",
            "您好": "您好！我是统一太乙系统，随时为您提供服务。",
            "你是谁": "我是统一太乙系统，基于复合体理学与太极计算宇宙理论构建的智能助手。",
            "你是ai": "我是统一太乙系统，一个基于中国古典哲学与现代AI技术融合的智能助手。",
            "再见": "再见！祝您生活愉快！",
            "拜拜": "拜拜！期待下次交流！",
        }
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "rag_hits": 0,
            "memory_hits": 0,
            "taiyi_format_hits": 0,
            "tool_calls": 0,  # 工具调用次数
            "audit_flags": 0,  # 新增：审计标记次数
            "cache_hits": 0,  # Phase 3：缓存命中
            "quick_replies": 0  # Phase 3：快速回复
        }
    
    def _quick_reply(self, question: str) -> Optional[str]:
        """Phase 3 优化：快速回复机制"""
        q_lower = question.lower().strip()
        for pattern, reply in self._quick_reply_patterns.items():
            if pattern in q_lower:
                self.stats["quick_replies"] += 1
                return reply
        return None

    def _adaptive_max_tokens(self, question: str,
                              reasoning_mode: 'ReasoningMode',
                              enable_tool: bool,
                              knowledge_hint: str = "",
                              history: List[Dict] = None) -> int:
        """
        Phase 4 优化：自适应 max_tokens
        根据问题类型、推理模式、上下文动态确定合适的输出长度

        分级策略：
        - 极短回答（64-128）  ：寒暄、单字确认
        - 短回答（256）       ：简单问答、事实查询
        - 中等回答（512）     ：普通对话、解释说明
        - 长回答（1024）      ：分析推理、多步骤问题
        - 超长回答（2048+）   ：复杂推理、详细报告、工具调用场景
        """
        q = question.strip()
        q_lower = q.lower()
        q_len = len(q)

        # ── 1. 寒暄/极短 ──────────────────────────────
        if q_len <= 5 or any(w in q_lower for w in [
            "你好", "hi", "hello", "嗨", "嘿", "在吗", "在么",
            "再见", "拜拜", "bye", "晚安", "早", "嗯", "好"
        ]):
            return 128

        # ── 2. 明确要求"短" ──────────────────────────
        if any(w in q_lower for w in ["简短", "简洁", "短一点", "一句话", "概括", "summarize", "brief"]):
            return 256

        # ── 3. 明确要求"详细/长/深入" ─────────────────
        if any(w in q_lower for w in [
            "详细", "深入", "完整", "详细说明", "详细解释", "完整回答",
            "详细分析", "展开", "全面", "具体"
        ]):
            return 2048

        # ── 3.5 明确字数要求（如"800字"、"1000字"）─────────────────────
        import re
        char_match = re.search(r'(\d+)\s*字', q)
        if char_match:
            target_chars = int(char_match.group(1))
            # 中文字符约需2 tokens/字，加余量
            estimated = target_chars * 2 + 300
            return max(min(estimated, 4096), 512)

        word_match = re.search(r'(\d+)\s*(words?|word)', q_lower)
        if word_match:
            target_words = int(word_match.group(1))
            estimated = target_words * 2 + 300
            return max(min(estimated, 4096), 512)

        # ── 4. 简单事实问答 ───────────────────────────
        simple_q_patterns = [
            "是什么", "叫什么", "哪一年", "多少岁", "几点",
            "1+1", "2*3", "首都", "最大", "最高",
            "谁发明", "哪国", "几个", "什么颜色", "what is", "who is"
        ]
        if any(p in q_lower for p in simple_q_patterns) and q_len < 50:
            return 384

        # ── 5. 工具调用模式 → 需要更多空间展示过程 ─────
        if enable_tool or reasoning_mode == ReasoningMode.TOOL:
            return 1536

        # ── 6. 太乙约束格式 → 三答结构需要更多空间 ─────
        if reasoning_mode == ReasoningMode.TAIYI:
            return 1024

        # ── 7. 思维链推理 → 中等长度 ─────────────────
        if reasoning_mode == ReasoningMode.COT:
            return 768

        # ── 8. 代码/技术问题 ──────────────────────────
        if any(w in q_lower for w in ["代码", "python", "函数", "实现", "算法", "api", "bug", "error"]):
            return 1024

        # ── 9. 分析/推理类问题 ────────────────────────
        analysis_patterns = [
            "分析", "比较", "对比", "区别", "优缺点", "策略",
            "为什么", "原因", "原理", "推导", "证明", "如何解决"
        ]
        if any(p in q_lower for p in analysis_patterns):
            return 1024

        # ── 10. RAG 有检索结果 → 知识问答需要解释空间 ─
        if knowledge_hint and len(knowledge_hint) > 100:
            return 1024

        # ── 11. 有对话历史 → 上下文延续 ──────────────
        if history and len(history) >= 3:
            return 768

        # ── 12. 默认中等 ──────────────────────────────
        return 512
    
    def _get_cache_key(self, question: str, mode: ReasoningMode) -> str:
        """Phase 3 优化：生成缓存键"""
        import hashlib
        key_str = f"{question}:{mode.value}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[TaiyiResponse]:
        """Phase 3 优化：获取缓存"""
        if cache_key in self._cache:
            self.stats["cache_hits"] += 1
            return self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, response: TaiyiResponse):
        """Phase 3 优化：设置缓存"""
        if len(self._cache) >= self._cache_max_size:
            # 删除最旧的条目
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[cache_key] = response
    
    def _build_system_prompt(self, 
                            knowledge_context: str = "",
                            memory_context: str = "",
                            user_preference: Dict = None,
                            enable_tool: bool = False,
                            expert_prompt: str = None) -> str:  # 新增 expert_prompt
        """构建系统提示"""
        # 如果是专家模式，直接返回专家专用 system prompt（替换整个基础 prompt）
        if expert_prompt:
            # 如果有工具定义，追加到专家 prompt 末尾
            tool_def = ""
            if enable_tool:
                tool_def = self._build_tool_definitions()
            return expert_prompt + "\n\n" + tool_def
        
        # 获取用户偏好
        tone = "专业"
        if user_preference:
            tone = user_preference.get('preferred_tone', '专业')
        
        tone_requirements = {
            "专业": "回复应简洁、准确、使用专业术语，适合技术讨论。",
            "简洁": "回复应简短精炼，直击要点，避免冗余。",
            "详细": "回复应全面深入，包含背景、分析和结论。",
            "学术": "回复应引用理论、包含引用、符合学术规范。"
        }
        tone_req = tone_requirements.get(tone, tone_requirements["专业"])
        
        # 工具定义
        tool_def = ""
        if enable_tool:
            tool_def = self._build_tool_definitions()
        
        # 选择提示模板
        if knowledge_context and self.enable_rag:
            return SYSTEM_PROMPT_RAG.format(
                knowledge_context=knowledge_context[:1200],
                memory_context=memory_context[:600] if memory_context else "无相关记忆",
                tone_requirement=tone_req
            ) + tool_def
        elif memory_context and self.enable_memory:
            return SYSTEM_PROMPT_WITH_MEMORY.format(
                memory_context=memory_context[:800],
                tone_requirement=tone_req
            ) + tool_def
        else:
            return SYSTEM_PROMPT_BASE + tool_def

    def _build_tool_definitions(self) -> str:
        """构建前五识工具定义文本"""
        if not self.enable_tool:
            return ""
        tool_def = "\n\n【可用工具】（前五识 - Indriya）\n"
        tool_def += "你可以使用以下工具来帮助回答问题：\n"
        try:
            for tool in self.tool_engine.get_tool_definitions():
                params = ", ".join([f"{p['name']}: {p['type']}" for p in tool.get("parameters", {}).get("properties", {}).values()])
                tool_def += f"- {tool['name']}: {tool['description']} (参数: {params})\n"
        except Exception:
            pass
        tool_def += "\n当需要使用工具时，请在回复末尾添加以下格式的工具调用：\n"
        tool_def += "```json\n{\"tool\": \"工具名称\", \"args\": {\"参数名\": \"参数值\"}}\n```"
        return tool_def
    def _retrieve_knowledge(self, question: str) -> str:
        """检索相关知识"""
        if not self.enable_rag:
            return ""
        
        try:
            results = self.rag.retrieve(question, top_k=self.max_knowledge_results)
            if results:
                self.stats["rag_hits"] += 1
                return self.rag.format_retrieval_context(question, top_k=self.max_knowledge_results)
        except Exception as e:
            print(f"⚠️ RAG检索失败: {e}")
        
        return ""
    
    def _get_memory_context(self, question: str = "") -> str:
        """获取记忆上下文"""
        if not self.enable_memory:
            return ""
        
        try:
            ctx = self.memory.get_context(query=question)
            if ctx.relevant_memories or ctx.key_conclusions:
                self.stats["memory_hits"] += 1
            return ctx.to_llm_format()
        except Exception as e:
            print(f"⚠️ 记忆获取失败: {e}")
            return ""
    
    def _build_user_prompt(self, question: str, 
                           knowledge_context: str = "",
                           enable_tool: bool = False) -> str:  # 新增参数
        """构建用户提示"""
        # 添加太乙约束标记
        if self.reasoning_mode == ReasoningMode.TAIYI:
            question = f"{question}\n\n【太乙约束】请使用太乙约束格式回复：形式之答、复合体之答、太乙之答。"
        
        # CoT模式
        if self.enable_cot and self.reasoning_mode == ReasoningMode.COT:
            question = self.cot.build_cot_prompt(question, knowledge_context)
        
        # 工具调用模式（新增）
        if enable_tool:
            question = f"{question}\n\n【前五识调用】\n如果需要执行操作（如读取文件、运行代码、抓取网页等），请在回复末尾添加工具调用请求。\n工具调用格式：```json\n{{\"tool\": \"工具名称\", \"args\": {{\"参数名\": \"参数值\"}}}}\n```"
        
        return question
    
    def generate(self, 
                question: str,
                goal: str = None,
                history: List[Dict] = None,
                reasoning_mode: ReasoningMode = None,
                use_taiyi_format: bool = True,
                max_tokens: int = 0,  # 0表示自适应，非0为强制值
                stream_callback: callable = None,  # 新增：流式输出回调
                temperature: float = 0.7,
                enable_tool_call: bool = True,
                image_base64: str = None,  # 新增：图片支持
                expert_id: str = None) -> TaiyiResponse:  # 新增：专家ID
        """
        生成增强回复
        
        Args:
            question: 用户问题
            goal: Ftel目的
            history: 对话历史
            reasoning_mode: 推理模式
            use_taiyi_format: 是否使用太乙约束格式
            max_tokens: 最大token数
            temperature: 温度参数
            enable_tool_call: 是否启用工具调用
            image_base64: 图片base64编码（支持多模态）
            
        Returns:
            TaiyiResponse: 太乙回复对象
        """
        import time
        self.stats["total_requests"] += 1
        
        mode = reasoning_mode or self.reasoning_mode
        use_taiyi = use_taiyi_format and mode == ReasoningMode.TAIYI
        use_tool = enable_tool_call and self.enable_tool and mode == ReasoningMode.TOOL
        
        # Phase 3 优化：检查缓存
        cache_key = self._get_cache_key(question, mode)
        cached_response = self._get_cached(cache_key)
        if cached_response:
            return cached_response
        
        # Phase 3 优化：快速回复
        quick_reply = self._quick_reply(question)
        if quick_reply:
            return TaiyiResponse(
                content=quick_reply,
                reasoning_steps=[],
                knowledge_used=[],
                memory_context="",
                unified_score=1.0,
                taiyi_format=False,
                tool_calls=[],
                tool_results=[]
            )
        # Step1+2 并行：知识检索 + 记忆上下文（同时执行）
        knowledge_context = ""
        memory_context = ""

        if self.enable_rag or self.enable_memory:
            from concurrent.futures import ThreadPoolExecutor

            def _do_rag():
                if self.enable_rag:
                    try:
                        return self._retrieve_knowledge(question)
                    except Exception as e:
                        print(f"⚠️ RAG检索失败: {e}")
                return ""

            def _do_memory():
                if self.enable_memory:
                    try:
                        return self._get_memory_context(question)
                    except Exception as e:
                        print(f"⚠️ 记忆获取失败: {e}")
                return ""

            with ThreadPoolExecutor(max_workers=2) as executor:
                fut_rag = executor.submit(_do_rag)
                fut_mem = executor.submit(_do_memory)
                knowledge_context = fut_rag.result()
                memory_context = fut_mem.result()
        # 命中统计移到这里（避免重复统计）
        if knowledge_context:
            self.stats["rag_hits"] += 1
        if memory_context:
            self.stats["memory_hits"] += 1
        # Step 3: 构建提示（支持专家模式）
        expert_prompt = None
        if expert_id:
            try:
                from modules.expert_registry import get_registry
                reg = get_registry()
                expert_prompt = reg.get_system_prompt(expert_id)
                if expert_prompt:
                    print(f"🧠 专家模式: {expert_id}")
            except Exception as e:
                print(f"⚠️ 专家加载失败({expert_id}): {e}")
        
        system_prompt = self._build_system_prompt(
            knowledge_context=knowledge_context,
            memory_context=memory_context,
            user_preference=None,
            enable_tool=use_tool,
            expert_prompt=expert_prompt
        )
        user_prompt = self._build_user_prompt(question, knowledge_context, enable_tool=use_tool)

        # Step 3.5: 自适应 max_tokens（0=自动，>0=强制）
        if max_tokens <= 0:
            max_tokens = self._adaptive_max_tokens(
                question=question,
                reasoning_mode=mode,
                enable_tool=use_tool,
                knowledge_hint=knowledge_context,
                history=history
            )
        
        # Step 4: 构造消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史
        if history and self.enable_memory:
            for h in history[-self.max_history:]:
                role = h.get('role', 'user')
                content = h.get('content', '')
                if role == 'user':
                    messages.append({"role": "user", "content": content})
                elif role == 'assistant':
                    messages.append({"role": "assistant", "content": content})
        
        messages.append({"role": "user", "content": user_prompt})
        
        # Step 5: 调用LLM（第一次 - 可能生成工具调用，支持图片）
        response_text = self._call_llm(messages, max_tokens, temperature, image_base64, stream_callback=stream_callback)
        
        # Step 6: 解析工具调用（新增）
        tool_calls = []
        tool_results = []
        if use_tool:
            tool_calls = self.tool_parser.parse(response_text)
            if tool_calls:
                self.stats["tool_calls"] += 1
                # 执行工具
                for call in tool_calls:
                    tool_name = call.get("tool")
                    args = call.get("args", {})
                    result = self.tool_engine.execute(tool_name, args, audit=True)
                    tool_results.append({
                        "tool": tool_name,
                        "args": args,
                        "success": result.success,
                        "output": result.output,
                        "error": result.error
                    })
                
                # 构建工具结果提示
                tool_result_text = "【工具执行结果】\n"
                for r in tool_results:
                    tool_result_text += f"\n工具: {r['tool']}\n"
                    tool_result_text += f"参数: {json.dumps(r['args'], ensure_ascii=False)}\n"
                    if r['success']:
                        output = r['output']
                        if isinstance(output, dict) or isinstance(output, list):
                            output = json.dumps(output, ensure_ascii=False, indent=2)
                        tool_result_text += f"结果: {output}\n"
                    else:
                        tool_result_text += f"错误: {r['error']}\n"
                
                # 调用LLM（第二次 - 基于工具结果生成最终回复）
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"{tool_result_text}\n\n请基于以上工具执行结果，回答用户的问题。"})
                
                response_text = self._call_llm(messages, max_tokens, temperature, image_base64)
        
        # Step 7: 解析太乙格式
        formal, composite, unified, has_format = self.taiyi_parser.parse(response_text)
        
        if has_format:
            self.stats["taiyi_format_hits"] += 1
        
        # Step 8: 提取推理步骤
        reasoning_steps = self.cot.extract_reasoning_steps(response_text)
        
        # Step 9: 计算统一评分（简化版）
        unified_score = self._compute_score(
            rag_used=bool(knowledge_context),
            memory_used=bool(memory_context),
            taiyi_format=has_format,
            response_length=len(response_text),
            tool_used=bool(tool_calls)
        )
        
        # Step 10: 第七识审计（新增）
        audit_result = None
        if self.enable_audit:
            try:
                audit_result = self.manas.audit_output(
                    input_text=question,
                    output_text=response_text,
                    context={
                        "goal": goal,
                        "knowledge_used": bool(knowledge_context),
                        "memory_used": bool(memory_context),
                        "tool_calls": len(tool_calls)
                    }
                )
                if audit_result.warnings:
                    self.stats["audit_flags"] += 1
            except Exception as e:
                print(f"⚠️ 第七识审计失败: {e}")
        
        # Phase 4: 自动保存关键结论
        try:
            if self.enhanced_memory is None:
                from modules.taiyi_memory import get_enhanced_memory
                self.enhanced_memory = get_enhanced_memory()
            
            # 评估重要性
            importance = self.enhanced_memory.assess_importance(response_text, "assistant")
            
            # 如果重要性高，自动保存结论
            if importance > 0.6 and len(response_text) > 100:
                # 提取太乙标签
                tags = self.enhanced_memory.extract_taiyi_tags(response_text)
                
                # 保存结论
                self.enhanced_memory.memory.save_conclusion(
                    topic=question[:50],
                    summary=response_text[:200],
                    confidence=importance,
                    tags=tags
                )
                self.stats["auto_conclusions"] = self.stats.get("auto_conclusions", 0) + 1
        except Exception as e:
            pass  # 不影响主流程
        
        return TaiyiResponse(
            content=response_text,
            reasoning_steps=reasoning_steps,
            knowledge_used=[{"source": "RAG", "content": knowledge_context[:200]}] if knowledge_context else [],
            memory_context=memory_context[:200],
            unified_score=unified_score,
            taiyi_format=has_format,
            formal_answer=formal,
            composite_answer=composite,
            unified_answer=unified,
            tool_calls=tool_calls,
            tool_results=tool_results
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """粗略估算token数（中文约1.5字/token，英文约4字符/token）"""
        if not text:
            return 0
        chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        others = len(text) - chinese
        return int(chinese * 1.5 + others / 3.5)

    def _truncate_messages(self, messages: List[Dict], max_tokens: int = 12000) -> List[Dict]:
        """
        智能截断消息历史，保留：
        1. 第一条 system prompt（截断到2000 token）
        2. 最近N轮对话（从后往前保留，直到达到token预算）
        """
        if not messages:
            return messages
        
        result = []
        total = 0
        
        # 1. 保留并截断 system prompt
        if messages[0].get("role") == "system":
            sys_msg = messages[0].copy()
            sys_text = sys_msg["content"]
            sys_tokens = self._estimate_tokens(sys_text)
            if sys_tokens > 2000:
                # 截断：保留前1500 token + 末尾500 token
                keep_start = int(len(sys_text) * 1500 / sys_tokens)
                keep_end = int(len(sys_text) * 500 / sys_tokens)
                sys_msg["content"] = sys_text[:max(keep_start, 500)] + "\n[... 内容已截断 ...]\n" + sys_text[-max(keep_end, 200):]
                print(f"⚠️ System prompt 已截断: {sys_tokens} → ~2000 tokens")
            result.append(sys_msg)
            total += min(sys_tokens, 2000)
        
        # 2. 从后往前保留对话历史
        history_msgs = messages[1:]
        kept = []
        for msg in reversed(history_msgs):
            t = self._estimate_tokens(msg.get("content", ""))
            if total + t > max_tokens:
                print(f"⚠️ 历史消息已截断: 保留最近 {len(kept)} 条，跳过 {len(history_msgs) - len(kept)} 条")
                break
            kept.append(msg)
            total += t
        
        result.extend(reversed(kept))
        return result

    def _call_llm(self, messages: List[Dict],
                   max_tokens: int, temperature: float,
                   image_base64: str = None,
                   stream_callback: callable = None) -> str:
        """调用LLM（支持多模态图片输入、流式输出）
        
        自动处理 input length too long 错误：截断历史后重试
        """
        if not self.llm.active_backend:
            return "[无可用LLM后端]"

        # 先尝试截断，避免第一轮就失败
        original_len = len(messages)
        messages = self._truncate_messages(messages)
        if len(messages) < original_len:
            print(f"⚠️ 消息已自动截断: {original_len} → {len(messages)} 条")

        try:
            return self._call_llm_core(messages, max_tokens, temperature, image_base64, stream_callback)
        except Exception as e:
            err_str = str(e)
            # 输入过长：截断后重试一次
            if "input length" in err_str.lower() or "too long" in err_str.lower():
                print(f"⚠️ 检测到输入过长，正在智能截断后重试... (error: {err_str[:100]})")
                messages = self._truncate_messages(messages, max_tokens=6000)  # 更激进的截断
                try:
                    return self._call_llm_core(messages, max_tokens, temperature, image_base64, stream_callback)
                except Exception as e2:
                    return f"[LLM调用失败(输入过长，已重试): {e2}]"
            return f"[LLM调用失败: {e}]"

    def _call_llm_core(self, messages: List[Dict],
                       max_tokens: int, temperature: float,
                       image_base64: str = None,
                       stream_callback: callable = None) -> str:
        """实际执行LLM调用的核心方法"""
        # 流式输出模式
        if stream_callback and hasattr(self.llm.active_backend, 'chat_with_image_stream'):
            return self._call_llm_stream(messages, max_tokens, temperature, image_base64, stream_callback)

        # 获取最新用户消息内容
        latest_content = messages[-1]["content"] if messages else ""

        # 使用支持多模态的chat接口
        if hasattr(self.llm.active_backend, 'chat_with_image'):
            # 多模态后端
            response = self.llm.active_backend.chat_with_image(
                content=latest_content,
                image_base64=image_base64,
                history=messages[:-1] if len(messages) > 1 else None,
                system_prompt=messages[0]["content"] if messages and messages[0]["role"] == "system" else None,
                max_tokens=max_tokens,
                temperature=temperature
            )
        elif hasattr(self.llm.active_backend, 'chat'):
            # 标准chat接口
            response = self.llm.active_backend.chat(
                latest_content,
                history=messages[:-1] if len(messages) > 1 else None,
                system_prompt=messages[0]["content"] if messages and messages[0]["role"] == "system" else None
            )
        else:
            # Fallback: 拼接消息
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            response = self.llm.generate(prompt, max_tokens, temperature)

        return response.strip()
    
    def _call_llm_stream(self, messages, max_tokens, temperature, image_base64, stream_callback):
        """流式LLM调用（内部方法）"""
        backend = self.llm.active_backend
        if not hasattr(backend, 'chat_with_image_stream'):
            # 后端不支持流式，降级为非流式
            return self._call_llm_core(messages, max_tokens, temperature, image_base64, stream_callback)
        
        latest_content = messages[-1]["content"] if messages else ""
        system_prompt = messages[0]["content"] if messages and messages[0]["role"] == "system" else None
        history = messages[1:-1] if len(messages) > 2 else None
        
        return backend.chat_with_image_stream(
            content=latest_content,
            image_base64=image_base64,
            history=history,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            callback=stream_callback
        )
    
    def _compute_score(self, 
                      rag_used: bool,
                      memory_used: bool,
                      taiyi_format: bool,
                      response_length: int,
                      tool_used: bool = False) -> float:  # 新增参数
        """计算统一评分"""
        score = 0.0
        
        if rag_used:
            score += 0.2
        if memory_used:
            score += 0.15
        if taiyi_format:
            score += 0.25
        if response_length > 100:
            score += 0.1
        if response_length > 300:
            score += 0.1
        if tool_used:  # 新增：工具调用加分
            score += 0.2
        
        return min(score, 1.0)
    
    def chat(self, question: str, goal: str = None) -> str:
        """
        简单对话接口 - 返回纯文本回复
        
        自动保存对话历史到记忆系统
        """
        # 获取记忆上下文
        memory_ctx = self._get_memory_context(question)
        
        # 生成回复
        response = self.generate(
            question=question,
            goal=goal,
            use_taiyi_format=True
        )
        
        # 保存到记忆
        if self.enable_memory:
            self.memory.add_message("user", question)
            self.memory.add_message("assistant", response.content)
        
        return response.content
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = max(1, self.stats["total_requests"])
        stats = {
            "total_requests": self.stats["total_requests"],
            "rag_hit_rate": f"{self.stats['rag_hits']/total:.1%}",
            "memory_hit_rate": f"{self.stats['memory_hits']/total:.1%}",
            "taiyi_format_rate": f"{self.stats['taiyi_format_hits']/total:.1%}",
            "tool_call_rate": f"{self.stats['tool_calls']/total:.1%}",
            "audit_flag_rate": f"{self.stats['audit_flags']/total:.1%}",
            "auto_conclusions": self.stats.get("auto_conclusions", 0),
            "rag_status": self.rag.status(),
            "memory_status": self.memory.status(),
            "tools_count": len(self.tool_engine.get_tool_definitions()),
            "audit_stats": self.manas.get_risk_statistics()
        }
        
        # 增强记忆统计
        if self.enhanced_memory:
            try:
                stats["enhanced_memory"] = self.enhanced_memory.get_memory_stats()
            except:
                pass
        
        return stats
    
    def format_response(self, response: TaiyiResponse) -> str:
        """格式化回复为可读文本"""
        lines = ["=" * 60]
        lines.append("🌌 统一太乙系统回复")
        lines.append("=" * 60)
        
        # 工具调用结果（新增）
        if response.tool_calls:
            lines.append("\n🔧 【工具调用】")
            for i, call in enumerate(response.tool_calls):
                result = response.tool_results[i] if i < len(response.tool_results) else {}
                status = "✅" if result.get("success") else "❌"
                lines.append(f"  {i+1}. {status} {call.get('tool', 'unknown')}")
                if result.get("success"):
                    output = str(result.get("output", ""))[:100]
                    lines.append(f"     输出: {output}...")
                else:
                    lines.append(f"     错误: {result.get('error', 'unknown')}")
        
        # 知识来源
        if response.knowledge_used:
            lines.append("\n📚 知识来源:")
            for k in response.knowledge_used:
                lines.append(f"  • {k['source']}: {k['content'][:100]}...")
        
        # 太乙格式
        if response.taiyi_format:
            lines.append("\n☯️ 【太乙约束格式】")
            if response.formal_answer:
                lines.append(f"\n  形式之答: {response.formal_answer}")  # 完整输出，不截断
            if response.composite_answer:
                lines.append(f"\n  复合体之答: {response.composite_answer}")  # 完整输出
            if response.unified_answer:
                lines.append(f"\n  太乙之答: {response.unified_answer}")  # 完整输出
        else:
            lines.append(f"\n{response.content}")
        
        # 统计
        lines.append(f"\n📊 统一评分: {response.unified_score:.1%}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# ==================== 全局实例 ====================

_enhancer_instance: Optional[TaiyiLLMEnhancer] = None


def get_enhancer(user_id: str = "default_user") -> TaiyiLLMEnhancer:
    """获取增强器单例"""
    global _enhancer_instance
    if _enhancer_instance is None:
        _enhancer_instance = TaiyiLLMEnhancer(user_id)
    return _enhancer_instance


# ==================== 测试 ====================

def test_enhancer():
    """测试太乙LLM增强器"""
    print("=" * 60)
    print("🧠 太乙LLM增强器测试")
    print("=" * 60)
    
    enhancer = TaiyiLLMEnhancer()
    
    # 统计
    print("\n📊 系统状态:")
    status = enhancer.get_statistics()
    for k, v in status.items():
        print(f"   {k}: {v}")
    
    # 测试问答
    test_questions = [
        ("什么是复合体理学？", None),
        ("请用太乙约束格式解释量子纠缠", None),
    ]
    
    for question, goal in test_questions:
        print(f"\n{'='*50}")
        print(f"问题: {question}")
        print("-"*50)
        
        response = enhancer.generate(
            question=question,
            goal=goal,
            use_taiyi_format=True
        )
        
        print(enhancer.format_response(response))
    
    # 最终统计
    print("\n📊 最终统计:")
    print(enhancer.get_statistics())
    
    print("\n✅ 太乙LLM增强器测试完成")


if __name__ == "__main__":
    test_enhancer()
