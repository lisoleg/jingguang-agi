#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复陈天桥认知测试的前端bug：
1. 选项字母重复显示（如 A. A. 39）
2. 正确答案被判错（API题目answer为字符串"A"，但前端按数字处理）
3. 作文字数不足直接0分 → 改为按比例给分
"""

import re

def fix_index_agi12(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # ============================================================
    # Fix 1: 添加辅助函数到每个 <script> 块中（在 CHEN_TEST 之前）
    # ============================================================
    helper_code = (
        "// -- 辅助函数：去除选项前缀 --\n"
        "function stripOptPrefix(opt) {\n"
        "  return typeof opt === 'string' ? opt.replace(/^[A-E]\\.\\s*/, '') : opt;\n"
        "}\n"
        "// -- 辅助函数：获取数字格式的正确答案 --\n"
        "function getCorrectAnswer(q) {\n"
        "  if (q.correct_answer !== undefined) return Number(q.correct_answer);\n"
        "  if (typeof q.answer === 'number') return q.answer;\n"
        "  if (typeof q.answer === 'string' && /^[A-E]$/.test(q.answer)) return q.answer.charCodeAt(0) - 65;\n"
        "  return Number(q.answer);\n"
        "}\n"
        "// -- 辅助函数：计算问答题/作文得分比例 --\n"
        "function calcTextScoreRatio(userAns, minWords) {\n"
        "  if (!userAns || userAns.trim().length === 0) return 0;\n"
        "  return Math.min(1.0, userAns.trim().length / (minWords || 50));\n"
        "}\n\n"
    )
    
    if 'function stripOptPrefix(opt)' not in content:
        content = content.replace('const CHEN_TEST = {', helper_code + 'const CHEN_TEST = {')
        changes.append("已添加辅助函数 stripOptPrefix / getCorrectAnswer / calcTextScoreRatio")
    else:
        changes.append("辅助函数已存在，跳过")
    
    # ============================================================
    # Fix 2: 选项渲染去除前缀
    # ============================================================
    old_opt_text = '<span class="chen-opt-text">${opt}</span>'
    new_opt_text = '<span class="chen-opt-text">${stripOptPrefix(opt)}</span>'
    count = content.count(old_opt_text)
    if count > 0:
        content = content.replace(old_opt_text, new_opt_text)
        changes.append(f"已修复选项文本重复前缀 ({count} 处)")
    
    # ============================================================
    # Fix 3: 答案判定逻辑
    # ============================================================
    old_numcorrect = 'const numCorrect = Number(q.answer);'
    new_numcorrect = 'const numCorrect = getCorrectAnswer(q);'
    count = content.count(old_numcorrect)
    if count > 0:
        content = content.replace(old_numcorrect, new_numcorrect)
        changes.append(f"已修复 review() 答案判定 ({count} 处)")
    
    old_fallback = 'const fallback = Number(q.answer);'
    new_fallback = 'const fallback = getCorrectAnswer(q);'
    count = content.count(old_fallback)
    if count > 0:
        content = content.replace(old_fallback, new_fallback)
        changes.append(f"已修复 fallback 答案判定 ({count} 处)")
    
    old_correct_display = 'q.answer !== undefined ? String.fromCharCode(65 + q.answer)'
    new_correct_display = 'getCorrectAnswer(q) !== undefined ? String.fromCharCode(65 + getCorrectAnswer(q))'
    count = content.count(old_correct_display)
    if count > 0:
        content = content.replace(old_correct_display, new_correct_display)
        changes.append(f"已修复正确答案显示 ({count} 处)")
    
    old_highlight = "if (oi === q.answer) cls = 'color:var(--green);font-weight:600';"
    new_highlight = "if (oi === getCorrectAnswer(q)) cls = 'color:var(--green);font-weight:600';"
    count = content.count(old_highlight)
    if count > 0:
        content = content.replace(old_highlight, new_highlight)
        changes.append(f"已修复选项高亮逻辑 ({count} 处)")
    
    # ============================================================
    # Fix 4: 作文字数评分改为按比例
    # ============================================================
    old_text_correct = "isCorrect = userAns && userAns.trim().length >= minWords;"
    new_text_correct = "const scoreRatio = calcTextScoreRatio(userAns, minWords);\n        isCorrect = scoreRatio >= 1.0;"
    count = content.count(old_text_correct)
    if count > 0:
        content = content.replace(old_text_correct, new_text_correct)
        changes.append(f"已修复问答题字数判定为比例评分 ({count} 处)")
    
    old_result_msg = "${isCorrect ? '&#10004; 字数达标，得分' : '&#10006; 字数不足或未作答，未得分'}"
    new_result_msg = "${scoreRatio >= 1.0 ? '&#10004; 字数达标，满分' : (scoreRatio > 0 ? '&#9993; 字数不足，得 ' + Math.round(scoreRatio * 100) + '% 分' : '&#10006; 未作答，0分')}"
    count = content.count(old_result_msg)
    if count > 0:
        content = content.replace(old_result_msg, new_result_msg)
        changes.append(f"已修复结果显示文案 ({count} 处)")
    
    old_q_text = "<div class=\"chen-test-q-text\">${q.question || q.q || '题目加载失败'}</div>"
    new_q_text = (
        "<div class=\"chen-test-q-text\">${q.question || q.q || '题目加载失败'}</div>\n"
        "        ${(q.type === 'essay' || q.type === 'composition') ? '<div style=\"font-size:10px;color:var(--amber);margin-top:4px\">&#9998; 字数要求：至少 ' + (q.minWords || 50) + ' 字</div>' : ''}"
    )
    count = content.count(old_q_text)
    if count > 0:
        content = content.replace(old_q_text, new_q_text)
        changes.append(f"已在题目中显式标注字数要求 ({count} 处)")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        changes.append(f"文件已保存: {filepath}")
    else:
        changes.append(f"无变化: {filepath}")
    
    return changes


def fix_chen_test_mode_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    helper_code = (
        "// -- 辅助函数：去除选项前缀 --\n"
        "function stripOptPrefix(opt) {\n"
        "  return typeof opt === 'string' ? opt.replace(/^[A-E]\\.\\s*/, '') : opt;\n"
        "}\n\n"
    )
    
    if 'function stripOptPrefix(opt)' not in content:
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('//'):
                insert_idx = i
                break
        lines.insert(insert_idx, helper_code)
        content = '\n'.join(lines)
        changes.append("已添加辅助函数 stripOptPrefix")
    
    old_opt_text = '<span class="chen-opt-text">${opt}</span>'
    new_opt_text = '<span class="chen-opt-text">${stripOptPrefix(opt)}</span>'
    count = content.count(old_opt_text)
    if count > 0:
        content = content.replace(old_opt_text, new_opt_text)
        changes.append(f"已修复选项文本重复前缀 ({count} 处)")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        changes.append(f"文件已保存: {filepath}")
    else:
        changes.append(f"无变化: {filepath}")
    
    return changes


def fix_app_py(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    old_block = (
        "            # 确保correct_answer字段存在\n"
        "            if 'correct_answer' not in q and 'answer' in q:\n"
        "                if isinstance(q['answer'], str) and q['answer'] in ['A', 'B', 'C', 'D', 'E']:\n"
        "                    q['correct_answer'] = ord(q['answer']) - ord('A')\n"
        "                elif isinstance(q['answer'], int):\n"
        "                    q['correct_answer'] = q['answer']"
    )
    
    new_block = (
        "            # 确保correct_answer字段存在\n"
        "            if 'correct_answer' not in q and 'answer' in q:\n"
        "                if isinstance(q['answer'], str) and q['answer'] in ['A', 'B', 'C', 'D', 'E']:\n"
        "                    q['correct_answer'] = ord(q['answer']) - ord('A')\n"
        "                elif isinstance(q['answer'], int):\n"
        "                    q['correct_answer'] = q['answer']\n"
        "            # 同时统一 answer 字段为数字索引，避免前端兼容问题\n"
        "            if 'answer' in q and isinstance(q['answer'], str) and q['answer'] in ['A', 'B', 'C', 'D', 'E']:\n"
        "                q['answer'] = ord(q['answer']) - ord('A')"
    )
    
    count = content.count(old_block)
    if count > 0:
        content = content.replace(old_block, new_block)
        changes.append(f"已修复 app.py 答案字段统一 ({count} 处)")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        changes.append(f"文件已保存: {filepath}")
    else:
        changes.append(f"无变化: {filepath}")
    
    return changes


if __name__ == '__main__':
    print("=" * 60)
    print("修复陈天桥认知测试前端Bug")
    print("=" * 60)
    
    print("\n--- 1. 修复 static/index_agi12.html ---")
    changes = fix_index_agi12('static/index_agi12.html')
    for c in changes:
        print(f"  {c}")
    
    print("\n--- 2. 修复 static/chen_test_mode.js ---")
    changes = fix_chen_test_mode_js('static/chen_test_mode.js')
    for c in changes:
        print(f"  {c}")
    
    print("\n--- 3. 修复 app.py 后端字段 ---")
    changes = fix_app_py('app.py')
    for c in changes:
        print(f"  {c}")
    
    print("\n" + "=" * 60)
    print("修复完成")
    print("=" * 60)
