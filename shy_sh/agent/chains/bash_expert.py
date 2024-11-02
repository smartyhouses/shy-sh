import os
import subprocess
from time import strftime
from rich.syntax import Syntax
from shy_sh.agent.models import FinalResponse
from langchain_core.runnables import chain
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from shy_sh.chat_models import get_llm
from textwrap import dedent
from rich import print
from uuid import uuid4

sys_template = dedent(
    """
    Output only a block of python code like this:
    ```sh
    #!/bin/bash
    set -e
    [your bash script]
    ```

    Don't write interactive commands or install new packages if not explicitly requested.
    Write a bash script that accomplishes the task.

    Task: {input}
    """
)


@chain
def _chain(_):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a bash expert. The current date and time is {timestamp}",
            ),
            MessagesPlaceholder("history", optional=True),
            ("human", sys_template),
        ]
    )
    return prompt | llm | StrOutputParser()


def bash_expert_chain(task: str, history, ask_before_execute: bool):
    print(f"👨‍💻 [bold yellow]Generating bash script...[/bold yellow]\n{task}\n\n")
    code = _chain.invoke(
        {
            "input": task,
            "timestamp": strftime("%Y-%m-%d %H:%M %Z"),
            "history": history,
        }
    )
    code = code.replace("```sh\n", "").replace("```", "")
    print(Syntax(code.strip(), "console", background_color="#212121"))
    print("\n")
    if ask_before_execute:
        confirm = (
            input(
                "\n[dark_orange]Do you want to execute this script? [Y/n]:[/dark_orange] "
            )
            or "y"
        )
        if confirm.lower() == "n":
            return FinalResponse(response="Task interrupted")

    file_path = f"/tmp/{uuid4().hex}.sh"
    with open(file_path, "w") as f:
        f.write(code)
    os.chmod(file_path, 0o755)
    result = subprocess.run(
        file_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout = result.stdout.decode() or result.stderr.decode() or "Done"
    print(Syntax(stdout.strip(), "console", background_color="#212121"))
    return f"Script executed:\n{code}\n\nOutput:\n{stdout}"
