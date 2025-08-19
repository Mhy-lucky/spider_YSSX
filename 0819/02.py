import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ---------------- 配置 ----------------
# INPUT_FILE = "/home/maohongyao/pro/code/deepl/input.txt"
# OUTPUT_FILE = "/home/maohongyao/pro/code/sougou/translation.txt"

# 本地调试用
INPUT_FILE = "/Users/admin/Desktop/爬虫实习/0814/input.txt"
OUTPUT_FILE = "translation.txt"
CHECK_INTERVAL = 10
MAX_CHARS = 1000

if not os.path.exists(OUTPUT_FILE):
    open(OUTPUT_FILE, "w", encoding="utf-8").close()

# ---------------- 浏览器初始化 ----------------
class SogouTranslatePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.driver.get("https://fanyi.sogou.com/")
        time.sleep(2)

    def select_target_language(self, lang_code):
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
        except:
            pass
        lang_span = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f".langs span[lang='{lang_code}']")
        ))
        lang_span.click()
        time.sleep(0.5)
        print(f"[INFO] 目标语言 {lang_code} 选择完成！")

    def input_text(self, text):
        input_box = self.wait.until(EC.presence_of_element_located((By.ID, "trans-input")))
        self.driver.execute_script("arguments[0].value = '';", input_box)
        input_box.send_keys(text)

    def get_translation(self, previous_text=""):
        result_p = self.wait.until(EC.presence_of_element_located((By.ID, "trans-result")))
        for _ in range(50):
            text = result_p.text.strip()
            if text and text != previous_text:
                lines = [line.strip() for line in text.splitlines() if line.strip() != ""]
                return lines
            self.driver.execute_script("arguments[0].scrollIntoView(true);", result_p)
            self.driver.execute_script("document.body.click();")
            time.sleep(0.5)
        return []

# ---------------- 按句拆分 ----------------
def chunk_paragraphs(text, max_chars=1000):
    chunks = []
    paragraphs = text.splitlines()
    sentence_end_re = re.compile(r'([。！？.!?])')
    for para in paragraphs:
        para = para.strip()
        if not para:
            chunks.append("")
            continue
        sentences = []
        last_index = 0
        for match in sentence_end_re.finditer(para):
            end = match.end()
            sentences.append(para[last_index:end].strip())
            last_index = end
        if last_index < len(para):
            sentences.append(para[last_index:].strip())
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
            else:
                current_chunk += sentence + " "
        if current_chunk:
            chunks.append(current_chunk.strip())
    return chunks

# ---------------- 保存函数 ----------------
def append_to_file(original_lines, translated_lines):
    min_len = min(len(original_lines), len(translated_lines))
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for i in range(min_len):
            f.write(original_lines[i].strip() + "\t" + translated_lines[i].strip() + "\n")
        f.write("\n")

# ---------------- 无限循环翻译 ----------------
if __name__ == "__main__":
    tgt_lang = input("请输入目标语言缩写（如 fr, de, ja, zh-CHS）: ").strip()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    page = SogouTranslatePage(driver)
    page.select_target_language(tgt_lang)

    processed_lines = 0
    previous_translation = ""

    print(f"🟢 程序启动，监控 {INPUT_FILE}，每块最多 {MAX_CHARS} 字...")

    while True:
        try:
            if not os.path.exists(INPUT_FILE):
                time.sleep(CHECK_INTERVAL)
                continue

            with open(INPUT_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = lines[processed_lines:]
            if not new_lines:
                time.sleep(CHECK_INTERVAL)
                continue

            chunks = chunk_paragraphs("".join(new_lines), max_chars=MAX_CHARS)

            for idx, chunk in enumerate(chunks, start=1):
                if not chunk:
                    with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
                        f_out.write("\n")
                    continue

                page.input_text(chunk)
                translations = page.get_translation(previous_translation)
                previous_translation = "\n".join(translations)
                append_to_file([chunk], translations)

                # ---- DeepL 风格输出，仅显示已翻译块编号 ----
                print(f"✅ 已翻译 {idx}/{len(chunks)} 个块内容")
                # ---------------------------------------------

                time.sleep(1)

            processed_lines = len(lines)

        except KeyboardInterrupt:
            print("🛑 程序手动停止")
            break
        except Exception as e:
            print(f"❌ 程序出错: {e}")
            time.sleep(CHECK_INTERVAL)

    driver.quit()
    print("🛑 浏览器已关闭")
