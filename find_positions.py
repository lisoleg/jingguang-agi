import os

filepath = r"C:\Users\1\WorkBuddy\2026-05-06-task-1\static\index_agi12.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

app_start = content.find('<div id="app">')
body_end = content.find('</body>')

if app_start == -1:
    print("ERROR: <div id='app'> not found")
    exit(1)
if body_end == -1:
    print("ERROR: </body> not found")
    exit(1)

marker = '<div id="app">'
prefix_end = app_start + len(marker)

print(f"prefix length: {prefix_end}")
print(f"body_end at: {body_end}")
print(f"inner length: {body_end - prefix_end}")
print("SUCCESS: positions found, ready for replacement")
