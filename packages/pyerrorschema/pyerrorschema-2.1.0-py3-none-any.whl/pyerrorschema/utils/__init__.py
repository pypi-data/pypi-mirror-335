"""Utility functions and helpers for PyErrorSchema.

This package provides common utilities used across the PyErrorSchema library,
including decorators and class manipulation functions.
"""

from .class_utils import get_parent_class
from .decorators import restrict_arguments

__all__ = ["restrict_arguments", "get_parent_class"]

