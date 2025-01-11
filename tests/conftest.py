import pytest
from typer import Typer
from typer.testing import CliRunner
from shy_sh.main import exec as main
from tests.utils import mock_settings


def pytest_addoption(parser):
    parser.addoption(
        "--eval", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    is_eval = config.getoption("--eval")
    skip_eval = pytest.mark.skip(reason="need --eval option to run")
    for item in items:
        if ("eval" in item.keywords and not is_eval) or (
            "eval" not in item.keywords and is_eval
        ):
            item.add_marker(skip_eval)


@pytest.fixture(autouse=True)
def mock_app_settings(request):
    if "eval" in request.keywords:
        return
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
