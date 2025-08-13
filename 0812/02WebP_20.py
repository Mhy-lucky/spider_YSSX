import json
import time
import os
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("02_log.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 设置Chrome无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome()

# 读取JSON关键词
with open('/Users/admin/爬虫实习/0811/keywords.json', 'r', encoding='utf-8') as file:
    keywords = json.load(file)

if not os.path.exists('images'):
    os.makedirs('images')



def search_and_download_images(keyword, max_images=20):
    logging.info(f"开始爬取关键词：{keyword}，目标图片数量：{max_images}")
    driver.get(f"https://huaban.com/search/?q={keyword}")
    time.sleep(3)  # 等待加载
    
    # 尽量滚动页面，加载更多图片
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
    
    downloaded_count = 0
    for i, img in enumerate(img_elements):
        if downloaded_count >= max_images:
            break
        img_url = img.get_attribute("src")
        if not img_url:
            logging.warning(f"图片元素{i}没有src属性，跳过。")
            continue
        
        if img_url.startswith("//"):
            img_url = "https:" + img_url

        img_name = os.path.join('images', f"{keyword}_{downloaded_count+1}.jpg")
        try:
            img_data = requests.get(img_url, timeout=10).content
            with open(img_name, 'wb') as f:
                f.write(img_data)
            logging.info(f"成功下载图片 {downloaded_count+1} ：{img_url}")
            downloaded_count += 1
        except Exception as e:
            logging.error(f"下载图片失败 {img_url}，错误：{e}")

    logging.info(f"关键词 {keyword} 下载完成，共下载 {downloaded_count} 张图片。")

for kw in keywords:
    search_and_download_images(kw, max_images=20)

driver.quit()
