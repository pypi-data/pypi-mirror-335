# pylint: disable=missing-class-docstring, missing-module-docstring

from typing import Generic, Literal, Optional

from pydantic import BaseModel
from typing_extensions import TypeVar

ResponseFormatT = TypeVar("ResponseFormatT", bound=BaseModel)


class ToolCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


class Usage(BaseModel):
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class Generation(BaseModel):
    content: Optional[str] = None
    finish_reason: Optional[
        Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
    ] = None
    role: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    usage: Optional[Usage] = None


class ParsedGeneration(Generation, Generic[ResponseFormatT]):
    parsed: Optional[ResponseFormatT] = None
