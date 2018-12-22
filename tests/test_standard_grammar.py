#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `parselglossy` package."""

import json
import math

import pytest
from parselglossy import standard_grammar


@pytest.fixture
def keywords():
    return F"""
int = 42
dbl = {math.pi}
bool = on
str = "fooffa"

int_array = {list(range(1, 5))}
dbl_array = [{math.pi}, {math.e}, {math.tau}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]

$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end
"""


keyword_ref = {
    'int': 42,
    'dbl': math.pi,
    'bool': True,
    'str': 'fooffa',
    'int_array': list(range(1, 5)),
    'dbl_array': [math.pi, math.e, math.tau],
    'bool_array': [True, True, True, False, True, False],
    'str_array': ["foo", "bar", "lorem", "IpSuM"],
    'raw': "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"
}


def test_keyword(keywords):

    bnf = standard_grammar.new_BNF()
    tokens = bnf.parseString(keywords).asDict()

    assert tokens == keyword_ref


@pytest.fixture
def sections():
    return F"""
defs {{
int = 42
dbl = {math.pi}
bool = on
str = "fooffa"

int_array = {list(range(1, 5))}
dbl_array = [{math.pi}, {math.e}, {math.tau}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]

$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end
}}

defs<apa> {{
int = 42
dbl = {math.pi}
bool = on
str = "fooffa"

int_array = {list(range(1, 5))}
dbl_array = [{math.pi}, {math.e}, {math.tau}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]

$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end
}}

defs<gorilla> {{
int = 42
dbl = {math.pi}
bool = on
str = "fooffa"

int_array = {list(range(1, 5))}
dbl_array = [{math.pi}, {math.e}, {math.tau}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]

$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end
}}
"""


section_ref = {
    'int': 42,
    'dbl': math.pi,
    'bool': True,
    'str': 'fooffa',
    'int_array': list(range(1, 5)),
    'dbl_array': [math.pi, math.e, math.tau],
    'bool_array': [True, True, True, False, True, False],
    'str_array': ["foo", "bar", "lorem", "IpSuM"],
    'raw': "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"
}


#def test_section(sections):
#    bnf = standard_grammar.BNF()
#    tokens = bnf.parseString(sections).asDict()
#
#    print(tokens)
#    #assert tokens == reference
