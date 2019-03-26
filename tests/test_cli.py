#!/usr/bin/env python

#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2019 Roberto Di Remigio, Radovan Bast, and contributors.
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

# -*- coding: utf-8 -*-
"""Tests for `parselglossy` package."""

import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from parselglossy import __version__, cli
from parselglossy.utils import as_complex


@pytest.mark.parametrize(
    "switch,expected",
    [
        ([], "Console script for parselglossy"),
        (["--version"], "parselglossy, version {}".format(__version__)),
        (["--help"], r"--help\s+Show this message and exit"),
    ],
    ids=["plain", "version", "help"],
)
def test_cli_switches(switch, expected):
    runner = CliRunner()
    result = runner.invoke(cli.cli, switch)
    assert result.exit_code == 0
    assert re.search(expected, result.output, re.M) is not None


@pytest.mark.parametrize(
    "command,out,reference",
    [
        (
            ["lex", "tests/cli/standard.inp"],
            "standard_ir.json",
            "tests/ref/standard_ir.json",
        ),
        (
            [
                "lex",
                "tests/cli/getkw.inp",
                "--outfile",
                "lex_ir.json",
                "--grammar",
                "getkw",
            ],
            "lex_ir.json",
            "tests/ref/getkw_ir.json",
        ),
        (
            [
                "validate",
                "tests/ref/scf_ir.json",
                "--template",
                "tests/validation/overall/template.yml",
            ],
            "scf_ir_fr.json",
            "tests/ref/scf_fr.json",
        ),
        (
            [
                "validate",
                "tests/ref/scf_ir.json",
                "--template",
                "tests/validation/overall/template.yml",
                "--outfile",
                "scf_fr.json",
            ],
            "scf_fr.json",
            "tests/ref/scf_fr.json",
        ),
        (
            [
                "parse",
                "tests/cli/scf.inp",
                "--template",
                "tests/validation/overall/template.yml",
            ],
            "scf_fr.json",
            "tests/ref/scf_fr.json",
        ),
        (
            [
                "parse",
                "tests/cli/scf.inp",
                "--template",
                "tests/validation/overall/template.yml",
                "--outfile",
                "scf_fr.json",
            ],
            "scf_fr.json",
            "tests/ref/scf_fr.json",
        ),
        (
            [
                "parse",
                "tests/cli/scf.inp",
                "--template",
                "tests/validation/overall/template.yml",
                "--grammar",
                "standard",
                "--dump-ir",
            ],
            "scf_fr.json",
            "tests/ref/scf_fr.json",
        ),
        (["doc", "tests/cli/docs_template.yml"], "input.rst", "tests/ref/input.rst"),
        (
            ["doc", "tests/cli/docs_template.yml", "--outfile", "input.rst"],
            "input.rst",
            "tests/ref/input.rst",
        ),
        (
            [
                "doc",
                "tests/cli/docs_template.yml",
                "--outfile",
                "input.rst",
                "--header",
                "Dwigt Rortugal's guide to input parameters",
            ],
            "input.rst",
            "tests/ref/dwigt.rst",
        ),
    ],
    ids=[
        "lex-default",
        "lex-getkw-w-outfile",
        "validate-default",
        "validate-w-outfile",
        "parse-default",
        "parse-w-outfile",
        "parse-w-dumpir",
        "doc-default",
        "doc-w-outfile",
        "doc-w-header",
    ],
)
def test_cli_commands(command, out, reference):
    runner = CliRunner()
    result = runner.invoke(cli.cli, command)
    assert result.exit_code == 0

    # Check dumped file matches with reference
    dumped = Path(out).resolve()
    ref = Path(reference)
    if command[0] == "doc":
        with ref.open("r") as ref, dumped.open("r") as o:
            assert o.read() == ref.read()
    else:
        with ref.open("r") as ref, dumped.open("r") as o:
            assert json.loads(o.read(), object_hook=as_complex) == json.loads(
                ref.read(), object_hook=as_complex
            )

    # Clean up file
    dumped.unlink()
