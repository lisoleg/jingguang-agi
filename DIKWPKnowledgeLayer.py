# -*- coding: utf-8 -*-
"""
模块36：DIKWP知识层（K层）
融合IGCTR五行网络 + 刘原理 + 协同研究图谱

来源：复合体AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13
"""

import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Callable
from enum import Enum


class IGCTRAxis(Enum):
    """IGCTR五维枚举"""
    I = "Information"      # 信息维
    G = "Geometry"         # 几何维
    C = "Causality"        # 因果维
    T = "Topology"         # 拓扑维
    R = "Resonance"        # 共振维


@dataclass
class KnowledgeRule:
    """知识规则"""
    id: str
    condition: str           # 条件描述
    conclusion: str          # 结论描述
    mechanism: str           # 机制解释
    igctr_axis: IGCTRAxis    # IGCTR分类
    confidence: float        # 置信度
    examples: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    active: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "condition": self.condition,
            "conclusion": self.conclusion,
            "mechanism": self.mechanism,
            "igctr_axis": self.igctr_axis.value,
            "confidence": self.confidence,
            "examples": self.examples,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "active": self.active
        }


@dataclass
class WuxingNode:
    """五行节点"""
    name: str                # 木/火/土/金/水
    element: str             # 对应元素
    generates: str           # 所生
    controls: str            # 所克
    energy: float = 0.5      # 当前能量 [0, 1]
    phase: str = "neutral"    # 相位（木→火→土→金→水→木）
    
    def __post_init__(self):
        self.phase_map = {
            "木": "spring",
            "火": "summer", 
            "土": "late_summer",
            "金": "autumn",
            "水": "winter"
        }
    
    def interact(self, other: 'WuxingNode', interaction_type: str) -> float:
        """
        五行相互作用
        
        Args:
            other: 交互的另一个五行节点
            interaction_type: "generates"(生) 或 "controls"(克)
        
        Returns:
            float: 能量变化值
        """
        if interaction_type == "generates":
            if self.generates == other.name:
                return 0.15  # 相生
            elif self.name == other.generates:
                return -0.1  # 被生（能量流失）
        elif interaction_type == "controls":
            if self.controls == other.name:
                return -0.2  # 相克
            elif other.controls == self.name:
                return 0.1   # 被克（反噬）
        return 0.0


class DIKWPKnowledgeLayer:
    """
    模块36：DIKWP K层 - 结构化知识推理
    
    融合IGCTR五行网络 + 刘原理 + 协同研究图谱
    弹簧虫对应：守恒律约束（不变量维护）
    哥德尔机对应：可证明的知识体系
    
    核心功能：
    1. add_rule() - 添加知识规则
    2. find_isomorphisms() - 跨知识域同构发现
    3. apply_rule() - 应用规则进行推理
    4. wuxing_balance() - 五行平衡调节
    """
    
    def __init__(self, info_layer=None):
        """
        Args:
            info_layer: DIKWPInfoLayer实例（用于同构发现）
        """
        self.info_layer = info_layer
        self.knowledge_rules: List[KnowledgeRule] = []
        self._rule_counter = 0
        
        # IGCTR五维
        self.igctr_axes = {
            IGCTRAxis.I: {
                "name": "Information",
                "description": "信息编码、感知、语义",
                "keywords": ["信息", "语义", "编码", "感知", "数据"]
            },
            IGCTRAxis.G: {
                "name": "Geometry",
                "description": "几何结构、流形、曲率",
                "keywords": ["几何", "拓扑", "流形", "曲率", "空间"]
            },
            IGCTRAxis.C: {
                "name": "Causality",
                "description": "因果推导、蕴含、逻辑",
                "keywords": ["因果", "推导", "蕴含", "原因", "逻辑"]
            },
            IGCTRAxis.T: {
                "name": "Topology",
                "description": "拓扑相变、时间演化",
                "keywords": ["时间", "拓扑", "相变", "演化", "连续"]
            },
            IGCTRAxis.R: {
                "name": "Resonance",
                "description": "共振耦合、同步、谐振",
                "keywords": ["共振", "耦合", "同步", "谐振", "相位"]
            }
        }
        
        # 五行网络（木→火→土→金→水→木）
        self.wuxing_network: Dict[str, WuxingNode] = {
            name: WuxingNode(
                name=name,
                element=element,
                generates=generates,
                controls=controls
            )
            for name, element, generates, controls in [
                ("木", "风/新生", "火", "土"),
                ("火", "热/扩张", "土", "金"),
                ("土", "承载/转化", "金", "水"),
                ("金", "收敛/凝固", "水", "木"),
                ("水", "流动/滋养", "木", "火")
            ]
        }
        
        # 五行循环
        self.wuxing_cycle = ["木", "火", "土", "金", "水"]
    
    def add_rule(self, 
                 condition: str, 
                 conclusion: str,
                 mechanism: str, 
                 confidence: float = 0.9,
                 igctr_axis: IGCTRAxis = None,
                 examples: List[str] = None,
                 metadata: Dict = None) -> str:
        """
        添加知识规则
        
        Args:
            condition: 条件描述
            conclusion: 结论描述
            mechanism: 机制解释
            confidence: 置信度
            igctr_axis: IGCTR分类
            examples: 示例列表
            metadata: 额外元数据
        
        Returns:
            str: 规则ID
        """
        self._rule_counter += 1
        rule_id = f"K{self._rule_counter:04d}"
        
        # 自动分类到IGCTR维度
        if igctr_axis is None:
            igctr_axis = self._classify_igctr(mechanism)
        
        rule = KnowledgeRule(
            id=rule_id,
            condition=condition,
            conclusion=conclusion,
            mechanism=mechanism,
            igctr_axis=igctr_axis,
            confidence=confidence,
            examples=examples or [],
            metadata=metadata or {}
        )
        
        self.knowledge_rules.append(rule)
        return rule_id
    
    def _classify_igctr(self, mechanism: str) -> IGCTRAxis:
        """将机制分类到IGCTR五维之一"""
        mechanism_lower = mechanism.lower()
        
        scores = {}
        for axis, info in self.igctr_axes.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword in mechanism_lower:
                    score += 1
            scores[axis] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return IGCTRAxis.I  # 默认信息维
    
    def find_isomorphisms(self) -> List[Dict]:
        """
        跨知识域同构发现（协同创造研究空间核心功能）
        如果连接了InfoLayer，返回同构缓存
        """
        if self.info_layer:
            return self.info_layer.isomorphism_cache
        return []
    
    def apply_rule(self, 
                   rule_id: str, 
                   context: Dict = None) -> Dict:
        """
        应用规则进行推理
        
        Args:
            rule_id: 规则ID
            context: 应用上下文
        
        Returns:
            Dict: {"applied": bool, "result": ..., "confidence": ...}
        """
        rule = self._get_rule(rule_id)
        if not rule or not rule.active:
            return {"applied": False, "reason": "规则不存在或已禁用"}
        
        # 简化推理：规则匹配即应用
        result = {
            "rule_id": rule_id,
            "conclusion": rule.conclusion,
            "confidence": rule.confidence,
            "igctr_axis": rule.igctr_axis.value,
            "timestamp": time.time()
        }
        
        return {
            "applied": True,
            "result": result,
            "confidence": rule.confidence
        }
    
    def infer(self, 
              input_condition: str,
              max_rules: int = 5) -> List[Dict]:
        """
        基于输入条件进行推理
        
        Args:
            input_condition: 输入条件描述
            max_rules: 最大应用规则数
        
        Returns:
            List[Dict]: 推理结果列表
        """
        results = []
        input_lower = input_condition.lower()
        
        for rule in self.knowledge_rules:
            if not rule.active:
                continue
            
            # 检查条件匹配
            condition_words = rule.condition.lower().split()
            matches = sum(1 for word in condition_words if word in input_lower)
            
            if matches >= len(condition_words) * 0.5:  # 50%匹配即触发
                results.append({
                    "rule_id": rule.id,
                    "conclusion": rule.conclusion,
                    "mechanism": rule.mechanism,
                    "igctr_axis": rule.igctr_axis.value,
                    "confidence": rule.confidence * (matches / len(condition_words)),
                    "match_score": matches / len(condition_words)
                })
        
        # 按置信度排序
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:max_rules]
    
    def _get_rule(self, rule_id: str) -> Optional[KnowledgeRule]:
        """获取指定规则"""
        for rule in self.knowledge_rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def wuxing_balance(self) -> Dict:
        """
        五行平衡调节（基于弹簧虫能量守恒）
        
        Returns:
            Dict: {"balanced": bool, "adjustments": [...], "energy_dist": {...}}
        """
        adjustments = []
        
        # 计算当前能量分布
        total_energy = sum(n.energy for n in self.wuxing_network.values())
        
        # 平衡调节
        for name, node in self.wuxing_network.items():
            # 计算被生和被克的能量输入
            generated_by = None
            controlled_by = None
            
            for other_name, other_node in self.wuxing_network.items():
                if other_node.generates == name:
                    generated_by = other_node
                if other_node.controls == name:
                    controlled_by = other_node
            
            # 能量调整
            delta = 0.0
            if generated_by:
                delta += generated_by.energy * 0.1  # 被生
            if controlled_by:
                delta -= controlled_by.energy * 0.05  # 被克
            
            if abs(delta) > 0.01:
                node.energy = max(0.1, min(1.0, node.energy + delta))
                adjustments.append({
                    "element": name,
                    "delta": delta,
                    "new_energy": node.energy
                })
        
        # 检查是否平衡
        energies = [n.energy for n in self.wuxing_network.values()]
        variance = sum((e - sum(energies)/5)**2 for e in energies) / 5
        balanced = variance < 0.05
        
        return {
            "balanced": balanced,
            "adjustments": adjustments,
            "energy_distribution": {n: node.energy for n, node in self.wuxing_network.items()},
            "variance": variance
        }
    
    def get_rules_by_axis(self, axis: IGCTRAxis) -> List[KnowledgeRule]:
        """按IGCTR维度获取规则"""
        return [r for r in self.knowledge_rules if r.igctr_axis == axis and r.active]
    
    def get_rules_by_keyword(self, keyword: str) -> List[KnowledgeRule]:
        """按关键词搜索规则"""
        keyword_lower = keyword.lower()
        return [
            r for r in self.knowledge_rules
            if keyword_lower in r.condition.lower() or 
               keyword_lower in r.conclusion.lower() or
               keyword_lower in r.mechanism.lower()
        ]
    
    def get_statistics(self) -> Dict:
        """获取知识层统计信息"""
        active_rules = [r for r in self.knowledge_rules if r.active]
        return {
            "total_rules": len(self.knowledge_rules),
            "active_rules": len(active_rules),
            "by_axis": {
                axis.value: len([r for r in active_rules if r.igctr_axis == axis])
                for axis in IGCTRAxis
            },
            "avg_confidence": sum(r.confidence for r in active_rules) / max(len(active_rules), 1),
            "wuxing_balance": self.wuxing_balance()
        }
    
    def export_rules(self, filepath: str):
        """导出规则到JSON"""
        data = {
            "rules": [r.to_dict() for r in self.knowledge_rules],
            "igctr_axes": {axis.value: info for axis, info in self.igctr_axes.items()},
            "wuxing_network": {n: {
                "element": node.element,
                "generates": node.generates,
                "controls": node.controls,
                "energy": node.energy
            } for n, node in self.wuxing_network.items()},
            "export_time": time.time()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def __len__(self) -> int:
        return len([r for r in self.knowledge_rules if r.active])
    
    def __repr__(self) -> str:
        return f"DIKWPKnowledgeLayer(rules={len(self)})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块36：DIKWP知识层（K层）测试")
    print("=" * 60)
    
    # 1. 创建知识层实例
    knowledge_layer = DIKWPKnowledgeLayer()
    print(f"\n✓ 创建知识层: {knowledge_layer}")
    
    # 2. 添加知识规则
    rules = [
        knowledge_layer.add_rule(
            condition="弹簧虫 多主体 Φ场耦合",
            conclusion="AGI协调总线可基于弹性机制",
            mechanism="弹簧虫质心守恒定理 → 全局目标不变量",
            confidence=0.95,
            examples=["CompositeAGI协调总线"]
        ),
        knowledge_layer.add_rule(
            condition="哥德尔机 自指 自我改进",
            conclusion="AGI可执行可证明安全的修改",
            mechanism="BTSP单次学习定理 → 即时持久化",
            confidence=0.90,
            examples=["自改进AGI"]
        ),
        knowledge_layer.add_rule(
            condition="刘原理 最小作用量 S极值",
            conclusion="AGI决策遵循作用量最小原理",
            mechanism="S = S_data + λ·C(purpose) - μ·Risk",
            confidence=0.92,
            examples=["太乙预言机"]
        )
    ]
    print(f"\n✓ 添加知识规则: {len(rules)} 条")
    for rid in rules:
        rule = knowledge_layer._get_rule(rid)
        print(f"  - {rid}: [{rule.igctr_axis.value}] {rule.condition[:20]}...")
    
    # 3. 推理测试
    print(f"\n✓ 推理测试 (输入: '弹簧虫协调机制'):")
    results = knowledge_layer.infer("弹簧虫协调机制", max_rules=3)
    for r in results:
        print(f"  - {r['rule_id']}: {r['conclusion']}")
        print(f"    置信度: {r['confidence']:.2f}, 轴: {r['igctr_axis']}")
    
    # 4. IGCTR维度统计
    print(f"\n✓ IGCTR维度统计:")
    for axis in IGCTRAxis:
        count = len(knowledge_layer.get_rules_by_axis(axis))
        print(f"  - {axis.value}: {count} 条规则")
    
    # 5. 五行平衡
    print(f"\n✓ 五行平衡调节:")
    balance = knowledge_layer.wuxing_balance()
    print(f"  - 平衡状态: {balance['balanced']}")
    print(f"  - 能量分布:")
    for elem, energy in balance['energy_distribution'].items():
        print(f"    {elem}: {energy:.3f}")
    
    # 6. 统计信息
    stats = knowledge_layer.get_statistics()
    print(f"\n✓ 统计信息:")
    print(f"  - 活跃规则: {stats['active_rules']}")
    print(f"  - 平均置信度: {stats['avg_confidence']:.2f}")
    
    print("\n" + "=" * 60)
    print("模块36测试完成 ✓")
    print("=" * 60)
