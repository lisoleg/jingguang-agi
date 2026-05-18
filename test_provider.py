#!/usr/bin/env python3
"""测试 SafeJSONProvider 是否正常工作"""
from flask import Flask, request, jsonify
from flask.json.provider import JSONProvider
import json as pyjson

class SafeJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return pyjson.dumps(obj, default=self._safe_default, **kwargs)
    
    def loads(self, s, **kwargs):
        print(f"[DEBUG] SafeJSONProvider.loads() called with type: {type(s)}")
        return pyjson.loads(s, **kwargs)
    
    def _safe_default(self, obj):
        return str(obj)[:100]

app = Flask(__name__)
app.json = SafeJSONProvider(app)

@app.route('/test', methods=['POST'])
def test():
    print("[DEBUG] Entering /test endpoint")
    data = request.get_json(force=True, silent=True)
    print(f"[DEBUG] request.get_json() result: {data}")
    return jsonify(data)

if __name__ == '__main__':
    print("Starting test server on port 5003...")
    app.run(host='0.0.0.0', port=5003, debug=False)
