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
"""Console script for parselglossy."""

import json
from pathlib import Path

import click

from . import __version__, api
from .utils import ComplexEncoder, as_complex, read_yaml_file


@click.group()
@click.version_option(prog_name="parselglossy", version=__version__)
def cli(args=None):
    """Console script for parselglossy."""
    return 0


@click.command(name="lex")
@click.argument(
    "infile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<infile>",
)
@click.option(
    "--outfile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="name or path for the lexed output JSON file",
    metavar="<outfile>",
)
@click.option(
    "--grammar",
    default="standard",
    type=click.Choice(["standard", "getkw"]),
    show_default=True,
    help="which grammar to use",
    metavar="<grammar>",
)
def _lex(infile: str, outfile: str, grammar: str) -> None:
    """Run lexer and dump intermediate representation to JSON.

    \b
    Parameters
    ----------
    infile : str
        The input file to be parsed.
    outfile : str
        The output file. Defaults to <infile>_ir.json
    grammar : str
        Which grammar to use.
    """

    if not outfile:
        outfile = infile.rsplit(".", 1)[0] + "_ir.json"

    api.lex(infile=infile, grammar=grammar, ir_file=outfile)


@click.command(name="validate")
@click.argument(
    "infile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<infile>",
)
@click.option(
    "--outfile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    default="",
    help="name or path for the validated output JSON file",
    metavar="<outfile>",
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<template>",
    help="which validation template to use",
)
def _validate(infile: str, outfile: str, template: str) -> None:
    """Validate intermediate representation into final representation.

    \b
    Parameters
    ----------
    infile : str
        The input file to be parsed.
    outfile : str
        The output file. Defaults to <infile>_fr.json
    template : str
        Which validation template to use.
    """

    if not outfile:
        outfile = infile.rsplit(".", 1)[0] + "_fr.json"

    api.validate(infile=infile, outfile=outfile, template=template)


@click.command(name="parse")
@click.argument(
    "infile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<infile>",
)
@click.option(
    "--outfile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    default="",
    help="name or path for the parsed JSON output file",
    metavar="<outfile>",
)
@click.option(
    "--grammar",
    default="standard",
    type=click.Choice(["standard", "getkw"]),
    show_default=True,
    help="which grammar to use",
    metavar="<grammar>",
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<template>",
    help="which validation template to use",
)
@click.option(
    "--dump-ir/--no-dump-ir",
    default=False,
    help="whether to dump intermediate representation to JSON file",
    show_default=True,
    metavar="<dumpir>",
)
def _parse(
    infile: str, outfile: str, grammar: str, template: str, dumpir: bool
) -> None:
    """Parse input file.

    \b
    Parameters
    ----------
    infile : str
        The input file to be parsed.
    outfile : str
        The output file. Defaults to <infile>_fr.json
    grammar : str
        Which grammar to use.
    template : str
        Which validation template to use.

    \b
    Notes
    -----
    The intermediate representation is saved to <outfile>_ir.json
    """

    if not outfile:
        outfile = infile.rsplit(".", 1)[0] + "_fr.json"

    api.parse(
        infile=infile,
        outfile=outfile,
        grammar=grammar,
        template=template,
        dump_ir=dumpir,
    )


@click.command(name="doc")
@click.option(
    "--doc-type",
    default="rst",
    type=click.Choice(["md", "rst", "tex"]),
    show_default=True,
    help="format for the autogenerated documentation",
    metavar="<doctype>",
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<template>",
    help="which validation template to use",
)
def _doc(doctype: str):
    """Generate documentation from validation template.

    \b
    Parameters
    ----------
    doctype : str
        Format of the generated documentation.
        Valid choices are ``md``, ``rst``, and ``tex``. Defaults to ``rst``.
    template : str
        Which validation template to use.
    """
    raise NotImplementedError("Coming soon!")


cli.add_command(_doc)
cli.add_command(_lex)
cli.add_command(_validate)
cli.add_command(_parse)
