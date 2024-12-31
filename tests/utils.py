from shy_sh.settings import settings, _Settings
from shy_sh.agents.llms import get_llm
from langchain_community.llms.fake import FakeListLLM
from langchain_core.messages import AIMessage
from contextlib import contextmanager


def mock_settings(config):
    config = _Settings.model_validate(config)
    for key in config.model_dump().keys():
        setattr(settings, key, getattr(config, key))


@contextmanager
def mock_llm(mocker, responses=["test", "test2", "test3", "test4"]):
    def to_ai_message(x):
        return AIMessage(content=x)

    llm = FakeListLLM(responses=responses) | to_ai_message
    mocker.patch("shy_sh.agents.llms._get_llm", return_value=llm)
    yield llm
    get_llm.cache_clear()
