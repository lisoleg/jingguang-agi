import sys

# 读取各部分
head_css = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()

# 从之前 split 的结果里取
head_css = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_body_old.html", 'r', encoding='utf-8').read()
html_part = head_css  # 这个文件实际就是 body_html_old
print(f"debug_body_old.html len: {len(html_part)}")

# 找 <script> 位置（JS开始）
script_pos = html_part.find('<script>')
print(f"First script tag at: {script_pos}")

# 分成 HTML 部分和 JS 部分
html_only = html_part[:script_pos]
js_only = html_part[script_pos:]
print(f"HTML only len: {len(html_only)}")
print(f"JS only len: {len(js_only)}")

# 写文件供后续使用
open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_html_only.html", 'w', encoding='utf-8').write(html_only)
open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_js_only.js", 'w', encoding='utf-8').write(js_only)
print("Split OK: debug_html_only.html + debug_js_only.js")
