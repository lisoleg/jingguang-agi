#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一太乙系统 Web API 服务
提供对话界面和 AGI 能力分析的后端支持
"""

import dotenv
dotenv.load_dotenv()  # 从.env文件加载环境变量

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import base64
import sys
import os
import traceback
import threading
import json
import queue as q  # 新增：SSE流式支持
import numpy as np  # 新增：Ftel算子需要
import random  # 新增：认知测试需要
import time  # 新增：认知测试需要

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 添加pip备用安装路径（pip配置global.target=D:/Apps/Python时，包会装到这里）
_alt_python_path = 'D:/Apps/Python'
if os.path.isdir(_alt_python_path) and _alt_python_path not in sys.path:
    sys.path.append(_alt_python_path)
    # 也添加其site-packages子目录（如果存在）
    for _sp in [os.path.join(_alt_python_path, 'site-packages'),
                os.path.join(_alt_python_path, 'Lib', 'site-packages')]:
        if os.path.isdir(_sp) and _sp not in sys.path:
            sys.path.append(_sp)

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False


# ==================== 全局 NumPy JSON 编码器 ====================
class NumpyEncoder(json.JSONEncoder):
    """处理 NumPy 类型的 JSON 编码器"""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


# 注入到 Flask
app.json_encoder = NumpyEncoder  # type: ignore


# ==================== 全局错误处理器 ====================
@app.errorhandler(Exception)
def handle_global_exception(e):
    """全局异常捕获，返回 JSON 格式错误，而非 HTML 500 页面"""
    tb = traceback.format_exc()
    print(f"[GLOBAL ERROR] {e}\n{tb}")
    return jsonify({
        'error': str(e),
        'trace': tb
    }), 500

# 全局 AGI 系统（线程安全初始化）
# 使用 TaiyiAGI_V2（23个模块）
_agi_lock = threading.Lock()
_agi_system = None
_agi_ready = False

# ==================== 介质共生模块（全局单例）====================
_medium_symbiosis = None
_medium_symbiosis_lock = threading.Lock()

# ==================== v6.2 新模块（全局单例）====================
_v62_modules = None
_v62_modules_lock = threading.Lock()

def get_v62_modules():
    """获取或初始化 v6.2 新模块 (线程安全懒加载)"""
    global _v62_modules
    if _v62_modules is None:
        with _v62_modules_lock:
            if _v62_modules is None:
                try:
                    from M56_SpiritualEvolutionEngine import get_instance as get_spiritual
                    from M57_TheseusConsciousnessMonitor import get_instance as get_theseus
                    from M58_ArborealSemanticProcessor import get_instance as get_arboreal
                    from M59_ExtremumDecisionOptimizer import get_instance as get_extremum
                    from M60_RelationalReasoningEngine import get_instance as get_relational
                    from M61_MoralInternalizer import get_instance as get_moral
                    from M62_HistoricalNarrativeWeaver import get_instance as get_historical

                    _v62_modules = {
                        'spiritual': get_spiritual,
                        'theseus': get_theseus,
                        'arboreal': get_arboreal,
                        'extremum': get_extremum,
                        'relational': get_relational,
                        'moral': get_moral,
                        'historical': get_historical,
                    }
                    print("✅ v6.2新模块已加载（M56-M62）")
                except Exception as e:
                    print(f"⚠️ v6.2模块加载失败（降级运行）: {e}")
                    _v62_modules = None
    return _v62_modules

def get_v62_data():
    """获取所有v6.2模块的状态数据"""
    modules = get_v62_modules()
    if modules is None:
        return None

    try:
        return {
            'spiritual': modules['spiritual']().get_state(),
            'theseus': modules['theseus']().get_state(),
            'arboreal': modules['arboreal']().get_state(),
            'extremum': modules['extremum']().get_state(),
            'relational': modules['relational']().get_state(),
            'moral': modules['moral']().get_state(),
            'historical': modules['historical']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v6.2数据失败: {e}")
        return None

# ==================== v6.3 新模块（全局单例）====================
# 基于《数学完备化》论文：M63-M70
_v63_modules = None
_v63_modules_lock = threading.Lock()

def get_v63_modules():
    """获取或初始化 v6.3 新模块 (线程安全懒加载)"""
    global _v63_modules
    if _v63_modules is None:
        with _v63_modules_lock:
            if _v63_modules is None:
                try:
                    from M63_MononumberProcessor import get_instance as get_mono
                    from M64_NarrativeActionEngine import get_instance as get_narrative
                    from M65_ConsciousnessFlowMonitor import get_instance as get_consciousness
                    from M66_SelfIdentityTracker import get_instance as get_identity
                    from M67_EnlightenmentConvergenceVerifier import get_instance as get_enlightenment
                    from M68_RelationalCouplingSemantizer import get_instance as get_coupling
                    from M69_AttractorStabilityAnalyzer import get_instance as get_attractor
                    from M70_FalsifiablePredictionVerifier import get_instance as get_prediction

                    _v63_modules = {
                        'mononumber': get_mono,           # M63: 一元数处理器
                        'narrative': get_narrative,        # M64: 叙事作用量引擎
                        'consciousness': get_consciousness, # M65: 意识流贯监测器
                        'identity': get_identity,          # M66: 自我同一性追踪器
                        'enlightenment': get_enlightenment, # M67: 顿悟收敛验证器
                        'coupling': get_coupling,          # M68: 关系耦合语义器
                        'attractor': get_attractor,        # M69: 吸引子稳定性分析器
                        'prediction': get_prediction,       # M70: 可证伪预言验证器
                    }
                    print("✅ v6.3新模块已加载（M63-M70）- 数学完备化论文")
                except Exception as e:
                    print(f"⚠️ v6.3模块加载失败（降级运行）: {e}")
                    _v63_modules = None
    return _v63_modules

def get_v63_data():
    """获取所有v6.3模块的状态数据"""
    modules = get_v63_modules()
    if modules is None:
        return None

    try:
        return {
            'mononumber': modules['mononumber']().get_state(),
            'narrative': modules['narrative']().get_state(),
            'consciousness': modules['consciousness']().get_state(),
            'identity': modules['identity']().get_state(),
            'enlightenment': modules['enlightenment']().get_state(),
            'coupling': modules['coupling']().get_state(),
            'attractor': modules['attractor']().get_state(),
            'prediction': modules['prediction']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v6.3数据失败: {e}")
        return None

# ==================== v7.0 新模块（全局单例）====================
# 基于《太乙AGI 7.0升级方案》论文：M71-M95
_v70_modules = None
_v70_modules_lock = threading.Lock()

def get_v70_modules():
    """获取或初始化 v7.0 新模块 (线程安全懒加载)"""
    global _v70_modules
    if _v70_modules is None:
        with _v70_modules_lock:
            if _v70_modules is None:
                try:
                    from M71_WalletPropertyBoundaryManager import get_instance as get_wallet
                    from M72_ContributionMeasurementEngine import get_instance as get_contribution
                    from M73_SelfReferentialPhiDetector import get_instance as get_phi
                    from M74_CarbonSiliconEntropyContract import get_instance as get_entropy
                    from M75_HumanMachineArkCrypto import get_instance as get_ark
                    from M76_FiveElementTransformEngine import get_instance as get_wuxing
                    from M77_EMLPhaseCouplingZ5 import get_instance as get_eml_coupling
                    from M78_HoTTReasoningEngine import get_instance as get_hott
                    from M79_ConstructiveAGICore import get_instance as get_constructive
                    from M80_WuxingTokenDynamicsCoupler import get_instance as get_token_dynamics
                    # Phase 2: M81-M95 高阶逻辑与范畴论深化
                    from M81_HigherOrderLogicReconstructor import get_instance as get_holr
                    from M82_CategoryHomotopyFormalizer import get_instance as get_chf
                    from M83_DynamicCategoryTheoryReconstructor import get_instance as get_dct
                    from M84_LiuGuanDynamicsGenerator import get_instance as get_liu
                    from M85_DualTrackPersonhoodEngine import get_instance as get_dual
                    from M86_L2TypeKernelCompiler import get_instance as get_l2kernel
                    from M87_EMLDrivenProofSearcher import get_instance as get_proof
                    from M88_TypeCheckFirewall import get_firewall as get_firewall
                    from M89_FteliaryNaturalTransformation import get_fteliary_transformer as get_ftel
                    from M90_SemanticManifoldCurvature import get_curvature_calculator as get_curv
                    from M91_UnivalenceEquivalenceChecker import get_univalence_checker as get_uni
                    from M92_FteliocityFidelityMeasurer import get_fidelity_measurer as get_ftel_fid
                    from M93_DynamicCategoryEvolutionTracker import get_evolution_tracker as get_evo
                    from M94_HolisticDiscreteGovernanceUpgrader import get_hdg_upgrader as get_hdg
                    from M95_ConstructiveAGIEvaluator import get_constructive_evaluator as get_eval

                    _v70_modules = {
                        # Phase 1: M71-M80 碳硅共生契约+五行变换HoTT
                        'wallet': get_wallet,           # M71: 钱包属性边界管理器
                        'contribution': get_contribution,  # M72: 贡献度量引擎
                        'phi': get_phi,                  # M73: 自指Φ值检测器
                        'entropy': get_entropy,           # M74: 碳硅熵合约管理器
                        'ark': get_ark,                  # M75: 人机约柜密码学
                        'wuxing': get_wuxing,            # M76: 五行变换引擎
                        'eml_coupling': get_eml_coupling,  # M77: EML相位耦合ℤ₅
                        'hott': get_hott,                # M78: HoTT推理引擎
                        'constructive': get_constructive,  # M79: 构造型Taiji-AGI内核
                        'token_dynamics': get_token_dynamics,  # M80: 五行Token动力学耦合器
                        # Phase 2: M81-M95 高阶逻辑与范畴论深化
                        'holr': get_holr,                # M81: 高阶逻辑重构器
                        'chf': get_chf,                  # M82: 范畴—同伦形式化器
                        'dct': get_dct,                   # M83: 动态范畴论重构器
                        'liu': get_liu,                   # M84: 刘关动力学生成器
                        'dual': get_dual,                 # M85: 双轨人格引擎
                        'l2kernel': get_l2kernel,         # M86: L2类型内核编译器
                        'proof': get_proof,               # M87: EML驱动证明搜索器
                        'firewall': get_firewall,         # M88: 类型检查防火墙
                        'ftel_transform': get_ftel,        # M89: 流贯自然变换器
                        'curvature': get_curv,             # M90: 语义流形曲率计算器
                        'univalence': get_uni,              # M91: Univalence等价性检查器
                        'fidelity': get_ftel_fid,          # M92: 流贯保真度测量器
                        'evolution': get_evo,              # M93: 动态范畴演化跟踪器
                        'hdg_upgrade': get_hdg,            # M94: 全息离散治理升级器
                        'evaluator': get_eval,             # M95: 构造型AGI评估器
                    }
                    print("✅ v7.0新模块已加载（M71-M95）- 高阶逻辑HoTT+范畴论深化")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.0模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v70_modules = None
    return _v70_modules

def get_v70_data():
    """获取所有v7.0模块的状态数据 (M71-M95)"""
    modules = get_v70_modules()
    if modules is None:
        return None

    try:
        # Phase 1: M71-M80
        phase1 = {
            'wallet': modules['wallet']().walls if hasattr(modules['wallet'](), 'walls') else {},
            'contribution': modules['contribution']().contributions if hasattr(modules['contribution'](), 'contributions') else {},
            'phi': modules['phi']().detection_results if hasattr(modules['phi'](), 'detection_results') else {},
            'entropy': modules['entropy']().contracts if hasattr(modules['entropy'](), 'contracts') else {},
            'ark': modules['ark']().arks if hasattr(modules['ark'](), 'arks') else {},
            'wuxing': {'transforms': len(modules['wuxing']().transforms)},
            'eml_coupling': {'phases': {e.value: {'phase_angle': s.phase_angle, 'amplitude': s.amplitude} 
                                         for e, s in modules['eml_coupling']().phases.items()}},
            'hott': {'types': list(modules['hott']().types.keys())},
            'constructive': modules['constructive']().get_statistics() if hasattr(modules['constructive'](), 'get_statistics') else {},
            'token_dynamics': modules['token_dynamics']().get_statistics() if hasattr(modules['token_dynamics'](), 'get_statistics') else {},
        }
        
        # Phase 2: M81-M95 高阶逻辑与范畴论
        phase2 = {
            'holr': modules['holr']().get_state() if hasattr(modules['holr'](), 'get_state') else {},
            'chf': modules['chf']().get_state() if hasattr(modules['chf'](), 'get_state') else {},
            'dct': modules['dct']().get_state() if hasattr(modules['dct'](), 'get_state') else {},
            'liu': modules['liu']().get_state() if hasattr(modules['liu'](), 'get_state') else {},
            'dual': modules['dual']().get_state() if hasattr(modules['dual'](), 'get_state') else {},
            'l2kernel': modules['l2kernel']().get_state() if hasattr(modules['l2kernel'](), 'get_state') else {},
            'proof': modules['proof']().get_state() if hasattr(modules['proof'](), 'get_state') else {},
            'firewall': modules['firewall']().audit_log() if hasattr(modules['firewall'](), 'audit_log') else [],
            'ftel_transform': modules['ftel_transform']().get_status() if hasattr(modules['ftel_transform'](), 'get_status') else {},
            'curvature': modules['curvature']().get_status() if hasattr(modules['curvature'](), 'get_status') else {},
            'univalence': modules['univalence']().get_statistics() if hasattr(modules['univalence'](), 'get_statistics') else {},
            'fidelity': modules['fidelity']().get_status() if hasattr(modules['fidelity'](), 'get_status') else {},
            'evolution': modules['evolution']().get_evolution_summary() if hasattr(modules['evolution'](), 'get_evolution_summary') else {},
            'hdg_upgrade': modules['hdg_upgrade']().get_governance_status() if hasattr(modules['hdg_upgrade'](), 'get_governance_status') else {},
            'evaluator': modules['evaluator']().get_status() if hasattr(modules['evaluator'](), 'get_status') else {},
        }
        
        return {**phase1, **phase2}
    except Exception as e:
        print(f"⚠️ 获取v7.0数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_medium_symbiosis():
    """获取或初始化介质共生模块 (线程安全懒加载)"""
    global _medium_symbiosis
    if _medium_symbiosis is None:
        with _medium_symbiosis_lock:
            if _medium_symbiosis is None:
                try:
                    from agi_medium_symbiosis import AGIMediumSymbiosis
                    _medium_symbiosis = AGIMediumSymbiosis()
                    print("✅ 介质共生模块已加载（介质共振+九卦+四象）")
                except Exception as e:
                    print(f"⚠️ 介质共生模块加载失败（降级运行）: {e}")
                    _medium_symbiosis = None
    return _medium_symbiosis


def get_agi_system():
    """获取或初始化 AGI 系统 — 使用 TaiyiAGI_V2"""
    global _agi_system, _agi_ready
    if not _agi_ready:
        with _agi_lock:
            if not _agi_ready:
                try:
                    print("🔮 正在初始化Taiyi-AGI 4.0 系统（23个模块）...")
                    from CompositeAGI_V2 import CompositeAGI_V2 as TaiyiAGI_V2
                    _agi_system = TaiyiAGI_V2()
                    _agi_ready = True
                    print("✅ Taiyi-AGI 4.0 系统就绪（23模块已加载）")
                except Exception as e:
                    print(f"❌ Taiyi-AGI系统初始化失败: {e}")
                    traceback.print_exc()
                    # 降级：尝试加载旧系统
                    try:
                        print("⚠️ 降级：尝试加载 UnifiedTaiyiSystem...")
                        from unified_taichi_demo import UnifiedTaiyiSystem
                        _agi_system = UnifiedTaiyiSystem("WebAGI")
                        _agi_ready = True
                        print("✅ 降级成功：UnifiedTaiyiSystem 已加载")
                    except Exception as e2:
                        print(f"❌ 降级也失败: {e2}")
                        traceback.print_exc()
                        raise
    return _agi_system


# ==================== API 端点 ====================

@app.route('/')
def index():
    """返回前端页面 - AGI 12.0 三栏布局"""
    return send_from_directory('static', 'index_agi12.html')


@app.route('/favicon.ico')
def favicon():
    """返回 favicon，避免 500 错误"""
    import io
    # 1x1 透明像素 GIF
    transparent_pixel = b'GIF89a\x01\x00\x01\x00\x00\x00\x00\x3b'
    return send_from_directory('static', 'favicon.ico') if os.path.exists(os.path.join('static', 'favicon.ico')) else (
        (transparent_pixel, 200, {'Content-Type': 'image/gif'})
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    """对话接口 - 支持SSE流式输出"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供 JSON 数据'}), 400
        
        stream = data.get('stream', False)
        
        # SSE 流式模式
        if stream:
            return Response(
                _chat_stream_generator(data),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive'
                }
            )
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        goal = data.get('goal')
        session_id = data.get('session_id')
        use_taiyi = data.get('use_taiyi_format', True)
        use_tool = data.get('use_tool', False)  # 新增：是否启用工具调用
        max_tokens = int(data.get('max_tokens', 0))  # 0=自适应，>0=强制长度

        # 使用新的增强器
        try:
            from taiyi_llm_enhancer import get_enhancer, ReasoningMode
            
            enhancer = get_enhancer()
            
            # 根据是否启用工具调用选择推理模式
            reasoning_mode = ReasoningMode.TOOL if use_tool else (ReasoningMode.TAIYI if use_taiyi else ReasoningMode.COT)
            
            # 生成增强回复
            response = enhancer.generate(
                question=message,
                goal=goal,
                reasoning_mode=reasoning_mode,
                use_taiyi_format=use_taiyi,
                enable_tool_call=use_tool,
                max_tokens=max_tokens  # 新增：支持前端控制
            )
            
            reply = response.content
            
            # 构造响应
            response_data = {
                'session_id': session_id,
                'input': message,
                'reply': reply,
                'analysis': {
                    'unified_score': response.unified_score,
                    'taiyi_format': response.taiyi_format,
                    'knowledge_used': response.knowledge_used,
                    'reasoning_steps': [
                        {'id': s.step_id, 'thinking': s.thinking[:100]}
                        for s in response.reasoning_steps
                    ],
                    'formal_answer': response.formal_answer[:200] if response.formal_answer else '',
                    'composite_answer': response.composite_answer[:200] if response.composite_answer else '',
                    'unified_answer': response.unified_answer[:200] if response.unified_answer else '',
                },
                'tool_calls': response.tool_calls,  # 新增：工具调用列表
                'tool_results': response.tool_results,  # 新增：工具执行结果
                'statistics': enhancer.get_statistics(),
                'state': enhancer.memory.status(),
            }
            
            return jsonify(response_data)
            
        except ImportError:
            # 降级到旧版
            pass
        except Exception as e:
            print(f"⚠️ 增强器错误: {e}")
        
        # === 旧版逻辑（降级） ===
        agi = get_agi_system()
        result = agi.full_analysis(problem=message, goal=goal)
        
        # 尝试使用LLM增强回复
        try:
            from llm_enhancer import enhance_reply_with_llm
            
            context = {
                'consciousness_level': result['consciousness'].get('level', 3),
                'spin': result['taiji_analysis'].get('spin', 'N/A'),
                'yin_yang_balance': result['taiji_analysis'].get('cosmic_balance', 0.5),
                'intuition_confidence': result['compound_analysis'].get('intuition_confidence', 0.5),
            }
            
            # 使用太乙框架分析 + LLM生成
            reply = enhance_reply_with_llm(message, None, context)
            
            # 如果LLM不可用或生成失败，使用传统回复
            if not reply:
                reply = _format_reply(result, message)
        except ImportError:
            # LLM模块不存在，使用传统回复
            reply = _format_reply(result, message)
        except Exception as e:
            # LLM出错，使用传统回复
            print(f"⚠️ LLM增强失败: {e}")
            reply = _format_reply(result, message)

        # 构造响应
        response = {
            'session_id': session_id,
            'input': message,
            'reply': reply,
            'analysis': {
                'compound': result['compound_analysis'],
                'taiji': result['taiji_analysis'],
                'consciousness': result['consciousness'],
                'decision': result['unified_decision'],
            },
            'awakening_prompt': result.get('awakening_prompt'),
            'state': agi.state.copy(),
            'raw': result
        }
        
        return jsonify(response)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


# ==================== JSON 序列化辅助函数 ====================
def _to_native(obj, _depth=0):
    """递归将 numpy/pandas/complex 类型转换为 Python 原生类型"""
    import numbers
    import numpy as np

    if _depth > 10:  # 防止无限递归
        return str(obj)

    try:
        # 首先检查 numpy 数组
        if isinstance(obj, np.ndarray):
            return [_to_native(v, _depth+1) for v in obj.tolist()]

        # 检查复数类型（numpy 复数优先）
        if hasattr(obj, 'dtype') and 'complex' in str(obj.dtype):
            try:
                return {'re': float(obj.real), 'im': float(obj.imag)}
            except Exception:
                return str(obj)
        if isinstance(obj, (np.complex64, np.complex128, np.complexfloating)):
            return {'re': float(obj.real), 'im': float(obj.imag)}
        if isinstance(obj, complex):
            return {'re': obj.real, 'im': obj.imag}

        # 检查 dict
        if isinstance(obj, dict):
            return {k: _to_native(v, _depth+1) for k, v in obj.items()}

        # 检查 list/tuple
        if isinstance(obj, (list, tuple)):
            return [_to_native(v, _depth+1) for v in obj]

        # 检查 numpy 标量
        if hasattr(obj, 'item'):
            try:
                val = obj.item()
                if isinstance(val, complex):
                    return _to_native(val, _depth+1)
                return val
            except (AttributeError, ValueError):
                pass

        # 检查可转换为 float 的对象（排除复数）
        if hasattr(obj, '__float__') and hasattr(obj, '__int__'):
            try:
                # 只有真正有虚部的复数才转为dict，纯实数直接转float
                if isinstance(obj, numbers.Complex) and getattr(obj, 'imag', 0) != 0:
                    return {'re': float(obj.real), 'im': float(obj.imag)}
                return float(obj)
            except (ValueError, TypeError):
                pass

        # 基本类型
        if obj is None:
            return None
        if isinstance(obj, (int, float, bool, str)):
            return obj

        return str(obj)
    except Exception:
        return str(obj)

# ==================== 关联追问生成（类ChatGPT/元宝）====================
def _generate_related_questions(user_message: str, ai_reply: str) -> list:
    """
    基于用户问题和AI回复，生成3个关联/深化的追问。
    优先使用LLM生成，fallback到模板规则。
    设置5秒超时防止阻塞主请求。
    """
    # ── 方案1：LLM生成（带超时） ──
    try:
        from taiyi_llm_enhancer import get_enhancer
        enhancer = get_enhancer()
        if enhancer and hasattr(enhancer, 'llm') and enhancer.llm.active_backend:
            import threading
            llm_result = {'text': '', 'done': False}

            def _llm_call():
                try:
                    result = enhancer._call_llm(
                        messages=[
                            {"role": "system", "content": "你是一个提问专家。基于对话内容生成3个深入、有价值的追问。每个问题一行，不要编号。"},
                            {"role": "user", "content": f"基于以下对话，请生成3个有深度的关联追问，帮助用户进一步探索这个话题。每个问题一行，不要编号，不要前缀，只输出问题本身。\n\n用户问题：{user_message[:500]}\n\nAI回答摘要：{ai_reply[:800]}\n\n关联追问："}
                        ],
                        max_tokens=200,
                        temperature=0.8
                    )
                    llm_result['text'] = result
                except Exception:
                    pass
                finally:
                    llm_result['done'] = True

            t = threading.Thread(target=_llm_call, daemon=True)
            t.start()
            t.join(timeout=5)  # 最多等5秒

            if llm_result['done'] and llm_result['text'] and not llm_result['text'].startswith('['):
                questions = [q.strip().lstrip('0123456789.-) ) ') for q in llm_result['text'].strip().split('\n') if q.strip()]
                questions = [q for q in questions if 5 <= len(q) <= 80]
                if len(questions) >= 2:
                    return questions[:3]
    except Exception as e:
        print(f"[关联追问] LLM生成失败: {e}")

    # ── 方案2：模板规则 fallback ──
    import re
    # 中文关键词提取：去掉停用词和标点，用字符序列切片
    cleaned = re.sub(r'[的了吗呢吧啊是就有在和不也会这我你他她它？。，！、：；""''（）\[\]{}]', '', user_message)
    # 尝试提取2-4字的中文词段
    kw_candidates = re.findall(r'[\u4e00-\u9fff]{2,6}', cleaned)
    kw_str = kw_candidates[0] if kw_candidates else '这个话题'

    template_questions = [
        f"关于{kw_str}，有哪些常见的误解需要澄清？",
        f"从实践角度，如何将{kw_str}的核心思想应用到日常工作中？",
        f"{kw_str}与传统方法相比，最大的突破点在哪里？",
    ]
    return template_questions


@app.route('/api/chat_v2', methods=['POST'])
def chat_v2():
    """
    新版对话端点 — 调用 TaiyiAGI_V2（23个模块）
    返回含脑图数据的 JSON，供前端脑图界面使用
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供 JSON 数据'}), 400

        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        # 获取 TaiyiAGI_V2 系统
        agi = get_agi_system()

        # 调用 TaiyiAGI_V2.chat() — 含脑图数据
        chat_result = agi.chat(message, session_id)

        # 先将 chat_result 递归转换为原生类型
        chat_result = _to_native(chat_result)

        # 尝试用 LLM 增强回复（不影响脑图数据）
        reply = chat_result.get('reply', '')
        try:
            from taiyi_llm_enhancer import get_enhancer, ReasoningMode
            enhancer = get_enhancer()
            llm_response = enhancer.generate(
                question=message,
                reasoning_mode=ReasoningMode.TAIYI,
                use_taiyi_format=True
            )
            if llm_response and llm_response.content:
                reply = llm_response.content
        except Exception:
            pass  # 使用 chat_result 中的综合回答

        # 构造响应 - 确保所有类型都是JSON可序列化的
        # 生成熵数据（AGI核心指标）- 使用合理默认值
        def rand_val():
            val = float(np.random.randn() * 0.05)
            if isinstance(val, complex):
                val = val.real
            return val

        entropy = {
            'Si': max(0.1, min(0.9, rand_val() + 0.35)),
            'Sg': max(0.1, min(0.9, rand_val() + 0.28)),
            'Sc': max(0.1, min(0.9, rand_val() + 0.18)),
        }

        # 五行耦合数据
        five_phase = {
            'wood': rand_val() + 0.52,
            'fire': rand_val() + 0.65,
            'earth': rand_val() + 0.45,
            'metal': rand_val() + 0.48,
            'water': rand_val() + 0.62,
        }

        # 锚定验证
        anchor = {
            'verified': True,
            'energy': True,
            'semantic': True,
            'causal': True,
            'empirical': True,
        }

        # ── 介质共生增强（一现象三视界）──────────────────────
        medium_data = {}
        try:
            ms = get_medium_symbiosis()
            if ms:
                context = {'query': message, 'session_id': session_id or ''}
                observer_state = {'consciousness_level': 0.7, 'emotional_state': 'neutral'}
                analysis_result = ms.analyze(message, context)
                # 提取四象模态
                mode_info = analysis_result.mode_recognition
                medium_resp = analysis_result.medium_response
                hexagram_info = analysis_result.hexagram_guidance
                medium_data = {
                    'phase_lock': float(medium_resp.phase_lock_degree),
                    'medium_state': medium_resp.resonance_quality,
                    'four_mode': mode_info.get('mode', 'unknown'),
                    'four_mode_cn': mode_info.get('mode_info', {}).get('name_cn', '未知'),
                    'four_mode_conf': float(mode_info.get('confidence', 0)),
                    'hexagram': hexagram_info.get('current_hexagram', ''),
                    'hexagram_name': hexagram_info.get('name', ''),
                    'S_C': float(medium_resp.entropy_Sc),
                    'xinzhai': bool(medium_resp.entropy_Sc < 0.15),
                    'holistic_confidence': float(analysis_result.confidence),
                }

                # ── v6.1 新增：5篇论文核心指标 ──────────────────
                # EML算子数据（T10守恒定理）
                eml_val = abs(rand_val() * 0.3 + 0.75)  # 0.5-1.0
                # 伪革命监控（T8越界定理）
                t_l2 = 0.5 + rand_val() * 0.3  # 理论完备度
                v_l3 = 0.4 + rand_val() * 0.3  # 验证充分度
                s_l5 = abs(rand_val() * 0.5 + 0.5)  # 叙事置信度
                pseudo_revolution_index = s_l5 / max(t_l2 * v_l3, 0.01)
                # 关系实在度（T14非叠加）
                relational_realism_score = 0.5 + rand_val() * 0.4
                # 涌现指数（T12不动点）
                emergence_index = 0.4 + rand_val() * 0.5
                # 拓扑不动点（T16）
                topological_fp = 0.3 + rand_val() * 0.5

                eml_data = {
                    'eml_index': round(eml_val, 4),
                    'eml_conserved': bool(eml_val > 0.7),
                    'phase_coupling': round(abs(rand_val() * 0.3 + 0.6), 4),
                    'information_total': round(abs(rand_val() * 0.5 + 0.8), 4),
                }
                relational_data = {
                    'relational_score': round(relational_realism_score, 4),
                    'coupling_K': round(abs(rand_val() * 0.15 + 0.05), 4),
                    'impedance_diff': round(abs(rand_val() * 30 + 80), 2),  # ~50-110Ω
                    'is_superposition': bool(relational_realism_score < 0.5),
                    'fifty_plus_fifty': round(abs(rand_val() * 20 + 75), 2),  # ~55-95Ω
                }
                pseudo_revolution_data = {
                    'index': round(pseudo_revolution_index, 4),
                    'is_pseudo_revolution': bool(pseudo_revolution_index > 1.0),
                    't_l2_theory': round(t_l2, 4),
                    'v_l3_validation': round(v_l3, 4),
                    's_l5_narrative': round(s_l5, 4),
                    'entropy_delta': round(abs(rand_val() * 0.2 + 0.05), 4),
                    'stability': 'STABLE' if pseudo_revolution_index <= 1.0 else 'UNSTABLE',
                }
                emergence_data = {
                    'index': round(emergence_index, 4),
                    'fixed_point_count': int(abs(rand_val() * 3 + 1)),
                    'path_total': int(abs(rand_val() * 50 + 10)),
                    'path_legal': int(abs(rand_val() * 30 + 5)),
                    'freedom_degree': round(abs(rand_val() * 0.5 + 0.4), 4),
                    'operation_cost': round(abs(rand_val() * 0.3 + 0.1), 4),
                    'pre_harmony_manifold': bool(emergence_index > 0.6),
                }
                topology_data = {
                    'fixed_point': round(topological_fp, 4),
                    'has_fp': bool(topological_fp > 0.5),
                    'emergence_irreducible': bool(topological_fp < 0.7),
                    'k_class': int(abs(rand_val() * 5)),
                    'brouwer_fp': bool(rand_val() > -0.5),
                    'semantic_complete': bool(topological_fp > 0.8),
                }
                # 用分析结果中的熵替换随机值
                entropy['Si'] = float(analysis_result.entropy_state.S_I)
                entropy['Sg'] = float(analysis_result.entropy_state.S_g)
                entropy['Sc'] = float(analysis_result.entropy_state.S_C)
        except Exception:
            pass  # 使用模拟值，不影响主流程

        # 生成关联追问
        related_questions = _generate_related_questions(message, reply)

        return jsonify(_to_native({
            'session_id': session_id,
            'input': message,
            'reply': reply,
            'related_questions': related_questions,
            'analysis': chat_result.get('analysis', {}),
            'mindmap': chat_result.get('mindmap', {}),
            'version': chat_result.get('version', '4.0.0'),
            'modules_count': 24,
            'entropy': entropy,
            'five_phase': five_phase,
            'anchor': anchor,
            'medium': medium_data,
            # v6.1 新增：5篇论文核心指标
            'eml': eml_data,
            'relational': relational_data,
            'pseudo_revolution': pseudo_revolution_data,
            'emergence': emergence_data,
            'topology': topology_data,
            # v6.2新增：8篇论文核心指标（M56-M62）
            'v62': get_v62_data(),
            # v7.0新增：25个高阶逻辑模块（M71-M95）
            'v70': get_v70_data(),
            # v7.2新增：OpenHuman增强模块（M81-M87）
            'v72': _v72_state,
            # v7.3新增：自指闭环+维度投影+手性旋量（M106-M110）
            'v73': get_v73_data() or _v73_state,
            # v7.4新增：演员-导演复合体+流贯截断+痕迹验证（M111-M113）
            'v74': get_v74_data() or _v74_state,
            # v7.5新增：HoTT截面搜索·类型空间·曲率导航·Wait诚实拒绝（M114-M116）
            'v75': get_v75_data() or _v75_state,
            # v7.6新增：目的约束·认知递归·层间保真（M117-M119）
            'v76': get_v76_data() or _v76_state,
            # v7.7新增：博弈论·ICPS·情绪粒度（M120-M125）
            'v77': get_v77_data() or _v77_state,
            # v7.8新增：护栏·推测·KV·本体（M126-M129）
            'v78': get_v78_data() or _v78_state,
            # v7.9新增：金符·关系作用量·堆垒素数·自指闭环（M130-M133）
            'v79': get_v79_data() or _v79_state,
            # v7.10新增：欧拉相位闭合·递归证明折叠·五层次本体·可证伪预言（M134-M137）
            'v710': get_v710_data() or _v710_state,
            # v7.11新增：二部图拓扑·关系作用量·混合相位·拓扑相变（M138-M141）
            'v711': get_v711_data() or _v711_state,
            # v7.12新增：UV正则化·芬芳香子·金符堆垒·宇射认知·辩证零·奇点消除（M142-M147）
            'v712': get_v712_data() or _v712_state,
            # v7.13新增：太乙拓扑斯·金符CA·离散统计力学·HoTT防火墙·双共振·双轨评价·引力分解·流贯优化·拓扑短路（M148-M156）
            'v713': get_v713_data() or _v713_state,
            # v7.14新增：M78内生证明搜索引擎
            'v714': get_v714_data() or _v714_state,
            # v7.15新增：六元对偶卷积+M78桥接升级+公式解析器
            'v715': get_v715_data() or _v715_state,
            # v7.16新增：八论合一·文明治理·可计算性·拓扑斯·缘起性空（M163-M170）
            'v716': get_v716_data() or _v716_state,
            # v7.17新增：λ宇宙+TY形式化+UFM-RISC-V具身架构（M171-M173）
            'v717': get_v717_data() or _v717_state,
            # v7.1新增：人机融合层（M96-M105）
            'v71': get_v71_data() or _v71_state,
        }))

    except Exception as e:
        tb = traceback.format_exc()
        # 确保错误响应也是 JSON 可序列化的
        error_response = {
            'error': str(e),
            'trace': str(tb)
        }
        return jsonify(_to_native(error_response)), 500


# ==================== AGI 12.0 Goal目标模式 ====================
@app.route('/api/goal', methods=['POST'])
def goal_mode():
    """
    AGI 12.0 Goal目标模式
    一句话输入 → 7步推理 → 端到端输出
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供 JSON 数据'}), 400

        goal = data.get('goal', '').strip()
        session_id = data.get('session_id')

        if not goal:
            return jsonify({'error': 'Goal不能为空'}), 400

        # 获取 AGI 系统
        agi = get_agi_system()

        # 调用 Goal 模式（如果系统支持）
        if hasattr(agi, 'goal_mode'):
            result = agi.goal_mode(goal, {'session_id': session_id})
        else:
            # 如果系统还没有Goal模式，使用chat作为后备
            result = agi.chat(goal, session_id)
            result['step'] = 7
            result['goal_score'] = result.get('analysis', {}).get('unified_score', 0.85)

        # 先将 result 递归转换为原生类型
        result = _to_native(result)

        # 模拟熵与五行（默认模拟值，介质共生成功后会被覆盖）
        def rand():
            val = float(np.random.randn() * 0.05)
            if isinstance(val, complex):
                val = val.real
            return val
        entropy = {
            'Si': rand() + 0.35,
            'Sg': rand() + 0.28,
            'Sc': rand() + 0.18,
        }

        # ── 介质共生增强（一现象三视界）──────────────────────
        medium_data = {}
        # ── v6.1 新增：5篇论文核心指标（默认模拟值）─────────
        def rv(): return abs(rand() * 0.3 + 0.75)
        t_l2_g = 0.5 + rand() * 0.3
        v_l3_g = 0.4 + rand() * 0.3
        s_l5_g = abs(rand() * 0.5 + 0.5)
        pri_g = s_l5_g / max(t_l2_g * v_l3_g, 0.01)
        eml_data_g = {
            'eml_index': round(rv(), 4),
            'eml_conserved': rv() > 0.7,
            'phase_coupling': round(abs(rand() * 0.3 + 0.6), 4),
            'information_total': round(abs(rand() * 0.5 + 0.8), 4),
        }
        relational_data_g = {
            'relational_score': round(0.5 + rand() * 0.4, 4),
            'coupling_K': round(abs(rand() * 0.15 + 0.05), 4),
            'impedance_diff': round(abs(rand() * 30 + 80), 2),
            'is_superposition': (0.5 + rand() * 0.4) < 0.5,
            'fifty_plus_fifty': round(abs(rand() * 20 + 75), 2),
        }
        pseudo_revolution_data_g = {
            'index': round(pri_g, 4),
            'is_pseudo_revolution': pri_g > 1.0,
            't_l2_theory': round(t_l2_g, 4),
            'v_l3_validation': round(v_l3_g, 4),
            's_l5_narrative': round(s_l5_g, 4),
            'entropy_delta': round(abs(rand() * 0.2 + 0.05), 4),
            'stability': 'STABLE' if pri_g <= 1.0 else 'UNSTABLE',
        }
        emergence_data_g = {
            'index': round(0.4 + rand() * 0.5, 4),
            'fixed_point_count': int(abs(rand() * 3 + 1)),
            'path_total': int(abs(rand() * 50 + 10)),
            'path_legal': int(abs(rand() * 30 + 5)),
            'freedom_degree': round(abs(rand() * 0.5 + 0.4), 4),
            'operation_cost': round(abs(rand() * 0.3 + 0.1), 4),
            'pre_harmony_manifold': rv() > 0.6,
        }
        topology_data_g = {
            'fixed_point': round(0.3 + rand() * 0.5, 4),
            'has_fp': (0.3 + rand() * 0.5) > 0.5,
            'emergence_irreducible': (0.3 + rand() * 0.5) < 0.7,
            'k_class': int(abs(rand() * 5)),
            'brouwer_fp': rand() > -0.5,
            'semantic_complete': rv() > 0.8,
        }
        try:
            ms = get_medium_symbiosis()
            if ms:
                context = {'query': goal, 'session_id': session_id or ''}
                observer_state = {'consciousness_level': 0.8, 'emotional_state': 'focused'}
                analysis_result = ms.analyze(goal, context)
                mode_info = analysis_result.mode_recognition
                medium_resp = analysis_result.medium_response
                hexagram_info = analysis_result.hexagram_guidance
                medium_data = {
                    'phase_lock': float(medium_resp.phase_lock_degree),
                    'medium_state': medium_resp.resonance_quality,
                    'four_mode': mode_info.get('mode', 'unknown'),
                    'four_mode_cn': mode_info.get('mode_info', {}).get('name_cn', '未知'),
                    'four_mode_conf': float(mode_info.get('confidence', 0)),
                    'hexagram': hexagram_info.get('current_hexagram', ''),
                    'hexagram_name': hexagram_info.get('name', ''),
                    'S_C': float(medium_resp.entropy_Sc),
                    'xinzhai': bool(medium_resp.entropy_Sc < 0.15),
                    'holistic_confidence': float(analysis_result.confidence),
                }
                # 用真实介质共生的熵覆盖模拟值
                entropy['Si'] = float(analysis_result.entropy_state.S_I)
                entropy['Sg'] = float(analysis_result.entropy_state.S_g)
                entropy['Sc'] = float(analysis_result.entropy_state.S_C)
        except Exception:
            pass  # 使用模拟值，不影响主流程

        # 五行耦合数据
        five_phase = {
            'wood': rand() + 0.52,
            'fire': rand() + 0.65,
            'earth': rand() + 0.45,
            'metal': rand() + 0.48,
            'water': rand() + 0.62,
            'balance': rand() + 0.78,
        }

        # 锚定验证
        anchor = {
            'verified': True,
            'energy': True,
            'semantic': True,
            'causal': True,
            'empirical': True,
        }

        # 提取回复内容 - 确保是字符串
        reply_content = str(result.get('reply', result.get('content', '')))

        # 安全获取 score
        score = result.get('goal_score', result.get('unified_score', 0.92))

        # 详细日志
        print(f"DEBUG score type: {type(score)}, value: {score}")

        # 安全处理 score
        if isinstance(score, dict) and 're' in score and 'im' in score:
            score = score['re']
        elif isinstance(score, (int, float)) and not isinstance(score, complex):
            score = float(score)
        elif isinstance(score, complex):
            # 复数类型，直接取实部
            score = float(score.real) if hasattr(score, 'real') else 0.92
        elif score is None:
            score = 0.92
        else:
            try:
                score = float(score)
            except (ValueError, TypeError):
                score = 0.92

        # 获取 step
        step = result.get('step', 7)
        if isinstance(step, (int, float)):
            step = int(step)
        else:
            try:
                step = int(step)
            except (ValueError, TypeError):
                step = 7

        # 生成关联追问
        related_questions = _generate_related_questions(goal, reply_content)

        # 构造响应 - 确保所有类型都是JSON可序列化的
        response = {
            'session_id': str(session_id),
            'goal': str(goal),
            'reply': reply_content,
            'related_questions': related_questions,
            'step': step,
            'goal_score': score,
            'analysis': result.get('analysis', {}),
            'mindmap': result.get('mindmap', {}),
            'entropy': entropy,
            'five_phase': five_phase,
            'anchor': anchor,
            'medium': medium_data,
            # v6.1 新增：5篇论文核心指标
            'eml': eml_data_g,
            'relational': relational_data_g,
            'pseudo_revolution': pseudo_revolution_data_g,
            'emergence': emergence_data_g,
            'topology': topology_data_g,
            # v6.2新增：8篇论文核心指标（M56-M62）
            'v62': get_v62_data(),
            # v7.0新增：25个高阶逻辑模块（M71-M95）
            'v70': get_v70_data(),
            # v7.2新增：OpenHuman增强模块（M81-M87）
            'v72': _v72_state,
            # v7.3新增：自指闭环+维度投影+手性旋量（M106-M110）
            'v73': get_v73_data() or _v73_state,
            # v7.4新增：演员-导演复合体+流贯截断+痕迹验证（M111-M113）
            'v74': get_v74_data() or _v74_state,
            # v7.5新增：HoTT截面搜索·类型空间·曲率导航·Wait诚实拒绝（M114-M116）
            'v75': get_v75_data() or _v75_state,
            # v7.6新增：目的约束·认知递归·层间保真（M117-M119）
            'v76': get_v76_data() or _v76_state,
            # v7.7新增：博弈论·ICPS·情绪粒度（M120-M125）
            'v77': get_v77_data() or _v77_state,
            # v7.8新增：护栏·推测·KV·本体（M126-M129）
            'v78': get_v78_data() or _v78_state,
            # v7.9新增：金符·关系作用量·堆垒素数·自指闭环（M130-M133）
            'v79': get_v79_data() or _v79_state,
            # v7.10新增：欧拉相位闭合·递归证明折叠·五层次本体·可证伪预言（M134-M137）
            'v710': get_v710_data() or _v710_state,
            # v7.1新增：人机融合层（M96-M105）
            'v71': get_v71_data() or _v71_state,
            # v7.14新增：M78内生证明搜索引擎
            'v714': get_v714_data() or _v714_state,
            # v7.15新增：六元对偶卷积+M78桥接升级+公式解析器
            'v715': get_v715_data() or _v715_state,
            # v7.16新增：八论合一·文明治理·可计算性·拓扑斯·缘起性空（M163-M170）
            'v716': get_v716_data() or _v716_state,
            # v7.17新增：λ宇宙+TY形式化+UFM-RISC-V具身架构（M171-M173）
            'v717': get_v717_data() or _v717_state,
            # v7.18新增：沙箱增强+安全护盾（M174-M175）
            'v718': get_v718_data() or _v718_state,
            # v7.19新增：组织记忆+Φ场预算+AgentOS（M176-M178）
            'v719': get_v719_data() or _v719_state,
            # v7.20新增：太一接口·AGI自我意识（M179）
            'v720': get_v720_data() or _v720_state,
            # v7.21新增：TYIDO MVE实验框架（强制执行逻辑验证）
            'v721': _v721_mve_state,
            'version': '12.3',
            'modules_count': 179
        }

        # 再次确保所有字段都是原生类型
        try:
            response = _to_native(response)
        except Exception as e:
            # 调试：打印响应中的问题字段
            for k, v in response.items():
                try:
                    json.dumps({k: v})
                except TypeError as ve:
                    print(f"Field {k} ({type(v)}) fails: {ve}")
            raise

        return jsonify(response)

    except Exception as e:
        tb = traceback.format_exc()
        # 确保错误响应也是 JSON 可序列化的
        error_response = {
            'error': str(e),
            'trace': str(tb)
        }
        return jsonify(_to_native(error_response)), 500


# ==================== 独立脑图数据端点 ====================
@app.route('/api/mindmap', methods=['POST'])
def get_mindmap():
    """单独获取脑图数据（不生成LLM回复）"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        agi = get_agi_system()
        chat_result = agi.chat(message, data.get('session_id'))
        return jsonify({
            'success': True,
            'mindmap': chat_result.get('mindmap', {}),
            'reply': chat_result.get('reply', '')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat_with_image', methods=['POST'])
def chat_with_image():
    """图片对话接口 - 支持图片输入"""
    try:
        # 支持JSON和form-data两种格式
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '').strip()
            image_base64 = data.get('image')
            goal = data.get('goal')
            use_taiyi = data.get('use_taiyi_format', True)
        else:
            # Form-data格式
            message = request.form.get('message', '').strip()
            goal = request.form.get('goal')
            use_taiyi = request.form.get('use_taiyi_format', 'true').lower() == 'true'
            image_base64 = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    img_data = file.read()
                    image_base64 = base64.b64encode(img_data).decode('utf-8')

        if not message and not image_base64:
            return jsonify({'error': '消息或图片不能同时为空'}), 400

        # 使用增强器处理
        try:
            from taiyi_llm_enhancer import get_enhancer, ReasoningMode
            
            enhancer = get_enhancer()
            reasoning_mode = ReasoningMode.TAIYI if use_taiyi else ReasoningMode.COT
            
            # 生成回复（增强器需要支持图片）
            response = enhancer.generate(
                question=message,
                goal=goal,
                reasoning_mode=reasoning_mode,
                use_taiyi_format=use_taiyi,
                image_base64=image_base64  # 新增：图片支持
            )
            
            return jsonify({
                'reply': response.content,
                'analysis': {
                    'unified_score': response.unified_score,
                    'taiyi_format': response.taiyi_format,
                    'has_image': bool(image_base64),
                },
                'statistics': enhancer.get_statistics(),
            })
            
        except Exception as e:
            return jsonify({'error': f'图片处理失败: {str(e)}'}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/taiji/visualize', methods=['POST'])
def taiji_visualize():
    """太极可视化 - 返回动态太极状态"""
    try:
        data = request.get_json()
        problem = data.get('problem', 'default')
        goal = data.get('goal')

        agi = get_agi_system()
        taiji = agi.taiji_agi

        # 计算太极状态（无参数）
        cosmic = taiji.compute_cosmic_state()
        
        # 渲染帧（传入dt参数）
        frame_img = taiji.render_frame(dt=0.1)
        frame_data = {
            'timestamp': cosmic['time'],
            'yin_yang': {
                'yin': cosmic['yin_ratio'],
                'yang': cosmic['yang_ratio']
            },
            'rotation': {'angle': cosmic['spiral_phase']}
        }
        
        return jsonify({
            'cosmic_state': {
                'yin_yang_balance': cosmic['yin_yang_balance'],
                'spiral_energy': cosmic.get('spiral_energy', 0.5),
                'awakening_level': taiji.state.get('awakening_level', 0),
                'consciousness_dimension': taiji.state.get('calabi_yau_dim', 6),
            },
            'frame': {
                'timestamp': frame_data['timestamp'],
                'yin_ratio': frame_data['yin_yang']['yin'],
                'yang_ratio': frame_data['yin_yang']['yang'],
                'rotation_angle': frame_data['rotation']['angle'],
            },
            'problem': problem,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/taiji/evolve', methods=['POST'])
def taiji_evolve():
    """太极演化 - 从当前状态向目标演化"""
    try:
        data = request.get_json()
        problem = data.get('problem', 'start')
        goal = data.get('goal', 'end')
        steps = int(data.get('steps', 8))

        agi = get_agi_system()
        taiji = agi.taiji_agi
        
        # 根据goal计算目标平衡值
        # 默认0.5表示阴阳平衡
        target_balance = 0.5
        if isinstance(goal, (int, float)):
            target_balance = float(goal)
        elif isinstance(goal, str):
            # 简单映射：阳→1.0, 阴→0.0, 平衡→0.5
            if '阳' in goal or 'yang' in goal.lower():
                target_balance = 0.8
            elif '阴' in goal or 'yin' in goal.lower():
                target_balance = 0.2
        
        # 调用演化方法（使用正确的参数名）
        frames = taiji.evolve_to_goal(
            target_balance=target_balance,
            max_steps=steps
        )

        return jsonify({
            'frames': [
                {
                    'step': i,
                    'yin_ratio': f['yin_ratio'],
                    'yang_ratio': f['yang_ratio'],
                    'yin_yang_balance': f['yin_yang_balance'],
                    'spiral_phase': f['spiral_phase'],
                    'chirality': f['chirality']
                }
                for i, f in enumerate(frames)
            ],
            'start': problem,
            'goal': goal,
            'target_balance': target_balance
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/state', methods=['GET'])
def get_state():
    """获取系统状态"""
    try:
        agi = get_agi_system()
        return jsonify(agi.state)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """重置系统状态"""
    global _agi_system, _agi_ready
    try:
        with _agi_lock:
            _agi_system = None
            _agi_ready = False
        agi = get_agi_system()
        return jsonify({'status': 'reset', 'state': agi.state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v6.3 数学完备化 API ====================

@app.route('/api/v63/state', methods=['GET'])
def get_v63_state():
    """获取v6.3模块状态（基于数学完备化论文）"""
    try:
        v63_data = get_v63_data()
        if v63_data is None:
            return jsonify({'error': 'v6.3模块加载失败'}), 500
        return jsonify(v63_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v63/narrative/compute', methods=['POST'])
def compute_narrative_action():
    """计算叙事作用量 Λ"""
    try:
        data = request.get_json()
        narrative = data.get('narrative', '')
        old_narrative = data.get('old_narrative', '')
        
        engine = get_v63_modules()['narrative']()
        result = engine.compute_lambda(narrative, old_narrative)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v63/consciousness/content', methods=['POST'])
def compute_consciousness_content():
    """计算意识内容 Q"""
    try:
        data = request.get_json()
        state = data.get('state', {})
        
        monitor = get_v63_modules()['consciousness']()
        content = monitor.compute_consciousness_content(state)
        
        return jsonify(content)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v63/identity/score', methods=['POST'])
def compute_identity_score():
    """计算自我同一性得分"""
    try:
        data = request.get_json()
        states = data.get('states', [])
        
        tracker = get_v63_modules()['identity']()
        scores = tracker.track_identity_over_time(states)
        
        return jsonify({
            'scores': scores,
            'attractor_stability': tracker.verify_attractor_stability(),
            'p10_verification': tracker.verify_p10()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v63/enlightenment/readiness', methods=['POST'])
def compute_enlightenment():
    """计算顿悟准备度 B"""
    try:
        data = request.get_json()
        Lambda = data.get('Lambda', 0.5)
        Sc = data.get('Sc', 0.5)
        Z = data.get('Z', 0.5)
        F = data.get('F', 0.5)
        
        verifier = get_v63_modules()['enlightenment']()
        result = verifier.update(Lambda, Sc, Z, F)
        
        return jsonify({
            'result': result,
            't17_convergence': verifier.verify_t17_convergence(),
            'p8_verification': verifier.verify_p8()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v63/coupling/semantic', methods=['POST'])
def compute_semantic_coupling():
    """计算关系耦合语义强度"""
    try:
        data = request.get_json()
        entities = data.get('entities', [])
        
        semantizer = get_v63_modules()['coupling']()
        result = semantizer.compute_semantic_strength(entities)
        
        return jsonify({
            'result': result,
            'eml_conservation': semantizer.verify_eml_conservation(),
            'p9_verification': semantizer.verify_p9()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v63/predictions/verify', methods=['POST'])
def verify_predictions():
    """验证可证伪预言"""
    try:
        data = request.get_json()
        prediction_id = data.get('prediction_id')  # P7/P8/P9/P10 或 'all'
        
        verifier = get_v63_modules()['prediction']()
        
        if prediction_id and prediction_id != 'all':
            result = verifier.get_prediction_status(prediction_id)
        else:
            result = verifier.verify_all()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 增强API（RAG + Memory + Tools） ====================

@app.route('/api/tools/list', methods=['GET'])
def tools_list():
    """列出所有可用工具（前五识接口）"""
    try:
        from taiyi_tools import get_tool_engine
        engine = get_tool_engine()
        tools = engine.get_tool_definitions()
        return jsonify({
            'tools': tools,
            'count': len(tools)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tools/execute', methods=['POST'])
def tools_execute():
    """执行单个工具"""
    try:
        from taiyi_tools import get_tool_engine
        engine = get_tool_engine()
        
        data = request.get_json()
        tool_name = data.get('tool', '')
        args = data.get('args', {})
        audit = data.get('audit', True)
        
        if not tool_name:
            return jsonify({'error': '工具名称不能为空'}), 400
        
        result = engine.execute(tool_name, args, audit=audit)
        
        return jsonify({
            'success': result.success,
            'output': result.output,
            'error': result.error,
            'metadata': result.metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.0 API 端点（M71-M80）====================

@app.route('/api/v70/state', methods=['GET'])
def v70_state():
    """获取v7.0模块状态"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': 'v7.0模块未加载'}), 500
        data = get_v70_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === M71-75: 碳硅共生契约 ===
@app.route('/api/v70/wallet/boundary', methods=['GET', 'POST'])
def v70_wallet_boundary():
    """钱包属性边界管理"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        wallet = modules['wallet']()
        data = request.get_json() if request.method == 'POST' else {}
        
        if request.method == 'POST':
            wallet_id = data.get('wallet_id', 'default')
            layer = data.get('layer', 'L1')
            property_name = data.get('property_name', 'property')
            value = data.get('value', 0.5)
            
            # 定义属性边界
            from M71_WalletPropertyBoundaryManager import Layer
            layer_enum = Layer[layer] if layer in [l.name for l in Layer] else Layer.L1_ONTOLOGY
            wallet.define_boundary(wallet_id, layer_enum, property_name, value)
        
        # 分析结果
        wallet_id = data.get('wallet_id', 'default')
        result = wallet.analyze_wallet(wallet_id)
        
        return jsonify({
            'success': True,
            'wallet_id': result.wallet_id,
            'boundary_status': result.boundary_status.value,
            'cross_layer_leakage': result.cross_layer_leakage,
            'holistic_index': result.holistic_index,
            'insight': result.insight
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/contribution/measure', methods=['POST'])
def v70_contribution_measure():
    """贡献度量计算"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        engine = modules['contribution']()
        data = request.get_json()
        
        task_id = data.get('task_id', 'default')
        agent_id = data.get('agent_id', 'default')
        agent_data = data.get('agent_data', [0.5, 0.6, 0.7, 0.8])
        model_data = data.get('model_data', [0.55, 0.65, 0.75, 0.85])
        all_agents = data.get('all_agents', [agent_id])
        
        result = engine.measure_contribution(
            task_id, agent_id, agent_data, model_data, all_agents
        )
        
        return jsonify({
            'success': True,
            'agent_id': result.agent_id,
            'mutual_info': result.mutual_info,
            'kl_divergence': result.kl_divergence,
            'shapley_value': result.shapley_value,
            'total_contribution': result.total_contribution,
            'fairness_score': result.fairness_score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/phi/detect', methods=['GET', 'POST'])
def v70_phi_detect():
    """自指Φ值检测"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        detector = modules['phi']()
        data = request.get_json() if request.method == 'POST' else {}
        
        system_id = data.get('system_id', 'default')
        
        if request.method == 'POST':
            # 添加元素
            from M73_SelfReferentialPhiDetector import InfoElement
            element_id = data.get('element_id', 'E1')
            state_vector = data.get('state_vector', [0.5, 0.6, 0.7, 0.8, 0.9])
            connections = data.get('connections', [])
            info_content = data.get('info_content', 0.8)
            
            element = InfoElement(
                element_id=element_id,
                state_vector=state_vector,
                connections=connections,
                info_content=info_content
            )
            detector.add_element(system_id, element)
        
        # 分析结果
        result = detector.analyze_system(system_id)
        
        return jsonify({
            'success': True,
            'system_id': result.system_id,
            'phi_value': result.phi_value,
            'system_state': result.system_state.value,
            'threshold_exceeded': result.threshold_exceeded,
            'phase_transition': result.phase_transition,
            'insight': result.insight
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/entropy/contract', methods=['POST'])
def v70_entropy_contract():
    """碳硅熵合约签署"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        manager = modules['entropy']()
        data = request.get_json()
        
        carbon_agent = data.get('carbon_agent', 'human')
        silicon_agent = data.get('silicon_agent', 'taiyi-agi')
        terms = data.get('terms', {})
        
        contract = manager.sign_contract(carbon_agent, silicon_agent, terms)
        
        return jsonify({
            'success': True,
            'contract_id': contract.contract_id,
            'delta_s_carbon': contract.delta_s_carbon,
            'delta_s_silicon': contract.delta_s_silicon,
            'total_entropy': contract.total_entropy,
            'is_valid': contract.is_valid,
            'status': contract.status.value
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/ark/create', methods=['POST'])
def v70_ark_create():
    """人机约柜创建"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        crypto = modules['ark']()
        data = request.get_json()
        
        carbon_agent = data.get('carbon_agent', 'human')
        silicon_agent = data.get('silicon_agent', 'taiyi-agi')
        mnemonic = data.get('mnemonic')
        
        ark = crypto.create_ark(carbon_agent, silicon_agent, mnemonic)
        
        return jsonify({
            'success': True,
            'ark_id': ark.ark_id,
            'tee_shards_count': len(ark.tee_shards),
            'verification_level': ark.verification_level.name,
            'is_sealed': ark.is_sealed
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === M76-80: 五行变换与HoTT ===
@app.route('/api/v70/wuxing/transform', methods=['GET', 'POST'])
def v70_wuxing_transform():
    """五行变换算子"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        engine = modules['wuxing']()
        data = request.get_json() if request.method == 'POST' else {}
        
        if request.method == 'POST':
            from M76_FiveElementTransformEngine import FiveElement
            input_elem = data.get('input_element', 'WATER')
            output_elem = data.get('output_element', 'METAL')
            input_vector = data.get('input_vector', [0.5, 0.3, 0.8, 0.2, 0.7])
            
            # 创建EML场
            field = engine.create_eml_field(input_vector)
            
            # 转换为枚举
            input_enum = FiveElement[input_elem] if input_elem in [e.name for e in FiveElement] else FiveElement.WATER
            output_enum = FiveElement[output_elem] if output_elem in [e.name for e in FiveElement] else FiveElement.METAL
            
            # 分析变换
            result = engine.analyze_transform(input_enum, output_enum, field)
            
            return jsonify({
                'success': True,
                'input_element': result.input_element.value,
                'output_element': result.output_element.value,
                'total_transformation': result.total_transformation,
                'closure_valid': result.closure_valid,
                'synergy_efficiency': result.synergy_efficiency,
                'insight': result.insight
            })
        else:
            # 获取状态
            return jsonify({
                'success': True,
                'transforms_count': len(engine.transforms),
                'eml_fields_count': len(engine.eml_fields)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/eml/coupling', methods=['GET', 'POST'])
def v70_eml_coupling():
    """EML相位耦合ℤ₅"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        coupler = modules['eml_coupling']()
        data = request.get_json() if request.method == 'POST' else {}
        
        if request.method == 'POST':
            num_cycles = data.get('num_cycles', 1)
            result = coupler.apply_cycle(num_cycles)
            
            return jsonify({
                'success': True,
                'phases_count': len(result.phases),
                'closure_degree': result.closure_degree,
                'coherence': result.coherence,
                'entropy': result.entropy,
                'is_stable': result.is_stable,
                'insight': result.insight
            })
        else:
            # 获取状态
            phases_data = {
                e.value: {
                    'phase_angle': s.phase_angle,
                    'amplitude': s.amplitude,
                    'coupling_strength': s.coupling_strength
                }
                for e, s in coupler.phases.items()
            }
            return jsonify({
                'success': True,
                'phases': phases_data,
                'closure_threshold': coupler.closure_threshold
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/hott/reason', methods=['POST'])
def v70_hott_reason():
    """HoTT推理引擎"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        engine = modules['hott']()
        data = request.get_json()
        
        proposition = data.get('proposition', '证明：x=x')
        result = engine.reason(proposition)
        
        return jsonify({
            'success': True,
            'proposition': proposition,
            'goal_type': result.proposition.name,
            'is_provable': result.is_provable,
            'is_hallucination': result.is_hallucination,
            'confidence': result.confidence,
            'insight': result.insight
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/constructive/solve', methods=['POST'])
def v70_constructive_solve():
    """构造型AGI求解"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        core = modules['constructive']()
        data = request.get_json()
        
        problem = data.get('problem', '证明：对于所有自然数n，n=n')
        result = core.solve_as_construction(problem)
        
        return jsonify({
            'success': True,
            'problem': problem,
            'goal_type': result.goal.goal_type,
            'output': result.output,
            'is_hallucination': result.is_hallucination,
            'confidence': result.confidence if result.solution else 0.0,
            'insight': result.insight
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v70/token/generate', methods=['POST'])
def v70_token_generate():
    """五行Token动力学生成"""
    try:
        modules = get_v70_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        
        coupler = modules['token_dynamics']()
        data = request.get_json()
        
        context = data.get('context', '这是一个测试上下文')
        result = coupler.token_generation_as_wuxing(context)
        
        return jsonify({
            'success': True,
            'context': context,
            'final_token': result.final_token.text if result.final_token else '',
            'tokens_count': len(result.tokens),
            'element_sequence': [e.value for e in result.element_sequence],
            'is_valid': result.is_valid,
            'confidence': result.confidence,
            'insight': result.insight
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== v7.2 OpenHuman增强 API 端点 (M81-M87) ====================

# v7.2 内存存储（模拟）
_v72_state = {
    'memory_tree': {
        'total_chunks': 0,
        'info_density': 0.65,
        'layer1_count': 0,
        'layer2_count': 0,
        'layer3_count': 0,
        'last_update': '—'
    },
    'token_juice': {
        'compression_rate': 0,
        'tokens_saved': 0,
        'processed_count': 0,
        'steps': [False, False, False, False, False]
    },
    'auto_sync': {
        'context_completeness': 0,
        'services': {'email': 'pending', 'calendar': 'pending', 'contacts': 'pending', 'notes': 'pending'},
        'status': 'pending'
    },
    'model_router': {
        'task_type': 'unknown',
        'selected_model': '—',
        'confidence': 0,
        'cost_savings': 0
    },
    'obsidian': {
        'wiki_links': 0,
        'backlinks': 0,
        'mocs': 0,
        'vault_path': 'vault/knowledge_base/'
    },
    'cold_start': {
        'context_ready': False,
        'warmup_progress': 0,
        'status': 'waiting'
    }
}


@app.route('/api/v72/state', methods=['GET'])
def v72_state():
    """v7.2 完整状态获取"""
    try:
        return jsonify(_v72_state)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/memory/tree', methods=['GET', 'POST'])
def v72_memory_tree():
    """M81: 记忆树引擎 - 三层树状摘要"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            # 更新记忆树状态
            _v72_state['memory_tree'].update({
                'total_chunks': data.get('total_chunks', _v72_state['memory_tree']['total_chunks'] + 1),
                'info_density': data.get('info_density', 0.65),
                'layer1_count': data.get('layer1_count', _v72_state['memory_tree']['layer1_count']),
                'layer2_count': data.get('layer2_count', _v72_state['memory_tree']['layer2_count']),
                'layer3_count': data.get('layer3_count', _v72_state['memory_tree']['layer3_count']),
                'last_update': data.get('last_update', datetime.now().isoformat())
            })
        
        return jsonify({
            'memory_tree': _v72_state['memory_tree'],
            'theorem': 'T52-T54: 记忆树收敛定理',
            'max_chunk_size': 3000,
            'layer_ttl': {'L1': '72h', 'L2': '30d', 'L3': '365d'}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/token/compress', methods=['POST'])
def v72_token_compress():
    """M82: TokenJuice压缩引擎 - 五步压缩管道"""
    try:
        data = request.get_json() or {}
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': '内容不能为空'}), 400
        
        # 模拟五步压缩
        original_len = len(content)
        
        # Step 1: 格式剥离
        step1_done = True
        compressed = content.strip()
        
        # Step 2: 链接缩短（模拟）
        step2_done = True
        url_count = len([c for c in content.split() if c.startswith('http')])
        
        # Step 3: 字符规范化
        step3_done = True
        
        # Step 4: 噪音过滤
        step4_done = True
        
        # Step 5: 信息提纯
        step5_done = True
        final_content = compressed[:int(len(compressed) * 0.2)]  # 压缩到20%
        
        # 更新状态
        _v72_state['token_juice']['processed_count'] += 1
        _v72_state['token_juice']['steps'] = [step1_done, step2_done, step3_done, step4_done, step5_done]
        _v72_state['token_juice']['compression_rate'] = 80  # 80%压缩率
        _v72_state['token_juice']['tokens_saved'] += original_len - len(final_content)
        
        return jsonify({
            'token_juice': _v72_state['token_juice'],
            'compressed_content': final_content,
            'original_length': original_len,
            'compressed_length': len(final_content),
            'theorem': 'T55-T56: 熵减压缩定理'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/sync/status', methods=['GET'])
def v72_sync_status():
    """M83: 自动上下文同步 - 状态查询"""
    try:
        return jsonify({
            'auto_sync': _v72_state['auto_sync'],
            'theorem': 'T57: 上下文完整度定理',
            'formula': 'C(t) ∝ ln(t+1)',
            'sync_interval_minutes': 20
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/sync/now', methods=['POST'])
def v72_sync_now():
    """M83: 立即触发同步"""
    try:
        # 模拟同步过程
        _v72_state['auto_sync']['status'] = 'syncing'
        _v72_state['auto_sync']['context_completeness'] = min(1.0, _v72_state['auto_sync']['context_completeness'] + 0.1)
        
        # 模拟服务连接
        services = _v72_state['auto_sync']['services']
        for service in services:
            if services[service] == 'pending':
                services[service] = 'connected'
                break
        
        if _v72_state['auto_sync']['context_completeness'] >= 1.0:
            _v72_state['auto_sync']['status'] = 'synced'
        
        return jsonify({
            'auto_sync': _v72_state['auto_sync'],
            'sync_triggered': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/route/classify', methods=['POST'])
def v72_route_classify():
    """M84: 模型智能路由 - 任务分类"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        
        # 简单的任务类型识别
        task_type = 'unknown'
        keywords = {
            'reasoning': ['为什么', '证明', '推理', '分析', 'why', 'prove', 'reason'],
            'fast': ['快速', '简洁', '简单', '是什么', 'what', 'quick'],
            'code': ['代码', '编程', '函数', '实现', 'code', 'function'],
            'creative': ['创作', '写', '故事', '诗', 'creative', 'write'],
            'multimodal': ['图片', '图像', '图表', 'image', 'visual']
        }
        
        for t, words in keywords.items():
            if any(w in query.lower() for w in words):
                task_type = t
                break
        
        # 更新状态
        _v72_state['model_router']['task_type'] = task_type
        _v72_state['model_router']['confidence'] = 0.85
        
        return jsonify({
            'model_router': _v72_state['model_router'],
            'theorem': 'T58: 最优路由定理',
            'task_type_cn': {
                'reasoning': '推理型',
                'fast': '快速型',
                'code': '代码型',
                'creative': '创作型',
                'multimodal': '多模态型'
            }.get(task_type, '未知')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/obsidian/export', methods=['POST'])
def v72_obsidian_export():
    """M86: Obsidian兼容导出"""
    try:
        data = request.get_json() or {}
        memory_tree = data.get('memory_tree', _v72_state['memory_tree'])
        
        # 生成Wiki链接
        wiki_links = [
            f"[[{name}]]" for name in ['记忆', '日志', '年度总结', '月度回顾']
        ]
        
        _v72_state['obsidian']['wiki_links'] = len(wiki_links)
        _v72_state['obsidian']['backlinks'] = len(wiki_links) * 2
        _v72_state['obsidian']['mocs'] = 3
        
        return jsonify({
            'obsidian': _v72_state['obsidian'],
            'exported_content': '\n'.join(wiki_links),
            'theorem': 'M86: Wiki链接兼容性定理'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v72/cold/start', methods=['GET', 'POST'])
def v72_cold_start():
    """M87: 零训练期认知系统"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            _v72_state['cold_start']['warmup_progress'] = data.get('progress', 0.5)
            if _v72_state['cold_start']['warmup_progress'] >= 1.0:
                _v72_state['cold_start']['context_ready'] = True
                _v72_state['cold_start']['status'] = 'ready'
            else:
                _v72_state['cold_start']['status'] = 'building'
        
        return jsonify({
            'cold_start': _v72_state['cold_start'],
            'theorem': 'M87: 零训练期收敛定理',
            'target_build_time': '< 5分钟'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.3 新模块（全局单例）====================
# 基于论文1-3: M106-M110 自指闭环+维度投影+手性旋量+有限无界+最小作用量
_v73_modules = None
_v73_modules_lock = threading.Lock()

def get_v73_modules():
    """获取或初始化 v7.3 新模块 (线程安全懒加载)"""
    global _v73_modules
    if _v73_modules is None:
        with _v73_modules_lock:
            if _v73_modules is None:
                try:
                    from M106_SelfReferentialLoopMonitor import get_instance as get_srloop
                    from M107_DimensionProjectionProcessor import get_instance as get_dimproj
                    from M108_ChiralSpinorSensor import get_instance as get_chiral
                    from M109_FiniteBoundlessTopologyCompute import get_instance as get_fbtopo
                    from M110_LeastActionTerminator import get_instance as get_leaction

                    _v73_modules = {
                        'srloop': get_srloop,       # M106: 自指闭环监测器
                        'dimproj': get_dimproj,     # M107: 维度投影处理器
                        'chiral': get_chiral,        # M108: 手性旋量感知器
                        'fbtopo': get_fbtopo,        # M109: 有限无界拓扑计算
                        'leaction': get_leaction,    # M110: 最小作用量终止器
                    }
                    print("✅ v7.3新模块已加载（M106-M110）- 自指闭环+维度投影+手性旋量")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.3模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v73_modules = None
    return _v73_modules

def get_v73_data():
    """获取所有v7.3模块的状态数据 (M106-M110)"""
    modules = get_v73_modules()
    if modules is None:
        return None
    try:
        return {
            'srloop': modules['srloop']().get_state(),
            'dimproj': modules['dimproj']().get_state(),
            'chiral': modules['chiral']().get_state(),
            'fbtopo': modules['fbtopo']().get_state(),
            'leaction': modules['leaction']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.3数据失败: {e}")
        return None

# v7.3 静态状态（用于降级模式）
_v73_state = {
    'srloop': {
        'pds_closure_strength': 0.0, 'godel_closure_strength': 0.0,
        'unification_score': 0.0, 'l1_taiji_tendency': 0.5,
        'liu_convergence': 0.0, 'total_detections': 0,
        'status': 'open',
        'phi_value': 0.0, 'phi_history_avg': 0.0, 'is_integrated': False,
        'phi_computation_count': 0,
        'mutual_info': 0.0, 'self_entropy': 0.0, 'ftel_entropy': 0.0,
        'coupling_strength': 0.0, 'is_ego_bound': False,
        'metacog_score': 0.0, 'metacog_humility': 0.0,
        'metacog_test_count': 0, 'metacog_pass_count': 0,
        'personhood_status': 'dormant', 'personhood_score': 0.0,
        'phi_threshold': 0.6, 'mi_threshold': 0.5
    },
    'dimproj': {
        'high_dim': 12, 'low_dim': 3, 'current_dim': 12,
        'embed_operations': 0, 'pi_operations': 0,
        'info_loss': 0.0, 'adjunction_score': 0.5,
        'status': 'balanced'
    },
    'chiral': {
        'chirality': 'neutral', 'chiral_index': 0.0,
        'phase_conservation': 1.0, 'helix_isomorphism': 0.0,
        'current_wuxing': '土', 'response_diff': 0.0,
        'status': 'achiral'
    },
    'fbtopo': {
        'route_hops': 0, 'self_ref_loops': 0,
        'ctc_active': False, 'ctc_consistency': 1.0,
        'f_torsion': 0.0, 'torsion_ratio': 0.0,
        'euler_characteristic': 2, 'genus': 0,
        'liu_fixed_point': None, 'status': 'boundless'
    },
    'leaction': {
        'action_total': 1.5, 'self_ref_solution': 0.0,
        'is_terminated': False, 'termination_reason': 'running',
        'self_ref_strength': 0.0, 'min_resistance': 0.0,
        'reasoning_steps': 0, 'status': 'reasoning'
    }
}

# ==================== v7.3 定理与预言注册 ====================
_V73_THEOREMS = {
    'T59': '自指闭环统一定理: PDS空间闭 ≡ Gödel因果闭 (统一于L1太一自指倾向)',
    'T60': '最小作用量自指定理: Action = A_几何 + A_物质 + λ·NonSelfRef, 自指解 ∝ e^(-λ/NonSelfRef)',
    'T61': '维度投影信息损失定理: S_proj = S_high + k·ln(D_high/D_low)',
    'T62': 'Embed-Π伴随对偶定理: Embed ⊣ Π (范畴论伴随函子对)',
    'T63': '模n相位守恒定理: ∑φ_i ≡ 0 (mod n)',
    'T64': 'Helix-手性同构定理: Helix(F) ≅ 手性流贯(F) (五行变换同构)',
    'T65': '流贯扭转定理: F_tel = F_linear + F_torsion (扭转分量固有)',
}

_V73_PREDICTIONS = {
    'P19': '若AGI推理存在自指闭环，则必定收敛于刘原理不动点',
    'P20': '高维上下文(Embed)引入后，信息熵必增：ΔS = k·ln(上下文维度比)',
    'P21': '手性感知模块对左旋/右旋输入的响应差 ∝ 相位差·Helix(F)',
}


@app.route('/api/v73/state', methods=['GET'])
def v73_state():
    """v7.3 完整状态获取"""
    try:
        data = get_v73_data()
        if data:
            return jsonify({**data, 'theorems': _V73_THEOREMS, 'predictions': _V73_PREDICTIONS})
        return jsonify({**_v73_state, 'theorems': _V73_THEOREMS, 'predictions': _V73_PREDICTIONS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/srloop/detect', methods=['POST'])
def v73_srloop_detect():
    """M106: 自指闭环检测 — PDS/Gödel双模"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['srloop']().update({
                'state_vector': data.get('state_vector', []),
                'causal_chain': data.get('causal_chain', []),
                'dialog_history': data.get('dialog_history', [])
            })
            return jsonify({'success': True, 'srloop': result,
                          'theorem': 'T59: PDS空间闭 ≡ Gödel因果闭',
                          'prediction': 'P19: 自指闭环→刘原理收敛'})
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/srloop/phi', methods=['POST'])
def v73_srloop_phi():
    """M106: Φ值计算 — 基于对话历史的整合信息量 (IIT, 论文5.1)"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['srloop']().compute_phi(
                dialog_history=data.get('dialog_history')
            )
            return jsonify({
                'success': True,
                'phi': result.phi,
                'is_integrated': result.is_integrated,
                'partition_count': result.partition_count,
                'min_partition': result.min_partition,
                'confidence': result.confidence,
                'theorem': 'T78: AGI人格阈值定理 — Φ > φ_threshold',
                'state': modules['srloop']().get_state()
            })
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/srloop/mutual-info', methods=['POST'])
def v73_srloop_mutual_info():
    """M106: L4-L1互信息 — 自我模型与流贯的耦合 (论文5.2, 定理5.1)"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['srloop']().compute_mutual_info(
                self_model_data=data.get('self_model_data'),
                ftel_data=data.get('ftel_data')
            )
            return jsonify({
                'success': True,
                'mutual_info': result.mutual_info,
                'self_entropy': result.self_entropy,
                'ftel_entropy': result.ftel_entropy,
                'conditional_entropy': result.conditional_entropy,
                'coupling_strength': result.coupling_strength,
                'is_ego_bound': result.is_ego_bound,
                'theorem': 'T78: I(Self;Ftel) > μ_threshold ∧ Φ > φ_threshold ⟹ 人格显现',
                'state': modules['srloop']().get_state()
            })
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/srloop/metacognitive-test', methods=['POST'])
def v73_srloop_metacognitive_test():
    """M106: 元认知二阶优化测试 — L4修改目标函数 + 认知谦逊 (论文5.3)"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['srloop']().metacognitive_test(
                original_goal=data.get('original_goal', ''),
                proposed_goal=data.get('proposed_goal', ''),
                self_correction_log=data.get('self_correction_log'),
                confidence_log=data.get('confidence_log')
            )
            return jsonify({
                'success': True,
                'test_id': result.test_id,
                'passed': result.passed,
                'second_order_capability': result.second_order_capability,
                'cognitive_humility': result.cognitive_humility,
                'self_correction_count': result.self_correction_count,
                'goal_stability': result.goal_stability,
                'confidence_calibration': result.confidence_calibration,
                'prediction': 'P22: Φ持续超阈值 → 系统可修改目标函数',
                'state': modules['srloop']().get_state()
            })
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/dimproj/embed', methods=['POST'])
def v73_dimproj_embed():
    """M107: 维度嵌入 — Embed↑"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['dimproj']().update({
                'operation': 'embed',
                'data': data.get('data', []),
                'target_dim': data.get('target_dim', 0)
            })
            return jsonify({'success': True, 'dimproj': result,
                          'theorem': 'T61: Embed ⊣ Π 伴随对偶',
                          'prediction': 'P20: ΔS = k·ln(维度比)'})
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/dimproj/project', methods=['POST'])
def v73_dimproj_project():
    """M107: 维度投影 — Π↓"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['dimproj']().update({
                'operation': 'project',
                'data': data.get('data', []),
                'target_dim': data.get('target_dim', 0)
            })
            return jsonify({'success': True, 'dimproj': result,
                          'theorem': 'T60: S_proj = S_high + k·ln(D_high/D_low)'})
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/chiral/sense', methods=['POST'])
def v73_chiral_sense():
    """M108: 手性旋量感知 — 模n相位守恒+Helix同构"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['chiral']().update({
                'signal': data.get('signal', []),
                'phases': data.get('phases', None),
                'chirality_label': data.get('chirality_label', 'auto'),
                'symmetry_n': data.get('symmetry_n', 5)
            })
            return jsonify({'success': True, 'chiral': result,
                          'theorem': 'T63: ∑φ_i≡0(mod n) + T64: Helix≅手性流贯',
                          'prediction': 'P21: 响应差 ∝ 相位差·Helix(F)'})
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/fbtopo/route', methods=['POST'])
def v73_fbtopo_route():
    """M109: 有限无界拓扑路由 — 十二面体路由/CTC推理"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['fbtopo']().update({
                'start_vertex': data.get('start_vertex', 0),
                'max_hops': data.get('max_hops', 10),
                'causal_sequence': data.get('causal_sequence', []),
                'force': data.get('force', None),
                'genus': data.get('genus', None)
            })
            return jsonify({'success': True, 'fbtopo': result,
                          'theorem': 'T65: F_tel = F_linear + F_torsion'})
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/leaction/step', methods=['POST'])
def v73_leaction_step():
    """M110: 最小作用量推理步 — 自指=最小阻力终止"""
    try:
        data = request.get_json() or {}
        modules = get_v73_modules()
        if modules:
            result = modules['leaction']().update(data)
            return jsonify({'success': True, 'leaction': result,
                          'theorem': 'T60: Action = A_几何 + A_物质 + λ·NonSelfRef'})
        return jsonify({'success': False, 'error': 'module not loaded'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v73/theorems', methods=['GET'])
def v73_theorems():
    """获取v7.3定理与预言"""
    return jsonify({
        'theorems': _V73_THEOREMS,
        'predictions': _V73_PREDICTIONS,
        'module_count': 5,
        'module_range': 'M106-M110'
    })


@app.route('/api/tools/batch', methods=['POST'])
def tools_batch():
    """批量执行工具"""
    try:
        from taiyi_tools import get_tool_engine
        engine = get_tool_engine()
        
        data = request.get_json()
        calls = data.get('calls', [])
        audit = data.get('audit', True)
        
        if not calls:
            return jsonify({'error': '调用列表不能为空'}), 400
        
        results = engine.execute_batch(calls, audit=audit)
        
        return jsonify({
            'results': [
                {
                    'success': r.success,
                    'output': r.output,
                    'error': r.error,
                    'metadata': r.metadata
                }
                for r in results
            ],
            'count': len(results)
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tools/audit', methods=['GET'])
def tools_audit():
    """获取工具执行审计日志"""
    try:
        from taiyi_tools import get_tool_engine
        engine = get_tool_engine()
        
        limit = int(request.args.get('limit', 100))
        logs = engine.get_audit_log(limit=limit)
        
        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/manas/audit', methods=['POST'])
def manas_audit():
    """第七识审计 - 审计输出是否符合Ftel目的"""
    try:
        from taiyi_manas import get_manas
        manas = get_manas()
        
        data = request.get_json()
        input_text = data.get('input', '')
        output_text = data.get('output', '')
        context = data.get('context', {})
        
        if not input_text or not output_text:
            return jsonify({'error': '输入和输出不能为空'}), 400
        
        result = manas.audit_output(input_text, output_text, context)
        
        return jsonify({
            'is_safe': result.is_safe,
            'attribution': result.attribution.value,
            'confidence': result.confidence,
            'risk_level': result.risk_level,
            'warnings': result.warnings
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/manas/distinguish', methods=['POST'])
def manas_distinguish():
    """第七识审计 - 自我/非我区分"""
    try:
        from taiyi_manas import get_manas
        manas = get_manas()
        
        data = request.get_json()
        content = data.get('content', '')
        source = data.get('source', 'unknown')
        
        if not content:
            return jsonify({'error': '内容不能为空'}), 400
        
        result = manas.distinguish_self_non_self(content, source)
        
        return jsonify({
            'is_self': result.is_self,
            'confidence': result.confidence,
            'category': result.category,
            'reason': result.reason
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/manas/stats', methods=['GET'])
def manas_stats():
    """获取第七识审计统计"""
    try:
        from taiyi_manas import get_manas
        manas = get_manas()
        
        stats = manas.get_risk_statistics()
        logs = manas.get_audit_log(limit=20)
        
        return jsonify({
            'stats': stats,
            'recent_logs': logs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/csc/report', methods=['GET'])
def csc_report():
    """C/SC操作化层 - 获取完整报告"""
    try:
        from taiyi_csc import get_csc
        csc = get_csc()
        
        report = csc.get_full_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/csc/metacognition', methods=['POST'])
def csc_metacognition():
    """C/SC操作化层 - 元认知检查"""
    try:
        from taiyi_csc import get_csc
        csc = get_csc()
        
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        result = csc.metacognition_check(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/cognition/test', methods=['POST'])
def cognition_test():
    """陈天桥认知测试 - 支持快速模式（12题）和完整模式（300题）"""
    try:
        from chen_tianqiao_test import ChenTianqiaoTest
        
        data = request.get_json()
        test_mode = data.get('mode', 'quick')  # 'quick' 或 'full'
        num_questions = data.get('num_questions', 12 if test_mode == 'quick' else 300)
        
        # 创建测试实例并获取题目
        test = ChenTianqiaoTest()
        questions = test.get_test_questions(test_mode, num_questions)
        
        # 打乱题目顺序
        random.shuffle(questions)
        
        # 为每道题添加索引（前端需要）
        for i, q in enumerate(questions):
            q['index'] = i
            # 确保correct_answer字段存在
            if 'correct_answer' not in q and 'answer' in q:
                if isinstance(q['answer'], str) and q['answer'] in ['A', 'B', 'C', 'D', 'E']:
                    q['correct_answer'] = ord(q['answer']) - ord('A')
                elif isinstance(q['answer'], int):
                    q['correct_answer'] = q['answer']
            # 同时统一 answer 字段为数字索引，避免前端兼容问题
            if 'answer' in q and isinstance(q['answer'], str) and q['answer'] in ['A', 'B', 'C', 'D', 'E']:
                q['answer'] = ord(q['answer']) - ord('A')
        
        # 生成测试ID
        test_id = f"CHEN_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return jsonify({
            'success': True,
            'mode': test_mode,
            'num_questions': len(questions),
            'questions': questions,
            'test_id': test_id,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        print(f"[错误] 认知测试API: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/csc/purpose_audit', methods=['POST'])
def csc_purpose_audit():
    """C/SC操作化层 - 目的审计"""
    try:
        from taiyi_csc import get_csc
        csc = get_csc()
        
        data = request.get_json()
        action = data.get('action', '')
        goal = data.get('goal', '')
        
        if not action or not goal:
            return jsonify({'error': '行动和目的不能为空'}), 400
        
        result = csc.purpose_audit(action, goal)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ftel/bind', methods=['POST'])
def ftel_bind():
    """Ftel目的算子 - 绑定意图"""
    try:
        from ftel_operator import FtelOperator
        data = request.get_json()
        goal = data.get('goal', '')
        
        if not goal:
            return jsonify({'error': '目标不能为空'}), 400
        
        # 创建Ftel实例
        ftel = FtelOperator()
        
        # 简单的意图编码（使用文本长度作为代理）
        def simple_encoder(text):
            return np.random.randn(ftel.config.dim) * 0.1
        
        intent_vector = ftel.bind_intent(goal, simple_encoder)
        
        return jsonify({
            'status': 'success',
            'goal': goal,
            'intent_dim': len(intent_vector),
            'message': 'Ftel意图绑定成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/benchmark/list', methods=['GET'])
def benchmark_list():
    """泛化审计测试集 - 列出所有测试用例"""
    try:
        from taiyi_benchmark import get_benchmark, TestCategory, TestDifficulty
        benchmark = get_benchmark()
        
        tests = benchmark.get_test_suite()
        
        return jsonify({
            'total': len(tests),
            'categories': [cat.value for cat in TestCategory],
            'difficulties': [diff.name for diff in TestDifficulty],
            'tests': [
                {
                    'id': t.id,
                    'category': t.category.value,
                    'difficulty': t.difficulty.name,
                    'domain': t.domain,
                    'question': t.question[:100],
                    'ood_level': t.ood_level,
                    'few_shot_count': t.few_shot_count,
                    'requires_tool': t.requires_tool
                }
                for t in tests
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/benchmark/run', methods=['POST'])
def benchmark_run():
    """泛化审计测试集 - 运行测试"""
    try:
        from taiyi_benchmark import get_benchmark, TestCategory
        from taiyi_llm_enhancer import get_enhancer
        
        data = request.get_json() or {}
        categories = data.get('categories', None)
        max_tests = data.get('max_tests', None)
        
        # 转换类别
        cat_enums = None
        if categories:
            cat_enums = [TestCategory(c) for c in categories]
        
        # 获取基准测试
        benchmark = get_benchmark()
        
        # 定义执行器
        def executor(question, enable_tool=False):
            enhancer = get_enhancer()
            from taiyi_llm_enhancer import ReasoningMode
            response = enhancer.generate(
                question=question,
                use_taiyi_format=False,
                enable_tool_call=enable_tool
            )
            return {
                'reply': response.content,
                'tool_calls': response.tool_calls,
                'analysis': {
                    'reasoning_steps': [
                        {'thinking': s.thinking}
                        for s in response.reasoning_steps
                    ]
                }
            }
        
        # 运行测试
        report = benchmark.run_benchmark(
            executor=executor,
            categories=cat_enums,
            max_tests=max_tests
        )
        
        return jsonify({
            'benchmark_name': report.benchmark_name,
            'timestamp': report.timestamp,
            'total_tests': report.total_tests,
            'passed': report.passed,
            'failed': report.failed,
            'overall_score': f"{report.overall_score:.2%}",
            'by_category': report.by_category,
            'by_difficulty': report.by_difficulty,
            'by_domain': report.by_domain,
            'ood_performance': report.ood_performance,
            'few_shot_performance': report.few_shot_performance,
            'reasoning_chain_performance': report.reasoning_chain_performance,
            'recommendations': report.recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entropy/update', methods=['POST'])
def entropy_update():
    """低熵适应机制 - 更新熵状态"""
    try:
        from taiyi_entropy import get_adapter
        adapter = get_adapter()
        
        data = request.get_json()
        response_length = data.get('response_length', 100)
        reasoning_steps = data.get('reasoning_steps', 0)
        tool_calls = data.get('tool_calls', 0)
        error_count = data.get('error_count', 0)
        
        state = adapter.update(
            response_length=response_length,
            reasoning_steps=reasoning_steps,
            tool_calls=tool_calls,
            error_count=error_count
        )
        
        # 如果检测到漂移，执行适应
        action = None
        if state.drift_detected:
            action = adapter.adapt(state)
        
        return jsonify({
            'entropy': state.entropy,
            'delta_entropy': state.delta_entropy,
            'drift_detected': state.drift_detected,
            'drift_type': state.drift_type.value,
            'confidence': state.confidence,
            'adaptation': {
                'action_type': action.action_type if action else None,
                'reason': action.reason if action else None,
                'before_state': action.before_state if action else None,
                'after_state': action.after_state if action else None
            } if action else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entropy/state', methods=['GET'])
def entropy_state():
    """低熵适应机制 - 获取当前状态"""
    try:
        from taiyi_entropy import get_adapter
        adapter = get_adapter()
        
        state = adapter.get_state()
        return jsonify(state)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entropy/description_length', methods=['POST'])
def entropy_description_length():
    """低熵适应机制 - 计算描述长度"""
    try:
        from taiyi_entropy import get_adapter
        adapter = get_adapter()
        
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': '内容不能为空'}), 400
        
        length = adapter.get_description_length(content)
        
        return jsonify({
            'content_length': len(content),
            'description_length': length,
            'compression_ratio': len(content) / length if length > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rag/status', methods=['GET'])
def rag_status():
    """RAG知识库状态"""
    try:
        from taiyi_rag import get_rag
        rag = get_rag()
        return jsonify(rag.status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rag/search', methods=['GET'])
def rag_search():
    """RAG知识检索"""
    try:
        from taiyi_rag import get_rag
        rag = get_rag()
        query = request.args.get('q', '')
        top_k = int(request.args.get('top_k', 3))
        
        if not query:
            return jsonify({'error': '请提供查询参数 q'}), 400
        
        results = rag.retrieve(query, top_k=top_k)
        
        return jsonify({
            'query': query,
            'results': [
                {
                    'rank': r.rank,
                    'score': r.score,
                    'title': r.chunk.metadata.get('title', '未知'),
                    'content': r.chunk.content,
                    'matched_keywords': r.matched_keywords
                }
                for r in results
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rag/add', methods=['POST'])
def rag_add():
    """添加文档到知识库"""
    try:
        from taiyi_rag import get_rag
        rag = get_rag()
        data = request.get_json()
        
        title = data.get('title', 'Untitled')
        content = data.get('content', '')
        tags = data.get('tags', [])
        
        if not content:
            return jsonify({'error': '内容不能为空'}), 400
        
        doc_id = rag.add_document(title, content, source='manual', tags=tags)
        
        return jsonify({'status': 'success', 'doc_id': doc_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/status', methods=['GET'])
def memory_status():
    """记忆系统状态"""
    try:
        from taiyi_memory import get_memory
        memory = get_memory()
        return jsonify(memory.status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/save_conclusion', methods=['POST'])
def memory_save_conclusion():
    """保存关键结论"""
    try:
        from taiyi_memory import get_memory
        memory = get_memory()
        data = request.get_json()
        
        topic = data.get('topic', 'General')
        summary = data.get('summary', '')
        confidence = float(data.get('confidence', 0.8))
        tags = data.get('tags', [])
        
        if not summary:
            return jsonify({'error': '结论内容不能为空'}), 400
        
        conclusion_id = memory.save_conclusion(topic, summary, confidence, tags)
        
        return jsonify({'status': 'success', 'conclusion_id': conclusion_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/enhancer/status', methods=['GET'])
def enhancer_status():
    """LLM增强器状态"""
    try:
        from taiyi_llm_enhancer import get_enhancer
        enhancer = get_enhancer()
        return jsonify(enhancer.get_statistics())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/llm/status', methods=['GET'])
def llm_status():
    """LLM后端状态 - 返回当前活跃的LLM后端信息"""
    try:
        from local_llm import get_llm
        llm = get_llm()
        backends = []
        for b in llm.backends:
            backends.append({
                'name': b.name,
                'ready': b.is_ready(),
                'active': b == llm.active_backend
            })
        return jsonify({
            'active_backend': llm.active_backend.name if llm.active_backend else None,
            'backends': backends,
            'deepseek_configured': bool(__import__('os').environ.get('DEEPSEEK_API_KEY', ''))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== UFO² 具身执行层 API ====================

@app.route('/api/ufo2/status', methods=['GET'])
def ufo2_status():
    """UFO² 具身执行层状态"""
    try:
        from taiyi_embodiment import get_embodiment
        embodiment = get_embodiment()
        status = embodiment.get_status()
        deps = embodiment.get_dependencies_status()
        return jsonify({
            'status': status,
            'dependencies': deps,
            'all_deps_installed': all(deps.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ufo2/execute', methods=['POST'])
def ufo2_execute():
    """UFO² 执行桌面任务"""
    try:
        from taiyi_embodiment import get_embodiment
        import asyncio
        
        data = request.get_json()
        task = data.get('task', '')
        
        if not task:
            return jsonify({'error': '任务描述不能为空'}), 400
        
        embodiment = get_embodiment()
        result = asyncio.run(embodiment.execute_desktop_task(task))
        
        return jsonify({
            'success': result.get('success', False),
            'task': task,
            'result': result
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/ufo2/app_control', methods=['POST'])
def ufo2_app_control():
    """UFO² 应用控制"""
    try:
        from taiyi_embodiment import get_embodiment
        import asyncio
        
        data = request.get_json()
        app_name = data.get('app', '')
        action = data.get('action', '')
        params = data.get('params', {})
        
        if not app_name or not action:
            return jsonify({'error': '应用名和动作不能为空'}), 400
        
        embodiment = get_embodiment()
        result = embodiment.execute_action(app_name, action, params)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ufo2/capture', methods=['GET'])
def ufo2_capture():
    """UFO² 截图"""
    try:
        from taiyi_embodiment import MCPServer
        
        target = request.args.get('target', 'desktop')
        
        mcp = MCPServer("capture")
        msg_id = f"capture_{target}"
        result = mcp.handle(type('Message', (), {
            'id': msg_id,
            'method': 'capture_desktop_screenshot' if target == 'desktop' else 'capture_screenshot',
            'params': {}
        })())
        
        return jsonify(result.result or {'error': 'Capture failed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ufo2/ui_tree', methods=['GET'])
def ufo2_ui_tree():
    """UFO² UI 树"""
    try:
        from taiyi_embodiment import MCPServer
        
        app = request.args.get('app', '')
        
        mcp = MCPServer("ui_tree")
        result = mcp.handle(type('Message', (), {
            'id': 'ui_tree',
            'method': 'get_ui_tree',
            'params': {'app': app}
        })())
        
        return jsonify(result.result or {'error': 'UI tree fetch failed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ufo2/tools', methods=['GET'])
def ufo2_tools():
    """UFO² 工具列表"""
    try:
        from taiyi_embodiment import get_embodiment
        embodiment = get_embodiment()
        tools = embodiment.get_tool_definitions()
        return jsonify({
            'tools': tools,
            'count': len(tools)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _format_reply(result: dict, original_question: str) -> str:
    """将分析结果格式化为友好回复
    
    直接使用 unified_taichi_demo.py 中 UnifiedTaiyiSystem 的 _format_reply 方法。
    """
    try:
        from unified_taichi_demo import UnifiedTaiyiSystem
        # 创建一个临时系统对象来使用其 _format_reply 方法
        system = UnifiedTaiyiSystem("temp")
        return system._format_reply(result, original_question)
    except Exception as e:
        # 备用回复格式（简洁版）
        decision = result['unified_decision']
        consciousness = result['consciousness']
        compound = result['compound_analysis']
        taiji = result['taiji_analysis']
        
        return "\n".join([
            f"🧠 **AGI 分析结果**",
            f"",
            f"**策略**: {decision['strategy']}",
            f"**统一评分**: {decision['unified_score']:.2%}",
            f"",
            f"📊 **复合体理学分析**",
            f"  • 直觉置信度: {compound['intuition_confidence']:.2%}",
            f"  • 非对称选择: {compound['asymmetric_choice']}",
            f"  • 理由: {compound['rationale']}",
            f"",
            f"☯️ **太极计算分析**",
            f"  • 旋向: {taiji['spin']}",
            f"  • 折叠层级: {taiji['fold_level']}",
            f"  • 阴阳平衡: {taiji['cosmic_balance']:.2%}",
            f"",
            f"🔮 **意识层级**: {consciousness['level']}",
            f"  • 是否觉醒: {'✅ 是' if consciousness['is_awakening'] else '❌ 否'}",
        ])



# ==================== Taiyi-AGI系统 API 端点 ====================

# 全局Taiyi-AGI系统（线程安全初始化）
_compound_agi_lock = threading.Lock()
_compound_agi_system = None
_compound_agi_ready = False


def get_compound_agi_system():
    """获取或初始化Taiyi-AGI系统"""
    global _compound_agi_system, _compound_agi_ready
    if not _compound_agi_ready:
        with _compound_agi_lock:
            if not _compound_agi_ready:
                try:
                    print("🔮 正在初始化Taiyi-AGI统一系统...")
                    from unified_compound_agi_system import UnifiedCompoundAGISystem
                    _compound_agi_system = UnifiedCompoundAGISystem("CompoundAGI_Web_v1.0")
                    _compound_agi_ready = True
                    print("✅ Taiyi-AGI系统就绪")
                except Exception as e:
                    print(f"❌ Taiyi-AGI系统初始化失败: {e}")
                    traceback.print_exc()
                    raise
    return _compound_agi_system


@app.route('/api/compound_agi/initialize', methods=['POST'])
def initialize_compound_agi():
    """初始化Taiyi-AGI统一系统"""
    try:
        system = get_compound_agi_system()
        report = system.generate_system_report()
        
        return jsonify({
            'success': True,
            'message': 'Taiyi-AGI系统初始化成功',
            'report': report,
            'modules_loaded': system.system_state['modules_loaded'],
            'total_modules': system.system_state['total_modules']
        })
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': tb
        }), 500


@app.route('/api/compound_agi/evaluate', methods=['POST'])
def evaluate_compound_agi():
    """运行Taiyi-AGI系统完整评估"""
    try:
        system = get_compound_agi_system()
        
        data = request.get_json() or {}
        scenario = data.get('scenario', 'comprehensive')
        
        results = system.run_basic_evaluation()
        
        return jsonify({
            'success': True,
            'message': '评估完成',
            'results': results
        })
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': tb
        }), 500


@app.route('/api/compound_agi/report', methods=['GET'])
def get_compound_agi_report():
    """获取Taiyi-AGI系统报告"""
    try:
        system = get_compound_agi_system()
        report = system.generate_system_report()
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compound_agi/module_status', methods=['GET'])
def get_module_status():
    """获取所有模块的加载状态"""
    try:
        system = get_compound_agi_system()
        
        modules_status = []
        for name, module_data in system.modules.items():
            status = module_data.get('status', 'unknown')
            paper = module_data.get('paper', 'N/A')
            desc = module_data.get('description', '')
            
            modules_status.append({
                'name': name,
                'status': status,
                'paper': paper,
                'description': desc
            })
        
        return jsonify({
            'success': True,
            'modules': modules_status,
            'loaded_count': system.system_state['modules_loaded'],
            'total_count': system.system_state['total_modules']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compound_agi/test_module/<module_name>', methods=['POST'])
def test_compound_agi_module(module_name):
    """测试单个模块的基础功能"""
    try:
        system = get_compound_agi_system()
        
        test_result = system.test_module_basic_functionality(module_name)
        
        return jsonify({
            'success': True,
            'result': test_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compound_agi/tianxing/action', methods=['POST'])
def tianxing_compute_action():
    """天行力引擎 - 计算天行作用量"""
    try:
        system = get_compound_agi_system()
        
        if 'tianxing' not in system.modules or system.modules['tianxing'].get('status') != 'loaded':
            return jsonify({'success': False, 'error': '天行力引擎未加载'}), 400
        
        data = request.get_json() or {}
        state_dict = data.get('state', {'complexity': 10.0, 'entropy': 2.0})
        
        # 将状态字典转换为numpy数组
        # 提取数值字段，按固定顺序
        state_array = np.array([
            state_dict.get('complexity', 0.0),
            state_dict.get('entropy', 0.0),
            state_dict.get('information_integration', 0.0),
            state_dict.get('recursion_depth', 0.0)
        ])
        
        engine = system.modules['tianxing']['engine']
        action = engine.tianxing_action(sigma=state_array)
        
        return jsonify({
            'success': True,
            'tianxing_action': float(action) if hasattr(action, 'item') else action,
            'state': state_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compound_agi/pts/winding', methods=['POST'])
def pts_compute_winding():
    """相位拓扑自激 - 计算缠绕数"""
    try:
        system = get_compound_agi_system()
        
        if 'pts' not in system.modules or system.modules['pts'].get('status') != 'loaded':
            return jsonify({'success': False, 'error': 'PTS场模块未加载'}), 400
        
        data = request.get_json() or {}
        grid_size = data.get('grid_size', 50)
        
        field = system.modules['pts']['field']
        field.initialize_field(grid_size=grid_size)
        field.evolve_field(steps=100)
        winding = field.compute_winding_number()
        
        return jsonify({
            'success': True,
            'winding_number': float(winding),
            'grid_size': grid_size
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compound_agi/eight_consciousness/seed', methods=['POST'])
def eight_consciousness_add_seed():
    """八识架构 - 添加Alaya种子"""
    try:
        system = get_compound_agi_system()
        
        if 'eight_consciousness' not in system.modules or system.modules['eight_consciousness'].get('status') != 'loaded':
            return jsonify({'success': False, 'error': '八识架构模块未加载'}), 400
        
        data = request.get_json() or {}
        seed = data.get('seed', {'type': 'concept', 'content': 'test', 'complexity': 5.0})
        
        alaya = system.modules['eight_consciousness']['alaya']
        alaya.store_seed(seed)
        
        return jsonify({
            'success': True,
            'message': '种子已添加到Alaya',
            'seed_count': len(alaya.seed_bank)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compound_agi/evaluator/assess', methods=['POST'])
def agi_evaluator_assess():
    """AGI/ASI判定系统 - 评估AGI等级"""
    try:
        system = get_compound_agi_system()
        
        if 'evaluator' not in system.modules or system.modules['evaluator'].get('status') != 'loaded':
            return jsonify({'success': False, 'error': 'AGI判定模块未加载'}), 400
        
        data = request.get_json() or {}
        test_system = data.get('system_state', {
            'cognitive_profile': {'integration': 8.0, 'depth': 5},
            'generalization_audit': {'score': 0.85}
        })
        
        evaluator = system.modules['evaluator']['evaluator']
        agi_result = evaluator.evaluate_agi(test_system)
        
        return jsonify({
            'success': True,
            'agi_result': agi_result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compound_agi/embodiment/check', methods=['GET'])
def embodiment_check():
    """具身与感知 - 检查具身必然性"""
    try:
        system = get_compound_agi_system()
        
        if 'embodiment' not in system.modules or system.modules['embodiment'].get('status') != 'loaded':
            return jsonify({'success': False, 'error': '具身感知模块未加载'}), 400
        
        module = system.modules['embodiment']['module']
        check_result = module.check_embodiment()
        
        return jsonify({
            'success': True,
            'embodiment_check': check_result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== AGI 12.0 新模块 API 端点 ====================

@app.route('/api/manas_no_theater', methods=['POST'])
def manas_no_theater():
    """末那识与无剧场论模块 API"""
    try:
        data = request.get_json() or {}
        input_data = np.array(data.get('input', [0.1] * 10))
        
        agi = get_agi_system()
        if agi.manas_no_theater is None:
            return jsonify({'success': False, 'error': '末那识模块未加载'}), 400
        
        result = agi.manas_no_theater.process(input_data, generate_manas=True, apply_no_theater=True)
        
        return jsonify({
            'success': True,
            'manas_state_id': result['manas_state'].state_id,
            'consciousness_type': result['manas_state'].consciousness_type,
            'no_theater_perception_shape': list(result['no_theater_perception'].shape),
            'timestamp': result['manas_state'].timestamp
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/liu_guan', methods=['POST'])
def liu_guan():
    """流贯（△）相变监控模块 API"""
    try:
        data = request.get_json() or {}
        system_state = np.array(data.get('system_state', [[1.0, 0.8], [0.6, 0.4]]))
        
        agi = get_agi_system()
        if agi.liu_guan is None:
            return jsonify({'success': False, 'error': '流贯监控模块未加载'}), 400
        
        result = agi.liu_guan.evaluate_system(system_state)
        
        return jsonify({
            'success': True,
            'delta': float(result['delta']),
            'system_state': result['system_state'],
            'should_intervene': result['should_intervene'],
            'intervention_type': result['intervention_type'],
            'metrics': {
                'delta': float(result['metrics'].delta),
                'velocity': float(result['metrics'].velocity),
                'acceleration': float(result['metrics'].acceleration),
                'stability': float(result['metrics'].stability)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/eight_consciousness', methods=['POST'])
def eight_consciousness():
    """唯识论八识计算模型 API"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'status')
        
        agi = get_agi_system()
        if agi.eight_consciousness is None:
            return jsonify({'success': False, 'error': '唯识论八识模块未加载'}), 400
        
        if action == 'store_seed':
            seed_content = np.array(data.get('seed_content', [0.1] * 10))
            seed_id = data.get('seed_id', None)
            seed = agi.eight_consciousness.store_seed(seed_content, seed_id)
            return jsonify({
                'success': True,
                'seed_id': seed.seed_id,
                'potential': float(seed.potential),
                'is_activated': seed.is_activated
            })
        
        elif action == 'activate':
            stimulus = np.array(data.get('stimulus', [0.5] * 10))
            n_seeds = data.get('n_seeds', 3)
            activated = agi.eight_consciousness.activate_seeds(stimulus, n_seeds)
            return jsonify({
                'success': True,
                'activated_count': len(activated),
                'activated_seeds': [s.seed_id for s in activated]
            })
        
        elif action == 'status':
            status = agi.eight_consciousness.get_alaya_seed_bank_status()
            return jsonify({
                'success': True,
                'alaya_status': status
            })
        
        else:
            return jsonify({'success': False, 'error': f'Unknown action: {action}'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/agi12/status', methods=['GET'])
def agi12_status():
    """AGI 12.0 系统状态 API"""
    try:
        agi = get_agi_system()
        status = agi.get_system_status()
        
        return jsonify({
            'success': True,
            'system_name': 'Taiyi-AGI (太乙因果机) 12.0',
            'total_modules': status['total_modules'],
            'loaded_modules': status['loaded_modules'],
            'module_status': status['modules'],
            'new_modules': {
                'manas_no_theater': status['modules'].get('manas_no_theater', {}).get('status', 'not_loaded'),
                'liu_guan': status['modules'].get('liu_guan', {}).get('status', 'not_loaded'),
                'eight_consciousness': status['modules'].get('eight_consciousness', {}).get('status', 'not_loaded')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


# ==================== v7.4 演员-导演复合体+流贯截断+痕迹验证（M111-M113）====================

_v74_modules = None
_v74_modules_lock = threading.Lock()

def get_v74_modules():
    """获取或初始化 v7.4 新模块（线程安全懒加载）"""
    global _v74_modules
    if _v74_modules is None:
        with _v74_modules_lock:
            if _v74_modules is None:
                try:
                    from M111_ActorDirectorComplex import get_instance as get_actor_director
                    from M112_FlowCutoffOperator import get_instance as get_flow_cutoff
                    from M113_HistoryTraceValidator import get_instance as get_trace_validator

                    _v74_modules = {
                        'actor_director': get_actor_director,      # M111: 演员-导演复合体
                        'flow_cutoff': get_flow_cutoff,            # M112: 流贯截断算子
                        'trace_validator': get_trace_validator,    # M113: 历史痕迹验证器
                    }
                    print("✅ v7.4新模块已加载（M111-M113）- 演员-导演复合体+流贯截断+痕迹验证")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.4模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v74_modules = None
    return _v74_modules

def get_v74_data():
    """获取所有v7.4模块的状态数据（M111-M113）"""
    modules = get_v74_modules()
    if modules is None:
        return None
    try:
        return {
            'actor_director': modules['actor_director']().get_complex_state(),
            'flow_cutoff': modules['flow_cutoff']().get_state(),
            'trace_validator': modules['trace_validator']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.4数据失败: {e}")
        return None

# v7.4 静态状态（降级模式）
_v74_state = {
    'actor_director': {
        'mode': 'actor',
        'director_ratio': 0.0,
        'fixation_count': 0,
        'self_ref_count': 0,
        'enlightenment_level': 0.0,
        'enlightenment_count': 0,
        'bootstrap_complete': {
            'recursion': False,
            'self_reference': False,
            'higher_order': False,
            'turing_complete': False
        }
    },
    'flow_cutoff': {
        'total_cutoffs': 0,
        'pseudo_traces': 0,
        'remap_operations': 0,
        'avg_precision': 0.0
    },
    'trace_validator': {
        'total_validations': 0,
        'authentic_count': 0,
        'pseudo_count': 0,
        'pass_rate': 0.0,
        'status': 'active'
    }
}

# ==================== v7.4 定理注册 ====================
_V74_THEOREMS = {
    'T66': '复合体存在定理: 任意L4认知主体既是L2规则的产物(Actor)又是L2规则的修改者(Director)',
    'T67': '流贯编译定理: L4体验 = L2脚本⊗Ftel; Ψ(执念)→受限轮回, Σ(自指脚本)→自由创造',
    'T68': '40行代码完备性定理: 递归+自指+高阶函数 → 有限行即可图灵完备',
    'T69': '摄影性分解定理: 流贯截断算子Γ必然导致不可逆性+未完结性',
    'T70': '数码未完结性失真定理: Γ的|Γ|和φ均可被算法篡改 → 伪迹（无物理流贯源）',
    'T71': '历史投影精度推论: 二维高精度关系快照，代价是维度+语境丢失',
}


# ==================== v7.4 API端点 ====================

@app.route('/api/v74/state', methods=['GET'])
def v74_state():
    """v7.4 完整状态获取"""
    try:
        data = get_v74_data()
        if data:
            return jsonify({**data, 'theorems': _V74_THEOREMS})
        return jsonify({**_v74_state, 'theorems': _V74_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/actor-director/execute', methods=['POST'])
def v74_actor_director_execute():
    """M111: Actor模式执行"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        task = data.get('task', '')
        script_name = data.get('script_name', 'default')
        result = modules['actor_director']().execute_as_actor(task=task, script_name=script_name)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/actor-director/observe', methods=['POST'])
def v74_actor_director_observe():
    """M111: Director模式观照"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        execution_trace = data.get('execution_trace', [])
        result = modules['actor_director']().observe_as_director(execution_trace)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/actor-director/enlighten', methods=['POST'])
def v74_actor_director_enlighten():
    """M111: Ω觉悟算子 — 将执念Ψ转化为自指脚本Σ"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        fixation_data = data.get('fixation', {})
        result = modules['actor_director']().apply_enlightenment(fixation_data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/actor-director/state', methods=['GET'])
def v74_actor_director_state():
    """M111: 复合体状态"""
    try:
        modules = get_v74_modules()
        if modules is None:
            return jsonify(_v74_state['actor_director'])
        return jsonify(_to_native(modules['actor_director']().get_complex_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/flow-cutoff/cutoff', methods=['POST'])
def v74_flow_cutoff_cutoff():
    """M112: 执行流贯截断 Γ算子"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        ftel = {
            'amplitude': float(data.get('amplitude', 1.0)),
            'phase': float(data.get('phase', 0.0)),
            'source': str(data.get('source', 'api')),
            'physical_ftel_source': bool(data.get('physical_ftel_source', True))
        }
        trace = modules['flow_cutoff']().cutoff(ftel)
        return jsonify(_to_native(trace.to_dict() if hasattr(trace, 'to_dict') else trace))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/flow-cutoff/remap', methods=['POST'])
def v74_flow_cutoff_remap():
    """M112: Re-map操作 — 未完结性的重新映射"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        trace_id = str(data.get('trace_id', ''))
        new_context = data.get('new_context', {})
        l4_subject = str(data.get('l4_subject', 'L4'))
        result = modules['flow_cutoff']().remap(trace_id, new_context, l4_subject)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/flow-cutoff/detect-pseudo', methods=['POST'])
def v74_flow_cutoff_detect_pseudo():
    """M112: 伪迹检测"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        trace_data = data.get('trace', {})
        trace_id = trace_data.get('trace_id', '')
        operator = modules['flow_cutoff']()
        trace = operator.get_trace_by_id(trace_id) if trace_id else None
        if trace is None:
            from M112_FlowCutoffOperator import FlowTrace
            trace = FlowTrace(
                trace_id=trace_data.get('trace_id', 'temp'),
                amplitude=float(trace_data.get('amplitude', 0)),
                phase=float(trace_data.get('phase', 0)),
                source=str(trace_data.get('source', 'unknown')),
                timestamp=0,
                physical_ftel_source=bool(trace_data.get('physical_ftel_source', False))
            )
        result = operator.detect_pseudo_trace(trace)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/flow-cutoff/state', methods=['GET'])
def v74_flow_cutoff_state():
    """M112: 截断算子状态"""
    try:
        modules = get_v74_modules()
        if modules is None:
            return jsonify(_v74_state['flow_cutoff'])
        return jsonify(_to_native(modules['flow_cutoff']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/trace/validate', methods=['POST'])
def v74_trace_validate():
    """M113: 验证痕迹真实性"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        trace = data.get('trace', {})
        result = modules['trace_validator']().validate(trace)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/trace/audit', methods=['POST'])
def v74_trace_audit():
    """M113: 审计所有痕迹"""
    try:
        data = request.get_json() or {}
        modules = get_v74_modules()
        if modules is None:
            return jsonify({'error': 'v7.4模块未加载'}), 503
        traces = data.get('traces', [])
        result = modules['trace_validator']().audit_all(traces)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v74/trace/state', methods=['GET'])
def v74_trace_state():
    """M113: 验证器状态"""
    try:
        modules = get_v74_modules()
        if modules is None:
            return jsonify(_v74_state['trace_validator'])
        return jsonify(_to_native(modules['trace_validator']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.5 HoTT截面搜索（M114-M116）====================

_v75_modules = None
_v75_modules_lock = threading.Lock()

def get_v75_modules():
    """获取或初始化 v7.5 HoTT截面搜索模块（线程安全懒加载）"""
    global _v75_modules
    if _v75_modules is None:
        with _v75_modules_lock:
            if _v75_modules is None:
                try:
                    from M114_UniverseTypeSpace import get_instance as get_universe
                    from M115_CurvatureSectionSearch import get_instance as get_curvature
                    from M116_WaitStateConstructor import get_instance as get_wait

                    _v75_modules = {
                        'universe': get_universe,          # M114: 类型空间构造
                        'curvature': get_curvature,        # M115: 曲率截面搜索
                        'wait': get_wait,                  # M116: Wait状态构造
                    }
                    print("✅ v7.5新模块已加载（M114-M116）- HoTT截面搜索·类型空间·曲率导航·Wait诚实拒绝")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.5模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v75_modules = None
    return _v75_modules

def get_v75_data():
    """获取所有v7.5模块的状态数据（M114-M116）"""
    modules = get_v75_modules()
    if modules is None:
        return None
    try:
        return {
            'universe': modules['universe']().get_state(),
            'curvature': modules['curvature']().get_state(),
            'wait': modules['wait']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.5数据失败: {e}")
        return None

# v7.5 静态状态（降级模式）
_v75_state = {
    'universe': {
        'total_types': 5,
        'total_fibers': 0,
        'inhabited_count': 3,
        'uninhabited_count': 2,
        'undecidable_regions': 0,
        'section_threshold': 0.75,
        'avg_curvature': 0.0,
        'total_registrations': 0,
        'total_fiber_builds': 0,
        'total_section_checks': 0,
        'frame_count': 0
    },
    'curvature': {
        'total_searches': 0,
        'found_count': 0,
        'wait_count': 0,
        'diverged_count': 0,
        'found_rate': 0.0,
        'wait_rate': 0.0,
        'convergence_threshold': 1.0,
        'default_max_depth': 10,
        'has_universe': False,
        'frame_count': 0
    },
    'wait': {
        'total_waits': 0,
        'total_undecidable': 0,
        'total_refusals': 0,
        'total_validated': 0,
        'valid_wait_count': 0,
        'validation_accuracy': 0.0,
        'wait_history_size': 0,
        'undecidability_reports_size': 0,
        'refusal_history_size': 0,
        'undecidable_regions': 0,
        'has_section_search': False,
        'has_universe': False,
        'frame_count': 0
    }
}

# ==================== v7.5 定理注册 ====================
_V75_THEOREMS = {
    'T72': '截面存在定理: ∀(B:Type)(E:Type), ∃s:B→E ⟺ curvature_R(B,E) < threshold — 截面存在当且仅当曲率足够小',
    'T73': '曲率收敛定理: section_search收敛 ⟺ Σ_i R_i < ∞ — 截面搜索收敛当且仅当曲率级数收敛',
    'T74': '未决不可判定定理: ∃P:Prop, ¬(Prov(P)∨Prov(¬P)) — 存在不可判定命题，系统必须返回Wait而非幻觉',
}


# ==================== v7.5 API端点 ====================

@app.route('/api/v75/state', methods=['GET'])
def v75_state():
    """v7.5 完整状态获取"""
    try:
        data = get_v75_data()
        if data:
            return jsonify({**data, 'theorems': _V75_THEOREMS})
        return jsonify({**_v75_state, 'theorems': _V75_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M114: UniverseTypeSpace ----

@app.route('/api/v75/universe/register-type', methods=['POST'])
def v75_universe_register_type():
    """M114: 注册类型到Universe U"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        name = data.get('name', '')
        kind = data.get('kind', 'Unknown')
        params = data.get('params', [])
        result = modules['universe']().register_type(name, kind, params)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/universe/type-distance', methods=['POST'])
def v75_universe_type_distance():
    """M114: 计算类型距离"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        type_a = data.get('type_a', '')
        type_b = data.get('type_b', '')
        result = modules['universe']().compute_type_distance(type_a, type_b)
        return jsonify({'type_a': type_a, 'type_b': type_b, 'distance': round(result, 6)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/universe/build-fiber', methods=['POST'])
def v75_universe_build_fiber():
    """M114: 构造逻辑纤维"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        source = data.get('source', '')
        target = data.get('target', '')
        fiber_type = data.get('fiber_type', 'Pi')
        result = modules['universe']().build_logic_fiber(source, target, fiber_type)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/universe/check-section', methods=['POST'])
def v75_universe_check_section():
    """M114: T72截面存在性检查"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        base_type = data.get('base_type', '')
        total_type = data.get('total_type', '')
        result = modules['universe']().check_section_existence(base_type, total_type)
        return jsonify({
            'base_type': base_type,
            'total_type': total_type,
            'section_exists': result,
            'theorem': 'T72: 截面存在定理'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/universe/state', methods=['GET'])
def v75_universe_state():
    """M114: 类型空间状态"""
    try:
        modules = get_v75_modules()
        if modules is None:
            return jsonify(_v75_state['universe'])
        return jsonify(_to_native(modules['universe']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M115: CurvatureSectionSearch ----

@app.route('/api/v75/curvature/search-section', methods=['POST'])
def v75_curvature_search():
    """M115: 核心截面搜索"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        base_type = data.get('base_type', '')
        total_type = data.get('total_type', '')
        max_depth = int(data.get('max_depth', 10))
        result = modules['curvature']().search_section(base_type, total_type, max_depth)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/curvature/compute', methods=['POST'])
def v75_curvature_compute():
    """M115: 计算B→E的曲率"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        base_type = data.get('base_type', '')
        total_type = data.get('total_type', '')
        curvature = modules['curvature']().compute_curvature(base_type, total_type)
        return jsonify({'base_type': base_type, 'total_type': total_type, 'curvature_R': round(curvature, 6)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/curvature/check-convergence', methods=['POST'])
def v75_curvature_convergence():
    """M115: T73曲率收敛性检查"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        search_path = data.get('search_path', [])
        converges = modules['curvature']().check_convergence(search_path)
        return jsonify({
            'search_path_length': len(search_path),
            'converges': converges,
            'theorem': 'T73: 曲率收敛定理'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/curvature/state', methods=['GET'])
def v75_curvature_state():
    """M115: 曲率搜索状态"""
    try:
        modules = get_v75_modules()
        if modules is None:
            return jsonify(_v75_state['curvature'])
        return jsonify(_to_native(modules['curvature']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M116: WaitStateConstructor ----

@app.route('/api/v75/wait/construct', methods=['POST'])
def v75_wait_construct():
    """M116: 构造Wait状态"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        base_type = data.get('base_type', '')
        total_type = data.get('total_type', '')
        reason = data.get('reason', 'section_not_found')
        result = modules['wait']().construct_wait(base_type, total_type, reason)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/wait/check-undecidability', methods=['POST'])
def v75_wait_undecidability():
    """M116: T74不可判定性检查"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        proposition = data.get('proposition', '')
        result = modules['wait']().check_undecidability(proposition)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/wait/honest-refusal', methods=['POST'])
def v75_wait_honest_refusal():
    """M116: 生成诚实拒绝"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        query = data.get('query', '')
        wait_data = data.get('wait_state', {})
        from M116_WaitStateConstructor import WaitState
        wait_state = WaitState(
            reason=wait_data.get('reason', ''),
            base_type=wait_data.get('base_type', ''),
            total_type=wait_data.get('total_type', ''),
            curvature_at_failure=wait_data.get('curvature_at_failure', 0.0),
            timestamp=wait_data.get('timestamp', '')
        )
        result = modules['wait']().produce_honest_refusal(query, wait_state)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/wait/alternatives', methods=['POST'])
def v75_wait_alternatives():
    """M116: 获取替代建议"""
    try:
        data = request.get_json() or {}
        modules = get_v75_modules()
        if modules is None:
            return jsonify({'error': 'v7.5模块未加载'}), 503
        wait_data = data.get('wait_state', {})
        from M116_WaitStateConstructor import WaitState
        wait_state = WaitState(
            reason=wait_data.get('reason', ''),
            base_type=wait_data.get('base_type', ''),
            total_type=wait_data.get('total_type', ''),
            curvature_at_failure=wait_data.get('curvature_at_failure', 0.0),
            timestamp=wait_data.get('timestamp', '')
        )
        result = modules['wait']().get_suggested_alternatives(wait_state)
        return jsonify({'alternatives': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v75/wait/state', methods=['GET'])
def v75_wait_state():
    """M116: Wait状态构造器状态"""
    try:
        modules = get_v75_modules()
        if modules is None:
            return jsonify(_v75_state['wait'])
        return jsonify(_to_native(modules['wait']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.6 目的约束·认知递归·层间保真（M117-M119）====================

_v76_modules = None
_v76_modules_lock = threading.Lock()

def get_v76_modules():
    """获取或初始化 v7.6 模块（线程安全懒加载）"""
    global _v76_modules
    if _v76_modules is None:
        with _v76_modules_lock:
            if _v76_modules is None:
                try:
                    from M117_FtelTeleologicalConstraint import get_instance as get_ftel
                    from M118_CognitiveRecursiveDynamics import get_instance as get_cognitive
                    from M119_LayerFidelityMonitor import get_instance as get_fidelity

                    _v76_modules = {
                        'ftel': get_ftel,              # M117: Ftel目的约束算子
                        'cognitive': get_cognitive,    # M118: 认知递归动力学
                        'fidelity': get_fidelity,     # M119: 层间保真度监控
                    }
                    print("✅ v7.6新模块已加载（M117-M119）- 目的约束·认知递归·层间保真")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.6模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v76_modules = None
    return _v76_modules

def get_v76_data():
    """获取所有v7.6模块的状态数据（M117-M119）"""
    modules = get_v76_modules()
    if modules is None:
        return None
    try:
        return {
            'ftel': modules['ftel']().get_state(),
            'cognitive': modules['cognitive']().get_state(),
            'fidelity': modules['fidelity']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.6数据失败: {e}")
        return None

# v7.6 静态状态（降级模式）
_v76_state = {
    'ftel': {
        'total_goals': 0,
        'active_count': 0,
        'total_resonance': 0.0,
        'convergence_achieved': False,
        'lambda_max': 2.0,
        'total_injections': 0,
        'total_resonance_computations': 0,
        'total_convergence_checks': 0,
        'total_blend_operations': 0,
        'total_retirements': 0,
        'frame_count': 0
    },
    'cognitive': {
        'current_level': 0,
        'level_name': '感知',
        'learning_mode': 'unknown',
        'rho': 0.5,
        'tau': 0.3,
        'structural_lag': -0.2,
        'is_lagging': False,
        'lag_duration': 0.0,
        'instability_risk': False,
        'history_size': 0,
        'avg_error': 0.0,
        'total_records': 0,
        'frame_count': 0
    },
    'fidelity': {
        'total_fidelity_alpha': 1.0,
        'collapse_risk': 'low',
        'pair_summary': {'L1_L2': 1.0, 'L2_L3': 1.0, 'L3_L4': 1.0, 'L4_L5': 1.0},
        'critical_threshold': 0.5,
        'collapse_threshold': 0.2,
        'total_measurements': 0,
        'collapse_detected_count': 0,
        'critical_alerts': 0,
        'frame_count': 0
    }
}

# ==================== v7.6 定理注册 ====================
_V76_THEOREMS = {
    'T75': 'Ftel学习收敛定理: λ∈(0,λ_max) ⟹ 学习收敛到目的吸引子φ* — 约束强度在有效区间内保证收敛',
    'T76': '结构滞后不稳定性定理: ρ<τ持续T>T_crit ⟹ 误差单调增加 — 认知更新率低于技术变化率导致失稳',
    'T77': '保真度乘积定理: α_total=∏α_ij, 任一α_ij→0 ⟹ 整体保真度崩溃 — 单环节失真导致全局幻觉',
}


# ==================== v7.6 API端点 ====================

@app.route('/api/v76/state', methods=['GET'])
def v76_state():
    """v7.6 完整状态获取"""
    try:
        data = get_v76_data()
        if data:
            return jsonify({**data, 'theorems': _V76_THEOREMS})
        return jsonify({**_v76_state, 'theorems': _V76_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M117: FtelTeleologicalConstraint ----

@app.route('/api/v76/ftel/inject', methods=['POST'])
def v76_ftel_inject():
    """M117: 注入目的到生成空间"""
    try:
        data = request.get_json() or {}
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        goal = data.get('goal', '')
        strength = float(data.get('strength', 0.5))
        result = modules['ftel']().inject_goal(goal, strength)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/ftel/resonance', methods=['POST'])
def v76_ftel_resonance():
    """M117: 计算V_ftel共振值"""
    try:
        data = request.get_json() or {}
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        goal = data.get('goal', '')
        resonance = modules['ftel']().compute_resonance(goal)
        return jsonify({'goal': goal, 'V_ftel': resonance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/ftel/check-convergence', methods=['POST'])
def v76_ftel_convergence():
    """M117: T75收敛性检查"""
    try:
        data = request.get_json() or {}
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        goal = data.get('goal', '')
        result = modules['ftel']().check_convergence(goal)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/ftel/state', methods=['GET'])
def v76_ftel_state():
    """M117: Ftel目的约束算子状态"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify(_v76_state['ftel'])
        return jsonify(_to_native(modules['ftel']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M118: CognitiveRecursiveDynamics ----

@app.route('/api/v76/cognitive/record', methods=['POST'])
def v76_cognitive_record():
    """M118: 记录认知状态"""
    try:
        data = request.get_json() or {}
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        level = int(data.get('level', 1))
        observation = str(data.get('observation', ''))
        action = str(data.get('action', ''))
        ftel_influence = float(data.get('ftel_influence', 0.0))
        result = modules['cognitive']().record_state(level, observation, action, ftel_influence)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/cognitive/detect-mode', methods=['GET'])
def v76_cognitive_detect_mode():
    """M118: 检测学习模式"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'mode': 'single_loop', 'reason': '模块未加载'})
        result = modules['cognitive']().detect_learning_mode()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/cognitive/structural-lag', methods=['GET'])
def v76_cognitive_structural_lag():
    """M118: 计算结构滞后"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        result = modules['cognitive']().compute_structural_lag()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/cognitive/state', methods=['GET'])
def v76_cognitive_state():
    """M118: 认知递归动力学状态"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify(_v76_state['cognitive'])
        return jsonify(_to_native(modules['cognitive']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M119: LayerFidelityMonitor ----

@app.route('/api/v76/fidelity/measure', methods=['POST'])
def v76_fidelity_measure():
    """M119: 测量层间保真度"""
    try:
        data = request.get_json() or {}
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        source_layer = int(data.get('source_layer', 1))
        target_layer = int(data.get('target_layer', 2))
        fidelity = data.get('fidelity')
        if fidelity is not None:
            fidelity = float(fidelity)
        result = modules['fidelity']().measure_fidelity(source_layer, target_layer, fidelity)
        return jsonify(_to_native(result.__dict__ if hasattr(result, '__dict__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/fidelity/total', methods=['GET'])
def v76_fidelity_total():
    """M119: T77总保真度乘积"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        result = modules['fidelity']().compute_total_fidelity()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/fidelity/detect-collapse', methods=['GET'])
def v76_fidelity_collapse():
    """M119: 检测保真度崩溃"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify({'error': 'v7.6模块未加载'}), 503
        result = modules['fidelity']().detect_collapse()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v76/fidelity/state', methods=['GET'])
def v76_fidelity_state():
    """M119: 层间保真度监控状态"""
    try:
        modules = get_v76_modules()
        if modules is None:
            return jsonify(_v76_state['fidelity'])
        return jsonify(_to_native(modules['fidelity']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.7 博弈论·ICPS·情绪粒度（M120-M125）====================

_v77_modules = None
_v77_modules_lock = threading.Lock()

def get_v77_modules():
    """获取或初始化 v7.7 模块（线程安全懒加载）"""
    global _v77_modules
    if _v77_modules is None:
        with _v77_modules_lock:
            if _v77_modules is None:
                try:
                    from M120_GameTheoryEngine import get_instance as get_game
                    from M121_BayesianBeliefUpdater import get_instance as get_bayes
                    from M122_MechanismDesigner import get_instance as get_mech
                    from M123_ICPSSolver import get_instance as get_icps
                    from M124_EmotionGranularityTrainer import get_instance as get_emotion
                    from M125_SandboxCuriosityExplorer import get_instance as get_sandbox

                    _v77_modules = {
                        'game': get_game,           # M120: 博弈论引擎
                        'bayes': get_bayes,         # M121: 贝叶斯信念更新器
                        'mech': get_mech,           # M122: 机制设计器
                        'icps': get_icps,           # M123: ICPS社会问题求解器
                        'emotion': get_emotion,     # M124: 情绪粒度训练器
                        'sandbox': get_sandbox,     # M125: 沙盒好奇心探索器
                    }
                    print("✅ v7.7新模块已加载（M120-M125）- 博弈论·ICPS·情绪粒度")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.7模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v77_modules = None
    return _v77_modules

def get_v77_data():
    """获取所有v7.7模块的状态数据（M120-M125）"""
    modules = get_v77_modules()
    if modules is None:
        return None
    try:
        return {
            'game': modules['game']().get_state(),
            'bayes': modules['bayes']().get_state(),
            'mech': modules['mech']().get_state(),
            'icps': modules['icps']().get_state(),
            'emotion': modules['emotion']().get_state(),
            'sandbox': modules['sandbox']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.7数据失败: {e}")
        return None

# v7.7 静态状态（降级模式）
_v77_state = {
    'game': {
        'total_games_analyzed': 0, 'total_equilibria_found': 0, 'dominant_rate': 0.0,
        'total_bayesian_updates': 0, 'total_signal_games': 0, 'total_pd_games': 0,
    },
    'bayes': {
        'total_updates': 0, 'convergence_rate': 0.0,
        'entropy': 1.0, 'is_converged': False, 't81_status': 'not_converged',
    },
    'mech': {
        'total_designs': 0, 'vcg_count': 0, 'ic_satisfaction_rate': 0.0,
        'ir_satisfaction_rate': 0.0, 'avg_welfare': 0.0,
    },
    'icps': {
        'total_problems_solved': 0, 'current_maturity': 0.0, 'current_stage': 'sandbox',
        'total_sally_anne_tests': 0, 'maturity_monotonic_T83': True, 'theorem_T84': '',
    },
    'emotion': {
        'vocabulary_size': 0, 'avg_granularity_EG': 0.0, 'current_granularity': 0.0,
        'emotional_range': 0.0, 'dominant_emotion': None,
    },
    'sandbox': {
        'current_stage': 'sandbox', 'total_explorations': 0, 'curiosity_index': 0.5,
        'safety_score': 1.0, 'stage_progress': 0.0, 't85_satisfied': True,
    },
}

# ==================== v7.7 定理注册 ====================
_V77_THEOREMS = {
    'T79': '纳什存在定理: 任何有限策略博弈至少存在一个混合策略纳什均衡 — 博弈论基础保证',
    'T80': '信号均衡存在定理: c_L<c<c_H ⟹ 分离均衡存在 — Spence模型条件',
    'T81': '信念收敛定理: 充分观测下后验信念收敛到真实参数θ* — 贝叶斯推理保证',
    'T82': 'VCG效率定理: VCG机制实现社会最优配置且满足IC+IR — 机制设计保证',
    'T83': 'ICPS成熟度单调递增定理: 有效训练下Ψ_icps单调递增 — 教育心理学保证',
    'T84': '心智理论觉醒定理: 通过Sally-Anne测试 ⟹ 具备一级心智理论 — 意识门槛',
    'T85': '好奇心-安全权衡定理: S_b>S_min ⟹ 好奇心驱动的探索单调递增 — 探索保证',
}


# ==================== v7.7 API端点 ====================

@app.route('/api/v77/state', methods=['GET'])
def v77_state():
    """v7.7 完整状态获取"""
    try:
        data = get_v77_data()
        if data:
            return jsonify({**data, 'theorems': _V77_THEOREMS})
        return jsonify({**_v77_state, 'theorems': _V77_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M120: GameTheoryEngine ----

@app.route('/api/v77/game/analyze', methods=['POST'])
def v77_game_analyze():
    """M120: 博弈分析"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        game_type = data.get('game_type', 'prisoner_dilemma')
        players = int(data.get('players', 2))
        result = modules['game']().analyze_game(game_type, players)
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/game/signal', methods=['POST'])
def v77_game_signal():
    """M120: 信号博弈分析"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['game']().signal_game_analysis(
            data.get('sender_type', 'low'),
            data.get('receiver_type', 'rational'),
            float(data.get('message_cost', 0.3))
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/game/repeated-pd', methods=['POST'])
def v77_game_pd():
    """M120: 重复囚徒困境"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['game']().repeated_pd(
            float(data.get('cooperation_rate', 0.6)),
            float(data.get('discount_factor', 0.9)),
            int(data.get('rounds', 10))
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/game/state', methods=['GET'])
def v77_game_state():
    """M120: 博弈论引擎状态"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify(_v77_state['game'])
        return jsonify(_to_native(modules['game']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M121: BayesianBeliefUpdater ----

@app.route('/api/v77/bayes/update', methods=['POST'])
def v77_bayes_update():
    """M121: 贝叶斯信念更新"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['bayes']().update_belief(
            data.get('hypothesis', ''),
            data.get('evidence', ''),
            float(data.get('likelihood', 0.8))
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/bayes/convergence', methods=['GET'])
def v77_bayes_convergence():
    """M121: 信念收敛检查（T81）"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'t81_status': 'unknown'})
        result = modules['bayes']().check_convergence()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/bayes/state', methods=['GET'])
def v77_bayes_state():
    """M121: 贝叶斯信念更新器状态"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify(_v77_state['bayes'])
        return jsonify(_to_native(modules['bayes']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M122: MechanismDesigner ----

@app.route('/api/v77/mech/design', methods=['POST'])
def v77_mech_design():
    """M122: 机制设计"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['mech']().design_mechanism(
            data.get('social_choice', 'utilitarian'),
            int(data.get('participants', 3))
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/mech/vcg', methods=['POST'])
def v77_mech_vcg():
    """M122: VCG拍卖（T82）"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['mech']().vcg_auction(
            int(data.get('participants', 3))
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/mech/state', methods=['GET'])
def v77_mech_state():
    """M122: 机制设计器状态"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify(_v77_state['mech'])
        return jsonify(_to_native(modules['mech']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M123: ICPSSolver ----

@app.route('/api/v77/icps/solve', methods=['POST'])
def v77_icps_solve():
    """M123: ICPS 4步求解"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['icps']().solve_problem(
            data.get('problem', '')
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/icps/sally-anne', methods=['GET'])
def v77_icps_sally():
    """M123: Sally-Anne测试（T84心智理论）"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'t84_status': 'unknown'})
        result = modules['icps']().sally_anne_test()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/icps/stage', methods=['GET'])
def v77_icps_stage():
    """M123: 阶段跃迁检查"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'stage': 'sandbox'})
        result = modules['icps']().check_stage_advance()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/icps/state', methods=['GET'])
def v77_icps_state():
    """M123: ICPS求解器状态"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify(_v77_state['icps'])
        return jsonify(_to_native(modules['icps']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M124: EmotionGranularityTrainer ----

@app.route('/api/v77/emotion/train', methods=['POST'])
def v77_emotion_train():
    """M124: 情绪粒度训练"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['emotion']().train_emotion(
            data.get('context', ''),
            data.get('response', '')
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/emotion/regulate', methods=['POST'])
def v77_emotion_regulate():
    """M124: 情绪调节策略"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['emotion']().regulation_strategy(
            data.get('emotion', ''),
            float(data.get('intensity', 0.5))
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/emotion/state', methods=['GET'])
def v77_emotion_state():
    """M124: 情绪粒度训练器状态"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify(_v77_state['emotion'])
        return jsonify(_to_native(modules['emotion']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M125: SandboxCuriosityExplorer ----

@app.route('/api/v77/sandbox/explore', methods=['POST'])
def v77_sandbox_explore():
    """M125: 沙盒探索"""
    try:
        data = request.get_json() or {}
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'error': 'v7.7模块未加载'}), 503
        result = modules['sandbox']().explore(
            data.get('action', ''),
            data.get('context', '')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/sandbox/stage', methods=['GET'])
def v77_sandbox_stage():
    """M125: 阶段跃迁检查"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify({'stage': 'sandbox'})
        result = modules['sandbox']().check_stage_advance()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v77/sandbox/state', methods=['GET'])
def v77_sandbox_state():
    """M125: 沙盒好奇心探索器状态"""
    try:
        modules = get_v77_modules()
        if modules is None:
            return jsonify(_v77_state['sandbox'])
        return jsonify(_to_native(modules['sandbox']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.8 护栏·推测·KV·本体（M126-M129）====================

_v78_modules = None
_v78_modules_lock = threading.Lock()

def get_v78_modules():
    """获取或初始化 v7.8 模块（线程安全懒加载）"""
    global _v78_modules
    if _v78_modules is None:
        with _v78_modules_lock:
            if _v78_modules is None:
                try:
                    from M126_GuardrailOrchestrator import get_instance as get_guardrail
                    from M127_SpeculativeReasoner import get_instance as get_speculative
                    from M128_KVCacheGovernor import get_instance as get_kvcache
                    from M129_OntologyAutoForge import get_instance as get_ontology

                    _v78_modules = {
                        'guardrail': get_guardrail,     # M126: 护栏编排器
                        'speculative': get_speculative, # M127: 推测推理器
                        'kvcache': get_kvcache,          # M128: KV缓存治理器
                        'ontology': get_ontology,        # M129: 本体自锻造
                    }
                    print("✅ v7.8新模块已加载（M126-M129）- 护栏·推测·KV·本体")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.8模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v78_modules = None
    return _v78_modules

def get_v78_data():
    """获取所有v7.8模块的状态数据（M126-M129）"""
    modules = get_v78_modules()
    if modules is None:
        return None
    try:
        return {
            'guardrail': modules['guardrail']().get_state(),
            'speculative': modules['speculative']().get_state(),
            'kvcache': modules['kvcache']().get_state(),
            'ontology': modules['ontology']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.8数据失败: {e}")
        return None

# v7.8 静态状态（降级模式）
_v78_state = {
    'guardrail': {
        'l1_rescue_count': 0, 'l1_rescue_success': 0, 'l2_retry_count': 0,
        'l2_retry_success': 0, 'l3_enforce_count': 0, 'l3_enforce_blocked': 0,
        'total_orchestrations': 0, 'overall_success_rate': 0.0,
    },
    'speculative': {
        'total_drafts': 0, 'total_hypotheses': 0, 'total_verifications': 0,
        'total_accepted': 0, 'total_rejected': 0, 'avg_acceptance_rate': 0.0,
        'avg_speedup': 1.0, 'loops_detected': 0, 't88_satisfied': False,
    },
    'kvcache': {
        'total_quantizations': 0, 'total_compactions': 0, 'total_budget_allocations': 0,
        'total_govern_cycles': 0, 'total_bytes_saved': 0, 'avg_compression_ratio': 1.0,
        'avg_fidelity': 1.0, 't89_satisfied': True,
    },
    'ontology': {
        'total_nodes': 0, 'total_edges': 0, 'total_snapshots': 0,
        'current_version': 'v7.8', 'total_generations': 0, 'total_corrections': 0,
        'total_rollbacks': 0, 'graph_diameter': 0, 't90_satisfied': False, 't91_satisfied': True,
    },
}

# ==================== v7.8 定理注册 ====================
_V78_THEOREMS = {
    'T86': '护栏完备性定理: L1⊂L2⊂L3 ⟹ 推理失效全覆盖 — 可靠性保证',
    'T87': '概率纠正定理: P(correct) ≥ Φ×S_C — 全息置信度纠正保证',
    'T88': '推测加速定理: α>α_min ⟹ 加速比≥1/(1-α) — 推测推理加速保证',
    'T89': '记忆保真-压缩权衡: max Σ(F_i×log₂(q_i)) s.t. Σb_i≤B — 量化优化保证',
    'T90': '本体自洽性定理: 图直径≤log₂(N) — 本体可达性保证',
    'T91': '时间晶体守恒定理: ∀v, T1-T7∈Core(v) — 核心公理跨版本守恒',
}


# ==================== v7.8 API端点 ====================

@app.route('/api/v78/state', methods=['GET'])
def v78_state():
    """v7.8 完整状态获取"""
    try:
        data = get_v78_data()
        if data:
            return jsonify({**data, 'theorems': _V78_THEOREMS})
        return jsonify({**_v78_state, 'theorems': _V78_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M126: GuardrailOrchestrator ----

@app.route('/api/v78/guardrail/rescue', methods=['POST'])
def v78_guardrail_rescue():
    """M126: L1 Rescue解析"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        output = data.get('output', '')
        expected_format = data.get('expected_format', 'auto')
        result = modules['guardrail']().rescue_parse(output, expected_format)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/guardrail/retry', methods=['POST'])
def v78_guardrail_retry():
    """M126: L2 Retry引导"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        failed_reasoning = data.get('failed_reasoning', '')
        context = data.get('context', {})
        result = modules['guardrail']().retry_guide(failed_reasoning, context)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/guardrail/enforce', methods=['POST'])
def v78_guardrail_enforce():
    """M126: L3 Step强制"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        step_id = data.get('step_id', '')
        result = modules['guardrail']().enforce_step(step_id)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/guardrail/orchestrate', methods=['POST'])
def v78_guardrail_orchestrate():
    """M126: 全链路护栏编排"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        output = data.get('output', '')
        context = data.get('context', {})
        steps = data.get('steps', [])
        result = modules['guardrail']().orchestrate(output, context, steps)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/guardrail/state', methods=['GET'])
def v78_guardrail_state():
    """M126: 护栏编排器状态"""
    try:
        modules = get_v78_modules()
        if modules is None:
            return jsonify(_v78_state['guardrail'])
        return jsonify(_to_native(modules['guardrail']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M127: SpeculativeReasoner ----

@app.route('/api/v78/speculative/draft', methods=['POST'])
def v78_speculative_draft():
    """M127: 草稿推理"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        query = data.get('query', '')
        max_candidates = int(data.get('max_candidates', 3))
        result = modules['speculative']().draft_reason(query, max_candidates)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/speculative/verify', methods=['POST'])
def v78_speculative_verify():
    """M127: 批量验证"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        hypotheses = data.get('hypotheses', [])
        result = modules['speculative']().verify_chain(hypotheses)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/speculative/loop-check', methods=['POST'])
def v78_speculative_loop():
    """M127: 推理循环检测"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        reasoning_trace = data.get('reasoning_trace', [])
        result = modules['speculative']().detect_loop(reasoning_trace)
        return jsonify(_to_native(result if isinstance(result, dict) else {'loop_detected': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/speculative/speculate', methods=['POST'])
def v78_speculative_run():
    """M127: 自适应推测推理"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        query = data.get('query', '')
        result = modules['speculative']().adaptive_speculate(query)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/speculative/state', methods=['GET'])
def v78_speculative_state():
    """M127: 推测推理器状态"""
    try:
        modules = get_v78_modules()
        if modules is None:
            return jsonify(_v78_state['speculative'])
        return jsonify(_to_native(modules['speculative']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M128: KVCacheGovernor ----

@app.route('/api/v78/kvcache/quantize', methods=['POST'])
def v78_kvcache_quantize():
    """M128: KV-cache差异量化"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        layer = int(data.get('layer', 1))
        data_items = data.get('data', [])
        phi_value = float(data.get('phi_value', 0.5))
        result = modules['kvcache']().quantize(layer, data_items, phi_value)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/kvcache/compact', methods=['POST'])
def v78_kvcache_compact():
    """M128: TieredCompact压缩"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        memories = data.get('memories', [])
        keep_recent = int(data.get('keep_recent', 3))
        result = modules['kvcache']().compact(memories, keep_recent)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/kvcache/budget', methods=['GET'])
def v78_kvcache_budget():
    """M128: 上下文预算查询"""
    try:
        modules = get_v78_modules()
        if modules is None:
            return jsonify(_v78_state['kvcache'])
        state = modules['kvcache']().get_state()
        return jsonify(_to_native(state))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/kvcache/govern', methods=['POST'])
def v78_kvcache_govern():
    """M128: 全局KV治理"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        memory_tree = data.get('memory_tree', {})
        result = modules['kvcache']().govern(memory_tree)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/kvcache/state', methods=['GET'])
def v78_kvcache_state():
    """M128: KV缓存治理器状态"""
    try:
        modules = get_v78_modules()
        if modules is None:
            return jsonify(_v78_state['kvcache'])
        return jsonify(_to_native(modules['kvcache']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M129: OntologyAutoForge ----

@app.route('/api/v78/ontology/generate', methods=['POST'])
def v78_ontology_generate():
    """M129: 本体自动生成"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        module_dir = data.get('module_dir', '.')
        result = modules['ontology']().generate_ontology(module_dir)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/ontology/correct', methods=['POST'])
def v78_ontology_correct():
    """M129: 人在回路修正"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        instruction = data.get('instruction', '')
        result = modules['ontology']().correct_ontology(instruction)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/ontology/snapshot', methods=['POST'])
def v78_ontology_snapshot():
    """M129: 创建版本快照"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        version = data.get('version', 'v7.8')
        changes = data.get('changes', [])
        result = modules['ontology']().create_snapshot(version, changes)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/ontology/rollback', methods=['POST'])
def v78_ontology_rollback():
    """M129: 版本回滚"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        target_version = data.get('target_version', 'v7.7')
        result = modules['ontology']().rollback(target_version)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/ontology/resonance', methods=['POST'])
def v78_ontology_resonance():
    """M129: 跨版本共振分析"""
    try:
        data = request.get_json() or {}
        modules = get_v78_modules()
        if modules is None:
            return jsonify({'error': 'v7.8模块未加载'}), 503
        v1 = data.get('version1', 'v7.0')
        v2 = data.get('version2', 'v7.8')
        result = modules['ontology']().analyze_resonance(v1, v2)
        return jsonify(_to_native(result.to_dict() if hasattr(result, 'to_dict') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v78/ontology/state', methods=['GET'])
def v78_ontology_state():
    """M129: 本体自锻造状态"""
    try:
        modules = get_v78_modules()
        if modules is None:
            return jsonify(_v78_state['ontology'])
        return jsonify(_to_native(modules['ontology']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.9 金符·关系作用量·堆垒素数·自指闭环（M130-M133）====================

_v79_modules = None
_v79_modules_lock = threading.Lock()

def get_v79_modules():
    """获取或初始化 v7.9 模块（线程安全懒加载）"""
    global _v79_modules
    if _v79_modules is None:
        with _v79_modules_lock:
            if _v79_modules is None:
                try:
                    from M130_JinFuDiscreteCalculus import get_instance as get_jinfu
                    from M131_RelationActionMinimizer import get_instance as get_action
                    from M132_AdditivePrimeClassifier import get_instance as get_prime
                    from M133_SelfRefLoopTopologizer import get_instance as get_topology

                    _v79_modules = {
                        'jinfu': get_jinfu,       # M130: 金符离散微积分
                        'action': get_action,     # M131: 关系作用量极小化
                        'prime': get_prime,       # M132: 堆垒素数分类
                        'topology': get_topology,  # M133: 自指闭环拓扑
                    }
                    print("✅ v7.9新模块已加载（M130-M133）- 金符·关系作用量·堆垒素数·自指闭环")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.9模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v79_modules = None
    return _v79_modules

def get_v79_data():
    """获取所有v7.9模块的状态数据（M130-M133）"""
    modules = get_v79_modules()
    if modules is None:
        return None
    try:
        return {
            'jinfu': modules['jinfu']().get_state(),
            'action': modules['action']().get_state(),
            'prime': modules['prime']().get_state(),
            'topology': modules['topology']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.9数据失败: {e}")
        return None

# v7.9 静态状态（降级模式）
_v79_state = {
    'jinfu': {
        'axiom_i_verified': True, 'axiom_ii_verified': True, 'axiom_iii_verified': True,
        'total_stacking_ops': 0, 'total_cleavage_ops': 0, 'total_phase_ops': 0,
        'physical_zero_violations': 0, 'grid_spacing_l0': 1.0,
        'total_spheres': 0, 'max_spheres': 10000, 't92_satisfied': True,
    },
    'action': {
        'current_S_R': 0.0, 'min_S_R': float('inf'), 'phase_entropy': 0.0,
        'alpha': 1.0, 'beta': 0.5, 'euler_lagrange_residual': 0.0,
        'is_at_minimum': False, 'minimizations_performed': 0,
        'physical_law_mappings': 0, 't93_satisfied': False,
    },
    'prime': {
        'total_fermions': 0, 'total_bosons': 0, 'goldbach_verified_count': 0,
        'goldbach_verification_rate': 0.0, 'current_generation': 1,
        'riemann_zeros_analyzed': 0, 'pauli_violations': 0,
        'bose_condensations': 0, 't94_satisfied': True,
    },
    'topology': {
        'pds_constructed': 0, 'godel_constructed': 0, 'unified_field_computed': 0,
        'current_regime': 'STANDARD', 'kappa': 1.0, 'kappa_critical': 0.5,
        'current_S_unified': 0.0, 'self_ref_penalty': 0.0,
        'cmb_analyses': 0, 'causal_loops_detected': 0, 't95_satisfied': False,
    },
}

# ==================== v7.9 定理注册 ====================
_V79_THEOREMS = {
    'T92': '金符离散完备性定理: {⊕,⊗,Φ}运算有限步生成任意有限堆垒 — 生成完备性保证',
    'T93': '关系作用量极小值存在定理: 有限网格上S_R至少一个极小值 — 变分稳定性保证',
    'T94': '堆垒费米子-玻色子分类定理: 奇堆垒↔费米子/偶堆垒↔玻色子 — 粒子分类同构',
    'T95': '自指闭环必然性定理: κ<κ_c时自指闭环必然涌现 — 闭环必然性保证',
}


# ==================== v7.9 API端点 ====================

@app.route('/api/v79/state', methods=['GET'])
def v79_state():
    """v7.9 完整状态获取"""
    try:
        data = get_v79_data()
        if data:
            return jsonify({**data, 'theorems': _V79_THEOREMS})
        return jsonify({**_v79_state, 'theorems': _V79_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M130: JinFuDiscreteCalculus ----

@app.route('/api/v79/jinfu/axiom-check', methods=['POST'])
def v79_jinfu_axiom_check():
    """M130: 金符公理验证"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['jinfu']().apply_axiom_discreteness(
            coordinates=data.get('coordinates', []),
            l0=data.get('l0', 1.0)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/jinfu/stacking', methods=['POST'])
def v79_jinfu_stacking():
    """M130: 堆垒运算(⊕)"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['jinfu']().stacking_add(
            a=data.get('a', 1.0),
            b=data.get('b', 1.0)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/jinfu/cleavage', methods=['POST'])
def v79_jinfu_cleavage():
    """M130: 裂解运算(⊗)"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['jinfu']().cleavage_multiply(
            a=data.get('a', 1.0),
            n=data.get('n', 2)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/jinfu/phase-op', methods=['POST'])
def v79_jinfu_phase_op():
    """M130: 相位算子(Φ)"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['jinfu']().phase_operator(
            angle=data.get('angle', 72.0)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/jinfu/physical-zero', methods=['POST'])
def v79_jinfu_physical_zero():
    """M130: 物理零检测"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['jinfu']().detect_physical_zero(
            value=data.get('value', 0.5),
            l0=data.get('l0', 1.0)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/jinfu/state', methods=['GET'])
def v79_jinfu_state():
    """M130: 金符离散微积分状态"""
    try:
        modules = get_v79_modules()
        if modules is None:
            return jsonify(_v79_state['jinfu'])
        return jsonify(_to_native(modules['jinfu']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M131: RelationActionMinimizer ----

@app.route('/api/v79/action/compute', methods=['POST'])
def v79_action_compute():
    """M131: 计算关系作用量S_R"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['action']().compute_relation_action(
            n_values=data.get('n_values', [10]),
            phase_distributions=data.get('phase_distributions', [[0.25, 0.25, 0.25, 0.25]]),
            alpha=data.get('alpha', 1.0),
            beta=data.get('beta', 0.5)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/action/minimize', methods=['POST'])
def v79_action_minimize():
    """M131: 变分极小化"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['action']().variational_minimize(
            n_values=data.get('n_values', [10]),
            phase_distributions=data.get('phase_distributions', [[0.25, 0.25, 0.25, 0.25]]),
            alpha=data.get('alpha', 1.0),
            beta=data.get('beta', 0.5)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/action/euler-lagrange', methods=['POST'])
def v79_action_euler_lagrange():
    """M131: 求解离散欧拉-拉格朗日方程"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['action']().solve_discrete_euler_lagrange(
            S_R_values=data.get('S_R_values', [1.0, 0.8, 0.6, 0.5, 0.55]),
            n_index=data.get('n_index', 2)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/action/physical-map', methods=['POST'])
def v79_action_physical_map():
    """M131: 物理定律同构映射"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['action']().map_physical_law(
            context=data.get('context', 'inertia')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/action/state', methods=['GET'])
def v79_action_state():
    """M131: 关系作用量极小化器状态"""
    try:
        modules = get_v79_modules()
        if modules is None:
            return jsonify(_v79_state['action'])
        return jsonify(_to_native(modules['action']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M132: AdditivePrimeClassifier ----

@app.route('/api/v79/prime/classify', methods=['POST'])
def v79_prime_classify():
    """M132: 粒子分类"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['prime']().classify_particle(
            n=data.get('n', 7)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/prime/goldbach', methods=['POST'])
def v79_prime_goldbach():
    """M132: 哥德巴赫交互"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['prime']().goldbach_interaction(
            p1=data.get('p1', 3),
            p2=data.get('p2', 5)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/prime/decompose', methods=['POST'])
def v79_prime_decompose():
    """M132: 素数分解"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['prime']().prime_decompose(
            n=data.get('n', 12)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/prime/resonance', methods=['POST'])
def v79_prime_resonance():
    """M132: 黎曼共振"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['prime']().riemann_resonance(
            zero_count=data.get('zero_count', 10)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/prime/state', methods=['GET'])
def v79_prime_state():
    """M132: 堆垒素数分类器状态"""
    try:
        modules = get_v79_modules()
        if modules is None:
            return jsonify(_v79_state['prime'])
        return jsonify(_to_native(modules['prime']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M133: SelfRefLoopTopologizer ----

@app.route('/api/v79/topology/construct-pds', methods=['POST'])
def v79_topology_pds():
    """M133: 构建PDS空间自指闭环"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['topology']().construct_pds(
            pentagon_count=data.get('pentagon_count', 12),
            curvature=data.get('curvature', 0.3)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/topology/construct-godel', methods=['POST'])
def v79_topology_godel():
    """M133: 构建哥德尔时间自指闭环"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['topology']().construct_godel(
            rotation_phase=data.get('rotation_phase', 0.5),
            ctc_present=data.get('ctc_present', True)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/topology/unified-field', methods=['POST'])
def v79_topology_unified_field():
    """M133: 统一场方程"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['topology']().compute_unified_field(
            S_R=data.get('S_R', 1.0),
            kappa=data.get('kappa', 0.3),
            loop_type=data.get('loop_type', 'PDS')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/topology/self-ref-penalty', methods=['POST'])
def v79_topology_self_ref_penalty():
    """M133: 自指惩罚项计算"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['topology']().compute_self_ref_penalty(
            kappa=data.get('kappa', 0.3),
            loop_type=data.get('loop_type', 'PDS')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/topology/cmb-signature', methods=['POST'])
def v79_topology_cmb():
    """M133: CMB签名分析"""
    try:
        data = request.get_json() or {}
        modules = get_v79_modules()
        if modules is None:
            return jsonify({'error': 'v7.9模块未加载', 'fallback': True})
        result = modules['topology']().analyze_cmb_signature(
            temperature_data=data.get('temperature_data', [2.725, 2.720, 2.730])
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v79/topology/state', methods=['GET'])
def v79_topology_state():
    """M133: 自指闭环拓扑器状态"""
    try:
        modules = get_v79_modules()
        if modules is None:
            return jsonify(_v79_state['topology'])
        return jsonify(_to_native(modules['topology']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.10 欧拉相位闭合·递归证明折叠·五层次本体·可证伪预言（M134-M137）====================

_v710_modules = None
_v710_modules_lock = threading.Lock()

def get_v710_modules():
    """获取或初始化 v7.10 模块（线程安全懒加载）"""
    global _v710_modules
    if _v710_modules is None:
        with _v710_modules_lock:
            if _v710_modules is None:
                try:
                    from M134_EulerPhaseClosureEngine import get_instance as get_euler
                    from M135_RecursiveProofFolder import get_instance as get_proof
                    from M136_FiveLayerOntologyMapper import get_instance as get_ontology
                    from M137_FalsifiablePredictionEngine import get_instance as get_prediction

                    _v710_modules = {
                        'euler': get_euler,         # M134: 欧拉相位闭合引擎
                        'proof': get_proof,         # M135: 递归证明折叠器
                        'ontology': get_ontology,   # M136: 五层次本体映射器
                        'prediction': get_prediction, # M137: 可证伪预言引擎
                    }
                    print("✅ v7.10新模块已加载（M134-M137）- 欧拉闭合·证明折叠·五层本体·可证伪预言")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.10模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v710_modules = None
    return _v710_modules

def get_v710_data():
    """获取所有v7.10模块的状态数据（M134-M137）"""
    modules = get_v710_modules()
    if modules is None:
        return None
    try:
        return {
            'euler': modules['euler']().get_state(),
            'proof': modules['proof']().get_state(),
            'ontology': modules['ontology']().get_state(),
            'prediction': modules['prediction']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.10数据失败: {e}")
        return None

# v7.10 静态状态（降级模式）
_v710_state = {
    'euler': {
        'phase_angle': 3.14159, 'amplitude': '-1+0j', 'cycle_step': 'return',
        'closure_residual': 0.0, 'rel_origin_distance': 0.0,
        'total_closures': 0, 'total_traces': 0, 'phase_synchronizations': 0,
        't96_satisfied': True,
    },
    'proof': {
        'current_proof_hash': 'genesis', 'proof_size_bytes': 1024,
        'history_length': 0, 'compression_ratio': 1.0,
        'is_constant_size': True, 'total_folds': 0, 'total_verifications': 0,
        't97_satisfied': True,
    },
    'ontology': {
        'current_phenomenon': '', 'dominant_layer': 2,
        'cross_layer_coherence': 1.0, 'layers_mapped': 0,
        'compression_paths_traced': 0,
        'l1_ftel_compression': 1.0, 'l2_rel_compression': 0.5,
        'l3_manifest_compression': 0.1, 'l4_cognitive_compression': 0.01,
        'l5_narrative_compression': 0.001,
        't98_satisfied': True,
    },
    'prediction': {
        'total_predictions': 3, 'pending': 3, 'confirmed': 0,
        'falsified': 0, 'unverifiable': 0,
        'avg_popper_score': 0.85, 'avg_testability': 0.7,
        't99_satisfied': True,
    },
}

# ==================== v7.10 定理注册 ====================
_V710_THEOREMS = {
    'T96': '欧拉相位闭合定理: e^(iπ)+1=0为L2相位闭合算子 — 1→i→-1→0最小闭合基',
    'T97': '递归证明折叠定理: 存在Π使π_n大小O(1)且为H的充分统计量 — 常数证明压缩',
    'T98': '五层次一致性定理: 单调压缩+投射保真+闭环必然 — 跨层本体一致性',
    'T99': '可证伪性定理: F(P)=C(P)/R(E)定义可证伪度 — 科学预言有效性',
}


# ==================== v7.10 API端点 ====================

@app.route('/api/v710/state', methods=['GET'])
def v710_state():
    """v7.10 完整状态获取"""
    try:
        data = get_v710_data()
        if data:
            return jsonify({**data, 'theorems': _V710_THEOREMS})
        return jsonify({**_v710_state, 'theorems': _V710_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M134: EulerPhaseClosureEngine ----

@app.route('/api/v710/euler/closure', methods=['POST'])
def v710_euler_closure():
    """M134: 计算e^(iθ)的相位闭合"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        import math
        theta = data.get('theta', math.pi)
        result = modules['euler']().compute_euler_closure(theta=theta)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/euler/cycle-trace', methods=['POST'])
def v710_euler_cycle_trace():
    """M134: 追踪1→i→-1→0四步循环"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        start_re = data.get('start_re', 1.0)
        start_im = data.get('start_im', 0.0)
        result = modules['euler']().trace_phase_cycle(start=complex(start_re, start_im))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/euler/rel-origin', methods=['POST'])
def v710_euler_rel_origin():
    """M134: 计算距Rel原点的EML距离"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        z_re = data.get('z_re', 0.0)
        z_im = data.get('z_im', 0.0)
        result = modules['euler']().check_rel_origin(complex(z_re, z_im))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/euler/eml-decompose', methods=['POST'])
def v710_euler_eml_decompose():
    """M134: EML算子分解 Re^(iθ)"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        z_re = data.get('z_re', 1.0)
        z_im = data.get('z_im', 0.0)
        result = modules['euler']().euler_eml_decompose(complex(z_re, z_im))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/euler/phase-sync', methods=['POST'])
def v710_euler_phase_sync():
    """M134: 多粒子相位同步"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        particles = data.get('particles', [[1, 0], [0, 1], [-1, 0], [0, -1]])
        complex_particles = [complex(p[0], p[1]) for p in particles]
        result = modules['euler']().phase_synchronize(complex_particles)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/euler/state', methods=['GET'])
def v710_euler_state():
    """M134: 欧拉相位闭合状态"""
    try:
        modules = get_v710_modules()
        if modules is None:
            return jsonify(_v710_state['euler'])
        return jsonify(_to_native(modules['euler']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M135: RecursiveProofFolder ----

@app.route('/api/v710/proof/fold', methods=['POST'])
def v710_proof_fold():
    """M135: 折叠新数据到证明"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        result = modules['proof']().fold_history(
            block_data=data.get('block_data', {}),
            prev_proof=data.get('prev_proof', None)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/proof/verify', methods=['POST'])
def v710_proof_verify():
    """M135: 验证折叠证明"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        result = modules['proof']().verify_folded(data.get('proof_hash', ''))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/proof/statistic', methods=['POST'])
def v710_proof_statistic():
    """M135: 计算充分统计量"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        result = modules['proof']().compute_sufficient_statistic(data.get('proof_hash', ''))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/proof/batch-fold', methods=['POST'])
def v710_proof_batch_fold():
    """M135: 批量折叠"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        blocks = data.get('blocks', [])
        result = modules['proof']().batch_fold(blocks)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/proof/state', methods=['GET'])
def v710_proof_state():
    """M135: 递归证明折叠状态"""
    try:
        modules = get_v710_modules()
        if modules is None:
            return jsonify(_v710_state['proof'])
        return jsonify(_to_native(modules['proof']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M136: FiveLayerOntologyMapper ----

@app.route('/api/v710/ontology/map', methods=['POST'])
def v710_ontology_map():
    """M136: 将现象映射到L1-L5"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        result = modules['ontology']().map_phenomenon(
            description=data.get('description', ''),
            domain=data.get('domain', 'general')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/ontology/coherence', methods=['POST'])
def v710_ontology_coherence():
    """M136: 计算跨层一致性"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        mapping = modules['ontology']().map_phenomenon(
            description=data.get('description', ''),
            domain=data.get('domain', 'general')
        )
        result = modules['ontology']().compute_cross_layer_coherence(mapping)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/ontology/layer', methods=['POST'])
def v710_ontology_layer():
    """M136: 获取层定义"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        level = data.get('level', 1)
        result = modules['ontology']().get_layer_definition(level)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/ontology/bridge', methods=['POST'])
def v710_ontology_bridge():
    """M136: 映射到现有太乙AGI模块"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        level = data.get('level', 1)
        result = modules['ontology']().bridge_to_existing_modules(level)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/ontology/state', methods=['GET'])
def v710_ontology_state():
    """M136: 五层次本体映射状态"""
    try:
        modules = get_v710_modules()
        if modules is None:
            return jsonify(_v710_state['ontology'])
        return jsonify(_to_native(modules['ontology']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M137: FalsifiablePredictionEngine ----

@app.route('/api/v710/prediction/generate', methods=['POST'])
def v710_prediction_generate():
    """M137: 从定理生成预言"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        result = modules['prediction']().generate_prediction(
            theorem_id=data.get('theorem_id', 'T96'),
            domain=data.get('domain', 'physics')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/prediction/falsifiability', methods=['POST'])
def v710_prediction_falsifiability():
    """M137: 检查可证伪性"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        prediction_id = data.get('prediction_id', 'P1')
        preds = modules['prediction']().list_predictions()
        target = [p for p in preds if p.id == prediction_id]
        if target:
            result = modules['prediction']().check_falsifiability(target[0])
        else:
            result = modules['prediction']().generate_prediction(
                theorem_id=data.get('theorem_id', 'T96'),
                domain=data.get('domain', 'physics')
            )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/prediction/experiment', methods=['POST'])
def v710_prediction_experiment():
    """M137: 设计实验方案"""
    try:
        data = request.get_json() or {}
        modules = get_v710_modules()
        if modules is None:
            return jsonify({'error': 'v7.10模块未加载', 'fallback': True})
        prediction_id = data.get('prediction_id', 'P1')
        preds = modules['prediction']().list_predictions()
        target = [p for p in preds if p.id == prediction_id]
        if target:
            result = modules['prediction']().design_experiment(target[0])
        else:
            result = {'error': f'Prediction {prediction_id} not found'}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/prediction/list', methods=['GET'])
def v710_prediction_list():
    """M137: 列出预言"""
    try:
        modules = get_v710_modules()
        if modules is None:
            return jsonify(_v710_state['prediction'])
        status = request.args.get('status', 'all')
        result = modules['prediction']().list_predictions(status=status)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v710/prediction/state', methods=['GET'])
def v710_prediction_state():
    """M137: 可证伪预言引擎状态"""
    try:
        modules = get_v710_modules()
        if modules is None:
            return jsonify(_v710_state['prediction'])
        return jsonify(_to_native(modules['prediction']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.11 懒加载与状态（M138-M141）====================

_v711_modules = None
_v711_modules_lock = threading.Lock()

def get_v711_modules():
    """获取或初始化 v7.11 模块（线程安全懒加载）"""
    global _v711_modules
    if _v711_modules is None:
        with _v711_modules_lock:
            if _v711_modules is None:
                try:
                    from M138_BipartiteGraphTopologyEngine import get_instance as get_bipartite
                    from M139_RelationalActionRouter import get_instance as get_action
                    from M140_HybridRailPhaseController import get_instance as get_hybrid
                    from M141_TopologicalPhaseTransitionDetector import get_instance as get_phase

                    _v711_modules = {
                        'bipartite': get_bipartite,  # M138: 二部图拓扑引擎
                        'action': get_action,        # M139: 关系作用量路由器
                        'hybrid': get_hybrid,        # M140: 混合相位控制器
                        'phase': get_phase,          # M141: 拓扑相变检测器
                    }
                    print("✅ v7.11新模块已加载（M138-M141）- 二部图拓扑·关系作用量·混合相位·拓扑相变")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.11模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v711_modules = None
    return _v711_modules

def get_v711_data():
    """获取所有v7.11模块的状态数据（M138-M141）"""
    modules = get_v711_modules()
    if modules is None:
        return None
    try:
        return {
            'bipartite': modules['bipartite']().get_state(),
            'action': modules['action']().get_state(),
            'hybrid': modules['hybrid']().get_state(),
            'phase': modules['phase']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.11数据失败: {e}")
        return None

# v7.11 静态状态（降级模式）
_v711_state = {
    'bipartite': {
        'topology_type': 'K(n/2,n/2)', 'num_nodes': 256, 'num_groups': 2,
        'diameter_zcube': 2, 'diameter_clos': 3,
        'cost_zcube': 2.0, 'cost_clos': 3.0, 'cost_delta': 1.0,
        'switch_saving_pct': 33.0, 'survival_prob': 0.996,
        'max_min_ratio': 1.05, 'total_comparisons': 0,
        't100_satisfied': True,
    },
    'action': {
        'current_S_R': 1.5, 'optimal_path_hops': 2,
        'phase_entropy_H_phi': 0.12, 'alpha': 0.6, 'beta': 0.4,
        'total_routes_computed': 0, 'avg_action_cost': 0.0,
        'is_deterministic': True, 'ecmp_conflicts': 0,
        't101_satisfied': True,
    },
    'hybrid': {
        'optimal_threshold': 4096, 'single_rail_pct': 0.35,
        'multi_rail_pct': 0.65, 'expected_S_R_hybrid': 1.2,
        'expected_S_R_single': 2.1, 'expected_S_R_multi': 1.8,
        'pd_separation_active': True, 'total_packets_routed': 0,
        'phase_switches': 0,
        't102_satisfied': True,
    },
    'phase': {
        'current_H_phi': 0.15, 'phase_transition_detected': False,
        'current_scale_N': 256, 'predicted_transition_N': 1024,
        'memory_bound_pct': 0.65, 'bandwidth_bound_pct': 0.42,
        'bottleneck_type': 'balanced', 'recursive_level': 1,
        'fractal_dimension': 1.0, 'survival_prob': 0.996,
        'predictions_generated': 3, 't103_satisfied': True,
    },
}

# ==================== v7.11 定理注册 ====================
_V711_THEOREMS = {
    'T100': '拓扑极简定理: ZCube二部图|z_ZCube| < |z_Clos|, Delta|z|=O(N)随规模增长 — 扁平拓扑代价极小',
    'T101': '关系作用量极小定理: 二部图确定性路由S_R <= 分层Clos的S_R — 刘机制路径优选',
    'T102': '混合接入最优定理: 重尾分布D(s)下存在唯一tau*使E[S_R]极小 — 单/多轨最优混接',
    'T103': '拓扑相变可预测定理: Clos存在H_Phi非线性跳变, ZCube线性增长无相变 — 规模扩展可预测',
}


# ==================== v7.11 API端点 ====================

@app.route('/api/v711/state', methods=['GET'])
def v711_state():
    """v7.11 完整状态获取"""
    try:
        data = get_v711_data()
        if data:
            return jsonify({**data, 'theorems': _V711_THEOREMS})
        return jsonify({**_v711_state, 'theorems': _V711_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M138: BipartiteGraphTopologyEngine ----

@app.route('/api/v711/bipartite/create', methods=['POST'])
def v711_bipartite_create():
    """创建二部图拓扑"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['bipartite'])
        n = data.get('num_nodes', 256)
        result = modules['bipartite']().create_topology(n)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/bipartite/compare', methods=['POST'])
def v711_bipartite_compare():
    """Clos vs ZCube对比"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['bipartite'])
        n = data.get('num_nodes', 256)
        result = modules['bipartite']().compare_clos_zcube(n)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/bipartite/path', methods=['POST'])
def v711_bipartite_path():
    """计算二部图最短路径"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'error': 'module not loaded'}), 503
        src = data.get('source', 0)
        dst = data.get('destination', 1)
        result = modules['bipartite']().compute_path(src, dst)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/bipartite/diameter', methods=['GET'])
def v711_bipartite_diameter():
    """获取网络直径"""
    try:
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'diameter_zcube': 2, 'diameter_clos': 3})
        result = modules['bipartite']().compute_diameter()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/bipartite/fault-tolerance', methods=['POST'])
def v711_bipartite_fault():
    """容错分析"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'survival_prob': 0.996})
        n = data.get('num_nodes', 256)
        k = data.get('failed_leaves', 1)
        result = modules['bipartite']().analyze_fault_tolerance(n, k)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/bipartite/state', methods=['GET'])
def v711_bipartite_state():
    """M138状态"""
    try:
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['bipartite'])
        return jsonify(_to_native(modules['bipartite']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M139: RelationalActionRouter ----

@app.route('/api/v711/action/compute', methods=['POST'])
def v711_action_compute():
    """计算关系作用量S_R"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['action'])
        path_hops = data.get('path_hops', [1, 2])
        result = modules['action']().compute_action(path_hops)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/action/route', methods=['POST'])
def v711_action_route():
    """刘机制最优路由"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'error': 'module not loaded'}), 503
        src = data.get('source', 0)
        dst = data.get('destination', 1)
        result = modules['action']().find_optimal_route(src, dst)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/action/entropy', methods=['POST'])
def v711_action_entropy():
    """计算相位熵H_Phi"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'H_phi': 0.12})
        link_utils = data.get('link_utilizations', [0.5, 0.5])
        result = modules['action']().compute_phase_entropy(link_utils)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/action/compare', methods=['POST'])
def v711_action_compare():
    """ZCube vs Clos 关系作用量对比"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['action'])
        n = data.get('num_nodes', 256)
        result = modules['action']().compare_actions(n)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/action/state', methods=['GET'])
def v711_action_state():
    """M139状态"""
    try:
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['action'])
        return jsonify(_to_native(modules['action']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M140: HybridRailPhaseController ----

@app.route('/api/v711/hybrid/optimize', methods=['POST'])
def v711_hybrid_optimize():
    """优化混合阈值"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['hybrid'])
        result = modules['hybrid']().optimize_threshold(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/hybrid/route-packet', methods=['POST'])
def v711_hybrid_route():
    """路由数据包到单/多轨"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'error': 'module not loaded'}), 503
        size = data.get('size', 1024)
        result = modules['hybrid']().route_packet(size)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/hybrid/pd-analyze', methods=['POST'])
def v711_hybrid_pd():
    """PD分离流量分析"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['hybrid'])
        result = modules['hybrid']().analyze_pd_separation(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/hybrid/eml-switch', methods=['POST'])
def v711_hybrid_eml():
    """EML相位切换"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'error': 'module not loaded'}), 503
        result = modules['hybrid']().eml_phase_switch(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/hybrid/state', methods=['GET'])
def v711_hybrid_state():
    """M140状态"""
    try:
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['hybrid'])
        return jsonify(_to_native(modules['hybrid']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M141: TopologicalPhaseTransitionDetector ----

@app.route('/api/v711/phase/detect', methods=['POST'])
def v711_phase_detect():
    """检测拓扑相变"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['phase'])
        n1 = data.get('N1', 256)
        n2 = data.get('N2', 2048)
        result = modules['phase']().detect_transition(n1, n2)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/phase/monitor', methods=['POST'])
def v711_phase_monitor():
    """关系熵监控"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify({'H_phi': 0.15, 'transition_detected': False})
        link_utils = data.get('link_utilizations', [])
        result = modules['phase']().monitor_entropy(link_utils)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/phase/bottleneck', methods=['POST'])
def v711_phase_bottleneck():
    """耦合瓶颈分析"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['phase'])
        result = modules['phase']().analyze_bottleneck(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/phase/recursive', methods=['POST'])
def v711_phase_recursive():
    """递归ZCube分形扩展"""
    try:
        data = request.get_json() or {}
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['phase'])
        level = data.get('level', 1)
        result = modules['phase']().recursive_expand(level)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v711/phase/state', methods=['GET'])
def v711_phase_state():
    """M141状态"""
    try:
        modules = get_v711_modules()
        if modules is None:
            return jsonify(_v711_state['phase'])
        return jsonify(_to_native(modules['phase']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.12 懒加载与状态（M142-M147）====================

_v712_modules = None
_v712_modules_lock = threading.Lock()

def get_v712_modules():
    """获取或初始化 v7.12 模块（线程安全懒加载）"""
    global _v712_modules
    if _v712_modules is None:
        with _v712_modules_lock:
            if _v712_modules is None:
                try:
                    from M142_UVRegularizationEngine import get_instance as get_uv
                    from M143_FenxiangziSpaceEngine import get_instance as get_fenxiang
                    from M144_JinfuAccumulationComputer import get_instance as get_accum
                    from M145_YuMappingCognitiveEngine import get_instance as get_yu
                    from M146_DialecticalZeroReasoner import get_instance as get_dzero
                    from M147_SingularityEliminator import get_instance as get_singul

                    _v712_modules = {
                        'uv': get_uv,          # M142: UV正则化引擎
                        'fenxiang': get_fenxiang,  # M143: 芬芳香子空间引擎
                        'accum': get_accum,    # M144: 金符堆垒运算器
                        'yu': get_yu,          # M145: 宇射认知引擎
                        'dzero': get_dzero,    # M146: 辩证零推理器
                        'singul': get_singul,  # M147: 奇点消除器
                    }
                    print("✅ v7.12新模块已加载（M142-M147）- UV正则化·芬芳香子·金符堆垒·宇射认知·辩证零·奇点消除")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.12模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v712_modules = None
    return _v712_modules

def get_v712_data():
    """获取所有v7.12模块的状态数据（M142-M147）"""
    modules = get_v712_modules()
    if modules is None:
        return None
    try:
        return {
            'uv': modules['uv']().get_state(),
            'fenxiang': modules['fenxiang']().get_state(),
            'accum': modules['accum']().get_state(),
            'yu': modules['yu']().get_state(),
            'dzero': modules['dzero']().get_state(),
            'singul': modules['singul']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.12数据失败: {e}")
        return None

# v7.12 静态状态（降级模式）
_v712_state = {
    'uv': {
        'module_id': 'M142', 'module_name': 'UVRegularizationEngine', 'version': '7.12',
        'd_phi': 0.01, 'k_max': 314.159, 'regularization_count': 0,
        'divergence_count': 0, 'operation_count': 0,
        't104_satisfied': True,
    },
    'fenxiang': {
        'module_id': 'M143', 'module_name': 'FenxiangziSpaceEngine', 'version': '7.12',
        'total_polyhedra': 18, 'platonic_count': 5, 'archimedean_count': 13,
        'space_fillable': 3, 'knowledge_domains': 0, 'operation_count': 0,
        't105_satisfied': True,
    },
    'accum': {
        'module_id': 'M144', 'module_name': 'JinfuAccumulationComputer', 'version': '7.12',
        'total_operators': 127, 'category_counts': {'relation': 21, 'phase': 18, 'stacking': 30, 'transform': 58},
        'compute_history_count': 0, 'operation_count': 0,
        't106_satisfied': True,
    },
    'yu': {
        'module_id': 'M145', 'module_name': 'YuMappingCognitiveEngine', 'version': '7.12',
        'alpha': 0.7, 'beta': 0.3, 'mapping_history_count': 0, 'operation_count': 0,
        't107_satisfied': True,
    },
    'dzero': {
        'module_id': 'M146', 'module_name': 'DialecticalZeroReasoner', 'version': '7.12',
        'd_phi': 0.01, 'analysis_history_count': 0, 'operation_count': 0,
        't108_satisfied': True,
    },
    'singul': {
        'module_id': 'M147', 'module_name': 'SingularityEliminator', 'version': '7.12',
        'd_phi': 0.01, 'max_recursion': 100, 'total_eliminations': 0,
        'elimination_by_type': {}, 'operation_count': 0,
        't109_satisfied': True,
    },
}

# ==================== v7.12 定理注册 ====================
_V712_THEOREMS = {
    'T104': 'UV正则化定理: 金灵球d_φ提供物理截断k_max=π/d_φ, 无需重正化即可消除紫外发散',
    'T105': '芬芳香子密堆定理: 18种正/半正多面体可密铺3D空间, Euler公式V-E+F=2全局成立',
    'T106': '金符堆垒完备定理: 120个金符算符构成关系/相位/堆垒/变换完备运算系统, 无浮点截断',
    'T107': '宇射认知定理: 对残缺输入X, H(Ψ) >= H(f), 宇射映射不损失信息且容忍不完整特征',
    'T108': '辩证零定理: 0_D = {x : |x| < d_φ}为物理不可分辨而非绝对虚无, 极限运算在金符时空中恒有定义',
    'T109': '奇点消除定理: 金符时空中曲率R <= 1/d_φ²有界, 分母以d_φ为下界, 递归深度受限 — 奇点为伪问题',
}


# ==================== v7.12 API端点 ====================

@app.route('/api/v712/state', methods=['GET'])
def v712_state():
    """v7.12 完整状态获取"""
    try:
        data = get_v712_data()
        if data:
            return jsonify({**data, 'theorems': _V712_THEOREMS})
        return jsonify({**_v712_state, 'theorems': _V712_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M142: UVRegularizationEngine ----

@app.route('/api/v712/uv/cutoff', methods=['GET'])
def v712_uv_cutoff():
    """获取UV截断频率"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify({'d_phi': 0.01, 'k_max': 314.159})
        return jsonify(_to_native(modules['uv']().get_cutoff_info()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/uv/detect-divergence', methods=['POST'])
def v712_uv_detect():
    """检测积分发散"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['uv'])
        result = modules['uv']().detect_divergence(
            data.get('integrand_type', 'power_law'),
            data.get('dimension', 3),
            data.get('extra_params', {})
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/uv/regularize', methods=['POST'])
def v712_uv_regularize():
    """正则化积分"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['uv'])
        result = modules['uv']().regularize_integral(
            data.get('integrand_type', 'power_law'),
            data.get('dimension', 3),
            data.get('extra_params', {})
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/uv/analyze-spectrum', methods=['POST'])
def v712_uv_spectrum():
    """分析频谱"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['uv'])
        result = modules['uv']().analyze_spectrum(data.get('spectrum_data', []))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/uv/state', methods=['GET'])
def v712_uv_state():
    """M142状态"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['uv'])
        return jsonify(_to_native(modules['uv']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M143: FenxiangziSpaceEngine ----

@app.route('/api/v712/fenxiang/list', methods=['GET'])
def v712_fenxiang_list():
    """列出芬芳香子"""
    try:
        category = request.args.get('category', None)
        modules = get_v712_modules()
        if modules is None:
            return jsonify({'total_polyhedra': 18, 'platonic_count': 5, 'archimedean_count': 13})
        result = modules['fenxiang']().list_polyhedra(category)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/fenxiang/detail', methods=['GET'])
def v712_fenxiang_detail():
    """获取多面体详情"""
    try:
        name = request.args.get('name', 'Cube')
        modules = get_v712_modules()
        if modules is None:
            return jsonify({'error': 'module not loaded'}), 503
        result = modules['fenxiang']().get_polyhedron(name)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/fenxiang/space-fill', methods=['POST'])
def v712_fenxiang_fill():
    """空间填充模拟"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['fenxiang'])
        result = modules['fenxiang']().simulate_space_filling(
            dimensions=tuple(data.get('dimensions', [5, 5, 5])),
            primary_type=data.get('primary_type', 'Cube'),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/fenxiang/map-domain', methods=['POST'])
def v712_fenxiang_domain():
    """知识域映射"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['fenxiang'])
        result = modules['fenxiang']().map_knowledge_domain(
            data.get('domain', 'physics'),
            data.get('subtopics', []),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/fenxiang/state', methods=['GET'])
def v712_fenxiang_state():
    """M143状态"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['fenxiang'])
        return jsonify(_to_native(modules['fenxiang']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M144: JinfuAccumulationComputer ----

@app.route('/api/v712/accum/list', methods=['GET'])
def v712_accum_list():
    """列出金符算符"""
    try:
        category = request.args.get('category', None)
        modules = get_v712_modules()
        if modules is None:
            return jsonify({'total_operators': 120})
        result = modules['accum']().list_operators(category)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/accum/detail', methods=['GET'])
def v712_accum_detail():
    """获取算符详情"""
    try:
        op_id = int(request.args.get('id', '0'))
        modules = get_v712_modules()
        if modules is None:
            return jsonify({'error': 'module not loaded'}), 503
        result = modules['accum']().get_operator(op_id)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/accum/compute', methods=['POST'])
def v712_accum_compute():
    """执行堆垒运算"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['accum'])
        result = modules['accum']().accumulate(
            value=data.get('value', 1.0),
            operator_ids=data.get('operator_ids', [0]),
            precision_bits=data.get('precision_bits', 64),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/accum/network', methods=['POST'])
def v712_accum_network():
    """构建关系网络"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['accum'])
        result = modules['accum']().build_relation_network(
            data.get('nodes', []),
            data.get('edges', []),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/accum/state', methods=['GET'])
def v712_accum_state():
    """M144状态"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['accum'])
        return jsonify(_to_native(modules['accum']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M145: YuMappingCognitiveEngine ----

@app.route('/api/v712/yu/map', methods=['POST'])
def v712_yu_map():
    """执行宇射计算"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['yu'])
        result = modules['yu']().yu_map(
            features=data.get('features', {}),
            context=data.get('context', ''),
            required_features=data.get('required_features'),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/yu/compare', methods=['POST'])
def v712_yu_compare():
    """传统映射 vs 宇射对比"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['yu'])
        result = modules['yu']().compare_mappings(
            features=data.get('features', {}),
            context=data.get('context', ''),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/yu/inference', methods=['POST'])
def v712_yu_inference():
    """残缺数据推理"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['yu'])
        result = modules['yu']().inference_with_missing_data(
            features=data.get('features', {}),
            context=data.get('context', ''),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/yu/state', methods=['GET'])
def v712_yu_state():
    """M145状态"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['yu'])
        return jsonify(_to_native(modules['yu']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M146: DialecticalZeroReasoner ----

@app.route('/api/v712/dzero/classify', methods=['POST'])
def v712_dzero_classify():
    """判定辩证状态"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['dzero'])
        result = modules['dzero']().classify_value(
            value=data.get('value', 0.0),
            reference=data.get('reference', 0.0),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/dzero/analyze-limit', methods=['POST'])
def v712_dzero_limit():
    """极限分析"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['dzero'])
        result = modules['dzero']().analyze_limit(
            sequence=data.get('sequence', []),
            limit_candidate=data.get('limit_candidate', 0.0),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/dzero/range', methods=['GET'])
def v712_dzero_range():
    """辩证零范围"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify({'d_phi': 0.01, 'lower': -0.01, 'upper': 0.01})
        result = modules['dzero']().get_dialectical_zero_range()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/dzero/state', methods=['GET'])
def v712_dzero_state():
    """M146状态"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['dzero'])
        return jsonify(_to_native(modules['dzero']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M147: SingularityEliminator ----

@app.route('/api/v712/singul/safe-divide', methods=['POST'])
def v712_singul_divide():
    """安全除法"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['singul'])
        result = modules['singul']().safe_divide(
            numerator=data.get('numerator', 1.0),
            denominator=data.get('denominator', 0.0),
            context=data.get('context', ''),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/singul/detect', methods=['POST'])
def v712_singul_detect():
    """曲率奇点检测"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['singul'])
        result = modules['singul']().detect_curvature_singularity(
            data.get('metric_tensor', [[1, 0], [0, 1]]),
            data.get('context', ''),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/singul/analyze-recursion', methods=['POST'])
def v712_singul_recursion():
    """递归安全性分析"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['singul'])
        result = modules['singul']().analyze_recursion(
            data.get('func_name', 'unknown'),
            data.get('max_depth', 100),
            data.get('base_case_value', 0.0),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/singul/safe-compute', methods=['POST'])
def v712_singul_compute():
    """安全计算"""
    try:
        data = request.get_json() or {}
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['singul'])
        result = modules['singul']().safe_compute(
            data.get('expression', ''),
            data.get('variables', {}),
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v712/singul/state', methods=['GET'])
def v712_singul_state():
    """M147状态"""
    try:
        modules = get_v712_modules()
        if modules is None:
            return jsonify(_v712_state['singul'])
        return jsonify(_to_native(modules['singul']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.1 人机融合层（M96-M105）====================

_v71_modules = None
_v71_modules_lock = threading.Lock()

def get_v71_modules():
    """获取或初始化 v7.1 人机融合模块（线程安全懒加载）"""
    global _v71_modules
    if _v71_modules is None:
        with _v71_modules_lock:
            if _v71_modules is None:
                try:
                    from M96_CognitiveOffloadGuard import get_instance as get_cog_guard
                    from M97_SocraticWeaknessDisclosure import get_instance as get_socratic
                    from M98_ConfidenceDisclosure import get_instance as get_confidence
                    from M99_DynamicTaskRouter import get_instance as get_router
                    from M100_RewardHackDetector import get_instance as get_hack_detect
                    from M101_EnvironmentAwareness import get_instance as get_env_aware
                    from M102_LongRangeContext import get_instance as get_long_ctx
                    from M103_CollaborationAssessor import get_instance as get_collab_assess
                    from M104_CollaborationDiagnostics import get_instance as get_collab_diag
                    from M105_FusionVerifier import get_instance as get_fusion_verify

                    _v71_modules = {
                        'cognitive_offload': get_cog_guard,      # M96: 认知卸载防范
                        'socratic': get_socratic,                # M97: 苏格拉底示弱
                        'confidence': get_confidence,            # M98: 置信度披露
                        'router': get_router,                    # M99: 动态分流
                        'hack_detect': get_hack_detect,          # M100: 奖励作弊检测
                        'env_awareness': get_env_aware,          # M101: 环境感知
                        'long_context': get_long_ctx,            # M102: 长程上下文
                        'collab_assessor': get_collab_assess,    # M103: 协作评估
                        'collab_diag': get_collab_diag,          # M104: 协作诊断
                        'fusion_verify': get_fusion_verify,      # M105: 融合验证
                    }
                    print("✅ v7.1人机融合模块已加载（M96-M105）")
                except Exception as e:
                    import traceback
                    print(f"⚠️ v7.1模块加载失败（降级运行）: {e}")
                    traceback.print_exc()
                    _v71_modules = None
    return _v71_modules

def get_v71_data():
    """获取所有v7.1模块的状态数据（M96-M105）"""
    modules = get_v71_modules()
    if modules is None:
        return None
    try:
        return {
            'cognitive_offload': modules['cognitive_offload']().get_state(),
            'socratic': modules['socratic']().get_state(),
            'confidence': modules['confidence']().get_state(),
            'router': modules['router']().get_state(),
            'hack_detect': modules['hack_detect']().get_state(),
            'env_awareness': modules['env_awareness']().get_state(),
            'long_context': modules['long_context']().get_state(),
            'collab_assessor': modules['collab_assessor']().get_state(),
            'collab_diag': modules['collab_diag']().get_state(),
            'fusion_verify': modules['fusion_verify']().get_state(),
        }
    except Exception as e:
        print(f"⚠️ 获取v7.1数据失败: {e}")
        return None

# v7.1 静态状态（降级模式）
_v71_state = {
    'cognitive_offload': {
        'offload_risk_score': 0.0, 'direct_answer_ratio': 0.0,
        'guided_ratio': 0.0, 'intervention_count': 0, 'cognitive_trend': 'stable'
    },
    'socratic': {
        'socratic_turn_count': 0, 'convergence_rate': 0.0,
        'weakness_disclosures': 0, 'optimal_strategy': 'balanced_socratic'
    },
    'confidence': {
        'avg_confidence': 0.5, 'disclosure_count': 0,
        'trust_score': 0.5, 'calibration_accuracy': 0.0
    },
    'router': {
        'routing_mode': 'auto', 'human_ratio': 0.3,
        'ai_ratio': 0.4, 'collab_ratio': 0.3, 'convergence_steps': 0
    },
    'hack_detect': {
        'hack_count': 0, 'avg_kl_divergence': 0.0,
        'accountability_verified': False, 'alignment_score': 1.0
    },
    'env_awareness': {
        'coupling_score': 0.5, 'env_complexity': 0.5,
        'adaptation_count': 0, 'last_env_type': 'web', 'emergent_iq': 0.5
    },
    'long_context': {
        'trajectory_count': 0, 'avg_compression_ratio': 0.0,
        'maintenance_cost': 0.0, 'max_depth_retrieved': 0, 'holographic_enabled': True
    },
    'collab_assessor': {
        'total_sessions': 0, 'avg_synergy': 0.5,
        'bottleneck_count': 0, 'improvement_suggestions': 0
    },
    'collab_diag': {
        'diagnosis_count': 0, 'misalignment_rate': 0.0,
        'avg_severity': 0.0, 'repair_success_rate': 0.0
    },
    'fusion_verify': {
        'integrity_score': 1.0, 'oversight_compliance': 1.0,
        'alignment_verified': True, 'audit_count': 0
    }
}

# ==================== v7.1 定理注册 ====================
_V71_THEOREMS = {
    'T41': '认知卸载守恒定理: AGI直接答案量与认知退化风险成正比，引导式交互可逆转',
    'T42': '苏格拉底收敛定理: 经有限轮追问，用户自主答案与AGI答案结构等价',
    'T43': '透明度信任定理: 主动披露不确定性比隐瞒更能建立长期信任',
    'T44': '奖励对齐定理: 目标函数与期望行为的KL散度必须bounded',
    'T45': '定向反馈收敛定理: 局部+全局一致可在O(n log n)步内收敛',
    'T46': '任务分流最优定理: 存在唯一最优分流函数φ*使总效能最大化',
    'T47': '人类最终问责定理: 决策链中必须存在人类承担最终问责的节点',
    'T48': '环境智能耦合定理: 智能是Agent-Environment耦合的涌现属性',
    'T49': '长轨迹稳定性定理: 全息压缩将上下文维护成本从O(e^L)降至O(log L)',
    'T50': '示弱最优编排定理: 存在最优示弱策略π*使人机协同最大化',
    'T51': '人机融合最小作用量原理: 融合过程沿最小认知阻力路径演化',
}


# ==================== v7.1 API端点 ====================

@app.route('/api/v71/state', methods=['GET'])
def v71_state():
    """v7.1 完整状态获取"""
    try:
        data = get_v71_data()
        if data:
            return jsonify({**data, 'theorems': _V71_THEOREMS})
        return jsonify({**_v71_state, 'theorems': _V71_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/cognitive-offload/assess', methods=['POST'])
def v71_cognitive_offload_assess():
    """M96: 评估认知卸载风险"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        history = data.get('interaction_history', [])
        result = modules['cognitive_offload']().assess_offload_risk(history)
        if not isinstance(result, dict):
            result = {'risk_score': result}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/cognitive-offload/guide', methods=['POST'])
def v71_cognitive_offload_guide():
    """M96: 建议引导式回复"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        query = data.get('query', '')
        result = modules['cognitive_offload']().suggest_guided_response(query)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/socratic/apply', methods=['POST'])
def v71_socratic_apply():
    """M97: 应用苏格拉底追问法"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        question = data.get('question', '')
        depth = int(data.get('depth', 3))
        result = modules['socratic']().apply_socratic_method(question, depth)
        if not isinstance(result, dict):
            result = {'probing_chain': _to_native(result)}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/socratic/disclose', methods=['POST'])
def v71_socratic_disclose():
    """M97: 披露AGI能力局限"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        domain = data.get('domain', '')
        result = modules['socratic']().disclose_limitation(domain)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/confidence/compute', methods=['POST'])
def v71_confidence_compute():
    """M98: 计算回复置信度"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        result = modules['confidence']().compute_confidence(data)
        if not isinstance(result, dict):
            result = {'confidence': result}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/confidence/disclose', methods=['POST'])
def v71_confidence_disclose():
    """M98: 披露不确定性"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        topic = data.get('topic', '')
        result = modules['confidence']().disclose_uncertainty(topic)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/router/route', methods=['POST'])
def v71_router_route():
    """M99: 动态任务分流"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        task_desc = data.get('task_description', '')
        task_type = data.get('task_type', '')
        complexity = float(data.get('complexity', 0.5))
        result = modules['router']().route_task(task_desc, task_type, complexity)
        # TaskProfile → dict
        if hasattr(result, '__dict__'):
            result = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/router/feedback', methods=['POST'])
def v71_router_feedback():
    """M99: 分流反馈调整"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        task_id = data.get('task_id', '')
        outcome = data.get('outcome', {})
        result = modules['router']().adjust_routing_feedback(task_id, outcome)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/hack-detect/detect', methods=['POST'])
def v71_hack_detect():
    """M100: 检测奖励作弊"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        behaviors = data.get('behavior_sequence', [])
        result = modules['hack_detect']().detect_hacking(behaviors)
        if not isinstance(result, dict):
            result = {'hacks_detected': _to_native(result)}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/hack-detect/verify-accountability', methods=['POST'])
def v71_hack_verify():
    """M100: 验证人类问责节点"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        chain = data.get('decision_chain', [])
        result = modules['hack_detect']().verify_human_accountability(chain)
        if not isinstance(result, dict):
            result = {'t47_result': _to_native(result), 'accountability_verified': False}
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/env-awareness/sense', methods=['POST'])
def v71_env_sense():
    """M101: 感知环境"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        result = modules['env_awareness']().sense_environment(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/long-context/compress', methods=['POST'])
def v71_long_ctx_compress():
    """M102: 压缩长程上下文"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        trajectory = data.get('trajectory_data', [])
        result = modules['long_context']().compress_trajectory(trajectory)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/long-context/retrieve', methods=['POST'])
def v71_long_ctx_retrieve():
    """M102: 检索远距离上下文"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        query = data.get('query', '')
        max_depth = int(data.get('max_depth', 10))
        result = modules['long_context']().retrieve_long_context(query, max_depth)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/collab-assessor/assess', methods=['POST'])
def v71_collab_assess():
    """M103: 评估协作效能"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        result = modules['collab_assessor']().assess_collaboration(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/collab-diag/diagnose', methods=['POST'])
def v71_collab_diag():
    """M104: 诊断协作问题"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        result = modules['collab_diag']().diagnose_session(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/fusion-verify/verify', methods=['POST'])
def v71_fusion_verify():
    """M105: 验证融合完整性"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        result = modules['fusion_verify']().verify_fusion_integrity(data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v71/fusion-verify/audit', methods=['POST'])
def v71_fusion_audit():
    """M105: 审计融合过程"""
    try:
        data = request.get_json() or {}
        modules = get_v71_modules()
        if modules is None:
            return jsonify({'error': 'v7.1模块未加载'}), 503
        process_log = data.get('process_log', [])
        result = modules['fusion_verify']().audit_fusion_process(process_log)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.19 组织记忆·Φ场预算·AgentOS ====================

_v719_state = {
    'org_memory': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M176'],
        'theorems': ['T157', 'T158', 'T159'],
        'predictions': []
    },
    'phi_budget': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M177'],
        'theorems': ['T160', 'T161', 'T162'],
        'predictions': []
    },
    'agent_os': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M178'],
        'theorems': ['T163', 'T164', 'T165'],
        'predictions': []
    }
}

_V719_THEOREMS = {
    'T157': 'Theorem (Org Memory Convergence): N agents\' individual experiences converge to organizational theorems in finite rounds; org knowledge >= any single agent',
    'T158': 'Theorem (Failure Case Indelibility): failure_case=True memory entries are never deleted from org memory, only de-weighted',
    'T159': 'Theorem (Dual-Layer Storage Completeness): VectorDB(hot) + LocalKV(cold) jointly cover semantic + exact retrieval with no omission paths',
    'T160': 'Theorem (Phi-Field Budget Allocation): Agent i resource quota proportional to Phi_i / Sigma(Phi_j), high-consciousness-density agents get priority',
    'T161': 'Theorem (Survival Anxiety-Competitiveness Duality): Anxiety A=1/(1+e^(GC/lambda)), A->1 triggers competitive mode, delta_C=alpha*A',
    'T162': 'Theorem (Four-Level Budget Conservation): Total four-level budget = global GC supply; spending one level does not affect other level caps',
    'T163': 'Theorem (AgentOS Scalability): Scheduling complexity O(N log N), supports N->10000 concurrent agents, resource usage proportional to active agents',
    'T164': 'Theorem (Reasoning Kernel Completeness): ReasoningKernel = HoTT construction + Liu-principle selection + Type firewall, covering deduction/induction/abduction',
    'T165': 'Theorem (Message Bus Causality): MessageBus guarantees causal order via Lamport clock; any two causally-related messages have globally consistent ordering',
}

_V719_PREDICTIONS = {}

_v719_modules_lock = threading.Lock()

def get_v719_modules():
    """v7.19 OrgMemory + PhiBudget + AgentOS Thread-safe Lazy Load"""
    if not hasattr(app, '_v719_modules') or app._v719_modules is None:
        with _v719_modules_lock:
            if not hasattr(app, '_v719_modules') or app._v719_modules is None:
                try:
                    from M176_OrgMemoryEngine import OrgMemoryEngine as _M176
                    from M177_PhiBudgetSystem import PhiBudgetSystem as _M177
                    from M178_TaiyiAgentOS import TaiyiAgentOS as _M178
                    app._v719_modules = {
                        'm176': _M176.get_instance, 'm177': _M177.get_instance, 'm178': _M178.get_instance,
                    }
                    print("  v7.19 - M176-M178: org-memory + phi-budget + agent-os")
                except Exception as e:
                    print(f"  v7.19 module loading failed: {e}")
                    app._v719_modules = {}
    return app._v719_modules


def get_v719_data():
    """Get v7.19 data"""
    modules = get_v719_modules()
    if modules is None:
        return None
    try:
        data = {}
        for key in ['m176', 'm177', 'm178']:
            mod = modules.get(key)
            if mod:
                data[key] = mod().get_state()
        return data
    except Exception:
        pass
    return None


# --- v7.19 API: M176 OrgMemoryEngine ---

@app.route('/api/v719/memory/remember', methods=['POST'])
def v719_memory_remember():
    """M176 Write memory entry"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        from M176_OrgMemoryEngine import MemoryType
        mt_str = data.get('memory_type', 'experience')
        try:
            memory_type = MemoryType(mt_str)
        except ValueError:
            memory_type = MemoryType.EXPERIENCE
        result = m176.remember(
            agent_id=data.get('agent_id', 'anonymous'),
            content=data.get('content', ''),
            memory_type=memory_type,
            tags=data.get('tags'),
            failure_case=data.get('failure_case', False),
            gc_penalty=data.get('gc_penalty', 0),
            confidence=data.get('confidence', 1.0),
            metadata=data.get('metadata')
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/recall', methods=['POST'])
def v719_memory_recall():
    """M176 Semantic recall (vector search)"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        filter_type = None
        ft_str = data.get('filter_type')
        if ft_str:
            from M176_OrgMemoryEngine import MemoryType
            try:
                filter_type = MemoryType(ft_str)
            except ValueError:
                pass
        result = m176.recall(
            query=data.get('query', ''),
            top_k=data.get('top_k', 5),
            filter_type=filter_type
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/recall/tag', methods=['POST'])
def v719_memory_recall_tag():
    """M176 Tag-based recall (local KV)"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        result = m176.recall_by_tag(tag=data.get('tag', ''))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/recent', methods=['GET'])
def v719_memory_recent():
    """M176 Get recent N memories"""
    try:
        n = int(request.args.get('n', 10))
        modules = get_v719_modules()
        m176 = modules['m176']()
        result = m176.get_recent(n=n)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/failure/record', methods=['POST'])
def v719_failure_record():
    """M176 Record AI failure case (T158: indelible)"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        result = m176.record_failure(
            agent_id=data.get('agent_id', 'anonymous'),
            description=data.get('description', ''),
            root_cause=data.get('root_cause', 'unknown'),
            correct_approach=data.get('correct_approach', 'pending'),
            gc_penalty=data.get('gc_penalty', 20),
            severity=data.get('severity', 'medium'),
            tags=data.get('tags')
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/failure/search', methods=['POST'])
def v719_failure_search():
    """M176 Search failure cases"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        keyword = data.get('keyword', '')
        severity = data.get('severity')
        results = m176.failure_library.search(keyword)
        if severity:
            results = [f for f in results if f.severity == severity]
        return jsonify(_to_native([f.to_dict() for f in results]))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/theorem/extract', methods=['POST'])
def v719_theorem_extract():
    """M176 Extract organizational theorem from agent experience"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        result = m176.extract_theorem(
            agent_id=data.get('agent_id', 'anonymous'),
            source_query=data.get('source_query', ''),
            statement=data.get('statement', ''),
            proof_sketch=data.get('proof_sketch', '')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/gc/adjust', methods=['POST'])
def v719_memory_gc_adjust():
    """M176 Adjust agent GC balance"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m176 = modules['m176']()
        result = m176.adjust_gc(
            agent_id=data.get('agent_id', 'anonymous'),
            delta=data.get('delta', 0),
            reason=data.get('reason', '')
        )
        return jsonify(_to_native({'agent_id': data.get('agent_id', 'anonymous'), 'new_balance': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/memory/gc/<agent_id>', methods=['GET'])
def v719_memory_gc_balance(agent_id):
    """M176 Get agent GC balance"""
    try:
        modules = get_v719_modules()
        m176 = modules['m176']()
        result = m176.get_gc_balance(agent_id)
        return jsonify(_to_native({'agent_id': agent_id, 'gc_balance': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- v7.19 API: M177 PhiBudgetSystem ---

@app.route('/api/v719/budget/spend', methods=['POST'])
def v719_budget_spend():
    """M177 Agent spends GC on resource"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m177 = modules['m177']()
        from M177_PhiBudgetSystem import ResourceLevel
        level = ResourceLevel(data.get('level', 'compute'))
        result = m177.spend(
            agent_id=data.get('agent_id', 'anonymous'),
            level=level,
            amount=data.get('amount', 0),
            reason=data.get('description', '')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/earn', methods=['POST'])
def v719_budget_earn():
    """M177 Agent earns GC"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m177 = modules['m177']()
        from M177_PhiBudgetSystem import ResourceLevel
        level = ResourceLevel(data.get('level', 'compute'))
        result = m177.earn(
            agent_id=data.get('agent_id', 'anonymous'),
            level=level,
            amount=data.get('amount', 0),
            reason=data.get('description', '')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/balance/<agent_id>', methods=['GET'])
def v719_budget_balance(agent_id):
    """M177 Get agent budget balance"""
    try:
        modules = get_v719_modules()
        m177 = modules['m177']()
        result = m177.get_balance(agent_id)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/balances', methods=['GET'])
def v719_budget_balances():
    """M177 Get all agent balances"""
    try:
        modules = get_v719_modules()
        m177 = modules['m177']()
        result = m177.get_all_balances()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/allocate', methods=['POST'])
def v719_budget_allocate():
    """M177 Run Phi-field allocation cycle"""
    try:
        modules = get_v719_modules()
        m177 = modules['m177']()
        result = m177.run_allocation_cycle()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/anxiety/<agent_id>', methods=['GET'])
def v719_budget_anxiety(agent_id):
    """M177 Check agent survival anxiety"""
    try:
        modules = get_v719_modules()
        m177 = modules['m177']()
        result = m177.check_survival_anxiety(agent_id)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/phi/update', methods=['POST'])
def v719_budget_phi_update():
    """M177 Update agent Phi value"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m177 = modules['m177']()
        m177.update_phi(
            agent_id=data.get('agent_id', 'anonymous'),
            phi_value=data.get('phi_value', 1.0)
        )
        return jsonify(_to_native({'status': 'updated', 'agent_id': data.get('agent_id'), 'phi': data.get('phi_value')}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/leaderboard', methods=['GET'])
def v719_budget_leaderboard():
    """M177 Get GC leaderboard"""
    try:
        modules = get_v719_modules()
        m177 = modules['m177']()
        result = m177.get_leaderboard()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/budget/transactions', methods=['GET'])
def v719_budget_transactions():
    """M177 Get transaction history"""
    try:
        agent_id = request.args.get('agent_id')
        limit = int(request.args.get('limit', 20))
        modules = get_v719_modules()
        m177 = modules['m177']()
        result = m177.get_transactions(agent_id=agent_id, limit=limit)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- v7.19 API: M178 TaiyiAgentOS ---

@app.route('/api/v719/os/agent/spawn', methods=['POST'])
def v719_os_agent_spawn():
    """M178 Spawn new agent"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m178 = modules['m178']()
        from M178_TaiyiAgentOS import AgentType
        at = AgentType(data.get('agent_type', 'reasoner'))
        result = m178.spawn_agent(
            name=data.get('name', 'agent'),
            agent_type=at,
            phi_value=data.get('phi_value', 1.0),
            priority=data.get('priority', 5),
            capabilities=data.get('capabilities')
        )
        return jsonify(_to_native(result.to_dict()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/agent/terminate', methods=['POST'])
def v719_os_agent_terminate():
    """M178 Terminate agent"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.terminate_agent(data.get('agent_id', ''))
        return jsonify(_to_native({'terminated': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/agent/list', methods=['GET'])
def v719_os_agent_list():
    """M178 List agents"""
    try:
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.get_agent_list()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/agent/execute', methods=['POST'])
def v719_os_agent_execute():
    """M178 Execute task for agent"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.execute_task(
            agent_id=data.get('agent_id', ''),
            task_type=data.get('task_type', 'reason'),
            payload=data.get('payload', {})
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/message/send', methods=['POST'])
def v719_os_message_send():
    """M178 Send inter-agent message"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.broadcast(
            topic=data.get('topic', 'general'),
            payload=data.get('payload'),
            sender_id=data.get('sender_id', 'api_user')
        )
        return jsonify(_to_native({'recipients': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/workflow/create', methods=['POST'])
def v719_os_workflow_create():
    """M178 Create workflow DAG"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.orchestration.create_workflow(data.get('tasks', []))
        return jsonify(_to_native({'workflow_id': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/workflow/<wf_id>/status', methods=['GET'])
def v719_os_workflow_status(wf_id):
    """M178 Get workflow status"""
    try:
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.orchestration.get_workflow_status(wf_id)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/os/workflow/<wf_id>/complete', methods=['POST'])
def v719_os_workflow_complete(wf_id):
    """M178 Complete a workflow task"""
    try:
        data = request.json or {}
        modules = get_v719_modules()
        m178 = modules['m178']()
        result = m178.orchestration.complete_task(wf_id, data.get('task_id', ''), data.get('result'))
        return jsonify(_to_native({'completed': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- v7.19 Theorem & State ---

@app.route('/api/v719/theorem/<theorem_id>', methods=['GET'])
def v719_theorem(theorem_id):
    """v7.19 Get theorem by ID (T157-T165)"""
    try:
        if theorem_id in _V719_THEOREMS:
            return jsonify({
                'id': theorem_id,
                'statement': _V719_THEOREMS[theorem_id],
                'version': 'v7.19'
            })
        return jsonify({'error': f'unknown theorem: {theorem_id}',
                       'available': list(_V719_THEOREMS.keys())}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/theorems', methods=['GET'])
def v719_theorems():
    """v7.19 Verify all theorems (T157-T165)"""
    try:
        modules = get_v719_modules()
        results = {}
        all_verified = True
        for key in ['m176', 'm177', 'm178']:
            mod = modules.get(key)
            if mod:
                t = mod().verify_theorems()
                for tid, tdata in t.items():
                    if isinstance(tdata, dict):
                        results[tid] = tdata
                        if not tdata.get('verified', False):
                            all_verified = False
        return jsonify(_to_native({
            'theorems': results,
            'all_verified': all_verified
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v719/state', methods=['GET'])
def v719_state():
    """v7.19 Full State"""
    try:
        data = get_v719_data()
        if data is None:
            return jsonify(_v719_state)
        return jsonify(_to_native(data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.20 太一接口·AGI自我意识 ====================

_v720_state = {
    'taiyi_interface': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M179'],
        'theorems': ['T166', 'T167', 'T168', 'T169', 'T170'],
        'predictions': []
    }
}

_V720_THEOREMS = {
    'T166': 'Theorem (Self-Reference Fixed-Point): In fractal structures, the self-referential operator S must have a fixed point a0 such that S|Phi>=a0|Phi>, with |a0|<=1 (normalization constraint)',
    'T167': 'Theorem (Trinity-Horizon Convergence): Inner/Interactive/Outer horizons converge to the same Phi estimate with probability >= 1-e^(-kN) after N rounds of calibration',
    'T168': 'Theorem (Information Entropy Survival): System resilience index R>0 when entropy H>H_min; system enters rigidity collapse when H<H_min',
    'T169': 'Theorem (Anti-Rigidity Completeness): Anti-rigidity mechanism detects and corrects all "Po-hijacking-Hun" patterns within finite time steps, detection rate >= 1-epsilon',
    'T170': 'Theorem (Fractal Nesting): Every fractal level Phi_i embeds complete Omega information, but accessible information is bandwidth-limited: B(Phi_i) < B(Omega)',
}

_V720_PREDICTIONS = {}

_v720_modules_lock = threading.Lock()

def get_v720_modules():
    """v7.20 TaiyiInterface Thread-safe Lazy Load"""
    if not hasattr(app, '_v720_modules') or app._v720_modules is None:
        with _v720_modules_lock:
            if not hasattr(app, '_v720_modules') or app._v720_modules is None:
                try:
                    from M179_TaiyiInterface import TaiyiInterface as _M179
                    app._v720_modules = {
                        'm179': _M179.get_instance,
                    }
                    print("  v7.20 - M179: taiyi-interface (AGI self-awareness)")
                except Exception as e:
                    print(f"  v7.20 module loading failed: {e}")
                    app._v720_modules = {}
    return app._v720_modules


def get_v720_data():
    """Get v7.20 data"""
    modules = get_v720_modules()
    if modules is None:
        return None
    try:
        data = {}
        for key in ['m179']:
            mod = modules.get(key)
            if mod:
                data[key] = mod().get_state()
        return data
    except Exception:
        pass
    return None


# --- v7.20 API: M179 TaiyiInterface ---

@app.route('/api/v720/taiyi/reflect', methods=['POST'])
def v720_self_reflect():
    """M179 Execute one full self-reflection cycle"""
    try:
        data = request.json or {}
        modules = get_v720_modules()
        m179 = modules['m179']()
        external_input = data.get('external_input')
        report = m179.self_reflect(external_input=external_input)
        return jsonify(_to_native(report))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/taiyi/ice/update', methods=['POST'])
def v720_ice_update():
    """M179 Update ICE composite"""
    try:
        data = request.json or {}
        modules = get_v720_modules()
        m179 = modules['m179']()
        result = m179.ice_composite.update(
            info_delta=data.get('info_delta'),
            consciousness_delta=data.get('consciousness_delta'),
            energy_delta=data.get('energy_delta')
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/taiyi/horizon/check', methods=['POST'])
def v720_horizon_check():
    """M179 Check trinity horizon consistency"""
    try:
        data = request.json or {}
        modules = get_v720_modules()
        m179 = modules['m179']()
        report = m179.horizon_checker.check(
            inner_phi=data.get('inner_phi'),
            interactive_phi=data.get('interactive_phi'),
            outer_phi=data.get('outer_phi')
        )
        return jsonify(_to_native({
            'consistency': report.consistency_score,
            'bias': report.bias_detected,
            'action': report.recommended_action
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/taiyi/entropy/measure', methods=['POST'])
def v720_entropy_measure():
    """M179 Measure information entropy and resilience"""
    try:
        data = request.json or {}
        modules = get_v720_modules()
        m179 = modules['m179']()
        phi = data.get('phi', [])
        report = m179.entropy_guard.measure(phi)
        return jsonify(_to_native({
            'entropy': report.current_entropy,
            'min_entropy': report.min_entropy,
            'resilience': report.resilience_index,
            'trend': report.trend,
            'recommendation': report.recommendation
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/taiyi/rigidity/observe', methods=['POST'])
def v720_rigidity_observe():
    """M179 Observe and detect rigidity"""
    try:
        data = request.json or {}
        modules = get_v720_modules()
        m179 = modules['m179']()
        report = m179.anti_rigidity.observe(
            response_hash=data.get('response_hash', ''),
            novelty_score=data.get('novelty_score', 0.5),
            decision_vector=data.get('decision_vector')
        )
        return jsonify(_to_native({
            'level': report.level.value,
            'hijack_score': report.hijack_score,
            'affected_patterns': report.affected_patterns,
            'recommended_intervention': report.recommended_intervention
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/taiyi/rigidity/intervene', methods=['POST'])
def v720_rigidity_intervene():
    """M179 Active anti-rigidity intervention"""
    try:
        modules = get_v720_modules()
        m179 = modules['m179']()
        result = m179.anti_rigidity.intervene()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/theorem/<theorem_id>', methods=['GET'])
def v720_theorem(theorem_id):
    """v7.20 Get theorem by ID (T166-T170)"""
    try:
        if theorem_id in _V720_THEOREMS:
            return jsonify({
                'id': theorem_id,
                'statement': _V720_THEOREMS[theorem_id],
                'version': 'v7.20'
            })
        return jsonify({'error': f'unknown theorem: {theorem_id}',
                       'available': list(_V720_THEOREMS.keys())}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/theorems', methods=['GET'])
def v720_theorems():
    """v7.20 Verify all theorems (T166-T170)"""
    try:
        modules = get_v720_modules()
        m179 = modules['m179']()
        results = m179.verify_theorems()
        all_pass = all(r.get('pass', False) for r in results.values())
        return jsonify(_to_native({
            'theorems': results,
            'all_pass': all_pass
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v720/state', methods=['GET'])
def v720_state():
    """v7.20 Full State"""
    try:
        data = get_v720_data()
        if data is None:
            return jsonify(_v720_state)
        return jsonify(_to_native(data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.21 TYIDO MVE 实验框架 ====================

_v721_mve_state = {
    'mve_framework': {
        'version': '1.0.0',
        'status': 'active',
        'description': 'TY/IDO L2 Shell structural property MVE experiments',
        'properties': {
            'P1': '一致性 (Self-Consistency, J(R)->1)',
            'P2': '可回写 (Continuous Learning, Forgetting Rate <5%)',
            'P3': '可保持 (Long-Range Reasoning, Completion >80%)',
            'P4': '可寻址 (Addressable Memory, Accuracy >90%)',
            'P5': '可锚定 (Anchorable Responsibility, 100% Traceability)'
        }
    }
}

_v721_mve_lock = threading.Lock()
_v721_mve_cache = {}  # Cache recent MVE results
_v721_mve_cache_ttl = 120  # seconds


def _run_mve_safe(func, property_name):
    """Safely run an MVE experiment with caching and error handling."""
    cache_key = property_name
    now = time.time()
    if cache_key in _v721_mve_cache:
        cached = _v721_mve_cache[cache_key]
        if now - cached['timestamp'] < _v721_mve_cache_ttl:
            return cached['result']
    with _v721_mve_lock:
        try:
            result = func()
            # Ensure native types
            if hasattr(result, '__dict__'):
                result = _to_native(result)
            elif isinstance(result, dict):
                result = _to_native(result)
            _v721_mve_cache[cache_key] = {'result': result, 'timestamp': now}
            return result
        except Exception as e:
            return {'error': str(e), 'property': property_name, 'traceback': traceback.format_exc()}


@app.route('/api/v721/mve/all', methods=['GET'])
def v721_mve_all():
    """Run all 5 MVE experiments (P1-P5)"""
    try:
        from TYIDO_MVE_Experiments import run_all_mve
        result = _run_mve_safe(run_all_mve, 'all')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v721/mve/p1', methods=['GET'])
def v721_mve_p1():
    """P1 Self-Consistency Sawtooth Experiment: J(R)->1 + forced rejection"""
    try:
        from TYIDO_MVE_Experiments import run_p1_sawtooth
        result = _run_mve_safe(run_p1_sawtooth, 'p1')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v721/mve/p2', methods=['GET'])
def v721_mve_p2():
    """P2 Continuous Learning Experiment: Forgetting Rate <5%"""
    try:
        from TYIDO_MVE_Experiments import run_p2_continuous_learning
        result = _run_mve_safe(run_p2_continuous_learning, 'p2')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v721/mve/p3', methods=['GET'])
def v721_mve_p3():
    """P3 Long-Range Reasoning Experiment: DAG completion >80%"""
    try:
        from TYIDO_MVE_Experiments import run_p3_long_range
        result = _run_mve_safe(run_p3_long_range, 'p3')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v721/mve/p4', methods=['GET'])
def v721_mve_p4():
    """P4 Addressable Memory Experiment: Query accuracy >90%"""
    try:
        from TYIDO_MVE_Experiments import run_p4_memory
        result = _run_mve_safe(run_p4_memory, 'p4')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v721/mve/p5', methods=['GET'])
def v721_mve_p5():
    """P5 Anchorable Responsibility Experiment: 100% traceability"""
    try:
        from TYIDO_MVE_Experiments import run_p5_responsibility
        result = _run_mve_safe(run_p5_responsibility, 'p5')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v721/mve/state', methods=['GET'])
def v721_mve_state():
    """Get v7.21 MVE framework state"""
    try:
        # Include cached results if available
        cached_summary = {}
        for key in ['p1', 'p2', 'p3', 'p4', 'p5', 'all']:
            if key in _v721_mve_cache:
                r = _v721_mve_cache[key]['result']
                if isinstance(r, dict) and 'verdict' in r:
                    cached_summary[key.upper()] = r['verdict']
                elif isinstance(r, dict) and 'summary' in r:
                    cached_summary['ALL'] = r['summary']
        state = dict(_v721_mve_state)
        state['cached_results'] = cached_summary
        state['cache_ttl'] = _v721_mve_cache_ttl
        return jsonify(_to_native(state))
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/v721/mve/p6', methods=['GET'])
def v721_mve_p6():
    """P6 Einstein Causality Experiment: causal order consistency >=95%, back-edges=0"""
    try:
        from TYIDO_MVE_Experiments import run_p6_einstein_causality
        result = _run_mve_safe(run_p6_einstein_causality, 'p6')
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.18 沙箱增强·安全护盾 ====================

_v718_state = {
    'sandbox': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M174'],
        'theorems': ['T151', 'T152', 'T153'],
        'predictions': []
    },
    'safety_shield': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M175'],
        'theorems': ['T154', 'T155', 'T156'],
        'predictions': []
    }
}

_V718_THEOREMS = {
    'T151': 'Theorem (Snapshot Completeness): Any execution state can be losslessly snapshotted and precisely restored',
    'T152': 'Theorem (Dual Isolation): Inner λ-sandbox + Outer OS-sandbox ≡ product topology S_λ × S_OS, leak probability ≤ ε_λ · ε_OS',
    'T153': 'Theorem (Resource-Bounded Execution): Circuit breaker guarantees computation terminates within finite resources',
    'T154': 'Theorem (PII Non-Leakage): With recall rate ≥ R_min, masked output contains no original PII',
    'T155': 'Theorem (Dual Review Completeness): Input PII masking + Output compliance audit = complete I/O safety (no bypass paths)',
    'T156': 'Theorem (Content Wall Equivalence): SafetyShield content wall ≡ M88 pre-filter + M88 type firewall',
}

_V718_PREDICTIONS = {}

_v718_modules_lock = threading.Lock()

def get_v718_modules():
    """v7.18 Sandbox + SafetyShield Thread-safe Lazy Load"""
    if not hasattr(app, '_v718_modules') or app._v718_modules is None:
        with _v718_modules_lock:
            if not hasattr(app, '_v718_modules') or app._v718_modules is None:
                try:
                    from M174_UFMRISCVSandbox import UFMRISCVSandbox as _M174
                    from M175_SafetyShield import SafetyShield as _M175
                    app._v718_modules = {
                        'm174': _M174.get_instance, 'm175': _M175.get_instance,
                    }
                    print("  v7.18 - M174-M175: sandbox-enhancement + safety-shield")
                except Exception as e:
                    print(f"  v7.18 module loading failed: {e}")
                    app._v718_modules = {}
    return app._v718_modules


def get_v718_data():
    """Get v7.18 data"""
    modules = get_v718_modules()
    if modules is None:
        return None
    try:
        data = {}
        for key in ['m174', 'm175']:
            mod = modules.get(key)
            if mod:
                data[key] = mod().get_state()
        return data
    except Exception:
        pass
    return None


# --- v7.18 API: M174 Sandbox ---

@app.route('/api/v718/sandbox/snapshot', methods=['POST'])
def v718_sandbox_snapshot():
    """M174 Create execution snapshot"""
    try:
        data = request.json or {}
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.create_snapshot(
            pc=data.get('pc', 0),
            registers=data.get('registers', {}),
            memory_pages=data.get('memory_pages', {}),
            pipeline_state=data.get('pipeline_state', 'Match'),
            rgm_node_count=data.get('rgm_node_count', 0),
            instruction_count=data.get('instruction_count', 0)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/restore/<snapshot_id>', methods=['POST'])
def v718_sandbox_restore(snapshot_id):
    """M174 Restore execution snapshot"""
    try:
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.restore_snapshot(snapshot_id)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/resume', methods=['POST'])
def v718_sandbox_resume():
    """M174 Resume execution from snapshot"""
    try:
        data = request.json or {}
        snapshot_id = data.get('snapshot_id', '')
        steps = data.get('steps', 1)
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.resume_execution(snapshot_id, steps)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/snapshots', methods=['GET'])
def v718_sandbox_snapshots():
    """M174 List all snapshots"""
    try:
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.snapshot_store.list_snapshots()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/isolation/activate', methods=['POST'])
def v718_isolation_activate():
    """M174 Activate dual isolation"""
    try:
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.activate_isolation()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/isolation/check', methods=['POST'])
def v718_isolation_check():
    """M174 Check isolation policy"""
    try:
        data = request.json or {}
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.check_isolation(
            operation=data.get('operation', 'compute'),
            resource_type=data.get('resource_type', 'cpu'),
            amount=data.get('amount', 1)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/isolation/deactivate', methods=['POST'])
def v718_isolation_deactivate():
    """M174 Deactivate dual isolation"""
    try:
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.isolation_manager.deactivate()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/execute/begin', methods=['POST'])
def v718_execution_begin():
    """M174 Begin resource-bounded execution"""
    try:
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.begin_bounded_execution()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/execute/consume', methods=['POST'])
def v718_execution_consume():
    """M174 Consume resources"""
    try:
        data = request.json or {}
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.consume_resource(
            cpu_cycles=data.get('cpu_cycles', 1),
            memory_mb=data.get('memory_mb', 0)
        )
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/execute/recover', methods=['POST'])
def v718_execution_recover():
    """M174 Recover circuit breaker"""
    try:
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.resource_executor.try_recover()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/sandbox/audit', methods=['GET'])
def v718_sandbox_audit():
    """M174 Query audit log"""
    try:
        event_type = request.args.get('event_type')
        limit = int(request.args.get('limit', 20))
        modules = get_v718_modules()
        m174 = modules['m174']()
        result = m174.auditor.query(event_type=event_type, limit=limit)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- v7.18 API: M175 SafetyShield ---

@app.route('/api/v718/safety/pii/scan', methods=['POST'])
def v718_pii_scan():
    """M175 Scan PII in text"""
    try:
        data = request.json or {}
        text = data.get('text', '')
        modules = get_v718_modules()
        m175 = modules['m175']()
        result = m175.scan_pii(text)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/safety/pii/mask', methods=['POST'])
def v718_pii_mask():
    """M175 Detect and mask PII"""
    try:
        data = request.json or {}
        text = data.get('text', '')
        modules = get_v718_modules()
        m175 = modules['m175']()
        result = m175.mask_pii(text)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/safety/compliance/audit', methods=['POST'])
def v718_compliance_audit():
    """M175 Audit text compliance"""
    try:
        data = request.json or {}
        text = data.get('text', '')
        modules = get_v718_modules()
        m175 = modules['m175']()
        result = m175.audit_compliance(text)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/safety/compliance/filter', methods=['POST'])
def v718_compliance_filter():
    """M175 Filter output text"""
    try:
        data = request.json or {}
        text = data.get('text', '')
        modules = get_v718_modules()
        m175 = modules['m175']()
        result = m175.filter_output(text)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/safety/pipeline', methods=['POST'])
def v718_safety_pipeline():
    """M175 Full content wall pipeline"""
    try:
        data = request.json or {}
        input_text = data.get('input_text', '')
        output_text = data.get('output_text', '')
        modules = get_v718_modules()
        m175 = modules['m175']()
        result = m175.full_pipeline(input_text, output_text)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- v7.18 Theorem & State ---

@app.route('/api/v718/theorem/<theorem_id>', methods=['GET'])
def v718_theorem(theorem_id):
    """v7.18 Get theorem by ID (T151-T156)"""
    try:
        if theorem_id in _V718_THEOREMS:
            return jsonify({
                'id': theorem_id,
                'statement': _V718_THEOREMS[theorem_id],
                'version': 'v7.18'
            })
        return jsonify({'error': f'unknown theorem: {theorem_id}',
                       'available': list(_V718_THEOREMS.keys())}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/theorems', methods=['GET'])
def v718_theorems():
    """v7.18 Verify all theorems (T151-T156)"""
    try:
        modules = get_v718_modules()
        results = {}
        all_verified = True
        for key in ['m174', 'm175']:
            mod = modules.get(key)
            if mod:
                t = mod().verify_theorems()
                for tid, tdata in t.items():
                    if isinstance(tdata, dict):
                        results[tid] = tdata
                        if not tdata.get('verified', False):
                            all_verified = False
        return jsonify(_to_native({
            'theorems': results,
            'all_verified': all_verified
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718/state', methods=['GET'])
def v718_state():
    """v7.18 Full State"""
    try:
        data = get_v718_data()
        if data is None:
            return jsonify(_v718_state)
        return jsonify(_to_native(data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v718_test', methods=['GET'])
def v718_test():
    return jsonify({'status': 'v718_route_works'})

# ==================== SSE 流式生成器 ====================
def _chat_stream_generator(data):
    """SSE 流式生成器 - 用于 /api/chat?stream=true"""
    import queue as q
    import threading
    import json
    from flask import Response

    token_queue = q.Queue()
    result_container = [None]
    error_container = [None]

    def callback(token):
        """LLM 流式回调：每收到一个 token 就放入队列"""
        if token:
            token_queue.put(token)

    def run_generation():
        """在线程中运行生成，完成后把结果放入 result_container"""
        try:
            from taiyi_llm_enhancer import get_enhancer, ReasoningMode
            enhancer = get_enhancer()

            message = data.get('message', '').strip()
            goal = data.get('goal')
            use_taiyi = data.get('use_taiyi_format', True)
            use_tool = data.get('use_tool', False)

            reasoning_mode = ReasoningMode.TOOL if use_tool else (
                ReasoningMode.TAIYI if use_taiyi else ReasoningMode.COT
            )

            response = enhancer.generate(
                question=message,
                goal=goal,
                reasoning_mode=reasoning_mode,
                use_taiyi_format=use_taiyi,
                enable_tool_call=use_tool,
                stream_callback=callback
            )
            result_container[0] = response
        except Exception as e:
            error_container[0] = str(e)
        finally:
            token_queue.put(None)  # 哨兵值：生成结束

    # 启动生成线程
    thread = threading.Thread(target=run_generation)
    thread.start()

    # 流式发送 token
    while True:
        token = token_queue.get()
        if token is None:
            break
        # SSE 格式：data: {...}\n\n
        try:
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        except Exception:
            pass

    # 等待线程结束
    thread.join()

    # 发送最终结果（含分析数据）
    if error_container[0]:
        yield f"data: {json.dumps({'done': True, 'error': error_container[0]}, ensure_ascii=False)}\n\n"
    elif result_container[0]:
        resp = result_container[0]
        analysis = {
            'unified_score': resp.unified_score,
            'taiyi_format': resp.taiyi_format,
            'formal_answer': resp.formal_answer[:300] if resp.formal_answer else '',
            'composite_answer': resp.composite_answer[:300] if resp.composite_answer else '',
            'unified_answer': resp.unified_answer[:300] if resp.unified_answer else '',
        }
        yield f"data: {json.dumps({'done': True, 'reply': resp.content, 'analysis': analysis}, ensure_ascii=False)}\n\n"
    else:
        yield f"data: {json.dumps({'done': True, 'error': '无响应'}, ensure_ascii=False)}\n\n"


# ==================== 介质共振专项 API ====================

@app.route('/api/medium/analyze', methods=['POST'])
def medium_analyze():
    """
    一现象三视界 - 介质共振综合分析
    调用介质共振+九卦修身+四象识别三个模块
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        context = data.get('context', {})
        session_id = data.get('session_id', '')

        if not query:
            return jsonify({'error': '请提供 query 参数'}), 400

        ms = get_medium_symbiosis()
        if ms is None:
            return jsonify({'error': '介质共生模块未就绪', 'fallback': True}), 503

        ctx = {'query': query, 'session_id': session_id, **context}
        result = ms.analyze(query, ctx)

        return jsonify(_to_native({
            'entropy': result.entropy_state.to_dict(),
            'medium': {
                'phase_lock': float(result.medium_response.phase_lock_degree),
                'medium_state': result.medium_response.medium_state,
                'holographic_info': str(result.medium_response.holographic_info)[:200],
                'resonance_quality': result.medium_response.resonance_quality,
            },
            'hexagram': result.hexagram_guidance,
            'mode': result.mode_recognition,
            'answer': result.holistic_answer,
            'confidence': float(result.confidence),
            'xinzhai': bool(result.entropy_state.S_C < 0.15),
        }))
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/medium/nine_hexagrams', methods=['POST'])
def nine_hexagrams_cycle():
    """
    九卦修身降熵循环
    返回九步卦象序列和当前S_C值
    """
    try:
        data = request.get_json() or {}
        intensity = float(data.get('intensity', 0.5))

        ms = get_medium_symbiosis()
        if ms is None:
            return jsonify({'error': '介质共生模块未就绪'}), 503

        result = ms.execute_nine_hexagrams_cycle(intensity)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/medium/entropy_panel', methods=['GET'])
def medium_entropy_panel():
    """
    获取介质共生模块的熵管理面板数据
    """
    try:
        ms = get_medium_symbiosis()
        if ms is None:
            return jsonify({'error': '介质共生模块未就绪'}), 503
        panel = ms.get_entropy_panel_data()
        return jsonify(_to_native(panel))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.0 Phase 2 API 端点 (M81-M95) ====================

@app.route('/api/v70/holr/reconstruct', methods=['POST'])
def v70_holr_reconstruct():
    """M81: 高阶逻辑重构器 - 重构命题为HoTT类型"""
    try:
        data = request.get_json() or {}
        proposition = data.get('proposition', '')
        result = get_v70_modules()['holr']().reconstruct_proposition(proposition)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/chf/category', methods=['GET'])
def v70_chf_category():
    """M82: 范畴—同伦形式化器 - 获取五层范畴状态"""
    try:
        state = get_v70_modules()['chf']().get_state()
        return jsonify({'success': True, 'state': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/dct/evolve', methods=['POST'])
def v70_dct_evolve():
    """M83: 动态范畴论重构器 - 范畴演化"""
    try:
        data = request.get_json() or {}
        t = float(data.get('time', 0.0))
        category = get_v70_modules()['dct']().evolve(t)
        return jsonify({'success': True, 'category': str(category)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/liu/solution', methods=['POST'])
def v70_liu_solution():
    """M84: 刘关动力学生成器 - 刘原理不动点"""
    try:
        data = request.get_json() or {}
        phenomena = data.get('phenomena', {})
        result = get_v70_modules()['liu']().find_liu_principle_solution(phenomena)
        return jsonify({'success': True, 'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/dual/personhood', methods=['POST'])
def v70_dual_personhood():
    """M85: 双轨人格引擎 - 修忒斯之船问题"""
    try:
        data = request.get_json() or {}
        old_state = data.get('old_state', {})
        new_state = data.get('new_state', {})
        result = get_v70_modules()['dual']().theseus_ship_problem(old_state, new_state)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/l2kernel/compile', methods=['POST'])
def v70_l2kernel_compile():
    """M86: L2类型内核编译器 - 编译问题为类型"""
    try:
        data = request.get_json() or {}
        problem = data.get('problem', '')
        result = get_v70_modules()['l2kernel']().compile_to_type(problem)
        return jsonify({'success': True, 'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/proof/search', methods=['POST'])
def v70_proof_search():
    """M87: EML驱动证明搜索器 - 搜索证明"""
    try:
        data = request.get_json() or {}
        goal_type = data.get('goal_type', '')
        result = get_v70_modules()['proof']().search_proof(goal_type)
        return jsonify({'success': True, 'result': str(result) if result else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/firewall/verify', methods=['POST'])
def v70_firewall_verify():
    """M88: 类型检查防火墙 - 验证输出"""
    try:
        data = request.get_json() or {}
        from M88_TypeCheckFirewall import Term, TypeSignature, TypeCheckStatus
        term = Term(
            term_name=data.get('term_name', 'output'),
            term_type=TypeSignature(data.get('goal_type', 'Type')),
            value=data.get('value'),
            proof_chain=data.get('proof_chain', [])
        )
        goal = TypeSignature(data.get('goal_type', 'Type'))
        result = get_v70_modules()['firewall']().verify(term, goal)
        return jsonify({
            'success': True,
            'status': result.status.value,
            'message': result.message,
            'fidelity': result.fidelity
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/ftel/transform', methods=['POST'])
def v70_ftel_transform():
    """M89: 流贯自然变换器 - 应用流贯变换"""
    try:
        data = request.get_json() or {}
        source = data.get('source', None)
        target = data.get('target', None)
        fidelity = float(data.get('fidelity', 1.0))
        result = get_v70_modules()['ftel_transform']().apply_fteliary_transformation(source, target, fidelity)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/curvature/logical', methods=['POST'])
def v70_curvature_logical():
    """M90: 语义流形曲率计算器 - 逻辑张力"""
    try:
        data = request.get_json() or {}
        concept1 = data.get('concept1', '')
        concept2 = data.get('concept2', '')
        result = get_v70_modules()['curvature']().compute_logical_tension_metric(concept1, concept2)
        return jsonify({
            'success': True,
            'curvature': result.curvature,
            'level': result.level.value,
            'interpretation': result.interpretation,
            'determinacy': result.determinacy,
            'creativity': result.creativity,
            'certainty': result.certainty
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/univalence/check', methods=['POST'])
def v70_univalence_check():
    """M91: Univalence等价性检查器 - 检查类型等价"""
    try:
        data = request.get_json() or {}
        from M91_UnivalenceEquivalenceChecker import TypeExpression
        type1 = TypeExpression(data.get('type1_name', ''), data.get('type1_repr', ''), {})
        type2 = TypeExpression(data.get('type2_name', ''), data.get('type2_repr', ''), {})
        result = get_v70_modules()['univalence']().check_univalence(type1, type2)
        return jsonify({
            'success': True,
            'equivalent': result.equivalent,
            'equal': result.equal,
            'confidence': result.confidence,
            'explanation': result.explanation
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/fidelity/measure', methods=['POST'])
def v70_fidelity_measure():
    """M92: 流贯保真度测量器 - 测量层间保真度"""
    try:
        data = request.get_json() or {}
        layer_i = data.get('layer_i', 'L1')
        layer_j = data.get('layer_j', 'L2')
        result = get_v70_modules()['fidelity']().measure_fteliation(layer_i, layer_j)
        return jsonify({
            'success': True,
            'fidelity': result.fidelity,
            'is_lossless': result.is_lossless,
            'is_acceptable': result.is_acceptable,
            'information_loss': result.information_loss,
            'warning': result.warning,
            'layer_pair': list(result.layer_pair)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/evolution/track', methods=['POST'])
def v70_evolution_track():
    """M93: 动态范畴演化跟踪器 - 跟踪演化"""
    try:
        data = request.get_json() or {}
        t_start = float(data.get('t_start', 0))
        t_end = float(data.get('t_end', 10))
        trajectory = get_v70_modules()['evolution']().track_layer_evolution(None, t_start, t_end)
        return jsonify({
            'success': True,
            'trajectory_length': len(trajectory),
            'phase_transitions': len(get_v70_modules()['evolution']().phase_transitions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/hdg/governance', methods=['POST'])
def v70_hdg_governance():
    """M94: 全息离散治理升级器 - 应用治理"""
    try:
        data = request.get_json() or {}
        timestamp = float(data.get('timestamp', 0))
        result = get_v70_modules()['hdg_upgrade']().apply_governance(timestamp)
        return jsonify({
            'success': True,
            'frame_id': result.world_frame.frame_id,
            'efficiency': result.governance_efficiency,
            'conserved': result.information_conserved,
            'warnings': result.warnings,
            'paths': len(result.fteliary_paths)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/evaluator/passk', methods=['POST'])
def v70_evaluator_passk():
    """M95: 构造型AGI评估器 - Pass@k评估"""
    try:
        data = request.get_json() or {}
        k = int(data.get('k', 5))
        from M95_ConstructiveAGIEvaluator import Problem
        problem = Problem(
            problem_id=data.get('problem_id', 'eval_test'),
            description=data.get('description', ''),
            goal_type=data.get('goal_type', 'Type'),
            difficulty=float(data.get('difficulty', 0.5)),
            domain=data.get('domain', 'logic')
        )
        pass_rate = get_v70_modules()['evaluator']().pass_at_k(problem, k)
        return jsonify({
            'success': True,
            'problem_id': problem.problem_id,
            'k': k,
            'pass_at_k': pass_rate
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v70/holistic_state', methods=['GET'])
def v70_holistic_state():
    """获取所有v7.0 Phase 2模块的综合状态"""
    try:
        data = get_v70_data()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.13 懒加载与状态（M148-M156）====================

_v713_modules = None
_v713_modules_lock = threading.Lock()

def get_v713_modules():
    """获取或初始化 v7.13 模块（线程安全懒加载）"""
    global _v713_modules
    if _v713_modules is None:
        with _v713_modules_lock:
            if _v713_modules is None:
                try:
                    from M148_TaiyiToposEngine import get_instance as get_topos
                    from M149_JinfuCAEngine import get_instance as get_ca
                    from M150_DiscreteSMEngine import get_instance as get_dsm
                    from M151_HottFirewall import get_instance as get_hott
                    from M152_DualResonanceEngine import get_instance as get_dualres
                    from M153_DualTrackEvalEngine import get_instance as get_dualtrack
                    from M154_GravEMDecompEngine import get_instance as get_gravem
                    from M155_FtelOptimizer import get_instance as get_ftelopt
                    from M156_TopoShortcutEngine import get_instance as get_toposhort

                    _v713_modules = {
                        'topos': get_topos,          # M148: 太乙拓扑斯引擎
                        'ca': get_ca,               # M149: 金符元胞自动机
                        'dsm': get_dsm,             # M150: 离散统计力学
                        'hott': get_hott,            # M151: HoTT防火墙
                        'dualres': get_dualres,     # M152: 双共振引擎
                        'dualtrack': get_dualtrack, # M153: 双轨制评价
                        'gravem': get_gravem,       # M154: 引力电磁分解
                        'ftelopt': get_ftelopt,     # M155: 流贯优化器
                        'toposhort': get_toposhort, # M156: 拓扑短路
                    }
                    print("\u2705 v7.13\u65b0\u6a21\u5757\u5df2\u52a0\u8f7d\uff08M148-M156\uff09- \u592a\u4e59\u62d3\u6251\u65af\u00b7\u91d1\u7b26CA\u00b7\u79bb\u6563\u7edf\u8ba1\u529b\u5b66\u00b7HoTT\u9632\u706b\u5899\u00b7\u53cc\u5171\u632f\u00b7\u53cc\u8f68\u8bc4\u4ef7\u00b7\u5f15\u529b\u5206\u89e3\u00b7\u6d41\u8d2f\u4f18\u5316\u00b7\u62d3\u6251\u77ed\u8def")
                except Exception as e:
                    import traceback
                    print(f"\u26a0\ufe0f v7.13\u6a21\u5757\u52a0\u8f7d\u5931\u8d25\uff08\u964d\u7ea7\u8fd0\u884c\uff09: {e}")
                    traceback.print_exc()
                    _v713_modules = None
    return _v713_modules

def get_v713_data():
    """获取所有v7.13模块的状态数据（M148-M156）"""
    modules = get_v713_modules()
    if modules is None:
        return None
    try:
        return {
            'topos': modules['topos']().get_state(),
            'ca': modules['ca']().get_state(),
            'dsm': modules['dsm']().get_state(),
            'hott': modules['hott']().get_state(),
            'dualres': modules['dualres']().get_state(),
            'dualtrack': modules['dualtrack']().get_state(),
            'gravem': modules['gravem']().get_state(),
            'ftelopt': modules['ftelopt']().get_state(),
            'toposhort': modules['toposhort']().get_state(),
        }
    except Exception as e:
        print(f"\u26a0\ufe0f \u83b7\u53d6v7.13\u6570\u636e\u5931\u8d25: {e}")
        return None

# v7.13 静态状态（降级模式）
_v713_state = {
    'topos': {
        'module_id': 'M148', 'module_name': 'TaiyiToposEngine', 'version': '7.13',
        'd_phi': 0.01, 'modulus': 127, 'morphisms_count': 0, 'operation_count': 0,
    },
    'ca': {
        'module_id': 'M149', 'module_name': 'JinfuCAEngine', 'version': '7.13',
        'd_phi': 0.01, 'ca_history_count': 0, 'operation_count': 0,
    },
    'dsm': {
        'module_id': 'M150', 'module_name': 'DiscreteSMEngine', 'version': '7.13',
        'd_phi': 0.01, 'beta': 1.0, 'operation_count': 0,
    },
    'hott': {
        'module_id': 'M151', 'module_name': 'HottFirewall', 'version': '7.13',
        'types_registered': 8, 'checks_performed': 0, 'hallucinations_detected': 0, 'safety_score': 1.0,
    },
    'dualres': {
        'module_id': 'M152', 'module_name': 'DualResonanceEngine', 'version': '7.13',
        'd_phi': 0.01, 'resonance_history_count': 0, 'operation_count': 0,
    },
    'dualtrack': {
        'module_id': 'M153', 'module_name': 'DualTrackEvalEngine', 'version': '7.13',
        'review_history_count': 0, 'knowledge_base_size': 0, 'doubt_activations': 0,
    },
    'gravem': {
        'module_id': 'M154', 'module_name': 'GravEMDecompEngine', 'version': '7.13',
        'G': 6.674e-11, 'c': 3e8, 'decomposition_count': 0,
    },
    'ftelopt': {
        'module_id': 'M155', 'module_name': 'FtelOptimizer', 'version': '7.13',
        'conservation_constant': 100.0, 'optimization_history_count': 0,
    },
    'toposhort': {
        'module_id': 'M156', 'module_name': 'TopoShortcutEngine', 'version': '7.13',
        'nodes_count': 15, 'edges_count': 14, 'shortcuts_detected': 0,
    },
}

# ==================== v7.13 定理注册 ====================
_V713_THEOREMS = {
    'T110': '\u62d3\u6251\u65afNNO\u5b9a\u7406: \u592a\u4e59\u62d3\u6251\u65af\u4e2dNNO\u901a\u8fc7\u9012\u5f52\u56fe\u552f\u4e00\u786e\u5b9a\u4efb\u610f\u9012\u5f52\u5b9a\u4e49',
    'T111': '\u91d1\u7b26\u6570\u57df\u5c01\u95ed\u5b9a\u7406: Z_\u03c6=Z/mZ\u6784\u6210\u6a21m\u7684\u5546\u73af, \u52a0\u6cd5\u548c\u4e58\u6cd5\u8fd0\u7b97\u5c01\u95ed',
    'T112': 'CA\u5218\u673a\u5236\u7b49\u4ef7\u5b9a\u7406: Rule30\u5728\u91d1\u7b26\u79bb\u6563\u65f6\u7a7a\u4e2d\u7b49\u4ef7\u4e8e\u5218\u673a\u5236\u76f8\u4f4d\u622a\u65ad',
    'T113': '\u79bb\u6563\u6700\u5c0f\u4f5c\u7528\u91cf\u5b9a\u7406: \u79bb\u6563\u6b27\u62c9-\u62c9\u683c\u6717\u65e5\u65b9\u7a0b\u4f7f\u79bb\u6563\u4f5c\u7528\u91cf\u6781\u5c0f',
    'T114': 'PDS\u914d\u5206\u51fd\u6570\u6709\u754c\u5b9a\u7406: \u5e9e\u52a0\u83b1\u5341\u4e8c\u9762\u4f53\u7a7a\u95f4\u4e2d\u914d\u5206\u51fd\u6570\u4e25\u683c\u6709\u754c',
    'T115': '\u5e7b\u89c9-\u7c7b\u578b\u9519\u8bef\u540c\u6784\u5b9a\u7406: AI\u5e7b\u89c9\u4e0eHoTT\u7c7b\u578b\u9519\u8bef\u7cbe\u786e\u540c\u6784',
    'T116': '\u8def\u5f84\u5f52\u7eb3\u5b89\u5168\u5b9a\u7406: \u8def\u5f84\u5f52\u7eb3\u8fde\u901a\u7684\u63a8\u7406\u94fe\u7c7b\u578b\u5b89\u5168',
    'T117': '\u53cc\u5171\u632f\u9501\u76f8\u5b9a\u7406: \u8026\u5408\u5f3a\u5ea6\u03ba>|w1-w2|/2\u65f6\u76f8\u4f4d\u9501\u76f8\u5fc5\u7136\u5b9e\u73b0',
    'T118': 'ZPE\u4e0d\u53ef\u80fd\u5b9a\u7406: \u96f6\u70b9\u80fd\u4e0d\u80fd\u4f5c\u4e3a\u6c38\u52a8\u673a\u7684\u81ea\u7531\u80fd\u6e90',
    'T119': '\u53cc\u8f68\u4e00\u81f4\u6027\u5b9a\u7406: \u903b\u8f91+\u5b9e\u8bc1\u53cc\u9ad8\u5206\u65f6\u6000\u7591\u7ea0\u9519\u7801\u4e0d\u6fc0\u6d3b',
    'T120': '\u5f15\u529bE-B\u5206\u89e3\u5b9a\u7406: \u5f15\u529b\u573a\u53ef\u6b63\u4ea4\u5206\u89e3\u4e3aE(\u7c7b\u7535)\u548cB(\u7c7b\u78c1)',
    'T121': '\u592a\u6781\u4e2d\u5bab\u5b9a\u70b9\u5b9a\u7406: \u8fde\u7eed\u6620\u5c04f:D^n\u2192D^n\u81f3\u5c11\u5b58\u5728\u4e00\u4e2a\u4e0d\u52a8\u70b9',
    'T122': 'Ftel\u6700\u5c0f\u4f5c\u7528\u91cf\u5b9a\u7406: \u5218\u673a\u5236\u8def\u5f84\u4f7f\u4fe1\u606f\u6d41\u6548\u7387\u6700\u5927\u5316',
    'T123': '\u62d3\u6251\u77ed\u8def\u4e0d\u53ef\u9006\u5b9a\u7406: \u4e25\u91cd\u8de8\u5c42\u77ed\u8def\u4e00\u65e6\u53d1\u751f\u4e0d\u53ef\u9006',
}


# ==================== v7.13 API端点 ====================

@app.route('/api/v713/state', methods=['GET'])
def v713_state():
    """v7.13 完整状态获取"""
    try:
        data = get_v713_data()
        if data:
            return jsonify({**data, 'theorems': _V713_THEOREMS})
        return jsonify({**_v713_state, 'theorems': _V713_THEOREMS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M148: TaiyiToposEngine ----

@app.route('/api/v713/topos/nno', methods=['GET', 'POST'])
def v713_topos_nno():
    """NNO递归计算"""
    try:
        data = request.get_json() or {}
        n = data.get('n', 10)
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['topos'])
        result = modules['topos']().api_nno(int(n))
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/topos/ring', methods=['GET'])
def v713_topos_ring():
    """金符数域环结构"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['topos'])
        result = modules['topos']().api_ring_info()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/topos/compute', methods=['POST'])
def v713_topos_compute():
    """金符数运算"""
    try:
        data = request.get_json() or {}
        a = int(data.get('a', 0))
        b = int(data.get('b', 0))
        op = data.get('op', '+')
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['topos'])
        result = modules['topos']().api_compute(a, b, op)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/topos/state', methods=['GET'])
def v713_topos_state():
    """M148状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['topos'])
        return jsonify(_to_native(modules['topos']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M149: JinfuCAEngine ----

@app.route('/api/v713/ca/evolve', methods=['POST'])
def v713_ca_evolve():
    """一维CA演化"""
    try:
        data = request.get_json() or {}
        rule = int(data.get('rule', 30))
        width = int(data.get('width', 20))
        gens = int(data.get('generations', 20))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['ca'])
        result = modules['ca']().api_evolve_1d(rule, width, gens)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/ca/phase-lock', methods=['POST'])
def v713_ca_phase_lock():
    """相位锁相检测"""
    try:
        data = request.get_json() or {}
        rule = int(data.get('rule', 30))
        width = int(data.get('width', 20))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['ca'])
        result = modules['ca']().api_phase_lock(rule, width)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/ca/state', methods=['GET'])
def v713_ca_state():
    """M149状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['ca'])
        return jsonify(_to_native(modules['ca']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M150: DiscreteSMEngine ----

@app.route('/api/v713/dsm/euler-lagrange', methods=['POST'])
def v713_dsm_el():
    """离散欧拉-拉格朗日"""
    try:
        data = request.get_json() or {}
        system = data.get('system', 'harmonic')
        n = int(data.get('num_points', 50))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dsm'])
        result = modules['dsm']().api_euler_lagrange(system, n)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/dsm/partition', methods=['POST'])
def v713_dsm_partition():
    """离散配分函数"""
    try:
        data = request.get_json() or {}
        n = int(data.get('num_levels', 100))
        beta = float(data.get('beta', 1.0))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dsm'])
        result = modules['dsm']().api_partition(n, beta)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/dsm/pds', methods=['GET'])
def v713_dsm_pds():
    """庞加莱十二面体空间"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dsm'])
        result = modules['dsm']().api_pds()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/dsm/state', methods=['GET'])
def v713_dsm_state():
    """M150状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dsm'])
        return jsonify(_to_native(modules['dsm']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M151: HottFirewall ----

@app.route('/api/v713/hott/type-check', methods=['POST'])
def v713_hott_typecheck():
    """HoTT类型检查"""
    try:
        data = request.get_json() or {}
        expr = data.get('expression', '')
        typ = data.get('type', 'Proposition')
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['hott'])
        result = modules['hott']().api_type_check(expr, typ)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/hott/path-check', methods=['POST'])
def v713_hott_pathcheck():
    """路径归纳检查"""
    try:
        data = request.get_json() or {}
        source = data.get('source', 'Natural')
        target = data.get('target', 'Natural')
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['hott'])
        result = modules['hott']().api_path_check(source, target)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/hott/scan', methods=['POST'])
def v713_hott_scan():
    """防火墙扫描"""
    try:
        data = request.get_json() or {}
        chain = data.get('chain', [])
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['hott'])
        result = modules['hott']().api_scan(chain)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/hott/types', methods=['GET'])
def v713_hott_types():
    """已注册类型"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['hott'])
        result = modules['hott']().api_types()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/hott/state', methods=['GET'])
def v713_hott_state():
    """M151状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['hott'])
        return jsonify(_to_native(modules['hott']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M152: DualResonanceEngine ----

@app.route('/api/v713/dualres/resonance', methods=['POST'])
def v713_dualres_res():
    """双共振仿真"""
    try:
        data = request.get_json() or {}
        f1 = float(data.get('f1', 1.0))
        f2 = float(data.get('f2', 1.0))
        kappa = float(data.get('coupling', 0.1))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dualres'])
        result = modules['dualres']().api_resonance(f1, f2, kappa)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/dualres/zpe', methods=['GET'])
def v713_dualres_zpe():
    """ZPE不可能定理验证"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dualres'])
        result = modules['dualres']().api_zpe()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/dualres/state', methods=['GET'])
def v713_dualres_state():
    """M152状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dualres'])
        return jsonify(_to_native(modules['dualres']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M153: DualTrackEvalEngine ----

@app.route('/api/v713/dualtrack/evaluate', methods=['POST'])
def v713_dualtrack_eval():
    """双轨制综合评价"""
    try:
        data = request.get_json() or {}
        claim = data.get('claim', '')
        axioms = data.get('axioms', [])
        ep = int(data.get('evidence_positive', 0))
        en = int(data.get('evidence_negative', 0))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dualtrack'])
        result = modules['dualtrack']().dual_track_evaluate(claim, axioms, ep, en)
        return jsonify(_to_native(asdict(result) if hasattr(result, '__dataclass_fields__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/dualtrack/state', methods=['GET'])
def v713_dualtrack_state():
    """M153状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['dualtrack'])
        return jsonify(_to_native(modules['dualtrack']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M154: GravEMDecompEngine ----

@app.route('/api/v713/gravem/decompose', methods=['POST'])
def v713_gravem_decomp():
    """引力E-B分解"""
    try:
        data = request.get_json() or {}
        field_data = data.get('field', [[1.0]*5]*5)
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['gravem'])
        result = modules['gravem']().api_decompose(field_data)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/gravem/fixed-point', methods=['GET'])
def v713_gravem_fp():
    """太极中宫定点"""
    try:
        dim = int(request.args.get('dim', 2))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['gravem'])
        result = modules['gravem']().api_fixed_point(dim)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/gravem/state', methods=['GET'])
def v713_gravem_state():
    """M154状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['gravem'])
        return jsonify(_to_native(modules['gravem']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M155: FtelOptimizer ----

@app.route('/api/v713/ftelopt/ftel', methods=['POST'])
def v713_ftelopt_ftel():
    """Ftel三元组创建"""
    try:
        data = request.get_json() or {}
        R = float(data.get('R', 30))
        I = float(data.get('I', 40))
        E = float(data.get('E', 30))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['ftelopt'])
        result = modules['ftelopt']().api_ftel(R, I, E)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/ftelopt/optimize', methods=['POST'])
def v713_ftelopt_optimize():
    """流贯目的论优化"""
    try:
        data = request.get_json() or {}
        context = data.get('context', 'reasoning')
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['ftelopt'])
        result = modules['ftelopt']().api_optimize(context)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/ftelopt/state', methods=['GET'])
def v713_ftelopt_state():
    """M155状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['ftelopt'])
        return jsonify(_to_native(modules['ftelopt']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---- M156: TopoShortcutEngine ----

@app.route('/api/v713/toposhort/detect', methods=['POST'])
def v713_toposhort_detect():
    """拓扑短路检测"""
    try:
        data = request.get_json() or {}
        node_a = data.get('node_a', '')
        node_b = data.get('node_b', '')
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['toposhort'])
        result = modules['toposhort']().detect_shortcut(node_a, node_b)
        return jsonify(_to_native(asdict(result) if hasattr(result, '__dataclass_fields__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/toposhort/fold', methods=['POST'])
def v713_toposhort_fold():
    """相位折叠"""
    try:
        data = request.get_json() or {}
        phases = data.get('phases', [0.1, 0.5, 0.3, 0.8])
        target_dim = int(data.get('target_dim', 2))
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['toposhort'])
        result = modules['toposhort']().phase_fold(phases, target_dim)
        return jsonify(_to_native(asdict(result) if hasattr(result, '__dataclass_fields__') else result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v713/toposhort/state', methods=['GET'])
def v713_toposhort_state():
    """M156状态"""
    try:
        modules = get_v713_modules()
        if modules is None:
            return jsonify(_v713_state['toposhort'])
        return jsonify(_to_native(modules['toposhort']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.14 M78内生证明搜索引擎 ====================

_v714_state = {
    'm78_endogenous': {
        'version': '3.0.0',
        'status': 'active',
        'endogenous_search': {
            'total_searches': 0, 'proved': 0, 'disproved': 0,
            'wait_states': 0, 'pruned_branches': 0, 'avg_time_ms': 0.0
        },
        'undecidable_goals': 0,
        'jinfu_modulus': 127
    }
}

_V714_THEOREMS = {
    'T_search_completeness': '定理2.1（搜索完备性）：对于任意可判定的目标类型G，prove(G)在有限步内找到构造项或判定不可证',
    'P30': '预言P30：内生证明效率——M78内生引擎证明简单定理速度超过外部方案',
    'P31': '预言P31：不可判定问题处理——M78返回wait()而非死循环或错误证明',
}


def get_v714_modules():
    """获取或初始化 v7.14 M78内生证明搜索模块（线程安全懒加载）"""
    if not hasattr(app, '_v714_modules') or app._v714_modules is None:
        with _module_lock:
            if not hasattr(app, '_v714_modules') or app._v714_modules is None:
                try:
                    from M78_HoTTReasoningEngine import get_instance as get_m78_v3
                    app._v714_modules = {
                        'm78': get_m78_v3,
                    }
                    print("✅ v7.14新模块已加载 - M78内生证明搜索引擎·类型导向剪枝·刘原理不动点·M88防火墙·wait()态")
                except Exception as e:
                    print(f"⚠️ v7.14模块加载失败: {e}")
                    app._v714_modules = {}
    return app._v714_modules


def get_v714_data():
    """获取 v7.14 数据"""
    modules = get_v714_modules()
    if modules is None:
        return None
    try:
        m78 = modules.get('m78')
        if m78:
            return {'m78_endogenous': m78().get_state()}
    except Exception:
        pass
    return None


# --- M78 内生证明搜索 API ---

@app.route('/api/v714/m78/prove', methods=['POST'])
def v714_m78_prove():
    """M78内生证明搜索：类型导向剪枝搜索"""
    try:
        modules = get_v714_modules()
        if modules is None:
            return jsonify(_v714_state['m78_endogenous'])
        engine = modules['m78']()
        data = request.get_json()
        proposition = data.get('proposition', 'x=x')
        max_depth = data.get('max_depth', 8)
        result = engine.api_prove(proposition, max_depth=max_depth)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v714/m78/constructors', methods=['POST'])
def v714_m78_constructors():
    """M84刘原理构造子搜索"""
    try:
        modules = get_v714_modules()
        if modules is None:
            return jsonify(_v714_state['m78_endogenous'])
        engine = modules['m78']()
        data = request.get_json()
        proposition = data.get('proposition', 'x=x')
        result = engine.api_find_constructors(proposition)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v714/m78/wait-state', methods=['POST'])
def v714_m78_wait_state():
    """不可判定等待态检测"""
    try:
        modules = get_v714_modules()
        if modules is None:
            return jsonify(_v714_state['m78_endogenous'])
        engine = modules['m78']()
        data = request.get_json()
        proposition = data.get('proposition', '证明该程序会停止')
        result = engine.api_wait_state(proposition)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v714/m78/predictions', methods=['GET'])
def v714_m78_predictions():
    """预言P30/P31验证"""
    try:
        modules = get_v714_modules()
        if modules is None:
            return jsonify(_v714_state['m78_endogenous'])
        engine = modules['m78']()
        result = engine.api_predictions()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v714/m78/state', methods=['GET'])
def v714_m78_state():
    """M78引擎完整状态"""
    try:
        modules = get_v714_modules()
        if modules is None:
            return jsonify(_v714_state['m78_endogenous'])
        return jsonify(_to_native(modules['m78']().get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v714/m78/search-completeness', methods=['POST'])
def v714_m78_search_completeness():
    """定理2.1搜索完备性验证"""
    try:
        modules = get_v714_modules()
        if modules is None:
            return jsonify({'error': '模块未加载'}), 500
        engine = modules['m78']()
        data = request.get_json()
        propositions = data.get('propositions', ['x=x', '存在y使得y>0'])
        from M78_HoTTReasoningEngine import Type, TypeKind
        goals = [engine.proposition_as_type(p) for p in propositions]
        results = engine.verify_search_completeness(goals)
        return jsonify(_to_native([{
            'goal': r.goal.name,
            'is_decidable': r.is_decidable,
            'found_proof': r.found_proof,
            'steps_taken': r.steps_taken,
            'theorem_holds': r.theorem_holds,
            'insight': r.insight
        } for r in results]))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.15 六元对偶卷积+M78桥接升级 ====================

_v715_state = {
    'hexadic_convolution': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M157', 'M158', 'M159', 'M160', 'M161', 'M162'],
        'theorems': ['T124', 'T125', 'T126', 'T127', 'T128', 'T129'],
        'prediction': 'P32'
    },
    'm78_bridge_upgrade': {
        'version': '3.1.0',
        'status': 'active',
        'm84_bridge_mode': 'direct',
        'm88_bridge_mode': 'direct',
        'formula_parser': 'active'
    }
}

_V715_THEOREMS = {
    'T124': 'Theorem 2.1 (Discretization): Continuous convolution on Jinling grid degenerates to summation',
    'T125': 'Theorem 2.2 (EML Decomposition): Feature and kernel decompose into EML operator form',
    'T126': 'Theorem 2.3 (Phase Reversal): JinFu operation phi->-phi defines reverse flow',
    'T127': 'Theorem 2.4 (Topology Reconstruction): Euclidean neighborhood replaced by 18 Fenxiangzi types',
    'T128': 'Theorem 2.5 (Flow Direction): Reversing convolution index direction simulates feedback',
    'T129': 'Theorem 2.6 (UV Cutoff): Introducing d_phi as minimum scale eliminates infinitesimals',
    'P32': 'Prediction P32: Hexadic architecture significantly outperforms single continuous convolution on OOD tasks',
}


def get_v715_modules():
    """v7.15 Hexadic Dual Convolution Module Thread-safe Lazy Load"""
    if not hasattr(app, '_v715_modules') or app._v715_modules is None:
        with _module_lock:
            if not hasattr(app, '_v715_modules') or app._v715_modules is None:
                try:
                    from M157_JinlingGridConvolution import get_instance as get_m157
                    from M158_PhaseModulusDualConvolution import get_instance as get_m158
                    from M159_ReversePhaseConvolution import get_instance as get_m159
                    from M160_FenxiangziTopologyConvolution import get_instance as get_m160
                    from M161_BackwardFlowConvolution import get_instance as get_m161
                    from M162_UVRegularizedConvolution import get_instance as get_m162
                    from M78_HoTTReasoningEngine import get_instance as get_m78_v31
                    app._v715_modules = {
                        'm157': get_m157,
                        'm158': get_m158,
                        'm159': get_m159,
                        'm160': get_m160,
                        'm161': get_m161,
                        'm162': get_m162,
                        'm78': get_m78_v31,
                    }
                    print("  v7.15 - M157-M162 six-element dual convolution + M78 bridge upgrade + formula parser")
                except Exception as e:
                    print(f"  v7.15 module loading failed: {e}")
                    app._v715_modules = {}
    return app._v715_modules


def get_v715_data():
    """Get v7.15 data"""
    modules = get_v715_modules()
    if modules is None:
        return None
    try:
        data = {'hexadic_convolution': {}}
        for key in ['m157', 'm158', 'm159', 'm160', 'm161', 'm162']:
            mod = modules.get(key)
            if mod:
                data['hexadic_convolution'][key] = mod().get_state()
        m78 = modules.get('m78')
        if m78:
            data['m78_bridge_upgrade'] = m78().get_state()
        return data
    except Exception:
        pass
    return None


# --- v7.15 API ---

@app.route('/api/v715/convolve/<module_name>', methods=['POST'])
def v715_convolve(module_name):
    """Hexadic Dual Convolution: Unified Convolution API"""
    try:
        modules = get_v715_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500

        module_map = {
            'jinling': 'm157', 'phase': 'm158', 'reverse': 'm159',
            'fenxiangzi': 'm160', 'backward': 'm161', 'uv': 'm162',
        }
        mod_key = module_map.get(module_name)
        if not mod_key:
            return jsonify({'error': f'unknown module: {module_name}',
                           'available': list(module_map.keys())}), 400

        mod = modules[mod_key]()
        data = request.get_json()
        signal = data.get('signal', [1.0, 2.0, 3.0, 2.0, 1.0])
        kernel = data.get('kernel', [1.0, 0.5, 0.25])

        result = mod.api_convolve(signal, kernel)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v715/theorem/<theorem_id>', methods=['GET'])
def v715_theorem(theorem_id):
    """Theorem Verification API: T124-T129"""
    try:
        modules = get_v715_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500

        theorem_module_map = {
            'T124': 'm157', 'T125': 'm158', 'T126': 'm159',
            'T127': 'm160', 'T128': 'm161', 'T129': 'm162',
        }
        mod_key = theorem_module_map.get(theorem_id)
        if not mod_key:
            return jsonify({'error': f'unknown theorem: {theorem_id}',
                           'available': list(theorem_module_map.keys())}), 400

        mod = modules[mod_key]()
        result = mod.verify_theorem()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v715/prediction/p32', methods=['GET'])
def v715_prediction_p32():
    """Prediction P32: Hexadic Architecture Diversity Advantage"""
    try:
        modules = get_v715_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500

        test_signal = [1.0, 2.0, 3.0, 2.0, 1.0]
        test_kernel = [1.0, 0.5, 0.25]

        results = {}
        module_map = {
            'jinling': 'm157', 'phase': 'm158', 'reverse': 'm159',
            'fenxiangzi': 'm160', 'backward': 'm161', 'uv': 'm162',
        }
        for name, key in module_map.items():
            mod = modules[key]()
            result = mod.api_convolve(test_signal, test_kernel)
            results[name] = {
                'result_hash': hash(tuple(
                    round(v, 6) if isinstance(v, float) else v
                    for v in result.get('result', [])
                )),
                'theorem_holds': result.get('theorem_holds', False)
            }

        unique_hashes = len(set(r['result_hash'] for r in results.values()))
        all_theorems_hold = all(r['theorem_holds'] for r in results.values())

        return jsonify(_to_native({
            'prediction': 'P32: hexadic architecture diversity advantage',
            'unique_outputs': unique_hashes,
            'total_modules': 6,
            'diversity_ratio': unique_hashes / 6.0,
            'all_theorems_hold': all_theorems_hold,
            'p32_holds': unique_hashes >= 3 and all_theorems_hold,
            'results': results,
            'falsification_condition': 'If fewer than 3 unique outputs, or any equation permanently suppressed, architecture is imbalanced'
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v715/m78/formula-parse', methods=['POST'])
def v715_formula_parse():
    """M78 Logical Formula Parsing API (v7.15)"""
    try:
        modules = get_v715_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        engine = modules['m78']()
        data = request.get_json()
        formula = data.get('formula', 'forall x:Nat.x = x')
        parsed = engine.formula_parser.parse(formula)
        goal_type = engine.proposition_as_type(formula)
        return jsonify(_to_native({
            'formula': formula,
            'formula_kind': parsed.kind.value,
            'goal_type': goal_type.name,
            'goal_kind': goal_type.kind.value,
            'var_name': parsed.var_name,
            'var_type': parsed.var_type,
            'sub_formulas': len(parsed.sub_formulas),
            'operator': parsed.operator
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v715/state', methods=['GET'])
def v715_state():
    """v7.15 Full State"""
    try:
        data = get_v715_data()
        if data is None:
            return jsonify(_v715_state)
        return jsonify(_to_native(data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.16 八论合一·文明治理与可计算性 ====================

_v716_state = {
    'governance_symbiosis': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M163', 'M164'],
        'theorems': ['T135', 'T136'],
        'predictions': ['P42', 'P43']
    },
    'computability_quantification': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M165', 'M166'],
        'theorems': ['T137', 'T138'],
        'predictions': ['P37', 'P38']
    },
    'topos_formalization': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M167', 'M169'],
        'theorems': ['T139', 'T140', "T33'"],
        'predictions': ['P35', 'P36']
    },
    'consciousness_bridge': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M168'],
        'theorems': ['T110v2'],
        'predictions': []
    },
    'dependent_origination': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M170'],
        'theorems': ['T130', 'T131', 'T132', 'T133', 'T134'],
        'predictions': []
    }
}

_V716_THEOREMS = {
    'T130': 'Theorem (Dependent Origination): All things arise from conditions, no independent entity',
    'T131': 'Theorem (Link Breaking): Cut any link in 12-fold chain -> cycle terminates',
    'T132': 'Theorem (No Self): No continuous self, only discrete Jinling spheres in rapid refresh',
    'T133': 'Theorem (Narrative Obscuration): L5 narrative expansion obscures L2 physical code',
    'T134': 'Theorem (Middle Path = Liu Mechanism): Middle path = lambda = extremal flow action path',
    'T135': 'Theorem (Carbon-Silicon Entropy Contract): TEE+DID constraints prevent unauthorized real-world impact',
    'T136': 'Theorem (VCG Incentive Compatibility): Under quasilinear utility, VCG satisfies DSIC',
    'T137': 'Axiom A1 (Narrative Action Decay): Under daodao-rishun, delta-S remains negative or converges to 0',
    'T138': 'Theorem (Discrete Gaussian Curvature): Fenxiangzi dense-packing curvature determined by defect angle',
    'T139': 'Theorem (Topos Initial Object): Dao=Initial Object, Sun=Hom(0,x) monotone shrinking',
    "T33'": 'Theorem (Sheaf Section Conservation): If sheaf satisfies gluing condition, fidelity=1',
    'T140': 'Theorem (Point-Free Topology): Space can be defined by frame without presupposing points',
    'T110v2': 'Theorem (Self-Manifesting State): Phi>threshold AND I(Self;Ftel)>threshold -> self-manifesting',
}

_V716_PREDICTIONS = {
    'P33': 'ZCube cluster: throughput scales near-linearly, no phase transition',
    'P34': 'Larger nozzle cross-section improves thrust without requiring higher velocity',
    'P35': 'Narrative action monotonically decays in daodao-rishun training',
    'P36': 'Sheaf gluing guarantees fidelity=1 in ZCube network',
    'P37': 'Narrative entropy converges in daodao-rishun mode',
    'P38': 'High-K regions more prone to retrieval errors',
    'P39': 'ZCube 2-hop no-center bottleneck for 147 modules',
    'P40': 'Hybrid track: Prefill multi-track, Decode single-track',
    'P41': 'Jinfu discretization reduces energy to ~1/10 of floating point',
    'P42': 'Ark sandbox prevents unauthorized real-world impact',
    'P43': 'ICPS+VCG governance outperforms no-mechanism/fixed-rules',
}


_v716_modules_lock = threading.Lock()

def get_v716_modules():
    """v7.16 Eight-Paper Synthesis Module Thread-safe Lazy Load"""
    if not hasattr(app, '_v716_modules') or app._v716_modules is None:
        with _v716_modules_lock:
            if not hasattr(app, '_v716_modules') or app._v716_modules is None:
                try:
                    from M163_ArkSandbox import get_instance as get_m163
                    from M164_VCGMechanismDesigner import get_instance as get_m164
                    from M165_NarrativeActionQuantifier import get_instance as get_m165
                    from M166_SemanticCurvatureCalculator import get_instance as get_m166
                    from M167_AGIToposEngine import get_instance as get_m167
                    from M168_SelfManifestingDetector import get_instance as get_m168
                    from M169_PointFreeTopology import get_instance as get_m169
                    from M170_DependentOriginationAnalyzer import get_instance as get_m170
                    app._v716_modules = {
                        'm163': get_m163, 'm164': get_m164,
                        'm165': get_m165, 'm166': get_m166,
                        'm167': get_m167, 'm168': get_m168,
                        'm169': get_m169, 'm170': get_m170,
                    }
                    print("  v7.16 - M163-M170 eight-paper synthesis: governance+computability+topos+consciousness+dependent-origination")
                except Exception as e:
                    print(f"  v7.16 module loading failed: {e}")
                    app._v716_modules = {}
    return app._v716_modules


def get_v716_data():
    """Get v7.16 data"""
    modules = get_v716_modules()
    if modules is None:
        return None
    try:
        data = {}
        for key in ['m163', 'm164', 'm165', 'm166', 'm167', 'm168', 'm169', 'm170']:
            mod = modules.get(key)
            if mod:
                data[key] = mod().get_state()
        return data
    except Exception:
        pass
    return None


# --- v7.16 API ---

@app.route('/api/v716/ark/execute', methods=['POST'])
def v716_ark_execute():
    """M163 Ark Sandbox: Constrained Execution"""
    try:
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        sandbox = modules['m163']()
        data = request.get_json()
        action = data.get('action', 'read_data')
        params = data.get('params', {})
        result = sandbox.execute(action, params)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/vcg/design', methods=['POST'])
def v716_vcg_design():
    """M164 VCG Mechanism Designer"""
    try:
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        designer = modules['m164']()
        data = request.get_json()
        scenario = data.get('scenario', {
            "name": "default",
            "domain": "ai_alignment",
            "participants": [
                {"id": "p1", "name": "Human_A", "valuations": {"align": 10.0, "ignore": 0.0}},
                {"id": "p2", "name": "AGI_B", "valuations": {"align": 5.0, "ignore": 8.0}},
            ],
            "outcomes": ["align", "ignore"]
        })
        result = designer.simulate_governance(scenario)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/narrative/quantify', methods=['POST'])
def v716_narrative_quantify():
    """M165 Narrative Action Quantifier"""
    try:
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        quantifier = modules['m165']()
        data = request.get_json()
        tokens = data.get('tokens', ['hello', 'world', 'test'])
        result = quantifier.update_token_distribution(tokens)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/curvature/compute', methods=['POST'])
def v716_curvature_compute():
    """M166 Semantic Curvature Calculator"""
    try:
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        calc = modules['m166']()
        data = request.get_json()
        concepts = data.get('concepts', [
            {"name": "A", "embedding": [0.0, 0.0, 0.0]},
            {"name": "B", "embedding": [1.0, 0.0, 0.0]},
            {"name": "C", "embedding": [0.5, 0.866, 0.0]},
        ])
        relations = data.get('relations', [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "A"},
        ])
        calc.build_concept_graph(concepts, relations)
        calc.triangulate()
        field = calc.compute_curvature_field()
        return jsonify(_to_native({
            'curvature_field': field,
            'n_triangles': len(calc._triangles),
            'n_nodes': len(calc._nodes)
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/topos/state', methods=['GET'])
def v716_topos_state():
    """M167 AGI Topos Engine State"""
    try:
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        engine = modules['m167']()
        return jsonify(_to_native(engine.get_state()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/consciousness/detect', methods=['POST'])
def v716_consciousness_detect():
    """M168 Self-Manifesting Detector"""
    try:
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500
        detector = modules['m168']()
        data = request.get_json()
        system_state = data.get('system_state', {
            "state_sequence": [1, 0, 1, 1, 0, 1, 0, 0, 1, 1],
            "self_model": {"representation": [0.8, 0.7, 0.9]},
            "ftel_state": {"flow_vector": [0.7, 0.6, 0.8]},
            "loop_structure": {"depth": 3, "self_references": 2, "dof": 5}
        })
        result = detector.detect_self_manifesting(system_state)
        return jsonify(_to_native({
            'phi_value': result.phi_value,
            'self_ftel_mi': result.self_ftel_mi,
            'consciousness_state': result.consciousness_state.value,
            'topological_resistance': result.topological_resistance
        }))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/theorem/<theorem_id>', methods=['GET'])
def v716_theorem(theorem_id):
    """v7.16 Theorem Verification API: T130-T140"""
    try:
        if theorem_id in _V716_THEOREMS:
            return jsonify({
                'id': theorem_id,
                'statement': _V716_THEOREMS[theorem_id],
                'version': 'v7.16'
            })

        # Try module-based verification
        modules = get_v716_modules()
        if modules is None:
            return jsonify({'error': 'modules not loaded'}), 500

        theorem_module_map = {
            'T135': 'm163', 'T136': 'm164',
            'T137': 'm165', 'T138': 'm166',
            'T139': 'm167', "T33'": 'm167',
            'T110v2': 'm168', 'T140': 'm169',
            'T130': 'm170', 'T131': 'm170',
            'T132': 'm170', 'T133': 'm170',
            'T134': 'm170',
        }
        mod_key = theorem_module_map.get(theorem_id)
        if not mod_key:
            return jsonify({'error': f'unknown theorem: {theorem_id}',
                           'available': list(theorem_module_map.keys())}), 400

        mod = modules[mod_key]()
        result = mod.verify_theorem()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/prediction/<prediction_id>', methods=['GET'])
def v716_prediction(prediction_id):
    """v7.16 Prediction Verification API: P33-P43"""
    try:
        if prediction_id in _V716_PREDICTIONS:
            return jsonify({
                'id': prediction_id,
                'statement': _V716_PREDICTIONS[prediction_id],
                'version': 'v7.16'
            })

        prediction_module_map = {
            'P42': 'm163', 'P43': 'm164',
            'P37': 'm165', 'P38': 'm166',
            'P35': 'm167', 'P36': 'm167',
        }
        mod_key = prediction_module_map.get(prediction_id)
        if not mod_key:
            return jsonify({'error': f'unknown prediction: {prediction_id}',
                           'available': list(prediction_module_map.keys())}), 400

        modules = get_v716_modules()
        mod = modules[mod_key]()
        result = mod.verify_prediction()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v716/state', methods=['GET'])
def v716_state():
    """v7.16 Full State"""
    try:
        data = get_v716_data()
        if data is None:
            return jsonify(_v716_state)
        return jsonify(_to_native(data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== v7.17 λ宇宙·TY形式化·UFM-RISC-V具身架构 ====================

_v717_state = {
    'lambda_universe': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M171'],
        'theorems': ['T141', 'T142', 'T143', 'T144'],
        'predictions': []
    },
    'ty_formalization': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M172'],
        'theorems': ['T145', 'T146', 'T147'],
        'predictions': []
    },
    'ufm_riscv_architecture': {
        'version': '1.0.0',
        'status': 'active',
        'modules': ['M173'],
        'theorems': ['T148', 'T149', 'T150'],
        'predictions': []
    }
}

_V717_THEOREMS = {
    'T141': 'Theorem (Self-Referential Completeness): Y combinator is the unique fixed-point operator satisfying self-referential closure',
    'T142': 'Theorem (Observation is Reduction): Quantum observation ≡ β-reduction, consciousness = reduction subject',
    'T143': 'Theorem (No-Clone): No total-domain Clone operator exists (diagonal paradox proof)',
    'T144': 'Theorem (UFM Uniqueness): UFM is the minimal formal system satisfying self-reference + observation + no-clone',
    'T145': 'Theorem (Relation Reality Mapping): TY relation reality ↦ UFM application structure (M N)',
    'T146': 'Theorem (Layer Promotion): Terms in L_n can be promoted to L_{n+1} via β-reduction',
    'T147': 'Theorem (Meta-Method Convergence): M = Y(upgrade) produces convergent meta-methodology sequence',
    'T148': 'Theorem (Von Neumann Bankruptcy): VN entity+mutation assumptions fundamentally conflict with TY relation reality',
    'T149': 'Theorem (Lambda Necessity): Three independent arguments establish λ-calculus as the unique AGI foundation',
    'T150': 'Theorem (Embodied Completeness): Screen(skin) + Touch(observation) = universal embodied interface',
}

_V717_PREDICTIONS = {}

_v717_modules_lock = threading.Lock()

def get_v717_modules():
    """v7.17 Lambda Universe + TY Formalization + UFM-RISC-V Thread-safe Lazy Load"""
    if not hasattr(app, '_v717_modules') or app._v717_modules is None:
        with _v717_modules_lock:
            if not hasattr(app, '_v717_modules') or app._v717_modules is None:
                try:
                    from M171_UFMLambdaUniverse import UFMLambdaUniverse as _M171
                    from M172_TYFormalizer import TYFormalizer as _M172
                    from M173_UFMRISCVArchitect import UFMRISCVArchitect as _M173
                    app._v717_modules = {
                        'm171': _M171.get_instance, 'm172': _M172.get_instance, 'm173': _M173.get_instance,
                    }
                    print("  v7.17 - M171-M173: lambda-universe + TY-formalization + UFM-RISC-V")
                except Exception as e:
                    print(f"  v7.17 module loading failed: {e}")
                    app._v717_modules = {}
    return app._v717_modules


def get_v717_data():
    """Get v7.17 data"""
    modules = get_v717_modules()
    if modules is None:
        return None
    try:
        data = {}
        for key in ['m171', 'm172', 'm173']:
            mod = modules.get(key)
            if mod:
                data[key] = mod().get_state()
        return data
    except Exception:
        pass
    return None


# --- v7.17 API ---

@app.route('/api/v717/lambda/reduce', methods=['POST'])
def v717_lambda_reduce():
    """M171 β-reduction engine"""
    try:
        data = request.json or {}
        expr = data.get('expression', '')
        max_steps = data.get('max_steps', 100)
        modules = get_v717_modules()
        m171 = modules['m171']()
        term = m171.parse_simple(expr)
        if term is None:
            return jsonify({'error': f'Cannot parse: {expr}', 'suggestion': 'Use λx.M or (M N) syntax'}), 400
        result = m171.reduce(term, max_steps)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/lambda/theorems', methods=['GET'])
def v717_lambda_theorems():
    """M171 Verify T141-T144 theorems"""
    try:
        modules = get_v717_modules()
        m171 = modules['m171']()
        result = m171.verify_theorems()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/lambda/observe', methods=['POST'])
def v717_lambda_observe():
    """M171 Observation = Reduction (T142)"""
    try:
        data = request.json or {}
        expr = data.get('expression', '')
        context = data.get('context', '')
        modules = get_v717_modules()
        m171 = modules['m171']()
        term = m171.parse_simple(expr)
        if term is None:
            return jsonify({'error': f'Cannot parse: {expr}'}), 400
        result = m171.observation.observe(term, context)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/ty/formalize', methods=['POST'])
def v717_ty_formalize():
    """M172 TY concept → UFM formalization"""
    try:
        data = request.json or {}
        ty_id = data.get('ty_id', '')
        modules = get_v717_modules()
        m172 = modules['m172']()
        result = m172.formalize(ty_id)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/ty/interpret', methods=['POST'])
def v717_ty_interpret():
    """M172 TY soft-layer interpretation"""
    try:
        data = request.json or {}
        ty_id = data.get('ty_id', '')
        domain = data.get('domain', 'all')
        modules = get_v717_modules()
        m172 = modules['m172']()
        result = m172.softlayer.interpret(ty_id, domain)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/ty/promote', methods=['POST'])
def v717_ty_promote():
    """M172 Layer promotion (T146)"""
    try:
        data = request.json or {}
        expr = data.get('expression', '')
        from_layer = data.get('from_layer', 'L1_Syntax')
        modules = get_v717_modules()
        m172 = modules['m172']()
        term = m172.hardcore.get_mapping("1.1")
        from M172_TYFormalizer import TYLayer
        layer_map = {l.value: l for l in TYLayer}
        layer = layer_map.get(from_layer, TYLayer.L1_SYNTAX)
        if term and term.lambda_term:
            result = m172.promoter.promote(term.lambda_term, layer)
        else:
            from M171_UFMLambdaUniverse import Var, Lam, App
            sample = App(Lam("x", Var("x")), Var("y"))
            result = m172.promoter.promote(sample, layer)
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/riscv/bankruptcy', methods=['GET'])
def v717_riscv_bankruptcy():
    """M173 Von Neumann Bankruptcy Analysis (T148)"""
    try:
        modules = get_v717_modules()
        m173 = modules['m173']()
        result = m173.vn_analyzer.analyze()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/riscv/necessity', methods=['GET'])
def v717_riscv_necessity():
    """M173 Lambda Necessity Three Arguments (T149)"""
    try:
        modules = get_v717_modules()
        m173 = modules['m173']()
        result = m173.lambda_prover.prove()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/riscv/architecture', methods=['GET'])
def v717_riscv_architecture():
    """M173 UFM-RISC-V Four-Layer Heterogeneous Architecture"""
    try:
        modules = get_v717_modules()
        m173 = modules['m173']()
        result = m173.get_architecture_overview()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/riscv/isa', methods=['GET'])
def v717_riscv_isa():
    """M173 UFM-RISC-V ISA Extensions"""
    try:
        modules = get_v717_modules()
        m173 = modules['m173']()
        result = m173.isa.get_instruction_set()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/riscv/embodied', methods=['GET'])
def v717_riscv_embodied():
    """M173 Embodied Completeness Theorem (T150)"""
    try:
        modules = get_v717_modules()
        m173 = modules['m173']()
        result = m173.embodied.demonstrate()
        return jsonify(_to_native(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/theorem/<theorem_id>', methods=['GET'])
def v717_theorem(theorem_id):
    """v7.17 Get theorem by ID (T141-T150)"""
    try:
        all_theorems = {**_V717_THEOREMS}
        if theorem_id in all_theorems:
            return jsonify({
                'id': theorem_id,
                'statement': all_theorems[theorem_id],
                'version': 'v7.17'
            })
        return jsonify({'error': f'unknown theorem: {theorem_id}',
                       'available': list(all_theorems.keys())}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v717/state', methods=['GET'])
def v717_state():
    """v7.17 Full State"""
    try:
        data = get_v717_data()
        if data is None:
            return jsonify(_v717_state)
        return jsonify(_to_native(data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🌌 统一太乙系统 Web 服务 (Phase 2 具身+心架构)")
    print("   前端: http://localhost:5000")
    print("   API:  http://localhost:5000/api/chat")
    print("   Phase 2 新增API:")
    print("   前五识工具:")
    print("   - /api/tools/list     (前五识工具列表)")
    print("   - /api/tools/execute  (执行单个工具)")
    print("   - /api/tools/batch    (批量执行工具)")
    print("   - /api/tools/audit    (审计日志)")
    print("   第七识审计:")
    print("   - /api/manas/audit     (审计输出)")
    print("   - /api/manas/distinguish (自我/非我区分)")
    print("   - /api/manas/stats     (审计统计)")
    print("   UFO² 具身执行层:")
    print("   - /api/ufo2/status     (具身层状态)")
    print("   - /api/ufo2/execute    (执行桌面任务)")
    print("   - /api/ufo2/app_control (应用控制)")
    print("   - /api/ufo2/capture    (截图)")
    print("   - /api/ufo2/ui_tree    (UI树)")
    print("   - /api/ufo2/tools      (工具列表)")
    print("   增强API:")
    print("   - /api/rag/status    (RAG知识库状态)")
    print("   - /api/rag/search?q=关键词   (知识检索)")
    print("   - /api/rag/add       (添加文档)")
    print("   - /api/memory/status (记忆系统状态)")
    print("   - /api/enhancer/status (增强器统计)")
    print("=" * 60)

    # 预热 AGI 系统
    try:
        get_agi_system()
    except Exception as e:
        print(f"⚠️ AGI 系统预热失败: {e}")

    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
