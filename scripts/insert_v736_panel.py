#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insert_v736_panel.py
Inserts v7.36 panel (M244-M249) CSS/HTML/JS into index_agi12.html.
"""
import os, re

FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'static', 'index_agi12.html')
FRONTEND = os.path.normpath(FRONTEND)

# --- CSS (inserted once before </style> or after v735 CSS) ---
CSS_MARKER = '.panel-v735 {'
CSS_INSERT_AFTER = '<!-- ========== v7.35 Panels (M236-M243) ========== -->'

V736_CSS = """
      /* ====== v7.36 panel styling ====== */
      .panel-v736 { border-left: 2px solid #a78bfa; background: rgba(167,139,250,0.04); }
      .panel-v736 .panel-title { color: #a78bfa; }
"""

# --- HTML panels (inserted after v7.35 panels block) ---
HTML_ANCHOR = '      <!-- ========== v7.35 Panels (M236-M243) ========== -->'

V736_HTML = """
      <!-- ========== v7.36 Panels (M244-M249) ========== -->

      <!-- M244 Higher-Order Kuramoto Sync -->
      <div class="panel-section panel-v736" id="v736-kuramoto-panel" data-hint="M244 高阶Kuramoto同步: 一级相变+滞后回线+社会共识涌现 T2.72-T2.74">
        <div class="panel-title">M244 高阶Kuramoto同步</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736KuramotoState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v736KuramotoT272()" style="font-size:9px;padding:2px 6px">T272</button>
          <button onclick="v736KuramotoT273()" style="font-size:9px;padding:2px 6px">T273</button>
          <button onclick="v736KuramotoT274()" style="font-size:9px;padding:2px 6px">T274</button>
          <button onclick="v736KuramotoSim()" style="font-size:9px;padding:2px 6px">仿真</button>
          <span id="v736-kuramoto-t272" style="color:var(--txt3)">T272</span>
          <span id="v736-kuramoto-t273" style="color:var(--txt3)">T273</span>
          <span id="v736-kuramoto-t274" style="color:var(--txt3)">T274</span>
        </div>
        <div id="v736-kuramoto-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M245 Five Geometric Archetypes -->
      <div class="panel-section panel-v736" id="v736-geom-panel" data-hint="M245 五大几何原型: Oloid/钢板网/三角钻头/正方变三角/鲁珀特之泪 T2.75-T2.77">
        <div class="panel-title">M245 五大几何原型</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736GeomState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v736GeomT275()" style="font-size:9px;padding:2px 6px">T275</button>
          <button onclick="v736GeomT276()" style="font-size:9px;padding:2px 6px">T276</button>
          <button onclick="v736GeomT277()" style="font-size:9px;padding:2px 6px">T277</button>
          <button onclick="v736GeomAll()" style="font-size:9px;padding:2px 6px">全部原型</button>
          <span id="v736-geom-t275" style="color:var(--txt3)">T275</span>
          <span id="v736-geom-t276" style="color:var(--txt3)">T276</span>
          <span id="v736-geom-t277" style="color:var(--txt3)">T277</span>
        </div>
        <div id="v736-geom-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M246 Arithmetic Justice -->
      <div class="panel-section panel-v736" id="v736-arith-panel" data-hint="M246 算术正义: mHC算子+Birkhoff多面体+CSA素数采样+算术守恒 T2.78-T2.80">
        <div class="panel-title">M246 算术正义</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736ArithState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v736ArithT278()" style="font-size:9px;padding:2px 6px">T278</button>
          <button onclick="v736ArithT279()" style="font-size:9px;padding:2px 6px">T279</button>
          <button onclick="v736ArithT280()" style="font-size:9px;padding:2px 6px">T280</button>
          <button onclick="v736ArithCSA()" style="font-size:9px;padding:2px 6px">CSA注意力</button>
          <span id="v736-arith-t278" style="color:var(--txt3)">T278</span>
          <span id="v736-arith-t279" style="color:var(--txt3)">T279</span>
          <span id="v736-arith-t280" style="color:var(--txt3)">T280</span>
        </div>
        <div id="v736-arith-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M247 Cognitive Recursive Dynamics -->
      <div class="panel-section panel-v736" id="v736-crd-panel" data-hint="M247 认知递归动力学: CRD三层+EML螺旋+暗知识+IDO对偶 T2.81-T2.83">
        <div class="panel-title">M247 认知递归动力学</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736CrdState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v736CrdT281()" style="font-size:9px;padding:2px 6px">T281</button>
          <button onclick="v736CrdT282()" style="font-size:9px;padding:2px 6px">T282</button>
          <button onclick="v736CrdT283()" style="font-size:9px;padding:2px 6px">T283</button>
          <button onclick="v736CrdDark()" style="font-size:9px;padding:2px 6px">暗知识</button>
          <span id="v736-crd-t281" style="color:var(--txt3)">T281</span>
          <span id="v736-crd-t282" style="color:var(--txt3)">T282</span>
          <span id="v736-crd-t283" style="color:var(--txt3)">T283</span>
        </div>
        <div id="v736-crd-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M248 Simplicial Knowledge -->
      <div class="panel-section panel-v736" id="v736-simp-panel" data-hint="M248 单纯复形知识: 概念拓扑+霍奇三流推理(演绎/悖论/顿悟) T2.84-T2.86">
        <div class="panel-title">M248 单纯复形知识</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736SimpState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v736SimpT284()" style="font-size:9px;padding:2px 6px">T284</button>
          <button onclick="v736SimpT285()" style="font-size:9px;padding:2px 6px">T285</button>
          <button onclick="v736SimpT286()" style="font-size:9px;padding:2px 6px">T286</button>
          <button onclick="v736SimpHodge()" style="font-size:9px;padding:2px 6px">霍奇分解</button>
          <span id="v736-simp-t284" style="color:var(--txt3)">T284</span>
          <span id="v736-simp-t285" style="color:var(--txt3)">T285</span>
          <span id="v736-simp-t286" style="color:var(--txt3)">T286</span>
        </div>
        <div id="v736-simp-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- M249 DIKWP Semantic -->
      <div class="panel-section panel-v736" id="v736-dikwp-panel" data-hint="M249 DIKWP语义量纲: D->I->K->W->P双向群+约柜Ark归责+M178算子 T2.87-T2.89">
        <div class="panel-title">M249 DIKWP语义量纲</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736DikwpState()" style="font-size:9px;padding:2px 6px">状态</button>
          <button onclick="v736DikwpT287()" style="font-size:9px;padding:2px 6px">T287</button>
          <button onclick="v736DikwpT288()" style="font-size:9px;padding:2px 6px">T288</button>
          <button onclick="v736DikwpT289()" style="font-size:9px;padding:2px 6px">T289</button>
          <button onclick="v736DikwpArk()" style="font-size:9px;padding:2px 6px">约柜Ark</button>
          <span id="v736-dikwp-t287" style="color:var(--txt3)">T287</span>
          <span id="v736-dikwp-t288" style="color:var(--txt3)">T288</span>
          <span id="v736-dikwp-t289" style="color:var(--txt3)">T289</span>
        </div>
        <div id="v736-dikwp-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>

      <!-- v7.36 Global -->
      <div class="panel-section panel-v736" id="v736-global-panel" data-hint="v7.36 全局: M244-M249 定理验证+MVE">
        <div class="panel-title">v7.36 Global (M244-M249)</div>
        <div style="display:flex;gap:3px;flex-wrap:wrap;margin:3px 0">
          <button onclick="v736TheoremAll()" style="font-size:9px;padding:2px 6px">全部定理</button>
          <button onclick="v736HealthCheck()" style="font-size:9px;padding:2px 6px">健康检查</button>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;margin:3px 0">
          <span id="v736-g-t272" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T272</span>
          <span id="v736-g-t273" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T273</span>
          <span id="v736-g-t274" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T274</span>
          <span id="v736-g-t275" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T275</span>
          <span id="v736-g-t276" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T276</span>
          <span id="v736-g-t277" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T277</span>
          <span id="v736-g-t278" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T278</span>
          <span id="v736-g-t279" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T279</span>
          <span id="v736-g-t280" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T280</span>
          <span id="v736-g-t281" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T281</span>
          <span id="v736-g-t282" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T282</span>
          <span id="v736-g-t283" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T283</span>
          <span id="v736-g-t284" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T284</span>
          <span id="v736-g-t285" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T285</span>
          <span id="v736-g-t286" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T286</span>
          <span id="v736-g-t287" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T287</span>
          <span id="v736-g-t288" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T288</span>
          <span id="v736-g-t289" style="font-size:8px;padding:1px 4px;background:rgba(167,139,250,0.2);border-radius:3px;color:var(--txt3)">T289</span>
        </div>
        <div id="v736-global-result" style="font-size:9px;color:var(--txt2);max-height:110px;overflow-y:auto;padding:3px;background:rgba(0,0,0,0.2);border-radius:4px;display:none;line-height:1.3;white-space:pre-wrap"></div>
      </div>
"""

# --- JavaScript (inserted before end of script block, after v7.35 JS) ---
JS_ANCHOR = '// v7.35 Global'

V736_JS = """
// ========== v7.36 Functions ==========

function v736Fetch(url, cb, method, body) {
  var opt = { method: method || 'GET', headers: {'Content-Type':'application/json'} };
  if (body) opt.body = JSON.stringify(body);
  fetch(url, opt).then(function(r){ return r.json(); }).then(cb).catch(function(e){ cb({error: String(e)}); });
}
function v736ShowResult(id, d) {
  var el = document.getElementById(id);
  if (!el) return;
  el.style.display = 'block';
  el.textContent = typeof d === 'string' ? d : JSON.stringify(d, null, 2);
}

// M244 Kuramoto
function v736KuramotoState() { v736Fetch('/api/v736/m244/state', function(d){ v736ShowResult('v736-kuramoto-result', d); }); }
function v736KuramotoT272() { v736Fetch('/api/v736/m244/verify_theorem', function(d){ v736ShowResult('v736-kuramoto-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.72'){var s=document.getElementById('v736-kuramoto-t272');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736KuramotoT273() { v736Fetch('/api/v736/m244/verify_theorem', function(d){ v736ShowResult('v736-kuramoto-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.73'){var s=document.getElementById('v736-kuramoto-t273');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736KuramotoT274() { v736Fetch('/api/v736/m244/verify_theorem', function(d){ v736ShowResult('v736-kuramoto-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.74'){var s=document.getElementById('v736-kuramoto-t274');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736KuramotoSim() { v736Fetch('/api/v736/m244/compute', function(d){ v736ShowResult('v736-kuramoto-result', d); }, 'POST', {n_oscillators:20, K1:1.0, K2:2.0, n_steps:100}); }

// M245 Geometric Archetypes
function v736GeomState() { v736Fetch('/api/v736/m245/state', function(d){ v736ShowResult('v736-geom-result', d); }); }
function v736GeomT275() { v736Fetch('/api/v736/m245/verify_theorem', function(d){ v736ShowResult('v736-geom-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.75'){var s=document.getElementById('v736-geom-t275');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736GeomT276() { v736Fetch('/api/v736/m245/verify_theorem', function(d){ v736ShowResult('v736-geom-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.76'){var s=document.getElementById('v736-geom-t276');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736GeomT277() { v736Fetch('/api/v736/m245/verify_theorem', function(d){ v736ShowResult('v736-geom-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.77'){var s=document.getElementById('v736-geom-t277');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736GeomAll() { v736Fetch('/api/v736/m245/all_archetypes', function(d){ v736ShowResult('v736-geom-result', d); }); }

// M246 Arithmetic Justice
function v736ArithState() { v736Fetch('/api/v736/m246/state', function(d){ v736ShowResult('v736-arith-result', d); }); }
function v736ArithT278() { v736Fetch('/api/v736/m246/verify_theorem', function(d){ v736ShowResult('v736-arith-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.78'){var s=document.getElementById('v736-arith-t278');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736ArithT279() { v736Fetch('/api/v736/m246/verify_theorem', function(d){ v736ShowResult('v736-arith-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.79'){var s=document.getElementById('v736-arith-t279');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736ArithT280() { v736Fetch('/api/v736/m246/verify_theorem', function(d){ v736ShowResult('v736-arith-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.80'){var s=document.getElementById('v736-arith-t280');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736ArithCSA() { v736Fetch('/api/v736/m246/csa_attention', function(d){ v736ShowResult('v736-arith-result', d); }, 'POST', {n:16}); }

// M247 CRD
function v736CrdState() { v736Fetch('/api/v736/m247/state', function(d){ v736ShowResult('v736-crd-result', d); }); }
function v736CrdT281() { v736Fetch('/api/v736/m247/verify_theorem', function(d){ v736ShowResult('v736-crd-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.81'){var s=document.getElementById('v736-crd-t281');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736CrdT282() { v736Fetch('/api/v736/m247/verify_theorem', function(d){ v736ShowResult('v736-crd-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.82'){var s=document.getElementById('v736-crd-t282');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736CrdT283() { v736Fetch('/api/v736/m247/verify_theorem', function(d){ v736ShowResult('v736-crd-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.83'){var s=document.getElementById('v736-crd-t283');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736CrdDark() { v736Fetch('/api/v736/m247/dark_knowledge', function(d){ v736ShowResult('v736-crd-result', d); }, 'POST', {dim:8}); }

// M248 Simplicial Knowledge
function v736SimpState() { v736Fetch('/api/v736/m248/state', function(d){ v736ShowResult('v736-simp-result', d); }); }
function v736SimpT284() { v736Fetch('/api/v736/m248/verify_theorem', function(d){ v736ShowResult('v736-simp-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.84'){var s=document.getElementById('v736-simp-t284');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736SimpT285() { v736Fetch('/api/v736/m248/verify_theorem', function(d){ v736ShowResult('v736-simp-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.85'){var s=document.getElementById('v736-simp-t285');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736SimpT286() { v736Fetch('/api/v736/m248/verify_theorem', function(d){ v736ShowResult('v736-simp-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.86'){var s=document.getElementById('v736-simp-t286');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736SimpHodge() { v736Fetch('/api/v736/m248/hodge_reason', function(d){ v736ShowResult('v736-simp-result', d); }, 'POST', {flow:[1.2,-0.5,0.8,0.3,-1.1,0.6]}); }

// M249 DIKWP
function v736DikwpState() { v736Fetch('/api/v736/m249/state', function(d){ v736ShowResult('v736-dikwp-result', d); }); }
function v736DikwpT287() { v736Fetch('/api/v736/m249/verify_theorem', function(d){ v736ShowResult('v736-dikwp-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.87'){var s=document.getElementById('v736-dikwp-t287');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736DikwpT288() { v736Fetch('/api/v736/m249/verify_theorem', function(d){ v736ShowResult('v736-dikwp-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.88'){var s=document.getElementById('v736-dikwp-t288');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736DikwpT289() { v736Fetch('/api/v736/m249/verify_theorem', function(d){ v736ShowResult('v736-dikwp-result', d); (d.theorems||[]).forEach(function(t){ if(t.theorem==='T2.89'){var s=document.getElementById('v736-dikwp-t289');if(s)s.style.color=t.proved?'#34d399':'#f87171';}}); }); }
function v736DikwpArk() { v736Fetch('/api/v736/m249/ark_accountability', function(d){ v736ShowResult('v736-dikwp-result', d); }, 'POST', {decision:'test AGI decision', source:'taiyi-agi', action:'reason', consequence:'output generated'}); }

// v7.36 Global
function v736TheoremAll() {
  var urls = [
    '/api/v736/m244/verify_theorem', '/api/v736/m245/verify_theorem',
    '/api/v736/m246/verify_theorem', '/api/v736/m247/verify_theorem',
    '/api/v736/m248/verify_theorem', '/api/v736/m249/verify_theorem'
  ];
  var results = {}; var done = 0; var n = urls.length;
  var ids = ['t272','t273','t274','t275','t276','t277','t278','t279','t280','t281','t282','t283','t284','t285','t286','t287','t288','t289'];
  urls.forEach(function(url) {
    v736Fetch(url, function(d) {
      (d.theorems||[]).forEach(function(t) {
        var tid = t.theorem.replace('T2.','t');
        results[tid] = t;
        var sid = 'v736-g-' + tid;
        var el = document.getElementById(sid);
        if (el) el.style.color = t.proved ? '#34d399' : '#f87171';
      });
      done++;
      if (done === n) v736ShowResult('v736-global-result', results);
    });
  });
}
function v736HealthCheck() { v736Fetch('/api/v736/health', function(d){ v736ShowResult('v736-global-result', d); }); }

"""

def main():
    with open(FRONTEND, 'r', encoding='utf-8') as f:
        content = f.read()

    # Guard: don't insert twice
    if '<!-- ========== v7.36 Panels (M244-M249) ==========' in content:
        print('v7.36 panels already present, skipping HTML insert.')
    else:
        # Insert CSS before </style> that's near the panel-v735 style
        if '.panel-v735 {' in content and '.panel-v736 {' not in content:
            content = content.replace('.panel-v735 {', V736_CSS + '      .panel-v735 {', 1)
            print('CSS inserted.')
        # Insert HTML after v7.35 panels comment
        content = content.replace(
            '      <!-- ========== v7.35 Panels (M236-M243) ========== -->',
            '      <!-- ========== v7.35 Panels (M236-M243) ========== -->' + V736_HTML,
            1
        )
        print('HTML panels inserted.')

    if '// ========== v7.36 Functions ==========' in content:
        print('v7.36 JS already present, skipping JS insert.')
    else:
        # Insert JS before "// v7.35 Global"
        content = content.replace(
            '// v7.35 Global',
            V736_JS + '\n// v7.35 Global',
            1
        )
        print('JS inserted.')

    with open(FRONTEND, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Done. File size: {len(content)} chars')


if __name__ == '__main__':
    main()
