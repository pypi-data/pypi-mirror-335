"""sphinx-ifelse documentation build configuration file"""

import datetime
import os

from typing import Dict, List, Tuple

from sphinx import __version__ as sphinx_version
print ('sphinx version: ' + str(sphinx_version))

from sphinx_ifelse import __version__ as sphinx_ifelse_version
print ('sphinx_ifelse version: ' + str(sphinx_ifelse_version))

#from sphinx_needs import __version__ as sphinx_needs_version
#print ('sphinx-needs version: ' + str(sphinx_needs_version))

from sphinx_ifelse.utils import tags2dict
# -- General configuration ------------------------------------------------

# General information about the project.
project = "Sphinx-IfElse"
now = datetime.datetime.now()
copyright = f"2025-{now.year}, PhilipPartsch"
author = "PhilipPartsch"

master_doc = "index"
language = "en"

version = release = sphinx_ifelse_version

# -- General configuration
on_rtd = os.environ.get("READTHEDOCS") == "True"

extensions = [
   'sphinx_ifelse',
]

# -- extension configuration: ifelse

ifelse_variants = {
   'html': True,
   'latex': False,
   'pdf': False,
   'epub': False,
   'l1': 3,
   'l2': 3,
   'l3': 3,
}
