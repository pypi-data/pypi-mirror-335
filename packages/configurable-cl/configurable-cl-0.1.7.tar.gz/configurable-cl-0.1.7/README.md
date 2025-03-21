# Configurable Components Library (CCL)

## Overview

The Configurable Components Library is a modular framework designed to simplify the configuration and management of components—such as models, datasets, optimizers, and metrics—in AI projects. Its support for nested, hierarchical configurations allows you to update settings or extend functionality by defining new subclasses, all while keeping your core code clean and maintainable.

## Key Features

- **Hierarchical Configuration**: Organize your system into multi-level, nested components, making it easier to manage and update complex setups.
- **Dynamic Instantiation**: Create components from Python dictionaries or YAML files, enabling straightforward swapping of implementations.
- **Schema-Based Validation**: Automatically enforce type checks, default values, and parameter constraints.
- **Extendable Architecture**: Add or modify components by creating new subclasses with unique aliases, without altering the main codebase.
- **Automatic Preconditions**: Validate configurations at instantiation to catch errors early in the development process.

## Installation

### Using pip

Install the package via pip:

```bash
pip install configurable-cl
```

## Usage

### Core Classes

The library is centered around tree main classes: **`Schema`**, **`Configurable`** and **`TypedConfigurable`**.

#### The Schema Class

The Schema class plays a crucial role in validating configurations. It allows you to define the expected type for each configuration parameter and enforce constraints such as:

- **Type Checking and Conversion:** Validate simple types (e.g., int, float, str) as well as complex types using type hints (e.g., Union, Literal, List, Dict, etc.).
- **Default Values and Optional Parameters:** Specify a default value and mark parameters as optional.
- **Aliases:** Support alternative keys for configuration parameters.
- **Recursive Validation:** Validate nested structures to ensure overall configuration consistency.
- **Path Type Conversion:** When a parameter is expected to be a Path, the schema automatically converts the given string into a pathlib.Path object, ensuring that path-related configurations are handled appropriately.

#### Configurable

The `Configurable` class provides dynamic component creation using a defined `config_schema`. It handles parameter validation, assigns configuration parameters as instance attributes, and performs precondition checks during instantiation.
If you use `Configurable`, **you must use** `from_config(...)` to instantiate. You can use `__init__` for custom initialization but you lose the automatic validation, automatic adding attributes and preconditionning.

**Example:**

```python
from configurable import Configurable, Schema

class MyComponent(Configurable):
    config_schema = {
        'learning_rate': Schema(float, default=0.01),
        'batch_size': Schema(int, default=32),
    }

    def preconditions(self):
        assert self.learning_rate > 0, "Learning rate must be positive"

    def __init__(self):
        # Custom initialization if needed
        pass
```

#### TypedConfigurable

`TypedConfigurable` extends `Configurable` to support dynamic subclass selection based on a `type` parameter. This approach allows you to define a hierarchy of component implementations and select the appropriate one at runtime.

**Example with Abstract Base Classes:**

```python
from configurable import TypedConfigurable, Schema
import abc

class BaseComponent(TypedConfigurable, abc.ABC):
    aliases = ['base_component']

    @abc.abstractmethod
    def process(self):
        pass

class SpecificComponentA(BaseComponent):
    aliases = ['component_a']
    config_schema = {
        'param1': Schema(int, default=10),
    }

    def process(self):
        return f"Processing with param1: {self.param1}"

class SpecificComponentB(BaseComponent):
    aliases = ['component_b']
    config_schema = {
        'param2': Schema(str, default="default_value"),
    }

    def process(self):
        return f"Processing with param2: {self.param2}"

# Example of dynamic instantiation:
config_a = {'type': 'component_a', 'param1': 20}
component_a = BaseComponent.from_config(config_a)
print(component_a.process())

config_b = {'type': 'component_b', 'param2': "custom_value"}
component_b = BaseComponent.from_config(config_b)
print(component_b.process())
```

### Nested & Hierarchical Configuration

One of the library’s key strengths is its support for nested configurations. For example, in an AI pipeline, you might configure a data preprocessor, a model, and an optimizer, each with its own set of parameters:

```yaml
pipeline:
  data_preprocessor:
    type: 'preprocessor'
    params:
      normalization: true
      resize: 256
  model:
    type: 'advanced_model'
    params:
      layers: 50
      dropout: 0.5
  optimizer:
    type: 'adam_optimizer'
    params:
      learning_rate: 0.001
```

Each block (e.g., `data_preprocessor`, `model`, `optimizer`) can represent a `Configurable` or `TypedConfigurable` component, ensuring a consistent and validated configuration across your system.

## Adding and Configuring Components

### Configurable

To add a new component, subclass `Configurable` and define your configuration schema along with any necessary preconditions:

```python
from configurable import Configurable, Schema

class NewComponent(Configurable):
    config_schema = {
        'param1': Schema(str),
        'param2': Schema(int, default=10),
    }

    def preconditions(self):
        assert self.param2 >= 0, "param2 must be non-negative"
```

You can then provide a configuration via a YAML file or dictionary:

```yaml
component:
  param1: "example"
```

```python
import NewComponent

component = NewComponent.from_config(config['component'])
```

### TypedConfigurable

For cases where different implementations (e.g., various models or datasets) are needed, define a base class extending `TypedConfigurable` and create subclasses with unique aliases. This allows you to easily swap implementations by simply updating the configuration.

## Why Use This Library?

This library is intended for AI engineers looking for a flexible and maintainable way to manage component configurations. Its modest yet practical design helps you:

- **Separate Configuration from Code**: Update functionality through configuration files or additional subclasses, without modifying core logic.
- **Facilitate Experimentation**: Easily switch between different implementations for rapid testing and iteration.
- **Manage Nested Architectures**: Build and validate multi-level configurations that reflect the structure of your system.
- **Reduce Errors**: Automatic validation and precondition checks help catch issues early in the development process.

## Contact

For further inquiries or contributions, please contact: [julienrabault@icloud.com](mailto:julienrabault@icloud.com)
