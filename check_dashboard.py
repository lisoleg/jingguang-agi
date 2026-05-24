# 读取文件，找到 dashboard-content 的结束位置
with open('static/index_agi12.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_dashboard = False
depth = 0
start_line = -1
end_line = -1

for i, line in enumerate(lines, 1):
    stripped = line.strip()
    
    # 找到 dashboard-content 开始
    if not in_dashboard and 'id="dashboard-content"' in line and '<div' in line:
        in_dashboard = True
        start_line = i
        depth = 0
        print(f"Found dashboard-content at line {i}")
        continue
    
    if in_dashboard:
        import re
        # 移除注释避免误判
        clean_line = re.sub(r'<!--.*?-->', '', line)
        # 计算 <div> 和 </div> 的数量差
        opens = len(re.findall(r'<div[\s>]', clean_line))
        closes = clean_line.count('</div>')
        depth += opens - closes
        
        # 调试输出（前30行）
        if i - start_line <= 30:
            print(f"  Line {i}: depth={depth}, opens={opens}, closes={closes}")
            print(f"    {stripped[:70]}")
        
        # 如果深度归零，说明找到了 dashboard-content 的结束 </div>
        if depth <= 0 and i > start_line:
            end_line = i
            print(f"\nFound end at line {i}")
            print(f"Total lines in dashboard-content: {i - start_line + 1}")
            # 显示结束位置上下文
            print(f"\n--- Context around end ---")
            for j in range(max(0, i-5), min(len(lines), i+2)):
                print(f"  Line {j+1}: {lines[j].rstrip()[:100]}")
            break

if end_line == -1:
    print(f"\nERROR: dashboard-content not properly closed!")
    print(f"Reached end of file, current depth={depth}")
