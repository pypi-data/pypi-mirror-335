import json
from logging import Logger
from typing import Any, List, Dict, Union, Callable, Optional
from openai import OpenAI as OpenAIOriginal
from pydantic._internal._model_construction import ModelMetaclass
from lumix.api.openai import OpenAIMixin
from lumix.utils.logger import LoggerMixin
from lumix.types.messages import Message, TypeMessage
from lumix.types.openai.sync import ChatCompletion
from lumix.types.openai.sse import Stream, ChatCompletionChunk


__all__ = [
    "OpenAI",
]


class OpenAI(LoggerMixin, OpenAIMixin):
    """"""
    api_key: str
    client: OpenAIOriginal

    def __init__(
            self,
            model: str,
            base_url: Optional[str] = "https://api.openai.com/v1",
            api_key: Optional[str] = None,
            key_name: Optional[str] = None,
            client: Optional[OpenAIOriginal] = None,
            verbose: Optional[bool] = False,
            logger: Optional[Union[Logger, Callable]] = None,
            **kwargs: Any,
    ):
        """ Initialize a new instance of OpenAI client.

        Args:
            model:
                The model to use for completion.
            base_url:
                The base URL of the API endpoint.
            api_key:
                The API key used for authentication.
            key_name:
                The name of the API key used for authentication. If not provided, the first
                API key in the environment variables will be used.
            client:
                The HTTP client instance used to make requests to the API. This could be an instance
                of a library like `requests` or a custom client implementation.
            verbose:
                A boolean flag indicating whether to enable verbose output. When set to True,
                additional debugging information or logs will be displayed.
            logger:
                A logger instance used for logging messages.
            **kwargs:
                Additional keyword arguments.
        Examples:
            ```python
            from lumix.llm import OpenAI

            base_url = "https://open.bigmodel.cn/api/paas/v4"
            llm = OpenAI(model="glm-4-flash", base_url=base_url, api_key="your_api_key")
            ```
        """
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.key_name = key_name
        self.set_client(client)
        self.logger = logger
        self.verbose = verbose
        self.kwargs = kwargs

    def completion(
            self,
            prompt: Optional[str] = None,
            messages: Optional[Union[List[TypeMessage], List[Dict]]] = None,
            stream: Optional[bool] = False,
            tools: List[Dict] = None,
            **kwargs,
    ) -> Union[ChatCompletion | Stream[ChatCompletionChunk]]:
        """ Call OpenAI API to get a completion.

        Args:
            prompt: The prompt to generate a completion.
            messages: The messages to generate a completion.
            stream: Whether to stream the response or not.
            tools: The tools to generate a completion.
            **kwargs:

        Returns:
            Union[ChatCompletion | Stream[ChatCompletionChunk]]

        Examples:
            ```python
            completion = self.llm.completion(prompt="你好")
            print(completion.choices[0].message.content)
            ```
        """
        if prompt is not None:
            messages = [Message(role="user", content=prompt)]

        if not isinstance(messages[0], dict):
            messages = [msg.to_dict() for msg in messages]

        self._logger(msg=f"[User] {messages[-1].get("content")}\n", color="blue")
        completion = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=tools, stream=stream, **kwargs)
        if stream:
            return self.sse(completion)
        else:
            return self.sync(completion)

    def sse(self, completion: Stream[ChatCompletionChunk]) -> Stream[ChatCompletionChunk]:
        """"""
        content = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content
            yield chunk
        self._logger(msg=f"[Assistant] {content}\n", color="green")

    def sync(self, completion: ChatCompletion) -> ChatCompletion:
        """"""
        self._logger(msg=f"[Assistant] {completion.choices[0].message.content}\n", color="green")
        return completion

    def structured_schema(self, schema: ModelMetaclass,) -> List[Dict]:
        """"""
        json_schema = schema.model_json_schema()
        schema_tools = [{
            'type': 'function',
            'function': {
                'name': json_schema.get("title"),
                'description': json_schema.get("description"),
                "parameters": {
                    "type": "object",
                    'properties': json_schema.get("properties"),
                    'required': json_schema.get("required")
                },
            }}]
        return schema_tools

    def parse_dict(self, arguments: str) -> Dict:
        """"""
        try:
            return json.loads(arguments)
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}")

    def structured_output(
            self,
            schema: ModelMetaclass,
            prompt: Optional[str] = None,
            messages: Optional[Union[List[TypeMessage], List[Dict]]] = None,
            **kwargs
    ) -> Dict:
        """结构化输出

        Args:
            schema: 输出结构Scheme
            prompt: prompt
            messages: messages
            **kwargs:

        Returns:
            结构化数据

        Examples:
            ```python
            class Joke(BaseModel):
                '''Joke to tell user.'''
                setup: str = Field(description="The setup of the joke")
                punchline: str = Field(description="The punchline to the joke")
                rating: int = Field(description="How funny the joke is, from 1 to 10")

            data = self.llm.structured_output(schema=Joke, prompt="给我讲个简单的笑话")
            pprint(data)
            ```

        """
        schema_tools = self.structured_schema(schema)
        completion = self.completion(
            prompt=prompt, messages=messages, stream=False, tools=schema_tools, **kwargs)
        if completion.choices[0].message.tool_calls is not None:
            return self.parse_dict(completion.choices[0].message.tool_calls[0].function.arguments)
        else:
            content = completion.choices[0].message.content
            self.error(msg=f"[{__class__.__name__}] No structured data found in the response: {content}")
            return {}
