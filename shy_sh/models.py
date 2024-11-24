from typing import Optional, TypedDict, Annotated
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class ToolRequest(BaseModel):
    tool: str
    arg: str
    thoughts: Optional[str] = None


class FinalResponse(BaseModel):
    response: str


class ToolMeta(BaseModel):
    stop_execution: bool = False
    skip_print: bool = False


class State(TypedDict):
    input: str
    timestamp: str
    lang_spec: str
    ask_before_execute: bool = True
    tools_instructions: str | None = None
    few_shot_examples: Annotated[list, add_messages] = []
    history: Annotated[list, add_messages] = []
    tool_history: Annotated[list, add_messages] = []
