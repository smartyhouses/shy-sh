import typer
from typing import Optional, Annotated
from importlib.metadata import version
from shy_sh.agent.agent import ShyAgent
from shy_sh.settings import settings, configure_yaml
from rich import print


def exec(
    prompt: Annotated[Optional[list[str]], typer.Argument(allow_dash=False)] = None,
    interactive: Annotated[
        Optional[bool],
        typer.Option(
            "-i",
            help="Interactive mode [default false if a prompt is passed]",
        ),
    ] = False,
    ask_before_execute: Annotated[
        Optional[bool],
        typer.Option(
            "-a",
            help="Ask confirmation before executing scripts [default false]",
        ),
    ] = False,
    configure: Annotated[
        Optional[bool], typer.Option("--configure", help="Configure LLM")
    ] = False,
    display_version: Annotated[
        Optional[bool], typer.Option("--version", help="Show version")
    ] = False,
):
    if display_version:
        print(f"Version: {version(__package__ or 'shy-sh')}")
        return
    if configure:
        configure_yaml()
        return
    task = " ".join(prompt or [])
    print(f"[bold italic dark_orange]{settings.llm.provider} - {settings.llm.name}[/]")
    if not task:
        interactive = True
    else:
        print(f"✨: {task}\n")
    ShyAgent(interactive=interactive, ask_before_execute=ask_before_execute).start(task)


def main():
    typer.run(exec)


if __name__ == "__main__":
    main()
