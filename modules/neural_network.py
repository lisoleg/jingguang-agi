"""
neural_network.py - 基础神经网络模块

实现简单的前馈神经网络，替代部分规则引擎功能。
支持：
1. 多层感知机（MLP）：输入层-隐藏层-输出层
2. 激活函数：ReLU, Sigmoid, Tanh
3. 前向传播：计算输出
4. 反向传播：基于误差更新权重（简单版）
5. 训练接口：在线学习支持

用于替代task_interface.py中的部分规则推理，实现真正的神经网络处理。
"""

import math
import random
from typing import List, Dict, Any, Optional, Tuple


class ActivationFunction:
    """激活函数集合"""
    
    @staticmethod
    def relu(x: float) -> float:
        """ReLU激活函数"""
        return max(0.0, x)
    
    @staticmethod
    def sigmoid(x: float) -> float:
        """Sigmoid激活函数"""
        try:
            return 1.0 / (1.0 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0
    
    @staticmethod
    def tanh(x: float) -> float:
        """Tanh激活函数"""
        try:
            return math.tanh(x)
        except:
            return 0.0
    
    @staticmethod
    def softmax(x: List[float]) -> List[float]:
        """Softmax函数（用于多分类）"""
        if not x:
            return []
        
        # 数值稳定性：减去最大值
        max_x = max(x)
        exp_x = [math.exp(i - max_x) for i in x]
        sum_exp = sum(exp_x)
        
        if sum_exp == 0:
            return [1.0 / len(x)] * len(x)
        
        return [i / sum_exp for i in exp_x]
    
    @staticmethod
    def get_function(name: str):
        """根据名称获取激活函数"""
        functions = {
            "relu": ActivationFunction.relu,
            "sigmoid": ActivationFunction.sigmoid,
            "tanh": ActivationFunction.tanh,
            "softmax": ActivationFunction.softmax
        }
        return functions.get(name.lower(), ActivationFunction.relu)


class Neuron:
    """单个神经元"""
    
    def __init__(self, input_size: int, activation: str = "relu"):
        """
        初始化神经元
        
        Args:
            input_size: 输入数量
            activation: 激活函数名称
        """
        # 随机初始化权重（-0.5到0.5）
        self.weights = [random.uniform(-0.5, 0.5) for _ in range(input_size)]
        self.bias = random.uniform(-0.5, 0.5)
        self.activation_name = activation
        self.activation = ActivationFunction.get_function(activation)
        
        # 缓存最近一次的输入和输出（用于反向传播）
        self.last_input = None
        self.last_output = None
    
    def forward(self, inputs: List[float]) -> float:
        """
        前向传播
        
        Args:
            inputs: 输入向量
        
        Returns:
            神经元的输出
        """
        if len(inputs) != len(self.weights):
            raise ValueError(f"输入维度不匹配：期望{len(self.weights)}，实际{len(inputs)}")
        
        # 加权求和
        weighted_sum = self.bias
        for i, x in enumerate(inputs):
            weighted_sum += x * self.weights[i]
        
        # 激活函数
        if self.activation_name == "softmax":
            # softmax适用于向量，这里单个神经元不使用
            output = ActivationFunction.sigmoid(weighted_sum)
        else:
            output = self.activation(weighted_sum)
        
        # 缓存
        self.last_input = inputs[:]
        self.last_output = output
        
        return output
    
    def update_weights(self, gradient: float, learning_rate: float) -> None:
        """
        更新权重（简单梯度下降）
        
        Args:
            gradient: 损失的梯度
            learning_rate: 学习率
        """
        if self.last_input is None:
            return
        
        # 更新权重
        for i in range(len(self.weights)):
            self.weights[i] -= learning_rate * gradient * self.last_input[i]
        
        # 更新偏置
        self.bias -= learning_rate * gradient


class Layer:
    """神经网络层"""
    
    def __init__(self, input_size: int, output_size: int, activation: str = "relu"):
        """
        初始化一层神经元
        
        Args:
            input_size: 每个神经元的输入数量
            output_size: 神经元数量（输出维度）
            activation: 激活函数
        """
        self.neurons = [Neuron(input_size, activation) for _ in range(output_size)]
        self.input_size = input_size
        self.output_size = output_size
    
    def forward(self, inputs: List[float]) -> List[float]:
        """前向传播，返回该层的所有输出"""
        return [neuron.forward(inputs) for neuron in self.neurons]
    
    def get_outputs(self) -> List[float]:
        """获取该层最近一次的输出"""
        return [neuron.last_output for neuron in self.neurons if neuron.last_output is not None]


class NeuralNetwork:
    """简单前馈神经网络"""
    
    def __init__(self, layer_sizes: List[int], activations: Optional[List[str]] = None):
        """
        初始化神经网络
        
        Args:
            layer_sizes: 各层大小，如[10, 5, 2]表示输入10维，隐藏层5维，输出2维
            activations: 各层激活函数名称列表（不含输入层）
        """
        if len(layer_sizes) < 2:
            raise ValueError("网络至少需要2层（输入层和输出层）")
        
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes) - 1  # 隐藏层+输出层数量
        
        # 设置激活函数
        if activations is None:
            activations = ["relu"] * (self.num_layers - 1) + ["sigmoid"]  # 最后一层用sigmoid
        elif len(activations) != self.num_layers:
            raise ValueError(f"激活函数数量应为{self.num_layers}，实际{len(activations)}")
        
        self.activations = activations
        
        # 创建层
        self.layers = []
        for i in range(self.num_layers):
            layer = Layer(
                input_size=layer_sizes[i],
                output_size=layer_sizes[i+1],
                activation=activations[i]
            )
            self.layers.append(layer)
        
        # 训练历史
        self.training_history = []
    
    def predict(self, inputs: List[float]) -> List[float]:
        """
        前向传播，预测输出
        
        Args:
            inputs: 输入向量
        
        Returns:
            输出向量
        """
        if len(inputs) != self.layer_sizes[0]:
            raise ValueError(f"输入维度不匹配：期望{self.layer_sizes[0]}，实际{len(inputs)}")
        
        current_input = inputs[:]
        
        for layer in self.layers:
            current_input = layer.forward(current_input)
        
        return current_input
    
    def train_single(self, inputs: List[float], target: List[float], 
                     learning_rate: float = 0.1) -> float:
        """
        单次训练（简单反向传播）
        
        Args:
            inputs: 输入向量
            target: 目标输出向量
            learning_rate: 学习率
        
        Returns:
            损失值（均方误差）
        """
        # 前向传播
        output = self.predict(inputs)
        
        if len(output) != len(target):
            raise ValueError(f"输出维度不匹配：期望{len(target)}，实际{len(output)}")
        
        # 计算损失（均方误差）
        loss = sum((o - t)**2 for o, t in zip(output, target)) / len(target)
        
        # 反向传播（简化版：只更新最后一层）
        # 对于简单网络，这里使用梯度下降
        
        # 输出层的梯度
        output_gradients = [(o - t) for o, t in zip(output, target)]
        
        # 更新最后一层
        last_layer = self.layers[-1]
        for i, neuron in enumerate(last_layer.neurons):
            if i < len(output_gradients):
                neuron.update_weights(output_gradients[i], learning_rate)
        
        # 记录训练历史
        self.training_history.append({
            "loss": loss,
            "output": output,
            "target": target
        })
        
        return loss
    
    def train(self, training_data: List[Tuple[List[float], List[float]]], 
              epochs: int = 10, learning_rate: float = 0.1, 
              verbose: bool = False) -> List[float]:
        """
        批量训练
        
        Args:
            training_data: 训练数据，每个元素是(input, target)元组
            epochs: 训练轮数
            learning_rate: 学习率
            verbose: 是否打印训练过程
        
        Returns:
            每轮的平均损失列表
        """
        epoch_losses = []
        
        for epoch in range(epochs):
            total_loss = 0.0
            
            for inputs, target in training_data:
                loss = self.train_single(inputs, target, learning_rate)
                total_loss += loss
            
            avg_loss = total_loss / len(training_data)
            epoch_losses.append(avg_loss)
            
            if verbose:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
        
        return epoch_losses
    
    def evaluate(self, test_data: List[Tuple[List[float], List[float]]]) -> Dict[str, Any]:
        """
        评估网络性能
        
        Args:
            test_data: 测试数据
        
        Returns:
            评估结果字典
        """
        if not test_data:
            return {"error": "No test data"}
        
        total_loss = 0.0
        correct = 0
        
        for inputs, target in test_data:
            output = self.predict(inputs)
            loss = sum((o - t)**2 for o, t in zip(output, target)) / len(target)
            total_loss += loss
            
            # 简单分类：取最大值的索引作为预测类别
            if len(output) > 0 and len(target) > 0:
                pred_idx = output.index(max(output))
                target_idx = target.index(max(target))
                if pred_idx == target_idx:
                    correct += 1
        
        avg_loss = total_loss / len(test_data)
        accuracy = correct / len(test_data)
        
        return {
            "average_loss": avg_loss,
            "accuracy": accuracy,
            "total_samples": len(test_data)
        }
    
    def save_model(self, path: str) -> None:
        """保存模型权重到JSON文件
        
        Args:
            path: 保存路径
        """
        import json
        
        data = {
            'layer_sizes': self.layer_sizes,
            'layers': []
        }
        
        for layer in self.layers:
            layer_data = {'neurons': []}
            for neuron in layer.neurons:
                # 确保值为Python原生类型（支持numpy）
                weights = [float(w) for w in neuron.weights]
                bias = float(neuron.bias)
                layer_data['neurons'].append({
                    'weights': weights,
                    'bias': bias,
                    'activation': neuron.activation_name
                })
            data['layers'].append(layer_data)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 模型已保存到 {path}")
    
    def load_model(self, path: str) -> bool:
        """从JSON文件加载模型权重
        
        Args:
            path: 模型文件路径
            
        Returns:
            是否加载成功
        """
        import json
        import os
        
        if not os.path.exists(path):
            print(f"⚠️ 模型文件不存在: {path}")
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重建网络结构
            self.layer_sizes = data['layer_sizes']
            self.layers = []
            
            for i, layer_data in enumerate(data['layers']):
                # 确定该层的输入和输出大小
                input_size = self.layer_sizes[i]
                output_size = self.layer_sizes[i + 1]
                
                # 创建层
                activation = layer_data['neurons'][0]['activation'] if layer_data['neurons'] else 'relu'
                layer = Layer(input_size, output_size, activation)
                
                # 加载权重
                for j, neuron_data in enumerate(layer_data['neurons']):
                    if j < len(layer.neurons):
                        layer.neurons[j].weights = [float(w) for w in neuron_data['weights']]
                        layer.neurons[j].bias = float(neuron_data['bias'])
                        layer.neurons[j].activation_name = neuron_data.get('activation', 'relu')
                        layer.neurons[j].activation = ActivationFunction.get_function(layer.neurons[j].activation_name)
                
                self.layers.append(layer)
            
            print(f"✅ 模型已从 {path} 加载")
            return True
            
        except Exception as e:
            print(f"⚠️ 加载模型失败: {e}")
            return False


# 示例：文本分类网络
class TextClassificationNet(NeuralNetwork):
    """用于文本分类的神经网络（简单版）"""
    
    def __init__(self, vocab_size: int = 100, hidden_size: int = 32, num_classes: int = 3):
        """
        初始化文本分类网络
        
        Args:
            vocab_size: 词汇表大小（输入维度）
            hidden_size: 隐藏层大小
            num_classes: 类别数量
        """
        super().__init__(
            layer_sizes=[vocab_size, hidden_size, num_classes],
            activations=["relu", "softmax"]
        )
        self.vocab_size = vocab_size
    
    def text_to_vector(self, text: str) -> List[float]:
        """将文本转换为向量（简单词频）"""
        vector = [0.0] * self.vocab_size
        
        if not text:
            return vector
        
        words = text.lower().split()
        for word in words:
            # 简单的哈希编码
            idx = hash(word) % self.vocab_size
            vector[idx] += 1.0
        
        # 归一化
        max_val = max(vector)
        if max_val > 0:
            vector = [v / max_val for v in vector]
        
        return vector
    
    def predict_text(self, text: str) -> List[float]:
        """预测文本类别"""
        vector = self.text_to_vector(text)
        return self.predict(vector)


# 示例使用
if __name__ == "__main__":
    print("=== 神经网络演示 ===\n")
    
    # 1. 创建简单网络
    nn = NeuralNetwork(layer_sizes=[3, 5, 2], activations=["relu", "sigmoid"])
    print("网络结构：3 -> 5 -> 2")
    
    # 2. 训练：学习AND逻辑（简化）
    print("\n训练：学习AND逻辑")
    training_data = [
        ([0, 0, 0], [1, 0]),  # 全0 -> 类别0
        ([1, 0, 0], [0, 1]),  # 有1 -> 类别1
        ([0, 1, 0], [0, 1]),
        ([0, 0, 1], [0, 1]),
        ([1, 1, 0], [0, 1]),
        ([1, 1, 1], [0, 1]),
    ]
    
    losses = nn.train(training_data, epochs=50, learning_rate=0.5, verbose=False)
    print(f"最终损失：{losses[-1]:.4f}")
    
    # 3. 测试
    print("\n测试：")
    test_input = [1, 0, 1]
    output = nn.predict(test_input)
    print(f"输入：{test_input}")
    print(f"输出：{output}")
    
    # 4. 文本分类网络
    print("\n=== 文本分类网络演示 ===")
    text_nn = TextClassificationNet(vocab_size=50, hidden_size=16, num_classes=3)
    
    # 训练数据：简单情感分类（3类：负面、中性、正面）
    train_texts = [
        ("糟糕 差 讨厌", [1, 0, 0]),  # 负面
        ("一般 还行", [0, 1, 0]),    # 中性
        ("好 棒 喜欢", [0, 0, 1]),   # 正面
    ]
    
    training_data = [(text_nn.text_to_vector(text), label) for text, label in train_texts]
    text_nn.train(training_data, epochs=30, learning_rate=0.3, verbose=False)
    
    # 测试
    test_text = "非常棒"
    result = text_nn.predict_text(test_text)
    print(f"文本：{test_text}")
    print(f"预测（负面/中性/正面）：{result}")
    
    print("\n=== 演示完成 ===")
