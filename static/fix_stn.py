#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix STN layout issues in index_agi12.html
"""
import re

with open('index_agi12.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === Fix 1: Remove duplicate ftel-console inside center-panel (lines 4677-4698) ===
# The inner ftel-console is inside center-panel, we keep only the body-level one
old_inner_console = '''      <!-- STN Phase 3: 流贯控制台 -->
      <div id="ftel-console">
        <div class="console-entropy">
          <span style="font-size:10px;color:var(--txt2)">H</span>
          <div style="position:relative;display:inline-block">
            <div class="console-entropy-track">
              <div class="console-entropy-fill" id="console-entropy-fill" style="width:30%"></div>
            </div>
            <!-- S_threshold 阈值标记（推论3.1.1临界点） -->
            <div id="console-threshold-marker" style="position:absolute;left:50%;top:-3px;width:1px;height:12px;background:var(--amber);opacity:.7" title="S_threshold: 信息熵临界阈值"></div>
          </div>
          <span class="console-entropy-val" id="console-entropy-val">0.30</span>
        </div>
        <div class="console-btns">
          <button class="console-btn" onclick="handleConsoleCmd('summarize')" title="对当前对话路径自动摘要">&#128220; 摘要</button>
          <button class="console-btn" onclick="handleConsoleCmd('debate')" title="对当前问题启动诘辩模式">&#9876; 诘辩</button>
          <button class="console-btn" onclick="handleConsoleCmd('integrate')" title="整合多版本答案">&#128259; 整合</button>
        </div>
        <input type="text" class="console-cmd-input" id="console-cmd-input"
               placeholder="/fork Q3  |  /summarize  |  /debate  |  /integrate  |  /help"
               onkeydown="if(event.key==='Enter'){handleConsoleCmdInput(this.value);this.value='';}">
        <span class="console-status" id="console-status">就绪</span>
      </div>'''

if old_inner_console in content:
    content = content.replace(old_inner_console, '')
    print("✅ Fix 1: Removed duplicate inner ftel-console")
else:
    print("⚠️ Fix 1: Inner ftel-console pattern not found exactly")

# === Fix 2: Fix stn_core.js path ===
content = content.replace(
    '<script src="stn_core.js"></script>',
    '<script src="/static/stn_core.js"></script>'
)
print("✅ Fix 2: Fixed stn_core.js path to /static/stn_core.js")

# === Fix 3: Remove duplicate inline STN JS block (lines 4916-5368) ===
# Find and remove the inline <script> block that duplicates stn_core.js
inline_js_start = content.find('  <script>\n  // ═══════════════════════════════════════════════════════════════\n  //  STN 苏格拉底拓扑网络')
if inline_js_start != -1:
    # Find the matching </script>
    inline_js_end = content.find('</script>', inline_js_start)
    if inline_js_end != -1:
        inline_js_end += len('</script>')
        content = content[:inline_js_start] + content[inline_js_end:]
        print("✅ Fix 3: Removed duplicate inline STN JS block")
    else:
        print("⚠️ Fix 3: Could not find end of inline JS block")
else:
    print("⚠️ Fix 3: Inline JS block not found")

# === Fix 4: Fix right-panel missing closing tag ===
# The right-panel (id="right-panel") starts at line 4733 but never closes before right-column closes
# We need to add </div> for right-panel before </div> for right-column
# Find: relation-map-panel closing, then right-column closing
old_right_end = '''        </div>
      </div>
    </div>
  </div>
  
  <!-- 帮助弹窗 -->'''
new_right_end = '''        </div>
      </div>
      </div>  <!-- /right-panel -->
    </div>  <!-- /right-column -->
  </div>  <!-- /main -->

  <!-- 帮助弹窗 -->'''

if old_right_end in content:
    content = content.replace(old_right_end, new_right_end)
    print("✅ Fix 4: Fixed right-panel and right-column closing tags")
else:
    print("⚠️ Fix 4: right-panel end pattern not found")

# === Fix 5: Add clear labels to STN panels ===
# Add label to ontology-nav
old_onto = '''  <div id="ontology-nav">
    <span class="onto-label">◆ 本体导航：</span>'''
new_onto = '''  <!-- ═══════════════════════════════════════════════════════════════
       L1 本体导航 (Ontology Navigator) — 始终显示核心意图
  ════════════════════════════════════════════════════════════════ -->
  <div id="ontology-nav">
    <span class="onto-label">◆ 本体导航 [L1]：</span>'''

if old_onto in content:
    content = content.replace(old_onto, new_onto)
    print("✅ Fix 5a: Added L1 label to ontology-nav")
else:
    print("⚠️ Fix 5a: ontology-nav pattern not found")

# Add label to ftel-console
old_ftel = '''  <!-- ═══════════════════════════════════════════════════════════════
       底部：流贯控制台 (Ftel Console) — L2投射生成层
   ════════════════════════════════════════════════════════════════ -->
  <div id="ftel-console">'''
new_ftel = '''  <!-- ═══════════════════════════════════════════════════════════════
       L2 流贯控制台 (Ftel Console) — 投射生成层
  ════════════════════════════════════════════════════════════════ -->
  <div id="ftel-console" data-panel-label="L2 流贯控制台">'''

if old_ftel in content:
    content = content.replace(old_ftel, new_ftel)
    print("✅ Fix 5b: Added L2 label to ftel-console")
else:
    print("⚠️ Fix 5b: ftel-console pattern not found")

# Add label to forest-view-panel
old_forest = '<div id="forest-view-panel" style="display:none;flex-direction:column;height:100%;overflow:hidden">'
new_forest = '<div id="forest-view-panel" style="display:none;flex-direction:column;height:100%;overflow:hidden" data-panel-label="L3 思维森林">'

if old_forest in content:
    content = content.replace(old_forest, new_forest)
    print("✅ Fix 5c: Added L3 label to forest-view-panel")
else:
    print("⚠️ Fix 5c: forest-view-panel pattern not found")

# Add label to center-panel
old_center = '<div id="center-panel">'
new_center = '<div id="center-panel" data-panel-label="L4 语境工作区">'

# Only replace the first occurrence (the real center-panel)
if old_center in content:
    content = content.replace(old_center, new_center, 1)
    print("✅ Fix 5d: Added L4 label to center-panel")
else:
    print("⚠️ Fix 5d: center-panel pattern not found")

# Add label to right-panel (DAG)
old_dag = '<div id="right-panel" data-hint="对话关系图：展示多线索问答结构。点击节点可跳转到对应对话，线条颜色区分话题">'
new_dag = '<div id="right-panel" data-hint="对话关系图：展示多线索问答结构。点击节点可跳转到对应对话，线条颜色区分话题" data-panel-label="DAG关系图">'

if old_dag in content:
    content = content.replace(old_dag, new_dag)
    print("✅ Fix 5e: Added DAG label to right-panel")
else:
    print("⚠️ Fix 5e: right-panel pattern not found")

# === Fix 6: Ensure input textarea is visible ===
# The input area uses id="main-input2" but CSS targets #main-input
# Add CSS to handle both
old_css_end = '</style>'
new_css_end = '''/* STN Fix: Ensure input is visible */
#main-input2, #goal-input2 {
  width: 100%;
  min-height: 60px;
  background: var(--bg3);
  border: 1px solid var(--bdr);
  border-radius: 8px;
  color: var(--txt);
  padding: 10px 12px;
  font-family: inherit;
  font-size: 13px;
  resize: vertical;
  outline: none;
}
#main-input2:focus, #goal-input2:focus {
  border-color: var(--acc);
}

/* STN Panel Labels */
[data-panel-label]::before {
  content: attr(data-panel-label);
  position: absolute;
  top: 2px;
  right: 6px;
  font-size: 9px;
  color: var(--txt3);
  background: rgba(0,0,0,0.5);
  padding: 1px 4px;
  border-radius: 3px;
  pointer-events: none;
  z-index: 10;
}
#center-panel[data-panel-label], #right-panel[data-panel-label] {
  position: relative;
}
</style>'''

if old_css_end in content:
    content = content.replace(old_css_end, new_css_end)
    print("✅ Fix 6: Added input visibility CSS and panel labels")
else:
    print("⚠️ Fix 6: </style> tag not found")

# Write back
with open('index_agi12.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All fixes applied! File saved.")
