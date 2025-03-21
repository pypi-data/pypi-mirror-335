from io import BytesIO
from pandas import DataFrame
from pydantic import BaseModel, ConfigDict
from typing import Union, Literal, Optional
from PIL import Image


__all__ = [
    "Content",
    "TextContent",
    "ImageURL",
    "ImageContent",
    "ImageURLContent",
    "AudioContent",
    "ChartContent",
    "TableContent",
    "CiteContent",
    "QueryContent",
]


class Content(BaseModel):
    """"""
    type: str = "text"


class TextContent(Content):
    """"""
    type: Literal["text"] = "text"
    text: Optional[str] = None


class ImageURL(BaseModel):
    """"""
    url: str


class ImageURLContent(Content):
    """"""
    type: Literal["image_url"] = "image_url"
    image_url: ImageURL


class ImageContent(Content):
    """"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: Literal["image"] = "image"
    image: Union[Image.Image, str, bytes]


class AudioContent(BaseModel):
    """"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: Literal["audio"] = "audio"
    audio_url: Optional[Union[BytesIO, bytes, str]] = None


class ChartContent(Content):
    """"""
    type: Literal["chart"] = "chart"
    chart: Optional[str] = None


class TableContent(Content):
    """"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: Literal["table"] = "table"
    table: Optional[DataFrame] = None


class CiteContent(Content):
    """"""
    type: Literal["cite"] = "cite"
    content: Optional[str] = None


class QueryContent(Content):
    """"""
    type: Literal["query"] = "query"
    content: Optional[str] = None
