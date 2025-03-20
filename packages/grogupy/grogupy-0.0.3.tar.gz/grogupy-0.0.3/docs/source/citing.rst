.. _citing:

Citing grogupy
==============

grogupy is a completely open-source software package. It is released under the MIT license.
Currently there is no way to explicitly cite grogupy, but you can cite the underlying paper:
*Relativistic magnetic interactions from nonorthogonal basis sets*.

.. code-block:: bibtex

    @article{martinez2023relativistic,
        title={Relativistic magnetic interactions from nonorthogonal basis sets},
        author={Mart{\'\i}nez-Carracedo, Gabriel and Oroszl{\'a}ny, L{\'a}szl{\'o} and Garc{\'\i}a-Fuente, Amador and Ny{\'a}ri, Bendeg{\'u}z and Udvardi, L{\'a}szl{\'o} and Szunyogh, L{\'a}szl{\'o} and Ferrer, Jaime},
        journal={Physical Review B},
        volume={108},
        number={21},
        pages={214418},
        year={2023},
        publisher={APS}
    }

grogupy builds on the sisl package, which should also be cited.

.. code-block:: bibtex

    @software{zerothi_sisl,
    author       = {Papior, Nick},
    title        = {sisl: v0.14.3.},
    year         = {2024},
    doi          = {10.5281/zenodo.597181},
    url          = {https://doi.org/10.5281/zenodo.597181}
    }

Furthermore all the command line scripts and the ``grgupy`` package can print out the citation in **bibtex**
format.

.. code-block:: python3

    >>> import grogupy
    >>> print(grogupy.cite)
        @article{martinez2023relativistic,
            title={Relativistic magnetic interactions from nonorthogonal basis sets},
            author={Mart{\'\i}nez-Carracedo, Gabriel and Oroszl{\'a}ny, L{\'a}szl{\'o} and Garc{\'\i}a-Fuente, Amador and Ny{\'a}ri, Bendeg{\'u}z and Udvardi, L{\'a}szl{\'o} and Szunyogh, L{\'a}szl{\'o} and Ferrer, Jaime},
            journal={Physical Review B},
            volume={108},
            number={21},
            pages={214418},
            year={2023},
            publisher={APS}
        }

        @software{zerothi_sisl,
        author       = {Papior, Nick},
        title        = {sisl: v0.14.3.},
        year         = {2024},
        doi          = {10.5281/zenodo.597181},
        url          = {https://doi.org/10.5281/zenodo.597181}
        }


.. code-block:: console

    grogupy --cite
    @article{martinez2023relativistic,
        title={Relativistic magnetic interactions from nonorthogonal basis sets},
        author={Mart{\'\i}nez-Carracedo, Gabriel and Oroszl{\'a}ny, L{\'a}szl{\'o} and Garc{\'\i}a-Fuente, Amador and Ny{\'a}ri, Bendeg{\'u}z and Udvardi, L{\'a}szl{\'o} and Szunyogh, L{\'a}szl{\'o} and Ferrer, Jaime},
        journal={Physical Review B},
        volume={108},
        number={21},
        pages={214418},
        year={2023},
        publisher={APS}
    }

    @software{zerothi_sisl,
    author       = {Papior, Nick},
    title        = {sisl: v0.14.3.},
    year         = {2024},
    doi          = {10.5281/zenodo.597181},
    url          = {https://doi.org/10.5281/zenodo.597181}
    }
