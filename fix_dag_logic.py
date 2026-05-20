#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复对话关系链(DAG)逻辑：
1. 全局Q/A编号（跨线索）
2. 修复detectNewThread：引用之前问题时不应开新线索
3. 添加跨线索边（引用/整合/诘辩）
4. 添加全屏切换功能
"""

import re

FILE = r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12_cleaned.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ═══════════════════════════════════════════════════════════════
# 1. 替换 detectNewThread 函数
# ═══════════════════════════════════════════════════════════════
old_detect = """function detectNewThread(newContent) {
  const threads = STATE.dag_data.threads;
  if (threads.length === 0) return true; // 第一条消息

  const lastThread = threads[threads.length - 1];
  const qaPairs = lastThread.qa_pairs;
  if (!qaPairs || qaPairs.length === 0) return true;

  // 获取最后一条QA对
  const lastQA = qaPairs[qaPairs.length - 1];
  if (!lastQA) return true;

  // ── 追问词检测：继续当前线索的强信号 ──────────────────────────────
  // 这些词表明用户想继续深入当前话题
  const followWords = ['那', '那么', '还有', '另外', '接着', '然后呢', '为什么', '怎么',
    '能', '请', '帮我', '给我', '讲', '说', '具体', '详细', '能否', '能否详细',
    '能否解释', '能举个例子吗', '举个例子', '比如', '换句话说', '也就是说',
    '也就是说', '所以', '因此', '那如果', '那是不是', '这是不是意味着'];
  const startsWithFollow = followWords.some(w => newContent.startsWith(w) || newContent.includes(w));
  if (startsWithFollow && qaPairs.length > 0) {
    return false; // 是追问，继续当前线索
  }

  // ── 核心话题延续性检测 ─────────────────────────────────────────────
  // 真正的问题是：当前问题是否在"持续深入"上一轮讨论的核心话题？

  // 获取上一轮对话的核心内容（答案内容最能代表当前讨论的核心）
  const lastContent = lastQA.content || '';
  const lastKeywords = extractKeywords(lastContent);
  const currentKeywords = extractKeywords(newContent);

  // 关键词重叠率：衡量话题延续程度
  const overlap = lastKeywords.filter(k => currentKeywords.includes(k));
  const overlapRatio = lastKeywords.length > 0 ? overlap.length / lastKeywords.length : 0;

  // ── 判断标准：话题是否真的在持续深入 ────────────────────────────────
  //
  // ★ 新线索的触发条件（必须满足以下至少一个）：
  // 1. 关键词重叠率极低（<15%）：说明话题明显跳转
  // 2. 检测到全新话题词：上一轮没出现过的具体话题词
  // 3. 内容长度对比：当前问题简短但与上一轮内容无重叠 → 可能是全新话题
  // 4. 陈天桥测试题：每道题独立话题，强制开新线索（已通过meta.force_new_thread处理）
  //
  // ★ 继续当前线索的条件：
  // 1. 关键词重叠率较高（≥15%）：话题在延续
  // 2. 上一轮回答中包含具体实体/概念，当前问题继续追问
  // 3. 语义上明显是"追问"而非"新话题"

  // 关键话题词库：这些词出现意味着话题切换
  const topicSwitchWords = [
    // 全新话题开始
    '另外', '还有个问题', '顺便问一下', '对了', '突然想到',
    '我想了解', '我想知道', '能介绍一下', '帮我查一下',
    // 陈天桥测试题特征
    '陈天桥', '认知测试', '测试开始'
  ];

  const hasTopicSwitch = topicSwitchWords.some(w => newContent.includes(w));

  // 检测全新话题词（上一轮没出现过的具体名词）
  const lastContentLower = lastContent.toLowerCase();
  const newTopicWords = currentKeywords.filter(k =>
    k.length >= 2 &&
    !lastContentLower.includes(k) &&
    overlap.indexOf(k) === -1
  );

  // 综合判断：是否开新线索
  // 条件1：话题跳转词出现
  if (hasTopicSwitch) {
    return true;
  }

  // 条件2：关键词重叠率太低（话题完全跳转）
  // 阈值设为15%，低于这个说明是全新话题
  if (overlapRatio < 0.15 && lastKeywords.length >= 3) {
    return true;
  }

  // 条件3：出现大量新话题词（>=3个），且原有话题词几乎不重叠
  if (newTopicWords.length >= 3 && overlap.length <= 1) {
    return true;
  }

  // 默认：继续当前线索（视为追问或持续深入）
  return false;
}"""

new_detect = """function detectNewThread(newContent) {
  const threads = STATE.dag_data.threads;
  if (threads.length === 0) return true;

  const lastThread = threads[threads.length - 1];
  const qaPairs = lastThread.qa_pairs;
  if (!qaPairs || qaPairs.length === 0) return true;

  const lastQA = qaPairs[qaPairs.length - 1];
  if (!lastQA) return true;

  const content = newContent.toLowerCase();

  // 强信号1：引用之前的问题编号 -> 绝对不是新线索
  const refQPattern = /(?:问题)?[qQ](\\d+)|第\\s*(\\d+)\\s*个?问题|第\\s*(\\d+)\\s*题|上述|前面|之前|刚才/i;
  if (refQPattern.test(newContent)) return false;

  // 强信号2：整合/综合请求 -> 绝对不是新线索
  const integrateWords = ['整合', '综合', '总结', '归纳', '汇总', '比较', '对比',
    '分析一下', '评价一下', '前面三个', '上述', '以上回答', 'A1', 'A2', 'A3'];
  if (integrateWords.some(w => content.includes(w))) return false;

  // 强信号3：追问词检测
  const followWords = ['那', '那么', '还有', '接着', '然后呢', '为什么', '怎么',
    '能否', '能否详细', '能否解释', '举个例子', '比如', '换句话说', '也就是说',
    '所以', '因此', '那如果', '那是不是', '这是不是意味着',
    '什么意思', '详细', '具体', '展开', '深入'];
  if (followWords.some(w => content.includes(w))) return false;

  // 核心话题延续性检测
  const lastContent = lastQA.content || '';
  const lastKeywords = extractKeywords(lastContent);
  const currentKeywords = extractKeywords(newContent);
  const overlap = lastKeywords.filter(k => currentKeywords.includes(k));
  const overlapRatio = lastKeywords.length > 0 ? overlap.length / lastKeywords.length : 0;

  const topicSwitchWords = [
    '另外', '还有个问题', '顺便问一下', '对了', '突然想到',
    '我想了解', '我想知道', '能介绍一下', '帮我查一下',
    '换个话题', '说点别的', '聊点别的'
  ];
  if (topicSwitchWords.some(w => content.includes(w))) return true;

  if (overlapRatio < 0.15 && lastKeywords.length >= 3) return true;

  return false;
}"""

if old_detect in content:
    content = content.replace(old_detect, new_detect)
    print("[OK] detectNewThread replaced")
else:
    print("[WARN] detectNewThread old text not found, skipping")


# ═══════════════════════════════════════════════════════════════
# 2. 替换 addQA2DAG 函数（添加全局编号 + 跨线索链接追踪）
# ═══════════════════════════════════════════════════════════════
old_addqa = """function addQA2DAG(type, content, meta = {}) {
  STATE.qa_counter++;
  const { threads } = STATE.dag_data;

  // 用户消息：检测是否开新线索
  if (type === 'question' || type === 'goal') {
    // 测试题目强制每题开新线索
    const isNewThread = meta.force_new_thread || detectNewThread(content);

    if (isNewThread || threads.length === 0) {
      // 开新线索
      STATE.thread_counter++;
      const newThread = {
        id: 'thread_' + STATE.thread_counter,
        qa_pairs: [],
      };
      threads.push(newThread);
    }
  }

  // 获取当前线索
  const currentThread = threads[threads.length - 1];
  if (!currentThread) return null;

  const qa = {
    id: type[0].toUpperCase() + '_' + STATE.qa_counter,
    type: type,
    content: content,
    timestamp: new Date().toISOString(),
    hist_idx: STATE.history.length,
  };

  currentThread.qa_pairs.push(qa);
  renderDAG();
  return qa;
}"""

new_addqa = """function addQA2DAG(type, content, meta = {}) {
  STATE.qa_counter++;
  const { threads } = STATE.dag_data;

  // 用户消息：检测是否开新线索
  if (type === 'question' || type === 'goal') {
    const isNewThread = meta.force_new_thread || detectNewThread(content);

    if (isNewThread || threads.length === 0) {
      STATE.thread_counter++;
      const newThread = {
        id: 'thread_' + STATE.thread_counter,
        qa_pairs: [],
        links: [],  // 跨线索链接
      };
      threads.push(newThread);
    }
  }

  const currentThread = threads[threads.length - 1];
  if (!currentThread) return null;
  if (!currentThread.links) currentThread.links = [];

  // 全局编号
  let globalId = '';
  if (type === 'question' || type === 'goal' || type === 'user') {
    STATE.global_q_counter++;
    globalId = 'Q' + STATE.global_q_counter;
  } else {
    STATE.global_a_counter++;
    globalId = 'A' + STATE.global_a_counter;
  }

  const qa = {
    id: type[0].toUpperCase() + '_' + STATE.qa_counter,
    global_id: globalId,
    type: type,
    content: content,
    timestamp: new Date().toISOString(),
    hist_idx: STATE.history.length,
    relation: 'QA',       // QA / REF / INTEGRATE / ELENCHUS
    ref_targets: [],      // 引用的目标global_id列表
  };

  // 检测关系类型
  const lower = (content || '').toLowerCase();
  if (/真的|确定|如果|会怎样|为什么|何以见得|请证明/i.test(content)) {
    qa.relation = 'ELENCHUS';
  } else if (/上述|之前|刚才|如前所述|引用|参照|问题[qQ]?\\d+|第\\d+个?问题/i.test(content)) {
    qa.relation = 'REF';
    // 尝试提取引用的Q编号
    const refMatch = content.match(/[qQ]?(\\d+)|第\\s*(\\d+)\\s*个?问题|第\\s*(\\d+)\\s*题/g);
    if (refMatch) {
      refMatch.forEach(m => {
        const num = parseInt(m.replace(/\\D/g, ''), 10);
        if (num > 0) qa.ref_targets.push('Q' + num);
      });
    }
  } else if (/整合|综合|总结|综上|基于以上|前面三个|A1|A2|A3/i.test(content)) {
    qa.relation = 'INTEGRATE';
    // 整合前面所有答案
    threads.forEach(t => {
      t.qa_pairs.forEach(p => {
        if (p.type === 'answer' && p.global_id) qa.ref_targets.push(p.global_id);
      });
    });
  }

  currentThread.qa_pairs.push(qa);
  renderDAG();
  return qa;
}"""

if old_addqa in content:
    content = content.replace(old_addqa, new_addqa)
    print("[OK] addQA2DAG replaced")
else:
    print("[WARN] addQA2DAG old text not found, skipping")


# ═══════════════════════════════════════════════════════════════
# 3. 替换 pushMsg 中 AI 回复部分（添加全局编号）
# ═══════════════════════════════════════════════════════════════
old_pushmsg_ai = """  } else {
    // AI回复：添加到当前线索的最后一个问题后面
    if (threads.length > 0) {
      const currentThread = threads[threads.length - 1];
      // 确保当前线程有QA对
      if (!currentThread.qa_pairs) currentThread.qa_pairs = [];
      const lastQ = currentThread.qa_pairs.filter(q => q.type === 'question' || q.type === 'user').slice(-1)[0];
      if (lastQ || currentThread.qa_pairs.length > 0) {
        STATE.qa_counter++;
        const ansQA = {
          id: 'A_' + STATE.qa_counter,
          type: 'answer',
          content: content,
          timestamp: new Date().toISOString(),
          hist_idx: STATE.history.length - 1,
        };
        currentThread.qa_pairs.push(ansQA);
        renderDAG();
      } else {
        // 如果线程中没有问题（异常情况），创建一个新的Q A对
        STATE.qa_counter++;
        const ansQA = {
          id: 'A_' + STATE.qa_counter,
          type: 'answer',
          content: content,
          timestamp: new Date().toISOString(),
          hist_idx: STATE.history.length - 1,
        };
        currentThread.qa_pairs.push(ansQA);
        renderDAG();
      }
    } else {
      // 如果没有任何线程，创建一个新线程（异常情况）
      STATE.thread_counter++;
      const newThread = {
        id: 'thread_' + STATE.thread_counter,
        qa_pairs: [],
      };
      threads.push(newThread);
      STATE.qa_counter++;
      newThread.qa_pairs.push({
        id: 'A_' + STATE.qa_counter,
        type: 'answer',
        content: content,
        timestamp: new Date().toISOString(),
        hist_idx: STATE.history.length - 1,
      });
      renderDAG();
    }
  }"""

new_pushmsg_ai = """  } else {
    // AI回复：添加到当前线索的最后一个问题后面
    if (threads.length > 0) {
      const currentThread = threads[threads.length - 1];
      if (!currentThread.qa_pairs) currentThread.qa_pairs = [];
      const lastQ = currentThread.qa_pairs.filter(q => q.type === 'question' || q.type === 'user').slice(-1)[0];
      STATE.global_a_counter++;
      const ansQA = {
        id: 'A_' + (++STATE.qa_counter),
        global_id: 'A' + STATE.global_a_counter,
        type: 'answer',
        content: content,
        timestamp: new Date().toISOString(),
        hist_idx: STATE.history.length - 1,
        relation: 'QA',
        ref_targets: [],
      };
      currentThread.qa_pairs.push(ansQA);
      renderDAG();
    } else {
      STATE.thread_counter++;
      const newThread = {
        id: 'thread_' + STATE.thread_counter,
        qa_pairs: [],
        links: [],
      };
      threads.push(newThread);
      STATE.global_a_counter++;
      newThread.qa_pairs.push({
        id: 'A_' + (++STATE.qa_counter),
        global_id: 'A' + STATE.global_a_counter,
        type: 'answer',
        content: content,
        timestamp: new Date().toISOString(),
        hist_idx: STATE.history.length - 1,
        relation: 'QA',
        ref_targets: [],
      });
      renderDAG();
    }
  }"""

if old_pushmsg_ai in content:
    content = content.replace(old_pushmsg_ai, new_pushmsg_ai)
    print("[OK] pushMsg AI reply replaced")
else:
    print("[WARN] pushMsg AI reply old text not found, skipping")


# ═══════════════════════════════════════════════════════════════
# 4. 替换 renderDAG 函数（全局编号 + 跨线索边 + 全屏支持）
# ═══════════════════════════════════════════════════════════════
# 由于renderDAG很长且复杂，我们采用分段替换策略

# 4a. 替换 badge 计算（全局编号）
old_badge = """      // 标签（Q/A/G）
      const labelBg = isG ? 'var(--goal)' : (isQ ? 'var(--acc)' : 'var(--green)');
      const labelText = isG ? ('G' + (qa._nodeIdx + 1)) : (isQ ? ('Q' + (qa._nodeIdx + 1)) : ('A' + (qa._nodeIdx + 1)));"""

new_badge = """      // 标签（Q/A/G）——使用全局编号
      const labelBg = isG ? 'var(--goal)' : (isQ ? 'var(--acc)' : 'var(--green)'));
      const labelText = qa.global_id || (isG ? ('G' + (qa._nodeIdx + 1)) : (isQ ? ('Q' + (qa._nodeIdx + 1)) : ('A' + (qa._nodeIdx + 1))));"""

if old_badge in content:
    content = content.replace(old_badge, new_badge)
    print("[OK] renderDAG badge replaced")
else:
    print("[WARN] renderDAG badge old text not found, skipping")


# 4b. 在renderDAG绘制边之后、绘制节点之前，添加跨线索边绘制
# 我们找到 "// 绘制边" 后面的线程内边绘制结束位置，然后插入跨线索边

old_edges_end = """    // 绘制边
    thread.qa_pairs.forEach((qa, qi) => {
      if (qi < thread.qa_pairs.length - 1) {
        const nextQA = thread.qa_pairs[qi + 1];
        const path = `M${qa.x},${qa.y + nodeH/2 - 8} L${nextQA.x},${nextQA.y - nodeH/2 + 8}`;
        dagG.append('path')
          .attr('d', path)
          .attr('stroke', threadColor).attr('stroke-width', 1.5).attr('fill', 'none').attr('opacity', 0.6);
      }
    });

    // 绘制节点"""

new_edges_end = """    // 绘制边（线程内）
    thread.qa_pairs.forEach((qa, qi) => {
      if (qi < thread.qa_pairs.length - 1) {
        const nextQA = thread.qa_pairs[qi + 1];
        const path = `M${qa.x},${qa.y + nodeH/2 - 8} L${nextQA.x},${nextQA.y - nodeH/2 + 8}`;
        dagG.append('path')
          .attr('d', path)
          .attr('stroke', threadColor).attr('stroke-width', 1.5).attr('fill', 'none').attr('opacity', 0.6);
      }
    });

    // 绘制跨线索引用/整合边
    thread.qa_pairs.forEach((qa) => {
      if (qa.relation === 'REF' || qa.relation === 'INTEGRATE') {
        qa.ref_targets.forEach(targetId => {
          // 在所有线程中查找目标节点
          threads.forEach((tgtThread, tgtTi) => {
            if (tgtTi === ti) return; // 同线程已在上面绘制
            tgtThread.qa_pairs.forEach(tgtQA => {
              if (tgtQA.global_id === targetId) {
                const isRef = qa.relation === 'REF';
                const linkColor = isRef ? 'var(--sky)' : 'var(--grow)';
                const linkDash = isRef ? '3,2' : '5,3';
                const path = `M${qa.x - nodeW/2 + 5},${qa.y} L${tgtQA.x + nodeW/2 - 5},${tgtQA.y}`;
                dagG.append('path')
                  .attr('d', path)
                  .attr('stroke', linkColor)
                  .attr('stroke-width', 1.5)
                  .attr('stroke-dasharray', linkDash)
                  .attr('fill', 'none')
                  .attr('opacity', 0.7);
              }
            });
          });
        });
      }
    });

    // 绘制节点"""

if old_edges_end in content:
    content = content.replace(old_edges_end, new_edges_end)
    print("[OK] renderDAG cross-thread edges added")
else:
    print("[WARN] renderDAG edges old text not found, skipping")


# 4c. 在 tooltip 中也显示全局编号
old_tooltip = """      g.on('mouseover', function(event) {
        const tt = document.getElementById('tooltip');
        if (tt) {
          tt.innerHTML = `<strong style="color:var(--acc2)">${labelText}</strong><br>${(qa.content||'').slice(0,80)}${(qa.content||'').length > 80 ? '…' : ''}`;"""

new_tooltip = """      g.on('mouseover', function(event) {
        const tt = document.getElementById('tooltip');
        if (tt) {
          const relLabel = qa.relation && qa.relation !== 'QA' ? ` <span style="font-size:9px;color:${SOCRATIC_RELATIONS[qa.relation]?.color||'#888'}">[${SOCRATIC_RELATIONS[qa.relation]?.label||qa.relation}]</span>` : '';
          tt.innerHTML = `<strong style="color:var(--acc2)">${labelText}</strong>${relLabel}<br>${(qa.content||'').slice(0,80)}${(qa.content||'').length > 80 ? '…' : ''}`;"""

if old_tooltip in content:
    content = content.replace(old_tooltip, new_tooltip)
    print("[OK] renderDAG tooltip replaced")
else:
    print("[WARN] renderDAG tooltip old text not found, skipping")


# ═══════════════════════════════════════════════════════════════
# 5. 在 toggleDAG 之后插入 fullscreen 函数
# ═══════════════════════════════════════════════════════════════
old_toggledag = """function toggleDAG() {
  const container = document.getElementById('dag-container');
  const btn = document.getElementById('btn-dag-toggle');
  if (!container || !btn) return;
  DAG_COLLAPSED = !DAG_COLLAPSED;
  container.style.display = DAG_COLLAPSED ? 'none' : 'flex';
  btn.innerHTML = DAG_COLLAPSED ? '&#9658;' : '&#9660;';
  btn.title = DAG_COLLAPSED ? '展开对话关系链' : '折叠对话关系链';
}"""

new_toggledag = """function toggleDAG() {
  const container = document.getElementById('dag-container');
  const btn = document.getElementById('btn-dag-toggle');
  if (!container || !btn) return;
  DAG_COLLAPSED = !DAG_COLLAPSED;
  container.style.display = DAG_COLLAPSED ? 'none' : 'flex';
  btn.innerHTML = DAG_COLLAPSED ? '&#9658;' : '&#9660;';
  btn.title = DAG_COLLAPSED ? '展开对话关系链' : '折叠对话关系链';
}

// ════════════════════════════════════════════════════════════════
// DAG 全屏切换
// ════════════════════════════════════════════════════════════════
let DAG_FULLSCREEN = false;
function toggleDAGFullscreen() {
  let overlay = document.getElementById('dag-fullscreen-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'dag-fullscreen-overlay';
    overlay.innerHTML = `
      <div id="dag-fullscreen-header">
        <span class="fs-title">&#128279; 对话关系链（全屏）</span>
        <span class="fs-badge" id="fs-badge">0 线索</span>
        <button class="fs-close" onclick="toggleDAGFullscreen()">&#10005; 缩回</button>
      </div>
      <div id="dag-fullscreen-body">
        <svg id="dag-fullscreen-svg"><g id="dag-fullscreen-g"></g></svg>
      </div>
    `;
    document.body.appendChild(overlay);
  }
  DAG_FULLSCREEN = !DAG_FULLSCREEN;
  overlay.classList.toggle('active', DAG_FULLSCREEN);
  if (DAG_FULLSCREEN) {
    renderDAGFullscreen();
  }
}

function renderDAGFullscreen() {
  const { threads } = STATE.dag_data;
  const dagG = d3.select('#dag-fullscreen-g');
  if (!dagG.node()) return;
  dagG.selectAll('*').remove();

  if (threads.length === 0) return;

  const fsSvg = document.getElementById('dag-fullscreen-svg');
  const w = fsSvg ? fsSvg.clientWidth : 1200;
  const h = Math.max(800, threads.length * 200);
  if (fsSvg) fsSvg.setAttribute('height', h);

  const threadGap = 40;
  const nodeGap = 20;
  const nodeW = Math.min(420, w - threadGap - 40);
  const nodeH = 85;
  const threadLabelH = 24;

  let currentY = 20;
  threads.forEach((thread, ti) => {
    const threadColor = ['var(--acc)', 'var(--green)', 'var(--sky)', 'var(--goal)', 'var(--patch)'][ti % 5];

    dagG.append('rect')
      .attr('x', 20).attr('y', currentY)
      .attr('width', 8).attr('height', threadLabelH)
      .attr('rx', 4).attr('fill', threadColor);

    dagG.append('text')
      .attr('x', 36).attr('y', currentY + 18)
      .attr('fill', threadColor).attr('font-size', '12px').attr('font-weight', '600')
      .text('线索 ' + (ti + 1) + ': ' + getThreadKeywords(thread));

    currentY += threadLabelH + 12;

    thread.qa_pairs.forEach((qa, qi) => {
      qa._fsX = threadGap + nodeW / 2;
      qa._fsY = currentY + nodeH / 2;
      currentY += nodeH + nodeGap;
    });
    currentY += 25;

    // 边
    thread.qa_pairs.forEach((qa, qi) => {
      if (qi < thread.qa_pairs.length - 1) {
        const nextQA = thread.qa_pairs[qi + 1];
        dagG.append('path')
          .attr('d', `M${qa._fsX},${qa._fsY + nodeH/2 - 8} L${nextQA._fsX},${nextQA._fsY - nodeH/2 + 8}`)
          .attr('stroke', threadColor).attr('stroke-width', 2).attr('fill', 'none').attr('opacity', 0.6);
      }
    });

    // 跨线索边
    thread.qa_pairs.forEach((qa) => {
      if (qa.relation === 'REF' || qa.relation === 'INTEGRATE') {
        qa.ref_targets.forEach(targetId => {
          threads.forEach((tgtThread, tgtTi) => {
            if (tgtTi === ti) return;
            tgtThread.qa_pairs.forEach(tgtQA => {
              if (tgtQA.global_id === targetId) {
                const isRef = qa.relation === 'REF';
                dagG.append('path')
                  .attr('d', `M${qa._fsX - nodeW/2 + 5},${qa._fsY} L${tgtQA._fsX + nodeW/2 - 5},${tgtQA._fsY}`)
                  .attr('stroke', isRef ? 'var(--sky)' : 'var(--grow)')
                  .attr('stroke-width', 2)
                  .attr('stroke-dasharray', isRef ? '4,3' : '6,4')
                  .attr('fill', 'none').attr('opacity', 0.75);
              }
            });
          });
        });
      }
    });

    // 节点
    thread.qa_pairs.forEach((qa) => {
      const isQ = qa.type === 'question' || qa.type === 'user';
      const isG = qa.type === 'goal';
      const isA = qa.type === 'answer';
      const nodeClass = isG ? 'dag-node dag-node-goal' : (isQ ? 'dag-node dag-node-user' : 'dag-node dag-node-ai');
      const labelBg = isG ? 'var(--goal)' : (isQ ? 'var(--acc)' : 'var(--green)');
      const labelText = qa.global_id || (isG ? 'G' : (isQ ? 'Q' : 'A'));

      const g = dagG.append('g')
        .attr('transform', `translate(${qa._fsX},${qa._fsY})`)
        .style('cursor', 'pointer')
        .on('click', () => highlightHistory(qa.hist_idx));

      g.append('rect')
        .attr('x', -nodeW / 2).attr('y', -nodeH / 2)
        .attr('width', nodeW).attr('height', nodeH)
        .attr('rx', 8).attr('class', nodeClass);

      g.append('rect')
        .attr('x', -nodeW / 2 + 6).attr('y', -nodeH / 2 + 6)
        .attr('width', 34).attr('height', 20).attr('rx', 4)
        .attr('fill', labelBg);

      g.append('text')
        .attr('x', -nodeW / 2 + 23).attr('y', -nodeH / 2 + 20)
        .attr('text-anchor', 'middle').attr('class', 'dag-badge').attr('font-size', '11px')
        .text(labelText);

      const txt = (qa.content || '').slice(0, 45);
      g.append('text')
        .attr('x', -nodeW / 2 + 48).attr('y', -nodeH / 2 + 20)
        .attr('class', 'dag-label').attr('font-size', '11px')
        .text(txt + ((qa.content||'').length > 45 ? '…' : ''));

      if ((qa.content||'').length > 45) {
        const line2 = (qa.content || '').slice(45, 80);
        g.append('text')
          .attr('x', -nodeW / 2 + 10).attr('y', -nodeH / 2 + 38)
          .attr('class', 'dag-label').attr('font-size', '9px').attr('fill', 'var(--txt2)')
          .text(line2 + ((qa.content||'').length > 80 ? '…' : ''));
      }
    });
  });

  const totalNodes = threads.reduce((sum, t) => sum + t.qa_pairs.length, 0);
  const fsBadge = document.getElementById('fs-badge');
  if (fsBadge) fsBadge.textContent = threads.length + ' 线索 · ' + totalNodes + ' 节点';
}"""

if old_toggledag in content:
    content = content.replace(old_toggledag, new_toggledag)
    print("[OK] toggleDAG + fullscreen added")
else:
    print("[WARN] toggleDAG old text not found, skipping")


# ═══════════════════════════════════════════════════════════════
# 6. 更新帮助文档（添加关系类型示例）
# ═══════════════════════════════════════════════════════════════
old_help = """          <div class="help-section-title">&#128279; 右侧对话关系链（苏格拉底拓扑）</div>
          <div class="help-item"><strong>节点</strong>：Q=问题, A=回答，点击节点跳转对应对话</div>
          <div class="help-item"><strong>关系类型</strong>：问答/引用/整合/诘辩（T3.1诘辩涌现定理）</div>
          <div class="help-item"><strong>折叠</strong>：点击&#9660;按钮折叠/展开对话关系链</div>"""

new_help = """          <div class="help-section-title">&#128279; 右侧对话关系链（苏格拉底拓扑）</div>
          <div class="help-item"><strong>节点</strong>：Q=问题, A=回答，点击节点跳转对应对话</div>
          <div class="help-item"><strong>关系类型</strong>：问答/引用/整合/诘辩（T3.1诘辩涌现定理）</div>
          <div class="help-item"><strong>引用(REF)</strong>："问题Q3的观察者尺度参数是什么意思" → 追问Q3</div>
          <div class="help-item"><strong>整合(INTEGRATE)</strong>："将前面三个回答整合为一个论文" → 链接A1+A2+A3</div>
          <div class="help-item"><strong>诘辩(ELENCHUS)</strong>："何以见得？请证明" → 苏格拉底式追问</div>
          <div class="help-item"><strong>折叠</strong>：点击&#9660;按钮折叠/展开对话关系链</div>
          <div class="help-item"><strong>全屏</strong>：点击&#9974;按钮全屏查看对话关系链</div>"""

if old_help in content:
    content = content.replace(old_help, new_help)
    print("[OK] help text updated")
else:
    print("[WARN] help text old text not found, skipping")


# ═══════════════════════════════════════════════════════════════
# 保存
# ═══════════════════════════════════════════════════════════════
with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone. File saved:", FILE)
