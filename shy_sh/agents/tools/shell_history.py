from typing import Annotated
from rich import print
from langgraph.prebuilt import InjectedState
from langchain.tools import tool
from shy_sh.models import State, ToolMeta
from shy_sh.utils import get_shell_history


@tool(response_format="content_and_artifact")
def shell_history(arg: str, state: Annotated[State, InjectedState]):
    """to get the history of the last commands executed by the user in the shell, useful to understand what the user has already tried, use it if the user asks to check a previous command launched before the chat started"""
    print(f"📜 [bold yellow]Let me check...[/bold yellow]\n")
    history = get_shell_history()
    return f"These are the last commands executed by the user:\n{history}", ToolMeta()
