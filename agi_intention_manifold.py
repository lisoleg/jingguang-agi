# -*- coding: utf-8 -*-
"""
复合体AGI 6.0 - 意图流形曲率引擎
Intention Manifold Curvature Engine

基于复合体理学全息拓扑动力学：
- 意图流形曲率 → 界面自适应布局
- 费马极值原理 → 最优展示路径
- 太乙预言机 → 意图预判

核心创新：
曲率决定信息密度、展示形式、交互深度

版本: v1.0
日期: 2026-05-13
"""

import math
import time
import re
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict


class IntentType(Enum):
    """意图类型枚举"""
    QUERY = "query"              # 查询
    TASK = "task"               # 任务
    CREATION = "creation"       # 创作
    ANALYSIS = "analysis"      # 分析
    DISCUSSION = "discussion"   # 讨论
    LEARNING = "learning"       # 学习
    CODE = "code"               # 代码
    SUMMARY = "summary"         # 总结
    COMPARISON = "comparison"    # 比较
    UNKNOWN = "unknown"          # 未知


class CurvatureLevel(Enum):
    """曲率层级"""
    VERY_LOW = (0.0, 0.2, "极低曲率", "概览模式")
    LOW = (0.2, 0.4, "低曲率", "简略模式")
    MEDIUM = (0.4, 0.6, "中曲率", "标准模式")
    HIGH = (0.6, 0.8, "高曲率", "详细模式")
    VERY_HIGH = (0.8, 1.0, "极高曲率", "全息模式")


class DensityMode(Enum):
    """信息密度模式"""
    ATOMIC = "atomic"           # 原子级 - 最低密度
    MOLECULAR = "molecular"     # 分子级 - 低密度
    ORGANIC = "organic"          # 有机级 - 中密度
    SYSTEMIC = "systemic"       # 系统级 - 高密度
    HOLOGRAPHIC = "holographic" # 全息级 - 最高密度


@dataclass
class Intent:
    """意图数据"""
    raw_text: str = ""           # 原始文本
    intent_type: IntentType = IntentType.UNKNOWN
    confidence: float = 0.0      # 置信度
    entities: List[Dict] = field(default_factory=list)  # 实体
    keywords: List[str] = field(default_factory=list)   # 关键词
    
    # 复杂度评估
    complexity: float = 0.5      # 0-1 复杂度
    depth_requirement: float = 0.5  # 深度要求
    breadth_requirement: float = 0.5  # 广度要求
    
    # 曲率参数
    curvature: float = 0.5      # 流形曲率
    curvature_level: CurvatureLevel = CurvatureLevel.MEDIUM
    
    # 元数据
    context_history: List[str] = field(default_factory=list)
    user_expertise: float = 0.5  # 用户专业度
    session_goal: Optional[str] = None


@dataclass
class ManifoldPoint:
    """流形上的点"""
    position: Tuple[float, float]  # 在语义空间的位置
    dimension: int = 0             # 维度
    curvature: float = 0.5          # 曲率
    neighbors: List[int] = field(default_factory=list)  # 邻居索引
    
    # 度量属性
    distance_to_query: float = float('inf')
    geodesic_distance: float = 0.0
    
    # 语义属性
    semantic_label: str = ""
    importance: float = 0.5


@dataclass
class GeodesicPath:
    """测地线路径"""
    points: List[ManifoldPoint] = field(default_factory=list)
    total_distance: float = 0.0
    curvature_variation: float = 0.0  # 曲率变化
    
    # 最优性
    is_optimal: bool = False
    optimization_score: float = 0.0
    
    def compute_total_distance(self):
        """计算路径总距离"""
        if len(self.points) < 2:
            self.total_distance = 0.0
            return
        
        total = 0.0
        for i in range(1, len(self.points)):
            dx = self.points[i].position[0] - self.points[i-1].position[0]
            dy = self.points[i].position[1] - self.points[i-1].position[1]
            total += math.sqrt(dx * dx + dy * dy)
        
        self.total_distance = total


@dataclass
class DisplayConfig:
    """展示配置"""
    density_mode: DensityMode = DensityMode.ORGANIC
    depth: int = 3               # 展示深度
    show_reasoning: bool = False # 显示推理链
    show_sources: bool = False   # 显示来源
    show_examples: bool = True   # 显示示例
    
    # 可视化类型
    viz_type: str = "auto"       # auto/flowchart/mindmap/table/story
    layout_type: str = "adaptive"  # adaptive/linear/grid/hierarchical
    
    # 交互模式
    interaction_mode: str = "standard"  # standard/expert/minimal
    auto_expand: bool = True     # 自动展开
    
    # 全息参数
    hologram_layers: int = 3      # 全息层数
    projection_angle: float = 0.0 # 投影角度


class IntentionManifoldEngine:
    """
    意图流形曲率引擎
    
    核心功能：
    1. 意图识别 - 分析用户输入的语义
    2. 曲率计算 - 在语义空间计算流形曲率
    3. 费马路径 - 寻找最优展示路径
    4. 自适应展示 - 根据曲率生成展示配置
    
    融合复合体理学：
    - 刘原理 → 作用量评分
    - 三视界法 → 多层展示
    - 太乙预言机 → 意图预判
    - 全息拓扑动力学 → 信息密度自适应
    """
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        IntentType.QUERY: [
            r"什么是", r"怎么", r"如何", r"为什么", r"多少",
            r"哪个", r"什么", r"哪一", r"是不是", r"有没有"
        ],
        IntentType.TASK: [
            r"帮我", r"请", r"帮我做", r"完成", r"执行",
            r"制作", r"生成", r"创建", r"写", r"做"
        ],
        IntentType.CREATION: [
            r"创作", r"设计", r"写", r"编", r"构思",
            r"发明", r"创新", r"策划", r"规划"
        ],
        IntentType.ANALYSIS: [
            r"分析", r"比较", r"对比", r"评估", r"研究",
            r"探讨", r"论述", r"论证", r"检验"
        ],
        IntentType.DISCUSSION: [
            r"讨论", r"聊聊", r"说说", r"谈谈", r"觉得",
            r"认为", r"关于", r"对于"
        ],
        IntentType.LEARNING: [
            r"学习", r"了解", r"认识", r"掌握", r"入门",
            r"教我", r"讲解", r"解释", r"说明"
        ],
        IntentType.CODE: [
            r"代码", r"程序", r"函数", r"算法", r"实现",
            r"编程", r"开发", r"调试", r"运行"
        ],
        IntentType.SUMMARY: [
            r"总结", r"概括", r"归纳", r"汇总", r"提炼",
            r"摘要", r"要点", r"简述"
        ],
        IntentType.COMPARISON: [
            r"比较", r"对比", r"差异", r"区别", r"不同",
            r"哪个好", r"哪个更", r"vs", r" versus "
        ],
    }
    
    # 复杂度评估词汇
    COMPLEXITY_INCREASERS = [
        "复杂", "深入", "详细", "全面", "彻底", "系统",
        "专业", "高级", "底层", "核心", "本质"
    ]
    
    COMPLEXITY_DECREASERS = [
        "简单", "简要", "简略", "概述", "大概", "粗略",
        "入门", "基础", "初学", "快速"
    ]
    
    def __init__(self):
        """初始化引擎"""
        # 当前意图
        self.current_intent: Optional[Intent] = None
        self.intent_history: List[Intent] = []
        
        # 语义空间
        self.semantic_space: List[ManifoldPoint] = []
        self.semantic_dimensions = 10
        
        # 测地线路径
        self.current_path: Optional[GeodesicPath] = None
        
        # 展示配置
        self.display_config = DisplayConfig()
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 统计
        self.stats = {
            "total_intents": 0,
            "avg_complexity": 0.0,
            "avg_curvature": 0.0,
        }
        
        # 预训练的意图预测模型(简化版)
        self.taiyi_predictions: Dict[str, float] = {}
    
    def analyze_intent(self, text: str,
                      context: Optional[List[str]] = None) -> Intent:
        """
        分析用户意图
        
        Args:
            text: 用户输入文本
            context: 上下文历史
            
        Returns:
            意图分析结果
        """
        with self._lock:
            intent = Intent()
            intent.raw_text = text
            
            # 1. 意图类型识别
            intent.intent_type = self._classify_intent_type(text)
            
            # 2. 实体和关键词提取
            intent.entities = self._extract_entities(text)
            intent.keywords = self._extract_keywords(text)
            
            # 3. 复杂度评估
            intent.complexity = self._assess_complexity(text)
            
            # 4. 用户专业度评估(基于用词)
            intent.user_expertise = self._assess_expertise(text)
            
            # 5. 深度/广度要求
            intent.depth_requirement, intent.breadth_requirement = \
                self._assess_requirements(text, intent.complexity)
            
            # 6. 曲率计算
            intent.curvature = self._compute_curvature(intent)
            intent.curvature_level = self._get_curvature_level(intent.curvature)
            
            # 7. 上下文
            if context:
                intent.context_history = context[-5:]  # 最近5条
            
            # 保存
            self.current_intent = intent
            self.intent_history.append(intent)
            self.stats["total_intents"] += 1
            
            return intent
    
    def _classify_intent_type(self, text: str) -> IntentType:
        """分类意图类型"""
        scores = defaultdict(float)
        
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    scores[intent_type] += 1
        
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] >= 1:
                return best_type[0]
        
        return IntentType.UNKNOWN
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """提取实体(简化版)"""
        entities = []
        
        # 人名识别
        # 这里使用简化规则，实际应用中应使用NER模型
        
        # 数字实体
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        for num in numbers:
            entities.append({
                "type": "number",
                "value": num,
                "span": text.find(num)
            })
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词
        words = re.findall(r'[\w]+', text)
        
        # 过滤停用词
        stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就",
            "不", "人", "都", "一", "一个", "上", "也", "很",
            "到", "说", "要", "去", "你", "会", "着", "没有",
            "看", "好", "自己", "这", "那", "吗", "吧"
        }
        
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        return keywords[:10]  # 限制数量
    
    def _assess_complexity(self, text: str) -> float:
        """评估复杂度"""
        complexity = 0.5  # 基础复杂度
        
        # 文本长度
        length = len(text)
        if length > 100:
            complexity += 0.1
        elif length > 200:
            complexity += 0.2
        
        # 关键词调整
        for word in self.COMPLEXITY_INCREASERS:
            if word in text:
                complexity += 0.05
        
        for word in self.COMPLEXITY_DECREASERS:
            if word in text:
                complexity -= 0.05
        
        # 问号数量(复杂问题通常多个问号)
        question_count = text.count('?') + text.count('？')
        if question_count > 1:
            complexity += 0.1 * (question_count - 1)
        
        # 限制范围
        return max(0.1, min(0.9, complexity))
    
    def _assess_expertise(self, text: str) -> float:
        """评估用户专业度"""
        expertise = 0.5
        
        # 专业术语
        technical_terms = [
            "算法", "架构", "协议", "接口", "系统", "模块",
            "函数", "变量", "参数", "返回", "类型", "类",
            "API", "SDK", "SDK", "HTTP", "TCP", "SQL",
            "部署", "优化", "性能", "并发", "异步"
        ]
        
        for term in technical_terms:
            if term in text:
                expertise += 0.05
        
        # 专业表达
        if any(word in text for word in ["具体", "详细", "深入", "底层"]):
            expertise += 0.1
        
        return min(1.0, expertise)
    
    def _assess_requirements(self, text: str, 
                            complexity: float) -> Tuple[float, float]:
        """评估深度和广度要求"""
        depth = complexity
        breadth = complexity
        
        # 深度关键词
        depth_keywords = {
            "详细": 0.2, "深入": 0.2, "全面": 0.15,
            "彻底": 0.2, "完整": 0.15, "具体": 0.1
        }
        
        for word, boost in depth_keywords.items():
            if word in text:
                depth = min(1.0, depth + boost)
        
        # 广度关键词
        breadth_keywords = {
            "比较": 0.2, "对比": 0.2, "分析": 0.15,
            "研究": 0.15, "探讨": 0.1, "所有": 0.2
        }
        
        for word, boost in breadth_keywords.items():
            if word in text:
                breadth = min(1.0, breadth + boost)
        
        return depth, breadth
    
    def _compute_curvature(self, intent: Intent) -> float:
        """
        计算流形曲率
        
        曲率 = f(复杂度, 深度要求, 专业度, 意图类型)
        """
        # 加权计算
        curvature = (
            intent.complexity * 0.35 +
            intent.depth_requirement * 0.25 +
            intent.user_expertise * 0.15 +
            (1.0 - intent.breadth_requirement) * 0.15 +
            self._intent_type_to_curvature(intent.intent_type) * 0.1
        )
        
        return min(1.0, max(0.0, curvature))
    
    def _intent_type_to_curvature(self, intent_type: IntentType) -> float:
        """意图类型到曲率的映射"""
        mapping = {
            IntentType.QUERY: 0.3,
            IntentType.TASK: 0.5,
            IntentType.CREATION: 0.7,
            IntentType.ANALYSIS: 0.8,
            IntentType.DISCUSSION: 0.4,
            IntentType.LEARNING: 0.5,
            IntentType.CODE: 0.7,
            IntentType.SUMMARY: 0.3,
            IntentType.COMPARISON: 0.6,
            IntentType.UNKNOWN: 0.5,
        }
        return mapping.get(intent_type, 0.5)
    
    def _get_curvature_level(self, curvature: float) -> CurvatureLevel:
        """获取曲率层级"""
        for level in CurvatureLevel:
            low, high, _, _ = level.value
            if low <= curvature < high:
                return level
            if curvature >= 0.95:  # 最高级
                return CurvatureLevel.VERY_HIGH
        return CurvatureLevel.MEDIUM
    
    # ==================== 费马路径搜索 ====================
    
    def compute_optimal_path(self, 
                           query_point: Optional[Tuple[float, float]] = None,
                           target_domain: Optional[str] = None) -> GeodesicPath:
        """
        计算最优测地线路径
        
        基于费马原理：光在介质中沿时间最短路径传播
        
        Args:
            query_point: 查询点在语义空间的位置
            target_domain: 目标领域
            
        Returns:
            最优路径
        """
        if query_point is None:
            query_point = (0.5, 0.5)  # 默认中心点
        
        path = GeodesicPath()
        
        if self.current_intent is None:
            return path
        
        # 构建语义空间点
        self._build_semantic_space(query_point)
        
        # 简化的Dijkstra路径搜索
        # 实际应用中应使用更复杂的算法
        path.points = self._dijkstra_search(query_point, target_domain)
        
        # 计算路径属性
        path.compute_total_distance()
        path.curvature_variation = self._compute_curvature_variation(path)
        
        # 评估最优性
        path.optimization_score = self._evaluate_path_optimization(path)
        path.is_optimal = path.optimization_score > 0.8
        
        self.current_path = path
        return path
    
    def _build_semantic_space(self, query_point: Tuple[float, float]):
        """构建语义空间"""
        self.semantic_space = []
        
        if self.current_intent is None:
            return
        
        # 基于意图类型生成空间点
        intent_type = self.current_intent.intent_type
        
        point_templates = {
            IntentType.QUERY: [
                (0.3, 0.4), (0.5, 0.5), (0.7, 0.6)
            ],
            IntentType.TASK: [
                (0.2, 0.3), (0.4, 0.5), (0.6, 0.7), (0.8, 0.8)
            ],
            IntentType.CREATION: [
                (0.1, 0.2), (0.3, 0.4), (0.5, 0.6), (0.7, 0.8), (0.9, 0.9)
            ],
            IntentType.ANALYSIS: [
                (0.2, 0.2), (0.4, 0.4), (0.6, 0.6), (0.8, 0.8)
            ],
        }
        
        points = point_templates.get(intent_type, [(0.3, 0.3), (0.5, 0.5), (0.7, 0.7)])
        
        for i, pos in enumerate(points):
            point = ManifoldPoint(
                position=pos,
                dimension=i,
                curvature=self.current_intent.curvature * (0.8 + 0.4 * (i / len(points))),
                distance_to_query=math.sqrt(
                    (pos[0] - query_point[0])**2 + (pos[1] - query_point[1])**2
                ),
                importance=0.5 + 0.5 * (i / len(points)),
                semantic_label=f"level_{i}"
            )
            self.semantic_space.append(point)
        
        # 建立邻居关系
        for i in range(len(self.semantic_space) - 1):
            self.semantic_space[i].neighbors.append(i + 1)
            self.semantic_space[i + 1].neighbors.append(i)
    
    def _dijkstra_search(self, 
                        start: Tuple[float, float],
                        target: Optional[str]) -> List[ManifoldPoint]:
        """简化的Dijkstra路径搜索"""
        if not self.semantic_space:
            return []
        
        # 简单贪心搜索
        path = [self.semantic_space[0]]
        
        for i in range(1, len(self.semantic_space)):
            path.append(self.semantic_space[i])
        
        return path
    
    def _compute_curvature_variation(self, path: GeodesicPath) -> float:
        """计算路径曲率变化"""
        if len(path.points) < 2:
            return 0.0
        
        variations = []
        for i in range(1, len(path.points)):
            var = abs(
                path.points[i].curvature - path.points[i-1].curvature
            )
            variations.append(var)
        
        return sum(variations) / len(variations) if variations else 0.0
    
    def _evaluate_path_optimization(self, path: GeodesicPath) -> float:
        """
        评估路径最优性
        
        基于多个因素：
        1. 路径距离
        2. 曲率变化平滑度
        3. 重要性覆盖
        """
        # 距离评分
        distance_score = max(0, 1.0 - path.total_distance / 10)
        
        # 平滑度评分
        smoothness_score = max(0, 1.0 - path.curvature_variation * 5)
        
        # 覆盖评分
        importance_sum = sum(p.importance for p in path.points)
        coverage_score = min(1.0, importance_sum / len(path.points))
        
        # 综合评分
        score = (
            distance_score * 0.3 +
            smoothness_score * 0.4 +
            coverage_score * 0.3
        )
        
        return score
    
    # ==================== 展示配置生成 ====================
    
    def generate_display_config(self) -> DisplayConfig:
        """
        根据意图和曲率生成展示配置
        
        基于复合体理学：
        - 曲率大 → 高密度 → 全息展示
        - 曲率小 → 低密度 → 概览展示
        """
        if self.current_intent is None:
            return DisplayConfig()
        
        config = DisplayConfig()
        curvature = self.current_intent.curvature
        curvature_level = self.current_intent.curvature_level
        
        # 1. 信息密度模式
        if curvature < 0.25:
            config.density_mode = DensityMode.ATOMIC
        elif curvature < 0.45:
            config.density_mode = DensityMode.MOLECULAR
        elif curvature < 0.65:
            config.density_mode = DensityMode.ORGANIC
        elif curvature < 0.85:
            config.density_mode = DensityMode.SYSTEMIC
        else:
            config.density_mode = DensityMode.HOLOGRAPHIC
        
        # 2. 展示深度
        config.depth = int(1 + curvature * 5)  # 1-6层
        
        # 3. 推理链显示
        config.show_reasoning = curvature > 0.5
        
        # 4. 来源显示
        config.show_sources = curvature > 0.4
        
        # 5. 示例显示
        config.show_examples = True
        
        # 6. 可视化类型
        intent_type = self.current_intent.intent_type
        if intent_type == IntentType.ANALYSIS:
            config.viz_type = "flowchart"
        elif intent_type == IntentType.CREATION:
            config.viz_type = "mindmap"
        elif intent_type == IntentType.COMPARISON:
            config.viz_type = "table"
        elif intent_type == IntentType.SUMMARY:
            config.viz_type = "outline"
        elif intent_type == IntentType.LEARNING:
            config.viz_type = "story"
        else:
            config.viz_type = "auto"
        
        # 7. 布局类型
        if curvature < 0.3:
            config.layout_type = "linear"
        elif curvature < 0.7:
            config.layout_type = "adaptive"
        else:
            config.layout_type = "hierarchical"
        
        # 8. 交互模式
        if self.current_intent.user_expertise > 0.7:
            config.interaction_mode = "expert"
        elif self.current_intent.user_expertise < 0.3:
            config.interaction_mode = "minimal"
        else:
            config.interaction_mode = "standard"
        
        # 9. 全息参数
        config.hologram_layers = int(1 + curvature * 4)
        config.projection_angle = curvature * 360
        
        self.display_config = config
        return config
    
    # ==================== 太乙预言机 - 意图预判 ====================
    
    def predict_next_intent(self) -> Optional[IntentType]:
        """
        太乙预言机 - 预测下一个意图
        
        基于历史模式分析
        """
        if len(self.intent_history) < 2:
            return None
        
        # 简单马尔可夫链
        recent = self.intent_history[-3:]
        types = [i.intent_type for i in recent]
        
        # 模式识别
        if types[-1] == IntentType.QUERY:
            # 查询后可能是任务
            return IntentType.TASK
        elif types[-1] == IntentType.ANALYSIS:
            # 分析后可能是总结
            return IntentType.SUMMARY
        elif types[-1] == IntentType.LEARNING:
            # 学习后可能是实践
            return IntentType.TASK
        
        return None
    
    # ==================== 实用函数 ====================
    
    def get_intent_summary(self) -> str:
        """获取意图摘要"""
        if self.current_intent is None:
            return "无当前意图"
        
        i = self.current_intent
        return (
            f"类型: {i.intent_type.value}\n"
            f"复杂度: {i.complexity:.2f}\n"
            f"曲率: {i.curvature:.2f} ({i.curvature_level.value[2]})\n"
            f"专业度: {i.user_expertise:.2f}\n"
            f"深度要求: {i.depth_requirement:.2f}\n"
            f"广度要求: {i.breadth_requirement:.2f}"
        )
    
    def get_display_summary(self) -> str:
        """获取展示配置摘要"""
        if self.current_intent is None:
            return "无配置"
        
        config = self.generate_display_config()
        
        return (
            f"密度模式: {config.density_mode.value}\n"
            f"展示深度: {config.depth}\n"
            f"显示推理链: {config.show_reasoning}\n"
            f"显示来源: {config.show_sources}\n"
            f"可视化类型: {config.viz_type}\n"
            f"布局类型: {config.layout_type}\n"
            f"交互模式: {config.interaction_mode}\n"
            f"全息层数: {config.hologram_layers}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "intent": {
                "raw_text": self.current_intent.raw_text if self.current_intent else "",
                "intent_type": self.current_intent.intent_type.value if self.current_intent else "",
                "confidence": self.current_intent.confidence if self.current_intent else 0.0,
                "complexity": self.current_intent.complexity if self.current_intent else 0.0,
                "curvature": self.current_intent.curvature if self.current_intent else 0.0,
                "curvature_level": self.current_intent.curvature_level.value[2] if self.current_intent else "",
                "keywords": self.current_intent.keywords if self.current_intent else [],
            },
            "display_config": {
                "density_mode": self.display_config.density_mode.value,
                "depth": self.display_config.depth,
                "show_reasoning": self.display_config.show_reasoning,
                "show_sources": self.display_config.show_sources,
                "viz_type": self.display_config.viz_type,
                "layout_type": self.display_config.layout_type,
                "hologram_layers": self.display_config.hologram_layers,
            },
            "stats": self.stats,
            "history_count": len(self.intent_history),
        }


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=== 意图流形曲率引擎测试 ===\n")
    
    # 创建引擎
    engine = IntentionManifoldEngine()
    
    # 测试用例
    test_cases = [
        ("帮我分析一下这个项目的架构设计，要深入详细的", "深度分析型"),
        ("什么是Python？请简要说明", "简单查询型"),
        ("帮我写一个快速排序算法，要求性能最优", "代码任务型"),
        ("比较一下React和Vue的优缺点", "对比分析型"),
        ("我想学习机器学习，从入门开始讲解", "学习型"),
    ]
    
    for text, description in test_cases:
        print(f"--- 测试: {description} ---")
        print(f"输入: {text}\n")
        
        # 分析意图
        intent = engine.analyze_intent(text)
        
        print(f"意图类型: {intent.intent_type.value}")
        print(f"复杂度: {intent.complexity:.2f}")
        print(f"曲率: {intent.curvature:.2f} ({intent.curvature_level.value[2]})")
        print(f"专业度: {intent.user_expertise:.2f}")
        print(f"深度要求: {intent.depth_requirement:.2f}")
        print(f"广度要求: {intent.breadth_requirement:.2f}")
        print(f"关键词: {intent.keywords}")
        
        # 生成展示配置
        config = engine.generate_display_config()
        print(f"\n展示配置:")
        print(f"  密度模式: {config.density_mode.value}")
        print(f"  展示深度: {config.depth}")
        print(f"  可视化类型: {config.viz_type}")
        print(f"  布局类型: {config.layout_type}")
        print(f"  全息层数: {config.hologram_layers}")
        
        # 预测下一个意图
        next_intent = engine.predict_next_intent()
        if next_intent:
            print(f"\n预测下一个意图: {next_intent.value}")
        
        print()
    
    # 测试路径搜索
    print("--- 路径搜索测试 ---")
    path = engine.compute_optimal_path((0.3, 0.4))
    print(f"路径点数: {len(path.points)}")
    print(f"路径距离: {path.total_distance:.3f}")
    print(f"曲率变化: {path.curvature_variation:.3f}")
    print(f"最优性评分: {path.optimization_score:.3f}")
    print(f"是否最优: {path.is_optimal}")
    
    print("\n测试完成!")
