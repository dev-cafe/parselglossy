#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2018 Roberto Di Remigio, and contributors.
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

from pyparsing import (Combine, Dict, Forward, Group, Literal, ParseException,
                       Regex, SkipTo, StringEnd, Word, ZeroOrMore, alphanums,
                       alphas, delimitedList, line, lineno, pythonStyleComment,
                       quotedString, removeQuotes)

from . import token_actions


def BNF():
    """
    Standard grammar, reminiscent of Getkw
    """
    sect_begin = Literal("{").suppress()
    sect_end = Literal("}").suppress()
    array_begin = Literal("[").suppress()
    array_end = Literal("]").suppress()
    tag_begin = Literal("<").suppress()
    tag_end = Literal(">").suppress()
    eql = Literal("=").suppress()
    dmark = Literal('$').suppress()
    end_data = Literal('$end').suppress()
    prtable = alphanums + r'!$%&*+-./<>?@^_|~'
    int_t = Regex('[-]?\d+')
    float_t = Regex('-?\d+\.\d*([eE]?[+-]?\d+)?')
    bool_t = Regex('([Yy]es|[Nn]o|[Tt]rue|[Ff]alse|[Oo]n|[Oo]ff)')

    # Helper definitions
    kstr = quotedString.setParseAction(
        removeQuotes) ^ float_t ^ int_t ^ bool_t ^ Word(prtable)
    name = Word(alphas + "_", alphanums + "_")
    vec = array_begin + delimitedList(
        float_t ^ int_t ^ bool_t ^ Word(prtable) ^ Literal("\n").suppress() ^
        quotedString.setParseAction(removeQuotes)) + array_end
    sect = name + sect_begin
    tag_sect = name + Group(tag_begin + name + tag_end) + sect_begin

    # Grammar
    keyword = name + eql + kstr
    vector = name + eql + vec
    data = Combine(dmark + name) + SkipTo(end_data) + end_data
    section = Forward()
    sect_def = (sect | tag_sect)
    input = section | data | vector | keyword
    section << sect_def + ZeroOrMore(input) + sect_end

    # Parsing actions
    int_t.setParseAction(token_actions.to_int)
    float_t.setParseAction(token_actions.to_float)
    bool_t.setParseAction(token_actions.to_bool)
    keyword.setParseAction(token_actions.to_scalar)
    vector.setParseAction(token_actions.to_array)
    data.setParseAction(token_actions.to_data)
    sect.setParseAction(token_actions.to_section)
    #sect.setParseAction(self.add_sect)
    #tag_sect.setParseAction(self.add_sect)
    #sect_end.setParseAction(self.pop_sect)

    bnf = ZeroOrMore(input) + StringEnd().setFailAction(
        token_actions.parse_error)
    bnf.ignore(pythonStyleComment)

    return Dict(bnf)
