"""
增量加载机制模块

实现AGI系统的增量/懒加载，支持：
1. 模块按需加载（Lazy Loading）
2. 大型数据集分块加载（Chunked Loading）
3. 加载进度跟踪
4. 优先级加载（关键模块优先）
5. 内存-aware加载（避免OOM）
"""

import importlib
import sys
import time
import threading
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from enum import Enum
from dataclasses import dataclass, field
import logging

T = TypeVar('T')


class LoadingPriority(Enum):
    """加载优先级"""
    CRITICAL = 0  # 关键模块（必须最先加载）
    HIGH = 1      # 高优先级
    NORMAL = 2    # 正常优先级
    LOW = 3       # 低优先级（可以延迟加载）


class LoadingStatus(Enum):
    """加载状态"""
    PENDING = "pending"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    DEFERRED = "deferred"  # 已推迟（内存不足等）


@dataclass
class LoadableModule(Generic[T]):
    """可加载模块描述"""
    name: str
    loader: Callable[[], T]  # 加载函数
    priority: LoadingPriority = LoadingPriority.NORMAL
    status: LoadingStatus = LoadingStatus.PENDING
    instance: Optional[T] = None
    error: Optional[str] = None
    load_time: float = 0.0
    memory_mb: float = 0.0
    dependencies: List[str] = field(default_factory=list)


class IncrementalLoader:
    """
    增量加载器
    
    支持特性：
    - 按需加载（Lazy Loading）
    - 优先级加载
    - 进度跟踪
    - 内存限制
    - 依赖管理
    """
    
    def __init__(self, max_memory_mb: float = 2048.0):
        """
        初始化增量加载器
        
        参数:
            max_memory_mb: 最大内存使用量（MB），超过后推迟低优先级加载
        """
        self.modules: Dict[str, LoadableModule] = {}
        self.loading_order: List[str] = []
        self.max_memory_mb = max_memory_mb
        self.used_memory_mb = 0.0
        self._lock = threading.Lock()
        self._loading = False
        
    def register(self, 
                 name: str, 
                 loader: Callable[[], T],
                 priority: LoadingPriority = LoadingPriority.NORMAL,
                 dependencies: Optional[List[str]] = None) -> 'IncrementalLoader':
        """
        注册可加载模块
        
        用法:
            loader.register('knowledge_graph', load_kg, priority=LoadingPriority.HIGH)
        """
        with self._lock:
            self.modules[name] = LoadableModule(
                name=name,
                loader=loader,
                priority=priority,
                dependencies=dependencies or []
            )
        return self  # 支持链式调用
    
    def load_critical(self) -> Dict[str, Any]:
        """
        加载所有CRITICAL优先级模块（同步阻塞）
        
        返回:
            已加载模块实例字典
        """
        return self._load_by_priority(LoadingPriority.CRITICAL)
    
    def load_all(self, callback: Optional[Callable[[str, float], None]] = None):
        """
        加载所有模块（按优先级顺序）
        
        参数:
            callback: 进度回调函数，接收(module_name, progress_ratio)
        """
        self._loading = True
        
        # 按优先级排序
        sorted_modules = sorted(
            self.modules.values(),
            key=lambda m: (m.priority.value, m.name)
        )
        
        total = len(sorted_modules)
        
        for i, module in enumerate(sorted_modules):
            if not self._loading:  # 允许取消
                break
                
            progress = i / total
            if callback:
                callback(module.name, progress)
            
            self._load_module(module)
        
        if callback:
            callback('complete', 1.0)
        
        self._loading = False
    
    def load_on_demand(self, name: str) -> Optional[Any]:
        """
        按需加载模块（懒加载核心方法）
        
        参数:
            name: 模块名称
            
        返回:
            模块实例，失败返回None
            
        用法:
            kg = loader.load_on_demand('knowledge_graph')
        """
        with self._lock:
            if name not in self.modules:
                raise ValueError(f"Module '{name}' not registered")
            
            module = self.modules[name]
            
            # 已加载，直接返回
            if module.status == LoadingStatus.LOADED:
                return module.instance
            
            # 加载中，等待完成
            if module.status == LoadingStatus.LOADING:
                # 简单实现：递归加载（实际应该用条件变量）
                return None
        
        # 检查依赖
        self._ensure_dependencies(name)
        
        # 执行加载
        self._load_module(self.modules[name])
        
        return self.modules[name].instance
    
    def _ensure_dependencies(self, name: str):
        """确保依赖模块已加载"""
        module = self.modules[name]
        for dep in module.dependencies:
            if dep in self.modules:
                dep_module = self.modules[dep]
                if dep_module.status != LoadingStatus.LOADED:
                    self.load_on_demand(dep)
    
    def _load_module(self, module: LoadableModule):
        """加载单个模块（内部方法）"""
        module.status = LoadingStatus.LOADING
        
        try:
            start_time = time.time()
            
            # 检查内存限制
            if self.used_memory_mb + module.memory_mb > self.max_memory_mb:
                if module.priority in [LoadingPriority.LOW, LoadingPriority.NORMAL]:
                    module.status = LoadingStatus.DEFERRED
                    logging.info(f"⏸️ 推迟加载 {module.name}（内存不足）")
                    return
            
            # 执行加载
            instance = module.loader()
            
            module.instance = instance
            module.status = LoadingStatus.LOADED
            module.load_time = time.time() - start_time
            module.error = None
            
            # 更新内存使用（简化：假设每个模块占用100MB）
            if module.memory_mb == 0:
                module.memory_mb = 100.0
            self.used_memory_mb += module.memory_mb
            
            logging.info(f"✅ 已加载模块: {module.name} ({module.load_time:.2f}s)")
            
        except Exception as e:
            module.status = LoadingStatus.FAILED
            module.error = str(e)
            logging.error(f"❌ 加载失败 {module.name}: {e}")
    
    def _load_by_priority(self, priority: LoadingPriority) -> Dict[str, Any]:
        """按优先级加载模块"""
        results = {}
        
        with self._lock:
            target_modules = [
                m for m in self.modules.values() 
                if m.priority == priority and m.status == LoadingStatus.PENDING
            ]
        
        for module in target_modules:
            self._load_module(module)
            if module.status == LoadingStatus.LOADED:
                results[module.name] = module.instance
        
        return results
    
    def get_status(self) -> Dict:
        """获取所有模块的加载状态"""
        with self._lock:
            return {
                name: {
                    'status': m.status.value,
                    'priority': m.priority.name,
                    'load_time': m.load_time,
                    'memory_mb': m.memory_mb,
                    'error': m.error
                }
                for name, m in self.modules.items()
            }
    
    def get_progress(self) -> float:
        """获取总体加载进度（0.0-1.0）"""
        with self._lock:
            if not self.modules:
                return 1.0
            
            loaded = sum(1 for m in self.modules.values() 
                        if m.status == LoadingStatus.LOADED)
            return loaded / len(self.modules)
    
    def cancel_loading(self):
        """取消正在进行的加载"""
        self._loading = False


class ChunkedLoader(Generic[T]):
    """
    分块加载器 - 用于大型数据集
    
    支持：
    - 分块读取大文件
    - 流式处理数据
    - 断点续传
    """
    
    def __init__(self, chunk_size: int = 1000):
        """
        初始化分块加载器
        
        参数:
            chunk_size: 每块大小（行数或条目数）
        """
        self.chunk_size = chunk_size
        self.total_chunks = 0
        self.loaded_chunks = 0
        self.current_chunk = 0
        
    def load_chunks(self, 
                   data_source: Any,
                   processor: Callable[[List[T]], Any],
                   max_chunks: Optional[int] = None) -> List[Any]:
        """
        分块加载并处理数据
        
        参数:
            data_source: 数据源（文件对象、迭代器等）
            processor: 每块数据的处理函数
            max_chunks: 最大加载块数（None表示全部加载）
            
        返回:
            每块的处理结果列表
        """
        results = []
        chunk = []
        
        for i, item in enumerate(data_source):
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
                # 处理当前块
                result = processor(chunk)
                results.append(result)
                
                self.loaded_chunks += 1
                chunk = []
                
                # 检查是否达到最大块数
                if max_chunks and self.loaded_chunks >= max_chunks:
                    break
        
        # 处理最后一块
        if chunk:
            result = processor(chunk)
            results.append(result)
            self.loaded_chunks += 1
        
        return results
    
    def get_progress(self) -> float:
        """获取分块加载进度"""
        if self.total_chunks == 0:
            return 0.0
        return self.loaded_chunks / self.total_chunks


# ==================== 全局增量加载器实例 ====================

# AGI系统增量加载器
agi_loader = IncrementalLoader(max_memory_mb=4096.0)

# RAG知识库分块加载器
rag_chunked_loader = ChunkedLoader(chunk_size=500)


# ==================== 使用示例 ====================

if __name__ == '__main__':
    import time
    
    # 示例1：注册模块
    def load_agi_core():
        time.sleep(0.5)  # 模拟加载时间
        return {"type": "AGICore", "status": "ready"}
    
    def load_knowledge_graph():
        time.sleep(1.0)
        return {"type": "KnowledgeGraph", "nodes": 1000}
    
    def load_tool_framework():
        time.sleep(0.3)
        return {"type": "ToolFramework", "tools": 13}
    
    # 注册模块
    agi_loader.register('agi_core', load_agi_core, priority=LoadingPriority.CRITICAL)
    agi_loader.register('knowledge_graph', load_knowledge_graph, priority=LoadingPriority.HIGH)
    agi_loader.register('tool_framework', load_tool_framework, priority=LoadingPriority.NORMAL)
    
    # 示例2：加载关键模块
    print("🔮 加载关键模块...")
    critical = agi_loader.load_critical()
    print(f"已加载关键模块: {list(critical.keys())}")
    
    # 示例3：按需加载
    print("\n📦 按需加载知识图谱...")
    kg = agi_loader.load_on_demand('knowledge_graph')
    print(f"知识图谱: {kg}")
    
    # 示例4：查看状态
    print("\n📊 加载状态:")
    status = agi_loader.get_status()
    for name, info in status.items():
        print(f"  {name}: {info['status']} ({info['load_time']:.2f}s)")
    
    # 示例5：分块加载
    print("\n📂 分块加载示例...")
    
    # 模拟大数据集
    big_data = range(10000)
    
    def process_chunk(chunk):
        return len(chunk)
    
    loader = ChunkedLoader(chunk_size=1000)
    results = loader.load_chunks(big_data, process_chunk, max_chunks=5)
    print(f"已加载 {len(results)} 块，每块 {results[0]} 条")
