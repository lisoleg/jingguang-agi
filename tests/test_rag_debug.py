#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("Test 1: Starting", flush=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Test 2: Script dir = {script_dir}", flush=True)

sys.path.insert(0, script_dir)
print("Test 3: Path updated", flush=True)

import taiyi_rag
print("Test 4: taiyi_rag imported", flush=True)

# Check __file__ issue
print(f"Test 5: RAG_DB_PATH = {taiyi_rag.RAG_DB_PATH}", flush=True)

# Override path
taiyi_rag.RAG_DB_PATH = os.path.join(script_dir, ".workbuddy", "rag", "knowledge_base.db")
os.makedirs(os.path.dirname(taiyi_rag.RAG_DB_PATH), exist_ok=True)
print(f"Test 6: New RAG_DB_PATH = {taiyi_rag.RAG_DB_PATH}", flush=True)

print("Test 7: Creating TaiyiRAG...", flush=True)
rag = taiyi_rag.TaiyiRAG()
print("Test 8: TaiyiRAG created", flush=True)

status = rag.status()
print(f"Test 9: Status = {status}", flush=True)

# Test retrieve
print("Test 10: Testing retrieve...", flush=True)
results = rag.retrieve("复合体理学", top_k=2)
print(f"Test 11: Got {len(results)} results", flush=True)

for r in results:
    print(f"  [{r.rank}] score={r.score:.3f}", flush=True)
