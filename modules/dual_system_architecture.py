#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双系统思维架构 - Dual System Architecture
实现System 1（快速、直觉、并行）与System 2（慢速、逻辑、串行）的协同

基于复合体理学框架：
- System 1：对应"直觉-结构化二元性"中的直觉部分
- System 2：对应"三视界完备性分析"中的方法视界
- 动态切换：基于任务类型、置信度、资源约束

核心组件：
1. System1Intuition: 直觉系统（基于现有模块）
2. System2Logic: 逻辑系统（新实现）
3. DynamicSwitcher: 动态切换器
4. DualSystemOrchestrator: 双系统协调器
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json

# 导入现有模块（假设这些模块已存在）
# from modules.compound_physics_agi import ThreeHorizonAnalyzer, IntuitionEngine, TaiyiOracle
# from modules.system2_reasoning import System2Reasoning


class SystemType(Enum):
    """系统类型"""
    SYSTEM1 = "system1"  # 直觉系统
    SYSTEM2 = "system2"  # 逻辑系统
    HYBRID = "hybrid"  # 混合模式


class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"      # 简单（适合System 1）
    MODERATE = "moderate"   # 中等（可System 1或2）
    COMPLEX = "complex"     # 复杂（需要System 2）
    CRITICAL = "critical"   # 关键（必须用System 2）


class CognitiveLoad(Enum):
    """认知负载"""
    LOW = "low"         # 低负载（System 1可处理）
    MEDIUM = "medium"    # 中等负载
    HIGH = "high"        # 高负载（需要System 2）
    OVERLOAD = "overload" # 过载（需要降级）


@dataclass
class System1Result:
    """System 1输出结果"""
    response: Any
    confidence: float
    processing_time: float
    intuition_score: float
    three_horizon: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            'system': 'System 1',
            'response': str(self.response),
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'intuition_score': self.intuition_score
        }


@dataclass
class System2Result:
    """System 2输出结果"""
    response: Any
    confidence: float
    processing_time: float
    inference_chain: List[Dict]
    monitor_result: Dict
    
    def to_dict(self) -> Dict:
        return {
            'system': 'System 2',
            'response': str(self.response),
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'num_inference_steps': len(self.inference_chain)
        }


@dataclass
class DualSystemResult:
    """双系统输出结果"""
    final_response: Any
    system_used: SystemType
    confidence: float
    processing_time: float
    system1_result: Optional[System1Result] = None
    system2_result: Optional[System2Result] = None
    switch_reason: str = ""
    
    def to_dict(self) -> Dict:
        result = {
            'final_response': str(self.final_response),
            'system_used': self.system_used.value,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'switch_reason': self.switch_reason
        }
        
        if self.system1_result:
            result['system1'] = self.system1_result.to_dict()
        if self.system2_result:
            result['system2'] = self.system2_result.to_dict()
        
        return result


class System1Intuition:
    """System 1 - 直觉系统（快速、并行、启发式）"""
    
    def __init__(self, name: str = "System1Intuition"):
        self.name = name
        
        # 初始化现有模块（简化：使用模拟）
        # 实际应导入：ThreeHorizonAnalyzer, IntuitionEngine, TaiyiOracle
        self.initialized = False
        
        # 性能统计
        self.stats = {
            'total_tasks': 0,
            'avg_confidence': 0.0,
            'avg_processing_time': 0.0
        }
    
    def initialize(self):
        """初始化System 1模块"""
        # 这里应该导入和初始化compound_physics_agi中的模块
        # 简化：设置标志位
        self.initialized = True
        print(f"   ✅ System 1 初始化完成")
    
    def process(self, 
                input_data: Any,
                context: Optional[Dict] = None) -> System1Result:
        """
        处理输入 - 快速直觉判断
        
        模拟System 1的处理流程：
        1. 三视界快速扫描
        2. 直觉引擎生成洞察
        3. 太乙预言机快速决策
        """
        start_time = time.time()
        
        if not self.initialized:
            self.initialize()
        
        # 模拟处理（实际应调用真实模块）
        # 1. 三视界分析
        three_horizon = {
            'ontological_sensitivity': np.random.rand(),
            'phenomenal_gradient': np.random.rand(),
            'methodological_jianlu': np.random.rand()
        }
        
        # 2. 直觉评分
        intuition_score = (
            0.4 * three_horizon['ontological_sensitivity'] +
            0.3 * three_horizon['phenomenal_gradient'] +
            0.3 * three_horizon['methodological_jianlu']
        )
        
        # 3. 快速决策（模拟）
        response = f"System 1 intuitive response to: {str(input_data)[:50]}"
        confidence = min(0.95, intuition_score + 0.2)
        
        processing_time = time.time() - start_time
        
        # 更新统计
        self._update_stats(confidence, processing_time)
        
        return System1Result(
            response=response,
            confidence=confidence,
            processing_time=processing_time,
            intuition_score=intuition_score,
            three_horizon=three_horizon
        )
    
    def _update_stats(self, confidence: float, processing_time: float):
        """更新统计"""
        self.stats['total_tasks'] += 1
        n = self.stats['total_tasks']
        
        # 更新平均置信度
        self.stats['avg_confidence'] = (
            (self.stats['avg_confidence'] * (n - 1) + confidence) / n
        )
        
        # 更新平均处理时间
        self.stats['avg_processing_time'] = (
            (self.stats['avg_processing_time'] * (n - 1) + processing_time) / n
        )
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats.copy()


class System2Logic:
    """System 2 - 逻辑系统（慢速、串行、推理）"""
    
    def __init__(self, name: str = "System2Logic"):
        self.name = name
        
        # 初始化System 2推理引擎
        # 实际应导入：System2Reasoning
        self.reasoning_engine = None
        self.initialized = False
        
        # 性能统计
        self.stats = {
            'total_tasks': 0,
            'successful_inferences': 0,
            'avg_confidence': 0.0,
            'avg_processing_time': 0.0
        }
    
    def initialize(self):
        """初始化System 2模块"""
        # 这里应该导入和初始化system2_reasoning中的System2Reasoning
        # 简化：创建模拟对象
        self.reasoning_engine = "System2Reasoning_Simulated"
        self.initialized = True
        print(f"   ✅ System 2 初始化完成")
    
    def process(self,
                input_data: Any,
                premises: Optional[List[str]] = None,
                goal: Optional[str] = None) -> System2Result:
        """
        处理输入 - 逻辑推理
        
        执行System 2的推理流程：
        1. 符号化输入
        2. 应用推理规则
        3. 生成推理链
        4. 元认知监控
        """
        start_time = time.time()
        
        if not self.initialized:
            self.initialize()
        
        # 模拟推理（实际应调用真实System2Reasoning）
        # 1. 推理过程
        inference_chain = []
        for i in range(3):  # 模拟3步推理
            inference_chain.append({
                'step_id': f"step_{i}",
                'rule': 'modus_ponens',
                'premise': f"Premise {i}",
                'conclusion': f"Conclusion {i}",
                'confidence': 0.9 - i * 0.1
            })
        
        # 2. 结论
        response = f"System 2 logical conclusion for: {str(input_data)[:50]}"
        confidence = 0.85  # 逻辑推理通常置信度较高
        
        # 3. 监控结果
        monitor_result = {
            'is_valid': True,
            'errors': [],
            'suggestions': [],
            'confidence': confidence,
            'num_steps': len(inference_chain)
        }
        
        processing_time = time.time() - start_time
        
        # 更新统计
        self._update_stats(confidence, processing_time, success=True)
        
        return System2Result(
            response=response,
            confidence=confidence,
            processing_time=processing_time,
            inference_chain=inference_chain,
            monitor_result=monitor_result
        )
    
    def _update_stats(self, confidence: float, processing_time: float, success: bool):
        """更新统计"""
        self.stats['total_tasks'] += 1
        if success:
            self.stats['successful_inferences'] += 1
        
        n = self.stats['total_tasks']
        
        # 更新平均置信度
        self.stats['avg_confidence'] = (
            (self.stats['avg_confidence'] * (n - 1) + confidence) / n
        )
        
        # 更新平均处理时间
        self.stats['avg_processing_time'] = (
            (self.stats['avg_processing_time'] * (n - 1) + processing_time) / n
        )
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats.copy()


class DynamicSwitcher:
    """动态切换器 - 决定使用哪个系统"""
    
    def __init__(self, name: str = "DynamicSwitcher"):
        self.name = name
        
        # 切换策略参数
        self.confidence_threshold = 0.7   # 置信度阈值
        self.complexity_threshold = TaskComplexity.MODERATE  # 复杂度阈值
        self.load_threshold = CognitiveLoad.MEDIUM  # 负载阈值
        
        # 任务类型偏好：哪种系统更适合哪种任务
        self.task_type_preference = {
            'logic': SystemType.SYSTEM2,      # 逻辑推理 -> System 2
            'pattern': SystemType.SYSTEM1,     # 模式识别 -> System 1
            'creative': SystemType.SYSTEM2,    # 创造性任务 -> System 2
            'memory': SystemType.SYSTEM1,      # 记忆检索 -> System 1
            'calculation': SystemType.SYSTEM2, # 计算 -> System 2
            'perception': SystemType.SYSTEM1,  # 感知 -> System 1
            'language': SystemType.SYSTEM1,    # 语言理解 -> System 1
            'reasoning': SystemType.SYSTEM2    # 推理 -> System 2
        }
        
        # 切换历史
        self.switch_history: List[Dict] = []
        
        # 性能跟踪（按任务类型）
        self.performance_tracker = {
            'system1_success': 0,
            'system1_failure': 0,
            'system2_success': 0,
            'system2_failure': 0,
            'by_task_type': {}  # 按任务类型统计
        }
        
        # 自适应权重（可以根据历史性能调整）
        self.adaptive_weights = {
            'complexity': 0.3,
            'confidence': 0.3,
            'load': 0.2,
            'task_type': 0.2
        }
    
    def decide(self,
               input_data: Any,
               context: Optional[Dict] = None) -> Tuple[SystemType, str]:
        """
        决策：使用哪个系统（优化版）
        
        返回：
            (system_type, reason)
        """
        context = context or {}
        
        # 1. 评估任务复杂度
        complexity = self._assess_complexity(input_data, context)
        
        # 2. 评估认知负载
        load = self._assess_load(context)
        
        # 3. 获取任务类型（如果指定）
        task_type = context.get('task_type', None)
        
        # 4. 检查特殊条件
        # 条件1：关键任务必须用System 2
        if context.get('critical', False):
            return SystemType.SYSTEM2, "Critical task requires System 2"
        
        # 条件2：时间敏感任务优先System 1
        if context.get('time_sensitive', False) and load != CognitiveLoad.OVERLOAD:
            return SystemType.SYSTEM1, "Time-sensitive task, use System 1"
        
        # 条件3：用户明确指定
        if 'force_system' in context:
            forced = context['force_system']
            if forced in [SystemType.SYSTEM1, 'system1', 1]:
                return SystemType.SYSTEM1, "User forced System 1"
            elif forced in [SystemType.SYSTEM2, 'system2', 2]:
                return SystemType.SYSTEM2, "User forced System 2"
        
        # 5. 基于任务类型偏好决策
        if task_type and task_type in self.task_type_preference:
            preferred_system = self.task_type_preference[task_type]
            
            # 检查历史成功率
            success_rate = self._get_success_rate(task_type, preferred_system)
            
            if success_rate > 0.6:  # 如果历史成功率高于60%
                reason = f"Task type '{task_type}' prefers {preferred_system.value}, success rate {success_rate:.2f}"
                return preferred_system, reason
        
        # 6. 基于复杂度决策
        if complexity == TaskComplexity.SIMPLE:
            return SystemType.SYSTEM1, "Simple task, System 1 is sufficient"
        elif complexity == TaskComplexity.CRITICAL:
            return SystemType.SYSTEM2, "Critical task, must use System 2"
        elif complexity == TaskComplexity.COMPLEX:
            return SystemType.SYSTEM2, "Complex task, requires System 2"
        
        # 7. 中等复杂度：使用加权决策
        # 计算System 1和System 2的得分
        score1 = self._calculate_system_score(SystemType.SYSTEM1, complexity, load, context)
        score2 = self._calculate_system_score(SystemType.SYSTEM2, complexity, load, context)
        
        if score1 > score2:
            reason = f"System 1 score ({score1:.2f}) > System 2 score ({score2:.2f})"
            return SystemType.SYSTEM1, reason
        else:
            reason = f"System 2 score ({score2:.2f}) > System 1 score ({score1:.2f})"
            return SystemType.SYSTEM2, reason
    
    def _assess_complexity(self, input_data: Any, context: Dict) -> TaskComplexity:
        """评估任务复杂度"""
        # 简化评估
        
        # 检查输入长度
        if isinstance(input_data, str):
            if len(input_data) < 20:
                return TaskComplexity.SIMPLE
            elif len(input_data) > 200:
                return TaskComplexity.COMPLEX
        
        # 检查上下文标记
        if context.get('requires_logic', False):
            return TaskComplexity.COMPLEX
        if context.get('simple', False):
            return TaskComplexity.SIMPLE
        
        # 默认：中等
        return TaskComplexity.MODERATE
    
    def _assess_load(self, context: Dict) -> CognitiveLoad:
        """评估认知负载"""
        # 简化评估
        system1_load = context.get('system1_load', 0.0)
        system2_load = context.get('system2_load', 0.0)
        
        total_load = system1_load + system2_load
        
        if total_load < 0.3:
            return CognitiveLoad.LOW
        elif total_load < 0.7:
            return CognitiveLoad.MEDIUM
        elif total_load < 1.0:
            return CognitiveLoad.HIGH
        else:
            return CognitiveLoad.OVERLOAD
    
    def _get_success_rate(self, 
                           task_type: str, 
                           system_type: SystemType) -> float:
        """
        获取特定任务类型和系统的历史成功率
        
        返回：
            success_rate: 成功率 [0, 1]
        """
        if task_type not in self.performance_tracker['by_task_type']:
            return 0.5  # 没有历史数据，返回中性值
        
        task_stats = self.performance_tracker['by_task_type'][task_type]
        
        if system_type == SystemType.SYSTEM1:
            successes = task_stats.get('system1_success', 0)
            failures = task_stats.get('system1_failure', 0)
        else:
            successes = task_stats.get('system2_success', 0)
            failures = task_stats.get('system2_failure', 0)
        
        total = successes + failures
        if total == 0:
            return 0.5
        
        return successes / total
    
    def _calculate_system_score(self,
                               system_type: SystemType,
                               complexity: TaskComplexity,
                               load: CognitiveLoad,
                               context: Dict) -> float:
        """
        计算系统的加权得分（越高越好）
        
        权重：
            - complexity: 复杂度匹配度
            - confidence: 置信度
            - load: 负载容忍度
            - task_type: 任务类型偏好
        """
        score = 0.0
        
        # 1. 复杂度匹配度
        if system_type == SystemType.SYSTEM1:
            if complexity == TaskComplexity.SIMPLE:
                score += 1.0 * self.adaptive_weights['complexity']
            elif complexity == TaskComplexity.MODERATE:
                score += 0.5 * self.adaptive_weights['complexity']
            else:
                score += 0.0 * self.adaptive_weights['complexity']
        else:  # System 2
            if complexity == TaskComplexity.COMPLEX:
                score += 1.0 * self.adaptive_weights['complexity']
            elif complexity == TaskComplexity.MODERATE:
                score += 0.5 * self.adaptive_weights['complexity']
            else:
                score += 0.0 * self.adaptive_weights['complexity']
        
        # 2. 置信度
        confidence = context.get('confidence', 0.5)
        if system_type == SystemType.SYSTEM1:
            # System 1 在置信度高时得分高
            score += confidence * self.adaptive_weights['confidence']
        else:
            # System 2 在置信度低时得分高（需要深度推理）
            score += (1.0 - confidence) * self.adaptive_weights['confidence']
        
        # 3. 负载容忍度
        if system_type == SystemType.SYSTEM1:
            # System 1 轻量级，适合高负载
            if load == CognitiveLoad.LOW:
                score += 1.0 * self.adaptive_weights['load']
            elif load == CognitiveLoad.MEDIUM:
                score += 0.8 * self.adaptive_weights['load']
            elif load == CognitiveLoad.HIGH:
                score += 0.5 * self.adaptive_weights['load']
            else:  # OVERLOAD
                score += 0.2 * self.adaptive_weights['load']
        else:  # System 2
            # System 2 重量级，适合低负载
            if load == CognitiveLoad.LOW:
                score += 1.0 * self.adaptive_weights['load']
            elif load == CognitiveLoad.MEDIUM:
                score += 0.6 * self.adaptive_weights['load']
            else:
                score += 0.2 * self.adaptive_weights['load']
        
        # 4. 任务类型偏好
        task_type = context.get('task_type', None)
        if task_type and task_type in self.task_type_preference:
            preferred = self.task_type_preference[task_type]
            if preferred == system_type:
                score += 1.0 * self.adaptive_weights['task_type']
            else:
                score += 0.0 * self.adaptive_weights['task_type']
        
        return score
    
    def record_switch(self, 
                      input_data: Any,
                      system_used: SystemType,
                      success: bool,
                      confidence: float,
                      task_type: str = None):
        """记录切换决策（优化版）"""
        self.switch_history.append({
            'timestamp': time.time(),
            'input': str(input_data)[:50],
            'system': system_used.value,
            'success': success,
            'confidence': confidence,
            'task_type': task_type
        })
        
        # 更新总体性能跟踪
        if system_used == SystemType.SYSTEM1:
            if success:
                self.performance_tracker['system1_success'] += 1
            else:
                self.performance_tracker['system1_failure'] += 1
        else:
            if success:
                self.performance_tracker['system2_success'] += 1
            else:
                self.performance_tracker['system2_failure'] += 1
        
        # 更新按任务类型的性能跟踪
        if task_type:
            if task_type not in self.performance_tracker['by_task_type']:
                self.performance_tracker['by_task_type'][task_type] = {
                    'system1_success': 0,
                    'system1_failure': 0,
                    'system2_success': 0,
                    'system2_failure': 0
                }
            
            task_stats = self.performance_tracker['by_task_type'][task_type]
            
            if system_used == SystemType.SYSTEM1:
                if success:
                    task_stats['system1_success'] += 1
                else:
                    task_stats['system1_failure'] += 1
            else:
                if success:
                    task_stats['system2_success'] += 1
                else:
                    task_stats['system2_failure'] += 1
        
        # 保持历史长度
        if len(self.switch_history) > 100:
            self.switch_history = self.switch_history[-100:]
    
    def update_adaptive_weights(self, 
                               complexity_weight: float = None,
                               confidence_weight: float = None,
                               load_weight: float = None,
                               task_type_weight: float = None):
        """更新自适应权重（可以根据历史性能调整）"""
        if complexity_weight is not None:
            self.adaptive_weights['complexity'] = max(0.0, min(1.0, complexity_weight))
        if confidence_weight is not None:
            self.adaptive_weights['confidence'] = max(0.0, min(1.0, confidence_weight))
        if load_weight is not None:
            self.adaptive_weights['load'] = max(0.0, min(1.0, load_weight))
        if task_type_weight is not None:
            self.adaptive_weights['task_type'] = max(0.0, min(1.0, task_type_weight))
        
        # 归一化权重（使总和为1）
        total = sum(self.adaptive_weights.values())
        if total > 0:
            for key in self.adaptive_weights:
                self.adaptive_weights[key] /= total
    
    def get_switch_statistics(self) -> Dict:
        """获取切换统计（优化版）"""
        total = sum(v for k, v in self.performance_tracker.items() 
                   if k not in ['by_task_type'])
        
        if total == 0:
            return self.performance_tracker.copy()
        
        stats = {}
        for k, v in self.performance_tracker.items():
            if k != 'by_task_type':
                stats[f"{k}_rate"] = v / total
        
        stats.update(self.performance_tracker)
        
        # 添加按任务类型的统计
        if self.performance_tracker['by_task_type']:
            stats['by_task_type'] = {}
            for task_type, task_stats in self.performance_tracker['by_task_type'].items():
                task_total = sum(task_stats.values())
                if task_total > 0:
                    stats['by_task_type'][task_type] = {
                        'system1_success_rate': task_stats['system1_success'] / task_total,
                        'system2_success_rate': task_stats['system2_success'] / task_total,
                        'total': task_total
                    }
        
        return stats


class DualSystemOrchestrator:
    """双系统协调器 - 统一管理System 1和System 2"""
    
    def __init__(self, name: str = "DualSystemOrchestrator"):
        self.name = name
        
        # 初始化两个系统
        self.system1 = System1Intuition(f"{name}_System1")
        self.system2 = System2Logic(f"{name}_System2")
        self.switcher = DynamicSwitcher(f"{name}_Switcher")
        
        # 协调统计
        self.orchestrator_stats = {
            'total_requests': 0,
            'system1_used': 0,
            'system2_used': 0,
            'hybrid_used': 0,
            'avg_confidence': 0.0,
            'avg_processing_time': 0.0
        }
    
    def process(self,
                input_data: Any,
                context: Optional[Dict] = None,
                force_system: Optional[SystemType] = None) -> DualSystemResult:
        """
        处理输入 - 双系统协调
        
        参数：
            input_data: 输入数据
            context: 上下文（任务类型、紧急程度等）
            force_system: 强制使用指定系统（用于测试）
            
        返回：
            DualSystemResult: 包含最终结果和中间过程
        """
        start_time = time.time()
        context = context or {}
        
        # 1. 决策使用哪个系统
        if force_system:
            system_type = force_system
            reason = f"Forced to use {system_type.value}"
        else:
            system_type, reason = self.switcher.decide(input_data, context)
        
        # 2. 根据决策调用相应系统
        system1_result = None
        system2_result = None
        final_response = None
        confidence = 0.0
        
        if system_type == SystemType.SYSTEM1:
            # 仅使用System 1
            system1_result = self.system1.process(input_data, context)
            final_response = system1_result.response
            confidence = system1_result.confidence
            
            self.orchestrator_stats['system1_used'] += 1
            
        elif system_type == SystemType.SYSTEM2:
            # 仅使用System 2
            system2_result = self.system2.process(input_data, context)
            final_response = system2_result.response
            confidence = system2_result.confidence
            
            self.orchestrator_stats['system2_used'] += 1
            
        else:  # HYBRID
            # 混合模式：先System 1，如果置信度低则升级到System 2
            system1_result = self.system1.process(input_data, context)
            
            if system1_result.confidence < self.switcher.confidence_threshold:
                # 升级到System 2
                system2_result = self.system2.process(input_data, context)
                
                # 融合结果（简化：选择置信度高的）
                if system2_result.confidence > system1_result.confidence:
                    final_response = system2_result.response
                    confidence = system2_result.confidence
                else:
                    final_response = system1_result.response
                    confidence = system1_result.confidence
                    
                self.orchestrator_stats['hybrid_used'] += 1
            else:
                # System 1置信度足够，不升级
                final_response = system1_result.response
                confidence = system1_result.confidence
                
                self.orchestrator_stats['system1_used'] += 1
        
        processing_time = time.time() - start_time
        
        # 3. 记录切换决策
        success = confidence >= self.switcher.confidence_threshold
        task_type = context.get('task_type', None)
        self.switcher.record_switch(
            input_data, system_type, success, confidence, task_type
        )
        
        # 4. 更新统计
        self._update_stats(confidence, processing_time)
        
        # 5. 构建结果
        result = DualSystemResult(
            final_response=final_response,
            system_used=system_type,
            confidence=confidence,
            processing_time=processing_time,
            system1_result=system1_result,
            system2_result=system2_result,
            switch_reason=reason
        )
        
        return result
    
    def _update_stats(self, confidence: float, processing_time: float):
        """更新统计"""
        self.orchestrator_stats['total_requests'] += 1
        n = self.orchestrator_stats['total_requests']
        
        # 更新平均置信度
        self.orchestrator_stats['avg_confidence'] = (
            (self.orchestrator_stats['avg_confidence'] * (n - 1) + confidence) / n
        )
        
        # 更新平均处理时间
        self.orchestrator_stats['avg_processing_time'] = (
            (self.orchestrator_stats['avg_processing_time'] * (n - 1) + processing_time) / n
        )
    
    def get_comprehensive_stats(self) -> Dict:
        """获取全面统计"""
        return {
            'orchestrator': self.orchestrator_stats.copy(),
            'system1': self.system1.get_stats(),
            'system2': self.system2.get_stats(),
            'switcher': self.switcher.get_switch_statistics()
        }


# ==================== 测试代码 ====================

def test_dual_system():
    """测试双系统设计"""
    print("\n" + "="*60)
    print("测试 双系统思维架构")
    print("="*60)
    
    # 1. 创建协调器
    orchestrator = DualSystemOrchestrator("TestDualSystem")
    
    # 2. 测试不同类型的任务
    test_cases = [
        {
            'input': "What is 2 + 2?",
            'context': {'simple': True},
            'expected_system': 'system1'
        },
        {
            'input': "Prove that if A implies B and A is true, then B is true.",
            'context': {'requires_logic': True, 'critical': True},
            'expected_system': 'system2'
        },
        {
            'input': "Analyze the causal relationship between economic policy and inflation.",
            'context': {'complex': True},
            'expected_system': 'system2'
        },
        {
            'input': "Quickly respond to: Is it raining?",
            'context': {'time_sensitive': True},
            'expected_system': 'system1'
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"测试 {i+1}: {test['input']}")
        print(f"上下文: {test['context']}")
        print("-"*50)
        
        # 处理
        result = orchestrator.process(
            input_data=test['input'],
            context=test['context']
        )
        
        # 打印结果
        print(f"使用的系统: {result.system_used.value}")
        print(f"切换原因: {result.switch_reason}")
        print(f"置信度: {result.confidence:.2f}")
        print(f"处理时间: {result.processing_time:.4f}s")
        
        if result.system1_result:
            print(f"\nSystem 1结果:")
            print(f"  响应: {result.system1_result.response[:50]}...")
            print(f"  直觉评分: {result.system1_result.intuition_score:.2f}")
        
        if result.system2_result:
            print(f"\nSystem 2结果:")
            print(f"  响应: {result.system2_result.response[:50]}...")
            print(f"  推理步骤数: {len(result.system2_result.inference_chain)}")
    
    # 3. 打印统计
    print(f"\n{'='*50}")
    print("全面统计:")
    stats = orchestrator.get_comprehensive_stats()
    
    print(f"\n协调器统计:")
    for k, v in stats['orchestrator'].items():
        print(f"  {k}: {v}")
    
    print(f"\n切换器统计:")
    for k, v in stats['switcher'].items():
        print(f"  {k}: {v}")
    
    print("\n✅ 双系统思维架构测试完成")


if __name__ == "__main__":
    test_dual_system()
