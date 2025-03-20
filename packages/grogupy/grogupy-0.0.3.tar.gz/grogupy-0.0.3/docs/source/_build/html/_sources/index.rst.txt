.. grogupy master file, created by
   sphinx-quickstart on Thu Oct 10 17:10:03 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. module:: grogupy
   :no-index:

.. title:: grogupy: Relativistic magnetic interactions from non-orthogonal basis sets
.. meta::
   :description: Relativistic magnetic interactions from non-orthogonal basis sets.
   :keywords: DFT, physics, grogupy, magnetic interactions, Siesta


grogupy: Relativistic magnetic interactions from non-orthogonal basis sets
==========================================================================

grogupy was created to easily extract magnetic interaction parameters from
density functional theory (DFT) calculations. Because the underlying theory
focuses on non-orthogonal basis sets, the most straightforward software to
use for the DFT calculation is `Siesta <https://siesta-project.org/siesta/>`_.

It is based on the grogupy matlab implementation and the `sisl
<https://sisl.readthedocs.io/en/latest/index.html>`_ package and this work
was carried out by the `TRILMAX <https://trilmax.elte.hu>`_.

More on the theoretical background can be seen on `arXiv
<https://arxiv.org/abs/2309.02558>`_.

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: -- Quick-start guides
        :link: quickstart/index
        :link-type: doc

        Simple tutorial to introduce the ``grogupy`` package.

    .. grid-item-card:: -- Tutorials
        :link: tutorials/index
        :link-type: doc

        In depth tutorials to explore all the possibilities
        with ``grogupy``.

    .. grid-item-card::  -- API reference
        :link: API/modules
        :link-type: doc

        Detailed description of the implementation for advanced users.


    .. grid-item-card::  -- Implementation
        :link: development/index
        :link-type: doc

        Guides for developers.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Getting started

   introduction
   quickstart/index
   citing

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: User Guide

   tutorials/index
   visualizations/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Advanced usage

   API/modules
   environment/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Development

   development/index

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Extras

   changelog/index
   bibliography
