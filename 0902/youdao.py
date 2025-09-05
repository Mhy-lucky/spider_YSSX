# -*- coding: utf-8 -*-
import sys
import os
import time
import random
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchWindowException


# ---------------- 语言映射 ----------------
LANG_MAP = {
    "zh": "zh-CHS",
    "en": "en",
    "ja": "ja",
    "th": "th",
    "ko": "ko",
    "ar": "ar",
    "de": "de",
    "ru": "ru",
    "fr": "fr",
    "nl": "nl",
    "pt": "pt",
    "es": "es",
    "it": "it",
    "vi": "vi",
    "id": "id"
}

# ---------------- 配置 ----------------
CHECK_INTERVAL = 10
MAX_CHARS = 4500
PROCESSED_FILE = "processed_lines.txt"

# ---------------- 浏览器初始化 ----------------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument("--remote-debugging-port=9222")  

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://fanyi.youdao.com/#/TextTranslate")
    except Exception as e:
        print(f"页面加载超时: {e}")
        time.sleep(5)

    try:
        driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
    except Exception:
        pass
    time.sleep(random.uniform(1, 2))
    return driver

# ---------------- 浏览器重启 ----------------
def restart_driver(driver, src_lang, tgt_lang):
    try:
        if driver:
            driver.quit()
    except Exception:
        pass
    time.sleep(2)  # 等待短暂时间再重启
    driver = init_driver()
    select_language(driver, src_lang, tgt_lang)
    return driver

# ---------------- 选择语言 ----------------
def select_language(driver, src_lang, tgt_lang):
    wait = WebDriverWait(driver, 20)
    src_code = LANG_MAP.get(src_lang.lower(), src_lang.lower())
    tgt_code = LANG_MAP.get(tgt_lang.lower(), tgt_lang.lower())

    src_selector = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".lang-container.lanFrom-container .lang-text-ai")
    ))
    src_selector.click()
    src_option = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f'div.language-item[data-code="{src_code}"]')
    ))
    src_option.click()

    tgt_selector = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".lang-container.lanTo-container .lang-text-ai")
    ))
    tgt_selector.click()
    tgt_option = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f'div.language-item[data-code="{tgt_code}"]')
    ))
    tgt_option.click()

# ---------------- 输入与获取翻译 ----------------
def translate_text(driver, text):
    wait = WebDriverWait(driver, 20)
    input_box = wait.until(EC.visibility_of_element_located((By.ID, "js_fanyi_input")))
    
    input_box.clear()
    input_box.send_keys(text)
    input_box.send_keys(Keys.RETURN)
    
    time.sleep(random.uniform(3, 6))
    
    output_box = wait.until(EC.visibility_of_element_located((By.ID, "js_fanyi_output_resultOutput")))
    lines_translated = []
    paragraphs = output_box.find_elements(By.CSS_SELECTOR, "p.tgt")
    for p in paragraphs:
        span = p.find_element(By.CSS_SELECTOR, "span.tgt")
        lines_translated.append(span.text)
    return lines_translated

# ---------------- 保存结果 ----------------
def append_to_file(pairs):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for original, translated in pairs:
            f.write(f"{original}\t{translated}\n")

# ---------------- 记录已处理的行 ----------------
def load_processed_lines():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_processed_lines(processed_lines):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(processed_lines))

# ---------------- 主程序 ----------------
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("用法: python script.py inputfile outputfile 源语言 目标语言")
        sys.exit(1)

    INPUT_FILE = sys.argv[1]
    OUTPUT_FILE = sys.argv[2]
    src_lang_input = sys.argv[3]
    tgt_lang_input = sys.argv[4]

    processed_lines = load_processed_lines()
    chromedriver_autoinstaller.install()
    driver = init_driver()
    select_language(driver, src_lang_input, tgt_lang_input)

    print(f"🟢 程序启动，监控 {INPUT_FILE}，每批次最多 {MAX_CHARS} 字符...")

    no_new_content_logged = False

while True:
    try:
        if not os.path.exists(INPUT_FILE):
            time.sleep(CHECK_INTERVAL)
            continue

        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        new_lines = [line for line in lines if line not in processed_lines]
        if not new_lines:
            if not no_new_content_logged:
                print("无新内容，等待中...")
                no_new_content_logged = True
            time.sleep(CHECK_INTERVAL)
            continue
        else:
            no_new_content_logged = False

        batch, batch_len = [], 0
        for line in new_lines:
            chunks = [line] if len(line) <= MAX_CHARS else [line[i:i+MAX_CHARS] for i in range(0, len(line), MAX_CHARS)]
            for chunk in chunks:
                if batch_len + len(chunk) > MAX_CHARS:
                    try:
                        translated_lines = translate_text(driver, "\n".join(batch))
                    except (WebDriverException, NoSuchWindowException):
                        print("⚠️ 浏览器异常，正在重启...")
                        driver = restart_driver(driver, src_lang_input, tgt_lang_input)
                        translated_lines = translate_text(driver, "\n".join(batch))

                    if len(translated_lines) == len(batch):
                        append_to_file(list(zip(batch, translated_lines)))
                        processed_lines.update(batch)
                        save_processed_lines(processed_lines)
                    else:
                        print(f"⚠️ 本批次行数不匹配，丢弃 {len(batch)} 行内容")
                    batch = [chunk]
                    batch_len = len(chunk)
                else:
                    batch.append(chunk)
                    batch_len += len(chunk)

        if batch:
            try:
                translated_lines = translate_text(driver, "\n".join(batch))
            except (WebDriverException, NoSuchWindowException):
                print("⚠️ 浏览器异常，正在重启...")
                driver = restart_driver(driver, src_lang_input, tgt_lang_input)
                translated_lines = translate_text(driver, "\n".join(batch))

            if len(translated_lines) == len(batch):
                append_to_file(list(zip(batch, translated_lines)))
                processed_lines.update(batch)
                save_processed_lines(processed_lines)
            else:
                print(f"⚠️ 本批次行数不匹配，丢弃 {len(batch)} 行内容")

        print(f"✅ 已翻译并追加 {len(new_lines)} 条新内容到 {OUTPUT_FILE} 请追加需翻译的新内容到 {INPUT_FILE}")
        time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("🛑 程序手动停止")
        break
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        driver = restart_driver(driver, src_lang_input, tgt_lang_input)
        time.sleep(CHECK_INTERVAL)