import dataclasses
import numpy as np
import pytest
from idspy_toolkit.utils import snake2camel, camel2snake, get_field_with_type, extract_ndarray_info, \
    _imas_default_values, __get_field_type, get_all_class, _check_simplified_types
from tests.classes_skels import ClassListNested, ClassListMixDictIn, ClassOldStyle, ClassListMixDict


def test_snake2camel():
    # Test the snake2camel function
    assert snake2camel("device_type") == "DeviceType"
    assert snake2camel("first_name") == "FirstName"
    assert snake2camel("my_snake_string") == "MySnakeString"
    assert snake2camel("all_caps") == "AllCaps"
    assert snake2camel("") == ""


def test_camel2snake():
    # Test the camel2snake function
    assert camel2snake("DeviceType") == "device_type"
    assert camel2snake("FirstName") == "first_name"
    assert camel2snake("MySnakeString") == "my_snake_string"
    assert camel2snake("AllCaps") == "all_caps"
    assert camel2snake("") == ""


def test_class_type_extraction():
    test1 = ClassListNested()
    with pytest.raises(ValueError):
        get_field_with_type(test1, ClassListNested.space)
    assert get_field_with_type(test1, "space") == (567, int)
    field_space = [x for x in dataclasses.fields(test1) if x.name == "space"][0]
    assert get_field_with_type(test1, field_space) == (567, int)


def test_type_check():
    test1 = ClassListNested()
    field_space = [x for x in dataclasses.fields(test1) if x.name == "space"][0]

    test1.space = 2.23
    with pytest.raises(TypeError):
        get_field_with_type(test1, "space")
    with pytest.raises(TypeError):
        get_field_with_type(test1, field_space)
    test1.space = np.array(123)
    assert get_field_with_type(test1, "space") == (123, int)
    test1.space = np.array(123.)
    with pytest.raises(TypeError):
        get_field_with_type(test1, "space")
    test1.space = None
    assert get_field_with_type(test1, "space") == (None, int)

    list_item = ClassListMixDict()
    assert get_field_with_type(list_item, "time") == (["1.234", "5.678"], str)


def test_extract_ndarray():
    good_str = r"numpy.ndarray[(<class 'int'>,), float]"
    good_str_2 = r"numpy.ndarray[(<class 'int'>, <class 'int'>,), float]"
    bad_str_1 = r"numpy.ndarray[float, float]"
    bad_str_2 = r"numpy.ndarray[(<class 'float'>,), float]"
    extract_ndarray_info(good_str)
    extract_ndarray_info(good_str_2)
    with pytest.raises(ValueError):
        extract_ndarray_info(bad_str_1)
    with pytest.raises(ValueError):
        extract_ndarray_info(bad_str_2)


def test_imas_default_values():
    assert _imas_default_values(bool) is False
    assert _imas_default_values(int) == 999999999
    assert _imas_default_values(float) == 9.0e40
    assert _imas_default_values(str) == ""
    assert _imas_default_values(complex) == complex(9.0e40, -9.0e40)
    assert _imas_default_values(list) == []
    assert _imas_default_values(tuple) == []
    assert isinstance(_imas_default_values(ClassOldStyle), ClassOldStyle)
    # Test for numpy arrays
    assert np.array_equal(_imas_default_values(np.ndarray), np.array([]))
    # TODO : add tests corresponding to list of IDS


def test_get_fields_type():
    test1 = ClassListNested()
    field_space = {x.name: __get_field_type(x) for x in dataclasses.fields(test1)}
    assert field_space["time"] == str
    assert field_space["space"] == int
    assert field_space["name"] == str
    assert field_space["jsonarg"] == dict
    assert field_space["nestedclass"] == ClassListMixDictIn


def test_get_all_classes():
    import tests.classes_skels as iutils
    dict_report = {}
    get_all_class(iutils, dict_report)
    assert len(dict_report) == 19
    assert sorted(dict_report.keys()) == sorted(["ArrayClass", "BaseClass", "BaseClassUT", "Class1", "Class3",
                                                 "ClassEmpty", "ClassList", "ClassList2",
                                                 "ClassOldStyle",
                                                 "ClassListMix",
                                                 "ClassListMixDict", "ClassListMixDict2",
                                                 "ClassListMixDictIn",
                                                 "ClassListNested", "ClassListNestedList", "ClassListNightmare",
                                                 "subclass", "subsubclass", "IdsVersion"])


def test_check_simplified_types():
    # Test if an integer variable has the expected type
    assert _check_simplified_types(int, int) is True
    assert _check_simplified_types(int, np.int32) is True
    assert _check_simplified_types(int, np.int64) is True

    # Test if a float variable has the expected type
    assert _check_simplified_types(float, float) is True
    assert _check_simplified_types(float, np.float32) is True
    assert _check_simplified_types(float, np.float64) is True

    # Test if a complex variable has the expected type
    assert _check_simplified_types(complex, np.complex64) is True
    assert _check_simplified_types(np.complex128, np.complex64) is True


    # Test if a string variable has the expected type
    assert _check_simplified_types(str, int) is False
    assert _check_simplified_types(str, bytearray) is False
