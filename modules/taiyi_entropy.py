#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一太乙系统 - 低熵适应机制
实现：概念漂移检测、描述长度监控、自适应更新策略

基于复合体理学"一现象，三视界"框架：
- 微视界：Jitter、不可压缩涨落
- 中视界：描述长度压缩、Ftel驱动的学习/更新
- 宏视界：低熵存续、共识拓扑
"""

import os
import sys
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import deque
import statistics


# ==================== 定义 ====================

class DriftType(Enum):
    """漂移类型"""
    SUDDEN = "sudden"       # 突然漂移
    GRADUAL = "gradual"     # 渐进漂移
    RECURRING = "recurring" # 循环漂移
    INCREASE = "increase"  # 概念增加
    UNKNOWN = "unknown"     # 未知


@dataclass
class EntropyState:
    """熵状态"""
    timestamp: str
    entropy: float              # 当前熵值
    delta_entropy: float        # 熵变化
    drift_detected: bool       # 是否检测到漂移
    drift_type: DriftType      # 漂移类型
    confidence: float          # 置信度


@dataclass
class AdaptationAction:
    """适应动作"""
    action_type: str           # 动作类型
    reason: str                # 原因
    before_state: Dict          # 之前状态
    after_state: Dict          # 之后状态
    effectiveness: float      # 有效性评分


# ==================== 低熵适应机制 ====================

class LowEntropyAdapter:
    """
    低熵适应机制
    
    功能：
    1. 概念漂移检测
    2. 描述长度监控
    3. 自适应更新策略
    """

    def __init__(self):
        # 熵跟踪
        self._entropy_history = deque(maxlen=100)
        self._response_time_history = deque(maxlen=100)
        self._error_history = deque(maxlen=100)
        
        # 漂移检测参数
        self._drift_threshold = 0.3  # 熵变化阈值
        self._window_size = 10        # 滑动窗口大小
        self._baseline_entropy = 0.5  # 基线熵值
        
        # 适应策略
        self._adaptation_strategies = {
            "memory_decay": 0.95,      # 记忆衰减率
            "learning_rate": 0.1,     # 学习率
            "consolidation_threshold": 0.7,  # 记忆巩固阈值
            "forgetting_threshold": 0.2       # 遗忘阈值
        }
        
        # 适应历史
        self._adaptation_history = []
        
        # 线程安全
        self._lock = threading.Lock()

    def update(self, 
               response_length: int,
               reasoning_steps: int,
               tool_calls: int,
               error_count: int = 0) -> EntropyState:
        """
        更新熵状态
        
        基于响应特征计算当前熵值
        """
        with self._lock:
            # 计算当前熵值
            # 熵 = f(响应长度方差, 推理步数方差, 错误率, 工具使用)
            response_time = time.time()  # 简化：使用时间戳作为代理
            
            # 熵值计算（简化版）
            entropy = self._calculate_entropy(
                response_length=response_length,
                reasoning_steps=reasoning_steps,
                tool_calls=tool_calls,
                error_count=error_count
            )
            
            # 计算熵变化
            delta_entropy = 0.0
            if self._entropy_history:
                baseline = sum(self._entropy_history) / len(self._entropy_history)
                delta_entropy = entropy - baseline
            
            # 漂移检测
            drift_detected, drift_type = self._detect_drift()
            
            # 更新历史
            self._entropy_history.append(entropy)
            self._response_time_history.append(response_length)
            self._error_history.append(error_count)
            
            return EntropyState(
                timestamp=datetime.now().isoformat(),
                entropy=entropy,
                delta_entropy=delta_entropy,
                drift_detected=drift_detected,
                drift_type=drift_type,
                confidence=0.8  # 默认置信度
            )

    def _calculate_entropy(self,
                           response_length: int,
                           reasoning_steps: int,
                           tool_calls: int,
                           error_count: int) -> float:
        """计算熵值"""
        # 标准化各因素
        length_factor = min(response_length / 1000, 1.0) * 0.3
        reasoning_factor = min(reasoning_steps / 20, 1.0) * 0.3
        tool_factor = min(tool_calls / 5, 1.0) * 0.2
        error_factor = min(error_count / 3, 1.0) * 0.2
        
        # 熵值 = 各因素加权和
        entropy = (length_factor + reasoning_factor + tool_factor + error_factor)
        
        # 基线调整
        entropy = 0.5 + (entropy - 0.5) * 0.5
        
        return max(0.0, min(1.0, entropy))

    def _detect_drift(self) -> Tuple[bool, DriftType]:
        """检测概念漂移"""
        if len(self._entropy_history) < self._window_size:
            return False, DriftType.UNKNOWN
        
        # 计算滑动窗口平均
        window = list(self._entropy_history)[-self._window_size:]
        window_mean = sum(window) / len(window)
        window_std = statistics.stdev(window) if len(window) > 1 else 0
        
        # 检测突然漂移（均值突变）
        if len(self._entropy_history) >= 2:
            recent = self._entropy_history[-1]
            previous = self._entropy_history[-2]
            sudden_change = abs(recent - previous)
            if sudden_change > self._drift_threshold:
                return True, DriftType.SUDDEN
        
        # 检测渐进漂移（标准差增大）
        if window_std > 0.2:
            return True, DriftType.GRADUAL
        
        # 检测循环漂移（波动模式）
        if len(window) >= 4:
            if all(abs(window[i] - window[i+1]) < 0.1 for i in range(len(window)-1)):
                return True, DriftType.RECURRING
        
        return False, DriftType.UNKNOWN

    def adapt(self, drift_state: EntropyState) -> AdaptationAction:
        """
        执行适应动作
        
        根据漂移状态选择合适的适应策略
        """
        with self._lock:
            before_state = {
                "memory_decay": self._adaptation_strategies["memory_decay"],
                "learning_rate": self._adaptation_strategies["learning_rate"],
                "entropy": drift_state.entropy
            }
            
            action_type = "no_change"
            reason = "熵值稳定"
            
            # 根据漂移类型选择策略
            if drift_state.drift_detected:
                if drift_state.drift_type == DriftType.SUDDEN:
                    # 突然漂移：快速适应
                    self._adaptation_strategies["learning_rate"] *= 1.5
                    self._adaptation_strategies["memory_decay"] *= 0.9
                    action_type = "fast_adaptation"
                    reason = "检测到突然漂移，加速学习"
                    
                elif drift_state.drift_type == DriftType.GRADUAL:
                    # 渐进漂移：温和调整
                    self._adaptation_strategies["learning_rate"] *= 1.1
                    action_type = "gradual_adaptation"
                    reason = "检测到渐进漂移，温和调整"
                    
                elif drift_state.drift_type == DriftType.RECURRING:
                    # 循环漂移：保持稳定
                    self._adaptation_strategies["memory_decay"] *= 1.05
                    action_type = "stabilize"
                    reason = "检测到循环漂移，保持稳定"
            
            # 限制参数范围
            self._adaptation_strategies["learning_rate"] = max(0.01, min(1.0, 
                self._adaptation_strategies["learning_rate"]))
            self._adaptation_strategies["memory_decay"] = max(0.8, min(1.0,
                self._adaptation_strategies["memory_decay"]))
            
            after_state = {
                "memory_decay": self._adaptation_strategies["memory_decay"],
                "learning_rate": self._adaptation_strategies["learning_rate"],
                "entropy": drift_state.entropy
            }
            
            action = AdaptationAction(
                action_type=action_type,
                reason=reason,
                before_state=before_state,
                after_state=after_state,
                effectiveness=0.8  # 默认有效性
            )
            
            self._adaptation_history.append(action)
            
            return action

    def get_description_length(self, data: Any) -> float:
        """
        计算描述长度
        
        基于MDL原理计算数据的描述长度
        """
        data_str = str(data)
        
        # 简化：使用字符串长度作为描述长度的代理
        # 实际应该使用更复杂的压缩算法
        base_length = len(data_str)
        
        # 考虑重复性（重复越少，描述长度越长）
        unique_ratio = len(set(data_str)) / max(len(data_str), 1)
        description_length = base_length / (unique_ratio + 0.1)
        
        return description_length

    def consolidate_memory(self, importance: float) -> bool:
        """
        记忆巩固
        
        判断是否应该将当前信息巩固到长期记忆
        """
        with self._lock:
            threshold = self._adaptation_strategies["consolidation_threshold"]
            return importance >= threshold

    def should_forget(self, last_access_time: float, access_count: int) -> bool:
        """
        遗忘判断
        
        判断是否应该遗忘某个记忆
        """
        with self._lock:
            # 基于访问时间和次数的遗忘判断
            time_since_access = time.time() - last_access_time
            access_decay = access_count / max(1, time_since_access + 1)
            
            threshold = self._adaptation_strategies["forgetting_threshold"]
            return access_decay < threshold

    def get_state(self) -> Dict:
        """获取当前状态"""
        with self._lock:
            avg_entropy = sum(self._entropy_history) / len(self._entropy_history) if self._entropy_history else 0.5
            
            # 检测当前漂移状态
            drift_detected, drift_type = self._detect_drift()
            
            return {
                "entropy": {
                    "current": self._entropy_history[-1] if self._entropy_history else 0.5,
                    "average": avg_entropy,
                    "delta": self._entropy_history[-1] - avg_entropy if self._entropy_history else 0.0,
                    "history_size": len(self._entropy_history)
                },
                "drift": {
                    "detected": drift_detected,
                    "type": drift_type.value,
                    "threshold": self._drift_threshold
                },
                "adaptation_strategies": self._adaptation_strategies.copy(),
                "recent_adaptations": [
                    {
                        "action_type": a.action_type,
                        "reason": a.reason,
                        "effectiveness": a.effectiveness
                    }
                    for a in self._adaptation_history[-5:]
                ],
                "statistics": {
                    "total_adaptations": len(self._adaptation_history),
                    "avg_error_rate": sum(self._error_history) / max(len(self._error_history), 1),
                    "avg_response_length": sum(self._response_time_history) / max(len(self._response_time_history), 1)
                }
            }


# ==================== 全局实例 ====================

_adapter_instance = None
_adapter_lock = threading.Lock()


def get_adapter() -> LowEntropyAdapter:
    """获取低熵适应器单例"""
    global _adapter_instance
    if _adapter_instance is None:
        with _adapter_lock:
            if _adapter_instance is None:
                _adapter_instance = LowEntropyAdapter()
    return _adapter_instance


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Low Entropy Adaptation Mechanism Test")
    print("=" * 60)
    
    adapter = get_adapter()
    
    # Test 1: 正常熵值更新
    print("\nTest 1: Normal Entropy Update")
    for i in range(5):
        state = adapter.update(
            response_length=100 + i * 10,
            reasoning_steps=3,
            tool_calls=1,
            error_count=0
        )
        print(f"  Step {i+1}: entropy={state.entropy:.3f}, drift={state.drift_detected}")
    
    # Test 2: 突然漂移
    print("\nTest 2: Sudden Drift Detection")
    state = adapter.update(
        response_length=500,  # 突然变长
        reasoning_steps=10,
        tool_calls=3,
        error_count=2
    )
    print(f"  Detected: drift={state.drift_detected}, type={state.drift_type.value}")
    
    # Test 3: 适应动作
    print("\nTest 3: Adaptation Action")
    action = adapter.adapt(state)
    print(f"  Action: {action.action_type}")
    print(f"  Reason: {action.reason}")
    print(f"  Before: {action.before_state}")
    print(f"  After: {action.after_state}")
    
    # Test 4: 描述长度
    print("\nTest 4: Description Length")
    text1 = "hello world hello world hello world"
    text2 = "xyz abc def ghi jkl mno pqr"
    len1 = adapter.get_description_length(text1)
    len2 = adapter.get_description_length(text2)
    print(f"  Repetitive text: {len1:.1f}")
    print(f"  Unique text: {len2:.1f}")
    
    # Test 5: 获取状态
    print("\nTest 5: Current State")
    status = adapter.get_state()
    print(f"  Current entropy: {status['entropy']['current']:.3f}")
    print(f"  Drift detected: {status['drift']['detected']}")
    print(f"  Adaptation strategies: {status['adaptation_strategies']}")
    
    print("\nLow Entropy Adaptation Mechanism Ready")
