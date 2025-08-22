# -*- coding: utf-8 -*-
import re
from collections import Counter
import unicodedata

INPUT_FILE = "/home/maohongyao/pro/code/clean/data_clean.zh"
COL_IDX = 2  # 第三列

AD_KEYWORDS = [
    "UU看书", "ＵＵ看书", "uukanshu", "ｕｕｋａｎｓｈｕ",
    "小说网", "白金小说网", "随梦小说网", "百度搜索"
]

RE_HTML = re.compile(r"<[^>]+>")
RE_CHAPTER = re.compile(r'^第[零一二三四五六七八九十百千0-9]+[章节卷回](?:[:：\s]|$)')
RE_SPECIAL = re.compile(r"[★☆●◆■□▲▼※◎○◇]")

ZERO_WIDTH = ''.join(['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\ufeff'])
RE_ZERO_WIDTH = re.compile('[%s]' % re.escape(ZERO_WIDTH))

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFKC', s)
    s = RE_ZERO_WIDTH.sub('', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    total = len(lines)
    third_col_lengths = [len(line.split("\t")[COL_IDX]) for line in lines if len(line.split("\t"))>COL_IDX]

    print(f"\n📊 总行数: {total}")
    if third_col_lengths:
        print(f"📏 第三列最短长度: {min(third_col_lengths)}, 最长长度: {max(third_col_lengths)}")

    # 空行
    empty = [i for i, line in enumerate(lines, 1) 
             if len(line.split("\t"))>COL_IDX and not line.split("\t")[COL_IDX].strip()]
    print(f"\n🔍 第三列空行: {len(empty)}")
    if empty:
        print("例子:", empty[:10])
    else:
        print("✅ 无问题")

    # 无中文
    no_cn = [i for i, line in enumerate(lines, 1)
             if len(line.split("\t"))>COL_IDX and not re.search(r'[\u4e00-\u9fff]', line.split("\t")[COL_IDX])]
    print(f"\n🔍 第三列无中文行: {len(no_cn)}")
    if no_cn:
        print("例子:", no_cn[:10])
    else:
        print("✅ 无问题")

    # HTML
    html_lines = [i for i, line in enumerate(lines, 1)
                  if len(line.split("\t"))>COL_IDX and RE_HTML.search(line.split("\t")[COL_IDX])]
    print(f"\n🔍 第三列含 HTML 标签的行: {len(html_lines)}")
    if html_lines:
        print("例子:", html_lines[:10])
    else:
        print("✅ 无问题")

    # 广告/来源
    ad_lines = []
    for i, line in enumerate(lines, 1):
        if len(line.split("\t"))<=COL_IDX:
            continue
        text = normalize_text(line.split("\t")[COL_IDX]).lower()
        for kw in AD_KEYWORDS:
            if kw.lower() in text:
                ad_lines.append(i)
                break
    print(f"\n🔍 第三列广告/来源残留: {len(ad_lines)}")
    if ad_lines:
        for idx in ad_lines[:10]:
            print(f"行号 {idx}: '{lines[idx-1].split(chr(9))[COL_IDX]}'")
    else:
        print("✅ 无问题")

    # 章节标题
    chapter_lines = []
    for i, line in enumerate(lines, 1):
        if len(line.split("\t"))<=COL_IDX:
            continue
        text = normalize_text(line.split("\t")[COL_IDX])
        if RE_CHAPTER.match(text):
            chapter_lines.append(i)
    print(f"\n🔍 第三列章节标题行: {len(chapter_lines)}")
    if chapter_lines:
        for idx in chapter_lines[:10]:
            print(f"行号 {idx}: '{lines[idx-1].split(chr(9))[COL_IDX]}'")
    else:
        print("✅ 无问题")

    # 特殊符号
    special_lines = []
    for i, line in enumerate(lines, 1):
        if len(line.split("\t"))<=COL_IDX:
            continue
        text = line.split("\t")[COL_IDX]
        if RE_SPECIAL.search(text):
            special_lines.append(i)
    print(f"\n🔍 第三列特殊符号行: {len(special_lines)}")
    if special_lines:
        for idx in special_lines[:10]:
            print(f"行号 {idx}: '{lines[idx-1].split(chr(9))[COL_IDX]}'")
    else:
        print("✅ 无问题")

    # 重复行
    counter = Counter([line.split("\t")[COL_IDX] for line in lines if len(line.split("\t"))>COL_IDX])
    dup_lines = [i for i, line in enumerate(lines, 1)
                 if len(line.split("\t"))>COL_IDX and counter[line.split("\t")[COL_IDX]]>1]
    print(f"\n🔍 第三列重复行: {len(dup_lines)}")
    if dup_lines:
        for idx in dup_lines[:10]:
            print(f"行号 {idx}: '{lines[idx-1].split(chr(9))[COL_IDX]}'")
    else:
        print("✅ 无问题")

if __name__ == "__main__":
    main()
