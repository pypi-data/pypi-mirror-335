import io
import os
import base64
import requests
import mimetypes
import urllib.parse
from PIL import Image
from pydantic import ConfigDict, Field
from typing import Optional, Literal, Tuple, Union, List, Dict
from .base import Message
from .content import ImageURL, TextContent, ImageContent, ImageURLContent


__all__ = [
    "ImageMessage",
]


class ImageMessage(Message):
    """"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    role: Literal["user", "assistant"] = Field(default="user", description="""The role of the author of this message.""")
    content: Optional[Union[str, List]] = Field(default=None, description="""The content of the message.""")

    def __init__(
            self,
            images: Optional[List[Image.Image | str]] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        _content = []
        if isinstance(self.content, list):
            _content = self.content
        elif isinstance(self.content, str):
            _content.append(TextContent(text=self.content))
        if images:
            for image in images:
                _content.append(ImageContent(image=image))
        self.content = _content

    def image_object_bytes(self, image: Image.Image) -> Tuple[bytes, str]:
        """"""
        img_bytes = io.BytesIO()
        if image.mode == "RGB":
            mime_type = "jpeg"
            image.save(img_bytes, format='JPEG')
        elif image.mode == "RGBA":
            mime_type = "png"
            image.save(img_bytes, format='PNG')
        else:
            raise ValueError("Unsupported image mode: {}".format(image.mode))
        return img_bytes.getvalue(), mime_type

    def image_file_bytes(self, path: str) -> Tuple[bytes, str]:
        """"""
        expanded_path = os.path.expanduser(path)
        mime_type, _ = mimetypes.guess_type(path)
        with open(expanded_path, 'rb') as f:
            image_data = f.read()
        return image_data, mime_type

    def image_url_bytes(self, url: str) -> Tuple[bytes, str]:
        """"""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image_data = response.content
        mime_type, _ = mimetypes.guess_type(url)
        return image_data, mime_type

    def validate_image_type(self, image: Union[str, Image.Image]) -> Literal["image", "path", "url"]:
        """"""
        if isinstance(image, Image.Image):
            return "image"
        elif isinstance(image, str):
            parsed = urllib.parse.urlparse(image)
            if parsed.scheme in ["http", "https"]:
                return "url"
            else:
                return "path"
        else:
            raise ValueError(f"[{__class__.__name__}] Unsupported image type: <{type(image)}>")

    def trans_bytes_base64(self, image: bytes, mime_type: str) -> str:
        """"""
        base64_str = base64.b64encode(image).decode('utf-8')
        return f"data:{mime_type};base64,{base64_str}"

    def trans_bytes_object(self, image: bytes, **kwargs) -> Image.Image:
        """"""
        return Image.open(io.BytesIO(image))

    def read_image_as_bytes(self, image: Union[str, Image]) -> Tuple[bytes, str]:
        """"""
        image_type = self.validate_image_type(image)
        if image_type == "image":
            return self.image_object_bytes(image)
        elif image_type == "path":
            return self.image_file_bytes(image)
        elif image_type == "url":
            return self.image_url_bytes(image)
        else:
            raise ValueError(f"[{__class__.__name__}] Unsupported image type: <{type(image)}>")

    def read_image_as_object(self, image: Union[str, Image]) -> Image.Image:
        """"""
        image_bytes, mime = self.read_image_as_bytes(image)
        return self.trans_bytes_object(image_bytes)

    def read_image_as_base64(self, image: Union[str, Image]) -> str:
        """"""
        image_bytes, mime = self.read_image_as_bytes(image)
        return self.trans_bytes_base64(image_bytes, mime)

    def to_dict(
            self,
            image_type: Literal["base64", "PIL"] = "PIL",
            image_url: Optional[bool] = False,
            **kwargs
    ) -> Dict:
        """"""
        if isinstance(self.content, str):
            return self.model_dump()
        else:
            _content = []
            for content in self.content:
                if isinstance(content, (TextContent, ImageURLContent)):
                    _content.append(content.model_dump())
                elif isinstance(content, ImageContent):
                    if image_url:
                        image_base64 = self.read_image_as_base64(image=content.image)
                        _content.append(ImageURLContent(image_url=ImageURL(url=image_base64)))
                    else:
                        if image_type == "base64":
                            image_base64 = self.read_image_as_base64(image=content.image)
                            _content.append(ImageContent(image=image_base64))
                        else:
                            image_object = self.read_image_as_object(image=content.image)
                            _content.append(ImageContent(image=image_object))
                else:
                    raise ValueError(f"[{__class__.__name__}] Unsupported content type: {type(content)}")
            self.content = _content
            return self.model_dump()
