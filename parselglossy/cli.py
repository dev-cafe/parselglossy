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


import click

from . import __version__, api
from .utils import default_outfile


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
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    default=None,
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
        The output file. By default, save as ``<infile>_ir.json`` in the
        current working directory.
    grammar : str
        Which grammar to use.
    """

    if outfile is None:
        outfile = default_outfile(fname=infile, suffix="_ir.json")

    api.lex(infile=infile, grammar=grammar, ir_file=outfile)


@click.command(name="validate")
@click.argument(
    "infile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<infile>",
)
@click.option(
    "--outfile",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    default=None,
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
        The output file. Defaults to ``<infile>_fr.json`` in the current
        working directory.
    template : str
        Which validation template to use.
    """

    if outfile is None:
        outfile = default_outfile(fname=infile, suffix="_fr.json")

    api.validate(infile=infile, template=template, fr_file=outfile)


@click.command(name="parse")
@click.argument(
    "infile",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<infile>",
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<template>",
    help="which validation template to use",
)
@click.option(
    "--outfile",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    default=None,
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
    "--dump-ir/--no-dump-ir",
    default=False,
    help="whether to dump intermediate representation to JSON file",
    show_default=True,
    metavar="<dump_ir>",
)
def _parse(
    infile: str, template: str, outfile: str, grammar: str, dump_ir: bool
) -> None:
    """Parse input file.

    \b
    Parameters
    ----------
    infile : str
        The input file to be parsed.
    template : str
        Which validation template to use.
    outfile : str
        The output file. Defaults to ``<infile>_fr.json`` in the current working
        directory.
    grammar : str
        Which grammar to use.
    dump_ir : bool
        Whether to dump intermediate representation to file.
        False by default.

    \b
    Notes
    -----
    If requested, the intermediate representation is saved to
    ``<outfile>_ir.json`` in the current working directory.
    """

    if outfile is None:
        outfile = default_outfile(fname=infile, suffix="_fr.json")

    api.parse(
        infile=infile,
        template=template,
        outfile=outfile,
        grammar=grammar,
        dump_ir=dump_ir,
    )


@click.command(name="doc")
@click.argument(
    "template",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    metavar="<template>",
)
@click.option(
    "--outfile",
    type=click.Path(exists=False, dir_okay=False, resolve_path=True),
    default="input.rst",
    show_default=True,
    metavar="<outfile>",
    help="where to save the generated documentation",
)
@click.option(
    "--header",
    type=str,
    default="Input parameters",
    show_default=True,
    metavar="<header>",
    help="header for the documentation page",
)
def _doc(template: str, outfile: str, header: str):
    """Generate documentation from validation template.

    \b
    Parameters
    ----------
    template : str
        Which validation template to use.
    output : str
        Where to save the generated documentation.
        Defaults to ``input.rst`` in the current working directory.
    header : str
        Header for the documentation page.
        Defaults to ``Input parameters``.
    """

    if not outfile:
        outfile = "input.rst"

    api.document(template=template, outfile=outfile, header=header)


cli.add_command(_doc)
cli.add_command(_lex)
cli.add_command(_validate)
cli.add_command(_parse)
