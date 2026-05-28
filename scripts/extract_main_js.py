import os

src = r'C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12_working.html'
dst = r'C:\Users\1\WorkBuddy\2026-05-06-task-1\static\main_app.js'

with open(src, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# inline JS: line 4814 (<script>) to line 12858 (</script>)
# 提取 4815..12857 (0-indexed 4814..12857), 跳过 <script> 和 </script> 标签本身
js_lines = lines[4814:12858]

# 头部注释
header = '// main_app.js - 从 index_agi12_working.html 提取的主应用 JS\n// 包含: handleSendBtn / handleGoalBtn / renderHistory / addMsg 等所有主对话逻辑\n\n'

with open(dst, 'w', encoding='utf-8') as f:
    f.write(header)
    f.writelines(js_lines)

print(f'提取完成，写入 {len(js_lines)} 行到 {dst}')
print(f'文件大小: {os.path.getsize(dst)} bytes')
