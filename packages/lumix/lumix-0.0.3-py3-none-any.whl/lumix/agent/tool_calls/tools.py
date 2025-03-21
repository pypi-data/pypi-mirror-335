import traceback
from typing import Tuple
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional, Callable
from lumix.types.tools import Function
from .register import register_tool


__all__ = [
    "Tools",
]


class Tools(BaseModel):
    """"""
    descriptions: List[Dict] = Field(default=[], description="Description of the tool")
    hooks: Dict[str, Callable] = Field(default={}, description="Hooks of the tool")
    tools: List[Callable] = Field(default=None, description="List of function to be used as tools")
    params_fun: Optional[Callable] = Field(default=None, description="Function to clean the parameters of the tool")

    def __init__(self, tools: List[Callable], **kwargs):
        super().__init__(tools=tools, **kwargs)
        self.register_tools()

    def register_tools(self):
        """"""
        _ = [register_tool(hooks=self.hooks, descriptions=self.descriptions)(fun)for fun in self.tools]

    def validate_function(self, function: Function) -> Tuple[Function, Optional[str]]:
        """"""
        function = Function.model_validate(function.model_dump())
        if isinstance(function.arguments, str):
            return function, f"Arguments: {function.arguments}, Please use a valid JSON string for the arguments."
        elif function.name not in self.hooks:
            return function, f"Tool `{function.name}` not found. Please use a provided tool."
        else:
            return function, None

    def validate_run_error(self, error: str) -> str:
        """"""
        return f"执行失败，可能无数据或参数输入有误，请检查输出参数等信息。\n\nError:```\n{error}\n```"

    def dispatch_function(self, function: Function) -> Any:
        """"""
        function, validate_message = self.validate_function(function)
        if validate_message:
            return validate_message
        tool_call = self.hooks[function.name]
        try:
            ret = tool_call(**function.arguments)
        except:
            ret = self.validate_run_error(traceback.format_exc())
        return str(ret)

    def dispatch_data(self, function: Function) -> Any:
        """"""
        function, validate_message = self.validate_function(function)
        if validate_message:
            return validate_message
        tool_call = self.hooks[function.name]
        try:
            data = tool_call(**function.arguments).load()
            ret = data.to_frame(chinese_column=True).to_markdown()
        except:
            ret = self.validate_run_error(traceback.format_exc())
        return ret
