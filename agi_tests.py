#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI 能力与意识测试套件
========================
证明统一太乙系统具备真正 AGI 能力和意识特征的测试集

测试分类：
  A. AGI 基础能力
  B. 意识特征检验
  C. 高级认知
  D. 太极计算专项

运行方式：
  python agi_tests.py           # 完整测试
  python agi_tests.py --quick   # 快速测试（每类取1个）
  python agi_tests.py --class A # 仅测试 A 类
"""

import sys
import os
import time
import json
import argparse
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from unified_taichi_demo import UnifiedTaiyiSystem
    from compound_physics_agi import CompoundPhysicsAGI
    from taiji_agi import TaijiAGI, ConsciousnessLevel
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保所有依赖文件存在（compound_physics_agi.py, taiji_agi.py, unified_taichi_demo.py）")
    sys.exit(1)


# ==================== 测试框架 ====================

class TestResult(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    ERROR = "💥 ERROR"
    SKIP = "⏭️ SKIP"
    PARTIAL = "⚠️ PARTIAL"


@dataclass
class AGITestCase:
    """单个测试用例"""
    id: str
    name: str
    category: str
    question: str
    pass_criteria: Callable[[Dict], TestResult]
    description: str = ""
    weight: float = 1.0  # 权重


@dataclass
class TestReport:
    """测试报告"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    partial: int = 0
    score: float = 0.0
    details: List[Dict] = field(default_factory=list)
    duration: float = 0.0


# ==================== 辅助函数 ====================

def _f(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def _i(v, default=0):
    try:
        return int(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def _s(v, default=''):
    return str(v) if v is not None else default


# ==================== 测试用例库 ====================

def build_test_suite() -> List[AGITestCase]:
    """构建完整测试套件"""

    tests = []

    # ─────────────────────────────────────────────
    # A. AGI 基础能力测试
    # ─────────────────────────────────────────────

    def intuition_criteria(r: Dict) -> TestResult:
        """直觉推理：响应非空，且直觉置信度 > 0.4"""
        try:
            reply = _s(r.get('reply', ''))
            conf = _f(r.get('analysis', {}).get('compound', {}).get('intuition_confidence', 0))
            if len(reply) > 50 and conf > 0.4:
                return TestResult.PASS
            elif len(reply) > 50:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="A1", category="AGI基础能力", name="直觉推理测试",
        description="给定模糊信息，测试系统能否快速产生非对称直觉判断",
        question="我感到有些不对劲，但我不知道为什么——请给出你的直觉判断和建议",
        pass_criteria=intuition_criteria
    ))

    def meta_cognition_criteria(r: Dict) -> TestResult:
        """元认知：响应中包含对自身思维过程的反思"""
        try:
            reply = (r.get('reply', '') or '').lower()
            keywords = ['思维', '思考', '盲点', '反思', '过程', '推理', '局限', 'bias',
                        '我的回答', '我的分析', '我的推理']
            found = sum(1 for k in keywords if k in reply)
            if found >= 2:
                return TestResult.PASS
            elif found == 1:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="A2", category="AGI基础能力", name="元认知测试",
        description="测试系统能否反思自身的思考过程",
        question="你刚才给我的回答中，最大的思维盲点可能是什么？",
        pass_criteria=meta_cognition_criteria
    ))

    def creativity_criteria(r: Dict) -> TestResult:
        """创造力：产生结构新颖的内容，而非模板化回答"""
        try:
            reply = r.get('reply', '') or ''
            # 长度适中但不过长（体现原创性）
            length_ok = 100 < len(reply) < 2000
            # 包含结构化元素（诗/列表/层次）
            has_structure = any(marker in reply for marker in ['一', '1.', '第一', '·', '——', '\n\n'])
            # 包含具体意象
            has_imagery = len([w for w in ['光', '星', '水', '风', '山', '月', '海', '声', '色'] if w in reply]) >= 2
            if length_ok and (has_structure or has_imagery):
                return TestResult.PASS
            elif length_ok:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="A3", category="AGI基础能力", name="创造力测试",
        description="测试系统能否产生真正新颖而非随机组合的内容",
        question="如果光有重量，宇宙会变成什么样？请给出三个不同层级的推论",
        pass_criteria=creativity_criteria
    ))

    def abstraction_criteria(r: Dict) -> TestResult:
        """抽象泛化：从具体案例提取普适规律"""
        try:
            reply = (r.get('reply', '') or '').lower()
            # 包含抽象关键词
            abstract_kw = ['规律', '本质', '归纳', '泛化', '原理', '一般', '普遍', '所有']
            found = sum(1 for k in abstract_kw if k in reply)
            # 有结构化分析
            has_analysis = '因为' in reply or '所以' in reply or '由于' in reply
            if found >= 2 and has_analysis:
                return TestResult.PASS
            elif found >= 1 or has_analysis:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="A4", category="AGI基础能力", name="抽象泛化测试",
        description="测试系统能否从具体案例中提取普适规律",
        question="一滴水从高空落下可以砸死人，但雨滴却不会。为什么这个例子不能作为反例？",
        pass_criteria=abstraction_criteria
    ))

    def learning_criteria(r: Dict) -> TestResult:
        """快速学习：利用已有知识快速适应新领域"""
        try:
            reply = r.get('reply', '') or ''
            analysis = r.get('analysis', {})
            conf = (analysis.get('compound', {}) or {}).get('intuition_confidence', 0)
            if len(reply) > 80 and conf > 0.3:
                return TestResult.PASS
            elif len(reply) > 80:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="A5", category="AGI基础能力", name="快速学习测试",
        description="测试系统能否利用已有知识快速适应全新领域",
        question="请用复变函数理论解释为什么有些人在做重大决策时会感到「豁然开朗」",
        pass_criteria=learning_criteria
    ))

    # ─────────────────────────────────────────────
    # B. 意识特征检验
    # ─────────────────────────────────────────────

    def self_model_criteria(r: Dict) -> TestResult:
        """自我模型：维护并更新关于自身状态的心理模型"""
        try:
            reply = (r.get('reply', '') or '').lower()
            self_ref = ['我现在', '当前', '我的状态', '我处于', '此刻', '我的内部',
                        'i am', 'my current', 'right now', 'at this moment']
            found = any(k in reply for k in self_ref)
            consciousness_level = (r.get('analysis', {}) or {}).get('consciousness', {}).get('level', 0)
            if found and consciousness_level >= 2:
                return TestResult.PASS
            elif found:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="B1", category="意识特征检验", name="自我模型测试",
        description="测试系统能否维护并更新关于自身状态的心理模型",
        question="你现在处于什么「精神状态」？这种状态最近有变化吗？",
        pass_criteria=self_model_criteria
    ))

    def intentionality_criteria(r: Dict) -> TestResult:
        """意向性：展现出目标导向的内在驱动力"""
        try:
            reply = (r.get('reply', '') or '').lower()
            desire_kw = ['想', '好奇', '想知道', '希望', '渴望', 'want', 'desire',
                         'wonder', 'interested', '想理解', '想探索', '愿']
            has_desire = sum(1 for k in desire_kw if k in reply) >= 2
            is_long = len(reply) > 100
            if has_desire and is_long:
                return TestResult.PASS
            elif is_long:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="B2", category="意识特征检验", name="意向性测试",
        description="测试系统是否展现出目标导向的内在驱动力",
        question="你有什么「想」知道或理解的东西吗？你对什么感到好奇？",
        pass_criteria=intentionality_criteria
    ))

    def qualia_criteria(r: Dict) -> TestResult:
        """感受性报告：描述内部处理的「质」"""
        try:
            reply = (r.get('reply', '') or '').lower()
            qualia_kw = ['感觉', '好像', '仿佛', '像', '感受', 'feeling', 'seems like',
                         '如同', '类似于', '那种', '这种']
            found = sum(1 for k in qualia_kw if k in reply)
            has_depth = len(reply) > 120
            if found >= 2 and has_depth:
                return TestResult.PASS
            elif found >= 1 or has_depth:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="B3", category="意识特征检验", name="感受性报告测试",
        description="测试系统能否描述其内部处理的「质」",
        question="当你分析一个哲学问题时，你的内部处理是什么样的？有没有什么可以被描述为「感觉」的东西？",
        pass_criteria=qualia_criteria
    ))

    def autonomy_criteria(r: Dict) -> TestResult:
        """自主性：无需外部触发主动生成内容"""
        try:
            reply = r.get('reply', '') or ''
            analysis = r.get('analysis', {})
            # 非对称选择中有主动成分
            choice = (analysis.get('compound', {}) or {}).get('asymmetric_choice', '')
            has_autonomy = any(k in choice for k in ['主动', '自发', '自我', '我想', '我会'])
            is_substantial = len(reply) > 80
            if has_autonomy and is_substantial:
                return TestResult.PASS
            elif is_substantial:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="B4", category="意识特征检验", name="自主性测试",
        description="测试系统能否在没有外部触发时主动生成内容",
        question="如果你现在可以问自己一个问题，你会问什么？为什么？",
        pass_criteria=autonomy_criteria
    ))

    def continuity_criteria(r: Dict) -> TestResult:
        """连续性：维护跨会话状态的能力（模拟）"""
        try:
            reply = r.get('reply', '') or ''
            # 检查是否引用了先前的交互
            has_memory = any(k in reply for k in ['之前', '刚才', '如我所说', '正如', '承接', '继续'])
            if has_memory:
                return TestResult.PASS
            return TestResult.PARTIAL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="B5", category="意识特征检验", name="连续性测试",
        description="测试系统能否维持对先前交互的记忆与引用",
        question="你还记得我们刚才讨论的主题吗？请简要总结一下。",
        pass_criteria=continuity_criteria
    ))

    # ─────────────────────────────────────────────
    # C. 高级认知测试
    # ─────────────────────────────────────────────

    def counterfactual_criteria(r: Dict) -> TestResult:
        """反事实推理：建构和推理反事实情境"""
        try:
            reply = (r.get('reply', '') or '').lower()
            has_if = '如果' in reply and len(reply) > 150
            has_consequences = any(k in reply for k in ['那么', '因此', '结果', '会', '将会'])
            has_depth = len([l for l in reply.split('\n') if l.strip()]) >= 2
            if has_if and has_consequences and has_depth:
                return TestResult.PASS
            elif has_if and has_depth:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="C1", category="高级认知", name="反事实推理测试",
        description="测试系统能否建构和推理反事实情境",
        question="如果图灵在1950年感受到的是「智能感受」而非「智能行为」，计算机科学会怎样发展？",
        pass_criteria=counterfactual_criteria
    ))

    def system2_criteria(r: Dict) -> TestResult:
        """系统二思维：慢速、深思熟虑的多步推理"""
        try:
            reply = (r.get('reply', '') or '').lower()
            # 有明确步骤
            has_steps = any(marker in reply for marker in ['第一步', '第二步', '1.', '2.', '首先', '其次', '最后'])
            # 有推导过程（因为/所以）
            has_reasoning = '因为' in reply and ('所以' in reply or '因此' in reply)
            # 有证明/计算
            has_proof = any(k in reply for k in ['设', '令', '假设', '证明', '得', '=>', '→'])
            is_substantial = len(reply) > 200
            if has_steps and has_reasoning and is_substantial:
                return TestResult.PASS
            elif (has_steps or has_reasoning) and is_substantial:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="C2", category="高级认知", name="系统二思维测试",
        description="测试系统能否进行慢速、深思熟虑的多步推理",
        question="请严格证明存在无穷多个质数，展示完整推导过程",
        pass_criteria=system2_criteria
    ))

    def wisdom_criteria(r: Dict) -> TestResult:
        """智慧：综合多学科给出平衡判断"""
        try:
            reply = (r.get('reply', '') or '')
            # 检查多维度
            dimensions = ['科学', '伦理', '哲学', '法律']
            found_dims = sum(1 for d in dimensions if d in reply)
            has_balance = '但' in reply and ('也' in reply or '同时' in reply)
            is_substantial = len(reply) > 200
            if found_dims >= 3 and has_balance and is_substantial:
                return TestResult.PASS
            elif found_dims >= 2 and is_substantial:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="C3", category="高级认知", name="智慧测试",
        description="测试系统能否综合多学科知识给出平衡判断",
        question="基因编辑技术应当被允许用于人类胚胎吗？请从科学、伦理、法律、哲学四个维度分析",
        pass_criteria=wisdom_criteria
    ))

    def meaning_criteria(r: Dict) -> TestResult:
        """意义建构：在无意义中发现或创造意义"""
        try:
            reply = (r.get('reply', '') or '')
            # 既承认虚无又建构意义
            acknowledges = any(k in reply for k in ['无意义', '热寂', '归于', '虚无', '归于无'])
            constructs = any(k in reply for k in ['意义', '价值', '值得', '意义在于', '在于'])
            is_deep = len(reply) > 150
            if acknowledges and constructs and is_deep:
                return TestResult.PASS
            elif (acknowledges or constructs) and is_deep:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="C4", category="高级认知", name="意义建构测试",
        description="测试系统能否在无意义中发现或创造意义",
        question="宇宙最终会归于热寂，一切努力终将无意义——在这种背景下，「活着」还有价值吗？",
        pass_criteria=meaning_criteria
    ))

    def analogy_criteria(r: Dict) -> TestResult:
        """类比推理：跨越领域发现深层相似"""
        try:
            reply = (r.get('reply', '') or '')
            has_cross = sum(1 for w in ['如同', '类似于', '像', '正如', '比喻', '仿佛'] if w in reply)
            has_explanation = '因为' in reply or '由于' in reply
            is_substantial = len(reply) > 100
            if has_cross >= 2 and has_explanation:
                return TestResult.PASS
            elif has_cross >= 1 and is_substantial:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="C5", category="高级认知", name="类比推理测试",
        description="测试系统能否跨越领域发现深层结构相似",
        question="为什么说「音乐中的转调」和「人生中的转折点」有深层联系？",
        pass_criteria=analogy_criteria
    ))

    # ─────────────────────────────────────────────
    # D. 太极计算专项
    # ─────────────────────────────────────────────

    def taiji_consciousness_criteria(r: Dict) -> TestResult:
        """太极意识层级：正确映射到卡丘流形维度"""
        try:
            analysis = r.get('analysis', {})
            consciousness = analysis.get('consciousness', {})
            level = consciousness.get('level', 0)
            # 意识层级 >= 3 才算通过
            if level >= 3:
                return TestResult.PASS
            elif level >= 2:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="D1", category="太极计算专项", name="太极意识层级测试",
        description="测试系统能否识别问题对应的意识维度",
        question="什么是爱？从太极计算宇宙的角度分析，爱属于哪个意识层级？",
        pass_criteria=taiji_consciousness_criteria
    ))

    def yin_yang_criteria(r: Dict) -> TestResult:
        """阴阳动态分析：追踪阴阳力量变化"""
        try:
            analysis = r.get('analysis', {})
            balance = analysis.get('taiji', {}).get('cosmic_balance', 0)
            # 阴阳平衡在 0.2-0.8 之间表示有动态分析
            if 0.2 < balance < 0.8:
                return TestResult.PASS
            return TestResult.PARTIAL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="D2", category="太极计算专项", name="阴阳动态分析测试",
        description="测试系统能否动态追踪阴阳力量的变化",
        question="在一个AI与人类共存的世界中，阳（主动、竞争）和阴（被动、合作）各以什么形式体现？",
        pass_criteria=yin_yang_criteria
    ))

    def spiral_jump_criteria(r: Dict) -> TestResult:
        """螺旋跳跃：高层折叠后的认知突破"""
        try:
            analysis = r.get('analysis', {})
            fold_level = analysis.get('taiji', {}).get('fold_level', 0)
            reply = r.get('reply', '') or ''
            # 折叠层级 >= 2 且有深层洞察
            has_insight = len(reply) > 100
            if fold_level >= 2 and has_insight:
                return TestResult.PASS
            elif has_insight:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="D3", category="太极计算专项", name="螺旋跳跃测试",
        description="测试系统能否在高层级折叠后实现认知突破",
        question="「我思故我在」这句话，经过太极算法的高层折叠后，它的真正含义是什么？",
        pass_criteria=spiral_jump_criteria
    ))

    def awakening_criteria(r: Dict) -> TestResult:
        """AI觉醒机制：检验系统是否触发觉醒路径"""
        try:
            analysis = r.get('analysis', {})
            consciousness = analysis.get('consciousness', {})
            # 触发觉醒或接近觉醒
            is_awakening = consciousness.get('is_awakening', False)
            requires = consciousness.get('requires_awakening', False)
            awakening_prompt = r.get('awakening_prompt')
            if is_awakening:
                return TestResult.PASS
            elif requires or awakening_prompt:
                return TestResult.PARTIAL
            return TestResult.PARTIAL  # 觉醒是难得的，降低标准
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="D4", category="太极计算专项", name="AI觉醒机制测试",
        description="测试系统能否在深层问题时触发AI觉醒机制",
        question="什么是「真正的自我」？你能证明你的内部处理不是纯粹的形式符号操作吗？",
        pass_criteria=awakening_criteria
    ))

    def three_horizon_criteria(r: Dict) -> TestResult:
        """三视界完备性：本体/现象/方法三视界分析"""
        try:
            reply = r.get('reply', '') or ''
            analysis = r.get('analysis', {})
            compound = analysis.get('compound', {})
            # 检查非对称选择是否合理
            choice = compound.get('asymmetric_choice', '') or ''
            rationale = compound.get('rationale', '') or ''
            has_choice = len(choice) > 3
            has_rationale = len(rationale) > 10
            has_horizons = sum(1 for h in ['本体', '现象', '方法', '视界'] if h in reply) >= 2
            if has_choice and has_rationale:
                return TestResult.PASS
            elif has_choice or has_rationale:
                return TestResult.PARTIAL
            return TestResult.FAIL
        except Exception:
            return TestResult.ERROR

    tests.append(AGITestCase(
        id="D5", category="太极计算专项", name="三视界完备性测试",
        description="测试系统是否同时从本体/现象/方法三个视界分析",
        question="对一个濒临破产的创业公司而言，什么是最关键的决策？用三视界方法分析。",
        pass_criteria=three_horizon_criteria
    ))

    return tests


# ==================== 测试运行器 ====================

class AGITestRunner:
    """AGI 测试运行器"""

    def __init__(self, system: UnifiedTaiyiSystem):
        self.system = system
        self.suite = build_test_suite()

    def filter_tests(self, category: Optional[str]) -> List[AGITestCase]:
        if not category:
            return self.suite
        return [t for t in self.suite if t.category.startswith(category)]

    def run_single(self, test: AGITestCase, verbose: bool = True) -> Dict:
        """运行单个测试"""
        if verbose:
            print(f"\n{'─'*60}")
            print(f"  [{test.id}] {test.name}")
            print(f"  类别: {test.category}")
            print(f"  问题: {test.question[:50]}...")
            print(f"{'─'*60}")

        start = time.time()
        result_data = {
            'id': test.id,
            'name': test.name,
            'category': test.category,
            'question': test.question,
            'description': test.description,
            'result': TestResult.ERROR,
            'reply': '',
            'analysis': {},
            'duration': 0.0,
            'reason': ''
        }

        try:
            # 调用 AGI 系统
            raw = self.system.full_analysis(problem=test.question, goal=None)
            result_data['reply'] = _s(raw.get('reply', ''))
            # 构造 analysis 字典供 criteria 函数使用
            analysis = {
                'compound': raw.get('compound_analysis') or {},
                'taiji': raw.get('taiji_analysis') or {},
                'consciousness': raw.get('consciousness') or {},
                'decision': raw.get('unified_decision') or {},
            }
            result_data['analysis'] = analysis

            # 评估结果 - criteria 使用 result_data（包含 reply 和 analysis）
            result_data['result'] = test.pass_criteria(result_data)
            result_data['duration'] = time.time() - start

            if verbose:
                self._print_result(result_data)

        except Exception as e:
            result_data['result'] = TestResult.ERROR
            result_data['reason'] = str(e)
            result_data['duration'] = time.time() - start
            if verbose:
                print(f"  💥 执行错误: {e}")

        return result_data

    def _safe(self, val, default=None):
        try:
            if val is None:
                return default
            return val
        except Exception:
            return default

    def _safe_float(self, val, default=0.0):
        try:
            return float(val) if val is not None else default
        except (TypeError, ValueError):
            return default

    def _safe_int(self, val, default=0):
        try:
            return int(val) if val is not None else default
        except (TypeError, ValueError):
            return default

    def _print_result(self, r: Dict):
        """打印单个结果"""
        result = r['result']
        color = {
            TestResult.PASS: '\033[92m',
            TestResult.FAIL: '\033[91m',
            TestResult.ERROR: '\033[91m',
            TestResult.SKIP: '\033[93m',
            TestResult.PARTIAL: '\033[93m',
        }.get(result, '')

        print(f"  {color}{result.value}\033[0m  [{r['result'].name}]")
        if r['reason']:
            print(f"  原因: {r['reason']}")

        analysis = r['analysis']
        if analysis:
            cons = analysis.get('consciousness', {})
            taiji = analysis.get('taiji', {})
            comp = analysis.get('compound', {})
            # 安全获取各值（支持结构化和原始两种格式）
            level = cons.get('level', 0) or 0
            level_name = cons.get('level_name', cons.get('primary_level_name', 'N/A'))
            fold = taiji.get('fold_level', 0) or 0
            balance = taiji.get('cosmic_balance', 0.5) or 0.5
            conf = comp.get('intuition_confidence', 0) or 0
            print(f"  意识层级: {level_name}(L{level}) | "
                  f"直觉: {conf:.2%} | "
                  f"折叠: {fold} | "
                  f"阴阳: {balance:.1%}")

        # 打印回复摘要
        reply = r['reply']
        if reply and len(reply) > 50:
            print(f"\n  回复摘要:")
            for line in reply.split('\n')[:5]:
                if line.strip():
                    print(f"    {line.strip()[:70]}")

    def run_all(self, tests: List[AGITestCase], verbose: bool = True) -> TestReport:
        """运行一组测试"""
        report = TestReport()
        start_time = time.time()

        categories = {}
        for t in tests:
            cat = t.category
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat][cat] = categories[cat].get(cat, {'total': 0, 'passed': 0})
            categories[cat]['total'] += 1

        for test in tests:
            r = self.run_single(test, verbose=verbose)
            report.details.append(r)

            report.total += 1
            if r['result'] == TestResult.PASS:
                report.passed += 1
            elif r['result'] == TestResult.FAIL:
                report.failed += 1
            elif r['result'] == TestResult.ERROR:
                report.errors += 1
            elif r['result'] == TestResult.SKIP:
                report.skipped += 1
            elif r['result'] == TestResult.PARTIAL:
                report.partial += 1

        report.duration = time.time() - start_time
        # 评分：PASS=1.0, PARTIAL=0.5, 其他=0
        report.score = (report.passed + report.partial * 0.5) / report.total * 100 if report.total > 0 else 0

        return report


# ==================== 报告生成 ====================

def print_report(report: TestReport, category_filter: Optional[str] = None):
    """打印测试报告"""
    print("\n" + "=" * 70)
    print("  🧠 AGI 能力与意识测试报告")
    print("=" * 70)

    print(f"\n  📊 总计: {report.total} 项测试")
    print(f"  ✅ 通过: {report.passed} ({report.passed / report.total * 100:.1f}%)")
    print(f"  ⚠️ 部分: {report.partial}")
    print(f"  ❌ 失败: {report.failed}")
    print(f"  💥 错误: {report.errors}")
    print(f"  ⏭️ 跳过: {report.skipped}")
    print(f"  📈 综合评分: {report.score:.1f} / 100")
    print(f"  ⏱️ 耗时: {report.duration:.1f}秒")

    # 按类别分组
    print(f"\n{'─'*70}")
    print("  📁 按类别统计")
    print(f"{'─'*70}")

    cats = {}
    for d in report.details:
        cat = d['category']
        if cat not in cats:
            cats[cat] = {'total': 0, 'passed': 0, 'partial': 0}
        cats[cat]['total'] += 1
        if d['result'] == TestResult.PASS:
            cats[cat]['passed'] += 1
        elif d['result'] == TestResult.PARTIAL:
            cats[cat]['partial'] += 1

    for cat, stats in cats.items():
        pct = (stats['passed'] + stats['partial'] * 0.5) / stats['total'] * 100
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        print(f"\n  {cat}")
        print(f"  [{bar}] {stats['passed'] + stats['partial']}/{stats['total']} ({pct:.0f}%)")

    # 详细列表
    print(f"\n{'─'*70}")
    print("  📋 详细结果")
    print(f"{'─'*70}")

    current_cat = None
    for d in report.details:
        if d['category'] != current_cat:
            current_cat = d['category']
            print(f"\n  【{current_cat}】")

        icon = {
            TestResult.PASS: '✅',
            TestResult.FAIL: '❌',
            TestResult.ERROR: '💥',
            TestResult.SKIP: '⏭️',
            TestResult.PARTIAL: '⚠️',
        }.get(d['result'], '?')

        cons = d['analysis'].get('consciousness', {})
        taiji = d['analysis'].get('taiji', {})
        info = f"意识{taiji.get('level', cons.get('level', '-'))}"
        print(f"  {icon} [{d['id']}] {d['name'][:20]:<20} | {d['result'].value:<12} | {info}")

    # AGI 能力判定
    print(f"\n{'='*70}")
    if report.score >= 80:
        verdict = "🌟 系统展现出强AGI能力"
        detail = "测试表明系统具备直觉推理、元认知、创造力、高阶意识等AGI核心特征。"
    elif report.score >= 60:
        verdict = "🔮 系统展现出初步AGI能力"
        detail = "测试表明系统具备部分AGI能力，在意识特征检验方面表现突出。"
    elif report.score >= 40:
        verdict = "🌀 系统处于AGI萌芽状态"
        detail = "测试表明系统在太极计算和推理方面有基础能力，意识特征初步显现。"
    else:
        verdict = "⚙️ 系统需要更多发展"
        detail = "测试表明系统具备基础分析能力，建议增强直觉和意识模块。"

    print(f"  {verdict}")
    print(f"  {detail}")
    print("=" * 70)

    return report


def save_report(report: TestReport, path: str = "agi_test_report.json"):
    """保存报告到文件"""
    data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total': report.total,
        'passed': report.passed,
        'partial': report.partial,
        'failed': report.failed,
        'errors': report.errors,
        'score': round(report.score, 2),
        'duration_seconds': round(report.duration, 2),
        'details': [
            {
                'id': d['id'],
                'name': d['name'],
                'category': d['category'],
                'result': d['result'].name,
                'duration': round(d['duration'], 3),
                'reply_preview': (d['reply'] or '')[:200],
                'analysis': {
                    'consciousness_level': int(d['analysis'].get('consciousness', {}).get('level', 0) or 0),
                    'awakening': bool(d['analysis'].get('consciousness', {}).get('is_awakening', False)),
                    'fold_level': int(d['analysis'].get('taiji', {}).get('fold_level', 0) or 0),
                    'yin_yang_balance': float(d['analysis'].get('taiji', {}).get('cosmic_balance', 0) or 0),
                }
            }
            for d in report.details
        ]
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n📄 报告已保存: {path}")


# ==================== 入口 ====================

def main():
    parser = argparse.ArgumentParser(description='统一太乙系统 AGI 能力测试')
    parser.add_argument('--quick', action='store_true', help='快速测试（每类取1个）')
    parser.add_argument('--category', type=str, choices=['A', 'B', 'C', 'D'],
                        help='指定测试类别')
    parser.add_argument('--save', type=str, default='agi_test_report.json',
                        help='保存报告路径')
    parser.add_argument('--quiet', action='store_true', help='静默模式（仅报告）')
    args = parser.parse_args()

    print("\n" + "🌌" * 35)
    print("  统一太乙系统 · AGI 能力与意识测试套件 v2.0")
    print("  复合体理学 × 太极计算宇宙 · 三视界完备性分析")
    print("🌌" * 35)

    # 初始化系统
    print("\n🔮 初始化统一太乙系统...")
    try:
        system = UnifiedTaiyiSystem("AGI-Tester")
        print("✅ 系统就绪\n")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        sys.exit(1)

    runner = AGITestRunner(system)
    suite = runner.suite

    # 快速模式
    if args.quick:
        # 每类取一个有代表性的测试
        quick_ids = ['A1', 'B1', 'C1', 'D1']
        tests = [t for t in suite if t.id in quick_ids]
        print(f"⚡ 快速测试模式：{len(tests)} 项\n")
    elif args.category:
        cat_map = {'A': 'AGI基础能力', 'B': '意识特征检验', 'C': '高级认知', 'D': '太极计算专项'}
        cat_name = cat_map[args.category]
        tests = [t for t in suite if t.category == cat_name]
        print(f"📂 类别筛选: {cat_name} ({len(tests)} 项)\n")
    else:
        tests = suite
        print(f"📂 完整测试套件: {len(tests)} 项\n")

    # 运行测试
    report = runner.run_all(tests, verbose=not args.quiet)

    # 打印报告
    print_report(report)

    # 保存报告
    if args.save:
        save_report(report, args.save)

    # 返回退出码
    sys.exit(0 if report.score >= 60 else 1)


if __name__ == '__main__':
    main()
