# -*- coding: utf-8 -*-
from docx import Document

files = [
    r"C:\Users\1\Downloads\论文艺创作的全息离散拓扑：基于"一现象、三视界、五层次"元方法论的流贯动力学与审美生成.docx",
    r"C:\Users\1\Downloads\论终极规律的自指不动点与最小性：为什么必须是刘原理（Liu's Principle）.docx"
]

for i, f in enumerate(files):
    print(f'\n{"="*60}')
    print(f'论文 {i+1}')
    print(f'{"="*60}')
    try:
        doc = Document(f)
        text = '\n'.join([p.text for p in doc.paragraphs])
        print(text[:18000])
    except Exception as e:
        print(f'Error: {e}')
