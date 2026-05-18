#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宇宙五重设计偏好模块
Universe Five Design Preferences Module

基于《宇宙的五重设计偏好》文档实现
分形、螺旋、嵌套、微不对称、涌现 - 宇宙的五种基本语法

理论来源：
- 复合体理学"一现象，三视界"诠释法
- 相空间流形上的五类基本自同胚/自同态映射
- PTS(相位拓扑自激)模型
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DesignPreferenceType(Enum):
    """宇宙五重设计偏好类型"""
    FRACTAL = "fractal"              # 分形 - 迭代函数系统
    SPIRAL = "spiral"                # 螺旋 - SO(2)旋转与径向指数映射
    NESTING = "nesting"              # 嵌套 - O(3)同心对称
    MICRO_ASYMMETRY = "asymmetry"    # 微不对称 - 镜像破缺
    EMERGENCE = "emergence"          # 涌现 - 元胞自动机全局吸引子


@dataclass
class PreferenceSignature:
    """设计偏好特征签名"""
    preference_type: DesignPreferenceType
    strength: float           # 偏好强度 (0-1)
    dimension: float          # 特征维数 (Hausdorff维度/旋转参数等)
    entropy: float            # 信息熵
    description: str          # 描述


class FractalAnalyzer:
    """
    分形分析器
    基于迭代函数系统(IFS)理论
    - 分形 ≈ 相位奇异点的递归级联
    - Hausdorff维数 D_H 表征自相似度
    """
    
    def __init__(self):
        self.phi = (1 + math.sqrt(5)) / 2  # 黄金比例
    
    def compute_hausdorff_dimension(self, complexity_sequence: List[float]) -> float:
        """
        计算 Hausdorff 维数估计
        
        理论基础：宇宙分形的 D_H 与黄赤交角 ε ≈ 23.44° 有量子化关联
        预言：D_H 的分布满足 D_H ≈ 1 + sin²(ε/2)
        """
        if not complexity_sequence or len(complexity_sequence) < 2:
            return 1.0
        
        # 使用盒计数近似
        n = len(complexity_sequence)
        variance = sum((x - sum(complexity_sequence)/n)**2 for x in complexity_sequence) / n
        
        # 基于复杂度估算分形维数
        if variance < 1e-10:
            return 1.0  # 完全规律，维数=1
        
        # 经验估计：D_H ≈ 1 + log(variance)/log(n)
        if n > 1 and variance > 0:
            d_h = 1.0 + math.log(max(variance, 1e-10)) / math.log(n)
            return max(1.0, min(3.0, d_h))
        return 1.5
    
    def detect_self_similarity(self, data: List[float], scales: int = 3) -> Dict:
        """
        检测自相似性（多尺度分析）
        """
        n = len(data)
        if n < scales * 2:
            return {'self_similar': False, 'ratio': 0.0, 'dimension': 1.0}
        
        # 不同尺度计算均值和标准差
        scale_stats = []
        for scale in range(1, scales + 1):
            chunk_size = max(1, n // (2 ** scale))
            chunks = [data[i:i+chunk_size] for i in range(0, n, chunk_size)]
            if chunks:
                means = [sum(c)/len(c) for c in chunks if c]
                std = math.sqrt(sum((m - sum(means)/len(means))**2 for m in means) / len(means)) if len(means) > 1 else 0
                scale_stats.append(std)
        
        # 自相似性通过跨尺度比率判断
        if len(scale_stats) >= 2 and scale_stats[0] > 1e-10:
            ratio = scale_stats[-1] / scale_stats[0]
            is_similar = 0.3 < ratio < 3.0
        else:
            ratio = 1.0
            is_similar = False
        
        dimension = self.compute_hausdorff_dimension(data)
        return {
            'self_similar': is_similar,
            'ratio': ratio,
            'dimension': dimension,
            'phi_alignment': abs(ratio - self.phi) < 0.3  # 是否接近黄金比例
        }
    
    def apply_ifs_transformation(self, point: Tuple[float, float], 
                                  n_iters: int = 100) -> List[Tuple[float, float]]:
        """
        迭代函数系统变换（巴纳赫不动点）
        """
        points = [point]
        x, y = point
        
        # 简单的仿射IFS（类似Barnsley蕨叶）
        transforms = [
            (0.0, 0.0, 0.0, 0.16, 0.0, 0.0, 0.01),
            (0.85, 0.04, -0.04, 0.85, 0.0, 1.60, 0.85),
            (0.20, -0.26, 0.23, 0.22, 0.0, 1.60, 0.07),
            (-0.15, 0.28, 0.26, 0.24, 0.0, 0.44, 0.07),
        ]
        
        for _ in range(n_iters):
            r = random.random()
            cumulative = 0
            for a, b, c, d, e, f, prob in transforms:
                cumulative += prob
                if r <= cumulative:
                    x_new = a * x + b * y + e
                    y_new = c * x + d * y + f
                    x, y = x_new, y_new
                    points.append((x, y))
                    break
        
        return points


class SpiralAnalyzer:
    """
    螺旋分析器
    基于对数螺旋理论（SO(2)旋转 + 径向指数映射）
    - 螺旋 ≈ 角动量锁定的能量最优解
    - 对数螺旋是生长约束下的唯一等角解
    """
    
    def __init__(self):
        self.phi = (1 + math.sqrt(5)) / 2  # 黄金比例
        self.golden_angle = 2 * math.pi / (self.phi ** 2)  # 黄金角 ≈ 137.5°
    
    def compute_logarithmic_spiral_parameter(self, 
                                              radii: List[float], 
                                              angles: List[float]) -> Dict:
        """
        计算对数螺旋参数 r = a * e^(b*θ)
        """
        if len(radii) != len(angles) or len(radii) < 2:
            return {'is_spiral': False, 'a': 1.0, 'b': 0.0}
        
        # 线性回归估计参数
        log_r = [math.log(max(r, 1e-10)) for r in radii]
        
        n = len(angles)
        mean_theta = sum(angles) / n
        mean_log_r = sum(log_r) / n
        
        numerator = sum((angles[i] - mean_theta) * (log_r[i] - mean_log_r) for i in range(n))
        denominator = sum((angles[i] - mean_theta) ** 2 for i in range(n))
        
        if abs(denominator) < 1e-10:
            return {'is_spiral': False, 'a': 1.0, 'b': 0.0}
        
        b = numerator / denominator
        a = math.exp(mean_log_r - b * mean_theta)
        
        # 判断是否接近黄金螺旋
        is_golden = abs(b - math.log(self.phi) / (math.pi/2)) < 0.1
        
        return {
            'is_spiral': True,
            'a': a,
            'b': b,
            'is_golden': is_golden,
            'growth_rate': b
        }
    
    def generate_fibonacci_spiral(self, n_points: int = 20) -> List[Tuple[float, float]]:
        """生成斐波那契螺旋（模拟向日葵种子排列）"""
        points = []
        for i in range(n_points):
            angle = i * self.golden_angle
            radius = math.sqrt(i + 1)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))
        return points
    
    def analyze_query_spiral(self, query_tokens: List[str]) -> Dict:
        """
        分析查询中的螺旋性（语义层面的递进发展）
        """
        n = len(query_tokens)
        if n < 3:
            return {'spiral_depth': 0, 'progression_type': 'linear'}
        
        # 简单启发：查询中词语的语义"层叠"程度
        unique_ratio = len(set(query_tokens)) / n
        progression_index = 1 - unique_ratio  # 重复度越高，螺旋性越强
        
        return {
            'spiral_depth': progression_index,
            'progression_type': 'logarithmic' if progression_index > 0.3 else 'linear',
            'golden_ratio_present': abs(n / max(len(set(query_tokens)), 1) - self.phi) < 0.5
        }


class NestingAnalyzer:
    """
    嵌套分析器
    基于球对称势场中的径向节点壳层
    - 嵌套 ≈ O(3)同心对称的多重稳定解
    - 每层对应一个"量子数"（主量子数n）
    """
    
    def __init__(self, max_levels: int = 5):
        self.max_levels = max_levels
        self.nesting_levels: List[Dict] = []
    
    def add_nesting_level(self, content: Any, level: int, 
                           metadata: Optional[Dict] = None) -> None:
        """添加嵌套层"""
        if level > self.max_levels:
            level = self.max_levels
        
        self.nesting_levels.append({
            'level': level,
            'content': content,
            'metadata': metadata or {},
            'quantum_number': level,      # 对应主量子数
            'energy': 1.0 / (level ** 2)  # 氢原子能级 E_n = -1/n²
        })
    
    def compute_nesting_depth(self) -> Dict:
        """计算嵌套深度和能量分布"""
        if not self.nesting_levels:
            return {'depth': 0, 'energy_levels': [], 'coherence': 0.0}
        
        max_level = max(l['level'] for l in self.nesting_levels)
        energy_levels = [1.0 / (n**2) for n in range(1, max_level + 1)]
        
        # 相干性：各层是否形成稳定的嵌套结构
        level_counts = {}
        for entry in self.nesting_levels:
            lv = entry['level']
            level_counts[lv] = level_counts.get(lv, 0) + 1
        
        # 嵌套相干性 = 层间分布均匀度
        total = len(self.nesting_levels)
        coherence = len(level_counts) / max_level if max_level > 0 else 0.0
        
        return {
            'depth': max_level,
            'energy_levels': energy_levels,
            'coherence': coherence,
            'level_distribution': level_counts
        }
    
    def analyze_knowledge_nesting(self, concepts: List[str]) -> Dict:
        """分析概念知识的嵌套层次"""
        # 简单启发：按概念长度/复杂度分层
        for i, concept in enumerate(concepts):
            complexity = len(concept.split()) + concept.count('，') + concept.count(',')
            level = min(complexity, self.max_levels)
            self.add_nesting_level(concept, level, {'index': i})
        
        return self.compute_nesting_depth()


class MicroAsymmetryDetector:
    """
    微不对称检测器
    基于Ginzburg-Landau对称破缺理论
    - 微不对称 ≈ CP破坏导致的相位空间倾斜
    - 当外部耦合κ > κ_c时，系统选择单一手性
    """
    
    def __init__(self, critical_coupling: float = 0.5):
        self.kappa_c = critical_coupling  # 临界耦合常数
    
    def detect_symmetry_breaking(self, data: List[float]) -> Dict:
        """
        检测数据中的对称破缺
        
        基于Ginzburg-Landau势能：V(φ) = α|φ|² + β|φ|⁴
        当α < 0时，发生自发对称破缺
        """
        if not data or len(data) < 4:
            return {'broken': False, 'skewness': 0.0, 'handedness': 'none'}
        
        n = len(data)
        mean = sum(data) / n
        
        # 计算偏度（三阶矩）
        variance = sum((x - mean)**2 for x in data) / n
        std = math.sqrt(max(variance, 1e-10))
        skewness = sum(((x - mean) / std)**3 for x in data) / n
        
        # 检测峰度（四阶矩）
        kurtosis = sum(((x - mean) / std)**4 for x in data) / n - 3
        
        # 判断手性（正负偏度对应左/右手性）
        is_broken = abs(skewness) > 0.5
        handedness = 'left' if skewness < -0.5 else ('right' if skewness > 0.5 else 'none')
        
        return {
            'broken': is_broken,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'handedness': handedness,
            'alpha_sign': 'negative' if kurtosis < 0 else 'positive',  # GL参数α符号
            'coupling_strength': abs(skewness)
        }
    
    def compute_chirality(self, sequence: str) -> Dict:
        """
        计算字符串序列的手性（左/右旋性）
        """
        # 分析字符分布的对称性
        char_counts = {}
        for c in sequence:
            char_counts[c] = char_counts.get(c, 0) + 1
        
        counts = list(char_counts.values())
        total = sum(counts)
        
        if total == 0:
            return {'chirality': 0.0, 'dominant_handedness': 'none'}
        
        # 归一化频率
        freqs = sorted([c/total for c in counts])
        n = len(freqs)
        
        # 计算分布的手性：将分布与其镜像比较
        mid = n // 2
        left_sum = sum(freqs[:mid])
        right_sum = sum(freqs[mid:])
        
        chirality = (right_sum - left_sum) / (right_sum + left_sum + 1e-10)
        
        return {
            'chirality': chirality,
            'dominant_handedness': 'right' if chirality > 0.1 else ('left' if chirality < -0.1 else 'balanced'),
            'symmetry_breaking_degree': abs(chirality)
        }


class EmergenceAnalyzer:
    """
    涌现分析器
    基于元胞自动机和复杂系统理论
    - 涌现 ≈ 非线性耦合超过阈值，线性失效
    - 涌现 = 局部规则下宏观有序的自发出现
    """
    
    def __init__(self, emergence_threshold: float = 0.618):
        self.threshold = emergence_threshold  # 涌现阈值（黄金分割）
        self.interaction_history: List[Dict] = []
    
    def measure_emergence_index(self, local_states: List[float], 
                                  global_state: float) -> Dict:
        """
        测量涌现指数
        
        涌现指数 = 全局状态与局部状态均值的偏离程度
        """
        if not local_states:
            return {'emergence_index': 0.0, 'is_emergent': False}
        
        local_mean = sum(local_states) / len(local_states)
        local_max = max(local_states)
        
        # 涌现指数：全局状态超出局部状态的程度
        if local_max > 1e-10:
            emergence_index = abs(global_state - local_mean) / local_max
        else:
            emergence_index = 0.0
        
        return {
            'emergence_index': emergence_index,
            'is_emergent': emergence_index > self.threshold,
            'complexity_boost': global_state / max(local_mean, 1e-10),
            'local_mean': local_mean,
            'global_state': global_state
        }
    
    def simulate_cellular_automaton(self, initial_state: List[int], 
                                     rule_number: int = 110, 
                                     steps: int = 10) -> List[List[int]]:
        """
        模拟元胞自动机（Rule 110支持普适计算，是涌现的典型代表）
        """
        # 将规则数转换为规则表
        rule_binary = format(rule_number, '08b')
        rule_map = {}
        for i, bit in enumerate(reversed(rule_binary)):
            left = (i >> 2) & 1
            center = (i >> 1) & 1
            right = i & 1
            rule_map[(left, center, right)] = int(bit)
        
        history = [initial_state[:]]
        current = initial_state[:]
        n = len(current)
        
        for _ in range(steps):
            next_state = []
            for j in range(n):
                left = current[(j - 1) % n]
                center = current[j]
                right = current[(j + 1) % n]
                next_state.append(rule_map.get((left, center, right), 0))
            current = next_state
            history.append(current[:])
        
        return history
    
    def detect_phase_transition(self, complexity_values: List[float]) -> Dict:
        """
        检测涌现的相变点
        基于"涌现 = 非线性系统超过临界点"的原理
        """
        if len(complexity_values) < 3:
            return {'transition_detected': False, 'transition_index': -1}
        
        n = len(complexity_values)
        max_delta = 0
        transition_idx = -1
        
        # 寻找最大变化率的点（相变往往发生在此）
        for i in range(1, n - 1):
            delta = abs(complexity_values[i+1] - complexity_values[i-1])
            if delta > max_delta:
                max_delta = delta
                transition_idx = i
        
        mean = sum(complexity_values) / n
        std = math.sqrt(sum((x - mean)**2 for x in complexity_values) / n)
        
        return {
            'transition_detected': max_delta > std,
            'transition_index': transition_idx,
            'max_gradient': max_delta,
            'variance': std
        }


class UniverseFivePreferences:
    """
    宇宙五重设计偏好分析系统
    
    整合分形、螺旋、嵌套、微不对称、涌现五大宇宙基本语法
    用于分析任意数据/查询中的"宇宙级结构偏好"
    """
    
    def __init__(self):
        self.fractal = FractalAnalyzer()
        self.spiral = SpiralAnalyzer()
        self.nesting = NestingAnalyzer()
        self.asymmetry = MicroAsymmetryDetector()
        self.emergence = EmergenceAnalyzer()
        
        print("宇宙五重设计偏好分析系统初始化完成")
    
    def analyze(self, query: str, data: Optional[List[float]] = None) -> Dict:
        """
        对查询进行五重设计偏好分析
        
        参数:
            query: 查询字符串
            data: 可选数值数据
            
        返回:
            五重偏好分析报告
        """
        if data is None:
            # 从查询生成模拟数值数据
            data = [ord(c) / 128.0 for c in query[:50]]
        
        tokens = query.split()
        
        # 1. 分形分析
        fractal_result = self.fractal.detect_self_similarity(data)
        
        # 2. 螺旋分析
        spiral_result = self.spiral.analyze_query_spiral(tokens)
        
        # 3. 嵌套分析
        nesting_result = self.nesting.analyze_knowledge_nesting(tokens)
        
        # 4. 微不对称分析
        asymmetry_result = self.asymmetry.detect_symmetry_breaking(data)
        chirality = self.asymmetry.compute_chirality(query)
        
        # 5. 涌现分析
        local_states = data[:10] if len(data) >= 10 else data
        global_complexity = len(set(tokens)) / max(len(tokens), 1)
        emergence_result = self.emergence.measure_emergence_index(local_states, global_complexity)
        
        # 综合评分
        preference_scores = {
            'fractal': fractal_result.get('dimension', 1.0) / 3.0,
            'spiral': spiral_result.get('spiral_depth', 0.0),
            'nesting': nesting_result.get('coherence', 0.0),
            'asymmetry': asymmetry_result.get('coupling_strength', 0.0),
            'emergence': emergence_result.get('emergence_index', 0.0)
        }
        
        dominant = max(preference_scores, key=preference_scores.get)
        overall_score = sum(preference_scores.values()) / 5
        
        return {
            'fractal': fractal_result,
            'spiral': spiral_result,
            'nesting': nesting_result,
            'asymmetry': {**asymmetry_result, 'chirality': chirality},
            'emergence': emergence_result,
            'preference_scores': preference_scores,
            'dominant_preference': dominant,
            'overall_complexity': overall_score,
            'phi_resonance': abs(overall_score - (1/1.618)) < 0.1  # 是否接近黄金分割点
        }
    
    def get_interpretation(self, analysis: Dict) -> str:
        """生成五重设计偏好分析的自然语言解释"""
        dominant = analysis.get('dominant_preference', 'unknown')
        score = analysis.get('overall_complexity', 0.0)
        phi_res = analysis.get('phi_resonance', False)
        
        interpretation_map = {
            'fractal': '分形自相似结构（多尺度递归嵌入）',
            'spiral': '螺旋增长模式（角动量锁定的对数展开）',
            'nesting': '嵌套层次组织（量子化壳层分级）',
            'asymmetry': '微不对称选择（手性相位破缺）',
            'emergence': '涌现复杂性（非线性临界相变）'
        }
        
        desc = interpretation_map.get(dominant, '未知偏好')
        phi_note = "（处于黄金分割共振点！）" if phi_res else ""
        
        return (f"主导偏好：{desc}，综合复杂度={score:.3f}{phi_note}。"
                f"分形维数D={analysis.get('fractal', {}).get('dimension', 1.0):.2f}，"
                f"螺旋深度={analysis.get('spiral', {}).get('spiral_depth', 0.0):.2f}，"
                f"嵌套相干={analysis.get('nesting', {}).get('coherence', 0.0):.2f}，"
                f"手性={analysis.get('asymmetry', {}).get('chirality', {}).get('dominant_handedness', 'none')}，"
                f"涌现指数={analysis.get('emergence', {}).get('emergence_index', 0.0):.2f}")


if __name__ == "__main__":
    print("=" * 60)
    print("宇宙五重设计偏好分析系统测试")
    print("=" * 60)
    
    analyzer = UniverseFivePreferences()
    
    test_cases = [
        "什么是AGI？",
        "信息-几何-意识三元共振如何驱动宇宙演化？",
        "分形维数与黎曼猜想的关系是什么？"
    ]
    
    for query in test_cases:
        print(f"\n查询: {query}")
        result = analyzer.analyze(query)
        print(f"  解释: {analyzer.get_interpretation(result)}")
    
    print("\n测试完成!")
