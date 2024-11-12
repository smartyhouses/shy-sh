import os
import yaml

from typing import Type, Any, Literal

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from pydantic import BaseModel
from pathlib import Path
from rich.prompt import Prompt, FloatPrompt


class BaseLLMSchema(BaseModel):
    provider: str
    name: str
    api_key: str = ""
    temperature: float = 0.0


class LLMSchema(BaseLLMSchema):
    agent_pattern: Literal["function_call", "react"] = "function_call"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=[
            "~/.config/shy/config.yaml",
            "~/.config/shy/config.yml",
            "./shy.yaml",
            "./shy.yml",
        ]
    )

    llm: LLMSchema = LLMSchema(provider="ollama", name="llama3.1")

    vision_llm: BaseLLMSchema | None = None

    language: str = ""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        **kwargs: Any,
    ):
        return (YamlConfigSettingsSource(settings_cls),)


settings = Settings()
PROVIDERS = ["ollama", "openai", "google", "anthropic", "groq", "aws"]


def get_or_create_settings_path():
    file_name = None
    for f in reversed(settings.model_config["yaml_file"]):
        f = Path(f).expanduser()
        if os.path.exists(f):
            file_name = f
            break
    if not file_name:
        file_name = settings.model_config["yaml_file"][0]
        file_name = Path(file_name).expanduser()
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
    return file_name


def configure_yaml():
    provider = Prompt.ask(
        "[green bold]Provider[/]",
        default=settings.llm.provider,
        show_choices=True,
        choices=PROVIDERS,
    )
    agent_pattern = Prompt.ask(
        "[green bold]Agent Pattern[/]",
        default=settings.llm.agent_pattern,
        show_choices=True,
        choices=["function_call", "react"],
    )
    name = Prompt.ask(
        "[green bold]Model[/]",
        default=settings.llm.name,
    )

    api_key = Prompt.ask(
        "[green bold]API Key[/]",
        default=settings.llm.api_key,
        password=True,
        show_default=False,
    )
    temperature = FloatPrompt.ask(
        "[green bold]Temperature[/]",
        default=settings.llm.temperature,
    )
    language = Prompt.ask(
        "[green bold]Language[/]",
        default=settings.language,
    )
    setup_vision = Prompt.ask(
        "[green bold]Do you want to setup a vision model?[/]",
        default="n",
        show_choices=True,
        choices=["y", "n"],
    )

    vision_llm = None
    if setup_vision == "y":
        vision_llm = configure_vision_model()

    file_name = get_or_create_settings_path()

    with open(file_name, "w") as f:
        f.write(
            yaml.dump(
                {
                    "llm": {
                        "provider": provider,
                        "agent_pattern": agent_pattern,
                        "name": name,
                        "api_key": api_key,
                        "temperature": temperature,
                    },
                    "vision_llm": vision_llm,
                    "language": language,
                }
            )
        )

    print(f"Configuration saved to {file_name}")


def configure_vision_model():
    provider = Prompt.ask(
        "[green bold]Provider[/]",
        show_choices=True,
        choices=PROVIDERS,
        default=(
            settings.vision_llm.provider
            if settings.vision_llm
            else settings.llm.provider
        ),
    )
    name = Prompt.ask(
        "[green bold]Model[/]",
        default=settings.vision_llm.name if settings.vision_llm else settings.llm.name,
    )

    api_key = Prompt.ask(
        "[green bold]API Key[/]",
        password=True,
        show_default=False,
        default=(
            settings.vision_llm.api_key if settings.vision_llm else settings.llm.api_key
        ),
    )
    temperature = FloatPrompt.ask(
        "[green bold]Temperature[/]",
        default=(
            settings.vision_llm.temperature
            if settings.vision_llm
            else settings.llm.temperature
        ),
    )

    return {
        "provider": provider,
        "name": name,
        "api_key": api_key,
        "temperature": temperature,
    }
