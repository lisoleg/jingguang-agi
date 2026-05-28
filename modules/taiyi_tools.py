#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一太乙系统 - 前五识（Indriya）工具调用框架 V2.0
实现具身性基础：文件读写、代码执行、浏览器操作、API调用

扩展功能：
- 动态工具注册/注销
- 工具分组与命名空间
- 工具依赖管理
- 插件式扩展机制
- 异步执行支持
"""

import os
import sys
import json
import subprocess
import tempfile
import threading
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Callable, Set, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import traceback
import shutil
import re


# ==================== 工具定义 ====================

class ToolCategory(Enum):
    """工具类别（对应五识+太乙）"""
    SIGHT = "眼识"      # 视觉/读取
    HEARING = "耳识"    # 听觉/监听
    SMELL = "鼻识"       # 嗅觉/采样
    TASTE = "舌识"       # 味觉/验证
    BODY = "身识"        # 身体/执行
    MANAS = "末那识"     # 第七识/审计/元认知
    TAIYI = "太乙"       # 太乙预言机/高级推理


@dataclass
class ToolMetadata:
    """工具元数据"""
    version: str = "1.0.0"
    author: str = "Taiyi System"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_at: str = ""
    last_modified: str = ""


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Any = None
    enum: List[Any] = field(default_factory=list)  # 枚举值


@dataclass
class ToolDefinition:
    """工具定义（前五识接口）"""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter] = field(default_factory=list)
    dangerous: bool = False  # 是否危险操作（需审计）
    metadata: ToolMetadata = field(default_factory=ToolMetadata)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    execution_time: float = 0.0  # 执行时间（秒）


# ==================== 工具注册表 V2.0 ====================

class ToolRegistry:
    """工具注册表（前五识中心）- 支持动态注册和插件机制"""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._executors: Dict[str, Callable] = {}
        self._namespaces: Dict[str, Set[str]] = {}  # 命名空间 -> 工具名集合
        self._groups: Dict[str, Set[str]] = {}  # 分组 -> 工具名集合
        self._plugins: Dict[str, Any] = {}  # 插件名称 -> 插件实例

    def register(self, definition: ToolDefinition, executor: Callable,
                 namespace: str = "default", groups: List[str] = None):
        """注册工具（支持命名空间和分组）"""
        self._tools[definition.name] = definition
        self._executors[definition.name] = executor
        
        # 注册命名空间
        if namespace not in self._namespaces:
            self._namespaces[namespace] = set()
        self._namespaces[namespace].add(definition.name)
        
        # 注册分组
        if groups:
            for group in groups:
                if group not in self._groups:
                    self._groups[group] = set()
                self._groups[group].add(definition.name)
        
        # 更新时间戳
        definition.metadata.last_modified = datetime.now().isoformat()

    def unregister(self, name: str) -> bool:
        """注销工具"""
        if name not in self._tools:
            return False
        
        definition = self._tools[name]
        
        # 从命名空间移除
        for ns in self._namespaces:
            self._namespaces[ns].discard(name)
        
        # 从分组移除
        for group in self._groups:
            self._groups[group].discard(name)
        
        # 删除工具和执行器
        del self._tools[name]
        del self._executors[name]
        
        return True

    def register_plugin(self, name: str, plugin: Any) -> bool:
        """注册插件"""
        self._plugins[name] = plugin
        return True

    def get_plugin(self, name: str) -> Optional[Any]:
        """获取插件"""
        return self._plugins.get(name)

    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def get_executor(self, name: str) -> Optional[Callable]:
        return self._executors.get(name)

    def list_tools(self, namespace: str = None, group: str = None) -> List[ToolDefinition]:
        """列出工具（可选过滤）"""
        if namespace:
            names = self._namespaces.get(namespace, set())
            return [self._tools[n] for n in names if n in self._tools]
        if group:
            names = self._groups.get(group, set())
            return [self._tools[n] for n in names if n in self._tools]
        return list(self._tools.values())

    def list_namespaces(self) -> List[str]:
        """列出所有命名空间"""
        return list(self._namespaces.keys())

    def list_groups(self) -> List[str]:
        """列出所有分组"""
        return list(self._groups.keys())

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """按类别获取工具"""
        return [t for t in self._tools.values() if t.category == category]

    def get_dangerous_tools(self) -> List[ToolDefinition]:
        """获取所有危险工具"""
        return [t for t in self._tools.values() if t.dangerous]

    def get_stats(self) -> Dict:
        """获取注册统计"""
        category_count = {}
        for tool in self._tools.values():
            cat = tool.category.value
            category_count[cat] = category_count.get(cat, 0) + 1
        
        return {
            "total_tools": len(self._tools),
            "by_category": category_count,
            "dangerous_tools": len(self.get_dangerous_tools()),
            "namespaces": len(self._namespaces),
            "groups": len(self._groups),
            "plugins": len(self._plugins)
        }

    def get_openai_functions(self) -> List[Dict]:
        """返回OpenAI Function Calling格式"""
        functions = []
        for tool in self._tools.values():
            func = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            for param in tool.parameters:
                prop = {
                    "type": param.type,
                    "description": param.description
                }
                if param.enum:
                    prop["enum"] = param.enum
                if param.default is not None:
                    prop["default"] = param.default
                func["parameters"]["properties"][param.name] = prop
                if param.required:
                    func["parameters"]["required"].append(param.name)
            functions.append(func)
        return functions

    def check_dependencies(self, tool_name: str) -> Dict[str, bool]:
        """检查工具依赖是否满足"""
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": "工具不存在"}
        
        deps = tool.metadata.dependencies
        return {dep: dep in self._tools for dep in deps}


# ==================== 内置工具实现 ====================

def _exec_file_read(args: Dict) -> ToolResult:
    """文件读取工具"""
    path = args.get("path", "")
    if not path:
        return ToolResult(False, None, "路径不能为空")
    try:
        if not os.path.exists(path):
            return ToolResult(False, None, f"文件不存在: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ToolResult(True, content, metadata={"path": path, "length": len(content)})
    except Exception as e:
        return ToolResult(False, None, str(e))


def _exec_file_write(args: Dict) -> ToolResult:
    """文件写入工具"""
    path = args.get("path", "")
    content = args.get("content", "")
    mode = args.get("mode", "write")  # "write" or "append"
    
    if not path:
        return ToolResult(False, None, "路径不能为空")
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, 'w' if mode == "write" else 'a', encoding='utf-8') as f:
            f.write(content)
        return ToolResult(True, f"已{'写入' if mode == 'write' else '追加'} {len(content)} 字符", 
                       metadata={"path": path})
    except Exception as e:
        return ToolResult(False, None, str(e))


def _exec_python_run(args: Dict) -> ToolResult:
    """Python代码执行工具"""
    code = args.get("code", "")
    timeout = args.get("timeout", 30)
    
    if not code:
        return ToolResult(False, None, "代码不能为空")
    
    try:
        # 使用子进程执行（安全隔离）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        os.unlink(temp_path)
        
        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
        if result.returncode != 0:
            return ToolResult(False, output, f"执行失败，返回码: {result.returncode}")
        return ToolResult(True, output)
        
    except subprocess.TimeoutExpired:
        return ToolResult(False, None, f"执行超时（{timeout}秒）")
    except Exception as e:
        return ToolResult(False, None, str(e))


def _exec_bash_run(args: Dict) -> ToolResult:
    """Bash命令执行工具"""
    command = args.get("command", "")
    timeout = args.get("timeout", 30)
    
    if not command:
        return ToolResult(False, None, "命令不能为空")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
        return ToolResult(True, output)
        
    except subprocess.TimeoutExpired:
        return ToolResult(False, None, f"执行超时（{timeout}秒）")
    except Exception as e:
        return ToolResult(False, None, str(e))


def _exec_web_fetch(args: Dict) -> ToolResult:
    """网页抓取工具（眼识）"""
    url = args.get("url", "")
    timeout = args.get("timeout", 10)
    
    if not url:
        return ToolResult(False, None, "URL不能为空")
    
    try:
        import urllib.request
        import urllib.error
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            # 尝试解码
            try:
                text = content.decode('utf-8')
            except:
                text = content.decode('gbk', errors='replace')
            
            return ToolResult(True, text, metadata={"url": url, "length": len(text)})
            
    except Exception as e:
        return ToolResult(False, None, str(e))


def _exec_api_call(args: Dict) -> ToolResult:
    """API调用工具"""
    url = args.get("url", "")
    method = args.get("method", "GET")
    headers = args.get("headers", {})
    body = args.get("body", None)
    timeout = args.get("timeout", 30)
    
    if not url:
        return ToolResult(False, None, "URL不能为空")
    
    try:
        import urllib.request
        import json as json_mod
        
        req = urllib.request.Request(url, headers=headers)
        req.get_method = lambda: method
        
        if body and method in ["POST", "PUT", "PATCH"]:
            if isinstance(body, dict):
                body = json_mod.dumps(body).encode('utf-8')
                req.add_header('Content-Type', 'application/json')
            req.data = body
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read().decode('utf-8')
            try:
                data = json_mod.loads(content)
            except:
                data = content
            
            return ToolResult(True, data, metadata={
                "status": response.status,
                "headers": dict(response.headers)
            })
            
    except Exception as e:
        return ToolResult(False, None, str(e))


# ==================== V2.0 新增工具实现 ====================

def _exec_web_search(args: Dict) -> ToolResult:
    """网页搜索工具（眼识扩展）"""
    query = args.get("query", "")
    max_results = args.get("max_results", 5)
    
    if not query:
        return ToolResult(False, None, "搜索关键词不能为空")
    
    try:
        import urllib.parse
        import urllib.request
        
        # 使用 DuckDuckGo 搜索
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='replace')
            
        # 简单解析搜索结果
        results = []
        # 提取搜索结果标题和链接
        pattern = r'<a class="result__a" href="([^"]+)">([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        for url, title in matches[:max_results]:
            results.append({
                "title": title.strip(),
                "url": url
            })
        
        return ToolResult(True, {
            "query": query,
            "count": len(results),
            "results": results
        }, metadata={"engine": "duckduckgo"})
        
    except Exception as e:
        return ToolResult(False, None, f"搜索失败: {str(e)}")


def _exec_grep(args: Dict) -> ToolResult:
    """代码搜索工具（眼识增强）"""
    path = args.get("path", "")
    pattern = args.get("pattern", "")
    file_type = args.get("file_type", "")  # 如 ".py", ".js"
    case_sensitive = args.get("case_sensitive", True)
    max_results = args.get("max_results", 100)
    
    if not path:
        return ToolResult(False, None, "搜索路径不能为空")
    if not pattern:
        return ToolResult(False, None, "搜索模式不能为空")
    
    if not os.path.exists(path):
        return ToolResult(False, None, f"路径不存在: {path}")
    
    try:
        import fnmatch
        
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for root, dirs, files in os.walk(path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in files:
                # 文件类型过滤
                if file_type and not filename.endswith(file_type):
                    continue
                
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(pattern, line, flags):
                                results.append({
                                    "file": filepath,
                                    "line": line_num,
                                    "content": line.strip(),
                                    "match": re.search(pattern, line, flags).group()
                                })
                                if len(results) >= max_results:
                                    break
                except Exception:
                    continue
                
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break
        
        return ToolResult(True, {
            "pattern": pattern,
            "path": path,
            "count": len(results),
            "matches": results
        })
        
    except Exception as e:
        return ToolResult(False, None, f"搜索失败: {str(e)}")


def _exec_file_operations(args: Dict) -> ToolResult:
    """文件操作工具（身识增强）- mkdir, rm, mv, cp"""
    operation = args.get("operation", "")  # mkdir, rm, mv, cp
    source = args.get("source", "")
    target = args.get("target", "")
    
    if not operation:
        return ToolResult(False, None, "操作类型不能为空")
    if not source:
        return ToolResult(False, None, "源路径不能为空")
    
    try:
        if operation == "mkdir":
            os.makedirs(source, exist_ok=True)
            return ToolResult(True, f"目录创建成功: {source}")
        
        elif operation == "rm":
            if os.path.isdir(source):
                shutil.rmtree(source)
            else:
                os.remove(source)
            return ToolResult(True, f"删除成功: {source}")
        
        elif operation == "mv":
            if not target:
                return ToolResult(False, None, "移动操作需要目标路径")
            shutil.move(source, target)
            return ToolResult(True, f"移动成功: {source} -> {target}")
        
        elif operation == "cp":
            if not target:
                return ToolResult(False, None, "复制操作需要目标路径")
            if os.path.isdir(source):
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            return ToolResult(True, f"复制成功: {source} -> {target}")
        
        elif operation == "list":
            items = []
            for item in os.listdir(source):
                full_path = os.path.join(source, item)
                items.append({
                    "name": item,
                    "type": "dir" if os.path.isdir(full_path) else "file",
                    "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                })
            return ToolResult(True, {"path": source, "items": items})
        
        else:
            return ToolResult(False, None, f"未知操作: {operation}")
    
    except Exception as e:
        return ToolResult(False, None, f"操作失败: {str(e)}")


def _exec_code_analysis(args: Dict) -> ToolResult:
    """代码分析工具（末那识）"""
    path = args.get("path", "")
    analysis_type = args.get("type", "stats")  # stats, imports, functions, complexity
    
    if not path:
        return ToolResult(False, None, "代码路径不能为空")
    
    if not os.path.exists(path):
        return ToolResult(False, None, f"文件不存在: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if analysis_type == "stats":
            lines = content.split('\n')
            return ToolResult(True, {
                "path": path,
                "lines": len(lines),
                "characters": len(content),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "bytes": os.path.getsize(path)
            })
        
        elif analysis_type == "imports":
            import_pattern = r'^(?:import|from)\s+([\w.]+)'
            imports = re.findall(import_pattern, content, re.MULTILINE)
            return ToolResult(True, {
                "path": path,
                "imports": list(set(imports)),
                "count": len(set(imports))
            })
        
        elif analysis_type == "functions":
            func_pattern = r'(?:def|class)\s+(\w+)\s*[(\:]'
            matches = re.findall(func_pattern, content)
            return ToolResult(True, {
                "path": path,
                "functions": matches,
                "count": len(matches)
            })
        
        elif analysis_type == "complexity":
            # 简单复杂度估计
            complexity_keywords = ['if', 'elif', 'for', 'while', 'and', 'or', 'except']
            count = sum(content.count(kw) for kw in complexity_keywords)
            return ToolResult(True, {
                "path": path,
                "estimated_complexity": count,
                "level": "low" if count < 20 else "medium" if count < 50 else "high"
            })
        
        else:
            return ToolResult(False, None, f"未知分析类型: {analysis_type}")
    
    except Exception as e:
        return ToolResult(False, None, f"分析失败: {str(e)}")


def _exec_system_info(args: Dict) -> ToolResult:
    """系统信息工具（末那识）"""
    info_type = args.get("type", "all")  # all, cpu, memory, disk, platform
    
    try:
        import platform
        
        result = {"info_type": info_type}
        
        if info_type in ["all", "platform"]:
            result["platform"] = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            }
        
        if info_type in ["all", "cpu"]:
            try:
                import psutil
                result["cpu"] = {
                    "count": psutil.cpu_count(),
                    "percent": psutil.cpu_percent(interval=0.1),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                }
            except ImportError:
                result["cpu"] = {"error": "psutil not available"}
        
        if info_type in ["all", "memory"]:
            try:
                import psutil
                mem = psutil.virtual_memory()
                result["memory"] = {
                    "total": mem.total,
                    "available": mem.available,
                    "percent": mem.percent,
                    "used": mem.used
                }
            except ImportError:
                result["memory"] = {"error": "psutil not available"}
        
        if info_type in ["all", "disk"]:
            try:
                import psutil
                disk = psutil.disk_usage('/')
                result["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            except ImportError:
                result["disk"] = {"error": "psutil not available"}
        
        return ToolResult(True, result)
    
    except Exception as e:
        return ToolResult(False, None, f"获取系统信息失败: {str(e)}")


def _exec_taiyi_oracle(args: Dict) -> ToolResult:
    """太乙预言机工具（太乙）- 高级推理和分析"""
    query = args.get("query", "")
    mode = args.get("mode", "analyze")  # analyze, predict, evaluate
    
    if not query:
        return ToolResult(False, None, "查询不能为空")
    
    try:
        # 太乙预言机核心分析
        result = {
            "query": query,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "微视界": "从微观层面分析问题的具体机制和局部特征",
                "中视界": "从中观层面理解问题的结构关系和演化规律",
                "宏视界": "从宏观层面把握问题的整体趋势和目的导向"
            },
            "insights": [
                f"【太乙视角】{query}需要从多维度进行综合分析",
                "【三视界融合】微视界的具体机制、中视界的结构关系、宏视界的目的导向形成统一分析框架",
                "【太乙约束】在太极阴阳对立统一中寻求平衡点和转化路径"
            ],
            "recommendation": "建议采用渐进式验证策略，结合规则引擎与LLM的混合推理模式"
        }
        
        return ToolResult(True, result, metadata={"oracle_type": "taiyi_v1"})
    
    except Exception as e:
        return ToolResult(False, None, f"太乙预言机分析失败: {str(e)}")


def _exec_hash_calculate(args: Dict) -> ToolResult:
    """哈希计算工具（末那识）"""
    text = args.get("text", "")
    hash_type = args.get("type", "md5")  # md5, sha1, sha256, sha512
    
    if not text:
        return ToolResult(False, None, "文本不能为空")
    
    try:
        if hash_type == "md5":
            result = hashlib.md5(text.encode()).hexdigest()
        elif hash_type == "sha1":
            result = hashlib.sha1(text.encode()).hexdigest()
        elif hash_type == "sha256":
            result = hashlib.sha256(text.encode()).hexdigest()
        elif hash_type == "sha512":
            result = hashlib.sha512(text.encode()).hexdigest()
        else:
            return ToolResult(False, None, f"不支持的哈希类型: {hash_type}")
        
        return ToolResult(True, {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "type": hash_type,
            "hash": result
        })
    
    except Exception as e:
        return ToolResult(False, None, f"哈希计算失败: {str(e)}")


# ==================== 工具执行引擎 ====================

class ToolEngine:
    """工具执行引擎（第五识执行中心）"""

    def __init__(self):
        self.registry = ToolRegistry()
        self._init_builtin_tools()
        self._audit_log = []  # 审计日志

    def _init_builtin_tools(self):
        """初始化内置工具"""
        # 文件读写（身识）
        self.registry.register(ToolDefinition(
            name="file_read",
            description="读取文件内容",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("path", "string", "文件路径", required=True)
            ],
            dangerous=False
        ), _exec_file_read)

        self.registry.register(ToolDefinition(
            name="file_write",
            description="写入文件内容",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("path", "string", "文件路径", required=True),
                ToolParameter("content", "string", "写入内容", required=True),
                ToolParameter("mode", "string", "写入模式：write(覆盖) 或 append(追加)", required=False, default="write")
            ],
            dangerous=True
        ), _exec_file_write)

        # 代码执行（身识）
        self.registry.register(ToolDefinition(
            name="python_run",
            description="执行Python代码",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("code", "string", "Python代码", required=True),
                ToolParameter("timeout", "number", "超时时间（秒）", required=False, default=30)
            ],
            dangerous=True
        ), _exec_python_run)

        self.registry.register(ToolDefinition(
            name="bash_run",
            description="执行Bash命令",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("command", "string", "Bash命令", required=True),
                ToolParameter("timeout", "number", "超时时间（秒）", required=False, default=30)
            ],
            dangerous=True
        ), _exec_bash_run)

        # 网页抓取（眼识）
        self.registry.register(ToolDefinition(
            name="web_fetch",
            description="抓取网页内容",
            category=ToolCategory.SIGHT,
            parameters=[
                ToolParameter("url", "string", "网页URL", required=True),
                ToolParameter("timeout", "number", "超时时间（秒）", required=False, default=10)
            ],
            dangerous=False
        ), _exec_web_fetch)

        # API调用（身识）
        self.registry.register(ToolDefinition(
            name="api_call",
            description="调用API接口",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("url", "string", "API URL", required=True),
                ToolParameter("method", "string", "HTTP方法", required=False, default="GET"),
                ToolParameter("headers", "object", "请求头", required=False, default={}),
                ToolParameter("body", "object", "请求体", required=False, default=None),
                ToolParameter("timeout", "number", "超时时间（秒）", required=False, default=30)
            ],
            dangerous=False
        ), _exec_api_call)

        # ========== V2.0 新增工具 ==========

        # 网页搜索（眼识扩展）
        self.registry.register(ToolDefinition(
            name="web_search",
            description="网页搜索工具",
            category=ToolCategory.SIGHT,
            parameters=[
                ToolParameter("query", "string", "搜索关键词", required=True),
                ToolParameter("max_results", "number", "最大结果数", required=False, default=5)
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.0.0", tags=["search", "web"])
        ), _exec_web_search, groups=["search", "information"])

        # 代码搜索（眼识增强）
        self.registry.register(ToolDefinition(
            name="grep",
            description="代码搜索工具",
            category=ToolCategory.SIGHT,
            parameters=[
                ToolParameter("path", "string", "搜索路径", required=True),
                ToolParameter("pattern", "string", "正则表达式模式", required=True),
                ToolParameter("file_type", "string", "文件类型过滤（如.py）", required=False, default=""),
                ToolParameter("case_sensitive", "boolean", "是否区分大小写", required=False, default=True),
                ToolParameter("max_results", "number", "最大结果数", required=False, default=100)
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.0.0", tags=["search", "code"])
        ), _exec_grep, groups=["search", "code"])

        # 文件操作（身识增强）
        self.registry.register(ToolDefinition(
            name="file_ops",
            description="文件操作工具（mkdir/rm/mv/cp/list）",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("operation", "string", "操作类型：mkdir/rm/mv/cp/list", required=True,
                            enum=["mkdir", "rm", "mv", "cp", "list"]),
                ToolParameter("source", "string", "源路径", required=True),
                ToolParameter("target", "string", "目标路径（mv/cp操作需要）", required=False, default="")
            ],
            dangerous=True,
            metadata=ToolMetadata(version="2.0.0", tags=["file", "filesystem"])
        ), _exec_file_operations, groups=["file"])

        # 代码分析（末那识）
        self.registry.register(ToolDefinition(
            name="code_analysis",
            description="代码分析工具",
            category=ToolCategory.MANAS,
            parameters=[
                ToolParameter("path", "string", "代码文件路径", required=True),
                ToolParameter("type", "string", "分析类型：stats/imports/functions/complexity",
                            required=False, default="stats",
                            enum=["stats", "imports", "functions", "complexity"])
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.0.0", tags=["analysis", "code"])
        ), _exec_code_analysis, groups=["analysis", "code"])

        # 系统信息（末那识）
        self.registry.register(ToolDefinition(
            name="system_info",
            description="系统信息工具",
            category=ToolCategory.MANAS,
            parameters=[
                ToolParameter("type", "string", "信息类型：all/cpu/memory/disk/platform",
                            required=False, default="all",
                            enum=["all", "cpu", "memory", "disk", "platform"])
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.0.0", tags=["system", "info"])
        ), _exec_system_info, groups=["system", "info"])

        # 太乙预言机（太乙）
        self.registry.register(ToolDefinition(
            name="taiyi_oracle",
            description="太乙预言机工具 - 三视界分析",
            category=ToolCategory.TAIYI,
            parameters=[
                ToolParameter("query", "string", "分析查询", required=True),
                ToolParameter("mode", "string", "分析模式：analyze/predict/evaluate",
                            required=False, default="analyze",
                            enum=["analyze", "predict", "evaluate"])
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.0.0", tags=["oracle", "taiyi", "reasoning"])
        ), _exec_taiyi_oracle, groups=["oracle", "taiyi"], namespace="taiyi")

        # 哈希计算（末那识）
        self.registry.register(ToolDefinition(
            name="hash_calculate",
            description="哈希计算工具",
            category=ToolCategory.MANAS,
            parameters=[
                ToolParameter("text", "string", "要计算哈希的文本", required=True),
                ToolParameter("type", "string", "哈希类型：md5/sha1/sha256/sha512",
                            required=False, default="sha256",
                            enum=["md5", "sha1", "sha256", "sha512"])
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.0.0", tags=["hash", "crypto"])
        ), _exec_hash_calculate, groups=["utility"])

        # ========== UFO² 具身执行层（身识扩展 - 桌面自动化）==========
        
        # UFO² 桌面任务执行
        def _exec_ufo2_desktop(args: Dict) -> ToolResult:
            """UFO² 桌面任务执行器"""
            task = args.get("task", "")
            if not task:
                return ToolResult(False, None, "任务描述不能为空")
            try:
                from modules.taiyi_embodiment import get_embodiment
                import asyncio
                embodiment = get_embodiment()
                result = asyncio.run(embodiment.execute_desktop_task(task))
                return ToolResult(True, result)
            except Exception as e:
                return ToolResult(False, None, str(e))
        
        self.registry.register(ToolDefinition(
            name="ufo2_desktop_control",
            description="通过 UFO² AgentOS 执行 Windows 桌面自动化任务",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("task", "string", "要执行的桌面任务描述（如：打开记事本、关闭浏览器等）", required=True)
            ],
            dangerous=True,
            metadata=ToolMetadata(version="2.1.0", tags=["embodiment", "desktop", "automation", "ufo2"])
        ), _exec_ufo2_desktop, groups=["embodiment", "desktop"])
        
        # UFO² 应用控制
        def _exec_ufo2_app(args: Dict) -> ToolResult:
            """UFO² 应用控制执行器"""
            app = args.get("app", "")
            action = args.get("action", "")
            params = args.get("params", {})
            if not app or not action:
                return ToolResult(False, None, "应用名和动作不能为空")
            try:
                from modules.taiyi_embodiment import get_embodiment
                import asyncio
                embodiment = get_embodiment()
                result = embodiment.execute_action(app, action, params)
                return ToolResult(True, result)
            except Exception as e:
                return ToolResult(False, None, str(e))
        
        self.registry.register(ToolDefinition(
            name="ufo2_app_control",
            description="控制特定应用的 UFO² AppAgent（Excel/Word/Chrome等）",
            category=ToolCategory.BODY,
            parameters=[
                ToolParameter("app", "string", "应用名称（如：excel, word, chrome, notepad）", required=True),
                ToolParameter("action", "string", "动作（如：click, type, scroll, set_cell）", required=True),
                ToolParameter("params", "object", "动作参数", required=False, default={})
            ],
            dangerous=True,
            metadata=ToolMetadata(version="2.1.0", tags=["embodiment", "app", "control", "ufo2"])
        ), _exec_ufo2_app, groups=["embodiment", "app"])
        
        # UFO² 截图
        def _exec_ufo2_capture(args: Dict) -> ToolResult:
            """UFO² 截图执行器"""
            target = args.get("target", "desktop")
            try:
                from modules.taiyi_embodiment import MCPServer
                msg_id = f"capture_{target}"
                mcp = MCPServer("capture")
                result = mcp.handle(type('Message', (), {
                    'id': msg_id,
                    'method': 'capture_desktop_screenshot' if target == 'desktop' else 'capture_screenshot',
                    'params': {}
                })())
                return ToolResult(True, result.result)
            except Exception as e:
                return ToolResult(False, None, str(e))
        
        self.registry.register(ToolDefinition(
            name="ufo2_capture",
            description="捕获桌面或窗口截图（用于视觉感知）",
            category=ToolCategory.SIGHT,
            parameters=[
                ToolParameter("target", "string", "截图目标：desktop（桌面）或 window（当前窗口）", 
                            required=False, default="desktop")
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.1.0", tags=["embodiment", "vision", "screenshot", "ufo2"])
        ), _exec_ufo2_capture, groups=["embodiment", "vision"])
        
        # UFO² UI 树
        def _exec_ufo2_ui_tree(args: Dict) -> ToolResult:
            """UFO² UI 树执行器"""
            app = args.get("app", "")
            try:
                from modules.taiyi_embodiment import MCPServer
                mcp = MCPServer("ui_tree")
                result = mcp.handle(type('Message', (), {
                    'id': 'ui_tree',
                    'method': 'get_ui_tree',
                    'params': {'app': app}
                })())
                return ToolResult(True, result.result)
            except Exception as e:
                return ToolResult(False, None, str(e))
        
        self.registry.register(ToolDefinition(
            name="ufo2_ui_tree",
            description="获取 UI 元素树（用于了解界面结构）",
            category=ToolCategory.SIGHT,
            parameters=[
                ToolParameter("app", "string", "应用名称（可选，不填则获取当前焦点窗口）", required=False, default="")
            ],
            dangerous=False,
            metadata=ToolMetadata(version="2.1.0", tags=["embodiment", "ui", "tree", "ufo2"])
        ), _exec_ufo2_ui_tree, groups=["embodiment", "ui"])

    def execute(self, tool_name: str, args: Dict, audit: bool = True) -> ToolResult:
        """执行工具（带审计和执行时间追踪）"""
        import time
        start_time = time.time()
        
        executor = self.registry.get_executor(tool_name)
        if not executor:
            return ToolResult(False, None, f"工具不存在: {tool_name}")

        # 审计日志
        if audit:
            log_entry = {
                "tool": tool_name,
                "args": args,
                "timestamp": datetime.now().isoformat()
            }
            self._audit_log.append(log_entry)

        # 执行
        try:
            result = executor(args)
            if isinstance(result, ToolResult):
                result.execution_time = time.time() - start_time
                if audit:
                    log_entry["result"] = result.success
                    log_entry["output_length"] = len(str(result.output)) if result.output else 0
                    log_entry["execution_time"] = result.execution_time
            return result
        except Exception as e:
            error_msg = f"工具执行异常: {e}\n{traceback.format_exc()}"
            if audit:
                log_entry["error"] = error_msg
            return ToolResult(False, None, error_msg, execution_time=time.time() - start_time)

    def execute_batch(self, calls: List[Dict], audit: bool = True) -> List[ToolResult]:
        """批量执行工具"""
        results = []
        for call in calls:
            tool_name = call.get("tool")
            args = call.get("args", {})
            result = self.execute(tool_name, args, audit)
            results.append(result)
        return results

    def execute_async(self, tool_name: str, args: Dict, callback: Callable = None) -> asyncio.Task:
        """异步执行工具"""
        import time
        
        async def _async_execute():
            start_time = time.time()
            result = self.execute(tool_name, args, audit=True)
            result.execution_time = time.time() - start_time
            
            if callback:
                callback(result)
            
            return result
        
        loop = asyncio.get_event_loop()
        return loop.create_task(_async_execute())

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        return self._audit_log[-limit:]

    def clear_audit_log(self):
        """清空审计日志"""
        self._audit_log.clear()

    def get_tool_definitions(self) -> List[Dict]:
        """获取工具定义（用于LLM Function Calling）"""
        return self.registry.get_openai_functions()

    def get_stats(self) -> Dict:
        """获取工具引擎统计"""
        return self.registry.get_stats()


# ==================== 全局引擎 ====================

_engine_instance = None
_engine_lock = threading.Lock()


def get_tool_engine() -> ToolEngine:
    """获取全局工具引擎（线程安全）"""
    global _engine_instance
    if _engine_instance is None:
        with _engine_lock:
            if _engine_instance is None:
                _engine_instance = ToolEngine()
    return _engine_instance


# ==================== 测试 ====================

if __name__ == "__main__":
    # 测试工具引擎
    engine = get_tool_engine()

    print("🔧 工具引擎测试")
    print("=" * 60)

    # 列出所有工具
    print("\n📋 已注册工具:")
    for tool in engine.registry.list_tools():
        print(f"  • {tool.name} ({tool.category.value}) - {tool.description}")

    # 测试文件读取
    print("\n🧪 测试: file_read")
    result = engine.execute("file_read", {"path": "app.py"})
    print(f"  成功: {result.success}")
    if result.success:
        print(f"  输出长度: {len(result.output)} 字符")
    else:
        print(f"  错误: {result.error}")

    # 测试Python执行
    print("\n🧪 测试: python_run")
    result = engine.execute("python_run", {"code": "print('Hello from Taiyi Tools!')\nx = 1 + 2\nprint(f'1+2={x}')"})
    print(f"  成功: {result.success}")
    if result.success:
        print(f"  输出: {result.output['stdout']}")
    else:
        print(f"  错误: {result.error}")

    # 测试网页抓取
    print("\n🧪 测试: web_fetch")
    result = engine.execute("web_fetch", {"url": "http://httpbin.org/get"})
    print(f"  成功: {result.success}")
    if result.success:
        print(f"  内容长度: {result.metadata['length']} 字符")
    else:
        print(f"  错误: {result.error}")

    # 显示审计日志
    print("\n📝 审计日志:")
    for log in engine.get_audit_log():
        print(f"  • {log['timestamp']} - {log['tool']} - 成功:{log.get('result', 'N/A')}")

    print("\n✅ 工具引擎测试完成")
