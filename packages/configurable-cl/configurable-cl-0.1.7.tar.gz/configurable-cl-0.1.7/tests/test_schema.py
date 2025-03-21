import unittest
from pathlib import Path
from typing import Union, List, Dict, Literal, Iterable

from configurable import Schema


class TestSchema(unittest.TestCase):
    """Tests unitaires pour la classe Schema."""

    def test_simple_int(self):
        schema = Schema(int)
        config = {'value': 5}
        self.assertEqual(schema.validate(config, 'value'), 5)

    def test_invalid_type(self):
        schema = Schema(int)
        config = {'value': 'not an int'}
        with self.assertRaises(TypeError):
            schema.validate(config, 'value')

    def test_optional_with_default(self):
        schema = Schema(int, optional=True, default=10)
        config = {}
        self.assertEqual(schema.validate(config, 'value'), 10)

    def test_missing_required_key(self):
        schema = Schema(int)
        config = {}
        with self.assertRaises(KeyError):
            schema.validate(config, 'value')

    def test_alias(self):
        schema = Schema(int, aliases=['num'])
        config = {'num': 20}
        self.assertEqual(schema.validate(config, 'value'), 20)

    def test_union_type_valid(self):
        schema = Schema(Union[int, str])
        config_str = {'value': 'hello'}
        config_int = {'value': 123}
        self.assertEqual(schema.validate(config_str, 'value'), 'hello')
        self.assertEqual(schema.validate(config_int, 'value'), 123)

    def test_union_type_invalid(self):
        schema = Schema(Union[int, str])
        config = {'value': 1.5}
        with self.assertRaises(TypeError):
            schema.validate(config, 'value')

    def test_literal_valid(self):
        schema = Schema(Literal['a', 'b'])
        config = {'value': 'a'}
        self.assertEqual(schema.validate(config, 'value'), 'a')

    def test_literal_invalid(self):
        schema = Schema(Literal['a', 'b'])
        config = {'value': 'c'}
        with self.assertRaises(TypeError):
            schema.validate(config, 'value')

    def test_list_type_valid(self):
        schema = Schema(List[int])
        config = {'value': [1, 2, 3]}
        self.assertEqual(schema.validate(config, 'value'), [1, 2, 3])

    def test_list_type_invalid(self):
        schema = Schema(List[int])
        config = {'value': [1, '2', 3]}
        with self.assertRaises(TypeError):
            schema.validate(config, 'value')

    def test_dict_type_valid(self):
        schema = Schema(Dict[str, int])
        config = {'value': {'a': 1, 'b': 2}}
        self.assertEqual(schema.validate(config, 'value'), {'a': 1, 'b': 2})

    def test_dict_type_invalid(self):
        schema = Schema(Dict[str, int])
        config = {'value': {'a': 1, 'b': '2'}}
        with self.assertRaises(TypeError):
            schema.validate(config, 'value')

    def test_iterable_type_valid(self):
        schema = Schema(Iterable[int])
        config = {'value': (1, 2, 3)}
        self.assertEqual(tuple(schema.validate(config, 'value')), (1, 2, 3))

    def test_iterable_type_invalid(self):
        schema = Schema(Iterable[int])
        config = {'value': 123}
        with self.assertRaises(Exception):
            schema.validate(config, 'value')

    def test_path_valid(self):
        schema = Schema(Path)
        config = {'value': '.'}
        path_obj = schema.validate(config, 'value')
        self.assertIsInstance(path_obj, Path)
        self.assertEqual(str(path_obj), '.')

    def test_repr(self):
        schema = Schema(int, aliases=['alias'], optional=True, default=0)
        self.assertIn("Schema(", repr(schema))

