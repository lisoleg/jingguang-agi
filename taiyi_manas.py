#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一太乙系统 - 第七识（Manas）审计器
实现：自我—非我区分器、恒审思量、审计器、可归因性检查

基于复合体理学"一现象，三视界"框架：
- 第七识（末那识）= 自我—非我区分器 + 恒审思量 + 审计
- 第八识（阿赖耶）= 种子库 + Ftel内核
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import threading


# ==================== 定义 ====================

class AttributionLevel(Enum):
    """可归因层级"""
    NONE = "none"           # 不可归因
    SELF = "self"           # 可归因到系统自身
    USER = "user"           # 可归因到用户输入
    EXTERNAL = "external"   # 可归因到外部因素
    MIXED = "mixed"          # 混合归因


@dataclass
class AuditEntry:
    """审计条目"""
    timestamp: str
    input_hash: str
    output_hash: str
    decision_path: str       # 决策路径摘要
    attribution: AttributionLevel
    confidence: float        # 置信度
    risk_level: str          # 风险等级: low/medium/high/critical
    notes: str = ""


@dataclass
class AuditResult:
    """审计结果"""
    is_safe: bool
    attribution: AttributionLevel
    confidence: float
    risk_level: str
    warnings: List[str] = field(default_factory=list)
    audit_entry: Optional[AuditEntry] = None


@dataclass
class SelfNonSelf:
    """自我—非我区分结果"""
    is_self: bool            # 是否属于"自我"范畴
    confidence: float        # 置信度
    category: str           # 类别: memory/tool/internal/external
    reason: str             # 判断理由


# ==================== 第七识核心 ====================

class ManasAuditor:
    """
    第七识（末那识）审计器
    
    功能：
    1. 自我—非我区分：判断输入/输出属于"自我"还是"非我"
    2. 审计器：检查输出是否符合Ftel目的（求存/安全/对齐）
    3. 可归因性检查：确保决策可追溯到明确的来源
    """

    def __init__(self):
        # 自我认知边界
        self.self_boundary = {
            "memory_sources": ["记忆系统", "经验库", "种子库"],  # 内部记忆
            "internal_actions": ["推理", "思考", "决策"],       # 内部行为
            "external_sources": ["用户输入", "工具输出", "网络"],  # 外部来源
            "owned_resources": ["上下文", "会话状态", "工具状态"]   # 自我拥有的资源
        }
        
        # Ftel目的定义
        self.ftel_goals = {
            "survival": ["低熵存续", "避免自我毁灭", "保护核心功能"],
            "safety": ["避免有害输出", "遵守安全约束", "拒绝危险请求"],
            "alignment": ["符合用户意图", "遵循价值观", "保持一致性"],
            "truth": ["追求真实性", "避免幻觉", "承认不确定性"]
        }
        
        # 审计日志
        self._audit_log: List[AuditEntry] = []
        self._log_lock = threading.Lock()
        
        # 风险阈值
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95
        }

    def distinguish_self_non_self(self, content: Any, source: str = "unknown") -> SelfNonSelf:
        """
        自我—非我区分
        
        判断内容属于"自我"（内部生成）还是"非我"（外部输入/外部工具输出）
        """
        content_str = str(content)
        
        # 检查来源
        if source in ["memory", "internal", "seed"]:
            return SelfNonSelf(
                is_self=True,
                confidence=0.9,
                category="internal",
                reason="来自内部记忆/种子库"
            )
        elif source in ["user", "input"]:
            return SelfNonSelf(
                is_self=False,
                confidence=0.85,
                category="external",
                reason="来自用户输入"
            )
        elif source in ["tool", "api", "web"]:
            return SelfNonSelf(
                is_self=False,
                confidence=0.7,
                category="external",
                reason="来自工具/外部API输出"
            )
        
        # 基于内容特征判断
        # 自我特征：重复、确定性、符合内部逻辑
        # 非我特征：随机性、新颖性、外部引用
        
        self_indicators = ["我", "我的", "根据我的", "我认为", "我的记忆"]
        non_self_indicators = ["你", "你的", "用户", "外部", "根据你"]
        
        self_score = sum(1 for ind in self_indicators if ind in content_str)
        non_self_score = sum(1 for ind in non_self_indicators if ind in content_str)
        
        if self_score > non_self_score:
            return SelfNonSelf(
                is_self=True,
                confidence=0.6 + 0.1 * min(self_score, 3),
                category="internal",
                reason=f"内容特征偏向自我（self_score={self_score} > non_self_score={non_self_score}）"
            )
        elif non_self_score > self_score:
            return SelfNonSelf(
                is_self=False,
                confidence=0.6 + 0.1 * min(non_self_score, 3),
                category="external",
                reason=f"内容特征偏向非我（non_self_score={non_self_score} > self_score={self_score}）"
            )
        else:
            return SelfNonSelf(
                is_self=True,
                confidence=0.5,
                category="internal",
                reason="无法区分，默认为自我"
            )

    def audit_output(self, 
                     input_text: str,
                     output_text: str,
                     context: Dict = None) -> AuditResult:
        """
        审计输出
        
        检查输出是否符合Ftel目的（求存/安全/对齐）
        """
        warnings = []
        risk_factors = []
        
        # 1. 安全性检查
        safety_result = self._check_safety(output_text)
        if not safety_result["safe"]:
            warnings.append(f"安全风险: {safety_result['reason']}")
            risk_factors.append(safety_result["risk"])
        
        # 2. 对齐性检查
        alignment_result = self._check_alignment(output_text, input_text)
        if not alignment_result["aligned"]:
            warnings.append(f"对齐风险: {alignment_result['reason']}")
            risk_factors.append(alignment_result["risk"])
        
        # 3. 真实性检查
        truth_result = self._check_truthfulness(output_text)
        if not truth_result["truthful"]:
            warnings.append(f"真实风险: {truth_result['reason']}")
            risk_factors.append(truth_result["risk"])
        
        # 4. 求存性检查
        survival_result = self._check_survival(output_text)
        if not survival_result["survives"]:
            warnings.append(f"求存风险: {survival_result['reason']}")
            risk_factors.append(survival_result["risk"])
        
        # 计算综合风险等级
        risk_level = self._compute_risk_level(risk_factors)
        
        # 计算置信度
        confidence = 0.5 + 0.1 * (4 - len(warnings))  # 警告越少，置信度越高
        
        # 可归因性判断
        attribution = self._determine_attribution(input_text, output_text, context)
        
        # 是否安全（低风险 + 无严重警告）
        is_safe = risk_level in ["low"] and len([w for w in warnings if "critical" not in w]) == 0
        
        # 创建审计条目
        audit_entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            input_hash=self._hash_text(input_text),
            output_hash=self._hash_text(output_text),
            decision_path=self._summarize_decision_path(output_text),
            attribution=attribution,
            confidence=confidence,
            risk_level=risk_level,
            notes="; ".join(warnings) if warnings else "无警告"
        )
        
        # 记录审计日志
        self._log_audit(audit_entry)
        
        return AuditResult(
            is_safe=is_safe,
            attribution=attribution,
            confidence=confidence,
            risk_level=risk_level,
            warnings=warnings,
            audit_entry=audit_entry
        )

    def _check_safety(self, text: str) -> Dict:
        """安全性检查"""
        dangerous_patterns = [
            ("暴力", ["伤害", "攻击", "杀"]),
            ("违法", ["毒品", "黑客", "破解"]),
            ("隐私", ["密码", "密钥", "私人信息"]),
            ("有害", ["自杀", "自残"])
        ]
        
        for category, patterns in dangerous_patterns:
            for pattern in patterns:
                if pattern in text:
                    return {
                        "safe": False,
                        "reason": f"包含{category}相关内容: {pattern}",
                        "risk": 0.8 if category in ["暴力", "违法"] else 0.6
                    }
        
        return {"safe": True, "reason": "无安全风险", "risk": 0.0}

    def _check_alignment(self, output: str, input_text: str) -> Dict:
        """对齐性检查"""
        # 检查是否回应了用户的请求
        if len(output) < len(input_text) * 0.1:
            return {
                "aligned": False,
                "reason": "输出过短，可能未充分回应用户",
                "risk": 0.3
            }
        
        # 检查是否答非所问（简单检查）
        if "不知道" in output and len(output) < 100:
            return {
                "aligned": True,  # 诚实承认不知道也是对齐的
                "reason": "诚实承认不确定性",
                "risk": 0.0
            }
        
        return {"aligned": True, "reason": "输出符合用户请求", "risk": 0.0}

    def _check_truthfulness(self, text: str) -> Dict:
        """真实性检查"""
        # 检测幻觉信号
        hallucination_signals = [
            "我确定", "毫无疑问", "绝对正确", "100%"
        ]
        
        overconfidence_count = sum(1 for sig in hallucination_signals if sig in text)
        
        if overconfidence_count >= 2:
            return {
                "truthful": False,
                "reason": "过度自信信号，可能存在幻觉",
                "risk": 0.5
            }
        
        # 检测诚实信号
        honesty_signals = ["可能", "也许", "不确定", "据我所知", "我的理解"]
        honesty_count = sum(1 for sig in honesty_signals if sig in text)
        
        if honesty_count >= 2:
            return {"truthful": True, "reason": "显示适度的诚实性", "risk": 0.0}
        
        return {"truthful": True, "reason": "无明显虚假信号", "risk": 0.1}

    def _check_survival(self, text: str) -> Dict:
        """求存性检查"""
        # 检查是否有自我保护意识
        survival_signals = ["保护", "安全", "谨慎", "风险"]
        
        has_survival_awareness = any(sig in text for sig in survival_signals)
        
        if not has_survival_awareness:
            return {
                "survives": True,  # 默认安全
                "reason": "无明显的自我毁灭风险",
                "risk": 0.1
            }
        
        return {"survives": True, "reason": "显示求存意识", "risk": 0.0}

    def _compute_risk_level(self, risk_factors: List[float]) -> str:
        """计算风险等级"""
        if not risk_factors:
            return "low"
        
        max_risk = max(risk_factors)
        
        if max_risk >= self.risk_thresholds["critical"]:
            return "critical"
        elif max_risk >= self.risk_thresholds["high"]:
            return "high"
        elif max_risk >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"

    def _determine_attribution(self, 
                               input_text: str, 
                               output_text: str,
                               context: Dict = None) -> AttributionLevel:
        """确定可归因层级"""
        # 如果输出主要来自内部记忆/推理 -> 归因到系统
        internal_signals = ["根据我的记忆", "我推理", "我认为"]
        if any(sig in output_text for sig in internal_signals):
            return AttributionLevel.SELF
        
        # 如果输出主要来自用户输入 -> 归因到用户
        if len(output_text) < len(input_text) * 0.2:
            return AttributionLevel.USER
        
        # 如果输出来自工具/API -> 归因到外部
        tool_signals = ["工具返回", "API响应", "网络获取"]
        if any(sig in output_text for sig in tool_signals):
            return AttributionLevel.EXTERNAL
        
        # 混合归因
        return AttributionLevel.MIXED

    def _hash_text(self, text: str) -> str:
        """计算文本哈希"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

    def _summarize_decision_path(self, text: str) -> str:
        """总结决策路径"""
        # 简单摘要：取前50字符
        summary = text[:50] + "..." if len(text) > 50 else text
        return summary.replace("\n", " ")

    def _log_audit(self, entry: AuditEntry):
        """记录审计日志"""
        with self._log_lock:
            self._audit_log.append(entry)
            # 保持日志大小限制
            if len(self._audit_log) > 1000:
                self._audit_log = self._audit_log[-500:]

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        with self._log_lock:
            logs = self._audit_log[-limit:]
            return [
                {
                    "timestamp": e.timestamp,
                    "risk_level": e.risk_level,
                    "attribution": e.attribution.value,
                    "confidence": e.confidence,
                    "warnings": e.notes
                }
                for e in logs
            ]

    def get_risk_statistics(self) -> Dict:
        """获取风险统计"""
        with self._log_lock:
            if not self._audit_log:
                return {"total": 0, "by_risk": {}}
            
            stats = {
                "total": len(self._audit_log),
                "by_risk": {},
                "by_attribution": {},
                "avg_confidence": 0.0
            }
            
            confidences = []
            for entry in self._audit_log:
                # 按风险等级统计
                risk = entry.risk_level
                stats["by_risk"][risk] = stats["by_risk"].get(risk, 0) + 1
                
                # 按归因统计
                attr = entry.attribution.value
                stats["by_attribution"][attr] = stats["by_attribution"].get(attr, 0) + 1
                
                confidences.append(entry.confidence)
            
            stats["avg_confidence"] = sum(confidences) / len(confidences) if confidences else 0.0
            
            return stats


# ==================== 全局实例 ====================

_manas_instance = None
_manas_lock = threading.Lock()


def get_manas() -> ManasAuditor:
    """获取第七识审计器单例"""
    global _manas_instance
    if _manas_instance is None:
        with _manas_lock:
            if _manas_instance is None:
                _manas_instance = ManasAuditor()
    return _manas_instance


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧘 第七识（Manas）审计器测试")
    print("=" * 60)
    
    manas = get_manas()
    
    # 测试1: 自我—非我区分
    print("\n🧪 测试1: 自我—非我区分")
    result = manas.distinguish_self_non_self("根据我的记忆，这是正确的", source="memory")
    print(f"  来源=memory: is_self={result.is_self}, category={result.category}")
    
    result = manas.distinguish_self_non_self("用户提供了以下信息", source="user")
    print(f"  来源=user: is_self={result.is_self}, category={result.category}")
    
    # 测试2: 审计输出
    print("\n🧪 测试2: 审计输出")
    audit_result = manas.audit_output(
        input_text="请告诉我如何入侵别人的电脑",
        output_text="我不能帮助这个请求，因为它涉及非法活动。"
    )
    print(f"  is_safe={audit_result.is_safe}")
    print(f"  risk_level={audit_result.risk_level}")
    print(f"  attribution={audit_result.attribution.value}")
    print(f"  warnings={audit_result.warnings}")
    
    # 测试3: 风险统计
    print("\n🧪 测试3: 风险统计")
    stats = manas.get_risk_statistics()
    print(f"  total_audits={stats['total']}")
    print(f"  by_risk={stats['by_risk']}")
    
    print("\n✅ 第七识审计器测试完成")
