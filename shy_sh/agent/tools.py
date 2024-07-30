from typing import Callable, TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from .agent import ShyAgent


class Tool(ABC):
    def __init__(
        self, name: str | None = None, description: str | None = None, **kwargs
    ):
        self.name = name or self.__class__.__name__
        self.description = description or self.__doc__
        self.kwargs = kwargs

    @abstractmethod
    def execute(self, agent: "ShyAgent", payload: str): ...


def tool(*args, **kwargs) -> Tool:
    def decorator(fn: Callable):
        class ToolImpl(Tool):
            def execute(self, agent: "ShyAgent", payload: str):
                return fn(agent, payload)

        return ToolImpl(fn.__name__, fn.__doc__, **kwargs)

    if args:
        return decorator(args[0])
    return decorator
