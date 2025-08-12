import os
import time
import json
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By

# 配置日志，日志文件 spider.log 会保存在当前目录
logging.basicConfig(
    filename='spider.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 读取关键词
try:
    with open("/Users/admin/爬虫实习/0811/keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)
    logging.info("成功读取关键词文件 keywords.json")
except Exception as e:
    logging.error(f"读取关键词文件失败：{e}")
    raise

# 创建图片文件夹
if not os.path.exists("images"):
    os.makedirs("images")
    logging.info("创建图片保存文件夹 images")

# 初始化webdriver
driver = webdriver.Chrome()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

for keyword in keywords:
    logging.info(f"开始爬取关键词：{keyword}")
    print(f"正在爬取：{keyword}")
    search_url = f"https://huaban.com/search?type=material&q={keyword}"
    driver.get(search_url)
    time.sleep(5)

    links = driver.find_elements(By.CSS_SELECTOR, "a.__7D5D_BHJ")  

    if not links:
        logging.warning(f"关键词[{keyword}]未找到详情页链接")
        print(f"❌ 未找到详情页链接：{keyword}")
        continue

    detail_urls = []
    for link in links[:5]:
        href = link.get_attribute("href")
        if href and not href.startswith("http"):
            href = "https://huaban.com" + href
        detail_urls.append(href)

    for i, detail_url in enumerate(detail_urls):
        logging.info(f"访问详情页 {i+1}: {detail_url}")
        print(f"访问详情页 {i+1}: {detail_url}")
        driver.get(detail_url)
        time.sleep(5)

        try:
            img_elem = driver.find_element(By.CSS_SELECTOR, "img.transparent-img-bg")
            img_url = img_elem.get_attribute("srcset")

            if img_url.startswith("//"):
                img_url = "https:" + img_url

            logging.info(f"获取到高清图片链接：{img_url}")
            print(f"高清图片链接：{img_url}")

            response = requests.get(img_url, headers={
                "User-Agent": headers["User-Agent"],
                "Referer": detail_url
            })

            if response.status_code == 200:
                file_path = os.path.join("images", f"{keyword}_{i+1}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                logging.info(f"图片保存成功：{file_path}")
                print(f"✅ 保存成功: {file_path}")
            else:
                logging.error(f"请求图片失败，状态码：{response.status_code}，链接：{img_url}")
                print(f"❌ 请求图片失败，状态码：{response.status_code}")

        except Exception as e:
            logging.error(f"详情页图片获取或下载失败，关键词[{keyword}], 详情页[{detail_url}]，错误：{e}")
            print(f"❌ 详情页图片获取或下载失败：{e}")

driver.quit()
logging.info("爬取任务完成")
print("🎉 爬取完成！")
