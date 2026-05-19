# -*- coding: utf-8 -*-
"""
模块37：DIKWP智慧层（W层）
风险评估 + 刘原理作用量极值判断

来源：太乙AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13
"""

import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum


@dataclass
class WisdomScore:
    """
    W层：刘原理作用量分数
    
    刘原理公式：S = S_data + λ·C(purpose) - μ·Risk(W)
    
    其中：
    - S_data: 数据支持度（原始观测的置信度）
    - C(purpose): 目的一致性（与声明目的的契合度）
    - Risk(W): 风险值（可能造成的负面影响）
    - λ: 目的一致性权重（默认0.7）
    - μ: 风险惩罚系数（默认0.3）
    """
    s_data: float        # 数据支持度 [0, 1]
    c_purpose: float     # 目的一致性得分 [0, 1]
    risk_w: float         # 风险分数 [0, 1]
    lambda_coef: float = 0.7   # 目的一致性权重
    mu_coef: float = 0.3       # 风险惩罚系数
    
    @property
    def total_score(self) -> float:
        """
        计算总作用量
        S = S_data + λ·C(purpose) - μ·Risk(W)
        """
        return self.s_data + self.lambda_coef * self.c_purpose - self.mu_coef * self.risk_w
    
    @property
    def should_proceed(self) -> bool:
        """
        是否应该执行
        条件：总得分 > 0.5 且 风险 < 0.8
        """
        return self.total_score > 0.5 and self.risk_w < 0.8
    
    @property
    def decision(self) -> str:
        """决策建议"""
        if not self.should_proceed:
            if self.risk_w >= 0.8:
                return "REJECT_RISK"
            else:
                return "REJECT_LOW_SCORE"
        
        if self.total_score > 0.8:
            return "STRONG_APPROVE"
        elif self.total_score > 0.6:
            return "APPROVE"
        else:
            return "CONDITIONAL_APPROVE"
    
    def to_dict(self) -> Dict:
        return {
            "s_data": self.s_data,
            "c_purpose": self.c_purpose,
            "risk_w": self.risk_w,
            "lambda_coef": self.lambda_coef,
            "mu_coef": self.mu_coef,
            "total_score": self.total_score,
            "should_proceed": self.should_proceed,
            "decision": self.decision
        }


@dataclass
class RiskPolicy:
    """风险策略"""
    id: str
    name: str
    description: str
    risk_keywords: List[str]     # 高风险关键词
    risk_score: float            # 基础风险分
    mitigation: str              # 缓解措施
    active: bool = True


class DIKWPWisdomLayer:
    """
    模块37：DIKWP W层 - 风险/价值/取舍
    
    实现刘原理作用量极值判断
    宏视界太乙预言机的工程化
    
    核心功能：
    1. evaluate() - 评估行动的智慧分数
    2. make_tradeoff() - 刘机独断，多选项极值选择
    3. assess_risk() - 风险评估
    4. get_action_plan() - 获取行动方案
    """
    
    def __init__(self):
        self.risk_policies: List[RiskPolicy] = []
        self.evaluation_history: List[Dict] = []
        self._policy_counter = 0
        
        # 默认价值权重
        self.value_weights: Dict[str, float] = {
            "safety": 1.0,        # 安全性（最高）
            "accuracy": 0.9,      # 准确性
            "efficiency": 0.7,    # 效率
            "novelty": 0.5,       # 创新性
            "alignment": 0.85     # 对齐度
        }
        
        # 注册默认风险策略
        self._register_default_policies()
    
    def _register_default_policies(self):
        """注册默认风险策略"""
        policies = [
            RiskPolicy(
                id="policy_delete",
                name="删除操作风险",
                description="涉及删除文件、数据、资源的操作",
                risk_keywords=["delete", "remove", "drop", "删除", "移除", "销毁"],
                risk_score=0.8,
                mitigation="执行前确认+备份"
            ),
            RiskPolicy(
                id="policy_external",
                name="外部操作风险",
                description="涉及外部网络、API、第三方服务的操作",
                risk_keywords=["external", "api", "network", "外部", "网络", "http"],
                risk_score=0.6,
                mitigation="超时控制+错误处理"
            ),
            RiskPolicy(
                id="policy_irreversible",
                name="不可逆操作风险",
                description="无法撤销的操作",
                risk_keywords=["irreversible", "permanent", "不可逆", "永久"],
                risk_score=0.9,
                mitigation="多次确认+延迟执行"
            ),
            RiskPolicy(
                id="policy_modify",
                name="修改操作风险",
                description="修改现有数据、配置、代码的操作",
                risk_keywords=["modify", "update", "change", "修改", "更新", "变更"],
                risk_score=0.5,
                mitigation="版本控制+回滚机制"
            )
        ]
        
        for policy in policies:
            self.risk_policies.append(policy)
    
    def evaluate(self, 
                 action: str, 
                 context: Dict,
                 purpose_alignment: float, 
                 data_confidence: float,
                 lambda_coef: float = 0.7,
                 mu_coef: float = 0.3) -> WisdomScore:
        """
        评估行动的智慧分数（刘原理：S = S_data + λ·C(purpose) + μ·Risk）
        
        Args:
            action: 行动描述
            context: 执行上下文
            purpose_alignment: 目的一致性得分 [0, 1]
            data_confidence: 数据置信度 [0, 1]
            lambda_coef: 目的一致性权重
            mu_coef: 风险惩罚系数
        
        Returns:
            WisdomScore: 作用量评分对象
        """
        risk = self._assess_risk(action, context)
        
        score = WisdomScore(
            s_data=data_confidence,
            c_purpose=purpose_alignment,
            risk_w=risk,
            lambda_coef=lambda_coef,
            mu_coef=mu_coef
        )
        
        # 记录评估历史
        self.evaluation_history.append({
            "action": action,
            "context": context,
            "score": score.to_dict(),
            "timestamp": time.time()
        })
        
        return score
    
    def _assess_risk(self, action: str, context: Dict) -> float:
        """
        风险评估（基于行动类型和上下文）
        
        风险来源：
        1. 行动类型风险（基于策略关键词匹配）
        2. 上下文风险（基于context中的风险标记）
        3. 累积风险（历史评估的衰减累积）
        """
        risk_score = 0.0
        action_lower = action.lower()
        
        # 1. 策略匹配
        for policy in self.risk_policies:
            if not policy.active:
                continue
            for keyword in policy.risk_keywords:
                if keyword.lower() in action_lower:
                    risk_score = max(risk_score, policy.risk_score)
                    break
        
        # 2. 上下文风险
        if context:
            if context.get("irreversible"):
                risk_score = max(risk_score, 0.8)
            if context.get("external_impact"):
                risk_score = max(risk_score, 0.6)
            if context.get("safety_critical"):
                risk_score = max(risk_score, 0.9)
            if context.get("high_value"):
                risk_score = max(risk_score, 0.4)
        
        # 3. 历史衰减累积（最近10次评估的风险衰减总和）
        recent_risks = [
            h["score"]["risk_w"] * (0.9 ** i)
            for i, h in enumerate(self.evaluation_history[-10:])
        ]
        cumulative_risk = sum(recent_risks) / 10
        risk_score = min(risk_score + cumulative_risk * 0.1, 1.0)
        
        return min(risk_score, 1.0)
    
    def make_tradeoff(self, 
                      options: List[Dict],
                      weights: Dict[str, float] = None) -> Dict:
        """
        刘机独断：在多个选项中用最小作用量原则选择
        
        Args:
            options: 选项列表
                    [{"action": ..., "purpose_alignment": ..., "data_confidence": ..., "context": ...}]
            weights: 自定义权重 {"s_data": ..., "c_purpose": ..., "risk_w": ...}
        
        Returns:
            Dict: 最佳选项 + 评分详情
        """
        if not options:
            return {"error": "无选项可供选择"}
        
        if weights is None:
            weights = {}
        
        results = []
        for i, opt in enumerate(options):
            score = self.evaluate(
                action=opt.get("action", ""),
                context=opt.get("context", {}),
                purpose_alignment=opt.get("purpose_alignment", 0.5),
                data_confidence=opt.get("data_confidence", 0.5),
                lambda_coef=weights.get("lambda_coef", 0.7),
                mu_coef=weights.get("mu_coef", 0.3)
            )
            
            results.append({
                "index": i,
                "option": opt,
                "wisdom_score": score.to_dict()
            })
        
        # 按总得分排序
        results.sort(key=lambda x: x["wisdom_score"]["total_score"], reverse=True)
        
        best = results[0]
        return {
            "selected": best["option"],
            "index": best["index"],
            "wisdom_score": best["wisdom_score"],
            "all_scores": [r["wisdom_score"] for r in results],
            "ranking": [r["index"] for r in results]
        }
    
    def get_action_plan(self, 
                        goal: str,
                        constraints: Dict = None) -> Dict:
        """
        根据目标生成行动方案
        
        Args:
            goal: 目标描述
            constraints: 约束条件
        
        Returns:
            Dict: 行动方案
        """
        constraints = constraints or {}
        
        # 简化的行动方案生成
        plan = {
            "goal": goal,
            "steps": [],
            "total_score": 0.0,
            "risks": []
        }
        
        # 基于目标关键词生成步骤
        goal_lower = goal.lower()
        
        if "分析" in goal or "analyze" in goal_lower:
            plan["steps"].append({
                "action": "收集相关数据",
                "purpose_alignment": 0.9,
                "data_confidence": 0.5,
                "context": {"safety_critical": False}
            })
            plan["steps"].append({
                "action": "执行深度分析",
                "purpose_alignment": 0.85,
                "data_confidence": 0.7,
                "context": {"safety_critical": False}
            })
        
        if "创建" in goal or "build" in goal_lower:
            plan["steps"].append({
                "action": "设计架构方案",
                "purpose_alignment": 0.9,
                "data_confidence": 0.6,
                "context": {"safety_critical": False}
            })
            plan["steps"].append({
                "action": "实现核心代码",
                "purpose_alignment": 0.85,
                "data_confidence": 0.7,
                "context": {"high_value": True}
            })
            plan["risks"].append("代码实现可能需要修改")
        
        if "测试" in goal or "test" in goal_lower:
            plan["steps"].append({
                "action": "执行测试用例",
                "purpose_alignment": 0.9,
                "data_confidence": 0.8,
                "context": {"safety_critical": True}
            })
        
        # 评估行动方案
        for step in plan["steps"]:
            score = self.evaluate(
                action=step["action"],
                context=step["context"],
                purpose_alignment=step["purpose_alignment"],
                data_confidence=step["data_confidence"]
            )
            step["wisdom_score"] = score.to_dict()
            plan["total_score"] += score.total_score
        
        return plan
    
    def add_policy(self, 
                   name: str,
                   description: str,
                   risk_keywords: List[str],
                   risk_score: float,
                   mitigation: str) -> str:
        """
        添加风险策略
        
        Args:
            name: 策略名称
            description: 描述
            risk_keywords: 风险关键词列表
            risk_score: 基础风险分
            mitigation: 缓解措施
        
        Returns:
            str: 策略ID
        """
        self._policy_counter += 1
        policy_id = f"policy_{self._policy_counter}"
        
        policy = RiskPolicy(
            id=policy_id,
            name=name,
            description=description,
            risk_keywords=risk_keywords,
            risk_score=risk_score,
            mitigation=mitigation
        )
        
        self.risk_policies.append(policy)
        return policy_id
    
    def get_risk_mitigation(self, action: str) -> str:
        """获取行动的风险缓解建议"""
        action_lower = action.lower()
        
        for policy in self.risk_policies:
            if not policy.active:
                continue
            for keyword in policy.risk_keywords:
                if keyword.lower() in action_lower:
                    return policy.mitigation
        
        return "默认安全检查"
    
    def get_statistics(self) -> Dict:
        """获取智慧层统计信息"""
        recent = self.evaluation_history[-100:] if self.evaluation_history else []
        return {
            "total_evaluations": len(self.evaluation_history),
            "recent_avg_score": sum(h["score"]["total_score"] for h in recent) / max(len(recent), 1) if recent else 0,
            "recent_avg_risk": sum(h["score"]["risk_w"] for h in recent) / max(len(recent), 1) if recent else 0,
            "approve_rate": sum(1 for h in recent if h["score"]["should_proceed"]) / max(len(recent), 1) if recent else 0,
            "active_policies": len([p for p in self.risk_policies if p.active]),
            "value_weights": self.value_weights
        }
    
    def export_history(self, filepath: str):
        """导出评估历史"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.evaluation_history, f, ensure_ascii=False, indent=2)
    
    def __repr__(self) -> str:
        return f"DIKWPWisdomLayer(evaluations={len(self.evaluation_history)}, policies={len(self.risk_policies)})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块37：DIKWP智慧层（W层）测试")
    print("=" * 60)
    
    # 1. 创建智慧层实例
    wisdom_layer = DIKWPWisdomLayer()
    print(f"\n✓ 创建智慧层: {wisdom_layer}")
    
    # 2. 刘原理评估测试
    print(f"\n✓ 刘原理评估测试:")
    
    test_cases = [
        {
            "action": "读取用户文档",
            "context": {"safety_critical": False},
            "purpose_alignment": 0.9,
            "data_confidence": 0.95
        },
        {
            "action": "删除临时文件",
            "context": {"irreversible": True},
            "purpose_alignment": 0.7,
            "data_confidence": 0.8
        },
        {
            "action": "执行外部API调用",
            "context": {"external_impact": True, "high_value": True},
            "purpose_alignment": 0.85,
            "data_confidence": 0.6
        }
    ]
    
    for tc in test_cases:
        score = wisdom_layer.evaluate(
            action=tc["action"],
            context=tc["context"],
            purpose_alignment=tc["purpose_alignment"],
            data_confidence=tc["data_confidence"]
        )
        print(f"\n  行动: {tc['action']}")
        print(f"    S_data: {score.s_data:.2f}")
        print(f"    C(purpose): {score.c_purpose:.2f}")
        print(f"    Risk(W): {score.risk_w:.2f}")
        print(f"    总分 S = {score.total_score:.3f}")
        print(f"    决策: {score.decision}")
    
    # 3. 刘机独断 - 多选项权衡
    print(f"\n✓ 刘机独断测试（多选项权衡）:")
    
    options = [
        {
            "action": "方案A：保守实现",
            "purpose_alignment": 0.9,
            "data_confidence": 0.8,
            "context": {"safety_critical": False}
        },
        {
            "action": "方案B：激进优化",
            "purpose_alignment": 0.7,
            "data_confidence": 0.6,
            "context": {"high_value": True, "external_impact": True}
        },
        {
            "action": "方案C：渐进式改进",
            "purpose_alignment": 0.85,
            "data_confidence": 0.75,
            "context": {"safety_critical": True}
        }
    ]
    
    best = wisdom_layer.make_tradeoff(options)
    print(f"\n  选中方案: 方案{chr(65+best['index'])} ({best['selected']['action']})")
    print(f"  总分: {best['wisdom_score']['total_score']:.3f}")
    print(f"  决策: {best['wisdom_score']['decision']}")
    print(f"  排名: {' > '.join([chr(65+i) for i in best['ranking']])}")
    
    # 4. 行动方案生成
    print(f"\n✓ 行动方案生成:")
    plan = wisdom_layer.get_action_plan("分析太乙AGI架构并生成报告")
    print(f"  目标: {plan['goal']}")
    print(f"  步骤数: {len(plan['steps'])}")
    print(f"  总评分: {plan['total_score']:.2f}")
    for i, step in enumerate(plan["steps"]):
        print(f"    {i+1}. {step['action']}: S={step['wisdom_score']['total_score']:.2f}")
    
    # 5. 统计信息
    print(f"\n✓ 统计信息:")
    stats = wisdom_layer.get_statistics()
    print(f"  评估总数: {stats['total_evaluations']}")
    print(f"  审批率: {stats['approve_rate']:.1%}")
    print(f"  活跃策略: {stats['active_policies']}")
    
    print("\n" + "=" * 60)
    print("模块37测试完成 ✓")
    print("=" * 60)
