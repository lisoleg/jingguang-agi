#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量读取12个文档的内容"""

import os
import sys

PY_DOCX = True
PY_FITZ = True

try:
    from docx import Document
except ImportError:
    PY_DOCX = False

try:
    import fitz
except ImportError:
    PY_FITZ = False

DOWNLOADS = r'C:\Users\1\Downloads'

FILES = [
    '弹簧虫：多主体 △ 场耦合、能量循环与鲁棒动态平衡.docx',
    '面向中国场景的 DIKWP 开源系统白皮书.pdf',
    '时间基态与空间激发：基于\u201c一现象三视界\u201d的六维卡丘流形、JIAIJIA 锁协议与宇宙计算重构.docx',
    '[任正非]《从系统工程角度出发规划华为大生产体系架构，建设世界一流的先进生产系统》[20180224]C.pdf',
    '基于复合体理学的协同创造研究空间方案（含编号体系）.docx',
    '论人工意识的实现：基于DIKWP超维架构与IAWW场论的终极统一范式.docx',
]

# 尝试发现其余文件
import glob
all_files = os.listdir(DOWNLOADS)

def read_docx(path):
    try:
        doc = Document(path)
        return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        return f'[ERROR reading docx: {e}]'

def read_pdf(path):
    try:
        doc = fitz.open(path)
        return ''.join([page.get_text() for page in doc])
    except Exception as e:
        return f'[ERROR reading pdf: {e}]'

for fname in FILES:
    path = os.path.join(DOWNLOADS, fname)
    if not os.path.exists(path):
        print(f'[NOT FOUND] {fname}')
        continue
    
    ext = os.path.splitext(fname)[1].lower()
    if ext == '.docx':
        text = read_docx(path)
    elif ext == '.pdf':
        text = read_pdf(path)
    else:
        text = '[Unknown format]'
    
    print(f'\n{"="*60}')
    print(f'FILE: {fname}')
    print(f'LENGTH: {len(text)} chars')
    print(f'{"="*60}')
    print(text[:4000])
    print('...[truncated]...' if len(text) > 4000 else '')
