import pytest
from dataclasses import dataclass
from typing import Union
import idspy_toolkit.simplexml as simplexml


class NotReallyDict(dict):
    pass


test_notreallydict = NotReallyDict({"a": 1, "b": NotReallyDict({"c": 2, })})
test_notreallydict_xml = r'<root><a type="int">1</a><b type="dict"><c type="int">2</c></b></root>'

dict_sample = {
    "data": {
        "id": "123",
        "values": [1, 2, 3],
        "descr": {"a": 1, "b": 2},
        "values_2d": [[1, 2, 3], [1, 2, 3]]
    },
    "offset": 2,
    "id": 123,
}

true_string = (r'<root><data type="dict"><id type="str">123</id><values type="list"><item type="int">1</item>'
               r'<item type="int">2</item><item type="int">3</item></values><descr type="dict"><a type="int">1</a>'
               r'<b type="int">2</b></descr><values_2d type="list"><item type="list"><item type="int">1</item>'
               r'<item type="int">2</item><item type="int">3</item></item><item type="list"><item type="int">1</item>'
               r'<item type="int">2</item><item type="int">3</item></item></values_2d></data>'
               r'<offset type="int">2</offset><id type="int">123</id></root>')

xml_with_empty_str = ('<root><empty_str type="str" /><half_empty_list type="list"><item type="str">a</item>'
                      '<item type="str" /></half_empty_list></root>')


def compare_dict(dict1, dict2) -> bool:
    equal = all([dict1[key] == dict2[key]
                 for key in dict1.keys()
                 if ((key in dict2) and (not isinstance(dict2[key], dict)))])
    return equal


def test_clean_key():
    assert simplexml.clean_key("#test") == "test"
    assert simplexml.clean_key("@test") == "test"


def test_guess_from_val():
    assert simplexml.guess_from_val({"a": 1}) == {"a": 1}
    assert simplexml.guess_from_val("42") == 42
    assert abs(simplexml.guess_from_val("4.2") - 4.2) < 1e-8
    assert simplexml.guess_from_val(str(complex(4, 2))) == complex(4, 2)
    assert simplexml.guess_from_val("  False ") is False
    assert simplexml.guess_from_val("  false ") is False
    assert simplexml.guess_from_val("  True ") is True
    assert simplexml.guess_from_val("  true ") is True
    assert simplexml.guess_from_val("test val") == "test val"


def test_write_xml():
    xmlstr = simplexml.dict_to_xml(dict_sample)
    assert xmlstr == true_string


def test_write_derived_xml():
    xmlstr = simplexml.dict_to_xml(test_notreallydict)
    assert xmlstr == test_notreallydict_xml


def test_read_derived_xml():
    xmldict = simplexml.xml_to_dict(test_notreallydict_xml)
    equal = compare_dict(xmldict, test_notreallydict)
    assert equal is True
    equal = compare_dict(xmldict.get("b", {}), test_notreallydict["b"])
    assert equal is True


def test_read_xml():
    xmldict = simplexml.xml_to_dict(true_string)
    equal = compare_dict(xmldict, dict_sample)
    assert equal is True
    equal = compare_dict(xmldict.get("data", {}), dict_sample["data"])
    assert equal is True
    equal = compare_dict(xmldict.get("data", {}).get("descr", {}), dict_sample["data"]["descr"])
    assert equal is True


def test_empty_string_to_xml():
    empty_dict = {"empty_str": "",
                  "half_empty_list": ["a", ""]}
    xmldict = simplexml.dict_to_xml(empty_dict)
    assert xmldict == xml_with_empty_str


def test_xml_to_empty_string():
    empty_dict = {"empty_str": "",
                  "half_empty_list": ["a", ""]}
    ret_dict = simplexml.xml_to_dict(xml_with_empty_str)
    equal = compare_dict(empty_dict, ret_dict)
    assert equal is True


def test_empty_dict_to_xml():
    empty_dict = {"empty_str": "",
                  "hempty_dict": {}}
    xml_dict = simplexml.dict_to_xml(empty_dict)
    ret_dict = simplexml.xml_to_dict(xml_dict)
    is_equal = compare_dict(empty_dict, ret_dict)
    assert is_equal is True

def test_dict_to_xml():
    with pytest.raises(ValueError) as excinfo:
        simplexml.dict_to_xml("42")
    with pytest.raises(ValueError) as excinfo:
        simplexml.dict_to_xml("{'a':42}")
    #assert str(excinfo.value) == "Invalid email address"


def test_xml_attrib():
    new_attrib = simplexml.XmlAttrib(text=str(complex(4, 2)), type="complex")
    assert new_attrib.value == complex(4, 2)
    new_attrib = simplexml.XmlAttrib(text=str(complex(4, 2)), type="number")
    assert new_attrib.value == complex(4, 2)
    new_attrib = simplexml.XmlAttrib(text=str(4.2), type="number")
    assert new_attrib.value == complex(4.2, 0)
    new_attrib = simplexml.XmlAttrib(text=" true ", type="bool")
    assert new_attrib.value is True
    new_attrib = simplexml.XmlAttrib(text=" false ", type="bool")
    assert new_attrib.value is False
    new_attrib = simplexml.XmlAttrib(text="[toto, tata , titi]", type="str")
    assert new_attrib.value == "[toto, tata , titi]"

    new_attrib = simplexml.XmlAttrib(text="[4.2, 4.2 , 4.2]", type="list")
    assert new_attrib.value == [4.2, 4.2, 4.2, ]

    new_attrib = simplexml.XmlAttrib(text="[toto, tata , titi]", type="list")
    assert new_attrib.value == ["toto", "tata", "titi" ]

    new_attrib = simplexml.XmlAttrib(text="[toto, tata , titi]", type="null")
    assert new_attrib.value is None

    new_attrib = simplexml.XmlAttrib(type="null")
    assert new_attrib.value is None

    new_attrib = simplexml.XmlAttrib(text="42", )
    assert new_attrib.value == 42