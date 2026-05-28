#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("B1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
print("B2", flush=True)

taiyi_rag.RAG_DB_PATH = os.path.join(script_dir, ".workbuddy", "rag", "knowledge_base.db")
os.makedirs(os.path.dirname(taiyi_rag.RAG_DB_PATH), exist_ok=True)

# Manually create TaiyiRAG without calling __init__ methods
print("B3: Creating RAG without init", flush=True)
rag = object.__new__(taiyi_rag.TaiyiRAG)
rag.db_path = taiyi_rag.RAG_DB_PATH
rag.parser = taiyi_rag.DocumentParser()
rag._lock = __import__('threading').Lock()
print("B4: RAG object created manually", flush=True)

# Test _init_db
print("B5: Calling _init_db", flush=True)
try:
    rag._init_db()
    print("B6: _init_db completed", flush=True)
except Exception as e:
    print(f"B6 ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

# Test add_document
print("B7: Testing add_document", flush=True)
try:
    doc_id = rag.add_document("测试", "测试内容", "test", ["tag1"])
    print(f"B8: add_document returned {doc_id}", flush=True)
except Exception as e:
    print(f"B8 ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("B9: Done", flush=True)
