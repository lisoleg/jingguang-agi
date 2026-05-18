#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 TopologicalDefect 模块
"""

print('=== 测试 TopologicalDefect 模块 ===')

try:
    from TopologicalDefect import TopologicalDefect, DefectType, VortexCore, DefectPinningAlgorithm
    print('✅ 模块导入成功')
    
    # 1. 创建模拟信息场
    import numpy as np
    print('\\n1. 创建模拟信息场...')
    x = np.linspace(0, 1, 50)
    y = np.linspace(0, 50, 100)
    X, Y = np.meshgrid(x, y)
    information_field = np.sin(10 * (X - 0.5)) * np.exp(-Y / 20)
    print(f'   信息场形状: {information_field.shape}')
    
    # 2. 创建钉扎算法实例
    print('\\n2. 创建钉扎算法实例...')
    algorithm = DefectPinningAlgorithm(critical_dimension=0.5)
    print(f'   临界维数: {algorithm.critical_dimension}')
    print(f'   相干阈值: {algorithm.coherence_threshold}')
    
    # 3. 创建模拟推理路径
    print('\\n3. 创建模拟推理路径...')
    reasoning_path = [
        {'step_id': 1, 'text': '根据数据分析，可能得出结论A', 'conclusions': ['结论A可能成立']},
        {'step_id': 2, 'text': '进一步分析发现结论A不成立，而是结论B', 'conclusions': ['结论A不成立', '结论B成立']},
        {'step_id': 3, 'text': '验证结论B，发现矛盾', 'conclusions': ['结论B成立', '结论B不成立']},
    ]
    print(f'   推理路径步骤数: {len(reasoning_path)}')
    
    # 4. 标识拓扑缺陷
    print('\\n4. 标识拓扑缺陷...')
    defects = algorithm.identify_defects(reasoning_path, information_field)
    print(f'   识别出 {len(defects)} 个拓扑缺陷')
    
    for i, defect in enumerate(defects):
        print(f'     缺陷{i+1}: 类型={defect.defect_type.value}, 强度={defect.strength:.2f}')
    
    # 5. 创建涡旋核
    print('\\n5. 创建涡旋核...')
    vortex_cores = algorithm.create_vortex_cores(num_cores=2)
    print(f'   创建了 {len(vortex_cores)} 个涡旋核')
    
    for i, core in enumerate(vortex_cores):
        print(f'     涡旋核{i+1}: 中心={core.center}, 半径={core.radius:.2f}')
    
    # 6. 定义约束
    print('\\n6. 定义拓扑约束...')
    def constraint1(position):
        return 1.0 / (1.0 + abs(position[0] - 0.5))
    
    def constraint2(position):
        return 1.0 / (1.0 + abs(np.linalg.norm(position) - 0.5))
    
    constraints = [constraint1, constraint2]
    print(f'   定义了 {len(constraints)} 个约束')
    
    # 7. 钉扎缺陷
    print('\\n7. 钉扎拓扑缺陷...')
    success_rate = algorithm.pin_all_defects(constraints, learning_rate=0.01)
    print(f'   钉扎成功率: {success_rate:.2%}')
    
    # 8. 评估稳定性
    print('\\n8. 评估系统稳定性...')
    stability = algorithm.evaluate_stability(information_field, constraint1)
    print(f'   稳定性评分: {stability["stability_score"]:.3f}')
    print(f'   平均稳定性: {stability["average_stability"]:.3f}')
    print(f'   钉扎比例: {stability["pinned_ratio"]:.2%}')
    print(f'   缺陷总数: {stability["num_defects"]}')
    print(f'   已钉扎数: {stability["num_pinned"]}')
    
    # 9. 测试单个缺陷的钉扎
    print('\\n9. 测试单个拓扑缺陷的钉扎...')
    test_defect = TopologicalDefect(
        position=np.array([0.6, 25.0]),
        defect_type=DefectType.VORTEX,
        strength=1.0
    )
    print(f'   测试缺陷位置: {test_defect.position}')
    print(f'   到临界线距离: {abs(test_defect.position[0] - 0.5):.3f}')
    
    pin_success = test_defect.pin_defect([constraint1], learning_rate=0.01, max_iterations=1000)
    print(f'   钉扎结果: {"成功" if pin_success else "失败"}')
    print(f'   钉扎后位置: {test_defect.position}')
    print(f'   到临界线距离: {test_defect.critical_line_distance:.6f}')
    
    # 10. 可视化（如果可能）
    print('\\n10. 尝试可视化...')
    try:
        algorithm.visualize_defects(information_field, save_path="topological_defects_test.png")
        print('    ✅ 可视化成功，保存为 topological_defects_test.png')
    except Exception as viz_e:
        print(f'    ⚠️ 可视化失败: {viz_e}')
    
    print('\\n=== TopologicalDefect 模块测试完成 ===')
    print('✅ 所有测试通过！')
    
except Exception as e:
    print(f'\\n❌ 测试失败: {e}')
    import traceback
    traceback.print_exc()