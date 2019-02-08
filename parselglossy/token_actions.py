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
# Roberto Di Remigio, and contributors. OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# parselglossy library, see: <http://parselglossy.readthedocs.io/>
#

import logging


def to_bool(toks):
    truthy = ['1', 'TRUE', 'ON', 'YES', 'Y']
    falsey = ['0', 'FALSE', 'OFF', 'NO', 'N']

    defined = False
    if toks[0] is None:
        defined = False
    elif toks[0].upper() in falsey:
        defined = False
    elif toks[0].upper() in truthy:
        defined = True
    else:
        defined = False

    return defined


def to_int(toks):
    return int(toks[0])


def to_float(toks):
    return float(toks[0])


def to_str(toks):
    return str(toks[0])


def to_scalar(token):
    logging.info('token to_scalar')
    logging.info(F'key = {token[0]}\n scalar = {token[1]}')
    return tuple(token)


def to_array(token):
    logging.info('token to_array')
    logging.info(F'key = {token[0]}\n array = {token[1:]}')
    return (token[0], token[1:])


def to_data(token):
    logging.info('token to_data')
    logging.info(F'key = {token[0]}\n data = {token[1]}')
    return (token[0], token[1])


def to_section(token):
    logging.info('token to_section')
    logging.info(F'key = {token[0]}\n section = {token[1:]}\n')
    print(F'token to_section {token}')
    print(F'key = {token[0]}\n section = {token[1:]}\n')
    print(F'{token[0]}<{token[1:]}>')
    #return (token[0], token[1])


def end_of_section(token):
    print(F'gotcha!')


def parse_error(s, t, d, err):
    """
    Raises error from pyparsing
    """
    raise err
