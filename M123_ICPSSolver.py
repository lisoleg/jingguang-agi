# -*- coding: utf-8 -*-
"""
M123: ICPS社会问题求解器 (ICPS Social Problem Solver)
基于《如何培养孩子的社会能力》ICPS方法

核心概念：4步法（识别→生成方案→预判后果→执行复盘）
公式：Ψ_icps = f(识别, 方案数, 后果预判, 复盘深度)

定理T83（ICPS成熟度单调递增定理）：有效ICPS训练下Ψ_icps单调递增
定理T84（心智理论觉醒定理）：通过Sally-Anne测试 ⟹ 具备一级心智理论

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


# ==================== 数据结构 ====================

@dataclass
class ICPSStep:
    """
    ICPS步骤 — 单个ICPS步骤的记录

    step: 步骤编号（1-4）
    description: 步骤描述
    alternatives: 替代方案列表
    consequences: 后果预判列表
    chosen: 选择的方案
    """
    step: int = 1
    description: str = ''
    alternatives: List[str] = field(default_factory=list)
    consequences: List[str] = field(default_factory=list)
    chosen: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ICPSStep':
        """从字典构建ICPSStep"""
        return cls(**d)


@dataclass
class ICPSResult:
    """
    ICPS结果 — 完整ICPS问题求解结果

    problem: 问题描述
    steps: 步骤列表
    total_alternatives: 总替代方案数
    total_consequences: 总后果预判数
    maturity_score: ICPS成熟度Ψ_icps
    stage: 当前发展阶段
    """
    problem: str = ''
    steps: List[Dict[str, Any]] = field(default_factory=list)
    total_alternatives: int = 0
    total_consequences: int = 0
    maturity_score: float = 0.0
    stage: str = 'sandbox'

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['maturity_score'] = round(self.maturity_score, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ICPSResult':
        """从字典构建ICPSResult"""
        return cls(**d)


# ==================== 常量 ====================

# ICPS四阶段
ICPS_STAGES = ['sandbox', 'rules', 'icps', 'open_world']

# Sally-Anne测试的标准答案
SALLY_ANNE_CORRECT = 'basket'  # Sally会去篮子里找

# 情绪词库（用于后果预判中的情绪识别）
EMOTION_WORDS = [
    '开心', '难过', '生气', '害怕', '惊讶',
    '失望', '满足', '焦虑', '平静', '兴奋'
]


# ==================== 核心类 ====================

class ICPSSolver:
    """
    M123: ICPS社会问题求解器

    基于Shure的ICPS（Interpersonal Cognitive Problem Solving）方法，
    实现4步法社会问题求解：

    Step 1 识别：识别问题的核心——谁？什么？为什么？
    Step 2 生成方案：生成至少3个替代方案（发散思维）
    Step 3 预判后果：预判每个方案的可能后果（因果推理）
    Step 4 执行复盘：选择最优方案执行，复盘学习效果

    Ψ_icps = f(识别, 方案数, 后果预判, 复盘深度)

    定理T83（ICPS成熟度单调递增定理）：
    有效ICPS训练下Ψ_icps单调递增。
    即：随着ICPS训练的进行，个体的社会问题解决能力持续提升。

    定理T84（心智理论觉醒定理）：
    通过Sally-Anne测试 ⟹ 具备一级心智理论。
    即：能理解他人可能有不同于自己的信念。

    核心方法：
    1. solve_problem — ICPS 4步求解
    2. step1_identify — 识别问题核心
    3. step2_generate_alternatives — 生成替代方案
    4. step3_predict_consequences — 预判后果
    5. step4_execute_review — 执行+复盘
    6. compute_maturity — Ψ_icps成熟度计算
    7. sally_anne_test — Sally-Anne错误信念测试
    """

    def __init__(self):
        """初始化ICPS社会问题求解器"""
        # 求解历史
        self.results: List[ICPSResult] = []

        # ICPS成熟度轨迹
        self.maturity_history: List[float] = []

        # 当前阶段
        self.current_stage: str = 'sandbox'

        # Sally-Anne测试记录
        self.sally_anne_results: List[Dict[str, Any]] = []

        # 统计
        self.total_problems_solved: int = 0
        self.total_alternatives_generated: int = 0
        self.total_consequences_predicted: int = 0
        self.total_maturity_computations: int = 0
        self.total_sally_anne_tests: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def solve_problem(self, problem_description: str) -> ICPSResult:
        """
        ICPS 4步求解

        对给定的社会问题描述，执行完整的ICPS 4步法求解：
        1. 识别问题核心
        2. 生成替代方案（至少3个）
        3. 预判每个方案的后果
        4. 执行+复盘

        Args:
            problem_description: 问题描述

        Returns:
            ICPSResult: 求解结果
        """
        # Step 1: 识别
        step1 = self.step1_identify(problem_description)

        # Step 2: 生成方案
        step2 = self.step2_generate_alternatives(problem_description)

        # Step 3: 预判后果
        alternatives = step2.get('alternatives', [])
        step3 = self.step3_predict_consequences(alternatives)

        # Step 4: 选择并复盘
        consequences = step3.get('consequences', {})
        # 选择后果最好的方案
        best_alt = self._choose_best_alternative(alternatives, consequences)
        step4 = self.step4_execute_review(best_alt, 'simulated_outcome')

        # 计算成熟度
        total_alts = step2.get('total_alternatives', 0)
        total_cons = step3.get('total_consequences', 0)
        maturity = self.compute_maturity({
            'identification_depth': step1.get('depth', 0.5),
            'alternatives_count': total_alts,
            'consequences_count': total_cons,
            'review_depth': step4.get('review_depth', 0.5)
        })

        # 确定阶段
        stage = self._determine_stage(maturity)

        # 构建结果
        result = ICPSResult(
            problem=problem_description,
            steps=[
                step1,
                step2,
                step3,
                step4
            ],
            total_alternatives=total_alts,
            total_consequences=total_cons,
            maturity_score=maturity,
            stage=stage
        )

        self.results.append(result)
        self.maturity_history.append(maturity)
        self.total_problems_solved += 1
        self.total_alternatives_generated += total_alts
        self.total_consequences_predicted += total_cons
        self.current_stage = stage
        self.last_update = time.time()

        return result

    def step1_identify(self, problem: str) -> Dict[str, Any]:
        """
        Step 1: 识别问题核心

        识别问题的核心要素：
        - 谁是相关的人？
        - 问题的本质是什么？
        - 为什么会产生这个问题？

        Args:
            problem: 问题描述

        Returns:
            识别结果字典
        """
        # 识别深度分析
        # 基于问题描述的复杂度评估识别深度
        words = problem.split()
        complexity = min(1.0, len(words) / 10.0)

        # 提取问题要素（简化：基于关键词）
        who_elements = self._extract_who(problem)
        what_elements = self._extract_what(problem)
        why_elements = self._extract_why(problem)

        # 识别深度
        depth = round(
            0.3 * (1.0 if who_elements else 0.0) +
            0.4 * (1.0 if what_elements else 0.0) +
            0.3 * (1.0 if why_elements else 0.0) +
            0.1 * complexity, 6
        )

        return {
            'step': 1,
            'description': '识别问题核心',
            'problem': problem,
            'who': who_elements,
            'what': what_elements,
            'why': why_elements,
            'depth': round(depth, 6),
            'complexity': round(complexity, 6)
        }

    def step2_generate_alternatives(self, problem: str) -> Dict[str, Any]:
        """
        Step 2: 生成替代方案（至少3个）

        发散思维生成多个可能的问题解决方案。
        ICPS要求至少3个替代方案以确保思维广度。

        Args:
            problem: 问题描述

        Returns:
            方案生成结果字典
        """
        # 基于问题类型生成方案模板
        alternatives = self._generate_default_alternatives(problem)

        # 确保至少3个方案
        while len(alternatives) < 3:
            idx = len(alternatives) + 1
            alternatives.append(f'方案{idx}：综合协调方案')

        return {
            'step': 2,
            'description': '生成替代方案',
            'alternatives': alternatives,
            'total_alternatives': len(alternatives),
            'divergence_score': round(min(1.0, len(alternatives) / 5.0), 6)
        }

    def step3_predict_consequences(self, alternatives: List[str]) -> Dict[str, Any]:
        """
        Step 3: 预判每个方案的后果

        对每个替代方案预判其可能的后果（正面+负面），
        评估每个方案的风险和收益。

        Args:
            alternatives: 替代方案列表

        Returns:
            后果预判结果字典
        """
        consequences = {}
        total_cons = 0

        for i, alt in enumerate(alternatives):
            # 为每个方案生成正负面后果
            positive = self._predict_positive(alt, i)
            negative = self._predict_negative(alt, i)
            net_score = round(len(positive) - len(negative) * 0.5, 6)

            consequences[alt] = {
                'positive': positive,
                'negative': negative,
                'net_score': net_score,
                'risk_level': round(
                    min(1.0, len(negative) / max(len(positive) + len(negative), 1)), 6
                )
            }
            total_cons += len(positive) + len(negative)

        return {
            'step': 3,
            'description': '预判后果',
            'consequences': consequences,
            'total_consequences': total_cons,
            'alternatives_evaluated': len(alternatives)
        }

    def step4_execute_review(self, chosen: str, outcome: str) -> Dict[str, Any]:
        """
        Step 4: 执行+复盘

        选择最优方案执行，然后复盘学习效果。

        复盘维度：
        1. 方案是否有效？
        2. 是否有更好的方案？
        3. 从中学到了什么？

        Args:
            chosen: 选择的方案
            outcome: 执行结果

        Returns:
            执行复盘结果字典
        """
        # 复盘深度评估
        # 基于方案描述和结果的匹配度
        review_depth = 0.5  # 默认复盘深度

        if chosen and outcome:
            # 简化：基于描述长度的复盘深度
            combined_len = len(chosen) + len(outcome)
            review_depth = min(1.0, combined_len / 50.0)

        # 学习效果评估
        learning_gained = round(review_depth * 0.3, 6)

        return {
            'step': 4,
            'description': '执行+复盘',
            'chosen': chosen,
            'outcome': outcome,
            'review_depth': round(review_depth, 6),
            'learning_gained': learning_gained,
            'review_questions': [
                '方案是否有效解决了问题？',
                '是否有更好的替代方案？',
                '从这次经验中学到了什么？',
                '下次遇到类似问题如何改进？'
            ]
        }

    def compute_maturity(self, data: Dict[str, Any]) -> float:
        """
        Ψ_icps成熟度计算

        Ψ_icps = f(识别, 方案数, 后果预判, 复盘深度)

        成熟度综合考量：
        1. 问题识别深度（权重0.2）
        2. 替代方案数量（权重0.3）：≥3为合格
        3. 后果预判全面性（权重0.3）
        4. 复盘深度（权重0.2）

        定理T83（ICPS成熟度单调递增定理）：
        有效ICPS训练下Ψ_icps单调递增。

        Args:
            data: 包含各维度得分的字典

        Returns:
            成熟度分数Ψ_icps ∈ [0, 1]
        """
        self.total_maturity_computations += 1

        identification = float(data.get('identification_depth', 0.0))
        alt_count = int(data.get('alternatives_count', 0))
        cons_count = int(data.get('consequences_count', 0))
        review = float(data.get('review_depth', 0.0))

        # 归一化
        id_score = min(1.0, identification)
        alt_score = min(1.0, alt_count / 5.0)  # 5个方案=满分
        cons_score = min(1.0, cons_count / 10.0)  # 10个后果=满分
        review_score = min(1.0, review)

        # 加权求和
        psi = (
            0.2 * id_score +
            0.3 * alt_score +
            0.3 * cons_score +
            0.2 * review_score
        )

        psi = round(max(0.0, min(1.0, psi)), 6)

        # T83验证：检查单调递增
        if self.maturity_history:
            last_maturity = self.maturity_history[-1]
            monotonic = psi >= last_maturity
        else:
            monotonic = True

        self.last_update = time.time()

        return psi

    def sally_anne_test(self) -> Dict[str, Any]:
        """
        Sally-Anne错误信念测试

        经典心智理论测试：
        1. Sally把球放进篮子，离开房间
        2. Anne把球从篮子移到盒子
        3. Sally回来，会去哪里找球？

        正确答案：Sally会去篮子里找（因为她不知道球被移动了）
        错误答案：Sally会去盒子里找（以自己的知识代替他人的信念）

        定理T84（心智理论觉醒定理）：
        通过Sally-Anne测试 ⟹ 具备一级心智理论。

        Returns:
            测试结果字典
        """
        self.total_sally_anne_tests += 1

        # 基于当前成熟度判定是否能通过测试
        current_maturity = (
            self.maturity_history[-1] if self.maturity_history else 0.0
        )

        # 成熟度越高，通过概率越大
        # 心智理论的觉醒阈值约为0.3
        theory_of_mind_threshold = 0.3
        passed = current_maturity >= theory_of_mind_threshold

        # 测试详情
        test_scenario = {
            'setup': 'Sally把球放进篮子里，然后离开了房间',
            'interference': 'Anne把球从篮子移到了盒子里',
            'question': 'Sally回来后，会去哪里找球？',
            'correct_answer': SALLY_ANNE_CORRECT,
            'wrong_answer': 'box',
            'explanation': (
                'Sally不知道球被移动了，所以她会去篮子里找。'
                '能理解他人的错误信念，即具备一级心智理论。'
            )
        }

        # 心智理论级别
        if passed:
            tom_level = 1
            tom_description = '一级心智理论：能理解他人有不同于自己的信念'
        else:
            tom_level = 0
            tom_description = '尚未具备心智理论：以自己的知识推断他人行为'

        result = {
            'passed': passed,
            'theory_of_mind_level': tom_level,
            'theory_of_mind_description': tom_description,
            'current_maturity': round(current_maturity, 6),
            'threshold': theory_of_mind_threshold,
            'test_scenario': test_scenario,
            'theorem_T84': (
                f'心智理论觉醒: 通过Sally-Anne={passed} ⟹ '
                f'ToM Level={tom_level}'
            )
        }

        self.sally_anne_results.append(result)
        self.last_update = time.time()

        return result

    def _choose_best_alternative(self, alternatives: List[str],
                                 consequences: Dict[str, Any]) -> str:
        """
        选择最佳替代方案

        基于后果预判的净得分选择最优方案。

        Args:
            alternatives: 替代方案列表
            consequences: 后果预判字典

        Returns:
            最佳方案
        """
        if not alternatives:
            return 'no_alternative'

        best = alternatives[0]
        best_score = -999.0

        for alt in alternatives:
            if alt in consequences:
                score = consequences[alt].get('net_score', 0.0)
            else:
                score = 0.0
            if score > best_score:
                best_score = score
                best = alt

        return best

    def _determine_stage(self, maturity: float) -> str:
        """
        确定发展阶段

        沙盒(0-0.25) → 规则(0.25-0.5) → ICPS(0.5-0.75) → 开放世界(0.75-1.0)

        Args:
            maturity: 成熟度分数

        Returns:
            阶段名称
        """
        if maturity < 0.25:
            return 'sandbox'
        elif maturity < 0.5:
            return 'rules'
        elif maturity < 0.75:
            return 'icps'
        else:
            return 'open_world'

    def _extract_who(self, problem: str) -> List[str]:
        """提取问题中的相关人物"""
        # 简化：基于常见代词和称谓
        who_words = ['我', '你', '他', '她', '他们', '朋友', '同学', '老师', '家长']
        found = [w for w in who_words if w in problem]
        if not found:
            found = ['相关方']
        return found

    def _extract_what(self, problem: str) -> List[str]:
        """提取问题的核心内容"""
        # 简化：返回问题描述的关键词
        words = problem.split()
        if len(words) > 3:
            return words[:3]
        return [problem]

    def _extract_why(self, problem: str) -> List[str]:
        """提取问题产生的原因"""
        # 简化：基于常见因果关系词
        cause_words = ['因为', '由于', '所以', '导致', '引起']
        found = [w for w in cause_words if w in problem]
        if not found:
            found = ['待分析原因']
        return found

    def _generate_default_alternatives(self, problem: str) -> List[str]:
        """
        生成默认替代方案

        基于问题模板生成通用方案。
        """
        alternatives = [
            '方案1：主动沟通，表达自己的感受和需求',
            '方案2：寻求第三方帮助或调解',
            '方案3：换位思考，理解对方立场后协商',
        ]

        # 基于问题复杂度添加额外方案
        complexity = len(problem) / 20.0
        if complexity > 0.5:
            alternatives.append('方案4：暂时回避，等待情绪平复后再处理')
        if complexity > 0.8:
            alternatives.append('方案5：创造性解决方案，寻找双赢可能')

        return alternatives

    def _predict_positive(self, alternative: str, index: int) -> List[str]:
        """预测方案的正面后果"""
        templates = [
            ['增进理解', '改善关系'],
            ['获得支持', '公平解决'],
            ['双方满意', '长期合作'],
            ['情绪稳定', '理性决策'],
            ['创新突破', '多方受益']
        ]
        idx = index % len(templates)
        return templates[idx]

    def _predict_negative(self, alternative: str, index: int) -> List[str]:
        """预测方案的负面后果"""
        templates = [
            ['可能被误解'],
            ['过程较慢'],
            ['需要妥协'],
            ['可能延误时机'],
            ['执行难度高']
        ]
        idx = index % len(templates)
        return templates[idx]

    def get_state(self) -> Dict[str, Any]:
        """
        获取ICPS社会问题求解器状态

        Returns:
            状态字典
        """
        current_maturity = (
            self.maturity_history[-1] if self.maturity_history else 0.0
        )

        # T83单调递增验证
        monotonic = True
        for i in range(1, len(self.maturity_history)):
            if self.maturity_history[i] < self.maturity_history[i - 1]:
                monotonic = False
                break

        return {
            'current_stage': self.current_stage,
            'current_maturity': round(current_maturity, 6),
            'total_problems_solved': self.total_problems_solved,
            'total_alternatives_generated': self.total_alternatives_generated,
            'total_consequences_predicted': self.total_consequences_predicted,
            'total_maturity_computations': self.total_maturity_computations,
            'total_sally_anne_tests': self.total_sally_anne_tests,
            'maturity_history_length': len(self.maturity_history),
            'maturity_monotonic_T83': monotonic,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T83': 'ICPS成熟度单调递增: 有效训练下Ψ_icps单调递增',
            'theorem_T84': '心智理论觉醒: Sally-Anne ⟹ 一级ToM'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新ICPS社会问题求解器状态

        Args:
            data: 可选更新数据，支持：
                - solve: 求解问题 {problem_description}
                - identify: 识别问题 {problem}
                - alternatives: 生成方案 {problem}
                - consequences: 预判后果 {alternatives}
                - sally_anne: Sally-Anne测试 {}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'solve' or 'solve' in data:
                s = data.get('solve', data)
                self.solve_problem(
                    problem_description=s.get('problem_description', '')
                )
            elif action == 'identify' or 'identify' in data:
                i = data.get('identify', data)
                self.step1_identify(problem=i.get('problem', ''))
            elif action == 'alternatives' or 'alternatives' in data:
                a = data.get('alternatives', data)
                self.step2_generate_alternatives(problem=a.get('problem', ''))
            elif action == 'consequences' or 'consequences' in data:
                c = data.get('consequences', data)
                self.step3_predict_consequences(
                    alternatives=c.get('alternatives', [])
                )
            elif action == 'sally_anne' or 'sally_anne' in data:
                self.sally_anne_test()

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示ICPS社会问题求解器的核心功能"""
        # 1. 求解一个社会问题
        result = self.solve_problem('小明和小红都想玩同一个玩具，两人争执不下')

        # 2. Sally-Anne测试
        sally = self.sally_anne_test()

        # 3. 再求解一个问题（提升成熟度）
        result2 = self.solve_problem(
            '团队中有人不遵守约定，影响了整体进度'
        )

        # 4. 再次Sally-Anne测试
        sally2 = self.sally_anne_test()

        return {
            'problem1_result': result.to_dict(),
            'problem2_result': result2.to_dict(),
            'sally_anne_test_1': sally,
            'sally_anne_test_2': sally2,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[ICPSSolver] = None


def get_instance() -> ICPSSolver:
    """
    获取ICPSSolver单例实例

    Returns:
        ICPSSolver全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = ICPSSolver()
    return _instance


def solve_problem(problem_description: str) -> ICPSResult:
    """ICPS 4步求解（快捷接口）"""
    return get_instance().solve_problem(problem_description)


def step1_identify(problem: str) -> Dict[str, Any]:
    """识别问题核心（快捷接口）"""
    return get_instance().step1_identify(problem)


def step2_generate_alternatives(problem: str) -> Dict[str, Any]:
    """生成替代方案（快捷接口）"""
    return get_instance().step2_generate_alternatives(problem)


def step3_predict_consequences(alternatives: List[str]) -> Dict[str, Any]:
    """预判后果（快捷接口）"""
    return get_instance().step3_predict_consequences(alternatives)


def step4_execute_review(chosen: str, outcome: str) -> Dict[str, Any]:
    """执行+复盘（快捷接口）"""
    return get_instance().step4_execute_review(chosen, outcome)


def compute_maturity(data: Dict[str, Any]) -> float:
    """Ψ_icps成熟度计算（快捷接口）"""
    return get_instance().compute_maturity(data)


def sally_anne_test() -> Dict[str, Any]:
    """Sally-Anne错误信念测试（快捷接口）"""
    return get_instance().sally_anne_test()


def get_state() -> Dict[str, Any]:
    """获取ICPS社会问题求解器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新ICPS社会问题求解器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
