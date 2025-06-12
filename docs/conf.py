# Configuration file for the Sphinx documentation builder.
#
import os
import sys

# Set dummy environment variables for Pydantic settings to avoid validation errors during build
os.environ["MAIL_SERVER"] = "smtp.example.com"
os.environ["MAIL_PORT"] = "587"
os.environ["MAIL_USERNAME"] = "user"
os.environ["MAIL_PASSWORD"] = "password"

sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('..'))
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'fastapi-tdd'
copyright = '2025, Carol'
author = 'Carol'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    # 'autodoc_pydantic',
    'sphinx_rtd_theme',
    'sphinx.ext.autosummary', # Ensure this IS in extensions
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_autosummary/**', '**/migrations/**']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for Napoleon ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = False # Ensure this is False (as per step 1.e)

# -- Options for autodoc / typehints ------------------------------------------
autodoc_typehints = 'description' # Ensure this is 'description' (as per step 1.e)
typehints_fully_qualified = False # Ensure this is False (as per step 1.e)
typehints_merge_getAsDouble = True # Ensure this is True (as per step 1.e)
# autodoc_mock_imports = ["pydantic", "sqlalchemy"]
autosummary_generate = True # Set to True as per step 1.c
# Ensure no autodoc_pydantic specific configurations
