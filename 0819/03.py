from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SogouTranslatePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.driver.get("https://fanyi.sogou.com/")

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

    def input_text(self, text):
        input_box = self.wait.until(EC.presence_of_element_located((By.ID, "trans-input")))
        self.driver.execute_script("arguments[0].value = '';", input_box)
        input_box.send_keys(text)

    def get_translation(self, previous_text=""):
        result_p = self.wait.until(EC.presence_of_element_located((By.ID, "trans-result")))
        for _ in range(50):  # 最长等待 25 秒
            text = result_p.text.strip()
            if text and text != previous_text:
                lines = [line.strip() for line in text.splitlines() if line.strip() != ""]
                return lines
            self.driver.execute_script("arguments[0].scrollIntoView(true);", result_p)
            self.driver.execute_script("document.body.click();")
            time.sleep(0.5)
        return []

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    page = SogouTranslatePage(driver)

    target_lang = input("请输入目标语言缩写（如 fr, de, ja, zh-CHS）: ").strip()
    page.select_target_language(target_lang)

    input_text = input("请输入要翻译的文本：").strip()
    page.input_text(input_text)
    translations = page.get_translation()
    print("翻译结果：", translations)

if __name__ == "__main__":
    main()
