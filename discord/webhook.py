from httpx import AsyncClient
from typing import List

from models.discord.webhook import Webhook as WebhookPD
from models.discord.embed import WebhookEmbed as WebhookEmbedPD

from utils.json import json_creater

class Webhook:
    def __init__(self, url: str):
        self.url = url
        self.webhook = WebhookPD()

    def add_embed(self, embed: WebhookEmbedPD):
        self.webhook.embeds.append(embed)

    async def send(self, client: AsyncClient):
        if self.webhook.embeds:
            data = self.webhook.dict()
            x = 0

            for _ in range(0, len(self.webhook.embeds), 10):
                embeds = self.webhook.embeds[x:x + 10]
                embeds = [embed.dict() for embed in embeds]
                data['embeds'] = embeds
                response = await client.post(self.url, json = data)
                 
                if response.status_code != 204: print(response.status_code)
                try: 
                    print(response.status_code)
                    print(type(response.status_code))
                except Exception as e: print(e)
                
                x += 10
                
        print('='*30)