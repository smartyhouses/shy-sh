import pytest
from langchain_core.messages import HumanMessage, AIMessage
from shy_sh.agents.chains.shell_expert import shexpert_chain
from shy_sh.agents.chains.python_expert import pyexpert_chain
from shy_sh.agents.chains.alternative_commands import get_alternative_commands
from shy_sh.utils import parse_code


@pytest.mark.eval
def test_shell_expert_base():
    code = shexpert_chain.invoke(
        {
            "input": "list files",
            "timestamp": "2022-01-01",
            "system": "linux",
            "shell": "bash",
            "history": [],
        }
    )
    code = parse_code(code)
    assert code.startswith("#!/")
    assert "set -e" in code
    assert "ls" in code


@pytest.mark.eval
def test_shell_expert_with_history():
    code = shexpert_chain.invoke(
        {
            "input": "create a script that works",
            "timestamp": "2022-01-01",
            "system": "linux",
            "shell": "bash",
            "history": [
                HumanMessage(content="list files"),
                AIMessage(content="""{"tool": "shell", "args": {"arg": "dir"}}"""),
                HumanMessage(content="I'm on linux"),
            ],
        }
    )
    code = parse_code(code)
    assert code.startswith("#!/")
    assert "ls" in code


@pytest.mark.eval
def test_python_expert_base():
    code = pyexpert_chain.invoke(
        {
            "input": "write a script that prints the current date and time plus the word 'hello'",
            "timestamp": "2022-01-01",
            "history": [],
        }
    )
    code = parse_code(code)
    assert "print(" in code
    assert "datetime" in code
    assert "now()" in code


@pytest.mark.eval
def test_alternatve_commands():
    result = get_alternative_commands(
        {
            "cmd": "ls *.py",
            "timestamp": "2022-01-01",
            "system": "linux",
            "shell": "bash",
            "history": [HumanMessage(content="find all python files")],
        }
    )
    cmds = [r[1] for r in result]
    assert [True for r in result if "find" in r[1]]
    assert [True for r in result if "ls" in r[1]]


@pytest.mark.eval
def test_alternatve_commands_powershell():
    result = get_alternative_commands(
        {
            "cmd": "ls *.py",
            "timestamp": "2022-01-01",
            "system": "windows",
            "shell": "powershell",
            "history": [HumanMessage(content="find all python files")],
        }
    )

    assert [True for r in result if "Get-ChildItem" in r[1]]
