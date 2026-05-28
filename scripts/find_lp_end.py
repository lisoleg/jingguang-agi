import sys

content = open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12_working.html", 'r', encoding='utf-8').readlines()

# 找 left-panel 闭合行
lp_start = 2082  # 1-indexed
depth = 0
lp_end = None
for i in range(lp_start - 1, len(content)):
    line = content[i]
    depth += line.count('<div')
    depth -= line.count('</div>')
    if depth == 0 and i >= lp_start - 1:
        lp_end = i + 1  # 1-indexed
        break

print(f"left-panel closes at line: {lp_end}")
if lp_end:
    print(f"closing line: {content[lp_end-1].strip()[:100]}")
