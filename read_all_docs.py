#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量读取12个文档的核心内容并输出摘要"""

import os
import sys
import json

from docx import Document
import fitz

DOWNLOADS = r'C:\Users\1\Downloads'

# 12个文件
FILES = [
    ('弹簧虫：多主体 △ 场耦合、能量循环与鲁棒动态平衡.docx', 'docx'),
    ('面向中国场景的 DIKWP 开源系统白皮书.pdf', 'pdf'),
    ('\u65f6\u95f4\u57fa\u6001\u4e0e\u7a7a\u95f4\u6fc0\u53d1\uff1a\u57fa\u4e8e\u201c\u4e00\u73b0\u8c61\u4e09\u89c6\u754c\u201d\u7684\u516d\u7ef4\u5361\u4e18\u6d41\u5f62\u3001JIAIJIA \u9501\u534f\u8bae\u4e0e\u5b87\u5b99\u8ba1\u7b97\u91cd\u6784.docx', 'docx'),
    ('[任正非]《从系统工程角度出发规划华为大生产体系架构，建设世界一流的先进生产系统》[20180224]C.pdf', 'pdf'),
    ('基于复合体理学的协同创造研究空间方案（含编号体系）.docx', 'docx'),
    ('论人工意识的实现：基于DIKWP超维架构与IAWW场论的终极统一范式.docx', 'docx'),
]

# 尝试找其他6个文件
import glob
all_files = os.listdir(DOWNLOADS)

# 额外查找可能的文件
EXTRA_PATTERNS = [
    '太乙预言机：基于 Lisp',
    '宇宙即 Lisp',
    '太乙预言机三部曲',
    '泛系流贯',
    '迈向万有在兹',
    'Lisp机、哥德尔',
    'AGI 奇点降临',
    '万物皆计算',
    '从LISP宏到全息',
    '中医基础理论的复合体',
    'EFTFT',
    '主体数学宣言',
]

extra_found = []
for pattern in EXTRA_PATTERNS:
    for f in all_files:
        if pattern in f and f not in [x[0] for x in FILES] and f not in extra_found:
            ext = f.split('.')[-1].lower()
            if ext in ('docx', 'pdf'):
                extra_found.append(f)
                break

print(f"找到额外文件: {len(extra_found)}")
for f in extra_found:
    print(f"  - {f}")

ALL_FILES = FILES + [(f, f.split('.')[-1].lower()) for f in extra_found[:6]]

def read_docx(path):
    try:
        doc = Document(path)
        return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        return f'[ERROR: {e}]'

def read_pdf(path):
    try:
        doc = fitz.open(path)
        return ''.join([page.get_text() for page in doc])
    except Exception as e:
        return f'[ERROR: {e}]'

results = {}
for fname, ftype in ALL_FILES:
    path = os.path.join(DOWNLOADS, fname)
    if not os.path.exists(path):
        print(f'[NOT FOUND] {fname[:50]}')
        continue
    
    if ftype == 'docx':
        text = read_docx(path)
    elif ftype == 'pdf':
        text = read_pdf(path)
    else:
        text = '[unknown]'
    
    results[fname] = text
    print(f'\n{"="*70}')
    print(f'FILE: {fname[:60]}')
    print(f'LENGTH: {len(text)} chars')
    print(f'{"="*70}')
    # 只打印前3000字
    print(text[:3000])
    if len(text) > 3000:
        print('\n...[后段摘要]...')
        print(text[-1000:])

print(f'\n\n总计读取: {len(results)} 个文件')
