# Copyright (c) [2024-2025] [Laszlo Oroszlany, Daniel Pozsar]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "grogupy documentation"
copyright = "2024, grogupy"
author = "Author"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


# -- Built in extensions -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/index.html
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinxcontrib.bibtex",
    "rst2pdf.pdfbuilder",
    "nbsphinx",
]

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = False
napoleon_use_rtype = False
napoleon_use_ivar = False
napoleon_preprocess_types = True
# Using attr_annotations = True ensures that
# autodoc_type_aliases is in effect.
# Then there is no need to use napoleon_type_aliases.
napoleon_attr_annotations = True


autosummary_generate = True

# Add __init__ classes to the documentation
autoclass_content = "class"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "special-members": "__call__",
    "inherited-members": True,
    "show-inheritance": True,
}
# alphabetical | groupwise | bysource
# How automodule + autoclass orders content.
# Right now, the current way sisl documents things
# is basically groupwise. So lets be explicit
autodoc_member_order = "groupwise"

# Show type-hints in both the signature
# and in the variable list
autodoc_typehints = "signature"

# typehints only shows the minimal class, instead
# of full module paths
# The linkage is still problematic, and a known issue:
#  https://github.com/sphinx-doc/sphinx/issues/10455
# autodoc will likely get a rewrite. Until then..
autodoc_typehints_format = "short"

# Do not evaluate things that are defaulted in arguments.
# Show them *as-is*.
autodoc_preserve_defaults = True

# Automatically create the autodoc_type_aliases
# This is handy for commonly used terminologies.
# It currently puts everything into a `<>` which
# is sub-optimal (i.e. one cannot do "`umpy.ndarray` or `any`")
# Perhaps just a small tweak and it works.
autodoc_type_aliases = {
    # general terms
    "array-like": "numpy.ndarray",
    "array_like": "numpy.ndarray",
    "int-like": "int or numpy.ndarray",
    "float-like": "float or numpy.ndarray",
    "sequence": "sequence",
    "np.ndarray": "numpy.ndarray",
    "ndarray": "numpy.ndarray",
}


# Add any extra style files that we need
html_css_files = [
    "css/custom_styles.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css",
]

# If false, no index is generated.
html_use_modindex = True
html_use_index = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "grogupy"

# for bibliography
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "plain"
master_doc = "index"
bibtex_encoding = "latin"
bibtex_tooltips = True

# pdf documentation
pdf_documents = [
    ("index", "grogupy_documentation", "grogupy documentation", "Daniel Pozsar"),
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
