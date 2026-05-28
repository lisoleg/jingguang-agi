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
# tail = original[BODY_END:]

# 找 <!-- 主区域 --> 的位置（2077行附近）
main_comment = original.find('<!-- 主区域 -->')
print(f"main_comment position: {main_comment}")

# 找 </div> 对应 #main 的闭合位置
main_start = original.find('<div id="main">')
print(f"main_start: {main_start}")

# 找 #main 对应的闭合 </div>
# 从 main_start 开始数 div 嵌套层级
depth = 0
main_end = None
for i in range(main_start, len(original)):
    if original[i:i+len('<div')] == '<div':
        # 简化：按行处理更可靠
        pass
    pass

print("Analysis done")
