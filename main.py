from playwright.async_api import async_playwright
from httpx import AsyncClient
from asyncio import run
from dotenv import load_dotenv
from os import getenv

from platforms.linkedin import LinkedinScraper
from utils.webhook import Webhook

load_dotenv()

async def main():
    async with async_playwright() as p:
        async with AsyncClient() as client:
            # browser = await p.chromium.launch(headless = True)
            browser = await p.chromium.launch(headless = False)
            webhook = Webhook(client, getenv('WEBHOOK'))
            page = await browser.new_page()

            crawler = LinkedinScraper(page, client, webhook)

            await crawler.run('React.js')
            await crawler.run('React.js', is_remote = False)
        
            await browser.close()

run(main())