# -*- coding: utf-8 -*-
"""
读取PDF文件的脚本
使用pdfplumber提取文本
"""
import sys

try:
    import pdfplumber
    print("✅ pdfplumber已安装")
except ImportError:
    print("❌ pdfplumber未安装，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber

def read_pdf(file_path):
    """读取PDF文件并返回文本内容"""
    print(f"\n📄 正在读取: {file_path}")
    print("=" * 60)
    
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"总页数: {len(pdf.pages)}\n")
            
            full_text = ""
            for i, page in enumerate(pdf.pages, 1):
                print(f"--- 第 {i} 页 ---")
                text = page.extract_text()
                if text:
                    print(text[:500])  # 只打印前500字符
                    full_text += f"\n\n=== 第 {i} 页 ===\n\n" + text
                    print(f"\n✅ 第 {i} 页提取完成（{len(text)} 字符）")
                else:
                    print("（此页无文本内容）")
            
            print("\n" + "=" * 60)
            print(f"✅ 读取完成！总字符数: {len(full_text)}")
            return full_text
            
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python read_pdf.py <PDF文件路径>")
        print("\n可用的PDF文件：")
        import os
        downloads = r"C:\Users\1\Downloads"
        for f in os.listdir(downloads):
            if f.endswith(".pdf"):
                print(f"  - {f}")
    else:
        file_path = sys.argv[1]
        text = read_pdf(file_path)
        
        # 保存到文本文件
        if text:
            output_file = file_path.replace(".pdf", ".txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"\n💾 文本已保存到: {output_file}")
