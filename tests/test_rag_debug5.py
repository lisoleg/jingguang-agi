#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
print("D1", flush=True)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import taiyi_rag
import json
print("D2", flush=True)

taiyi_rag.RAG_DB_PATH = os.path.join(script_dir, ".workbuddy", "rag", "knowledge_base.db")
os.makedirs(os.path.dirname(taiyi_rag.RAG_DB_PATH), exist_ok=True)

# Create RAG manually
rag = object.__new__(taiyi_rag.TaiyiRAG)
rag.db_path = taiyi_rag.RAG_DB_PATH
rag.parser = taiyi_rag.DocumentParser()
rag._lock = __import__('threading').Lock()
rag._init_db()
print("D3: DB initialized", flush=True)

# Test adding one of the builtin docs
test_doc = {
    "title": "复合体理学核心理论",
    "content": "复合体理学四重理论基石：...",
    "tags": ["复合体理学", "理论", "四基石", "定理"]
}
print("D4: Testing add_document with Chinese doc", flush=True)
try:
    doc_id = rag.add_document(test_doc["title"], test_doc["content"],
                            source="builtin", tags=test_doc["tags"])
    print(f"D5: Success, doc_id={doc_id}", flush=True)
except Exception as e:
    print(f"D5 ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

# Test JSON serialization of tags
print("D6: Testing JSON serialization", flush=True)
try:
    tags_json = json.dumps(test_doc["tags"])
    print(f"D7: tags JSON: {tags_json}", flush=True)
except Exception as e:
    print(f"D7 ERROR: {e}", flush=True)

print("D8: Done", flush=True)
