from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import nltk
import time
import os

nltk.download('punkt', quiet=True)

# ------------------- 配置 -------------------
# /Users/admin/Desktop/coding/0901/
INPUT_FILE = "all_articles.txt"  # 输入 URL 列表
OUTPUT_FILE = "sentences.txt"       # 输出分句文件
FAILED_FILE = "failed_urls.txt"     # 保存失败 URL
PROCESSED_FILE = "processed_urls.txt"  # 已处理 URL
WAIT_TIME = 2                        # 页面加载等待秒数
CHECK_INTERVAL = 5                   # 循环检测间隔秒数

# ------------------- 初始化 -------------------
processed_urls = set()
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        processed_urls = set(line.strip() for line in f if line.strip())

# ------------------- 初始化浏览器 -------------------
def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# ------------------- 分句 -------------------
def fetch_and_split(url, driver):
    try:
        driver.get(url)
        time.sleep(WAIT_TIME)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        if not text.strip():
            return None
        sentences = nltk.sent_tokenize(text)
        return sentences
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# ------------------- 保存 -------------------
def append_to_file(file_path, lines):
    with open(file_path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
        f.flush()

def mark_processed(url):
    processed_urls.add(url)
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")
        f.flush()

# ------------------- 主循环 -------------------
def main():
    driver = init_driver()
    print("程序启动，可用 Ctrl+C 停止。")

    try:
        while True:
            if not os.path.exists(INPUT_FILE):
                print(f"输入文件不存在，等待 {CHECK_INTERVAL} 秒...")
                time.sleep(CHECK_INTERVAL)
                continue

            with open(INPUT_FILE, "r") as f:
                urls = [line.strip() for line in f if line.strip()]

            new_urls = [u for u in urls if u not in processed_urls]

            if not new_urls:
                print("无新 URL，等待中...")
                time.sleep(CHECK_INTERVAL)
                continue

            for url in new_urls:
                # print(f"🔍 Processing: {url}")
                sentences = fetch_and_split(url, driver)
                if sentences:
                    append_to_file(OUTPUT_FILE, sentences)
                    mark_processed(url)
                    print(f"[Got] URL: {url}, 共 {len(sentences)} 句")
                else:
                    append_to_file(FAILED_FILE, [url])
                    mark_processed(url)
                    print(f"[Failed] URL: {url}")

            print(f"✔ 本轮完成，等待 {CHECK_INTERVAL} 秒后继续...")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("Hand_Stop")
    finally:
        driver.quit()
        print("🛑 浏览器已关闭")

if __name__ == "__main__":
    main()
