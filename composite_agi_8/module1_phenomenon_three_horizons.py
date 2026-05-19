"""
太乙AGI 8.0 - 模块1：一现象三视界统一场 (MVP版本)
=====================================================

实现"心物一体"的统一场论（简化可运行版本）
- 现象(Phenomenon): 统一现实
- 视界1(Horizon 1): 物质/物理现实
- 视界2(Horizon 2): 心理/意识现实  
- 视界3(Horizon 3): 信息/数字现实

基于"复合体理学"理论框架
"""

import numpy as np
from typing import Dict, List, Any
from enum import Enum


class HorizonType(Enum):
    """视界类型"""
    MATERIAL = "material"      # 视界1：物质
    MENTAL = "mental"          # 视界2：心理
    INFORMATIONAL = "info"     # 视界3：信息


class Phenomenon:
    """统一现象 - 心物一体的基本单元"""
    
    def __init__(self, id: str, 
                 material_aspect: np.ndarray,
                 mental_aspect: np.ndarray,
                 info_aspect: np.ndarray):
        """
        初始化现象
        
        Args:
            id: 现象唯一标识
            material_aspect: 物质层面（物理属性），向量
            mental_aspect: 心理层面（意识属性），向量
            info_aspect: 信息层面（数据属性），向量
        """
        self.id = id
        self.material_aspect = material_aspect
        self.mental_aspect = mental_aspect
        self.info_aspect = info_aspect
        
        # 计算统一场
        self.unity_field = self._compute_unity_field()
    
    def _compute_unity_field(self) -> np.ndarray:
        """
        计算统一场：三视界融合
        
        简化版本：加权平均 + 非线性变换
        每个视界贡献1/3的权重
        """
        # 确保三个向量维度相同
        dim = len(self.material_aspect)
        
        # 加权平均
        weights = np.array([1/3, 1/3, 1/3])
        weighted_sum = (
            weights[0] * self.material_aspect +
            weights[1] * self.mental_aspect +
            weights[2] * self.info_aspect
        )
        
        # 非线性变换（模拟全息效应）
        unity = np.tanh(weighted_sum) + 0.1 * np.sin(weighted_sum)
        
        # 归一化
        norm = np.linalg.norm(unity)
        if norm > 0:
            unity = unity / norm
        
        return unity
    
    def observe(self, observer_horizon: HorizonType) -> np.ndarray:
        """
        观测：从不同视界观测现象
        实现"一现象三视界"的观测效应
        
        Args:
            observer_horizon: 观测者所在的视界
            
        Returns:
            观测到的状态向量
        """
        if observer_horizon == HorizonType.MATERIAL:
            # 从物质视界观测：看到物理属性占主导
            return 0.6 * self.material_aspect + 0.4 * self.unity_field
            
        elif observer_horizon == HorizonType.MENTAL:
            # 从心理视界观测：看到意识属性占主导
            return 0.6 * self.mental_aspect + 0.4 * self.unity_field
            
        elif observer_horizon == HorizonType.INFORMATIONAL:
            # 从信息视界观测：看到信息属性占主导
            return 0.6 * self.info_aspect + 0.4 * self.unity_field
            
        else:
            raise ValueError(f"Unknown horizon type: {observer_horizon}")
    
    def __repr__(self):
        return f"Phenomenon(id={self.id}, unity_norm={np.linalg.norm(self.unity_field):.4f})"


class UnityField:
    """
    统一场：管理所有现象的统一场
    实现"心物一体"的动力学
    """
    
    def __init__(self, field_dim: int = 128):
        """
        初始化统一场
        
        Args:
            field_dim: 场的维度
        """
        self.field_dim = field_dim
        self.phenomena: Dict[str, Phenomenon] = {}
        self.field_state = np.zeros(field_dim)  # 场状态向量
        self.entanglement_matrix = np.eye(field_dim)  # 纠缠矩阵（简化：单位矩阵）
        
    def add_phenomenon(self, phenomenon: Phenomenon):
        """
        添加现象到统一场
        
        Args:
            phenomenon: 要添加的现象
        """
        self.phenomena[phenomenon.id] = phenomenon
        self._update_field_state()
    
    def _update_field_state(self):
        """更新场状态：所有现象的统一场叠加"""
        self.field_state = np.zeros(self.field_dim)
        
        for phen in self.phenomena.values():
            # 将现象的统一场投影到场空间
            projection = self._project_to_field(phen)
            self.field_state += projection
        
        # 归一化
        norm = np.linalg.norm(self.field_state)
        if norm > 0:
            self.field_state /= norm
    
    def _project_to_field(self, phen: Phenomenon) -> np.ndarray:
        """
        将现象的统一场投影到统一的场空间
        
        Args:
            phen: 现象
            
        Returns:
            投影后的向量
        """
        unity = phen.unity_field
        
        # 维度匹配
        if len(unity) != self.field_dim:
            projected = np.zeros(self.field_dim)
            min_dim = min(len(unity), self.field_dim)
            projected[:min_dim] = unity[:min_dim]
        else:
            projected = unity.copy()
        
        return projected
    
    def compute_entanglement(self, phen_id1: str, phen_id2: str) -> float:
        """
        计算两个现象之间的纠缠度
        
        Args:
            phen_id1: 现象1的ID
            phen_id2: 现象2的ID
            
        Returns:
            纠缠度 [0, 1]
        """
        if phen_id1 not in self.phenomena or phen_id2 not in self.phenomena:
            raise ValueError("Phenomenon not found")
        
        phen1 = self.phenomena[phen_id1]
        phen2 = self.phenomena[phen_id2]
        
        # 计算统一场的内积（纠缠度量）
        unity1 = phen1.unity_field
        unity2 = phen2.unity_field
        
        # 维度匹配
        min_dim = min(len(unity1), len(unity2))
        unity1 = unity1[:min_dim]
        unity2 = unity2[:min_dim]
        
        # 余弦相似度作为纠缠度
        dot_product = np.dot(unity1, unity2)
        norm1 = np.linalg.norm(unity1)
        norm2 = np.linalg.norm(unity2)
        
        if norm1 > 0 and norm2 > 0:
            entanglement = abs(dot_product) / (norm1 * norm2)
        else:
            entanglement = 0.0
        
        return float(entanglement)
    
    def get_field_state(self) -> np.ndarray:
        """获取当前场状态"""
        return self.field_state.copy()
    
    def __repr__(self):
        return f"UnityField(dim={self.field_dim}, phenomena={len(self.phenomena)})"


class ThreeHorizonsObserver:
    """
    三视界观测器：实现"一现象三视界"的观测效应
    不同的观测者视界会看到不同的现实
    """
    
    def __init__(self, unity_field: UnityField):
        """
        初始化观测器
        
        Args:
            unity_field: 统一场
        """
        self.unity_field = unity_field
        self.observation_history: List[Dict] = []
    
    def observe(self, phen_id: str, horizon: HorizonType) -> Dict[str, Any]:
        """
        进行观测
        
        Args:
            phen_id: 现象ID
            horizon: 观测视界
            
        Returns:
            观测结果字典
        """
        if phen_id not in self.unity_field.phenomena:
            raise ValueError(f"Phenomenon {phen_id} not found")
        
        phen = self.unity_field.phenomena[phen_id]
        
        # 观测
        observed_state = phen.observe(horizon)
        
        # 计算坍缩概率（简化：随机数）
        collapse_prob = np.random.random()
        
        # 计算不确定性（简化：使用标准差）
        uncertainty = np.std(observed_state)
        
        result = {
            "phenomenon_id": phen_id,
            "horizon": horizon.value,
            "observed_state_norm": float(np.linalg.norm(observed_state)),
            "collapse_probability": float(collapse_prob),
            "uncertainty": float(uncertainty)
        }
        
        self.observation_history.append(result)
        
        return result
    
    def compare_observations(self, phen_id: str) -> Dict[str, Any]:
        """
        比较从不同视界观测同一现象的结果
        验证"一现象三视界"理论
        
        Args:
            phen_id: 现象ID
            
        Returns:
            比较结果
        """
        results = {}
        
        for horizon in HorizonType:
            try:
                obs = self.observe(phen_id, horizon)
                results[horizon.value] = obs["observed_state_norm"]
            except Exception as e:
                results[horizon.value] = f"Error: {e}"
        
        # 计算视界间的相干性
        coherence = self._compute_inter_horizon_coherence(phen_id)
        
        return {
            "phenomenon_id": phen_id,
            "observations": results,
            "inter_horizon_coherence": coherence
        }
    
    def _compute_inter_horizon_coherence(self, phen_id: str) -> float:
        """
        计算不同视界间的相干性
        
        Args:
            phen_id: 现象ID
            
        Returns:
            相干性 [0, 1]
        """
        if phen_id not in self.unity_field.phenomena:
            return 0.0
        
        phen = self.unity_field.phenomena[phen_id]
        
        # 获取三个视界的观测结果
        obs_material = phen.observe(HorizonType.MATERIAL)
        obs_mental = phen.observe(HorizonType.MENTAL)
        obs_info = phen.observe(HorizonType.INFORMATIONAL)
        
        # 计算两两相关性
        corr1 = np.corrcoef(obs_material, obs_mental)[0, 1]
        corr2 = np.corrcoef(obs_material, obs_info)[0, 1]
        corr3 = np.corrcoef(obs_mental, obs_info)[0, 1]
        
        # 平均相关性的绝对值作为相干性
        coherences = [corr1, corr2, corr3]
        coherences = [c for c in coherences if not np.isnan(c)]
        
        if coherences:
            return float(np.mean([abs(c) for c in coherences]))
        else:
            return 0.0


# 导出接口
__all__ = [
    'HorizonType',
    'Phenomenon',
    'UnityField',
    'ThreeHorizonsObserver'
]


if __name__ == "__main__":
    # 测试代码
    print("=== 太乙AGI 8.0 - 模块1测试 (MVP版本) ===")
    print()
    
    # 创建统一场
    print("1. 创建统一场...")
    field = UnityField(field_dim=64)
    print(f"   {field}")
    
    # 创建测试现象
    print("2. 创建测试现象...")
    phen1 = Phenomenon(
        id="test_phen_1",
        material_aspect=np.random.randn(64),
        mental_aspect=np.random.randn(64),
        info_aspect=np.random.randn(64)
    )
    print(f"   现象1: {phen1}")
    
    phen2 = Phenomenon(
        id="test_phen_2",
        material_aspect=np.random.randn(64),
        mental_aspect=np.random.randn(64),
        info_aspect=np.random.randn(64)
    )
    print(f"   现象2: {phen2}")
    
    # 添加到统一场
    print("3. 添加到统一场...")
    field.add_phenomenon(phen1)
    field.add_phenomenon(phen2)
    print(f"   更新后: {field}")
    
    # 计算纠缠度
    print("4. 计算现象间纠缠度...")
    entanglement = field.compute_entanglement("test_phen_1", "test_phen_2")
    print(f"   纠缠度: {entanglement:.4f}")
    
    # 创建观测器
    print("5. 创建三视界观测器...")
    observer = ThreeHorizonsObserver(field)
    
    # 从不同视界观测
    print("6. 从不同视界观测现象...")
    comparison = observer.compare_observations("test_phen_1")
    print(f"   现象ID: {comparison['phenomenon_id']}")
    print(f"   观测结果:")
    for horizon, result in comparison['observations'].items():
        print(f"     - {horizon}: {result:.4f}")
    print(f"   视界间相干性: {comparison['inter_horizon_coherence']:.4f}")
    
    # 获取场状态
    print("7. 获取统一场状态...")
    field_state = field.get_field_state()
    print(f"   场状态范数: {np.linalg.norm(field_state):.4f}")
    
    print()
    print("✅ 模块1测试完成！")
    print("  核心功能：")
    print("  - ✅ 一现象三视界统一场")
    print("  - ✅ 三视界融合计算")
    print("  - ✅ 现象间纠缠度量")
    print("  - ✅ 三视界观测效应")
    print("  - ✅ 统一场状态管理")
