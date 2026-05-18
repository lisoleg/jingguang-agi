#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM加载诊断脚本 - 详细排查ctransformers加载问题
"""

import sys
import os
import traceback

# 添加D盘Python路径
sys.path.insert(0, "D:/Apps/Python")

print("=" * 60)
print("🔮 LLM加载诊断工具")
print("=" * 60)

# 1. 检查CPU信息
print("\n📊 步骤1: 检查CPU信息...")
try:
    import platform
    print(f"   系统: {platform.system()} {platform.machine()}")
    print(f"   Python: {sys.version}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 尝试绕过cpuinfo检查
print("\n🛠️ 步骤2: 打补丁绕过cpuinfo检查...")
try:
    class FakeCpuInfo:
        @staticmethod
        def get_cpu_info():
            return {
                'brand': 'Intel Generic',
                'arch': 'X86_64',
                'count': 8,
                'flags': ['avx', 'avx2', 'fma', 'sse4_1', 'sse4_2']
            }
    
    # 在导入ctransformers之前替换模块
    sys.modules['cpuinfo'] = FakeCpuInfo()
    sys.modules['cpuinfo.cpuinfo'] = FakeCpuInfo()
    print("   ✅ cpuinfo模块已替换为FakeCpuInfo")
except Exception as e:
    print(f"   ❌ 补丁失败: {e}")

# 3. 检查ctransformers库文件
print("\n📂 步骤3: 检查ctransformers库文件...")
lib_base = "D:/Apps/Python/ctransformers/lib"
for subdir in ['avx2', 'avx', 'basic']:
    lib_dir = os.path.join(lib_base, subdir)
    if os.path.exists(lib_dir):
        files = os.listdir(lib_dir)
        print(f"   {subdir}: {files}")
    else:
        print(f"   {subdir}: 不存在")

# 4. 尝试导入ctransformers
print("\n📦 步骤4: 导入ctransformers...")
try:
    from ctransformers import LLM, Config
    print("   ✅ ctransformers导入成功")
    print(f"   LLM类: {LLM}")
    print(f"   Config类: {Config}")
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 5. 检查模型文件
print("\n📄 步骤5: 检查模型文件...")
model_path = os.path.abspath("models/qwen2.5-3b-instruct-q4_k_m.gguf")
print(f"   模型路径: {model_path}")
print(f"   文件存在: {os.path.exists(model_path)}")
if os.path.exists(model_path):
    size = os.path.getsize(model_path)
    print(f"   文件大小: {size / (1024**3):.2f} GB")
else:
    print("   ❌ 模型文件不存在！")
    sys.exit(1)

# 6. 尝试创建LLM实例
print("\n🚀 步骤6: 创建LLM实例...")
try:
    # 方法1: 使用默认配置
    print("   方法1: 使用AutoModelForCausalLM...")
    from ctransformers import AutoModelForCausalLM
    try:
        llm = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="qwen2",
            config=Config(context_length=4096, threads=4)
        )
        print("   ✅ AutoModelForCausalLM加载成功！")
    except Exception as e:
        print(f"   ❌ AutoModelForCausalLM失败: {e}")
        
        # 方法2: 直接使用LLM类
        print("   方法2: 直接使用LLM类...")
        try:
            llm = LLM(
                model_path=model_path,
                model_type="qwen2",
                config=Config(context_length=4096, threads=4)
            )
            print("   ✅ LLM类加载成功！")
        except Exception as e2:
            print(f"   ❌ LLM类失败: {e2}")
            traceback.print_exc()

except Exception as e:
    print(f"❌ 未预期的错误: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
