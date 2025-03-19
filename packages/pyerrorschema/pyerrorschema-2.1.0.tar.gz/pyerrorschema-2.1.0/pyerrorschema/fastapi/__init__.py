"""FastAPI integration for PyErrorSchema.

This module provides FastAPI-specific implementations of the ErrorSchema
and ErrGroup classes, allowing for seamless integration with FastAPI
applications.
"""

from .fastapi_base import FastAPIErrorSchema
from .fastapi_group import FastAPIErrGroup

__all__ = ["FastAPIErrorSchema", "FastAPIErrGroup"]
