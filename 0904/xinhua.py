import asyncio
import json
import os
from playwright.async_api import async_playwright

CHANNEL_FILE = "/Users/admin/Desktop/coding/0904/channels.json"  # 频道 JSON，每行一个 URL 或 ["channels"]
ARTICLES_FILE = "articles.txt"
FAILED_FILE = "failed.txt"
PROGRESS_FILE = "progress.json"  # 记录已爬取频道

async def crawl_channel(page, url):
    await page.goto(url, timeout=60000)
    article_urls = set()

    while True:
        # 获取文章列表链接
        links = await page.locator("#list div.tit a").all()
        for l in links:
            try:
                href = await l.get_attribute("href")
                if href:
                    if href.startswith(".."):
                        href = "https://english.news.cn" + href.replace("..", "")
                    elif href.startswith("/"):
                        href = "https://english.news.cn" + href
                    article_urls.add(href)
            except:
                pass

        # 点击 More
        more_btn = page.locator("#more.list-more")
        if await more_btn.count() == 0 or not await more_btn.is_visible():
            break
        try:
            await more_btn.click()
            await page.wait_for_timeout(2000)
        except:
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
        data = json.load(f)
        # 兼容 JSON 是 list 或 {"channels": [...]}
        channels = data.get("channels") if isinstance(data, dict) else data

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
                articles = await crawl_channel(page, url)
                for a in articles:
                    articles_out.write(a + "\n")
                articles_out.flush()

                progress["done"].append(url)
                print(f"✅ 成功抓到 {len(articles)} 篇文章")
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
