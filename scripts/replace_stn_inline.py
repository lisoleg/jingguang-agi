import sys

filepath = 'static/index_agi12.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 位置已确认
script_start = 236976   # '<script>' 位置
script_end   = 546716   # '</script>' 位置 + len('</script>')

new_script_tag = '  <script src="stn_core.js"></script>\n'

new_content = content[:script_start] + new_script_tag + content[script_end:]

with open('static/index_agi12_stn_final.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

old_len = len(content)
new_len = len(new_content)
print(f'Old length: {old_len}')
print(f'New length: {new_len}')
print(f'Removed inline STN JS: {script_end - script_start} bytes')
print(f'Added external reference: {len(new_script_tag)} bytes')
print(f'Output: static/index_agi12_stn_final.html')
print('SUCCESS')
