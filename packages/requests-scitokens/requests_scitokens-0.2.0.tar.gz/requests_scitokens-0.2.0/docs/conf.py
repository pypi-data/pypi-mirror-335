# Copyright (C) 2024-2025 Cardiff University

from datetime import (
    datetime,
    timezone,
)

from requests_scitokens import __version__ as requests_scitokens_version

# -- Project information -------------

project = "requests-scitokens"
copyright = f"{datetime.now(tz=timezone.utc).date().year}, Cardiff University"
author = "Duncan Macleod"

# The full version, including alpha/beta/rc tags
release = requests_scitokens_version
version = release.split("+", 1)[0]


# -- General configuration -----------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output ---------

html_theme = "furo"
html_title = f"{project} {version}"

pygments_dark_style = "monokai"

default_role = "obj"

# -- Extensions ----------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_automodapi.automodapi",
    "sphinx_copybutton",
    "sphinx_design",
]

# -- intersphinx

intersphinx_mapping = {name: (url, None) for name, url in {
    "python": "https://docs.python.org/3/",
    "requests": "https://requests.readthedocs.io/en/stable/",
    "scitokens": "https://scitokens.readthedocs.io/en/latest/",
}.items()}

# -- napoleon

napoleon_use_rtype = False

# -- automodapi

automodapi_inherited_members = False

# -- copybutton

copybutton_prompt_text = " |".join((  # noqa: FLY002
    ">>>",
    r"\.\.\.",
    r"\$"
    r"In \[\d*\]:",
    r" {2,5}\.\.\.:",
    " {5,8}: ",
))
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
