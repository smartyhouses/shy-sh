import subprocess
from rich.syntax import Syntax
from shy_sh.agent.models import FinalResponse
from rich import print


def bash_exec(arg: str, ask_before_execute: bool):
    print(f"🛠️ [bold green]{arg}[/bold green]")
    if ask_before_execute:
        confirm = (
            input(
                "\n[dark_orange]Do you want to execute this command? [Y/n]:[/dark_orange] "
            )
            or "y"
        )
        if confirm.lower() == "n":
            return FinalResponse(response="Task interrupted")

    result = subprocess.run(
        arg,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout = result.stdout.decode() or result.stderr.decode() or "Success!"
    print(Syntax(stdout.strip(), "console", background_color="#212121"))
    return stdout
