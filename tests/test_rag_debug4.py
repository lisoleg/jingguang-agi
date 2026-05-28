#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("C1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
print("C2", flush=True)

taiyi_rag.RAG_DB_PATH = os.path.join(script_dir, ".workbuddy", "rag", "knowledge_base.db")
os.makedirs(os.path.dirname(taiyi_rag.RAG_DB_PATH), exist_ok=True)

# Create RAG manually
rag = object.__new__(taiyi_rag.TaiyiRAG)
rag.db_path = taiyi_rag.RAG_DB_PATH
rag.parser = taiyi_rag.DocumentParser()
rag._lock = __import__('threading').Lock()
rag._init_db()
print("C3: DB initialized", flush=True)

# Test _load_builtin_knowledge
print("C4: Calling _load_builtin_knowledge", flush=True)
try:
    rag._load_builtin_knowledge()
    print("C5: _load_builtin_knowledge completed", flush=True)
except Exception as e:
    print(f"C5 ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("C6: Done", flush=True)
