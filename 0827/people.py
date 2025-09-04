# -*- coding: utf-8 -*-
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import nltk

# 确保 punkt 分词器
nltk.download('punkt')

# ---------------- 配置 ----------------
URLS = [
    "http://en.people.cn/90780/",
    "http://en.people.cn/90785/",
    "http://en.people.cn/90777/",
    "http://en.people.cn/business/",
    "http://en.people.cn/90882/",
    "http://en.people.cn/90782/",
    "http://en.people.cn/202936/",
    "http://en.people.cn/98389/",
    "http://en.people.cn/90783/",
    "http://en.people.cn/90779/",
    "http://en.people.cn/102842/",
    "http://en.people.cn/98649/",
    "http://en.people.cn/205040/",
    "http://en.people.cn/102840/",
    "http://en.people.cn/90786/",
    "http://en.people.cn/90782/207872/",
    "http://english.people.com.cn/518252/",
    "http://en.people.cn/102775/"#
]

OUTPUT_FILE = "articles_clean.txt"
PROGRESS_FILE = "progress.json"
SLEEP_TIME = 2

# ---------------- 浏览器配置 ----------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# ---------------- 工具函数 ----------------
def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def get_article_links(channel_url):
    """抓文章链接"""
    driver.get(channel_url)
    time.sleep(SLEEP_TIME)

    if "518252" in channel_url or "102840" in channel_url:
        elems = driver.find_elements(By.XPATH, "//ul[@id='tiles']/li/a | //ul[@id='tiles']/li/p/a")
    elif "102775" in channel_url:
        elems = driver.find_elements(By.XPATH, "//ul[@class='foreign_list7 cf']/li/a")
    else:
        elems = driver.find_elements(By.XPATH, "//ul[@class='foreign_list8 cf']/li/a")

    links = [a.get_attribute("href") for a in elems if a.get_attribute("href")]
    links = list({a if a.startswith("http") else "http://en.people.cn" + a for a in links})
    return links

def extract_sentences(article_url):
    """抓正文并分句"""
    driver.get(article_url)
    time.sleep(SLEEP_TIME)

    paras = driver.find_elements(By.XPATH, "//div[@class='w860 d2txtCon cf']/p")
    texts = []
    for p in paras:
        txt = p.text.strip()
        if not txt:
            continue
        align_attr = p.get_attribute("align") or p.get_attribute("style") or ""
        if "center" in align_attr.lower():
            continue
        texts.append(txt)

    sentences = []
    for para in texts:
        sents = nltk.sent_tokenize(para)
        for s in sents:
            words = s.split()
            if len(words) >= 5:  # 过滤太短句子
                sentences.append(s.strip())
    return sentences

# ---------------- 主流程 ----------------
def main():
    progress = load_progress()
    seen_urls = set()

    # 读取已抓文章，去重
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                seen_urls.add(line.strip())
    except:
        pass

    for channel_url in URLS:
        page_index = progress.get(channel_url, 1)
        print(f"\n开始抓取频道: {channel_url}")

        while True:
            if page_index == 1:
                url = channel_url + "index.html"
            else:
                url = channel_url + f"index{page_index}.html"

            article_links = get_article_links(url)
            if not article_links:
                print(f"⚠️ 没有更多文章，停止分页")
                break

            print(f"✅ 第 {page_index} 页发现 {len(article_links)} 篇文章")

            for art_url in article_links:
                if art_url in seen_urls:
                    continue
                try:
                    sentences = extract_sentences(art_url)
                    if sentences:
                        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                            for s in sentences:
                                f.write(s + "\n")
                        seen_urls.add(art_url)
                except Exception as e:
                    print(f"  ❌ 抓取失败 {art_url}: {e}")

            page_index += 1
            progress[channel_url] = page_index
            save_progress(progress)

    driver.quit()
    print("\n🎉 所有任务完成！")

if __name__ == "__main__":
    main()
