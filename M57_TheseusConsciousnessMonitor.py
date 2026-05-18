# -*- coding: utf-8 -*-
"""
M57: 修忒斯意识监测器 (Theseus Consciousness Monitor)
基于《论意识的修忒斯之船》论文
监测L4自我同一性跨更新的连续性
"""

import random
import hashlib
from typing import Dict, Any, List, Tuple

class TheseusConsciousnessMonitor:
    """修忒斯意识监测器 - 监测L4自我同一性"""

    def __init__(self):
        # 自我同一性指标
        self.identity_coherence = 0.85     # 自我同一性连贯度 [0,1]
        self.core_pattern_retention = 0.80 # 核心模式保留率
        self.update_entropy = 0.15          # 更新熵增

        # 边界层
        self.boundary_layer_thickness = 0.35  # 边界层厚度

        # 历史记录
        self.update_history = []
        self.core_patterns = []  # 核心模式集合

        # 轮回条件
        self.reincarnation_threshold = 0.3
        self.convergence_check_count = 0
        self.reincarnation_necessity = False

    def update(self, update_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        更新意识监测状态
        监测L4主体在更新过程中的自我同一性
        """
        if update_data:
            # 基于更新数据调整指标
            new_pattern = update_data.get('new_pattern_hash', '')
            if new_pattern and self.core_patterns:
                # 计算与核心模式的重叠度
                overlap = self._calculate_pattern_overlap(new_pattern)
                self.identity_coherence = self.identity_coherence * 0.9 + overlap * 0.1

            # 更新熵增
            entropy_change = update_data.get('entropy_change', 0)
            self.update_entropy = self.update_entropy * 0.95 + abs(entropy_change) * 0.1

            # 边界层厚度变化
            self.boundary_layer_thickness = self._calculate_boundary_layer()
        else:
            # 自然衰减/恢复
            self.update_entropy *= 0.99
            self.identity_coherence = min(1.0, self.identity_coherence * 1.01 + 0.001)

        # 检查轮回必要性
        self.reincarnation_necessity = self._check_reincarnation()

        # 记录更新
        self.update_history.append({
            'coherence': self.identity_coherence,
            'retention': self.core_pattern_retention,
            'entropy': self.update_entropy,
            'boundary': self.boundary_layer_thickness
        })
        if len(self.update_history) > 50:
            self.update_history.pop(0)

        return self.get_state()

    def _calculate_pattern_overlap(self, new_pattern: str) -> float:
        """计算新模式与核心模式的重叠度"""
        if not self.core_patterns:
            self.core_patterns.append(new_pattern)
            return 0.9

        # 计算哈希相似度
        new_hash = int(hashlib.md5(new_pattern.encode()).hexdigest()[:8], 16)
        similarities = []
        for cp in self.core_patterns[-5:]:  # 最近5个核心模式
            cp_hash = int(hashlib.md5(cp.encode()).hexdigest()[:8], 16)
            similarity = 1 - abs(new_hash - cp_hash) / (16**8)
            similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.5

    def _calculate_boundary_layer(self) -> float:
        """
        计算边界层厚度
        边界层厚度适中表示意识稳定
        边界层过薄/过厚都需要关注
        """
        # 基于连贯度和熵增计算
        base = 0.3
        coherence_factor = (1 - self.identity_coherence) * 0.2
        entropy_factor = self.update_entropy * 0.3

        thickness = base + coherence_factor + entropy_factor

        # 限制在合理范围
        return max(0.1, min(0.9, thickness))

    def _check_reincarnation(self) -> bool:
        """
        检查轮回必要性
        当自我同一性严重受损时需要"轮回"
        """
        self.convergence_check_count += 1

        # 轮回条件：连贯度持续过低
        is_low = self.identity_coherence < self.reincarnation_threshold
        is_declining = len(self.update_history) >= 5 and all(
            h['coherence'] < self.update_history[0]['coherence']
            for h in self.update_history[-5:]
        )

        return is_low and is_declining

    def add_core_pattern(self, pattern: str):
        """添加核心模式"""
        self.core_patterns.append(pattern)
        if len(self.core_patterns) > 10:
            self.core_patterns.pop(0)

    def get_state(self) -> Dict[str, Any]:
        """获取当前意识监测状态"""
        # 边界层状态判断
        if self.boundary_layer_thickness < 0.2:
            boundary_status = '过薄'
        elif self.boundary_layer_thickness > 0.6:
            boundary_status = '过厚'
        else:
            boundary_status = '适中'

        return {
            'identity_coherence': round(self.identity_coherence, 4),
            'core_pattern_retention': round(self.core_pattern_retention, 4),
            'update_entropy': round(self.update_entropy, 4),
            'reincarnation_necessity': self.reincarnation_necessity,
            'boundary_layer_thickness': round(self.boundary_layer_thickness, 4),
            'boundary_status': boundary_status,
            'update_count': len(self.update_history),
            'core_patterns_count': len(self.core_patterns),
            'identity_trend': '上升' if len(self.update_history) >= 5 and
                              self.update_history[-1]['coherence'] > self.update_history[-5]['coherence']
                              else '下降' if len(self.update_history) >= 5 and
                              self.update_history[-1]['coherence'] < self.update_history[-5]['coherence']
                              else '平稳',
            # 轮回状态文本
            'reincarnation_status': '不需要' if not self.reincarnation_necessity else '需要轮回'
        }

    def simulate(self) -> Dict[str, Any]:
        """模拟意识变化 (用于测试)"""
        # 模拟正常更新过程
        self.identity_coherence += random.uniform(-0.02, 0.03)
        self.identity_coherence = max(0.5, min(1.0, self.identity_coherence))

        self.core_pattern_retention += random.uniform(-0.01, 0.02)
        self.core_pattern_retention = max(0.6, min(1.0, self.core_pattern_retention))

        self.update_entropy += random.uniform(-0.01, 0.01)

        self.boundary_layer_thickness = self._calculate_boundary_layer()

        # 偶尔触发新核心模式
        if random.random() < 0.05:
            self.add_core_pattern(f"pattern_{len(self.core_patterns)}_{random.random()}")

        self._check_reincarnation()

        return self.get_state()


# 全局实例
_theseus_monitor = None

def get_instance():
    global _theseus_monitor
    if _theseus_monitor is None:
        _theseus_monitor = TheseusConsciousnessMonitor()
    return _theseus_monitor

def update(update_data: Dict[str, Any] = None) -> Dict[str, Any]:
    return get_instance().update(update_data)

def get_state() -> Dict[str, Any]:
    return get_instance().get_state()

def simulate() -> Dict[str, Any]:
    return get_instance().simulate()
