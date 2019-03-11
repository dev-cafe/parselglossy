from parselglossy.validate import type_matches
import pytest


def test_type_matches():

    # str
    assert type_matches('a string', 'str')
    assert not type_matches(1.0, 'str')

    # float and int
    assert type_matches(1.0, 'float')
    assert type_matches(1.0e-8, 'float')
    assert type_matches(1, 'int')
    assert not type_matches(1, 'float')

    # complex
    assert type_matches(1.0+1.0j, 'complex')

    # bool
    assert type_matches(True, 'bool')
    assert type_matches(False, 'bool')
    assert not type_matches(0, 'bool')

    # lists
    assert type_matches([1, 2, 3], 'List[int]')
    assert not type_matches((1, 2, 3), 'List[int]')
    assert not type_matches([1, 2, 3], 'List[float]')
    assert type_matches([1.0, 2.0, 3.0], 'List[float]')
    assert not type_matches([1.0, 2.0, 3], 'List[float]')

    # unexpected type input
    with pytest.raises(ValueError):
        assert type_matches('example', 'weird')
        assert type_matches('example', 'List[strange]')
