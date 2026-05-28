#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TYIDO Property 4 审计测试: 记忆（可寻址）
===========================================
测试 5 个目标模块的 P4 集成情况：
  M71 WalletPropertyBoundaryManager
  M72 ContributionMeasurementEngine
  M73 SelfReferentialPhiDetector
  M74 CarbonSiliconEntropyContract
  M176 OrgMemoryEngine

审计维度（5 项 × 5 模块 = 25 项）：
  1. P4基础设施初始化 — 4个组件非None
  2. get_state含tyido_p4 — 诊断段存在且含store_stats
  3. write持久化 — 核心操作后P4存储有数据
  4. read回读 — 从P4存储能读回写入的数据
  5. get_state verdict — 写入后verdict=PASS
"""

import sys

passed = 0
failed = 0
failures = []


def run_check(module: str, desc: str, func):
    """执行单条审计检查"""
    global passed, failed
    try:
        func()
        passed += 1
        print(f"  [PASS] {desc}")
    except Exception as e:
        failed += 1
        msg = f"{type(e).__name__}: {e}"
        failures.append((module, desc, msg))
        print(f"  [FAIL] {desc} — {msg}")


def audit_m71():
    print("\n--- M71 WalletPropertyBoundaryManager ---")
    from modules.M71_WalletPropertyBoundaryManager import get_instance, Layer
    inst = get_instance()

    def check_init():
        assert inst._p4_available is True
        assert inst._p4_store is not None
        assert inst._p4_index is not None
        assert inst._p4_forget_policy is not None
        assert inst._p4_merge_engine is not None

    def check_state():
        s = inst.get_state()
        assert "tyido_p4" in s
        assert s["tyido_p4"]["available"] is True
        assert "store_stats" in s["tyido_p4"]
        assert "index_stats" in s["tyido_p4"]
        assert "forget_stats" in s["tyido_p4"]
        assert "verdict" in s["tyido_p4"]

    def check_write_boundary():
        inst.define_boundary("W-T4", Layer.L1_ONTOLOGY, "prop1", 0.6)
        keys = inst._p4_store.keys()
        assert any("wallet:W-T4" in k for k in keys), f"P4 keys: {keys}"

    def check_write_contribution():
        inst.measure_contribution("a1", [0.1, 0.3], [0.2, 0.4], ["bob"])
        keys = inst._p4_store.keys()
        assert any("contribution:a1" in k for k in keys), f"P4 keys: {keys}"

    def check_read_verdict():
        s = inst.get_state()
        assert s["tyido_p4"]["verdict"] == "PASS", f"verdict={s['tyido_p4']['verdict']}"
        r = inst._p4_store.read("contribution:a1")
        assert r["found"] is True, f"read result: {r}"
        assert "total_contribution" in r["value"]

    run_check("M71", "P4基础设施初始化", check_init)
    run_check("M71", "get_state含tyido_p4", check_state)
    run_check("M71", "write持久化(边界定义)", check_write_boundary)
    run_check("M71", "write持久化(贡献度量)", check_write_contribution)
    run_check("M71", "read回读 + verdict=PASS", check_read_verdict)


def audit_m72():
    print("\n--- M72 ContributionMeasurementEngine ---")
    from modules.M72_ContributionMeasurementEngine import get_instance
    inst = get_instance()

    def check_init():
        assert inst._p4_available is True
        assert inst._p4_store is not None
        assert inst._p4_index is not None

    def check_state():
        s = inst.get_state()
        assert "tyido_p4" in s
        assert s["tyido_p4"]["available"] is True
        assert "store_stats" in s["tyido_p4"]

    def check_write():
        inst.update_agent_profile("a1", "base_contribution", 0.75)
        keys = inst._p4_store.keys()
        assert any("profile:a1" in k for k in keys), f"P4 keys: {keys}"

    def check_read():
        r = inst._p4_store.read("profile:a1:base_contribution")
        assert r["found"] is True, f"read: {r}"
        assert r["value"] == 0.75

    def check_verdict():
        s = inst.get_state()
        assert s["tyido_p4"]["verdict"] == "PASS", f"verdict={s['tyido_p4']['verdict']}"

    run_check("M72", "P4基础设施初始化", check_init)
    run_check("M72", "get_state含tyido_p4", check_state)
    run_check("M72", "write持久化(代理配置)", check_write)
    run_check("M72", "read回读", check_read)
    run_check("M72", "verdict=PASS", check_verdict)


def audit_m73():
    print("\n--- M73 SelfReferentialPhiDetector ---")
    from modules.M73_SelfReferentialPhiDetector import get_instance, InfoElement
    inst = get_instance()

    def check_init():
        assert inst._p4_available is True
        assert inst._p4_store is not None
        assert inst._p4_index is not None

    def check_state():
        s = inst.get_state()
        assert "tyido_p4" in s
        assert s["tyido_p4"]["available"] is True

    def check_write():
        inst.build_system("S-T4", [
            InfoElement("E1", [0.3, 0.5], ["E2"], 0.7, False),
            InfoElement("E2", [0.4, 0.6], ["E1"], 0.8, False),
        ])
        inst.analyze_system("S-T4")
        keys = inst._p4_store.keys()
        assert any("detection:S-T4" in k for k in keys), f"P4 keys: {keys}"

    def check_read():
        r = inst._p4_store.read("detection:S-T4")
        assert r["found"] is True, f"read: {r}"
        assert "phi_value" in r["value"]

    def check_verdict():
        s = inst.get_state()
        assert s["tyido_p4"]["verdict"] == "PASS", f"verdict={s['tyido_p4']['verdict']}"

    run_check("M73", "P4基础设施初始化", check_init)
    run_check("M73", "get_state含tyido_p4", check_state)
    run_check("M73", "write持久化(检测)", check_write)
    run_check("M73", "read回读", check_read)
    run_check("M73", "verdict=PASS", check_verdict)


def audit_m74():
    print("\n--- M74 CarbonSiliconEntropyContract ---")
    from modules.M74_CarbonSiliconEntropyContract import get_instance
    inst = get_instance()

    def check_init():
        assert inst._p4_available is True
        assert inst._p4_store is not None
        assert inst._p4_index is not None

    def check_state():
        s = inst.get_state()
        assert "tyido_p4" in s
        assert s["tyido_p4"]["available"] is True

    def check_write_contract():
        inst.sign_contract("h-t4", "ai-t4")
        keys = inst._p4_store.keys()
        assert any("contract:CONT-" in k for k in keys), f"P4 keys: {keys}"

    def check_write_entropy():
        inst.compute_carbon_entropy_change("h-t4", "test action for P4")
        keys = inst._p4_store.keys(tag="entropy_change")
        assert len(keys) > 0, f"entropy_change keys: {keys}"

    def check_read_verdict():
        s = inst.get_state()
        assert s["tyido_p4"]["verdict"] == "PASS", f"verdict={s['tyido_p4']['verdict']}"
        # 读取合约数据
        ckeys = [k for k in inst._p4_store.keys() if "contract:CONT-" in k]
        assert len(ckeys) > 0, "no contract keys found"
        r = inst._p4_store.read(ckeys[0])
        assert r["found"] is True, f"read contract: {r}"

    run_check("M74", "P4基础设施初始化", check_init)
    run_check("M74", "get_state含tyido_p4", check_state)
    run_check("M74", "write持久化(合约签署)", check_write_contract)
    run_check("M74", "write持久化(熵变记录)", check_write_entropy)
    run_check("M74", "read回读 + verdict=PASS", check_read_verdict)


def audit_m176():
    print("\n--- M176 OrgMemoryEngine ---")
    from modules.M176_OrgMemoryEngine import OrgMemoryEngine, MemoryType
    inst = OrgMemoryEngine.get_instance()

    def check_init():
        assert inst._p4_available is True
        assert inst._p4_store is not None
        assert inst._p4_index is not None

    def check_state():
        s = inst.get_state()
        assert "tyido_p4" in s
        assert s["tyido_p4"]["available"] is True

    def check_write():
        inst.remember("a-t4", "P4审计测试记忆", memory_type=MemoryType.EXPERIENCE, tags=["test"])
        keys = inst._p4_store.keys()
        assert any("org_memory:" in k for k in keys), f"P4 keys: {keys}"

    def check_read():
        org_keys = [k for k in inst._p4_store.keys() if "org_memory:" in k]
        assert len(org_keys) > 0, "no org_memory keys found"
        r = inst._p4_store.read(org_keys[-1])
        assert r["found"] is True, f"read: {r}"
        assert "P4审计测试记忆" in r["value"]["content"], f"value: {r['value']}"

    def check_verdict():
        s = inst.get_state()
        assert s["tyido_p4"]["verdict"] == "PASS", f"verdict={s['tyido_p4']['verdict']}"

    run_check("M176", "P4基础设施初始化", check_init)
    run_check("M176", "get_state含tyido_p4", check_state)
    run_check("M176", "write持久化(remember)", check_write)
    run_check("M176", "read回读", check_read)
    run_check("M176", "verdict=PASS", check_verdict)


if __name__ == "__main__":
    print("=" * 60)
    print("TYIDO P4 审计测试: 记忆（可寻址）")
    print("=" * 60)

    audit_m71()
    audit_m72()
    audit_m73()
    audit_m74()
    audit_m176()

    print("\n" + "=" * 60)
    print(f"审计结果: {passed}/{passed + failed} PASS")
    if failed > 0:
        print(f"失败项 ({failed}):")
        for mod, desc, msg in failures:
            print(f"  [{mod}] {desc}: {msg}")
    else:
        print("ALL PASS!")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
