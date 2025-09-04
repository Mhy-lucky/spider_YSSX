# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import time
import re
import os

# -----------------------------
# Selenium 配置
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=chrome_options)

# -----------------------------
# 提取页面文章链接
# -----------------------------
def extract_article_links(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    article_links = set()
    for a in soup.find_all("a", href=True):
        href = a['href'].strip()
        # 统一处理 // 开头的链接
        if href.startswith("//"):
            full_url = "http:" + href
        elif href.startswith("http"):
            full_url = href
        else:
            full_url = "http://en.people.cn" + href
        # 匹配文章链接
        if "/n3/" in href or re.search(r"/\d+/\d+/index\.html$", href):
            article_links.add(full_url)
    return article_links

# -----------------------------
# 爬取子频道文章（支持翻页，边爬边写）
# -----------------------------
def crawl_subchannel(url, visited_articles, output_file):
    articles = set()
    try:
        driver.get(url)
        time.sleep(2)
    except WebDriverException:
        print(f"  无法访问子频道: {url}")
        return articles

    while True:
        page_articles = extract_article_links(driver.page_source)
        for link in page_articles:
            if link not in visited_articles:
                with open(output_file, "a") as f:
                    f.write(link + "\n")
                visited_articles.add(link)
        articles.update(page_articles)

        # 翻页处理
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except NoSuchElementException:
            break
        except WebDriverException:
            break
    return articles

# -----------------------------
# 获取子频道链接（严格递增）
# -----------------------------
def get_subchannels(main_url, max_increment=20):
    """
    根据主频道 URL 构造子频道 URL，严格在主频道基础上递增
    """
    subchannels = []
    match = re.match(r"(http://en\.people\.cn/\d+/)(\d+)/index\.html", main_url)
    if not match:
        return subchannels

    prefix = match.group(1)   # 主频道前缀
    main_num = int(match.group(2))

    for i in range(1, max_increment + 1):
        sub_num = main_num + i
        sub_url = f"{prefix}{main_num}/{sub_num}/index.html"
        subchannels.append(sub_url)
    return subchannels

# -----------------------------
# 读取已抓取文章（断点续爬）
# -----------------------------
def load_visited(output_file):
    visited_articles = set()
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            for line in f:
                visited_articles.add(line.strip())
    return visited_articles

# -----------------------------
# 主程序
# -----------------------------
def main():
    output_file = "/Users/admin/Desktop/coding/all_articles.txt"
    visited_articles = load_visited(output_file)

    with open("/Users/admin/Desktop/coding/0901/urls.txt", "r") as f:
        main_channels = [line.strip() for line in f if line.strip()]

    for main_url in main_channels:
        print(f"处理主频道: {main_url}")
        try:
            driver.get(main_url)
            time.sleep(2)
        except WebDriverException:
            print(f"无法访问主频道: {main_url}")
            continue

        # 1. 主频道首页文章
        main_articles = extract_article_links(driver.page_source)
        new_articles = main_articles - visited_articles
        for link in new_articles:
            with open(output_file, "a") as f:
                f.write(link + "\n")
            visited_articles.add(link)
        print(f"  主频道抓取 {len(new_articles)} 篇文章")

        # 2. 构造严格递增子频道
        subchannels = get_subchannels(main_url)

        # 3. 遍历子频道
        for sub_url in subchannels:
            print(f"  爬取子频道: {sub_url}")
            sub_articles = crawl_subchannel(sub_url, visited_articles, output_file)
            if sub_articles:
                print(f"    子频道抓取 {len(sub_articles)} 篇文章")
            else:
                print(f"    子频道无效或无文章: {sub_url}")

    print(f"总共爬取 {len(visited_articles)} 篇文章")

# -----------------------------
# 入口
# -----------------------------
if __name__ == "__main__":
    main()
    driver.quit()
