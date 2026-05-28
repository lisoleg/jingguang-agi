#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试升级后的CompositeAGI_V2系统（包含IGCTR v2.3）
"""

print("=" * 60)
print("测试升级后的CompositeAGI_V2系统")
print("=" * 60)

# 导入升级后的系统
try:
    from CompositeAGI_V2 import CompositeAGI_V2
    print("\n✓ CompositeAGI_V2 导入成功")
except ImportError as e:
    print(f"\n✗ CompositeAGI_V2 导入失败: {e}")
    exit(1)

# 创建系统实例
print("\n正在初始化CompositeAGI_V2系统...")
agi = CompositeAGI_V2()

# 测试查询
test_queries = [
    "什么是波函数坍缩？",
    "暗物质存在吗？",
    "如何实现AGI？"
]

print("\n" + "=" * 60)
print("开始测试查询处理...")
print("=" * 60)

for i, query in enumerate(test_queries, 1):
    print(f"\n[测试 {i}/{len(test_queries)}]")
    result = agi.process_query(query)
    
    print(f"查询: {query}")
    
    # 检查IGCTR v2.3结果
    if 'igctr_v23' in result.get('module_results', {}):
        igctr_v23 = result['module_results']['igctr_v23']
        print(f"  IGCTR v2.3版本: {igctr_v23.get('version', 'N/A')}")
        print(f"  梯度流收敛: {igctr_v23.get('gradient_flow_converged', False)}")
        
        three_horizons = igctr_v23.get('three_horizons', {})
        if 'micro' in three_horizons:
            print(f"  三视界（微）: {three_horizons['micro']['focus']}")
    
    print(f"  综合回答生成: {'成功' if result.get('synthesized_answer') else '失败'}")
    print("-" * 60)

# 打印系统运行时间
runtime = (agi.start_time - agi.start_time).total_seconds() if hasattr(agi, 'start_time') else 0
print(f"\n系统运行时间: {runtime:.3f}秒")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
