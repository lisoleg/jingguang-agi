import sys

# 读取原文件（含CSS和新加的STN CSS）
original = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()

# 关键位置
STYLE_END = original.find('</style>') + len('</style>')   # 86446
BODY_START = original.find('<body>')                      # 86455
APP_START = original.find('<div id="app">')              # 86462
BODY_END = original.find('</body>')                     # 544098

print(f"STYLE_END: {STYLE_END}")
print(f"BODY_START: {BODY_START}")
print(f"APP_START: {APP_START}")
print(f"BODY_END: {BODY_END}")

assert STYLE_END > 0 and BODY_START > 0 and APP_START > 0 and BODY_END > 0

# 三部分
head_css = original[:STYLE_END]   # head + CSS（含我们新加的STN CSS）
# body_inner = original[APP_START + len('<div id="app">'):BODY_END]
# tail = original[BODY_END:]

# 读取已分离的 JS 部分（debug_js_only.js = 310580 bytes）
js_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'r', encoding='utf-8').read()
print(f"\njs_part len: {len(js_part)}")
print(f"js_part starts with: {repr(js_part[:60])}")

# 读取原 HTML 结构部分（debug_html_only.html = 147042 bytes）
html_old = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'r', encoding='utf-8').read()
print(f"html_old len: {len(html_old)}")
print(f"html_old starts with: {repr(html_old[:80])}")
print(f"html_old ends with: {repr(html_old[-80:])}")

print("\nOK: all parts loaded, ready to generate STN HTML...")
