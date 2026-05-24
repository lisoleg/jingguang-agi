// ═════════════════════════════════════════════════════════════
//  STN 苏格拉底拓扑网络 — 核心JS函数（v1.0）
//  左侧：思维森林视图 | 底部：流贯控制台 | 全局：本体导航
// ═════════════════════════════════════════════════════════════

// ─── 全局状态 ───
const stnState = {
  forestData: [],       // 森林树数据
  activeNodeId: null,    // 当前活跃节点
  rootNodeId: null,     // 根节点ID
  collapsedNodes: new Set(),  // 折叠的节点
  forestFilter: '',       // 过滤关键词
  consoleEntropy: 0.20,  // 控制台熵值
  ctxUsage: 0,           // 上下文使用率
  ontoVisible: false,     // 本体导航是否可见
  currentView: 'dashboard' // 'dashboard' | 'forest'
};

// ─── 本体导航 (Ontology Navigator) ───
function toggleOntoNav() {
  stnState.ontoVisible = !stnState.ontoVisible;
  const el = document.getElementById('ontology-nav');
  if (el) el.classList.toggle('visible', stnState.ontoVisible);
}

function updateOntoNav(rootText) {
  const el = document.getElementById('onto-root');
  if (el) el.textContent = rootText || '未初始化';
}

// ─── 左侧面板视图切换 ───
function switchLeftPanel(view) {
  stnState.currentView = view;
  const dashboard = document.getElementById('dashboard-content');
  const forest = document.getElementById('forest-view-panel');
  const btnD = document.getElementById('btn-view-dashboard');
  const btnF = document.getElementById('btn-view-forest');
  if (dashboard) dashboard.style.display = view === 'dashboard' ? 'flex' : 'none';
  if (forest) forest.style.display = view === 'forest' ? 'flex' : 'none';
  if (btnD) {
    btnD.style.background = view === 'dashboard' ? 'var(--acc)' : 'transparent';
    btnD.style.color = view === 'dashboard' ? '#fff' : 'var(--txt2)';
  }
  if (btnF) {
    btnF.style.background = view === 'forest' ? 'var(--acc)' : 'transparent';
    btnF.style.color = view === 'forest' ? '#fff' : 'var(--txt2)';
  }
  if (view === 'forest') renderForestView();
}

// ─── 思维森林视图渲染 ───
function renderForestView() {
  const container = document.getElementById('forest-tree');
  const empty = document.getElementById('forest-empty');
  if (!container) return;

  const data = stnState.forestData;
  if (!data || data.length === 0) {
    if (empty) empty.style.display = 'block';
    container.innerHTML = '';
    return;
  }
  if (empty) empty.style.display = 'none';

  const rootNodes = data.filter(n => !n.parent || n.parent === null);
  container.innerHTML = rootNodes.map(n => renderForestNode(n, data, 0)).join('');

  // 绘制SVG连线
  renderForestLinks(data);
  updateForestStats(data);
}

function renderForestNode(node, allData, depth) {
  const isCollapsed = stnState.collapsedNodes.has(node.id);
  const children = allData.filter(n => n.parent === node.id);
  const hasChildren = children.length > 0;
  const isActive = node.id === stnState.activeNodeId;
  const isRoot = !node.parent;
  let iconClass = 'q';
  if (node.type === 'A') iconClass = 'a';
  else if (node.type === 'G') iconClass = 'g';
  else if (node.type === 'S') iconClass = 's';
  else if (node.type === 'E') iconClass = 'e';

  let html = '<div class="forest-node' +
    (isActive ? ' active' : '') +
    (isRoot ? ' forest-node-root' : '') +
    '" data-id="' + node.id + '" onclick="selectForestNode(\'' + node.id + '\')">';

  // 缩进
  if (depth > 0) html += '<span style="display:inline-block;width:' + (depth * 14) + 'px"></span>';

  // 折叠按钮
  if (hasChildren) {
    html += '<span class="forest-collapse-btn' + (isCollapsed ? ' collapsed' : '') +
      '" onclick="event.stopPropagation();toggleForestNode(\'' + node.id + '\')">';
    html += isCollapsed ? '▸' : '▾';
    html += '</span> ';
  } else {
    html += '<span style="display:inline-block;width:14px"></span> ';
  }

  // 图标
  html += '<span class="forest-node-icon ' + iconClass + '">' + (node.type || 'Q') + '</span> ';

  // 文本（支持过滤高亮）
  const label = (node.label || node.text || '节点').substring(0, 40);
  const filter = stnState.forestFilter.toLowerCase();
  let display = label;
  if (filter) {
    const idx = label.toLowerCase().indexOf(filter);
    if (idx >= 0) {
      display = label.substring(0, idx) +
        '<mark style="background:var(--acc-glow);color:var(--acc2)">' +
        label.substring(idx, idx + filter.length) + '</mark>' +
        label.substring(idx + filter.length);
    }
  }
  html += '<span>' + display + '</span>';

  // 分叉标记
  if (node.isFork) html += ' <span style="color:#a855f7;font-size:8px">⑂</span>';

  html += '</div>';

  // 子节点
  if (hasChildren && !isCollapsed) {
    html += '<div class="forest-node-children">';
    children.forEach(child => {
      html += renderForestNode(child, allData, depth + 1);
    });
    html += '</div>';
  }

  return html;
}

function renderForestLinks(data) {
  const svg = document.getElementById('forest-links-svg');
  if (!svg) return;
  // 简单实现：暂时不画SVG连线，后续版本补充
  svg.innerHTML = '';
}

function toggleForestNode(id) {
  if (stnState.collapsedNodes.has(id)) {
    stnState.collapsedNodes.delete(id);
  } else {
    stnState.collapsedNodes.add(id);
  }
  renderForestView();
}

function selectForestNode(id) {
  stnState.activeNodeId = id;
  renderForestView();
  // 滚动到对应消息
  const msgEl = document.querySelector('[data-node-id="' + id + '"]');
  if (msgEl) {
    msgEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    msgEl.classList.add('msg-stn-active');
    setTimeout(() => msgEl.classList.remove('msg-stn-active'), 2000);
  }
  updateWorkspaceForNode(id);
}

function forestExpandAll() {
  stnState.collapsedNodes.clear();
  renderForestView();
}

function forestCollapseAll() {
  stnState.forestData.forEach(n => {
    const children = stnState.forestData.filter(c => c.parent === n.id);
    if (children.length > 0) stnState.collapsedNodes.add(n.id);
  });
  renderForestView();
}

function forestScrollToActive() {
  if (!stnState.activeNodeId) return;
  const el = document.querySelector('#forest-tree [data-id="' + stnState.activeNodeId + '"]');
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function forestGoToRoot() {
  if (stnState.rootNodeId) {
    selectForestNode(stnState.rootNodeId);
  }
}

function forestFilter(val) {
  stnState.forestFilter = val;
  renderForestView();
}

function updateForestStats(data) {
  const statsEl = document.getElementById('forest-stats');
  const depthEl = document.getElementById('forest-depth');
  if (statsEl) statsEl.textContent = '节点: ' + data.length;
  if (depthEl && data.length > 0) {
    let maxDepth = 0;
    data.forEach(n => {
      let d = 0;
      let cur = n;
      while (cur && cur.parent) {
        d++;
        cur = data.find(p => p.id === cur.parent);
        if (d > 50) break;
      }
      if (d > maxDepth) maxDepth = d;
    });
    depthEl.textContent = '深度: ' + maxDepth;
  }
}

// ─── 工作区控制 ───
function updateWorkspaceForNode(nodeId) {
  const node = stnState.forestData.find(n => n.id === nodeId);
  if (!node) return;
  // 高亮中间面板对应消息
  const msgs = document.querySelectorAll('#center-panel .msg, #workspace-content .ws-msg');
  msgs.forEach(m => m.classList.remove('ws-msg-active'));
  // 尝试通过 data-node-id 定位
  const target = document.querySelector('[data-node-id="' + nodeId + '"]');
  if (target) {
    target.classList.add('ws-msg-active');
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// ─── 流贯控制台 (Ftel Console) ───
function ftelSummarize() {
  setConsoleStatus('正在总结...', 'warn');
  if (typeof sendMessage === 'function') {
    sendMessage('/summarize');
  }
}

function ftelDebate() {
  setConsoleStatus('正在发起诘辩...', 'warn');
  if (typeof sendMessage === 'function') {
    sendMessage('/debate');
  }
}

function ftelIntegrate() {
  setConsoleStatus('正在整合...', 'warn');
  if (typeof sendMessage === 'function') {
    sendMessage('/integrate');
  }
}

function ftelCmdKeyDown(e) {
  if (e.key === 'Enter') {
    const input = document.getElementById('ftel-cmd-input');
    if (input && input.value.trim()) {
      const cmd = input.value.trim();
      input.value = '';
      if (typeof sendMessage === 'function') {
        sendMessage(cmd);
      }
      setConsoleStatus('命令执行中...', 'warn');
    }
  }
}

function setConsoleStatus(text, type) {
  const el = document.getElementById('ftel-status');
  if (el) {
    el.textContent = text;
    el.style.color = type === 'warn' ? 'var(--amber)' : type === 'error' ? 'var(--red)' : 'var(--txt2)';
  }
}

function updateConsoleEntropy(val) {
  const fill = document.getElementById('ftel-entropy-fill');
  const valEl = document.getElementById('ftel-entropy-val');
  if (fill) {
    const pct = Math.min(100, val * 100);
    fill.style.width = pct + '%';
    fill.style.background = pct > 70 ? 'var(--red)' : pct > 40 ? 'var(--amber)' : 'var(--green)';
  }
  if (valEl) valEl.textContent = val.toFixed(2);
  stnState.consoleEntropy = val;
}

function updateConsoleCTX(used, total) {
  const fill = document.getElementById('ftel-ctx-fill');
  const valEl = document.getElementById('ftel-ctx-val');
  const pct = total > 0 ? (used / total * 100) : 0;
  if (fill) fill.style.width = Math.min(100, pct) + '%';
  if (valEl) valEl.textContent = Math.round(pct) + '%';
  stnState.ctxUsage = pct;
}

// ─── 陈天桥测试 / 右侧面板更新函数 ───
// 熵值面板更新 (Si/Sg/Sc 三维熵条)
function updateEntropyPanel(data) {
  if (!data) return;
  const si = data.Si || data.S_i || data.si || 0.35;
  const sg = data.Sg || data.S_g || data.sg || 0.28;
  const sc = data.Sc || data.S_c || data.sc || 0.18;
  const siVal = Math.max(0.05, Math.min(0.95, Number(si)));
  const sgVal = Math.max(0.05, Math.min(0.95, Number(sg)));
  const scVal = Math.max(0.05, Math.min(0.95, Number(sc)));
  const barSi = document.getElementById('bar-si');
  const barSg = document.getElementById('bar-sg');
  const barSc = document.getElementById('bar-sc');
  const valSi = document.getElementById('val-si');
  const valSg = document.getElementById('val-sg');
  const valSc = document.getElementById('val-sc');
  if (barSi) barSi.style.width = (siVal * 100) + '%';
  if (barSg) barSg.style.width = (sgVal * 100) + '%';
  if (barSc) barSc.style.width = (scVal * 100) + '%';
  if (valSi) valSi.textContent = siVal.toFixed(2);
  if (valSg) valSg.textContent = sgVal.toFixed(2);
  if (valSc) valSc.textContent = scVal.toFixed(2);
}

// 五行仪表盘更新 (木/火/土/金/水)
function updateFivePhasePanel(data) {
  if (!data) return;
  const ids = ['wood', 'fire', 'earth', 'metal', 'water'];
  ids.forEach(k => {
    const el = document.getElementById('val-' + k);
    if (el) el.textContent = Number(data[k] || 0).toFixed(2);
  });
}

// 锚定验证面板更新
function updateAnchorPanel(data) {
  if (!data) { data = { verified: false }; }
  const indicator = document.getElementById('anchor-indicator');
  const text = document.getElementById('anchor-text');
  if (indicator && text) {
    if (data.verified) {
      indicator.className = 'anchor-indicator';
      text.textContent = '锚定验证通过';
    } else if (data.warning) {
      indicator.className = 'anchor-indicator warning';
      text.textContent = '部分约束待验证';
    } else {
      indicator.className = 'anchor-indicator danger';
      text.textContent = '等待验证';
    }
  }
  ['energy', 'semantic', 'causal', 'empirical'].forEach(k => {
    const dot = document.getElementById('anchor-' + k);
    if (dot) dot.className = 'anchor-dot ' + ((data[k] !== false) ? 'ok' : 'fail');
  });
}

// 介质共振面板更新 (stub - 完整实现依赖其他面板元素)
function updateMediumPanel(data) {
  if (!data) return;
  const phaseLock = Number(data.phase_lock || 0);
  const fill = document.getElementById('phase-ring-fill');
  const ringText = document.getElementById('phase-ring-text');
  if (fill) {
    const circumference = 2 * Math.PI * 18;
    fill.setAttribute('stroke-dasharray', (circumference * phaseLock) + ' ' + circumference);
    fill.setAttribute('stroke', phaseLock > 0.7 ? 'var(--xinzhai)' : phaseLock > 0.4 ? 'var(--medium)' : 'var(--phase-low)');
  }
  if (ringText) ringText.textContent = Math.round(phaseLock * 100) + '%';
}

// ─── STN 面板显示/隐藏 ───
function toggleSTNPanel(panel, btn) {
  document.querySelectorAll('.stn-toggle-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const forest = document.getElementById('forest-panel');
  const dag = document.getElementById('dag-panel');
  const consoleEl = document.getElementById('ftel-console');

  if (forest) forest.classList.toggle('hidden', panel !== 'forest');
  if (dag) dag.classList.toggle('hidden', panel !== 'dag');
  if (consoleEl) consoleEl.classList.toggle('hidden', panel !== 'console');
}

// ─── 从现有对话数据构建森林树 ───
function buildForestFromHistory() {
  // 优先从 appState.chatHistory 构建
  const history = (window.appState && window.appState.chatHistory) || [];
  let nodes = [];

  if (history.length > 0) {
    history.forEach((item, i) => {
      const isUser = item.role === 'user';
      nodes.push({
        id: 'node_' + i,
        type: isUser ? 'Q' : 'A',
        label: (item.content || '').substring(0, 50),
        text: item.content || '',
        parent: i > 0 ? 'node_' + (i - 1) : null,
        isFork: false,
        timestamp: item.timestamp || Date.now()
      });
    });
  } else {
    // fallback：从 DOM 读取
    const msgs = document.querySelectorAll('#history .msg, #workspace-content .ws-msg');
    if (msgs.length === 0) return;
    msgs.forEach((msg, i) => {
      const isUser = msg.classList.contains('msg-user') || msg.classList.contains('ws-msg-user');
      const textEl = msg.querySelector('.msg-text, .ws-msg-text') || msg;
      const text = textEl.textContent || '';
      nodes.push({
        id: 'node_' + i,
        type: isUser ? 'Q' : 'A',
        label: text.substring(0, 50),
        text: text,
        parent: i > 0 ? 'node_' + (i - 1) : null,
        isFork: false
      });
    });
  }

  stnState.forestData = nodes;
  if (nodes.length > 0) stnState.rootNodeId = nodes[0].id;
  if (nodes.length > 0) stnState.activeNodeId = nodes[nodes.length - 1].id;

  renderForestView();
  updateOntoNav(nodes.length > 0 ? nodes[0].label : '未初始化');

  // 绘制 DAG 边（如果 DAG 面板可见）
  if (typeof renderDAG === 'function') {
    try { renderDAG(); } catch(e) { console.warn('[STN] renderDAG error:', e); }
  }
}

// ─── 拦截现有 sendMessage 来更新森林 ───
(function patchSendMessage() {
  if (window._stnPatched) return;
  const _orig = window.sendMessage;
  window.sendMessage = function(text) {
    if (typeof _orig === 'function') _orig.apply(this, arguments);
    // 延迟更新森林（等AI回复后）
    setTimeout(buildForestFromHistory, 1500);
  };
  window._stnPatched = true;
})();

// ─── 覆盖 updateDashboard 来同步控制台熵值 ───
(function patchUpdateDashboard() {
  if (window._stnPatchedDashboard) return;
  const _orig = window.updateDashboard;
  window.updateDashboard = function(d) {
    if (typeof _orig === 'function') _orig.apply(this, arguments);
    if (d && d.entropy !== undefined) {
      updateConsoleEntropy(d.entropy);
    }
    if (d && d.ctx_usage !== undefined) {
      updateConsoleCTX(d.ctx_usage.used || 0, d.ctx_usage.total || 100);
    }
  };
  window._stnPatchedDashboard = true;
})();

// ─── 初始化 ───
document.addEventListener('DOMContentLoaded', function() {
  // 延迟初始化（等主JS加载完毕）
  setTimeout(function() {
    buildForestFromHistory();
    // 默认显示森林视图和对话工作区
    if (typeof switchLeftPanel === 'function') {
      switchLeftPanel('forest');
    }
    // 确保流贯控制台可见
    var ftel = document.getElementById('ftel-console');
    if (ftel) ftel.classList.remove('hidden');
    console.log('[STN] 苏格拉底拓扑网络 v1.0 已加载');
  }, 800);
});

// 导出供全局调用
window.stnApi = {
  buildForestFromHistory,
  renderForestView,
  selectForestNode,
  switchLeftPanel,
  toggleSTNPanel,
  updateConsoleEntropy,
  updateConsoleCTX
};

console.log('[STN] stn_core.js loaded');
