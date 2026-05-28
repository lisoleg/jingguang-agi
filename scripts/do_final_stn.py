import sys

# 读取原文件
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
# tail = original[BODY_END:]   # </body></html>

# 已分离的 HTML 和 JS
html_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'r', encoding='utf-8').read()
js_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'r', encoding='utf-8').read()

print(f"\nhead_css len: {len(head_css)}")
print(f"html_part len: {len(html_part)}")
print(f"js_part len: {len(js_part)}")

# 验证
assert html_part.strip().endswith('</div>'), f"html_part should end with </div>"
assert js_part.strip().startswith('<script>'), f"js_part should start with <script>"

print("\nAll parts loaded and verified!")
print("Ready to generate STN HTML and write final file.")
