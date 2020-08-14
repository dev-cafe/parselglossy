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

"""Console script for parselglossy."""

from pathlib import Path
from typing import List, Union

import click

from . import __version__
from .api import generate


@click.group()
@click.version_option(prog_name="parselglossy", version=__version__)
def cli(args=None):
    """Console script for parselglossy."""
    return 0


@click.command(name="generate")
@click.option(
    "--template",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    metavar="<template>",
    help="which validation template to use",
)
@click.option(
    "--target",
    type=click.Path(exists=False, dir_okay=True, resolve_path=True),
    default="input_parser",
    show_default=True,
    metavar="<target>",
    help="name of the generated Python module",
)
@click.option(
    "--grammar",
    "-g",
    default=["standard"],
    multiple=True,
    show_default=True,
    metavar="<grammar>",
    help="which grammar to use, specify multiple times for multiple external files",
)
@click.option(
    "--tokenize",
    type=str,
    default=None,
    metavar="<tokenize>",
    help="tokenizing commands for the custom grammar",
)
@click.option(
    "--docfile",
    type=str,
    default="input.rst",
    show_default=True,
    metavar="<header>",
    help="name for the generated documentation file",
)
@click.option(
    "--doc-header",
    type=str,
    default="Input parameters",
    show_default=True,
    metavar="<header>",
    help="header for the documentation page",
)
def _generate(
    template: str,
    target: str,
    grammar: Union[str, List[str]],
    tokenize: str,
    docfile: str,
    doc_header: str,
):
    """Generate parser Python module and documentation from a grammar and a
    validation template.

    \b
    Parameters
    ----------
    template : str
        Which validation template to use.
    target : str
        Name of the generated Python moduel.
        Defaults to ``input_parameters`` in the current working directory.
    grammar : str
        Which grammar to use, can be a list of files.
        Defaults to ``standard``.
    tokenize : str
        Tokenizing commands to run with the custom grammar.
        Defaults to ``None``.
    docfile : str
        The name of the documentation file for the input.
        Defaults to `input.rst`.
    doc_header : str
        Header for the documentation page.
        Defaults to ``Input parameters``.
    """

    if not docfile:
        docfile = "input.rst"

    if "standard" in grammar or "getkw" in grammar:
        grammar_ = grammar[0]
    else:
        grammar_ = [Path(_).resolve() for _ in grammar]  # type: ignore

    generate(
        template=template,
        where=target,
        grammar=grammar_,
        tokenize=tokenize,
        docfile=docfile,
        doc_header=doc_header,
    )


cli.add_command(_generate)
