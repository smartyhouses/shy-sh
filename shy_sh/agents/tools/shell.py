import pyperclip
from typing import Annotated
from rich import print
from langgraph.prebuilt import InjectedState
from langchain.tools import tool
from shy_sh.models import State, ToolMeta
from shy_sh.utils import ask_confirm, run_shell, syntax, stream_shell
from shy_sh.agents.chains.explain import explain


@tool(response_format="content_and_artifact")
def shell(arg: str, state: Annotated[State, InjectedState]):
    """to execute a shell command in the terminal, useful for every task that requires to interact with the current system or local files, do not pass multiple lines commands, avoid to install new packages if not explicitly requested"""
    print(f"🛠️ [bold green]{arg}[/bold green]")
    confirm = "y"
    if state["ask_before_execute"]:
        confirm = ask_confirm()
    print()
    if confirm == "n":
        return "Command interrupted by the user", ToolMeta(
            stop_execution=True, skip_print=True
        )
    elif confirm == "c":
        pyperclip.copy(arg)
        return "Command copied to the clipboard!", ToolMeta(stop_execution=True)
    elif confirm == "e":
        inputs = {
            "task": state["history"][-1].content,
            "script_type": "shell command",
            "script": arg,
            "timestamp": state["timestamp"],
        }
        ret = explain(inputs)
        if ret:
            return ret

    result = ""
    for chunk in stream_shell(arg):
        print(chunk, end="", flush=True)
        result += chunk
    result = result or "Success"

    return result, ToolMeta()
