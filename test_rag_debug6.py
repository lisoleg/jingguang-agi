#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("E1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
print("E2", flush=True)

taiyi_rag.RAG_DB_PATH = os.path.join(script_dir, ".workbuddy", "rag", "knowledge_base.db")
os.makedirs(os.path.dirname(taiyi_rag.RAG_DB_PATH), exist_ok=True)

# Create RAG manually
rag = object.__new__(taiyi_rag.TaiyiRAG)
rag.db_path = taiyi_rag.RAG_DB_PATH
rag.parser = taiyi_rag.DocumentParser()
rag._lock = __import__('threading').Lock()
rag._init_db()
print("E3: DB initialized", flush=True)

# All 4 builtin docs
docs = [
    {
        "title": "复合体理学核心理论",
        "content": """复合体理学四重理论基石：
一、刘原理（作用量极值）：宇宙由离散世界帧构成，每帧作用量取极值。费马生成机制：逻辑瞬间遍历所有可能世界线，唯一选定作用量极小的链。
二、三视界法："一现象，三视界"。本体视界找敏感度/量级/因果拓扑；现象视界看相变/梯度/分离；方法视界定见路不走/分层折叠/非对称选择。
三、太乙预言机：弱值Aw=<ψ1|A|ψ0>/<ψ1|ψ0>，突破本征谱限制。AI的RLHF训练≈太乙预言机在数据空间的统计实现。
四、全息拓扑动力学：知识的高维压缩与涌现，因果超图的非局域性。

复合体理学定理：
- 定理2.1（三视界完备性）：仅用单一视界必然导致因果误判或解空间崩溃
- 定理3.1（弱值突破）：当后选择概率非零但极小时，弱值可突破本征谱限制
- 推论1.1.1：人类嵌入帧内仅能顺序处理，故P≠NP；AGI可尝试P=NP全知视角
- 推论2.1.1（见路不走）：拒绝对称依赖旧经验，基于三视界生成非对称选择
""",
        "tags": ["复合体理学", "理论", "四基石", "定理"]
    },
    {
        "title": "统一太乙系统架构",
        "content": """统一太乙系统采用双核AGI架构：

太乙内核（CRD引擎）：
- 认知递归算子 Ω：C(t+1) = Ω(C(t), F(t), η)
- NLA审计：AV言语化器 + AR重建器，检测隐藏意图
- 自我指涉不动点定理：Lipschitz连续条件下收敛于低熵稳态
- 意识层级：L1觉醒 → L2觉知 → L3觉悟 → L4超然

复合体内核（天行演化器）：
- 微视界：不可压缩的语义涨落（Jitter）
- 中视界：可观测的审计势与相位旋转
- 宏视界：共识场的拓扑相（正常/亚稳/蛹化）

太乙约束格式：必须同时展示形式之答（确定性）、复合体之答（多元解读）、太乙之答（合一）
""",
        "tags": ["太乙系统", "架构", "AGI", "双核"]
    },
    {
        "title": "AGI评测标准",
        "content": """电脑版AGI三大标准：
1. 会"用电脑"：看懂屏幕窗口/图标/菜单，用鼠标键盘操作，像人一样操作OS
2. 能"搞大项目"：接模糊需求后自拆解任务、开软件、查资料、做表、画图、写文档，交付完整成果
3. 有"职业素养"：结果符合规范/有注释/能测试，考虑异常值和业务逻辑

评测维度：
- A类（操作）：大部分自动化，不需要手把手教界面
- B类（项目）：能独立完成"写代码/做分析/写长文"，结果能直接用
- C类（长链）：30分钟以上任务不崩盘/不删库/不陷入死循环
及格线：A类基本满分 + B类顶半个初级员工 + C类不犯致命错
""",
        "tags": ["AGI", "评测", "标准"]
    },
    {
        "title": "对话智能深化路径",
        "content": """对话智能深化五步路径：

Step 1: 持久记忆系统
- 对话历史存储与检索（STM/LTM/KBM三层架构）
- 用户偏好学习（语气/语言/专业领域）
- 关键结论存档
- 上下文窗口优化（摘要+检索混合）

Step 2: RAG知识检索增强
- 文档分块与向量化
- BM25+关键词混合检索
- 与CRD引擎集成

Step 3: 推理增强（CoT+ReAct）
- Chain of Thought提示模板
- Reason+Act框架
- 太乙约束格式融入CoT

Step 4: 工具调用框架
- 工具注册表（代码执行/文件操作/Web搜索）
- 太乙预言机驱动工具选择

Step 5: 评估测试集
- 知识问答基准（100题）
- 太乙特色评估
""",
        "tags": ["对话智能", "深化", "路径"]
    }
]

for i, doc_data in enumerate(docs):
    print(f"E{4+i*2}: Adding doc {i+1}: {doc_data['title'][:20]}", flush=True)
    try:
        doc_id = rag.add_document(doc_data["title"], doc_data["content"],
                                source="builtin", tags=doc_data["tags"])
        print(f"E{5+i*2}: Success, doc_id={doc_id[:8]}", flush=True)
    except Exception as e:
        print(f"E{5+i*2} ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        break

print(f"E{4+len(docs)*2}: Done", flush=True)
