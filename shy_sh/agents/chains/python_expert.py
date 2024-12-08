from langchain_core.runnables import chain
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from shy_sh.agents.llms import get_llm
from textwrap import dedent

msg_template = dedent(
    """
    Output only a block of python code like this:
    ```python
    [your python code]
    ```

    Write a python script that accomplishes the task. Do not use interactive commands and try to avoid external libraries if not explicitly requested.
    Task: {input}
    """
)


@chain
def pyexpert_chain(_):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a python expert. The current date and time is {timestamp}",
            ),
            MessagesPlaceholder("history"),
            ("human", msg_template),
        ]
    )
    return prompt | llm | StrOutputParser()
