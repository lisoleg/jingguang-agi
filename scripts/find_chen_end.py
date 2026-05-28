lines = open('C:/Users/1/WorkBuddy/2026-05-06-task-1/static/main_app.js', encoding='utf-8').readlines()
start = next(i for i, l in enumerate(lines) if l.strip().startswith('const CHEN_TEST = {'))
print(f'CHEN_TEST starts at line {start+1}')
depth = 0
end = None
for i in range(start, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth <= 0 and i > start:
        end = i
        break
print(f'CHEN_TEST ends at line {end+1}')
print('End line content:', lines[end].rstrip())
# Also print a few lines after to see context
print('--- Lines after end ---')
for j in range(end+1, min(end+5, len(lines))):
    print(f'{j+1}: {lines[j].rstrip()}')
