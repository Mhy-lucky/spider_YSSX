import os
import time
import urllib.parse
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------- 用户配置 -------------------
# INPUT_FILE = "/Users/admin/Desktop/爬虫实习/0814/input.txt"
INPUT_FILE =  "/home/maohongyao/pro/code/deepl/input.txt"
OUTPUT_FILE = "google_trans.txt"
TARGET_LANG = input("请输入目标语言代码（如 'zh-CN'、'en'、'ja' 等）：").strip() or "zh-CN"
MAX_CHARS = 4000  # 每批最大字符数
WAIT_TIME = 10    # 页面等待时间
CHECK_INTERVAL = 5  # 每隔多少秒检查文件是否有新内容

# ------------------- 已处理集合 -------------------
processed_lines = set()
driver = None

# ------------------- 初始化浏览器 -------------------
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

    # 每次使用临时独立目录，避免 user-data-dir 冲突
    tmp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={tmp_user_data_dir}")
    service = Service("/home/maohongyao/chrome/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver
# ------------------- 拆分长段落 -------------------
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

# ------------------- 单行翻译 -------------------
def translate_line(line):
    global driver
    if driver is None:
        driver = init_driver()
    encoded_text = urllib.parse.quote(line)
    url = f"https://translate.google.com/?sl=auto&tl={TARGET_LANG}&text={encoded_text}&op=translate"
    driver.get(url)
    wait = WebDriverWait(driver, WAIT_TIME)
    try:
        el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[jsname='W297wb']")))
        return el.text.strip()
    except:
        print(f"⚠️ 翻译失败：{line}")
        return ""

# ------------------- 保存结果 -------------------
def append_to_file(pairs):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for original, translated in pairs:
            f.write(f"{original}\t{translated}\n")

# ------------------- 读取已翻译内容 -------------------
def load_processed_lines():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    processed_lines.add(line.strip().split("\t")[0])

# ------------------- 检查新内容 -------------------
def read_new_lines():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    new_lines = [line for line in lines if line not in processed_lines]
    return new_lines

# ------------------- 持续翻译 -------------------
def main():
    global driver
    load_processed_lines()
    print("开始监控文件，按 Ctrl+C 停止...")

    try:
        while True:
            new_lines = read_new_lines()
            if new_lines:
                print(f"检测到 {len(new_lines)} 条新内容，开始翻译...")
                # 分批处理
                batch, batch_len = [], 0
                for line in new_lines:
                    chunks = split_long_paragraph_by_chars(line, MAX_CHARS) if len(line) > MAX_CHARS else [line]
                    for chunk in chunks:
                        if batch_len + len(chunk) + 1 > MAX_CHARS:
                            # 翻译当前批次
                            translated_pairs = [(l, translate_line(l)) for l in batch]
                            append_to_file(translated_pairs)
                            processed_lines.update(batch)
                            batch = [chunk]
                            batch_len = len(chunk)
                        else:
                            batch.append(chunk)
                            batch_len += len(chunk) + 1
                # 翻译最后一批
                if batch:
                    translated_pairs = [(l, translate_line(l)) for l in batch]
                    append_to_file(translated_pairs)
                    processed_lines.update(batch)
                print(f"✅ 已完成 {len(new_lines)} 条内容的翻译，请输入新的内容。")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("监控已停止。")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()

