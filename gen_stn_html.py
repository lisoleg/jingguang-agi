import sys

# 读取原文件
filepath = r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 定位标记
app_marker = '<div id="app">'
body_marker = '</body>'

app_pos = content.find(app_marker)
body_pos = content.find(body_marker)

if app_pos == -1:
    print("ERROR: app marker not found")
    sys.exit(1)
if body_pos == -1:
    print("ERROR: body marker not found")
    sys.exit(1)

prefix = content[:app_pos + len(app_marker)]
suffix = content[body_pos:]

print(f"prefix end: {app_pos + len(app_marker)}")
print(f"body start: {body_pos}")
print(f"total len: {len(content)}")
print("Markers found OK")
