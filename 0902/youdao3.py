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
        print("正在初始化浏览器...")
        options = Options()
        options.add_argument('--headless')  # 可根据需求选择启用或禁用 headless 模式
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)
        driver.get("https://fanyi.youdao.com/#/TextTranslate")
        driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
        time.sleep(random.uniform(1, 2))
        print("浏览器初始化完成。")
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
        print(f"正在选择源语言：{src_lang} 和目标语言：{tgt_lang}")
        wait = WebDriverWait(driver, 20)
        src_code = LANG_MAP.get(src_lang.lower(), src_lang.lower())
        tgt_code = LANG_MAP.get(tgt_lang.lower(), tgt_lang.lower())

        print(f"选择源语言代码：{src_code}，目标语言代码：{tgt_code}")

        # 选择源语言
        src_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanFrom-container .lang-text-ai")))
        src_selector.click()
        src_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'div.language-item[data-code="{src_code}"]')))
        src_option.click()

        # 选择目标语言
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
        print(f"正在翻译的文本: {text}")  # 打印将要翻译的文本
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
        
        print(f"翻译结果: {lines_translated}")  # 打印翻译后的结果
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
        print(f"正在写入文件 {output_file}...")
        with open(output_file, "a", encoding="utf-8") as f:
            for original, translated in pairs:
                print(f"写入: {original} -> {translated}")  # 打印每行写入内容
                f.write(f"{original}\t{translated}\n")
        print("写入完成。")
    except (OSError, IOError) as e:
        print(f"❌ 写入文件异常: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 未知写入异常: {e}")
        traceback.print_exc()

# ---------------- 记录已处理的行 ----------------
def load_processed_lines(processed_file):
    try:
        print(f"加载已处理的行 {processed_file}...")
        if os.path.exists(processed_file):
            with open(processed_file, "r", encoding="utf-8") as f:
                processed_lines = set(f.read().splitlines())
                print(f"已处理的行数: {len(processed_lines)}")
                return processed_lines
        return set()
    except Exception as e:
        print(f"❌ 读取已处理文件异常: {e}")
        traceback.print_exc()
        return set()

def save_processed_lines(processed_lines, processed_file):
    try:
        print(f"保存已处理的行 {processed_file}...")
        with open(processed_file, "w", encoding="utf-8") as f:
            f.write("\n".join(processed_lines))
        print(f"已处理行数保存成功: {len(processed_lines)}")
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
            print("正在检查输入文件...")
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
                print(f"❌ 输入文件 {INPUT_FILE} 不存在，等待中...")
                time.sleep(CHECK_INTERVAL)
                continue

            with open(INPUT_FILE, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"读取到 {len(lines)} 行待翻译的内容。")

            # 处理新的内容
            new_lines = [line for line in lines if line not in processed_lines]
            if not new_lines:
                if not no_new_content_logged:
                    print("无新内容，等待中...")
                    no_new_content_logged = True
                time.sleep(CHECK_INTERVAL)
                continue
            else:
                no_new_content_logged = False

            print(f"将翻译 {len(new_lines)} 行新的内容。")
            batch, batch_len = [], 0
            for line in new_lines:
                chunks = [line] if len(line) <= MAX_CHARS else [line[i:i+MAX_CHARS] for i in range(0, len(line), MAX_CHARS)]
                for chunk in chunks:
                    if batch_len + len(chunk) > MAX_CHARS:
                        try:
                            translated_lines = translate_text(driver, "\n".join(batch))
                            if translated_lines:
                                append_to_file(list(zip(batch, translated_lines)), OUTPUT_FILE)
                                processed_lines.update(batch)
                                save_processed_lines(processed_lines, PROCESSED_FILE)
                            else:
                                print(f"❌ 本批次翻译失败，丢弃 {len(batch)} 行内容")
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
                    if translated_lines:
                        append_to_file(list(zip(batch, translated_lines)), OUTPUT_FILE)
                        processed_lines.update(batch)
                        save_processed_lines(processed_lines, PROCESSED_FILE)
                    else:
                        print(f"❌ 本批次翻译失败，丢弃 {len(batch)} 行内容")
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
