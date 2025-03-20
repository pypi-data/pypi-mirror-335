# Copyright (c) [2024-2025] [Laszlo Oroszlany, Daniel Pozsar]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Visualization
=============

.. currentmodule:: grogupy.viz


This submodule contains various routines to plot the system of magnetic entities
and pairs. Furthermore it will be able to plot the calculated magnetic exchange
parameters.

Functions
---------

.. autosummary::
   :toctree: _generated/

    plot_contour              Plots the contour for the integration.
    plot_kspace               Plots the k-space for the Brillouin-zone sampling.
    plot_magnetic_entities    Plots the magnetic entities.
    plot_pairs                Plots the pairs.
    plot_DM                   Plots the DM vectors.


Background information
----------------------

Currently all the functions are using the ``plotly`` library.
This decision was made because it can be used in the Jupyter
environment and supports interactive and 3D plots.

Examples
--------

For examples, see the various functions.

"""

from .. import __all__
from ..config import CONFIG
from ..physics import Builder, Contour, Kspace
from .viz import plot_contour, plot_DM, plot_kspace, plot_magnetic_entities, plot_pairs

__all__.extend(
    ["plot_contour", "plot_DM", "plot_kspace", "plot_magnetic_entities", "plot_pairs"]
)

CONFIG._Config__viz_loaded = True

setattr(Contour, "plot", plot_contour)
setattr(Kspace, "plot", plot_kspace)
setattr(Builder, "plot_DM", plot_DM)
setattr(Builder, "plot_magnetic_entities", plot_magnetic_entities)
setattr(Builder, "plot_pairs", plot_pairs)
