import pytest
from dataclasses import dataclass
from typing import Union
from idspy_toolkit.toolkit import list_ids_members


@dataclass
class Address:
    street: str
    city: str
    zip_code: int


@dataclass
class Person:
    name: str
    age: int
    address: Address


@dataclass
class Employee:
    id: int
    person: Person


@dataclass
class Department:
    id: int
    name: str
    employees: list[Employee]



def test_list_ids_members():
    # Test case 1: list all attribute IDs of a simple dataclass instance
    person = Person(name="John", age=30, address=Address(street="123 Main St.", city="New York", zip_code=10001))
    expected_ids = [
    #    "/Person",
        "/Person/name",
        "/Person/age",
    #    "/Person/address",
        "/Person/address/street",
        "/Person/address/city",
        "/Person/address/zip_code"
    ]
    assert sorted(list_ids_members(person)) == sorted(expected_ids)

    # Test case 2: list all attribute IDs of a nested dataclass instance
    employee = Employee(id=1, person=person)
    expected_ids = [
     #   "/Employee",
        "/Employee/id",
     #   "/Employee/person",
        "/Employee/person/name",
        "/Employee/person/age",
     #   "/Employee/person/address",
        "/Employee/person/address/street",
        "/Employee/person/address/city",
        "/Employee/person/address/zip_code"
    ]
    assert sorted(list_ids_members(employee)) == sorted(expected_ids)

    # Test case 3: list all attribute IDs of a dataclass instance with a list of nested dataclass instances
    department = Department(id=1, name="Sales", employees=[employee])
    expected_ids = [
    #    "/Department",
        "/Department/id",
        "/Department/name",
  #      "/Department/employees#000000",
        "/Department/employees#000000/id",
   #     "/Department/employees#000000/person",
        "/Department/employees#000000/person/name",
        "/Department/employees#000000/person/age",
    #    "/Department/employees#000000/person/address",
        "/Department/employees#000000/person/address/street",
        "/Department/employees#000000/person/address/city",
        "/Department/employees#000000/person/address/zip_code"
    ]
    assert sorted(list_ids_members(department)) == sorted(expected_ids)

    # Test case 4: raise TypeError if the input parameter is not a dataclass instance
    with pytest.raises(TypeError):
        list_ids_members("not a dataclass instance")