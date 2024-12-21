import pyperclip
from typing import Annotated
from io import StringIO
from rich import print
from rich.live import Live
from langgraph.prebuilt import InjectedState
from langchain.tools import tool
from contextlib import redirect_stdout, redirect_stderr
from shy_sh.models import State, ToolMeta
from shy_sh.utils import ask_confirm, tools_to_human, syntax
from shy_sh.agents.chains.python_expert import pyexpert_chain
from shy_sh.agents.chains.explain import explain


@tool(response_format="content_and_artifact")
def python_expert(arg: str, state: Annotated[State, InjectedState]):
    """to delegate the task to a python expert that can write and execute python code, use only if you cant resolve the task with shell, just explain what do you want to achieve in a short sentence in the arg without including any python code"""
    print(f"🐍 [bold yellow]Generating python script...[/bold yellow]\n")
    inputs = {
        "timestamp": state["timestamp"],
        "history": tools_to_human(state["history"] + state["tool_history"]),
        "input": arg,
    }
    code = ""
    with Live() as live:
        for chunk in pyexpert_chain.stream(inputs):
            code += chunk
            live.update(syntax(code, "python", "command"), refresh=True)
        code = code.replace("```python\n", "")
        code = code[: code.rfind("```")]
        live.update(syntax(code.strip(), "python", "command"))

    confirm = "y"
    if state["ask_before_execute"]:
        confirm = ask_confirm()
    print()
    if confirm == "n":
        return "Command canceled by user", ToolMeta(
            stop_execution=True, skip_print=True
        )
    elif confirm == "c":
        pyperclip.copy(code)
        return "Script copied to the clipboard!", ToolMeta(stop_execution=True)
    elif confirm == "e":
        inputs = {
            "task": arg,
            "script_type": "python script",
            "script": code,
            "timestamp": state["timestamp"],
        }
        ret = explain(inputs)
        if ret:
            return ret

    stdout = StringIO()
    stderr = StringIO()
    with redirect_stderr(stderr):
        with redirect_stdout(stdout):
            exec(code, {"__name__": "__main__"})
    output = stdout.getvalue().strip() or stderr.getvalue().strip()[-500:] or "Done"
    print(syntax(output, theme="command"))
    return (
        f"\nScript executed:\n```python\n{code.strip()}\n```\n\nOutput:\n{output}",
        ToolMeta(),
    )
