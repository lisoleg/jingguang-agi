#!/usr/bin/env python3
"""
MVE_v735_T254_T272.py — v7.35 Minimum Viable Experiment
Tests T2.54-T2.72 for M236-M243 modules (using actual exported functions)
"""
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def test_m236():
    from modules.M236_MinimalComputationalismEngine import (
        verify_theorem_t254, verify_theorem_t255, verify_organizational_invariance, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M236_MinimalComputationalismEngine"
    r254 = verify_theorem_t254()
    r255 = verify_theorem_t255()
    oi = verify_organizational_invariance()
    print(f"  M236: T254={r254['proved']}, T255={r255['proved']}, OrgInv={oi.get('invariant_preserved', oi.get('proved', 'N/A'))}")
    return r254["proved"] and r255["proved"]

def test_m237():
    from modules.M237_PrimeBasisCodecEngine import (
        verify_theorem_t256, verify_theorem_t257, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M237_PrimeBasisCodecEngine"
    r256 = verify_theorem_t256()
    r257 = verify_theorem_t257()
    print(f"  M237: T256={r256['proved']}, T257={r257['proved']}")
    return r256["proved"] and r257["proved"]

def test_m238():
    from modules.M238_TopoSpectralDynamicsEngine import (
        verify_theorem_t258, verify_theorem_t259, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M238_TopoSpectralDynamicsEngine"
    r258 = verify_theorem_t258()
    r259 = verify_theorem_t259()
    print(f"  M238: T258={r258['proved']}, T259={r259['proved']}")
    return r258["proved"] and r259["proved"]

def test_m239():
    from modules.M239_LightBasedComputeEngine import (
        verify_theorem_t260, verify_theorem_t261, verify_theorem_t262, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M239_LightBasedComputeEngine"
    r260 = verify_theorem_t260()
    r261 = verify_theorem_t261()
    r262 = verify_theorem_t262()
    print(f"  M239: T260={r260['proved']}, T261={r261['proved']}, T262={r262['proved']}")
    return r260["proved"] and r261["proved"] and r262["proved"]

def test_m240():
    from modules.M240_InverseTopologyEngine import (
        verify_theorem_t263, verify_theorem_t264, verify_theorem_t265, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M240_InverseTopologyEngine"
    r263 = verify_theorem_t263()
    r264 = verify_theorem_t264()
    r265 = verify_theorem_t265()
    print(f"  M240: T263={r263['proved']}, T264={r264['proved']}, T265={r265['proved']}")
    return r263["proved"] and r264["proved"] and r265["proved"]

def test_m241():
    from modules.M241_FtelConfinementEngine import (
        verify_theorem_t263 as vt263, verify_theorem_t264 as vt264,
        verify_theorem_t265 as vt265, verify_prediction_p1, verify_prediction_p2, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M241_FtelConfinementEngine"
    r263b = vt263()
    r264b = vt264()
    r265b = vt265()
    p1 = verify_prediction_p1()
    p2 = verify_prediction_p2()
    print(f"  M241: T263b={r263b['proved']}, T264b={r264b['proved']}, T265b={r265b['proved']}, P1={p1['holds']}, P2={p2['holds']}")
    return r263b["proved"] and r264b["proved"] and r265b["proved"]

def test_m242():
    from modules.M242_MNQWaveCoherenceEngine import (
        verify_theorem_t266, verify_theorem_t267, verify_theorem_t268,
        verify_prediction_p1, verify_prediction_p2, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M242_MNQWaveCoherenceEngine"
    r266 = verify_theorem_t266()
    r267 = verify_theorem_t267()
    r268 = verify_theorem_t268()
    p1 = verify_prediction_p1()
    p2 = verify_prediction_p2()
    print(f"  M242: T266={r266['proved']}, T267={r267['proved']}, T268={r268['proved']}, P1={p1['holds']}, P2={p2['holds']}")
    return r266["proved"] and r267["proved"] and r268["proved"]

def test_m243():
    from modules.M243_RelationalGraphTransformerBridge import (
        verify_theorem_t269, verify_theorem_t270, verify_theorem_t271,
        verify_prediction_p1, verify_prediction_p2, get_instance
    )
    e = get_instance()
    assert e.get_state()["module"] == "M243_RelationalGraphTransformerBridge"
    r269 = verify_theorem_t269()
    r270 = verify_theorem_t270()
    r271 = verify_theorem_t271()
    p1 = verify_prediction_p1()
    p2 = verify_prediction_p2()
    print(f"  M243: T269={r269['proved']}, T270={r270['proved']}, T271={r271['proved']}, P1={p1['holds']}, P2={p2['holds']}")
    return r269["proved"] and r270["proved"] and r271["proved"]

if __name__ == "__main__":
    print("=" * 60)
    print("MVE v7.35: T2.54-T2.72 (M236-M243)")
    print("=" * 60)
    results = {}
    for name, fn in [
        ("M236", test_m236), ("M237", test_m237), ("M238", test_m238),
        ("M239", test_m239), ("M240", test_m240), ("M241", test_m241),
        ("M242", test_m242), ("M243", test_m243),
    ]:
        try:
            ok = fn()
            results[name] = "PASS" if ok else "FAIL"
        except Exception as ex:
            results[name] = f"ERROR: {ex}"
            import traceback; traceback.print_exc()

    print("\n" + "=" * 60)
    n_pass = sum(1 for v in results.values() if v == "PASS")
    n_total = len(results)
    print(f"Results: {n_pass}/{n_total} PASS")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 60)
