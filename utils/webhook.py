from httpx import AsyncClient

class Webhook:
    def __init__(self, client: AsyncClient, webhookURL: str):
        self.client = client
        self.webhookURL = webhookURL

        self.embeds = []

    async def embed(self, embeds: list):
        for embed in embeds:
            if 'company_name' in embed:
                embed['footer'] = {}
                embed['footer']['text'] = embed['company_name']
                embed.pop('company_name')
                self.embeds.append(embed)

                if len(self.embeds) == 10:
                    await self.send()
            
            else: 
                embed.pop('description')
                print(embed)
        
        if self.embeds: await self.send()

    async def send(self):
        if self.embeds:
            data = {'embeds': self.embeds}
            
            await self.client.post(self.webhookURL, json = data)
            self.embeds = []        