# -*- coding: utf-8 -*-

import pathlib
import sys

import guzzle_sphinx_theme
from sphinx.ext.apidoc import main

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

from parselglossy import __version__ as _version  # isort:skip
from parselglossy import __author__ as _author  # isort:skip

# -- General configuration ---------------------------------------------

extensions = ["sphinx.ext.napoleon", "sphinx.ext.viewcode", "guzzle_sphinx_theme"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = u"parselglossy"
copyright = u"2018, dev-cafe"
author = _author
# The short X.Y version.
version = _version
# The full version, including alpha/beta/rc tags.
release = _version
language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False

# -- Options for HTML output -------------------------------------------
html_title = "parselglossy Documentation"
html_short_title = f"parselglossy {version}"
html_show_sourcelink = False
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = "guzzle_sphinx_theme"
html_theme_options = {
    # Set the name of the project to appear in the sidebar
    "project_nav_name": "parselglossy"
}


def run_apidoc(_):
    cur_dir = pathlib.Path(__file__).parent
    module = cur_dir.parent / project
    main(["-e", "-o", str(cur_dir), str(module), "--force"])


def setup(app):
    app.connect("builder-inited", run_apidoc)
