#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("G1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
import re
print("G2", flush=True)

parser = taiyi_rag.DocumentParser()

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

print("G3: Step 1 - re.sub", flush=True)
text = re.sub(r'\s+', ' ', content).strip()
print(f"G4: Text length = {len(text)}", flush=True)

print("G5: Step 2 - init chunks list", flush=True)
chunks = []
start = 0
chunk_idx = 0

print("G6: Step 3 - entering while loop", flush=True)
while start < len(text):
    print(f"  G{6+chunk_idx}: Chunk {chunk_idx}, start={start}", flush=True)
    end = start + parser.CHUNK_SIZE
    chunk_text = text[start:end]
    print(f"  G{7+chunk_idx}: Chunk {chunk_idx}, end={end}, len={len(chunk_text)}", flush=True)

    if end < len(text):
        for sep in ['。', '！', '？', '；', '，']:
            last_sep = chunk_text.rfind(sep)
            if last_sep > parser.CHUNK_SIZE // 2:
                chunk_text = chunk_text[:last_sep + 1]
                print(f"  G{8+chunk_idx}: Chunk {chunk_idx}, cut at {sep}, new len={len(chunk_text)}", flush=True)
                break

    print(f"  G{9+chunk_idx}: Chunk {chunk_idx}, extracting keywords", flush=True)
    keywords = parser._extract_keywords(chunk_text)
    print(f"  G{10+chunk_idx}: Chunk {chunk_idx}, keywords={len(keywords)}", flush=True)

    print(f"  G{11+chunk_idx}: Chunk {chunk_idx}, computing tfidf", flush=True)
    tfidf = parser._compute_tfidf(chunk_text, keywords)
    print(f"  G{12+chunk_idx}: Chunk {chunk_idx}, tfidf={len(tfidf)}", flush=True)

    print(f"  G{13+chunk_idx}: Chunk {chunk_idx}, creating DocumentChunk", flush=True)
    try:
        chunk = taiyi_rag.DocumentChunk(
            chunk_id="test_id",
            document_id="test_doc",
            content=chunk_text.strip(),
            keywords=keywords,
            tfidf_scores=tfidf
        )
        print(f"  G{14+chunk_idx}: Chunk {chunk_idx}, created successfully", flush=True)
    except Exception as e:
        print(f"  G{14+chunk_idx} ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        break

    chunks.append(chunk)
    chunk_idx += 1
    start = start + len(chunk_text) - parser.CHUNK_OVERLAP
    if start <= 0:
        start = min(parser.CHUNK_SIZE, len(text))

print(f"G{6+chunk_idx}: Done, total chunks = {len(chunks)}", flush=True)
