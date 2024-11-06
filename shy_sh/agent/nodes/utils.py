import json
from time import strftime
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from shy_sh.settings import settings
from shy_sh.utils import detect_shell, detect_os, run_shell
from shy_sh.agent.tools import tools
from shy_sh.models import ToolRequest


def get_graph_inputs(
    task: str,
    history: list,
    examples: list,
    ask_before_execute: bool,
):
    return {
        "input": task,
        "history": history,
        "timestamp": strftime("%Y-%m-%d %H:%M %Z"),
        "ask_before_execute": ask_before_execute,
        "lang_spec": settings.language or "",
        "few_shot_examples": examples,
        "tools_instructions": _format_tools(),
    }


def parse_react_tool(message):
    maybe_tool = message.content[
        message.content.index("{") : message.content.rindex("}") + 1
    ]
    return ToolRequest.model_validate_json(maybe_tool)


def has_tool_calls(message):
    if settings.llm.agent_pattern == "function_call":
        return bool(getattr(message, "tool_calls", None))
    elif settings.llm.agent_pattern == "react":
        try:
            parse_react_tool(message)
            return True
        except Exception:
            pass
    return False


def run_few_shot_examples():
    shell = detect_shell()
    os = detect_os()
    actions = [
        {
            "tool": "shell",
            "arg": "echo %cd%" if shell in ["powershell", "cmd"] else "pwd",
            "thoughts": "I'm checking the current working directory",
        },
        {
            "tool": "shell",
            "arg": "git rev-parse --abbrev-ref HEAD",
            "thoughts": "I'm checking if it's a git repository",
        },
    ]
    result = []
    result.append(
        HumanMessage(
            content=f"You are on {os} system using {shell} as shell. Check your tools"
        )
    )
    for action in actions:
        uid = uuid4().hex
        ai_message, response = _run_example(action, uid)
        result.append(ai_message)
        if settings.llm.agent_pattern == "react":
            result.append(HumanMessage(content=f"Tool response:\n{response}"))
        elif settings.llm.agent_pattern == "function_call":
            result.append(ToolMessage(content=response, tool_call_id=uid))
    result.append(AIMessage(content="Ok"))
    return result


def _run_example(action, uid):
    ai_message = AIMessage(content=json.dumps(action))
    if settings.llm.agent_pattern == "function_call":
        ai_message.tool_calls = [
            {
                "name": action["tool"],
                "args": {"arg": action["arg"]},
                "id": uid,
                "type": "tool_call",
            }
        ]
    return ai_message, run_shell(action["arg"])


def _format_tools():
    if settings.llm.agent_pattern == "function_call":
        return None
    return "\n".join(map(lambda tool: f'- "{tool.name}": {tool.description}', tools))
