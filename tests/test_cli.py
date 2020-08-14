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
import re
import subprocess
from pathlib import Path
from shutil import rmtree

import pytest
from click.testing import CliRunner

from parselglossy import __version__, cli
from parselglossy.utils import as_complex


@pytest.mark.parametrize(
    "switch,expected",
    [
        ([], "Console script for parselglossy"),
        (["--version"], f"parselglossy, version {__version__}"),
        (["--help"], r"--help\s+Show this message and exit"),
    ],
    ids=["plain", "version", "help"],
)
def test_cli_switches(switch, expected):
    runner = CliRunner()
    result = runner.invoke(cli.cli, switch)
    assert result.exit_code == 0, f"{result.output}"
    assert re.search(expected, result.output, re.M) is not None


@pytest.mark.parametrize(
    "command,inp,references",
    [
        (
            [
                "generate",
                "--template",
                "tests/validation/overall/template.yml",
                "--target",
                "fufamu",
                "--grammar",
                "standard",
                "--docfile",
                "foo.rst",
            ],
            "tests/api/scf.inp",
            ("tests/ref/scf_fr.json", "tests/ref/generated_input.rst"),
        ),
        (
            [
                "generate",
                "--template",
                "tests/validation/overall/template.yml",
                "--target",
                "fufamu",
                "-g",
                f"{Path(__file__).parents[1].absolute() / 'parselglossy/grammars/atoms.py'}",
                "-g",
                f"{Path(__file__).parents[1].absolute() / 'parselglossy/grammars/getkw.py'}",
                "--tokenize",
                "from . import getkw; lexer = getkw.grammar(has_complex=True); ir = lexer.parseString(in_str).asDict()\n",
                "--docfile",
                "babar.rst",
            ],
            "tests/api/scf.inp",
            ("tests/ref/scf_fr.json", "tests/ref/generated_input.rst"),
        ),
    ],
    ids=["generate-default", "generated-custom-grammar"],
)
def test_cli_generate(command, inp, references):
    runner = CliRunner()
    result = runner.invoke(cli.cli, command)
    assert result.exit_code == 0, f"{result.output}"

    parser_dir = Path.cwd() / f"{command[4]}"

    # Check generated documentation agrees with reference
    ref_rst = Path(references[1]).resolve()
    dumped = parser_dir / f"docs/{command[-1]}"
    with ref_rst.open("r") as ref, dumped.open("r") as o:
        assert o.read() == ref.read()

    # write a front-end using the generated module
    front = Path("dwigt.py")
    with front.open("w") as buf:
        buf.write(f"from {command[4]} import cli\ncli.cli()")

    # spawn a subprocess to run the generated parser's CLI and parse an input file
    subprocess.run(["python", "dwigt.py", inp])

    # Check final representation matches with reference
    ref_json = Path(references[0]).resolve()
    out = Path("scf_fr.json").resolve()
    with ref_json.open("r") as ref, out.open("r") as o:
        assert json.loads(o.read(), object_hook=as_complex) == json.loads(
            ref.read(), object_hook=as_complex
        )

    # delete front-end and parsed output
    front.unlink()
    out.unlink()

    # clean up generated parser
    rmtree(parser_dir)
