from playwright.async_api._generated import Page, ElementHandle
from httpx import AsyncClient
from bs4 import BeautifulSoup
from asyncio import sleep
from re import findall

from utils.webhook import Webhook

blacklist = ['GeekHunter', 'Netvagas']

class LinkedinScraper:
    search = ''
    jobs = []
    is_remote = True

    def __init__(self, page: Page, client: AsyncClient, webhook: Webhook):
        self.page = page
        self.client = client
        self.webhook = webhook
        self.scroll_position = 0

    async def run(self, search: str, *, is_remote: bool = True):
        self.search = search
        self.is_remote = is_remote

        await self._search()        
        await self._get_jobs()

        if self.jobs: await self.webhook.embed(self.jobs)

    async def _search(self):
        url = f'https://www.linkedin.com/jobs/search/?location=Brasil&geoId=106057199&keywords={self.search}'
        url += '&f_TPR=r86400' # últimas 24 horas

        if self.is_remote: url += '&f_WT=2'
        else: 
            url += '&f_PP=106701406' # RJ
            url += '&f_WT=1%2C3' # presencial e híbrido
        
        await self.page.goto(url)

    async def _get_jobs(self):
        await self._is_scrollable()
        jobs = await self.page.query_selector_all('.jobs-search__results-list li')

        for i, job in enumerate(jobs):
            job_data = {}
            job_data['company_name'] = await self.__get_selector_inner_text('.base-search-card__subtitle', job)

            if job_data['company_name'] in blacklist: continue
            job_data['url'] = await (await job.query_selector('a')).get_attribute('href')
            print(job_data['url'])

            job_infos = await self._fetch_job_infos(job_data['url'])
            job_data.update(job_infos)

            job_string = job_data['title']  + '\n' + job_data['description']
            requirements = findall(r'react\.?js', job_string.lower())

            if requirements: self.jobs.append(job_data)        

    async def _fetch_job_infos(self, url: str):
        job_data = {}
        response = await self.client.get(url)

        if not 'body' in response.text: return await self._fetch_job_infos(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        job_data['title'] = soup.find('h1', class_ = 'top-card-layout__title').text.strip()
        job_data['description'] = soup.find('div', class_ = 'show-more-less-html__markup').text.strip()

        return job_data
    
    async def _is_scrollable(self):
        more = self.page.locator('.infinite-scroller__show-more-button')

        if (await more.is_visible()): await more.click()

        await self.page.locator('body').evaluate('e => scroll(0, e.scrollHeight)')
        await sleep(2)
        scroll_position = await self.page.evaluate('e => pageYOffset')

        if self.scroll_position != scroll_position:
            self.scroll_position = scroll_position
            
            return await self._is_scrollable()

    async def __get_selector_inner_text(self, selector: str, element_handle: ElementHandle | None = None):
        if not element_handle: return (await self.page.inner_text(selector)).strip()

        element = await element_handle.query_selector(selector)
        return (await element.inner_text()).strip()