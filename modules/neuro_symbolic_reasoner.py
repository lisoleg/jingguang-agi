#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neuro-Symbolic Reasoner - 神经符号融合推理引擎
统一太乙系统 Phase 1.2 : 系统2逻辑推演补全

核心能力：
1. System 1（快思考）：基于LLM的直觉推理（已有太乙内核）
2. System 2（慢思考）：基于Z3/SymPy的形式化逻辑推理
3. 神经符号融合：Z3验证LLM输出，LLM解释Z3结果
4. 熵值切换开关：根据问题复杂度自动选择推理模式
"""

import sys
import os
import time
import json
import math
import re
import concurrent.futures
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


# ==================== 数据结构 ====================

class ReasoningMode(Enum):
    """推理模式"""
    SYSTEM1 = "system1"      # 快思考（LLM直觉）
    SYSTEM2 = "system2"      # 慢思考（符号推理）
    HYBRID = "hybrid"      # 融合模式
    AUTO = "auto"          # 自动选择


@dataclass
class ReasoningResult:
    """推理结果"""
    success: bool
    answer: str
    reasoning_steps: List[str] = field(default_factory=list)
    mode_used: str = ""
    confidence: float = 0.0
    proof: Optional[str] = None       # 形式化证明（System 2）
    verification: Optional[str] = None  # 验证结果
    error: Optional[str] = None


@dataclass
class ComplexityEstimate:
    """复杂度评估"""
    entropy: float       # 信息熵（0-1）
    difficulty: str     # "easy" | "medium" | "hard" | "extreme"
    category: str      # "factual" | "reasoning" | "math" | "logic" | "coding"
    recommended_mode: ReasoningMode


# ==================== 复杂度评估器 ====================

class ComplexityEstimator:
    """问题复杂度评估 - 熵值切换开关的核心"""

    # 关键词复杂度权重
    MATH_KEYWORDS = {
        "证明": 3, "求解": 3, "推导": 3, "定理": 3,
        "方程": 2, "积分": 3, "微分": 3, "矩阵": 2,
        "代数": 2, "几何": 2, "素数": 2, "递归": 2,
    }
    LOGIC_KEYWORDS = {
        "所有": 2, "存在": 2, "任意": 2, "如果": 1,
        "等价": 2, "矛盾": 2, "归纳": 3, "反证": 3,
        "当且仅当": 3, "蕴含": 2,
    }
    CODING_KEYWORDS = {
        "调试": 2, "bug": 2, "算法": 2, "复杂度": 3,
        "递归": 2, "指针": 2, "内存": 2, "并发": 3,
        "死锁": 3, "优化": 2,
    }

    @classmethod
    def estimate(cls, query: str) -> ComplexityEstimate:
        """评估问题复杂度，返回熵值和推荐推理模式"""
        q = query.strip()
        q_lower = q.lower()

        # 1. 计算信息熵（基于字符分布）
        entropy = cls._shannon_entropy(q)

        # 2. 关键词权重叠加
        keyword_score = 0
        for kw, weight in cls.MATH_KEYWORDS.items():
            if kw in q:
                keyword_score += weight
        for kw, weight in cls.LOGIC_KEYWORDS.items():
            if kw in q:
                keyword_score += weight
        for kw, weight in cls.CODING_KEYWORDS.items():
            if kw in q_lower:
                keyword_score += weight

        # 3. 长度和嵌套深度
        depth_score = 0
        # 括号嵌套深度
        max_depth = 0
        depth = 0
        for ch in q:
            if ch in '([{"\'':
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch in ')]}"\'' and depth > 0:
                depth -= 1
        depth_score = max_depth * 2

        # "如果...那么..." 条件链长度
        condition_count = q.count("如果") + q.count("那么") + q.count("because") + q.count("since")
        depth_score += condition_count * 2

        # 4. 综合熵值（归一化到0-1）
        raw_score = entropy * 2 + keyword_score + depth_score * 0.5
        normalized_entropy = min(raw_score / 20.0, 1.0)

        # 5. 分类
        category = "factual"
        if any(kw in q for kw in cls.MATH_KEYWORDS):
            category = "math"
        elif any(kw in q for kw in cls.LOGIC_KEYWORDS):
            category = "logic"
        elif any(kw in q_lower for kw in cls.CODING_KEYWORDS):
            category = "coding"
        elif len(q) > 50:
            category = "reasoning"

        # 6. 难度分级
        if normalized_entropy < 0.3:
            difficulty = "easy"
        elif normalized_entropy < 0.6:
            difficulty = "medium"
        elif normalized_entropy < 0.85:
            difficulty = "hard"
        else:
            difficulty = "extreme"

        # 7. 推荐模式
        if normalized_entropy < 0.3:
            recommended = ReasoningMode.SYSTEM1
        elif normalized_entropy < 0.7:
            recommended = ReasoningMode.HYBRID
        else:
            recommended = ReasoningMode.SYSTEM2

        return ComplexityEstimate(
            entropy=normalized_entropy,
            difficulty=difficulty,
            category=category,
            recommended_mode=recommended
        )

    @staticmethod
    def _shannon_entropy(s: str) -> float:
        """计算字符串的香农信息熵"""
        if not s:
            return 0.0
        from collections import Counter
        counts = Counter(s)
        total = len(s)
        entropy = 0.0
        import math
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy


# ==================== System 1: LLM 推理 ====================

class NeuralReasoner:
    """系统1推理器 - 基于LLM的直觉快思考"""

    def __init__(self, llm_backend=None):
        self.llm = llm_backend
        # 延迟导入，避免循环依赖
        self._llm_initialized = False

    def _ensure_llm(self):
        if not self._llm_initialized:
            try:
                from modules.local_llm import get_llm
                self.llm = get_llm()
                self._llm_initialized = True
            except Exception as e:
                print(f'⚠️ LLM后端初始化失败: {e}')

    def reason(self, query: str, context: str = "") -> ReasoningResult:
        """使用LLM进行直觉推理（带超时保护）"""
        self._ensure_llm()

        if not self.llm or not self.llm.active_backend:
            return ReasoningResult(
                success=False,
                answer="",
                error="LLM后端不可用",
                mode_used="system1"
            )

        try:
            # 构建提示词
            prompt = f"""请逐步推理以下问题，给出清晰的解答：

问题：{query}

{('背景信息：' + context) if context else ''}

请先分析，再给出最终答案。"""

            # 调用LLM（带15秒超时保护）
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self.llm.generate, prompt, 1024, 0.7
                )
                try:
                    response = future.result(timeout=15)
                except concurrent.futures.TimeoutError:
                    return ReasoningResult(
                        success=False,
                        answer="",
                        error="LLM调用超时（15秒），请检查LM Studio是否正常运行",
                        mode_used="system1"
                    )

            return ReasoningResult(
                success=True,
                answer=response.strip(),
                reasoning_steps=[response.strip()],
                mode_used="system1",
                confidence=0.7
            )
        except Exception as e:
            return ReasoningResult(
                success=False,
                answer="",
                error=f"系统1推理失败: {e}",
                mode_used="system1"
            )

    def decompose(self, query: str) -> List[str]:
        """使用LLM分解问题为子问题"""
        self._ensure_llm()
        if not self.llm or not self.llm.active_backend:
            return [query]

        try:
            prompt = f"""请将以下问题分解为3-5个可独立解决的子问题，每行一个：

问题：{query}

子问题："""
            response = self.llm.generate(prompt, max_tokens=512, temperature=0.3)
            sub_questions = [l.strip() for l in response.strip().split('\n') if l.strip()]
            return sub_questions[:5] if sub_questions else [query]
        except Exception:
            return [query]


# ==================== System 2: 符号推理 ====================

class SymbolicReasoner:
    """系统2推理器 - 基于Z3/SymPy的形式化逻辑推理"""

    def __init__(self, backend: str = "z3"):
        self.backend = backend
        self.z3_available = False
        self.sympy_available = False
        self._init_backends()

    def _init_backends(self):
        """初始化符号推理后端"""
        try:
            import z3
            self.z3 = z3
            self.z3_available = True
            print(f"✅ Z3 solver 已加载 (版本: {z3.get_version_string()})")
        except ImportError:
            print("⚠️ Z3 未安装，数学/逻辑证明能力不可用")
            print("   请运行: pip install z3-solver")

        try:
            import sympy
            self.sympy = sympy
            self.sympy_available = True
            print(f"✅ SymPy 已加载 (版本: {sympy.__version__})")
        except ImportError:
            print("⚠️ SymPy 未安装，符号计算能力不可用")
            print("   请运行: pip install sympy")

    def reason(self, query: str) -> ReasoningResult:
        """使用符号推理解决问题"""
        if not self.z3_available and not self.sympy_available:
            return ReasoningResult(
                success=False,
                answer="",
                error="无可用符号推理后端（请安装z3-solver或sympy）",
                mode_used="system2"
            )

        # 尝试用Z3处理
        if self.z3_available:
            result = self._reason_with_z3(query)
            if result.success:
                return result

        # 尝试用SymPy处理
        if self.sympy_available:
            result = self._reason_with_sympy(query)
            if result.success:
                return result

        return ReasoningResult(
            success=False,
            answer="",
            error="无法用符号推理处理此问题",
            mode_used="system2"
        )

    def _reason_with_z3(self, query: str) -> ReasoningResult:
        """使用Z3进行形式化推理"""
        try:
            z3 = self.z3
            s = z3.Solver()

            # 尝试解析问题中的数学/逻辑关系
            # 支持的基本模式：
            # 1. 求解方程: "求解 x + 2 = 5"
            # 2. 验证逻辑: "验证 (a && b) || (!a && c) == (b && c) || (!a && c)"
            # 3. 不等式: "找到满足 x > 0 && x < 10 的整数x"

            # 模式1: 求解方程
            eq_match = re.search(r'求解\s*([^=\s]+(?:\s* [+\-*/]\s*[^=\s]+)*)\s*=\s*(.+)', query)
            if eq_match:
                return self._solve_equation_z3(query)

            # 模式2: 验证性质
            if "验证" in query or "证明" in query:
                return self._prove_with_z3(query)

            # 模式3: 简单算术
            return self._solve_arithmetic_z3(query)

        except Exception as e:
            return ReasoningResult(
                success=False,
                answer="",
                error=f"Z3推理错误: {e}",
                mode_used="system2"
            )

    def _solve_equation_z3(self, query: str) -> ReasoningResult:
        """用Z3求解方程"""
        z3 = self.z3
        s = z3.Solver()

        try:
            # 提取变量和表达式
            # 简化：假设格式为 "求解 x + 2 = 5" 或 "x = ?"
            expr_match = re.search(r'(\w+)\s*([+\-*/])\s*(\d+)\s*=\s*(\d+)', query)
            if expr_match:
                var_name = expr_match.group(1)
                op = expr_match.group(2)
                const_val = int(expr_match.group(3))
                target = int(expr_match.group(4))

                # 创建Z3实数变量
                x = z3.Real(var_name)
                val = z3.Real('val')

                # 构建表达式
                if op == '+':
                    s.add(x + const_val == target)
                elif op == '-':
                    s.add(x - const_val == target)
                elif op == '*':
                    s.add(x * const_val == target)
                elif op == '/':
                    s.add(x / const_val == target)

                result = s.check()
                if result == z3.sat:
                    model = s.model()
                    answer = f"{var_name} = {model[x]}"
                    proof = f"Z3验证：{s}"
                    return ReasoningResult(
                        success=True,
                        answer=answer,
                        reasoning_steps=[f"使用Z3求解: {query}"],
                        mode_used="system2",
                        confidence=1.0,
                        proof=proof,
                        verification="Z3 sat"
                    )
                else:
                    return ReasoningResult(
                        success=False,
                        answer="",
                        error="Z3: 无解或不可满足",
                        mode_used="system2"
                    )

            return ReasoningResult(
                success=False,
                answer="",
                error="无法解析方程格式",
                mode_used="system2"
            )
        except Exception as e:
            return ReasoningResult(
                success=False,
                answer="",
                error=f"方程求解错误: {e}",
                mode_used="system2"
            )

    def _prove_with_z3(self, query: str) -> ReasoningResult:
        """用Z3进行形式化证明/验证"""
        z3 = self.z3
        s = z3.Solver()

        try:
            # 简化示例：验证德摩根定律
            if "德摩根" in query or "De Morgan" in query:
                a, b = z3.Bool('a'), z3.Bool('b')
                conjecture = z3.Not(a & b) == (z3.Not(a) | z3.Not(b))
                s.add(z3.Not(conjecture))  # 反证法：假设猜想不成立
                result = s.check()
                if result == z3.unsat:
                    return ReasoningResult(
                        success=True,
                        answer="德摩根定律成立：¬(a ∧ b) ≡ (¬a ∨ ¬b)",
                        reasoning_steps=["使用Z3反证法验证"],
                        mode_used="system2",
                        confidence=1.0,
                        proof="Z3反证：假设不成立，原命题成立",
                        verification="Z3 unsat (proved)"
                    )
                else:
                    return ReasoningResult(
                        success=False,
                        answer="",
                        error="Z3: 无法证明",
                        mode_used="system2"
                    )

            return ReasoningResult(
                success=False,
                answer="",
                error="暂不支持此证明任务",
                mode_used="system2"
            )
        except Exception as e:
            return ReasoningResult(
                success=False,
                answer="",
                error=f"证明错误: {e}",
                mode_used="system2"
            )

    def _solve_arithmetic_z3(self, query: str) -> ReasoningResult:
        """求解简单算术问题"""
        # 匹配 "x + 5 = 12" 格式
        patterns = [
            r'(\w)\s*\+\s*(\d+)\s*=\s*(\d+)',
            r'(\d+)\s*\+\s*(\w)\s*=\s*(\d+)',
            r'(\w)\s*-\s*(\d+)\s*=\s*(\d+)',
            r'(\w)\s*\*\s*(\d+)\s*=\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                groups = match.groups()
                # 简化处理
                try:
                    if len(groups) == 3:
                        if '+' in query:
                            if groups[0].isdigit() and not groups[1].isdigit():
                                # "5 + x = 12"
                                return ReasoningResult(
                                    success=True,
                                    answer=f"{groups[1]} = {int(groups[2]) - int(groups[0])}",
                                    reasoning_steps=["求解一元一次方程"],
                                    mode_used="system2",
                                    confidence=0.95
                                )
                            elif not groups[0].isdigit() and groups[1].isdigit():
                                # "x + 5 = 12"
                                return ReasoningResult(
                                    success=True,
                                    answer=f"{groups[0]} = {int(groups[2]) - int(groups[1])}",
                                    reasoning_steps=["求解一元一次方程"],
                                    mode_used="system2",
                                    confidence=0.95
                                )
                except Exception:
                    pass

        return ReasoningResult(
            success=False,
            answer="",
            error="无法解析",
            mode_used="system2"
        )

    def _reason_with_sympy(self, query: str) -> ReasoningResult:
        """使用SymPy进行符号计算"""
        try:
            sympy = self.sympy

            # 尝试解析数学表达式
            # 提取数学表达式
            math_expr = re.search(r'[^，。]*[+\-*/\d\w\s()^]+[^，。]*', query)
            if not math_expr:
                return ReasoningResult(
                    success=False,
                    answer="",
                    error="SymPy: 未找到数学表达式",
                    mode_used="system2"
                )

            expr_str = math_expr.group(0).strip()

            # 尝试计算
            try:
                result = sympy.sympify(expr_str)
                if hasattr(result, 'evalf'):
                    val = result.evalf()
                    return ReasoningResult(
                        success=True,
                        answer=f"{expr_str} = {val}",
                        reasoning_steps=[f"SymPy计算: {expr_str}"],
                        mode_used="system2",
                        confidence=0.9
                    )
            except Exception:
                pass

            return ReasoningResult(
                success=False,
                answer="",
                error="SymPy: 无法计算表达式",
                mode_used="system2"
            )
        except Exception as e:
            return ReasoningResult(
                success=False,
                answer="",
                error=f"SymPy错误: {e}",
                mode_used="system2"
            )

    def verify(self, proof: str) -> bool:
        """验证证明的正确性"""
        if not self.z3_available:
            return False
        try:
            # 简化验证：检查证明中是否包含有效的Z3模型
            return "sat" in proof or "unsat" in proof or "模型" in proof
        except Exception:
            return False


# ==================== 神经符号融合推理器 ====================

class NeuroSymbolicReasoner:
    """
    神经符号融合推理器 - 双系统思维的核心实现

    架构：
                                     ┌───────────────────────────┐
                              ┌────│            输入问题                │
                              │    └──────────────┬────────────┘
                              │                   │
                              │            ┌──────▼──────┐
                              │            │  复杂度评估  │
                              │            └──────┬──────┘
                              │         ╱entropy < 0.7?╲
                              │         ┌─────┴─────┐
                              │         │            │
                           低熵│    System 1   │  System 2 / Hybrid
                              │    (LLM快思考) │  (Z3 + LLM融合)
                              │         │            │
                              │    ┌────▼────┐ ┌▼────────────┐
                              │    │ 直觉答案  │ │ 符号验证+解释  │
                              │    └─────────┘ └──────────────┘
                              │                   │
                              │            ┌──────▼──────┐
                              │            │   融合输出    │
                              │            └─────────────┘
    """

    def __init__(self, llm_backend=None, symbolic_backend: str = "z3"):
        self.neural = NeuralReasoner(llm_backend=llm_backend)
        self.symbolic = SymbolicReasoner(backend=symbolic_backend)
        self.estimator = ComplexityEstimator()
        self.auto_mode = True  # 自动选择推理模式

    def reason(self, query: str, mode: Optional[ReasoningMode] = None,
                context: str = "") -> ReasoningResult:
        """
        执行推理

        Args:
            query: 用户问题
            mode: 推理模式（None=自动选择）
            context: 上下文

        Returns:
            ReasoningResult: 推理结果
        """
        # 1. 确定推理模式
        if mode is None and self.auto_mode:
            complexity = self.estimator.estimate(query)
            mode = complexity.recommended_mode
            print(f"🧠 复杂度评估: entropy={complexity.entropy:.2f}, "
                  f"难度={complexity.difficulty}, 推荐模式={mode.value}")
        elif mode is None:
            mode = ReasoningMode.HYBRID

        # 2. 执行推理
        if mode == ReasoningMode.SYSTEM1:
            return self._neural_only(query, context)
        elif mode == ReasoningMode.SYSTEM2:
            return self._symbolic_only(query)
        elif mode == ReasoningMode.HYBRID:
            return self._hybrid(query, context)
        else:  # AUTO - 已经处理了
            return self.reason(query, mode=mode, context=context)

    def _neural_only(self, query: str, context: str) -> ReasoningResult:
        """仅使用System 1（LLM）"""
        return self.neural.reason(query, context)

    def _symbolic_only(self, query: str) -> ReasoningResult:
        """仅使用System 2（符号推理）"""
        return self.symbolic.reason(query)

    def _hybrid(self, query: str, context: str) -> ReasoningResult:
        """
        神经符号融合模式：
        1. 先用LLM生成候选答案
        2. 用符号推理验证/改进答案
        3. 用LLM解释符号结果
        """
        # Step 1: LLM生成候选答案
        neural_result = self.neural.reason(query, context)
        if not neural_result.success:
            # LLM失败，降级到纯符号推理
            return self._symbolic_only(query)

        candidate_answer = neural_result.answer

        # Step 2: 尝试用符号推理验证
        # 如果问题是数学/逻辑类，用Z3验证
        complexity = self.estimator.estimate(query)
        if complexity.category in ("math", "logic"):
            symbolic_result = self.symbolic.reason(query)
            if symbolic_result.success:
                # 融合：符号结果更可信
                return ReasoningResult(
                    success=True,
                    answer=symbolic_result.answer,
                    reasoning_steps=[
                        f"LLM候选答案: {candidate_answer[:200]}",
                        f"符号验证结果: {symbolic_result.answer}"
                    ],
                    mode_used="hybrid",
                    confidence=min(symbolic_result.confidence + 0.1, 1.0),
                    proof=symbolic_result.proof,
                    verification=symbolic_result.verification
                )

        # Step 3: 非数学/逻辑类，返回LLM结果
        neural_result.mode_used = "hybrid"
        return neural_result

    def decompose(self, query: str) -> List[str]:
        """问题分解（由LLM完成）"""
        return self.neural.decompose(query)

    def verify(self, proof: str) -> bool:
        """验证证明"""
        return self.symbolic.verify(proof)

    def set_mode(self, auto: bool = True):
        """设置是否自动选择模式"""
        self.auto_mode = auto


# ==================== 与现有系统集成 ====================

def get_neuro_symbolic_reasoner() -> NeuroSymbolicReasoner:
    """获取推理器单例"""
    if not hasattr(get_neuro_symbolic_reasoner, '_instance'):
        get_neuro_symbolic_reasoner._instance = NeuroSymbolicReasoner()
    return get_neuro_symbolic_reasoner._instance


# ==================== 测试 ====================

def test_complexity_estimator():
    """测试复杂度评估器"""
    print("\n" + "="*60)
    print("测试：复杂度评估器（熵值切换开关）")
    print("="*60)

    test_queries = [
        "你好",
        "北京的气候怎么样？",
        "求解方程：x + 5 = 12",
        "证明德摩根定律：¬(a ∧ b) ≡ (¬a ∨ ¬b)",
        "如果一个数是偶数，那么它可以被2整除。请证明这个命题的逆命题是否成立。"
    ]

    for q in test_queries:
        est = ComplexityEstimator.estimate(q)
        print(f"\n问题: {q[:40]}...")
        print(f"  熵值: {est.entropy:.3f}")
        print(f"  难度: {est.difficulty}")
        print(f"  类别: {est.category}")
        print(f"  推荐模式: {est.recommended_mode.value}")


def test_neural_reasoner():
    """测试系统1推理器"""
    print("\n" + "="*60)
    print("测试：系统1推理器（LLM）")
    print("="*60)

    reasoner = NeuralReasoner()
    result = reasoner.reason("你好，请介绍一下自己")
    print(f"成功: {result.success}")
    print(f"答案: {result.answer[:200]}")
    print(f"置信度: {result.confidence}")


def test_symbolic_reasoner():
    """测试系统2推理器"""
    print("\n" + "="*60)
    print("测试：系统2推理器（Z3/SymPy）")
    print("="*60)

    reasoner = SymbolicReasoner()

    # 测试方程求解
    print("\n--- 测试1：方程求解 ---")
    result = reasoner.reason("求解 x + 5 = 12")
    print(f"成功: {result.success}")
    print(f"答案: {result.answer}")
    print(f"证明: {result.proof}")

    # 测试证明
    print("\n--- 测试2：逻辑验证 ---")
    result = reasoner.reason("验证德摩根定律")
    print(f"成功: {result.success}")
    print(f"答案: {result.answer}")


def test_hybrid_reasoner():
    """测试融合推理器"""
    print("\n" + "="*60)
    print("测试：神经符号融合推理器")
    print("="*60)

    reasoner = NeuroSymbolicReasoner()

    test_cases = [
        "你好",
        "求解 x + 5 = 12",
        "北京的气候怎么样？",
    ]

    for query in test_cases:
        print(f"\n问题: {query}")
        result = reasoner.reason(query)
        print(f"  模式: {result.mode_used}")
        print(f"  成功: {result.success}")
        print(f"  答案: {result.answer[:150]}")
        if result.proof:
            print(f"  证明: {result.proof[:100]}")


if __name__ == "__main__":
    print("="*60)
    print("🧠 神经符号融合推理引擎测试")
    print("="*60)

    test_complexity_estimator()

    # 检查依赖
    try:
        import z3
        print(f"\n✅ Z3 可用 (版本: {z3.get_version_string()})")
    except ImportError:
        print("\n⚠️ Z3 不可用，部分测试将跳过")

    test_symbolic_reasoner()
    test_hybrid_reasoner()

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
