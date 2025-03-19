"""Exception to error type mapping utility for PyErrorSchema.

This module provides the ExceptionMapper class which handles mapping Python exceptions
to standardized error types based on configured schema mappings.
"""

from functools import lru_cache
from typing import ClassVar, Dict, Final, Optional, Tuple

from .exceptions import (
    DEFAULT_ERROR_TYPE,
    EXCEPTION_MAPPINGS_BASE,
    EXCEPTION_MAPPINGS_FASTAPI,
)

SCHEMA_TO_MAPPINGS = {
    "ErrorSchema": EXCEPTION_MAPPINGS_BASE,
    "FastAPIErrorSchema": EXCEPTION_MAPPINGS_FASTAPI,
}


class ExceptionMapper:
    """Mapper between exception types and error types.

    The mapping structure is organized as:
    {
        'module_name': {
            'exception_class_name': 'error_type'
        }
    }
    """

    _default_schema_name: Final[str] = "ErrorSchema"
    _default_error_type: Final[str] = DEFAULT_ERROR_TYPE
    _valid_schemas: ClassVar[frozenset] = frozenset(SCHEMA_TO_MAPPINGS.keys())

    @classmethod
    def validate_schema(cls, schema_name: str) -> None:
        """Validate that the schema name is known."""
        if schema_name not in cls._valid_schemas:
            raise ValueError(
                f"Unknown schema: {schema_name}. "
                f"Valid schemas are: {sorted(cls._valid_schemas)}"
            )

    @classmethod
    @lru_cache(maxsize=None)
    def get_mapping(
        cls,
        schema_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Get the mapping between exception types and error types.

        Args:
            schema_name: Optional name of the schema to use. If None, uses default schema.

        Returns:
            Dictionary mapping module names to their exception mappings
        """
        schema_name = schema_name or cls._default_schema_name
        cls.validate_schema(schema_name)
        return SCHEMA_TO_MAPPINGS[schema_name]

    @classmethod
    @lru_cache(maxsize=128)
    def get_error_type(
        cls,
        schema_name: str,
        exc_module: str,
        exc_class: str,
    ) -> Optional[str]:
        """Get the error type for a given exception type.

        Args:
            schema_name: Name of the schema to use
            exc_module: Module name of the exception
            exc_class: Class name of the exception

        Returns:
            Mapped error type or default error type if no mapping exists
        """
        mapping = cls.get_mapping(schema_name)
        error_type = (
            mapping
            .get(exc_module, {})
            .get(exc_class, None)
        )
        return error_type

    @classmethod
    def get_error_type_from_exception(
        cls,
        schema_name: str,
        exc: Exception,
    ) -> str:
        """Map an exception instance to its corresponding error type.

        This method traverses the exception's inheritance hierarchy (MRO) to find the first
        matching error type mapping. It starts with the most specific exception class and
        moves up the hierarchy until either:

        - A matching error type is found
        - The base 'object' class is reached
        - No mapping is found (returns default error type)

        Args:
            schema_name: Name of the error schema to use for mapping
            exc: Exception instance to map to an error type

        Returns:
            str: The mapped error type if found, otherwise the default error type

        Raises:
            TypeError: If the provided exc argument is not an Exception instance

        Example:
            Given an inheritance chain: HTTPError -> RequestException -> Exception -> object
            The method will check mappings in this order:
            1. HTTPError
            2. RequestException
            3. Exception
            4. Returns default_error_type if no mapping is found
        """
        if not isinstance(exc, Exception):
            raise TypeError(f"Expected Exception, got {type(exc)}")

        # Get the MRO of the exception
        exc_mro: Tuple[type, ...] = exc.__class__.__mro__
        error_type = cls._default_error_type

        # Walk up the inheritance hierarchy
        for exc_class in exc_mro:
            if exc_class.__name__ == "BaseException":
                break

            mapped_type = cls.get_error_type(
                schema_name,
                exc_class.__module__,
                exc_class.__name__,
            )
            if mapped_type is not None:
                error_type = mapped_type
                break

        return error_type

    @classmethod
    def clear_caches(cls) -> None:
        """Clear all cached mappings."""
        cls.get_mapping.cache_clear()
        cls.get_error_type.cache_clear()
