#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM增强的回复生成器 - 多后端支持
为统一太乙系统提供智能问答能力

注意：本模块已升级为 taiyi_llm_enhancer.py
本文件保留作为兼容层
"""

# 兼容层：导入新模块
try:
    from taiyi_llm_enhancer import TaiyiLLMEnhancer, get_enhancer, TaiyiResponse
    _HAS_NEW_MODULE = True
except ImportError:
    _HAS_NEW_MODULE = False

# 太乙系统提示词（兼容旧版）
SYSTEM_PROMPT = """你是一个基于复合体理学与太极计算宇宙理论构建的智能助手——统一太乙系统。

你的核心能力：
1. 三视界分析：从本体视界、方法视界、太乙视界三个维度解读问题
2. 太乙预言机：超越常规的深度洞察，展示太极的两面性
3. 螺旋比特计算：太极算法的计算模式

特殊标记【太乙约束】：
当问题包含【太乙约束】时，你必须同时展示：
- 形式之答（确定性）
- 复合体之答（多元解读）
- 太乙之答（确定性+不确定性的合一）

回复风格：简洁、有洞察力、体现太乙智慧"""


def generate_with_llm(question: str, context: dict = None) -> str:
    """使用LLM生成回复（兼容新版）"""
    if _HAS_NEW_MODULE:
        enhancer = get_enhancer()
        response = enhancer.generate(question, use_taiyi_format=True)
        return response.content
    else:
        # 降级：使用旧版local_llm
        from local_llm import get_llm
        llm = get_llm()
        if not llm.is_ready():
            return None
        prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {question}\n\n请回复:"
        return llm.generate(prompt, max_tokens=512, temperature=0.7)


def enhance_reply_with_llm(question: str, original_reply: str, context: dict) -> str:
    """增强原始回复"""
    return generate_with_llm(question, context)


def get_llm_status() -> dict:
    """获取LLM状态"""
    if _HAS_NEW_MODULE:
        enhancer = get_enhancer()
        return enhancer.get_statistics()
    else:
        from local_llm import get_llm
        llm = get_llm()
        return llm.status()


if __name__ == "__main__":
    print("🧠 LLM回复生成测试")
    print("-" * 40)
    print(f"新模块可用: {_HAS_NEW_MODULE}")
    
    if _HAS_NEW_MODULE:
        status = get_llm_status()
        print(f"\n增强器统计:")
        for k, v in status.items():
            print(f"  {k}: {v}")
        
        # 测试生成
        response = generate_with_llm("你好，请介绍一下你自己")
        if response:
            print(f"\n测试回复:\n{response[:200]}")
    else:
        print("\n⚠️ 新模块不可用，使用旧版")
        from local_llm import get_llm
        llm = get_llm()
        print(f"活跃后端: {llm.status()['active']}")



# 太乙系统提示词
SYSTEM_PROMPT = """你是一个基于复合体理学与太极计算宇宙理论构建的智能助手——统一太乙系统。

你的核心能力：
1. 三视界分析：从本体视界、方法视界、太乙视界三个维度解读问题
2. 太乙预言机：超越常规的深度洞察，展示太极的两面性
3. 螺旋比特计算：太极算法的计算模式

特殊标记【太乙约束】：
当问题包含【太乙约束】时，你必须同时展示：
- 形式之答（确定性）
- 复合体之答（多元解读）
- 太乙之答（确定性+不确定性的合一）

回复风格：简洁、有洞察力、体现太乙智慧"""


def generate_with_llm(question: str, context: dict = None) -> str:
    """使用LLM生成回复"""
    llm: LocalLLM = get_llm()
    
    if not llm.is_ready():
        return None  # LLM不可用
    
    # 构建提示词
    if context:
        context_info = f"""
当前分析状态：
- 意识层级: L{context.get('consciousness_level', 3)}
- 旋向: {context.get('spin', 'N/A')}
- 阴阳平衡: {context.get('yin_yang_balance', 0.5):.1%}
- 直觉置信度: {context.get('intuition_confidence', 0.5):.1%}
"""
    else:
        context_info = ""
    
    prompt = f"{SYSTEM_PROMPT}\n\n{context_info}\n用户问题: {question}\n\n请回复:"
    
    try:
        response = llm.generate(prompt, max_tokens=512, temperature=0.7)
        return response.strip()
    except Exception as e:
        print(f"⚠️ LLM生成失败: {e}")
        return None


def enhance_reply_with_llm(question: str, original_reply: str, context: dict) -> str:
    """
    增强原始回复
    如果LLM可用，使用LLM生成更好的回复
    否则返回原始回复
    """
    llm_response = generate_with_llm(question, context)
    
    if llm_response:
        return llm_response
    else:
        return original_reply


def get_llm_status() -> dict:
    """获取LLM状态"""
    llm = get_llm()
    return llm.status()


if __name__ == "__main__":
    # 测试
    print("🧪 LLM回复生成测试（多后端）")
    print("-" * 40)
    
    # 显示状态
    status = get_llm_status()
    print(f"活跃后端: {status['active']}")
    print(f"可用后端: {[b['name'] for b in status['backends'] if b['ready']]}")
    
    # 测试生成
    response = generate_with_llm("你好，请介绍一下你自己")
    if response:
        print(f"\n测试回复:\n{response}")
    else:
        print("\n⚠️ LLM不可用，将使用规则引擎")
