"""
test_agi.py - AGI最小工作原型测试用例（增强版）

测试覆盖（增强版）：
1. 复合体核心结构测试
2. 能量流动引擎测试
3. 自适应学习模块测试（增强：真正自学习）
4. 任务处理接口测试（增强：新推理规则、扩展词库）
5. 向量数据库测试（新增）
6. 神经网络测试（新增）
7. 集成测试（增强）

运行方式：
    python test_agi.py -v
"""

import unittest
import sys
import os
from typing import Any, Dict, List

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agi_core import (
    ComplexUnit, ComplexNetwork, LayerType, 
    create_default_network
)
from energy_engine import EnergyEngine, EnergyPacket
from adaptive_learner import AdaptiveLearner, FeedbackType, Experience
from task_interface import (
    TaskInterface, TaskType, TaskStatus,
    TextProcessor, ReasoningEngine, DecisionMaker
)
from utils import AGILogger, format_dict, clamp, calculate_similarity

# 导入新增模块
from vector_db import VectorDB
from neural_network import NeuralNetwork, TextClassificationNet


class TestAGICore(unittest.TestCase):
    """测试复合体核心结构"""
    
    def setUp(self):
        self.unit = ComplexUnit("test1", LayerType.PERCEPTION, energy=0.5)
        self.network = ComplexNetwork()
    
    def test_complex_unit_creation(self):
        """测试复合体单元创建"""
        self.assertEqual(self.unit.id, "test1")
        self.assertEqual(self.unit.layer, LayerType.PERCEPTION)
        self.assertEqual(self.unit.energy, 0.5)
        self.assertTrue(self.unit.is_activated())  # 0.5 > 0.3
    
    def test_complex_unit_energy(self):
        """测试能量操作"""
        self.unit.receive_energy(0.3)
        self.assertAlmostEqual(self.unit.energy, 0.8)
        
        consumed = self.unit.consume_energy(0.2)
        self.assertAlmostEqual(consumed, 0.2)
        self.assertAlmostEqual(self.unit.energy, 0.6)
        
        # 消耗超过现有能量
        consumed = self.unit.consume_energy(1.0)
        self.assertAlmostEqual(consumed, 0.6)
        self.assertAlmostEqual(self.unit.energy, 0.0)
    
    def test_complex_unit_attention(self):
        """测试注意力权重"""
        self.unit.update_attention(0.8)
        self.assertEqual(self.unit.attention_weight, 0.8)
        
        # 测试边界
        self.unit.update_attention(1.5)
        self.assertEqual(self.unit.attention_weight, 1.0)
        
        self.unit.update_attention(-0.5)
        self.assertEqual(self.unit.attention_weight, 0.0)
    
    def test_network_add_unit(self):
        """测试向网络添加单元"""
        self.network.add_unit(self.unit)
        self.assertIn("test1", self.network.units)
        self.assertEqual(len(self.network.units), 1)
    
    def test_network_connect(self):
        """测试复合体连接"""
        unit1 = ComplexUnit("U1", LayerType.PERCEPTION)
        unit2 = ComplexUnit("U2", LayerType.COGNITION)
        self.network.add_unit(unit1)
        self.network.add_unit(unit2)
        
        self.network.connect("U1", "U2")
        self.assertIn("U2", self.network.connections["U1"])
        self.assertIn("U1", unit2.inputs)
    
    def test_network_layer_units(self):
        """测试获取层级单元"""
        p1 = ComplexUnit("P1", LayerType.PERCEPTION)
        p2 = ComplexUnit("P2", LayerType.PERCEPTION)
        c1 = ComplexUnit("C1", LayerType.COGNITION)
        self.network.add_unit(p1)
        self.network.add_unit(p2)
        self.network.add_unit(c1)
        
        perception_units = self.network.get_layer_units(LayerType.PERCEPTION)
        self.assertEqual(len(perception_units), 2)
        
        cognition_units = self.network.get_layer_units(LayerType.COGNITION)
        self.assertEqual(len(cognition_units), 1)
    
    def test_network_propagate(self):
        """测试信号传播"""
        p1 = ComplexUnit("P1", LayerType.PERCEPTION, energy=1.0)
        c1 = ComplexUnit("C1", LayerType.COGNITION)
        self.network.add_unit(p1)
        self.network.add_unit(c1)
        self.network.connect("P1", "C1")
        
        results = self.network.propagate("P1", 0.5)
        self.assertIn("C1", results)


class TestEnergyEngine(unittest.TestCase):
    """测试能量流动引擎"""
    
    def setUp(self):
        self.network = create_default_network()
        self.engine = EnergyEngine(self.network)
    
    def test_energy_allocation(self):
        """测试能量分配"""
        initial = self.engine.energy_pool
        self.engine.allocate_energy("P1", 0.3)
        # P1初始能量0.8，最多接收0.2（上限1.0），所以energy_pool减少0.2
        self.assertEqual(self.engine.energy_pool, initial - 0.2)
        
        unit = self.network.units["P1"]
        self.assertEqual(unit.energy, 1.0)  # 0.8 + 0.2 = 1.0 (capped)
    
    def test_distribute_to_layer(self):
        """测试向层级分配能量"""
        initial_pool = self.engine.energy_pool
        self.engine.distribute_to_layer(LayerType.COGNITION, 0.5)
        
        for unit in self.network.get_layer_units(LayerType.COGNITION):
            self.assertGreater(unit.energy, 0.6)  # 0.6 + gain
        
        self.assertLess(self.engine.energy_pool, initial_pool)
    
    def test_energy_report(self):
        """测试能量报告生成"""
        report = self.engine.get_energy_report()
        self.assertIn("energy_pool", report)
        self.assertIn("layer_averages", report)
        self.assertIn("unit_energies", report)
    
    def test_information_value_evaluation(self):
        """测试信息价值评估"""
        normal_text = "这是一条普通消息"
        value1 = self.engine.evaluate_information_value(normal_text)
        self.assertGreaterEqual(value1, 0.0)
        self.assertLessEqual(value1, 1.0)
        
        important_text = "重要：系统需要紧急处理，立即行动！"
        value2 = self.engine.evaluate_information_value(important_text)
        self.assertGreaterEqual(value2, 0.0)
        self.assertLessEqual(value2, 1.0)
    
    def test_process_signal(self):
        """测试信号处理（能量传递）"""
        results = self.engine.process_signal("P1", 0.5)
        self.assertIsInstance(results, list)
    
    def test_consume_energy(self):
        """测试能量消耗"""
        initial = self.engine.energy_pool
        consumed = self.engine.consume_for_processing("C1", 0.1)
        self.assertEqual(consumed, 0.1)
        # 消耗0.1，但回收30%(0.03)到能量池，所以能量池增加0.03
        self.assertEqual(self.engine.energy_pool, initial + 0.03)


class TestAdaptiveLearner(unittest.TestCase):
    """测试自适应学习模块（增强版：真正自学习）"""
    
    def setUp(self):
        self.network = create_default_network()
        self.engine = EnergyEngine(self.network)
        self.learner = AdaptiveLearner(self.network, self.engine)
    
    def test_record_experience(self):
        """测试记录经验"""
        exp = self.learner.record_experience(
            task_id="test_1",
            task_type="text",
            input_data="hello",
            output_data="Hello!",
            feedback=FeedbackType.POSITIVE
        )
        self.assertEqual(len(self.learner.experiences), 1)
        self.assertEqual(exp.feedback, FeedbackType.POSITIVE)
        self.assertEqual(self.learner.stats["total_tasks"], 1)
    
    def test_performance_evaluation(self):
        """测试性能评估"""
        # 完全匹配
        score1 = self.learner.evaluate_performance("hello", "hello")
        self.assertEqual(score1, 1.0)
        
        # 包含关系
        score2 = self.learner.evaluate_performance("hello world", "world")
        self.assertGreater(score2, 0.5)
        
        # 数值近似
        score3 = self.learner.evaluate_performance(10.0, 9.5)
        self.assertGreater(score3, 0.8)
    
    def test_adapt_parameters(self):
        """测试参数调整（真实调整）"""
        # 创建一个失败经验
        exp = Experience(
            task_id="test_adapt",
            task_type="text",
            input_data="test",
            output_data="bad",
            feedback=FeedbackType.NEGATIVE,
            performance_score=0.2
        )
        
        adjustments = self.learner.adapt_parameters(exp)
        self.assertIsInstance(adjustments, dict)
        self.assertGreater(len(adjustments), 0)
        
        # 检查权重是否被调整
        for key in adjustments:
            if "attention" in key:
                self.assertIn("old", adjustments[key])
                self.assertIn("new", adjustments[key])
    
    def test_learning_insights(self):
        """测试学习洞察（增强版）"""
        # 添加一些经验
        for i in range(5):
            self.learner.record_experience(
                task_id=f"insight_{i}",
                task_type="text",
                input_data=f"test {i}",
                output_data="output",
                feedback=FeedbackType.POSITIVE if i < 3 else FeedbackType.NEGATIVE
            )
        
        insights = self.learner.get_learning_insights()
        self.assertIn("total_experiences", insights)
        self.assertIn("recent_avg_performance", insights)
        self.assertIn("learning_progress", insights)
    
    def test_save_load_experiences(self):
        """测试经验保存和加载"""
        # 记录经验
        self.learner.record_experience(
            task_id="save_test",
            task_type="text",
            input_data="hello",
            output_data="Hello!",
            feedback=FeedbackType.POSITIVE
        )
        
        # 保存
        self.learner.save_experiences("test_experiences.json")
        
        # 创建新的learner并加载
        new_learner = AdaptiveLearner(self.network, self.engine)
        new_learner.load_experiences("test_experiences.json")
        
        self.assertEqual(len(new_learner.experiences), 1)
        
        # 清理
        import os
        if os.path.exists("test_experiences.json"):
            os.remove("test_experiences.json")
    
    def test_real_learning_loop(self):
        """测试真正自学习循环（新增）"""
        # 添加多个经验，触发学习
        for i in range(10):
            feedback = FeedbackType.POSITIVE if i % 2 == 0 else FeedbackType.NEGATIVE
            self.learner.record_experience(
                task_id=f"learn_{i}",
                task_type="text" if i < 5 else "reasoning",
                input_data=f"input {i}",
                output_data=f"output {i}",
                feedback=feedback
            )
        
        # 检查学习状态
        self.assertEqual(len(self.learner.experiences), 10)
        self.assertGreater(len(self.learner.parameter_memory), 0)
        
        # 检查不确定性跟踪
        insights = self.learner.get_learning_insights()
        self.assertIn("uncertainty_levels", insights)
    
    def test_suggest_improvements(self):
        """测试改进建议（新增）"""
        # 添加一些失败经验
        for i in range(5):
            self.learner.record_experience(
                task_id=f"suggest_{i}",
                task_type="text",
                input_data="test",
                output_data="bad",
                feedback=FeedbackType.NEGATIVE
            )
        
        suggestions = self.learner.suggest_improvements()
        self.assertIsInstance(suggestions, list)


class TestTaskInterface(unittest.TestCase):
    """测试任务处理接口（增强版：新推理规则、扩展词库）"""
    
    def setUp(self):
        self.network = create_default_network()
        self.engine = EnergyEngine(self.network)
        self.learner = AdaptiveLearner(self.network, self.engine)
        self.interface = TaskInterface(self.network, self.engine, self.learner)
    
    def test_text_understanding(self):
        """测试文本理解（增强版：扩展词库）"""
        task = self.interface.create_task(
            "text", 
            "你好，我是AGI系统，我可以学习和推理！"
        )
        task = self.interface.process(task)
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIn("concepts", task.output)
        self.assertIn("sentiment", task.output)
        self.assertIn("intent", task.output)
        
        # 检查是否识别了AGI相关概念
        concepts = task.output.get("concepts", [])
        self.assertGreater(len(concepts), 0)
    
    def test_reasoning(self):
        """测试推理功能（增强版：多种推理类型）"""
        task = self.interface.create_task(
            "reasoning",
            "因为系统能量高，所以应该能处理复杂任务",
            facts={"energy": 0.8}
        )
        task = self.interface.process(task)
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIn("conclusions", task.output)
        self.assertIn("reasoning_types", task.output)
        
        # 检查是否包含因果推理
        reasoning_types = task.output.get("reasoning_types", [])
        self.assertGreater(len(reasoning_types), 0)
    
    def test_decision_making(self):
        """测试决策功能（增强版：多维度评分）"""
        options = [
            {"name": "方案A", "成本": 0.3, "收益": 0.8, "舒适度": "高"},
            {"name": "方案B", "成本": 0.6, "收益": 0.9, "舒适度": "中"},
            {"name": "方案C", "成本": 0.2, "收益": 0.5, "舒适度": "低"}
        ]
        
        task = self.interface.create_task("decision", options)
        task = self.interface.process(task)
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIn("choice", task.output)
        self.assertIn("confidence", task.output)
        self.assertIn("score_details", task.output)
    
    def test_task_summary(self):
        """测试任务摘要"""
        # 处理几个任务
        for i in range(3):
            task = self.interface.create_task("text", f"test {i}")
            self.interface.process(task)
        
        summary = self.interface.get_task_summary()
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["completed"], 3)
        self.assertEqual(summary["success_rate"], 1.0)
    
    def test_text_processor_extended(self):
        """测试文本处理器（扩展版：更多词汇）"""
        processor = TextProcessor()
        
        # 测试AGI相关概念
        result = processor.understand("AGI是通用人工智能")
        self.assertIn("agi", result.get("concepts", []))
        
        # 测试扩展的情感词
        result = processor.understand("这个系统非常excellent和amazing！")
        self.assertEqual(result["sentiment"], "positive")
    
    def test_reasoning_engine_extended(self):
        """测试推理引擎（扩展版：多种推理规则）"""
        engine = ReasoningEngine()
        
        # 添加事实
        engine.add_fact("系统状态", "运行中")
        engine.add_fact("能量水平", "高")
        
        # 测试因果推理
        result = engine.reason("因为系统能量高，所以处理能力强")
        self.assertGreater(len(result.get("conclusions", [])), 0)
        
        # 测试演绎推理（包含"所有"）
        result2 = engine.reason("所有的AGI系统都需要能量")
        self.assertGreater(len(result2.get("conclusions", [])), 0)


class TestVectorDB(unittest.TestCase):
    """测试向量数据库（新增）"""
    
    def setUp(self):
        self.db = VectorDB(dimension=64)
    
    def test_add_and_search(self):
        """测试添加和搜索"""
        # 添加文本
        id1 = self.db.add("人工智能是计算机科学的一个分支")
        id2 = self.db.add("机器学习是人工智能的子集")
        
        self.assertEqual(self.db.size(), 2)
        
        # 搜索
        results = self.db.search("什么是人工智能", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("score", results[0])
        self.assertIn("text", results[0])
    
    def test_similarity(self):
        """测试相似度计算"""
        self.db.add("深度学习使用神经网络")
        self.db.add("AGI是通用人工智能")
        
        # 相似查询
        results = self.db.search("神经网络", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0]["score"], 0.0)
    
    def test_export_import(self):
        """测试导入导出"""
        self.db.add("测试文本1", {"category": "test"})
        self.db.add("测试文本2", {"category": "test"})
        
        # 导出
        self.assertTrue(self.db.export_to_json("test_vector_db.json"))
        
        # 导入到新数据库
        new_db = VectorDB()
        count = new_db.import_from_json("test_vector_db.json")
        self.assertEqual(count, 2)
        
        # 清理
        import os
        if os.path.exists("test_vector_db.json"):
            os.remove("test_vector_db.json")
    
    def test_delete(self):
        """测试删除"""
        record_id = self.db.add("要删除的文本")
        self.assertEqual(self.db.size(), 1)
        
        result = self.db.delete(record_id)
        self.assertTrue(result)
        self.assertEqual(self.db.size(), 0)


class TestNeuralNetwork(unittest.TestCase):
    """测试神经网络（新增）"""
    
    def test_network_creation(self):
        """测试网络创建"""
        nn = NeuralNetwork(layer_sizes=[3, 5, 2])
        self.assertEqual(nn.layer_sizes, [3, 5, 2])
        self.assertEqual(len(nn.layers), 2)
    
    def test_forward_propagation(self):
        """测试前向传播"""
        nn = NeuralNetwork(layer_sizes=[3, 5, 2])
        inputs = [0.5, 0.3, 0.8]
        
        output = nn.predict(inputs)
        self.assertEqual(len(output), 2)
        self.assertIsInstance(output[0], float)
    
    def test_training(self):
        """测试训练"""
        nn = NeuralNetwork(layer_sizes=[3, 5, 2])
        
        # 简单训练数据
        training_data = [
            ([0, 0, 0], [1, 0]),
            ([1, 0, 0], [0, 1]),
            ([0, 1, 0], [0, 1]),
            ([0, 0, 1], [0, 1]),
        ]
        
        losses = nn.train(training_data, epochs=20, learning_rate=0.3, verbose=False)
        self.assertEqual(len(losses), 20)
        self.assertLess(losses[-1], losses[0])  # 损失应该下降
    
    def test_evaluation(self):
        """测试评估"""
        nn = NeuralNetwork(layer_sizes=[3, 5, 2])
        
        test_data = [
            ([0, 0, 0], [1, 0]),
            ([1, 0, 0], [0, 1]),
        ]
        
        # 先简单训练
        nn.train(test_data, epochs=10, learning_rate=0.5, verbose=False)
        
        # 评估
        result = nn.evaluate(test_data)
        self.assertIn("accuracy", result)
        self.assertIn("average_loss", result)
    
    def test_text_classification(self):
        """测试文本分类网络"""
        text_nn = TextClassificationNet(vocab_size=50, hidden_size=16, num_classes=3)
        
        # 训练
        train_texts = [
            ("好 棒 喜欢", [0, 0, 1]),   # 正面
            ("差 糟 讨厌", [1, 0, 0]),   # 负面
            ("一般 还行", [0, 1, 0]),       # 中性
        ]
        
        training_data = [(text_nn.text_to_vector(text), label) for text, label in train_texts]
        text_nn.train(training_data, epochs=20, learning_rate=0.3, verbose=False)
        
        # 测试
        result = text_nn.predict_text("非常好")
        self.assertEqual(len(result), 3)
        self.assertGreater(max(result), 0.0)


class TestIntegration(unittest.TestCase):
    """集成测试（增强版）"""
    
    def setUp(self):
        self.network = create_default_network()
        self.engine = EnergyEngine(self.network)
        self.learner = AdaptiveLearner(self.network, self.engine)
        self.interface = TaskInterface(self.network, self.engine, self.learner)
    
    def test_full_pipeline(self):
        """测试完整流程：输入文本 -> 理解 -> 推理 -> 决策"""
        user_input = "我需要选择一个旅行方案，帮我决定"
        
        # 步骤1：文本理解
        task1 = self.interface.create_task("text", user_input)
        task1 = self.interface.process(task1)
        self.assertEqual(task1.status, TaskStatus.COMPLETED)
        understanding = task1.output
        
        # 步骤2：推理
        task2 = self.interface.create_task("reasoning", user_input)
        task2 = self.interface.process(task2)
        self.assertEqual(task2.status, TaskStatus.COMPLETED)
        
        # 步骤3：决策
        options = [
            {"name": "飞机", "时间": 0.9, "成本": 0.3},
            {"name": "高铁", "时间": 0.6, "成本": 0.7}
        ]
        task3 = self.interface.create_task("decision", options)
        task3 = self.interface.process(task3)
        self.assertEqual(task3.status, TaskStatus.COMPLETED)
        self.assertIn("choice", task3.output)
    
    def test_vector_db_integration(self):
        """测试向量数据库集成（新增）"""
        # 创建向量数据库
        db = VectorDB(dimension=64)
        db.add("AGI是通用人工智能")
        db.add("复合体理学研究系统演化")
        
        # 搜索
        results = db.search("什么是AGI")
        self.assertGreater(len(results), 0)
    
    def test_neural_network_integration(self):
        """测试神经网络集成（新增）"""
        # 创建并训练网络
        nn = NeuralNetwork(layer_sizes=[3, 4, 2])
        training_data = [
            ([1, 0, 0], [0, 1]),
            ([0, 1, 0], [0, 1]),
            ([0, 0, 1], [0, 1]),
            ([0, 0, 0], [1, 0]),
        ]
        nn.train(training_data, epochs=30, learning_rate=0.3, verbose=False)
        
        # 测试
        output = nn.predict([1, 0, 0])
        self.assertEqual(len(output), 2)


if __name__ == "__main__":
    print("=" * 60)
    print("  AGI最小工作原型 - 单元测试（增强版）")
    print("=" * 60)
    
    # 配置日志
    logger = AGILogger("Test")
    logger.info("开始单元测试...")
    
    # 运行测试
    unittest.main(verbosity=2)
