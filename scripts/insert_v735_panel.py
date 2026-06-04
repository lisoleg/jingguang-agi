#!/usr/bin/env python3
"""Insert v7.35 panels into index_agi12.html"""
import re

HTML_FILE = "D:/WorkBuddy/2026-05-06-task-1/static/index_agi12.html"

with open(HTML_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. CSS insertion (after .panel-v734 .panel-title)
CSS_V735 = """
.panel-v735{border-left:2px solid #06b6d4!important;background:linear-gradient(90deg,rgba(6,182,212,.06),transparent)!important}
.panel-v735 .panel-title{color:#67e8f9!important}
"""

css_anchor = ".panel-v734 .panel-title{color:#c4b5fd!important}"
content = content.replace(css_anchor, css_anchor + "\n" + CSS_V735, 1)

# 2. HTML panels insertion (before </div><!-- END dashboard-content -->)
HTML_V735 = """
      <!-- ========== v7.35 Panels (M236-M243) ========== -->
      <div class="panel-section panel-v735" id="v735-mincomp-panel" data-hint="M236 极简计算主义: 组织不变量+F-ISA指令集+弱意识必要性·T2.54-T2.55">
        <div class="panel-title">M236 极简计算主义</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735MinCompState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735MinCompInvariant()" style="font-size:9px;padding:2px 6px">不变量</button>
          <button onclick="v735MinCompISA()" style="font-size:9px;padding:2px 6px">ISA</button>
          <button onclick="v735MinCompT254()" style="font-size:9px;padding:2px 6px">T254</button>
          <button onclick="v735MinCompT255()" style="font-size:9px;padding:2px 6px">T255</button>
          <span id="v735-mincomp-t254" style="color:var(--txt3)">T254</span>
          <span id="v735-mincomp-t255" style="color:var(--txt3)">T255</span>
        </div>
        <div id="v735-mincomp-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-prime-panel" data-hint="M237 素基编码: 分布式素数筛选+临界阻尼+素基最优编码·T2.56-T2.57">
        <div class="panel-title">M237 素基编码</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735PrimeState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735PrimeEncode()" style="font-size:9px;padding:2px 6px">编码</button>
          <button onclick="v735PrimeSieve()" style="font-size:9px;padding:2px 6px">筛选</button>
          <button onclick="v735PrimeT256()" style="font-size:9px;padding:2px 6px">T256</button>
          <button onclick="v735PrimeT257()" style="font-size:9px;padding:2px 6px">T257</button>
          <span id="v735-prime-t256" style="color:var(--txt3)">T256</span>
          <span id="v735-prime-t257" style="color:var(--txt3)">T257</span>
        </div>
        <div id="v735-prime-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-topospec-panel" data-hint="M238 拓扑-谱动力学: 傅里叶对偶+谱模态+Hodge分解·T2.58-T2.59">
        <div class="panel-title">M238 拓扑-谱动力学</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735TopoSpecState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735TopoSpecHodge()" style="font-size:9px;padding:2px 6px">Hodge</button>
          <button onclick="v735TopoSpecFourier()" style="font-size:9px;padding:2px 6px">傅里叶</button>
          <button onclick="v735TopoSpecT258()" style="font-size:9px;padding:2px 6px">T258</button>
          <button onclick="v735TopoSpecT259()" style="font-size:9px;padding:2px 6px">T259</button>
          <span id="v735-topospec-t258" style="color:var(--txt3)">T258</span>
          <span id="v735-topospec-t259" style="color:var(--txt3)">T259</span>
        </div>
        <div id="v735-topospec-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-lightcomp-panel" data-hint="M239 光基计算: 虹光身+5D存储+脏腑频率+光子黑洞·T2.60-T2.62">
        <div class="panel-title">M239 光基计算</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735LightState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735LightCompute()" style="font-size:9px;padding:2px 6px">光计算</button>
          <button onclick="v735LightRainbow()" style="font-size:9px;padding:2px 6px">虹光身</button>
          <button onclick="v735Light5D()" style="font-size:9px;padding:2px 6px">5D存储</button>
          <button onclick="v735LightT260()" style="font-size:9px;padding:2px 6px">T260</button>
          <span id="v735-light-t260" style="color:var(--txt3)">T260</span>
        </div>
        <div id="v735-lightcomp-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-invetopo-panel" data-hint="M240 逆向拓扑: 心流+内丹+密宗+元气神机·T2.63-T2.65">
        <div class="panel-title">M240 逆向拓扑</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735InvTopoState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735InvTopoFlow()" style="font-size:9px;padding:2px 6px">心流</button>
          <button onclick="v735InvTopoNeidan()" style="font-size:9px;padding:2px 6px">内丹</button>
          <button onclick="v735InvTopoT263()" style="font-size:9px;padding:2px 6px">T263</button>
          <span id="v735-invetopo-t263" style="color:var(--txt3)">T263</span>
        </div>
        <div id="v735-invetopo-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-ftelconf-panel" data-hint="M241 流贯囚禁: 跳频抗干扰+MIMO波束成形+U/R过程+意识越狱·T2.66-T2.68">
        <div class="panel-title">M241 流贯囚禁</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735FtelConfState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735FtelHop()" style="font-size:9px;padding:2px 6px">跳频</button>
          <button onclick="v735FtelMIMO()" style="font-size:9px;padding:2px 6px">MIMO</button>
          <button onclick="v735FtelPrisonBreak()" style="font-size:9px;padding:2px 6px">越狱</button>
          <button onclick="v735FtelT266()" style="font-size:9px;padding:2px 6px">T266</button>
          <span id="v735-ftelconf-t266" style="color:var(--txt3)">T266</span>
        </div>
        <div id="v735-ftelconf-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-mnqwave-panel" data-hint="M242 MNQ信息波包场: 能量波相干+玻尔兹曼分布+金灵球网络·T2.69-T2.70">
        <div class="panel-title">M242 MNQ波相干</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735MNQState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735MNQCoherence()" style="font-size:9px;padding:2px 6px">相干</button>
          <button onclick="v735MNQGoldenBall()" style="font-size:9px;padding:2px 6px">金灵球</button>
          <button onclick="v735MNQT269()" style="font-size:9px;padding:2px 6px">T269</button>
          <span id="v735-mnqwave-t269" style="color:var(--txt3)">T269</span>
        </div>
        <div id="v735-mnqwave-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <div class="panel-section panel-v735" id="v735-rgt-panel" data-hint="M243 Kumo RGT桥接: 关系图变换器+PluRel幂律+度分布预测·T2.71-T2.72">
        <div class="panel-title">M243 RGT桥接</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735RGTState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v735RGTTransform()" style="font-size:9px;padding:2px 6px">变换</button>
          <button onclick="v735RGTPluRel()" style="font-size:9px;padding:2px 6px">PluRel</button>
          <button onclick="v735RGTT271()" style="font-size:9px;padding:2px 6px">T271</button>
          <span id="v735-rgt-t271" style="color:var(--txt3)">T271</span>
        </div>
        <div id="v735-rgt-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- v7.35 Global -->
      <div class="panel-section panel-v735" id="v735-global-panel" data-hint="v7.35 全局: M236-M243 定理验证+MVE">
        <div class="panel-title">v7.35 Global (M236-M243)</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v735TheoremAll()" style="font-size:9px;padding:2px 6px;background:#0891b2">全定理 T254-T272</button>
          <button onclick="v735MveRunAll()" style="font-size:9px;padding:2px 6px;background:#0891b2">MVE T254-T272</button>
        </div>
        <div style="font-size:8px;color:var(--txt3)">
          <span id="v735-g-t254" style="color:var(--txt3)">T254</span>
          <span id="v735-g-t255" style="color:var(--txt3)">T255</span>
          <span id="v735-g-t256" style="color:var(--txt3)">T256</span>
          <span id="v735-g-t257" style="color:var(--txt3)">T257</span>
          <span id="v735-g-t258" style="color:var(--txt3)">T258</span>
          <span id="v735-g-t259" style="color:var(--txt3)">T259</span>
          <span id="v735-g-t260" style="color:var(--txt3)">T260</span>
          <span id="v735-g-t261" style="color:var(--txt3)">T261</span>
          <span id="v735-g-t262" style="color:var(--txt3)">T262</span>
          <span id="v735-g-t263" style="color:var(--txt3)">T263</span>
          <span id="v735-g-t264" style="color:var(--txt3)">T264</span>
          <span id="v735-g-t265" style="color:var(--txt3)">T265</span>
          <span id="v735-g-t266" style="color:var(--txt3)">T266</span>
          <span id="v735-g-t267" style="color:var(--txt3)">T267</span>
          <span id="v735-g-t268" style="color:var(--txt3)">T268</span>
          <span id="v735-g-t269" style="color:var(--txt3)">T269</span>
          <span id="v735-g-t270" style="color:var(--txt3)">T270</span>
          <span id="v735-g-t271" style="color:var(--txt3)">T271</span>
          <span id="v735-g-t272" style="color:var(--txt3)">T272</span>
        </div>
        <div id="v735-global-result" style="font-size:9px;color:var(--txt2);max-height:140px;overflow-y:auto;padding:4px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.4;white-space:pre-wrap"></div>
      </div>

"""

html_anchor = '</div><!-- END dashboard-content -->'
content = content.replace(html_anchor, HTML_V735 + "\n" + html_anchor, 1)

# 3. JS insertion (after v734Fetch function)
JS_V735 = """
// ========== v7.35 Functions ==========
function v735Fetch(url, cb) {
  fetch(url).then(function(r) { return r.json(); }).then(function(d) { cb(d); }).catch(function(e) { cb({error: String(e)}); });
}
function v735ShowResult(id, txt) { var el = document.getElementById(id); if (el) { el.style.display = 'block'; el.textContent = typeof txt === 'object' ? JSON.stringify(txt, null, 2) : txt; } }

// M236 MinimalComputationalism
function v735MinCompState() { v735Fetch('/api/v735/minimal_computationalism/state', function(d) { v735ShowResult('v735-mincomp-result', d); }); }
function v735MinCompInvariant() { v735Fetch('/api/v735/minimal_computationalism/organizational_invariant', function(d) { v735ShowResult('v735-mincomp-result', d); }); }
function v735MinCompISA() { v735Fetch('/api/v735/minimal_computationalism/fisa_instruction', function(d) { v735ShowResult('v735-mincomp-result', d); }); }
function v735MinCompT254() { v735Fetch('/api/v735/minimal_computationalism/verify_t254', function(d) { v735ShowResult('v735-mincomp-result', d); var s = document.getElementById('v735-mincomp-t254'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }
function v735MinCompT255() { v735Fetch('/api/v735/minimal_computationalism/verify_t255', function(d) { v735ShowResult('v735-mincomp-result', d); var s = document.getElementById('v735-mincomp-t255'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M237 PrimeBasisCodec
function v735PrimeState() { v735Fetch('/api/v735/prime_basis_codec/state', function(d) { v735ShowResult('v735-prime-result', d); }); }
function v735PrimeEncode() { v735Fetch('/api/v735/prime_basis_codec/encode', function(d) { v735ShowResult('v735-prime-result', d); }); }
function v735PrimeSieve() { v735Fetch('/api/v735/prime_basis_codec/distributed_sieve', function(d) { v735ShowResult('v735-prime-result', d); }); }
function v735PrimeT256() { v735Fetch('/api/v735/prime_basis_codec/verify_t256', function(d) { v735ShowResult('v735-prime-result', d); var s = document.getElementById('v735-prime-t256'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }
function v735PrimeT257() { v735Fetch('/api/v735/prime_basis_codec/verify_t257', function(d) { v735ShowResult('v735-prime-result', d); var s = document.getElementById('v735-prime-t257'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M238 TopoSpectralDynamics
function v735TopoSpecState() { v735Fetch('/api/v735/topo_spectral_dynamics/state', function(d) { v735ShowResult('v735-topospec-result', d); }); }
function v735TopoSpecHodge() { v735Fetch('/api/v735/topo_spectral_dynamics/hodge_decomposition', function(d) { v735ShowResult('v735-topospec-result', d); }); }
function v735TopoSpecFourier() { v735Fetch('/api/v735/topo_spectral_dynamics/fourier_dual', function(d) { v735ShowResult('v735-topospec-result', d); }); }
function v735TopoSpecT258() { v735Fetch('/api/v735/topo_spectral_dynamics/verify_t258', function(d) { v735ShowResult('v735-topospec-result', d); var s = document.getElementById('v735-topospec-t258'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }
function v735TopoSpecT259() { v735Fetch('/api/v735/topo_spectral_dynamics/verify_t259', function(d) { v735ShowResult('v735-topospec-result', d); var s = document.getElementById('v735-topospec-t259'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M239 LightBasedCompute
function v735LightState() { v735Fetch('/api/v735/light_based_compute/state', function(d) { v735ShowResult('v735-lightcomp-result', d); }); }
function v735LightCompute() { v735Fetch('/api/v735/light_based_compute/compute', function(d) { v735ShowResult('v735-lightcomp-result', d); }); }
function v735LightRainbow() { v735Fetch('/api/v735/light_based_compute/rainbow_body', function(d) { v735ShowResult('v735-lightcomp-result', d); }); }
function v735Light5D() { v735Fetch('/api/v735/light_based_compute/storage_5d', function(d) { v735ShowResult('v735-lightcomp-result', d); }); }
function v735LightT260() { v735Fetch('/api/v735/light_based_compute/verify_t260', function(d) { v735ShowResult('v735-lightcomp-result', d); var s = document.getElementById('v735-light-t260'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M240 InverseTopology
function v735InvTopoState() { v735Fetch('/api/v735/inverse_topology/state', function(d) { v735ShowResult('v735-invetopo-result', d); }); }
function v735InvTopoFlow() { v735Fetch('/api/v735/inverse_topology/flow_ftel', function(d) { v735ShowResult('v735-invetopo-result', d); }); }
function v735InvTopoNeidan() { v735Fetch('/api/v735/inverse_topology/neidan', function(d) { v735ShowResult('v735-invetopo-result', d); }); }
function v735InvTopoT263() { v735Fetch('/api/v735/inverse_topology/verify_t263', function(d) { v735ShowResult('v735-invetopo-result', d); var s = document.getElementById('v735-invetopo-t263'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M241 FtelConfinement
function v735FtelConfState() { v735Fetch('/api/v735/ftel_confinement/state', function(d) { v735ShowResult('v735-ftelconf-result', d); }); }
function v735FtelHop() { v735Fetch('/api/v735/ftel_confinement/frequency_hopping', function(d) { v735ShowResult('v735-ftelconf-result', d); }); }
function v735FtelMIMO() { v735Fetch('/api/v735/ftel_confinement/mimo_beamforming', function(d) { v735ShowResult('v735-ftelconf-result', d); }); }
function v735FtelPrisonBreak() { v735Fetch('/api/v735/ftel_confinement/consciousness_prison_break', function(d) { v735ShowResult('v735-ftelconf-result', d); }); }
function v735FtelT266() { v735Fetch('/api/v735/ftel_confinement/verify_t266', function(d) { v735ShowResult('v735-ftelconf-result', d); var s = document.getElementById('v735-ftelconf-t266'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M242 MNQWaveCoherence
function v735MNQState() { v735Fetch('/api/v735/mnq_wave_coherence/state', function(d) { v735ShowResult('v735-mnqwave-result', d); }); }
function v735MNQCoherence() { v735Fetch('/api/v735/mnq_wave_coherence/coherence', function(d) { v735ShowResult('v735-mnqwave-result', d); }); }
function v735MNQGoldenBall() { v735Fetch('/api/v735/mnq_wave_coherence/golden_ball_network', function(d) { v735ShowResult('v735-mnqwave-result', d); }); }
function v735MNQT269() { v735Fetch('/api/v735/mnq_wave_coherence/verify_t269', function(d) { v735ShowResult('v735-mnqwave-result', d); var s = document.getElementById('v735-mnqwave-t269'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// M243 RGT Bridge
function v735RGTState() { v735Fetch('/api/v735/rgt_bridge/state', function(d) { v735ShowResult('v735-rgt-result', d); }); }
function v735RGTTransform() { v735Fetch('/api/v735/rgt_bridge/transform', function(d) { v735ShowResult('v735-rgt-result', d); }); }
function v735RGTPluRel() { v735Fetch('/api/v735/rgt_bridge/plurel_powerlaw', function(d) { v735ShowResult('v735-rgt-result', d); }); }
function v735RGTT271() { v735Fetch('/api/v735/rgt_bridge/verify_t271', function(d) { v735ShowResult('v735-rgt-result', d); var s = document.getElementById('v735-rgt-t271'); if (s) s.style.color = d.proved ? '#34d399' : '#f87171'; }); }

// v7.35 Global
function v735TheoremAll() {
  var endpoints = [
    '/api/v735/minimal_computationalism/verify_t254', '/api/v735/minimal_computationalism/verify_t255',
    '/api/v735/prime_basis_codec/verify_t256', '/api/v735/prime_basis_codec/verify_t257',
    '/api/v735/topo_spectral_dynamics/verify_t258', '/api/v735/topo_spectral_dynamics/verify_t259',
    '/api/v735/light_based_compute/verify_t260', '/api/v735/light_based_compute/verify_t261',
    '/api/v735/light_based_compute/verify_t262',
    '/api/v735/inverse_topology/verify_t263', '/api/v735/inverse_topology/verify_t264',
    '/api/v735/inverse_topology/verify_t265',
    '/api/v735/ftel_confinement/verify_t266', '/api/v735/ftel_confinement/verify_t267',
    '/api/v735/ftel_confinement/verify_t268',
    '/api/v735/mnq_wave_coherence/verify_t269', '/api/v735/mnq_wave_coherence/verify_t270',
    '/api/v735/rgt_bridge/verify_t271', '/api/v735/rgt_bridge/verify_t272'
  ];
  var results = [];
  var ids = ['t254','t255','t256','t257','t258','t259','t260','t261','t262','t263','t264','t265','t266','t267','t268','t269','t270','t271','t272'];
  var n = endpoints.length;
  var done = 0;
  endpoints.forEach(function(url, i) {
    v735Fetch(url, function(d) {
      results[i] = d;
      done++;
      var sid = 'v735-g-' + ids[i];
      var s = document.getElementById(sid);
      if (s) s.style.color = d.proved ? '#34d399' : '#f87171';
      if (done === n) v735ShowResult('v735-global-result', results);
    });
  });
}
function v735MveRunAll() { v735TheoremAll(); }

"""

js_anchor = "// M232 TOSAS"
# Insert before M232 TOSAS section
content = content.replace(js_anchor, JS_V735 + "\n" + js_anchor, 1)

# Write back
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("OK: v7.35 panels inserted into index_agi12.html")
