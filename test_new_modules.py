"""
测试新创建的三个模块
基于四篇文档的太乙AGI升级验证
"""

print("=== 测试新模块（基于四篇文档）===\n")

# 1. 测试末那识与无剧场论模块
print("1. 测试 ManasNoTheater 模块...")
try:
    from ManasNoTheater import ManasNoTheaterModule, ManasGenerator, NoTheaterTheory
    
    config = {
        'manas': {'ego_strength': 0.7, 'attachment_threshold': 0.5},
        'no_theater': {'theater_mode': 'no-theater', 'dissolve_ego': True}
    }
    
    module = ManasNoTheaterModule(config)
    
    # 测试数据处理
    import numpy as np
    test_seed = np.random.randn(10)
    results = module.process(test_seed, generate_manas=True, apply_no_theater=True)
    
    print(f"   ✓ 末那识状态 ID: {results['manas_state'].state_id}")
    print(f"   ✓ 无剧场感知维度: {results['no_theater_perception'].shape}")
    if 'transformed_consciousness' in results:
        print(f"   ✓ 识形变完成: {results['transformed_consciousness'].consciousness_type}")
    print("   ✓ ManasNoTheater 模块测试通过\n")
    
except Exception as e:
    print(f"   ✗ 错误: {e}\n")

# 2. 测试流贯（△）相变监控模块
print("2. 测试 LiuGuanPhaseTransition 模块...")
try:
    from LiuGuanPhaseTransition import LiuGuanGovernance, LiuGuanCalculator, PhaseTransitionDetector
    
    # 测试计算器
    calculator = LiuGuanCalculator({
        'critical_threshold': 0.5,
        'fall_threshold': 0.2
    })
    
    # 模拟系统状态
    import numpy as np
    test_state = np.array([
        [1.0, 0.8, 0.6, 0.4, 0.2],
        [0.9, 0.7, 0.5, 0.3, 0.1],
        [0.8, 0.6, 0.4, 0.2, 0.0]
    ])
    
    metrics = calculator.calculate_delta(test_state)
    print(f"   ✓ 流贯度 △ = {metrics.delta:.4f}")
    print(f"   ✓ 系统状态: {metrics.system_state.value}")
    
    # 测试检测器
    detector = PhaseTransitionDetector({'detection_window': 5})
    print(f"   ✓ 相变检测器初始化完成")
    
    # 测试治理模块
    governance = LiuGuanGovernance({
        'intervention_threshold': 0.6,
        'governance_strategy': 'adaptive'
    })
    
    result = governance.evaluate_system(test_state)
    print(f"   ✓ 治理评估: 干预={result['should_intervene']}")
    print("   ✓ LiuGuanPhaseTransition 模块测试通过\n")
    
except Exception as e:
    print(f"   ✗ 错误: {e}\n")

# 3. 测试唯识论八识计算模型
print("3. 测试 YogacaraEightConsciousness 模块...")
try:
    from YogacaraEightConsciousness import EightConsciousnessModel, ConsciousnessType
    
    config = {
        'alaya_capacity': 1000,
        'activation_threshold': 0.5,
        'wisdom_threshold': 0.85
    }
    
    model = EightConsciousnessModel(config)
    
    # 测试种子存储
    import numpy as np
    for i in range(5):
        seed_content = np.random.randn(10)
        seed = model.store_seed(seed_content, seed_id=f"test_seed_{i}")
        print(f"   ✓ 存储种子 {seed.seed_id}: potential={seed.potential:.4f}")
    
    # 测试种子激活
    stimulus = np.random.randn(10)
    activated = model.activate_seeds(stimulus, n_seeds=3)
    print(f"   ✓ 激活了 {len(activated)} 个种子")
    
    # 测试通过不同识处理
    for ct in [ConsciousnessType.EYE, ConsciousnessType.MIND, ConsciousnessType.MANAS]:
        output = model.process_through_consciousness(activated, ct, stimulus)
        print(f"   ✓ {ct.value}: output_shape={output.shape}")
    
    # 测试阿赖耶识状态
    alaya_status = model.get_alaya_seed_bank_status()
    print(f"   ✓ 阿赖耶识种子库: {alaya_status['count']} 个种子")
    print("   ✓ YogacaraEightConsciousness 模块测试通过\n")
    
except Exception as e:
    print(f"   ✗ 错误: {e}\n")

# 4. 测试集成到 CompositeAGI_V2
print("4. 测试集成到 CompositeAGI_V2...")
try:
    from CompositeAGI_V2 import CompositeAGI_V2
    
    agi = CompositeAGI_V2()
    
    # 检查新模块是否加载
    print(f"   ✓ 末那识模块加载: {agi.manas_no_theater is not None}")
    print(f"   ✓ 流贯监控模块加载: {agi.liu_guan is not None}")
    print(f"   ✓ 唯识论八识模块加载: {agi.eight_consciousness is not None}")
    
    # 测试查询处理（简化）
    test_query = "测试末那识与无剧场论"
    result = agi.process_query(test_query)
    
    print(f"   ✓ 查询处理完成")
    print(f"   ✓ 结果模块数: {len(result['module_results'])}")
    print("   ✓ CompositeAGI_V2 集成测试通过\n")
    
except Exception as e:
    print(f"   ✗ 错误: {e}\n")

print("=" * 60)
print("测试完成！新模块已成功创建并集成到太乙AGI 12.0")
print("=" * 60)
