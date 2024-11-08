from langchain_core.runnables import chain
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from shy_sh.agents.llms import get_llm
from textwrap import dedent


msg_template = dedent(
    """
    Output only a block of code like this:
    ```sh
    #!/bin/sh
    set -e
    [your shell script]
    ```

    This is a template for sh, but you should use the right shell syntaxt depending on your system.
    Don't write interactive commands or install new packages if not explicitly requested.
    Write a shell script that accomplishes the task.

    Task: {input}
    """
)


@chain
def shexpert_chain(_):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a shell expert. The current date and time is {timestamp}\nYou are running on {system} using {shell} as shell",
            ),
            MessagesPlaceholder("history", optional=True),
            ("human", msg_template),
        ]
    )
    return prompt | llm | StrOutputParser()
