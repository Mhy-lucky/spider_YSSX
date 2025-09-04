# -*- coding: utf-8 -*-
"""
全功能大文件小说清洗脚本（带正则说明）
特点：
1. 保序去重
2. 广告/品牌过滤
3. 脏关键词 & 括号内脏关键词过滤（AC自动机）
4. 特殊符号、重复字符、控制字符、零宽字符过滤
5. HTML标签、URL、邮箱、QQ、章节、整句标点过滤
6. 生僻字/半句检测 + 结尾合法标点
7. 原始行保留输出
8. 屏幕打印进度
"""

import re
import unicodedata
from collections import Counter
import ahocorasick

# ---------- 配置 ----------
INPUT_FILE = "/data1/to_hongyao/chinese_web_novel.zh"
OUTPUT_FILE = "/data1/to_hongyao/data_clean_all.zh"
DEFAULT_MAX_LEN = 300
PROGRESS_INTERVAL = 1_000_000

# ---------- 广告/品牌 ----------
SITE_BRANDS = [
    "UU看书", "ＵＵ看书", "uukanshu", "ｕｕｋａｎｓｈｕ",
    "小说网", "顶点小说", "笔趣阁", "biquge", "ＢＩＱＵＧＥ",
    "www", "ＷＷＷ", "．com", ".com", "．net", ".net", "ｎｅｔ",
    "qidian", "jjwxc", "17k", "zongheng", "faloo", "sfacg",
    "shuqi", "hongxiu", "zhuishushenqi", "ikanshu", "dingdian",
    "bqg", "kanshuzhong", "piaotian", "69shu", "soxs", "txt", "23us",
    "百度搜索", "白金小说网", "随梦小说网", "新世纪小说网", "无错小说网",
    "看小说最快更新", "给力文学网"
]

NON_CONTENT_KEYWORDS = [
    "版权", "目录", "声明", "本书", "作者简介", "封面", "序言", "推荐序", "出版", "ISBN",
    "书名", "责任编辑", "手机阅读", "无弹窗", "最新章节", "收藏本站", "求推荐票", "打赏",
    "感谢订阅", "下载", "阅读网", "起点", "晋江", "飞卢", "书友", "加更", "求月票",
    "上一章", "下一章", "返回书页", "加入书签", "求收藏"
]

# ---------- 脏关键词 ----------
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

BRACKET_KEYWORDS = ["广告", "更新", "电脑", "系统", "软件", "来源", "网址", "小说", "版权"]

# ---------- 正则 ----------
# 中文字符检测：至少包含一个汉字
RE_CHINESE = re.compile(r'[\u4e00-\u9fff]')

# HTML标签检测：<tag>形式的标签
RE_HTML = re.compile(r'<[^>]+>')

# URL检测：http:// 或 www
RE_URL = re.compile(r'(http[s]?://|www\.)', re.I)

# 邮箱检测
RE_EMAIL = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')

# 手机或QQ号检测：连续5-11位数字
RE_PHONE_QQ = re.compile(r'\b\d{5,11}\b')

# 章节/卷/回检测，如 "第一章" "第十回"
RE_CHAPTER = re.compile(r'^第[\s零一二三四五六七八九十百千0-9]{1,10}[章节卷回]')

# 全为标点或空白字符
RE_ALL_PUNCT = re.compile(r'^[\s，。、“”‘’：；！？…—,.!?\-~··]+$')

# 重复字符 >= 6
RE_REPEAT_CHAR = re.compile(r'(.)\1{5,}')

# 控制字符
RE_CTRL = re.compile(r'[\x00-\x1f]')

# 双斜杠 //
RE_SLASH_SLASH = re.compile(r'//')

# 特殊符号过滤：★☆●◆■□▲▼※◎○◇
RE_SPECIAL_SYMBOLS = re.compile(r"[★☆●◆■□▲▼※◎○◇]")

# 广告句型过滤
RE_ADS = re.compile(
    r'(百度搜索.*|白金小说网.*|随梦小说网.*|新世纪小说网.*|无错小说网.*|看小说最快更新.*|给力文学网.*)',
    re.I
)

# 零宽字符：\u200b \u200c \u200d \u200e \u200f \ufeff
ZERO_WIDTH = ''.join(['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\ufeff'])
RE_ZERO_WIDTH = re.compile('[%s]' % re.escape(ZERO_WIDTH))

# 问号重复两次以上检测
two_or_more_question = re.compile(r'\?{2,}|？{2,}')

# 特殊符号 [【*[
special_symbols2 = re.compile(r'[【*\[]')

# 整句括号匹配：整句被（）或()包裹
full_bracket_pattern = re.compile(r'^[（(].*[)）]')

# 括号内内容匹配
bracket_inner_pattern = re.compile(r'[（(]([^）)]*)[)）]')

# 允许字符集（汉字、数字、标点）
allowed_chars = re.compile(r'^[\u4e00-\u9fff0-9，。！？：；、“”‘’—…（）《》\s]+$')

# 结尾合法标点：。！？及带引号的
VALID_END = re.compile(r'(。|！|？|。”|！”|？”)$')

# ---------- AC 自动机 ----------
ALLOWED_CHARS_AC = "一二三四五六七八九十百千万亿零〇甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥" \
                   "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" \
                   "，。！？：；、“”‘’（）【】——、…《》  "

def build_ac_automaton(words):
    A = ahocorasick.Automaton()
    for idx, word in enumerate(words):
        A.add_word(word, (idx, word))
    A.make_automaton()
    return A

DIRTY_AC = build_ac_automaton(DIRTY_KEYWORDS)       # 脏关键词
BRACKET_AC = build_ac_automaton(BRACKET_KEYWORDS)   # 括号内脏关键词
ALLOWED_AC = build_ac_automaton(ALLOWED_CHARS_AC)   # 生僻字检测

def contains_dirty_ac(text, automaton):
    for _, _ in automaton.iter(text):
        return True
    return False

def has_illegal_char(text):
    for c in text:
        if not ALLOWED_AC.exists(c):
            return True
    return False

# ---------- 核心检查 ----------
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

    norm = unicodedata.normalize('NFKC', text)
    norm = RE_ZERO_WIDTH.sub('', norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    lower = norm.lower()

    # 正则过滤说明
    if not RE_CHINESE.search(norm):           # 没有中文
        counters["no_chinese"] += 1
        return False, "no_chinese"
    if RE_HTML.search(norm):                  # HTML标签
        counters["html"] += 1
        return False, "html"
    if RE_CTRL.search(norm) or "�" in norm:   # 控制字符或替换符
        counters["control_or_replacement"] += 1
        return False, "control_or_replacement"
    if RE_ALL_PUNCT.fullmatch(norm):          # 全标点
        counters["all_punct"] += 1
        return False, "all_punct"
    if RE_REPEAT_CHAR.search(norm):           # 重复字符
        counters["repeat_char"] += 1
        return False, "repeat_char"
    if RE_URL.search(norm) or RE_EMAIL.search(norm) or RE_PHONE_QQ.search(norm):
        counters["url_email_phone"] += 1
        return False, "url_email_phone"
    if RE_CHAPTER.match(norm):                # 章节
        counters["chapter"] += 1
        return False, "chapter"
    if RE_SLASH_SLASH.search(norm):           # //
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
    if contains_dirty_ac(norm, DIRTY_AC):
        counters["dirty_keywords"] += 1
        return False, "dirty_keywords"
    if not allowed_chars.match(norm):
        counters["illegal_chars"] += 1
        return False, "illegal_chars"
    if two_or_more_question.search(norm):
        counters["multi_question"] += 1
        return False, "multi_question"
    if special_symbols2.search(norm):
        counters["special_symbols2"] += 1
        return False, "special_symbols2"
    if full_bracket_pattern.match(norm):
        counters["full_bracket"] += 1
        return False, "full_bracket"
    tmp = norm
    while match := bracket_inner_pattern.search(tmp):
        if contains_dirty_ac(match.group(1), BRACKET_AC):
            counters["bracket_dirty"] += 1
            return False, "bracket_dirty"
        tmp = tmp[match.end():]
    if has_illegal_char(norm):
        counters["has_illegal_char"] += 1
        return False, "has_illegal_char"
    if not VALID_END.search(norm):
        counters["invalid_end"] += 1
        return False, "invalid_end"

    return True, None

# ---------- 清洗核心 ----------
def run():
    total = kept = dropped = 0
    counters = Counter()
    seen_hashes = set()

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as fin, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as fout:

        for line_no, line in enumerate(fin, 1):
            total += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                counters["short_cols"] += 1
                dropped += 1
                continue

            text = parts[2]
            norm = unicodedata.normalize('NFKC', text)
            norm = RE_ZERO_WIDTH.sub('', norm)
            norm = re.sub(r'\s+', ' ', norm).strip()
            text_hash = hash(norm)

            if text_hash in seen_hashes:
                counters["duplicate"] += 1
                dropped += 1
                continue
            seen_hashes.add(text_hash)

            keep, reason = is_valid(text, DEFAULT_MAX_LEN, counters)
            if not keep:
                dropped += 1
                continue

            fout.write(line + "\n")
            kept += 1

            if kept % 100_000 == 0:
                print(f"[progress] kept={kept} / seen={total}")

    print("\n=== Done ===")
    print(f"完成 ✅ 总行数: {total}, 保留: {kept}, 删除: {dropped}")
    print("Drop reasons 统计：")
    for k, v in counters.most_common():
        if v:
            print(f"  - {k}: {v}")

if __name__ == "__main__":
    run()
