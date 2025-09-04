import asyncio
from playwright.async_api import async_playwright

async def translate_text(input_text, target_language='ja'):
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 打开 DeepL 翻译页面
        await page.goto('https://www.deepl.com/translator')

        # 等待并选择目标语言
        await page.wait_for_selector('button[data-testid="translator-target-lang-btn"]')
        await page.click('button[data-testid="translator-target-lang-btn"]')
        await page.wait_for_selector(f'button[data-testid="translator-lang-option-{target_language}"]')
        await page.click(f'button[data-testid="translator-lang-option-{target_language}"]')

        # 等待并获取源文本输入框
        source_input = await page.wait_for_selector('div.lmt__textarea.lmt__source_textarea div[contenteditable="true"]', timeout=60000)

        # 输入文本
        await source_input.fill(input_text)

        # 等待翻译结果
        await page.wait_for_selector('div.lmt__textarea.lmt__target_textarea div[contenteditable="true"]', timeout=60000)
        translated_text = await page.inner_text('div.lmt__textarea.lmt__target_textarea div[contenteditable="true"]')

        # 打印翻译结果
        print(f"原文: {input_text}")
        print(f"翻译: {translated_text}")

        # 关闭浏览器
        await browser.close()

# 示例用法
input_text = "Hello, how are you?"
asyncio.run(translate_text(input_text))
