from langchain_core.messages import AIMessage
from shy_sh.settings import settings
from shy_sh.models import State
from shy_sh.agents.llms import get_llm_context
from shy_sh.utils import count_tokens, syntax
from shy_sh.agents.chains.shy_agent import shy_agent_chain
from shy_sh.agents.misc import has_tool_calls
from rich.live import Live

console_theme = {
    "lexer": "console",
    "theme": "one-dark",
    "background_color": "#181818",
}

loading_str = "⏱️ Loading..."


def chatbot(state: State):
    final_message = None
    history = _compress_history(state["history"], state["tool_history"])
    with Live() as live:
        live.update(loading_str)
        for chunk in shy_agent_chain.stream({**state, "history": history}):
            final_message = chunk if final_message is None else final_message + chunk
            message = _parse_chunk_message(final_message)
            if _maybe_have_tool_calls(final_message, message):
                live.update(loading_str)
            else:
                live.update(
                    syntax(f"🤖: {message}"),
                    refresh=True,
                )
        message = _parse_chunk_message(final_message)
        ai_message = AIMessage(
            content=message, tool_calls=getattr(final_message, "tool_calls", [])
        )
        has_tools = has_tool_calls(ai_message)
        if not message or (settings.llm.agent_pattern == "react" and has_tools):
            live.update("")
        else:
            live.update(syntax(f"\n🤖: {message}"))
    return {"tool_history": [ai_message]}


def _maybe_have_tool_calls(message, parsed_message):
    return (
        not message.content
        or getattr(message, "tool_calls", None)
        or (parsed_message.startswith("{") and settings.llm.agent_pattern == "react")
    )


def _parse_chunk_message(chunk):
    if isinstance(chunk.content, list):
        return "".join(c.get("text") for c in chunk.content if c.get("type") == "text")
    else:
        return chunk.content


def _compress_history(history, tool_history):
    max_len = get_llm_context()
    tokens = count_tokens(history + tool_history)
    while tokens > max_len:
        history = history[2:]
        if not history:
            break
        tokens = count_tokens(history + tool_history)
    return history
