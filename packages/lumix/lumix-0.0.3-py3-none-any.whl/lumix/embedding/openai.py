from logging import Logger
from openai import OpenAI as OpenAIOriginal
from typing import List, Union, Callable, Optional
from lumix.types.embedding import CreateEmbeddingResponse
from lumix.api.openai import OpenAIMixin
from lumix.utils.logger import LoggerMixin
from lumix.embedding.base import EmbeddingMixin


__all__ = [
    "OpenAIEmbedding"
]


class OpenAIEmbedding(LoggerMixin, OpenAIMixin, EmbeddingMixin):
    """"""
    verbose: bool = False
    batch_size: Optional[int]
    api_key: Optional[str] = None
    api_key_name: Optional[str] = None

    def __init__(
            self,
            model: str,
            base_url: Optional[str] = "https://api.openai.com/v1",
            api_key: Optional[str] = "BASE_URL",
            key_name: Optional[str] = "BASE_URL",
            client: Optional[OpenAIOriginal] = None,
            timeout: Optional[float] = 30.0,
            max_retries: Optional[int] = 5,
            verbose: bool = False,
            logger: Optional[Union[Logger, Callable]] = None,
            **kwargs
    ):
        """"""
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.key_name = key_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.set_client(client)
        self.logger = logger
        self.verbose = verbose
        self.kwargs = kwargs

    def __call__(
            self,
            text: Union[str, List[str]],
    ) -> CreateEmbeddingResponse:
        if isinstance(text, str):
            text = [text]
        return self.embedding(text=text)

    def embedding(
            self,
            text: Union[str, List[str]],
    ) -> CreateEmbeddingResponse:
        """"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return CreateEmbeddingResponse.model_validate(response.model_dump())
