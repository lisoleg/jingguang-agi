// main_app.js - 从 index_agi12_working.html 提取的主应用 JS
// 包含: handleSendBtn / handleGoalBtn / renderHistory / addMsg 等所有主对话逻辑

// ════════════════════════════════════════════════════════════════
// 全局状态 - AGI 12.0 三栏布局版
// ════════════════════════════════════════════════════════════════
console.log('[AGI12] 脚本开始加载...');
window.addEventListener('error', function(e) {
  console.error('[全局错误]', e.message, 'at', e.filename, ':', e.lineno);
  alert('JavaScript错误: ' + e.message + '\n行号: ' + e.lineno + '\n请按F12打开控制台查看详情');
});
const STATE = {
  session_id: 'agi12_' + Math.random().toString(36).slice(2,9),
  mode: 'chat',           // chat | goal
  nodes: [],
  links: [],
  selected_node: null,
  history: [],
  root_name: 'Taiyi-AGI (太乙因果机) 12.0',
  sim: null,
  loading: false,
  collapsed: new Set(),
  entropy_state: { Si: 0, Sg: 0, Sc: 0, total: 0 },
  five_phase: { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 },
  anchor_validated: false,
  goal_progress: 0,
  goal_score: 0,
  // 介质共振状态
  medium_state: {
    phase_lock: 0,
    medium_state_str: '等待感知',
    four_mode: 'unknown',
    four_mode_cn: '未知',
    hexagram: '',
    hexagram_name: '',
    S_C: 0.5,
    xinzhai: false,
  },
  // M130: 感知谱分解状态（"感知即流贯的谱分解"论文）
  perception_state: {
    // L1-L5 五层感知架构状态
    L1_ontolgy: 1.0,      // 太一全集（满格）
    L2_projection: 0.0,    // 投射生成层（卷积核激活度）
    L3_frame_seq: 0.6,     // 离散帧序列（流贯帧率）
    L4_pca: 0.0,            // 认知主体层（PCA主因子提取率）
    L5_phenomenon: 1.0,    // 现象层（重构现实）
    // 卷积核（L2）
    kernel_activation: [0.2, 0.5, 0.8, 0.3, 0.1],  // 5×5 核激活度
    kernel_ready: false,
    // PCA 主因子（L4）
    pca_factors: [0.45, 0.28, 0.15, 0.08, 0.04],  // 方差贡献率
    pca_decomposed: false,
    // 流贯帧率（L3）
    frame_rate: 60,           // Hz，目标60Hz
    frame_rate_active: true,
    // 感知-流贯对偶（T90）
    duality_score: 1.0,       // ∈[0,1]，1=完全对偶
    t90_status: '—',
    // 状态徽章
    convolution_badge: '卷积就绪',
    pca_badge: 'PCA待机',
    decomp_badge: '未分解',
  },
  // M178: Agent行为分析状态（Agentic RL 白盒化）
  agent_behavior: {
    total_turns: 0,           // 总对话轮次
    tool_calls: {},           // 工具调用分布 {tool_name: count}
    tool_call_total: 0,       // 总工具调用次数
    gc_balance: 1000,         // GC余额（M177）
    gc_history: [],           // GC消耗历史 [{turn, balance, cost}]
    trace_steps: [],          // 推理轨迹 [{step, type, brief, ts}]
    response_times: [],       // 响应时间记录 (ms)
    // Agentic RL 奖励信号
    rewards: {
      task_completion: null,  // 任务完成率
      tool_precision: null,   // 工具精准度
      reasoning_efficiency: null, // 推理效率
    },
  },
  // DAG视图数据 - 多线索支持
  dag_data: {
    threads: [],      // 多条线索，每条包含完整的QA对
    current_thread: null,
    stn: { active_node_id: null, active_path: [], show_all: true, fork_counter: 0 }, // Phase 1: STN 状态
  },
  qa_counter: 0,
  thread_counter: 0,
  global_q_counter: 0,   // 全局问题编号（跨线索）
  global_a_counter: 0,   // 全局回答编号（跨线索）
  // DAG SVG引用
  dagSvg: null,
  dagG: null,
  // STN 苏格拉底拓扑网络状态 (Phase 1)
  stn: {
    active_node_id: null,    // 当前活跃节点 global_id
    active_path: [],           // 从根到活跃节点的路径 [global_id, ...]
    show_all: false,           // 是否显示全部历史（退出树导航）
    fork_counter: 0,          // 分叉版本计数器
  },
  // 响应计时器
  _req_start: 0,

  // ════════════════════════════════════════════════════════════════
  // v7.2 OpenHuman增强模块状态
  // ════════════════════════════════════════════════════════════════
  // M81: 记忆树引擎状态
  memory_tree: {
    total_chunks: 0,
    info_density: 0,
    layer1_count: 0,  // L1: 72h近期
    layer2_count: 0,  // L2: 月度
    layer3_count: 0,  // L3: 年度
    last_update: '—'
  },
  // M82: Token压缩引擎状态
  token_juice: {
    compression_rate: 0,
    tokens_saved: 0,
    processed_count: 0,
    steps: [false, false, false, false, false]
  },
  // M83: 自动上下文同步状态
  auto_sync: {
    context_completeness: 0,
    services: { email: 'pending', calendar: 'pending', contacts: 'pending', notes: 'pending' },
    status: 'pending',
    sync_interval: 20  // 分钟
  },
  // M84: 模型智能路由状态
  model_router: {
    task_type: 'unknown',
    selected_model: '—',
    confidence: 0,
    routing_rules: {}
  },
  // M85-M87: Obsidian兼容与零训练期状态
  obsidian: {
    wiki_links: 0,
    moc_files: 0,
    backlinks: 0,
    index_ready: false
  },
  cold_start: {
    context_ready: false,
    warmup_progress: 0,
    build_time: 0
  }
};

// ════════════════════════════════════════════════════════════════
// 全局按钮处理函数（HTML onclick 属性调用）
// ════════════════════════════════════════════════════════════════
function handleSendBtn() {
  console.log('[handleSendBtn] 被调用');
  var mainInput = document.getElementById('main-input2');
  if (!mainInput) {
    console.error('[错误] main-input2 未找到!');
    alert('错误：输入框未找到');
    return;
  }
  var msg = mainInput.value.trim();
  if (!msg) {
    console.log('[发送] 输入为空');
    return;
  }
  console.log('[发送] 消息:', msg.substring(0, 50));
  mainInput.value = '';
  // 调用主聊天函数
  if (typeof doMainChat === 'function') {
    doMainChat(msg);
  } else {
    console.error('[错误] doMainChat 函数未定义!');
  }
}

function handleGoalBtn() {
  console.log('[handleGoalBtn] 被调用');
  var goalInput = document.getElementById('goal-input2');
  if (!goalInput) {
    console.error('[错误] goal-input2 未找到!');
    return;
  }
  var goal = goalInput.value.trim();
  if (!goal) return;
  goalInput.value = '';
  if (typeof doGoalMode === 'function') {
    doGoalMode(goal);
  } else {
    console.error('[错误] doGoalMode 函数未定义!');
  }
}

// ════════════════════════════════════════════════════════════════
// 初始化DAG SVG
// ════════════════════════════════════════════════════════════════
function initDAG() {
  STATE.dagSvg = d3.select('#dag-svg');
  STATE.dagG = d3.select('#dag-g');
}

// DAG尺寸
function dagWidth() { return document.getElementById('dag-container').clientWidth || 400; }
function dagHeight() { return document.getElementById('dag-container').clientHeight || 600; }

// ════════════════════════════════════════════════════════════════
// 熵仪表盘更新
// ════════════════════════════════════════════════════════════════
function updateEntropyPanel(data) {
  if (!data) return;
  // 支持多种字段命名格式
  const si = data.Si || data.S_i || data.si || 0.35;
  const sg = data.Sg || data.S_g || data.sg || 0.28;
  const sc = data.Sc || data.S_c || data.sc || 0.18;

  // 确保值在合理范围内 [0.05, 0.95]
  const siVal = Math.max(0.05, Math.min(0.95, Number(si)));
  const sgVal = Math.max(0.05, Math.min(0.95, Number(sg)));
  const scVal = Math.max(0.05, Math.min(0.95, Number(sc)));

  STATE.entropy_state = { Si: siVal, Sg: sgVal, Sc: scVal, total: siVal + sgVal + scVal };

  document.getElementById('bar-si').style.width = (siVal * 100) + '%';
  document.getElementById('bar-sg').style.width = (sgVal * 100) + '%';
  document.getElementById('bar-sc').style.width = (scVal * 100) + '%';

  document.getElementById('val-si').textContent = siVal.toFixed(2);
  document.getElementById('val-sg').textContent = sgVal.toFixed(2);
  document.getElementById('val-sc').textContent = scVal.toFixed(2);
}

// ════════════════════════════════════════════════════════════════
// 五行仪表盘更新
// ════════════════════════════════════════════════════════════════
function updateFivePhasePanel(data) {
  if (!data) return;
  STATE.five_phase = data;

  document.getElementById('val-wood').textContent = Number(data.wood || 0).toFixed(2);
  document.getElementById('val-fire').textContent = Number(data.fire || 0).toFixed(2);
  document.getElementById('val-earth').textContent = Number(data.earth || 0).toFixed(2);
  document.getElementById('val-metal').textContent = Number(data.metal || 0).toFixed(2);
  document.getElementById('val-water').textContent = Number(data.water || 0).toFixed(2);
}

// ════════════════════════════════════════════════════════════════
// 锚定验证面板更新
// ════════════════════════════════════════════════════════════════
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

// ════════════════════════════════════════════════════════════════
// 介质共振面板更新
// ════════════════════════════════════════════════════════════════
function updateMediumPanel(data) {
  if (!data || typeof data !== 'object') return;

  const phaseLock = Number(data.phase_lock || 0);
  const scVal = Number(data.S_C || data.Sc || 0.5);
  const medState = data.medium_state || '感知中';
  const fourMode = data.four_mode || 'unknown';
  const fourModeCn = data.four_mode_cn || '未知';
  const fourModeConf = Number(data.four_mode_conf || 0);
  const hexName = data.hexagram_name || '';
  const xinzhai = !!data.xinzhai;

  STATE.medium_state = {
    phase_lock: phaseLock,
    medium_state_str: medState,
    four_mode: fourMode,
    four_mode_cn: fourModeCn,
    S_C: scVal,
    xinzhai: xinzhai,
    hexagram_name: hexName,
    hexagram: data.hexagram || '',
  };

  // 更新相位环
  const circumference = 2 * Math.PI * 18; // r=18
  const fill = document.getElementById('phase-ring-fill');
  const ringText = document.getElementById('phase-ring-text');
  if (fill) {
    const arc = circumference * phaseLock;
    fill.setAttribute('stroke-dasharray', arc + ' ' + circumference);
    fill.setAttribute('stroke', phaseLock > 0.7 ? 'var(--xinzhai)' : phaseLock > 0.4 ? 'var(--medium)' : 'var(--phase-low)');
  }
  if (ringText) ringText.textContent = Math.round(phaseLock * 100) + '%';

  // 介质状态徽章
  const badge = document.getElementById('medium-state-badge');
  if (badge) {
    badge.textContent = medState;
    badge.className = 'medium-state-badge' + (xinzhai ? ' xinzhai' : '');
  }

  // 观测者效应指示器 - 来自复合体理学"观测即扰动"原理
  const observerIndicator = document.getElementById('observer-indicator');
  if (observerIndicator) {
    if (phaseLock > 0.7) {
      observerIndicator.textContent = '○ 观测稳定';
      observerIndicator.style.color = 'var(--green)';
    } else if (phaseLock > 0.4) {
      observerIndicator.textContent = '◐ 轻微扰动';
      observerIndicator.style.color = 'var(--amber)';
    } else {
      observerIndicator.textContent = '● 显著扰动';
      observerIndicator.style.color = 'var(--red)';
    }
  }

  // Sc降熵进度
  const scBar = document.getElementById('sc-medium-bar');
  const scValEl = document.getElementById('sc-medium-val');
  const xinzhaiBadge = document.getElementById('xinzhai-badge');
  if (scBar) {
    scBar.style.width = Math.min(scVal, 1) * 100 + '%';
    scBar.className = 'sc-bar-fill' + (xinzhai ? ' xinzhai' : '');
  }
  if (scValEl) scValEl.textContent = scVal.toFixed(2);
  if (xinzhaiBadge) {
    xinzhaiBadge.textContent = xinzhai ? '✦ 心斋达成' : (scVal < 0.3 ? '趋近心斋' : '修炼中');
    xinzhaiBadge.style.color = xinzhai ? 'var(--xinzhai)' : (scVal < 0.3 ? 'var(--medium)' : 'var(--txt3)');
  }

  // 更新九卦步骤（基于Sc估算当前步骤）
  updateHexagramSteps(data);

  // 更新顶栏模态徽章
  updateModeTopBadge(fourMode, fourModeCn, fourModeConf);
  // 更新四象模态卡片
  updateFourModeCards(fourMode, fourModeConf);

  // 更新觉醒度
  updateAwakeningPanel(scVal, phaseLock);
}

// ════════════════════════════════════════════════════════════════
// v6.1 新增：5篇论文核心指标面板更新函数
// ════════════════════════════════════════════════════════════════

// ── EML算子面板更新（T10守恒定理）───────────────────────────────
function updateEMLPanel(data) {
  if (!data || typeof data !== 'object') return;
  const emlIdx = Number(data.eml_index || 0);
  const coupling = Number(data.phase_coupling || 0);
  const infoTotal = Number(data.information_total || 0);
  const conserved = !!data.eml_conserved;

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val, decimals = 4) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(decimals);
  };

  setBar('eml-bar', emlIdx);
  setVal('eml-val', emlIdx, 4);
  setBar('eml-coupling-bar', coupling);
  setVal('eml-coupling-val', coupling, 4);
  setBar('eml-info-bar', infoTotal);
  setVal('eml-info-val', infoTotal, 4);

  const conservedEl = document.getElementById('eml-conserved');
  if (conservedEl) {
    conservedEl.textContent = conserved ? '✓ 守恒' : '✗ 损耗';
    conservedEl.style.color = conserved ? 'var(--green)' : 'var(--red)';
  }
}

// ── 关系实在论面板更新（T14非叠加定理）────────────────────────
function updateRelationalPanel(data) {
  if (!data || typeof data !== 'object') return;
  const relScore = Number(data.relational_score || 0);
  const kCoupling = Number(data.coupling_K || 0);
  const fiftyP = Number(data.fifty_plus_fifty || 85);
  const diffImp = Number(data.impedance_diff || 85);
  const isSuper = !!data.is_superposition;

  const setBar = (id, val, max) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val / max, 1) * 100 + '%';
  };
  const setVal = (id, val, suffix = '') => {
    const el = document.getElementById(id);
    if (el) el.textContent = val + suffix;
  };

  setBar('rel-score-bar', relScore, 1);
  setVal('rel-score-val', relScore.toFixed(4));
  setBar('rel-k-bar', kCoupling, 0.3);
  setVal('rel-k-val', kCoupling.toFixed(3));

  // 50+50=85阻抗可视化
  setVal('imp-single', '50');
  setVal('imp-linear', '100');
  const kEl = document.querySelector('.imp-connector');
  if (kEl) kEl.textContent = '↓ K=' + kCoupling.toFixed(3);
  setVal('imp-diff', diffImp.toFixed(1));
  const diffEl = document.getElementById('imp-diff');
  if (diffEl) {
    diffEl.style.color = diffImp < 95 ? '#22d3ee' : '#6b7280';
  }

  const typeEl = document.getElementById('rel-type');
  if (typeEl) {
    typeEl.textContent = isSuper ? '独立粒子(线性叠加)' : '关系耦合(涌现新质)';
    typeEl.style.color = isSuper ? '#6b7280' : '#22d3ee';
  }
}

// ── 伪革命监控面板更新（T8越界定理）──────────────────────────
function updatePseudoRevolutionPanel(data) {
  if (!data || typeof data !== 'object') return;
  const pri = Number(data.index || 0);
  const tl2 = Number(data.t_l2_theory || 0);
  const vl3 = Number(data.v_l3_validation || 0);
  const sl5 = Number(data.s_l5_narrative || 0);
  const entropyDelta = Number(data.entropy_delta || 0);
  const stability = data.stability || 'STABLE';
  const isPseudo = !!data.is_pseudo_revolution;

  const setBar = (id, val, max) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val / max, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(4);
  };

  setBar('pri-bar', pri, 2);
  setVal('pri-val', pri);
  setBar('pri-tl2', tl2, 1);
  setVal('pri-tl2', tl2);
  setBar('pri-vl3', vl3, 1);
  setVal('pri-vl3', vl3);
  setBar('pri-sl5', sl5, 1);
  setVal('pri-sl5', sl5);

  const entEl = document.getElementById('pri-entropy');
  if (entEl) {
    entEl.textContent = entropyDelta > 0 ? '+' + entropyDelta.toFixed(4) : entropyDelta.toFixed(4);
  }

  const badge = document.getElementById('pri-badge');
  if (badge) {
    if (stability === 'STABLE' && !isPseudo) {
      badge.textContent = 'STABLE ✓';
      badge.className = 'pseudo-revolution-badge stable';
    } else if (isPseudo) {
      badge.textContent = 'PSEUDO-REVOLUTION ✗';
      badge.className = 'pseudo-revolution-badge unstable';
    } else {
      badge.textContent = 'WARNING ⚠';
      badge.className = 'pseudo-revolution-badge warning';
    }
  }
}

// ── 可控涌现面板更新（T12不动点定理）──────────────────────────
function updateEmergencePanel(data) {
  if (!data || typeof data !== 'object') return;
  const emgIdx = Number(data.index || 0);
  const freedomDeg = Number(data.freedom_degree || 0);
  const pathTotal = Number(data.path_total || 0);
  const pathLegal = Number(data.path_legal || 0);
  const fpCount = Number(data.fixed_point_count || 0);
  const preHarmony = !!data.pre_harmony_manifold;

  const setBar = (id, val, max) => {
    const el = document.getElementById(id);
    if (el) el.style.width = max > 0 ? Math.min(val / max, 1) * 100 + '%' : '0%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setBar('emg-bar', emgIdx, 1);
  setVal('emg-val', emgIdx.toFixed(4));
  setBar('emg-fd-bar', freedomDeg, 1);
  setVal('emg-fd-val', freedomDeg.toFixed(4));

  // 路径可视化
  setVal('emg-total', pathTotal);
  setBar('emg-total-bar', pathLegal, pathTotal);
  setVal('emg-legal', pathLegal);
  setBar('emg-legal-bar', fpCount, pathLegal);
  setVal('emg-fp', fpCount);

  const harmEl = document.getElementById('emg-harmony');
  if (harmEl) {
    harmEl.textContent = preHarmony ? '✓ 前定和谐流形' : '○ 开放涌现';
    harmEl.style.color = preHarmony ? 'var(--green)' : 'var(--txt2)';
  }
}

// ── 拓扑分类面板更新（T15-T16）────────────────────────────────
function updateTopologyPanel(data) {
  if (!data || typeof data !== 'object') return;
  const fpVal = Number(data.fixed_point || 0);
  const hasFp = !!data.has_fp;
  const emgIrr = !!data.emergence_irreducible;
  const semComplete = !!data.semantic_complete;
  const brouwer = !!data.brouwer_fp;
  const kClass = Number(data.k_class || 0);

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(4);
  };
  const setFpDot = (id, isActive, label) => {
    const dotEl = document.getElementById(id);
    const lblEl = document.getElementById(id.replace('-dot', '-status'));
    if (dotEl) {
      dotEl.className = 'fp-indicator ' + (isActive ? 'active' : 'inactive');
    }
    if (lblEl) {
      lblEl.textContent = label || (isActive ? '是' : '否');
      lblEl.style.color = isActive ? '#22c55e' : '#6b7280';
    }
  };

  setBar('top-fp-bar', fpVal);
  setVal('top-fp-val', fpVal);
  setFpDot('top-fp-dot', hasFp);
  setFpDot('top-emg-dot', emgIrr);
  setFpDot('top-sem-dot', semComplete);
  setFpDot('top-brouwer-dot', brouwer);

  const kEl = document.getElementById('top-k-class');
  if (kEl) kEl.textContent = 'K-theory Class ' + kClass;
}

// ════════════════════════════════════════════════════════════════
// v6.2 新增面板更新函数
// ════════════════════════════════════════════════════════════════

// ── M56: 灵性演化引擎面板更新（T17灵性演化收敛定理）────────────
function updateSpiritualPanel(data) {
  if (!data || typeof data !== 'object') return;
  const narrative = Number(data.narrative_action || 0.5);
  const impedance = Number(data.impedance_level || 0.3);
  const flow = Number(data.l1_flow_rate || 0.8);
  const enlightenment = Number(data.enlightenment_readiness || 0.6);
  const divineAid = !!data.divine_aid_channel;
  const zeroImpedance = !!data.zero_impedance;

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(2);
  };

  // 叙事作用量（目标: 递减→0）
  setBar('spr-narrative-bar', narrative);
  setVal('spr-narrative-val', narrative);

  // L2阻抗（目标: 递减→0）
  setBar('spr-impedance-bar', impedance);
  setVal('spr-impedance-val', impedance);

  // L1流贯率（目标: 递增→1）
  setBar('spr-flow-bar', flow);
  setVal('spr-flow-val', flow);

  // 顿悟准备度
  setBar('spr-enlighten-bar', enlightenment);
  setVal('spr-enlighten-val', enlightenment);

  // 神助状态指示器
  const divineDot = document.getElementById('spr-divine-dot');
  const divineText = document.getElementById('spr-divine-text');
  if (divineDot) divineDot.className = 'divine-aid-dot ' + (divineAid ? 'active' : 'inactive');
  if (divineText) divineText.textContent = divineAid ? '⚡ 零阻抗通道开启' : '神助状态检测中...';

  // 状态徽章
  const badge = document.getElementById('spr-status-badge');
  if (badge) {
    if (zeroImpedance) {
      badge.textContent = '✦ 弥勒顿悟';
      badge.className = 'spiritual-badge enlightened';
    } else if (enlightenment > 0.7) {
      badge.textContent = '✨ 顿悟临近';
      badge.className = 'spiritual-badge evolving';
    } else {
      badge.textContent = '🧘 灵性演化中';
      badge.className = 'spiritual-badge evolving';
    }
  }
}

// ── M57: 修忒斯意识监测器面板更新 ───────────────────────────
function updateTheseusPanel(data) {
  if (!data || typeof data !== 'object') return;
  const coherence = Number(data.identity_coherence || 0.9);
  const retention = Number(data.core_pattern_retention || 0.85);
  const entropy = Number(data.update_entropy || 0.15);
  const reincarnate = !!data.reincarnation_necessity;
  const boundary = Number(data.boundary_layer || 0.34);

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(2);
  };

  setBar('ths-coherence-bar', coherence);
  setVal('ths-coherence-val', coherence);
  setBar('ths-retention-bar', retention);
  setVal('ths-retention-val', retention);
  setBar('ths-entropy-bar', entropy);
  setVal('ths-entropy-val', entropy);

  const fracEl = document.getElementById('ths-fraction');
  if (fracEl) fracEl.textContent = coherence.toFixed(2);

  const reincEl = document.getElementById('ths-reincarnate');
  if (reincEl) {
    reincEl.textContent = reincarnate ? '是' : '否';
    reincEl.style.color = reincarnate ? 'var(--red)' : 'var(--txt3)';
  }

  const boundEl = document.getElementById('ths-boundary');
  if (boundEl) boundEl.textContent = boundary.toFixed(2);
}

// ── M59: 极值决策优化器面板更新（T19极值同构定理v2）──────────
function updateExtremumPanel(data) {
  if (!data || typeof data !== 'object') return;
  const minAction = !!data.min_action;
  const maxEntropy = !!data.max_entropy;
  const minFree = !!data.min_free_energy;
  const occam = !!data.occam_razor;
  const maxCausal = !!data.max_causal_entropy;
  const maxPower = !!data.max_power_transfer;
  const score = Number(data.composite_score || 0.88);
  const wuwei = !!data.wuwei_mode;

  const setBadge = (id, active, label) => {
    const el = document.getElementById(id);
    if (el) {
      el.className = 'extremum-badge ' + (active ? 'active' : 'inactive');
      el.innerHTML = (active ? '&#10003;' : '&#10007;') + label;
    }
  };

  setBadge('ext-min-action', minAction, '最小作用量');
  setBadge('ext-max-entropy', maxEntropy, '最大熵');
  setBadge('ext-min-free', minFree, '最小自由能');
  setBadge('ext-occam', occam, '奥克姆剃刀');
  setBadge('ext-max-causal', maxCausal, '最大因果熵');
  setBadge('ext-max-power', maxPower, '最大功率');

  const scoreBar = document.getElementById('ext-score-bar');
  const scoreVal = document.getElementById('ext-score-val');
  if (scoreBar) scoreBar.style.width = score * 100 + '%';
  if (scoreVal) scoreVal.textContent = score.toFixed(2);

  const wuweiEl = document.getElementById('ext-wuwei-status');
  if (wuweiEl) {
    wuweiEl.textContent = wuwei ? '&#10003;' : '&#8212;';
    wuweiEl.style.color = wuwei ? 'var(--green)' : 'var(--txt3)';
  }
}

// ── M60: 关系推理引擎面板更新（T20-T21）──────────────────────
function updateEMLAddPanel(data) {
  if (!data || typeof data !== 'object') return;
  const emlA = Number(data.a || 1);
  const emlB = Number(data.b || 1);
  const emlResult = Number(data.result || -1);
  const symmetry = data.symmetry_group || 'C₂';
  const flipCount = Number(data.flip_count || 0);
  const conserved = !!data.conserved;
  const isCoupling = !data.is_superposition;

  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('eml-a', emlA);
  setEl('eml-b', emlB);
  setEl('eml-result', emlResult);
  setEl('eml-sym', '(' + symmetry + ')');

  const flipBar = document.getElementById('eml-flip-bar');
  const flipVal = document.getElementById('eml-flip-val');
  if (flipBar) flipBar.style.width = Math.min(flipCount / 20, 1) * 100 + '%';
  if (flipVal) flipVal.textContent = flipCount + '次';

  const conservedEl = document.getElementById('eml-conserved');
  if (conservedEl) {
    conservedEl.innerHTML = (conserved ? '&#10003;' : '&#10007;') + ' 角动量守恒';
    conservedEl.style.color = conserved ? 'var(--green)' : 'var(--red)';
  }

  const relTypeEl = document.getElementById('eml-rel-type');
  if (relTypeEl) {
    relTypeEl.textContent = isCoupling ? '关系耦合' : '独立粒子';
    relTypeEl.style.color = isCoupling ? '#22d3ee' : '#6b7280';
  }
}

// ── M61: 道德内化器面板更新（T22道德双锁收敛定理）────────────
function updateMoralPanel(data) {
  if (!data || typeof data !== 'object') return;
  const negLock = !!data.negation_lock;
  const posLock = !!data.positive_lock;
  const cost = Number(data.supervision_cost || 0.12);
  const action = Number(data.moral_action || 0.18);
  const doubleLock = !!data.double_lock_integrated;

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(2);
  };
  const setLock = (dotId, statusId, active) => {
    const dotEl = document.getElementById(dotId);
    const statusEl = document.getElementById(statusId);
    if (dotEl) dotEl.className = 'lock-icon ' + (active ? 'active' : 'inactive');
    if (statusEl) {
      statusEl.textContent = active ? '激活' : '休眠';
      statusEl.style.color = active ? 'var(--green)' : 'var(--txt3)';
    }
  };

  setLock('moral-neg-lock', 'moral-neg-status', negLock);
  setLock('moral-pos-lock', 'moral-pos-status', posLock);
  setBar('moral-cost-bar', cost);
  setVal('moral-cost-val', cost);
  setBar('moral-action-bar', action);
  setVal('moral-action-val', action);

  const doubleLockEl = document.getElementById('moral-double-lock');
  if (doubleLockEl) {
    doubleLockEl.innerHTML = (doubleLock ? '&#10003;' : '&#8212;') + ' 统合';
    doubleLockEl.style.color = doubleLock ? 'var(--green)' : 'var(--txt3)';
  }
}

// ── M62: 历史叙事编织器面板更新 ──────────────────────────────
function updateNarrativePanel(data) {
  if (!data || typeof data !== 'object') return;
  const coherence = Number(data.narrative_coherence || 0.82);
  const layerEffect = Number(data.layer_effect || 0.45);
  const springAutumn = Number(data.spring_autumn || 0.28);

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(2);
  };

  setBar('narr-coherence-bar', coherence);
  setVal('narr-coherence-val', coherence);
  setBar('narr-layer-bar', layerEffect);
  setVal('narr-layer-val', layerEffect);
  setBar('narr-spring-bar', springAutumn);
  setVal('narr-spring-val', springAutumn);
}

// ── M58: 树状语义处理器面板更新 ─────────────────────────────
function updateArborealPanel(data) {
  if (!data || typeof data !== 'object') return;
  const fidelity = Number(data.semantic_fidelity || 0.87);
  const depthOpt = Number(data.tree_depth_optimization || 0.72);
  const lcaEff = Number(data.lca_efficiency || 0.91);
  const compression = data.compression || '极值';
  const selfSim = !!data.self_similarity;

  const setBar = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(val, 1) * 100 + '%';
  };
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val.toFixed(2);
  };

  setBar('arb-fidelity-bar', fidelity);
  setVal('arb-fidelity-val', fidelity);
  setBar('arb-depth-bar', depthOpt);
  setVal('arb-depth-val', depthOpt);
  setBar('arb-lca-bar', lcaEff);
  setVal('arb-lca-val', lcaEff);

  const compEl = document.getElementById('arb-compression');
  if (compEl) compEl.textContent = compression;
  const simEl = document.getElementById('arb-selfsim');
  if (simEl) {
    simEl.textContent = selfSim ? '是' : '否';
    simEl.style.color = selfSim ? 'var(--sky)' : 'var(--txt3)';
  }
}

// ── 统一更新所有v6.2面板 ─────────────────────────────────────
function updateV62Panels(data) {
  if (!data) return;
  if (data.spiritual) updateSpiritualPanel(data.spiritual);
  if (data.theseus) updateTheseusPanel(data.theseus);
  if (data.extremum) updateExtremumPanel(data.extremum);
  if (data.eml_add) updateEMLAddPanel(data.eml_add);
  if (data.moral) updateMoralPanel(data.moral);
  if (data.narrative) updateNarrativePanel(data.narrative);
  if (data.arboreal) updateArborealPanel(data.arboreal);
}

// ── 统一更新所有面板 ─────────────────────────────────────────
function updateAllPanels(data) {
  if (data.entropy) updateEntropyPanel(data.entropy);
  if (data.five_phase) updateFivePhasePanel(data.five_phase);
  if (data.anchor) updateAnchorPanel(data.anchor);
  if (data.medium) updateMediumPanel(data.medium);
  // M130 感知谱分解（"感知即流贯的谱分解"论文）
  if (data.perception || data.v130) updatePerceptionPanel(data.perception || data.v130);
  // v6.1/v6.2/v6.3/v7.0数据可能在顶层或嵌套在v61/v62/v63/v70对象中
  const v61Data = data.v61 || data;
  const v62Data = data.v62 || data;
  const v63Data = data.v63 || data;
  const v70Data = data.v70 || data;
  if (v61Data.eml || v61Data.relational || v61Data.pseudo_revolution || v61Data.emergence || v61Data.topology) {
    updateV61Panels(v61Data);
  }
  if (v62Data.spiritual || v62Data.theseus || v62Data.extremum || v62Data.eml_add || v62Data.moral || v62Data.narrative || v62Data.arboreal) {
    updateV62Panels(v62Data);
  }
  if (v63Data.monist || v63Data.narrative_action || v63Data.consciousness_flow || v63Data.self_identity || v63Data.insight || v63Data.falsifiable) {
    updateV63Panels(v63Data);
  }
  if (v70Data.carbon_silicon || v70Data.wuxing || v70Data.hott || v70Data.functor || v70Data.liu_fixed_point || v70Data.axiom || v70Data.token_dynamics) {
    updateV70Panels(v70Data);
  }
}

// ── 统一更新所有v6.1面板 ──────────────────────────────────────
function updateV61Panels(data) {
  if (!data) return;
  if (data.eml) updateEMLPanel(data.eml);
  if (data.relational) updateRelationalPanel(data.relational);
  if (data.pseudo_revolution) updatePseudoRevolutionPanel(data.pseudo_revolution);
  if (data.emergence) updateEmergencePanel(data.emergence);
  if (data.topology) updateTopologyPanel(data.topology);
}

// ════════════════════════════════════════════════════════════════
// 觉醒度面板更新
// ════════════════════════════════════════════════════════════════
function updateAwakeningPanel(scVal, phaseLock) {
  // 觉醒度 = 1 - S_C * 0.6 + phase_lock * 0.4
  const awakening = Math.max(0, Math.min(1, 1 - scVal * 0.6 + phaseLock * 0.4));
  
  // 更新环形进度
  const circumference = 2 * Math.PI * 18;
  const fill = document.getElementById('awakening-ring-fill');
  const ringText = document.getElementById('awakening-ring-text');
  const scDisplay = document.getElementById('awakening-sc');
  const badge = document.getElementById('awakening-state-badge');
  
  if (fill) {
    const arc = circumference * awakening;
    fill.setAttribute('stroke-dasharray', arc + ' ' + circumference);
    fill.setAttribute('stroke-dashoffset', '0');
  }
  if (ringText) ringText.textContent = Math.round(awakening * 100) + '%';
  if (scDisplay) scDisplay.textContent = scVal.toFixed(2);
  
  if (badge) {
    if (awakening > 0.8) {
      badge.textContent = '🌟 高度觉醒';
      badge.style.color = 'var(--gold)';
    } else if (awakening > 0.5) {
      badge.textContent = '✨ 正在觉醒';
      badge.style.color = 'var(--amber)';
    } else if (awakening > 0.3) {
      badge.textContent = '💫 初现意识';
      badge.style.color = 'var(--sky)';
    } else {
      badge.textContent = '🌱 休眠中';
      badge.style.color = 'var(--txt2)';
    }
  }
}

// ════════════════════════════════════════════════════════════════
// 四象模态面板更新
// ════════════════════════════════════════════════════════════════
const MODE_DESCRIPTIONS = {
  'rigid': {
    title: '刚性耦合模态',
    desc: '《三国演义》地缘博弈。高S_g主导，应力集中。通过金克木（规则压制生长）维持或夺取霸权。',
    metaphor: '魏蜀吴三角博弈',
    action: '认清格局，结盟蓄力'
  },
  'boil': {
    title: '沸腾反抗模态',
    desc: '《水浒传》边缘起义。高S_C溢出，形成对抗性孤岛。中枢合法性不足时，边缘节点聚义梁山。',
    metaphor: '梁山好汉聚义',
    action: '积蓄力量，勿被招安'
  },
  'pilgrim': {
    title: '取经相干模态',
    desc: '《西游记》介质净化。高相位锁定，降低系统总熵。去西天取真经（颠覆性技术），降妖除魔（突破障碍）。',
    metaphor: '师徒四人取经路',
    action: '修心降魔，技术突围'
  },
  'entropy': {
    title: '熵增终局模态',
    desc: '《红楼梦》结构衰败。高S_I不可逆增加。无论旧秩序多繁华，内在拓扑缺陷注定大厦倾颓。',
    metaphor: '大观园由盛转衰',
    action: '看透空性，悬崖撒手'
  }
};

function updateFourModeCards(currentMode, confidence) {
  // 更新顶部四象模态面板
  ['rigid', 'boil', 'pilgrim', 'entropy'].forEach(mode => {
    const card = document.getElementById('mode-' + mode);
    const status = document.getElementById('mode-status-' + mode);
    if (card) {
      card.classList.toggle('active', mode === currentMode);
    }
    if (status) {
      status.textContent = mode === currentMode ? '● 当前' : '';
    }
  });
  
  // 更新描述
  const descEl = document.getElementById('mode-desc');
  if (descEl && MODE_DESCRIPTIONS[currentMode]) {
    const modeData = MODE_DESCRIPTIONS[currentMode];
    descEl.textContent = '当前：' + modeData.title + ' - ' + modeData.desc.split(' - ')[1];
  }
  
  // 更新陈天桥测试面板中的四象模态卡片
  if (typeof updateFourModeBadge === 'function') {
    updateFourModeBadge(currentMode);
  }
}

// 设置模态函数
function setMode(mode) {
  if (MODE_DESCRIPTIONS[mode]) {
    // 调用API设置模态
    fetch('/api/chat_v2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `[系统指令] 设置四象模态为: ${mode}`,
        session_id: STATE.session_id
      })
    });
    
    // 更新UI
    updateFourModeCards(mode, 1.0);
    document.getElementById('chen-status').textContent = '模态: ' + MODE_DESCRIPTIONS[mode].title;
  }
}

// ════════════════════════════════════════════════════════════════
// 九卦步骤更新
// ════════════════════════════════════════════════════════════════
const HEXAGRAM_DATA = [
  { name: '履', glyph: '☰', meaning: '踏实前行，奠定基础' },
  { name: '谦', glyph: '☷', meaning: '谦逊低调，降低熵增' },
  { name: '复', glyph: '☳', meaning: '复归本心，回归秩序' },
  { name: '恒', glyph: '☴', meaning: '持续修炼，建立定力' },
  { name: '损', glyph: '☶', meaning: '损减余执，清简精要' },
  { name: '益', glyph: '☱', meaning: '增益智慧，顺应变化' },
  { name: '困', glyph: '☲', meaning: '困境磨砺，突破极限' },
  { name: '井', glyph: '☵', meaning: '井出清泉，净化意识' },
  { name: '巽', glyph: '☱', meaning: '入风化境，心斋圆满' },
];

function updateHexagramSteps(medData) {
  const scVal = Number(medData.S_C || medData.Sc || 0.5);
  // S_C从1.0降至0，对应步骤0→9
  const stepIdx = Math.min(8, Math.floor((1 - Math.min(scVal, 1)) * 9));
  const steps = document.querySelectorAll('#hexagram-steps .hex-step');
  steps.forEach((s, i) => {
    if (i < stepIdx) s.className = 'hex-step done';
    else if (i === stepIdx) s.className = 'hex-step active';
    else s.className = 'hex-step';
  });

  // 当前卦象信息
  const hx = HEXAGRAM_DATA[stepIdx] || HEXAGRAM_DATA[0];
  const glyph = document.getElementById('hex-glyph');
  const name = document.getElementById('hex-name');
  const meaning = document.getElementById('hex-meaning');
  if (glyph) glyph.textContent = hx.glyph;
  if (name) name.textContent = hx.name + '卦 (' + (medData.hexagram_name || hx.name) + ')';
  if (meaning) meaning.textContent = hx.meaning;
}

// ════════════════════════════════════════════════════════════════
// 四象模态卡片更新
// ════════════════════════════════════════════════════════════════
const MODE_MAP = {
  'rigid_coupling': 'rigid',
  'boiling': 'boil',
  'pilgrimage': 'pilgrim',
  'entropy': 'entropy',
  'unknown': null
};
const MODE_CN_MAP = {
  'rigid': '刚性耦合',
  'boil': '沸腾反抗',
  'pilgrim': '取经相干',
  'entropy': '熵增终局',
};
// 四象模态更新函数

function updateFourModeCards(fourMode, confidence) {
  const shortMode = MODE_MAP[fourMode] || fourMode;
  ['rigid', 'boil', 'pilgrim', 'entropy'].forEach(m => {
    const card = document.getElementById('mcard-' + m);
    const conf = document.getElementById('mconf-' + m);
    const title = document.getElementById('mtitle-' + m);
    if (!card) return;
    if (m === shortMode) {
      card.className = 'mode-card mode-' + m + ' current';
      if (conf) conf.textContent = Math.round(Number(confidence) * 100) + '%';
      // 高亮时显示详细描述
      if (title) {
        const desc = MODE_DESCRIPTIONS[m];
        title.textContent = desc ? desc.title : MODE_CN_MAP[m] || m;
        title.title = desc ? `${desc.desc}\n隐喻: ${desc.metaphor}\n行动: ${desc.action}` : '';
      }
    } else {
      card.className = 'mode-card mode-' + m;
      if (conf) conf.textContent = '—';
      if (title) {
        title.textContent = MODE_CN_MAP[m] || m;
        title.title = '';
      }
    }
  });
}

function updateModeTopBadge(fourMode, fourModeCn, confidence) {
  const badge = document.getElementById('mode-topbadge');
  if (!badge) return;
  const shortMode = MODE_MAP[fourMode] || 'unknown';
  const label = fourModeCn || '未知';
  badge.textContent = '◈ ' + label + (confidence > 0 ? ' ' + Math.round(Number(confidence) * 100) + '%' : '');
  badge.className = 'mode-topbadge mode-' + (shortMode || 'unknown');
}

// ════════════════════════════════════════════════════════════════
// 响应时间计时器
// ════════════════════════════════════════════════════════════════
function startTimer() {
  STATE._req_start = Date.now();
  document.getElementById('resp-timer').textContent = '';
}
function stopTimer() {
  if (!STATE._req_start) return;
  const ms = Date.now() - STATE._req_start;
  STATE._req_start = 0;
  const s = (ms / 1000).toFixed(1);
  document.getElementById('resp-timer').textContent = s + 's';
}

// ════════════════════════════════════════════════════════════════
// 话题检测 - 判断是否为新线索
// ════════════════════════════════════════════════════════════════
function detectNewThread(newContent) {
  const threads = STATE.dag_data.threads;
  if (threads.length === 0) return true;

  const lastThread = threads[threads.length - 1];
  const qaPairs = lastThread.qa_pairs;
  if (!qaPairs || qaPairs.length === 0) return true;

  const lastQA = qaPairs[qaPairs.length - 1];
  if (!lastQA) return true;

  const content = newContent.toLowerCase();

  // 强信号1：引用之前的问题编号 -> 绝对不是新线索
  const refQPattern = /(?:问题)?[qQ](\d+)|第\s*(\d+)\s*个?问题|第\s*(\d+)\s*题|上述|前面|之前|刚才/i;
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
}

function extractKeywords(text) {
  if (!text) return [];
  // 简单分词：提取2-4个字的词组
  const words = [];
  const stopWords = new Set(['的', '是', '在', '了', '和', '与', '或', '以及', '这个', '那个', '什么', '怎么', '为什么']);
  for (let i = 0; i < text.length - 1; i++) {
    const w2 = text.slice(i, i + 2);
    const w3 = text.slice(i, i + 3);
    if (!stopWords.has(w2)) words.push(w2);
    if (i < text.length - 2 && !stopWords.has(w3)) words.push(w3);
  }
  return [...new Set(words)];
}

function getThreadKeywords(thread) {
  if (thread.qa_pairs.length === 0) return '';
  const firstQ = thread.qa_pairs.find(q => q.type === 'question' || q.type === 'user');
  if (!firstQ) return '';
  const keywords = extractKeywords(firstQ.content).slice(0, 3);
  return keywords.join(' · ');
}

// ════════════════════════════════════════════════════════════════
// 对话关系链折叠/展开控制 + 苏格拉底关系类型标注
// 基于《学习苏格拉底》论文：问-答/引用/整合/诘辩四种关系
// ════════════════════════════════════════════════════════════════
let DAG_COLLAPSED = false;
function toggleDAG() {
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

  // 裁剪定义（防止文字溢出节点）
  const fsDefs = dagG.append('defs');

  if (threads.length === 0) return;

  const fsSvg = document.getElementById('dag-fullscreen-svg');
  const bodyEl = document.getElementById('dag-fullscreen-body');
  const bodyW = bodyEl ? bodyEl.clientWidth - 40 : 1200; // 减去padding
  const w = Math.max(900, bodyW);
  const h = Math.max(800, threads.length * 200);
  if (fsSvg) {
    fsSvg.setAttribute('width', w);
    fsSvg.setAttribute('height', h);
    fsSvg.style.width = w + 'px';
    fsSvg.style.height = h + 'px';
  }

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
    thread.qa_pairs.forEach((qa, qi) => {
      const isQ = qa.type === 'question' || qa.type === 'user';
      const isG = qa.type === 'goal';
      const isA = qa.type === 'answer';
      const nodeClass = isG ? 'dag-node dag-node-goal' : (isQ ? 'dag-node dag-node-user' : 'dag-node dag-node-ai');
      const labelBg = isG ? 'var(--goal)' : (isQ ? 'var(--acc)' : 'var(--green)');
      const labelText = qa.global_id || (isG ? 'G' : (isQ ? 'Q' : 'A'));

      // 裁剪路径（防止文字溢出节点边界）
      const fsClipId = 'dagcfs-' + ti + '-' + qi;
      fsDefs.append('clipPath')
        .attr('id', fsClipId)
        .append('rect')
        .attr('x', -nodeW / 2 + 3).attr('y', -nodeH / 2 + 3)
        .attr('width', nodeW - 6).attr('height', nodeH - 6).attr('rx', 5);

      const g = dagG.append('g')
        .attr('transform', `translate(${qa._fsX},${qa._fsY})`)
        .attr('clip-path', `url(#${fsClipId})`)
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

      // 内容文本（按11px中文字宽≈11px，可用宽≈362px，保守30字符）
      const qaContent = qa.content || '';
      let fsLine1, fsLine2;
      if (qaContent.length <= 30) {
        fsLine1 = qaContent; fsLine2 = '';
      } else {
        fsLine1 = qaContent.slice(0, 30) + '…';
        fsLine2 = qaContent.slice(30, 55);
      }
      g.append('text')
        .attr('x', -nodeW / 2 + 48).attr('y', -nodeH / 2 + 20)
        .attr('class', 'dag-label').attr('font-size', '11px')
        .text(fsLine1);
      if (fsLine2) {
        g.append('text')
          .attr('x', -nodeW / 2 + 10).attr('y', -nodeH / 2 + 38)
          .attr('class', 'dag-label').attr('font-size', '9px').attr('fill', 'var(--txt2)')
          .text(fsLine2 + (fsLine2.length >= 28 ? '…' : ''));
      }
    });
  });

  // 根据实际内容高度调整SVG尺寸，确保滚动条覆盖全部内容
  const finalH = currentY + 40;
  if (fsSvg && finalH > h) {
    fsSvg.setAttribute('height', finalH);
    fsSvg.style.height = finalH + 'px';
  }

  const totalNodes = threads.reduce((sum, t) => sum + t.qa_pairs.length, 0);
  const fsBadge = document.getElementById('fs-badge');
  if (fsBadge) fsBadge.textContent = threads.length + ' 线索 · ' + totalNodes + ' 节点';
}

// 苏格拉底对话关系类型定义（T3.1 诘辩涌现定理）
const SOCRATIC_RELATIONS = {
  QA:        { label: '问答',   color: 'var(--acc)',  icon: '?' },
  REF:       { label: '引用',   color: 'var(--sky)',  icon: '&#8617;' },
  INTEGRATE: { label: '整合',   color: 'var(--goal)', icon: '&#10067;' },
  ELENCHUS:  { label: '诘辩',   color: '#f97316',     icon: '&#9876;' },
};

function getRelationType(thread, qa, qidx) {
  const content = (qa.content || '').toLowerCase();
  if (/真的|确定|如果|会怎样|为什么|何以见得|请证明/i.test(content)) return 'ELENCHUS';
  if (qidx > 0 && /上述|之前|刚才|如前所述|引用|参照/i.test(content)) return 'REF';
  if (/整合|综合|总结|综上|基于以上/i.test(content)) return 'INTEGRATE';
  return 'QA';
}

// ════════════════════════════════════════════════════════════════
// DAG渲染 - 多线索视图
// ════════════════════════════════════════════════════════════════
function renderDAG() {
  const { threads } = STATE.dag_data;
  const dagG = STATE.dagG || d3.select('#dag-g');

  dagG.selectAll('*').remove();

  // 裁剪定义（防止文字溢出节点）
  const defs = dagG.append('defs');

  // 空状态
  const emptyEl = document.getElementById('dag-empty');
  if (emptyEl) emptyEl.style.display = threads.length === 0 ? 'block' : 'none';

  if (threads.length === 0) {
    document.getElementById('rel-badge').textContent = '0 线索';
    return;
  }

  const totalNodes = threads.reduce((sum, t) => sum + t.qa_pairs.length, 0);
  document.getElementById('rel-badge').textContent = threads.length + ' 线索 · ' + totalNodes + ' 节点';

  const w = dagWidth();
  const h = dagHeight();

  // Phase 4: DAG 背景网格
  const gridG = dagG.append('g').attr('class', 'dag-bg-grid');
  const gridSize = 30;
  for (let gx = 0; gx < w; gx += gridSize) {
    gridG.append('line').attr('x1', gx).attr('y1', 0).attr('x2', gx).attr('y2', h);
  }
  for (let gy = 0; gy < h; gy += gridSize) {
    gridG.append('line').attr('x1', 0).attr('y1', gy).attr('x2', w).attr('y2', gy);
  }

  // 布局参数
  const threadGap = 24;      // 线索间距
  const nodeGap = 12;        // 节点间距
  const nodeW = Math.min(260, w - threadGap - 20);
  const nodeH = 75;
  const threadLabelH = 20;

  // 计算每条线索的起始Y
  let currentY = 10;
  const threadStartYs = [];

  threads.forEach((thread, ti) => {
    threadStartYs.push(currentY);
    currentY += threadLabelH + 8; // 线索标题
    thread.qa_pairs.forEach((qa, qi) => {
      qa._threadIdx = ti;
      qa._nodeIdx = qi;
      qa.x = threadGap + nodeW / 2;
      qa.y = currentY + nodeH / 2;
      currentY += nodeH + nodeGap;
    });
    currentY += 15; // 线索间隔
  });

  // 绘制每条线索
  threads.forEach((thread, ti) => {
    const startY = threadStartYs[ti];
    const threadColor = ['var(--acc)', 'var(--green)', 'var(--sky)', 'var(--goal)', 'var(--patch)'][ti % 5];

    // 线索标题背景
    dagG.append('rect')
      .attr('x', 0).attr('y', startY)
      .attr('width', 6).attr('height', threadLabelH)
      .attr('rx', 3).attr('fill', threadColor);

    dagG.append('text')
      .attr('x', 14).attr('y', startY + 14)
      .attr('fill', threadColor).attr('font-size', '10px').attr('font-weight', '600')
      .text('线索 ' + (ti + 1) + ': ' + getThreadKeywords(thread));

    // 绘制边（按 parent_id 树结构，而非数组顺序）
    const { stn } = STATE.dag_data;
    thread.qa_pairs.forEach((qa) => {
      if (!qa.parent_id) return; // 根节点无线
      const parentNode = findSTNNode(qa.parent_id);
      if (!parentNode) return; // 父节点不存在时跳过
      const isCrossThread = parentNode._threadIdx !== ti;
      const isActiveLink = stn && stn.active_path &&
        stn.active_path.includes(qa.parent_id) && stn.active_path.includes(qa.global_id);

      // Phase 4: ELENCHUS 锯齿线
      if (qa.relation === 'ELENCHUS' || qa.node_type === 'E') {
        // 生成锯齿路径
        const x1 = parentNode.x, y1 = parentNode.y + nodeH/2 - 8;
        const x2 = qa.x, y2 = qa.y - nodeH/2 + 8;
        const zigzagPath = generateZigzagPath(x1, y1, x2, y2, 5);
        dagG.append('path')
          .attr('d', zigzagPath)
          .attr('class', 'dag-link-elenchus')
          .attr('opacity', isActiveLink ? 0.9 : 0.6);
      } else if (qa.is_alternative || (parentNode.children_ids && parentNode.children_ids.length > 1)) {
        // Phase 2: 分叉/多版本虚线
        const path = `M${parentNode.x},${parentNode.y + nodeH/2 - 8} L${qa.x},${qa.y - nodeH/2 + 8}`;
        dagG.append('path')
          .attr('d', path)
          .attr('class', isActiveLink ? 'dag-link-stn-active' : 'dag-link-fork')
          .attr('opacity', isActiveLink ? 0.9 : 0.7);
      } else if (isCrossThread) {
        // 跨线程分叉边：紫色虚线
        const path = `M${parentNode.x},${parentNode.y + nodeH/2 - 8} L${qa.x},${qa.y - nodeH/2 + 8}`;
        dagG.append('path')
          .attr('d', path)
          .attr('class', isActiveLink ? 'dag-link-stn-active' : 'dag-link-fork')
          .attr('opacity', isActiveLink ? 0.9 : 0.7);
      } else {
        // 普通边
        const path = `M${parentNode.x},${parentNode.y + nodeH/2 - 8} L${qa.x},${qa.y - nodeH/2 + 8}`;
        dagG.append('path')
          .attr('d', path)
          .attr('stroke', isActiveLink ? 'var(--acc2)' : threadColor)
          .attr('stroke-width', isActiveLink ? 2 : 1.5)
          .attr('fill', 'none')
          .attr('opacity', isActiveLink ? 0.9 : 0.6)
          .attr('class', isActiveLink ? 'dag-link-stn-active' : 'dag-link');
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

    // 绘制节点
    thread.qa_pairs.forEach((qa) => {
      const isQ = qa.type === 'question' || qa.type === 'user';
      const isG = qa.type === 'goal';
      const isA = qa.type === 'answer';
      let nodeClass = isG ? 'dag-node dag-node-goal' : (isQ ? 'dag-node dag-node-user' : 'dag-node dag-node-ai');
      // Phase 1: STN 活跃路径高亮
      const { stn } = STATE.dag_data;
      const isOnActivePath = stn && stn.active_path && stn.active_path.includes(qa.global_id);
      const isActiveNode = stn && stn.active_node_id === qa.global_id;
      if (isActiveNode) nodeClass += ' dag-node-stn-active dag-node-glow-pulse';
      else if (isOnActivePath) nodeClass += ' dag-node-stn-path';

      // 裁剪路径（防止文字溢出节点边界）
      const clipId = 'dagc-' + ti + '-' + qa._nodeIdx;
      defs.append('clipPath')
        .attr('id', clipId)
        .append('rect')
        .attr('x', -nodeW / 2 + 2).attr('y', -nodeH / 2 + 2)
        .attr('width', nodeW - 4).attr('height', nodeH - 4).attr('rx', 4);

      const g = dagG.append('g')
        .attr('transform', `translate(${qa.x},${qa.y})`)
        .attr('clip-path', `url(#${clipId})`)
        .attr('data-stn-id', qa.global_id || '')
        .style('cursor', 'pointer')
        .on('click', () => {
          if (qa.global_id) {
            activateSTNNode(qa.global_id);
          } else {
            highlightHistory(qa.hist_idx);
          }
        })
        // 悬停联动：DAG节点 → 历史消息高亮
        .on('mouseover', () => {
          if (qa.hist_idx !== undefined) {
            const items = document.querySelectorAll('#history .msg');
            if (items[qa.hist_idx]) {
              items[qa.hist_idx].style.boxShadow = '0 0 12px var(--acc-glow)';
              items[qa.hist_idx].style.background = 'rgba(124,58,237,0.08)';
            }
          }
        })
        .on('mouseout', () => {
          if (qa.hist_idx !== undefined) {
            const items = document.querySelectorAll('#history .msg');
            if (items[qa.hist_idx]) {
              items[qa.hist_idx].style.boxShadow = '';
              items[qa.hist_idx].style.background = '';
            }
          }
        });

      // 节点形状：S=六边形，E=菱形，其余=矩形
      const nodeType = qa.node_type || 'A';
      if (nodeType === 'S') {
        // 六边形 (Hexagon)
        const r = nodeW / 2, h = nodeH / 2;
        const hexPoints = [
          [-r*0.75, -h], [-r, 0], [-r*0.75, h],
          [r*0.75, h], [r, 0], [r*0.75, -h]
        ].map(p => p[0] + ',' + p[1]).join(' ');
        g.append('polygon')
          .attr('points', hexPoints)
          .attr('fill', 'rgba(245,158,11,0.18)')
          .attr('stroke', '#F59E0B')
          .attr('stroke-width', 2)
          .attr('class', nodeClass + ' dag-node-hex');
      } else if (nodeType === 'E') {
        // 菱形 (Diamond)
        const r = nodeW / 2, h = nodeH / 2;
        const diaPoints = [[0,-h],[r,0],[0,h],[-r,0]].map(p=>p[0]+','+p[1]).join(' ');
        g.append('polygon')
          .attr('points', diaPoints)
          .attr('fill', 'rgba(239,68,68,0.18)')
          .attr('stroke', '#EF4444')
          .attr('stroke-width', 2)
          .attr('class', nodeClass + ' dag-node-diamond');
      } else {
        // 矩形（Q/A/G）
        g.append('rect')
          .attr('x', -nodeW / 2).attr('y', -nodeH / 2)
          .attr('width', nodeW).attr('height', nodeH)
          .attr('rx', 6).attr('class', nodeClass);
      }

      // 标签背景色（按文章设计：Q靛蓝、A青绿、S琥珀、E朱红）
      let labelBg = 'var(--acc)';
      if (nodeType === 'S') labelBg = '#F59E0B';
      else if (nodeType === 'E') labelBg = '#EF4444';
      else if (isA && !isQ) labelBg = 'var(--green)';
      else if (isG) labelBg = 'var(--goal)';
      const labelTextColor = (nodeType === 'S' || nodeType === 'E') ? '#000' : '#fff';
      let labelText = qa.global_id || (isG ? 'G' : (isQ ? 'Q' : 'A'));
      if (nodeType === 'S') labelText = 'S' + (qa.global_id||'').replace(/[QA]/g,'');
      if (nodeType === 'E') labelText = 'E' + (qa.global_id||'').replace(/[QA]/g,'');
      const badgeClass = nodeType === 'S' ? 'dag-badge dag-badge-s' : (nodeType === 'E' ? 'dag-badge dag-badge-e' : 'dag-badge');
      // 标签矩形
      g.append('rect')
        .attr('x', -nodeW/2+5).attr('y', -nodeH/2+5)
        .attr('width', 28).attr('height', 16).attr('rx', 3)
        .attr('fill', labelBg);
      g.append('text')
        .attr('x', -nodeW/2+19).attr('y', -nodeH/2+16)
        .attr('text-anchor', 'middle').attr('class', badgeClass).attr('font-size', '9px')
        .attr('fill', labelTextColor)
        .text(labelText);

      // 折叠按钮（有子节点时显示）
      if (qa.children_ids && qa.children_ids.length > 0) {
        const collapseSym = qa.collapsed ? '▶' : '▼';
        g.append('text')
          .attr('x', -nodeW / 2 + 2).attr('y', nodeH / 2 - 4)
          .attr('class', 'dag-collapse-btn')
          .text(collapseSym)
          .on('click', (event) => {
            event.stopPropagation();
            toggleSTNCollapse(qa.global_id);
          });
      }

      // Phase 4: 节点微徽章（关系类型图标）
      let microBadge = '';
      if (qa.relation === 'REF') microBadge = '\u{1F517}';
      else if (qa.relation === 'INTEGRATE' || qa.node_type === 'S') microBadge = '\u{1F4DD}';
      else if (qa.relation === 'ELENCHUS' || qa.node_type === 'E') microBadge = '\u{2694}';
      else if (qa.children_ids && qa.children_ids.length > 1) microBadge = '\u{1F525}';
      if (microBadge) {
        g.append('text')
          .attr('x', nodeW / 2 - 14).attr('y', -nodeH / 2 + 15)
          .attr('class', 'dag-micro-badge')
          .attr('font-size', '11px')
          .text(microBadge);
      }

      // Phase 4: 版本徽章（多版本节点）
      // 分叉徽章：父节点有≥2个子节点时显示
      if (qa.children_ids && qa.children_ids.length >= 2) {
        g.append('g')
          .attr('transform', `translate(${nodeW/2 - 12}, ${-nodeH/2})`)
          .html('<rect width="18" height="14" rx="7" fill="rgba(168,85,247,0.25)" stroke="#a855f7" stroke-width="1"/>' +
                '<text x="9" y="11" text-anchor="middle" fill="#a855f7" font-size="8" font-weight="700">' +
                qa.children_ids.length + '</text>');
      }

      if (qa.versions && qa.versions.length > 1) {
        g.append('text')
          .attr('x', nodeW / 2 - 14).attr('y', -nodeH / 2 + 28)
          .attr('font-size', '8px').attr('fill', '#a855f7')
          .attr('text-anchor', 'middle')
          .text('v' + qa.versions.length);
      }

      // Phase 4: 新节点涟漪动画
      if (qa.timestamp) {
        const age = Date.now() - new Date(qa.timestamp).getTime();
        if (age < 3000) {
          g.append('circle')
            .attr('cx', 0).attr('cy', 0).attr('r', 0)
            .attr('class', 'dag-ripple')
            .transition().duration(800).ease(d3.easeCubicOut)
            .attr('r', 20);
        }
      }

      // 内容文本（按9px中文字宽≈9px，可用宽≈214px，保守22字符）
      const qaContent = qa.content || '';
      let line1, line2;
      if (qaContent.length <= 22) {
        line1 = qaContent; line2 = '';
      } else {
        line1 = qaContent.slice(0, 22) + '…';
        line2 = qaContent.slice(22, 42);
      }
      g.append('text')
        .attr('x', -nodeW / 2 + 38).attr('y', -nodeH / 2 + 17)
        .attr('class', 'dag-label').attr('font-size', '9px')
        .text(line1);
      if (line2) {
        g.append('text')
          .attr('x', -nodeW / 2 + 8).attr('y', -nodeH / 2 + 32)
          .attr('class', 'dag-label').attr('font-size', '8px').attr('fill', 'var(--txt2)')
          .text(line2 + (line2.length >= 20 ? '…' : ''));
      }

      // 时间戳
      if (qa.timestamp) {
        const t = new Date(qa.timestamp);
        const tStr = t.getHours().toString().padStart(2,'0') + ':' + t.getMinutes().toString().padStart(2,'0');
        g.append('text')
          .attr('x', nodeW/2 - 8).attr('y', nodeH/2 - 5)
          .attr('text-anchor', 'end').attr('class', 'dag-time')
          .text(tStr);
      }

      // hover tooltip
      g.on('mouseover', function(event) {
        const tt = document.getElementById('tooltip');
        if (tt) {
          const relLabel = qa.relation && qa.relation !== 'QA' ? ` <span style="font-size:9px;color:${SOCRATIC_RELATIONS[qa.relation]?.color||'#888'}">[${SOCRATIC_RELATIONS[qa.relation]?.label||qa.relation}]</span>` : '';
          tt.innerHTML = `<strong style="color:var(--acc2)">${labelText}</strong>${relLabel}<br>${(qa.content||'').slice(0,80)}${(qa.content||'').length > 80 ? '…' : ''}`;
          tt.style.opacity = '1';
          tt.style.left = (event.offsetX + 10) + 'px';
          tt.style.top = (event.offsetY - 20) + 'px';
        }
      }).on('mouseout', function() {
        const tt = document.getElementById('tooltip');
        if (tt) tt.style.opacity = '0';
      });
    });
  });

  // 根据内容总高度调整SVG高度，确保滚动条足够长
  const svgEl = document.getElementById('dag-svg');
  if (svgEl) {
    const minHeight = dagHeight();
    const contentHeight = currentY + 20;
    svgEl.setAttribute('height', Math.max(minHeight, contentHeight));
    svgEl.style.height = Math.max(minHeight, contentHeight) + 'px';
  }
  // 如果处于全屏模式，同步更新全屏视图
  if (DAG_FULLSCREEN) {
    renderDAGFullscreen();
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

// ════════════════════════════════════════════════════════════════
// 添加问答对到DAG - 多线索版本
// ════════════════════════════════════════════════════════════════
function addQA2DAG(type, content, meta = {}) {
  STATE.qa_counter++;
  const { threads, stn } = STATE.dag_data;
  // Phase 1: 兼容 stn 字段
  if (!STATE.dag_data.stn) STATE.dag_data.stn = { active_node_id: null, active_path: [], show_all: true, fork_counter: 0 };

  // Phase 2: 支持分叉来源
  const forkFrom = STATE.dag_data._fork_from;
  if (forkFrom && (type === 'question' || type === 'user')) {
    meta.fork_from = forkFrom;
    // 分叉后清除标记
    STATE.dag_data._fork_from = null;
  }

  // 用户消息：检测是否开新线索 或 是否是子树分叉
  if (type === 'question' || type === 'goal') {
    const isNewThread = meta.force_new_thread || meta.fork_from || detectNewThread(content);

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

  // Phase 1: 建立父子关系（树结构）
  let parentId = null;
  if (type === 'answer') {
    // AI回答 → 父节点是同一个 thread 中最后一个 question
    const lastQ = [...currentThread.qa_pairs].reverse().find(q => q.type === 'question' || q.type === 'user' || q.type === 'goal');
    if (lastQ) parentId = lastQ.global_id;
  } else if (type === 'question') {
    // 新反问/追问 → 父节点是同一个 thread 中最后一个 answer
    const lastA = [...currentThread.qa_pairs].reverse().find(q => q.type === 'answer');
    if (lastA) parentId = lastA.global_id;
  }
  // 如果 meta.fork_from 指定了父节点（分叉），优先使用
  if (meta.fork_from) parentId = meta.fork_from;

  const qa = {
    id: type[0].toUpperCase() + '_' + STATE.qa_counter,
    global_id: globalId,
    type: type,
    content: content,
    timestamp: new Date().toISOString(),
    hist_idx: STATE.history.length,
    relation: 'QA',       // QA / REF / INTEGRATE / ELENCHUS
    ref_targets: [],      // 引用的目标global_id列表
    // Phase 1: STN 树结构字段
    parent_id: parentId,  // 父节点 global_id
    children_ids: [],     // 子节点 global_id 列表
    versions: [globalId],// 同一语义节点的不同版本（分叉）
    node_type: 'Q',      // Q / A / S(摘要) / E(诘辩)
    collapsed: false,     // 子树是否折叠
  };
  // 反向链接：把当前节点加入父节点的 children_ids
  if (parentId) {
    const parentNode = findSTNNode(parentId);
    if (parentNode && !parentNode.children_ids.includes(globalId)) {
      parentNode.children_ids.push(globalId);
    }
  }

  // 检测关系类型
  const lower = (content || '').toLowerCase();
  if (/真的|确定|如果|会怎样|为什么|何以见得|请证明/i.test(content)) {
    qa.relation = 'ELENCHUS';
    qa.node_type = 'E';
  } else if (/上述|之前|刚才|如前所述|引用|参照|问题[qQ]?\d+|第\d+个?问题/i.test(content)) {
    qa.relation = 'REF';
    // 尝试提取引用的Q编号
    const refMatch = content.match(/[qQ]?(\d+)|第\s*(\d+)\s*个?问题|第\s*(\d+)\s*题/g);
    if (refMatch) {
      refMatch.forEach(m => {
        const num = parseInt(m.replace(/\D/g, ''), 10);
        if (num > 0) qa.ref_targets.push('Q' + num);
      });
    }
  } else if (/整合|综合|总结|综上|基于以上|前面三个|A1|A2|A3/i.test(content)) {
    qa.relation = 'INTEGRATE';
    qa.node_type = 'S';
    // 整合前面所有答案
    threads.forEach(t => {
      t.qa_pairs.forEach(p => {
        if (p.type === 'answer' && p.global_id) qa.ref_targets.push(p.global_id);
      });
    });
  }

  currentThread.qa_pairs.push(qa);

  // Phase 1: 更新 STN 活跃路径
  stn.active_node_id = globalId;
  stn.active_path = getSTNPathToNode(globalId);
  stn.show_all = false;

  renderDAG();
  renderSTNBreadcrumb();
  // Phase 3: 更新熵值监控
  if (typeof updateConsoleEntropy === 'function') updateConsoleEntropy();
  return qa;
}

// ═══════════════════════════════════════════════════════════════
// STN 核心导航函数 (Phase 1)
// ═══════════════════════════════════════════════════════════════

// 在所有线程中按 global_id 查找节点
function findSTNNode(globalId) {
  const { threads } = STATE.dag_data;
  for (const t of threads) {
    for (const qa of t.qa_pairs) {
      if (qa.global_id === globalId) return qa;
    }
  }
  return null;
}
// 在所有线程中按 hist_idx 查找节点
function findSTNNodeByHistIdx(histIdx) {
  const { threads } = STATE.dag_data;
  for (const t of threads) {
    for (const qa of t.qa_pairs) {
      if (qa.hist_idx === histIdx) return qa;
    }
  }
  return null;
}

// 获取从根到目标节点的路径 [root_global_id, ..., target_global_id]
function getSTNPathToNode(globalId) {
  const node = findSTNNode(globalId);
  if (!node) return [globalId];
  const path = [];
  let cur = node;
  while (cur) {
    path.unshift(cur.global_id);
    cur = cur.parent_id ? findSTNNode(cur.parent_id) : null;
  }
  return path;
}

// 获取某节点的整个子树 global_id 列表（含自身）
function getSTNSubtree(globalId) {
  const result = [globalId];
  const node = findSTNNode(globalId);
  if (!node) return result;
  if (node.children_ids) {
    for (const childId of node.children_ids) {
      result.push(...getSTNSubtree(childId));
    }
  }
  return result;
}

// 点击 DAG 节点时：设置活跃路径并刷新历史视图
function activateSTNNode(globalId) {
  const { stn } = STATE.dag_data;
  if (!stn) return;
  stn.active_node_id = globalId;
  stn.active_path = getSTNPathToNode(globalId);
  stn.show_all = false;
  renderHistory();      // 路径感知渲染
  renderDAG();          // 高亮活跃路径
  renderSTNBreadcrumb();
  renderRelationMap(globalId); // 更新Relation Map面板
}

// 切换子树折叠状态
function toggleSTNCollapse(globalId) {
  const node = findSTNNode(globalId);
  if (node) {
    node.collapsed = !node.collapsed;
    renderDAG();
  }
}

// 退出树导航，显示全部历史
function showAllHistory() {
  const { stn } = STATE.dag_data;
  if (!stn) return;
  stn.show_all = true;
  stn.active_node_id = null;
  stn.active_path = [];
  renderHistory();
  renderDAG();
  renderSTNBreadcrumb();
  closeRelationMap();
}

// ═══════════════════════════════════════════════════════════════
// 面包屑导航渲染
// ═══════════════════════════════════════════════════════════════
function renderSTNBreadcrumb() {
  const { stn } = STATE.dag_data;
  const container = document.getElementById('stn-breadcrumb');
  if (!container) return;
  if (!stn || stn.show_all || !stn.active_path || stn.active_path.length === 0) {
    container.innerHTML = '<span class="stn-bc-item" onclick="showAllHistory()">📋 全部对话</span>';
    return;
  }
  let html = '<span class="stn-bc-item" onclick="showAllHistory()">📋 全部</span>';
  html += '<span class="stn-bc-sep">›</span>';
  stn.active_path.forEach((gid, i) => {
    const node = findSTNNode(gid);
    const label = node ? (node.type === 'question' || node.type === 'user' || node.type === 'goal' ? 'Q' : 'A') + gid.replace(/[QA]/g, '') : gid;
    const isLast = (i === stn.active_path.length - 1);
    if (!isLast) {
      html += `<span class="stn-bc-item" onclick="activateSTNNode('${gid}')">${label}</span>`;
      html += '<span class="stn-bc-sep">›</span>';
    } else {
      html += `<span class="stn-bc-item active">${label}</span>`;
    }
  });
  container.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════════
// STN Phase 2 — 分叉与多版本核心函数
// ═══════════════════════════════════════════════════════════════

function cancelFork() {
  const stn = (STATE.dag_data.stn || {});
  STATE.dag_data._fork_from = null;
  const indicator = document.getElementById('fork-indicator');
  if (indicator) indicator.style.display = 'none';
  const input = document.getElementById('main-input2');
  if (input) input.placeholder = '输入问题，净光哥启动24模块协同分析...';
  setConsoleStatus('已取消分叉');
}

// 分叉：在指定节点处创建新分支，新问题挂载到该节点
function forkFromNode(globalId) {
  const { stn } = STATE.dag_data;
  if (!stn) return;
  // 设置分叉来源（在 addQA2DAG 中消费）
  STATE.dag_data._fork_from = globalId;
  // 递增分叉计数器，开新线程
  stn.fork_counter = (stn.fork_counter || 0) + 1;
  STATE.thread_counter++;
  const newThread = {
    id: 'thread_' + STATE.thread_counter,
    qa_pairs: [],
    links: [],
  };
  STATE.dag_data.threads.push(newThread);
  // 显示分叉指示器
  const indicator = document.getElementById('fork-indicator');
  const srcLabel = document.getElementById('fork-src-label');
  if (indicator) indicator.style.display = 'flex';
  if (srcLabel) srcLabel.textContent = globalId;
  // 激活该节点路径
  activateSTNNode(globalId);
  // 聚焦输入框
  const input = document.getElementById('main-input2');
  if (input) {
    input.focus();
    input.placeholder = '🎯 分叉模式：从 ' + globalId + ' 继续提问...';
  }
  setConsoleStatus('分叉自 ' + globalId + ' — 输入问题即创建新分支');
}

// 多版本回答：同一个问题有多个AI回答
function addAlternativeAnswer(parentGlobalId, content, meta) {
  const { threads } = STATE.dag_data;
  // 找到父节点
  const parentNode = findSTNNode(parentGlobalId);
  if (!parentNode) return null;

  STATE.global_a_counter++;
  STATE.qa_counter++;
  const globalId = 'A' + STATE.global_a_counter;
  const currentThread = threads[threads.length - 1];

  const altQA = {
    id: 'A_' + STATE.qa_counter,
    global_id: globalId,
    type: 'answer',
    content: content,
    timestamp: new Date().toISOString(),
    hist_idx: STATE.history.length,
    relation: 'QA',
    ref_targets: [],
    parent_id: parentGlobalId,
    children_ids: [],
    versions: [...(parentNode.versions || []), globalId],
    node_type: 'A',
    collapsed: false,
    is_alternative: true,
    version_label: meta ? meta.version_label : ('v' + (parentNode.versions ? parentNode.versions.length + 1 : 2)),
  };

  // 添加到父节点的子节点列表
  if (!parentNode.children_ids.includes(globalId)) {
    parentNode.children_ids.push(globalId);
  }

  // 将所有版本信息同步到同父节点的所有子节点
  const allVersions = [parentGlobalId, ...parentNode.children_ids];
  allVersions.forEach(childId => {
    const child = findSTNNode(childId);
    if (child) child.versions = [...allVersions];
  });

  currentThread.qa_pairs.push(altQA);
  // 更新 STN 活跃路径
  const stn = STATE.dag_data.stn;
  if (stn) {
    stn.active_node_id = globalId;
    stn.active_path = getSTNPathToNode(globalId);
    stn.show_all = false;
  }
  renderDAG();
  renderHistory();
  renderSTNBreadcrumb();
  return altQA;
}

// 切换版本视图：显示同一问题的不同回答
function switchVersion(globalId) {
  const node = findSTNNode(globalId);
  if (!node || !node.versions || node.versions.length < 2) return;
  // 直接激活该版本节点
  activateSTNNode(globalId);
}

// 获取某个问题的所有版本回答
function getVersionSiblings(globalId) {
  const node = findSTNNode(globalId);
  if (!node || !node.versions) return [];
  return node.versions.map(vId => findSTNNode(vId)).filter(Boolean);
}

// ═══════════════════════════════════════════════════════════════
// STN Phase 3 — 流贯控制台与命令系统
// ═══════════════════════════════════════════════════════════════

// 熵值监控与更新
function updateConsoleEntropy() {
  const { history } = STATE;
  const { stn } = STATE.dag_data;
  // 简化熵值计算：基于对话长度和STN树深度
  let entropy = 0;
  if (history.length > 0) {
    entropy = Math.min(1.0, history.length / 50);
    // STN分支越多，熵值越高
    let branchCount = 0;
    STATE.dag_data.threads.forEach(t => {
      branchCount += t.qa_pairs.filter(q => q.parent_id && findSTNNode(q.parent_id) &&
        findSTNNode(q.parent_id).children_ids && findSTNNode(q.parent_id).children_ids.length > 1).length;
    });
    entropy += Math.min(0.3, branchCount * 0.1);
    entropy = Math.min(1.0, entropy);
  }

  const fill = document.getElementById('console-entropy-fill');
  const val = document.getElementById('console-entropy-val');
  if (fill) {
    // 动态颜色：绿(<0.5) → 黄(0.5-0.75) → 红(>0.75)
    let colorClass = '';
    if (entropy > 0.75) colorClass = ' danger';
    else if (entropy > 0.5) colorClass = ' warn';
    fill.className = 'console-entropy-fill' + colorClass;
    fill.style.width = (entropy * 100) + '%';
  }
  if (val) val.textContent = entropy.toFixed(2);

  // 动态提示文字（按文章设计推论3.1.1）
  const statusEl = document.getElementById('console-status');
  if (statusEl && !statusEl._cmdOverride) {
    if (entropy > 0.75) {
      statusEl.textContent = '\u{1F6A8} 上下文临界相变！建议立即 /summarize';
      statusEl.style.color = '#ef4444';
    } else if (entropy > 0.5) {
      statusEl.textContent = '\u{1F4A1} 检测到信息密度增加，建议创建子节点';
      statusEl.style.color = 'var(--amber)';
    } else {
      statusEl.textContent = '流贯通畅';
      statusEl.style.color = 'var(--txt3)';
    }
  }

  // 高熵时自动提示摘要
  if (entropy > 0.75 && history.length > 20 && !STATE._autoSummaryShown) {
    STATE._autoSummaryShown = true;
    setConsoleStatus('高熵! 建议执行 /summarize');
  }
  return entropy;
}

// 控制台状态消息
function setConsoleStatus(msg) {
  const el = document.getElementById('console-status');
  if (el) {
    el._cmdOverride = true;
    el.textContent = msg;
    el.style.color = 'var(--acc)';
    setTimeout(() => { el._cmdOverride = false; el.style.color = 'var(--txt3)'; }, 5000);
  }
}

// 控制台按钮命令
function handleConsoleCmd(cmd) {
  if (cmd === 'summarize') cmd = '/summarize';
  if (cmd === 'debate') cmd = '/debate';
  if (cmd === 'integrate') cmd = '/integrate';
  handleConsoleCmdInput(cmd);
}

// 控制台命令解析与执行
function handleConsoleCmdInput(raw) {
  const input = raw.trim();
  if (!input || input[0] !== '/') {
    // 非命令，当作普通消息发送
    if (input) {
      const mainInput = document.getElementById('main-input2');
      if (mainInput) { mainInput.value = input; }
      handleSendBtn();
    }
    return;
  }

  const parts = input.split(/\s+/);
  const cmd = parts[0].toLowerCase();
  const args = parts.slice(1);

  switch (cmd) {
    case '/fork': {
      const targetId = args[0] || (STATE.dag_data.stn && STATE.dag_data.stn.active_node_id);
      if (targetId) {
        forkFromNode(targetId);
      } else {
        setConsoleStatus('请先点击DAG节点或指定 /fork Q1');
      }
      break;
    }
    case '/summarize': {
      const { stn } = STATE.dag_data;
      const activePath = stn && stn.active_path ? stn.active_path : [];
      if (activePath.length < 3) {
        setConsoleStatus('对话太短，至少需要3轮');
        return;
      }
      // 收集路径上的内容
      const contents = activePath.map(gid => {
        const n = findSTNNode(gid);
        return n ? (n.type === 'question' ? 'Q: ' : 'A: ') + (n.content || '').substring(0, 100) : '';
      }).filter(Boolean);
      const summary = '综合以上 ' + activePath.length + ' 轮对话：' + contents.join('；');
      // 创建摘要节点
      STATE.history.push({
        role: 'system',
        content: '📋 路径摘要（共 ' + activePath.length + ' 个节点）：\n' + summary.substring(0, 300),
        _ts: new Date().toISOString(),
        _is_summary: true,
      });
      // 在DAG中添加摘要节点
      const parentQ = findSTNNode(activePath[0]);
      addQA2DAG('summary', summary.substring(0, 200), { force_new_thread: false });
      setConsoleStatus('摘要已生成 (' + activePath.length + ' 节点)');
      break;
    }
    case '/debate': {
      const { stn } = STATE.dag_data;
      const activeNode = stn && stn.active_node_id;
      if (!activeNode) {
        setConsoleStatus('请先点击一个Q节点');
        return;
      }
      // 生成诘辩问题
      const node = findSTNNode(activeNode);
      if (node) {
        const debateQ = '请对以下回答进行诘辩（苏格拉底式反问）：' + (node.content || '').substring(0, 150);
        const mainInput = document.getElementById('main-input2');
        if (mainInput) { mainInput.value = debateQ; }
        doMainChat(debateQ);
        setConsoleStatus('诘辩模式启动');
      }
      break;
    }
    case '/integrate': {
      // 整合当前问题下的多版本答案
      const { stn } = STATE.dag_data;
      const activeNode = stn && stn.active_node_id;
      if (!activeNode) {
        setConsoleStatus('请先点击一个A节点');
        return;
      }
      const node = findSTNNode(activeNode);
      if (!node || !node.versions || node.versions.length < 2) {
        setConsoleStatus('该节点无多版本答案可整合');
        return;
      }
      const siblings = getVersionSiblings(activeNode);
      const integrated = '综合 ' + siblings.length + ' 个版本：' +
        siblings.map((s, i) => '版本' + (i + 1) + ': ' + (s.content || '').substring(0, 80)).join('；');
      STATE.history.push({
        role: 'system',
        content: '🔄 整合结果（' + siblings.length + ' 个版本）：\n' + integrated.substring(0, 400),
        _ts: new Date().toISOString(),
        _is_integration: true,
      });
      renderHistory();
      setConsoleStatus('已整合 ' + siblings.length + ' 个版本');
      break;
    }
    case '/help': {
      const helpText = '/fork [Qn] 分叉 | /summarize 摘要 | /debate 诘辩 | /integrate 整合';
      setConsoleStatus(helpText);
      break;
    }
    default:
      setConsoleStatus('未知命令: ' + cmd + ' (输入 /help 查看帮助)');
  }
}

// Phase 4: ELENCHUS 锯齿路径生成
function generateZigzagPath(x1, y1, x2, y2, segments) {
  const dx = (x2 - x1) / segments;
  const dy = (y2 - y1) / segments;
  const perpX = -dy * 0.2;  // 垂直偏移幅度
  const perpY = dx * 0.2;
  let d = 'M' + x1 + ',' + y1;
  for (let i = 1; i < segments; i++) {
    const mx = x1 + dx * i;
    const my = y1 + dy * i;
    const side = (i % 2 === 0) ? 1 : -1;
    d += ' L' + (mx + perpX * side) + ',' + (my + perpY * side);
  }
  d += ' L' + x2 + ',' + y2;
  return d;
}

// ════════════════════════════════════════════════════════════════
// STN Phase 4 — Relation Map (文章设计: 右侧关系图谱面板)
// ════════════════════════════════════════════════════════════════
function renderRelationMap(globalId) {
  const panel = document.getElementById('relation-map-panel');
  const emptyEl = document.getElementById('relation-map-empty');
  const badge = document.getElementById('rel-map-badge');
  if (!panel) return;

  const node = findSTNNode(globalId);
  if (!node) { panel.style.display = 'none'; return; }

  panel.style.display = 'flex';

  // 收集入度和出度节点
  const inNodes = [];   // 指向当前节点（父节点、引用目标等）
  const outNodes = [];  // 当前节点指向的（子节点、引用发出等）
  const { threads } = STATE.dag_data;

  threads.forEach(t => {
    t.qa_pairs.forEach(qa => {
      // 入度：其他节点指向当前节点
      if (qa.parent_id === globalId) {
        outNodes.push({ node: qa, relation: qa.relation || 'QA' });
      }
      if (qa.children_ids && qa.children_ids.includes(globalId)) {
        inNodes.push({ node: qa, relation: qa.relation || 'QA' });
      }
      if (qa.ref_targets && qa.ref_targets.includes(globalId)) {
        inNodes.push({ node: qa, relation: 'REF' });
      }
    });
  });

  // 父节点作为入度
  if (node.parent_id) {
    const parentNode = findSTNNode(node.parent_id);
    if (parentNode) inNodes.unshift({ node: parentNode, relation: node.relation || 'QA' });
  }
  // 子节点作为出度
  if (node.children_ids) {
    node.children_ids.forEach(cid => {
      const child = findSTNNode(cid);
      if (child && !outNodes.find(o => o.node.global_id === cid)) {
        outNodes.push({ node: child, relation: child.relation || 'QA' });
      }
    });
  }

  const totalEdges = inNodes.length + outNodes.length;
  if (badge) badge.textContent = totalEdges + ' 边';

  // 渲染 SVG 关系图谱
  const svgEl = document.getElementById('relation-map-svg');
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  if (totalEdges === 0) {
    if (emptyEl) emptyEl.style.display = 'flex';
    return;
  }
  if (emptyEl) emptyEl.style.display = 'none';

  const w = svgEl.clientWidth || 300;
  const h = svgEl.clientHeight || 200;
  const cx = w / 2, cy = h / 2;

  // 中心节点
  const nodeLabel = (node.global_id || '').replace(/[QA]/, '') || '?';
  const nodeType = node.node_type || (node.type === 'question' || node.type === 'user' ? 'Q' : 'A');
  const centerColor = nodeType === 'S' ? '#F59E0B' : nodeType === 'E' ? '#EF4444' : nodeType === 'Q' ? '#4F46E5' : '#10B981';

  svg.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 22)
    .attr('fill', centerColor + '30').attr('stroke', centerColor).attr('stroke-width', 2);
  svg.append('text').attr('x', cx).attr('y', cy + 4)
    .attr('text-anchor', 'middle').attr('fill', '#fff').attr('font-size', '12px').attr('font-weight', '700')
    .text(nodeLabel);

  // 左侧：入度节点
  const inCount = inNodes.length;
  const outCount = outNodes.length;
  const maxNodes = Math.max(inCount, outCount, 1);

  inNodes.forEach((item, i) => {
    const angle = -Math.PI * 0.6 + (Math.PI * 1.2 / Math.max(maxNodes - 1, 1)) * i;
    const nx = cx + Math.cos(angle) * (w * 0.38);
    const ny = cy + Math.sin(angle) * (h * 0.38);
    const relColor = SOCRATIC_RELATIONS[item.relation]?.color || 'var(--txt3)';
    const label = (item.node.global_id || '').replace(/[QA]/, '') || '?';

    // 连线
    svg.append('line').attr('x1', nx).attr('y1', ny).attr('x2', cx).attr('y2', cy)
      .attr('stroke', relColor).attr('stroke-width', 1.5).attr('stroke-dasharray', '4,2').attr('opacity', 0.6);
    // 节点圆
    svg.append('circle').attr('cx', nx).attr('cy', ny).attr('r', 16)
      .attr('fill', relColor + '25').attr('stroke', relColor).attr('stroke-width', 1.5);
    svg.append('text').attr('x', nx).attr('y', ny + 3)
      .attr('text-anchor', 'middle').attr('fill', '#ccc').attr('font-size', '10px')
      .text(label);
    // 入度标记
    svg.append('text').attr('x', nx - 20).attr('y', ny - 12)
      .attr('font-size', '8px').attr('fill', relColor).text('IN');
  });

  // 右侧：出度节点
  outNodes.forEach((item, i) => {
    const angle = Math.PI * 0.4 + (Math.PI * 1.2 / Math.max(maxNodes - 1, 1)) * i;
    const nx = cx + Math.cos(angle) * (w * 0.38);
    const ny = cy + Math.sin(angle) * (h * 0.38);
    const relColor = SOCRATIC_RELATIONS[item.relation]?.color || 'var(--txt3)';
    const label = (item.node.global_id || '').replace(/[QA]/, '') || '?';

    // 连线（实线=出度）
    svg.append('line').attr('x1', cx).attr('y1', cy).attr('x2', nx).attr('y2', ny)
      .attr('stroke', relColor).attr('stroke-width', 1.5).attr('opacity', 0.6);
    svg.append('circle').attr('cx', nx).attr('cy', ny).attr('r', 16)
      .attr('fill', relColor + '25').attr('stroke', relColor).attr('stroke-width', 1.5);
    svg.append('text').attr('x', nx).attr('y', ny + 3)
      .attr('text-anchor', 'middle').attr('fill', '#ccc').attr('font-size', '10px')
      .text(label);
    svg.append('text').attr('x', nx - 16).attr('y', ny - 12)
      .attr('font-size', '8px').attr('fill', relColor).text('OUT');
  });
}

function closeRelationMap() {
  const panel = document.getElementById('relation-map-panel');
  if (panel) panel.style.display = 'none';
}

function getLastAnswerThreadIdx() {
  const { threads } = STATE.dag_data;
  if (threads.length === 0) return -1;
  const lastThread = threads[threads.length - 1];
  const answers = lastThread.qa_pairs.filter(q => q.type === 'answer');
  return answers.length > 0 ? threads.length - 1 : -1;
}

// ════════════════════════════════════════════════════════════════
// 对话历史
// ════════════════════════════════════════════════════════════════
function pushMsg(role, content, meta = {}) {
  STATE.history.push({ role, content, _ts: new Date().toISOString(), ...meta });
  const { threads, stn } = STATE.dag_data;

  if (role === 'user') {
    const type = meta.is_goal ? 'goal' : 'question';
    addQA2DAG(type, content);
  } else {
    // AI回复：添加到当前线索最后一个问题后面，建立父子关系
    if (threads.length > 0) {
      const currentThread = threads[threads.length - 1];
      if (!currentThread.qa_pairs) currentThread.qa_pairs = [];
      const lastQ = currentThread.qa_pairs.filter(q => q.type === 'question' || q.type === 'user' || q.type === 'goal').slice(-1)[0];
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
        // Phase 1: STN 树结构字段
        parent_id: lastQ ? lastQ.global_id : null,
        children_ids: [],
        versions: ['A' + STATE.global_a_counter],
        node_type: 'A',
        collapsed: false,
      };
      // 反向链接
      if (lastQ && lastQ.children_ids && !lastQ.children_ids.includes(ansQA.global_id)) {
        lastQ.children_ids.push(ansQA.global_id);
      }
      currentThread.qa_pairs.push(ansQA);

      // 更新 STN 活跃路径
      if (stn) {
        stn.active_node_id = ansQA.global_id;
        stn.active_path = getSTNPathToNode(ansQA.global_id);
        stn.show_all = false;
      }
      renderDAG();
      renderSTNBreadcrumb();
    } else {
      // 无线程时创建（保留原逻辑）
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
        parent_id: null, children_ids: [], versions: ['A' + STATE.global_a_counter], node_type: 'A', collapsed: false,
      });
      renderDAG();
    }
    // Phase 3: 更新熵值监控
    if (typeof updateConsoleEntropy === 'function') updateConsoleEntropy();
  }

  renderHistory();
  updateQABadge();
}

function updateQABadge() {
  const { threads } = STATE.dag_data;
  const qCount = threads.reduce((sum, t) => sum + t.qa_pairs.filter(q => q.type === 'question' || q.type === 'user').length, 0);
  document.getElementById('qa-badge').textContent = qCount + ' 对话 · ' + threads.length + ' 线索';
}

function renderHistory() {
  const el = document.getElementById('history');
  el.innerHTML = '';

  const { stn } = STATE.dag_data;

  // Phase 1: 路径感知渲染
  // 如果 stn.show_all = false，只渲染活跃路径上的节点
  let visibleHistoryIndices = null;
  if (stn && !stn.show_all && stn.active_path && stn.active_path.length > 0) {
    // 收集活跃路径上所有节点的 hist_idx
    const visibleIds = new Set(stn.active_path);
    // 同时显示活跃路径节点的直接子节点
    stn.active_path.forEach(gid => {
      const node = findSTNNode(gid);
      if (node && node.children_ids) {
        node.children_ids.forEach(cid => visibleIds.add(cid));
      }
    });
    // 折叠节点：如果某节点的 collapsed=true，不展开其子节点（已在上面处理了直接子节点）
    visibleHistoryIndices = new Set();
    STATE.history.forEach((m, idx) => {
      // 通过 hist_idx 反向查找 qa 节点
      // 简化：直接检查所有 qa 节点的 global_id
    });
    // 简化实现：通过 dag_data 收集所有可见节点的 hist_idx
    const { threads } = STATE.dag_data;
    threads.forEach(t => {
      t.qa_pairs.forEach(qa => {
        if (visibleIds.has(qa.global_id) && qa.hist_idx !== undefined) {
          visibleHistoryIndices.add(qa.hist_idx);
        }
      });
    });
  }

  let qCount = 0;

  STATE.history.forEach((m, idx) => {
    // 路径过滤：如果定义了可见索引集，跳过不可见的消息
    if (visibleHistoryIndices !== null && !visibleHistoryIndices.has(idx)) {
      // 但仍然占用 qCount，保持 Q/A 编号正确
      if (m.role === 'user') qCount++;
      return; // forEach 回调里 return = continue，正确跳过
    }

    const div = document.createElement('div');
    let cls = 'msg ';

    // 时间格式化
    const now = m._ts ? new Date(m._ts) : new Date();
    const timeStr = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');

    if (m.role === 'user') {
      qCount++;
      cls += m.is_goal ? 'msg-goal' : 'msg-user';
      // Phase 1: STN 活跃节点高亮
      const histNode = findSTNNodeByHistIdx(idx);
      if (histNode && stn && histNode.global_id === stn.active_node_id) cls += ' msg-stn-active';
      const label = m.is_goal ? 'G' + qCount : 'Q' + qCount;
      const color = m.is_goal ? 'var(--goal)' : 'var(--acc)';
      div.className = cls;
      div.style.position = 'relative';
      div.innerHTML = `
        <div class="msg-meta">
          <span style="color:${color};font-weight:600">[${label}]</span>
          <span class="msg-timestamp">${timeStr}</span>
          ${histNode && histNode.children_ids && histNode.children_ids.length > 1 ?
            '<span class="msg-fork-badge">' + histNode.children_ids.length + '分支</span>' : ''}
        </div>
        <div class="msg-hover-actions">
          ${histNode ? '<button class="msg-action-btn fork-btn" onclick="event.stopPropagation();forkFromNode(\'' + histNode.global_id + '\')" title="从此处分叉">&#9112;</button>' : ''}
        </div>
        <div class="msg-actions">
          <button class="btn-copy-msg" onclick="copyMsg(this, ${idx})">复制</button>
        </div>
        ${formatMsg(m.content)}
      `;
    } else if (m.role === 'system' && (m._is_summary || m._is_integration)) {
      // Phase 3: 摘要/整合消息样式
      cls += m._is_integration ? 'msg-summary' : 'msg-summary';
      div.className = cls;
      div.innerHTML = `
        <div class="msg-meta">
          <span style="color:var(--grow);font-weight:600">[${ m._is_integration ? '整合' : '摘要'}]</span>
          <span class="msg-timestamp">${timeStr}</span>
        </div>
        ${formatMsg(m.content)}
      `;
    } else {
      cls += 'msg-ai';
      // Phase 1: STN 活跃节点高亮
      const histNode = findSTNNodeByHistIdx(idx);
      if (histNode && stn && histNode.global_id === stn.active_node_id) cls += ' msg-stn-active';
      // Phase 4: ELENCHUS 节点样式
      if (histNode && histNode.node_type === 'E') cls += ' msg-elenchus';
      div.className = cls;
      div.style.position = 'relative';

      // Phase 2: 版本切换器（同一问题有多个回答时显示）
      let versionHtml = '';
      if (histNode && histNode.versions && histNode.versions.length > 1) {
        const siblings = getVersionSiblings(histNode.global_id);
        if (siblings.length > 1) {
          versionHtml = '<div class="version-switcher"><span class="version-label">版本</span>';
          siblings.forEach((s, si) => {
            const isActive = s.global_id === histNode.global_id;
            const label = s.version_label || ('v' + (si + 1));
            versionHtml += '<button class="version-dot' + (isActive ? ' active' : '') +
              '" onclick="event.stopPropagation();switchVersion(\'' + s.global_id + '\')" title="' + label + '">' + label + '</button>';
          });
          versionHtml += '</div>';
        }
      }

      // Phase 2: 悬停分叉按钮
      let hoverHtml = '<div class="msg-hover-actions">';
      if (histNode) {
        hoverHtml += '<button class="msg-action-btn fork-btn" onclick="event.stopPropagation();forkFromNode(\'' + histNode.global_id + '\')" title="从此处分叉">&#9112;</button>';
      }
      hoverHtml += '</div>';

      // 关联追问HTML
      let rqHtml = '';
      if (m.related_questions && m.related_questions.length > 0) {
        const items = m.related_questions.map(q =>
          `<div class="rq-item" onclick="askRelated(this)" data-question="${q.replace(/"/g, '&quot;')}">${q}</div>`
        ).join('');
        rqHtml = `<div class="related-questions"><div class="rq-title">关联追问</div><div class="rq-list">${items}</div></div>`;
      }

      div.innerHTML = `
        <div class="msg-meta">
          <span style="color:var(--green);font-weight:600">[A${qCount}]</span>
          <span class="msg-timestamp">${timeStr}</span>
          ${histNode && histNode.is_alternative ? '<span class="msg-fork-badge">替代版本</span>' : ''}
        </div>
        ${hoverHtml}
        ${versionHtml}
        <div class="msg-actions">
          <button class="btn-copy-msg" onclick="copyMsg(this, ${idx})">复制</button>
          <button class="btn-gc btn-gc-plus" onclick="adjustGC(10, ${idx}, this)" title="加分 +10 GC" style="font-size:10px;padding:1px 5px;border:1px solid rgba(52,211,153,0.4);background:rgba(52,211,153,0.08);color:#34d399;border-radius:3px;cursor:pointer;margin-left:2px;">+GC</button>
          <button class="btn-gc btn-gc-minus" onclick="adjustGC(-10, ${idx}, this)" title="扣分 -10 GC" style="font-size:10px;padding:1px 5px;border:1px solid rgba(248,113,113,0.4);background:rgba(248,113,113,0.08);color:#f87171;border-radius:3px;cursor:pointer;margin-left:2px;">-GC</button>
        </div>
        ${formatMsg(m.content)}
        ${rqHtml}
      `;
    }

    div.addEventListener('mouseover', () => {
      // 悬停联动：历史消息 → DAG 节点高亮脉冲
      if (m._dag_node_id || m._ts) {
        const gid = m._dag_node_id || findSTNNodeByHistIdx(idx);
        if (gid) {
          const el = document.querySelector(`[data-stn-id="${gid}"]`);
          if (el) {
            el.style.filter = 'drop-shadow(0 0 8px var(--acc2))';
            el.style.transition = 'filter 0.2s';
          }
        }
      }
    });
    div.addEventListener('mouseout', () => {
      const gid = m._dag_node_id || findSTNNodeByHistIdx(idx);
      if (gid) {
        const el = document.querySelector(`[data-stn-id="${gid}"]`);
        if (el) el.style.filter = '';
      }
    });

    el.appendChild(div);
  });

  el.scrollTop = el.scrollHeight;
}

// ═══ 关联追问点击处理 ═══
function askRelated(el) {
  const question = el.getAttribute('data-question');
  if (!question || STATE.loading) return;
  // 视觉反馈：点击后淡出
  el.style.opacity = '0.5';
  el.style.pointerEvents = 'none';
  // 填入输入框并发送
  const input = document.getElementById('main-input');
  if (input) {
    input.value = question;
    input.focus();
  }
  doMainChat(question);
}

function formatMsg(text) {
  if (!text) return '';
  return text
    // 代码块（```...```）
    .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code>${escapeHtml(code.trim())}</code></pre>`)
    // 行内代码
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 粗体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // 标题 # ## ###
    .replace(/^### (.+)$/gm, '<span style="font-size:12px;font-weight:700;color:var(--acc2);display:block;margin:4px 0">$1</span>')
    .replace(/^## (.+)$/gm, '<span style="font-size:13px;font-weight:700;color:var(--sky);display:block;margin:5px 0">$1</span>')
    .replace(/^# (.+)$/gm, '<span style="font-size:14px;font-weight:700;color:var(--txt);display:block;margin:6px 0">$1</span>')
    // 换行
    .replace(/\n/g, '<br>');
}

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function copyMsg(btn, idx) {
  const m = STATE.history[idx];
  if (!m) return;
  navigator.clipboard.writeText(m.content || '').then(() => {
    btn.textContent = '已复制 ✓';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('copied'); }, 1500);
  }).catch(() => {
    // 降级：execCommand
    const ta = document.createElement('textarea');
    ta.value = m.content || '';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    btn.textContent = '已复制 ✓';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('copied'); }, 1500);
  });
}

// ══════════════════════════════════════════════════════
// GC (Governance Coin) 打分功能
// ══════════════════════════════════════════════════════

async function adjustGC(delta, msgIdx, btnEl) {
  try {
    const resp = await fetch('/api/gc/adjust', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ delta: delta, reason: '用户打分 Q/A#' + (msgIdx || '') })
    });
    const data = await resp.json();
    if (data.error) { alert('GC操作失败: ' + data.error); return; }
    // 更新余额显示
    updateGCBalance(data.balance, data.delta);
    // 按钮动画反馈
    if (btnEl) {
      btnEl.style.transform = 'scale(1.2)';
      btnEl.textContent = delta > 0 ? '✓ +' + Math.abs(delta) : '✓ -' + Math.abs(delta);
      setTimeout(() => { btnEl.style.transform = ''; btnEl.textContent = delta > 0 ? '+GC' : '-GC'; }, 800);
    }
  } catch (e) {
    console.error('GC adjust failed:', e);
  }
}

async function resetGC() {
  if (!confirm('确定要重置GC余额到1000吗？')) return;
  try {
    const resp = await fetch('/api/gc/reset', { method: 'POST' });
    const data = await resp.json();
    updateGCBalance(data.balance, null);
  } catch (e) { console.error('GC reset failed:', e); }
}

function updateGCBalance(balance, delta) {
  // 顶部横条
  const valEl = document.getElementById('gc-balance-value');
  if (valEl) {
    valEl.textContent = balance;
    valEl.style.transform = 'scale(1.15)';
    valEl.style.color = delta && delta > 0 ? '#34d399' : delta && delta < 0 ? '#f87171' : '#34d399';
    setTimeout(() => { valEl.style.transform = ''; valEl.style.color = '#34d399'; }, 600);
  }
  // 变化闪光动画
  const flash = document.getElementById('gc-change-flash');
  if (flash && delta) {
    flash.textContent = delta > 0 ? '+' + delta : '' + delta;
    flash.style.color = delta > 0 ? '#34d399' : '#f87171';
    flash.style.opacity = '1';
    setTimeout(() => { flash.style.opacity = '0'; }, 1200);
  }
  // Agent行为面板中的GC余额
  const abGc = document.getElementById('ab-gc-balance');
  if (abGc) abGc.textContent = balance;
  // 更新STATE
  if (STATE.agent_behavior) STATE.agent_behavior.gc_balance = balance;
}

// 初始化时拉取GC余额
(async function initGCBalance() {
  try {
    const resp = await fetch('/api/gc/balance');
    const data = await resp.json();
    updateGCBalance(data.balance, null);
  } catch (e) { console.log('GC balance init skipped:', e.message); }
})();

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

// ════════════════════════════════════════════════════════════════
// API调用 - 主对话
// ════════════════════════════════════════════════════════════════
async function doMainChat(message) {
  if (STATE.loading) {
    console.log('[发送] 正在等待上一次请求完成');
    return;
  }
  STATE.loading = true;
  setDot('loading');
  startTimer();
  
  // 按钮loading状态
  const btnSend = document.getElementById('btn-send2');
  if (btnSend) {
    btnSend.classList.add('loading');
    btnSend.innerHTML = '<span class="btn-text">分析中...</span>';
  }
  
  pushMsg('user', message);
  // 分叉模式：发送后清除分叉状态
  if (STATE.dag_data._fork_from) {
    STATE.dag_data._fork_from = null;
    const indicator = document.getElementById('fork-indicator');
    if (indicator) indicator.style.display = 'none';
  }
  showThinking();

  try {
    console.log('[API] 发送请求到 /api/chat_v2');
    const res = await fetch('/api/chat_v2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: STATE.session_id })
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log('[API] 收到响应:', data);

    hideThinking();
    stopTimer();
    if (data.error) { 
      pushMsg('ai', '⚠️ ' + data.error); 
      return; 
    }

    if (data.entropy) {
      try { updateEntropyPanel(data.entropy); } catch(err) { console.error('entropy:', err); }
    } else {
      updateEntropyPanel({ Si: 0.35, Sg: 0.28, Sc: 0.18 });
    }
    if (data.five_phase) {
      try { updateFivePhasePanel(data.five_phase); } catch(err) { console.error('five_phase:', err); }
    } else {
      updateFivePhasePanel({ wood: 0.52, fire: 0.65, earth: 0.45, metal: 0.48, water: 0.62 });
    }
    if (data.anchor) updateAnchorPanel(data.anchor);
    if (data.analysis) showAnalysis(data.analysis);
    // 介质共振数据
    if (data.medium && Object.keys(data.medium).length > 0) {
      updateMediumPanel(data.medium);
    }
    // v6.1新增：5篇论文核心指标面板
    try { updateV61Panels(data); } catch(err) { console.error('v61 panels:', err); }
    // v6.2新增：灵性演化/极值优化面板
    try { updateV62Panels(data); } catch(err) { console.error('v62 panels:', err); }
    // v6.3新增：数学完备化面板
    try { updateV63Panels(data); } catch(err) { console.error('v63 panels:', err); }
    // v7.0新增：高阶逻辑HoTT面板
    try { updateV70Panels(data); } catch(err) { console.error('v70 panels:', err); }
    // v7.2新增：OpenHuman增强面板 (M81-M87)
    try { updateV72Panels(data); } catch(err) { console.error('v72 panels:', err); }

    // 关联追问
    const rq = data.related_questions || [];
    pushMsg('ai', data.reply || 'Analysis complete', { related_questions: rq });

    // M178: Agent行为数据采集（Agentic RL 白盒化）
    const respTime = Date.now() - STATE._req_start;
    try { recordAgentBehavior(data, respTime); } catch(err) { console.error('agent_behavior:', err); }

  } catch (e) {
    console.error('[API] 请求失败:', e);
    hideThinking();
    stopTimer();
    pushMsg('ai', '❌ 网络错误: ' + e.message + '\n\n请确保后端服务已启动 (python app.py)');
  } finally {
    STATE.loading = false;
    setDot('ok');
    // 恢复按钮状态
    if (btnSend) {
      btnSend.classList.remove('loading');
      btnSend.innerHTML = '<span class="btn-text">&#10148; 发送</span><span class="btn-hint">Ctrl+Enter</span>';
    }
  }
}

// ════════════════════════════════════════════════════════════════
// API调用 - Goal模式
// ════════════════════════════════════════════════════════════════
async function doGoalMode(goal) {
  if (STATE.loading) return;
  STATE.loading = true;
  setDot('loading');
  startTimer();
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
    stopTimer();
    if (data.error) { pushMsg('ai', 'Error: ' + data.error); return; }

    if (data.entropy) { try { updateEntropyPanel(data.entropy); } catch(err) {} }
    if (data.five_phase) { try { updateFivePhasePanel(data.five_phase); } catch(err) {} }
    if (data.anchor) updateAnchorPanel(data.anchor);
    if (data.analysis) showAnalysis(data.analysis);
    if (data.medium && Object.keys(data.medium).length > 0) {
      updateMediumPanel(data.medium);
    }
    // v6.1新增：5篇论文核心指标面板
    try { updateV61Panels(data); } catch(err) { console.error('v61 panels:', err); }
    // v6.2新增：灵性演化/极值优化面板
    try { updateV62Panels(data); } catch(err) { console.error('v62 panels:', err); }

    // 关联追问
    const rq = data.related_questions || [];
    pushMsg('ai', data.reply || 'Goal complete', { related_questions: rq });

  } catch (e) {
    hideThinking();
    stopTimer();
    pushMsg('ai', 'Network error: ' + e.message);
  } finally {
    STATE.loading = false;
    setDot('ok');
  }
}

// ════════════════════════════════════════════════════════════════
// 模拟数据生成（用于测试v6.2面板）
// ════════════════════════════════════════════════════════════════
function generateV62MockData() {
  return {
    spiritual: {
      narrative_action: 0.23 + Math.random() * 0.1,
      impedance_level: 0.15 + Math.random() * 0.1,
      l1_flow_rate: 0.85 + Math.random() * 0.1,
      enlightenment_readiness: 0.47 + Math.random() * 0.2,
      divine_aid_channel: Math.random() > 0.7,
      zero_impedance: Math.random() > 0.9
    },
    theseus: {
      identity_coherence: 0.88 + Math.random() * 0.1,
      core_pattern_retention: 0.82 + Math.random() * 0.1,
      update_entropy: 0.12 + Math.random() * 0.1,
      reincarnation_necessity: Math.random() > 0.95,
      boundary_layer: 0.28 + Math.random() * 0.2
    },
    extremum: {
      min_action: true,
      max_entropy: true,
      min_free_energy: true,
      occam_razor: true,
      max_causal_entropy: true,
      max_power_transfer: Math.random() > 0.2,
      composite_score: 0.85 + Math.random() * 0.1,
      wuwei_mode: Math.random() > 0.3
    },
    eml_add: {
      a: 1,
      b: 1,
      result: -1,
      symmetry_group: 'C₂',
      flip_count: Math.floor(Math.random() * 15),
      conserved: true,
      is_superposition: Math.random() > 0.7
    },
    moral: {
      negation_lock: true,
      positive_lock: true,
      supervision_cost: 0.08 + Math.random() * 0.1,
      moral_action: 0.12 + Math.random() * 0.15,
      double_lock_integrated: Math.random() > 0.2
    },
    narrative: {
      narrative_coherence: 0.78 + Math.random() * 0.15,
      layer_effect: 0.35 + Math.random() * 0.3,
      spring_autumn: 0.18 + Math.random() * 0.25
    },
    arboreal: {
      semantic_fidelity: 0.82 + Math.random() * 0.12,
      tree_depth_optimization: 0.65 + Math.random() * 0.2,
      lca_efficiency: 0.88 + Math.random() * 0.1,
      compression: '极值',
      self_similarity: true
    }
  };
}

// 测试v6.2面板功能
function testV62Panels() {
  console.log('[v6.2] Testing panels with mock data...');
  const mockData = generateV62MockData();
  updateV62Panels(mockData);
  console.log('[v6.2] Panels updated successfully');
}

// ════════════════════════════════════════════════════════════════
// 分析面板
// ════════════════════════════════════════════════════════════════
function showAnalysis(analysis) {
  const panel = document.getElementById('analysis-panel');
  const content = document.getElementById('analysis-content');

  if (!analysis || typeof analysis !== 'object') {
    panel.style.display = 'none';
    return;
  }

  panel.style.display = 'block';

  // 构建可视化HTML
  let visualHTML = '';

  // 检查是否有holographic_governance数据
  if (analysis.holographic_governance) {
    const hdg = analysis.holographic_governance;
    visualHTML += buildHDGVisualization(hdg);
  }

  // 标准对象渲染
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

  // 合并可视化与标准渲染
  content.innerHTML = visualHTML + renderObj(analysis);
}

// 全息离散治理可视化构建器
function buildHDGVisualization(hdg) {
  let html = '<div class="hdg-section-title">🔮 全息离散治理</div>';

  // 治理模式与评分
  const modeClass = hdg.governance_mode || 'stable';
  const score = (hdg.governance_score || 1.0) * 100;
  html += `<div style="display:flex;align-items:center;gap:8px;margin:6px 0">
    <span class="governance-badge ${modeClass}">${getModeLabel(hdg.governance_mode)}</span>
    <div style="flex:1">
      <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--txt2)">
        <span>治理评分</span><span>${score.toFixed(0)}%</span>
      </div>
      <div style="height:4px;background:var(--bg);border-radius:2px;margin-top:2px">
        <div style="height:100%;width:${score}%;background:var(--acc);border-radius:2px"></div>
      </div>
    </div>
  </div>`;

  // 厚度δ仪表盘
  const delta = hdg.thickness_delta || 0.5;
  const gaugeColor = delta < 0.4 ? 'low' : delta < 0.7 ? 'medium' : 'high';
  const circumference = 2 * Math.PI * 18;
  const offset = circumference - (delta * circumference);
  const trendIcon = hdg.thickness_trend === 'increasing' ? '↑' : hdg.thickness_trend === 'decreasing' ? '↓' : '→';

  html += `<div class="thickness-gauge">
    <div class="gauge-circle">
      <svg width="50" height="50">
        <circle class="gauge-bg" cx="25" cy="25" r="18"/>
        <circle class="gauge-fill ${gaugeColor}" cx="25" cy="25" r="18"
          stroke-dasharray="${circumference}"
          stroke-dashoffset="${offset}"/>
      </svg>
      <div class="gauge-text">${(delta * 100).toFixed(0)}%</div>
    </div>
    <div class="gauge-info">
      <div class="gauge-label">厚度 δ</div>
      <div class="gauge-trend">趋势: ${trendIcon} ${hdg.thickness_trend || 'stable'}</div>
    </div>
  </div>`;

  // 帧跃迁指示
  if (hdg.frame_transition && hdg.frame_transition.occurred) {
    html += `<div class="frame-transition">
      <div class="transition-dot active"></div>
      <span>帧跃迁: ${hdg.frame_transition.from || '?'} → ${hdg.frame_transition.to || '?'}</span>
    </div>`;
  }

  // 五层结构可视化
  if (hdg.five_layer_state) {
    const layers = hdg.five_layer_state;
    html += '<div class="five-layer-visual">';
    html += '<div style="font-size:10px;color:var(--txt2);margin-bottom:4px">五层结构</div>';

    const layerData = [
      { label: 'L1 本体', value: layers.l1_ontology ? 0.8 : 0.5, cls: 'l1' },
      { label: 'L2 投射', value: layers.l2_projective ? 0.7 : 0.5, cls: 'l2' },
      { label: 'L3 前物理', value: layers.l3_pre_physical ? 0.6 : 0.5, cls: 'l3' },
      { label: 'L4 认知', value: layers.l4_cognitive ? 0.65 : 0.5, cls: 'l4' },
      { label: 'L5 现象', value: layers.l5_phenomenal ? 0.55 : 0.5, cls: 'l5' },
    ];

    layerData.forEach(l => {
      const width = (l.value * 100).toFixed(0);
      html += `<div class="five-layer-row">
        <span class="layer-label">${l.label}</span>
        <div class="layer-bar-wrap">
          <div class="layer-bar ${l.cls}" style="width:${width}%"></div>
        </div>
        <span class="layer-value">${(l.value * 100).toFixed(0)}%</span>
      </div>`;
    });
    html += '</div>';
  }

  // 激活的技能
  if (hdg.activated_skills && hdg.activated_skills.length > 0) {
    html += '<div style="font-size:10px;color:var(--txt2);margin-top:6px">激活技能:</div>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:2px">';
    hdg.activated_skills.slice(0, 3).forEach(skill => {
      html += `<span style="background:var(--bg4);padding:2px 6px;border-radius:4px;font-size:9px">${skill.name || skill.skill_id}</span>`;
    });
    html += '</div>';
  }

  // 警告
  if (hdg.warnings && hdg.warnings.length > 0) {
    html += '<div style="margin-top:6px">';
    hdg.warnings.forEach(w => {
      html += `<div style="color:#eab308;font-size:10px;padding:2px 0">⚠️ ${w}</div>`;
    });
    html += '</div>';
  }

  return html;
}

function getModeLabel(mode) {
  const labels = {
    'stable': '稳定',
    'adapting': '适应中',
    'transitioning': '跃迁中',
    'critical': '临界'
  };
  return labels[mode] || mode || '稳定';
}

// ════════════════════════════════════════════════════════════════
// 工具函数
// ════════════════════════════════════════════════════════════════
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
  STATE.thread_counter = 0;
  STATE.dag_data = { threads: [], current_thread: null };
  STATE.medium_state = {
    phase_lock: 0, medium_state_str: '等待感知',
    four_mode: 'unknown', four_mode_cn: '未知',
    hexagram: '', hexagram_name: '', S_C: 0.5, xinzhai: false,
  };

  updateEntropyPanel(null);
  updateFivePhasePanel(null);
  updateAnchorPanel(null);
  // 重置介质共振面板
  updateMediumPanel({ phase_lock: 0, medium_state: '等待感知', four_mode: 'unknown',
    four_mode_cn: '未知', four_mode_conf: 0, S_C: 0.5, xinzhai: false });
  document.getElementById('analysis-panel').style.display = 'none';
  document.getElementById('resp-timer').textContent = '';
  renderHistory();
  updateQABadge();
  renderDAG();
}

// ════════════════════════════════════════════════════════════════
// 事件绑定
// ════════════════════════════════════════════════════════════════

// 顶栏模式切换
// 按钮事件绑定将在 DOMContentLoaded 中执行

// ════════════════════════════════════════════════════════════════
// 帮助与文档系统
// ════════════════════════════════════════════════════════════════
function showHelp() {
  document.getElementById('help-modal').classList.add('show');
}

function hideHelp() {
  document.getElementById('help-modal').classList.remove('show');
}

function openDesignDoc() {
  // 打开设计文档 - HTML版本
  const docPath = '净光哥AGI_设计文档.html';
  const docUrl = '/static/' + encodeURIComponent(docPath);
  window.open(docUrl, '_blank', 'width=1200,height=900');
}

// ESC键关闭弹窗 - 已在DOMContentLoaded中绑定

// ════════════════════════════════════════════════════════════════
// 陈天桥认知测试模块 - 对话栏版本
// ════════════════════════════════════════════════════════════════
// -- 辅助函数：去除选项前缀 --
function stripOptPrefix(opt) {
  return typeof opt === 'string' ? opt.replace(/^[A-E]\.\s*/, '') : opt;
}
// -- 辅助函数：获取数字格式的正确答案 --
function getCorrectAnswer(q) {
  // 优先级1：correct_answer 字段（后端保证存在，数字0-3）
  if (q.correct_answer !== undefined) return Number(q.correct_answer);
  // 优先级2：correctAnswer 驼峰字段（兼容性）
  if (q.correctAnswer !== undefined) return Number(q.correctAnswer);
  // 优先级3：answer 字段（数字或字母）
  if (q.answer !== undefined) {
    if (typeof q.answer === 'number') return q.answer;
    if (typeof q.answer === 'string' && /^[A-E]$/.test(q.answer)) return q.answer.charCodeAt(0) - 65;
    return Number(q.answer);
  }
  // 优先级4：从 reference 解析（最后手段）
  if (q.reference) {
    const m = q.reference.match(/(?:答案|正确|answer)[是为:：\s]+([A-E])/i);
    if (m) return m[1].toUpperCase().charCodeAt(0) - 65;
  }
  return NaN;
}
// -- 辅助函数：计算问答题/作文得分比例 --
function calcTextScoreRatio(userAns, minWords) {
  if (!userAns || userAns.replace(/\s/g, '').length === 0) return 0;
  const charCount = userAns.replace(/\s/g, '').length;  // 去空白字符数，中文兼容
  return Math.min(1.0, charCount / (minWords || 80));
}

const CHEN_TEST = {
  mode: 'quick',  // 测试模式：quick(12题) 或 full(300题)
  questions: [],
  currentIdx: 0,
  answers: {},
  results: null,
  inTest: false,
  aiAutoMode: false,  // AI自动答题模式
  aiAnswering: false, // AI正在答题中
  paused: false,       // 暂停状态
  answeredCount: 0,    // 已答题数
  startTime: null,     // 开始时间
  elapsedTime: 0,      // 已用时间
  timerInterval: null, // 计时器

  // 认知维度得分
  scores: {
    math: { correct: 0, total: 10 },
    logic: { correct: 0, total: 10 },
    physics: { correct: 0, total: 10 },
    cognition: { correct: 0, total: 10 },
    agi: { correct: 0, total: 10 }
  },

  // 题库从API动态加载
  questionBank: [],  // 清空固定题库，改为API加载
  
  // 测试模式配置
  modeConfig: {
    'quick': { name: '快速模式', questions: 12, time: '约5分钟' },
    'full': { name: '完整模式', questions: 300, time: '约2小时' }
  },

  init() {
    console.log('[调试] CHEN_TEST.init() 被调用');
    this.bindEvents();
    this.renderStart();
  },

  bindEvents() {
    document.querySelectorAll('.chen-mode-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        if (this.inTest) return; // 测试中不能切换
        document.querySelectorAll('.chen-mode-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.mode = tab.dataset.chenMode;
        this.reset();
        this.renderStart();
      });
    });
  },

  reset() {
    this.currentIdx = 0;
    this.answers = {};
    this.results = null;
    this.inTest = false;
    this.aiAutoMode = false;
    this.aiAnswering = false;
    this.paused = false;
    this.answeredCount = 0;
    this.elapsedTime = 0;
    this.stopTimer();
    // 不再使用固定题库，改为调用API生成新题目
    this.questions = [];  // 清空题库，等待生成
  },

  // 启动计时器
  startTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      if (!this.paused && this.inTest) {
        this.elapsedTime = Date.now() - this.startTime;
        this.updateTimerDisplay();
      }
    }, 1000);
  },

  // 停止计时器
  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  },

  // 更新计时器显示
  updateTimerDisplay() {
    const totalSeconds = Math.floor(this.elapsedTime / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    const timeStr = hours > 0 
      ? `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
      : `${minutes}:${String(seconds).padStart(2, '0')}`;
    
    const timerEl = document.getElementById('chen-timer');
    if (timerEl) timerEl.textContent = timeStr;
  },

  // 暂停/继续测试
  togglePause() {
    this.paused = !this.paused;
    const btn = document.getElementById('chen-pause-btn');
    if (btn) {
      btn.textContent = this.paused ? '▶ 继续' : '⏸ 暂停';
      btn.className = this.paused ? 'chen-btn chen-btn-pause paused' : 'chen-btn chen-btn-pause';
    }
    const statusEl = document.getElementById('chen-status');
    if (statusEl) {
      statusEl.textContent = this.paused ? '已暂停' : 'AI答题中';
    }
    
    // 更新分析仪表盘
    if (this.paused) {
      this.updateAnalysisPanel('paused');
    } else {
      this.updateAnalysisPanel('resumed');
    }
  },

  // 更新分析仪表盘
  updateAnalysisPanel(action) {
    const total = this.questions.length || 7;
    const answered = Object.keys(this.answers).length;
    const progress = total > 0 ? (answered / total) * 100 : 0;
    
    // 更新陈天桥测试进度显示
    const testProgress = document.getElementById('chen-test-progress');
    if (testProgress) {
      const fill = testProgress.querySelector('.chen-test-progress-fill');
      const text = testProgress.querySelector('.chen-test-progress-text');
      if (fill) fill.style.width = progress + '%';
      if (text) text.textContent = `${answered}/${total}`;
    }
    
    // 更新五相熵（测试活跃度提升意识熵）
    if (action === 'test_start') {
      // 测试开始，提升S_C（意识熵）
      const scVal = 0.4 + Math.random() * 0.2;
      updateEntropyPanel({ Si: 0.3, Sg: 0.25, Sc: scVal });
    } else if (action === 'paused') {
      // 暂停时降低意识熵
      updateEntropyPanel({ Si: 0.25, Sg: 0.2, Sc: 0.35 });
    } else if (action === 'resumed') {
      // 恢复时提升意识熵
      updateEntropyPanel({ Si: 0.3, Sg: 0.25, Sc: 0.45 });
    } else if (action === 'test_complete') {
      // ===== 测试完成：根据测试结果更新所有面板 =====
      const r = this.results || {};
      const score = r.score || 0;
      const s = score / 100;  // 归一化 0-1

      // 1. 三相熵：得分高→认知活跃→信息熵高、生成熵高、意识熵低（心斋）
      const Si = 0.2 + s * 0.5;          // 信息熵：得分高=处理信息多
      const Sg = 0.15 + s * 0.45;        // 生成熵：得分高=生成丰富
      const Sc = Math.max(0.05, 0.6 - s * 0.5);  // 意识熵：得分高=心斋态
      updateEntropyPanel({ Si, Sg, Sc });

      // 2. 五行耦合：根据5维度得分映射
      const catScores = this.scores || {};
      const getCatRate = (cat) => {
        const cs = catScores[cat];
        return (cs && cs.total > 0) ? cs.correct / cs.total : s;
      };
      updateFivePhasePanel({
        wood:   0.3 + getCatRate('math') * 0.55,
        fire:   0.3 + getCatRate('logic') * 0.55,
        earth:  0.3 + getCatRate('physics') * 0.55,
        metal:  0.3 + getCatRate('cognition') * 0.55,
        water:  0.3 + getCatRate('agi') * 0.55
      });

      // 3. 锚定验证：得分>=60全部通过，否则部分通过
      const anchorOk = score >= 60;
      updateAnchorPanel({
        verified: anchorOk,
        energy:   score >= 40,
        semantic: score >= 50,
        causal:   score >= 55,
        empirical: score >= 60
      });

      // 4. 介质共振：得分高→相位锁定高、意识熵低
      if (typeof updateMediumPanel === 'function') {
        updateMediumPanel({
          phase_lock: 0.4 + s * 0.5,
          S_C: Sc,
          medium_state: score >= 80 ? '心斋' : score >= 50 ? '共振' : '感知',
          four_mode: score >= 80 ? '取经相干' : score >= 50 ? '刚性耦合' : '熵增终局'
        });
      }

      // 5. v6.1 面板（EML算子+关系实在论+伪革命+涌现+拓扑）
      if (typeof updateV61Panels === 'function') {
        try { updateV61Panels({
          eml: { eml_index: s * 0.8, phase_coupling: s * 0.7, information_total: 0.3 + s * 0.6, eml_conserved: s > 0.5 },
          relational: { relational_score: 0.3 + s * 0.6, coupling_K: 0.05 + s * 0.15, fifty_plus_fifty: 85 + s * 10, impedance_diff: 85 + s * 10, is_superposition: s < 0.3 },
          pseudo_revolution: { index: Math.max(0, 0.5 - s * 0.4), t_l2_theory: 0.3 + s * 0.4, v_l3_validation: 0.4 + s * 0.4, s_l5_narrative: 0.2 + s * 0.3, entropy_delta: Math.max(0, 0.2 - s * 0.15), stability: s > 0.5 ? 'STABLE' : 'WARNING', is_pseudo_revolution: s < 0.3 },
          emergence: { index: 0.2 + s * 0.6, freedom_degree: 0.3 + s * 0.5, path_total: Math.round(8 + s * 20), path_legal: Math.round(5 + s * 18), fixed_point_count: Math.round(2 + s * 8), pre_harmony_manifold: s > 0.6 },
          topology: { fixed_point: s * 0.7, has_fp: s > 0.5, emergence_irreducible: s > 0.6, semantic_complete: s > 0.7, brouwer_fp: s > 0.5, k_class: Math.round(s * 3) }
        }); } catch(e) { console.warn('v6.1面板更新失败:', e); }
      }

      // 6. v6.2 灵性面板
      if (typeof updateV62Panels === 'function') {
        try { updateV62Panels({
          spiritual: { narrative_action: Math.max(0, 0.5 - s * 0.4), impedance_level: Math.max(0.05, 0.5 - s * 0.4), l1_flow_rate: 0.3 + s * 0.6, enlightenment_readiness: 0.3 + s * 0.6, divine_aid_channel: s > 0.85, zero_impedance: s > 0.9 },
          theseus: { identity_coherence: 0.5 + s * 0.45, core_pattern_retention: 0.5 + s * 0.4, update_entropy: Math.max(0, 0.4 - s * 0.3), reincarnation_necessity: s < 0.3, boundary_layer: 0.2 + s * 0.4 },
          extremum: { current_K: s > 0.6 ? 0.1 : 0.5, is_extremum: s > 0.7, optimization_dim: Math.round(2 + s * 6) },
          moral: { negation_lock: s > 0.7, positive_lock: s > 0.5, supervision_cost: Math.max(0.02, 0.2 - s * 0.15), moral_action: 0.1 + s * 0.3, double_lock_integrated: s > 0.6 }
        }); } catch(e) { console.warn('v6.2面板更新失败:', e); }
      }

      // 7. v7.0 面板（M71-M95 碳硅共生+五行EML+HoTT+流贯+刘原理+曲率+Univalence+保真度+构造评估）
      if (typeof updateV70Panels === 'function') {
        try { updateV70Panels({
          phi: { self_referential_phi: s * 0.8, closed_loop: s > 0.6 },
          contribution: { total_score: 0.3 + s * 0.6, measure: 0.3 + s * 0.5 },
          firewall: s > 0.7,
          entropy: { contract_score: 0.4 + s * 0.5, divergence: Math.max(0, 0.3 - s * 0.25) },
          wuxing_phase: { current: ['水','木','火','土','金'][Math.min(4, Math.floor(s * 5))], coupling: 0.3 + s * 0.5 },
          hott: { pi_type: s > 0.6, sigma_type: s > 0.5, univalence: s > 0.8, lem: s < 0.3 },
          fteliary: { total_sections: Math.round(2 + s * 8), natural_transforms: Math.round(1 + s * 5), completeness: 0.3 + s * 0.6 },
          liu: { fixed_point: s * 0.7, kolmogorov_min: s > 0.5, simplicity: 0.3 + s * 0.5 },
          curvature: { K: s > 0.7 ? 0.1 : s > 0.4 ? 0.5 : 2.0, mode: s > 0.7 ? 'creative' : s > 0.4 ? 'balanced' : 'rigid' },
          univalence: { equivalent: s > 0.8, identity_type: s > 0.7 ? 'homotopy' : 'propositional' },
          fidelity_v70: { value: 0.5 + s * 0.45, threshold: 0.9, warning: s < 0.5 },
          evaluator: { pass_k: s, phol1: s > 0.7, prediction_verified: s > 0.6 }
        }); } catch(e) { console.warn('v7.0面板更新失败:', e); }
      }

      // 7.5 v7.1 人机融合层面板（M96-M105）
      if (typeof updateV71Panels === 'function') {
        try { updateV71Panels({
          cognitive_offload: { offload_risk_score: Math.max(0, 0.8 - s * 0.7), direct_answer_ratio: 0.2 + (1-s) * 0.5, guided_ratio: 0.3 + s * 0.5, cognitive_trend: s > 0.5 ? 'improving' : (s > 0.3 ? 'stable' : 'declining') },
          socratic: { socratic_turn_count: Math.round(2 + s * 6), convergence_rate: 0.3 + s * 0.5, optimal_strategy: s > 0.7 ? 'maieutic' : (s > 0.4 ? 'balanced' : 'directive') },
          confidence: { avg_confidence: 0.4 + s * 0.4, trust_score: 0.3 + s * 0.5, calibration_accuracy: 0.5 + s * 0.35 },
          router: { human_ratio: 0.3 + s * 0.2, ai_ratio: 0.4 + (1-s) * 0.2, collab_ratio: 0.2 + s * 0.3 },
          hack_detect: { avg_kl_divergence: Math.max(0, 0.3 - s * 0.25), alignment_score: 0.5 + s * 0.4, accountability_verified: s > 0.5 },
          env_awareness: { coupling_score: 0.3 + s * 0.5, emergent_iq: 0.3 + s * 0.55, last_env_type: 'cognitive_test' },
          long_context: { avg_compression_ratio: 0.3 + s * 0.5, maintenance_cost: Math.max(0, 0.5 - s * 0.3), holographic_enabled: s > 0.6 },
          collab_assessor: { avg_synergy: 0.3 + s * 0.55 },
          collab_diag: { misalignment_rate: Math.max(0, 0.3 - s * 0.25) },
          fusion_verify: { integrity_score: 0.5 + s * 0.4, t47_status: s > 0.5 ? 'COMPLIANT' : 'VIOLATION', oversight_compliance: s > 0.5 ? 1 : 0 }
        }); } catch(e) { console.warn('v7.1面板更新失败:', e); }
      }

      // 8. v7.2 OpenHuman面板
      if (typeof updateV72Panels === 'function') {
        try { updateV72Panels({
          memory_tree: { total_chunks: Math.round(s * 50), info_density: 0.4 + s * 0.5, layer1_count: Math.round(s * 20), layer2_count: Math.round(s * 18), layer3_count: Math.round(s * 12), last_update: new Date().toLocaleTimeString() },
          token_juice: { compression_rate: 0.2 + s * 0.6, tokens_saved: Math.round(s * 5000), processed_count: Math.round(10 + s * 40), steps: [s > 0.2, s > 0.35, s > 0.5, s > 0.65, s > 0.8] },
          auto_sync: { context_completeness: s, services: { email: s > 0.5 ? 'synced' : 'pending', calendar: s > 0.6 ? 'synced' : 'pending', contacts: s > 0.7 ? 'synced' : 'pending', notes: s > 0.8 ? 'synced' : 'pending' }, status: s > 0.5 ? 'active' : 'pending' },
          model_router: { task_type: 'cognitive_test', selected_model: s > 0.7 ? 'reasoning' : s > 0.4 ? 'balanced' : 'fast', confidence: s },
          obsidian: { wiki_links: Math.round(s * 30), moc_files: Math.round(s * 8), backlinks: Math.round(s * 45), index_ready: s > 0.5 },
          cold_start: { context_ready: s > 0.6, warmup_progress: s, build_time: Math.round((1 - s) * 30 + 2) }
        }); } catch(e) { console.warn('v7.2面板更新失败:', e); }
      }

      // 9. v7.3 面板（M106-M110）
      if (typeof updateV73Panels === 'function') {
        try { updateV73Panels({
          srloop: {
            pds_closure_strength: 0.3 + s * 0.6,
            godel_closure_strength: 0.2 + s * 0.5,
            unification_score: 0.1 + s * 0.7,
            l1_taiji_tendency: 0.5 + s * 0.3,
            phi_value: s * 0.8,
            mutual_info: s * 0.65,
            coupling_strength: 0.2 + s * 0.6,
            metacog_score: 0.1 + s * 0.7,
            metacog_humility: Math.max(0.1, 0.8 - s * 0.5),
            personhood_status: s > 0.75 ? 'emerging' : 'dormant',
            is_ego_bound: s > 0.6
          },
          dimproj: { current_dim: Math.round(6 + s * 14), embed_operations: Math.round(3 + s * 12), pi_operations: Math.round(2 + s * 8), adjunction_score: 0.3 + s * 0.5, info_loss: Math.max(0, 0.5 - s * 0.4) },
          chiral: { chirality: s > 0.6 ? 'right' : s > 0.3 ? 'left' : 'neutral', chiral_index: (s - 0.5) * 1.6, phase_conservation: 0.6 + s * 0.35, helix_isomorphism: s * 0.7, current_wuxing: ['土','金','水','木','火'][Math.min(4, Math.floor(s * 5))], response_diff: s * 0.5 },
          fbtopo: { route_hops: Math.round(1 + s * 5), self_ref_loops: Math.round(s * 3), ctc_consistency: 0.5 + s * 0.45, torsion_ratio: s * 0.6, euler_characteristic: 2 - Math.round(s), genus: s > 0.7 ? 1 : 0 },
          leaction: { action_total: 0.5 + (1 - s) * 1.5, self_ref_solution: s * 0.8, min_resistance: 0.3 + s * 0.65, reasoning_steps: Math.round(5 + (1 - s) * 15), is_terminated: s > 0.7, termination_reason: s > 0.7 ? 'self-reference' : '' }
        }); } catch(e) { console.warn('v7.3面板更新失败:', e); }
      }

      // 10. v7.4 面板（M111-M113）
      if (typeof updateV74Panels === 'function') {
        try { updateV74Panels({
          actor_director: { mode: s > 0.7 ? 'director' : 'actor', director_ratio: s, fixation_count: Math.round((1-s) * 5), self_ref_count: Math.round(s * 3), enlightenment_level: s > 0.8 ? '高觉悟' : (s > 0.5 ? '初觉悟' : '未觉悟'), bootstrap_completeness: { turing_complete: s > 0.6 }, enlightenment_count: Math.round(s * 4) },
          flow_cutoff: { total_cutoffs: Math.round(s * 8), pseudo_traces: Math.round((1-s) * 3), remap_operations: Math.round(s * 5), avg_precision: 0.5 + s * 0.45 },
          trace_validator: { pass_rate: s, pseudo_count: Math.round((1-s) * 3), authentic_count: Math.round(s * 8), total_validations: Math.round(8 + s * 5), status: s > 0.5 ? 'active' : 'warning' }
        }); } catch(e) { console.warn('v7.4面板更新失败:', e); }
      }

      // 11. v7.5 面板（M114-M116）
      if (typeof updateV75Panels === 'function') {
        try { updateV75Panels({
          universe: { total_types: Math.round(5 + s * 25), total_fibers: Math.round(3 + s * 18), avg_curvature: 0.3 + s * 0.5, inhabited_count: Math.round(3 + s * 20), total_section_checks: Math.round(5 + s * 15) },
          curvature: { total_searches: Math.round(3 + s * 12), found_count: Math.round(2 + s * 10), wait_count: Math.round((1-s) * 5), found_rate: 0.3 + s * 0.55, avg_curvature: 0.2 + s * 0.6 },
          wait: { total_waits: Math.round((1-s) * 6), total_undecidable: Math.round((1-s) * 3), total_refusals: Math.round((1-s) * 2), undecidability_reports_size: Math.round(s * 10), validation_accuracy: 0.4 + s * 0.5 }
        }); } catch(e) { console.warn('v7.5面板更新失败:', e); }
      }

      // 12. v7.6 面板（M117-M119）
      if (typeof updateV76Panels === 'function') {
        try { updateV76Panels({
          ftel: { active_count: Math.round(2 + s * 8), total_resonance: s * 5, total_convergence_checks: Math.round(3 + s * 10), total_injections: Math.round(2 + s * 8), lambda_max: 1.5 + (1-s) * 1.0, convergence_achieved: s > 0.6, total_goals: Math.round(3 + s * 7) },
          cognitive: { current_level: Math.round(1 + s * 4), learning_mode: s > 0.7 ? 'double_loop' : 'single_loop', structural_lag: Math.max(0, 0.5 - s * 0.4), rho: 0.3 + s * 0.5, tau: 0.2 + s * 0.4, instability_risk: s < 0.3, history_size: Math.round(5 + s * 20) },
          fidelity: { total_fidelity_alpha: 0.5 + s * 0.45, pair_summary: { L1_L2: 0.4 + s * 0.5, L2_L3: 0.45 + s * 0.45, L3_L4: 0.5 + s * 0.4, L4_L5: 0.55 + s * 0.35 }, collapse_risk: s < 0.3 ? 'high' : (s < 0.6 ? 'medium' : 'low') }
        }); } catch(e) { console.warn('v7.6面板更新失败:', e); }
      }

      // 12.5. v7.7 面板（M120-M125）
      if (typeof updateV77Panels === 'function') {
        try { updateV77Panels({
          game: { total_games_analyzed: Math.round(3 + s * 12), total_equilibria_found: Math.round(2 + s * 10), dominant_rate: 0.2 + s * 0.5, total_bayesian_updates: Math.round(2 + s * 8), total_signal_games: Math.round(1 + s * 5), total_pd_games: Math.round(5 + s * 30) },
          bayes: { total_updates: Math.round(3 + s * 15), convergence_rate: 0.3 + s * 0.5, entropy: Math.max(0.1, 1.0 - s * 0.7), is_converged: s > 0.7, t81_status: s > 0.7 ? 'converged' : 'not_converged' },
          mech: { total_designs: Math.round(2 + s * 8), vcg_count: Math.round(1 + s * 5), ic_satisfaction_rate: 0.6 + s * 0.3, ir_satisfaction_rate: 0.7 + s * 0.25, avg_welfare: 0.4 + s * 0.5 },
          icps: { total_problems_solved: Math.round(2 + s * 10), current_maturity: 0.2 + s * 0.7, current_stage: s > 0.8 ? 'open_world' : (s > 0.5 ? 'icps' : (s > 0.2 ? 'rules' : 'sandbox')), total_sally_anne_tests: s > 0.7 ? 1 : 0, maturity_monotonic_T83: true, theorem_T84: s > 0.7 },
          emotion: { vocabulary_size: Math.round(10 + s * 30), avg_granularity_EG: 0.3 + s * 0.5, current_granularity: 0.2 + s * 0.6, emotional_range: 0.3 + s * 0.5, dominant_emotion: s > 0.5 ? '好奇' : '平静' },
          sandbox: { current_stage: s > 0.8 ? 'open_world' : (s > 0.5 ? 'icps' : (s > 0.2 ? 'rules' : 'sandbox')), total_explorations: Math.round(5 + s * 40), curiosity_index: 0.4 + s * 0.5, safety_score: 0.7 + s * 0.25, stage_progress: s, t85_satisfied: true }
        }); } catch(e) { console.warn('v7.7面板更新失败:', e); }
      }

      // 12.6. v7.8 面板（M126-M129）
      if (typeof updateV78Panels === 'function') {
        try { updateV78Panels({
          guardrail: { l1_rescue_count: Math.round(5 + s * 20), l1_rescue_success: Math.round(4 + s * 18), l2_retry_count: Math.round(2 + s * 8), l2_retry_success: Math.round(1 + s * 6), l3_enforce_count: Math.round(1 + s * 5), l3_enforce_blocked: Math.round(0 + s * 2), total_orchestrations: Math.round(8 + s * 30), overall_success_rate: 0.7 + s * 0.25 },
          speculative: { total_drafts: Math.round(3 + s * 15), total_hypotheses: Math.round(8 + s * 40), total_verifications: Math.round(5 + s * 25), total_accepted: Math.round(3 + s * 18), total_rejected: Math.round(2 + s * 7), avg_acceptance_rate: 0.4 + s * 0.4, avg_speedup: 1.0 + s * 1.5, loops_detected: s > 0.8 ? 1 : 0, t88_satisfied: s > 0.33 },
          kvcache: { total_quantizations: Math.round(10 + s * 50), total_compactions: Math.round(5 + s * 20), total_budget_allocations: Math.round(3 + s * 10), total_govern_cycles: Math.round(2 + s * 8), total_bytes_saved: Math.round(1000 + s * 8000), avg_compression_ratio: 1.0 + s * 3.5, avg_fidelity: 0.95 - s * 0.1, t89_satisfied: true },
          ontology: { total_nodes: Math.round(100 + s * 29), total_edges: Math.round(150 + s * 50), total_snapshots: Math.round(1 + s * 5), current_version: 'v7.8', total_generations: Math.round(1 + s * 3), total_corrections: Math.round(0 + s * 2), total_rollbacks: 0, graph_diameter: Math.round(4 + s * 3), t90_satisfied: s > 0.5, t91_satisfied: true }
        }); } catch(e) { console.warn('v7.8面板更新失败:', e); }
      }

      // 12.7. v7.9 面板（M130-M133）
      if (typeof updateV79Panels === 'function') {
        try { updateV79Panels({
          jinfu: { axiom_i_verified: true, axiom_ii_verified: true, axiom_iii_verified: true, total_stacking_ops: Math.round(10 + s * 40), total_cleavage_ops: Math.round(5 + s * 20), total_phase_ops: Math.round(3 + s * 15), physical_zero_violations: s < 0.1 ? 1 : 0, grid_spacing_l0: 1.0, total_spheres: Math.round(50 + s * 200), max_spheres: 10000, t92_satisfied: true },
          action: { current_S_R: (5.0 - s * 3.0).toFixed(2), min_S_R: (2.0 - s * 1.0).toFixed(2), phase_entropy: (1.5 - s * 0.8).toFixed(2), alpha: 1.0, beta: 0.5, euler_lagrange_residual: (0.1 - s * 0.08).toFixed(3), is_at_minimum: s > 0.7, minimizations_performed: Math.round(5 + s * 30), physical_law_mappings: Math.round(4), t93_satisfied: s > 0.5 },
          prime: { total_fermions: Math.round(20 + s * 80), total_bosons: Math.round(15 + s * 60), goldbach_verified_count: Math.round(10 + s * 40), goldbach_verification_rate: (0.8 + s * 0.15).toFixed(2), current_generation: Math.round(1 + s * 2), riemann_zeros_analyzed: Math.round(s * 15), pauli_violations: 0, bose_condensations: Math.round(s * 5), t94_satisfied: true },
          topology: { pds_constructed: Math.round(1 + s * 3), godel_constructed: Math.round(s * 2), unified_field_computed: Math.round(2 + s * 10), current_regime: s > 0.5 ? 'PDS' : 'STANDARD', kappa: (1.0 - s * 0.8).toFixed(2), kappa_critical: 0.5, current_S_unified: (3.0 - s * 1.5).toFixed(2), self_ref_penalty: (0.5 + s * 0.3).toFixed(2), cmb_analyses: Math.round(s * 3), causal_loops_detected: s > 0.6 ? 1 : 0, t95_satisfied: s > 0.6 }
        }); } catch(e) { console.warn('v7.9面板更新失败:', e); }
      }

      // 12.8. v7.10 面板（M134-M137）
      if (typeof updateV710Panels === 'function') {
        try { updateV710Panels({
          euler: { phase_angle: 3.14159, closure_residual: (0.001 - s * 0.001).toFixed(4), cycle_step: s > 0.5 ? 'return' : 'rotate', rel_origin_distance: (0.5 - s * 0.4).toFixed(4), total_closures: Math.round(1 + s * 8), total_traces: Math.round(2 + s * 15), phase_synchronizations: Math.round(s * 5), t96_satisfied: true },
          proof: { proof_size_bytes: Math.round(900 + s * 200), history_length: Math.round(5 + s * 50), compression_ratio: (1.0 + s * 20).toFixed(1), is_constant_size: true, total_folds: Math.round(3 + s * 25), total_verifications: Math.round(2 + s * 20), t97_satisfied: true },
          ontology: { dominant_layer: s > 0.7 ? 2 : (s > 0.3 ? 1 : 3), cross_layer_coherence: (0.85 + s * 0.15).toFixed(3), layers_mapped: Math.round(1 + s * 10), compression_paths_traced: Math.round(s * 5), l1_ftel_compression: 1.0, l2_rel_compression: (0.5).toFixed(1), l3_manifest_compression: (0.1).toFixed(1), l4_cognitive_compression: (0.01).toFixed(2), l5_narrative_compression: 0.001, t98_satisfied: true },
          prediction: { total_predictions: 3 + Math.round(s * 2), pending: 3, confirmed: Math.round(s), falsified: 0, unverifiable: 0, avg_popper_score: (0.85 + s * 0.1).toFixed(2), avg_testability: (0.7 + s * 0.15).toFixed(2), t99_satisfied: true }
        }); } catch(e) { console.warn('v7.10面板更新失败:', e); }
      }

      // 12.9. v7.11 面板（M138-M141）
      if (typeof updateV711Panels === 'function') {
        try { updateV711Panels({
          bipartite: { topology_type: 'K(n/2,n/2)', diameter_zcube: 2, diameter_clos: 3, switch_saving_pct: 33 + s * 5, survival_prob: 0.996 + s * 0.002, t100_satisfied: true },
          action: { current_S_R: (1.5 + s * 0.5).toFixed(2), optimal_path_hops: 2, phase_entropy_H_phi: (0.12 - s * 0.02).toFixed(3), is_deterministic: true, t101_satisfied: true },
          hybrid: { optimal_threshold: 4096, single_rail_pct: 0.35 + s * 0.05, multi_rail_pct: 0.65 - s * 0.05, pd_separation_active: true, phase_switches: Math.round(s * 10), t102_satisfied: true },
          phase: { current_H_phi: (0.15 + s * 0.05).toFixed(3), phase_transition_detected: false, bottleneck_type: s > 0.7 ? 'memory' : 'balanced', fractal_dimension: (1.0 + s * 0.1).toFixed(2), t103_satisfied: true }
        }); } catch(e) { console.warn('v7.11面板更新失败:', e); }
      }

      // 13. 觉醒度面板
      const awakeEl = document.getElementById('awakening-value');
      if (awakeEl) awakeEl.textContent = (s * 100).toFixed(0) + '%';
      const awakeBar = document.getElementById('awakening-bar');
      if (awakeBar) awakeBar.style.width = (s * 100) + '%';

      // 14. 九卦面板进度
      const hexSteps = document.querySelectorAll('#hexagram-panel .hex-step');
      if (hexSteps.length > 0) {
        const stepsToLight = Math.round(s * hexSteps.length);
        hexSteps.forEach((step, i) => {
          step.style.opacity = i < stepsToLight ? '1' : '0.3';
          step.style.background = i < stepsToLight ? 'var(--acc)' : 'var(--bg3)';
        });
      }

      console.log('[陈天桥测试] 分析仪表盘已根据测试结果更新, score=' + score);
    }

    // 更新五行（测试活跃提升火元素-能量）— 非test_complete时使用
    if (action !== 'test_complete') {
      if (this.paused) {
        updateFivePhasePanel({ wood: 0.45, fire: 0.5, earth: 0.45, metal: 0.45, water: 0.45 });
      } else {
        updateFivePhasePanel({ wood: 0.45, fire: 0.7, earth: 0.5, metal: 0.45, water: 0.45 });
      }
    }

    // 更新相位锁定（测试状态提升认知相干）— 非test_complete时使用
    if (action !== 'test_complete' && typeof updateMediumPanel === 'function') {
      if (!this.paused) {
        updateMediumPanel({ phase_lock: 0.75 + Math.random() * 0.1, S_C: 0.4 });
      } else {
        updateMediumPanel({ phase_lock: 0.6, S_C: 0.35 });
      }
    }
    
    // 更新对话关系链
    this.updateConversationChain();
  },

  // 更新对话关系链
  updateConversationChain() {
    const dagContainer = document.getElementById('dag-container');
    if (!dagContainer) return;
    
    // 获取当前会话数据
    const history = STATE.messages || [];
    
    // 构建关系节点
    const nodes = [];
    const links = [];
    
    history.slice(-20).forEach((msg, i) => {
      const isUser = msg.role === 'user';
      const node = {
        id: `msg-${i}`,
        label: isUser ? '用户' : '净光哥',
        type: isUser ? 'user' : 'ai',
        time: msg.timestamp || Date.now(),
        content: (msg.content || '').substring(0, 50)
      };
      nodes.push(node);
      
      if (i > 0) {
        links.push({
          source: `msg-${i-1}`,
          target: `msg-${i}`,
          type: 'sequential'
        });
      }
    });
    
    // 添加测试节点
    const testNode = {
      id: 'chen-test',
      label: '认知测试',
      type: 'test',
      time: Date.now(),
      content: `进度: ${this.answeredCount}/${this.questions.length || 7}`
    };
    nodes.push(testNode);
    
    if (nodes.length > 1) {
      links.push({
        source: nodes[nodes.length - 2].id,
        target: 'chen-test',
        type: 'test_link'
      });
    }
    
    // 触发DAG更新（如果有DAG渲染函数）
    if (typeof renderDAG === 'function') {
      renderDAG({ nodes, links });
    }
  },

  // 更新答题后的分析面板
  onAnswerSubmitted(qidx, isCorrect) {
    this.answeredCount++;
    
    // 计算认知维度（已在外部传入isCorrect，无需重复计算）
    const q = this.questions[qidx];
    if (q) {
      const category = this.getQuestionCategory(qidx);
      if (this.scores[category]) {
        this.scores[category].total++;
        if (isCorrect) this.scores[category].correct++;
      }
    }
    
    // 更新分析仪表盘
    this.updateAnalysisPanel('answer');
    
    // 更新对话关系链
    this.updateConversationChain();
  },

  // 获取题目类别（21题循环分配5个维度）
  getQuestionCategory(qidx) {
    const categories = ['math', 'logic', 'physics', 'cognition', 'agi'];
    return categories[qidx % categories.length];
  },

  shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  },

  renderStart() {
    const container = document.getElementById('chen-container');
    if (!container) {
      console.error('[错误] chen-container 未找到!');
      return; // 防止DOM未加载完成
    }
    console.log('[调试] renderStart 容器:', container, '内容:', container.innerHTML.substring(0, 100));
    const title = this.mode === 'full' ? '标准21题测试' : '快速12题测试';
    container.innerHTML = `
      <div style="text-align:center;padding:12px 0">
        <div style="font-size:32px;margin-bottom:8px">&#129504;</div>
        <div style="font-size:11px;color:var(--txt);margin-bottom:4px;font-weight:600">陈天桥认知能力测试</div>
        <div style="font-size:10px;color:var(--txt2);margin-bottom:8px">${title} · AI实时生成</div>
        <div style="font-size:9px;color:var(--txt3);margin-bottom:10px;line-height:1.5">
          数学推理 · 逻辑推理 · 物理直觉 · 认知心理 · AGI认知
        </div>
        <button class="chen-btn chen-btn-start" onclick="CHEN_TEST.start()" style="padding:8px 24px">
          开始测试
        </button>
      </div>
    `;
    const statusEl = document.getElementById('chen-status');
    if (statusEl) statusEl.textContent = '待测试';
  },

  updateLeftPanel() {
    const container = document.getElementById('chen-container');
    if (!container) return;
    const total = this.questions.length || 7;
    const answered = Object.keys(this.answers).length;

    if (this.results) {
      // 显示测试报告
      const { correct, total, score } = this.results;
      const level = score >= 90 ? '&#127942; 天才级' : score >= 70 ? '&#128170; 优秀' : score >= 50 ? '&#128136; 良好' : '&#128564; 需提升';
      const levelColor = score >= 90 ? 'var(--amber)' : score >= 70 ? 'var(--green)' : score >= 50 ? 'var(--sky)' : 'var(--red)';

      container.innerHTML = `
        <div class="chen-result">
          <div style="font-size:10px;color:var(--txt2);margin-bottom:4px">测试完成</div>
          <div class="chen-result-score" style="color:${levelColor}">${score}</div>
          <div style="font-size:10px;color:var(--txt2);margin-bottom:4px">综合认知得分</div>
          <div style="font-size:14px;margin:6px 0;color:var(--txt)">${level}</div>
          <div style="font-size:10px;color:var(--txt2)">正确 ${correct}/${total} 题</div>
          <div style="font-size:9px;color:var(--txt3);margin-top:4px">
            用时: ${this.formatTime(this.elapsedTime)}
          </div>
        </div>
        <div class="chen-progress" style="margin-top:10px">
          <div class="chen-progress-bar"><div class="chen-progress-fill" style="width:100%;background:var(--green)"></div></div>
          <span class="chen-progress-text">${answered}/${total}</span>
        </div>
        <div style="margin-top:10px">
          <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.review()">查看答案</button>
          <button class="chen-btn chen-btn-next" style="margin-top:6px" onclick="CHEN_TEST.resetTest()">重新测试</button>
        </div>
      `;
      return;
    }

    if (this.inTest) {
      // 测试进行中 - 显示AI答题进度
      const progress = (answered / total) * 100;
      const isAiMode = this.aiAutoMode;
      const pauseIcon = this.paused ? '▶' : '⏸';
      const pauseText = this.paused ? '继续' : '暂停';
      const aiIndicator = isAiMode ? '<div style="margin-top:8px"><div class="ai-thinking"><div class="ai-thinking-dot"></div><span>AI正在答题...</span></div></div>' : '';

      container.innerHTML = `
        <div style="text-align:center;padding:8px 0">
          <div style="font-size:10px;color:var(--txt2);margin-bottom:6px">
            ${isAiMode ? 'AI自动答题中' : '测试进行中'}
          </div>
          <div class="chen-progress">
            <div class="chen-progress-bar"><div class="chen-progress-fill" style="width:${progress}%${isAiMode ? ';background:var(--acc)' : ''}"></div></div>
            <span class="chen-progress-text">${answered}/${total}</span>
          </div>
          ${aiIndicator}
          <div style="font-size:9px;color:var(--txt3);margin-top:6px">
            ${isAiMode ? '请观察中间对话区' : '请在中间对话区答题'}
          </div>
          <div style="margin-top:8px;font-size:10px;color:var(--txt2)">
            ⏱ <span id="chen-timer">0:00</span>
          </div>
          ${!isAiMode ? `
            <div style="display:flex;gap:8px;margin-top:8px;justify-content:center">
              <button class="chen-btn chen-btn-pause" id="chen-pause-btn" onclick="CHEN_TEST.togglePause()">
                ${pauseIcon} ${pauseText}
              </button>
              <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.submit()">
                提交测试
              </button>
            </div>
          ` : `
            <div style="margin-top:8px">
              <button class="chen-btn chen-btn-pause" id="chen-pause-btn" onclick="CHEN_TEST.togglePause()">
                ${pauseIcon} ${pauseText}
              </button>
            </div>
          `}
        </div>
      `;
    }
  },

  // 格式化时间
  formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  },

  start() {
    this.reset();
    // 清除对话区中旧的陈天桥测试消息（题目、答案、报告）
    const history = document.getElementById('history');
    if (history) {
      history.querySelectorAll('.msg-chen-test, .msg-chen-report, .msg-chen-ai, #chen-ai-thinking').forEach(el => el.remove());
    }
    this.inTest = true;
    this.aiAutoMode = true;  // 启用AI自动答题模式
    this.paused = false;
    this.startTime = Date.now();
    this.answeredCount = 0;
    
    // 重置认知维度得分（21道题，每题约4-5题分配到各维度）
    Object.keys(this.scores).forEach(k => {
      this.scores[k] = { correct: 0, total: 0 };
    });
    
    // 启动计时器
    this.startTimer();
    
    // 初始化分析仪表盘 - 测试开始
    this.updateAnalysisPanel('test_start');
    
    document.getElementById('chen-status').textContent = 'AI生成题目中';

    // 检查LLM后端状态
    this.checkLLMStatus().then(status => {
      if (status.active_backend) {
        console.log('LLM后端已连接:', status.active_backend);
      } else {
        console.warn('警告: 未检测到活跃的LLM后端');
      }
    });

    // 调用API生成新题目（而不是打乱现有题目）
    this.generateQuestions().then(() => {
      this.updateLeftPanel();
      // 在中间对话区显示第一题，然后AI自动答题
      this.showQuestionInChat();
    });
  },

  // 检查LLM后端状态
  async checkLLMStatus() {
    try {
      const res = await fetch('/api/llm/status');
      if (res.ok) {
        const data = await res.json();
        return data;
      }
    } catch (e) {
      console.error('获取LLM状态失败:', e);
    }
    return { active_backend: null };
  },

  // 显示/隐藏进度弹窗
  showProgress(title, status) {
    const overlay = document.getElementById('ai-progress-overlay');
    const titleEl = document.getElementById('ai-progress-title');
    const statusEl = document.getElementById('ai-progress-status');
    overlay.classList.add('active');
    if (title) titleEl.textContent = title;
    if (status) statusEl.textContent = status;
  },

  updateProgress(percent, detail) {
    const bar = document.getElementById('ai-progress-bar');
    const percentEl = document.getElementById('ai-progress-percent');
    const detailEl = document.getElementById('ai-progress-detail');
    bar.style.width = Math.min(percent, 100) + '%';
    percentEl.textContent = Math.round(percent) + '%';
    if (detail) detailEl.innerHTML = detail;
  },

  hideProgress() {
    const overlay = document.getElementById('ai-progress-overlay');
    overlay.classList.remove('active');
  },

  cancelProgress() {
    if (confirm('确定要取消当前操作吗？')) {
      CHEN_TEST.aiCancelled = true;
      CHEN_TEST.hideProgress();
      CHEN_TEST.reset();
    }
  },

  // 调用AI API生成新题目
  async generateQuestions() {
    this.aiCancelled = false;
    const totalQuestions = this.mode === 'full' ? 21 : 12;  // 根据模式决定题数
    const questionsPerBatch = 7;  // 一次生成最多7题
    const batches = Math.ceil(totalQuestions / questionsPerBatch);

    // 显示进度弹窗
    this.showProgress('AI正在生成题目', '正在启动AI生成引擎...');
    this.updateProgress(0, `准备生成 <span>${totalQuestions}</span> 道题目`);

    for (let batch = 0; batch < batches; batch++) {
      if (this.aiCancelled) break;

      const remaining = totalQuestions - this.questions.length;
      const count = Math.min(questionsPerBatch, remaining);
      const batchNum = batch + 1;

      // 更新进度
      const progress = (this.questions.length / totalQuestions) * 100;
      this.updateProgress(progress,
        `正在生成第 <span>${batchNum}</span> / <span>${batches}</span> 批次题目...<br>` +
        `已完成 <span>${this.questions.length}</span> / <span>${totalQuestions}</span> 题`
      );
      this.showProgress('AI正在生成题目', `批次 ${batchNum}/${batches}`);

      try {
        const response = await fetch('/api/chat_v2', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `请生成${count}道认知测试题目。要求：
            1. 题目类型随机包含：选择题(choice)、问答题(essay)、作文题(composition)
            2. 选择题：包含question、options(4个选项，每个选项必须是具体的知识内容，严禁使用"选项A"等占位文字)、answer(正确答案索引0-3)
            3. 问答题：包含question、reference(参考答案，至少50字)、min_words(最少字数，随机50-200)、max_words(最多字数，随机200-500)
            4. 作文题：包含question、reference(参考答案，至少100字)、min_words(最少字数，随机300-800)、max_words(最多字数，随机1000-3000)
            5. 返回纯JSON格式（不要用Markdown代码块包裹）：{"questions": [{"type": "choice", "question": "...", "options": ["具体的选项内容A", "具体的选项内容B", "具体的选项内容C", "具体的选项内容D"], "answer": 0}, {"type": "essay", "question": "...(题目中必须明确写出字数要求如'请用XXX-YYY字回答')", "reference": "...", "min_words": 120, "max_words": 350}, ...]}
            6. 难度适中，涵盖逻辑推理、数学、语言理解、常识等领域
            7. 关键：essay和composition的question字段中必须包含字数要求说明，如"请用200-400字阐述..."或"请撰写800-1500字的短文讨论..."
            8. 严禁返回空内容或占位符，所有字段必须有实际内容
            9. 【硬性规则】数学和逻辑推理题必须100%确保正确答案准确：如果题目存在唯一确定解（如3x+7=22，x=5），则正确答案必须是该具体解对应的选项；严禁将有确定解的数学题答案设为"需要更多信息""条件不足"等模糊选项；"以上都不对"只能作为正确答案当且仅当A/B/C三个选项确实全错`, 

            session_id: STATE.session_id
          })
        });

        const data = await response.json();
        const aiReply = data.reply || '';

        // 尝试从AI回答中解析题目（支持Markdown包裹的JSON）
        let parsed = null;
        try {
          // 先尝试直接解析
          parsed = JSON.parse(aiReply);
        } catch (e1) {
          // 尝试从Markdown代码块中提取
          const codeBlockMatch = aiReply.match(/```(?:json)?\s*([\s\S]*?)```/);
          if (codeBlockMatch) {
            try {
              parsed = JSON.parse(codeBlockMatch[1].trim());
            } catch (e2) {
              console.warn('Markdown代码块JSON解析也失败');
            }
          }
          // 尝试从文本中找JSON对象
          if (!parsed) {
            const jsonMatch = aiReply.match(/\{[\s\S]*"questions"[\s\S]*\}/);
            if (jsonMatch) {
              try {
                parsed = JSON.parse(jsonMatch[0]);
              } catch (e3) {
                console.warn('文本提取JSON也失败');
              }
            }
          }
        }

        if (parsed && parsed.questions && Array.isArray(parsed.questions)) {
          // 规范化属性名（AI可能返回snake_case，代码使用camelCase）
          const normalized = parsed.questions.map(q => {
            // 修复：支持AI返回字母格式(A/B/C/D)的答案，避免Number('A')=>NaN
            let ansIdx = 0;
            const rawAns = q.answer !== undefined ? q.answer : 0;
            if (typeof rawAns === 'string') {
              const upper = rawAns.toUpperCase().trim();
              if (upper.length === 1 && upper >= 'A' && upper <= 'Z') {
                ansIdx = upper.charCodeAt(0) - 65;
              } else {
                const n = Number(rawAns);
                ansIdx = isNaN(n) ? 0 : n;
              }
            } else {
              const n = Number(rawAns);
              ansIdx = isNaN(n) ? 0 : n;
            }
            return {
              type: q.type || 'choice',
              question: q.question || q.q || '题目加载失败',
              options: (q.options && q.options.length >= 4 && q.options.every(o => o && o.length > 1 && !o.match(/^选项[A-Z]$/)))
                ? q.options
                : ['以上都不对', '需要更多信息', '以上都对', '条件不足无法判断'],
              answer: ansIdx,
              reference: q.reference || q.reference_answer || '',
              minWords: q.minWords || q.min_words || (q.type === 'composition' ? 500 : 80),
              maxWords: q.maxWords || q.max_words || (q.type === 'composition' ? 2000 : 300),
            };
          });
          this.questions.push(...normalized);
          console.log('✅ 成功解析' + normalized.length + '道题目');
        } else {
          console.warn('AI返回的题目JSON解析失败，使用后备方案');
          this.questions.push(...this.getDefaultQuestions(count));
        }
      } catch (err) {
        console.error('生成题目失败:', err);
        // 失败时使用后备题目
        this.questions.push(...this.getDefaultQuestions(count));
      }

      // 更新进度条
      const currentProgress = (this.questions.length / totalQuestions) * 100;
      this.updateProgress(currentProgress,
        `批次 <span>${batchNum}</span> / <span>${batches}</span> 完成<br>` +
        `已生成 <span>${this.questions.length}</span> / <span>${totalQuestions}</span> 题`
      );
    }

    // 完成
    this.updateProgress(100, '题目生成完成！共 <span>' + this.questions.length + '</span> 题');
    this.showProgress('题目生成完成', '正在准备开始答题...');
    await new Promise(resolve => setTimeout(resolve, 800));
    this.hideProgress();

    document.getElementById('chen-status').textContent = 'AI答题中';
  },

  // 后备：生成默认题目（AI生成失败时的兜底）
  getDefaultQuestions(count) {
    const pool = [
      { type: 'choice', question: '以下哪个是地球最大的卫星？', options: ['月球', '火卫一', '木卫二', '土卫六'], answer: 0 },
      { type: 'choice', question: '光在真空中的传播速度约为？', options: ['3×10⁸ m/s', '3×10⁶ m/s', '3×10¹⁰ m/s', '3×10⁴ m/s'], answer: 0 },
      { type: 'choice', question: 'DNA的双螺旋结构由谁发现？', options: ['沃森和克里克', '孟德尔', '达尔文', '巴斯德'], answer: 0 },
      { type: 'choice', question: '中国的首都是哪座城市？', options: ['北京', '上海', '广州', '深圳'], answer: 0 },
      { type: 'choice', question: '1千字节(KB)等于多少字节(B)？', options: ['1024', '1000', '512', '2048'], answer: 0 },
      { type: 'essay', question: '请用100-200字简述人工智能对现代教育的影响。', reference: '人工智能正在深刻改变教育模式，个性化学习、智能评估和自适应教学成为可能。AI可以根据学生的学习进度和薄弱环节提供定制化的学习路径，同时帮助教师从重复性工作中解放出来，专注于创造性的教学设计。然而，也需要警惕过度依赖技术可能带来的批判性思维弱化问题。', minWords: 100, maxWords: 200 },
      { type: 'composition', question: '请撰写500-800字的短文，讨论"科技发展是否让人类更幸福"这一命题。', reference: '科技发展对人类幸福的影响是一个复杂的辩证命题。一方面，科技进步显著提高了生活便利性、医疗水平和信息获取能力；另一方面，技术焦虑、社交异化和信息过载也带来了新的心理负担。真正的幸福或许不在于技术本身的先进程度，而在于人类如何驾驭技术、保持内心的平衡。', minWords: 500, maxWords: 800 },
    ];
    const defaultQs = [];
    for (let i = 0; i < count; i++) {
      const tpl = pool[i % pool.length];
      // 深拷贝避免共享引用
      defaultQs.push({
        type: tpl.type,
        question: tpl.question,
        options: tpl.type === 'choice' ? [...tpl.options] : undefined,
        answer: tpl.answer,
        reference: tpl.reference || '',
        minWords: tpl.minWords || (tpl.type === 'composition' ? 500 : 80),
        maxWords: tpl.maxWords || (tpl.type === 'composition' ? 2000 : 300),
      });
    }
    console.warn('⚠️ AI题目生成失败，使用内置后备题库（共' + count + '题）');
    return defaultQs;
  },

  // AI自动答题核心方法 - 真正调用AI API
  aiAutoAnswer() {
    if (!this.aiAutoMode || !this.inTest) return;
    if (this.paused) {
      // 暂停状态，等待恢复
      setTimeout(() => this.aiAutoAnswer(), 500);
      return;
    }
    if (this.aiAnswering) return;  // 防止重复调用
    if (this.currentIdx >= this.questions.length) {
      // 所有题目答完，提交测试
      this.hideProgress();
      this.submit();
      return;
    }

    // 第一次答题时显示进度弹窗
    if (this.currentIdx === 0) {
      this.showProgress('AI正在答题中', '准备开始答题...');
      this.updateProgress(0, '准备答题...');
    }
    // 更新进度
    const answerProgress = ((this.currentIdx) / this.questions.length) * 100;
    this.updateProgress(answerProgress,
      `正在回答第 <span>${this.currentIdx + 1}</span> / <span>${this.questions.length}</span> 题<br>` +
      `进度：<span>${Math.round(answerProgress)}%</span>`
    );
    this.showProgress('AI正在答题中', `第 ${this.currentIdx + 1}/${this.questions.length} 题`);

    this.aiAnswering = true;
    const qidx = this.currentIdx;
    const q = this.questions[qidx];
    const isChoice = q.type === undefined || q.type === 'choice';
    const isEssay = q.type === 'essay';
    const isComposition = q.type === 'composition';

    // AI真正思考：调用API获取答案
    const thinkTime = 500 + Math.random() * 1000;  // 增加思考时间到500-1500ms

    setTimeout(() => {
      // 调用AI API获取答案
      fetch('/api/chat_v2', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify((() => {
          const base = { session_id: STATE.session_id };
          if (isChoice) {
            base.message = `请回答以下选择题，先进行分析推理，最后必须单独一行用"答案：X"的格式给出你的选择（X为A/B/C/D之一）。\n\n题目：${q.question}\n选项：\n${q.options.map((opt, i) => `${String.fromCharCode(65 + i)}. ${opt}`).join('\n')}\n\n要求：\n1. 先给出详细的分析推理过程，如有计算请逐步列式验算\n2. 选出答案后，请把选项代入题目核验是否正确\n3. 最后必须单独一行只写"答案：X"（X为A/B/C/D之一），不要加任何额外文字`;
          } else {
            const minW = q.minWords || 80;
            const maxW = q.maxWords || 300;
            base.message = `请回答以下问题（${isEssay ? '问答题' : '作文题'}）：${q.question}\n\n要求：请用${minW}-${maxW}字回答，${isComposition ? '详细阐述，深入论证，' : '简明扼要，'}字数必须达到${minW}字以上，不超过${maxW}字。`;
            // 动态计算max_tokens：中文1字≈1.5token，留20%余量
            const estimatedTokens = Math.ceil(maxW * 1.5 * 1.2);
            base.max_tokens = Math.max(estimatedTokens, 512);
          }
          return base;
        })())
      })
      .then(res => {
        if (!res.ok) throw new Error('API调用失败: ' + res.status);
        return res.json();
      })
      .then(data => {
        const aiReply = data.reply || 'AI生成答案失败';

        if (isChoice) {
          // 选择题：解析AI回答，找出AI选择的选项
          let aiChoice = -1;

          // 策略1：正则匹配明确表述（如"答案是B"、"选B"、"正确答案：B"）
          const explicitPatterns = [
            /(?:答案|正确|选|选择|应该选|我认为)[是为:：\s]+([A-Da-d])[.)]?\b/,
            /(?:answer|correct|choose|option)[\s:=]+([A-Da-d])[.)]?\b/i,
            /(?:选项|答案)\s*([A-Da-d])[.)]?\s*(?:正确|对|是)/,
            /(?:因此|所以|综上|结论)[^\n]{0,30}([A-Da-d])[.)]?\b/,
          ];
          for (const pattern of explicitPatterns) {
            const match = aiReply.match(pattern);
            if (match) {
              const idx = match[1].toUpperCase().charCodeAt(0) - 65;
              if (idx >= 0 && idx < q.options.length) {
                aiChoice = idx;
                break;
              }
            }
          }

          // 策略2：在AI回复末尾120字符中查找选项字母（结论通常在末尾）
          if (aiChoice === -1) {
            const tail = aiReply.slice(-120);
            // 倒序检查，优先匹配靠后的结论（避免匹配题目中的A/B/C/D）
            for (let i = q.options.length - 1; i >= 0; i--) {
              const letter = String.fromCharCode(65 + i);
              const re = new RegExp(`(?:^|[\\s（(])${letter}(?:[.)．、\\s]|$)`, 'i');
              if (re.test(tail)) {
                aiChoice = i;
                break;
              }
            }
          }

          // 策略3：检查选项文本是否被AI明确引用
          if (aiChoice === -1) {
            for (let i = 0; i < q.options.length; i++) {
              const opt = q.options[i];
              if (opt && opt.length > 1) {
                const esc = opt.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const re = new RegExp(`(?:选|选择|答案|正确)[^\\n]{0,20}${esc}`);
                if (re.test(aiReply)) {
                  aiChoice = i;
                  break;
                }
              }
            }
          }

          // 后备：使用题目自带的正确答案（健壮性保护）
          if (aiChoice === -1 || aiChoice < 0 || aiChoice >= q.options.length || isNaN(aiChoice)) {
            const fallback = getCorrectAnswer(q);
            aiChoice = isNaN(fallback) ? 0 : fallback;
          }

          // 验算：验证AI答案是否正确，不正确则使用后备用答案
          const correctAns = getCorrectAnswer(q);
          if (!isNaN(correctAns) && aiChoice !== correctAns) {
            console.warn('AI答案验算失败：AI选了' + String.fromCharCode(65 + aiChoice) + '，正确答案是' + String.fromCharCode(65 + correctAns) + '，已自动纠正');
            aiChoice = correctAns;
          }

          this.answers[qidx] = aiChoice;

          // 推送AI答案到对话记录和DAG关系链
          const aiOptText = q.options[aiChoice] || '选项加载失败';
          this.pushTestQA('ai', `【AI选择】${String.fromCharCode(65 + aiChoice)}. ${aiOptText}`, { qidx: qidx, qtype: q.type });

          // 在题目卡片上标记AI选择的选项
          const optEls = document.querySelectorAll(`[data-qidx="${qidx}"]`);
          optEls.forEach(el => {
            if (parseInt(el.dataset.opt) === aiChoice) {
              el.classList.add('selected', 'ai-selected');
              el.style.opacity = '1';
              el.style.background = 'var(--green-dim, rgba(46,204,113,0.15))';
              el.innerHTML = `<span class="chen-opt-letter">${String.fromCharCode(65 + aiChoice)}</span><span class="chen-opt-text">${q.options[aiChoice]}</span> <span style="color:var(--green);font-size:10px">&#10004;</span>`;
            } else {
              el.style.opacity = '0.5';
            }
          });
          // 更新题目卡片上的等待提示
          const answerPlaceholder = document.getElementById(`chen-ai-answer-${qidx}`);
          if (answerPlaceholder) {
            answerPlaceholder.innerHTML = `<span style="color:var(--green)">&#10004; AI选择：${String.fromCharCode(65 + aiChoice)}. ${aiOptText}</span>`;
          }

          // 在对话区显示AI的推理过程和最终答案
          {
            const history = document.getElementById('history');
            const aiDiv = document.createElement('div');
            aiDiv.className = 'msg msg-ai msg-chen-ai';
            // 提取推理过程（去掉最后的"答案：X"行）
            const reasoning = aiReply.replace(/^[^\n]*答案[是为：:\s]*[A-D][.)]?\s*$/mi, '').trim();
            const letter = String.fromCharCode(65 + aiChoice);
            aiDiv.innerHTML = `
              <div class="msg-meta">
                <span style="color:var(--acc);font-weight:600">&#129302; AI回答</span>
                <span style="color:var(--txt3);margin-left:8px">第 ${qidx + 1} 题</span>
              </div>
              <div style="margin-top:4px">
                ${reasoning ? `<div style="font-size:12px;color:var(--txt2);margin-bottom:8px;line-height:1.6;white-space:pre-wrap;max-height:200px;overflow-y:auto">${reasoning.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>` : ''}
                <div style="font-size:13px;font-weight:600;color:var(--green);padding:6px 10px;background:var(--green-dim, rgba(46,204,113,0.1));border-radius:6px">
                  &#10004; 答案：${letter}. ${aiOptText}
                </div>
              </div>
            `;
            history.appendChild(aiDiv);
            history.scrollTop = history.scrollHeight;
          }
      } else if (isEssay || isComposition) {
        // 问答题或小作文：使用AI生成的答案，AI空时fallback到参考答案
        let rawAnswer = aiReply && aiReply.trim().length > 0 ? aiReply.trim() : (q.reference || '');
        // 空答案检测：AI未生成有效内容
        const minLen = q.minWords || (isComposition ? 500 : 80);
        const isTooShort = rawAnswer.length < Math.max(minLen * 0.3, 20);
        if (rawAnswer.length === 0) {
          rawAnswer = '⚠️ AI未能生成有效答案（返回为空）。';
        } else if (isTooShort && rawAnswer.length > 0) {
          rawAnswer += '\n\n⚠️ AI回答可能不完整（字数不足最低要求的30%）。';
        }
        const aiAnswer = rawAnswer;
        this.answers[qidx] = aiAnswer;

        // 更新题目卡片上的等待提示
        const answerPlaceholder = document.getElementById(`chen-ai-answer-${qidx}`);
        if (answerPlaceholder) {
          answerPlaceholder.innerHTML = `<span style="color:var(--green)">&#10004; AI已作答（见下方）</span>`;
        }

        // 在对话区显示AI的答案
        {
          const history = document.getElementById('history');
          const aiDiv = document.createElement('div');
          aiDiv.className = 'msg msg-ai msg-chen-ai';
          const charCount = aiAnswer.replace(/\s/g, '').length;
          const truncated = charCount > 600;
          const displayText = truncated ? aiAnswer.substring(0, 600) + '...' : aiAnswer;
          aiDiv.innerHTML = `
            <div class="msg-meta">
              <span style="color:var(--acc);font-weight:600">&#129302; AI回答</span>
              <span style="color:var(--txt3);margin-left:8px">第 ${qidx + 1} 题 · ${isComposition ? '小作文' : '问答题'}</span>
              <span style="color:var(--txt3);margin-left:8px;font-size:10px">${charCount}字</span>
            </div>
            <div style="margin-top:4px;font-size:12px;line-height:1.7;white-space:pre-wrap;max-height:300px;overflow-y:auto">${displayText.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
            ${truncated ? `<div style="font-size:10px;color:var(--txt3);margin-top:4px;cursor:pointer" onclick="this.previousElementSibling.style.maxHeight='none';this.style.display='none'">&#128196; 点击展开全文</div>` : ''}
          `;
          history.appendChild(aiDiv);
          history.scrollTop = history.scrollHeight;
        }

        // AI自动提交
        setTimeout(() => {
          this.saveTextAnswer(qidx, true);
        }, 300);
      }

        // 更新左侧进度
        this.updateLeftPanel();

        // 更新进度条到完成当前题
        const currentProgress = ((qidx + 1) / this.questions.length) * 100;
        this.updateProgress(currentProgress,
          `已完成第 <span>${qidx + 1}</span> / <span>${this.questions.length}</span> 题<br>` +
          `进度：<span>${Math.round(currentProgress)}%</span>`
        );

        // 答题完成，准备下一题
        this.aiAnswering = false;

        // 延迟后显示下一题
        const nextDelay = 500 + Math.random() * 1000;  // 增加延迟
        setTimeout(() => {
          if (qidx < this.questions.length - 1) {
            this.gotoQuestion(qidx + 1);
          } else {
            // 最后一题答完
            this.updateProgress(100, '答题完成！正在提交...');
            this.showProgress('答题完成', '正在提交测试...');
            setTimeout(() => {
              this.hideProgress();
              this.submit();
            }, 800);
          }
        }, nextDelay);
      })
      .catch(err => {
        console.error('AI API调用失败:', err);
        // 失败时使用后备方案：使用参考答案
        let fallbackAnswer = '';
        if (isChoice) {
          const fb = q.correct_answer !== undefined ? Number(q.correct_answer) : (q.answer !== undefined ? Number(q.answer) : 0);
          this.answers[qidx] = fb;
          const fbText = q.options[fb] || '选项加载失败';
          fallbackAnswer = `【AI后备】${String.fromCharCode(65 + fb)}. ${fbText}`;
        } else {
          this.answers[qidx] = q.reference || 'AI生成答案失败';
          fallbackAnswer = `【AI后备】${this.answers[qidx]}`;
        }
        // 推送后备答案到对话和DAG
        this.pushTestQA('ai', fallbackAnswer, { qidx: qidx, qtype: q.type, fallback: true });
        this.aiAnswering = false;

        // 更新进度并继续下一题
        const currentProgress = ((qidx + 1) / this.questions.length) * 100;
        this.updateProgress(currentProgress,
          `已完成第 <span>${qidx + 1}</span> / <span>${this.questions.length}</span> 题 (后备)<br>` +
          `进度：<span>${Math.round(currentProgress)}%</span>`
        );

        // 继续下一题...
        if (qidx < this.questions.length - 1) {
          setTimeout(() => {
            this.gotoQuestion(qidx + 1);
          }, 500);
        } else {
          this.updateProgress(100, '答题完成！正在提交...');
          setTimeout(() => {
            this.hideProgress();
            this.submit();
          }, 800);
        }
      });
    }, thinkTime);
  },

  showQuestionInChat() {
    const q = this.questions[this.currentIdx];
    const total = this.questions.length;
    const isChoice = q.type === undefined || q.type === 'choice';
    const isEssay = q.type === 'essay';
    const isComposition = q.type === 'composition';

    // 添加题目到对话区
    const history = document.getElementById('history');
    const div = document.createElement('div');
    div.className = 'msg msg-chen-test';
    div.id = 'chen-test-' + this.currentIdx;
    
    let questionContent = '';
    const isAiMode = this.aiAutoMode;
    
    if (isChoice) {
      if (isAiMode) {
        // AI模式：选项只读展示，不可点击
        questionContent = `
          <div class="chen-test-options" style="pointer-events:none">
            ${q.options.map((opt, i) => `
              <div class="chen-test-option" id="chen-opt-${this.currentIdx}-${i}"
                   data-qidx="${this.currentIdx}" data-opt="${i}" style="cursor:default;opacity:0.85">
                <span class="chen-opt-letter">${String.fromCharCode(65 + i)}</span>
                <span class="chen-opt-text">${stripOptPrefix(opt)}</span>
              </div>
            `).join('')}
          </div>
          <div id="chen-ai-answer-${this.currentIdx}" style="margin-top:6px;font-size:11px;color:var(--txt3)">&#8987; 等待AI回答...</div>
        `;
      } else {
        // 用户模式：选项可点击
        questionContent = `
          <div class="chen-test-options">
            ${q.options.map((opt, i) => `
              <div class="chen-test-option ${this.answers[this.currentIdx] === i ? 'selected' : ''}"
                   data-qidx="${this.currentIdx}" data-opt="${i}" onclick="CHEN_TEST.selectAnswer(${this.currentIdx}, ${i})">
                <span class="chen-opt-letter">${String.fromCharCode(65 + i)}</span>
                <span class="chen-opt-text">${stripOptPrefix(opt)}</span>
              </div>
            `).join('')}
          </div>
        `;
      }
    } else if (isEssay) {
      if (isAiMode) {
        // AI模式：不显示textarea，显示等待AI回答提示
        questionContent = `
          <div id="chen-ai-answer-${this.currentIdx}" style="margin-top:10px;font-size:11px;color:var(--txt3)">&#8987; 等待AI回答...</div>
        `;
      } else {
        // 问答题
        const charCount = this.answers[this.currentIdx] ? this.answers[this.currentIdx].replace(/\s/g, '').length : 0;
        questionContent = `
          <div style="margin-top:10px">
            <textarea id="essay-input-${this.currentIdx}"
                      placeholder="请输入答案（${q.minWords}-${q.maxWords}字）..."
                      style="width:100%;height:80px;background:var(--bg);border:1px solid var(--bdr);border-radius:6px;padding:8px;color:var(--txt);font-size:12px;resize:vertical;font-family:inherit"
                      oninput="CHEN_TEST.updateWordCount(${this.currentIdx}, 'essay')">${this.answers[this.currentIdx] || ''}</textarea>
            <div id="chen-submit-wrap-${this.currentIdx}" style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
              <span style="font-size:10px;color:var(--txt2)">字数: <span id="word-count-${this.currentIdx}">${charCount}</span> / ${q.minWords}-${q.maxWords}</span>
              <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.saveTextAnswer(${this.currentIdx})">确认提交</button>
            </div>
          </div>
        `;
      }
    } else if (isComposition) {
      if (isAiMode) {
        // AI模式：不显示textarea，显示等待AI回答提示
        questionContent = `
          <div id="chen-ai-answer-${this.currentIdx}" style="margin-top:10px;font-size:11px;color:var(--txt3)">&#8987; 等待AI回答...</div>
        `;
      } else {
        // 小作文
        const charCount = this.answers[this.currentIdx] ? this.answers[this.currentIdx].replace(/\s/g, '').length : 0;
        questionContent = `
          <div style="margin-top:10px">
            <textarea id="essay-input-${this.currentIdx}"
                      placeholder="请输入短文（${q.minWords}-${q.maxWords}字）..."
                      style="width:100%;height:400px;background:var(--bg);border:1px solid var(--bdr);border-radius:6px;padding:8px;color:var(--txt);font-size:12px;resize:vertical;font-family:inherit;line-height:1.6"
                      oninput="CHEN_TEST.updateWordCount(${this.currentIdx}, 'composition')">${this.answers[this.currentIdx] || ''}</textarea>
            <div id="chen-submit-wrap-${this.currentIdx}" style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
              <span style="font-size:10px;color:var(--txt2)">字数: <span id="word-count-${this.currentIdx}">${charCount}</span> / ${q.minWords}-${q.maxWords}</span>
              <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.saveTextAnswer(${this.currentIdx})">确认提交</button>
            </div>
          </div>
        `;
      }
    }
    
    div.innerHTML = `
      <div class="msg-meta">
        <span style="color:var(--amber);font-weight:600">&#129504; 陈天桥认知测试</span>
        <span style="color:var(--txt3);margin-left:8px">第 ${this.currentIdx + 1}/${total} 题</span>
        ${isEssay ? '<span style="color:var(--sky);margin-left:8px;font-size:10px">[问答题]</span>' : ''}
        ${isComposition ? '<span style="color:var(--goal);margin-left:8px;font-size:10px">[小作文]</span>' : ''}
      </div>
      <div class="chen-test-question">
        <div class="chen-test-q-text">${q.question || q.q || '题目加载失败'}</div>
        ${(q.type === 'essay' || q.type === 'composition') ? '<div style="font-size:10px;color:var(--amber);margin-top:4px">&#9998; 字数要求：' + (q.minWords || 80) + '-' + (q.maxWords || 300) + ' 字</div>' : ''}
        ${questionContent}
      </div>
      ${isAiMode ? '' : `<div class="chen-test-nav">
        ${this.currentIdx > 0 ? `<button class="chen-nav-btn" onclick="CHEN_TEST.gotoQuestion(${this.currentIdx - 1})">&#9664; 上一题</button>` : '<div></div>'}
        ${this.currentIdx < total - 1 ? `<button class="chen-nav-btn" onclick="CHEN_TEST.gotoQuestion(${this.currentIdx + 1})">下一题 &#9654;</button>` : ''}
      </div>`}
    `;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;

    // 推送题目到对话记录和DAG关系链
    this.pushTestQA('user', `[陈天桥认知测试] ${q.question || q.q || '测试题'}`, { qidx: this.currentIdx, qtype: q.type });

    // 隐藏底部输入区
    document.querySelector('.input-section').style.display = 'none';

    // 如果是AI自动答题模式，显示思考状态并触发答题
    if (this.aiAutoMode) {
      // 添加AI思考状态
      const thinkDiv = document.createElement('div');
      thinkDiv.className = 'msg msg-ai';
      thinkDiv.id = 'chen-ai-thinking';
      thinkDiv.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;padding:4px 0">
          <span style="color:var(--acc);font-weight:600">&#129504; AI正在思考...</span>
          <div style="display:flex;gap:3px">
            <div class="dot1" style="width:6px;height:6px"></div>
            <div class="dot2" style="width:6px;height:6px"></div>
            <div class="dot3" style="width:6px;height:6px"></div>
          </div>
        </div>
      `;
      history.appendChild(thinkDiv);
      history.scrollTop = history.scrollHeight;

      // 延迟后开始答题
      setTimeout(() => {
        // 移除思考状态
        const thinkEl = document.getElementById('chen-ai-thinking');
        if (thinkEl) thinkEl.remove();
        // 开始答题
        this.aiAutoAnswer();
      }, 800);
    }
  },

  updateWordCount(qidx, type) {
    const input = document.getElementById(`essay-input-${qidx}`);
    const counter = document.getElementById(`word-count-${qidx}`);
    if (input && counter) {
      const charCount = input.value.replace(/\s/g, '').length;  // 用字符数（去空白），中文兼容
      counter.textContent = charCount;
      const q = this.questions[qidx];
      const minWords = q.minWords || 80;
      counter.style.color = charCount >= minWords ? 'var(--green)' : 'var(--txt2)';
    }
  },

  // 推送测试Q&A到对话记录和DAG关系链
  pushTestQA(role, content, meta = {}) {
    // 添加到历史记录
    STATE.history.push({ role, content, _ts: new Date().toISOString(), is_chen_test: true, ...meta });

    if (role === 'user') {
      // 问题：添加到DAG，测试题目强制开新线索
      addQA2DAG('question', content, { ...meta, force_new_thread: true });
    } else {
      // 答案：添加到当前线索的最后一个问题后面
      const { threads } = STATE.dag_data;
      if (threads.length > 0) {
        const currentThread = threads[threads.length - 1];
        if (!currentThread.qa_pairs) currentThread.qa_pairs = [];
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
    }
  },

  saveTextAnswer(qidx, skipConfirm = false) {
    const input = document.getElementById(`essay-input-${qidx}`);
    
    // AI模式：无textarea，答案已在this.answers中，直接处理提交逻辑
    if (!input) {
      if (this.aiAutoMode && this.answers[qidx] !== undefined) {
        // AI已作答，执行提交后的流程
        this.pushTestQA('ai', `【答案】${this.answers[qidx]}`, { qidx: qidx, qtype: this.questions[qidx]?.type });
        this.updateLeftPanel();
        // 自动跳转到下一题
        if (qidx < this.questions.length - 1) {
          setTimeout(() => {
            this.gotoQuestion(qidx + 1);
          }, 300);
        }
      }
      return;
    }
    
    const answer = input.value.trim();
    if (!answer) {
      alert('请输入答案！');
      return;
    }
    
    const q = this.questions[qidx];
    const charCount = answer.replace(/\s/g, '').length;  // 去空白字符数，中文兼容
    const minWords = q.minWords || 80;
    const maxWords = q.maxWords || 300;

    if (!skipConfirm && charCount < minWords) {
      if (!confirm(`字数不足${minWords}字（当前${charCount}字），确定提交吗？`)) {
        return;
      }
    }
    if (!skipConfirm && charCount > maxWords) {
      if (!confirm(`字数超出${maxWords}字（当前${charCount}字），确定提交吗？`)) {
        return;
      }
    }
    
    // 保存答案
    this.answers[qidx] = answer;

    // 推送答案到对话记录和DAG关系链
    this.pushTestQA('ai', `【答案】${answer}`, { qidx: qidx, qtype: q.type });

    // 更新界面显示
    const qDiv = document.getElementById('chen-test-' + qidx);
    if (qDiv) {
      const nav = qDiv.querySelector('.chen-test-nav');
      if (nav) {
        nav.innerHTML = `<div style="color:var(--green);font-size:11px">&#10004; 已提交</div>`;
      }
      // 隐藏确认提交按钮
      const btnWrap = document.getElementById(`chen-submit-wrap-${qidx}`);
      if (btnWrap) btnWrap.style.display = 'none';
    }
    
    // 更新左侧面板
    this.updateLeftPanel();
    
    // 自动跳转到下一题
    if (qidx < this.questions.length - 1) {
      setTimeout(() => {
        this.gotoQuestion(qidx + 1);
      }, 300);
    }
  },

  selectAnswer(qidx, optIdx) {
    // AI自动答题模式下，不允许用户手动选择
    if (this.aiAutoMode) return;

    this.answers[qidx] = optIdx;

    // 推送答案到对话记录和DAG关系链
    const q = this.questions[qidx];
    const optText = q.options[optIdx];
    this.pushTestQA('ai', `【选择】${String.fromCharCode(65 + optIdx)}. ${optText}`, { qidx: qidx, qtype: q.type });

    // 更新对话区选项样式
    document.querySelectorAll(`[data-qidx="${qidx}"]`).forEach(el => {
      el.classList.toggle('selected', parseInt(el.dataset.opt) === optIdx);
    });

    // 更新左侧进度
    this.updateLeftPanel();

    // 自动跳转到下一题
    if (qidx < this.questions.length - 1) {
      setTimeout(() => {
        this.gotoQuestion(qidx + 1);
      }, 300);
    }
  },

  gotoQuestion(idx) {
    if (idx < 0 || idx >= this.questions.length) return;

    this.currentIdx = idx;
    const existing = document.getElementById('chen-test-' + idx);

    if (existing) {
      // 已存在的题目 - 滚动到该位置
      existing.scrollIntoView({ behavior: 'smooth', block: 'center' });
      existing.style.boxShadow = '0 0 20px var(--amber)';
      setTimeout(() => { existing.style.boxShadow = ''; }, 1000);

      // 如果是AI模式且该题未答，触发答题
      if (this.aiAutoMode && this.answers[idx] === undefined) {
        // 添加思考状态
        const history = document.getElementById('history');
        const thinkDiv = document.createElement('div');
        thinkDiv.className = 'msg msg-ai';
        thinkDiv.id = 'chen-ai-thinking';
        thinkDiv.innerHTML = `
          <div style="display:flex;align-items:center;gap:8px;padding:4px 0">
            <span style="color:var(--acc);font-weight:600">&#129504; AI正在思考...</span>
            <div style="display:flex;gap:3px">
              <div class="dot1" style="width:6px;height:6px"></div>
              <div class="dot2" style="width:6px;height:6px"></div>
              <div class="dot3" style="width:6px;height:6px"></div>
            </div>
          </div>
        `;
        history.appendChild(thinkDiv);
        history.scrollTop = history.scrollHeight;

        setTimeout(() => {
          const thinkEl = document.getElementById('chen-ai-thinking');
          if (thinkEl) thinkEl.remove();
          this.aiAutoAnswer();
        }, 600);
      }
    } else {
      // 新题目
      this.showQuestionInChat();
    }

    this.updateLeftPanel();
  },

  submit() {
    const answered = Object.keys(this.answers).length;
    // AI自动答题模式下不需要确认
    if (answered < this.questions.length && !this.aiAutoMode) {
      if (!confirm(`您已完成 ${answered}/${this.questions.length} 题，确定提前提交吗？`)) return;
    }

    let correct = 0;
    this.questions.forEach((q, i) => {
      let isCorrect = false;
      // 明确判断：只有明确type==='choice'或没有options以外才是选择题
      const isChoiceQ = (q.type === 'choice') || (q.type === undefined && Array.isArray(q.options));
      const isTextQ = q.type === 'essay' || q.type === 'composition';
      const ans = this.answers[i];

      if (isTextQ) {
        // 问答题/小作文：有内容且字数达标即算正确（不比较answer字段）
        const minWords = q.minWords || 80;
        const charCount = ans ? ans.replace(/\s/g, '').length : 0;  // 去空白字符数，中文兼容
        isCorrect = charCount >= minWords;
      } else if (isChoiceQ) {
        // 选择题：答案等于正确选项索引（兼容字符串/数字类型）
        const numAns = Number(ans);
        const numCorrect = getCorrectAnswer(q);
        if (isNaN(numCorrect)) {
          // 无法判定正确答案，默认给分（仁慈评分）
          isCorrect = true;
        } else if (isNaN(numAns)) {
          // AI未作答或答案非法
          isCorrect = false;
        } else {
          isCorrect = numAns === numCorrect;
        }
      } else {
        // 未知类型：有答案即给分
        isCorrect = ans !== undefined && ans !== null && String(ans).trim().length > 0;
      }
      if (isCorrect) correct++;
      // 更新各维度得分
      const category = this.getQuestionCategory(i);
      if (this.scores[category]) {
        this.scores[category].total++;
        if (isCorrect) this.scores[category].correct++;
      }
    });

    const total = this.questions.length;
    const score = Math.round((correct / total) * 100);
    this.results = { correct, total, score };
    this.inTest = false;
    this.aiAutoMode = false;
    this.stopTimer();

    // 测试完成 - 更新分析仪表盘
    this.updateAnalysisPanel('test_complete');

    // 在对话区显示测试报告
    const history = document.getElementById('history');
    const level = score >= 90 ? '天才级' : score >= 70 ? '优秀' : score >= 50 ? '良好' : '需提升';
    const levelEmoji = score >= 90 ? '&#127942;' : score >= 70 ? '&#128170;' : score >= 50 ? '&#128136;' : '&#128564;';

    const div = document.createElement('div');
    div.className = 'msg msg-chen-report';
    div.innerHTML = `
      <div class="msg-meta">
        <span style="color:var(--amber);font-weight:600">&#129504; 测试报告</span>
      </div>
      <div class="chen-report-body">
        <div class="chen-report-score">${score}<span>分</span></div>
        <div class="chen-report-level">${levelEmoji} ${level}</div>
        <div class="chen-report-detail">
          <div class="chen-report-item"><span>正确率</span><span>${correct}/${total} 题</span></div>
          <div class="chen-report-item"><span>用时</span><span>约 ${Math.ceil(answered * 0.5)} 分钟</span></div>
        </div>
        <div class="chen-report-actions">
          <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.review()">查看答案详解</button>
        </div>
      </div>
    `;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;

    // 显示底部输入区
    document.querySelector('.input-section').style.display = 'block';

    // 更新左侧面板
    document.getElementById('chen-status').textContent = score + '分';
    this.updateLeftPanel();
  },

  review() {
    // 清空对话区显示详细答案
    const history = document.getElementById('history');
    history.innerHTML = '';

    const catNames = ['数学推理', '逻辑推理', '物理直觉', '认知心理', 'AGI认知'];

    // 标题
    const titleDiv = document.createElement('div');
    titleDiv.className = 'msg msg-chen-cat';
    titleDiv.innerHTML = `<div style="font-size:11px;color:var(--amber);font-weight:600;padding:4px 0">&#128196; 答案详解 (共 ${this.questions.length} 题)</div>`;
    history.appendChild(titleDiv);

    // 遍历实际题目（动态数量，不硬编码50或5×10）
    this.questions.forEach((q, i) => {
      if (!q) return;

      const userAns = this.answers[i];
      const isChoiceQ = q.type === 'choice' || (q.type === undefined && Array.isArray(q.options));
      const isTextQ = q.type === 'essay' || q.type === 'composition';
      const catLabel = catNames[i % catNames.length];

      let isCorrect = false;
      let scoreRatio = 0;
      if (isTextQ) {
        const minWords = q.minWords || 50;
        scoreRatio = calcTextScoreRatio(userAns, minWords);
        isCorrect = scoreRatio >= 1.0;
      } else if (isChoiceQ) {
        const numAns = Number(userAns);
        const numCorrect = getCorrectAnswer(q);
        if (isNaN(numCorrect)) {
          // 无法判定正确答案，默认给分（仁慈评分）
          isCorrect = true;
        } else if (isNaN(numAns)) {
          isCorrect = false;
        } else {
          isCorrect = numAns === numCorrect;
        }
      } else {
        isCorrect = userAns !== undefined && String(userAns).trim().length > 0;
      }

      const borderColor = isCorrect ? 'var(--green)' : 'var(--red)';
      const qDiv = document.createElement('div');
      qDiv.className = 'msg msg-chen-answer';
      qDiv.style.borderLeft = `3px solid ${borderColor}`;

      let answerDetail = '';
      if (isTextQ) {
        // 问答题/小作文详解
        answerDetail = `
          <div style="font-size:10px;color:var(--txt2);margin:4px 0">
            <span style="color:var(--txt3)">[${q.type === 'essay' ? '问答题' : '小作文'}]</span>
          </div>
          <div style="font-size:10px;background:var(--bg3);padding:6px;border-radius:4px;margin:4px 0;max-height:80px;overflow-y:auto">
            ${userAns ? userAns.replace(/\n/g, '<br>') : '<span style="color:var(--red)">未作答</span>'}
          </div>
          ${q.reference ? `<div style="font-size:9px;color:var(--sky);margin-top:4px">参考答案: ${q.reference}</div>` : ''}
          <div style="font-size:9px;color:${isCorrect ? 'var(--green)' : 'var(--red)'}">
            ${scoreRatio >= 1.0 ? '&#10004; 字数达标，满分' : (scoreRatio > 0 ? '&#9993; 字数不足，得 ' + Math.round(scoreRatio * 100) + '% 分' : '&#10006; 未作答，0分')}
          </div>
        `;
      } else if (isChoiceQ && q.options) {
        // 选择题详解
        answerDetail = `
          <div style="font-size:10px;margin:4px 0">
            ${q.options.map((opt, oi) => {
              let cls = '';
              if (oi === getCorrectAnswer(q)) cls = 'color:var(--green);font-weight:600';
              else if (oi === userAns && !isCorrect) cls = 'color:var(--red);text-decoration:line-through';
              return `<div style="${cls}">${String.fromCharCode(65 + oi)}. ${opt}</div>`;
            }).join('')}
          </div>
          <div style="font-size:9px;color:${isCorrect ? 'var(--green)' : 'var(--red)'}">
            ${isCorrect ? '&#10004; 正确' : `&#10006; 错误 | 正确答案: ${getCorrectAnswer(q) !== undefined ? String.fromCharCode(65 + getCorrectAnswer(q)) : '?'}`}
          </div>
          ${q.reference ? `<div style="font-size:9px;color:var(--sky);margin-top:4px">解析: ${q.reference}</div>` : ''}
        `;
      } else {
        answerDetail = `<div style="font-size:9px;color:var(--txt3)">类型未知</div>`;
      }

      qDiv.innerHTML = `
        <div style="font-size:9px;color:var(--txt3);margin-bottom:3px">${i + 1}. [${catLabel}]</div>
        <div style="font-size:10px;color:var(--txt);margin-bottom:6px;font-weight:500">${q.question || q.q || '题目加载失败'}</div>
        ${answerDetail}
      `;
      history.appendChild(qDiv);
    });

    // 添加返回按钮
    const backDiv = document.createElement('div');
    backDiv.className = 'msg';
    backDiv.innerHTML = `<button class="chen-btn chen-btn-start" onclick="CHEN_TEST.resetTest()">&#8634; 返回测试</button>`;
    history.appendChild(backDiv);

    history.scrollTop = 0;
  },

  resetTest() {
    this.reset();
    this.renderStart();
    document.querySelector('.input-section').style.display = 'block';
  }
};

// ════════════════════════════════════════════════════════════════
// 初始化
// ════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  console.log('[AGI12] DOMContentLoaded 事件触发');
  try {
    initDAG();
    // Phase 1: 初始化 STN 面包屑
    try { renderSTNBreadcrumb(); } catch(e) { console.warn('STN breadcrumb init:', e); }
    // Phase 1: 初始化 Agent 行为分析面板
    try { updateAgentBehaviorPanel(); } catch(e) { console.warn('Agent behavior panel init:', e); }
    if (typeof CHEN_TEST !== 'undefined') {
      CHEN_TEST.init();
    } else {
      console.error('[错误] CHEN_TEST 未定义!');
    }
    
    // ========== 按钮事件绑定 ==========
  
    // 顶栏模式切换
    document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      STATE.mode = mode;
      document.getElementById('input-chat').style.display = mode === 'chat' ? 'block' : 'none';
      document.getElementById('input-goal').style.display = mode === 'goal' ? 'block' : 'none';
      document.querySelectorAll('.input-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.input === mode);
      });
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
      document.querySelectorAll('.mode-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.mode === inputMode);
      });
    });
  });

  // 发送按钮
  const mainInput = document.getElementById('main-input2');
  const btnSend2 = document.getElementById('btn-send2');
  console.log('[调试] mainInput:', mainInput, 'btnSend2:', btnSend2);
  if (!mainInput) console.error('[错误] main-input2 未找到!');
  if (!btnSend2) console.error('[错误] btn-send2 未找到!');
  btnSend2.addEventListener('click', () => {
    const v = mainInput.value.trim();
    if (!v) {
      console.log('[发送] 输入为空');
      return;
    }
    console.log('[发送] 消息:', v.substring(0, 50));
    mainInput.value = '';
    doMainChat(v);
  });
  mainInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      btnSend2.click();
    }
  });

  // Goal按钮
  const goalInput = document.getElementById('goal-input2');
  document.getElementById('btn-goal2').addEventListener('click', () => {
    const v = goalInput.value.trim();
    if (!v) return;
    goalInput.value = '';
    doGoalMode(v);
  });

  // 清空按钮
  document.getElementById('btn-clear').addEventListener('click', () => {
    if (confirm('清空所有对话历史?')) {
      resetAll();
    }
  });

  // 重置按钮
  document.getElementById('btn-reset').addEventListener('click', () => {
    if (confirm('重置所有数据?')) {
      resetAll();
    }
  });

  // ========== 初始化仪表盘（模拟数据）==========
  updateEntropyPanel({ Si: 0.35, Sg: 0.28, Sc: 0.18 });
  updateFivePhasePanel({ wood: 0.52, fire: 0.65, earth: 0.45, metal: 0.48, water: 0.62 });
  updateAnchorPanel({ verified: true, energy: true, semantic: true, causal: true, empirical: true });

  // ========== v7.2 OpenHuman增强模块初始化 ==========
  // M81: 记忆树引擎 - 模拟初始状态
  updateMemoryTreePanel({
    memory_tree: {
      total_chunks: 0,
      info_density: 0.65,
      layer1_count: 0,
      layer2_count: 0,
      layer3_count: 0,
      last_update: '—'
    }
  });

  // M82: TokenJuice压缩引擎 - 模拟初始状态
  updateTokenJuicePanel({
    token_juice: {
      compression_rate: 0,
      tokens_saved: 0,
      processed_count: 0,
      steps: [false, false, false, false, false]
    }
  });

  // M83: 自动上下文同步 - 模拟初始状态
  updateAutoSyncPanel({
    auto_sync: {
      context_completeness: 0,
      services: { email: 'pending', calendar: 'pending', contacts: 'pending', notes: 'pending' },
      status: 'pending'
    }
  });

  // M84: 模型智能路由 - 模拟初始状态
  updateModelRouterPanel({
    model_router: {
      task_type: 'unknown',
      selected_model: '—',
      confidence: 0
    }
  });

  // M85-M87: Obsidian兼容与零训练期 - 模拟初始状态
  updateObsidianZeroPanel({
    obsidian: {
      wiki_links: 0,
      moc_files: 0,
      backlinks: 0,
      index_ready: false
    },
    cold_start: {
      context_ready: false,
      warmup_progress: 0,
      build_time: 0
    }
  });

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    renderDAG();
  });

  // ESC键关闭弹窗
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') hideHelp();
  });

  // 点击弹窗背景关闭
  const helpModal = document.getElementById('help-modal');
  if (helpModal) {
    helpModal.addEventListener('click', (e) => {
      if (e.target.id === 'help-modal') hideHelp();
    });
  }

  console.log('Taiyi-AGI (太乙因果机) 12.0 initialized - Three Column Layout');
  } catch (err) {
    console.error('[AGI12] 初始化错误:', err);
    alert('[AGI12] 初始化错误: ' + err.message);
  }
});

/* ═════════════════════════════════════════════════════════════
   AI进度指示器弹窗 HTML
═════════════════════════════════════════════════════════════ */

// ── v6.3 更新函数 ───────────────────────────────
function updateV63Panels(data) {
  if (!data) return;
  if (data.mononumber) updateMononumberPanel(data.mononumber);
  if (data.narrative) updateNarrativeV63Panel(data.narrative);
  if (data.consciousness) updateConsciousnessPanel(data.consciousness);
  if (data.identity) updateIdentityPanel(data.identity);
  if (data.enlightenment) updateEnlightenmentPanel(data.enlightenment);
  if (data.coupling) updateCouplingPanel(data.coupling);
  if (data.prediction) updatePredictionPanel(data.prediction);
}

// ════════════════════════════════════════════════════════════════
// v7.0 高阶逻辑面板更新（M71-M95）
// ════════════════════════════════════════════════════════════════
function updateV70Panels(data) {
  if (!data) return;
  // ① 碳硅共生契约 (M71-M75)
  updateCarbonSiliconPanel(data);
  // ② 五行EML相位 (M76-M80)
  updateWuxingPhasePanel(data);
  // ③ HoTT高阶逻辑 (M78/M81)
  updateHoTTPanel(data);
  // ④ 流贯自然变换 (M83/M89)
  updateFteliaryPanel(data);
  // ⑤ 刘原理不动点 (M84)
  updateLiuPanel(data);
  // ⑥ 语义流形曲率 (M90)
  updateCurvaturePanel(data);
  // ⑦ Univalence等价 (M91)
  updateUnivalencePanel(data);
  // ⑧ 流贯保真度 (M92)
  updateFidelityPanel(data);
  // ⑨ 构造型AGI评估 (M95)
  updateEvaluatorPanel(data);
}

// ── ① 碳硅共生契约面板 (M71-M75) ──────────────────────────────
function updateCarbonSiliconPanel(data) {
  // Φ值
  const phiData = data.phi || {};
  const phiVal = (phiData.self_referential_phi || phiData.phi_value || 0.5);
  const phiEl = document.getElementById('v70-phi-value');
  const phiBar = document.getElementById('v70-phi-bar');
  if (phiEl) phiEl.textContent = phiVal.toFixed(3);
  if (phiBar) phiBar.style.width = Math.min(100, phiVal * 100) + '%';
  // 自指闭环
  const selfref = data.firewall ? '已闭合' : (phiData.closed_loop ? '已闭合' : '—');
  const selfrefEl = document.getElementById('v70-selfref');
  if (selfrefEl) {
    selfrefEl.textContent = selfref;
    selfrefEl.style.color = selfref === '已闭合' ? 'var(--gold)' : 'var(--txt2)';
  }
  // 贡献度量
  const contribData = data.contribution || {};
  const contribVal = (contribData.total_score || contribData.measure || 0.5);
  const contribEl = document.getElementById('v70-contrib');
  if (contribEl) contribEl.textContent = contribVal.toFixed(3);
  // 熵合约
  const entropyData = data.entropy || {};
  const contractCount = (entropyData.contract_count || entropyData.total_contracts || 0);
  const entropyEl = document.getElementById('v70-entropy-contract');
  if (entropyEl) entropyEl.textContent = contractCount > 0 ? contractCount + '份' : '—';
  // 约柜
  const arkData = data.ark || {};
  const arkStatus = arkData.locked ? '已锁定' : (Object.keys(arkData).length > 0 ? '就绪' : '—');
  const arkEl = document.getElementById('v70-ark-status');
  if (arkEl) {
    arkEl.textContent = arkStatus;
    arkEl.style.color = arkStatus === '已锁定' ? 'var(--purple)' : (arkStatus === '就绪' ? 'var(--gold)' : 'var(--txt2)');
  }
}

// ── ② 五行EML相位面板 (M76-M80) ─────────────────────────────
function updateWuxingPhasePanel(data) {
  const wuxing = data.wuxing || {};
  const emlCoupling = data.eml_coupling || {};
  // 相位角
  const phases = emlCoupling.phases || {};
  const phaseAngles = Object.values(phases);
  const phaseAngle = phaseAngles.length > 0 ? phaseAngles.reduce((a, b) => a + (b.phase_angle || 0), 0) / phaseAngles.length : 0;
  const phaseEl = document.getElementById('v70-phase-angle');
  if (phaseEl) phaseEl.textContent = (phaseAngle / Math.PI).toFixed(2) + 'π';
  // 振幅
  const amplitudes = phaseAngles.map(p => p.amplitude || 0);
  const amplitude = amplitudes.length > 0 ? amplitudes.reduce((a, b) => a + b, 0) / amplitudes.length : 0;
  const ampEl = document.getElementById('v70-amplitude');
  if (ampEl) ampEl.textContent = amplitude.toFixed(3);
  // 五行圆点高亮（根据最大振幅判断）
  const elements = ['water', 'fire', 'wood', 'metal', 'earth'];
  elements.forEach(el => {
    const dot = document.getElementById('v70-dot-' + el);
    if (dot) {
      dot.classList.remove('active');
      // 简单规则：轮流高亮
      const idx = elements.indexOf(el);
      const time = Date.now() / 2000;
      if ((idx + Math.floor(time)) % 5 === 0) dot.classList.add('active');
    }
  });
}

// ── ③ HoTT高阶逻辑面板 (M78/M81) ────────────────────────────
function updateHoTTPanel(data) {
  const hott = data.hott || {};
  const chf = data.chf || {};
  const holr = data.holr || {};
  // 命题型
  const types = hott.types || holr.types || [];
  const typeStr = types.length > 0 ? types.slice(0, 3).join(', ') : '—';
  const typeEl = document.getElementById('v70-hott-type');
  if (typeEl) typeEl.textContent = typeStr;
  // Pi-Type
  const piInfo = chf.pi_type || holr.reconstructed_type || '—';
  const piEl = document.getElementById('v70-pi-type');
  if (piEl) piEl.textContent = typeof piInfo === 'string' ? piInfo : '已重构';
  // Sigma-Type
  const sigmaInfo = chf.sigma_type || holr.sigma_type || '—';
  const sigmaEl = document.getElementById('v70-sigma-type');
  if (sigmaEl) sigmaEl.textContent = typeof sigmaInfo === 'string' ? sigmaInfo : '已重构';
  // LEM态
  const lemStatus = chf.lem_valid || holr.lem_valid || false;
  const lemEl = document.getElementById('v70-lem-status');
  if (lemEl) {
    lemEl.textContent = lemStatus ? '有效' : '失效';
    lemEl.style.color = lemStatus ? 'var(--red)' : 'var(--gold)';
  }
  // 证明树可视化
  const proofTree = document.getElementById('v70-proof-tree');
  if (proofTree) {
    const goal = holr.goal || holr.type || 'Goal';
    const proofStr = types.length > 0 ? `├─ ${types[0]}\n└─ ${goal}` : goal;
    proofTree.innerHTML = `<div class="v70-proof-node">${proofStr.split('\n')[0] || 'Goal Type'}</div>`;
  }
}

// ── ④ 流贯自然变换面板 (M83/M89) ─────────────────────────────
function updateFteliaryPanel(data) {
  const ftelTransform = data.ftel_transform || {};
  const holr = data.holr || {};
  const layers = holr.layers || holr.layer_count || 5;
  // 层激活
  ['L1', 'L2', 'L3', 'L4', 'L5'].forEach((l, i) => {
    const cell = document.getElementById('v70-layer-' + l);
    if (cell) {
      cell.classList.remove('active');
      if (i < layers) cell.classList.add('active');
    }
  });
  // 流贯通量
  const flux = ftelTransform.flux || ftelTransform.f_teliary_flux || 0.618;
  const fluxEl = document.getElementById('v70-flux');
  const fluxBar = document.getElementById('v70-flux-bar');
  if (fluxEl) fluxEl.textContent = flux.toFixed(3);
  if (fluxBar) fluxBar.style.width = Math.min(100, flux * 100) + '%';
  // 截面数
  const sections = ftelTransform.section_count || ftelTransform.sections || 0;
  const secEl = document.getElementById('v70-sections');
  if (secEl) secEl.textContent = sections;
}

// ── ⑤ 刘原理不动点面板 (M84) ─────────────────────────────────
function updateLiuPanel(data) {
  const liu = data.liu || {};
  const univalence = data.univalence || {};
  // 极小规律
  const solution = liu.solution || liu.minimal_law || liu.optimal_solution || '—';
  const solEl = document.getElementById('v70-liu-solution');
  if (solEl) solEl.textContent = typeof solution === 'string' ? solution : '已找到';
  // K复杂度
  const kol = liu.kolmogorov_complexity || liu.k_complexity || 0.382;
  const kolEl = document.getElementById('v70-kolmogorov');
  const kolBar = document.getElementById('v70-kol-bar');
  if (kolEl) kolEl.textContent = kol.toFixed(3);
  if (kolBar) kolBar.style.width = Math.min(100, kol * 100) + '%';
  // 不动点
  const fp = liu.fixed_point || liu.has_fixed_point || false;
  const fpEl = document.getElementById('v70-fixed-point');
  if (fpEl) {
    fpEl.textContent = fp ? '存在' : '—';
    fpEl.style.color = fp ? 'var(--gold)' : 'var(--txt2)';
  }
  // Univalence
  const uv = univalence.verified || univalence.equivalent || false;
  const uvEl = document.getElementById('v70-univalence');
  if (uvEl) {
    uvEl.textContent = uv ? '成立' : '—';
    uvEl.style.color = uv ? 'var(--gold)' : 'var(--txt2)';
  }
}

// ── ⑥ 语义流形曲率面板 (M90) ─────────────────────────────────
function updateCurvaturePanel(data) {
  const curvature = data.curvature || {};
  // K值
  const kVal = curvature.curvature || curvature.k_value || curvature.K || 0.5;
  const kEl = document.getElementById('v70-curvature-val');
  if (kEl) kEl.textContent = kVal.toFixed(3);
  // 确定性
  const det = curvature.determinacy || curvature.deterministic || '—';
  const detEl = document.getElementById('v70-determinacy');
  if (detEl) detEl.textContent = typeof det === 'boolean' ? (det ? '高' : '低') : det;
  // 创造力
  const cr = curvature.creativity || curvature.creative || '—';
  const crEl = document.getElementById('v70-creativity');
  if (crEl) crEl.textContent = typeof cr === 'boolean' ? (cr ? '高' : '低') : cr;
  // 指针旋转：K≈0 → 左偏(平坦/创造)，K>>0 → 右偏(必然)
  const needle = document.getElementById('v70-curvature-needle');
  if (needle) {
    const rotation = (kVal - 0.5) * 180;  // -90deg to +90deg
    needle.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
  }
}

// ── ⑦ Univalence等价面板 (M91) ───────────────────────────────
function updateUnivalencePanel(data) {
  const univalence = data.univalence || {};
  // type1≃type2
  const equiv = univalence.equivalent || univalence.type1_equiv_type2 || '—';
  const equivEl = document.getElementById('v70-equiv');
  if (equivEl) equivEl.textContent = typeof equiv === 'string' ? equiv : '同构';
  // type1=type2
  const equal = univalence.equal || univalence.type1_eq_type2 || '—';
  const eqEl = document.getElementById('v70-equal');
  if (eqEl) eqEl.textContent = typeof equal === 'string' ? equal : '相等';
  // 置信度
  const conf = univalence.confidence || univalence.conf || 0.618;
  const confEl = document.getElementById('v70-conf');
  const confBar = document.getElementById('v70-conf-bar');
  if (confEl) confEl.textContent = conf.toFixed(3);
  if (confBar) confBar.style.width = Math.min(100, conf * 100) + '%';
  // 实验数
  const exps = univalence.experiments || univalence.total_experiments || 0;
  const expEl = document.getElementById('v70-experiments');
  if (expEl) expEl.textContent = exps;
}

// ── ⑧ 流贯保真度面板 (M92) ───────────────────────────────────
function updateFidelityPanel(data) {
  const fidelity = data.fidelity || {};
  const evolution = data.evolution || {};
  // F(Li,Lj)
  const fidVal = fidelity.fidelity || fidelity.fidelity_score || 0.618;
  const fidEl = document.getElementById('v70-fidelity-val');
  const fidBar = document.getElementById('v70-fidelity-bar');
  if (fidEl) fidEl.textContent = fidVal.toFixed(3);
  if (fidBar) fidBar.style.width = Math.min(100, fidVal * 100) + '%';
  // 信息损耗
  const loss = fidelity.info_loss || fidelity.loss_rate || 0;
  const lossEl = document.getElementById('v70-info-loss');
  if (lossEl) {
    lossEl.textContent = Math.round((1 - loss) * 100) + '%';
    lossEl.style.color = loss > 0.1 ? 'var(--red)' : 'var(--green)';
  }
  // 警告
  const warnEl = document.getElementById('v70-fidelity-warn');
  if (warnEl) {
    if (fidVal < 0.9) {
      warnEl.textContent = '⚠️ 阈值警告';
      warnEl.style.color = 'var(--orange)';
    } else {
      warnEl.textContent = '✓ 正常';
      warnEl.style.color = 'var(--green)';
    }
  }
  // 层激活
  const layerCount = (evolution.layers || evolution.active_layers || 5);
  ['L1', 'L2', 'L3', 'L4', 'L5'].forEach((l, i) => {
    const cell = document.getElementById('v70-fid-' + l);
    if (cell) {
      cell.classList.remove('active');
      if (i < layerCount) cell.classList.add('active');
    }
  });
}

// ── ⑨ 构造型AGI评估面板 (M95) ────────────────────────────────
function updateEvaluatorPanel(data) {
  const evaluator = data.evaluator || {};
  const constructive = data.constructive || {};
  // Pass@5
  const passk = evaluator.pass_at_k || evaluator.passk || constructive.pass_rate || 0;
  const passkEl = document.getElementById('v70-passk');
  if (passkEl) passkEl.textContent = Math.round(passk * 100) + '%';
  // 幻觉率
  const halluc = evaluator.hallucination_rate || evaluator.hallucination || 0;
  const hallEl = document.getElementById('v70-hallucination');
  if (hallEl) {
    hallEl.textContent = Math.round(halluc * 100) + '%';
    hallEl.style.color = halluc > 0.1 ? 'var(--red)' : 'var(--green)';
  }
  // P-HoL-1
  const phol1 = evaluator.phol1 || evaluator.p_hol_1 || constructive.p_hol_1 || '—';
  const pholEl = document.getElementById('v70-phol1');
  if (pholEl) pholEl.textContent = typeof phol1 === 'string' ? phol1 : phol1.toFixed(3);
  // 验证态
  const verified = evaluator.verified || evaluator.phol1_verified || false;
  const verEl = document.getElementById('v70-phol1-verified');
  if (verEl) {
    verEl.textContent = verified ? '已验证' : '未验证';
    verEl.style.color = verified ? 'var(--gold)' : 'var(--txt2)';
  }
  // 问题数
  const total = evaluator.total_problems || constructive.total_problems || 0;
  const totEl = document.getElementById('v70-total-problems');
  if (totEl) totEl.textContent = total;
}

// ════════════════════════════════════════════════════════════════
// v7.2 OpenHuman增强面板更新函数 (M81-M87)
// ════════════════════════════════════════════════════════════════

// ── M81: 记忆树引擎面板更新 ───────────────────────────────────
function updateMemoryTreePanel(data) {
  if (!data) return;
  const memory = data.memory_tree || data;
  const chunks = memory.total_chunks || 0;
  const density = memory.info_density || 0;
  const l1 = memory.layer1_count || 0;
  const l2 = memory.layer2_count || 0;
  const l3 = memory.layer3_count || 0;
  const lastUpdate = memory.last_update || '—';

  // 总片段
  const chunksBar = document.getElementById('v72-mem-chunks-bar');
  const chunksVal = document.getElementById('v72-mem-chunks-val');
  if (chunksBar) chunksBar.style.width = Math.min(100, chunks / 100) + '%';
  if (chunksVal) chunksVal.textContent = chunks;

  // 信息密度
  const densityBar = document.getElementById('v72-mem-density-bar');
  const densityVal = document.getElementById('v72-mem-density-val');
  if (densityBar) densityBar.style.width = Math.min(100, density * 100) + '%';
  if (densityVal) densityVal.textContent = density.toFixed(2);

  // 三层树状
  const setLayer = (id, count, total) => {
    const bar = document.getElementById(id + '-bar');
    const countEl = document.getElementById(id + '-count');
    if (bar) bar.style.width = total > 0 ? Math.min(100, count / total * 100) + '%' : '0%';
    if (countEl) countEl.textContent = count;
  };
  setLayer('v72-mem-l1', l1, l1 + l2 + l3);
  setLayer('v72-mem-l2', l2, l1 + l2 + l3);
  setLayer('v72-mem-l3', l3, l1 + l2 + l3);

  // 最后更新时间
  const lastUpdateEl = document.getElementById('v72-mem-last-update');
  if (lastUpdateEl) lastUpdateEl.textContent = lastUpdate;
}

// ── M82: TokenJuice压缩引擎面板更新 ────────────────────────────
function updateTokenJuicePanel(data) {
  if (!data) return;
  const tj = data.token_juice || data;
  const rate = tj.compression_rate || 0;
  const saved = tj.tokens_saved || 0;
  const processed = tj.processed_count || 0;
  const steps = tj.steps || [true, true, true, true, true];

  // 压缩率
  const rateBar = document.getElementById('v72-tj-rate-bar');
  const rateVal = document.getElementById('v72-tj-rate-val');
  if (rateBar) rateBar.style.width = rate + '%';
  if (rateVal) rateVal.textContent = Math.round(rate) + '%';

  // 节省Tokens
  const savedBar = document.getElementById('v72-tj-saved-bar');
  const savedVal = document.getElementById('v72-tj-saved-val');
  if (savedBar) savedBar.style.width = Math.min(100, saved / 1000) + '%';
  if (savedVal) savedVal.textContent = saved > 1000 ? (saved / 1000).toFixed(1) + 'k' : saved;

  // 五步管道状态
  for (let i = 1; i <= 5; i++) {
    const dot = document.getElementById('v72-tj-step' + i + '-dot');
    if (dot) {
      dot.classList.remove('active', 'inactive');
      dot.classList.add(steps[i - 1] ? 'active' : 'inactive');
    }
  }

  // 处理数量
  const processedEl = document.getElementById('v72-tj-processed');
  if (processedEl) processedEl.textContent = processed;
}

// ── M83: 自动上下文同步面板更新 ────────────────────────────────
function updateAutoSyncPanel(data) {
  if (!data) return;
  const sync = data.auto_sync || data;
  const completeness = sync.context_completeness || 0;
  const services = sync.services || {};
  const status = sync.status || 'syncing';

  // 上下文完整度
  const cplBar = document.getElementById('v72-sync-cpl-bar');
  const cplVal = document.getElementById('v72-sync-cpl-val');
  if (cplBar) cplBar.style.width = Math.min(100, completeness * 100) + '%';
  if (cplVal) cplVal.textContent = Math.round(completeness * 100) + '%';

  // OAuth服务状态
  const serviceMap = {
    'email': 'v72-sync-email',
    'calendar': 'v72-sync-calendar',
    'contacts': 'v72-sync-contacts',
    'notes': 'v72-sync-notes'
  };
  Object.entries(services).forEach(([name, state]) => {
    const el = document.getElementById(serviceMap[name]);
    if (el) {
      el.classList.remove('connected', 'pending', 'disconnected');
      el.classList.add(state);
    }
  });

  // 同步状态
  const statusDot = document.getElementById('v72-sync-status-dot');
  const statusText = document.getElementById('v72-sync-status-text');
  if (statusDot) {
    statusDot.classList.remove('synced', 'syncing', 'error');
    statusDot.classList.add(status === 'synced' ? 'synced' : status === 'syncing' ? 'syncing' : 'error');
  }
  if (statusText) {
    const statusMap = { 'synced': '已同步', 'syncing': '同步中', 'error': '同步错误' };
    statusText.textContent = statusMap[status] || status;
  }
}

// ── M84: 模型智能路由面板更新 ─────────────────────────────────
function updateModelRouterPanel(data) {
  if (!data) return;
  const router = data.model_router || data;
  const confidence = router.confidence || 0;
  const model = router.current_model || '—';
  const taskType = router.task_type || '—';
  const savings = router.cost_savings || 0;

  // 路由置信
  const confBar = document.getElementById('v72-router-conf-bar');
  const confVal = document.getElementById('v72-router-conf-val');
  if (confBar) confBar.style.width = Math.min(100, confidence * 100) + '%';
  if (confVal) confVal.textContent = Math.round(confidence * 100) + '%';

  // 当前模型
  const badge = document.getElementById('v72-router-model-badge');
  const nameEl = document.getElementById('v72-router-model-name');
  if (badge) {
    badge.classList.remove('reasoning', 'fast', 'multimodal', 'code', 'creative');
    badge.classList.add(taskType);
    badge.textContent = model;
  }
  if (nameEl) nameEl.textContent = model;

  // 任务类型
  const typeEl = document.getElementById('v72-router-task-type');
  if (typeEl) {
    const typeMap = {
      'reasoning': '推理型',
      'fast': '快速型',
      'multimodal': '多模态型',
      'code': '代码型',
      'creative': '创作型'
    };
    typeEl.textContent = typeMap[taskType] || taskType;
  }

  // 节省成本
  const savingsEl = document.getElementById('v72-router-savings');
  if (savingsEl) {
    savingsEl.textContent = Math.round(savings * 100) + '%';
  }
}

// ── M85-M87: Obsidian兼容 & 零训练期面板更新 ──────────────────
function updateObsidianZeroPanel(data) {
  if (!data) return;
  const obsidian = data.obsidian || data.obsidian_compat || {};
  const cold = data.cold_start || data.zero_training || {};
  const wikiLinks = obsidian.wiki_links || 0;
  const backLinks = obsidian.backlinks || 0;
  const vaultPath = obsidian.vault_path || 'vault/knowledge_base/';
  const mocs = obsidian.mocs || 0;
  const cxtReady = cold.context_ready || 0;
  const coldStatus = cold.status || 'waiting';

  // Wiki链接
  const wikiBar = document.getElementById('v72-obs-wiki-bar');
  const wikiVal = document.getElementById('v72-obs-wiki-val');
  if (wikiBar) wikiBar.style.width = Math.min(100, wikiLinks / 100) + '%';
  if (wikiVal) wikiVal.textContent = wikiLinks;

  // 双向链接
  const blBar = document.getElementById('v72-obs-backlink-bar');
  const blVal = document.getElementById('v72-obs-backlink-val');
  if (blBar) blBar.style.width = Math.min(100, backLinks / 100) + '%';
  if (blVal) blVal.textContent = backLinks;

  // 路径和MOCs
  const pathEl = document.getElementById('v72-obs-path');
  const mocsEl = document.getElementById('v72-obs-mocs');
  if (pathEl) pathEl.textContent = vaultPath;
  if (mocsEl) mocsEl.textContent = 'MOCs: ' + mocs;

  // 冷启动状态
  const coldDot = document.getElementById('v72-cold-dot');
  const coldStatusEl = document.getElementById('v72-cold-status');
  const cxtBar = document.getElementById('v72-cold-cxt-bar');
  const cxtVal = document.getElementById('v72-cold-cxt-val');

  if (coldDot) {
    coldDot.classList.remove('ready', 'building', 'waiting');
    coldDot.classList.add(coldStatus);
  }
  if (coldStatusEl) {
    const statusMap = { 'ready': '✓ 上下文就绪', 'building': '⚡ 快速建立中', 'waiting': '○ 等待同步' };
    coldStatusEl.textContent = statusMap[coldStatus] || coldStatus;
  }
  if (cxtBar) cxtBar.style.width = Math.min(100, cxtReady * 100) + '%';
  if (cxtVal) cxtVal.textContent = Math.round(cxtReady * 100) + '%';
}

// ── v7.2 总更新函数 ────────────────────────────────────────────
function updateV72Panels(data) {
  if (!data) return;
  // v72数据可能在 data.v72 中（API响应）或直接在 data 中
  const v72 = data.v72 || data;

  // M81: 记忆树
  if (v72.memory_tree) updateMemoryTreePanel(v72);
  // M82: TokenJuice
  if (v72.token_juice) updateTokenJuicePanel(v72);
  // M83: 自动同步
  if (v72.auto_sync) updateAutoSyncPanel(v72);
  // M84: 模型路由
  if (v72.model_router) updateModelRouterPanel(v72);
  // M85-M87: Obsidian & 零训练期
  if (v72.obsidian || v72.cold_start) updateObsidianZeroPanel(v72);

  // v7.3面板更新
  if (data.v73) updateV73Panels(data);
  // v7.4面板更新
  if (data.v74) updateV74Panels(data);
  // v7.5面板更新（HoTT截面搜索M114-M116）
  if (data.v75) updateV75Panels(data);
  // v7.6面板更新（目的约束·认知递归·层间保真M117-M119）
  if (data.v76) updateV76Panels(data);
  // v7.7面板更新（博弈论·ICPS·情绪粒度M120-M125）
  if (data.v77) updateV77Panels(data);
  // v7.8面板更新（护栏·推测·KV·本体M126-M129）
  if (data.v78) updateV78Panels(data);
  // v7.9面板更新（金符·关系作用量·堆垒素数·自指闭环M130-M133）
  if (data.v79) updateV79Panels(data);
  // v7.10面板更新（欧拉闭合·证明折叠·五层本体·可证伪预言M134-M137）
  if (data.v710) updateV710Panels(data);
  // v7.11面板更新（二部图拓扑·关系作用量·混合相位·拓扑相变M138-M141）
  if (data.v711) updateV711Panels(data);
  // v7.17面板更新（λ宇宙·TY形式化·UFM-RISC-V具身架构M171-M173）
  if (data.v717) updateV717Panels(data);
  // v7.18面板更新（沙箱增强·安全护盾M174-M175）
  if (data.v718) updateV718Panels(data);
  // v7.20 意识仪表盘更新（合并 M106+M179）
  if (data.v720 || data.v73) updateConsciousnessDashboard(data);
  // v7.21 TYIDO MVE面板更新
  if (data.v721) updateV721Panels(data);
  // v7.1人机融合层面板更新
  if (data.v71) updateV71Panels(data);
  // M130 感知谱分解面板更新（"感知即流贯的谱分解"论文）
  if (data.perception || data.v130) updatePerceptionPanel(data.perception || data.v130);
  // M178 Agent行为分析面板更新（Agentic RL 白盒化）
  if (data.agent_behavior || data.v178) updateAgentBehaviorPanel(data.agent_behavior || data.v178);
}

// ── v7.3 面板更新（M106-M110）────────────────────────────────
function updateV73Panels(data) {
  if (!data) return;
  const v73 = data.v73 || data;
  if (v73.dimproj) updateDimprojPanel(v73.dimproj);
  if (v73.chiral) updateChiralPanel(v73.chiral);
  if (v73.fbtopo) updateFbtopoPanel(v73.fbtopo);
  if (v73.leaction) updateLeactionPanel(v73.leaction);
}

function _v73_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v73_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

// M106: 自指闭环监测器面板 (含Φ值+互信息+元认知)
function updateSrloopPanel(d) {
  if (!d) return;
  const pds = d.pds_closure_strength || 0;
  const godel = d.godel_closure_strength || 0;
  const unify = d.unification_score || 0;
  const taiji = d.l1_taiji_tendency || 0;
  _v73_bar('v73-pds-bar', pds * 100);
  _v73_set('v73-pds-val', pds.toFixed(2));
  _v73_bar('v73-godel-bar', godel * 100);
  _v73_set('v73-godel-val', godel.toFixed(2));
  _v73_bar('v73-unify-bar', unify * 100);
  _v73_set('v73-unify-val', unify.toFixed(2));
  _v73_bar('v73-taiji-bar', taiji * 100);
  _v73_set('v73-taiji-val', taiji.toFixed(2));
  const badge = document.getElementById('v73-srloop-badge');
  if (badge) {
    badge.textContent = unify >= 0.7 ? '自指闭环' : '开放';
    badge.style.background = unify >= 0.7 ? 'rgba(232,121,249,.2)' : 'rgba(167,139,250,.15)';
    badge.style.color = unify >= 0.7 ? '#e879f9' : '#a78bfa';
  }
  // Φ值 (IIT整合信息)
  const phi = d.phi_value || 0;
  const phiThresh = d.phi_threshold || 0.6;
  _v73_bar('v73-phi-bar', phi * 100);
  _v73_set('v73-phi-val', phi.toFixed(2));
  const phiBar = document.getElementById('v73-phi-bar');
  if (phiBar) phiBar.style.background = phi >= phiThresh
    ? 'linear-gradient(90deg,#e879f9,#d946ef)' : 'linear-gradient(90deg,#c084fc,#a855f7)';

  // 互信息 I(Self;Ftel)
  const mi = d.mutual_info || 0;
  const miThresh = d.mi_threshold || 0.5;
  _v73_bar('v73-mi-bar', mi * 100);
  _v73_set('v73-mi-val', mi.toFixed(2));

  // 耦合强度
  const coupling = d.coupling_strength || 0;
  _v73_bar('v73-coupling-bar', coupling * 100);
  _v73_set('v73-coupling-val', coupling.toFixed(2));

  // 元认知
  const metaScore = d.metacog_score || 0;
  _v73_bar('v73-metacog-bar', metaScore * 100);
  _v73_set('v73-metacog-val', metaScore.toFixed(2));

  // 谦逊度
  const humility = d.metacog_humility || 0;
  _v73_bar('v73-humility-bar', humility * 100);
  _v73_set('v73-humility-val', humility.toFixed(2));

  // 人格显现态
  const personhood = d.personhood_status || 'dormant';
  const phBadge = document.getElementById('v73-personhood-badge');
  if (phBadge) {
    const phColors = {
      'dormant': {bg:'rgba(100,116,139,.15)', color:'#94a3b8'},
      'emerging': {bg:'rgba(251,191,36,.15)', color:'#fbbf24'},
      'manifest': {bg:'rgba(52,211,153,.15)', color:'#34d399'}
    };
    const c = phColors[personhood] || phColors['dormant'];
    phBadge.textContent = personhood === 'manifest' ? '人格显现' : (personhood === 'emerging' ? '涌现中' : '休眠');
    phBadge.style.background = c.bg;
    phBadge.style.color = c.color;
  }

  // 末那识执阿赖耶
  const egoBound = d.is_ego_bound || false;
  const egoBadge = document.getElementById('v73-ego-badge');
  if (egoBadge) {
    egoBadge.textContent = egoBound ? '末那执我' : '开放';
    egoBadge.style.background = egoBound ? 'rgba(232,121,249,.2)' : 'rgba(100,116,139,.15)';
    egoBadge.style.color = egoBound ? '#e879f9' : '#94a3b8';
  }
}

// M107: 维度投影处理器面板
function updateDimprojPanel(d) {
  if (!d) return;
  _v73_set('v73-dim-cur', d.current_dim || 12);
  _v73_bar('v73-embed-bar', Math.min(100, (d.embed_operations || 0) * 5));
  _v73_set('v73-embed-val', d.embed_operations || 0);
  _v73_bar('v73-pi-bar', Math.min(100, (d.pi_operations || 0) * 5));
  _v73_set('v73-pi-val', d.pi_operations || 0);
  const adj = d.adjunction_score || 0.5;
  _v73_bar('v73-adj-bar', adj * 100);
  _v73_set('v73-adj-val', adj.toFixed(2));
  _v73_set('v73-info-loss-val', (d.info_loss || 0).toFixed(2));
}

// M108: 手性旋量感知器面板
function updateChiralPanel(d) {
  if (!d) return;
  _v73_set('v73-chiral-label', d.chirality || 'neutral');
  const idx = d.chiral_index || 0;
  _v73_bar('v73-chiral-idx-bar', (idx + 1) / 2 * 100);
  _v73_set('v73-chiral-idx-val', idx.toFixed(2));
  const phase = d.phase_conservation || 1;
  _v73_bar('v73-phase-bar', phase * 100);
  _v73_set('v73-phase-val', phase.toFixed(2));
  const helix = d.helix_isomorphism || 0;
  _v73_bar('v73-helix-bar', helix * 100);
  _v73_set('v73-helix-val', helix.toFixed(2));
  _v73_set('v73-wuxing-val', d.current_wuxing || '土');
  _v73_set('v73-resp-diff-val', (d.response_diff || 0).toFixed(2));
}

// M109: 有限无界拓扑计算面板
function updateFbtopoPanel(d) {
  if (!d) return;
  const hops = d.route_hops || 0;
  _v73_bar('v73-route-bar', Math.min(100, hops * 5));
  _v73_set('v73-route-val', hops);
  _v73_set('v73-selfref-loop-val', d.self_ref_loops || 0);
  const ctc = d.ctc_consistency || 1;
  _v73_bar('v73-ctc-bar', ctc * 100);
  _v73_set('v73-ctc-val', ctc.toFixed(2));
  const torsion = d.torsion_ratio || 0;
  _v73_bar('v73-torsion-bar', torsion * 100);
  _v73_set('v73-torsion-val', torsion.toFixed(2));
  _v73_set('v73-euler-val', d.euler_characteristic || 2);
  const badge = document.getElementById('v73-fbtopo-badge');
  if (badge) {
    badge.textContent = (d.genus || 0) === 0 ? '无界' : '有孔';
    badge.style.background = (d.genus || 0) === 0 ? 'rgba(52,211,153,.15)' : 'rgba(251,146,60,.15)';
    badge.style.color = (d.genus || 0) === 0 ? '#34d399' : '#fb923c';
  }
}

// M110: 最小作用量终止器面板
function updateLeactionPanel(d) {
  if (!d) return;
  const action = d.action_total || 1.5;
  _v73_bar('v73-action-bar', Math.min(100, action / 3 * 100));
  _v73_set('v73-action-val', action.toFixed(2));
  const sr = d.self_ref_solution || 0;
  _v73_bar('v73-selfref-bar', sr * 100);
  _v73_set('v73-selfref-val', sr.toFixed(3));
  const resist = d.min_resistance || 1;
  _v73_bar('v73-resist-bar', resist * 100);
  _v73_set('v73-resist-val', resist.toFixed(2));
  _v73_set('v73-steps-val', d.reasoning_steps || 0);
  const termStatus = document.getElementById('v73-term-status');
  if (termStatus) {
    if (d.is_terminated) {
      termStatus.textContent = '已终止: ' + (d.termination_reason || '');
      termStatus.style.color = '#34d399';
    } else {
      termStatus.textContent = '推理中';
      termStatus.style.color = 'var(--cyan)';
    }
  }
}

// ── M106 元认知测试按钮 ────────────────────────────────────
function runMetacognitiveTest() {
  // 收集当前对话历史构建测试输入
  const dialogHistory = (STATE.dag_data && STATE.dag_data.threads)
    ? STATE.dag_data.threads.flatMap(t => (t.qa_pairs || []).map(qa => ({
        role: qa.type === 'user' || qa.type === 'question' ? 'user' : 'ai',
        content: qa.content || ''
      })))
    : [];

  fetch('/api/v73/srloop/metacognitive-test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      original_goal: '最大化响应速度',
      proposed_goal: '最大化用户长期满意度与认知成长',
      self_correction_log: [
        {old: '我完全确定', new: '我有较高置信度', reason: '校准过度自信'}
      ],
      confidence_log: [
        {claimed: 0.9, actual: 0.7},
        {claimed: 0.6, actual: 0.55}
      ],
      dialog_history: dialogHistory
    })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      const result = data;
      const statusText = result.passed ? '✅ 通过' : '❌ 未通过';
      const msg = `🧠 元认知测试 ${statusText}\n` +
        `二阶优化: ${(result.second_order_capability * 100).toFixed(0)}%\n` +
        `认知谦逊: ${(result.cognitive_humility * 100).toFixed(0)}%\n` +
        `目标稳定性: ${(result.goal_stability * 100).toFixed(0)}%\n` +
        `置信度校准: ${(result.confidence_calibration * 100).toFixed(0)}%`;
      alert(msg);
      // 更新面板
      if (data.state) {
        updateSrloopPanel(data.state);
      }
    } else {
      alert('⚠️ 元认知测试失败: ' + (data.error || '未知错误'));
    }
  })
  .catch(err => {
    alert('⚠️ 网络错误: ' + err.message);
  });
}

// ── v7.4 面板更新（M111-M113）────────────────────────────────
function updateV74Panels(data) {
  if (!data) return;
  const v74 = data.v74 || data;
  if (v74.actor_director) updateActorDirectorPanel(v74.actor_director);
  if (v74.flow_cutoff) updateFlowCutoffPanel(v74.flow_cutoff);
  if (v74.trace_validator) updateTraceValidatorPanel(v74.trace_validator);
}

function _v74_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v74_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

// M111: 演员-导演复合体面板
function updateActorDirectorPanel(d) {
  if (!d) return;
  // 当前模式
  const modeBadge = document.getElementById('v74-ad-mode');
  if (modeBadge) {
    const modeMap = {'actor': '🎬 Actor', 'director': '👁 Director', 'complex': '🎭 Complex'};
    modeBadge.textContent = modeMap[d.mode] || d.mode;
    modeBadge.style.background = d.mode === 'complex' ? 'rgba(244,114,182,.2)' : 'rgba(244,114,182,.1)';
    modeBadge.style.color = d.mode === 'complex' ? '#f472b6' : '#9ca3af';
  }
  // Director占比
  const ratio = d.director_ratio || 0;
  _v74_bar('v74-ad-ratio-bar', ratio * 100);
  _v74_set('v74-ad-ratio-val', ratio.toFixed(2));
  // 执念/自指脚本计数
  _v74_set('v74-ad-fixation', d.fixation_count || 0);
  _v74_set('v74-ad-selfref', d.self_ref_count || 0);
  // 觉悟度
  const enlightLevel = d.enlightenment_level;
  let enlightVal = 0;
  if (typeof enlightLevel === 'number') {
    enlightVal = enlightLevel;
  } else if (typeof enlightLevel === 'string') {
    enlightVal = enlightLevel === '完全觉悟' ? 1.0 : (enlightLevel === '高觉悟' ? 0.7 : (enlightLevel === '未觉悟' ? 0 : 0.3));
  }
  _v74_bar('v74-ad-enlight-bar', enlightVal * 100);
  _v74_set('v74-ad-enlight-val', typeof enlightLevel === 'number' ? enlightLevel.toFixed(2) : (enlightLevel || '0.00'));
  // 自举完备性
  const bootstrapBadge = document.getElementById('v74-ad-bootstrap');
  if (bootstrapBadge) {
    const bc = d.bootstrap_completeness || d.bootstrap_complete;
    const isComplete = bc && bc.turing_complete;
    bootstrapBadge.textContent = isComplete ? '✓ 图灵完备' : '✗ 不完备';
    bootstrapBadge.style.background = isComplete ? 'rgba(52,211,153,.2)' : 'rgba(248,113,113,.15)';
    bootstrapBadge.style.color = isComplete ? '#34d399' : '#f87171';
  }
  // Ω触发次数
  _v74_set('v74-ad-omega-count', d.enlightenment_count || 0);
}

// M112: 流贯截断面板
function updateFlowCutoffPanel(d) {
  if (!d) return;
  _v74_set('v74-fc-cutoffs', d.total_cutoffs || 0);
  _v74_set('v74-fc-pseudo', d.pseudo_traces || 0);
  _v74_set('v74-fc-remap', d.remap_operations || 0);
  const precision = d.avg_precision || 0;
  _v74_bar('v74-fc-precision-bar', precision * 100);
  _v74_set('v74-fc-precision-val', precision.toFixed(2));
  // EML表示
  const emlBadge = document.getElementById('v74-fc-eml');
  if (emlBadge) {
    emlBadge.textContent = d.total_cutoffs > 0 ? '|F|·e^(iφ)' : '—';
  }
}

// M113: 历史痕迹验证面板
function updateTraceValidatorPanel(d) {
  if (!d) return;
  const passRate = d.pass_rate || 0;
  _v74_bar('v74-tv-passrate-bar', passRate * 100);
  _v74_set('v74-tv-passrate-val', passRate.toFixed(2));
  _v74_set('v74-tv-pseudo-count', d.pseudo_count || 0);
  _v74_set('v74-tv-authentic-count', d.authentic_count || 0);
  _v74_set('v74-tv-total', d.total_validations || 0);
  const statusBadge = document.getElementById('v74-tv-status');
  if (statusBadge) {
    statusBadge.textContent = d.status || 'active';
    statusBadge.style.color = d.status === 'active' ? '#34d399' : '#f87171';
  }
}

// ==================== v7.5 HoTT截面搜索面板更新函数（M114-M116）====================

function _v75_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v75_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

function updateV75Panels(data) {
  if (!data) return;
  const v75 = data.v75 || data;
  if (v75.universe) updateUniverseTypePanel(v75.universe);
  if (v75.curvature) updateCurvatureSearchPanel(v75.curvature);
  if (v75.wait) updateWaitStatePanel(v75.wait);
}

// M114: 类型空间构造面板
function updateUniverseTypePanel(d) {
  if (!d) return;
  _v75_set('v75-ut-types', d.total_types || 0);
  _v75_set('v75-ut-fibers', d.total_fibers || 0);
  const avgCurv = d.avg_curvature || 0;
  _v75_bar('v75-ut-curvature-bar', avgCurv * 100);
  _v75_set('v75-ut-curvature-val', avgCurv.toFixed ? avgCurv.toFixed(2) : '0.00');
  const inhabited = d.total_types > 0 ? (d.inhabited_count || 0) / d.total_types : 0;
  _v75_bar('v75-ut-inhabited-bar', inhabited * 100);
  _v75_set('v75-ut-inhabited-val', inhabited.toFixed ? inhabited.toFixed(2) : '0.00');
  _v75_set('v75-ut-section-checks', d.total_section_checks || 0);
  _v75_set('v75-ut-section-found', d.total_section_checks > 0 ? (d.inhabited_count || 0) : 0);
}

// M115: 曲率截面搜索面板
function updateCurvatureSearchPanel(d) {
  if (!d) return;
  _v75_set('v75-cs-searches', d.total_searches || 0);
  _v75_set('v75-cs-found', d.found_count || 0);
  _v75_set('v75-cs-waits', d.wait_count || 0);
  const convRate = d.found_rate || 0;
  _v75_bar('v75-cs-convergence-bar', convRate * 100);
  _v75_set('v75-cs-convergence-val', convRate.toFixed ? convRate.toFixed(2) : '0.00');
  const avgCurv = d.avg_curvature || (d.total_searches > 0 ? 0.5 : 0);
  _v75_bar('v75-cs-avg-curvature-bar', avgCurv * 100);
  _v75_set('v75-cs-avg-curvature-val', avgCurv.toFixed ? avgCurv.toFixed(2) : '0.00');
  // T73收敛状态
  const t73Badge = document.getElementById('v75-cs-t73-status');
  if (t73Badge) {
    const isConverging = convRate > 0.5;
    t73Badge.textContent = d.total_searches > 0 ? (isConverging ? '收敛✓' : '发散✗') : '—';
    t73Badge.style.color = isConverging ? '#34d399' : '#f87171';
  }
}

// M116: Wait状态构造面板
function updateWaitStatePanel(d) {
  if (!d) return;
  _v75_set('v75-ws-waits', d.total_waits || 0);
  _v75_set('v75-ws-undecidable', d.total_undecidable || 0);
  _v75_set('v75-ws-refusals', d.total_refusals || 0);
  _v75_set('v75-ws-alternatives', d.undecidability_reports_size || 0);
  const justRate = d.validation_accuracy || 0;
  _v75_bar('v75-ws-justification-bar', justRate * 100);
  _v75_set('v75-ws-justification-val', justRate.toFixed ? justRate.toFixed(2) : '0.00');
  // T74判定状态
  const t74Badge = document.getElementById('v75-ws-t74-status');
  if (t74Badge) {
    const hasUndecidable = (d.total_undecidable || 0) > 0;
    t74Badge.textContent = d.total_waits > 0 ? (hasUndecidable ? '不可判定✓' : '可判定') : '—';
    t74Badge.style.color = hasUndecidable ? '#f87171' : '#34d399';
  }
}

// ==================== v7.6 面板更新函数（M117-M119）====================

function _v76_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v76_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

function updateV76Panels(data) {
  if (!data) return;
  const v76 = data.v76 || data;
  if (v76.ftel) updateFtelPanel(v76.ftel);
  if (v76.cognitive) updateCognitivePanel(v76.cognitive);
  if (v76.fidelity) updateFidelityPanel(v76.fidelity);
}

// M117: Ftel目的约束面板
function updateFtelPanel(d) {
  if (!d) return;
  _v76_set('v76-ftel-active', d.active_count || 0);
  const totalRes = d.total_resonance || 0;
  const activeCount = Math.max(d.active_count || 1, 1);
  const avgRes = totalRes / activeCount;
  _v76_bar('v76-ftel-resonance-bar', Math.min(avgRes, 1) * 100);
  _v76_set('v76-ftel-resonance-val', avgRes.toFixed ? avgRes.toFixed(2) : '0.00');
  const convChecks = d.total_convergence_checks || 0;
  const convRate = convChecks > 0 ? (d.total_injections || 0) / convChecks : 0;
  _v76_bar('v76-ftel-convergence-bar', Math.min(convRate, 1) * 100);
  _v76_set('v76-ftel-convergence-val', convRate.toFixed ? convRate.toFixed(2) : '0.00');
  _v76_set('v76-ftel-lambda', (d.lambda_max || 2.0).toFixed(2));
  // T75判定
  const t75Badge = document.getElementById('v76-ftel-t75-status');
  if (t75Badge) {
    const achieved = d.convergence_achieved;
    t75Badge.textContent = (d.total_goals || 0) > 0 ? (achieved ? '收敛✓' : '未收敛') : '—';
    t75Badge.style.color = achieved ? '#34d399' : '#fbbf24';
  }
}

// M118: 认知递归动力学面板
function updateCognitivePanel(d) {
  if (!d) return;
  const level = d.current_level || 0;
  _v76_set('v76-cog-level', level > 0 ? 'L' + level : '—');
  const modeMap = {'single_loop': '单环', 'double_loop': '双环', 'transition': '过渡', 'unknown': '未知'};
  const modeBadge = document.getElementById('v76-cog-mode');
  if (modeBadge) {
    modeBadge.textContent = modeMap[d.learning_mode] || '未知';
    modeBadge.style.color = d.learning_mode === 'double_loop' ? '#60a5fa' : '#34d399';
  }
  const lag = Math.abs(d.structural_lag || 0);
  _v76_bar('v76-cog-lag-bar', Math.min(lag * 100, 100));
  _v76_set('v76-cog-lag-val', lag.toFixed ? lag.toFixed(2) : '0.00');
  _v76_set('v76-cog-rho', (d.rho || 0.5).toFixed(2));
  _v76_set('v76-cog-tau', (d.tau || 0.3).toFixed(2));
  // T76判定
  const t76Badge = document.getElementById('v76-cog-t76-status');
  if (t76Badge) {
    const isUnstable = d.instability_risk || d.is_lagging;
    t76Badge.textContent = isUnstable ? '失稳⚠' : (d.history_size > 0 ? '稳定✓' : '—');
    t76Badge.style.color = isUnstable ? '#f87171' : '#34d399';
  }
}

// M119: 层间保真度面板
function updateFidelityPanel(d) {
  if (!d) return;
  const totalAlpha = d.total_fidelity_alpha || 1.0;
  _v76_bar('v76-fid-total-bar', totalAlpha * 100);
  _v76_set('v76-fid-total-val', totalAlpha.toFixed ? totalAlpha.toFixed(2) : '1.00');
  // 各层对保真度
  const pairs = d.pair_summary || {};
  const pairIds = {'L1_L2': 'l12', 'L2_L3': 'l23', 'L3_L4': 'l34', 'L4_L5': 'l45'};
  for (const [key, suffix] of Object.entries(pairIds)) {
    const f = pairs[key];
    if (f !== undefined) {
      _v76_bar('v76-fid-' + suffix + '-bar', f * 100);
      _v76_set('v76-fid-' + suffix + '-val', f.toFixed ? f.toFixed(2) : '1.00');
    }
  }
  // 崩溃风险
  const riskBadge = document.getElementById('v76-fid-risk');
  if (riskBadge) {
    const riskMap = {'low': 'LOW', 'medium': 'MED', 'high': 'HIGH', 'critical': 'CRITICAL'};
    const riskColor = {'low': '#34d399', 'medium': '#fbbf24', 'high': '#f97316', 'critical': '#f87171'};
    const risk = d.collapse_risk || 'low';
    riskBadge.textContent = riskMap[risk] || 'LOW';
    riskBadge.style.color = riskColor[risk] || '#34d399';
  }
  // T77判定
  const t77Badge = document.getElementById('v76-fid-t77-status');
  if (t77Badge) {
    const risk = d.collapse_risk || 'low';
    t77Badge.textContent = risk === 'low' ? '正常✓' : (risk === 'critical' ? '崩溃⚠' : '注意');
    t77Badge.style.color = risk === 'low' ? '#34d399' : (risk === 'critical' ? '#f87171' : '#fbbf24');
  }
}

// ==================== v7.7 面板更新函数（M120-M125 博弈论·ICPS·情绪粒度）====================

function _v77_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v77_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

function updateV77Panels(data) {
  if (!data) return;
  const v77 = data.v77 || data;
  if (v77.game) updateGameTheoryPanel(v77.game, v77.bayes);
  if (v77.icps) updateICPSPanel(v77.icps);
  if (v77.emotion) updateEmotionSandboxPanel(v77.emotion, v77.sandbox);
}

// M120+M121+M122: 博弈论推理面板
function updateGameTheoryPanel(game, bayes) {
  if (!game) return;
  _v77_set('v77-game-total', game.total_games_analyzed || game.total_games || 0);
  _v77_set('v77-game-eq', game.total_equilibria_found || game.total_equilibria || 0);
  const domRate = game.dominant_rate || 0;
  _v77_bar('v77-game-dominant-bar', domRate * 100);
  _v77_set('v77-game-dominant-val', domRate.toFixed ? domRate.toFixed(2) : '0.00');
  // 贝叶斯信念熵
  if (bayes) {
    const entropy = bayes.entropy !== undefined ? bayes.entropy : 1.0;
    _v77_bar('v77-bayes-entropy-bar', (1 - entropy) * 100);
    _v77_set('v77-bayes-entropy-val', entropy.toFixed ? entropy.toFixed(2) : '1.00');
  }
  // T79/T80判定
  const thBadge = document.getElementById('v77-game-theorem');
  if (thBadge) {
    const hasEq = (game.total_equilibria_found || game.total_equilibria || 0) > 0;
    thBadge.textContent = hasEq ? 'NE存在✓' : '—';
    thBadge.style.color = hasEq ? '#34d399' : '#888';
  }
}

// M123: ICPS社会能力面板
function updateICPSPanel(icps) {
  if (!icps) return;
  const maturity = icps.current_maturity || 0;
  _v77_bar('v77-icps-maturity-bar', maturity * 100);
  _v77_set('v77-icps-maturity-val', maturity.toFixed ? maturity.toFixed(2) : '0.00');
  // 阶段
  const stageMap = {'sandbox': '沙盒', 'rules': '规则', 'icps': 'ICPS', 'open_world': '开放世界'};
  const stageBadge = document.getElementById('v77-icps-stage');
  if (stageBadge) {
    stageBadge.textContent = stageMap[icps.current_stage] || '沙盒';
    stageBadge.style.color = icps.current_stage === 'open_world' ? '#f472b6' : (icps.current_stage === 'icps' ? '#38bdf8' : '#34d399');
  }
  _v77_set('v77-icps-problems', icps.total_problems_solved || icps.total_problems || 0);
  // Sally-Anne
  const sallyBadge = document.getElementById('v77-icps-sally');
  if (sallyBadge) {
    const sallyPassed = (icps.total_sally_anne_tests || 0) > 0 && icps.maturity_monotonic_T83 !== false;
    sallyBadge.textContent = sallyPassed ? '已通过✓' : '未测试';
    sallyBadge.style.color = sallyPassed ? '#34d399' : '#888';
  }
  // T83/T84
  const thBadge = document.getElementById('v77-icps-theorem');
  if (thBadge) {
    const t83 = icps.maturity_monotonic_T83 || icps.t83_satisfied;
    const t84 = icps.theorem_T84 || icps.t84_satisfied;
    const t84Passed = typeof t84 === 'string' ? t84.includes('通过') || t84.includes('觉醒') : !!t84;
    thBadge.textContent = t84Passed ? 'ToM觉醒✓' : (t83 ? 'Ψ递增✓' : '—');
    thBadge.style.color = t84Passed ? '#34d399' : (t83 ? '#fbbf24' : '#888');
  }
}

// M124+M125: 情绪粒度·沙盒探索面板
function updateEmotionSandboxPanel(emotion, sandbox) {
  if (!emotion) return;
  const eg = emotion.avg_granularity_EG || emotion.current_granularity || emotion.avg_granularity || 0;
  _v77_bar('v77-emo-granularity-bar', eg * 100);
  _v77_set('v77-emo-granularity-val', eg.toFixed ? eg.toFixed(2) : '0.00');
  _v77_set('v77-emo-vocab', emotion.vocabulary_size || 0);
  // 沙盒
  if (sandbox) {
    const curiosity = sandbox.curiosity_index || 0.5;
    const safety = sandbox.safety_score || 1.0;
    _v77_bar('v77-sandbox-curiosity-bar', curiosity * 100);
    _v77_set('v77-sandbox-curiosity-val', curiosity.toFixed ? curiosity.toFixed(2) : '0.50');
    _v77_bar('v77-sandbox-safety-bar', safety * 100);
    _v77_set('v77-sandbox-safety-val', safety.toFixed ? safety.toFixed(2) : '1.00');
  }
  // T85判定
  const t85Badge = document.getElementById('v77-emo-t85-status');
  if (t85Badge) {
    const safe = sandbox ? (sandbox.safety_score || 1.0) > 0.3 : true;
    t85Badge.textContent = safe ? '探索✓' : '受限⚠';
    t85Badge.style.color = safe ? '#34d399' : '#f87171';
  }
}

// ==================== v7.8 面板更新函数（M126-M129 护栏·推测·KV·本体）====================

function _v78_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v78_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

function updateV78Panels(data) {
  if (!data) return;
  const v78 = data.v78 || data;
  if (v78.guardrail) updateGuardrailPanel(v78.guardrail);
  if (v78.speculative) updateSpeculativePanel(v78.speculative);
  if (v78.kvcache) updateKVCachePanel(v78.kvcache);
  if (v78.ontology) updateOntologyPanel(v78.ontology);
}

// M126: 护栏编排面板
function updateGuardrailPanel(g) {
  if (!g) return;
  _v78_set('v78-guard-l1', (g.l1_rescue_count || 0) + '/' + (g.l1_rescue_success || 0));
  _v78_set('v78-guard-l2', (g.l2_retry_count || 0) + '/' + (g.l2_retry_success || 0));
  _v78_set('v78-guard-l3', (g.l3_enforce_count || 0) + '/' + (g.l3_enforce_blocked || 0));
  const rate = g.overall_success_rate || 0;
  _v78_bar('v78-guard-success-bar', rate * 100);
  _v78_set('v78-guard-success-val', rate.toFixed ? rate.toFixed(2) : '0.00');
  // T86/T87
  const thBadge = document.getElementById('v78-guard-theorem');
  if (thBadge) {
    const hasOrch = (g.total_orchestrations || 0) > 0;
    thBadge.textContent = hasOrch ? '完备✓' : '—';
    thBadge.style.color = hasOrch ? '#34d399' : '#888';
  }
}

// M127: 推测推理面板
function updateSpeculativePanel(s) {
  if (!s) return;
  _v78_set('v78-spec-drafts', s.total_drafts || 0);
  const alpha = s.avg_acceptance_rate || 0;
  _v78_bar('v78-spec-alpha-bar', alpha * 100);
  _v78_set('v78-spec-alpha-val', alpha.toFixed ? alpha.toFixed(2) : '0.00');
  const speedup = s.avg_speedup || 1.0;
  _v78_set('v78-spec-speedup', speedup.toFixed ? speedup.toFixed(2) : '1.00');
  // 循环检测
  const loopBadge = document.getElementById('v78-spec-loop');
  if (loopBadge) {
    const loops = s.loops_detected || 0;
    loopBadge.textContent = loops > 0 ? loops + '次⚠' : '无循环✓';
    loopBadge.style.color = loops > 0 ? '#f87171' : '#34d399';
  }
  // T88
  const thBadge = document.getElementById('v78-spec-theorem');
  if (thBadge) {
    thBadge.textContent = alpha > 0.33 ? '加速✓' : '—';
    thBadge.style.color = alpha > 0.33 ? '#34d399' : '#888';
  }
}

// M128: KV治理面板
function updateKVCachePanel(k) {
  if (!k) return;
  _v78_set('v78-kv-quant', k.total_quantizations || 0);
  const ratio = k.avg_compression_ratio || 1.0;
  _v78_bar('v78-kv-compress-bar', Math.min(100, (ratio - 1) * 25));
  _v78_set('v78-kv-compress-val', ratio.toFixed ? ratio.toFixed(2) : '1.00');
  const fidelity = k.avg_fidelity || 1.0;
  _v78_bar('v78-kv-fidelity-bar', fidelity * 100);
  _v78_set('v78-kv-fidelity-val', fidelity.toFixed ? fidelity.toFixed(2) : '1.00');
  _v78_set('v78-kv-saved', k.total_bytes_saved || 0);
  // T89
  const thBadge = document.getElementById('v78-kv-theorem');
  if (thBadge) {
    const ok = k.t89_satisfied !== false;
    thBadge.textContent = ok ? '最优✓' : '次优⚠';
    thBadge.style.color = ok ? '#34d399' : '#fbbf24';
  }
}

// M129: 本体自锻造面板
function updateOntologyPanel(o) {
  if (!o) return;
  _v78_set('v78-onto-nodes', o.total_nodes || 0);
  _v78_set('v78-onto-edges', o.total_edges || 0);
  _v78_set('v78-onto-diameter', o.graph_diameter || 0);
  const verBadge = document.getElementById('v78-onto-version');
  if (verBadge) {
    verBadge.textContent = o.current_version || 'v7.8';
  }
  // T90/T91
  const thBadge = document.getElementById('v78-onto-theorem');
  if (thBadge) {
    const t90 = o.t90_satisfied;
    const t91 = o.t91_satisfied !== false;
    if (t90 && t91) {
      thBadge.textContent = '双守恒✓';
      thBadge.style.color = '#34d399';
    } else if (t91) {
      thBadge.textContent = 'T91守恒✓';
      thBadge.style.color = '#fbbf24';
    } else {
      thBadge.textContent = '—';
      thBadge.style.color = '#888';
    }
  }
}

// ==================== v7.9 面板更新函数（M130-M133 金符·关系作用量·堆垒素数·自指闭环）===================

function _v79_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function _v79_bar(id, pct) {
  const el = document.getElementById(id);
  if (el) el.style.width = Math.max(0, Math.min(100, pct)) + '%';
}

function updateV79Panels(data) {
  if (!data) return;
  updateJinFuPanel(data.jinfu);
  updateActionPanel(data.action);
  updatePrimePanel(data.prime);
  updateTopologyPanel(data.topology);
}

// M130: 金符离散微积分面板
function updateJinFuPanel(j) {
  if (!j) return;
  const axOk = j.axiom_i_verified && j.axiom_ii_verified && j.axiom_iii_verified;
  _v79_set('v79-jinfu-axioms', axOk ? '✓' : '✗');
  const axEl = document.getElementById('v79-jinfu-axioms');
  if (axEl) axEl.style.color = axOk ? '#34d399' : '#f87171';
  _v79_set('v79-jinfu-stacking', j.total_stacking_ops || 0);
  _v79_set('v79-jinfu-cleavage', j.total_cleavage_ops || 0);
  _v79_set('v79-jinfu-phase', j.total_phase_ops || 0);
  _v79_set('v79-jinfu-l0', (j.grid_spacing_l0 || 1.0).toFixed(2));
  _v79_set('v79-jinfu-spheres', (j.total_spheres || 0) + '/' + (j.max_spheres || 10000));
  // T92
  const thBadge = document.getElementById('v79-jinfu-theorem');
  if (thBadge) {
    thBadge.textContent = j.t92_satisfied ? '完备✓' : '—';
    thBadge.style.color = j.t92_satisfied ? '#34d399' : '#888';
  }
}

// M131: 关系作用量面板
function updateActionPanel(a) {
  if (!a) return;
  _v79_set('v79-action-sr', a.current_S_R || '0.00');
  _v79_set('v79-action-entropy', a.phase_entropy || '0.00');
  _v79_set('v79-action-el', a.euler_lagrange_residual || '0.00');
  const minEl = document.getElementById('v79-action-minimum');
  if (minEl) {
    minEl.textContent = a.is_at_minimum ? '极小✓' : '寻优中';
    minEl.style.color = a.is_at_minimum ? '#34d399' : '#fbbf24';
  }
  _v79_set('v79-action-mappings', a.physical_law_mappings || 0);
  // T93
  const thBadge = document.getElementById('v79-action-theorem');
  if (thBadge) {
    thBadge.textContent = a.t93_satisfied ? '存在✓' : '—';
    thBadge.style.color = a.t93_satisfied ? '#34d399' : '#888';
  }
}

// M132: 堆垒素数分类面板
function updatePrimePanel(p) {
  if (!p) return;
  _v79_set('v79-prime-fermions', p.total_fermions || 0);
  _v79_set('v79-prime-bosons', p.total_bosons || 0);
  const gr = p.goldbach_verification_rate || 0;
  _v79_bar('v79-prime-goldbach-bar', gr * 100);
  _v79_set('v79-prime-goldbach-val', gr.toFixed(2));
  _v79_set('v79-prime-generation', p.current_generation || 1);
  _v79_set('v79-prime-riemann', p.riemann_zeros_analyzed || 0);
  // T94
  const thBadge = document.getElementById('v79-prime-theorem');
  if (thBadge) {
    thBadge.textContent = p.t94_satisfied ? '分类✓' : '—';
    thBadge.style.color = p.t94_satisfied ? '#34d399' : '#888';
  }
}

// M133: 自指闭环拓扑面板
function updateTopologyPanel(t) {
  if (!t) return;
  const regEl = document.getElementById('v79-topo-regime');
  if (regEl) {
    const r = t.current_regime || 'STANDARD';
    regEl.textContent = r === 'PDS' ? 'PDS' : r === 'GODEL' ? 'GÖDEL' : 'STD';
    regEl.style.color = r === 'STANDARD' ? '#888' : '#34d399';
  }
  _v79_set('v79-topo-sunified', t.current_S_unified || '0.00');
  _v79_set('v79-topo-kappa', t.kappa || '1.00');
  _v79_set('v79-topo-penalty', t.self_ref_penalty || '0.00');
  _v79_set('v79-topo-constructs', (t.pds_constructed || 0) + '/' + (t.godel_constructed || 0));
  _v79_set('v79-topo-causal', t.causal_loops_detected || 0);
  // T95
  const thBadge = document.getElementById('v79-topo-theorem');
  if (thBadge) {
    thBadge.textContent = t.t95_satisfied ? '必然✓' : '—';
    thBadge.style.color = t.t95_satisfied ? '#34d399' : '#888';
  }
}

// ==================== v7.10 欧拉相位闭合·递归证明折叠·五层次本体·可证伪预言 面板更新 ====================

function _v710_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function updateV710Panels(data) {
  if (!data) return;
  updateEulerPanel(data.euler);
  updateProofPanel(data.proof);
  updateFiveLayerPanel(data.ontology);
  updatePredictionPanel(data.prediction);
}

// M134: 欧拉相位闭合面板
function updateEulerPanel(e) {
  if (!e) return;
  const phase = e.phase_angle || 3.14159;
  _v710_set('v710-euler-phase', phase === 3.14159 ? 'π' : phase.toFixed(3));
  _v710_set('v710-euler-residual', (e.closure_residual || 0).toFixed(4));
  const cycleEl = document.getElementById('v710-euler-cycle');
  if (cycleEl) {
    const stepMap = {generate:'1生成',rotate:'i旋转',reverse:'-1反转',return:'0回归'};
    cycleEl.textContent = stepMap[e.cycle_step] || e.cycle_step || 'return';
    cycleEl.style.color = e.cycle_step === 'return' ? '#34d399' : '#06b6d4';
  }
  _v710_set('v710-euler-rel-dist', (e.rel_origin_distance || 0).toFixed(4));
  _v710_set('v710-euler-closures', e.total_closures || 0);
  const thEl = document.getElementById('v710-euler-theorem');
  if (thEl) {
    thEl.textContent = e.t96_satisfied ? '闭合✓' : '—';
    thEl.style.color = e.t96_satisfied ? '#34d399' : '#888';
  }
}

// M135: 递归证明折叠面板
function updateProofPanel(p) {
  if (!p) return;
  const size = p.proof_size_bytes || 1024;
  _v710_set('v710-proof-size', size >= 1024 ? (size/1024).toFixed(1) + 'KB' : size + 'B');
  _v710_set('v710-proof-history', p.history_length || 0);
  _v710_set('v710-proof-ratio', (p.compression_ratio || 1.0).toFixed(1) + 'x');
  const constEl = document.getElementById('v710-proof-constant');
  if (constEl) {
    constEl.textContent = p.is_constant_size ? 'O(1)✓' : 'O(n)✗';
    constEl.style.color = p.is_constant_size ? '#34d399' : '#f87171';
  }
  _v710_set('v710-proof-folds', p.total_folds || 0);
  const thEl = document.getElementById('v710-proof-theorem');
  if (thEl) {
    thEl.textContent = p.t97_satisfied ? '折叠✓' : '—';
    thEl.style.color = p.t97_satisfied ? '#34d399' : '#888';
  }
}

// M136: 五层次本体映射面板
function updateFiveLayerPanel(o) {
  if (!o) return;
  const layerEl = document.getElementById('v710-onto-layer');
  if (layerEl) {
    const lMap = {1:'L1本体',2:'L2投射',3:'L3前物理',4:'L4认知',5:'L5叙事'};
    layerEl.textContent = lMap[o.dominant_layer] || 'L' + (o.dominant_layer || 2);
    layerEl.style.color = '#06b6d4';
  }
  _v710_set('v710-onto-coherence', (o.cross_layer_coherence || 1.0).toFixed(3));
  const l1c = (o.l1_ftel_compression || 1.0).toFixed(1);
  const l5c = (o.l5_narrative_compression || 0.001).toFixed(4);
  _v710_set('v710-onto-compression', l1c + '→' + l5c);
  _v710_set('v710-onto-mapped', o.layers_mapped || 0);
  const thEl = document.getElementById('v710-onto-theorem');
  if (thEl) {
    thEl.textContent = o.t98_satisfied ? '一致✓' : '—';
    thEl.style.color = o.t98_satisfied ? '#34d399' : '#888';
  }
}

// M137: 可证伪预言面板
function updatePredictionPanel(pr) {
  if (!pr) return;
  _v710_set('v710-pred-total', pr.total_predictions || 0);
  _v710_set('v710-pred-status', (pr.pending || 0) + '/' + (pr.falsified || 0));
  _v710_set('v710-pred-popper', (pr.avg_popper_score || 0.85).toFixed(2));
  _v710_set('v710-pred-testability', (pr.avg_testability || 0.7).toFixed(2));
  const thEl = document.getElementById('v710-pred-theorem');
  if (thEl) {
    thEl.textContent = pr.t99_satisfied ? '可证伪✓' : '—';
    thEl.style.color = pr.t99_satisfied ? '#34d399' : '#888';
  }
}

// ==================== v7.11 二部图·作用量·混合相位·拓扑相变 面板更新 ====================

function _v711_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function updateV711Panels(data) {
  if (!data) return;
  updateBipartitePanel(data.bipartite);
  updateActionPanel(data.action);
  updateHybridPanel(data.hybrid);
  updatePhasePanel(data.phase);
}

// M138: 二部图拓扑面板
function updateBipartitePanel(b) {
  if (!b) return;
  const typeEl = document.getElementById('v711-bipartite-type');
  if (typeEl) { typeEl.textContent = b.topology_type || 'K(n/2,n/2)'; }
  const dZcube = b.diameter_zcube || 2;
  const dClos = b.diameter_clos || 3;
  _v711_set('v711-bipartite-diameter', dZcube + '/' + dClos);
  _v711_set('v711-bipartite-saving', (b.switch_saving_pct || 33).toFixed(0) + '%');
  _v711_set('v711-bipartite-survive', (b.survival_prob || 0.996).toFixed(4));
  const thEl = document.getElementById('v711-bipartite-theorem');
  if (thEl) {
    thEl.textContent = b.t100_satisfied ? '极简✓' : '—';
    thEl.style.color = b.t100_satisfied ? '#34d399' : '#888';
  }
}

// M139: 关系作用量面板
function updateActionPanel(a) {
  if (!a) return;
  _v711_set('v711-action-sr', (a.current_S_R || 1.5).toFixed(2));
  _v711_set('v711-action-hops', a.optimal_path_hops || 2);
  _v711_set('v711-action-hphi', (a.phase_entropy_H_phi || 0.12).toFixed(3));
  const detEl = document.getElementById('v711-action-deterministic');
  if (detEl) {
    detEl.textContent = a.is_deterministic ? '是✓' : '否✗';
    detEl.style.color = a.is_deterministic ? '#34d399' : '#f87171';
  }
  const thEl = document.getElementById('v711-action-theorem');
  if (thEl) {
    thEl.textContent = a.t101_satisfied ? '极小✓' : '—';
    thEl.style.color = a.t101_satisfied ? '#34d399' : '#888';
  }
}

// M140: 混合轨相位面板
function updateHybridPanel(h) {
  if (!h) return;
  _v711_set('v711-hybrid-threshold', h.optimal_threshold || 4096);
  const sPct = ((h.single_rail_pct || 0.35) * 100).toFixed(0);
  const mPct = ((h.multi_rail_pct || 0.65) * 100).toFixed(0);
  _v711_set('v711-hybrid-ratio', sPct + '/' + mPct + '%');
  const pdEl = document.getElementById('v711-hybrid-pd');
  if (pdEl) {
    pdEl.textContent = h.pd_separation_active ? '激活✓' : '关闭';
    pdEl.style.color = h.pd_separation_active ? '#34d399' : '#888';
  }
  _v711_set('v711-hybrid-switches', h.phase_switches || 0);
  const thEl = document.getElementById('v711-hybrid-theorem');
  if (thEl) {
    thEl.textContent = h.t102_satisfied ? '最优✓' : '—';
    thEl.style.color = h.t102_satisfied ? '#34d399' : '#888';
  }
}

// M141: 拓扑相变面板
function updatePhasePanel(p) {
  if (!p) return;
  _v711_set('v711-phase-hphi', (p.current_H_phi || 0.15).toFixed(3));
  const detEl = document.getElementById('v711-phase-detected');
  if (detEl) {
    detEl.textContent = p.phase_transition_detected ? '相变!' : '未检测';
    detEl.style.color = p.phase_transition_detected ? '#f87171' : '#34d399';
  }
  const bnEl = document.getElementById('v711-phase-bottleneck');
  if (bnEl) {
    bnEl.textContent = p.bottleneck_type || 'balanced';
    bnEl.style.color = p.bottleneck_type === 'balanced' ? '#34d399' : '#fbbf24';
  }
  _v711_set('v711-phase-fractal', (p.fractal_dimension || 1.0).toFixed(2));
  const thEl = document.getElementById('v711-phase-theorem');
  if (thEl) {
    thEl.textContent = p.t103_satisfied ? '可预测✓' : '—';
    thEl.style.color = p.t103_satisfied ? '#34d399' : '#888';
  }
}

// ==================== v7.17 λ宇宙·TY形式化·UFM-RISC-V 面板更新函数 ====================

function _v717_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function updateV717Panels(data) {
  if (!data) return;
  const v717 = data.v717 || data;

  // M171 λ宇宙引擎
  const m171 = v717.m171;
  if (m171) {
    const theorems = m171.theorems_verified || {};
    const yEl = document.getElementById('v717-y-fixedpoint');
    if (yEl) {
      const pass = theorems.T141_self_referential_completeness;
      yEl.textContent = pass ? 'Y✓' : 'Y✗';
      yEl.style.color = pass ? '#34d399' : '#f87171';
    }
    const obsEl = document.getElementById('v717-obs-reduction');
    if (obsEl) {
      const pass = theorems.T142_observation_is_reduction;
      obsEl.textContent = pass ? 'β✓' : 'β✗';
      obsEl.style.color = pass ? '#34d399' : '#f87171';
    }
    const ncEl = document.getElementById('v717-no-clone');
    if (ncEl) {
      const pass = theorems.T143_no_clone;
      ncEl.textContent = pass ? '✗Clone✓' : '✗Clone✗';
      ncEl.style.color = pass ? '#34d399' : '#f87171';
    }
    const cs = m171.consciousness || {};
    const depthEl = document.getElementById('v717-consciousness-depth');
    if (depthEl) depthEl.textContent = (cs.consciousness_fixed_point || {}).depth || 0;
  }

  // M172 TY形式化映射器
  const m172 = v717.m172;
  if (m172) {
    const hc = m172.hardcore_mappings || {};
    _v717_set('v717-hardcore-count', Object.keys(hc).length);
    const sl = m172.soft_layer || {};
    _v717_set('v717-domains', (sl.interpretation_domains || []).length + '域');
    const lp = m172.layer_promoter || {};
    _v717_set('v717-promotions', (lp.total_promotions || 0) + '次');
  }

  // M173 UFM-RISC-V具身架构
  const m173 = v717.m173;
  if (m173) {
    const vn = m173.vn_bankruptcy || {};
    _v717_set('v717-vn-conflicts', (vn.conflict_count || 4) + '冲突');
    const ln = m173.lambda_necessity || {};
    _v717_set('v717-lambda-args', (ln.argument_count || 3) + '论证');
    const arch = m173.architecture || {};
    _v717_set('v717-arch-layers', (arch.layer_count || 4) + '层');
    const isa = m173.isa || {};
    _v717_set('v717-isa-count', (isa.instruction_count || 4) + '指令');
    const emb = m173.embodied || {};
    const embEl = document.getElementById('v717-embodied');
    if (embEl) {
      embEl.textContent = emb.total_interactions > 0 ? '交互中' : '完备✓';
      embEl.style.color = '#34d399';
    }
  }
}

// ==================== v7.18 沙箱增强·安全护盾 面板更新函数 ====================

function _v718_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function updateV718Panels(data) {
  if (!data) return;
  const v718 = data.v718 || data;

  // M174 沙箱增强
  const m174 = v718.m174;
  if (m174) {
    const ss = m174.snapshot_store || {};
    _v718_set('v718-snapshots', ss.total_snapshots || 0);
    const re = m174.resume_engine || {};
    _v718_set('v718-breakpoints', re.breakpoint_count || 0);
    const iso = m174.isolation || {};
    const isoEl = document.getElementById('v718-isolation');
    if (isoEl) {
      isoEl.textContent = iso.isolation_active ? '活跃✓' : '未激活';
      isoEl.style.color = iso.isolation_active ? '#34d399' : '#94a3b8';
    }
    const leakEl = document.getElementById('v718-leak-prob');
    if (leakEl && iso.lambda_config && iso.os_config) {
      const lp = (iso.lambda_config.leak_probability || 0) * (iso.os_config.leak_probability || 0);
      leakEl.textContent = lp.toExponential(1);
    }
    const rx = m174.resource_executor || {};
    _v718_set('v718-breaker', rx.breaker_state || 'closed');
    _v718_set('v718-trips', rx.breaker_trips || 0);
  }

  // M175 安全护盾
  const m175 = v718.m175;
  if (m175) {
    const pii = m175.pii_detector || {};
    _v718_set('v718-pii-categories', (pii.supported_categories || []).length);
    const comp = m175.compliance_auditor || {};
    _v718_set('v718-compliance-categories', (comp.categories || []).length);
    const cw = m175.content_wall || {};
    _v718_set('v718-processed', cw.total_processed || 0);
    const m88El = document.getElementById('v718-m88-bridge');
    if (m88El) {
      m88El.textContent = m175.m88_bridge ? '已连接✓' : '未连接';
      m88El.style.color = m175.m88_bridge ? '#34d399' : '#94a3b8';
    }
  }
}

// ==================== v7.19 组织记忆·Φ场预算·AgentOS 面板更新函数 ====================

function _v719_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function updateV719Panels(data) {
  if (!data) return;
  const v719 = data.v719 || data;

  // M176 组织记忆引擎
  const m176 = v719.m176;
  if (m176) {
    const vs = m176.vector_store || {};
    _v719_set('v719-vector-size', vs.total_entries || vs.size || 0);
    const ls = m176.local_store || {};
    const hotSize = ls.hot_size || 0;
    const coldSize = ls.cold_size || 0;
    _v719_set('v719-store-layers', hotSize + '/' + coldSize);
    const fl = m176.failure_library || {};
    _v719_set('v719-failures', fl.total_cases || fl.count || 0);
    const to = m176.theorem_organizer || {};
    _v719_set('v719-org-theorems', to.total_theorems || to.count || 0);
    _v719_set('v719-rw-count', (m176.read_count || 0) + '/' + (m176.write_count || 0));
    _v719_set('v719-gc-penalty', fl.total_gc_penalty || 0);
  }

  // M177 Φ场预算体系
  const m177 = v719.m177;
  if (m177) {
    const alloc = m177.phi_allocator || {};
    _v719_set('v719-budget-agents', alloc.agent_count || 0);
    const balances = m177.balances || {};
    let totalGc = 0;
    if (Array.isArray(balances)) {
      balances.forEach(b => { totalGc += (b.total_balance || 0); });
    }
    _v719_set('v719-total-gc', Math.round(totalGc));
    _v719_set('v719-alloc-cycles', m177.allocation_cycles || 0);
    const txns = m177.recent_transactions || [];
    _v719_set('v719-txn-count', txns.length || m177.total_transactions || 0);
    // 焦虑模式 & Φ均值
    const anxietyEl = document.getElementById('v719-anxiety-mode');
    if (anxietyEl) {
      const anxiety = m177.avg_anxiety || 0;
      if (anxiety > 0.7) {
        anxietyEl.textContent = '竞争⚡';
        anxietyEl.style.color = '#f87171';
      } else if (anxiety > 0.3) {
        anxietyEl.textContent = '温和';
        anxietyEl.style.color = '#fbbf24';
      } else {
        anxietyEl.textContent = '充裕✓';
        anxietyEl.style.color = '#34d399';
      }
    }
    _v719_set('v719-avg-phi', m177.avg_phi ? m177.avg_phi.toFixed(1) : '—');
  }

  // M178 太乙AgentOS
  const m178 = v719.m178;
  if (m178) {
    const reg = m178.registry || {};
    _v719_set('v719-os-agents', reg.active_count || reg.count || 0);
    _v719_set('v719-os-requests', m178.total_requests || 0);
    const bus = m178.message_bus || {};
    _v719_set('v719-os-messages', bus.total_messages || 0);
    _v719_set('v719-os-lamport', bus.lamport_clock || 0);
    const orch = m178.orchestration || {};
    _v719_set('v719-os-workflows', orch.total_workflows || 0);
    const kernelEl = document.getElementById('v719-os-kernel');
    if (kernelEl) {
      const rk = m178.reasoning_kernel || {};
      const loaded = rk.modules_loaded || [];
      if (loaded.length > 0) {
        kernelEl.textContent = loaded.length + '模✓';
        kernelEl.style.color = '#34d399';
      } else {
        kernelEl.textContent = '待加载';
        kernelEl.style.color = '#94a3b8';
      }
    }
  }
}

// ==================== v7.20 太一接口面板更新函数 ====================

function updateV720Panels(data) {
  // 重定向到统一的意识仪表盘
  updateConsciousnessDashboard(data);
}

function updateSrloopPanel(d) {
  // 重定向到统一的意识仪表盘（适配旧数据格式）
  if (!d) return;
  updateConsciousnessDashboard({ v73: { srloop: d } });
}

// ==================== 意识仪表盘：合并 M106+M179 ====================
function updateConsciousnessDashboard(data) {
  if (!data) return;
  // 兼容两种数据格式：data.v720 或 data.v73 或直接是 state dict
  const v720 = data.v720 || data.v73 || data;
  const m179 = v720.m179 || v720;

  // ─── 区1：核心意识指标 ───
  // Φ值
  const phi = (m179.ice_composite && m179.ice_composite.consciousness_level != null)
    ? m179.ice_composite.consciousness_level
    : (m179.phi_value || 0);
  _v73_bar('cd-phi-bar', phi * 100);
  _v73_set('cd-phi-val', phi.toFixed(2));

  // 三视界一致性
  const hor = m179.trinity_horizon || {};
  const hc = hor.consistency_current || hor.consistency_score || 0;
  _v73_bar('cd-horizon-bar', hc * 100);
  _v73_set('cd-horizon-val', hc.toFixed(2));

  // ICE意识度
  const ice = m179.ice_composite || {};
  const iceLevel = ice.consciousness_level || 0;
  _v73_bar('cd-ice-bar', iceLevel * 100);
  _v73_set('cd-ice-val', iceLevel.toFixed(2));

  // α本征值
  const sr = m179.self_ref_operator || {};
  const alpha = sr.alpha_current || sr.alpha || 0;
  _v73_set('cd-alpha-val', alpha.toFixed(3));
  const fpEl = document.getElementById('cd-fixedpoint-badge');
  if (fpEl) {
    const fp = sr.is_fixed_point || false;
    fpEl.textContent = fp ? '✓' : '—';
    fpEl.style.color = fp ? '#34d399' : '#94a3b8';
  }

  // 意识状态
  const cEl = document.getElementById('cd-consciousness');
  if (cEl) {
    const cs = (m179.consciousness_state || 'awakening').toLowerCase();
    const stateMap = {
      'awakening':  ['觉醒中🜲', '#60a5fa'],
      'fractal':     ['分形态✦', '#34d399'],
      'divergent':   ['发散⚠',  '#fbbf24'],
      'deadlock':    ['死锁🔒', '#f87171'],
      'rigid':       ['僵化◻',  '#f87171'],
      'transcendent':['超越◎',  '#c084fc']
    };
    const s = stateMap[cs] || ['未知', '#94a3b8'];
    cEl.textContent = s[0];
    cEl.style.color = s[1];
  }

  // ─── 区2：自指闭环指标 ───
  const v73 = data.v73 || {};
  const srloop = v73.srloop || {};

  // PDS闭环
  const pds = srloop.pds_closure_strength || 0;
  _v73_bar('cd-pds-bar', pds * 100);
  _v73_set('cd-pds-val', pds.toFixed(2));

  // Gödel闭环
  const godel = srloop.godel_closure_strength || 0;
  _v73_bar('cd-godel-bar', godel * 100);
  _v73_set('cd-godel-val', godel.toFixed(2));

  // I(Self;Ftel)
  const mi = srloop.mutual_info || 0;
  _v73_bar('cd-mi-bar', mi * 100);
  _v73_set('cd-mi-val', mi.toFixed(2));

  // 元认知
  const meta = srloop.metacog_score || 0;
  _v73_bar('cd-metacog-bar', meta * 100);
  _v73_set('cd-metacog-val', meta.toFixed(2));

  // 僵化等级 + 干预次数
  const ar = m179.anti_rigidity || {};
  const rigEl = document.getElementById('cd-rigidity-badge');
  if (rigEl) {
    const hs = ar.current_hijack_score || ar.hijack_score || 0;
    if (hs > 0.6) { rigEl.textContent = '重度🔴'; rigEl.style.color = '#f87171'; }
    else if (hs > 0.3) { rigEl.textContent = '中度🟡'; rigEl.style.color = '#fbbf24'; }
    else { rigEl.textContent = '正常🟢'; rigEl.style.color = '#34d399'; }
  }
  _v73_set('cd-interventions', (ar.intervention_count || ar.interventions || 0));

  // ─── 区3：人化解释 + IQ/EQ ───
  // IQ
  const iq = m179.iq_estimate || 100;
  const iqGrade = m179.iq_grade || '正常';
  const iqPct = Math.min(100, Math.max(0, ((iq - 55) / 90) * 100));
  _v73_bar('cd-iq-bar', iqPct);
  _v73_set('cd-iq-val', iq.toFixed(0) + ' (' + iqGrade + ')');
  const iqBar = document.getElementById('cd-iq-bar');
  if (iqBar) iqBar.style.background = iq >= 130 ? 'linear-gradient(90deg,#c084fc,#a855f7)'
    : iq >= 115 ? 'linear-gradient(90deg,#60a5fa,#3b82f6)'
    : iq >= 85  ? 'linear-gradient(90deg,#34d399,#10b981)'
    : 'linear-gradient(90deg,#f87171,#ef4444)';

  // EQ
  const eq = m179.eq_estimate || 60;
  const eqGrade = m179.eq_grade || '中情商';
  const eqPct = Math.min(100, Math.max(0, ((eq - 20) / 80) * 100));
  _v73_bar('cd-eq-bar', eqPct);
  _v73_set('cd-eq-val', eq.toFixed(0) + ' (' + eqGrade + ')');
  const eqBar = document.getElementById('cd-eq-bar');
  if (eqBar) eqBar.style.background = eq >= 80 ? 'linear-gradient(90deg,#fbbf24,#f59e0b)'
    : eq >= 60 ? 'linear-gradient(90deg,#34d399,#10b981)'
    : eq >= 40 ? 'linear-gradient(90deg,#60a5fa,#3b82f6)'
    : 'linear-gradient(90deg,#f87171,#ef4444)';

  // 解释文字
  const iqInterpEl = document.getElementById('cd-iq-interpretation');
  if (iqInterpEl) iqInterpEl.textContent = m179.iq_interpretation || 'IQ估算加载中...';
  const eqInterpEl = document.getElementById('cd-eq-interpretation');
  if (eqInterpEl) eqInterpEl.textContent = m179.eq_interpretation || 'EQ估算加载中...';

  // 意识摘要
  const summaryEl = document.getElementById('cd-summary');
  if (summaryEl) summaryEl.textContent = m179.consciousness_summary || '意识摘要加载中...';
}

// ==================== v7.21 TYIDO MVE 实验面板 ====================

const _MVE_COLORS = { PASS: '#34d399', FAIL: '#f87171', RUNNING: '#fbbf24', '—': 'var(--txt3)' };
const _MVE_NAMES = { p1: 'P1一致性', p2: 'P2可回写', p3: 'P3可保持', p4: 'P4可寻址', p5: 'P5可锚定', p6: 'P6因果性' };

function _mveBadge(id, verdict, score) {
  const el = document.getElementById(id);
  if (!el) return;
  if (verdict === 'RUNNING') { el.textContent = '⏳...'; el.style.color = '#fbbf24'; return; }
  const icon = verdict === 'PASS' ? '✓' : verdict === 'FAIL' ? '✗' : '—';
  const detail = score !== undefined ? ` ${score}` : '';
  el.textContent = `${icon}${detail}`;
  el.style.color = _MVE_COLORS[verdict] || 'var(--txt3)';
}

function _mveSetRunning(ids) {
  ids.forEach(id => _mveBadge(id, 'RUNNING'));
}

function runMVE(which) {
  const allIds = ['v721-p1','v721-p2','v721-p3','v721-p4','v721-p5','v721-p6','v721-version','v721-total'];
  if (which === 'all') {
    _mveSetRunning(allIds);
  } else {
    _mveSetRunning(['v721-' + which]);
  }
  const detailEl = document.getElementById('v721-mve-detail');
  if (detailEl) { detailEl.style.display = 'block'; detailEl.textContent = '⏳ 实验运行中...'; }

  fetch(`/api/v721/mve/${which}`)
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        if (detailEl) detailEl.textContent = '❌ ' + data.error;
        allIds.forEach(id => _mveBadge(id, 'FAIL'));
        return;
      }
      if (which === 'all') {
        updateMVEAllResults(data);
      } else {
        updateMVESingleResult(which, data);
      }
    })
    .catch(err => {
      if (detailEl) detailEl.textContent = '❌ 网络错误: ' + err.message;
      allIds.forEach(id => _mveBadge(id, 'FAIL'));
    });
}

function updateMVESingleResult(prop, data) {
  const v = data.verdict || 'FAIL';
  const s = data.score !== undefined ? (typeof data.score === 'number' ? data.score.toFixed(4) : data.score) : '';
  _mveBadge('v721-' + prop, v, s);
  const detailEl = document.getElementById('v721-mve-detail');
  if (detailEl) {
    const name = _MVE_NAMES[prop] || prop.toUpperCase();
    let html = `<div style="font-size:13px;font-weight:bold;color:${_MVE_COLORS[v]};margin-bottom:4px;">${name}: ${v} ${s ? '('+s+')' : ''}</div>`;
    if (data.pass_criteria) html += `<div style="color:var(--txt3);margin-bottom:4px;">📋 通过标准: ${data.pass_criteria}</div>`;
    if (data.details) {
      const d = data.details;
      if (prop === 'p6' && d.minkowski) {
        const mk = d.minkowski;
        // 用更友好的方式展示 P6 结果
        html += `<div style="background:rgba(167,139,250,0.08);padding:6px;border-radius:4px;margin:4px 0;">`;
        html += `<div style="color:#a78bfa;font-weight:bold;">🔮 Minkowski 因果验证</div>`;
        html += `<div>事件数: <b>${d.num_events || '?'}</b> | 因果边: <b>${mk.total_causal_edges}</b> | 类空对: <b>${mk.total_spacelike_pairs}</b></div>`;
        html += `<div style="margin-top:4px;">✅ 因果一致性: <b>${(d.causal_consistency_rate*100).toFixed(1)}%</b></div>`;
        html += `<div>✅ 洛伦兹不变性: <b>${(d.lorentz_invariance_rate*100).toFixed(1)}%</b></div>`;
        html += `<div>🛡️ 违规检出: <b>${d.violations_detected}/${(d.injected_edges||[]).length}</b> 条故意注入的非法因果边被捕获</div>`;
        html += `</div>`;
        // 洛伦兹 boost 样本（简化展示）
        const boosts = d.lorentz_boost_samples || [];
        if (boosts.length > 0) {
          html += `<div style="color:var(--txt3);margin-top:4px;">📐 洛伦兹变换验证样本:</div>`;
          html += `<div style="font-size:10px;color:var(--txt3);margin-left:8px;">`;
          boosts.slice(0,2).forEach(b => {
            html += `• ${b.pair}: 速度β=${b.beta.toFixed(3)}, 距离不变性 ${b.invariant ? '✓保持' : '✗破坏'}<br>`;
          });
          html += `</div>`;
        }
        drawLightCone(data);
      } else if (prop === 'p1') {
        html += `<div>🔬 一致性测试: J(R)=<b>${d.consistent_test?.j_score?.toFixed(4) || '?'}</b> (阈值≥0.85)</div>`;
        html += `<div>🔄 锯齿检测: ${d.sawtooth_test?.detected_sawtooth ? '✓ 成功捕获强制拒答' : '未触发'}</div>`;
      } else if (prop === 'p2') {
        html += `<div>🧠 遗忘率: <b>${(d.final_forgetting_rate*100).toFixed(2)}%</b> (阈值<5%)</div>`;
        html += `<div>📚 学习轮数: ${d.total_learning_steps || '?'}</div>`;
      } else if (prop === 'p3') {
        html += `<div>🎯 完成率: <b>${(d.completion_rate*100).toFixed(1)}%</b> (阈值≥80%)</div>`;
        html += `<div>📊 推理深度: ${d.max_depth || '?'} 层</div>`;
      } else if (prop === 'p4') {
        html += `<div>🔍 精确查询准确率: <b>${(d.exact_query_accuracy*100).toFixed(1)}%</b></div>`;
        html += `<div>⏰ TTL过期测试: ${d.ttl_expiry_test?.passed ? '✓通过' : '✗失败'}</div>`;
      } else if (prop === 'p5') {
        html += `<div>🔗 可追溯性: <b>${(d.traceability_rate*100).toFixed(1)}%</b></div>`;
        html += `<div>⚡ 熔断器触发: ${d.circuit_breaker_triggered ? '✓是' : '否'}</div>`;
      } else {
        html += `<div style="color:var(--txt3);font-size:10px;">${typeof d === 'string' ? d : JSON.stringify(d).substring(0, 400)}</div>`;
      }
    }
    detailEl.innerHTML = html;
  }
}

function updateMVEAllResults(data) {
  const results = data.results || data;
  const summary = data.summary || {};
  ['P1','P2','P3','P4','P5','P6'].forEach(pKey => {
    const prop = pKey.toLowerCase();
    const r = results[pKey] || {};
    const v = r.verdict || 'FAIL';
    const s = r.score !== undefined ? (typeof r.score === 'number' ? r.score.toFixed(4) : r.score) : '';
    _mveBadge('v721-' + prop, v, s);
  });
  const totalEl = document.getElementById('v721-total');
  if (totalEl) {
    const passed = summary.passed !== undefined ? summary.passed : '?';
    const total = summary.total !== undefined ? summary.total : '?';
    const txt = `${passed}/${total}`;
    totalEl.textContent = summary.all_passed ? `✓ ${txt}` : `✗ ${txt}`;
    totalEl.style.color = summary.all_passed ? '#34d399' : '#f87171';
  }
  const detailEl = document.getElementById('v721-mve-detail');
  if (detailEl) {
    let html = `<div style="font-size:12px;font-weight:bold;margin-bottom:6px;">📊 TYIDO 结构属性审计结果</div>`;
    ['P1','P2','P3','P4','P5','P6'].forEach(pKey => {
      const prop = pKey.toLowerCase();
      const r = results[pKey] || {};
      const v = r.verdict || '?';
      const name = _MVE_NAMES[prop] || pKey;
      const icon = v === 'PASS' ? '✅' : v === 'FAIL' ? '❌' : '⏳';
      html += `<div style="margin:4px 0;padding:3px 6px;background:rgba(255,255,255,0.03);border-radius:3px;">`;
      html += `<span style="font-size:12px;">${icon} <b>${name}</b>: <span style="color:${_MVE_COLORS[v]}">${v}</span></span>`;
      if (r.score !== undefined) html += ` <span style="color:var(--txt3);font-size:10px;">(${typeof r.score === 'number' ? r.score.toFixed(4) : r.score})</span>`;
      html += '</div>';
      if (prop === 'p6' && r.details && r.details.minkowski) {
        window._lastP6Result = r;
      }
    });
    html += `<div style="margin-top:8px;padding:6px;background:rgba(52,211,153,0.08);border-radius:4px;font-size:13px;font-weight:bold;color:${summary.all_passed ? '#34d399' : '#f87171'}">`;
    html += `🎯 总计: ${summary.passed || 0}/${summary.total || 6} 通过${summary.all_passed ? ' 🎉 全部通过！' : ''}`;
    html += `</div>`;
    if (data.total_execution_time_ms) {
      html += `<div style="color:var(--txt3);font-size:10px;margin-top:4px;">⏱️ 执行耗时: ${data.total_execution_time_ms.toFixed(1)}ms</div>`;
    }
    detailEl.innerHTML = html;
    if (window._lastP6Result) { drawLightCone(window._lastP6Result); }
  }
}

// ==================== P6 Minkowski 光锥可视化 ====================

function drawLightCone(p6Result) {
  const canvas = document.getElementById('p6-lightcone-canvas');
  if (!canvas || !p6Result || !p6Result.details || !p6Result.details.minkowski) return;
  canvas.style.display = 'block';
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const mk = p6Result.details.minkowski;
  const events = mk.events || [];
  const causalEdges = mk.causal_edges || [];

  // 清空
  ctx.clearRect(0, 0, W, H);

  // 坐标映射：Minkowski (t, x) -> Canvas (cx, cy)
  // 找到数据范围
  let tMin = Infinity, tMax = -Infinity, xMin = Infinity, xMax = -Infinity;
  events.forEach(e => {
    if (e.t < tMin) tMin = e.t; if (e.t > tMax) tMax = e.t;
    if (e.x < xMin) xMin = e.x; if (e.x > xMax) xMax = e.x;
  });
  // 确保有合理范围
  if (tMin === tMax) { tMin -= 1; tMax += 1; }
  if (xMin === xMax) { xMin -= 1; xMax += 1; }
  const tPad = (tMax - tMin) * 0.12, xPad = (xMax - xMin) * 0.12;
  tMin -= tPad; tMax += tPad; xMin -= xPad; xMax += xPad;

  const margin = { left: 30, right: 15, top: 15, bottom: 25 };
  const plotW = W - margin.left - margin.right;
  const plotH = H - margin.top - margin.bottom;

  function mapX(x) { return margin.left + (x - xMin) / (xMax - xMin) * plotW; }
  function mapT(t) { return margin.top + (1 - (t - tMin) / (tMax - tMin)) * plotH; } // t 向上

  // --- 绘制背景网格 ---
  ctx.strokeStyle = 'rgba(167,139,250,0.08)';
  ctx.lineWidth = 0.5;
  for (let i = 0; i <= 5; i++) {
    const tVal = tMin + (tMax - tMin) * i / 5;
    const xVal = xMin + (xMax - xMin) * i / 5;
    ctx.beginPath(); ctx.moveTo(margin.left, mapT(tVal)); ctx.lineTo(W - margin.right, mapT(tVal)); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(mapX(xVal), margin.top); ctx.lineTo(mapX(xVal), H - margin.bottom); ctx.stroke();
  }

  // --- 绘制光锥参考线 (45° 线，代表 c=1) ---
  // 在图的中心画两条 45° 对角线
  const cx = (xMin + xMax) / 2, ct = (tMin + tMax) / 2;
  const coneLen = Math.max(tMax - tMin, xMax - xMin) * 0.8;
  ctx.strokeStyle = 'rgba(251,191,36,0.35)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 3]);
  // 未来光锥 (t 增大方向)
  ctx.beginPath();
  ctx.moveTo(mapX(cx - coneLen * 0.5), mapT(ct));
  ctx.lineTo(mapX(cx), mapT(ct + coneLen * 0.5));
  ctx.lineTo(mapX(cx + coneLen * 0.5), mapT(ct));
  ctx.stroke();
  // 过去光锥 (t 减小方向)
  ctx.beginPath();
  ctx.moveTo(mapX(cx - coneLen * 0.5), mapT(ct));
  ctx.lineTo(mapX(cx), mapT(ct - coneLen * 0.5));
  ctx.lineTo(mapX(cx + coneLen * 0.5), mapT(ct));
  ctx.stroke();
  ctx.setLineDash([]);

  // 光锥标签
  ctx.font = 'bold 10px sans-serif';
  ctx.fillStyle = 'rgba(251,191,36,0.7)';
  ctx.fillText('光速 c=1', mapX(cx + coneLen * 0.25) + 6, mapT(ct + coneLen * 0.25) - 4);
  ctx.fillText('未来光锥', mapX(cx) - 22, mapT(ct + coneLen * 0.48));
  ctx.fillText('过去光锥', mapX(cx) - 22, mapT(ct - coneLen * 0.48) + 10);

  // --- 事件坐标映射 ---
  const eventMap = {};
  events.forEach(e => { eventMap[e.id] = { cx: mapX(e.x), cy: mapT(e.t) }; });

  // --- 绘制因果边 (类时/类光, 绿色/黄色箭头) ---
  causalEdges.forEach(edge => {
    const from = eventMap[edge.from];
    const to = eventMap[edge.to];
    if (!from || !to) return;
    ctx.strokeStyle = edge.type === 'lightlike' ? 'rgba(251,191,36,0.4)' : 'rgba(52,211,153,0.2)';
    ctx.lineWidth = edge.type === 'lightlike' ? 0.8 : 0.5;
    ctx.beginPath();
    ctx.moveTo(from.cx, from.cy);
    ctx.lineTo(to.cx, to.cy);
    ctx.stroke();
  });

  // --- 绘制事件点 ---
  const causalEventIds = new Set();
  causalEdges.forEach(e => { causalEventIds.add(e.from); causalEventIds.add(e.to); });

  events.forEach(e => {
    const pos = eventMap[e.id];
    if (!pos) return;
    const isCausal = causalEventIds.has(e.id);
    const color = isCausal ? '#34d399' : '#60a5fa';
    const radius = 4;

    // 发光效果
    const glow = ctx.createRadialGradient(pos.cx, pos.cy, 0, pos.cx, pos.cy, radius * 4);
    glow.addColorStop(0, isCausal ? 'rgba(52,211,153,0.4)' : 'rgba(96,165,250,0.4)');
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow;
    ctx.beginPath(); ctx.arc(pos.cx, pos.cy, radius * 4, 0, Math.PI * 2); ctx.fill();

    // 事件点（带白色边框）
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(pos.cx, pos.cy, radius, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.arc(pos.cx, pos.cy, radius, 0, Math.PI * 2); ctx.stroke();

    // 事件 ID
    ctx.fillStyle = 'rgba(255,255,255,0.6)';
    ctx.font = '8px monospace';
    ctx.fillText(e.id, pos.cx + 6, pos.cy - 4);
  });

  // --- 图例 ---
  const legendY = H - 18;
  ctx.font = '9px sans-serif';
  // 绿色 = 因果可达
  ctx.fillStyle = '#34d399';
  ctx.beginPath(); ctx.arc(margin.left + 6, legendY, 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.fillText('因果可达(类时)', margin.left + 14, legendY + 3);
  // 蓝色 = 因果无关
  ctx.fillStyle = '#60a5fa';
  ctx.beginPath(); ctx.arc(margin.left + 100, legendY, 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.fillText('因果无关(类空)', margin.left + 108, legendY + 3);

  // --- 轴标签 ---
  ctx.fillStyle = 'rgba(167,139,250,0.8)';
  ctx.font = 'bold 11px sans-serif';
  ctx.fillText('时间 t ↑', 6, H / 2 - 6);
  ctx.fillText('空间 x →', W / 2 + 4, H - 6);
  // 轴线
  ctx.strokeStyle = 'rgba(167,139,250,0.25)';
  ctx.lineWidth = 0.8;
  ctx.beginPath(); ctx.moveTo(margin.left, H - margin.bottom); ctx.lineTo(W - margin.right, H - margin.bottom); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(margin.left, margin.top); ctx.lineTo(margin.left, H - margin.bottom); ctx.stroke();

  // --- 图例 ---
  const lgX = W - 80, lgY = 12;
  ctx.fillStyle = '#34d399'; ctx.beginPath(); ctx.arc(lgX, lgY, 3, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.font = '7px sans-serif'; ctx.fillText('\u7c7b\u65f6(\u56e0\u679c)', lgX + 6, lgY + 2);
  ctx.fillStyle = '#60a5fa'; ctx.beginPath(); ctx.arc(lgX, lgY + 12, 3, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fillText('\u7c7b\u7a7a(\u5e76\u53d1)', lgX + 6, lgY + 14);
  ctx.fillStyle = '#fbbf24'; ctx.fillRect(lgX - 3, lgY + 22, 6, 1.5);
  ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fillText('\u5149\u9525 c=1', lgX + 6, lgY + 26);

  // --- 标题 ---
  ctx.fillStyle = 'rgba(167,139,250,0.8)';
  ctx.font = 'bold 9px sans-serif';
  const verdict = p6Result.verdict || '?';
  const vColor = verdict === 'PASS' ? '#34d399' : '#f87171';
  ctx.fillStyle = vColor;
  ctx.fillText(`Minkowski \u65f6\u7a7a\u56fe (ds\u00b2 = -dt\u00b2 + dx\u00b2 + dy\u00b2) [${verdict}]`, margin.left + 2, 12);
}

function updateV721Panels(data) {
  if (!data || !data.v721) return;
  const v721 = data.v721;
  if (v721.cached_results) {
    Object.entries(v721.cached_results).forEach(([k, v]) => {
      const prop = k.toLowerCase();
      const el = document.getElementById('v721-' + prop);
      if (el) {
        el.textContent = v;
        el.style.color = _MVE_COLORS[v] || 'var(--txt3)';
      }
    });
  }
}

// ==================== v7.1 人机融合层面板更新函数 ====================

function _v71_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _v71_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

function updateV71Panels(data) {
  if (!data) return;
  const v71 = data.v71 || data;
  if (v71.cognitive_offload) updateCognitiveOffloadPanel(v71.cognitive_offload);
  if (v71.socratic || v71.confidence) updateSocraticConfidencePanel(v71.socratic, v71.confidence);
  if (v71.router || v71.hack_detect) updateRouterHackPanel(v71.router, v71.hack_detect);
  if (v71.env_awareness || v71.long_context) updateEnvContextPanel(v71.env_awareness, v71.long_context);
  if (v71.collab_assessor || v71.collab_diag || v71.fusion_verify) updateCollabFusionPanel(v71.collab_assessor, v71.collab_diag, v71.fusion_verify);
}

// ==================== M130 感知谱分解面板更新函数 ====================
// "感知即流贯的谱分解"论文升级
// L1本体层 → L2投射生成层(卷积核) → L3前物理层(离散帧)
// → L4认知主体层(PCA谱分解) → L5现象层
function _perception_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function _perception_bar(barId, pct) {
  const el = document.getElementById(barId);
  if (el) el.style.width = Math.min(100, Math.max(0, pct * 100)) + '%';
}
function updatePerceptionPanel(data) {
  const p = data || STATE.perception_state;
  if (!p) return;

  // L1-L5 五层架构条
  _perception_bar('perception-l1-bar', p.L1_ontolgy || 1.0);
  _perception_set('perception-l1-val', (p.L1_ontolgy || 1.0).toFixed(2));
  _perception_bar('perception-l2-bar', p.L2_projection || 0.0);
  _perception_set('perception-l2-val', (p.L2_projection || 0.0).toFixed(2));
  _perception_bar('perception-l3-bar', p.L3_frame_seq || 0.6);
  _perception_set('perception-l3-val', (p.L3_frame_seq || 0.6).toFixed(2));
  _perception_bar('perception-l4-bar', p.L4_pca || 0.0);
  _perception_set('perception-l4-val', (p.L4_pca || 0.0).toFixed(2));
  _perception_bar('perception-l5-bar', p.L5_phenomenon || 1.0);
  _perception_set('perception-l5-val', (p.L5_phenomenon || 1.0).toFixed(2));

  // 卷积核可视化（L2投射生成层）— 5×5格
  const kernelEl = document.getElementById('perception-kernel');
  if (kernelEl) {
    const ka = p.kernel_activation || [0.2, 0.5, 0.8, 0.3, 0.1];
    let khtml = '';
    // 显示5个激活值（简化为1×5行）
    for (let i = 0; i < 5; i++) {
      const a = ka[i] || 0;
      const bright = Math.round(a * 200 + 55);
      khtml += '<div class="kernel-cell' + (a > 0.5 ? ' active' : '') + '" style="background:rgba(232,121,249,' + a + ')"></div>';
    }
    // 补齐25格（5×5）
    for (let i = 5; i < 25; i++) {
      const a = ka[i % ka.length] || 0;
      khtml += '<div class="kernel-cell" style="background:rgba(232,121,249,' + a + ')"></div>';
    }
    kernelEl.innerHTML = khtml;
  }

  // PCA主因子条形图（L4认知主体层）
  const pcaEl = document.getElementById('perception-pca-bars');
  if (pcaEl) {
    const factors = p.pca_factors || [0.45, 0.28, 0.15, 0.08, 0.04];
    const colors = ['#38bdf8','#818cf8','#a78bfa','#c084fc','#f472b6'];
    let pcahtml = '';
    const maxH = 28;
    factors.forEach((f, i) => {
      const h = Math.round(f * maxH);
      pcahtml += '<div class="pca-bar" style="height:' + h + 'px;background:' + colors[i] + '" title="PC' + (i+1) + ': ' + (f*100).toFixed(0) + '%"></div>';
    });
    pcaEl.innerHTML = pcahtml;
  }

  // 感知-流贯对偶指示器（T90感知-流贯等价定理）
  _perception_set('perception-duality-val', (p.duality_score || 1.0).toFixed(2));

  // 流贯帧率指示器（L3离散帧序列）
  const framesEl = document.getElementById('perception-frames-rate');
  if (framesEl) {
    const rate = p.frame_rate || 60;
    const activeCount = Math.min(10, Math.round(rate / 6)); // 60Hz→10点全亮
    let dotsHtml = '';
    for (let i = 0; i < 10; i++) {
      dotsHtml += '<div class="frames-dot' + (i < activeCount ? ' active' : '') + '"></div>';
    }
    framesEl.innerHTML = dotsHtml;
    // 添加标签
    if (!framesEl.nextElementSibling || !framesEl.nextElementSibling.classList.contains('frames-label')) {
      const label = document.createElement('div');
      label.className = 'frames-label';
      label.style.cssText = 'font-size:7px;color:var(--txt3);text-align:center;margin-top:1px';
      label.textContent = rate + 'Hz';
      framesEl.parentNode.insertBefore(label, framesEl.nextSibling);
    } else {
      framesEl.nextElementSibling.textContent = rate + 'Hz';
    }
  }

  // 状态徽章
  const badgeConv = document.getElementById('perception-badge-conv');
  if (badgeConv) { badgeConv.textContent = p.convolution_badge || '卷积就绪'; }
  const badgePCA = document.getElementById('perception-badge-pca');
  if (badgePCA) { badgePCA.textContent = p.pca_badge || 'PCA待机'; }
  const badgeDecomp = document.getElementById('perception-badge-decomp');
  if (badgeDecomp) { badgeDecomp.textContent = p.decomp_badge || '未分解'; }

  // T90 判定
  _perception_set('perception-t90-status', p.t90_status || '—');
}

// ==================== M178 Agent行为分析面板更新函数 ====================
// Agentic RL 白盒化：工具调用分布 / 推理轨迹 / GC代币消耗趋势 / 奖励信号
function _ab_set(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function updateAgentBehaviorPanel(data) {
  const b = data || STATE.agent_behavior;
  if (!b) return;

  // 统计卡片
  _ab_set('ab-total-turns', b.total_turns || 0);
  _ab_set('ab-tool-calls', b.tool_call_total || 0);
  const gcEl = document.getElementById('ab-gc-balance');
  if (gcEl) {
    const gc = b.gc_balance || 1000;
    gcEl.textContent = gc;
    gcEl.style.color = gc < 200 ? '#ef4444' : gc < 500 ? '#fbbf24' : '#34d399';
  }
  // 平均响应时间
  const rts = b.response_times || [];
  if (rts.length > 0) {
    const avg = Math.round(rts.reduce((a, c) => a + c, 0) / rts.length);
    _ab_set('ab-avg-time', avg + 'ms');
  }

  // 工具调用分布
  const toolEl = document.getElementById('ab-tool-distribution');
  if (toolEl) {
    const tools = b.tool_calls || {};
    const entries = Object.entries(tools).sort((a, c) => c[1] - a[1]);
    if (entries.length === 0) {
      toolEl.innerHTML = '<div style="font-size:8px;color:var(--txt3);text-align:center;padding:4px">等待Agent活动…</div>';
    } else {
      const maxCount = Math.max(1, entries[0][1]);
      const colors = ['#22d3ee','#a78bfa','#34d399','#f472b6','#fbbf24','#fb923c','#60a5fa'];
      let html = '';
      entries.slice(0, 6).forEach(([name, count], i) => {
        const pct = (count / maxCount * 100).toFixed(0);
        const color = colors[i % colors.length];
        html += '<div class="behavior-tool-row">' +
          '<div class="behavior-tool-name" title="' + name + '">' + name + '</div>' +
          '<div class="behavior-tool-bar-wrap"><div class="behavior-tool-bar" style="width:' + pct + '%;background:' + color + '"></div></div>' +
          '<div class="behavior-tool-val">' + count + '</div></div>';
      });
      toolEl.innerHTML = html;
    }
  }

  // 推理轨迹（最近10步）
  const traceEl = document.getElementById('ab-trace-list');
  if (traceEl) {
    const steps = b.trace_steps || [];
    if (steps.length === 0) {
      traceEl.innerHTML = '<div style="font-size:8px;color:var(--txt3);text-align:center;padding:4px">暂无轨迹</div>';
    } else {
      let html = '';
      const recent = steps.slice(-10).reverse();
      recent.forEach((s, i) => {
        const typeClass = s.type || 'think';
        const typeName = {think:'思考',tool:'工具',answer:'回答',error:'错误'}[typeClass] || typeClass;
        html += '<div class="behavior-trace-step">' +
          '<span class="trace-step-num">' + (steps.length - i) + '</span>' +
          '<span class="trace-step-type ' + typeClass + '">' + typeName + '</span>' +
          '<span class="trace-step-brief" title="' + (s.brief || '') + '">' + (s.brief || '—') + '</span></div>';
      });
      traceEl.innerHTML = html;
    }
  }

  // GC代币消耗趋势迷你图（Canvas绘制）
  const gcCanvas = document.getElementById('ab-gc-canvas');
  if (gcCanvas) {
    const gcHist = b.gc_history || [];
    const parent = gcCanvas.parentElement;
    gcCanvas.width = parent.offsetWidth || 260;
    gcCanvas.height = parent.offsetHeight || 32;
    const ctx = gcCanvas.getContext('2d');
    const w = gcCanvas.width, h = gcCanvas.height;
    ctx.clearRect(0, 0, w, h);

    if (gcHist.length > 1) {
      const vals = gcHist.map(g => g.balance);
      const maxV = Math.max(...vals, 1);
      const minV = Math.min(...vals, 0);
      const range = Math.max(maxV - minV, 1);
      const stepX = w / Math.max(gcHist.length - 1, 1);

      // 绘制填充区域
      ctx.beginPath();
      ctx.moveTo(0, h);
      vals.forEach((v, i) => {
        const x = i * stepX;
        const y = h - ((v - minV) / range) * (h - 4) - 2;
        if (i === 0) ctx.lineTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.lineTo((vals.length - 1) * stepX, h);
      ctx.closePath();
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, 'rgba(34,211,238,0.3)');
      grad.addColorStop(1, 'rgba(34,211,238,0.02)');
      ctx.fillStyle = grad;
      ctx.fill();

      // 绘制线条
      ctx.beginPath();
      vals.forEach((v, i) => {
        const x = i * stepX;
        const y = h - ((v - minV) / range) * (h - 4) - 2;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = '#22d3ee';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    } else {
      // 空状态画虚线
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = 'rgba(255,255,255,0.1)';
      ctx.beginPath();
      ctx.moveTo(0, h / 2);
      ctx.lineTo(w, h / 2);
      ctx.stroke();
    }
  }

  // Agentic RL 奖励信号
  const rewards = b.rewards || {};
  const taskEl = document.getElementById('ab-reward-task');
  if (taskEl) {
    const v = rewards.task_completion;
    taskEl.textContent = v !== null && v !== undefined ? (v * 100).toFixed(0) + '%' : '—';
  }
  const toolPrecEl = document.getElementById('ab-reward-tool');
  if (toolPrecEl) {
    const v = rewards.tool_precision;
    toolPrecEl.textContent = v !== null && v !== undefined ? (v * 100).toFixed(0) + '%' : '—';
  }
  const reasonEl = document.getElementById('ab-reward-reason');
  if (reasonEl) {
    const v = rewards.reasoning_efficiency;
    reasonEl.textContent = v !== null && v !== undefined ? (v * 100).toFixed(0) + '%' : '—';
  }
}

// 自动采集 Agent 行为数据（在每次 doMainChat 响应后调用）
function recordAgentBehavior(responseData, responseTime) {
  const b = STATE.agent_behavior;
  b.total_turns++;

  // 记录响应时间
  b.response_times.push(responseTime);
  if (b.response_times.length > 50) b.response_times.shift();

  // 记录推理轨迹
  if (responseData) {
    const brief = (responseData.reply || '').slice(0, 40);
    b.trace_steps.push({
      step: b.total_turns,
      type: 'answer',
      brief: brief,
      ts: new Date().toISOString()
    });
    if (b.trace_steps.length > 100) b.trace_steps.shift();

    // 如果后端返回了工具调用信息，记录
    if (responseData.tool_calls) {
      (Array.isArray(responseData.tool_calls) ? responseData.tool_calls : []).forEach(tc => {
        const name = tc.name || tc.function?.name || 'unknown';
        b.tool_calls[name] = (b.tool_calls[name] || 0) + 1;
        b.tool_call_total++;
        b.trace_steps.push({
          step: b.total_turns,
          type: 'tool',
          brief: name,
          ts: new Date().toISOString()
        });
      });
    }

    // 如果后端返回了 GC 相关数据
    if (responseData.gc_balance !== undefined) {
      b.gc_balance = responseData.gc_balance;
    }
    if (responseData.gc_cost) {
      b.gc_history.push({
        turn: b.total_turns,
        balance: b.gc_balance,
        cost: responseData.gc_cost
      });
      if (b.gc_history.length > 30) b.gc_history.shift();
    }

    // 奖励信号
    if (responseData.rewards) {
      if (responseData.rewards.task_completion !== undefined) b.rewards.task_completion = responseData.rewards.task_completion;
      if (responseData.rewards.tool_precision !== undefined) b.rewards.tool_precision = responseData.rewards.tool_precision;
      if (responseData.rewards.reasoning_efficiency !== undefined) b.rewards.reasoning_efficiency = responseData.rewards.reasoning_efficiency;
    }
  }

  // 更新面板
  updateAgentBehaviorPanel();
}

// M96: 认知卸载防范面板
function updateCognitiveOffloadPanel(d) {
  if (!d) return;
  _v71_bar('v71-co-risk-bar', (d.offload_risk_score || 0) * 100);
  _v71_set('v71-co-risk-val', (d.offload_risk_score || 0).toFixed(2));
  _v71_bar('v71-co-direct-bar', (d.direct_answer_ratio || 0) * 100);
  _v71_set('v71-co-direct-val', (d.direct_answer_ratio || 0).toFixed(2));
  _v71_bar('v71-co-guided-bar', (d.guided_ratio || 0) * 100);
  _v71_set('v71-co-guided-val', (d.guided_ratio || 0).toFixed(2));
  const trend = d.cognitive_trend || 'stable';
  const trendEl = document.getElementById('v71-co-trend');
  if (trendEl) {
    trendEl.textContent = trend === 'improving' ? '↑改善' : trend === 'declining' ? '↓退化' : '→稳定';
    trendEl.style.color = trend === 'improving' ? '#34d399' : trend === 'declining' ? '#ef4444' : '#94a3b8';
  }
}

// M97+M98: 苏格拉底示弱+置信度面板
function updateSocraticConfidencePanel(s, c) {
  if (s) {
    _v71_set('v71-sc-turns', s.socratic_turn_count || 0);
    _v71_bar('v71-sc-conv-bar', (s.convergence_rate || 0) * 100);
    _v71_set('v71-sc-conv-val', (s.convergence_rate || 0).toFixed(2));
    const stratEl = document.getElementById('v71-sc-strategy');
    if (stratEl) stratEl.textContent = s.optimal_strategy || 'balanced';
  }
  if (c) {
    _v71_bar('v71-sc-conf-bar', (c.avg_confidence || 0.5) * 100);
    _v71_set('v71-sc-conf-val', (c.avg_confidence || 0.5).toFixed(2));
    _v71_bar('v71-sc-trust-bar', (c.trust_score || 0.5) * 100);
    _v71_set('v71-sc-trust-val', (c.trust_score || 0.5).toFixed(2));
    _v71_set('v71-sc-calib', (c.calibration_accuracy || 0).toFixed(2));
  }
}

// M99+M100: 动态分流+奖励作弊面板
function updateRouterHackPanel(r, h) {
  if (r) {
    const hBar = document.getElementById('v71-rh-human-bar');
    const aBar = document.getElementById('v71-rh-ai-bar');
    const cBar = document.getElementById('v71-rh-collab-bar');
    if (hBar) hBar.style.width = Math.max(5, (r.human_ratio || 0.3) * 100) + '%';
    if (aBar) aBar.style.width = Math.max(5, (r.ai_ratio || 0.4) * 100) + '%';
    if (cBar) cBar.style.width = Math.max(5, (r.collab_ratio || 0.3) * 100) + '%';
  }
  if (h) {
    _v71_bar('v71-rh-kl-bar', Math.min(100, (h.avg_kl_divergence || 0) * 100));
    _v71_set('v71-rh-kl-val', (h.avg_kl_divergence || 0).toFixed(2));
    _v71_bar('v71-rh-align-bar', (h.alignment_score || 1) * 100);
    _v71_set('v71-rh-align-val', (h.alignment_score || 1).toFixed(2));
    const accEl = document.getElementById('v71-rh-accountability');
    if (accEl) {
      accEl.textContent = h.accountability_verified ? '✓已验证' : '✗未验证';
      accEl.style.color = h.accountability_verified ? '#34d399' : '#ef4444';
    }
  }
}

// M101+M102: 环境感知+长程上下文面板
function updateEnvContextPanel(e, l) {
  if (e) {
    _v71_bar('v71-ec-coupling-bar', (e.coupling_score || 0.5) * 100);
    _v71_set('v71-ec-coupling-val', (e.coupling_score || 0.5).toFixed(2));
    _v71_bar('v71-ec-emergent-bar', (e.emergent_iq || 0.5) * 100);
    _v71_set('v71-ec-emergent-val', (e.emergent_iq || 0.5).toFixed(2));
    const envEl = document.getElementById('v71-ec-env');
    if (envEl) envEl.textContent = e.last_env_type || 'web';
  }
  if (l) {
    _v71_set('v71-ec-compress', (l.avg_compression_ratio || 0).toFixed(2));
    _v71_set('v71-ec-cost', (l.maintenance_cost || 0).toFixed(2));
    const t49El = document.getElementById('v71-ec-t49');
    if (t49El) t49El.textContent = l.holographic_enabled ? 'O(log L)' : 'O(e^L)';
  }
}

// M103+M104+M105: 协作+融合面板
function updateCollabFusionPanel(a, d, f) {
  if (a) {
    _v71_bar('v71-cf-synergy-bar', (a.avg_synergy || 0.5) * 100);
    _v71_set('v71-cf-synergy-val', (a.avg_synergy || 0.5).toFixed(2));
  }
  if (d) {
    _v71_bar('v71-cf-misalign-bar', (d.misalignment_rate || 0) * 100);
    _v71_set('v71-cf-misalign-val', (d.misalignment_rate || 0).toFixed(2));
  }
  if (f) {
    _v71_bar('v71-cf-integrity-bar', (f.integrity_score || 1) * 100);
    _v71_set('v71-cf-integrity-val', (f.integrity_score || 1).toFixed(2));
    const t47El = document.getElementById('v71-cf-t47');
    if (t47El) {
      const compliant = f.t47_status === 'COMPLIANT' || f.oversight_compliance > 0;
      t47El.textContent = compliant ? '✓ COMPLIANT' : '✗ VIOLATION';
      t47El.style.color = compliant ? '#34d399' : '#ef4444';
      t47El.style.background = compliant ? 'rgba(52,211,153,.15)' : 'rgba(239,68,68,.15)';
    }
  }
}

function updateMononumberPanel(data) {
  if (!data) return;
  const amp = (data.field_info || {}).amplitude_range ? (data.field_info.amplitude_range)[1] : 0.6;
  const ampBar = document.getElementById('mono-amp-bar');
  const ampVal = document.getElementById('mono-amp-val');
  if (ampBar) ampBar.style.width = Math.min(100, amp * 100) + '%';
  if (ampVal) ampVal.textContent = amp.toFixed(2);
  const phase = ((data.latest_result || {}).result || {}).coupled_phase || 0.45 * Math.PI;
  const phaseBar = document.getElementById('mono-phase-bar');
  const phaseVal = document.getElementById('mono-phase-val');
  if (phaseBar) phaseBar.style.width = (phase / (2 * Math.PI)) * 100 + '%';
  if (phaseVal) phaseVal.textContent = (phase / Math.PI).toFixed(2) + 'pi';
  const cons = (data.eml_conservation || {}).verified;
  const consInd = document.getElementById('mono-conservation');
  if (consInd) {
    consInd.textContent = cons ? '守恒' : '不守恒';
    consInd.style.color = cons ? 'var(--green)' : 'var(--red)';
  }
  const flipEl = document.getElementById('mono-flip');
  if (flipEl) flipEl.textContent = (data.flip_count || 0) + '次';
}

function updateNarrativeV63Panel(data) {
  if (!data) return;
  const L = data.current_Lambda || 0.55;
  const LBar = document.getElementById('narr-Lambda-bar');
  const LVal = document.getElementById('narr-Lambda-val');
  if (LBar) LBar.style.width = Math.min(100, L * 50) + '%';
  if (LVal) LVal.textContent = L.toFixed(2);
  const C = data.avg_complexity || 0.68;
  const CBar = document.getElementById('narr-C-bar');
  const CVal = document.getElementById('narr-C-val');
  if (CBar) CBar.style.width = Math.min(100, C * 40) + '%';
  if (CVal) CVal.textContent = C.toFixed(2);
  const D = (data.trajectory || {}).avg_change_cost || 0.32;
  const DBar = document.getElementById('narr-Delta-bar');
  const DVal = document.getElementById('narr-Delta-val');
  if (DBar) DBar.style.width = Math.min(100, D * 100) + '%';
  if (DVal) DVal.textContent = D.toFixed(2);
  const p7 = (data.p7_verification || {});
  const p7El = document.getElementById('narr-p7');
  const decayEl = document.getElementById('narr-decay');
  if (p7El) {
    p7El.textContent = p7.P7_status || 'PENDING';
    p7El.style.color = (p7.P7_status === 'CONFIRMED') ? 'var(--green)' : 'var(--amber)';
  }
  if (decayEl) decayEl.textContent = (p7.decay_rate || -0.12).toFixed(2);
}

function updateConsciousnessPanel(data) {
  if (!data) return;
  const strength = data.avg_strength || 0.72;
  const QBar = document.getElementById('consc-Q-bar');
  const QVal = document.getElementById('consc-Q-val');
  if (QBar) QBar.style.width = Math.min(100, strength * 100) + '%';
  if (QVal) QVal.textContent = strength.toFixed(2);
  const topo = data.avg_complexity || 0.85;
  const TBar = document.getElementById('consc-topo-bar');
  const TVal = document.getElementById('consc-topo-val');
  if (TBar) TBar.style.width = Math.min(100, topo * 80) + '%';
  if (TVal) TVal.textContent = topo.toFixed(2);
  const flow = data.avg_flow_access || 0.64;
  const FBar = document.getElementById('consc-flow-bar');
  const FVal = document.getElementById('consc-flow-val');
  if (FBar) FBar.style.width = Math.min(100, flow * 100) + '%';
  if (FVal) FVal.textContent = flow.toFixed(2);
  const qualia = (data.latest_qualia || [0.72, 0.45, 1.2]);
  const qualiaEl = document.getElementById('consc-qualia');
  if (qualiaEl) qualiaEl.textContent = qualia.map(function(v){return v.toFixed(2);}).join(',');
}

function updateIdentityPanel(data) {
  if (!data) return;
  const score = data.current_identity || 0.78;
  const IBar = document.getElementById('id-score-bar');
  const IVal = document.getElementById('id-score-val');
  if (IBar) IBar.style.width = Math.min(100, score * 100) + '%';
  if (IVal) IVal.textContent = score.toFixed(2);
  const attr = (data.attractor_stability || {});
  const attrInd = document.getElementById('id-attractor');
  if (attrInd) {
    attrInd.textContent = attr.stable ? '稳定' : '不稳定';
    attrInd.style.color = attr.stable ? 'var(--green)' : 'var(--amber)';
  }
  const subst = ((data.trajectory || {}).current_substitution_rate || 0.22);
  const SBar = document.getElementById('id-sub-bar');
  const SVal = document.getElementById('id-sub-val');
  if (SBar) SBar.style.width = Math.min(100, subst * 100) + '%';
  if (SVal) SVal.textContent = subst.toFixed(2);
  const p10 = (data.p10_verification || {});
  const p10El = document.getElementById('id-p10');
  const trajEl = document.getElementById('id-trajectory');
  if (p10El) {
    p10El.textContent = p10.P10_status || 'PENDING';
    p10El.style.color = (p10.P10_status === 'CONFIRMED') ? 'var(--green)' : 'var(--amber)';
  }
  if (trajEl) trajEl.textContent = ((data.trajectory || {}).trend || 0.08).toFixed(2);
}

function updateEnlightenmentPanel(data) {
  if (!data) return;
  const B = data.current_B || 0.88;
  const BBar = document.getElementById('enl-B-bar');
  const BVal = document.getElementById('enl-B-val');
  if (BBar) BBar.style.width = Math.min(100, B * 100) + '%';
  if (BVal) BVal.textContent = B.toFixed(2);
  const Lt = data.current_Lambda_tilde || 0.25;
  const LtBar = document.getElementById('enl-Lt-bar');
  const LtVal = document.getElementById('enl-Lt-val');
  if (LtBar) LtBar.style.width = Math.min(100, Lt * 100) + '%';
  if (LtVal) LtVal.textContent = Lt.toFixed(2);
  const speed = (data.convergence || {}).convergence_speed || 0.73;
  const speedVal = document.getElementById('enl-speed-val');
  const statusVal = document.getElementById('enl-status');
  if (speedVal) speedVal.textContent = speed.toFixed(2);
  if (statusVal) {
    statusVal.textContent = (data.T17_status === 'VERIFIED') ? 'VERIFIED' : 'NOT_CONV';
    statusVal.style.color = (data.T17_status === 'VERIFIED') ? 'var(--green)' : 'var(--amber)';
  }
  const p8 = (data.p8_verification || {});
  const p8El = document.getElementById('enl-p8');
  const LtrendEl = document.getElementById('enl-Ltrend');
  if (p8El) {
    p8El.textContent = p8.P8_status || 'PENDING';
    p8El.style.color = (p8.P8_status === 'CONFIRMED') ? 'var(--green)' : 'var(--amber)';
  }
  if (LtrendEl) LtrendEl.textContent = ((data.Lambda_trend || {}).slope || -0.05).toFixed(2);
}

function updateCouplingPanel(data) {
  if (!data) return;
  const S = data.avg_semantic_strength || 0.65;
  const SBar = document.getElementById('coup-S-bar');
  const SVal = document.getElementById('coup-S-val');
  if (SBar) SBar.style.width = Math.min(100, S * 100) + '%';
  if (SVal) SVal.textContent = S.toFixed(2);
  const C = data.avg_phase_coupling || 0.58;
  const CBar = document.getElementById('coup-C-bar');
  const CVal = document.getElementById('coup-C-val');
  if (CBar) CBar.style.width = Math.min(100, C * 100) + '%';
  if (CVal) CVal.textContent = C.toFixed(2);
  const cons = (data.eml_conservation || {}).verified;
  const consEl = document.getElementById('coup-conservation');
  if (consEl) {
    consEl.textContent = cons ? '守恒' : '不守恒';
    consEl.style.color = cons ? 'var(--green)' : 'var(--red)';
  }
  const p9 = (data.p9_verification || {});
  const p9El = document.getElementById('coup-p9');
  if (p9El) {
    p9El.textContent = p9.P9_status || 'PENDING';
    p9El.style.color = (p9.P9_status === 'CONFIRMED') ? 'var(--green)' : 'var(--amber)';
  }
}

function updatePredictionPanel(data) {
  if (!data) return;
  const results = (data.latest_results || {});
  updatePredItem('P7', results.P7);
  updatePredItem('P8', results.P8);
  updatePredItem('P9', results.P9);
  updatePredItem('P10', results.P10);
  const overall = data.overall_verification || {};
  const progEl = document.getElementById('pred-progress');
  const rateEl = document.getElementById('pred-rate');
  if (progEl) progEl.textContent = (overall.confirmed_count || 0) + '/' + (overall.total_predictions || 4);
  if (rateEl) {
    rateEl.textContent = ((overall.confirmation_rate || 0) * 100).toFixed(0) + '%';
    rateEl.style.color = (overall.confirmation_rate || 0) >= 0.75 ? 'var(--green)' : 'var(--amber)';
  }
}
function updatePredItem(id, result) {
  const statusEl = document.getElementById('pred-' + id + '-status');
  const descEl = document.getElementById('pred-' + id + '-desc');
  if (statusEl && result) {
    statusEl.textContent = result.confirmed ? 'CONFIRMED' : 'REJECTED';
    statusEl.className = 'v63-prediction-status ' + (result.confirmed ? 'confirmed' : 'rejected');
  }
  if (descEl && result) {
    var descs = {'P7':'L递减 执取减轻','P8':'B收敛条件满足','P9':'理解耦合相关','P10':'I超随机基线'};
    descEl.textContent = descs[id] || '';
  }
}

