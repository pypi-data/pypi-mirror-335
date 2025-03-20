import pytest
import numpy as np
from idspy_dictionaries.dataclasses_idsschema import StructArray, IdsVersion
from idspy_dictionaries._version import (
    _IDSPY_VERSION,
    _IDSPY_IMAS_DD_GIT_COMMIT,
    _IDSPY_IMAS_DD_VERSION,
    _IDSPY_INTERNAL_VERSION
)

# Define common numpy types for testing
NUMPY_INT_TYPES = [np.int32, np.int64]
NUMPY_FLOAT_TYPES = [np.float32, np.float64]
NUMPY_COMPLEX_TYPES = [np.complex64, np.complex128]

def test_structarray_initialization_empty():
    # Test empty initialization
    sa = StructArray()
    assert len(sa) == 0
    assert sa.type_items is None

def test_structarray_initialization_list_int():
    # Test initialization with list and type
    with pytest.raises(TypeError):
        sa = StructArray([1, 2, 3], int)

def test_structarray_initialization_int():
    # Test initialization with list and type
    with pytest.raises(TypeError):
        sa = StructArray(type_item=int)
#
#
# def test_structarray_numpy_int64():
#     sa = StructArray(type_input=np.int64)
#     values = [np.int64(1), np.int64(2**32), np.int64(2**60)]
#     for val in values:
#         sa.append(val)
#
#     assert len(sa) == 3
#     assert all(isinstance(x, np.int64) for x in sa)
#
#     # Test type enforcement
#     with pytest.raises(TypeError):
#         sa.append(1.2)  # regular Python int
#
#     with pytest.raises(TypeError):
#         sa.append(np.float32(1.2))
#
# def test_structarray_numpy_float64():
#     sa = StructArray(type_input=np.float64)
#     values = [np.float64(1.5), np.float64(np.pi), np.float64(1e-10)]
#     for val in values:
#         sa.append(val)
#
#     assert len(sa) == 3
#     assert all(isinstance(x, np.float64) for x in sa)
#
#     # Test type enforcement
#     with pytest.raises(TypeError):
#         sa.append(np.complex128(.5,.5))  # regular Python float
#
#
# def test_structarray_numpy_float64_with_float():
#     sa = StructArray(type_input=np.float64)
#     values = [np.float64(1.5), np.float64(np.pi), np.float64(1e-10)]
#     for val in values:
#         sa.append(float(val))
#
#     assert len(sa) == 3
#     assert all(isinstance(x, float) for x in sa)
#
#     sa.append(1.5)  # regular Python float
#     assert len(sa) == 4
#
# def test_structarray_numpy_complex128():
#     sa = StructArray(type_input=np.complex128)
#     values = [
#         np.complex128(1 + 2j),
#         np.complex128(3.14 - 2.718j),
#         np.complex128(1e-10 + 1e-10j)
#     ]
#     for val in values:
#         sa.append(val)
#
#     assert len(sa) == 3
#     assert all(isinstance(x, np.complex128) for x in sa)
#
#     # Test type enforcement
#     sa.append(1 + 2j)  # regular Python complex
#
# @pytest.mark.parametrize("numpy_type", NUMPY_INT_TYPES)
# def test_structarray_numpy_int_types(numpy_type):
#     sa = StructArray(type_input=numpy_type)
#     val = numpy_type(42)
#     sa.append(val)
#     assert isinstance(sa[0], numpy_type)
#     assert sa[0] == val
#
# @pytest.mark.parametrize("numpy_type", NUMPY_FLOAT_TYPES)
# def test_structarray_numpy_float_types(numpy_type):
#     sa = StructArray(type_input=numpy_type)
#     val = numpy_type(3.14159)
#     sa.append(val)
#     assert isinstance(sa[0], numpy_type)
#     assert np.isclose(sa[0], val)
#
# @pytest.mark.parametrize("numpy_type", NUMPY_COMPLEX_TYPES)
# def test_structarray_numpy_complex_types(numpy_type):
#     sa = StructArray(type_input=numpy_type)
#     val = numpy_type(1. + 2.0j)
#     sa.append(val)
#     assert isinstance(sa[0], numpy_type)
#     assert np.isclose(sa[0], val)
#
# def test_structarray_numpy_array():
#     # Test with 1D array
#     sa = StructArray(type_input=np.ndarray)
#     arr1 = np.array([1, 2, 3])
#     arr2 = np.array([4, 5, 6])
#     sa.append(arr1)
#     sa.append(arr2)
#
#     assert len(sa) == 2
#     assert all(isinstance(x, np.ndarray) for x in sa)
#     assert np.array_equal(sa[0], arr1)
#     assert np.array_equal(sa[1], arr2)
#
# def test_structarray_numpy_array_2d():
#     sa = StructArray(type_input=np.ndarray)
#     arr = np.array([[1, 2], [3, 4]])
#     sa.append(arr)
#
#     assert len(sa) == 1
#     assert isinstance(sa[0], np.ndarray)
#     assert sa[0].shape == (2, 2)
#     assert np.array_equal(sa[0], arr)
#
# def test_structarray_type_conversion():
#     sa = StructArray(type_input=np.float64)
#
#     # These should raise TypeError
#     sa.append(np.int64(1))
#     sa.append(np.float32(1.0))
#     sa.append(1.0)
#     assert len(sa) == 3
#
# def test_structarray_mixed_numeric_arrays():
#     # Test with tuple of allowed types
#     allowed_types = (np.int64, np.float64, np.complex128)
#     with pytest.raises(TypeError):
#         sa = StructArray(type_input=allowed_types)
#
#
# def test_structarray_large_values():
#     sa = StructArray(type_input=np.float64)
#
#     # Test very large and very small values
#     large_val = np.float64(1e308)
#     small_val = np.float64(1e-308)
#     sa.append(large_val)
#     sa.append(small_val)
#
#     assert np.isclose(sa[0], large_val)
#     assert np.isclose(sa[1], small_val)
#
# def test_structarray_numpy_complex128():
#     sa = StructArray(type_input=int)
#     values = [
#         np.complex128(1 + 2j),
#         np.float64(1.2),
#     ]
#     with pytest.raises(TypeError):
#         for val in values:
#             sa.append(val)
#
#     assert len(sa) == 0
#



def test_idsversion_initialization():
    # Test default initialization
    version = IdsVersion()
    assert version.idspy_version == _IDSPY_VERSION
    assert version.imas_dd_git_commit == _IDSPY_IMAS_DD_GIT_COMMIT
    assert version.imas_dd_version == _IDSPY_IMAS_DD_VERSION
    assert version.idspy_internal_version == _IDSPY_INTERNAL_VERSION


def test_idsversion_immutability():
    version = IdsVersion()
    # Test that the dataclass is frozen (immutable)
    with pytest.raises(AttributeError):
        version.idspy_version = "1.0.0"


def test_idsversion_equality():
    version1 = IdsVersion()
    version2 = IdsVersion()

    # Test equality with another IdsVersion instance
    assert version1 == version2

    # Test equality with string
    assert version1 == _IDSPY_VERSION

    # Test inequality
    assert not (version1 == "999999.999.999")

    # Test equality with invalid type
    assert version1.__eq__(42) is NotImplemented


@pytest.mark.parametrize("version_str,expected", [
    ("0.0.1", False),  # older version
    (_IDSPY_VERSION, False),  # same version
    ("999999.999.999", True),  # newer version
])
def test_idsversion_less_than(version_str, expected):
    version = IdsVersion()
    assert (version < version_str) == expected

    # Test with invalid type
    assert version.__lt__(42) is NotImplemented


@pytest.mark.parametrize("version_str,expected", [
    ("0.0.1", True),  # older version
    (_IDSPY_VERSION, False),  # same version
    ("999999.999.999", False),  # newer version
])
def test_idsversion_greater_than(version_str, expected):
    version = IdsVersion()
    assert (version > version_str) == expected

    # Test with invalid type
    assert version.__gt__(42) is NotImplemented


def test_idsversion_comparison_between_instances():
    base_version = IdsVersion()

    # Create a test instance with a different version
    test_versions = {
        "older": "0.0.1",
        "same": _IDSPY_VERSION,
        "newer": "999999.999.999"
    }

    for version_type, version_str in test_versions.items():
        test_version = IdsVersion()
        # We can't modify the version directly due to frozen=True,
        # so we'll use object.__setattr__ for testing purposes
        object.__setattr__(test_version, 'idspy_version', version_str)

        if version_type == "older":
            assert base_version > test_version
            assert not base_version < test_version
        elif version_type == "same":
            assert base_version == test_version
            assert not base_version < test_version
            assert not base_version > test_version
        else:  # newer
            assert base_version < test_version
            assert not base_version > test_version


def test_idsversion_string_representation():
    version = IdsVersion()
    repr_str = repr(version)

    # Check that all attributes are present in the string representation
    assert "idspy_version" in repr_str
    assert "imas_dd_git_commit" in repr_str
    assert "imas_dd_version" in repr_str
    assert "idspy_internal_version" in repr_str

    # Check that all values are present
    assert _IDSPY_VERSION in repr_str
    assert _IDSPY_IMAS_DD_GIT_COMMIT in repr_str
    assert _IDSPY_IMAS_DD_VERSION in repr_str
    assert _IDSPY_INTERNAL_VERSION in repr_str


@pytest.mark.parametrize("invalid_version", [
    None,
    123,
    [],
    {},
    True
])
def test_idsversion_invalid_comparisons(invalid_version):
    version = IdsVersion()
    assert version.__eq__(invalid_version) is NotImplemented
    assert version.__lt__(invalid_version) is NotImplemented
    assert version.__gt__(invalid_version) is NotImplemented
