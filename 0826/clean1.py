# -*- coding: utf-8 -*-
"""
大文件清洗 + 保序去重 + 广告过滤增强
支持增量清洗，从指定行开始，并持久化哈希
"""

import re
import unicodedata
from collections import Counter
import os

# ---------- 配置 ----------
INPUT_FILE = "/data1/to_hongyao/chinese_web_novel.zh"
OUTPUT_FILE = "/home/maohongyao/pro/code/clean/data_clean.zh"
DEFAULT_MAX_LEN = 300
START_LINE = 2234385126  # 从哪一行开始继续清洗（前面已清洗完的行数 + 1）
SEEN_FILE = "/data1/to_hongyao/seen_hashes.txt"

# ---------- 广告/品牌 ----------
SITE_BRANDS = [
    "UU看书", "ＵＵ看书", "uukanshu", "ｕｕｋａｎｓｈｕ",
    "小说网", "顶点小说", "笔趣阁", "biquge", "ＢＩＱＵＧＥ",
    "www", "ＷＷＷ", "．com", ".com", "．net", ".net", "ｎｅｔ",
    "qidian", "jjwxc", "17k", "zongheng", "faloo", "sfacg",
    "shuqi", "hongxiu", "zhuishushenqi", "ikanshu", "dingdian",
    "bqg", "kanshuzhong", "piaotian", "69shu", "soxs", "txt", "23us",
    # 新增中文广告
    "百度搜索", "白金小说网", "随梦小说网", "新世纪小说网", "无错小说网",
    "看小说最快更新", "给力文学网"
]

NON_CONTENT_KEYWORDS = [
    "版权", "目录", "声明", "本书", "作者简介", "封面", "序言", "推荐序", "出版", "ISBN",
    "书名", "责任编辑", "手机阅读", "无弹窗", "最新章节", "收藏本站", "求推荐票", "打赏",
    "感谢订阅", "下载", "阅读网", "起点", "晋江", "飞卢", "书友", "加更", "求月票",
    "上一章", "下一章", "返回书页", "加入书签", "求收藏"
]

# ---------- 正则 ----------
RE_CHINESE = re.compile(r'[\u4e00-\u9fff]')
RE_HTML = re.compile(r'<[^>]+>')
RE_URL = re.compile(r'(http[s]?://|www\.)', re.I)
RE_EMAIL = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
RE_PHONE_QQ = re.compile(r'\b\d{5,11}\b')
RE_CHAPTER = re.compile(r'^第[\s零一二三四五六七八九十百千0-9]{1,10}[章节卷回]')
RE_ALL_PUNCT = re.compile(r'^[\s，。、“”‘’：；！？…—,.!?\-~··]+$')
RE_REPEAT_CHAR = re.compile(r'(.)\1{5,}')
RE_CTRL = re.compile(r'[\x00-\x1f]')
RE_SLASH_SLASH = re.compile(r'//')
RE_SPECIAL_SYMBOLS = re.compile(r"[★☆●◆■□▲▼※◎○◇]")

# 新增广告句型正则
RE_ADS = re.compile(
    r'(百度搜索.*|白金小说网.*|随梦小说网.*|新世纪小说网.*|无错小说网.*|看小说最快更新.*|给力文学网.*)',
    re.I
)

ZERO_WIDTH = ''.join(['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\ufeff'])
RE_ZERO_WIDTH = re.compile('[%s]' % re.escape(ZERO_WIDTH))

# ---------- 工具函数 ----------
def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFKC', s)
    s = RE_ZERO_WIDTH.sub('', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def brand_noise_hit(s_norm_lower: str) -> bool:
    for b in SITE_BRANDS:
        if b.lower() in s_norm_lower:
            return True
    letters_digits = re.sub(r'[^a-z0-9]+', '', s_norm_lower)
    if any(tld in letters_digits for tld in ["com", "cn", "org", "net"]):
        if "www" in letters_digits:
            return True
    return False

def is_valid(text: str, max_len: int, counters: Counter):
    if not text or text.strip() == "":
        counters["empty"] += 1
        return False, "empty"
    if len(text) > max_len:
        counters["too_long"] += 1
        return False, "too_long"
    if text.isdigit():
        counters["digit_only"] += 1
        return False, "digit_only"

    norm = normalize_text(text)
    lower = norm.lower()

    if not RE_CHINESE.search(norm):
        counters["no_chinese"] += 1
        return False, "no_chinese"
    if RE_HTML.search(norm):
        counters["html"] += 1
        return False, "html"
    if RE_CTRL.search(norm) or "�" in norm:
        counters["control_or_replacement"] += 1
        return False, "control_or_replacement"
    if RE_ALL_PUNCT.fullmatch(norm):
        counters["all_punct"] += 1
        return False, "all_punct"
    if RE_REPEAT_CHAR.search(norm):
        counters["repeat_char"] += 1
        return False, "repeat_char"
    if RE_URL.search(norm) or RE_EMAIL.search(norm) or RE_PHONE_QQ.search(norm):
        counters["url_email_phone"] += 1
        return False, "url_email_phone"
    if RE_CHAPTER.match(norm):
        counters["chapter"] += 1
        return False, "chapter"
    if RE_SLASH_SLASH.search(norm):
        counters["slash_slash"] += 1
        return False, "slash_slash"
    if any(kw in norm for kw in NON_CONTENT_KEYWORDS):
        counters["non_content_kw"] += 1
        return False, "non_content_kw"
    if RE_SPECIAL_SYMBOLS.search(norm):
        counters["special_symbols"] += 1
        return False, "special_symbols"
    if brand_noise_hit(lower):
        counters["brand_noise"] += 1
        return False, "brand_noise"
    if RE_ADS.search(norm):
        counters["ads"] += 1
        return False, "ads"

    return True, None

# ---------- 清洗核心 ----------
def run():
    total = kept = dropped = 0
    counters = Counter()
    seen_hashes = set()

    # 尝试加载之前的哈希集合
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    seen_hashes.add(int(line))
        print(f"[INFO] Loaded {len(seen_hashes)} hashes from {SEEN_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as fin, \
         open(OUTPUT_FILE, "a", encoding="utf-8") as fout, \
         open(SEEN_FILE, "a") as fseen:

        for line_no, line in enumerate(fin, 1):
            if line_no < START_LINE:
                continue  # 跳过已清洗过的行

            total += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= 2:
                counters["short_cols"] += 1
                dropped += 1
                continue

            text = parts[2]
            norm = normalize_text(text)
            text_hash = hash(norm)

            if text_hash in seen_hashes:
                counters["duplicate"] += 1
                dropped += 1
                continue
            seen_hashes.add(text_hash)
            fseen.write(f"{text_hash}\n")  # 实时追加到哈希文件

            keep, reason = is_valid(text, DEFAULT_MAX_LEN, counters)
            if not keep:
                dropped += 1
                continue

            fout.write(line)  # 保留原始行，已包含 \n
            kept += 1

            if kept % 100000 == 0:
                print(f"[progress] kept={kept} / processed={total} / line={line_no}")

    print("\n=== Done ===")
    print(f"完成 ✅ 总行数: {total}, 保留: {kept}, 删除: {dropped}")
    print("Drop reasons 统计：")
    for k, v in counters.most_common():
        if v:
            print(f"  - {k}: {v}")

if __name__ == "__main__":
    run()
