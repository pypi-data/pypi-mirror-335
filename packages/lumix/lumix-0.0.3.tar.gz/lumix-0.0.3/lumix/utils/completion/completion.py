from typing import Union, Optional
from lumix.types.openai.literal import TypeRole, TypeFinishReason
from lumix.types.openai.sse import ChatCompletionChunk
from lumix.types.openai.sync import ChatCompletion

from .sync import *
from .chunk import *


__all__ = [
    "ali_chunk",
    "TransCompletionContent",
]


class TransCompletionContent:
    """"""
    def __init__(
            self,
            role: TypeRole = "assistant",
            content: Optional[str] = None,
            model: Optional[str] = None,
            finish_reason: Optional[TypeFinishReason] = None,
            chunk: Optional[ChatCompletionChunk] = None,
            **kwargs
    ):
        """"""
        self.role = role
        self.content = content
        self.model = model
        self.finish_reason = finish_reason
        self.chunk = chunk
        self.kwargs = kwargs

    def completion_chunk(self,) -> ChatCompletionChunk:
        """"""
        return chat_completion_chunk(
            self.role, self.content, chunk=self.chunk,
            model=self.model, finish_reason=self.finish_reason)

    def completion(self) -> ChatCompletion:
        """"""
        return chat_completion(
            role=self.role, content=self.content,
            model=self.model, finish_reason=self.finish_reason
        )


def ali_chunk(
        i: int, completion: Union[ChatCompletion, ChatCompletionChunk],
):
    """"""
    return f"id: {i}\ndata: {completion.model_dump_json()}\r\n\r\n".encode("utf-8")
