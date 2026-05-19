# -*- coding: utf-8 -*-
"""
模块34：DIKWP数据层（D层）
原始数据证据溯源，带哈希指纹 + 审计轨迹

来源：太乙AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13
"""

import hashlib
import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum


class DIKWPLayer(Enum):
    """DIKWP六层枚举"""
    D = "Data"
    I = "Information"
    K = "Knowledge"
    W = "Wisdom"
    P = "Purpose"
    R = "Reliability"


@dataclass
class DataRecord:
    """D层：原始数据记录，带来源和哈希指纹"""
    id: str
    content: str
    source: str          # 数据来源（URL/传感器/用户输入）
    timestamp: float
    hash: str = field(init=False)
    confidence: float = 1.0
    metadata: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """计算内容哈希（防篡改）"""
        content = f"{self.content}{self.source}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def verify_integrity(self) -> bool:
        """验证数据完整性"""
        return self.hash == self._compute_hash()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "tags": self.tags
        }


class DIKWPDataLayer:
    """
    模块34：DIKWP D层 - 原始数据证据溯源
    
    弹簧虫对应：每个方块（Agent）的原始物理状态
    IGCTR对应：微视界感知总线
    
    核心功能：
    1. ingest() - 摄入原始数据，自动生成哈希指纹
    2. verify_integrity() - 验证数据完整性（防篡改）
    3. get_audit_trail() - 返回完整的数据审计轨迹
    4. query() - 按条件查询数据记录
    """
    
    def __init__(self):
        self.records: Dict[str, DataRecord] = {}
        self.audit_log: List[Dict] = []
        self._counter = 0
    
    def ingest(self, content: str, source: str, 
               confidence: float = 1.0,
               metadata: Dict = None,
               tags: List[str] = None) -> DataRecord:
        """
        摄入原始数据，自动生成哈希指纹
        
        Args:
            content: 原始内容
            source: 数据来源（URL/传感器/用户输入）
            confidence: 置信度 [0, 1]
            metadata: 额外元数据
            tags: 标签列表
        
        Returns:
            DataRecord: 新创建的数据记录
        """
        self._counter += 1
        record_id = f"D_{int(time.time()*1000)}_{self._counter:04d}"
        
        record = DataRecord(
            id=record_id,
            content=content,
            source=source,
            timestamp=time.time(),
            confidence=confidence,
            metadata=metadata or {},
            tags=tags or []
        )
        
        self.records[record_id] = record
        self._add_audit_entry("ingest", record_id, record.hash)
        
        return record
    
    def ingest_batch(self, items: List[Dict]) -> List[DataRecord]:
        """
        批量摄入原始数据
        
        Args:
            items: [{"content": ..., "source": ..., "confidence": ...}, ...]
        
        Returns:
            List[DataRecord]: 创建的记录列表
        """
        results = []
        for item in items:
            record = self.ingest(
                content=item.get("content", ""),
                source=item.get("source", "unknown"),
                confidence=item.get("confidence", 1.0),
                metadata=item.get("metadata"),
                tags=item.get("tags")
            )
            results.append(record)
        return results
    
    def verify_integrity(self, record_id: str) -> bool:
        """
        验证数据完整性（防篡改）
        
        Args:
            record_id: 数据记录ID
        
        Returns:
            bool: 完整性是否通过验证
        """
        if record_id not in self.records:
            return False
        return self.records[record_id].verify_integrity()
    
    def verify_all(self) -> Dict[str, bool]:
        """
        验证所有数据记录的完整性
        
        Returns:
            Dict[str, bool]: {record_id: 是否有效}
        """
        return {
            rid: record.verify_integrity() 
            for rid, record in self.records.items()
        }
    
    def get_record(self, record_id: str) -> Optional[DataRecord]:
        """获取指定数据记录"""
        return self.records.get(record_id)
    
    def get_audit_trail(self, limit: int = None) -> List[Dict]:
        """
        返回完整的数据审计轨迹
        
        Args:
            limit: 限制返回条数（最近N条）
        
        Returns:
            List[Dict]: 审计轨迹列表
        """
        if limit:
            return self.audit_log[-limit:]
        return self.audit_log.copy()
    
    def query(self, 
              keyword: str = None,
              source: str = None,
              min_confidence: float = None,
              tags: List[str] = None,
              since: float = None) -> List[DataRecord]:
        """
        按条件查询数据记录
        
        Args:
            keyword: 内容关键词
            source: 数据来源
            min_confidence: 最低置信度
            tags: 标签列表（需全部匹配）
            since: 时间戳下限
        
        Returns:
            List[DataRecord]: 匹配的记录列表
        """
        results = []
        for record in self.records.values():
            # 关键词过滤
            if keyword and keyword.lower() not in record.content.lower():
                continue
            
            # 来源过滤
            if source and source != record.source:
                continue
            
            # 置信度过滤
            if min_confidence and record.confidence < min_confidence:
                continue
            
            # 标签过滤
            if tags and not all(t in record.tags for t in tags):
                continue
            
            # 时间过滤
            if since and record.timestamp < since:
                continue
            
            results.append(record)
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取数据层统计信息"""
        records = list(self.records.values())
        return {
            "total_records": len(records),
            "avg_confidence": sum(r.confidence for r in records) / max(len(records), 1),
            "by_source": self._group_by_source(records),
            "by_tag": self._group_by_tags(records),
            "integrity_rate": sum(1 for r in records if r.verify_integrity()) / max(len(records), 1),
            "audit_entries": len(self.audit_log)
        }
    
    def _group_by_source(self, records: List[DataRecord]) -> Dict[str, int]:
        """按来源分组统计"""
        sources = {}
        for r in records:
            sources[r.source] = sources.get(r.source, 0) + 1
        return sources
    
    def _group_by_tags(self, records: List[DataRecord]) -> Dict[str, int]:
        """按标签分组统计"""
        tags = {}
        for r in records:
            for t in r.tags:
                tags[t] = tags.get(t, 0) + 1
        return tags
    
    def _add_audit_entry(self, action: str, record_id: str, hash_value: str):
        """添加审计日志条目"""
        self.audit_log.append({
            "action": action,
            "record_id": record_id,
            "hash": hash_value,
            "timestamp": time.time()
        })
    
    def export_audit_log(self, filepath: str):
        """导出审计日志到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, ensure_ascii=False, indent=2)
    
    def __len__(self) -> int:
        return len(self.records)
    
    def __repr__(self) -> str:
        return f"DIKWPDataLayer(records={len(self.records)}, audit_entries={len(self.audit_log)})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("模块34：DIKWP数据层（D层）测试")
    print("=" * 60)
    
    # 1. 创建数据层实例
    data_layer = DIKWPDataLayer()
    print(f"\n✓ 创建数据层: {data_layer}")
    
    # 2. 摄入数据
    record1 = data_layer.ingest(
        content="太乙AGI 6.0升级方案核心是DIKWP六层语义治理",
        source="user_input",
        confidence=0.95,
        tags=["AGI", "DIKWP", "治理"]
    )
    print(f"\n✓ 摄入数据记录: {record1.id}")
    print(f"  - 内容: {record1.content[:30]}...")
    print(f"  - 哈希: {record1.hash}")
    print(f"  - 置信度: {record1.confidence}")
    
    # 3. 批量摄入
    batch = [
        {"content": "弹簧虫论文提出三大定理", "source": "research", "tags": ["弹簧虫"]},
        {"content": "哥德尔机实现自指升级", "source": "research", "tags": ["哥德尔"]},
        {"content": "Lean证明接口形式化验证", "source": "formal", "tags": ["Lean"]}
    ]
    records = data_layer.ingest_batch(batch)
    print(f"\n✓ 批量摄入: {len(records)} 条记录")
    
    # 4. 验证完整性
    is_valid = data_layer.verify_integrity(record1.id)
    print(f"\n✓ 完整性验证: {is_valid}")
    
    # 5. 查询
    results = data_layer.query(source="research")
    print(f"\n✓ 查询结果(source=research): {len(results)} 条")
    
    # 6. 统计信息
    stats = data_layer.get_statistics()
    print(f"\n✓ 统计信息:")
    print(f"  - 总记录数: {stats['total_records']}")
    print(f"  - 平均置信度: {stats['avg_confidence']:.2f}")
    print(f"  - 完整性率: {stats['integrity_rate']:.1%}")
    
    # 7. 审计轨迹
    audit = data_layer.get_audit_trail(limit=3)
    print(f"\n✓ 审计轨迹(最近3条): {len(audit)} 条")
    
    print("\n" + "=" * 60)
    print("模块34测试完成 ✓")
    print("=" * 60)
