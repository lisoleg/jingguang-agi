import sys

# 读取原文件各部分
original = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html", 'r', encoding='utf-8').read()

# 找关键位置
style_end = original.find('</style>') + len('</style>')
body_start = original.find('<body>')
app_start = original.find('<div id="app">')
body_end = original.find('</body>')

print(f"style_end: {style_end}")
print(f"body_start: {body_start}")
print(f"app_start: {app_start}")
print(f"body_end: {body_end}")

# 策略：保留 head+CSS（到 </style> 为止）
# 替换 <body>...<div id="app"> 之间的内容（即 <body> 标签行）
# 替换 <div id="app"> 到 </body> 之间的内容为 STN 结构
# 保留 </body></html> 结尾

head_part = original[:style_end]  # 含CSS，到 </style> 为止
tail_part = original[body_end:]  # </body></html>

print(f"head_part len: {len(head_part)}")
print(f"tail_part len: {len(tail_part)}")
print("Ready to generate STN body...")

# 生成 STN body HTML
NEW_BODY = orig_body = original[style_end:body_end]
print(f"orig body len: {len(orig_body)}")
