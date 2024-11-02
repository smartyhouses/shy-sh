import subprocess
import pyperclip
from rich.syntax import Syntax
from shy_sh.agent.models import FinalResponse
from shy_sh.agent.utils import ask_confirm, decode_output
from rich import print


def shell_exec(arg: str, ask_before_execute: bool):
    print(f"🛠️ [bold green]{arg}[/bold green]")
    if ask_before_execute:
        confirm = ask_confirm()
        if confirm == "n":
            return FinalResponse(response="Task interrupted")
        elif confirm == "c":
            pyperclip.copy(arg)
            return FinalResponse(response="Command copied to the clipboard!")

    result = subprocess.run(
        arg,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout = decode_output(result) or "Success!"
    print(Syntax(stdout.strip(), "console", background_color="#212121"))
    return stdout
