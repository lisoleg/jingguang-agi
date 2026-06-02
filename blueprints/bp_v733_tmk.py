# -*- coding: utf-8 -*-
"""
Blueprint: v733 (28 routes)
M223-M225 — 金符学3D复广数 + MNQ8能流引擎 + SOP六体系自动生成器 + ICE自指闭环+Lean4对接+HAP协议
URL prefix: /api/v733
Version: v7.33 TMK (太一万有理论六合统合)
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
# v733 全局状态与总览
# ══════════════════════════════════════════════════

@bp.route('/overview', methods=['GET'])
def api_v733_overview():
    """v7.33 TMK模块全局总览"""
    try:
        from modules.M223_GoldenSymbol3D import get_instance as m223_inst
        from modules.M224_SOPGeneratorEngine import get_instance as m224_inst
        from modules.M225_ICELeanLoop import get_instance as m225_inst

        return jsonify({
            'version': 'v7.33',
            'codename': 'TMK (太一万有理论六合统合)',
            'modules': {
                'M223': {'name': 'GoldenSymbol3D', 'desc': '金符学3D复广数+MNQ8能流引擎', 'state': m223_inst().get_state()},
                'M224': {'name': 'SOPGeneratorEngine', 'desc': 'SOP六体系自动生成引擎', 'state': m224_inst().get_state()},
                'M225': {'name': 'ICELeanLoop', 'desc': 'ICE自指闭环+Lean4对接+HAP协议', 'state': m225_inst().get_state()},
            },
            'theorems': ['T2.32', 'T2.33', 'T2.34', 'T2.35', 'T2.36', 'T2.37', 'T2.38', 'T2.39'],
            'routes_count': 28,
            'url_prefix': '/api/v733'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/theorems/all', methods=['GET'])
def api_v733_theorems_all():
    """v7.33 全部定理验证 (T2.32-T2.39)"""
    try:
        from modules.M223_GoldenSymbol3D import verify_theorem_t232, verify_theorem_t233, verify_theorem_t234
        from modules.M224_SOPGeneratorEngine import verify_theorem_t235, verify_theorem_t236
        from modules.M225_ICELeanLoop import verify_theorem_t237, verify_theorem_t238, verify_theorem_t239

        results = {
            'T232': verify_theorem_t232(),
            'T233': verify_theorem_t233(),
            'T234': verify_theorem_t234(),
            'T235': verify_theorem_t235(),
            'T236': verify_theorem_t236(),
            'T237': verify_theorem_t237(),
            'T238': verify_theorem_t238(),
            'T239': verify_theorem_t239(),
        }

        all_passed = all(r.get('passed', False) for r in results.values())

        return jsonify({
            'version': 'v7.33',
            'theorems': results,
            'total': len(results),
            'passed': sum(1 for r in results.values() if r.get('passed', False)),
            'failed': sum(1 for r in results.values() if not r.get('passed', False)),
            'all_passed': all_passed
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
