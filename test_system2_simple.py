#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试System 2推理功能"""

from system2_reasoning import System2Reasoning

# 创建System 2
system2 = System2Reasoning('Test')

# 测试案例
test_cases = [
    (['P implies Q', 'P'], 'Q', '格式: implies'),
    (['P → Q', 'P'], 'Q', '格式: →'),
]

for premises, goal, desc in test_cases:
    print(f"\n测试: {desc}")
    print(f"  前提: {premises}")
    print(f"  目标: {goal}")
    
    result = system2.reason(premises, goal)
    
    print(f"  成功: {result['success']}")
    if result['conclusion']:
        print(f"  结论: {result['conclusion']}")
    print(f"  推理步骤数: {len(result['inference_chain'])}")
    
    if result['inference_chain']:
        print(f"  推理链:")
        for step in result['inference_chain'][:2]:  # 只显示前2步
            print(f"    {step}")
