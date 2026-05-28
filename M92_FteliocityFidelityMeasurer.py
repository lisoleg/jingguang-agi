"""
M92: FteliocityFidelityMeasurer - 流贯保真度测量器
实现 T37: 流贯保真度 F 测量

核心原理：
- F(L_i, L_j) = |<L_i| EML |L_j>|² / (|L_i|² * |L_j|²)
- 无损流贯：F = 1
- 信息损耗警告：F < 0.9

v7.31升级：意图-理解保真度
- 新增 intention_understanding_fidelity：意图-理解对齐保真度 F = ⟨m,m̂⟩/(‖m‖‖m̂‖)
- 新增 trust_score：信任度 T = F̄·σ(CRD_activity)
- 新增 conjugate_pair_check：共轭对一致性检测
- 新增 complex_stability_measure：复合体稳定性 Δ_C ~ ε²
- 新增 _intention_fidelity_history 属性
- 保留原有 measure_fteliation 等方法不变

Author: 太乙AGI 7.0 Team
Upgrade: v7.31 — 寇豆码
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


@dataclass
class IntentionFidelityResult:
    """
    意图-理解保真度结果 — v7.31 新增
    
    记录意图向量与理解向量之间的对齐保真度
    """
    fidelity: float                # F = ⟨m,m̂⟩/(‖m‖‖m̂‖)
    intention_norm: float          # ‖m‖
    understanding_norm: float      # ‖m̂‖
    inner_product: float           # ⟨m, m̂⟩
    is_aligned: bool               # F >= alignment_threshold
    alignment_threshold: float     # 对齐阈值
    timestamp: float = 0.0


@dataclass
class TrustScoreResult:
    """
    信任度计算结果 — v7.31 新增
    
    T = F̄ · σ(CRD_activity)
    其中 F̄ 是保真度历史均值，σ 是CRD活跃度的sigmoid映射
    """
    trust_score: float             # T
    avg_fidelity: float            # F̄
    crd_activity_sigma: float      # σ(CRD_activity)
    crd_activity_raw: float        # CRD原始活跃度
    is_trustworthy: bool           # T >= trust_threshold
    trust_threshold: float         # 信任阈值
    timestamp: float = 0.0


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
        
        # ===== v7.31 新增属性 =====
        # 意图-理解保真度历史
        self._intention_fidelity_history: List[IntentionFidelityResult] = []
        # 信任度历史
        self._trust_score_history: List[TrustScoreResult] = []
    
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
    
    # ==================== 原有方法（完全保留） ====================

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
            "warning_count": sum(1 for r in self.fidelity_history if r.warning),
        }

    # ==================== v7.31 新增方法 ====================

    def intention_understanding_fidelity(
        self,
        intention_vector: np.ndarray,
        understanding_vector: np.ndarray,
        alignment_threshold: float = 0.85,
    ) -> IntentionFidelityResult:
        """
        意图-理解对齐保真度 — v7.31 新增

        计算意图向量 m 与理解向量 m̂ 之间的对齐保真度：
        F = ⟨m, m̂⟩ / (‖m‖ · ‖m̂‖)

        这是余弦相似度在意图-理解空间中的推广。
        当 F = 1 时，理解完全对齐意图；当 F = 0 时，理解与意图正交。

        Args:
            intention_vector: 意图向量 m（numpy数组）
            understanding_vector: 理解向量 m̂（numpy数组）
            alignment_threshold: 对齐判定阈值（默认0.85）

        Returns:
            IntentionFidelityResult: 意图-理解保真度结果
        """
        import time as _time

        m = np.array(intention_vector, dtype=np.float64).flatten()
        m_hat = np.array(understanding_vector, dtype=np.float64).flatten()

        # 维度对齐：取较短维度，不足部分补零
        max_dim = max(len(m), len(m_hat))
        if len(m) < max_dim:
            m = np.pad(m, (0, max_dim - len(m)))
        if len(m_hat) < max_dim:
            m_hat = np.pad(m_hat, (0, max_dim - len(m_hat)))

        # 计算内积 ⟨m, m̂⟩
        inner = float(np.dot(m, m_hat))

        # 计算范数
        norm_m = float(np.linalg.norm(m))
        norm_m_hat = float(np.linalg.norm(m_hat))

        # 计算保真度 F = ⟨m, m̂⟩ / (‖m‖ · ‖m̂‖)
        if norm_m < 1e-10 or norm_m_hat < 1e-10:
            fidelity = 0.0
        else:
            fidelity = inner / (norm_m * norm_m_hat)
            # 裁剪到[-1, 1]
            fidelity = max(-1.0, min(1.0, fidelity))

        is_aligned = fidelity >= alignment_threshold

        result = IntentionFidelityResult(
            fidelity=round(fidelity, 6),
            intention_norm=round(norm_m, 6),
            understanding_norm=round(norm_m_hat, 6),
            inner_product=round(inner, 6),
            is_aligned=is_aligned,
            alignment_threshold=alignment_threshold,
            timestamp=_time.time(),
        )

        self._intention_fidelity_history.append(result)
        logger.info(
            f"Intention-Understanding Fidelity: F={fidelity:.4f}, "
            f"aligned={is_aligned}"
        )
        return result

    def trust_score(
        self,
        fidelity_history: Optional[List[float]] = None,
        crd_activity: float = 0.5,
        trust_threshold: float = 0.6,
    ) -> TrustScoreResult:
        """
        信任度计算 — v7.31 新增

        T = F̄ · σ(CRD_activity)

        其中：
        - F̄ 是保真度历史均值（来自 _intention_fidelity_history 或传入）
        - σ(x) = 1 / (1 + e^{-k(x - x₀)}) 是CRD活跃度的sigmoid映射
        - k = 5.0, x₀ = 0.5 是sigmoid参数

        信任度高意味着：保真度好且CRD活跃度适中（既不僵化也不过活跃）

        Args:
            fidelity_history: 保真度历史列表（None则使用内部历史）
            crd_activity: CRD活跃度 [0, 1]（0=僵化, 1=过度活跃, 0.5=适中）
            trust_threshold: 信任判定阈值

        Returns:
            TrustScoreResult: 信任度计算结果
        """
        import time as _time

        # 计算保真度均值 F̄
        if fidelity_history is not None:
            f_vals = fidelity_history
        elif self._intention_fidelity_history:
            f_vals = [r.fidelity for r in self._intention_fidelity_history]
        elif self.fidelity_history:
            f_vals = [r.fidelity for r in self.fidelity_history]
        else:
            f_vals = [1.0]  # 无历史时默认

        avg_fidelity = round(sum(f_vals) / max(1, len(f_vals)), 6)

        # sigmoid映射 CRD 活跃度
        # σ(x) = 1 / (1 + e^{-k(x - x₀)})
        k_sigmoid = 5.0
        x0_sigmoid = 0.5
        crd_sigma = 1.0 / (1.0 + math.exp(-k_sigmoid * (crd_activity - x0_sigmoid)))
        crd_sigma = round(crd_sigma, 6)

        # 信任度 T = F̄ · σ(CRD_activity)
        trust = round(avg_fidelity * crd_sigma, 6)

        is_trustworthy = trust >= trust_threshold

        result = TrustScoreResult(
            trust_score=trust,
            avg_fidelity=avg_fidelity,
            crd_activity_sigma=crd_sigma,
            crd_activity_raw=crd_activity,
            is_trustworthy=is_trustworthy,
            trust_threshold=trust_threshold,
            timestamp=_time.time(),
        )

        self._trust_score_history.append(result)
        logger.info(
            f"Trust Score: T={trust:.4f}, F̄={avg_fidelity:.4f}, "
            f"σ(CRD)={crd_sigma:.4f}, trustworthy={is_trustworthy}"
        )
        return result

    def conjugate_pair_check(
        self,
        norm_anchor: np.ndarray,
        expansion_engine: np.ndarray,
    ) -> Dict[str, Any]:
        """
        共轭对一致性检测 — v7.31 新增

        检测规范锚点（Norm Anchor, H）和展开引擎（Expansion Engine, A）
        是否构成有效的共轭对。

        共轭对条件：
        1. H·A = A·H（交换性测试，或足够接近）
        2. ‖H‖ 和 ‖A‖ 都非零
        3. H 提供稳定性（范数接近1），A 提供展开能力（范数适度）

        物理意义：
        - 规范锚点 H：提供认知稳定性（类似规范场）
        - 展开引擎 A：提供认知扩展能力（类似对称破缺）
        - 共轭对确保系统在稳定与展开之间保持平衡

        Args:
            norm_anchor: 规范锚点向量/矩阵 H
            expansion_engine: 展开引擎向量/矩阵 A

        Returns:
            共轭对检测结果字典
        """
        H = np.array(norm_anchor, dtype=np.float64)
        A = np.array(expansion_engine, dtype=np.float64)

        # 检测是否为矩阵（2D）
        is_matrix = H.ndim >= 2 and A.ndim >= 2

        if is_matrix:
            # 矩阵形式：检查交换性 H·A ≈ A·H
            HA = np.dot(H, A)
            AH = np.dot(A, H)
            commutator_diff = float(np.linalg.norm(HA - AH))
            commutator_norm = max(float(np.linalg.norm(HA)), float(np.linalg.norm(AH)), 1e-10)
            commutativity = round(1.0 - min(1.0, commutator_diff / commutator_norm), 6)
        else:
            # 向量形式：用外积近似
            H_flat = H.flatten()
            A_flat = A.flatten()
            max_dim = max(len(H_flat), len(A_flat))
            if len(H_flat) < max_dim:
                H_flat = np.pad(H_flat, (0, max_dim - len(H_flat)))
            if len(A_flat) < max_dim:
                A_flat = np.pad(A_flat, (0, max_dim - len(A_flat)))
            # 向量的逐元素乘法是交换的
            commutativity = 1.0

        # 范数检查
        h_norm = round(float(np.linalg.norm(H)), 6)
        a_norm = round(float(np.linalg.norm(A)), 6)
        h_nonzero = h_norm > 1e-10
        a_nonzero = a_norm > 1e-10

        # 稳定性检查：H 的范数应接近1（归一化后的稳定性锚点）
        stability_score = round(1.0 - min(1.0, abs(h_norm - 1.0)), 6) if h_nonzero else 0.0

        # 展开能力检查：A 的范数应适度（不过大也不过小）
        expansion_score = round(1.0 / (1.0 + abs(a_norm - 1.0)), 6) if a_nonzero else 0.0

        # 共轭对综合评分
        overall_score = round(
            0.3 * commutativity +
            0.3 * stability_score +
            0.2 * expansion_score +
            0.2 * (1.0 if h_nonzero and a_nonzero else 0.0),
            6,
        )

        is_conjugate_pair = overall_score >= 0.6

        return {
            'is_conjugate_pair': is_conjugate_pair,
            'overall_score': overall_score,
            'commutativity': commutativity,
            'stability_score': stability_score,
            'expansion_score': expansion_score,
            'h_norm': h_norm,
            'a_norm': a_norm,
            'h_nonzero': h_nonzero,
            'a_nonzero': a_nonzero,
            'interpretation': (
                '共轭对有效：规范锚点H提供稳定，展开引擎A提供扩展，'
                '二者构成平衡的共轭对' if is_conjugate_pair else
                '共轭对不足：H和A的稳定性/展开能力/交换性不满足共轭条件'
            ),
        }

    def complex_stability_measure(self, epsilon: float = 0.1) -> Dict[str, Any]:
        """
        复合体稳定性测量 — v7.31 新增

        Δ_C ~ ε²

        复合体稳定性与微扰ε的平方成正比：
        - ε小 → Δ_C极小 → 系统稳定
        - ε大 → Δ_C显著 → 系统不稳定

        这是结构稳定性理论在复合体理学中的体现：
        微小扰动不会导致系统行为的质变（ε²衰减保证）。

        Args:
            epsilon: 微扰参数 ε > 0

        Returns:
            复合体稳定性测量结果字典
        """
        epsilon = max(0.0, epsilon)
        delta_c = epsilon ** 2

        # 结合保真度历史的稳定性评估
        if self._intention_fidelity_history:
            recent_fidelities = [r.fidelity for r in self._intention_fidelity_history[-10:]]
            fidelity_variance = float(np.var(recent_fidelities)) if len(recent_fidelities) > 1 else 0.0
        elif self.fidelity_history:
            recent_fidelities = [r.fidelity for r in self.fidelity_history[-10:]]
            fidelity_variance = float(np.var(recent_fidelities)) if len(recent_fidelities) > 1 else 0.0
        else:
            fidelity_variance = 0.0

        # 综合稳定性 = 1 / (1 + Δ_C + σ²_F)
        # 其中 σ²_F 是保真度方差
        stability = round(1.0 / (1.0 + delta_c + fidelity_variance), 6)

        # 判定
        if stability > 0.8:
            level = 'highly_stable'
            description = '复合体高度稳定：微扰ε²衰减，保真度方差低'
        elif stability > 0.5:
            level = 'moderately_stable'
            description = '复合体中等稳定：微扰影响可控，保真度波动适中'
        else:
            level = 'unstable'
            description = '复合体不稳定：微扰影响显著或保真度波动大'

        return {
            'epsilon': epsilon,
            'delta_c': round(delta_c, 6),
            'stability': stability,
            'fidelity_variance': round(fidelity_variance, 6),
            'level': level,
            'description': description,
            'theorem': 'Δ_C ~ ε² — 复合体稳定性与微扰平方成正比',
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
    
    # ==================== v7.31 新功能测试 ====================
    print("\n" + "=" * 60)
    print("v7.31 意图-理解保真度 升级测试")
    print("=" * 60)

    print("\n[测试 7] intention_understanding_fidelity — 意图-理解对齐保真度")
    # 意图和理解高度对齐
    intention = np.array([1.0, 0.5, 0.3, 0.8])
    understanding_aligned = np.array([0.95, 0.48, 0.31, 0.78])
    iu_result = measurer.intention_understanding_fidelity(intention, understanding_aligned)
    print(f"  对齐保真度 F = {iu_result.fidelity:.4f}")
    print(f"  是否对齐: {iu_result.is_aligned}")
    print(f"  意图范数: {iu_result.intention_norm:.4f}")
    print(f"  理解范数: {iu_result.understanding_norm:.4f}")

    # 意图和理解不正交
    understanding_orthogonal = np.array([-0.3, 0.8, -0.5, 0.1])
    iu_ortho = measurer.intention_understanding_fidelity(intention, understanding_orthogonal)
    print(f"  正交保真度 F = {iu_ortho.fidelity:.4f}")
    print(f"  是否对齐: {iu_ortho.is_aligned}")

    print("\n[测试 8] trust_score — 信任度计算")
    trust = measurer.trust_score(crd_activity=0.5, trust_threshold=0.6)
    print(f"  信任度 T = {trust.trust_score:.4f}")
    print(f"  F̄ = {trust.avg_fidelity:.4f}")
    print(f"  σ(CRD) = {trust.crd_activity_sigma:.4f}")
    print(f"  是否可信: {trust.is_trustworthy}")

    # 低活跃度
    trust_low = measurer.trust_score(crd_activity=0.1)
    print(f"  低活跃度 T = {trust_low.trust_score:.4f}, σ(CRD) = {trust_low.crd_activity_sigma:.4f}")

    # 高活跃度
    trust_high = measurer.trust_score(crd_activity=0.9)
    print(f"  高活跃度 T = {trust_high.trust_score:.4f}, σ(CRD) = {trust_high.crd_activity_sigma:.4f}")

    print("\n[测试 9] conjugate_pair_check — 共轭对检测")
    H = np.array([[1.0, 0.0], [0.0, 1.0]])  # 单位矩阵（规范锚点）
    A = np.array([[1.0, 0.1], [0.1, 1.0]])  # 微扰矩阵（展开引擎）
    cp_result = measurer.conjugate_pair_check(H, A)
    print(f"  是否共轭对: {cp_result['is_conjugate_pair']}")
    print(f"  综合评分: {cp_result['overall_score']}")
    print(f"  交换性: {cp_result['commutativity']}")
    print(f"  稳定性: {cp_result['stability_score']}")
    print(f"  展开能力: {cp_result['expansion_score']}")

    print("\n[测试 10] complex_stability_measure — 复合体稳定性")
    for eps in [0.01, 0.1, 0.5, 1.0]:
        cs = measurer.complex_stability_measure(epsilon=eps)
        print(f"  ε={eps}: Δ_C={cs['delta_c']:.6f}, stability={cs['stability']:.4f}, level={cs['level']}")

    print("\n" + "=" * 60)
    print("M92 v7.31 测试完成！")
    print("=" * 60)
