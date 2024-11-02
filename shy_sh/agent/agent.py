import subprocess
import json
from shy_sh.settings import settings
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from time import strftime
from rich import print
from rich.syntax import Syntax
from rich.live import Live
from shy_sh.agent.chains.shy_agent import shy_agent_chain
from shy_sh.agent.chains.python_expert import python_expert_chain
from shy_sh.agent.chains.shell_exec import shell_exec
from shy_sh.agent.chains.shell_expert import shell_expert_chain
from shy_sh.agent.chains.screenshot import screenshot_chain
from shy_sh.agent.utils import decode_output, detect_os, detect_shell

from .tools import tool
from .models import ToolRequest, FinalResponse


class ShyAgent:
    def __init__(
        self,
        max_iterations: int = 4,
        interactive=False,
        ask_before_execute=False,
        screenshot=False,
    ):
        self.max_iterations = max_iterations
        self.interactive = interactive
        self.ask_before_execute = ask_before_execute
        self.screenshot = screenshot
        self.history = []
        self.tools = self._get_tools()

    @property
    def formatted_tools(self):
        return "\n".join(
            map(lambda tool: f'- "{tool.name}": {tool.description}', self.tools)
        )

    def _get_tools(self):
        @tool
        def shell(arg: str):
            """to execute a shell command in the terminal, useful for every task that requires to interact with the current system or local files, do not pass interactive commands, avoid to install new packages if not explicitly requested"""
            return shell_exec(arg, self.ask_before_execute)

        @tool
        def python_expert(arg: str):
            """to delegate the task to a python expert that can write and execute python code, use only if you cant resolve the task with shell, just forward the task as argument without any python code"""
            return python_expert_chain(arg, self.history, self.ask_before_execute)

        @tool
        def shell_expert(arg: str):
            """to delegate the task to a shell expert that can write and execute complex shell scripts, use only if you cant resolve the task with a simple shell command, just forward the task as argument without any shell code"""
            return shell_expert_chain(arg, self.history, self.ask_before_execute)

        return [shell, shell_expert, python_expert]

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
            tool_answer = tool.execute(action.arg)
        except Exception as e:
            tool_answer = f"🚨 There was an error: {e}"
        return tool_answer

    def _get_few_shot_examples(self):
        shell = detect_shell()
        os = detect_os()
        actions = [
            {
                "tool": "shell",
                "arg": "echo %cd%" if shell in ['powershell','cmd'] else "pwd",
                "thoughts": "I'm checking the current working directory",
            },
            {
                "tool": "shell",
                "arg": "git rev-parse --abbrev-ref HEAD",
                "thoughts": "I'm checking if it's a git repository",
            },
        ]
        result = []
        result.append(HumanMessage(content=f"You are on {os} system using {shell} as shell. Check your tools"))
        for action in actions:
            result.append(AIMessage(content=json.dumps(action)))
            response = subprocess.run(
                action["arg"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            response = decode_output(response)

            result.append(HumanMessage(content=f"Tool response:\n{response}"))
        result.append(AIMessage(content="Ok"))
        return result

    def _update_task_with_image(self, task: str):
        result = screenshot_chain(task)
        return f"\nContext informations - This is what I'm seeing in my screen right now:\n{result}\n\nTask: {task}"

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
            for chunk in shy_agent_chain.stream(inputs):
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
        if self.screenshot:
            task = self._update_task_with_image(task)
            self.screenshot = False
        else:
            task = f"Task: {task}"
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
            else:
                print("🤖: 👋 Bye!")
