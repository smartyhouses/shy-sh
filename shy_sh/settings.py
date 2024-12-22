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
from questionary import unsafe_prompt, confirm, text, Style


class BaseLLMSchema(BaseModel):
    provider: str
    name: str
    api_key: str = ""
    temperature: float = 0.0


class LLMSchema(BaseLLMSchema):
    agent_pattern: Literal["function_call", "react"] = "react"


class _Settings(BaseModel):
    llm: LLMSchema = LLMSchema(provider="ollama", name="llama3.2")

    vision_llm: BaseLLMSchema | None = None

    language: str = ""


class Settings(BaseSettings, _Settings):
    model_config = SettingsConfigDict(
        yaml_file=[
            "~/.config/shy/config.yaml",
            "~/.config/shy/config.yml",
            "./shy.yaml",
            "./shy.yml",
        ]
    )

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
    for f in reversed(settings.model_config["yaml_file"]):  # type: ignore
        f = Path(f).expanduser()
        if os.path.exists(f):
            file_name = f
            break
    if not file_name:
        file_name = settings.model_config["yaml_file"][0]  # type: ignore
        file_name = Path(file_name).expanduser()
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
    return file_name


_text_style = {
    "qmark": "",
    "style": Style.from_dict(
        {
            "selected": "fg:darkorange noreverse",
            "question": "fg:ansigreen nobold",
            "highlighted": "fg:darkorange",
            "text": "fg:darkorange",
            "answer": "fg:darkorange nobold",
            "instruction": "fg:darkorange",
        }
    ),
}

_select_style = {
    "pointer": "►",
    "instruction": " ",
    **_text_style,
}


def _try_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return "Please enter a valid number"


def configure_yaml():

    questions = [
        {
            "type": "select",
            "name": "provider",
            "message": "Provider:",
            "choices": PROVIDERS,
            "default": settings.llm.provider,
            **_select_style,
        },
        {
            "type": "select",
            "name": "agent_pattern",
            "message": "Agent Pattern:",
            "choices": ["function_call", "react"],
            "default": settings.llm.agent_pattern,
            **_select_style,
        },
        {
            "type": "text",
            "name": "name",
            "message": "Model:",
            "default": settings.llm.name,
            **_text_style,
        },
        {
            "type": "password",
            "name": "api_key",
            "message": "API Key:",
            "default": settings.llm.api_key,
            **_text_style,
        },
        {
            "type": "text",
            "name": "temperature",
            "message": "Temperature:",
            "default": str(settings.llm.temperature),
            "validate": lambda x: _try_float(x),
            **_text_style,
        },
    ]

    llm = unsafe_prompt(questions)
    language = text("Language:", default=settings.language, **_text_style).unsafe_ask()

    llm["temperature"] = float(llm["temperature"])

    vision_llm = settings.vision_llm.model_dump() if settings.vision_llm else llm.copy()

    setup_vision = confirm(
        "Setup Vision Model?", default=False, **_text_style
    ).unsafe_ask()
    if setup_vision:
        vision_llm = configure_vision_model()

    file_name = get_or_create_settings_path()

    with open(file_name, "w") as f:
        f.write(
            yaml.dump(
                {
                    "llm": llm,
                    "vision_llm": vision_llm,
                    "language": language,
                }
            )
        )

    print(f"\nConfiguration saved to {file_name}")


def configure_vision_model():
    questions = [
        {
            "type": "select",
            "name": "provider",
            "message": "Provider:",
            "choices": PROVIDERS,
            "default": (
                settings.vision_llm.provider
                if settings.vision_llm
                else settings.llm.provider
            ),
            **_select_style,
        },
        {
            "type": "text",
            "name": "name",
            "message": "Model:",
            "default": (
                settings.vision_llm.name if settings.vision_llm else settings.llm.name
            ),
            **_text_style,
        },
        {
            "type": "password",
            "name": "api_key",
            "message": "API Key:",
            "default": (
                settings.vision_llm.api_key
                if settings.vision_llm
                else settings.llm.api_key
            ),
            **_text_style,
        },
        {
            "type": "text",
            "name": "temperature",
            "message": "Temperature:",
            "default": str(
                settings.vision_llm.temperature
                if settings.vision_llm
                else settings.llm.temperature
            ),
            "validate": lambda x: _try_float(x),
            **_text_style,
        },
    ]

    return unsafe_prompt(questions)
