# -*- coding: utf-8 -*-
"""
太乙AGI 6.0 - 弹簧虫协调总线动画引擎
Spring Worm Coordination Bus Animation Engine

灵感来源：弹簧虫定理
- 质心守恒：用户焦点保持稳定
- 能量循环：交互能量有效传递
- 缓冲碰撞：复杂操作的平滑过渡

融合复合体理学全息拓扑动力学

版本: v1.0
日期: 2026-05-13
"""

import math
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading


class EasingFunction(Enum):
    """缓动函数枚举"""
    # 线性
    LINEAR = "linear"
    
    # 弹簧类
    SPRING = "spring"
    SPRING_BOUNCY = "spring_bouncy"
    SPRING_SMOOTH = "spring_smooth"
    
    # 弹性类
    ELASTIC = "elastic"
    ELASTIC_IN = "elastic_in"
    ELASTIC_OUT = "elastic_out"
    
    # 缓动类
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    
    # 弹性阻尼
    DAMPED = "damped"
    UNDERDAMPED = "underdamped"
    CRITICAL = "critical"
    OVERDAMPED = "overdamped"


@dataclass
class SpringPhysics:
    """弹簧物理参数"""
    stiffness: float = 200.0      # 刚度系数 (N/m)
    damping: float = 10.0         # 阻尼系数
    mass: float = 1.0             # 质量 (kg)
    
    # 状态
    position: float = 0.0         # 当前位置
    velocity: float = 0.0         # 当前速度
    target: float = 0.0          # 目标位置
    displacement: float = 0.0    # 位移
    
    # 能量
    kinetic_energy: float = 0.0   # 动能
    potential_energy: float = 0.0 # 势能
    total_energy: float = 0.0    # 总能量
    
    # 状态标志
    is_settled: bool = True       # 是否稳定
    oscillation_count: int = 0    # 振荡次数
    
    def compute_derivatives(self) -> Tuple[float, float]:
        """
        计算弹簧运动方程的导数
        基于胡克定律和阻尼力
        """
        # 位移 = 当前位置 - 目标位置
        self.displacement = self.position - self.target
        
        # 弹簧力 F = -k * x (胡克定律)
        spring_force = -self.stiffness * self.displacement
        
        # 阻尼力 F = -c * v
        damping_force = -self.damping * self.velocity
        
        # 合外力
        total_force = spring_force + damping_force
        
        # 加速度 a = F / m
        acceleration = total_force / self.mass
        
        return (self.velocity, acceleration)
    
    def update(self, dt: float) -> bool:
        """
        更新弹簧状态
        使用RK4积分
        
        Args:
            dt: 时间步长
            
        Returns:
            是否稳定
        """
        # RK4积分
        k1_v, k1_a = self.compute_derivatives()
        
        temp_pos = self.position + k1_v * dt * 0.5
        temp_vel = self.velocity + k1_a * dt * 0.5
        saved_disp = self.displacement
        saved_kin = self.kinetic_energy
        
        self.position = temp_pos
        self.velocity = temp_vel
        
        k2_v, k2_a = self.compute_derivatives()
        
        self.position = temp_pos + k2_v * dt * 0.5
        self.velocity = temp_vel + k2_a * dt * 0.5
        
        k3_v, k3_a = self.compute_derivatives()
        
        self.position = temp_pos + k3_v * dt
        self.velocity = temp_vel + k3_a * dt
        
        k4_v, k4_a = self.compute_derivatives()
        
        # 更新位置和速度
        self.position += (k1_v + 2*k2_v + 2*k3_v + k4_v) * dt / 6
        self.velocity += (k1_a + 2*k2_a + 2*k3_a + k4_a) * dt / 6
        
        # 计算能量
        self.kinetic_energy = 0.5 * self.mass * self.velocity ** 2
        self.potential_energy = 0.5 * self.stiffness * self.displacement ** 2
        self.total_energy = self.kinetic_energy + self.potential_energy
        
        # 检查是否稳定
        self.is_settled = (abs(self.displacement) < 0.001 and 
                          abs(self.velocity) < 0.001)
        
        # 记录振荡
        if abs(self.displacement) > 0.01:
            self.oscillation_count += 1
        
        return self.is_settled
    
    def set_target(self, target: float, impulse: float = 0.0):
        """
        设置目标位置
        
        Args:
            target: 目标位置
            impulse: 冲量(初始速度)
        """
        self.target = target
        self.velocity += impulse
        self.is_settled = False


@dataclass
class WormSegment:
    """虫段数据"""
    index: int              # 段索引
    position: Tuple[float, float]  # 位置 (x, y)
    velocity: Tuple[float, float]  # 速度 (vx, vy)
    acceleration: Tuple[float, float]  # 加速度 (ax, ay)
    curvature: float = 0.0  # 曲率
    tension: float = 0.0    # 张力
    mass: float = 1.0       # 质量
    
    # 视觉属性
    radius: float = 10.0    # 半径
    color_hue: float = 200  # 色调
    glow_intensity: float = 0.5  # 发光强度
    opacity: float = 1.0    # 透明度


@dataclass
class AnimationTask:
    """动画任务"""
    id: str
    start_time: float
    duration: float
    start_value: Any
    end_value: Any
    easing: EasingFunction
    callback: Optional[Callable] = None
    on_complete: Optional[Callable] = None
    
    # 状态
    progress: float = 0.0
    current_value: Any = None
    is_complete: bool = False
    
    def update(self, current_time: float) -> Any:
        """更新动画进度"""
        elapsed = current_time - self.start_time
        self.progress = min(elapsed / self.duration, 1.0)
        
        # 应用缓动函数
        eased_progress = self._apply_easing(self.progress)
        
        # 计算当前值
        if isinstance(self.start_value, (int, float)):
            self.current_value = self._interpolate(
                self.start_value, self.end_value, eased_progress
            )
        elif isinstance(self.start_value, tuple):
            self.current_value = tuple(
                self._interpolate(s, e, eased_progress) 
                for s, e in zip(self.start_value, self.end_value)
            )
        elif isinstance(self.start_value, list):
            self.current_value = [
                self._interpolate(s, e, eased_progress) 
                for s, e in zip(self.start_value, self.end_value)
            ]
        
        if self.progress >= 1.0 and not self.is_complete:
            self.is_complete = True
            if self.on_complete:
                self.on_complete(self)
        
        return self.current_value
    
    def _interpolate(self, start: float, end: float, t: float) -> float:
        """插值"""
        return start + (end - start) * t
    
    def _apply_easing(self, t: float) -> float:
        """应用缓动函数"""
        if self.easing == EasingFunction.LINEAR:
            return t
        
        elif self.easing == EasingFunction.EASE_IN:
            return t * t
        
        elif self.easing == EasingFunction.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        
        elif self.easing == EasingFunction.EASE_IN_OUT:
            return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
        
        elif self.easing == EasingFunction.SPRING:
            # 弹簧效果
            omega = math.sqrt(200)  # 假设刚度200
            zeta = 0.5  # 阻尼比
            decay = math.exp(-zeta * omega * t)
            return 1 - decay * math.cos(omega * math.sqrt(1 - zeta**2) * t)
        
        elif self.easing == EasingFunction.SPRING_BOUNCY:
            omega = math.sqrt(300)
            zeta = 0.3
            decay = math.exp(-zeta * omega * t)
            return 1 - decay * (1 + omega * t) * math.cos(omega * t)
        
        elif self.easing == EasingFunction.SPRING_SMOOTH:
            omega = math.sqrt(150)
            zeta = 0.7
            decay = math.exp(-zeta * omega * t)
            return 1 - decay * math.cos(omega * math.sqrt(1 - zeta**2) * t)
        
        elif self.easing == EasingFunction.ELASTIC:
            if t == 0 or t == 1:
                return t
            return math.sin(13 * math.pi / 2 * t) * pow(2, -10 * t) + 1
        
        elif self.easing == EasingFunction.ELASTIC_OUT:
            if t == 0 or t == 1:
                return t
            return math.sin(-13 * math.pi / 2 * (t + 1)) * math.pow(2, -10 * t) + 1
        
        elif self.easing == EasingFunction.DAMPED:
            omega = math.sqrt(100)
            zeta = 1.0  # 临界阻尼
            return 1 - (1 + omega * t) * math.exp(-omega * t)
        
        elif self.easing == EasingFunction.UNDERDAMPED:
            omega = math.sqrt(200)
            zeta = 0.5
            return 1 - math.exp(-zeta * omega * t) * (
                math.cos(omega * math.sqrt(1 - zeta**2) * t) +
                (zeta / math.sqrt(1 - zeta**2)) * 
                math.sin(omega * math.sqrt(1 - zeta**2) * t)
            )
        
        elif self.easing == EasisFunction.OVERDAMPED:
            omega = math.sqrt(200)
            zeta = 2.0
            r1 = -omega * (zeta + math.sqrt(zeta**2 - 1))
            r2 = -omega * (zeta - math.sqrt(zeta**2 - 1))
            return 1 + (r2 * math.exp(r1 * t) - r1 * math.exp(r2 * t)) / (r2 - r1)
        
        return t


class SpringWormEngine:
    """
    弹簧虫协调总线动画引擎
    
    核心功能：
    1. 弹簧物理系统 - 实现惯性/弹性/阻尼动效
    2. 虫链动画 - 连接多个元素的平滑动画
    3. 缓动函数库 - 丰富的缓动函数
    4. 任务调度 - 管理多个并行动画
    
    融合复合体理学：
    - 质心守恒 → 焦点稳定
    - 能量循环 → 动效传递
    - 缓冲碰撞 → 平滑过渡
    """
    
    def __init__(self):
        """初始化引擎"""
        # 弹簧系统
        self.springs: Dict[str, SpringPhysics] = {}
        
        # 虫链
        self.worm_chains: Dict[str, List[WormSegment]] = {}
        
        # 动画任务
        self.animation_tasks: Dict[str, AnimationTask] = {}
        self._task_counter = 0
        
        # 全局参数
        self.global_speed: float = 1.0
        self.enable_spring: bool = True
        self.enable_worm: bool = True
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 回调
        self.on_update: Optional[Callable] = None
        self._running = False
        self._last_update = time.time()
        
        # 能量统计
        self.energy_stats = {
            "total_kinetic": 0.0,
            "total_potential": 0.0,
            "max_velocity": 0.0,
        }
    
    # ==================== 弹簧管理 ====================
    
    def create_spring(self, spring_id: str,
                     stiffness: float = 200.0,
                     damping: float = 10.0,
                     mass: float = 1.0) -> SpringPhysics:
        """
        创建弹簧
        
        Args:
            spring_id: 弹簧ID
            stiffness: 刚度
            damping: 阻尼
            mass: 质量
        """
        with self._lock:
            spring = SpringPhysics(
                stiffness=stiffness,
                damping=damping,
                mass=mass,
            )
            self.springs[spring_id] = spring
            return spring
    
    def set_spring_target(self, spring_id: str, 
                         target: float,
                         impulse: float = 0.0):
        """设置弹簧目标"""
        if spring_id in self.springs:
            self.springs[spring_id].set_target(target, impulse)
    
    def get_spring_value(self, spring_id: str) -> float:
        """获取弹簧当前值"""
        if spring_id in self.springs:
            return self.springs[spring_id].position
        return 0.0
    
    def remove_spring(self, spring_id: str):
        """移除弹簧"""
        with self._lock:
            if spring_id in self.springs:
                del self.springs[spring_id]
    
    # ==================== 虫链管理 ====================
    
    def create_worm_chain(self, chain_id: str,
                         segment_count: int = 5,
                         spacing: float = 20.0) -> List[WormSegment]:
        """
        创建虫链
        
        Args:
            chain_id: 链ID
            segment_count: 段数
            spacing: 段间距
        """
        segments = []
        for i in range(segment_count):
            segment = WormSegment(
                index=i,
                position=(i * spacing, 0),
                velocity=(0, 0),
                acceleration=(0, 0),
                radius=10 - i * 0.5,  # 渐变半径
                color_hue=200 + i * 10,  # 渐变色调
                glow_intensity=0.8 - i * 0.1,
                opacity=1.0 - i * 0.1,
            )
            segments.append(segment)
        
        with self._lock:
            self.worm_chains[chain_id] = segments
        
        return segments
    
    def update_worm_chain(self, chain_id: str, 
                         head_position: Tuple[float, float],
                         dt: float = 0.016):
        """
        更新虫链
        
        Args:
            chain_id: 链ID
            head_position: 头部目标位置
            dt: 时间步长
        """
        if chain_id not in self.worm_chains:
            return
        
        segments = self.worm_chains[chain_id]
        
        # 头部跟随目标
        segments[0].position = head_position
        
        # 链式跟随(弹簧连接)
        for i in range(1, len(segments)):
            prev = segments[i - 1]
            curr = segments[i]
            
            # 计算方向
            dx = prev.position[0] - curr.position[0]
            dy = prev.position[1] - curr.position[1]
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 0:
                # 归一化方向
                nx = dx / dist
                ny = dy / dist
                
                # 理想间距
                ideal_spacing = curr.radius * 2 + 5
                
                # 弹力
                if dist > ideal_spacing:
                    force = (dist - ideal_spacing) * 0.5
                    curr.velocity = (
                        curr.velocity[0] + nx * force * dt,
                        curr.velocity[1] + ny * force * dt
                    )
                
                # 阻尼
                damping_factor = 0.9
                curr.velocity = (
                    curr.velocity[0] * damping_factor,
                    curr.velocity[1] * damping_factor
                )
                
                # 更新位置
                curr.position = (
                    curr.position[0] + curr.velocity[0],
                    curr.position[1] + curr.velocity[1]
                )
                
                # 计算曲率
                if i > 0:
                    prev_dir = (prev.position[0] - segments[i-1].position[0],
                               prev.position[1] - segments[i-1].position[1])
                    curr_dir = (curr.position[0] - prev.position[0],
                               curr.position[1] - prev.position[1])
                    
                    cross = prev_dir[0] * curr_dir[1] - prev_dir[1] * curr_dir[0]
                    dot = prev_dir[0] * curr_dir[0] + prev_dir[1] * curr_dir[1]
                    
                    if dot != 0:
                        curr.curvature = abs(cross) / (dot + 0.001)
                    else:
                        curr.curvature = 0
    
    def get_worm_chain_data(self, chain_id: str) -> List[Dict]:
        """获取虫链数据"""
        if chain_id not in self.worm_chains:
            return []
        
        return [
            {
                "index": seg.index,
                "position": seg.position,
                "radius": seg.radius,
                "color_hue": seg.color_hue,
                "glow_intensity": seg.glow_intensity,
                "opacity": seg.opacity,
                "curvature": seg.curvature,
            }
            for seg in self.worm_chains[chain_id]
        ]
    
    # ==================== 动画任务管理 ====================
    
    def animate(self, 
               start_value: Any,
               end_value: Any,
               duration: float,
               easing: EasingFunction = EasingFunction.SPRING_SMOOTH,
               task_id: Optional[str] = None,
               on_complete: Optional[Callable] = None) -> str:
        """
        创建动画任务
        
        Args:
            start_value: 起始值
            end_value: 结束值
            duration: 持续时间(秒)
            easing: 缓动函数
            task_id: 任务ID
            on_complete: 完成回调
        """
        if task_id is None:
            task_id = f"task_{self._task_counter}"
            self._task_counter += 1
        
        task = AnimationTask(
            id=task_id,
            start_time=time.time(),
            duration=duration,
            start_value=start_value,
            end_value=end_value,
            easing=easing,
            on_complete=on_complete,
        )
        
        with self._lock:
            self.animation_tasks[task_id] = task
        
        return task_id
    
    def cancel_animation(self, task_id: str):
        """取消动画"""
        with self._lock:
            if task_id in self.animation_tasks:
                del self.animation_tasks[task_id]
    
    def get_animation_value(self, task_id: str) -> Optional[Any]:
        """获取动画当前值"""
        if task_id in self.animation_tasks:
            task = self.animation_tasks[task_id]
            return task.current_value
        return None
    
    def is_animation_complete(self, task_id: str) -> bool:
        """检查动画是否完成"""
        if task_id in self.animation_tasks:
            return self.animation_tasks[task_id].is_complete
        return True
    
    # ==================== 更新循环 ====================
    
    def update(self, dt: Optional[float] = None):
        """
        更新引擎
        
        Args:
            dt: 时间步长(秒)
        """
        current_time = time.time()
        
        if dt is None:
            dt = current_time - self._last_update
        
        dt = min(dt, 0.1)  # 限制最大dt
        dt *= self.global_speed
        
        with self._lock:
            # 更新弹簧
            self._update_springs(dt)
            
            # 更新动画任务
            self._update_animations(current_time)
            
            # 更新能量统计
            self._update_energy_stats()
        
        # 触发更新回调
        if self.on_update:
            self.on_update(self)
        
        self._last_update = current_time
    
    def _update_springs(self, dt: float):
        """更新所有弹簧"""
        for spring in self.springs.values():
            spring.update(dt)
    
    def _update_animations(self, current_time: float):
        """更新所有动画任务"""
        completed = []
        
        for task in self.animation_tasks.values():
            task.update(current_time)
            
            if task.is_complete:
                completed.append(task.id)
        
        # 清理完成的动画
        for task_id in completed:
            del self.animation_tasks[task_id]
    
    def _update_energy_stats(self):
        """更新能量统计"""
        total_kinetic = 0.0
        total_potential = 0.0
        max_vel = 0.0
        
        for spring in self.springs.values():
            total_kinetic += spring.kinetic_energy
            total_potential += spring.potential_energy
            max_vel = max(max_vel, abs(spring.velocity))
        
        self.energy_stats = {
            "total_kinetic": total_kinetic,
            "total_potential": total_potential,
            "max_velocity": max_vel,
        }
    
    # ==================== 预设动画 ====================
    
    def animate_fade_in(self, element_id: str, duration: float = 0.3) -> str:
        """淡入动画"""
        return self.animate(0.0, 1.0, duration, 
                           EasingFunction.EASE_OUT,
                           f"fade_in_{element_id}")
    
    def animate_fade_out(self, element_id: str, duration: float = 0.3) -> str:
        """淡出动画"""
        return self.animate(1.0, 0.0, duration,
                           EasingFunction.EASE_IN,
                           f"fade_out_{element_id}")
    
    def animate_slide_in(self, 
                        element_id: str,
                        start_offset: float,
                        end_offset: float = 0.0,
                        duration: float = 0.5) -> str:
        """滑入动画"""
        return self.animate(start_offset, end_offset, duration,
                           EasingFunction.SPRING_BOUNCY,
                           f"slide_{element_id}")
    
    def animate_scale(self,
                     element_id: str,
                     start_scale: float,
                     end_scale: float,
                     duration: float = 0.4) -> str:
        """缩放动画"""
        return self.animate(start_scale, end_scale, duration,
                           EasingFunction.ELASTIC_OUT,
                           f"scale_{element_id}")
    
    def animate_color_shift(self,
                           element_id: str,
                           start_hue: float,
                           end_hue: float,
                           duration: float = 0.6) -> str:
        """颜色渐变动画"""
        return self.animate(start_hue, end_hue, duration,
                           EasingFunction.EASE_IN_OUT,
                           f"color_{element_id}")
    
    def animate_pulse(self,
                     element_id: str,
                     base_value: float,
                     amplitude: float,
                     duration: float = 1.0) -> str:
        """脉冲动画"""
        return self.animate(
            base_value, 
            base_value + amplitude, 
            duration / 2,
            EasingFunction.SINE
        ) if False else None  # 占位
    
    def animate_path_follow(self,
                           element_id: str,
                           path_points: List[Tuple[float, float]],
                           duration: float) -> str:
        """
        路径跟随动画
        
        Args:
            element_id: 元素ID
            path_points: 路径点列表
            duration: 持续时间
        """
        task_id = f"path_{element_id}"
        
        task = AnimationTask(
            id=task_id,
            start_time=time.time(),
            duration=duration,
            start_value=0,
            end_value=len(path_points) - 1,
            easing=EasingFunction.LINEAR,
        )
        
        with self._lock:
            self.animation_tasks[task_id] = task
        
        return task_id
    
    # ==================== 实用函数 ====================
    
    def get_all_spring_values(self) -> Dict[str, float]:
        """获取所有弹簧当前值"""
        return {
            spring_id: spring.position 
            for spring_id, spring in self.springs.items()
        }
    
    def get_all_animation_values(self) -> Dict[str, Any]:
        """获取所有动画当前值"""
        return {
            task_id: task.current_value 
            for task_id, task in self.animation_tasks.items()
        }
    
    def get_engine_state(self) -> Dict[str, Any]:
        """获取引擎状态"""
        return {
            "springs": {
                sid: {
                    "position": s.position,
                    "velocity": s.velocity,
                    "target": s.target,
                    "is_settled": s.is_settled,
                }
                for sid, s in self.springs.items()
            },
            "animations": {
                tid: {
                    "progress": t.progress,
                    "is_complete": t.is_complete,
                    "current_value": t.current_value,
                }
                for tid, t in self.animation_tasks.items()
            },
            "worm_chains": {
                cid: self.get_worm_chain_data(cid)
                for cid in self.worm_chains.keys()
            },
            "energy": self.energy_stats,
            "is_running": self._running,
        }
    
    def clear_all(self):
        """清除所有状态"""
        with self._lock:
            self.springs.clear()
            self.worm_chains.clear()
            self.animation_tasks.clear()
            self.energy_stats = {
                "total_kinetic": 0.0,
                "total_potential": 0.0,
                "max_velocity": 0.0,
            }


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=== 弹簧虫动画引擎测试 ===\n")
    
    # 创建引擎
    engine = SpringWormEngine()
    
    # 测试弹簧系统
    print("1. 弹簧系统测试")
    spring = engine.create_spring("test_spring", stiffness=200, damping=15)
    print(f"   创建弹簧: 刚度={spring.stiffness}, 阻尼={spring.damping}")
    
    # 施加冲量
    engine.set_spring_target("test_spring", 100, impulse=50)
    
    # 模拟更新
    print("   模拟弹簧振荡...")
    for i in range(20):
        engine.update(0.05)
        state = engine.get_spring_value("test_spring")
        print(f"   t={i*50:3d}ms: pos={state:7.3f}, settled={spring.is_settled}")
        if spring.is_settled:
            break
    
    print()
    
    # 测试虫链
    print("2. 虫链系统测试")
    chain = engine.create_worm_chain("test_worm", segment_count=8, spacing=25)
    print(f"   创建虫链: {len(chain)}段")
    
    # 移动虫链头部
    import random
    positions = [(200 + i * 10, 100 + math.sin(i * 0.5) * 50) for i in range(10)]
    
    for i, pos in enumerate(positions):
        engine.update_worm_chain("test_worm", pos)
        if i < 3 or i == len(positions) - 1:
            data = engine.get_worm_chain_data("test_worm")
            head = data[0]
            tail = data[-1]
            print(f"   Step {i}: head=({head['position'][0]:.1f}, {head['position'][1]:.1f}), "
                  f"tail=({tail['position'][0]:.1f}, {tail['position'][1]:.1f})")
    
    print()
    
    # 测试动画任务
    print("3. 动画任务测试")
    
    # 淡入动画
    fade_id = engine.animate_fade_in("element1")
    print(f"   创建淡入动画: {fade_id}")
    
    # 滑入动画
    slide_id = engine.animate_slide_in("element2", -200, 0)
    print(f"   创建滑入动画: {slide_id}")
    
    # 缩放动画
    scale_id = engine.animate_scale("element3", 0.5, 1.2)
    print(f"   创建缩放动画: {scale_id}")
    
    # 模拟动画过程
    print("   模拟动画过程...")
    for i in range(15):
        engine.update(0.05)
        
        fade_val = engine.get_animation_value(fade_id)
        slide_val = engine.get_animation_value(slide_id)
        scale_val = engine.get_animation_value(scale_id)
        
        if i < 5 or i == 14:
            print(f"   t={i*50:3d}ms: fade={fade_val:.3f if fade_val else 'N/A'}, "
                  f"slide={slide_val:.1f if slide_val else 'N/A'}, "
                  f"scale={scale_val:.3f if scale_val else 'N/A'}")
    
    print()
    
    # 引擎状态
    print("4. 引擎状态")
    state = engine.get_engine_state()
    print(f"   弹簧数量: {len(state['springs'])}")
    print(f"   动画数量: {len(state['animations'])}")
    print(f"   虫链数量: {len(state['worm_chains'])}")
    print(f"   总动能: {state['energy']['total_kinetic']:.4f}")
    print(f"   最大速度: {state['energy']['max_velocity']:.4f}")
    
    print("\n测试完成!")
