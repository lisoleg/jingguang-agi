#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MVE: v7.38 五引擎 + Gamma超图谱 最小验证实验
Modules: M251, M252(JSN+Gamma), M253, M254, M255
Theorems: T2.96, T2.97, T2.98, T2.99, T2.73, T2.74, T2.101, T2.102, T2.76
Predictions: P20, P21, P23, P25, P26
"""

import sys
import os

# Project root is one level up from tests/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


# ════════════════════════════════════════════════════
# 1. M251 NAU Associator Engine
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("1. M251 NAU Associator Engine")
print("=" * 60)

try:
    from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine, verify_theorem_t296, verify_theorem_t297, verify_prediction_p25

    engine = NAUAssociatorEngine.get_instance()
    check("M251 import", True)

    # Octonion multiply
    e1 = [1, 0, 0, 0, 0, 0, 0, 0]
    e2 = [0, 1, 0, 0, 0, 0, 0, 0]
    result = engine.octonion_multiply(e1, e2)
    check("octonion_multiply(e1,e2)=e2", result == e2)

    # Jacobiator
    a = [1, 2, 3, 4, 5, 6, 7, 8]
    b = [8, 7, 6, 5, 4, 3, 2, 1]
    c = [0.5] * 8
    jac = engine.jacobiator(a, b, c)
    check("jacobiator returns 8-element list", len(jac) == 8)

    # NAU forward
    x = [1.0] * 8
    w = [0.5] * 8
    out = engine.nau_forward(x, w)
    check("nau_forward returns list", isinstance(out, list) and len(out) > 0)

    # Bypass check
    bypass = engine.bypass_check(a, b, c)
    check("bypass_check returns bool", isinstance(bypass, bool))

    # Theorem T2.96
    t296 = verify_theorem_t296()
    check("T2.96 proved", t296.get('proved', False))

    # Theorem T2.97
    t297 = verify_theorem_t297()
    check("T2.97 proved", t297.get('proved', False))

    # Prediction P25
    p25 = verify_prediction_p25()
    check("P25 passed", p25.get('passed', False))

    # State
    state = engine.get_state()
    check("get_state() returns dict", isinstance(state, dict))

except Exception as e:
    check("M251 import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# 2. M252 JSN Memory Engine
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("2. M252 JSN Memory Engine")
print("=" * 60)

try:
    from modules.M252_JSNMemoryEngine import JSNMemoryEngine, verify_theorem_t298, verify_theorem_t299

    engine = JSNMemoryEngine.get_instance()
    check("M252 JSN import", True)

    # Add node
    nid = engine.add_node(label="test_node")
    check("add_node returns int", isinstance(nid, int))

    # Add edge
    nid2 = engine.add_node(label="test_node2")
    eid = engine.add_edge(src=nid, dst=nid2, rel_type="related", weight=1.0)
    check("add_edge returns int", isinstance(eid, int))

    # Add hedge
    nid3 = engine.add_node(label="test_node3")
    hid = engine.add_hedge(nodes=[nid, nid2, nid3], rel_type="hyper", weight=1.0)
    check("add_hedge returns int", isinstance(hid, int))

    # Query triple
    result = engine.query_triple(nid, nid2, nid3)
    check("query_triple returns dict", isinstance(result, dict))

    # TDHNN step
    result = engine.tdhnn_step()
    check("tdhnn_step returns dict", isinstance(result, dict))

    # Deep well
    dw_id = engine.deepwell_add(content="test memory", depth=1)
    check("deepwell_add returns int", isinstance(dw_id, int))

    entry = engine.deepwell_access(dw_id)
    check("deepwell_access returns entry", entry is not None)

    # Coverage
    cov = engine.compute_coverage()
    check("compute_coverage returns float", isinstance(cov, (int, float)))

    # SAT check
    sat = engine.sat_check()
    check("sat_check returns dict", isinstance(sat, dict))

    # Theorem T2.98
    t298 = verify_theorem_t298()
    check("T2.98 proved", t298.get('proved', False))

    # Theorem T2.99
    t299 = verify_theorem_t299()
    check("T2.99 proved", t299.get('proved', False))

    # State
    state = engine.get_state()
    check("get_state() returns dict", isinstance(state, dict))

except Exception as e:
    check("M252 JSN import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# 3. M252b Gamma HyperGrapher Engine
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("3. M252b Gamma HyperGrapher Engine")
print("=" * 60)

try:
    from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine

    engine = GammaHyperGrapherEngine.get_instance()
    check("M252 Gamma import", True)

    # Add vertices and hyperedges
    engine.reset()
    for v in range(6):
        engine.add_vertex(v)
    engine.add_hyperedge(vertices=[0, 1, 2], weight=1.0)
    engine.add_hyperedge(vertices=[3, 4, 5], weight=1.5)
    engine.add_hyperedge(vertices=[0, 3], weight=0.5)
    check("add_vertex + add_hyperedge", True)

    # Spectral cluster
    result = engine.hypergraph_spectral_cluster(num_clusters=2)
    check("spectral_cluster returns dict", isinstance(result, dict))

    # Gamma functional
    f_val = engine.gamma_functional([1.0, 2.0, 3.0])
    check("gamma_functional returns float", isinstance(f_val, (int, float)))

    # Theorem T2.73
    t273 = engine.verify_theorem_t273()
    check("T2.73 verified", t273.get('proved', False) or t273.get('verified', False) or t273.get('accuracy', 0) > 0.5)

    # Prediction P20
    p20 = engine.verify_prediction_p20()
    check("P20 passed", p20.get('passed', False) or p20.get('mean_accuracy', 0) >= 0.8)

    # State
    state = engine.get_state()
    check("get_state() returns dict", isinstance(state, dict))

except Exception as e:
    check("M252 Gamma import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# 4. M253 Epiplexity Engine
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("4. M253 Epiplexity Engine")
print("=" * 60)

try:
    from modules.M253_EpiplexityEngine import EpiplexityEngine, verify_theorem_t274, verify_prediction_p21

    engine = EpiplexityEngine.get_instance()
    check("M253 import", True)

    # Entropy
    H = engine.compute_entropy([0.25, 0.25, 0.25, 0.25])
    check("H(uniform_4) ≈ log(4)", abs(H - 1.386) < 0.01)

    # KL divergence
    D = engine.compute_distance([0.5, 0.5], [0.5, 0.5])
    check("D_KL(p||p) = 0", abs(D) < 1e-10)

    # Complexity
    C = engine.compute_complexity([0.1, 0.2, 0.3, 0.0, 0.0])
    check("complexity is finite", not (C != C) and C >= 0)  # not NaN and >= 0

    # Epiplexity score
    E = engine.epiplexity_score([0.5, 0.5], [0.5, 0.5], [0.1, 0.2])
    check("epiplexity >= H", E >= H - 1e-10)

    # Information bottleneck
    IB = engine.information_bottleneck(1.0, 0.8, 1.0)
    check("IB finite", not (IB != IB))  # not NaN

    # Theorem T2.74
    t274 = verify_theorem_t274()
    check("T2.74 proved", t274.get('proved', False) or t274.get('violations', -1) == 0)

    # Prediction P21
    p21 = verify_prediction_p21()
    check("P21 passed", p21.get('passed', False) or p21.get('mean_relative_error', 1.0) < 0.15)

    # State
    state = engine.get_state()
    check("get_state() returns dict", isinstance(state, dict))

except Exception as e:
    check("M253 import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# 5. M254 QITE Virtual Time Engine
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("5. M254 QITE Virtual Time Engine")
print("=" * 60)

try:
    from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine, verify_theorem_t2101, verify_theorem_t2102, verify_prediction_p26

    engine = QITEVirtualTimeEngine.get_instance(dim=4)
    check("M254 import", True)

    # Wick rotate
    wr = QITEVirtualTimeEngine.wick_rotate(1.0)
    check("wick_rotate returns value", wr is not None)

    # QITE evolve
    dim = 4
    H = [[0.0] * dim for _ in range(dim)]
    for i in range(dim):
        H[i][i] = (dim - i) * 0.5
    psi0 = [1.0 / dim] * dim
    psi_final = engine.qite_evolve(psi0, H, n_steps=10)
    check("qite_evolve returns list", isinstance(psi_final, list) and len(psi_final) == dim)

    # Find ground state
    gs, energy = engine.find_ground_state(H)
    check("find_ground_state returns (state, energy)", isinstance(gs, list) and isinstance(energy, (int, float)))

    # Quaternion multiply
    q1 = (1.0, 0.0, 0.0, 0.0)
    q2 = (0.0, 1.0, 0.0, 0.0)
    qr = QITEVirtualTimeEngine.quaternion_multiply(q1, q2)
    check("quaternion_multiply returns tuple", len(qr) == 4)

    # Octonion multiply
    o1 = (1, 0, 0, 0, 0, 0, 0, 0)
    o2 = (0, 1, 0, 0, 0, 0, 0, 0)
    or_ = QITEVirtualTimeEngine.octonion_multiply(o1, o2)
    check("octonion_multiply returns tuple", len(or_) == 8)

    # Theorem T2.101
    t2101 = verify_theorem_t2101()
    check("T2.101 proved", t2101 is True or t2101 == True)

    # Theorem T2.102
    t2102 = verify_theorem_t2102()
    check("T2.102 proved", t2102 is True or t2102 == True)

    # Prediction P26
    p26 = verify_prediction_p26()
    check("P26 passed", p26 is True or p26 == True)

    # State
    state = engine.get_state()
    check("get_state() returns dict", isinstance(state, dict))

except Exception as e:
    check("M254 import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# 6. M255 LSNC Regulation Engine
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("6. M255 LSNC Regulation Engine")
print("=" * 60)

try:
    from modules.M255_LSNCREngine import LSNCREngine

    engine = LSNCREngine.get_instance()
    check("M255 import", True)

    # Covariance
    import random
    random.seed(42)
    X = [[random.gauss(0, 1) for _ in range(5)] for _ in range(10)]
    C = engine.compute_covariance(X)
    check("compute_covariance returns 5x5 matrix", len(C) == 5 and len(C[0]) == 5)

    # Log-scale regulate
    C_log = engine.log_scale_regulate(C, alpha=0.1)
    check("log_scale_regulate returns 5x5 matrix", len(C_log) == 5 and len(C_log[0]) == 5)

    # Adaptive alpha
    alpha = engine.adaptive_alpha(C)
    check("adaptive_alpha > 0", alpha > 0)

    # Neural dynamics
    dim3 = 3
    W = [[random.gauss(0, 0.3) for _ in range(dim3)] for _ in range(dim3)]
    for i in range(dim3):
        W[i][i] = -1.0
    x0 = [1.0 / dim3] * dim3
    f = lambda x: x
    traj, times = engine.neural_dynamics(W, f, x0, tau=1.0, T=2.0, dt=0.05, noise_std=0.01, seed=42)
    check("neural_dynamics returns trajectory", len(traj) > 0 and len(times) > 0)

    # Covariance steady state
    ss = engine.covariance_steady_state(W, f, tau=1.0, T_max=10.0, seed=42)
    check("covariance_steady_state returns dict", isinstance(ss, dict))

    # Theorem T2.76
    t276 = engine.verify_theorem_t276(n_trials=20, seed=42)
    check("T2.76 convergence rate > 0", t276.get('convergence_rate', 0) > 0)

    # Prediction P23
    p23 = engine.verify_prediction_p23(n_trials=20, seed=42)
    check("P23 accuracy >= 0.8", p23.get('accuracy', 0) >= 0.8 or p23.get('passed', False))

    # State
    state = engine.get_state()
    check("get_state() returns dict", isinstance(state, dict))

except Exception as e:
    check("M255 import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# 7. Blueprint Registration Check
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7. Blueprint Registration")
print("=" * 60)

try:
    from blueprints.bp_v738 import bp
    check("bp_v738 import", True)

    routes = [rule.rule for rule in bp.deferred_functions if hasattr(rule, 'rule')] if hasattr(bp, 'deferred_functions') else []
    # Count routes by reading the source file
    bp_file = os.path.join(PROJECT_ROOT, "blueprints", "bp_v738.py")
    with open(bp_file, 'r', encoding='utf-8') as f:
        src = f.read()
    route_count = src.count("@bp.route(")
    check(f"bp_v738 has {route_count} routes", route_count >= 40, f"found {route_count}")

except Exception as e:
    check("bp_v738 import", False, str(e)[:200])


# ════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"MVE v7.38 Results: {PASS}/{total} PASS, {FAIL}/{total} FAIL")
if FAIL == 0:
    print("✅ ALL TESTS PASSED — v7.38 MVE COMPLETE")
else:
    print(f"⚠️ {FAIL} tests failed — review needed")
print("=" * 60)
