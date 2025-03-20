import pytest
import dataclasses
from typing import Optional
from numpy import ndarray
import numpy as np

from tests.classes_skels import *
from idspy_toolkit.accessor import get_ids_value_from_string, \
    set_ids_value_from_string, is_list_member, copy_ids, get_type_arg, create_instance_from_type, _is_0d_array, _convert_bytes_to_str
from idspy_toolkit.utils import _imas_default_values

@dataclasses.dataclass
class SubSubClass:
    member_subsubclass_aa: Optional[str] = dataclasses.field(default=""
                                                             )
    member_subsubclass_bb: Optional[int] = dataclasses.field(default=999999999
                                                             )
    member_subsubclass_cc: Optional[float] = dataclasses.field(default=9.4e40
                                                               )


@dataclasses.dataclass
class SubClass:
    member_subclass: Optional[SubSubClass] = dataclasses.field(
        default=None
    )


@dataclasses.dataclass
class BaseClass:
    list_member: list[SubClass] = dataclasses.field(
        default_factory=list,

    )
    list_member_foreign: list["SubclassNested"] = dataclasses.field(
        default_factory=list,

    )
    nda_member: Optional[ndarray[(int, int), float]] = dataclasses.field(
        default=None,
    )

    @dataclasses.dataclass
    class SubclassNested:
        member_subsubclass_aa: Optional[str] = dataclasses.field(default=""
                                                                 )


@dataclasses.dataclass
class DbgSubDataClass:
    subfield1: str
    subfield2: int


@dataclasses.dataclass
class DbgMainDataClass:
    field1: str
    field2: int
    subfield_list: list[DbgSubDataClass]


@dataclasses.dataclass
class SubDataClass:
    subfield1: str
    subfield2: int


@dataclasses.dataclass
class MainDataClass:
    field1: str
    field2: int
    subfield: SubDataClass
    subfield_list: list[SubDataClass]


@dataclasses.dataclass
class MyClass:
    __test__ = False
    my_list: list[int]
    my_string: str


@dataclasses.dataclass
class TestListMemberClass:
    __test__ = False
    # Regular list field
    simple_list: list[int] = dataclasses.field(default_factory=list)
    
    # Field with ndims metadata
    array_field: np.ndarray = dataclasses.field(
        default=None,
        metadata={"ndims": 2, "field_type": np.ndarray}
    )
    
    array_field_int: list[int] = dataclasses.field(
        default=None,
        metadata={"ndims": 2, "field_type": int}
    )
    # Field with ndims but specified as numpy array
    numpy_field: np.ndarray = dataclasses.field(
        default=None,
        metadata={"ndims": 2, "field_type": np.ndarray}
    )
    
    # Regular non-list field
    normal_field: int = dataclasses.field(default=0)
    
    # List with complex type
    complex_list: list[SubDataClass] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class TestListMemberMetadataClass:
    __test__ = False
    # Field with complete metadata
    field_with_metadata: np.ndarray = dataclasses.field(
        default=None,
        metadata={"ndims": 2, "field_type": np.ndarray}
    )
    
    # Field with empty metadata
    field_empty_metadata: np.ndarray = dataclasses.field(
        default=None,
        metadata={}
    )
    
    # Field with metadata but no ndims
    field_no_ndims: np.ndarray = dataclasses.field(
        default=None,
        metadata={"field_type": np.ndarray}
    )
    
    # Field without metadata
    field_no_metadata: np.ndarray = dataclasses.field(
        default=None
    )


def test_get_type_arg():
    assert get_type_arg(MyClass, "my_list") == (int, True)
    assert get_type_arg(MyClass, "my_string") == (str, False)
    with pytest.raises(KeyError):
        get_type_arg(MyClass, "nonexistent_field")


def test_is_list_member():
    test_class = TestListMemberClass()
    
    # Test regular list field
    assert is_list_member(test_class, "simple_list") is True
    
    # Test field with ndims metadata but not numpy array
    assert is_list_member(test_class, "array_field") is False
    
    # Test field with ndims metadata but not numpy array
    assert is_list_member(test_class, "array_field_int") is True
    
    # Test field with ndims metadata and numpy array type
    assert is_list_member(test_class, "numpy_field") is False
    
    # Test regular non-list field
    assert is_list_member(test_class, "normal_field") is False
    
    # Test list with complex type
    assert is_list_member(test_class, "complex_list") is True
    
    # Test non-existent field
    with pytest.raises(KeyError):
        is_list_member(test_class, "non_existent_field")


def test_get_ids_value_from_string():
    # create source dataclass with nested dataclass containing list
    source_subfield_list = [
        SubDataClass("subfield1_1", 1),
        SubDataClass("subfield1_2", 2),
        SubDataClass("subfield1_3", 3),
        SubDataClass("subfield1_4", 4),
        SubDataClass("subfield1_5", 5)
    ]
    source_dataclass = MainDataClass("field1", 123, SubDataClass("subfield1", 1), source_subfield_list)

    # create destination dataclass with different values
    dest_subfield_list = [
        SubDataClass("dest_subfield1_1", 10),
        SubDataClass("dest_subfield1_2", 20),
        SubDataClass("dest_subfield1_3", 30),
        SubDataClass("dest_subfield1_4", 40),
        SubDataClass("dest_subfield1_5", 50)
    ]
    dest_dataclass = MainDataClass("dest_field1", 456, SubDataClass("dest_subfield1", 100), dest_subfield_list)

    # copy source to destination
    copy_ids(dest_dataclass, source_dataclass)
    with pytest.raises(KeyError):
        get_ids_value_from_string(source_dataclass, "/MainDataClass/subfield_list#000000/")
    with pytest.raises(KeyError):
        get_ids_value_from_string(source_dataclass, "/MainDataClass/subfield_list#000001/")
    with pytest.raises(KeyError):
        get_ids_value_from_string(source_dataclass, "/MainDataClass/subfield_list#000001")

    # check that destination dataclass now has same values as source dataclass
    assert get_ids_value_from_string(dest_dataclass, "field1") == "field1"
    assert get_ids_value_from_string(dest_dataclass, "field2") == 123
    assert get_ids_value_from_string(dest_dataclass, "subfield/subfield1") == "subfield1"
    assert get_ids_value_from_string(dest_dataclass, "subfield/subfield2") == 1
    assert get_ids_value_from_string(source_dataclass, "subfield_list#000001/subfield1") == "subfield1_2"

def test_set_ids_value_from_string():
    # Create a test instance of MainDataClass
    test_mc = DbgMainDataClass(
        field1="value1",
        field2=123,
        subfield_list=[
            DbgSubDataClass(subfield1="subvalue1", subfield2=456),
            DbgSubDataClass(subfield1="subvalue2", subfield2=789)
        ]
    )

    # Test setting an existing value
    set_ids_value_from_string(test_mc, "field1", "new_value")
    assert test_mc.field1 == "new_value"

    # Test setting a value in a subfield
    set_ids_value_from_string(test_mc, "subfield_list#0000/subfield2", 999)
    assert test_mc.subfield_list[0].subfield2 == 999

    # Test creating a missing subfield
    set_ids_value_from_string(test_mc, "subfield_list#0002/subfield1", "new_subvalue")
    assert test_mc.subfield_list[2].subfield1 == "new_subvalue"

    # Test setting a value in a subfield of type list without number
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_mc, "subfield_list/subfield2", 777)

    # Test setting a value in a subfield of type list without number with create_missing=False
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_mc, "subfield_list/subfield2", 777, create_missing=False)

    # Test setting a value in a non-list subfield with create_missing=True
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_mc, "field3/subfield1", "new_value", create_missing=True)

    # Test setting a value in a list subfield without specifying an index
    with pytest.raises(ValueError):
        set_ids_value_from_string(test_mc, "subfield_list", "new_value")

    # Test setting a value in a list subfield with an invalid index
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_mc, "subfield_list#0001/subfield2#99", 999)




@dataclasses.dataclass
class MyClass:
    my_list: list[int] = field(default_factory=list)
    my_string: str =""


def test_create_instance_from_type():
    assert isinstance(create_instance_from_type(int), int)
    assert isinstance(create_instance_from_type(float), float)
    assert isinstance(create_instance_from_type(str), str)
    assert isinstance(create_instance_from_type(list), list)
    assert isinstance(create_instance_from_type(tuple), list)
    assert isinstance(create_instance_from_type(bool), bool)
    assert isinstance(create_instance_from_type(complex), complex)
   # assert isinstance(create_instance_from_type(ndarray), ndarray)

    assert create_instance_from_type(int) == _imas_default_values(int)
    assert create_instance_from_type(float) == _imas_default_values(float)
    assert create_instance_from_type(str) == _imas_default_values(str)
    assert create_instance_from_type(list) == _imas_default_values(list)
    assert create_instance_from_type(tuple) == _imas_default_values(list)
    assert create_instance_from_type(bool) == _imas_default_values(bool)
    assert create_instance_from_type(complex) == _imas_default_values(complex)
    #assert create_instance_from_type(ndarray) == _imas_default_values(ndarray)


def test_is_list_member_metadata():
    test_class = TestListMemberMetadataClass()
    
    # Test field with complete metadata
    assert is_list_member(test_class, "field_with_metadata") is False
    
    # Test field with empty metadata
    assert is_list_member(test_class, "field_empty_metadata") is False
    
    # Test field with metadata but no ndims
    assert is_list_member(test_class, "field_no_ndims") is False
    
    # Test field without metadata
    assert is_list_member(test_class, "field_no_metadata") is False

    # Test with non-dataclass
    with pytest.raises(TypeError):
        is_list_member("not_a_dataclass", "some_field")


def test_is_0d_array():
    # Test 0D numpy array
    zero_d = np.array(5)  # Creates a 0D array (scalar)
    assert _is_0d_array(zero_d) is True
    
    # Test 1D numpy array
    one_d = np.array([1, 2, 3])
    assert _is_0d_array(one_d) is False
    
    # Test 2D numpy array
    two_d = np.array([[1, 2], [3, 4]])
    assert _is_0d_array(two_d) is False
    
    # Test non-numpy types
    assert _is_0d_array(5) is False  # integer
    assert _is_0d_array([1, 2, 3]) is False  # list
    assert _is_0d_array("string") is False  # string
    assert _is_0d_array(None) is False  # None
    
    # Test empty numpy array
    empty_array = np.array([])
    assert _is_0d_array(empty_array) is False
    
    # Test numpy scalar types
    assert _is_0d_array(np.float64(5.0)) is False
    assert _is_0d_array(np.int32(5)) is False


def test_convert_bytes_to_str():
    # Test simple list of bytes
    bytes_list = [b'hello', b'world']
    result = _convert_bytes_to_str(bytes_list)
    np.testing.assert_array_equal(result, np.array(['hello', 'world']))
    
    # Test nested list of bytes
    nested_bytes = [[b'hello', b'world'], [b'foo', b'bar']]
    result = _convert_bytes_to_str(nested_bytes)
    np.testing.assert_array_equal(result, np.array([['hello', 'world'], ['foo', 'bar']]))
    
    # Test numpy array of bytes
    bytes_array = np.array([b'hello', b'world'])
    result = _convert_bytes_to_str(bytes_array)
    np.testing.assert_array_equal(result, np.array(['hello', 'world']))
    
    # Test mixed nested structure
    mixed_data = [b'hello', [b'world', b'foo'], b'bar']
    with pytest.raises(ValueError):
        _convert_bytes_to_str(mixed_data)
    
    # Test empty list
    empty_list = []
    result = _convert_bytes_to_str(empty_list)
    np.testing.assert_array_equal(result, np.array([]))
    
    # Test tuple input
    bytes_tuple = (b'hello', b'world')
    result = _convert_bytes_to_str(bytes_tuple)
    np.testing.assert_array_equal(result, np.array(['hello', 'world']))
    
    # Test nested tuple and list mix
    mixed_tuple_list = ([b'hello', b'world'], (b'foo', b'bar'))
    result = _convert_bytes_to_str(mixed_tuple_list)
    np.testing.assert_array_equal(result, np.array([['hello', 'world'], ['foo', 'bar']]))
    
    # Test 2D numpy array of bytes
    array_2d = np.array([[b'hello', b'world'], [b'foo', b'bar']])
    result = _convert_bytes_to_str(array_2d)
    np.testing.assert_array_equal(result, np.array([['hello', 'world'], ['foo', 'bar']]))


def test_get_type_arg_edge_cases():
    # Test handling of NameError (lines 72-80)
    class ForwardRefClass:
        field: "NonExistentType"
    
    with pytest.raises(KeyError):
        get_type_arg(ForwardRefClass, "field")
    
    # Test handling of KeyError (line 102)
    with pytest.raises(KeyError):
        get_type_arg(MyClass, "non_existent")

def test_get_ids_value_from_string_edge_cases():
    # Test handling of empty paths (lines 140-141)
    with pytest.raises(KeyError):
        get_ids_value_from_string(MyClass(), "")
    
    # Test handling of invalid paths (line 163)
    with pytest.raises(AttributeError):
        get_ids_value_from_string(MyClass(), "invalid/path")

def test_set_ids_value_from_string_edge_cases():
    test_class = MainDataClass("test", 1, SubDataClass("sub", 2), [])
    
    # Test handling of missing attributes (lines 216-224)
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_class, "nonexistent/path", "value")
    
    # Test handling of list elements (lines 228-231)
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_class, "subfield_list/invalid", "value")

    # Test type validation (lines 281-285)
    with pytest.raises(ValueError):
        set_ids_value_from_string(test_class, "field1", 123)  # Should be string
    
    # Test list validation (line 289)
    with pytest.raises(ValueError):
        set_ids_value_from_string(test_class, "subfield_list", "not_a_list")

def test_copy_ids_edge_cases():
    # Test handling of non-dataclass inputs (lines 345-346)
    with pytest.raises(TypeError):
        copy_ids("not_a_dataclass", MyClass())
    
    # Test handling of missing fields (lines 348, 352)
    class SourceClass:
        field: str = "test"
    class DestClass:
        other_field: str = "other"
    
    with pytest.raises(TypeError):
        copy_ids(DestClass(), SourceClass())

def test_set_ids_value_complex_cases():
    test_class = MainDataClass("test", 1, SubDataClass("sub", 2), [])
    
    # Test XML string conversion (lines 373-387)
    xml_value = "<root><item>test</item></root>"
    set_ids_value_from_string(test_class, "field1", xml_value, todict=True)
    
    # Test JSON string conversion (lines 390-401)
    json_value = '{"item": "test"}'
    set_ids_value_from_string(test_class, "field1", json_value, todict=True)
    
    # Test bytes conversion (lines 408-422)
    bytes_value = b"test"
    set_ids_value_from_string(test_class, "field1", bytes_value)

def test_list_operations():
    test_class = MainDataClass("test", 1, SubDataClass("sub", 2), [])
    
    # Test list creation (lines 426-436)
    set_ids_value_from_string(test_class, "subfield_list#0/subfield1", "new_value", create_missing=True)
    assert test_class.subfield_list[0].subfield1 == "new_value"
    
    # Test list bounds checking (line 442)
    with pytest.raises(IndexError):
        set_ids_value_from_string(test_class, "subfield_list#999/subfield1", "value")

def test_type_validation():
    test_class = MainDataClass("test", 1, SubDataClass("sub", 2), [])
    
    # Test type validation for lists (lines 479-486)
    # with pytest.raises(ValueError):
    #     set_ids_value_from_string(test_class, "subfield_list#0", "not_a_subclass")
    
    # Test type validation for simple fields (lines 493-500)
    with pytest.raises(ValueError):
        set_ids_value_from_string(test_class, "field2", "not_an_int")

def test_get_type_arg_additional_cases():
    # Test field with name attribute (lines 102, 106)
    field = dataclasses.field(default=None)
    field.name = "test_field"
    
    with pytest.raises(KeyError):
        get_type_arg(MyClass, field)

def test_get_ids_value_from_string_additional_cases():
    test_class = MainDataClass("test", 1, SubDataClass("sub", 2), [
        SubDataClass("list1", 1),
        SubDataClass("list2", 2)
    ])
    
    # Test list access with invalid index (lines 146-147)
    with pytest.raises(IndexError):
        get_ids_value_from_string(test_class, "subfield_list#5/subfield1")
    
    # Test empty list access (line 169)
    empty_class = MainDataClass("test", 1, SubDataClass("sub", 2), [])
    with pytest.raises(ValueError):
        get_ids_value_from_string(empty_class, "subfield_list#0/subfield1")

def test_set_ids_value_from_string_additional_cases():
    test_class = MainDataClass("test", 1, SubDataClass("sub", 2), [])
    
    # Test list operations with create_missing=False (lines 222-234)
    with pytest.raises(IndexError):
        set_ids_value_from_string(test_class, "subfield_list#0/subfield1", "value", create_missing=False)
    
    # Test list with non-zero offset when empty (line 226)
    with pytest.raises(IndexError):
        set_ids_value_from_string(test_class, "subfield_list#1/subfield1", "value", create_missing=True)
    
    # Test list attribute that isn't a list (lines 228-230)
    with pytest.raises(AttributeError):
        set_ids_value_from_string(test_class, "field1#0", "value")
    
    # Test missing attribute with create_missing=False (line 240)
    with pytest.raises(KeyError):
        set_ids_value_from_string(test_class, "nonexistent", "value", create_missing=False)


