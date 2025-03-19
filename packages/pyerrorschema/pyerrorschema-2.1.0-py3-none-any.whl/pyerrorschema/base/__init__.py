"""Core error schema implementation for PyErrorSchema.

This package provides the base error schema classes and error group functionality
that form the foundation of the PyErrorSchema library.
"""

from .err_base import ErrorSchema
from .err_group import ErrGroup

__all__ = [
    "ErrorSchema",
    "ErrGroup",
]
