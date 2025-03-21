import numpy as np
from pydantic import BaseModel
from typing import List, Optional
from openai.types.embedding import Embedding
from openai.types.create_embedding_response import (
    Usage, CreateEmbeddingResponse as OpenAICreateEmbeddingResponse)


__all__ = [
    "Usage",
    "Embedding",
    "CreateEmbeddingResponse",
    "SimilarityMatch",
]


class CreateEmbeddingResponse(OpenAICreateEmbeddingResponse):
    """"""
    def to_numpy(self):
        """"""
        return np.array(self.to_list())

    def to_list(self):
        """"""
        return [emb.embedding for emb in self.data]


class SimilarityMatch(BaseModel):
    """"""
    source: str
    idx: List[int] = []
    target: List[str] = []
    score: List[float] = []
