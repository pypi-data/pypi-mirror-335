"""Utility decorators for PyErrorSchema.

This module provides decorators used throughout the PyErrorSchema package
for modifying function and class behavior.
"""

from functools import wraps
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def restrict_arguments(*forbidden_args: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator that disallows specific named arguments for a class method.

    Args:
        *forbidden_args (str): Arguments that are not allowed to be passed.

    Usage:
        ```
        @restrict_arguments("arg1", "arg2")
        def some_method(self, **kwargs):
            ...
        ```
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for arg in forbidden_args:
                if arg in kwargs:
                    raise ValueError(f"Overriding the '{arg}' field is not allowed.")
            return func(*args, **kwargs)
        return wrapper
    return decorator
