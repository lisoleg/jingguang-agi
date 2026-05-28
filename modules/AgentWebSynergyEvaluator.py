#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentWeb协同评估器 - 基于7G、AgentWeb与FPGA优先文档
AgentWeb三元共振定理：Φ-Γ-Ψ三元共振评估

核心定理：
1. AgentWeb三元共振定理：Φ-Γ-Ψ三者共振
2. 天地一体Agent协同定理：共振度正比于协同效率

基于IGCTR理论：
- Φ: 信息相位场（Token/消息）
- Γ: 几何构型空间（节点/链路/FPGA）
- Ψ: 意识场（Agent意图/人意图）
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class ResonanceState(Enum):
    """共振状态"""
    LOW = "low"           # 低共振
    MODERATE = "moderate" # 中等共振
    HIGH = "high"         # 高共振
    CRITICAL = "critical" # 临界共振


@dataclass
class AgentNode:
    """Agent节点"""
    agent_id: str
    domain: str              # 领域: 天基/空基/地基/具身
    compute_tflops: float    # 算力TFLOPS
    memory_gb: float         # 内存GB
    latency_ms: float       # 通信延迟ms
    intent_vector: np.ndarray  # 意图向量
    phi_field_strength: float  # Φ场强度
    resource_availability: float  # 资源可用性


@dataclass
class TriadicResonance:
    """三元共振状态"""
    phi_field_strength: float   # Φ场（信息流动）
    gamma_reconfigurability: float  # Γ场（资源可重构）
    psi_intent_alignment: float  # Ψ场（意图对齐）
    resonance_degree: float      # 共振度 (0-1)
    state: ResonanceState


@dataclass
class SynergyTask:
    """协同任务"""
    task_id: str
    description: str
    required_domains: List[str]
    urgency: float            # 紧急度 (0-1)
    complexity: float         # 复杂度 (0-1)
    participants: List[str]    # 参与的Agent ID


class AgentWebSynergyEvaluator:
    """
    AgentWeb协同评估器
    
    定理3.2.1（AgentWeb三元共振）:
    AgentWeb可运行Web5自主身份(DID)、自主数据(Data Vault)、
    自主价值(Token四元) 当且仅当 Φ-Γ-Ψ 共振
    
    定理4.1.1推论（天地一体Agent协同）:
    η_skyground ∝ ResonanceDegree(Ψ_agents) / Latency(comm)
    """
    
    # 权重配置
    PHI_WEIGHT = 0.4      # Φ场权重
    GAMMA_WEIGHT = 0.3    # Γ场权重
    PSI_WEIGHT = 0.3      # Ψ场权重
    
    # 共振阈值
    LOW_THRESHOLD = 0.3
    MODERATE_THRESHOLD = 0.6
    HIGH_THRESHOLD = 0.8
    
    def __init__(self):
        self.agents: Dict[str, AgentNode] = {}
        self.resonance_history: List[TriadicResonance] = []
        self.synergy_tasks: List[SynergyTask] = []
        self.domain_coupling: Dict[Tuple[str, str], float] = {}
        
    def register_agent(self, agent: AgentNode) -> bool:
        """
        注册Agent节点
        
        Args:
            agent: Agent节点
            
        Returns:
            是否成功
        """
        if agent.agent_id in self.agents:
            return False
            
        self.agents[agent.agent_id] = agent
        return True
        
    def evaluate_triadic_resonance(self, agent_ids: List[str]) -> TriadicResonance:
        """
        评估三元共振度
        
        Φ-Γ-Ψ三元共振评估
        
        Args:
            agent_ids: 参与评估的Agent列表
            
        Returns:
            三元共振状态
        """
        if not agent_ids:
            return TriadicResonance(0, 0, 0, 0, ResonanceState.LOW)
            
        # 提取参与Agent
        participating_agents = [self.agents[a] for a in agent_ids if a in self.agents]
        if not participating_agents:
            return TriadicResonance(0, 0, 0, 0, ResonanceState.LOW)
            
        # 计算Φ场强度（信息流动）
        phi_field = np.mean([a.phi_field_strength for a in participating_agents])
        
        # 计算Γ场（资源可重构性）
        # 可用性 + 算力/内存比
        resource_util = [a.resource_availability for a in participating_agents]
        compute_ratio = [a.compute_tflops / max(a.memory_gb, 1) for a in participating_agents]
        gamma_field = (np.mean(resource_util) + np.mean(compute_ratio) / 100) / 2
        
        # 计算Ψ场（意图对齐）
        intent_vectors = [a.intent_vector for a in participating_agents]
        if len(intent_vectors) > 1:
            # 计算意图向量余弦相似度
            psi_field = self._calculate_intent_alignment(intent_vectors)
        else:
            psi_field = 1.0
            
        # 综合共振度
        resonance_degree = (self.PHI_WEIGHT * phi_field + 
                          self.GAMMA_WEIGHT * gamma_field + 
                          self.PSI_WEIGHT * psi_field)
        
        # 确定共振状态
        if resonance_degree < self.LOW_THRESHOLD:
            state = ResonanceState.LOW
        elif resonance_degree < self.MODERATE_THRESHOLD:
            state = ResonanceState.MODERATE
        elif resonance_degree < self.HIGH_THRESHOLD:
            state = ResonanceState.HIGH
        else:
            state = ResonanceState.CRITICAL
            
        resonance = TriadicResonance(
            phi_field_strength=phi_field,
            gamma_reconfigurability=gamma_field,
            psi_intent_alignment=psi_field,
            resonance_degree=resonance_degree,
            state=state
        )
        
        self.resonance_history.append(resonance)
        return resonance
        
    def _calculate_intent_alignment(self, intent_vectors: List[np.ndarray]) -> float:
        """计算意图对齐度（余弦相似度平均）"""
        if len(intent_vectors) < 2:
            return 1.0
            
        n = len(intent_vectors)
        alignments = []
        
        for i in range(n):
            for j in range(i + 1, n):
                v1 = intent_vectors[i]
                v2 = intent_vectors[j]
                
                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)
                
                if norm1 > 0 and norm2 > 0:
                    cosine = np.dot(v1, v2) / (norm1 * norm2)
                    alignments.append(cosine)
                    
        return np.mean(alignments) if alignments else 0.0
        
    def evaluate_skyground_synergy(self, task: SynergyTask) -> Dict[str, Any]:
        """
        评估天地一体协同效率
        
        定理推论：η_skyground ∝ ResonanceDegree(Ψ_agents) / Latency(comm)
        
        Args:
            task: 协同任务
            
        Returns:
            协同效率评估
        """
        # 获取任务参与者
        participants = [self.agents[a] for a in task.participants if a in self.agents]
        if not participants:
            return {"status": "no_participants", "synergy_efficiency": 0.0}
            
        # 计算共振度
        resonance = self.evaluate_triadic_resonance(task.participants)
        
        # 计算平均通信延迟
        latencies = [p.latency_ms for p in participants]
        avg_latency = np.mean(latencies)
        
        # 天地域间耦合
        domains = set(p.domain for p in participants)
        cross_domain_score = len(domains) / 4  # 最多4个域
        
        # 计算协同效率
        # η ∝ (共振度 × 跨域分数) / (延迟/1000)
        latency_factor = avg_latency / 1000  # 归一化
        domain_factor = 1 + cross_domain_score
        
        synergy_efficiency = (resonance.resonance_degree * domain_factor) / max(latency_factor, 0.001)
        
        return {
            "task_id": task.task_id,
            "resonance_degree": resonance.resonance_degree,
            "resonance_state": resonance.state.value,
            "avg_latency_ms": avg_latency,
            "cross_domain_score": cross_domain_score,
            "synergy_efficiency": synergy_efficiency,
            "efficiency_category": self._categorize_efficiency(synergy_efficiency),
            "recommendation": self._generate_recommendation(resonance, task)
        }
        
    def _categorize_efficiency(self, efficiency: float) -> str:
        """效率分类"""
        if efficiency > 5.0:
            return "excellent"
        elif efficiency > 2.0:
            return "good"
        elif efficiency > 0.5:
            return "moderate"
        else:
            return "poor"
            
    def _generate_recommendation(self, resonance: TriadicResonance, 
                                 task: SynergyTask) -> str:
        """生成优化建议"""
        recommendations = []
        
        if resonance.phi_field_strength < 0.5:
            recommendations.append("提高信息场强度: 增加消息流动频率")
            
        if resonance.gamma_reconfigurability < 0.5:
            recommendations.append("提升资源可重构性: 启用FPGA动态配置")
            
        if resonance.psi_intent_alignment < 0.5:
            recommendations.append("对齐Agent意图: 使用统一意图协议")
            
        if task.urgency > 0.8 and resonance.state in [ResonanceState.LOW, ResonanceState.MODERATE]:
            recommendations.append("⚠️ 高优先级任务需提升共振度至HIGH+")
            
        return "; ".join(recommendations) if recommendations else "共振状态良好"
        
    def compute_web5_triadic_readiness(self) -> Dict[str, Any]:
        """
        评估Web5三元就绪度
        
        Web5三要素: DID(Φ-通证), Data(Γ-词元), Value(Ψ-智元)
        
        Returns:
            Web5就绪度评估
        """
        if not self.agents:
            return {"status": "no_agents", "readiness": 0.0}
            
        # Φ-DID就绪（信息场）
        phi_readiness = np.mean([a.phi_field_strength for a in self.agents.values()])
        
        # Γ-Data就绪（几何场）
        gamma_readiness = np.mean([a.resource_availability for a in self.agents.values()])
        
        # Ψ-Value就绪（意识场）
        psi_readiness = self._calculate_intent_alignment(
            [a.intent_vector for a in self.agents.values()]
        )
        
        # 综合就绪度
        overall_readiness = (phi_readiness * 0.3 + 
                            gamma_readiness * 0.35 + 
                            psi_readiness * 0.35)
        
        return {
            "phi_did_readiness": phi_readiness,
            "gamma_data_readiness": gamma_readiness,
            "psi_value_readiness": psi_readiness,
            "overall_readiness": overall_readiness,
            "status": "ready" if overall_readiness > 0.6 else "not_ready"
        }
        
    def get_diagnostic_report(self) -> Dict[str, Any]:
        """获取诊断报告"""
        recent_resonances = self.resonance_history[-10:] if self.resonance_history else []
        
        avg_resonance = np.mean([r.resonance_degree for r in recent_resonances]) if recent_resonances else 0
        avg_phi = np.mean([r.phi_field_strength for r in recent_resonances]) if recent_resonances else 0
        avg_gamma = np.mean([r.gamma_reconfigurability for r in recent_resonances]) if recent_resonances else 0
        avg_psi = np.mean([r.psi_intent_alignment for r in recent_resonances]) if recent_resonances else 0
        
        return {
            "title": "AgentWeb协同评估诊断报告",
            "theorem": "AgentWeb三元共振定理 (定理3.2.1)",
            "total_agents": len(self.agents),
            "active_tasks": len(self.synergy_tasks),
            "avg_resonance_degree": avg_resonance,
            "phi_field_avg": avg_phi,
            "gamma_field_avg": avg_gamma,
            "psi_field_avg": avg_psi,
            "resonance_trend": self._analyze_resonance_trend(),
            "web5_readiness": self.compute_web5_triadic_readiness(),
            "recommendation": "Φ-Γ-Ψ三元共振是AgentWeb的核心基础设施"
        }
        
    def _analyze_resonance_trend(self) -> str:
        """分析共振趋势"""
        if len(self.resonance_history) < 5:
            return "数据不足"
            
        recent = self.resonance_history[-5:]
        degrees = [r.resonance_degree for r in recent]
        
        slope = np.polyfit(range(len(degrees)), degrees, 1)[0]
        
        if slope > 0.05:
            return "上升趋势 📈"
        elif slope < -0.05:
            return "下降趋势 📉"
        else:
            return "稳定趋势 ➡️"


def demo():
    """演示AgentWeb协同评估器"""
    print("=" * 70)
    print("AgentWeb协同评估器 - 基于7G/AgentWeb文档")
    print("=" * 70)
    
    evaluator = AgentWebSynergyEvaluator()
    
    # 注册天地一体Agent
    agents = [
        AgentNode(
            agent_id="satellite_1",
            domain="天基",
            compute_tflops=100,
            memory_gb=256,
            latency_ms=50,
            intent_vector=np.array([0.8, 0.6, 0.9]),
            phi_field_strength=0.85,
            resource_availability=0.9
        ),
        AgentNode(
            agent_id="drone_1",
            domain="空基",
            compute_tflops=20,
            memory_gb=64,
            latency_ms=10,
            intent_vector=np.array([0.7, 0.8, 0.85]),
            phi_field_strength=0.75,
            resource_availability=0.8
        ),
        AgentNode(
            agent_id="ground_1",
            domain="地基",
            compute_tflops=200,
            memory_gb=512,
            latency_ms=5,
            intent_vector=np.array([0.9, 0.7, 0.8]),
            phi_field_strength=0.9,
            resource_availability=0.95
        ),
    ]
    
    for agent in agents:
        evaluator.register_agent(agent)
        
    # 评估三元共振
    resonance = evaluator.evaluate_triadic_resonance([a.agent_id for a in agents])
    print(f"\n🔮 三元共振评估:")
    print(f"   - Φ场强度: {resonance.phi_field_strength:.2%}")
    print(f"   - Γ场可重构性: {resonance.gamma_reconfigurability:.2%}")
    print(f"   - Ψ场意图对齐: {resonance.psi_intent_alignment:.2%}")
    print(f"   - 综合共振度: {resonance.resonance_degree:.2%}")
    print(f"   - 共振状态: {resonance.state.value}")
    
    # 评估协同任务
    task = SynergyTask(
        task_id="disaster_response",
        description="灾害应急通信",
        required_domains=["天基", "空基", "地基"],
        urgency=0.9,
        complexity=0.7,
        participants=["satellite_1", "drone_1", "ground_1"]
    )
    
    synergy = evaluator.evaluate_skyground_synergy(task)
    print(f"\n🚀 天地协同效率:")
    print(f"   - 任务: {synergy['task_id']}")
    print(f"   - 协同效率: {synergy['synergy_efficiency']:.2f}")
    print(f"   - 分类: {synergy['efficiency_category']}")
    
    # Web5就绪度
    web5 = evaluator.compute_web5_triadic_readiness()
    print(f"\n🌐 Web5就绪度:")
    print(f"   - Φ-DID就绪: {web5['phi_did_readiness']:.2%}")
    print(f"   - Γ-Data就绪: {web5['gamma_data_readiness']:.2%}")
    print(f"   - Ψ-Value就绪: {web5['psi_value_readiness']:.2%}")
    print(f"   - 综合就绪度: {web5['overall_readiness']:.2%}")
    
    return evaluator


if __name__ == "__main__":
    demo()
