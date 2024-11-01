from typing import Optional
from pydantic import BaseModel


class ToolRequest(BaseModel):
    tool: str
    arg: str
    thoughts: Optional[str] = None


class FinalResponse(BaseModel):
    response: str
