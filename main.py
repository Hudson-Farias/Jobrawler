from playwright.async_api import async_playwright
from httpx import AsyncClient
from asyncio import run, TaskGroup
from dotenv import load_dotenv
from os import getenv

from discord.webhook import Webhook
from platforms.linkedin import LinkedinScraper

load_dotenv()

webhooks = {}

async def crawlling(client):
    async with TaskGroup() as tg:
        for webhook, page, is_remote in webhooks.values():
            crawler = LinkedinScraper(page, client, webhook)
            tg.create_task(crawler.run('React.js', is_remote = is_remote))
            
    async with TaskGroup() as tg:
        for webhook, _, __ in webhooks.values():
            tg.create_task(webhook.send(client))


async def main():
    async with async_playwright() as p:
        async with AsyncClient() as client:
            print('Iniciando...')
            browser = await p.chromium.launch(headless = getenv('HEADLESS') == 'true')
            print('Iniciado')
            
            webhooks['remote'] = Webhook(getenv('WEBHOOK_REMOTE')), (await browser.new_page()), True
            webhooks['onsite'] = Webhook(getenv('WEBHOOK_ONSITE')), (await browser.new_page()), False
            
            await crawlling(client)
        
            print('Fechando...')
            await browser.close()

run(main())