# -*- coding: utf-8 -*-
"""M107: 维度投影处理器 (Dimension Projection Processor)
基于论文2: Embed↑/Π↓对偶运算
核心定理：
  T60 维度投影信息损失定理: S_proj = S_high + k·ln(D_high/D_low)
  T61 Embed-Π伴随对偶定理: Embed ⊣ Π (范畴论伴随函子对)
可证伪预言：P20 高维上下文(Embed)引入后，信息熵必增：ΔS = k·ln(上下文维度比)
"""

import math
import time
from typing import Dict, Any, List, Optional

class DimensionProjectionProcessor:
    """维度投影处理器 — Embed↑/Π↓对偶运算"""

    def __init__(self):
        # 高维空间参数
        self.high_dim: int = 12
        self.low_dim: int = 3
        self.current_dim: int = 12

        # Embed(↑) 嵌入参数
        self.embed_operations: int = 0
        self.embed_info_gain: float = 0.0
        self.embed_dimension_ratio: float = 1.0

        # Π(↓) 投影参数
        self.pi_operations: int = 0
        self.pi_info_loss: float = 0.0
        self.pi_compression: float = 0.0

        # 信息度量
        self.entropy_high: float = 0.0
        self.entropy_low: float = 0.0
        self.info_loss: float = 0.0
        self.boltzmann_k: float = 1.0  # Boltzmann常数(归一化)

        # 对偶性度量
        self.adjunction_score: float = 0.0  # Embed ⊣ Π 对偶度
        self.naturality_square: float = 0.0  # 自然性方图可换度

        # 统计
        self.total_projections: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def embed(self, low_data: List[float], target_dim: int = 0) -> Dict[str, Any]:
        """Embed↑: 将低维数据嵌入高维空间"""
        if target_dim <= 0:
            target_dim = self.high_dim

        n = len(low_data)
        if n == 0:
            return {'success': False, 'reason': 'empty_data'}

        # 嵌入：扩展维度，补零或线性插值
        embedded = list(low_data)
        if target_dim > n:
            # 线性插值扩展
            step = n / max(1, target_dim - 1)
            interpolated = []
            for i in range(target_dim):
                src_idx = min(n - 1, int(i * step))
                interpolated.append(low_data[src_idx])
            embedded = interpolated

        self.embed_operations += 1
        dim_ratio = target_dim / max(1, n)
        self.embed_dimension_ratio = dim_ratio

        # P20: ΔS = k·ln(上下文维度比)
        self.embed_info_gain = round(self.boltzmann_k * math.log(max(1e-9, dim_ratio)), 6)
        self.entropy_high = round(self.entropy_low + self.embed_info_gain, 6)
        self.current_dim = target_dim

        return {
            'success': True,
            'original_dim': n,
            'target_dim': target_dim,
            'info_gain': self.embed_info_gain,
            'dimension_ratio': round(dim_ratio, 4),
            'operation': 'Embed↑'
        }

    def project(self, high_data: List[float], target_dim: int = 0) -> Dict[str, Any]:
        """Π↓: 将高维数据投影到低维空间"""
        if target_dim <= 0:
            target_dim = self.low_dim

        n = len(high_data)
        if n == 0:
            return {'success': False, 'reason': 'empty_data'}

        # 投影：PCA简化版 — 取前target_dim个分量
        projected = high_data[:target_dim] if n >= target_dim else high_data + [0.0] * (target_dim - n)

        self.pi_operations += 1
        dim_ratio = n / max(1, target_dim)

        # T60: S_proj = S_high + k·ln(D_high/D_low)
        self.pi_info_loss = round(self.boltzmann_k * math.log(max(1e-9, dim_ratio)), 6)
        self.entropy_low = round(self.entropy_high - self.pi_info_loss, 6)
        self.pi_compression = round(1.0 - target_dim / max(1, n), 4)
        self.info_loss = self.pi_info_loss
        self.current_dim = target_dim
        self.total_projections += 1

        return {
            'success': True,
            'original_dim': n,
            'target_dim': target_dim,
            'info_loss': self.pi_info_loss,
            'compression': self.pi_compression,
            'operation': 'Π↓'
        }

    def compute_adjunction(self) -> Dict[str, Any]:
        """计算Embed-Π伴随对偶性 (T61)"""
        # T61: Embed ⊣ Π (伴随函子对)
        # 对偶度 = 信息增益与信息损失的对称性
        total_ops = self.embed_operations + self.pi_operations
        if total_ops == 0:
            self.adjunction_score = 0.5
        else:
            balance = 1.0 - abs(self.embed_operations - self.pi_operations) / max(1, total_ops)
            info_symmetry = 1.0 - abs(self.embed_info_gain - self.pi_info_loss) / max(0.01, abs(self.embed_info_gain) + abs(self.pi_info_loss))
            self.adjunction_score = round((balance + info_symmetry) / 2.0, 4)

        # 自然性方图可换度
        self.naturality_square = round(
            math.exp(-abs(self.embed_info_gain + self.pi_info_loss)), 4
        )

        return {
            'adjunction_score': self.adjunction_score,
            'naturality_square': self.naturality_square,
            'is_adjunction': self.adjunction_score >= 0.7,
            'theorem': 'T61: Embed ⊣ Π 伴随对偶'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """更新状态"""
        if data:
            op = data.get('operation', '')
            if op == 'embed':
                self.embed(data.get('data', []), data.get('target_dim', 0))
            elif op == 'project':
                self.project(data.get('data', []), data.get('target_dim', 0))

        self.compute_adjunction()
        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            'high_dim': self.high_dim,
            'low_dim': self.low_dim,
            'current_dim': self.current_dim,
            'embed_operations': self.embed_operations,
            'embed_info_gain': round(self.embed_info_gain, 4),
            'pi_operations': self.pi_operations,
            'pi_info_loss': round(self.pi_info_loss, 4),
            'pi_compression': self.pi_compression,
            'entropy_high': round(self.entropy_high, 4),
            'entropy_low': round(self.entropy_low, 4),
            'info_loss': round(self.info_loss, 4),
            'adjunction_score': self.adjunction_score,
            'naturality_square': self.naturality_square,
            'total_projections': self.total_projections,
            'frame_count': self.frame_count,
            'status': 'balanced' if self.adjunction_score >= 0.7 else 'imbalanced',
            'last_update': self.last_update
        }

    def simulate(self) -> Dict[str, Any]:
        """模拟运行"""
        import random
        low_data = [random.gauss(0, 1) for _ in range(3)]
        self.embed(low_data, 12)
        high_data = [random.gauss(0, 1) for _ in range(12)]
        self.project(high_data, 3)
        return self.update()


# 全局单例
_dimproj_instance: Optional[DimensionProjectionProcessor] = None

def get_instance() -> DimensionProjectionProcessor:
    global _dimproj_instance
    if _dimproj_instance is None:
        _dimproj_instance = DimensionProjectionProcessor()
    return _dimproj_instance

def update(data=None): return get_instance().update(data)
def get_state(): return get_instance().get_state()
def simulate(): return get_instance().simulate()
