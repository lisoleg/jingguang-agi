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

# 策略：
# 1. head_css = original[:STYLE_END]  (含CSS，我们新加的STN CSS已经在了）
# 2. 替换 APP_START+len ~ BODY_END 之间的 HTML 为 STN 结构
# 3. tail = original[BODY_END:]
# 但注意：JS函数在 <body> 里面、HTML结构之后
# 实际上 JS 函数在 debug_js_only.js 里（310580 bytes）
# 我们直接拼接：head_css + STN_html + js_part + tail

# 验证
assert STYLE_END > 0
assert BODY_START > 0  
assert APP_START > 0
assert BODY_END > 0

print("\nAll positions found OK")
print(f"File size: {len(original)}")

# 读取已分离的 JS 部分
js_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'r', encoding='utf-8').read()
print(f"js_part length: {len(js_part)}")
print(f"js_part starts with: {repr(js_part[:60])}")

# 读取已分离的 HTML 部分（我们要替换它）
html_old = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'r', encoding='utf-8').read()
print(f"html_old length: {len(html_old)}")
print(f"html_old starts with: {repr(html_old[:80])}")
print(f"html_old ends with: {repr(html_old[-80:])}")

print("\nReady to generate STN HTML and write final file.")
