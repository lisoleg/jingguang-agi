#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UFO² (Windows AgentOS) 集成模块
为统一复合体AGI系统提供视觉感知层

功能：
1. 屏幕捕获和图像采集
2. UI元素识别和定位
3. GUI操作执行（点击、输入、滚动等）
4. 视觉问答（VQA）接口
5. 与统一AGI系统的集成

基于微软UFO²论文和Windows AgentOS架构
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import base64
from PIL import ImageGrab, Image
import io


class UIElementType(Enum):
    """UI元素类型"""
    BUTTON = "button"
    TEXTBOX = "textbox"
    COMBOBOX = "combobox"
    CHECKBOX = "checkbox"
    RADIOBUTTON = "radiobutton"
    LISTVIEW = "listview"
    MENU = "menu"
    TAB = "tab"
    SCROLLBAR = "scrollbar"
    WINDOW = "window"
    UNKNOWN = "unknown"


class GUIActionType(Enum):
    """GUI操作类型"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE_TEXT = "type_text"
    PRESS_KEY = "press_key"
    SCROLL = "scroll"
    DRAG = "drag"
    SELECT = "select"
    HOVER = "hover"


@dataclass
class UIElement:
    """UI元素"""
    element_id: str
    element_type: UIElementType
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    text: str = ""
    name: str = ""
    enabled: bool = True
    visible: bool = True
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'element_id': self.element_id,
            'element_type': self.element_type.value,
            'bbox': self.bbox,
            'text': self.text,
            'name': self.name,
            'enabled': self.enabled,
            'visible': self.visible,
            'confidence': self.confidence
        }


@dataclass
class GUIAction:
    """GUI操作"""
    action_type: GUIActionType
    element_id: Optional[str] = None
    bbox: Optional[Tuple[int, int, int, int]] = None
    text: Optional[str] = None
    key: Optional[str] = None
    scroll_amount: Optional[int] = None
    duration: float = 0.1
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'action_type': self.action_type.value,
            'element_id': self.element_id,
            'bbox': self.bbox,
            'text': self.text,
            'key': self.key,
            'scroll_amount': self.scroll_amount,
            'duration': self.duration
        }


class UFOScreenCapture:
    """UFO²屏幕捕获模块"""
    
    def __init__(self, scale_factor: float = 1.0):
        """
        初始化屏幕捕获模块
        
        参数:
            scale_factor: 图像缩放因子
        """
        self.scale_factor = scale_factor
        self.capture_history: List[np.ndarray] = []
        self.max_history = 10
        
    def capture_screen(self, 
                      region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        捕获屏幕
        
        参数:
            region: 捕获区域 (x1, y1, x2, y2)，None表示全屏
            
        返回:
            screenshot: 屏幕截图 (numpy array, RGB)
        """
        # 使用PIL捕获屏幕
        pil_image = ImageGrab.grab(bbox=region)
        
        # 转换为numpy array
        screenshot = np.array(pil_image)
        
        # 转换为RGB（PIL默认是BGR）
        screenshot = screenshot[..., ::-1].copy()
        
        # 缩放
        if self.scale_factor != 1.0:
            from PIL import Image as PILImage
            pil_img = PILImage.fromarray(screenshot)
            new_size = (
                int(pil_img.width * self.scale_factor),
                int(pil_img.height * self.scale_factor)
            )
            pil_img = pil_img.resize(new_size, PILImage.LANCZOS)
            screenshot = np.array(pil_img)[..., ::-1].copy()
            
        # 保存到历史
        self.capture_history.append(screenshot)
        if len(self.capture_history) > self.max_history:
            self.capture_history.pop(0)
            
        return screenshot
    
    def capture_window(self, window_title: str) -> Optional[np.ndarray]:
        """
        捕获特定窗口
        
        参数:
            window_title: 窗口标题
            
        返回:
            screenshot: 窗口截图，如果未找到窗口则返回None
        """
        # 简化版：使用pywin32或ctypes查找窗口
        # 这里使用简化实现
        try:
            import win32gui
            
            def enum_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        rect = win32gui.GetWindowRect(hwnd)
                        results.append((hwnd, title, rect))
                return True
            
            results = []
            win32gui.EnumWindows(enum_callback, results)
            
            if results:
                hwnd, title, rect = results[0]
                x1, y1, x2, y2 = rect
                region = (x1, y1, x2, y2)
                return self.capture_screen(region=region)
            else:
                return None
                
        except ImportError:
            print("警告: 需要安装pywin32才能捕获特定窗口")
            return None
    
    def image_to_base64(self, image: np.ndarray) -> str:
        """
        将图像转换为base64编码
        
        参数:
            image: 图像数组
            
        返回:
            base64_str: base64编码字符串
        """
        pil_image = Image.fromarray(image[..., ::-1].copy())
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return base64_str
    
    def save_screenshot(self, 
                       image: np.ndarray, 
                       filepath: str):
        """
        保存截图
        
        参数:
            image: 图像数组
            filepath: 文件路径
        """
        pil_image = Image.fromarray(image[..., ::-1].copy())
        pil_image.save(filepath)
        print(f"✓ 截图已保存: {filepath}")


class UFOUIElementDetector:
    """UFO² UI元素检测器"""
    
    def __init__(self, 
                 confidence_threshold: float = 0.5):
        """
        初始化UI元素检测器
        
        参数:
            confidence_threshold: 置信度阈值
        """
        self.confidence_threshold = confidence_threshold
        self.detection_history: List[List[UIElement]] = []
        
    def detect_ui_elements(self, 
                          screenshot: np.ndarray) -> List[UIElement]:
        """
        检测UI元素
        
        参数:
            screenshot: 屏幕截图
            
        返回:
            elements: UI元素列表
        """
        # 简化版：使用模板匹配或OCR
        # 完整实现需要使用深度学习模型（如YOLO、Faster R-CNN）
        
        elements = []
        
        # 模拟检测：在实际应用中，这里应该调用UFO²的检测模型
        # 这里返回模拟数据
        
        # 模拟按钮
        elements.append(UIElement(
            element_id='btn_1',
            element_type=UIElementType.BUTTON,
            bbox=(100, 100, 200, 150),
            text='确定',
            name='Button_OK',
            confidence=0.95
        ))
        
        # 模拟文本框
        elements.append(UIElement(
            element_id='txt_1',
            element_type=UIElementType.TEXTBOX,
            bbox=(100, 200, 400, 250),
            text='',
            name='TextBox_Input',
            confidence=0.90
        ))
        
        # 保存到历史
        self.detection_history.append(elements)
        if len(self.detection_history) > 10:
            self.detection_history.pop(0)
            
        return elements
    
    def find_element_by_text(self, 
                             elements: List[UIElement], 
                             text: str) -> Optional[UIElement]:
        """
        根据文本查找UI元素
        
        参数:
            elements: UI元素列表
            text: 要查找的文本
            
        返回:
            element: 找到的UI元素，如果未找到则返回None
        """
        for element in elements:
            if text.lower() in element.text.lower() or text.lower() in element.name.lower():
                return element
        return None
    
    def find_element_by_type(self, 
                             elements: List[UIElement], 
                             element_type: UIElementType) -> List[UIElement]:
        """
        根据类型查找UI元素
        
        参数:
            elements: UI元素列表
            element_type: UI元素类型
            
        返回:
            filtered: 符合条件的UI元素列表
        """
        return [e for e in elements if e.element_type == element_type]
    
    def visualize_detection(self, 
                            screenshot: np.ndarray, 
                            elements: List[UIElement]) -> np.ndarray:
        """
        可视化UI元素检测结果
        
        参数:
            screenshot: 屏幕截图
            elements: UI元素列表
            
        返回:
            visualized: 可视化后的图像
        """
        import cv2
        
        visualized = screenshot.copy()
        
        for element in elements:
            x1, y1, x2, y2 = element.bbox
            
            # 绘制边界框
            cv2.rectangle(visualized, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{element.element_type.value}: {element.text or element.name}"
            cv2.putText(visualized, label, (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
        return visualized


class UFOGUIExecutor:
    """UFO² GUI执行器"""
    
    def __init__(self, 
                 safety_level: str = "medium"):
        """
        初始化GUI执行器
        
        参数:
            safety_level: 安全级别 ("low", "medium", "high")
        """
        self.safety_level = safety_level
        self.execution_history: List[Dict] = []
        
    def execute_action(self, 
                      action: GUIAction, 
                      screenshot: Optional[np.ndarray] = None) -> Dict:
        """
        执行GUI操作
        
        参数:
            action: GUI操作
            screenshot: 当前屏幕截图（可选）
            
        返回:
            result: 执行结果
        """
        import pyautogui
        
        result = {
            'action': action.to_dict(),
            'success': False,
            'message': '',
            'timestamp': time.time()
        }
        
        try:
            if action.action_type == GUIActionType.CLICK:
                if action.bbox:
                    x = (action.bbox[0] + action.bbox[2]) // 2
                    y = (action.bbox[1] + action.bbox[3]) // 2
                    pyautogui.click(x, y, duration=action.duration)
                    result['success'] = True
                    result['message'] = f'点击坐标 ({x}, {y})'
                    
            elif action.action_type == GUIActionType.DOUBLE_CLICK:
                if action.bbox:
                    x = (action.bbox[0] + action.bbox[2]) // 2
                    y = (action.bbox[1] + action.bbox[3]) // 2
                    pyautogui.doubleClick(x, y, duration=action.duration)
                    result['success'] = True
                    result['message'] = f'双击坐标 ({x}, {y})'
                    
            elif action.action_type == GUIActionType.TYPE_TEXT:
                if action.text:
                    pyautogui.write(action.text, interval=0.05)
                    result['success'] = True
                    result['message'] = f'输入文本: {action.text}'
                    
            elif action.action_type == GUIActionType.PRESS_KEY:
                if action.key:
                    pyautogui.press(action.key)
                    result['success'] = True
                    result['message'] = f'按键: {action.key}'
                    
            elif action.action_type == GUIActionType.SCROLL:
                if action.scroll_amount:
                    pyautogui.scroll(action.scroll_amount)
                    result['success'] = True
                    result['message'] = f'滚动: {action.scroll_amount}'
                    
            # 其他操作类型...
            
            # 保存到历史
            self.execution_history.append(result)
            if len(self.execution_history) > 50:
                self.execution_history.pop(0)
                
        except Exception as e:
            result['message'] = f'执行失败: {str(e)}'
            
        return result
    
    def execute_action_sequence(self, 
                                actions: List[GUIAction]) -> List[Dict]:
        """
        执行GUI操作序列
        
        参数:
            actions: GUI操作列表
            
        返回:
            results: 执行结果列表
        """
        results = []
        
        for i, action in enumerate(actions):
            print(f"执行操作 {i+1}/{len(actions)}: {action.action_type.value}")
            result = self.execute_action(action)
            results.append(result)
            
            if not result['success']:
                print(f"  ✗ 操作失败: {result['message']}")
                break
            else:
                print(f"  ✓ {result['message']}")
                
        return results


class UFOVisualPerceptionModule:
    """UFO²视觉感知模块（完整集成）"""
    
    def __init__(self, 
                 enable_screen_capture: bool = True,
                 enable_ui_detection: bool = True,
                 enable_gui_execution: bool = True):
        """
        初始化视觉感知模块
        
        参数:
            enable_screen_capture: 是否启用屏幕捕获
            enable_ui_detection: 是否启用UI元素检测
            enable_gui_execution: 是否启用GUI操作执行
        """
        self.enable_screen_capture = enable_screen_capture
        self.enable_ui_detection = enable_ui_detection
        self.enable_gui_execution = enable_gui_execution
        
        # 初始化子模块
        if self.enable_screen_capture:
            self.screen_capture = UFOScreenCapture()
            
        if self.enable_ui_detection:
            self.ui_detector = UFOUIElementDetector()
            
        if self.enable_gui_execution:
            self.gui_executor = UFOGUIExecutor()
            
        # 状态
        self.current_screenshot: Optional[np.ndarray] = None
        self.current_elements: List[UIElement] = []
        
    def perceive(self, 
                 capture_new: bool = True) -> Dict:
        """
        执行感知（主接口）
        
        参数:
            capture_new: 是否捕获新屏幕截图
            
        返回:
            perception_result: 感知结果
        """
        result = {
            'timestamp': time.time(),
            'screenshot': None,
            'ui_elements': [],
            'success': False
        }
        
        try:
            # 1. 屏幕捕获
            if self.enable_screen_capture and capture_new:
                self.current_screenshot = self.screen_capture.capture_screen()
                result['screenshot'] = self.current_screenshot
                
            # 2. UI元素检测
            if self.enable_ui_detection and self.current_screenshot is not None:
                self.current_elements = self.ui_detector.detect_ui_elements(
                    self.current_screenshot
                )
                result['ui_elements'] = [e.to_dict() for e in self.current_elements]
                
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def execute_gui_action(self, 
                          action: GUIAction) -> Dict:
        """
        执行GUI操作
        
        参数:
            action: GUI操作
            
        返回:
            result: 执行结果
        """
        if not self.enable_gui_execution:
            return {'success': False, 'message': 'GUI执行器未启用'}
            
        return self.gui_executor.execute_action(
            action, 
            screenshot=self.current_screenshot
        )
    
    def answer_visual_question(self, 
                               question: str, 
                               screenshot: Optional[np.ndarray] = None) -> str:
        """
        回答视觉问题（VQA）
        
        参数:
            question: 问题
            screenshot: 屏幕截图（可选，如果为None则使用当前截图）
            
        返回:
            answer: 答案
        """
        # 简化版：在实际应用中，这里应该调用多模态LLM（如Qwen-VL）
        
        if screenshot is None:
            if self.current_screenshot is None:
                self.perceive(capture_new=True)
            screenshot = self.current_screenshot
            
        # 模拟VQA
        # 在实际应用中，这里应该：
        # 1. 将screenshot转换为base64
        # 2. 调用Qwen-VL API
        # 3. 返回答案
        
        answer = f"[模拟VQA] 问题: {question}\n"
        answer += "答案: 需要集成Qwen-VL多模态模型才能回答视觉问题。"
        
        return answer
    
    def get_module_status(self) -> Dict:
        """获取模块状态"""
        return {
            'enable_screen_capture': self.enable_screen_capture,
            'enable_ui_detection': self.enable_ui_detection,
            'enable_gui_execution': self.enable_gui_execution,
            'has_screenshot': self.current_screenshot is not None,
            'ui_element_count': len(self.current_elements)
        }


# ==================== 测试函数 ====================

def test_ufo2_integration():
    """测试UFO²集成模块"""
    print("=" * 60)
    print("测试 UFO² (Windows AgentOS) 集成模块")
    print("=" * 60)
    
    # 1. 创建视觉感知模块
    print("\n1. 创建视觉感知模块")
    perception = UFOVisualPerceptionModule(
        enable_screen_capture=True,
        enable_ui_detection=True,
        enable_gui_execution=False  # 测试时不执行GUI操作
    )
    print(f"  ✓ 模块创建完成")
    print(f"  屏幕捕获: {perception.enable_screen_capture}")
    print(f"  UI检测: {perception.enable_ui_detection}")
    print(f"  GUI执行: {perception.enable_gui_execution}")
    
    # 2. 执行感知
    print("\n2. 执行感知（屏幕捕获 + UI元素检测）")
    try:
        result = perception.perceive(capture_new=True)
        if result['success']:
            print(f"  ✓ 感知成功")
            print(f"  截图形状: {result['screenshot'].shape}")
            print(f"  UI元素数量: {len(result['ui_elements'])}")
        else:
            print(f"  ✗ 感知失败: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ✗ 感知失败: {e}")
    
    # 3. 测试UI元素检测
    print("\n3. 测试UI元素检测")
    if perception.current_elements:
        for i, element in enumerate(perception.current_elements[:3]):
            print(f"  元素{i+1}: {element.element_type.value} - {element.text or element.name}")
    
    # 4. 测试VQA
    print("\n4. 测试视觉问答（VQA）")
    answer = perception.answer_visual_question("屏幕上有什么按钮？")
    print(f"  问题: 屏幕上有什么按钮？")
    print(f"  答案: {answer[:100]}...")
    
    # 5. 获取模块状态
    print("\n5. 获取模块状态")
    status = perception.get_module_status()
    print(f"  模块状态: {status}")
    
    print("\n" + "=" * 60)
    print("UFO²集成模块测试完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # 运行测试
    test_ufo2_integration()
