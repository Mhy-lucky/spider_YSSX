import json
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 设置Chrome无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
chrome_options.add_argument("--no-sandbox")  # 防止沙盒问题

# 启动浏览器
driver = webdriver.Chrome()

# 读取JSON文件，提取关键词
with open('/Users/admin/爬虫实习/0811/keywords.json', 'r', encoding='utf-8') as file:
    keywords = json.load(file)


# 创建文件夹来存储图片
if not os.path.exists('downloaded_images'):
    os.makedirs('downloaded_images')

# 用于搜索和下载图片的函数
def search_and_download_images(keyword):
    driver.get(f"https://huaban.com/search/?q={keyword}")  # 替换成花瓣网的搜索URL
    
    time.sleep(3)  # 等待页面加载完成
    
    # 找到图片
    img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.transparent-img-bg')
    
    if img_elements:
        # 获取第一张图片的URL
        img_url = img_elements[0].get_attribute("src")
        
        # 如果图片URL以'//'开头，补全为完整的URL
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        
        # 保存图片
        img_name = os.path.join('downloaded_images', f"{keyword}.jpg")
        img_data = requests.get(img_url).content
        with open(img_name, 'wb') as file:
            file.write(img_data)
        print(f"图片已保存: {img_name}")
    else:
        print(f"未找到与'{keyword}'相关的图片。")

# 为每个关键词搜索并下载图片
for keyword in keywords:
    search_and_download_images(keyword)

# 关闭浏览器
driver.quit()
