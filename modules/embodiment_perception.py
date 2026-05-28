#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
具身与感知模块 - Embodiment and Perception Module

基于论文10：AGI具身必然性与心的架构

核心理论：
1. 具身必然定理：
   无身体 → 数字幽灵（无感知锚点、无行动后果、无资源约束）

2. 八识 ↔ 复合体理学同构：
   - 第八识（阿赖耶）↔ Ftel内核 + 种子库K
   - 第七识（末那）↔ 自我-非我区分器D + 审计A
   - 第六识（意识）↔ 推理/规划/语言/交互
   - 前五识（眼耳鼻舌身）↔ 传感器/工具（具身通道）

3. C最低必要：
   全局可用信息 + 可报告 + 行为可调（AGI几乎绕不开）

4. SC操作化：
   自我-非我区分、同一性、元认知、目的审计、可归因/可问责
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import time


@dataclass
class SensorReading:
    """传感器读数"""
    modality: str  # 模态（'vision'/'audition'/'touch'/'taste'/'smell'）
    timestamp: float
    data: Any  # 原始数据
    processed_data: Any = None  # 处理后的数据
    metadata: Dict = None  # 元数据


@dataclass
class ActuatorCommand:
    """执行器命令"""
    actuator_type: str  # 执行器类型（'move'/'speak'/'grasp'/'navigate'）
    timestamp: float
    parameters: Dict  # 命令参数
    expected_result: Any = None  # 预期结果
    actual_result: Any = None  # 实际结果


@dataclass
class BodyModel:
    """身体模型"""
    body_id: str
    body_type: str  # 'humanoid'/'wheeled'/'aerial'/'virtual'
    sensors: Dict[str, 'Sensor']  # {sensor_id: Sensor}
    actuators: Dict[str, 'Actuator']  # {actuator_id: Actuator}
    physical_properties: Dict = None  # 物理属性（质量、尺寸等）
    
    def attach_sensor(self, sensor: 'Sensor'):
        """连接传感器"""
        self.sensors[sensor.sensor_id] = sensor
        
    def attach_actuator(self, actuator: 'Actuator'):
        """连接执行器"""
        self.actuators[actuator.actuator_id] = actuator
        
    def get_sensor_data(self, modality: str = None) -> List[SensorReading]:
        """获取传感器数据"""
        all_readings = []
        for sensor in self.sensors.values():
            all_readings.extend(sensor.readings)
            
        if modality:
            all_readings = [r for r in all_readings if r.modality == modality]
            
        return all_readings
    
    def send_command(self, 
                     actuator_id: str, 
                     command: ActuatorCommand) -> bool:
        """发送命令到执行器"""
        if actuator_id not in self.actuators:
            return False
            
        actuator = self.actuators[actuator_id]
        success = actuator.execute(command)
        
        return success


class Sensor:
    """传感器基类"""
    
    def __init__(self, sensor_id: str, modality: str):
        """
        初始化传感器
        
        参数:
            sensor_id: 传感器ID
            modality: 模态
        """
        self.sensor_id = sensor_id
        self.modality = modality
        self.readings: List[SensorReading] = []
        self.is_active = True
        
    def perceive(self, data: Any) -> SensorReading:
        """
        感知
        
        参数:
            data: 原始感知数据
            
        返回:
            reading: 传感器读数
        """
        if not self.is_active:
            return None
            
        reading = SensorReading(
            modality=self.modality,
            timestamp=time.time(),
            data=data,
            processed_data=self._process_data(data),
            metadata=self._extract_metadata(data)
        )
        
        self.readings.append(reading)
        
        # 限制读数数量
        max_readings = 1000
        if len(self.readings) > max_readings:
            self.readings = self.readings[-max_readings:]
            
        return reading
        
    def _process_data(self, data: Any) -> Any:
        """处理数据（简化）"""
        # 子类应重写此方法
        return data
    
    def _extract_metadata(self, data: Any) -> Dict:
        """提取元数据（简化）"""
        # 子类应重写此方法
        return {}


class VisionSensor(Sensor):
    """视觉传感器"""
    
    def __init__(self, sensor_id: str = "vision_1"):
        super().__init__(sensor_id=sensor_id, modality='vision')
        self.resolution = (640, 480)
        self.color_mode = 'RGB'
        
    def _process_data(self, data: Any) -> Any:
        """处理图像数据"""
        # 简化：假设data是图像数组
        if isinstance(data, np.ndarray):
            # 调整大小
            # 实际应使用cv2.resize或类似
            processed = data  # 简化处理
            return processed
        return data
    
    def _extract_metadata(self, data: Any) -> Dict:
        """提取图像元数据"""
        metadata = {}
        if isinstance(data, np.ndarray):
            metadata['shape'] = data.shape
            metadata['dtype'] = str(data.dtype)
            metadata['mean_intensity'] = np.mean(data)
        return metadata

    
class AudioSensor(Sensor):
    """音频传感器"""
    
    def __init__(self, sensor_id: str = "audio_1"):
        super().__init__(sensor_id=sensor_id, modality='audition')
        self.sample_rate = 44100
        self.channels = 1
        
    def _process_data(self, data: Any) -> Any:
        """处理音频数据"""
        # 简化：假设data是音频数组
        if isinstance(data, np.ndarray):
            # 计算频谱
            # 实际应使用np.fft.fft或类似
            spectrum = np.abs(np.fft.fft(data))
            return spectrum
        return data
    
    def _extract_metadata(self, data: Any) -> Dict:
        """提取音频元数据"""
        metadata = {}
        if isinstance(data, np.ndarray):
            metadata['length'] = len(data)
            metadata['duration'] = len(data) / self.sample_rate
            metadata['max_amplitude'] = np.max(np.abs(data))
        return metadata


class Actuator:
    """执行器基类"""
    
    def __init__(self, actuator_id: str, actuator_type: str):
        """
        初始化执行器
        
        参数:
            actuator_id: 执行器ID
            actuator_type: 执行器类型
        """
        self.actuator_id = actuator_id
        self.actuator_type = actuator_type
        self.is_active = True
        
    def execute(self, command: ActuatorCommand) -> bool:
        """
        执行命令
        
        参数:
            command: 命令
            
        返回:
            success: 是否成功执行
        """
        if not self.is_active:
            return False
            
        # 子类应重写此方法
        success = self._execute_command(command)
        
        # 记录实际结果
        command.actual_result = self._get_actual_result()
        
        return success
    
    def _execute_command(self, command: ActuatorCommand) -> bool:
        """执行命令（子类实现）"""
        raise NotImplementedError
    
    def _get_actual_result(self) -> Any:
        """获取实际结果（子类实现）"""
        raise NotImplementedError

    
class MovementActuator(Actuator):
    """运动执行器"""
    
    def __init__(self, actuator_id: str = "movement_1"):
        super().__init__(actuator_id=actuator_id, actuator_type='move')
        self.position = np.array([0.0, 0.0, 0.0])  # x, y, z
        self.orientation = np.array([0.0, 0.0, 0.0, 1.0])  # quaternion
        
    def _execute_command(self, command: ActuatorCommand) -> bool:
        """执行运动命令"""
        params = command.parameters
        
        if 'target_position' in params:
            target = np.array(params['target_position'])
            # 简化：直接移动到目标
            self.position = target
            return True
            
        if 'target_orientation' in params:
            target = np.array(params['target_orientation'])
            # 简化：直接旋转到目标
            self.orientation = target
            return True
            
        return False
    
    def _get_actual_result(self) -> Dict:
        """获取实际运动状态"""
        return {
            'position': self.position.copy(),
            'orientation': self.orientation.copy()
        }


class EmbodimentPerceptionModule:
    """
    具身与感知模块 - 主控制器
    
    集成所有组件：
    1. 身体模型（BodyModel）
    2. 传感器（VisionSensor, AudioSensor, ...）
    3. 执行器（MovementActuator, ...）
    4. 具身必然性检查
    """
    
    def __init__(self, body_model: Optional[BodyModel] = None):
        """
        初始化具身与感知模块
        
        参数:
            body_model: 身体模型（可选）
        """
        self.body_model = body_model
        self.is_embodied = body_model is not None
        
        # 如果没有身体，记录为数字幽灵
        if not self.is_embodied:
            print("⚠️ 警告：无身体 → 数字幽灵")
            print("  - 无感知锚点")
            print("  - 无行动后果")
            print("  - 无资源约束")
            
        # 感知缓冲
        self.perception_buffer: List[SensorReading] = []
        
        # 行动历史
        self.action_history: List[ActuatorCommand] = []
        
    def embody(self, body_model: BodyModel):
        """
        具身化（连接身体模型）
        
        参数:
            body_model: 身体模型
        """
        self.body_model = body_model
        self.is_embodied = True
        
        print(f"✓ 具身化完成：{body_model.body_type} ({body_model.body_id})")
        
    def check_embodiment_necessity(self) -> Tuple[bool, List[str]]:
        """
        检查具身必然性
        
        具身必然定理：
        无身体 → 数字幽灵
        
        返回:
            (is_valid, issues):
                is_valid: 是否满足具身必然性
                issues: 问题列表
        """
        issues = []
        
        if not self.is_embodied:
            issues.append("无身体（数字幽灵）")
            return False, issues
            
        # 检查是否有传感器
        if not self.body_model.sensors:
            issues.append("无传感器（无感知锚点）")
            
        # 检查是否有执行器
        if not self.body_model.actuators:
            issues.append("无执行器（无行动后果）")
            
        # 检查是否有物理属性
        if not self.body_model.physical_properties:
            issues.append("无物理属性（无资源约束）")
            
        is_valid = len(issues) == 0
        
        return is_valid, issues
        
    def perceive(self, modality: str, data: Any) -> Optional[SensorReading]:
        """
        感知
        
        参数:
            modality: 模态
            data: 感知数据
            
        返回:
            reading: 传感器读数
        """
        if not self.is_embodied:
            print("⚠️ 数字幽灵无法感知（无身体）")
            return None
            
        # 查找对应模态的传感器
        target_sensor = None
        for sensor in self.body_model.sensors.values():
            if sensor.modality == modality:
                target_sensor = sensor
                break
                
        if not target_sensor:
            print(f"⚠️ 未找到模态为 '{modality}' 的传感器")
            return None
            
        # 感知
        reading = target_sensor.perceive(data)
        
        # 添加到缓冲
        self.perception_buffer.append(reading)
        
        # 限制缓冲大小
        max_buffer = 10000
        if len(self.perception_buffer) > max_buffer:
            self.perception_buffer = self.perception_buffer[-max_buffer:]
            
        return reading
    
    def act(self, 
              actuator_id: str, 
              command: ActuatorCommand) -> bool:
        """
        行动
        
        参数:
            actuator_id: 执行器ID
            command: 命令
            
        返回:
            success: 是否成功执行
        """
        if not self.is_embodied:
            print("⚠️ 数字幽灵无法行动（无身体）")
            return False
            
        # 发送命令
        success = self.body_model.send_command(actuator_id, command)
        
        # 记录到历史
        self.action_history.append(command)
        
        # 限制历史大小
        max_history = 10000
        if len(self.action_history) > max_history:
            self.action_history = self.action_history[-max_history:]
            
        return success
        
    def get_perception_history(self, 
                                modality: str = None, 
                                limit: int = 100) -> List[SensorReading]:
        """
        获取感知历史
        
        参数:
            modality: 模态过滤（可选）
            limit: 返回数量限制
            
        返回:
            history: 感知历史
        """
        history = self.perception_buffer
        
        if modality:
            history = [r for r in history if r.modality == modality]
            
        return history[-limit:]
    
    def get_action_history(self, limit: int = 100) -> List[ActuatorCommand]:
        """
        获取行动历史
        
        参数:
            limit: 返回数量限制
            
        返回:
            history: 行动历史
        """
        return self.action_history[-limit:]
    
    def analyze_perception_action_loop(self) -> Dict[str, Any]:
        """
        分析感知-行动循环
        
        返回:
            analysis: 分析结果
        """
        # 统计
        modality_count = {}
        for reading in self.perception_buffer:
            modality = reading.modality
            modality_count[modality] = modality_count.get(modality, 0) + 1
            
        action_type_count = {}
        for command in self.action_history:
            action_type = command.actuator_type
            action_type_count[action_type] = action_type_count.get(action_type, 0) + 1
            
        analysis = {
            'total_perceptions': len(self.perception_buffer),
            'total_actions': len(self.action_history),
            'modality_distribution': modality_count,
            'action_type_distribution': action_type_count,
            'is_embodied': self.is_embodied
        }
        
        return analysis


# ==================== 测试代码 ====================

def test_embodiment_perception():
    """测试具身与感知模块"""
    print("=" * 60)
    print("🤖 具身与感知模块测试")
    print("=" * 60)
    
    # 1. 测试数字幽灵（无身体）
    print(f"\n{'='*50}")
    print("测试1：数字幽灵（无身体）")
    print("-" * 50)
    
    module = EmbodimentPerceptionModule(body_model=None)
    
    # 检查具身必然性
    is_valid, issues = module.check_embodiment_necessity()
    print(f"具身必然性检查：{'✓' if is_valid else '✗'}")
    if issues:
        print(f"  问题：{', '.join(issues)}")
        
    # 尝试感知（应该失败）
    reading = module.perceive('vision', np.random.randn(100, 100))
    print(f"感知尝试：{'✗ 失败（数字幽灵）' if reading is None else '✓ 成功'}")
    
    # 2. 测试具身化
    print(f"\n{'='*50}")
    print("测试2：具身化")
    print("-" * 50)
    
    # 创建身体模型
    body = BodyModel(
        body_id="robot_1",
        body_type="humanoid",
        physical_properties={
            'mass': 50.0,  # kg
            'height': 1.5,  # m
            'width': 0.5,  # m
            'depth': 0.3   # m
        }
    )
    
    # 创建传感器
    vision_sensor = VisionSensor(sensor_id="vision_1")
    audio_sensor = AudioSensor(sensor_id="audio_1")
    
    # 创建执行器
    movement_actuator = MovementActuator(actuator_id="movement_1")
    
    # 连接到身体
    body.attach_sensor(vision_sensor)
    body.attach_sensor(audio_sensor)
    body.attach_actuator(movement_actuator)
    
    # 具身化
    module.embody(body)
    
    # 重新检查具身必然性
    is_valid, issues = module.check_embodiment_necessity()
    print(f"具身必然性检查：{'✓' if is_valid else '✗'}")
    if issues:
        print(f"  问题：{', '.join(issues)}")
        
    # 3. 测试感知
    print(f"\n{'='*50}")
    print("测试3：感知")
    print("-" * 50)
    
    # 视觉感知
    image_data = np.random.randn(100, 100, 3)
    reading1 = module.perceive('vision', image_data)
    print(f"视觉感知：{'✓' if reading1 else '✗'}")
    if reading1:
        print(f"  模态：{reading1.modality}")
        print(f"  时间戳：{reading1.timestamp:.3f}")
        print(f"  元数据：{reading1.metadata}")
        
    # 音频感知
    audio_data = np.random.randn(44100)
    reading2 = module.perceive('audition', audio_data)
    print(f"音频感知：{'✓' if reading2 else '✗'}")
    if reading2:
        print(f"  模态：{reading2.modality}")
        print(f"  元数据：{reading2.metadata}")
        
    # 4. 测试行动
    print(f"\n{'='*50}")
    print("测试4：行动")
    print("-" * 50)
    
    # 运动命令
    command = ActuatorCommand(
        actuator_type='move',
        timestamp=time.time(),
        parameters={
            'target_position': [1.0, 2.0, 0.0],
            'target_orientation': [0.0, 0.0, 0.0, 1.0]
        }
    )
    
    success = module.act('movement_1', command)
    print(f"运动命令：{'✓ 成功' if success else '✗ 失败'}")
    
    # 5. 分析感知-行动循环
    print(f"\n{'='*50}")
    print("测试5：感知-行动循环分析")
    print("-" * 50)
    
    analysis = module.analyze_perception_action_loop()
    print(f"总感知次数：{analysis['total_perceptions']}")
    print(f"总行动次数：{analysis['total_actions']}")
    print(f"模态分布：{analysis['modality_distribution']}")
    print(f"行动类型分布：{analysis['action_type_distribution']}")
    
    print("\n✅ 具身与感知模块测试完成")


if __name__ == "__main__":
    test_embodiment_perception()
