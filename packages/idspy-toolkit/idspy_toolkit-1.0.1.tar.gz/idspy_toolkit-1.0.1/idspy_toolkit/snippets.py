from typing import Any
from dataclasses import is_dataclass
from dataclasses import Field, fields
from typing import Union, Any
import inspect

_IDS_LIST_DELIMITER = "#"


def format_ids_substring(number: int, delimiter: str = "#") -> str:
    """
        return format for IDS list index.

        Args:
            number (int): index to consider.
            delimiter (str): the character used to specify item position

        Returns:
            str:: A string representation of the list index.

        Example:
            >>> import idspy_toolkit
            >>> format_ids_substring(123,"#")
            #000123
        """
    return "{0}{1:06d}".format(delimiter, number)


def is_dataclass_field(ids: object, item: Union["str", Field[Any]]) -> bool:
    """
    Check if an item is a dataclass field.

    :param ids: The object to check for the field.
    :param item: The item to check, which can be a string representing the field name or a Field instance.
    :return: True if item is a dataclass field, False otherwise.
    """
    if isinstance(item, str):
        return item in [x.name for x in fields(ids)]
    elif getattr(item, "name", None) is not None:
        return item.name in [x.name for x in fields(ids)]
    else:
        return False


def is_dataclass_instance(obj: Any) -> bool:
    """
        check if the object correspond to a python dataclass
    :param obj:
    :return: true or false
    """
    return is_dataclass(obj) and not isinstance(obj, type)


def sort_h5_keys(h5keylist: list, delimiter: str = r"/") -> list:
    """
    Sorts the input list of strings by increasing number of "/", and for elements with the same number of "/",
    by alphabetic order and number after the # increasing.

    :param h5keylist: The list of strings to sort.
    :param delimiter: The delimiter used to separate elements, default=/.
    :Returns: list: The sorted list of strings.
    """
  #  return sorted(h5keylist, key=lambda x: ( x.strip().lower(), x.count(delimiter)))
    return sorted(h5keylist, key=lambda x: (x.count(delimiter), x.strip().lower()))
