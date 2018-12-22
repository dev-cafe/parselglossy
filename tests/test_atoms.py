#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `parselglossy` package."""

import itertools
import math

import pytest
from parselglossy import atoms


@pytest.mark.parametrize(
    'atom, test_input, expected',
    list(itertools.product([atoms.bool_t], atoms.truthy, [True])) + list(
        itertools.product([atoms.bool_t], atoms.falsey, [False])) +
    [(atoms.int_t, '42', 42), (atoms.int_t, '-42', -42),
     (atoms.float_t, F'{math.pi}', math.pi),
     (atoms.float_t, F'-{math.pi}', -math.pi),
     (atoms.float_t, F'{542.12335321:.12e}', 542.12335321),
     (atoms.float_t, F'{542.12335321:.12E}', 542.12335321),
     (atoms.str_t, 'fooffa', 'fooffa'),
     (atoms.complex_t, F'{math.pi} +{math.pi}*j', math.pi + math.pi * 1j),
     (atoms.complex_t, F'-{math.pi}+{math.pi}*j', -math.pi + math.pi * 1j),
     (atoms.complex_t, F'1 -1*j', 1 - 1j), (atoms.complex_t, F'+1-1*j', 1 - 1j),
     (atoms.complex_t, F'{math.e}*j', math.e * 1j),
     (atoms.data_t, (F'$raw\nH 0.0 0.0 0.0\nF 1.0 1.0 1.0\n$end'),
      ('raw', 'H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n')),
     (atoms.data_t, (F'$RAW\nH 0.0 0.0 0.0\nF 1.0 1.0 1.0\n$END'),
      ('RAW', 'H 0.0 0.0 0.0\nF 1.0 1.0 1.0\n'))])
def test_keyword(atom, test_input, expected):
    assert atom.parseString(test_input)[0] == expected
