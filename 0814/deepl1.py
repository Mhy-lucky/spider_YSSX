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
import argparse

# ---------------- 配置 ----------------
CHECK_INTERVAL = 10     # 秒，每隔多少秒检查新内容
MAX_CHARS = 1500        # 每批次最大字符数
PROCESSED_FILE = "processed_lines.txt"

# ---------------- 语言缩写映射表 ----------------
LANGUAGE_MAP = {
    'en': 'en-US', 
    'zh': 'zh-Hans'
}

# ---------------- 浏览器初始化 ----------------
def init_driver():
    driver = None
    try:
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 可根据需求选择启用或禁用 headless 模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--remote-debugging-port=9222")  

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.deepl.com/translator")
        time.sleep(3)

        # ---------------- 关闭 "Introducing DeepL AI Labs" 弹窗 ----------------
        try:
            close_button_svg = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[data-name='XMarkSmall']"))
            )
            close_button_svg.click()  # 点击关闭按钮
            print("🎯 已关闭 Introducing DeepL AI Labs 弹窗")
        except TimeoutException as e:
            print(f"❌ 关闭 Introducing DeepL AI Labs 弹窗失败: {e}")
            traceback.print_exc()

        # ---------------- 关闭 Cookie 横幅 ----------------
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid*='cookie-banner'] button"))
            )
            cookie_button.click()  # 点击关闭 Cookie 横幅
            print("🎯 已关闭 Cookie 横幅")
        except TimeoutException as e:
            print(f"❌ 关闭 Cookie 横幅失败: {e}")
            traceback.print_exc()

        # ---------------- 选择目标语言 ----------------
        select_target_language(driver)

        return driver

    except WebDriverException as e:
        print(f"❌ 浏览器初始化异常: {e}")
        traceback.print_exc()
        if driver:
            try: driver.quit()
            except Exception as inner_e:
                print(f"❌ 关闭浏览器失败: {inner_e}")
                traceback.print_exc()
        raise
    except Exception as e:
        print(f"❌ 未知浏览器初始化异常: {e}")
        traceback.print_exc()
        if driver:
            try: driver.quit()
            except Exception as inner_e:
                print(f"❌ 关闭浏览器失败: {inner_e}")
                traceback.print_exc()
        raise

# ---------------- 选择目标语言 ----------------
def select_target_language(driver):
    try:
        tgt_lang = args.target_lang  # 从命令行参数中获取目标语言
        full_lang = LANGUAGE_MAP.get(tgt_lang, tgt_lang)  # 使用映射表获取完整语言代码

        # 等待目标语言下拉按钮可点击
        lang_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='translator-target-lang-btn']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", lang_btn)
        driver.execute_script("arguments[0].click();", lang_btn)

        # 等待目标语言选项可点击
        lang_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[@data-testid='translator-lang-option-{full_lang}']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", lang_option)
        driver.execute_script("arguments[0].click();", lang_option)

        print(f"🎯 已选择目标语言：{full_lang}")
    except Exception as e:
        print(f"❌ 选择目标语言失败: {e}")
        traceback.print_exc()
        raise

# ---------------- 输入与获取翻译 ----------------
def set_source_text(driver, text, timeout=15):
    try:
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
    except Exception as e:
        print(f"❌ 设置输入文本失败: {e}")
        traceback.print_exc()
        raise

def get_translated_text(driver, timeout=60):
    try:
        timeout = float(timeout)  # 强制转换 timeout 为 float 类型
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
            except Exception as e:
                print(f"❌ 获取翻译文本失败: {e}")
                traceback.print_exc()
                raise
            time.sleep(0.5)
        return "无法获取翻译结果"
    except Exception as e:
        print(f"❌ 获取翻译结果失败: {e}")
        traceback.print_exc()
        raise

# ---------------- 监测与重启服务器 ----------------
def restart_driver_if_needed(driver):
    try:
        # 检查浏览器是否卡住，尝试获取网页标题
        title = driver.title
        if "DeepL" not in title:
            print("❌ 检测到浏览器卡住或无响应，尝试重启浏览器...")
            driver.quit()
            return init_driver()  # 重新启动浏览器
        return driver
    except Exception as e:
        print(f"❌ 检测浏览器状态失败，准备重启：{e}")
        traceback.print_exc()
        try:
            driver.quit()
        except Exception as inner_e:
            print(f"❌ 关闭浏览器失败: {inner_e}")
            traceback.print_exc()
        return init_driver()

# ---------------- 保存函数 ----------------
def append_to_file(original, translated):
    try:
        orig_lines = original.strip().split("\n")
        trans_lines = translated.strip().split("\n")
        min_len = min(len(orig_lines), len(trans_lines))

        with open(args.output_file, "a", encoding="utf-8") as f:
            for i in range(min_len):
                f.write(orig_lines[i].strip() + "\t" + trans_lines[i].strip() + "\n")
    except Exception as e:
        print(f"❌ 保存翻译结果到文件失败: {e}")
        traceback.print_exc()
        raise

# ---------------- 翻译前清空输出 ----------------
def clear_output(driver):
    try:
        output_div = driver.find_element(By.CSS_SELECTOR,
            'd-textarea[data-testid="translator-target-input"] div[contenteditable="true"]')
        driver.execute_script("arguments[0].innerText='';", output_div)
    except NoSuchElementException as e:
        print(f"❌ 未找到输出区域: {e}")
    except Exception as e:
        print(f"❌ 清空输出区域失败: {e}")
        traceback.print_exc()

# ---------------- 段落拆分（单段落超长，按字符数，保持单词完整） ----------------
def split_long_paragraph_by_chars(paragraph, max_chars):
    try:
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
    except Exception as e:
        print(f"❌ 拆分段落失败: {e}")
        traceback.print_exc()
        raise

# ---------------- 记录已处理的行 ----------------
def load_processed_lines(processed_file):
    try:
        if os.path.exists(processed_file):
            with open(processed_file, "r", encoding="utf-8") as f:
                return set(f.read().splitlines())
        return set()
    except Exception as e:
        print(f"❌ 读取已处理文件失败: {e}")
        traceback.print_exc()
        raise

def save_processed_lines(processed_lines, processed_file):
    try:
        with open(processed_file, "w", encoding="utf-8") as f:
            f.write("\n".join(processed_lines))
    except Exception as e:
        print(f"❌ 保存已处理文件失败: {e}")
        traceback.print_exc()
        raise

# ---------------- 主程序 ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeepL Translator Script")
    parser.add_argument("input_file", help="输入文件路径")
    parser.add_argument("output_file", help="输出文件路径")
    parser.add_argument("source_lang", help="源语言缩写（如 en, zh, ja）")
    parser.add_argument("target_lang", help="目标语言缩写（如 en, zh, ja）")

    args = parser.parse_args()

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
                except Exception:
                    print("❌ 浏览器启动或语言选择失败，5秒后重试...")
                    time.sleep(5)
                    continue

            # 检查输入文件
            if not os.path.exists(args.input_file):
                time.sleep(CHECK_INTERVAL)
                continue

            try:
                with open(args.input_file, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"❌ 读取输入文件失败: {e}")
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
                                    select_target_language(driver)  # ✅ 每次新建浏览器先选语言
                                clear_output(driver)
                                set_source_text(driver, "\n".join(batch))
                                translated = get_translated_text(driver)
                                
                                # 检查输入行数和输出行数是否一致
                                orig_lines = "\n".join(batch).strip().split("\n")
                                trans_lines = translated.strip().split("\n")
                                
                                if len(orig_lines) == len(trans_lines):
                                    append_to_file("\n".join(batch), translated)
                                    processed_lines.update(batch)
                                    save_processed_lines(processed_lines, PROCESSED_FILE)
                                else:
                                    print(f"⚠️ 本批次行数不匹配，丢弃 {len(batch)} 行内容")
                                break
                            except Exception as e:
                                attempt += 1
                                time.sleep(5)
                                try: driver.quit()
                                except: pass
                                driver = None
                        if translated is None:
                            translated = "翻译失败"
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
                            select_target_language(driver)  # ✅ 每次新建浏览器先选语言
                        clear_output(driver)
                        set_source_text(driver, "\n".join(batch))
                        translated = get_translated_text(driver)
                        
                        # 检查输入行数和输出行数是否一致
                        orig_lines = "\n".join(batch).strip().split("\n")
                        trans_lines = translated.strip().split("\n")
                        
                        if len(orig_lines) == len(trans_lines):
                            append_to_file("\n".join(batch), translated)
                            processed_lines.update(batch)
                            save_processed_lines(processed_lines, PROCESSED_FILE)
                        else:
                            print(f"⚠️ 本批次行数不匹配，丢弃 {len(batch)} 行内容")
                        break
                    except Exception as e:
                        attempt += 1
                        time.sleep(5)
                        try: driver.quit()
                        except: pass
                        driver = None

            print(f"✅ 已翻译并追加 {len(new_lines)} 条新内容到 {args.output_file}")
            save_processed_lines(processed_lines, PROCESSED_FILE)  # 更新已处理行记录
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
