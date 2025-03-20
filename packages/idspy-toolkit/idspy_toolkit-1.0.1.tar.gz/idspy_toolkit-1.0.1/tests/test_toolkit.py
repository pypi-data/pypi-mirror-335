import dataclasses
import numpy as np
import pytest
from idspy_toolkit.utils import snake2camel, camel2snake, get_field_with_type, extract_ndarray_info, \
    _imas_default_values, __get_field_type, get_all_class
from idspy_toolkit.accessor import get_type_arg
from idspy_toolkit.toolkit import fill_default_values_ids
from typing import Optional

from unittest.mock import patch, MagicMock


@dataclasses.dataclass#(slots=True)
class child3:
    # c3:str=dataclasses.field(default_factory=lambda:"here")
    c3: str = dataclasses.field(default="nested_value")


@dataclasses.dataclass#(slots=True)
class child2:
    c2: child3 = dataclasses.field(default=None)


@dataclasses.dataclass#(slots=True)
class child1:
    b: str = ""


@dataclasses.dataclass#(slots=True)
class root:
    a: str = dataclasses.field(default="a")
    b: child1 = dataclasses.field(default=None)
    c: child2 = dataclasses.field(default=None)


def test_creation_subtype():
    ut_test = root()
    assert ut_test.c is None
    atype, _ = get_type_arg(ut_test, "c")
    assert dataclasses.is_dataclass(atype())
    fill_default_values_ids(ut_test)
    assert ut_test.c.c2 is not None
    assert ut_test.c.c2.c3 == "nested_value"




@pytest.fixture
def sample_dataclasses():
    """Fixture providing sample dataclasses for testing."""

    @dataclasses.dataclass
    class SimpleDataClass:
        value: int = 0
        name: str = "default"

    @dataclasses.dataclass
    class NestedDataClass:
        simple: SimpleDataClass = dataclasses.field(default_factory=SimpleDataClass)
        values: list[int] = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class ComplexDataClass:
        nested: NestedDataClass = dataclasses.field(default_factory=NestedDataClass)
        items: list[SimpleDataClass] = dataclasses.field(default_factory=list)
        data: list[float] = dataclasses.field(default_factory=list)

    return {
        'SimpleDataClass': SimpleDataClass,
        'NestedDataClass': NestedDataClass,
        'ComplexDataClass': ComplexDataClass
    }


@pytest.fixture
def mock_dependencies():
    """Fixture for mocking dependencies."""
    # Patch get_type_arg which is exported publicly
    with patch('idspy_toolkit.accessor.get_type_arg') as mock_get_type_arg:
        # Patch __fill_default_values_ids at its internal location
        with patch('idspy_toolkit.toolkit.__fill_default_values_ids') as mock_fill_default:
            yield {
                'get_type_arg': mock_get_type_arg,
                'fill_default': mock_fill_default
            }


def test_simple_dataclass(sample_dataclasses, mock_dependencies):
    """Test filling a simple dataclass with default values."""
    # Configure mocks
    mock_dependencies['get_type_arg'].side_effect = [
        (int, None),
        (str, None)
    ]

    # Create instance
    simple_ids = sample_dataclasses['SimpleDataClass']()

    # Call function
    fill_default_values_ids(simple_ids)

    # Verify __fill_default_values_ids was called for each field
    mock_fill = mock_dependencies['fill_default']
    assert mock_fill.call_count == 2
    mock_fill.assert_any_call(simple_ids, 'value', int, None)
    mock_fill.assert_any_call(simple_ids, 'name', str, None)


def test_nested_dataclass(sample_dataclasses, mock_dependencies):
    """Test filling a dataclass that contains another dataclass."""
    SimpleDataClass = sample_dataclasses['SimpleDataClass']
    NestedDataClass = sample_dataclasses['NestedDataClass']

    # Configure mocks for the parent and nested dataclass fields
    mock_dependencies['get_type_arg'].side_effect = [
        (SimpleDataClass, False),
        (int, False),  # For SimpleDataClass.value
        (str, False),  # For SimpleDataClass.name
        (list[int], True)
    ]

    # Create instance with empty nested dataclass
    nested_ids = NestedDataClass(simple=SimpleDataClass())

    # Call function
    fill_default_values_ids(nested_ids)

    # Check the nested object was processed
    mock_fill = mock_dependencies['fill_default']
    assert mock_fill.call_count == 4  # 1 class and 3 fields total
    mock_fill.assert_any_call(nested_ids, 'simple', SimpleDataClass, None)
    mock_fill.assert_any_call(nested_ids, 'values', int, None)


def test_list_without_fill(sample_dataclasses, mock_dependencies):
    """Test that lists are not populated when fill_list is False."""
    ComplexDataClass = sample_dataclasses['ComplexDataClass']
    NestedDataClass = sample_dataclasses['NestedDataClass']
    SimpleDataClass = sample_dataclasses['SimpleDataClass']

    # Create instance with a list
    complex_ids = ComplexDataClass()

    # Configure mocks
    mock_dependencies['get_type_arg'].side_effect = [
        (NestedDataClass, None),
        (SimpleDataClass, None),  # For NestedDataClass.simple
        (int, None),  # For SimpleDataClass.value in nested
        (str, None),  # For SimpleDataClass.name in nested
        (list[int], None),  # For NestedDataClass.values
        (list[SimpleDataClass], None),
        (list[float], None)
    ]

    # Call function with fill_list=False (default)
    fill_default_values_ids(complex_ids)

    # Verify the lists remain empty
    assert len(complex_ids.items) == 0
    assert len(complex_ids.data) == 0


def test_list_with_fill(sample_dataclasses, mock_dependencies):
    """Test that lists are populated when fill_list is True."""
    ComplexDataClass = sample_dataclasses['ComplexDataClass']
    NestedDataClass = sample_dataclasses['NestedDataClass']
    SimpleDataClass = sample_dataclasses['SimpleDataClass']

    # Create instance with a list
    complex_ids = ComplexDataClass()

    # Configure mocks to return appropriate types
    def mock_side_effect(*args, **kwargs):
        field_vars = args[1]
        if field_vars.name == 'items':
            return SimpleDataClass, True
        elif field_vars.name == 'data':
            return float, True
        elif field_vars.name == 'nested':
            return NestedDataClass, False
        elif field_vars.name == 'simple':
            return SimpleDataClass, False
        elif field_vars.name == 'values':
            return int, True
        elif field_vars.name == 'value':
            return int, False
        elif field_vars.name == 'name':
            return str, False
        else:
            return None, False

    mock_dependencies['get_type_arg'].side_effect = mock_side_effect

    # Patch the recursive call to fill_default_values_ids
    with patch('idspy_toolkit.fill_default_values_ids', side_effect=fill_default_values_ids) as mock_recursive:
        # Call function with fill_list=True, error should be raised in case of list of int
        with pytest.raises(TypeError):
            fill_default_values_ids(complex_ids, fill_list=True)



def test_with_root_type(sample_dataclasses, mock_dependencies):
    """Test passing a root_type parameter."""
    SimpleDataClass = sample_dataclasses['SimpleDataClass']

    simple_ids = SimpleDataClass()
    root_type = MagicMock()

    mock_dependencies['get_type_arg'].side_effect = [
        (int, None),
        (str, None)
    ]

    # Call with root_type
    fill_default_values_ids(simple_ids, root_type=root_type)

    # Verify root_type was passed
    mock_fill = mock_dependencies['fill_default']
    mock_fill.assert_any_call(simple_ids, 'value', int, root_type)
    mock_fill.assert_any_call(simple_ids, 'name', str, root_type)


def test_key_error_handling(sample_dataclasses, mock_dependencies):
    """Test handling of KeyError when getting type arguments."""
    SimpleDataClass = sample_dataclasses['SimpleDataClass']

    simple_ids = SimpleDataClass()

    # First call raises KeyError, second call succeeds
    mock_dependencies['get_type_arg'].side_effect = [
        KeyError("Test error"),
        (int, None),
        KeyError("Test error"),
        (str, None)
    ]

    # Function should handle the KeyError and continue
    fill_default_values_ids(simple_ids)

    # Verify __fill_default_values_ids was still called for each field
    mock_fill = mock_dependencies['fill_default']
    assert mock_fill.call_count == 2


def test_integration():
    """Integration test with real implementation."""

    # For integration testing, we need to import the actual function
    # import idspy_toolkit as pkg

    # Define test classes
    @dataclasses.dataclass
    class SimpleDataClass:
        value: Optional[int] = None
        name: Optional[str] = None

    @dataclasses.dataclass
    class TestClass:
        int_val: Optional[int] = None
        str_val: Optional[str] = None
        nested: Optional[SimpleDataClass] = None

    # Create test instance
    test_obj = TestClass()

    # Call the actual function (no mocks for integration test)
    fill_default_values_ids(test_obj)

    # Verify values were filled with actual implementation
    assert test_obj.int_val is not None
    assert test_obj.str_val is not None
    assert isinstance(test_obj.nested, SimpleDataClass)
    assert test_obj.nested.value is not None
    assert test_obj.nested.name is not None


def test_dataclass_list_items(sample_dataclasses):
    """Test filling list items that are dataclasses."""
    SimpleDataClass = sample_dataclasses['SimpleDataClass']

    @dataclasses.dataclass
    class ListContainer:
        items: list[SimpleDataClass] = dataclasses.field(default_factory=list)


    container = ListContainer()
    fill_default_values_ids(container, fill_list=False)
    assert len(container.items) == 0
    container = ListContainer()
    fill_default_values_ids(container, fill_list=True)
    assert len(container.items) == 1
    #container.items.append(SimpleDataClass(value=None, name=None))
    fill_default_values_ids(container, fill_list=True)
    assert len(container.items) == 1
    fill_default_values_ids(container, fill_list=False)
    assert len(container.items) == 1


@pytest.mark.parametrize("fill_list,expected_count", [
    (False, 0),  # No items added when fill_list is False
    (True, 1)  # One item added when fill_list is True
])
def test_parametrized_list_filling(sample_dataclasses, mock_dependencies, fill_list, expected_count):
    """Test list filling behavior with different fill_list parameter values."""
    SimpleDataClass = sample_dataclasses['SimpleDataClass']

    @dataclasses.dataclass
    class ListContainer:
        items: list[SimpleDataClass] = dataclasses.field(default_factory=list)

    container = ListContainer()

    # Configure get_type_arg to return the appropriate type
    mock_dependencies['get_type_arg'].return_value = (SimpleDataClass, None)

    # Set up recursive call mocking
    with patch('idspy_toolkit.fill_default_values_ids', side_effect=fill_default_values_ids) as mock_recursive:
        # Call function with the parametrized fill_list value
        fill_default_values_ids(container, fill_list=fill_list)

        # Check if items were added according to the expectation
        assert len(container.items) == expected_count

