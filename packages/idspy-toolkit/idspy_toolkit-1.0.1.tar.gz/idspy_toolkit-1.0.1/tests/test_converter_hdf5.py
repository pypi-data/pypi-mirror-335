import dataclasses

import pytest
import h5py
from tests.classes_skels import *
from idspy_toolkit.converter import ids_to_hdf5, get_inner_type_list, hdf5_to_ids, _is_list_empty, _is_item_list
from random import randrange
from typing import Union
from numpy import array

import numpy as np


@pytest.fixture(scope="function")
def hdf5_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / "class_ids_{0:04d}.h5".format(randrange(0, 9999))
    return fn


def _parse_hdf5(list_to_check: list, name: str) -> Union[None, int]:
    if name in list_to_check:
        list_to_check.remove(name)
    else:
        raise ValueError(f"item not expected found {name}")
    if len(list_to_check) == 0:
        return 0
    return None


# contents of test_image.py
def test_creation_class(hdf5_file):
    myclass = ClassOldStyle()
    assert ids_to_hdf5(myclass, hdf5_file) == (0,0)


def test_creation_dataclass_empty(hdf5_file):
    myclass = ClassEmpty()
    assert ids_to_hdf5(myclass, hdf5_file) == (0, 0)


def test_creation_dataclass_single(hdf5_file):
    myclass = Class1()
    assert ids_to_hdf5(myclass, hdf5_file) == (1, 1)


def test_creation_dataclass_evil(hdf5_file):
    myclass = ClassListNightmare()
    assert ids_to_hdf5(myclass, hdf5_file) == (1, 6)


test_class = [
    (Class1, (1, 1)),
    (Class3, (1, 3)),
    (ClassList, (1, 1)),
    (ClassList2, (1, 1)),
    (ClassListMix, (1, 3)),
    (ClassListMixDict, (1, 4)),
    (ClassListNested, (2, 10)),
    (ClassListNestedList, (3, 15))
]


@pytest.mark.parametrize('classtype, expected', test_class)
def test_creation_dataclass_multiple(hdf5_file, classtype, expected):
    myclass = classtype()
    assert ids_to_hdf5(myclass, hdf5_file) == expected


test_class = [
    (Class1, ("Class1",
              "Class1/time",)),
    (Class3, ("Class3",
              "Class3/time", "Class3/space", "Class3/name")),
    (ClassList, ("ClassList",
                 "ClassList/time",)),
    (ClassList2, ("ClassList2",
                  "ClassList2/time",)),
    (ClassListMix, ("ClassListMix",
                    "ClassListMix/name", "ClassListMix/space", "ClassListMix/time")),
    (ClassListMixDict, ("ClassListMixDict", "ClassListMixDict/jsonarg", "ClassListMixDict/name",
                        "ClassListMixDict/space", "ClassListMixDict/time")),
    (ClassListNested, ("ClassListNested", "ClassListNested/nestedclass",
                       "ClassListNested/nestedclass/jsonarg1_0", "ClassListNested/nestedclass/jsonarg1_1",
                       "ClassListNested/nestedclass/name1", "ClassListNested/nestedclass/space1",
                       "ClassListNested/nestedclass/time1", "ClassListNested/jsonarg_0",
                       "ClassListNested/jsonarg_1", "ClassListNested/name",
                       "ClassListNested/space", "ClassListNested/time")),
    (ClassListNestedList, ("ClassListNestedList",
                           "ClassListNestedList/nestedclass#000000",
                           "ClassListNestedList/nestedclass#000000/jsonarg1_0",
                           "ClassListNestedList/nestedclass#000000/jsonarg1_1",
                           "ClassListNestedList/nestedclass#000000/name1",
                           "ClassListNestedList/nestedclass#000000/space1",
                           "ClassListNestedList/nestedclass#000000/time1",
                           "ClassListNestedList/nestedclass#000001",
                           "ClassListNestedList/nestedclass#000001/jsonarg1_0",
                           "ClassListNestedList/nestedclass#000001/jsonarg1_1",
                           "ClassListNestedList/nestedclass#000001/name1",
                           "ClassListNestedList/nestedclass#000001/space1",
                           "ClassListNestedList/nestedclass#000001/time1",
                           "ClassListNestedList/jsonarg_0",
                           "ClassListNestedList/jsonarg_1",
                           "ClassListNestedList/name",
                           "ClassListNestedList/space",
                           "ClassListNestedList/time")
     )
]


@pytest.mark.parametrize("classtype, expected", test_class)
def test_structure_dataclass_multiple(hdf5_file, classtype, expected):
    myclass = classtype()
    ids_to_hdf5(myclass, hdf5_file)
    current_list = list(expected)

    with h5py.File(hdf5_file, "r") as f:
        f["/"].visit(lambda x: _parse_hdf5(current_list, x))
        assert len(current_list) == 0


def test_list_type():
    assert isinstance(get_inner_type_list([2, ]), int)
    assert get_inner_type_list([[]]) is None
    assert isinstance(get_inner_type_list([[2, ], ]), int)
    assert isinstance(get_inner_type_list([[[2, ], [3, 4]]]), int)
    assert isinstance(get_inner_type_list([[{3: 4, 5: 6}, ], ]), dict)


def test_structure_dataclass_list_nested(hdf5_file):
    myclass = BaseClass(
        list_member=[
            subclass(member_subclass=subsubclass(member_subsubclass_aa="123", member_subsubclass_bb=12345)), subclass(),
        ], )
    ids_to_hdf5(myclass, hdf5_file)

    read_class = BaseClass()
    hdf5_to_ids(hdf5_file, read_class)

    assert len(read_class.list_member) == 1
    assert read_class.list_member[0] == myclass.list_member[0]


def test_structure_dataclass_array_0d(hdf5_file):
    myclass = ArrayClass()
    myclass.val_array_0d = array(42.)

    ids_to_hdf5(myclass, hdf5_file)
    read_class = ArrayClass()
    hdf5_to_ids(hdf5_file, read_class)
    assert np.testing.assert_array_equal(read_class.val_array_1d, myclass.val_array_1d) is None
    assert np.testing.assert_array_equal(read_class.val_array_0d, myclass.val_array_0d) is None
    assert isinstance(read_class.val_array_0d, np.floating) is True
    assert isinstance(read_class.val_array_0d, np.ndarray) is False


def test_is_list_empty():
    assert _is_list_empty([]) is True
    assert _is_list_empty(()) is True
    assert _is_list_empty(np.array([])) is True
    assert _is_list_empty(np.array(1)) is False
    assert _is_list_empty([1, 2, 3]) is False
    assert _is_list_empty("not a list") is False


def test_is_item_list():
    assert _is_item_list([]) is True
    assert _is_item_list(()) is True
    assert _is_item_list(np.array([])) is True
    assert _is_item_list(np.array(1)) is False
    assert _is_item_list([1, 2, 3]) is True
    assert _is_item_list("not a list") is False
