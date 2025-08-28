# -*- coding: utf-8 -*-
"""
高效大文件小说清洗（生僻字/半句）
输入: 第三列文本
输出: 原始行保留，只写合法行
"""

import ahocorasick
import re

INPUT_FILE = "/data1/to_hongyao/data.zh"
OUTPUT_FILE = "/data1/to_hongyao/data_clean.zh"
PROGRESS_INTERVAL = 1_000_000

# 允许字符：汉字、常用标点、数字、空格
ALLOWED_CHARS = "一二三四五六七八九十百千万亿零〇甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥" \
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" \
                "，。！？：；、“”‘’（）【】——、…《》  "

# 结尾允许字符
VALID_END = re.compile(r'(。|！|？|。”|！”|？”)$')

# ---------- 构建 AC 自动机 ----------
AC_ALLOWED = ahocorasick.Automaton()
for c in ALLOWED_CHARS:
    AC_ALLOWED.add_word(c, c)
AC_ALLOWED.make_automaton()

def has_illegal_char(text):
    for c in text:
        if not AC_ALLOWED.exists(c):
            return True
    return False

def is_line_valid(text):
    if has_illegal_char(text):
        return False
    if not VALID_END.search(text):
        return False
    return True

def run():
    total = kept = dropped = 0
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as fin, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
        for line in fin:
            total += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                dropped += 1
                continue
            col3 = parts[2]
            if not is_line_valid(col3):
                dropped += 1
                continue
            fout.write(line)  # 保留原始行
            kept += 1
            if total % PROGRESS_INTERVAL == 0:
                print(f"[seen] {total:,}  [kept] {kept:,}")
    print(f"Done ✅ 总行数: {total:,}, 保留: {kept:,}, 删除: {dropped:,}")
    print(f"输出文件: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
