#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("F1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
print("F2", flush=True)

parser = taiyi_rag.DocumentParser()
print("F3: Parser created", flush=True)

# First doc content
content = """复合体理学四重理论基石：
一、刘原理（作用量极值）：宇宙由离散世界帧构成，每帧作用量取极值。费马生成机制：逻辑瞬间遍历所有可能世界线，唯一选定作用量极小的链。
二、三视界法："一现象，三视界"。本体视界找敏感度/量级/因果拓扑；现象视界看相变/梯度/分离；方法视界定见路不走/分层折叠/非对称选择。
三、太乙预言机：弱值Aw=<ψ1|A|ψ0>/<ψ1|ψ0>，突破本征谱限制。AI的RLHF训练≈太乙预言机在数据空间的统计实现。
四、全息拓扑动力学：知识的高维压缩与涌现，因果超图的非局域性。

复合体理学定理：
- 定理2.1（三视界完备性）：仅用单一视界必然导致因果误判或解空间崩溃
- 定理3.1（弱值突破）：当后选择概率非零但极小时，弱值可突破本征谱限制
- 推论1.1.1：人类嵌入帧内仅能顺序处理，故P≠NP；AGI可尝试P=NP全知视角
- 推论2.1.1（见路不走）：拒绝对称依赖旧经验，基于三视界生成非对称选择
"""

print("F4: Parsing text...", flush=True)
try:
    doc_id, title, source, tags, chunks = parser.parse_text(content, "复合体理学核心理论", "builtin", ["tag1"])
    print(f"F5: Success - doc_id={doc_id}, chunks={len(chunks)}", flush=True)
except Exception as e:
    print(f"F5 ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("F6: Done", flush=True)
