# -*- coding: utf-8 -*-
"""
Blueprint: v733c (52 routes)
M223-M225 — 金符学3D复广数 + MNQ8能流引擎 + SOP六体系自动生成器 + ICE自指闭环+Lean4对接+HAP协议
M226 — PCT端口兼容性定理引擎 (T2.40)
M155 IDO — Ftel信息力增强 + 时间箭头 (T2.41)
M227 — EML指数-对数混合函数引擎 (T2.42)
M228 — Liu机制变分原理引擎 (T2.43)
URL prefix: /api/v733
Version: v7.33c TMK (太一万有理论六合统合 + TMK端口兼容性 + EML + Liu机制)
"""

import math
import shared_state
from flask import Blueprint, request, jsonify

bp = Blueprint('v733', __name__, url_prefix='/api/v733')


# ══════════════════════════════════════════════════
# M223 GoldenSymbol3D — 金符学3D复广数+MNQ8能流引擎
# ══════════════════════════════════════════════════

@bp.route('/golden/compute', methods=['POST'])
def api_v733_golden_compute():
    """
    阴龙积 ⊙ 运算

    POST body:
      z1: {a, b, c}   第一个金符
      z2: {a, b, c}   第二个金符
      lam: float       耦合参数 (default 1.0)
    """
    try:
        from modules.M223_GoldenSymbol3D import GoldenSymbol, yin_long_product
        data = request.get_json(force=True) or {}
        z1_data = data.get('z1', {'a': 0, 'b': 0, 'c': 0})
        z2_data = data.get('z2', {'a': 0, 'b': 0, 'c': 0})
        lam = float(data.get('lam', 1.0))

        z1 = GoldenSymbol(z1_data['a'], z1_data['b'], z1_data['c'])
        z2 = GoldenSymbol(z2_data['a'], z2_data['b'], z2_data['c'])
        result = yin_long_product(z1, z2, lam=lam)

        return jsonify({
            'z1': z1.to_dict(),
            'z2': z2.to_dict(),
            'lam': lam,
            'result': result.to_dict(),
            'result_norm_sq': result.norm_sq()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/golden/properties', methods=['POST'])
def api_v733_golden_properties():
    """
    金符属性查询 (norm, conjugate, normalized)

    POST body:
      z: {a, b, c}    金符
    """
    try:
        from modules.M223_GoldenSymbol3D import GoldenSymbol
        data = request.get_json(force=True) or {}
        z_data = data.get('z', {'a': 0, 'b': 0, 'c': 0})
        z = GoldenSymbol(z_data['a'], z_data['b'], z_data['c'])

        return jsonify({
            'original': z.to_dict(),
            'conjugate': z.conjugate().to_dict(),
            'norm_sq': z.norm_sq(),
            'norm': z.norm(),
            'normalized': z.normalized().to_dict() if z.norm() > 1e-12 else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/mnq8/grid/create', methods=['POST'])
def api_v733_mnq8_grid_create():
    """
    创建MNQ8仿真网格

    POST body:
      topology: str    拓扑类型 ("1d"/"2d"/"3d")
      size: int         网格尺寸 (default 10)
      mass_threshold: float   MASS_FACE阈值 (default 1.0)
      lam: float        耦合参数 (default 1.0)
    """
    try:
        from modules.M223_GoldenSymbol3D import MNQ8Grid, MNQ8Simulation, GoldenSymbol
        import random
        data = request.get_json(force=True) or {}
        topology = data.get('topology', '1d')
        size = int(data.get('size', 10))
        mass_threshold = float(data.get('mass_threshold', 1.0))
        lam = float(data.get('lam', 1.0))

        grid = MNQ8Grid(topology=topology, size=size)
        # 随机初始化网格
        for i in range(grid.node_count()):
            gs = GoldenSymbol(
                random.gauss(0, 1),
                random.gauss(0, 1),
                random.gauss(0, 1)
            )
            grid.set_node(i, gs)

        # 缓存到shared_state
        if not hasattr(shared_state, '_v733_sim'):
            shared_state._v733_sim = {}
        sim_id = f"sim_{len(shared_state._v733_sim)}"
        sim = MNQ8Simulation(grid, mass_threshold=mass_threshold, lam=lam)
        shared_state._v733_sim[sim_id] = sim

        return jsonify({
            'sim_id': sim_id,
            'topology': topology,
            'size': size,
            'node_count': grid.node_count(),
            'mass_threshold': mass_threshold,
            'lam': lam,
            'grid': grid.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/mnq8/simulate', methods=['POST'])
def api_v733_mnq8_simulate():
    """
    运行MNQ8仿真

    POST body:
      sim_id: str       仿真ID (不提供则新建1d仿真)
      steps: int         仿真步数 (default 10)
    """
    try:
        from modules.M223_GoldenSymbol3D import MNQ8Grid, MNQ8Simulation, GoldenSymbol
        import random
        data = request.get_json(force=True) or {}
        sim_id = data.get('sim_id', None)
        steps = int(data.get('steps', 10))

        if sim_id and hasattr(shared_state, '_v733_sim') and sim_id in shared_state._v733_sim:
            sim = shared_state._v733_sim[sim_id]
        else:
            # 自动创建默认仿真
            grid = MNQ8Grid(topology='1d', size=10)
            for i in range(grid.node_count()):
                gs = GoldenSymbol(random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))
                grid.set_node(i, gs)
            sim = MNQ8Simulation(grid, mass_threshold=1.0, lam=1.0)
            sim_id = 'default'
            if not hasattr(shared_state, '_v733_sim'):
                shared_state._v733_sim = {}
            shared_state._v733_sim[sim_id] = sim

        results = sim.run(steps=steps)
        stats = sim.get_statistics()

        # 序列化结果
        serialized = []
        for r in results:
            serialized.append(r.to_dict())

        return jsonify({
            'sim_id': sim_id,
            'steps_run': steps,
            'results': serialized,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/mnq8/experiment', methods=['POST'])
def api_v733_mnq8_experiment():
    """
    运行对照实验 (HEX_RING_GAP vs BACKGROUND_OSC)

    POST body:
      mass_threshold: float   MASS_FACE阈值 (default 1.0)
    """
    try:
        from modules.M223_GoldenSymbol3D import run_comparison_experiment
        data = request.get_json(force=True) or {}
        mass_threshold = float(data.get('mass_threshold', 1.0))

        result = run_comparison_experiment(mass_threshold=mass_threshold)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/mnq8/inject_hex_ring', methods=['POST'])
def api_v733_mnq8_inject_hex_ring():
    """
    向网格注入HEX_RING_GAP强耦合囚禁态

    POST body:
      sim_id: str          仿真ID
      center_idx: int      中心节点索引
      radius: int           半径 (default 1)
    """
    try:
        data = request.get_json(force=True) or {}
        sim_id = data.get('sim_id', 'default')

        if not hasattr(shared_state, '_v733_sim') or sim_id not in shared_state._v733_sim:
            return jsonify({'error': f'Simulation {sim_id} not found'}), 404

        sim = shared_state._v733_sim[sim_id]
        center_idx = int(data.get('center_idx', 0))
        radius = int(data.get('radius', 1))

        sim.grid.inject_hex_ring_gap(center_idx, radius=radius)

        return jsonify({
            'sim_id': sim_id,
            'center_idx': center_idx,
            'radius': radius,
            'grid': sim.grid.to_dict(),
            'status': 'injected'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m223/state', methods=['GET'])
def api_v733_m223_state():
    """M223模块状态查询"""
    try:
        from modules.M223_GoldenSymbol3D import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m223/theorems', methods=['GET'])
def api_v733_m223_theorems():
    """M223定理验证 (T2.32-T2.34)"""
    try:
        from modules.M223_GoldenSymbol3D import verify_theorem_t232, verify_theorem_t233, verify_theorem_t234
        t232 = verify_theorem_t232()
        t233 = verify_theorem_t233()
        t234 = verify_theorem_t234()
        return jsonify({
            'T232': t232,
            'T233': t233,
            'T234': t234,
            'all_passed': t232.get('passed', False) and t233.get('passed', False) and t234.get('passed', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M224 SOPGeneratorEngine — SOP六体系自动生成引擎
# ══════════════════════════════════════════════════

@bp.route('/sop/generate_preset', methods=['POST'])
def api_v733_sop_generate_preset():
    """
    从预设生成SOP报告

    POST body:
      preset: str   预设名 ("superconductor"/"consensus"/"qualia"/"cmb")
    """
    try:
        from modules.M224_SOPGeneratorEngine import SOPGenerator
        data = request.get_json(force=True) or {}
        preset = data.get('preset', 'superconductor')

        gen = SOPGenerator()
        report = gen.generate_from_preset(preset)
        if report is None:
            return jsonify({'error': f'Unknown preset: {preset}'}), 400

        # 缓存报告
        if not hasattr(shared_state, '_v733_sop_reports'):
            shared_state._v733_sop_reports = {}
        rid = f"sop_{len(shared_state._v733_sop_reports)}"
        shared_state._v733_sop_reports[rid] = report
        gen._reports[rid] = report

        return jsonify({
            'report_id': rid,
            'preset': preset,
            'report': report.to_dict(),
            'markdown': report.render_md()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sop/generate_custom', methods=['POST'])
def api_v733_sop_generate_custom():
    """
    自定义SOP报告生成

    POST body:
      phenomenon: str     现象描述
      analyst: str         分析者名称 (default "TY-API")
      H1: str              内视界锚定 (optional)
      H2: str              外视界锚定 (optional)
      H3: str              统一视界锚定 (optional)
    """
    try:
        from modules.M224_SOPGeneratorEngine import SOPGenerator
        data = request.get_json(force=True) or {}
        phenomenon = data.get('phenomenon', 'unspecified')
        analyst = data.get('analyst', 'TY-API')
        H1 = data.get('H1', '')
        H2 = data.get('H2', '')
        H3 = data.get('H3', '')

        gen = SOPGenerator()
        report = gen.generate_custom(
            phenomenon=phenomenon,
            analyst=analyst,
            H1=H1, H2=H2, H3=H3
        )

        # 缓存
        if not hasattr(shared_state, '_v733_sop_reports'):
            shared_state._v733_sop_reports = {}
        rid = f"sop_{len(shared_state._v733_sop_reports)}"
        shared_state._v733_sop_reports[rid] = report
        gen._reports[rid] = report

        return jsonify({
            'report_id': rid,
            'report': report.to_dict(),
            'markdown': report.render_md()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sop/auto_generate', methods=['POST'])
def api_v733_sop_auto_generate():
    """
    自动分类并生成SOP报告

    POST body:
      phenomenon: str   现象描述 (自动分类)
    """
    try:
        from modules.M224_SOPGeneratorEngine import SOPGenerator
        data = request.get_json(force=True) or {}
        phenomenon = data.get('phenomenon', 'unspecified')

        gen = SOPGenerator()
        category = gen.classify_phenomenon(phenomenon)
        report = gen.auto_generate(phenomenon)

        # 缓存
        if not hasattr(shared_state, '_v733_sop_reports'):
            shared_state._v733_sop_reports = {}
        rid = f"sop_{len(shared_state._v733_sop_reports)}"
        shared_state._v733_sop_reports[rid] = report
        gen._reports[rid] = report

        return jsonify({
            'report_id': rid,
            'category': category,
            'report': report.to_dict(),
            'markdown': report.render_md()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sop/list', methods=['GET'])
def api_v733_sop_list():
    """列出所有已生成的SOP报告"""
    try:
        from modules.M224_SOPGeneratorEngine import SOPGenerator
        gen = SOPGenerator()
        # 合并shared_state缓存
        if hasattr(shared_state, '_v733_sop_reports'):
            for rid, report in shared_state._v733_sop_reports.items():
                if rid not in gen._reports:
                    gen._reports[rid] = report
        reports = gen.list_reports()
        return jsonify({'reports': reports, 'count': len(reports)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sop/report/<report_id>', methods=['GET'])
def api_v733_sop_get_report(report_id):
    """获取指定SOP报告"""
    try:
        from modules.M224_SOPGeneratorEngine import SOPGenerator
        gen = SOPGenerator()
        if hasattr(shared_state, '_v733_sop_reports') and report_id in shared_state._v733_sop_reports:
            report = shared_state._v733_sop_reports[report_id]
            return jsonify({'report_id': report_id, 'report': report.to_dict(), 'markdown': report.render_md()})
        report = gen.get_report(report_id)
        if report is None:
            return jsonify({'error': f'Report {report_id} not found'}), 404
        return jsonify({'report_id': report_id, 'report': report.to_dict(), 'markdown': report.render_md()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m224/state', methods=['GET'])
def api_v733_m224_state():
    """M224模块状态查询"""
    try:
        from modules.M224_SOPGeneratorEngine import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m224/theorems', methods=['GET'])
def api_v733_m224_theorems():
    """M224定理验证 (T2.35-T2.36)"""
    try:
        from modules.M224_SOPGeneratorEngine import verify_theorem_t235, verify_theorem_t236
        t235 = verify_theorem_t235()
        t236 = verify_theorem_t236()
        return jsonify({
            'T235': t235,
            'T236': t236,
            'all_passed': t235.get('passed', False) and t236.get('passed', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M225 ICELeanLoop — ICE自指闭环+Lean4对接+HAP协议
# ══════════════════════════════════════════════════

@bp.route('/ice/create_session', methods=['POST'])
def api_v733_ice_create_session():
    """
    创建ICE会话

    POST body:
      mass_threshold: float   MASS_FACE阈值 (default 1.0)
      sphere_count: int       初始金灵球数量 (default 5)
    """
    try:
        from modules.M225_ICELeanLoop import JinlingHeap, JinlingSphere, ICESession
        import random, uuid
        data = request.get_json(force=True) or {}
        mass_threshold = float(data.get('mass_threshold', 1.0))
        sphere_count = int(data.get('sphere_count', 5))

        heap = JinlingHeap()
        for i in range(sphere_count):
            sphere = JinlingSphere(
                sid=f"S{i}",
                i_int=random.randint(1, 5),
                ports=[f"p{j}" for j in range(random.randint(1, 3))],
                chi=random.randint(1, 3),
                mod=random.randint(1, 7),
                phase=random.gauss(0, 1)
            )
            heap.add_sphere(sphere)

        ice = ICESession(heap, mass_threshold=mass_threshold)

        # 缓存
        if not hasattr(shared_state, '_v733_ice_sessions'):
            shared_state._v733_ice_sessions = {}
        session_id = f"ice_{uuid.uuid4().hex[:8]}"
        shared_state._v733_ice_sessions[session_id] = ice

        return jsonify({
            'session_id': session_id,
            'mass_threshold': mass_threshold,
            'sphere_count': sphere_count,
            'heap': heap.to_dict(),
            'status': 'created'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ice/observe', methods=['POST'])
def api_v733_ice_observe():
    """
    ICE ℐ (内视界观测)

    POST body:
      session_id: str   ICE会话ID
    """
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get('session_id', '')

        if not hasattr(shared_state, '_v733_ice_sessions') or session_id not in shared_state._v733_ice_sessions:
            return jsonify({'error': f'Session {session_id} not found'}), 404

        ice = shared_state._v733_ice_sessions[session_id]
        snapshot = ice.observe()

        return jsonify({
            'session_id': session_id,
            'observation': snapshot
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ice/decide', methods=['POST'])
def api_v733_ice_decide():
    """
    ICE ℂ (被观测=自身 → 刘机制优选)

    POST body:
      session_id: str   ICE会话ID
      goal: str          目标描述
    """
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get('session_id', '')
        goal = data.get('goal', 'optimize')

        if not hasattr(shared_state, '_v733_ice_sessions') or session_id not in shared_state._v733_ice_sessions:
            return jsonify({'error': f'Session {session_id} not found'}), 404

        ice = shared_state._v733_ice_sessions[session_id]
        preferred = ice.decide(goal)

        return jsonify({
            'session_id': session_id,
            'goal': goal,
            'preferred_heap': preferred.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ice/actuate', methods=['POST'])
def api_v733_ice_actuate():
    """
    ICE ℰ (可改L₃堆垒 → MNQ8调度执行)

    POST body:
      session_id: str    ICE会话ID
      goal: str           目标描述
    """
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get('session_id', '')
        goal = data.get('goal', 'optimize')

        if not hasattr(shared_state, '_v733_ice_sessions') or session_id not in shared_state._v733_ice_sessions:
            return jsonify({'error': f'Session {session_id} not found'}), 404

        ice = shared_state._v733_ice_sessions[session_id]
        preferred = ice.decide(goal)
        result = ice.actuate(preferred)

        return jsonify({
            'session_id': session_id,
            'goal': goal,
            'actuation_result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ice/cycle', methods=['POST'])
def api_v733_ice_cycle():
    """
    ICE完整闭环 ℐ→ℂ→ℰ (observe→decide→actuate)

    POST body:
      session_id: str   ICE会话ID
      goal: str          目标描述
    """
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get('session_id', '')
        goal = data.get('goal', 'optimize')

        if not hasattr(shared_state, '_v733_ice_sessions') or session_id not in shared_state._v733_ice_sessions:
            return jsonify({'error': f'Session {session_id} not found'}), 404

        ice = shared_state._v733_ice_sessions[session_id]
        result = ice.run_cycle(goal)

        return jsonify({
            'session_id': session_id,
            'goal': goal,
            'cycle_result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ice/decide_and_write', methods=['POST'])
def api_v733_ice_decide_and_write():
    """
    ICE决定并写入 (decide + actuate + 返回SOP报告)

    POST body:
      session_id: str   ICE会话ID
      goal: str          目标描述
    """
    try:
        data = request.get_json(force=True) or {}
        session_id = data.get('session_id', '')
        goal = data.get('goal', 'optimize')

        if not hasattr(shared_state, '_v733_ice_sessions') or session_id not in shared_state._v733_ice_sessions:
            return jsonify({'error': f'Session {session_id} not found'}), 404

        ice = shared_state._v733_ice_sessions[session_id]
        report = ice.decide_and_write(goal)

        if hasattr(report, 'to_dict'):
            return jsonify({'session_id': session_id, 'report': report.to_dict()})
        else:
            return jsonify({'session_id': session_id, 'report': str(report)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lean/export_abc', methods=['POST'])
def api_v733_lean_export_abc():
    """
    Lean4 ABC弱形式导出

    POST body:
      mass_face: float      MASS_FACE值
      excess_loop: float     过剩环路值
    """
    try:
        from modules.M225_ICELeanLoop import LeanExporter
        data = request.get_json(force=True) or {}
        mass_face = float(data.get('mass_face', 0.0))
        excess_loop = float(data.get('excess_loop', 0.0))

        exporter = LeanExporter()
        lean_code = exporter.export_abc_weak(mass_face, excess_loop)

        return jsonify({
            'mass_face': mass_face,
            'excess_loop': excess_loop,
            'lean_code': lean_code,
            'exporter_state': exporter.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lean/export_riemann', methods=['POST'])
def api_v733_lean_export_riemann():
    """
    Lean4 Riemann提示导出

    POST body:
      mass_face: float      MASS_FACE值
      excess_loop: float     过剩环路值
    """
    try:
        from modules.M225_ICELeanLoop import LeanExporter
        data = request.get_json(force=True) or {}
        mass_face = float(data.get('mass_face', 0.0))
        excess_loop = float(data.get('excess_loop', 0.0))

        exporter = LeanExporter()
        lean_code = exporter.export_riemann_hint(mass_face, excess_loop)

        return jsonify({
            'mass_face': mass_face,
            'excess_loop': excess_loop,
            'lean_code': lean_code
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lean/export_custom', methods=['POST'])
def api_v733_lean_export_custom():
    """
    自定义Lean4定理导出

    POST body:
      theorem_name: str     定理名
      statement: str         定理陈述
      proof_sketch: str      证明草稿 (optional)
    """
    try:
        from modules.M225_ICELeanLoop import LeanExporter
        data = request.get_json(force=True) or {}
        theorem_name = data.get('theorem_name', 'custom_theorem')
        statement = data.get('statement', 'True')
        proof_sketch = data.get('proof_sketch', '')

        exporter = LeanExporter()
        lean_code = exporter.export_custom(theorem_name, statement, proof_sketch)

        return jsonify({
            'theorem_name': theorem_name,
            'statement': statement,
            'lean_code': lean_code
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lean/loop', methods=['POST'])
def api_v733_lean_loop():
    """
    ICE-Lean4自动迭代闭环

    POST body:
      phenomenon: str       现象描述
      theorem_type: str     定理类型 ("abc_weak"/"riemann"/default "abc_weak")
      max_rounds: int       最大迭代轮数 (default 3)
    """
    try:
        from modules.M225_ICELeanLoop import JinlingHeap, JinlingSphere, ICESession, LeanExporter, ICELeanLoop
        import random
        data = request.get_json(force=True) or {}
        phenomenon = data.get('phenomenon', 'unspecified')
        theorem_type = data.get('theorem_type', 'abc_weak')
        max_rounds = int(data.get('max_rounds', 3))

        # 创建ICE会话
        heap = JinlingHeap()
        for i in range(5):
            sphere = JinlingSphere(
                sid=f"S{i}", i_int=random.randint(1, 5),
                ports=[f"p{j}" for j in range(random.randint(1, 3))],
                chi=random.randint(1, 3), mod=random.randint(1, 7),
                phase=random.gauss(0, 1)
            )
            heap.add_sphere(sphere)

        ice = ICESession(heap, mass_threshold=1.0)
        exporter = LeanExporter()
        loop = ICELeanLoop(ice, max_rounds=max_rounds)

        result = loop.run(phenomenon=phenomenon, theorem_type=theorem_type)

        return jsonify({
            'phenomenon': phenomenon,
            'theorem_type': theorem_type,
            'max_rounds': max_rounds,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/hap/protocol', methods=['POST'])
def api_v733_hap_protocol():
    """
    HAP人类-AGI联合证明协议 (5步)

    POST body:
      intent: str           人类意图描述
      theorem_type: str     定理类型 (default "abc_weak")
    """
    try:
        from modules.M225_ICELeanLoop import JinlingHeap, JinlingSphere, ICESession, HAPProtocol
        import random
        data = request.get_json(force=True) or {}
        intent = data.get('intent', 'unspecified')
        theorem_type = data.get('theorem_type', 'abc_weak')

        heap = JinlingHeap()
        for i in range(5):
            sphere = JinlingSphere(
                sid=f"S{i}", i_int=random.randint(1, 5),
                ports=[f"p{j}" for j in range(random.randint(1, 3))],
                chi=random.randint(1, 3), mod=random.randint(1, 7),
                phase=random.gauss(0, 1)
            )
            heap.add_sphere(sphere)

        ice = ICESession(heap, mass_threshold=1.0)
        hap = HAPProtocol(ice)

        result = hap.run_full_protocol(intent=intent, theorem_type=theorem_type)

        return jsonify({
            'intent': intent,
            'theorem_type': theorem_type,
            'protocol_result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/hap/step/<int:step_num>', methods=['POST'])
def api_v733_hap_step(step_num):
    """
    HAP协议单步执行

    POST body:
      session_id: str       ICE会话ID (1-2步需要)
      intent: str           人类意图
      theorem_type: str     定理类型 (3-5步)
      converged: bool       是否收敛 (5步)
    """
    try:
        from modules.M225_ICELeanLoop import HAPProtocol, ICESession
        data = request.get_json(force=True) or {}
        intent = data.get('intent', 'unspecified')
        theorem_type = data.get('theorem_type', 'abc_weak')

        session_id = data.get('session_id', '')
        if not hasattr(shared_state, '_v733_ice_sessions') or session_id not in shared_state._v733_ice_sessions:
            return jsonify({'error': f'Session {session_id} not found. Create one first via /ice/create_session'}), 404

        ice = shared_state._v733_ice_sessions[session_id]
        hap = HAPProtocol(ice)

        if step_num == 1:
            result = hap.step1_human_intent(intent)
        elif step_num == 2:
            result = hap.step2_agi_structure(intent)
        elif step_num == 3:
            result = hap.step3_human_formalize(intent, theorem_type)
        elif step_num == 4:
            result = hap.step4_agi_verify(intent, theorem_type)
        elif step_num == 5:
            converged = data.get('converged', True)
            result = hap.step5_human_review(converged)
        else:
            return jsonify({'error': f'Invalid step: {step_num}. Must be 1-5'}), 400

        return jsonify({'step': step_num, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m225/state', methods=['GET'])
def api_v733_m225_state():
    """M225模块状态查询"""
    try:
        from modules.M225_ICELeanLoop import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m225/theorems', methods=['GET'])
def api_v733_m225_theorems():
    """M225定理验证 (T2.37-T2.39)"""
    try:
        from modules.M225_ICELeanLoop import verify_theorem_t237, verify_theorem_t238, verify_theorem_t239
        t237 = verify_theorem_t237()
        t238 = verify_theorem_t238()
        t239 = verify_theorem_t239()
        return jsonify({
            'T237': t237,
            'T238': t238,
            'T239': t239,
            'all_passed': t237.get('passed', False) and t238.get('passed', False) and t239.get('passed', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M226 PCTChecker — PCT端口兼容性定理引擎 (T2.40)
# ══════════════════════════════════════════════════

@bp.route('/pct/check', methods=['POST'])
def api_v733_pct_check():
    """
    PCT四条件兼容性校验

    POST body:
      src: {ports, phase, chi, grade, name}   源金灵球
      dst: {ports, phase, chi, grade, name}   目标金灵球
      target_phase: float                      目标相位 (default 0.0)
      tolerance: float                         相位容差 (default 0.3)
    """
    try:
        from modules.M226_PCTChecker import PCTChecker, PCTSphere
        data = request.get_json(force=True) or {}
        src_data = data.get('src', {})
        dst_data = data.get('dst', {})
        target_phase = float(data.get('target_phase', 0.0))
        tolerance = float(data.get('tolerance', 0.3))

        src = PCTSphere(
            ports=int(src_data.get('ports', 0)),
            phase=float(src_data.get('phase', 0.0)),
            chi=int(src_data.get('chi', 0)),
            grade=int(src_data.get('grade', 0)),
            name=src_data.get('name', ''),
        )
        dst = PCTSphere(
            ports=int(dst_data.get('ports', 0)),
            phase=float(dst_data.get('phase', 0.0)),
            chi=int(dst_data.get('chi', 0)),
            grade=int(dst_data.get('grade', 0)),
            name=dst_data.get('name', ''),
        )

        checker = PCTChecker()
        result = checker.check_pct(src, dst, target_phase=target_phase, tolerance=tolerance)

        return jsonify({
            'src': {'name': src.name, 'ports': src.ports, 'phase': src.phase, 'chi': src.chi, 'grade': src.grade},
            'dst': {'name': dst.name, 'ports': dst.ports, 'phase': dst.phase, 'chi': dst.chi, 'grade': dst.grade},
            'result': {
                'direction_ok': result.direction_ok,
                'chirality_ok': result.chirality_ok,
                'phase_ok': result.phase_ok,
                'grade_ok': result.grade_ok,
                'compatible': result.compatible,
                'details': result.details,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/pct/score', methods=['POST'])
def api_v733_pct_score():
    """
    PCT兼容性评分 (0-4)

    POST body:
      src: {ports, phase, chi, grade, name}
      dst: {ports, phase, chi, grade, name}
    """
    try:
        from modules.M226_PCTChecker import PCTChecker, PCTSphere
        data = request.get_json(force=True) or {}
        src_data = data.get('src', {})
        dst_data = data.get('dst', {})

        src = PCTSphere(
            ports=int(src_data.get('ports', 0)), phase=float(src_data.get('phase', 0.0)),
            chi=int(src_data.get('chi', 0)), grade=int(src_data.get('grade', 0)),
            name=src_data.get('name', ''),
        )
        dst = PCTSphere(
            ports=int(dst_data.get('ports', 0)), phase=float(dst_data.get('phase', 0.0)),
            chi=int(dst_data.get('chi', 0)), grade=int(dst_data.get('grade', 0)),
            name=dst_data.get('name', ''),
        )

        checker = PCTChecker()
        score = checker.pct_score(src, dst)
        compatible = checker.is_port_compatible(src, dst)

        return jsonify({'score': score, 'compatible': compatible, 'max_score': 4})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/pct/filter_candidates', methods=['POST'])
def api_v733_pct_filter_candidates():
    """
    β-Rewire候选边PCT过滤

    POST body:
      spheres: [{name, ports, phase, chi, mod, grade}, ...]
      min_score: int   最低分数 (default 3)
    """
    try:
        from modules.M226_PCTChecker import PCTChecker, PCTSphere
        data = request.get_json(force=True) or {}
        spheres_data = data.get('spheres', [])
        min_score = int(data.get('min_score', 3))

        checker = PCTChecker()
        spheres = []
        for s in spheres_data:
            spheres.append(PCTSphere(
                ports=int(s.get('ports', 0)), phase=float(s.get('phase', 0.0)),
                chi=int(s.get('chi', 0)), mod=float(s.get('mod', 1.0)),
                grade=int(s.get('grade', 0)), name=s.get('name', ''),
            ))

        candidates = checker.filter_rewire_candidates(spheres, min_score=min_score)
        serialized = []
        for c in candidates:
            serialized.append({
                'src_name': c.src_name, 'dst_name': c.dst_name,
                'port_src': c.port_src, 'port_dst': c.port_dst,
                'tag': c.tag,
                'compatible': c.pct_result.compatible,
                'score': sum([c.pct_result.direction_ok, c.pct_result.chirality_ok,
                             c.pct_result.phase_ok, c.pct_result.grade_ok]),
            })

        return jsonify({'candidates': serialized, 'total': len(serialized), 'min_score': min_score})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m226/state', methods=['GET'])
def api_v733_m226_state():
    """M226模块状态查询"""
    try:
        from modules.M226_PCTChecker import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m226/theorems', methods=['GET'])
def api_v733_m226_theorems():
    """M226定理验证 (T2.40)"""
    try:
        from modules.M226_PCTChecker import verify_theorem_t240
        t240 = verify_theorem_t240()
        return jsonify({'T240': t240, 'all_passed': t240.get('passed', False)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M155 IDO — Ftel信息力增强 + 时间箭头 (T2.41)
# ══════════════════════════════════════════════════

@bp.route('/ido/info_amount', methods=['POST'])
def api_v733_ido_info_amount():
    """
    计算图Shannon信息量

    POST body:
      heap: {node_id: degree, ...}   度分布字典
    """
    try:
        from modules.M155_FtelOptimizer import get_instance
        data = request.get_json(force=True) or {}
        heap = data.get('heap', {})
        heap_float = {k: float(v) for k, v in heap.items()}

        engine = get_instance()
        result = engine.api_info_amount(heap_float)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ido/info_force', methods=['POST'])
def api_v733_ido_info_force():
    """
    计算节点信息力梯度

    POST body:
      node_id: str                    目标节点
      heap: {node_id: degree, ...}    度分布字典
    """
    try:
        from modules.M155_FtelOptimizer import get_instance
        data = request.get_json(force=True) or {}
        node_id = data.get('node_id', '')
        heap = data.get('heap', {})
        heap_float = {k: float(v) for k, v in heap.items()}

        engine = get_instance()
        result = engine.api_info_force(node_id, heap_float)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ido/update', methods=['POST'])
def api_v733_ido_update():
    """
    IDO信息力驱动mod微调

    POST body:
      node_id: str                     目标节点
      heap: {node_id: degree, ...}     度分布字典
      current_mod: float               当前mod值 (default 1.0)
      dt: float                        时间步长 (default 0.1)
    """
    try:
        from modules.M155_FtelOptimizer import get_instance
        data = request.get_json(force=True) or {}
        node_id = data.get('node_id', '')
        heap = data.get('heap', {})
        heap_float = {k: float(v) for k, v in heap.items()}
        current_mod = float(data.get('current_mod', 1.0))
        dt = float(data.get('dt', 0.1))

        engine = get_instance()
        result = engine.api_ido_update(node_id, heap_float, current_mod, dt)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ido/time_arrow', methods=['POST'])
def api_v733_ido_time_arrow():
    """
    时间箭头判定

    POST body:
      info_history: [float, ...]   信息量历史序列 (optional, 使用内部历史)
    """
    try:
        from modules.M155_FtelOptimizer import get_instance
        data = request.get_json(force=True) or {}
        info_history = data.get('info_history', None)

        engine = get_instance()
        result = engine.api_time_arrow(info_history)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m155/state', methods=['GET'])
def api_v733_m155_state():
    """M155模块状态查询 (含IDO增强)"""
    try:
        from modules.M155_FtelOptimizer import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m155/theorems', methods=['GET'])
def api_v733_m155_theorems():
    """M155定理验证 (T122 + T2.41)"""
    try:
        from modules.M155_FtelOptimizer import get_instance
        engine = get_instance()
        t122 = engine.verify_ftel_least_action()
        t241 = engine.verify_theorem_t241()
        return jsonify({
            'T122': t122,
            'T241': t241,
            'all_passed': t122.get('verified', False) and t241.get('verified', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M227 EML — 指数-对数混合函数引擎 (T2.42)
# ══════════════════════════════════════════════════

@bp.route('/eml/compute', methods=['POST'])
def api_v733_eml_compute():
    """
    EML核心函数 z = exp(x) - log(y)

    POST body:
      x: float   指数参数
      y: float   对数参数 (must > 0)
    """
    try:
        from modules.M227_EMLEngine import get_instance
        data = request.get_json(force=True) or {}
        x = float(data.get('x', 0.0))
        y = float(data.get('y', 1.0))

        engine = get_instance()
        result = engine.eml(x, y)
        return jsonify({'x': x, 'y': y, 'eml_result': result, 'formula': 'exp(x) - log(y)'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/eml/add', methods=['POST'])
def api_v733_eml_add():
    """
    EML加法近似 eml_add(a, b) ≈ a + b

    POST body:
      a: float
      b: float
    """
    try:
        from modules.M227_EMLEngine import get_instance
        data = request.get_json(force=True) or {}
        a = float(data.get('a', 0.0))
        b = float(data.get('b', 0.0))

        engine = get_instance()
        eml_result = engine.eml_add(a, b)
        classic = a + b
        error = abs(eml_result - classic)
        return jsonify({
            'a': a, 'b': b,
            'eml_add': eml_result,
            'classic_add': classic,
            'absolute_error': error,
            'relative_error': error / max(abs(classic), 1e-15)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/eml/mul', methods=['POST'])
def api_v733_eml_mul():
    """
    EML乘法 eml_mul(a, b) = exp(ln a + ln b) = a·b

    POST body:
      a: float   (must > 0)
      b: float   (must > 0)
    """
    try:
        from modules.M227_EMLEngine import get_instance
        data = request.get_json(force=True) or {}
        a = float(data.get('a', 1.0))
        b = float(data.get('b', 1.0))

        engine = get_instance()
        eml_result = engine.eml_mul(a, b)
        classic = a * b
        error = abs(eml_result - classic)
        return jsonify({
            'a': a, 'b': b,
            'eml_mul': eml_result,
            'classic_mul': classic,
            'absolute_error': error,
            'relative_error': error / max(abs(classic), 1e-15)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/eml/polar_multiply', methods=['POST'])
def api_v733_eml_polar_multiply():
    """
    EML极坐标数乘法 (m⊗e^{iθ})

    POST body:
      a: {m, theta}   第一个极坐标数
      b: {m, theta}   第二个极坐标数
    """
    try:
        from modules.M227_EMLEngine import get_instance, EMLNumber
        data = request.get_json(force=True) or {}
        a_data = data.get('a', {'m': 1.0, 'theta': 0.0})
        b_data = data.get('b', {'m': 1.0, 'theta': 0.0})

        engine = get_instance()
        a = EMLNumber(m=float(a_data.get('m', 1.0)), theta=float(a_data.get('theta', 0.0)))
        b = EMLNumber(m=float(b_data.get('m', 1.0)), theta=float(b_data.get('theta', 0.0)))
        result = engine.eml_multiply(a, b)

        return jsonify({
            'a': {'m': a.m, 'theta': a.theta},
            'b': {'m': b.m, 'theta': b.theta},
            'product': {'m': result.m, 'theta': result.theta}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/eml/polar_add', methods=['POST'])
def api_v733_eml_polar_add():
    """
    EML极坐标数加法 (转笛卡尔→加→转回)

    POST body:
      a: {m, theta}   第一个极坐标数
      b: {m, theta}   第二个极坐标数
    """
    try:
        from modules.M227_EMLEngine import get_instance, EMLNumber
        data = request.get_json(force=True) or {}
        a_data = data.get('a', {'m': 1.0, 'theta': 0.0})
        b_data = data.get('b', {'m': 1.0, 'theta': 0.0})

        engine = get_instance()
        a = EMLNumber(m=float(a_data.get('m', 1.0)), theta=float(a_data.get('theta', 0.0)))
        b = EMLNumber(m=float(b_data.get('m', 1.0)), theta=float(b_data.get('theta', 0.0)))
        result = engine.eml_add_polar(a, b)

        return jsonify({
            'a': {'m': a.m, 'theta': a.theta},
            'b': {'m': b.m, 'theta': b.theta},
            'sum': {'m': result.m, 'theta': result.theta}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/eml/comparison', methods=['POST'])
def api_v733_eml_comparison():
    """
    经典运算 vs EML运算对比

    POST body:
      x: float
      y: float
    """
    try:
        from modules.M227_EMLEngine import get_instance
        data = request.get_json(force=True) or {}
        x = float(data.get('x', 1.0))
        y = float(data.get('y', 2.0))

        engine = get_instance()
        comparison = engine.eml_comparison(x, y)
        return jsonify({'x': x, 'y': y, 'comparison': comparison})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m227/state', methods=['GET'])
def api_v733_m227_state():
    """M227模块状态查询"""
    try:
        from modules.M227_EMLEngine import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m227/theorems', methods=['GET'])
def api_v733_m227_theorems():
    """M227定理验证 (T2.42)"""
    try:
        from modules.M227_EMLEngine import get_instance
        engine = get_instance()
        t242 = engine.verify_theorem()
        return jsonify({'T242': t242, 'all_passed': t242.get('pass', False)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M228 LiuMechanism — Liu机制变分原理引擎 (T2.43)
# ══════════════════════════════════════════════════

@bp.route('/liu/action', methods=['POST'])
def api_v733_liu_action():
    """
    Liu作用量 S = Σ(T_i - V_i)

    POST body:
      heap: {V: [{sid, i_int, ports, chi, mod, phase}, ...], E: [{src, dst, w}, ...]}
      (不提供heap则使用demo heap)
    """
    try:
        from modules.M228_LiuMechanism import get_instance
        data = request.get_json(force=True) or {}

        engine = get_instance()
        if 'heap' in data and data['heap']:
            heap = engine.heap_from_dict(data['heap'])
        else:
            heap = engine.create_demo_heap(n_spheres=5, n_edges=4)

        action = engine.compute_action(heap)
        return jsonify({'action': action, 'sphere_count': len(heap.V), 'edge_count': len(heap.E)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/liu/variation', methods=['POST'])
def api_v733_liu_variation():
    """
    Liu变分 δS (对每个球相位施加微扰)

    POST body:
      heap: {V: [...], E: [...]}   (optional, 使用demo)
      epsilon: float               微扰大小 (default 0.01)
    """
    try:
        from modules.M228_LiuMechanism import get_instance
        data = request.get_json(force=True) or {}
        epsilon = float(data.get('epsilon', 0.01))

        engine = get_instance()
        if 'heap' in data and data['heap']:
            heap = engine.heap_from_dict(data['heap'])
        else:
            heap = engine.create_demo_heap(n_spheres=5, n_edges=4)

        variation = engine.compute_variation(heap, epsilon=epsilon)
        return jsonify({'variation': variation, 'epsilon': epsilon, 'sphere_count': len(heap.V)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/liu/equilibrium', methods=['POST'])
def api_v733_liu_equilibrium():
    """
    Liu平衡判定 δS < threshold

    POST body:
      heap: {V: [...], E: [...]}   (optional, 使用demo)
      threshold: float              平衡阈值 (default 0.1)
    """
    try:
        from modules.M228_LiuMechanism import get_instance
        data = request.get_json(force=True) or {}
        threshold = float(data.get('threshold', 0.1))

        engine = get_instance()
        if 'heap' in data and data['heap']:
            heap = engine.heap_from_dict(data['heap'])
        else:
            heap = engine.create_demo_heap(n_spheres=5, n_edges=4)

        is_eq = engine.check_equilibrium(heap, threshold=threshold)
        variation = engine.compute_variation(heap)
        return jsonify({'is_equilibrium': is_eq, 'variation': variation, 'threshold': threshold})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/liu/free_energy', methods=['POST'])
def api_v733_liu_free_energy():
    """
    Liu自由能 F = M - T·H

    POST body:
      heap: {V: [...], E: [...]}   (optional, 使用demo)
      temperature: float            温度参数 (default 1.0)
    """
    try:
        from modules.M228_LiuMechanism import get_instance
        data = request.get_json(force=True) or {}
        temperature = float(data.get('temperature', 1.0))

        engine = get_instance()
        if 'heap' in data and data['heap']:
            heap = engine.heap_from_dict(data['heap'])
        else:
            heap = engine.create_demo_heap(n_spheres=5, n_edges=4)

        free_energy = engine.compute_free_energy(heap, temperature=temperature)
        return jsonify({'free_energy': free_energy, 'temperature': temperature, 'edge_count': len(heap.E)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/liu/evolution', methods=['POST'])
def api_v733_liu_evolution():
    """
    Liu演化方向判定 (equilibrium/minimizing/expanding)

    POST body:
      heap: {V: [...], E: [...]}   (optional, 使用demo)
    """
    try:
        from modules.M228_LiuMechanism import get_instance
        data = request.get_json(force=True) or {}

        engine = get_instance()
        if 'heap' in data and data['heap']:
            heap = engine.heap_from_dict(data['heap'])
        else:
            heap = engine.create_demo_heap(n_spheres=5, n_edges=4)

        evolution = engine.compute_evolution_direction(heap)
        return jsonify({'evolution': evolution, 'sphere_count': len(heap.V), 'edge_count': len(heap.E)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/liu/full_analysis', methods=['POST'])
def api_v733_liu_full_analysis():
    """
    Liu机制全量分析 (action + variation + equilibrium + free_energy + evolution)

    POST body:
      heap: {V: [...], E: [...]}   (optional, 使用demo)
      epsilon: float               微扰 (default 0.01)
      threshold: float             平衡阈值 (default 0.1)
      temperature: float           温度 (default 1.0)
    """
    try:
        from modules.M228_LiuMechanism import get_instance
        data = request.get_json(force=True) or {}
        epsilon = float(data.get('epsilon', 0.01))
        threshold = float(data.get('threshold', 0.1))
        temperature = float(data.get('temperature', 1.0))

        engine = get_instance()
        if 'heap' in data and data['heap']:
            heap = engine.heap_from_dict(data['heap'])
        else:
            heap = engine.create_demo_heap(n_spheres=5, n_edges=4)

        analysis = engine.full_analysis(heap, epsilon=epsilon, threshold=threshold, temperature=temperature)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m228/state', methods=['GET'])
def api_v733_m228_state():
    """M228模块状态查询"""
    try:
        from modules.M228_LiuMechanism import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m228/theorems', methods=['GET'])
def api_v733_m228_theorems():
    """M228定理验证 (T2.43)"""
    try:
        from modules.M228_LiuMechanism import get_instance
        engine = get_instance()
        t243 = engine.verify_theorem()
        return jsonify({'T243': t243, 'all_passed': t243.get('pass', False)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M229 ActionSurfaceRouter — 混合动作面路由器 (PhoneHarness)
# ══════════════════════════════════════════════════

@bp.route('/router/route', methods=['POST'])
def api_v733_router_route():
    """
    路由任务到最佳动作面

    POST body:
      task: str   任务描述
    """
    try:
        from modules.M229_ActionSurfaceRouter import get_instance
        data = request.get_json(force=True) or {}
        task = data.get('task', '')

        engine = get_instance()
        result = engine.route_task(task)
        return jsonify({
            'task': result.task,
            'surface': result.surface.value,
            'confidence': result.confidence,
            'reason': result.reason,
            'affinity_scores': result.affinity_scores,
            'alternatives': [{'surface': s.value, 'score': round(sc, 4)} for s, sc in result.alternatives],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/router/surfaces', methods=['GET'])
def api_v733_router_surfaces():
    """查询所有动作面状态"""
    try:
        from modules.M229_ActionSurfaceRouter import get_instance
        engine = get_instance()
        return jsonify(engine.get_surface_status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/router/surface/<surface_name>', methods=['GET'])
def api_v733_router_surface_detail(surface_name):
    """查询单个动作面详情"""
    try:
        from modules.M229_ActionSurfaceRouter import get_instance
        engine = get_instance()
        return jsonify(engine.get_surface_status(surface_name))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/router/workflow', methods=['POST'])
def api_v733_router_workflow():
    """
    执行跨动作面工作流

    POST body:
      tasks: [str]   任务列表
    """
    try:
        from modules.M229_ActionSurfaceRouter import get_instance
        data = request.get_json(force=True) or {}
        tasks = data.get('tasks', [])

        engine = get_instance()
        result = engine.execute_workflow(tasks)
        return jsonify({
            'workflow_id': result.workflow_id,
            'success': result.success,
            'total_duration_ms': result.total_duration_ms,
            'surface_transitions': result.surface_transitions,
            'steps': [{
                'step_id': s.step_id,
                'task': s.task,
                'surface': s.surface.value,
                'status': s.status,
            } for s in result.steps],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m229/state', methods=['GET'])
def api_v733_m229_state():
    """M229模块状态查询"""
    try:
        from modules.M229_ActionSurfaceRouter import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m229/theorems', methods=['GET'])
def api_v733_m229_theorems():
    """M229定理验证 (T2.44)"""
    try:
        from modules.M229_ActionSurfaceRouter import get_instance
        engine = get_instance()
        t244 = engine.verify_theorem()
        return jsonify({'T244': t244, 'all_passed': t244.get('pass', False)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M230 SideEffectVerifier — 可验证副作用引擎 (PhoneHarness)
# ══════════════════════════════════════════════════

@bp.route('/verifier/register', methods=['POST'])
def api_v733_verifier_register():
    """
    注册预期副作用

    POST body:
      operation: str            操作描述
      effect_type: str          persist/topology/state/evidence
      expected_state: dict      预期操作后状态
      pre_state: dict           操作前状态(optional)
    """
    try:
        from modules.M230_SideEffectVerifier import get_instance
        data = request.get_json(force=True) or {}
        operation = data.get('operation', '')
        effect_type = data.get('effect_type', 'persist')
        expected_state = data.get('expected_state', {})
        pre_state = data.get('pre_state')

        engine = get_instance()
        ticket = engine.register_effect(operation, effect_type, expected_state, pre_state)
        return jsonify({
            'ticket_id': ticket.ticket_id,
            'operation': ticket.operation,
            'effect_type': ticket.effect_type.value,
            'pre_hash': ticket.pre_hash,
            'status': ticket.status.value,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verifier/verify', methods=['POST'])
def api_v733_verifier_verify():
    """
    验证副作用是否真实发生

    POST body:
      ticket_id: str     副作用票据ID
      post_state: dict   操作后实际状态
    """
    try:
        from modules.M230_SideEffectVerifier import get_instance
        data = request.get_json(force=True) or {}
        ticket_id = data.get('ticket_id', '')
        post_state = data.get('post_state')

        engine = get_instance()
        result = engine.verify_effect(ticket_id, post_state)
        return jsonify({
            'ticket_id': result.ticket_id,
            'status': result.status.value,
            'hash_changed': result.hash_match,
            'integrity': result.integrity,
            'details': result.details,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verifier/batch', methods=['POST'])
def api_v733_verifier_batch():
    """
    批量验证副作用

    POST body:
      ticket_ids: [str]        票据ID列表
      post_states: {id: dict}  各票据对应post_state
    """
    try:
        from modules.M230_SideEffectVerifier import get_instance
        data = request.get_json(force=True) or {}
        ticket_ids = data.get('ticket_ids', [])
        post_states = data.get('post_states', {})

        engine = get_instance()
        result = engine.batch_verify(ticket_ids, post_states)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verifier/audit', methods=['GET'])
def api_v733_verifier_audit():
    """查询审计轨迹"""
    try:
        from modules.M230_SideEffectVerifier import get_instance
        engine = get_instance()
        return jsonify(engine.audit_trail())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m230/state', methods=['GET'])
def api_v733_m230_state():
    """M230模块状态查询"""
    try:
        from modules.M230_SideEffectVerifier import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m230/theorems', methods=['GET'])
def api_v733_m230_theorems():
    """M230定理验证 (T2.45)"""
    try:
        from modules.M230_SideEffectVerifier import get_instance
        engine = get_instance()
        t245 = engine.verify_theorem()
        return jsonify({'T245': t245, 'all_passed': t245.get('pass', False)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M231 FailureAttributor — 失败归因引擎 (PhoneHarness)
# ══════════════════════════════════════════════════

@bp.route('/attributor/attribute', methods=['POST'])
def api_v733_attributor_attribute():
    """
    对失败测试进行归因

    POST body:
      test_name: str       测试名称
      error_message: str   错误信息
      exception_type: str  异常类型(optional)
      traceback_str: str   堆栈跟踪(optional)
    """
    try:
        from modules.M231_FailureAttributor import get_instance
        data = request.get_json(force=True) or {}
        test_name = data.get('test_name', '')
        error_message = data.get('error_message', '')
        exception_type = data.get('exception_type', '')
        traceback_str = data.get('traceback_str', '')

        engine = get_instance()
        result = engine.attribute_failure(test_name, error_message, exception_type, traceback_str)
        return jsonify({
            'failure_id': result.failure_id,
            'primary_category': result.primary_category.value,
            'confidence': result.confidence,
            'all_scores': result.all_scores,
            'evidence': result.evidence,
            'fix_suggestion': result.fix_suggestion,
            'secondary_categories': [c.value for c in result.secondary_categories],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/attributor/root_cause', methods=['POST'])
def api_v733_attributor_root_cause():
    """
    追踪根因

    POST body:
      failure_ids: [str]   失败ID列表(optional)
    """
    try:
        from modules.M231_FailureAttributor import get_instance
        data = request.get_json(force=True) or {}
        failure_ids = data.get('failure_ids')

        engine = get_instance()
        root = engine.trace_root_cause(failure_ids)
        return jsonify({
            'root_category': root.root_category.value,
            'root_evidence': root.root_evidence,
            'chain': root.chain,
            'suggested_fix': root.suggested_fix,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/attributor/fix', methods=['POST'])
def api_v733_attributor_fix():
    """
    生成修复建议

    POST body:
      (同attribute接口)
    """
    try:
        from modules.M231_FailureAttributor import get_instance
        data = request.get_json(force=True) or {}
        test_name = data.get('test_name', '')
        error_message = data.get('error_message', '')
        exception_type = data.get('exception_type', '')

        engine = get_instance()
        attr = engine.attribute_failure(test_name, error_message, exception_type)
        fix = engine.suggest_fix(attr)
        return jsonify(fix)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m231/state', methods=['GET'])
def api_v733_m231_state():
    """M231模块状态查询"""
    try:
        from modules.M231_FailureAttributor import get_instance
        inst = get_instance()
        return jsonify(inst.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m231/theorems', methods=['GET'])
def api_v733_m231_theorems():
    """M231定理验证 (T2.46)"""
    try:
        from modules.M231_FailureAttributor import get_instance
        engine = get_instance()
        t246 = engine.verify_theorem()
        return jsonify({'T246': t246, 'all_passed': t246.get('pass', False)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# v733 全局状态与总览
# ══════════════════════════════════════════════════

@bp.route('/overview', methods=['GET'])
def api_v733_overview():
    """v7.33c TMK模块全局总览"""
    try:
        from modules.M223_GoldenSymbol3D import get_instance as m223_inst
        from modules.M224_SOPGeneratorEngine import get_instance as m224_inst
        from modules.M225_ICELeanLoop import get_instance as m225_inst
        from modules.M226_PCTChecker import get_instance as m226_inst
        from modules.M155_FtelOptimizer import get_instance as m155_inst
        from modules.M227_EMLEngine import get_instance as m227_inst
        from modules.M228_LiuMechanism import get_instance as m228_inst
        from modules.M229_ActionSurfaceRouter import get_instance as m229_inst
        from modules.M230_SideEffectVerifier import get_instance as m230_inst
        from modules.M231_FailureAttributor import get_instance as m231_inst

        return jsonify({
            'version': 'v7.33c',
            'codename': 'TMK (太一万有理论六合统合 + EML + Liu机制 + PhoneHarness混合动作面)',
            'modules': {
                'M223': {'name': 'GoldenSymbol3D', 'desc': '金符学3D复广数+MNQ8能流引擎', 'state': m223_inst().get_state()},
                'M224': {'name': 'SOPGeneratorEngine', 'desc': 'SOP六体系自动生成引擎', 'state': m224_inst().get_state()},
                'M225': {'name': 'ICELeanLoop', 'desc': 'ICE自指闭环+Lean4对接+HAP协议', 'state': m225_inst().get_state()},
                'M226': {'name': 'PCTChecker', 'desc': 'PCT端口兼容性定理引擎', 'state': m226_inst().get_state()},
                'M155': {'name': 'FtelOptimizer', 'desc': 'Ftel+IDO信息力+时间箭头', 'state': m155_inst().get_state()},
                'M227': {'name': 'EMLEngine', 'desc': 'EML指数-对数混合函数引擎', 'state': m227_inst().get_state()},
                'M228': {'name': 'LiuMechanism', 'desc': 'Liu机制变分原理引擎', 'state': m228_inst().get_state()},
                'M229': {'name': 'ActionSurfaceRouter', 'desc': '混合动作面路由器(PhoneHarness)', 'state': m229_inst().get_state()},
                'M230': {'name': 'SideEffectVerifier', 'desc': '可验证副作用引擎(PhoneHarness)', 'state': m230_inst().get_state()},
                'M231': {'name': 'FailureAttributor', 'desc': '失败归因引擎(PhoneHarness)', 'state': m231_inst().get_state()},
            },
            'theorems': ['T2.32', 'T2.33', 'T2.34', 'T2.35', 'T2.36', 'T2.37', 'T2.38', 'T2.39', 'T2.40', 'T2.41', 'T2.42', 'T2.43', 'T2.44', 'T2.45', 'T2.46'],
            'routes_count': 70,
            'url_prefix': '/api/v733'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/theorems/all', methods=['GET'])
def api_v733_theorems_all():
    """v7.33c 全部定理验证 (T2.32-T2.46)"""
    try:
        from modules.M223_GoldenSymbol3D import verify_theorem_t232, verify_theorem_t233, verify_theorem_t234
        from modules.M224_SOPGeneratorEngine import verify_theorem_t235, verify_theorem_t236
        from modules.M225_ICELeanLoop import verify_theorem_t237, verify_theorem_t238, verify_theorem_t239
        from modules.M226_PCTChecker import verify_theorem_t240
        from modules.M155_FtelOptimizer import get_instance as m155_get
        from modules.M227_EMLEngine import get_instance as m227_get
        from modules.M228_LiuMechanism import get_instance as m228_get
        from modules.M229_ActionSurfaceRouter import get_instance as m229_get
        from modules.M230_SideEffectVerifier import get_instance as m230_get
        from modules.M231_FailureAttributor import get_instance as m231_get

        m155_engine = m155_get()
        m227_engine = m227_get()
        m228_engine = m228_get()
        m229_engine = m229_get()
        m230_engine = m230_get()
        m231_engine = m231_get()

        results = {
            'T232': verify_theorem_t232(),
            'T233': verify_theorem_t233(),
            'T234': verify_theorem_t234(),
            'T235': verify_theorem_t235(),
            'T236': verify_theorem_t236(),
            'T237': verify_theorem_t237(),
            'T238': verify_theorem_t238(),
            'T239': verify_theorem_t239(),
            'T240': verify_theorem_t240(),
            'T241': m155_engine.verify_theorem(),
            'T242': m227_engine.verify_theorem(),
            'T243': m228_engine.verify_theorem(),
            'T244': m229_engine.verify_theorem(),
            'T245': m230_engine.verify_theorem(),
            'T246': m231_engine.verify_theorem(),
        }

        all_passed = all(r.get('pass', False) or r.get('passed', False) or r.get('verified', False) for r in results.values())

        return jsonify({
            'version': 'v7.33c',
            'theorems': results,
            'total': len(results),
            'passed': sum(1 for r in results.values() if r.get('pass', False) or r.get('passed', False) or r.get('verified', False)),
            'failed': sum(1 for r in results.values() if not (r.get('pass', False) or r.get('passed', False) or r.get('verified', False))),
            'all_passed': all_passed
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
