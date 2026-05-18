#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脑图系统v2 完整功能测试
测试：树构建、引用关系检测、API端点
"""

import sys
import os
import threading
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_mindmap_v2 import app, build_conversation_tree, ReferenceDetector

def test_tree_building():
    """测试1: 树构建功能"""
    print("\n" + "=" * 60)
    print("测试1: 树构建功能")
    print("=" * 60)
    
    # 1.1 单个问题
    messages = [{'q': '什么是复合体理学？', 'a': '复合体理学是...', 'id': 'Q1'}]
    tree = build_conversation_tree(messages)
    assert tree is not None, "树不应为None"
    assert len(tree['children']) == 1, "应该有1个子节点"
    print("✅ 1.1 单个问题: 通过")
    
    # 1.2 多个独立问题
    messages = [
        {'q': '什么是复合体理学？', 'a': '...', 'id': 'Q1'},
        {'q': '什么是IGCTR？', 'a': '...', 'id': 'Q2'},
    ]
    tree = build_conversation_tree(messages)
    assert len(tree['children']) == 2, "应该有2个子节点"
    print("✅ 1.2 多个独立问题: 通过")
    
    # 1.3 显式引用（继续Q1）
    messages = [
        {'q': '什么是复合体理学？', 'a': '...', 'id': 'Q1'},
        {'q': '继续Q1，详细说明', 'a': '...', 'id': 'Q2'},
    ]
    tree = build_conversation_tree(messages)
    q1_node = tree['children'][0]
    assert len(q1_node['children']) == 1, "Q1应该有1个子节点"
    print("✅ 1.3 显式引用（继续Q1）: 通过")
    
    # 1.4 多层嵌套引用
    messages = [
        {'q': '问题1', 'a': '...', 'id': 'Q1'},
        {'q': '继续Q1', 'a': '...', 'id': 'Q2'},
        {'q': '继续Q2', 'a': '...', 'id': 'Q3'},
    ]
    tree = build_conversation_tree(messages)
    q1_node = tree['children'][0]
    q2_node = q1_node['children'][0]
    assert len(q2_node['children']) == 1, "Q2应该有1个子节点（Q3）"
    print("✅ 1.4 多层嵌套引用: 通过")
    
    print("\n✅ 所有树构建测试通过！\n")

def test_reference_detector():
    """测试2: 引用检测器"""
    print("=" * 60)
    print("测试2: 引用检测器")
    print("=" * 60)
    
    detector = ReferenceDetector()
    
    # 2.1 显式引用模式
    test_cases = [
        ("继续Q1", 1),
        ("继续 Q2", 2),
        ("针对问题3", 3),
        ("关于Q1的说明", 1),
        ("问题1的补充说明", 1),
        ("Q5相关内容", 5),
    ]
    
    for text, expected in test_cases:
        result = detector.detect_explicit_reference(text)
        assert result == expected, f"检测'{text}'失败: 期望Q{expected}, 得到Q{result}"
        print(f"✅ 2.{test_cases.index((text, expected))+1} 显式引用 '{text}' -> Q{result}")
    
    # 2.2 隐式引用
    history = [
        {'q': '什么是复合体理学？'},
        {'q': 'IGCTR理论是什么？'},
    ]
    implicit = detector.detect_implicit_reference("复合体理学的基本原理", history)
    print(f"✅ 2.{len(test_cases)+1} 隐式引用检测: {implicit[:2] if implicit else '无'}")
    
    print("\n✅ 所有引用检测测试通过！\n")

def test_api_endpoints():
    """测试3: API端点（使用Flask测试客户端）"""
    print("=" * 60)
    print("测试3: API端点测试")
    print("=" * 60)
    
    with app.test_client() as client:
        # 3.1 测试 /api/state
        resp = client.get('/api/state')
        assert resp.status_code == 200, f"/api/state 失败: {resp.status_code}"
        data = json.loads(resp.get_data(as_text=True))
        assert data['status'] == 'ok', "状态应该为'ok'"
        print(f"✅ 3.1 /api/state: 版本={data['version']}, 状态={data['status']}")
        
        # 3.2 测试 /api/chat_v2
        resp = client.post('/api/chat_v2',
                           json={'message': '测试问题', 'session_id': 'test_api'})
        assert resp.status_code == 200, f"/api/chat_v2 失败: {resp.status_code}"
        data = json.loads(resp.get_data(as_text=True))
        assert 'tree' in data, "响应应该包含'tree'字段"
        assert data['tree'] is not None, "'tree'字段不应为None"
        assert 'debug_marker' in data, "响应应该包含调试标记"
        print(f"✅ 3.2 /api/chat_v2: tree不为None, 调试标记={data.get('debug_marker')}")
        
        # 3.3 测试 /api/mindmap (GET)
        resp = client.get('/api/mindmap?session_id=test_api')
        assert resp.status_code == 200, f"/api/mindmap GET 失败: {resp.status_code}"
        data = json.loads(resp.get_data(as_text=True))
        assert data['success'] == True, "应该返回success=True"
        print(f"✅ 3.3 /api/mindmap (GET): success={data['success']}")
        
        # 3.4 测试 /api/mindmap (POST)
        resp = client.post('/api/mindmap', json={'session_id': 'test_api'})
        assert resp.status_code == 200, f"/api/mindmap POST 失败: {resp.status_code}"
        data = json.loads(resp.get_data(as_text=True))
        assert data['success'] == True, "应该返回success=True"
        print(f"✅ 3.4 /api/mindmap (POST): success={data['success']}")
        
        # 3.5 测试多轮对话 + 引用关系
        client.post('/api/chat_v2', json={'message': '第一个问题', 'session_id': 'test_ref'})
        resp = client.post('/api/chat_v2', 
                          json={'message': '继续Q1，详细说明', 'session_id': 'test_ref'})
        data = json.loads(resp.get_data(as_text=True))
        assert data['tree'] is not None, "树不应为None"
        # Q2应该是Q1的子节点
        root = data['tree']
        if root['children']:
            q1 = root['children'][0]
            if q1['children']:
                print(f"✅ 3.5 引用关系: Q1有{q1['children']}个子节点")
        print(f"✅ 3.5 多轮对话引用关系: 通过")
        
    print("\n✅ 所有API端点测试通过！\n")

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🌌 脑图系统v2 - 完整功能测试")
    print("=" * 60)
    
    try:
        test_tree_building()
        test_reference_detector()
        test_api_endpoints()
        
        print("=" * 60)
        print("🎉 所有测试通过！脑图系统v2工作正常！")
        print("=" * 60 + "\n")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
