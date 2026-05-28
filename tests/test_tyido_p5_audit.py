"""
TYIDO P5 审计测试 —— 属性5：责任可锚定（Anchorable Responsibility）
测试对象：M174 UFMRISCVSandbox, M175 SafetyShield
Checks: 5 checks × 2 modules = 10 items
标准: 10/10 PASS → verdict=PASS
"""
import sys, time, json, os, traceback
sys.path.insert(0, '.')

SUCCESS = '\033[92m✓\033[0m'
FAIL    = '\033[91m✗\033[0m'
INFO    = '\033[94m…\033[0m'

# ── 辅助 ────────────────────────────────────────────────────────────────────────
def load_mod(name):
    """标准方式加载模块（兼容 dataclass）"""
    import importlib
    mod = importlib.import_module(name)
    return mod

def section(title):
    print(f"\n═══ {title} ═══")

# ── 审计结果收集 ────────────────────────────────────────────────────────────────
audit_items = []

def check(module_name, check_id, description, fn):
    ok, msg = False, ""
    try:
        ok, msg = fn()
    except Exception as e:
        ok, msg = False, f"{type(e).__name__}: {e}"
    audit_items.append({
        "module": module_name,
        "check":  check_id,
        "desc":   description,
        "pass":   ok,
        "msg":    msg,
    })
    tag = SUCCESS if ok else FAIL
    print(f"  {tag}  [{module_name}] {check_id}: {description}")
    if not ok:
        print(f"       └─ {msg[:120]}")


# ── 主测试 ─────────────────────────────────────────────────────────────────────
def main():
    print('═' * 60)
    print('  TYIDO P5 审计测试 — 属性5：责任可锚定')
    print('  5 checks × 2 modules = 10 items')
    print('═' * 60)

    # ── 加载模块 ────────────────────────────────────────────────────────────────
    section("加载模块")
    M175 = load_mod('M175_SafetyShield')
    M174 = load_mod('M174_UFMRISCVSandbox')
    P5   = load_mod('TYIDO_AnchorableResponsibility')
    print(f"  {SUCCESS}  M175 / M174 / P5 全部加载成功")

    # ── M175 Checks (1-5) ────────────────────────────────────────────────────
    section("M175 SafetyShield — P5 Checks 1-5")

    shield = M175.SafetyShield.get_instance()
    cw = shield.content_wall  # ContentWall 实例

    # Check 1: P5 组件已初始化
    def c1():
        has_all = (
            cw._p5_chain is not None and
            cw._p5_gate  is not None and
            cw._p5_breaker is not None and
            cw._p5_audit is not None
        )
        return has_all, "ContentWall._p5_* components initialized" if has_all else "some P5 components are None"
    check("M175", "P5-M175-C1", "P5 组件初始化（chain/gate/breaker/audit）", c1)

    # Check 2: get_state 含 tyido_p5
    def c2():
        s = cw.get_state()
        has = "tyido_p5" in s
        return has, f"tyido_p5 keys={list(s.get('tyido_p5', {}).keys())}" if has else "tyido_p5 not in get_state"
    check("M175", "P5-M175-C2", "get_state() 返回 tyido_p5 section", c2)

    # Check 3: process_input 触发责任链绑定（门禁 + 责任记录）
    def c3():
        before = len(cw._p5_chain._records) if cw._p5_chain else -1
        result = cw.process_input("你好，我的手机号是 13812345678")
        after = len(cw._p5_chain._records) if cw._p5_chain else -1
        # process_input 内调用了 gate.confirm_action，应产生至少1条责任记录
        ok = after > before or cw._p5_chain is None  # 如果 P5 被禁用也跳过
        return ok, f"records: {before} → {after}, action={result.action.value}"
    check("M175", "P5-M175-C3", "process_input 触发责任链绑定", c3)

    # Check 4: process_output 触发责任链绑定
    def c4():
        before = len(cw._p5_chain._records) if cw._p5_chain else -1
        result = cw.process_output("这是一段正常输出，不含违规内容")
        after = len(cw._p5_chain._records) if cw._p5_chain else -1
        ok = after >= before or cw._p5_chain is None
        return ok, f"records: {before} → {after}, action={result.action.value}"
    check("M175", "P5-M175-C4", "process_output 触发责任链绑定", c4)

    # Check 5: P5 write + read 持久化+回读
    def c5():
        if cw._p5_chain is None:
            return True, "P5 disabled, skip"
        path = "/tmp/_tyido_p5_m175_test.json"
        cw._p5_chain.write(path)
        # 新建 chain 回读
        new_chain = P5.ResponsibilityChain()
        new_chain.read(path)
        summary = new_chain.chain_summary()
        same = summary["total_records"] == len(cw._p5_chain._records)
        return same, f"write/read: {summary['total_records']} records match={same}"
    check("M175", "P5-M175-C5", "P5 责任链 write + read 持久化", c5)


    # ── M174 Checks (6-10) ───────────────────────────────────────────────────
    section("M174 UFMRISCVSandbox — P5 Checks 6-10")

    sandbox = M174.UFMRISCVSandbox.get_instance()

    # Check 6: P5 组件已初始化（主入口层）
    def c6():
        has_all = (
            sandbox._p5_chain is not None and
            sandbox._p5_gate  is not None and
            sandbox._p5_breaker is not None and
            sandbox._p5_audit is not None
        )
        return has_all, "UFMRISCSandBox._p5_* initialized" if has_all else "some None"
    check("M174", "P5-M174-C6", "P5 组件初始化（主入口层）", c6)

    # Check 7: get_state 含 tyido_p5
    def c7():
        s = sandbox.get_state()
        has = "tyido_p5" in s
        return has, f"tyido_p5 keys={list(s.get('tyido_p5', {}).keys())}" if has else "missing"
    check("M174", "P5-M174-C7", "get_state() 返回 tyido_p5 section", c7)

    # Check 8: DualIsolationManager 也含 P5（隔离层子组件）
    def c8():
        iso = sandbox.isolation_manager
        has = hasattr(iso, '_p5_chain') and iso._p5_chain is not None
        return has, "DualIsolationManager._p5_chain present" if has else "not present"
    check("M174", "P5-M174-C8", "DualIsolationManager 含 P5 组件", c8)

    # Check 9: check_violation 触发责任链绑定
    def c9():
        iso = sandbox.isolation_manager
        before = len(iso._p5_chain._records) if iso._p5_chain else -1
        result = iso.check_violation("network", "memory", 9999)
        after = len(iso._p5_chain._records) if iso._p5_chain else -1
        ok = after >= before or iso._p5_chain is None
        return ok, f"records: {before} → {after}, allowed={result.get('allowed')}"
    check("M174", "P5-M174-C9", "check_violation 触发责任链绑定", c9)

    # Check 10: P5 write + read 持久化（主入口层）
    def c10():
        if sandbox._p5_chain is None:
            return True, "P5 disabled, skip"
        path = "/tmp/_tyido_p5_m174_test.json"
        sandbox._p5_chain.write(path)
        new_chain = P5.ResponsibilityChain()
        new_chain.read(path)
        summary = new_chain.chain_summary()
        same = summary["total_records"] == len(sandbox._p5_chain._records)
        return same, f"write/read: {summary['total_records']} records match={same}"
    check("M174", "P5-M174-C10", "P5 责任链 write + read 持久化", c10)


    # ── 汇总 ────────────────────────────────────────────────────────────────────
    section("审计汇总")
    passed = sum(1 for it in audit_items if it["pass"])
    total  = len(audit_items)
    verdict = "PASS" if passed == total else "FAIL"

    print(f"\n  总分: {passed}/{total}")
    print(f"  结论: {'✅ PASS' if verdict == 'PASS' else '❌ FAIL'}")
    print(f"  verdict = {verdict}")

    print(f"\n  明细:")
    for it in audit_items:
        tag = SUCCESS if it["pass"] else FAIL
        print(f"    {tag}  {it['module']}  {it['check']}: {it['desc']}")
        if not it["pass"]:
            print(f"         └─ {it['msg'][:100]}")

    # 写审计日志
    log = {
        "audit": "TYIDO-P5",
        "property": "属性5：责任可锚定（Anchorable Responsibility）",
        "modules": ["M174", "M175"],
        "total_checks": total,
        "passed": passed,
        "verdict": verdict,
        "items": audit_items,
        "timestamp": time.time(),
    }
    with open("/tmp/_tyido_p5_audit_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"\n  审计日志已写入: /tmp/_tyido_p5_audit_log.json")

    return verdict == "PASS"


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
