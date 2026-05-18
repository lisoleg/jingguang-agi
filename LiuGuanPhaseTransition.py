"""
流贯（△）相变监控模块 (LiuGuanPhaseTransition.py)
基于复合体理学的流贯动力学与相变分析

核心理论：
1. 流贯（△）：流的贯通性，系统各部分的连贯流动
2. 相变：系统从一种状态跃迁到另一种状态（如LTCM从稳定到崩盘）
3. 本体论陨落：系统失去其本体论基础（如LTCM的模型失效）

数学实现：
- 流贯度计算：△ = 信息贯通性 - 边界摩擦损耗
- 相变检测：监控 △ 值的突变
- 陨落预警：当 △ < 阈值时触发系统重构
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemState(Enum):
    """系统状态枚举"""
    STABLE = "稳定"              # △ > 阈值，系统稳定
    CRITICAL = "临界"             # △ ≈ 阈值，接近相变
    PHASE_TRANSITION = "相变"    # △ 突变，正在相变
    ONTOLOGICAL_FALL = "本体论陨落"  # △ < 阈值，系统崩盘


@dataclass
class LiuGuanMetrics:
    """流贯度指标数据结构"""
    delta: float                     # 流贯度 △
    information_connectivity: float   # 信息贯通性
    boundary_friction: float        # 边界摩擦损耗
    system_state: SystemState       # 系统状态
    timestamp: int                 # 时间戳
    metadata: Dict[str, Any] = field(default_factory=dict)


class LiuGuanCalculator:
    """
    流贯度（△）计算器
    
    实现流贯度的数学计算：
    △ = 信息贯通性 - 边界摩擦损耗
    
    理论背景：
    - 高 △：系统各部分连贯流动，如健康金融系统
    - 低 △：系统摩擦增大，接近相变（如LTCM崩盘前夕）
    - 负 △：系统本体论陨落，模型失效
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化流贯度计算器
        
        Args:
            config: 配置参数
                - connectivity_weight: 信息贯通性权重
                - friction_weight: 边界摩擦权重
                - critical_threshold: 临界阈值
                - fall_threshold: 陨落阈值
        """
        self.config = config
        self.connectivity_weight = config.get('connectivity_weight', 1.0)
        self.friction_weight = config.get('friction_weight', 1.0)
        self.critical_threshold = config.get('critical_threshold', 0.5)
        self.fall_threshold = config.get('fall_threshold', 0.2)
        
        # 历史记录（用于相变检测）
        self.history: List[LiuGuanMetrics] = []
        
        logger.info(f"LiuGuanCalculator initialized: critical={self.critical_threshold}, fall={self.fall_threshold}")
    
    def calculate_delta(self, system_state: np.ndarray, 
                       interaction_matrix: Optional[np.ndarray] = None) -> LiuGuanMetrics:
        """
        计算流贯度 △
        
        Args:
            system_state: 系统状态矩阵 (n_components, n_features)
            interaction_matrix: 组件间交互矩阵 (n_components, n_components)，可选
            
        Returns:
            LiuGuanMetrics: 流贯度指标
        """
        n = system_state.shape[0]
        
        # 1. 计算信息贯通性
        information_connectivity = self._calculate_information_connectivity(
            system_state, interaction_matrix
        )
        
        # 2. 计算边界摩擦损耗
        boundary_friction = self._calculate_boundary_friction(system_state)
        
        # 3. 计算流贯度 △
        delta = (self.connectivity_weight * information_connectivity - 
                self.friction_weight * boundary_friction)
        
        # 4. 判断系统状态
        system_state_enum = self._classify_system_state(delta)
        
        # 5. 创建指标对象
        metrics = LiuGuanMetrics(
            delta=delta,
            information_connectivity=information_connectivity,
            boundary_friction=boundary_friction,
            system_state=system_state_enum,
            timestamp=len(self.history),
            metadata={
                'n_components': n,
                'connectivity_weight': self.connectivity_weight,
                'friction_weight': self.friction_weight
            }
        )
        
        # 6. 记录历史
        self.history.append(metrics)
        
        logger.info(f"△ = {delta:.4f}, State: {system_state_enum.value}")
        
        return metrics
    
    def _calculate_information_connectivity(self, system_state: np.ndarray,
                                          interaction_matrix: Optional[np.ndarray]) -> float:
        """
        计算信息贯通性
        
        信息贯通性衡量系统各部分之间的信息流动效率。
        高贯通性 = 信息顺畅流动（如健康市场的价格发现）
        
        数学实现：
        - 如果有交互矩阵：使用图论的中心性度量
        - 如果只有状态矩阵：使用相关系数矩阵的特征值
        """
        n = system_state.shape[0]
        
        if interaction_matrix is not None:
            # 使用交互矩阵计算信息贯通性
            # 方法：计算图的平均路径长度和聚类系数
            assert interaction_matrix.shape == (n, n), "Interaction matrix must be n x n"
            
            # 简化：使用矩阵 Frobenius 范数作为贯通性度量
            connectivity = np.linalg.norm(interaction_matrix, 'fro') / (n ** 2)
            
        else:
            # 使用状态矩阵计算相关系数
            corr_matrix = np.corrcoef(system_state)
            
            # 贯通性 = 相关系数矩阵的平均绝对值（排除对角线）
            mask = ~np.eye(n, dtype=bool)
            connectivity = np.mean(np.abs(corr_matrix[mask]))
        
        # 归一化到 [0, 1]
        connectivity = min(max(connectivity, 0.0), 1.0)
        
        return connectivity
    
    def _calculate_boundary_friction(self, system_state: np.ndarray) -> float:
        """
        计算边界摩擦损耗
        
        边界摩擦损耗衡量系统各部分之间的"摩擦"或"阻力"。
        高摩擦 = 信息流动受阻（如市场恐慌时的流动性枯竭）
        
        数学实现：
        - 使用状态矩阵的梯度（相邻组件间的差异）
        - 梯度越大，摩擦越大
        """
        n, d = system_state.shape
        
        # 计算相邻组件间的差异（梯度）
        if n > 1:
            gradients = np.diff(system_state, axis=0)
            friction = np.mean(np.linalg.norm(gradients, axis=1))
        else:
            friction = 0.0
        
        # 归一化到 [0, 1]
        friction = min(friction, 1.0)
        
        return friction
    
    def _classify_system_state(self, delta: float) -> SystemState:
        """
        根据流贯度 △ 判断系统状态
        
        △ > critical_threshold: 稳定
        fall_threshold < △ ≤ critical_threshold: 临界
        △ ≤ fall_threshold: 本体论陨落
        相变检测：△ 的历史突变
        """
        # 1. 基础分类
        if delta > self.critical_threshold:
            state = SystemState.STABLE
        elif delta > self.fall_threshold:
            state = SystemState.CRITICAL
        else:
            state = SystemState.ONTOLOGICAL_FALL
        
        # 2. 相变检测（检查历史突变）
        if len(self.history) >= 2:
            prev_delta = self.history[-1].delta
            delta_change = abs(delta - prev_delta)
            
            # 如果 △ 突变超过阈值，标记为相变
            if delta_change > 0.3:  # 突变阈值
                state = SystemState.PHASE_TRANSITION
                logger.warning(f"Phase transition detected! △ changed by {delta_change:.4f}")
        
        return state


class PhaseTransitionDetector:
    """
    相变检测器
    
    检测系统是否正在经历相变（如LTCM从稳定到崩盘）
    实现基于流贯度 △ 的时间序列分析
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化相变检测器
        
        Args:
            config: 配置参数
                - detection_window: 检测窗口大小
                - mutation_threshold: 突变阈值
                - trend_threshold: 趋势阈值
        """
        self.config = config
        self.detection_window = config.get('detection_window', 10)
        self.mutation_threshold = config.get('mutation_threshold', 0.3)
        self.trend_threshold = config.get('trend_threshold', -0.1)
        
        logger.info(f"PhaseTransitionDetector initialized: window={self.detection_window}")
    
    def detect_phase_transition(self, liu_guan_history: List[LiuGuanMetrics]) -> Tuple[bool, str]:
        """
        检测相变
        
        Args:
            liu_guan_history: 流贯度历史记录
            
        Returns:
            Tuple[bool, str]: (是否发生相变, 相变类型描述)
        """
        if len(liu_guan_history) < self.detection_window:
            return False, "Insufficient data"
        
        # 获取最近窗口的数据
        recent = liu_guan_history[-self.detection_window:]
        deltas = [m.delta for m in recent]
        
        # 1. 检测突变（△ 的剧烈变化）
        delta_diff = np.diff(deltas)
        max_mutation = np.max(np.abs(delta_diff))
        
        if max_mutation > self.mutation_threshold:
            mutation_idx = np.argmax(np.abs(delta_diff))
            return True, f"突变型相变 at t={mutation_idx}, magnitude={max_mutation:.4f}"
        
        # 2. 检测趋势（△ 的持续下降）
        if len(deltas) >= 2:
            trend = np.polyfit(range(len(deltas)), deltas, 1)[0]
            
            if trend < self.trend_threshold:
                return True, f"趋势型相变, trend={trend:.4f} (持续下降)"
        
        # 3. 检测状态切换（稳定 → 临界 → 陨落）
        states = [m.system_state for m in recent]
        unique_states = set(states)
        
        if len(unique_states) >= 2 and SystemState.ONTOLOGICAL_FALL in unique_states:
            return True, f"状态切换型相变: {[s.value for s in states]}"
        
        return False, "No phase transition detected"
    
    def predict_ontological_fall(self, liu_guan_history: List[LiuGuanMetrics]) -> Tuple[float, str]:
        """
        预测本体论陨落（如LTCM崩盘）
        
        Args:
            liu_guan_history: 流贯度历史记录
            
        Returns:
            Tuple[float, str]: (陨落概率, 预测依据)
        """
        if len(liu_guan_history) < 5:
            return 0.0, "Insufficient data for prediction"
        
        # 获取最近的流贯度
        recent_deltas = [m.delta for m in liu_guan_history[-5:]]
        
        # 预测指标1：△ 的持续下降趋势
        trend = np.polyfit(range(len(recent_deltas)), recent_deltas, 1)[0]
        
        # 预测指标2：△ 的波动率
        volatility = np.std(recent_deltas)
        
        # 预测指标3：当前 △ 值
        current_delta = recent_deltas[-1]
        
        # 综合预测（简化逻辑）
        fall_probability = 0.0
        reasons = []
        
        if trend < -0.05:
            fall_probability += 0.4
            reasons.append(f"△ 下降趋势 (trend={trend:.4f})")
        
        if volatility > 0.2:
            fall_probability += 0.3
            reasons.append(f"△ 高波动 (volatility={volatility:.4f})")
        
        if current_delta < 0.4:
            fall_probability += 0.3
            reasons.append(f"△ 接近临界值 (current={current_delta:.4f})")
        
        fall_probability = min(fall_probability, 1.0)
        
        reason_str = "; ".join(reasons) if reasons else "System stable"
        
        return fall_probability, reason_str


class LiuGuanGovernance:
    """
    流贯治理模块
    
    基于流贯度 △ 的系统治理策略
    当检测到相变或本体论陨落风险时，触发治理干预
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化流贯治理模块
        
        Args:
            config: 配置参数
                - intervention_threshold: 干预阈值
                - governance_strategy: 治理策略 ('active', 'passive', 'adaptive')
        """
        self.config = config
        self.intervention_threshold = config.get('intervention_threshold', 0.6)
        self.governance_strategy = config.get('governance_strategy', 'adaptive')
        
        # 初始化子模块
        self.calculator = LiuGuanCalculator(config.get('calculator', {}))
        self.detector = PhaseTransitionDetector(config.get('detector', {}))
        
        # 治理记录
        self.governance_log = []
        
        logger.info(f"LiuGuanGovernance initialized: strategy={self.governance_strategy}")
    
    def evaluate_system(self, system_state: np.ndarray,
                      interaction_matrix: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        评估系统状态并决定是否干预
        
        Args:
            system_state: 系统状态矩阵
            interaction_matrix: 交互矩阵（可选）
            
        Returns:
            Dict: 评估结果和治理建议
        """
        # 1. 计算流贯度
        metrics = self.calculator.calculate_delta(system_state, interaction_matrix)
        
        # 2. 检测相变
        is_phase_transition, transition_desc = self.detector.detect_phase_transition(
            self.calculator.history
        )
        
        # 3. 预测本体论陨落
        fall_probability, fall_reason = self.detector.predict_ontological_fall(
            self.calculator.history
        )
        
        # 4. 决策：是否干预
        should_intervene = self._should_intervene(
            metrics, is_phase_transition, fall_probability
        )
        
        # 5. 生成治理建议
        governance_action = None
        if should_intervene:
            governance_action = self._generate_governance_action(
                metrics, is_phase_transition, fall_probability
            )
            
            # 记录治理日志
            self.governance_log.append({
                'timestamp': metrics.timestamp,
                'action': governance_action,
                'delta': metrics.delta,
                'fall_probability': fall_probability
            })
            
            logger.warning(f"Governance intervention triggered: {governance_action}")
        
        # 6. 返回评估结果
        return {
            'metrics': metrics,
            'is_phase_transition': is_phase_transition,
            'transition_description': transition_desc,
            'fall_probability': fall_probability,
            'fall_reason': fall_reason,
            'should_intervene': should_intervene,
            'governance_action': governance_action,
            'history_length': len(self.calculator.history)
        }
    
    def _should_intervene(self, metrics: LiuGuanMetrics, 
                          is_phase_transition: bool,
                          fall_probability: float) -> bool:
        """
        决策是否干预
        
        干预条件：
        1. △ < 干预阈值
        2. 检测到相变
        3. 本体论陨落概率 > 干预阈值
        """
        if metrics.delta < self.intervention_threshold:
            return True
        
        if is_phase_transition:
            return True
        
        if fall_probability > self.intervention_threshold:
            return True
        
        return False
    
    def _generate_governance_action(self, metrics: LiuGuanMetrics,
                                     is_phase_transition: bool,
                                     fall_probability: float) -> str:
        """
        生成治理动作
        
        根据系统状态和治理策略生成具体的干预动作
        """
        if self.governance_strategy == 'active':
            # 主动干预：无论风险大小都干预
            return self._active_governance(metrics)
        
        elif self.governance_strategy == 'passive':
            # 被动干预：只在确凿风险时干预
            return self._passive_governance(metrics, fall_probability)
        
        else:  # 'adaptive'
            # 自适应干预：根据相变检测结果动态调整
            return self._adaptive_governance(metrics, is_phase_transition)
    
    def _active_governance(self, metrics: LiuGuanMetrics) -> str:
        """主动治理：重构系统连接"""
        return "Active: Reconfigure system connectivity"
    
    def _passive_governance(self, metrics: LiuGuanMetrics, 
                             fall_probability: float) -> str:
        """被动治理：增加边界润滑"""
        if fall_probability > 0.8:
            return "Passive: Emergency liquidity injection (system rescue)"
        else:
            return "Passive: Increase boundary lubrication (reduce friction)"
    
    def _adaptive_governance(self, metrics: LiuGuanMetrics,
                              is_phase_transition: bool) -> str:
        """自适应治理：根据相变类型选择策略"""
        if metrics.system_state == SystemState.ONTOLOGICAL_FALL:
            return "Adaptive: System restart (ontological reconstruction)"
        
        elif is_phase_transition:
            return "Adaptive: Phase transition management (smooth transition)"
        
        else:
            return "Adaptive: Monitor and adjust parameters"


# 集成到全息离散治理（Holographic Discrete Governance）
class HolographicDiscreteGovernanceWithLiuGuan:
    """
    集成流贯治理的全息离散治理
    
    在原有 HolographicDiscreteGovernance 基础上，增加流贯（△）监控
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化集成模块"""
        self.config = config
        
        # 原有全息离散治理组件
        self.world_frames = {}
        self.governance_entropy = 0.0
        
        # 新增：流贯治理模块
        self.liu_guan_governance = LiuGuanGovernance(
            config.get('liu_guan', {})
        )
        
        logger.info("HolographicDiscreteGovernanceWithLiuGuan initialized")
    
    def process_world_frame(self, frame_id: str, 
                          frame_data: np.ndarray) -> Dict[str, Any]:
        """
        处理世界帧（集成流贯评估）
        
        Args:
            frame_id: 帧ID
            frame_data: 帧数据（系统状态矩阵）
            
        Returns:
            Dict: 处理结果
        """
        # 1. 存储世界帧
        self.world_frames[frame_id] = frame_data
        
        # 2. 评估流贯度（新增）
        liu_guan_result = self.liu_guan_governance.evaluate_system(frame_data)
        
        # 3. 原有全息离散治理逻辑（简化）
        governance_result = self._apply_holographic_governance(frame_id, frame_data)
        
        # 4. 集成结果
        integrated_result = {
            'frame_id': frame_id,
            'liu_guan': liu_guan_result,
            'holographic': governance_result,
            'integrated_action': self._integrate_actions(
                liu_guan_result, governance_result
            )
        }
        
        logger.info(f"Processed frame {frame_id}: △={liu_guan_result['metrics'].delta:.4f}")
        
        return integrated_result
    
    def _apply_holographic_governance(self, frame_id: str, 
                                       frame_data: np.ndarray) -> Dict[str, Any]:
        """应用原有全息离散治理逻辑（简化实现）"""
        # 这里简化为计算治理熵
        entropy = np.random.random()  # 模拟熵计算
        self.governance_entropy = entropy
        
        return {
            'entropy': entropy,
            'action': 'holographic_adjustment'
        }
    
    def _integrate_actions(self, liu_guan_result: Dict, 
                          holographic_result: Dict) -> str:
        """集成流贯治理与全息治理的动作"""
        if liu_guan_result['should_intervene']:
            return f"Integrated: {liu_guan_result['governance_action']} + {holographic_result['action']}"
        else:
            return "Integrated: Continue monitoring"


# 测试用例
if __name__ == "__main__":
    print("=== 流贯（△）相变监控模块测试 ===\n")
    
    # 1. 测试流贯度计算
    print("1. 测试流贯度计算:")
    calculator = LiuGuanCalculator({
        'critical_threshold': 0.5,
        'fall_threshold': 0.2
    })
    
    # 模拟系统状态（3个组件，每个有5个特征）
    test_state = np.array([
        [1.0, 0.8, 0.6, 0.4, 0.2],
        [0.9, 0.7, 0.5, 0.3, 0.1],
        [0.8, 0.6, 0.4, 0.2, 0.0]
    ])
    
    metrics = calculator.calculate_delta(test_state)
    print(f"   △ = {metrics.delta:.4f}")
    print(f"   信息贯通性 = {metrics.information_connectivity:.4f}")
    print(f"   边界摩擦 = {metrics.boundary_friction:.4f}")
    print(f"   系统状态 = {metrics.system_state.value}\n")
    
    # 2. 测试相变检测
    print("2. 测试相变检测:")
    detector = PhaseTransitionDetector({'detection_window': 5})
    
    # 模拟 △ 的下降（如LTCM崩盘前夕）
    for i in range(10):
        test_state = np.random.randn(3, 5) * (1.0 - i * 0.1)  # 逐渐降低信号强度
        m = calculator.calculate_delta(test_state)
        
        if i >= 5:
            is_transition, desc = detector.detect_phase_transition(calculator.history)
            if is_transition:
                print(f"   t={i}: 相变检测! {desc}")
    
    # 3. 测试流贯治理
    print("\n3. 测试流贯治理:")
    governance = LiuGuanGovernance({
        'intervention_threshold': 0.6,
        'governance_strategy': 'adaptive'
    })
    
    # 模拟系统评估
    for i in range(5):
        test_state = np.random.randn(3, 5)
        result = governance.evaluate_system(test_state)
        
        print(f"   评估 {i+1}: △={result['metrics'].delta:.4f}, "
              f"干预={result['should_intervene']}, "
              f"动作={result['governance_action']}")
    
    # 4. 测试集成模块
    print("\n4. 测试集成模块 (Holographic + LiuGuan):")
    integrated = HolographicDiscreteGovernanceWithLiuGuan({})
    
    for i in range(3):
        frame_id = f"frame_{i}"
        frame_data = np.random.randn(3, 5)
        result = integrated.process_world_frame(frame_id, frame_data)
        
        print(f"   帧 {frame_id}: {result['integrated_action']}")
    
    print("\n=== 测试完成 ===")
