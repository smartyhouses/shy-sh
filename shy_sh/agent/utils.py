from typing import Literal
import platform
import os


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
        encoding = 'cp'+str(oemCP)
        response = process.stdout.decode(encoding) or process.stderr.decode(encoding)
    return response

def detect_shell():
    shell = os.environ.get('SHELL') or os.environ.get('COMSPEC')
    shell = shell.lower()
    if 'powershell' in shell:
        return 'powershell'
    elif 'cmd' in shell:
        return 'cmd'
    
    return shell.lower()

def detect_os():
    return platform.system()