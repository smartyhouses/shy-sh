from typing import Callable
from abc import ABC, abstractmethod


class Tool(ABC):
    def __init__(
        self, name: str | None = None, description: str | None = None, **kwargs
    ):
        self.name = name or self.__class__.__name__
        self.description = description or self.__doc__
        self.kwargs = kwargs

    @abstractmethod
    def execute(self, payload: str): ...


def tool(*args, **kwargs) -> Tool:
    def decorator(fn: Callable):
        class ToolImpl(Tool):
            def execute(self, payload: str):
                return fn(payload)

        return ToolImpl(fn.__name__, fn.__doc__, **kwargs)

    if args:
        return decorator(args[0])
    return decorator
