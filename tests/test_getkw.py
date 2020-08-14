#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2020 Roberto Di Remigio, Radovan Bast, and contributors.
#
# This file is part of parselglossy.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# parselglossy library, see: <http://parselglossy.readthedocs.io/>
#

"""Tests for `parselglossy` package."""

import json
import math
from io import StringIO

import pytest

from parselglossy.grammars import getkw, lexer

# fmt: off
reference = {
    'int': 42
  , 'dbl': math.pi
  , 'bool': True
  , 'str': 'fooffa'
  , 'int_array': [42]
  , 'dbl_array': [math.pi, math.e, 2.0*math.pi]
  , 'bool_array': [True, True, True, False, True, False]
  , 'str_array': ["foo", "bar", "lorem", "IpSuM"]
  , 'raw': "H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n"
}
# fmt: on


def contents():
    contents = """/* This is a comment */
int = 42
// This is another comment
dbl = {PI}
bool = on
str = "fooffa"

! Yet another comment
$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end

# I love comments!
int_array = [42]
dbl_array = [{PI}, {E}, {TAU}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
"""
    return contents


@pytest.fixture
def keywords():
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    keys = """{CONTENTS}
"""
    return keys.format(CONTENTS=stuff)


def test_keyword(keywords):
    """Test an input made only of keywords."""
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, keywords)

    assert tokens == reference
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == reference


def section(name):
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    sect = """{NAME} {{
    {CONTENTS}
}}
"""
    return sect.format(NAME=name, CONTENTS=stuff)


@pytest.mark.parametrize("name", ["topsect", "foo<bar>"])
def test_section(name):
    """Test an input made of one section, tagged or untagged."""
    ref_dict = {name: dict(reference)}
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, section(name))

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == ref_dict


@pytest.fixture
def flat_sections():
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    sects = """topsect {{
    {CONTENTS}
}}

foo<bar> {{
    {CONTENTS}
}}
"""
    return sects.format(CONTENTS=stuff)


def test_flat_sections(flat_sections):
    """Test an input made of two unnested sections, tagged or untagged."""
    ref_dict = {"topsect": dict(reference), "foo<bar>": dict(reference)}
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, flat_sections)

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == ref_dict


@pytest.fixture
def nested_sections():
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    sects = """topsect {{
    {CONTENTS}

    foo<bar> {{
        {CONTENTS}
    }}
}}
"""
    return sects.format(CONTENTS=stuff)


def test_nested_sections(nested_sections):
    """Test an input made of two nested sections, tagged or untagged."""
    ref_dict = {"topsect": dict(reference)}
    ref_dict["topsect"]["foo<bar>"] = dict(reference)
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, nested_sections)

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == ref_dict


def keywords_and_section(name):
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    template = """/* This is a comment */
int = 42
// This is another comment
dbl = {PI}
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
int_array = [42]
dbl_array = [{PI}, {E}, {TAU}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
"""
    inp = template.format(
        PI=math.pi, E=math.e, TAU=2.0 * math.pi, NAME=name, CONTENTS=stuff
    )
    return inp


@pytest.mark.parametrize("name", ["topsect", "foo<bar>"])
def test_keywords_and_section(name):
    """Test an input made of keywords, one section, tagged or untagged, and more keywords."""
    ref_dict = dict(reference)
    ref_dict[name] = dict(reference)
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, keywords_and_section(name))

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == ref_dict


@pytest.fixture
def keywords_and_flat_sections():
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    template = """/* This is a comment */
int = 42
// This is another comment
dbl = {PI}
bool = on
str = "fooffa"

topsect {{
    {CONTENTS}
}}

! Yet another comment
$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end

foo<bar> {{
    {CONTENTS}
}}

# I love comments!
int_array = [42]
dbl_array = [{PI}, {E}, {TAU}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
"""
    inp = template.format(PI=math.pi, E=math.e, TAU=2.0 * math.pi, CONTENTS=stuff)
    return inp


def test_keywords_and_flat_sections(keywords_and_flat_sections):
    """Test an input made of keywords and two unnested sections, interspersed."""
    ref_dict = dict(reference)
    ref_dict["topsect"] = dict(reference)
    ref_dict["foo<bar>"] = dict(reference)
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, keywords_and_flat_sections)

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == ref_dict


@pytest.fixture
def keywords_and_nested_sections():
    stuff = contents().format(PI=math.pi, E=math.e, TAU=2.0 * math.pi)
    template = """/* This is a comment */
int = 42
// This is another comment
dbl = {PI}
bool = on
str = "fooffa"

! Yet another comment
$raw
H 0.0 0.0 0.0
F 1.0 1.0 1.0
$end

topsect {{
    {CONTENTS}

    foo<bar> {{
        {CONTENTS}
    }}
}}

# I love comments!
int_array = [42]
dbl_array = [{PI}, {E}, {TAU}]
bool_array = [on, true, yes, False, True, false]
str_array = [foo, bar, "lorem", "IpSuM"]
"""
    inp = template.format(PI=math.pi, E=math.e, TAU=2.0 * math.pi, CONTENTS=stuff)
    return inp


def test_keywords_and_nested_sections(keywords_and_nested_sections):
    """Test an input made of keywords and two nested sections, interspersed."""
    ref_dict = dict(reference)
    ref_dict["topsect"] = dict(reference)
    ref_dict["topsect"]["foo<bar>"] = dict(reference)
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, keywords_and_nested_sections)

    assert tokens == ref_dict
    # dump to JSON
    getkw_json = StringIO()
    json.dump(tokens, getkw_json, indent=4)
    del tokens

    # load from JSON
    tokens = json.loads(getkw_json.getvalue())

    assert tokens == ref_dict


@pytest.fixture
def data_only_section():
    stuff = """molecule {
$coords
H  0.0000  0.0000 -0.7000
H  0.0000  0.0000  0.7000
$end
}
    """
    return stuff


def test_data_only_section(data_only_section):
    ref = {
        "molecule": {"coords": "H  0.0000  0.0000 -0.7000\nH  0.0000  0.0000  0.7000\n"}
    }
    grammar = getkw.grammar()
    tokens = lexer.parse_string_to_dict(grammar, data_only_section)

    assert tokens == ref
