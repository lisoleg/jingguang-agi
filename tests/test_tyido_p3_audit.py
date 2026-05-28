# -*- coding: utf-8 -*-
"""
TY/IDO Property 3 综合审计测试
================================
验证 M67/M68/M69/M70 四个模块的长程推理能力完整实现：
1. 子目标分解 (SubGoalDecomposer)
2. 每步验证 (StepVerifier)
3. 错误恢复/Plan B (PlanBFallback)
4. 资源预算/降级 (ResourceBudget)

审计标准：每个模块至少包含以下检查项：
✅ P3基础设施已初始化（_p3_decomposer, _p3_verifier, _p3_fallback, _p3_budget）
✅ 注册了至少2个fallback plan（Plan B + Plan C）
✅ get_state()包含tyido_p3诊断段
✅ 正常执行时返回PASS verdict
✅ 预算耗尽时触发DEGRADED verdict（优雅降级）
✅ 核心方法执行后P3诊断数据完整
"""

import sys
import os
import time
import traceback

# 确保路径正确
_base = os.path.dirname(os.path.abspath(__file__))
if _base not in sys.path:
    sys.path.insert(0, _base)

# 导入共享基础设施
from TYIDO_LongRangeReasoning import (
    SubGoalDecomposer, StepVerifier, PlanBFallback, ResourceBudget
)

# 导入审计模块
from modules.M67_EnlightenmentConvergenceVerifier import SpiritualEvolutionVerifier
from modules.M68_RelationalCouplingSemantizer import RelationalCouplingSemantizer
from modules.M69_AttractorStabilityAnalyzer import AttractorStabilityAnalyzer
from modules.M70_FalsifiablePredictionVerifier import FalsifiablePredictionVerifier


class AuditResult:
    """审计结果容器"""
    def __init__(self, module_name):
        self.module_name = module_name
        self.checks = []  # (check_name, passed: bool, detail: str)

    def add(self, name, passed, detail=""):
        self.checks.append((name, passed, detail))
        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {detail}")

    @property
    def all_passed(self):
        return all(c[1] for c in self.checks)

    @property
    def pass_count(self):
        return sum(1 for c in self.checks if c[1])

    @property
    def total_count(self):
        return len(self.checks)

    def summary(self):
        passed = self.pass_count
        total = self.total_count
        verdict = "PASS" if self.all_passed else "FAIL"
        return f"[{verdict}] {self.module_name}: {passed}/{total}"


def check_p3_infrastructure(instance, ar):
    """检查1: P3四个核心组件已初始化"""
    has_decomposer = hasattr(instance, '_p3_decomposer') and instance._p3_decomposer is not None
    has_verifier = hasattr(instance, '_p3_verifier') and instance._p3_verifier is not None
    has_fallback = hasattr(instance, '_p3_fallback') and instance._p3_fallback is not None
    has_budget = hasattr(instance, '_p3_budget') and instance._p3_budget is not None
    ar.add("P3基础设施初始化", all([has_decomposer, has_verifier, has_fallback, has_budget]),
           f"decomposer={has_decomposer}, verifier={has_verifier}, fallback={has_fallback}, budget={has_budget}")


def check_fallback_plans(instance, ar):
    """检查2: 注册了至少2个fallback plan"""
    if hasattr(instance, '_p3_fallback') and instance._p3_fallback:
        plans = instance._p3_fallback.get_state()
        plan_count = len(plans.get('registered_plans', []))
        ar.add("Fallback注册数≥2", plan_count >= 2,
               f"已注册 {plan_count} 个降级计划")
    else:
        ar.add("Fallback注册数≥2", False, "无fallback组件")


def check_get_state_p3(instance, ar):
    """检查3: get_state()包含tyido_p3段"""
    try:
        state = instance.get_state()
        has_p3 = 'tyido_p3' in state
        if has_p3:
            p3 = state['tyido_p3']
            has_verdict = 'verdict' in p3
            ar.add("get_state含tyido_p3", has_verdict,
                   f"verdict={p3.get('verdict')}, keys={list(p3.keys())}")
        else:
            ar.add("get_state含tyido_p3", False, "state中无tyido_p3段")
    except Exception as e:
        ar.add("get_state含tyido_p3", False, f"异常: {e}")


def check_normal_execution_passes(module_name, instance, ar, exercise_func):
    """检查4: 正常执行返回PASS verdict"""
    try:
        result = exercise_func(instance)
        # 结果可能来自exercise直接返回，也可能从get_state获取
        if isinstance(result, dict) and 'tyido_p3' in result:
            verdict = result['tyido_p3'].get('verdict', 'UNKNOWN')
        else:
            state = instance.get_state()
            p3 = state.get('tyido_p3', {})
            verdict = p3.get('verdict', 'UNKNOWN')

        is_pass = verdict in ('PASS', None)  # None表示预算未耗尽=正常
        ar.add("正常执行verdict", is_pass, f"verdict={verdict}")
    except Exception as e:
        ar.add("正常执行verdict", False, f"异常: {e}")


def check_p3_diagnostics_complete(module_name, instance, ar, exercise_func):
    """检查5: 执行后P3诊断数据完整（4个核心段）"""
    try:
        exercise_func(instance)
        state = instance.get_state()
        p3 = state.get('tyido_p3', {})
        required_keys = ['subgoal_progress', 'verifier_state', 'fallback_state', 'budget_state']
        present = [k for k in required_keys if k in p3]
        missing = [k for k in required_keys if k not in p3]
        ar.add("P3诊断完整(4段)", len(missing) == 0,
               f"present={present}, missing={missing}")
    except Exception as e:
        ar.add("P3诊断完整(4段)", False, f"异常: {e}")


def check_graceful_degradation(module_key, instance, ar, exercise_func_with_tiny_budget):
    """检查6: 极小预算下触发DEGRADED"""
    try:
        # 用极小预算创建新实例
        from modules.M67_EnlightenmentConvergenceVerifier import SpiritualEvolutionVerifier as M67
        from modules.M68_RelationalCouplingSemantizer import RelationalCouplingSemantizer as M68
        from modules.M69_AttractorStabilityAnalyzer import AttractorStabilityAnalyzer as M69
        from modules.M70_FalsifiablePredictionVerifier import FalsifiablePredictionVerifier as M70

        module_map = {
            'M67_顿悟收敛验证器': M67, 'M68_关系耦合语义器': M68,
            'M69_吸引子稳定性分析器': M69, 'M70_可证伪预言验证器': M70
        }
        Cls = module_map[module_key]

        # 创建极小预算实例
        tiny = Cls()
        # 手动替换预算为极小值 — max_steps=0 使 exhausted() 在 start 后立即返回 True
        tiny._p3_budget = ResourceBudget(max_time=0.0, max_steps=0)

        result = exercise_func_with_tiny_budget(tiny)
        # 判断是否有DEGRADED verdict
        if isinstance(result, dict) and 'tyido_p3' in result:
            verdict = result['tyido_p3'].get('verdict', '')
        else:
            state = tiny.get_state()
            p3 = state.get('tyido_p3', {})
            verdict = p3.get('verdict', '')

        is_degraded = verdict in ('DEGRADED', 'TIMEOUT', 'FAIL')
        ar.add("预算耗尽降级", is_degraded, f"verdict={verdict}")
    except Exception as e:
        ar.add("预算耗尽降级", False, f"异常: {e}")


# ============================================================
# 各模块的 exercise 函数
# ============================================================

def exercise_m67_normal(inst):
    """M67 正常执行"""
    import numpy as np
    for t in range(5):
        Lambda = 1.0 * np.exp(-0.3 * t) + 0.1
        Sc = 0.8 * np.exp(-0.2 * t) + 0.2
        Z = 0.9 * np.exp(-0.4 * t) + 0.1
        F = 0.3 + 0.6 * (1 - np.exp(-0.3 * t))
        result = inst.update(Lambda, Sc, Z, F)
    return result


def exercise_m67_tiny(inst):
    """M67 极小预算执行（单次调用即触发降级）"""
    return inst.update(Lambda=0.5, Sc=0.3, Z=0.4, F=0.5)


def exercise_m68_normal(inst):
    """M68 正常执行"""
    inst.compute_phase_coupling("意识", "流贯")
    inst.compute_phase_coupling("空性", "实相")
    return inst.compute_semantic_strength(["意识", "流贯", "同一性", "关系", "实在"])


def exercise_m68_tiny(inst):
    """M68 极小预算执行（单次调用即触发降级）"""
    return inst.compute_phase_coupling("意识", "流贯")


def exercise_m69_normal(inst):
    """M69 正常执行"""
    import numpy as np
    np.random.seed(42)
    for t in range(15):
        state = np.random.rand(3).tolist()
        inst.add_state(state)
    return inst.get_state()


def exercise_m69_tiny(inst):
    """M69 极小预算执行（单次调用即触发降级）"""
    return inst.add_state([0.5, 0.3, 0.7])


def exercise_m70_normal(inst):
    """M70 正常执行"""
    import numpy as np
    Lambda_vals = [float(np.exp(-0.1*t)) for t in range(10)]
    subj_scores = [float(0.5 + 0.2*t) for t in range(10)]
    inst.record_p7(Lambda_vals, subj_scores)
    B_vals = [float(0.1 + 0.08*t) for t in range(10)]
    inst.record_p8(B_vals, Lambda_trend=-0.2, Z_trend=-0.15, F_trend=0.1)
    return inst.verify_all()


def exercise_m70_tiny(inst):
    """M70 极小预算执行（单次调用即触发降级）"""
    import numpy as np
    Lambda_vals = [float(np.random.rand()) for _ in range(5)]
    subj_scores = [float(np.random.rand()) for _ in range(5)]
    return inst.record_p7(Lambda_vals, subj_scores)


# ============================================================
# 主审计流程
# ============================================================

def audit_module(module_name, cls, exercise_normal, exercise_tiny):
    """审计单个模块"""
    print(f"\n{'='*60}")
    print(f"审计 {module_name}")
    print(f"{'='*60}")

    ar = AuditResult(module_name)

    # 创建实例
    instance = cls()

    # 检查1: P3基础设施
    check_p3_infrastructure(instance, ar)

    # 检查2: Fallback注册
    check_fallback_plans(instance, ar)

    # 检查3: get_state含tyido_p3
    check_get_state_p3(instance, ar)

    # 检查4: 正常执行
    check_normal_execution_passes(module_name, instance, ar, exercise_normal)

    # 检查5: P3诊断完整
    instance2 = cls()
    check_p3_diagnostics_complete(module_name, instance2, ar, exercise_normal)

    # 检查6: 优雅降级
    check_graceful_degradation(module_name, instance, ar, exercise_tiny)

    print(f"\n--- {ar.summary()} ---")
    return ar


def main():
    print("=" * 60)
    print("TY/IDO Property 3 综合审计测试")
    print("=" * 60)
    print(f"审计目标: M67/M68/M69/M70 共4个模块")
    print(f"审计维度: 6项检查 × 4模块 = 24项")
    print()

    results = []

    # M67
    results.append(audit_module(
        "M67_顿悟收敛验证器",
        SpiritualEvolutionVerifier,
        exercise_m67_normal,
        exercise_m67_tiny
    ))

    # M68
    results.append(audit_module(
        "M68_关系耦合语义器",
        RelationalCouplingSemantizer,
        exercise_m68_normal,
        exercise_m68_tiny
    ))

    # M69
    results.append(audit_module(
        "M69_吸引子稳定性分析器",
        AttractorStabilityAnalyzer,
        exercise_m69_normal,
        exercise_m69_tiny
    ))

    # M70
    results.append(audit_module(
        "M70_可证伪预言验证器",
        FalsifiablePredictionVerifier,
        exercise_m70_normal,
        exercise_m70_tiny
    ))

    # ============================================================
    # 汇总
    # ============================================================
    print(f"\n{'='*60}")
    print("审计汇总")
    print(f"{'='*60}")

    total_checks = 0
    total_pass = 0
    all_pass = True
    for r in results:
        print(f"  {r.summary()}")
        total_checks += r.total_count
        total_pass += r.pass_count
        if not r.all_passed:
            all_pass = False

    print(f"\n总计: {total_pass}/{total_checks} 通过")
    if all_pass:
        print("\n🎉 全部审计通过! Property 3 (长程推理/可保持) 完整实现。")
    else:
        print("\n⚠️ 部分检查未通过，详见上方具体失败项。")

    # 列出所有失败项
    failures = []
    for r in results:
        for name, passed, detail in r.checks:
            if not passed:
                failures.append(f"  [{r.module_name}] {name}: {detail}")
    if failures:
        print("\n失败项明细:")
        for f in failures:
            print(f)

    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
