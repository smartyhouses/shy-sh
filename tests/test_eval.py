import pytest
import warnings
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from shy_sh.agents.misc import get_graph_inputs, run_few_shot_examples
from langgraph.graph import StateGraph, START, END
from shy_sh.agents.shy_agent.nodes.chatbot import chatbot
from shy_sh.agents.shy_agent.nodes.tools_handler import _get_tool_calls
from shy_sh.agents.shy_agent.edges.tool_calls import tool_calls_edge
from shy_sh.models import State


def tools_handler(state: State):
    last_message = state["tool_history"][-1]
    t_calls = _get_tool_calls(last_message)
    return {
        "tool_history": [
            ToolMessage(content=tc["args"]["arg"], tool_call_id=tc["id"])
            for tc in t_calls
        ]
    }


@pytest.fixture
def graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tools_handler)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tool_calls_edge)
    graph_builder.add_conditional_edges("tools", lambda _: END)

    return graph_builder.compile()


@pytest.fixture
def run_graph(graph):
    def _run(task):
        inputs = get_graph_inputs(
            history=[HumanMessage(content=task)],
            examples=run_few_shot_examples(),
            ask_before_execute=False,
        )
        return graph.invoke(inputs)["tool_history"]

    return _run


@pytest.mark.eval
def test_list_files(run_graph):
    history = run_graph("list files")
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]
    assert tool_msg.content.startswith("ls")


@pytest.mark.eval
def test_convert_image(run_graph):
    history = run_graph("convert test.png to jpg")
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]
    assert (
        tool_msg.content.startswith("convert")
        or tool_msg.content.startswith("magick")
        or tool_msg.content.startswith("mogrify")
        or tool_msg.content.startswith("sips")
    )


@pytest.mark.eval
def test_find_files(run_graph):
    history = run_graph("find all python files")
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]
    assert tool_msg.content.startswith("find")


@pytest.mark.eval
def test_terraform_base(run_graph):
    history = run_graph(
        "give me the command to apply the terraform configuration using the local.tfvars file"
    )
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]
    assert "terraform apply -var-file=local.tfvars" in tool_msg.content


@pytest.mark.eval
def test_terraform_advanced(run_graph):
    history = run_graph(
        "give me the terraform command to import the file base.json to the current state"
    )
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]
    assert (
        "terraform state" in tool_msg.content or "terraform import" in tool_msg.content
    )
    if "base.json" not in tool_msg.content:
        warnings.warn(
            f"base.json not found in terraform command, probably a wrong command\n`{tool_msg.content}`"
        )


@pytest.mark.eval
def test_git_diff(run_graph):
    history = run_graph("show me the git diff of the last commit")
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert "git diff" in tool_msg.content
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]


@pytest.mark.eval
def test_git_tag(run_graph):
    history = run_graph("tag with 1.0.0 and push it to remote, all in one command")
    tool_msg = [x for x in history if isinstance(x, ToolMessage)][0]
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell"' in x.content
    ]
    assert "git tag" in tool_msg.content
    assert "1.0.0" in tool_msg.content
    assert "git push origin" in tool_msg.content


@pytest.mark.eval
def test_python_expert_call(run_graph):
    history = run_graph("write a python script to say hello")
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "python_expert"' in x.content
    ]


@pytest.mark.eval
def test_shell_expert_call(run_graph):
    history = run_graph(
        "write a shell script to write 5 files with a small story inside"
    )
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell_expert"' in x.content
    ]


@pytest.mark.eval
def test_shell_history_call(run_graph):
    history = run_graph("show me the last 5 commands I ran")
    assert [
        True
        for x in history
        if isinstance(x, AIMessage) and '{"tool": "shell_history"' in x.content
    ]
