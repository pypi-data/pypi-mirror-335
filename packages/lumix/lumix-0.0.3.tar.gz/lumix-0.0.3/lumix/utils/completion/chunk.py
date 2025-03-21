from typing import Optional, Literal
from lumix.types.openai.literal import TypeRole
from lumix.types.openai.sse import *
from lumix.utils.string import random_string
from lumix.utils.time import int_time


__all__ = [
    "chat_completion_chunk"
]


def chat_completion_chunk(
        role: TypeRole,
        content: str,
        model: str,
        chunk: Optional[ChatCompletionChunk] = None,
        finish_reason: Optional[Literal["stop", "length", "tool_calls", "content_filter", "function_call"]] = None,
) -> ChatCompletionChunk:
    """"""
    choices = [Choice(delta=ChoiceDelta(role=role, content=content), index=0, finish_reason=finish_reason)]
    if chunk:
        _id = chunk.id
        created = chunk.created
        model = chunk.model
    else:
        _id = random_string()
        created = int_time()

    return ChatCompletionChunk(
        choices=choices, id=_id, created=created, model=model,
        object="chat.completion.chunk")
