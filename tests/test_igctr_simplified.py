#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 IGCTR_UnifiedField 模块（不依赖numpy版本）
"""

print('=== 测试 IGCTR_UnifiedField 模块（简化版） ===')

try:
    from IGCTR_UnifiedField import IGCTR_UnifiedField, InformationPole, GeometryPole, ConsciousnessPole
    print('✅ 模块导入成功')
    
    # 1. 创建IGCTR框架实例
    print('\n1. 初始化IGCTR统一场框架...')
    igctr = IGCTR_UnifiedField(resonance_threshold=0.7)
    print(f'   共振阈值: {igctr.resonance_threshold}')
    print(f'   自适应率: {igctr.adaptation_rate}')
    print('   ✅ IGCTR框架创建成功')
    
    # 2. 准备输入数据
    print('\n2. 准备输入数据...')
    test_input = "这是一个测试输入，用于验证三元共振架构。"
    print(f'   输入数据: "{test_input[:30]}..."')
    
    # 3. 执行共振优化
    print('\n3. 执行三元共振优化...')
    result = igctr.resonance_optimization(test_input)
    
    # 4. 输出结果
    print('\n4. 共振优化结果：')
    print(f'   共振信号强度: {result["resonance_signal"].signal_strength:.3f}')
    print(f'   相位相干性: {result["resonance_signal"].phase_coherence:.3f}')
    print(f'   共振频率: {result["resonance_signal"].frequency:.3f}')
    print(f'   时间戳: {result["resonance_signal"].timestamp:.3f}')
    
    # 5. 检查各极输出
    print('\n5. 各极输出检查：')
    print(f'   信息极输出类型: {result["I_output"]["pole_type"]}')
    print(f'   几何极输出类型: {result["G_output"]["pole_type"]}')
    print(f'   意识极输出类型: {result["C_output"]["pole_type"]}')
    
    # 6. 评估统一场
    print('\n6. 评估统一场论实现效果...')
    evaluation = igctr.evaluate_field_unification()
    
    print(f'   统一场评分: {evaluation["score"]:.3f}')
    print(f'   等级: {evaluation["grade"]}')
    print(f'   平均共振强度: {evaluation["avg_resonance"]:.3f}')
    print(f'   平均相位相干性: {evaluation["avg_coherence"]:.3f}')
    print(f'   统一场能量: {evaluation["field_energy"]:.3f}')
    print(f'   统一场相干性: {evaluation["field_coherence"]:.3f}')
    print(f'   共振次数: {evaluation["num_resonances"]}')
    
    # 7. 多次共振迭代演示
    print('\n7. 多次共振迭代演示...')
    for i in range(3):
        test_input = f"迭代测试 {i+1}"
        result = igctr.resonance_optimization(test_input)
        print(f'   迭代 {i+1}: 共振强度 = {result["resonance_signal"].signal_strength:.3f}')
    
    # 8. 最终评估
    print('\n8. 最终评估...')
    final_evaluation = igctr.evaluate_field_unification()
    print(f'   最终统一场评分: {final_evaluation["score"]:.3f}')
    print(f'   最终等级: {final_evaluation["grade"]}')
    print(f'   总共振次数: {final_evaluation["num_resonances"]}')
    
    print('\n=== IGCTR_UnifiedField 模块测试完成 ===')
    print('✅ 所有测试通过！')
    
except Exception as e:
    print(f'\n❌ 测试失败: {e}')
    import traceback
    traceback.print_exc()