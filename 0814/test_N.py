import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- 配置 ----------------
INPUT_FILE = "/Users/admin/Desktop/爬虫实习/0814/input.txt"
OUTPUT_FILE = "niutrans_results.txt"
CHECK_INTERVAL = 10
MAX_WORDS = 600
MAX_LINES = 10

# ---------------- 浏览器初始化 ----------------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://niutrans.com/trans?type=text")
    time.sleep(3)
    return driver

# ---------------- 输入输出函数 ----------------
def set_source_text(driver, text, timeout=15):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            input_box = driver.find_element(By.CSS_SELECTOR, "textarea#sourceText")
            input_box.clear()
            input_box.send_keys(text)
            return
        except:
            time.sleep(0.2)
    raise Exception("未找到输入框")

def get_translated_text(driver, timeout=30):
    # Niutrans 翻译可能需要一点时间
    end_time = time.time() + timeout
    prev_text = ""
    while time.time() < end_time:
        try:
            output_box = driver.find_element(By.CSS_SELECTOR, "textarea#targetText")
            text = output_box.get_attribute("value").strip()
            if text and text == prev_text:
                return text
            prev_text = text
        except:
            pass
        time.sleep(0.5)
    return "无法获取翻译结果"

def select_language(driver, src_lang, tgt_lang):
    # Niutrans 默认界面有两个下拉选择源语言和目标语言
    try:
        src_select = driver.find_element(By.CSS_SELECTOR, "select#sourceLang")
        src_select.send_keys(src_lang)
        tgt_select = driver.find_element(By.CSS_SELECTOR, "select#targetLang")
        tgt_select.send_keys(tgt_lang)
    except:
        print("⚠️ 语言选择失败，使用默认语言")

def translate_niutrans(driver, text, src_lang, tgt_lang):
    select_language(driver, src_lang, tgt_lang)
    set_source_text(driver, text)
    # Niutrans 有一个翻译按钮
    try:
        translate_btn = driver.find_element(By.CSS_SELECTOR, "button#btnTranslate")
        translate_btn.click()
    except:
        pass
    return get_translated_text(driver)

# ---------------- 保存函数 ----------------
def append_to_file(original, translated):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(original.strip() + "\n\n")
        f.write(translated.strip() + "\n\n")

# ---------------- 无限循环 ----------------
if __name__ == "__main__":
    src_lang = input("请输入源语言缩写（如 zh/en/ja）：").strip()
    tgt_lang = input("请输入目标语言缩写（如 en/zh/ja）：").strip()

    processed_lines = set()
    driver = init_driver()
    print(f"🟢 监控 {INPUT_FILE}，每批次最多 {MAX_WORDS} 词或 {MAX_LINES} 条...")

    while True:
        try:
            if not os.path.exists(INPUT_FILE):
                time.sleep(CHECK_INTERVAL)
                continue

            with open(INPUT_FILE, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            new_lines = [line for line in lines if line not in processed_lines]
            if not new_lines:
                time.sleep(CHECK_INTERVAL)
                continue

            batch = []
            batch_words = 0
            for line in new_lines:
                words = len(line.split())
                if batch_words + words > MAX_WORDS or len(batch) >= MAX_LINES:
                    translated = translate_niutrans(driver, "\n".join(batch), src_lang, tgt_lang)
                    append_to_file("\n".join(batch), translated)
                    processed_lines.update(batch)
                    batch = [line]
                    batch_words = words
                else:
                    batch.append(line)
                    batch_words += words

            if batch:
                translated = translate_niutrans(driver, "\n".join(batch), src_lang, tgt_lang)
                append_to_file("\n".join(batch), translated)
                processed_lines.update(batch)

            print(f"✅ 已翻译并追加 {len(new_lines)} 条新内容到 {OUTPUT_FILE}")
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("🛑 程序手动停止")
            break
        except Exception as e:
            print(f"❌ 程序出错: {e}")
            print(traceback.format_exc())
            time.sleep(CHECK_INTERVAL)

    if driver:
        driver.quit()
        print("🛑 浏览器已关闭")
