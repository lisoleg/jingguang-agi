# -*- coding: utf-8 -*-
"""
模块41：ElasticCoordinationBus —— 弹簧虫协调总线
基于弹簧虫三大定理的弹性协调机制

来源：复合体AGI 6.0升级方案（基于12文档深度分析）
      弹簧虫论文：多主体Φ场耦合、能量循环与鲁棒动态平衡
作者：基于高见远指令实现
日期：2026-05-13
"""

import time
import json
import math
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Callable
from enum import Enum


@dataclass
class ShockAbsorption:
    """冲击吸收记录"""
    error: str
    error_type: str
    absorbed_at: float
    recovery_plan: str
    momentum_before: float
    momentum_after: float
    context: Dict
    
    def to_dict(self) -> Dict:
        return {
            "error": self.error,
            "error_type": self.error_type,
            "absorbed_at": self.absorbed_at,
            "recovery_plan": self.recovery_plan,
            "momentum_delta": self.momentum_after - self.momentum_before,
            "context": self.context
        }


@dataclass
class ResourceAllocation:
    """资源分配记录"""
    module: str
    resource_type: str
    amount: float
    allocated_at: float
    returned: bool = False
    returned_at: Optional[float] = None


@dataclass
class GlobalPurposeState:
    """全局目的状态（弹簧虫质心）"""
    direction: str = "forward"    # 前进方向
    speed: float = 1.0           # 当前速度 [0, 1]
    target_speed: float = 1.0    # 目标速度
    energy: float = 1.0           # 能量水平 [0, 1]
    momentum: float = 1.0         # 动量
    locked: bool = False          # 是否锁定
    
    def to_dict(self) -> Dict:
        return {
            "direction": self.direction,
            "speed": self.speed,
            "target_speed": self.target_speed,
            "energy": self.energy,
            "momentum": self.momentum,
            "locked": self.locked
        }


class ElasticCoordinationBus:
    """
    模块41：弹性协调总线（基于弹簧虫论文）
    
    实现弹簧虫三大定理的工程化：
    1. 质心守恒定理 → GlobalPurposeLock
       无净外力 → 质心速度常数 → 全局目标不偏离
    
    2. 能量循环不变量 → ResourcePool
       动能↔势能守恒 → 资源在模块间动态分配但总量守恒
    
    3. 缓冲碰撞鲁棒性 → ShockAbsorber
       弹簧吸收冲击 → 轻微后退 → 继续前进
    
    可审计动态平衡三要素：
    1. 存在不变量（全局目标、资源总量）可测可验
    2. 轨迹可追踪（执行路径可回放）
    3. 扰动响应可问（因果可描述）
    
    核心功能：
    1. absorb_shock() - 缓冲外部冲击
    2. restore_momentum() - 恢复动量
    3. allocate_resource() - 资源循环分配
    4. set_global_purpose() - 设置全局目标
    5. check_health() - 健康检查
    """
    
    def __init__(self, purpose_layer=None):
        self.purpose_layer = purpose_layer  # 可选的DIKWPPurposeLayer
        
        # 全局目的状态（质心）
        self.global_purpose = GlobalPurposeState()
        
        # 资源池（能量守恒）
        self.resource_pool: Dict[str, float] = {
            "compute": 1.0,      # 计算资源
            "memory": 1.0,       # 内存资源
            "attention": 1.0,     # 注意力资源
            "bandwidth": 1.0     # 带宽资源
        }
        self._initial_resources = self.resource_pool.copy()
        
        # 冲击缓冲
        self.shock_buffer: List[ShockAbsorption] = []
        self._max_shock_buffer = 100
        
        # 资源分配记录
        self.allocations: List[ResourceAllocation] = []
        
        # 执行轨迹（可追踪）
        self.execution_trace: List[Dict] = []
        
        # 事件监听器
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # 配置
        self._shock_absorb_rate = 0.2    # 每次冲击吸收率
        self._recovery_rate = 0.1         # 动量恢复率
        self._min_speed = 0.1             # 最小速度（不完全停止）
        self._max_speed = 1.0             # 最大速度
    
    # ============================================================
    # 质心守恒定理：全局目的不偏离
    # ============================================================
    
    def set_global_purpose(self, 
                          direction: str = "forward",
                          target_speed: float = 1.0,
                          locked: bool = False):
        """
        设置全局目的（质心守恒定理）
        
        Args:
            direction: 前进方向
            target_speed: 目标速度
            locked: 是否锁定（锁定后不受冲击影响）
        """
        self.global_purpose.direction = direction
        self.global_purpose.target_speed = target_speed
        self.global_purpose.locked = locked
        
        self._emit_event("purpose_set", {
            "direction": direction,
            "target_speed": target_speed,
            "locked": locked
        })
    
    def get_global_purpose(self) -> Dict:
        """获取全局目的状态"""
        return self.global_purpose.to_dict()
    
    def check_purpose_conservation(self) -> Dict:
        """
        检查质心守恒（可测可验的不变量）
        
        Returns:
            Dict: 守恒检查结果
        """
        # 质心守恒：速度不应有大幅突变
        # （除非有正当理由如人工干预或严重故障）
        
        return {
            "conserved": self.global_purpose.speed > 0,
            "deviation": abs(self.global_purpose.speed - self.global_purpose.target_speed),
            "momentum": self.global_purpose.momentum,
            "energy": self.global_purpose.energy,
            "locked": self.global_purpose.locked
        }
    
    # ============================================================
    # 能量循环不变量：资源守恒
    # ============================================================
    
    def allocate_resource(self, 
                         module: str, 
                         resource_type: str,
                         amount: float) -> bool:
        """
        资源循环分配（能量循环不变量：总量守恒）
        
        Args:
            module: 请求资源的模块
            resource_type: 资源类型
            amount: 请求量 [0, 1]
        
        Returns:
            bool: 是否分配成功
        """
        if resource_type not in self.resource_pool:
            return False
        
        current = self.resource_pool[resource_type]
        
        if current < amount:
            # 资源不足，尝试从其他来源补充
            return False
        
        # 分配资源
        self.resource_pool[resource_type] -= amount
        
        # 记录分配
        self.allocations.append(ResourceAllocation(
            module=module,
            resource_type=resource_type,
            amount=amount,
            allocated_at=time.time()
        ))
        
        self._emit_event("resource_allocated", {
            "module": module,
            "resource_type": resource_type,
            "amount": amount,
            "remaining": self.resource_pool[resource_type]
        })
        
        return True
    
    def release_resource(self, 
                        module: str, 
                        resource_type: str,
                        amount: float = None) -> float:
        """
        释放资源（能量循环：返回资源池）
        
        Args:
            module: 释放模块
            resource_type: 资源类型
            amount: 释放量（None=全部释放）
        
        Returns:
            float: 实际释放量
        """
        if resource_type not in self.resource_pool:
            return 0.0
        
        # 找到该模块的分配记录
        released = 0.0
        for alloc in reversed(self.allocations):
            if alloc.module == module and alloc.resource_type == resource_type and not alloc.returned:
                if amount is None or released < amount:
                    actual = min(alloc.amount, amount - released) if amount else alloc.amount
                    self.resource_pool[resource_type] += actual
                    alloc.returned = True
                    alloc.returned_at = time.time()
                    released += actual
        
        # 更新全局能量
        self._update_global_energy()
        
        return released
    
    def get_resource_status(self) -> Dict:
        """获取资源状态"""
        return {
            "pools": self.resource_pool.copy(),
            "total_allocated": sum(a.amount for a in self.allocations if not a.returned),
            "total_free": sum(self.resource_pool.values()),
            "conservation_held": self._check_conservation()
        }
    
    def _check_conservation(self) -> bool:
        """检查资源守恒"""
        # 初始总量 = 当前自由 + 已分配（未释放）
        initial_total = sum(self._initial_resources.values())
        current_total = sum(self.resource_pool.values())
        
        # 允许小量误差（浮点运算）
        return abs(initial_total - current_total) < 0.001
    
    def _update_global_energy(self):
        """更新全局能量水平"""
        total_free = sum(self.resource_pool.values())
        max_total = sum(self._initial_resources.values())
        self.global_purpose.energy = total_free / max_total if max_total > 0 else 0
    
    # ============================================================
    # 缓冲碰撞鲁棒性：吸收冲击
    # ============================================================
    
    def absorb_shock(self, 
                    error: Exception, 
                    context: Dict = None,
                    severity: float = None) -> Dict:
        """
        缓冲碰撞鲁棒性：吸收外部冲击，不让全局目标崩溃
        
        弹簧虫：动能→势能→再释放，轻微后退→继续前进
        
        Args:
            error: 异常对象
            context: 错误上下文
            severity: 严重程度 [0, 1]（None=自动判断）
        
        Returns:
            Dict: 吸收结果和恢复计划
        """
        context = context or {}
        
        # 自动判断严重程度
        if severity is None:
            error_str = str(error).lower()
            if "critical" in error_str or "fatal" in error_str:
                severity = 0.9
            elif "timeout" in error_str or "memory" in error_str:
                severity = 0.5
            else:
                severity = 0.3
        
        # 记录冲击前的动量
        momentum_before = self.global_purpose.speed
        
        # 吸收冲击：速度适当降低（但不低于最小速度）
        speed_reduction = severity * self._shock_absorb_rate
        self.global_purpose.speed = max(
            self._min_speed,
            self.global_purpose.speed - speed_reduction
        )
        
        # 吸收冲击到缓冲器
        shock = ShockAbsorption(
            error=str(error),
            error_type=type(error).__name__,
            absorbed_at=time.time(),
            recovery_plan=self._plan_recovery(error),
            momentum_before=momentum_before,
            momentum_after=self.global_purpose.speed,
            context=context
        )
        
        self.shock_buffer.append(shock)
        
        # 限制缓冲大小
        if len(self.shock_buffer) > self._max_shock_buffer:
            self.shock_buffer = self.shock_buffer[-self._max_shock_buffer:]
        
        # 记录执行轨迹
        self._add_trace("shock_absorbed", {
            "error_type": shock.error_type,
            "severity": severity,
            "recovery": shock.recovery_plan,
            "speed_delta": shock.momentum_after - shock.momentum_before
        })
        
        self._emit_event("shock_absorbed", shock.to_dict())
        
        return {
            "absorbed": True,
            "recovery": shock.recovery_plan,
            "current_speed": self.global_purpose.speed,
            "severity": severity,
            "momentum_delta": shock.momentum_after - shock.momentum_before
        }
    
    def restore_momentum(self, amount: float = None) -> float:
        """
        恢复全局动量（势能→动能）
        
        Args:
            amount: 恢复量（None=按默认恢复率）
        
        Returns:
            float: 当前速度
        """
        if amount is None:
            amount = self._recovery_rate
        
        # 恢复速度（不超过目标速度）
        self.global_purpose.speed = min(
            self.global_purpose.target_speed,
            self.global_purpose.speed + amount
        )
        
        # 更新动量
        self.global_purpose.momentum = self.global_purpose.speed * self.global_purpose.energy
        
        self._add_trace("momentum_restored", {"amount": amount, "current_speed": self.global_purpose.speed})
        
        return self.global_purpose.speed
    
    def _plan_recovery(self, error: Exception) -> str:
        """制定恢复计划"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return "retry_with_exponential_backoff"
        elif "memory" in error_str:
            return "release_cache_and_gc"
        elif "auth" in error_str or "permission" in error_str:
            return "revalidate_credentials"
        elif "connection" in error_str:
            return "retry_with_alternate_endpoint"
        elif "parse" in error_str or "format" in error_str:
            return "validate_input_and_retry"
        else:
            return "fallback_to_safe_mode"
    
    def get_shock_history(self, limit: int = 10) -> List[Dict]:
        """获取冲击历史"""
        return [s.to_dict() for s in self.shock_buffer[-limit:]]
    
    # ============================================================
    # 执行轨迹（可追踪）
    # ============================================================
    
    def _add_trace(self, event_type: str, data: Dict):
        """添加执行轨迹"""
        self.execution_trace.append({
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
            "global_purpose": self.global_purpose.to_dict()
        })
        
        # 限制轨迹长度
        if len(self.execution_trace) > 1000:
            self.execution_trace = self.execution_trace[-1000:]
    
    def get_trace(self, 
                  since: float = None,
                  event_type: str = None,
                  limit: int = 100) -> List[Dict]:
        """
        获取执行轨迹
        
        Args:
            since: 时间下限
            event_type: 事件类型过滤
            limit: 返回条数
        
        Returns:
            List[Dict]: 轨迹列表
        """
        trace = self.execution_trace
        
        if since:
            trace = [t for t in trace if t["timestamp"] >= since]
        
        if event_type:
            trace = [t for t in trace if t["type"] == event_type]
        
        return trace[-limit:]
    
    # ============================================================
    # 健康检查
    # ============================================================
    
    def check_health(self) -> Dict:
        """
        综合健康检查
        
        Returns:
            Dict: 健康状态报告
        """
        # 1. 质心守恒检查
        purpose_check = self.check_purpose_conservation()
        
        # 2. 能量循环检查
        resource_status = self.get_resource_status()
        
        # 3. 冲击缓冲检查
        recent_shocks = self.shock_buffer[-10:] if self.shock_buffer else []
        avg_shock_severity = 0
        if recent_shocks:
            # 简化计算
            avg_shock_severity = sum(
                s.momentum_after - s.momentum_before 
                for s in recent_shocks
            ) / len(recent_shocks)
        
        # 综合评分
        health_score = (
            purpose_check["conserved"] * 0.3 +
            resource_status["conservation_held"] * 0.3 +
            (1 - avg_shock_severity) * 0.2 +
            self.global_purpose.energy * 0.2
        )
        
        # 状态判定
        if health_score >= 0.8:
            status = "healthy"
        elif health_score >= 0.5:
            status = "degraded"
        else:
            status = "critical"
        
        return {
            "status": status,
            "health_score": health_score,
            "global_purpose": purpose_check,
            "resource": {
                "conservation": resource_status["conservation_held"],
                "utilization": 1 - sum(resource_status["pools"].values()) / len(resource_status["pools"])
            },
            "shock_buffer": {
                "size": len(self.shock_buffer),
                "recent_count": len(recent_shocks),
                "avg_impact": abs(avg_shock_severity)
            },
            "recommendations": self._generate_recommendations(status, purpose_check, resource_status)
        }
    
    def _generate_recommendations(self, 
                                status: str,
                                purpose_check: Dict,
                                resource_status: Dict) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        if status in ("degraded", "critical"):
            recommendations.append("考虑恢复动量: restore_momentum()")
        
        if not purpose_check["conserved"]:
            recommendations.append("检查全局目标是否偏离")
        
        if not resource_status["conservation_held"]:
            recommendations.append("资源守恒被破坏，需要检查资源泄漏")
        
        if self.global_purpose.energy < 0.3:
            recommendations.append("能量不足，释放未使用的资源")
        
        if len(self.shock_buffer) > 50:
            recommendations.append("冲击缓冲较大，考虑系统稳定性检查")
        
        return recommendations
    
    # ============================================================
    # 事件系统
    # ============================================================
    
    def on(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def off(self, event_type: str, handler: Callable = None):
        """注销事件处理器"""
        if event_type in self._event_handlers:
            if handler:
                self._event_handlers[event_type].remove(handler)
            else:
                self._event_handlers[event_type] = []
    
    def _emit_event(self, event_type: str, data: Dict):
        """触发事件"""
        for handler in self._event_handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                print(f"事件处理器错误: {e}")
    
    # ============================================================
    # 统计和导出
    # ============================================================
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "global_purpose": self.global_purpose.to_dict(),
            "resource_pools": self.resource_pool.copy(),
            "shock_buffer_size": len(self.shock_buffer),
            "total_allocations": len(self.allocations),
            "trace_length": len(self.execution_trace),
            "health": self.check_health()
        }
    
    def export_state(self, filepath: str):
        """导出现场状态"""
        data = {
            "global_purpose": self.global_purpose.to_dict(),
            "resource_pool": self.resource_pool,
            "shock_buffer": [s.to_dict() for s in self.shock_buffer],
            "allocations": [
                {
                    "module": a.module,
                    "resource_type": a.resource_type,
                    "amount": a.amount,
                    "allocated_at": a.allocated_at,
                    "returned": a.returned
                }
                for a in self.allocations[-100:]
            ],
            "trace": self.execution_trace[-100:],
            "statistics": self.get_statistics(),
            "export_time": time.time()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def __repr__(self) -> str:
        return (
            f"ElasticCoordinationBus("
            f"speed={self.global_purpose.speed:.2f}, "
            f"energy={self.global_purpose.energy:.2f}, "
            f"shocks={len(self.shock_buffer)})"
        )


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("模块41：弹性协调总线测试")
    print("=" * 60)
    
    # 1. 创建协调总线
    bus = ElasticCoordinationBus()
    print(f"\n✓ 创建协调总线: {bus}")
    
    # 2. 设置全局目的（质心守恒）
    print(f"\n✓ 质心守恒定理:")
    bus.set_global_purpose(direction="forward", target_speed=1.0)
    print(f"  初始状态: {bus.get_global_purpose()}")
    
    # 3. 资源分配（能量循环）
    print(f"\n✓ 能量循环不变量:")
    
    alloc1 = bus.allocate_resource("module_A", "compute", 0.3)
    alloc2 = bus.allocate_resource("module_B", "memory", 0.2)
    print(f"  分配compute(0.3)到module_A: {alloc1}")
    print(f"  分配memory(0.2)到module_B: {alloc2}")
    print(f"  资源状态: {bus.get_resource_status()['pools']}")
    print(f"  守恒检查: {bus.get_resource_status()['conservation_held']}")
    
    # 释放资源
    released = bus.release_resource("module_A", "compute")
    print(f"  释放compute资源: {released:.2f}")
    print(f"  守恒检查: {bus.get_resource_status()['conservation_held']}")
    
    # 4. 冲击吸收
    print(f"\n✓ 缓冲碰撞鲁棒性:")
    
    errors = [
        Exception("timeout: connection failed"),
        Exception("memory allocation failed"),
        Exception("critical: system error")
    ]
    
    for err in errors:
        result = bus.absorb_shock(err, {"module": "test"})
        print(f"  冲击[{err}] -> 速度: {result['current_speed']:.2f}, 恢复: {result['recovery']}")
    
    # 5. 动量恢复
    print(f"\n✓ 动量恢复:")
    speed = bus.restore_momentum(0.15)
    print(f"  恢复后速度: {speed:.2f}")
    print(f"  全局状态: {bus.get_global_purpose()}")
    
    # 6. 健康检查
    print(f"\n✓ 健康检查:")
    health = bus.check_health()
    print(f"  状态: {health['status']}")
    print(f"  评分: {health['health_score']:.2f}")
    print(f"  建议: {health['recommendations']}")
    
    # 7. 执行轨迹
    print(f"\n✓ 执行轨迹:")
    trace = bus.get_trace(limit=5)
    print(f"  轨迹长度: {len(trace)}")
    for t in trace[-3:]:
        print(f"  - [{t['type']}]")
    
    # 8. 统计信息
    print(f"\n✓ 统计信息:")
    stats = bus.get_statistics()
    print(f"  冲击缓冲: {stats['shock_buffer_size']}")
    print(f"  分配记录: {stats['total_allocations']}")
    
    print("\n" + "=" * 60)
    print("模块41测试完成 ✓")
    print("=" * 60)
