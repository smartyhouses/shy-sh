import re
from langchain_core.runnables import chain
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from shy_sh.agents.llms import get_llm
from shy_sh.settings import settings
from textwrap import dedent
from rich.live import Live


msg_template = dedent(
    """
    Find some alternative commands or variation of the original that can be used to accomplish the same task as the given command.

    The commands should be compatible with the current system and shell.
    Generate only one line of code for each alternative command and prepend it with a small and concise description of what it does.
    Output each command in a separate block of code like this:

    # Max 1 line description of the command{lang_spec}
    ```
    command
    ```

    Given command: 
    ```
    {cmd}
    ```
    """
)


@chain
def alternative_commands_chain(_):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpfull shell assistant. The current date and time is {timestamp}.\nYou are running on {system} using {shell} as shell",
            ),
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
    return re.findall(r"([^\n]+)\n```[a-z]*\n([^\n]+)\n```", response)
