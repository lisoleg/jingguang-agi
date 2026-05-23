content = open('static/index_agi12.html', 'r', encoding='utf-8').read()
marker = '// STN 苏格拉底拓扑网络'
pos = content.find(marker)
if pos == -1:
    print('NOT FOUND')
else:
    print(f'STN block starts at byte: {pos}')
    end = content.find('</script>', pos)
    print(f'</script> at byte: {end}')
    start = content.rfind('<script>', 0, pos)
    print(f'<script> at byte: {start}')
    print(f'Block length: {end + 9 - start}')
