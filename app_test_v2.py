#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太乙AGI 4.0 — 对话引用关系脑图系统 v2

核心设计理念：
- 每一轮问答对作为一个节点（Q1&A1, Q2&A2, ...）
- 检测问答对之间的引用关系（显式+隐式）
- 按引用关系构建树状结构（不是从回答中提取要点）

引用检测策略：
1. 显式引用： "继续Q1"、"针对问题2"、"关于Q3的..."
2. 隐式引用： 计算语义相似度（关键词重叠 + TF-IDF）
3. 时间衰减： 越近的问题权重越高

树状结构构建：
- 根节点：对话主题
- 第一层：没有被引用的问答对（独立问题）
- 深层：被引用的问答对作为子节点
"""

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from flask.json.provider import JSONProvider
import sys, os, traceback, json as pyjson, re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

# ==================== JSONProvider ====================
class SafeJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        return pyjson.dumps(obj, default=self._safe_default, **kwargs)
    
    def loads(self, s, **kwargs):
        return pyjson.loads(s, **kwargs)
    
    def _safe_default(self, obj):
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (complex, np.complex64, np.complex128)):
            return {'__complex__': True, 'real': obj.real, 'imag': obj.imag}
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            d = {}
            for k, v in obj.__dict__.items():
                try:
                    pyjson.dumps(v, default=self._safe_default)
                    d[str(k)] = v
                except Exception:
                    d[str(k)] = str(v)[:200]
            return d
        return str(obj)[:200]

app.json = SafeJSONProvider(app)

def safe_jsonify(data, status=200):
    """安全的jsonify包装"""
    def _sanitize(obj):
        import numpy as np
        if obj is None:
            return None
        if isinstance(obj, bool):
            return obj
        if isinstance(obj, (int, float, str)):
            return obj
        if isinstance(obj, (complex, np.complex64, np.complex128)):
            return {'__complex__': True, 'real': obj.real, 'imag': obj.imag}
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, dict):
            return {str(k): _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_sanitize(v) for v in obj]
        if hasattr(obj, 'to_dict'):
            return _sanitize(obj.to_dict())
        if hasattr(obj, '__dict__'):
            return _sanitize(obj.__dict__)
        return str(obj)[:200]
    
    cleaned = _sanitize(data)
    response = app.response_class(
        response=pyjson.dumps(cleaned, ensure_ascii=False),
        status=status,
        mimetype='application/json; charset=utf-8'
    )
    return response

def parse_request_json():
    """直接从 request.get_data() 解析 JSON"""
    try:
        raw = request.get_data(as_text=True)
        if not raw:
            raw = request.data.decode('utf-8', errors='replace') if request.data else ''
        if raw:
            return pyjson.loads(raw)
    except Exception:
        pass
    return {}

# ==================== 全局初始化 ====================
_agi = None
_agi_lock = __import__('threading').Lock()

# 对话历史存储（内存中，按session_id索引）
# 结构: { 
#   session_id: {
#     'messages': [{'q': '...', 'a': '...', 'id': 'Q1'}, ...],
#     'tree': { 'id': 'root', 'children': [...] },
#     'created_at': '...'
#   }
# }
_conversation_store: Dict[str, Dict] = {}

def get_agi():
    global _agi
    with _agi_lock:
        if _agi is None:
            print("🔮 正在初始化太乙AGI 4.0...")
            from CompositeAGI_V2 import CompositeAGI_V2
            _agi = CompositeAGI_V2()
            print("✅ 太乙AGI 4.0 系统就绪！")
    return _agi

def get_conversation(session_id: str) -> Dict:
    """获取或创建对话记录"""
    if session_id not in _conversation_store:
        _conversation_store[session_id] = {
            'messages': [],  # 存储问答对
            'tree': None,     # 树状结构
            'created_at': datetime.now().isoformat(),
        }
    return _conversation_store[session_id]

# ==================== 核心：引用关系检测 ====================

class ReferenceDetector:
    """
    引用关系检测器
    
    策略：
    1. 显式引用检测：正则匹配"继续Q1"、"针对问题2"等
    2. 隐式引用检测：关键词重叠度 + 时间衰减
    """
    
    # 显式引用关键词模式
    EXPLICIT_PATTERNS = [
        r'继续\s*[Qq](\d+)',           # "继续Q1"
        r'针对\s*[Qq](\d+)',           # "针对Q1"
        r'关于\s*[Qq](\d+)',           # "关于Q1"
        r'问题\s*(\d+)',                # "问题1"
        r'Q\s*(\d+)',                  # "Q1"
        r'第\s*(\d+)\s*个',            # "第1个"
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p) for p in self.EXPLICIT_PATTERNS]
    
    def detect_explicit_reference(self, question: str) -> Optional[int]:
        """
        检测显式引用
        
        返回:
            - 被引用的问题编号（1-based），如果没找到返回None
        """
        for pattern in self.patterns:
            match = pattern.search(question)
            if match:
                try:
                    ref_id = int(match.group(1))
                    if ref_id > 0:
                        return ref_id
                except ValueError:
                    continue
        return None
    
    def detect_implicit_reference(self, question: str, history: List[Dict], top_k: int = 1) -> List[Tuple[int, float]]:
        """
        检测隐式引用（基于关键词重叠）
        
        参数:
            question: 当前问题
            history: 历史问答对列表 [{'q': '...', 'a': '...', 'id': 'Q1'}, ...]
            top_k: 返回最相关的top_k个
        
        返回:
            [(问题编号, 相似度), ...] 按相似度降序
        """
        if not history:
            return []
        
        # 提取当前问题的关键词
        current_keywords = set(self._extract_keywords(question))
        
        similarities = []
        for i, item in enumerate(history):
            # 提取历史问题的关键词
            hist_keywords = set(self._extract_keywords(item['q']))
            
            # 计算重叠度（Jaccard相似度）
            if not current_keywords or not hist_keywords:
                similarity = 0.0
            else:
                overlap = len(current_keywords & hist_keywords)
                union = len(current_keywords | hist_keywords)
                similarity = overlap / union if union > 0 else 0.0
            
            # 时间衰减：越近的问题权重越高
            time_decay = 1.0 / (1.0 + (len(history) - i) * 0.1)
            similarity *= time_decay
            
            similarities.append((i + 1, similarity))  # 1-based编号
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 只返回相似度 > 阈值的
        result = [(ref_id, sim) for ref_id, sim in similarities[:top_k] if sim > 0.1]
        
        return result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单实现：去停用词 + 分词）"""
        # 停用词表（简化版）
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', 
                     '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', 
                     '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        # 简单分词（按空格 + 标点）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)
        
        # 去停用词 + 长度过滤
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        
        return keywords

# 全局引用检测器
_reference_detector = ReferenceDetector()

def build_conversation_tree(messages: List[Dict]) -> Dict:
    """
    构建对话树状结构
    
    参数:
        messages: 问答对列表 [{'q': '...', 'a': '...', 'id': 'Q1'}, ...]
    
    返回:
        树状结构 {
            'id': 'root',
            'label': '对话主题',
            'children': [...]
        }
    """
    if not messages:
        return None
    
    # 构建节点列表
    nodes = []
    for i, msg in enumerate(messages):
        node = {
            'id': f'Q{i+1}',
            'label': msg['q'][:30] + ('...' if len(msg['q']) > 30 else ''),
            'question': msg['q'],
            'answer': msg['a'][:200],  # 摘要
            'full_answer': msg['a'],
            'children': [],
        }
        nodes.append(node)
    
    # 检测引用关系，构建父子关系
    parent_map = {}  # node_id -> parent_id
    for i, msg in enumerate(messages):
        current_id = i + 1  # 1-based
        
        # 1. 先检测显式引用
        explicit_ref = _reference_detector.detect_explicit_reference(msg['q'])
        
        if explicit_ref and explicit_ref <= len(messages):
            # 显式引用成功
            parent_map[current_id] = explicit_ref
        else:
            # 2. 检测隐式引用
            implicit_refs = _reference_detector.detect_implicit_reference(
                msg['q'], messages[:i], top_k=1
            )
            
            if implicit_refs:
                best_ref_id, best_sim = implicit_refs[0]
                parent_map[current_id] = best_ref_id
            else:
                # 没有引用，作为根节点的直接子节点
                parent_map[current_id] = 0  # 0表示根节点
    
    # 构建树
    root = {
        'id': 'root',
        'label': messages[0]['q'][:50] if messages else '对话主题',
        'children': [],
    }
    
    # 建立父子关系
    node_dict = {0: root}
    for i, node in enumerate(nodes):
        node_dict[i + 1] = node
    
    for child_id, parent_id in parent_map.items():
        if parent_id in node_dict:
            node_dict[parent_id]['children'].append(node_dict[child_id])
    
    return root

# ==================== API端点 ====================

@app.route('/')
def index():
    return app.send_static_file('index_v2.html')

@app.route('/api/chat_v2', methods=['POST'])
def chat_v2():
    """
    主对话接口 (v2.0 - 引用关系检测版本)
    """
    print("DEBUG_V2: Entering chat_v2()")  # 唯一标记
    try:
        data = parse_request_json()
        message = (data.get('message') or '').strip()
        if not message:
            return safe_jsonify({'error': '消息不能为空'}, 400)
        
        session_id = data.get('session_id', 'default')
        conv = get_conversation(session_id)
        
        # 调用AGI获取回答
        agi = get_agi()
        result = agi.chat(message, session_id)
        reply = str(result.get('reply', ''))
        
        # 添加问答对到历史
        qa_id = len(conv['messages']) + 1
        conv['messages'].append({
            'q': message,
            'a': reply,
            'id': f'Q{qa_id}',
        })
        
        # 重新构建对话树
        conv['tree'] = build_conversation_tree(conv['messages'])
        print(f"DEBUG: Built tree for {len(conv['messages'])} messages, tree is {type(conv['tree'])}")
        if conv['tree']:
            print(f"DEBUG: Tree has {len(conv['tree'].get('children', []))} children")
        
        return safe_jsonify({
            'session_id': session_id,
            'reply': reply,
            'tree': conv['tree'],
            'current_node': f'Q{qa_id}',
            'version': '4.0.0',
        }, 200)
        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ /api/chat_v2 错误: {e}\n{tb}")
        return safe_jsonify({'error': str(e), 'trace': tb[:3000]}, 500)

@app.route('/api/mindmap', methods=['GET', 'POST'])
def get_mindmap():
    """获取当前对话的脑图（树状结构）"""
    try:
        if request.method == 'POST':
            data = parse_request_json()
            session_id = data.get('session_id', 'default')
        else:
            session_id = request.args.get('session_id', 'default')
        
        conv = get_conversation(session_id)
        return safe_jsonify({
            'success': True,
            'tree': conv.get('tree'),
            'message_count': len(conv.get('messages', [])),
        }, 200)
    except Exception as e:
        return safe_jsonify({'success': False, 'error': str(e)}, 500)

@app.route('/api/node_chat', methods=['POST'])
def node_chat():
    """
    节点追问接口
    
    点击树中某个节点，针对该节点内容追问
    """
    try:
        data = parse_request_json()
        node_id = data.get('node_id', '')
        node_question = data.get('node_question', '')
        user_question = (data.get('question') or '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_question:
            return safe_jsonify({'error': '问题不能为空'}, 400)
        
        # 构造带上下文的提问
        context = f"""
[上下文]
用户正在针对「{node_question}」进行追问。

原始问题：{node_question}
原始回答：{data.get('node_answer', '')[:300]}

用户追问：{user_question}

请针对原始问题和回答，深入回答用户的追问。
"""
        
        agi = get_agi()
        result = agi.chat(context, session_id)
        reply = str(result.get('reply', ''))
        
        # 添加问答对到历史
        conv = get_conversation(session_id)
        qa_id = len(conv['messages']) + 1
        conv['messages'].append({
            'q': user_question,
            'a': reply,
            'id': f'Q{qa_id}',
            'parent': node_id,  # 记录父节点
        })
        
        # 重新构建对话树
        conv['tree'] = build_conversation_tree(conv['messages'])
        
        return safe_jsonify({
            'session_id': session_id,
            'node_id': node_id,
            'question': user_question,
            'reply': reply[:3000],
            'tree': conv['tree'],
            'current_node': f'Q{qa_id}',
        }, 200)
        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ /api/node_chat 错误: {e}\n{tb}")
        return safe_jsonify({'error': str(e), 'trace': tb[:2000]}, 500)

@app.route('/api/state', methods=['GET'])
def get_state():
    try:
        agi = get_agi()
        return safe_jsonify({
            'version': getattr(agi, 'version', '4.0.0'),
            'modules_loaded': 23,
            'status': 'ok',
            'active_sessions': len(_conversation_store),
        }, 200)
    except Exception as e:
        return safe_jsonify({'error': str(e)}, 500)

# ==================== 启动 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🌌 太乙AGI 4.0 — 对话引用关系脑图系统 v2")
    print("   前端: http://localhost:5002")
    print("   API:  http://localhost:5002/api/chat_v2")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
