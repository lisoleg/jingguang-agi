#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一太乙系统 - 启动脚本
自动检测并配置LLM后端，启动Flask服务
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

# Fix Windows console encoding for emoji support
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def safe_print(*args, **kwargs):
    """Print that handles emoji on Windows GBK console."""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # fallback: remove emoji
        import re
        msg = " ".join(str(a) for a in args)
        msg = msg.encode('ascii', errors='ignore').decode('ascii')
        print(msg, **{k:v for k,v in kwargs.items() if k != 'file'})

print("=" * 60)
print("🔮 统一太乙系统 - AGI问答系统")
print("=" * 60)

# 1. 检查LLM后端
print("\n🔍 步骤1: 检查LLM后端...")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.local_llm import get_llm, LocalLLM, OpenRouterBackend, OllamaBackend

llm = get_llm()
status = llm.status()

print(f"\n后端状态:")
for b in status["backends"]:
    icon = "✅" if b["ready"] else "❌"
    print(f"  {icon} {b['name']}")

active = status["active"]
print(f"\n🚀 当前活跃后端: {active}")

if active == "rule_engine":
    print("\n⚠️  当前使用规则引擎（LLM未配置）")
    print("   要启用真正的LLM能力，请选择以下方案之一：")
    print("")
    print("   【方案1】使用OpenRouter免费LLM（推荐）")
    url = "http://localhost:" + str(5000)
#     print("   访问: localhost:" + str(5000))
    print("      2. 设置环境变量：")
    print("         set OPENROUTER_API_KEY=sk-or-v1-xxxxx")
    print("      3. 重新运行此脚本")
    print("")
    print("   【方案2】使用Ollama（本地运行）")
    print("      1. 下载安装 Ollama: https://ollama.com/download")
    print("      2. 运行: ollama pull qwen2:3b")
    print("      3. 重新运行此脚本")
    print("")

# 2. 启动Flask服务
print("\n🚀 步骤2: 启动Flask服务...")
# print("   访问地址: <ADDRESS_REMOVED>
# print("   按 Ctrl+C 停止服务\n")

try:
    from app import app
    app.run(host="0.0.0.0", port=5000, debug=False)
except KeyboardInterrupt:
    print("\n\n👋 太乙系统已停止")
except Exception as e:
    print(f"\n❌ 启动失败: {e}")
    sys.exit(1)
