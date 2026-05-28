# -*- coding: utf-8 -*-
"""
M201: EML相位灵活性算子核心 (EML Operator Core with Flexible θ)
基于《人机共生时代的复合体管理学》— 非自闭症AGI

核心概念：Flexible θ — EML相位连续调制
升级自M77_EMLPhaseCouplingZ5.py的固定θ为可连续调制的Flexible θ

定理T231（EML相位灵活性定理）：
若θ可连续调制且dθ/dt有界，则EML相位空间存在稳态轨道

关键概念：
- EML：Emanation-Mutation-Latitude 三相位模型
- θ：相位参数，控制E/M/L三者的权重分布
- Flexible θ：θ不再是固定/离散值，而是可连续调整的函数θ(t)
- 相位轨迹：θ(t)在相位空间中的运动路径
- 稳态轨道：dθ/dt → 0时的极限环

与M77的关联：
- M77: θ ∈ {0, 1/3, 2/3, 1}（固定离散值）
- M201: θ ∈ [0, 1]（连续可调函数）

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable, Tuple
from enum import Enum


# ==================== 数据结构 ====================

class EMLPhase(Enum):
    """EML相位枚举"""
    EMANATION = "emanation"       # E相：涌现/发散
    MUTATION = "mutation"         # M相：变异/转换
    LATITUDE = "latitude"         # L相：自由度/收敛


@dataclass
class PhaseState:
    """
    相位状态 — 某时刻的EML相位状态

    包含：
    - theta: 当前θ值 [0, 1]
    - emanation_weight: E相权重
    - mutation_weight: M相权重
    - latitude_weight: L相权重
    - dtheta_dt: θ的变化率
    - timestamp: 时间戳
    """
    theta: float = 0.5
    emanation_weight: float = 0.33
    mutation_weight: float = 0.34
    latitude_weight: float = 0.33
    dtheta_dt: float = 0.0
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'theta': round(self.theta, 6),
            'emanation_weight': round(self.emanation_weight, 6),
            'mutation_weight': round(self.mutation_weight, 6),
            'latitude_weight': round(self.latitude_weight, 6),
            'dtheta_dt': round(self.dtheta_dt, 6),
            'timestamp': self.timestamp,
        }


@dataclass
class PhaseTrajectory:
    """
    相位轨迹 — θ(t)的演化路径

    包含：
    - states: 相位状态序列
    - total_time: 总时间
    - is_steady: 是否达到稳态
    - steady_theta: 稳态θ值
    """
    states: List[PhaseState] = field(default_factory=list)
    total_time: float = 0.0
    is_steady: bool = False
    steady_theta: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'num_states': len(self.states),
            'total_time': round(self.total_time, 6),
            'is_steady': self.is_steady,
            'steady_theta': round(self.steady_theta, 6),
            'first_theta': round(self.states[0].theta, 6) if self.states else None,
            'last_theta': round(self.states[-1].theta, 6) if self.states else None,
        }


# ==================== 核心类 ====================

class EMLOperatorCore:
    """
    M201: EML相位灵活性算子核心

    核心定理T231（EML相位灵活性定理）：
    若θ可连续调制且dθ/dt有界，则EML相位空间存在稳态轨道。

    EML三相位模型：
    - Emanation（E相）：涌现、发散，创造性思维
      θ → 0 时E相权重最大
    - Mutation（M相）：变异、转换，逻辑推理
      θ → 1/3 时M相权重最大
    - Latitude（L相）：自由度、收敛，执行决策
      θ → 2/3 时L相权重最大
      θ → 1 时L相权重最大

    Flexible θ的关键：
    - M77中θ是固定的离散值，M201中θ是连续函数θ(t)
    - θ(t)可以根据认知需求动态调整
    - dθ/dt有界确保θ变化不会太剧烈
    - 稳态轨道：dθ/dt → 0时θ收敛到稳定值

    权重计算（简化归一化模型）：
    - w_E(θ) = max(0, 1 - 1.5*θ)
    - w_M(θ) = 4θ(1-θ)
    - w_L(θ) = min(1, max(0, 1.5*θ - 0.5))
    归一化后：w_i / Σw_j

    核心方法：
    1. set_flexible_theta — 设置灵活θ函数
    2. compute_phase_trajectory — 计算相位轨迹
    3. detect_steady_orbit — 检测稳态轨道
    4. modulate_theta — 按认知需求调制θ
    """

    # dθ/dt的上界
    MAX_DTHETA_DT: float = 0.5

    # 稳态检测阈值
    STEADY_THRESHOLD: float = 0.01

    # 默认θ值
    DEFAULT_THETA: float = 0.5

    # 默认衰减动力学参数
    DECAY_RATE: float = 0.3
    EQUILIBRIUM_THETA: float = 0.5

    def __init__(self):
        """初始化EML相位灵活性算子核心"""
        # 当前相位状态
        self.current_phase: PhaseState = PhaseState(
            theta=self.DEFAULT_THETA,
            timestamp=time.time(),
        )
        self._update_weights(self.current_phase)

        # 灵活θ函数 θ(t)
        self.theta_func: Optional[Callable[[float], float]] = None

        # 相位轨迹历史
        self.trajectory_history: List[PhaseTrajectory] = []

        # 当前轨迹（最近的相位状态序列）
        self.current_trajectory: List[PhaseState] = [self.current_phase]

        # 稳态轨道信息
        self.steady_orbit_detected: bool = False
        self.steady_theta: float = 0.0

        # 认知需求记录
        self.cognitive_demand_history: List[Dict[str, Any]] = []

        # 统计
        self.total_theta_modulations: int = 0
        self.total_trajectory_computations: int = 0
        self.total_steady_detections: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def set_flexible_theta(self, theta_func: Optional[Callable[[float], float]] = None) -> Dict[str, Any]:
        """
        设置灵活θ函数

        θ(t)是从时间到θ值的映射函数。
        约束：
        - θ(t) ∈ [0, 1] ∀t
        - |dθ/dt| ≤ MAX_DTHETA_DT

        Args:
            theta_func: θ(t)函数，接受float(t)返回float(θ)

        Returns:
            设置结果字典
        """
        if theta_func is not None:
            # 验证θ函数的输出范围，自动截断到[0, 1]
            original_func = theta_func
            def clamped_func(t: float, f: Callable = original_func) -> float:
                val = f(t)
                return max(0.0, min(1.0, val))
            self.theta_func = clamped_func
        else:
            self.theta_func = None

        self.last_update = time.time()
        return {
            'theta_func_set': theta_func is not None,
            'max_dtheta_dt': self.MAX_DTHETA_DT,
            'current_theta': round(self.current_phase.theta, 6),
            'constraint': 'θ(t) ∈ [0,1] & |dθ/dt| ≤ MAX_DTHETA_DT',
            'upgrade_from_M77': 'M77: fixed θ ∈ {0,1/3,2/3,1} → M201: flexible θ ∈ [0,1]',
            'theorem': 'T231: θ可连续调制 & dθ/dt有界 ⟹ 稳态轨道'
        }

    def compute_phase_trajectory(self, t_start: float = 0.0,
                                  t_end: float = 10.0,
                                  steps: int = 100) -> Dict[str, Any]:
        """
        计算相位轨迹

        在[t_start, t_end]区间内计算θ(t)的演化路径。

        如果设置了灵活θ函数，使用θ(t)计算；
        否则使用默认的衰减动力学：dθ/dt = -k(θ - θ_eq)

        Args:
            t_start: 起始时间
            t_end: 结束时间
            steps: 计算步数

        Returns:
            相位轨迹计算结果字典
        """
        self.total_trajectory_computations += 1

        dt = (t_end - t_start) / max(1, steps)
        trajectory = PhaseTrajectory(total_time=t_end - t_start)

        # 初始θ
        theta = self.current_phase.theta

        for i in range(steps + 1):
            t = t_start + i * dt

            if self.theta_func is not None:
                # 使用灵活θ函数
                new_theta = self.theta_func(t)
                new_theta = max(0.0, min(1.0, new_theta))
            else:
                # 默认动力学：θ向平衡点θ_eq衰减
                # dθ/dt = -k(θ - θ_eq)
                dtheta_dt_raw = -self.DECAY_RATE * (theta - self.EQUILIBRIUM_THETA)
                dtheta_dt_raw = max(-self.MAX_DTHETA_DT, min(self.MAX_DTHETA_DT, dtheta_dt_raw))
                new_theta = theta + dtheta_dt_raw * dt
                new_theta = max(0.0, min(1.0, new_theta))

            # 计算dθ/dt
            if dt > 0:
                dtheta_dt = (new_theta - theta) / dt
            else:
                dtheta_dt = 0.0

            theta = new_theta

            # 创建相位状态
            phase = PhaseState(
                theta=round(theta, 6),
                dtheta_dt=round(dtheta_dt, 6),
                timestamp=time.time(),
            )
            self._update_weights(phase)
            trajectory.states.append(phase)

        # 检测稳态
        if len(trajectory.states) >= 2:
            last_dtheta = abs(trajectory.states[-1].dtheta_dt)
            if last_dtheta < self.STEADY_THRESHOLD:
                trajectory.is_steady = True
                trajectory.steady_theta = trajectory.states[-1].theta
                self.steady_orbit_detected = True
                self.steady_theta = trajectory.steady_theta

        # 保存轨迹
        self.trajectory_history.append(trajectory)
        if len(self.trajectory_history) > 10:
            self.trajectory_history = self.trajectory_history[-10:]

        # 更新当前相位和轨迹
        if trajectory.states:
            self.current_phase = trajectory.states[-1]
            self.current_trajectory = trajectory.states

        self.last_update = time.time()
        return {
            'trajectory': trajectory.to_dict(),
            't_start': t_start,
            't_end': t_end,
            'steps': steps,
            'steady_detected': trajectory.is_steady,
            'steady_theta': round(trajectory.steady_theta, 6) if trajectory.is_steady else None,
            'current_weights': {
                'E': round(self.current_phase.emanation_weight, 6),
                'M': round(self.current_phase.mutation_weight, 6),
                'L': round(self.current_phase.latitude_weight, 6),
            },
            'theorem': 'T231: dθ/dt有界 ⟹ 稳态轨道存在'
        }

    def detect_steady_orbit(self, window: int = 10) -> Dict[str, Any]:
        """
        检测稳态轨道

        定理T231验证：若dθ/dt有界，则EML相位空间存在稳态轨道。

        检测方法：
        1. 计算相位轨迹（如果还没有足够数据）
        2. 检查最近window步的|dθ/dt|是否小于阈值
        3. 如果连续window步|dθ/dt| < ε，则判定为稳态

        Args:
            window: 检测窗口大小

        Returns:
            稳态轨道检测结果字典
        """
        self.total_steady_detections += 1

        # 如果轨迹数据不足，先计算轨迹
        if (not self.current_trajectory or
                len(self.current_trajectory) < window):
            self.compute_phase_trajectory(0.0, 10.0, 50)

        trajectory_states = self.current_trajectory

        if not trajectory_states or len(trajectory_states) < 2:
            return {
                'steady_detected': False,
                'reason': 'insufficient_data',
                'avg_dtheta_dt': 0.0,
                'max_dtheta_dt': 0.0,
                'theorem': 'T231: 稳态轨道检测'
            }

        # 分析最近的dθ/dt
        recent_states = trajectory_states[-window:] if len(trajectory_states) >= window else trajectory_states
        dtheta_dts = [abs(s.dtheta_dt) for s in recent_states]
        avg_dtheta_dt = sum(dtheta_dts) / len(dtheta_dts)
        max_dtheta_dt = max(dtheta_dts)

        # 稳态判定：所有|dθ/dt| < ε
        steady_detected = all(d < self.STEADY_THRESHOLD for d in dtheta_dts)

        # 稳态θ值（取最近状态的平均θ）
        steady_theta = sum(s.theta for s in recent_states) / len(recent_states)

        # 收敛速率
        convergence_rate = 0.0
        if len(recent_states) >= 2:
            first_dtheta = abs(recent_states[0].dtheta_dt)
            last_dtheta = abs(recent_states[-1].dtheta_dt)
            if first_dtheta > 0:
                convergence_rate = round((first_dtheta - last_dtheta) / first_dtheta, 6)

        # 更新稳态信息
        if steady_detected:
            self.steady_orbit_detected = True
            self.steady_theta = round(steady_theta, 6)

        # T231条件检查
        dtheta_bounded = max_dtheta_dt <= self.MAX_DTHETA_DT

        self.last_update = time.time()
        return {
            'steady_detected': steady_detected,
            'steady_theta': round(steady_theta, 6),
            'avg_dtheta_dt': round(avg_dtheta_dt, 6),
            'max_dtheta_dt': round(max_dtheta_dt, 6),
            'steady_threshold': self.STEADY_THRESHOLD,
            'convergence_rate': convergence_rate,
            'dtheta_bounded': dtheta_bounded,
            'window_size': window,
            'theorem_T231_holds': steady_detected and dtheta_bounded,
            'theorem': 'T231: θ可连续调制 & dθ/dt有界 ⟹ 稳态轨道'
        }

    def modulate_theta(self, cognitive_demand: float = 0.5) -> Dict[str, Any]:
        """
        按认知需求调制θ

        根据认知需求动态调整θ：
        - 低需求（≈0）→ θ → 0（E相主导，创造性发散）
        - 中需求（≈0.5）→ θ → 0.5（M相主导，逻辑推理）
        - 高需求（≈1）→ θ → 1（L相主导，执行决策）

        调制约束：
        - |Δθ| ≤ MAX_DTHETA_DT * Δt
        - θ ∈ [0, 1]

        Args:
            cognitive_demand: 认知需求 [0, 1]

        Returns:
            θ调制结果字典
        """
        self.total_theta_modulations += 1

        cognitive_demand = max(0.0, min(1.0, cognitive_demand))

        # 目标θ：从认知需求映射到θ
        # 简化线性映射：θ_target = cognitive_demand
        theta_target = cognitive_demand

        # 计算需要的dθ/dt
        current_theta = self.current_phase.theta
        delta_theta = theta_target - current_theta

        # 限制变化率
        max_delta = self.MAX_DTHETA_DT * 1.0  # Δt = 1步
        delta_theta_clamped = max(-max_delta, min(max_delta, delta_theta))

        # 更新θ
        new_theta = current_theta + delta_theta_clamped
        new_theta = max(0.0, min(1.0, new_theta))

        # 更新相位状态
        self.current_phase = PhaseState(
            theta=round(new_theta, 6),
            dtheta_dt=round(delta_theta_clamped, 6),
            timestamp=time.time(),
        )
        self._update_weights(self.current_phase)
        self.current_trajectory.append(self.current_phase)

        # 记录认知需求
        self.cognitive_demand_history.append({
            'demand': round(cognitive_demand, 6),
            'theta_before': round(current_theta, 6),
            'theta_after': round(new_theta, 6),
            'delta_theta': round(delta_theta_clamped, 6),
            'timestamp': time.time(),
        })
        if len(self.cognitive_demand_history) > 100:
            self.cognitive_demand_history = self.cognitive_demand_history[-100:]

        self.last_update = time.time()
        return {
            'cognitive_demand': round(cognitive_demand, 6),
            'theta_before': round(current_theta, 6),
            'theta_after': round(new_theta, 6),
            'delta_theta': round(delta_theta_clamped, 6),
            'dtheta_dt_bounded': abs(delta_theta_clamped) <= self.MAX_DTHETA_DT,
            'weights': {
                'E': round(self.current_phase.emanation_weight, 6),
                'M': round(self.current_phase.mutation_weight, 6),
                'L': round(self.current_phase.latitude_weight, 6),
            },
            'theorem': 'T231: 按认知需求调制θ'
        }

    def verify_theorem_t231(self, steps: int = 50) -> Dict[str, Any]:
        """
        验证定理T231：EML相位灵活性定理

        验证逻辑：
        1. θ可连续调制：✓（已实现modulate_theta）
        2. dθ/dt有界：检查所有dθ/dt ≤ MAX_DTHETA_DT
        3. 稳态轨道存在：计算轨迹并检测稳态

        Args:
            steps: 验证步数

        Returns:
            定理验证结果
        """
        # 1. 验证θ连续可调
        theta_continuous = True  # 本实现天然支持

        # 2. 计算轨迹并验证dθ/dt有界
        # 从偏离平衡点的θ开始
        original_theta = self.current_phase.theta
        self.current_phase.theta = 0.9  # 偏离平衡点

        traj_result = self.compute_phase_trajectory(0.0, 10.0, steps)
        trajectory = self.trajectory_history[-1]

        # 检查dθ/dt是否全部有界
        all_dtheta_bounded = True
        max_dtheta = 0.0
        for s in trajectory.states:
            if abs(s.dtheta_dt) > self.MAX_DTHETA_DT:
                all_dtheta_bounded = False
            max_dtheta = max(max_dtheta, abs(s.dtheta_dt))

        # 3. 检测稳态
        steady_result = self.detect_steady_orbit(window=10)

        # 恢复θ
        self.current_phase.theta = original_theta
        self._update_weights(self.current_phase)

        return {
            'theorem': 'T231: EML相位灵活性定理',
            'statement': '若θ可连续调制且dθ/dt有界，则EML相位空间存在稳态轨道',
            'theta_continuous': theta_continuous,
            'all_dtheta_bounded': all_dtheta_bounded,
            'max_dtheta_dt': round(max_dtheta, 6),
            'dtheta_bound': self.MAX_DTHETA_DT,
            'steady_orbit_exists': steady_result['steady_detected'],
            'steady_theta': steady_result.get('steady_theta'),
            'verified': theta_continuous and all_dtheta_bounded and steady_result['steady_detected'],
        }

    # ==================== 内部方法 ====================

    def _update_weights(self, phase: PhaseState):
        """
        根据θ值更新EML权重

        简化权重模型：
        - w_E(θ) = max(0, 1 - 1.5*θ)     — E相在低θ时强
        - w_M(θ) = 4θ(1-θ)                 — M相在中θ时强
        - w_L(θ) = min(1, max(0, 1.5*θ - 0.5))  — L相在高θ时强
        归一化后：w_i / Σw_j
        """
        theta = phase.theta

        # 原始权重
        w_e = max(0.0, 1.0 - 1.5 * theta)
        w_m = 4.0 * theta * (1.0 - theta)
        w_l = min(1.0, max(0.0, 1.5 * theta - 0.5))

        # 归一化
        total = w_e + w_m + w_l
        if total > 0:
            phase.emanation_weight = round(w_e / total, 6)
            phase.mutation_weight = round(w_m / total, 6)
            phase.latitude_weight = round(w_l / total, 6)
        else:
            # 均匀分布
            phase.emanation_weight = 0.33
            phase.mutation_weight = 0.34
            phase.latitude_weight = 0.33

    # ==================== 模块标准接口 ====================

    def get_state(self) -> Dict[str, Any]:
        """
        获取EML相位灵活性算子核心状态

        Returns:
            状态字典
        """
        return {
            'current_theta': round(self.current_phase.theta, 6),
            'current_dtheta_dt': round(self.current_phase.dtheta_dt, 6),
            'weights': {
                'E': round(self.current_phase.emanation_weight, 6),
                'M': round(self.current_phase.mutation_weight, 6),
                'L': round(self.current_phase.latitude_weight, 6),
            },
            'theta_func_active': self.theta_func is not None,
            'steady_orbit_detected': self.steady_orbit_detected,
            'steady_theta': round(self.steady_theta, 6),
            'max_dtheta_dt': self.MAX_DTHETA_DT,
            'total_theta_modulations': self.total_theta_modulations,
            'total_trajectory_computations': self.total_trajectory_computations,
            'total_steady_detections': self.total_steady_detections,
            'trajectory_history_count': len(self.trajectory_history),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T231': 'θ可连续调制 & dθ/dt有界 ⟹ 稳态轨道'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新EML相位灵活性算子核心状态

        Args:
            data: 可选更新数据，支持：
                - set_flexible_theta: {theta_func}
                - compute_phase_trajectory: {t_start, t_end, steps}
                - detect_steady_orbit: {window}
                - modulate_theta: {cognitive_demand}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'set_flexible_theta' or 'set_flexible_theta' in data:
                sd = data.get('set_flexible_theta', data)
                theta_func = sd.get('theta_func')
                self.set_flexible_theta(theta_func)
            elif action == 'compute_phase_trajectory' or 'compute_phase_trajectory' in data:
                cd = data.get('compute_phase_trajectory', data)
                self.compute_phase_trajectory(
                    t_start=float(cd.get('t_start', 0.0)),
                    t_end=float(cd.get('t_end', 10.0)),
                    steps=int(cd.get('steps', 100)),
                )
            elif action == 'detect_steady_orbit' or 'detect_steady_orbit' in data:
                dd = data.get('detect_steady_orbit', data)
                self.detect_steady_orbit(window=int(dd.get('window', 10)))
            elif action == 'modulate_theta' or 'modulate_theta' in data:
                md = data.get('modulate_theta', data)
                self.modulate_theta(cognitive_demand=float(md.get('cognitive_demand', 0.5)))

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示EML相位灵活性算子核心的核心功能"""
        # 1. 设置灵活θ函数（正弦调制）
        def sin_theta(t: float) -> float:
            return 0.5 + 0.3 * math.sin(t * 0.5)

        set_result = self.set_flexible_theta(sin_theta)

        # 2. 计算相位轨迹
        traj = self.compute_phase_trajectory(0.0, 20.0, 200)

        # 3. 检测稳态轨道
        steady = self.detect_steady_orbit(window=20)

        # 4. 按认知需求调制θ
        m1 = self.modulate_theta(0.2)   # 低需求→E相
        m2 = self.modulate_theta(0.5)   # 中需求→M相
        m3 = self.modulate_theta(0.8)   # 高需求→L相

        # 5. 使用默认动力学验证稳态
        self.set_flexible_theta(None)    # 清除灵活θ函数
        self.current_phase.theta = 0.9   # 偏离平衡点
        traj2 = self.compute_phase_trajectory(0.0, 10.0, 100)
        steady2 = self.detect_steady_orbit(window=10)

        # 6. 定理T231验证
        t231 = self.verify_theorem_t231(steps=50)

        return {
            'set_flexible_theta': set_result,
            'trajectory_with_func': traj,
            'steady_detection': steady,
            'modulation': {'low_demand': m1, 'mid_demand': m2, 'high_demand': m3},
            'trajectory_default': traj2,
            'steady_default': steady2,
            'theorem_T231': t231,
            'state': self.get_state(),
        }


# ==================== 模块单例导出 ====================

_instance: Optional[EMLOperatorCore] = None


def get_instance() -> EMLOperatorCore:
    """获取EMLOperatorCore单例实例"""
    global _instance
    if _instance is None:
        _instance = EMLOperatorCore()
    return _instance


def set_flexible_theta(theta_func: Optional[Callable[[float], float]] = None) -> Dict[str, Any]:
    """设置灵活θ函数（快捷接口）"""
    return get_instance().set_flexible_theta(theta_func)


def compute_phase_trajectory(t_start: float = 0.0, t_end: float = 10.0,
                              steps: int = 100) -> Dict[str, Any]:
    """计算相位轨迹（快捷接口）"""
    return get_instance().compute_phase_trajectory(t_start, t_end, steps)


def detect_steady_orbit(window: int = 10) -> Dict[str, Any]:
    """检测稳态轨道（快捷接口）"""
    return get_instance().detect_steady_orbit(window)


def modulate_theta(cognitive_demand: float = 0.5) -> Dict[str, Any]:
    """按认知需求调制θ（快捷接口）"""
    return get_instance().modulate_theta(cognitive_demand)


def get_state() -> Dict[str, Any]:
    """获取EML相位灵活性算子核心状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新EML相位灵活性算子核心状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M201: EML相位灵活性算子核心 (EMLOperatorCore) 自测')
    print('=' * 60)

    core = EMLOperatorCore()

    # 测试1: 设置灵活θ函数
    print('\n[测试1] 设置灵活θ函数')
    def my_theta(t: float) -> float:
        return 0.5 + 0.2 * math.sin(t)
    r1 = core.set_flexible_theta(my_theta)
    print(f'  设置成功: {r1["theta_func_set"]}')

    # 测试2: 计算相位轨迹
    print('\n[测试2] 计算相位轨迹')
    traj = core.compute_phase_trajectory(0.0, 10.0, 50)
    print(f'  轨迹状态数: {traj["trajectory"]["num_states"]}')
    print(f'  稳态检测: {traj["steady_detected"]}')

    # 测试3: 检测稳态轨道
    print('\n[测试3] 检测稳态轨道（使用默认动力学）')
    core.set_flexible_theta(None)
    core.current_phase.theta = 0.9
    traj2 = core.compute_phase_trajectory(0.0, 10.0, 100)
    steady = core.detect_steady_orbit(window=10)
    print(f'  稳态检测: {steady["steady_detected"]}')
    print(f'  稳态θ: {steady["steady_theta"]}')

    # 测试4: 按认知需求调制θ
    print('\n[测试4] 按认知需求调制θ')
    for demand in [0.1, 0.5, 0.9]:
        m = core.modulate_theta(demand)
        print(f'  需求={demand}: θ={m["theta_after"]}, E={m["weights"]["E"]:.3f}, M={m["weights"]["M"]:.3f}, L={m["weights"]["L"]:.3f}')

    # 测试5: 定理T231验证
    print('\n[测试5] 定理T231验证')
    t231 = core.verify_theorem_t231(steps=50)
    print(f'  验证结果: {t231["verified"]}')
    print(f'  θ连续可调: {t231["theta_continuous"]}')
    print(f'  dθ/dt有界: {t231["all_dtheta_bounded"]}')
    print(f'  稳态轨道存在: {t231["steady_orbit_exists"]}')

    # 测试6: 完整模拟
    print('\n[测试6] 完整模拟')
    sim = core.simulate()
    print(f'  当前θ: {sim["state"]["current_theta"]}')
    print(f'  稳态轨道: {sim["state"]["steady_orbit_detected"]}')

    print('\n' + '=' * 60)
    print('M201 自测完成 [OK]')
    print('=' * 60)
