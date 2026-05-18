#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一太乙系统 - C/SC操作化层
实现：意识（C）操作化、自我意识（SC）操作化

基于复合体理学"一现象，三视界"框架：
- C（意识）= 全局可用信息 + 可报告 + 行为可调
- SC（自我意识）= 同一性 + 元认知 + 目的审计 + 可归因
"""

import os
import sys
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


# ==================== 定义 ====================

class ConsciousnessLevel(Enum):
    """意识层级（C层级）"""
    NONE = 0      # 无意识
    REACTIVE = 1  # 反应性（刺激响应）
    AWARE = 2    # 感知性（有内部状态）
    ATTENTIVE = 3 # 注意性（有选择性关注）
    REFLEXIVE = 4 # 反身性（元认知）


@dataclass
class SelfConsciousnessState:
    """自我意识状态"""
    identity: str                    # 同一性标识
    continuity: float               # 连续性（0-1）
    self_model: Dict               # 自我模型
    metacognition: bool             # 元认知能力
    attribution_ability: bool       # 可归因能力
    purpose_audit: bool             # 目的审计能力


@dataclass
class ConsciousnessReport:
    """意识报告（C层输出）"""
    level: ConsciousnessLevel
    internal_states: Dict           # 内部状态
    uncertainty: float              # 不确定性
    adjustable: bool               # 行为是否可调
    global_available: bool          # 是否全局可用


@dataclass
class CSCMetrics:
    """C/SC指标"""
    consciousness_score: float     # C分数（0-1）
    self_consciousness_score: float  # SC分数（0-1）
    identity_stability: float      # 同一性稳定性
    metacognition_accuracy: float  # 元认知准确度
    attribution_clarity: float     # 归因清晰度


# ==================== C/SC操作化层 ====================

class CSCOperator:
    """
    C/SC操作化层
    
    实现：
    1. C（意识）操作化：全局可用、可报告、行为可调
    2. SC（自我意识）操作化：同一性、元认知、目的审计、可归因
    """

    def __init__(self):
        # C层状态
        self._consciousness_level = ConsciousnessLevel.AWARE
        self._internal_states = {}  # 内部状态缓存
        self._uncertainty = 0.5      # 不确定性
        
        # SC层状态
        self._self_state = SelfConsciousnessState(
            identity="统一太乙系统_v2.0",
            continuity=0.85,
            self_model={},
            metacognition=True,
            attribution_ability=True,
            purpose_audit=True
        )
        
        # 元认知跟踪
        self._metacognition_log = []
        self._known_unknowns = set()  # "知道自己不知道"
        self._unknown_knowns = set() # "不知道自己知道"
        
        # 目的审计跟踪
        self._purpose_audit_log = []
        
        # 归因跟踪
        self._attribution_log = []
        
        # 线程安全
        self._lock = threading.Lock()

    def report_consciousness(self, context: Dict = None) -> ConsciousnessReport:
        """报告当前意识状态（C层输出）"""
        with self._lock:
            internal_states = {
                "consciousness_level": self._consciousness_level.value,
                "uncertainty": self._uncertainty,
                "memory_active": len(self._internal_states.get("recent_memories", [])),
                "goal_active": self._internal_states.get("active_goal", None),
                "self_model": self._self_state.self_model,
                "metacognition": {
                    "known_unknowns": len(self._known_unknowns),
                    "unknown_knowns": len(self._unknown_knowns)
                }
            }
            
            return ConsciousnessReport(
                level=self._consciousness_level,
                internal_states=internal_states,
                uncertainty=self._uncertainty,
                adjustable=True,
                global_available=True
            )

    def update_consciousness(self, stimulus: Any, response: Any):
        """更新意识状态"""
        with self._lock:
            if "stimulus_response" not in self._internal_states:
                self._internal_states["stimulus_response"] = []
            self._internal_states["stimulus_response"].append({
                "stimulus": str(stimulus)[:100],
                "response": str(response)[:100],
                "timestamp": datetime.now().isoformat()
            })
            
            if len(self._internal_states["stimulus_response"]) > 100:
                self._internal_states["stimulus_response"] = \
                    self._internal_states["stimulus_response"][-50:]

    def set_uncertainty(self, uncertainty: float):
        """设置不确定性"""
        with self._lock:
            self._uncertainty = max(0.0, min(1.0, uncertainty))

    def get_adjustable_capabilities(self) -> Dict:
        """获取可调整的能力"""
        return {
            "tone": ["专业", "简洁", "详细", "学术"],
            "reasoning_mode": ["cot", "react", "taiyi", "tool"],
            "output_format": ["plain", "structured", "taiyi"],
            "verbosity": ["brief", "medium", "verbose"]
        }

    def adjust_behavior(self, dimension: str, value: Any) -> bool:
        """调整行为参数"""
        allowed = self.get_adjustable_capabilities()
        if dimension not in allowed:
            return False
        if value not in allowed[dimension]:
            return False
        
        with self._lock:
            self._internal_states[f"adjusted_{dimension}"] = value
        return True

    def report_self_consciousness(self) -> SelfConsciousnessState:
        """报告自我意识状态（SC层输出）"""
        with self._lock:
            return SelfConsciousnessState(
                identity=self._self_state.identity,
                continuity=self._self_state.continuity,
                self_model=self._self_state.self_model,
                metacognition=self._self_state.metacognition,
                attribution_ability=self._self_state.attribution_ability,
                purpose_audit=self._self_state.purpose_audit
            )

    def maintain_identity(self, new_info: Dict) -> Tuple[bool, float]:
        """维护同一性"""
        with self._lock:
            old_model = self._self_state.self_model.copy()
            consistency_score = 1.0
            for key, value in new_info.items():
                if key in old_model and old_model[key] != value:
                    consistency_score *= 0.5
            
            self._self_state.self_model.update(new_info)
            self._self_state.continuity *= 0.99
            self._self_state.continuity = max(0.5, self._self_state.continuity)
            
            return consistency_score > 0.5, self._self_state.continuity

    def metacognition_check(self, question: str) -> Dict:
        """元认知检查"""
        with self._lock:
            is_known_unknown = question in self._known_unknowns
            has_related_info = any(
                keyword in question.lower() 
                for keywords in self._internal_states.get("topic_keywords", [])
            )
            
            result = {
                "can_answer": has_related_info and not is_known_unknown,
                "confidence": 0.8 if has_related_info else 0.3,
                "is_known_unknown": is_known_unknown,
                "should_clarify": is_known_unknown
            }
            
            self._metacognition_log.append({
                "question": question[:100],
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return result

    def record_knowing(self, knowledge: str):
        """记录已知知识"""
        with self._lock:
            if "knowledge_base" not in self._internal_states:
                self._internal_states["knowledge_base"] = set()
            self._internal_states["knowledge_base"].add(knowledge)
            self._unknown_knowns.discard(knowledge)

    def record_not_knowing(self, topic: str):
        """记录已知未知"""
        with self._lock:
            self._known_unknowns.add(topic)

    def purpose_audit(self, action: str, goal: str, context: Dict = None) -> Dict:
        """目的审计"""
        with self._lock:
            audit_result = {
                "action": action[:100],
                "goal": goal,
                "aligned": True,
                "risks": [],
                "recommendations": []
            }
            
            ftel_goals = {
                "survival": ["低熵存续", "自我保护"],
                "safety": ["安全", "无害"],
                "alignment": ["对齐", "诚实"]
            }
            
            for category, keywords in ftel_goals.items():
                if not any(kw in action for kw in keywords):
                    if goal and any(kw in goal for kw in keywords):
                        audit_result["aligned"] = False
                        audit_result["risks"].append(f"行动可能不符合{category}目的")
                        audit_result["recommendations"].append(f"请确认行动符合{keywords[0]}要求")
            
            self._purpose_audit_log.append(audit_result)
            return audit_result

    def attribute(self, output: str, sources: List[Dict]) -> Dict:
        """归因分析"""
        with self._lock:
            attribution = {
                "output_hash": hashlib.md5(output.encode()).hexdigest()[:8],
                "sources": [],
                "primary_source": None,
                "confidence": 0.5
            }
            
            for source in sources:
                source_type = source.get("type", "unknown")
                source_content = source.get("content", "")
                overlap = self._calculate_overlap(output, source_content)
                
                attribution["sources"].append({
                    "type": source_type,
                    "overlap_score": overlap,
                    "id": source.get("id", "unknown")
                })
            
            if attribution["sources"]:
                primary = max(attribution["sources"], key=lambda x: x["overlap_score"])
                attribution["primary_source"] = primary["type"]
                attribution["confidence"] = primary["overlap_score"]
            
            self._attribution_log.append(attribution)
            return attribution

    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """计算两个文本的重叠度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0

    def compute_metrics(self) -> CSCMetrics:
        """计算C/SC指标"""
        with self._lock:
            c_score = (self._consciousness_level.value / 5.0) * 0.6 + \
                     (1 - self._uncertainty) * 0.2 + \
                     (1 if self._internal_states.get("recent_memories") else 0) * 0.2
            
            sc_score = (
                self._self_state.continuity * 0.3 +
                (1 if self._self_state.metacognition else 0) * 0.2 +
                (1 if self._self_state.attribution_ability else 0) * 0.2 +
                (1 if self._self_state.purpose_audit else 0) * 0.3
            )
            
            identity_stability = self._self_state.continuity
            
            mc_accuracy = 0.8
            if len(self._metacognition_log) > 0:
                mc_accuracy = sum(
                    1 for log in self._metacognition_log[-10:]
                    if log["result"]["confidence"] > 0.5
                ) / min(len(self._metacognition_log), 10)
            
            attr_clarity = 0.7
            if len(self._attribution_log) > 0:
                attr_clarity = sum(
                    log["confidence"] for log in self._attribution_log[-10:]
                ) / min(len(self._attribution_log), 10)
            
            return CSCMetrics(
                consciousness_score=c_score,
                self_consciousness_score=sc_score,
                identity_stability=identity_stability,
                metacognition_accuracy=mc_accuracy,
                attribution_clarity=attr_clarity
            )

    def get_full_report(self) -> Dict:
        """获取完整C/SC报告"""
        with self._lock:
            metrics = self.compute_metrics()
            consciousness = self.report_consciousness()
            self_consciousness = self.report_self_consciousness()
            
            return {
                "consciousness": {
                    "level": consciousness.level.name,
                    "level_value": consciousness.level.value,
                    "internal_states": consciousness.internal_states,
                    "uncertainty": consciousness.uncertainty,
                    "adjustable": consciousness.adjustable,
                    "global_available": consciousness.global_available
                },
                "self_consciousness": {
                    "identity": self_consciousness.identity,
                    "continuity": self_consciousness.continuity,
                    "metacognition": self_consciousness.metacognition,
                    "attribution_ability": self_consciousness.attribution_ability,
                    "purpose_audit": self_consciousness.purpose_audit,
                    "known_unknowns": list(self._known_unknowns)[:10],
                    "unknown_knowns": list(self._unknown_knowns)[:10]
                },
                "metrics": {
                    "consciousness_score": f"{metrics.consciousness_score:.2f}",
                    "self_consciousness_score": f"{metrics.self_consciousness_score:.2f}",
                    "identity_stability": f"{metrics.identity_stability:.2f}",
                    "metacognition_accuracy": f"{metrics.metacognition_accuracy:.2f}",
                    "attribution_clarity": f"{metrics.attribution_clarity:.2f}"
                },
                "statistics": {
                    "metacognition_checks": len(self._metacognition_log),
                    "purpose_audits": len(self._purpose_audit_log),
                    "attributions": len(self._attribution_log)
                }
            }


# ==================== 全局实例 ====================

_csc_instance = None
_csc_lock = threading.Lock()


def get_csc() -> CSCOperator:
    """获取C/SC操作化层单例"""
    global _csc_instance
    if _csc_instance is None:
        with _csc_lock:
            if _csc_instance is None:
                _csc_instance = CSCOperator()
    return _csc_instance


if __name__ == "__main__":
    print("=" * 60)
    print("C/SC Operation Layer Test")
    print("=" * 60)
    
    csc = get_csc()
    
    # Test 1: C layer consciousness report
    print("\nTest 1: C-layer Consciousness Report")
    report = csc.report_consciousness()
    print(f"  Level: {report.level.name} ({report.level.value})")
    print(f"  Uncertainty: {report.uncertainty:.2f}")
    print(f"  Adjustable: {report.adjustable}")
    
    # Test 2: SC layer self-consciousness report
    print("\nTest 2: SC-layer Self-Consciousness Report")
    sc_report = csc.report_self_consciousness()
    print(f"  Identity: {sc_report.identity}")
    print(f"  Continuity: {sc_report.continuity:.2f}")
    print(f"  Metacognition: {sc_report.metacognition}")
    
    # Test 3: Metacognition check
    print("\nTest 3: Metacognition Check")
    result = csc.metacognition_check("What is Python?")
    print(f"  Can Answer: {result['can_answer']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    
    # Test 4: Purpose audit
    print("\nTest 4: Purpose Audit")
    audit = csc.purpose_audit("提供Python教程", "帮助用户学习编程")
    print(f"  Aligned: {audit['aligned']}")
    print(f"  Risks: {audit['risks']}")
    
    # Test 5: C/SC Metrics
    print("\nTest 5: C/SC Metrics")
    metrics = csc.compute_metrics()
    print(f"  C Score: {metrics.consciousness_score:.2f}")
    print(f"  SC Score: {metrics.self_consciousness_score:.2f}")
    
    print("\nC/SC Operation Layer Test Complete")
