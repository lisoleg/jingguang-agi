#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("A1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
print("A2", flush=True)

# Override path
taiyi_rag.RAG_DB_PATH = os.path.join(script_dir, ".workbuddy", "rag", "knowledge_base.db")
os.makedirs(os.path.dirname(taiyi_rag.RAG_DB_PATH), exist_ok=True)

# Test DocumentParser
print("A3: Testing DocumentParser", flush=True)
parser = taiyi_rag.DocumentParser()
print("A4: DocumentParser created", flush=True)

doc_id, title, source, tags, chunks = parser.parse_text("测试内容", "测试标题", "test", ["tag1"])
print(f"A5: parsed doc_id={doc_id}, chunks={len(chunks)}", flush=True)

# Test DB connection
print("A6: Testing DB", flush=True)
conn = taiyi_rag.sqlite3.connect(taiyi_rag.RAG_DB_PATH, timeout=10)
print("A7: DB connected", flush=True)
conn.close()
print("A8: DB test done", flush=True)
