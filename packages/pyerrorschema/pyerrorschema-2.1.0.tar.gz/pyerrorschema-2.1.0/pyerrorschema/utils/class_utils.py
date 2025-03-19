"""Utility functions for class manipulation in PyErrorSchema.

This module provides helper functions for working with Python classes
and their relationships.
"""

import sys
from typing import Any


def get_parent_class(cls: type) -> Any:
    """Get the parent class of a given class.

    Args:
        cls (type): The class to get the parent of.

    Returns:
        Any: The parent class of the given class.
    """
    return sys.modules[cls.__module__].__dict__[cls.__qualname__.split('.')[0]]
