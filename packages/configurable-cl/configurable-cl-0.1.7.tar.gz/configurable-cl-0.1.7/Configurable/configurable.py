import inspect
import warnings
from functools import wraps
from typing import (
    Union, Dict,
)

import yaml

from configurable.schema import Schema, ValidationError
from configurable.utils import _setup_logger, get_all_subclasses

"""
author: Julien Rabault
Configuration Management Module for AI Applications.

This module provides classes and utilities for managing configurations,
validating schemas, and creating Configurable objects from configuration data.
It is particularly useful for AI applications where configurations can be complex
and need to be validated at runtime.

Classes:
    - Schema: Defines the schema for configuration attributes.
    - GlobalConfig: Singleton class for global configuration settings.
    - Configurable: Base class for objects that can be customized via configuration.
    - TypedConfigurable: Base class for typed Configurable objects.

Functions:
    - get_all_subclasses: Recursively retrieves all subclasses of a class.
    - load_yaml: Loads YAML configuration files.
    - _setup_logger: Configures a logger for a specific module with console and file handlers.

Example:
    ```python
    class MyModel(Configurable):

        aliase = ['my_model']

        config_schema = {
            'learning_rate': Schema(float, default=0.001),
            'epochs': Schema(int, default=10),
        }

        def __init__(self):
            pass

        def preconditions(self):
            assert self.batch_size > 0, "Batch size must be greater than 0."

    config = {
        'learning_rate': 0.01,
        'epochs': 20,
    }

    model = MyModel.from_config(config)
    ```
"""

_init_patched_classes = set()

class GlobalConfig:
    """
    Singleton class that holds global configuration data.

    This class ensures that only one instance of the global configuration exists,
    which can be accessed and modified throughout the application.

    Attributes:
        _instance (GlobalConfig): The singleton instance.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config=None):
        if config is not None:
            self.__dict__.update(self._process_config(config))

    def _process_config(self, config):
        processed_config = {}
        for key, value in config.items():
            if isinstance(value, str) and value.endswith('.yml'):
                try:
                    with open(value, 'r') as yml_file:
                        processed_config[key] = yaml.safe_load(yml_file)
                except Exception as e:
                    raise ValueError(f"Error loading YAML file '{value}': {e}")
            else:
                processed_config[key] = value
        return processed_config

    def __setitem__(self, name, value):
        if not isinstance(name, str):
            raise TypeError("GlobalConfig keys must be strings")
        self.__dict__.setdefault(name, None)
        self.__dict__[name] = value

    def __getitem__(self, name):
        if not isinstance(name, str):
            raise TypeError("GlobalConfig keys must be strings")
        if name not in self.__dict__:
            raise KeyError(
                f"GlobalConfig does not have key: {name}, see: {self.__dict__}"
            )
        return self.__dict__.get(name, None)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        return self.__dict__


class Configurable:
    """
    Base class for Configurable objects using the `from_config` class method.

    This class allows objects to be created and configured from a configuration dictionary or file.

    Attributes:
        config_schema (dict): Defines the schema for configuration attributes.
        aliases (list): Alternative names for the class, useful for subclass identification.

    Example:
        ```python
        class MyAlgorithm(Configurable):

            aliases = ['my_algorithm']

            config_schema = {
                'learning_rate': Schema(float, optional=True, default=0.01),
                'batch_size': Schema(int, optional=True, default=32),
            }

            def __init__(self):
                pass

            def preconditions(self):
                assert self.batch_size > 0, "Batch size must be greater than 0."

        config = {
            'learning_rate': 0.001,
            'batch_size': 64,
        }

        algorithm = MyAlgorithm.from_config(config)
        ```
    """

    config_schema: Dict = {"name": Schema(Union[str, None], optional=True, default=None)}
    aliases = []
    _init_patched = False

    def __new__(cls, *args, **kwargs):
        """
        Creates an instance. If instantiated directly via __init__ instead of `from_config`, a warning is issued.
        """
        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame, 3)

        if not any(frame.function in ("from_config", "_from_config") for frame in outer_frames):
            warnings.warn(
                f"Direct instantiation of a {cls.__name__} object. It is recommended to use 'from_config' instead.",
                UserWarning,
                stacklevel=2
            )

        return super().__new__(cls)

    @classmethod
    def from_config(cls, config_data, *args, debug=False, **kwargs):
        """
        Creates an instance of the class from configuration data.

        Args:
            config_data (dict or str): Configuration data as a dictionary or a path to a YAML file.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Configurable: An instance of the class.

        Raises:
            IOError: If there is an error loading the configuration file.
            TypeError: If the configuration data is of invalid type.
            KeyError: If the configuration data is missing required keys.
            ValidationError: If there are validation errors in the configuration data.
        """
        return cls._from_config(config_data, *args, debug=debug, **kwargs)

    @classmethod
    def _from_config(cls, config_data, *args, debug=False, **kwargs):
        """
        Core logic for creating an instance from configuration data.
        """
        config_data = cls._safe_open(config_data)
        config_validate = cls._validate_config(config_data)
        original_init = cls.__init__
        cls._patch_init(debug=debug)
        try:
            instance = cls(*args, config_validate=config_validate, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Error while instantiating {cls.__name__} with config: {config_validate}") from e
        finally:
            cls.__init__ = original_init
        return instance

    @classmethod
    def _patch_init(cls, debug=False):
        """
        Temporarily patches the `__init__` method to inject validated configuration parameters.

        This method overrides the class constructor to ensure that validated configuration parameters
        are set before the original initialization is executed. It also sets up logging and global
        configurations. After instance creation, the original `__init__` method is restored.

        Args:
            debug (bool, optional): Enables debugging mode for logging. Defaults to False.
        """
        original_init = cls.__init__

        @wraps(original_init)
        def wrapped_init(self, *args, config_validate=None, **kwargs):
            if config_validate is None:
                raise ValueError(f"Missing 'config_validate' in {cls.__name__} initialization.")

            # Apply validated config to instance
            for key, value in config_validate.items():
                setattr(self, key, value)

            self.global_config = GlobalConfig()
            self.config = config_validate

            name = f"{self.__class__.__name__}[{self.name}]" if getattr(self, "name", None) else self.__class__.__name__
            self.logger = _setup_logger(name, config_validate, debug=debug)

            # Extract required init parameters
            init_signature = inspect.signature(original_init)
            init_args = {}

            for param_name, param in init_signature.parameters.items():
                if param_name in {"self", "args", "kwargs", "config_validate"}:
                    continue
                if param_name in kwargs:
                    init_args[param_name] = kwargs.pop(param_name)
                elif param_name in config_validate:
                    init_args[param_name] = config_validate[param_name]
                elif param.default == inspect.Parameter.empty:
                    raise TypeError(f"Missing required argument '{param_name}' for {cls.__name__}.__init__")

            # Ensure preconditions before calling __init__
            self.preconditions()
            original_init(self, *args, **init_args)

        cls.__init__ = wrapped_init
        _init_patched_classes.add(cls)

    @classmethod
    def _safe_open(cls, config_data):
        if isinstance(config_data, str):
            try:
                with open(config_data, "r") as file:
                    config_data = yaml.safe_load(file)
            except Exception as e:
                raise IOError(f"Error loading config file: {e}")
        elif not isinstance(config_data, dict):
            raise TypeError(
                "Invalid type for config_data. Expected dict after loading from YAML."
            )
        return config_data

    @classmethod
    def _validate_config(cls, config_data, dynamic_schema=None):
        if dynamic_schema is None:
            dynamic_schema = {}
        config_schema = {}
        for base in reversed(cls.__mro__):
            if hasattr(base, "config_schema"):
                if isinstance(base.config_schema, dict):
                    config_schema.update(base.config_schema)
                else:
                    raise TypeError(
                        f"config_schema must be a dictionary, got {type(base.config_schema).__name__}"
                    )
        config_schema.update(dynamic_schema)

        validated_config = {}
        errors = []

        for key, schema in config_schema.items():
            if not isinstance(schema, Schema):
                raise TypeError(
                    f"Schema object expected for key '{key}' in class '{cls.__name__}'"
                )

            try:
                validated_value = schema.validate(config_data, key)
                validated_config[key] = validated_value
            except KeyError:
                errors.append(
                    f"Missing required key '{key}' in configuration for class '{cls.__name__}'."
                )
            except TypeError as e:
                errors.append(
                    f"Type error for key '{key}' in class '{cls.__name__}': {str(e)}"
                )
            except ValueError as e:
                errors.append(
                    f"Value error for key '{key}' in class '{cls.__name__}': {str(e)}"
                )
            except Exception as e:
                errors.append(
                    f"Unexpected error for key '{key}' in class '{cls.__name__}': {str(e)}"
                )

        if errors:
            cls_name = cls.__name__
            cls_aliases = ", ".join(cls.aliases)
            cls_name_aliases = (
                f"{cls_name} [{cls_aliases}]" if cls.aliases else cls_name
            )
            raise ValidationError(
                f"Validation errors in configuration for class '{cls_name_aliases}':",
                errors=errors,
            )

        # Check for unexpected keys
        valid_keys = set(config_schema.keys())
        for schema in config_schema.values():
            if isinstance(schema.aliases, list):
                valid_keys.update(schema.aliases)

        invalid_keys = set(config_data.keys()) - valid_keys
        if invalid_keys:
            warnings.warn(
                f"Unknown keys in configuration for class '{cls.__name__}': {', '.join(invalid_keys)}",
                UserWarning,
            )

        return validated_config

    def preconditions(self):
        """
        Check if all preconditions are met before running the algorithm.
        """
        pass

    def to_config(self, exclude=[], add={}):
        config = {}
        for key, value in self.__dict__.items():
            if key not in exclude and not key.startswith("_"):
                config[key] = value
        config.update(add)
        return config

    def get_config_schema(self):
        return self.config_schema

    def save_dict_to_yaml(self, data: dict, file_path: str):
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def __reduce__(self):
        """
        __reduce__ method for pickle serialization.
        It ensures the correct class is used during unpickling.
        """
        return (rebuild_configurable, (self.__class__, self.config, self.__getstate__()))

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("logger", None)
        state.pop("global_config", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not hasattr(self, "global_config"):
            self.global_config = GlobalConfig()
        if not hasattr(self, "logger"):
            name = self.__class__.__name__ + (
                f"[{self.name}]" if getattr(self, "name", None) else self.__class__.__name__)
            self.logger = _setup_logger(name, self.config, debug=False)

    def __str__(self):
        def recursive_str(d, indent=0):
            string = ""
            for key, value in d.items():
                if not isinstance(value, GlobalConfig):
                    if isinstance(value, dict):
                        string += (
                            f"{' ' * indent}{key}:\n{recursive_str(value, indent + 2)}"
                        )
                    else:
                        string += f"{' ' * indent}{key}: {value}\n"
            return string

        config_string = ""
        config_string += recursive_str(self.__dict__)
        return config_string


class TypedConfigurable(Configurable):
    """
    Base class for typed Configurable objects.

    This class extends `Configurable` to allow for dynamic subclass instantiation
    based on a 'type' key in the configuration data.

    Attributes:
        config_schema (dict): Defines the schema for configuration attributes, including 'type'.

    Example:
        ```python
        class BaseModel(TypedConfigurable):
            aliases = ['base_model']

        class CNNModel(BaseModel):
            aliases = ['cnn', 'convolutional']

            config_schema = {
                'filters': Schema(int, default=32),
                'kernel_size': Schema(int, default=3),
            }

            def __init__(self:
                pass

        config = {
            'type': 'cnn',
            'filters': 64,
            'kernel_size': 5,
        }

        model = BaseModel.from_config(config)
        ```
    """

    config_schema = {"type": Schema(str)}

    @classmethod
    def from_config(cls, config_data, *args, **kwargs):
        """
        Create an instance of the correct subclass based on 'type' in config_data.
        """
        config_data = cls._safe_open(config_data)
        try:
            type_name = config_data["type"]
        except KeyError:
            raise ValueError(
                f"Missing required key: 'type' for class {cls.__name__} in config file."
            )

        subclass = cls.find_subclass_by_type_name(type_name)
        if subclass is None:
            subclasses = get_all_subclasses(cls)
            raise ValueError(
                f"Type '{type_name}' not found. Available types: {[el.get_all_name() for el in subclasses]}\n"
                f"If you add a custom class in a new files .py, make sure to add it import in the __init__.py file"
            )

        return subclass._from_config(config_data, *args, **kwargs)

    @classmethod
    def find_subclass_by_type_name(cls, type_name: str):
        assert (
                type(type_name) == str
        ), f"type_name must be a string, got {type(type_name)}"
        for subclass in cls.__subclasses__():
            if type_name.lower() in [alias.lower() for alias in subclass.aliases] + [
                subclass.__name__.lower()
            ]:
                return subclass
            else:
                subsubclass = subclass.find_subclass_by_type_name(type_name)
                if subsubclass:
                    return subsubclass
        return None

    @classmethod
    def get_all_name(cls):
        return f"{cls.__name__} ({', '.join(cls.aliases)})"


def rebuild_configurable(cls, config, state):
    """
    Reconstruction function for pickle.

    Args:
        cls (type): The original class of the instance.
        config (dict): The validated configuration of the instance.
        state (dict): The state extracted from the instance via __getstate__.

    Returns:
        An instance of `cls`, reconstructed with the correct configuration.
    """
    instance = cls._from_config(config)
    instance.__setstate__(state)
    return instance

