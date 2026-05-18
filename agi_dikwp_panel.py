# -*- coding: utf-8 -*-
"""
复合体AGI 6.0 - DIKWP状态实时仪表盘
DIKWP Real-time Status Dashboard

基于复合体理学六层语义架构：
D(数据) → I(信息) → K(知识) → W(智慧) → P(目的) → R(可靠)

融合BFT共识验证与Lean形式化证明状态

版本: v1.0
日期: 2026-05-13
"""

import time
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import threading


class LayerStatus(Enum):
    """层级状态枚举"""
    ACTIVE = "active"      # 活跃
    PROCESSING = "processing"  # 处理中
    COMPLETE = "complete"  # 完成
    WARNING = "warning"    # 警告
    ERROR = "error"        # 错误
    PENDING = "pending"    # 待处理


class BFTState(Enum):
    """BFT共识状态"""
    PENDING = "pending"
    VOTING = "voting"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"
    BYZANTINE_FAULT = "byzantine_fault"


@dataclass
class LayerMetrics:
    """层级指标"""
    name: str
    full_name: str
    score: float = 0.0           # 0-1 评分
    status: LayerStatus = LayerStatus.PENDING
    progress: float = 0.0        # 0-1 处理进度
    confidence: float = 0.0      # 0-1 置信度
    details: Dict = field(default_factory=dict)
    
    # 历史数据
    history: List[float] = field(default_factory=list)
    max_history = 20
    
    def update(self, score: float, status: Optional[LayerStatus] = None):
        """更新指标"""
        self.score = score
        if status:
            self.status = status
        
        # 更新历史
        self.history.append(score)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # 更新置信度(基于历史稳定性)
        if len(self.history) >= 3:
            variance = sum((x - sum(self.history) / len(self.history)) ** 2 
                          for x in self.history) / len(self.history)
            self.confidence = max(0, 1.0 - math.sqrt(variance) * 2)


@dataclass
class BFTConsensus:
    """BFT共识数据"""
    state: BFTState = BFTState.PENDING
    votes: List[bool] = field(default_factory=list)
    validators: List[str] = field(default_factory=list)
    threshold: float = 0.66      # 共识阈值
    current_ratio: float = 0.0   # 当前投票比例
    message_history: List[Dict] = field(default_factory=list)
    
    def add_vote(self, validator: str, vote: bool):
        """添加投票"""
        if validator not in self.validators:
            self.validators.append(validator)
            self.votes.append(vote)
            self.current_ratio = sum(self.votes) / len(self.votes) if self.votes else 0
        
        # 检查共识
        if len(self.votes) >= 3:
            if self.current_ratio >= self.threshold:
                self.state = BFTState.CONSENSUS_REACHED
            elif (1 - self.current_ratio) >= self.threshold:
                self.state = BFTState.CONSENSUS_FAILED
        else:
            self.state = BFTState.VOTING


@dataclass
class LeanProof:
    """Lean形式化证明状态"""
    is_proving: bool = False
    proof_complete: bool = False
    theorem_name: str = ""
    steps_completed: int = 0
    total_steps: int = 0
    current_step: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def get_progress(self) -> float:
        """获取证明进度"""
        if self.total_steps == 0:
            return 0.0
        return self.steps_completed / self.total_steps


class DIKWPPanel:
    """
    DIKWP状态实时仪表盘
    
    实现六层语义可视化：
    D(数据层) → I(信息层) → K(知识层) → W(智慧层) → P(目的层) → R(可靠层)
    
    融合：
    - 实时状态追踪
    - BFT共识验证
    - Lean形式化证明状态
    - 认知商数(CQ)计算
    """
    
    # 层级定义
    LAYERS = [
        {"id": "D", "name": "数据层", "full_name": "Data Layer", 
         "color": "#4FC3F7", "description": "原始数据采集与验证"},
        {"id": "I", "name": "信息层", "full_name": "Information Layer", 
         "color": "#81C784", "description": "实体识别与关系抽取"},
        {"id": "K", "name": "知识层", "full_name": "Knowledge Layer", 
         "color": "#FFD54F", "description": "知识图谱构建与推理"},
        {"id": "W", "name": "智慧层", "full_name": "Wisdom Layer", 
         "color": "#FF8A65", "description": "多策略融合与决策"},
        {"id": "P", "name": "目的层", "full_name": "Purpose Layer", 
         "color": "#BA68C8", "description": "意图对齐与伦理约束"},
        {"id": "R", "name": "可靠层", "full_name": "Reliability Layer", 
         "color": "#E57373", "description": "BFT共识与形式化验证"},
    ]
    
    def __init__(self):
        """初始化DIKWP仪表盘"""
        # 六层指标
        self.layers: Dict[str, LayerMetrics] = {}
        for layer_def in self.LAYERS:
            self.layers[layer_def["id"]] = LayerMetrics(
                name=layer_def["id"],
                full_name=layer_def["full_name"],
            )
        
        # BFT共识
        self.bft = BFTConsensus()
        
        # Lean证明
        self.lean_proof = LeanProof()
        
        # 综合指标
        self.cognitive_quotient: float = 0.0  # 认知商数
        self.processing_status: str = "idle"
        self.last_update: float = time.time()
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 历史记录
        self.cq_history: List[float] = []
        
        # 拓扑状态(用于可视化)
        self.topology_state = {
            "curvature": 0.5,
            "density": 0.5,
            "flow_direction": "forward",
            "anomalies": []
        }
    
    def update_layer(self, layer_id: str, score: float,
                    status: Optional[LayerStatus] = None,
                    details: Optional[Dict] = None):
        """
        更新指定层级的状态
        
        Args:
            layer_id: 层级ID (D/I/K/W/P/R)
            score: 评分 (0-1)
            status: 状态
            details: 详细信息
        """
        with self._lock:
            if layer_id not in self.layers:
                return
            
            layer = self.layers[layer_id]
            layer.update(score, status)
            
            if details:
                layer.details.update(details)
            
            # 更新处理进度
            if status == LayerStatus.PROCESSING:
                layer.progress = min(layer.progress + 0.1, 0.9)
            elif status == LayerStatus.COMPLETE:
                layer.progress = 1.0
            
            # 更新综合指标
            self._compute_cognitive_quotient()
            self.last_update = time.time()
    
    def _compute_cognitive_quotient(self):
        """计算认知商数(CQ)"""
        scores = []
        weights = {"D": 0.10, "I": 0.15, "K": 0.20, "W": 0.25, "P": 0.20, "R": 0.10}
        
        for layer_id, weight in weights.items():
            if layer_id in self.layers:
                score = self.layers[layer_id].score
                # 权重 × 分数
                weighted = score * weight
                
                # 置信度调整
                confidence = self.layers[layer_id].confidence
                weighted *= (0.5 + 0.5 * confidence)
                
                scores.append(weighted)
        
        # CQ = 加权和 + BFT共识加成
        cq = sum(scores)
        bft_bonus = 0.1 if self.bft.state == BFTState.CONSENSUS_REACHED else 0.0
        self.cognitive_quotient = min(cq + bft_bonus, 1.0)
        
        # 更新历史
        self.cq_history.append(self.cognitive_quotient)
        if len(self.cq_history) > 50:
            self.cq_history.pop(0)
    
    def update_bft_vote(self, validator: str, vote: bool):
        """更新BFT投票"""
        with self._lock:
            self.bft.add_vote(validator, vote)
            
            # 更新可靠层状态
            if self.bft.state == BFTState.CONSENSUS_REACHED:
                self.layers["R"].status = LayerStatus.COMPLETE
                self.layers["R"].score = self.bft.current_ratio
                self.layers["R"].details["consensus"] = "reached"
            elif self.bft.state == BFTState.CONSENSUS_FAILED:
                self.layers["R"].status = LayerStatus.ERROR
                self.layers["R"].score = self.bft.current_ratio
                self.layers["R"].details["consensus"] = "failed"
            
            self._compute_cognitive_quotient()
    
    def start_lean_proof(self, theorem: str, steps: int):
        """开始Lean形式化证明"""
        with self._lock:
            self.lean_proof.is_proving = True
            self.lean_proof.proof_complete = False
            self.lean_proof.theorem_name = theorem
            self.lean_proof.total_steps = steps
            self.lean_proof.steps_completed = 0
            self.lean_proof.errors = []
            self.lean_proof.warnings = []
    
    def update_lean_proof(self, step: int, current_step: str,
                         error: Optional[str] = None,
                         warning: Optional[str] = None):
        """更新Lean证明进度"""
        with self._lock:
            self.lean_proof.steps_completed = step
            self.lean_proof.current_step = current_step
            
            if error:
                self.lean_proof.errors.append(error)
                self.layers["R"].status = LayerStatus.WARNING
            
            if warning:
                self.lean_proof.warnings.append(warning)
    
    def complete_lean_proof(self, success: bool):
        """完成Lean证明"""
        with self._lock:
            self.lean_proof.is_proving = False
            self.lean_proof.proof_complete = success
            
            if success:
                self.layers["R"].status = LayerStatus.COMPLETE
                self.layers["R"].score = 1.0
            else:
                self.layers["R"].status = LayerStatus.ERROR
    
    def get_layer_status(self, layer_id: str) -> Dict[str, Any]:
        """获取指定层级状态"""
        if layer_id not in self.layers:
            return {}
        
        layer = self.layers[layer_id]
        
        # 查找层级定义
        layer_def = next((d for d in self.LAYERS if d["id"] == layer_id), {})
        
        return {
            "id": layer_id,
            "name": layer.name,
            "full_name": layer_def.get("full_name", ""),
            "color": layer_def.get("color", "#888888"),
            "description": layer_def.get("description", ""),
            "score": layer.score,
            "status": layer.status.value,
            "progress": layer.progress,
            "confidence": layer.confidence,
            "history": layer.history.copy(),
            "details": layer.details.copy(),
        }
    
    def get_full_status(self) -> Dict[str, Any]:
        """获取完整状态"""
        with self._lock:
            # 获取所有层级状态
            layers_status = []
            for layer_def in self.LAYERS:
                layer_id = layer_def["id"]
                if layer_id in self.layers:
                    layers_status.append(self.get_layer_status(layer_id))
            
            # BFT状态
            bft_status = {
                "state": self.bft.state.value,
                "votes": self.bft.votes.copy(),
                "validators": self.bft.validators.copy(),
                "ratio": self.bft.current_ratio,
                "threshold": self.bft.threshold,
            }
            
            # Lean证明状态
            lean_status = {
                "is_proving": self.lean_proof.is_proving,
                "proof_complete": self.lean_proof.proof_complete,
                "theorem_name": self.lean_proof.theorem_name,
                "progress": self.lean_proof.get_progress(),
                "steps": f"{self.lean_proof.steps_completed}/{self.lean_proof.total_steps}",
                "current_step": self.lean_proof.current_step,
                "errors": self.lean_proof.errors.copy(),
                "warnings": self.lean_proof.warnings.copy(),
            }
            
            return {
                "layers": layers_status,
                "cognitive_quotient": self.cognitive_quotient,
                "cq_history": self.cq_history.copy(),
                "bft": bft_status,
                "lean_proof": lean_status,
                "processing_status": self.processing_status,
                "last_update": self.last_update,
                "topology_state": self.topology_state.copy(),
            }
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """
        获取可视化数据
        用于渲染实时仪表盘
        """
        status = self.get_full_status()
        
        # 雷达图数据
        radar_data = {
            "labels": [layer["name"] for layer in status["layers"]],
            "values": [layer["score"] for layer in status["layers"]],
            "colors": [layer["color"] for layer in status["layers"]],
        }
        
        # 进度条数据
        progress_data = []
        for layer in status["layers"]:
            # 进度条颜色映射
            color = layer["color"]
            if layer["status"] == "error":
                color = "#E57373"
            elif layer["status"] == "warning":
                color = "#FFB74D"
            
            progress_data.append({
                "label": layer["name"],
                "value": layer["score"],
                "progress": layer["progress"],
                "color": color,
                "status": layer["status"],
            })
        
        # CQ仪表盘
        cq_gauge = {
            "value": status["cognitive_quotient"],
            "history": status["cq_history"],
            "trend": "up" if len(status["cq_history"]) >= 2 and 
                    status["cq_history"][-1] > status["cq_history"][-2] else "down",
        }
        
        # BFT状态
        bft_visual = {
            "state": status["bft"]["state"],
            "votes": status["bft"]["votes"],
            "ratio": status["bft"]["ratio"],
            "validators": len(status["bft"]["validators"]),
        }
        
        # Lean证明状态
        lean_visual = {
            "is_active": status["lean_proof"]["is_proving"],
            "theorem": status["lean_proof"]["theorem_name"],
            "progress": status["lean_proof"]["progress"],
            "steps": status["lean_proof"]["steps"],
            "has_errors": len(status["lean_proof"]["errors"]) > 0,
        }
        
        return {
            "radar": radar_data,
            "progress": progress_data,
            "cq_gauge": cq_gauge,
            "bft": bft_visual,
            "lean": lean_visual,
            "topology": status["topology_state"],
        }
    
    def get_ascii_status(self) -> str:
        """获取ASCII艺术状态显示"""
        status = self.get_full_status()
        
        lines = []
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│              DIKWP 实时状态仪表盘                       │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        
        # 六层进度条
        for layer in status["layers"]:
            bar_len = 20
            filled = int(layer["score"] * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            pct = int(layer["score"] * 100)
            
            status_icon = {
                "active": "●",
                "processing": "◐",
                "complete": "✓",
                "warning": "⚠",
                "error": "✗",
                "pending": "○"
            }.get(layer["status"], "○")
            
            lines.append(f"│ {layer['name']}[{layer['full_name']:15}] {status_icon} {bar} {pct:3d}% │")
        
        lines.append("├─────────────────────────────────────────────────────────┤")
        
        # CQ评分
        cq = status["cognitive_quotient"]
        cq_bar_len = 30
        cq_filled = int(cq * cq_bar_len)
        cq_bar = "█" * cq_filled + "░" * (cq_bar_len - cq_filled)
        cq_pct = int(cq * 100)
        
        lines.append(f"│ 综合认知商数(CQ): {cq_bar} {cq_pct:3d}%              │")
        
        lines.append("├─────────────────────────────────────────────────────────┤")
        
        # BFT状态
        bft_state = status["bft"]["state"]
        bft_ratio = status["bft"]["ratio"]
        lines.append(f"│ BFT共识状态: {bft_state:20} 投票比: {bft_ratio:.2f}        │")
        
        # Lean证明状态
        lean = status["lean_proof"]
        if lean["is_proving"]:
            lines.append(f"│ Lean证明: {lean['theorem_name'][:20]:20} [{lean['steps']}]       │")
        elif lean["proof_complete"]:
            lines.append(f"│ Lean证明: ✓ {lean['theorem_name'][:30]:30} │")
        
        lines.append("└─────────────────────────────────────────────────────────┘")
        
        return "\n".join(lines)
    
    def reset(self):
        """重置仪表盘"""
        with self._lock:
            for layer_id in self.layers:
                self.layers[layer_id] = LayerMetrics(
                    name=layer_id,
                    full_name=self.layers[layer_id].full_name,
                )
            
            self.bft = BFTConsensus()
            self.lean_proof = LeanProof()
            self.cognitive_quotient = 0.0
            self.processing_status = "idle"
            self.cq_history = []


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 创建仪表盘
    panel = DIKWPPanel()
    
    print("=== DIKWP状态实时仪表盘测试 ===\n")
    
    # 模拟处理流程
    print("模拟处理流程...")
    
    # D层处理
    panel.update_layer("D", 0.0, LayerStatus.PROCESSING)
    time.sleep(0.1)
    panel.update_layer("D", 0.85, LayerStatus.COMPLETE)
    
    # I层处理
    panel.update_layer("I", 0.0, LayerStatus.PROCESSING)
    time.sleep(0.1)
    panel.update_layer("I", 0.92, LayerStatus.COMPLETE)
    
    # K层处理
    panel.update_layer("K", 0.0, LayerStatus.PROCESSING)
    time.sleep(0.1)
    panel.update_layer("K", 0.78, LayerStatus.COMPLETE)
    
    # W层处理
    panel.update_layer("W", 0.0, LayerStatus.PROCESSING)
    time.sleep(0.1)
    panel.update_layer("W", 0.88, LayerStatus.COMPLETE)
    
    # P层处理
    panel.update_layer("P", 0.0, LayerStatus.PROCESSING)
    time.sleep(0.1)
    panel.update_layer("P", 0.95, LayerStatus.COMPLETE)
    
    # BFT投票
    print("\n模拟BFT共识...")
    panel.update_bft_vote("validator_1", True)
    panel.update_bft_vote("validator_2", True)
    panel.update_bft_vote("validator_3", True)
    
    # Lean证明
    print("模拟Lean形式化证明...")
    panel.start_lean_proof("prime_zero_duality", 10)
    for i in range(10):
        panel.update_lean_proof(i, f"step_{i}_verified")
    panel.complete_lean_proof(True)
    
    # 显示ASCII状态
    print(panel.get_ascii_status())
    
    # 显示可视化数据
    print("\n=== 可视化数据 ===")
    viz = panel.get_visualization_data()
    
    print(f"\n雷达图数据: {viz['radar']}")
    print(f"\nCQ仪表盘: {viz['cq_gauge']}")
    print(f"\nBFT状态: {viz['bft']}")
    print(f"\nLean状态: {viz['lean']}")
    
    # 完整状态
    print("\n=== 完整状态数据 ===")
    full_status = panel.get_full_status()
    print(f"认知商数: {full_status['cognitive_quotient']:.4f}")
    print(f"处理状态: {full_status['processing_status']}")
    print(f"最后更新: {time.ctime(full_status['last_update'])}")
