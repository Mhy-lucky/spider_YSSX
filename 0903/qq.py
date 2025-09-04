# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

OUTPUT_FILE = "translations.txt"

async def append_to_file(pairs):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for orig, trans in pairs:
            f.write(f"{orig}\t{trans}\n")

async def translate_text(text):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 想看浏览器运行就 False
        page = await browser.new_page()
        await page.goto("https://fanyi.qq.com/")

        # 等待输入框加载
        textarea = await page.wait_for_selector("div.tea-textarea-group textarea")

        # 清空输入框
        await textarea.fill("")

        # 拆行输入，模拟真实用户行为
        lines = text.strip().split("\n")
        for line in lines:
            await textarea.type(line, delay=500)  # 50ms 延迟更像真人输入
            await textarea.press("Enter")        # 防止网页缓存上一次内容

        # 等待翻译结果生成
        await page.wait_for_selector("div.target-text-box div.target-text-list")

        # 获取翻译结果
        translated_elements = await page.query_selector_all("div.target-text-box div.target-text-list")
        translated_texts = [await el.inner_text() for el in translated_elements]

        pairs = list(zip(lines, translated_texts))
        await append_to_file(pairs)

        print("✅ 翻译完成并保存到文件:", OUTPUT_FILE)
        for o, t in pairs:
            print(f"{o} → {t}")

        await browser.close()

if __name__ == "__main__":
    text = """今天天气很好
我喜欢
希望明天天气也好"""

    asyncio.run(translate_text(text))
