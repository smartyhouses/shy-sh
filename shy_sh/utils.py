import os
import platform
import subprocess
from typing import Literal
from tiktoken import get_encoding
from rich.prompt import Prompt
from rich.syntax import Syntax
from langchain_core.messages import HumanMessage, ToolMessage


def ask_confirm(explain=True) -> Literal["y", "n", "c", "e"]:
    if explain:
        choiches = ["y", "n", "c", "e", "yes", "no", "copy", "explain"]
    else:
        choiches = ["y", "n", "c", "yes", "no", "copy"]

    return Prompt.ask(  # type: ignore
        f"\n[dark_orange]Do you want to execute this command?[/] [bold magenta][[underline]Y[/]es/[underline]n[/]o/[underline]c[/]opy{'/[underline]e[/]xplain' if explain else ''}][/]",
        choices=choiches,
        default="y",
        show_default=False,
        show_choices=False,
        case_sensitive=False,
    ).lower()[0]


PRINT_THEMES = {
    "response": {
        "theme": "one-dark",
        "background_color": "#181818",
    },
    "command": {
        "background_color": "#212121",
    },
}


def syntax(text: str, lexer: str = "console", theme: str = "response"):
    return Syntax(
        text,
        lexer,
        word_wrap=True,
        **PRINT_THEMES.get(theme, {}),  # type: ignore
    )


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


def decode_output2(text: bytes):
    try:
        response = text.decode()
    except UnicodeDecodeError:
        # windows
        import ctypes

        oemCP = ctypes.windll.kernel32.GetConsoleOutputCP()
        encoding = "cp" + str(oemCP)
        response = text.decode(encoding)
    return response


def run_shell(cmd: str):
    if cmd == "history" or cmd.startswith("history "):
        return get_shell_history()
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    return decode_output(result)


def stream_shell(cmd: str):
    if cmd == "history" or cmd.startswith("history "):
        return get_shell_history()
    result = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    while result.poll() is None:
        chunk = b""
        if result.stdout is not None and result.stdout.readable():
            chunk += result.stdout.read(1)
        yield decode_output2(chunk)
    remaining = b""
    if result.stdout is not None and result.stdout.readable():
        remaining += result.stdout.read()
    if result.stderr is not None and result.stderr.readable():
        remaining += result.stderr.read()

    if remaining:
        yield decode_output2(remaining)


def detect_shell():
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC") or "sh"
    shell = shell.lower().split("/")[-1]
    if "powershell" in shell:
        return "powershell"
    elif "cmd" in shell:
        return "cmd"

    return shell


def detect_os():
    system = platform.system() or "linux"
    if system.lower() == "darwin":
        return "macos"
    return system


def count_tokens(
    messages: list, encoding_name: str = "o200k_base", offset: int = 2000
) -> int:
    text = "\n".join(msg.content for msg in messages)
    encoding = get_encoding(encoding_name)
    return len(encoding.encode(text)) + offset


def tools_to_human(messages):
    return [
        HumanMessage(msg.content) if isinstance(msg, ToolMessage) else msg
        for msg in messages
    ]


HISTORY_FILES = {
    "bash": ".bash_history",
    "sh": ".bash_history",
    "zsh": ".zsh_history",
    "fish": ".local/share/fish/fish_history",
    "ksh": ".ksh_history",
    "tcsh": ".history",
}


def get_shell_history():
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
