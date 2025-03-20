Quickstart
==========

Installation
------------

.. grid:: 1 2 2 2
    :gutter: 4

    .. grid-item-card:: Using pip
        :columns: 12 12 12 12

        grogupy can be quickly installed via pip from `PyPI <https://pypi.org>`_.

        ++++

        .. code-block:: bash

            python3 -m pip install --index-url https://test.pypi.org/simple/ grogupy

    .. grid-item-card:: Using conda
        :columns: 12 12 12 12

        grogupy is also available on `Anaconda/Miniconda <https://docs.conda.io/projects/conda/en/latest/>`_.

        ++++

        .. code-block:: bash

            python3 -m pip install --index-url https://test.pypi.org/simple/ grogupy

    .. grid-item-card:: Using source code
        :columns: 12 12 12 12

        Or if you want to use the latest development version, first go to an empty
        directory and clone the git repository. Then you can build the wheel and install with pip.

        ++++

        .. code-block:: bash

            git clone https://github.com/danielpozsar/grogupy.git
            python -m build
            pip install grogupy-1.0.0-py3-none-any



Quickstart tutorials
--------------------

.. toctree::
   :maxdepth: 1

   ../notebooks/quickstart/Calculate magnetic parameters.ipynb
   ../notebooks/quickstart/Visualize the exchange.ipynb
   ../notebooks/quickstart/Convergence with high throughput.ipynb
   Running in HPC.rst
