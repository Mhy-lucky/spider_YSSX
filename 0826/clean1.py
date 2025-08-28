# -*- coding: utf-8 -*-
"""
高效大文件小说清洗（Aho-Corasick 自动机版）
特点：
1. 只处理第三列
2. 删除脏关键词、括号内脏关键词、特殊符号、问号、非中文字符、整句括号
3. 适合大文件（百GB以上）
4. 保留原始行写入文件
5. 屏幕打印进度
"""

import ahocorasick
import re

INPUT_FILE = "/data1/to_hongyao/data_clean.zh"
OUTPUT_FILE = "/data1/to_hongyao/data_clean_cleaned.zh"
PROGRESS_INTERVAL = 1_000_000  # 每处理100万行打印一次

# 脏关键词
DIRTY_KEYWORDS = [
    "去广告太多？有弹窗？", "界面清新，全站广告", "未完待续", "月票", "票票", "票",
    "加更", "PS", "敬请关注", "大力支持", "更新", "&", "小说网", "转载", "版权",
    "免费阅读", "访问", "下载", "新书", "书友", "书荒", "多多支持", "收藏", "发表",
    "贴吧", "评论", "瓶颈", "打赏", "断更", "亲们", "剧情", "补更", "详见拙作",
    "启航", "书迷", "本人", "一更", "二更", "三更", "四更", "章", "和谐", "群",
    "红包", "金牌", "首发", "河蟹", "友情提示", "小说", "补充", "英语翻译", "休息",
    "写", "更", "电脑", "（）", "码", "发布", "办公室", "老张", "注", "作者",
    "域名", "网", "书评","点击","榜","上榜","推荐","免费","最新","书城","观众","水字数"
]

# 括号内脏关键词
BRACKET_KEYWORDS = ["广告", "更新", "电脑", "系统", "软件", "来源", "网址", "小说", "版权"]

# ---------- 正则 ----------
allowed_chars = re.compile(r'^[\u4e00-\u9fff0-9，。！？：；、“”‘’—…（）《》\s]+$')
two_or_more_question = re.compile(r'\?{2,}|？{2,}')
special_symbols = re.compile(r'[【*\[]')
full_bracket_pattern = re.compile(r'^[（(].*[)）]')

# 括号内匹配正则
bracket_inner_pattern = re.compile(r'[（(]([^）)]*)[)）]')

# ---------- 构建 Aho-Corasick 自动机 ----------
def build_ac_automaton(words):
    A = ahocorasick.Automaton()
    for idx, word in enumerate(words):
        A.add_word(word, (idx, word))
    A.make_automaton()
    return A

DIRTY_AC = build_ac_automaton(DIRTY_KEYWORDS)
BRACKET_AC = build_ac_automaton(BRACKET_KEYWORDS)

# ---------- 核心检查 ----------
def contains_dirty_ac(text, automaton):
    for _, _ in automaton.iter(text):
        return True
    return False

def is_line_valid(text: str) -> bool:
    if contains_dirty_ac(text, DIRTY_AC):
        return False
    if not allowed_chars.match(text):
        return False
    if two_or_more_question.search(text):
        return False
    if special_symbols.search(text):
        return False
    if full_bracket_pattern.match(text):
        return False
    # 括号内脏关键词
    tmp = text
    while match := bracket_inner_pattern.search(tmp):
        if contains_dirty_ac(match.group(1), BRACKET_AC):
            return False
        tmp = tmp[match.end():]
    return True

# ---------- 清洗核心 ----------
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
