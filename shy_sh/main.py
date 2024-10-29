import typer
from typing import Optional, Annotated

from shy_sh.agent.agent import ShyAgent
from shy_sh.settings import settings, configure_yaml
from rich import print


def exec(
    prompt: Annotated[Optional[list[str]], typer.Argument(allow_dash=False)] = None,
    interactive: Annotated[
        Optional[bool],
        typer.Option(
            "-i",
            help="Interactive mode [default false if a prompt is passed else false]",
        ),
    ] = False,
    configure: Annotated[
        Optional[bool], typer.Option("--configure", help="Configure LLM")
    ] = False,
):
    if configure:
        configure_yaml()
        return
    task = " ".join(prompt or [])
    print(f"[bold italic dark_orange]{settings.llm.provider} - {settings.llm.name}[/]")
    if not task:
        interactive = True
    else:
        print(f"✨: {task}\n")
    ShyAgent(interactive=interactive).start(task)


def main():
    typer.run(exec)


if __name__ == "__main__":
    main()
