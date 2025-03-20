import dataclasses
from dataclasses import Field
from typing import Any, Type, Union, List, Tuple, TypeVar
from typing import get_args, _GenericAlias
from inspect import getmembers, isclass
from typing_extensions import Protocol
import numpy as np
import re
from idspy_toolkit.snippets import is_dataclass_field
from inspect import isdatadescriptor


class DataClass(Protocol):
    __dataclass_fields__: dict[str, Any]


DC = TypeVar("DC", bound=DataClass)


def snake2camel(snake_string: str) -> str:
    """
    convert a string from snake_case to CamelCase
    :param snake_string: string to modify
    :return: the converted string
        Example::
        >>> snake2camel("device_type")
        'DeviceType'
    """
    temp = snake_string.split("_")
    return "".join([*map(str.title, temp)])


def camel2snake(camel_string: str) -> str:
    """
    convert string from CamelCase to snake_case
    :param camel_string: string to modify
    :return: the converted string

    Example::
        >>> camel2snake("DeviceType")
        'device_type'
    """

    return "".join(["_" + c.lower() if c.isupper() else c
                    for c in camel_string]).lstrip("_")


def _imas_default_values(guessed_type: Type) -> Union[List[Any], Any, None, List[None]]:
    """
        return a default value for a given type
    :TODO : handle numpy array
    :param guessed_type:
    :return: default value of the corresponding type
    """

    if type(guessed_type) == type:
        try:
            guessed_type = guessed_type()
        # TypeError occurs if guessed_type corresponds to a numpy array
        # since constructor needs at least a shape in that case
        except TypeError:
            return np.array([])
        if isinstance(guessed_type, bool):
            return False
        elif isinstance(guessed_type, int):
            return int(999999999)
        elif isinstance(guessed_type, float):
            return float(9.0e40)
        elif isinstance(guessed_type, str):
            return str("")
        elif isinstance(guessed_type, complex):
            return complex(9.0e40, -9.0e40)
        elif isinstance(guessed_type, (list, tuple)):
            return []
        else:
            if dataclasses.is_dataclass(guessed_type):
                return guessed_type
            else:
                print("unknow type found", guessed_type, type(guessed_type))
                return None
    else:
        return [_imas_default_values(get_args(guessed_type)[0]), ]


def __get_field_main_type(field: Field[Any]) -> Type:
    """
        return the main type of a dataclass field. As example, for a field of type list[str], it will return list
    :param field: name of the dataclass field
    :return: type of the field
    :TODO : check function when used with numpy array
    """
    if "list" in str(field.type):
        field_type = list
    elif "tuple" in str(field.type):
        field_type = tuple
    elif "ndarray" in str(field.type):
        field_type = np.ndarray
    else:
        field_type = __get_field_type(field)

    return field_type


def __get_field_type(field: Field[Any]) -> Type:
    """
        return the inner type of a dataclass field. As example, for a field of type list[str], it will return str
    :param field: name of the dataclass field
    :return: type of the field
    :TODO : check function when used with numpy array and/or list
    """
    try:
        field_type = tuple(x for x in field.type.__args__ if x is not type(None))[0]
    except AttributeError:
        field_type = field.type

    return field_type



def get_field_with_type(ids: Type[DC],
                        ids_field: Union[str, Field[Any]]) -> Tuple[Any, Type]:
    """Get the value of a field from a dataclass instance, along with the expected type.

    :param ids: The dataclass instance to get the field value from.
    :type ids: dataclasses.dataclass
    :param ids_field: The field whose value to get. Can be either a string representing the field name, or a `dataclasses.Field` object.
    :type ids_field: Union[str, dataclasses.fields]
    :raises ValueError: If the `field` argument does not represent a field name of the `ids` class.
    :raises TypeError: If the type of the field value does not match the expected type.
    :return: A tuple containing the value of the field and its expected type.
    :rtype: Tuple[Any, Type]
    """
    # if member_descriptor is passed as argument, throw an exception
    if isdatadescriptor(ids_field):
        raise TypeError(f"argument ids_field {ids_field} cannot be a class member descriptor")
    # check if member is of type field
    extracted_field = ids_field
    if is_dataclass_field(ids, ids_field):
        if isinstance(ids_field, str):
            field_value = getattr(ids, ids_field, None)
            extracted_field = [x for x in dataclasses.fields(ids) if ids_field == x.name][0]
        else:
            field_value = getattr(ids, ids_field.name, None)
    # or a string representing a fieldname
    elif hasattr(ids, "__dataclass_fields__"):
        if ids.__dataclass_fields__.get(ids_field, None) is not None:
            extracted_field: dict[str, Any] = ids.__dataclass_fields__.get(ids_field)
            field_value = getattr(ids, extracted_field.name)
        else:
            raise ValueError(f"argument {str(ids_field)} does not represent a fieldname of the class {str(ids)}")

    # replace type with main type, for list items
    expected_field_type = __get_field_type(extracted_field)
    if field_value is None:
        return None, expected_field_type

    raise_error_type = False
    is_array_like = False
    if isinstance(field_value, (tuple, list)):
        is_array_like = True
        if len(field_value) == 0:
            return field_value, expected_field_type
        else:
            if not isinstance(field_value[0], expected_field_type):
                raise TypeError(
                    f"field {extracted_field.name} should be a list of {str(expected_field_type)} and not a list of {type(field_value[0])}")
    elif isinstance(field_value, np.ndarray):
        if field_value.ndim == 0:
            field_value = field_value[()]
        else:
            is_array_like = True
            if not isinstance(field_value[0], expected_field_type):
                raise TypeError(
                    f"field {extracted_field.name} should be a numpy.ndarray of {str(expected_field_type)} and not a list of {type(field_value[0])}")

    if not is_array_like:
        if not _check_simplified_types(type(field_value), expected_field_type):
            raise_error_type = True
    else:
        if not _check_simplified_types(type(field_value[0]) , expected_field_type):
            raise_error_type = True
    if raise_error_type is True:
        raise TypeError(
            f"field {extracted_field.name} should be {str(expected_field_type)} and not {type(field_value)}")

    return field_value, expected_field_type


def _check_simplified_types(vartype, expected_type) -> bool:
    """

    Check if the type of a variable matches the expected type.

    Parameters:
    - vartype (Type): The type of the variable.
    - expected_type (Union[Type, Tuple[Type]]): The expected type or types.

    Returns:
    - bool: True if the type matches, False otherwise.

    Example Usage:
    ```
    # Check if an integer variable has the expected type
    var_type = int
    expected = int
    match = _check_simplified_types(var_type, expected)
    print(match)  # Output: True

    # Check if a float variable has the expected type
    var_type = float
    expected = (float, np.inexact)
    match = _check_simplified_types(var_type, expected)
    print(match)  # Output: True

    # Check if a string variable has the expected type
    var_type = str
    expected = int
    match = _check_simplified_types(var_type, expected)
    print(match)  # Output: False
    ```
    """
    if isinstance(expected_type, str):
        if "ndarray" in expected_type:
            expected_type = np.ndarray
    if not isinstance(vartype, expected_type):
        # check if
        type_match = False
        if np.issubdtype(vartype, np.integer) and np.issubdtype(expected_type, np.integer):
            type_match = True
        elif np.issubdtype(vartype, np.inexact) and np.issubdtype(expected_type, np.inexact):
            type_match = True
        elif np.issubdtype(vartype, np.integer) and np.issubdtype(expected_type, np.inexact):
            type_match = True
        elif (vartype in (list, tuple, np.ndarray)) and (expected_type in (list, tuple, np.ndarray)):
            type_match = True
        elif vartype == expected_type:
            type_match = True
        elif np.issubdtype(vartype, np.str_) and np.issubdtype(expected_type, np.str_):
            type_match = True
    return type_match


def _get_all_subdataclasses(member, current_dict: dict) -> None:
    if not dataclasses.is_dataclass(member):
        return
    current_dict.update({str(type(member)).split('.')[-1][:-2]: member})
    for attr in dataclasses.fields(member):
        if "ForwardRef" in str(attr.type):
            fwd_type = str(attr.type).split("ForwardRef")[1][2:-3]
            current_dict.update({fwd_type: getattr(member, fwd_type.split(".")[1])})
            _get_all_subdataclasses(getattr(member, fwd_type.split(".")[1])(), current_dict)
        else:

            current_var_type = __get_field_type(attr)
            if str(current_var_type) == "typing.Any":
                continue
            # if var is of type numpy array or ndarray
            if "numpy." in str(current_var_type):
                continue
            if isinstance(current_var_type, (_GenericAlias,)) or isinstance(current_var_type(), (str, int, float)):
                continue

            _get_all_subdataclasses(current_var_type(), current_dict)


def get_all_class(module_name, current_dict: dict) -> None:
    """
        create a dict where all keys are strings of  all dataclasses of the module
        :param module_name: name of the ids module
        :param current_dict: generated dict
        :return : None
    """

    correspondance_table = {x[0]: x[1] for x in getmembers(module_name, predicate=isclass) if
                            (x[0].startswith("__") is False) and ("ndarray" not in x[0])}
    for k, v in correspondance_table.items():
        member = v()
        _get_all_subdataclasses(member, current_dict)


def extract_ndarray_info(expr: str):
    data_type_equiv = {'int': np.int32,
                       'float': np.float64,
                       'complex': np.complex128,
                       'str': str}
    pattern = r".*ndarray\[\((.*?)\),\s*(\w+)\]"

    match = re.match(pattern, expr)
    if match:
        contents = match.group(1)
        data_type = match.group(2)
    else:
        raise ValueError(f"expression {expr} does not match with an numpy.ndarray")

    dim_set = tuple(set([x.strip() for x in contents.split(",") if x != ""]))
    if len(dim_set) > 1:
        raise ValueError(f"expression {expr} does not match with an numpy.ndarray, dimension error")
    if dim_set[0] != "<class 'int'>":
        raise ValueError(f"expression {expr} does not match with an numpy.ndarray, dimension has to be integer")
    shape = (0,) * len([x for x in contents.split(",") if x != ""])
    return shape, data_type_equiv.get(data_type, str)
