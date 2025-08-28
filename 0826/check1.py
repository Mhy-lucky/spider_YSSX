# -*- coding: utf-8 -*-
"""
小说第三列全面噪声检查 + 删除脏数据
功能：
1. 检查第三列是否含噪声
2. 删除含噪声的行
3. 打印匹配行及原因到屏幕
4. 支持进度显示
"""

import re
from collections import Counter

INPUT_FILE = '/data1/to_hongyao/data_clean_cleaned.zh'
OUTPUT_FILE = '/data1/to_hongyao/data.zh'

# 全局脏关键词
DIRTY_KEYWORDS = [
    "去广告太多？有弹窗？","界面清新，全站广告","未完待续","月票","票票",
    "票","加更","PS","敬请关注","大力支持","更新","&","小说网","转载","版权",
    "免费阅读","访问","下载","新书","书友","书荒","多多支持","收藏","发表",
    "贴吧","评论","瓶颈","打赏","断更","亲们","剧情","补更","详见拙作","启航",
    "书迷","本人","一更","二更","三更","四更","章","和谐","群","红包","金牌",
    "首发","河蟹","友情提示","小说","补充","英语翻译","休息","写","更","电脑",
    "（）","码","发布","办公室","老张","注","作者","域名","网","书评"
]

# 括号内关键词
BRACKET_KEYWORDS = DIRTY_KEYWORDS

# 正则
RE_DIRTY = re.compile("|".join(map(re.escape, DIRTY_KEYWORDS)))
RE_ALLOWED = re.compile(r'^[\u4e00-\u9fff0-9，。！？：；、“”‘’—…（）《》\s]+$')
RE_MULTI_Q = re.compile(r'\?{2,}|？{2,}')
RE_SPECIAL = re.compile(r'[【*\[]')
RE_FULL_BRACKET = re.compile(r'^[（(].+[)）]$')
RE_BRACKET = re.compile(r'[（(](.*?)[)）]')
RE_HTML = re.compile(r'<[^>]+>')
RE_URL = re.compile(r'(http[s]?://|www\.)', re.I)
RE_EMAIL = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
RE_PHONE_QQ = re.compile(r'\b\d{5,11}\b')
RE_REPEAT_CHAR = re.compile(r'(.)\1{5,}')

PROGRESS_INTERVAL = 1_000_0000

def check_noise(col3):
    issues = []

    if RE_DIRTY.search(col3):
        issues.append("dirty_keyword")
    if not RE_ALLOWED.match(col3):
        issues.append("non_chinese_or_invalid_chars")
    if RE_MULTI_Q.search(col3):
        issues.append("multi_question")
    if RE_SPECIAL.search(col3):
        issues.append("special_symbol")
    if RE_FULL_BRACKET.match(col3):
        issues.append("full_bracket")
    for m in RE_BRACKET.finditer(col3):
        content = m.group(1)
        if any(k in content for k in BRACKET_KEYWORDS):
            issues.append("bracket_dirty")
            break
    if RE_HTML.search(col3):
        issues.append("html_tag")
    if RE_URL.search(col3) or RE_EMAIL.search(col3) or RE_PHONE_QQ.search(col3):
        issues.append("url_email_phone")
    if RE_REPEAT_CHAR.search(col3):
        issues.append("repeat_char")
    return issues

def run():
    line_count = 0
    kept_lines = 0
    dropped_lines = 0
    counters = Counter()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:

        for line in f:
            line_count += 1
            parts = line.strip().split('\t')
            if len(parts) < 3:
                dropped_lines += 1
                continue
            col3 = parts[2]
            issues = check_noise(col3)
            if issues:
                dropped_lines += 1
                for i in issues:
                    counters[i] += 1
                continue  # 直接删除这一行
            # 写入干净行
            fout.write(line + '\n')
            kept_lines += 1

            if line_count % PROGRESS_INTERVAL == 0:
                print(f"[progress] processed {line_count:,} lines, kept {kept_lines:,}, dropped {dropped_lines:,}")

    print("\n=== Done ===")
    print(f"Total lines: {line_count:,}, Kept: {kept_lines:,}, Dropped: {dropped_lines:,}")
    print("Issue counts:")
    for k, v in counters.most_common():
        print(f"  {k}: {v}")
    print("Cleaned file saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    run()
