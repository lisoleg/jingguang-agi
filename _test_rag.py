#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
print('SCRIPT START', flush=True)
try:
    import taiyi_rag
    print('IMPORT OK', flush=True)
    rag = taiyi_rag.TaiyiRAG()
    print('INIT OK', flush=True)
    print('STATUS:', rag.status(), flush=True)
    results = rag.retrieve('复合体理学', top_k=2)
    print('RESULTS:', len(results), flush=True)
    for r in results:
        print(f'  [{r.rank}] {r.chunk.metadata.get("title")} score={r.score:.3f}', flush=True)
    print('ALL DONE', flush=True)
except Exception as e:
    import traceback
    traceback.print_exc(file=sys.stderr)
    print('ERROR:', str(e), flush=True)
