from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

# 手动指定 chromedriver 路径
chromedriver_path = "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/chromedriver_autoinstaller/139/chromedriver"

# 设置浏览器选项
chrome_options = Options()
# chrome_options.add_argument('--headless')  # 无界面模式
chrome_options.add_argument('--disable-gpu')  # 禁用GPU
chrome_options.add_argument('--no-sandbox')  # 解决某些环境下的错误
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  # 伪装成真实用户

# 使用 Service 来指定 chromedriver 路径
service = Service(executable_path=chromedriver_path)

# 启动 WebDriver 并指定 chromedriver 路径
driver = webdriver.Chrome(service=service, options=chrome_options)

# 设置最大超时时间（页面加载时的超时设置）
driver.set_page_load_timeout(120)  # 设置页面加载的超时时间为120秒

# 打开有道翻译页面
url = "https://fanyi.youdao.com/#/TextTranslate"
try:
    driver.get(url)
except Exception as e:
    print(f"页面加载超时: {e}")
    driver.quit()
    exit()

# 使用 WebDriverWait 等待页面上的元素加载完成
wait = WebDriverWait(driver, 20)  # 等待 20 秒

try:
    # 等待源语言选择框加载完毕并点击源语言选择框
    source_language_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanFrom-container .lang-text-ai")))
    source_language_selector.click()

    # 选择泰语（源语言）
    thai_language = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-code="zh-CHS"]')))
    thai_language.click()

    # 等待目标语言选择框加载完毕并点击目标语言选择框
    target_language_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanTo-container .lang-text-ai")))
    target_language_selector.click()

    # 选择中文（目标语言）
    chinese_language = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-code="th"]')))
    chinese_language.click()

    # 等待输入框加载完毕
    input_box = wait.until(EC.visibility_of_element_located((By.ID, "js_fanyi_input")))

    # 输入待翻译内容
    input_box.clear()  # 清空输入框
    input_box.send_keys("今天天气真好")  # 输入待翻译内容
    input_box.send_keys(Keys.RETURN)  # 模拟按回车键进行翻译

    # 等待翻译结果加载
    time.sleep(random.uniform(5, 7))  # 随机延时，模拟用户操作

    # 获取翻译结果
    output_box = driver.find_element(By.ID, "js_fanyi_output_resultOutput")
    translated_texts = output_box.find_elements(By.CSS_SELECTOR, "span.tgt")

    # 获取原文和翻译文
    original_text = input_box.text
    translated_text = "\n".join([span.text for span in translated_texts])

    # 输出原文和翻译
    print(f"原文: {original_text}")
    print(f"翻译: {translated_text}")

    # 将原文和翻译结果保存到文件
    OUTPUT_FILE = "translation_results.txt"

    def append_to_file(pairs):
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for original, translated in pairs:
                f.write(f"{original}\t{translated}\n")

    # 保存原文和翻译结果到文件
    append_to_file([(original_text, translated_text)])

except Exception as e:
    print(f"出现错误: {e}")

finally:
    # 关闭浏览器
    driver.quit()
