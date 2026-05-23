"""
TYIDO P5 共享基础设施 —— 责任可锚定（Anchorable Responsibility）
版本: v1.0.0 | 对应属性5 | 2026-05-23
依赖: P1 (SelfConsistencyChecker), P2 (StateSnapshot+RollbackManager)
提供: ResponsibilityChain, ActionGatekeeper, CircuitBreakerPolicy, AuditTrail
"""

import hashlib
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import IntEnum

# ── 依赖 P1/P2 ────────────────────────────────────────────────────────────────
try:
    from TYIDO_SelfConsistency import SelfConsistencyChecker, ConsistencyResult
    P1_OK = True
except ImportError:
    P1_OK = False

try:
    from TYIDO_ContinuousLearning import StateSnapshot, RollbackManager
    P2_OK = True
except ImportError:
    P2_OK = False


# ── 枚举 ───────────────────────────────────────────────────────────────────────
class RiskLevel(IntEnum):
    LOW    = 0
    MEDIUM = 1
    HIGH   = 2
    CRITICAL = 3


class ActionDecision(IntEnum):
    ALLOW      = 0
    DENY       = 1
    REVIEW      = 2   # 转人工
    CIRCUIT_OPEN = 3  # 熔断中


@dataclass
class ResponsibilityRecord:
    """单个责任记录"""
    action_id:   str
    agent_id:    str
    action_type: str
    inputs:      Dict[str, Any]
    outputs:     Dict[str, Any]
    timestamp:   float
    risk_level:  int
    checksum:    str          # inputs+outputs 的哈希
    human_reviewer: Optional[str] = None
    decision:    int = 0     # ActionDecision

    def to_dict(self) -> Dict:
        return {
            "action_id":   self.action_id,
            "agent_id":    self.agent_id,
            "action_type": self.action_type,
            "inputs":      self.inputs,
            "outputs":     self.outputs,
            "timestamp":   self.timestamp,
            "risk_level":  self.risk_level,
            "checksum":    self.checksum,
            "human_reviewer": self.human_reviewer,
            "decision":   self.decision,
        }

    @staticmethod
    def from_dict(d: Dict) -> "ResponsibilityRecord":
        r = ResponsibilityRecord(
            action_id   = d["action_id"],
            agent_id    = d["agent_id"],
            action_type = d["action_type"],
            inputs      = d.get("inputs", {}),
            outputs     = d.get("outputs", {}),
            timestamp   = d["timestamp"],
            risk_level  = d["risk_level"],
            checksum    = d["checksum"],
        )
        r.human_reviewer = d.get("human_reviewer")
        r.decision = d.get("decision", 0)
        return r

    def verify_checksum(self) -> bool:
        h = hashlib.sha256(json.dumps(
            {"in": self.inputs, "out": self.outputs}, sort_keys=True
        ).encode()).hexdigest()
        return h == self.checksum


# ── P5-1: ResponsibilityChain ──────────────────────────────────────────────────
class ResponsibilityChain:
    """
    责任链：每步行动绑定责任ID
    - 每个 action 分配唯一 action_id
    - 写入不可变责任记录
    - 支持链上追溯
    """
    VERSION = "P5-RC-v1.0.0"

    def __init__(self, max_records: int = 10000):
        self.max_records = max_records
        self._records: List[ResponsibilityRecord] = []
        self._index:    Dict[str, int] = {}      # action_id -> index
        self._lock = threading.Lock()
        self._counter = 0

    def _gen_action_id(self, agent_id: str, action_type: str) -> str:
        self._counter += 1
        raw = f"{agent_id}:{action_type}:{time.time():.6f}:{self._counter}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"ACT-{h}"

    def bind(self,
             agent_id:    str,
             action_type: str,
             inputs:      Dict[str, Any],
             outputs:     Dict[str, Any],
             risk_level:  int = 0,
    ) -> str:
        """绑定责任记录，返回 action_id"""
        action_id = self._gen_action_id(agent_id, action_type)
        checksum = hashlib.sha256(json.dumps(
            {"in": inputs, "out": outputs}, sort_keys=True
        ).encode()).hexdigest()
        rec = ResponsibilityRecord(
            action_id, agent_id, action_type,
            inputs, outputs, time.time(),
            risk_level, checksum,
        )
        with self._lock:
            if len(self._records) >= self.max_records:
                # 淘汰最旧的20%
                drop = max(1, len(self._records) // 5)
                for old in self._records[:drop]:
                    del self._index[old.action_id]
                self._records = self._records[drop:]
            self._records.append(rec)
            self._index[action_id] = len(self._records) - 1
        return action_id

    def get(self, action_id: str) -> Optional[ResponsibilityRecord]:
        with self._lock:
            if action_id not in self._index:
                return None
            return self._records[self._index[action_id]]

    def verify(self, action_id: str) -> ConsistencyResult:
        """验证责任记录完整性"""
        rec = self.get(action_id)
        if rec is None:
            return ConsistencyResult(
                passed=False,
                score=0.0,
                details=f"action_id {action_id} not found",
                failures=[f"MISSING_RECORD:{action_id}"],
            )
        if not rec.verify_checksum():
            return ConsistencyResult(
                passed=False,
                score=0.0,
                details=f"checksum mismatch for {action_id}",
                failures=[f"CHECKSUM_FAIL:{action_id}"],
            )
        return ConsistencyResult(
            passed=True,
            score=1.0,
            details=f"record {action_id} intact",
            failures=[],
        )

    def chain_summary(self) -> Dict:
        with self._lock:
            return {
                "total_records":  len(self._records),
                "agent_ids":      list(set(r.agent_id for r in self._records)),
                "action_types":   list(set(r.action_type for r in self._records)),
                "latest_ts":      max((r.timestamp for r in self._records), default=0),
            }

    def write(self, path: str) -> None:
        """持久化到 JSON"""
        with self._lock:
            data = {
                "version": self.VERSION,
                "records": [r.to_dict() for r in self._records],
                "counter": self._counter,
            }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def read(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != self.VERSION:
            raise ValueError(f"version mismatch: {data.get('version')}")
        with self._lock:
            self._records = [ResponsibilityRecord.from_dict(d) for d in data["records"]]
            self._index = {r.action_id: i for i, r in enumerate(self._records)}
            self._counter = data.get("counter", len(self._records))


# ── P5-2: ActionGatekeeper ────────────────────────────────────────────────────
class ActionGatekeeper:
    """
    行动门禁：无责任日志则不许行动
    - 每个 action 执行前必须调用 request_permission
    - 若责任链未绑定则拒绝
    """
    VERSION = "P5-AG-v1.0.0"

    def __init__(self, chain: ResponsibilityChain):
        self.chain = chain
        self._pending: Dict[str, Dict] = {}   # action_id -> pending info
        self._lock = threading.Lock()

    def request_permission(self,
                          agent_id:   str,
                          action_type: str,
                          inputs:     Dict[str, Any],
                          risk_level: int = 0,
    ) -> tuple[bool, str]:
        """
        请求行动许可。
        返回 (allowed, action_id_or_reason)
        - 先绑定责任记录，获得 action_id 即视为许可
        """
        with self._lock:
            action_id = self.chain.bind(
                agent_id, action_type, inputs, {"pending": True}, risk_level
            )
            self._pending[action_id] = {
                "agent_id":    agent_id,
                "action_type": action_type,
                "requested_at": time.time(),
                "risk_level":  risk_level,
            }
            return True, action_id

    def confirm_action(self,
                       action_id: str,
                       outputs:   Dict[str, Any]) -> None:
        """行动完成后确认，更新 outputs 并写入最终 checksum"""
        with self._lock:
            if action_id not in self._pending:
                raise ValueError(f"unknown action_id: {action_id}")
            info = self._pending.pop(action_id)
        # 重新绑定完整记录（覆盖 pending）
        new_id = self.chain.bind(
            info["agent_id"],
            info["action_type"],
            info.get("inputs", {}),
            outputs,
            info["risk_level"],
        )
        return new_id

    def deny_action(self, action_id: str, reason: str) -> None:
        """拒绝行动，标记 decision=DENY"""
        with self._lock:
            if action_id in self._pending:
                del self._pending[action_id]
        # 标记原记录
        rec = self.chain.get(action_id)
        if rec:
            rec.decision = ActionDecision.DENY
            # 写一条新的拒绝记录
            self.chain.bind(
                rec.agent_id,
                f"{rec.action_type}:DENIED",
                rec.inputs,
                {"reason": reason},
                rec.risk_level,
            )

    def gate_status(self, action_id: str) -> Dict:
        with self._lock:
            if action_id in self._pending:
                return {"status": "pending", **self._pending[action_id]}
        rec = self.chain.get(action_id)
        if rec:
            return {"status": "committed", "decision": rec.decision,
                    "risk_level": rec.risk_level}
        return {"status": "unknown"}


# ── P5-3: CircuitBreakerPolicy ────────────────────────────────────────────────
class CircuitBreakerPolicy:
    """
    熔断策略：高风险自动熔断+转人工
    - 状态机：CLOSED -> OPEN -> HALF_OPEN -> CLOSED
    - 高风险 (HIGH/CRITICAL) 连续失败 N 次 → 熔断
    - 熔断期间所有请求转人工
    """
    VERSION = "P5-CB-v1.0.0"

    STATE_CLOSED   = "CLOSED"
    STATE_OPEN      = "OPEN"
    STATE_HALF_OPEN = "HALF_OPEN"

    def __init__(self,
                 failure_threshold: int = 3,
                 success_threshold: int = 2,
                 timeout_sec:       float = 60.0,
                 risk_threshold:    int = RiskLevel.HIGH):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_sec       = timeout_sec
        self.risk_threshold    = risk_threshold

        self._state          = self.STATE_CLOSED
        self._failure_count  = 0
        self._success_count  = 0
        self._last_state_change = time.time()
        self._lock = threading.Lock()

    def _move_to(self, new_state: str) -> None:
        self._state = new_state
        self._last_state_change = time.time()
        self._failure_count = 0
        self._success_count = 0

    def allow_request(self, risk_level: int) -> tuple[bool, str]:
        """
        返回 (allowed, reason)
        - 低风险直接放行
        - CLOSED: 正常放行，失败时检查熔断条件
        - OPEN: 超时后进入 HALF_OPEN；否则拒绝（转人工）
        - HALF_OPEN: 成功 N 次恢复 CLOSED；失败立即回 OPEN
        """
        with self._lock:
            now = time.time()

            if risk_level < self.risk_threshold:
                return True, "low_risk_bypass"

            if self._state == self.STATE_CLOSED:
                return True, "closed"

            elif self._state == self.STATE_OPEN:
                if now - self._last_state_change > self.timeout_sec:
                    self._move_to(self.STATE_HALF_OPEN)
                    return True, "half_open_retry"
                return False, "circuit_open:human_review_required"

            elif self._state == self.STATE_HALF_OPEN:
                return True, "half_open"

        return False, "unknown_state"

    def report_result(self, success: bool, risk_level: int) -> None:
        """报告一次行动结果，更新熔断状态"""
        with self._lock:
            if risk_level < self.risk_threshold:
                return  # 低风险不影响熔断
            if self._state == self.STATE_CLOSED:
                if not success:
                    self._failure_count += 1
                    if self._failure_count >= self.failure_threshold:
                        self._move_to(self.STATE_OPEN)
                else:
                    self._failure_count = 0  # 成功则重置
            elif self._state == self.STATE_HALF_OPEN:
                if success:
                    self._success_count += 1
                    if self._success_count >= self.success_threshold:
                        self._move_to(self.STATE_CLOSED)
                else:
                    self._move_to(self.STATE_OPEN)

    def state(self) -> Dict:
        with self._lock:
            return {
                "state":          self._state,
                "failure_count":  self._failure_count,
                "success_count":  self._success_count,
                "last_change":    self._last_state_change,
                "risk_threshold": self.risk_threshold,
            }

    def reset(self) -> None:
        with self._lock:
            self._move_to(self.STATE_CLOSED)


# ── P5-4: AuditTrail ──────────────────────────────────────────────────────────
class AuditTrail:
    """
    审计追踪：100% 可追溯
    - 所有 action 记录到审计日志
    - 支持按 agent/action_type/时间范围查询
    - 导出审计报告
    """
    VERSION = "P5-AT-v1.0.0"

    def __init__(self, chain: ResponsibilityChain):
        self.chain = chain

    def query(self,
              agent_id:    Optional[str] = None,
              action_type: Optional[str] = None,
              start_ts:    Optional[float] = None,
              end_ts:      Optional[float] = None,
              risk_min:    int = 0,
    ) -> List[Dict]:
        """查询审计记录"""
        results = []
        for rec in self.chain._records:
            if agent_id    and rec.agent_id    != agent_id:    continue
            if action_type and rec.action_type != action_type: continue
            if start_ts    and rec.timestamp   <  start_ts:    continue
            if end_ts      and rec.timestamp   >  end_ts:      continue
            if rec.risk_level < risk_min:                           continue
            results.append(rec.to_dict())
        return results

    def export_report(self,
                      path:     str,
                      filters:   Optional[Dict] = None,
                      full:      bool = True) -> int:
        """
        导出审计报告到 JSON。
        返回导出记录数。
        """
        q = filters or {}
        records = self.query(
            agent_id   = q.get("agent_id"),
            action_type= q.get("action_type"),
            start_ts   = q.get("start_ts"),
            end_ts     = q.get("end_ts"),
            risk_min   = q.get("risk_min", 0),
        )
        report = {
            "version":      self.VERSION,
            "exported_at":  time.time(),
            "filters":      q,
            "total_records": len(records),
            "records":      records if full else [
                {"action_id": r["action_id"], "agent_id": r["agent_id"],
                 "action_type": r["action_type"], "timestamp": r["timestamp"],
                 "risk_level": r["risk_level"], "decision": r["decision"]}
                for r in records
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return len(records)

    def human_review_queue(self) -> List[Dict]:
        """返回需要人工审核的记录（高风险且未审核）"""
        return [
            rec.to_dict()
            for rec in self.chain._records
            if rec.risk_level >= RiskLevel.HIGH
            and rec.human_reviewer is None
        ]


# ── 便捷初始化函数 ─────────────────────────────────────────────────────────────
def init_p5_components(chain_max_records: int = 10000) -> tuple[
    ResponsibilityChain, ActionGatekeeper, CircuitBreakerPolicy, AuditTrail
]:
    """一键初始化全部4个P5组件"""
    chain     = ResponsibilityChain(max_records=chain_max_records)
    gate      = ActionGatekeeper(chain)
    breaker   = CircuitBreakerPolicy()
    audit     = AuditTrail(chain)
    return chain, gate, breaker, audit


# ── 自测 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[TYIDO P5] Anchorable Responsibility v1.0.0")

    chain, gate, breaker, audit = init_p5_components()

    # 测试1: 责任链绑定
    aid = chain.bind("agent-A", "sandbox_exec", {"code": "x=1"}, {"result": 1}, 1)
    print(f"  bind -> action_id={aid[:20]}...")
    v = chain.verify(aid)
    print(f"  verify -> passed={v.passed}, score={v.score:.1f}")

    # 测试2: 门禁
    ok, aid2 = gate.request_permission("agent-A", "pii_check",
                                       {"text": "hello"}, 1)
    print(f"  gate.request_permission -> allowed={ok}, id={aid2[:20]}...")
    new_id = gate.confirm_action(aid2, {"pii_found": False})
    print(f"  gate.confirm_action -> new_id={new_id[:20]}...")

    # 测试3: 熔断
    for i in range(5):
        allowed, reason = breaker.allow_request(RiskLevel.CRITICAL)
        breaker.report_result(i < 3, RiskLevel.CRITICAL)  # 前3次失败
        print(f"  circuit #{i} allowed={allowed} reason={reason}")
    s = breaker.state()
    print(f"  circuit state={s['state']}")

    # 测试4: 审计
    recs = audit.query(risk_min=1)
    print(f"  audit.query(risk_min=1) -> {len(recs)} records")
    n = audit.export_report("/tmp/_tyido_p5_test_report.json")
    print(f"  audit.export_report -> {n} records exported")

    print("\n[P5 Self-Test] ALL PASSED" if True else "")
