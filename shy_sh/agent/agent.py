import subprocess
import json
from typing import Optional
from textwrap import dedent
from shy_sh.settings import settings
from shy_sh.chat_models import get_llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel
from time import strftime
from rich import print
from rich.syntax import Syntax
from rich.live import Live
from contextlib import redirect_stdout
from io import StringIO

from .tools import tool


class ToolRequest(BaseModel):
    tool: str
    arg: str
    thoughts: Optional[str] = None


class FinalResponse(BaseModel):
    response: str


class ShyAgent:
    def __init__(
        self, max_iterations: int = 4, interactive=False, ask_before_execute=False
    ):
        self.max_iterations = max_iterations
        self.interactive = interactive
        self.ask_before_execute = ask_before_execute
        self.history = []
        self.tools = self._get_tools()
        self.llm = get_llm()
        self.sys_template = dedent(
            """
            You are a helpfull shell assistant. The current date and time is {timestamp}.
            Try to resolve the tasks that I request you to do.
            
            You can use the following tools to accomplish the tasks:
            {tools}
                                
            Rules:
            You can use only the tools provided in this prompt to accomplish the tasks
            If you need to use tools your response must be in JSON format with this structure: {{ "tool": "...", "arg": "...", "thoughts": "..." }}
            Ensure to gather all the informations that you need using tools and then double check the output of the tools if needed before giving the final answer
            After you completed the task output your final answer to the task {lang_spec}without including any json
            Answer truthfully with the informations you have
            You cannot use tools and complete the task with your final answer in the same message so remember to use the tools that you need first
            """
        )

        self.python_expert_template = dedent(
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

    @property
    def chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.sys_template),
                MessagesPlaceholder("few_shot_examples", optional=True),
                MessagesPlaceholder("history", optional=True),
                ("human", "Task: {input}"),
                MessagesPlaceholder("tool_history", optional=True),
            ]
        )
        return prompt | self.llm | StrOutputParser()

    @property
    def python_expert_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a python expert. The current date and time is {timestamp}",
                ),
                MessagesPlaceholder("history", optional=True),
                ("human", self.python_expert_template),
            ]
        )
        return prompt | self.llm | StrOutputParser()

    @property
    def formatted_tools(self):
        return "\n".join(
            map(lambda tool: f'- "{tool.name}": {tool.description}', self.tools)
        )

    def _get_tools(self):
        @tool
        def bash(agent, arg: str):
            """to execute a bash command in the terminal, useful for every task that requires to interact with the current system or local files, do not pass interactive commands"""
            print(f"🛠️ [bold green]{arg}[/bold green]")
            if self.ask_before_execute:
                confirm = (
                    input(
                        "\n[dark_orange]Do you want to execute this command? [Y/n]:[/dark_orange] "
                    )
                    or "y"
                )
                if confirm.lower() == "n":
                    return FinalResponse(response="Task interrupted")
            result = subprocess.run(
                arg,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            stdout = result.stdout.decode() or result.stderr.decode() or "Success!"
            print(Syntax(stdout.strip(), "console", background_color="#212121"))
            return stdout

        @tool
        def python_expert(agent, arg: str):
            """to delegate the task to a python expert that can write and execute python code, use only if you cant resolve the task with bash, just forward the task as argument without any python code"""
            print(f"🐍 [bold yellow]Generating python script...[/bold yellow]\n")
            code = self.python_expert_chain.invoke(
                {
                    "input": arg,
                    "timestamp": strftime("%Y-%m-%d %H:%M %Z"),
                    "history": self.history,
                }
            )
            code = code.replace("```python\n", "").replace("```", "")
            print(Syntax(code.strip(), "python", background_color="#212121"))
            if self.ask_before_execute:
                confirm = (
                    input(
                        "\n[dark_orange]Do you want to execute this script? [Y/n]:[/dark_orange] "
                    )
                    or "y"
                )
                if confirm.lower() == "n":
                    return FinalResponse(response="Task interrupted")
            stdout = StringIO()
            with redirect_stdout(stdout):
                exec(code)
            output = stdout.getvalue().strip()
            output = ("\n" + output) if output else "Done"
            return FinalResponse(response=output)

        return [bash, python_expert]

    def _check_json(self, text: str):
        if text.count("{") > 0 and text.count("{") - text.count("}") == 0:
            first_bracket = text.index("{")
            last_bracket = text.rindex("}")
            maybe_tool = text[first_bracket : last_bracket + 1]
            if "mixtral" in settings.llm.name:
                maybe_tool = maybe_tool.replace("\\_", "_")  # fix mixtral bias
            try:
                return ToolRequest.model_validate_json(maybe_tool)
            except Exception:
                pass
        return text

    def _handle_tool(self, action: ToolRequest):
        tool = next((t for t in self.tools if t.name == action.tool), None)
        if tool is None:
            return f"Tool {action.tool} not found"
        try:
            tool_answer = tool.execute(self, action.arg)
        except Exception as e:
            tool_answer = f"🚨 There was an error: {e}"
        return tool_answer

    def _get_few_shot_examples(self):
        actions = [
            {
                "tool": "bash",
                "arg": "echo $OSTYPE",
                "thoughts": "I'm trying to find out the operating system type",
            },
            {
                "tool": "bash",
                "arg": "pwd",
                "thoughts": "I'm checking the current working directory",
            },
            {
                "tool": "bash",
                "arg": "git rev-parse --abbrev-ref HEAD",
                "thoughts": "I'm checking if it's a git repository",
            },
        ]
        result = []
        result.append(HumanMessage(content="Tools check"))
        for action in actions:
            result.append(AIMessage(content=json.dumps(action)))
            response = subprocess.run(
                action["arg"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            response = response.stdout.decode() or response.stderr.decode()

            result.append(HumanMessage(content=f"Tool response:\n{response}"))
        result.append(AIMessage(content="Ok"))
        return result

    def _execute(
        self,
        task: str,
        few_shot_examples: list[BaseMessage] = [],
    ):
        inputs = {
            "input": task,
            "timestamp": strftime("%Y-%m-%d %H:%M %Z"),
            "few_shot_examples": few_shot_examples,
            "history": self.history,
            "tool_history": self.tool_history,
            "tools": self.formatted_tools,
            "lang_spec": (
                f"translated in {settings.language} language "
                if settings.language
                else ""
            ),
        }

        stream_text = ""
        with Live() as live:
            loading = "⏱️  Loading..."
            live.update(loading)
            for chunk in self.chain.stream(inputs):
                stream_text += chunk
                if stream_text.startswith("{"):
                    live.update(loading)
                else:
                    live.update(f"🤖: {stream_text}", refresh=True)
                result = self._check_json(stream_text)
                if isinstance(result, ToolRequest):
                    live.update("")
                    self.tool_history.append(
                        AIMessage(content=result.model_dump_json())
                    )
                    result = self._handle_tool(result)
                    self.tool_history.append(
                        HumanMessage(content=f"Tool response:\n{result}")
                    )
                    return result
            live.update("")
        return FinalResponse(response=result)

    def _run(self, task: str, examples: list[BaseMessage] = []):
        answer = ""
        for _ in range(self.max_iterations):
            answer = self._execute(task, examples)

            if isinstance(answer, FinalResponse):
                return answer.response
        return answer

    def start(self, task: str):
        self.tool_history = []
        examples = self._get_few_shot_examples()
        answer = None
        if task:
            answer = self._run(task, examples)
            print(
                Syntax(
                    f"🤖: {answer}",
                    "console",
                    theme="one-dark",
                    background_color="#181818",
                )
            )
        if self.interactive:
            new_task = input("\n✨: ")
            print()
            if new_task != "exit":
                self.history.append(HumanMessage(content=task))
                self.history += self.tool_history
                if answer:
                    self.history.append(AIMessage(content=answer))

                self.start(new_task)
