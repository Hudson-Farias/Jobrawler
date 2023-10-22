from pydantic import BaseModel
from typing import Optional, List

class EmbedAuthor(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    icon_url: Optional[str] = None

class EmbedField(BaseModel):
    name: str
    value: str
    inline: Optional[bool] = True

class EmbedThumbnail(BaseModel):
    url: str

class EmbedImage(BaseModel):
    url: str

class EmbedFooter(BaseModel):
    text: Optional[str] = None
    icon_url: Optional[str] = None

class WebhookEmbed(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    author: Optional[EmbedAuthor] = None
    fields: List[EmbedField] = None
    image: Optional[EmbedImage] = None
    thumbnail: Optional[EmbedThumbnail] = None
    footer: Optional[EmbedFooter] = None
    color: Optional[int] = None
