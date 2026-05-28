import sys

html_old = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12_working.html", 'r', encoding='utf-8').read()

# 找 CSS 结束位置（</style> 之后到 <body> 之前的内容保留）
style_end = html_old.find('</style>')
body_start = html_old.find('<body>')
app_start = html_old.find('<div id="app">')
body_end = html_old.find('</body>')

assert style_end > 0, "style_end not found"
assert body_start > 0, "body_start not found"
assert app_start > 0, "app_start not found"
assert body_end > 0, "body_end not found"

# 三部分：head+CSS / body HTML / JS+结束
head_css = html_old[:style_end + len('</style>')]
body_html_old = html_old[app_start + len('<div id="app">'):body_end]
js_footer = html_old[body_end:]  # </body></html> 以及可能的中间JS

print(f"head_css len: {len(head_css)}")
print(f"body_html_old len: {len(body_html_old)}")
print(f"js_footer len: {len(js_footer)}")
print("OK: parts split successfully")

# 把 body_html_old 写文件供检查
open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\debug_body_old.html", 'w', encoding='utf-8').write(body_html_old)
print("debug_body_old.html written")
