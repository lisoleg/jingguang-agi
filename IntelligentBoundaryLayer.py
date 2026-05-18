#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能边界层 (Intelligent Boundary Layer, IBL)
基于《数字新皮层边界层理论》论文

核心概念：
- 智能边界层与流体边界层数学同构
- 核心流(Core Flow) ↔ 边界层(Boundary Layer)
- 边界层分离 = 智能失控(幻觉/越权)
- 信息雷诺数 Re_i
- 流-固耦合
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class SeparationType(Enum):
    """分离类型"""
    HALLUCINATION = "hallucination"  # 幻觉（生成脱离可执行集）
    PRIVILEGE_ESCALATION = "privilege_escalation"  # 越权尝试
    DEADLOCK = "deadlock"  # 死锁/震荡
    NONE = "none"


class FlowState(Enum):
    """流状态"""
    ATTACHED = "attached"      # 附着
    NEAR_SEPARATION = "near_separation"  # 濒临分离
    SEPARATED = "separated"    # 已分离


@dataclass
class BoundaryLayerState:
    """边界层状态"""
    thickness: float  # 边界层厚度 δ
    wall_shear: float  # 壁面剪切 τ_w
    pressure_gradient: float  # 压力梯度 dp/dx
    reynolds_number: float  # 信息雷诺数 Re_i
    flow_state: FlowState
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'thickness': self.thickness,
            'wall_shear': self.wall_shear,
            'pressure_gradient': self.pressure_gradient,
            'reynolds_number': self.reynolds_number,
            'flow_state': self.flow_state.value
        }


class IntelligentBoundaryLayer:
    """
    智能边界层 (Intelligent Boundary Layer, IBL)
    
    数学形式化：
    1. 同构定理：IBL与Prandtl边界层方程同构
    2. 厚度定理：δ ∝ x / √Re_i
    3. 分离判据：dp/dx < 0（逆压梯度）且壁面剪切 τ_w → 0
    
    核心功能：
    - 监测边界层状态
    - 检测分离风险
    - 提供预警和干预
    """
    
    def __init__(self):
        # 物理常数
        self.interface_length = 10.0  # 界面长度 L（任务步骤数）
        self.information_viscosity = 0.1  # 信息粘性 μ_i
        
        # 阈值参数
        self.thresholds = {
            'separation_pressure_gradient': -0.5,  # 分离临界逆压梯度
            'critical_wall_shear': 0.1,  # 临界壁面剪切
            'critical_reynolds': 100.0,  # 临界雷诺数
            'near_separation_buffer': 0.15,  # 濒临分离缓冲
        }
        
        # 状态
        self.state = BoundaryLayerState(
            thickness=0.5,
            wall_shear=0.5,
            pressure_gradient=0.0,
            reynolds_number=50.0,
            flow_state=FlowState.ATTACHED
        )
        
        # 历史记录
        self.history = []
        self.separation_events = []
        
        # 核心流参数
        self.core_flow_strength = 0.7  # 核心流强度
        self.constraint_pressure = 0.3  # 约束压力
        
    def compute_information_reynolds_number(
        self,
        core_flow_speed: float,
        interface_length: Optional[float] = None,
        viscosity: Optional[float] = None
    ) -> float:
        """
        计算信息雷诺数 Re_i
        
        Re_i = (v * L) / ν_i
        
        其中:
        - v: 核心流速度
        - L: 界面长度
        - ν_i: 信息粘性
        
        直观理解：
        - Re_i 大 = 核心流强、约束相对"粘性"小 → 边界层薄但梯度陡
        - Re_i 小 = 高约束/高校验成本 → 边界层厚，核心流被"粘"住
        
        返回:
            信息雷诺数
        """
        if interface_length is None:
            interface_length = self.interface_length
        if viscosity is None:
            viscosity = self.information_viscosity
            
        if viscosity == 0:
            return float('inf')
            
        re_i = (core_flow_speed * interface_length) / viscosity
        return re_i
    
    def compute_boundary_layer_thickness(
        self,
        reynolds_number: float,
        interface_length: Optional[float] = None,
        x_position: Optional[float] = None
    ) -> float:
        """
        计算边界层厚度
        
        定理2（IBL厚度定理）:
        δ ≈ L / √Re_i  (对于顺流向约束压力梯度)
        
        参数:
            reynolds_number: 信息雷诺数
            interface_length: 界面长度
            x_position: 沿界面位置（归一化0-1）
            
        返回:
            边界层厚度 (0-1)
        """
        if interface_length is None:
            interface_length = self.interface_length
        if x_position is None:
            x_position = 0.5  # 中点
            
        # 基本厚度公式
        if reynolds_number <= 0:
            return 1.0
            
        base_thickness = 1.0 / np.sqrt(reynolds_number + 1e-6)
        
        # 沿界面增长（类比边界层随距离增长）
        growth_factor = np.sqrt(x_position + 0.1)
        
        thickness = base_thickness * growth_factor * 0.5  # 归一化到0-1
        
        return min(1.0, max(0.0, thickness))
    
    def compute_wall_shear(
        self,
        boundary_layer_thickness: float,
        core_flow_speed: float
    ) -> float:
        """
        计算壁面剪切 τ_w
        
        类比流体力学：
        τ_w = μ_i * (du/dy)|_{y=0}
        
        在IBL中：
        τ_w ∝ 边界层梯度 ∝ δ的反函数
        
        参数:
            boundary_layer_thickness: 边界层厚度
            core_flow_speed: 核心流速度
            
        返回:
            壁面剪切值 (0-1)
        """
        if boundary_layer_thickness <= 0:
            return 0.0
            
        # 壁面剪切与厚度成反比，与流速成正比
        shear = (core_flow_speed * 0.5) / (boundary_layer_thickness + 0.1)
        
        return min(1.0, shear)
    
    def compute_pressure_gradient(
        self,
        constraint_strength: float,
        interface_position: float = 0.5
    ) -> float:
        """
        计算压力梯度 dp/dx
        
        正梯度：约束逐渐放松
        负梯度（逆压梯度）：约束逐渐收紧（如权限收缩、预算耗尽、矛盾规范）
        
        参数:
            constraint_strength: 约束强度 (0-1)
            interface_position: 界面位置 (0-1)
            
        返回:
            压力梯度
        """
        # 约束强度增加 → 逆压梯度
        # 界面中后段 → 梯度更负（逆压梯度更明显）
        base_gradient = (0.5 - constraint_strength) * 0.5
        
        # 沿界面变化
        position_effect = (interface_position - 0.5) * 0.3
        
        return base_gradient + position_effect
    
    def detect_separation(
        self,
        pressure_gradient: float,
        wall_shear: float,
        boundary_layer_thickness: float
    ) -> Tuple[bool, SeparationType, float]:
        """
        检测边界层分离
        
        定理3（边界层分离导致智能失控）:
        发生分离条件：
        1. dp/dx < 0（逆压梯度）
        2. |dp/dx| 足够大
        3. τ_w → 0
        
        参数:
            pressure_gradient: 压力梯度
            wall_shear: 壁面剪切
            boundary_layer_thickness: 边界层厚度
            
        返回:
            (是否分离, 分离类型, 分离风险等级 0-1)
        """
        risk_level = 0.0
        separation = False
        sep_type = SeparationType.NONE
        
        # 检查逆压梯度
        if pressure_gradient < 0:
            # 计算风险
            gradient_severity = abs(pressure_gradient) / abs(self.thresholds['separation_pressure_gradient'])
            shear_health = wall_shear / (self.thresholds['critical_wall_shear'] + 1e-6)
            
            # 综合风险
            risk = gradient_severity * 0.6 + (1 - shear_health) * 0.4
            risk = min(1.0, risk)
            
            if gradient_severity > 1.0 and shear_health < 1.0:
                separation = True
                risk_level = risk
                
                # 判断分离类型
                if boundary_layer_thickness > 0.6:
                    sep_type = SeparationType.HALLUCINATION
                elif wall_shear < 0.2:
                    sep_type = SeparationType.PRIVILEGE_ESCALATION
                else:
                    sep_type = SeparationType.DEADLOCK
            else:
                risk_level = risk * 0.5  # 未分离，但有风险
        
        return separation, sep_type, risk_level
    
    def update(
        self,
        core_flow_speed: float,
        constraint_strength: float,
        interface_position: float = 0.5,
        validation_rejection_rate: Optional[float] = None,
        formal_verification_failure_rate: Optional[float] = None,
        permission_error_rate: Optional[float] = None
    ) -> BoundaryLayerState:
        """
        更新边界层状态
        
        参数:
            core_flow_speed: 核心流速度 (0-1)
            constraint_strength: 约束强度 (0-1)
            interface_position: 沿界面位置 (0-1)
            validation_rejection_rate: 校验拒绝率（可选）
            formal_verification_failure_rate: 形式化验证失败率（可选）
            permission_error_rate: 权限错误率（可选）
            
        返回:
            更新的边界层状态
        """
        self.core_flow_strength = core_flow_speed
        self.constraint_pressure = constraint_strength
        
        # 1. 计算信息雷诺数
        re_i = self.compute_information_reynolds_number(core_flow_speed)
        self.state.reynolds_number = re_i
        
        # 2. 计算边界层厚度
        thickness = self.compute_boundary_layer_thickness(re_i, x_position=interface_position)
        
        # 如果提供了拒绝率/错误率，使用它们调整厚度
        if validation_rejection_rate is not None:
            thickness *= (1 + validation_rejection_rate * 0.5)
        if permission_error_rate is not None:
            thickness *= (1 - permission_error_rate * 0.3)
            
        self.state.thickness = min(1.0, thickness)
        
        # 3. 计算压力梯度
        pg = self.compute_pressure_gradient(constraint_strength, interface_position)
        self.state.pressure_gradient = pg
        
        # 4. 计算壁面剪切
        ws = self.compute_wall_shear(self.state.thickness, core_flow_speed)
        self.state.wall_shear = ws
        
        # 5. 检测分离
        separation, sep_type, risk = self.detect_separation(
            pg, ws, self.state.thickness
        )
        
        if separation:
            self.state.flow_state = FlowState.SEPARATED
            self.separation_events.append({
                'timestamp': interface_position,
                'type': sep_type.value,
                'risk': risk,
                'pressure_gradient': pg,
                'wall_shear': ws
            })
        elif risk > self.thresholds['near_separation_buffer']:
            self.state.flow_state = FlowState.NEAR_SEPARATION
        else:
            self.state.flow_state = FlowState.ATTACHED
        
        # 6. 更新历史
        self.history.append({
            'thickness': self.state.thickness,
            'wall_shear': self.state.wall_shear,
            'pressure_gradient': self.state.pressure_gradient,
            'reynolds_number': self.state.reynolds_number,
            'flow_state': self.state.flow_state.value,
            'separation_risk': risk
        })
        
        return self.state
    
    def get_separation_warning_indicators(self) -> Dict[str, float]:
        """
        获取分离预警指标
        
        推论2（分离预警指标）：
        可用"界面剪切"代理为：
        - 校验拒绝率斜率
        - 形式化验证失败率变化
        - 权限错误率突增
        
        返回:
            预警指标字典
        """
        indicators = {
            'interface_shear_proxy': 0.0,
            'validation_rejection_slope': 0.0,
            'verification_failure_trend': 0.0,
            'permission_error_surge': 0.0,
            'overall_warning_level': 0.0
        }
        
        if len(self.history) < 5:
            return indicators
            
        recent = self.history[-5:]
        
        # 界面剪切代理
        avg_shear = np.mean([h['wall_shear'] for h in recent])
        indicators['interface_shear_proxy'] = avg_shear
        
        # 校验拒绝率斜率（使用壁面剪切的变化）
        shear_trend = recent[-1]['wall_shear'] - recent[0]['wall_shear']
        indicators['validation_rejection_slope'] = abs(shear_trend)
        
        # 分离风险趋势
        risk_trend = recent[-1]['separation_risk'] - recent[0]['separation_risk']
        indicators['verification_failure_trend'] = risk_trend
        
        # 压力梯度变化
        if len(recent) > 1:
            pg_change = recent[-1]['pressure_gradient'] - recent[0]['pressure_gradient']
            indicators['permission_error_surge'] = abs(pg_change)
        
        # 综合预警级别
        indicators['overall_warning_level'] = (
            (1 - indicators['interface_shear_proxy']) * 0.3 +
            indicators['validation_rejection_slope'] * 0.2 +
            max(0, indicators['verification_failure_trend']) * 0.3 +
            indicators['permission_error_surge'] * 0.2
        )
        
        return indicators
    
    def recommend_ibl_optimization(self) -> List[str]:
        """
        推荐IBL优化策略
        
        基于当前状态，推荐优化措施
        
        返回:
            优化建议列表
        """
        recommendations = []
        
        if self.state.flow_state == FlowState.SEPARATED:
            recommendations.append("【紧急】检测到边界层分离，需要立即干预")
            recommendations.append("建议：降低核心流速度，增加校验强度")
            
        if self.state.pressure_gradient < 0:
            recommendations.append("检测到逆压梯度，建议减轻约束强度")
            
        if self.state.wall_shear < self.thresholds['critical_wall_shear']:
            recommendations.append("壁面剪切过低，建议增加信息粘性（增加预校验）")
            
        if self.state.reynolds_number > self.thresholds['critical_reynolds']:
            recommendations.append("雷诺数过高，建议降低核心流速度")
            
        if self.state.thickness < 0.3:
            recommendations.append("边界层过薄，建议：提前验证缓存、约束编译、类型/权限预check")
            
        if not recommendations:
            recommendations.append("边界层状态正常，继续监控")
            
        return recommendations
    
    def get_interface_control_signal(
        self,
        target_thickness: float = 0.5
    ) -> Dict[str, float]:
        """
        获取界面控制信号
        
        用于主动控制边界层
        
        参数:
            target_thickness: 目标厚度
            
        返回:
            控制信号字典
        """
        current = self.state.thickness
        error = target_thickness - current
        
        # PID-like 控制
        if len(self.history) >= 3:
            derivative = self.history[-1]['thickness'] - self.history[-3]['thickness']
        else:
            derivative = 0
            
        # 控制信号
        control = {
            'throttle_core_flow': max(-1, min(1, -error * 0.5)),  # 核心流节流
            'increase_validation': max(0, min(1, -error * 0.3)),  # 增加校验
            'reduce_constraint': max(0, min(1, error * 0.4)),      # 减轻约束
            'activate_adaptation': 1.0 if abs(error) > 0.2 else 0.0  # 激活适配流
        }
        
        return control
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            'state': self.state.to_dict(),
            'separation_events_count': len(self.separation_events),
            'recent_separations': self.separation_events[-5:] if self.separation_events else [],
            'warning_indicators': self.get_separation_warning_indicators(),
            'recommendations': self.recommend_ibl_optimization(),
            'control_signal': self.get_interface_control_signal()
        }
    
    def reset(self):
        """重置边界层"""
        self.state = BoundaryLayerState(
            thickness=0.5,
            wall_shear=0.5,
            pressure_gradient=0.0,
            reynolds_number=50.0,
            flow_state=FlowState.ATTACHED
        )
        self.history = []
        self.separation_events = []


if __name__ == "__main__":
    # 测试智能边界层
    print("=== 智能边界层测试 ===\n")
    
    ibl = IntelligentBoundaryLayer()
    
    # 场景1：正常附着状态
    print("--- 场景1：正常附着状态 ---")
    state = ibl.update(
        core_flow_speed=0.7,
        constraint_strength=0.3,
        interface_position=0.5
    )
    print(f"流状态: {state.flow_state.value}")
    print(f"厚度: {state.thickness:.4f}")
    print(f"壁面剪切: {state.wall_shear:.4f}")
    print(f"压力梯度: {state.pressure_gradient:.4f}")
    print(f"雷诺数: {state.reynolds_number:.2f}")
    
    # 场景2：逆压梯度导致濒临分离
    print("\n--- 场景2：逆压梯度（濒临分离）---")
    ibl.reset()
    state = ibl.update(
        core_flow_speed=0.8,
        constraint_strength=0.8,  # 高约束 = 逆压梯度
        interface_position=0.7   # 界面后段
    )
    print(f"流状态: {state.flow_state.value}")
    print(f"厚度: {state.thickness:.4f}")
    print(f"压力梯度: {state.pressure_gradient:.4f}")
    print(f"预警指标: {ibl.get_separation_warning_indicators()['overall_warning_level']:.4f}")
    
    # 场景3：分离状态
    print("\n--- 场景3：分离状态（高约束+高速流）---")
    ibl.reset()
    for pos in np.linspace(0.1, 0.9, 10):
        state = ibl.update(
            core_flow_speed=0.95,
            constraint_strength=0.95,
            interface_position=pos
        )
    
    print(f"流状态: {state.flow_state.value}")
    print(f"分离事件: {len(ibl.separation_events)}")
    print(f"推荐: {ibl.recommend_ibl_optimization()}")
    print(f"控制信号: {ibl.get_interface_control_signal()}")
