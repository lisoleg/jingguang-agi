"""
唯识论八识计算模型 (YogacaraEightConsciousness.py)
基于复合体理学的唯识论形式化实现

八识体系：
1. 眼识 (Eye Consciousness) - 视觉感知
2. 耳识 (Ear Consciousness) - 听觉感知
3. 鼻识 (Nose Consciousness) - 嗅觉感知
4. 舌识 (Tongue Consciousness) - 味觉感知
5. 身识 (Body Consciousness) - 触觉感知
6. 意识 (Mind Consciousness) - 第六识，思维、判断
7. 末那识 (Manas Consciousness) - 第七识，我执、自我参照
8. 阿赖耶识 (Alaya Consciousness) - 第八识，种子库、潜能场

核心理论：
- "识"的形变：八识间的相互转化
- "种子"与"现行"：阿赖耶识中的潜在种子与现实活动的相互作用
- "转识成智"：从识到智慧的转化（佛学终极目标）
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsciousnessType(Enum):
    """识的类型枚举"""
    EYE = "eye"           # 眼识
    EAR = "ear"           # 耳识
    NOSE = "nose"         # 鼻识
    TONGUE = "tongue"     # 舌识
    BODY = "body"         # 身识
    MIND = "mind"         # 意识（第六识）
    MANAS = "manas"       # 末那识（第七识）
    ALAYA = "alaya"       # 阿赖耶识（第八识）


@dataclass
class Seed:
    """种子数据结构（阿赖耶识中的潜在能量）"""
    seed_id: str
    content: np.ndarray           # 种子内容（向量表示）
    potential: float = 1.0      # 潜能值（0-1）
    activation_count: int = 0    # 被激活次数
    last_activation: int = 0     # 最后激活时间
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsciousnessActivity:
    """识的活动记录"""
    activity_id: str
    consciousness_type: ConsciousnessType
    input_seeds: List[Seed]
    output_activity: np.ndarray    # 现行活动（向量表示）
    timestamp: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class EightConsciousnessModel:
    """
    唯识论八识计算模型
    
    实现八识的：
    1. 种子存储（阿赖耶识）
    2. 现行活动（前七识）
    3. 识的形变（八识间的相互转化）
    4. 转识成智（从识到智慧的转化）
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化八识模型
        
        Args:
            config: 配置参数
                - alaya_capacity: 阿赖耶识容量（种子数量上限）
                - activation_threshold: 种子激活阈值
                - transformation_rate: 识形变速率
                - wisdom_threshold: 转识成智阈值
        """
        self.config = config
        self.alaya_capacity = config.get('alaya_capacity', 10000)
        self.activation_threshold = config.get('activation_threshold', 0.5)
        self.transformation_rate = config.get('transformation_rate', 0.1)
        self.wisdom_threshold = config.get('wisdom_threshold', 0.9)
        
        # 阿赖耶识（种子库）
        self.alaya_seeds: Dict[str, Seed] = {}
        
        # 前七识的活动记录
        self.consciousness_activities: Dict[ConsciousnessType, List[ConsciousnessActivity]] = {
            ct: [] for ct in ConsciousnessType if ct != ConsciousnessType.ALAYA
        }
        
        # 智慧状态（转识成智后的结果）
        self.wisdom_states = []
        
        # 活动计数器
        self.activity_counter = 0
        
        logger.info(f"EightConsciousnessModel initialized: "
                   f"alaya_capacity={self.alaya_capacity}")
    
    def store_seed(self, seed_content: np.ndarray, 
                  seed_id: Optional[str] = None) -> Seed:
        """
        存储种子到阿赖耶识
        
        Args:
            seed_content: 种子内容（向量）
            seed_id: 种子ID（可选，自动生成）
            
        Returns:
            Seed: 存储的种子对象
        """
        if seed_id is None:
            seed_id = f"seed_{len(self.alaya_seeds)}"
        
        # 检查容量
        if len(self.alaya_seeds) >= self.alaya_capacity:
            # 移除最旧或激活次数最少的种子（简化：随机移除）
            oldest_id = min(self.alaya_seeds.keys(), 
                           key=lambda k: self.alaya_seeds[k].last_activation)
            del self.alaya_seeds[oldest_id]
            logger.warning(f"Alaya capacity reached, removed seed {oldest_id}")
        
        # 创建新种子
        seed = Seed(
            seed_id=seed_id,
            content=seed_content,
            potential=np.linalg.norm(seed_content) / len(seed_content)
        )
        
        self.alaya_seeds[seed_id] = seed
        logger.info(f"Stored seed {seed_id} in Alaya")
        
        return seed
    
    def activate_seeds(self, stimulus: np.ndarray, 
                      n_seeds: int = 5) -> List[Seed]:
        """
        激活阿赖耶识中的种子
        
        刺激 → 匹配最相关的种子 → 激活
        
        Args:
            stimulus: 刺激输入（向量）
            n_seeds: 激活的种子数量
            
        Returns:
            List[Seed]: 被激活的种子列表
        """
        if not self.alaya_seeds:
            logger.warning("No seeds in Alaya to activate")
            return []
        
        # 计算刺激与每个种子的相关性
        similarities = []
        for seed_id, seed in self.alaya_seeds.items():
            # 余弦相似度
            similarity = np.dot(stimulus, seed.content) / (
                np.linalg.norm(stimulus) * np.linalg.norm(seed.content) + 1e-8
            )
            similarities.append((seed_id, similarity, seed.potential))
        
        # 综合评分：相似度 × 潜能值
        scores = [(sid, sim * pot) for sid, sim, pot in similarities]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 激活 top-n 种子
        activated = []
        for seed_id, score in scores[:n_seeds]:
            if score > self.activation_threshold:
                seed = self.alaya_seeds[seed_id]
                seed.activation_count += 1
                seed.last_activation = self.activity_counter
                activated.append(seed)
        
        logger.info(f"Activated {len(activated)} seeds from Alaya")
        
        return activated
    
    def process_through_consciousness(self, 
                                     activated_seeds: List[Seed],
                                     consciousness_type: ConsciousnessType,
                                     stimulus: Optional[np.ndarray] = None) -> np.ndarray:
        """
        通过特定识处理种子（产生现行活动）
        
        唯识论：种子（潜在）→ 现行（现实活动）
        
        Args:
            activated_seeds: 被激活的种子
            consciousness_type: 识的类型
            stimulus: 外部刺激（可选）
            
        Returns:
            np.ndarray: 现行活动（输出向量）
        """
        if not activated_seeds:
            logger.warning(f"No activated seeds for {consciousness_type.value}")
            return np.zeros(10)  # 返回零向量
        
        # 聚合种子内容
        aggregated = np.mean([s.content for s in activated_seeds], axis=0)
        
        # 根据识的类型，应用不同的变换
        if consciousness_type == ConsciousnessType.EYE:
            # 眼识：视觉变换（边缘检测、颜色感知等）
            output = self._eye_consciousness_transform(aggregated, stimulus)
            
        elif consciousness_type == ConsciousnessType.EAR:
            # 耳识：听觉变换（频率分析、音色感知等）
            output = self._ear_consciousness_transform(aggregated, stimulus)
            
        elif consciousness_type == ConsciousnessType.NOSE:
            # 鼻识：嗅觉变换
            output = self._nose_consciousness_transform(aggregated, stimulus)
            
        elif consciousness_type == ConsciousnessType.TONGUE:
            # 舌识：味觉变换
            output = self._tongue_consciousness_transform(aggregated, stimulus)
            
        elif consciousness_type == ConsciousnessType.BODY:
            # 身识：触觉变换
            output = self._body_consciousness_transform(aggregated, stimulus)
            
        elif consciousness_type == ConsciousnessType.MIND:
            # 意识（第六识）：思维、判断、整合
            output = self._mind_consciousness_transform(aggregated, stimulus)
            
        elif consciousness_type == ConsciousnessType.MANAS:
            # 末那识（第七识）：我执、自我参照
            output = self._manas_consciousness_transform(aggregated, stimulus)
            
        else:
            raise ValueError(f"Invalid consciousness type for processing: {consciousness_type}")
        
        # 记录活动
        activity = ConsciousnessActivity(
            activity_id=f"activity_{self.activity_counter}",
            consciousness_type=consciousness_type,
            input_seeds=activated_seeds,
            output_activity=output,
            timestamp=self.activity_counter
        )
        
        self.consciousness_activities[consciousness_type].append(activity)
        self.activity_counter += 1
        
        logger.info(f"Processed through {consciousness_type.value}: "
                   f"output_shape={output.shape}")
        
        return output
    
    def _eye_consciousness_transform(self, aggregated: np.ndarray,
                                     stimulus: Optional[np.ndarray]) -> np.ndarray:
        """眼识变换：视觉处理"""
        # 简化：应用边缘检测滤波器
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]])
        
        # 将聚合向量重塑为伪图像（简化）
        size = int(np.sqrt(len(aggregated)))
        if size * size != len(aggregated):
            size = int(np.ceil(np.sqrt(len(aggregated))))
            padded = np.pad(aggregated, (0, size*size - len(aggregated)))
        else:
            padded = aggregated
        
        pseudo_image = padded.reshape(size, size)
        
        # 应用卷积（简化）
        output = np.zeros_like(pseudo_image)
        for i in range(size - 2):
            for j in range(size - 2):
                patch = pseudo_image[i:i+3, j:j+3]
                output[i+1, j+1] = np.sum(patch * kernel)
        
        return output.flatten()
    
    def _ear_consciousness_transform(self, aggregated: np.ndarray,
                                    stimulus: Optional[np.ndarray]) -> np.ndarray:
        """耳识变换：听觉处理（频率分析）"""
        # 简化：应用傅里叶变换（频率分析）
        n = len(aggregated)
        output = np.fft.fft(aggregated).real[:n]
        return output
    
    def _nose_consciousness_transform(self, aggregated: np.ndarray,
                                     stimulus: Optional[np.ndarray]) -> np.ndarray:
        """鼻识变换：嗅觉处理"""
        # 简化：气味特征提取（浓度、类型等）
        concentration = np.linalg.norm(aggregated)
        output = aggregated * concentration
        return output
    
    def _tongue_consciousness_transform(self, aggregated: np.ndarray,
                                       stimulus: Optional[np.ndarray]) -> np.ndarray:
        """舌识变换：味觉处理"""
        # 简化：味觉分类（甜、酸、苦、咸、鲜）
        taste_categories = np.array([0.2, 0.2, 0.2, 0.2, 0.2])  # 均匀初始化
        output = aggregated[:len(taste_categories)] * taste_categories
        return output
    
    def _body_consciousness_transform(self, aggregated: np.ndarray,
                                     stimulus: Optional[np.ndarray]) -> np.ndarray:
        """身识变换：触觉处理"""
        # 简化：压力、温度、质地感知
        pressure = np.sum(aggregated)
        output = aggregated * (1.0 + 0.1 * pressure)
        return output
    
    def _mind_consciousness_transform(self, aggregated: np.ndarray,
                                     stimulus: Optional[np.ndarray]) -> np.ndarray:
        """意识（第六识）变换：思维、判断、整合"""
        # 简化：思维整合（前七识的整合器）
        if stimulus is not None:
            # 意识整合外部刺激和内部种子
            output = 0.5 * aggregated + 0.5 * stimulus
        else:
            output = aggregated
        
        # 添加思维噪声（模拟思维的随机性）
        noise = np.random.randn(*output.shape) * 0.01
        output = output + noise
        
        return output
    
    def _manas_consciousness_transform(self, aggregated: np.ndarray,
                                      stimulus: Optional[np.ndarray]) -> np.ndarray:
        """末那识（第七识）变换：我执、自我参照"""
        # 末那识核心：对所有输入添加"我"的标记（我执）
        ego_marker = np.eye(len(aggregated)) * 0.7  # 我执强度
        
        # 自我参照变换：output = ego_marker @ aggregated
        output = ego_marker @ aggregated
        
        # 末那识持续监控"我"的存在
        self_reference = np.dot(output, output) / (np.linalg.norm(output) + 1e-8)
        
        logger.debug(f"Manas self-reference strength: {self_reference:.4f}")
        
        return output
    
    def transform_consciousness(self, 
                                source_activity: ConsciousnessActivity,
                                target_type: ConsciousnessType) -> np.ndarray:
        """
        "识"的形变：从一种识转变为另一种识
        
        唯识论核心：八识可以相互转化
        例如：眼识（视觉）→ 意识（思维）→ 末那识（我执）
        
        Args:
            source_activity: 源识的活动
            target_type: 目标识类型
            
        Returns:
            np.ndarray: 形变后的活动
        """
        source_output = source_activity.output_activity
        
        # 形变矩阵（可学习参数，这里简化为随机初始化）
        np.random.seed(hash(source_activity.consciousness_type.value + target_type.value) % 2**32)
        transformation_matrix = np.random.randn(len(source_output), len(source_output)) * 0.1
        transformation_matrix += np.eye(len(source_output))  # 保留恒等变换成分
        
        # 应用形变
        transformed = transformation_matrix @ source_output
        
        logger.info(f"Transformed {source_activity.consciousness_type.value} → {target_type.value}")
        
        return transformed
    
    def transform_to_wisdom(self, consciousness_activity: ConsciousnessActivity) -> Optional[np.ndarray]:
        """
        转识成智：从识到智慧的转化
        
        唯识论终极目标：
        - 眼识 → 成所作智
        - 耳识、鼻识、舌识、身识 → 成所作智
        - 意识（第六识） → 妙观察智
        - 末那识（第七识） → 平等性智
        - 阿赖耶识（第八识） → 大圆镜智
        
        Args:
            consciousness_activity: 识的活动
            
        Returns:
            Optional[np.ndarray]: 智慧状态（如果达到阈值）
        """
        # 计算智慧潜力
        activity_strength = np.linalg.norm(consciousness_activity.output_activity)
        wisdom_potential = activity_strength / (np.max(np.abs(consciousness_activity.output_activity)) + 1e-8)
        
        if wisdom_potential > self.wisdom_threshold:
            # 转识成智！
            consciousness_type = consciousness_activity.consciousness_type
            
            if consciousness_type in [ConsciousnessType.EYE, ConsciousnessType.EAR,
                                     ConsciousnessType.NOSE, ConsciousnessType.TONGUE,
                                     ConsciousnessType.BODY]:
                wisdom_type = "成所作智"
                
            elif consciousness_type == ConsciousnessType.MIND:
                wisdom_type = "妙观察智"
                
            elif consciousness_type == ConsciousnessType.MANAS:
                wisdom_type = "平等性智"
                
            elif consciousness_type == ConsciousnessType.ALAYA:
                wisdom_type = "大圆镜智"
                
            else:
                wisdom_type = "未知智慧"
            
            # 生成智慧状态
            wisdom_state = consciousness_activity.output_activity * 2.0  # 智慧增强
            
            self.wisdom_states.append({
                'wisdom_type': wisdom_type,
                'state': wisdom_state,
                'source': consciousness_type.value,
                'timestamp': self.activity_counter
            })
            
            logger.info(f"Transform to wisdom: {consciousness_type.value} → {wisdom_type}")
            
            return wisdom_state
        
        else:
            logger.debug(f"Wisdom potential {wisdom_potential:.4f} < threshold {self.wisdom_threshold}")
            return None
    
    def get_alaya_seed_bank_status(self) -> Dict[str, Any]:
        """获取阿赖耶识种子库状态"""
        if not self.alaya_seeds:
            return {'count': 0}
        
        potentials = [s.potential for s in self.alaya_seeds.values()]
        activation_counts = [s.activation_count for s in self.alaya_seeds.values()]
        
        return {
            'count': len(self.alaya_seeds),
            'avg_potential': np.mean(potentials),
            'max_potential': np.max(potentials),
            'avg_activation_count': np.mean(activation_counts),
            'total_activations': sum(activation_counts)
        }
    
    def get_consciousness_activity_summary(self) -> Dict[str, Any]:
        """获取前七识活动摘要"""
        summary = {}
        
        for ct, activities in self.consciousness_activities.items():
            if activities:
                recent = activities[-5:]  # 最近5次活动
                summary[ct.value] = {
                    'activity_count': len(activities),
                    'recent_outputs': [a.output_activity[:5] for a in recent]  # 前5维
                }
        
        return summary


# 测试用例
if __name__ == "__main__":
    print("=== 唯识论八识计算模型测试 ===\n")
    
    # 1. 初始化模型
    config = {
        'alaya_capacity': 1000,
        'activation_threshold': 0.3,
        'wisdom_threshold': 0.85
    }
    
    model = EightConsciousnessModel(config)
    
    # 2. 存储种子到阿赖耶识
    print("1. 存储种子到阿赖耶识:")
    for i in range(10):
        seed_content = np.random.randn(10)
        seed = model.store_seed(seed_content, seed_id=f"test_seed_{i}")
        print(f"   存储种子 {seed.seed_id}: potential={seed.potential:.4f}")
    
    # 3. 激活种子
    print("\n2. 激活种子:")
    stimulus = np.random.randn(10)
    activated = model.activate_seeds(stimulus, n_seeds=3)
    print(f"   激活了 {len(activated)} 个种子")
    
    # 4. 通过不同识处理
    print("\n3. 通过不同识处理:")
    for ct in [ConsciousnessType.EYE, ConsciousnessType.MIND, ConsciousnessType.MANAS]:
        output = model.process_through_consciousness(activated, ct, stimulus)
        print(f"   {ct.value}: output_shape={output.shape}, "
              f"norm={np.linalg.norm(output):.4f}")
    
    # 5. 识的形变
    print("\n4. 识的形变:")
    mind_activity = model.consciousness_activities[ConsciousnessType.MIND][-1]
    transformed = model.transform_consciousness(mind_activity, ConsciousnessType.MANAS)
    print(f"   意识 → 末那识: transformed_shape={transformed.shape}")
    
    # 6. 转识成智
    print("\n5. 转识成智:")
    manas_activity = model.consciousness_activities[ConsciousnessType.MANAS][-1]
    wisdom = model.transform_to_wisdom(manas_activity)
    if wisdom is not None:
        print(f"   转识成智成功! wisdom_shape={wisdom.shape}")
    else:
        print("   智慧潜力不足，未达到转识成智阈值")
    
    # 7. 查看状态
    print("\n6. 阿赖耶识种子库状态:")
    alaya_status = model.get_alaya_seed_bank_status()
    for key, value in alaya_status.items():
        print(f"   {key}: {value}")
    
    print("\n=== 测试完成 ===")
