from pydantic import BaseModel
from typing import Optional, List

from models.discord.embed import WebhookEmbed

class Webhook(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    content: Optional[str] = None
    embeds: Optional[List[WebhookEmbed]] = []