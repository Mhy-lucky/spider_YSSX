from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# ---------------- 配置 ----------------
# INPUT_FILE = "/Users/admin/Desktop/爬虫实习/0814/input.txt"
# OUTPUT_FILE = "trans.txt"

INPUT_FILE =  "/home/maohongyao/pro/code/deepl/input.txt"
OUTPUT_FILE = "/home/maohongyao/pro/code/deepl/trans.txt"


CHECK_INTERVAL = 10     # 秒，每隔多少秒检查新内容
MAX_CHARS = 1500        # 每批次最大字符数

# ---------------- 浏览器初始化 ----------------
def init_driver():
    options = Options()
    options.binary_location = "/home/maohongyao/chrome/opt/google/chrome/chrome" 
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service("/home/maohongyao/chrome/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.deepl.com/translator")
    time.sleep(3)
    # 尝试关闭 cookie 横幅
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "div[data-testid*='cookie-banner'] button")
        )
        cookie_button.click()
    except:
        pass
    return driver

# ---------------- 选择目标语言 ----------------
def select_target_language(driver, tgt_lang):
    """
    tgt_lang 例子：
    en-US, zh-Hans, zh-Hant, ja, fr, de ...
    """
    try:
        # 打开语言选择下拉
        lang_btn = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "button[data-testid='translator-target-lang-btn']")
        )
        driver.execute_script("arguments[0].click();", lang_btn)  # ✅ execute_script 点击稳定

        # 点击指定语言
        lang_option = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, f"//button[@data-testid='translator-lang-option-{tgt_lang}']")
        )
        driver.execute_script("arguments[0].click();", lang_option)  # ✅ execute_script 点击稳定
        print(f"🎯 已选择目标语言：{tgt_lang}")
    except Exception as e:
        print(f"❌ 选择目标语言失败: {e}")

# ---------------- 输入输出函数 ----------------
def set_source_text(driver, text, timeout=15):
    input_div = WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(By.CSS_SELECTOR,
            'd-textarea[data-testid="translator-source-input"] div[contenteditable="true"]')
    )
    driver.execute_script("""
        let div = arguments[0];
        div.focus();
        div.innerText = '';
        div.dispatchEvent(new Event('input', { bubbles: true }));
        div.innerText = arguments[1];
        div.dispatchEvent(new Event('input', { bubbles: true }));
    """, input_div, text)

def get_translated_text(driver, timeout=60):
    prev_text = ""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            output_div = driver.find_element(By.CSS_SELECTOR,
                'd-textarea[data-testid="translator-target-input"] div[contenteditable="true"]')
            ps = output_div.find_elements(By.TAG_NAME, "p")
            text = "\n".join([p.text for p in ps if p.text])
            if text and text == prev_text:
                return text
            prev_text = text
        except:
            pass
        time.sleep(0.5)
    return "无法获取翻译结果"

# ---------------- 保存函数 ----------------
def append_to_file(original, translated):
    orig_lines = original.strip().split("\n")
    trans_lines = translated.strip().split("\n")
    min_len = min(len(orig_lines), len(trans_lines))

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for i in range(min_len):
            f.write(orig_lines[i].strip() + "\t" + trans_lines[i].strip() + "\n\n")

# ---------------- 翻译前清空输出 ----------------
def clear_output(driver):
    try:
        output_div = driver.find_element(By.CSS_SELECTOR,
            'd-textarea[data-testid="translator-target-input"] div[contenteditable="true"]')
        driver.execute_script("arguments[0].innerText='';", output_div)
    except:
        pass

# ---------------- 段落拆分（单段落超长，按字符数，保持单词完整） ----------------
def split_long_paragraph_by_chars(paragraph, max_chars):
    words = paragraph.split(" ")
    chunks, current, length = [], [], 0

    for w in words:
        if length + len(w) + (1 if current else 0) <= max_chars:
            current.append(w)
            length += len(w) + (1 if current else 0)
        else:
            chunks.append(" ".join(current))
            current = [w]
            length = len(w)
    if current:
        chunks.append(" ".join(current))

    return chunks

# ---------------- 无限循环翻译 ----------------
if __name__ == "__main__":
    print("请输入要翻译文件的正确路径！Ctrl+C 退出")
    tgt_lang = input("请输入目标语言缩写（如：en-US/zh-Hans/zh-Hant/ja）：").strip()

    processed_lines = set()
    driver = None
    print(f"🟢 程序启动，监控 {INPUT_FILE}，每批次最多 {MAX_CHARS} 字符...")

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

            # ---------------- 分批次处理 ----------------
            batch, batch_len = [], 0

            for line in new_lines:
                # 段落本身超过 MAX_CHARS，先拆分
                if len(line) > MAX_CHARS:
                    chunks = split_long_paragraph_by_chars(line, MAX_CHARS)
                else:
                    chunks = [line]

                for chunk in chunks:
                    if batch_len + len(chunk) + (1 if batch else 0) > MAX_CHARS:
                        # 翻译当前批次
                        attempt, translated = 0, None
                        while attempt < 5:
                            try:
                                if driver is None:
                                    driver = init_driver()
                                    select_target_language(driver, tgt_lang)  # ✅ 每次新建浏览器先选语言
                                clear_output(driver)
                                set_source_text(driver, "\n".join(batch))
                                translated = get_translated_text(driver)
                                break
                            except:
                                attempt += 1
                                time.sleep(5)
                                try: driver.quit()
                                except: pass
                                driver = None
                        if translated is None:
                            translated = "翻译失败"
                        append_to_file("\n".join(batch), translated)
                        processed_lines.update(batch)
                        batch = [chunk]
                        batch_len = len(chunk)
                    else:
                        batch.append(chunk)
                        batch_len += len(chunk) + (1 if batch else 0)

            # 翻译最后一批
            if batch:
                attempt, translated = 0, None
                while attempt < 5:
                    try:
                        if driver is None:
                            driver = init_driver()
                            select_target_language(driver, tgt_lang)  # ✅ 每次新建浏览器先选语言
                        clear_output(driver)
                        set_source_text(driver, "\n".join(batch))
                        translated = get_translated_text(driver)
                        break
                    except:
                        attempt += 1
                        time.sleep(5)
                        try: driver.quit()
                        except: pass
                        driver = None
                if translated is None:
                    translated = "翻译失败"
                append_to_file("\n".join(batch), translated)
                processed_lines.update(batch)

            print(f"✅ 已翻译并追加 {len(new_lines)} 条新内容到 {OUTPUT_FILE}")
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("🛑 程序手动停止")
            break
        except Exception as e:
            print(f"❌ 程序出错: {e}")
            time.sleep(CHECK_INTERVAL)

    if driver:
        driver.quit()
        print("🛑 浏览器已关闭")
