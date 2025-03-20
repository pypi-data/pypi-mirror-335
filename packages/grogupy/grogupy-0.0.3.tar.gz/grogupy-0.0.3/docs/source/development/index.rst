Contributing to grogupy
=======================

Currently there is no way to contribute to the development for outsiders.
However here is a summary for the 'approved' developers.

Create environment
------------------

First you have to clone the repository from Github or Gitea. Gitea is the
old development platform, so it should only be used for tracking early stage
changes in the code.

.. code-block:: bash

    git clone https://gitea.vo.elte.hu/et209d/grogupy.git
    git clone https://github.com/danielpozsar/grogupy.git

Then the easiest way is to create a a virtual environment (.venv), for
example with VSCode.

* Use python 3.9.6

* install dependencies from:

  * requirements.txt

  * requirements-dev.txt

  * /docs/requirements.txt

Finally you have to install and run ``pre-commit``, which is mainly used
to automatically format the code, which makes it nicer and reduces git
differences.

.. code-block:: bash

    pre-commit install
    pre-commit run --all-files



Build wheel
-----------

You can find a detailed documentation on `PYPI <https://packaging.python.
org/en/latest/tutorials/packaging-projects/>`_, but you can read here a
short summary. First you need some API Tokens for Test PYPI, to be able
to upload. You can read about this `here <https://test.pypi.org/help/#apitoken>`_
. I own the current project, so you have to contact me.

Use the following commands for a quick setup from the **grogupy_project**
folder:

* Build wheel.

.. code-block:: bash

    python -m build

* Push to PYPI test repository.

.. code-block:: bash

    python -m twine upload --repository testpypi dist/*

* Or install right away from the `dist/` directory.

.. code-block:: bash

    pip install grogupy-1.0.0-py3-none-any

Build documentation
-------------------

Yo can go to the **docs/source** directory and modify the *.rst*
files to change the documentation. However to document the API of the
package it is advised to use automatic documentation generation.

* To build the documentation navigate to the **docs/source** folder.

.. code-block:: bash

    cd docs/source

* Then build the documentation. After this the html page can be found in
  **docs/source/_build/html**. If there is already a documentation you can
  remove it by running ``make clean``.

.. code-block:: bash

    make html

* To build a pdf containing the documentation use the rst2pdf extension.

.. code-block:: bash

    sphinx-build -b pdf . _build/pdf
