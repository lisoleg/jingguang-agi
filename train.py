#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AGI训练目标函数 - 基于SEGUE（广义熵大统一表达式）

论文：论多尺度熵效应的广义熵大统一：基于拓扑荷守恒与"一现象，三视界"框架的IGCTR诠释

SEGUE训练目标：
min L_AGI = S_total = S_von + S_shannon + S_geo + S_topo + S_thermo + I(A:B)

即：最小化总熵
或者等价地：max I(A:B) （最大化互信息）
"""


import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import random
import time

# 导入SEGUE评估器
from segue_evaluator import SEGUEEvaluator


@dataclass
class TrainingExample:
    """训练样本"""
    inputs: List[float]
    target: List[float]
    metadata: Optional[Dict] = None


class AGITrainer:
    """AGI训练器 - 基于SEGUE损失函数"""
    
    def __init__(self,
                 model: Any,  # AGI模型（如NeuralNetwork）
                 learning_rate: float = 0.1,
                 epochs: int = 10):
        """
        初始化AGI训练器
        
        参数:
            model: AGI模型
            learning_rate: 学习率
            epochs: 训练轮数
        """
        self.model = model
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        # SEGUE评估器
        self.segue_evaluator = SEGUEEvaluator()
        
        # 训练历史
        self.training_history: List[Dict] = []
        
        # SEGUE损失历史
        self.segue_loss_history: List[float] = []
        
    def segue_loss(self, 
                    outputs: List[float],
                    targets: List[float],
                    agi_state: Optional[Dict] = None) -> float:
        """
        基于SEGUE的损失函数
        
        公式：L_SEGUE = S_total = S_von + S_shannon + S_geo + S_topo + S_thermo + I(A:B)
        
        简化版：L_SEGUE = MSE(outputs, targets) + λ * S_total
        
        参数:
            outputs: 模型输出
            targets: 目标输出
            agi_state: AGI系统状态（可选，用于计算S_total）
            
        返回:
            loss: SEGUE损失值
        """
        # 1. 基础损失（均方误差）
        mse_loss = sum((o - t)**2 for o, t in zip(outputs, targets)) / len(targets)
        
        # 2. 如果提供了AGI状态，计算SEGUE总熵
        if agi_state is not None:
            # 计算SEGUE总熵
            segue_result = self.segue_evaluator.evaluate_agi_system(agi_state)
            S_total = segue_result['S_total']
            
            # 综合损失：MSE + λ * S_total
            lambda_reg = 0.01  # 正则化系数
            loss = mse_loss + lambda_reg * S_total
        else:
            # 没有AGI状态时，只使用MSE
            loss = mse_loss
            
        return loss
    
    def compute_quantum_state(self, 
                               outputs: List[float]) -> 'QuantumState':
        """
        从输出构建量子态（用于计算S_von）
        
        简化：将输出视为密度矩阵的特征值
        """
        from segue_evaluator import QuantumState
        
        # 将输出转换为密度矩阵（简化）
        n = len(outputs)
        rho = np.diag(outputs)  # 对角矩阵
        
        # 归一化（确保迹为1）
        trace = np.trace(rho)
        if trace > 1e-10:
            rho = rho / trace
            
        return QuantumState(density_matrix=rho)
    
    def compute_classical_state(self, 
                                  outputs: List[float]) -> 'ClassicalState':
        """
        从输出构建经典态（用于计算S_shannon）
        
        简化：将输出视为概率分布
        """
        from segue_evaluator import ClassicalState
        
        # 将输出转换为概率分布（softmax）
        exp_outputs = np.exp(outputs - np.max(outputs))  # 数值稳定性
        p = exp_outputs / np.sum(exp_outputs)
        
        return ClassicalState(probability_distribution=p)
    
    def train_single(self, 
                     example: TrainingExample,
                     agi_state: Optional[Dict] = None) -> float:
        """
        单次训练
        
        参数:
            example: 训练样本
            agi_state: AGI系统状态（可选）
            
        返回:
            loss: 损失值
        """
        # 前向传播
        outputs = self.model.predict(example.inputs)
        
        # 计算SEGUE损失
        loss = self.segue_loss(outputs, example.target, agi_state)
        
        # 反向传播（简化：只更新最后一层）
        if hasattr(self.model, 'train_single'):
            # 如果模型有train_single方法，使用它
            model_loss = self.model.train_single(
                example.inputs, example.target, self.learning_rate
            )
            # 使用SEGUE损失替代原始损失
            loss = self.segue_loss(outputs, example.target, agi_state)
        else:
            # 否则，使用简单梯度下降（假设模型有layers属性）
            if hasattr(self.model, 'layers'):
                output_gradients = [(o - t) for o, t in zip(outputs, example.target)]
                
                last_layer = self.model.layers[-1]
                for i, neuron in enumerate(last_layer.neurons):
                    if i < len(output_gradients):
                        neuron.update_weights(output_gradients[i], self.learning_rate)
                        
        return loss
    
    def train(self, 
                training_data: List[TrainingExample],
                agi_state: Optional[Dict] = None,
                verbose: bool = False) -> List[float]:
        """
        批量训练
        
        参数:
            training_data: 训练数据列表
            agi_state: AGI系统状态（可选）
            verbose: 是否打印训练过程
            
        返回:
            epoch_losses: 每轮的平均损失列表
        """
        epoch_losses = []
        
        for epoch in range(self.epochs):
            total_loss = 0.0
            
            for example in training_data:
                loss = self.train_single(example, agi_state)
                total_loss += loss
                
            avg_loss = total_loss / len(training_data)
            epoch_losses.append(avg_loss)
            
            # 记录训练历史
            self.training_history.append({
                'epoch': epoch,
                'avg_loss': avg_loss,
                'timestamp': time.time()
            })
            
            if verbose:
                print(f"Epoch {epoch+1}/{self.epochs}, Loss: {avg_loss:.6f}")
                
        return epoch_losses
    
    def evaluate(self, 
                test_data: List[TrainingExample]) -> float:
        """
        评估模型
        
        参数:
            test_data: 测试数据列表
            
        返回:
            avg_loss: 平均损失
        """
        total_loss = 0.0
        
        for example in test_data:
            outputs = self.model.predict(example.inputs)
            loss = self.segue_loss(outputs, example.target)
            total_loss += loss
            
        avg_loss = total_loss / len(test_data)
        
        return avg_loss
    
    def get_training_status(self) -> Dict:
        """
        获取训练状态
        
        返回:
            status: 训练状态信息
        """
        return {
            'epochs_trained': len(self.training_history),
            'latest_loss': self.training_history[-1]['avg_loss'] if self.training_history else None,
            'segue_loss_history_length': len(self.segue_loss_history),
            'model_type': type(self.model).__name__
        }


# ==================== 测试函数 ====================

def test_agi_trainer():
    """测试AGI训练器"""
    print("=" * 60)
    print("测试 AGI训练器 - 基于SEGUE损失函数")
    print("=" * 60)
    
    # 1. 创建模型（使用NeuralNetwork）
    try:
        from neural_network import NeuralNetwork
        
        # 创建神经网络：输入3维，隐藏层5维，输出2维
        model = NeuralNetwork(
            layer_sizes=[3, 5, 2],
            activations=["relu", "sigmoid"]
        )
        print("\n1. 创建模型完成")
        print(f"  层数: {len(model.layers)}")
        print(f"  层大小: {model.layer_sizes}")
        
    except ImportError:
        print("\n1. 无法导入NeuralNetwork，使用模拟模型")
        model = None
        
    # 2. 创建训练器
    print("\n2. 创建AGI训练器")
    trainer = AGITrainer(
        model=model,
        learning_rate=0.1,
        epochs=10
    )
    print(f"  学习率: {trainer.learning_rate}")
    print(f"  训练轮数: {trainer.epochs}")
    
    # 3. 创建训练数据
    print("\n3. 创建训练数据")
    training_data = []
    for i in range(20):
        inputs = [random.uniform(-1, 1) for _ in range(3)]
        target = [1.0 if inputs[0] > 0 else 0.0, 0.5]
        example = TrainingExample(inputs=inputs, target=target)
        training_data.append(example)
        
    print(f"  训练样本数: {len(training_data)}")
    
    # 4. 训练模型
    print("\n4. 训练模型（基于SEGUE损失函数）")
    if model:
        epoch_losses = trainer.train(
            training_data=training_data,
            agi_state=None,  # 暂时不提供AGI状态
            verbose=True
        )
        
        print(f"\n  最终损失: {epoch_losses[-1]:.6f}")
        print(f"  损失减少: {epoch_losses[0] - epoch_losses[-1]:.6f}")
        
    # 5. 获取训练状态
    print("\n5. 获取训练状态")
    status = trainer.get_training_status()
    print(f"  已训练轮数: {status['epochs_trained']}")
    print(f"  最新损失: {status['latest_loss']:.6f}")
    print(f"  模型类型: {status['model_type']}")
    
    print("\n" + "=" * 60)
    print("AGI训练器测试完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # 运行测试
    test_agi_trainer()
