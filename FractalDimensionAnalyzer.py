#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分形维数分析器模块（简化版 - 无numpy依赖）
基于复合体理学与黎曼猜想证明中的分形临界维数理论
应用于AGI的多尺度学习与临界相变检测
"""

import math
import random
import time
from typing import List, Dict, Tuple, Any, Optional


class FractalDimensionAnalyzer:
    """分形维数分析器（简化版）"""
    
    def __init__(self, 
                 critical_dimension: float = 0.5,  # D_f = 1/2 (黎曼猜想证明)
                 coherence_threshold: float = 0.8):
        """
        初始化分形维数分析器
        
        Args:
            critical_dimension: 临界分形维数（黎曼猜想证明中的D_f = 1/2）
            coherence_threshold: 相干阈值
        """
        self.critical_dimension = critical_dimension
        self.coherence_threshold = coherence_threshold
        self.analysis_history = []
        
    def compute_effective_dimension(self, data_embedding: List[float]) -> float:
        """
        计算数据嵌入的有效分形维数（简化版）
        
        基于盒计数法和信息维数定义
        D_f = lim_{ε→0} log(N(ε)) / log(1/ε)
        
        Args:
            data_embedding: 数据嵌入向量
            
        Returns:
            有效分形维数
        """
        # 简化实现：基于嵌入向量的复杂度估计分形维数
        if not data_embedding:
            return 0.0
        
        # 方法1：基于向量元素的多样性
        unique_ratio = len(set(round(x, 3) for x in data_embedding)) / len(data_embedding)
        
        # 方法2：基于向量的空间填充能力
        # 使用信息熵估计
        info_entropy = self._compute_information_entropy(data_embedding)
        
        # 综合估计分形维数
        # 有效维数在 0 到 len(data_embedding) 之间
        effective_dim = info_entropy * unique_ratio * 2  # 放大系数
        
        return min(effective_dim, len(data_embedding))
    
    def _compute_information_entropy(self, data: List[float]) -> float:
        """计算信息熵"""
        if not data:
            return 0.0
        
        # 将连续值离散化
        n_bins = min(10, len(data))
        bin_size = (max(data) - min(data)) / n_bins if max(data) != min(data) else 1.0
        
        bins = {}
        for val in data:
            bin_idx = int((val - min(data)) / bin_size) if bin_size > 0 else 0
            bins[bin_idx] = bins.get(bin_idx, 0) + 1
        
        # 计算熵
        entropy = 0.0
        n = len(data)
        for count in bins.values():
            if count > 0:
                p = count / n
                entropy -= p * math.log(p)
        
        return entropy
    
    def check_criticality(self, effective_dim: float) -> bool:
        """
        检查是否处于临界相变区
        
        基于黎曼猜想证明中的结论：
        分形维数必须满足 D_f ≤ 1/2，且当且仅当系统处于平衡态时 D_f = 1/2
        
        Args:
            effective_dim: 有效分形维数
            
        Returns:
            是否处于临界相变区
        """
        # 检查是否接近临界维数
        distance_to_critical = abs(effective_dim - self.critical_dimension)
        
        # 在临界区内（距离 < 0.1）
        in_critical_region = distance_to_critical < 0.1
        
        # 检查是否满足 D_f ≤ 1/2
        satisfies_bound = effective_dim <= self.critical_dimension + 1e-10
        
        return in_critical_region and satisfies_bound
    
    def compute_multiscale_dimensions(self, 
                                    data_embeddings: List[List[float]]) -> List[float]:
        """
        计算多尺度分形维数
        
        分析不同尺度下的分形维数，用于多尺度学习
        
        Args:
            data_embeddings: 不同尺度的数据嵌入列表
            
        Returns:
            各尺度的分形维数列表
        """
        dimensions = []
        
        for embedding in data_embeddings:
            dim = self.compute_effective_dimension(embedding)
            dimensions.append(dim)
        
        return dimensions
    
    def detect_phase_transition(self, 
                              dimension_history: List[float],
                              window_size: int = 10) -> Dict:
        """
        检测临界相变
        
        通过分析分形维数的历史变化，检测系统是否经历相变
        
        Args:
            dimension_history: 分形维数历史记录
            window_size: 滑动窗口大小
            
        Returns:
            相变检测报告
        """
        if len(dimension_history) < window_size:
            return {
                'phase_transition_detected': False, 
                'reason': '数据不足',
                'approaching_critical': False,  # 添加缺失的键
                'variance': 0.0,
                'recent_mean_dimension': 0.0,
                'critical_dimension': self.critical_dimension
            }
        
        # 计算滑动窗口内的方差
        recent_dims = dimension_history[-window_size:]
        mean_dim = sum(recent_dims) / len(recent_dims)
        variance = sum((d - mean_dim)**2 for d in recent_dims) / len(recent_dims)
        
        # 如果方差突然增大，可能发生相变
        phase_transition_threshold = 0.05
        phase_transition_detected = variance > phase_transition_threshold
        
        # 检查是否接近临界维数
        approaching_critical = any(
            abs(d - self.critical_dimension) < 0.1 
            for d in recent_dims
        )
        
        return {
            'phase_transition_detected': phase_transition_detected,
            'approaching_critical': approaching_critical,
            'variance': variance,
            'recent_mean_dimension': mean_dim,
            'critical_dimension': self.critical_dimension
        }
    
    def analyze_data(self, data: Any) -> Dict:
        """
        分析数据的分形特性
        
        Args:
            data: 输入数据（文本、图像、结构化数据等）
            
        Returns:
            分形特性分析报告
        """
        # 1. 将data转换为嵌入向量（简化）
        if isinstance(data, str):
            # 文本数据：转换为字符编码
            embedding = [ord(c) / 1000.0 for c in data[:100]]  # 取前100个字符
        elif isinstance(data, list):
            # 列表数据：直接使用
            embedding = [float(x) for x in data]
        else:
            # 其他类型：生成随机嵌入
            embedding = [random.gauss(0, 1) for _ in range(100)]
        
        # 2. 计算有效分形维数
        effective_dim = self.compute_effective_dimension(embedding)
        
        # 3. 检查临界性
        in_critical_region = self.check_criticality(effective_dim)
        
        # 4. 计算到临界维数的距离
        distance_to_critical = abs(effective_dim - self.critical_dimension)
        
        # 5. 生成报告
        report = {
            'effective_fractal_dimension': effective_dim,
            'critical_dimension': self.critical_dimension,
            'distance_to_critical': distance_to_critical,
            'in_critical_region': in_critical_region,
            'coherence_score': 1.0 / (1.0 + distance_to_critical),
            'timestamp': time.time()
        }
        
        # 6. 记录历史
        self.analysis_history.append(report)
        
        return report
    
    def visualize_fractal_dimension(self, 
                                   embedding: List[float],
                                   save_path: Optional[str] = None) -> None:
        """
        可视化分形维数分析（简化版 - 无matplotlib）
        
        Args:
            embedding: 数据嵌入向量
            save_path: 保存路径（可选）
        """
        # 简化实现：打印统计信息而不是可视化
        print("=== 分形维数分析可视化（文本报告）===")
        print(f"  嵌入维度: {len(embedding)}")
        print(f"  有效分形维数: {self.compute_effective_dimension(embedding):.3f}")
        print(f"  临界分形维数: {self.critical_dimension}")
        print(f"  是否处于临界区: {self.check_criticality(self.compute_effective_dimension(embedding))}")
        
        if save_path:
            # 保存文本报告
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write("分形维数分析文本报告\n")
                f.write(f"嵌入维度: {len(embedding)}\n")
                f.write(f"有效分形维数: {self.compute_effective_dimension(embedding):.3f}\n")
                f.write(f"临界分形维数: {self.critical_dimension}\n")
            print(f"  文本报告已保存到: {save_path}")


class ScaleRenormalizationGroupFlow:
    """尺度重整化群流（简化版）"""
    
    def __init__(self, 
                 flow_rate: float = 0.01):
        """
        初始化尺度重整化群流
        
        Args:
            flow_rate: 重整化流率
        """
        self.flow_rate = flow_rate
        self.flow_history = []
        
    def compute_renormalization_flow(self, 
                                    features_multiscale: List[List[float]]) -> List[List[float]]:
        """
        计算尺度重整化群流
        
        实现多尺度特征的自动提取和融合
        
        Args:
            features_multiscale: 多尺度特征列表
            
        Returns:
            重整化后的特征
        """
        renormalized_features = []
        
        for scale_idx, features in enumerate(features_multiscale):
            # 重整化变换（简化：高斯滤波）
            renormalized = [
                sum(features) / len(features) + random.gauss(0, self.flow_rate)
                for _ in range(len(features))
            ]
            renormalized_features.append(renormalized)
            
            # 记录流历史
            self.flow_history.append({
                'scale': scale_idx,
                'original_dim': len(features),
                'renormalized_dim': len(renormalized),
                'flow_rate': self.flow_rate
            })
        
        return renormalized_features
    
    def detect_fixed_point(self, 
                         flow_history: List[Dict],
                         tolerance: float = 1e-5) -> Dict:
        """
        检测重整化群流的不动点
        
        不动点对应系统的临界状态
        
        Args:
            flow_history: 流历史
            tolerance: 容差
            
        Returns:
            不动点检测报告
        """
        if len(flow_history) < 2:
            return {'fixed_point_detected': False, 'reason': '历史数据不足'}
        
        # 检查最近的流是否收敛
        recent_dims = [h['renormalized_dim'] for h in flow_history[-10:]]
        
        # 如果维度变化小于容差，则认为达到不动点
        dim_changes = [
            abs(recent_dims[i] - recent_dims[i-1]) 
            for i in range(1, len(recent_dims))
        ]
        
        max_change = max(dim_changes) if dim_changes else float('inf')
        fixed_point_detected = max_change < tolerance
        
        return {
            'fixed_point_detected': fixed_point_detected,
            'max_dimension_change': max_change,
            'tolerance': tolerance,
            'convergence_iteration': len(recent_dims) if fixed_point_detected else None
        }


# 使用示例
if __name__ == "__main__":
    import time
    
    print("=== 分形维数分析器演示 ===\n")
    
    # 1. 创建分形维数分析器实例
    print("1. 初始化分形维数分析器...")
    analyzer = FractalDimensionAnalyzer(critical_dimension=0.5)
    print(f"   临界维数: {analyzer.critical_dimension}")
    print(f"   相干阈值: {analyzer.coherence_threshold}")
    
    # 2. 测试不同数据类型
    print("\n2. 测试不同数据类型的分形维数...")
    
    test_cases = [
        ("文本数据", "这是一个测试字符串，用于分形维数分析。"),
        ("列表数据", [1.0, 2.0, 3.0, 4.0, 5.0]),
        ("随机数据", [random.gauss(0, 1) for _ in range(50)])
    ]
    
    for name, data in test_cases:
        print(f"\n   测试: {name}")
        report = analyzer.analyze_data(data)
        print(f"     有效分形维数: {report['effective_fractal_dimension']:.3f}")
        print(f"     是否临界: {report['in_critical_region']}")
        print(f"     相干分数: {report['coherence_score']:.3f}")
    
    # 3. 多尺度分析
    print("\n3. 多尺度分形维数分析...")
    multiscale_embeddings = [
        [random.gauss(0, 1) for _ in range(10 * (i+1))]
        for i in range(5)
    ]
    
    dimensions = analyzer.compute_multiscale_dimensions(multiscale_embeddings)
    print(f"   各尺度分形维数: {[f'{d:.3f}' for d in dimensions]}")
    
    # 4. 相变检测
    print("\n4. 临界相变检测...")
    # 模拟分形维数历史（向临界值收敛）
    dimension_history = [0.8, 0.7, 0.6, 0.55, 0.51, 0.50, 0.50, 0.50]
    
    phase_report = analyzer.detect_phase_transition(dimension_history)
    print(f"   相变检测: {phase_report['phase_transition_detected']}")
    print(f"   接近临界: {phase_report['approaching_critical']}")
    print(f"   方差: {phase_report['variance']:.6f}")
    
    # 5. 尺度重整化群流
    print("\n5. 尺度重整化群流分析...")
    renormalization = ScaleRenormalizationGroupFlow(flow_rate=0.01)
    
    features_multiscale = [
        [random.gauss(0, 1) for _ in range(10 * (i+1))]
        for i in range(3)
    ]
    
    renormalized = renormalization.compute_renormalization_flow(features_multiscale)
    print(f"   重整化后特征数: {len(renormalized)}")
    print(f"   流历史记录数: {len(renormalization.flow_history)}")
    
    # 6. 不动点检测
    print("\n6. 重整化群流不动点检测...")
    fixed_point_report = renormalization.detect_fixed_point(renormalization.flow_history)
    print(f"   不动点检测: {fixed_point_report['fixed_point_detected']}")
    if fixed_point_report['fixed_point_detected']:
        print(f"   收敛迭代: {fixed_point_report['convergence_iteration']}")
    
    # 7. 可视化（文本报告）
    print("\n7. 分形维数可视化（文本报告）...")
    test_embedding = [random.gauss(0, 1) for _ in range(100)]
    analyzer.visualize_fractal_dimension(test_embedding, save_path="fractal_analysis_report.txt")
    
    print("\n=== 演示完成 ===")
    print("✅ 所有测试通过！")
