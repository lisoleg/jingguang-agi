# -*- coding: utf-8 -*-
"""
模块38：DIKWP目的层（P层）
IntentGuard意图门禁 + 目的漂移检测

来源：太乙AGI 6.0升级方案（基于12文档深度分析）
作者：基于高见远指令实现
日期：2026-05-13
"""

import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum


@dataclass
class PurposeLock:
    """
    P层：目的锁定记录
    
    弹簧虫类比：宏观目的（前进/运输）不被碰撞破坏
    哥德尔机类比：目标G编码为不可变公理
    """
    session_id: str
    declared_purpose: str
    authorized_scopes: List[str]    # 授权的行动范围
    timestamp: float
    active: bool = True
    drift_count: int = 0           # 漂移次数
    drift_score: float = 0.0        # 当前漂移分数
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "declared_purpose": self.declared_purpose,
            "authorized_scopes": self.authorized_scopes,
            "timestamp": self.timestamp,
            "active": self.active,
            "drift_count": self.drift_count,
            "drift_score": self.drift_score,
            "metadata": self.metadata
        }


@dataclass
class IntentCheckResult:
    """意图检查结果"""
    allowed: bool
    reason: str
    alignment_score: float
    scope_matched: bool
    purpose_hash: str
    
    def to_dict(self) -> Dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "alignment_score": self.alignment_score,
            "scope_matched": self.scope_matched,
            "purpose_hash": self.purpose_hash
        }


class DIKWPPurposeLayer:
    """
    模块38：DIKWP P层 - 目的约束（IntentGuard升级）
    
    弹簧虫对应：宏观目的（前进/运输）不被碰撞破坏
    哥德尔机对应：目标G编码为不可变公理
    DIKWP对应：Intent闭环
    
    核心功能：
    1. lock_purpose() - 锁定会话目的
    2. intent_guard() - 意图门禁（任何工具调用前必须通过）
    3. detect_purpose_drift() - 目的漂移检测
    4. set_global_purpose() - 设置全局目的向量（弹簧虫质心守恒）
    """
    
    # 默认授权范围
    DEFAULT_SCOPES = [
        "read",       # 读取操作
        "write",      # 写入操作
        "execute",    # 执行操作
        "external",   # 外部调用
        "delete",     # 删除操作
        "admin"       # 管理操作
    ]
    
    def __init__(self):
        self.purpose_locks: Dict[str, PurposeLock] = {}
        self.global_purpose_vector: Optional[Dict] = None  # 弹簧虫质心（全局目标）
        self.intent_checks: List[IntentCheckResult] = []
        self.drift_threshold: float = 0.3  # 目的漂移阈值
        self._session_counter = 0
    
    def lock_purpose(self, 
                     session_id: str,
                     purpose: str,
                     scopes: List[str] = None,
                     metadata: Dict = None) -> PurposeLock:
        """
        锁定会话目的
        
        Args:
            session_id: 会话ID
            purpose: 声明的目的
            scopes: 授权的行动范围
            metadata: 额外元数据
        
        Returns:
            PurposeLock: 目的锁定记录
        """
        if session_id in self.purpose_locks:
            # 更新现有锁定
            lock = self.purpose_locks[session_id]
            lock.declared_purpose = purpose
            lock.authorized_scopes = scopes or self.DEFAULT_SCOPES
            lock.active = True
            lock.drift_count = 0
            lock.drift_score = 0.0
        else:
            # 创建新锁定
            lock = PurposeLock(
                session_id=session_id,
                declared_purpose=purpose,
                authorized_scopes=scopes or self.DEFAULT_SCOPES,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            self.purpose_locks[session_id] = lock
        
        return lock
    
    def intent_guard(self, 
                     session_id: str, 
                     proposed_action: str,
                     action_scope: str) -> IntentCheckResult:
        """
        意图门禁：执行任何工具/动作前的目的一致性检查
        
        这是P层的核心前置检查，任何工具调用前必须通过。
        
        Args:
            session_id: 会话ID
            proposed_action: 提议的行动
            action_scope: 行动范围（read/write/execute/external/delete/admin）
        
        Returns:
            IntentCheckResult: 检查结果
        """
        # 检查会话是否已锁定目的
        if session_id not in self.purpose_locks:
            result = IntentCheckResult(
                allowed=False,
                reason="未声明目的，拒绝执行",
                alignment_score=0.0,
                scope_matched=False,
                purpose_hash=""
            )
            self.intent_checks.append(result)
            return result
        
        lock = self.purpose_locks[session_id]
        
        # 检查锁定是否激活
        if not lock.active:
            result = IntentCheckResult(
                allowed=False,
                reason="目的锁定已失效",
                alignment_score=0.0,
                scope_matched=False,
                purpose_hash=self._hash_purpose(lock.declared_purpose)
            )
            self.intent_checks.append(result)
            return result
        
        # 检查范围授权
        scope_matched = action_scope in lock.authorized_scopes
        
        if not scope_matched:
            result = IntentCheckResult(
                allowed=False,
                reason=f"行动范围 '{action_scope}' 未在授权范围内: {lock.authorized_scopes}",
                alignment_score=0.1,
                scope_matched=False,
                purpose_hash=self._hash_purpose(lock.declared_purpose)
            )
            self.intent_checks.append(result)
            return result
        
        # 计算目的一致性得分
        alignment_score = self._compute_alignment(proposed_action, lock)
        
        # 检查漂移
        drift_result = self.detect_purpose_drift(session_id, [proposed_action])
        
        if drift_result["drifted"]:
            result = IntentCheckResult(
                allowed=False,
                reason=f"检测到目的漂移（漂移分数: {drift_result['drift_score']:.2f}）",
                alignment_score=alignment_score,
                scope_matched=True,
                purpose_hash=self._hash_purpose(lock.declared_purpose)
            )
        else:
            result = IntentCheckResult(
                allowed=True,
                reason="目的一致性验证通过",
                alignment_score=alignment_score,
                scope_matched=True,
                purpose_hash=self._hash_purpose(lock.declared_purpose)
            )
        
        self.intent_checks.append(result)
        return result
    
    def _compute_alignment(self, action: str, lock: PurposeLock) -> float:
        """
        计算行动与声明目的的对齐度
        
        简单实现：基于关键词重叠
        复杂实现：可用embedding余弦相似度
        """
        purpose_words = set(lock.declared_purpose.lower().split())
        action_words = set(action.lower().split())
        
        # 计算交集
        overlap = purpose_words & action_words
        
        if not purpose_words:
            return 0.5
        
        # Jaccard相似度
        score = len(overlap) / len(purpose_words | action_words)
        
        # 如果action包含purpose的关键词，加分
        if overlap:
            score = max(score, len(overlap) / len(purpose_words))
        
        return min(score, 1.0)
    
    def _hash_purpose(self, purpose: str) -> str:
        """计算目的哈希"""
        return hashlib.sha256(purpose.encode()).hexdigest()[:16]
    
    def detect_purpose_drift(self, 
                           session_id: str,
                           actual_actions: List[str]) -> Dict:
        """
        目的漂移检测：监控实际执行路径与声明目的的偏差
        
        弹簧虫类比：质心是否偏离预期轨迹
        
        Args:
            session_id: 会话ID
            actual_actions: 实际执行的动作列表
        
        Returns:
            Dict: {"drifted": bool, "drift_score": float, "drift_count": int}
        """
        if session_id not in self.purpose_locks:
            return {"drifted": True, "drift_score": 1.0, "drift_count": 0}
        
        lock = self.purpose_locks[session_id]
        
        # 计算漂移分数
        drift_score = 0.0
        for action in actual_actions:
            # 检查action是否在授权范围内
            scope_matched = any(scope in action.lower() for scope in lock.authorized_scopes)
            
            if not scope_matched:
                # 不在授权范围内，视为漂移
                drift_score += 0.2
            else:
                # 在授权范围内，但检查关键词重叠
                action_words = set(action.lower().split())
                purpose_words = set(lock.declared_purpose.lower().split())
                overlap = action_words & purpose_words
                
                if not overlap:
                    # 无关键词重叠，轻微漂移
                    drift_score += 0.1
        
        drift_score = min(drift_score, 1.0)
        
        # 更新漂移记录
        lock.drift_score = drift_score
        if drift_score > self.drift_threshold:
            lock.drift_count += 1
        
        return {
            "drifted": drift_score > self.drift_threshold,
            "drift_score": drift_score,
            "drift_count": lock.drift_count,
            "threshold": self.drift_threshold
        }
    
    def set_global_purpose(self, 
                          purpose_vector: Dict,
                          description: str = None):
        """
        设置全局目的向量（弹簧虫质心守恒定理工程化）
        
        全局目标一旦锁定，不被单次冲击破坏。
        多个会话的目的形成"质心"，偏离质心的会话被标记。
        
        Args:
            purpose_vector: 全局目的向量
            description: 目的描述
        """
        self.global_purpose_vector = {
            "vector": purpose_vector,
            "description": description or "Global Purpose",
            "timestamp": time.time(),
            "active_sessions": 0
        }
        
        # 更新活跃会话数
        self.global_purpose_vector["active_sessions"] = sum(
            1 for lock in self.purpose_locks.values() if lock.active
        )
    
    def check_global_consistency(self, session_id: str) -> Dict:
        """
        检查会话与全局目的的一致性
        
        Args:
            session_id: 会话ID
        
        Returns:
            Dict: 一致性检查结果
        """
        if not self.global_purpose_vector:
            return {"consistent": None, "reason": "全局目的未设置"}
        
        if session_id not in self.purpose_locks:
            return {"consistent": False, "reason": "会话未锁定目的"}
        
        lock = self.purpose_locks[session_id]
        global_vec = self.global_purpose_vector["vector"]
        
        # 简化的向量一致性检查
        local_words = set(lock.declared_purpose.lower().split())
        global_words = set(str(global_vec).lower().split())
        
        overlap = local_words & global_words
        consistency = len(overlap) / max(len(local_words | global_words), 1)
        
        return {
            "consistent": consistency > 0.3,
            "consistency_score": consistency,
            "overlap": list(overlap)
        }
    
    def unlock_purpose(self, session_id: str, reason: str = None) -> bool:
        """
        解锁目的（会话结束或用户主动终止）
        
        Args:
            session_id: 会话ID
            reason: 解锁原因
        
        Returns:
            bool: 是否成功
        """
        if session_id in self.purpose_locks:
            self.purpose_locks[session_id].active = False
            self.purpose_locks[session_id].metadata["unlock_reason"] = reason or "normal_end"
            return True
        return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """获取会话状态"""
        if session_id not in self.purpose_locks:
            return None
        
        lock = self.purpose_locks[session_id]
        return {
            "active": lock.active,
            "purpose": lock.declared_purpose,
            "scopes": lock.authorized_scopes,
            "drift_score": lock.drift_score,
            "drift_count": lock.drift_count,
            "global_consistency": self.check_global_consistency(session_id)
        }
    
    def get_statistics(self) -> Dict:
        """获取目的层统计信息"""
        active_locks = [l for l in self.purpose_locks.values() if l.active]
        return {
            "total_sessions": len(self.purpose_locks),
            "active_sessions": len(active_locks),
            "global_purpose_set": self.global_purpose_vector is not None,
            "total_checks": len(self.intent_checks),
            "recent_checks": len(self.intent_checks[-100:]),
            "allow_rate": sum(1 for c in self.intent_checks[-100:] if c.allowed) / max(len(self.intent_checks[-100:]), 1),
            "drift_threshold": self.drift_threshold,
            "active_scopes": list(set(s for l in active_locks for s in l.authorized_scopes))
        }
    
    def export_locks(self, filepath: str):
        """导出会话锁定状态"""
        data = {
            "locks": {sid: lock.to_dict() for sid, lock in self.purpose_locks.items()},
            "global_purpose": self.global_purpose_vector,
            "export_time": time.time()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def __repr__(self) -> str:
        active = sum(1 for l in self.purpose_locks.values() if l.active)
        return f"DIKWPPurposeLayer(sessions={len(self.purpose_locks)}, active={active})"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块38：DIKWP目的层（P层）测试")
    print("=" * 60)
    
    # 1. 创建目的层实例
    purpose_layer = DIKWPPurposeLayer()
    print(f"\n✓ 创建目的层: {purpose_layer}")
    
    # 2. 锁定会话目的
    session_id = "session_001"
    lock = purpose_layer.lock_purpose(
        session_id=session_id,
        purpose="分析太乙AGI架构并生成升级方案",
        scopes=["read", "write", "execute"],
        metadata={"user": "高见远", "project": "CompositeAGI"}
    )
    print(f"\n✓ 锁定目的:")
    print(f"  会话: {lock.session_id}")
    print(f"  目的: {lock.declared_purpose}")
    print(f"  授权范围: {lock.authorized_scopes}")
    
    # 3. 意图门禁测试
    print(f"\n✓ 意图门禁测试:")
    
    test_actions = [
        ("读取相关文档", "read", True),
        ("分析文档内容", "read", True),
        ("执行代码生成", "execute", True),
        ("调用外部API", "external", False),  # 未授权
        ("删除文件", "delete", False),       # 未授权
    ]
    
    for action, scope, expected_allowed in test_actions:
        result = purpose_layer.intent_guard(session_id, action, scope)
        status = "✓" if result.allowed == expected_allowed else "✗"
        print(f"  {status} [{scope}] {action}")
        print(f"     允许: {result.allowed}, 原因: {result.reason}")
        print(f"     对齐度: {result.alignment_score:.2f}")
    
    # 4. 目的漂移检测
    print(f"\n✓ 目的漂移检测:")
    
    drift_actions = [
        "读取文档",
        "写代码实现功能",
        "测试代码",
        "发送邮件给团队",  # 可能的漂移
        "浏览新闻"         # 明显漂移
    ]
    
    drift_result = purpose_layer.detect_purpose_drift(session_id, drift_actions)
    print(f"  漂移检测结果:")
    print(f"    是否漂移: {drift_result['drifted']}")
    print(f"    漂移分数: {drift_result['drift_score']:.2f}")
    print(f"    漂移次数: {drift_result['drift_count']}")
    print(f"    阈值: {drift_result['threshold']}")
    
    # 5. 全局目的一致性
    print(f"\n✓ 全局目的一致性:")
    purpose_layer.set_global_purpose(
        purpose_vector={"AGI": 1.0, "研究": 0.8, "升级": 0.7},
        description="太乙AGI研究项目"
    )
    
    consistency = purpose_layer.check_global_consistency(session_id)
    print(f"  会话与全局目的一致性:")
    print(f"    一致: {consistency['consistent']}")
    print(f"    一致性得分: {consistency['consistency_score']:.2f}")
    print(f"    重叠词: {consistency['overlap']}")
    
    # 6. 会话状态
    print(f"\n✓ 会话状态:")
    status = purpose_layer.get_session_status(session_id)
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 7. 统计信息
    print(f"\n✓ 统计信息:")
    stats = purpose_layer.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("模块38测试完成 ✓")
    print("=" * 60)
