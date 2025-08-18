from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

# ---------- 初始化浏览器 ----------
driver = webdriver.Chrome()
driver.get("https://translate.volcengine.com")  # 替换为实际网址
wait = WebDriverWait(driver, 15)
time.sleep(3)  # 等待页面加载完成

# ---------- 点击目标语言框 ----------
target_dropdown = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "div.select-lan-box > div.sc-dmctIk.iAAovA:last-child")
))
target_dropdown.click()

# ---------- 滚动并选择目标语言 ----------
target_lang_code = "ja"  # 日语
lang_list_container = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, "div.lang-content")
))

found = False
scroll_attempts = 0
while not found and scroll_attempts < 30:
    lang_items = lang_list_container.find_elements(By.CSS_SELECTOR, "div.lang-item")
    for item in lang_items:
        if item.get_attribute("data-lang") == target_lang_code:
            target_option = item
            found = True
            break
    if not found:
        driver.execute_script("arguments[0].scrollTop += 100;", lang_list_container)
        time.sleep(0.3)
        scroll_attempts += 1

if not found:
    raise Exception(f"目标语言 {target_lang_code} 未找到")

# 点击目标语言
ActionChains(driver).move_to_element(target_option).click(target_option).perform()

# ---------- 输入文本 ----------
input_box = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, "div.input-box div.slate-editor[contenteditable='true']")
))

text_to_translate = "今天天气很好。"

# 清空输入框
input_box.click()
ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
time.sleep(0.3)

# 逐字输入，延长间隔确保前端处理
for c in text_to_translate:
    input_box.send_keys(c)
    time.sleep(0.3)  # 0.3秒间隔

# 输入完成后触发 blur，让前端发送翻译请求
driver.execute_script("arguments[0].blur();", input_box)
time.sleep(1)  # 等待前端处理事件

# ---------- 获取翻译结果 ----------
output_box = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, "div.slate-editor[contenteditable='false']")
))

# 等待翻译结果稳定
translated_text = ""
previous_text = ""
for _ in range(40):  # 最多等待 20 秒
    spans = output_box.find_elements(By.CSS_SELECTOR, "span[data-slate-string]")
    translated_text = "".join([s.text for s in spans])
    if translated_text.strip() and translated_text == previous_text:
        break  # 稳定输出
    previous_text = translated_text
    time.sleep(0.5)

print("翻译结果:", translated_text)

driver.quit()
