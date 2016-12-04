# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    import pandas_plink
    version = pandas_plink.__version__
except ImportError:
    version = 'unknown'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
]
napoleon_google_docstring = True
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'pandas-plink'
copyright = '2016, Danilo Horta'
author = 'Danilo Horta'
release = version
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'default'
htmlhelp_basename = 'pandas-plinkdoc'
latex_elements = {}
latex_documents = [
    (master_doc, 'pandas-plink.tex', 'pandas-plink Documentation',
     'Danilo Horta', 'manual'),
]
man_pages = [
    (master_doc, 'pandas-plink', 'pandas-plink Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'pandas-plink', 'pandas-plink Documentation',
     author, 'pandas-plink', 'One line description of project.',
     'Miscellaneous'),
]
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'pandas': ('http://pandas-docs.github.io/pandas-docs-travis/', None)
}
