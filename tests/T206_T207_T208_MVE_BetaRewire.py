# -*- coding: utf-8 -*-
"""
T206-T208 MVE: BetaRewireEngine Auditability, Spectrum Jump, and Edge Bitmask Verification

T206: Beta-rewire auditability — version tracking, laplacian_history, serialization round-trip
T207: Laplacian spectrum jump — fine-grained verification for CONTRADICTION and MIS_MATCH
T208: edge_bitmask_diff ≠ 0 — topology change verified via edge set comparison

Part of M133 W2: L3 Beta-Rewire API for JinlingGraph topology
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.M133_W2_JinlingGraphBetaRewire import (
    JinlingGraph, PortEdge, DeltaPsi, ICEPatch
)


# ════════════════════════════════════════════════════════════════
# Helper: Edge Bitmask Computation
# ════════════════════════════════════════════════════════════════

def compute_edge_bitmask(graph: JinlingGraph) -> frozenset:
    """Compute a frozenset representation of the graph's edge topology.

    Each edge is represented as a tuple (src, dst, port_src, port_dst)
    which uniquely identifies the directed port-labeled connection.
    Two graphs with different edge_bitmask values have different topologies.
    """
    return frozenset(
        (e.src, e.dst, e.port_src, e.port_dst)
        for e in graph.edges()
    )


def build_ring_graph(n: int = 5, prefix: str = "n") -> JinlingGraph:
    """Build an n-node ring graph with directed edges."""
    g = JinlingGraph()
    for i in range(n):
        src = f"{prefix}{i+1}"
        dst = f"{prefix}{(i+1) % n + 1}"
        g.add_edge(PortEdge(src=src, dst=dst, port_src=i, port_dst=(i+1) % n, tag="ring"))
    return g


# ════════════════════════════════════════════════════════════════
# T206: β-rewire 可审计性验证
# ════════════════════════════════════════════════════════════════

def test_t206_auditability() -> dict:
    """T206: Verify beta-rewire produces complete audit trail.

    Checks:
    1. version increments monotonically after each rewire
    2. laplacian_history records each spectrum change
    3. to_dict/from_dict serialization round-trip preserves all state
    """
    result = {"theorem": "T206", "name": "beta_rewire_auditability", "tests": []}

    # Sub-test 1: Version tracking
    g = build_ring_graph(5)
    assert g.version == 0, f"Initial version should be 0, got {g.version}"

    versions = [g.version]
    for step in range(3):
        focus = f"n{min(step + 1, g.node_count())}"
        if focus not in g.adj and g.adj:
            focus = g.nodes()[0]
        delta = DeltaPsi(
            kind="CONTRADICTION" if step % 2 == 0 else "MIS_MATCH",
            focus=focus,
            magnitude=0.5 + step * 0.2
        )
        patch = ICEPatch(target="L3_GRAPH", action=f"rewire_step_{step}")
        g.beta_rewire(delta, patch)
        versions.append(g.version)

    # Version should be monotonically increasing
    version_monotonic = all(versions[i] < versions[i+1] for i in range(len(versions)-1))
    result["tests"].append({
        "name": "version_monotonic_increment",
        "passed": version_monotonic,
        "versions": versions,
        "expected": list(range(len(versions))),
    })

    # Sub-test 2: Laplacian history tracking
    # laplacian_history should have one entry per rewire (3 rewires = 3 entries)
    history_count = len(g.laplacian_history)
    history_ok = history_count == 3
    # Each entry should be a non-empty list of floats
    history_valid = all(
        isinstance(h, list) and len(h) > 0 and all(isinstance(v, float) for v in h)
        for h in g.laplacian_history
    )
    result["tests"].append({
        "name": "laplacian_history_tracking",
        "passed": history_ok and history_valid,
        "history_count": history_count,
        "expected_count": 3,
        "entries_valid": history_valid,
    })

    # Sub-test 3: Serialization round-trip
    data = g.to_dict()
    g2 = JinlingGraph.from_dict(data)

    # Verify nodes
    nodes_match = set(g.nodes()) == set(g2.nodes())
    # Verify edges
    edges_match = set(
        (e.src, e.dst, e.port_src, e.port_dst) for e in g.edges()
    ) == set(
        (e.src, e.dst, e.port_src, e.port_dst) for e in g2.edges()
    )
    # Verify version
    version_match = g.version == g2.version
    # Verify spectrum (recomputed on g2 should match g's current spectrum)
    spec_g = g.laplacian_spectrum()
    spec_g2 = g2.laplacian_spectrum()
    spectrum_match = all(abs(a - b) < 1e-3 for a, b in zip(spec_g, spec_g2))

    roundtrip_ok = nodes_match and edges_match and version_match and spectrum_match
    result["tests"].append({
        "name": "serialization_roundtrip",
        "passed": roundtrip_ok,
        "nodes_match": nodes_match,
        "edges_match": edges_match,
        "version_match": version_match,
        "spectrum_match": spectrum_match,
    })

    # Overall T206 result
    all_passed = all(t["passed"] for t in result["tests"])
    result["passed"] = all_passed
    result["pass_count"] = sum(1 for t in result["tests"] if t["passed"])
    result["total"] = len(result["tests"])
    return result


# ════════════════════════════════════════════════════════════════
# T207: Laplacian 谱跳变验证
# ════════════════════════════════════════════════════════════════

def test_t207_spectrum_jump() -> dict:
    """T207: Verify Laplacian spectrum jump for both CONTRADICTION and MIS_MATCH.

    Checks:
    1. CONTRADICTION rewire produces measurable spectrum change (Δ > ε)
    2. MIS_MATCH rewire produces measurable spectrum change (Δ > ε)
    3. Spectrum changes are not just floating-point noise (minimum Δ > 0.01)
    """
    result = {"theorem": "T207", "name": "laplacian_spectrum_jump", "tests": []}

    SPECTRUM_EPSILON = 0.01  # Minimum meaningful spectrum change

    # Sub-test 1: CONTRADICTION spectrum jump
    g1 = build_ring_graph(6)
    spec_before = g1.laplacian_spectrum()
    edges_before = g1.edge_count()

    delta1 = DeltaPsi(kind="CONTRADICTION", focus="n3", magnitude=1.0)
    patch1 = ICEPatch(target="L3_GRAPH", action="split")
    g1.beta_rewire(delta1, patch1)

    spec_after = g1.laplacian_spectrum()
    edges_after = g1.edge_count()

    # Compute L2 norm of spectrum change
    max_len = max(len(spec_before), len(spec_after))
    sb = spec_before + [0.0] * (max_len - len(spec_before))
    sa = spec_after + [0.0] * (max_len - len(spec_after))
    spectrum_delta = sum((a - b) ** 2 for a, b in zip(sb, sa)) ** 0.5

    any_change = any(abs(a - b) > 1e-3 for a, b in zip(sb, sa))
    meaningful_change = spectrum_delta > SPECTRUM_EPSILON
    edges_changed = edges_before != edges_after

    contradiction_ok = any_change and meaningful_change and edges_changed
    result["tests"].append({
        "name": "contradiction_spectrum_jump",
        "passed": contradiction_ok,
        "spectrum_before": spec_before[:5],
        "spectrum_after": spec_after[:5],
        "spectrum_delta_L2": round(spectrum_delta, 6),
        "meaningful_change": meaningful_change,
        "edges_before": edges_before,
        "edges_after": edges_after,
        "edges_changed": edges_changed,
    })

    # Sub-test 2: MIS_MATCH spectrum jump
    g2 = build_ring_graph(6, prefix="m")
    spec_before2 = g2.laplacian_spectrum()
    edges_before2 = g2.edge_count()

    delta2 = DeltaPsi(kind="MIS_MATCH", focus="m2", magnitude=0.7)
    patch2 = ICEPatch(target="L3_GRAPH", action="rewire_port")
    g2.beta_rewire(delta2, patch2)

    spec_after2 = g2.laplacian_spectrum()
    edges_after2 = g2.edge_count()

    max_len2 = max(len(spec_before2), len(spec_after2))
    sb2 = spec_before2 + [0.0] * (max_len2 - len(spec_before2))
    sa2 = spec_after2 + [0.0] * (max_len2 - len(spec_after2))
    spectrum_delta2 = sum((a - b) ** 2 for a, b in zip(sb2, sa2)) ** 0.5

    any_change2 = any(abs(a - b) > 1e-3 for a, b in zip(sb2, sa2))
    meaningful_change2 = spectrum_delta2 > SPECTRUM_EPSILON
    edges_changed2 = edges_before2 != edges_after2

    mismatch_ok = any_change2 and meaningful_change2 and edges_changed2
    result["tests"].append({
        "name": "mismatch_spectrum_jump",
        "passed": mismatch_ok,
        "spectrum_before": spec_before2[:5],
        "spectrum_after": spec_after2[:5],
        "spectrum_delta_L2": round(spectrum_delta2, 6),
        "meaningful_change": meaningful_change2,
        "edges_before": edges_before2,
        "edges_after": edges_after2,
        "edges_changed": edges_changed2,
    })

    # Sub-test 3: Spectrum change not just noise (aggregate check)
    # Both rewires should produce changes exceeding noise floor
    both_meaningful = meaningful_change and meaningful_change2
    result["tests"].append({
        "name": "spectrum_change_above_noise",
        "passed": both_meaningful,
        "contradiction_delta": round(spectrum_delta, 6),
        "mismatch_delta": round(spectrum_delta2, 6),
        "noise_floor": SPECTRUM_EPSILON,
    })

    # Overall T207 result
    all_passed = all(t["passed"] for t in result["tests"])
    result["passed"] = all_passed
    result["pass_count"] = sum(1 for t in result["tests"] if t["passed"])
    result["total"] = len(result["tests"])
    return result


# ════════════════════════════════════════════════════════════════
# T208: edge_bitmask_diff ≠ 0 验证
# ════════════════════════════════════════════════════════════════

def test_t208_edge_bitmask_diff() -> dict:
    """T208: Verify topology change via edge bitmask comparison.

    edge_bitmask = frozenset of (src, dst, port_src, port_dst) tuples

    Checks:
    1. CONTRADICTION rewire: bitmask_before ≠ bitmask_after
    2. MIS_MATCH rewire: bitmask_before ≠ bitmask_after
    3. NO_ANOMALY rewire: bitmask unchanged (no rewire should occur)
    4. Symmetric difference is non-empty (actual edge-level change)
    """
    result = {"theorem": "T208", "name": "edge_bitmask_diff", "tests": []}

    # Sub-test 1: CONTRADICTION changes bitmask
    g1 = build_ring_graph(5)
    bitmask_before = compute_edge_bitmask(g1)

    delta1 = DeltaPsi(kind="CONTRADICTION", focus="n2", magnitude=1.0)
    patch1 = ICEPatch(target="L3_GRAPH", action="split")
    g1.beta_rewire(delta1, patch1)

    bitmask_after = compute_edge_bitmask(g1)
    sym_diff = bitmask_before.symmetric_difference(bitmask_after)

    contradiction_ok = bitmask_before != bitmask_after and len(sym_diff) > 0
    result["tests"].append({
        "name": "contradiction_bitmask_change",
        "passed": contradiction_ok,
        "bitmask_size_before": len(bitmask_before),
        "bitmask_size_after": len(bitmask_after),
        "symmetric_diff_count": len(sym_diff),
        "changed": bitmask_before != bitmask_after,
    })

    # Sub-test 2: MIS_MATCH changes bitmask
    g2 = build_ring_graph(5, prefix="x")
    bitmask_before2 = compute_edge_bitmask(g2)

    delta2 = DeltaPsi(kind="MIS_MATCH", focus="x2", magnitude=0.5)
    patch2 = ICEPatch(target="L3_GRAPH", action="rewire_port")
    g2.beta_rewire(delta2, patch2)

    bitmask_after2 = compute_edge_bitmask(g2)
    sym_diff2 = bitmask_before2.symmetric_difference(bitmask_after2)

    mismatch_ok = bitmask_before2 != bitmask_after2 and len(sym_diff2) > 0
    result["tests"].append({
        "name": "mismatch_bitmask_change",
        "passed": mismatch_ok,
        "bitmask_size_before": len(bitmask_before2),
        "bitmask_size_after": len(bitmask_after2),
        "symmetric_diff_count": len(sym_diff2),
        "changed": bitmask_before2 != bitmask_after2,
    })

    # Sub-test 3: NO_ANOMALY does NOT change bitmask
    g3 = build_ring_graph(4, prefix="y")
    bitmask_before3 = compute_edge_bitmask(g3)

    delta3 = DeltaPsi(kind="NO_ANOMALY", focus="y1", magnitude=0.0)
    patch3 = ICEPatch(target="L3_GRAPH", action="noop")
    g3.beta_rewire(delta3, patch3)

    bitmask_after3 = compute_edge_bitmask(g3)

    no_change_ok = bitmask_before3 == bitmask_after3
    result["tests"].append({
        "name": "no_anomaly_bitmask_unchanged",
        "passed": no_change_ok,
        "bitmask_size_before": len(bitmask_before3),
        "bitmask_size_after": len(bitmask_after3),
        "unchanged": bitmask_before3 == bitmask_after3,
    })

    # Sub-test 4: Bitmask diff is non-empty after forced topology change
    # (This tests the forced_topo_change mechanism in beta_rewire)
    g4 = JinlingGraph()
    g4.add_edge(PortEdge(src="P", dst="Q", port_src=0, port_dst=1, tag="only"))
    bitmask_before4 = compute_edge_bitmask(g4)

    delta4 = DeltaPsi(kind="CONTRADICTION", focus="P", magnitude=1.0)
    patch4 = ICEPatch(target="L3_GRAPH", action="split_minimal")
    g4.beta_rewire(delta4, patch4)

    bitmask_after4 = compute_edge_bitmask(g4)
    sym_diff4 = bitmask_before4.symmetric_difference(bitmask_after4)

    # Even on a minimal graph (2 nodes, 1 edge), rewire must change topology
    forced_ok = len(sym_diff4) > 0
    result["tests"].append({
        "name": "minimal_graph_forced_change",
        "passed": forced_ok,
        "symmetric_diff_count": len(sym_diff4),
        "bitmask_before_size": len(bitmask_before4),
        "bitmask_after_size": len(bitmask_after4),
    })

    # Overall T208 result
    all_passed = all(t["passed"] for t in result["tests"])
    result["passed"] = all_passed
    result["pass_count"] = sum(1 for t in result["tests"] if t["passed"])
    result["total"] = len(result["tests"])
    return result


# ════════════════════════════════════════════════════════════════
# Runner
# ════════════════════════════════════════════════════════════════

def run_all_t206_t208() -> dict:
    """Run all T206-T208 MVE tests."""
    overall = {
        "experiment": "T206_T207_T208_MVE_BetaRewire",
        "theorems": [],
        "passed": 0,
        "failed": 0,
        "total_tests": 0,
    }

    for test_fn in [test_t206_auditability, test_t207_spectrum_jump, test_t208_edge_bitmask_diff]:
        r = test_fn()
        overall["theorems"].append(r)
        overall["passed"] += r["pass_count"]
        overall["failed"] += r["total"] - r["pass_count"]
        overall["total_tests"] += r["total"]

    overall["all_passed"] = overall["failed"] == 0
    return overall


if __name__ == "__main__":
    r = run_all_t206_t208()
    print("=" * 60)
    print("T206-T208 MVE: BetaRewire Engine Verification")
    print("=" * 60)

    for thm in r["theorems"]:
        status = "PASS" if thm["passed"] else "FAIL"
        print(f"\n[{status}] {thm['theorem']}: {thm['name']} ({thm['pass_count']}/{thm['total']})")
        for t in thm["tests"]:
            s = "PASS" if t["passed"] else "FAIL"
            print(f"  [{s}] {t['name']}")

    print(f"\n{'=' * 60}")
    print(f"Total: {r['passed']}/{r['total_tests']} tests passed")
    if r["all_passed"]:
        print("ALL T206-T208 MVE TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    sys.exit(0 if r["all_passed"] else 1)
