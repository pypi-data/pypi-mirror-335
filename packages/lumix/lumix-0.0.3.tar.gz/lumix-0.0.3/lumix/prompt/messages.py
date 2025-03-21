from typing import Any, List, Callable, Optional
from lumix.prompt.template import PromptTemplate
from lumix.utils.logger import LoggerMixin
from lumix.types.messages import Message, SystemMessage, UserMessage
from lumix.embedding import TypeEmbedding


__all__ = [
    "MessagesPrompt",
]


class MessagesPrompt(LoggerMixin):
    """"""
    system_message: SystemMessage
    embedding: TypeEmbedding
    few_shot: List[Message]
    rerank: bool = False
    n_shot: Optional[int]
    prompt_template: Optional[PromptTemplate]
    verbose: Optional[bool]
    logger: Optional[Callable]

    def __init__(
            self,
            system_message: Optional[SystemMessage] = None,
            few_shot: Optional[List[Message]] = None,
            embedding: Optional[TypeEmbedding] = None,
            rerank: bool = False,
            n_shot: Optional[int] = 5,
            prompt_template: Optional[PromptTemplate] = None,
            verbose: Optional[bool] = False,
            logger: Optional[Callable] = None,
            *args, **kwargs
    ):
        """

        :param system_message:
        :param embedding:
        :param few_shot:
        :param rerank: 是否进行 few-shot 重排
        :param n_shot: 取 n 个样例
        :param support_system: 支持一些不支持消息系统机制的模型
        """
        self.system_message = system_message
        self.embedding = embedding
        self.few_shot = few_shot
        self.rerank = rerank
        self.n_shot = n_shot
        self.prompt_template = prompt_template
        self.verbose = verbose
        self.logger = logger
        self.args = args
        self.kwargs = kwargs

        # validate params
        self.validate_embedding()

    def validate_embedding(self):
        """"""
        if self.rerank and self.embedding is None:
            raise ValueError("Embedding is not provided.")

    def validate_few_shot(self):
        """ 验证few-shot是否有效 """
        if len(self.few_shot) % 2 != 0:
            raise ValueError("Few-shot prompts must be in pairs.")
        else:
            return True

    def rerank_few_shot(
            self,
            content: str,
    ) -> List[Message]:
        """

        :param content:
        :return:
        """
        user_content = [message.content for message in self.few_shot if message.role == 'user']
        matched = self.embedding.filter(source=[content], target=user_content, top_n=self.n_shot, threshold=0.5)
        content_matched = matched[0]
        idx = content_matched.idx

        new_shot = []
        for i in idx[::-1]:
            new_shot.append(self.few_shot[i * 2])
            new_shot.append(self.few_shot[i * 2 + 1])
        return new_shot

    def prompt_format(
            self,
            content: Optional[str] = None,
            **kwargs: Any,
    ) -> List[Message]:
        """"""
        messages = []

        if self.system_message:
            messages.append(self.system_message)
        if self.few_shot is not None and len(self.few_shot) > 0:
            if self.rerank:
                few_shot = self.rerank_few_shot(content)
                self._logger(
                    msg=f"[{__class__.__name__}]Reranked few-shot prompts: {int(len(few_shot) / 2)}",
                    color="green")
            else:
                few_shot = self.few_shot
            messages.extend(few_shot)

        if self.prompt_template:
            kwargs.update({"content": content})
            content = self.prompt_template.format_prompt(**kwargs).to_string()
        messages.append(UserMessage(content=content))
        return messages
