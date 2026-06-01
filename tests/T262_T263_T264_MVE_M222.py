# -*- coding: utf-8 -*-
"""
T262-T264 MVE v732c -- M222 SerDesOntologyEngine
验证三定理 T4.1 / T4.2 / T4.3

Author: TaiyiAGI Team
"""

import sys
import os

# 双层路径注入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.M222_SerDesOntologyEngine import (
    TYSerializer, TYDeserializer, BiSerDesChecker,
    InformationLossAnalyzer, EMLFiveHardening,
    Frame, FrameSequence, SerializeResult, DeserializeResult, BiSerDesStatus,
    verify_theorem_t41, verify_theorem_t42, verify_theorem_t43,
)


def test_t262_serialize():
    """
    T262 -- T4.1 Taiyi Serialize theorem

    H(sigma) reflects information evolution during serialization.
    Entropy change must be bounded and quantifiable.
    """
    print("\n--- T262 T4.1 Serialize Theorem (M222) ---")

    # Test 1: verify_theorem_t41
    result = verify_theorem_t41(n_steps=5)
    assert result["passes"], f"T262.1 FAIL: {result}"
    print(f"  T262.1 T41 theorem: PASS (H_G={result['H_G']:.4f}, H_sigma={result['H_sigma']:.4f})")

    # Test 2: manual serialize
    from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
    g = JinlingGraph()
    for i in range(10):
        g.add_node(f"n{i}")
    for i in range(9):
        g.add_edge(PortEdge(src=f"n{i}", dst=f"n{i+1}", port_src=i, port_dst=i+1))
        g.add_edge(PortEdge(src=f"n{i+1}", dst=f"n{i}", port_src=i+1, port_dst=i))
    for i in range(0, 8, 3):
        g.add_edge(PortEdge(src=f"n{i}", dst=f"n{i+3}", port_src=i+20, port_dst=i+3))
        g.add_edge(PortEdge(src=f"n{i+3}", dst=f"n{i}", port_src=i+3, port_dst=i+20))

    serializer = TYSerializer()
    ser_result = serializer.serialize(g, n_steps=8)
    assert ser_result.source_graph_entropy > 0, "T262.2 FAIL: source entropy is 0"
    assert len(ser_result.frame_sequence.frames) > 0, "T262.2 FAIL: no frames"
    print(f"  T262.2 Manual serialize: PASS (frames={len(ser_result.frame_sequence.frames)}, H_G={ser_result.source_graph_entropy:.4f})")

    # Test 3: information loss analyzer
    analyzer = InformationLossAnalyzer()
    loss_timeline = analyzer.analyze_loss_over_time(ser_result.frame_sequence)
    assert len(loss_timeline) > 0, "T262.3 FAIL: empty loss timeline"
    print(f"  T262.3 Info loss analyzer: PASS (timeline_len={len(loss_timeline)})")

    # Test 4: Frame to_dict/from_dict round-trip
    frame = ser_result.frame_sequence.frames[0]
    d = frame.to_dict()
    frame2 = Frame.from_dict(d)
    assert frame2.frame_id == frame.frame_id, "T262.4 FAIL: frame round-trip"
    assert abs(frame2.entropy - frame.entropy) < 1e-10, "T262.4 FAIL: entropy mismatch"
    print("  T262.4 Frame round-trip: PASS")

    return True


def test_t263_deserialize():
    """
    T263 -- T4.2 Deserialize theorem

    Deserialize with ICE active should have structural correction capability.
    """
    print("\n--- T263 T4.2 Deserialize Theorem (M222) ---")

    # Test 1: verify_theorem_t42
    result = verify_theorem_t42(n_steps=5)
    assert result["passes"], f"T263.1 FAIL: T42 not passed"
    print(f"  T263.1 T42 theorem: PASS (ice_rewire={result.get('beta_rewire_ice', 'N/A')})")

    # Test 2: manual deserialize with ICE
    from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
    g = JinlingGraph()
    for i in range(6):
        g.add_node(f"n{i}")
    for i in range(5):
        g.add_edge(PortEdge(src=f"n{i}", dst=f"n{i+1}", port_src=i, port_dst=i+1))
        g.add_edge(PortEdge(src=f"n{i+1}", dst=f"n{i}", port_src=i+1, port_dst=i))

    serializer = TYSerializer()
    ser_result = serializer.serialize(g, n_steps=3)

    deserializer = TYDeserializer(ido_context={"ice_active": True})
    des_result = deserializer.deserialize(ser_result.frame_sequence, ice_active=True)
    assert des_result.ice_active, "T263.2 FAIL: ICE should be active"
    print(f"  T263.2 Deserialize with ICE: PASS (rewire={des_result.beta_rewire_applied})")

    # Test 3: deserialize without ICE
    des_result_no_ice = deserializer.deserialize(ser_result.frame_sequence, ice_active=False)
    assert not des_result_no_ice.ice_active, "T263.3 FAIL: ICE should be inactive"
    assert "表层" in des_result_no_ice.failure_reason or not des_result_no_ice.failure_reason, \
        f"T263.3: failure_reason={des_result_no_ice.failure_reason}"
    print(f"  T263.3 Deserialize without ICE: PASS (fidelity={des_result_no_ice.reconstruction_fidelity:.4f})")

    # Test 4: DeserializeResult to_dict
    d = des_result.to_dict()
    assert "ice_active" in d, "T263.4 FAIL: missing ice_active"
    assert "reconstruction_fidelity" in d, "T263.4 FAIL: missing fidelity"
    print("  T263.4 DeserializeResult to_dict: PASS")

    return True


def test_t264_biserdes():
    """
    T264 -- T4.3 bi-SerDes completeness theorem

    4 conditions simultaneously met <=> True-TaiyiAGI
    """
    print("\n--- T264 T4.3 bi-SerDes Completeness (M222) ---")

    # Test 1: verify_theorem_t43
    result = verify_theorem_t43()
    assert result["passes"], f"T264.1 FAIL: {result}"
    print(f"  T264.1 T43 theorem: PASS (configs={result['configs_tested']})")

    # Test 2: BiSerDesChecker
    checker = BiSerDesChecker()

    # True-TaiyiAGI
    status = checker.check({
        "fteliology_channel": True,
        "ice_composite": True,
        "beta_rewire": True,
        "behavior_loop": True,
    })
    assert status.is_complete, "T264.2 FAIL: should be complete"
    assert status.classification == "True-TaiyiAGI", f"T264.2: wrong class: {status.classification}"
    print(f"  T264.2 True-TaiyiAGI classification: PASS")

    # ECP-Only
    status = checker.check({
        "fteliology_channel": True,
        "ice_composite": False,
        "beta_rewire": False,
        "behavior_loop": False,
    })
    assert not status.is_complete, "T264.3 FAIL: should not be complete"
    assert status.classification == "ECP-Only", f"T264.3: wrong class: {status.classification}"
    print(f"  T264.3 ECP-Only classification: PASS")

    # Test 4: classify_existing_module
    status = checker.classify_existing_module("M222")
    assert status.has_serialize, "T264.4 FAIL: M222 should have serialize"
    print(f"  T264.4 Module classification: PASS (M222={status.classification})")

    # Test 5: EML five hardening
    from modules.M133_W2_JinlingGraphBetaRewire import JinlingGraph, PortEdge
    g = JinlingGraph()
    for i in range(6):
        g.add_node(f"n{i}")
    for i in range(5):
        g.add_edge(PortEdge(src=f"n{i}", dst=f"n{i+1}", port_src=i, port_dst=i+1))
        g.add_edge(PortEdge(src=f"n{i+1}", dst=f"n{i}", port_src=i+1, port_dst=i))

    hardening = EMLFiveHardening()
    h_result = hardening.verify_hardening(g)
    assert isinstance(h_result, dict), "T264.5 FAIL: hardening result not dict"
    assert "writeback" in h_result, "T264.5 FAIL: missing writeback check"
    print(f"  T264.5 EML hardening: PASS (results={h_result})")

    # Test 6: BiSerDesStatus to_dict
    status_dict = status.to_dict()
    assert "classification" in status_dict, "T264.6 FAIL: missing classification"
    assert "is_complete" in status_dict, "T264.6 FAIL: missing is_complete"
    print("  T264.6 BiSerDesStatus to_dict: PASS")

    return True


if __name__ == "__main__":
    results = {}
    try:
        results["T262"] = "PASS" if test_t262_serialize() else "FAIL"
    except Exception as e:
        results["T262"] = f"FAIL: {e}"
        import traceback
        traceback.print_exc()

    try:
        results["T263"] = "PASS" if test_t263_deserialize() else "FAIL"
    except Exception as e:
        results["T263"] = f"FAIL: {e}"
        import traceback
        traceback.print_exc()

    try:
        results["T264"] = "PASS" if test_t264_biserdes() else "FAIL"
    except Exception as e:
        results["T264"] = f"FAIL: {e}"
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("M222 SerDesOntologyEngine MVE Results")
    print("=" * 50)
    total = len(results)
    passed = sum(1 for v in results.values() if v == "PASS")
    for k, v in results.items():
        icon = "[OK]" if v == "PASS" else "[FAIL]"
        print(f"  {icon} {k}: {v}")
    print(f"\nTotal: {passed}/{total} PASS")
