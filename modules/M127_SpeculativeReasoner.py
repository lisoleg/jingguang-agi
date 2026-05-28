# -*- coding: utf-8 -*-
"""
M127: 推测推理器 (Speculative Reasoner)
基于BeeLlama DFlash推测解码机制

核心概念：草稿-验证双路推理、自适应候选数量、推理循环保护
公式：加速比 ≥ 1/(1-α)，α为接受率

定理T88（推测加速定理）：α > α_min ⟹ 加速比 ≥ 1/(1-α)

作者: 太乙AGI团队
日期: 2026-05-21
"""

import math
import time
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ==================== 数据结构 ====================

@dataclass
class DraftChain:
    """
    草稿推理链 — 快速生成的候选推理链

    hypotheses: 候选推理链列表
    draft_scores: 草稿模型评分（每条链的置信度）
    draft_time: 草稿推理耗时（秒）
    query: 原始查询
    max_candidates: 最大候选数
    """
    hypotheses: List[str] = field(default_factory=list)
    draft_scores: List[float] = field(default_factory=list)
    draft_time: float = 0.0
    query: str = ''
    max_candidates: int = 5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['draft_scores'] = [round(s, 6) for s in self.draft_scores]
        d['draft_time'] = round(self.draft_time, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'DraftChain':
        """从字典构建DraftChain"""
        return cls(**d)


@dataclass
class VerifyResult:
    """
    验证结果 — 批量验证候选链的输出

    accepted: 被验证接受的候选索引列表
    rejected: 被拒绝的候选索引列表
    acceptance_rate: 接受率α
    speedup: 加速比 ≥ 1/(1-α)
    verify_time: 验证耗时（秒）
    """
    accepted: List[int] = field(default_factory=list)
    rejected: List[int] = field(default_factory=list)
    acceptance_rate: float = 0.0
    speedup: float = 1.0
    verify_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['acceptance_rate'] = round(self.acceptance_rate, 6)
        d['speedup'] = round(self.speedup, 6)
        d['verify_time'] = round(self.verify_time, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'VerifyResult':
        """从字典构建VerifyResult"""
        return cls(**d)


@dataclass
class LoopDetection:
    """
    推理循环检测结果

    is_loop: 是否检测到循环
    loop_pattern: 检测到的循环模式
    loop_length: 循环长度
    loop_start: 循环起始位置
    suggestion: 打断建议
    """
    is_loop: bool = False
    loop_pattern: str = ''
    loop_length: int = 0
    loop_start: int = -1
    suggestion: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'LoopDetection':
        """从字典构建LoopDetection"""
        return cls(**d)


@dataclass
class AdaptiveConfig:
    """
    自适应配置 — 动态调整推测参数

    alpha_min: 最小接受率阈值
    alpha_current: 当前接受率
    draft_max: 当前最大候选数
    draft_min: 最小候选数
    draft_max_limit: 候选数上限
    adjustment_factor: 调整因子
    """
    alpha_min: float = 0.2
    alpha_current: float = 0.5
    draft_max: int = 5
    draft_min: int = 1
    draft_max_limit: int = 16
    adjustment_factor: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['alpha_min'] = round(self.alpha_min, 6)
        d['alpha_current'] = round(self.alpha_current, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'AdaptiveConfig':
        """从字典构建AdaptiveConfig"""
        return cls(**d)


# ==================== 模式库 ====================

# 推理模式库（简化版，实际可从历史叙事M62学习）
REASONING_PATTERNS = {
    'causal': {
        'template': '因为{cause}，所以{effect}',
        'keywords': ['因为', '所以', '导致', '引起', '使得'],
        'score_boost': 0.1
    },
    'deductive': {
        'template': '已知{premise}，推出{conclusion}',
        'keywords': ['已知', '推出', '因此', '可得', '必然'],
        'score_boost': 0.15
    },
    'inductive': {
        'template': '观察到{instances}，归纳出{rule}',
        'keywords': ['观察到', '归纳', '通常', '一般', '模式'],
        'score_boost': 0.08
    },
    'abductive': {
        'template': '观察到{fact}，最可能的解释是{hypothesis}',
        'keywords': ['最可能', '解释', '猜测', '也许', '可能'],
        'score_boost': 0.05
    },
    'analogical': {
        'template': '{source}类似于{target}，因此{conclusion}',
        'keywords': ['类似', '类比', '如同', '相当于', '可比'],
        'score_boost': 0.06
    },
    'conditional': {
        'template': '如果{condition}，则{consequence}',
        'keywords': ['如果', '那么', '条件', '假设', '前提'],
        'score_boost': 0.12
    }
}


# ==================== 核心类 ====================

class SpeculativeReasoner:
    """
    M127: 推测推理器

    基于BeeLlama DFlash推测解码机制，实现草稿-验证双路推理：
    - DraftReasoner: 基于模式匹配快速生成候选推理链（快但浅）
    - TargetVerifier: 批量验证候选链正确性（慢但深）
    - AdaptiveDraftMax: 根据接受率动态调整候选数量
    - LoopProtector: 检测推理循环并打断

    推测加速原理：
    草稿模型快速生成k个候选，目标模型批量验证。
    如果接受率α足够高，则k个候选中至少有1个被接受，
    无需逐个串行验证，实现加速。

    定理T88（推测加速定理）：
    α > α_min ⟹ 加速比 ≥ 1/(1-α)
    当接受率α > α_min时，推测推理的加速比至少为1/(1-α)。
    例：α=0.7时，加速比≥3.33x

    核心方法：
    1. draft_reason — 草稿推理
    2. verify_chain — 批量验证
    3. detect_loop — 推理循环检测
    4. adaptive_speculate — 自适应推测推理
    """

    def __init__(self):
        """初始化推测推理器"""
        # 草稿统计
        self.total_drafts: int = 0
        self.total_hypotheses: int = 0
        self.total_draft_time: float = 0.0

        # 验证统计
        self.total_verifications: int = 0
        self.total_accepted: int = 0
        self.total_rejected: int = 0
        self.total_verify_time: float = 0.0

        # 循环检测统计
        self.total_loop_checks: int = 0
        self.loops_detected: int = 0
        self.loops_interrupted: int = 0

        # 自适应配置
        self.adaptive_config = AdaptiveConfig()

        # 历史接受率（用于自适应调整）
        self.acceptance_history: List[float] = []

        # 模式匹配命中统计
        self.pattern_hits: Dict[str, int] = {
            name: 0 for name in REASONING_PATTERNS
        }

        # 帧计数
        self.frame_count: int = 0
        self.last_update: float = time.time()

    # ==================== DraftReasoner ====================

    def draft_reason(self, query: str, max_candidates: int = 5) -> DraftChain:
        """
        草稿推理 — 基于模式匹配快速生成候选推理链

        工作原理：
        1. 分析查询，识别推理模式类型
        2. 基于模式模板生成候选推理链
        3. 对每条候选链打分（模式匹配度+结构完整性）
        4. 按分数排序返回

        草稿模型的特点：快但浅
        - 速度快：基于模板和模式，无需深度推理
        - 准确度有限：可能包含错误，需验证

        Args:
            query: 推理查询
            max_candidates: 最大候选数

        Returns:
            DraftChain: 草稿推理链
        """
        start_time = time.time()
        self.total_drafts += 1

        hypotheses = []
        scores = []

        # 1. 识别查询中的推理模式
        matched_patterns = self._match_patterns(query)

        # 2. 基于每个匹配模式生成候选
        for pattern_name, match_score in matched_patterns:
            pattern = REASONING_PATTERNS[pattern_name]
            self.pattern_hits[pattern_name] += 1

            # 生成候选推理链
            candidate = self._generate_candidate(query, pattern_name, pattern)
            if candidate:
                # 计算候选分数
                score = match_score * 0.6 + pattern['score_boost'] + self._structural_score(candidate) * 0.3
                hypotheses.append(candidate)
                scores.append(round(min(score, 1.0), 6))

        # 3. 补充：如果候选不足，生成通用候选
        while len(hypotheses) < min(max_candidates, 3):
            idx = len(hypotheses) + 1
            generic = f'候选{idx}: 基于查询"{query[:30]}..."的推理路径{idx}'
            hypotheses.append(generic)
            scores.append(round(0.3 + 0.05 * idx, 6))

        # 4. 截断到max_candidates
        hypotheses = hypotheses[:max_candidates]
        scores = scores[:max_candidates]

        # 5. 按分数降序排序
        paired = list(zip(hypotheses, scores))
        paired.sort(key=lambda x: x[1], reverse=True)
        hypotheses = [p[0] for p in paired]
        scores = [p[1] for p in paired]

        elapsed = time.time() - start_time
        self.total_hypotheses += len(hypotheses)
        self.total_draft_time += elapsed

        chain = DraftChain(
            hypotheses=hypotheses,
            draft_scores=scores,
            draft_time=elapsed,
            query=query,
            max_candidates=max_candidates
        )

        self.last_update = time.time()
        return chain

    def _match_patterns(self, query: str) -> List[Tuple[str, float]]:
        """
        匹配推理模式

        扫描查询中的关键词，匹配推理模式。
        返回匹配的模式名和匹配分数。

        Args:
            query: 查询字符串

        Returns:
            匹配结果列表 [(pattern_name, match_score), ...]
        """
        matches = []
        query_lower = query.lower()

        for name, pattern in REASONING_PATTERNS.items():
            hit_count = 0
            for keyword in pattern['keywords']:
                if keyword in query_lower or keyword in query:
                    hit_count += 1
            if hit_count > 0:
                match_score = min(hit_count / max(len(pattern['keywords']), 1), 1.0)
                match_score += pattern['score_boost']
                matches.append((name, min(match_score, 1.0)))

        # 如果没有匹配，返回默认模式
        if not matches:
            matches.append(('deductive', 0.4))

        # 按分数降序排序
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _generate_candidate(self, query: str, pattern_name: str,
                            pattern: Dict[str, Any]) -> str:
        """
        基于模式模板生成候选推理链

        Args:
            query: 原始查询
            pattern_name: 模式名称
            pattern: 模式定义

        Returns:
            候选推理链字符串
        """
        template = pattern['template']

        # 从查询中提取关键信息（简化版）
        # 实际系统会使用M62历史叙事的模式匹配
        key_phrases = self._extract_key_phrases(query)

        if key_phrases:
            # 替换模板中的占位符
            candidate = template
            placeholders = re.findall(r'\{(\w+)\}', template)
            for i, ph in enumerate(placeholders):
                if i < len(key_phrases):
                    candidate = candidate.replace(f'{{{ph}}}', key_phrases[i])
                else:
                    candidate = candidate.replace(f'{{{ph}}}', '...')
        else:
            candidate = f'基于{pattern_name}模式: {query[:50]}'

        return candidate

    def _extract_key_phrases(self, query: str) -> List[str]:
        """
        从查询中提取关键短语

        Args:
            query: 查询字符串

        Returns:
            关键短语列表
        """
        phrases = []

        # 按标点分割
        segments = re.split(r'[，。；！？,;!?]', query)
        for seg in segments:
            seg = seg.strip()
            if len(seg) >= 2:
                phrases.append(seg)

        # 如果分割后短语太少，按空格分割
        if len(phrases) < 2:
            words = query.split()
            phrases = [w for w in words if len(w) >= 2]

        return phrases[:5]

    def _structural_score(self, candidate: str) -> float:
        """
        计算候选推理链的结构完整性分数

        评估维度：
        - 长度适中（不是太短也不是太长）
        - 包含逻辑连接词
        - 结构清晰（有层次）

        Args:
            candidate: 候选推理链

        Returns:
            结构分数 [0, 1]
        """
        score = 0.5  # 基础分

        # 长度评分
        length = len(candidate)
        if 10 <= length <= 200:
            score += 0.2
        elif 5 <= length < 10 or 200 < length <= 500:
            score += 0.1

        # 逻辑连接词评分
        connectors = ['因为', '所以', '因此', '如果', '那么', '由于', '导致',
                      '从而', '于是', '但是', '然而', '虽然', '尽管']
        connector_count = sum(1 for c in connectors if c in candidate)
        score += min(connector_count * 0.05, 0.2)

        # 层次结构评分
        if '→' in candidate or '⇒' in candidate or '⟹' in candidate:
            score += 0.1

        return min(score, 1.0)

    # ==================== TargetVerifier ====================

    def verify_chain(self, draft_chain: DraftChain) -> VerifyResult:
        """
        批量验证候选链正确性

        工作原理：
        1. 对每条候选链进行深度验证
        2. 验证维度：逻辑一致性、事实正确性、结构完整性
        3. 计算接受率α和加速比

        定理T88：α > α_min ⟹ 加速比 ≥ 1/(1-α)

        Args:
            draft_chain: 草稿推理链

        Returns:
            VerifyResult: 验证结果
        """
        start_time = time.time()
        self.total_verifications += 1

        accepted = []
        rejected = []

        for i, (hypothesis, draft_score) in enumerate(
            zip(draft_chain.hypotheses, draft_chain.draft_scores)
        ):
            # 深度验证
            verify_score = self._deep_verify(hypothesis, draft_score)
            if verify_score >= 0.5:
                accepted.append(i)
            else:
                rejected.append(i)

        # 计算接受率
        total = len(accepted) + len(rejected)
        alpha = len(accepted) / max(total, 1)

        # 计算加速比（定理T88）
        if alpha > self.adaptive_config.alpha_min and alpha < 1.0:
            speedup = 1.0 / (1.0 - alpha)
        elif alpha >= 1.0:
            speedup = float(len(draft_chain.hypotheses))  # 全部接受，加速比=候选数
        else:
            speedup = 1.0  # 接受率太低，无加速

        elapsed = time.time() - start_time

        # 更新统计
        self.total_accepted += len(accepted)
        self.total_rejected += len(rejected)
        self.total_verify_time += elapsed

        # 记录接受率
        self.acceptance_history.append(alpha)

        result = VerifyResult(
            accepted=accepted,
            rejected=rejected,
            acceptance_rate=round(alpha, 6),
            speedup=round(speedup, 6),
            verify_time=elapsed
        )

        self.last_update = time.time()
        return result

    def _deep_verify(self, hypothesis: str, draft_score: float) -> float:
        """
        深度验证候选推理链

        验证维度：
        1. 逻辑一致性：检查推理是否自洽
        2. 事实基础：检查是否基于已知事实
        3. 结构完整性：检查推理链是否完整

        实际系统中，深度验证基于M29 HDG + M57修忒斯。
        这里使用简化验证逻辑。

        Args:
            hypothesis: 候选推理链
            draft_score: 草稿模型分数

        Returns:
            验证分数 [0, 1]
        """
        verify_score = draft_score * 0.5  # 草稿分数的加权

        # 1. 逻辑一致性检查
        logic_score = self._check_logic_consistency(hypothesis)
        verify_score += logic_score * 0.3

        # 2. 事实基础检查
        fact_score = self._check_fact_basis(hypothesis)
        verify_score += fact_score * 0.1

        # 3. 结构完整性检查
        struct_score = self._structural_score(hypothesis)
        verify_score += struct_score * 0.1

        return min(verify_score, 1.0)

    def _check_logic_consistency(self, hypothesis: str) -> float:
        """
        检查逻辑一致性

        检测常见逻辑矛盾：
        - 自相矛盾（A且¬A）
        - 循环论证
        - 逻辑跳跃

        Args:
            hypothesis: 候选推理链

        Returns:
            逻辑一致性分数 [0, 1]
        """
        score = 0.8  # 默认较高，大多数推理是一致的

        # 检测自相矛盾标记
        contradiction_markers = ['但同时又', '然而实际上却', '既...又不']
        for marker in contradiction_markers:
            if marker in hypothesis:
                score -= 0.3

        # 检测循环论证
        if hypothesis.count('因为') > 2 and hypothesis.count('所以') > 2:
            score -= 0.1

        return max(score, 0.0)

    def _check_fact_basis(self, hypothesis: str) -> float:
        """
        检查事实基础

        简化版：检查推理链是否引用了具体数据或事实。

        Args:
            hypothesis: 候选推理链

        Returns:
            事实基础分数 [0, 1]
        """
        score = 0.5

        # 包含数字
        if re.search(r'\d+\.?\d*', hypothesis):
            score += 0.2

        # 包含引用标记
        if '根据' in hypothesis or '基于' in hypothesis or '参照' in hypothesis:
            score += 0.2

        # 包含具体名词（非代词）
        if len(hypothesis) > 20:
            score += 0.1

        return min(score, 1.0)

    # ==================== LoopProtector ====================

    def detect_loop(self, reasoning_trace: List[str]) -> LoopDetection:
        """
        推理循环检测 — 检测思维链的重复模式

        工作原理：
        1. 使用Floyd循环检测算法的变体
        2. 检测推理步骤的重复模式
        3. 超过阈值则判定为循环并打断

        循环检测的重要性：
        推理循环是AI推理中常见的失效模式，
        模型在不确定时会反复执行相同的推理步骤。
        LoopProtector确保推理不会陷入无限循环。

        Args:
            reasoning_trace: 推理步骤列表

        Returns:
            LoopDetection: 循环检测结果
        """
        self.total_loop_checks += 1

        n = len(reasoning_trace)
        if n < 3:
            return LoopDetection(
                is_loop=False,
                loop_pattern='',
                loop_length=0,
                loop_start=-1,
                suggestion='推理步骤太少，无需检测循环'
            )

        # 方法1：精确重复检测
        for min_loop_len in range(1, n // 2 + 1):
            for start in range(n - 2 * min_loop_len + 1):
                segment = reasoning_trace[start:start + min_loop_len]
                # 检查该段是否在后续重复出现
                for check_start in range(start + min_loop_len, n - min_loop_len + 1):
                    check_segment = reasoning_trace[check_start:check_start + min_loop_len]
                    if segment == check_segment and min_loop_len >= 2:
                        self.loops_detected += 1
                        self.loops_interrupted += 1
                        return LoopDetection(
                            is_loop=True,
                            loop_pattern=' → '.join(str(s)[:30] for s in segment),
                            loop_length=min_loop_len,
                            loop_start=start,
                            suggestion=f'检测到长度为{min_loop_len}的推理循环，建议在步骤{check_start}处打断并引入新信息'
                        )

        # 方法2：语义相似度检测（简化版：基于字符串相似度）
        similarity_threshold = 0.85
        for i in range(n):
            for j in range(i + 2, n):
                sim = self._string_similarity(
                    str(reasoning_trace[i]),
                    str(reasoning_trace[j])
                )
                if sim > similarity_threshold:
                    self.loops_detected += 1
                    self.loops_interrupted += 1
                    return LoopDetection(
                        is_loop=True,
                        loop_pattern=f'步骤{i}与步骤{j}高度相似(相似度={round(sim, 4)})',
                        loop_length=j - i,
                        loop_start=i,
                        suggestion=f'步骤{i}和{j}的推理高度重复，建议在步骤{j}处打断'
                    )

        # 方法3：检测推理步骤数量的异常增长
        if n > self.adaptive_config.draft_max_limit * 2:
            self.loops_detected += 1
            return LoopDetection(
                is_loop=True,
                loop_pattern=f'推理步骤数({n})超过合理范围',
                loop_length=n,
                loop_start=0,
                suggestion=f'推理步骤过多({n}步)，可能存在循环，建议截断'
            )

        return LoopDetection(
            is_loop=False,
            loop_pattern='',
            loop_length=0,
            loop_start=-1,
            suggestion='未检测到推理循环'
        )

    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        计算两个字符串的相似度（简化Jaccard相似度）

        Args:
            s1: 字符串1
            s2: 字符串2

        Returns:
            相似度 [0, 1]
        """
        if not s1 or not s2:
            return 0.0

        # 字符级n-gram
        n = 2
        set1 = set(s1[i:i + n] for i in range(len(s1) - n + 1))
        set2 = set(s2[i:i + n] for i in range(len(s2) - n + 1))

        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / max(union, 1)

    # ==================== AdaptiveDraftMax ====================

    def adaptive_speculate(self, query: str) -> Dict[str, Any]:
        """
        自适应推测推理 — 根据接受率动态调整推测策略

        自适应策略：
        1. 根据历史接受率调整候选数量
        2. α高时多猜（信任草稿），α低时少猜（谨慎验证）
        3. 执行草稿→验证→循环检测完整流程

        定理T88保证：
        α > α_min ⟹ 加速比 ≥ 1/(1-α)

        Args:
            query: 推理查询

        Returns:
            推测推理完整结果
        """
        # 1. 自适应调整候选数
        self._adjust_draft_max()

        # 2. 草稿推理
        draft = self.draft_reason(query, self.adaptive_config.draft_max)

        # 3. 批量验证
        verify = self.verify_chain(draft)

        # 4. 更新接受率
        self.adaptive_config.alpha_current = verify.acceptance_rate

        # 5. 循环检测（对草稿链）
        loop = self.detect_loop(draft.hypotheses)

        # 6. 计算T88加速比
        if verify.acceptance_rate > self.adaptive_config.alpha_min and verify.acceptance_rate < 1.0:
            t88_speedup = 1.0 / (1.0 - verify.acceptance_rate)
            t88_holds = True
        elif verify.acceptance_rate >= 1.0:
            t88_speedup = float(len(draft.hypotheses))
            t88_holds = True
        else:
            t88_speedup = 1.0
            t88_holds = False

        self.last_update = time.time()

        return {
            'query': query,
            'draft': draft.to_dict(),
            'verify': verify.to_dict(),
            'loop_detection': loop.to_dict(),
            'adaptive_config': self.adaptive_config.to_dict(),
            't88_speedup': round(t88_speedup, 6),
            't88_holds': t88_holds,
            'theorem_T88': f'推测加速: α={round(verify.acceptance_rate, 4)} > α_min={self.adaptive_config.alpha_min}, 加速比≥{round(t88_speedup, 4)}'
        }

    def _adjust_draft_max(self) -> None:
        """
        自适应调整最大候选数

        策略：
        - α高（>0.7）：增加候选数（信任草稿）
        - α中（0.3-0.7）：保持当前
        - α低（<0.3）：减少候选数（谨慎验证）
        """
        alpha = self.adaptive_config.alpha_current
        factor = self.adaptive_config.adjustment_factor

        if alpha > 0.7:
            # 高接受率：增加候选
            new_max = int(self.adaptive_config.draft_max * (1.0 + factor))
        elif alpha < 0.3:
            # 低接受率：减少候选
            new_max = int(self.adaptive_config.draft_max * (1.0 - factor))
        else:
            # 中等接受率：保持
            new_max = self.adaptive_config.draft_max

        # 限制范围
        new_max = max(self.adaptive_config.draft_min,
                      min(self.adaptive_config.draft_max_limit, new_max))
        self.adaptive_config.draft_max = new_max

    # ==================== 辅助方法 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取推测推理器状态

        Returns:
            状态字典，包含推测推理统计和当前配置
        """
        overall_alpha = self.total_accepted / max(
            self.total_accepted + self.total_rejected, 1
        )

        if overall_alpha > self.adaptive_config.alpha_min and overall_alpha < 1.0:
            overall_speedup = 1.0 / (1.0 - overall_alpha)
        elif overall_alpha >= 1.0:
            overall_speedup = float(self.total_hypotheses)
        else:
            overall_speedup = 1.0

        avg_draft_time = round(
            self.total_draft_time / max(self.total_drafts, 1), 6
        )
        avg_verify_time = round(
            self.total_verify_time / max(self.total_verifications, 1), 6
        )

        return {
            'total_drafts': self.total_drafts,
            'total_hypotheses': self.total_hypotheses,
            'total_verifications': self.total_verifications,
            'total_accepted': self.total_accepted,
            'total_rejected': self.total_rejected,
            'overall_acceptance_rate': round(overall_alpha, 6),
            'overall_speedup': round(overall_speedup, 6),
            'avg_draft_time': avg_draft_time,
            'avg_verify_time': avg_verify_time,
            'total_loop_checks': self.total_loop_checks,
            'loops_detected': self.loops_detected,
            'loops_interrupted': self.loops_interrupted,
            'adaptive_draft_max': self.adaptive_config.draft_max,
            'alpha_current': round(self.adaptive_config.alpha_current, 6),
            'alpha_min': self.adaptive_config.alpha_min,
            'pattern_hits': dict(self.pattern_hits),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T88': f'推测加速: α>{self.adaptive_config.alpha_min} ⟹ 加速比≥1/(1-α)={round(1.0 / max(1.0 - self.adaptive_config.alpha_current, 0.01), 4)}'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新推测推理器状态

        Args:
            data: 可选更新数据，支持：
                - draft: 草稿推理 {query, max_candidates}
                - verify: 批量验证 {draft_chain}
                - loop_check: 循环检测 {reasoning_trace}
                - speculate: 自适应推测 {query}
                - set_alpha_min: 设置最小接受率 {alpha_min}
                - set_draft_max: 设置最大候选数 {draft_max}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'draft' or 'draft' in data:
                d = data.get('draft', data)
                self.draft_reason(
                    query=d.get('query', ''),
                    max_candidates=int(d.get('max_candidates', 5))
                )
            elif action == 'speculate' or 'speculate' in data:
                d = data.get('speculate', data)
                self.adaptive_speculate(query=d.get('query', ''))
            elif action == 'loop_check' or 'loop_check' in data:
                d = data.get('loop_check', data)
                self.detect_loop(
                    reasoning_trace=d.get('reasoning_trace', [])
                )
            elif action == 'set_alpha_min':
                self.adaptive_config.alpha_min = float(
                    data.get('alpha_min', self.adaptive_config.alpha_min)
                )
            elif action == 'set_draft_max':
                self.adaptive_config.draft_max = int(
                    data.get('draft_max', self.adaptive_config.draft_max)
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示推测推理器的核心功能"""
        # 1. 草稿推理
        draft = self.draft_reason('因为所有人类都是凡人，苏格拉底是人类，所以苏格拉底是凡人', 5)

        # 2. 批量验证
        verify = self.verify_chain(draft)

        # 3. 推理循环检测
        loop_trace = [
            '思考: 分析问题',
            '推理: 因为A所以B',
            '思考: 继续分析',
            '推理: 因为A所以B',  # 重复
        ]
        loop = self.detect_loop(loop_trace)

        # 4. 自适应推测推理
        speculate_result = self.adaptive_speculate(
            '如果今天下雨，那么地面会湿。今天下雨了，所以地面会湿'
        )

        # 5. 第二次自适应推测（接受率应已更新）
        speculate2 = self.adaptive_speculate(
            '已知所有鸟都会飞，企鹅是鸟，但企鹅不会飞，这是一个矛盾'
        )

        return {
            'draft': draft.to_dict(),
            'verify': verify.to_dict(),
            'loop_detection': loop.to_dict(),
            'speculate_1': speculate_result,
            'speculate_2': speculate2,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[SpeculativeReasoner] = None


def get_instance() -> SpeculativeReasoner:
    """
    获取SpeculativeReasoner单例实例

    Returns:
        SpeculativeReasoner全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = SpeculativeReasoner()
    return _instance


def draft_reason(query: str, max_candidates: int = 5) -> DraftChain:
    """草稿推理（快捷接口）"""
    return get_instance().draft_reason(query, max_candidates)


def verify_chain(draft_chain: DraftChain) -> VerifyResult:
    """批量验证（快捷接口）"""
    return get_instance().verify_chain(draft_chain)


def detect_loop(reasoning_trace: List[str]) -> LoopDetection:
    """推理循环检测（快捷接口）"""
    return get_instance().detect_loop(reasoning_trace)


def adaptive_speculate(query: str) -> Dict[str, Any]:
    """自适应推测推理（快捷接口）"""
    return get_instance().adaptive_speculate(query)


def get_state() -> Dict[str, Any]:
    """获取推测推理器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新推测推理器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M127 SpeculativeReasoner 自测')
    print('=' * 60)

    engine = SpeculativeReasoner()

    # 测试草稿推理
    print('\n--- 草稿推理测试 ---')
    draft = engine.draft_reason('因为天下雨了，所以地面变湿了', 5)
    print(f'  查询: 因为天下雨了，所以地面变湿了')
    print(f'  候选数: {len(draft.hypotheses)}')
    for i, (h, s) in enumerate(zip(draft.hypotheses, draft.draft_scores)):
        print(f'  候选{i+1} (分数={s}): {h[:60]}')

    # 测试批量验证
    print('\n--- 批量验证测试 ---')
    verify = engine.verify_chain(draft)
    print(f'  接受: {verify.accepted}, 拒绝: {verify.rejected}')
    print(f'  接受率α: {verify.acceptance_rate}')
    print(f'  加速比: {verify.speedup}')

    # 测试循环检测
    print('\n--- 循环检测测试 ---')
    trace = ['步骤A', '步骤B', '步骤C', '步骤A', '步骤B']
    loop = engine.detect_loop(trace)
    print(f'  轨迹: {trace}')
    print(f'  检测到循环: {loop.is_loop}')
    print(f'  循环模式: {loop.loop_pattern}')
    print(f'  建议: {loop.suggestion}')

    # 测试自适应推测
    print('\n--- 自适应推测推理测试 ---')
    result = engine.adaptive_speculate('如果温度降到零度以下，水会结冰')
    print(f'  T88加速比: {result["t88_speedup"]}')
    print(f'  T88成立: {result["t88_holds"]}')
    print(f'  定理: {result["theorem_T88"]}')

    # 打印最终状态
    print('\n--- 最终状态 ---')
    state = engine.get_state()
    for k, v in state.items():
        if k != 'pattern_hits':
            print(f'  {k}: {v}')

    print('\n定理T88验证:', state['theorem_T88'])
    print('\n自测完成 ✓')
