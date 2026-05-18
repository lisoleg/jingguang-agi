"""
vector_db.py - 简单向量数据库

实现基于内存的向量存储和相似度检索。
用于替代规则引擎的部分功能，实现基于向量的知识表示和检索。

核心功能：
1. 向量存储：存储文本及其向量表示
2. 相似度计算：余弦相似度、欧氏距离
3. 最近邻检索：根据查询向量找到最相似的记录
4. 知识管理：添加、删除、更新知识条目
"""

import math
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json


class VectorDB:
    """简单向量数据库"""
    
    def __init__(self, dimension: int = 128):
        """
        初始化向量数据库
        
        Args:
            dimension: 向量维度（默认128，简单文本使用小维度）
        """
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}  # id -> vector
        self.data: Dict[str, Dict] = {}  # id -> metadata
        self.text_index: Dict[str, str] = {}  # text_hash -> id
        self.index_counter = 0
    
    def _hash_text(self, text: str) -> str:
        """计算文本的哈希值作为索引"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    def _simple_encode(self, text: str) -> List[float]:
        """
        简单文本编码（替代真实embedding）
        基于字符频率和n-gram特征生成向量
        """
        vector = [0.0] * self.dimension
        
        if not text:
            return vector
        
        text_lower = text.lower()
        
        # 特征1：字符频率（前64维）
        char_freq = {}
        for char in text_lower:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        for char, freq in char_freq.items():
            idx = hash(char) % (self.dimension // 2)
            vector[idx] = min(freq / len(text), 1.0)
        
        # 特征2：词频特征（后64维）
        words = text_lower.split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        for word, freq in word_freq.items():
            idx = (self.dimension // 2) + (hash(word) % (self.dimension // 2))
            vector[idx] = min(freq / len(words), 1.0)
        
        # 归一化
        norm = math.sqrt(sum(v**2 for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def add(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        添加文本到向量数据库
        
        Args:
            text: 文本内容
            metadata: 附加元数据
        
        Returns:
            添加的记录ID
        """
        text_hash = self._hash_text(text)
        
        # 检查是否已存在
        if text_hash in self.text_index:
            return self.text_index[text_hash]
        
        # 生成ID
        record_id = f"vec_{self.index_counter}"
        self.index_counter += 1
        
        # 编码文本
        vector = self._simple_encode(text)
        
        # 存储
        self.vectors[record_id] = vector
        self.data[record_id] = {
            "text": text,
            "metadata": metadata or {},
            "timestamp": self._get_timestamp()
        }
        self.text_index[text_hash] = record_id
        
        return record_id
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索最相似的文本
        
        Args:
            query: 查询文本
            top_k: 返回最相似的前k个结果
        
        Returns:
            相似结果列表，每个结果包含id、text、score等信息
        """
        if not self.vectors:
            return []
        
        query_vector = self._simple_encode(query)
        
        # 计算相似度
        similarities = []
        for record_id, vector in self.vectors.items():
            score = self._cosine_similarity(query_vector, vector)
            similarities.append((record_id, score))
        
        # 排序取top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:top_k]
        
        # 格式化结果
        results = []
        for record_id, score in top_results:
            results.append({
                "id": record_id,
                "text": self.data[record_id]["text"],
                "score": score,
                "metadata": self.data[record_id]["metadata"]
            })
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a**2 for a in vec1))
        norm2 = math.sqrt(sum(b**2 for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """计算欧氏距离"""
        if len(vec1) != len(vec2):
            return float('inf')
        
        distance = math.sqrt(sum((a - b)**2 for a, b in zip(vec1, vec2)))
        return distance
    
    def get(self, record_id: str) -> Optional[Dict]:
        """根据ID获取记录"""
        if record_id not in self.data:
            return None
        
        return {
            "id": record_id,
            "vector": self.vectors.get(record_id),
            **self.data[record_id]
        }
    
    def delete(self, record_id: str) -> bool:
        """删除记录"""
        if record_id not in self.data:
            return False
        
        # 从text_index中删除
        text = self.data[record_id]["text"]
        text_hash = self._hash_text(text)
        if text_hash in self.text_index:
            del self.text_index[text_hash]
        
        # 删除数据
        del self.vectors[record_id]
        del self.data[record_id]
        
        return True
    
    def update(self, record_id: str, text: Optional[str] = None, 
               metadata: Optional[Dict] = None) -> bool:
        """更新记录"""
        if record_id not in self.data:
            return False
        
        # 如果文本更新，需要重新编码
        if text is not None:
            old_text = self.data[record_id]["text"]
            old_hash = self._hash_text(old_text)
            if old_hash in self.text_index:
                del self.text_index[old_hash]
            
            new_hash = self._hash_text(text)
            self.text_index[new_hash] = record_id
            
            self.vectors[record_id] = self._simple_encode(text)
            self.data[record_id]["text"] = text
        
        # 更新元数据
        if metadata is not None:
            self.data[record_id]["metadata"] = metadata
        
        return True
    
    def size(self) -> int:
        """返回数据库大小"""
        return len(self.data)
    
    def clear(self) -> None:
        """清空数据库"""
        self.vectors.clear()
        self.data.clear()
        self.text_index.clear()
        self.index_counter = 0
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import time
        return str(time.time())
    
    def export_to_json(self, filepath: str) -> bool:
        """导出到JSON文件"""
        try:
            export_data = {
                "dimension": self.dimension,
                "records": []
            }
            
            for record_id in self.data:
                export_data["records"].append({
                    "id": record_id,
                    "vector": self.vectors.get(record_id, []),
                    **self.data[record_id]
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except:
            return False
    
    def import_from_json(self, filepath: str) -> int:
        """从JSON文件导入"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            self.clear()
            self.dimension = import_data.get("dimension", 128)
            
            count = 0
            for record in import_data.get("records", []):
                record_id = record["id"]
                self.vectors[record_id] = record.get("vector", [])
                self.data[record_id] = {
                    "text": record.get("text", ""),
                    "metadata": record.get("metadata", {}),
                    "timestamp": record.get("timestamp", "")
                }
                
                text_hash = self._hash_text(self.data[record_id]["text"])
                self.text_index[text_hash] = record_id
                
                # 更新计数器
                if record_id.startswith("vec_"):
                    try:
                        num = int(record_id.split("_")[1])
                        self.index_counter = max(self.index_counter, num + 1)
                    except:
                        pass
                
                count += 1
            
            return count
        except:
            return 0


# 示例用法
if __name__ == "__main__":
    # 创建向量数据库
    db = VectorDB(dimension=64)
    
    # 添加知识
    db.add("人工智能是计算机科学的一个分支", {"category": "definition"})
    db.add("机器学习是人工智能的子集", {"category": "relationship"})
    db.add("深度学习使用神经网络", {"category": "technology"})
    db.add("AGI是通用人工智能", {"category": "definition"})
    
    # 搜索
    results = db.search("什么是人工智能", top_k=3)
    print("搜索结果：")
    for r in results:
        print(f"  - {r['text']} (相似度: {r['score']:.3f})")
    
    print(f"\n数据库大小: {db.size()}")
