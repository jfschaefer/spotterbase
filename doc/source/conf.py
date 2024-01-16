# Sphinx configuration file

project = 'spotterbase'
copyright = '2022, Jan Frederik Schaefer'
author = 'Jan Frederik Schaefer'

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from spotterbase import __version__
release = __version__

extensions = [
        'sphinx.ext.autodoc',
        'sphinxcontrib.apidoc',
        'spotterbase.utils.sphinx_rdf',
        'spotterbase.utils.sphinx_warnings',
        'sphinx.ext.todo',
]

apidoc_module_dir = str(Path(__file__).parent.parent.parent/'spotterbase')
apidoc_output_dir = 'apidocs'

autodoc_typehints_format = 'short'
autodoc_preserve_defaults = True
autodoc_type_aliases = {
    
}

templates_path = ['_templates']
exclude_patterns = ['apidocs/modules.rst']

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
