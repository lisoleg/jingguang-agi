#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新AGI 12.0 JavaScript部分"""

import re

with open(r'C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到script部分
script_start = content.find('<script>')
script_end = content.find('</script>')

old_script = content[script_start:script_end + len('</script>')]

# 新的JavaScript
new_script = '''<script>
// ════════════════════════════════════════════════════════════
// 全局状态 - AGI 12.0 三栏布局版
// ════════════════════════════════════════════════════════════
const STATE = {
  session_id: 'agi12_' + Math.random().toString(36).slice(2,9),
  mode: 'chat',           // chat | goal
  nodes: [],
  links: [],
  selected_node: null,
  history: [],
  root_name: '太乙AGI 12.0',
  sim: null,
  loading: false,
  collapsed: new Set(),
  entropy_state: { Si: 0, Sg: 0, Sc: 0, total: 0 },
  five_phase: { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 },
  anchor_validated: false,
  goal_progress: 0,
  goal_score: 0,
  // DAG视图数据
  dag_data: {
    qa_pairs: [],
    edges: [],
  },
  qa_counter: 0,
  // DAG SVG引用
  dagSvg: null,
  dagG: null,
};

// ════════════════════════════════════════════════════════════
// 初始化DAG SVG
// ════════════════════════════════════════════════════════════
function initDAG() {
  STATE.dagSvg = d3.select('#dag-svg');
  STATE.dagG = d3.select('#dag-g');
}

// DAG尺寸
function dagWidth() { return document.getElementById('dag-container').clientWidth || 400; }
function dagHeight() { return document.getElementById('dag-container').clientHeight || 600; }

// ════════════════════════════════════════════════════════════
// 熵仪表盘更新
// ════════════════════════════════════════════════════════════
function updateEntropyPanel(data) {
  if (!data) return;
  const si = data.Si || data.S_i || 0;
  const sg = data.Sg || data.S_g || 0;
  const sc = data.Sc || data.S_c || 0;

  STATE.entropy_state = { Si: si, Sg: sg, Sc: sc, total: si + sg + sc };

  document.getElementById('bar-si').style.width = (si * 100) + '%';
  document.getElementById('bar-sg').style.width = (sg * 100) + '%';
  document.getElementById('bar-sc').style.width = (sc * 100) + '%';

  document.getElementById('val-si').textContent = si.toFixed(2);
  document.getElementById('val-sg').textContent = sg.toFixed(2);
  document.getElementById('val-sc').textContent = sc.toFixed(2);
}

// ════════════════════════════════════════════════════════════
// 五行仪表盘更新
// ════════════════════════════════════════════════════════════
function updateFivePhasePanel(data) {
  if (!data) return;
  STATE.five_phase = data;

  document.getElementById('val-wood').textContent = (data.wood || 0).toFixed(2);
  document.getElementById('val-fire').textContent = (data.fire || 0).toFixed(2);
  document.getElementById('val-earth').textContent = (data.earth || 0).toFixed(2);
  document.getElementById('val-metal').textContent = (data.metal || 0).toFixed(2);
  document.getElementById('val-water').textContent = (data.water || 0).toFixed(2);
}

// ════════════════════════════════════════════════════════════
// 锚定验证面板更新
// ════════════════════════════════════════════════════════════
function updateAnchorPanel(data) {
  if (!data) { data = { verified: false }; }
  STATE.anchor_validated = data.verified || false;

  const indicator = document.getElementById('anchor-indicator');
  const text = document.getElementById('anchor-text');

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

  const items = ['anchor-energy', 'anchor-semantic', 'anchor-causal', 'anchor-empirical'];
  items.forEach((id, i) => {
    const dot = document.getElementById(id);
    const key = ['energy', 'semantic', 'causal', 'empirical'][i];
    dot.className = 'anchor-dot ' + ((data[key] !== false) ? 'ok' : 'fail');
  });
}

// ════════════════════════════════════════════════════════════
// DAG渲染 - 紧凑的关系链视图
// ════════════════════════════════════════════════════════════
function renderDAG() {
  const { qa_pairs, edges } = STATE.dag_data;
  const dagG = STATE.dagG || d3.select('#dag-g');
  const dagSvg = STATE.dagSvg || d3.select('#dag-svg');

  dagG.selectAll('*').remove();

  // 空状态
  const emptyEl = document.getElementById('dag-empty');
  if (emptyEl) emptyEl.style.display = qa_pairs.length === 0 ? 'block' : 'none';

  if (qa_pairs.length === 0) {
    document.getElementById('rel-badge').textContent = '0 节点';
    return;
  }

  document.getElementById('rel-badge').textContent = qa_pairs.length + ' 节点';

  const w = dagWidth();
  const h = dagHeight();

  // 紧凑布局 - 垂直流式布局
  const nodeW = Math.min(280, w - 60);
  const nodeH = 90;
  const gapX = 20;
  const gapY = 16;

  // 计算一行能放多少个
  const cols = Math.max(1, Math.floor((w + gapX) / (nodeW + gapX)));
  const colW = (w - nodeW) / Math.max(1, cols - 1);

  qa_pairs.forEach((qa, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    qa.x = col * colW + nodeW / 2;
    qa.y = row * (nodeH + gapY) + nodeH / 2 + 20;
  });

  // 绘制边
  edges.forEach(edge => {
    const src = qa_pairs.find(q => q.id === edge.source);
    const tgt = qa_pairs.find(q => q.id === edge.target);
    if (src && tgt) {
      const path = `M${src.x},${src.y + nodeH/2 - 10} C${src.x},${(src.y + tgt.y)/2} ${tgt.x},${(src.y + tgt.y)/2} ${tgt.x},${tgt.y - nodeH/2 + 10}`;
      const markerId = edge.type === 'ref' ? 'url(#arrow-ref)' : (edge.type === 'follow' ? 'url(#arrow-follow)' : 'url(#arrow)');
      dagG.append('path')
        .attr('class', edge.type === 'ref' ? 'dag-link-ref' : (edge.type === 'follow' ? 'dag-link-follow' : 'dag-link'))
        .attr('d', path)
        .attr('marker-end', markerId);
    }
  });

  // 绘制节点
  qa_pairs.forEach((qa) => {
    const isQ = qa.type === 'question' || qa.type === 'user';
    const isG = qa.type === 'goal';
    const nodeClass = isG ? 'dag-node dag-node-goal' : (isQ ? 'dag-node dag-node-user' : 'dag-node dag-node-ai');
    const labelText = isQ ? 'Q' + qa.num : (isG ? 'G' + qa.num : 'A' + qa.num);

    const g = dagG.append('g')
      .attr('transform', `translate(${qa.x},${qa.y})`)
      .style('cursor', 'pointer')
      .on('click', () => highlightHistory(qa.hist_idx));

    // 背景
    g.append('rect')
      .attr('x', -nodeW / 2).attr('y', -nodeH / 2)
      .attr('width', nodeW).attr('height', nodeH)
      .attr('rx', 8).attr('class', nodeClass);

    // 标签
    g.append('rect')
      .attr('x', -nodeW / 2 + 6).attr('y', -nodeH / 2 + 6)
      .attr('width', 32).attr('height', 18).attr('rx', 4)
      .attr('fill', isG ? 'var(--goal)' : (isQ ? 'var(--acc)' : 'var(--green)'));

    g.append('text')
      .attr('x', -nodeW / 2 + 22).attr('y', -nodeH / 2 + 18)
      .attr('text-anchor', 'middle').attr('class', 'dag-badge')
      .text(labelText);

    // 内容
    const content = (qa.content || '').slice(0, 35);
    g.append('text')
      .attr('x', -nodeW / 2 + 10).attr('y', 5)
      .attr('class', 'dag-label').text(content + (qa.content.length > 35 ? '...' : ''));

    // 时间
    if (qa.timestamp) {
      const time = new Date(qa.timestamp).toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit'});
      g.append('text')
        .attr('x', nodeW / 2 - 10).attr('y', nodeH / 2 - 8)
        .attr('text-anchor', 'end').attr('class', 'dag-time')
        .text(time);
    }
  });

  // 自动居中
  if (qa_pairs.length > 0) {
    const minY = Math.min(...qa_pairs.map(q => q.y));
    const offsetY = Math.max(20, 40 - minY);
    dagG.attr('transform', `translate(0,${offsetY})`);
  }
}

function highlightHistory(idx) {
  const items = document.querySelectorAll('#history .msg');
  if (items[idx]) {
    items[idx].scrollIntoView({ behavior: 'smooth', block: 'center' });
    items[idx].style.boxShadow = '0 0 12px var(--acc)';
    setTimeout(() => { items[idx].style.boxShadow = ''; }, 2000);
  }
}

// ════════════════════════════════════════════════════════════
// 添加问答对到DAG
// ════════════════════════════════════════════════════════════
function addQA2DAG(type, content, meta = {}) {
  STATE.qa_counter++;
  const qa = {
    id: type[0].toUpperCase() + '_' + STATE.qa_counter,
    type: type,
    num: Math.ceil(STATE.qa_counter / 2),
    content: content,
    timestamp: new Date().toISOString(),
    hist_idx: STATE.history.length,
    parent_refs: meta.parent_refs || [],
  };

  STATE.dag_data.qa_pairs.push(qa);

  if (meta.parent_id) {
    STATE.dag_data.edges.push({
      source: meta.parent_id,
      target: qa.id,
      type: 'follow'
    });
  }

  if (meta.parent_refs) {
    meta.parent_refs.forEach(refId => {
      STATE.dag_data.edges.push({
        source: refId,
        target: qa.id,
        type: 'ref'
      });
    });
  }

  renderDAG();
  return qa;
}

function getLastAnswerId() {
  const answers = STATE.dag_data.qa_pairs.filter(q => q.type === 'answer');
  return answers.length > 0 ? answers[answers.length - 1].id : null;
}

// ════════════════════════════════════════════════════════════
// 对话历史
// ════════════════════════════════════════════════════════════
function pushMsg(role, content, meta = {}) {
  STATE.history.push({ role, content, ...meta });

  if (role === 'user') {
    const type = meta.is_goal ? 'goal' : 'question';
    const lastAns = getLastAnswerId();
    addQA2DAG(type, content, { parent_id: lastAns });
  } else {
    const lastQA = STATE.dag_data.qa_pairs[STATE.dag_data.qa_pairs.length - 1];
    if (lastQA && lastQA.type !== 'answer') {
      lastQA.answer_content = content;
      // 添加答案节点
      STATE.qa_counter++;
      const ansQA = {
        id: 'A_' + STATE.qa_counter,
        type: 'answer',
        num: lastQA.num,
        content: content,
        timestamp: new Date().toISOString(),
        hist_idx: STATE.history.length - 1,
      };
      STATE.dag_data.qa_pairs.push(ansQA);
      STATE.dag_data.edges.push({
        source: lastQA.id,
        target: ansQA.id,
        type: 'answer'
      });
      renderDAG();
    }
  }

  renderHistory();
  updateQABadge();
}

function updateQABadge() {
  const qCount = Math.ceil(STATE.dag_data.qa_pairs.length / 2);
  document.getElementById('qa-badge').textContent = qCount + ' 对话';
}

function renderHistory() {
  const el = document.getElementById('history');
  el.innerHTML = '';

  let qCount = 0;

  STATE.history.forEach((m) => {
    const div = document.createElement('div');
    let cls = 'msg ';
    let metaHtml = '';

    if (m.role === 'user') {
      qCount++;
      cls += m.is_goal ? 'msg-goal' : 'msg-user';
      const label = m.is_goal ? 'G' + qCount : 'Q' + qCount;
      metaHtml = `<div class="msg-meta"><span style="color:${m.is_goal ? 'var(--goal)' : 'var(--acc)'};font-weight:600">[${label}]</span></div>`;
    } else {
      cls += 'msg-ai';
      metaHtml = `<div class="msg-meta"><span style="color:var(--green);font-weight:600">[A${qCount}]</span></div>`;
    }

    div.className = cls;
    div.innerHTML = metaHtml + formatMsg(m.content);
    el.appendChild(div);
  });

  el.scrollTop = el.scrollHeight;
}

function formatMsg(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

function showThinking() {
  const el = document.getElementById('history');
  const div = document.createElement('div');
  div.className = 'msg msg-ai';
  div.id = 'thinking-bubble';
  div.innerHTML = '<div class="thinking"><div class="dot1"></div><div class="dot2"></div><div class="dot3"></div></div>';
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

function hideThinking() {
  const b = document.getElementById('thinking-bubble');
  if (b) b.remove();
}

// ════════════════════════════════════════════════════════════
// API调用 - 主对话
// ════════════════════════════════════════════════════════════
async function doMainChat(message) {
  if (STATE.loading) return;
  STATE.loading = true;
  setDot('loading');
  pushMsg('user', message);
  showThinking();

  try {
    const res = await fetch('/api/chat_v2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: STATE.session_id })
    });
    const data = await res.json();

    hideThinking();
    if (data.error) { pushMsg('ai', 'Error: ' + data.error); return; }

    if (data.entropy) updateEntropyPanel(data.entropy);
    if (data.five_phase) updateFivePhasePanel(data.five_phase);
    if (data.anchor) updateAnchorPanel(data.anchor);
    if (data.analysis) showAnalysis(data.analysis);

    pushMsg('ai', data.reply || 'Analysis complete');

  } catch (e) {
    hideThinking();
    pushMsg('ai', 'Network error: ' + e.message);
  } finally {
    STATE.loading = false;
    setDot('ok');
  }
}

// ════════════════════════════════════════════════════════════
// API调用 - Goal模式
// ════════════════════════════════════════════════════════════
async function doGoalMode(goal) {
  if (STATE.loading) return;
  STATE.loading = true;
  setDot('loading');
  pushMsg('user', goal, { is_goal: true });
  showThinking();

  try {
    const res = await fetch('/api/goal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal, session_id: STATE.session_id })
    });
    const data = await res.json();

    hideThinking();
    if (data.error) { pushMsg('ai', 'Error: ' + data.error); return; }

    if (data.entropy) updateEntropyPanel(data.entropy);
    if (data.five_phase) updateFivePhasePanel(data.five_phase);
    if (data.anchor) updateAnchorPanel(data.anchor);
    if (data.analysis) showAnalysis(data.analysis);

    pushMsg('ai', data.reply || 'Goal complete');

  } catch (e) {
    hideThinking();
    pushMsg('ai', 'Network error: ' + e.message);
  } finally {
    STATE.loading = false;
    setDot('ok');
  }
}

// ════════════════════════════════════════════════════════════
// 分析面板
// ════════════════════════════════════════════════════════════
function showAnalysis(analysis) {
  const panel = document.getElementById('analysis-panel');
  const content = document.getElementById('analysis-content');

  if (!analysis || typeof analysis !== 'object') {
    panel.style.display = 'none';
    return;
  }

  panel.style.display = 'block';

  function renderObj(obj, depth = 0) {
    if (!obj || typeof obj !== 'object') return String(obj || '-');
    const entries = Object.entries(obj).filter(([k]) => !k.startsWith('_'));
    if (!entries.length) return '-';

    return entries.slice(0, 10).map(([k, v]) => {
      if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
        return `<div class="analysis-item" style="margin-left:${depth * 6}px">
          <span class="analysis-key">${k}</span>
          <div class="analysis-nested">${renderObj(v, depth + 1)}</div>
        </div>`;
      }
      return `<div class="analysis-item"><span class="analysis-key">${k}:</span> <span class="analysis-val">${String(v)}</span></div>`;
    }).join('');
  }

  content.innerHTML = renderObj(analysis);
}

// ════════════════════════════════════════════════════════════
// 工具函数
// ════════════════════════════════════════════════════════════
function setDot(state) {
  const d = document.getElementById('status-dot');
  d.className = state === 'loading' ? 'dot-loading' : 'dot-ok';
}

function resetAll() {
  STATE.nodes = [];
  STATE.links = [];
  STATE.history = [];
  STATE.selected_node = null;
  STATE.session_id = 'agi12_' + Math.random().toString(36).slice(2, 9);
  STATE.entropy_state = { Si: 0, Sg: 0, Sc: 0, total: 0 };
  STATE.five_phase = { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 };
  STATE.anchor_validated = false;
  STATE.goal_progress = 0;
  STATE.goal_score = 0;
  STATE.qa_counter = 0;
  STATE.dag_data = { qa_pairs: [], edges: [] };

  updateEntropyPanel(null);
  updateFivePhasePanel(null);
  updateAnchorPanel(null);
  document.getElementById('analysis-panel').style.display = 'none';
  renderHistory();
  updateQABadge();
  renderDAG();
}

// ════════════════════════════════════════════════════════════
// 事件绑定
// ════════════════════════════════════════════════════════════

// 顶栏模式切换
document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const mode = btn.dataset.mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.mode-tab').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
    document.getElementById('chat-input').style.display = mode === 'chat' ? 'block' : 'none';
    document.getElementById('goal-input-area').style.display = mode === 'goal' ? 'block' : 'none';
    STATE.mode = mode;
  });
});

// 左侧模式切换标签
document.querySelectorAll('.mode-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const mode = tab.dataset.mode;
    document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('chat-input').style.display = mode === 'chat' ? 'block' : 'none';
    document.getElementById('goal-input-area').style.display = mode === 'goal' ? 'block' : 'none';
    STATE.mode = mode;
  });
});

// 中间区域输入模式切换
document.querySelectorAll('.input-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const inputMode = tab.dataset.input;
    document.querySelectorAll('.input-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('input-chat').style.display = inputMode === 'chat' ? 'block' : 'none';
    document.getElementById('input-goal').style.display = inputMode === 'goal' ? 'block' : 'none';
  });
});

// 左侧主输入
const mainInput = document.getElementById('main-input');
document.getElementById('btn-send').onclick = () => {
  const v = mainInput.value.trim();
  if (!v) return;
  mainInput.value = '';
  doMainChat(v);
};
mainInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    document.getElementById('btn-send').click();
  }
});

// 左侧Goal输入
const goalInput = document.getElementById('goal-input');
document.getElementById('btn-goal').onclick = () => {
  const v = goalInput.value.trim();
  if (!v) return;
  goalInput.value = '';
  doGoalMode(v);
};

// 中间区域输入
const mainInput2 = document.getElementById('main-input2');
document.getElementById('btn-send2').onclick = () => {
  const v = mainInput2.value.trim();
  if (!v) return;
  mainInput2.value = '';
  doMainChat(v);
};
mainInput2.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    document.getElementById('btn-send2').click();
  }
});

// 中间区域Goal输入
const goalInput2 = document.getElementById('goal-input2');
document.getElementById('btn-goal2').onclick = () => {
  const v = goalInput2.value.trim();
  if (!v) return;
  goalInput2.value = '';
  doGoalMode(v);
};

// 清空按钮
document.getElementById('btn-clear').onclick = () => {
  if (confirm('Clear all conversation history?')) {
    resetAll();
  }
};

// 重置按钮
document.getElementById('btn-reset').onclick = () => {
  if (confirm('Reset all data?')) {
    resetAll();
  }
};

// ════════════════════════════════════════════════════════════
// 初始化
// ════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initDAG();

  // 初始化仪表盘（模拟数据）
  updateEntropyPanel({ Si: 0.35, Sg: 0.28, Sc: 0.18 });
  updateFivePhasePanel({ wood: 0.52, fire: 0.65, earth: 0.45, metal: 0.48, water: 0.62 });
  updateAnchorPanel({ verified: true, energy: true, semantic: true, causal: true, empirical: true });

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    renderDAG();
  });

  console.log('AGI 12.0 initialized - Three Column Layout');
});
</script>'''

# 替换script部分
new_content = content[:script_start] + new_script + content[script_end:]

# 写入
with open(r'C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'JavaScript updated, total length: {len(new_content)}')
