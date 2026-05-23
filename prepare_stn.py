import sys

# 读取各部件
head_css = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()
head_end = head_css.find('</style>') + len('</style>')

head_part = head_css[:head_end]  # 含CSS
# 注意：body 标签在 head_part 之外，需要单独处理

# 读取 JS 部分（已分离好的）
js_part = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'r', encoding='utf-8').read()

# 读取原 HTML 部分（含顶栏+三栏）
html_old = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'r', encoding='utf-8').read()

# 验证结构
assert html_old.strip().endswith('</div>'), f"html_old should end with </div>, got: {html_old.strip()[-30:]}"
assert js_part.strip().startswith('<script>'), f"js_part should start with <script>, got: {js_part.strip()[:30]}"

print(f"head_part ends at: {head_end}")
print(f"html_old len: {len(html_old)}")
print(f"js_part len: {len(js_part)}")
print("Structure OK - ready to generate new HTML")
