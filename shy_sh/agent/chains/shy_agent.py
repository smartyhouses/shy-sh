from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain
from shy_sh.agent.chat_models import get_llm
from textwrap import dedent

sys_template = dedent(
    """
    You are a helpfull shell assistant. The current date and time is {timestamp}.
    Try to resolve the tasks that I request you to do.

    You can use the following tools to accomplish the tasks:
    {tools}
                        
    Rules:
    You can use only the tools provided in this prompt to accomplish the tasks
    If you need to use tools your response must be in JSON format with this structure: {{ "tool": "...", "arg": "...", "thoughts": "..." }}
    Use the shell and your other tools to gather all the information that you need before starting the actual task and also to double check the results if needed before giving the final answer
    After you completed the task output your final answer to the task {lang_spec}without including any json
    Answer truthfully with the informations you have
    You cannot use tools and complete the task with your final answer in the same message so remember to use the tools that you need first
    """
)


@chain
def shy_agent_chain(_):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", sys_template),
            MessagesPlaceholder("few_shot_examples", optional=True),
            MessagesPlaceholder("history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("tool_history", optional=True),
        ]
    )
    return prompt | llm | StrOutputParser()
