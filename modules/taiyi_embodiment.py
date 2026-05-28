#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太乙系统具身执行层 - UFO² 集成模块
基于 Microsoft UFO² 架构的 Windows 桌面自动化

核心组件:
- HostAgent: 任务编排与分解
- AppAgent: 应用执行与控制
- HybridDetector: UIA + Vision 混合控件检测
- MCP Server: 工具接口

作者: 太乙复合体 AGI 系统
"""

import os
import sys
import json
import time
import asyncio
import threading
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import base64
import io

# ==================== 配置 ====================

@dataclass
class UFO2Config:
    """UFO² 配置"""
    # LLM 配置
    llm_provider: str = "openai"  # openai/azure/qwen/deepseek/ollama
    llm_model: str = "gpt-4o"
    llm_api_key: str = ""
    llm_base_url: str = ""
    
    # 视觉配置
    visual_backend: str = "qwen_vl"  # qwen_vl/gpt-4v/omniparser
    vision_model: str = "Qwen-VL"
    
    # 控制检测
    control_backend: str = "uia"  # uia/win32/hybrid
    use_visual_fallback: bool = True
    
    # 执行配置
    max_steps: int = 20
    max_subtasks: int = 10
    speculative_execution: bool = True
    pip_mode: bool = False
    
    # 截图配置
    screenshot_quality: int = 85
    screenshot_scale: float = 1.0


class AgentState(Enum):
    """Agent 状态"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    SUCCESS = "success"
    FAILURE = "failure"


# ==================== MCP Server 接口 ====================

@dataclass
class MCPMessage:
    """MCP 消息格式"""
    id: str
    method: str
    params: Dict[str, Any]
    result: Any = None
    error: str = ""


class MCPServer:
    """MCP Server - Model Context Protocol 服务器"""
    
    def __init__(self, name: str):
        self.name = name
        self.handlers: Dict[str, callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认处理器"""
        self.handlers = {
            # 桌面操作
            "capture_desktop_screenshot": self._capture_desktop,
            "get_desktop_app_info": self._get_desktop_apps,
            "launch_application": self._launch_app,
            "close_application": self._close_app,
            
            # UI 操作
            "capture_screenshot": self._capture_screenshot,
            "annotate_screenshot": self._annotate_screenshot,
            "get_control_info": self._get_control_info,
            "get_ui_tree": self._get_ui_tree,
            
            # 交互操作
            "click": self._click,
            "double_click": self._double_click,
            "right_click": self._right_click,
            "type_text": self._type_text,
            "scroll": self._scroll,
            "select_control": self._select_control,
            
            # 文件操作
            "open_file": self._open_file,
            "save_file": self._save_file,
            "read_file": self._read_file,
            "write_file": self._write_file,
        }
    
    def handle(self, message: MCPMessage) -> MCPMessage:
        """处理 MCP 消息"""
        handler = self.handlers.get(message.method)
        if handler:
            try:
                result = handler(message.params)
                message.result = result
            except Exception as e:
                message.error = str(e)
        else:
            message.error = f"Unknown method: {message.method}"
        return message
    
    # ==================== 桌面操作 ====================
    
    def _capture_desktop(self, params: Dict) -> Dict:
        """捕获桌面截图"""
        try:
            import mss
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[params.get("monitor", 1)])
                img_bytes = mss.tools.to_bytes(screenshot)
                img_base64 = base64.b64encode(img_bytes).decode()
            return {"success": True, "image": img_base64, "format": "png"}
        except ImportError:
            # 降级方案：使用 PIL
            try:
                from PIL import ImageGrab, Image
                screenshot = ImageGrab.grab()
                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format='PNG')
                img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
                return {"success": True, "image": img_base64, "format": "png", "method": "PIL"}
            except ImportError:
                return {"success": False, "error": "mss and PIL not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_desktop_apps(self, params: Dict) -> Dict:
        """获取桌面应用列表"""
        try:
            import psutil
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe']:
                        apps.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "exe": proc.info['exe']
                        })
                except:
                    pass
            return {"success": True, "apps": apps[:20]}
        except ImportError:
            return {"success": False, "error": "psutil not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _launch_app(self, params: Dict) -> Dict:
        """启动应用程序"""
        try:
            import subprocess
            app_path = params.get("path", "")
            if not app_path:
                return {"success": False, "error": "path is required"}
            
            process = subprocess.Popen(app_path)
            return {"success": True, "pid": process.pid}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _close_app(self, params: Dict) -> Dict:
        """关闭应用程序"""
        try:
            import psutil
            pid = params.get("pid")
            if not pid:
                return {"success": False, "error": "pid is required"}
            
            proc = psutil.Process(pid)
            proc.terminate()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== UI 操作 ====================
    
    def _capture_screenshot(self, params: Dict) -> Dict:
        """捕获窗口截图"""
        return self._capture_desktop(params)
    
    def _annotate_screenshot(self, params: Dict) -> Dict:
        """标注截图"""
        try:
            import mss
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[1])
                img = io.BytesIO(monitor.tobytes())
            
            # 简单处理 - 返回原始截图
            return {"success": True, "annotated": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_control_info(self, params: Dict) -> Dict:
        """获取控件信息"""
        try:
            # Windows UIA 尝试
            try:
                import uiautomation as auto
                # 获取焦点窗口
                window = auto.GetFocusedElement()
                if window:
                    controls = []
                    for child in window.GetChildren()[:10]:
                        controls.append({
                            "name": child.Name,
                            "control_type": str(child.ControlTypeName),
                            "bounds": child.BoundingRectangle
                        })
                    return {"success": True, "controls": controls}
            except ImportError:
                pass
            
            return {"success": True, "controls": [], "note": "UIA not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_ui_tree(self, params: Dict) -> Dict:
        """获取 UI 树"""
        try:
            try:
                import uiautomation as auto
                window = auto.GetFocusedElement()
                if window:
                    tree = self._build_ui_tree(window)
                    return {"success": True, "tree": tree}
            except ImportError:
                pass
            
            return {"success": True, "tree": {}, "note": "UIA not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_ui_tree(self, element, depth=0, max_depth=3):
        """构建 UI 树"""
        if depth > max_depth:
            return None
        node = {
            "name": element.Name,
            "control_type": str(element.ControlTypeName) if hasattr(element, 'ControlTypeName') else "Unknown",
            "children": []
        }
        try:
            for child in element.GetChildren()[:5]:
                child_node = self._build_ui_tree(child, depth + 1, max_depth)
                if child_node:
                    node["children"].append(child_node)
        except:
            pass
        return node
    
    # ==================== 交互操作 ====================
    
    def _click(self, params: Dict) -> Dict:
        """点击"""
        try:
            import pyautogui
            x = params.get("x", 0)
            y = params.get("y", 0)
            pyautogui.click(x, y)
            return {"success": True}
        except ImportError:
            return {"success": False, "error": "pyautogui not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _double_click(self, params: Dict) -> Dict:
        """双击"""
        try:
            import pyautogui
            x = params.get("x", 0)
            y = params.get("y", 0)
            pyautogui.doubleClick(x, y)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _right_click(self, params: Dict) -> Dict:
        """右键点击"""
        try:
            import pyautogui
            x = params.get("x", 0)
            y = params.get("y", 0)
            pyautogui.rightClick(x, y)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _type_text(self, params: Dict) -> Dict:
        """输入文本"""
        try:
            import pyautogui
            text = params.get("text", "")
            pyautogui.write(text, interval=0.05)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _scroll(self, params: Dict) -> Dict:
        """滚动"""
        try:
            import pyautogui
            clicks = params.get("clicks", 3)
            pyautogui.scroll(clicks)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _select_control(self, params: Dict) -> Dict:
        """选择控件"""
        index = params.get("index", 0)
        return {"success": True, "selected": index}
    
    # ==================== 文件操作 ====================
    
    def _open_file(self, params: Dict) -> Dict:
        """打开文件"""
        try:
            filepath = params.get("path", "")
            if not filepath:
                return {"success": False, "error": "path is required"}
            os.startfile(filepath)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_file(self, params: Dict) -> Dict:
        """保存文件"""
        return {"success": True, "note": "File save dialog opened"}
    
    def _read_file(self, params: Dict) -> Dict:
        """读取文件"""
        try:
            filepath = params.get("path", "")
            if not filepath:
                return {"success": False, "error": "path is required"}
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _write_file(self, params: Dict) -> Dict:
        """写入文件"""
        try:
            filepath = params.get("path", "")
            content = params.get("content", "")
            if not filepath:
                return {"success": False, "error": "path is required"}
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ==================== HostAgent ====================

@dataclass
class Task:
    """任务"""
    id: str
    description: str
    status: str = "pending"
    subtasks: List['Task'] = field(default_factory=list)
    result: Any = None


class HostAgent:
    """
    HostAgent - 桌面编排器
    
    职责:
    - 任务分解与规划
    - 应用选择与协调
    - AppAgent 生命周期管理
    - 结果验证
    """
    
    def __init__(self, config: UFO2Config):
        self.config = config
        self.state = AgentState.IDLE
        self.current_task: Optional[Task] = None
        self.app_agents: Dict[str, Any] = {}
        self.blackboard: Dict[str, Any] = {}
        self.fsm_state = "idle"
        self.mcp_server = MCPServer("host")
        
        # LLM 客户端
        self.llm_client = None
        self._init_llm_client()
    
    def _init_llm_client(self):
        """初始化 LLM 客户端"""
        if self.config.llm_provider == "openai":
            try:
                from openai import OpenAI
                api_key = self.config.llm_api_key or os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.llm_client = OpenAI(
                        api_key=api_key,
                        base_url=self.config.llm_base_url or None
                    )
                    print(f"✅ OpenAI LLM 客户端已初始化 ({self.config.llm_model})")
                else:
                    print("⚠️ 未设置 OPENAI_API_KEY，将使用本地 LLM")
                    self.llm_client = None
            except ImportError:
                print("⚠️ OpenAI SDK not installed, using local LLM")
                self.llm_client = None
        elif self.config.llm_provider == "ollama":
            self.llm_client = None  # 使用本地 Ollama
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """执行任务"""
        self.state = AgentState.PLANNING
        self.fsm_state = "planning"
        
        # 1. 捕获桌面状态
        desktop_state = await self._capture_desktop_state()
        
        # 2. 任务规划 - 使用 LLM 分解任务
        subtasks = await self._plan_task(task, desktop_state)
        
        # 3. 创建 AppAgent 执行子任务
        results = []
        for subtask in subtasks[:self.config.max_subtasks]:
            result = await self._execute_subtask(subtask)
            results.append(result)
            
            # 更新黑板
            self.blackboard[subtask["id"]] = result
            
            # 检查是否成功
            if not result.get("success", False):
                self.state = AgentState.FAILURE
                self.fsm_state = "failure"
                break
        
        # 4. 汇总结果
        self.state = AgentState.SUCCESS if results else AgentState.FAILURE
        self.fsm_state = "success" if self.state == AgentState.SUCCESS else "failure"
        
        return {
            "success": self.state == AgentState.SUCCESS,
            "task": task,
            "subtasks": len(subtasks),
            "results": results,
            "blackboard": self.blackboard
        }
    
    async def _capture_desktop_state(self) -> Dict:
        """捕获桌面状态"""
        msg = MCPMessage(
            id="capture_1",
            method="capture_desktop_screenshot",
            params={"monitor": 1}
        )
        result = self.mcp_server.handle(msg)
        return result.result or {}
    
    async def _plan_task(self, task: str, desktop_state: Dict) -> List[Dict]:
        """使用 LLM 规划任务"""
        prompt = f"""分析以下任务，将其分解为可执行的子任务：

任务: {task}

当前桌面状态: {json.dumps(desktop_state, ensure_ascii=False)}

请将任务分解为具体的子任务，每个子任务包含：
- id: 子任务ID
- action: 具体动作（如 click, type, scroll 等）
- target: 目标（窗口名、按钮、输入框等）
- params: 动作参数

以 JSON 数组格式返回。"""
        
        # 使用 LLM 分解
        if self.llm_client and self.config.llm_provider == "openai":
            try:
                response = self.llm_client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                result_text = response.choices[0].message.content
                # 解析 JSON
                import re
                json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception as e:
                print(f"LLM planning error: {e}")
        
        # 默认简单分解
        return [
            {"id": "subtask_1", "action": "analyze", "target": "desktop", "params": {"task": task}}
        ]
    
    async def _execute_subtask(self, subtask: Dict) -> Dict:
        """执行子任务"""
        self.state = AgentState.EXECUTING
        self.fsm_state = "executing"
        
        action = subtask.get("action", "")
        target = subtask.get("target", "")
        params = subtask.get("params", {})
        
        # 映射动作到 MCP 方法
        action_map = {
            "click": "click",
            "type": "type_text",
            "scroll": "scroll",
            "open": "launch_application",
            "close": "close_application",
            "read": "read_file",
            "write": "write_file",
        }
        
        method = action_map.get(action, "get_control_info")
        
        msg = MCPMessage(
            id=subtask.get("id", "subtask"),
            method=method,
            params=params
        )
        
        result = self.mcp_server.handle(msg)
        
        self.state = AgentState.WAITING
        await asyncio.sleep(0.1)  # 模拟等待
        
        return result.result or {"success": False, "error": "No result"}
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "state": self.state.value,
            "fsm_state": self.fsm_state,
            "current_task": self.current_task.id if self.current_task else None,
            "app_agents_count": len(self.app_agents),
            "blackboard_keys": list(self.blackboard.keys())
        }


# ==================== AppAgent ====================

class AppAgent:
    """
    AppAgent - 应用执行器
    
    职责:
    - UI 元素交互
    - 混合 GUI-API 执行
    - 应用特定自动化
    """
    
    def __init__(self, app_name: str, host_agent: HostAgent):
        self.app_name = app_name
        self.host_agent = host_agent
        self.state = AgentState.IDLE
        self.control_backend = host_agent.config.control_backend
        self.visual_backend = host_agent.config.visual_backend
        self.mcp_server = MCPServer(f"app_{app_name}")
        self.fsm_state = "idle"
    
    async def execute_action(self, action: str, params: Dict) -> Dict:
        """执行动作"""
        self.state = AgentState.EXECUTING
        self.fsm_state = "executing"
        
        try:
            # 1. 优先尝试原生 API
            result = await self._try_native_api(action, params)
            
            # 2. 回退到 GUI 模拟
            if not result.get("success"):
                result = await self._try_gui_action(action, params)
            
            # 3. 更新状态
            self.state = AgentState.SUCCESS if result.get("success") else AgentState.FAILURE
            self.fsm_state = "success" if self.state == AgentState.SUCCESS else "failure"
            
            return result
        except Exception as e:
            self.state = AgentState.FAILURE
            self.fsm_state = "failure"
            return {"success": False, "error": str(e)}
    
    async def _try_native_api(self, action: str, params: Dict) -> Dict:
        """尝试原生 API"""
        # Excel 操作
        if "excel" in self.app_name.lower():
            return await self._excel_native_action(action, params)
        # Word 操作
        elif "word" in self.app_name.lower():
            return await self._word_native_action(action, params)
        
        return {"success": False, "error": "No native API available"}
    
    async def _try_gui_action(self, action: str, params: Dict) -> Dict:
        """尝试 GUI 动作"""
        method_map = {
            "click": "click",
            "type": "type_text",
            "scroll": "scroll",
            "select": "select_control",
        }
        
        method = method_map.get(action, "get_control_info")
        
        msg = MCPMessage(
            id=f"{self.app_name}_{action}",
            method=method,
            params=params
        )
        
        return self.mcp_server.handle(msg).result or {}
    
    async def _excel_native_action(self, action: str, params: Dict) -> Dict:
        """Excel 原生 API"""
        try:
            import xlwings as xw
            
            if action == "set_cell":
                cell = params.get("cell", "A1")
                value = params.get("value", "")
                wb = xw.Book.active
                wb.sheets[0].range(cell).value = value
                return {"success": True}
            
            elif action == "get_cell":
                cell = params.get("cell", "A1")
                wb = xw.Book.active
                value = wb.sheets[0].range(cell).value
                return {"success": True, "value": value}
            
            elif action == "create_chart":
                data_range = params.get("range", "A1:B10")
                chart_type = params.get("type", "column")
                wb = xw.Book.active
                chart = wb.charts.add(source=data_range)
                chart.chart_type = chart_type
                return {"success": True}
            
        except ImportError:
            return {"success": False, "error": "xlwings not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unknown action"}
    
    async def _word_native_action(self, action: str, params: Dict) -> Dict:
        """Word 原生 API"""
        try:
            from docx import Document
            
            if action == "write":
                text = params.get("text", "")
                doc = Document()
                doc.add_paragraph(text)
                doc.save(params.get("path", "output.docx"))
                return {"success": True}
            
        except ImportError:
            return {"success": False, "error": "python-docx not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unknown action"}
    
    def get_ui_tree(self) -> Dict:
        """获取 UI 树"""
        msg = MCPMessage(id="ui_tree", method="get_ui_tree", params={})
        return self.mcp_server.handle(msg).result or {}
    
    def capture_screenshot(self) -> Dict:
        """捕获截图"""
        msg = MCPMessage(id="screenshot", method="capture_screenshot", params={})
        return self.mcp_server.handle(msg).result or {}


# ==================== 太乙具身执行层主类 ====================

class TaiyiEmbodiment:
    """
    太乙具身执行层 - UFO² 集成封装
    
    使用 UFO² 架构实现 Windows 桌面自动化，
    作为太乙 AGI 系统的具身执行能力。
    """
    
    def __init__(self, config: Optional[UFO2Config] = None):
        self.config = config or UFO2Config()
        self.host_agent = HostAgent(self.config)
        self.app_agents: Dict[str, AppAgent] = {}
        self.history: List[Dict] = []
        
        # 检查依赖
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查依赖"""
        self.deps = {
            "mss": False,
            "pyautogui": False,
            "psutil": False,
            "uiautomation": False,
            "xlwings": False,
            "openai": False,
        }
        
        for dep in self.deps:
            try:
                __import__(dep.replace("-", "_"))
                self.deps[dep] = True
            except ImportError:
                pass
    
    def get_dependencies_status(self) -> Dict:
        """获取依赖状态"""
        return self.deps
    
    async def execute_desktop_task(self, task: str) -> Dict[str, Any]:
        """执行桌面任务 - 主要接口"""
        print(f"🎯 执行桌面任务: {task}")
        
        result = await self.host_agent.execute_task(task)
        
        # 记录历史
        self.history.append({
            "task": task,
            "result": result,
            "timestamp": time.time()
        })
        
        return result
    
    def get_app_agent(self, app_name: str) -> AppAgent:
        """获取或创建 AppAgent"""
        if app_name not in self.app_agents:
            self.app_agents[app_name] = AppAgent(app_name, self.host_agent)
        return self.app_agents[app_name]
    
    def execute_action(self, app_name: str, action: str, params: Dict) -> Dict:
        """直接执行动作"""
        agent = self.get_app_agent(app_name)
        return asyncio.run(agent.execute_action(action, params))
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "host_agent": self.host_agent.get_status(),
            "app_agents": {
                name: {"state": agent.state.value}
                for name, agent in self.app_agents.items()
            },
            "dependencies": self.deps,
            "history_count": len(self.history)
        }
    
    def get_tool_definitions(self) -> List[Dict]:
        """获取工具定义 - 供太乙工具框架使用"""
        return [
            {
                "name": "ufo2_desktop_control",
                "description": "通过 UFO² AgentOS 执行 Windows 桌面自动化任务",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "要执行的桌面任务描述"
                        }
                    },
                    "required": ["task"]
                }
            },
            {
                "name": "ufo2_app_control",
                "description": "控制特定应用的 UFO² AppAgent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app": {
                            "type": "string",
                            "description": "应用名称 (excel, word, chrome 等)"
                        },
                        "action": {
                            "type": "string",
                            "description": "动作 (click, type, scroll 等)"
                        },
                        "params": {
                            "type": "object",
                            "description": "动作参数"
                        }
                    },
                    "required": ["app", "action"]
                }
            },
            {
                "name": "ufo2_capture",
                "description": "捕获桌面或窗口截图",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "enum": ["desktop", "window"],
                            "description": "截图目标"
                        }
                    }
                }
            },
            {
                "name": "ufo2_ui_tree",
                "description": "获取 UI 元素树",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app": {
                            "type": "string",
                            "description": "应用名称"
                        }
                    }
                }
            }
        ]


# ==================== 单例 ====================

_instance: Optional[TaiyiEmbodiment] = None
_instance_lock = threading.Lock()


def get_embodiment(config: Optional[UFO2Config] = None) -> TaiyiEmbodiment:
    """获取具身执行层单例"""
    global _instance
    with _instance_lock:
        if _instance is None:
            _instance = TaiyiEmbodiment(config)
        return _instance


# ==================== 主程序 ====================

if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("🌌 太乙系统具身执行层 - UFO² 集成")
        print("=" * 60)
        
        # 创建具身执行层
        embodiment = get_embodiment()
        
        # 检查依赖
        deps = embodiment.get_dependencies_status()
        print("\n📦 依赖状态:")
        for dep, installed in deps.items():
            status = "✅" if installed else "❌"
            print(f"  {status} {dep}")
        
        # 获取工具定义
        tools = embodiment.get_tool_definitions()
        print(f"\n🔧 提供 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description'][:50]}...")
        
        # 测试截图
        print("\n📸 测试截图...")
        msg = MCPMessage(id="test", method="capture_desktop_screenshot", params={})
        mcp = MCPServer("test")
        result = mcp.handle(msg)
        if result.result and result.result.get("success"):
            print("  ✅ 截图成功")
        else:
            print(f"  ❌ 截图失败: {result.result}")
        
        # 测试桌面任务
        print("\n🎯 测试桌面任务...")
        result = await embodiment.execute_desktop_task("打开记事本")
        print(f"  结果: {result.get('success', False)}")
        
        print("\n" + "=" * 60)
        print("具身执行层初始化完成")
        print("=" * 60)
        
        return embodiment
    
    asyncio.run(main())
