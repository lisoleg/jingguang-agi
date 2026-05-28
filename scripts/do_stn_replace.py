import sys

# 读取原文件
filepath = r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html"
outpath = r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12_stn.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

app_marker = '<div id="app">'
body_marker = '</body>'

app_pos = content.find(app_marker)
body_pos = content.find(body_marker)

assert app_pos != -1, "app marker not found"
assert body_pos != -1, "body marker not found"

prefix = content[:app_pos + len(app_marker)]
suffix = content[body_pos:]

# STN 主体HTML（替换 <div id="app"> 和 </body> 之间的所有内容）
NEW_INNER = '''  <!-- ══════════════════════════════════════════════════════════
       全局浮层：本体导航 (Ontology Navigator) — L1本体层
       始终显示当前对话的"核心意图"Root Node
   ══════════════════════════════════════════════════════════ -->
  <div id="ontology-nav">
    <span class="onto-label">◆ 本体导航：</span>
    <span class="onto-root" id="onto-root" title="点击回到根节点">未初始化</span>
    <span class="onto-spacer"></span>
    <button class="onto-toggle" onclick="toggleOntoNav()" title="收起本体导航">✕</button>
  </div>

  <!-- ══════════════════════════════════════════════════════════
       顶栏（STN模式精简版）
   ══════════════════════════════════════════════════════════ -->
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
      <button class="stn-toggle-btn" data-panel="console" onclick="toggleSTNPanel('console',this)" title="流贯控制台">�底控制台</button>
    </div>
    <button class="btn-reset" id="btn-reset" title="重置对话">↺ 重置</button>
  </div>

  <!-- ══════════════════════════════════════════════════════════
       STN主体：左(森林) + 中(工作区) + 右(DAG)
   ══════════════════════════════════════════════════════════ -->
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
      <!-- 搜索过滤 -->
      <div style="padding:4px 8px;border-bottom:1px solid var(--bdr);flex-shrink:0">
        <input type="text" id="forest-search" placeholder="搜索节点..."
               style="width:100%;background:var(--bg3);border:1px solid var(--bdr);
                      border-radius:4px;color:var(--txt);font-size:9px;
                      padding:3px 6px;font-family:inherit;outline:none"
               oninput="forestFilter(this.value)">
      </div>
      <!-- 面包屑导航 -->
      <div id="stn-breadcrumb">
        <span class="stn-bc-item active" onclick="forestGoToRoot()">Root</span>
      </div>
      <!-- 森林树容器 -->
      <div id="forest-view">
        <div class="forest-empty-state" id="forest-empty" style="text-align:center;padding:20px 10px;color:var(--txt3);font-size:10px">
          🌱 发送消息后此处显示<br>对话树状结构
        </div>
        <svg id="forest-links-svg"></svg>
        <div id="forest-tree"></div>
      </div>
      <!-- 森林底部统计 -->
      <div style="padding:4px 8px;border-top:1px solid var(--bdr);flex-shrink:0;
                   font-size:8px;color:var(--txt3);display:flex;justify-content:space-between">
        <span id="forest-stats">节点: 0</span>
        <span id="forest-depth">深度: 0</span>
      </div>
      <!-- 拖拽调整宽度 -->
      <div id="forest-resizer"></div>
    </div>

    <!-- 中间：语境工作区 (Context Workspace) — L4认知主体层 -->
    <div id="workspace-panel">
      <div id="workspace-header">
        <span class="ws-breadcrumb" id="ws-breadcrumb">
          <span class="ws">Root</span>
        </span>
        <span class="spacer"></span>
        <span class="ws-badge" id="ws-mode-badge">对话模式</span>
      </div>
      <!-- 工作区内容：对话历史 -->
      <div id="workspace-content">
        <div id="ws-empty-state" style="text-align:center;padding:40px 20px;color:var(--txt3);font-size:12px">
          <div style="font-size:36px;margin-bottom:12px;opacity:.4">💬</div>
          开始对话，STN将记录<br>完整的思维拓扑结构
        </div>
        <div id="ws-messages"></div>
      </div>
      <!-- 工作区输入区 -->
      <div id="workspace-input-area">
        <div id="ws-mode-tabs" style="display:flex;gap:3px;margin-bottom:4px">
          <button class="input-tab active" data-mode="chat" onclick="wsSwitchMode('chat',this)">💬 对话</button>
          <button class="input-tab" data-mode="goal" onclick="wsSwitchMode('goal',this)">🎯 Goal</button>
          <button class="input-tab" data-mode="fork" onclick="wsSwitchMode('fork',this)">⑂ 分叉</button>
        </div>
        <textarea id="workspace-input" placeholder="输入消息... (Shift+Enter 换行，Enter 发送)"
                  onkeydown="wsInputKeyDown(event)"></textarea>
        <div id="workspace-input-actions">
          <span class="ws-input-hint" id="ws-input-hint">Enter 发送 · Shift+Enter 换行</span>
          <button class="ws-send-btn" id="ws-send-btn" onclick="wsSendMessage()">发送 ➤</button>
        </div>
        <!-- 分叉模式提示 -->
        <div id="ws-fork-hint" style="display:none;padding:4px 8px;background:rgba(168,85,247,.1);
                    border:1px solid rgba(168,85,247,.3);border-radius:4px;
                    font-size:9px;color:#a855f7;margin-top:4px">
          ✦ 分叉模式：输入将从选中节点创建新对话分支
        </div>
      </div>
    </div>

    <!-- 右侧：DAG关系图面板（可隐藏） -->
    <div id="dag-panel">
      <div class="right-header">
        <span class="right-icon">🔗</span>
        <span class="right-title">DAG 关系图</span>
        <span class="rel-badge" id="dag-count">0</span>
        <span class="spacer"></span>
        <button class="btn-dag-fullscreen" onclick="toggleDAGFullscreen()" title="全屏DAG">⛶</button>
      </div>
      <div id="dag-container">
        <svg id="dag-svg"></svg>
        <div class="dag-empty-state" id="dag-empty-state">
          <div class="dag-empty-icon">🔗</div>
          <div class="dag-empty-text">DAG关系图将在此显示</div>
        </div>
      </div>
      <div id="dag-footer">
        <div class="dag-stat"><div class="dag-dot dot-q"></div><span>Q: <span id="dag-q-count">0</span></span></div>
        <div class="dag-stat"><div class="dag-dot dot-a"></div><span>A: <span id="dag-a-count">0</span></span></div>
        <div class="dag-stat"><div class="dag-dot dot-follow"></div><span>分支: <span id="dag-fork-count">0</span></span></div>
      </div>
      <!-- 拖拽调整宽度 -->
      <div id="dag-resizer"></div>
    </div>

  </div><!-- /#stn-main -->

  <!-- ══════════════════════════════════════════════════════════
       底部：流贯控制台 (Ftel Console) — L2投射生成层
   ══════════════════════════════════════════════════════════ -->
  <div id="ftel-console">
    <div class="ftel-section" title="上下文进度（已用/总容量）">
      <span class="ftel-label">CTX</span>
      <div class="ftel-progress">
        <div class="ftel-progress-fill" id="ftel-ctx-fill" style="width:0%"></div>
      </div>
      <span class="ftel-entropy-val" id="ftel-ctx-val">0%</span>
    </div>
    <div class="ftel-section" title="系统熵值（越低越稳定）">
      <span class="ftel-label">S</span>
      <div class="ftel-entropy-track">
        <div class="ftel-entropy-fill" id="ftel-entropy-fill" style="width:20%"></div>
      </div>
      <span class="ftel-entropy-val" id="ftel-entropy-val">0.20</span>
    </div>
    <div class="console-btns">
      <button class="console-btn" onclick="ftelSummarize()" title="一键总结当前对话">📝 总结</button>
      <button class="console-btn" onclick="ftelDebate()" title="发起诘辩（ELENCHUS）">⚔️ 诘辩</button>
      <button class="console-btn" onclick="ftelIntegrate()" title="整合当前对话为知识">🔥 整合</button>
    </div>
    <input type="text" class="console-cmd-input" id="ftel-cmd-input"
           placeholder="输入命令：/fork /summarize /debate /integrate /help"
           onkeydown="ftelCmdKeyDown(event)">
    <span class="console-status" id="ftel-status">就绪</span>
  </div>

'''

new_content = prefix + NEW_INNER + suffix

with open(outpath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"OK: written to {outpath}")
print(f"Original len: {len(content)}")
print(f"New len: {len(new_content)}")
