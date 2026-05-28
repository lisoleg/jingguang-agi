#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM集成模块 - 多后端支持
支持：Ollama、在线API、规则引擎fallback
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any

# 添加缓存支持
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.cache_manager import cached, cache_manager

# 添加D盘Python路径（用于ctransformers）
sys.path.insert(0, "D:/Apps/Python")

# 模型配置
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

# Ollama配置
OLLAMA_API_BASE = "http://localhost:11434/api"

# 在线API配置（可配置）
ONLINE_API_URL = ""  # 例如：https://api.openai.com/v1/chat/completions
ONLINE_API_KEY = ""  # 从环境变量读取

# DeepSeek配置（优先使用）
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"  # 可选: deepseek-reasoner


class LLMBackend:
    """LLM后端基类"""
    def __init__(self, name: str):
        self.name = name
        self.ready = False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        raise NotImplementedError
    
    def is_ready(self) -> bool:
        return self.ready


class OllamaBackend(LLMBackend):
    """Ollama后端"""
    def __init__(self, model: str = "qwen2:3b"):
        super().__init__("ollama")
        self.model = model
        self.api_base = OLLAMA_API_BASE
        self._check_ready()
    
    def _check_ready(self):
        try:
            resp = requests.get(f"{self.api_base}/tags", timeout=2)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if self.model in models:
                    self.ready = True
                else:
                    print(f"⚠️ Ollama已运行但未拉取模型 {self.model}")
                    print(f"   请运行: ollama pull {self.model}")
            else:
                self.ready = False
        except:
            self.ready = False
    
    @cached('llm_cache', ttl=3600)
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        try:
            resp = requests.post(
                f"{self.api_base}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
            return f"[Ollama错误: {resp.text}]"
        except Exception as e:
            return f"[Ollama异常: {e}]"


class OnlineAPIBackend(LLMBackend):
    """在线API后端（OpenAI兼容）"""
    def __init__(self, api_url: str, api_key: str, model: str):
        super().__init__("online_api")
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.ready = bool(api_url and api_key)
    
    @cached('llm_cache', ttl=3600)
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[API错误: {resp.text}]"
        except Exception as e:
            return f"[API异常: {e}]"


class RuleEngineBackend(LLMBackend):
    """规则引擎后端（fallback）"""
    def __init__(self):
        super().__init__("rule_engine")
        self.ready = True  # 规则引擎始终可用
    
    @cached('llm_cache', ttl=3600)
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        # 简单规则回复
        if "你好" in prompt or "hi" in prompt.lower():
            return "你好！我是统一太乙系统，基于复合体理学与太极计算宇宙理论构建。"
        elif "?" in prompt or "？" in prompt or "什么" in prompt:
            return "这是一个很好的问题。从复合体理学的角度来看，需要从三视界（本体视界、方法视界、太乙视界）综合分析。"
        else:
            return "我正在思考这个问题。作为太乙系统，我会从复合体理学的角度给出分析。"


class LocalLLM:
    """统一LLM接口 - 多后端支持"""
    
    def __init__(self):
        self.backends = []
        self.active_backend = None
        self._init_backends()
    
    def _init_backends(self):
        """初始化所有可用的后端"""
        # 1. 尝试Ollama
        print("🔍 检查Ollama...")
        ollama = OllamaBackend()
        self.backends.append(ollama)
        if ollama.is_ready():
            print(f"   ✅ Ollama可用 (模型: {ollama.model})")
            self.active_backend = ollama
        else:
            print(f"   ⚠️ Ollama未运行或未拉取模型")
        
        # 2. 尝试DeepSeek API（优先）
        if DEEPSEEK_API_KEY:
            print("🔍 检查DeepSeek API...")
            deepseek = OnlineAPIBackend(DEEPSEEK_API_URL, DEEPSEEK_API_KEY, DEEPSEEK_MODEL)
            self.backends.append(deepseek)
            if not self.active_backend:
                self.active_backend = deepseek
                print(f"   ✅ DeepSeek API可用 (模型: {DEEPSEEK_MODEL})")
            else:
                print(f"   ✅ DeepSeek API可用 (作为fallback)")
        
        # 3. 尝试通用在线API
        api_key = os.environ.get("LLM_API_KEY", "")
        api_url = os.environ.get("LLM_API_URL", "")
        if api_key and api_url:
            print("🔍 检查在线API...")
            online = OnlineAPIBackend(api_url, api_key, "gpt-3.5-turbo")
            self.backends.append(online)
            if not self.active_backend:
                self.active_backend = online
                print("   ✅ 在线API可用")
            else:
                print("   ✅ 在线API可用 (作为fallback)")
        
        # 4. 规则引擎（始终可用）
        print("🔍 加载规则引擎...")
        rule = RuleEngineBackend()
        self.backends.append(rule)
        if not self.active_backend:
            self.active_backend = rule
            print("   ✅ 规则引擎已加载（LLM不可用）")
        else:
            print("   ✅ 规则引擎已加载（作为fallback）")
    
    def is_ready(self) -> bool:
        """检查是否有任何后端可用"""
        return any(b.is_ready() for b in self.backends)
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """生成回复"""
        if not self.active_backend:
            return "[错误：无可用LLM后端]"
        
        # 尝试活跃后端
        result = self.active_backend.generate(prompt, max_tokens, temperature)
        
        # 如果失败，尝试其他后端
        if result.startswith("[") and "错误" in result or "异常" in result:
            for backend in self.backends:
                if backend != self.active_backend and backend.is_ready():
                    result = backend.generate(prompt, max_tokens, temperature)
                    if not (result.startswith("[") and "错误" in result):
                        self.active_backend = backend
                        break
        
        return result
    
    def chat(self, message: str, history: list = None) -> str:
        """对话接口"""
        return self.generate(message)
    
    def status(self) -> Dict:
        """返回所有后端状态"""
        return {
            "active": self.active_backend.name if self.active_backend else None,
            "backends": [
                {"name": b.name, "ready": b.is_ready()}
                for b in self.backends
            ]
        }


# 全局LLM实例
_llm_instance = None


def get_llm() -> LocalLLM:
    """获取LLM单例"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LocalLLM()
    return _llm_instance


def test_llm():
    """测试LLM"""
    print("=" * 60)
    print("🧪 LLM后端测试")
    print("=" * 60)
    
    llm = get_llm()
    
    print("\n后端状态:")
    status = llm.status()
    for b in status["backends"]:
        print(f"   {b['name']}: {'✅ 可用' if b['ready'] else '❌ 不可用'}")
    print(f"\n当前活跃后端: {status['active']}")
    
    print("\n测试生成:")
    tests = ["你好", "什么是复合体理学？", "1+1等于几？"]
    for q in tests:
        print(f"\n问题: {q}")
        resp = llm.generate(q, max_tokens=100)
        print(f"回答: {resp[:200]}...")


if __name__ == "__main__":
    test_llm()
