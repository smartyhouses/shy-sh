from rich import print
from langgraph.graph import END
from shy_sh.models import State, ToolMeta
from shy_sh.settings import settings
from shy_sh.utils import syntax


def final_response_edge(state: State):
    last_tool = state["tool_history"][-1]
    artifact = getattr(last_tool, "artifact", None)
    if isinstance(artifact, ToolMeta) and artifact.stop_execution:
        message = last_tool.content
        if settings.llm.agent_pattern == "react":
            message = message.replace("Tool response:\n", "", 1)
        if not artifact.skip_print:
            print(syntax(f"🤖: {message}"))
        return END
    print()
    return "chatbot"
