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

# 设置 shared_state 的 app 引用
import shared_state
shared_state.set_app(app)


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
    import sys, traceback as tb_mod
    tb_str = ''
    try:
        tb_str = tb_mod.format_exc()
    except:
        pass
    # 安全打印（避免 Windows 控制台编码问题）
    try:
        sys.stderr.write(f"[GLOBAL ERROR] {type(e).__name__}: {str(e)[:200]}\n")
        if tb_str:
            sys.stderr.write(tb_str[-2000:])  # 只打印最后 2000 字符
    except:
        pass
    # 构造安全的可序列化错误响应
    try:
        err_msg = str(e)[:500]
        return jsonify({
            'error': err_msg,
            'trace': tb_str[-3000:] if tb_str else ''
        }), 500
    except:
        # 最后兜底：返回纯文本 500
        return 'Internal Server Error', 500

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
                    from modules.M56_SpiritualEvolutionEngine import get_instance as get_spiritual
                    from modules.M57_TheseusConsciousnessMonitor import get_instance as get_theseus
                    from modules.M58_ArborealSemanticProcessor import get_instance as get_arboreal
                    from modules.M59_ExtremumDecisionOptimizer import get_instance as get_extremum
                    from modules.M60_RelationalReasoningEngine import get_instance as get_relational
                    from modules.M61_MoralInternalizer import get_instance as get_moral
                    from modules.M62_HistoricalNarrativeWeaver import get_instance as get_historical

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
                    from modules.M63_MononumberProcessor import get_instance as get_mono
                    from modules.M64_NarrativeActionEngine import get_instance as get_narrative
                    from modules.M65_ConsciousnessFlowMonitor import get_instance as get_consciousness
                    from modules.M66_SelfIdentityTracker import get_instance as get_identity
                    from modules.M67_EnlightenmentConvergenceVerifier import get_instance as get_enlightenment
                    from modules.M68_RelationalCouplingSemantizer import get_instance as get_coupling
                    from modules.M69_AttractorStabilityAnalyzer import get_instance as get_attractor
                    from modules.M70_FalsifiablePredictionVerifier import get_instance as get_prediction

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
                    from modules.M71_WalletPropertyBoundaryManager import get_instance as get_wallet
                    from modules.M72_ContributionMeasurementEngine import get_instance as get_contribution
                    from modules.M73_SelfReferentialPhiDetector import get_instance as get_phi
                    from modules.M74_CarbonSiliconEntropyContract import get_instance as get_entropy
                    from modules.M75_HumanMachineArkCrypto import get_instance as get_ark
                    from modules.M76_FiveElementTransformEngine import get_instance as get_wuxing
                    from modules.M77_EMLPhaseCouplingZ5 import get_instance as get_eml_coupling
                    from modules.M78_HoTTReasoningEngine import get_instance as get_hott
                    from modules.M79_ConstructiveAGICore import get_instance as get_constructive
                    from modules.M80_WuxingTokenDynamicsCoupler import get_instance as get_token_dynamics
                    # Phase 2: M81-M95 高阶逻辑与范畴论深化
                    from modules.M81_HigherOrderLogicReconstructor import get_instance as get_holr
                    from modules.M82_CategoryHomotopyFormalizer import get_instance as get_chf
                    from modules.M83_DynamicCategoryTheoryReconstructor import get_instance as get_dct
                    from modules.M84_LiuGuanDynamicsGenerator import get_instance as get_liu
                    from modules.M85_DualTrackPersonhoodEngine import get_instance as get_dual
                    from modules.M86_L2TypeKernelCompiler import get_instance as get_l2kernel
                    from modules.M87_EMLDrivenProofSearcher import get_instance as get_proof
                    from modules.M88_TypeCheckFirewall import get_firewall as get_firewall
                    from modules.M89_FteliaryNaturalTransformation import get_fteliary_transformer as get_ftel
                    from modules.M90_SemanticManifoldCurvature import get_curvature_calculator as get_curv
                    from modules.M91_UnivalenceEquivalenceChecker import get_univalence_checker as get_uni
                    from modules.M92_FteliocityFidelityMeasurer import get_fidelity_measurer as get_ftel_fid
                    from modules.M93_DynamicCategoryEvolutionTracker import get_evolution_tracker as get_evo
                    from modules.M94_HolisticDiscreteGovernanceUpgrader import get_hdg_upgrader as get_hdg
                    from modules.M95_ConstructiveAGIEvaluator import get_constructive_evaluator as get_eval

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
                    from modules.agi_medium_symbiosis import AGIMediumSymbiosis
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
                    from modules.CompositeAGI_V2 import CompositeAGI_V2 as TaiyiAGI_V2
                    _agi_system = TaiyiAGI_V2()
                    _agi_ready = True
                    print("✅ Taiyi-AGI 4.0 系统就绪（23模块已加载）")
                except Exception as e:
                    print(f"❌ Taiyi-AGI系统初始化失败: {e}")
                    traceback.print_exc()
                    # 降级：尝试加载旧系统
                    try:
                        print("⚠️ 降级：尝试加载 UnifiedTaiyiSystem...")
                        from modules.unified_taichi_demo import UnifiedTaiyiSystem
                        _agi_system = UnifiedTaiyiSystem("WebAGI")
                        _agi_ready = True
                        print("✅ 降级成功：UnifiedTaiyiSystem 已加载")
                    except Exception as e2:
                        print(f"❌ 降级也失败: {e2}")
                        traceback.print_exc()
                        raise
    return _agi_system


# ==================== API 端点 ====================

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

        # bool 必须在 float 检查之前（bool 是 int 子类，有 __float__ 和 __int__）
        if isinstance(obj, bool):
            return obj

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
        from modules.taiyi_llm_enhancer import get_enhancer
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


# ==================== AGI 12.0 Goal目标模式 ====================
# ==================== 独立脑图数据端点 ====================
# ==================== v6.3 数学完备化 API ====================

# ==================== 增强API（RAG + Memory + Tools） ====================

# ==================== v7.0 API 端点（M71-M80）====================

# === M71-75: 碳硅共生契约 ===
# === M76-80: 五行变换与HoTT ===
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
                    from modules.M106_SelfReferentialLoopMonitor import get_instance as get_srloop
                    from modules.M107_DimensionProjectionProcessor import get_instance as get_dimproj
                    from modules.M108_ChiralSpinorSensor import get_instance as get_chiral
                    from modules.M109_FiniteBoundlessTopologyCompute import get_instance as get_fbtopo
                    from modules.M110_LeastActionTerminator import get_instance as get_leaction

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


# ==================== UFO² 具身执行层 API ====================

def _format_reply(result: dict, original_question: str) -> str:
    """将分析结果格式化为友好回复
    
    直接使用 unified_taichi_demo.py 中 UnifiedTaiyiSystem 的 _format_reply 方法。
    """
    try:
        from modules.unified_taichi_demo import UnifiedTaiyiSystem
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
                    from modules.unified_compound_agi_system import UnifiedCompoundAGISystem
                    _compound_agi_system = UnifiedCompoundAGISystem("CompoundAGI_Web_v1.0")
                    _compound_agi_ready = True
                    print("✅ Taiyi-AGI系统就绪")
                except Exception as e:
                    print(f"❌ Taiyi-AGI系统初始化失败: {e}")
                    traceback.print_exc()
                    raise
    return _compound_agi_system


# ==================== AGI 12.0 新模块 API 端点 ====================

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
                    from modules.M111_ActorDirectorComplex import get_instance as get_actor_director
                    from modules.M112_FlowCutoffOperator import get_instance as get_flow_cutoff
                    from modules.M113_HistoryTraceValidator import get_instance as get_trace_validator

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
                    from modules.M114_UniverseTypeSpace import get_instance as get_universe
                    from modules.M115_CurvatureSectionSearch import get_instance as get_curvature
                    from modules.M116_WaitStateConstructor import get_instance as get_wait

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

# ---- M114: UniverseTypeSpace ----

# ---- M115: CurvatureSectionSearch ----

# ---- M116: WaitStateConstructor ----

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
                    from modules.M117_FtelTeleologicalConstraint import get_instance as get_ftel
                    from modules.M118_CognitiveRecursiveDynamics import get_instance as get_cognitive
                    from modules.M119_LayerFidelityMonitor import get_instance as get_fidelity

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

# ---- M117: FtelTeleologicalConstraint ----

# ---- M118: CognitiveRecursiveDynamics ----

# ---- M119: LayerFidelityMonitor ----

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
                    from modules.M120_GameTheoryEngine import get_instance as get_game
                    from modules.M121_BayesianBeliefUpdater import get_instance as get_bayes
                    from modules.M122_MechanismDesigner import get_instance as get_mech
                    from modules.M123_ICPSSolver import get_instance as get_icps
                    from modules.M124_EmotionGranularityTrainer import get_instance as get_emotion
                    from modules.M125_SandboxCuriosityExplorer import get_instance as get_sandbox

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

# ---- M120: GameTheoryEngine ----

# ---- M121: BayesianBeliefUpdater ----

# ---- M122: MechanismDesigner ----

# ---- M123: ICPSSolver ----

# ---- M124: EmotionGranularityTrainer ----

# ---- M125: SandboxCuriosityExplorer ----

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
                    from modules.M126_GuardrailOrchestrator import get_instance as get_guardrail
                    from modules.M127_SpeculativeReasoner import get_instance as get_speculative
                    from modules.M128_KVCacheGovernor import get_instance as get_kvcache
                    from modules.M129_OntologyAutoForge import get_instance as get_ontology

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

# ---- M126: GuardrailOrchestrator ----

# ---- M127: SpeculativeReasoner ----

# ---- M128: KVCacheGovernor ----

# ---- M129: OntologyAutoForge ----

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
                    from modules.M130_JinFuDiscreteCalculus import get_instance as get_jinfu
                    from modules.M131_RelationActionMinimizer import get_instance as get_action
                    from modules.M132_AdditivePrimeClassifier import get_instance as get_prime
                    from modules.M133_SelfRefLoopTopologizer import get_instance as get_topology

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

# ---- M130: JinFuDiscreteCalculus ----

# ---- M131: RelationActionMinimizer ----

# ---- M132: AdditivePrimeClassifier ----

# ---- M133: SelfRefLoopTopologizer ----

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
                    from modules.M134_EulerPhaseClosureEngine import get_instance as get_euler
                    from modules.M135_RecursiveProofFolder import get_instance as get_proof
                    from modules.M136_FiveLayerOntologyMapper import get_instance as get_ontology
                    from modules.M137_FalsifiablePredictionEngine import get_instance as get_prediction

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

# ---- M134: EulerPhaseClosureEngine ----

# ---- M135: RecursiveProofFolder ----

# ---- M136: FiveLayerOntologyMapper ----

# ---- M137: FalsifiablePredictionEngine ----

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
                    from modules.M138_BipartiteGraphTopologyEngine import get_instance as get_bipartite
                    from modules.M139_RelationalActionRouter import get_instance as get_action
                    from modules.M140_HybridRailPhaseController import get_instance as get_hybrid
                    from modules.M141_TopologicalPhaseTransitionDetector import get_instance as get_phase

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

# ---- M138: BipartiteGraphTopologyEngine ----

# ---- M139: RelationalActionRouter ----

# ---- M140: HybridRailPhaseController ----

# ---- M141: TopologicalPhaseTransitionDetector ----

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
                    from modules.M142_UVRegularizationEngine import get_instance as get_uv
                    from modules.M143_FenxiangziSpaceEngine import get_instance as get_fenxiang
                    from modules.M144_JinfuAccumulationComputer import get_instance as get_accum
                    from modules.M145_YuMappingCognitiveEngine import get_instance as get_yu
                    from modules.M146_DialecticalZeroReasoner import get_instance as get_dzero
                    from modules.M147_SingularityEliminator import get_instance as get_singul

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

# ---- M142: UVRegularizationEngine ----

# ---- M143: FenxiangziSpaceEngine ----

# ---- M144: JinfuAccumulationComputer ----

# ---- M145: YuMappingCognitiveEngine ----

# ---- M146: DialecticalZeroReasoner ----

# ---- M147: SingularityEliminator ----

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
                    from modules.M96_CognitiveOffloadGuard import get_instance as get_cog_guard
                    from modules.M97_SocraticWeaknessDisclosure import get_instance as get_socratic
                    from modules.M98_ConfidenceDisclosure import get_instance as get_confidence
                    from modules.M99_DynamicTaskRouter import get_instance as get_router
                    from modules.M100_RewardHackDetector import get_instance as get_hack_detect
                    from modules.M101_EnvironmentAwareness import get_instance as get_env_aware
                    from modules.M102_LongRangeContext import get_instance as get_long_ctx
                    from modules.M103_CollaborationAssessor import get_instance as get_collab_assess
                    from modules.M104_CollaborationDiagnostics import get_instance as get_collab_diag
                    from modules.M105_FusionVerifier import get_instance as get_fusion_verify

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
                    from modules.M176_OrgMemoryEngine import OrgMemoryEngine as _M176
                    from modules.M177_PhiBudgetSystem import PhiBudgetSystem as _M177
                    from modules.M178_TaiyiAgentOS import TaiyiAgentOS as _M178
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

# --- v7.19 API: M177 PhiBudgetSystem ---

# --- v7.19 API: M178 TaiyiAgentOS ---

# --- v7.19 Theorem & State ---

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
                    from modules.M179_TaiyiInterface import TaiyiInterface as _M179
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


# ==================== v7.22 EqProp+FHN 流贯引擎 ====================

_v722_state = {
    'eqprop_fhn_engine': {
        'version': '1.0.0',
        'status': 'active',
        'description': 'EqProp+FHN L3 Ftel dynamics engine (M180)',
        'theorems': ['T180', 'T181', 'T182'],
        'capacity': {
            'T180': 'EqProp-FHN Value Theorem (local credit assignment)',
            'T181': 'EqProp-FHN Ceiling Theorem (L2 shell deficiency)',
            'T182': 'Compatible Absorption Theorem (L3 sub-engine integration)',
        }
    },
    'l2_shell': {
        'consistency_ok': False,
        'writeback_ok': True,
        'preservation_ok': True,
        'addressability_ok': True,
        'anchorability_ok': True,
        'overall_status': 'partial',
        'missing_attributes': ['Consistency(M88)'],
    },
    'integration': {
        'engine_name': 'EqPropFHN',
        'l3_role': 'Ftel dynamics sub-engine',
        'l2_shell_status': 'partial',
        'local_learning_active': False,
        'total_params': 18,
        'total_neurons': 6,
        'energy_consumption': 0.0,
    }
}

_v722_lock = threading.Lock()
_v722_cache = {}
_v722_cache_ttl = 120


def _run_eqprop_safe(func, cache_key):
    """Safely run EqProp+FHN experiment with caching."""
    now = time.time()
    if cache_key in _v722_cache:
        cached = _v722_cache[cache_key]
        if now - cached['timestamp'] < _v722_cache_ttl:
            return cached['result']
    with _v722_lock:
        try:
            result = func()
            if hasattr(result, '__dict__'):
                result = _to_native(result)
            elif isinstance(result, dict):
                result = _to_native(result)
            _v722_cache[cache_key] = {'result': result, 'timestamp': now}
            return result
        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}


# ==================== v7.23 E2E归约+宇宙音律+自举智能 ====================

_V723_THEOREMS = {
    'T183': 'E2E Captures Knowing How Theorem: 端到端模型在L3流贯层实现了对Knowing How的隐式捕获 (M181)',
    'T184': 'E2E Structural Deficiency Theorem: E2E模型的L2代数壳缺失五项硬化属性 (M181)',
    'T185': 'Taiyi AGI Possibility Theorem: 太乙AGI因L2壳硬化五项属性，跳出AGI不可能判决域 (M181)',
    'T186': 'Natural Number Emergence Theorem: ℕ是IDO对L1流贯Φ归约时由L2壳导出的最小拓扑不变量 (M182)',
    'T187': 'Ontological Boundary Layer Isomorphism Theorem: L2代数壳与Prandtl边界层同构 (M182)',
    'T188': 'AGI Bootstrap Possibility Theorem: L2壳具备三条件则可从纯流贯交互中自举出ℕ⁺ℚ⁺物理定律 (M183)',
}

_v723_state = {
    'e2e_reduction': {
        'version': '1.0.0',
        'status': 'active',
        'description': 'E2E Reduction Engine (M181)',
        'theorems': ['T183', 'T184', 'T185'],
        'capacity': {
            'T183': 'E2E Captures Knowing How Theorem',
            'T184': 'E2E Structural Deficiency Theorem',
            'T185': 'Taiyi AGI Possibility Theorem',
        }
    },
    'cosmic_harmony': {
        'version': '1.0.0',
        'status': 'active',
        'description': 'Cosmic Harmony Engine (M182)',
        'theorems': ['T186', 'T187'],
        'capacity': {
            'T186': 'Natural Number Emergence Theorem',
            'T187': 'Ontological Boundary Layer Isomorphism Theorem',
        }
    },
    'bootstrap_intelligence': {
        'version': '1.0.0',
        'status': 'active',
        'description': 'Bootstrap Intelligence Engine (M183)',
        'theorems': ['T188'],
        'capacity': {
            'T188': 'AGI Bootstrap Possibility Theorem',
        }
    },
    'l2_shell': {
        'consistency_ok': False,
        'writeback_ok': True,
        'preservation_ok': True,
        'addressability_ok': True,
        'anchorability_ok': True,
        'overall_status': 'partial',
        'missing_attributes': ['Consistency(M88)'],
    },
    'p8_mve': {
        'total_experiments': 6,
        'passed': 0,
        'overall_score': '0/6',
        'verdict': 'PENDING',
    }
}

_v723_lock = threading.Lock()
_v723_cache = {}
_v723_cache_ttl = 120


def _run_v723_safe(func, cache_key):
    """Safely run v7.23 experiment with 120s TTL caching."""
    now = time.time()
    if cache_key in _v723_cache:
        cached = _v723_cache[cache_key]
        if now - cached['timestamp'] < _v723_cache_ttl:
            return cached['result']
    with _v723_lock:
        try:
            result = func()
            if hasattr(result, '__dict__'):
                result = _to_native(result)
            elif isinstance(result, dict):
                result = _to_native(result)
            _v723_cache[cache_key] = {'result': result, 'timestamp': now}
            return result
        except Exception as e:
            return {'error': str(e), 'traceback': traceback.format_exc()}


# ---------- v7.23 /api/v723/ 路由 ----------

def _make_p8_result(verify_result, theorem_id):
    """Convert verify_theorem result to P8 MVE format"""
    verified = verify_result.get('verified', False)
    counterexample = verify_result.get('counterexample')
    status = 'PASSED' if verified and not counterexample else 'FAILED'
    return {
        'experiment': f'P8_{theorem_id}',
        'theorem': theorem_id,
        'verified': verified,
        'proof_sketch': verify_result.get('proof_sketch', ''),
        'evidence': verify_result.get('evidence', []),
        'counterexample': counterexample,
        'status': status,
    }


# ============================================================
# v7.24 LLM Wiki 知识引擎 — M184 + T189/T190 + P9 MVE
# 来源：drpang.ai《RAG 之后：LLM Wiki 正在成为个人知识库的新范式》
# ============================================================

_V724_STATE = {
    'wiki_engine': {
        'status': 'active',
        'version': '1.0.0',
        'modules': ['M184'],
        'theorems': ['T189', 'T190'],
        'predictions': [],
    },
    'pages_count': 0,
    'edges_count': 0,
    'verified_pages': 0,
}

_V724_LOCK = threading.Lock()
_V724_ENGINE = None  # 延迟初始化


def _get_v724_engine():
    """获取（延迟初始化的）LLMWikiEngine 实例，自动注入 M176/M178"""
    global _V724_ENGINE
    if _V724_ENGINE is None:
        with _V724_LOCK:
            if _V724_ENGINE is None:
                try:
                    from modules.M184_LLMWikiEngine import LLMWikiEngine, IngestMode, QueryMode
                    _V724_ENGINE = LLMWikiEngine()

                    # --- 对接 M176 OrgMemoryEngine ---
                    try:
                        from modules.M176_OrgMemoryEngine import OrgMemoryEngine
                        org_mem = OrgMemoryEngine.get_instance()
                        _V724_ENGINE.set_org_memory(org_mem)
                        print("[v724] M176 OrgMemoryEngine 已绑定")
                    except Exception as e176:
                        print(f"[v724] M176 绑定跳过: {e176}")

                    # --- 对接 M178 TaiyiAgentOS MessageBus ---
                    try:
                        from modules.M178_TaiyiAgentOS import TaiyiAgentOS
                        agent_os = TaiyiAgentOS.get_instance()
                        _V724_ENGINE.set_agent_os(agent_os)
                        print("[v724] M178 TaiyiAgentOS 已绑定")
                    except Exception as e178:
                        print(f"[v724] M178 绑定跳过: {e178}")

                except Exception as e:
                    print(f"[v724] 初始化失败: {e}")
                    _V724_ENGINE = None
    return _V724_ENGINE


def _run_v724_safe(func, *args, **kwargs):
    """安全执行 v724 引擎方法，捕获异常"""
    try:
        engine = _get_v724_engine()
        if engine is None:
            return {'error': 'LLMWikiEngine 初始化失败', 'verified': False}
        return func(engine, *args, **kwargs)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'verified': False}


# ============================================================
# v7.25 — M185 UnderstandEngine API
# ============================================================

_V725_STATE = {
    'understand_engine': {
        'status': 'active',
        'version': '1.0.0',
        'modules': ['M185'],
        'theorems': ['T191', 'T192', 'T193'],
    },
    'rlm_engine': {
        'status': 'active',
        'version': '1.0.0',
        'modules': ['M186'],
        'total_executions': 0,
    },
    'context_rot': {
        'status': 'active',
        'version': '1.0.0',
        'modules': ['M187'],
        'monitoring': False,
    },
    'intentionality': {
        'status': 'active',
        'version': '1.0.0',
        'modules': ['M188'],
        'theorems': ['T194', 'T195', 'T196'],
    },
    'nodes_count': 0,
    'edges_count': 0,
    'project_name': '',
}

_V725_LOCK = threading.Lock()
_V725_ORCHESTRATOR = None  # 延迟初始化


def _get_v725_orchestrator():
    """获取（延迟初始化的）UnderstandOrchestrator 实例，自动注入 M184 WikiEngine"""
    global _V725_ORCHESTRATOR
    if _V725_ORCHESTRATOR is None:
        with _V725_LOCK:
            if _V725_ORCHESTRATOR is None:
                try:
                    from modules.M185_UnderstandEngine import UnderstandOrchestrator
                    wiki_engine = _get_v724_engine()
                    org_memory = None
                    try:
                        from modules.M176_OrgMemoryEngine import OrgMemoryEngine
                        org_memory = OrgMemoryEngine.get_instance()
                    except Exception:
                        pass
                    _V725_ORCHESTRATOR = UnderstandOrchestrator(
                        wiki_engine=wiki_engine,
                        org_memory=org_memory,
                    )
                    print("[v725] M185 UnderstandOrchestrator 已初始化")
                except Exception as e:
                    print(f"[v725] 初始化失败: {e}")
                    _V725_ORCHESTRATOR = None
    return _V725_ORCHESTRATOR


def _run_v725_safe(func, *args, **kwargs):
    """安全执行 v725 编排器方法"""
    try:
        orchestrator = _get_v725_orchestrator()
        if orchestrator is None:
            return {'error': 'UnderstandOrchestrator 初始化失败'}
        return func(orchestrator, *args, **kwargs)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


# ============================================================
# v7.25-RLM RLM 递归语言模型 (M186)
# ============================================================

def _get_rlm_engine():
    """延迟获取 RLMEngine 单例"""
    try:
        from modules.M186_RLMEngine import get_instance
        return get_instance()
    except Exception as e:
        print(f"[v725-rlm] 加载失败: {e}")
        return None


# ============================================================
# v7.25-Rot Context Rot 检测器 (M187)
# ============================================================

def _get_context_rot_detector():
    """延迟获取 ContextRotDetector 单例"""
    try:
        from modules.M187_ContextRotDetector import get_instance
        return get_instance()
    except Exception as e:
        print(f"[v725-rot] 加载失败: {e}")
        return None


# ============================================================
# v7.25-Int 意向性引擎 (M188)
# ============================================================

def _get_intentionality_engine():
    """延迟获取 IntentionalityEngine 单例"""
    try:
        from modules.M188_IntentionalityEngine import get_instance
        return get_instance()
    except Exception as e:
        print(f"[v725-int] 加载失败: {e}")
        return None


# ============================================================
# v7.25b 幂律·对数·三分损益·类型论面板 (M189 + BFT升级 + M187/M188升级)
# ============================================================

# ============================================================
# v7.26 阿卡西链式数据库 (M190 AkashaChainDB)
# "信息寓于关联，而非实体"
# ============================================================

# ============================================================
# v7.29 M190b AkashaChainDB v2 性能优化
# 分片索引·WAL持久化·布隆过滤器·查询缓存
# ============================================================

# ---- v730: M190c AkashaChainDB v3 UA集成 ----

# ============================================================
# v7.27 太极OS·流锻内核 (M191-M195)
# ============================================================

# --- M191 JinlingSphere 金灵球堆垒引擎 ---

# --- M192 TaijiContinuation 延续/思程 ---

# --- M193 PhiScheduler Φ流贯调度器 ---

# --- M194 CarbonSiliconGAN 碳硅GAN共演引擎 ---

# --- M195 WorldModelSubsystem 世界模型子系统 ---

# ============================================================
# v7.18 沙箱增强·安全护盾
# ============================================================

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

# ═══════════════════════════════════════════
# GC (Governance Coin) 调整 API
# ═══════════════════════════════════════════

import json as _gc_json

_GC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.workbuddy', 'gc_balance.json')

def _gc_load():
    try:
        with open(_GC_FILE, 'r', encoding='utf-8') as f:
            return _gc_json.load(f)
    except:
        return {'balance': 1000, 'history': []}

def _gc_save(data):
    os.makedirs(os.path.dirname(_GC_FILE), exist_ok=True)
    with open(_GC_FILE, 'w', encoding='utf-8') as f:
        _gc_json.dump(data, f, ensure_ascii=False, indent=2)

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
                    from modules.M174_UFMRISCVSandbox import UFMRISCVSandbox as _M174
                    from modules.M175_SafetyShield import SafetyShield as _M175
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

# --- v7.18 API: M175 SafetyShield ---

# --- v7.18 Theorem & State ---

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
            from modules.taiyi_llm_enhancer import get_enhancer, ReasoningMode
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

# ==================== v7.0 Phase 2 API 端点 (M81-M95) ====================

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
                    from modules.M148_TaiyiToposEngine import get_instance as get_topos
                    from modules.M149_JinfuCAEngine import get_instance as get_ca
                    from modules.M150_DiscreteSMEngine import get_instance as get_dsm
                    from modules.M151_HottFirewall import get_instance as get_hott
                    from modules.M152_DualResonanceEngine import get_instance as get_dualres
                    from modules.M153_DualTrackEvalEngine import get_instance as get_dualtrack
                    from modules.M154_GravEMDecompEngine import get_instance as get_gravem
                    from modules.M155_FtelOptimizer import get_instance as get_ftelopt
                    from modules.M156_TopoShortcutEngine import get_instance as get_toposhort

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

# ---- M148: TaiyiToposEngine ----

# ---- M149: JinfuCAEngine ----

# ---- M150: DiscreteSMEngine ----

# ---- M151: HottFirewall ----

# ---- M152: DualResonanceEngine ----

# ---- M153: DualTrackEvalEngine ----

# ---- M154: GravEMDecompEngine ----

# ---- M155: FtelOptimizer ----

# ---- M156: TopoShortcutEngine ----

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


_v714_modules_lock = threading.Lock()

def get_v714_modules():
    """获取或初始化 v7.14 M78内生证明搜索模块（线程安全懒加载）"""
    if not hasattr(app, '_v714_modules') or app._v714_modules is None:
        with _v714_modules_lock:
            if not hasattr(app, '_v714_modules') or app._v714_modules is None:
                try:
                    from modules.M78_HoTTReasoningEngine import get_instance as get_m78_v3
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


_v715_modules_lock = threading.Lock()

def get_v715_modules():
    """v7.15 Hexadic Dual Convolution Module Thread-safe Lazy Load"""
    if not hasattr(app, '_v715_modules') or app._v715_modules is None:
        with _v715_modules_lock:
            if not hasattr(app, '_v715_modules') or app._v715_modules is None:
                try:
                    from modules.M157_JinlingGridConvolution import get_instance as get_m157
                    from modules.M158_PhaseModulusDualConvolution import get_instance as get_m158
                    from modules.M159_ReversePhaseConvolution import get_instance as get_m159
                    from modules.M160_FenxiangziTopologyConvolution import get_instance as get_m160
                    from modules.M161_BackwardFlowConvolution import get_instance as get_m161
                    from modules.M162_UVRegularizedConvolution import get_instance as get_m162
                    from modules.M78_HoTTReasoningEngine import get_instance as get_m78_v31
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
                    from modules.M163_ArkSandbox import get_instance as get_m163
                    from modules.M164_VCGMechanismDesigner import get_instance as get_m164
                    from modules.M165_NarrativeActionQuantifier import get_instance as get_m165
                    from modules.M166_SemanticCurvatureCalculator import get_instance as get_m166
                    from modules.M167_AGIToposEngine import get_instance as get_m167
                    from modules.M168_SelfManifestingDetector import get_instance as get_m168
                    from modules.M169_PointFreeTopology import get_instance as get_m169
                    from modules.M170_DependentOriginationAnalyzer import get_instance as get_m170
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
                    from modules.M171_UFMLambdaUniverse import UFMLambdaUniverse as _M171
                    from modules.M172_TYFormalizer import TYFormalizer as _M172
                    from modules.M173_UFMRISCVArchitect import UFMRISCVArchitect as _M173
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

# ==================== 专家系统 API（agency-agents-zh 215位专家）====================

# 懒加载全局注册表
_expert_registry = None
_expert_registry_lock = threading.Lock()

def get_expert_registry() -> 'ExpertRegistry':
    """获取全局 ExpertRegistry 单例（懒加载）"""
    global _expert_registry
    if _expert_registry is None:
        with _expert_registry_lock:
            if _expert_registry is None:
                try:
                    from modules.expert_registry import get_registry
                    _expert_registry = get_registry()
                except Exception as e:
                    print(f"⚠️ 专家注册表加载失败: {e}")
                    _expert_registry = None
    return _expert_registry


# ==================== v7.28 万物理解引擎 (M196) API ====================

_v728_engine = None
_v728_lock = threading.Lock()


def get_v728_engine():
    """获取 M196 万物理解引擎单例"""
    global _v728_engine
    if _v728_engine is None:
        with _v728_lock:
            if _v728_engine is None:
                try:
                    from modules.M196_UnderstandAnythingEngine import UnderstandAnythingEngine
                    _v728_engine = UnderstandAnythingEngine.get_instance()
                except Exception as e:
                    print(f"[v728] 万物理解引擎加载失败: {e}")
                    _v728_engine = None
    return _v728_engine


# ── v728b 增强 API：UA × 专家系统深度集成 ──────────────────────


# ==================== 注册 Blueprints ====================
from blueprints.bp_core import bp as bp_core
from blueprints.bp_core_api import bp as bp_core_api
from blueprints.bp_v63 import bp as bp_v63
from blueprints.bp_v70 import bp as bp_v70
from blueprints.bp_v71 import bp as bp_v71
from blueprints.bp_v710 import bp as bp_v710
from blueprints.bp_v711 import bp as bp_v711
from blueprints.bp_v712 import bp as bp_v712
from blueprints.bp_v713 import bp as bp_v713
from blueprints.bp_v714 import bp as bp_v714
from blueprints.bp_v715 import bp as bp_v715
from blueprints.bp_v716 import bp as bp_v716
from blueprints.bp_v717 import bp as bp_v717
from blueprints.bp_v718 import bp as bp_v718
from blueprints.bp_v719 import bp as bp_v719
from blueprints.bp_v72 import bp as bp_v72
from blueprints.bp_v720 import bp as bp_v720
from blueprints.bp_v721 import bp as bp_v721
from blueprints.bp_v722 import bp as bp_v722
from blueprints.bp_v723 import bp as bp_v723
from blueprints.bp_v724 import bp as bp_v724
from blueprints.bp_v725 import bp as bp_v725
from blueprints.bp_v725b import bp as bp_v725b
from blueprints.bp_v726 import bp as bp_v726
from blueprints.bp_v727 import bp as bp_v727
from blueprints.bp_v728 import bp as bp_v728
from blueprints.bp_v729 import bp as bp_v729
from blueprints.bp_v73 import bp as bp_v73
from blueprints.bp_v730 import bp as bp_v730
from blueprints.bp_v731 import bp as bp_v731
from blueprints.bp_v74 import bp as bp_v74
from blueprints.bp_v75 import bp as bp_v75
from blueprints.bp_v76 import bp as bp_v76
from blueprints.bp_v77 import bp as bp_v77
from blueprints.bp_v78 import bp as bp_v78
from blueprints.bp_v79 import bp as bp_v79

app.register_blueprint(bp_core)
app.register_blueprint(bp_core_api)
app.register_blueprint(bp_v63)
app.register_blueprint(bp_v70)
app.register_blueprint(bp_v71)
app.register_blueprint(bp_v710)
app.register_blueprint(bp_v711)
app.register_blueprint(bp_v712)
app.register_blueprint(bp_v713)
app.register_blueprint(bp_v714)
app.register_blueprint(bp_v715)
app.register_blueprint(bp_v716)
app.register_blueprint(bp_v717)
app.register_blueprint(bp_v718)
app.register_blueprint(bp_v719)
app.register_blueprint(bp_v72)
app.register_blueprint(bp_v720)
app.register_blueprint(bp_v721)
app.register_blueprint(bp_v722)
app.register_blueprint(bp_v723)
app.register_blueprint(bp_v724)
app.register_blueprint(bp_v725)
app.register_blueprint(bp_v725b)
app.register_blueprint(bp_v726)
app.register_blueprint(bp_v727)
app.register_blueprint(bp_v728)
app.register_blueprint(bp_v729)
app.register_blueprint(bp_v73)
app.register_blueprint(bp_v730)
app.register_blueprint(bp_v731)
app.register_blueprint(bp_v74)
app.register_blueprint(bp_v75)
app.register_blueprint(bp_v76)
app.register_blueprint(bp_v77)
app.register_blueprint(bp_v78)
app.register_blueprint(bp_v79)

# ==================== 以下为主程序入口 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🌌 统一太乙系统 Web 服务 (Phase 2 具身+心架构)")
    print("   前端: http://localhost:5000")
    print("   API:  http://localhost:5000/api/chat")
    print("   专家系统 API:")
    print("   - /api/experts                    (列出所有专家)")
    print("   - /api/experts?department=engineering  (按部门过滤)")
    print("   - /api/experts/<expert_id>        (专家详情)")
    print("   - /api/experts/search?q=写作       (搜索专家)")
    print("   - /api/experts/departments        (部门列表)")
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

# ============================================================
# v7.31 True AGI 升级 — M197-M206 + P13-P17 MVE
# ============================================================

# --- M197 ToMEngine 心理理论引擎 ---
# --- M198 SelfModelCore 自我模型核心 ---
# --- M199 SocialRelTopology 社会关系拓扑 ---
# --- M200 CognitiveFlexibilityEngine 认知灵活性引擎 ---
# --- M201 EMLOperatorCore EML相位灵活性 ---
# --- M202 AutismSpectrumDetector 认知谱系检测器 ---
# --- M203 CRDReflectorEngine 双轨CRD反射引擎 ---
# --- M204 AGIMonitorOperator AGI监控算子 ---
# --- M205 TrustCalibrationEngine 信任校准引擎 ---
# --- M206 ControlledEntropyEngine 可控熵增引擎 ---
# --- v7.31 MVE Experiments (P13-P17) ---
# --- v7.31 Theorem Verification ---
