import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

# ---------------- 配置 ----------------
# 获取当前脚本所在目录
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # 构建文件完整路径
# INPUT_FILE = os.path.join(BASE_DIR, "input.txt")
INPUT_FILE = "/home/maohongyao/0814/input.txt"
OUTPUT_FILE = "/home/maohongyao/0814/trans_results.txt"
CHECK_INTERVAL = 10     # 秒，每隔多少秒检查新内容
MAX_WORDS = 600         # 每批次最大词数
MAX_LINES = 10          # 每批次最大条数

# ---------------- 浏览器初始化 ----------------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=chrome_options)
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

# ---------------- 选择语言 ----------------
def select_language(driver, button_selector, lang_code, lang_name):
    for attempt in range(5):
        try:
            btn = WebDriverWait(driver, 30).until(
                lambda d: d.find_element(By.CSS_SELECTOR, button_selector)
            )
            btn.click()
            option = WebDriverWait(driver, 30).until(
                lambda d: d.find_element(By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{lang_code}')]")
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            ActionChains(driver).move_to_element(option).click().perform()
            time.sleep(0.3)
            return
        except Exception as e:
            print(f"⚠️ 选择语言 {lang_name} {lang_code} 失败，重试 {attempt+1}/5")
            print("❌ 错误原因:", e)
            time.sleep(2)
    raise Exception(f"选择语言 {lang_name} {lang_code} 最终失败")

# ---------------- 输入输出函数 ----------------
def set_source_text(driver, text, timeout=15):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            input_div = driver.find_element(By.CSS_SELECTOR,
                'd-textarea[data-testid="translator-source-input"] div[contenteditable="true"]')
            driver.execute_script("""
                let div = arguments[0];
                div.focus();
                div.innerText = '';
                div.dispatchEvent(new Event('input', { bubbles: true }));
                div.innerText = arguments[1];
                div.dispatchEvent(new Event('input', { bubbles: true }));
            """, input_div, text)
            return
        except:
            time.sleep(0.2)
    raise Exception("未找到可编辑输入区域")

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

def translate_deepl(driver, text, src_lang, tgt_lang, wait_time=30):
    # 刷新页面防止卡住
    driver.refresh()
    time.sleep(5)

    select_language(driver, "button[data-testid='translator-source-lang-btn']", src_lang, "源语言")
    select_language(driver, "button[data-testid='translator-target-lang-btn']", tgt_lang, "目标语言")
    set_source_text(driver, text, wait_time)
    return get_translated_text(driver, wait_time)

# ---------------- 保存函数 ----------------
def append_to_file(original, translated):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(original.strip() + "\n\n")
        f.write(translated.strip() + "\n\n")

# ---------------- 无限循环翻译 ----------------
if __name__ == "__main__":
    print("请输入要翻译文件的正确路径！Ctrl+C 退出")
    src_lang = input("请输入源语言缩写（如：en/zh/ja）：").strip()
    tgt_lang = input("请输入目标语言缩写，要区别美式/英式、简体/繁体（如：en-US/zh-Hans/zh-Hant/ja）：").strip()

    processed_lines = set()
    driver = None
    print(f"🟢 程序启动，监控 {INPUT_FILE}，每批次最多 {MAX_WORDS} 词或 {MAX_LINES} 条...")

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

            # 分批次
            batch = []
            batch_words = 0
            for line in new_lines:
                words = len(line.split())
                if batch_words + words > MAX_WORDS or len(batch) >= MAX_LINES:
                    # 翻译当前批次
                    attempt = 0
                    translated = None
                    while attempt < 5:
                        try:
                            if driver is None:
                                driver = init_driver()
                            translated = translate_deepl(driver, "\n".join(batch), src_lang, tgt_lang)
                            break
                        except Exception as e:
                            print(f"⚠️ 翻译失败，重连中... ({attempt+1}/5)")
                            print(traceback.format_exc())
                            attempt += 1
                            time.sleep(5)
                            try: driver.quit()
                            except: pass
                            driver = None
                    if translated is None:
                        translated = "翻译失败"
                    append_to_file("\n".join(batch), translated)
                    processed_lines.update(batch)
                    batch = [line]
                    batch_words = words
                else:
                    batch.append(line)
                    batch_words += words

            # 翻译最后一批
            if batch:
                attempt = 0
                translated = None
                while attempt < 5:
                    try:
                        if driver is None:
                            driver = init_driver()
                        translated = translate_deepl(driver, "\n".join(batch), src_lang, tgt_lang)
                        break
                    except Exception as e:
                        print(f"⚠️ 翻译失败，重连中... ({attempt+1}/5)")
                        print(traceback.format_exc())
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
