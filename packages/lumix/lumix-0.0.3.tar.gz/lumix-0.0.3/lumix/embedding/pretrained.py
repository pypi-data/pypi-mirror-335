from lumix.types.embedding import Usage, Embedding, CreateEmbeddingResponse
from lumix.utils.logger import LoggerMixin
from lumix.embedding.base import EmbeddingMixin
from typing import Optional, Callable, Union, List, Tuple
from functools import lru_cache


__all__ = [
    "PretrainedEmbedding"
]


class PretrainedEmbedding(LoggerMixin, EmbeddingMixin):
    """"""
    def __init__(
            self,
            name_or_path: Optional[str] = None,
            batch_size: int = 32,
            normalize_embeddings: bool = False,
            device: Optional[str] = None,
            verbose: bool = False,
            logger: Optional[Callable] = None,
            **kwargs
    ):
        """"""
        # local
        self.name_or_path = name_or_path
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        self.device = device
        self.verbose = verbose
        self.logger = logger
        self.pretrained_model = self.from_pretrained()

    def __call__(
            self,
            text: Union[str, List[str]],
    ) -> CreateEmbeddingResponse:
        if isinstance(text, str):
            text = [text]
        return self.embedding(text=text)

    @lru_cache()
    def from_pretrained(self):
        """"""
        from sentence_transformers import SentenceTransformer
        if self.name_or_path:
            self._logger(msg=f"[{__class__.__name__}] Loading model ...", color="green")
            model = SentenceTransformer(self.name_or_path, device=self.device)
            self._logger(msg=f"[{__class__.__name__}] Success load model ...", color="green")
            return model
        else:
            raise ValueError(f"[{__class__.__name__}] Path: {self.name_or_path} not find.")

    @classmethod
    def tokens_usage(cls, text: List[str]) -> Usage:
        """"""
        tokens = sum([len(sample) for sample in text])
        usage = Usage(prompt_tokens=0, total_tokens=tokens)
        return usage

    @classmethod
    def trans_input_text(cls, text: Union[str, List[str]], ) -> List[str]:
        """"""
        if isinstance(text, str):
            text = [text]
        return text

    def embedding(
            self,
            text: Union[str, List[str], Tuple[str, ...]],
    ) -> CreateEmbeddingResponse:
        """"""
        text = self.trans_input_text(text=text)
        usage = self.tokens_usage(text=text)
        vectors = self.pretrained_model.encode(
            sentences=text, batch_size=self.batch_size, show_progress_bar=self.verbose,
            device=self.device, normalize_embeddings=self.normalize_embeddings,
        )
        emb = [Embedding(embedding=vec, index=i, object="embedding") for i, vec in enumerate(vectors)]
        return CreateEmbeddingResponse(data=emb, model=self.name_or_path, object='list', usage=usage)
