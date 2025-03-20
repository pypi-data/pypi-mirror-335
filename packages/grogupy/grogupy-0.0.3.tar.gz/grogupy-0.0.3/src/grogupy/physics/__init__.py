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
Physics
=======

.. currentmodule:: grogupy.physics



Functions
---------

.. autosummary::
   :toctree: _generated/

    builder
    contour
    kspace
    magnetism


Background information
----------------------

Examples
--------

For examples, see the various functions.

"""

from .. import __all__
from .builder import Builder
from .contour import Contour
from .hamiltonian import Hamiltonian
from .kspace import Kspace
from .magnetic_entity import MagneticEntity
from .pair import Pair

__all__.extend(
    [
        "Contour",
        "Kspace",
        "MagneticEntity",
        "Pair",
        "Hamiltonian",
        "Builder",
    ]
)
