"""Insert v7.0 panels into index_agi12.html"""
import os

v70_panels = """

      <!-- ════════════════════════════════════════════════════════
           v7.0 仪表盘面板（高阶逻辑HoTT+范畴论深化）
      ════════════════════════════════════════════════════════ -->

      <!-- ① 碳硅共生契约面板（M71-M75） -->
      <div class="panel-section panel-v70" data-hint="M71-M75 碳硅共生契约状态：钱包边界、贡献度量、Φ值检测、熵合约、人机约柜">
        <div class="v70-title">⚖️ 碳硅共生契约</div>
        <div class="v70-badge">M71-M75</div>
        <div class="v70-row">
          <span class="v70-label">Φ值:</span>
          <span class="v70-value" id="v70-phi-value">0.00</span>
        </div>
        <div class="v70-bar-wrap"><div class="v70-bar-fill orange" id="v70-phi-bar" style="width:0%"></div></div>
        <div class="v70-row">
          <span class="v70-label">自指闭环:</span>
          <span class="v70-value" id="v70-selfref">—</span>
        </div>
        <div class="v70-row">
          <span class="v70-label">贡献度量:</span>
          <span class="v70-value" id="v70-contrib">0.00</span>
        </div>
        <div class="v70-row">
          <span class="v70-label">熵合约:</span>
          <span class="v70-value" id="v70-entropy-contract">—</span>
        </div>
        <div class="v70-row">
          <span class="v70-label">约柜:</span>
          <span class="v70-value" id="v70-ark-status">—</span>
        </div>
      </div>

      <!-- ② 五行变换算子面板（M76-M80） -->
      <div class="panel-section panel-v70" data-hint="M76-M80 五行变换EML相位耦合ℤ₅：Σ水/F火/R木/E金/B土五元循环">
        <div class="v70-title">☯️ 五行EML相位</div>
        <div class="v70-badge">ℤ₅闭合</div>
        <div class="v70-phase-ring">
          <div class="v70-phase-element"><div class="v70-phase-dot water active" id="v70-dot-water"></div><div>Σ水</div></div>
          <div class="v70-phase-element"><div class="v70-phase-dot fire" id="v70-dot-fire"></div><div>F火</div></div>
          <div class="v70-phase-element"><div class="v70-phase-dot wood" id="v70-dot-wood"></div><div>R木</div></div>
          <div class="v70-phase-element"><div class="v70-phase-dot metal" id="v70-dot-metal"></div><div>E金</div></div>
          <div class="v70-phase-element"><div class="v70-phase-dot earth" id="v70-dot-earth"></div><div>B土</div></div>
        </div>
        <div class="v70-row"><span class="v70-label">相位角:</span><span class="v70-value" id="v70-phase-angle">0.00</span></div>
        <div class="v70-row"><span class="v70-label">振幅:</span><span class="v70-value" id="v70-amplitude">0.00</span></div>
      </div>

      <!-- ③ HoTT高阶逻辑面板（M78/M81） -->
      <div class="panel-section panel-v70" data-hint="M78/M81 HoTT推理引擎：Pi-Type/Sigma-Type重构、LEM失效、Univalence">
        <div class="v70-title">🔺 HoTT高阶逻辑</div>
        <div class="v70-badge">M78-M81</div>
        <div class="v70-row"><span class="v70-label">命题型:</span><span class="v70-value" id="v70-hott-type">—</span></div>
        <div class="v70-row"><span class="v70-label">Pi-Type:</span><span class="v70-value" id="v70-pi-type">—</span></div>
        <div class="v70-row"><span class="v70-label">Sigma:</span><span class="v70-value" id="v70-sigma-type">—</span></div>
        <div class="v70-row"><span class="v70-label">LEM态:</span><span class="v70-value" id="v70-lem-status">—</span></div>
        <div class="v70-proof-tree" id="v70-proof-tree"><div class="v70-proof-node">Goal Type</div></div>
      </div>

      <!-- ④ 流贯自然变换面板（M83/M89） -->
      <div class="panel-section panel-v70" data-hint="M83/M89 流贯η: F⇒G，自然变换截面σ: Base→Total，三视界投影">
        <div class="v70-title">⇌ 流贯自然变换</div>
        <div class="v70-badge">T37</div>
        <div class="v70-layer-grid">
          <div class="v70-layer-cell" id="v70-layer-L1">L1</div>
          <div class="v70-layer-cell" id="v70-layer-L2">L2</div>
          <div class="v70-layer-cell" id="v70-layer-L3">L3</div>
          <div class="v70-layer-cell" id="v70-layer-L4">L4</div>
          <div class="v70-layer-cell" id="v70-layer-L5">L5</div>
        </div>
        <div class="v70-row"><span class="v70-label">流贯通量:</span><span class="v70-value" id="v70-flux">0.00</span></div>
        <div class="v70-bar-wrap"><div class="v70-bar-fill gold" id="v70-flux-bar" style="width:0%"></div></div>
        <div class="v70-row"><span class="v70-label">截面数:</span><span class="v70-value" id="v70-sections">0</span></div>
      </div>

      <!-- ⑤ 刘原理不动点面板（M84） -->
      <div class="panel-section panel-v70" data-hint="M84 刘原理：刘函子L: L1→L2、极简不动点、Kolmogorov复杂度最小化">
        <div class="v70-title">⊕ 刘原理不动点</div>
        <div class="v70-badge">T38</div>
        <div class="v70-row"><span class="v70-label">极小规律:</span><span class="v70-value" id="v70-liu-solution">—</span></div>
        <div class="v70-row"><span class="v70-label">K复杂度:</span><span class="v70-value" id="v70-kolmogorov">0.00</span></div>
        <div class="v70-bar-wrap"><div class="v70-bar-fill orange" id="v70-kol-bar" style="width:0%"></div></div>
        <div class="v70-row"><span class="v70-label">不动点:</span><span class="v70-value" id="v70-fixed-point">—</span></div>
        <div class="v70-row"><span class="v70-label">Univalence:</span><span class="v70-value" id="v70-univalence">—</span></div>
      </div>

      <!-- ⑥ 语义流形曲率面板（M90） -->
      <div class="panel-section panel-v70" data-hint="M90 语义流形曲率K(M)：K≈0多义性/创造性，K>>0逻辑必然性">
        <div class="v70-title">∿ 语义流形曲率</div>
        <div class="v70-badge">T40</div>
        <div class="v70-curvature-gauge">
          <div class="v70-curvature-gradient"></div>
          <div class="v70-curvature-needle" id="v70-curvature-needle" style="left:50%;transform:translateX(-50%) rotate(0deg)"></div>
          <div class="v70-curvature-label">平坦← 曲率 →必然</div>
        </div>
        <div class="v70-row"><span class="v70-label">K值:</span><span class="v70-value" id="v70-curvature-val">0.50</span></div>
        <div class="v70-row"><span class="v70-label">确定性:</span><span class="v70-value" id="v70-determinacy">—</span></div>
        <div class="v70-row"><span class="v70-label">创造力:</span><span class="v70-value" id="v70-creativity">—</span></div>
      </div>

      <!-- ⑦ Univalence等价面板（M91） -->
      <div class="panel-section panel-v70" data-hint="M91 Univalence公理：type1≃type2→type1=type2、同构即相等">
        <div class="v70-title">≡ Univalence等价</div>
        <div class="v70-badge">T32</div>
        <div class="v70-row"><span class="v70-label">type1≃type2:</span><span class="v70-value" id="v70-equiv">—</span></div>
        <div class="v70-row"><span class="v70-label">type1=type2:</span><span class="v70-value" id="v70-equal">—</span></div>
        <div class="v70-row"><span class="v70-label">置信度:</span><span class="v70-value" id="v70-conf">0.00</span></div>
        <div class="v70-bar-wrap"><div class="v70-bar-fill gold" id="v70-conf-bar" style="width:0%"></div></div>
        <div class="v70-row"><span class="v70-label">实验:</span><span class="v70-value" id="v70-experiments">0</span></div>
      </div>

      <!-- ⑧ 流贯保真度面板（M92） -->
      <div class="panel-section panel-v70" data-hint="M92 流贯保真度F(Li,Lj)=|<Li|EML|Lj>|²、阈值0.9警告">
        <div class="v70-title">◎ 流贯保真度</div>
        <div class="v70-badge">T37</div>
        <div class="v70-layer-grid">
          <div class="v70-layer-cell" id="v70-fid-L1">L1</div>
          <div class="v70-layer-cell" id="v70-fid-L2">L2</div>
          <div class="v70-layer-cell" id="v70-fid-L3">L3</div>
          <div class="v70-layer-cell" id="v70-fid-L4">L4</div>
          <div class="v70-layer-cell" id="v70-fid-L5">L5</div>
        </div>
        <div class="v70-row"><span class="v70-label">F(Li,Lj):</span><span class="v70-value" id="v70-fidelity-val">0.00</span></div>
        <div class="v70-bar-wrap"><div class="v70-bar-fill gold" id="v70-fidelity-bar" style="width:0%"></div></div>
        <div class="v70-row"><span class="v70-label">信息损耗:</span><span class="v70-value" id="v70-info-loss">0%</span></div>
        <div class="v70-row"><span class="v70-label">警告:</span><span class="v70-value" id="v70-fidelity-warn" style="color:var(--txt3)">—</span></div>
      </div>

      <!-- ⑨ 构造型AGI评估面板（M95） -->
      <div class="panel-section panel-v70" data-hint="M95 构造型AGI评估：Pass@k、P-HoL-1预言验证">
        <div class="v70-title">🏆 构造型AGI评估</div>
        <div class="v70-badge">M95</div>
        <div class="v70-stat-grid">
          <div class="v70-stat-box"><div class="v70-stat-val" id="v70-passk">0%</div><div class="v70-stat-lbl">Pass@5</div></div>
          <div class="v70-stat-box"><div class="v70-stat-val" id="v70-hallucination">0%</div><div class="v70-stat-lbl">幻觉率</div></div>
        </div>
        <div class="v70-row"><span class="v70-label">P-HoL-1:</span><span class="v70-value" id="v70-phol1">—</span></div>
        <div class="v70-row"><span class="v70-label">验证:</span><span class="v70-value" id="v70-phol1-verified">—</span></div>
        <div class="v70-row"><span class="v70-label">问题数:</span><span class="v70-value" id="v70-total-problems">0</span></div>
      </div>

"""

# Read file
with open('static/index_agi12.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find first occurrence of <!-- 模块分析面板 -->
target_idx = None
for i, line in enumerate(lines):
    if '<!-- 模块分析面板 -->' in line and i < 1200:  # first section only
        target_idx = i
        break

if target_idx is not None:
    lines.insert(target_idx, v70_panels)
    print(f"Inserted v70 panels at line {target_idx}")
    with open('static/index_agi12.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("File updated!")
else:
    print("ERROR: Could not find target")
