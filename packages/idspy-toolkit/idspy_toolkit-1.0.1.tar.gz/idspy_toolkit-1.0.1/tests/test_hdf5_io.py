import pytest
import h5py
from tests.classes_skels import *
from idspy_toolkit.converter import ids_to_hdf5, hdf5_to_ids
from random import randrange
from typing import Union
from idspy_dictionaries import ids_gyrokinetics_local as gkids
from idspy_dictionaries.dataclasses_idsschema import StructArray
import idspy_toolkit
import numpy as np

from idspy_toolkit.exceptions import IdsVersionError


@pytest.fixture(scope="function")
def hdf5_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / "class_ids_{0:04d}.h5".format(randrange(0, 9999))
    return fn

def test_write_empty_version(hdf5_file):
    ids = gkids.Eigenmode()

    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.version = ""
    with pytest.raises(IdsVersionError):
        ids_to_hdf5(ids, hdf5_file)


def test_write_none_version(hdf5_file):
    ids = gkids.Eigenmode()

    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.version = None
    with pytest.raises(IdsVersionError):
        ids_to_hdf5(ids, hdf5_file)


def test_wavevector_write(hdf5_file):
    ids = gkids.Wavevector()
    ids.radial_wavevector_norm = 2
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    with pytest.raises(TypeError):
        ids.eigenmode.append(gkids.Wavevector())
    ids.eigenmode.append(gkids.Eigenmode())
    ids.eigenmode[-1].poloidal_turns = 2
    assert len(ids.eigenmode) == 1
    assert ids_to_hdf5(ids, hdf5_file) == (2, 2)
    ids_read = gkids.Wavevector()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert len(ids_read.eigenmode) == 1, "no eigenmode found"
    assert ids_read.eigenmode[0].poloidal_turns == ids.eigenmode[-1].poloidal_turns
    assert isinstance(ids_read.eigenmode, StructArray)

def test_wavevector_write_only_eigenmode(hdf5_file):
    ids = gkids.Wavevector()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.eigenmode.append(gkids.Eigenmode())
    ids.eigenmode[-1].poloidal_turns = 2
    #assert ids_to_hdf5(ids, hdf5_file) == (2, 2)
    ids_to_hdf5(ids, hdf5_file)
    ids_read = gkids.Wavevector()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert len(ids_read.eigenmode) == 1
    assert isinstance(ids_read.eigenmode, StructArray)

def test_eigenmode_write(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = '{"a":2}'
    ids.code.output_flag = 2
    assert ids_to_hdf5(ids, hdf5_file) == (2, 2)
    ids_read = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert ids_read.code.parameters == ids.code.parameters
    assert ids_read.code.output_flag == ids.code.output_flag


def test_eigenmode_overwrite(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = '{"a":2}'
    ids.code.output_flag = 2
    assert ids_to_hdf5(ids, hdf5_file, overwrite=True) == (2, 2)
    ids_read = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert ids_read.code.parameters == ids.code.parameters
    assert ids_read.code.output_flag == ids.code.output_flag
    ids.code.output_flag = 42
    ids.code.parameters = '{"a":3}'
    assert ids_to_hdf5(ids, hdf5_file, overwrite=True) == (2, 2)
    ids_read = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert ids_read.code.parameters == ids.code.parameters
    assert ids_read.code.output_flag == ids.code.output_flag


def test_eigenmode_write_wrong_type(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = '{"a":2}'
    ids.code.output_flag = 2
    assert ids_to_hdf5(ids, hdf5_file) == (2, 2)
    ids_read = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert ids_read.code.parameters == ids.code.parameters
    np.testing.assert_array_equal(ids_read.code.output_flag, ids.code.output_flag)


def test_class_dict_conversion(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = '{"a":2}'
    ids.code.output_flag = 2
    assert ids_to_hdf5(ids, hdf5_file) == (2, 2)
    ids_read = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=True)
    assert isinstance(ids_read.code.parameters, dict) is True
    assert ids_read.code.parameters == {"a": 2}
    np.testing.assert_array_equal(ids_read.code.output_flag, ids.code.output_flag)


def test_class_dict_no_conversion(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = {"a": 2}
    ids.code.output_flag = 2
    assert ids_to_hdf5(ids, hdf5_file) == (2, 2)
    ids_read = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert isinstance(ids_read.code.parameters, dict) is False
    assert isinstance(ids_read.code.parameters, str) is True
    assert ids_read.code.parameters == '<root><a type="int">2</a></root>'


def test_class_dict_conversion_in_list(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = {"a": 2, "b": {"c": 4}}
    ids.code.output_flag = 2

    ids_wavevector = gkids.Wavevector()
    ids_wavevector.radial_wavevector_norm = 4.
    ids_wavevector.binormal_wavevector_norm = 2.
    ids_wavevector.eigenmode.append(ids)
    assert ids_to_hdf5(ids_wavevector, hdf5_file) == (3, 4)
    ids_read = gkids.Wavevector()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=True)
    assert isinstance(ids_read.eigenmode[0].code.parameters, dict) is True
    assert ids_read.eigenmode[0].code.parameters.get("a") == 2
    assert ids_read.eigenmode[0].code.parameters.get("b").get("c") == 4


def test_class_dict_no_conversion_in_list(hdf5_file):
    ids = gkids.Eigenmode()
    idspy_toolkit.fill_default_values_ids(new_ids=ids)
    ids.code.parameters = {"a": 2, "b": {"c": 4}}
    ids.code.output_flag = 2

    ids_wavevector = gkids.Wavevector()
    ids_wavevector.radial_wavevector_norm = 4.
    ids_wavevector.binormal_wavevector_norm = 2.
    ids_wavevector.eigenmode.append(ids)
    assert ids_to_hdf5(ids_wavevector, hdf5_file) == (3, 4)
    ids_read = gkids.Wavevector()
    idspy_toolkit.fill_default_values_ids(new_ids=ids_read)
    hdf5_to_ids(hdf5_file, ids_read, todict=False)
    assert isinstance(ids_read.eigenmode[0].code.parameters, dict) is False
    assert isinstance(ids_read.eigenmode[0].code.parameters, str) is True
    assert ids_read.eigenmode[
               0].code.parameters == '<root><a type="int">2</a><b type="dict"><c type="int">4</c></b></root>'


def test_class_dict_format(hdf5_file):
    test = ClassListMixDict()
    assert ids_to_hdf5(test, hdf5_file) == (1, 4)
    ids_read = ClassListMixDict([], -999, "", {})
    hdf5_to_ids(hdf5_file, ids_read, todict=True)
    #   print("output", ids_read)
    assert test.space == ids_read.space
    assert test.name == ids_read.name
    assert all([a == b for a, b in zip(sorted(test.time), sorted(ids_read.time))])


def test_empty_array(hdf5_file):
    test = ArrayClass()
    assert ids_to_hdf5(test, hdf5_file) == (1, 2)
    ids_read = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read, fill=True, todict=True)
    assert ids_read.val_0d == 999.999
    assert isinstance(ids_read.val_array_1d, np.ndarray) is True
    assert hasattr(ids_read, "val_array_1d") is True
    assert ids_read.val_array_1d.shape == (0,)
    with h5py.File(hdf5_file, "r") as f:
        assert tuple(f.keys()) == ('ArrayClass', 'metadata')
        assert f['ArrayClass'].get('val_array_1d') is None

def test_array_size_constraints(hdf5_file):
    # Create test data with arrays of different sizes and dimensions
    ids = ArrayClass()
    ids.val_array_1d = np.arange(1000)  # 1D array with 1000 elements
    ids.val_array_2d = np.ones((100, 100))  # 2D array with 10000 elements
    ids.val_array_3d = np.ones((10, 10, 10))  # 3D array with 1000 elements
    
    # Test max_array_dim constraint
    ids_to_hdf5(ids, hdf5_file, overwrite=True, max_array_dim=2)
    ids_read = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read, fill=True)
    
    # 3D array should be skipped, others should be present
    assert hasattr(ids_read, "val_array_1d")
    assert hasattr(ids_read, "val_array_2d")
    assert ids_read.val_array_3d.size == 0  # Should be empty array
    
    # Test max_array_elements constraint
    ids_to_hdf5(ids, hdf5_file, overwrite=True, max_array_elements=5000)
    ids_read = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read, fill=True)
    
    # 2D array (10000 elements) should be skipped
    assert hasattr(ids_read, "val_array_1d")
    assert ids_read.val_array_2d.size == 0  # Should be empty
    assert hasattr(ids_read, "val_array_3d")

def test_array_size_mb_constraint(hdf5_file):
    # Create test data with large arrays
    ids = ArrayClass()
    # Create array of approximately 10MB (float64 = 8 bytes)
    ids.val_array_1d = np.ones(1250000, dtype=np.float64)  # ~10MB
    # Create array of approximately 2MB
    ids.val_array_2d = np.ones((500, 500), dtype=np.float64)  # ~2MB
    
    # Test max_array_size constraint (5MB)
    ids_to_hdf5(ids, hdf5_file, overwrite=True, max_array_size=5)
    ids_read = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read, fill=True)
    
    # Large array should be skipped, smaller one should be present
    assert ids_read.val_array_1d.size == 0  # Should be empty
    assert hasattr(ids_read, "val_array_2d")
    np.testing.assert_array_equal(ids_read.val_array_2d, ids.val_array_2d)

def test_combined_array_constraints(hdf5_file):
    ids = ArrayClass()
    # Create various test arrays
    ids.val_array_1d = np.ones(1000)  # Small 1D array
    ids.val_array_2d = np.ones((100, 100))  # Medium 2D array
    ids.val_array_3d = np.ones((50, 50, 50))  # Large 3D array
    
    # Test combined constraints
    ids_to_hdf5(ids, hdf5_file, overwrite=True,
                max_array_dim=2,
                max_array_size=1,  # 1MB
                max_array_elements=5000)
    
    ids_read = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read,
                fill=True,
                max_array_dim=2,
                max_array_size=1,
                max_array_elements=5000)
    
    # Only val_array_1d should be present (others exceed constraints)
    assert hasattr(ids_read, "val_array_1d")
    np.testing.assert_array_equal(ids_read.val_array_1d, ids.val_array_1d)
    assert ids_read.val_array_2d.size == 0
    assert ids_read.val_array_3d.size == 0

def test_array_constraints_loading(hdf5_file):
    # First save without constraints
    ids = ArrayClass()
    ids.val_array_1d = np.ones(1000)
    ids.val_array_2d = np.ones((100, 100))
    ids.val_array_3d = np.ones((10, 10, 10))
    
    ids_to_hdf5(ids, hdf5_file, overwrite=True)
    
    # Test loading with different constraints
    ids_read1 = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read1, max_array_dim=1)
    assert hasattr(ids_read1, "val_array_1d")
    assert ids_read1.val_array_2d.size == 0
    assert ids_read1.val_array_3d.size == 0
    
    ids_read2 = ArrayClass()
    hdf5_to_ids(hdf5_file, ids_read2, max_array_elements=500)
    assert hasattr(ids_read2, "val_array_1d")
    assert ids_read2.val_array_2d.size == 0
    assert hasattr(ids_read2, "val_array_3d")


