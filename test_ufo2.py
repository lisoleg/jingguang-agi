#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UFO² 具身执行层测试套件
测试太乙系统的桌面自动化能力

测试用例:
1. 截图功能
2. 桌面任务执行
3. 应用控制
4. UI 树获取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from taiyi_tools import get_tool_engine
from taiyi_embodiment import get_embodiment, UFO2Config


def test_screenshot():
    """测试截图功能"""
    print("\n" + "=" * 60)
    print("🧪 测试 1: UFO² 截图")
    print("=" * 60)
    
    engine = get_tool_engine()
    result = engine.execute('ufo2_capture', {'target': 'desktop'})
    
    print(f"成功: {result.success}")
    if result.success:
        img_size = len(str(result.output.get('image', '')))
        print(f"图片大小: {img_size:,} bytes")
        print(f"方法: {result.output.get('method', 'mss')}")
        return True
    else:
        print(f"错误: {result.error}")
        return False


def test_ui_tree():
    """测试 UI 树获取"""
    print("\n" + "=" * 60)
    print("🧪 测试 2: UFO² UI 树")
    print("=" * 60)
    
    engine = get_tool_engine()
    result = engine.execute('ufo2_ui_tree', {'app': ''})
    
    print(f"成功: {result.success}")
    if result.success:
        tree = result.output.get('tree', {})
        print(f"树结构: {tree.get('name', 'N/A')}")
        return True
    else:
        print(f"错误: {result.error}")
        return False


def test_app_control():
    """测试应用控制"""
    print("\n" + "=" * 60)
    print("🧪 测试 3: UFO² 应用控制")
    print("=" * 60)
    
    engine = get_tool_engine()
    
    # 测试获取桌面应用列表
    result = engine.execute('ufo2_app_control', {
        'app': 'system',
        'action': 'list_apps',
        'params': {}
    })
    
    print(f"成功: {result.success}")
    if result.success:
        apps = result.output.get('apps', [])
        print(f"应用数量: {len(apps)}")
        for app in apps[:5]:
            print(f"  - {app.get('name', 'N/A')}")
        return True
    else:
        print(f"错误: {result.error}")
        return False


def test_desktop_task():
    """测试桌面任务"""
    print("\n" + "=" * 60)
    print("🧪 测试 4: UFO² 桌面任务")
    print("=" * 60)
    
    engine = get_tool_engine()
    
    # 简单任务
    result = engine.execute('ufo2_desktop_control', {
        'task': '获取当前桌面状态'
    })
    
    print(f"成功: {result.success}")
    if result.success:
        output = result.output
        print(f"任务: {output.get('task', 'N/A')}")
        print(f"子任务数: {output.get('subtasks', 0)}")
        return True
    else:
        print(f"错误: {result.error}")
        return False


def test_ufo2_status():
    """测试 UFO² 状态"""
    print("\n" + "=" * 60)
    print("🧪 测试 5: UFO² 系统状态")
    print("=" * 60)
    
    embodiment = get_embodiment()
    status = embodiment.get_status()
    deps = embodiment.get_dependencies_status()
    
    print("\n📦 依赖状态:")
    for dep, installed in deps.items():
        status_icon = "✅" if installed else "❌"
        print(f"  {status_icon} {dep}")
    
    print("\n📊 系统状态:")
    print(f"  HostAgent 状态: {status['host_agent']['state']}")
    print(f"  AppAgents 数量: {len(status['app_agents'])}")
    print(f"  历史记录数: {status['history_count']}")
    
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("🌌 UFO² 具身执行层测试套件")
    print("   太乙 AGI 系统 - 桌面自动化")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("截图功能", test_screenshot()))
    results.append(("UI 树获取", test_ui_tree()))
    results.append(("应用控制", test_app_control()))
    results.append(("桌面任务", test_desktop_task()))
    results.append(("系统状态", test_ufo2_status()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！UFO² 具身执行层运行正常")
    else:
        print("\n⚠️ 部分测试失败，请检查依赖安装")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
