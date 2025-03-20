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
"""grogupy is a package capable of calculating magnetic interactions.

    The main focus is on calculating the parameters of the generalized Heisenberg
    model including the exchange between the pairs and the anisotropy of the
    magnetic entities. This is done by reading in the Hamiltonian to a single
    non-collinear DFT calculation, where the DFT software can be non-orthogonal.
"""

__all__ = []
__version__ = "0.0.3"


from ._tqdm import _tqdm

# pre-import stuff
from .config import CONFIG
from .io import load, save, save_magnopy
from .physics import Builder, Contour, Hamiltonian, Kspace, MagneticEntity, Pair

# extend namespace
__all__.extend(
    [
        "_tqdm",
        "save",
        "save_magnopy",
        "load",
        "Contour",
        "Kspace",
        "MagneticEntity",
        "Pair",
        "Hamiltonian",
        "Builder",
    ]
)


__bibtex__ = """
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

"""

__citation__ = __bibtex__
cite = __bibtex__
