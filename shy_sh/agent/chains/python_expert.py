import pyperclip
from io import StringIO
from contextlib import redirect_stdout
from time import strftime
from rich.syntax import Syntax
from shy_sh.agent.models import FinalResponse
from langchain_core.runnables import chain
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from shy_sh.agent.chat_models import get_llm
from shy_sh.agent.utils import ask_confirm
from textwrap import dedent
from rich import print

sys_template = dedent(
    """
    Output only a block of python code like this:
    ```python
    [your python code]
    ```

    Do not wrap your script in if __name__ == "__main__": block

    Write a python script that accomplishes the task.
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
                "You are a python expert. The current date and time is {timestamp}",
            ),
            MessagesPlaceholder("history", optional=True),
            ("human", sys_template),
        ]
    )
    return prompt | llm | StrOutputParser()


def python_expert_chain(task: str, history, ask_before_execute: bool):
    print(f"🐍 [bold yellow]Generating python script...[/bold yellow]\n")
    code = _chain.invoke(
        {
            "input": task,
            "timestamp": strftime("%Y-%m-%d %H:%M %Z"),
            "history": history,
        }
    )
    code = code.replace("```python\n", "").replace("```", "")
    print(Syntax(code.strip(), "python", background_color="#212121"))
    if ask_before_execute:
        confirm = ask_confirm()
        if confirm == "n":
            return FinalResponse(response="Command canceled by user")
        elif confirm == "c":
            pyperclip.copy(code)
            return FinalResponse(response="Script copied to the clipboard!")
    stdout = StringIO()
    with redirect_stdout(stdout):
        exec(code)
    output = stdout.getvalue().strip() or "Done"
    print(Syntax(output, "python", background_color="#212121"))
    return f"\nScript executed:\n```python\n{code.strip()}\n```\n\nOutput:\n{output}"
