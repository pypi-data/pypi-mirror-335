from logging import Logger
from typing import List, Tuple, Literal, Callable, Optional, Union

from lumix.utils import LoggerMixin
from lumix.utils.completion import TransCompletionContent
from lumix.utils.string import random_string
from lumix.types.openai.sse import ChatCompletionChunk, Stream, ChoiceDeltaToolCall, ChoiceDeltaToolCallFunction
from lumix.types.openai.sync import ChatCompletion, ChatCompletionMessageToolCall, Function
from lumix.types.messages import TypeMessage, Message, ToolMessage, ChatCompletionMessage
from lumix.agent.tool_calls.tools import Tools
from lumix.llm import TypeLLM


__all__ = ["ToolsAgent"]


class ToolsAgent(LoggerMixin):
    """
    todo: 1. 区分Agent模型与Reasoning模型
    todo: 2. 增加sse模式
    """
    model: str
    api_key: Optional[str]
    api_key_name: Optional[str]
    base_url: str
    tools: Tools

    def __init__(
            self,
            llm: TypeLLM,
            tools: Tools,
            split: Literal["think"] = "think",
            parse_tool_type: Optional[Literal["vllm"]] = None,
            max_calls: int = 5,
            logger: Optional[Union[Logger, Callable]] = None,
            verbose: Optional[bool] = False,
    ):
        """"""
        self.llm = llm
        self.tools = tools
        self.split = split
        self.parse_tool_type = parse_tool_type
        self.max_calls = max_calls
        self.logger = logger
        self.verbose = verbose

    def completion(
            self,
            prompt: Optional[str] = None,
            messages: Optional[List[Message]] = None,
            stream: Optional[bool] = False,
            **kwargs,
    ) -> Union[ChatCompletion | Stream[ChatCompletionChunk]]:
        """"""
        if prompt is not None:
            messages = [Message(role="user", content=prompt)]
        self._logger(msg=f"[User] {messages[-1].content}\n", color="blue")
        if stream:
            return self.sse(messages)
        else:
            return self.sync(messages)

    def function_call_content_split(self) -> Tuple[str, str]:
        """"""
        if self.split == "think":
            return "<think>\n\n", "</think>\n\n"
        else:
            return "", ""

    def sync(
            self,
            messages: Optional[List[TypeMessage]] = None,
    ) -> ChatCompletion:
        """"""
        call_times = 0
        finish_reason = None
        completion: Optional[ChatCompletion] = None

        while finish_reason != "stop" and call_times < self.max_calls:
            completion = self.llm.completion(messages=messages, tools=self.tools.descriptions)
            finish_reason = completion.choices[0].finish_reason
            call_times += 1

            if completion.choices[0].finish_reason == "tool_calls":
                self._logger(msg=f"[Assistant]: {completion.choices[0].message.content}", color="green")
                messages.append(completion.choices[0].message)

                function = completion.choices[0].message.tool_calls[0].function
                self._logger(msg=f"[Assistant] name: {function.name}, arguments: {function.arguments}\n", color="green")

                observation = self.tools.dispatch_function(function=function)
                self._logger(msg=f"[Observation] \n{observation}\n", color="magenta")
                messages.append(ToolMessage(role="tool", content=observation, tool_call_id=completion.choices[0].message.tool_calls[0].id))

            elif completion.choices[0].finish_reason == "stop":
                self._logger(msg=f"[Assistant] {completion.choices[0].message.content}\n", color="green")

        if call_times >= self.max_calls:
            if completion and completion.choices[0].finish_reason == "tool_calls":
                function = completion.choices[0].message.tool_calls[0].function
                msg = f"[Assistant] 达到最大调用次数，模型未能给出最终回答。\n[Last Tool] Function: {function.name}, Arguments: {function.arguments}\n"
                self._logger(msg=msg, color="red")
            elif completion and completion.choices[0].finish_reason == "stop":
                pass
            else:
                self._logger(msg=f"[Assistant] Error: {completion}")
        return completion

    def parse_stream_tool_call(
            self,
            chunks: List[ChatCompletionChunk],
    ) -> ChatCompletionMessage:
        """"""
        if self.parse_tool_type == "vllm":
            name = ""
            arguments = ""
            _id = ""
            index = 0
            content = ""
            for chunk in chunks:
                if chunk.choices[0].delta.tool_calls:
                    _tool_call = chunk.choices[0].delta.tool_calls[0]
                    _id = _tool_call.id
                    index = _tool_call.index
                    if _tool_call.function.arguments:
                        arguments += _tool_call.function.arguments
                    if _tool_call.function.name:
                        name += _tool_call.function.name
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
            function = ChoiceDeltaToolCallFunction(name=name, arguments=arguments)
            tool_call = ChoiceDeltaToolCall(id=_id, index=index, function=function, name=name,)
        else:
            content = chunks[-1].choices[0].content
            tool_call = chunks[-1].choices[0].delta.tool_calls[0]
        try:
            arguments = eval(tool_call.function.arguments)
            arguments = tool_call.function.arguments
        except Exception as e:
            arguments = "{}"

        tool_call = ChatCompletionMessageToolCall(
            id=f"chatcmpl-tool-{random_string(length=32)}", type="function",
            function=Function(name=tool_call.function.name, arguments=arguments),
        )
        return ChatCompletionMessage(role="assistant", content=content, tool_calls=[tool_call])

    def sse(
            self,
            messages: Optional[List[TypeMessage]] = None,
    ) -> Stream[ChatCompletionChunk]:
        """"""
        finish_reason = None
        call_times = 0
        chunk: Optional[ChatCompletionChunk] = None
        chunks: List[ChatCompletionChunk] = []
        start_split, end_split = self.function_call_content_split()
        message: ChatCompletionMessage = ChatCompletionMessage(role="user", content="")

        yield TransCompletionContent(role="tool", content=start_split, model=self.llm.model).completion_chunk()

        while finish_reason != "stop" and call_times < self.max_calls:
            completion = self.llm.completion(messages=messages, tools=self.tools.descriptions, stream=True)
            call_times += 1
            chunks: List[ChatCompletionChunk] = []

            for chunk in completion:
                chunks.append(chunk)

                if chunk.choices[0].finish_reason == "stop":
                    chunk.choices[0].finish_reason = None
                    yield chunk
                    chunk.choices[0].finish_reason = "stop"
                    message = self.parse_stream_tool_call(chunks=chunks)
                    messages.append(message)
                    self._logger(msg=f"[Assistant]: {message.content}", color="green")

                elif chunk.choices[0].finish_reason == "tool_calls":
                    yield chunk
                    # parse tool call
                    message = self.parse_stream_tool_call(chunks=chunks)
                    messages.append(message)
                    self._logger(msg=f"[Assistant]: {message.content}", color="green")
                    if message.tool_calls:
                        msg = f"[Tool] Function: {message.tool_calls[0].function.name}; Arguments: {message.tool_calls[0].function.arguments}\n"
                        self._logger(msg=msg, color="yellow")
                        chunk = TransCompletionContent(role="assistant", content=msg, model=self.llm.model).completion_chunk()
                        yield chunk

                    # call tool response
                    observation = self.tools.dispatch_function(function=message.tool_calls[0].function)
                    self._logger(msg=f"[Observation]: \n{observation}\n", color="cyan")
                    yield TransCompletionContent(
                        role="tool", content=f"[Observation]: \n{observation}\n",
                        model=chunk.model, finish_reason=None, chunk=chunk,
                    ).completion_chunk()
                    messages.append(ToolMessage(role="tool", content=observation, tool_call_id=message.tool_calls[0].id))
                else:
                    yield chunk
            finish_reason = chunk.choices[0].finish_reason

        if call_times >= self.max_calls and chunks[-1].choices[0].finish_reason == "tool_calls":
            function = message.tool_calls[0].function
            msg = f"{end_split}[Assistant] 达到最大调用次数，模型未能给出最终回答。\n[Last Tool] Function: {function.name}, Arguments: {function.arguments}\n"
            chunk = TransCompletionContent(role="assistant", content=msg, model=self.llm.model, finish_reason=None).completion_chunk()
            yield chunk
            self._logger(msg=msg, color="green")
        else:
            if chunk and chunk.choices[0].finish_reason == "stop":
                message = messages[-1]
                chunk = TransCompletionContent(role="assistant", content=f"{end_split}{message.content}", model=self.llm.model, finish_reason=None).completion_chunk()
                yield chunk

            else:
                chunk = TransCompletionContent(role="assistant", content=f"错误结束。", model=self.llm.model, finish_reason=None).completion_chunk()
                self._logger(msg=f"[Assistant] {chunk.choices[0].delta.content}\n", color="green")
                yield chunk
        stop_chunk = TransCompletionContent(role="assistant", content="", model=self.llm.model, finish_reason="stop").completion_chunk()
        yield stop_chunk
