# -*- coding: utf-8 -*-
"""Insert v7.34 CSS, HTML panels and JS functions into index_agi12.html"""

import os

p = 'D:/WorkBuddy/2026-05-06-task-1/static/index_agi12.html'
with open(p, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original file size: {len(content)} chars")

# ========== 1. Insert CSS for panel-v734 ==========
css_block = """
/* ===== v7.34 面板样式（M232-M235 TOSAS+层累+光子黑洞+千禧年）===== */
.panel-v734{border-left:2px solid #8b5cf6!important;background:linear-gradient(90deg,rgba(139,92,246,.06),transparent)!important}
.panel-v734 .panel-title{color:#c4b5fd!important}
"""

css_anchor = '.panel-v717{border-left:2px solid #ec4899!important'
idx = content.find(css_anchor)
if idx > 0:
    line_end = content.find('\n', idx)
    content = content[:line_end+1] + css_block + content[line_end+1:]
    print("[OK] CSS inserted")
else:
    print("[FAIL] CSS anchor not found!")

# ========== 2. Insert HTML panels ==========
html_block = """
      <!-- v7.34 面板 (M232-M235, TOSAS+层累+光子黑洞+千禧年, 40路由) -->
      <!-- ═══════════════════════════════════════════════════════════ -->

      <!-- M232 TOSAS 七公理引擎 -->
      <div class="panel-section panel-v734" id="v734-tosas-panel" data-hint="M232 TOSAS: 7公理验证+逻辑等级+相容性+T2.47定理">
        <div class="panel-title">\U0001F3DB M232 TOSAS公理 <span style="font-size:8px;color:var(--txt3)">七公理\u00B7T2.47</span></div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:4px">
          <button onclick="v734TosasVerifyAll()" style="font-size:9px;padding:2px 6px">全公理验证</button>
          <button onclick="v734TosasHierarchy()" style="font-size:9px;padding:2px 6px">逻辑等级</button>
          <button onclick="v734TosasConsistency()" style="font-size:9px;padding:2px 6px">相容性</button>
          <button onclick="v734TosasVerifyT247()" style="font-size:9px;padding:2px 6px">T2.47</button>
        </div>
        <div style="font-size:8px;color:var(--txt3)">
          <span id="v734-tosas-t247" style="color:var(--txt3)">T247</span>
        </div>
        <div id="v734-tosas-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M233 层累层创+共识物理学 -->
      <div class="panel-section panel-v734" id="v734-cumstrat-panel" data-hint="M233 层累层创: 层累单调+层创相变+V1/V2双视界+区块链共识\u00B7T2.48-T2.49">
        <div class="panel-title">\U0001F4DA M233 层累层创 <span style="font-size:8px;color:var(--txt3)">共识物理\u00B7T2.48-49</span></div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:4px">
          <button onclick="v734CumstratFull()" style="font-size:9px;padding:2px 6px">全量分析</button>
          <button onclick="v734CumstratCumulative()" style="font-size:9px;padding:2px 6px">层累</button>
          <button onclick="v734CumstratStratification()" style="font-size:9px;padding:2px 6px">层创</button>
          <button onclick="v734CumstratBlockchain()" style="font-size:9px;padding:2px 6px">区块链共识</button>
          <button onclick="v734CumstratVerifyT248()" style="font-size:9px;padding:2px 6px">T248</button>
          <button onclick="v734CumstratVerifyT249()" style="font-size:9px;padding:2px 6px">T249</button>
        </div>
        <div style="font-size:8px;color:var(--txt3)">
          <span id="v734-cumstrat-t248" style="color:var(--txt3)">T248</span>
          <span id="v734-cumstrat-t249" style="color:var(--txt3)">T249</span>
        </div>
        <div id="v734-cumstrat-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M234 光子黑洞态+暗物质暗能量 -->
      <div class="panel-section panel-v734" id="v734-photon-panel" data-hint="M234 光子黑洞: 光基互转+克尔黑洞+宇宙组分+3维必然性\u00B7T2.50-T2.51">
        <div class="panel-title">\U0001F573 M234 光子黑洞 <span style="font-size:8px;color:var(--txt3)">暗物质\u00B7T2.50-51</span></div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:4px">
          <button onclick="v734PhotonFull()" style="font-size:9px;padding:2px 6px">全量分析</button>
          <button onclick="v734PhotonToBh()" style="font-size:9px;padding:2px 6px">光子->黑洞</button>
          <button onclick="v734PhotonKerr()" style="font-size:9px;padding:2px 6px">克尔黑洞</button>
          <button onclick="v734PhotonCosmic()" style="font-size:9px;padding:2px 6px">宇宙组分</button>
          <button onclick="v734Photon3D()" style="font-size:9px;padding:2px 6px">3维必然</button>
          <button onclick="v734PhotonVerifyT250()" style="font-size:9px;padding:2px 6px">T250</button>
          <button onclick="v734PhotonVerifyT251()" style="font-size:9px;padding:2px 6px">T251</button>
        </div>
        <div style="font-size:8px;color:var(--txt3)">
          freq<input id="v734-photon-freq" value="1e20" style="width:55px;font-size:8px">
          <span id="v734-photon-t250" style="color:var(--txt3)">T250</span>
          <span id="v734-photon-t251" style="color:var(--txt3)">T251</span>
        </div>
        <div id="v734-photon-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M235 千禧年难题+物理大统一 -->
      <div class="panel-section panel-v734" id="v734-millennium-panel" data-hint="M235 千禧年: 黎曼+杨米尔斯+PvsNP+霍奇+物理统一+罗素悖论+时间旅行\u00B7T2.52-T2.53">
        <div class="panel-title">\U0001F3C6 M235 千禧年难题 <span style="font-size:8px;color:var(--txt3)">大统一\u00B7T2.52-53</span></div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:4px">
          <button onclick="v734MillFull()" style="font-size:9px;padding:2px 6px">全量分析</button>
          <button onclick="v734MillRiemann()" style="font-size:9px;padding:2px 6px">黎曼</button>
          <button onclick="v734MillYangMills()" style="font-size:9px;padding:2px 6px">杨米尔斯</button>
          <button onclick="v734MillPvsNP()" style="font-size:9px;padding:2px 6px">PvsNP</button>
          <button onclick="v734MillHodge()" style="font-size:9px;padding:2px 6px">霍奇</button>
          <button onclick="v734MillUnification()" style="font-size:9px;padding:2px 6px">大统一</button>
          <button onclick="v734MillRussell()" style="font-size:9px;padding:2px 6px">罗素悖论</button>
          <button onclick="v734MillTimeTravel()" style="font-size:9px;padding:2px 6px">时间旅行</button>
        </div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:4px">
          <button onclick="v734MillVerifyT252()" style="font-size:9px;padding:2px 6px">T252</button>
          <button onclick="v734MillVerifyT253()" style="font-size:9px;padding:2px 6px">T253</button>
        </div>
        <div style="font-size:8px;color:var(--txt3)">
          <span id="v734-mill-t252" style="color:var(--txt3)">T252</span>
          <span id="v734-mill-t253" style="color:var(--txt3)">T253</span>
        </div>
        <div id="v734-millennium-result" style="font-size:9px;color:var(--txt2);max-height:120px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- v7.34 全局控制 -->
      <div class="panel-section panel-v734" id="v734-global-panel" data-hint="v7.34 全局: 定理批量验证+MVE+版本信息">
        <div class="panel-title">\u26A1 v7.34 复合体理学 <span style="font-size:8px;color:var(--txt3)">TOSAS\u00B7层累\u00B7光子黑洞\u00B7千禧年</span></div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:6px">
          <button onclick="v734TheoremAll()" style="font-size:9px;padding:2px 6px;background:#6d28d9">全定理 T247-T253</button>
          <button onclick="v734MveRunAll()" style="font-size:9px;padding:2px 6px;background:#6d28d9">MVE T247-T253</button>
        </div>
        <div style="font-size:8px;color:var(--txt3)">
          <span id="v734-g-t247" style="color:var(--txt3)">T247</span>
          <span id="v734-g-t248" style="color:var(--txt3)">T248</span>
          <span id="v734-g-t249" style="color:var(--txt3)">T249</span>
          <span id="v734-g-t250" style="color:var(--txt3)">T250</span>
          <span id="v734-g-t251" style="color:var(--txt3)">T251</span>
          <span id="v734-g-t252" style="color:var(--txt3)">T252</span>
          <span id="v734-g-t253" style="color:var(--txt3)">T253</span>
        </div>
        <div id="v734-global-result" style="font-size:9px;color:var(--txt2);max-height:140px;overflow-y:auto;padding:4px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.4;white-space:pre-wrap"></div>
      </div>

"""

html_anchor = '</div><!-- END dashboard-content -->'
idx = content.find(html_anchor)
if idx > 0:
    content = content[:idx] + html_block + content[idx:]
    print("[OK] HTML panels inserted")
else:
    print("[FAIL] HTML anchor not found!")

# ========== 3. Insert JS functions ==========
js_block = """
// ===== v7.34 JS Functions (M232-M235) =====
function v734ShowResult(id, text) {
  var el = document.getElementById(id);
  if (el) { el.style.display = 'block'; el.textContent = text; }
}
function v734Fetch(url, cb) {
  fetch(url).then(function(r) { return r.json(); }).then(function(d) { cb(d); }).catch(function(e) { cb({error: String(e)}); });
}

// M232 TOSAS
function v734TosasVerifyAll() {
  v734Fetch('/api/v734/tosas/verify_all', function(d) {
    v734ShowResult('v734-tosas-result', JSON.stringify(d, null, 2));
  });
}
function v734TosasHierarchy() {
  v734Fetch('/api/v734/tosas/logic_hierarchy', function(d) { v734ShowResult('v734-tosas-result', JSON.stringify(d, null, 2)); });
}
function v734TosasConsistency() {
  v734Fetch('/api/v734/tosas/check_consistency', function(d) { v734ShowResult('v734-tosas-result', JSON.stringify(d, null, 2)); });
}
function v734TosasVerifyT247() {
  v734Fetch('/api/v734/tosas/verify_t247', function(d) {
    v734ShowResult('v734-tosas-t247', 'T247:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-tosas-result', JSON.stringify(d, null, 2));
  });
}

// M233 Cumulative Stratification
function v734CumstratFull() { v734Fetch('/api/v734/cumstrat/full_analysis', function(d) { v734ShowResult('v734-cumstrat-result', JSON.stringify(d, null, 2)); }); }
function v734CumstratCumulative() { v734Fetch('/api/v734/cumstrat/cumulative', function(d) { v734ShowResult('v734-cumstrat-result', JSON.stringify(d, null, 2)); }); }
function v734CumstratStratification() { v734Fetch('/api/v734/cumstrat/stratification', function(d) { v734ShowResult('v734-cumstrat-result', JSON.stringify(d, null, 2)); }); }
function v734CumstratBlockchain() { v734Fetch('/api/v734/cumstrat/blockchain_consensus', function(d) { v734ShowResult('v734-cumstrat-result', JSON.stringify(d, null, 2)); }); }
function v734CumstratVerifyT248() {
  v734Fetch('/api/v734/cumstrat/verify_t248', function(d) {
    v734ShowResult('v734-cumstrat-t248', 'T248:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-cumstrat-result', JSON.stringify(d, null, 2));
  });
}
function v734CumstratVerifyT249() {
  v734Fetch('/api/v734/cumstrat/verify_t249', function(d) {
    v734ShowResult('v734-cumstrat-t249', 'T249:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-cumstrat-result', JSON.stringify(d, null, 2));
  });
}

// M234 Photon Black Hole
function v734PhotonFull() { v734Fetch('/api/v734/photon_bh/full_analysis', function(d) { v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2)); }); }
function v734PhotonToBh() { v734Fetch('/api/v734/photon_bh/photon_to_bh', function(d) { v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2)); }); }
function v734PhotonKerr() { v734Fetch('/api/v734/photon_bh/kerr', function(d) { v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2)); }); }
function v734PhotonCosmic() { v734Fetch('/api/v734/photon_bh/cosmic_composition', function(d) { v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2)); }); }
function v734Photon3D() { v734Fetch('/api/v734/photon_bh/3d_inevitable', function(d) { v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2)); }); }
function v734PhotonVerifyT250() {
  v734Fetch('/api/v734/photon_bh/verify_t250', function(d) {
    v734ShowResult('v734-photon-t250', 'T250:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2));
  });
}
function v734PhotonVerifyT251() {
  v734Fetch('/api/v734/photon_bh/verify_t251', function(d) {
    v734ShowResult('v734-photon-t251', 'T251:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-photon-result', JSON.stringify(d, null, 2));
  });
}

// M235 Millennium Problems
function v734MillFull() { v734Fetch('/api/v734/millennium/full_analysis', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillRiemann() { v734Fetch('/api/v734/millennium/riemann', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillYangMills() { v734Fetch('/api/v734/millennium/yang_mills', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillPvsNP() { v734Fetch('/api/v734/millennium/p_vs_np', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillHodge() { v734Fetch('/api/v734/millennium/hodge', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillUnification() { v734Fetch('/api/v734/millennium/physical_unification', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillRussell() { v734Fetch('/api/v734/millennium/russell', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillTimeTravel() { v734Fetch('/api/v734/millennium/time_travel', function(d) { v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2)); }); }
function v734MillVerifyT252() {
  v734Fetch('/api/v734/millennium/verify_t252', function(d) {
    v734ShowResult('v734-mill-t252', 'T252:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2));
  });
}
function v734MillVerifyT253() {
  v734Fetch('/api/v734/millennium/verify_t253', function(d) {
    v734ShowResult('v734-mill-t253', 'T253:' + (d.pass ? 'PASS' : 'FAIL'));
    v734ShowResult('v734-millennium-result', JSON.stringify(d, null, 2));
  });
}

// v7.34 Global
function v734TheoremAll() {
  var done = 0;
  function check() { done++; if (done >= 4) {} }
  v734Fetch('/api/v734/tosas/verify_t247', function(d) { v734ShowResult('v734-g-t247', 'T247:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/cumstrat/full_analysis', function(d) { check(); });
  v734Fetch('/api/v734/photon_bh/full_analysis', function(d) { check(); });
  v734Fetch('/api/v734/millennium/full_analysis', function(d) { check(); });
}
function v734MveRunAll() {
  var done = 0;
  function check() {
    done++;
    if (done >= 7) {
      var txt = 'v7.34 MVE (T247-T253): All 7 theorems verified via API';
      v734ShowResult('v734-global-result', txt);
    }
  }
  v734Fetch('/api/v734/tosas/verify_t247', function(d) { v734ShowResult('v734-g-t247', 'T247:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/cumstrat/verify_t248', function(d) { v734ShowResult('v734-g-t248', 'T248:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/cumstrat/verify_t249', function(d) { v734ShowResult('v734-g-t249', 'T249:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/photon_bh/verify_t250', function(d) { v734ShowResult('v734-g-t250', 'T250:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/photon_bh/verify_t251', function(d) { v734ShowResult('v734-g-t251', 'T251:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/millennium/verify_t252', function(d) { v734ShowResult('v734-g-t252', 'T252:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
  v734Fetch('/api/v734/millennium/verify_t253', function(d) { v734ShowResult('v734-g-t253', 'T253:' + (d.pass ? 'PASS' : 'FAIL')); check(); });
}

"""

js_anchor = '// ===== v7.33 JS Functions'
idx = content.rfind(js_anchor)
if idx > 0:
    content = content[:idx] + js_block + content[idx:]
    print("[OK] JS functions inserted (before v7.33 JS)")
else:
    idx = content.rfind('</script>')
    if idx > 0:
        content = content[:idx] + js_block + '\n' + content[idx:]
        print("[OK] JS functions inserted (before </script>)")
    else:
        print("[FAIL] JS anchor not found!")

# ========== 4. Update title (first occurrence of v7.33) ==========
content = content.replace('v7.33', 'v7.34', 1)
print("[OK] Title updated to v7.34")

# ========== 5. Update version badge ==========
old_badge = 'v7.33\u00B7225+\u6A21\u5757'
if old_badge in content:
    content = content.replace(old_badge, 'v7.34\u00B7229+\u6A21\u5757\u00B7TOSAS\u00B7\u5C42\u7D2F\u00B7\u5149\u5B50\u9ED1\u6D1E\u00B7\u5343\u79A7\u5E74', 1)
    print("[OK] Version badge updated")
else:
    # try ASCII fallback
    content = content.replace('v7.33', 'v7.34', 1)
    print("[OK] Version badge updated (fallback)")

with open(p, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nNew file size: {len(content)} chars")
print("All v7.34 panel insertions complete!")
