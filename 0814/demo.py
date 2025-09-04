from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time

# ---------------- 初始化浏览器 ----------------
chrome_options = Options()
# chrome_options.add_argument("--headless=new")  # 调试时可注释
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.deepl.com/translator")
time.sleep(2)

# 尝试关闭 cookie 横幅
try:
    cookie_button = WebDriverWait(driver, 5).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "div[data-testid*='cookie-banner'] button")
    )
    cookie_button.click()
except:
    pass

# ---------------- 输入输出函数 ----------------
def set_source_text(text, timeout=15):
    """向 DeepL 输入框输入文本"""
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

def get_translated_text(timeout=60):
    """获取 DeepL 翻译结果（整段文本一次性抓取）"""
    prev_text = ""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            output_div = driver.find_element(By.CSS_SELECTOR,
                'd-textarea[data-testid="translator-target-input"] div[contenteditable="true"]')
            ps = output_div.find_elements(By.TAG_NAME, "p")
            text = "\n".join([p.text for p in ps if p.text])
            if text and text == prev_text:  # 当结果稳定时返回
                return text
            prev_text = text
        except:
            pass
        time.sleep(0.5)
    return "无法获取翻译结果"

# ---------------- 翻译函数 ----------------
def translate_deepl(text, src_lang="en", tgt_lang="zh-Hans", wait_time=15):
    wait = WebDriverWait(driver, wait_time)

    # 选择源语言
    source_btn = wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "button[data-testid='translator-source-lang-btn']"))
    source_btn.click()
    source_option = wait.until(lambda d: d.find_element(By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{src_lang}')]"))
    source_option.click()
    time.sleep(0.2)

    # 选择目标语言
    target_btn = wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "button[data-testid='translator-target-lang-btn']"))
    target_btn.click()
    target_option = wait.until(lambda d: d.find_element(By.XPATH, f"//button[contains(@data-testid,'translator-lang-option-{tgt_lang}')]"))
    target_option.click()
    time.sleep(0.2)

    # 输入文本
    set_source_text(text, wait_time)

    # 获取翻译结果
    return get_translated_text(wait_time)

# ---------------- 主程序 ----------------
if __name__ == "__main__":
    print("请输入要翻译文件的正确路径！")
    output_file = "trans_results.txt"  # 输出文件
    try:
        print("\n请输入源语言缩写（如：en/zh/ja）：")
        src_lang = input().strip()
        print("请输入目标语言缩写（如：en-US/zh-Hans/zh-Hant/ja）：")
        tgt_lang = input().strip()

        print("\n请输入要翻译的内容（可多行输入），输入 'exit' 回车结束输入：")
        lines = []
        while True:
            line = input()
            if line.strip().lower() == "exit":
                break
            lines.append(line)

        # 执行翻译
        print("\n⌛ 正在翻译...")
        full_input = "\n".join(lines)
        translated = translate_deepl(full_input, src_lang, tgt_lang)
        print("✅ 翻译完成！")

        # 保存 TXT：原文在上，译文在下，对应行保持一致
        with open(output_file, "w", encoding="utf-8") as f:
            # 写入原文
            f.write("\n".join(lines) + "\n")
            f.write("\n")  # 空行分隔原文和译文
            # 写入译文
            f.write(translated + "\n")

        print(f"✅ 已保存翻译结果到 {output_file}")

    except Exception as e:
        print(f"❌ 程序运行出错: {str(e)}")
    finally:
        driver.quit()
        print("🛑 浏览器已关闭")
