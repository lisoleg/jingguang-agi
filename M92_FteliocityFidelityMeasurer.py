"""
M92: FteliocityFidelityMeasurer - 流贯保真度测量器
实现 T37: 流贯保真度 F 测量

核心原理：
- F(L_i, L_j) = |<L_i| EML |L_j>|² / (|L_i|² * |L_j|²)
- 无损流贯：F = 1
- 信息损耗警告：F < 0.9

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


@dataclass
class EMLState:
    """EML量子态"""
    name: str
    vector: np.ndarray  # 态矢量 |ψ⟩
    phase: float        # 相位
    layer: str           # 所属层
    
    def __post_init__(self):
        self.vector = np.array(self.vector, dtype=np.complex128)
        # 归一化
        norm = np.linalg.norm(self.vector)
        if norm > 0:
            self.vector = self.vector / norm


@dataclass
class EMLEmbeddedOperator:
    """EML嵌入算子"""
    name: str
    matrix: np.ndarray
    
    def __post_init__(self):
        self.matrix = np.array(self.matrix, dtype=np.complex128)
    
    def apply(self, state: EMLState) -> EMLState:
        """应用算子到态"""
        new_vector = np.dot(self.matrix, state.vector)
        return EMLState(
            name=f"{self.name}_applied",
            vector=new_vector,
            phase=state.phase,
            layer=state.layer
        )


@dataclass
class FidelityResult:
    """保真度测量结果"""
    fidelity: float           # F(L_i, L_j)
    is_lossless: bool         # F ≈ 1
    is_acceptable: bool       # F >= 0.9
    information_loss: float    # 1 - F
    warning: Optional[str]     # 警告信息
    layer_pair: Tuple[str, str]


class FteliocityFidelityMeasurer:
    """流贯保真度测量器"""
    
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
        self.eml_states: Dict[str, EMLState] = {}
        self.eml_operators: Dict[str, EMLEmbeddedOperator] = {}
        self.fidelity_history: List[FidelityResult] = []
        self._setup_default_operators()
    
    def _setup_default_operators(self):
        """设置默认EML算子"""
        # 五行算子（简化的2x2矩阵表示）
        operators = {
            "water": np.array([[1, 0], [0, 0.8]], dtype=np.complex128),  # Σ: 信息蓄积
            "fire": np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128),  # F: 流贯执行
            "wood": np.array([[1.1, 0], [0, 1]], dtype=np.complex128),   # R: 递归生长
            "metal": np.array([[0.9, 0], [0, 0.9]], dtype=np.complex128),  # E: 熵减收敛
            "earth": np.array([[1, 0], [0, 1]], dtype=np.complex128),     # B: 稳态锚定
        }
        
        for name, matrix in operators.items():
            self.eml_operators[name] = EMLEmbeddedOperator(name=name, matrix=matrix)
    
    def register_state(self, state: EMLState):
        """注册EML态"""
        self.eml_states[state.name] = state
        logger.info(f"Registered EML state: {state.name} at layer {state.layer}")
    
    def inner_product(self, state1: EMLState, state2: EMLState) -> complex:
        """计算内积 ⟨L_i | L_j⟩"""
        return np.vdot(state1.vector, state2.vector)
    
    def norm(self, state: EMLState) -> float:
        """计算态的范数 |ψ|"""
        return np.linalg.norm(state.vector)
    
    def compute_fidelity(
        self, 
        L_i: EMLState, 
        L_j: EMLState, 
        eml_operator: Optional[EMLEmbeddedOperator] = None
    ) -> float:
        """
        计算流贯保真度
        
        F(L_i, L_j) = |<L_i| EML |L_j>|² / (|L_i|² * |L_j|²)
        
        当 eml_operator 为 None 时，使用恒等算子
        """
        if eml_operator is None:
            # 恒等算子
            inner = self.inner_product(L_i, L_j)
        else:
            # 应用 EML 算子
            applied = eml_operator.apply(L_j)
            inner = self.inner_product(L_i, applied)
        
        # 分子: |<L_i| EML |L_j>|²
        numerator = abs(inner) ** 2
        
        # 分母: |L_i|² * |L_j|²
        denominator = self.norm(L_i) ** 2 * self.norm(L_j) ** 2
        
        if denominator == 0:
            logger.warning("Zero denominator in fidelity calculation")
            return 0.0
        
        fidelity = numerator / denominator
        
        # 确保在 [0, 1] 范围内
        return max(0.0, min(1.0, float(fidelity)))
    
    def check_lossless_fteliation(self, fidelity: float, threshold: float = 0.99) -> bool:
        """无损流贯：F ≈ 1"""
        return fidelity >= threshold
    
    def information_loss_warning(
        self, 
        fidelity: float, 
        threshold: float = 0.9
    ) -> Optional[str]:
        """信息损耗警告：F < 0.9"""
        if fidelity < threshold:
            loss_percent = (1 - fidelity) * 100
            return f"⚠️ 高信息损耗！损失 {loss_percent:.1f}%，L2规则在L3/L5被切割！"
        return None
    
    def measure_fteliation(
        self, 
        layer_i: str, 
        layer_j: str,
        eml_operator_name: Optional[str] = None
    ) -> FidelityResult:
        """测量层间流贯保真度"""
        logger.info(f"Measuring fteliation: {layer_i} → {layer_j}")
        
        # 获取态
        L_i = self.eml_states.get(layer_i)
        L_j = self.eml_states.get(layer_j)
        
        if L_i is None or L_j is None:
            # 创建默认态
            L_i = EMLState(
                name=layer_i,
                vector=np.array([1.0, 0.0], dtype=np.complex128),
                phase=0.0,
                layer=layer_i
            )
            L_j = EMLState(
                name=layer_j,
                vector=np.array([0.0, 1.0], dtype=np.complex128),
                phase=math.pi / 4,
                layer=layer_j
            )
        
        # 获取算子
        eml_op = self.eml_operators.get(eml_operator_name) if eml_operator_name else None
        
        # 计算保真度
        fidelity = self.compute_fidelity(L_i, L_j, eml_op)
        
        # 检查
        is_lossless = self.check_lossless_fteliation(fidelity)
        is_acceptable = fidelity >= 0.9
        warning = self.information_loss_warning(fidelity)
        information_loss = 1.0 - fidelity
        
        result = FidelityResult(
            fidelity=fidelity,
            is_lossless=is_lossless,
            is_acceptable=is_acceptable,
            information_loss=information_loss,
            warning=warning,
            layer_pair=(layer_i, layer_j)
        )
        
        self.fidelity_history.append(result)
        logger.info(f"  F({layer_i}, {layer_j}) = {fidelity:.4f}")
        if warning:
            logger.warning(f"  {warning}")
        
        return result
    
    def measure_all_layers(self) -> List[FidelityResult]:
        """测量所有层间流贯"""
        results = []
        layers = ["L1", "L2", "L3", "L4", "L5"]
        
        for i in range(len(layers) - 1):
            result = self.measure_fteliation(layers[i], layers[i+1])
            results.append(result)
        
        return results
    
    def compute_average_fidelity(self, layer_prefix: str = "") -> float:
        """计算平均保真度"""
        relevant = [
            r for r in self.fidelity_history 
            if r.layer_pair[0].startswith(layer_prefix) or not layer_prefix
        ]
        
        if not relevant:
            return 0.0
        
        return sum(r.fidelity for r in relevant) / len(relevant)
    
    def detect_fidelity_degradation(self, window: int = 10) -> List[str]:
        """检测保真度退化"""
        warnings = []
        
        if len(self.fidelity_history) < window:
            return warnings
        
        recent = self.fidelity_history[-window:]
        for i, result in enumerate(recent):
            if result.fidelity < 0.8:
                warnings.append(
                    f"Layer {result.layer_pair}: F={result.fidelity:.4f} < 0.8"
                )
            
            # 检查连续下降
            if i > 0 and recent[i].fidelity < recent[i-1].fidelity - 0.1:
                warnings.append(
                    f"Significant drop at layer {result.layer_pair}: "
                    f"{recent[i-1].fidelity:.4f} → {result.fidelity:.4f}"
                )
        
        return warnings
    
    def get_layer_fidelity_profile(self) -> Dict[str, float]:
        """获取层的保真度配置"""
        layers = ["L1", "L2", "L3", "L4", "L5"]
        profile = {}
        
        for i, layer in enumerate(layers):
            # 计算该层作为源和目标的平均保真度
            source_results = [r for r in self.fidelity_history if r.layer_pair[0] == layer]
            target_results = [r for r in self.fidelity_history if r.layer_pair[1] == layer]
            
            source_avg = sum(r.fidelity for r in source_results) / len(source_results) if source_results else 1.0
            target_avg = sum(r.fidelity for r in target_results) / len(target_results) if target_results else 1.0
            
            profile[layer] = (source_avg + target_avg) / 2
        
        return profile
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        avg_fidelity = self.compute_average_fidelity()
        return {
            "registered_states": len(self.eml_states),
            "registered_operators": len(self.eml_operators),
            "fidelity_history_entries": len(self.fidelity_history),
            "average_fidelity": avg_fidelity,
            "lossless_count": sum(1 for r in self.fidelity_history if r.is_lossless),
            "warning_count": sum(1 for r in self.fidelity_history if r.warning)
        }


# 单例访问
def get_fidelity_measurer() -> FteliocityFidelityMeasurer:
    """获取流贯保真度测量器单例"""
    return FteliocityFidelityMeasurer()


if __name__ == "__main__":
    # 测试流贯保真度测量器
    print("=" * 60)
    print("M92: FteliocityFidelityMeasurer - 流贯保真度测量器测试")
    print("=" * 60)
    
    measurer = get_fidelity_measurer()
    
    # 注册EML态
    print("\n[测试 1] 注册EML态")
    measurer.register_state(EMLState("L1", np.array([1.0, 0.0], dtype=np.complex128), 0.0, "L1"))
    measurer.register_state(EMLState("L2", np.array([0.7, 0.7], dtype=np.complex128), math.pi/6, "L2"))
    measurer.register_state(EMLState("L3", np.array([0.5, 0.8], dtype=np.complex128), math.pi/4, "L3"))
    print(f"  注册了 {len(measurer.eml_states)} 个EML态")
    
    # 测试用例 2: 层间保真度测量
    print("\n[测试 2] 层间保真度测量")
    result12 = measurer.measure_fteliation("L1", "L2")
    print(f"  F(L1, L2) = {result12.fidelity:.4f}")
    print(f"  无损: {result12.is_lossless}")
    print(f"  可接受: {result12.is_acceptable}")
    
    result23 = measurer.measure_fteliation("L2", "L3", "fire")
    print(f"  F(L2, L3) = {result23.fidelity:.4f}")
    
    # 测试用例 3: 使用五行算子
    print("\n[测试 3] 五行算子流贯")
    for op_name in ["water", "fire", "wood", "metal", "earth"]:
        result = measurer.measure_fteliation("L1", "L3", op_name)
        print(f"  {op_name}: F = {result.fidelity:.4f}")
    
    # 测试用例 4: 所有层测量
    print("\n[测试 4] 所有层间测量")
    all_results = measurer.measure_all_layers()
    for r in all_results:
        print(f"  {r.layer_pair[0]} → {r.layer_pair[1]}: F = {r.fidelity:.4f}")
    
    # 测试用例 5: 保真度配置
    print("\n[测试 5] 层保真度配置")
    profile = measurer.get_layer_fidelity_profile()
    for layer, fidelity in profile.items():
        print(f"  {layer}: {fidelity:.4f}")
    
    # 测试用例 6: 状态查询
    print("\n[测试 6] 状态查询")
    status = measurer.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("M92 测试完成！")
    print("=" * 60)
