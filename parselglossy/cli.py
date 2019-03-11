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


@click.group()
def cli(args=None):
    """Console script for parselglossy."""
    return 0


@click.command()
@click.option(
    '--dump-ir/--no-dump-ir',
    default=False,
    help='serialize IR to JSON file',
    metavar='<dumpir>')
@click.argument('infile', metavar='<infile>')
def lex(dumpir, infile):
    """Run lexer to obtain JSON intermediate representation.

    \b
    Parameters
    ----------
    dumpir : bool
             Whether to serialize IR to JSON. Location and name of file are
             determined based on the input file.
    infile : str or path
            The input file to be parsed.
    """
    ir = {}
    return ir


@click.command()
@click.option(
    '--dump-fr/--no-dump-fr',
    default=False,
    help='serialize FR to JSON file',
    metavar='<dumpfr>')
def validate(dumpfr, ir):
    """Validate intermediate representation into final representation.

    \b
    Parameters
    ----------
    dumpir : bool
             Whether to serialize FR to JSON. Location and name of file are
             determined based on the input file.
    ir : dict
         Intermediate representation of the input file.
    """
    fr = {}
    return fr


@click.command()
@click.option(
    '--dump/--no-dump',
    default=False,
    help='serialize parsed input to JSON file',
    metavar='<dump>')
@click.argument('infile', metavar='<infile>')
def parse(dump, infile):
    """Parse input file.

    \b
    Parameters
    ----------
    dumpir : bool
             Whether to serialize parsed input to JSON. Location and name of file are
             determined based on the input file.
    infile : str or path
            The input file to be parsed.
    """
    ir = lex(infile, dump)
    fr = validate(dump, ir)
    return fr


@click.command()
@click.option('--doc-type', type=click.Choice(['md', 'rst', 'tex']))
def doc(doctype):
    """Generate documentation from validation specs.

    \b
    Parameters
    ----------
    doctype : str
              Format of the generated documentation.
              Valid choices are `md`, `rst`, and `tex`.
    """
    pass


cli.add_command(lex)
cli.add_command(validate)
cli.add_command(parse)
cli.add_command(doc)
