"""
main.py - AGI最小工作原型入口程序（增强版）

演示基于复合体理学框架的AGI核心功能（增强版）：
1. 复合体网络初始化
2. 能量流动演示
3. 多任务处理演示（扩展版）
4. 自适应学习演示（真正自学习）
5. 向量数据库演示（新增）
6. 神经网络演示（新增）
7. 完整流程演示

运行方式：
    python main.py
"""

import sys
import time
from typing import List, Dict, Any

# 导入AGI核心模块
from agi_core import create_default_network, ComplexNetwork, LayerType
from energy_engine import EnergyEngine
from adaptive_learner import AdaptiveLearner, FeedbackType
from task_interface import TaskInterface, TaskType
from utils import AGILogger, print_header, print_separator, format_network_visualization

# 导入新增模块
from vector_db import VectorDB
from neural_network import NeuralNetwork, TextClassificationNet


def demo_network_initialization(logger):
    """演示1：复合体网络初始化"""
    print_header("演示1：复合体网络初始化")
    
    logger.info("创建默认4层复合体网络...")
    network = create_default_network()
    
    # 展示网络结构
    print("\n网络结构：")
    print(format_network_visualization(network))
    
    # 展示网络状态
    state = network.get_network_state()
    print(f"\n网络状态：")
    print(f"  总复合体数：{state['total_units']}")
    print(f"  层级分布：{state['layer_distribution']}")
    print(f"  总能量：{state['total_energy']:.2f}")
    print(f"  激活单元：{state['active_units']}")
    
    return network


def demo_energy_flow(network, logger):
    """演示2：能量流动引擎"""
    print_header("演示2：能量流动引擎")
    
    logger.info("初始化能量引擎...")
    engine = EnergyEngine(network)
    
    # 展示初始能量分布
    print("\n初始能量状态：")
    report = engine.get_energy_report()
    print(f"  能量池：{report['energy_pool']:.2f}")
    for layer, avg in report['layer_averages'].items():
        print(f"  {layer}层平均能量：{avg:.2f}")
    
    # 演示能量分配
    print("\n执行能量分配...")
    engine.allocate_energy("P1", 0.3)
    engine.allocate_energy("C1", 0.2)
    engine.distribute_to_layer(LayerType.DECISION, 0.5)
    
    # 演示信号处理（能量传递）
    print("\n模拟信号传递（P1 -> C1 -> D1）...")
    results = engine.process_signal("P1", 0.5)
    print(f"  传递到：{results}")
    
    # 演示能量消耗
    print("\n模拟信息处理能量消耗...")
    consumed = engine.consume_for_processing("C1", 0.1)
    print(f"  C1消耗能量：{consumed:.2f}")
    
    # 信息价值评估
    print("\n信息价值评估演示：")
    test_texts = [
        "这是一条普通消息...",
        "重要：系统需要紧急处理...",
        "紧急通知：必须立即行动..."
    ]
    for text in test_texts:
        value = engine.evaluate_information_value(text)
        print(f"  '{text[:20]}...' -> 价值：{value:.2f}")
    
    # 最终能量报告
    print("\n最终能量状态：")
    report = engine.get_energy_report()
    print(f"  能量池：{report['energy_pool']:.2f}")
    print(f"  单元能量：{report['unit_energies']}")
    
    return engine


def demo_task_processing(network, engine, logger):
    """演示3：多任务处理接口（增强版）"""
    print_header("演示3：多任务处理接口（增强版）")
    
    logger.info("初始化任务接口...")
    learner = AdaptiveLearner(network, engine)
    task_interface = TaskInterface(network, engine, learner)
    
    # 任务1：文本理解（增强版：更多概念和情感）
    print("\n任务1：文本理解（增强版）")
    task1 = task_interface.create_task(
        "text", 
        "你好，我是AGI系统，我可以学习、推理和决策！",
        generate_response=True
    )
    task1 = task_interface.process(task1)
    print(f"  输入：{task1.input_data}")
    print(f"  输出：{task1.output}")
    print(f"  置信度：{task1.confidence:.2f}")
    print(f"  处理时间：{task1.processing_time:.3f}s")
    
    # 任务2：简单推理（增强版：多种推理类型）
    print("\n任务2：简单推理（增强版）")
    task2 = task_interface.create_task(
        "reasoning",
        "因为系统能量高，所以应该能处理复杂任务，所有AGI系统都具备学习能力",
        facts={"energy": 0.8},
        rules=["高能量规则", "学习进步规则"]
    )
    task2 = task_interface.process(task2)
    print(f"  输入：{task2.input_data}")
    print(f"  推理结论：{task2.output.get('conclusions', [])}")
    print(f"  推理类型：{task2.output.get('reasoning_types', [])}")
    print(f"  置信度：{task2.confidence:.2f}")
    
    # 任务3：决策制定（增强版）
    print("\n任务3：决策制定（增强版）")
    options = [
        {"name": "方案A：飞机", "成本": 0.3, "收益": 0.8, "风险": "低", "舒适度": "高"},
        {"name": "方案B：高铁", "成本": 0.6, "收益": 0.9, "风险": "中", "舒适度": "中"},
        {"name": "方案C：自驾", "成本": 0.2, "收益": 0.5, "风险": "低", "舒适度": "低"}
    ]
    task3 = task_interface.create_task(
        "decision",
        options,
        criteria_weights={"成本": -1.0, "收益": 1.0, "舒适度": 0.8}
    )
    # 设置决策权重
    task_interface.decision_maker.criteria_weights = {"成本": -1.0, "收益": 1.0, "舒适度": 0.8}
    task3 = task_interface.process(task3)
    print(f"  选项数：{len(options)}")
    print(f"  决策结果：{task3.output.get('choice', {}).get('name', 'N/A')}")
    print(f"  理由：{task3.output.get('reason', 'N/A')}")
    print(f"  置信度：{task3.confidence:.2f}")
    print(f"  详细分数：{task3.output.get('score_details', {})}")
    
    # 任务摘要
    print("\n任务处理摘要：")
    summary = task_interface.get_task_summary()
    print(f"  总任务数：{summary['total']}")
    print(f"  成功率：{summary.get('success_rate', 0):.2f}")
    print(f"  平均处理时间：{summary.get('avg_processing_time', 0):.3f}s")
    
    return task_interface


def demo_adaptive_learning(network, engine, logger):
    """演示4：自适应学习模块（真正自学习）"""
    print_header("演示4：自适应学习模块（真正自学习）")
    
    logger.info("初始化自适应学习模块...")
    learner = AdaptiveLearner(network, engine)
    
    # 模拟一些学习经验（多样化和增强）
    print("\n模拟学习任务（真正自学习）...")
    
    test_cases = [
        ("text", "你好，AGI世界！", "你好！我是AGI原型系统。", FeedbackType.POSITIVE),
        ("text", "再见，世界", "再见！期待下次交流。", FeedbackType.POSITIVE),
        ("reasoning", "A大于B，因为能量高", "A大于B", FeedbackType.POSITIVE),
        ("text", "错误输入xxx", "不知道", FeedbackType.NEGATIVE),
        ("decision", "选择方案", "方案A", FeedbackType.POSITIVE),
        ("text", "AGI可以改变世界", "AGI是通用人工智能", FeedbackType.POSITIVE),
        ("reasoning", "所有系统都需要能量", "系统需要能量支持", FeedbackType.POSITIVE),
        ("text", "bad error fail", "错误", FeedbackType.NEGATIVE),
    ]
    
    for i, (task_type, inp, out, feedback) in enumerate(test_cases):
        exp = learner.record_experience(
            task_id=f"learn_{i}",
            task_type=task_type,
            input_data=inp,
            output_data=out,
            feedback=feedback
        )
        print(f"  经验{i+1}：{task_type}任务，反馈={feedback.value}，分数={exp.performance_score:.2f}")
    
    # 展示学习洞察（增强版）
    print("\n学习洞察（增强版）：")
    insights = learner.get_learning_insights()
    print(f"  总经验数：{insights['total_experiences']}")
    print(f"  最近平均表现：{insights['recent_avg_performance']:.2f}")
    print(f"  表现趋势：{insights['performance_trend']}")
    print(f"  最弱任务类型：{insights['weakest_task_type']}")
    print(f"  学习进度：{insights.get('learning_progress', 0):.2f}")
    
    # 展示统计（增强版）
    print(f"\n学习统计（增强版）：")
    print(f"  总任务：{learner.stats['total_tasks']}")
    print(f"  成功：{learner.stats['successful_tasks']}")
    print(f"  失败：{learner.stats['failed_tasks']}")
    print(f"  平均表现：{learner.stats['avg_performance']:.2f}")
    print(f"  自适应调整次数：{learner.stats['adaptation_count']}")
    print(f"  模式调整次数：{learner.stats['pattern_adjustments']}")
    
    # 展示不确定性
    print(f"\n不确定性跟踪：")
    for task_type, uncertainty in insights.get('uncertainty_levels', {}).items():
        print(f"  {task_type}: {uncertainty:.2f}")
    
    # 改进建议
    suggestions = learner.suggest_improvements()
    if suggestions:
        print(f"\n改进建议：")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    return learner


def demo_vector_database(logger):
    """演示5：向量数据库（新增）"""
    print_header("演示5：向量数据库（新增）")
    
    logger.info("初始化向量数据库...")
    db = VectorDB(dimension=64)
    
    # 添加知识
    print("\n添加知识到向量数据库...")
    knowledge_items = [
        ("人工智能是计算机科学的一个分支", {"category": "definition", "source": "textbook"}),
        ("机器学习是人工智能的子集", {"category": "relationship", "type": "hierarchy"}),
        ("深度学习使用神经网络", {"category": "technology", "subfield": "DL"}),
        ("AGI是通用人工智能", {"category": "definition", "level": "advanced"}),
        ("复合体理学研究系统演化", {"category": "theory", "field": "interdisciplinary"}),
        ("能量管理优化系统性能", {"category": "principle", "application": "AGI"}),
    ]
    
    for text, metadata in knowledge_items:
        record_id = db.add(text, metadata)
        print(f"  添加：{text[:30]}... (ID: {record_id})")
    
    # 搜索演示
    print("\n搜索演示：")
    queries = [
        "什么是人工智能",
        "AGI的定义",
        "能量如何管理"
    ]
    
    for query in queries:
        results = db.search(query, top_k=3)
        print(f"\n  查询：{query}")
        if results:
            for i, r in enumerate(results, 1):
                print(f"    结果{i}：{r['text'][:40]}... (相似度: {r['score']:.3f})")
        else:
            print("    无结果")
    
    print(f"\n数据库大小: {db.size()}")
    
    # 导出演示
    export_path = "vector_db_export.json"
    if db.export_to_json(export_path):
        print(f"\n已导出到：{export_path}")
    
    return db


def demo_neural_network(logger):
    """演示6：神经网络（新增）"""
    print_header("演示6：神经网络（新增）")
    
    logger.info("初始化神经网络...")
    
    # 1. 创建简单网络
    print("\n1. 创建前馈神经网络（3 -> 5 -> 2）")
    nn = NeuralNetwork(layer_sizes=[3, 5, 2], activations=["relu", "sigmoid"])
    print(f"   网络结构：{nn.layer_sizes}")
    
    # 2. 训练演示
    print("\n2. 训练：学习简单逻辑")
    training_data = [
        ([0, 0, 0], [1, 0]),  # 全0 -> 类别0
        ([1, 0, 0], [0, 1]),  # 有1 -> 类别1
        ([0, 1, 0], [0, 1]),
        ([0, 0, 1], [0, 1]),
        ([1, 1, 0], [0, 1]),
        ([1, 1, 1], [0, 1]),
    ]
    
    losses = nn.train(training_data, epochs=50, learning_rate=0.3, verbose=False)
    print(f"   最终损失：{losses[-1]:.4f}")
    print(f"   初始损失：{losses[0]:.4f}")
    
    # 3. 测试
    print("\n3. 测试网络：")
    test_input = [1, 0, 1]
    output = nn.predict(test_input)
    print(f"   输入：{test_input}")
    print(f"   输出：{output}")
    print(f"   预测类别：{output.index(max(output))}")
    
    # 4. 文本分类网络
    print("\n4. 文本分类网络演示")
    text_nn = TextClassificationNet(vocab_size=50, hidden_size=16, num_classes=3)
    
    # 训练数据：简单情感分类（3类：负面/中性/正面）
    train_texts = [
        ("糟糕 差 讨厌 失败", [1, 0, 0]),  # 负面
        ("一般 还行 普通", [0, 1, 0]),    # 中性
        ("好 棒 喜欢 成功", [0, 0, 1]),   # 正面
        ("错误 问题 bug", [1, 0, 0]),        # 负面
        ("不错 优秀 完美", [0, 0, 1]),      # 正面
    ]
    
    training_data = [(text_nn.text_to_vector(text), label) for text, label in train_texts]
    text_nn.train(training_data, epochs=30, learning_rate=0.3, verbose=False)
    
    # 测试
    test_texts = ["非常棒", "好差啊", "还行吧"]
    print("\n   文本分类测试：")
    for text in test_texts:
        result = text_nn.predict_text(text)
        category = ["负面", "中性", "正面"][result.index(max(result))]
        print(f"   文本：{text} -> 预测：{category} (原始输出: {result})")
    
    return nn, text_nn


def demo_integrated_run(network, engine, learner, logger):
    """演示7：完整流程演示（增强版）"""
    print_header("演示7：完整流程演示（增强版：文本理解 -> 推理 -> 决策）")
    
    logger.info("创建任务接口...")
    task_interface = TaskInterface(network, engine, learner)
    
    # 完整流程：理解用户输入 -> 推理 -> 决策
    user_input = "我需要选择一个旅行方案，帮我决定，要考虑成本和舒适度"
    
    print(f"\n用户输入：{user_input}")
    
    # 步骤1：理解文本（增强版）
    print("\n步骤1：文本理解（增强版）")
    task1 = task_interface.create_task("text", user_input)
    task1 = task_interface.process(task1)
    understanding = task1.output
    print(f"  意图：{understanding.get('intent', 'N/A')}")
    print(f"  情感：{understanding.get('sentiment', 'N/A')}")
    print(f"  概念：{understanding.get('concepts', [])}")
    print(f"  复杂度：{understanding.get('complexity', 'N/A')}")
    
    # 步骤2：推理分析（增强版）
    print("\n步骤2：推理分析（增强版）")
    context = {
        "user_intent": understanding.get('intent'),
        "concepts": understanding.get('concepts', [])
    }
    task2 = task_interface.create_task("reasoning", user_input, **context)
    task2 = task_interface.process(task2)
    print(f"  推理结论数：{len(task2.output.get('conclusions', []))}")
    for concl in task2.output.get('conclusions', []):
        print(f"    - 类型：{concl.get('type', 'N/A')}, {concl.get('inference', concl.get('result', 'N/A'))}")
    
    # 步骤3：制定决策（增强版）
    print("\n步骤3：制定决策（增强版）")
    travel_options = [
        {"name": "方案1：飞机", "时间": 0.9, "成本": 0.3, "舒适度": 0.8, "风险": "低"},
        {"name": "方案2：高铁", "时间": 0.6, "成本": 0.7, "舒适度": 0.7, "风险": "中"},
        {"name": "方案3：自驾", "时间": 0.4, "成本": 0.8, "舒适度": 0.5, "风险": "低"}
    ]
    task3 = task_interface.create_task("decision", travel_options)
    task_interface.decision_maker.criteria_weights = {"时间": 1.0, "成本": -1.0, "舒适度": 0.8, "风险": -0.5}
    task3 = task_interface.process(task3)
    choice = task3.output.get('choice', {})
    print(f"  推荐：{choice.get('name', 'N/A')}")
    print(f"  理由：{task3.output.get('reason', 'N/A')}")
    print(f"  置信度：{task3.confidence:.2f}")
    print(f"  所有方案得分：{task3.output.get('all_scores', [])}")
    
    # 最终系统状态
    print("\n最终系统状态：")
    state = network.get_network_state()
    print(f"  激活单元：{state['active_units']}/{state['total_units']}")
    energy_report = engine.get_energy_report()
    print(f"  剩余能量池：{energy_report['energy_pool']:.2f}")
    
    # 学习总结
    print("\n学习总结：")
    insights = learner.get_learning_insights()
    print(f"  总经验数：{insights['total_experiences']}")
    print(f"  学习进度：{insights.get('learning_progress', 0):.2f}")
    suggestions = learner.suggest_improvements()
    if suggestions:
        print(f"  改进建议：{suggestions[0]}")


def main():
    """主函数：运行所有演示（增强版）"""
    print_header("AGI最小工作原型 - 基于复合体理学框架（增强版）", "=")
    
    logger = AGILogger("AGI-Demo")
    logger.info("AGI系统启动...")
    
    try:
        # 演示1：网络初始化
        network = demo_network_initialization(logger)
        time.sleep(0.5)
        
        # 演示2：能量流动
        engine = demo_energy_flow(network, logger)
        time.sleep(0.5)
        
        # 演示3：任务处理（增强版）
        task_interface = demo_task_processing(network, engine, logger)
        time.sleep(0.5)
        
        # 演示4：自适应学习（增强版）
        learner = demo_adaptive_learning(network, engine, logger)
        time.sleep(0.5)
        
        # 演示5：向量数据库（新增）
        db = demo_vector_database(logger)
        time.sleep(0.5)
        
        # 演示6：神经网络（新增）
        nn, text_nn = demo_neural_network(logger)
        time.sleep(0.5)
        
        # 演示7：完整流程（增强版）
        demo_integrated_run(network, engine, learner, logger)
        
        print_header("演示完成！（增强版）", "=")
        logger.info("AGI系统演示完成")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
