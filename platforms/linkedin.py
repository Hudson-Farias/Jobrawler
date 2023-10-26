from playwright.async_api._generated import Page, ElementHandle
from httpx import AsyncClient
from bs4 import BeautifulSoup
from asyncio import sleep
from re import findall, escape, IGNORECASE

from models.discord.embed import WebhookEmbed, EmbedFooter
from discord.webhook import Webhook

blacklist = ['GeekHunter', 'Netvagas']
urls = []

class Crawler:
    def __init__(self, page: Page, client: AsyncClient, webhook: Webhook, strings: []):
        self.page = page
        self.client = client
        self.webhook = webhook
        self.strings = strings
        self.scroll_position = 0

    async def run(self, query: str, is_remote: bool):
        await self.__search(query, is_remote)        
        await self.__get_jobs()

    async def __search(self, query: str, is_remote: bool):
        url = f'https://www.linkedin.com/jobs/search/?location=Brasil&geoId=106057199&keywords={query}'
        url += '&f_TPR=r86400' # últimas 24 horas

        if is_remote: url += '&f_WT=2'
        else: 
            url += '&f_PP=106701406' # RJ
            url += '&f_WT=1%2C3' # presencial e híbrido
        
        await self.page.goto(url)

    async def __get_jobs(self):
        await self.__is_scrollable()
        jobs = await self.page.query_selector_all('.jobs-search__results-list li')

        for i, job in enumerate(jobs):
            
            if i == 5: break
            
            company_name = await self.__get_selector_inner_text('.base-search-card__subtitle', job)
            if company_name in blacklist: continue
            
            url  = await (await job.query_selector('a')).get_attribute('href')
            if url in urls: continue
            urls.append(url)
            
            self.embed = WebhookEmbed()
            self.embed.footer = EmbedFooter(text = company_name)
            self.embed.url = url

            await self.__fetch_job_infos(self.embed.url)

            text = self.embed.title  + '\n' + self.embed.description[:100]
            pattern = '|'.join(escape(s) for s in self.strings)
            requirements = findall(pattern, text, IGNORECASE)
            
            self.embed.description = '' ## disable desc

            if requirements: self.webhook.add_embed(self.embed)        

    async def __fetch_job_infos(self, url: str):
        response = await self.client.get(url)
        if not 'body' in response.text: return await self.__fetch_job_infos(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        self.embed.title = soup.find('h1', class_ = 'top-card-layout__title').text.strip()
        self.embed.description = soup.find('div', class_ = 'show-more-less-html__markup').text.strip()

    async def __is_scrollable(self):
        more = self.page.locator('.infinite-scroller__show-more-button')

        if (await more.is_visible()): await more.click()

        await self.page.locator('body').evaluate('e => scroll(0, e.scrollHeight)')
        await sleep(2)
        scroll_position = await self.page.evaluate('e => pageYOffset')

        if self.scroll_position != scroll_position:
            self.scroll_position = scroll_position
            
            return await self.__is_scrollable()

    async def __get_selector_inner_text(self, selector: str, element_handle: ElementHandle | None = None):
        if not element_handle: return (await self.page.inner_text(selector)).strip()

        element = await element_handle.query_selector(selector)
        return (await element.inner_text()).strip()