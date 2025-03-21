import typing
from pathlib import Path
from typing import (
    Union,
    Iterable,
)

import typing_extensions
from typing_extensions import Literal


class ValidationError(Exception):
    """
    Custom exception class for validation errors.
    """

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or []

    def __str__(self):
        error_messages = "\n".join(self.errors)
        return f"{self.args[0]}\n{error_messages}"


Config = Union[dict, str]

from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin, Literal
import collections.abc


class Schema:
    """
    Defines the schema for configuration attributes.

    Attributes:
        expected_type (Type): The expected type of the configuration attribute.
        aliases (List[str], optional): Alternative keys for the configuration attribute.
        optional (bool, optional): Indicates whether the configuration attribute is optional.
        default (Any, optional): Default value for the configuration attribute if it is missing.

    Note:
        The expected_type can be a primitive type (e.g., int, str, float) or a typing type (e.g., List, Dict). You can use Path for file paths.

    Examples:
        ```python
        Schema(int, aliases=['num_epochs'], optional=True, default=10)
        ```
    """

    def __init__(
        self,
        type: Type,
        aliases: Optional[List[str]] = None,
        optional: bool = False,
        default: Any = None,
    ):
        """
        Initializes a Schema instance.

        Args:
            expected_type (Type): The expected type of the configuration attribute.The expected_type can be a primitive type (e.g., int, str, float) or a typing type (e.g., List, Dict). You can use Path for file paths.
            aliases (List[str], optional): Alternative keys for the configuration attribute.
            optional (bool, optional): Indicates whether the configuration attribute is optional.
            default (Any, optional): Default value for the configuration attribute if it is missing.
        """
        self.expected_type = type
        self.aliases = aliases or []
        self.optional = optional or default is not None
        self.default = default

    def validate(self, config: Dict[str, Any], key: str) -> Any:
        """
        Validates and retrieves the value of a configuration attribute from a config dictionary.

        Args:
            config (Dict[str, Any]): The configuration dictionary to validate.
            key (str): The primary key for the configuration attribute.

        Returns:
            Any: The validated and possibly converted value of the configuration attribute.

        Raises:
            ValueError: If the value is found but cannot be converted to the expected type.
            KeyError: If the value is missing and not optional.
        """
        keys_to_check = [key] + self.aliases
        for k in keys_to_check:
            if k in config:
                value = config[k]
                return self._validate_type(value, self.expected_type)
        if self.optional:
            return self.default
        raise KeyError(f"Required configuration key(s) {keys_to_check} not found in config.")

    def _validate_type(self, value: Any, expected_type: Type) -> Any:
        """
        Recursively validates the value against the expected type.

        Args:
            value (Any): The value to validate.
            expected_type (Type): The expected type.

        Returns:
            Any: The validated value.

        """
        origin = get_origin(expected_type)
        args = get_args(expected_type)
        if value is None and self.optional:
            return None
        elif origin is Union:
            # Try each type in the Union
            for typ in args:
                try:
                    return self._validate_type(value, typ)
                except TypeError:
                    continue
            expected_types = ", ".join(self._type_name(t) for t in args)
            raise TypeError(
                f"Value '{value}' does not match any type in Union[{expected_types}]"
            )
        elif origin is Literal:
            if value in args:
                return value
            else:
                raise TypeError(f"Value '{value}' is not a valid Literal {args}")
        elif origin in (list, List):
            if not isinstance(value, list):
                raise TypeError(f"Expected list but got {type(value).__name__}")
            if not args:
                return value  # No type specified for list elements
            element_type = args[0]
            return [self._validate_type(item, element_type) for item in value]
        elif origin in (dict, Dict):
            if not isinstance(value, dict):
                raise TypeError(f"Expected dict but got {type(value).__name__}")
            if not args or len(args) != 2:
                return value  # No type specified for dict keys and values
            key_type, val_type = args
            return {
                self._validate_type(k, key_type): self._validate_type(v, val_type)
                for k, v in value.items()
            }
        elif origin in (Iterable, collections.abc.Iterable):
            if not isinstance(value, collections.abc.Iterable):
                raise ValidationError(
                    f"Expected iterable but got {type(value).__name__}"
                )
            if not args:
                return value
            element_type = args[0]
            return type(value)(
                self._validate_type(item, element_type) for item in value
            )
        elif origin is typing.Sequence or origin is collections.abc.Sequence:
            if not isinstance(value, collections.abc.Sequence):
                raise TypeError(f"Expected Sequence but got {type(value).__name__}")
            if not args:
                return value  # No type specified for sequence elements
            element_type = args[0]
            return [self._validate_type(item, element_type) for item in value]
        elif expected_type is Path:
            try:
                return Path(value)
            except Exception as e:
                raise TypeError(f"Invalid path: {e}")
        # need `or expected_type is Any` because sinstance(expected_type, type) is False for Any
        elif isinstance(expected_type, type) or expected_type is Any:
            if expected_type is Any or expected_type is typing_extensions.Any:
                return value
            elif isinstance(value, expected_type):
                return value
            else:
                raise TypeError(
                    f"Expected type {expected_type.__name__} but got {type(value).__name__}"
                )
        else:
            raise TypeError(f"Unsupported type {expected_type}")

    def _type_name(self, typ: Type) -> str:
        """
        Retrieves a string representation of the type.

        Returns:
            str: The name of the type.
        """
        origin = get_origin(typ)
        args = get_args(typ)
        if origin is Union:
            return f"Union[{', '.join(self._type_name(t) for t in args)}]"
        elif origin is Literal:
            return f"Literal{args}"
        elif origin in (list, List):
            if args:
                return f"List[{self._type_name(args[0])}]"
            else:
                return "List"
        elif origin in (dict, Dict):
            if args and len(args) == 2:
                return f"Dict[{self._type_name(args[0])}, {self._type_name(args[1])}]"
            else:
                return "Dict"
        elif origin in (Iterable, collections.abc.Iterable):
            if args:
                return f"Iterable[{self._type_name(args[0])}]"
            else:
                return "Iterable"
        elif hasattr(typ, "__name__"):
            return typ.__name__
        else:
            return str(typ)

    def __repr__(self):
        return f"Schema(type={self.expected_type}, aliases={self.aliases}, optional={self.optional}, default={self.default})"
