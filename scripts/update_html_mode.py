#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新前端HTML文件，添加测试模式选择（快速模式12题/完整模式300题）"""

html_file = 'static/index_agi12.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换1: 更新模式选项卡
old_tabs = '''<div class="chen-test-mode-tabs">
            <div class="chen-mode-tab active" data-chen-mode="all">标准21题</div>
          </div>'''

new_tabs = '''<div class="chen-test-mode-tabs">
            <div class="chen-mode-tab active" data-chen-mode="quick">快速模式 (12题)</div>
            <div class="chen-mode-tab" data-chen-mode="full">完整模式 (300题)</div>
          </div>'''

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
    print("✓ 已更新模式选项卡")
else:
    print("⚠ 未找到模式选项卡，尝试手动定位...")
    # 使用更灵活的方法
    import re
    pattern = r'<div class="chen-test-mode-tabs">.*?</div>\s*</div>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print(f"  找到标签区域: {match.group()[:100]}...")
    else:
        print("  ✗ 未找到")

# 替换2: 更新测试说明文字
old_desc = '''<div style="font-size:11px;color:var(--txt3);margin-bottom:4px;font-weight:600">陈天桥认知能力测试</div>
              <div style="font-size:10px;color:var(--txt3);margin-bottom:8px">标准21题测试 · AI实时生成</div>
              <div style="font-size:9px;color:var(--txt3);margin-bottom:10px;line-height:1.5">
                数学推理 · 逻辑推理 · 物理直觉 · 认知心理 · AGI认知
              </div>'''

new_desc = '''<div style="font-size:11px;color:var(--txt3);margin-bottom:4px;font-weight:600" id="chen-test-title">陈天桥认知测试</div>
              <div style="font-size:10px;color:var(--txt3);margin-bottom:8px" id="chen-test-subtitle">选择测试模式后开始</div>
              <div style="font-size:9px;color:var(--txt3);margin-bottom:10px;line-height:1.5" id="chen-test-desc">
                自我意识 · 因果推理 · 抽象思维 · 时间感知 · 价值判断
              </div>
              <div style="margin-bottom:12px;font-size:10px;color:var(--txt2);display:none" id="chen-test-info">
                <span id="chen-mode-info">快速模式：12题，约5分钟</span>
              </div>'''

if old_desc in content:
    content = content.replace(old_desc, new_desc)
    print("✓ 已更新测试说明")
else:
    print("⚠ 未找到测试说明文字")

# 替换3: 更新按钮文字
old_btn = '''<button class="chen-btn chen-btn-start" onclick="try{console.log('[调试] 开始测试按钮被点击');CHEN_TEST.start();}catch(e){console.error('[错误]',e);alert('错误:'+e.message);}" style="padding:8px 24px">
              开始测试
            </button>'''

new_btn = '''<button class="chen-btn chen-btn-start" onclick="try{console.log('[调试] 开始测试按钮被点击');CHEN_TEST.start();}catch(e){console.error('[错误]',e);alert('错误:'+e.message);}" style="padding:8px 24px" id="chen-start-btn">
              选择模式并开始
            </button>'''

if old_btn in content:
    content = content.replace(old_btn, new_btn)
    print("✓ 已更新按钮")
else:
    print("⚠ 未找到按钮，尝试查找...")
    if 'chen-btn-start' in content:
        print("  ✓ 找到按钮元素")

# 保存更新后的内容
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✓ HTML文件已更新: {html_file}")
print("\n需要继续更新：")
print("  1. JavaScript中的CHEN_TEST对象，添加模式选择逻辑")
print("  2. 测试结果展示，区分快速模式和完整模式")
