'''最初版demo，固定输入和目标语言'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ---------------- 配置 ----------------
URL = "https://fanyi.sogou.com"
TEXT_TO_TRANSLATE = "今天天气下雨"
TARGET_LANG_CODE = "de"
OUTPUT_FILE = "translation.txt"

# ---------------- 初始化浏览器 ----------------
driver = webdriver.Chrome()
driver.get(URL)
wait = WebDriverWait(driver, 10)

# ---------------- 输入文本 ----------------
text_input = wait.until(EC.element_to_be_clickable((By.ID, "trans-input")))
text_input.click()
text_input.clear()
text_input.send_keys(TEXT_TO_TRANSLATE)

# ---------------- 选择目标语言 ----------------
tl_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".tl-selector .text")))
tl_selector.click()
time.sleep(0.5)

# 根据首字母选择语言分组
first_letter = TARGET_LANG_CODE[0].upper()
try:
    letter_span = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f".letter.langSelectList-char#{first_letter}")
    ))
    letter_span.click()
    time.sleep(0.2)
except:
    pass

# 点击具体语言
lang_span = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, f".langs span[lang='{TARGET_LANG_CODE}']")
))
lang_span.click()
time.sleep(0.5)

# ---------------- 获取翻译结果 ----------------
def get_translation(driver, max_wait=15):
    start = time.time()
    while time.time() - start < max_wait:
        try:
            el = driver.find_element(By.ID, "trans-result")
            text = el.text.strip()
            if text:
                return text
        except:
            pass
        time.sleep(0.2)
    return ""

result_text = get_translation(driver, max_wait=15)
if result_text:
    print("翻译结果:", result_text)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(result_text)
else:
    print("翻译超时或未获取到结果")

driver.quit()
