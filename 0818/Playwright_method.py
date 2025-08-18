import asyncio
from playwright.async_api import async_playwright
import time

async def translate_text(text, target_lang="ja"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 可见窗口方便调试
        page = await browser.new_page()
        await page.goto("https://translate.volcengine.com/mobile")
        
        # 等待输入框加载完成
        input_selector = "div.input-box div.slate-editor[contenteditable='true']"
        await page.wait_for_selector(input_selector)
        
        # 点击输入框
        input_box = await page.query_selector(input_selector)
        await input_box.click()
        
        # 清空原有内容
        await input_box.evaluate("el => el.innerHTML = ''")
        
        # 粘贴文本（一次性输入，避免触发防自动化）
        await input_box.type(text, delay=50)  # 模拟真实输入，可调 delay
        
        # ---------- 等待翻译结果 ----------
        output_selector = "div.slate-editor[contenteditable='false'] span[data-slate-string]"
        
        prev_text = ""
        for _ in range(50):  # 最多等待 10 秒 (50*0.2)
            await asyncio.sleep(0.2)
            output_box = await page.query_selector(output_selector)
            if output_box:
                current_text = await output_box.inner_text()
                # 如果翻译结果稳定不再变化，停止等待
                if current_text and current_text == prev_text:
                    break
                prev_text = current_text
        
        translation = prev_text
        await browser.close()
        return translation

# ---------------- 测试 ----------------
text_to_translate = "我真的累了"
translated = asyncio.run(translate_text(text_to_translate, target_lang="ja"))
print("翻译结果:", translated)
