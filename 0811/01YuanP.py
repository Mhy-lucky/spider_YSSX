import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# 读取关键词
with open("keywords.json", "r", encoding="utf-8") as f:
    keywords = json.load(f)

# 创建图片文件夹
if not os.path.exists("images"):
    os.makedirs("images")

# 初始化webdriver
driver = webdriver.Chrome()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

for keyword in keywords:
    print(f"\n正在爬取：{keyword}")
    search_url = f"https://huaban.com/search?type=material&q={keyword}"
    driver.get(search_url)
    time.sleep(5)

    # 获取搜索页所有图片详情页链接
    links = driver.find_elements(By.CSS_SELECTOR, "a.__7D5D_BHJ")  

    if not links:
        print(f"❌ 未找到详情页链接：{keyword}")
        continue

    # 提取href链接，避免元素失效
    detail_urls = []
    for link in links[:5]:  # 只取前5个，按需调整
        href = link.get_attribute("href")
        if href and not href.startswith("http"):
            href = "https://huaban.com" + href
        detail_urls.append(href)

    # 访问详情页并下载高清图
    for i, detail_url in enumerate(detail_urls):
        print(f"访问详情页 {i+1}: {detail_url}")
        driver.get(detail_url)
        time.sleep(5)

        try:
            img_elem = driver.find_element(By.CSS_SELECTOR, "img.transparent-img-bg")
            img_url = img_elem.get_attribute("src") 

            if img_url.startswith("//"):
                img_url = "https:" + img_url

            print(f"高清图片链接：{img_url}")

            response = requests.get(img_url, headers={
                "User-Agent": headers["User-Agent"],
                "Referer": detail_url
            })

            if response.status_code == 200:
                file_path = os.path.join("images", f"{keyword}_{i+1}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ 保存成功: {file_path}")
            else:
                print(f"❌ 请求图片失败，状态码：{response.status_code}")

        except Exception as e:
            print(f"❌ 详情页图片获取或下载失败：{e}")

driver.quit()
print("🎉 爬取完成！")
