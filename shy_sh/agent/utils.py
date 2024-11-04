from typing import Literal
import platform
import os
from tiktoken import get_encoding


def ask_confirm() -> Literal["y", "n", "c"]:
    return (
        input(
            "\n[dark_orange]Do you want to execute this command? [Y/n/c]:[/dark_orange] "
        )
        or "y"
    )[0].lower()


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


def detect_shell():
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC")
    shell = shell.lower()
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
