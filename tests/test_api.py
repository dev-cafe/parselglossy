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
from pathlib import Path
from shutil import rmtree

import pytest

from parselglossy import api
from parselglossy.utils import as_complex


@pytest.mark.parametrize(
    "args,out,reference",
    [
        (("tests/api/standard.inp",), None, "tests/ref/standard_ir.json"),
        (
            ("tests/api/scf.inp", "standard", "scf_ir.json"),
            "scf_ir.json",
            "tests/ref/scf_ir.json",
        ),
        (
            ("tests/api/getkw.inp", "getkw", "lex_ir.json"),
            "lex_ir.json",
            "tests/ref/getkw_ir.json",
        ),
    ],
    ids=["lex-default", "lex-standard-w-outfile", "lex-getkw-w-outfile"],
)
def test_api_lex(args, out, reference):
    ir = api.lex(*args)

    # Check intermediate representation matches with reference
    ref_json = Path(reference).resolve()
    if out is None:
        with ref_json.open("r") as f:
            assert ir == json.loads(f.read(), object_hook=as_complex)
    else:
        dumped = Path(out).resolve()
        with ref_json.open("r") as ref, dumped.open("r") as o:
            assert json.loads(o.read(), object_hook=as_complex) == json.loads(
                ref.read(), object_hook=as_complex
            )
        # Clean up JSON file
        dumped.unlink()


@pytest.mark.parametrize(
    "args,out,reference",
    [
        (
            ("tests/ref/scf_ir.json", "tests/validation/overall/template.yml"),
            None,
            "tests/ref/scf_fr.json",
        ),
        (
            (
                "tests/ref/scf_ir.json",
                "tests/validation/overall/template.yml",
                "scf_fr.json",
            ),
            "scf_fr.json",
            "tests/ref/scf_fr.json",
        ),
    ],
    ids=["validate-default", "validate-w-outfile"],
)
def test_api_validate(args, out, reference):
    fr = api.validate(*args)

    # Check final representation matches with reference
    ref_json = Path(reference).resolve()
    if out is None:
        with ref_json.open("r") as f:
            assert fr == json.loads(f.read(), object_hook=as_complex)
    else:
        dumped = Path(out).resolve()
        with ref_json.open("r") as ref, dumped.open("r") as o:
            assert json.loads(o.read(), object_hook=as_complex) == json.loads(
                ref.read(), object_hook=as_complex
            )
        # Clean up JSON file
        dumped.unlink()


@pytest.mark.parametrize(
    "args,out,reference",
    [
        (
            ("tests/api/scf.inp", "tests/validation/overall/template.yml"),
            None,
            "tests/ref/scf_fr.json",
        ),
        (
            (
                "tests/api/scf.inp",
                "tests/validation/overall/template.yml",
                "scf_fr.json",
            ),
            "scf_fr.json",
            "tests/ref/scf_fr.json",
        ),
        (
            (
                "tests/api/scf.inp",
                "tests/validation/overall/template.yml",
                None,
                "standard",
                True,
            ),
            None,
            "tests/ref/scf_fr.json",
        ),
    ],
    ids=["parse-default", "parse-w-outfile", "parse-w-dumpir"],
)
def test_api_parse(args, out, reference):
    fr = api.parse(*args)

    # Check final representation matches with reference
    ref_json = Path(reference).resolve()
    if out is None:
        with ref_json.open("r") as f:
            assert fr == json.loads(f.read(), object_hook=as_complex)
    else:
        dumped = Path(out).resolve()
        with ref_json.open("r") as ref, dumped.open("r") as o:
            assert json.loads(o.read(), object_hook=as_complex) == json.loads(
                ref.read(), object_hook=as_complex
            )
        # Clean up JSON file
        dumped.unlink()


@pytest.mark.parametrize(
    "args,out,reference",
    [
        (("tests/api/docs_template.yml",), None, "tests/ref/input.rst"),
        (
            ("tests/api/docs_template.yml", "input.rst"),
            "input.rst",
            "tests/ref/input.rst",
        ),
        (
            (
                "tests/api/docs_template.yml",
                "input.rst",
                "Dwigt Rortugal's guide to input parameters",
            ),
            "input.rst",
            "tests/ref/dwigt.rst",
        ),
    ],
    ids=["document-default", "document-w-outfile", "document-w-header"],
)
def test_api_document(args, out, reference):
    docs = api.document(*args)

    # Check final representation matches with reference
    ref_rst = Path(reference).resolve()
    if out is None:
        with ref_rst.open("r") as ref:
            assert docs == ref.read()
    else:
        dumped = Path(out).resolve()
        with ref_rst.open("r") as ref, dumped.open("r") as o:
            assert o.read() == ref.read()

        # Clean up .rst file
        dumped.unlink()


@pytest.mark.parametrize(
    "args,inp,references",
    [
        (
            {
                "template": "tests/validation/overall/template.yml",
                "docfile": "foo.rst",
                "grammar": "standard",
            },
            "tests/api/scf.inp",
            ("tests/ref/scf_fr.json", "tests/ref/generated_input.rst"),
        ),
        (
            {
                "template": "tests/validation/overall/template.yml",
                "docfile": "babar.rst",
                "grammar": [
                    Path(__file__).parents[1].absolute()
                    / f"parselglossy/grammars/{x}.py"
                    for x in ["atoms", "getkw"]
                ],
                "tokenize": "from . import getkw; lexer = getkw.grammar(has_complex=True); ir = lexer.parseString(in_str).asDict()",
            },
            "tests/api/scf.inp",
            ("tests/ref/scf_fr.json", "tests/ref/generated_input.rst"),
        ),
    ],
    ids=["generate-default", "generated-custom-grammar"],
)
def test_api_generate(args, inp, references):
    # generate parser
    parser_dir = api.generate(**args)

    # use generated parser to parse inp
    from input_parser import api as generated_api

    fr = generated_api.parse(inp)

    # Check final representation matches with reference
    ref_json = Path(references[0]).resolve()
    with ref_json.open("r") as ref:
        assert fr == json.loads(ref.read(), object_hook=as_complex)

    # Check generated documentation agrees with reference
    ref_rst = Path(references[1]).resolve()
    dumped = parser_dir / f"docs/{args['docfile']}"
    with ref_rst.open("r") as ref, dumped.open("r") as o:
        assert o.read() == ref.read()

    # clean up generated parser
    rmtree(parser_dir)
