"""FastAPI error group implementation for managing collections of FastAPI errors.

This module provides specialized error group handling for FastAPI applications.
"""

from copy import deepcopy
from typing import Iterator, List, Union

from typing_extensions import Self

from ..base.err_group import ErrGroup
from ..types import MsgType
from .fastapi_base import FastAPIErrorSchema


class FastAPIErrGroup(ErrGroup):
    """A group of FastAPIErrorSchema instances.

    Attributes:
        error_schemas (List[FastAPIErrorSchema]): The list of FastAPIErrorSchema instances.
    """

    def __init__(self) -> None:
        """Initialize an empty FastAPI error group."""
        self._error_schemas: List[FastAPIErrorSchema] = []

    def __iter__(self) -> Iterator[FastAPIErrorSchema]:
        """Iterate over the FastAPIErrorSchema instances in the group."""
        return iter(self._error_schemas)

    def __getitem__(self, index: int) -> FastAPIErrorSchema:
        """Get the FastAPIErrorSchema instance at the given index."""
        return self._error_schemas[index]

    def __setitem__(self, index: int, value: FastAPIErrorSchema) -> None:
        """Set the FastAPIErrorSchema instance at the given index."""
        if not isinstance(value, FastAPIErrorSchema):
            raise ValueError("The error schema must be an instance of FastAPIErrorSchema.")
        return super().__setitem__(index, value)

    ## Methods for converting the error schemas ##

    def to_dict(self, target: MsgType = "backend") -> List[dict]:
        """Convert the error schemas to a dictionary.

        .. note:: This method is deprecated. Use `to_dicts` instead.
        """
        return [err.to_dict(target) for err in self._error_schemas]

    def to_dicts(self, target: MsgType = "backend") -> List[dict]:
        """Convert the error schemas to a dictionary."""
        return [err.to_dict(target) for err in self._error_schemas]

    def to_string(self, target: MsgType = "backend") -> str:
        """Convert the error schemas to a string."""
        return f"[{', '.join(err.to_string(target) for err in self._error_schemas)}]"

    def to_list(self) -> List[FastAPIErrorSchema]:
        """Convert the error schemas to a list."""
        return deepcopy(self._error_schemas)

    ## Methods for modifying the error schemas ##

    def append(self, error_schema: FastAPIErrorSchema) -> None:
        """Add an error schema to the group."""
        if not isinstance(error_schema, FastAPIErrorSchema):
            raise ValueError("The error schema must be an instance of FastAPIErrorSchema.")
        self._error_schemas.append(error_schema)

    def extend(self, error_schemas: Union[List[FastAPIErrorSchema], Self]) -> None:
        """Extend the error schemas with a list of error schemas."""
        if isinstance(error_schemas, FastAPIErrGroup):
            self._error_schemas.extend(error_schemas.to_list())
        elif isinstance(error_schemas, list):
            if not all(isinstance(err, FastAPIErrorSchema) for err in error_schemas):
                raise ValueError("All elements must be instances of FastAPIErrorSchema.")
            self._error_schemas.extend(error_schemas)
        else:
            raise ValueError(
                "The argument must be a list of FastAPIErrorSchema "
                "instances or an instance of FastAPIErrGroup."
            )

    ## Special methods for FastAPIErrGroup ##

    def append_loc(self, loc: str) -> None:
        """Globally append a location to all error schemas in the group.

        Args:
            loc (str): The location to append.
        """
        for err in self._error_schemas:
            err.loc.append(loc)

    def extend_loc(self, locs: List[str]) -> None:
        """Globally extend the locations of all error schemas in the group.

        Args:
            locs (List[str]): The locations to extend.
        """
        for err in self._error_schemas:
            err.loc.extend(locs)

    def update_input(self, input_dict: dict, overwrite: bool = False) -> None:
        """Globally update input data for all error schemas in the group.

        Args:
            input_dict (dict): The input data to update or assign.
            overwrite (bool): If True, completely replace existing input data.
                              If False, merge with existing input data.
        """
        for err in self._error_schemas:
            err.input = input_dict if overwrite else {**err.input, **input_dict}
