import sphinx_rtd_theme


def get_version():
    import pandas_plink

    return pandas_plink.__version__


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
# Change to True when developing it.
autosummary_generate = False
autosectionlabel_prefix_document = True
napoleon_numpy_docstring = True

source_suffix = ".rst"

master_doc = "index"

project = "pandas-plink"
copyright = "2018, Danilo Horta"
author = "Danilo Horta"

version = get_version()
release = version

language = None

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "conf.py"]

pygments_style = "default"

todo_include_todos = False

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_sidebars = {"**": ["relations.html", "searchbox.html"]}

htmlhelp_basename = "pandas-plinkdoc"

man_pages = [(master_doc, "pandas-plink", "pandas-plink Documentation", [author], 1)]

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

epub_exclude_files = ["search.html"]

intersphinx_mapping = {
    "python": ("http://docs.python.org/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "xarray": ("http://xarray.pydata.org/en/stable/", None),
}
