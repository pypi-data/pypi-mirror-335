"""Sohinx config."""

import logstruct

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "logstruct"
copyright = "2024-, Karoline Pauls"
author = "Karoline Pauls"
version = logstruct.__version__ if "post" not in logstruct.__version__ else ""
release = logstruct.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxcontrib.programoutput",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
default_role = "any"
nitpicky = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = [
    "theme-override.css",
]

html_context = {
    "display_gitlab": True,
    "gitlab_user": "karolinepauls",  # Username
    "gitlab_repo": "logstruct",  # Repo name
    "gitlab_version": "master",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
}

programoutput_prompt_template = "{output}"
