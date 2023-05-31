from playwright.async_api import async_playwright
from httpx import AsyncClient
from asyncio import run

from platforms.linkedin import LinkedinScraper

async def main():
    async with async_playwright() as p:
        async with AsyncClient() as client:
            # browser = await p.chromium.launch(headless = True)
            browser = await p.chromium.launch(headless = False)
            page = await browser.new_page()

            sl = LinkedinScraper(page, client)

            await sl.run('React.js')
            # await sl.run('React.js', is_remote = False)
            input()
        
            await browser.close()

run(main())