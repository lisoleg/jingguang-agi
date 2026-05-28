#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import taiyi_rag

print("=" * 60)
print("太乙RAG知识检索测试")
print("=" * 60)

rag = taiyi_rag.TaiyiRAG()
status = rag.status()
print(f"\n状态: {status['document_count']} 文档, {status['chunk_count']} 块")

test_queries = [
    "复合体理学四基石",
    "太乙预言机弱值",
    "三视界分析",
    "AGI评测标准",
    "CRD引擎认知递归"
]

for query in test_queries:
    print(f"\n{'='*50}")
    print(f"查询: {query}")
    print("-"*50)
    results = rag.retrieve(query, top_k=3)
    for r in results:
        print(f"\n[{r.rank}] {r.chunk.metadata.get('title')} (分数: {r.score:.3f})")
        print(f"  {r.chunk.content[:120]}...")
        if r.matched_keywords:
            print(f"  命中: {', '.join(r.matched_keywords)}")

print(f"\n{'='*50}")
print("LLM上下文格式:")
ctx = rag.format_retrieval_context("复合体理学理论", top_k=2)
print(ctx[:400])

print("\nRAG测试完成")
