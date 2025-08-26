import json
import os
import re
import time
import nltk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ---------------- nltk 初始化 ----------------
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# ---------------- 配置 ----------------
urls = [
    "http://en.people.cn/index.html",
    "http://en.people.cn/90780/index.html",
    "http://en.people.cn/90785/index.html",
    "http://en.people.cn/90777/index.html",
    "http://en.people.cn/business/index.html",
    "http://en.people.cn/90882/index.html",
    "http://en.people.cn/90782/index.html",
    "http://en.people.cn/202936/index.html",
    "http://en.people.cn/98389/index.html",
    "http://en.people.cn/90783/index.html",
    "http://en.people.cn/90779/index.html",
    "http://en.people.cn/102842/index.html",
    "http://en.people.cn/98649/index.html",
    "http://en.people.cn/205040/index.html",
    "http://en.people.cn/102840/index.html",
    "http://en.people.cn/90786/index.html",
    "http://en.people.cn/90782/207872/index.html",
    "http://english.people.com.cn/518252/index.html",
    "http://en.people.cn/102775/index.html"
]

save_dir = "single_sentences"
os.makedirs(save_dir, exist_ok=True)
progress_file = "progress.json"

chrome_options = Options()
# chrome_options.add_argument("--headless")  # 需要可取消注释
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

# ---------------- 辅助函数 ----------------
def split_into_sentences(text):
    """
    使用 nltk 拆分句子，并过滤掉小于5个词的句子
    """
    sentences = sent_tokenize(text)
    filtered = [s.strip() for s in sentences if len(s.strip().split()) >= 5]
    return filtered


def save_sentences(title, sentences, page_index):
    """保存文章，每句一行"""
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
    filename = f"{save_dir}/{safe_title}_page{page_index}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for sentence in sentences:
            f.write(sentence + "\n")

def load_progress():
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

# ---------------- 主抓取逻辑 ----------------
progress = load_progress()

for channel_url in urls:
    print(f"\n开始抓取频道: {channel_url}")
    page_index = progress.get(channel_url, 1)
    last_page_article_count = -1

    while True:
        # 正确拼接翻页 URL
        if page_index == 1:
            url = channel_url
        else:
            if channel_url.endswith("index.html"):
                url = channel_url.replace("index.html", f"index{page_index}.html")
            else:
                url = channel_url.rstrip("/") + f"/index{page_index}.html"

        driver.get(url)
        time.sleep(2)

        try:
            article_links = driver.find_elements(By.XPATH, "//ul[@class='foreign_list8 cf']/li/a")
            article_hrefs = [a.get_attribute("href") for a in article_links if a.get_attribute("href")]
            article_hrefs = list({a if a.startswith("http") else "http://en.people.cn" + a for a in article_hrefs})

            if not article_hrefs:
                print(f"❌ 页面 {url} 无文章，停止翻页")
                break
            if len(article_hrefs) == last_page_article_count:
                print(f"⚠️ 页面 {url} 文章数量未变化，可能到达最后一页，停止翻页")
                break
            last_page_article_count = len(article_hrefs)
            print(f"✅ 第 {page_index} 页发现 {len(article_hrefs)} 篇文章")

        except Exception as e:
            print(f"获取文章列表失败: {url} | 错误: {e}")
            break

        for art_url in article_hrefs:
            try:
                driver.get(art_url)
                time.sleep(1)
                content_div = driver.find_element(By.XPATH, "//div[@class='w860 d2txtCon cf']")
                paragraphs = content_div.find_elements(By.TAG_NAME, "p")

                sentences = []
                for p in paragraphs:
                    if p.find_elements(By.TAG_NAME, "img"):
                        continue
                    text = p.text.strip()
                    if text:
                        sents = split_into_sentences(text)
                        sentences.extend(sents)

                title = driver.title.split("_")[0]
                if sentences:
                    save_sentences(title, sentences, page_index)
                    print(f"   ✔ {title} ({len(sentences)} 句)")
                else:
                    print(f"   ⚠️ {title} 无有效正文")

            except Exception as e:
                print(f"文章抓取失败: {art_url} | 错误: {e}")

        progress[channel_url] = page_index + 1
        save_progress(progress)
        page_index += 1

driver.quit()
print("\n🎉 全部频道抓取完成，每篇文章已按句子保存，可随时断点续爬")
