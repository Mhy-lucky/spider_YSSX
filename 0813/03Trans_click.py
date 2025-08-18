from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# ---------------- 全局初始化浏览器 ----------------
chrome_options = Options()
chrome_options.add_argument("--headless")       # 无界面模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.deepl.com/translator")
time.sleep(2)  # 等页面加载

# 尝试关闭 cookie 横幅
try:
    cookie_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='cookie-banner-lax'] button"))
    )
    cookie_button.click()
    print("✅ 已关闭 cookie 横幅")
except TimeoutException:
    print("⚠️ 没有找到 cookie 横幅")

output_file = "trans_results.txt"

# ---------------- 翻译函数 ----------------
def translate_deepl(text, src_lang, tgt_lang, timeout=15):
    wait = WebDriverWait(driver, 10)

    # 选择源语言
    source_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='translator-source-lang-btn']")))
    source_btn.click()
    source_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{src_lang.lower()}')]"))
    )
    source_option.click()
    time.sleep(0.2)

    # 选择目标语言
    target_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='translator-target-lang-btn']")))
    target_btn.click()
    target_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{tgt_lang.lower()}')]"))
    )
    target_option.click()
    time.sleep(0.2)

    # 输入文本
    input_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "d-textarea[data-testid='translator-source-input']")))
    # 清空已有内容
    driver.execute_script("arguments[0].innerText = '';", input_div)
    # 输入文本
    driver.execute_script("arguments[0].innerText = arguments[1];", input_div, text)


    translated_text=""
    try:
        translated = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "d-textarea[data-testid='translator-target-input'] p span")
            )
        )
        return translated.text
    except:
        pass


    return translated_text

# ---------------- 主程序 ----------------
if __name__ == "__main__":
    src_lang = input("请输入源语言缩写（如：en/zh/ja）：").strip()
    tgt_lang = input("请输入目标语言缩写（如：en/zh/ja）：").strip()

    print("\n请输入要翻译的内容（可多行输入），输入 'exit' 回车结束输入：")
    lines = []
    while True:
        line = input()
        if line.strip().lower() == "exit":
            break
        if line.strip():
            lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            print(f"\n正在翻译: {line}")
            translated = translate_deepl(line, src_lang, tgt_lang)
            print(f"翻译结果: {translated}")
            f.write(f"{line}\n{translated}\n\n")

    driver.quit()
    print(f"\n✅ 所有翻译完成，结果已保存到 {output_file}")
