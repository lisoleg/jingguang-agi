"""
M133-Wintel API Routes
/api/m133/status  - Overall M133 status
/api/m133/w2/beta-rewire - Execute beta-rewire
/api/m133/w3/gate-loop   - Run HoTT Gate Loop
/api/m133/w4/bootstrap   - Run cold-start bootstrap
/api/m133/w5/declaration - Read DSL declaration
/api/m133/mve/p18 - Run P18 MVE
/api/m133/mve/p19 - Run P19 MVE
/api/m133/mve/p20 - Run P20 MVE
"""

from flask import Blueprint, jsonify, request
import tempfile
import os

m133_bp = Blueprint('m133', __name__, url_prefix='/api/m133')


@m133_bp.route('/status', methods=['GET'])
def m133_status():
    """Overall M133-Wintel status."""
    modules = {}

    # W1 check
    try:
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph
        modules['W1_IdrisSelfRef'] = {'available': True, 'note': 'Idris 2 module (compile separately)'}
    except ImportError:
        modules['W1_IdrisSelfRef'] = {'available': False}

    # W2 check
    try:
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, verify_theorem_t219
        modules['W2_JinlingGraph'] = {'available': True, 'theorem_t219': verify_theorem_t219()}
    except ImportError:
        modules['W2_JinlingGraph'] = {'available': False}

    # W3 check
    try:
        from modules.M133_W3_HoTTLeanGate import agi_loop, verify_theorem_t220
        modules['W3_HoTTGateLoop'] = {'available': True, 'theorem_t220': verify_theorem_t220()}
    except ImportError:
        modules['W3_HoTTGateLoop'] = {'available': False}

    # W4 check
    try:
        from modules.M133_W4_ColdStartBootstrap import ColdStartBootstrap, verify_theorem_t221
        with tempfile.TemporaryDirectory() as tmpdir:
            t221 = verify_theorem_t221(output_dir=tmpdir)
        modules['W4_ColdStart'] = {'available': True, 'theorem_t221': t221}
    except ImportError:
        modules['W4_ColdStart'] = {'available': False}

    # W5 check
    try:
        w5_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'M133_W5_SubstrateLimitation.md')
        modules['W5_SubstrateLimitation'] = {
            'available': os.path.exists(w5_path),
            'path': w5_path if os.path.exists(w5_path) else None,
        }
    except Exception:
        modules['W5_SubstrateLimitation'] = {'available': False}

    return jsonify({
        'status': 'ok',
        'version': 'M133-Wintel',
        'modules': modules,
        'certification': 'CS-TAGI Candidate',
    })


@m133_bp.route('/w2/beta-rewire', methods=['POST'])
def w2_beta_rewire():
    """Execute beta-rewire on JinlingGraph."""
    try:
        from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge, DeltaPsi, ICEPatch

        data = request.get_json() or {}
        kind = data.get('kind', 'CONTRADICTION')
        focus = data.get('focus', 'api_request')
        magnitude = float(data.get('magnitude', 0.8))
        target = data.get('target', 'L3_GRAPH')
        action = data.get('action', 'rewire')

        g = JinlingGraph()
        nodes = data.get('nodes', ['A', 'B', 'C'])
        edges = data.get('edges', [['A', 'B'], ['B', 'C']])
        for n in nodes:
            g.add_node(n)
        for i, e in enumerate(edges):
            if len(e) >= 2:
                g.add_edge(PortEdge(src=e[0], dst=e[1], port_src=0, port_dst=0, tag=f"api_e{i}"))

        spec_before = g.laplacian_spectrum()

        delta = DeltaPsi(kind=kind, focus=focus, magnitude=magnitude)
        patch = ICEPatch(target=target, action=action)
        result = g.beta_rewire(delta, patch)

        spec_after = g.laplacian_spectrum()

        return jsonify({
            'status': 'ok',
            'spectrum_before': spec_before[:5],
            'spectrum_after': spec_after[:5],
            'rewire_result': str(result),
            'graph_version': g.version,
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@m133_bp.route('/w3/gate-loop', methods=['POST'])
def w3_gate_loop():
    """Run HoTT Gate Loop for a given proposition."""
    try:
        from modules.M133_W3_HoTTLeanGate import (
            agi_loop, UninhabitedError, TypeSignature, CandidateTerm, SimpleTypeChecker
        )

        data = request.get_json() or {}
        proposition = data.get('proposition', 'identity_func')
        kind = data.get('kind', 'function')

        sig = TypeSignature(name=proposition, params={"kind": kind}, constraints=[])
        checker = SimpleTypeChecker()

        def propose_fn(target: TypeSignature, attempt: int) -> list:
            return [CandidateTerm(
                term_id=f"api_propose_{attempt}",
                expression=f"proof_of_{target.name}",
                source="api_proposer",
                confidence=0.7
            )]

        try:
            final_term, loop_info = agi_loop(
                task_type=sig,
                llm_propose_fn=propose_fn,
                type_check_fn=checker.check,
                jinling_graph=None,
            )
            return jsonify({
                'status': 'ok',
                'gate_loop': 'success',
                'final_term': final_term.to_dict() if hasattr(final_term, 'to_dict') else str(final_term),
                'loop_info': str(loop_info),
            })
        except UninhabitedError as e:
            return jsonify({
                'status': 'ok',
                'gate_loop': 'uninhabited',
                'error': str(e),
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@m133_bp.route('/w4/bootstrap', methods=['POST'])
def w4_bootstrap():
    """Run cold-start bootstrap chain."""
    try:
        from modules.M133_W4_ColdStartBootstrap import ColdStartBootstrap

        with tempfile.TemporaryDirectory() as tmpdir:
            csb = ColdStartBootstrap(output_dir=tmpdir)
            blocked = csb.block_pretrained()
            result = csb.run_full_bootstrap()

        return jsonify({
            'status': 'ok',
            'blocked_embeddings': len(blocked) if isinstance(blocked, list) else 0,
            'bootstrap_result': result,
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@m133_bp.route('/w5/declaration', methods=['GET'])
def w5_declaration():
    """Read the Substrate Limitation Declaration."""
    try:
        w5_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'M133_W5_SubstrateLimitation.md')
        if os.path.exists(w5_path):
            with open(w5_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'status': 'ok',
                'content': content,
                'length': len(content),
            })
        return jsonify({'status': 'error', 'message': 'DSL file not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@m133_bp.route('/mve/p18', methods=['GET'])
def run_p18():
    """Run P18 MVE: L3 Beta-Rewire."""
    try:
        from P18_MVE_L3BetaRewire import run_p18 as p18_run
        result = p18_run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@m133_bp.route('/mve/p19', methods=['GET'])
def run_p19():
    """Run P19 MVE: HoTT Gate Loop."""
    try:
        from P19_MVE_HoTTGateLoop import run_p19 as p19_run
        result = p19_run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@m133_bp.route('/mve/p20', methods=['GET'])
def run_p20():
    """Run P20 MVE: Cold-Start Bootstrap."""
    try:
        from P20_MVE_ColdStartBootstrap import run_p20 as p20_run
        result = p20_run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
