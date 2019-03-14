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
"""Error-handling facilities."""

from pyparsing import ParseFatalException


class ValidationError(Exception):
    """Exception raised for invalid input files."""
    pass


class SpecificationError(Exception):
    """Exception raised for malformed validation template."""
    pass


class EmptyListError(ParseFatalException):
    """Exception raised by the parser for empty lists."""

    def __init__(self, s, loc, msg):
        super().__init__(s, loc, 'Empty lists not allowed \'{}\''.format(msg))


def raise_pyparsing_exception(exception, s, loc, toks):
    """Helper function to raise exceptions as parse actions.

    Parameters
    ----------
    exception:
        Exception to be thrown.
    s: str
        The original parse string.
    loc: int
        Location is `s` where the match started.
    toks: ParseResults
        List of matched tokens.

    Raises
    ------
    exception

    Notes
    -----
    See: https://stackoverflow.com/a/13409786
    """
    raise exception(s, loc, toks[0])


def raise_pyparsing_empty_list(s, loc, toks):
    """Helper function to raise empty list exception as parse action.

    Parameters
    ----------
    s: str
        The original parse string.
    loc: int
        Location is `s` where the match started.
    toks: ParseResults
        List of matched tokens.

    Raises
    ------
    exception
    """
    raise_pyparsing_exception(EmptyListError, s, loc, toks)
