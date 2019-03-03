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
reference = {
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
    keys = """{CONTENTS}
"""
    return keys.format(CONTENTS=stuff)


def test_keyword(keywords):
    """Test an input made only of keywords."""
    grammar = getkw.grammar()
    tokens = grammar.parseString(keywords).asDict()

    assert tokens == reference
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == reference


def section(name):
    stuff = contents().format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, LIST=list(range(1, 5)))
    sect = """{NAME} {{
    {CONTENTS}
}}
"""
    return sect.format(NAME=name, CONTENTS=stuff)


@pytest.mark.parametrize('name', [
    'topsect',
    'foo<bar>',
])
def test_section(name):
    """Test an input made of one section, tagged or untagged."""
    ref_dict = {name: reference}
    grammar = getkw.grammar()
    tokens = grammar.parseString(section(name)).asDict()

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == ref_dict


@pytest.fixture
def flat():
    stuff = contents().format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, LIST=list(range(1, 5)))
    sects = """topsect {{
    {CONTENTS}
}}

foo<bar> {{
    {CONTENTS}
}}
"""
    return sects.format(CONTENTS=stuff)


def test_flat_sections(flat):
    """Test an input made of two unnested sections, tagged or untagged."""
    ref_dict = {'topsect': reference, 'foo<bar>': reference}
    grammar = getkw.grammar()
    tokens = grammar.parseString(flat).asDict()

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == ref_dict


@pytest.fixture
def nested():
    stuff = contents().format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, LIST=list(range(1, 5)))
    sects = """topsect {{
    {CONTENTS}

    foo<bar> {{
        {CONTENTS}
    }}
}}
"""
    return sects.format(CONTENTS=stuff)


def test_nested_sections(nested):
    """Test an input made of two nested sections, tagged or untagged."""
    ref_dict = {'topsect': reference}
    ref_dict['topsect']['foo<bar>'] = dict(reference)
    grammar = getkw.grammar()
    tokens = grammar.parseString(nested).asDict()

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == ref_dict


def keywords_and_section(name):
    stuff = """/* This is a comment */
int = 42
// This is another comment
dbl = {PI}
cmplx = -1 -{E}*I
bool = on
str = "fooffa"

{NAME} {{
    {CONTENTS}
}}

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
    inp = stuff.format(
        PI=math.pi,
        E=math.e,
        TAU=2.0 * math.pi,
        LIST=list(range(1, 5)),
        NAME=name,
        CONTENTS=contents())
    return inp


@pytest.mark.parametrize('name', [
    'topsect',
    'foo<bar>',
])
def test_keywords_and_section(name):
    """Test an input made of keywords, one section, tagged or untagged, and more keywords."""
    ref_dict = dict(reference, **({name: reference}))
    grammar = getkw.grammar()
    tokens = grammar.parseString(keywords_and_section(name)).asDict()

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, cls=ComplexEncoder)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue(), object_hook=as_complex)

    assert tokens == ref_dict
