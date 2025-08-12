import json
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_log.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Chrome无头配置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome()

# 读取JSON关键词，只取前10个
with open('/Users/admin/Desktop/爬虫实习/0811/keywords.json', 'r', encoding='utf-8') as file:
    keywords = json.load(file)

output_file = "image_urls.txt"

# 用于保存图片URL
def save_urls(keyword, urls):
    with open(output_file, 'a', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{keyword}\t{url}\n")

def crawl_urls(keyword, max_images=20):
    logging.info(f"开始爬取关键词：{keyword}，目标图片数量：{max_images}")

    # 构建包含筛选条件的 URL
    search_url = f"https://huaban.com/search?q={keyword}&sort=all&type=material&filter_ids=material_category-5342726.5342727%3Amaterial_category%3A%E9%AB%98%E7%AB%AF%E5%85%8D%E6%8A%A0&original={keyword}"
    driver.get(search_url)
    time.sleep(3)

    # 滚动加载更多图片
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.transparent-img-bg')
    urls = []
    count = 0
    for img in img_elements:
        if count >= max_images:
            break
        img_url = img.get_attribute("src")
        if not img_url:
            continue
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        urls.append(img_url)
        count += 1

    logging.info(f"关键词 {keyword} 找到 {len(urls)} 张图片URL")
    save_urls(keyword, urls)

for kw in keywords:
    crawl_urls(kw)

driver.quit()
logging.info("爬取完成，所有图片URL已保存到 " + output_file)
