# -*- coding: utf-8 -*-
"""
Blueprint: v732 (10 routes)
M207-M211 — 复合体理学新五大引擎
URL prefix: /api/v732
"""

import math
import shared_state
from flask import Blueprint, request, jsonify

bp = Blueprint('v732', __name__, url_prefix='/api/v732')


# ══════════════════════════════════════════════════
# M207 GoldenSymbol3D — 金符3D复广数+阴龙积+MNQ8能流
# ══════════════════════════════════════════════════

@bp.route('/golden/compute', methods=['POST'])
def api_v732_golden_compute():
    """
    金符3D复广数运算

    POST body:
      z1: [a, b, c]      第一个金符
      z2: [a, b, c]      第二个金符
      lambda: float       阴龙积λ (default: 1.0)
      ops: ["add","mul","yin_long","modulus"]  操作列表

    Returns:
      结果字典
    """
    try:
        from modules.M207_GoldenSymbol3D import GoldenSymbol, yin_long_product
        data = request.get_json(force=True) or {}
        a1, b1, c1 = data.get('z1', [1.0, 0.0, 0.0])
        a2, b2, c2 = data.get('z2', [0.0, 1.0, 0.0])
        lam = float(data.get('lambda', 1.0))
        ops = data.get('ops', ['yin_long', 'modulus'])

        z1 = GoldenSymbol(a1, b1, c1)
        z2 = GoldenSymbol(a2, b2, c2)

        result = {
            'z1': z1.to_dict(),
            'z2': z2.to_dict(),
            'lambda': lam,
        }
        if 'add' in ops:
            s = z1 + z2
            result['add'] = s.to_dict()
        if 'mul' in ops:
            p = z1 * z2
            result['mul'] = p.to_dict()
        if 'yin_long' in ops:
            yl = yin_long_product(z1, z2, lam=lam)
            result['yin_long'] = yl.to_dict()
        if 'modulus' in ops:
            result['modulus_z1'] = round(z1.modulus(), 6)
            result['modulus_z2'] = round(z2.modulus(), 6)
        if 'conjugate' in ops:
            result['conjugate_z1'] = z1.conjugate().to_dict()

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/golden/mnq_grid', methods=['POST'])
def api_v732_golden_mnq_grid():
    """
    MNQ8能流格计算

    POST body:
      rows: int   格行数 (default: 4)
      cols: int   格列数 (default: 4)
      steps: int  演化步数 (default: 5)
      lambda: float  阴龙积λ (default: 1.0)
      theta_bias: float  相位偏置注入 (default: 0.0)

    Returns:
      格状态 + 激活率 + Oloid微分
    """
    try:
        from modules.M207_GoldenSymbol3D import MNQ8Grid
        data = request.get_json(force=True) or {}
        rows = int(data.get('rows', 4))
        cols = int(data.get('cols', 4))
        steps = int(data.get('steps', 5))
        lam = float(data.get('lambda', 1.0))
        theta_bias = float(data.get('theta_bias', 0.0))

        grid = MNQ8Grid(rows, cols, lambda_=lam)
        if theta_bias != 0.0:
            grid.inject_phase(theta_bias)
        step_results = []
        for i in range(steps):
            sr = grid.step()
            step_results.append({
                'step': i + 1,
                'mean_modulus': round(sr.get('mean_modulus', 0), 4),
                'max_modulus': round(sr.get('max_modulus', 0), 4),
            })

        oloid = grid.oloid_differential()
        state = grid.get_state()

        return jsonify({
            'result': {
                'rows': rows,
                'cols': cols,
                'steps_run': steps,
                'step_results': step_results,
                'oloid_differential': {k: round(v, 6) for k, v in oloid.items()},
                'is_locked': grid.is_locked(),
                'final_state': state,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M208 TianxingPhaseLock — 天行相位选择算子
# ══════════════════════════════════════════════════

@bp.route('/tianxing/lock', methods=['POST'])
def api_v732_tianxing_lock():
    """
    天行相位选择 — Π̂_φ锁定

    POST body:
      theta: float       相位角 (弧度, default: π/4)
      noise_level: float 噪声水平 (default: 0.05)
      n_trials: int      重复次数 (default: 10, 用于统计)

    Returns:
      波粒锁定结果 + 统计
    """
    try:
        from modules.M208_TianxingPhaseLock import PhaseSelector, UndeterminedState
        data = request.get_json(force=True) or {}
        theta = float(data.get('theta', math.pi / 4))
        noise_level = float(data.get('noise_level', 0.05))
        n_trials = min(int(data.get('n_trials', 10)), 100)

        ps = PhaseSelector(noise_level)
        results = []
        for _ in range(n_trials):
            state = UndeterminedState(theta_expect=theta)
            r = ps.wave_to_particle(state, theta)
            results.append(r.value)

        up_count = results.count('up')
        down_count = results.count('down')

        return jsonify({
            'result': {
                'theta': round(theta, 6),
                'noise_level': noise_level,
                'n_trials': n_trials,
                'up_count': up_count,
                'down_count': down_count,
                'up_ratio': round(up_count / n_trials, 4),
                'majority': 'up' if up_count >= down_count else 'down',
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M209 AmbiguityEngine — 歧义保留+延迟坍缩
# ══════════════════════════════════════════════════

@bp.route('/ambiguity/register', methods=['POST'])
def api_v732_ambiguity_register():
    """
    注册歧义关系

    POST body:
      rel_id: str         关系标识 (default: "rel_1")
      automorphisms: [{"name": str, "src": str, "tgt": str, "phase_shift": float}, ...]
      readings: [str, ...]  可能读取列表

    Returns:
      G_ambig阶数 + L5多值性
    """
    try:
        from modules.M209_AmbiguityEngine import (
            AmbiguityEngine, AmbiguityAutomorphism, AmbiguityKind
        )
        data = request.get_json(force=True) or {}
        rel_id = data.get('rel_id', 'rel_1')
        autos_raw = data.get('automorphisms', [
            {"name": "default_flip", "src": "A", "tgt": "B", "phase_shift": math.pi}
        ])
        readings = data.get('readings', ['A', 'B'])

        engine = AmbiguityEngine()
        autos = [
            AmbiguityAutomorphism(
                name=a.get('name', 'auto'),
                source_reading=a.get('src', 'A'),
                target_reading=a.get('tgt', 'B'),
                kind=AmbiguityKind.SEMANTIC,
                phase_shift=float(a.get('phase_shift', math.pi)),
            )
            for a in autos_raw
        ]
        group = engine.register_ambiguity(rel_id, autos)
        proj = engine.retain_ambiguity(rel_id, readings)
        l5 = proj.compute_projection()

        return jsonify({
            'result': {
                'rel_id': rel_id,
                'g_ambig': group.to_dict(),
                'l5_projection': l5,
                'is_nontrivial': group.is_nontrivial,
                'l5_cardinality': engine.l5_projection_cardinality(rel_id),
                'is_ambiguity_not_flaw': engine.is_ambiguity_not_flaw(rel_id),
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ambiguity/collapse', methods=['POST'])
def api_v732_ambiguity_collapse():
    """
    歧义上下文坍缩

    POST body:
      rel_id: str             关系标识
      automorphisms: [...]    歧义自同构列表
      theta_context: float    上下文相位 (0→up, π→down)

    Returns:
      坍缩结果
    """
    try:
        from modules.M209_AmbiguityEngine import (
            AmbiguityEngine, AmbiguityAutomorphism, AmbiguityKind
        )
        data = request.get_json(force=True) or {}
        rel_id = data.get('rel_id', 'rel_1')
        autos_raw = data.get('automorphisms', [
            {"name": "flip", "src": "A", "tgt": "B", "phase_shift": math.pi}
        ])
        theta_context = float(data.get('theta_context', math.pi / 4))

        engine = AmbiguityEngine()
        autos = [
            AmbiguityAutomorphism(
                name=a.get('name', 'auto'),
                source_reading=a.get('src', 'A'),
                target_reading=a.get('tgt', 'B'),
                kind=AmbiguityKind.SEMANTIC,
                phase_shift=float(a.get('phase_shift', math.pi)),
            )
            for a in autos_raw
        ]
        engine.register_ambiguity(rel_id, autos)
        collapse = engine.collapse_with_context(rel_id, theta_context)

        return jsonify({'result': collapse})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M210 QianmenEightGeneral — 千门八将+ΔS策略审查
# ══════════════════════════════════════════════════

@bp.route('/qianmen/apply_general', methods=['POST'])
def api_v732_qianmen_apply_general():
    """
    应用千门八将手法

    POST body:
      general: str   八将类型 (zheng/ti/fan/tuo/bing/si/jing/kai)
      s_deviate: float  偏离后S_Rel (default: 10.0)
      s_optimal: float  ArgMin最优S_Rel (default: 5.0)

    Returns:
      ΔS量化 + 手法解析
    """
    try:
        from modules.M210_QianmenEightGeneral import (
            QianmenCensorEngine, GeneralType
        )
        data = request.get_json(force=True) or {}
        general_str = data.get('general', 'zheng').lower()
        s_deviate = float(data.get('s_deviate', 10.0))
        s_optimal = float(data.get('s_optimal', 5.0))

        # 类型映射
        gtype_map = {
            'zheng': GeneralType.ZHENG, 'ti': GeneralType.TI,
            'fan': GeneralType.FAN,     'tuo': GeneralType.TUO,
            'bing': GeneralType.BING,   'si': GeneralType.SI,
            'jing': GeneralType.JING,   'kai': GeneralType.KAI,
        }
        gtype = gtype_map.get(general_str, GeneralType.ZHENG)

        engine = QianmenCensorEngine()
        result = engine.apply_general(gtype, s_deviate, s_optimal)

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qianmen/censor_review', methods=['POST'])
def api_v732_qianmen_censor_review():
    """
    千门审查制提案审查

    POST body:
      proposals: [
        {
          "id": str,
          "m": int,          参与金灵球数
          "h": float,        相位混乱度H[Θ]
          "penalty": float,  非自指惩罚
          "has_self_ref": bool,
          "general": str,    使用的千门手法 (可选)
          "delta_s": float   ΔS显式估算 (使用千门时必须)
        }, ...
      ]

    Returns:
      审查结果 + 显隐互转
    """
    try:
        from modules.M210_QianmenEightGeneral import (
            QianmenCensorEngine, SRelEstimate, GeneralType
        )
        data = request.get_json(force=True) or {}
        proposals = data.get('proposals', [
            {"id": "plan_A", "m": 3, "h": 0.2, "penalty": 0.0, "has_self_ref": True}
        ])

        gtype_map = {
            'zheng': GeneralType.ZHENG, 'ti': GeneralType.TI,
            'fan': GeneralType.FAN,     'tuo': GeneralType.TUO,
            'bing': GeneralType.BING,   'si': GeneralType.SI,
            'jing': GeneralType.JING,   'kai': GeneralType.KAI,
        }

        engine = QianmenCensorEngine()
        results = []
        for p in proposals:
            est = SRelEstimate(
                m_count=int(p.get('m', 3)),
                phase_entropy=float(p.get('h', 0.3)),
                penalty=float(p.get('penalty', 0.0)),
            )
            general_used = None
            if 'general' in p:
                general_used = gtype_map.get(p['general'].lower())
            r = engine.submit_proposal(
                p['id'], est,
                has_self_ref=bool(p.get('has_self_ref', True)),
                general_used=general_used,
                delta_s_explicit=p.get('delta_s'),
            )
            results.append(r)

        exchange = engine.manifest_latent_exchange('api_call')
        censor_state = engine.get_state()

        return jsonify({
            'result': {
                'verdicts': results,
                'selected': [r for r in results if r.get('verdict') == 'SELECTED'],
                'latent_count': sum(1 for r in results if r.get('verdict') == 'LATENT'),
                'rejected_count': sum(1 for r in results if r.get('verdict') == 'REJECTED'),
                'manifest_exchange': exchange,
                'censor_state': censor_state,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M211 HexaSysSOP — 六合统合7步SOP
# ══════════════════════════════════════════════════

@bp.route('/hexasys/run_sop', methods=['POST'])
def api_v732_hexasys_run_sop():
    """
    执行六合统合7步SOP

    POST body:
      nodes: [str, ...]             Rel节点列表
      edges: [[src, dst, weight]]   边列表
      input_nodes: [str, ...]       IDO输入节点
      output_nodes: [str, ...]      IDO输出节点
      proposals: [{...}, ...]       刘机制提案
      theta_context: float          天行锁定相位 (default: π/4)
      noise_level: float            噪声水平 (default: 0.05)

    Returns:
      完整7步SOP执行报告
    """
    try:
        from modules.M211_HexaSysSOP import HexaSysSOP
        data = request.get_json(force=True) or {}

        nodes = data.get('nodes', ['A', 'B', 'C'])
        edges_raw = data.get('edges', [['A', 'B', 1.0], ['B', 'C', 0.8]])
        edges = [(e[0], e[1], float(e[2])) for e in edges_raw]
        input_nodes = data.get('input_nodes', [nodes[0]] if nodes else ['A'])
        output_nodes = data.get('output_nodes', [nodes[-1]] if nodes else ['C'])
        proposals = data.get('proposals', [
            {'id': 'plan_default', 'm': 3, 'h': 0.3, 'penalty': 0.0, 'has_self_ref': True}
        ])
        theta_context = float(data.get('theta_context', math.pi / 4))
        noise_level = float(data.get('noise_level', 0.05))

        engine = HexaSysSOP(noise_level=noise_level)
        report = engine.run_full_sop(
            nodes=nodes, edges=edges,
            input_nodes=input_nodes, output_nodes=output_nodes,
            proposals=proposals,
            theta_context=theta_context,
        )

        return jsonify({'result': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/hexasys/state', methods=['GET'])
def api_v732_hexasys_state():
    """
    获取六合统合引擎当前状态 (GET)

    Returns:
      引擎全局状态快照
    """
    try:
        from modules.M211_HexaSysSOP import HexaSysSOP
        engine = HexaSysSOP()
        state = engine.get_state()
        return jsonify({'result': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/hexasys/single_step', methods=['POST'])
def api_v732_hexasys_single_step():
    """
    执行单步SOP

    POST body:
      step: int (1-7)       步骤编号
      params: {}            步骤参数

    Returns:
      单步结果
    """
    try:
        from modules.M211_HexaSysSOP import HexaSysSOP
        data = request.get_json(force=True) or {}
        step = int(data.get('step', 1))
        params = data.get('params', {})

        engine = HexaSysSOP()

        if step == 1:
            nodes = params.get('nodes', ['A', 'B', 'C'])
            edges_raw = params.get('edges', [['A', 'B', 1.0]])
            edges = [(e[0], e[1], float(e[2])) for e in edges_raw]
            r = engine.step1_ty_build_rel(nodes, edges, phi_inj=float(params.get('phi_inj', 1.0)))
        elif step == 2:
            engine.step1_ty_build_rel(
                params.get('nodes', ['A', 'B', 'C']),
                [(e[0], e[1], float(e[2])) for e in params.get('edges', [['A', 'B', 1.0]])],
            )
            r = engine.step2_ido_dual(
                params.get('input_nodes', ['A']),
                params.get('output_nodes', ['C']),
            )
        elif step == 5:
            theta = float(params.get('theta_context', math.pi / 4))
            r = engine.step5_tianxing_lock(theta)
        elif step == 6:
            r = engine.step6_mnq_numeric(
                symbols=params.get('symbols'),
                grid_size=int(params.get('grid_size', 4)),
            )
        else:
            return jsonify({'error': f'step {step} requires prior context; use run_sop instead'}), 400

        return jsonify({
            'result': {
                'step': r.step.value,
                'name': r.step.name,
                'success': r.success,
                'rho_rel': round(r.rho_rel, 4),
                'elapsed_ms': round(r.elapsed_ms, 2),
                'notes': r.notes,
                'output': r.output,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
