"""
TYIDO Property 2: 持续学习（可回写）基础设施
================================================

提供所有模块共享的回滚和灾难性遗忘防护能力：

1. StateSnapshot: 状态快照（deep copy + timestamp + checksum）
2. RollbackManager: 回滚管理器（快照栈 + 回滚 + 前进）
3. ForgettingGuard: 灾难性遗忘防护（知识稳定性监控 + 核心知识保护）
4. LearningRecord: 学习记录（增量式知识更新追踪）

设计原则：
- 快照基于 deep copy，确保完全独立
- 核心知识标记为 protected，回滚和学习均不可覆盖
- 灾难性遗忘检测：比较新旧状态的关键指标偏差
"""

from __future__ import annotations

import copy
import time
import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable, Set


# ============================================================
# 状态快照
# ============================================================

@dataclass
class StateSnapshot:
    """
    状态快照 — 在特定时间点保存的完整模块状态

    属性:
        snapshot_id: 唯一快照ID（SHA256前8位）
        timestamp: 创建时间戳
        state_data: 完整状态数据的深拷贝
        checksum: 状态数据的校验和（用于验证完整性）
        description: 快照描述
        is_protected: 是否为受保护快照（核心知识）
        key_metrics: 关键指标签名（用于遗忘检测）
    """
    snapshot_id: str
    timestamp: float
    state_data: Dict[str, Any]
    checksum: str
    description: str = ""
    is_protected: bool = False
    key_metrics: Dict[str, float] = field(default_factory=dict)

    @staticmethod
    def create(
        state_data: Dict[str, Any],
        description: str = "",
        is_protected: bool = False,
        key_metrics: Optional[Dict[str, float]] = None
    ) -> "StateSnapshot":
        """创建快照（自动生成ID、时间戳和校验和）"""
        # 深拷贝确保独立
        frozen = copy.deepcopy(state_data)

        # 校验和
        raw = json.dumps(frozen, sort_keys=True, default=str, ensure_ascii=False)
        checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]

        # ID
        id_raw = f"{time.time()}_{checksum}_{description}"
        snapshot_id = hashlib.sha256(id_raw.encode()).hexdigest()[:8]

        return StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            state_data=frozen,
            checksum=checksum,
            description=description,
            is_protected=is_protected,
            key_metrics=key_metrics or {}
        )

    def verify_integrity(self) -> bool:
        """验证快照数据完整性"""
        raw = json.dumps(self.state_data, sort_keys=True, default=str, ensure_ascii=False)
        current_checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return current_checksum == self.checksum


# ============================================================
# 回滚管理器
# ============================================================

class RollbackManager:
    """
    回滚管理器 — 管理状态快照栈，支持回滚/前进操作

    特性:
        - 快照栈: 最多保留 max_snapshots 个快照
        - 回滚: 弹出最新快照，恢复状态
        - 前进: 回滚后可以前进到之前的状态
        - 受保护快照: 不可被自动清理
    """

    def __init__(self, max_snapshots: int = 50):
        self.max_snapshots = max_snapshots
        self._snapshot_stack: List[StateSnapshot] = []
        self._undo_stack: List[StateSnapshot] = []  # 回滚后暂存，支持前进
        self._rollback_count: int = 0
        self._forward_count: int = 0

    def save_snapshot(
        self,
        state_data: Dict[str, Any],
        description: str = "",
        is_protected: bool = False,
        key_metrics: Optional[Dict[str, float]] = None
    ) -> StateSnapshot:
        """
        保存当前状态快照

        返回:
            StateSnapshot: 已保存的快照
        """
        snapshot = StateSnapshot.create(
            state_data, description, is_protected, key_metrics
        )
        self._snapshot_stack.append(snapshot)
        self._undo_stack.clear()  # 新操作清空前进栈

        # 超过上限时清理（保留受保护快照）
        self._cleanup()

        return snapshot

    def rollback(self) -> Optional[StateSnapshot]:
        """
        回滚到上一个快照

        返回:
            StateSnapshot 或 None（无可回滚的快照）
        """
        if len(self._snapshot_stack) < 2:
            return None

        # 保留一个当前状态到 undo 栈
        current = self._snapshot_stack.pop()
        self._undo_stack.append(current)

        self._rollback_count += 1
        return self._snapshot_stack[-1]

    def forward(self) -> Optional[StateSnapshot]:
        """
        前进到下一个状态（仅在回滚后可用）

        返回:
            StateSnapshot 或 None
        """
        if not self._undo_stack:
            return None

        snapshot = self._undo_stack.pop()
        self._snapshot_stack.append(snapshot)

        self._forward_count += 1
        return snapshot

    def get_current(self) -> Optional[StateSnapshot]:
        """获取当前（最新）快照"""
        return self._snapshot_stack[-1] if self._snapshot_stack else None

    def get_snapshot_history(self) -> List[Dict[str, Any]]:
        """获取快照历史摘要"""
        return [
            {
                'id': s.snapshot_id,
                'timestamp': s.timestamp,
                'description': s.description,
                'is_protected': s.is_protected,
                'metrics': s.key_metrics
            }
            for s in self._snapshot_stack
        ]

    def _cleanup(self):
        """清理超过上限的非保护快照"""
        while len(self._snapshot_stack) > self.max_snapshots:
            # 从最旧的非保护快照开始清理
            removed = False
            for i, s in enumerate(self._snapshot_stack):
                if not s.is_protected:
                    self._snapshot_stack.pop(i)
                    removed = True
                    break
            if not removed:
                break  # 全是保护快照，停止清理

    def get_state(self) -> Dict[str, Any]:
        """获取回滚管理器状态"""
        return {
            'total_snapshots': len(self._snapshot_stack),
            'protected_snapshots': sum(1 for s in self._snapshot_stack if s.is_protected),
            'rollback_count': self._rollback_count,
            'forward_count': self._forward_count,
            'can_rollback': len(self._snapshot_stack) >= 2,
            'can_forward': len(self._undo_stack) > 0,
            'history': self.get_snapshot_history()[-10:]  # 最近10条
        }


# ============================================================
# 灾难性遗忘防护
# ============================================================

@dataclass
class ForgettingAlert:
    """
    遗忘警报 — 当检测到潜在灾难性遗忘时生成
    """
    alert_type: str          # 'drift', 'sudden_change', 'critical_loss'
    severity: float          # 0.0-1.0
    metric_name: str         # 哪个指标
    old_value: float
    new_value: float
    change_ratio: float      # 变化比率
    threshold: float         # 触发阈值
    description: str = ""
    timestamp: float = field(default_factory=time.time)


class ForgettingGuard:
    """
    灾难性遗忘防护 — 监控学习过程中的知识稳定性

    核心机制:
        1. 关键指标漂移检测: 比较新状态与基线快照的指标偏差
        2. 突变检测: 单次更新导致指标剧烈变化
        3. 核心知识保护: 标记为 protected 的知识不可被覆盖
        4. 遗忘分数: 综合评估遗忘风险（0=安全, 1=严重遗忘）
    """

    def __init__(
        self,
        drift_threshold: float = 0.3,
        sudden_change_threshold: float = 0.5,
        protected_keys: Optional[Set[str]] = None
    ):
        self.drift_threshold = drift_threshold
        self.sudden_change_threshold = sudden_change_threshold
        self.protected_keys = protected_keys or set()

        self._baseline_metrics: Dict[str, float] = {}
        self._alerts: List[ForgettingAlert] = []
        self._learning_events: List[Dict] = []
        self._total_checks: int = 0
        self._alert_count: int = 0

    def set_baseline(self, metrics: Dict[str, float]):
        """
        设置基线指标（通常在系统初始化或核心知识学习后调用）

        参数:
            metrics: 关键指标字典，如 {'accuracy': 0.95, 'coverage': 0.8}
        """
        self._baseline_metrics = copy.deepcopy(metrics)

    def check_forgetting(
        self,
        current_metrics: Dict[str, float],
        previous_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        检测灾难性遗忘风险

        参数:
            current_metrics: 当前状态的指标
            previous_metrics: 前一个状态的指标（用于突变检测）

        返回:
            dict: {
                'forgetting_risk': float,      # 综合遗忘风险 0-1
                'drift_scores': dict,           # 各指标漂移分数
                'alerts': list,                 # 警报列表
                'protected_intact': bool        # 核心知识是否完好
            }
        """
        self._total_checks += 1

        # 如果未设置基线，跳过漂移检测（初始化阶段）
        if not self._baseline_metrics:
            return {
                'forgetting_risk': 0.0,
                'drift_scores': {},
                'alerts': [],
                'protected_intact': True,
                'tyido_p2_verdict': 'PASS'
            }

        drift_scores = {}
        alerts = []
        max_drift = 0.0

        # 1. 基线漂移检测
        for key, current_val in current_metrics.items():
            if key not in self._baseline_metrics:
                continue

            baseline_val = self._baseline_metrics[key]
            if abs(baseline_val) < 1e-10:
                continue  # 避免除零

            drift = abs(current_val - baseline_val) / max(abs(baseline_val), 1e-10)
            drift_scores[key] = round(drift, 4)
            max_drift = max(max_drift, drift)

            # 检查是否超过漂移阈值
            if drift > self.drift_threshold:
                alert = ForgettingAlert(
                    alert_type='drift',
                    severity=round(min(1.0, drift), 4),
                    metric_name=key,
                    old_value=baseline_val,
                    new_value=current_val,
                    change_ratio=round(drift, 4),
                    threshold=self.drift_threshold,
                    description=f"指标 {key} 偏离基线 {drift:.2%} (阈值: {self.drift_threshold:.0%})"
                )
                alerts.append(alert)
                self._alerts.append(alert)

        # 2. 突变检测（与前一状态比较）
        if previous_metrics:
            for key, current_val in current_metrics.items():
                if key not in previous_metrics:
                    continue

                prev_val = previous_metrics[key]
                if abs(prev_val) < 1e-10:
                    continue

                change = abs(current_val - prev_val) / max(abs(prev_val), 1e-10)

                if change > self.sudden_change_threshold:
                    alert = ForgettingAlert(
                        alert_type='sudden_change',
                        severity=round(min(1.0, change), 4),
                        metric_name=key,
                        old_value=prev_val,
                        new_value=current_val,
                        change_ratio=round(change, 4),
                        threshold=self.sudden_change_threshold,
                        description=f"指标 {key} 突变 {change:.2%} (阈值: {self.sudden_change_threshold:.0%})"
                    )
                    alerts.append(alert)
                    self._alerts.append(alert)

        # 3. 核心知识保护检查
        protected_intact = True
        for key in self.protected_keys:
            if key in current_metrics and key in self._baseline_metrics:
                if current_metrics[key] != self._baseline_metrics[key]:
                    protected_intact = False
                    alert = ForgettingAlert(
                        alert_type='critical_loss',
                        severity=1.0,
                        metric_name=key,
                        old_value=self._baseline_metrics[key],
                        new_value=current_metrics[key],
                        change_ratio=1.0,
                        threshold=0.0,
                        description=f"核心知识 {key} 被修改！"
                    )
                    alerts.append(alert)
                    self._alerts.append(alert)

        # 4. 综合遗忘风险
        forgetting_risk = min(1.0, max_drift) if drift_scores else 0.0
        if alerts:
            max_severity = max(a.severity for a in alerts)
            forgetting_risk = max(forgetting_risk, max_severity)

        self._alert_count += len(alerts)

        return {
            'forgetting_risk': round(forgetting_risk, 4),
            'drift_scores': drift_scores,
            'alerts': [
                {
                    'type': a.alert_type,
                    'severity': a.severity,
                    'metric': a.metric_name,
                    'description': a.description
                }
                for a in alerts
            ],
            'protected_intact': protected_intact,
            'tyido_p2_verdict': 'PASS' if forgetting_risk < self.drift_threshold and protected_intact else 'NEED_ATTENTION'
        }

    def record_learning_event(self, event: Dict[str, Any]):
        """
        记录学习事件

        参数:
            event: {
                'type': str,           # 'update', 'new_knowledge', 'merge', etc.
                'description': str,
                'metrics_before': dict,
                'metrics_after': dict,
                'source': str
            }
        """
        event['timestamp'] = time.time()
        self._learning_events.append(event)

    def get_learning_trajectory(self) -> List[Dict[str, Any]]:
        """获取学习轨迹"""
        return self._learning_events[-20:]  # 最近20条

    def get_alert_history(self) -> List[Dict[str, Any]]:
        """获取警报历史"""
        return [
            {
                'type': a.alert_type,
                'severity': a.severity,
                'metric': a.metric_name,
                'description': a.description,
                'timestamp': a.timestamp
            }
            for a in self._alerts[-20:]
        ]

    def get_state(self) -> Dict[str, Any]:
        """获取防护器状态"""
        return {
            'total_checks': self._total_checks,
            'total_alerts': self._alert_count,
            'protected_keys': list(self.protected_keys),
            'baseline_metrics': self._baseline_metrics,
            'recent_alerts': self.get_alert_history()[-5:],
            'learning_events_count': len(self._learning_events)
        }


# ============================================================
# 学习记录
# ============================================================

@dataclass
class LearningRecord:
    """
    学习记录 — 增量式知识更新追踪

    记录每次学习操作的输入、输出、影响范围和验证结果。
    """
    record_id: str
    timestamp: float
    operation: str          # 'add', 'update', 'merge', 'delete', 'rollback'
    target: str             # 操作目标（模块/组件名）
    before_state: Dict[str, Any] = field(default_factory=dict)
    after_state: Dict[str, Any] = field(default_factory=dict)
    delta_metrics: Dict[str, float] = field(default_factory=dict)
    forgetting_risk: float = 0.0
    verified: bool = False
    description: str = ""

    @staticmethod
    def create(
        operation: str,
        target: str,
        before_state: Optional[Dict] = None,
        after_state: Optional[Dict] = None,
        description: str = ""
    ) -> "LearningRecord":
        id_raw = f"{time.time()}_{operation}_{target}"
        record_id = hashlib.sha256(id_raw.encode()).hexdigest()[:8]

        # 计算变化量
        delta = {}
        if before_state and after_state:
            for key in set(list(before_state.keys()) + list(after_state.keys())):
                b = before_state.get(key, 0)
                a = after_state.get(key, 0)
                if isinstance(b, (int, float)) and isinstance(a, (int, float)):
                    delta[key] = round(a - b, 6)

        return LearningRecord(
            record_id=record_id,
            timestamp=time.time(),
            operation=operation,
            target=target,
            before_state=before_state or {},
            after_state=after_state or {},
            delta_metrics=delta,
            description=description
        )


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TYIDO Property 2: 持续学习基础设施 自测")
    print("=" * 60)

    # 1. 测试 StateSnapshot
    print("\n--- StateSnapshot ---")
    data = {"accuracy": 0.95, "count": 42, "items": [1, 2, 3]}
    snap = StateSnapshot.create(data, description="test_snapshot", key_metrics={"accuracy": 0.95})
    print(f"Snapshot ID: {snap.snapshot_id}")
    print(f"Integrity: {snap.verify_integrity()}")
    snap.state_data["accuracy"] = 0.0  # 修改副本不影响原数据
    print(f"After tampering, original still: {data['accuracy']}")

    # 2. 测试 RollbackManager
    print("\n--- RollbackManager ---")
    rm = RollbackManager(max_snapshots=5)
    for i in range(3):
        rm.save_snapshot({"step": i, "value": i * 10}, description=f"step_{i}")
    print(f"Snapshots: {len(rm._snapshot_stack)}")
    current = rm.get_current()
    print(f"Current: {current.state_data}")
    rolled = rm.rollback()
    print(f"After rollback: {rolled.state_data}")
    fwd = rm.forward()
    print(f"After forward: {fwd.state_data}")
    print(f"Manager state: {rm.get_state()}")

    # 3. 测试 ForgettingGuard
    print("\n--- ForgettingGuard ---")
    guard = ForgettingGuard(
        drift_threshold=0.3,
        protected_keys={"core_accuracy"}
    )
    guard.set_baseline({"accuracy": 0.95, "coverage": 0.8, "core_accuracy": 1.0})

    # 正常学习
    result1 = guard.check_forgetting({"accuracy": 0.93, "coverage": 0.82, "core_accuracy": 1.0})
    print(f"Normal learning: risk={result1['forgetting_risk']}, verdict={result1['tyido_p2_verdict']}")

    # 灾难性遗忘
    result2 = guard.check_forgetting({"accuracy": 0.3, "coverage": 0.1, "core_accuracy": 0.5})
    print(f"Catastrophic: risk={result2['forgetting_risk']}, verdict={result2['tyido_p2_verdict']}")
    print(f"  Alerts: {len(result2['alerts'])}")
    for a in result2['alerts']:
        print(f"    [{a['type']}] {a['description']}")

    # 4. 测试 LearningRecord
    print("\n--- LearningRecord ---")
    lr = LearningRecord.create(
        "update", "M63_EML",
        before_state={"coupling_count": 10},
        after_state={"coupling_count": 15},
        description="新增5次耦合"
    )
    print(f"Record: {lr.record_id}, delta: {lr.delta_metrics}")

    print("\n" + "=" * 60)
    print("TYIDO Property 2 基础设施 自测完成")
    print("=" * 60)
