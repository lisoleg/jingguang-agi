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

# 三部分：
# 1. head + CSS（到 </style> 为止）— 已经包含新的STN CSS
head_css = original[:STYLE_END]
# 2. JS函数（从第一个 <script> 开始，到 </body> 之前）
#    实际上 JS 在 <body> 内部，在 HTML 结构之后
#    我们需要找到 HTML 结构结束、JS 开始的位置
#    策略：找到 </div> 之后紧跟的 <script> 标签
# 实际上更简单：直接找到原文件中 <script> 标签的位置
# 但注意：原文件有多个 <script> 标签（D3.js CDN是第一个）
# 找 "const appState" 或者 "function" 或者 "{ " 的 JS 代码开始位置
# 简单策略：找到 debug_html_only.html 的末尾（即HTML结构结束位置）
# 我们之前已经分离好了：debug_html_only.html = 147042 bytes, debug_js_only.js = 310580 bytes

print("\nNow building new file...")

# 读取已分离的 HTML 部分和 JS 部分
html_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'r', encoding='utf-8').read()
js_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'r', encoding='utf-8').read()

print(f"html_part len: {len(html_part)}")
print(f"js_part len: {len(js_part)}")

# 验证
assert html_part.strip().endswith('</div>'), f"html_part should end with </div>, got: {html_part.strip()[-50:]}"
assert js_part.strip().startswith('<script>'), f"js_part should start with <script>, got: {js_part.strip()[:50]}"

print("Validation OK")
