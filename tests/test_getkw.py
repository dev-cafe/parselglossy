#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `parselglossy` package."""

import json
import math

import pytest
from parselglossy import getkw_grammar
from parselglossy.atoms import ComplexEncoder, as_complex


@pytest.fixture
def keywords():
    return F"""
int = 42
dbl = {math.pi}
cmplx = -1 -{math.e}*I
bool = on
str = "fooffa"

$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end

int_array = {list(range(1, 5))}
dbl_array = [{math.pi}, {math.e}, {math.tau}]
cmplx_array = [{math.pi} -2*j, {math.e}-2.0*J, {math.tau}+1.5*i]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
"""


# yapf: disable
keyword_ref = {
     'int': 42
    , 'dbl': math.pi
    , 'cmplx': complex(-1, -math.e)
    , 'bool': True
    , 'str': 'fooffa'
    , 'int_array': list(range(1, 5))
    , 'dbl_array': [math.pi, math.e, math.tau]
    , 'cmplx_array': [complex(math.pi, -2.0), complex(math.e, -2.0), complex(math.tau, 1.5)]
    , 'bool_array': [True, True, True, False, True, False]
    , 'str_array': ["foo", "bar", "lorem", "IpSuM"]
    , 'raw': "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"
}
# yapf: enable


@pytest.mark.dependency()
def test_keyword(keywords):
    grammar = getkw_grammar.getkw()
    tokens = grammar.parseString(keywords).asDict()
    result = getkw_grammar.flatten_dict(tokens)

    # dump to JSON
    json.dump(result, pytest.getkw_keywords_json, cls=ComplexEncoder)

    assert result == keyword_ref


@pytest.mark.dependency(depends=['test_keyword'])
def test_keyword_from_json():
    # load from JSON
    tokens = json.loads(
        pytest.getkw_keywords_json.getvalue(), object_hook=as_complex)

    assert tokens == keyword_ref
