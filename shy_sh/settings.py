import os
import yaml

from typing import Type, Any

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from pydantic import BaseModel
from pathlib import Path
from rich.prompt import Prompt, FloatPrompt


class LLMSchema(BaseModel):
    provider: str
    name: str
    api_key: str = ""
    temperature: float = 0.0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=[
            "~/.config/shy/config.yml",
            "~/.config/shy/config.yaml",
            "./shy.yml",
            "./shy.yaml",
        ]
    )

    llm: LLMSchema = LLMSchema(provider="ollama", name="llama3.1")

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
    for f in settings.model_config["yaml_file"]:
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

    file_name = get_or_create_settings_path()

    with open(file_name, "w") as f:
        f.write(
            yaml.dump(
                {
                    "llm": {
                        "provider": provider,
                        "name": name,
                        "api_key": api_key,
                        "temperature": temperature,
                    },
                    "language": language,
                }
            )
        )

    print(f"Configuration saved to {file_name}")
