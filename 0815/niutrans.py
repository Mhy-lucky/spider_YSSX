import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置目标语言
TARGET_LANG_VALUE = "ja"  # 日语
TEXT_TO_TRANSLATE = "你好，世界！这是一个测试。"

class NiuTransPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

        # 定位器
        self.input_box = (By.CSS_SELECTOR, "textarea.source-container")
        self.lang_dropdown_btn = (By.CSS_SELECTOR, "button.selBtn")
        self.result_container = (By.CSS_SELECTOR, "div.results-container")
        
    def open(self, url):
        """打开页面"""
        self.driver.get(url)

    def input_text(self, text):
        """输入要翻译的文本"""
        box = self.wait.until(EC.presence_of_element_located(self.input_box))
        box.clear()
        box.send_keys(text)

    def select_target_language(self, lang_value):
        """循环选择目标语言，直到成功"""
        success = False
        attempt = 0

        while not success:
            attempt += 1
            print(f"[Attempt {attempt}] 尝试选择目标语言: {lang_value}...", flush=True)
            try:
                # 打开下拉菜单
                dropdown_button = self.wait.until(EC.element_to_be_clickable(self.lang_dropdown_btn))
                dropdown_button.click()
                print("[Step] 下拉菜单已点击", flush=True)
                time.sleep(1)  # 等待下拉渲染

                # 找到目标语言按钮
                target_lang_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[@value='{lang_value}']"))
                )

                # 滚动并点击
                actions = ActionChains(self.driver)
                actions.move_to_element(target_lang_button).perform()
                time.sleep(0.5)
                target_lang_button.click()
                print("[Step] 目标语言按钮点击完成，等待语言生效...", flush=True)
                time.sleep(1)

                # 检查语言是否生效
                dropdown_text = dropdown_button.text.strip()
                if lang_value in dropdown_text or "日语" in dropdown_text:
                    print(f"✅ 目标语言 {lang_value} 已成功选择并生效", flush=True)
                    success = True
                else:
                    print("⚠️ 目标语言尚未生效，需要完成安全验证或重新点击", flush=True)
                    print("请完成安全验证后按回车继续...")
                    input()

            except Exception as e:
                print(f"[Error] 点击目标语言失败: {e}", flush=True)
                print("请完成安全验证后按回车继续...")
                input()



    def get_translation_result(self, timeout=10):
        """等待翻译结果真正更新"""
        try:
            elem = self.driver.find_element(*self.result_container)
            start_time = time.time()
            last_text = elem.text.strip()

            while time.time() - start_time < timeout:
                current_text = elem.text.strip()
                if current_text and current_text != last_text:
                    return current_text
                time.sleep(0.2)
            print("⚠️ 翻译超时或未更新")
            return None
        except Exception as e:
            print(f"获取翻译结果出错: {e}")
            return None


def main():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)

    page = NiuTransPage(driver)
    try:
        page.open("https://niutrans.com/trans?type=text")
        page.input_text(TEXT_TO_TRANSLATE)

        print("⚠️ 如果页面弹出验证码，请手动完成后按回车继续...")
        input("完成输入文本的安全验证后按回车继续...")

        if page.select_target_language(TARGET_LANG_VALUE):
            print(f"✅ 已选择目标语言: {TARGET_LANG_VALUE}")
        else:
            print("⚠️ 未找到目标语言按钮，使用默认语言")

        translated_text = page.get_translation_result()
        print("\n原文:", TEXT_TO_TRANSLATE)
        print("译文:", translated_text if translated_text else "未获取到译文")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
