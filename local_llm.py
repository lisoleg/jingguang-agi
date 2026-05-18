#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM集成模块 - 多后端支持
支持：LM Studio（本地）、OpenRouter（免费）、Ollama、规则引擎fallback

后端优先级：LM Studio > OpenRouter > Ollama > 规则引擎
"""

import os
import sys
import json
import requests
import concurrent.futures
from typing import Optional, Dict, Any, List

# LM Studio配置（本地优先）
LM_STUDIO_API_BASE = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen2.5-3b-instruct"  # 默认模型

# OpenRouter配置（免费LLM API）
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "google/gemini-flash-2.0:free"  # 免费模型

# DeepSeek配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"  # 可选: deepseek-reasoner

# Ollama配置
OLLAMA_API_BASE = "http://localhost:11434/api"
OLLAMA_MODEL = "qwen2:3b"

# 规则引擎回复模板
RULE_REPLIES = {
    "greeting": "你好！我是统一太乙系统，基于复合体理学与太极计算宇宙理论构建。",
    "question": "这是一个很好的问题。从复合体理学的角度来看，需要从三视界（本体视界、方法视界、太乙视界）综合分析。",
    "default": "我正在思考这个问题。作为太乙系统，我会从复合体理学的角度给出分析。"
}


class LLMBackend:
    """LLM后端基类"""
    def __init__(self, name: str):
        self.name = name
        self.ready = False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        raise NotImplementedError
    
    def is_ready(self) -> bool:
        return self.ready


class LMStudioBackend(LLMBackend):
    """LM Studio后端（本地优先）"""
    def __init__(self, api_base: str = LM_STUDIO_API_BASE, 
                 model: str = LM_STUDIO_MODEL):
        super().__init__("lm_studio")
        self.api_base = api_base.rstrip('/')
        self.model = model
        self.chat_endpoint = f"{self.api_base}/chat/completions"
        self.models_endpoint = f"{self.api_base}/models"
        self._check_ready()
    
    def _check_ready(self):
        """检查LM Studio是否运行"""
        try:
            resp = requests.get(self.models_endpoint, timeout=2)
            if resp.status_code == 200:
                self.ready = True
                print(f"   ✅ LM Studio可用 (模型: {self.model})")
            else:
                self.ready = False
                print(f"   ⚠️ LM Studio API返回错误: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.ready = False
            print(f"   ⚠️ LM Studio未运行 (API: {self.api_base})")
            print(f"      请启动LM Studio并启用Local Server")
        except Exception as e:
            self.ready = False
            print(f"   ❌ LM Studio检查失败: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7, 
                system_prompt: Optional[str] = None) -> str:
        """生成回复"""
        if not self.ready:
            return "[LM Studio未运行，请启动LM Studio]"
        
        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 构建请求
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # 发送请求
            resp = requests.post(self.chat_endpoint, json=data, timeout=120)
            
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"[LM Studio错误: {resp.status_code} {resp.text[:200]}]"
        
        except Exception as e:
            return f"[LM Studio异常: {e}]"
    
    def chat(self, message: str, history: Optional[List[Dict]] = None,
             system_prompt: Optional[str] = None) -> str:
        """对话接口（支持历史）"""
        if not self.ready:
            return self.generate(message, system_prompt=system_prompt)
        
        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史消息
            if history:
                messages.extend(history)
            
            # 添加当前消息
            messages.append({"role": "user", "content": message})
            
            # 构建请求
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.7,
                "stream": False
            }
            
            # 发送请求
            resp = requests.post(self.chat_endpoint, json=data, timeout=120)
            
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"[LM Studio错误: {resp.status_code} {resp.text[:200]}]"
        
        except Exception as e:
            return f"[LM Studio异常: {e}]"
    
    def chat_with_image(self, content: str, image_base64: str = None,
                        history: Optional[List[Dict]] = None,
                        system_prompt: Optional[str] = None,
                        max_tokens: int = 51200,
                        temperature: float = 0.7) -> str:
        """多模态对话接口（支持图片输入）
        
        Args:
            content: 文本内容
            image_base64: 图片base64编码（可选）
            history: 对话历史
            system_prompt: 系统提示
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            LLM生成的回复
        """
        if not self.ready:
            return "[LM Studio未运行，请启动LM Studio]"
        
        # 检查是否支持多模态
        if image_base64:
            # 需要多模态模型（如Qwen2-VL、llava等）
            # 检查模型名称
            model_lower = self.model.lower()
            multimodal_models = ['qwen2-vl', 'qwen-vl', 'llava', 'moondream', 'minicpm-v']
            is_multimodal = any(m in model_lower for m in multimodal_models)
            
            if not is_multimodal:
                return "[当前模型不支持图片输入，请使用多模态模型如Qwen2-VL]"
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史消息
            if history:
                messages.extend(history)
            
            # 构建用户消息（支持图片）
            if image_base64:
                # 多模态格式
                user_content = [
                    {"type": "text", "text": content}
                ]
                # 判断图片格式
                if "data:image/" in image_base64[:50]:
                    user_content.append({"type": "image_url", "image_url": {"url": image_base64}})
                else:
                    user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}})
                messages.append({"role": "user", "content": user_content})
            else:
                messages.append({"role": "user", "content": content})
            
            # 构建请求
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # 发送请求
            resp = requests.post(self.chat_endpoint, json=data, timeout=180)
            
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"[LM Studio错误: {resp.status_code} {resp.text[:200]}]"
        
        except Exception as e:
            return f"[LM Studio多模态异常: {e}]"


class OpenRouterBackend(LLMBackend):
    """OpenRouter后端（免费LLM API）"""
    def __init__(self):
        super().__init__("openrouter")
        self.api_url = OPENROUTER_API_URL
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.ready = bool(self.api_key)
        if self.ready:
            print(f"   ✅ OpenRouter可用 (模型: {self.model})")
        else:
            print(f"   ⚠️ OpenRouter未配置API_KEY")
            print(f"      获取免费key: https://openrouter.ai/keys")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        if not self.ready:
            return "[OpenRouter未配置API_KEY]"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://workbuddy.local",
                "X-Title": "Taiyi-AGI-System"
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
            return f"[OpenRouter错误: {resp.status_code} {resp.text[:200]}]"
        except Exception as e:
            return f"[OpenRouter异常: {e}]"
    
    def chat_with_image(self, content: str, image_base64: str = None,
                        history: Optional[List[Dict]] = None,
                        system_prompt: Optional[str] = None,
                        max_tokens: int = 51200,
                        temperature: float = 0.7) -> str:
        """OpenRouter多模态对话接口（支持图片输入）"""
        if not self.ready:
            return "[OpenRouter未配置API_KEY]"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://workbuddy.local",
                "X-Title": "Taiyi-AGI-System"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if history:
                messages.extend(history)
            
            # 构建用户消息
            if image_base64:
                # 多模态格式
                user_content = [
                    {"type": "text", "text": content}
                ]
                if "data:image/" in image_base64[:50]:
                    user_content.append({"type": "image_url", "image_url": {"url": image_base64}})
                else:
                    user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}})
                messages.append({"role": "user", "content": user_content})
            else:
                messages.append({"role": "user", "content": content})
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[OpenRouter多模态错误: {resp.status_code} {resp.text[:200]}]"
        except Exception as e:
            return f"[OpenRouter多模态异常: {e}]"


class DeepSeekBackend(LLMBackend):
    """DeepSeek API后端（OpenAI兼容）"""
    def __init__(self):
        super().__init__("deepseek")
        self.api_url = DEEPSEEK_API_URL
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.ready = bool(self.api_key)
        if self.ready:
            print(f"   ✅ DeepSeek可用 (模型: {self.model})")
        else:
            print(f"   ⚠️ DeepSeek未配置API_KEY")
            print(f"      请设置环境变量: DEEPSEEK_API_KEY")
            print(f"      获取key: https://platform.deepseek.com/")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        if not self.ready:
            return "[DeepSeek未配置API_KEY]"
        
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
            return f"[DeepSeek错误: {resp.status_code} {resp.text[:200]}]"
        except Exception as e:
            return f"[DeepSeek异常: {e}]"
    
    def chat_with_image(self, content: str, image_base64: str = None,
                        history: Optional[List[Dict]] = None,
                        system_prompt: Optional[str] = None,
                        max_tokens: int = 51200,
                        temperature: float = 0.7) -> str:
        """DeepSeek对话接口（暂不支持图片，fallback到文本）"""
        if not self.ready:
            return "[DeepSeek未配置API_KEY]"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if history:
                messages.extend(history)
            
            # DeepSeek暂不支持多模态，如果有图片则提示
            if image_base64:
                content = content + "\n[注意：DeepSeek API暂不支持图片输入，已忽略图片]"
            
            messages.append({"role": "user", "content": content})
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[DeepSeek对话错误: {resp.status_code} {resp.text[:200]}]"
        except Exception as e:
            return f"[DeepSeek对话异常: {e}]"


class OllamaBackend(LLMBackend):
    """Ollama后端"""
    def __init__(self, model: str = OLLAMA_MODEL):
        super().__init__("ollama")
        self.model = model
        self.api_base = OLLAMA_API_BASE
        self._check_ready()
    
    def _check_ready(self):
        try:
            resp = requests.get(f"{self.api_base}/tags", timeout=2)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if any(self.model in m for m in models):
                    self.ready = True
                    print(f"   ✅ Ollama可用 (模型: {self.model})")
                else:
                    print(f"   ⚠️ Ollama已运行但未拉取模型 {self.model}")
                    print(f"      请运行: ollama pull {self.model}")
            else:
                self.ready = False
        except:
            self.ready = False
            print(f"   ⚠️ Ollama未运行 (API: {self.api_base})")
    
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
            return f"[Ollama错误: {resp.text[:200]}]"
        except Exception as e:
            return f"[Ollama异常: {e}]"
    
    def chat_with_image(self, content: str, image_base64: str = None,
                        history: Optional[List[Dict]] = None,
                        system_prompt: Optional[str] = None,
                        max_tokens: int = 51200,
                        temperature: float = 0.7) -> str:
        """Ollama多模态对话接口（支持图片输入，需要多模态模型如llava）"""
        if not self.ready:
            return "[Ollama未运行]"
        
        if image_base64:
            # Ollama多模态需要llava等模型
            model_lower = self.model.lower()
            if 'llava' not in model_lower and 'moondream' not in model_lower:
                return "[Ollama当前模型不支持图片，请使用llava模型]"
            
            try:
                # Ollama多模态API
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                if history:
                    messages.extend(history)
                
                # 图片数据
                import base64
                img_bytes = base64.b64decode(image_base64)
                import base64 as b64
                
                user_content = [
                    {"type": "text", "text": content}
                ]
                user_content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                })
                messages.append({"role": "user", "content": user_content})
                
                resp = requests.post(
                    f"{self.api_base}/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": temperature
                        }
                    },
                    timeout=120
                )
                if resp.status_code == 200:
                    return resp.json().get("message", {}).get("content", "")
                return f"[Ollama多模态错误: {resp.text[:200]}]"
            except Exception as e:
                return f"[Ollama多模态异常: {e}]"
        
        # 无图片时使用标准chat
        return self.generate(content, max_tokens, temperature)


class RuleEngineBackend(LLMBackend):
    """规则引擎后端（fallback）"""
    def __init__(self):
        super().__init__("rule_engine")
        self.ready = True
        self.replies = RULE_REPLIES
        print(f"   ✅ 规则引擎已加载（LLM不可用时的fallback）")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["你好", "hi", "hello", "介绍"]):
            return self.replies["greeting"]
        elif any(w in prompt_lower for w in ["?", "？", "什么", "怎么", "为什么"]):
            return self.replies["question"]
        else:
            return self.replies["default"]


class LocalLLM:
    """统一LLM接口 - 多后端支持"""
    
    def __init__(self):
        self.backends = []
        self.active_backend = None
        self._init_backends()
    
    def _init_backends(self):
        """初始化所有可用的后端（优先级：DeepSeek > LM Studio > OpenRouter > Ollama > 规则引擎）"""
        print("🔍 检查LLM后端...")
        
        # 0. DeepSeek API（最高优先级，在线API）
        deepseek = DeepSeekBackend()
        self.backends.append(deepseek)
        if deepseek.is_ready() and self.active_backend is None:
            self.active_backend = deepseek
        
        # 1. LM Studio（本地，次优先）
        lm_studio = LMStudioBackend()  # 使用本文件定义的类
        self.backends.append(lm_studio)
        if lm_studio.is_ready() and self.active_backend is None:
            self.active_backend = lm_studio
        
        # 1. OpenRouter（免费LLM API）
        openrouter = OpenRouterBackend()
        self.backends.append(openrouter)
        if openrouter.is_ready() and self.active_backend is None:
            self.active_backend = openrouter
        
        # 2. Ollama
        ollama = OllamaBackend()
        self.backends.append(ollama)
        if ollama.is_ready() and self.active_backend is None:
            self.active_backend = ollama
        
        # 3. 规则引擎（始终可用）
        rule = RuleEngineBackend()
        self.backends.append(rule)
        if self.active_backend is None:
            self.active_backend = rule
        
        print(f"\n🚀 当前活跃后端: {self.active_backend.name}")
    
    def is_ready(self) -> bool:
        """检查是否有任何后端可用"""
        return any(b.is_ready() for b in self.backends)
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """生成回复（带30秒超时保护）"""
        if not self.active_backend:
            return "[错误：无可用LLM后端]"
        
        # 尝试活跃后端（带30秒超时）
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                self.active_backend.generate, prompt, max_tokens, temperature
            )
            try:
                result = future.result(timeout=30)
            except concurrent.futures.TimeoutError:
                result = "[错误：LLM调用超时（30秒）]"
        
        # 如果失败，尝试其他后端
        if result.startswith("[") and ("错误" in result or "异常" in result):
            for backend in self.backends:
                if backend != self.active_backend and backend.is_ready():
                    result = backend.generate(prompt, max_tokens, temperature)
                    if not (result.startswith("[") and ("错误" in result or "异常" in result)):
                        self.active_backend = backend
                        print(f"   ℹ️ 已切换到后端: {backend.name}")
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
        status_icon = '✅' if b['ready'] else '❌'
        print(f"   {status_icon} {b['name']}")
    print(f"\n当前活跃后端: {status['active']}")
    
    print("\n测试生成:")
    tests = ["你好", "什么是复合体理学？", "1+1等于几？"]
    for q in tests:
        print(f"\n问题: {q}")
        resp = llm.generate(q, max_tokens=100)
        print(f"回答: {resp[:200]}")


if __name__ == "__main__":
    test_llm()
