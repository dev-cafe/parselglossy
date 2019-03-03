#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `parselglossy` package."""

import json
import math
from io import StringIO

import pytest
from parselglossy import getkw
from parselglossy.atoms import ComplexEncoder, as_complex

# yapf: disable
reference_contents = {
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

refs = {
     'keywords' : reference_contents
    , 'untagged' : {'topsect' : reference_contents}
    , 'tagged' : {'foo<bar>' : reference_contents}
}
# yapf: enable


def contents():
    contents = """/* This is a comment */
int = 42
// This is another comment
dbl = {PI}
cmplx = -1 -{E}*I
bool = on
str = "fooffa"

! Yet another comment
$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end

# I love comments!
int_array = {LIST}
dbl_array = [{PI}, {E}, {TAU}]
cmplx_array = [{PI} -2*j, {E}-2.0*J, {TAU}+1.5*i]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
"""
    return contents


@pytest.fixture
def keywords():
    stuff = contents().format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, LIST=list(range(1, 5)))
    keys = """topsect {{
    {CONTENTS:s}
}}
"""
    return keys.format(CONTENTS=stuff)


def test_keyword(keywords):
    grammar = getkw.grammar()
    tokens = grammar.parseString(keywords).asDict()['topsect']

    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)

    assert tokens == refs['keywords']
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == refs['keywords']


def section(name):
    stuff = contents().format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, LIST=list(range(1, 5)))
    sect = """{NAME} {{
    {CONTENTS:s}
}}
"""
    return sect.format(NAME=name, CONTENTS=stuff)


@pytest.mark.parametrize('name,which', [
    ('topsect', 'untagged'),
    ('foo<bar>', 'tagged'),
])
def test_section(name, which):
    print(section(name))
    grammar = getkw.grammar()
    tokens = grammar.parseString(section(name)).asDict()

    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)

    assert tokens == refs[which]
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == refs[which]
