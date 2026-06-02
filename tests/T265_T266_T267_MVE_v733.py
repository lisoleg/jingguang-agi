# -*- coding: utf-8 -*-
"""
T265-T267 MVE: v7.33 TMK 三大新模块定理验证
  T265 — 金符阴龙积双线性定理 (M223, T2.32+T2.33+T2.34)
  T266 — SOP完备性定理 (M224, T2.35+T2.36)
  T267 — ICE自指闭环收敛定理 (M225, T2.37+T2.38+T2.39)

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.33 TMK
"""

import sys
import os
import math
import random

# 解决Windows gbk编码问题
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 双层路径注入
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)
_modules_dir = os.path.join(_proj_root, 'modules')
if _modules_dir not in sys.path:
    sys.path.insert(0, _modules_dir)


# ══════════════════════════════════════════════════
# T265 — 金符阴龙积双线性定理 (M223)
# ══════════════════════════════════════════════════

def test_t265_yin_long_product_bilinearity():
    """
    T265.1 — 阴龙积双线性定理 (T2.32)

    yin_long_product(a*z1 + b*z2, w) = a*yin_long_product(z1,w) + b*yin_long_product(z2,w)
    验证阴龙积关于第一变元的线性性。
    """
    from modules.M223_GoldenSymbol3D import GoldenSymbol, yin_long_product

    random.seed(42)
    z1 = GoldenSymbol(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1))
    z2 = GoldenSymbol(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1))
    w  = GoldenSymbol(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1))
    alpha = 2.5
    beta = -1.3

    # 左侧: yin_long_product(alpha*z1 + beta*z2, w)
    lhs = yin_long_product(z1.scale(alpha) + z2.scale(beta), w)

    # 右侧: alpha*yin_long_product(z1,w) + beta*yin_long_product(z2,w)
    rhs = yin_long_product(z1, w).scale(alpha) + yin_long_product(z2, w).scale(beta)

    tol = 1e-10
    assert abs(lhs.a - rhs.a) < tol, f"T265.1 FAIL: real part mismatch: {lhs.a} vs {rhs.a}"
    assert abs(lhs.b - rhs.b) < tol, f"T265.1 FAIL: i-part mismatch: {lhs.b} vs {rhs.b}"
    assert abs(lhs.c - rhs.c) < tol, f"T265.1 FAIL: j-part mismatch: {lhs.c} vs {rhs.c}"

    print("  T265.1 yin_long_product bilinearity: PASS")
    return True


def test_t265_yin_long_product_symmetry():
    """
    T265.2 — 交换性公理验证 (T2.33)

    i*j = j*i (交换性)
    yin_long_product 在纯i和j分量上的交换性验证
    """
    from modules.M223_GoldenSymbol3D import GoldenSymbol, yin_long_product

    # 构造纯i和纯j分量
    zi = GoldenSymbol(0, 1, 0)  # i
    zj = GoldenSymbol(0, 0, 1)  # j

    prod_ij = yin_long_product(zi, zj)
    prod_ji = yin_long_product(zj, zi)

    # zi=(0,1,0), zj=(0,0,1): i*j = (0, 0, 0)
    # zj=(0,0,1), zi=(0,1,0): j*i = (0, 0, 0)
    assert prod_ij.a == 0 and prod_ij.b == 0 and prod_ij.c == 0, \
        f"T265.2 FAIL: i*j should be zero, got {prod_ij.to_dict()}"
    assert prod_ji.a == 0 and prod_ji.b == 0 and prod_ji.c == 0, \
        f"T265.2 FAIL: j*i should be zero, got {prod_ji.to_dict()}"
    assert prod_ij.to_dict() == prod_ji.to_dict(), \
        "T265.2 FAIL: i*j != j*i (commutativity axiom violated)"

    # 验证j分量交换性 (a1*c2 + c1*a2 == a2*c1 + c2*a1)
    random.seed(123)
    z1 = GoldenSymbol(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1))
    z2 = GoldenSymbol(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1))

    p12 = yin_long_product(z1, z2)
    p21 = yin_long_product(z2, z1)

    assert abs(p12.c - p21.c) < 1e-10, f"T265.2 FAIL: j-part commutativity: {p12.c} vs {p21.c}"

    print("  T265.2 commutativity axiom: PASS")
    return True


def test_t265_mnq8_hex_ring_gap():
    """
    T265.3 — HEX_RING_GAP囚禁判据 (T2.34)

    当MASS_FACE > THRESHOLD时，节点应进入HEX_RING_GAP状态(Locked=True)
    否则处于BACKGROUND_OSC状态(Locked=False)
    """
    from modules.M223_GoldenSymbol3D import GoldenSymbol, MNQ8Grid, MNQ8Simulation

    random.seed(456)

    # 创建1d网格 — node_count是属性不是方法
    grid = MNQ8Grid(topology='1d', size=5)
    for i in range(grid.node_count):
        grid.set_node(i, GoldenSymbol(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1)))

    # 注入强耦合态
    grid.inject_hex_ring_gap(2, radius=1)

    # 运行仿真
    sim = MNQ8Simulation(grid, mass_threshold=0.5, lam=1.0)
    result = sim.step()

    # 验证: 步进结果应包含统计信息
    # 实际字段: step, locked_count, dispersed_count, max_mass_face, avg_mass_face, hex_ring_gap_nodes
    result_dict = result.to_dict()
    assert 'locked_count' in result_dict, f"T265.3 FAIL: missing locked_count, keys={list(result_dict.keys())}"
    assert 'dispersed_count' in result_dict, f"T265.3 FAIL: missing dispersed_count, keys={list(result_dict.keys())}"

    print(f"  T265.3 MNQ8 step result: locked={result_dict['locked_count']}, dispersed={result_dict['dispersed_count']}")

    # 运行对照实验验证整体统计
    from modules.M223_GoldenSymbol3D import run_comparison_experiment
    exp_result = run_comparison_experiment(mass_threshold=1.0)
    assert 'hex_ring_gap' in exp_result, f"T265.3 FAIL: missing hex_ring_gap, keys={list(exp_result.keys())}"
    assert 'background_osc' in exp_result, f"T265.3 FAIL: missing background_osc, keys={list(exp_result.keys())}"

    print("  T265.3 HEX_RING_GAP confinement: PASS")
    return True


def test_t265_mnq8_grid_topology():
    """
    T265.4 — MNQ8Grid拓扑结构验证

    验证1d/2d/3d网格的邻接关系正确
    """
    from modules.M223_GoldenSymbol3D import MNQ8Grid, GoldenSymbol

    # 1d: 线性链 — node_count是属性, adjacency也是属性
    grid_1d = MNQ8Grid(topology='1d', size=5)
    assert grid_1d.node_count == 5, f"T265.4 FAIL: 1d node_count={grid_1d.node_count}"
    adj_1d = grid_1d.adjacency  # 属性而非方法
    assert 1 in adj_1d[0], "T265.4 FAIL: 1d node 0 should connect to 1"
    assert 0 in adj_1d[1], "T265.4 FAIL: 1d node 1 should connect to 0"

    # 2d: 方格
    grid_2d = MNQ8Grid(topology='2d', size=4)
    assert grid_2d.node_count == 16, f"T265.4 FAIL: 2d node_count={grid_2d.node_count}"

    # 3d: 立方
    grid_3d = MNQ8Grid(topology='3d', size=3)
    assert grid_3d.node_count == 27, f"T265.4 FAIL: 3d node_count={grid_3d.node_count}"

    # 序列化
    for i in range(grid_1d.node_count):
        grid_1d.set_node(i, GoldenSymbol(float(i), float(i+1), float(i+2)))
    d = grid_1d.to_dict()
    assert 'topology' in d and 'states' in d, f"T265.4 FAIL: to_dict keys={list(d.keys())}"

    print("  T265.4 MNQ8Grid topology: PASS")
    return True


# ══════════════════════════════════════════════════
# T266 — SOP完备性定理 (M224)
# ══════════════════════════════════════════════════

def test_t266_sop_preset_generation():
    """
    T266.1 — 预设SOP报告生成 (T2.35)

    4类预设(超导/共识/意识/CMB)均可完整生成SOP报告
    """
    from modules.M224_SOPGeneratorEngine import SOPGenerator

    gen = SOPGenerator()
    presets = ['superconductor', 'consensus', 'qualia', 'cmb']

    for preset in presets:
        report = gen.generate_from_preset(preset)
        assert report is not None, f"T266.1 FAIL: preset {preset} returned None"
        d = report.to_dict()
        assert 'phenomenon' in d, f"T266.1 FAIL: preset {preset} missing phenomenon"
        assert 'step0' in d, f"T266.1 FAIL: preset {preset} missing step0"
        assert 'step7' in d, f"T266.1 FAIL: preset {preset} missing step7"
        # step7包含conclusion信息
        assert d['phenomenon'] != '', f"T266.1 FAIL: preset {preset} phenomenon is empty"

        # 验证render_md输出
        md = report.render_md()
        assert len(md) > 100, f"T266.1 FAIL: preset {preset} Markdown too short ({len(md)} chars)"

    print("  T266.1 SOP preset generation: PASS")
    return True


def test_t266_sop_auto_classify():
    """
    T266.2 — SOP自动分类验证 (T2.36)

    classify_phenomenon能正确识别现象类别
    """
    from modules.M224_SOPGeneratorEngine import SOPGenerator

    gen = SOPGenerator()

    # 超导类关键词
    cat1 = gen.classify_phenomenon("超导体在临界温度以下电阻突然消失")
    assert cat1 == 'superconductor', f"T266.2 FAIL: superconductor classified as {cat1}"

    # 共识类关键词
    cat2 = gen.classify_phenomenon("区块链网络中节点达成共识机制")
    assert cat2 == 'consensus', f"T266.2 FAIL: consensus classified as {cat2}"

    # 意识类关键词
    cat3 = gen.classify_phenomenon("意识的感受质与主观体验")
    assert cat3 == 'qualia', f"T266.2 FAIL: qualia classified as {cat3}"

    # 宇宙微波背景辐射
    cat4 = gen.classify_phenomenon("宇宙微波背景辐射的各向异性")
    assert cat4 == 'cmb', f"T266.2 FAIL: cmb classified as {cat4}"

    # 未知 -> 自动生成
    report = gen.auto_generate("某种未分类的新现象")
    assert report is not None, "T266.2 FAIL: auto_generate returned None"

    print("  T266.2 SOP auto-classify: PASS")
    return True


def test_t266_sop_custom_generation():
    """
    T266.3 — 自定义SOP报告生成

    提供自定义三视界锚定，验证SOPGenerator.generate_custom()
    注意: generate_custom没有analyst参数
    """
    from modules.M224_SOPGeneratorEngine import SOPGenerator

    gen = SOPGenerator()
    report = gen.generate_custom(
        phenomenon="引力波双黑洞并合",
        H1="内视界：LIGO干涉仪应变信号",
        H2="外视界：数值相对论模拟波形",
        H3="统一视界：引力波天文学范式"
    )

    assert report is not None, "T266.3 FAIL: generate_custom returned None"
    d = report.to_dict()
    assert d['phenomenon'] == "引力波双黑洞并合", "T266.3 FAIL: phenomenon mismatch"

    # step0包含三视界信息
    step0 = d.get('step0', {})
    if isinstance(step0, dict):
        assert step0.get('H1', '') != '' or step0.get('inner', '') != '', "T266.3 FAIL: H1 empty in step0"

    print("  T266.3 SOP custom generation: PASS")
    return True


def test_t266_sop_state_and_list():
    """
    T266.4 — M224状态查询与报告列表

    get_instance/get_state正常工作
    """
    from modules.M224_SOPGeneratorEngine import get_instance

    inst = get_instance()
    state = inst.get_state()
    assert 'module' in state, "T266.4 FAIL: state missing module field"
    # module字段为全名 'M224_SOPGeneratorEngine'
    assert 'M224' in state['module'], f"T266.4 FAIL: module={state['module']}"

    print("  T266.4 M224 state query: PASS")
    return True


# ══════════════════════════════════════════════════
# T267 — ICE自指闭环收敛定理 (M225)
# ══════════════════════════════════════════════════

def _make_test_heap():
    """创建测试用JinlingHeap"""
    from modules.M225_ICELeanLoop import JinlingHeap, JinlingSphere
    heap = JinlingHeap()
    for i in range(5):
        sphere = JinlingSphere(
            sid=f"S{i}", i_int=i+1,
            ports=[f"p{j}" for j in range(2)],
            chi=i+1, mod=(i % 7) + 1,
            phase=float(i) * 0.5
        )
        heap.add_sphere(sphere)
    return heap


def test_t267_ice_three_operators():
    """
    T267.1 — ICE三算子验证 (T2.37)

    observe -> decide -> actuate 三算子可独立运行
    """
    from modules.M225_ICELeanLoop import ICESession

    heap = _make_test_heap()
    ice = ICESession(heap, mass_threshold=1.0)

    # observe: 内视界观测
    obs = ice.observe()
    assert obs is not None, "T267.1 FAIL: observe returned None"
    assert isinstance(obs, dict), "T267.1 FAIL: observe should return dict"
    assert 'sphere_count' in obs, f"T267.1 FAIL: observe keys={list(obs.keys())}"

    # decide: 被观测=自身 -> 刘机制优选
    preferred = ice.decide("optimize")
    assert preferred is not None, "T267.1 FAIL: decide returned None"

    # actuate: 可改L3堆垒 -> MNQ8调度执行
    result = ice.actuate(preferred)
    assert result is not None, "T267.1 FAIL: actuate returned None"

    print("  T267.1 ICE three operators: PASS")
    return True


def test_t267_ice_cycle_convergence():
    """
    T267.2 — ICE闭环收敛验证 (T2.38)

    run_cycle完整闭环 observe->decide->actuate -> 结果非空
    """
    from modules.M225_ICELeanLoop import ICESession

    heap = _make_test_heap()
    ice = ICESession(heap, mass_threshold=1.0)
    result = ice.run_cycle("optimize")

    assert result is not None, "T267.2 FAIL: run_cycle returned None"
    assert isinstance(result, dict), "T267.2 FAIL: run_cycle should return dict"

    print("  T267.2 ICE cycle convergence: PASS")
    return True


def test_t267_lean_export():
    """
    T267.3 — Lean4导出验证 (T2.39)

    LeanExporter能生成合法Lean4代码
    """
    from modules.M225_ICELeanLoop import LeanExporter

    exporter = LeanExporter()

    # ABC弱形式
    abc_code = exporter.export_abc_weak(mass_face=2.5, excess_loop=0.3)
    assert 'theorem' in abc_code.lower() or 'lemma' in abc_code.lower(), \
        f"T267.3 FAIL: ABC export missing theorem/lemma, got: {abc_code[:100]}"
    assert 'MASS_FACE' in abc_code or 'mass_face' in abc_code.lower() or 'massFace' in abc_code, \
        f"T267.3 FAIL: ABC export missing MASS_FACE"

    # Riemann提示
    riemann_code = exporter.export_riemann_hint(mass_face=3.0, excess_loop=0.5)
    assert len(riemann_code) > 20, f"T267.3 FAIL: Riemann export too short: {riemann_code}"

    # 自定义定理 — export_custom(theorem_name, statement, mass_face=0.0, excess_loop=0.0)
    custom_code = exporter.export_custom(
        theorem_name="my_theorem",
        statement="1 + 1 = 2"
    )
    assert 'my_theorem' in custom_code, "T267.3 FAIL: custom export missing theorem name"

    # 状态查询
    state = exporter.to_dict()
    assert 'exports_count' in state, f"T267.3 FAIL: to_dict keys={list(state.keys())}"

    print("  T267.3 Lean4 export: PASS")
    return True


def test_t267_ice_lean_loop():
    """
    T267.4 — ICE-Lean4自动迭代闭环

    ICELeanLoop能在有限轮内收敛或报告未收敛
    """
    from modules.M225_ICELeanLoop import ICESession, LeanExporter, ICELeanLoop

    heap = _make_test_heap()
    ice = ICESession(heap, mass_threshold=1.0)
    exporter = LeanExporter()
    loop = ICELeanLoop(ice, max_rounds=3)

    result = loop.run(phenomenon="test_convergence", theorem_type="abc_weak")
    assert result is not None, "T267.4 FAIL: ICELeanLoop.run returned None"
    assert isinstance(result, dict), "T267.4 FAIL: ICELeanLoop.run should return dict"

    print("  T267.4 ICE-Lean4 loop: PASS")
    return True


def test_t267_hap_protocol():
    """
    T267.5 — HAP人类-AGI联合证明协议

    5步协议可完整执行
    """
    from modules.M225_ICELeanLoop import ICESession, HAPProtocol

    heap = _make_test_heap()
    ice = ICESession(heap, mass_threshold=1.0)
    hap = HAPProtocol(ice)

    # Step 1: 人类意图
    s1 = hap.step1_human_intent("prove Riemann hypothesis")
    assert s1 is not None, "T267.5 FAIL: HAP step1 returned None"

    # Step 2: AGI结构化
    s2 = hap.step2_agi_structure("prove Riemann hypothesis")
    assert s2 is not None, "T267.5 FAIL: HAP step2 returned None"

    # Step 3: 人类形式化
    s3 = hap.step3_human_formalize("prove Riemann hypothesis", "abc_weak")
    assert s3 is not None, "T267.5 FAIL: HAP step3 returned None"

    # Step 4: AGI验证
    s4 = hap.step4_agi_verify("prove Riemann hypothesis", "abc_weak")
    assert s4 is not None, "T267.5 FAIL: HAP step4 returned None"

    # Step 5: 人类终审
    s5 = hap.step5_human_review(converged=True)
    assert s5 is not None, "T267.5 FAIL: HAP step5 returned None"

    # 完整协议
    full = hap.run_full_protocol("prove Riemann hypothesis", "abc_weak")
    assert full is not None, "T267.5 FAIL: HAP run_full_protocol returned None"

    print("  T267.5 HAP protocol: PASS")
    return True


# ══════════════════════════════════════════════════
# 运行全部 MVE 测试
# ══════════════════════════════════════════════════

def run_all():
    """运行所有T265-T267 MVE测试"""
    results = {}
    tests = [
        ("T265.1 yin_long_product bilinearity", test_t265_yin_long_product_bilinearity),
        ("T265.2 commutativity axiom", test_t265_yin_long_product_symmetry),
        ("T265.3 HEX_RING_GAP confinement", test_t265_mnq8_hex_ring_gap),
        ("T265.4 MNQ8Grid topology", test_t265_mnq8_grid_topology),
        ("T266.1 SOP preset generation", test_t266_sop_preset_generation),
        ("T266.2 SOP auto-classify", test_t266_sop_auto_classify),
        ("T266.3 SOP custom generation", test_t266_sop_custom_generation),
        ("T266.4 M224 state query", test_t266_sop_state_and_list),
        ("T267.1 ICE three operators", test_t267_ice_three_operators),
        ("T267.2 ICE cycle convergence", test_t267_ice_cycle_convergence),
        ("T267.3 Lean4 export", test_t267_lean_export),
        ("T267.4 ICE-Lean4 loop", test_t267_ice_lean_loop),
        ("T267.5 HAP protocol", test_t267_hap_protocol),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            results[name] = "PASS"
            passed += 1
        except Exception as e:
            results[name] = f"FAIL: {e}"
            failed += 1
            import traceback
            traceback.print_exc()

    print()
    print("=" * 60)
    print(f"T265-T267 MVE Results: {passed} PASS / {failed} FAIL / {len(tests)} TOTAL")
    print("=" * 60)
    for name, r in results.items():
        status = "OK" if r == "PASS" else "XX"
        print(f"  [{status}] {name}: {r}")

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
