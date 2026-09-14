from pathlib import Path
from docx import Document

root = Path(__file__).parent
files = [
    root / "实验六 基尔霍夫定律验证实验报告.docx",
    root / "实验1-2" / "实验一 元件伏安特性测量实验报告.docx",
    root / "实验1-2" / "实验二 电位电压测定与电位图实验报告.docx",
]
for file in files:
    doc = Document(file)
    for p in doc.paragraphs:
        if p.text.startswith("【原理扩展】"):
            # Preserve the paragraph's existing run formatting while removing only our marker.
            p.runs[0].text = p.runs[0].text.replace("【原理扩展】", "", 1)
    doc.save(file)
