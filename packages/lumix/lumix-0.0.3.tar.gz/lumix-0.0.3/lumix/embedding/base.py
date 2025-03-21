import numpy as np
from typing import List, Union, Tuple, Optional
from lumix.types.embedding import CreateEmbeddingResponse, SimilarityMatch


__all__ = [
    "cosine_similarity",
    "EmbeddingMixin",
]


def cosine_similarity(
        vector1: np.array,
        vector2: np.array,
) -> np.array:
    """

    :param vector1:
    :param vector2:
    :return:
    """
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1, axis=1, keepdims=True)
    norm_vector2 = np.linalg.norm(vector2, axis=0, keepdims=True)
    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity


class EmbeddingMixin:
    """"""
    def embedding(
            self,
            text: Union[str, List[str], Tuple[str, ...]],
    ) -> CreateEmbeddingResponse:
        """"""
        return CreateEmbeddingResponse()

    def embedding_content(
            self,
            data: Union[List[str], CreateEmbeddingResponse] = None,
    ) -> CreateEmbeddingResponse:
        """"""
        if isinstance(data, (CreateEmbeddingResponse, np.ndarray)):
            return data
        else:
            return self.embedding(data)

    def similarity_matrix(
            self,
            source: Union[List[str], np.ndarray, CreateEmbeddingResponse] = None,
            target: Union[List[str], np.ndarray, CreateEmbeddingResponse] = None,
    ) -> np.ndarray:
        """"""
        source_vector = self.embedding_content(source).to_numpy()
        target_vector = self.embedding_content(target).to_numpy()
        matrix = cosine_similarity(source_vector, target_vector.T)
        return matrix

    def filter_item(
            self,
            src: Union[str, np.ndarray],
            idx: List[int],
            score: List[float],
            target: List[str],
            threshold: Optional[float] = 0.5,
    ) -> SimilarityMatch:
        """"""
        match = SimilarityMatch(source=src)
        for idx, _score, dst in zip(idx, score, target):
            if _score > threshold:
                match.idx.append(idx)
                match.target.append(dst)
                match.score.append(_score)
        return match

    def filter(self,
               source: Union[List[str], np.ndarray, CreateEmbeddingResponse] = None,
               target: Union[List[str], np.ndarray, CreateEmbeddingResponse] = None,
               top_n: Optional[int] = 1,
               threshold: Optional[float] = 0.5,
    ) -> List[SimilarityMatch]:
        """"""
        matrix = self.similarity_matrix(source=source, target=target)
        sorted_indices = np.argsort(-matrix, axis=1)
        sorted_matrix = np.sort(-matrix, axis=1)
        top_n_idx = sorted_indices[:, :top_n].tolist()
        top_n_score = np.abs(sorted_matrix[:, :top_n]).round(4).tolist()

        if isinstance(source, CreateEmbeddingResponse):
            source = source.to_list()
        if isinstance(target, CreateEmbeddingResponse):
            target = target.to_list()

        match_list = []
        for src, idx, score in zip(source, top_n_idx, top_n_score):
            match_list.append(self.filter_item(src, idx, score, threshold=threshold, target=target))
        return match_list
