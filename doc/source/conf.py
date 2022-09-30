# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'spotterbase'
copyright = '2022, Jan Frederik Schaefer'
author = 'Jan Frederik Schaefer'

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from spotterbase import __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.apidoc']

apidoc_module_dir = str(Path(__file__).parent.parent.parent/'spotterbase')
apidoc_output_dir = 'apidocs'

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
