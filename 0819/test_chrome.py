from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import shutil
import sys
import os

def init_headless_chrome():
    # 手动指定 chromedriver 路径（假设已安装）
    # Linux 服务器常见路径
    chromedriver_path = "/usr/bin/chromedriver"
    chrome_path = "/usr/bin/google-chrome"  # 如果是 Chromium，可以改为 /usr/bin/chromium-browser

    # 检查路径是否存在
    if not os.path.exists(chromedriver_path):
        print(f"❌ chromedriver 未找到: {chromedriver_path}")
        sys.exit(1)
    if not os.path.exists(chrome_path):
        print(f"❌ Chrome/Chromium 未找到: {chrome_path}")
        sys.exit(1)

    options = Options()
    options.binary_location = chrome_path
    options.add_argument("--headless=new")       # 无头模式
    options.add_argument("--no-sandbox")         # 服务器推荐
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=VizDisplayCompositor")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 使用示例
if __name__ == "__main__":
    driver = init_headless_chrome()
    driver.get("https://fanyi.sogou.com/")
    print("✅ 页面打开成功")
    driver.quit()
