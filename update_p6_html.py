# -*- coding: utf-8 -*-
"""Update index_agi12.html to add P6 Einstein causality test UI"""
import re

with open('static/index_agi12.html', 'r', encoding='utf-8') as f:
    content = f.read()

updated = 0

# 1. Add P6 button after P5 button
old_btn = '''<button onclick="runMVE('p5')" style="font-size:9px;padding:2px 6px;border:1px solid var(--txt2);background:var(--panel-bg);color:var(--txt2);border-radius:3px;cursor:pointer;">P5</button>'''
new_btn = '''<button onclick="runMVE('p5')" style="font-size:9px;padding:2px 6px;border:1px solid var(--txt2);background:var(--panel-bg);color:var(--txt2);border-radius:3px;cursor:pointer;">P5</button>
          <button onclick="runMVE('p6')" style="font-size:9px;padding:2px 6px;border:1px solid #a78bfa;background:var(--panel-bg);color:#a78bfa;border-radius:3px;cursor:pointer;">P6</button>'''
if old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    updated += 1
    print('[1/4] Added P6 button')
else:
    # Try alternate match (may have different spacing)
    print('[1/4] WARNING: P5 button not found, skipping')

# 2. Add P6 row after P5 row in panel
old_row = '''        <div class="v77-row">
          <div class="v77-label">P5 可锚定</div>
          <div class="v77-badge" id="v721-p5" style="color:var(--txt3)">—</div>
          <div class="v77-label">总计</div>
          <div class="v77-badge" id="v721-total" style="color:var(--txt3)">—</div>
        </div>'''
new_row = '''        <div class="v77-row">
          <div class="v77-label">P5 可锚定</div>
          <div class="v77-badge" id="v721-p5" style="color:var(--txt3)">—</div>
          <div class="v77-label">P6 因果性</div>
          <div class="v77-badge" id="v721-p6" style="color:var(--txt3)">—</div>
        </div>
        <div class="v77-row">
          <div class="v77-label">总计</div>
          <div class="v77-badge" id="v721-total" style="color:var(--txt3)">—</div>
          <div class="v77-label">版本</div>
          <div class="v77-badge" id="v721-version" style="color:var(--txt3);font-size:8px;">v7.21</div>
        </div>'''
if old_row in content:
    content = content.replace(old_row, new_row, 1)
    updated += 1
    print('[2/4] Added P6 panel row + version badge')
else:
    print('[2/4] WARNING: P5 row not found, skipping')

# 3. Update JS allIds to include v721-p6
old_ids = "'v721-p1','v721-p2','v721-p3','v721-p4','v721-p5','v721-total'"
new_ids = "'v721-p1','v721-p2','v721-p3','v721-p4','v721-p5','v721-p6','v721-version','v721-total'"
if old_ids in content:
    content = content.replace(old_ids, new_ids, 1)
    updated += 1
    print('[3/4] Updated JS allIds (added v721-p6, v721-version)')
else:
    print('[3/4] WARNING: allIds not found, skipping')

# 4. Update _MVE_NAMES to include p6
old_names = "'p5': 'P5可锚定'"
new_names = """'p5': 'P5可锚定',
  'p6': 'P6因果性'"""
if old_names in content:
    content = content.replace(old_names, new_names, 1)
    updated += 1
    print('[4/4] Updated _MVE_NAMES (added p6)')
else:
    print('[4/4] WARNING: _MVE_NAMES p5 not found, skipping')

# 5. Update updateMVEAllResults to handle P6 and version
# In the results loop, change from ['P1','P2','P3','P4','P5'] to include P6
old_loop = "['P1','P2','P3','P4','P5'].forEach"
new_loop = "['P1','P2','P3','P4','P5','P6'].forEach"
if old_loop in content:
    content = content.replace(old_loop, new_loop)
    print('[5/5] Updated results loop to include P6')
    updated += 1
else:
    print('[5/5] WARNING: results loop not found')

print(f'\nTotal updates applied: {updated}')

with open('static/index_agi12.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('HTML file updated successfully')
