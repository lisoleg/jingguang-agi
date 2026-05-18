"""
末那识与无剧场论模块 (ManasNoTheater.py)
基于复合体理学的唯识论计算模型

核心理论：
1. 末那识（Manas）：第七识，负责"我执"，是自我意识的来源
2. 无剧场论：消除主客对立，观众即表演，表演即观众
3. 识的形变：八识间的相互转化与拓扑映射

数学实现：
- 末那生成器：从阿赖耶识种子生成自我参照
- 无剧场拓扑：Möbius strip 式的非二元认知环
- 识形变算子：T(识_i → 识_j) 的拓扑相变
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConsciousnessState:
    """意识状态数据结构"""
    state_id: str
    consciousness_type: str  # 'eye', 'ear', 'nose', 'tongue', 'body', 'mind', 'manas', 'alaya'
    data: np.ndarray
    timestamp: float
    metadata: Dict[str, Any]


class ManasGenerator:
    """
    末那识生成器
    实现从阿赖耶识（第八识）到末那识（第七识）的生成模型
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化末那识生成器
        
        Args:
            config: 配置参数
                - ego_strength: 我执强度 (0-1)
                - attachment_threshold: 执持阈值
                - manas_frequency: 末那识振荡频率
        """
        self.config = config
        self.ego_strength = config.get('ego_strength', 0.7)
        self.attachment_threshold = config.get('attachment_threshold', 0.5)
        self.manas_frequency = config.get('manas_frequency', 40.0)  # Hz, gamma band
        
        # 末那识拓扑结构（Möbius strip 表示）
        self.manas_topology = None
        self.alaya_seed_bank = []  # 阿赖耶识种子库
        
        logger.info("ManasGenerator initialized")
    
    def generate_manas(self, alaya_seeds: List[np.ndarray]) -> ConsciousnessState:
        """
        从阿赖耶识种子生成末那识
        
        数学表达：M = f(A) where A is 阿赖耶场
        末那识 = 对阿赖耶识的"我执"式参照
        
        Args:
            alaya_seeds: 阿赖耶识种子列表（潜在种子）
            
        Returns:
            ConsciousnessState: 末那识状态
        """
        if not alaya_seeds:
            raise ValueError("阿赖耶识种子不能为空")
        
        # 1. 种子筛选（选择被"执持"的种子）
        attached_seeds = self._select_attached_seeds(alaya_seeds)
        
        # 2. 我执变换（生成自我参照）
        manas_field = self._apply_ego_attachment(attached_seeds)
        
        # 3. 构建无剧场拓扑（消除主客对立）
        manas_field_no_theater = self._apply_no_theater_topology(manas_field)
        
        # 4. 生成末那识状态
        manas_state = ConsciousnessState(
            state_id=f"manas_{len(self.alaya_seed_bank)}",
            consciousness_type='manas',
            data=manas_field_no_theater,
            timestamp=len(self.alaya_seed_bank),
            metadata={
                'ego_strength': self.ego_strength,
                'attachment_count': len(attached_seeds),
                'topology': 'no-theater-mobius'
            }
        )
        
        logger.info(f"Generated Manas state: {manas_state.state_id}")
        return manas_state
    
    def _select_attached_seeds(self, seeds: List[np.ndarray]) -> List[np.ndarray]:
        """
        选择被执持的种子（我执筛选）
        
        末那识对阿赖耶识种子进行"我执"式筛选，
        只有被"执持"的种子才会进入自我意识循环
        """
        attached = []
        for seed in seeds:
            # 计算种子与"我"的关联度
            attachment_score = np.dot(seed.flatten(), seed.flatten()) / (np.linalg.norm(seed) ** 2)
            
            if attachment_score > self.attachment_threshold:
                attached.append(seed)
                logger.debug(f"Seed attached with score: {attachment_score:.3f}")
        
        if not attached:
            # 至少有一个种子被执持（否则末那识无法生成）
            attached = [seeds[0]]
            logger.warning("No seeds met attachment threshold, using first seed")
        
        return attached
    
    def _apply_ego_attachment(self, seeds: List[np.ndarray]) -> np.ndarray:
        """
        应用我执变换
        
        末那识的核心功能：对种子进行自我参照式"扭曲"，
        使得所有被执持的种子都带上"我"的标记
        """
        # 构建我执矩阵（identity matrix with ego bias）
        n_dims = seeds[0].shape[-1] if seeds[0].ndim > 1 else seeds[0].shape[0]
        ego_matrix = np.eye(n_dims) * self.ego_strength
        
        # 对每个种子应用我执变换
        manas_components = []
        for seed in seeds:
            seed_flat = seed.flatten()
            # 我执变换：seed' = ego_matrix @ seed
            transformed = ego_matrix @ seed_flat
            manas_components.append(transformed)
        
        # 聚合所有末那成分
        manas_field = np.mean(manas_components, axis=0)
        return manas_field
    
    def _apply_no_theater_topology(self, manas_field: np.ndarray) -> np.ndarray:
        """
        应用无剧场拓扑
        
        无剧场论核心：消除主客对立
        - 有剧场：有固定的观众（自我）和表演（感知）
        - 无剧场：观众即表演，表演即观众（非二元）
        
        数学实现：使用 Möbius strip 拓扑，使得"观察者"与"被观察者"在同一曲面上
        """
        # 构建 Möbius strip 参数化
        n = len(manas_field)
        t = np.linspace(0, 2*np.pi, n)
        
        # Möbius strip 坐标
        R = 1.0  # 主半径
        w = 0.3  # 带宽
        
        X = (R + w * np.cos(t/2)) * np.cos(t)
        Y = (R + w * np.cos(t/2)) * np.sin(t)
        Z = w * np.sin(t/2)
        
        # 将末那识场映射到 Möbius strip
        # 使得"主体"与"客体"在拓扑上不可分
        manas_3d = np.column_stack([X, Y, Z])
        
        # 投影回原始维度（保持信息守恒）
        manas_no_theater = manas_field + 0.1 * np.mean(manas_3d, axis=1)[:n]
        
        # 归一化（保持单位长度）
        manas_no_theater = manas_no_theater / np.linalg.norm(manas_no_theater)
        
        self.manas_topology = manas_3d
        logger.info("Applied no-theater topology (Möbius strip)")
        
        return manas_no_theater


class NoTheaterTheory:
    """
    无剧场论实现
    
    消除主客对立，实现真正的非二元认知
    核心：观众=表演，表演=观众，无独立的"观者"
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化无剧场论模块
        
        Args:
            config: 配置参数
                - dissolve_ego: 是否消解自我边界
                - theater_mode: 'traditional' or 'no-theater'
        """
        self.config = config
        self.theater_mode = config.get('theater_mode', 'no-theater')
        self.dissolve_ego = config.get('dissolve_ego', True)
        
        logger.info(f"NoTheaterTheory initialized in {self.theater_mode} mode")
    
    def process_perception(self, perception_input: np.ndarray, 
                          context: Dict[str, Any] = None) -> np.ndarray:
        """
        处理感知（无剧场模式）
        
        传统剧场：perception = f(observer, object)
        无剧场：perception = observer ≡ object（同一性）
        
        Args:
            perception_input: 感知输入
            context: 上下文信息
            
        Returns:
            np.ndarray: 无剧场感知（主客不二）
        """
        if self.theater_mode == 'traditional':
            # 传统剧场：保持主客对立
            return self._traditional_theater_processing(perception_input)
        
        else:  # no-theater
            # 无剧场：消解观察者边界
            return self._no_theater_processing(perception_input)
    
    def _traditional_theater_processing(self, perception: np.ndarray) -> np.ndarray:
        """
        传统剧场处理（有主客对立）
        
        观察者 ≠ 被观察对象
        存在独立的"观者"（self）
        """
        # 传统模式：观察者与被观察者分离
        observer = np.eye(perception.shape[0])  # 单位矩阵（独立的观者）
        observed = perception
        
        # 感知 = 观察者对被观察者的"解读"
        perceived = observer @ observed
        
        logger.debug("Traditional theater processing (with observer-object duality)")
        return perceived
    
    def _no_theater_processing(self, perception: np.ndarray) -> np.ndarray:
        """
        无剧场处理（主客不二）
        
        观察者 ≡ 被观察对象
        无独立的"观者"，观者即被观者
        """
        # 确保perception是2D数组（如果是1D则转换为2D列向量）
        if perception.ndim == 1:
            perception_2d = perception.reshape(-1, 1)  # 转换为列向量 (n, 1)
        else:
            perception_2d = perception
        
        if self.dissolve_ego:
            # 消解自我边界：使得 perception 自身即为主体
            # 数学实现：perception 与自身的同一性映射
            # 使用2D数组进行计算
            norm_sq = np.linalg.norm(perception_2d) ** 2
            if norm_sq > 0:
                identity_map = perception_2d @ perception_2d.T / norm_sq
                no_theater_perception = identity_map @ perception_2d
            else:
                no_theater_perception = perception_2d
            
            # 如果输入是1D，输出也转换为1D
            if perception.ndim == 1:
                no_theater_perception = no_theater_perception.flatten()
            
            logger.debug("No-theater processing (observer = object)")
            return no_theater_perception
        
        else:
            # 不完全消解（保留微弱的自我感）
            n = perception_2d.shape[0]
            weak_ego = 0.1 * np.eye(n)
            no_theater_perception = (weak_ego + np.outer(perception_2d.flatten(), perception_2d.flatten())) @ perception_2d
            
            # 如果输入是1D，输出也转换为1D
            if perception.ndim == 1:
                no_theater_perception = no_theater_perception.flatten()
            
            return no_theater_perception


class ConsciousnessTransformation:
    """
    "识"的形变模型
    
    实现唯识论八识间的相互转化
    八识：眼识、耳识、鼻识、舌识、身识、意识、末那识、阿赖耶识
    """
    
    def __init__(self):
        """初始化识形变模型"""
        self.consciousness_types = ['eye', 'ear', 'nose', 'tongue', 'body', 'mind', 'manas', 'alaya']
        self.transformation_history = []
        
        logger.info("ConsciousnessTransformation model initialized")
    
    def transform(self, source_state: ConsciousnessState, 
                 target_type: str,
                 method: str = 'direct_mapping') -> ConsciousnessState:
        """
        识的形变：从一种识转变为另一种识
        
        Args:
            source_state: 源意识状态
            target_type: 目标识类型（'eye', 'ear', ..., 'alaya'）
            method: 形变方法（'direct_mapping', 'topological_phase_transition'）
            
        Returns:
            ConsciousnessState: 形变后的意识状态
        """
        if target_type not in self.consciousness_types:
            raise ValueError(f"Invalid target type: {target_type}")
        
        if method == 'direct_mapping':
            transformed_data = self._direct_mapping(source_state.data, source_state.consciousness_type, target_type)
            
        elif method == 'topological_phase_transition':
            transformed_data = self._topological_phase_transition(source_state.data, target_type)
            
        else:
            raise ValueError(f"Unknown transformation method: {method}")
        
        # 创建新的意识状态
        transformed_state = ConsciousnessState(
            state_id=f"transformed_{source_state.state_id}_{target_type}",
            consciousness_type=target_type,
            data=transformed_data,
            timestamp=len(self.transformation_history),
            metadata={
                'source_type': source_state.consciousness_type,
                'method': method,
                'transformation_id': len(self.transformation_history)
            }
        )
        
        # 记录形变历史
        self.transformation_history.append({
            'source': source_state.consciousness_type,
            'target': target_type,
            'method': method,
            'timestamp': transformed_state.timestamp
        })
        
        logger.info(f"Transformed {source_state.consciousness_type} → {target_type} via {method}")
        return transformed_state
    
    def _direct_mapping(self, source_data: np.ndarray, source_type: str, target_type: str) -> np.ndarray:
        """
        直接映射形变
        
        简单的线性变换：T: 识_i → 识_j
        """
        # 构建形变矩阵（根据源类型和目标类型）
        n = source_data.shape[-1] if source_data.ndim > 0 else 1
        
        # 使用可训练的形变矩阵（这里简化为随机初始化）
        np.random.seed(hash(source_type + target_type) % 2**32)
        transformation_matrix = np.random.randn(n, n) * 0.1 + np.eye(n)
        
        # 应用形变
        if source_data.ndim == 1:
            transformed = transformation_matrix @ source_data
        else:
            transformed = transformation_matrix @ source_data.flatten()
            transformed = transformed.reshape(source_data.shape)
        
        return transformed
    
    def _topological_phase_transition(self, source_data: np.ndarray, target_type: str) -> np.ndarray:
        """
        拓扑相变形变
        
        通过拓扑结构的相变来实现识的形变
        更贴近唯识论的"识"转换机制
        """
        # 计算源数据的拓扑不变量（如 Euler characteristic）
        euler_char = self._compute_euler_characteristic(source_data)
        
        logger.debug(f"Euler characteristic of source: {euler_char}")
        
        # 根据目标识类型，确定目标拓扑
        target_topology = self._get_target_topology(target_type)
        
        # 执行拓扑相变
        # 简化：通过添加噪声来模拟相变
        phase_transition_noise = np.random.randn(*source_data.shape) * 0.1
        
        if target_topology == 'sphere':
            # 球形拓扑（如眼识、耳识）
            transformed = source_data + phase_transition_noise * 0.5
            
        elif target_topology == 'torus':
            # 环状拓扑（如末那识的 Möbius 结构）
            transformed = source_data * 1.2 + phase_transition_noise
            
        elif target_topology == 'hyperbolic':
            # 双曲拓扑（如阿赖耶识的无限潜能）
            transformed = np.tanh(source_data) + phase_transition_noise * 0.3
            
        else:
            transformed = source_data + phase_transition_noise
        
        return transformed
    
    def _compute_euler_characteristic(self, data: np.ndarray) -> int:
        """
        计算数据的 Euler characteristic（拓扑不变量）
        
        简化实现：假设数据是点云，使用拓扑数据分析（TDA）方法
        """
        # 简化：返回数据的秩作为 Euler characteristic 的近似
        if data.ndim == 1:
            return int(np.linalg.matrix_rank(data.reshape(-1, 1)))
        else:
            return int(np.linalg.matrix_rank(data))
    
    def _get_target_topology(self, consciousness_type: str) -> str:
        """
        获取目标识类型的拓扑结构
        
        根据唯识论，不同识对应不同的拓扑结构
        """
        topology_map = {
            'eye': 'sphere',      # 眼识：球形（视觉空间）
            'ear': 'sphere',      # 耳识：球形（听觉空间）
            'nose': 'sphere',     # 鼻识：球形（嗅觉空间）
            'tongue': 'sphere',   # 舌识：球形（味觉空间）
            'body': 'torus',      # 身识：环状（身体边界）
            'mind': 'hyperbolic', # 意识：双曲（思维空间）
            'manas': 'mobius',    # 末那识：Möbius 带（自我参照）
            'alaya': 'infinite'   # 阿赖耶识：无限维（种子库）
        }
        
        return topology_map.get(consciousness_type, 'sphere')


class ManasNoTheaterModule:
    """
    末那识与无剧场论的统一模块
    
    整合：
    1. 末那识生成器（ManasGenerator）
    2. 无剧场论（NoTheaterTheory）
    3. 识形变模型（ConsciousnessTransformation）
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化统一模块
        
        Args:
            config: 配置参数
        """
        self.config = config
        
        # 初始化子模块
        self.manas_generator = ManasGenerator(config.get('manas', {}))
        self.no_theater = NoTheaterTheory(config.get('no_theater', {}))
        self.transformation = ConsciousnessTransformation()
        
        # 状态管理
        self.current_manas_state = None
        self.alaya_seed_bank = []
        
        logger.info("ManasNoTheaterModule initialized")
    
    def process(self, input_data: np.ndarray, 
                generate_manas: bool = True,
                apply_no_theater: bool = True) -> Dict[str, Any]:
        """
        完整处理流程
        
        Args:
            input_data: 输入数据（来自阿赖耶识种子库）
            generate_manas: 是否生成末那识
            apply_no_theater: 是否应用无剧场论
            
        Returns:
            Dict: 处理结果
        """
        results = {}
        
        # 1. 生成末那识（从阿赖耶识）
        if generate_manas:
            # 假设 input_data 是阿赖耶识种子
            alaya_seeds = [input_data]  # 简化：单个种子
            self.current_manas_state = self.manas_generator.generate_manas(alaya_seeds)
            results['manas_state'] = self.current_manas_state
            
            logger.info(f"Generated Manas: {self.current_manas_state.state_id}")
        
        # 2. 应用无剧场论处理感知
        if apply_no_theater and self.current_manas_state is not None:
            perception_input = self.current_manas_state.data
            no_theater_perception = self.no_theater.process_perception(perception_input)
            
            results['no_theater_perception'] = no_theater_perception
            logger.info("Applied no-theater processing")
        
        # 3. 识形变（可选：将末那识形变为其他识）
        if 'no_theater_perception' in results:
            # 示例：将末那识形变为"意识"（第六识）
            transformed = self.transformation.transform(
                ConsciousnessState(
                    state_id='temp',
                    consciousness_type='manas',
                    data=results['no_theater_perception'],
                    timestamp=0,
                    metadata={}
                ),
                target_type='mind',
                method='topological_phase_transition'
            )
            
            results['transformed_consciousness'] = transformed
            logger.info(f"Transformed Manas → Mind")
        
        return results
    
    def get_manas_topology_visualization(self) -> np.ndarray:
        """
        获取末那识拓扑可视化数据
        
        Returns:
            np.ndarray: Möbius strip 坐标 (N, 3)
        """
        if self.manas_generator.manas_topology is not None:
            return self.manas_generator.manas_topology
        else:
            logger.warning("No topology data available. Run process() first.")
            return None


# 测试用例
if __name__ == "__main__":
    # 配置
    config = {
        'manas': {
            'ego_strength': 0.7,
            'attachment_threshold': 0.5
        },
        'no_theater': {
            'theater_mode': 'no-theater',
            'dissolve_ego': True
        }
    }
    
    # 创建模块
    module = ManasNoTheaterModule(config)
    
    # 测试数据（模拟阿赖耶识种子）
    test_seed = np.random.randn(10)
    
    # 处理
    results = module.process(test_seed, generate_manas=True, apply_no_theater=True)
    
    print("=== 末那识与无剧场论模块测试 ===")
    print(f"输入种子维度: {test_seed.shape}")
    print(f"末那识状态 ID: {results['manas_state'].state_id}")
    print(f"末那识数据类型: {results['manas_state'].consciousness_type}")
    print(f"无剧场感知维度: {results['no_theater_perception'].shape}")
    
    if 'transformed_consciousness' in results:
        print(f"形变后意识类型: {results['transformed_consciousness'].consciousness_type}")
    
    # 获取拓扑可视化
    topology = module.get_manas_topology_visualization()
    if topology is not None:
        print(f"末那识拓扑（Möbius strip）形状: {topology.shape}")
