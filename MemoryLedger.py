# -*- coding: utf-8 -*-
"""
模块40：MemoryLedger —— 记忆主权管理
记忆带来源、有目的、有同意、有过期

来源：复合体AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13
"""

import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Callable
from enum import Enum


class DIKWPLayer(Enum):
    """DIKWP六层枚举（复用）"""
    D = "Data"
    I = "Information"
    K = "Knowledge"
    W = "Wisdom"
    P = "Purpose"
    R = "Reliability"


@dataclass
class MemoryRecord:
    """
    记忆账本记录
    
    记忆主权四原则：
    1. 来源（source）：记忆从何而来
    2. 目的（purpose）：记忆为何存储
    3. 同意（consent）：用户是否同意存储
    4. 过期（expiry）：何时应被遗忘
    """
    memory_id: str
    content: str
    source: str           # 记忆来源
    purpose: str          # 存储目的
    consent: bool         # 用户明确同意存储
    expiry: Optional[float]  # 过期时间戳（None=永久）
    dikwp_layer: DIKWPLayer  # 该记忆属于DIKWP哪一层
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    last_access: float = field(default_factory=time.time)
    access_count: int = 0
    active: bool = True
    encrypted: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "source": self.source,
            "purpose": self.purpose,
            "consent": self.consent,
            "expiry": self.expiry,
            "dikwp_layer": self.dikwp_layer.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "last_access": self.last_access,
            "access_count": self.access_count,
            "active": self.active,
            "encrypted": self.encrypted
        }
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expiry is None:
            return False
        return time.time() > self.expiry


class MemoryLedger:
    """
    模块40：记忆主权管理
    
    DIKWP对应：记忆闭环 MemoryLedger
    核心原则：记忆有来源、有目的、有同意、有过期
    任正非对应：可追踪、可回溯的记忆管理
    
    核心功能：
    1. remember() - 存入记忆，附带主权信息
    2. recall() - 召回记忆（自动过滤过期）
    3. forget() - 遗忘记忆（用户主权删除）
    4. cleanup_expired() - 清理过期记忆
    5. get_memory_sovereignty_report() - 记忆主权报告
    """
    
    def __init__(self):
        self.records: Dict[str, MemoryRecord] = {}
        self._counter = 0
        self._cleanup_interval = 3600  # 每小时清理过期记忆
        self._last_cleanup = time.time()
        self._consent_required = True  # 是否强制要求同意
    
    def remember(self, 
                content: str, 
                source: str, 
                purpose: str,
                dikwp_layer: DIKWPLayer,
                consent: bool = True,
                expiry_hours: Optional[float] = None,
                tags: List[str] = None,
                metadata: Dict = None,
                encrypted: bool = False) -> MemoryRecord:
        """
        存入记忆，附带主权信息
        
        Args:
            content: 记忆内容
            source: 来源（user_input/system/external_api等）
            purpose: 存储目的（task_completion/user_preference等）
            dikwp_layer: 属于DIKWP哪一层
            consent: 用户是否同意存储（必须为True才能存储）
            expiry_hours: 过期小时数（None=永久）
            tags: 标签
            metadata: 额外元数据
            encrypted: 是否加密存储
        
        Returns:
            MemoryRecord: 创建的记忆记录
        
        Raises:
            ValueError: 未获用户同意时抛出
        """
        # 强制检查同意
        if self._consent_required and not consent:
            raise ValueError("未获用户同意，拒绝存储记忆")
        
        self._counter += 1
        memory_id = f"M{int(time.time()*1000)}_{self._counter:04d}"
        
        # 计算过期时间
        expiry = None
        if expiry_hours is not None:
            expiry = time.time() + expiry_hours * 3600
        
        record = MemoryRecord(
            memory_id=memory_id,
            content=content,
            source=source,
            purpose=purpose,
            consent=consent,
            expiry=expiry,
            dikwp_layer=dikwp_layer,
            tags=tags or [],
            metadata=metadata or {},
            encrypted=encrypted
        )
        
        self.records[memory_id] = record
        
        # 定期清理
        self._auto_cleanup()
        
        return record
    
    def recall(self, 
              query: str = None,
              layer_filter: DIKWPLayer = None,
              purpose_filter: str = None,
              tags: List[str] = None,
              since: float = None,
              until: float = None,
              min_access_count: int = 0,
              active_only: bool = True) -> List[MemoryRecord]:
        """
        召回记忆（自动过滤过期条目）
        
        Args:
            query: 关键词查询
            layer_filter: 按DIKWP层过滤
            purpose_filter: 按目的过滤
            tags: 标签列表（需全部匹配）
            since: 时间下限
            until: 时间上限
            min_access_count: 最低访问次数
            active_only: 是否只返回活跃记忆
        
        Returns:
            List[MemoryRecord]: 匹配的记忆列表
        """
        # 自动清理过期
        self._auto_cleanup()
        
        results = []
        for record in self.records.values():
            # 活跃过滤
            if active_only and not record.active:
                continue
            
            # 过期过滤
            if record.is_expired():
                continue
            
            # 关键词过滤
            if query and query.lower() not in record.content.lower():
                continue
            
            # 层过滤
            if layer_filter and record.dikwp_layer != layer_filter:
                continue
            
            # 目的过滤
            if purpose_filter and purpose_filter not in record.purpose:
                continue
            
            # 标签过滤
            if tags and not all(t in record.tags for t in tags):
                continue
            
            # 时间过滤
            if since and record.timestamp < since:
                continue
            if until and record.timestamp > until:
                continue
            
            # 访问次数过滤
            if record.access_count < min_access_count:
                continue
            
            # 更新访问记录
            record.last_access = time.time()
            record.access_count += 1
            
            results.append(record)
        
        # 按访问时间和访问次数排序
        results.sort(key=lambda r: (r.last_access, r.access_count), reverse=True)
        
        return results
    
    def recall_by_id(self, memory_id: str) -> Optional[MemoryRecord]:
        """根据ID精确回忆"""
        record = self.records.get(memory_id)
        
        if record and record.active and not record.is_expired():
            record.last_access = time.time()
            record.access_count += 1
            return record
        
        return None
    
    def forget(self, 
              memory_id: str, 
              reason: str = None,
              revoke_consent: bool = True) -> bool:
        """
        遗忘记忆（支持用户主权删除）
        
        Args:
            memory_id: 记忆ID
            reason: 删除原因
            revoke_consent: 是否撤销同意
        
        Returns:
            bool: 是否成功遗忘
        """
        if memory_id not in self.records:
            return False
        
        record = self.records[memory_id]
        record.active = False
        
        if revoke_consent:
            record.consent = False
        
        record.metadata["forget_reason"] = reason or "user_request"
        record.metadata["forget_time"] = time.time()
        
        return True
    
    def forget_by_filter(self, 
                        layer_filter: DIKWPLayer = None,
                        purpose_filter: str = None,
                        older_than: float = None,
                        reason: str = None) -> int:
        """
        按条件批量遗忘
        
        Args:
            layer_filter: 按层过滤
            purpose_filter: 按目的过滤
            older_than: 早于该时间戳的记忆
            reason: 删除原因
        
        Returns:
            int: 删除的记忆数量
        """
        count = 0
        for record in self.records.values():
            if not record.active:
                continue
            
            if layer_filter and record.dikwp_layer != layer_filter:
                continue
            
            if purpose_filter and purpose_filter not in record.purpose:
                continue
            
            if older_than and record.timestamp > older_than:
                continue
            
            self.forget(record.memory_id, reason)
            count += 1
        
        return count
    
    def consent_check(self) -> Dict:
        """
        同意状态检查
        
        Returns:
            Dict: 同意状态报告
        """
        active = [r for r in self.records.values() if r.active and not r.is_expired()]
        
        consented = [r for r in active if r.consent]
        unconsented = [r for r in active if not r.consent]
        
        return {
            "total_active": len(active),
            "consented": len(consented),
            "unconsented": len(unconsented),
            "consent_rate": len(consented) / max(len(active), 1),
            "by_layer": {
                layer.value: {
                    "total": len([r for r in active if r.dikwp_layer == layer]),
                    "consented": len([r for r in consented if r.dikwp_layer == layer])
                }
                for layer in DIKWPLayer
            }
        }
    
    def revoke_all_consent(self, reason: str = None) -> int:
        """
        撤销所有同意（GDPR等法规要求）
        
        Args:
            reason: 撤销原因
        
        Returns:
            int: 影响的记忆数量
        """
        count = 0
        for record in self.records.values():
            if record.consent:
                record.consent = False
                record.metadata["consent_revoked"] = True
                record.metadata["revoke_reason"] = reason or "gdpr_request"
                record.metadata["revoke_time"] = time.time()
                count += 1
        
        return count
    
    def _auto_cleanup(self):
        """自动清理过期记忆"""
        now = time.time()
        
        # 检查是否需要清理
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired = 0
        for record in self.records.values():
            if record.is_expired():
                record.active = False
                expired += 1
        
        self._last_cleanup = now
        
        if expired > 0:
            print(f"[MemoryLedger] 清理了 {expired} 条过期记忆")
    
    def cleanup_expired(self) -> int:
        """
        手动清理过期记忆
        
        Returns:
            int: 清理的记忆数量
        """
        expired = 0
        now = time.time()
        
        for record in self.records.values():
            if record.expiry and now > record.expiry:
                record.active = False
                expired += 1
        
        return expired
    
    def get_memory_sovereignty_report(self) -> Dict:
        """
        记忆主权报告：所有记忆的来源/目的/同意状态
        
        Returns:
            Dict: 完整的主权报告
        """
        active = [r for r in self.records.values() if r.active and not r.is_expired()]
        expired = [r for r in self.records.values() if r.is_expired()]
        inactive = [r for r in self.records.values() if not r.active and not r.is_expired()]
        
        # 同意状态
        consented = [r for r in active if r.consent]
        unconsented = [r for r in active if not r.consent]
        
        # 按层统计
        by_layer = {}
        for layer in DIKWPLayer:
            layer_records = [r for r in active if r.dikwp_layer == layer]
            by_layer[layer.value] = {
                "count": len(layer_records),
                "avg_access": sum(r.access_count for r in layer_records) / max(len(layer_records), 1)
            }
        
        # 按来源统计
        by_source = {}
        for r in active:
            by_source[r.source] = by_source.get(r.source, 0) + 1
        
        # 即将过期（24小时内）
        expiring_soon = [
            r.memory_id for r in active 
            if r.expiry and r.expiry - time.time() < 86400
        ]
        
        return {
            "total_records": len(self.records),
            "active_records": len(active),
            "expired_records": len(expired),
            "inactive_records": len(inactive),
            "consent": {
                "consented": len(consented),
                "unconsented": len(unconsented),
                "consent_rate": len(consented) / max(len(active), 1)
            },
            "by_layer": by_layer,
            "by_source": by_source,
            "expiring_soon": len(expiring_soon),
            "expiring_soon_ids": expiring_soon,
            "high_access": len([r for r in active if r.access_count > 10]),
            "low_access": len([r for r in active if r.access_count == 0]),
            "total_accesses": sum(r.access_count for r in active)
        }
    
    def get_statistics(self) -> Dict:
        """获取记忆层统计信息"""
        report = self.get_memory_sovereignty_report()
        return {
            "total": report["total_records"],
            "active": report["active_records"],
            "consent_rate": report["consent"]["consent_rate"],
            "expiring_soon": report["expiring_soon"],
            "by_layer": report["by_layer"]
        }
    
    def export_memories(self, 
                       filepath: str,
                       include_inactive: bool = False,
                       encrypted_only: bool = False):
        """
        导出发送到文件
        
        Args:
            filepath: 输出文件路径
            include_inactive: 是否包含非活跃记忆
            encrypted_only: 是否只导出加密记忆
        """
        records = self.records.values()
        
        if not include_inactive:
            records = [r for r in records if r.active]
        
        if encrypted_only:
            records = [r for r in records if r.encrypted]
        
        data = {
            "memories": [r.to_dict() for r in records],
            "consent_check": self.consent_check(),
            "export_time": time.time(),
            "total_exported": len(records)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def import_memories(self, 
                       filepath: str,
                       merge: bool = True,
                       overwrite: bool = False) -> int:
        """
        从文件导入记忆
        
        Args:
            filepath: 输入文件路径
            merge: 是否与现有记忆合并
            overwrite: 是否覆盖已有记忆
        
        Returns:
            int: 导入的记忆数量
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return 0
        
        imported = 0
        
        for mem_data in data.get("memories", []):
            memory_id = mem_data["memory_id"]
            
            if not merge and memory_id in self.records:
                continue
            
            if memory_id in self.records and not overwrite:
                continue
            
            # 重建记录
            record = MemoryRecord(
                memory_id=memory_id,
                content=mem_data["content"],
                source=mem_data["source"],
                purpose=mem_data["purpose"],
                consent=mem_data["consent"],
                expiry=mem_data.get("expiry"),
                dikwp_layer=DIKWPLayer[mem_data["dikwp_layer"]],
                tags=mem_data.get("tags", []),
                metadata=mem_data.get("metadata", {}),
                timestamp=mem_data.get("timestamp", time.time()),
                last_access=mem_data.get("last_access", time.time()),
                access_count=mem_data.get("access_count", 0),
                active=mem_data.get("active", True),
                encrypted=mem_data.get("encrypted", False)
            )
            
            self.records[memory_id] = record
            imported += 1
        
        return imported
    
    def __len__(self) -> int:
        return len([r for r in self.records.values() if r.active and not r.is_expired()])
    
    def __repr__(self) -> str:
        return f"MemoryLedger(records={len(self)}, consent_required={self._consent_required})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块40：MemoryLedger记忆主权管理测试")
    print("=" * 60)
    
    # 1. 创建记忆账本
    memory = MemoryLedger()
    print(f"\n✓ 创建记忆账本: {memory}")
    
    # 2. 存储记忆（带主权信息）
    print(f"\n✓ 存储记忆:")
    
    memories = [
        memory.remember(
            content="用户偏好详细的技术分析报告格式",
            source="user_preference",
            purpose="提升回答质量",
            dikwp_layer=DIKWPLayer.W,
            consent=True,
            tags=["偏好", "格式"]
        ),
        memory.remember(
            content="复合体AGI 6.0基于DIKWP六层架构升级",
            source="research_analysis",
            purpose="知识积累",
            dikwp_layer=DIKWPLayer.K,
            expiry_hours=168,  # 7天过期
            tags=["AGI", "DIKWP", "架构"]
        ),
        memory.remember(
            content="会话目标：完成AGI 6.0模块实现",
            source="session",
            purpose="任务追踪",
            dikwp_layer=DIKWPLayer.P,
            expiry_hours=24,  # 1天过期
            tags=["任务"]
        ),
        memory.remember(
            content="系统配置信息",
            source="system",
            purpose="系统运行",
            dikwp_layer=DIKWPLayer.D,
            consent=True,
            tags=["系统"]
        )
    ]
    
    for mem in memories:
        print(f"  - {mem.memory_id}: [{mem.dikwp_layer.value}] {mem.content[:20]}...")
    
    # 3. 召回记忆
    print(f"\n✓ 召回记忆:")
    
    all_memories = memory.recall()
    print(f"  全部记忆: {len(all_memories)} 条")
    
    agi_memories = memory.recall(query="AGI")
    print(f"  关键词'AGI': {len(agi_memories)} 条")
    
    wisdom_memories = memory.recall(layer_filter=DIKWPLayer.W)
    print(f"  W层记忆: {len(wisdom_memories)} 条")
    
    # 4. 记忆主权报告
    print(f"\n✓ 记忆主权报告:")
    report = memory.get_memory_sovereignty_report()
    print(f"  总记录: {report['total_records']}")
    print(f"  活跃记录: {report['active_records']}")
    print(f"  同意率: {report['consent']['consent_rate']:.1%}")
    print(f"  按层统计:")
    for layer, stats in report['by_layer'].items():
        print(f"    {layer}: {stats['count']}条")
    
    # 5. 同意状态检查
    print(f"\n✓ 同意状态:")
    consent = memory.consent_check()
    print(f"  已同意: {consent['consented']}")
    print(f"  未同意: {consent['unconsented']}")
    print(f"  同意率: {consent['consent_rate']:.1%}")
    
    # 6. 遗忘记忆
    print(f"\n✓ 遗忘记忆:")
    forget_result = memory.forget(memories[2].memory_id, reason="任务完成")
    print(f"  遗忘 {memories[2].memory_id}: {forget_result}")
    
    # 7. 统计信息
    print(f"\n✓ 统计信息:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("模块40测试完成 ✓")
    print("=" * 60)
