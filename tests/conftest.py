import pytest
from typer import Typer
from typer.testing import CliRunner
from shy_sh.main import exec as main
from tests.utils import mock_settings


@pytest.fixture(autouse=True)
def mock_app_settings():
    mock_settings(
        {
            "language": "esperanto",
            "llm": {
                "agent_pattern": "react",
                "api_key": "xxx",
                "name": "test",
                "provider": "ollama",
                "temperature": 1.0,
            },
            "vision_llm": {
                "api_key": "xxx",
                "name": "test",
                "provider": "ollama",
                "temperature": 1.0,
            },
        }
    )


@pytest.fixture(autouse=True)
def mock_readline(mocker):
    mocker.patch("readline.set_history_length")
    mocker.patch("readline.read_history_file")
    mocker.patch("readline.write_history_file")


@pytest.fixture()
def exec():
    runner = CliRunner()
    app = Typer()
    app.command()(main)

    def invoke(cmd, **kwargs):
        return runner.invoke(app, cmd.split(" "), **kwargs)

    return invoke
