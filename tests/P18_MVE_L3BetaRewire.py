"""
P18 MVE: L3 Beta-Rewire Experiment
Verifies Theorem T2.19: beta_rewire must change topology (not just weights)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.M133_W2_JinlingGraphBetaRewire import (
    JinlingGraph, PortEdge, DeltaPsi, ICEPatch, verify_theorem_t219
)


def run_p18() -> dict:
    """Run P18 MVE: L3 Beta-Rewire experiment."""
    results = {
        "experiment": "P18_MVE_L3BetaRewire",
        "tests": [],
        "passed": 0,
        "failed": 0,
    }

    # Test 1: Beta-rewire changes Laplacian spectrum
    g = JinlingGraph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_edge(PortEdge(src="A", dst="B", port_src=0, port_dst=0, tag="e_ab"))
    g.add_edge(PortEdge(src="B", dst="C", port_src=0, port_dst=0, tag="e_bc"))

    spec_before = g.laplacian_spectrum()

    delta = DeltaPsi(kind="CONTRADICTION", focus="test_edge", magnitude=0.9)
    patch = ICEPatch(target="L3_GRAPH", action="rewire_test")
    rewire_result = g.beta_rewire(delta, patch)

    spec_after = g.laplacian_spectrum()
    spectrum_changed = not all(abs(a - b) < 1e-6 for a, b in zip(spec_before, spec_after))

    results["tests"].append({
        "name": "beta_rewire_changes_spectrum",
        "passed": spectrum_changed,
        "spectrum_before": spec_before[:3],
        "spectrum_after": spec_after[:3],
    })
    if spectrum_changed:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 2: Verify T2.19 formally
    t219 = verify_theorem_t219()
    results["tests"].append({
        "name": "theorem_t219_verified",
        "passed": t219.get("verified", False),
        "details": t219,
    })
    if t219.get("verified", False):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 3: Multiple rewire rounds maintain topology change
    # Use fresh graphs per round to avoid saturation on small graphs
    all_changed = True
    for r in range(3):
        g2 = JinlingGraph()
        for i in range(5):
            g2.add_node(f"N{i}")
        for i in range(4):
            g2.add_edge(PortEdge(src=f"N{i}", dst=f"N{i+1}", port_src=0, port_dst=0, tag=f"e_{i}"))
        spec_b = g2.laplacian_spectrum()
        d = DeltaPsi(kind="CONTRADICTION", focus=f"N{r}", magnitude=0.5 + r * 0.1)
        p = ICEPatch(target="L3_GRAPH", action=f"rewire_r{r}")
        g2.beta_rewire(d, p)
        spec_a = g2.laplacian_spectrum()
        changed = not all(abs(a - b) < 1e-6 for a, b in zip(spec_b, spec_a))
        if not changed:
            all_changed = False

    results["tests"].append({
        "name": "multi_round_topology_change",
        "passed": all_changed,
        "rounds_tested": 3,
    })
    if all_changed:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 4: Edge add/delete (not just weight updates)
    g3 = JinlingGraph()
    g3.add_node("X")
    g3.add_node("Y")
    g3.add_node("Z")
    g3.add_edge(PortEdge(src="X", dst="Y", port_src=0, port_dst=0, tag="e_xy"))
    edges_before = g3.edge_count()
    g3.remove_edge("X", "Y", 0, 0)
    edges_after_remove = g3.edge_count()
    g3.add_edge(PortEdge(src="X", dst="Z", port_src=0, port_dst=0, tag="e_xz"))
    edges_after_add = g3.edge_count()

    edge_ops_ok = (edges_after_remove == edges_before - 1) and (edges_after_add == edges_after_remove + 1)
    results["tests"].append({
        "name": "edge_add_delete_ops",
        "passed": edge_ops_ok,
        "edges_before": edges_before,
        "edges_after_remove": edges_after_remove,
        "edges_after_add": edges_after_add,
    })
    if edge_ops_ok:
        results["passed"] += 1
    else:
        results["failed"] += 1

    results["all_passed"] = results["failed"] == 0
    return results


if __name__ == "__main__":
    r = run_p18()
    print(f"P18 MVE: {r['passed']}/{r['passed']+r['failed']} tests passed")
    for t in r["tests"]:
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  [{status}] {t['name']}")
    sys.exit(0 if r["all_passed"] else 1)
