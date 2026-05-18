#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脑图v2核心功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_mindmap_v2 import build_conversation_tree, ReferenceDetector

def test_tree_building():
    """测试树构建功能"""
    print("=" * 60)
    print("测试1: 单个问题")
    print("=" * 60)
    
    messages = [
        {'q': '什么是复合体理学？', 'a': '复合体理学是...', 'id': 'Q1'},
    ]
    
    tree = build_conversation_tree(messages)
    print(f"Tree: {tree}")
    print(f"根节点子节点数: {len(tree['children'])}")
    assert len(tree['children']) == 1, "应该有一个子节点"
    print("✅ 测试1通过\n")
    
    print("=" * 60)
    print("测试2: 多个独立问题")
    print("=" * 60)
    
    messages = [
        {'q': '什么是复合体理学？', 'a': '复合体理学是...', 'id': 'Q1'},
        {'q': '什么是IGCTR理论？', 'a': 'IGCTR是...', 'id': 'Q2'},
    ]
    
    tree = build_conversation_tree(messages)
    print(f"根节点子节点数: {len(tree['children'])}")
    # Q1和Q2都是独立问题，应该都在根节点下
    assert len(tree['children']) == 2, "应该有两个子节点"
    print("✅ 测试2通过\n")
    
    print("=" * 60)
    print("测试3: 显式引用（继续Q1）")
    print("=" * 60)
    
    messages = [
        {'q': '什么是复合体理学？', 'a': '复合体理学是...', 'id': 'Q1'},
        {'q': '继续Q1，能详细讲讲吗？', 'a': '当然可以...', 'id': 'Q2'},
    ]
    
    tree = build_conversation_tree(messages)
    print(f"Tree: {tree}")
    # Q2应该作为Q1的子节点
    q1_node = tree['children'][0]
    print(f"Q1子节点数: {len(q1_node.get('children', []))}")
    assert len(q1_node.get('children', [])) == 1, "Q1应该有一个子节点"
    print("✅ 测试3通过\n")
    
    print("=" * 60)
    print("测试4: 引用检测器")
    print("=" * 60)
    
    detector = ReferenceDetector()
    
    # 测试显式引用
    ref = detector.detect_explicit_reference("继续Q1")
    print(f"检测'继续Q1': Q{ref}")
    assert ref == 1, "应该检测到Q1"
    
    ref = detector.detect_explicit_reference("针对问题2的追问")
    print(f"检测'针对问题2': Q{ref}")
    assert ref == 2, "应该检测到Q2"
    
    # 测试隐式引用
    history = [
        {'q': '什么是复合体理学？', 'a': '...'},
        {'q': '什么是IGCTR理论？', 'a': '...'},
    ]
    implicit_refs = detector.detect_implicit_reference("复合体理学的基本原理是什么？", history)
    print(f"隐式引用检测结果: {implicit_refs}")
    print("✅ 测试4通过\n")
    
    print("=" * 60)
    print("所有测试通过！✅")
    print("=" * 60)

if __name__ == '__main__':
    test_tree_building()
