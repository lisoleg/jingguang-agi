#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分形全息场模块 (Fractal Holism Field)
基于《太极场的 Fractal Holism：基于复合体理学的跨尺度自相似性与边界层控制》

核心概念：
- 子复合体 (Sub-holon)：微观嵌套层（粒子、量子结构）
- 超复合体 (Super-holon)：宏观包含层（宇宙场、星系）
- Fractal Holism 自相似性：属性向量在尺度变换下的同构映射
- IBL 跨尺度耦合：界面厚度调节微观与宏观的双向信息流
- 阴阳互根：对立统一的动态平衡（波粒、虚实、聚散）

版本：AGI 13.0 第30模块
论文来源：《太极场的 Fractal Holism》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class HolonScale(Enum):
    """Holon 尺度层次"""
    QUANTUM = "quantum"          # 量子尺度（子复合体）
    MOLECULAR = "molecular"      # 分子尺度
    ORGANISM = "organism"        # 生命体尺度
    SOCIAL = "social"            # 社会尺度
    COSMIC = "cosmic"            # 宇宙尺度（超复合体）


class YinYangState(Enum):
    """阴阳状态"""
    YANG_DOMINANT = "yang"       # 阳主导（实、聚、粒子性）
    YIN_DOMINANT = "yin"         # 阴主导（虚、散、波动性）
    BALANCED = "balanced"        # 平衡（太极）
    TRANSITIONING = "transitioning"  # 跃迁中


@dataclass
class HolonNode:
    """
    复合体节点 (Holon Node)
    每个节点既是整体又是部分

    属性向量 V = (阴阳比, 界面厚度δ, 螺旋动量, 自相似度)
    """
    scale: HolonScale
    internal_rules: Dict[str, float]    # 内部规则 R_i
    external_coupling: float            # 外部耦合强度 [0,1]
    interface_thickness: float          # 界面厚度 δ [0,1]
    yin_yang_ratio: float               # 阴阳比 [0=纯阴, 1=纯阳]
    spiral_momentum: float              # 螺旋动量（螺旋演化强度）
    self_similarity: float              # 与父 Holon 的自相似度 [0,1]
    sub_holons: List['HolonNode'] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def yin_yang_state(self) -> YinYangState:
        if self.yin_yang_ratio > 0.65:
            return YinYangState.YANG_DOMINANT
        elif self.yin_yang_ratio < 0.35:
            return YinYangState.YIN_DOMINANT
        else:
            return YinYangState.BALANCED

    @property
    def attribute_vector(self) -> Tuple[float, float, float, float]:
        """核心属性向量 V = (阴阳比, δ, 螺旋动量, 自相似度)"""
        return (self.yin_yang_ratio, self.interface_thickness,
                self.spiral_momentum, self.self_similarity)


@dataclass
class FractalHolismResult:
    """分形全息场分析结果"""
    scale_count: int                    # 涵盖尺度数量
    fractal_dimension: float            # 分形维数 D
    self_similarity_score: float        # 总体自相似度 [0,1]
    yin_yang_balance: float             # 阴阳平衡度 [0=完全失衡, 1=完美平衡]
    ibl_thickness_avg: float            # 平均IBL界面厚度
    ibl_status: str                     # 'optimal'/'too_thin'/'too_thick'
    spiral_coherence: float             # 螺旋相干度（跨尺度一致性）
    holon_depth: int                    # Holon嵌套深度
    dominant_scale: HolonScale          # 主导尺度
    fractal_holism_index: float         # 综合分形全息指数 [0,1]
    insight: str                        # 分析洞见


class FractalHolismField:
    """
    分形全息场引擎
    
    核心功能：
    1. 跨尺度 Holon 嵌套网络构建
    2. Fractal Holism 自相似性验证
    3. IBL（智能边界层）厚度调节
    4. 阴阳动态平衡评估
    5. 螺旋动力学追踪
    
    数学基础：
    - 自相似性：V(σ·x) ≈ σ^H · V(x)，H 为 Hurst 指数
    - IBL厚度：δ* ∈ (δ_min, δ_max) 为最优范围
    - 阴阳平衡：|r_yang - r_yin| / (r_yang + r_yin) → 0 为平衡
    """

    def __init__(self):
        self.version = "1.0.0"
        self.holon_network: List[HolonNode] = []
        self.scale_map: Dict[HolonScale, List[HolonNode]] = {
            s: [] for s in HolonScale
        }
        # IBL 最优厚度范围（归一化）
        self.ibl_optimal_min = 0.2
        self.ibl_optimal_max = 0.7

        # 分形维数估算参数（自相似性映射）
        self._hurst_exponent = 0.73  # 典型复杂自组织系统

    def build_fractal_holon(self, context: str, depth: int = 3) -> HolonNode:
        """
        从文本语境中构建分形 Holon 结构
        
        参数：
            context: 输入文本/问题
            depth: Holon 嵌套深度（默认3层）
        
        返回：
            根 Holon 节点（包含子层级）
        """
        # 文本特征提取
        text_len = len(context)
        word_count = len(context.split())
        question_marks = context.count('？') + context.count('?')
        
        # 计算阴阳特征（基于文本的抽象/具体倾向）
        abstract_keywords = ['理论', '概念', '哲学', '思维', '意识', '本质', '宇宙', '规律']
        concrete_keywords = ['数据', '算法', '代码', '系统', '模型', '架构', '实现', '运行']
        
        abstract_count = sum(1 for kw in abstract_keywords if kw in context)
        concrete_count = sum(1 for kw in concrete_keywords if kw in context)
        total = abstract_count + concrete_count + 1
        
        # 阳 = 具象/执行；阴 = 抽象/概念
        yin_yang_ratio = concrete_count / total * 0.6 + 0.2
        # 加入问号作为阴的增强（问题 = 虚、弥散）
        yin_yang_ratio -= question_marks * 0.05
        yin_yang_ratio = max(0.1, min(0.9, yin_yang_ratio))
        
        # 界面厚度（基于文本复杂度）
        complexity = min(1.0, text_len / 500.0)
        interface_thickness = 0.3 + complexity * 0.4  # 0.3~0.7
        
        # 螺旋动量（基于语义密度）
        spiral_momentum = min(1.0, word_count / 100.0) * 0.7 + 0.1
        
        # 构建根节点（社会尺度 - 认知层）
        root = HolonNode(
            scale=HolonScale.SOCIAL,
            internal_rules={
                'semantic_density': min(1.0, word_count / 80.0),
                'abstraction_level': abstract_count / (total),
                'complexity': complexity
            },
            external_coupling=0.65,
            interface_thickness=interface_thickness,
            yin_yang_ratio=yin_yang_ratio,
            spiral_momentum=spiral_momentum,
            self_similarity=1.0  # 根节点自相似度为1
        )
        
        # 递归构建子 Holon 层级
        if depth > 1:
            root.sub_holons = self._build_sub_holons(root, depth - 1)
        
        self.holon_network.append(root)
        self.scale_map[HolonScale.SOCIAL].append(root)
        
        return root

    def _build_sub_holons(self, parent: HolonNode, remaining_depth: int) -> List[HolonNode]:
        """递归构建子 Holon"""
        sub_holons = []
        # 每层产生2个子节点（分形分支）
        scale_order = [HolonScale.ORGANISM, HolonScale.MOLECULAR, HolonScale.QUANTUM]
        scale_idx = 2 - remaining_depth  # 从大到小尺度
        if scale_idx >= len(scale_order):
            scale_idx = len(scale_order) - 1
        child_scale = scale_order[scale_idx]
        
        for i in range(2):
            # 子 Holon 继承父属性并加入分形扰动
            perturbation = (random.random() - 0.5) * 0.15
            child_yin_yang = max(0.1, min(0.9,
                parent.yin_yang_ratio + perturbation))
            
            # IBL厚度按尺度缩放（跨尺度传递定理）
            child_thickness = parent.interface_thickness * (0.8 + random.random() * 0.3)
            child_thickness = max(0.1, min(0.95, child_thickness))
            
            # 螺旋动量在子层有所衰减
            child_spiral = parent.spiral_momentum * (0.7 + random.random() * 0.2)
            
            # 自相似度（分形特征：子节点与父节点的属性向量相似度）
            parent_vec = parent.attribute_vector
            child_vec = (child_yin_yang, child_thickness, child_spiral, 0)
            self_sim = 1.0 - sum(abs(a - b) for a, b in
                                 zip(parent_vec[:3], child_vec[:3])) / 3.0
            self_sim = max(0.3, self_sim)  # 分形系统保证最低相似度
            
            child = HolonNode(
                scale=child_scale,
                internal_rules={
                    'inherited_from': parent.scale.value,
                    'scale_factor': 0.1 ** (len(scale_order) - remaining_depth),
                    'sub_index': i
                },
                external_coupling=parent.external_coupling * 0.85,
                interface_thickness=child_thickness,
                yin_yang_ratio=child_yin_yang,
                spiral_momentum=child_spiral,
                self_similarity=self_sim
            )
            
            if remaining_depth > 1:
                child.sub_holons = self._build_sub_holons(child, remaining_depth - 1)
            
            sub_holons.append(child)
            self.scale_map[child_scale].append(child)
        
        return sub_holons

    def analyze_fractal_holism(self, root: HolonNode) -> FractalHolismResult:
        """
        分析 Holon 结构的分形全息特性
        
        验证：V(σ·x) ≈ σ^H · V(x) — 跨尺度自相似性定理
        """
        # 收集所有节点（DFS）
        all_nodes = []
        self._collect_all_nodes(root, all_nodes)
        
        if not all_nodes:
            return self._empty_result()
        
        # 1. 计算总体自相似度
        sim_scores = [n.self_similarity for n in all_nodes]
        avg_similarity = sum(sim_scores) / len(sim_scores)
        
        # 2. 阴阳平衡分析
        yin_yang_values = [n.yin_yang_ratio for n in all_nodes]
        avg_yin_yang = sum(yin_yang_values) / len(yin_yang_values)
        # 平衡度：与0.5的距离越近越好
        balance = 1.0 - abs(avg_yin_yang - 0.5) * 2
        
        # 3. IBL 厚度分析
        thicknesses = [n.interface_thickness for n in all_nodes]
        avg_thickness = sum(thicknesses) / len(thicknesses)
        
        if avg_thickness < self.ibl_optimal_min:
            ibl_status = 'too_thin'   # 边界消失，系统分离
        elif avg_thickness > self.ibl_optimal_max:
            ibl_status = 'too_thick'  # 边界僵化，系统死寂
        else:
            ibl_status = 'optimal'    # 半透膜，最优
        
        # 4. 螺旋相干度（跨层螺旋动量的方差越小，相干越高）
        spirals = [n.spiral_momentum for n in all_nodes]
        avg_spiral = sum(spirals) / len(spirals)
        spiral_variance = sum((s - avg_spiral) ** 2 for s in spirals) / len(spirals)
        spiral_coherence = 1.0 / (1.0 + spiral_variance * 10)
        
        # 5. 分形维数估算（基于嵌套分支结构）
        holon_depth = self._calc_depth(root)
        branch_factor = 2  # 每层2个分支
        if holon_depth > 1:
            fractal_dim = math.log(len(all_nodes)) / math.log(branch_factor * holon_depth)
            fractal_dim = max(1.0, min(2.0, fractal_dim))
        else:
            fractal_dim = 1.0
        
        # 6. 综合分形全息指数
        fhi = (avg_similarity * 0.35 + balance * 0.25 +
               (1 if ibl_status == 'optimal' else 0.5) * 0.2 +
               spiral_coherence * 0.2)
        
        # 主导尺度（节点最多的尺度）
        scale_counts = {s: len(nodes) for s, nodes in self.scale_map.items()
                        if nodes}
        dominant_scale = max(scale_counts, key=scale_counts.get) if scale_counts else HolonScale.SOCIAL
        
        # 生成洞见
        insight = self._generate_insight(avg_similarity, balance, ibl_status,
                                          spiral_coherence, fhi)
        
        return FractalHolismResult(
            scale_count=len(set(n.scale for n in all_nodes)),
            fractal_dimension=round(fractal_dim, 3),
            self_similarity_score=round(avg_similarity, 3),
            yin_yang_balance=round(balance, 3),
            ibl_thickness_avg=round(avg_thickness, 3),
            ibl_status=ibl_status,
            spiral_coherence=round(spiral_coherence, 3),
            holon_depth=holon_depth,
            dominant_scale=dominant_scale,
            fractal_holism_index=round(fhi, 3),
            insight=insight
        )

    def _collect_all_nodes(self, node: HolonNode, result: List[HolonNode]):
        """深度优先收集所有节点"""
        result.append(node)
        for child in node.sub_holons:
            self._collect_all_nodes(child, result)

    def _calc_depth(self, node: HolonNode, current: int = 1) -> int:
        """计算 Holon 嵌套深度"""
        if not node.sub_holons:
            return current
        return max(self._calc_depth(child, current + 1)
                   for child in node.sub_holons)

    def _generate_insight(self, similarity: float, balance: float,
                          ibl_status: str, spiral_coherence: float,
                          fhi: float) -> str:
        """基于分析结果生成语义洞见"""
        parts = []
        
        if fhi > 0.75:
            parts.append("系统呈现高度分形全息态——局部完美映射整体")
        elif fhi > 0.55:
            parts.append("系统具备中等分形全息性，跨尺度自相似结构清晰可辨")
        else:
            parts.append("系统分形全息性较弱，各尺度相对独立")
        
        if balance > 0.7:
            parts.append("阴阳高度平衡，太极场处于动态平衡点")
        elif balance < 0.4:
            parts.append("阴阳失衡显著，系统偏向单极化演化")
        
        ibl_map = {
            'optimal': 'IBL界面处于最优半透状态，跨尺度信息交换畅通',
            'too_thin': 'IBL界面过薄，系统存在层级分离风险（混沌边缘）',
            'too_thick': 'IBL界面过厚，边界僵化，演化能力受限'
        }
        parts.append(ibl_map[ibl_status])
        
        if spiral_coherence > 0.7:
            parts.append("螺旋动力学高度相干，系统保持稳定自组织演化")
        
        return '；'.join(parts)

    def _empty_result(self) -> FractalHolismResult:
        return FractalHolismResult(
            scale_count=0, fractal_dimension=1.0, self_similarity_score=0.0,
            yin_yang_balance=0.5, ibl_thickness_avg=0.5, ibl_status='optimal',
            spiral_coherence=0.5, holon_depth=1, dominant_scale=HolonScale.SOCIAL,
            fractal_holism_index=0.5, insight="无足够数据进行分形全息分析"
        )

    def process(self, text: str) -> Dict[str, Any]:
        """
        主处理接口：输入文本，返回分形全息分析结果
        
        参数：
            text: 输入文本
        返回：
            dict 包含 fractal_holism_index, yin_yang_balance, ibl_status 等
        """
        root = self.build_fractal_holon(text, depth=3)
        result = self.analyze_fractal_holism(root)
        
        # 清理网络以避免内存积累
        self.holon_network.clear()
        for k in self.scale_map:
            self.scale_map[k].clear()
        
        return {
            'module': 'FractalHolismField',
            'version': self.version,
            'fractal_holism_index': result.fractal_holism_index,
            'fractal_dimension': result.fractal_dimension,
            'self_similarity': result.self_similarity_score,
            'yin_yang_balance': result.yin_yang_balance,
            'yin_yang_state': (
                '阳主' if result.yin_yang_balance < 0.4 and
                sum(n.yin_yang_ratio for n in [root]) / max(1, 1) > 0.5
                else '阴阳平衡'
            ),
            'ibl_status': result.ibl_status,
            'ibl_thickness': result.ibl_thickness_avg,
            'spiral_coherence': result.spiral_coherence,
            'holon_depth': result.holon_depth,
            'scale_count': result.scale_count,
            'dominant_scale': result.dominant_scale.value,
            'insight': result.insight
        }


if __name__ == '__main__':
    engine = FractalHolismField()
    
    test_texts = [
        "太极场是宇宙的分形全息结构，阴阳在各尺度呈现自相似性",
        "请帮我实现一个Python算法优化系统性能",
        "意识是什么？智能的本质是时间中的动态共振还是空间的静态映射？"
    ]
    
    for text in test_texts:
        print(f"\n输入: {text[:40]}...")
        result = engine.process(text)
        print(f"  分形全息指数: {result['fractal_holism_index']}")
        print(f"  阴阳平衡度: {result['yin_yang_balance']}")
        print(f"  IBL状态: {result['ibl_status']}")
        print(f"  洞见: {result['insight'][:60]}...")
