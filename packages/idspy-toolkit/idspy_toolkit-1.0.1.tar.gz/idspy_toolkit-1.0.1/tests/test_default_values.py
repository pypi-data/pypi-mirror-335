import numpy as np
import pytest
from dataclasses import dataclass

from idspy_toolkit.constants import (IMAS_DEFAULT_INT, IMAS_DEFAULT_STR,
                                 IMAS_DEFAULT_FLOAT, IMAS_DEFAULT_CPLX, IMAS_DEFAULT_LIST)

from idspy_toolkit.toolkit import is_default_imas_value

# Sample dataclass for testing
@dataclass
class IDS:
    value_str: str = IMAS_DEFAULT_STR
    value_int: int = IMAS_DEFAULT_INT
    value_float: float = IMAS_DEFAULT_FLOAT
    value_cplx: complex = IMAS_DEFAULT_CPLX
    value_list: list = None
    value_none: None = None

@dataclass
class NewType:
    value_str: str = "other str"

# Unit tests
@pytest.fixture
def sample_ids():
    return IDS(
        value_str=IMAS_DEFAULT_STR,
        value_int=IMAS_DEFAULT_INT,
        value_float=IMAS_DEFAULT_FLOAT,
        value_cplx=IMAS_DEFAULT_CPLX,
        value_list=IMAS_DEFAULT_LIST,
        value_none=None
    )


def test_default_string(sample_ids):
    assert is_default_imas_value(sample_ids, "value_str") is True


def test_default_int(sample_ids):
    assert is_default_imas_value(sample_ids, "value_int") is True


def test_default_float(sample_ids):
    assert is_default_imas_value(sample_ids, "value_float") is True


def test_default_complex(sample_ids):
    assert is_default_imas_value(sample_ids, "value_cplx") is True


def test_default_list(sample_ids):
    assert is_default_imas_value(sample_ids, "value_list") is True


def test_default_none(sample_ids):
    assert is_default_imas_value(sample_ids, "value_none") is True


def test_non_default_string(sample_ids):
    sample_ids.value_str = "non-default"
    assert is_default_imas_value(sample_ids, "value_str") is False


def test_non_default_int(sample_ids):
    sample_ids.value_int = 42
    assert is_default_imas_value(sample_ids, "value_int") is False

def test_non_default_int_np(sample_ids):
    sample_ids.value_int = np.int32(42)
    assert is_default_imas_value(sample_ids, "value_int") is False


def test_non_default_float(sample_ids):
    sample_ids.value_float = 3.14
    assert is_default_imas_value(sample_ids, "value_float") is False


def test_non_default_float_np(sample_ids):
    sample_ids.value_float = np.float64(3.14)
    assert is_default_imas_value(sample_ids, "value_float") is False


def test_non_default_complex(sample_ids):
    sample_ids.value_cplx = 1 + 1j
    assert is_default_imas_value(sample_ids, "value_cplx") is False

def test_non_default_complex_np(sample_ids):
    sample_ids.value_cplx = np.complex64(1 + 1j)
    assert is_default_imas_value(sample_ids, "value_cplx") is False

def test_non_default_list(sample_ids):
    sample_ids.value_list = [1, 2, 3]
    assert is_default_imas_value(sample_ids, "value_list") is False


def test_non_default_none(sample_ids):
    sample_ids.value_none = "not none"
    assert is_default_imas_value(sample_ids, "value_none") is False


def test_unknown_type(sample_ids):
    sample_ids.value_none = NewType()
    with pytest.raises(TypeError):
        is_default_imas_value(sample_ids, "value_none")

