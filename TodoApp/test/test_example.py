import pytest

def test_example():
    assert 3==3

def test_is_instance():
    assert isinstance('this is a string',str)

def test_is_boolean():
    validated = True
    assert validated is True

def test_type():
    assert type('hello' is str)
    assert type('world' is not int)

def test_greaterthan():
    assert 7>3

class student:
    def __init__(self,first_name:str, last_name:str, major:str, age:int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.age = age

def test_person():
    p = student('Niranjan', 'Reddy', 'Computer Science', 24)
    assert p.first_name == 'Niranjan', 'First name should be Niranjan'
    assert p.last_name == 'Reddy', 'Last name should be Reddy'
    assert p.major == 'Computer Science', 'Major should be Computer Science'
    assert p.age == 24, 'Age should be 24'


