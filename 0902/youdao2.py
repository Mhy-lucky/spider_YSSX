# -*- coding: utf-8 -*-
import sys
import os
import time
import random
import traceback
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementNotInteractableException, StaleElementReferenceException,
    NoSuchWindowException
)
import nltk

# 确保 punkt 分句器
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize

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
    driver = None
    try:
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
        driver.get("https://fanyi.youdao.com/#/TextTranslate")
        driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
        time.sleep(random.uniform(1, 2))
    except WebDriverException as e:
        print(f"❌ 浏览器初始化异常: {e}")
        traceback.print_exc()
        if driver:
            try: driver.quit()
            except: pass
        raise
    except Exception as e:
        print(f"❌ 未知浏览器异常: {e}")
        traceback.print_exc()
        if driver:
            try: driver.quit()
            except: pass
        raise
    return driver

# ---------------- 选择语言 ----------------
def select_language(driver, src_lang, tgt_lang):
    try:
        wait = WebDriverWait(driver, 20)
        src_code = LANG_MAP.get(src_lang.lower(), src_lang.lower())
        tgt_code = LANG_MAP.get(tgt_lang.lower(), tgt_lang.lower())

        src_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanFrom-container .lang-text-ai")))
        src_selector.click()
        src_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'div.language-item[data-code="{src_code}"]')))
        src_option.click()

        tgt_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanTo-container .lang-text-ai")))
        tgt_selector.click()
        tgt_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'div.language-item[data-code="{tgt_code}"]')))
        tgt_option.click()

        print(f"✅ 已选择源语言 {src_lang} -> {src_code}，目标语言 {tgt_lang} -> {tgt_code}")
    except (TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
        print(f"❌ 语言选择异常: {e}")
        traceback.print_exc()
        raise
    except Exception as e:
        print(f"❌ 未知语言选择异常: {e}")
        traceback.print_exc()
        raise

# ---------------- 输入与获取翻译 ----------------
def translate_text(driver, text):
    try:
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
            try:
                span = p.find_element(By.CSS_SELECTOR, "span.tgt")
                lines_translated.append(span.text)
            except Exception as e_inner:
                print(f"❌ 某行提取翻译异常: {e_inner}")
                traceback.print_exc()
                lines_translated.append("")
        return lines_translated
    except (TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
        print(f"❌ 翻译异常: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"❌ 未知翻译异常: {e}")
        traceback.print_exc()
        return None

# ---------------- 保存结果 ----------------
def append_to_file(pairs, output_file):
    try:
        with open(output_file, "a", encoding="utf-8") as f:
            for original, translated in pairs:
                f.write(f"{original}\t{translated}\n")
    except (OSError, IOError) as e:
        print(f"❌ 写入文件异常: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 未知写入异常: {e}")
        traceback.print_exc()

# ---------------- 记录已处理的行 ----------------
def load_processed_lines(processed_file):
    try:
        if os.path.exists(processed_file):
            with open(processed_file, "r", encoding="utf-8") as f:
                return set(f.read().splitlines())
        return set()
    except Exception as e:
        print(f"❌ 读取已处理文件异常: {e}")
        traceback.print_exc()
        return set()

def save_processed_lines(processed_lines, processed_file):
    try:
        with open(processed_file, "w", encoding="utf-8") as f:
            f.write("\n".join(processed_lines))
    except Exception as e:
        print(f"❌ 保存已处理文件异常: {e}")
        traceback.print_exc()

# ---------------- 主程序 ----------------
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("用法: python script.py inputfile outputfile 源语言 目标语言")
        sys.exit(1)

    INPUT_FILE = sys.argv[1]
    OUTPUT_FILE = sys.argv[2]
    src_lang_input = sys.argv[3]
    tgt_lang_input = sys.argv[4]

    processed_lines = load_processed_lines(PROCESSED_FILE)
    chromedriver_autoinstaller.install()

    driver = None
    no_new_content_logged = False  # 循环外定义一次

    while True:
        try:
            # 初始化浏览器
            if not driver:
                try:
                    driver = init_driver()
                    select_language(driver, src_lang_input, tgt_lang_input)
                except Exception:
                    print("❌ 浏览器启动或语言选择失败，5秒后重试...")
                    time.sleep(5)
                    continue

            # 检查输入文件
            if not os.path.exists(INPUT_FILE):
                time.sleep(CHECK_INTERVAL)
                continue

            try:
                with open(INPUT_FILE, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"❌ 读取输入文件异常: {e}")
                traceback.print_exc()
                time.sleep(CHECK_INTERVAL)
                continue


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
                            if translated_lines and len(translated_lines) == len(batch):
                                append_to_file(list(zip(batch, translated_lines)), OUTPUT_FILE)
                                processed_lines.update(batch)
                                save_processed_lines(processed_lines, PROCESSED_FILE)
                            else:
                                print(f"⚠️ 本批次行数不匹配，丢弃 {len(batch)} 行内容")
                        except Exception as e:
                            print(f"❌ 本批次翻译失败: {e}")
                            traceback.print_exc()
                            try:
                                driver.quit()
                            except: pass
                            driver = None
                        batch = [chunk]
                        batch_len = len(chunk)
                    else:
                        batch.append(chunk)
                        batch_len += len(chunk)

            if batch:
                try:
                    translated_lines = translate_text(driver, "\n".join(batch))
                    if translated_lines and len(translated_lines) == len(batch):
                        append_to_file(list(zip(batch, translated_lines)), OUTPUT_FILE)
                        processed_lines.update(batch)
                        save_processed_lines(processed_lines, PROCESSED_FILE)
                    else:
                        print(f"⚠️ 本批次行数不匹配，丢弃 {len(batch)} 行内容")
                except Exception as e:
                    print(f"❌ 本批次翻译失败: {e}")
                    traceback.print_exc()
                    try:
                        driver.quit()
                    except: pass
                    driver = None

            print(f"✅ 已翻译并追加 {len(new_lines)} 条新内容到 {OUTPUT_FILE}")
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("🛑 程序手动停止")
            if driver:
                try: driver.quit()
                except: pass
            break
        except NoSuchWindowException as e:
            print(f"❌ 浏览器异常关闭: {e}")
            traceback.print_exc()
            try:
                if driver:
                    driver.quit()
            except: pass
            driver = None
            time.sleep(5)
        except Exception as e:
            print(f"❌ 主循环未知异常: {e}")
            traceback.print_exc()
            try:
                if driver:
                    driver.quit()
            except: pass
            driver = None
            time.sleep(CHECK_INTERVAL)
