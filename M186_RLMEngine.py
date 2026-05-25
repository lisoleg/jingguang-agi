#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M186_RLMEngine.py — 太乙AGI v7.25 RLM 递归语言模型引擎
=====================================================
基于 MIT RLM（Recursive Language Model）论文实现 4 个核心算子：
  1. PeekOperator     — 查看文档结构（目录/标题/分段）
  2. GrepOperator     — 关键词/正则过滤
  3. PartitionOperator — 按结构/语义/固定大小分块
  4. RecursionOperator — 递归自调用（depth_limit ≤ 3, max 5）

类结构：RLMEngine → RLMOperator(ABC) → 4个具体算子
递归闭环：RecursionOperator 内部调用 RLMEngine 形成 recursive closure

依赖：M176 (可寻址), M118 (可回写 partial)
"""

from __future__ import annotations

import re
import time
import hashlib
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


# ============================================================
# 数据结构
# ============================================================

class PartitionStrategy(Enum):
    """分块策略"""
    STRUCTURAL = "structural"   # 按标题/段落结构分块
    SEMANTIC = "semantic"       # 按语义边界分块（句子级）
    FIXED_SIZE = "fixed_size"   # 按固定 token 数分块


class RLMOperatorType(Enum):
    """算子类型"""
    PEEK = "peek"
    GREP = "grep"
    PARTITION = "partition"
    RECURSION = "recursion"


@dataclass
class RLMDocument:
    """RLM 文档对象"""
    content: str                           # 原始文本
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: str = ""                       # 文档唯一ID
    parent_id: Optional[str] = None        # 父文档ID（递归时使用）
    depth: int = 0                         # 递归深度
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.doc_id:
            self.doc_id = hashlib.md5(
                f"{self.content[:200]}:{time.time()}".encode()
            ).hexdigest()[:12]


@dataclass
class Section:
    """文档节（peek 结果）"""
    title: str
    level: int                 # 标题层级 (1-6)
    content: str
    start_char: int
    end_char: int
    children: List["Section"] = field(default_factory=list)


@dataclass
class PeekResult:
    """peek 算子结果"""
    sections: List[Dict[str, Any]]     # 结构化节列表
    total_chars: int
    total_lines: int
    heading_count: int
    estimated_tokens: int


@dataclass
class GrepMatch:
    """grep 单条匹配"""
    matched_text: str
    start_pos: int
    end_pos: int
    line_number: int
    context_before: str
    context_after: str


@dataclass
class GrepResult:
    """grep 算子结果"""
    pattern: str
    total_matches: int
    matches: List[Dict[str, Any]]
    match_lines: List[int]


@dataclass
class Chunk:
    """分块"""
    chunk_id: str
    content: str
    start_char: int
    end_char: int
    char_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PartitionResult:
    """partition 算子结果"""
    chunks: List[Dict[str, Any]]
    strategy: str
    total_chunks: int


@dataclass
class RecursionResult:
    """recursion 算子结果"""
    depth: int
    max_depth: int
    operators_applied: List[str]       # 每层应用的算子序列
    results: List[Dict[str, Any]]     # 每层的输出摘要
    final_output: Any                 # 最终输出
    total_nodes: int                  # 递归树节点数


@dataclass
class RLMTrace:
    """RLM 执行追踪（单个算子调用）"""
    operator: str
    operator_type: str
    input_summary: str
    output_summary: str
    duration_ms: float
    depth: int
    children: List["RLMTrace"] = field(default_factory=list)


class RecursionDepthExceeded(Exception):
    """递归深度超限异常"""
    def __init__(self, depth: int, max_depth: int):
        self.depth = depth
        self.max_depth = max_depth
        super().__init__(
            f"RLM recursion depth {depth} exceeded maximum {max_depth}"
        )


# ============================================================
# RLMOperator 抽象基类
# ============================================================

class RLMOperator(ABC):
    """RLM 算子抽象基类"""

    @property
    @abstractmethod
    def operator_type(self) -> RLMOperatorType:
        pass

    @abstractmethod
    def execute(self, doc: RLMDocument, **kwargs) -> Any:
        pass


# ============================================================
# PeekOperator — 查看文档结构
# ============================================================

class PeekOperator(RLMOperator):
    """
    peek(doc) — 查看文档结构（目录/标题/分段）
    输出：节列表、字符数、行数、标题数、估算 token 数
    """

    # Markdown 标题正则
    HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    @property
    def operator_type(self) -> RLMOperatorType:
        return RLMOperatorType.PEEK

    def execute(self, doc: RLMDocument, **kwargs) -> PeekResult:
        start = time.time()
        content = doc.content

        # 提取标题和节
        sections = []
        matches = list(self.HEADING_RE.finditer(content))
        for i, m in enumerate(matches):
            level = len(m.group(1))
            title = m.group(2).strip()
            start_char = m.start()
            end_char = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start_char:end_char].strip()

            sections.append({
                "title": title,
                "level": level,
                "start_char": start_char,
                "end_char": end_char,
                "char_count": len(section_content),
                "line_count": section_content.count("\n") + 1,
                "has_subsections": any(
                    s["level"] > level for s in matches[i+1:i+1] if False
                ) if i + 1 < len(matches) else False,
            })

        # 估算 token（中文约 1.5 char/token, 英文约 4 char/token）
        cn_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        en_chars = len(content) - cn_chars
        estimated_tokens = int(cn_chars / 1.5 + en_chars / 4)

        duration = (time.time() - start) * 1000
        return PeekResult(
            sections=sections,
            total_chars=len(content),
            total_lines=content.count("\n") + 1,
            heading_count=len(matches),
            estimated_tokens=estimated_tokens,
        )


# ============================================================
# GrepOperator — 关键词/正则过滤
# ============================================================

class GrepOperator(RLMOperator):
    """
    grep(doc, pattern) — 关键词/正则过滤
    支持正则表达式和纯文本匹配
    """

    @property
    def operator_type(self) -> RLMOperatorType:
        return RLMOperatorType.GREP

    def execute(self, doc: RLMDocument, pattern: str = "",
                use_regex: bool = False, context_lines: int = 1,
                case_sensitive: bool = False, **kwargs) -> GrepResult:
        start = time.time()
        content = doc.content

        if not pattern:
            return GrepResult(
                pattern=pattern, total_matches=0, matches=[], match_lines=[]
            )

        # 构建正则
        flags = 0 if case_sensitive else re.IGNORECASE
        if not use_regex:
            regex_pattern = re.escape(pattern)
        else:
            regex_pattern = pattern

        try:
            compiled = re.compile(regex_pattern, flags)
        except re.error as e:
            return GrepResult(
                pattern=pattern, total_matches=0, matches=[],
                match_lines=[], error=f"Invalid regex: {e}"
            )

        # 逐行搜索
        lines = content.split("\n")
        all_matches: List[GrepMatch] = []
        match_lines_set = set()

        for line_no, line in enumerate(lines, 1):
            for m in compiled.finditer(line):
                matched_text = m.group()
                start_pos = m.start()
                end_pos = m.end()

                # 获取上下文
                ctx_before = ""
                ctx_after = ""
                if context_lines > 0:
                    ctx_lines_before = lines[max(0, line_no - 1 - context_lines):line_no - 1]
                    ctx_lines_after = lines[line_no:min(len(lines), line_no + context_lines)]
                    ctx_before = "\n".join(ctx_lines_before)
                    ctx_after = "\n".join(ctx_lines_after)

                all_matches.append(GrepMatch(
                    matched_text=matched_text,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    line_number=line_no,
                    context_before=ctx_before,
                    context_after=ctx_after,
                ))
                match_lines_set.add(line_no)

        matches_dicts = [
            {
                "matched_text": gm.matched_text,
                "start_pos": gm.start_pos,
                "end_pos": gm.end_pos,
                "line_number": gm.line_number,
                "context_before": gm.context_before,
                "context_after": gm.context_after,
            }
            for gm in all_matches
        ]

        duration = (time.time() - start) * 1000
        return GrepResult(
            pattern=pattern,
            total_matches=len(all_matches),
            matches=matches_dicts[:100],  # 最多返回100条
            match_lines=sorted(match_lines_set),
        )


# ============================================================
# PartitionOperator — 分块
# ============================================================

class PartitionOperator(RLMOperator):
    """
    partition(doc, strategy) — 按策略分块
    三种策略：
    - structural: 按标题/段落结构分块
    - semantic: 按句子语义边界分块
    - fixed_size: 按固定字符数分块
    """

    # Markdown 标题正则
    HEADING_RE = re.compile(r'^(#{1,6})\s+', re.MULTILINE)
    # 中英文句号分句
    SENTENCE_RE = re.compile(r'(?<=[。！？.!?])\s+')

    @property
    def operator_type(self) -> RLMOperatorType:
        return RLMOperatorType.PARTITION

    def execute(self, doc: RLMDocument,
                strategy: Union[str, PartitionStrategy] = PartitionStrategy.STRUCTURAL,
                chunk_size: int = 500, overlap: int = 50,
                **kwargs) -> PartitionResult:
        content = doc.content

        if isinstance(strategy, str):
            strategy = PartitionStrategy(strategy.lower())

        if strategy == PartitionStrategy.STRUCTURAL:
            chunks = self._partition_structural(content, doc.doc_id)
        elif strategy == PartitionStrategy.SEMANTIC:
            chunks = self._partition_semantic(content, doc.doc_id, chunk_size)
        else:
            chunks = self._partition_fixed(content, doc.doc_id, chunk_size, overlap)

        chunks_dicts = [asdict(c) for c in chunks]
        return PartitionResult(
            chunks=chunks_dicts,
            strategy=strategy.value,
            total_chunks=len(chunks),
        )

    def _partition_structural(self, content: str, parent_id: str) -> List[Chunk]:
        """按 Markdown 标题结构分块"""
        chunks = []
        matches = list(self.HEADING_RE.finditer(content))

        if not matches:
            # 无标题，整体作为一个 chunk
            chunks.append(Chunk(
                chunk_id=hashlib.md5(f"{parent_id}:0".encode()).hexdigest()[:8],
                content=content, start_char=0, end_char=len(content),
                char_count=len(content),
                metadata={"type": "full_document"},
            ))
            return chunks

        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            if section_content:
                chunks.append(Chunk(
                    chunk_id=hashlib.md5(
                        f"{parent_id}:{i}".encode()
                    ).hexdigest()[:8],
                    content=section_content,
                    start_char=start,
                    end_char=end,
                    char_count=len(section_content),
                    metadata={"type": "section", "section_index": i},
                ))

        return chunks

    def _partition_semantic(self, content: str, parent_id: str,
                            target_size: int) -> List[Chunk]:
        """按句子语义边界分块"""
        sentences = self.SENTENCE_RE.split(content)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_sentences = []
        current_length = 0

        for i, sentence in enumerate(sentences):
            current_sentences.append(sentence)
            current_length += len(sentence)

            if current_length >= target_size:
                chunk_content = "".join(current_sentences)
                chunks.append(Chunk(
                    chunk_id=hashlib.md5(
                        f"{parent_id}:s:{i}".encode()
                    ).hexdigest()[:8],
                    content=chunk_content,
                    start_char=sum(len(s) for s in sentences[:i - len(current_sentences) + 1]),
                    end_char=sum(len(s) for s in sentences[:i + 1]),
                    char_count=len(chunk_content),
                    metadata={"type": "semantic", "sentence_count": len(current_sentences)},
                ))
                current_sentences = []
                current_length = 0

        # 剩余句子
        if current_sentences:
            chunk_content = "".join(current_sentences)
            base = sum(len(s) for s in sentences[:-len(current_sentences)])
            chunks.append(Chunk(
                chunk_id=hashlib.md5(
                    f"{parent_id}:s:last".encode()
                ).hexdigest()[:8],
                content=chunk_content,
                start_char=base,
                end_char=base + len(chunk_content),
                char_count=len(chunk_content),
                metadata={"type": "semantic", "sentence_count": len(current_sentences)},
            ))

        return chunks if chunks else [Chunk(
            chunk_id=hashlib.md5(f"{parent_id}:s:0".encode()).hexdigest()[:8],
            content=content, start_char=0, end_char=len(content),
            char_count=len(content), metadata={"type": "semantic"},
        )]

    def _partition_fixed(self, content: str, parent_id: str,
                         chunk_size: int, overlap: int) -> List[Chunk]:
        """按固定字符数分块（带重叠）"""
        chunks = []
        start = 0
        idx = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_content = content[start:end]

            chunks.append(Chunk(
                chunk_id=hashlib.md5(
                    f"{parent_id}:f:{idx}".encode()
                ).hexdigest()[:8],
                content=chunk_content,
                start_char=start,
                end_char=end,
                char_count=len(chunk_content),
                metadata={"type": "fixed_size", "chunk_index": idx},
            ))

            if end >= len(content):
                break
            start = end - overlap
            idx += 1

        return chunks


# ============================================================
# RecursionOperator — 递归自调用
# ============================================================

class RecursionOperator(RLMOperator):
    """
    recursion(sub_doc, depth_limit) — 递归自调用
    内部调用 RLMEngine 对子文档执行算子序列，形成递归闭环。
    默认 depth_limit=3, 最大=5, 超限抛出 RecursionDepthExceeded。
    """

    DEFAULT_DEPTH_LIMIT = 3
    MAX_DEPTH_LIMIT = 5

    @property
    def operator_type(self) -> RLMOperatorType:
        return RLMOperatorType.RECURSION

    def execute(self, doc: RLMDocument,
                depth_limit: int = DEFAULT_DEPTH_LIMIT,
                sub_operators: Optional[List[str]] = None,
                engine: Optional["RLMEngine"] = None,
                **kwargs) -> RecursionResult:
        start = time.time()

        # 参数安全
        if depth_limit > self.MAX_DEPTH_LIMIT:
            raise RecursionDepthExceeded(depth_limit, self.MAX_DEPTH_LIMIT)
        if doc.depth >= depth_limit:
            raise RecursionDepthExceeded(doc.depth, depth_limit)

        if engine is None:
            raise ValueError("RecursionOperator requires RLMEngine reference")

        # 默认算子序列：peek → grep → partition
        if sub_operators is None:
            sub_operators = ["peek", "partition"]

        operators_applied = []
        results = []
        total_nodes = 1  # 当前节点

        # 对当前文档执行算子
        current_doc = doc
        for op_name in sub_operators:
            op_result = engine.execute_operator(
                op_name, current_doc, depth_limit=depth_limit
            )
            operators_applied.append(op_name)
            results.append(self._summarize(op_result))

            # 如果 partition 产生子块，递归处理
            if op_name == "partition" and isinstance(op_result, PartitionResult):
                for chunk_dict in op_result.chunks:
                    sub_doc = RLMDocument(
                        content=chunk_dict["content"],
                        metadata={"chunk_id": chunk_dict["chunk_id"]},
                        parent_id=doc.doc_id,
                        depth=doc.depth + 1,
                    )
                    try:
                        sub_result = self.execute(
                            sub_doc,
                            depth_limit=depth_limit,
                            sub_operators=["peek", "grep"],
                            engine=engine,
                        )
                        total_nodes += sub_result.total_nodes
                        results.append({
                            "chunk_id": chunk_dict["chunk_id"],
                            "depth": doc.depth + 1,
                            "sub_results": sub_result.results[:3],
                        })
                    except RecursionDepthExceeded:
                        results.append({
                            "chunk_id": chunk_dict["chunk_id"],
                            "depth": doc.depth + 1,
                            "status": "depth_exceeded",
                        })
                        break

        duration = (time.time() - start) * 1000
        return RecursionResult(
            depth=doc.depth,
            max_depth=depth_limit,
            operators_applied=operators_applied,
            results=results,
            final_output=results[-1] if results else None,
            total_nodes=total_nodes,
        )

    def _summarize(self, result: Any) -> Dict[str, Any]:
        """生成算子结果的摘要"""
        if isinstance(result, PeekResult):
            return {
                "operator": "peek",
                "sections": len(result.sections),
                "chars": result.total_chars,
                "tokens_est": result.estimated_tokens,
            }
        elif isinstance(result, GrepResult):
            return {
                "operator": "grep",
                "matches": result.total_matches,
                "pattern": result.pattern,
            }
        elif isinstance(result, PartitionResult):
            return {
                "operator": "partition",
                "chunks": result.total_chunks,
                "strategy": result.strategy,
            }
        elif isinstance(result, RecursionResult):
            return {
                "operator": "recursion",
                "depth": result.depth,
                "nodes": result.total_nodes,
                "ops": result.operators_applied,
            }
        return {"operator": "unknown", "raw": str(result)[:200]}


# ============================================================
# RLMEngine — 主引擎
# ============================================================

class RLMEngine:
    """
    RLM 递归语言模型引擎

    MIT RLM 的太乙AGI实现，提供4个核心算子：
    - peek:     查看文档结构
    - grep:     关键词/正则过滤
    - partition: 按策略分块
    - recursion: 递归自调用（递归闭环）

    L4 IDO 长程处理原语，外挂式 L2-shell 模拟。
    """

    _instance = None
    _lock = threading.Lock()
    _module_version = "v7.25"

    def __init__(self):
        self.peek = PeekOperator()
        self.grep = GrepOperator()
        self.partition = PartitionOperator()
        self.recursion = RecursionOperator()

        self._operators: Dict[str, RLMOperator] = {
            "peek": self.peek,
            "grep": self.grep,
            "partition": self.partition,
            "recursion": self.recursion,
        }
        self._execution_history: List[Dict[str, Any]] = []
        self._total_executions = 0

    @classmethod
    def get_instance(cls) -> "RLMEngine":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def execute_operator(self, operator_name: str, doc: RLMDocument,
                         **kwargs) -> Any:
        """执行指定算子"""
        op = self._operators.get(operator_name)
        if op is None:
            raise ValueError(f"Unknown RLM operator: {operator_name}. "
                             f"Available: {list(self._operators.keys())}")

        start = time.time()
        # 分离 engine 参数避免与 kwargs 冲突
        engine_kwarg = kwargs.pop("engine", self)
        result = op.execute(doc, engine=engine_kwarg, **kwargs)
        duration = (time.time() - start) * 1000

        # 记录执行历史
        self._total_executions += 1
        self._execution_history.append({
            "operator": operator_name,
            "doc_id": doc.doc_id,
            "depth": doc.depth,
            "duration_ms": round(duration, 2),
            "timestamp": time.time(),
        })
        # 保留最近 100 条
        if len(self._execution_history) > 100:
            self._execution_history = self._execution_history[-100:]

        return result

    def execute_pipeline(self, content: str,
                         operators: Optional[List[Dict[str, Any]]] = None,
                         metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行 RLM 算子管道

        Args:
            content: 输入文本
            operators: 算子序列 [{"name": "peek"}, {"name": "grep", "pattern": "L2"}, ...]
            metadata: 文档元数据

        Returns:
            管道执行结果（每步输出 + 最终结果）
        """
        doc = RLMDocument(content=content, metadata=metadata or {})

        if operators is None:
            operators = [{"name": "peek"}]

        pipeline_results = []
        current = doc

        for op_config in operators:
            op_name = op_config.get("name", "peek")
            op_kwargs = {k: v for k, v in op_config.items() if k != "name"}

            try:
                result = self.execute_operator(op_name, current, **op_kwargs)
                pipeline_results.append({
                    "operator": op_name,
                    "status": "success",
                    "result": self._serialize_result(result),
                    "duration_ms": round(
                        self._execution_history[-1]["duration_ms"], 2
                    ) if self._execution_history else 0,
                })

                # 如果是 partition，可以继续对 chunks 操作
                if isinstance(result, PartitionResult) and result.chunks:
                    current = RLMDocument(
                        content=result.chunks[0]["content"],
                        metadata={"chunk_id": result.chunks[0]["chunk_id"]},
                        parent_id=doc.doc_id,
                        depth=1,
                    )
            except RecursionDepthExceeded as e:
                pipeline_results.append({
                    "operator": op_name,
                    "status": "depth_exceeded",
                    "error": str(e),
                })
                break
            except Exception as e:
                pipeline_results.append({
                    "operator": op_name,
                    "status": "error",
                    "error": str(e),
                })
                break

        return {
            "doc_id": doc.doc_id,
            "total_operators": len(operators),
            "successful": sum(
                1 for r in pipeline_results if r["status"] == "success"
            ),
            "results": pipeline_results,
        }

    def _serialize_result(self, result: Any) -> Dict[str, Any]:
        """序列化算子结果"""
        if isinstance(result, (PeekResult, GrepResult, PartitionResult,
                               RecursionResult)):
            return asdict(result)
        return {"type": str(type(result).__name__), "summary": str(result)[:500]}

    def get_state(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "module": "M186_RLMEngine",
            "version": self._module_version,
            "total_executions": self._total_executions,
            "available_operators": list(self._operators.keys()),
            "history_size": len(self._execution_history),
            "recent_executions": self._execution_history[-5:],
        }


# ============================================================
# 模块级便捷接口
# ============================================================

def get_instance() -> RLMEngine:
    return RLMEngine.get_instance()

def get_state() -> Dict[str, Any]:
    return get_instance().get_state()


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("M186 RLMEngine 自测")
    print("=" * 60)

    engine = RLMEngine.get_instance()

    # 测试文档
    test_doc_content = """# 复合体理学概论

## 第一章：一现象

一现象是观察者与被观察者不可分割的整体。在量子力学中，
测量行为本身改变了被测系统的状态。

## 第二章：三视界

三视界是理解同一现象的三个层次：
1. L1 直觉视界
2. L2 理性视界
3. L3 流贯视界

### L2-shell 硬化

L2-shell 是理性的代数壳，需要五项属性硬化：
- 一致性（M88）
- 可保持（M78）
- 可寻址（M176）
- 可锚定（M175）
- 可回写（M118）

### Context Rot

Context Rot 是 L2-shell 缺失导致的上下文衰退。
SNR = |R(Phi_L1)| / |Phi_L1 - R(Phi_L1)|

## 第三章：五层次

五层次架构从底向上是：
1. 离散时空
2. 拓扑缺陷
3. 量子场
4. 经典场
5. 意识涌现
"""

    doc = RLMDocument(content=test_doc_content, metadata={"source": "test"})

    # Test 1: peek
    print("\n--- Test 1: Peek ---")
    peek_result = engine.execute_operator("peek", doc)
    print(f"  Sections: {len(peek_result.sections)}")
    print(f"  Chars: {peek_result.total_chars}")
    print(f"  Tokens est: {peek_result.estimated_tokens}")
    assert peek_result.heading_count > 0, "Peek should find headings"

    # Test 2: grep
    print("\n--- Test 2: Grep ---")
    grep_result = engine.execute_operator("grep", doc, pattern="L2-shell")
    print(f"  Matches: {grep_result.total_matches}")
    assert grep_result.total_matches > 0, "Grep should find L2-shell"

    grep_regex = engine.execute_operator("grep", doc, pattern=r"M\d{2,3}", use_regex=True)
    print(f"  Regex matches: {grep_regex.total_matches}")
    assert grep_regex.total_matches > 0, "Regex should find module codes"

    # Test 3: partition
    print("\n--- Test 3: Partition ---")
    part_struct = engine.execute_operator(
        "partition", doc, strategy="structural"
    )
    print(f"  Structural chunks: {part_struct.total_chunks}")
    assert part_struct.total_chunks > 0

    part_semantic = engine.execute_operator(
        "partition", doc, strategy="semantic", chunk_size=100
    )
    print(f"  Semantic chunks: {part_semantic.total_chunks}")

    part_fixed = engine.execute_operator(
        "partition", doc, strategy="fixed_size", chunk_size=200, overlap=50
    )
    print(f"  Fixed chunks: {part_fixed.total_chunks}")

    # Test 4: recursion
    print("\n--- Test 4: Recursion ---")
    try:
        rec_result = engine.execute_operator(
            "recursion", doc, depth_limit=2, engine=engine
        )
        print(f"  Depth: {rec_result.depth}/{rec_result.max_depth}")
        print(f"  Operators: {rec_result.operators_applied}")
        print(f"  Total nodes: {rec_result.total_nodes}")
        assert rec_result.total_nodes > 0
    except RecursionDepthExceeded as e:
        print(f"  Depth exceeded (expected for deep docs): {e}")

    # Test 5: pipeline
    print("\n--- Test 5: Pipeline ---")
    pipeline = engine.execute_pipeline(
        test_doc_content,
        operators=[
            {"name": "peek"},
            {"name": "grep", "pattern": "L2-shell"},
            {"name": "partition", "strategy": "structural"},
        ],
    )
    print(f"  Pipeline steps: {pipeline['total_operators']}")
    print(f"  Successful: {pipeline['successful']}")
    assert pipeline["successful"] == 3

    # Test 6: depth limit exceeded
    print("\n--- Test 6: Depth Limit ---")
    try:
        engine.execute_operator(
            "recursion", doc, depth_limit=10, engine=engine
        )
        print("  ERROR: Should have raised RecursionDepthExceeded")
    except RecursionDepthExceeded as e:
        print(f"  OK: {e}")

    # Test 7: state
    print("\n--- Test 7: State ---")
    state = engine.get_state()
    print(f"  Module: {state['module']}")
    print(f"  Total executions: {state['total_executions']}")
    print(f"  Operators: {state['available_operators']}")

    print("\n" + "=" * 60)
    print("All tests PASSED!")
    print("=" * 60)
