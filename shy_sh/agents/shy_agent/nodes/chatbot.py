from langchain_core.messages import AIMessage
from shy_sh.settings import settings
from shy_sh.models import State
from shy_sh.agents.llms import get_llm_context
from shy_sh.utils import count_tokens
from shy_sh.agents.chains.shy_agent import shy_agent_chain
from shy_sh.agents.misc import has_tool_calls
from rich.live import Live
from rich.syntax import Syntax

console_theme = {
    "lexer": "console",
    "theme": "one-dark",
    "background_color": "#181818",
}

loading_str = "⏱️ Loading..."


def chatbot(state: State):
    message = ""
    tool_calls = []
    history = _compress_history(state["history"], state["tool_history"])
    with Live() as live:
        live.update(loading_str)
        for chunk in shy_agent_chain.stream({**state, "history": history}):
            message += chunk.content
            if not message.startswith("{") or settings.llm.agent_pattern != "react":
                live.update(
                    Syntax(f"🤖: {message}", **console_theme),
                    refresh=True,
                )
            elif message.startswith("{") and settings.llm.agent_pattern == "react":
                live.update(loading_str)
            if hasattr(chunk, "tool_calls"):
                tool_calls += chunk.tool_calls
        ai_mmessage = AIMessage(content=message, tool_calls=tool_calls)
        if has_tool_calls(ai_mmessage):
            live.update("")
        else:
            live.update(
                Syntax(f"🤖: {message}", **console_theme),
            )
    return {"tool_history": [ai_mmessage]}


def _compress_history(history, tool_history):
    max_len = get_llm_context()
    tokens = count_tokens(history + tool_history)
    while tokens > max_len:
        history = history[2:]
        if not history:
            break
        tokens = count_tokens(history + tool_history)
    return history
