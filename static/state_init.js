// ════════════════════════════════════════════════════════════════
// state_init.js — 全局 STATE 对象初始化
// 从 index_agi12.html (a77cc1b) 提取，供 chen_test_core.js 等模块共享
// ════════════════════════════════════════════════════════════════

const STATE = {
  session_id: 'agi12_' + Math.random().toString(36).slice(2,9),
  mode: 'chat',           // chat | goal
  nodes: [],
  links: [],
  selected_node: null,
  history: [],
  messages: [],           // 对话消息列表（陈天桥测试使用）
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
  // DAG视图数据 - 多线索支持
  dag_data: {
    threads: [],
    current_thread: null,
  },
  qa_counter: 0,
  thread_counter: 0,
  global_q_counter: 0,
  global_a_counter: 0,
  dagSvg: null,
  dagG: null,
  _req_start: 0,
  // M81: 记忆树引擎状态
  memory_tree: {
    total_chunks: 0,
    info_density: 0,
    layer1_count: 0,
    layer2_count: 0,
    layer3_count: 0,
    last_update: '\u2014'
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
    sync_interval: 20
  },
  // M84: 模型智能路由状态
  model_router: {
    task_type: 'unknown',
    selected_model: '\u2014',
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
