# -*- coding: utf-8 -*-
"""
M231 FailureAttributor — 失败归因引擎
========================================
借鉴 PhoneHarness 的 Failure Attribution 概念，将太乙AGI测试失败
从笼统的"没做对"升级为精确定位的归因分析。

五大归因类别 (PhoneHarness映射):
  1. Controller Error — 规划/路由错误 (选错了动作面/策略)
  2. Worker Error    — 执行错误 (模块内操作失败)
  3. Tool Error      — 工具依赖失败 (AkashaChainDB/API不可用)
  4. Environment Error — 环境问题 (沙箱限制/权限不足/Python版本)
  5. Verifier Error  — 验证器假阳性 (正确结果被误判为失败)

核心方法论:
  失败不是终点，而是诊断的起点。
  "不是笼统的'没做对'，而是精确定位——是规划问题、执行问题、
   工具问题、环境问题还是验证问题？"

设计定理 T2.46: 归因完备性
  对于任何失败F，归因引擎能将F分类到
  {Controller, Worker, Tool, Environment, Verifier}中至少一个类别
  即: ∀F: failed(F) ⟹ ∃c ∈ Categories: attribute(F) = c

Author: 太乙AGI v7.33c (PhoneHarness Inspiration)
"""

import time
import traceback
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class AttributionCategory(Enum):
    """五大归因类别"""
    CONTROLLER = "controller"    # 规划/路由错误
    WORKER = "worker"            # 执行错误
    TOOL = "tool"                # 工具依赖失败
    ENVIRONMENT = "environment"  # 环境问题
    VERIFIER = "verifier"        # 验证器假阳性


# 归因关键词映射
CATEGORY_PATTERNS: Dict[AttributionCategory, Dict[str, List[str]]] = {
    AttributionCategory.CONTROLLER: {
        'error_patterns': [
            'route', 'routing', 'wrong surface', 'misrouted',
            '规划', '路由', '策略', '选择错误',
        ],
        'exception_types': ['ValueError', 'RoutingError'],
        'description': '规划/路由层面: 选择了错误的动作面或策略',
        'fix_hint': '检查任务描述是否清晰, 调整路由关键词映射',
    },
    AttributionCategory.WORKER: {
        'error_patterns': [
            'compute', 'calculation', 'implementation', 'logic',
            '计算', '实现', '逻辑', '算法', 'assertion',
        ],
        'exception_types': ['AssertionError', 'RuntimeError', 'ZeroDivisionError'],
        'description': '执行层面: 模块内部操作/计算/逻辑错误',
        'fix_hint': '检查模块核心逻辑, 修正算法实现',
    },
    AttributionCategory.TOOL: {
        'error_patterns': [
            'import', 'module', 'dependency', 'not found', 'missing',
            '导入', '依赖', '找不到', '缺少', 'No module',
            'akasha', 'database', 'connection',
        ],
        'exception_types': ['ImportError', 'ModuleNotFoundError', 'ConnectionError'],
        'description': '工具层面: 外部依赖/数据库/API不可用',
        'fix_hint': '检查依赖安装, 确认外部服务可用',
    },
    AttributionCategory.ENVIRONMENT: {
        'error_patterns': [
            'permission', 'sandbox', 'timeout', 'memory', 'disk',
            '权限', '沙箱', '超时', '内存', 'lock',
            'index.lock', 'python version', 'numpy',
        ],
        'exception_types': ['PermissionError', 'TimeoutError', 'OSError'],
        'description': '环境层面: 沙箱限制/权限/版本/资源不足',
        'fix_hint': '调整沙箱策略, 检查Python版本, 增加资源',
    },
    AttributionCategory.VERIFIER: {
        'error_patterns': [
            'threshold', 'tolerance', 'false positive', 'precision',
            '阈值', '容差', '假阳性', '精度',
            'float', 'rounding', 'epsilon',
        ],
        'exception_types': [],
        'description': '验证层面: 正确结果被误判(阈值/精度/容差问题)',
        'fix_hint': '调整验证阈值, 使用相对误差代替绝对误差',
    },
}


@dataclass
class FailureRecord:
    """失败记录"""
    failure_id: str
    test_name: str
    error_message: str
    exception_type: str = ""
    traceback_str: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class AttributionResult:
    """归因结果"""
    failure_id: str
    primary_category: AttributionCategory
    confidence: float          # 归因置信度 [0, 1]
    all_scores: Dict[str, float]  # 各类别得分
    evidence: List[str]        # 归因证据
    fix_suggestion: str        # 修复建议
    secondary_categories: List[AttributionCategory] = field(default_factory=list)
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class RootCause:
    """根因分析结果"""
    root_category: AttributionCategory
    root_evidence: str
    chain: List[Dict[str, Any]] = field(default_factory=list)
    suggested_fix: str = ""


class FailureAttributor:
    """
    M231 失败归因引擎

    核心能力:
      - attribute_failure(): 对失败测试进行归因
      - trace_root_cause(): 追踪根因链
      - suggest_fix(): 生成修复建议
      - batch_attribute(): 批量归因
    """

    def __init__(self):
        self._attributions: Dict[str, AttributionResult] = {}
        self._failure_counter = 0
        self._version = "v7.33c"

    # ─── 核心归因 ──────────────────────────────

    def _compute_category_scores(self, failure: FailureRecord) -> Dict[AttributionCategory, float]:
        """
        计算失败对各归因类别的匹配得分

        策略:
          1. 错误信息关键词匹配: 每个命中 +1.0
          2. 异常类型匹配: 精确匹配 +3.0
          3. 堆栈跟踪关键词: 每个命中 +0.5
        """
        scores = {cat: 0.0 for cat in AttributionCategory}
        combined_text = f"{failure.error_message} {failure.traceback_str}".lower()

        for cat, patterns in CATEGORY_PATTERNS.items():
            # 关键词匹配
            for kw in patterns['error_patterns']:
                if kw.lower() in combined_text:
                    scores[cat] += 1.0

            # 异常类型匹配
            if failure.exception_type:
                for exc_type in patterns['exception_types']:
                    if exc_type.lower() in failure.exception_type.lower():
                        scores[cat] += 3.0

        return scores

    def attribute_failure(self, test_name: str, error_message: str,
                          exception_type: str = "",
                          traceback_str: str = "") -> AttributionResult:
        """
        对失败测试进行归因

        Args:
            test_name: 测试名称
            error_message: 错误信息
            exception_type: 异常类型
            traceback_str: 堆栈跟踪

        Returns:
            AttributionResult
        """
        self._failure_counter += 1
        failure_id = f"FAIL-{self._failure_counter:04d}"

        failure = FailureRecord(
            failure_id=failure_id,
            test_name=test_name,
            error_message=error_message,
            exception_type=exception_type,
            traceback_str=traceback_str,
        )

        # 计算各类别得分
        scores = self._compute_category_scores(failure)

        # 选择最高分类别
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if sorted_cats[0][1] > 0:
            primary = sorted_cats[0][0]
            total_score = sum(s for _, s in sorted_cats)
            confidence = sorted_cats[0][1] / max(total_score, 0.001)
        else:
            # 无匹配 → 默认归因到Worker(执行层)
            primary = AttributionCategory.WORKER
            confidence = 0.3

        # 收集证据
        evidence = []
        patterns = CATEGORY_PATTERNS[primary]
        combined_text = f"{error_message} {traceback_str}".lower()
        for kw in patterns['error_patterns']:
            if kw.lower() in combined_text:
                evidence.append(f"关键词命中: '{kw}'")
        if exception_type:
            for exc_type in patterns['exception_types']:
                if exc_type.lower() in exception_type.lower():
                    evidence.append(f"异常类型匹配: '{exc_type}'")

        if not evidence:
            evidence.append(f"默认归因: 无明确关键词匹配")

        # 次要类别
        secondary = [cat for cat, score in sorted_cats[1:3] if score > 0]

        result = AttributionResult(
            failure_id=failure_id,
            primary_category=primary,
            confidence=round(confidence, 4),
            all_scores={cat.value: round(sc, 4) for cat, sc in scores.items()},
            evidence=evidence,
            fix_suggestion=patterns['fix_hint'],
            secondary_categories=secondary,
        )

        self._attributions[failure_id] = result
        return result

    # ─── 根因追踪 ──────────────────────────────

    def trace_root_cause(self, failure_ids: List[str] = None) -> RootCause:
        """
        追踪根因链

        分析多个失败之间的共同模式，找到根因
        """
        if failure_ids:
            results = [self._attributions[fid] for fid in failure_ids if fid in self._attributions]
        else:
            results = list(self._attributions.values())

        if not results:
            return RootCause(
                root_category=AttributionCategory.WORKER,
                root_evidence="无失败记录",
                suggested_fix="无需修复",
            )

        # 统计各类别出现频率
        cat_counts: Dict[AttributionCategory, int] = {}
        for r in results:
            cat_counts[r.primary_category] = cat_counts.get(r.primary_category, 0) + 1

        root_cat = max(cat_counts, key=cat_counts.get)
        root_count = cat_counts[root_cat]

        # 构建根因链
        chain = []
        for r in results:
            if r.primary_category == root_cat:
                chain.append({
                    'failure_id': r.failure_id,
                    'category': r.primary_category.value,
                    'confidence': r.confidence,
                    'evidence': r.evidence[:2],  # 取前2条证据
                })

        patterns = CATEGORY_PATTERNS[root_cat]

        return RootCause(
            root_category=root_cat,
            root_evidence=f"{root_count}/{len(results)} 失败归因到 {root_cat.value}",
            chain=chain,
            suggested_fix=patterns['fix_hint'],
        )

    # ─── 修复建议 ──────────────────────────────

    def suggest_fix(self, attribution: AttributionResult) -> Dict:
        """生成修复建议"""
        cat = attribution.primary_category
        patterns = CATEGORY_PATTERNS[cat]

        return {
            'failure_id': attribution.failure_id,
            'category': cat.value,
            'confidence': attribution.confidence,
            'diagnosis': patterns['description'],
            'fix_hint': patterns['fix_hint'],
            'evidence': attribution.evidence,
            'secondary': [c.value for c in attribution.secondary_categories],
        }

    # ─── 批量归因 ──────────────────────────────

    def batch_attribute(self, failures: List[Dict]) -> Dict:
        """批量归因"""
        results = []
        for f in failures:
            attr = self.attribute_failure(
                test_name=f.get('test_name', 'unknown'),
                error_message=f.get('error_message', ''),
                exception_type=f.get('exception_type', ''),
                traceback_str=f.get('traceback_str', ''),
            )
            results.append(attr)

        # 统计
        cat_dist = {}
        for r in results:
            cat = r.primary_category.value
            cat_dist[cat] = cat_dist.get(cat, 0) + 1

        return {
            'total_failures': len(results),
            'category_distribution': cat_dist,
            'attributions': [{
                'failure_id': r.failure_id,
                'category': r.primary_category.value,
                'confidence': r.confidence,
                'fix_hint': r.fix_suggestion,
            } for r in results],
        }

    # ─── 定理验证 T2.46 ─────────────────────────

    def verify_theorem(self) -> Dict:
        """
        定理 T2.46: 归因完备性

        对于任何失败F，归因引擎能将F分类到
        {Controller, Worker, Tool, Environment, Verifier}中至少一个类别

        验证方法:
          1. 构造覆盖5类归因的失败样本
          2. 对每个失败执行归因
          3. 验证归因结果不为空且类别有效
          4. 验证主要归因类别与预期一致
        """
        test_failures = [
            {
                'test_name': 'test_route_to_ice',
                'error_message': '路由错误: 选择了UA通道而非ICE形式化验证通道',
                'exception_type': 'ValueError',
                'expected_category': AttributionCategory.CONTROLLER,
            },
            {
                'test_name': 'test_eml_computation',
                'error_message': 'AssertionError: eml_add(5,3) 计算结果不匹配',
                'exception_type': 'AssertionError',
                'expected_category': AttributionCategory.WORKER,
            },
            {
                'test_name': 'test_akasha_import',
                'error_message': 'ImportError: No module named modules.M190_AkashaChainDB',
                'exception_type': 'ModuleNotFoundError',
                'expected_category': AttributionCategory.TOOL,
            },
            {
                'test_name': 'test_git_push',
                'error_message': 'PermissionError: .git/index.lock 沙箱权限被阻断',
                'exception_type': 'PermissionError',
                'expected_category': AttributionCategory.ENVIRONMENT,
            },
            {
                'test_name': 'test_liu_equilibrium',
                'error_message': '验证阈值过严: 变分0.099超过threshold=0.1被误判为不平衡',
                'exception_type': '',
                'expected_category': AttributionCategory.VERIFIER,
            },
            # 额外: 模糊错误(应归因到Worker默认)
            {
                'test_name': 'test_unknown_error',
                'error_message': '未知错误发生',
                'exception_type': '',
                'expected_category': AttributionCategory.WORKER,  # 默认
            },
        ]

        part_a_pass = True  # 每个失败都有归因
        part_b_pass = True  # 归因类别有效
        part_c_pass = True  # 主要归因与预期一致(至少5/6)
        correct_count = 0
        details = []

        for tf in test_failures:
            attr = self.attribute_failure(
                test_name=tf['test_name'],
                error_message=tf['error_message'],
                exception_type=tf['exception_type'],
            )

            # Part A: 归因不为空
            has_attribution = attr.primary_category is not None
            part_a_pass = part_a_pass and has_attribution

            # Part B: 类别有效
            valid_category = attr.primary_category in AttributionCategory
            part_b_pass = part_b_pass and valid_category

            # Part C: 与预期一致
            matches = attr.primary_category == tf['expected_category']
            if matches:
                correct_count += 1

            details.append({
                'test': tf['test_name'],
                'expected': tf['expected_category'].value,
                'actual': attr.primary_category.value,
                'match': matches,
                'confidence': attr.confidence,
            })

        part_c_pass = correct_count >= len(test_failures) - 1  # 允许1个偏差

        theorem_pass = part_a_pass and part_b_pass and part_c_pass

        return {
            'pass': theorem_pass,
            'theorem': 'T2.46',
            'description': '归因完备性: ∀F: failed(F) ⟹ ∃c ∈ Categories: attribute(F) = c',
            'parts': {
                'A_attribution_exists': {
                    'pass': part_a_pass,
                    'desc': '每个失败都有归因结果',
                },
                'B_valid_category': {
                    'pass': part_b_pass,
                    'desc': '归因类别属于五大类别',
                },
                'C_accuracy': {
                    'pass': part_c_pass,
                    'desc': f'归因准确性: {correct_count}/{len(test_failures)}',
                    'correct': correct_count,
                    'total': len(test_failures),
                    'details': details,
                },
            },
        }

    # ─── 模块接口 ──────────────────────────────

    def get_state(self) -> Dict:
        """模块状态查询"""
        cat_dist = {}
        for r in self._attributions.values():
            cat = r.primary_category.value
            cat_dist[cat] = cat_dist.get(cat, 0) + 1

        return {
            'version': self._version,
            'module': 'M231_FailureAttributor',
            'total_attributions': len(self._attributions),
            'category_distribution': cat_dist,
            'theorem': 'T2.46',
            'categories': [c.value for c in AttributionCategory],
        }


# ─── 单例 ────────────────────────────────────

_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = FailureAttributor()
    return _instance
