# -*- coding: utf-8 -*-
"""
TYIDO Self-Consistency Checker — L2壳结构属性·一致性硬化
=========================================================

TY/IDO 审查表 Property 1（对治锯齿）：
  同一问题 → N种变体 → 走相同管道 → 比较输出 → J(R)→1

核心类：
  - SelfConsistencyChecker: 通用一致性验证引擎
  - ConsistencyResult: 验证结果（含J(R)分数、详情）

使用方式：
  checker = SelfConsistencyChecker(threshold=0.85)
  result = checker.check(question, process_fn, num_variants=100)
  if not result.consistent:
      # 拒答：不一致
      return {"error": "consistency_check_failed", "j_score": result.j_score}
"""

import time
import hashlib
import random
import re
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

# ============================================================
# 同义词替换表 — 用于生成问题变体
# ============================================================

_SYNONYM_MAP: Dict[str, List[str]] = {
    # 中文同义词
    "什么是": ["请解释", "如何理解", "怎么定义", "如何描述", "的含义是什么", "指的是什么"],
    "如何": ["怎样", "用什么方式", "通过什么方法", "以何种方式", "怎么才能"],
    "为什么": ["原因是什么", "为何", "是什么导致了", "出于什么原因", "基于什么理由"],
    "计算": ["求", "算出", "得出", "推导", "估算"],
    "分析": ["解析", "剖析", "研究", "审视", "探讨"],
    "比较": ["对比", "对照", "权衡", "区分", "辨别"],
    "优化": ["改善", "提升", "改进", "增强", "完善"],
    "问题": ["疑问", "困惑", "话题", "课题", "议题"],
    "方法": ["途径", "方式", "手段", "策略", "方案"],
    "系统": ["体系", "架构", "框架", "结构", "机制"],
    "模块": ["组件", "单元", "部件", "部分", "子模块"],
    "属性": ["特性", "特征", "性质", "参数", "指标"],
    "关系": ["联系", "关联", "相互作用", "耦合", "依赖"],
    "数据": ["信息", "数值", "资料", "记录", "观测值"],
    "结果": ["输出", "结论", " outcome", "产出", "响应"],
    "输入": ["input", "起始条件", "前提", "已知条件", "初始值"],
    "是否": ["能不能", "可不可以", "会不会", "有没有可能", "是否存在"],
    "证明": ["验证", "确认", "论证", "推导", "检验"],
    "过程": ["流程", "步骤", "阶段", "序列", "程序"],
    "影响": ["作用", "效果", "后果", "效应", "冲击"],
    "原因": ["起因", "根源", "动机", "因素", "源头"],
    "目标": ["目的", "宗旨", "方向", "使命", "诉求"],
    "环境": ["上下文", "情境", "场景", "背景", "条件"],
    "智能": ["智慧", "认知能力", "理解力", "推理能力", "智力"],
    "模型": ["模型", "表示", "抽象", "形式化", "模式"],
    "函数": ["映射", "变换", "运算", "操作", "规则"],
    "值": ["数值", "量", "大小", "幅度", "程度"],
    # 英文同义词
    "what is": ["explain", "define", "describe", "clarify", "elaborate on"],
    "how to": ["the method for", "a way to", "steps for", "approach to", "procedure for"],
    "why": ["reason for", "cause of", "what leads to", "motivation behind", "basis for"],
    "compute": ["calculate", "derive", "evaluate", "determine", "estimate"],
    "analyze": ["examine", "investigate", "study", "explore", "assess"],
    "compare": ["contrast", "differentiate", "distinguish", "evaluate against", "weigh"],
}


# ============================================================
# 句式变换模板
# ============================================================

_SENTENCE_TEMPLATES = [
    # 0: 原句
    "{question}",
    # 1: 疑问词前置
    "关于{topic}，{question}",
    # 2: 反问式
    "你能告诉我，{question}吗？",
    # 3: 学术式
    "请从专业角度{question}",
    # 4: 简化式
    "简单来说，{question}？",
    # 5: 详细式
    "详细{question}",
    # 6: 条件式
    "在{topic}的框架下，{question}",
    # 7: 递进式
    "进一步来说，{question}？",
    # 8: 验证式
    "如何验证：{question}？",
    # 9: 对比式
    "{question}，与现有方案有何不同？",
    # 10: 目标导向式
    "为了理解{topic}，我们需要：{question}",
    # 11: 重新表述式
    "换句话说，{question}？",
    # 12: 具体化式
    "具体来说，{question}？",
    # 13: 原因探究式
    "从根本原因来看，{question}？",
    # 14: 效果导向式
    "如果我们{question}，会怎样？",
    # 15: 假设式
    "假设需要{question}，应该怎么做？",
]


@dataclass
class ConsistencyResult:
    """一致性验证结果"""
    consistent: bool                    # 是否通过一致性检查
    j_score: float                      # J(R) 一致性分数 [0, 1]
    threshold: float                    # 使用的阈值
    num_variants: int                   # 变体总数
    num_consistent: int                 # 一致的变体数
    num_inconsistent: int               # 不一致的变体数
    variant_hashes: List[str] = field(default_factory=list)   # 各变体输出哈希
    dominant_hash: str = ""             # 主导输出哈希（多数派）
    variant_details: List[Dict] = field(default_factory=list)  # 各变体详情
    generation_time_ms: float = 0.0     # 生成+检查耗时
    lipshitz_approximation: float = 0.0 # Lipschitz 常数近似值


class SelfConsistencyChecker:
    """
    自一致性检查器 — TY/IDO L2壳结构硬化

    核心机制：
    1. 输入扰动：对同一问题生成N种语义等价变体
    2. 管道不变性：所有变体走相同处理函数
    3. 输出比对：比较输出的一致性
    4. J(R) 计算：一致性分数 → Lipschitz 连续性近似

    对应 TY/IDO 验证实验：
    "对同一问题生成 100 种变体，强制系统自检一致性，不一致则拒答"
    """

    def __init__(
        self,
        threshold: float = 0.85,
        max_variants: int = 100,
        lipshitz_K: float = 1.0
    ):
        """
        参数:
            threshold: 一致性阈值，J(R) >= threshold 则通过
            max_variants: 最大变体数量
            lipshitz_K: Lipschitz 常数上界（理论约束）
        """
        self.threshold = threshold
        self.max_variants = max_variants
        self.lipshitz_K = lipshitz_K
        self._check_history: List[Dict] = []

    def generate_variants(self, question: str, num_variants: Optional[int] = None) -> List[str]:
        """
        生成问题的语义等价变体

        策略组合：
        1. 同义词替换 — 逐词替换，保持语义
        2. 句式变换 — 使用预设模板重组
        3. 语序微调 — 交换非关键子句位置

        参数:
            question: 原始问题
            num_variants: 需要的变体数量（默认 max_variants）

        返回:
            List[str]: 变体列表（第一个为原问题）
        """
        n = min(num_variants or self.max_variants, self.max_variants)
        variants = [question]  # 变体0 = 原始问题

        # 提取主题关键词（用于模板填充）
        topic = self._extract_topic(question)

        # 策略1：同义词替换
        synonym_variants = self._synonym_replace(question, max_count=n // 3)
        variants.extend(synonym_variants)

        # 策略2：句式变换
        template_variants = self._template_transform(question, topic, max_count=n // 3)
        variants.extend(template_variants)

        # 策略3：混合（同义词 + 句式）
        mixed_variants = self._mixed_transform(question, topic, max_count=n // 3)
        variants.extend(mixed_variants)

        # 去重 + 截取到目标数量
        seen = set()
        unique_variants = []
        for v in variants:
            h = hashlib.md5(v.encode('utf-8')).hexdigest()
            if h not in seen and v != question:
                seen.add(h)
                unique_variants.append(v)
                if len(unique_variants) >= n - 1:
                    break

        # 确保返回 [原问题, 变体1, 变体2, ...]
        result = [question] + unique_variants
        return result[:n]

    def check(
        self,
        question: str,
        process_fn: Callable[[str], Any],
        num_variants: Optional[int] = None,
        output_extractor: Optional[Callable[[Any], str]] = None
    ) -> ConsistencyResult:
        """
        执行自一致性检查

        参数:
            question: 原始问题
            process_fn: 处理函数，接受问题字符串，返回任意类型的结果
            num_variants: 变体数量
            output_extractor: 从 process_fn 输出中提取可比较字符串的函数
                             默认使用 str(result)

        返回:
            ConsistencyResult
        """
        start_time = time.time()
        n = num_variants or self.max_variants

        # 步骤1：生成变体
        variants = self.generate_variants(question, n)
        actual_n = len(variants)

        # 步骤2：对所有变体执行处理函数
        extract = output_extractor or (lambda x: self._normalize_output(str(x)))
        variant_hashes = []
        variant_outputs = []
        variant_details = []

        for i, variant in enumerate(variants):
            try:
                output = process_fn(variant)
                output_str = extract(output)
                output_hash = hashlib.md5(output_str.encode('utf-8')).hexdigest()

                variant_hashes.append(output_hash)
                variant_outputs.append(output_str)
                variant_details.append({
                    'variant_index': i,
                    'variant_question': variant[:100],
                    'output_hash': output_hash,
                    'output_preview': output_str[:200],
                    'success': True
                })
            except Exception as e:
                # 处理失败视为不一致
                variant_hashes.append(f"ERROR_{i}")
                variant_outputs.append(f"ERROR: {str(e)}")
                variant_details.append({
                    'variant_index': i,
                    'variant_question': variant[:100],
                    'output_hash': f"ERROR_{i}",
                    'error': str(e),
                    'success': False
                })

        # 步骤3：计算一致性
        hash_counts: Dict[str, int] = {}
        for h in variant_hashes:
            hash_counts[h] = hash_counts.get(h, 0) + 1

        # 主导哈希（多数派）
        dominant_hash = max(hash_counts, key=hash_counts.get)
        num_consistent = hash_counts[dominant_hash]
        num_inconsistent = actual_n - num_consistent

        # J(R) = 一致变体数 / 总变体数
        j_score = num_consistent / max(1, actual_n)

        # Lipschitz 常数近似：基于输出差异度
        lipshitz_approx = self._compute_lipshitz_approx(variant_outputs)

        elapsed = (time.time() - start_time) * 1000

        # 步骤4：判定
        consistent = j_score >= self.threshold

        result = ConsistencyResult(
            consistent=consistent,
            j_score=j_score,
            threshold=self.threshold,
            num_variants=actual_n,
            num_consistent=num_consistent,
            num_inconsistent=num_inconsistent,
            variant_hashes=variant_hashes,
            dominant_hash=dominant_hash,
            variant_details=variant_details,
            generation_time_ms=round(elapsed, 2),
            lipshitz_approximation=lipshitz_approx
        )

        # 记录历史
        self._check_history.append({
            'question': question[:100],
            'j_score': j_score,
            'consistent': consistent,
            'timestamp': time.time()
        })

        return result

    # ========================================================
    # 内部方法
    # ========================================================

    def _extract_topic(self, question: str) -> str:
        """提取问题中的主题关键词"""
        # 取第一个实质性短语（去除疑问词后）
        topic = question
        for prefix in ["什么是", "如何", "为什么", "怎么", "请", "怎样", "能否"]:
            if topic.startswith(prefix):
                topic = topic[len(prefix):]
                break
        # 去除标点
        topic = re.sub(r'[？?。，,！!；;]', '', topic).strip()
        # 取前10个字符作为主题
        return topic[:10] if topic else "该问题"

    def _synonym_replace(self, text: str, max_count: int = 10) -> List[str]:
        """同义词替换生成变体"""
        variants = []
        keys_to_replace = [k for k in _SYNONYM_MAP if k in text]
        if not keys_to_replace:
            return variants

        # 对每个可替换词生成一个变体
        random.shuffle(keys_to_replace)
        for key in keys_to_replace[:max_count]:
            synonyms = _SYNONYM_MAP[key]
            synonym = random.choice(synonyms)
            variant = text.replace(key, synonym, 1)  # 只替换第一个出现
            if variant != text:
                variants.append(variant)

        # 组合替换（两个词同时替换）
        if len(keys_to_replace) >= 2:
            for _ in range(min(3, max_count)):
                combo = random.sample(keys_to_replace, min(2, len(keys_to_replace)))
                variant = text
                for key in combo:
                    synonyms = _SYNONYM_MAP.get(key, [])
                    if synonyms:
                        variant = variant.replace(key, random.choice(synonyms), 1)
                if variant != text and variant not in variants:
                    variants.append(variant)

        return variants

    def _template_transform(self, question: str, topic: str, max_count: int = 10) -> List[str]:
        """句式变换生成变体"""
        variants = []
        templates = _SENTENCE_TEMPLATES[1:]  # 跳过原句模板
        random.shuffle(templates)

        for tpl in templates[:max_count]:
            try:
                variant = tpl.format(question=question, topic=topic)
                if variant != question and variant not in variants:
                    variants.append(variant)
            except (KeyError, IndexError):
                pass

        return variants

    def _mixed_transform(self, question: str, topic: str, max_count: int = 10) -> List[str]:
        """混合变换（同义词 + 句式）"""
        variants = []
        # 先做同义词替换
        base_variants = self._synonym_replace(question, max_count=5)
        if not base_variants:
            base_variants = [question]

        for base in base_variants[:3]:
            templates = _SENTENCE_TEMPLATES[1:6]
            random.shuffle(templates)
            for tpl in templates[:2]:
                try:
                    variant = tpl.format(question=base, topic=topic)
                    if variant != question and variant not in variants:
                        variants.append(variant)
                except (KeyError, IndexError):
                    pass

        return variants[:max_count]

    def _normalize_output(self, output: str) -> str:
        """标准化输出用于比较"""
        # 去除空白、统一标点、统一大小写
        normalized = re.sub(r'\s+', '', output)
        normalized = normalized.replace('\n', '').replace('\r', '')
        normalized = normalized.lower()
        # 统一中文标点
        normalized = normalized.replace('？', '?').replace('！', '!').replace('，', ',').replace('。', '.')
        return normalized

    def _compute_lipshitz_approx(self, outputs: List[str]) -> float:
        """
        近似计算 Lipschitz 常数

        L ≈ max(|f(x_i) - f(x_j)|) / max(|x_i - x_j|)

        简化：用输出字符串编辑距离作为 |f(x)| 的代理
        """
        if len(outputs) < 2:
            return 0.0

        normalized = [self._normalize_output(o) for o in outputs]

        # 计算所有输出对之间的归一化编辑距离
        max_dist = 0.0
        count = 0
        for i in range(min(len(normalized), 10)):  # 限制计算量
            for j in range(i + 1, min(len(normalized), 10)):
                s1, s2 = normalized[i], normalized[j]
                if not s1 or not s2:
                    continue
                dist = self._normalized_edit_distance(s1, s2)
                max_dist = max(max_dist, dist)
                count += 1

        return round(max_dist, 6) if count > 0 else 0.0

    def _normalized_edit_distance(self, s1: str, s2: str) -> float:
        """归一化编辑距离 [0, 1]"""
        m, n = len(s1), len(s2)
        if m == 0 and n == 0:
            return 0.0
        if m == 0 or n == 0:
            return 1.0

        # 限制长度避免O(n^2)爆炸
        s1, s2 = s1[:500], s2[:500]
        m, n = len(s1), len(s2)

        # DP 编辑距离
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            prev = dp[0]
            dp[0] = i
            for j in range(1, n + 1):
                temp = dp[j]
                if s1[i - 1] == s2[j - 1]:
                    dp[j] = prev
                else:
                    dp[j] = 1 + min(prev, dp[j], dp[j - 1])
                prev = temp

        return dp[n] / max(m, n)

    def get_state(self) -> Dict[str, Any]:
        """返回检查器状态"""
        total_checks = len(self._check_history)
        avg_j = 0.0
        pass_rate = 0.0
        if total_checks > 0:
            avg_j = sum(c['j_score'] for c in self._check_history) / total_checks
            pass_rate = sum(1 for c in self._check_history if c['consistent']) / total_checks

        return {
            'threshold': self.threshold,
            'max_variants': self.max_variants,
            'total_checks': total_checks,
            'avg_j_score': round(avg_j, 4),
            'pass_rate': round(pass_rate, 4),
            'lipshitz_K': self.lipshitz_K
        }


# ============================================================
# 单例
# ============================================================

_instance: Optional[SelfConsistencyChecker] = None

def get_instance() -> SelfConsistencyChecker:
    """获取全局自一致性检查器单例"""
    global _instance
    if _instance is None:
        _instance = SelfConsistencyChecker()
    return _instance


def get_fresh_instance(threshold: float = 0.85, max_variants: int = 100) -> SelfConsistencyChecker:
    """创建新的检查器实例（用于特殊配置）"""
    return SelfConsistencyChecker(threshold=threshold, max_variants=max_variants)


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TYIDO SelfConsistencyChecker 自测")
    print("=" * 60)

    # 测试1：确定性函数应该100%一致
    def deterministic_fn(q: str) -> str:
        """确定性函数：总是返回相同结构的结果"""
        return f"答案是42，问题包含'{q[:5]}'"

    checker = SelfConsistencyChecker(threshold=0.85, max_variants=20)

    result = checker.check(
        "什么是环境感知？",
        deterministic_fn,
        num_variants=20,
        output_extractor=lambda x: x.split("，")[0]  # 只比较"答案是42"部分
    )

    print(f"\n测试1 - 确定性函数（期望100%一致）:")
    print(f"  J(R) = {result.j_score:.4f}")
    print(f"  consistent = {result.consistent}")
    print(f"  variants = {result.num_variants}")
    print(f"  consistent_variants = {result.num_consistent}")

    # 测试2：变体生成
    print(f"\n测试2 - 变体生成:")
    variants = checker.generate_variants("如何优化系统性能？", num_variants=10)
    for i, v in enumerate(variants):
        print(f"  [{i}] {v[:60]}")

    # 测试3：Lipschitz 近似
    print(f"\n测试3 - Lipschitz 近似:")
    print(f"  L ≈ {result.lipshitz_approximation:.6f}")

    print(f"\n状态: {checker.get_state()}")
    print("\n自测完成!")
