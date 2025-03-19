# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as get_version
project = 'Hipersim'
copyright = '2024, DTU WIND AND ENERGY SYSTEMS'
author = 'Nikolay Dimitrov'
release = get_version('Hipersim')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "numpydoc",
    'nbsphinx',
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    # "sphinx_sitemap",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.ipynb_checkpoints/*.ipynb',
                    ]

# -- Options for nbsphinx -----------------------------------------------------

# Execute notebooks before conversion: 'always', 'never', 'auto' (default)
# We execute all notebooks, exclude the slow ones using 'exclude_patterns'
nbsphinx_execute = 'never'

# Use this kernel instead of the one stored in the notebook metadata:
#nbsphinx_kernel_name = 'python3'

# List of arguments to be passed to the kernel that executes the notebooks:
# nbsphinx_execute_arguments = []

# If True, the build process is continued even if an exception occurs:
#nbsphinx_allow_errors = True


# Controls when a cell will time out (defaults to 30; use -1 for no timeout):
nbsphinx_timeout = 180

# Default Pygments lexer for syntax highlighting in code cells:
#nbsphinx_codecell_lexer = 'ipython3'

# Width of input/output prompts used in CSS:
#nbsphinx_prompt_width = '8ex'

# If window is narrower than this, input/output prompts are on separate lines:
#nbsphinx_responsive_width = '700px'

# This is processed by Jinja2 and inserted before each notebook
nbsphinx_prolog = r"""
{% set docname = 'doc/' / env.doc2path(env.docname, base=None) %}


.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. nbinfo::

        :raw-html:`<a href="https://gitlab.windenergy.dtu.dk/HiperSim/hipersim/-/tree/master/{{ docname }}"><img alt="Edit on Gitlab" src="https://img.shields.io/badge/Edit%20on-Gitlab-blue?style=flat&logo=gitlab" style="vertical-align:text-bottom"></a>
        <a href="https://mybinder.org/v2/git/https%3A%2F%2Fgitlab.windenergy.dtu.dk%2FHiperSim%2Fhipersim.git/master?labpath={{ docname }}" target="_blank"><img alt="Launch with Binder" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`

"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
