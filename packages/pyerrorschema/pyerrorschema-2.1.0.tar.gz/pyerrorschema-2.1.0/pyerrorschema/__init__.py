"""PyErrorSchema: A structured error handling library for Python applications.

This library provides a robust framework for creating, managing, and handling
errors in a consistent and type-safe manner, with special support for FastAPI
applications.
"""

from .base import ErrGroup, ErrorSchema
from .fastapi import FastAPIErrGroup, FastAPIErrorSchema
from .mappings import ExceptionMapper

__all__ = [
    "ExceptionMapper",
    "FastAPIErrorSchema",
    "FastAPIErrGroup",
    "ErrorSchema",
    "ErrGroup",
]
