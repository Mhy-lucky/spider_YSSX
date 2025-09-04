# 假设清洗后的文件是 data_clean_all.zh
import re, unicodedata
from collections import Counter

# ---------- 这里直接导入你原来的正则和规则 ----------
RE_CHINESE = re.compile(r'[\u4e00-\u9fff]')
RE_ALL_PUNCT = re.compile(r'^[\s，。、“”‘’：；！？…—,.!?\-~··]+$')
VALID_END = re.compile(r'(。|！|？|。”|！”|？”)$')
ZERO_WIDTH = ''.join(['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\ufeff'])
RE_ZERO_WIDTH = re.compile('[%s]' % re.escape(ZERO_WIDTH))

def is_valid_simple(text):
    norm = unicodedata.normalize('NFKC', text)
    norm = RE_ZERO_WIDTH.sub('', norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    if not RE_CHINESE.search(norm):
        return False, "no_chinese"
    if RE_ALL_PUNCT.fullmatch(norm):
        return False, "all_punct"
    if not VALID_END.search(norm):
        return False, "invalid_end"
    return True, None

counters = Counter()
with open("/data1/to_hongyao/data_clean.zh", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3:
            counters["short_cols"] += 1
            continue
        keep, reason = is_valid_simple(parts[2])
        if not keep:
            counters[reason] += 1

print("=== 清洗后剩余问题统计 ===")
for k, v in counters.most_common():
    print(f"{k}: {v}")

