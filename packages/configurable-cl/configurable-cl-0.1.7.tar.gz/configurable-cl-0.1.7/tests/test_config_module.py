import pickle
from typing import Any, Iterable, Union, List

import pytest
from typing_extensions import Any, Iterable, Union

from configurable.configurable import Schema, GlobalConfig, Configurable, TypedConfigurable, ValidationError


# Test cases for the Schema class
def test_schema_validation_required_field():
    schema = Schema(int)
    config_data = {'key': 5}
    assert schema.validate(config_data, 'key') == 5

def test_schema_validation_any_type():
    schema = Schema(Any)
    config_data = {'key': 5}
    assert schema.validate(config_data, 'key') == 5

def test_schema_validation_list():
    schema = Schema(List[int])  # Liste d'entiers
    config_data = {'key': [1, 2, 3]}
    assert schema.validate(config_data, 'key') == [1, 2, 3]

def test_schema_validation_list_failure():
    schema = Schema(List[int])  # Liste d'entiers
    config_data = {'key': [1, '2', 3]}
    try:
        schema.validate(config_data, 'key')
        assert False, "Expected a validation error for invalid list element type."
    except TypeError:
        pass

def test_schema_validation_iterable():
    schema = Schema(Iterable)
    config_data = {'key': [1, 2, 3]}
    assert schema.validate(config_data, 'key') == [1, 2, 3]

    config_data = {'key': (1, 2, 3)}
    assert schema.validate(config_data, 'key') == (1, 2, 3)

    config_data = {'key': {1, 2, 3}}
    assert schema.validate(config_data, 'key') == {1, 2, 3}

def test_schema_validation_iterable_failure():
    schema = Schema(Iterable)
    config_data = {'key': 42}
    try:
        schema.validate(config_data, 'key')
        assert False, "Expected a validation error for non-iterable value."
    except ValidationError:
        pass

def test_schema_validation_union_type():
    schema = Schema(Union[int, str])
    config_data = {'key': 5}
    assert schema.validate(config_data, 'key') == 5

    config_data = {'key': 'hello'}
    assert schema.validate(config_data, 'key') == 'hello'

def test_schema_validation_union_type_failure():
    schema = Schema(Union[int, str])
    config_data = {'key': 5.5}
    try:
        schema.validate(config_data, 'key')
        assert False, "Expected a validation error for invalid union type."
    except TypeError:
        pass

def test_schema_validation_missing_required_field():
    schema = Schema(int)
    config_data = {}
    with pytest.raises(KeyError):
        schema.validate(config_data, 'key')


def test_schema_validation_optional_field_with_default():
    schema = Schema(int, optional=True, default=10)
    config_data = {}
    assert schema.validate(config_data, 'key') == 10


def test_schema_validation_aliases():
    schema = Schema(int, aliases=['alias1', 'alias2'])
    config_data = {'alias2': 15}
    assert schema.validate(config_data, 'key') == 15


def test_schema_validation_invalid_type():
    schema = Schema(int)
    config_data = {'key': 'not an int'}
    with pytest.raises(TypeError):
        schema.validate(config_data, 'key')


# Test cases for the GlobalConfig class
def test_global_config_singleton():
    config1 = GlobalConfig()
    config2 = GlobalConfig()
    assert config1 is config2


def test_global_config_set_and_get_item():
    config = GlobalConfig()
    config['key'] = 'value'
    assert config['key'] == 'value'


def test_global_config_invalid_key_type():
    config = GlobalConfig()
    with pytest.raises(TypeError):
        config[123] = 'value'


def test_global_config_missing_key():
    config = GlobalConfig()
    with pytest.raises(KeyError):
        _ = config['nonexistent']


# Test cases for the Configurable class
class MyConfigurable(Configurable):
    config_schema = {
        'param0': Schema(int),
        'param1': Schema(int, default=1),
        'param2': Schema(str, optional=True),
    }


def test_Configurable_from_config():
    config = {'param0': 1, 'param1': 10, 'param2': 'test'}
    obj = MyConfigurable.from_config(config)
    assert obj.param0 == 1
    assert obj.param1 == 10
    assert obj.param2 == 'test'

def test_override_default_value():
    config = {'param0': 1, 'param1': 10}
    obj = MyConfigurable.from_config(config)
    assert obj.param0 == 1
    assert obj.param1 == 10
    assert obj.param2 is None


def test_Configurable_from_config_with_defaults():
    config = {'param0': 1, }
    obj = MyConfigurable.from_config(config)
    assert obj.param0 == 1
    assert obj.param1 == 1
    assert obj.param2 is None


def test_Configurable_missing_required_param():
    config = {'param2': 'test'}
    with pytest.raises(ValidationError):
        MyConfigurable.from_config(config)


def test_Configurable_invalid_param_type():
    config = {'param1': 'not an int', 'param2': 'test'}
    with pytest.raises(ValidationError):
        MyConfigurable.from_config(config)


# Test cases for the TypedConfigurable class
class BaseAlgorithm(TypedConfigurable):
    config_schema = TypedConfigurable.config_schema.copy()
    aliases = ['base_algorithm']


class AlgorithmA(BaseAlgorithm):
    aliases = ['algorithm_a']
    config_schema = {
        'type': Schema(str),
        'param_a': Schema(int, default=5),
    }

    def __init__(self, param_a):
        self.param_a = param_a


class AlgorithmB(BaseAlgorithm):
    aliases = ['algorithm_b']
    config_schema = {
        'type': Schema(str),
        'param_b': Schema(str),
    }

    def __init__(self, ):
        pass

def test_typed_Configurable_from_config_algorithm_c():
    class AlgorithmC(Configurable):
        aliases = ['algorithm_c']
        config_schema = 1  # Incorrect type, should be a dict of Schema objects

        def __init__(self):
            pass

    # Configuration data for testing
    config_data = {
        'param_b': 42
    }

    with pytest.raises(TypeError) as exc_info:
        AlgorithmC.from_config(config_data)

    assert str(exc_info.value) in "config_schema must be a dictionary, got int"


def test_typed_Configurable_from_config_algorithm_a():
    config = {'type': 'algorithm_a', 'param_a': 10}
    obj = BaseAlgorithm.from_config(config)
    assert isinstance(obj, AlgorithmA)
    assert obj.param_a == 10


def test_typed_Configurable_from_config_algorithm_b():
    config = {'type': 'algorithm_b', 'param_b': 'value'}
    obj = BaseAlgorithm.from_config(config)
    assert isinstance(obj, AlgorithmB)
    assert obj.param_b == 'value'


def test_typed_Configurable_missing_type():
    config = {'param_a': 10}
    with pytest.raises(ValueError):
        BaseAlgorithm.from_config(config)


def test_typed_Configurable_invalid_type():
    config = {'type': 'unknown_type', 'param_a': 10}
    with pytest.raises(Exception):
        BaseAlgorithm.from_config(config)


def test_typed_Configurable_missing_required_param():
    config = {'type': 'algorithm_b'}
    with pytest.raises(ValidationError):
        BaseAlgorithm.from_config(config)


def test_AlgorithmA_pickle_serializable():
    """
    Test that an instance of AlgorithmA can be pickled and unpickled.
    """
    config = {'type': 'algorithm_a', 'param_a': 10}
    instance = BaseAlgorithm.from_config(config)
    pickled_instance = pickle.dumps(instance)

    loaded_instance = pickle.loads(pickled_instance)

    assert isinstance(loaded_instance, AlgorithmA)
    assert loaded_instance.param_a == instance.param_a

def test_AlgorithmB_pickle_serializable():
    config = {'type': 'algorithm_b', 'param_b': 'test_value'}
    instance = BaseAlgorithm.from_config(config)

    pickled_instance = pickle.dumps(instance)

    loaded_instance = pickle.loads(pickled_instance)
    assert isinstance(loaded_instance, AlgorithmB)
    assert hasattr(loaded_instance, 'param_b')

def test_AlgorithmA_pickle_unserializable():
    class Unserializable:
        """ Dummy class that is not serializable with pickle. """
        def __reduce__(self):
            raise TypeError("Not serializable")

    class AlgorithmWithUnserializable(AlgorithmA):
        def __init__(self, param_a):
            super().__init__(param_a)
            self.bad_param = Unserializable()

    config = {'type': 'AlgorithmWithUnserializable'}
    instance = BaseAlgorithm.from_config(config)

    with pytest.raises(AttributeError, match="Can't pickle"):
        pickle.dumps(instance)