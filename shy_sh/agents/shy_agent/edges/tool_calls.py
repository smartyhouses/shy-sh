from langgraph.graph import END
from shy_sh.models import State
from shy_sh.agents.misc import has_tool_calls


def tool_calls_edge(state: State):
    last_message = state["tool_history"][-1]
    if has_tool_calls(last_message):
        return "tools"
    return END
