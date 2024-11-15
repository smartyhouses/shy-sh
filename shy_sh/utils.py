import os
import platform
import subprocess
from typing import Literal
from tiktoken import get_encoding
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage, ToolMessage


def ask_confirm() -> Literal["y", "n", "c"]:
    return Prompt.ask(
        "\n[dark_orange]Do you want to execute this command?[/dark_orange]",
        choices=["Y", "n", "c"],
        default="y",
        show_default=False,
        case_sensitive=False,
    ).lower()


def decode_output(process):
    try:
        response = process.stdout.decode() or process.stderr.decode()
    except UnicodeDecodeError:
        # windows
        import ctypes

        oemCP = ctypes.windll.kernel32.GetConsoleOutputCP()
        encoding = "cp" + str(oemCP)
        response = process.stdout.decode(encoding) or process.stderr.decode(encoding)
    return response


def run_shell(cmd: str):
    if cmd == "history" or cmd.startswith("history "):
        return _get_history()
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    return decode_output(result)


def detect_shell():
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC")
    shell = shell.lower().split("/")[-1]
    if "powershell" in shell:
        return "powershell"
    elif "cmd" in shell:
        return "cmd"

    return shell.lower()


def detect_os():
    return platform.system()


def count_tokens(
    messages: list, encoding_name: str = "o200k_base", offset: int = 2000
) -> int:
    text = "\n".join(msg.content for msg in messages)
    encoding = get_encoding(encoding_name)
    return len(encoding.encode(text)) + offset


def tools_to_human(messages):
    return [
        HumanMessage(msg.content) for msg in messages if isinstance(msg, ToolMessage)
    ]


HISTORY_FILES = {
    "bash": ".bash_history",
    "sh": ".bash_history",
    "zsh": ".zsh_history",
    "fish": ".local/share/fish/fish_history",
    "ksh": ".ksh_history",
    "tcsh": ".history",
}


def _get_history():
    try:
        shell = detect_shell()
        history_file = HISTORY_FILES[shell]
        with open(os.path.expanduser(f"~/{history_file}"), "r") as f:
            history = f.read()
        return "\n".join(
            [
                cmd
                for cmd in history.strip().split("\n")[:-1]
                if cmd != "shy"
                and not cmd.startswith("shy ")
                and ";shy " not in cmd
                and not cmd.endswith(";shy")
            ][-5:]
        )
    except Exception:
        return "I can't get the history for this shell"
