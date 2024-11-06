from rich import print
from rich.syntax import Syntax
from langgraph.graph import END
from shy_sh.models import State, ToolMeta


def final_response_edge(state: State):
    last_tool = state["tool_history"][-1]
    artifact = getattr(last_tool, "artifact", None)
    if isinstance(artifact, ToolMeta) and artifact.stop_execution:
        print(
            Syntax(
                f"🤖: {last_tool.content}",
                "console",
                theme="one-dark",
                background_color="#181818",
            )
        )
        return END
    print()
    return "chatbot"
