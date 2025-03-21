Regolith System Template
========================

A Python package that powers the `System Template Regolith Filter <https://system-template-docs.readthedocs.io/en/stable/>`_ and provides a command-line tool for creating projects based on templates defined using the System Template syntax.

Installation
-------------

.. code-block:: bash

   pip install regolith-system-template

Command-Line Tool
-----------------

This package adds the :code:`system-template` command-line tool.

Before using the tool, set the :code:`REGOLITH_SYSTEM_TEMPLATE` environment variable to specify the directory where your templates are stored. Templates should be organized into subfolders within this directory, using the same format as the Regolith filter.

You can verify that :code:`system-template` is set up correctly by running the following command:

.. code-block:: bash

   system-template list

This will list all available templates in the :code:`REGOLITH_SYSTEM_TEMPLATE` directory.

To use a template, run:

.. code-block:: bash

   system-template run <template-name>

This will create a new system based on the template named :code:`<template-name>`.

Flags
-----

- :code:`--systems-path` - Instead of using the :code:`REGOLITH_SYSTEM_TEMPLATE` environment variable, specify the path to the template directory with this flag.
- :code:`--scope-path` - Provide the path to a file containing the scope for template execution. This is useful when executing a template within a Regolith project. In that case, use this flag to specify the project's global Regolith scope.
- :code:`--scope` - Define the scope in JSON format. When using System Template as a Regolith filter, it uses the scope defined in :code:`config.json`. This flag allows you to provide a replacement for that scope when running the command-line tool.
- :code:`--allow-non-empty` - By default, the tool does not run in non-empty directories. Use this flag to override this behavior.
- :code:`--replacements` - Provide a JSON object with key-value pairs to replace text in the template files. This corresponds to the :code:`replacements` setting in :code:`config.json` when using System Template as a Regolith filter.

For additional help, use the :code:`--help` flag.

Unlike the Regolith filter, the command-line tool is not restricted to exporting only to the :code:`RP/`, :code:`BP/`, and :code:`data/` directories.
