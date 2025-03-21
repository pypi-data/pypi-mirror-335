from typing import Literal


__all__ = [
    "TypeRole",
    "TypeFinishReason",
]

TypeRole = Literal["developer", "system", "user", "assistant", "tool"]
TypeFinishReason = Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
