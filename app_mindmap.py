#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简 Flask 服务 — 太乙AGI 4.0 脑图接口
仅含必需的端点，避开 app.py 中的历史复杂代码
"""
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from flask.json.provider import JSONProvider
import sys, os, traceback, json as pyjson

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

# ==================== Flask 2.2+ 自定义 JSONProvider ====================
class SafeJSONProvider(JSONProvider):
    """处理 complex / numpy 等非JSON原生类型"""
    def dumps(self, obj, **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        return pyjson.dumps(obj, default=self._safe_default, **kwargs)

    def loads(self, s, **kwargs):
        """反序列化JSON（用于request.get_json()）"""
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
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, dict)):
            try:
                return list(obj)[:20]
            except Exception:
                pass
        return str(obj)[:200]

app.json = SafeJSONProvider(app)

# ==================== 强化的 JSON 响应包装 ====================
def safe_jsonify(data, status=200):
    """
    安全的 jsonify 包装：递归清理所有非JSON原生类型，
    确保不会出现 'Object of type X is not JSON serializable' 错误。
    """
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
    response = app.make_response(pyjson.dumps(cleaned, ensure_ascii=False))
    response.status_code = status
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# ==================== 请求解析助手（绕开 Werkzeug json_module 限制） ====================
def parse_request_json():
    """
    直接从 request.get_data() 解析 JSON，
    避免 Werkzeug 的 request.get_json() 用 json_module 绑定导致的 loads 失效。
    """
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

def get_agi():
    global _agi
    with _agi_lock:
        if _agi is None:
            print("🔮 正在初始化太乙AGI 4.0（23个模块）...")
            from CompositeAGI_V2 import CompositeAGI_V2
            _agi = CompositeAGI_V2()
            print("✅ 太乙AGI 4.0 系统就绪！")
    return _agi

# ==================== 复杂度评估 ====================
import re as _re

# 简单问题的特征模式（命中任意一条 → 走轻量路径）
_SIMPLE_PATTERNS = [
    # 基础算术
    _re.compile(r'^[\d\s\+\-\*\/\(\)\.]+[=＝？?]?\s*\d*$'),
    # "X+Y等于几/是多少/=?" 类
    _re.compile(r'[\d一二三四五六七八九十百千万亿]+\s*[\+\-\*\/加减乘除]\s*[\d一二三四五六七八九十百千万亿]+\s*[等是=＝]?'),
    # "X是什么颜色/多少度/几岁"
    _re.compile(r'(是什么|是哪|几岁|多少度|什么颜色|什么意思|是谁|哪年|几月|几号)'),
    # 极短问题（8字以内）且不含复合体/AGI/框架词
    # 不在此处做长度判断，见函数内逻辑
]

_COMPLEX_KEYWORDS = [
    '复合体', '太乙', 'IGCTR', 'AGI', 'ASI', '量子', '意识', '拓扑', '三视界',
    '刘原理', '全息', '涌现', '宇宙', '框架', '分析', '推演', '预测', '系统',
    '机制', '理论', '模型', '算法', '架构', '研究', '哲学', '智能', '神经',
    '为什么', '如何', '怎样', '请解释', '请分析', '帮我', '深度',
]

def _is_simple_question(message: str) -> bool:
    """
    判断是否为简单问题。
    返回 True → 走轻量路径（直接回答，脑图只生成 1-3 个节点）
    返回 False → 走全量 AGI 分析路径
    """
    msg = message.strip()

    # 1. 含复杂关键词 → 复杂问题
    for kw in _COMPLEX_KEYWORDS:
        if kw in msg:
            return False

    # 2. 消息极短（≤15字）且符合简单模式 → 简单问题
    if len(msg) <= 15:
        for pat in _SIMPLE_PATTERNS:
            if pat.search(msg):
                return True
        # 极短且无复杂关键词，也视为简单
        if len(msg) <= 8:
            return True

    # 3. 纯数字/符号/算式
    if _re.match(r'^[\d\s\+\-\*\/\(\)\.=＝？?×÷]+$', msg):
        return True

    return False


def _make_simple_mindmap(message: str, reply: str) -> dict:
    """为简单问题生成极简脑图（1-3个节点）"""
    # 提取回复关键词作为子节点
    children = []
    # 尝试从回复中提取关键句（以句号/换行分隔，取前2个）
    sentences = [s.strip() for s in _re.split(r'[。\n]', reply) if len(s.strip()) > 2][:2]
    for i, s in enumerate(sentences):
        children.append({
            'id': f'simple_{i}',
            'key': f'simple_{i}',
            'name': s[:30],
            'group': 'core',
            'summary': s[:60],
            'children': [],
            'details': {},
            'enabled': True,
        })

    return {
        'id': 'center',
        'key': 'center',
        'name': message[:20],
        'group': 'center',
        'summary': reply[:40],
        'children': children,
        'details': {},
        'enabled': True,
    }


def _simplify_mindmap(mindmap: dict, max_nodes: int = 6) -> dict:
    """
    简化脑图，避免信息过载。
    
    策略：
    1. 中心节点保留
    2. 子节点最多保留 max_nodes-1 个
    3. 超过的子节点合并为"其他分析"节点
    4. 孙节点忽略（只保留2层）
    """
    if not mindmap or 'children' not in mindmap:
        return mindmap
    
    center = {
        'id': mindmap.get('id', 'center'),
        'key': mindmap.get('key', 'center'),
        'name': mindmap.get('name', '问题')[:25],
        'group': 'center',
        'summary': mindmap.get('summary', '')[:50],
        'children': [],
        'details': {},
        'enabled': True,
    }
    
    # 获取子节点并智能排序
    raw_children = mindmap.get('children', [])
    
    # 按名称去重 + 排序（核心在前）
    seen = set()
    prioritized = []
    others = []
    
    for child in raw_children:
        name = child.get('name', '')[:20]
        if name in seen:
            continue
        seen.add(name)
        
        # 核心关键词优先
        core_keywords = ['结论', '本质', '核心', '答案', '定义', '关键']
        if any(kw in name for kw in core_keywords):
            prioritized.append(child)
        else:
            others.append(child)
    
    # 合并所有子节点
    all_children = prioritized + others
    
    # 限制数量
    if len(all_children) > max_nodes - 1:
        kept = all_children[:max_nodes - 2]
        merged = all_children[max_nodes - 2:]
        
        # 创建合并节点
        if merged:
            merged_names = [c.get('name', '')[:15] for c in merged[:3]]
            center['children'].append({
                'id': 'others',
                'key': 'others',
                'name': f'其他({len(merged)}项)',
                'group': 'core',
                'summary': '、'.join(merged_names),
                'children': [],
                'details': {},
                'enabled': True,
            })
    else:
        kept = all_children
    
    # 只保留子节点，忽略孙节点（避免层级过深）
    for child in kept:
        child['children'] = []  # 去掉孙节点
        child['summary'] = (child.get('summary') or '')[:30]
        child['name'] = (child.get('name') or '')[:20]
        center['children'].append(child)
    
    return center


# ==================== 端点 ====================
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat_v2', methods=['POST'])
def chat_v2():
    """
    调用 CompositeAGI_V2.chat()，返回含脑图数据的JSON
    简单问题走轻量路径，复杂问题走全量 AGI 分析
    """
    try:
        data = parse_request_json()
        message = (data.get('message') or '').strip()
        if not message:
            return safe_jsonify({'error': '消息不能为空'}, 400)

        session_id = data.get('session_id', 'default')

        # ── 复杂度判断 ──────────────────────────────────────
        if _is_simple_question(message):
            # 轻量路径：直接用 Python 简单回答，不启动全量 AGI
            reply = _simple_answer(message)
            mindmap = _make_simple_mindmap(message, reply)
            print(f"⚡ [轻量路径] 问题: {message!r}")
            return safe_jsonify({
                'session_id': session_id,
                'input':      message,
                'reply':      reply,
                'analysis':   {'mode': 'simple', 'note': '问题较简单，已使用轻量回答'},
                'mindmap':    mindmap,
                'version':    '4.0.0',
                'simple':     True,
            }, 200)

        # ── 全量 AGI 路径 ───────────────────────────────────
        agi = get_agi()
        result = agi.chat(message, session_id)

        # 从分析结果构建有意义的脑图
        analysis = result.get('analysis', {})
        simple_mindmap = _analysis_to_mindmap(message, analysis, max_nodes=6)

        return safe_jsonify({
            'session_id': session_id,
            'input':      message,
            'reply':      str(result.get('reply', ''))[:2000],
            'analysis':   result.get('analysis', {}),
            'mindmap':    simple_mindmap,
            'version':    str(result.get('version', '4.0.0'))[:50],
            'simple':     False,
        }, 200)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ /api/chat_v2 错误: {e}\n{tb}")
        return safe_jsonify({'error': str(e), 'trace': tb[:3000]}, 500)


def _analysis_to_mindmap(question: str, analysis: dict, max_nodes: int = 6) -> dict:
    """
    将AGI分析结果转换为可读的脑图结构。
    从 module_results 提取关键结论作为节点。
    """
    center = {
        'id': 'center',
        'key': 'center',
        'name': question[:20] or '分析',
        'group': 'center',
        'summary': '太乙AGI分析结果',
        'children': [],
        'details': {},
        'enabled': True,
    }

    module_results = analysis.get('module_results', {})
    if not module_results:
        # 没有模块结果，返回简单脑图
        center['children'].append({
            'id': 'result', 'key': 'result',
            'name': '分析完成', 'group': 'core',
            'summary': '系统已完成分析',
            'children': [], 'details': {}, 'enabled': True,
        })
        return center

    # 模块名称映射：字段名 → 可读名称
    module_names = {
        'topological_defect': '拓扑缺陷分析',
        'fractal_analysis': '分形维数分析',
        'minimum_action': '最小作用量原理',
        'phase_field': '相位场知识表示',
        'ftel_operator': 'Ftel算子诊断',
        'quantum_computation': '量子场论计算',
        'wuxing_network': '五行网络协同',
        'igctr_resonance': 'IGCTR三元共振',
        'aleph_unification': '阿列夫-阿拉统一',
        'antimonotonicity': '反单调性信息公理',
        'cosmic_design': '宇宙五重设计偏好',
        'world_model': '世界模型三元共振',
        'causal_convergence': '因果收敛评估',
        'cognitive_pressure': '认知压力监测',
        'consciousness_emergence': '意识涌现探测',
        'federation_protocol': '联邦宇宙协议',
    }

    # 从每个模块提取关键结论
    children = []
    for key, result in module_results.items():
        name = module_names.get(key, key)
        summary = _extract_module_summary(key, result)

        # 为每个模块创建节点，并为 details 中的每个条目创建子节点
        module_children = []
        details = result if isinstance(result, dict) else {}
        for detail_key, detail_value in details.items():
            if detail_value is not None and detail_key not in ('status', 'timestamp'):
                # 将 detail 条目格式化为子节点
                detail_str = f"{detail_key}: {detail_value}"
                module_children.append({
                    'id': f"{key}__{detail_key}",
                    'key': detail_key,
                    'name': detail_str[:40],
                    'group': 'detail',
                    'summary': str(detail_value)[:60],
                    'children': [],
                    'details': {},
                    'enabled': True,
                })

        children.append({
            'id': key,
            'key': key,
            'name': name[:20],
            'group': 'core',
            'summary': summary[:40],
            'children': module_children,
            'details': result,
            'enabled': True,
        })

    # 限制节点数量
    if len(children) > max_nodes - 1:
        kept = children[:max_nodes - 2]
        merged = children[max_nodes - 2:]
        kept.append({
            'id': 'others', 'key': 'others',
            'name': f'其他({len(merged)}项)',
            'group': 'others',
            'summary': '、'.join([c['name'][:10] for c in merged[:3]]),
            'children': [], 'details': {}, 'enabled': True,
        })
        children = kept

    center['children'] = children
    return center


def _extract_module_summary(module_key: str, result: dict) -> str:
    """从模块结果中提取一句话摘要"""
    if not result or not isinstance(result, dict):
        return '分析完成'

    # 各模块的摘要提取逻辑
    extractors = {
        'topological_defect': lambda r:
            f"缺陷{r.get('defects_detected', '?')}个，稳定性{r.get('stability', '?')}",
        'fractal_analysis': lambda r:
            f"D_f={r.get('fractal_dimension', '?'):.2f}，{'临界' if r.get('is_critical') else '未临界'}",
        'minimum_action': lambda r:
            f"作用量={r.get('action_value', '?'):.3f}" if r.get('action_functional_defined') else '未定义',
        'phase_field': lambda r:
            f"相干性{r.get('phase_coherence', '?')}" if r.get('knowledge_activated') else '未激活',
        'ftel_operator': lambda r:
            f"证候：{r.get('syndrome_type', 'unknown')}" if r.get('syndrome_diagnosed') else '未诊断',
        'quantum_computation': lambda r:
            f"不确定性={r.get('bid_ask_spread', '?')}" if r.get('path_integral_computed') else '未计算',
        'wuxing_network': lambda r:
            '模块协同平衡' if r.get('balanced') else '模块协同中',
        'igctr_resonance': lambda r:
            f"共振强度{r.get('resonance_strength', '?'):.3f}",
        'aleph_unification': lambda r:
            f"统一场{r.get('unification_field_size', '?')}单元" if r.get('unified') else '未统一',
        'antimonotonicity': lambda r:
            f"信息量{r.get('query_information', '?'):.3f}",
        'cosmic_design': lambda r:
            f"主导偏好={r.get('dominant_preference', '?')}",
        'world_model': lambda r:
            f"I-G-C={r.get('igc_resonance', '?'):.3f}",
        'causal_convergence': lambda r:
            f"收敛{r.get('convergence_score', '?')}%" if r.get('converged') else '未收敛',
        'cognitive_pressure': lambda r:
            f"总压力{r.get('total_pressure', '?')}，过载{r.get('overload_nodes', '?')}个",
        'consciousness_emergence': lambda r:
            f"涌现概率{r.get('emergence_probability', '?')}%" if r.get('emergence_detected') else '未涌现',
        'federation_protocol': lambda r:
            f"最优协议={r.get('optimal_protocol', '?')}",
    }

    extractor = extractors.get(module_key)
    if extractor:
        try:
            return extractor(result)
        except Exception:
            pass

    # 兜底：取第一个非None值
    for k, v in result.items():
        if v is not None and not isinstance(v, (dict, list)):
            return f"{k}={str(v)[:20]}"
    return '分析完成'


def _simple_answer(message: str) -> str:
    """
    对简单问题给出直接回答（无需调用 AGI 框架）。
    支持：基本算术、简单事实问句。
    """
    msg = message.strip().rstrip('？?。！!')

    # 尝试计算算术表达式
    expr = msg
    # 中文数字和运算符替换
    zh_map = {
        '加': '+', '减': '-', '乘': '*', '除': '/',
        '×': '*', '÷': '/', '＋': '+', '－': '-',
        '等于': '', '是': '', '几': '', '多少': '',
        '零': '0', '一': '1', '二': '2', '三': '3',
        '四': '4', '五': '5', '六': '6', '七': '7',
        '八': '8', '九': '9', '十': '10', '百': '*100',
    }
    for zh, en in zh_map.items():
        expr = expr.replace(zh, en)
    expr = _re.sub(r'[^\d\+\-\*\/\(\)\.\s]', '', expr).strip()

    if expr:
        try:
            val = eval(expr, {"__builtins__": {}})  # nosec — 已清理非算术字符
            if isinstance(val, float) and val == int(val):
                val = int(val)
            return f"{message.rstrip('？?')} = **{val}**\n\n这是一道基础运算题，答案是 {val}。"
        except Exception:
            pass

    # 无法计算 → 尝试常见问题匹配
    return _answer_common_question(msg) or \
           f"「{msg}」—— 我是太乙AI，一个基于复合体理学的智能助手。有具体问题欢迎问我！"


def _answer_common_question(msg: str) -> str:
    """
    尝试回答常见简单问题。
    返回 None 表示无法回答。
    """
    # AI身份类
    if any(k in msg for k in ['男孩', '女孩', '男的', '女的', '性别', '男的女的']):
        return "我是一个AI助手，没有性别之分。我是由代码和数据构成的智能系统，可以帮助你回答问题和进行分析。"
    
    if any(k in msg for k in ['叫什么', '名字', '是谁', '你叫']):
        return "我是太乙AI，基于复合体理学和IGCTR理论框架构建的智能助手。叫我「太乙」就好！"
    
    if any(k in msg for k in ['你是谁', 'what are you', 'who are you']):
        return "我是太乙AI——一个融合东方哲学（太乙、复合体理学）与现代AGI技术的智能助手。基于IGCTR v2.3框架构建。"

    # 简单时间问题
    if any(k in msg for k in ['今天几号', '今天星期', '现在几点']):
        from datetime import datetime
        now = datetime.now()
        weekdays = ['一','二','三','四','五','六','日']
        return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M')}，星期{weekdays[now.weekday()]}。"

    # 你好吗
    if any(k in msg for k in ['你好', '你好吗', '最近如何']):
        return "你好！我是太乙AI，运行状态良好，随时准备为你服务。有什么我可以帮你的吗？"

    # 感谢/再见
    if any(k in msg for k in ['谢谢', '感谢', 'thx', 'thanks']):
        return "不客气！有问题随时问我。😊"
    
    if any(k in msg for k in ['再见', '拜拜', 'bye']):
        return "再见！期待下次对话。👋"

    # 能做什么
    if any(k in msg for k in ['能做什么', '能帮我', '有什么功能', '你会什么']):
        return "我可以：\n1. 回答问题（简单/复杂都行）\n2. 分析问题（复合体理学视角）\n3. 生成脑图\n4. 代码编写\n5. 数学计算\n6. 深度推理\n\n直接问我任何问题！"

    # 不知道怎么回答 → 返回 None，让调用方生成兜底回复
    return None

@app.route('/api/mindmap', methods=['POST'])
def get_mindmap():
    try:
        data = parse_request_json()
        message = (data.get('message') or '').strip()
        if not message:
            return safe_jsonify({'error': '消息不能为空'}, 400)
        agi = get_agi()
        result = agi.chat(message, data.get('session_id'))
        return safe_jsonify({
            'success': True,
            'mindmap': result.get('mindmap', {}),
            'reply': result.get('reply', '')
        }, 200)
    except Exception as e:
        return safe_jsonify({'success': False, 'error': str(e)}, 500)

@app.route('/api/node_chat', methods=['POST'])
def node_chat():
    """
    节点追问接口 — 点击脑图节点后的深入对话
    输入: { session_id, node_key, node_label, node_details, question, history }
    输出: { reply, grow_nodes: [...新分支...], patch_nodes: [...修正节点...] }
    """
    try:
        data = parse_request_json()
        node_key    = data.get('node_key', '')
        node_label  = data.get('node_label', '')
        node_details= data.get('node_details', {})
        question    = (data.get('question') or '').strip()
        session_id  = data.get('session_id', 'default')
        history     = data.get('history', [])   # [{role, content}, ...]

        if not question:
            return safe_jsonify({'error': '问题不能为空'}, 400)

        # 构造带节点上下文的增强提问
        context_msg = (
            f"[节点上下文: {node_label}]\n"
            f"节点数据: {pyjson.dumps(node_details, ensure_ascii=False, default=str)[:600]}\n"
            f"历史对话: {pyjson.dumps(history[-4:], ensure_ascii=False, default=str)[:400]}\n\n"
            f"用户追问: {question}"
        )

        agi = get_agi()
        result = agi.chat(context_msg, session_id)
        reply = str(result.get('reply', ''))

        # 从回复中生成新生长节点
        grow_nodes = _build_grow_nodes(node_key, node_label, question, reply)
        # 从回复中检测修正指令
        patch_nodes = _detect_patch_nodes(reply, node_key)

        return safe_jsonify({
            'session_id': session_id,
            'node_key':   node_key,
            'question':   question,
            'reply':      reply[:3000],
            'grow_nodes': grow_nodes,
            'patch_nodes': patch_nodes,
        }, 200)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ /api/node_chat 错误: {e}\n{tb}")
        return safe_jsonify({'error': str(e), 'trace': tb[:2000]}, 500)


def _build_grow_nodes(parent_key: str, parent_label: str, question: str, reply: str) -> list:
    """从对话结果构建新生长节点列表"""
    import re
    nodes = []

    # 从回复中提取段落作为子节点（以数字列表项、##标题等为依据）
    # 策略1：提取 1. 2. 3. 编号段落
    numbered = re.findall(r'\d+\.\s+\*{0,2}([^*\n]{5,60})\*{0,2}', reply)
    for i, txt in enumerate(numbered[:6]):
        nodes.append({
            'id':       f"{parent_key}__q{abs(hash(question))%9999}_{i}",
            'parent':   parent_key,
            'name':     txt.strip()[:40],
            'group':    'grow',
            'summary':  txt.strip()[:80],
            'children': [],
            'details':  {},
            'is_new':   True,
        })

    # 策略2：没有编号列表时，取回复首句作为单节点
    if not nodes:
        first_line = reply.strip().split('\n')[0][:60]
        if first_line:
            nodes.append({
                'id':       f"{parent_key}__q{abs(hash(question))%9999}_0",
                'parent':   parent_key,
                'name':     first_line,
                'group':    'grow',
                'summary':  first_line,
                'children': [],
                'details':  {},
                'is_new':   True,
            })
    return nodes


def _detect_patch_nodes(reply: str, node_key: str) -> list:
    """
    检测回复中是否包含对已有节点的修正指令
    关键词：修正为/更新为/应该是/实为
    """
    import re
    patches = []
    correction_patterns = [
        r'将"([^"]+)"(?:修正|更新|改为|订正)为"([^"]+)"',
        r'"([^"]+)"应(?:该|当)是"([^"]+)"',
        r'([^\s，,。]+)实为([^\s，,。\n]+)',
    ]
    for pat in correction_patterns:
        for m in re.finditer(pat, reply):
            patches.append({
                'node_key':  node_key,
                'old_label': m.group(1),
                'new_label': m.group(2),
            })
    return patches[:5]


@app.route('/api/state', methods=['GET'])
def get_state():
    try:
        agi = get_agi()
        return safe_jsonify({
            'version': getattr(agi, 'version', '4.0.0'),
            'modules_loaded': 23,
            'status': 'ok'
        }, 200)
    except Exception as e:
        return safe_jsonify({'error': str(e)}, 500)

# ==================== 启动 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🌌 太乙AGI 4.0 脑图服务")
    print("   前端: http://localhost:5002")
    print("   API:  http://localhost:5002/api/chat_v2")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
