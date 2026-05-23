# -*- coding: utf-8 -*-
"""
M69: 吸引子稳定性分析器 (Attractor Stability Analyzer)
基于《数学完备化》论文 §6.2 动力系统吸引子追踪

核心概念:
- 吸引子: 动力系统的稳定状态
- 吸引域: 吸引子吸引的状态空间区域
- 分岔: 系统结构的突变

定理6.1: 允许组分/叙事元素大规模替换，
        只要关系结构保持吸引子稳定，则I可维持

TY/IDO Property 3 集成 (长程推理/可保持):
- 子目标分解: 将稳定性分析拆分为多步推理链
- 每步验证: 每步结果经 StepVerifier 验收
- 错误恢复: Plan B 降级策略（近似计算 → 保守判定）
- 资源预算: 超时/算力限制下优雅降级
"""
# [_modified] M69 integrated with TYIDO P3 LongRangeReasoning

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import deque
import math
import sys
import os

# 导入 TY/IDO Property 3 共享基础设施
_tyido_path = os.path.dirname(os.path.abspath(__file__))
if _tyido_path not in sys.path:
    sys.path.insert(0, _tyido_path)

try:
    from TYIDO_LongRangeReasoning import (
        SubGoal, SubGoalDecomposer, StepVerifier,
        PlanBFallback, ResourceBudget, FallbackPlan
    )
    _P3_AVAILABLE = True
except ImportError:
    _P3_AVAILABLE = False

class AttractorStabilityAnalyzer:
    """
    吸引子稳定性分析器
    
    来源: §6.2 动力系统吸引子追踪
    
    TY/IDO Property 3 (长程推理/可保持) 集成:
    - 子目标分解: 将稳定性分析拆分为多步推理链
    - 每步验证: 每步结果经 StepVerifier 验收
    - 错误恢复: Plan B 降级策略
    - 资源预算: 超时/算力限制下优雅降级
    """
    _instance = None
    
    def __init__(self, history_length: int = 100):
        self.history_length = history_length
        self.state_trajectory: List[np.ndarray] = []
        self.attractors: List[dict] = []
        self.basin_boundaries: List[dict] = []
        self.stability_metrics: List[dict] = []
        self.current_attractor: Optional[dict] = None
        
        # TY/IDO Property 3 组件
        if _P3_AVAILABLE:
            self._p3_decomposer = SubGoalDecomposer(task_name="AttractorAnalysis")
            self._p3_verifier = StepVerifier()
            self._p3_fallback = PlanBFallback()
            self._p3_budget = ResourceBudget(max_time=10.0, max_steps=500)
            self._init_p3_fallbacks()
        else:
            self._p3_decomposer = None
            self._p3_verifier = None
            self._p3_fallback = None
            self._p3_budget = None
        self._p3_last_verdict = 'PASS'
    
    def _init_p3_fallbacks(self):
        """初始化 P3 降级策略"""
        if not self._p3_fallback:
            return
        # Plan B: 使用简化的质心估计
        self._p3_fallback.register_plan(FallbackPlan(
            plan_name="Plan B: simple_centroid",
            priority=1,
            strategy=self._fallback_simple_centroid,
            description="使用简化质心近似"
        ))
        # Plan C: 返回保守判定（不稳定）
        self._p3_fallback.register_plan(FallbackPlan(
            plan_name="Plan C: conservative_unstable",
            priority=2,
            strategy=self._fallback_conservative_unstable,
            description="保守判定为不稳定"
        ))
    
    def _fallback_simple_centroid(self, context: Dict[str, Any]) -> dict:
        """Plan B: 简化质心"""
        states = context.get('states', [])
        if not states:
            return {'center': [0.0, 0.0, 0.0], 'stability': 0.3, 'type': '不稳定吸引子'}
        centroid = np.mean(np.array(states[-10:]), axis=0).tolist()
        return {'center': centroid, 'stability': 0.4, 'type': '半稳定吸引子'}
    
    def _fallback_conservative_unstable(self, context: Dict[str, Any]) -> dict:
        """Plan C: 保守不稳定"""
        return {'center': [0.0, 0.0, 0.0], 'stability': 0.1, 'type': '不稳定吸引子'}
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def add_state(self, state: np.ndarray) -> dict:
        """
        添加状态到轨迹
        
        TY/IDO P3 长程推理模式:
        推理链: S1(输入验证) → S2(更新轨迹) → S3(更新吸引子) → S4(验证稳定性)
        
        Args:
            state: 状态向量
        """
        # --- TY/IDO P3: 资源预算启动 ---
        if self._p3_budget:
            self._p3_budget.start()
        
        p3_diagnostics = {'budget_exhausted': False, 'fallback_used': None}
        result = {'status': 'insufficient_data'}
        
        try:
            # 确保是numpy数组 (S1: 输入验证)
            if self._p3_budget and self._p3_budget.exhausted():
                raise TimeoutError("Budget exhausted at S1")
            
            if not isinstance(state, np.ndarray):
                state = np.array(state)

            if self._p3_budget:
                self._p3_budget.tick()
                v1 = self._p3_verifier.verify(
                    len(state),
                    {'name': 'state_dim_positive', 'type': 'min', 'expected': 1}
                )
                if not v1['passed']:
                    raise ValueError(f"S1 failed: state dimension invalid")
            
            # S2: 更新轨迹
            if self._p3_budget and self._p3_budget.exhausted():
                degrade = self._p3_budget.graceful_degrade({'step': 'S2_skipped', 'trajectory_len': len(self.state_trajectory)})
                p3_diagnostics['budget_exhausted'] = True
                raise TimeoutError("Budget exhausted at S2")
            
            self.state_trajectory.append(state)
            if len(self.state_trajectory) > self.history_length:
                self.state_trajectory.pop(0)
            if self._p3_budget:
                self._p3_budget.tick()
            if self._p3_budget and self._p3_budget.exhausted():
                raise TimeoutError("Budget exhausted at S3")
            
            result = self._update_attractor()
            if self._p3_budget:
                self._p3_budget.tick()
            if self._p3_verifier and result.get('stability') is not None:
                v4 = self._p3_verifier.verify(
                    result['stability'],
                    {'name': 'stability_range', 'type': 'range', 'low': 0, 'high': 1}
                )
                if not v4['passed']:
                    recovery = self._p3_fallback.try_recover(
                        failed_goal="S4_verify_stability",
                        error=ValueError(v4['details']),
                        context={'states': self.state_trajectory[-20:]}
                    )
                    p3_diagnostics['fallback_used'] = recovery['plan_used']
                    result = recovery['result']
            
            if self._p3_budget:
                self._p3_budget.tick()
        
        except TimeoutError:
            p3_diagnostics['budget_exhausted'] = True
            # 优雅降级: 返回保守不稳定判定
            if self._p3_fallback:
                recovery = self._p3_fallback.try_recover(
                    failed_goal="add_state",
                    error=TimeoutError("Budget exhausted"),
                    context={'states': self.state_trajectory[-10:] if self.state_trajectory else []}
                )
                p3_diagnostics['fallback_used'] = recovery['plan_used']
                result = recovery['result']
            else:
                result = {'stability': 0.1, 'type': '不稳定吸引子', 'degraded': True}
        
        except Exception as e:
            if self._p3_fallback:
                recovery = self._p3_fallback.try_recover(
                    failed_goal="add_state",
                    error=e,
                    context={'states': self.state_trajectory[-10:] if self.state_trajectory else []}
                )
                p3_diagnostics['fallback_used'] = recovery['plan_used']
                result = recovery['result']
            else:
                raise
        
        finally:
            if self._p3_budget:
                self._p3_budget.stop()
        
        # 附加 P3 诊断
        # P3 诊断 — budget_exhausted 优先于 fallback_used
        if p3_diagnostics.get('budget_exhausted'):
            result['tyido_p3'] = {'verdict': 'DEGRADED'}
            self._p3_last_verdict = 'DEGRADED'
        elif p3_diagnostics.get('fallback_used'):
            result['tyido_p3'] = {
                'verdict': 'RECOVERED',
                'fallback_used': p3_diagnostics['fallback_used']
            }
            self._p3_last_verdict = 'RECOVERED'
        elif _P3_AVAILABLE:
            result['tyido_p3'] = {'verdict': 'PASS'}
            self._p3_last_verdict = 'PASS'
        
        return result
    
    def _update_attractor(self) -> dict:
        """更新当前吸引子"""
        if len(self.state_trajectory) < 10:
            return {'status': 'insufficient_data'}
        
        # 使用最近的状态估计吸引子位置
        recent_states = np.array(self.state_trajectory[-20:])
        
        # 吸引子 = 状态分布的质心
        attractor_center = np.mean(recent_states, axis=0)
        
        # 吸引子半径 = 标准差
        attractor_radius = np.std(recent_states, axis=0)
        avg_radius = np.mean(attractor_radius)
        
        # 计算到吸引子的距离
        current_state = self.state_trajectory[-1]
        distance_to_attractor = np.linalg.norm(current_state - attractor_center)
        
        # 判断是否在吸引域内
        in_basin = distance_to_attractor < avg_radius * 2
        
        # 计算稳定性指标
        stability = self._compute_stability(attractor_center, recent_states)
        
        self.current_attractor = {
            'center': attractor_center.tolist(),
            'radius': float(avg_radius),
            'distance': float(distance_to_attractor),
            'in_basin': in_basin,
            'stability': stability,
            'type': self._classify_attractor(stability)
        }
        
        return self.current_attractor
    
    def _compute_stability(self, center: np.ndarray, states: np.ndarray) -> float:
        """
        计算稳定性指标
        
        稳定性 = 1 / (1 + 平均距离 + 方差)
        """
        distances = [np.linalg.norm(s - center) for s in states]
        avg_distance = np.mean(distances)
        variance = np.var(distances)
        
        stability = 1 / (1 + avg_distance + variance)
        
        return float(stability)
    
    def _classify_attractor(self, stability: float) -> str:
        """吸引子分类"""
        if stability > 0.8:
            return "稳定吸引子"
        elif stability > 0.5:
            return "半稳定吸引子"
        elif stability > 0.2:
            return "不稳定吸引子"
        else:
            return "混沌吸引子"
    
    def detect_bifurcation(self, window_size: int = 10) -> dict:
        """
        检测分岔（系统结构突变）
        
        分岔检测：比较相邻窗口的统计特性变化
        """
        if len(self.state_trajectory) < window_size * 2:
            return {'bifurcation': None, 'reason': '数据不足'}
        
        # 分割窗口
        states = np.array(self.state_trajectory)
        window1 = states[-window_size*2:-window_size]
        window2 = states[-window_size:]
        
        # 计算统计量
        mean1 = np.mean(window1, axis=0)
        mean2 = np.mean(window2, axis=0)
        var1 = np.var(window1, axis=0)
        var2 = np.var(window2, axis=0)
        
        # 均值变化
        mean_change = np.linalg.norm(mean2 - mean1)
        
        # 方差变化
        var_change = np.linalg.norm(var2 - var1)
        
        # 分岔阈值
        mean_threshold = 0.3
        var_threshold = 0.2
        
        bifurcation_detected = mean_change > mean_threshold or var_change > var_threshold
        
        if bifurcation_detected:
            self.basin_boundaries.append({
                'position': len(self.state_trajectory),
                'mean_change': float(mean_change),
                'var_change': float(var_change),
                'type': '均值分岔' if mean_change > mean_threshold else '方差分岔'
            })
        
        return {
            'bifurcation': bifurcation_detected,
            'mean_change': float(mean_change),
            'var_change': float(var_change),
            'threshold': {'mean': mean_threshold, 'var': var_threshold}
        }
    
    def compute_lyapunov_approximation(self, window_size: int = 20) -> dict:
        """
        计算Lyapunov指数近似
        
        正Lyapunov指数 = 混沌
        负Lyapunov指数 = 稳定
        """
        if len(self.state_trajectory) < window_size:
            return {'lyapunov': None, 'reason': '数据不足'}
        
        states = np.array(self.state_trajectory[-window_size:])
        
        # 计算相邻状态的分离率
        separations = []
        for i in range(len(states) - 1):
            sep = np.linalg.norm(states[i + 1] - states[i])
            separations.append(sep)
        
        # 简化Lyapunov估计
        if len(separations) > 1:
            # 增长率
            growth_rates = []
            for i in range(len(separations) - 1):
                if separations[i] > 0:
                    rate = np.log(separations[i + 1] / separations[i])
                    growth_rates.append(rate)
            
            lyapunov_approx = np.mean(growth_rates) if growth_rates else 0
        else:
            lyapunov_approx = 0
        
        return {
            'lyapunov_approx': float(lyapunov_approx),
            'interpretation': '混沌' if lyapunov_approx > 0.1 else 
                           '稳定' if lyapunov_approx < -0.1 else '临界',
            'window_size': window_size
        }
    
    def get_attractor_state(self) -> dict:
        """获取当前吸引子状态"""
        if self.current_attractor is None:
            return {'has_attractor': False}
        
        return {
            'has_attractor': True,
            'attractor': self.current_attractor,
            'bifurcation': self.detect_bifurcation(),
            'lyapunov': self.compute_lyapunov_approximation()
        }
    
    def get_basin_info(self) -> dict:
        """获取吸引域信息"""
        return {
            'basin_count': len(self.attractors),
            'boundary_events': len(self.basin_boundaries),
            'current_in_basin': self.current_attractor.get('in_basin', False) if self.current_attractor else None,
            'basin_boundaries': self.basin_boundaries[-5:]  # 最近5个
        }
    
    def get_state(self) -> dict:
        """获取分析器状态（含 TY/IDO P3 诊断）"""
        state = {
            'trajectory_length': len(self.state_trajectory),
            'attractor': self.current_attractor,
            'attractor_state': self.get_attractor_state(),
            'basin_info': self.get_basin_info(),
            'stability_metrics': self.stability_metrics[-10:] if self.stability_metrics else []
        }
        # TY/IDO P3 诊断
        if _P3_AVAILABLE and self._p3_decomposer:
            state['tyido_p3'] = {
                'subgoal_progress': self._p3_decomposer.get_progress(),
                'verifier_state': self._p3_verifier.get_state() if self._p3_verifier else {},
                'fallback_state': self._p3_fallback.get_state() if self._p3_fallback else {},
                'budget_state': self._p3_budget.get_state() if self._p3_budget else {},
                'verdict': self._p3_last_verdict
            }
        return state


_instance = None

def get_instance() -> AttractorStabilityAnalyzer:
    """获取AttractorStabilityAnalyzer单例"""
    global _instance
    if _instance is None:
        _instance = AttractorStabilityAnalyzer()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M69 吸引子稳定性分析器 测试")
    print("=" * 60)
    
    analyzer = AttractorStabilityAnalyzer(history_length=50)
    
    # 模拟状态轨迹（趋近吸引子）
    print("\n模拟状态轨迹:")
    np.random.seed(42)
    
    attractor = np.array([0.5, 0.5, 0.5])
    
    for t in range(30):
        # 状态 = 吸引子 + 噪声（噪声递减）
        noise_level = 0.5 * np.exp(-0.1 * t)
        state = attractor + np.random.randn(3) * noise_level
        
        result = analyzer.add_state(state)
        
        if t % 5 == 0:
            print(f"  t={t}: 距离吸引子={result.get('distance', 0):.4f}, "
                  f"稳定性={result.get('stability', 0):.4f}")
    
    # 吸引子状态
    attr_state = analyzer.get_attractor_state()
    print(f"\n吸引子状态: {attr_state}")
    
    # 分岔检测
    bif = analyzer.detect_bifurcation()
    print(f"\n分岔检测: {bif}")
    
    # Lyapunov近似
    lyap = analyzer.compute_lyapunov_approximation()
    print(f"\nLyapunov近似: {lyap}")
    
    # 整体状态
    state = analyzer.get_state()
    print(f"\n分析器状态:")
    print(f"  轨迹长度: {state['trajectory_length']}")
    print(f"  当前吸引子类型: {state['attractor']['type'] if state['attractor'] else 'N/A'}")
    
    print("\n" + "=" * 60)
    print("✅ M69 测试完成")
    print("=" * 60)
