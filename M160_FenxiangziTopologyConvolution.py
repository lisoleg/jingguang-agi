"""
M160 芬芳香子拓扑卷积 — FenxiangziTopologyConvolution
======================================================
论文来源：六元对偶卷积架构，方程Eq4，定理T2.4
核心定理：T127（拓扑重构定理）— 欧氏邻域替换为18类芬芳香子邻域
对偶轴：欧氏格子 <-> 非欧密堆（如十二面体）
与M143(芬芳香子)桥接
"""

from __future__ import annotations

import math
import random
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class FenxiangziType(Enum):
    """18种芬芳香子拓扑类型"""
    # 柏拉图正多面体 (5种)
    TETRAHEDRON = "tetrahedron"          # 正四面体
    OCTAHEDRON = "octahedron"            # 正八面体
    CUBE = "cube"                        # 正六面体(立方体)
    DODECAHEDRON = "dodecahedron"        # 正十二面体
    ICOSAHEDRON = "icosahedron"          # 正二十面体
    # 阿基米德半正多面体 (7种)
    CUBOCTAHEDRON = "cuboctahedron"      # 截半立方体
    TRUNCATED_TETRA = "truncated_tetra"  # 截角四面体
    TRUNCATED_CUBE = "truncated_cube"    # 截角立方体
    TRUNCATED_OCTA = "truncated_octa"    # 截角八面体
    RHOMBICUBOCTA = "rhombicubocta"      # 菱形截半立方体
    TRUNCATED_CUBOCTA = "truncated_cubocta"  # 截角截半立方体
    SNUB_CUBE = "snub_cube"             # 扭歪立方体
    # 拓扑变体 (6种)
    TORUS = "torus"                      # 环面
    KLEIN_BOTTLE = "klein_bottle"        # 克莱因瓶
    MOBIUS = "mobius"                    # 莫比乌斯带
    PROJECTIVE_PLANE = "projective_plane"  # 射影平面
    HYPERBOLIC = "hyperbolic"            # 双曲空间
    FRACTAL = "fractal"                  # 分形拓扑


# 每种拓扑类型的邻域大小（用于卷积核扩展）
FENXIANGZI_NEIGHBOR_COUNTS: Dict[FenxiangziType, int] = {
    FenxiangziType.TETRAHEDRON: 4,
    FenxiangziType.OCTAHEDRON: 6,
    FenxiangziType.CUBE: 8,
    FenxiangziType.DODECAHEDRON: 12,
    FenxiangziType.ICOSAHEDRON: 20,
    FenxiangziType.CUBOCTAHEDRON: 12,
    FenxiangziType.TRUNCATED_TETRA: 12,
    FenxiangziType.TRUNCATED_CUBE: 24,
    FenxiangziType.TRUNCATED_OCTA: 24,
    FenxiangziType.RHOMBICUBOCTA: 24,
    FenxiangziType.TRUNCATED_CUBOCTA: 48,
    FenxiangziType.SNUB_CUBE: 24,
    FenxiangziType.TORUS: 8,
    FenxiangziType.KLEIN_BOTTLE: 8,
    FenxiangziType.MOBIUS: 4,
    FenxiangziType.PROJECTIVE_PLANE: 6,
    FenxiangziType.HYPERBOLIC: 16,
    FenxiangziType.FRACTAL: 0,  # 分形拓扑邻域无限
}


@dataclass
class FenxiangziTopologyState:
    """芬芳香子拓扑卷积状态"""
    topology_type: FenxiangziType = FenxiangziType.DODECAHEDRON
    neighbor_count: int = 12
    curvature: float = 0.0  # 曲率：0=欧氏, >0=球面, <0=双曲
    total_convolutions: int = 0
    last_signal_length: int = 0
    last_kernel_length: int = 0
    m143_bridge_active: bool = True  # M143桥接状态
    created_at: float = field(default_factory=time.time)


class FenxiangziTopologyConvolution:
    """
    芬芳香子拓扑卷积 (Eq4/T2.4)

    定理T127：拓扑重构定理
    欧氏邻域替换为18类芬芳香子邻域，
    在非欧拓扑空间上重新定义卷积。

    标准卷积在欧氏格子上平移不变，
    芬芳香子卷积在非欧密铺上具有拓扑不变性。

    对偶轴：欧氏格子 <-> 非欧密堆
    如正十二面体密铺代替正方形格子。
    """

    _instance: Optional[FenxiangziTopologyConvolution] = None

    def __init__(self,
                 topology_type: FenxiangziType = FenxiangziType.DODECAHEDRON
                 ) -> None:
        self._state = FenxiangziTopologyState(
            topology_type=topology_type,
            neighbor_count=FENXIANGZI_NEIGHBOR_COUNTS.get(topology_type, 8),
        )
        self._update_curvature()

    def _update_curvature(self) -> None:
        """根据拓扑类型更新曲率"""
        t = self._state.topology_type
        if t in (FenxiangziType.HYPERBOLIC, FenxiangziType.FRACTAL):
            self._state.curvature = -1.0
        elif t in (FenxiangziType.TORUS, FenxiangziType.KLEIN_BOTTLE,
                   FenxiangziType.MOBIUS, FenxiangziType.PROJECTIVE_PLANE):
            self._state.curvature = 0.0
        else:
            # 柏拉图和阿基米德多面体对应正曲率
            self._state.curvature = 1.0

    @classmethod
    def get_instance(cls,
                     topology_type: FenxiangziType = FenxiangziType.DODECAHEDRON
                     ) -> FenxiangziTopologyConvolution:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(topology_type=topology_type)
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """重置单例（仅测试用）"""
        cls._instance = None

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "module": "M160_FenxiangziTopologyConvolution",
            "topology_type": self._state.topology_type.value,
            "neighbor_count": self._state.neighbor_count,
            "curvature": self._state.curvature,
            "total_convolutions": self._state.total_convolutions,
            "last_signal_length": self._state.last_signal_length,
            "last_kernel_length": self._state.last_kernel_length,
            "m143_bridge_active": self._state.m143_bridge_active,
            "created_at": self._state.created_at,
        }

    def _topology_weight(self, distance: int, topology: FenxiangziType
                         ) -> float:
        """
        非欧拓扑邻域权重

        欧氏格子权重均匀，非欧密铺权重由拓扑结构决定。
        球面拓扑：远处衰减快
        双曲拓扑：远处衰减慢
        """
        curvature = self._state.curvature
        if abs(curvature) < 1e-10:
            # 欧氏：均匀权重
            return 1.0
        elif curvature > 0:
            # 球面：高斯衰减
            return math.exp(-0.5 * distance * distance * abs(curvature))
        else:
            # 双曲：慢衰减
            return 1.0 / (1.0 + distance * abs(curvature))

    def fenxiangzi_convolve(self, signal: List[float],
                            topology_type: FenxiangziType
                            ) -> Dict[str, Any]:
        """
        芬芳香子拓扑卷积 (Eq4)

        定理T127：拓扑重构定理
        将卷积核的邻域从欧氏格子替换为芬芳香子拓扑邻域。

        1. 根据拓扑类型确定邻域大小
        2. 计算非欧邻域权重
        3. 加权卷积

        Args:
            signal: 输入信号序列
            topology_type: 芬芳香子拓扑类型

        Returns:
            包含result和metadata的字典
        """
        self._state.topology_type = topology_type
        self._state.neighbor_count = FENXIANGZI_NEIGHBOR_COUNTS.get(
            topology_type, 8
        )
        self._update_curvature()

        n = len(signal)
        if n == 0:
            return {"result": [], "metadata": {"error": "空信号"}}

        # 根据邻域大小构造非欧卷积核
        # 欧氏核是均匀的[1/n]，
        # 非欧核由拓扑权重决定
        neighbor = self._state.neighbor_count
        if neighbor <= 0:
            neighbor = min(n, 8)  # 分形拓扑回退

        half_w = neighbor // 2
        kernel_size = 2 * half_w + 1
        weights: List[float] = []
        for d in range(-half_w, half_w + 1):
            w = self._topology_weight(abs(d), topology_type)
            weights.append(w)

        # 归一化
        w_sum = sum(weights)
        if w_sum > 1e-12:
            weights = [w / w_sum for w in weights]

        # 加权卷积
        result: List[float] = []
        for i in range(n):
            acc = 0.0
            for j, w in enumerate(weights):
                s_idx = i - half_w + j
                if 0 <= s_idx < n:
                    acc += signal[s_idx] * w
            result.append(acc)

        self._state.total_convolutions += 1
        self._state.last_signal_length = n
        self._state.last_kernel_length = kernel_size

        metadata = {
            "theorem": "T127",
            "equation": "Eq4",
            "topology_type": topology_type.value,
            "neighbor_count": neighbor,
            "curvature": self._state.curvature,
            "kernel_weights": [round(w, 4) for w in weights],
            "kernel_size": kernel_size,
        }
        return {"result": result, "metadata": metadata}

    def verify_theorem(self) -> Dict[str, Any]:
        """
        验证定理T127：拓扑重构定理

        验证1：不同拓扑产生不同卷积结果
        验证2：欧氏拓扑（torus）近似均匀核
        """
        signal = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

        # 欧氏拓扑（环面曲率=0）
        euclidean_res = self.fenxiangzi_convolve(
            signal, FenxiangziType.TORUS
        )
        # 球面拓扑（十二面体曲率>0）
        spherical_res = self.fenxiangzi_convolve(
            signal, FenxiangziType.DODECAHEDRON
        )
        # 双曲拓扑
        hyperbolic_res = self.fenxiangzi_convolve(
            signal, FenxiangziType.HYPERBOLIC
        )

        # 验证不同拓扑产生不同结果
        euc_result = euclidean_res["result"]
        sph_result = spherical_res["result"]
        hyp_result = hyperbolic_res["result"]

        diff_euc_sph = sum(
            abs(a - b) for a, b in zip(euc_result, sph_result)
        )
        diff_euc_hyp = sum(
            abs(a - b) for a, b in zip(euc_result, hyp_result)
        )

        topology_differs = (diff_euc_sph > 1e-6 or diff_euc_hyp > 1e-6)

        # 欧氏核近似均匀
        euc_weights = euclidean_res["metadata"]["kernel_weights"]
        uniform_check = all(
            abs(w - euc_weights[0]) < 0.01 for w in euc_weights
        )

        return {
            "theorem": "T127",
            "verified": topology_differs and uniform_check,
            "detail": "拓扑重构定理：不同拓扑产生不同卷积，"
                      "欧氏拓扑核近似均匀",
            "euclidean_vs_spherical": round(diff_euc_sph, 6),
            "euclidean_vs_hyperbolic": round(diff_euc_hyp, 6),
            "euclidean_uniform_kernel": uniform_check,
        }

    def api_convolve(self, signal: List[float],
                     topology_type: FenxiangziType
                     ) -> Dict[str, Any]:
        """API辅助方法"""
        res = self.fenxiangzi_convolve(signal, topology_type)
        state = self.get_state()
        return {
            "api": "M160/fenxiangzi_convolve",
            "result": res["result"],
            "metadata": res["metadata"],
            "state": state,
        }


def get_instance(topology_type: FenxiangziType = FenxiangziType.DODECAHEDRON
                 ) -> FenxiangziTopologyConvolution:
    """模块级单例获取函数"""
    return FenxiangziTopologyConvolution.get_instance(
        topology_type=topology_type
    )


if __name__ == "__main__":
    print("=" * 60)
    print("M160 芬芳香子拓扑卷积 — 自测")
    print("=" * 60)

    conv = FenxiangziTopologyConvolution.get_instance()
    print(f"\n[状态] {conv.get_state()}")

    signal = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    # 测试不同拓扑类型
    test_types = [
        FenxiangziType.DODECAHEDRON,
        FenxiangziType.TORUS,
        FenxiangziType.HYPERBOLIC,
    ]

    for t in test_types:
        res = conv.fenxiangzi_convolve(signal, t)
        print(f"\n{t.value} 卷积结果:")
        print(f"  result = {[round(v, 4) for v in res['result']]}")
        print(f"  curvature = {res['metadata']['curvature']}")
        print(f"  weights = {res['metadata']['kernel_weights']}")

    # 验证定理
    verification = conv.verify_theorem()
    print(f"\n定理T127验证: {verification['verified']}")
    print(f"  euc vs sph: {verification['euclidean_vs_spherical']}")
    print(f"  euc vs hyp: {verification['euclidean_vs_hyperbolic']}")
    print(f"  euc uniform: {verification['euclidean_uniform_kernel']}")

    # API测试
    api_res = conv.api_convolve(signal, FenxiangziType.ICOSAHEDRON)
    print(f"\nAPI调用结果长度: {len(api_res['result'])}")

    print("\n" + "=" * 60)
    print("M160 自测完成")
    print("=" * 60)
