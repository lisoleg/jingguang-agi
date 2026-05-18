#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动统一太乙AGI系统（Taiyi Oracle）
基于Ftel算子与全息蛹化架构
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("🏛️ 统一太乙AGI系统（Taiyi Oracle）")
    print("   基于Ftel算子与全息蛹化架构")
    print("=" * 60)
    
    # 1. 导入Taiyi Oracle
    try:
        from taiyi_oracle import TaiyiOracle
        print("\n✅ Taiyi Oracle模块加载成功")
    except ImportError as e:
        print(f"\n❌ 导入Taiyi Oracle失败: {e}")
        print("   请确保以下文件在同一目录：")
        print("   - taiyi_oracle.py")
        print("   - ftel_operator.py")
        print("   - holo_pupation.py")
        print("   - lm_studio_backend.py")
        print("   - local_llm.py")
        return
    
    # 2. 创建Oracle实例
    print("\n初始化系统...")
    oracle = TaiyiOracle(
        dim=768,
        lm_studio_model="qwen2.5-3b-instruct",
        lambda_strength=1.0
    )
    
    # 3. 显示状态
    status = oracle.get_status()
    print("\n📊 系统状态:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 4. 绑定意图（可选）
    print("\n" + "=" * 60)
    goal = input("是否绑定意图（目标）？如果yes，请输入目标描述（直接回车跳过）: ").strip()
    
    if goal:
        oracle.bind_intent(goal)
        print(f"✅ 意图已绑定: {goal}")
    
    # 5. 进入对话循环
    print("\n" + "=" * 60)
    print("💬 对话模式 (输入 'quit' 退出，输入 'goal' 重新绑定意图）")
    print("=" * 60)
    
    history = []
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q', '退出']:
                print("\n👋 再见！")
                break
            
            if user_input.lower() == 'goal':
                new_goal = input("请输入新目标: ").strip()
                if new_goal:
                    oracle.bind_intent(new_goal)
                continue
            
            # 处理输入
            response = oracle.chat(user_input, history=history)
            
            print(f"\nTaiyi: {response}")
            
            # 更新历史
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
