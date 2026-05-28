import sys

# 读取原文件（含CSS）
original = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()

# 关键位置
STYLE_END = original.find('</style>') + len('</style>')
BODY_START = original.find('<body>')
APP_START = original.find('<div id="app">')
BODY_END = original.find('</body>')

print(f"STYLE_END: {STYLE_END}")
print(f"BODY_START: {BODY_START}")
print(f"APP_START: {APP_START}")
print(f"BODY_END: {BODY_END}")

# 三部分
head_css = original[:STYLE_END]   # head + CSS（含新增的STN CSS）
# body_inner = original[APP_START + len('<div id="app">'):BODY_END]
# tail = original[BODY_END:]

# 已分离的 JS 部分
js_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'r', encoding='utf-8').read()
print(f"\njs_part len: {len(js_part)}")
print(f"js_part starts with: {repr(js_part[:80])}")

# 已分离的 HTML 部分（原 body 结构）
html_old = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'r', encoding='utf-8').read()
print(f"html_old len: {len(html_old)}")
print(f"html_old starts with: {repr(html_old[:80])}")
print(f"html_old ends with: {repr(html_old[-80:])}")

# 验证
assert html_old.strip().endswith('</div>'), f"html_old should end with </div>"
assert js_part.strip().startswith('<script>'), f"js_part should start with <script>"

print("\nOK: all parts loaded and verified")
print("Now generating STN HTML structure...")
