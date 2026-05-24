lines = open('C:/Users/1/WorkBuddy/2026-05-06-task-1/static/main_app.js', encoding='utf-8').readlines()
# Delete lines 3349-5027 (0-indexed: 3348-5026)
new_lines = lines[:3348] + lines[5027:]
open('C:/Users/1/WorkBuddy/2026-05-06-task-1/static/main_app.js', 'w', encoding='utf-8').writelines(new_lines)
print(f'Done. Original: {len(lines)} lines, New: {len(new_lines)} lines, Removed: {len(lines)-len(new_lines)} lines')
# Verify no more CHEN_TEST const declaration
chen_decls = [(i+1, l.rstrip()) for i, l in enumerate(new_lines) if l.strip().startswith('const CHEN_TEST')]
print(f'CHEN_TEST const declarations remaining: {chen_decls}')
