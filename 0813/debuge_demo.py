from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# ---------------- 全局初始化浏览器 ----------------
print("🛠️ 正在初始化浏览器...")
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=chrome_options)
print("🌐 正在打开DeepL页面...")
driver.get("https://www.deepl.com/translator")
time.sleep(2)

# 尝试关闭 cookie 横幅
try:
    print("🍪 正在尝试关闭cookie横幅...")
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
    print(f"\n🔍 开始翻译: {text}")
    wait = WebDriverWait(driver, 10)

    # 选择源语言
    print(f"🌍 正在选择源语言: {src_lang}")
    try:
        source_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='translator-source-lang-btn']")))
        source_btn.click()
        print("   ✅ 已点击源语言按钮")
        
        source_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{src_lang}')]"))
        )
        source_option.click()
        print(f"   ✅ 已选择 {src_lang} 语言")
        time.sleep(0.2)
    except Exception as e:
        print(f"   ❌ 选择源语言出错: {str(e)}")
        return f"语言选择错误: {str(e)}"

    # 选择目标语言
    print(f"🌎 正在选择目标语言: {tgt_lang}")
    try:
        target_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='translator-target-lang-btn']")))
        target_btn.click()
        print("   ✅ 已点击目标语言按钮")
        
        target_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{tgt_lang}')]"))
        )
        target_option.click()
        print(f"   ✅ 已选择 {tgt_lang} 语言")
        time.sleep(0.2)
    except Exception as e:
        print(f"   ❌ 选择目标语言出错: {str(e)}")
        return f"语言选择错误: {str(e)}"

    # 输入文本
    print("⌨️ 正在输入文本...")
    try:
        input_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "d-textarea[data-testid='translator-source-input'] div")))
        print("   ✅ 找到输入框元素")
        
        driver.execute_script("arguments[0].innerText = '';", input_div) #清空
        driver.execute_script("arguments[0].innerText = arguments[1];", input_div, text) #输入
        print("   ✅ 已输入文本")
        
    except Exception as e:
        print(f"   ❌ 文本输入出错: {str(e)}")
        return f"输入错误: {str(e)}"
    time.sleep(3)  # 等待翻译结果加载

   
    print("🔄 正在获取翻译结果...")
    translated_text = ""
    try:
        # 最多等 10 秒，直到翻译结果非空
        end_time = time.time() + 10
        while time.time() < end_time:
            target_elem = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'd-textarea[data-testid="translator-target-input"]')
                )
            )
            text_value = driver.execute_script(
                "return arguments[0].innerText;", target_elem
            ).strip()
            if text_value:
                translated_text = text_value
                break
            time.sleep(0.2)  # 间隔 200ms 再取一次

        if not translated_text:
            translated_text = "无法获取翻译结果"

        print(f"   翻译结果: {translated_text}")

    except Exception as e:
        print(f"   ❌ 获取翻译结果出错: {str(e)}")




# ---------------- 主程序 ----------------
if __name__ == "__main__":
    try:
        print("\n中文简体（zh-Hans）,中文繁体（zh-Hant）,美式英语（en-US）,英式英语（en-GB）")
        src_lang = input("请输入源语言缩写（如：en/zh/ja）：").strip()
        tgt_lang = input("请输入目标语言缩写，要分简繁体和英美式（如：en-US/zh-Hans/ja）：").strip()


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
                print(f"\n{'='*40}")
                print(f"📝 原始文本: {line}")
                translated = translate_deepl(line, src_lang, tgt_lang)
                print(f"💡 翻译结果: {translated}")
                f.write(f"{line}\n{translated}\n\n")

        print(f"\n✅ 所有翻译完成，结果已保存到 {output_file}")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
    finally:
        driver.quit()
        print("🛑 浏览器已关闭")