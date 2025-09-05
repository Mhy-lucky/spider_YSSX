import sys
import os
import time
import traceback
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementNotInteractableException, StaleElementReferenceException,
    NoSuchWindowException
)
import argparse

# ---------------- 配置 ----------------
CHECK_INTERVAL = 10  # 秒，每隔多少秒检查新内容
PROCESSED_FILE = "processed_lines.txt"

# ---------------- 语言缩写映射表 ----------------
LANGUAGE_MAP = {
    'en': 'en', 
    'zh': 'zh-CHS'
}

class SogouTranslatePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        print("🟢 打开搜狗翻译页面...")
        self.driver.get("https://fanyi.sogou.com/")
        print("✅ 页面加载完成")

    def select_source_language(self, lang_code):
        try:
            sl_selector = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".sl-selector .text")))
            sl_selector.click()
            time.sleep(0.5)

            first_letter = lang_code[0].upper()
            try:
                letter_span = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f".letter.langSelectList-char#{first_letter}")
                ))
                letter_span.click()
                time.sleep(0.2)
            except (NoSuchElementException, ElementNotInteractableException) as e:
                print(f"❌ 错误：无法找到首字母索引或元素不可交互，异常：{e}")
                traceback.print_exc()
                raise

            lang_span = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f".langs span[lang='{lang_code}']")
            ))
            lang_span.click()

            if lang_code.lower() == "zh-chs":
                time.sleep(1.5)
                self.driver.execute_script("document.body.click();")
            else:
                time.sleep(0.5)
            print(f"🎯 源语言 {lang_code} 已选择")

        except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
            print(f"❌ 选择源语言失败: {e}")
            traceback.print_exc()
            raise

    def select_target_language(self, lang_code):
        try:
            tl_selector = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".tl-selector .text")))
            tl_selector.click()
            time.sleep(0.5)

            first_letter = lang_code[0].upper()
            try:
                letter_span = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f".letter.langSelectList-char#{first_letter}")
                ))
                letter_span.click()
                time.sleep(0.2)
            except (NoSuchElementException, ElementNotInteractableException) as e:
                print(f"❌ 错误：无法找到首字母索引或元素不可交互，异常：{e}")
                traceback.print_exc()
                raise

            lang_span = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f".langs span[lang='{lang_code}']")
            ))
            lang_span.click()

            if lang_code.lower() == "zh-chs":
                time.sleep(1.5)
                self.driver.execute_script("document.body.click();")
            else:
                time.sleep(0.5)
            print(f"🎯 目标语言 {lang_code} 已选择")

        except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
            print(f"❌ 选择目标语言失败: {e}")
            traceback.print_exc()
            raise

    def input_text(self, text):
        try:
            input_box = self.wait.until(EC.presence_of_element_located((By.ID, "trans-input")))
            self.driver.execute_script("arguments[0].value = '';", input_box)
            input_box.send_keys(text)
        except (NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
            print(f"❌ 输入文本失败: {e}")
            traceback.print_exc()
            raise

    def get_translation(self, previous_text=""):
        try:
            result_p = self.wait.until(EC.presence_of_element_located((By.ID, "trans-result")))
            for _ in range(50):
                text = result_p.text.strip()
                if text and text != previous_text:
                    return [line.strip() for line in text.splitlines() if line.strip()]
                self.driver.execute_script("arguments[0].scrollIntoView(true);", result_p)
                self.driver.execute_script("document.body.click();")
                time.sleep(0.5)
            return []
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
            print(f"❌ 获取翻译失败: {e}")
            traceback.print_exc()
            raise

# ---------------- 浏览器初始化 ----------------
def init_driver():
    driver = None
    try:
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
        driver.get("https://fanyi.sogou.com/")
        time.sleep(3)

        print("🎯 已打开浏览器并进入搜狗翻译页面")

        return driver

    except (WebDriverException, TimeoutException) as e:
        print(f"❌ 浏览器初始化异常: {e}")
        traceback.print_exc()
        if driver:
            try: driver.quit()
            except: pass
        raise
    except Exception as e:
        print(f"❌ 未知浏览器初始化异常: {e}")
        traceback.print_exc()
        if driver:
            try: driver.quit()
            except: pass
        raise

# ---------------- 检查与重启浏览器 ----------------
def restart_driver_if_needed(driver):
    try:
        title = driver.title
        if "搜狗" not in title:
            print("❌ 检测到浏览器卡住或无响应，尝试重启浏览器...")
            driver.quit()
            return init_driver()  # 重新启动浏览器
        return driver
    except (NoSuchWindowException, WebDriverException) as e:
        print(f"❌ 检测浏览器状态失败，准备重启：{e}")
        traceback.print_exc()
        try:
            driver.quit()
        except Exception as inner_e:
            print(f"❌ 关闭浏览器失败: {inner_e}")
            traceback.print_exc()
        return init_driver()

# ---------------- 分块逻辑 ----------------
def chunk_paragraphs(text, max_chars=1000):
    paragraphs = text.splitlines()
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            chunks.append("")
            continue
        words = para.split()
        current_chunk = ""
        for word in words:
            if len(current_chunk) + len(word) + 1 > max_chars:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "
            else:
                current_chunk += word + " "
        if current_chunk:
            chunks.append(current_chunk.strip())
    return chunks

# ---------------- 主程序 ----------------
def monitor_and_translate(input_file, output_file, page):
    processed_lines = 0
    previous_translation = ""
    batch_count = 0
    all_translated_printed = False  # ✅ 新增：文件已全部翻译提示只打印一次

    # 检查是否有断点续爬的记录
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            processed_lines = int(f.read().strip())  # 从文件中读取已处理的行号
            print(f"🟢 恢复断点，已处理 {processed_lines} 行")

    while True:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = lines[processed_lines:]
        if not new_lines:
            if not all_translated_printed:
                print("✅ 文件内容已全部翻译完成！追加新的内容吧")
                all_translated_printed = True
            time.sleep(5)
            continue
        else:
            all_translated_printed = False  # 文件有新增内容，重置标志

        chunks = chunk_paragraphs("".join(new_lines), max_chars=1000)

        with open(output_file, "a", encoding="utf-8") as f_out:
            for chunk in chunks:
                if not chunk:
                    f_out.write("\n")
                    continue

                page.input_text(chunk)
                translations = page.get_translation(previous_translation)
                previous_translation = "\n".join(translations)

                # 检查输入行数和输出行数是否一致
                orig_lines = "\n".join([chunk]).strip().split("\n")
                trans_lines = translations  # 已经是翻译后的列表，不需要再次处理

                if len(orig_lines) == len(trans_lines):
                    # 写入翻译内容
                    for trans in trans_lines:
                        f_out.write(f"{chunk}\t{trans}\n")

                    batch_count += 1
                    if batch_count % 10 == 0:
                        print(f"✅ 本批次输入与输出行数匹配，已翻译 {batch_count} 个块...")

                else:
                    print(f"⚠️ 本批次行数不匹配，丢弃该批次内容")
                    continue

                time.sleep(1)

        # 更新已处理行号
        processed_lines = len(lines)
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            f.write(str(processed_lines))  # 将已处理的行号写入文件

def main():
    # 获取命令行参数
    parser = argparse.ArgumentParser(description="Sogou Translate Automation Script")
    parser.add_argument("input_file", help="输入文件路径")
    parser.add_argument("output_file", help="输出文件路径")
    parser.add_argument("source_lang", help="源语言缩写（如 en, zh, ja 等）")
    parser.add_argument("target_lang", help="目标语言缩写（如 fr, de, ja, zh-CHS 等）")
    args = parser.parse_args()

    chromedriver_autoinstaller.install()

    driver = init_driver()
    page = SogouTranslatePage(driver)
    
    # 设置源语言和目标语言
    page.select_source_language(LANGUAGE_MAP.get(args.source_lang, args.source_lang))
    page.select_target_language(LANGUAGE_MAP.get(args.target_lang, args.target_lang))

    print("🟢 程序启动，开始监控文件并翻译...")

    monitor_and_translate(args.input_file, args.output_file, page)

if __name__ == "__main__":
    main()
