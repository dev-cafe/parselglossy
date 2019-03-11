#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import guzzle_sphinx_theme

sys.path.insert(0, os.path.abspath('..'))

from parselglossy import __version__ as psversion  # isort:skip

# -- General configuration ---------------------------------------------

extensions = [
    'sphinx.ext.napoleon', 'sphinx.ext.viewcode', 'guzzle_sphinx_theme'
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'parselglossy'
copyright = u"2018, dev-cafe"
author = u"Roberto Di Remigio, Radovan Bast"
# The short X.Y version.
version = psversion
# The full version, including alpha/beta/rc tags.
release = psversion
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False

# -- Options for HTML output -------------------------------------------
html_title = "parselglossy Documentation"
html_short_title = "parselglossy {}".format(version)
html_show_sourcelink = False
html_sidebars = {
    '**':
    ['logo-text.html', 'globaltoc.html', 'localtoc.html', 'searchbox.html']
}
html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = 'guzzle_sphinx_theme'
html_theme_options = {
    # Set the name of the project to appear in the sidebar
    "project_nav_name": "parselglossy",
}
html_static_path = ['_static']
