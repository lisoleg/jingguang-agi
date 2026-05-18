#!/usr/bin/env python3
"""调试脚本"""
import sys
import io
import time

# 复制CodeInterpreter的核心逻辑
class DebugTest:
    def __init__(self):
        self.safe_modules = {
            "math": __import__("math"),
            "random": __import__("random"),
            "json": __import__("json"),
        }
        
        for lib_name in ["numpy", "pandas", "matplotlib"]:
            try:
                lib = __import__(lib_name)
                self.safe_modules[lib_name] = lib
            except Exception:
                pass
        
        self.global_context = {}
    
    def _safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if name in self.safe_modules:
            return self.safe_modules[name]
        root = name.split('.')[0]
        if root in self.safe_modules:
            return self.safe_modules[root]
        raise ImportError(f"禁止导入: {name}")
    
    def execute(self, code):
        # 3. 创建执行环境
        print("DEBUG: Creating safe_builtins...")
        safe_builtins = {}
        for name in dir(__builtins__):
            if name in ("print", "len", "range", "str", "int", "float"):
                safe_builtins[name] = getattr(__builtins__, name)
        
        print(f"DEBUG: safe_builtins keys = {list(safe_builtins.keys())}")
        
        print("DEBUG: Creating exec_globals...")
        exec_globals = {
            "__builtins__": safe_builtins,
            **self.safe_modules,
            **self.global_context
        }
        exec_globals["__builtins__"]["__import__"] = self._safe_import
        
        print(f"DEBUG: exec_globals keys = {list(exec_globals.keys())}")
        print(f"DEBUG: exec_globals['__builtins__'] keys = {list(exec_globals['__builtins__'].keys())}")
        
        print("DEBUG: About to exec...")
        try:
            exec(code, exec_globals, {})
            print("DEBUG: exec succeeded")
        except Exception as e:
            print(f"DEBUG: exec failed: {e}")
            print(f"DEBUG: __builtins__ in exec_globals: {'__builtins__' in exec_globals}")
            if '__builtins__' in exec_globals:
                print(f"DEBUG: After error, __builtins__ keys = {list(exec_globals['__builtins__'].keys())}")

if __name__ == "__main__":
    test = DebugTest()
    test.execute('print("Hello World")')
