.. SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
..
.. SPDX-License-Identifier: CC-BY-4.0

.. start-badges

|python-versions| |pypi| |license| |reuse-status| |rtd-status| |pipeline-status|

.. |pypi| image:: https://img.shields.io/pypi/v/axonometry?label=PyPI&logo=pypi&color=blue
   :target: https://pypi.org/project/axonometry/

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/axonometry.svg
   :target: https://pypi.org/project/axonometry/

.. |license| image:: https://img.shields.io/pypi/l/axonometry?color=blue
   :target: https://axonometry.readthedocs.io/en/latest/license.html

.. |reuse-status| image:: https://api.reuse.software/badge/codeberg.org/mononym/axonometry
   :target: https://api.reuse.software/info/codeberg.org/mononym/axonometry

.. |rtd-status| image:: https://img.shields.io/readthedocs/axonometry?label=Read%20the%20Docs&logo=read-the-docs
   :target: https://axonometry.readthedocs.io/en/latest/

.. |pipeline-status| image:: https://ci.codeberg.org/api/badges/14144/status.svg?branch=beta
   :target: https://ci.codeberg.org/repos/14144/branches/beta

.. end-badges

Contents
^^^^^^^^

- `What is axonometry? <#what-is-axonometry>`__
- `How does it work? <#how-does-it-work>`__
- `Examples <#examples>`__
- `Installation <#installation>`__
- `Contributing <#contributing>`__
- `Acknowledgement <#acknowledgement>`__
- `License <#license>`__

.. start-pitch

What is axonometry?
-------------------

*Computer graphics meets architecture representation meets generative art.*

*axonometry* is the tip of the iceberg of a PhD project at the `AlICe laboratory <https://alicelab.be>`__. It is the result of a practical experimentation with questions related to the field of architectural representation, the role of computer graphics and drawing practices.

- *axonometry* is a proof-of-concept about a certain way of constructing 3D representations by projection.
- *axonometry* is a scripting library for generating axonometric drawings. It implements axonometric projection operations commonly used in the context of architectural representation. *axonometry* allows the exploration of three dimensional representation through the definition of projection operations. Think of it as a tool for generative drawing, oriented towards architectural representation.

How does it work?
-----------------

*axonometry* is basically a wrapper for `compas <https://compas.dev>`__ geometry objects and produces SVG vector files with the help of `vpype <https://vpype.readthedocs.io>`__.

.. end-pitch

Examples
--------

.. code:: python

   from axonometry as Axonometry
   Axonometry(15,45).save_svg("new_drawing")

.. image:: ./docs/source/_images/examples/new_drawing.png
   :align: center

.. code:: python

  from axonometry import Axonometry
  my_axo = Axonometry.random_angles()
  my_axo.import_obj_file("./examples/monkey.obj")
  my_axo.show_paths()

.. image:: ./docs/source/_images/examples/monkey_system.png
   :align: center

Installation
------------

Please refer to the `install section <https://axonometry.readthedocs.io/en/latest/install.html>`_ for detailed installation instructions.

TL;DR:

- Python 3.12 is recommended, but *axonometry* is also compatible with Python 3.10 and 3.11.
- `uv <https://docs.astral.sh/uv/#installation>`_ is the recommended package manager.

.. code:: bash

   # Install uv on Linux and macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Install uv on Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   # Get Python 3.12
   uv python install 3.12
   # Make virtual environment
   uv venv
   # Install axonometry
   uv pip install axonometry

Contributing
------------

All type of feedback is welcome. Contributions can take any form and do not necessarily require software development skills! Check the `Contributing section <https://axonometry.readthedocs.io/en/latest/contributing.html>`__ for more information.

Acknowledgement
---------------

Many thanks to the developers of *compas* and *vpype*. Not only did their libraries make this project possible, but inspecting their elegant codebase was an invaluable resource for deepening my Pyhton knowledge.

License
-------

This project is licensed under the GPLv3 License. Check the `Liceneses section <https://axonometry.readthedocs.io/en/latest/license.html>`__ for more information.
