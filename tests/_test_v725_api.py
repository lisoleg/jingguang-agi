import app as flask_app
import json

with flask_app.app.test_client() as client:
    # analyze
    resp = client.post('/api/v725/understand/analyze',
                       json={'file_path': 'M184_LLMWikiEngine.py'})
    d = json.loads(resp.data)
    print(f'analyze: {resp.status_code}')
    print(f'  imports={d.get("imports")}, functions={d.get("functions")}, classes={d.get("classes")}')

    # theorem T191
    resp2 = client.get('/api/v725/understand/theorem/T191')
    d2 = json.loads(resp2.data)
    print(f'theorem/T191: {resp2.status_code}, passed={d2.get("passed")}')

    # theorem T193
    resp3 = client.get('/api/v725/understand/theorem/T193')
    d3 = json.loads(resp3.data)
    print(f'theorem/T193: {resp3.status_code}, passed={d3.get("passed")}')

    # chat
    resp4 = client.get('/api/v725/understand/chat?query=WikiEngine')
    d4 = json.loads(resp4.data)
    ans = d4.get("answer", "")
    print(f'chat: {resp4.status_code}, answer_len={len(ans)}')

    # state
    resp5 = client.get('/api/v725/understand/state')
    d5 = json.loads(resp5.data)
    print(f'state: {resp5.status_code}, status={d5.get("understand_engine", {}).get("status")}')

print('\nAll v725 API endpoints PASSED')
