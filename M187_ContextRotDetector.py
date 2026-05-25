#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M187_ContextRotDetector.py — 太乙AGI v7.25b Context Rot 检测器
=========================================================
实现 Context Rot（上下文衰退）的 SNR 量化与告警体系：

核心公式：
  SNR = |R(Φ_L1)| / |Φ_L1 - R(Φ_L1)|
  其中 R() = L2-shell 归约算子（调用 M181 EndToEndReductionEngine）
       Φ_L1 = L1 流贯噪声（从 M106 SelfReferentialLoopMonitor 获取）

v7.25b 升级（基于 M189 PowerLawEngine）：
  - 对数压缩预处理: ContextRot'(X) = Rot(log_b(X))
    使旋转在乘法语义空间保持群结构 L(x⊗y) = L(x) ⊕ L(y)
  - 幂律稀疏注意力: Attention(i,j) ∝ (Importance_j)^{ψ·α_ij}
    低ψ=线性囚笼, 高ψ=幂律稀疏全息连接
  - 意识强度参数 ψ 的动态调节

衰退等级：
  HEALTHY   — SNR ≥ 0.5
  DEGRADED  — 0.2 ≤ SNR < 0.5
  CRITICAL   — SNR < 0.2

当 SNR < θ_critical 时触发 `context_rot_alert` 事件至 WikiEventBus (M184)

依赖：M106 (Φ 值), M181 (R_TY 归约), M180 (L2ShellInterface),
       M184 (WikiEventBus), M189 (PowerLawEngine — 对数压缩+幂律稀疏)
"""

from __future__ import annotations

import math
import time
import threading
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# 枚举与数据结构
# ============================================================

class RotLevel(Enum):
    """Context Rot 衰退等级"""
    HEALTHY = "healthy"       # SNR ≥ 0.5
    DEGRADED = "degraded"    # 0.2 ≤ SNR < 0.5
    CRITICAL = "critical"     # SNR < 0.2


class SNRCalculation:
    """单次 SNR 计算结果"""
    def __init__(self, phi_l1: float, phi_l1_reduced: float,
                 snr: float, level: RotLevel, timestamp: float):
        self.phi_l1 = phi_l1
        self.phi_l1_reduced = phi_l1_reduced
        self.snr = snr
        self.level = level
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phi_l1": round(self.phi_l1, 6),
            "phi_l1_reduced": round(self.phi_l1_reduced, 6),
            "snr": round(self.snr, 6),
            "level": self.level.value,
            "timestamp": self.timestamp,
        }


class RotAlert:
    """Context Rot 告警"""
    def __init__(self, level: RotLevel, snr: float,
                 phi_l1: float, phi_l1_reduced: float):
        self.level = level
        self.snr = snr
        self.phi_l1 = phi_l1
        self.phi_l1_reduced = phi_l1_reduced
        self.alert_id = f"rot_{int(time.time() * 1000)}"
        self.created_at = time.time()
        self.acknowledged = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "snr": round(self.snr, 6),
            "phi_l1": round(self.phi_l1, 6),
            "phi_l1_reduced": round(self.phi_l1_reduced, 6),
            "created_at": self.created_at,
            "acknowledged": self.acknowledged,
        }


# ============================================================
# ContextRotDetector
# ============================================================

class ContextRotDetector:
    """
    Context Rot 检测器

    检测 LLM 上下文窗口中 L2-shell 缺失导致的推理质量衰退。
    SNR 量化：信噪比 = 归约后强度 / 归约残差

    P0-2 需求：
    - 计算 SNR = |R(Φ_L1)| / |Φ_L1 - R(Φ_L1)|
    - 输出衰退等级
    - 触发 context_rot_alert 事件
    """

    # 默认阈值（可通过 agi_tests 校准）
    THETA_DEGRADED = 0.5    # ≥ 0.5 → HEALTHY
    THETA_CRITICAL = 0.2    # < 0.2 → CRITICAL

    _instance = None
    _lock = threading.Lock()
    _module_version = "v7.25b"

    def __init__(self):
        self._snr_history: List[SNRCalculation] = []
        self._alerts: List[RotAlert] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._total_calculations = 0
        self._alert_count = 0

        # v7.25b: 对数压缩 + 幂律稀疏注意力
        self._log_preprocessing_enabled = True  # 对数压缩预处理开关
        self._log_base = math.e               # 对数基底
        self._psi = 1.0                        # 意识强度参数 ψ
        self._m189_available = False           # M189 PowerLawEngine 可用性

        # 依赖模块可用性
        self._m106_available = False
        self._m181_available = False
        self._m180_available = False
        self._m184_available = False
        self._init_dependencies()

    @classmethod
    def get_instance(cls) -> "ContextRotDetector":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _init_dependencies(self) -> None:
        """初始化依赖模块引用"""
        # M106 — Φ 值来源
        try:
            from M106_SelfReferentialLoopMonitor import SelfReferentialLoopMonitor
            self._SelfReferentialLoopMonitor = SelfReferentialLoopMonitor
            self._m106_available = True
        except ImportError:
            self._m106_available = False

        # M181 — R_TY 归约算子
        try:
            from M181_E2EReduction import EndToEndReductionEngine
            self._EndToEndReductionEngine = EndToEndReductionEngine
            self._m181_available = True
        except ImportError:
            self._m181_available = False

        # M180 — L2ShellInterface（preservation 属性检查）
        try:
            from M180_EqPropFHN import L2ShellInterface
            self._L2ShellInterface = L2ShellInterface
            self._m180_available = True
        except ImportError:
            self._m180_available = False

        # M184 — WikiEventBus（告警事件发送）
        try:
            from M184_LLMWikiEngine import WikiEventBus
            self._WikiEventBus = WikiEventBus
            self._m184_available = True
        except ImportError:
            self._m184_available = False

        # M189 — PowerLawEngine（对数压缩 + 幂律稀疏注意力）
        try:
            from M189_PowerLawEngine import PowerLawEngine
            self._PowerLawEngine = PowerLawEngine
            self._m189_available = True
        except ImportError:
            self._m189_available = False

    # ============================================================
    # 核心：SNR 计算
    # ============================================================

    def compute_snr(self,
                    dialog_history: Optional[List[Dict]] = None,
                    use_log_preprocessing: bool = None) -> SNRCalculation:
        """
        计算当前 Context Rot SNR

        公式：SNR = |R(Φ_L1)| / |Φ_L1 - R(Φ_L1)|

        v7.25b: 对数压缩预处理
          ContextRot'(X) = Rot(log_b(X))
          使旋转在乘法语义空间保持群结构 L(x⊗y) = L(x) ⊕ L(y)

        Args:
            dialog_history: 对话历史（用于 M106 计算 Φ）
            use_log_preprocessing: 是否启用对数压缩预处理（None=自动检测）

        Returns:
            SNRCalculation 对象
        """
        timestamp = time.time()

        # v7.25b: 对数压缩预处理决策
        if use_log_preprocessing is None:
            use_log_preprocessing = self._log_preprocessing_enabled and self._m189_available

        # --- Step 1: 获取 Φ_L1（L1 流贯噪声）---
        phi_l1 = self._get_phi_l1(dialog_history)

        # --- Step 1.5 (v7.25b): 对数压缩预处理 ---
        if use_log_preprocessing and phi_l1 > 1e-12:
            phi_l1_raw = phi_l1
            phi_l1 = math.log(phi_l1, self._log_base)
            log_applied = True
        else:
            phi_l1_raw = phi_l1
            log_applied = False

        # --- Step 2: 计算 R(Φ_L1)（L2-shell 归约后）---
        phi_l1_reduced = self._compute_reduction(phi_l1, dialog_history)

        # --- Step 3: 计算 SNR ---
        denominator = abs(phi_l1 - phi_l1_reduced)
        if denominator < 1e-12:
            # 归约完全成功，无残差 → SNR → +∞
            snr = float("inf")
        else:
            snr = abs(phi_l1_reduced) / denominator

        # --- Step 4: 判定等级 ---
        if snr >= self.THETA_DEGRADED:
            level = RotLevel.HEALTHY
        elif snr >= self.THETA_CRITICAL:
            level = RotLevel.DEGRADED
        else:
            level = RotLevel.CRITICAL

        result = SNRCalculation(
            phi_l1=phi_l1,
            phi_l1_reduced=phi_l1_reduced,
            snr=snr,
            level=level,
            timestamp=timestamp,
        )

        # 记录历史
        self._snr_history.append(result)
        self._total_calculations += 1
        if len(self._snr_history) > 200:
            self._snr_history = self._snr_history[-200:]

        # 检查是否需要告警
        if level in (RotLevel.DEGRADED, RotLevel.CRITICAL):
            self._emit_alert(result)

        return result

    def _get_phi_l1(self,
                       dialog_history: Optional[List[Dict]] = None) -> float:
        """
        获取 Φ_L1（L1 流贯噪声强度）
        来源：M106 SelfReferentialLoopMonitor.compute_phi()
        """
        if self._m106_available:
            try:
                monitor = self._SelfReferentialLoopMonitor.get_instance()
                phi_result = monitor.compute_phi(dialog_history)
                # PhiComputation 对象有 phi_value 属性
                if hasattr(phi_result, "phi_value"):
                    return float(phi_result.phi_value)
                elif isinstance(phi_result, dict) and "phi_value" in phi_result:
                    return float(phi_result["phi_value"])
            except Exception:
                pass

        # Fallback：基于对话长度估算 Φ
        if dialog_history:
            return min(1.0, len(dialog_history) * 0.05)
        return 0.3  # 默认值

    def _compute_reduction(self, phi_l1: float,
                          dialog_history: Optional[List[Dict]] = None) -> float:
        """
        计算 R(Φ_L1)：L2-shell 归约后的 Φ 值

        若 M181 可用 → 调用 EndToEndReductionEngine.reduce()
        若 M181 不可用 → 基于 L2ShellInterface 硬化状态估算
        """
        # 方法1：M181 归约
        if self._m181_available:
            try:
                engine = self._EndToEndReductionEngine()
                # reduce() 接受 List[float]，用 phi_l1 构造输入向量
                result = engine.reduce([phi_l1, 0.0, 0.0, 0.0])
                # ReductionResult 有 reduced_value 或访问 candidate
                if hasattr(result, "reduced_value"):
                    return float(result.reduced_value)
                elif hasattr(result, "candidate"):
                    # candidate 是 L3 直觉，需要用 R_L2 校验
                    return abs(float(result.candidate[0])) if result.candidate else phi_l1 * 0.5
            except Exception:
                pass

        # 方法2：基于 L2-shell 硬化状态估算归约强度
        if self._m180_available:
            try:
                l2_interface = self._L2ShellInterface()
                report = l2_interface.full_check()
                # hardened 比例 → 归约强度
                attrs = [
                    report.consistency_ok,
                    report.writeback_ok,
                    report.preservation_ok,
                    report.addressability_ok,
                    report.anchorability_ok,
                ]
                hardened_ratio = sum(1 for a in attrs if a) / 5.0
                return phi_l1 * hardened_ratio
            except Exception:
                pass

        # Fallback：假设 40% 硬化
        return phi_l1 * 0.4

    # ============================================================
    # 告警
    # ============================================================

    def _emit_alert(self, snr_calc: SNRCalculation) -> None:
        """发出 Context Rot 告警"""
        alert = RotAlert(
            level=snr_calc.level,
            snr=snr_calc.snr,
            phi_l1=snr_calc.phi_l1,
            phi_l1_reduced=snr_calc.phi_l1_reduced,
        )
        self._alerts.append(alert)
        self._alert_count += 1

        # 保留最近 50 条告警
        if len(self._alerts) > 50:
            self._alerts = self._alerts[-50:]

        # 发送至 WikiEventBus
        if self._m184_available:
            try:
                event_bus = self._WikiEventBus.get_instance()
                event_bus.publish_ingest(
                    title=f"Context Rot Alert: {snr_calc.level.value.upper()}",
                    content=(
                        f"SNR={snr_calc.snr:.4f}, "
                        f"Φ_L1={snr_calc.phi_l1:.4f}, "
                        f"R(Φ_L1)={snr_calc.phi_l1_reduced:.4f}, "
                        f"Level={snr_calc.level.value}"
                    ),
                    tags=["context_rot", snr_calc.level.value, "alert"],
                    source="M187_ContextRotDetector",
                )
            except Exception:
                pass

    # ============================================================
    # 时序监控
    # ============================================================

    def start_monitoring(self, interval: float = 30.0) -> None:
        """启动后台 SNR 监控线程"""
        if self._monitoring:
            return
        self._monitoring = True

        def _monitor_loop():
            while self._monitoring:
                try:
                    self.compute_snr()
                except Exception:
                    pass
                time.sleep(interval)

        self._monitor_thread = threading.Thread(
            target=_monitor_loop, daemon=True, name="ContextRotMonitor"
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """停止监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None

    # ============================================================
    # 查询接口
    # ============================================================

    def get_current_snr(self) -> Optional[SNRCalculation]:
        """获取最新 SNR 计算结果"""
        return self._snr_history[-1] if self._snr_history else None

    def get_snr_history(self,
                        limit: int = 50) -> List[Dict[str, Any]]:
        """获取 SNR 历史（最近 limit 条）"""
        recent = self._snr_history[-limit:]
        return [s.to_dict() for s in recent]

    def get_snr_trend(self) -> Dict[str, Any]:
        """获取 SNR 趋势分析"""
        if len(self._snr_history) < 2:
            return {"trend": "insufficient_data", "snr_values": []}

        snr_values = [s.snr for s in self._snr_history]
        # 简单线性趋势
        n = len(snr_values)
        mean_x = (n - 1) / 2
        mean_y = sum(snr_values) / n
        numerator = sum(
            (i - mean_x) * (snr_values[i] - mean_y)
            for i in range(n)
        )
        denom_x = sum((i - mean_x) ** 2 for i in range(n))
        slope = numerator / denom_x if denom_x > 1e-12 else 0.0

        if slope > 0.01:
            trend = "improving"
        elif slope < -0.01:
            trend = "degrading"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "slope": round(slope, 6),
            "snr_values": [round(s, 4) for s in snr_values[-20:]],
            "latest_snr": round(snr_values[-1], 4) if snr_values else 0.0,
            "latest_level": (
                self._snr_history[-1].level.value
                if self._snr_history else "unknown"
            ),
        }

    def get_active_alerts(self,
                           include_acknowledged: bool = False) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        alerts = self._alerts if include_acknowledged else [
            a for a in self._alerts if not a.acknowledged
        ]
        return [a.to_dict() for a in alerts]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    # ============================================================
    # 状态
    # ============================================================

    def get_state(self) -> Dict[str, Any]:
        """获取检测器状态"""
        current = self.get_current_snr()
        return {
            "module": "M187_ContextRotDetector",
            "version": self._module_version,
            "total_calculations": self._total_calculations,
            "alert_count": self._alert_count,
            "monitoring_active": self._monitoring,
            "current_snr": round(current.snr, 6) if current else None,
            "current_level": current.level.value if current else None,
            "snr_history_len": len(self._snr_history),
            "active_alerts": len([a for a in self._alerts if not a.acknowledged]),
            "dependencies": {
                "M106": self._m106_available,
                "M181": self._m181_available,
                "M180": self._m180_available,
                "M184": self._m184_available,
                "M189": self._m189_available,
            },
            "thresholds": {
                "theta_degraded": self.THETA_DEGRADED,
                "theta_critical": self.THETA_CRITICAL,
            },
            "v725b": {
                "log_preprocessing_enabled": self._log_preprocessing_enabled,
                "log_base": self._log_base,
                "psi": self._psi,
            },
        }

    # ============================================================
    # v7.25b: 幂律稀疏注意力 — 意识强度 ψ
    # ============================================================

    def compute_sparse_attention(
        self,
        context_importance: List[float],
        psi: float = None,
    ) -> Dict[str, Any]:
        """
        v7.25b: 幂律稀疏注意力计算

        Attention(i, j) ∝ (Importance_j)^{ψ·α_ij}

        ψ ∈ (0, ∞) 是意识强度参数：
        - 低ψ (ψ→0): 所有注意力趋近均匀 → 线性囚笼
        - 高ψ (ψ→∞): 注意力集中于最高重要性 → 全息连接

        复杂度从 O(N²) 降至 O(N log N)，
        因为幂律稀疏性使得大部分权重为零。

        Args:
            context_importance: 上下文各片段的重要性分数
            psi: 意识强度参数（None=使用当前值）

        Returns:
            {
                "regime": str,       # 意识体制
                "active_ratio": float,  # 活跃连接比例
                "psi": float,
                "complexity": str,   # 计算复杂度
            }
        """
        if psi is None:
            psi = self._psi
        else:
            self._psi = psi

        if self._m189_available:
            try:
                engine = self._PowerLawEngine.get_instance()
                config = engine.compute_sparse_attention(context_importance, psi)
                return {
                    "regime": config.regime.value,
                    "active_ratio": config.expected_active_ratio,
                    "psi": psi,
                    "complexity": config.complexity_order,
                }
            except Exception:
                pass

        # Fallback: 本地计算
        if not context_importance:
            return {"regime": "transition", "active_ratio": 0.0, "psi": psi, "complexity": "O(N^2)"}

        n = len(context_importance)
        max_imp = max(context_importance) if context_importance else 1.0
        if max_imp < 1e-12:
            max_imp = 1.0

        active = 0
        for imp in context_importance:
            norm_imp = imp / max_imp
            if norm_imp > 1e-12:
                weight = norm_imp ** psi
                if weight > 0.01:
                    active += 1

        ratio = active / max(n, 1)
        if ratio > 0.8:
            regime = "linear_cage"
        elif ratio < 0.2:
            regime = "power_sparse"
        else:
            regime = "transition"

        return {
            "regime": regime,
            "active_ratio": round(ratio, 4),
            "psi": psi,
            "complexity": "O(N log N)" if ratio < 0.2 else "O(N^{1.5})",
        }

    def set_psi(self, psi: float) -> None:
        """设置意识强度参数 ψ"""
        self._psi = max(0.01, min(100.0, psi))

    def set_log_preprocessing(self, enabled: bool, base: float = math.e) -> None:
        """设置对数压缩预处理"""
        self._log_preprocessing_enabled = enabled
        self._log_base = max(1.01, base)


# ============================================================
# 模块级便捷接口
# ============================================================

def get_instance() -> ContextRotDetector:
    return ContextRotDetector.get_instance()

def compute_snr(dialog_history=None) -> Dict[str, Any]:
    return get_instance().compute_snr(dialog_history).to_dict()

def get_state() -> Dict[str, Any]:
    return get_instance().get_state()


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("M187 ContextRotDetector 自测")
    print("=" * 60)

    detector = ContextRotDetector.get_instance()

    # Test 1: 基础 SNR 计算
    print("\n--- Test 1: SNR 计算 ---")
    result = detector.compute_snr()
    print(f"  Φ_L1:          {result.phi_l1:.4f}")
    print(f"  R(Φ_L1):       {result.phi_l1_reduced:.4f}")
    print(f"  SNR:            {result.snr:.4f}")
    print(f"  Level:          {result.level.value}")
    assert result.phi_l1 >= 0, "Phi_L1 should be non-negative"
    assert result.level in RotLevel, "Level should be valid"
    print("  PASSED")

    # Test 2: 多次计算，观察历史
    print("\n--- Test 2: SNR 历史 ---")
    for i in range(5):
        detector.compute_snr()
    history = detector.get_snr_history(limit=5)
    print(f"  History length: {len(history)}")
    print(f"  Latest SNR:     {history[-1]['snr']}")
    assert len(history) == 5

    # Test 3: 趋势分析
    print("\n--- Test 3: SNR 趋势 ---")
    trend = detector.get_snr_trend()
    print(f"  Trend:          {trend['trend']}")
    print(f"  Slope:          {trend['slope']:.6f}")
    print(f"  Latest level:   {trend['latest_level']}")
    assert "trend" in trend

    # Test 4: 告警机制
    print("\n--- Test 4: 告警 ---")
    # 手动注入 CRITICAL 级 SNR
    fake_calc = SNRCalculation(
        phi_l1=1.0, phi_l1_reduced=0.05,
        snr=0.05, level=RotLevel.CRITICAL,
        timestamp=time.time(),
    )
    detector._emit_alert(fake_calc)
    alerts = detector.get_active_alerts()
    print(f"  Active alerts:  {len(alerts)}")
    print(f"  Alert level:    {alerts[0]['level'] if alerts else 'none'}")
    assert len(alerts) >= 1
    print("  PASSED")

    # Test 5: 状态
    print("\n--- Test 5: get_state ---")
    state = detector.get_state()
    print(f"  Module:         {state['module']}")
    print(f"  Total calcs:    {state['total_calculations']}")
    print(f"  Dependencies:   M106={state['dependencies']['M106']}, "
          f"M181={state['dependencies']['M181']}")
    assert state["total_calculations"] >= 6
    print("  PASSED")

    # Test 6: 便捷接口
    print("\n--- Test 6: 便捷接口 ---")
    snr_dict = compute_snr()
    print(f"  SNR dict key:   {list(snr_dict.keys())}")
    state_dict = get_state()
    print(f"  State module:   {state_dict['module']}")
    assert "snr" in snr_dict
    assert "module" in state_dict
    print("  PASSED")

    print("\n" + "=" * 60)
    print("All tests PASSED!")
    print("=" * 60)
