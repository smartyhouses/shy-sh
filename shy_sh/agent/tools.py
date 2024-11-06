import pyperclip
import os
import re
from typing import Annotated
from io import StringIO
from tempfile import NamedTemporaryFile
from rich import print
from rich.syntax import Syntax
from rich.live import Live
from langgraph.prebuilt import InjectedState
from langchain.tools import tool
from contextlib import redirect_stdout, redirect_stderr
from shy_sh.models import State, ToolMeta
from shy_sh.utils import ask_confirm, detect_shell, detect_os
from shy_sh.agent.chains.python_expert import pyexpert_chain
from shy_sh.agent.chains.shell_expert import shexpert_chain
from shy_sh.utils import run_shell


@tool(response_format="content_and_artifact")
def shell(arg: str, state: Annotated[State, InjectedState]):
    """to execute a shell command in the terminal, useful for every task that requires to interact with the current system or local files, do not pass interactive commands, do not pass multiple lines commands, avoid to install new packages if not explicitly requested"""
    print(f"🛠️ [bold green]{arg}[/bold green]")
    confirm = "y"
    if state["ask_before_execute"]:
        confirm = ask_confirm()
    print()
    if confirm == "n":
        return "Task interrupted", ToolMeta(stop_execution=True)
    elif confirm == "c":
        pyperclip.copy(arg)
        return "Command copied to the clipboard!", ToolMeta(stop_execution=True)

    result = run_shell(arg) or "Success!"
    print(Syntax(result.strip(), "console", background_color="#212121"))
    return result, ToolMeta()


@tool(response_format="content_and_artifact")
def python_expert(arg: str, state: Annotated[State, InjectedState]):
    """to delegate the task to a python expert that can write and execute python code, use only if you cant resolve the task with shell, just explain what do you want to achieve in a short sentence in the arg without including any python code"""
    print(f"🐍 [bold yellow]Generating python script...[/bold yellow]\n")
    inputs = {
        **state,
        "input": arg,
    }
    code = ""
    with Live() as live:
        for chunk in pyexpert_chain.stream(inputs):
            code += chunk
            live.update(
                Syntax(code, "python", background_color="#212121"), refresh=True
            )
        code = code.replace("```python\n", "").replace("```", "")
        live.update(Syntax(code.strip(), "python", background_color="#212121"))

    confirm = "y"
    if state["ask_before_execute"]:
        confirm = ask_confirm()
    print()
    if confirm == "n":
        return "Command canceled by user", ToolMeta(stop_execution=True)
    elif confirm == "c":
        pyperclip.copy(code)
        return "Script copied to the clipboard!", ToolMeta(stop_execution=True)

    stdout = StringIO()
    stderr = StringIO()
    with redirect_stderr(stderr):
        with redirect_stdout(stdout):
            exec(code, {"__name__": "__main__"})
    output = stdout.getvalue().strip() or stderr.getvalue().strip()[-500:] or "Done"
    print(Syntax(output, "console", background_color="#212121"))
    return (
        f"\nScript executed:\n```python\n{code.strip()}\n```\n\nOutput:\n{output}",
        ToolMeta(),
    )


@tool(response_format="content_and_artifact")
def shell_expert(arg: str, state: Annotated[State, InjectedState]):
    """to delegate the task to a shell expert that can write and execute long and complex shell scripts, use only if you cant resolve the task with a simple shell command, just explain what do you want to achieve in a short sentence in the arg without including any shell code"""
    print(f"💻 [bold dark_green]Generating shell script...[/bold dark_green]\n")
    shell = detect_shell()
    system = detect_os()
    inputs = {
        **state,
        "input": arg,
        "system": system,
        "shell": shell,
    }
    code = ""
    with Live() as live:
        for chunk in shexpert_chain.stream(inputs):
            code += chunk
            live.update(
                Syntax(code, "console", background_color="#212121"), refresh=True
            )

        code = re.sub(r"```\S+\n", "", code).replace("```", "")
        live.update(
            Syntax(code.strip(), "console", background_color="#212121"), refresh=True
        )

    confirm = "y"
    if state["ask_before_execute"]:
        confirm = ask_confirm()
    print()
    if confirm == "n":
        return "Task interrupted", ToolMeta(stop_execution=True)
    elif confirm == "c":
        pyperclip.copy(code)
        return "Script copied to the clipboard!", ToolMeta(stop_execution=True)

    ext = ".sh"
    if shell == "cmd":
        ext = ".bat"
    elif shell == "powershell":
        ext = ".ps1"
    with NamedTemporaryFile("w+", suffix=ext, delete_on_close=False) as file:
        file.write(code)
        file.close()
        os.chmod(file.name, 0o755)
        result = run_shell(file.name) or "Done"
    print()
    print(Syntax(result.strip(), "console", background_color="#212121"))
    return f"Script executed:\n{code}\n\nOutput:\n{result}", ToolMeta()


tools = [shell, shell_expert, python_expert]
tools_by_name = {tool.name: tool for tool in tools}
