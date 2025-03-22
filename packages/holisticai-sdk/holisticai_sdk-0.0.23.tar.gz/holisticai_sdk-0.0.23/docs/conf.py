# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Holisticai-SDK'
copyright = '2025, Holistic AI'
author = 'Holistic AI'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    'sphinx.ext.viewcode',
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    #"sphinx.ext.linkcode",
    "sphinx.ext.mathjax",
    #"sphinx_gallery.gen_gallery",
    #"sphinx_autodoc_typehints",
    "nbsphinx",
    "sphinx_copybutton",
    "sphinx_design",
    #"sphinx_prompt",
    #"numpydoc",
    "matplotlib.sphinxext.plot_directive",
    "sphinx_togglebutton",
    "sphinxcontrib.youtube",
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}


nbsphinx_allow_errors = True  # Permitir errores en los notebooks
nbsphinx_execute = 'never'  # Puede ser 'auto', 'always', o 'never'

html_show_sourcelink = False
# autodoc options
autodoc_default_options = {"members": True, "inherited-members": False}

# Turn on autosummary
autosummary_generate = True


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_logo = "_static/images/hai_logo.svg"
html_favicon = "_static/images/holistic_ai.png"

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

# Custom css
html_css_files = [
    "css/custom_style.css",
]