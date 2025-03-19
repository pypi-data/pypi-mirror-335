"""Base error schema classes and utilities for PyErrorSchema.

This module defines the core ErrorSchema class and its specialized subclasses
for different error types, providing a structured approach to error handling
with standardized formats and factory methods.
"""

import inspect
import json
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from ..mappings import ExceptionMapper
from ..utils import get_parent_class, restrict_arguments

ESType = TypeVar("ESType", bound="ErrorSchema")


class ErrorSchema(BaseModel):
    """Core class for error schemas in PyErrorSchema.

    Provides a structured approach to error handling with standardized formats
    and factory methods for creating error instances.
    """

    model_config = ConfigDict(extra="forbid")

    type: str = Field(default="")
    msg: str = Field(default="")

    def __repr__(self) -> str:
        """Return a string representation of the error schema."""
        attrs = [f"{k}={repr(v)}" for k, v in self.model_dump().items() if not k.startswith('_')]
        attrs_str = textwrap.indent(',\n'.join(attrs), '    ')
        return f"{self.__class__.__name__}(\n{attrs_str}\n)"

    def __str__(self) -> str:
        """Return a string representation of the error schema."""
        return self.__repr__()

    @classmethod
    def list_available_errors(cls) -> List[str]:
        """List all available error types."""
        return [
            name
            for name, _ in inspect.getmembers(cls, predicate=inspect.ismethod)
            if name.endswith("_error") and not name.startswith("_")
        ]

    @classmethod
    def get_mapping(cls) -> Dict[str, Dict[str, str]]:
        """Get the mapping between exception types and error types."""
        return ExceptionMapper.get_mapping(cls.__name__)

    #######################
    ### Utility methods ###
    #######################

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error schema to a dictionary."""
        return self.model_dump()

    def to_string(self) -> str:
        """Convert the error schema to a string."""
        return json.dumps(self.to_dict(), indent=2)

    #######################
    ### Factory methods ###
    #######################

    @classmethod
    def _create_error(cls, error_type: str, default_msg: str, **kwargs: Any) -> Self:
        """Create an error schema instance with a formatted message.

        This method serves as the core factory method for generating error instances.
        It formats the error message in the form of "<readable_error_type>: <msg>",
        where <readable_error_type> is the error type with underscores replaced by
        spaces and capitalized (e.g., "validation_error" becomes "Validation error").

        The message is determined by the following priority:
        1. If the "msg" argument is provided, it is used as the error message.
        2. If the "exc" argument is provided, it is appended to the error message.
        3. Otherwise, the "default_msg" is used.

        Args:
            error_type (str): The type of the error.
            default_msg (str): The default message of the error.
            **kwargs: Additional keyword arguments to pass to the error schema.

        Returns:
            ErrorSchema: An instance of the error schema with the formatted message.
        """
        msg = kwargs.pop("msg", default_msg)
        if "exc" in kwargs:
            msg += f" ({str(kwargs['exc'])})"

        pretty_type = error_type.replace("_", " ").capitalize()
        msg = msg[0].lower() + msg[1:]

        return cls(
            type=error_type,
            msg=f"{pretty_type}: {msg}",
            **kwargs,
        )

    @classmethod
    @restrict_arguments("type")
    def database_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a database error."""
        return cls._create_error("database_error", "Database error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def file_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a file error."""
        return cls._create_error("file_error", "File error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def runtime_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a runtime error."""
        return cls._create_error("runtime_error", "Runtime error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def timeout_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a timeout error."""
        return cls._create_error("timeout_error", "Timeout error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def parse_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a parse error."""
        return cls._create_error("parse_error", "Parse error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def value_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a value error."""
        return cls._create_error("value_error", "Value error occurred.", **kwargs)

    @classmethod
    def customized_error(cls, **kwargs: Any) -> Self:
        """Factory method to create an instance for a customized error."""
        error_type = kwargs.pop("type", "customized_error")
        return cls._create_error(error_type, "Customized error occurred.", **kwargs)


    @classmethod
    def from_exception(cls, exc: Exception, **kwargs: Any) -> Self:
        """Create an error schema instance from an exception.

        Automatically maps exceptions to appropriate error schemas based on their type.
        Captures both the primary exception and any chained exceptions (from either
        explicit 'raise ... from' or implicit exception chaining).

        If the exception is already an error schema, it will be returned directly.

        Args:
            exc (Exception): The exception to create an error schema from.
            **kwargs: Additional keyword arguments to pass to the error schema.
        """
        # Check if the exception is an instance of Exception
        if not isinstance(exc, Exception):
            raise TypeError(f"Expected Exception, got {type(exc)}")

        # If the exception is already an error schema, return it
        if isinstance(exc.args[0], cls):
            return exc.args[0]

        # Get the cause (explicit) or context (implicit) of the exception
        cause = exc.__cause__ or exc.__context__
        error_type = ExceptionMapper.get_error_type_from_exception(cls.__name__, exc)

        # Format message
        kwargs['msg'] = str(exc)
        if cause:
            kwargs['exc'] = cause

        return cls._create_error(error_type, "Error occurred.", **kwargs)

    ## Subclasses ##

    class Base(ABC, Generic[ESType]):
        """Base class for all error schema subclasses.

        This class provides a general error method for all error schema subclasses.
        Each subclass can define its own `display_name` attribute to customize the
        error message prefix. If not set, the class name will be used.

        Example:
            class File(Base):
                # Uses class name in error messages
                pass

            class DB(Base):
                # Customizes error message prefix
                display_name: str = "Database"

            # Usage examples:
            File.general(action="reading config.json")
            # Output: "File error occurred while reading config.json."

            DB.general(reason="connection timeout")
            # Output: "Database error occurred since connection timeout."

        The error method will automatically use the corresponding error factory
        (e.g., file_error for File class) from the parent class. If no matching
        error factory exists, it falls back to customized_error.
        """
        display_name: Optional[str] = None

        @classmethod
        def _get_name(cls) -> str:
            """Get the display name for error message formatting.

            Returns the custom name if it is defined, otherwise returns the class name.
            """
            return cls.display_name or cls.__name__

        @classmethod
        @abstractmethod
        def general(
            cls,
            *,
            action: Optional[str] = None,
            reason: Optional[str] = None,
            **kwargs: Any,
        ) -> ESType:
            """Create a general error instance for this error type.

            The error message will be formatted in one of two ways:
            - "<name> error occurred while <action>."
            - "<name> error occurred since <reason>."

            Args:
                action: Description of the action being performed when the error occurred.
                    Example: "reading file", "connecting to database"
                reason: Description of why the error occurred.
                    Example: "invalid format", "connection timeout"
                **kwargs: Additional keyword arguments to pass to the error factory method.

            Raises:
                ValueError: If both action and reason are provided.

            Returns:
                An error instance with the formatted message.
            """
            if action and reason:
                raise ValueError("Only one of 'action' or 'reason' should be provided.")

            name = cls._get_name()
            if action:
                kwargs["msg"] = f"{name} error occurred while {action}."
            elif reason:
                kwargs["msg"] = f"{name} error occurred since {reason}."

            error_method = f"{name.lower()}_error"
            parent_cls: ESType = get_parent_class(cls)

            return parent_cls.customized_error(type=error_method, **kwargs)

    class File(Base[ESType]):
        """Error schema for file operations.

        Provides methods for common file operation errors with automatic path type detection
        (file vs directory) for more precise error messages.

        Examples:
            >>> File.not_found(path="config.json")
            "File 'config.json' not found."

            >>> File.not_found(path="data/")
            "Directory 'data/' not found."

            >>> File.writing(path="output.txt")
            "Writing to file 'output.txt' failed."
        """

        @classmethod
        def _path_type(cls, path: str) -> str:
            """Get the type of the path."""
            return "file" if Path(path).suffix else "directory"

        @classmethod
        def not_found(cls, path: str, **kwargs: Any) -> ESType:
            """File not found error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"{path_type.capitalize()} '{path}' not found.", **kwargs,
            )

        @classmethod
        def already_exists(cls, path: str, **kwargs: Any) -> ESType:
            """File already exists error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"{path_type.capitalize()} '{path}' already exists.", **kwargs,
            )

        @classmethod
        def creating(cls, path: str, **kwargs: Any) -> ESType:
            """Creating error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Creating {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def writing(cls, path: str, **kwargs: Any) -> ESType:
            """Writing error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Writing to {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def reading(cls, path: str, **kwargs: Any) -> ESType:
            """Reading error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Reading from {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def removing(cls, path: str, **kwargs: Any) -> ESType:
            """Removing error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Removing {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def copying(cls, path: str, **kwargs: Any) -> ESType:
            """Copying error for a given path."""
            path_type = cls._path_type(path)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Copying {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def updating(cls, path: str, **kwargs: Any) -> ESType:
            """Updating error for a given path.

            only file is supported for this method.
            """
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Updating file '{path}' failed.", **kwargs,
            )

    class Map(Base[ESType]):
        """Error schema for dictionary operations.

        Provides methods for common dictionary operation errors with automatic
        key concatenation for more precise error messages.

        Examples:
            >>> Map.general(action="reading config.json")
            "Dict error occurred while reading config.json."

            >>> Map.missing_keys(keys=["name", "age"])
            "Keys ('name', 'age') not found in dictionary."
        """
        display_name: str = "Dict"

        @classmethod
        def missing_keys(cls, keys: List[str], **kwargs: Any) -> ESType:
            """Missing keys error for a given keys."""
            concat_keys = "', '".join(keys)
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"Keys ('{concat_keys}') not found in dictionary.", **kwargs,
            )

    class DB(Base[ESType]):
        """Error schema for database operations.

        Provides methods for common database operation errors with automatic
        description concatenation for more precise error messages.

        Examples:
            >>> DB.general(action="loading the data")
            "Database error occurred while loading the data."

            >>> DB.no_results(desc="while reading config.json")
            "No results found while reading config.json."

            >>> DB.foreign_key_violation()
            "Foreign key violation occurred."
        """
        display_name: str = "Database"

        @classmethod
        def no_results(cls, desc: str, **kwargs: Any) -> ESType:
            """No results when querying a database.

            Format for the message: "No results found while <desc>."
            """
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg=f"No results found while {desc}.", **kwargs,
            )

        @classmethod
        def foreign_key_violation(cls, **kwargs: Any) -> ESType:
            """Foreign key violation error."""
            parent_cls: ESType = get_parent_class(cls)
            return parent_cls.customized_error(
                type=f"{cls._get_name().lower()}_error",
                msg="Foreign key violation occurred.", **kwargs,
            )

    class Value(Base[ESType]):
        """Error schema for value operations.

        Provides methods for common value operation errors with automatic
        description concatenation for more precise error messages.
        """
        ...

    class Parse(Base[ESType]):
        """Error schema for parsing operations.

        Provides methods for common parsing operation errors with automatic
        description concatenation for more precise error messages.
        """
        ...

    class Runtime(Base[ESType]):
        """Error schema for runtime operations.

        Provides methods for common runtime operation errors with automatic
        description concatenation for more precise error messages.
        """
        ...

    class Unknown(Base[ESType]):
        """Error schema for unknown operations.

        Provides methods for common unknown operation errors with automatic
        description concatenation for more precise error messages.
        """
        ...
