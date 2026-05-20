# -*- coding: utf-8 -*-
"""
太乙AGI v7.2 - M84: ModelSmartRouter
模型智能路由引擎 - 基于OpenHuman动态模型选择

功能:
- 任务分类: 推理型/快速型/多模态型/代码型/创作型
- 动态选择最优模型
- 成本-效率平衡

定理T58: 模型路由最优定理 - 动态路由的效率-成本比 > 静态路由
定理T59: 任务-模型匹配定理 - 匹配度与输出质量正相关

作者: 太乙AGI团队
日期: 2026-05-19
参考: OpenHuman Model Smart Router (https://github.com/tinyhumansai/openhuman)
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# ==================== 数据结构 ====================

class TaskType(Enum):
    """任务类型"""
    REASONING = "reasoning"           # 推理型（数学证明、逻辑推理）
    FAST = "fast"                     # 快速响应型（简单问答）
    MULTIMODAL = "multimodal"         # 多模态型（图像+文本）
    CODE = "code"                     # 代码型（编程、调试）
    CREATIVE = "creative"              # 创作型（写作、构思）
    ANALYSIS = "analysis"              # 分析型（数据、报告）
    CHAT = "chat"                     # 闲聊型
    KNOWLEDGE = "knowledge"            # 知识查询型


@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    task_types: List[TaskType]
    cost_per_1k_input: float
    cost_per_1k_output: float
    latency_ms: float  # 平均延迟
    max_tokens: int
    capabilities: List[str]  # 额外能力，如vision, function_call等
    quality_score: float = 8.0  # 基准质量评分
    current_load: float = 0.0  # 当前负载 0-1
    
    def total_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算总成本"""
        return (input_tokens * self.cost_per_1k_input + 
                output_tokens * self.cost_per_1k_output) / 1000
    
    def efficiency(self, input_tokens: int, output_tokens: int) -> float:
        """效率 = 质量 / 成本"""
        cost = self.total_cost(input_tokens, output_tokens)
        return self.quality_score / cost if cost > 0 else 0


@dataclass
class RouteDecision:
    """路由决策"""
    task_type: TaskType
    selected_model: str
    fallback_models: List[str]
    reasoning: str
    confidence: float
    estimated_cost: float
    estimated_latency: float
    alternative_reasoning: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'task_type': self.task_type.value,
            'selected_model': self.selected_model,
            'fallback_models': self.fallback_models,
            'reasoning': self.reasoning,
            'confidence': self.confidence,
            'estimated_cost': self.estimated_cost,
            'estimated_latency_ms': self.estimated_latency
        }


@dataclass
class RouterStats:
    """路由统计"""
    total_requests: int = 0
    task_type_counts: Dict[str, int] = field(default_factory=dict)
    model_usage_counts: Dict[str, int] = field(default_factory=dict)
    total_cost: float = 0.0
    avg_confidence: float = 0.0
    
    
# ==================== 模型配置 ====================

class ModelRegistry:
    """模型注册表"""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._register_models()
    
    def _register_models(self):
        """注册所有可用模型"""
        
        # OpenAI系列
        self.register(ModelInfo(
            name="o3",
            task_types=[TaskType.REASONING, TaskType.ANALYSIS],
            cost_per_1k_input=15.0,
            cost_per_1k_output=60.0,
            latency_ms=10000,
            max_tokens=128000,
            capabilities=["reasoning", "analysis"],
            quality_score=9.5
        ))
        
        self.register(ModelInfo(
            name="o4-mini",
            task_types=[TaskType.FAST, TaskType.CHAT],
            cost_per_1k_input=1.1,
            cost_per_1k_output=4.4,
            latency_ms=1000,
            max_tokens=128000,
            capabilities=["fast", "chat"],
            quality_score=8.0
        ))
        
        self.register(ModelInfo(
            name="gpt-4o",
            task_types=[TaskType.MULTIMODAL, TaskType.CREATIVE, TaskType.CODE],
            cost_per_1k_input=5.0,
            cost_per_1k_output=15.0,
            latency_ms=3000,
            max_tokens=128000,
            capabilities=["vision", "creative", "code"],
            quality_score=9.0
        ))
        
        self.register(ModelInfo(
            name="gpt-4o-mini",
            task_types=[TaskType.FAST, TaskType.KNOWLEDGE],
            cost_per_1k_input=0.15,
            cost_per_1k_output=0.6,
            latency_ms=500,
            max_tokens=128000,
            capabilities=["fast", "knowledge"],
            quality_score=7.5
        ))
        
        # Anthropic系列
        self.register(ModelInfo(
            name="claude-opus-4",
            task_types=[TaskType.REASONING, TaskType.ANALYSIS, TaskType.CODE],
            cost_per_1k_input=15.0,
            cost_per_1k_output=75.0,
            latency_ms=5000,
            max_tokens=200000,
            capabilities=["reasoning", "analysis", "code", "long_context"],
            quality_score=9.5
        ))
        
        self.register(ModelInfo(
            name="claude-sonnet-4",
            task_types=[TaskType.MULTIMODAL, TaskType.CREATIVE, TaskType.CODE],
            cost_per_1k_input=3.0,
            cost_per_1k_output=15.0,
            latency_ms=2000,
            max_tokens=200000,
            capabilities=["vision", "creative", "code"],
            quality_score=8.8
        ))
        
        self.register(ModelInfo(
            name="claude-haiku-3",
            task_types=[TaskType.FAST, TaskType.CHAT],
            cost_per_1k_input=0.8,
            cost_per_1k_output=4.0,
            latency_ms=500,
            max_tokens=200000,
            capabilities=["fast", "chat"],
            quality_score=7.8
        ))
        
        # Google系列
        self.register(ModelInfo(
            name="gemini-2.5-pro",
            task_types=[TaskType.REASONING, TaskType.MULTIMODAL, TaskType.ANALYSIS],
            cost_per_1k_input=1.25,
            cost_per_1k_output=5.0,
            latency_ms=4000,
            max_tokens=1000000,
            capabilities=["vision", "long_context", "reasoning"],
            quality_score=9.2
        ))
        
        self.register(ModelInfo(
            name="gemini-2.0-flash",
            task_types=[TaskType.FAST, TaskType.KNOWLEDGE],
            cost_per_1k_input=0.0,  # 免费
            cost_per_1k_output=0.0,
            latency_ms=300,
            max_tokens=1000000,
            capabilities=["fast", "free"],
            quality_score=7.2
        ))
        
        # 本地模型
        self.register(ModelInfo(
            name="llama-3.1-70b",
            task_types=[TaskType.CODE, TaskType.KNOWLEDGE],
            cost_per_1k_input=0.0,  # 本地
            cost_per_1k_output=0.0,
            latency_ms=2000,
            max_tokens=128000,
            capabilities=["local", "code", "fast"],
            quality_score=8.2
        ))
        
        self.register(ModelInfo(
            name="qwen-2.5-72b",
            task_types=[TaskType.CODE, TaskType.CHAT, TaskType.KNOWLEDGE],
            cost_per_1k_input=0.0,  # 本地
            cost_per_1k_output=0.0,
            latency_ms=1500,
            max_tokens=128000,
            capabilities=["local", "chinese", "code"],
            quality_score=8.0
        ))
        
        # 太乙专用模型
        self.register(ModelInfo(
            name="taiji-agi-v7",
            task_types=[TaskType.REASONING, TaskType.CODE, TaskType.ANALYSIS],
            cost_per_1k_input=2.0,
            cost_per_1k_output=8.0,
            latency_ms=3000,
            max_tokens=256000,
            capabilities=["taiji", "reasoning", "formal_proof", "hott"],
            quality_score=9.3
        ))
    
    def register(self, model: ModelInfo):
        """注册模型"""
        self.models[model.name] = model
    
    def get(self, name: str) -> Optional[ModelInfo]:
        """获取模型"""
        return self.models.get(name)
    
    def get_by_task(self, task_type: TaskType) -> List[ModelInfo]:
        """按任务类型获取模型"""
        return [m for m in self.models.values() if task_type in m.task_types]
    
    def get_all(self) -> List[ModelInfo]:
        """获取所有模型"""
        return list(self.models.values())


# ==================== 核心引擎 ====================

class ModelSmartRouter:
    """
    模型智能路由引擎
    
    基于OpenHuman Model Smart Router：
    - 任务分类: 推理型/快速型/多模态型/代码型/创作型
    - 动态选择最优模型
    - 成本-效率平衡
    
    定理T58: 模型路由最优定理 - 动态路由的效率-成本比 > 静态路由
    定理T59: 任务-模型匹配定理 - 匹配度与输出质量正相关
    """
    
    # 任务分类特征
    REASONING_KEYWORDS = [
        '证明', '推导', '推理', '逻辑', '数学', '分析', '计算', '证明',
        'prove', 'deduce', 'reasoning', 'logic', 'theorem'
    ]
    
    CODE_KEYWORDS = [
        '代码', '程序', '函数', '调试', 'bug', '代码', '实现', '算法',
        'code', 'function', 'debug', 'implement', 'algorithm', 'class', 'import'
    ]
    
    MULTIMODAL_KEYWORDS = [
        '图片', '图像', '照片', '截图', '图表', '看图', '分析图片',
        'image', 'photo', 'picture', 'chart', 'screenshot', 'vision'
    ]
    
    CREATIVE_KEYWORDS = [
        '创作', '写作', '故事', '诗歌', '小说', '广告', '文案', '创意',
        'creative', 'write', 'story', 'poem', 'novel', 'advertise'
    ]
    
    FAST_KEYWORDS = [
        '是什么', '叫什么', '多少', '时间', '简单', '快速',
        'what', 'who', 'when', 'where', 'simple', 'quick'
    ]
    
    ANALYSIS_KEYWORDS = [
        '分析', '比较', '评估', '预测', '趋势', '报告', '总结',
        'analyze', 'compare', 'evaluate', 'predict', 'trend', 'report'
    ]
    
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.stats = RouterStats()
        
        # 路由权重配置
        self.weights = {
            'match': 0.4,      # 任务匹配度
            'load': 0.2,        # 负载均衡
            'cost': 0.2,       # 成本效率
            'quality': 0.2      # 质量
        }
    
    def classify_task(self, query: str) -> Tuple[TaskType, float]:
        """
        任务分类
        
        Returns:
            (任务类型, 置信度)
        """
        query_lower = query.lower()
        scores = {}
        
        # 检测各类任务
        for task_type, keywords in [
            (TaskType.REASONING, self.REASONING_KEYWORDS),
            (TaskType.CODE, self.CODE_KEYWORDS),
            (TaskType.MULTIMODAL, self.MULTIMODAL_KEYWORDS),
            (TaskType.CREATIVE, self.CREATIVE_KEYWORDS),
            (TaskType.ANALYSIS, self.ANALYSIS_KEYWORDS),
        ]:
            matches = sum(1 for kw in keywords if kw in query or kw in query_lower)
            scores[task_type] = matches / len(keywords)
        
        # 简单问答型（低复杂度）
        if '?' in query and len(query) < 100:
            scores[TaskType.FAST] = 0.5
        
        # 闲聊型
        if any(g in query for g in ['你好', 'hi', 'hello', '嗨', '嘿']):
            scores[TaskType.CHAT] = 0.4
        
        # 知识查询型
        if any(k in query for k in ['什么是', 'who is', 'define', '解释']):
            scores[TaskType.KNOWLEDGE] = 0.4
        
        # 找最高分
        if not scores:
            return TaskType.CHAT, 0.5
        
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # 置信度计算
        confidence = min(1.0, best_score * 2)
        
        return best_type, confidence
    
    def select_model(self, 
                    task_type: TaskType, 
                    context: Optional[Dict] = None) -> Tuple[str, List[str]]:
        """
        选择最优模型
        
        Args:
            task_type: 任务类型
            context: 上下文信息（输入token数等）
        
        Returns:
            (最优模型名, 备用模型列表)
        """
        candidates = self.model_registry.get_by_task(task_type)
        
        if not candidates:
            # 回退到通用模型
            candidates = [m for m in self.model_registry.get_all() 
                         if TaskType.CHAT in m.task_types or TaskType.KNOWLEDGE in m.task_types]
        
        input_tokens = context.get('input_tokens', 1000) if context else 1000
        output_tokens = context.get('output_tokens', 500) if context else 500
        
        scores = []
        for model in candidates:
            # 1. 任务匹配分 (0-1)
            match_score = 1.0 if task_type in model.task_types else 0.3
            
            # 2. 负载均衡分 (0-1)
            load_score = 1.0 - model.current_load
            
            # 3. 成本效率分 (归一化)
            efficiency = model.efficiency(input_tokens, output_tokens)
            max_efficiency = max(m.efficiency(input_tokens, output_tokens) for m in candidates) if candidates else 1
            cost_score = efficiency / max_efficiency if max_efficiency > 0 else 0
            
            # 4. 质量分 (归一化)
            max_quality = max(m.quality_score for m in candidates) if candidates else 10
            quality_score = model.quality_score / max_quality if max_quality > 0 else 0
            
            # 综合分数
            total = (self.weights['match'] * match_score +
                    self.weights['load'] * load_score +
                    self.weights['cost'] * cost_score +
                    self.weights['quality'] * quality_score)
            
            scores.append((model.name, total, model))
        
        # 排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        best_model = scores[0][0]
        fallback_models = [s[0] for s in scores[1:3]]  # 前2个备用
        
        return best_model, fallback_models
    
    def route(self, query: str, context: Optional[Dict] = None) -> RouteDecision:
        """
        完整路由决策
        
        Args:
            query: 用户查询
            context: 上下文信息
        
        Returns:
            RouteDecision
        """
        # 1. 任务分类
        task_type, confidence = self.classify_task(query)
        
        # 2. 模型选择
        selected_model, fallback_models = self.select_model(task_type, context)
        
        # 3. 获取模型信息
        model_info = self.model_registry.get(selected_model)
        
        # 4. 估算
        input_tokens = context.get('input_tokens', 1000) if context else 1000
        output_tokens = context.get('output_tokens', 500) if context else 500
        estimated_cost = model_info.total_cost(input_tokens, output_tokens) if model_info else 0
        estimated_latency = model_info.latency_ms if model_info else 1000
        
        # 5. 生成推理
        reasoning = self._generate_reasoning(task_type, selected_model, confidence)
        
        # 6. 更新统计
        self._update_stats(task_type, selected_model, confidence, estimated_cost)
        
        return RouteDecision(
            task_type=task_type,
            selected_model=selected_model,
            fallback_models=fallback_models,
            reasoning=reasoning,
            confidence=confidence,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency
        )
    
    def _generate_reasoning(self, task_type: TaskType, model: str, confidence: float) -> str:
        """生成路由推理"""
        reasonings = {
            TaskType.REASONING: f"推理任务，选择{model}（强推理能力）",
            TaskType.CODE: f"代码任务，选择{model}（代码专用优化）",
            TaskType.MULTIMODAL: f"多模态任务，选择{model}（视觉理解）",
            TaskType.CREATIVE: f"创意任务，选择{model}（创意生成）",
            TaskType.FAST: f"快速响应，选择{model}（低延迟）",
            TaskType.ANALYSIS: f"分析任务，选择{model}（深度分析）",
            TaskType.CHAT: f"闲聊任务，选择{model}（对话优化）",
            TaskType.KNOWLEDGE: f"知识查询，选择{model}（知识库丰富）"
        }
        
        base = reasonings.get(task_type, f"通用任务，选择{model}")
        if confidence < 0.5:
            base += f"（分类置信度{confidence:.0%}，可能有误）"
        
        return base
    
    def _update_stats(self, task_type: TaskType, model: str, confidence: float, cost: float):
        """更新统计"""
        self.stats.total_requests += 1
        self.stats.task_type_counts[task_type.value] = \
            self.stats.task_type_counts.get(task_type.value, 0) + 1
        self.stats.model_usage_counts[model] = \
            self.stats.model_usage_counts.get(model, 0) + 1
        self.stats.total_cost += cost
        
        # 更新模型负载
        model_info = self.model_registry.get(model)
        if model_info:
            model_info.current_load = min(1.0, model_info.current_load + 0.1)
    
    def release_load(self, model: str):
        """释放模型负载"""
        model_info = self.model_registry.get(model)
        if model_info:
            model_info.current_load = max(0.0, model_info.current_load - 0.1)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取路由统计"""
        return {
            'total_requests': self.stats.total_requests,
            'task_type_distribution': self.stats.task_type_counts,
            'model_usage_distribution': self.stats.model_usage_counts,
            'total_cost': self.stats.total_cost,
            'average_cost_per_request': self.stats.total_cost / self.stats.total_requests if self.stats.total_requests > 0 else 0,
            'theorem_T58_comparison': {
                'dynamic_cost_efficiency': self._compute_dynamic_efficiency(),
                'static_baseline': self._compute_static_baseline(),
                'improvement_percent': self._compute_improvement()
            }
        }
    
    def _compute_dynamic_efficiency(self) -> float:
        """计算动态路由效率"""
        if not self.stats.total_requests:
            return 0.0
        
        # 简化：效率 = 总质量 / 总成本
        total_quality = sum(
            self.model_registry.get(m).quality_score * c 
            for m, c in self.stats.model_usage_counts.items()
            if self.model_registry.get(m)
        )
        
        return total_quality / self.stats.total_cost if self.stats.total_cost > 0 else 0
    
    def _compute_static_baseline(self) -> float:
        """计算静态路由基线（总是使用最贵的模型）"""
        # 假设静态使用 claude-opus-4
        return 9.5 / 0.09  # 质量 / 单请求成本
    
    def _compute_improvement(self) -> float:
        """计算改进百分比"""
        dynamic = self._compute_dynamic_efficiency()
        static = self._compute_static_baseline()
        if static == 0:
            return 0
        return (dynamic - static) / static * 100

    def get_state(self) -> Dict[str, Any]:
        """获取状态（与其他模块一致的接口，委托给get_stats）"""
        return self.get_stats()
    
    def get_model_loads(self) -> Dict[str, float]:
        """获取所有模型负载"""
        return {
            name: info.current_load 
            for name, info in self.model_registry.models.items()
        }
    
    def get_routing_history(self, limit: int = 50) -> List[Dict]:
        """获取路由历史（简化版本，实际应从数据库读取）"""
        # 简化：返回当前统计
        return [{
            'task_type': task_type,
            'count': count
        } for task_type, count in self.stats.task_type_counts.items()]


# ==================== 太乙AGI专用路由 ====================

class TaijiModelRouter(ModelSmartRouter):
    """
    太乙AGI专用模型路由
    
    针对太乙AGI的任务类型优化
    """
    
    # 太乙AGI特定关键词
    TAIJI_KEYWORDS = {
        'formal_proof': ['证明', '定理', '形式化', '形式验证', 'HoTT', '范畴论'],
        'hott': ['同伦类型论', 'HoTT', '类型论', '命题即类型'],
        'category': ['范畴', '函子', '自然变换', '态射', '对象'],
        'consciousness': ['意识', '涌现', '主观体验', '感质', 'qualia'],
        'eml': ['EML', '流贯', '信息守恒', '相位'],
        'wuxing': ['五行', '相生相克', '金木水火土'],
        'memory': ['记忆', '上下文', '会话', '历史'],
    }
    
    def classify_taiji_task(self, query: str) -> Tuple[str, List[str]]:
        """
        太乙AGI特定任务分类
        
        Returns:
            (子任务类型, 推荐模型)
        """
        for subtask, keywords in self.TAIJI_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                # 太乙专用模型优先
                if subtask in ['formal_proof', 'hott', 'category', 'consciousness']:
                    return subtask, ['taiji-agi-v7', 'claude-opus-4']
                elif subtask in ['eml', 'wuxing']:
                    return subtask, ['taiji-agi-v7', 'qwen-2.5-72b']
                elif subtask == 'memory':
                    return subtask, ['taiji-agi-v7', 'gpt-4o-mini']
        
        return 'general', ['taiji-agi-v7']


# ==================== API端点函数 ====================

def create_model_smart_router() -> ModelSmartRouter:
    """工厂函数"""
    return ModelSmartRouter()


def create_taiji_router() -> TaijiModelRouter:
    """太乙专用路由工厂"""
    return TaijiModelRouter()


# 全局单例
_m84_instance: Optional['ModelSmartRouter'] = None

def get_instance() -> 'ModelSmartRouter':
    """获取M84 ModelSmartRouter全局单例"""
    global _m84_instance
    if _m84_instance is None:
        _m84_instance = ModelSmartRouter()
    return _m84_instance

def get_state() -> Dict[str, Any]:
    """模块级get_state，与其他模块统一"""
    return get_instance().get_state()


if __name__ == "__main__":
    # 测试代码
    router = ModelSmartRouter()
    taiji_router = TaijiModelRouter()
    
    print("=" * 60)
    print("ModelSmartRouter 测试")
    print("=" * 60)
    
    # 测试用例
    test_queries = [
        "证明勾股定理",
        "帮我写一个快速排序函数",
        "分析这张图片的内容",
        "写一首关于春天的诗",
        "今天天气怎么样？",
        "比较REST和GraphQL的优缺点",
        "你好，最近怎么样？",
        "什么是同伦类型论？"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 通用路由
        decision = router.route(query)
        print(f"  任务类型: {decision.task_type.value}")
        print(f"  选择模型: {decision.selected_model}")
        print(f"  置信度: {decision.confidence:.0%}")
        print(f"  推理: {decision.reasoning}")
        
        # 太乙专用路由
        subtask, models = taiji_router.classify_taiji_task(query)
        if subtask != 'general':
            print(f"  太乙子任务: {subtask}, 推荐: {models}")
    
    # 获取统计
    print("\n" + "=" * 60)
    print("路由统计")
    print("=" * 60)
    stats = router.get_stats()
    print(f"总请求数: {stats['total_requests']}")
    print(f"任务分布: {stats['task_type_distribution']}")
    print(f"模型使用: {stats['model_usage_distribution']}")
    print(f"定理T58改进: {stats['theorem_T58_comparison']['improvement_percent']:.1f}%")
