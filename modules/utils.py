"""
utils.py - 工具函数

提供AGI系统所需的通用工具函数：
- 日志功能：记录系统运行状态和事件
- 数据格式化：统一数据展示格式
- 时间工具：时间相关辅助函数
- 验证工具：输入验证和错误处理
"""

import time
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class AGILogger:
    """AGI系统日志器"""
    
    def __init__(self, name: str = "AGI", level: str = "INFO"):
        self.name = name
        self.level = level
        self.levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        self.logs: List[Dict] = []
        self.max_logs = 200
    
    def _log(self, level: str, message: str, data: Any = None) -> None:
        """记录日志"""
        if self.levels.get(level, 1) < self.levels.get(self.level, 1):
            return
        
        entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
            "data": data
        }
        self.logs.append(entry)
        
        # 控制台输出
        print(f"[{entry['datetime']}] {self.name}.{level}: {message}")
        if data is not None:
            print(f"  Data: {data}")
        
        # 限制日志数量
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
    
    def debug(self, message: str, data: Any = None) -> None:
        self._log("DEBUG", message, data)
    
    def info(self, message: str, data: Any = None) -> None:
        self._log("INFO", message, data)
    
    def warning(self, message: str, data: Any = None) -> None:
        self._log("WARNING", message, data)
    
    def error(self, message: str, data: Any = None) -> None:
        self._log("ERROR", message, data)
    
    def get_logs(self, level: str = None, count: int = 50) -> List[Dict]:
        """获取日志记录"""
        filtered = self.logs
        if level:
            filtered = [l for l in self.logs if l["level"] == level]
        return filtered[-count:]
    
    def clear(self) -> None:
        """清空日志"""
        self.logs.clear()


def format_dict(data: Dict, indent: int = 2, max_depth: int = 3, current_depth: int = 0) -> str:
    """格式化字典为可读字符串"""
    if current_depth >= max_depth:
        return "..."
    
    if not data:
        return "{}"
    
    lines = []
    spaces = " " * (indent * current_depth)
    
    for key, value in data.items():
        if isinstance(value, dict):
            formatted = format_dict(value, indent, max_depth, current_depth + 1)
            lines.append(f"{spaces}{key}: {formatted}")
        elif isinstance(value, (list, tuple)):
            if len(value) > 3:
                lines.append(f"{spaces}{key}: [{len(value)} items]")
            else:
                lines.append(f"{spaces}{key}: {value}")
        else:
            lines.append(f"{spaces}{key}: {value}")
    
    return "\n".join(lines)


def format_complex_state(unit) -> str:
    """格式化复合体状态为可读字符串"""
    from modules.agi_core import ComplexUnit
    
    if not isinstance(unit, ComplexUnit):
        return str(unit)
    
    energy_bar = _make_bar(unit.energy, 20, "█", "░")
    attention_bar = _make_bar(unit.attention_weight, 20, "●", "○")
    
    return (
        f"ComplexUnit: {unit.id}\n"
        f"  Layer: {unit.layer.value}\n"
        f"  Energy: {energy_bar} {unit.energy:.2f}\n"
        f"  Attention: {attention_bar} {unit.attention_weight:.2f}\n"
        f"  State: {format_dict(unit.state, max_depth=2)}"
    )


def _make_bar(value: float, length: int, fill_char: str, empty_char: str) -> str:
    """创建进度条字符串"""
    filled = int(value * length)
    return fill_char * filled + empty_char * (length - filled)


def format_network_visualization(network) -> str:
    """生成网络结构的可视化文本"""
    from modules.agi_core import ComplexNetwork, LayerType
    
    if not isinstance(network, ComplexNetwork):
        return str(network)
    
    lines = ["复合体网络结构:", "=" * 40]
    
    for layer in LayerType:
        units = network.get_layer_units(layer)
        if not units:
            continue
        
        lines.append(f"\n{layer.value.upper()} 层:")
        for unit in units:
            energy = _make_bar(unit.energy, 10, "█", "░")
            lines.append(f"  {unit.id}: {energy} ({unit.energy:.2f})")
            
            # 显示连接
            if unit.outputs:
                lines.append(f"    -> {', '.join(unit.outputs)}")
    
    return "\n".join(lines)


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception as e:
        return f'{{"error": "JSON serialization failed: {str(e)}"}}'


def time_it(func: callable, *args, **kwargs) -> tuple:
    """测量函数执行时间，返回(结果, 耗时)"""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


def validate_positive_number(value: Any, name: str = "value") -> float:
    """验证值为正数，否则抛出异常"""
    try:
        num = float(value)
        if num < 0:
            raise ValueError(f"{name} must be non-negative, got {value}")
        return num
    except (TypeError, ValueError) as e:
        raise ValueError(f"{name} must be a valid number, got {value}") from e


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """将值限制在指定范围内"""
    return max(min_val, min(max_val, value))


def calculate_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度（简单版：基于字符重叠）"""
    if not str1 or not str2:
        return 0.0
    
    set1 = set(str1.lower())
    set2 = set(str2.lower())
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


class Timer:
    """简单计时器"""
    
    def __init__(self):
        self.start_time = None
        self.elapsed = 0.0
    
    def start(self) -> None:
        self.start_time = time.time()
    
    def stop(self) -> float:
        if self.start_time is not None:
            self.elapsed = time.time() - self.start_time
            self.start_time = None
        return self.elapsed
    
    def get_elapsed(self) -> float:
        if self.start_time is not None:
            return time.time() - self.start_time
        return self.elapsed


def print_separator(char: str = "=", length: int = 60) -> None:
    """打印分隔线"""
    print(char * length)


def print_header(text: str, char: str = "=") -> None:
    """打印标题"""
    print(f"\n{char * 60}")
    print(f"  {text}")
    print(f"{char * 60}\n")
