import asyncio
import json
import os
from playwright.async_api import async_playwright

CHANNEL_FILE = "/Users/admin/Desktop/coding/0904/failed.txt"
ARTICLES_FILE = "/Users/admin/Desktop/coding/0904/articles.txt"
FAILED_FILE = "/Users/admin/Desktop/coding/0904/failed_1.txt"
PROGRESS_FILE = "/Users/admin/Desktop/coding/0904/progress.txt"
MORE_RETRY = 3  # 点击 More 失败时重试次数
WAIT_AFTER_CLICK = 2000  # 点击 More 后等待时间（毫秒）


async def crawl_channel(page, url, articles_out):
    await page.goto(url, timeout=60000)
    article_urls = set()

    while True:
        # 获取文章列表链接
        links = await page.locator("#list div.tit a").all()
        new_links = 0
        for l in links:
            try:
                href = await l.get_attribute("href")
                if href:
                    if href.startswith(".."):
                        href = "https://english.news.cn" + href.replace("..", "")
                    elif href.startswith("/"):
                        href = "https://english.news.cn" + href
                    if href not in article_urls:
                        article_urls.add(href)
                        new_links += 1
            except:
                pass

        # 只写入新增文章
        if new_links > 0:
            for link in list(article_urls)[-new_links:]:
                articles_out.write(link + "\n")
            articles_out.flush()

        print(f"📝 {new_links} new articles found on this page of {url}")

        # 点击 More 并重试
        more_btn = page.locator("#more.list-more")
        if await more_btn.count() == 0 or not await more_btn.is_visible():
            break

        success = False
        for attempt in range(MORE_RETRY):
            try:
                await more_btn.click()
                await page.wait_for_timeout(WAIT_AFTER_CLICK)
                success = True
                break
            except Exception as e:
                print(f"⚠️ 点击 More 失败，重试 {attempt + 1}/{MORE_RETRY}: {e}")
                await page.wait_for_timeout(1000)

        # 点击 More 后如果没有新文章，则跳到下一个频道
        if not success or new_links == 0:
            print(f"🛑 点击 More 后没有新文章，停止 {url}")
            break

    return list(article_urls)


async def main():
    # 读取进度
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress = json.load(f)
    else:
        progress = {"done": [], "failed": []}

        # 读取频道列表
    with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
        channels = [line.strip() for line in f if line.strip()]

    articles_out = open(ARTICLES_FILE, "a", encoding="utf-8")
    failed_out = open(FAILED_FILE, "a", encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in channels:
            if url in progress["done"] or url in progress["failed"]:
                print(f"⏭ 已处理过，跳过 {url}")
                continue

            print(f"📑 Crawling {url}")
            try:
                await crawl_channel(page, url, articles_out)
                progress["done"].append(url)
                print(f"✅ 完成频道 {url}")
            except Exception as e:
                print(f"❌ 失败: {url} ({e})")
                failed_out.write(url + "\n")
                failed_out.flush()
                progress["failed"].append(url)

            # 保存进度
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

        await browser.close()

    articles_out.close()
    failed_out.close()
    print(f"🎉 全部完成，文章存到 {ARTICLES_FILE}，失败频道存到 {FAILED_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
