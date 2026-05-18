#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LM Studio 后端集成
支持LM Studio本地运行的模型（OpenAI兼容API）

LM Studio默认运行在: http://localhost:1234
API格式兼容OpenAI API
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List


# LM Studio 配置
LM_STUDIO_API_BASE = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen2.5-3b-instruct"  # 默认模型名称


class LMStudioBackend:
    """
    LM Studio 后端
    
    支持LM Studio运行的任何GGUF模型
    默认API端点：http://localhost:1234/v1
    """
    
    def __init__(self, api_base: str = LM_STUDIO_API_BASE, 
                 model: str = LM_STUDIO_MODEL):
        self.api_base = api_base.rstrip('/')
        self.model = model
        self.ready = False
        self.chat_endpoint = f"{self.api_base}/chat/completions"
        self.models_endpoint = f"{self.api_base}/models"
        
        # 检查LM Studio是否运行
        self._check_ready()
    
    def _check_ready(self):
        """检查LM Studio是否运行"""
        try:
            resp = requests.get(self.models_endpoint, timeout=2)
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                model_names = [m.get("id", "") for m in models]
                
                # 检查目标模型是否可用
                if any(self.model in m for m in model_names):
                    self.ready = True
                    print(f"   ✅ LM Studio可用 (模型: {self.model})")
                else:
                    self.ready = True  # API可用，但模型可能名称不同
                    print(f"   ⚠️ LM Studio已运行，但未找到模型 '{self.model}'")
                    print(f"      可用模型: {model_names[:3]}...")
            else:
                self.ready = False
                print(f"   ❌ LM Studio API返回错误: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.ready = False
            print(f"   ⚠️ LM Studio未运行 (API: {self.api_base})")
            print(f"      请启动LM Studio并加载模型")
        except Exception as e:
            self.ready = False
            print(f"   ❌ LM Studio检查失败: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 512, 
               temperature: float = 0.7, system_prompt: Optional[str] = None) -> str:
        """
        生成回复
        
        Args:
            prompt: 用户输入
            max_tokens: 最大生成token数
            temperature: 温度参数
            system_prompt: 系统提示（可选）
            
        Returns:
            生成的文本
        """
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
            resp = requests.post(
                self.chat_endpoint,
                json=data,
                timeout=120  # LM Studio本地推理可能需要更长时间
            )
            
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"[LM Studio错误: {resp.status_code} {resp.text[:200]}]"
        
        except Exception as e:
            return f"[LM Studio异常: {e}]"
    
    def chat(self, message: str, history: Optional[List[Dict]] = None,
             system_prompt: Optional[str] = None) -> str:
        """
        对话接口（支持历史）
        
        Args:
            message: 当前消息
            history: 历史消息列表 [{"role": "user/assistant", "content": "..."}]
            system_prompt: 系统提示
            
        Returns:
            生成的回复
        """
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
            resp = requests.post(
                self.chat_endpoint,
                json=data,
                timeout=120
            )
            
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"[LM Studio错误: {resp.status_code} {resp.text[:200]}]"
        
        except Exception as e:
            return f"[LM Studio异常: {e}]"
    
    def chat_with_image_stream(self, content: str, image_base64: str = None,
                             history: list = None,
                             system_prompt: str = None,
                             max_tokens: int = 512, temperature: float = 0.7,
                             callback: callable = None) -> str:
        """
        流式聊天接口（支持回调逐字输出）
        LM Studio SSE 格式：每行 "data: {...}"，结束为 "data: [DONE]"
        """
        if not self.ready:
            return "[LM Studio未运行，请启动LM Studio]"

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": content})

            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }

            resp = requests.post(
                self.chat_endpoint,
                json=data,
                stream=True,
                timeout=600
            )

            full_text = []
            for line in resp.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8')
                if not line.startswith('data: '):
                    continue
                data_str = line[6:].strip()
                if data_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        if callback:
                            callback(token)
                        full_text.append(token)
                except Exception:
                    pass

            return ''.join(full_text)
        except Exception as e:
            return f"[LM Studio流式异常: {e}]"

    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self.ready
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        try:
            resp = requests.get(self.models_endpoint, timeout=2)
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                for m in models:
                    if self.model in m.get("id", ""):
                        return m
            return {}
        except:
            return {}


# ===== 测试代码 =====

def test_lm_studio():
    """测试LM Studio后端"""
    print("=" * 60)
    print("🧪 LM Studio 后端测试")
    print("=" * 60)
    
    # 1. 创建后端
    backend = LMStudioBackend()
    
    if not backend.is_ready():
        print("\n⚠️ LM Studio未运行")
        print("   请：")
        print("   1. 启动LM Studio")
        print("   2. 加载模型（如 qwen2.5-3b-instruct）")
        print("   3. 在LM Studio中启用'Local Server'")
        return
    
    # 2. 测试生成
    print("\n测试生成:")
    test_prompts = [
        "你好，请介绍一下你自己。",
        "什么是复合体理学？",
        "1+1等于几？"
    ]
    
    for prompt in test_prompts:
        print(f"\n问题: {prompt}")
        resp = backend.generate(prompt, max_tokens=100)
        print(f"回答: {resp[:200]}")
    
    # 3. 测试对话
    print("\n测试对话（带历史）:")
    history = []
    conversation = [
        "你好！",
        "请问复合体理学的核心思想是什么？",
        "能否详细解释一下Ftel算子？"
    ]
    
    for msg in conversation:
        print(f"\n用户: {msg}")
        resp = backend.chat(msg, history=history)
        print(f"助手: {resp[:150]}")
        
        # 更新历史
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": resp})
    
    print("\n✅ LM Studio测试完成")


if __name__ == "__main__":
    test_lm_studio()
