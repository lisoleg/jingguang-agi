import sys

# 读取原文件
original = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()

# 替换顶栏 + 主区域开头
old_topbar = '''  <!-- 顶栏 -->
  <div id="topbar">
    <div class="logo-wrap">
      <span class="logo">&#128302;</span>
      <span class="title">Taiyi-AGI (太乙因果机) 14.0</span>
      <span class="version-badge">170模块·141定理·八论合一·文明治理·可计算性·拓扑斯·缘起性空·复合体理学v3.12</span>
      <span class="theory-badge">一现象三视界</span>
    </div>
    <div class="dot-ok" id="status-dot"></div>
    <!-- 四象模态实时徽章 -->
    <span class="mode-topbadge mode-unknown" id="mode-topbadge" data-hint="当前对话的四象相干模态（刚性耦合/沸腾反抗/取经相干/熵增终局）">
      ◈ 模态感知中
    </span>
    <!-- 响应时间 -->
    <span class="resp-timer" id="resp-timer"></span>
    <span class="spacer"></span>
    <div class="doc-entry">
      <button class="btn-doc" onclick="openDesignDoc()" data-hint="查看Taiyi-AGI设计文档，了解系统架构">
        &#128196; 设计文档
      </button>
      <button class="btn-help" onclick="showHelp()" data-hint="查看使用说明，快速上手">
        &#10067; 使用说明
      </button>
    </div>
    <div class="header-actions">
      <div class="mode-toggle">
        <button class="mode-btn active" data-mode="chat">对话模式</button>
        <button class="mode-btn" data-mode="goal">Goal模式</button>
      </div>
      <button class="btn-reset" id="btn-reset">&#8634; 重置</button>
    </div>
  </div>

  <!-- 主区域 -->
  <div id="main">
    <!-- ═══════════════════════════════════════════════════════════════
         左侧：分析仪表盘（320px）
    ══════════════════════════════════════════════════════════════ -->'''

new_topbar = '''  <!-- ═══════════════════════════════════════════════════════════════
       全局浮层：本体导航 (Ontology Navigator) — L1本体层
       始终显示当前对话的"核心意图"Root Node
   ══════════════════════════════════════════════════════════════ -->
  <div id="ontology-nav">
    <span class="onto-label">◆ 本体导航：</span>
    <span class="onto-root" id="onto-root" title="点击回到根节点">未初始化</span>
    <span class="onto-spacer"></span>
    <button class="onto-toggle" onclick="toggleOntoNav()" title="收起本体导航">✕</button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       顶栏（STN模式精简版）
   ══════════════════════════════════════════════════════════════ -->
  <div id="topbar" class="stn-mode">
    <div class="logo-wrap">
      <span class="logo">🔮</span>
      <span class="title">Taiyi-AGI · STN</span>
      <span class="version-badge">v7.21</span>
      <span class="theory-badge">STN苏格拉底拓扑网络</span>
    </div>
    <div class="dot-ok" id="status-dot"></div>
    <span class="resp-timer" id="resp-timer"></span>
    <span class="spacer"></span>
    <!-- STN视图切换 -->
    <div class="header-actions" style="display:flex;gap:4px">
      <button class="stn-toggle-btn active" data-panel="forest" onclick="toggleSTNPanel('forest',this)" title="思维森林视图">🌲 森林</button>
      <button class="stn-toggle-btn" data-panel="dag" onclick="toggleSTNPanel('dag',this)" title="DAG关系图">🔗 DAG</button>
      <button class="stn-toggle-btn" data-panel="console" onclick="toggleSTNPanel('console',this)" title="流贯控制台">📟 控制台</button>
    </div>
    <button class="btn-reset" id="btn-reset" title="重置对话">↺ 重置</button>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════
       STN主体：左(森林) + 中(工作区) + 右(DAG)
   ══════════════════════════════════════════════════════════════ -->
  <div id="stn-main">
    <!-- 左侧：思维森林视图 (Forest View) — L3前物理层 -->
    <div id="forest-panel">
      <div id="forest-header">
        <span class="forest-title">🌲 思维森林</span>
        <div class="forest-actions">
          <button class="forest-btn" onclick="forestExpandAll()" title="展开全部">⊞</button>
          <button class="forest-btn" onclick="forestCollapseAll()" title="折叠全部">⊟</button>
          <button class="forest-btn" onclick="forestScrollToActive()" title="定位到活跃节点">⊙</button>
        </div>
      </div>
      <div style="padding:4px 8px;border-bottom:1px solid var(--bdr);flex-shrink:0">
        <input type="text" id="forest-search" placeholder="搜索节点..."
               style="width:100%;background:var(--bg3);border:1px solid var(--bdr);
                      border-radius:4px;color:var(--txt);font-size:9px;
                      padding:3px 6px;font-family:inherit;outline:none"
               oninput="forestFilter(this.value)">
      </div>
      <div id="stn-breadcrumb">
        <span class="stn-bc-item active" onclick="forestGoToRoot()">Root</span>
      </div>
      <div id="forest-view">
        <div class="forest-empty-state" id="forest-empty" style="text-align:center;padding:20px 10px;color:var(--txt3);font-size:10px">
          🌱 发送消息后此处显示<br>对话树状结构
        </div>
        <svg id="forest-links-svg"></svg>
        <div id="forest-tree"></div>
      </div>
      <div style="padding:4px 8px;border-top:1px solid var(--bdr);flex-shrink:0;
                   font-size:8px;color:var(--txt3);display:flex;justify-content:space-between">
        <span id="forest-stats">节点: 0</span>
        <span id="forest-depth">深度: 0</span>
      </div>
      <div id="forest-resizer"></div>
    </div>'''

if old_topbar in original:
    modified = original.replace(old_topbar, new_topbar, 1)
    print("OK: topbar + forest view replaced")
    print(f"Original len: {len(original)}")
    print(f"Modified len: {len(modified)}")
    # 只写到临时文件，不覆盖原文件
    open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12_stn_step1.html", 'w', encoding='utf-8').write(modified)
    print("Written to index_agi12_stn_step1.html")
else:
    print("ERROR: old_topbar not found")
    # 找差异
    idx = original.find('<div id="topbar">')
    if idx >= 0:
        print(f"Found <div id=topbar> at position {idx}")
        print(f"Context around: {repr(original[idx:idx+200])}")
    else:
        print("Could not find <div id=topbar> at all")
