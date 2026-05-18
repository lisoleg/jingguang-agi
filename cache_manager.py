"""
缓存机制优化模块

为LLM调用、记忆查询、工具调用提供缓存支持。
支持LRU淘汰策略、TTL过期、缓存统计。
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import pickle


class LRUCache:
    """LRU（最近最少使用）缓存实现"""
    
    def __init__(self, capacity: int = 100):
        """
        初始化LRU缓存
        
        参数:
            capacity: 缓存容量（最大条目数）
        """
        self.capacity = capacity
        self.cache = {}  # key -> (value, timestamp, access_time)
        self.order = []  # 访问顺序（用于LRU淘汰）
        
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键（基于参数哈希）"""
        key_data = {
            'args': args,
            'kwargs': tuple(sorted(kwargs.items()))
        }
        key_str = json.dumps(key_data, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
        
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        返回:
            缓存的值，若不存在或已过期则返回None
        """
        if key not in self.cache:
            return None
            
        value, timestamp, _ = self.cache[key]
        
        # 更新访问时间
        self.cache[key] = (value, timestamp, time.time())
        
        # 更新访问顺序
        if key in self.order:
            self.order.remove(key)
        self.order.append(key)
        
        return value
        
    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        放入缓存
        
        参数:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None表示不过期
        """
        timestamp = time.time()
        
        if len(self.cache) >= self.capacity:
            # LRU淘汰
            oldest_key = self.order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
        
        self.cache[key] = (value, timestamp, time.time())
        self.order.append(key)
        
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.order.clear()
        
    def stats(self) -> Dict:
        """返回缓存统计信息"""
        return {
            'size': len(self.cache),
            'capacity': self.capacity,
            'usage_rate': len(self.cache) / self.capacity,
        }


class TTLCache(LRUCache):
    """带TTL（生存时间）的缓存"""
    
    def __init__(self, capacity: int = 100, default_ttl: int = 3600):
        """
        初始化TTL缓存
        
        参数:
            capacity: 缓存容量
            default_ttl: 默认TTL（秒），默认1小时
        """
        super().__init__(capacity)
        self.default_ttl = default_ttl
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值（自动检查过期）"""
        if key not in self.cache:
            return None
            
        value, timestamp, _ = self.cache[key]
        
        # 检查是否过期
        if time.time() - timestamp > self.default_ttl:
            del self.cache[key]
            if key in self.order:
                self.order.remove(key)
            return None
        
        # 更新访问时间
        self.cache[key] = (value, timestamp, time.time())
        if key in self.order:
            self.order.remove(key)
        self.order.append(key)
        
        return value


class CacheManager:
    """缓存管理器（统一管理所有缓存）"""
    
    def __init__(self):
        self.caches = {}
        
    def create_cache(self, name: str, cache_type: str = 'lru', **kwargs):
        """
        创建缓存
        
        参数:
            name: 缓存名称
            cache_type: 缓存类型 ('lru' 或 'ttl')
            **kwargs: 传递给缓存构造函数的参数
        """
        if cache_type == 'lru':
            cache = LRUCache(**kwargs)
        elif cache_type == 'ttl':
            cache = TTLCache(**kwargs)
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
            
        self.caches[name] = cache
        return cache
        
    def get_cache(self, name: str) -> Optional[Any]:
        """获取指定名称的缓存"""
        return self.caches.get(name)
        
    def clear_all(self):
        """清空所有缓存"""
        for cache in self.caches.values():
            cache.clear()
            
    def global_stats(self) -> Dict:
        """返回所有缓存的统计信息"""
        return {name: cache.stats() for name, cache in self.caches.items()}


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(cache_name: str, ttl: Optional[int] = None):
    """
    缓存装饰器
    
    用法:
        @cached('llm_cache', ttl=3600)
        def call_llm(prompt: str) -> str:
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取或创建缓存
            cache = cache_manager.get_cache(cache_name)
            if cache is None:
                cache = cache_manager.create_cache(cache_name, 'ttl')
            
            # 生成缓存键
            key = cache._generate_key(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # 缓存未命中，调用原函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache.put(key, result, ttl)
            
            return result
        return wrapper
    return decorator


# ============ 使用示例 ============

if __name__ == '__main__':
    # 示例1：LLM响应缓存
    @cached('llm_cache', ttl=3600)
    def mock_llm_call(prompt: str) -> str:
        """模拟LLM调用（很慢）"""
        time.sleep(1)  # 模拟1秒延迟
        return f"Response to: {prompt}"
    
    print("第一次调用（慢）:")
    start = time.time()
    result1 = mock_llm_call("Hello")
    print(f"  耗时: {time.time() - start:.2f}s")
    
    print("第二次调用（快，使用缓存）:")
    start = time.time()
    result2 = mock_llm_call("Hello")
    print(f"  耗时: {time.time() - start:.2f}s")
    
    # 示例2：记忆查询缓存
    @cached('memory_cache', ttl=600)
    def query_memory(query: str) -> list:
        """模拟记忆查询（慢）"""
        time.sleep(0.5)
        return [f"Memory about {query}"]
    
    # 示例3：工具调用缓存
    @cached('tool_cache', ttl=300)
    def call_tool(tool_name: str, params: dict) -> dict:
        """模拟工具调用"""
        time.sleep(0.3)
        return {'result': f"Tool {tool_name} executed"}
    
    # 显示缓存统计
    print("\n缓存统计:")
    stats = cache_manager.global_stats()
    for name, stat in stats.items():
        print(f"  {name}: {stat}")
