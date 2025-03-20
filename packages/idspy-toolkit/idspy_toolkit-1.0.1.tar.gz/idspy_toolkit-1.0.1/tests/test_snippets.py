import pytest
from dataclasses import dataclass, field, Field, fields
from idspy_toolkit.snippets import is_dataclass_field

@dataclass
class ExampleDataClass:
    field1_a: str
    field1: str = "aa"
    field2: int = field(default=0)

def test_is_dataclass_field():
    example_instance = ExampleDataClass("value")
    example_instance_fields = [x for x in fields(example_instance)]
    # Test with string representing the field name
    assert is_dataclass_field(example_instance, "field1") is True
    assert is_dataclass_field(example_instance, "field1_a") is True
    assert is_dataclass_field(example_instance, "field2") is True
    assert is_dataclass_field(example_instance, "non_existent_field") is False

    # Test with Field instances
    assert is_dataclass_field(example_instance, example_instance_fields[0]) is True
    assert is_dataclass_field(example_instance, example_instance_fields[1]) is True
    assert is_dataclass_field(example_instance, example_instance_fields[2]) is True # test using the value stored
    # and not the member

    assert is_dataclass_field(example_instance, ExampleDataClass.field2) is False

    # Test with non-field item
    assert is_dataclass_field(example_instance, "not_a_field") is False
    assert is_dataclass_field(example_instance, 42) is False
    assert is_dataclass_field(example_instance, None) is False
