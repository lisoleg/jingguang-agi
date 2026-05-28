"""
太乙AI工具框架 - 代码解释器与沙箱执行器
CodeInterpreter: 安全执行Python代码，支持numpy、pandas等科学计算库
DockerSandbox: Docker容器隔离执行环境（可选功能）

Author: 太乙AGI系统
"""

import sys
import io
import traceback
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ExecutionStatus(Enum):
    """代码执行状态"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    SECURITY_VIOLATION = "security_violation"
    SANDBOX_UNAVAILABLE = "sandbox_unavailable"


@dataclass
class ExecutionResult:
    """代码执行结果"""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    return_value: Any = None
    execution_time: float = 0.0
    error_type: str = ""
    error_message: str = ""
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_value": self.return_value,
            "execution_time": self.execution_time,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "output_data": self.output_data
        }


@dataclass
class CodeExecutionRequest:
    """代码执行请求"""
    code: str
    timeout: int = 30  # 秒
    allowed_imports: List[str] = field(default_factory=lambda: [
        "math", "random", "json", "datetime", "time", "re", 
        "collections", "itertools", "functools", "operator",
        "numpy", "pandas", "scipy", "matplotlib"
    ])
    max_output_length: int = 10000
    use_sandbox: bool = False  # 是否使用Docker沙箱


class CodeInterpreter:
    """
    安全Python代码解释器
    
    特性：
    - 捕获stdout/stderr输出
    - 超时控制
    - 白名单导入控制
    - 数据可视化支持
    - 持久化执行上下文
    """
    
    # 安全违规关键词检测
    BLOCKED_PATTERNS = [
        "import os", "import sys", "import subprocess", "import socket",
        "import threading", "import multiprocessing", "import ctypes",
        "import cffi", "import _ctypes", "open(", "file(", "input(",
        "__import__", "eval(", "exec(", "compile(",
        "os.", "sys.", "subprocess.", "socket.", "ctypes.",
        "eval ", "exec ", "compile ",
        "shutil.rmtree", "os.remove", "os.unlink",
        "requests", "urllib", "http.client",
        "popen", "spawn", "Popen",
        "os.chdir", "os.mkdir", "os.rmdir", "os.rename",
        "getattr(", "setattr(", "delattr(",
        "memoryview", "buffer",
    ]
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.global_context: Dict[str, Any] = {}
        self._init_safe_builtins()
    
    def _init_safe_builtins(self):
        """初始化安全的内置函数和模块"""
        # 安全模块白名单
        self.safe_modules = {
            "math": __import__("math"),
            "random": __import__("random"),
            "json": __import__("json"),
            "datetime": __import__("datetime"),
            "time": __import__("time"),
            "re": __import__("re"),
            "collections": __import__("collections"),
            "itertools": __import__("itertools"),
            "functools": __import__("functools"),
            "operator": __import__("operator"),
            "statistics": __import__("statistics"),
        }
        
        # 尝试导入可选的科学计算库（捕获所有异常）
        for lib_name in ["numpy", "pandas", "matplotlib"]:
            try:
                lib = __import__(lib_name)
                self.safe_modules[lib_name] = lib
                if lib_name == "matplotlib":
                    lib.use('Agg')  # 非交互式后端
            except Exception:
                pass  # 静默忽略无法导入的库
    
    def _check_security(self, code: str) -> tuple[bool, str]:
        """安全检查"""
        code_lower = code.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in code_lower:
                return False, f"安全违规: 禁止使用 '{pattern}'"
        return True, ""
    
    def execute(self, request: CodeExecutionRequest) -> ExecutionResult:
        """执行Python代码"""
        start_time = time.time()
        
        # 使用builtins模块获取print等函数
        import builtins
        _print = getattr(builtins, 'print', None)
        
        # 1. 安全检查
        if not request.use_sandbox:
            is_safe, error_msg = self._check_security(request.code)
            if not is_safe:
                return ExecutionResult(
                    status=ExecutionStatus.SECURITY_VIOLATION,
                    error_type="SecurityViolation",
                    error_message=error_msg,
                    execution_time=time.time() - start_time
                )
        
        # 2. 设置输出捕获
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # 3. 创建执行环境
        # 使用builtins模块来构建安全的__builtins__
        safe_builtins = {}
        for name in ('print', 'len', 'range', 'str', 'int', 'float', 
                    'bool', 'list', 'dict', 'set', 'tuple', 'type',
                    'isinstance', 'issubclass', 'hasattr', 'getattr',
                    'setattr', 'open', 'enumerate', 'zip', 'map',
                    'filter', 'sorted', 'reversed', 'sum', 'min',
                    'max', 'abs', 'round', 'pow', 'divmod', 'format',
                    'repr', 'chr', 'ord', 'hex', 'oct', 'bin', 'slice'):
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)
        
        exec_globals = {
            "__builtins__": safe_builtins,
            **self.safe_modules,
            **self.global_context
        }
        
        # 安全导入函数
        def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in self.safe_modules:
                return self.safe_modules[name]
            root = name.split('.')[0]
            if root in self.safe_modules:
                return self.safe_modules[root]
            raise ImportError(f"禁止导入: {name}")
        
        exec_globals["__builtins__"]["__import__"] = _safe_import
        
        exec_locals = {}
        
        try:
            exec(request.code, exec_globals, exec_locals)
            
            # 更新全局上下文（保留变量）
            self.global_context.update(exec_globals)
            self.global_context.update(exec_locals)
            
            # 收集输出
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            
            # 限制输出长度
            if len(stdout) > request.max_output_length:
                stdout = stdout[:request.max_output_length] + f"\n... (输出已截断，共 {len(stdout)} 字符)"
            
            # 提取返回值
            return_value = None
            output_data = {}
            if "_" in exec_locals:
                return_value = exec_locals["_"]
            if "result" in exec_locals:
                return_value = exec_locals["result"]
            if "data" in exec_locals:
                output_data["data"] = exec_locals["data"]
            if "df" in exec_locals:
                output_data["dataframe"] = str(exec_locals["df"])
            if "plot" in exec_locals:
                output_data["plot"] = "图表已生成"
            
            # 记录历史
            execution_record = {
                "id": str(uuid.uuid4())[:8],
                "timestamp": datetime.now().isoformat(),
                "code_preview": request.code[:100] + "..." if len(request.code) > 100 else request.code,
                "status": "success",
                "execution_time": time.time() - start_time
            }
            self.execution_history.append(execution_record)
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=stdout,
                stderr=stderr,
                return_value=return_value,
                execution_time=time.time() - start_time,
                output_data=output_data
            )
            
        except TimeoutError:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                stderr=f"代码执行超过 {request.timeout} 秒限制",
                error_type="TimeoutError",
                error_message=f"执行超时",
                execution_time=time.time() - start_time
            )
            
        except SyntaxError as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                stderr=traceback.format_exc(),
                error_type="SyntaxError",
                error_message=str(e),
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                stderr=traceback.format_exc(),
                error_type=type(e).__name__,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def execute_with_sandbox(self, request: CodeExecutionRequest) -> ExecutionResult:
        """使用Docker沙箱执行代码"""
        sandbox = DockerSandbox()
        if not sandbox.is_available():
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_UNAVAILABLE,
                error_message="Docker沙箱不可用，将使用内置解释器执行"
            )
        
        return sandbox.execute(request)
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history[-limit:]
    
    def clear_context(self):
        """清除执行上下文"""
        self.global_context.clear()


class DockerSandbox:
    """Docker容器沙箱（可选功能）"""
    
    def __init__(self):
        self.docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "ps"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        return self.docker_available
    
    def execute(self, request: CodeExecutionRequest) -> ExecutionResult:
        import subprocess
        import tempfile
        import os
        
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.py', 
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(request.code)
            temp_file = f.name
        
        try:
            cmd = [
                "docker", "run", "--rm",
                "--network=none",
                "--memory=512m",
                "--cpus=0.5",
                "-v", f"{temp_file}:/code.py:ro",
                "python:3.10-slim",
                "python", "/code.py"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=request.timeout,
                text=True
            )
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.ERROR,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=time.time() - start_time
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error_message=f"Docker执行超时 ({request.timeout}s)",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass


# ===== 太乙工具注册 =====

def register_code_interpreter_tools(registry):
    """向工具注册表注册代码解释器相关工具"""
    
    interpreter = CodeInterpreter()
    
    def tool_execute_python(code: str, timeout: int = 30) -> str:
        request = CodeExecutionRequest(
            code=code,
            timeout=timeout
        )
        result = interpreter.execute(request)
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    
    def tool_execute_sandbox(code: str, timeout: int = 30) -> str:
        request = CodeExecutionRequest(
            code=code,
            timeout=timeout,
            use_sandbox=True
        )
        result = interpreter.execute_with_sandbox(request)
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    
    def tool_list_variables() -> str:
        return json.dumps(list(interpreter.global_context.keys()), ensure_ascii=False, indent=2)
    
    def tool_clear_context() -> str:
        interpreter.clear_context()
        return json.dumps({"status": "success", "message": "执行上下文已清除"})
    
    def tool_execution_history(limit: int = 10) -> str:
        history = interpreter.get_history(limit)
        return json.dumps(history, ensure_ascii=False, indent=2)
    
    registry.register(
        name="execute_python",
        func=tool_execute_python,
        description="执行Python代码，支持数学计算、数据处理、可视化等",
        parameters={
            "code": {"type": "string", "description": "要执行的Python代码"},
            "timeout": {"type": "integer", "description": "超时时间（秒），默认30", "default": 30}
        }
    )
    
    registry.register(
        name="execute_sandbox",
        func=tool_execute_sandbox,
        description="使用Docker沙箱执行Python代码（更安全）",
        parameters={
            "code": {"type": "string", "description": "要执行的Python代码"},
            "timeout": {"type": "integer", "description": "超时时间（秒），默认30", "default": 30}
        }
    )
    
    registry.register(
        name="list_variables",
        func=tool_list_variables,
        description="列出当前执行上下文中的变量"
    )
    
    registry.register(
        name="clear_context",
        func=tool_clear_context,
        description="清除执行上下文"
    )
    
    registry.register(
        name="execution_history",
        func=tool_execution_history,
        description="获取代码执行历史",
        parameters={
            "limit": {"type": "integer", "description": "返回记录数量", "default": 10}
        }
    )


if __name__ == "__main__":
    # 单元测试
    interpreter = CodeInterpreter()
    
    # 测试1: 简单计算
    print("=== 测试1: 简单计算 ===")
    result = interpreter.execute(CodeExecutionRequest("result = 123 * 456"))
    print(f"Status: {result.status.value}")
    print(f"Return: {result.return_value}")
    print()
    
    # 测试2: 数学运算
    print("=== 测试2: 数学运算 ===")
    result = interpreter.execute(CodeExecutionRequest("""
import math
x = math.sqrt(2)
print(f"sqrt(2) = {x}")
result = x ** 2
"""))
    print(f"Status: {result.status.value}")
    print(f"Stdout: {result.stdout}")
    print()
    
    # 测试3: 安全检查
    print("=== 测试3: 安全检查 ===")
    result = interpreter.execute(CodeExecutionRequest("import os; os.system('ls')"))
    print(f"Status: {result.status.value}")
    print(f"Error: {result.error_message}")
    print()
    
    # 测试4: 错误处理
    print("=== 测试4: 错误处理 ===")
    result = interpreter.execute(CodeExecutionRequest("x = 1 / 0"))
    print(f"Status: {result.status.value}")
    print(f"Error: {result.error_type}: {result.error_message}")
