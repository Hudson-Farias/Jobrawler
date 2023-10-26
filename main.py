from playwright.async_api import async_playwright
from httpx import AsyncClient
from asyncio import run, TaskGroup
from dotenv import load_dotenv
from os import getenv
from importlib import import_module

from discord.webhook import Webhook
from utils.json import json_load

load_dotenv()

webhooks = {}

plataforms: dict = json_load()

async def crawlling(client):
    for plataform in plataforms.values():
        if plataform['crawler_file']:         
            for query in plataform['queries']:
                async with TaskGroup() as tg:
                    for webhook, page, is_remote in webhooks.values():
                        module = import_module(plataform['crawler_file'])
                        crawler = module.Crawler(page, client, webhook, plataform['regex'])
                        tg.create_task(crawler.run(query, is_remote = is_remote))
            
    async with TaskGroup() as tg:
        for webhook, _, __ in webhooks.values():
            tg.create_task(webhook.send(client))


async def main():
    async with async_playwright() as p:
        async with AsyncClient() as client:
            print('Iniciando...')
            browser = await p.chromium.launch(headless = getenv('HEADLESS').lower() == 'true')
            print('Iniciado')
            
            webhooks['remote'] = Webhook(getenv('WEBHOOK_REMOTE')), (await browser.new_page()), True
            # webhooks['onsite'] = Webhook(getenv('WEBHOOK_ONSITE')), (await browser.new_page()), False
            
            await crawlling(client)
        
            print('Fechando...')
            await browser.close()

run(main())