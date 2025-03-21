from pydantic import Field
from typing import Literal, Optional, Union
from .base import Message


__all__ = ["ToolMessage"]


class ToolMessage(Message):
    """"""
    role: Literal["tool"] = Field(default="tool", description="角色")
    content: str = Field(default=None, description="对话内容")
    name: Optional[str] = Field(default="", description="""The name of the function to call.""")
    tool_call_id: Optional[Union[int, str, dict]] = Field(default="", description="id")
