#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反单调性信息公理应用模块
基于复合体理学与黎曼猜想证明中的反单调性信息公理与奇正不等式

核心思想：
1. 反单调性信息公理：素数集（离散、测度为零）的信息量大于自然数集（连续、测度无穷）
2. 奇正不等式：揭示了离散与连续之间的信息不对称性
3. 应用：从低信息量数据中提取高信息量特征
"""

import math
import random
import zlib
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from collections import Counter


class KolmogorovComplexity:
    """
    柯尔莫哥洛夫复杂度估算器
    
    使用压缩算法近似计算字符串的柯尔莫哥洛夫复杂度
    K(x) ≈ len(zlib.compress(x.encode()))
    """
    
    def __init__(self, compression_level: int = 9):
        """
        初始化柯尔莫哥洛夫复杂度估算器
        
        参数:
            compression_level: 压缩级别(0-9)
        """
        self.compression_level = compression_level
        
    def compute(self, data: str) -> int:
        """
        计算数据的柯尔莫哥洛夫复杂度
        
        参数:
            data: 输入数据（字符串）
            
        返回:
            估算的柯尔莫哥洛夫复杂度（字节数）
        """
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = str(data).encode('utf-8')
            
        # 使用zlib压缩近似K(x)
        compressed = zlib.compress(data_bytes, self.compression_level)
        return len(compressed)
        
    def normalized_complexity(self, data: str) -> float:
        """
        计算归一化柯尔莫哥洛夫复杂度
        
        返回:
            归一化复杂度（0-1之间，1表示最大复杂度）
        """
        if len(data) == 0:
            return 0.0
            
        k = self.compute(data)
        # 归一化：K(x) / len(x)
        return k / len(data.encode('utf-8'))


class PrimeLikeStructureDetector:
    """
    类素数结构检测器
    
    检测数据中的"素数集"式结构：
    - 离散性：数据点之间不连续
    - 低测度：在全局空间中占比很小
    - 高信息量：包含丰富的结构化信息
    """
    
    def __init__(self, threshold_discrete: float = 0.3, 
                 threshold_low_measure: float = 0.1):
        """
        初始化类素数结构检测器
        
        参数:
            threshold_discrete: 离散性阈值
            threshold_low_measure: 低测度阈值
        """
        self.threshold_discrete = threshold_discrete
        self.threshold_low_measure = threshold_low_measure
        
    def detect(self, data_set: List[Any], 
               global_space: Optional[List[Any]] = None) -> Dict:
        """
        检测数据集中的类素数结构
        
        参数:
            data_set: 待检测的数据集
            global_space: 全局空间（如果为None，则使用data_set本身）
            
        返回:
            {
                'is_prime_like': bool,  # 是否为类素数结构
                'discreteness': float,   # 离散性度量
                'measure': float,         # 测度（在全局空间中的占比）
                'info_content': float    # 信息量
            }
        """
        if not data_set:
            return {
                'is_prime_like': False,
                'discreteness': 0.0,
                'measure': 0.0,
                'info_content': 0.0
            }
            
        # 1. 计算离散性
        discreteness = self._compute_discreteness(data_set)
        
        # 2. 计算测度
        if global_space:
            measure = len(data_set) / len(global_space)
        else:
            # 如果没有提供全局空间，则假设data_set是全局空间的一个稀疏采样
            measure = 1.0  # 待定：需要更复杂的方法估算测度
            
        # 3. 计算信息量（使用柯尔莫哥洛夫复杂度）
        info_content = self._compute_info_content(data_set)
        
        # 4. 判断是否类素数结构
        is_prime_like = (
            discreteness > self.threshold_discrete and 
            measure < self.threshold_low_measure
        )
        
        return {
            'is_prime_like': is_prime_like,
            'discreteness': discreteness,
            'measure': measure,
            'info_content': info_content
        }
        
    def _compute_discreteness(self, data_set: List[Any]) -> float:
        """
        计算数据集的离散性
        
        方法：计算数据点之间的平均距离，距离越大，离散性越高
        """
        if len(data_set) < 2:
            return 1.0
            
        # 简化：假设数据可以转换为数值
        try:
            numeric_data = [float(x) for x in data_set]
            numeric_data.sort()
            
            # 计算相邻点的距离
            distances = [
                abs(numeric_data[i] - numeric_data[i-1]) 
                for i in range(1, len(numeric_data))
            ]
            
            avg_distance = sum(distances) / len(distances)
            
            # 归一化：假设最大合理距离为100
            normalized_discreteness = min(avg_distance / 100.0, 1.0)
            return normalized_discreteness
            
        except (ValueError, TypeError):
            # 如果不是数值数据，则使用其他方法（如编辑距离）
            return self._compute_discreteness_symbolic(data_set)
            
    def _compute_discreteness_symbolic(self, data_set: List[str]) -> float:
        """符号数据的离散性计算（简化版）"""
        if len(data_set) < 2:
            return 1.0
            
        # 计算平均编辑距离
        total_distance = 0
        count = 0
        for i in range(len(data_set)):
            for j in range(i+1, len(data_set)):
                dist = self._edit_distance(data_set[i], data_set[j])
                total_distance += dist
                count += 1
                
        avg_distance = total_distance / max(count, 1)
        
        # 归一化：假设最大编辑距离为100
        return min(avg_distance / 100.0, 1.0)
        
    def _edit_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离（Levenshtein距离）"""
        len1, len2 = len(s1), len(s2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
            
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # 删除
                    dp[i][j-1] + 1,      # 插入
                    dp[i-1][j-1] + cost   # 替换
                )
                
        return dp[len1][len2]
        
    def _compute_info_content(self, data_set: List[Any]) -> float:
        """计算数据集的信息量"""
        kolmogorov = KolmogorovComplexity()
        
        # 将数据集合并为一个字符串
        data_str = ' '.join(str(x) for x in data_set)
        
        # 计算柯尔莫哥洛夫复杂度
        complexity = kolmogorov.compute(data_str)
        
        # 归一化：除以数据长度
        if len(data_str) > 0:
            return complexity / len(data_str.encode('utf-8'))
        else:
            return 0.0


class AntiMonotonicityInformation:
    """
    反单调性信息公理应用
    
    核心功能：
    1. 应用"反单调性信息公理"：I(素数集) > I(自然数集)
    2. 设计"信息不对称性提取算法"
    3. 建立"信息压缩-解压不对称性"
    """
    
    def __init__(self):
        self.kolmogorov = KolmogorovComplexity()
        self.prime_detector = PrimeLikeStructureDetector()
        
    def compute_information_content(self, data_set: List[Any]) -> Dict:
        """
        计算数据集的信息量
        
        参数:
            data_set: 数据集
            
        返回:
            {
                'kolmogorov_complexity': int,  # 柯尔莫哥洛夫复杂度
                'normalized_complexity': float, # 归一化复杂度
                'is_prime_like': bool,         # 是否为类素数结构
                'info_density': float          # 信息密度
            }
        """
        # 转换为字符串
        data_str = ' '.join(str(x) for x in data_set)
        
        # 计算柯尔莫哥洛夫复杂度
        k_complexity = self.kolmogorov.compute(data_str)
        n_complexity = self.kolmogorov.normalized_complexity(data_str)
        
        # 检测是否为类素数结构
        prime_like_check = self.prime_detector.detect(data_set)
        
        # 计算信息密度（信息量/数据量）
        data_size = len(data_str.encode('utf-8'))
        info_density = k_complexity / max(data_size, 1)
        
        return {
            'kolmogorov_complexity': k_complexity,
            'normalized_complexity': n_complexity,
            'is_prime_like': prime_like_check['is_prime_like'],
            'info_density': info_density,
            'prime_like_details': prime_like_check
        }
        
    def extract_high_info_from_low_info(self, low_info_data: List[Any], 
                                        method: str = 'prime_like') -> List[Any]:
        """
        从低信息量数据中提取高信息量特征
        
        参数:
            low_info_data: 低信息量数据
            method: 提取方法（'prime_like' 或 'compression'）
            
        返回:
            高信息量特征列表
        """
        if method == 'prime_like':
            return self._extract_prime_like_structures(low_info_data)
        elif method == 'compression':
            return self._extract_by_compression(low_info_data)
        else:
            raise ValueError(f"Unknown method: {method}")
            
    def _extract_prime_like_structures(self, data: List[Any]) -> List[Any]:
        """
        提取类素数结构
        
        方法：
        1. 将数据分割成多个子集
        2. 检测每个子集是否为类素数结构
        3. 返回所有类素数子集
        """
        if len(data) < 2:
            return data
            
        high_info_features = []
        
        # 尝试不同的分割大小
        for subset_size in [2, 3, 5, 8, 13]:  # 斐波那契数列
            if subset_size > len(data):
                continue
                
            # 滑动窗口提取子集
            for i in range(len(data) - subset_size + 1):
                subset = data[i:i+subset_size]
                
                # 检测是否为类素数结构
                check = self.prime_detector.detect(subset, global_space=data)
                
                if check['is_prime_like']:
                    high_info_features.append({
                        'subset': subset,
                        'info_content': check['info_content'],
                        'discreteness': check['discreteness'],
                        'measure': check['measure']
                    })
                    
        # 按信息量排序
        high_info_features.sort(key=lambda x: x['info_content'], reverse=True)
        
        # 返回前N个高信息量特征
        top_n = min(10, len(high_info_features))
        return [f['subset'] for f in high_info_features[:top_n]]
        
    def _extract_by_compression(self, data: List[Any]) -> List[Any]:
        """
        通过压缩比提取高信息量特征
        
        方法：
        1. 计算整体数据的压缩比
        2. 逐个移除数据点，观察压缩比变化
        3. 移除后压缩比显著增加的点包含高信息量
        """
        if len(data) < 2:
            return data
            
        # 计算整体压缩比
        full_str = ' '.join(str(x) for x in data)
        full_compressed_size = self.kolmogorov.compute(full_str)
        full_size = len(full_str.encode('utf-8'))
        full_ratio = full_compressed_size / max(full_size, 1)
        
        # 逐个移除点，计算压缩比变化
        high_info_points = []
        for i in range(len(data)):
            # 移除第i个点
            subset = data[:i] + data[i+1:]
            subset_str = ' '.join(str(x) for x in subset)
            subset_compressed_size = self.kolmogorov.compute(subset_str)
            subset_size = len(subset_str.encode('utf-8'))
            subset_ratio = subset_compressed_size / max(subset_size, 1)
            
            # 压缩比变化（绝对值）
            ratio_change = abs(subset_ratio - full_ratio)
            
            if ratio_change > 0.01:  # 阈值：压缩比变化超过1%
                high_info_points.append({
                    'index': i,
                    'point': data[i],
                    'ratio_change': ratio_change
                })
                
        # 按压缩比变化排序
        high_info_points.sort(key=lambda x: x['ratio_change'], reverse=True)
        
        # 返回前N个高信息量点
        top_n = min(10, len(high_info_points))
        return [p['point'] for p in high_info_points[:top_n]]
        
    def verify_anti_monotonicity(self, set_A: List[Any], set_B: List[Any]) -> Dict:
        """
        验证反单调性：I(A) > I(B) 尽管 measure(A) < measure(B)
        
        参数:
            set_A: 数据集A（应该是类素数集）
            set_B: 数据集B（应该是连续集）
            
        返回:
            {
                'I_A': float,  # A的信息量
                'I_B': float,  # B的信息量
                'measure_A': float,  # A的测度
                'measure_B': float,  # B的测度
                'anti_monotonicity_holds': bool  # 反单调性是否成立
            }
        """
        # 计算信息量
        info_A = self.compute_information_content(set_A)
        info_B = self.compute_information_content(set_B)
        
        I_A = info_A['info_density']
        I_B = info_B['info_density']
        
        # 计算测度（简化：使用数据量作为测度的代理）
        measure_A = len(set_A) / max(len(set_A) + len(set_B), 1)
        measure_B = len(set_B) / max(len(set_A) + len(set_B), 1)
        
        # 验证反单调性：I_A > I_B 且 measure_A < measure_B
        anti_monotonicity_holds = (I_A > I_B) and (measure_A < measure_B)
        
        return {
            'I_A': I_A,
            'I_B': I_B,
            'measure_A': measure_A,
            'measure_B': measure_B,
            'anti_monotonicity_holds': anti_monotonicity_holds,
            'info_A_details': info_A,
            'info_B_details': info_B
        }


def demo():
    """演示反单调性信息公理应用"""
    print("=" * 60)
    print("反单调性信息公理应用演示")
    print("=" * 60)
    
    # 创建应用实例
    app = AntiMonotonicityInformation()
    
    # 示例1：素数集 vs 自然数集
    print("\n示例1：素数集 vs 自然数集")
    print("-" * 40)
    
    # 生成素数集（前20个素数）
    prime_set = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    # 生成自然数集（前100个自然数）
    natural_set = list(range(1, 101))
    
    # 验证反单调性
    result = app.verify_anti_monotonicity(prime_set, natural_set)
    
    print(f"素数集信息量 I(A): {result['I_A']:.4f}")
    print(f"自然数集信息量 I(B): {result['I_B']:.4f}")
    print(f"素数集测度 measure(A): {result['measure_A']:.4f}")
    print(f"自然数集测度 measure(B): {result['measure_B']:.4f}")
    print(f"反单调性成立: {result['anti_monotonicity_holds']}")
    
    # 示例2：从低信息量数据中提取高信息量特征
    print("\n示例2：从低信息量数据中提取高 information features")
    print("-" * 40)
    
    # 创建一个低信息量数据（大部分是重复值）
    low_info_data = [1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 5, 1, 1, 1]
    
    print(f"低信息量数据: {low_info_data}")
    
    # 提取高信息量特征
    high_info = app.extract_high_info_from_low_info(low_info_data, method='prime_like')
    
    print(f"提取的高信息量特征（类素数结构）:")
    for i, feature in enumerate(high_info[:5]):  # 只显示前5个
        print(f"  {i+1}. {feature}")
    
    # 示例3：计算数据集的信息量
    print("\n示例3：计算数据集的信息量")
    print("-" * 40)
    
    test_data = ["apple", "banana", "apple", "cherry", "banana", "date"]
    
    info_result = app.compute_information_content(test_data)
    
    print(f"数据集: {test_data}")
    print(f"柯尔莫哥洛夫复杂度: {info_result['kolmogorov_complexity']} bytes")
    print(f"归一化复杂度: {info_result['normalized_complexity']:.4f}")
    print(f"是否为类素数结构: {info_result['is_prime_like']}")
    print(f"信息密度: {info_result['info_density']:.4f}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    
    return app


if __name__ == "__main__":
    demo()
