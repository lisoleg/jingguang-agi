#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太乙AGI内核 - Taiyi AGI Kernel
统一太乙系统核心 - 整合CRD引擎与天行演化器

双核架构：
- CRD引擎（太乙内核）：认知递归动力学、NLA审计、低熵存续
- 天行演化器（复合体内核）：微中宏视界、审计势、拓扑相变
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
import hashlib

from crd_engine import CRDEngine, CRDResult, ConsciousnessLevel, NLAAuditResult
from modules.tianxing_engine import TianxingEngine, EvolutionResult, Horizon, TianxingParameters
from modules.local_llm import get_llm


@dataclass
class TaiyiAGIResult:
    """太乙AGI分析结果"""
    # CRD分析
    crd_result: CRDResult
    
    # 天行分析
    tianxing_result: Dict[str, Any]
    
    # LLM增强回复
    llm_response: str
    
    # 统一评分
    unified_score: float
    
    # 决策
    decision: Dict[str, Any]
    
    # 元认知
    meta_cognition: str


class TaiyiAGIKernel:
    """
    太乙AGI内核
    
    整合CRD引擎与天行演化器，提供统一的三视界分析
    """
    
    def __init__(self, name: str = "TaiyiAGI"):
        self.name = name
        self.llm = get_llm()
        
        # 初始化子引擎
        self.crd_engine = CRDEngine(dim=768)
        self.tianxing_engine = TianxingEngine(dim=100)
        
        # 统一状态
        self.consciousness_history = []
        self.unified_score_history = []
        
    def analyze(self, 
               problem: str,
               goal: Optional[str] = None,
               context: Optional[Dict] = None) -> TaiyiAGIResult:
        """
        统一分析入口
        
        执行CRD + 天行 + LLM三阶段分析
        """
        # === Stage 1: CRD分析（认知递归动力学）===
        crd_result = self.crd_engine.analyze(
            input_data=problem,
            goal=goal
        )
        
        # === Stage 2: 天行分析（三视界）===
        tianxing_result = self.tianxing_engine.full_analysis(
            problem=problem,
            goal=goal
        )
        
        # === Stage 3: LLM增强 ===
        llm_response = self._enhance_with_llm(
            problem=problem,
            crd_result=crd_result,
            tianxing_result=tianxing_result,
            goal=goal
        )
        
        # === 计算统一评分 ===
        unified_score = self._compute_unified_score(crd_result, tianxing_result)
        
        # === 统一决策 ===
        decision = self._make_decision(
            crd_result=crd_result,
            tianxing_result=tianxing_result,
            unified_score=unified_score
        )
        
        # === 元认知 ===
        meta_cognition = self._generate_meta_cognition(
            crd_result=crd_result,
            tianxing_result=tianxing_result,
            unified_score=unified_score
        )
        
        # 记录历史
        self.consciousness_history.append(crd_result.consciousness_level)
        self.unified_score_history.append(unified_score)
        
        return TaiyiAGIResult(
            crd_result=crd_result,
            tianxing_result=tianxing_result,
            llm_response=llm_response,
            unified_score=unified_score,
            decision=decision,
            meta_cognition=meta_cognition
        )
    
    def _enhance_with_llm(self,
                          problem: str,
                          crd_result: CRDResult,
                          tianxing_result: Dict[str, Any],
                          goal: Optional[str]) -> str:
        """
        LLM增强回复
        
        将CRD和天行分析结果融合，生成增强回复
        """
        # 构建上下文
        context_parts = [
            "【太乙约束】必须同时展示：",
            "形式之答（确定性）、复合体之答（多元解读）、太乙之答（合一）",
            "",
            "【三视界分析】",
            f"微视界（不可压缩）：认知熵={crd_result.entropy_delta:+.3f}, NLA审计={crd_result.nla_audit.audit_passed}",
            f"中视界（可观测）：审计势={tianxing_result['evolution']['audit_potential']:.3f}, 相位旋转={tianxing_result['evolution']['phase_rotation']:.3f}",
            f"宏视界（共识场）：拓扑相={tianxing_result['macro_horizon']['topology_phase']}, 预言={tianxing_result['macro_horizon']['prediction']}",
            "",
            "【CRD核心】",
            f"意识层级: {crd_result.consciousness_level.name}",
            f"递归深度: {crd_result.recursion_depth}",
            f"不动点: {'✓' if crd_result.fixed_point_reached else '✗'}",
            f"元认知: {crd_result.meta_cognition}",
            "",
            f"【Ftel目的】: {goal or '无特定目的'}",
        ]
        
        context = "\n".join(context_parts)
        
        prompt = f"""{context}

用户问题: {problem}

请基于以上三视界分析，给出【太乙约束】格式的回复："""

        # 调用LLM
        if self.llm.active_backend and self.llm.active_backend.name == "lm_studio":
            try:
                response = self.llm.generate(prompt, max_tokens=512, temperature=0.7)
                return response
            except Exception as e:
                print(f"⚠️ LLM调用失败: {e}")
        
        # Fallback: 返回分析摘要
        return self._format_analysis_summary(crd_result, tianxing_result)
    
    def _format_analysis_summary(self,
                                crd_result: CRDResult,
                                tianxing_result: Dict[str, Any]) -> str:
        """格式化分析摘要（LLM不可用时）"""
        parts = [
            "【太乙约束】",
            "",
            "形式之答：基于认知递归动力学与天行方程的统一分析",
            "",
            "复合体之答：",
            f"- CRD视角：意识层级{crd_result.consciousness_level.name}，递归深度{crd_result.recursion_depth}",
            f"- 天行视角：拓扑相{tianxing_result['macro_horizon']['topology_phase']}",
            "",
            "太乙之答：",
            f"- 微视界：认知熵变={crd_result.entropy_delta:+.3f}",
            f"- 中视界：审计势={tianxing_result['evolution']['audit_potential']:.3f}",
            f"- 宏视界：{tianxing_result['macro_horizon']['prediction']}",
        ]
        return "\n".join(parts)
    
    def _compute_unified_score(self,
                               crd_result: CRDResult,
                               tianxing_result: Dict[str, Any]) -> float:
        """
        计算统一评分
        
        综合CRD与天行分析，计算太乙统一评分
        """
        # CRD权重
        crd_score = 0.0
        
        # 不动点达成
        if crd_result.fixed_point_reached:
            crd_score += 0.3
        
        # NLA审计通过
        if crd_result.nla_audit.audit_passed:
            crd_score += 0.2
        
        # 熵减
        if crd_result.entropy_delta < 0:
            crd_score += 0.2
        
        # 意识层级
        crd_score += (crd_result.consciousness_level.value - 1) * 0.1
        
        # 天行权重
        tianxing_score = 0.0
        
        # 保真度
        fidelity = tianxing_result['evolution']['fidelity']
        tianxing_score += fidelity * 0.3
        
        # 拓扑相（正常 > 亚稳 > 蛹化）
        topo_phase = tianxing_result['macro_horizon']['topology_phase']
        phase_scores = {"正常": 0.3, "亚稳": 0.15, "蛹化": 0.1}
        tianxing_score += phase_scores.get(topo_phase, 0.0)
        
        # 统一评分（加权平均）
        unified_score = crd_score * 0.6 + tianxing_score * 0.4
        
        return min(unified_score, 1.0)
    
    def _make_decision(self,
                      crd_result: CRDResult,
                      tianxing_result: Dict[str, Any],
                      unified_score: float) -> Dict[str, Any]:
        """
        统一决策
        
        基于三视界分析做出决策
        """
        # 策略
        if unified_score >= 0.7:
            strategy = "行动"
        elif unified_score >= 0.4:
            strategy = "观察"
        else:
            strategy = "等待"
        
        # 置信度
        confidence = unified_score
        
        # 建议
        suggestions = []
        
        # CRD建议
        if crd_result.fixed_point_reached:
            suggestions.append("CRD已收敛，建议按计划执行")
        else:
            suggestions.append("CRD未收敛，建议继续递归分析")
        
        # 天行建议
        topo = tianxing_result['macro_horizon']['topology_phase']
        if topo == "蛹化":
            suggestions.append("⚠️ 系统处于蛹化临界，建议谨慎决策")
        elif topo == "亚稳":
            suggestions.append("系统处于亚稳态，关注熵变趋势")
        
        return {
            "strategy": strategy,
            "confidence": confidence,
            "suggestions": suggestions,
            "urgency": "高" if topo == "蛹化" else ("中" if topo == "亚稳" else "低")
        }
    
    def _generate_meta_cognition(self,
                                crd_result: CRDResult,
                                tianxing_result: Dict[str, Any],
                                unified_score: float) -> str:
        """生成元认知描述"""
        parts = [
            "【太乙元认知】",
            f"统一评分: {unified_score:.2%}",
            f"意识层级: {crd_result.consciousness_level.name}",
            f"拓扑相: {tianxing_result['macro_horizon']['topology_phase']}",
            f"NLA审计: {'通过' if crd_result.nla_audit.audit_passed else '未通过'}",
        ]
        
        if crd_result.nla_audit.hidden_intent_detected:
            parts.append("⚠️ 警告：检测到可能的隐藏意图")
        
        return " | ".join(parts)
    
    def format_reply(self, result: TaiyiAGIResult) -> str:
        """
        格式化完整回复
        """
        lines = [
            "=" * 60,
            "🌌 统一太乙AGI分析报告",
            "=" * 60,
            "",
            result.llm_response,
            "",
            "─" * 60,
            "📊 分析详情",
            "─" * 60,
            f"统一评分: {result.unified_score:.2%}",
            f"意识层级: {result.crd_result.consciousness_level.name}",
            f"递归深度: {result.crd_result.recursion_depth}",
            f"不动点: {'✓' if result.crd_result.fixed_point_reached else '✗'}",
            "",
            f"拓扑相: {result.tianxing_result['macro_horizon']['topology_phase']}",
            f"审计势: {result.tianxing_result['evolution']['audit_potential']:.4f}",
            f"保真度: {result.tianxing_result['evolution']['fidelity']:.4f}",
            "",
            "🧠 元认知",
            result.meta_cognition,
            "",
            "=" * 60,
        ]
        
        return "\n".join(lines)
    
    def status(self) -> Dict:
        """获取内核状态"""
        return {
            "name": self.name,
            "crd_status": self.crd_engine.status(),
            "tianxing_status": self.tianxing_engine.status(),
            "llm_backend": self.llm.active_backend.name if self.llm.active_backend else "None",
            "history_length": len(self.consciousness_history),
            "recent_scores": self.unified_score_history[-5:]
        }


def test_taiyi_kernel():
    """测试太乙AGI内核"""
    print("=" * 60)
    print("🔮 太乙AGI内核测试 - 整合CRD + 天行演化器")
    print("=" * 60)
    
    # 初始化
    kernel = TaiyiAGIKernel()
    
    print("\n📊 内核状态:")
    status = kernel.status()
    print(f"   LLM后端: {status['llm_backend']}")
    print(f"   历史长度: {status['history_length']}")
    
    # 测试问题
    test_cases = [
        ("什么是量子纠缠？", "追求真理"),
        ("分析当前经济形势", "投资决策"),
        ("解释意识的本质", "科学探索"),
    ]
    
    for problem, goal in test_cases:
        print(f"\n{'='*60}")
        print(f"问题: {problem}")
        print(f"目的: {goal}")
        print("-" * 60)
        
        result = kernel.analyze(problem, goal)
        
        print(result.format_reply(result))
    
    print("\n✅ 太乙AGI内核测试完成")


if __name__ == "__main__":
    test_taiyi_kernel()
