import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import os

# 自动安装匹配当前Chrome版本的chromedriver
chromedriver_autoinstaller.install()

# ---------------- 配置 ----------------
INPUT_FILE = "input.txt"
OUTPUT_FILE = "youdao_trans.txt"
CHECK_INTERVAL = 10    # 秒，每隔多少秒检查新内容
MAX_CHARS = 4500       # 每批次最大字符数
PROCESSED_FILE = "processed_lines.txt"  # 记录已翻译内容的文件

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

    # 启动浏览器
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://fanyi.youdao.com/#/TextTranslate")
    except Exception as e:
        print(f"页面加载超时: {e}")
        time.sleep(5)  # 再等几秒尝试页面渲染

    # 模拟滚动
    driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
    time.sleep(random.uniform(1, 2))
    return driver

# ---------------- 选择语言 ----------------
def select_language(driver, src_lang, tgt_lang):
    wait = WebDriverWait(driver, 20)

    # 源语言
    src_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanFrom-container .lang-text-ai")))
    src_selector.click()
    src_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-code="{src_lang}"]')))
    src_option.click()

    # 目标语言
    tgt_selector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".lang-container.lanTo-container .lang-text-ai")))
    tgt_selector.click()
    tgt_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-code="{tgt_lang}"]')))
    tgt_option.click()

# ---------------- 输入与获取翻译 ----------------
def translate_text(driver, text):
    wait = WebDriverWait(driver, 20)
    input_box = wait.until(EC.visibility_of_element_located((By.ID, "js_fanyi_input")))
    
    # 清空输入框
    input_box.clear()
    input_box.send_keys(text)
    input_box.send_keys(Keys.RETURN)
    
    # 等待随机时间，避免被识别
    time.sleep(random.uniform(3, 6))
    
    output_box = wait.until(EC.visibility_of_element_located((By.ID, "js_fanyi_output_resultOutput")))
    spans = output_box.find_elements(By.CSS_SELECTOR, "span.tgt")
    translated_text = "\n".join([s.text for s in spans])
    return translated_text

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
    src_lang = input("请输入源语言代码（如 th/zh-CHS/en）：").strip()
    tgt_lang = input("请输入目标语言代码（如 zh-CHS/en/ja）：").strip()

    processed_lines = load_processed_lines()  # 加载已翻译的行
    driver = init_driver()  # headless=False 可降低被识别
    select_language(driver, src_lang, tgt_lang)

    print(f"🟢 程序启动，监控 {INPUT_FILE}，每批次最多 {MAX_CHARS} 字符...")

    no_new_content_logged = False  # 标记：无新内容提示是否已打印

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
                no_new_content_logged = False  # 一旦有新内容，下次还能再提示

            batch, batch_len = [], 0
            for line in new_lines:
                # 拆分超长段落
                chunks = [line] if len(line) <= MAX_CHARS else [line[i:i+MAX_CHARS] for i in range(0, len(line), MAX_CHARS)]
                for chunk in chunks:
                    if batch_len + len(chunk) > MAX_CHARS:
                        translated = translate_text(driver, "\n".join(batch))
                        append_to_file(list(zip(batch, [translated]*len(batch))))
                        processed_lines.update(batch)
                        save_processed_lines(processed_lines)  # 保存已翻译的行
                        batch = [chunk]
                        batch_len = len(chunk)
                    else:
                        batch.append(chunk)
                        batch_len += len(chunk)
            # 翻译最后一批
            if batch:
                translated = translate_text(driver, "\n".join(batch))
                append_to_file(list(zip(batch, [translated]*len(batch))))
                processed_lines.update(batch)
                save_processed_lines(processed_lines)  # 保存已翻译的行

            print(f"✅ 已翻译并追加 {len(new_lines)} 条新内容到 {OUTPUT_FILE} 请追加需翻译的新内容到 {INPUT_FILE}")
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
