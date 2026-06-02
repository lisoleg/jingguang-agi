# -*- coding: utf-8 -*-
"""
Blueprint: v732b (12 routes)
M212-M217 — 复合体理学扩展六大引擎
URL prefix: /api/v732b
"""

import math
import shared_state
from flask import Blueprint, request, jsonify

bp = Blueprint('v732b', __name__, url_prefix='/api/v732b')


# ══════════════════════════════════════════════════
# M212 BloomIdolFreezeEngine — 偶像化伪共识冻结+共振成核
# ══════════════════════════════════════════════════

@bp.route('/bloom/detect_freeze', methods=['POST'])
def api_v732b_bloom_detect_freeze():
    """
    偶像化伪共识冻结检测

    POST body:
      propositions: [{"id": str, "content": str, "consensus": float}, ...]
      bloom_capacity: int     Bloom Table容量 (default: 1000)
      false_positive_rate: float  假阳性率 (default: 0.01)
      freeze_threshold: float     冻结偏心率阈值 (default: 0.9)

    Returns:
      冻结检测结果
    """
    try:
        from modules.M212_BloomIdolFreezeEngine import BloomIdolFreezeEngine
        data = request.get_json(force=True) or {}
        propositions = data.get('propositions', [
            {"id": "p1", "content": "standard_model", "consensus": 0.95}
        ])
        bloom_capacity = int(data.get('bloom_capacity', 1000))
        fp_rate = float(data.get('false_positive_rate', 0.01))
        freeze_threshold = float(data.get('freeze_threshold', 0.9))

        engine = BloomIdolFreezeEngine(
            bloom_capacity=bloom_capacity,
            false_positive_rate=fp_rate,
            freeze_threshold=freeze_threshold
        )
        result = engine.process_cycle(propositions)

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bloom/nucleate', methods=['POST'])
def api_v732b_bloom_nucleate():
    """
    共振成核者(天伤星)触发

    POST body:
      false_prop_id: str      伪命题标识
      iron_evidence: str      铁证内容
      current_e: float        当前偏心率 (default: 0.95)

    Returns:
      成核触发结果
    """
    try:
        from modules.M212_BloomIdolFreezeEngine import (
            BloomIdolFreezeEngine, ResonanceNucleator
        )
        data = request.get_json(force=True) or {}
        false_prop_id = data.get('false_prop_id', 'pseudo_consensus')
        iron_evidence = data.get('iron_evidence', 'contradictory_data')
        current_e = float(data.get('current_e', 0.95))

        engine = BloomIdolFreezeEngine()
        # Register some propositions first
        engine.idol_detector.register_proposition(
            false_prop_id, consensus=0.99
        )
        # Submit iron evidence
        engine.omega_reset.submit_evidence(false_prop_id, iron_evidence)
        # Attempt nucleation
        result = engine.nucleator.attempt_nucleation(
            false_prop_id, iron_evidence, current_e=current_e
        )

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M213 EccentricityGovernance — 偏心率定理+组织寿命
# ══════════════════════════════════════════════════

@bp.route('/eccentricity/analyze', methods=['POST'])
def api_v732b_eccentricity_analyze():
    """
    组织偏心率分析

    POST body:
      C: float           集中度 (default: 0.5)
      D: float           民主度 (default: 0.5)
      gamma: float       衰减率 (default: 0.1)

    Returns:
      偏心率+组织寿命分析
    """
    try:
        from modules.M213_EccentricityGovernance import EccentricityGovernance
        data = request.get_json(force=True) or {}
        C = float(data.get('C', 0.5))
        D = float(data.get('D', 0.5))
        gamma = float(data.get('gamma', 0.1))

        engine = EccentricityGovernance()
        result = engine.analyze_organization(C, D, gamma)

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M214 GoedelEscapeHatch — 哥德尔洞+显密双轨+遁甲
# ══════════════════════════════════════════════════

@bp.route('/goedel/analyze', methods=['POST'])
def api_v732b_goedel_analyze():
    """
    哥德尔洞+显密双轨+遁甲分析

    POST body:
      system_axioms: [str, ...]   系统公理集
      propositions: [str, ...]    待检验命题
      requires_escape: bool       是否需要遁甲逃逸 (default: False)

    Returns:
      哥德尔洞检测+双轨分析+遁甲评估
    """
    try:
        from modules.M214_GoedelEscapeHatch import GoedelEscapeHatch
        data = request.get_json(force=True) or {}
        system_axioms = data.get('system_axioms', ['A1', 'A2', 'A3'])
        propositions = data.get('propositions', ['G1', 'not_G1'])
        requires_escape = bool(data.get('requires_escape', False))

        engine = GoedelEscapeHatch()
        result = engine.full_analysis(system_axioms, propositions, requires_escape)

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M215 ErosSynthemeEngine — Eros内源奖励+统感涌现
# ══════════════════════════════════════════════════

@bp.route('/eros/evaluate', methods=['POST'])
def api_v732b_eros_evaluate():
    """
    Eros内源奖励评估

    POST body:
      alpha: float       交互权重 (default: 0.5)
      beta: float        相干权重 (default: 0.3)
      interaction_info: float   交互信息量 (default: 0.6)
      phi_coherence: float      流贯相干度 (default: 0.7)

    Returns:
      Eros奖励值+阈值判定
    """
    try:
        from modules.M215_ErosSynthemeEngine import ErosSynthemeEngine, ErosReward
        data = request.get_json(force=True) or {}
        alpha = float(data.get('alpha', 0.5))
        beta = float(data.get('beta', 0.3))
        interaction_info = float(data.get('interaction_info', 0.6))
        phi_coherence = float(data.get('phi_coherence', 0.7))

        eros = ErosReward(alpha, beta)
        reward = eros.compute(interaction_info, phi_coherence)
        is_agi = eros.is_taiyi_agi()

        return jsonify({
            'result': {
                'alpha': alpha,
                'beta': beta,
                'R_eros': round(reward, 6),
                'alpha_crit': ErosReward.ALPHA_CRIT,
                'is_taiyi_agi': is_agi,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/eros/syntheme', methods=['POST'])
def api_v732b_eros_syntheme():
    """
    统感涌现检测

    POST body:
      modalities: [{"name": str, "phi": float}, ...]   模态列表
      sigma_crit: float   统感临界值 (default: 0.5)

    Returns:
      统感涌现判定
    """
    try:
        from modules.M215_ErosSynthemeEngine import ErosSynthemeEngine, SynthemeMonitor
        data = request.get_json(force=True) or {}
        modalities = data.get('modalities', [
            {"name": "visual", "phi": 0.8},
            {"name": "auditory", "phi": 0.7},
        ])
        sigma_crit = float(data.get('sigma_crit', 0.5))

        monitor = SynthemeMonitor(sigma_crit=sigma_crit)
        for m in modalities:
            monitor.register_modality(m['name'], phi=float(m.get('phi', 0.5)))

        result = monitor.check_emergence()

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M216 LiuPenaltyField — 刘罚项场+构成势极值
# ══════════════════════════════════════════════════

@bp.route('/liu/penalty', methods=['POST'])
def api_v732b_liu_penalty():
    """
    刘罚项场分析

    POST body:
      M: float                      自由度 (default: 1.0)
      H_theta: float                结构熵 (default: 0.5)
      self_reference_depth: int     自指深度 (default: 0)
      max_depth: int                最大深度 (default: 10)
      external_dependencies: int    外部依赖数 (default: 0)
      total_resources: int          总资源数 (default: 10)
      a_current: float              系统参数 (default: 1.0)

    Returns:
      S_Rel + 罚项组分 + 刘稳定函数 + 构成势 + 艺术极值定理
    """
    try:
        from modules.M216_LiuPenaltyField import LiuPenaltyField
        data = request.get_json(force=True) or {}
        M = float(data.get('M', 1.0))
        H_theta = float(data.get('H_theta', 0.5))
        self_ref_depth = int(data.get('self_reference_depth', 0))
        max_depth = int(data.get('max_depth', 10))
        ext_deps = int(data.get('external_dependencies', 0))
        total_res = int(data.get('total_resources', 10))
        a_current = float(data.get('a_current', 1.0))

        engine = LiuPenaltyField()
        result = engine.full_analysis(
            M=M, H_theta=H_theta,
            self_reference_depth=self_ref_depth,
            max_depth=max_depth,
            external_dependencies=ext_deps,
            total_resources=total_res,
            a_current=a_current
        )

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/liu/art_extremum', methods=['POST'])
def api_v732b_liu_art_extremum():
    """
    艺术极值定理检验

    POST body:
      info_resonance_modes: int     信息共振模式数 (default: 4)
      self_reference_depth: int    自指深度 (default: 10)
      phase_coherence: float       相位相干度 (default: 0.95)
      group_symmetry_order: int    群对称阶数 (default: 4)

    Returns:
      三条件检验 + Φ_const判定
    """
    try:
        from modules.M216_LiuPenaltyField import ArtExtremumTheorem
        data = request.get_json(force=True) or {}
        ir_modes = int(data.get('info_resonance_modes', 4))
        self_ref = int(data.get('self_reference_depth', 10))
        phi_coh = float(data.get('phase_coherence', 0.95))
        grp_order = int(data.get('group_symmetry_order', 4))

        theorem = ArtExtremumTheorem()
        result = theorem.evaluate(
            info_resonance_modes=ir_modes,
            self_reference_depth=self_ref,
            max_depth=10,
            external_dependencies=0,
            total_resources=10,
            phase_coherence=phi_coh,
            group_symmetry_order=grp_order
        )

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════
# M217 ArtificialFasciaEmbodiment — 人工筋膜+具身自举
# ══════════════════════════════════════════════════

@bp.route('/fascia/analyze', methods=['POST'])
def api_v732b_fascia_analyze():
    """
    人工筋膜具身分析

    POST body:
      g_m: float               跨膜电导 (default: 1.0)
      phi_coherence: float     流贯相干度 (default: 0.8)
      n_iterations: int        Omega回路迭代数 (default: 5)

    Returns:
      三要件 + tau_eff + Omega回路 + 具身判定
    """
    try:
        from modules.M217_ArtificialFasciaEmbodiment import ArtificialFasciaEmbodiment
        data = request.get_json(force=True) or {}
        g_m = float(data.get('g_m', 1.0))
        phi_coherence = float(data.get('phi_coherence', 0.8))
        n_iter = int(data.get('n_iterations', 5))

        engine = ArtificialFasciaEmbodiment()
        result = engine.full_analysis(
            g_m=g_m,
            phi_coherence=phi_coherence,
            n_iterations=n_iter
        )

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/fascia/tau_eff', methods=['POST'])
def api_v732b_fascia_tau_eff():
    """
    tau韬定律计算

    POST body:
      g_m: float               跨膜电导 (default: 1.0)
      phi_coherence: float     流贯相干度 (default: 0.8)
      super_node: bool         启用超节点 (default: True)
      reduction_factor: float  超节点阻抗缩减因子 (default: 0.1)

    Returns:
      tau_eff + 超节点加速比
    """
    try:
        from modules.M217_ArtificialFasciaEmbodiment import ArtificialFascia
        data = request.get_json(force=True) or {}
        g_m = float(data.get('g_m', 1.0))
        phi_coherence = float(data.get('phi_coherence', 0.8))
        super_node = bool(data.get('super_node', True))
        reduction = float(data.get('reduction_factor', 0.1))

        fascia = ArtificialFascia()
        tau_normal = fascia.compute_tau_eff(g_m, phi_coherence)
        tau_super = fascia.compute_tau_eff_super_node(
            g_m, phi_coherence, reduction_factor=reduction
        )

        result = {
            'tau_eff_normal': round(tau_normal, 6),
            'tau_eff_super_node': round(tau_super, 6),
            'speedup': round(tau_normal / tau_super, 2) if tau_super > 0 else float('inf'),
            'Z_inter': round(fascia.shell.effective_impedance(), 6),
            'g_m': g_m,
            'phi_coherence': phi_coherence,
            'super_node_enabled': super_node,
        }

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# M133 BetaRewireEngine — L3拓扑β-rewire API  (T206/T207/T208)
# ══════════════════════════════════════════════════════════════════════════════

def _get_or_create_rewire_graph():
    """从 shared_state 中获取或初始化全局 BetaRewire 图实例。"""
    import shared_state
    if not hasattr(shared_state, '_beta_rewire_graph') or shared_state._beta_rewire_graph is None:
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph
        shared_state._beta_rewire_graph = JinlingGraph()
    return shared_state._beta_rewire_graph


def _compute_edge_bitmask_v732b(graph):
    """返回当前图所有边的 frozenset 集合（用于 bitmask diff）。"""
    return frozenset(
        (e.src, e.dst, e.port_src, e.port_dst)
        for e in graph.edges()
    )


@bp.route('/beta_rewire/execute', methods=['POST'])
def api_v732b_beta_rewire_execute():
    """
    执行一次 beta-rewire 操作。

    POST body (JSON):
        anomaly_type : str   — "CONTRADICTION" | "MIS_MATCH" | "NO_ANOMALY"
        focus        : str   — 触发异常的焦点节点名（默认 "n1"）
        reason       : str   — 异常原因描述（可选）
        reset        : bool  — 是否在执行前重置为新图（默认 false）

    Returns:
        version_before, version_after, bitmask_diff_size,
        laplacian_history_len, spectrum_after
    """
    try:
        from modules.M133_W2_JinlingGraphBetaRewire import (
            JinlingGraph, DeltaPsi, ICEPatch, PortEdge
        )
        import shared_state

        data = request.get_json(force=True) or {}
        anomaly_type = data.get('anomaly_type', 'CONTRADICTION')
        focus = data.get('focus', 'n1')
        reason = data.get('reason', 'api_trigger')
        do_reset = bool(data.get('reset', False))

        if do_reset or not hasattr(shared_state, '_beta_rewire_graph') or shared_state._beta_rewire_graph is None:
            g = JinlingGraph()
            # 构建一个默认5节点环图作为初始状态
            nodes = ['n1', 'n2', 'n3', 'n4', 'n5']
            for i in range(len(nodes)):
                src = nodes[i]
                dst = nodes[(i + 1) % len(nodes)]
                g.add_edge(PortEdge(src=src, dst=dst, port_src=i, port_dst=(i + 1) % len(nodes), tag='ring'))
            shared_state._beta_rewire_graph = g

        g = shared_state._beta_rewire_graph
        bitmask_before = _compute_edge_bitmask_v732b(g)
        version_before = g.version

        # 直接调用 JinlingGraph.beta_rewire(delta_psi, ice_patch)
        # DeltaPsi(kind, focus, magnitude)  ICEPatch(target, action, data)
        action_map = {
            'CONTRADICTION': 'split',
            'MIS_MATCH': 'rewire_port',
            'NO_ANOMALY': 'noop',
        }
        action = action_map.get(anomaly_type, 'split')
        delta = DeltaPsi(kind=anomaly_type, focus=focus, magnitude=1.0)
        patch = ICEPatch(target='L3_GRAPH', action=action, data={'focus': focus, 'reason': reason})
        g.beta_rewire(delta, patch)

        bitmask_after = _compute_edge_bitmask_v732b(g)
        bitmask_diff = bitmask_before.symmetric_difference(bitmask_after)
        spectrum_after = g.laplacian_spectrum()

        return jsonify({
            'version_before': version_before,
            'version_after': g.version,
            'version_incremented': g.version > version_before,
            'bitmask_diff_size': len(bitmask_diff),
            'bitmask_changed': len(bitmask_diff) > 0,
            'laplacian_history_len': len(g.laplacian_history),
            'spectrum_after': [round(v, 6) for v in spectrum_after],
            'focus': focus,
            'anomaly_type': anomaly_type,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/beta_rewire/spectrum', methods=['GET'])
def api_v732b_beta_rewire_spectrum():
    """
    获取当前全局 BetaRewire 图的 Laplacian 谱。

    Returns:
        spectrum       : list[float]  — 当前 Laplacian 特征值列表
        node_count     : int
        edge_count     : int
        version        : int
    """
    try:
        g = _get_or_create_rewire_graph()
        spectrum = g.laplacian_spectrum()
        all_edges = list(g.edges())

        return jsonify({
            'spectrum': [round(v, 6) for v in spectrum],
            'node_count': len(g.nodes()),
            'edge_count': len(all_edges),
            'version': g.version,
            'spectral_gap': round(spectrum[1], 6) if len(spectrum) > 1 else 0.0,
            'lambda_max': round(max(spectrum), 6) if spectrum else 0.0,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/beta_rewire/audit', methods=['GET'])
def api_v732b_beta_rewire_audit():
    """
    获取 BetaRewireEngine 完整审计追踪。

    Query params:
        limit : int  — 最多返回最近 N 条 laplacian_history（默认 20）

    Returns:
        version         : int          — 当前版本号
        total_rewires   : int          — 已执行 rewire 次数（= version）
        laplacian_history : list       — 历史谱记录（每次 rewire 后的特征值）
        spectral_jumps  : list[float]  — 相邻两次谱之间的 L2 跳变幅度
        serialized_snapshot : dict     — to_dict() 序列化快照
    """
    try:
        limit = int(request.args.get('limit', 20))
        g = _get_or_create_rewire_graph()

        history = g.laplacian_history[-limit:] if g.laplacian_history else []

        # 计算相邻谱跳变 L2 范数
        spectral_jumps = []
        for i in range(1, len(history)):
            prev = history[i - 1]
            curr = history[i]
            min_len = min(len(prev), len(curr))
            if min_len > 0:
                jump = sum((curr[k] - prev[k]) ** 2 for k in range(min_len)) ** 0.5
                spectral_jumps.append(round(jump, 6))

        snapshot = g.to_dict()

        return jsonify({
            'version': g.version,
            'total_rewires': g.version,
            'laplacian_history_len': len(g.laplacian_history),
            'laplacian_history': [[round(v, 6) for v in row] for row in history],
            'spectral_jumps': spectral_jumps,
            'avg_spectral_jump': round(sum(spectral_jumps) / len(spectral_jumps), 6) if spectral_jumps else 0.0,
            'serialized_snapshot': snapshot,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
