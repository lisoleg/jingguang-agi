# -*- coding: utf-8 -*-
"""
M118: 认知递归动力学 (Cognitive Recursive Dynamics)
基于《人机共生时代的复合体管理学》

核心概念：C_{t+1} = R(C_t, O_t, A_t, F_t) — 认知状态的递归追踪演化

单环学习 vs 双环学习：
- 单环学习：调整行为以减小误差（不改变目标）
- 双环学习：调整目标+行为（质疑目标本身）

结构滞后不稳定性：
技术进步超前认知演化→误差单调增加→解释AI幻觉为层间保真度崩溃

定理T76（结构滞后不稳定性定理）：
若认知更新率ρ < 技术变化率τ的持续时长 > T_crit，则误差单调增加

v7.31升级：双轨CRD
- 新增 dual_track_step：同时维护人轨和机轨
- 新增 compute_dual_convergence：检测双轨是否收敛
- 新增 verify_dual_convergence：定理验证函数
- 新增 _human_track_state / _agent_track_state 属性
- simulate() 加入双轨模式选项
- 保留原有 step / record_state 等方法不变

作者: 太乙AGI团队
日期: 2026-05-20
升级: v7.31 — 寇豆码
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


# ==================== 数据结构 ====================

class LearningMode(Enum):
    """学习模式枚举"""
    SINGLE_LOOP = "single_loop"     # 单环学习：调整行为
    DOUBLE_LOOP = "double_loop"     # 双环学习：调整目标+行为
    UNKNOWN = "unknown"             # 未知模式


@dataclass
class CognitiveState:
    """
    认知状态 — 递归动力学中的单步状态

    C_{t+1} = R(C_t, O_t, A_t, F_t)
    其中：
    - level: 认知层级（0=感知, 1=理解, 2=分析, 3=评估, 4=创造）
    - observation: 观察O_t（对外部世界的感知）
    - action: 行动A_t（基于认知的决策和行动）
    - ftel_influence: Ftel影响F_t（目的约束对认知的调制）
    - timestamp: 时间戳
    """
    level: int = 0                              # 认知层级 [0-4]
    observation: str = ''                       # 观察O_t
    action: str = ''                            # 行动A_t
    ftel_influence: float = 0.0                 # Ftel影响F_t
    timestamp: float = 0.0                      # 时间戳

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['ftel_influence'] = round(self.ftel_influence, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CognitiveState':
        """从字典构建CognitiveState"""
        return cls(**d)


@dataclass
class DualTrackState:
    """
    双轨认知状态 — v7.31 新增

    同时维护人轨（human_track）和机轨（agent_track）的认知状态。
    双轨CRD核心思想：人类和智能体各自维护独立的认知递归轨迹，
    通过 compute_dual_convergence 检测双轨是否收敛到共识。
    """
    human_state: CognitiveState      # 人轨状态
    agent_state: CognitiveState      # 机轨状态
    env_event: str = ''              # 环境事件
    convergence_score: float = 0.0   # 双轨收敛评分 [0, 1]
    timestamp: float = 0.0           # 时间戳

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'human_state': self.human_state.to_dict(),
            'agent_state': self.agent_state.to_dict(),
            'env_event': self.env_event,
            'convergence_score': round(self.convergence_score, 6),
            'timestamp': self.timestamp,
        }


# ==================== 核心类 ====================

class CognitiveRecursiveDynamics:
    """
    M118: 认知递归动力学

    核心递归公式：C_{t+1} = R(C_t, O_t, A_t, F_t)
    认知状态在每一时刻通过递归函数R更新：
    - C_t: 当前认知状态
    - O_t: 观察输入
    - A_t: 行动输出
    - F_t: Ftel目的约束的影响

    学习模式：
    - 单环学习(SINGLE_LOOP)：发现误差→调整行为→减小误差
      不质疑目标本身，只在目标框架内优化
    - 双环学习(DOUBLE_LOOP)：发现误差→质疑目标→调整目标+行为
      深层反思，可能改变目标本身

    结构滞后不稳定性：
    当技术变化率τ超过认知更新率ρ时，认知系统跟不上环境变化，
    导致误差单调增加。这解释了AI幻觉——层间保真度崩溃
    是结构滞后的一种表现。

    定理T76（结构滞后不稳定性定理）：
    若认知更新率ρ < 技术变化率τ的持续时长 > T_crit，
    则误差单调增加。

    核心方法：
    1. record_state — 记录认知状态
    2. detect_learning_mode — 检测当前学习模式（单环/双环）
    3. compute_structural_lag — 计算结构滞后 ρ vs τ
    4. predict_instability — 预测不稳定性

    v7.31 新增方法：
    5. dual_track_step — 双轨认知递推
    6. compute_dual_convergence — 检测双轨收敛
    7. verify_dual_convergence — 定理验证函数
    """

    # 认知层级定义
    LEVEL_NAMES = ['感知', '理解', '分析', '评估', '创造']

    # T76临界持续时间
    T_CRIT: float = 5.0

    def __init__(self):
        """初始化认知递归动力学"""
        # 认知状态历史
        self.state_history: List[CognitiveState] = []

        # 最大历史长度
        self.max_history: int = 100

        # 认知更新率ρ（认知系统自我更新的速率）
        self.rho: float = 0.5

        # 技术变化率τ（外部环境变化的速率）
        self.tau: float = 0.3

        # 当前学习模式
        self.current_learning_mode: LearningMode = LearningMode.UNKNOWN

        # 误差历史（用于检测学习模式和不稳定性）
        self.error_history: List[float] = []

        # 当前认知层级
        self.current_level: int = 0

        # 统计
        self.total_records: int = 0
        self.total_mode_detections: int = 0
        self.total_lag_computations: int = 0
        self.total_instability_predictions: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

        # ===== v7.31 新增属性 =====
        # 人轨状态（人类认知轨迹）
        self._human_track_state: Optional[CognitiveState] = None
        # 机轨状态（智能体认知轨迹）
        self._agent_track_state: Optional[CognitiveState] = None
        # 双轨历史
        self._dual_track_history: List[DualTrackState] = []
        # 双轨收敛阈值
        self._dual_convergence_threshold: float = 0.85

    # ==================== 原有方法（完全保留） ====================

    def record_state(self, level: int, observation: str = '',
                     action: str = '', ftel_influence: float = 0.0) -> CognitiveState:
        """
        记录认知状态

        将当前认知快照记录到历史中，实现递归追踪：
        C_{t+1} = R(C_t, O_t, A_t, F_t)

        Args:
            level: 认知层级 [0-4]
            observation: 观察O_t
            action: 行动A_t
            ftel_influence: Ftel影响F_t

        Returns:
            CognitiveState: 记录的认知状态
        """
        # 层级截断
        level = max(0, min(4, level))
        self.current_level = level

        # 创建认知状态
        state = CognitiveState(
            level=level,
            observation=observation,
            action=action,
            ftel_influence=round(ftel_influence, 6),
            timestamp=time.time()
        )

        # 添加到历史
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]

        # 更新认知更新率ρ：基于层级变化频率
        if len(self.state_history) >= 2:
            prev_level = self.state_history[-2].level
            if prev_level != level:
                # 层级变化→认知更新
                self.rho = round(
                    self.rho * 0.8 + 0.2 * (1.0 / max(1, len(self.state_history) - 1)),
                    6
                )
            else:
                # 层级不变→认知停滞，ρ衰减
                self.rho = round(max(0.01, self.rho * 0.99), 6)

        # 计算当前误差（简化：基于Ftel影响与理想值的偏差）
        error = abs(1.0 - ftel_influence) if ftel_influence > 0 else 0.5
        self.error_history.append(round(error, 6))
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]

        self.total_records += 1
        self.last_update = time.time()
        return state

    def detect_learning_mode(self) -> Dict[str, Any]:
        """
        检测当前学习模式（单环/双环）

        学习模式判定逻辑：
        - 单环学习：误差减小但目标不变（level稳定，error下降）
        - 双环学习：目标调整+行为改变（level变化，error可能先增后减）
        - 未知：历史数据不足

        Args:
            无参数

        Returns:
            学习模式检测结果字典
        """
        self.total_mode_detections += 1

        if len(self.state_history) < 3:
            self.current_learning_mode = LearningMode.UNKNOWN
            return {
                'mode': LearningMode.UNKNOWN.value,
                'confidence': 0.0,
                'reason': 'insufficient_history',
                'level_stability': 0.0,
                'error_trend': 0.0,
                'theorem': 'T76: 结构滞后不稳定性定理'
            }

        # 分析层级稳定性
        recent_levels = [s.level for s in self.state_history[-5:]]
        level_variance = round(
            sum((l - sum(recent_levels) / len(recent_levels)) ** 2
                for l in recent_levels) / len(recent_levels), 6
        )
        level_stability = round(1.0 - min(1.0, level_variance / 4.0), 6)

        # 分析误差趋势
        recent_errors = self.error_history[-5:] if len(self.error_history) >= 5 else self.error_history
        if len(recent_errors) >= 2:
            error_trend = round(recent_errors[-1] - recent_errors[0], 6)
        else:
            error_trend = 0.0

        # 判定学习模式
        if level_stability > 0.7 and error_trend < 0:
            # 层级稳定且误差下降 → 单环学习
            mode = LearningMode.SINGLE_LOOP
            confidence = round(min(1.0, level_stability * abs(error_trend) * 2), 6)
            reason = 'level_stable_error_decreasing'
        elif level_stability < 0.5:
            # 层级不稳定 → 双环学习（质疑目标）
            mode = LearningMode.DOUBLE_LOOP
            confidence = round(min(1.0, (1.0 - level_stability) * 0.8), 6)
            reason = 'level_unstable_goal_reconsideration'
        elif error_trend > 0.1:
            # 误差增加 → 可能触发双环学习
            mode = LearningMode.DOUBLE_LOOP
            confidence = round(min(1.0, error_trend * 0.5), 6)
            reason = 'error_increasing_triggers_reflection'
        else:
            # 默认单环
            mode = LearningMode.SINGLE_LOOP
            confidence = 0.3
            reason = 'default_single_loop'

        self.current_learning_mode = mode
        self.last_update = time.time()

        return {
            'mode': mode.value,
            'confidence': round(confidence, 6),
            'reason': reason,
            'level_stability': level_stability,
            'error_trend': error_trend,
            'current_level': self.current_level,
            'level_name': self.LEVEL_NAMES[self.current_level] if self.current_level < len(self.LEVEL_NAMES) else 'unknown',
            'theorem': 'T76: 结构滞后不稳定性定理'
        }

    def compute_structural_lag(self) -> Dict[str, Any]:
        """
        计算结构滞后 ρ vs τ

        结构滞后 = 认知更新率ρ与技术变化率τ之间的差距。
        当ρ < τ时，认知系统落后于技术环境的变化。

        滞后量 = τ - ρ
        滞后比 = τ / ρ（>1表示滞后）

        定理T76：若ρ < τ持续时长 > T_crit，则误差单调增加。

        Returns:
            结构滞后计算结果字典
        """
        self.total_lag_computations += 1

        lag = round(self.tau - self.rho, 6)
        lag_ratio = round(self.tau / max(self.rho, 0.001), 6)

        # 判断是否处于结构滞后状态
        is_lagging = self.rho < self.tau

        # 估算滞后持续时间
        lag_duration = 0.0
        if is_lagging and len(self.state_history) >= 2:
            # 简化：从历史中估算ρ < τ的持续帧数
            lag_frames = 0
            for i in range(len(self.state_history) - 1, -1, -1):
                lag_frames += 1
                if lag_frames > self.max_history:
                    break
            lag_duration = round(min(lag_frames, self.max_history), 2)

        # T76判定
        exceeds_t_crit = lag_duration > self.T_CRIT
        instability_risk = is_lagging and exceeds_t_crit

        self.last_update = time.time()
        return {
            'rho': round(self.rho, 6),                # 认知更新率
            'tau': round(self.tau, 6),                 # 技术变化率
            'lag': lag,                                # 滞后量 τ - ρ
            'lag_ratio': lag_ratio,                    # 滞后比 τ / ρ
            'is_lagging': is_lagging,                   # 是否滞后
            'lag_duration': lag_duration,              # 滞后持续帧数
            'T_crit': self.T_CRIT,                     # 临界持续时间
            'exceeds_T_crit': exceeds_t_crit,          # 是否超过T_crit
            'instability_risk': instability_risk,       # 不稳定性风险
            'theorem': 'T76: ρ<τ持续T>T_crit ⟹ 误差单调增加'
        }

    def predict_instability(self, horizon: int = 10) -> Dict[str, Any]:
        """
        预测不稳定性

        基于当前结构滞后和误差趋势，预测未来horizon步内的不稳定性。

        预测方法：
        1. 当前结构滞后状态（ρ vs τ）
        2. 误差趋势（递增/递减/平稳）
        3. 学习模式（单环可能不足以应对变化）
        4. 综合不稳定性评分

        Args:
            horizon: 预测步数（默认10）

        Returns:
            不稳定性预测结果字典
        """
        self.total_instability_predictions += 1

        # 获取结构滞后数据
        lag_data = self.compute_structural_lag()

        # 获取学习模式
        mode_data = self.detect_learning_mode()

        # 误差趋势
        error_trend = 0.0
        if len(self.error_history) >= 2:
            recent = self.error_history[-min(5, len(self.error_history)):]
            error_trend = round(recent[-1] - recent[0], 6)

        # 综合不稳定性评分
        instability_score = 0.0

        # 因子1：结构滞后贡献
        if lag_data['is_lagging']:
            instability_score += min(0.4, lag_data['lag'] * 0.5)

        # 因子2：超过T_crit贡献
        if lag_data['exceeds_T_crit']:
            instability_score += 0.3

        # 因子3：误差递增贡献
        if error_trend > 0:
            instability_score += min(0.2, error_trend * 0.5)

        # 因子4：单环学习在滞后环境下风险更高
        if mode_data['mode'] == 'single_loop' and lag_data['is_lagging']:
            instability_score += 0.1

        instability_score = round(min(1.0, instability_score), 6)

        # 预测：如果不稳定性评分 > 0.5，预测误差将单调增加
        predicted_monotonic_error = instability_score > 0.5

        # 建议行动
        if predicted_monotonic_error:
            if mode_data['mode'] == 'single_loop':
                recommendation = '切换到双环学习：质疑当前目标，调整认知框架'
            else:
                recommendation = '加速认知更新：提升ρ以追赶技术变化率τ'
        else:
            recommendation = '当前稳定：维持单环学习即可'

        self.last_update = time.time()
        return {
            'horizon': horizon,
            'instability_score': instability_score,
            'predicted_monotonic_error': predicted_monotonic_error,
            'error_trend': error_trend,
            'structural_lag': lag_data['lag'],
            'learning_mode': mode_data['mode'],
            'recommendation': recommendation,
            'rho': round(self.rho, 6),
            'tau': round(self.tau, 6),
            'theorem': 'T76: 结构滞后不稳定性定理'
        }

    def get_state(self) -> Dict[str, Any]:
        """
        获取认知递归动力学状态

        Returns:
            状态字典，包含：
            - 认知层级、学习模式
            - 结构滞后数据
            - 历史统计
        """
        lag_data = self.compute_structural_lag()
        mode_data = self.detect_learning_mode()

        return {
            'current_level': self.current_level,
            'level_name': self.LEVEL_NAMES[self.current_level] if self.current_level < len(self.LEVEL_NAMES) else 'unknown',
            'learning_mode': self.current_learning_mode.value,
            'rho': round(self.rho, 6),
            'tau': round(self.tau, 6),
            'structural_lag': lag_data['lag'],
            'is_lagging': lag_data['is_lagging'],
            'lag_duration': lag_data['lag_duration'],
            'instability_risk': lag_data['instability_risk'],
            'history_size': len(self.state_history),
            'avg_error': round(
                sum(self.error_history) / max(1, len(self.error_history)), 6
            ) if self.error_history else 0.0,
            'total_records': self.total_records,
            'total_mode_detections': self.total_mode_detections,
            'total_lag_computations': self.total_lag_computations,
            'total_instability_predictions': self.total_instability_predictions,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T76': '结构滞后: ρ<τ持续T>T_crit ⟹ 误差单调增加'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新认知递归动力学状态

        Args:
            data: 可选更新数据，支持：
                - record: 记录认知状态 {level, observation, action, ftel_influence}
                - set_tau: 设置技术变化率 {tau}
                - predict: 预测不稳定性 {horizon}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'record' or 'record' in data:
                rec = data.get('record', data)
                self.record_state(
                    level=int(rec.get('level', 0)),
                    observation=rec.get('observation', ''),
                    action=rec.get('action', ''),
                    ftel_influence=float(rec.get('ftel_influence', 0.0))
                )
            elif action == 'set_tau' or 'set_tau' in data:
                st = data.get('set_tau', data)
                self.tau = round(max(0.01, float(st.get('tau', 0.3))), 6)
            elif action == 'predict' or 'predict' in data:
                prd = data.get('predict', data)
                self.predict_instability(horizon=int(prd.get('horizon', 10)))

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    # ==================== v7.31 新增方法 ====================

    def dual_track_step(self, human_action: str, agent_action: str,
                        env_event: str = '') -> DualTrackState:
        """
        双轨认知递推 — v7.31 新增

        同时维护人轨（human track）和机轨（agent track）的认知状态，
        分别进行递归更新 C_{t+1} = R(C_t, O_t, A_t, F_t)。

        人轨：人类观察环境后做出行动，递归更新人类认知状态
        机轨：智能体观察环境后做出行动，递归更新智能体认知状态

        Args:
            human_action: 人类的行动描述
            agent_action: 智能体的行动描述
            env_event: 环境事件（双轨共享的观察O_t）

        Returns:
            DualTrackState: 双轨认知状态，包含收敛评分
        """
        now = time.time()

        # 获取前一步状态（用于递归更新）
        if self._human_track_state is None:
            # 初始化人轨
            human_obs = f"[env] {env_event}" if env_event else "initial_observation"
            human_state = CognitiveState(
                level=0,
                observation=human_obs,
                action=human_action,
                ftel_influence=0.3,
                timestamp=now,
            )
        else:
            # 递归更新：C_{t+1} = R(C_t, O_t, A_t, F_t)
            prev = self._human_track_state
            # 人轨层级递推：基于前一步 + 行动复杂度
            action_complexity = min(1.0, len(human_action) / 20.0) if human_action else 0.1
            new_level = max(0, min(4, prev.level + int(action_complexity * 2)))
            human_obs = f"[env] {env_event}" if env_event else prev.observation
            ftel_h = round(prev.ftel_influence * 0.9 + action_complexity * 0.1, 6)
            human_state = CognitiveState(
                level=new_level,
                observation=human_obs,
                action=human_action,
                ftel_influence=ftel_h,
                timestamp=now,
            )

        if self._agent_track_state is None:
            # 初始化机轨
            agent_obs = f"[env] {env_event}" if env_event else "initial_observation"
            agent_state = CognitiveState(
                level=0,
                observation=agent_obs,
                action=agent_action,
                ftel_influence=0.3,
                timestamp=now,
            )
        else:
            # 递归更新
            prev = self._agent_track_state
            action_complexity = min(1.0, len(agent_action) / 20.0) if agent_action else 0.1
            new_level = max(0, min(4, prev.level + int(action_complexity * 2)))
            agent_obs = f"[env] {env_event}" if env_event else prev.observation
            ftel_a = round(prev.ftel_influence * 0.9 + action_complexity * 0.1, 6)
            agent_state = CognitiveState(
                level=new_level,
                observation=agent_obs,
                action=agent_action,
                ftel_influence=ftel_a,
                timestamp=now,
            )

        # 更新双轨状态
        self._human_track_state = human_state
        self._agent_track_state = agent_state

        # 计算双轨收敛评分
        convergence_score = self._compute_track_similarity(human_state, agent_state)

        # 构建双轨状态
        dual_state = DualTrackState(
            human_state=human_state,
            agent_state=agent_state,
            env_event=env_event,
            convergence_score=convergence_score,
            timestamp=now,
        )

        # 记录到双轨历史
        self._dual_track_history.append(dual_state)
        if len(self._dual_track_history) > self.max_history:
            self._dual_track_history = self._dual_track_history[-self.max_history:]

        self.last_update = time.time()
        return dual_state

    def _compute_track_similarity(self, state_a: CognitiveState,
                                   state_b: CognitiveState) -> float:
        """
        计算两个认知状态的相似度 — v7.31 新增

        使用层级对齐度和Ftel影响对齐度的加权平均作为收敛评分。

        Args:
            state_a: 认知状态A
            state_b: 认知状态B

        Returns:
            float: 收敛评分 [0, 1]
        """
        # 层级对齐度
        level_diff = abs(state_a.level - state_b.level)
        level_alignment = 1.0 - level_diff / 4.0  # 归一化到[0,1]

        # Ftel影响对齐度
        ftel_diff = abs(state_a.ftel_influence - state_b.ftel_influence)
        ftel_alignment = 1.0 - min(1.0, ftel_diff)

        # 加权平均
        convergence = 0.6 * level_alignment + 0.4 * ftel_alignment
        return round(max(0.0, min(1.0, convergence)), 6)

    def compute_dual_convergence(self) -> Dict[str, Any]:
        """
        检测双轨是否收敛 — v7.31 新增

        基于双轨历史数据，计算人轨和机轨的收敛趋势：
        - 如果收敛评分持续上升 → 双轨趋同（好）
        - 如果收敛评分持续下降 → 双轨发散（需干预）
        - 如果收敛评分波动 → 双轨不稳定

        Returns:
            双轨收敛分析结果字典
        """
        if not self._dual_track_history:
            return {
                'converged': False,
                'convergence_score': 0.0,
                'trend': 'no_data',
                'recommendation': '需要先调用 dual_track_step 建立双轨历史',
            }

        # 获取最近的收敛评分序列
        recent_scores = [ds.convergence_score for ds in self._dual_track_history]

        # 当前收敛评分
        current_score = recent_scores[-1]

        # 平均收敛评分
        avg_score = round(sum(recent_scores) / len(recent_scores), 6)

        # 收敛趋势分析
        if len(recent_scores) >= 3:
            # 使用最近3步的趋势
            recent_3 = recent_scores[-3:]
            if recent_3[-1] > recent_3[0]:
                trend = 'converging'
            elif recent_3[-1] < recent_3[0]:
                trend = 'diverging'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        # 收敛趋势斜率（线性回归）
        slope = 0.0
        if len(recent_scores) >= 2:
            n = len(recent_scores)
            x_mean = (n - 1) / 2.0
            y_mean = sum(recent_scores) / n
            numerator = sum((i - x_mean) * (s - y_mean) for i, s in enumerate(recent_scores))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            if abs(denominator) > 1e-10:
                slope = round(numerator / denominator, 6)

        # 是否收敛
        is_converged = current_score >= self._dual_convergence_threshold

        # 建议
        if is_converged:
            recommendation = '双轨已收敛：人轨和机轨达成认知共识'
        elif trend == 'converging':
            recommendation = '双轨趋同中：继续交互以深化共识'
        elif trend == 'diverging':
            recommendation = '双轨发散：建议增加沟通频率或调整交互策略'
        else:
            recommendation = '双轨状态不稳定：需要更多交互数据'

        # 双轨当前状态摘要
        human_summary = None
        agent_summary = None
        if self._human_track_state:
            human_summary = {
                'level': self._human_track_state.level,
                'level_name': self.LEVEL_NAMES[self._human_track_state.level] if self._human_track_state.level < len(self.LEVEL_NAMES) else 'unknown',
                'ftel_influence': self._human_track_state.ftel_influence,
                'action': self._human_track_state.action,
            }
        if self._agent_track_state:
            agent_summary = {
                'level': self._agent_track_state.level,
                'level_name': self.LEVEL_NAMES[self._agent_track_state.level] if self._agent_track_state.level < len(self.LEVEL_NAMES) else 'unknown',
                'ftel_influence': self._agent_track_state.ftel_influence,
                'action': self._agent_track_state.action,
            }

        self.last_update = time.time()
        return {
            'converged': is_converged,
            'convergence_score': current_score,
            'avg_convergence_score': avg_score,
            'trend': trend,
            'slope': slope,
            'threshold': self._dual_convergence_threshold,
            'dual_track_steps': len(self._dual_track_history),
            'human_track': human_summary,
            'agent_track': agent_summary,
            'recommendation': recommendation,
        }

    def verify_dual_convergence(self, n_steps: int = 20) -> Dict[str, Any]:
        """
        定理验证函数：验证双轨CRD收敛性 — v7.31 新增

        构造一个模拟场景：人轨和机轨从不同初始状态出发，
        通过协同交互逐步收敛。

        验证定理：若人轨和机轨共享足够的环境事件和协同行动，
        则双轨收敛评分应趋向1.0。

        Args:
            n_steps: 模拟步数

        Returns:
            验证结果字典
        """
        # 保存当前状态
        saved_human = self._human_track_state
        saved_agent = self._agent_track_state
        saved_history = self._dual_track_history.copy()

        # 重置双轨状态
        self._human_track_state = None
        self._agent_track_state = None
        self._dual_track_history = []

        # 模拟：人轨和机轨从不同起点出发，逐步对齐
        convergence_scores = []
        for i in range(n_steps):
            # 环境事件相同
            env = f"shared_event_{i}"

            # 人类和智能体行动逐渐对齐
            if i < n_steps // 3:
                # 初始阶段：行动差异大
                human_act = f"human_explores_option_{i % 3}"
                agent_act = f"agent_suggests_alternative_{i % 5}"
            elif i < 2 * n_steps // 3:
                # 中期：行动趋于一致
                human_act = f"collaborative_step_{i}"
                agent_act = f"collaborative_step_{i}_refined"
            else:
                # 后期：行动高度对齐
                human_act = f"aligned_action_{i}"
                agent_act = f"aligned_action_{i}"

            dual = self.dual_track_step(human_act, agent_act, env)
            convergence_scores.append(dual.convergence_score)

        # 分析收敛趋势
        first_third = convergence_scores[:n_steps // 3] if n_steps >= 3 else convergence_scores
        last_third = convergence_scores[2 * n_steps // 3:] if n_steps >= 3 else convergence_scores

        avg_first = round(sum(first_third) / max(1, len(first_third)), 6)
        avg_last = round(sum(last_third) / max(1, len(last_third)), 6)

        # 收敛判定
        final_score = convergence_scores[-1] if convergence_scores else 0.0
        is_converging = avg_last > avg_first
        is_converged = final_score >= self._dual_convergence_threshold

        # 恢复状态
        self._human_track_state = saved_human
        self._agent_track_state = saved_agent
        self._dual_track_history = saved_history

        return {
            'theorem': '双轨CRD收敛性定理',
            'verified': is_converging,
            'n_steps': n_steps,
            'convergence_scores': [round(s, 4) for s in convergence_scores],
            'avg_first_third': avg_first,
            'avg_last_third': avg_last,
            'final_score': round(final_score, 6),
            'is_converged': is_converged,
            'is_converging': is_converging,
            'statement': (
                '若人轨和机轨共享足够的环境事件和协同行动，'
                '则双轨收敛评分应趋向收敛阈值。'
            ),
        }

    def simulate(self, dual_track: bool = False) -> Dict[str, Any]:
        """
        模拟运行 — 演示认知递归动力学的核心功能

        Args:
            dual_track: 是否启用双轨模式（v7.31 新增参数，默认False保持向后兼容）

        Returns:
            模拟结果字典
        """
        # 1. 记录多个认知状态
        s1 = self.record_state(0, '用户提出问题', '开始分析', 0.3)
        s2 = self.record_state(1, '理解问题语义', '检索知识', 0.5)
        s3 = self.record_state(2, '分析问题结构', '构建推理链', 0.7)
        s4 = self.record_state(3, '评估推理质量', '校验答案', 0.8)
        s5 = self.record_state(4, '创造性地整合', '生成回答', 0.6)

        # 2. 检测学习模式
        mode = self.detect_learning_mode()

        # 3. 计算结构滞后
        lag = self.compute_structural_lag()

        # 4. 预测不稳定性
        pred = self.predict_instability(horizon=10)

        result = {
            'recorded_states': {
                's1': s1.to_dict(),
                's5': s5.to_dict(),
            },
            'learning_mode': mode,
            'structural_lag': lag,
            'instability_prediction': pred,
            'state': self.get_state()
        }

        # v7.31: 双轨模式
        if dual_track:
            # 运行双轨模拟
            dual_results = []
            scenarios = [
                ('人类观察数据', '智能体分析模式', '环境输入_感知'),
                ('人类理解意图', '智能体匹配语义', '环境输入_理解'),
                ('人类分析结构', '智能体构建推理', '环境输入_分析'),
                ('人类评估结果', '智能体验证一致性', '环境输入_评估'),
                ('人类创新整合', '智能体生成回答', '环境输入_创造'),
            ]
            for h_act, a_act, env in scenarios:
                dual = self.dual_track_step(h_act, a_act, env)
                dual_results.append(dual.to_dict())

            dual_conv = self.compute_dual_convergence()
            dual_verify = self.verify_dual_convergence(n_steps=10)

            result['dual_track'] = {
                'dual_steps': dual_results,
                'dual_convergence': dual_conv,
                'dual_convergence_verify': dual_verify,
            }

        return result


# ==================== 模块单例导出 ====================

_instance: Optional[CognitiveRecursiveDynamics] = None


def get_instance() -> CognitiveRecursiveDynamics:
    """
    获取CognitiveRecursiveDynamics单例实例

    Returns:
        CognitiveRecursiveDynamics全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = CognitiveRecursiveDynamics()
    return _instance


def record_state(level: int, observation: str = '',
                 action: str = '', ftel_influence: float = 0.0) -> CognitiveState:
    """记录认知状态（快捷接口）"""
    return get_instance().record_state(level, observation, action, ftel_influence)


def detect_learning_mode() -> Dict[str, Any]:
    """检测当前学习模式（快捷接口）"""
    return get_instance().detect_learning_mode()


def compute_structural_lag() -> Dict[str, Any]:
    """计算结构滞后 ρ vs τ（快捷接口）"""
    return get_instance().compute_structural_lag()


def predict_instability(horizon: int = 10) -> Dict[str, Any]:
    """预测不稳定性（快捷接口）"""
    return get_instance().predict_instability(horizon)


def get_state() -> Dict[str, Any]:
    """获取认知递归动力学状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新认知递归动力学状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== v7.31 自测代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("M118: CognitiveRecursiveDynamics 测试（含 v7.31 双轨升级）")
    print("=" * 60)

    crd = CognitiveRecursiveDynamics()

    # ---- 原有功能测试 ----
    print("\n[测试 1] 原有 record_state 功能")
    s = crd.record_state(2, '观察数据', '分析处理', 0.7)
    print(f"  记录状态: level={s.level}, ftel={s.ftel_influence}")

    print("\n[测试 2] 原有 detect_learning_mode 功能")
    mode = crd.detect_learning_mode()
    print(f"  学习模式: {mode['mode']}, 置信度: {mode['confidence']}")

    print("\n[测试 3] 原有 compute_structural_lag 功能")
    lag = crd.compute_structural_lag()
    print(f"  ρ={lag['rho']}, τ={lag['tau']}, 滞后={lag['lag']}")

    # ---- v7.31 新功能测试 ----
    print("\n" + "=" * 60)
    print("v7.31 双轨CRD 测试")
    print("=" * 60)

    crd_v731 = CognitiveRecursiveDynamics()

    print("\n[测试 4] dual_track_step — 双轨递推")
    for i in range(5):
        dual = crd_v731.dual_track_step(
            human_action=f"人类行动_{i}",
            agent_action=f"智能体行动_{i}",
            env_event=f"环境事件_{i}",
        )
        print(f"  步骤{i}: 收敛评分={dual.convergence_score:.4f}, "
              f"人轨level={dual.human_state.level}, 机轨level={dual.agent_state.level}")

    print("\n[测试 5] compute_dual_convergence — 双轨收敛检测")
    conv = crd_v731.compute_dual_convergence()
    print(f"  收敛状态: {conv['converged']}")
    print(f"  收敛评分: {conv['convergence_score']}")
    print(f"  趋势: {conv['trend']}")
    print(f"  建议: {conv['recommendation']}")

    print("\n[测试 6] verify_dual_convergence — 收敛性定理验证")
    verify = crd_v731.verify_dual_convergence(n_steps=15)
    print(f"  定理验证: {verify['verified']}")
    print(f"  最终评分: {verify['final_score']}")
    print(f"  前段均值: {verify['avg_first_third']}")
    print(f"  后段均值: {verify['avg_last_third']}")

    print("\n[测试 7] simulate(dual_track=True) — 双轨模拟模式")
    crd2 = CognitiveRecursiveDynamics()
    sim_result = crd2.simulate(dual_track=True)
    print(f"  双轨步数: {len(sim_result['dual_track']['dual_steps'])}")
    print(f"  双轨收敛: {sim_result['dual_track']['dual_convergence']['convergence_score']}")
    print(f"  收敛验证: {sim_result['dual_track']['dual_convergence_verify']['verified']}")

    print("\n" + "=" * 60)
    print("M118 v7.31 测试完成！")
    print("=" * 60)
