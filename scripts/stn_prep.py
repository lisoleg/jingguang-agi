import sys

# 读取原文件
orig = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()

# 关键位置
STYLE_END = orig.find('</style>') + len('</style>')
BODY_START = orig.find('<body>')
APP_START = orig.find('<div id="app">')
BODY_END = orig.find('</body>')

print(f"STYLE_END: {STYLE_END}")
print(f"BODY_START: {BODY_START}")
print(f"APP_START: {APP_START}")
print(f"BODY_END: {BODY_END}")

# 三部分
head_css = orig[:STYLE_END]       # head + CSS（含新增的STN CSS）
body_html = orig[APP_START + len('<div id="app">'):BODY_END]  # 旧body HTML
tail = orig[BODY_END:]            # </body></html>

# 找 body_html 中 JS 开始的位置（第一个 <script> 标签之后，实际是 <script src= 不算，要的是 inline JS）
# 我们找 "const appState" 或者 "function " 或者 "{ " 的实际位置
# 更简单：利用之前已经发现的位置
# 已知：debug_html_only.html 长度 = 147042，debug_js_only.js 长度 = 310580
# 所以 body_html 的前 147042 字节是 HTML，后面是 JS
# 验证：
html_end = 147042
js_part = body_html[html_end:]
html_part = body_html[:html_end]

print(f"\nbody_html total len: {len(body_html)}")
print(f"html_part len (0~{html_end}): {len(html_part)}")
print(f"js_part len ({html_end}~): {len(js_part)}")
print(f"js_part starts with: {repr(js_part[:80])}")

# 验证 js_part 确实以 <script> 开头
assert js_part.strip().startswith('<script>'), f"Expected <script>, got: {js_part.strip()[:50]}"

print("\nOK: HTML/JS split verified, ready to substitute HTML part")
