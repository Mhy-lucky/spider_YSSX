from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class SogouTranslatePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        print("[INFO] 正在打开搜狗翻译页面...")
        self.driver.get("https://fanyi.sogou.com/")
        print("[INFO] 页面加载完成！")

    # 保留你原有语言选择方法
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

        if lang_code.lower() == "zh-chs":
            time.sleep(1.5)
            self.driver.execute_script("document.body.click();")
        else:
            time.sleep(0.5)
        print(f"[INFO] 目标语言 {lang_code} 选择完成！")

    def input_text(self, text):
        input_box = self.wait.until(EC.presence_of_element_located((By.ID, "trans-input")))
        self.driver.execute_script("arguments[0].value = '';", input_box)
        input_box.send_keys(text)

    # 改进：轮询 + 强制刷新渲染，确保无头模式可用
    def get_translation(self, previous_text=""):
        result_p = self.wait.until(EC.presence_of_element_located((By.ID, "trans-result")))
        for _ in range(50):  # 最长等待 25 秒
            text = result_p.text.strip()
            if text and text != previous_text:
                lines = [line.strip() for line in text.splitlines() if line.strip() != ""]
                return lines
            # 强制刷新渲染
            self.driver.execute_script("arguments[0].scrollIntoView(true);", result_p)
            self.driver.execute_script("document.body.click();")
            time.sleep(0.5)
        return []

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

def monitor_and_translate(input_file, output_file, page):
    processed_lines = 0
    previous_translation = ""

    while True:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = lines[processed_lines:]
        if not new_lines:
            time.sleep(2)
            continue

        chunks = chunk_paragraphs("".join(new_lines), max_chars=1000)

        with open(output_file, "a", encoding="utf-8") as f_out:
            for chunk in chunks:
                if not chunk:
                    f_out.write("\n")
                    continue

                page.input_text(chunk)
                translations = page.get_translation(previous_translation)
                previous_translation = "\n".join(translations)

                for trans in translations:
                    f_out.write(f"{chunk}\t{trans}\n")
                time.sleep(1)

        processed_lines = len(lines)

def main():
    # 在 main() 中初始化 driver 时
    options = webdriver.ChromeOptions()
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


    page = SogouTranslatePage(driver)

    target_lang = input("请输入目标语言缩写（如 fr, de, ja, zh-CHS）: ").strip()
    page.select_target_language(target_lang)

    print(f"🟢 程序启动...")

    input_file = "/home/maohongyao/pro/code/deepl/input.txt"
    output_file = "/home/maohongyao/pro/code/sougou/translation.txt"
    # input_file = "/Users/admin/Desktop/爬虫实习/0814/input.txt"
    # output_file = "translation.txt"

    if not os.path.exists(output_file):
        open(output_file, "w", encoding="utf-8").close()

    monitor_and_translate(input_file, output_file, page)

if __name__ == "__main__":
    main()
