"""

"""
from __future__ import annotations

import dataclasses
from typing import Any, Union, Tuple, TypeVar, Type
from typing_extensions import Protocol
from os import rename as os_rename
import os
import h5py
import numpy as np
import simplejson as js
from warnings import warn
from packaging.version import Version, parse, InvalidVersion

from idspy_toolkit.snippets import is_dataclass_instance, is_dataclass_field, sort_h5_keys, format_ids_substring
from idspy_toolkit.constants import IMAS_DEFAULT_INT, IMAS_DEFAULT_FLOAT, IMAS_DEFAULT_CPLX, IMAS_DEFAULT_STR
from idspy_toolkit.accessor import set_ids_value_from_string, _is_0d_array
from idspy_toolkit.toolkit import fill_default_values_ids, is_default_imas_value
from idspy_toolkit.simplexml import dict_to_xml
from idspy_toolkit.exceptions import IdsVersionError

from ._version import get_version


class DataClass(Protocol):
    __dataclass_fields__: dict[str, Any]

_MB_FACTOR = 1024*1024
DC = TypeVar("DC", bound=DataClass)
DEFAULT_VALUES_LIST = (IMAS_DEFAULT_INT, IMAS_DEFAULT_FLOAT,
                       IMAS_DEFAULT_CPLX, IMAS_DEFAULT_STR, None, list(), tuple([]))


def _create_hdf5_dataset(value_name: str, value: Any, parent_group,
                         max_array_dim: int | None = None,
                         max_array_size: int | None = None,
                         max_array_elements: int | None = None
                         ) -> int:
    """
        create the dataset and write the associated value
        dict are serialized as xml
    :param value_name:
    :param value:
    :param parent_group:
    :return: number of created dataset
             - ValueError in case where value is a list with more than one type of elements
             - None if the numpy.array doesn't match any of the element, size, dims criteria
    """
    if value is None:
        raise ValueError("cannot write None value in hdf5 file")

    if isinstance(value, np.ndarray):
        if value.ndim == 0:
            value = float(value)
        else:
            if max_array_elements is not None:
                if value.size>max_array_elements:
                    return 0
            if max_array_dim is not None:
                if value.ndim>max_array_dim:
                    return 0
            if max_array_size is not None:
                if value.size*value.itemsize > max_array_size*_MB_FACTOR:
                    return 0

    str_type = h5py.special_dtype(vlen=str)
    parent_group.attrs["len"] = 1
    parent_group.attrs["type"] = "item"
    created_dataset = 1
    if isinstance(value, str):
        parent_group.create_dataset(value_name,
                                    data=value.encode("utf8"),
                                    dtype=str_type)
    elif isinstance(value, dict):
        value_as_str = dict_to_xml(value)
        parent_group.create_dataset(value_name,
                                    data=value_as_str.encode("utf8"),
                                    dtype=str_type)
    elif isinstance(value, (list, tuple)):
        same_type = all(isinstance(sub, type(value[0])) for sub in value[1:])
        if same_type is False:
            del parent_group.attrs["len"]
            del parent_group.attrs["type"]
            raise ValueError(f"different types for value {value}")
        value_ref = value[0]
        if is_dataclass_instance(value_ref):
            del parent_group.attrs["len"]
            del parent_group.attrs["type"]
            raise ValueError(f"cannot write a dataclass as a dataset {value}")
        parent_group.attrs["len"] = len(value)
        parent_group.attrs["type"] = "list"

        if isinstance(value_ref, dict):
            created_dataset = len(value)
            for i, val in enumerate(value):
                value_as_str = dict_to_xml(val)
                parent_group.create_dataset(value_name + f"_{i}", data=value_as_str,
                                            dtype=str_type)
        elif isinstance(value_ref, (list, tuple)):
            inner_val = np.asarray(value)
            created_dataset = 1
            parent_group.create_dataset(value_name, data=inner_val, chunks=True, compression="gzip", )
        else:
            created_dataset = 1
            try:
                parent_group.create_dataset(value_name, data=value, chunks=True, compression="gzip", )
            except TypeError:
                print(f"error raised for {value_name}:{value}/{type(value)}")
                raise
    else:
        try:
            if not isinstance(value, np.ndarray):
                parent_group.create_dataset(value_name, data=value, shape=())
            else:
                parent_group.create_dataset(value_name, data=value)
        except TypeError:
            print("TypeError for ", parent_group, value_name, value)
            raise
    return created_dataset


def get_inner_type_list(item: Union[list, tuple]) -> Union[Any, None]:
    test_var = item

    while isinstance(test_var, (list, tuple)):
        try:
            test_var = test_var[0]
        except IndexError:
            return None

    return test_var


def _is_list_empty(item: Any) -> bool:
    """
    Check if the given item is an empty list, tuple, or numpy array.

    :param item: The item to be checked.
    :type item: Any

    :return: True if the item is an empty list, tuple, or numpy array, False otherwise.
    :rtype: bool
    """
    if isinstance(item, (list, tuple)):
        if len(item) == 0:
            return True
    elif isinstance(item, np.ndarray):
        if item.ndim == 0:
            return False
        else:
            if len(item) == 0:
                return True
    return False


def _is_item_list(item: Any) -> bool:
    """
    Check if the given item is a list, tuple, or numpy array.

    :param item: The item to be checked.
    :type item: Any

    :return: True if the item is a list, tuple, or numpy array, False otherwise.
    :rtype: bool
    """
    if isinstance(item, (list, tuple)):
        return True
    elif isinstance(item, np.ndarray):
        if item.ndim == 0:
            return False
        else:
            return True
    return False



def ids_to_hdf5(ids: Type[DC], filename: str, overwrite: bool = False,
                max_array_dim: int | None = None,
                max_array_size: int | None = None,
                max_array_elements: int | None = None
                ) -> Tuple[int, int]:
    """
    store an IDS class to a HDF5 file
    dict are stored as serialized json
    List of dict are serialized as a sequence of dataset
    List of values (int/float) as multidimensional dataset
    :param ids: IDS to store
    :param filename: name of the HDF5 file
    :param overwrite: what to do if file already exists?
    :param max_array_dim: max number of dimension for an array to write, otherwise data will be ignore, default is None
    :param max_array_size: max size (in MB) for an array to write, otherwise data will be ignore, default is None
    :param max_array_elements: max number of elements for an array to write, otherwise data will be ignore, default is None

    :return: IOError if HDF5 file already exist and overwrite is False, number of written groups and keys otherwise

    :TODO: manage empty files and empty group/dataclass
    :TODO: store strings as bytes
    """
    total_group: int = 0
    total_dataset: int = 0

    def _hdf5_header_metadata(h5file, ids):
        """
        write all main metadata to HDF5 root path
        ids script version
        dd version
        structure

        """
        g = h5file.create_group("metadata")
        g.attrs["toolkit_version"] = get_version()
        if getattr(ids, "version", None):
            ids_version = ids.version.idspy_version
            dd_version = ids.version.imas_dd_version
            dd_git_version = ids.version.imas_dd_git_commit

        else:
            ids_version = dd_version = dd_git_version = ""
            raise IdsVersionError(f"Current IDS has no version attribute")
        if "-" in dd_version:
            dd_version = dd_version.split("-")[0]
            dd_version = [int(x) for x in dd_version.split(".")]
            dd_version[-1] += 1
            dd_version = ".".join([str(x) for x in dd_version])
            print(f"has to update ddversion to {dd_version} from a dev one")
        if not ids_version:
            raise IdsVersionError("Output to HDF5 file without specifying idspy version will be removed"
                 " in version>=1.0.0 and an exception will be raised")
        if not dd_version:
            raise IdsVersionError("Output to HDF5 file without specifying data dictionary version will be removed"
                 " in version=1.0.0 and an exception will be raised")
        else:
            if Version(dd_version) < Version("4.0.0"):
                raise IdsVersionError("Data dictionary v4.0 is now mandatory", )

        g.attrs["ids_version"] = ids_version
        g.attrs["imas_dd_version"] = dd_version
        g.attrs["imas_dd_git_commit"] = dd_git_version

    def __check_all_fields_none(current_ids, default_vals_list):
        if "get_members_name" not in current_ids.__dir__():
            raise AttributeError("IDSPY dictionaries used does not follow current conventions")
        default_values_scalar = [x for x in default_vals_list if not isinstance(x, (tuple, list, np.ndarray))]

        number_fields = len(list(current_ids.get_members_name()))
        list_default: list[Union[None, Any]] = []

        for field_name in current_ids.get_members_name():
            field_value = getattr(current_ids, field_name)
            if isinstance(field_value, (list, tuple)):
                if len(field_value) == 0:
                    list_default.append(None)
            elif isinstance(field_value, np.ndarray):
                if field_value.size == 0:
                    list_default.append(None)
                elif field_value.ndim == 0:
                    if field_value[()].size==0:
                        list_default.append(None)
                    else:
                        if field_value[()] in default_values_scalar:
                            list_default.append(None)
                        # for vals in default_values_scalar:
                        #     if field_value[()] == vals:
                        #         list_default.append(None)
                        #         break
            elif field_value in default_values_scalar:
                 list_default.append(None)
        return len(list_default) == number_fields

    def _browse_ids(current_ids, parent_group, ids_group: int, ids_dataset: int,
                    named_group: Union[str, None] = None,
                    flat_idx: Union[int, None] = None) -> tuple[int, int]:
        if named_group is None:
            root_grp = str(type(current_ids)).split(".")[-1][:-2]
        else:
            root_grp = named_group

        if flat_idx is not None:
            root_grp = "{0}{1}".format(root_grp, format_ids_substring(flat_idx))

        all_none = __check_all_fields_none(current_ids, DEFAULT_VALUES_LIST)
        if all_none is True:
            return ids_group, ids_dataset

        current_grp = parent_group.create_group(root_grp)
        ids_group += 1

        for field in dataclasses.fields(current_ids):
            if (field_name := field.name) in ("version", "max_repr_length",):
                continue

            field_value = getattr(current_ids, field_name)
            if not dataclasses.is_dataclass(field_value):
                if not isinstance(field_value, dict):
                    if is_default_imas_value(current_ids, field_name) is True:
                        continue
                    # None not being part of the IMAS default values, a separated test is needed
                    elif field_value is None:
                        continue

            if isinstance(field_value, (list, tuple)):
                if is_dataclass_instance(field_value[0]):
                    for i, sub_ids in enumerate(field_value):
                        ids_group, ids_dataset = _browse_ids(sub_ids, current_grp,
                                                             ids_group, ids_dataset,
                                                             named_group=field_name,
                                                             flat_idx=i)
                else:
                    ids_dataset += _create_hdf5_dataset(field_name, field_value,
                                                        current_grp, max_array_dim,
                                                        max_array_size, max_array_elements)
            elif is_dataclass_instance(field_value):
                # call recursive function
                ids_group, ids_dataset = _browse_ids(field_value, current_grp,
                                                     ids_group, ids_dataset,
                                                     named_group=field_name)
            else:
                ids_dataset += _create_hdf5_dataset(field_name, field_value,
                                                        current_grp, max_array_dim,
                                                    max_array_size, max_array_elements)
        return ids_group, ids_dataset

    if overwrite is False:
        tmp_file = filename
        if os.path.exists(filename):
            raise IOError(f"HDF5 file {filename} already exist")
    else:
        tmp_file = str(filename) + ".tmp"
    # open the hdf5 file
    with h5py.File(tmp_file, "w") as h5f:
        _hdf5_header_metadata(h5f, ids)
        total_group, total_dataset = _browse_ids(ids, h5f, total_group, total_dataset)
    if overwrite is True:
        if os.path.exists(filename):
            os.remove(filename)
        os_rename(tmp_file, filename)
    return total_group, total_dataset


def _iterate_hdf5_dataset(name: str, hdf5obj: Any, h5struct: list) -> None:
    if isinstance(hdf5obj, h5py.Dataset):
        h5struct.append(r"/" + name)
    return None


def hdf5_to_ids(filename: str, ids: Type[DC], todict: bool = True,
                fill: bool = True,
                max_array_dim:int|None=None,
                max_array_size:int|None=None,
                max_array_elements:int|None=None) -> Type[DC]:
    """
    read an IDS from an HDF5 file and return it
    :param filename: hdf5 filename
    :param ids: ids dataclass, has to be a fully develop IDS
    :param todict: convert xml string to dict, default=True
    :param fill: automatically fill with default values of nested ids values if not in the file
    :param max_array_dim: max number of dimension for an array to load, otherwise data will be ignore, default is None
    :param max_array_size: max size (in MB) for an array to load, otherwise data will be ignore, default is None
    :param max_array_elements: max number of elements for an array to load, otherwise data will be ignore, default is None
    :return: IDS dataclass
    """
    if not os.path.exists(filename):
        raise IOError(f"HDF5 file {filename} not found")

    if ids is None:
        raise AttributeError("ids parameter cannot be None or empty")

    if fill is True:
        fill_default_values_ids(ids)

    h5struct_ds: list = []
    # open the hdf5 file and read it recursively
    with h5py.File(filename, "r") as h5f:
        if (metadata := h5f.get('metadata', None)) is not None:
            if Version(metadata.attrs.get('toolkit_version', '0.0.0')) <Version('0.8.1'):
                raise IdsVersionError(f"current package version is : {Version(metadata.attrs.get('toolkit_version', '0.0.0'))}"
                     f" and it is now deprecated, please update to version 1.0.0 or higher.")

        else:
            raise IdsVersionError("metadata will be mandatory with idspy_toolkit>=1.0.0")
        h5f.visititems(lambda x, y: _iterate_hdf5_dataset(x, y, h5struct_ds))
        if len(h5struct_ds) == 0:
            raise ValueError(f"file [{filename}] seems to be empty or corrupted")
        h5struct_ds = sort_h5_keys(h5struct_ds)

        for keys in h5struct_ds:
            if isinstance(h5f[keys][()], np.ndarray):
                if max_array_dim:
                    if h5f[keys][()].ndim > max_array_dim:
                        continue

                if max_array_elements:
                    if h5f[keys][()].size > max_array_elements:
                        continue

                if max_array_size:
                    if h5f[keys][()].size*h5f[keys][()].itemsize > max_array_size*_MB_FACTOR:
                        continue
            set_ids_value_from_string(ids, keys, h5f[keys][()], todict=todict, create_missing=fill)
    return ids
