# -*- coding: utf-8 -*-
"""M108: 手性旋量感知器 (Chiral Spinor Sensor)
基于论文3: 模n相位守恒+Helix同构
核心定理：
  T62 模n相位守恒定理: ∑φ_i ≡ 0 (mod n)
  T63 Helix-手性同构定理: Helix(F) ≅ 手性流贯(F) (五行变换同构)
可证伪预言：P21 手性感知模块对左旋/右旋输入的响应差 ∝ 相位差·Helix(F)
"""

import math
import time
from typing import Dict, Any, List, Optional

class ChiralSpinorSensor:
    """手性旋量感知器 — 模n相位守恒+Helix同构"""

    def __init__(self):
        # 手性参数
        self.chirality: str = 'neutral'  # 'left'/'right'/'neutral'
        self.chiral_index: float = 0.0   # 手性指数 (-1=左旋, +1=右旋)

        # 相位参数
        self.phases: List[float] = []     # 当前相位列表
        self.symmetry_n: int = 5          # 模n (五行)
        self.phase_sum: float = 0.0       # 相位总和
        self.phase_mod_n: float = 0.0     # 相位模n
        self.phase_conservation: float = 1.0  # 守恒度

        # Helix同构参数
        self.helix_pitch: float = 1.0     # 螺距
        self.helix_radius: float = 1.0    # 半径
        self.helix_chirality: float = 0.0  # Helix手性
        self.helix_isomorphism: float = 0.0  # Helix-手性同构度

        # 五行映射
        self.wuxing_phases: Dict[str, float] = {
            '木': 0.0, '火': math.pi * 2 / 5,
            '土': math.pi * 4 / 5, '金': math.pi * 6 / 5,
            '水': math.pi * 8 / 5
        }
        self.current_wuxing: str = '土'

        # 响应差
        self.left_response: float = 0.0
        self.right_response: float = 0.0
        self.response_diff: float = 0.0

        # 统计
        self.total_senses: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def sense_chirality(self, input_signal: List[float], chirality_label: str = 'auto') -> Dict[str, Any]:
        """感知输入信号的手性"""
        if not input_signal or len(input_signal) < 3:
            return {'chirality': 'neutral', 'chiral_index': 0.0}

        # 计算手性指数：信号的螺旋方向
        # 使用3D叉积的z分量判断左旋/右旋
        n = len(input_signal)
        cross_sum = 0.0
        for i in range(n - 2):
            # 简化3D叉积
            a = input_signal[i]
            b = input_signal[(i + 1) % n]
            c = input_signal[(i + 2) % n]
            cross_sum += (b - a) * (c - b) - (c - b) * (b - a) * 0.5

        chiral_idx = math.tanh(cross_sum / max(1, n))

        if chirality_label == 'auto':
            if chiral_idx < -0.3:
                self.chirality = 'left'
            elif chiral_idx > 0.3:
                self.chirality = 'right'
            else:
                self.chirality = 'neutral'
        else:
            self.chirality = chirality_label

        self.chiral_index = round(chiral_idx, 4)
        self.total_senses += 1

        # 记录左旋/右旋响应
        if self.chirality == 'left':
            self.left_response = abs(chiral_idx)
        elif self.chirality == 'right':
            self.right_response = abs(chiral_idx)

        return {
            'chirality': self.chirality,
            'chiral_index': self.chiral_index,
            'cross_sum': round(cross_sum, 4)
        }

    def compute_phase_conservation(self, phases: Optional[List[float]] = None) -> Dict[str, Any]:
        """计算模n相位守恒 (T62)"""
        if phases is not None:
            self.phases = phases

        if not self.phases:
            return {'conserved': True, 'mod_n': 0.0, 'n': self.symmetry_n}

        # T62: ∑φ_i ≡ 0 (mod n)
        self.phase_sum = sum(self.phases)
        self.phase_mod_n = self.phase_sum % self.symmetry_n

        # 守恒度 = 1 - |mod_n / n|
        self.phase_conservation = round(1.0 - abs(self.phase_mod_n) / self.symmetry_n, 4)

        is_conserved = self.phase_mod_n < 0.1 * self.symmetry_n

        return {
            'phase_sum': round(self.phase_sum, 4),
            'mod_n': round(self.phase_mod_n, 4),
            'n': self.symmetry_n,
            'conserved': is_conserved,
            'conservation_score': self.phase_conservation,
            'theorem': 'T62: ∑φ_i ≡ 0 (mod n)'
        }

    def compute_helix_isomorphism(self) -> Dict[str, Any]:
        """计算Helix-手性同构 (T63)"""
        # T63: Helix(F) ≅ 手性流贯(F) (五行变换同构)
        # Helix chirality from parameters
        self.helix_chirality = round(
            math.sin(self.helix_pitch) * self.chiral_index * self.helix_radius, 4
        )

        # 同构度 = 手性指数与Helix手性的相关性
        if abs(self.chiral_index) > 0.01 and abs(self.helix_chirality) > 0.01:
            ratio = self.helix_chirality / self.chiral_index
            self.helix_isomorphism = round(math.exp(-abs(ratio - 1.0)), 4)
        else:
            self.helix_isomorphism = 0.5

        # 更新五行对应
        phase_idx = int((self.chiral_index + 1) / 2 * 5) % 5
        wuxing_list = ['水', '木', '土', '金', '火']
        self.current_wuxing = wuxing_list[phase_idx]

        return {
            'helix_chirality': self.helix_chirality,
            'helix_isomorphism': self.helix_isomorphism,
            'current_wuxing': self.current_wuxing,
            'is_isomorphic': self.helix_isomorphism >= 0.7,
            'theorem': 'T63: Helix(F) ≅ 手性流贯(F)'
        }

    def compute_response_diff(self) -> Dict[str, Any]:
        """计算手性响应差 (P21)"""
        # P21: 响应差 ∝ 相位差·Helix(F)
        phase_diff = abs(self.phase_sum) if self.phases else 0.0
        self.response_diff = round(phase_diff * self.helix_isomorphism, 4)

        return {
            'left_response': round(self.left_response, 4),
            'right_response': round(self.right_response, 4),
            'response_diff': self.response_diff,
            'phase_diff': round(phase_diff, 4),
            'prediction': 'P21: 响应差 ∝ 相位差·Helix(F)'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """更新状态"""
        if data:
            signal = data.get('signal', [])
            if signal:
                self.sense_chirality(signal, data.get('chirality_label', 'auto'))
            phases = data.get('phases', None)
            if phases:
                self.compute_phase_conservation(phases)
            if 'helix_pitch' in data:
                self.helix_pitch = data['helix_pitch']
            if 'helix_radius' in data:
                self.helix_radius = data['helix_radius']
            if 'symmetry_n' in data:
                self.symmetry_n = data['symmetry_n']

        self.compute_helix_isomorphism()
        self.compute_response_diff()
        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            'chirality': self.chirality,
            'chiral_index': self.chiral_index,
            'phase_conservation': self.phase_conservation,
            'phase_mod_n': round(self.phase_mod_n, 4),
            'symmetry_n': self.symmetry_n,
            'helix_chirality': self.helix_chirality,
            'helix_isomorphism': self.helix_isomorphism,
            'current_wuxing': self.current_wuxing,
            'left_response': round(self.left_response, 4),
            'right_response': round(self.right_response, 4),
            'response_diff': self.response_diff,
            'total_senses': self.total_senses,
            'frame_count': self.frame_count,
            'status': 'chiral' if abs(self.chiral_index) > 0.3 else 'achiral',
            'last_update': self.last_update
        }

    def simulate(self) -> Dict[str, Any]:
        """模拟运行"""
        import random
        # 左旋信号
        left_signal = [math.sin(i * 0.5) for i in range(10)]
        self.sense_chirality(left_signal, 'auto')
        # 随机相位
        phases = [random.uniform(0, 2 * math.pi) for _ in range(5)]
        self.compute_phase_conservation(phases)
        return self.update()


# 全局单例
_chiral_instance: Optional[ChiralSpinorSensor] = None

def get_instance() -> ChiralSpinorSensor:
    global _chiral_instance
    if _chiral_instance is None:
        _chiral_instance = ChiralSpinorSensor()
    return _chiral_instance

def update(data=None): return get_instance().update(data)
def get_state(): return get_instance().get_state()
def simulate(): return get_instance().simulate()
