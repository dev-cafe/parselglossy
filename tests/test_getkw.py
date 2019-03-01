#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `parselglossy` package."""

import json
import math

import pytest

from parselglossy import getkw
from parselglossy.atoms import ComplexEncoder, as_complex


@pytest.fixture
def keywords():
    keys = """topsect {{
int = 42
dbl = {PI}
cmplx = -1 -{E}*I
bool = on
str = "fooffa"

$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end

int_array = {LIST}
dbl_array = [{PI}, {E}, {TAU}]
cmplx_array = [{PI} -2*j, {E}-2.0*J, {TAU}+1.5*i]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
}}
"""
    return keys.format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, LIST=list(range(1, 5)))


# yapf: disable
keyword_ref = {
     'int': 42
    , 'dbl': math.pi
    , 'cmplx': complex(-1, -math.e)
    , 'bool': True
    , 'str': 'fooffa'
    , 'int_array': list(range(1, 5))
    , 'dbl_array': [math.pi, math.e, 2.0*math.pi]
    , 'cmplx_array': [complex(math.pi, -2.0), complex(math.e, -2.0), complex(2.0*math.pi, 1.5)]
    , 'bool_array': [True, True, True, False, True, False]
    , 'str_array': ["foo", "bar", "lorem", "IpSuM"]
    , 'raw': "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"
}
# yapf: enable


@pytest.mark.dependency()
def test_keyword(keywords):
    grammar = getkw.grammar()
    tokens = grammar.parseString(keywords).asDict()['topsect']

    # dump to JSON
    json.dump(tokens, pytest.getkw_keywords_json, cls=ComplexEncoder)

    assert tokens == keyword_ref


@pytest.mark.dependency(depends=['test_keyword'])
def test_keyword_from_json():
    # load from JSON
    tokens = json.loads(
        pytest.getkw_keywords_json.getvalue(), object_hook=as_complex)

    assert tokens == keyword_ref
