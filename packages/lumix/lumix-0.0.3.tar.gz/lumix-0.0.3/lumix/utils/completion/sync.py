from typing import Optional
from lumix.types.openai.literal import *
from lumix.types.openai.sync import *
from lumix.utils.time import int_time
from lumix.utils.string import random_string


__all__ = [
    "chat_completion"
]


def chat_completion(
        role: TypeRole,
        content: str,
        model: str,
        prompt_tokens: Optional[int] = 0,
        completion_tokens: Optional[int] = 0,
        total_tokens: Optional[int] = 0,
        finish_reason: Optional[TypeFinishReason] = "stop",
        **kwargs,
) -> ChatCompletion:
    """"""
    if finish_reason is None:
        finish_reason = "stop"

    message = ChatCompletionMessage(role=role, content=content, )
    choices = [Choice(message=message, index=0, finish_reason=finish_reason)]
    usage = CompletionUsage(
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
        total_tokens=total_tokens)
    return ChatCompletion(
        choices=choices, id=random_string(),
        created=int_time(), model=model,
        object="chat.completion", usage=usage)
