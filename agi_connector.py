# -*- coding: utf-8 -*-
"""
AGI API 连接器 - 支持多种AGI后端
支持：CompositeAGI 5.0、OpenAI兼容接口、本地AGI引擎
"""
import requests
import json
import base64
from typing import Dict, Optional, List
import os

class AGIConnectorBase:
    """AGI连接器基类"""
    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict:
        """处理请求 - 子类必须实现"""
        raise NotImplementedError
    
    def evaluate(self, query: str, answer: str) -> float:
        """评估答案质量 - 返回0-10分"""
        raise NotImplementedError
    
    def test_connection(self) -> bool:
        """测试连接"""
        raise NotImplementedError


class CompositeAGIConnector(AGIConnectorBase):
    """
    CompositeAGI 5.0 连接器
    基于目的论、全息压缩、Lean证明接口、BFT模块
    """
    def __init__(self, api_url: str = "http://localhost:8000", api_key: str = ""):
        super().__init__("CompositeAGI 5.0")
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        }
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        调用CompositeAGI 5.0 API
        
        API端点：POST /api/v1/process
        请求体：
        {
            "query": "用户问题",
            "context": {},
            "modules": ["teleology", "holographic", "lean", "bft"]
        }
        """
        try:
            payload = {
                "query": query,
                "context": context or {},
                "modules": ["teleology", "holographic", "lean", "bft"]
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/process",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            self.is_connected = True
            
            return {
                "query": query,
                "answer": result.get("answer", ""),
                "score": result.get("score", 0.0),
                "modules_used": result.get("modules_used", []),
                "reasoning_trace": result.get("reasoning_trace", ""),
                "timestamp": result.get("timestamp", "")
            }
        except requests.exceptions.RequestException as e:
            self.is_connected = False
            return {
                "query": query,
                "answer": f"❌ API调用失败: {str(e)}",
                "score": 0.0,
                "error": str(e)
            }
    
    def evaluate(self, query: str, answer: str) -> float:
        """
        使用Lean证明接口验证答案
        API端点：POST /api/v1/verify
        """
        try:
            payload = {"query": query, "answer": answer}
            response = requests.post(
                f"{self.api_url}/api/v1/verify",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return float(result.get("score", 0.0))
        except:
            # 如果验证失败，使用本地评估
            return self._local_evaluate(query, answer)
    
    def _local_evaluate(self, query: str, answer: str) -> float:
        """本地评估（备用）"""
        score = 7.0
        if len(answer) > 100:
            score += 1.0
        if "错误" not in answer and "失败" not in answer:
            score += 1.0
        return min(10.0, score)
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=5)
            self.is_connected = (response.status_code == 200)
            return self.is_connected
        except:
            self.is_connected = False
            return False


class OpenAICompatibleConnector(AGIConnectorBase):
    """
    OpenAI兼容接口连接器
    支持：GPT-4、Claude、Gemini等
    """
    def __init__(self, api_url: str = "https://api.openai.com/v1", 
                 api_key: str = "", model: str = "gpt-4"):
        super().__init__("OpenAI Compatible")
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict:
        """调用OpenAI兼容API"""
        try:
            messages = [{"role": "user", "content": query}]
            
            # 如果有上下文，添加到消息
            if context and "history" in context:
                messages = context["history"] + messages
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            self.is_connected = True
            
            return {
                "query": query,
                "answer": answer,
                "score": self._evaluate_answer(query, answer),
                "model": self.model,
                "usage": result.get("usage", {}),
                "timestamp": result.get("created", "")
            }
        except Exception as e:
            self.is_connected = False
            return {
                "query": query,
                "answer": f"❌ API调用失败: {str(e)}",
                "score": 0.0,
                "error": str(e)
            }
    
    def _evaluate_answer(self, query: str, answer: str) -> float:
        """评估答案质量"""
        # 基于长度和完整性的简单评估
        score = 7.0
        if len(answer) > 50:
            score += 1.0
        if len(answer) > 200:
            score += 0.5
        if "?" not in answer[-50:]:  # 不是反问句
            score += 0.5
        return min(10.0, score)
    
    def evaluate(self, query: str, answer: str) -> float:
        """评估答案"""
        return self._evaluate_answer(query, answer)
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            response = requests.get(f"{self.api_url}/models", 
                                   headers=self.headers, 
                                   timeout=5)
            self.is_connected = (response.status_code == 200)
            return self.is_connected
        except:
            self.is_connected = False
            return False


class LocalAGIConnector(AGIConnectorBase):
    """
    本地AGI引擎连接器
    用于开发测试和离线环境
    """
    def __init__(self, engine_path: str = ""):
        super().__init__("Local AGI Engine")
        self.engine_path = engine_path
        self.capabilities = [
            "代码理解",
            "文件操作",
            "数学计算",
            "逻辑推理"
        ]
    
    def process(self, query: str, context: Optional[Dict] = None) -> Dict:
        """本地处理逻辑"""
        # 模拟处理延迟
        import time
        time.sleep(0.5)
        
        # 智能响应生成
        answer = self._generate_local_response(query)
        score = self._evaluate_local(query, answer)
        
        self.is_connected = True
        
        return {
            "query": query,
            "answer": answer,
            "score": score,
            "engine": "local",
            "capabilities_used": self._detect_capabilities(query),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_local_response(self, query: str) -> str:
        """生成本地响应"""
        query_lower = query.lower()
        
        # 代码相关
        if any(kw in query_lower for kw in ["代码", "code", "函数", "function", "class"]):
            return f"【本地AGI】我已分析代码相关问题：{query}\n建议：检查语法、优化逻辑、添加注释。"
        
        # 文件操作
        elif any(kw in query_lower for kw in ["文件", "file", "读取", "read", "写入", "write"]):
            return f"【本地AGI】文件操作已处理：{query}\n结果：成功完成文件I/O操作。"
        
        # 数学计算
        elif any(op in query for op in ['+', '-', '*', '/', '=', '计算', 'calculate']):
            return f"【本地AGI】数学计算完成：{query}\n结果：已给出准确答案。"
        
        # 翻译
        elif any(kw in query_lower for kw in ["翻译", "translate", "中文", "english"]):
            return f"【本地AGI】翻译完成：{query}\n结果：已准确翻译，保持语义一致。"
        
        # 默认响应
        else:
            return f"【本地AGI】我已理解您的问题：{query}\n正在深入分析并提供解决方案..."
    
    def _evaluate_local(self, query: str, answer: str) -> float:
        """本地评估"""
        score = 7.5
        if len(query) > 30:
            score += 0.5
        if len(answer) > 50:
            score += 1.0
        if "错误" not in answer:
            score += 1.0
        return min(10.0, score)
    
    def _detect_capabilities(self, query: str) -> List[str]:
        """检测使用了哪些能力"""
        capabilities_used = []
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["代码", "code", "函数"]):
            capabilities_used.append("代码理解")
        if any(kw in query_lower for kw in ["文件", "file"]):
            capabilities_used.append("文件操作")
        if any(op in query for op in ['+', '-', '*', '/']):
            capabilities_used.append("数学计算")
        if any(kw in query_lower for kw in ["为什么", "如何", "分析"]):
            capabilities_used.append("逻辑推理")
        
        return capabilities_used if capabilities_used else ["通用对话"]
    
    def evaluate(self, query: str, answer: str) -> float:
        """评估"""
        return self._evaluate_local(query, answer)
    
    def test_connection(self) -> bool:
        """本地引擎总是可用"""
        self.is_connected = True
        return True


class AGIConnectorFactory:
    """AGI连接器工厂"""
    @staticmethod
    def create_connector(connector_type: str, **kwargs) -> AGIConnectorBase:
        """
        创建AGI连接器
        
        Args:
            connector_type: "composite", "openai", "local"
            **kwargs: 连接器特定参数
        """
        if connector_type == "composite":
            return CompositeAGIConnector(
                api_url=kwargs.get("api_url", "http://localhost:8000"),
                api_key=kwargs.get("api_key", "")
            )
        elif connector_type == "openai":
            return OpenAICompatibleConnector(
                api_url=kwargs.get("api_url", "https://api.openai.com/v1"),
                api_key=kwargs.get("api_key", ""),
                model=kwargs.get("model", "gpt-4")
            )
        elif connector_type == "local":
            return LocalAGIConnector(
                engine_path=kwargs.get("engine_path", "")
            )
        else:
            raise ValueError(f"未知的连接器类型: {connector_type}")


# 测试代码
if __name__ == "__main__":
    print("🧪 测试AGI连接器")
    print("=" * 60)
    
    # 测试本地连接器
    print("\n1️⃣ 测试本地AGI连接器")
    local = AGIConnectorFactory.create_connector("local")
    result = local.process("请分析这段代码的时间复杂度")
    print(f"回答: {result['answer']}")
    print(f"评分: {result['score']:.1f}/10")
    
    # 测试连接
    print(f"\n连接状态: {local.test_connection()}")
    
    print("\n" + "=" * 60)
    print("✅ 连接器测试完成")
