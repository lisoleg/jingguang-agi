#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重构AGI 12.0为三栏布局"""

import re

with open(r'C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取各个部分
head = content[:230]  # <html>...<head>...<style>
script = content[27520:]  # <script>...到结束

# 新的CSS
new_css = """
:root{
  --bg:#09090f; --bg2:#111118; --bg3:#1a1a26; --bg4:#22222e;
  --acc:#7c3aed; --acc2:#a78bfa; --acc-glow:rgba(124,58,237,.25);
  --green:#10b981; --amber:#f59e0b; --red:#ef4444; --sky:#38bdf8;
  --txt:#e8e8f0; --txt2:#8888a0; --txt3:#555566; --bdr:#252535;
  --wood:#22c55e; --fire:#ef4444; --earth:#eab308; --metal:#94a3b8; --water:#3b82f6;
  --si:#8b5cf6; --sg:#06b6d4; --sc:#f472b6;
  --grow:#06b6d4; --patch:#f97316; --goal:#fbbf24;
  --r:10px;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--txt);
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif}

/* 三栏布局
  +----------+------------------+------------+
  | 左侧面板  |     中间对话区域   |  右侧DAG图  |
  | (分析仪表) |                  |            |
  |  - 熵    |  - 输入框        |  问答关系链 |
  |  - 五行  |  - 对话历史       |            |
  |  - 锚定  |                  |            |
  +----------+------------------+------------+
*/
#app{display:flex;height:100vh;flex-direction:column}
#topbar{
  height:52px;background:var(--bg2);border-bottom:1px solid var(--bdr);
  display:flex;align-items:center;padding:0 16px;gap:12px;flex-shrink:0;z-index:20
}
#main{flex:1;display:flex;overflow:hidden}

.logo-wrap{display:flex;align-items:center;gap:10px}
.logo{font-size:22px;animation:spin 20s linear infinite;display:inline-block}
@keyframes spin{to{transform:rotate(360deg)}}
.title{font-size:15px;font-weight:700;letter-spacing:.5px}
.version-badge{
  background:linear-gradient(135deg,var(--acc),#4f46e5);
  color:#fff;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:600;
}
.theory-badge{
  background:var(--bg3);color:var(--sky);border:1px solid var(--sky);
  padding:2px 8px;border-radius:20px;font-size:10px;
}
.dot-ok{width:8px;height:8px;border-radius:50%;background:var(--green)}
.dot-loading{width:8px;height:8px;border-radius:50%;background:var(--amber);
  animation:pulse .8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.spacer{flex:1}
.header-actions{display:flex;gap:8px;align-items:center}
.mode-toggle{
  display:flex;background:var(--bg3);border-radius:8px;padding:3px;gap:2px;
}
.mode-btn{
  padding:5px 12px;border:none;border-radius:6px;cursor:pointer;font-size:12px;
  font-family:inherit;background:transparent;color:var(--txt2);transition:all .2s;
}
.mode-btn.active{background:var(--acc);color:#fff}
.btn-reset{
  background:var(--bg3);border:1px solid var(--bdr);color:var(--txt2);
  padding:5px 12px;border-radius:8px;cursor:pointer;font-size:12px;
}
.btn-reset:hover{background:var(--bg4)}

/* 左侧面板（分析仪表盘） */
#left-panel{
  width:320px;background:var(--bg2);border-right:1px solid var(--bdr);
  display:flex;flex-direction:column;flex-shrink:0;overflow:hidden
}
.panel-header{
  padding:10px 14px;border-bottom:1px solid var(--bdr);flex-shrink:0;
  display:flex;align-items:center;gap:8px;
}
.panel-header-title{font-size:12px;font-weight:700;color:var(--txt)}

#mode-section{padding:10px 14px;border-bottom:1px solid var(--bdr);flex-shrink:0}
.mode-tabs{display:flex;gap:4px;margin-bottom:8px}
.mode-tab{
  flex:1;padding:6px 4px;border:1px solid var(--bdr);border-radius:6px;
  background:var(--bg3);cursor:pointer;text-align:center;font-size:10px;
  color:var(--txt2);transition:all .2s;
}
.mode-tab.active{background:var(--acc);color:#fff;border-color:var(--acc)}

#main-input{
  width:100%;background:var(--bg3);border:1px solid var(--bdr);
  border-radius:var(--r);color:var(--txt);padding:10px;font-size:12px;
  resize:none;height:68px;font-family:inherit;outline:none;line-height:1.5;
}
#main-input:focus{border-color:var(--acc)}
#goal-input{
  width:100%;background:var(--bg3);border:1px solid var(--goal);
  border-radius:var(--r);color:var(--txt);padding:10px;font-size:12px;
  resize:none;height:68px;font-family:inherit;outline:none;line-height:1.5;
}
#goal-input:focus{border-color:var(--goal);box-shadow:0 0 0 3px rgba(251,191,36,.15)}
.input-row{display:flex;gap:6px;margin-top:6px}
.btn-send{
  flex:1;padding:7px;background:var(--acc);border:none;border-radius:6px;
  color:#fff;font-size:12px;cursor:pointer;font-family:inherit;
}
.btn-send:hover{opacity:.85}
.btn-goal{
  width:100%;margin-top:6px;padding:8px;background:linear-gradient(135deg,var(--goal),#f59e0b);
  border:none;border-radius:6px;color:#000;font-size:12px;font-weight:700;
  cursor:pointer;font-family:inherit;transition:opacity .15s;
}
.btn-goal:hover{opacity:.85}

.panel-section{padding:10px 14px;border-bottom:1px solid var(--bdr);flex-shrink:0}
.panel-title{
  font-size:10px;color:var(--txt2);margin-bottom:8px;
  display:flex;align-items:center;gap:6px;font-weight:600;
}

.entropy-bars{display:flex;flex-direction:column;gap:6px}
.entropy-row{display:flex;align-items:center;gap:6px}
.entropy-label{font-size:10px;width:20px;color:var(--txt2)}
.entropy-bar-wrap{flex:1;height:8px;background:var(--bg);border-radius:4px;overflow:hidden}
.entropy-bar{height:100%;border-radius:4px;transition:width .5s ease}
.bar-si{background:var(--si)}.bar-sg{background:var(--sg)}.bar-sc{background:var(--sc)}
.entropy-value{font-size:10px;width:45px;text-align:right;color:var(--txt)}

.five-phase-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:4px}
.element-card{
  background:var(--bg3);border-radius:6px;padding:6px 2px;text-align:center;
  border:1px solid transparent;
}
.element-card.wood{border-color:var(--wood)}
.element-card.fire{border-color:var(--fire)}
.element-card.earth{border-color:var(--earth)}
.element-card.metal{border-color:var(--metal)}
.element-card.water{border-color:var(--water)}
.element-icon{font-size:14px}
.element-name{font-size:8px;color:var(--txt2);margin-top:2px}
.element-value{font-size:12px;font-weight:700;margin-top:2px}
.element-card.wood .element-value{color:var(--wood)}
.element-card.fire .element-value{color:var(--fire)}
.element-card.earth .element-value{color:var(--earth)}
.element-card.metal .element-value{color:var(--metal)}
.element-card.water .element-value{color:var(--water)}

.anchor-status{display:flex;align-items:center;gap:8px;margin-top:6px}
.anchor-indicator{width:10px;height:10px;border-radius:50%;background:var(--green)}
.anchor-indicator.warning{background:var(--amber)}.anchor-indicator.danger{background:var(--red)}
.anchor-text{font-size:10px;color:var(--txt)}
.anchor-details{
  margin-top:6px;font-size:9px;color:var(--txt2);
  display:grid;grid-template-columns:1fr 1fr;gap:3px;
}
.anchor-item{
  background:var(--bg3);padding:3px 6px;border-radius:4px;
  display:flex;align-items:center;gap:4px;
}
.anchor-dot{width:5px;height:5px;border-radius:50%}
.anchor-dot.ok{background:var(--green)}.anchor-dot.fail{background:var(--red)}

#analysis-panel{
  background:var(--bg2);max-height:140px;overflow-y:auto;
  border-top:1px solid var(--bdr);flex-shrink:0;
}
#analysis-panel::-webkit-scrollbar{width:3px}
#analysis-panel::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:2px}
.analysis-item{padding:5px 0;border-bottom:1px solid var(--bdr);font-size:11px}
.analysis-key{color:var(--acc2);font-weight:600}
.analysis-val{color:var(--txt)}
.analysis-nested{margin-left:10px;padding-left:6px;border-left:2px solid var(--bdr)}

/* 中间对话区域 */
#center-panel{
  flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--bg);
  min-width:0;
}
.center-header{
  height:44px;padding:0 16px;background:var(--bg2);
  border-bottom:1px solid var(--bdr);display:flex;align-items:center;gap:10px;
  flex-shrink:0;
}
.center-title{font-size:12px;font-weight:600;color:var(--txt)}
.qa-badge{
  background:var(--acc-glow);color:var(--acc2);padding:2px 8px;border-radius:20px;
  font-size:10px;font-weight:600;
}
.spacer-center{flex:1}
.btn-clear{
  background:var(--bg3);border:1px solid var(--bdr);color:var(--txt2);
  padding:4px 10px;border-radius:5px;cursor:pointer;font-size:10px;
}
.btn-clear:hover{background:var(--bg4)}

#history{flex:1;overflow-y:auto;padding:12px 16px;display:flex;flex-direction:column;gap:10px}
#history::-webkit-scrollbar{width:3px}
#history::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:2px}
.msg{border-radius:var(--r);padding:10px 12px;font-size:12.5px;line-height:1.6}
.msg-user{background:var(--acc-glow);border:1px solid rgba(124,58,237,.3);
  color:var(--txt);align-self:flex-end;max-width:85%}
.msg-ai{background:var(--bg2);border:1px solid var(--bdr);color:var(--txt);max-width:100%}
.msg-goal{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.3)}
.msg-meta{font-size:9px;color:var(--txt2);margin-bottom:3px}
.msg-goal-badge{
  background:rgba(251,191,36,.2);color:var(--goal);padding:1px 5px;
  border-radius:10px;font-size:9px;display:inline-block;margin-bottom:3px;
}
.msg-node-badge{
  background:rgba(6,182,212,.2);color:var(--grow);padding:1px 5px;border-radius:10px;font-size:9px;
}
.thinking{display:flex;gap:4px;align-items:center;padding:4px 0}
.dot1,.dot2,.dot3{width:5px;height:5px;border-radius:50%;background:var(--acc2);
  animation:bounce 1s infinite}
.dot2{animation-delay:.15s}.dot3{animation-delay:.3s}
@keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}

.input-section{
  padding:10px 16px 12px;background:var(--bg2);
  border-top:1px solid var(--bdr);flex-shrink:0;
}
.input-tabs{display:flex;gap:4px;margin-bottom:8px}
.input-tab{
  padding:5px 12px;border:1px solid var(--bdr);border-radius:5px;
  background:var(--bg3);cursor:pointer;font-size:10px;color:var(--txt2);
}
.input-tab.active{background:var(--acc);color:#fff;border-color:var(--acc)}

/* 右侧DAG关系图 */
#right-panel{
  width:400px;background:var(--bg2);border-left:1px solid var(--bdr);
  display:flex;flex-direction:column;flex-shrink:0;overflow:hidden
}
.right-header{
  height:44px;padding:0 14px;background:var(--bg2);
  border-bottom:1px solid var(--bdr);display:flex;align-items:center;gap:8px;
  flex-shrink:0;
}
.right-title{font-size:12px;font-weight:600;color:var(--txt)}
.right-icon{font-size:14px}
.rel-badge{
  background:var(--sky);color:#000;padding:2px 7px;border-radius:10px;
  font-size:9px;font-weight:600;
}

#dag-container{flex:1;position:relative;overflow:hidden;background:var(--bg)}
#dag-svg{width:100%;height:100%}

.dag-empty-state{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  text-align:center;color:var(--txt3);
}
.dag-empty-icon{font-size:42px;margin-bottom:10px;opacity:.4}
.dag-empty-text{font-size:12px}

.dag-node{fill:var(--bg3);stroke:var(--acc);stroke-width:2;rx:6;cursor:pointer}
.dag-node:hover{filter:brightness(1.2)}
.dag-node-user{fill:rgba(124,58,237,.2);stroke:var(--acc)}
.dag-node-ai{fill:rgba(16,185,129,.15);stroke:var(--green)}
.dag-node-goal{fill:rgba(251,191,36,.15);stroke:var(--goal)}
.dag-link{stroke:var(--bdr);stroke-width:1.5;fill:none;opacity:.6}
.dag-link-ref{stroke:var(--sky);stroke-width:1.5);stroke-dasharray:3,2;opacity:.7}
.dag-link-follow{stroke:var(--grow);stroke-width:1.5;opacity:.7}
.dag-label{font-size:10px;fill:var(--txt);pointer-events:none}
.dag-label-q{font-size:9px;fill:var(--acc2);font-weight:600}
.dag-label-a{font-size:9px;fill:var(--green)}
.dag-time{font-size:8px;fill:var(--txt3)}
.dag-badge{font-size:9px;fill:#fff;font-weight:600}

#dag-footer{
  padding:8px 14px;background:var(--bg2);
  border-top:1px solid var(--bdr);flex-shrink:0;
  display:flex;align-items:center;gap:10px;font-size:10px;color:var(--txt2);
}
.dag-stat{display:flex;align-items:center;gap:3px}
.dag-dot{width:7px;height:7px;border-radius:50%}
.dot-q{background:var(--acc)}.dot-a{background:var(--green)}
.dot-ref{background:var(--sky)}.dot-follow{background:var(--grow)}

#tooltip{position:absolute;background:var(--bg3);border:1px solid var(--bdr);
  border-radius:6px;padding:8px 12px;font-size:11px;line-height:1.6;
  max-width:260px;pointer-events:none;opacity:0;transition:opacity .15s;z-index:50}

#canvas-wrap{display:none}
.link{stroke:var(--bdr);stroke-width:2;fill:none;opacity:.6}
.link-grow{stroke:var(--grow);stroke-width:2;stroke-dasharray:4,3;fill:none;opacity:.7}
.node-g circle,.node-g rect{transition:filter .2s}
.node-g:hover circle,.node-g:hover rect{filter:brightness(1.2)}
.n-center{fill:var(--acc)}
.n-core{fill:var(--bg3);stroke:var(--acc);stroke-width:2}
.node-label{font-size:11px;fill:var(--txt);text-anchor:middle;pointer-events:none;
  dominant-baseline:middle;font-weight:500}
.node-label-center{font-size:13px;font-weight:700;color:#fff}
"""

# 新的body HTML
new_body = """<div id="app">
  <div id="topbar">
    <div class="logo-wrap">
      <span class="logo">&#128302;</span>
      <span class="title">复合体AGI 12.0</span>
      <span class="version-badge">24模块·8层</span>
      <span class="theory-badge">IAWW统一场论</span>
    </div>
    <div class="dot-ok" id="status-dot"></div>
    <span class="spacer"></span>
    <div class="header-actions">
      <div class="mode-toggle">
        <button class="mode-btn active" data-mode="chat">对话模式</button>
        <button class="mode-btn" data-mode="goal">Goal模式</button>
      </div>
      <button class="btn-reset" id="btn-reset">&#8634; 重置</button>
    </div>
  </div>

  <div id="main">
    <!-- 左侧：分析仪表盘 -->
    <div id="left-panel">
      <div class="panel-header">
        <span class="panel-header-title">&#128202; 分析仪表盘</span>
      </div>

      <div id="mode-section">
        <div class="mode-tabs">
          <div class="mode-tab active" data-mode="chat">&#128172; 对话</div>
          <div class="mode-tab" data-mode="goal">&#127919; Goal</div>
        </div>
        <div id="chat-input">
          <textarea id="main-input" placeholder="输入问题，AGI 12.0 启动24模块协同分析..."></textarea>
          <div class="input-row">
            <button class="btn-send" id="btn-send">发送</button>
          </div>
        </div>
        <div id="goal-input-area" style="display:none">
          <textarea id="goal-input" placeholder="输入Goal目标，如：帮我分析AGI 12.0的架构创新"></textarea>
          <button class="btn-goal" id="btn-goal">&#127919; 启动Goal推理</button>
        </div>
      </div>

      <div class="panel-section" id="entropy-panel">
        <div class="panel-title">&#9889; 三相熵耦合</div>
        <div class="entropy-bars">
          <div class="entropy-row">
            <span class="entropy-label" style="color:var(--si)">Si</span>
            <div class="entropy-bar-wrap"><div class="entropy-bar bar-si" id="bar-si" style="width:0%"></div></div>
            <span class="entropy-value" id="val-si">0.00</span>
          </div>
          <div class="entropy-row">
            <span class="entropy-label" style="color:var(--sg)">Sg</span>
            <div class="entropy-bar-wrap"><div class="entropy-bar bar-sg" id="bar-sg" style="width:0%"></div></div>
            <span class="entropy-value" id="val-sg">0.00</span>
          </div>
          <div class="entropy-row">
            <span class="entropy-label" style="color:var(--sc)">Sc</span>
            <div class="entropy-bar-wrap"><div class="entropy-bar bar-sc" id="bar-sc" style="width:0%"></div></div>
            <span class="entropy-value" id="val-sc">0.00</span>
          </div>
        </div>
      </div>

      <div class="panel-section" id="five-phase-panel">
        <div class="panel-title">&#9788; 五行耦合</div>
        <div class="five-phase-grid">
          <div class="element-card wood"><div class="element-icon">&#127795;</div><div class="element-name">木</div><div class="element-value" id="val-wood">0</div></div>
          <div class="element-card fire"><div class="element-icon">&#128293;</div><div class="element-name">火</div><div class="element-value" id="val-fire">0</div></div>
          <div class="element-card earth"><div class="element-icon">&#127757;</div><div class="element-name">土</div><div class="element-value" id="val-earth">0</div></div>
          <div class="element-card metal"><div class="element-icon">&#11044;</div><div class="element-name">金</div><div class="element-value" id="val-metal">0</div></div>
          <div class="element-card water"><div class="element-icon">&#128167;</div><div class="element-name">水</div><div class="element-value" id="val-water">0</div></div>
        </div>
      </div>

      <div class="panel-section" id="anchor-panel">
        <div class="panel-title">&#128737; 介质锚定</div>
        <div class="anchor-status">
          <div class="anchor-indicator" id="anchor-indicator"></div>
          <span class="anchor-text" id="anchor-text">等待验证</span>
        </div>
        <div class="anchor-details">
          <div class="anchor-item"><div class="anchor-dot ok" id="anchor-energy"></div><span>能量</span></div>
          <div class="anchor-item"><div class="anchor-dot ok" id="anchor-semantic"></div><span>语义</span></div>
          <div class="anchor-item"><div class="anchor-dot ok" id="anchor-causal"></div><span>因果</span></div>
          <div class="anchor-item"><div class="anchor-dot ok" id="anchor-empirical"></div><span>经验</span></div>
        </div>
      </div>

      <div id="analysis-panel" style="display:none;flex-shrink:0;padding:10px 14px">
        <div class="panel-title">&#128202; 模块分析</div>
        <div id="analysis-content"></div>
      </div>
    </div>

    <!-- 中间：对话区域 -->
    <div id="center-panel">
      <div class="center-header">
        <span class="center-title">&#128172; 对话</span>
        <span class="qa-badge" id="qa-badge">0 对话</span>
        <span class="spacer-center"></span>
        <button class="btn-clear" id="btn-clear">清空</button>
      </div>
      <div id="history"></div>
      <div class="input-section">
        <div class="input-tabs">
          <div class="input-tab active" data-input="chat">&#128172; 对话模式</div>
          <div class="input-tab" data-input="goal">&#127919; Goal模式</div>
        </div>
        <div id="input-chat">
          <textarea id="main-input2" placeholder="输入问题，AGI 12.0 启动24模块协同分析..."></textarea>
          <div class="input-row" style="margin-top:6px">
            <button class="btn-send" id="btn-send2">发送</button>
          </div>
        </div>
        <div id="input-goal" style="display:none">
          <textarea id="goal-input2" placeholder="输入Goal目标，如：帮我分析AGI 12.0的架构创新"></textarea>
          <button class="btn-goal" id="btn-goal2">&#127919; 启动Goal推理</button>
        </div>
      </div>
    </div>

    <!-- 右侧：DAG关系图 -->
    <div id="right-panel">
      <div class="right-header">
        <span class="right-icon">&#128279;</span>
        <span class="right-title">对话关系链</span>
        <span class="rel-badge" id="rel-badge">0 节点</span>
      </div>
      <div id="dag-container">
        <svg id="dag-svg">
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <path d="M0,0 L0,6 L9,3 z" fill="var(--txt3)"/>
            </marker>
            <marker id="arrow-ref" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <path d="M0,0 L0,6 L9,3 z" fill="var(--sky)"/>
            </marker>
            <marker id="arrow-follow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
              <path d="M0,0 L0,6 L9,3 z" fill="var(--grow)"/>
            </marker>
          </defs>
          <g id="dag-g"></g>
        </svg>
        <div class="dag-empty-state" id="dag-empty">
          <div class="dag-empty-icon">&#128279;</div>
          <div class="dag-empty-text">发送消息开始构建<br>对话关系链</div>
        </div>
        <div id="tooltip"></div>
      </div>
      <div id="dag-footer">
        <div class="dag-stat"><div class="dag-dot dot-q"></div><span>问题</span></div>
        <div class="dag-stat"><div class="dag-dot dot-a"></div><span>答案</span></div>
        <div class="dag-stat"><div class="dag-dot dot-ref"></div><span>引用</span></div>
        <div class="dag-stat"><div class="dag-dot dot-follow"></div><span>追问</span></div>
      </div>
    </div>
  </div>

  <div id="canvas-wrap">
    <svg id="svg-container">
      <defs>
        <radialGradient id="glow-center" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#7c3aed" stop-opacity=".6"/>
          <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <g id="zoom-layer"></g>
    </svg>
  </div>
</div>"""

# 组合
new_content = head + '<style>' + new_css + '</style>' + new_body + script

# 写入
with open(r'C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'文件已更新，长度: {len(new_content)}')
