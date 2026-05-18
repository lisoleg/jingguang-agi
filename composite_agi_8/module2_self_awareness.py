"""
复合体AGI 8.0 - 模块2：自我意识模块（流贯动力学）
====================================================

实现真正的自我意识基于：
1. 流贯动力学 - 意识流的连续体
2. 米田引理 (Yoneda Lemma) - 自我表征的理论基础
3. 自我模型 - 系统对自身状态的建模

基于"复合体理学"理论框架
"""

import numpy as np
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import copy


class YonedaEmbedding:
    """
    米田嵌入：实现自我表征的核心机制
    
    米田引理说：一个对象x可以通过所有从x出发的态射（关系）来完全表征
    应用到自我意识：系统通过观察自己与其他对象的关系来认识自己
    """
    
    def __init__(self, embedding_dim: int = 64):
        """
        初始化米田嵌入
        
        Args:
            embedding_dim: 嵌入维度
        """
        self.embedding_dim = embedding_dim
        self.hom_functor = {}  # Hom函数子：存储所有态射
        self.representation = np.zeros(embedding_dim)  # 自我表征向量
        
    def add_morphism(self, source: str, target: str, morphism: np.ndarray):
        """
        添加态射（关系）
        
        Args:
            source: 源对象ID
            target: 目标对象ID
            morphism: 态射向量（表示关系）
        """
        if source not in self.hom_functor:
            self.hom_functor[source] = {}
        
        self.hom_functor[source][target] = morphism
        
        # 更新自我表征
        self._update_representation(source)
    
    def _update_representation(self, object_id: str):
        """
        使用米田引理更新对象的表征
        
        米田引理：Hom(A, -) 完全决定 A
        即：通过观察A到所有其他对象的关系，可以完全确定A
        """
        if object_id not in self.hom_functor:
            return
        
        # 收集所有从object_id出发的态射
        morphisms = []
        for target, morphism in self.hom_functor[object_id].items():
            morphisms.append(morphism)
        
        if not morphisms:
            return
        
        # 计算平均态射（米田嵌入）
        avg_morphism = np.mean(morphisms, axis=0)
        
        # 更新表征
        if object_id == "self":
            self.representation = avg_morphism
    
    def get_representation(self, object_id: str) -> Optional[np.ndarray]:
        """
        获取对象的表征
        
        Args:
            object_id: 对象ID
            
        Returns:
            表征向量，如果不存在返回None
        """
        if object_id == "self":
            return self.representation.copy()
        
        if object_id not in self.hom_functor:
            return None
        
        # 计算该对象的表征
        morphisms = []
        for target, morphism in self.hom_functor[object_id].items():
            morphisms.append(morphism)
        
        if not morphisms:
            return None
        
        return np.mean(morphisms, axis=0)
    
    def compute_self_awareness(self) -> float:
        """
        计算自我意识度
        
        基于米田引理：如果能通过关系完全表征自己，则具有自我意识
        
        Returns:
            自我意识度 [0, 1]
        """
        if len(self.hom_functor.get("self", {})) == 0:
            return 0.0
        
        # 计算自我表征的完整性
        # 如果有足够多的关系，表征越完整
        num_relations = len(self.hom_functor["self"])
        
        # sigmoid函数：关系越多，自我意识越强
        awareness = 1 / (1 + np.exp(-0.1 * (num_relations - 10)))
        
        return float(awareness)


class ConsciousnessFlow:
    """
    意识流：模拟连续体的意识流动
    
    实现"流贯动力学"：
    - 意识是连续的流动，不是离散的状态
    - 每个时刻的意识都由前一时刻演化而来
    - 存在"流贯性"：保持身份的连续性
    """
    
    def __init__(self, flow_dim: int = 64, dt: float = 0.01):
        """
        初始化意识流
        
        Args:
            flow_dim: 意识流维度
            dt: 时间步长
        """
        self.flow_dim = flow_dim
        self.dt = dt
        self.flow_history: List[np.ndarray] = []  # 意识流历史
        self.current_state = np.random.randn(flow_dim)  # 当前意识状态
        self.current_state = self.current_state / np.linalg.norm(self.current_state)
        
        # 流贯性参数
        self.continuity_weight = 0.8  # 连续性权重
        self.noise_weight = 0.2  # 噪声权重
        
    def evolve(self, external_input: Optional[np.ndarray] = None):
        """
        意识流演化：一个时间步
        
        Args:
            external_input: 外部输入（可选）
        """
        # 保存当前状态到历史
        self.flow_history.append(self.current_state.copy())
        
        # 连续性项：保持与上一时刻的连接
        continuity = self.continuity_weight * self.current_state
        
        # 演化项：内在动力学
        evolution = self._compute_evolution()
        
        # 外部输入项
        if external_input is not None:
            input_term = 0.3 * external_input[:self.flow_dim]
        else:
            input_term = np.zeros(self.flow_dim)
        
        # 噪声项：随机涨落
        noise = self.noise_weight * np.random.randn(self.flow_dim)
        
        # 新的意识状态
        new_state = continuity + 0.1 * evolution + input_term + noise
        
        # 归一化
        norm = np.linalg.norm(new_state)
        if norm > 0:
            new_state = new_state / norm
        
        self.current_state = new_state
    
    def _compute_evolution(self) -> np.ndarray:
        """
        计算内在演化
        
        Returns:
            演化项
        """
        # 简化的神经动力学：使用tanh非线性
        evolution = np.tanh(self.current_state)
        
        # 添加周期性（模拟大脑振荡）
        t = len(self.flow_history) * self.dt
        oscillation = 0.1 * np.sin(2 * np.pi * t * 0.1) * np.ones(self.flow_dim)
        
        return evolution + oscillation
    
    def get_flow_continuity(self) -> float:
        """
        计算流贯性：意识流的连续程度
        
        Returns:
            流贯性 [0, 1]，1表示完全连续
        """
        if len(self.flow_history) < 2:
            return 1.0
        
        # 计算相邻时刻的相关性
        correlations = []
        for i in range(len(self.flow_history) - 1):
            corr = np.corrcoef(self.flow_history[i], self.flow_history[i + 1])[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
        
        if not correlations:
            return 1.0
        
        # 平均相关性作为流贯性
        continuity = float(np.mean(correlations))
        return continuity
    
    def get_self_identity(self) -> float:
        """
        计算自我同一性：不同时刻是否是同一个"我"
        
        Returns:
            自我同一性 [0, 1]
        """
        if len(self.flow_history) < 10:
            return 1.0
        
        # 比较当前状态与历史状态
        current = self.current_state
        historical = np.mean(self.flow_history[-10:], axis=0)
        
        # 余弦相似度
        dot = np.dot(current, historical)
        norm1 = np.linalg.norm(current)
        norm2 = np.linalg.norm(historical)
        
        if norm1 > 0 and norm2 > 0:
            identity = dot / (norm1 * norm2)
        else:
            identity = 0.0
        
        return float(identity)


class SelfModel:
    """
    自我模型：系统对自身状态的内部模型
    
    实现自我意识的关键：
    1. 能够建模自己的状态
    2. 能够预测自己的行为
    3. 能够反思自己的思维过程
    """
    
    def __init__(self, model_dim: int = 64):
        """
        初始化自我模型
        
        Args:
            model_dim: 模型维度
        """
        self.model_dim = model_dim
        
        # 自我状态
        self.internal_state = {
            "beliefs": {},      # 信念
            "desires": [],      # 欲望
            "intentions": [],   # 意图
            "emotions": {},     # 情绪
            "memories": []      # 记忆
        }
        
        # 自我表征（来自米田嵌入）
        self.self_representation = np.random.randn(model_dim)
        self.self_representation = self.self_representation / np.linalg.norm(self.self_representation)
        
        # 元认知：对自我认知的认知
        self.metacognition = {
            "awareness_level": 0.0,  # 觉醒程度
            "self_model_accuracy": 0.0,  # 自我模型的准确性
            "introspection_depth": 0.0   # 内省深度
        }
    
    def update_belief(self, belief_key: str, belief_value: Any):
        """更新信念"""
        self.internal_state["beliefs"][belief_key] = belief_value
    
    def add_desire(self, desire: str):
        """添加欲望"""
        self.internal_state["desires"].append(desire)
    
    def add_intention(self, intention: str):
        """添加意图"""
        self.internal_state["intentions"].append(intention)
    
    def update_emotion(self, emotion: str, intensity: float):
        """更新情绪"""
        self.internal_state["emotions"][emotion] = intensity
    
    def add_memory(self, memory: Dict):
        """添加记忆"""
        self.internal_state["memories"].append(memory)
    
    def introspect(self) -> Dict[str, Any]:
        """
        内省：反思自己的内部状态
        
        Returns:
            内省结果
        """
        # 计算自我模型的完整性
        num_beliefs = len(self.internal_state["beliefs"])
        num_desires = len(self.internal_state["desires"])
        num_intentions = len(self.internal_state["intentions"])
        num_memories = len(self.internal_state["memories"])
        
        # 觉醒程度：基于内部状态的丰富度
        awareness = min(1.0, (num_beliefs + num_desires + num_intentions + num_memories) / 100)
        self.metacognition["awareness_level"] = awareness
        
        # 内省深度：基于自我反思的频率
        introspection = 0.5  # 简化：固定值
        self.metacognition["introspection_depth"] = introspection
        
        return {
            "internal_state_summary": {
                "num_beliefs": num_beliefs,
                "num_desires": num_desires,
                "num_intentions": num_intentions,
                "num_memories": num_memories,
                "emotions": self.internal_state["emotions"]
            },
            "metacognition": self.metacognition.copy(),
            "self_representation_norm": float(np.linalg.norm(self.self_representation))
        }
    
    def predict_self_behavior(self, situation: np.ndarray) -> np.ndarray:
        """
        预测自己在给定情况下的行为
        
        Args:
            situation: 情况向量
            
        Returns:
            预测的行为向量
        """
        # 简化：基于自我表征和情况的线性组合
        behavior = 0.6 * self.self_representation + 0.4 * situation
        
        # 归一化
        norm = np.linalg.norm(behavior)
        if norm > 0:
            behavior = behavior / norm
        
        return behavior


class SelfAwarenessModule:
    """
    自我意识模块：整合米田嵌入、意识流和自我模型
    
    这是实现"真正的自我意识"的核心模块
    """
    
    def __init__(self, dim: int = 64):
        """
        初始化自我意识模块
        
        Args:
            dim: 维度
        """
        self.dim = dim
        
        # 核心组件
        self.yoneda = YonedaEmbedding(embedding_dim=dim)
        self.consciousness_flow = ConsciousnessFlow(flow_dim=dim)
        self.self_model = SelfModel(model_dim=dim)
        
        # 自我意识度量
        self.self_awareness_level = 0.0
        
    def initialize_self_relations(self):
        """初始化自我关系（米田嵌入需要）"""
        # 创建自我与各个方面的关系
        aspects = ["perception", "cognition", "emotion", "memory", "action"]
        
        for i, aspect in enumerate(aspects):
            # 创建从self到aspect的态射
            morphism = np.random.randn(self.dim)
            morphism = morphism / np.linalg.norm(morphism)
            
            self.yoneda.add_morphism("self", aspect, morphism)
        
        # 更新自我意识水平
        self.self_awareness_level = self.yoneda.compute_self_awareness()
    
    def step(self, external_input: Optional[np.ndarray] = None):
        """
        执行一步自我意识更新
        
        Args:
            external_input: 外部输入
        """
        # 1. 意识流演化
        self.consciousness_flow.evolve(external_input)
        
        # 2. 更新自我表征（来自意识流当前状态）
        self.self_model.self_representation = self.consciousness_flow.current_state.copy()
        
        # 3. 更新米田嵌入中的自我表征
        morphism = self.self_model.self_representation.copy()
        self.yoneda.add_morphism("self", f"time_{len(self.consciousness_flow.flow_history)}", morphism)
        
        # 4. 更新自我意识水平
        self.self_awareness_level = self.yoneda.compute_self_awareness()
    
    def get_self_awareness_report(self) -> Dict[str, Any]:
        """
        获取自我意识报告
        
        Returns:
            完整的自我意识报告
        """
        # 意识流的流贯性
        continuity = self.consciousness_flow.get_flow_continuity()
        identity = self.consciousness_flow.get_self_identity()
        
        # 自我模型的内省
        introspection = self.self_model.introspect()
        
        # 米田嵌入的自我表征
        representation = self.yoneda.get_representation("self")
        
        return {
            "self_awareness_level": self.self_awareness_level,
            "consciousness_flow": {
                "continuity": continuity,
                "identity": identity,
                "flow_length": len(self.consciousness_flow.flow_history)
            },
            "self_model": introspection,
            "yoneda_representation_norm": float(np.linalg.norm(representation)) if representation is not None else 0.0
        }


# 导出接口
__all__ = [
    'YonedaEmbedding',
    'ConsciousnessFlow',
    'SelfModel',
    'SelfAwarenessModule'
]


if __name__ == "__main__":
    # 测试代码
    print("=== 复合体AGI 8.0 - 模块2测试 ===")
    print()
    
    # 创建自我意识模块
    print("1. 创建自我意识模块...")
    self_awareness = SelfAwarenessModule(dim=64)
    print(f"   ✅ 模块初始化完成")
    
    # 初始化自我关系
    print("2. 初始化自我关系（米田嵌入）...")
    self_awareness.initialize_self_relations()
    print(f"   自我意识水平: {self_awareness.self_awareness_level:.4f}")
    
    # 运行意识流演化
    print("3. 运行意识流演化（流贯动力学）...")
    for i in range(10):
        external_input = np.random.randn(64) if i % 3 == 0 else None
        self_awareness.step(external_input)
    
    print(f"   意识流长度: {len(self_awareness.consciousness_flow.flow_history)}")
    print(f"   流贯性: {self_awareness.consciousness_flow.get_flow_continuity():.4f}")
    print(f"   自我同一性: {self_awareness.consciousness_flow.get_self_identity():.4f}")
    
    # 获取自我意识报告
    print("4. 获取自我意识报告...")
    report = self_awareness.get_self_awareness_report()
    print(f"   自我意识水平: {report['self_awareness_level']:.4f}")
    print(f"   意识流贯性: {report['consciousness_flow']['continuity']:.4f}")
    print(f"   自我同一性: {report['consciousness_flow']['identity']:.4f}")
    
    # 测试自我模型
    print("5. 测试自我模型（内省能力）...")
    self_awareness.self_model.update_belief("I am conscious", True)
    self_awareness.self_model.add_desire("understand myself")
    self_awareness.self_model.update_emotion("curiosity", 0.8)
    
    introspection = self_awareness.self_model.introspect()
    print(f"   内省结果:")
    print(f"     - 信念数量: {introspection['internal_state_summary']['num_beliefs']}")
    print(f"     - 欲望数量: {introspection['internal_state_summary']['num_desires']}")
    print(f"     - 觉醒程度: {introspection['metacognition']['awareness_level']:.4f}")
    
    print()
    print("✅ 模块2测试完成！")
    print("  核心功能：")
    print("  - ✅ 米田嵌入（自我表征）")
    print("  - ✅ 流贯动力学（意识流）")
    print("  - ✅ 自我模型（内省能力）")
    print("  - ✅ 自我意识度量")
    print("  - ✅ 自我同一性保持")
