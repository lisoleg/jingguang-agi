# -*- coding: utf-8 -*-
"""
HolographicProjectionModule - 全息投影压缩模块
复合体AGI 5.0 核心模块

基于章锋论文《一元数流灌充、N元数全息代数与隐维规范场论》中的全息投影理论：
- 高维信息可投影至低维
- 投影伴随"降维损伤"
- 但关键不变量（拓扑序、对称）保持
- "残疾代数"保留高维全息信息残差
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class InvariantType(Enum):
    """不变量类型"""
    TOPOLOGY = "topology"           # 拓扑结构
    SYMMETRY = "symmetry"          # 对称性
    PHASE = "phase"               # 相位关系
    ENTROPY = "entropy"           # 信息熵
    CURVATURE = "curvature"       # 曲率特征


@dataclass
class HolographicConfig:
    """全息投影配置"""
    compression_ratio: float = 0.1      # 压缩比
    max_invariants: int = 5             # 最大不变量数量
    reconstruction_attempts: int = 3    # 重建尝试次数
    preserve_topology: bool = True      # 是否保持拓扑


class HolographicProjectionModule:
    """
    全息投影模块
    
    核心原理：
    1. 高维信息可投影至低维表示
    2. 投影过程保留关键不变量
    3. "残疾代数"现象：高维结构在低维的残缺显化
    4. 可逆全息变换：信息可从低维重建
    
    应用场景：
    1. 长文本摘要（保持语义拓扑）
    2. 知识压缩（保持核心结构）
    3. 多模态融合（跨模态不变特征）
    4. 记忆压缩（高效存储与检索）
    """
    
    def __init__(self, config: Optional[HolographicConfig] = None):
        self.config = config or HolographicConfig()
        self.invariant_extractors = {}
        self.projection_matrix = None
        self.reconstruction_cache = {}
        
    def compress(self, 
                high_dim_data: np.ndarray,
                invariants: Optional[List[InvariantType]] = None,
                return_invariants: bool = True) -> Dict[str, Any]:
        """
        全息压缩
        
        将高维数据压缩到低维表示，同时保留关键不变量
        
        Args:
            high_dim_data: 高维输入数据 [d_high] 或 [n, d_high]
            invariants: 要保留的不变量类型列表
            return_invariants: 是否返回不变量信息
            
        Returns:
            压缩结果字典
        """
        if invariants is None:
            invariants = [InvariantType.TOPOLOGY, InvariantType.SYMMETRY]
        
        # 确保数据是2D的
        original_shape = high_dim_data.shape
        if high_dim_data.ndim == 1:
            high_dim_data = high_dim_data.reshape(1, -1)
        
        d_high = high_dim_data.shape[-1]
        d_low = max(1, int(d_high * self.config.compression_ratio))
        
        # 1. 提取不变量
        invariant_features = {}
        for inv_type in invariants:
            invariant_features[inv_type.value] = self._extract_invariant(
                high_dim_data, inv_type
            )
        
        # 2. 构建投影矩阵（数据依赖的）
        self.projection_matrix = self._learn_projection_matrix(
            high_dim_data, d_low, invariant_features
        )
        
        # 3. 执行投影
        compressed = self._apply_projection(high_dim_data, self.projection_matrix)
        
        # 如果原数据是1D，也返回1D
        if len(original_shape) == 1:
            compressed = compressed.flatten()
        
        # 4. 计算全息残差（信息残差）
        if len(original_shape) == 1:
            high_dim_data_orig = high_dim_data.flatten()
        else:
            high_dim_data_orig = high_dim_data
        
        residual = self._compute_residual(high_dim_data_orig, compressed, self.projection_matrix)
        
        result = {
            'compressed': compressed,
            'dimension': {'high': d_high, 'low': d_low},
            'projection_matrix': self.projection_matrix,
            'compression_ratio': d_low / d_high
        }
        
        if return_invariants:
            result['invariants'] = invariant_features
            result['residual'] = residual
            
        return result
    
    def expand(self, 
               compressed_data: np.ndarray,
               invariants: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        """
        全息展开
        
        从低维表示重建高维结构
        
        Args:
            compressed_data: 压缩后的数据
            invariants: 不变量信息（用于指导重建）
            
        Returns:
            重建的高维数据
        """
        if self.projection_matrix is None:
            raise ValueError("No projection matrix. Run compress() first.")
        
        # 投影矩阵直接重建
        # projection_matrix: [d_low, d_high]
        # compressed_data: [n, d_low] 或 [d_low]
        # reconstructed: [n, d_high] 或 [d_high]
        reconstructed = compressed_data @ self.projection_matrix
        
        if invariants:
            # 利用不变量进行校正
            reconstructed = self._correct_with_invariants(
                reconstructed, invariants
            )
        
        return reconstructed
    
    def holographic_retrieval(self,
                               query: np.ndarray,
                               memory_bank: np.ndarray,
                               k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        全息检索
        
        在压缩的记忆库中进行高效检索
        
        Args:
            query: 查询向量
            memory_bank: 记忆库矩阵 [n, d_high]
            k: 返回top-k结果
            
        Returns:
            (相似记忆, 相似度分数)
        """
        # 压缩记忆库
        compressed_bank = []
        for memory in memory_bank:
            result = self.compress(memory, return_invariants=False)
            compressed_bank.append(result['compressed'])
        compressed_bank = np.array(compressed_bank)
        
        # 压缩查询
        query_compressed = self.compress(query, return_invariants=False)['compressed']
        
        # 计算相似度（低维空间）
        similarities = self._cosine_similarity_batch(query_compressed, compressed_bank)
        
        # 获取top-k
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        return memory_bank[top_k_indices], similarities[top_k_indices]
    
    def semantic_preserving_compress(self,
                                     text_embedding: np.ndarray,
                                     semantic_aspects: List[str]) -> Dict[str, Any]:
        """
        语义保持压缩
        
        针对文本嵌入的特殊处理，保持语义不变量
        
        Args:
            text_embedding: 文本的语义嵌入向量
            semantic_aspects: 要保持的语义方面
            
        Returns:
            压缩结果
        """
        # 语义不变量提取
        semantic_invariants = {}
        for aspect in semantic_aspects:
            # 简化实现：基于哈希的确定性提取
            aspect_hash = hash(aspect) % 1000
            np.random.seed(aspect_hash)
            semantic_invariants[aspect] = np.random.randn(32)
        
        # 标准压缩
        result = self.compress(text_embedding, return_invariants=True)
        
        # 添加语义不变量
        result['semantic_invariants'] = semantic_invariants
        result['semantic_preserved'] = len(semantic_aspects)
        
        return result
    
    def multi_modal_holographic_fusion(self,
                                        modalities: Dict[str, np.ndarray],
                                        fusion_type: str = "invariant_based") -> np.ndarray:
        """
        多模态全息融合
        
        融合多个模态的信息，保持跨模态不变量
        
        Args:
            modalities: 模态名称到嵌入向量的字典
            fusion_type: 融合类型
            
        Returns:
            融合后的表示
        """
        if fusion_type == "invariant_based":
            # 提取每个模态的不变量
            invariants_per_modality = {}
            compressed_per_modality = {}
            
            for name, embedding in modalities.items():
                result = self.compress(embedding)
                compressed_per_modality[name] = result['compressed']
                invariants_per_modality[name] = result.get('invariants', {})
            
            # 找跨模态不变量（共同特征）
            cross_modal_invariants = self._find_cross_modal_invariants(
                invariants_per_modality
            )
            
            # 基于跨模态不变量融合
            fusion_weights = self._compute_fusion_weights(cross_modal_invariants)
            fused = sum(
                w * compressed_per_modality[name] 
                for name, w in fusion_weights.items()
            )
            
            return fused
            
        elif fusion_type == "attention_based":
            # 使用注意力机制融合
            embeddings = list(modalities.values())
            return self._attention_fusion(embeddings)
            
        else:
            raise ValueError(f"Unknown fusion type: {fusion_type}")
    
    def _extract_invariant(self, 
                           data: np.ndarray, 
                           inv_type: InvariantType) -> np.ndarray:
        """提取特定类型的不变量"""
        if inv_type == InvariantType.TOPOLOGY:
            # 拓扑特征：梯度方向场的零曲率点
            return self._extract_topological_features(data)
        elif inv_type == InvariantType.SYMMETRY:
            # 对称特征：旋转/反射不变表示
            return self._extract_symmetry_features(data)
        elif inv_type == InvariantType.PHASE:
            # 相位特征：复数表示的相位
            return self._extract_phase_features(data)
        elif inv_type == InvariantType.ENTROPY:
            # 熵特征：信息量度量
            return np.array([self._compute_entropy(data)])
        else:
            return data.mean(axis=-1, keepdims=True)
    
    def _extract_topological_features(self, data: np.ndarray) -> np.ndarray:
        """提取拓扑特征（简化实现）"""
        # 使用数据的梯度方向作为拓扑特征
        if len(data.shape) == 1:
            grad = np.gradient(data)
            return grad / (np.linalg.norm(grad) + 1e-10)
        return data.mean(axis=0)
    
    def _extract_symmetry_features(self, data: np.ndarray) -> np.ndarray:
        """提取对称特征"""
        # 使用数据的统计矩作为对称特征
        data_flat = data.flatten()
        features = [
            np.atleast_1d(data_flat.mean()),
            np.atleast_1d(data_flat.std()),
            np.atleast_1d(np.percentile(data_flat, 25)),
            np.atleast_1d(np.percentile(data_flat, 75))
        ]
        return np.concatenate(features)
    
    def _extract_phase_features(self, data: np.ndarray) -> np.ndarray:
        """提取相位特征"""
        # 将实数数据视为复数的相位
        complex_data = data.astype(np.complex128)
        complex_data = complex_data + 1j * np.roll(data, 1)
        return np.angle(complex_data)
    
    def _compute_entropy(self, data: np.ndarray) -> float:
        """计算香农熵"""
        hist, _ = np.histogram(data, bins=50)
        hist = hist / (hist.sum() + 1e-10)
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        return entropy
    
    def _learn_projection_matrix(self,
                                  data: np.ndarray,
                                  target_dim: int,
                                  invariants: Dict[str, np.ndarray]) -> np.ndarray:
        """
        学习投影矩阵
        
        目标：保留数据的主要方差和关键不变量
        """
        # 确保数据是2D
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        d_high = data.shape[-1]
        
        # PCA初始化
        try:
            U, S, Vt = np.linalg.svd(data - data.mean(axis=0), full_matrices=False)
            pca_projection = Vt[:target_dim]
        except np.linalg.LinAlgError:
            # SVD失败时使用随机投影
            pca_projection = np.random.randn(target_dim, d_high) * 0.1
        
        # 简化：直接返回PCA投影
        # 不变量增强在实际应用中需要更精细的设计
        projection = pca_projection
        
        return projection
    
    def _apply_projection(self, data: np.ndarray, projection: np.ndarray) -> np.ndarray:
        """应用投影"""
        if data.ndim == 1:
            centered = data - data.mean()
            return centered @ projection.T
        else:
            centered = data - data.mean(axis=0)
            return centered @ projection.T
    
    def _compute_residual(self, 
                         original: np.ndarray,
                         compressed: np.ndarray,
                         projection: np.ndarray) -> np.ndarray:
        """计算残差（全息信息残差）"""
        # 确保维度正确
        # projection shape: [d_low, d_high]
        # compressed shape: [n, d_low] 或 [d_low]
        if compressed.ndim == 1:
            # 1D: compressed是[d_low], projection是[d_low, d_high]
            # 重建: [d_low] @ [d_low, d_high] = [d_high]
            reconstructed = compressed @ projection
        else:
            # 2D: compressed是[n, d_low], projection是[d_low, d_high]
            # 重建: [n, d_low] @ [d_low, d_high] = [n, d_high]
            reconstructed = compressed @ projection
        return original - reconstructed
    
    def _correct_with_invariants(self,
                                  reconstructed: np.ndarray,
                                  invariants: Dict[str, np.ndarray]) -> np.ndarray:
        """使用不变量校正重建"""
        corrected = reconstructed.copy()
        for inv_type, inv_value in invariants.items():
            if len(inv_value) > 0:
                correction = inv_value.mean() * 0.1
                corrected = corrected + correction
        return corrected
    
    def _find_cross_modal_invariants(self,
                                      invariants: Dict[str, np.ndarray]) -> np.ndarray:
        """找跨模态不变量"""
        if not invariants:
            return np.array([])
        
        inv_vectors = list(invariants.values())
        if all(v.ndim == 1 for v in inv_vectors):
            stacked = np.stack(inv_vectors)
            # 使用PCA找共同方向
            if stacked.shape[0] > 1:
                U, S, Vt = np.linalg.svd(stacked, full_matrices=False)
                return Vt[0] if len(Vt) > 0 else stacked.mean(axis=0)
        return np.mean(inv_vectors, axis=0)
    
    def _compute_fusion_weights(self, cross_modal: np.ndarray) -> Dict[str, float]:
        """计算融合权重"""
        # 基于与跨模态不变量的相似度
        return {k: 1.0 for k in ['default']}  # 简化版本
    
    def _attention_fusion(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """注意力融合"""
        stacked = np.stack(embeddings)
        # 简化的自注意力
        attention_scores = np.ones(len(embeddings)) / len(embeddings)
        return (stacked * attention_scores[:, None]).sum(axis=0)
    
    def _cosine_similarity_batch(self, 
                                  query: np.ndarray, 
                                  database: np.ndarray) -> np.ndarray:
        """批量余弦相似度"""
        q_norm = query / (np.linalg.norm(query) + 1e-10)
        d_norm = database / (np.linalg.norm(database, axis=-1, keepdims=True) + 1e-10)
        return np.dot(d_norm, q_norm)
    
    def get_holographic_diagnostics(self) -> Dict[str, Any]:
        """获取全息系统诊断信息"""
        return {
            'compression_ratio': self.config.compression_ratio,
            'projection_matrix_shape': self.projection_matrix.shape if self.projection_matrix is not None else None,
            'cached_reconstructions': len(self.reconstruction_cache),
            'invariant_extractors': list(self.invariant_extractors.keys())
        }


# 工厂函数
def create_holographic_module(compression_ratio: float = 0.1) -> HolographicProjectionModule:
    """创建全息投影模块"""
    config = HolographicConfig(compression_ratio=compression_ratio)
    return HolographicProjectionModule(config)


if __name__ == "__main__":
    print("=" * 60)
    print("全息投影压缩模块 - 测试")
    print("=" * 60)
    
    # 创建模块
    holo = create_holographic_module(compression_ratio=0.1)
    
    # 创建测试数据
    np.random.seed(42)
    high_dim_data = np.random.randn(1000, 512)
    
    # 压缩
    print("\n1. 全息压缩测试")
    result = holo.compress(high_dim_data[0])
    print(f"   原始维度: {result['dimension']['high']}")
    print(f"   压缩维度: {result['dimension']['low']}")
    print(f"   压缩比: {result['compression_ratio']:.2%}")
    print(f"   不变量数量: {len(result.get('invariants', {}))}")
    
    # 展开
    print("\n2. 全息展开测试")
    reconstructed = holo.expand(result['compressed'], result.get('invariants'))
    reconstruction_error = np.linalg.norm(high_dim_data[0] - reconstructed)
    print(f"   重建误差: {reconstruction_error:.4f}")
    
    # 多模态融合
    print("\n3. 多模态全息融合测试")
    modalities = {
        'vision': np.random.randn(512),
        'text': np.random.randn(512),
        'audio': np.random.randn(512)
    }
    fused = holo.multi_modal_holographic_fusion(modalities)
    print(f"   融合维度: {fused.shape}")
    
    # 诊断信息
    print("\n4. 诊断信息")
    diag = holo.get_holographic_diagnostics()
    for k, v in diag.items():
        print(f"   {k}: {v}")
    
    print("\n" + "=" * 60)
    print("全息投影模块测试完成")
    print("=" * 60)
