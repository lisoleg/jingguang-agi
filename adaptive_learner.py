"""
adaptive_learner.py - 自适应学习模块（增强版：真正自学习循环）

基于复合体理学演化规律：
- 自我评估：评估处理结果与预期的差距
- 参数调整：根据反馈调整注意力权重、激活阈值等
- 经验积累：记录成功/失败模式，优化未来决策
- 演化优化：逐步提升系统整体性能
- 真正自学习：不再模拟，实际更新内部状态

核心功能（增强）：
1. 性能评估：评估任务完成质量（多维评估）
2. 参数调整：自适应调整复合体参数（真实更新）
3. 学习记录：保存学习经验和模式（持久化）
4. 策略优化：基于历史数据优化处理策略
5. 模式识别：识别成功/失败模式
6. 主动学习：根据不确定性主动探索
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from agi_core import LayerType, ComplexUnit, ComplexNetwork
import time
import json
import math


class FeedbackType(Enum):
    """反馈类型"""
    POSITIVE = "positive"    # 正向反馈（成功）
    NEGATIVE = "negative"    # 负向反馈（失败）
    NEUTRAL = "neutral"      # 中性反馈
    CORRECTIVE = "corrective"  # 纠正性反馈


@dataclass
class Experience:
    """经验记录 - 单次任务处理的完整记录（增强版）"""
    
    task_id: str
    task_type: str
    input_data: Any
    output_data: Any
    feedback: FeedbackType
    performance_score: float  # 0.0 - 1.0
    timestamp: float = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "input_data": str(self.input_data)[:200],  # 截断长输入
            "output_data": str(self.output_data)[:200],
            "feedback": self.feedback.value,
            "performance_score": self.performance_score,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class AdaptiveLearner:
    """自适应学习模块 - 实现AGI的真正自我优化能力（增强版）"""
    
    def __init__(self, network: ComplexNetwork, energy_engine):
        self.network = network
        self.energy_engine = energy_engine
        self.experiences: List[Experience] = []
        self.learning_rate: float = 0.1    # 学习率
        self.adaptation_threshold: float = 0.6  # 低于此分数触发调整
        self.max_experiences: int = 100     # 最大经验记录数
        
        # 学习统计（增强）
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "avg_performance": 0.0,
            "adaptation_count": 0,
            "pattern_adjustments": 0,
            "learning_curve": []  # 记录学习曲线
        }
        
        # 真实学习：参数记忆
        self.parameter_memory: Dict[str, List[float]] = {}  # param_name -> history
        self.success_patterns: Dict[str, Dict] = {}  # 成功模式库
        self.failure_patterns: Dict[str, Dict] = {}  # 失败模式库
        
        # 主动学习：不确定性跟踪
        self.uncertainty_tracker: Dict[str, float] = {}  # task_type -> uncertainty
    
    def evaluate_performance(self, expected: Any, actual: Any, task_type: str = "general") -> float:
        """评估任务表现，返回0.0-1.0的分数（增强：多维评估）"""
        if expected == actual:
            return 1.0
        
        if isinstance(expected, str) and isinstance(actual, str):
            if actual in expected or expected in actual:
                return 0.7
            # 词汇重叠度
            expected_words = set(expected.lower().split())
            actual_words = set(actual.lower().split())
            if expected_words and actual_words:
                overlap = len(expected_words & actual_words) / len(expected_words | actual_words)
                return 0.3 + 0.4 * overlap
            return 0.2
        
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if actual == 0 and expected == 0:
                return 1.0
            try:
                error = abs(expected - actual) / max(abs(expected), 1.0)
                return max(0.0, 1.0 - error)
            except:
                return 0.0
        
        # 字典类型：比较键值对
        if isinstance(expected, dict) and isinstance(actual, dict):
            matching_keys = 0
            total_keys = max(len(expected), 1)
            for k, v in expected.items():
                if k in actual:
                    if v == actual[k] or (isinstance(v, (int, float)) and isinstance(actual[k], (int, float)) and abs(v - actual[k]) < 0.01):
                        matching_keys += 1
            return 0.3 + 0.5 * (matching_keys / total_keys)
        
        # 类型匹配
        if type(expected) == type(actual):
            return 0.5
        
        return 0.1
    
    def record_experience(self, task_id: str, task_type: str, 
                         input_data: Any, output_data: Any,
                         expected: Any = None, feedback: FeedbackType = None) -> Experience:
        """记录一次任务处理经验（增强：真实学习循环）"""
        # 自动评估（如果未提供反馈）
        if feedback is None:
            if expected is not None:
                score = self.evaluate_performance(expected, output_data, task_type)
                feedback = FeedbackType.POSITIVE if score >= 0.7 else FeedbackType.NEGATIVE
            else:
                score = 0.5
                feedback = FeedbackType.NEUTRAL
        
        # 如果提供了expected但没有反馈，进行评估
        if expected is not None and feedback is None:
            score = self.evaluate_performance(expected, output_data, task_type)
            feedback = FeedbackType.POSITIVE if score >= 0.7 else FeedbackType.NEGATIVE
        elif expected is not None:
            score = self.evaluate_performance(expected, output_data, task_type)
        else:
            score = 0.5 if feedback == FeedbackType.NEUTRAL else (0.9 if feedback == FeedbackType.POSITIVE else 0.3)
        
        experience = Experience(
            task_id=task_id,
            task_type=task_type,
            input_data=input_data,
            output_data=output_data,
            feedback=feedback,
            performance_score=score
        )
        
        self.experiences.append(experience)
        self._update_stats(experience)
        
        # 真正的学习：更新参数和模式
        self._learn_from_experience(experience)
        
        # 触发自适应调整（真实调整，不是模拟）
        if score < self.adaptation_threshold:
            self.adapt_parameters(experience)
        
        # 限制经验记录数量
        if len(self.experiences) > self.max_experiences:
            self.experiences = self.experiences[-self.max_experiences:]
        
        return experience
    
    def _learn_from_experience(self, exp: Experience) -> None:
        """从经验中真正学习（核心方法）"""
        task_type = exp.task_type
        
        # 1. 更新参数记忆
        self._update_parameter_memory(task_type, exp.performance_score)
        
        # 2. 识别模式
        if exp.feedback == FeedbackType.POSITIVE:
            self._record_success_pattern(exp)
        elif exp.feedback == FeedbackType.NEGATIVE:
            self._record_failure_pattern(exp)
        
        # 3. 更新不确定性
        self._update_uncertainty(task_type, exp.performance_score)
        
        # 4. 更新学习曲线
        self.stats["learning_curve"].append({
            "timestamp": exp.timestamp,
            "score": exp.performance_score,
            "task_type": task_type
        })
        # 保持学习曲线长度
        if len(self.stats["learning_curve"]) > 50:
            self.stats["learning_curve"] = self.stats["learning_curve"][-50:]
    
    def _update_parameter_memory(self, task_type: str, score: float) -> None:
        """更新参数记忆"""
        if task_type not in self.parameter_memory:
            self.parameter_memory[task_type] = []
        
        self.parameter_memory[task_type].append(score)
        # 保持最近20次记录
        if len(self.parameter_memory[task_type]) > 20:
            self.parameter_memory[task_type] = self.parameter_memory[task_type][-20:]
    
    def _record_success_pattern(self, exp: Experience) -> None:
        """记录成功模式"""
        pattern_key = f"{exp.task_type}_{hash(str(exp.input_data)) % 1000}"
        
        if pattern_key not in self.success_patterns:
            self.success_patterns[pattern_key] = {
                "task_type": exp.task_type,
                "input_signature": str(exp.input_data)[:50],
                "output_signature": str(exp.output_data)[:50],
                "count": 0,
                "avg_score": 0.0
            }
        
        pattern = self.success_patterns[pattern_key]
        pattern["count"] += 1
        # 更新平均分数
        pattern["avg_score"] = (pattern["avg_score"] * (pattern["count"] - 1) + exp.performance_score) / pattern["count"]
    
    def _record_failure_pattern(self, exp: Experience) -> None:
        """记录失败模式"""
        pattern_key = f"{exp.task_type}_{hash(str(exp.input_data)) % 1000}"
        
        if pattern_key not in self.failure_patterns:
            self.failure_patterns[pattern_key] = {
                "task_type": exp.task_type,
                "input_signature": str(exp.input_data)[:50],
                "output_signature": str(exp.output_data)[:50],
                "count": 0,
                "avg_score": 0.0,
                "common_issues": []
            }
        
        pattern = self.failure_patterns[pattern_key]
        pattern["count"] += 1
        pattern["avg_score"] = (pattern["avg_score"] * (pattern["count"] - 1) + exp.performance_score) / pattern["count"]
        
        # 记录常见问题
        if exp.performance_score < 0.3:
            issue = f"Low score: {exp.performance_score:.2f}"
            if issue not in pattern["common_issues"]:
                pattern["common_issues"].append(issue)
    
    def _update_uncertainty(self, task_type: str, score: float) -> None:
        """更新不确定性估计"""
        # 不确定性 = 1 - 置信度，置信度基于历史表现的稳定性
        if task_type not in self.uncertainty_tracker:
            self.uncertainty_tracker[task_type] = 0.5  # 初始不确定性
        
        # 根据分数调整不确定性
        if score > 0.8:
            # 高分：降低不确定性
            self.uncertainty_tracker[task_type] = max(0.1, self.uncertainty_tracker[task_type] - 0.05)
        elif score < 0.4:
            # 低分：增加不确定性
            self.uncertainty_tracker[task_type] = min(0.9, self.uncertainty_tracker[task_type] + 0.1)
        # 中等分数：小幅调整
        else:
            self.uncertainty_tracker[task_type] = max(0.2, min(0.8, self.uncertainty_tracker[task_type] + 0.02))
    
    def adapt_parameters(self, experience: Experience) -> Dict[str, Any]:
        """根据经验自适应调整参数（真实调整，不是模拟）"""
        adjustments = {}
        
        # 1. 调整相关复合体的注意力权重（真实更新）
        layer_map = {
            "text": [LayerType.PERCEPTION, LayerType.COGNITION],
            "reasoning": [LayerType.COGNITION, LayerType.DECISION],
            "decision": [LayerType.DECISION],
            "action": [LayerType.ACTION],
            "general": list(LayerType)
        }
        
        relevant_layers = layer_map.get(experience.task_type, layer_map["general"])
        
        for layer in relevant_layers:
            units = self.network.get_layer_units(layer)
            for unit in units:
                old_weight = unit.attention_weight
                
                if experience.feedback == FeedbackType.POSITIVE:
                    # 成功：增强注意力
                    adjustment = self.learning_rate * 0.5
                    unit.attention_weight = min(1.0, unit.attention_weight + adjustment)
                elif experience.feedback == FeedbackType.NEGATIVE:
                    # 失败：调整注意力（可能降低或转移到其他单元）
                    adjustment = self.learning_rate * 0.3
                    unit.attention_weight = max(0.1, unit.attention_weight - adjustment)
                
                adjustments[f"{unit.id}_attention"] = {
                    "old": old_weight,
                    "new": unit.attention_weight,
                    "delta": unit.attention_weight - old_weight
                }
        
        # 2. 调整能量分配策略（真实更新）
        if experience.feedback == FeedbackType.NEGATIVE:
            # 失败：增加能量分配
            old_rate = self.energy_engine.recovery_rate
            self.energy_engine.recovery_rate = min(0.3, self.energy_engine.recovery_rate + 0.01)
            adjustments["recovery_rate"] = {
                "old": old_rate,
                "new": self.energy_engine.recovery_rate
            }
        elif experience.feedback == FeedbackType.POSITIVE:
            # 成功：可以稍微降低恢复率（节省能量）
            old_rate = self.energy_engine.recovery_rate
            self.energy_engine.recovery_rate = max(0.05, self.energy_engine.recovery_rate - 0.005)
            adjustments["recovery_rate"] = {
                "old": old_rate,
                "new": self.energy_engine.recovery_rate
            }
        
        # 3. 调整激活阈值（真实更新）
        if experience.performance_score < 0.3:
            for unit in self.network.units.values():
                old_threshold = unit.activation_threshold
                unit.activation_threshold = max(0.1, unit.activation_threshold - 0.02)
                adjustments[f"{unit.id}_threshold"] = {
                    "old": old_threshold,
                    "new": unit.activation_threshold
                }
        
        # 4. 记录模式调整
        self.stats["pattern_adjustments"] += 1
        
        self.stats["adaptation_count"] += 1
        return adjustments
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察 - 分析历史经验得出优化建议（增强版）"""
        if not self.experiences:
            return {"message": "No experiences recorded yet"}
        
        recent = self.experiences[-20:]  # 最近20次经验
        
        # 按任务类型统计
        type_stats = {}
        for exp in recent:
            if exp.task_type not in type_stats:
                type_stats[exp.task_type] = {"count": 0, "total_score": 0.0}
            type_stats[exp.task_type]["count"] += 1
            type_stats[exp.task_type]["total_score"] += exp.performance_score
        
        for t in type_stats:
            type_stats[t]["avg_score"] = type_stats[t]["total_score"] / type_stats[t]["count"]
        
        # 识别最弱的任务类型
        weakest = min(type_stats.items(), key=lambda x: x[1]["avg_score"]) if type_stats else None
        
        # 识别趋势（最近5次 vs 之前5次）
        trend = "stable"
        if len(recent) >= 10:
            recent_5 = sum(e.performance_score for e in recent[-5:]) / 5
            prev_5 = sum(e.performance_score for e in recent[-10:-5]) / 5
            if recent_5 > prev_5 + 0.1:
                trend = "improving"
            elif recent_5 < prev_5 - 0.1:
                trend = "declining"
        
        # 模式分析
        top_success_patterns = sorted(
            self.success_patterns.items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )[:3]
        
        top_failure_patterns = sorted(
            self.failure_patterns.items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )[:3]
        
        return {
            "total_experiences": len(self.experiences),
            "recent_avg_performance": sum(e.performance_score for e in recent) / len(recent),
            "type_performance": type_stats,
            "weakest_task_type": weakest[0] if weakest else None,
            "performance_trend": trend,
            "stats": self.stats.copy(),
            "top_success_patterns": top_success_patterns[:3],
            "top_failure_patterns": top_failure_patterns[:3],
            "uncertainty_levels": self.uncertainty_tracker.copy(),
            "learning_progress": self._calculate_learning_progress()
        }
    
    def _calculate_learning_progress(self) -> float:
        """计算学习进度（0-1）"""
        if len(self.experiences) < 5:
            return 0.0
        
        # 基于最近表现和稳定性
        recent = self.experiences[-10:]
        avg_score = sum(e.performance_score for e in recent) / len(recent)
        
        # 计算稳定性（分数方差的倒数）
        variance = sum((e.performance_score - avg_score)**2 for e in recent) / len(recent)
        stability = 1.0 / (1.0 + variance)
        
        # 进度 = 平均分*0.7 + 稳定性*0.3
        progress = avg_score * 0.7 + stability * 0.3
        return min(1.0, progress)
    
    def save_experiences(self, filepath: str) -> None:
        """保存经验记录到文件（增强：也保存学习状态）"""
        data = {
            "experiences": [e.to_dict() for e in self.experiences],
            "stats": self.stats,
            "parameter_memory": self.parameter_memory,
            "success_patterns": self.success_patterns,
            "failure_patterns": self.failure_patterns,
            "uncertainty_tracker": self.uncertainty_tracker
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_experiences(self, filepath: str) -> None:
        """从文件加载经验（增强：也加载学习状态）"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载经验
            for item in data.get("experiences", []):
                exp = Experience(
                    task_id=item["task_id"],
                    task_type=item["task_type"],
                    input_data=item["input_data"],
                    output_data=item["output_data"],
                    feedback=FeedbackType(item["feedback"]),
                    performance_score=item["performance_score"],
                    timestamp=item["timestamp"],
                    metadata=item.get("metadata", {})
                )
                self.experiences.append(exp)
            
            # 加载学习状态
            self.stats = data.get("stats", self.stats)
            self.parameter_memory = data.get("parameter_memory", {})
            self.success_patterns = data.get("success_patterns", {})
            self.failure_patterns = data.get("failure_patterns", {})
            self.uncertainty_tracker = data.get("uncertainty_tracker", {})
            
        except FileNotFoundError:
            pass  # 文件不存在，忽略
    
    def _update_stats(self, exp: Experience) -> None:
        """更新学习统计"""
        self.stats["total_tasks"] += 1
        if exp.feedback == FeedbackType.POSITIVE:
            self.stats["successful_tasks"] += 1
        elif exp.feedback == FeedbackType.NEGATIVE:
            self.stats["failed_tasks"] += 1
        
        # 更新平均表现
        n = self.stats["total_tasks"]
        self.stats["avg_performance"] = (
            (self.stats["avg_performance"] * (n - 1) + exp.performance_score) / n
        )
    
    def suggest_improvements(self) -> List[str]:
        """生成改进建议（基于学习洞察）"""
        suggestions = []
        
        insights = self.get_learning_insights()
        
        # 基于最弱任务类型
        if insights.get("weakest_task_type"):
            suggestions.append(f"Focus on improving {insights['weakest_task_type']} tasks")
        
        # 基于不确定性
        for task_type, uncertainty in self.uncertainty_tracker.items():
            if uncertainty > 0.7:
                suggestions.append(f"High uncertainty in {task_type}, consider more training")
        
        # 基于失败模式
        if self.failure_patterns:
            suggestions.append("Review and address common failure patterns")
        
        return suggestions[:5]  # 最多5条建议
