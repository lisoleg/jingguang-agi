import zipfile
import xml.etree.ElementTree as ET
import os
import glob

base = r"C:\Users\1\Downloads"
all_files = glob.glob(os.path.join(base, "*.docx"))
holographic_files = [f for f in all_files if "全息离散治理" in f]
holographic_files.sort(key=os.path.getmtime, reverse=True)

results = []

for i, fpath in enumerate(holographic_files[:4], 1):
    fname = os.path.basename(fpath)
    result = {"index": i, "filename": fname, "content": ""}
    try:
        with zipfile.ZipFile(fpath, "r") as z:
            with z.open("word/document.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                texts = []
                for elem in root.iter():
                    if elem.tag.endswith("}t"):
                        if elem.text:
                            texts.append(elem.text)
                text = " ".join(texts)
                result["content"] = text
    except Exception as e:
        result["content"] = f"Error: {e}"
    results.append(result)

# 保存到文件
with open(r"C:\Users\1\WorkBuddy\2026-05-06-task-1\_doc_holographic.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"=== DOC{r['index']}: {r['filename']} ===\n\n")
        f.write(r["content"][:10000])  # 保存前10000字符
        f.write("\n\n")
