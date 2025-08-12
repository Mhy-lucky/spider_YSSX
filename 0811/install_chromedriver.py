import chromedriver_autoinstaller
import os
import sys

# 自动下载并安装对应版本的 chromedriver
chromedriver_path = chromedriver_autoinstaller.install()

# 将 chromedriver 路径添加到环境变量
if chromedriver_path:
    os.environ["PATH"] += os.pathsep + os.path.dirname(chromedriver_path)

# 可选：测试 chromedriver 是否可用
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    print("chromedriver 安装并配置成功！")
    driver.quit()
except Exception as e:
    print("chromedriver 配置失败:", e)
    sys.exit(1)