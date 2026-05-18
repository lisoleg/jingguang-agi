#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
介质共振模块 (Medium Resonance Module)
基于复合体理学"一现象三视界"诠释法
实现非统计学的全息信息处理

核心原理:
- 术数的有效性不依赖于统计学，而依赖于介质共振
- 统计学处理离散符号的频次，术数处理连续介质的应力
- 当观测者达到"天人合一"(相位锁定)时，直接读取介质全息信息
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class PhaseField:
    """相位场"""
    amplitude: float  # 振幅
    frequency: float  # 频率
    phase: float     # 相位
    coherence: float # 相干度 [0, 1]

    def inner_product(self, other: 'PhaseField') -> float:
        """计算与另一个相位场的内积 (相位锁定度)"""
        return self.coherence * other.coherence * np.cos(self.phase - other.phase)

    def to_dict(self) -> Dict:
        return {
            'amplitude': float(self.amplitude),
            'frequency': float(self.frequency),
            'phase': float(self.phase),
            'coherence': float(self.coherence)
        }


@dataclass
class StressField:
    """应力场 (拓扑信息载体)"""
    topology: Dict[str, float]  # 拓扑结构: {节点: 应力值}
    gradient: np.ndarray        # 应力梯度
    holonomy: float            # 整体全息信息量
    singularities: List[Dict]  # 奇点列表 (高应力集中区)

    def to_dict(self) -> Dict:
        return {
            'topology': self.topology,
            'holonomy': float(self.holonomy),
            'singularities': self.singularities
        }


@dataclass
class MediumResponse:
    """介质共振响应"""
    stress_field: StressField
    phase_lock_degree: float  # g_C ∈ [0, 1]
    holistic_info: Dict       # 全息信息
    entropy_Sc: float         # 意识熵
    resonance_quality: str     # 'high', 'medium', 'low'

    def to_dict(self) -> Dict:
        return {
            'stress_field': self.stress_field.to_dict(),
            'phase_lock_degree': self.phase_lock_degree,
            'holistic_info': self.holistic_info,
            'entropy_Sc': self.entropy_Sc,
            'resonance_quality': self.resonance_quality
        }


class MediumResonanceModule:
    """
    介质共振模块

    实现非统计推断的信息获取方式:
    - 读取连续介质的拓扑应力场
    - 计算观测者与介质的相位锁定度
    - 提取全息信息 (局部包含整体)
    """

    def __init__(self):
        self.phi_self: Optional[PhaseField] = None
        self.phi_world: Optional[PhaseField] = None
        self.medium_history: List[MediumResponse] = []
        self.resonance_threshold = 0.6  # 相位锁定阈值

    def construct_self_phase_field(self, observer_state: Dict) -> PhaseField:
        """
        构建观测者相位场 Φ_self

        观测者状态包括:
        - 专注度 (coherence)
        - 心境 (phase)
        - 认知强度 (amplitude)
        """
        coherence = observer_state.get('coherence', 0.5)  # 专注度
        phase = observer_state.get('phase', 0.0)         # 心境偏移
        amplitude = observer_state.get('amplitude', 0.8) # 认知强度
        frequency = observer_state.get('frequency', 1.0) # 内在频率

        self.phi_self = PhaseField(
            amplitude=amplitude,
            frequency=frequency,
            phase=phase,
            coherence=coherence
        )
        return self.phi_self

    def read_world_phase_field(self, context: Dict) -> PhaseField:
        """
        读取全局介质相位场 Φ_world

        通过上下文构建介质的当前状态:
        - 时空坐标 (天时地利)
        - 社会能量场
        - 趋势方向
        """
        # 从上下文提取介质特征
        temporal_energy = context.get('temporal_energy', 0.5)
        spatial_tension = context.get('spatial_tension', 0.5)
        trend_direction = context.get('trend_direction', 0.0)

        # 构建介质相位场
        self.phi_world = PhaseField(
            amplitude=np.sqrt(temporal_energy * spatial_tension),
            frequency=1.0 + trend_direction * 0.5,
            phase=trend_direction * np.pi,
            coherence=max(0.1, 1.0 - abs(trend_direction))
        )
        return self.phi_world

    def compute_phase_lock_degree(self) -> float:
        """
        计算相位锁定度 g_C

        公式: g_C = ⟨Φ_self|Φ_world⟩ = coherence_self * coherence_world * cos(Δphase)
        当 g_C → 1 时, 达到"天人合一"
        """
        if self.phi_self is None or self.phi_world is None:
            return 0.0

        inner_prod = self.phi_self.inner_product(self.phi_world)

        # 归一化到 [0, 1]
        max_inner = self.phi_self.coherence * self.phi_world.coherence
        if max_inner == 0:
            return 0.0

        g_c = (inner_prod + max_inner) / (2 * max_inner)  # 映射到 [0, 1]
        return float(np.clip(g_c, 0.0, 1.0))

    def construct_local_manifold(self, context: Dict) -> Dict:
        """
        构建局部流形 (从当下情境)

        将时空坐标映射到介质的一个局部区域
        """
        manifold = {
            'dimension': context.get('dimension', 3),
            'curvature': context.get('curvature', 0.5),
            'connectivity': context.get('connectivity', 0.7),
            'local_nodes': context.get('local_nodes', []),
            'boundary_conditions': context.get('boundary', {})
        }
        return manifold

    def extract_stress_field(self, manifold: Dict, context: Dict) -> StressField:
        """
        从局部流形提取拓扑应力场

        应力场包含:
        - 各节点的应力分布
        - 应力梯度 (指向)
        - 整体全息信息量
        - 奇点 (高应力集中)
        """
        # 节点应力分布
        nodes = manifold.get('local_nodes', [])
        topology = {}
        for i, node in enumerate(nodes):
            # 应力 = 曲率 * 连接度 * 边界条件
            stress = (
                manifold['curvature'] *
                manifold['connectivity'] *
                (1.0 + 0.3 * np.sin(i * np.pi / max(1, len(nodes))))
            )
            topology[node.get('id', f'node_{i}')] = float(stress)

        # 如果没有显式节点，从上下文中推断
        if not topology:
            for key in ['pressure_points', 'stress_sources', 'key_factors']:
                if key in context:
                    for item in context[key]:
                        node_id = item.get('id', item.get('name', key))
                        topology[node_id] = float(item.get('stress', 0.5))

        # 计算应力梯度
        if len(topology) >= 2:
            values = list(topology.values())
            gradient = np.gradient(values)
        else:
            # 节点太少，使用默认梯度
            values = list(topology.values()) if topology else [0.5]
            gradient = np.array([0.0] * len(values))

        # 识别奇点 (应力极值)
        singularities = []
        for node_id, stress in topology.items():
            if stress > 0.8:  # 高应力区
                singularities.append({
                    'node': node_id,
                    'stress': stress,
                    'type': 'high_pressure',
                    'guidance': self._get_stress_guidance(stress, 'high')
                })
            elif stress < 0.2:  # 低应力区 (可能是机会)
                singularities.append({
                    'node': node_id,
                    'stress': stress,
                    'type': 'low_pressure',
                    'guidance': self._get_stress_guidance(stress, 'low')
                })

        # 计算全息信息量 (Holonomy)
        holonomy = self._compute_holonomy(topology, gradient)

        return StressField(
            topology=topology,
            gradient=gradient,
            holonomy=holonomy,
            singularities=singularities
        )

    def _compute_holonomy(self, topology: Dict, gradient: np.ndarray) -> float:
        """
        计算全息信息量

        基于拓扑复杂度和梯度变化
        """
        # 如果没有拓扑信息，返回基于上下文的默认全息度
        if not topology:
            # 默认值：从上下文推断基本全息度
            return 0.5  # 中等全息度作为默认值

        # 拓扑熵 (复杂度)
        n = len(topology)
        topology_entropy = -np.sum([
            v * np.log(v + 1e-10) for v in topology.values()
        ]) / np.log(n + 1)

        # 梯度熵 (变化程度)
        gradient_entropy = np.std(gradient)

        # 全息度 = 局部熵 / 整体复杂度
        holonomy = (topology_entropy + gradient_entropy) / 2
        # 确保返回值在 [0.1, 0.9] 范围内，避免极端值
        return float(np.clip(holonomy, 0.1, 0.9))

    def _get_stress_guidance(self, stress: float, stress_type: str) -> str:
        """根据应力类型给出指导"""
        if stress_type == 'high':
            if stress > 0.9:
                return "极高压力区，建议静心调息，等待介质松动"
            else:
                return "高压力区，可用'困'卦接受现状，不宜强行突破"
        else:
            return "低压力区，可能存在机会，关注边界条件变化"

    def extract_holistic_info(self, stress_field: StressField) -> Dict:
        """
        从应力场提取全息信息

        全息原理: 局部区域包含整体信息
        """
        if not stress_field.topology:
            return {'summary': '信息不足', 'insights': []}

        # 汇总统计
        values = list(stress_field.topology.values())
        avg_stress = np.mean(values)
        max_stress_node = max(stress_field.topology, key=stress_field.topology.get)
        min_stress_node = min(stress_field.topology, key=stress_field.topology.get)

        # 识别趋势
        trend = 'stable'
        if len(values) >= 3:
            slope = np.polyfit(range(len(values)), values, 1)[0]
            if slope > 0.05:
                trend = 'increasing'
            elif slope < -0.05:
                trend = 'decreasing'

        # 整体洞察
        insights = []

        # 高压节点洞察
        for sing in stress_field.singularities:
            if sing['type'] == 'high_pressure':
                insights.append(f"'{sing['node']}'处于高压状态: {sing['guidance']}")

        # 趋势洞察
        if trend == 'increasing':
            insights.append("整体应力正在上升，系统趋近临界点")
        elif trend == 'decreasing':
            insights.append("整体应力正在下降，趋于稳定或释放")

        # 全息洞察
        if stress_field.holonomy > 0.5:
            insights.append("高全息度: 局部信息高度关联整体，可信度高")
        else:
            insights.append("低全息度: 局部信息相对独立，需结合其他信息源")

        return {
            'summary': f"应力场分析: 平均{avg_stress:.2f}, 趋势{trend}",
            'max_stress_node': max_stress_node,
            'min_stress_node': min_stress_node,
            'trend': trend,
            'holonomy': stress_field.holonomy,
            'insights': insights
        }

    def read_medium_field(self, context: Dict, observer_state: Dict) -> MediumResponse:
        """
        读取介质场 (主接口)

        步骤:
        1. 构建观测者相位场 Φ_self
        2. 读取全局介质相位场 Φ_world
        3. 计算相位锁定度 g_C
        4. 构建局部流形
        5. 提取应力场
        6. 提取全息信息
        """
        # 1. 构建相位场
        self.construct_self_phase_field(observer_state)
        self.read_world_phase_field(context)

        # 2. 计算相位锁定度
        g_c = self.compute_phase_lock_degree()

        # 3. 构建局部流形
        manifold = self.construct_local_manifold(context)

        # 4. 提取应力场
        stress_field = self.extract_stress_field(manifold, context)

        # 5. 提取全息信息
        holistic_info = self.extract_holistic_info(stress_field)

        # 6. 计算意识熵
        # S_C = 1 - g_C (相位锁定度越高，意识熵越低)
        # 确保 g_c 不会太低导致 S_C 过高，使用更合理的映射
        entropy_Sc = max(0.05, min(0.95, 1.0 - g_c * 0.8))

        # 7. 评估共振质量
        if g_c >= 0.8:
            resonance_quality = 'high'  # 天人合一
        elif g_c >= 0.5:
            resonance_quality = 'medium'
        else:
            resonance_quality = 'low'

        response = MediumResponse(
            stress_field=stress_field,
            phase_lock_degree=g_c,
            holistic_info=holistic_info,
            entropy_Sc=entropy_Sc,
            resonance_quality=resonance_quality
        )

        # 保存历史
        self.medium_history.append(response)

        return response

    def resonance_response(self, query: str, medium_response: MediumResponse) -> Dict:
        """
        基于介质共振给出响应

        当 g_C 高时，直接获取全息信息
        当 g_C 低时，结合传统方法
        """
        g_c = medium_response.phase_lock_degree
        holistic = medium_response.holistic_info

        if g_c >= 0.8:
            # 天人合一: 直接读取
            return {
                'mode': 'direct_read',
                'confidence': g_c,
                'answer': holistic.get('summary', '全息信息读取成功'),
                'insights': holistic.get('insights', []),
                'stress_field': medium_response.stress_field.to_dict()
            }
        elif g_c >= 0.5:
            # 中等锁定: 混合模式
            return {
                'mode': 'hybrid',
                'confidence': g_c,
                'answer': f"[介质共振@{g_c:.0%}] {holistic.get('summary', '')}",
                'insights': holistic.get('insights', []),
                'recommendation': '建议提升专注度以增强共振质量',
                'stress_field': medium_response.stress_field.to_dict()
            }
        else:
            # 低锁定: 需要外部信息辅助
            return {
                'mode': 'needs_support',
                'confidence': g_c,
                'answer': f"[共振较弱@{g_c:.0%}] {holistic.get('summary', '信息不完整')}",
                'insights': holistic.get('insights', []),
                'recommendation': '建议通过冥想/专注提升意识熵调控能力',
                'stress_field': medium_response.stress_field.to_dict()
            }

    def get_entanglement_degree(self, entity_a: Dict, entity_b: Dict) -> float:
        """
        计算两实体的纠缠度 (全息关联)

        原理: 高度纠缠的实体之间，局部信息高度相关
        """
        # 提取关键特征
        features_a = self._extract_features(entity_a)
        features_b = self._extract_features(entity_b)

        # 计算余弦相似度
        if not features_a or not features_b:
            return 0.0

        dot_prod = sum(a * b for a, b in zip(features_a, features_b))
        norm_a = np.sqrt(sum(a**2 for a in features_a))
        norm_b = np.sqrt(sum(b**2 for b in features_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_prod / (norm_a * norm_b))

    def _extract_features(self, entity: Dict) -> List[float]:
        """提取实体的特征向量"""
        features = []

        # 数值特征
        numeric_keys = ['energy', 'stress', 'coherence', 'entropy', 'activity']
        for key in numeric_keys:
            features.append(float(entity.get(key, 0.5)))

        # 类型特征 (one-hot)
        type_map = {'high': [1, 0, 0], 'medium': [0, 1, 0], 'low': [0, 0, 1]}
        entity_type = entity.get('type', 'medium')
        features.extend(type_map.get(entity_type, [0, 0, 0]))

        return features[:8]  # 限制特征维度


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("介质共振模块测试")
    print("=" * 60)

    module = MediumResonanceModule()

    # 测试场景1: 高压决策情境
    print("\n【测试场景1: 高压决策】")
    context1 = {
        'temporal_energy': 0.9,  # 高时间压力
        'spatial_tension': 0.8,  # 高空间张力
        'trend_direction': 0.3,  # 上升趋势
        'pressure_points': [
            {'id': 'deadline', 'stress': 0.95},
            {'id': 'competition', 'stress': 0.85},
            {'id': 'resource', 'stress': 0.60}
        ]
    }
    observer1 = {
        'coherence': 0.7,   # 中等专注
        'phase': 0.2,      # 略偏焦虑
        'amplitude': 0.8
    }

    response1 = module.read_medium_field(context1, observer1)
    print(f"相位锁定度: {response1.phase_lock_degree:.2%}")
    print(f"意识熵 S_C: {response1.entropy_Sc:.2f}")
    print(f"共振质量: {response1.resonance_quality}")
    print(f"全息信息: {response1.holistic_info['summary']}")
    print("洞察:")
    for insight in response1.holistic_info.get('insights', []):
        print(f"  - {insight}")

    resonance_answer = module.resonance_response("如何突破当前困境?", response1)
    print(f"\n共振响应模式: {resonance_answer['mode']}")
    print(f"响应内容: {resonance_answer['answer']}")

    # 测试场景2: 天人合一状态
    print("\n【测试场景2: 天人合一状态】")
    context2 = {
        'temporal_energy': 0.5,
        'spatial_tension': 0.5,
        'trend_direction': 0.0,
        'pressure_points': [
            {'id': 'clarity', 'stress': 0.5},
            {'id': 'flow', 'stress': 0.5}
        ]
    }
    observer2 = {
        'coherence': 0.95,  # 高度专注
        'phase': 0.0,       # 平静
        'amplitude': 1.0
    }

    response2 = module.read_medium_field(context2, observer2)
    print(f"相位锁定度: {response2.phase_lock_degree:.2%}")
    print(f"意识熵 S_C: {response2.entropy_Sc:.2f}")
    print(f"共振质量: {response2.resonance_quality}")
    print(f"全息信息: {response2.holistic_info['summary']}")

    resonance_answer2 = module.resonance_response("我应该如何行动?", response2)
    print(f"\n共振响应模式: {resonance_answer2['mode']}")
    print(f"响应内容: {resonance_answer2['answer']}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
