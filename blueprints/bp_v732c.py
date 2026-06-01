# -*- coding: utf-8 -*-
"""
Blueprint: v732c (22 routes)
M218-M222 — ITA-Trigger + 临界金灵球初始化 + 双工厂契约 + 摄控中心太极映射 + SerDes本体论引擎
URL prefix: /api/v732c
"""

import math
import shared_state
from flask import Blueprint, request, jsonify

bp = Blueprint('v732c', __name__, url_prefix='/api/v732c')


# ══════════════════════════════════════════════════
# M218 ITATriggerEngine — ITA触发引擎
# ══════════════════════════════════════════════════

@bp.route('/ita/register_rule', methods=['POST'])
def api_v732c_ita_register_rule():
    """
    注册ITA规则

    POST body:
      info: str            环境提示信息
      context: dict        上下文向量
      action_chain: list   有序动作链
      category: str        同类Near-Miss分类键
    """
    try:
        from modules.M218_ITATriggerEngine import ITARuleEngine
        data = request.get_json(force=True) or {}
        engine = ITARuleEngine()
        rule_id = engine.register_rule(
            info=data.get('info', 'default_info'),
            context=data.get('context', {}),
            action_chain=data.get('action_chain', ['alert']),
            category=data.get('category', 'general')
        )
        # 存入shared_state以复用
        if not hasattr(shared_state, '_v732c_ita_engine'):
            shared_state._v732c_ita_engine = engine
        else:
            shared_state._v732c_ita_engine.rules.update(engine.rules)
            shared_state._v732c_ita_engine._rule_counter = engine._rule_counter
        return jsonify({'rule_id': rule_id, 'status': 'registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ita/evaluate', methods=['POST'])
def api_v732c_ita_evaluate():
    """
    评估ITA规则触发

    POST body:
      context: dict   当前上下文
    """
    try:
        from modules.M218_ITATriggerEngine import ITARuleEngine
        data = request.get_json(force=True) or {}
        engine = getattr(shared_state, '_v732c_ita_engine', None) or ITARuleEngine()
        results = engine.evaluate(data.get('context', {}))
        return jsonify({'results': [r if isinstance(r, dict) else str(r) for r in results]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ita/near_miss', methods=['POST'])
def api_v732c_ita_near_miss():
    """
    记录Near-Miss事件

    POST body:
      category: str    同类分类键
      severity: float  严重度 (0-1)
      root_cause: str  根因
    """
    try:
        from modules.M218_ITATriggerEngine import NearMissTracker, NearMissEvent
        import time
        data = request.get_json(force=True) or {}
        tracker = getattr(shared_state, '_v732c_nm_tracker', None) or NearMissTracker()
        event = NearMissEvent(
            event_id=f"nm_{int(time.time()*1000)}",
            category=data.get('category', 'general'),
            ita_rule_id=data.get('rule_id'),
            timestamp=time.time(),
            severity=float(data.get('severity', 0.5)),
            root_cause=data.get('root_cause', 'unknown')
        )
        result = tracker.record(event)
        shared_state._v732c_nm_tracker = tracker
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ita/classify_behavior', methods=['POST'])
def api_v732c_ita_classify():
    """
    ECP/ICE行为分类

    POST body:
      observations: list   行为观察列表
    """
    try:
        from modules.M218_ITATriggerEngine import ECPICEIdentifier
        data = request.get_json(force=True) or {}
        identifier = ECPICEIdentifier()
        result = identifier.classify_behavior(data.get('observations', []))
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M219 DualFactoryContract — 双工厂+智能契约
# ══════════════════════════════════════════════════

@bp.route('/factory/assess', methods=['POST'])
def api_v732c_factory_assess():
    """
    双工厂健康评估

    POST body:
      tf_metrics: dict    Token Factory指标
      af_metrics: dict    Agent Factory指标
      eta_threshold: float  价值率阈值 (default: 0.3)
    """
    try:
        from modules.M219_DualFactoryContract import (
            DualFactoryMonitor, TokenFactoryMetrics, AgentFactoryMetrics
        )
        data = request.get_json(force=True) or {}
        eta_threshold = float(data.get('eta_threshold', 0.3))
        monitor = DualFactoryMonitor(eta_threshold=eta_threshold)

        tf_data = data.get('tf_metrics', {})
        af_data = data.get('af_metrics', {})

        tf_metrics = TokenFactoryMetrics(
            throughput_ttf=float(tf_data.get('throughput_ttf', 1000)),
            latency_ms=float(tf_data.get('latency_ms', 50)),
            gpu_utilization=float(tf_data.get('gpu_utilization', 0.8)),
            kv_cache_hit_rate=float(tf_data.get('kv_cache_hit_rate', 0.9))
        )
        af_metrics = AgentFactoryMetrics(
            value_rate_eta=float(af_data.get('value_rate_eta', 0.5)),
            task_completion_rate=float(af_data.get('task_completion_rate', 0.85)),
            user_satisfaction=float(af_data.get('user_satisfaction', 0.7)),
            error_rate=float(af_data.get('error_rate', 0.05))
        )

        health = monitor.assess(tf_metrics, af_metrics)
        return jsonify({'health': health if isinstance(health, dict) else str(health)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/factory/schedule', methods=['POST'])
def api_v732c_factory_schedule():
    """
    刘机制帧节拍调度

    POST body:
      tasks: list        任务列表
      max_concurrent: int  最大并发 (default: 8)
    """
    try:
        from modules.M219_DualFactoryContract import LiuFrameScheduler
        data = request.get_json(force=True) or {}
        max_concurrent = int(data.get('max_concurrent', 8))
        scheduler = LiuFrameScheduler(max_concurrent=max_concurrent)
        result = scheduler.schedule(data.get('tasks', []))
        return jsonify({'result': result if isinstance(result, (dict, list)) else str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contract/register', methods=['POST'])
def api_v732c_contract_register():
    """
    注册声明式智能契约

    POST body:
      role: str            角色标识
      pre_conditions: dict 输入语义约束
      post_conditions: dict 期望效果区间
      tolerance: dict      容差带
      contract_type: str   MCP or A2A (default: MCP)
    """
    try:
        from modules.M219_DualFactoryContract import SmartContractRegistry, SmartContract
        import time
        data = request.get_json(force=True) or {}
        registry = getattr(shared_state, '_v732c_contract_registry', None) or SmartContractRegistry()

        contract = SmartContract(
            contract_id=f"sc_{int(time.time()*1000)}",
            role=data.get('role', 'agent'),
            pre_conditions=data.get('pre_conditions', {}),
            post_conditions=data.get('post_conditions', {}),
            tolerance=data.get('tolerance', {'default': 0.1}),
            contract_type=data.get('contract_type', 'MCP')
        )
        cid = registry.register(contract)
        shared_state._v732c_contract_registry = registry
        return jsonify({'contract_id': cid, 'status': 'registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/contract/list', methods=['GET'])
def api_v732c_contract_list():
    """
    列出所有智能契约

    Query params:
      contract_type: str   过滤类型 (optional)
    """
    try:
        from modules.M219_DualFactoryContract import SmartContractRegistry
        registry = getattr(shared_state, '_v732c_contract_registry', None) or SmartContractRegistry()
        ctype = request.args.get('contract_type')
        contracts = registry.list_contracts(ctype)
        return jsonify({'contracts': [c if isinstance(c, dict) else str(c) for c in contracts]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M220 CriticalJinlingInit — 临界金灵球初始化
# ══════════════════════════════════════════════════

@bp.route('/critical/init', methods=['POST'])
def api_v732c_critical_init():
    """
    临界金灵球初始化

    POST body:
      n_nodes: int           节点数 (default: 64)
      sparsity: float        稀疏度 (default: 0.15)
      inhib_ratio: float     抑制性连接比例 (default: 0.20)
      weight_std: float      权重标准差 (default: 0.1)
      spectral_tolerance: float  谱半径容差 (default: 0.3)
    """
    try:
        from modules.M220_CriticalJinlingInit import CriticalJinlingInitializer, CriticalInitConfig
        data = request.get_json(force=True) or {}
        config = CriticalInitConfig(
            n_nodes=int(data.get('n_nodes', 64)),
            sparsity=float(data.get('sparsity', 0.15)),
            inhib_ratio=float(data.get('inhib_ratio', 0.20)),
            weight_std=float(data.get('weight_std', 0.1)),
            spectral_tolerance=float(data.get('spectral_tolerance', 0.3))
        )
        initializer = CriticalJinlingInitializer(config)
        result = initializer.initialize()
        return jsonify({'result': result if isinstance(result, dict) else str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/critical/wigner_verify', methods=['POST'])
def api_v732c_critical_wigner():
    """
    Wigner半圆谱验证

    POST body:
      n_nodes: int      节点数 (default: 64)
      n_trials: int     验证次数 (default: 10)
    """
    try:
        from modules.M220_CriticalJinlingInit import CriticalJinlingInitializer, CriticalInitConfig
        data = request.get_json(force=True) or {}
        config = CriticalInitConfig(n_nodes=int(data.get('n_nodes', 64)))
        initializer = CriticalJinlingInitializer(config)
        result = initializer.initialize()
        verify = initializer.verify_wigner_semicircle(result)
        return jsonify({'verification': verify if isinstance(verify, dict) else str(verify)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/critical/compare', methods=['POST'])
def api_v732c_critical_compare():
    """
    临界 vs 随机初始化对比 (P1预言验证)

    POST body:
      n_trials: int   实验次数 (default: 30)
    """
    try:
        from modules.M220_CriticalJinlingInit import CriticalJinlingInitializer, CriticalInitConfig
        data = request.get_json(force=True) or {}
        config = CriticalInitConfig(n_nodes=32)  # 32节点减少计算量
        initializer = CriticalJinlingInitializer(config)
        result = initializer.compare_with_random(n_trials=int(data.get('n_trials', 30)))
        return jsonify({'comparison': result if isinstance(result, dict) else str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M221 DualFocusControl — 摄控中心/太极映射
# ══════════════════════════════════════════════════

@bp.route('/focus/orbit', methods=['POST'])
def api_v732c_focus_orbit():
    """
    圆锥曲线轨道计算

    POST body:
      energy: float        总能量
      angular_momentum: float  角动量
      mass: float          质量 (default: 1.0)
      k: float             力常数 (default: 1.0)
    """
    try:
        from modules.M221_DualFocusControl import ConicOrbitalMechanics
        data = request.get_json(force=True) or {}
        mech = ConicOrbitalMechanics()
        orbit = mech.compute_orbit(
            energy=float(data.get('energy', -0.5)),
            angular_momentum=float(data.get('angular_momentum', 1.0)),
            mass=float(data.get('mass', 1.0)),
            k=float(data.get('k', 1.0))
        )
        dual_focus = mech.compute_dual_focus(orbit)
        state = mech.classify_state(orbit)
        return jsonify({
            'orbit': orbit if isinstance(orbit, dict) else str(orbit),
            'dual_focus': dual_focus if isinstance(dual_focus, dict) else str(dual_focus),
            'state': state if isinstance(state, dict) else str(state)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/focus/velocities', methods=['POST'])
def api_v732c_focus_velocities():
    """
    相速度-群速度计算 (v₁v₂=c²验证)

    POST body:
      energy: float    总能量 (default: 1.5)
      momentum: float  动量 (default: 1.0)
      c: float         光速 (default: 1.0)
    """
    try:
        from modules.M221_DualFocusControl import ConicOrbitalMechanics
        data = request.get_json(force=True) or {}
        mech = ConicOrbitalMechanics()
        vg = mech.compute_velocities(
            energy=float(data.get('energy', 1.5)),
            momentum=float(data.get('momentum', 1.0)),
            c=float(data.get('c', 1.0))
        )
        return jsonify({'velocities': vg if isinstance(vg, dict) else str(vg)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/focus/govern', methods=['POST'])
def api_v732c_focus_govern():
    """
    双焦点摄控治理

    POST body:
      eccentricity: float   离心率
      energy: float         总能量
      context: dict         上下文信息
    """
    try:
        from modules.M221_DualFocusControl import DualFocusGovernor, ConicOrbitalMechanics, ConicOrbit
        data = request.get_json(force=True) or {}
        orbit = ConicOrbit(
            semi_latus_rectum=1.0,
            eccentricity=float(data.get('eccentricity', 0.5)),
            energy=float(data.get('energy', -0.5))
        )
        governor = DualFocusGovernor()
        result = governor.govern(orbit, data.get('context', {}))
        return jsonify({'governance': result if isinstance(result, dict) else str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/focus/moufang_dh', methods=['POST'])
def api_v732c_focus_moufang():
    """
    Moufang Loop DH密钥交换

    POST body:
      private_a: int   Alice私钥 (default: 7)
      private_b: int   Bob私钥 (default: 13)
    """
    try:
        from modules.M221_DualFocusControl import MoufangLoopCrypto
        data = request.get_json(force=True) or {}
        crypto = MoufangLoopCrypto()
        result = crypto.dh_key_exchange(
            private_a=int(data.get('private_a', 7)),
            private_b=int(data.get('private_b', 13))
        )
        return jsonify({'dh_result': result if isinstance(result, dict) else str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/focus/sbox', methods=['POST'])
def api_v732c_focus_sbox():
    """
    拟群S-Box轻量混淆

    POST body:
      data_bytes: list   待混淆字节列表
      key_row: int       密钥行索引 (default: 0)
    """
    try:
        from modules.M221_DualFocusControl import QuasigroupSBox
        data = request.get_json(force=True) or {}
        sbox = QuasigroupSBox()
        data_bytes = data.get('data_bytes', [0x48, 0x65, 0x6C, 0x6C, 0x6F])
        key_row = int(data.get('key_row', 0))
        result = sbox.substitute_batch(data_bytes, key_row)
        return jsonify({'sbox_result': result if isinstance(result, dict) else str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M222 SerDes Ontology Engine (6 routes)
# ══════════════════════════════════════════════════

@bp.route('/serdes/serialize', methods=['POST'])
def m222_serialize():
    """TY-Serialize: R->S, parallel relation space to serial frame sequence"""
    try:
        from modules.M222_SerDesOntologyEngine import TYSerializer
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(silent=True) or {}
        n_nodes = int(data.get('n_nodes', 8))
        n_steps = int(data.get('n_steps', 5))

        # Construct test graph
        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        for i in range(n_nodes - 1):
            g.add_edge(PortEdge(src=f'n{i}', dst=f'n{i+1}', port_src=i, port_dst=i+1))
            g.add_edge(PortEdge(src=f'n{i+1}', dst=f'n{i}', port_src=i+1, port_dst=i))
        for i in range(0, n_nodes - 2, 3):
            g.add_edge(PortEdge(src=f'n{i}', dst=f'n{i+2}', port_src=i+20, port_dst=i+2))
            g.add_edge(PortEdge(src=f'n{i+2}', dst=f'n{i}', port_src=i+2, port_dst=i+20))

        serializer = TYSerializer()
        result = serializer.serialize(g, n_steps=n_steps)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/deserialize', methods=['POST'])
def m222_deserialize():
    """TY-Deserialize: S->R, serial frame sequence back to relation space"""
    try:
        from modules.M222_SerDesOntologyEngine import TYSerializer, TYDeserializer
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(silent=True) or {}
        n_nodes = int(data.get('n_nodes', 8))
        n_steps = int(data.get('n_steps', 5))
        ice_active = data.get('ice_active', True)

        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        for i in range(n_nodes - 1):
            g.add_edge(PortEdge(src=f'n{i}', dst=f'n{i+1}', port_src=i, port_dst=i+1))
            g.add_edge(PortEdge(src=f'n{i+1}', dst=f'n{i}', port_src=i+1, port_dst=i))

        serializer = TYSerializer()
        ser_result = serializer.serialize(g, n_steps=n_steps)

        deserializer = TYDeserializer(ido_context={'ice_active': ice_active})
        des_result = deserializer.deserialize(ser_result.frame_sequence, ice_active=ice_active)
        return jsonify(des_result.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/biserdes_status', methods=['POST'])
def m222_biserdes_status():
    """Check bi-SerDes completeness status"""
    try:
        from modules.M222_SerDesOntologyEngine import BiSerDesChecker
        data = request.get_json(silent=True) or {}
        system_config = {
            'fteliology_channel': data.get('fteliology_channel', True),
            'ice_composite': data.get('ice_composite', True),
            'beta_rewire': data.get('beta_rewire', True),
            'behavior_loop': data.get('behavior_loop', True),
        }
        checker = BiSerDesChecker()
        status = checker.check(system_config)
        return jsonify(status.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/info_loss', methods=['POST'])
def m222_info_loss():
    """Compute information loss analysis"""
    try:
        from modules.M222_SerDesOntologyEngine import TYSerializer, InformationLossAnalyzer
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(silent=True) or {}
        n_nodes = int(data.get('n_nodes', 8))
        n_steps = int(data.get('n_steps', 5))

        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        for i in range(n_nodes - 1):
            g.add_edge(PortEdge(src=f'n{i}', dst=f'n{i+1}', port_src=i, port_dst=i+1))
            g.add_edge(PortEdge(src=f'n{i+1}', dst=f'n{i}', port_src=i+1, port_dst=i))

        serializer = TYSerializer()
        ser_result = serializer.serialize(g, n_steps=n_steps)

        analyzer = InformationLossAnalyzer()
        loss_timeline = analyzer.analyze_loss_over_time(ser_result.frame_sequence)
        return jsonify({
            'source_entropy': ser_result.source_graph_entropy,
            'serial_entropy': ser_result.serial_entropy,
            'info_loss': ser_result.info_loss,
            'loss_timeline': loss_timeline,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/eml_hardening', methods=['POST'])
def m222_eml_hardening():
    """EML five hardening verification"""
    try:
        from modules.M222_SerDesOntologyEngine import EMLFiveHardening
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(silent=True) or {}
        n_nodes = int(data.get('n_nodes', 8))

        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        for i in range(n_nodes - 1):
            g.add_edge(PortEdge(src=f'n{i}', dst=f'n{i+1}', port_src=i, port_dst=i+1))
            g.add_edge(PortEdge(src=f'n{i+1}', dst=f'n{i}', port_src=i+1, port_dst=i))

        hardening = EMLFiveHardening()
        result = hardening.verify_hardening(g)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/verify_theorem', methods=['GET'])
def m222_verify_theorem():
    """Verify M222 theorems T4.1/T4.2/T4.3"""
    try:
        from modules.M222_SerDesOntologyEngine import verify_theorem_t41, verify_theorem_t42, verify_theorem_t43
        theorem = request.args.get('theorem', 'all')
        results = {}
        if theorem in ('all', 't41'):
            results['T41'] = verify_theorem_t41()
        if theorem in ('all', 't42'):
            results['T42'] = verify_theorem_t42()
        if theorem in ('all', 't43'):
            results['T43'] = verify_theorem_t43()
        # Convert numpy types
        import numpy as np
        def convert(obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [convert(i) for i in obj]
            return obj
        return jsonify(convert(results))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M222 SerDesOntologyEngine — SerDes本体论引擎
# ══════════════════════════════════════════════════

@bp.route('/serdes/serialize', methods=['POST'])
def api_v732c_serdes_serialize():
    """
    执行TY-Serialize Π_s: R → S

    POST body:
      n_nodes: int       节点数 (默认12)
      n_edges: int       边数 (默认15)
      n_steps: int       β-rewire步数 (默认8)
    """
    try:
        from modules.M222_SerDesOntologyEngine import TYSerializer
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(force=True) or {}
        n_nodes = int(data.get('n_nodes', 12))
        n_edges = int(data.get('n_edges', min(n_nodes * 2, 20)))
        n_steps = int(data.get('n_steps', 8))

        # 构建测试图
        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        import random
        random.seed(42)
        for _ in range(n_edges):
            i, j = random.randint(0, n_nodes - 1), random.randint(0, n_nodes - 1)
            if i != j:
                g.add_edge(PortEdge(src=f'n{i}', dst=f'n{j}', port_src=0, port_dst=0))

        serializer = TYSerializer()
        result = serializer.serialize(g, n_steps=n_steps)
        return jsonify({
            'source_entropy': result.source_graph_entropy,
            'serial_entropy': result.serial_entropy,
            'info_loss': result.info_loss,
            'beta_steps': result.beta_steps,
            'passes_t41': result.passes_theorem_t41,
            'frame_count': len(result.frame_sequence.frames),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/deserialize', methods=['POST'])
def api_v732c_serdes_deserialize():
    """
    执行TY-Deserialize Δ_s: S → R

    POST body:
      n_nodes: int       节点数 (默认12)
      n_steps: int       Serialize步数 (默认8)
      ice_active: bool   ICE闭环是否活跃 (默认True)
    """
    try:
        from modules.M222_SerDesOntologyEngine import TYSerializer, TYDeserializer
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(force=True) or {}
        n_nodes = int(data.get('n_nodes', 12))
        n_steps = int(data.get('n_steps', 8))
        ice_active = bool(data.get('ice_active', True))

        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        import random
        random.seed(42)
        for _ in range(min(n_nodes * 2, 20)):
            i, j = random.randint(0, n_nodes - 1), random.randint(0, n_nodes - 1)
            if i != j:
                g.add_edge(PortEdge(src=f'n{i}', dst=f'n{j}', port_src=0, port_dst=0))

        serializer = TYSerializer()
        ser_result = serializer.serialize(g, n_steps=n_steps)

        deserializer = TYDeserializer()
        deser_result = deserializer.deserialize(ser_result.frame_sequence, ice_active=ice_active)
        return jsonify({
            'fidelity': deser_result.reconstruction_fidelity,
            'kl_divergence': deser_result.reconstruction_kl_div,
            'kl_converged': deser_result.kl_converged,
            'ice_active': deser_result.ice_active,
            'beta_rewire_applied': deser_result.beta_rewire_applied,
            'passes_t42': deser_result.passes_theorem_t42,
            'failure_reason': deser_result.failure_reason,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/biserdes_check', methods=['POST'])
def api_v732c_serdes_biserdes_check():
    """
    bi-SerDes完备性检验

    POST body:
      fteliology_channel: bool  流贯通道
      ice_composite: bool       ICE复合体
      beta_rewire: bool         β-rewire能力
      behavior_loop: bool       行为闭环
    """
    try:
        from modules.M222_SerDesOntologyEngine import BiSerDesChecker
        data = request.get_json(force=True) or {}
        checker = BiSerDesChecker()
        status = checker.check(data)
        return jsonify(status.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/eml_hardening', methods=['POST'])
def api_v732c_serdes_eml_hardening():
    """
    EML五项硬化验证

    POST body:
      n_nodes: int   节点数 (默认10)
      n_edges: int   边数 (默认15)
    """
    try:
        from modules.M222_SerDesOntologyEngine import EMLFiveHardening
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
        data = request.get_json(force=True) or {}
        n_nodes = int(data.get('n_nodes', 10))
        n_edges = int(data.get('n_edges', 15))

        g = JinlingGraph()
        for i in range(n_nodes):
            g.add_node(f'n{i}')
        import random
        random.seed(42)
        for _ in range(n_edges):
            i, j = random.randint(0, n_nodes - 1), random.randint(0, n_nodes - 1)
            if i != j:
                g.add_edge(PortEdge(src=f'n{i}', dst=f'n{j}', port_src=0, port_dst=0))

        hardening = EMLFiveHardening()
        result = hardening.verify_hardening(g)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/serdes/verify_theorem', methods=['POST'])
def api_v732c_serdes_verify_theorem():
    """
    验证M222定理

    POST body:
      theorem: str   定理编号 (t41/t42/t43)
      n_steps: int   β-rewire步数 (默认8)
    """
    try:
        from modules.M222_SerDesOntologyEngine import (
            verify_theorem_t41, verify_theorem_t42, verify_theorem_t43
        )
        data = request.get_json(force=True) or {}
        theorem = data.get('theorem', 't41').lower()
        n_steps = int(data.get('n_steps', 8))

        if theorem == 't41':
            result = verify_theorem_t41(n_steps=n_steps)
        elif theorem == 't42':
            result = verify_theorem_t42(n_steps=n_steps)
        elif theorem == 't43':
            result = verify_theorem_t43()
        else:
            return jsonify({'error': f'Unknown theorem: {theorem}. Use t41/t42/t43'}), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
