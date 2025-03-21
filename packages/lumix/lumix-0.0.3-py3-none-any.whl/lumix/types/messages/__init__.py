from .base import *
from .tool import *
from .image import ImageMessage
from typing import Union


TypeMessage = Union[
    Message,
    ToolMessage,
    ChoiceDelta,
    ImageMessage,
    ChatCompletionMessage,
]
