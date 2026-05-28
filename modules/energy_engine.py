"""
energy_engine.py - 能量流动引擎

基于复合体理学中的能量流动原理：
- 能量代表信息处理能力，高能量复合体处理更高效
- 注意力机制决定能量分配优先级
- 信息价值越高，分配能量越多
- 能量会随时间自然衰减（模拟熵增）

核心功能：
1. 能量分配：根据注意力权重分配能量
2. 能量损耗：模拟处理过程中的能量消耗
3. 能量恢复：任务完成后能量补充机制
4. 价值评估：评估信息价值以决定能量投入
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import time

from modules.agi_core import ComplexUnit, ComplexNetwork, LayerType


@dataclass
class EnergyPacket:
    """能量包 - 携带能量的信息单元"""
    
    value: float           # 能量值
    source_id: str         # 来源复合体ID
    target_id: str         # 目标复合体ID
    priority: float = 1.0  # 优先级（影响分配）
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def decay(self, rate: float = 0.01) -> None:
        """能量随时间衰减"""
        elapsed = time.time() - self.timestamp
        self.value = max(0.0, self.value * (1.0 - rate * elapsed))


class EnergyEngine:
    """能量流动引擎 - 管理复合体网络中的能量分配与流动"""
    
    def __init__(self, network: ComplexNetwork):
        self.network = network
        self.energy_pool: float = 10.0  # 总能量池
        self.decay_rate: float = 0.005   # 能量衰减率（每时间单位）
        self.recovery_rate: float = 0.1  # 能量恢复速率
        self.packets: List[EnergyPacket] = []  # 待处理的能量包
        self.history: List[Dict] = []    # 能量流动历史
        
    def allocate_energy(self, unit_id: str, base_amount: float = 0.2) -> float:
        """为指定复合体分配能量，返回实际分配量"""
        if unit_id not in self.network.units:
            return 0.0
        
        unit = self.network.units[unit_id]
        
        # 分配公式：基础量 × 注意力权重 × 能量池比例
        allocation = base_amount * unit.attention_weight * (self.energy_pool / 10.0)
        allocation = min(allocation, self.energy_pool, 1.0 - unit.energy)
        
        if allocation > 0:
            unit.receive_energy(allocation)
            self.energy_pool -= allocation
            self._record_event("allocate", unit_id, allocation)
        
        return allocation
    
    def distribute_to_layer(self, layer: LayerType, total_energy: float = 1.0) -> Dict[str, float]:
        """向指定层级的所有复合体分配能量"""
        units = self.network.get_layer_units(layer)
        if not units:
            return {}
        
        # 按注意力权重分配
        total_attention = sum(u.attention_weight for u in units)
        if total_attention == 0:
            return {}
        
        allocations = {}
        for unit in units:
            share = (unit.attention_weight / total_attention) * total_energy
            actual = unit.receive_energy(share)
            allocations[unit.id] = share
            self._record_event("distribute", unit.id, share)
        
        self.energy_pool -= total_energy
        return allocations
    
    def process_signal(self, source_id: str, signal_value: float) -> List[Tuple[str, float]]:
        """处理信号，向连接的复合体分发能量，返回(目标ID, 能量)列表"""
        if source_id not in self.network.connections:
            return []
        
        results = []
        targets = self.network.connections[source_id]
        
        for target_id in targets:
            target = self.network.units.get(target_id)
            if target is None:
                continue
            
            # 计算传递的能量：信号值 × 源注意力 × 目标注意力
            source = self.network.units[source_id]
            energy_transfer = signal_value * source.attention_weight * target.attention_weight
            
            # 创建能量包
            packet = EnergyPacket(
                value=energy_transfer,
                source_id=source_id,
                target_id=target_id
            )
            self.packets.append(packet)
            
            # 目标接收能量
            received = target.receive_energy(energy_transfer)
            results.append((target_id, received))
            
            self._record_event("transfer", target_id, energy_transfer, source_id)
        
        return results
    
    def consume_for_processing(self, unit_id: str, intensity: float = 0.1) -> float:
        """复合体处理信息时消耗能量"""
        if unit_id not in self.network.units:
            return 0.0
        
        unit = self.network.units[unit_id]
        consumed = unit.consume_energy(intensity)
        
        # 消耗的能量返回到能量池（部分回收）
        recycled = consumed * 0.3
        self.energy_pool += recycled
        
        self._record_event("consume", unit_id, consumed)
        return consumed
    
    def apply_decay(self) -> None:
        """对所有复合体应用能量衰减"""
        for unit in self.network.units.values():
            decay_amount = unit.energy * self.decay_rate
            unit.energy -= decay_amount
        
        # 能量包也衰减
        for packet in self.packets:
            packet.decay(self.decay_rate)
        
        # 清理空能量包
        self.packets = [p for p in self.packets if p.value > 0.01]
    
    def recover_energy(self) -> None:
        """恢复能量池（模拟休息/充电）"""
        self.energy_pool = min(10.0, self.energy_pool + self.recovery_rate)
    
    def evaluate_information_value(self, content: str, context: Dict = None) -> float:
        """评估信息价值，决定能量投入量
        
        简单启发式：
        - 长度适中（10-100字符）的信息价值较高
        - 包含关键词（重要、紧急、必须）的信息价值提升
        - 上下文中的优先级影响价值
        """
        if not content:
            return 0.1
        
        value = 0.5  # 基础价值
        
        # 长度因素
        length = len(content)
        if 10 <= length <= 100:
            value += 0.2
        elif length > 500:
            value -= 0.1
        
        # 关键词因素
        keywords = ["重要", "紧急", "必须", "关键", "重要", "urgent", "important", "critical"]
        for kw in keywords:
            if kw in content.lower():
                value += 0.15
                break
        
        # 上下文因素
        if context:
            if context.get("priority") == "high":
                value += 0.2
            elif context.get("priority") == "low":
                value -= 0.2
        
        return max(0.1, min(1.0, value))
    
    def _record_event(self, event_type: str, unit_id: str, amount: float, source_id: str = None) -> None:
        """记录能量流动事件"""
        self.history.append({
            "type": event_type,
            "unit_id": unit_id,
            "amount": amount,
            "source_id": source_id,
            "timestamp": time.time(),
            "energy_pool": self.energy_pool
        })
        
        # 保留最近100条记录
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def get_energy_report(self) -> Dict[str, Any]:
        """生成能量状态报告"""
        unit_energies = {uid: u.energy for uid, u in self.network.units.items()}
        layer_energies = {}
        
        for layer in LayerType:
            units = self.network.get_layer_units(layer)
            if units:
                layer_energies[layer.value] = sum(u.energy for u in units) / len(units)
        
        return {
            "energy_pool": self.energy_pool,
            "unit_energies": unit_energies,
            "layer_averages": layer_energies,
            "active_packets": len(self.packets),
            "total_consumed": sum(h["amount"] for h in self.history if h["type"] == "consume")
        }
