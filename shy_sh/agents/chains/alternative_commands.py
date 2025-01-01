import re
from langchain_core.runnables import chain
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from shy_sh.agents.llms import get_llm
from shy_sh.settings import settings
from shy_sh.utils import detect_shell
from textwrap import dedent
from rich.live import Live


msg_template = dedent(
    """
    Find some alternative commands or variation of the original that can be used to accomplish the same task as the given command.

    Generate only one line of code for each alternative command.
    Do not suggest alternatives that are not compatible with the current shell or operating system.
    Sort the commands by relevance and usefulness, the most relevant and useful commands should be at the top.
    Output each command in a separate block of code respecting the following format:

    # Max 1 line description of the command before each command block{lang_spec}
    ```
    command
    ```

    Given command: 
    ```
    {cmd}
    ```
    """
)

example_sh = dedent(
    """
    # List all files in the current directory in long format
    ```
    ls -l
    ```

    # List all files in the current directory in long format including hidden files
    ```
    ls -la
    ```

    # Find all files in the current directory and its subdirectories including hidden files
    ```
    find . -type f
    ```

    # Find all files in the current directory and print the full path
    ```
    find . -type f -print
    ```
    """
)

example_cmd = dedent(
    """
    # List all files in the current directory in long format including hidden files
    ```
    dir /A /B
    ```

    # Find all files in the current directory and its subdirectories
    ```
    dir /S
    ```

    # Find all files in the current directory and its subdirectories using tree
    ```
    tree /F
    ```

    # Find all files in the current directory and its subdirectories in plan ASCII
    ```
    tree /F /A
    ```
    """
)

example_psh = dedent(
    """
    # List all files in the current directory including hidden files
    ```
    Get-ChildItem -Force
    ```

    # Find all files in the current directory and its subdirectories
    ```
    Get-ChildItem -Recurse
    ```

    # List all file names in the current directory and its subdirectories, including hidden files
    ```
    Get-ChildItem -Recurse -Force -Name
    ```

    # List all directories in the current directory
    ```
    Get-ChildItem -Directory
    ```
    """
)


def get_example():
    shell = detect_shell()
    if shell == "powershell":
        return example_psh
    if shell == "cmd":
        return example_cmd
    return example_sh


@chain
def alternative_commands_chain(inputs):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpfull shell assistant. The current date and time is {timestamp}.\nYou are running on {system} using {shell} as shell",
            ),
            (
                "human",
                msg_template.format(cmd="ls", lang_spec=""),
            ),
            AIMessage(content=get_example()),
            MessagesPlaceholder("history"),
            ("human", msg_template),
        ]
    )
    return prompt | llm | StrOutputParser()


def get_alternative_commands(inputs):
    with Live() as live:
        live.update("⏱️ Finding an alternative solutions...")
        response = alternative_commands_chain.invoke(
            {
                **inputs,
                "lang_spec": (
                    f" in {settings.language} language" if settings.language else ""
                ),
            }
        )
        live.update("")
    return re.findall(r"([^\n]+)\n```[^\n]*\n([^\n]+)\n```", response)
