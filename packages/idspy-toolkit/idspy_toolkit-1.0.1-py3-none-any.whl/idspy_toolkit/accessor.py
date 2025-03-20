from __future__ import annotations

import dataclasses
from dataclasses import Field
from typing import get_type_hints, Any, get_origin, TypeVar, Type, Union

import numpy as np
from typing_extensions import Protocol
import inspect
from numpy import ndarray, array
import simplejson as js

from idspy_toolkit.snippets import _IDS_LIST_DELIMITER
from idspy_toolkit.simplexml import xml_to_dict
from idspy_toolkit.utils import camel2snake, extract_ndarray_info, _imas_default_values, _check_simplified_types
from idspy_toolkit.constants import IMAS_TO_PYTHON_TYPES

class DataClass(Protocol):
    __dataclass_fields__: dict[str, Any]


DC = TypeVar("DC", bound=DataClass)


def _is_0d_array(item: Any) -> bool:
    """
    Check if the given item is a OD numpy array (aka nightmare).

    :param item: The item to be checked.
    :type item: Any

    :return: True if the item is a 0D numpy array, False otherwise.
    :rtype: bool
    """
    if isinstance(item, ndarray):
        if item.ndim == 0:
            return True
    return False


def _convert_bytes_to_str(entry: list | tuple | ndarray) -> ndarray:
    output = []
    for items in entry:
        # items if it's not a list, is assumed to be a string
        # so checking if current items has a decode attribute
        # let's determine if current items is a list or a
        # list element
        if hasattr(items, "decode"):
            output.append(items.decode("utf8"))
        else:
            output.append(_convert_bytes_to_str(items))
    return array(output)


def is_list_member(cls_instance: Any, field_name: str) -> bool:
    """Check if a dataclass field is list-like based on its metadata.

    Args:
        cls_instance: Instance of a dataclass
        field_name: Name of the field to check

    Returns:
        bool: True if the field has ndims in metadata and 
        field_type is not np.ndarray, False otherwise
    """
    field_def = None
    for f in dataclasses.fields(cls_instance):
        if field_name == f.name:
            field_def = f
    if field_def is None:
        return is_list_member_guess(cls_instance, field_name)


    metadata = getattr(field_def, "metadata", {})
    if metadata.get("field_type") == np.ndarray:
        return False
    else:
        if metadata.get("field_type") is None:
            return is_list_member_guess(cls_instance, field_name)
        else:
            if "ndims" in metadata:
                return True
            else:
                return False


def is_list_member_guess(classname: Any, fieldname: str) -> bool:
    """
    Checks if a field_clazz in a dataclass is a list.

    :param classname: The  dataclass.
    :type classname: dataclass
    :param fieldname: The name of the field_clazz to check.
    :type fieldname: str
    :return: True if the field_clazz is a list, False otherwise.
    :rtype: bool
    """

    # Get the dataclass field_clazz object
    field = classname.__dataclass_fields__[fieldname]

    # Get the type of the field_clazz
    field_type = get_type_hints(classname)[field.name]

    # If the field_clazz type is a list or a new-style list, return True
    if isinstance(field_type, list) or field_type == list:
        return True

    # If the field_clazz type is a generic type that inherits from list or new-style list, return True
    if inspect.isclass(field_type) and (issubclass(field_type, list) or field_type == list):
        return True

    # If the field_clazz type is a type variable with a bound that inherits from list or new-style list, return True
    origin = get_origin(field_type)
    if origin is not None and inspect.isclass(origin) and (issubclass(origin, list) or origin == list):
        return True

    # Otherwise, return False
    return False


def get_type_arg(clazz: Type[DC], field_clazz: Union[str, Field[Any]]) -> Any:
    """
    Get the type argument of a dataclass field.

    :param clazz: The dataclass to get the field from.
    :param field_clazz: The name of the field to get the type argument from.
    :return: A tuple containing the type argument of the field and a boolean value indicating if the field is a list.
    :raises AttributeError: If the specified field is not found in the dataclass.
    :raises KeyError: If the specified field is not found in the current ids version.
    Examples:
        >>> @dataclass
        ... class Foo:
        ...     bar: list[int]
        ...
        >>> get_type_arg(Foo, 'bar')
        (int, True)
    """
    # had to use a try/except due to handle some forwardref cases in dataclasses
    is_list = False
    if getattr(field_clazz, "name", None) is None:
        field_is_string = True
    else:
        field_is_string = False

    if field_is_string is False:
        try:
            item = get_type_hints(clazz)[field_clazz.name]
            is_list = is_list_member(clazz, field_clazz.name)
        except NameError:
            item = get_type_hints(type(clazz))[field_clazz.name]
            is_list = is_list_member(type(clazz), field_clazz.name)
        except KeyError:
            raise KeyError(f"no matching entry in current ids version for entry {field_clazz}")
    else:
        try:
            item = get_type_hints(clazz)[field_clazz]
            is_list = is_list_member(clazz, field_clazz)
        except (AttributeError, KeyError, NameError):
            raise KeyError(f"no matching entry in current ids version for entry {field_clazz}")
    
    if "ndarray" in str(item):
        data_type = str(item)
    else:
        data_type = getattr(item, "__args__", (item,))[0]

    return data_type, is_list


def __split_path(path: str, root_type_str: str) -> list:
    path_members = [x for x in path.strip().split(r"/") if x]
    if path[0] == r"/":
        if path_members[0] not in root_type_str:
            raise AttributeError(
                f"given path [{path_members[0]}] does not correspond to current ids type {root_type_str}")
        path_members = path_members[1:]
    return path_members


def get_ids_value_from_string(ids: Type[DC], path: str) -> Any:
    """
    Get the value of a field_clazz within a nested dataclass object by specifying the path to it as a string.

    :param ids: The dataclass object to get the field_clazz value from.
    :param path: The path to the field_clazz within the dataclass object.
    :return: The value of the specified field_clazz.
    :raises AttributeError: If the specified path does not correspond to the type of the given dataclass object.
    :raises ValueError: If the specified path contains a non-existent field_clazz or if a list field_clazz is accessed with an out-of-range index.
    :raises TypeError: If the specified path contains a list field_clazz but the next part of the path is not an index.
    :raises KeyError: If the specified path corresponds to an IDS root and not an IDS member.

    Examples:
        >>> @dataclass
        ... class Foo:
        ...     bar: int = 0
        ...
        >>> foo = Foo()
        >>> foo.bar = 42
        >>> get_ids_value_from_string(foo, 'bar')
        42

        >>> @dataclass
        ... class Foo:
        ...     bar: List[str] = []
        ...
        >>> foo = Foo()
        >>> foo.bar = ['hello', 'world']
        >>> get_ids_value_from_string(foo, 'bar#0')
        'hello'
    """
    try:
        path_members = __split_path(path, str(type(ids)))
        current_attr = ids
    except IndexError:
        raise KeyError("get_ids_value_from_string does not allow to get a full IDS, just IDS members")

    for idx, subpath in enumerate(path_members):
        if _IDS_LIST_DELIMITER in subpath:
            name, offset = subpath.strip().split("#")
            offset = int(offset)
            name = camel2snake(name)
            # TODO: check that return value of getattr is a list as expected
            list_attr = getattr(current_attr, name, None)
            len_list_attr = len(list_attr)

            if name is None:
                raise ValueError(f"missing element {subpath}")
            if not isinstance(list_attr, (list, tuple)):
                raise AttributeError(f"element {name} is not a list")
            if len_list_attr < offset and offset > 0:
                raise IndexError(f"element {name} has a len of {len_list_attr} and cannot reach elem #{offset}")
            if len_list_attr == 0:
                raise ValueError(f"element {name} is empty")
            elif len_list_attr <= offset:
                raise IndexError(f"cannot access element {offset + 1}/{len_list_attr} for {name}")
            return get_ids_value_from_string(list_attr[offset], "/".join(path_members[idx + 1:]))
        else:
            if isinstance(current_attr, (list, tuple)):
                raise ValueError(f"attribute [{path_members[idx - 1]}] is a list")
            try:
                current_attr = getattr(current_attr, subpath)
            except AttributeError:
                raise AttributeError(f"no member named {subpath} in {type(current_attr)}")
    if isinstance(current_attr, bytes):
        return current_attr.decode("utf8")
    return current_attr



def create_instance_from_type(var_type: Any) -> Any:
    """
    Create a variable instance from the given type.

    :param var_type: A type to create a variable from.
    :type var_type: Any
    :return: A variable created from the given type.
    :rtype: Any
    :raises TypeError: If the input type is not a dataclass or a supported built-in type.
    :raises TypeError: If the input type is a dataclass that has a field_clazz with an unsupported type.
    """

    if dataclasses.is_dataclass(var_type):
        dict_args = {}
        for f in dataclasses.fields(var_type):
            arg_type, is_list = get_type_arg(var_type, f.name)
            if is_list is True:
                try:
                    created_element = var_type.__dataclass_fields__[f.name].default_factory()
                except TypeError:
                    created_element = list()
                dict_args.update({f.name: created_element})
            else:
                if "ndarray" in str(arg_type):
                    if not getattr(f, "metadata", None):
                        shape, dtype = extract_ndarray_info(str(arg_type))
                    else:
                        shape = (0,)*f.metadata["ndims"]
                        dtype = IMAS_TO_PYTHON_TYPES.get(f.metadata["imas_type"].strip().split("_")[0], None)
                    dict_args.update({f.name: ndarray(shape=shape, dtype=dtype)})
                else:
                    dict_args.update({f.name: arg_type()})
        return var_type(**dict_args)
    else:
        return _imas_default_values(var_type)


def set_ids_value_from_string(ids: Type[DC], path: str, value: Any, create_missing: bool = True, todict: bool = True):
    """
    Sets the value of an attribute in a nested dataclass given its path.

    :param ids: the nested dataclass instance to modify
    :type ids: dataclasses.dataclass

    :param path: the path of the attribute to modify
    :type path: str

    :param value: the new value to set for the attribute
    :type value: any

    :param create_missing: whether to create missing attributes or not, defaults to False
    :type create_missing: bool

    :param todict: try to convert any string as a python dict (it can be json or xml string), defaults to True
    :type todict: bool

    :raises AttributeError: if the given path does not correspond to the type of the `ids` argument
    :raises AttributeError: if an element in the path is missing or not of dataclass type, if the attribute is a list
     and create_missing is False, if an element in the list does not exist and create_missing is False,
     or if the attribute is a list and the path does not end with '#XXXX'
    :raises IndexError: if an element in the list is out of range

    :return: None
    """

    path_members = __split_path(path, str(type(ids)))
    current_ids = ids

    for idx, subpath in enumerate(path_members[:-1]):
        parent_ids = current_ids

        # '#' indicates current item is a list element
        if "#" in subpath:
            field_name, offset = subpath.strip().split("#")
            offset = int(offset)
            field_name = camel2snake(field_name)
            list_attr = getattr(current_ids, field_name, None)

            type_arg_list, is_list = get_type_arg(parent_ids, field_name)
            # TODO: exact role of create missing
            if field_name is None:
                if create_missing is False:
                    raise AttributeError(f"missing element {subpath}")
            if not isinstance(list_attr, (list, tuple)):
                raise AttributeError(f"element {field_name} is not a list but a {type(list_attr)}")

            len_list_attr = len(list_attr)
            if len_list_attr < offset and offset > 0:
                raise IndexError(f"element {field_name} has a len of {len_list_attr} and cannot reach elem #{offset}")

            if (offset == len_list_attr) and (create_missing is True):
                # create a new subitem and append it to the list
                list_attr.append(create_instance_from_type(type_arg_list))

            elif (offset == len_list_attr) and (create_missing is False):
                raise IndexError(
                    f"element number #{offset} does not exist and cannot be created :"
                    f" create_missing is {create_missing}")

                # set value of indicated subitem
            return set_ids_value_from_string(list_attr[offset], "/".join(path_members[idx + 1:]), value,
                                             create_missing=create_missing,
                                             todict=todict)
        else:
            try:
                current_ids = getattr(current_ids, subpath)
            except AttributeError:
                raise AttributeError(f"no member named {subpath} in {type(parent_ids)}")
            if current_ids is None:
                if create_missing is False:
                    raise AttributeError(f"missing element {subpath}")
                else:
                    if isinstance(parent_ids, (list, tuple)):
                        raise AttributeError(
                            f" item {path_members[idx - 1]} is represented by a list in the dataclass and should be "
                            f"reached with the syntex item#XXXX")
                    if not dataclasses.is_dataclass(parent_ids):
                        raise AttributeError(f" item {path_members[idx - 1]} is not of dataclass type {parent_ids}")
                    type_arg_list, is_list = get_type_arg(parent_ids, subpath)

                    # TODO : case is_list is True
                    new_entry = create_instance_from_type(type_arg_list)
                    setattr(parent_ids, subpath, new_entry)
                    current_ids = getattr(parent_ids, subpath)

    if current_ids is None:
        raise AttributeError(f"attribute [{path_members[-2]}] is missing in the IDS {type(ids)}")
    if isinstance(current_ids, (list, tuple)):
        raise AttributeError(f"attribute [{path_members[-2]}] is a list so it must be used as {path_members[-2]}#XXXX")


    # last attribute correspond to a list element
    if "#" in path_members[-1]:
        field_name, offset = path_members[-1].strip().split("#")
        offset = int(offset)
        attr_value = getattr(current_ids, field_name)
        if isinstance(attr_value, (list, tuple)):
            return setattr(current_ids, field_name[offset], value)
        else:
            raise AttributeError(f"attribute {field_name} is of type {type(attr_value)} and not list")

    attr_type, attr_list = get_type_arg(current_ids, path_members[-1])

    if _is_0d_array(value) is True:
        value = value[()]

    if isinstance(value, bytes):
        value = value.decode("utf8")

    if isinstance(value, str):
        if (todict is True) and (attr_type in (dict, str)):
            if value.strip()[0] == "<":
                value = xml_to_dict(value)
            elif value.strip()[0] == "{":
                try:
                    value = js.loads(value)
                except js.JSONDecodeError:
                    print(f"not a valid json string : [{value}]")
                    print("no conversion to dict possible")

    elif isinstance(value, (list, tuple, ndarray)):
        if isinstance(value, (list, tuple)):
            value = array(value)
        if isinstance(value.flatten()[0], bytes):
            value = _convert_bytes_to_str(value)
    if attr_list is True:
        if not _check_simplified_types(type(value), list):
            raise ValueError(
                f"value [{value}] for attr {path_members[-1]} is of type {type(value)} "
                f"and should be of type list[{attr_type}]")
        else:
            if not _check_simplified_types(type(value[0]), attr_type):
                raise ValueError(
                    f"value [{value}] for attr {path_members[-1]} is of type list[{type(value)}] "
                    f"and should be of type list[{attr_type}]")
    else:
        if not _check_simplified_types(type(value), attr_type):
            if not ((attr_type in (dict, str)) and (isinstance(value, dict) is True) and (todict is True)):
                raise ValueError(
                    f"value [{value}] for attr {path_members[-1]} is of type {type(value)}"
                    f" and should be of type {attr_type}/{attr_list}")

    setattr(current_ids, path_members[-1], value)


def copy_ids(dest_ids: Type[DC], source_ids: Type[DC],
             ignore_missing=False, keep_source_ids: bool = True, bytes_to_str: bool = True) -> None:
    """
    Copy the fields of the dataclass given at source_ids in the dataclass dest_ids.

    Args:
        dest_ids (dataclass): The destination dataclass to copy the fields to.
        source_ids (dataclass): The source dataclass to copy the fields from.
        ignore_missing (bool, optional): If True, missing fields in dest_ids are ignored. Otherwise, a KeyError is
        raised. Defaults to False.
        keep_source_ids (bool, optional): If False, the source fields are set to None after being copied to the
        destination dataclass. Defaults to False.
        bytes_to_str (bool, optional): If True, bytes fields are decoded to str if the destination field_clazz is of type str.
         Otherwise, they are copied as bytes. Defaults to True.

    Raises:
        TypeError: If dest_ids or source_ids is not a dataclass.
        KeyError: If ignore_missing is False and a field_clazz is missing in dest_ids.

    Returns:
        None
    """
    if type(dest_ids) != type(source_ids):
        raise TypeError(f"dest_ids and source_ids must be the same type and not {type(dest_ids)} and {type(source_ids)}")
    for field in dataclasses.fields(source_ids):
        field_name = field.name
        field_value = getattr(source_ids, field_name)

        # recursively call copy_ids for nested dataclasses
        if dataclasses.is_dataclass(field_value):
            nested_dest = getattr(dest_ids, field_name)
            if not dataclasses.is_dataclass(nested_dest):
                raise TypeError("Both dest_ids and source_ids must be dataclasses.")
            copy_ids(nested_dest, field_value, ignore_missing, keep_source_ids, bytes_to_str)
            if keep_source_ids is False:
                setattr(source_ids, field_name, None)
        else:
            # check if the field_clazz is present in the destination dataclass
            if not ignore_missing and not hasattr(dest_ids, field_name):
                raise KeyError(f"Field {field_name} is missing from dest_ids.")

            # get the field_clazz type from the destination dataclass
            field_type = get_type_hints(dest_ids)[field_name]

            # convert bytes to str if needed
            if bytes_to_str and isinstance(field_value, bytes) and issubclass(field_type, str):
                field_value = field_value.decode()


            setattr(dest_ids, field_name, field_value)

            # set the source field_clazz to None if keep_source_ids is False
            if keep_source_ids is False:
                setattr(source_ids, field_name, None)
