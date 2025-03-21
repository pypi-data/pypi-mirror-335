from pydantic import BaseModel


class TextContent(BaseModel):
    text: str


class ImageContentUrl(BaseModel):
    image_url: str
