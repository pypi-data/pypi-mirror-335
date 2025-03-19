"""Type definitions for the PyErrorSchema package."""

from typing import Literal

from typing_extensions import TypeAlias

MsgType: TypeAlias = Literal["backend", "frontend"]

__all__ = ["MsgType"]
