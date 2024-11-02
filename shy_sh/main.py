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
    no_ask: Annotated[
        Optional[bool],
        typer.Option(
            "-x",
            help="Do not ask for confirmation before executing scripts",
        ),
    ] = False,
    screenshot: Annotated[
        Optional[bool],
        typer.Option(
            "-s",
            help="Take a screenshot of the terminal before the execution",
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
    try:
        ShyAgent(
            interactive=interactive,
            ask_before_execute=not no_ask,
            screenshot=screenshot,
        ).start(task)
    except Exception as e:
        print(f"🚨 [bold red]{e}[/bold red]")


def main():
    typer.run(exec)


if __name__ == "__main__":
    main()
