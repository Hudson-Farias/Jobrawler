from httpx import AsyncClient
from typing import List

from models.discord.webhook import Webhook as WebhookPD
from models.discord.embed import WebhookEmbed as WebhookEmbedPD

class Webhook:
    def __init__(self, url: str):
        self.url = url
        self.webhook = WebhookPD()

    def add_embed(self, embed: WebhookEmbedPD):
        self.webhook.embeds.append(embed)

    async def send(self, client: AsyncClient):
        if self.webhook.embeds:
            print(len(self.webhook.embeds))
            data = self.webhook.dict()
            x = 0

            for _ in range(0, len(self.webhook.embeds), 10):
                embeds = self.webhook.embeds[x:x + 10]
                embeds = [embed.dict() for embed in embeds]
                
                data['embeds'] = embeds
                response = await client.post(self.url, json = data)
            
                x += 10