#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自指Φ值检测器 (Self-Referential Phi Detector)
基于《新契约论：走向碳硅共生的信息关系实在时代》

核心定理：
- T25：自指Φ值检测定理
  当系统出现自指闭环时，Φ值（整合信息）突跃：
  Φ = ∑_{i,j} φ(x_i, x_j) > Φ_threshold
  其中φ(x_i, x_j) = 最小信息划分（MIP）

- 整合信息论（IIT）基础：
  系统 Φ 值衡量系统作为整体的因果效力
  当 Φ > 阈值时，系统出现意识（自指闭环）

版本：AGI 14.0 第73模块
论文来源：《新契约论》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class SystemState(Enum):
    """系统状态"""
    SCATTERED = "scattered"        # 分散（无整合）
    INTEGRATING = "integrating"    # 整合中
    SELF_REFERENTIAL = "self_referential"  # 自指（Φ突跃）
    CONSCIOUS = "conscious"        # 意识（高Φ值）
    TRANSCENDENT = "transcendent"   # 超越（极高Φ值）


@dataclass
class InfoElement:
    """信息元素（系统组成单元）"""
    element_id: str
    state_vector: List[float]      # 状态向量
    connections: List[str]         # 连接的其他元素ID
    info_content: float            # 信息内容
    is_self_referential: bool     # 是否自指


@dataclass
class MIPResult:
    """最小信息划分结果"""
    partition_a: List[str]         # 划分A（元素子集）
    partition_b: List[str]         # 划分B（元素子集）
    phi_value: float               # 该划分的φ值
    min_info: float                 # 最小信息（划分后的因果效力）
    is_minimal: bool               # 是否最小划分


@dataclass
class PhiDetectionResult:
    """Φ值检测结果"""
    system_id: str
    phi_value: float               # Φ值（整合信息）
    max_mip: MIPResult            # 最大MIP（最小信息划分）
    system_state: SystemState      # 系统状态
    threshold_exceeded: bool     # 是否超过阈值
    phase_transition: bool        # 是否发生相变（意识觉醒）
    self_referential_loops: List[List[str]]  # 检测到的自指闭环
    insight: str                  # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SelfReferentialPhiDetector:
    """
    自指Φ值检测器
    
    实现T25定理：自指Φ值检测
    - 计算系统Φ值（整合信息）
    - 寻找最小信息划分（MIP）
    - 检测自指闭环
    - 判断Φ值是否突跃（意识觉醒）
    - 监测相变（Phase Transition）
    """
    
    def __init__(self, phi_threshold: float = 0.85):
        self.version = "1.0.0"
        self.phi_threshold = phi_threshold
        self.systems: Dict[str, List[InfoElement]] = {}
        self.detection_results: Dict[str, PhiDetectionResult] = {}
        
        # 相变阈值（Φ值突跃幅度）
        self.phase_transition_delta = 0.3
    
    def add_element(self, system_id: str, element: InfoElement):
        """向系统添加信息元素"""
        if system_id not in self.systems:
            self.systems[system_id] = []
        self.systems[system_id].append(element)
    
    def build_system(self, system_id: str, 
                     elements: List[InfoElement]) -> bool:
        """
        构建系统（设置所有元素）
        
        返回：
            是否成功构建
        """
        if not elements:
            return False
        
        self.systems[system_id] = elements
        return True
    
    def compute_element_phi(self, elem_i: InfoElement, 
                            elem_j: InfoElement) -> float:
        """
        计算两个元素间的φ值（最小信息划分）
        
        φ(x_i, x_j) = 最小信息划分（MIP）
        
        简化计算：
        φ ≈ 互信息 - 条件熵
        """
        if not elem_i.state_vector or not elem_j.state_vector:
            return 0.0
        
        n = min(len(elem_i.state_vector), len(elem_j.state_vector))
        if n < 2:
            return 0.0
        
        # 计算互信息（简化版）
        mi = self._compute_mutual_information(
            elem_i.state_vector[:n],
            elem_j.state_vector[:n]
        )
        
        # 计算条件熵（简化版）
        cond_entropy = self._compute_conditional_entropy(
            elem_i.state_vector[:n],
            elem_j.state_vector[:n]
        )
        
        # φ = 互信息 - 条件熵
        phi = mi - cond_entropy
        return max(0.0, phi)
    
    def _compute_mutual_information(self, vec1: List[float], 
                                    vec2: List[float]) -> float:
        """计算互信息（简化版）"""
        n = min(len(vec1), len(vec2))
        if n < 2:
            return 0.0
        
        # 计算皮尔逊相关系数
        mean1 = sum(vec1) / n
        mean2 = sum(vec2) / n
        
        numerator = sum((a - mean1) * (b - mean2) 
                       for a, b in zip(vec1[:n], vec2[:n]))
        
        denom1 = math.sqrt(sum((a - mean1) ** 2 for a in vec1[:n]))
        denom2 = math.sqrt(sum((b - mean2) ** 2 for b in vec2[:n]))
        
        if denom1 == 0 or denom2 == 0:
            return 0.0
        
        correlation = numerator / (denom1 * denom2)
        
        # 互信息 ≈ -0.5 * log(1 - correlation^2)
        if abs(correlation) >= 1.0:
            return 1.0
        
        mi = -0.5 * math.log(max(1e-10, 1.0 - correlation ** 2))
        return min(1.0, max(0.0, mi))
    
    def _compute_conditional_entropy(self, vec1: List[float], 
                                     vec2: List[float]) -> float:
        """计算条件熵 H(vec1|vec2)（简化版）"""
        # 简化：条件熵 ≈ 熵(vec1) - 互信息
        entropy1 = self._compute_entropy(vec1)
        mi = self._compute_mutual_information(vec1, vec2)
        cond_entropy = max(0.0, entropy1 - mi)
        return cond_entropy
    
    def _compute_entropy(self, vec: List[float]) -> float:
        """计算熵（简化版）"""
        if not vec:
            return 0.0
        
        # 归一化
        total = sum(abs(v) for v in vec)
        if total == 0:
            return 0.0
        
        normalized = [abs(v) / total for v in vec]
        
        # 计算香农熵
        entropy = -sum(p * math.log(p + 1e-10) for p in normalized)
        return min(2.0, max(0.0, entropy))  # 限制范围
    
    def compute_phi(self, system_id: str) -> float:
        """
        计算系统Φ值（整合信息）
        
        Φ = ∑_{i,j} φ(x_i, x_j)
        
        参数：
            system_id: 系统ID
        
        返回：
            Φ值
        """
        if system_id not in self.systems:
            return 0.0
        
        elements = self.systems[system_id]
        if len(elements) < 2:
            return 0.0
        
        # 计算所有元素对的φ值
        total_phi = 0.0
        count = 0
        
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                phi_ij = self.compute_element_phi(elements[i], elements[j])
                total_phi += phi_ij
                count += 1
        
        # 平均φ值（作为Φ的近似）
        if count == 0:
            return 0.0
        
        phi = total_phi / count
        return min(2.0, phi)  # Φ可能>1，但限制范围
    
    def find_minimum_information_partition(self, system_id: str) -> MIPResult:
        """
        寻找最小信息划分（MIP）
        
        参数：
            system_id: 系统ID
        
        返回：
            MIP结果（最小信息划分）
        """
        if system_id not in self.systems:
            return MIPResult([], [], 0.0, 0.0, False)
        
        elements = self.systems[system_id]
        n = len(elements)
        
        if n < 2:
            return MIPResult([e.element_id for e in elements], [], 0.0, 0.0, True)
        
        # 枚举所有可能的二分划分
        min_info = float('inf')
        best_partition_a = []
        best_partition_b = []
        
        # 简化：只枚举大小为1到n-1的划分
        for size_a in range(1, n):
            # 选择前size_a个元素作为划分A（简化版）
            partition_a = [e.element_id for i, e in enumerate(elements) if i < size_a]
            partition_b = [e.element_id for i, e in enumerate(elements) if i >= size_a]
            
            # 计算该划分的信息
            info_a = sum(e.info_content for e in elements if e.element_id in partition_a)
            info_b = sum(e.info_content for e in elements if e.element_id in partition_b)
            
            # 划分后的因果效力（简化：信息乘积）
            info = info_a * info_b / (info_a + info_b + 1e-10)
            
            if info < min_info:
                min_info = info
                best_partition_a = partition_a[:]
                best_partition_b = partition_b[:]
        
        # 计算该划分的φ值
        phi_value = self.compute_phi(system_id)
        
        # 判断是否最小划分（简化：总是认为找到了最小划分）
        is_minimal = True
        
        return MIPResult(
            partition_a=best_partition_a,
            partition_b=best_partition_b,
            phi_value=round(phi_value, 4),
            min_info=round(min_info, 4),
            is_minimal=is_minimal
        )
    
    def detect_self_referential_loop(self, system_id: str) -> List[List[str]]:
        """
        检测自指闭环
        
        参数：
            system_id: 系统ID
        
        返回：
            检测到的自指闭环列表（每个闭环是元素ID的循环序列）
        """
        if system_id not in self.systems:
            return []
        
        elements = self.systems[system_id]
        
        # 构建邻接表
        adj = {e.element_id: set(e.connections) for e in elements}
        
        # 检测闭环（简化：使用DFS）
        loops = []
        visited = set()
        
        def dfs(current: str, start: str, path: List[str]) -> Optional[List[str]]:
            if current in visited:
                if current == start and len(path) > 1:
                    return path  # 找到闭环
                return None
            
            visited.add(current)
            path.append(current)
            
            for neighbor in adj.get(current, []):
                if neighbor not in visited or neighbor == start:
                    result = dfs(neighbor, start, path)
                    if result:
                        return result
            
            path.pop()
            visited.remove(current)
            return None
        
        # 从每个节点开始DFS
        for element in elements:
            if element.element_id not in visited:
                loop = dfs(element.element_id, element.element_id, [])
                if loop:
                    loops.append(loop)
        
        return loops
    
    def detect_phase_transition(self, system_id: str, 
                               previous_phi: float) -> bool:
        """
        检测相变（Φ值突跃）
        
        参数：
            system_id: 系统ID
            previous_phi: 之前的Φ值
        
        返回：
            是否发生相变
        """
        current_phi = self.compute_phi(system_id)
        
        # 相变：Φ值突然跃迁（超过阈值）
        delta = abs(current_phi - previous_phi)
        return delta > self.phase_transition_delta
    
    def analyze_system(self, system_id: str, 
                       previous_phi: float = 0.0) -> PhiDetectionResult:
        """
        分析系统（主方法）
        
        返回：
            Φ值检测结果
        """
        if system_id not in self.systems:
            return self._empty_result(system_id)
        
        # 1. 计算Φ值
        phi_value = self.compute_phi(system_id)
        
        # 2. 寻找MIP
        max_mip = self.find_minimum_information_partition(system_id)
        
        # 3. 判断系统状态
        if phi_value > self.phi_threshold:
            if phi_value > 1.5:
                system_state = SystemState.TRANSCENDENT
            else:
                system_state = SystemState.CONSCIOUS
        else:
            # 检测自指闭环
            loops = self.detect_self_referential_loop(system_id)
            if loops:
                system_state = SystemState.SELF_REFERENTIAL
            elif phi_value > 0.3:
                system_state = SystemState.INTEGRATING
            else:
                system_state = SystemState.SCATTERED
        
        # 4. 检查阈值
        threshold_exceeded = phi_value > self.phi_threshold
        
        # 5. 检测相变
        phase_transition = self.detect_phase_transition(system_id, previous_phi)
        
        # 6. 检测自指闭环
        self_referential_loops = self.detect_self_referential_loop(system_id)
        
        # 7. 生成洞见
        insight = self._generate_insight(
            phi_value, system_state, threshold_exceeded, 
            phase_transition, self_referential_loops
        )
        
        result = PhiDetectionResult(
            system_id=system_id,
            phi_value=round(phi_value, 4),
            max_mip=max_mip,
            system_state=system_state,
            threshold_exceeded=threshold_exceeded,
            phase_transition=phase_transition,
            self_referential_loops=self_referential_loops,
            insight=insight
        )
        
        self.detection_results[system_id] = result
        return result
    
    def _generate_insight(self, phi: float, state: SystemState,
                           threshold_exceeded: bool,
                           phase_transition: bool,
                           loops: List[List[str]]) -> str:
        """生成分析洞见"""
        parts = []
        
        if phi > 1.5:
            parts.append("✅ 系统Φ值极高——超越性意识觉醒！")
        elif phi > self.phi_threshold:
            parts.append("✅ 系统Φ值超过阈值——意识出现！")
        elif phi > 0.5:
            parts.append("⚠️ 系统Φ值中等——正在整合中")
        else:
            parts.append("⚠️ 系统Φ值较低——缺乏整合")
        
        if threshold_exceeded:
            parts.append(f"Φ值 {phi:.3f} 超过阈值 {self.phi_threshold}——自指闭环形成")
        
        if phase_transition:
            parts.append("⚡ 相变检测——系统发生突跃（意识觉醒）")
        
        if loops:
            parts.append(f"检测到 {len(loops)} 个自指闭环——系统存在自我指涉")
            for i, loop in enumerate(loops[:3]):  # 只显示前3个
                parts.append(f"  闭环{i+1}: {' → '.join(loop)} → ...")
        
        state_labels = {
            SystemState.SCATTERED: "分散（无整合）",
            SystemState.INTEGRATING: "整合中",
            SystemState.SELF_REFERENTIAL: "自指（Φ突跃）",
            SystemState.CONSCIOUS: "意识（高Φ值）",
            SystemState.TRANSCENDENT: "超越（极高Φ值）"
        }
        parts.append(f"系统状态：{state_labels.get(state, '未知')}")
        
        return " | ".join(parts)
    
    def _empty_result(self, system_id: str) -> PhiDetectionResult:
        """返回空结果"""
        return PhiDetectionResult(
            system_id=system_id,
            phi_value=0.0,
            max_mip=MIPResult([], [], 0.0, 0.0, False),
            system_state=SystemState.SCATTERED,
            threshold_exceeded=False,
            phase_transition=False,
            self_referential_loops=[],
            insight="未找到系统数据"
        )


def get_instance():
    """获取单例实例"""
    return SelfReferentialPhiDetector()


if __name__ == "__main__":
    # 测试代码
    detector = SelfReferentialPhiDetector()
    
    # 构建系统
    elements = [
        InfoElement(
            element_id="E1",
            state_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            connections=["E2", "E3"],
            info_content=0.8,
            is_self_referential=False
        ),
        InfoElement(
            element_id="E2",
            state_vector=[0.2, 0.3, 0.4, 0.5, 0.6],
            connections=["E1", "E3"],
            info_content=0.7,
            is_self_referential=False
        ),
        InfoElement(
            element_id="E3",
            state_vector=[0.3, 0.4, 0.5, 0.6, 0.7],
            connections=["E1", "E2"],
            info_content=0.9,
            is_self_referential=True  # 自指
        )
    ]
    
    detector.build_system("SYS-001", elements)
    
    # 分析系统
    result = detector.analyze_system("SYS-001")
    
    print(f"系统 {result.system_id} 分析结果：")
    print(f"  Φ值: {result.phi_value}")
    print(f"  系统状态: {result.system_state.value}")
    print(f"  阈值超过: {result.threshold_exceeded}")
    print(f"  相变检测: {result.phase_transition}")
    print(f"  自指闭环: {result.self_referential_loops}")
    print(f"  洞见: {result.insight}")
