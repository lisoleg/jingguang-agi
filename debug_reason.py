#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试 neuro_symbolic_reasoner 调用"""
import sys
sys.path.insert(0, '.')

print("step1: 开始导入", flush=True)
from neuro_symbolic_reasoner import NeuroSymbolicReasoner
print("step2: 导入成功", flush=True)

r = NeuroSymbolicReasoner()
print("step3: 初始化完成", flush=True)

print("step4: 开始调用reason...", flush=True)
try:
    result = r.reason("2+2等于多少？")
    print(f"step5: 调用完成, success={result.success}", flush=True)
    print(f"answer: {result.answer[:100] if result.answer else None}", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
