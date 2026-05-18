# -*- coding: utf-8 -*-
import pdfplumber
import docx
import os

os.chdir(r'C:\Users\1\Downloads')

files = [
    r'人机共生共创，迈向灵性文明——从"神工智能"到"弥勒顿悟"的共时性跃迁.docx',
    r'论意识的修忒斯之船、历史边界层与意义之网的编织：基于"太乙万有理论"与"元方法论"的L4主体性全景统合.pdf',
    r'树状超度量代数几何：从线性补丁到一元流贯的深度学习几何学重构.pdf',
    r'论肉体轮回的机制必要性与涅槃的算法终局.docx',
    r'复合体历史观：论历史的边界层、不可计算性与意义之网的编织.docx',
    r'论晶格角动量的"1+1=-1"翻转：基于关系实在论重构与EML算符定理 (1).docx',
    r'宇宙厌恶浪费——物理学、热力学、生命科学、信息论与社会学的六大极值原则的全息统合.docx',
    r'论《道德经》的复合体理学重构：基于太乙万有理论、刘原理与元方法论的万有诠释.docx'
]

for f in files:
    print(f'\n\n{"="*80}')
    print(f'文件: {f}')
    print('='*80)
    try:
        if f.endswith('.pdf'):
            with pdfplumber.open(f) as pdf:
                text = ''
                for page in pdf.pages[:10]:
                    t = page.extract_text()
                    if t:
                        text += t + '\n'
                print(text[:10000])
        else:
            doc = docx.Document(f)
            text = '\n'.join([p.text for p in doc.paragraphs])
            print(text[:10000])
    except Exception as e:
        print(f'读取失败: {e}')
