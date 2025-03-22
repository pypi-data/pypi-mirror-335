Welcome to DiffScope's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api
   examples
   contributing
   changelog

DiffScope: Function-level Git Commit Analysis
============================================

DiffScope is a tool for analyzing Git commits at the function level, identifying which functions were modified, added, or deleted in each commit.

Features
--------

* Analyze GitHub commits at both file and function levels
* Identify exactly which functions were changed in each commit
* Detect function changes including signature, body, and docstring changes
* Supports multiple programming languages using tree-sitter
* Simple API for integration into other tools

Installation
-----------

.. code-block:: bash

   pip install diffscope

Basic Usage
----------

.. code-block:: python

   from diffscope import analyze_commit

   # Analyze a GitHub commit
   result = analyze_commit("https://github.com/owner/repo/commit/sha")

   # Print file-level changes
   print(f"Files changed: {len(result.modified_files)}")
   for file in result.modified_files:
       print(f"- {file.filename}: +{file.additions} -{file.deletions}")

   # Print function-level changes
   print(f"Functions changed: {len(result.modified_functions)}")
   for function in result.modified_functions:
       print(f"- {function.name} in {function.file}: {function.change_type}")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 