from langchain_core.messages import AIMessage
from shy_sh.settings import settings
from shy_sh.models import State
from shy_sh.agent.chains.shy_agent import shy_agent_chain
from shy_sh.agent.nodes.utils import has_tool_calls
from rich.live import Live
from rich.syntax import Syntax


def chatbot(state: State):
    message = ""
    tool_calls = []
    with Live() as live:
        for chunk in shy_agent_chain.stream(state):
            message += chunk.content
            if not message.startswith("{") or settings.llm.agent_pattern != "react":
                live.update(
                    Syntax(
                        f"🤖: {message}",
                        "console",
                        theme="one-dark",
                        background_color="#181818",
                    ),
                    refresh=True,
                )
            if hasattr(chunk, "tool_calls"):
                tool_calls += chunk.tool_calls
        ai_mmessage = AIMessage(content=message, tool_calls=tool_calls)
        if has_tool_calls(ai_mmessage):
            live.update("")
        else:
            live.update(
                Syntax(
                    f"🤖: {message}",
                    "console",
                    theme="one-dark",
                    background_color="#181818",
                ),
            )
    return {"tool_history": [ai_mmessage]}
