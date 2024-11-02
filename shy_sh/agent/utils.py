from typing import Literal


def ask_confirm() -> Literal["y", "n", "c"]:
    return (
        input(
            "\n[dark_orange]Do you want to execute this command? [Y/n/c]:[/dark_orange] "
        )
        or "y"
    )[0].lower()
