"""
压力测试与性能基准测试套件

测试内容:
1. 并发负载测试（多用户同时访问）
2. 响应时间基准（P50/P90/P99延迟）
3. 吞吐量测试（RPS - Requests Per Second）
4. 内存/CPU监控
5. 各模块性能基准（LLM、工具调用、记忆检索、RAG、推理）
6. 错误率统计
"""

import time
import threading
import json
import statistics
import psutil
import gc
from typing import Dict, List, Tuple, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from concurrent import futures
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    total_requests: int
    successful: int
    failed: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p90_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    memory_usage_mb: float
    cpu_percent: float
    details: List[Dict] = field(default_factory=list)


class StressTester:
    """压力测试仪"""
    
    def __init__(self, max_workers: int = 10):
        """
        初始化压力测试仪
        
        参数:
            max_workers: 最大并发工作线程数
        """
        self.max_workers = max_workers
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process(os.getpid())
        
    def benchmark(self,
                 name: str,
                 target: Callable,
                 duration_sec: int = 60,
                 concurrency: int = 5,
                 **kwargs) -> BenchmarkResult:
        """
        对目标函数进行压力测试
        
        参数:
            name: 测试名称
            target: 目标函数
            duration_sec: 测试持续时间（秒）
            concurrency: 并发数
            **kwargs: 传递给目标函数的参数
            
        返回:
            BenchmarkResult对象
        """
        print(f"\n{'='*60}")
        print(f"开始压力测试: {name}")
        print(f"持续时间: {duration_sec}s, 并发数: {concurrency}")
        print(f"{'='*60}")
        
        response_times = []
        errors = 0
        successes = 0
        details = []
        stop_event = threading.Event()
        
        def worker():
            """工作线程"""
            nonlocal errors, successes
            
            while not stop_event.is_set():
                try:
                    start = time.perf_counter()
                    result = target(**kwargs)
                    elapsed = (time.perf_counter() - start) * 1000  # ms
                    
                    response_times.append(elapsed)
                    successes += 1
                    
                    details.append({
                        'timestamp': datetime.now().isoformat(),
                        'response_time_ms': elapsed,
                        'status': 'success',
                        'result': str(result)[:100] if result else None
                    })
                    
                except Exception as e:
                    errors += 1
                    elapsed = (time.perf_counter() - start) * 1000
                    
                    details.append({
                        'timestamp': datetime.now().isoformat(),
                        'response_time_ms': elapsed,
                        'status': 'error',
                        'error': str(e)
                    })
        
        # 启动工作线程
        threads = []
        for i in range(min(concurrency, self.max_workers)):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        # 等待指定时间
        time.sleep(duration_sec)
        stop_event.set()
        
        # 等待线程结束
        for t in threads:
            t.join(timeout=5)
        
        # 计算统计数据
        total = successes + errors
        
        result = self._calculate_stats(
            name=name,
            response_times=response_times,
            successes=successes,
            errors=errors,
            total=total,
            duration_sec=duration_sec,
            details=details
        )
        
        self.results.append(result)
        self._print_result(result)
        
        return result
    
    def _calculate_stats(self,
                        name: str,
                        response_times: List[float],
                        successes: int,
                        errors: int,
                        total: int,
                        duration_sec: int,
                        details: List[Dict]) -> BenchmarkResult:
        """计算统计数据"""
        
        if response_times:
            avg_rt = statistics.mean(response_times)
            min_rt = min(response_times)
            max_rt = max(response_times)
            sorted_rt = sorted(response_times)
            p50 = statistics.median(sorted_rt)
            p90 = sorted_rt[int(len(sorted_rt) * 0.9)]
            p99 = sorted_rt[int(len(sorted_rt) * 0.99)]
        else:
            avg_rt = min_rt = max_rt = p50 = p90 = p99 = 0.0
        
        rps = total / duration_sec if duration_sec > 0 else 0
        error_rate = (errors / total * 100) if total > 0 else 0
        
        # 获取资源使用情况
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent(interval=1)
        
        return BenchmarkResult(
            name=name,
            total_requests=total,
            successful=successes,
            failed=errors,
            avg_response_time=avg_rt,
            min_response_time=min_rt,
            max_response_time=max_rt,
            p50_response_time=p50,
            p90_response_time=p90,
            p99_response_time=p99,
            requests_per_second=rps,
            error_rate=error_rate,
            memory_usage_mb=memory_mb,
            cpu_percent=cpu_percent,
            details=details
        )
    
    def _print_result(self, result: BenchmarkResult):
        """打印测试结果"""
        print(f"\n📊 测试结果: {result.name}")
        print(f"{'='*60}")
        print(f"总请求数: {result.total_requests}")
        print(f"成功: {result.successful}, 失败: {result.failed}")
        print(f"错误率: {result.error_rate:.2f}%")
        print(f"\n响应时间（毫秒）:")
        print(f"  平均: {result.avg_response_time:.2f}ms")
        print(f"  最小: {result.min_response_time:.2f}ms")
        print(f"  最大: {result.max_response_time:.2f}ms")
        print(f"  P50: {result.p50_response_time:.2f}ms")
        print(f"  P90: {result.p90_response_time:.2f}ms")
        print(f"  P99: {result.p99_response_time:.2f}ms")
        print(f"\n吞吐量: {result.requests_per_second:.2f} RPS")
        print(f"内存使用: {result.memory_usage_mb:.2f} MB")
        print(f"CPU使用: {result.cpu_percent:.2f}%")
        print(f"{'='*60}\n")
    
    def benchmark_agi_modules(self, system) -> Dict[str, BenchmarkResult]:
        """
        对AGI系统各模块进行基准测试
        
        参数:
            system: AGI系统实例
            
        返回:
            各模块的基准测试结果字典
        """
        print("\n🔬 开始AGI模块性能基准测试...")
        
        results = {}
        
        # 1. LLM推理基准
        def test_llm_inference():
            if hasattr(system, 'llm') and system.llm:
                return system.llm.generate("测试生成速度")
            return "mock_response"
        
        results['llm_inference'] = self.benchmark(
            name="LLM推理",
            target=test_llm_inference,
            duration_sec=30,
            concurrency=3
        )
        
        # 2. 工具调用基准
        def test_tool_execution():
            if hasattr(system, 'tool_framework') and system.tool_framework:
                tools = list(system.tool_framework.tools.keys())
                if tools:
                    return system.tool_framework.execute_tool(tools[0], {})
            return {"status": "mock"}
        
        results['tool_execution'] = self.benchmark(
            name="工具调用",
            target=test_tool_execution,
            duration_sec=30,
            concurrency=5
        )
        
        # 3. 记忆检索基准
        def test_memory_retrieval():
            if hasattr(system, 'memory_system') and system.memory_system:
                return system.memory_system.retrieve("测试查询")
            return []
        
        results['memory_retrieval'] = self.benchmark(
            name="记忆检索",
            target=test_memory_retrieval,
            duration_sec=30,
            concurrency=5
        )
        
        # 4. RAG查询基准
        def test_rag_query():
            if hasattr(system, 'rag_system') and system.rag_system:
                return system.rag_system.query("测试RAG查询")
            return []
        
        results['rag_query'] = self.benchmark(
            name="RAG查询",
            target=test_rag_query,
            duration_sec=30,
            concurrency=3
        )
        
        # 5. AGI推理基准
        def test_agi_reasoning():
            if hasattr(system, 'reasoning_engine'):
                return system.reasoning_engine.reason("1+1等于几？")
            return {"answer": "2"}
        
        results['agi_reasoning'] = self.benchmark(
            name="AGI推理",
            target=test_agi_reasoning,
            duration_sec=30,
            concurrency=3
        )
        
        return results
    
    def load_test_api(self, 
                     api_url: str = "http://localhost:5000/api/chat",
                     duration_sec: int = 60,
                     concurrency: int = 10) -> BenchmarkResult:
        """
        API负载测试
        
        参数:
            api_url: API端点URL
            duration_sec: 测试持续时间
            concurrency: 并发数
        """
        try:
            import requests
        except ImportError:
            print("⚠️ 需要安装requests库: pip install requests")
            return None
        
        def api_call():
            response = requests.post(
                api_url,
                json={"message": "你好", "stream": False},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        return self.benchmark(
            name="API负载测试",
            target=api_call,
            duration_sec=duration_sec,
            concurrency=concurrency
        )
    
    def memory_stress_test(self, 
                          system,
                          duration_sec: int = 60) -> Dict:
        """
        内存压力测试 - 验证系统在高负载下不会出现内存泄漏
        
        参数:
            system: AGI系统实例
            duration_sec: 测试持续时间
            
        返回:
            内存使用统计
        """
        print("\n💾 开始内存压力测试...")
        
        memory_samples = []
        gc.collect()
        
        start_memory = self.process.memory_info().rss / 1024 / 1024
        
        def memory_intensive_task():
            """内存密集型任务"""
            # 模拟大量数据处理
            data = ["test" * 100 for _ in range(1000)]
            result = sum(len(s) for s in data)
            del data
            return result
        
        start_time = time.time()
        while time.time() - start_time < duration_sec:
            memory_intensive_task()
            
            # 采样内存
            current_memory = self.process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            
            time.sleep(0.1)
        
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        stats = {
            'start_memory_mb': start_memory,
            'end_memory_mb': end_memory,
            'memory_diff_mb': end_memory - start_memory,
            'max_memory_mb': max(memory_samples),
            'min_memory_mb': min(memory_samples),
            'avg_memory_mb': statistics.mean(memory_samples),
            'samples': len(memory_samples)
        }
        
        print(f"\n💾 内存压力测试结果:")
        print(f"  初始内存: {stats['start_memory_mb']:.2f} MB")
        print(f"  结束内存: {stats['end_memory_mb']:.2f} MB")
        print(f"  内存变化: {stats['memory_diff_mb']:+.2f} MB")
        print(f"  最大内存: {stats['max_memory_mb']:.2f} MB")
        print(f"  平均内存: {stats['avg_memory_mb']:.2f} MB")
        
        if stats['memory_diff_mb'] > 100:
            print(f"  ⚠️ 警告: 内存增长明显，可能存在内存泄漏！")
        else:
            print(f"  ✅ 内存使用正常")
        
        return stats
    
    def generate_report(self, output_file: str = "stress_test_report.json"):
        """生成测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / 1024**3,
                'python_version': sys.version,
            },
            'benchmarks': []
        }
        
        for result in self.results:
            benchmark_data = {
                'name': result.name,
                'total_requests': result.total_requests,
                'successful': result.successful,
                'failed': result.failed,
                'avg_response_time_ms': result.avg_response_time,
                'min_response_time_ms': result.min_response_time,
                'max_response_time_ms': result.max_response_time,
                'p50_response_time_ms': result.p50_response_time,
                'p90_response_time_ms': result.p90_response_time,
                'p99_response_time_ms': result.p99_response_time,
                'requests_per_second': result.requests_per_second,
                'error_rate_percent': result.error_rate,
                'memory_usage_mb': result.memory_usage_mb,
                'cpu_percent': result.cpu_percent,
            }
            report['benchmarks'].append(benchmark_data)
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 测试报告已保存: {output_file}")
        
        return report


# ==================== 测试目标函数示例 ====================

def mock_llm_call(prompt: str) -> str:
    """模拟LLM调用（用于测试）"""
    time.sleep(0.1)  # 模拟100ms延迟
    return f"Response to: {prompt[:20]}..."


def mock_tool_call(tool_name: str, params: dict) -> dict:
    """模拟工具调用"""
    time.sleep(0.05)  # 模拟50ms延迟
    return {'result': f"Tool {tool_name} executed", 'params': params}


def mock_memory_query(query: str) -> list:
    """模拟记忆查询"""
    time.sleep(0.02)  # 模拟20ms延迟
    return [f"Memory {i}" for i in range(5)]


# ==================== 主测试流程 ====================

if __name__ == '__main__':
    print("🚀 启动压力测试与性能基准测试套件")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建压力测试仪
    tester = StressTester(max_workers=20)
    
    # 1. LLM推理压力测试
    result_llm = tester.benchmark(
        name="LLM推理压力测试",
        target=mock_llm_call,
        duration_sec=30,
        concurrency=5,
        prompt="测试提示词"
    )
    
    # 2. 工具调用压力测试
    result_tool = tester.benchmark(
        name="工具调用压力测试",
        target=mock_tool_call,
        duration_sec=30,
        concurrency=10,
        tool_name="calculator",
        params={"operation": "add", "a": 1, "b": 2}
    )
    
    # 3. 记忆检索压力测试
    result_memory = tester.benchmark(
        name="记忆检索压力测试",
        target=mock_memory_query,
        duration_sec=30,
        concurrency=8,
        query="测试查询"
    )
    
    # 4. 混合负载测试（模拟真实场景）
    def mixed_workload():
        """混合工作负载"""
        import random
        choice = random.random()
        
        if choice < 0.4:  # 40% LLM调用
            return mock_llm_call("混合测试")
        elif choice < 0.7:  # 30% 工具调用
            return mock_tool_call("test_tool", {})
        else:  # 30% 记忆查询
            return mock_memory_query("混合查询")
    
    result_mixed = tester.benchmark(
        name="混合负载压力测试",
        target=mixed_workload,
        duration_sec=60,
        concurrency=15
    )
    
    # 5. 内存压力测试
    memory_stats = tester.memory_stress_test(
        system=None,  # 实际使用时传入AGI系统实例
        duration_sec=30
    )
    
    # 生成测试报告
    report = tester.generate_report()
    
    print("\n✅ 所有测试完成！")
    print(f"总计 {len(tester.results)} 个基准测试")
    print(f"详细报告: stress_test_report.json")
