import re

with open('static/index_agi12.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 dashboard-content 的起始位置
start = content.find('id="dashboard-content"')
if start == -1:
    print('ERROR: dashboard-content not found')
else:
    print(f'dashboard-content start at position {start}')
    # 找到匹配的结束 </div>
    pos = start
    depth = 0
    in_target = False
    
    while pos < len(content):
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        
        if next_open == -1 and next_close == -1:
            break
        
        if next_open != -1 and (next_close == -1 or next_open < next_close):
            # 这是一个 <div> 标签（不是 </div>）
            if not in_target:
                in_target = True
                depth = 0
            depth += 1
            pos = next_open + 4
        elif next_close != -1:
            if in_target:
                depth -= 1
                if depth == 0:
                    end = next_close + 6
                    print(f'dashboard-content ends at position {end}')
                    print(f'Total length: {end - start} chars')
                    # 显示结束位置前后100字符
                    context_start = max(0, end - 100)
                    context_end = min(len(content), end + 50)
                    print('--- Context around end ---')
                    print(repr(content[context_start:context_end]))
                    break
            pos = next_close + 6
    else:
        print('ERROR: dashboard-content not properly closed!')
        print(f'Reached end of file, current depth={depth}')
