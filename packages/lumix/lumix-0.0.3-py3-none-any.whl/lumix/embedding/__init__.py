from .openai import *
from .pretrained import *
from typing import Union


TypeEmbedding = Union[
    OpenAIEmbedding,
    PretrainedEmbedding
]
