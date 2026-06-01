"""
M220 Critical Jinling Init — 临界金灵球初始化
================================================

理论来源: "合道初态" — 复合体理学
核心概念: Wigner半圆谱初始化, 临界金灵球, E/I平衡, β-rewire收敛
定理编号: T252 (合道初态定理)

架构概述:
    CriticalJinlingInitializer 实现 Wigner 半圆律指导下的金灵球网络初始化,
    使得邻接矩阵谱半径 ρ ≈ 2α, 处于临界态。
    临界态初始化的网络达到稳态所需 β-rewire 次数显著少于随机初始化。

    JinlingSphereAdapter 为 M191 JinlingSphereEngine 提供 init_mode="critical" 支持。

数学基础:
    - Wigner半圆律: ρ(λ) = (2/(πR²))·√(R²-λ²), |λ|≤R, R=2α
    - 临界态: 谱半径 ρ ≈ 2α (容差内), E/I平衡比 ≈ inhib_ratio
    - 金灵球节点: 𝒥_i = (I_int, Port, χ), 内禀相位 θ_i ∈ [0, 2π)

Author: Kou Dou Ma (寇豆码) — 太乙AGI Team
Version: v7.32c
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# 核心数据结构
# ---------------------------------------------------------------------------

@dataclass
class CriticalInitConfig:
    """临界初始化配置

    参数说明:
      n_nodes: 金灵球节点数
      sparsity: 连接概率 (0,1)
      inhib_ratio: 抑制性连接比例
      weight_std: α参数, 权重标准差
      spectral_tolerance: 谱半径容差 (相对误差)
      port_mask: N₈端口掩码 (8端口)
    """
    n_nodes: int = 64
    sparsity: float = 0.15
    inhib_ratio: float = 0.20
    weight_std: float = 0.1
    spectral_tolerance: float = 0.3
    port_mask: int = 0xFF  # N₈端口掩码(8端口)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "n_nodes": self.n_nodes,
            "sparsity": self.sparsity,
            "inhib_ratio": self.inhib_ratio,
            "weight_std": self.weight_std,
            "spectral_tolerance": self.spectral_tolerance,
            "port_mask": self.port_mask,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CriticalInitConfig":
        """从字典反序列化"""
        return cls(
            n_nodes=data.get("n_nodes", 64),
            sparsity=data.get("sparsity", 0.15),
            inhib_ratio=data.get("inhib_ratio", 0.20),
            weight_std=data.get("weight_std", 0.1),
            spectral_tolerance=data.get("spectral_tolerance", 0.3),
            port_mask=data.get("port_mask", 0xFF),
        )


@dataclass
class JinlingNode:
    """金灵球节点 𝒥_i = (I_int, Port, χ)

    内禀量:
      phase: 内禀相位 θ_i ∈ [0, 2π)
      modulus: 内禀模 m_i
      port_mask: 端口掩码 (N₈)
      node_type: 兴奋性(excitatory)/抑制性(inhibitory)
    """
    node_id: str
    phase: float          # 内禀相位 θ_i ∈ [0, 2π)
    modulus: float        # 内禀模 m_i
    port_mask: int        # 端口掩码
    node_type: str = "excitatory"  # excitatory/inhibitory

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "node_id": self.node_id,
            "phase": self.phase,
            "modulus": self.modulus,
            "port_mask": self.port_mask,
            "node_type": self.node_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JinlingNode":
        """从字典反序列化"""
        return cls(
            node_id=data["node_id"],
            phase=data["phase"],
            modulus=data["modulus"],
            port_mask=data.get("port_mask", 0xFF),
            node_type=data.get("node_type", "excitatory"),
        )


@dataclass
class CriticalInitResult:
    """临界初始化结果

    包含邻接矩阵、节点列表、特征值、谱半径等关键指标。
    passes_spectral_check 表示谱半径是否在容差范围内。
    """
    adjacency: np.ndarray         # 邻接矩阵
    nodes: List[JinlingNode]       # 金灵球节点
    eigenvalues: np.ndarray       # 特征值
    spectral_radius: float        # 谱半径
    expected_radius: float        # 预期谱半径 2α
    ei_balance: float             # E/I平衡比
    sparsity_actual: float        # 实际稀疏度
    passes_spectral_check: bool   # 谱半径校验

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典 (ndarray转为list)"""
        return {
            "adjacency": self.adjacency.tolist(),
            "nodes": [n.to_dict() for n in self.nodes],
            "eigenvalues": self.eigenvalues.tolist(),
            "spectral_radius": self.spectral_radius,
            "expected_radius": self.expected_radius,
            "ei_balance": self.ei_balance,
            "sparsity_actual": self.sparsity_actual,
            "passes_spectral_check": self.passes_spectral_check,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CriticalInitResult":
        """从字典反序列化"""
        return cls(
            adjacency=np.array(data["adjacency"]),
            nodes=[JinlingNode.from_dict(n) for n in data["nodes"]],
            eigenvalues=np.array(data["eigenvalues"]),
            spectral_radius=data["spectral_radius"],
            expected_radius=data["expected_radius"],
            ei_balance=data["ei_balance"],
            sparsity_actual=data["sparsity_actual"],
            passes_spectral_check=data["passes_spectral_check"],
        )


# ---------------------------------------------------------------------------
# CriticalJinlingInitializer — 临界金灵球初始化器
# ---------------------------------------------------------------------------

class CriticalJinlingInitializer:
    """临界金灵球初始化器

    执行 Wigner 半圆谱初始化:
      1. 生成 n_nodes 个 JinlingNode, phase ∈ [0, 2π), modulus ∈ N(1, 0.2)
      2. 以 sparsity 概率生成边, 权重 N(0, α), inhib_ratio 比例取负
      3. 计算邻接矩阵特征值, 验证谱半径 ≈ 2α
      4. 返回 CriticalInitResult

    核心定理 T252: 临界初始化 → 谱半径ρ≈2α → 达稳态β-rewire次数显著少于随机初始化
    """

    def __init__(self, config: CriticalInitConfig) -> None:
        """初始化

        Args:
            config: 临界初始化配置
        """
        self.config = config
        self._rng = np.random.default_rng()

    def initialize(self) -> CriticalInitResult:
        """执行Wigner半圆谱初始化

        Returns:
            CriticalInitResult 包含邻接矩阵、节点、特征值等
        """
        n = self.config.n_nodes
        alpha = self.config.weight_std

        # Step 1: 生成金灵球节点
        nodes: List[JinlingNode] = []
        n_inhib = int(n * self.config.inhib_ratio)

        for i in range(n):
            phase = self._rng.uniform(0, 2 * np.pi)
            modulus = float(np.clip(self._rng.normal(1.0, 0.2), 0.1, 3.0))
            node_type = "inhibitory" if i < n_inhib else "excitatory"
            node = JinlingNode(
                node_id=f"J-{uuid.uuid4().hex[:6]}",
                phase=phase,
                modulus=modulus,
                port_mask=self.config.port_mask,
                node_type=node_type,
            )
            nodes.append(node)

        # Step 2: 生成邻接矩阵 (Erdos-Renyi + 临界权重)
        adjacency = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            for j in range(i + 1, n):
                if self._rng.random() < self.config.sparsity:
                    # 权重 ~ N(0, α)
                    weight = float(self._rng.normal(0, alpha))
                    # 抑制性连接取负
                    if nodes[i].node_type == "inhibitory" or nodes[j].node_type == "inhibitory":
                        weight = -abs(weight)
                    adjacency[i, j] = weight
                    adjacency[j, i] = weight

        # Step 3: 计算特征值和谱半径
        eigenvalues = np.linalg.eigvals(adjacency)
        spectral_radius = float(np.max(np.abs(eigenvalues)))
        expected_radius = 2.0 * alpha

        # 谱半径校验: ρ ≈ 2α (容差内)
        relative_error = abs(spectral_radius - expected_radius) / max(expected_radius, 1e-10)
        passes_spectral_check = relative_error <= self.config.spectral_tolerance

        # 如果不通过, 进行缩放修正 (保持Wigner半圆律结构)
        if not passes_spectral_check and spectral_radius > 0:
            scale = expected_radius / spectral_radius
            adjacency = adjacency * scale
            eigenvalues = np.linalg.eigvals(adjacency)
            spectral_radius = float(np.max(np.abs(eigenvalues)))
            relative_error = abs(spectral_radius - expected_radius) / max(expected_radius, 1e-10)
            passes_spectral_check = relative_error <= self.config.spectral_tolerance

        # 计算E/I平衡比
        excitatory_weights = []
        inhibitory_weights = []
        for i in range(n):
            for j in range(i + 1, n):
                w = adjacency[i, j]
                if w > 0:
                    excitatory_weights.append(w)
                elif w < 0:
                    inhibitory_weights.append(abs(w))

        e_sum = sum(excitatory_weights) if excitatory_weights else 0.0
        i_sum = sum(inhibitory_weights) if inhibitory_weights else 1.0
        ei_balance = e_sum / i_sum if i_sum > 0 else float("inf")

        # 计算实际稀疏度
        total_possible = n * (n - 1) / 2
        actual_edges = int(np.count_nonzero(adjacency) / 2)
        sparsity_actual = actual_edges / total_possible if total_possible > 0 else 0.0

        return CriticalInitResult(
            adjacency=adjacency,
            nodes=nodes,
            eigenvalues=eigenvalues,
            spectral_radius=spectral_radius,
            expected_radius=expected_radius,
            ei_balance=ei_balance,
            sparsity_actual=sparsity_actual,
            passes_spectral_check=passes_spectral_check,
        )

    def verify_wigner_semicircle(self, result: CriticalInitResult) -> Dict[str, Any]:
        """验证特征值分布是否符合Wigner半圆律

        Wigner半圆律: ρ(λ) = (2/(πR²))·√(R²-λ²), |λ|≤R, R=2α

        计算实际特征值分布与理论分布的KL散度。

        Args:
            result: 临界初始化结果

        Returns:
            Dict 包含验证结果和KL散度
        """
        alpha = self.config.weight_std
        R = 2.0 * alpha  # 半圆半径

        eigenvalues = result.eigenvalues.real
        n_bins = 50

        # 只考虑 |λ| ≤ R 范围内的特征值
        within = eigenvalues[np.abs(eigenvalues) <= R]
        if len(within) < 2:
            return {
                "passes": False,
                "kl_divergence": float("inf"),
                "reason": "特征值不在半圆范围内",
            }

        # 实际分布 (直方图归一化)
        hist_actual, bin_edges = np.histogram(within, bins=n_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

        # 理论分布: Wigner半圆
        # ρ(λ) = (2/(πR²))·√(R²-λ²)
        with np.errstate(invalid="ignore"):
            theoretical = (2.0 / (np.pi * R * R)) * np.sqrt(np.maximum(R * R - bin_centers ** 2, 0))

        # KL散度计算 (需要避免零概率)
        eps = 1e-10
        p = hist_actual + eps
        q = theoretical + eps
        p = p / p.sum()
        q = q / q.sum()
        kl_divergence = float(np.sum(p * np.log(p / q)))

        # 判断标准: KL散度 < 1.0 视为通过
        passes = kl_divergence < 1.0

        return {
            "passes": passes,
            "kl_divergence": kl_divergence,
            "spectral_radius": result.spectral_radius,
            "expected_radius": R,
            "eigenvalue_count": len(eigenvalues),
            "within_count": len(within),
            "interpretation": (
                f"KL散度={kl_divergence:.4f}, 特征值分布符合Wigner半圆律"
                if passes
                else f"KL散度={kl_divergence:.4f}, 偏离Wigner半圆律"
            ),
        }

    def compare_with_random(self, n_trials: int = 100) -> Dict[str, Any]:
        """P1预言验证: 临界初始化 vs 随机初始化

        生成临界初始化和随机初始化的图各 n_trials 个,
        计算各自达到稳态所需 β-rewire 次数, t-test 比较。

        稳态判定: Laplacian history 收敛 (连续5步变化 < 0.01)。

        Args:
            n_trials: 重复实验次数

        Returns:
            Dict 包含比较结果
        """
        critical_rewire_counts: List[int] = []
        random_rewire_counts: List[int] = []

        for _ in range(n_trials):
            # 临界初始化
            crit_result = self.initialize()
            crit_rewire = self._simulate_rewire_to_steady(crit_result.adjacency)
            critical_rewire_counts.append(crit_rewire)

            # 随机初始化 (均匀权重, 不做谱半径修正)
            rand_adj = self._generate_random_adjacency()
            rand_rewire = self._simulate_rewire_to_steady(rand_adj)
            random_rewire_counts.append(rand_rewire)

        # 统计
        critical_mean = float(np.mean(critical_rewire_counts))
        random_mean = float(np.mean(random_rewire_counts))

        # t-test
        if len(critical_rewire_counts) > 1 and len(random_rewire_counts) > 1:
            from scipy import stats as sp_stats
            t_stat, p_value = sp_stats.ttest_ind(
                critical_rewire_counts, random_rewire_counts, equal_var=False
            )
        else:
            t_stat, p_value = 0.0, 1.0

        # P1预言: 临界初始化达稳态次数 < 随机初始化
        prediction_passes = critical_mean < random_mean and p_value < 0.05

        return {
            "critical_mean": critical_mean,
            "random_mean": random_mean,
            "critical_std": float(np.std(critical_rewire_counts)),
            "random_std": float(np.std(random_rewire_counts)),
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "prediction_passes": prediction_passes,
            "n_trials": n_trials,
        }

    def _generate_random_adjacency(self) -> np.ndarray:
        """生成随机邻接矩阵 (均匀权重, 不做谱半径修正)"""
        n = self.config.n_nodes
        adjacency = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            for j in range(i + 1, n):
                if self._rng.random() < self.config.sparsity:
                    # 均匀权重 (非临界)
                    weight = float(self._rng.uniform(-1, 1))
                    adjacency[i, j] = weight
                    adjacency[j, i] = weight

        return adjacency

    def _simulate_rewire_to_steady(self, adjacency: np.ndarray, max_steps: int = 500) -> int:
        """模拟 β-rewire 直到稳态

        稳态判定: Laplacian history 连续5步变化 < 0.01

        Args:
            adjacency: 初始邻接矩阵
            max_steps: 最大rewire步数

        Returns:
            达到稳态所需的rewire步数
        """
        adj = adjacency.copy()
        n = adj.shape[0]
        laplacian_history: List[float] = []
        steady_window = 5
        threshold = 0.01

        for step in range(max_steps):
            # 计算Laplacian矩阵的Frobenius范数
            degree = np.sum(np.abs(adj), axis=1)
            laplacian = np.diag(degree) - adj
            lap_norm = float(np.linalg.norm(laplacian, "fro"))
            laplacian_history.append(lap_norm)

            # 稳态检测
            if len(laplacian_history) >= steady_window + 1:
                recent = laplacian_history[-steady_window - 1:]
                changes = [abs(recent[i + 1] - recent[i]) for i in range(len(recent) - 1)]
                if all(c < threshold for c in changes):
                    return step + 1

            # β-rewire: 随机断开一条边, 重新连接
            nonzero_indices = np.argwhere(adj != 0)
            if len(nonzero_indices) == 0:
                return step + 1

            idx = self._rng.integers(0, len(nonzero_indices))
            i, j = nonzero_indices[idx]
            adj[i, j] = 0
            adj[j, i] = 0

            # 随机连接新边
            new_i, new_j = self._rng.integers(0, n, size=2)
            if new_i != new_j:
                weight = float(self._rng.normal(0, self.config.weight_std))
                adj[new_i, new_j] = weight
                adj[new_j, new_i] = weight

        return max_steps


# ---------------------------------------------------------------------------
# JinlingSphereAdapter — 适配M191 JinlingSphereEngine
# ---------------------------------------------------------------------------

class JinlingSphereAdapter:
    """适配 M191 JinlingSphereEngine

    为 M191 添加 init_mode="critical" 支持。
    当 init_mode="critical" 时, 用 CriticalJinlingInitializer 替代默认随机初始化。
    """

    def __init__(self, config: Optional[CriticalInitConfig] = None) -> None:
        """初始化适配器

        Args:
            config: 临界初始化配置, 若为None则使用默认配置
        """
        self.config = config or CriticalInitConfig()

    def upgrade_jinling_sphere(self, engine: Any, init_mode: str = "critical") -> Dict[str, Any]:
        """为M191添加init_mode="critical"支持

        当init_mode="critical"时, 用CriticalJinlingInitializer替代默认随机初始化。

        Args:
            engine: M191 JinlingSphereEngine 实例
            init_mode: 初始化模式 ("critical" | "random")

        Returns:
            Dict 包含初始化结果和模式信息
        """
        if init_mode == "critical":
            initializer = CriticalJinlingInitializer(self.config)
            result = initializer.initialize()

            # 将临界初始化结果注入到engine
            if hasattr(engine, "adjacency_matrix"):
                engine.adjacency_matrix = result.adjacency
            if hasattr(engine, "nodes"):
                engine.nodes = result.nodes
            if hasattr(engine, "spectral_radius"):
                engine.spectral_radius = result.spectral_radius

            return {
                "init_mode": "critical",
                "spectral_radius": result.spectral_radius,
                "expected_radius": result.expected_radius,
                "passes_spectral_check": result.passes_spectral_check,
                "ei_balance": result.ei_balance,
                "sparsity_actual": result.sparsity_actual,
            }
        else:
            # 默认随机初始化
            return {
                "init_mode": "random",
                "note": "使用M191默认随机初始化",
            }


# ---------------------------------------------------------------------------
# 模块级定理验证入口
# ---------------------------------------------------------------------------

def verify_theorem_t252(n_trials: int = 100) -> Dict[str, Any]:
    """验证 T252 合道初态定理 (模块级入口)

    定理内容: 临界初始化的谱半径ρ≈2α(容差内) → 达稳态β-rewire次数显著少于随机初始化

    验证方法:
      1. 100次重复实验
      2. 对比临界初始化 vs 随机初始化的rewire次数
      3. t-test检验显著性

    Args:
        n_trials: 重复实验次数

    Returns:
        定理验证结果
    """
    config = CriticalInitConfig()
    initializer = CriticalJinlingInitializer(config)

    # 先验证谱半径
    result = initializer.initialize()
    spectral_passes = result.passes_spectral_check

    # 再对比rewire次数
    comparison = initializer.compare_with_random(n_trials=n_trials)

    return {
        "theorem": "T252",
        "passes": spectral_passes and comparison["prediction_passes"],
        "spectral_check": {
            "passes": spectral_passes,
            "spectral_radius": result.spectral_radius,
            "expected_radius": result.expected_radius,
        },
        "rewire_comparison": comparison,
        "interpretation": (
            "T252成立: 临界初始化谱半径≈2α, 达稳态β-rewire次数显著少于随机初始化"
            if spectral_passes and comparison["prediction_passes"]
            else "T252验证不通过, 需检查参数或增加实验次数"
        ),
    }


# ---------------------------------------------------------------------------
# 模块导出
# ---------------------------------------------------------------------------

__all__ = [
    "CriticalInitConfig",
    "JinlingNode",
    "CriticalInitResult",
    "CriticalJinlingInitializer",
    "JinlingSphereAdapter",
    "verify_theorem_t252",
]
