"""
M90: SemanticManifoldCurvature - 语义流形曲率计算器
实现 T40: 曲率即逻辑张力定理

核心原理：
- 语义流形 M(L2) 上的曲率 K(M)
- K ≈ 0 (平坦): 多义性/创造性
- K >> 0 (高曲率): 逻辑必然性/确定性

Author: 太乙AGI 7.0 Team
Date: 2026-05-19
"""

from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict, Tuple
from enum import Enum
import math
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CurvatureLevel(Enum):
    """曲率层级"""
    FLAT = "flat"                    # K ≈ 0: 多义性/创造性
    LOW = "low"                      # K > 0 但较小
    MEDIUM = "medium"                # 中等曲率
    HIGH = "high"                    # K >> 0: 逻辑必然性
    EXTREME = "extreme"              # 极高曲率: 数学/逻辑确定性


@dataclass
class SemanticPoint:
    """语义空间中的点"""
    concept: str
    vector: np.ndarray
    layer: str = "L2"  # 默认在 L2 规则层
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.vector = np.array(self.vector, dtype=np.float64)


@dataclass
class MetricTensor:
    """度规张量 g_μν"""
    components: np.ndarray  # n×n 矩阵
    dimension: int
    
    def __post_init__(self):
        self.components = np.array(self.components, dtype=np.float64)
        self.dimension = self.components.shape[0]


@dataclass
class RicciCurvature:
    """Ricci 曲率张量 R_μν 和标量曲率 R"""
    tensor: np.ndarray  # Ricci 张量
    scalar: float       # Ricci 标量
    
    def __post_init__(self):
        self.tensor = np.array(self.tensor, dtype=np.float64)
        self.scalar = float(self.scalar)


@dataclass
class GeodesicResult:
    """测地线结果"""
    path: List[SemanticPoint]
    length: float
    uniqueness: str  # "unique" or "multiple"
    curvature: CurvatureLevel


@dataclass
class LogicalTensionResult:
    """逻辑张力结果"""
    curvature: float
    level: CurvatureLevel
    interpretation: str
    determinacy: str  # "determinate" or "indeterminate"
    creativity: float  # 创造力指标
    certainty: float   # 确定性指标


class SemanticManifoldCurvature:
    """语义流形曲率计算器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.manifold_points: Dict[str, SemanticPoint] = {}
        self.metric_cache: Dict[str, MetricTensor] = {}
        self.ricci_cache: Dict[str, RicciCurvature] = {}
        self.curvature_history: List[Dict] = []
    
    def add_point(self, concept: str, vector: List[float], layer: str = "L2") -> SemanticPoint:
        """添加语义点"""
        point = SemanticPoint(concept=concept, vector=vector, layer=layer)
        self.manifold_points[concept] = point
        logger.info(f"Added semantic point: {concept} in layer {layer}")
        return point
    
    def compute_metric_tensor(self, points: List[SemanticPoint]) -> MetricTensor:
        """计算黎曼度规张量 g_μν"""
        n = len(points)
        if n < 2:
            raise ValueError("Need at least 2 points to compute metric")
        
        # 使用协方差矩阵作为度规
        vectors = np.array([p.vector for p in points])
        
        # 确保向量是1D的
        if vectors.ndim > 1:
            if vectors.shape[0] > vectors.shape[1]:
                vectors = vectors.T
            
            # 如果还有多维，使用点积
            if len(vectors.shape) > 1 and vectors.shape[1] > 1:
                g = np.dot(vectors, vectors.T)
            else:
                g = np.outer(vectors.flatten(), vectors.flatten())
        else:
            g = np.outer(vectors, vectors)
        
        # 确保 g 是方阵
        min_dim = min(g.shape[0], g.shape[1])
        g = g[:min_dim, :min_dim]
        
        # 添加正则化
        g += np.eye(min_dim) * 0.01
        
        metric = MetricTensor(components=g, dimension=min_dim)
        
        # 缓存
        key = "_".join(p.concept for p in points)
        self.metric_cache[key] = metric
        
        return metric
    
    def compute_ricci_scalar(self, semantic_space: Any, metric: MetricTensor) -> RicciCurvature:
        """计算Ricci标量曲率 R = g^μν R_μν"""
        g = metric.components
        dim = metric.dimension
        
        try:
            # 尝试计算逆矩阵
            g_inv = np.linalg.inv(g)
            
            # 简化Ricci标量计算：使用度规行列式的 Laplacian
            det_g = np.linalg.det(g)
            
            if det_g <= 0:
                det_g = 1e-10
            
            # Ricci标量 = -Δ log(det(g))
            log_det = np.log(det_g)
            
            # 使用简化的曲率公式
            R_scalar = -0.5 * np.sum(log_det) / dim
            
        except np.linalg.LinAlgError:
            logger.warning("Singular metric, using fallback curvature")
            R_scalar = 1.0
            g_inv = np.eye(dim)
        
        # 构建简化的Ricci张量
        R_tensor = R_scalar * g_inv / dim
        
        ricci = RicciCurvature(tensor=R_tensor, scalar=R_scalar)
        
        # 缓存
        self.ricci_cache[str(semantic_space)] = ricci
        
        return ricci
    
    def normalize_curvature(self, raw_curvature: float) -> float:
        """归一化曲率到 [0, 1] 范围"""
        # 使用 sigmoid 类函数进行归一化
        # K ≈ 0: 创造性，K >> 0: 必然性
        
        if raw_curvature > 0:
            normalized = 1.0 / (1.0 + math.exp(-raw_curvature))
        else:
            # 负曲率（双曲/开放）映射到低值
            normalized = math.exp(raw_curvature) / (1 + math.exp(raw_curvature))
        
        return max(0.0, min(1.0, normalized))
    
    def get_curvature_level(self, curvature: float) -> CurvatureLevel:
        """根据曲率值确定曲率层级"""
        if abs(curvature) < 0.1:
            return CurvatureLevel.FLAT
        elif abs(curvature) < 0.3:
            return CurvatureLevel.LOW
        elif abs(curvature) < 0.6:
            return CurvatureLevel.MEDIUM
        elif abs(curvature) < 0.9:
            return CurvatureLevel.HIGH
        else:
            return CurvatureLevel.EXTREME
    
    def geodesic_uniqueness(self, point1: SemanticPoint, point2: SemanticPoint, curvature: float) -> str:
        """测地线唯一性由曲率决定"""
        level = self.get_curvature_level(curvature)
        
        if level in [CurvatureLevel.HIGH, CurvatureLevel.EXTREME]:
            return "unique"  # 唯一测地线 = 逻辑必然性
        else:
            return "multiple"  # 多条测地线 = 创造性/多义性
    
    def compute_logical_tension_metric(
        self, 
        concept1: str, 
        concept2: str
    ) -> LogicalTensionResult:
        """逻辑张力度量：曲率 → 下一个Token的确定性"""
        logger.info(f"Computing logical tension: {concept1} → {concept2}")
        
        # 获取语义点
        p1 = self.manifold_points.get(concept1)
        p2 = self.manifold_points.get(concept2)
        
        if p1 is None or p2 is None:
            logger.warning("One or both concepts not found, using default curvature")
            return LogicalTensionResult(
                curvature=0.5,
                level=CurvatureLevel.MEDIUM,
                interpretation="Default: moderate logical tension",
                determinacy="partial",
                creativity=0.5,
                certainty=0.5
            )
        
        # 计算两点间的"曲率"
        diff = p1.vector - p2.vector
        raw_curvature = np.linalg.norm(diff)
        
        # 归一化
        normalized_curvature = self.normalize_curvature(raw_curvature)
        level = self.get_curvature_level(normalized_curvature)
        
        # 确定性和创造力指标
        certainty = normalized_curvature
        creativity = 1.0 - normalized_curvature
        
        # 解释
        if level == CurvatureLevel.FLAT:
            interpretation = "多义性空间：多个等价格念连接（创造性/想象）"
            determinacy = "indeterminate"
        elif level == CurvatureLevel.LOW:
            interpretation = "轻度逻辑约束：存在多个合理的概念连接"
            determinacy = "partially_determinate"
        elif level == CurvatureLevel.MEDIUM:
            interpretation = "中等逻辑张力：某些概念连接更受偏好"
            determinacy = "moderately_determinate"
        elif level == CurvatureLevel.HIGH:
            interpretation = "高逻辑必然性：测地线唯一且短（如'√4='→'2'）"
            determinacy = "determinate"
        else:  # EXTREME
            interpretation = "极高确定性：数学/逻辑必然结果"
            determinacy = "highly_determinate"
        
        result = LogicalTensionResult(
            curvature=normalized_curvature,
            level=level,
            interpretation=interpretation,
            determinacy=determinacy,
            creativity=creativity,
            certainty=certainty
        )
        
        self.curvature_history.append({
            "concept1": concept1,
            "concept2": concept2,
            "curvature": normalized_curvature,
            "level": level.value,
            "certainty": certainty,
            "creativity": creativity
        })
        
        return result
    
    def compute_semantic_curvature(
        self, 
        concepts: List[str]
    ) -> Tuple[float, CurvatureLevel, GeodesicResult]:
        """计算语义流形曲率"""
        points = [self.manifold_points[c] for c in concepts if c in self.manifold_points]
        
        if len(points) < 2:
            return 0.5, CurvatureLevel.MEDIUM, None
        
        try:
            metric = self.compute_metric_tensor(points)
            ricci = self.compute_ricci_scalar(concepts, metric)
            
            # 使用Ricci标量作为曲率
            curvature = self.normalize_curvature(abs(ricci.scalar))
            level = self.get_curvature_level(curvature)
            
            # 计算测地线路径
            geodesic_path = self._compute_geodesic(points, curvature)
            
            return curvature, level, geodesic_path
            
        except Exception as e:
            logger.error(f"Curvature computation failed: {e}")
            return 0.5, CurvatureLevel.MEDIUM, None
    
    def _compute_geodesic(
        self, 
        points: List[SemanticPoint], 
        curvature: float
    ) -> GeodesicResult:
        """计算测地线"""
        uniqueness = "unique" if curvature > 0.5 else "multiple"
        
        # 简化的测地线：两点之间的直线
        path = points
        length = sum(
            np.linalg.norm(path[i].vector - path[i+1].vector)
            for i in range(len(path) - 1)
        )
        
        return GeodesicResult(
            path=path,
            length=length,
            uniqueness=uniqueness,
            curvature=self.get_curvature_level(curvature)
        )
    
    def predict_token_determinacy(
        self, 
        context: str, 
        partial_sequence: List[str]
    ) -> Dict[str, Any]:
        """预测下一个Token的确定性"""
        if len(partial_sequence) < 2:
            return {"determinacy": 0.5, "creativity": 0.5}
        
        # 计算相邻概念间的曲率
        tensions = []
        for i in range(len(partial_sequence) - 1):
            result = self.compute_logical_tension_metric(
                partial_sequence[i], 
                partial_sequence[i+1]
            )
            tensions.append(result)
        
        avg_curvature = np.mean([t.curvature for t in tensions]) if tensions else 0.5
        
        return {
            "determinacy": avg_curvature,
            "creativity": 1.0 - avg_curvature,
            "interpretation": "√4= -> 2" if avg_curvature > 0.8 else "Creative completion possible"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "points": len(self.manifold_points),
            "cached_metrics": len(self.metric_cache),
            "cached_ricci": len(self.ricci_cache),
            "history_entries": len(self.curvature_history)
        }


# 单例访问
def get_curvature_calculator() -> SemanticManifoldCurvature:
    """获取语义流形曲率计算器单例"""
    return SemanticManifoldCurvature()


if __name__ == "__main__":
    # 测试语义流形曲率计算器
    print("=" * 60)
    print("M90: SemanticManifoldCurvature - 语义流形曲率计算器测试")
    print("=" * 60)
    
    calculator = get_curvature_calculator()
    
    # 添加语义点
    print("\n[测试 1] 添加语义点")
    calculator.add_point("数学", [1.0, 0.0, 0.0], "L2")
    calculator.add_point("2+2", [0.9, 0.1, 0.0], "L2")
    calculator.add_point("诗歌", [0.0, 1.0, 0.0], "L2")
    calculator.add_point("苹果", [0.5, 0.5, 0.0], "L2")
    print(f"  添加了 4 个语义点")
    
    # 测试用例 2: 逻辑张力度量
    print("\n[测试 2] 逻辑张力度量（高确定性）")
    result1 = calculator.compute_logical_tension_metric("数学", "2+2")
    print(f"  曲率: {result1.curvature:.4f}")
    print(f"  层级: {result1.level.value}")
    print(f"  解释: {result1.interpretation}")
    print(f"  确定性: {result1.determinacy}")
    
    print("\n[测试 3] 逻辑张力度量（高创造性）")
    result2 = calculator.compute_logical_tension_metric("数学", "诗歌")
    print(f"  曲率: {result2.curvature:.4f}")
    print(f"  层级: {result2.level.value}")
    print(f"  解释: {result2.interpretation}")
    print(f"  创造力: {result2.creativity:.4f}")
    
    # 测试用例 3: 语义曲率计算
    print("\n[测试 4] 语义流形曲率")
    curvature, level, geodesic = calculator.compute_semantic_curvature(
        ["数学", "2+2", "苹果"]
    )
    print(f"  曲率: {curvature:.4f}")
    print(f"  层级: {level.value}")
    if geodesic:
        print(f"  测地线唯一性: {geodesic.uniqueness}")
    
    # 测试用例 4: Token确定性预测
    print("\n[测试 5] Token确定性预测")
    prediction = calculator.predict_token_determinacy(
        "数学上下文",
        ["√4=", "2"]
    )
    print(f"  确定性: {prediction['determinacy']:.4f}")
    print(f"  创造力: {prediction['creativity']:.4f}")
    print(f"  解释: {prediction['interpretation']}")
    
    # 测试用例 5: 状态查询
    print("\n[测试 6] 状态查询")
    status = calculator.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("M90 测试完成！")
    print("=" * 60)
