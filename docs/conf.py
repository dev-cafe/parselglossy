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

import pathlib
import sys

from sphinx.ext.apidoc import main

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

from parselglossy import __version__ as _version  # isort:skip
from parselglossy import __author__ as _author  # isort:skip

# -- General configuration ---------------------------------------------

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "parselglossy"
copyright = "2018, dev-cafe"
author = _author
# The short X.Y version.
version = _version
# The full version, including alpha/beta/rc tags.
release = _version
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
# Furo-specific option
pygments_dark_style = "monokai"
todo_include_todos = False

# -- Options for HTML output -------------------------------------------
html_title = "parselglossy"
html_short_title = f"parselglossy {version}"
html_show_sourcelink = False
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/dev-cafe/parselglossy/",
    "source_branch": "master",
    "source_directory": "docs/",
}


def run_apidoc(_):
    cur_dir = pathlib.Path(__file__).parent
    module = cur_dir.parent / project
    main(["-e", "-o", str(cur_dir), str(module), "--force"])


def setup(app):
    app.connect("builder-inited", run_apidoc)
