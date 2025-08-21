# -*- coding: utf-8 -*-

from pathlib import Path
import markdown
import sys

# ---------------- 输入 Markdown 文件 ----------------
if len(sys.argv) < 2:
    print("用法: python md_to_html.py 文件名.md")
    sys.exit(1)

input_file = sys.argv[1]
md_file = Path(input_file)

if not md_file.exists() or not md_file.suffix.lower() == ".md":
    print(f"❌ 文件不存在或不是 Markdown 文件: {md_file}")
    # 列出当前目录下的 .md 文件，方便检查
    md_list = list(Path('.').glob('*.md'))
    if md_list:
        print("当前目录下的 Markdown 文件：")
        for f in md_list:
            print(f" - {f.name}")
    else:
        print("当前目录下没有 Markdown 文件")
    sys.exit(1)

# ---------------- 读取 Markdown 内容 ----------------
text = md_file.read_text(encoding="utf-8")

# ---------------- 转换为 HTML ----------------
html_body = markdown.markdown(
    text,
    extensions=["fenced_code", "codehilite", "tables", "toc"]
)

# ---------------- HTML 模板 ----------------
html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>{md_file.stem}</title>
</head>
<body>
{html_body}
</body>
</html>
"""

# ---------------- 输出 HTML ----------------
output_file = md_file.with_suffix(".html")
output_file.write_text(html, encoding="utf-8")

print(f"✅ 转换完成: {output_file}")
