import re

with open('static/index_agi12.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取所有内联JavaScript
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
all_code = '\n'.join(scripts)

# 查找函数定义
func_defs = set()

# 方式1: function name()
defs1 = re.findall(r'function\s+(\w+)\s*\(', all_code)
func_defs.update(defs1)

# 方式2: const name = function() 或 const name = () =>
defs2 = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:function|(?:\([^)]*\)|\w+)\s*=>)', all_code)
func_defs.update(defs2)

# 方式3: obj.method = function() - 方法名
defs3 = re.findall(r'\w+\.(\w+)\s*=\s*function\s*\(', all_code)
func_defs.update(defs3)

# 方式4: name() { 简写方法（匹配在对象中的方法定义）
defs4 = re.findall(r'[,{]\s*(\w+)\s*\([^)]*\)\s*\{', all_code)
func_defs.update(defs4)

# 查找函数调用（简单的name()模式）
calls = re.findall(r'\b([a-zA-Z_]\w*)\s*\(', all_code)

# 排除关键字和内置函数
keywords = {'if', 'for', 'while', 'switch', 'catch', 'typeof', 'return', 'throw', 'new', 'console', 'alert', 'confirm', 'prompt', 'Math', 'Date', 'JSON', 'Object', 'Array', 'String', 'Number', 'Boolean', 'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval', 'encodeURI', 'decodeURI', 'encodeURIComponent', 'decodeURIComponent', 'escape', 'unescape', 'eval', 'undefined', 'null', 'true', 'false', 'NaN', 'Infinity', 'Error', 'RegExp', 'Function', 'Symbol', 'Map', 'Set', 'WeakMap', 'WeakSet', 'Promise', 'Proxy', 'Reflect', 'Intl', 'window', 'document', 'navigator', 'location', 'history', 'screen', 'localStorage', 'sessionStorage', 'fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource', 'URL', 'Blob', 'File', 'FileReader', 'FormData', 'Headers', 'Request', 'Response', 'AbortController', 'Image', 'Audio', 'Video', 'd3', 'Vue', 'React', 'angular', 'jQuery'}

# 统计调用次数
call_counts = {}
for c in calls:
    if c not in keywords and c not in func_defs:
        call_counts[c] = call_counts.get(c, 0) + 1

# 过滤出可能有问题的高频调用（超过1次）
undefined_calls = [(name, count) for name, count in call_counts.items() if count > 1]
undefined_calls.sort(key=lambda x: x[1], reverse=True)

print(f'总共找到 {len(func_defs)} 个函数定义')
print(f'总共找到 {len(set(calls))} 个不同调用')

if undefined_calls:
    print('\n⚠️  可能未定义的高频函数调用（>1次）：')
    for name, count in undefined_calls[:40]:
        print(f'  {name} (调用 {count} 次)')
    print(f'\n共 {len(undefined_calls)} 个可疑调用')
else:
    print('\n✅ 所有高频函数调用都有定义')
