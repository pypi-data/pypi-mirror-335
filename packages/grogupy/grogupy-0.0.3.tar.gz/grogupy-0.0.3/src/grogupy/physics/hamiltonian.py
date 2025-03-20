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
"""hamiltonian

_extended_summary_
"""

import copy
import warnings
from typing import Union

import numpy as np
import sisl
from numpy.typing import NDArray

from .. import _tqdm
from .._core.constants import TAU_X, TAU_Y, TAU_Z
from .._core.core import build_hh_ss, hsk
from .._core.utilities import RotMa2b
from ..batch.timing import DefaultTimer
from ..config import CONFIG
from .utilities import spin_tracer

if CONFIG.is_GPU:
    import cupy as cp
    from cupy.typing import NDArray as CNDArray


class Hamiltonian:
    """This class contains the data and the methods related to the Hamiltonian and geometry.

    It sets up the instance based on the path to the Hamiltonian of the DFT calculation and
    the DFT exchange orientation.

    Parameters
    ----------
    infile: Union[str, tuple[sisl.physics.Hamiltonian, sisl.physics.DensityMatrix]]
        Path to the .fdf file or the sisl Hamiltonian and Density matrix
    scf_xcf_orientation: Union[list, NDArray]. optional
        The reference orientation, by default [0,0,1]

    Examples
    --------
    Creating a Hamiltonian from the DFT calculation.

    >>> fdf_path = "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"
    >>> scf_xcf_orientation = np.array([0,0,1])
    >>> hamiltonian = Hamiltonian(fdf_path, scf_xcf_orientation)
    >>> print(hamiltonian)
    <grogupy.Hamiltonian scf_xcf_orientation=[0 0 1], orientation=[0 0 1], NO=84>

    Methods
    -------
    rotate(orientation) :
        It rotates the exchange field of the Hamiltonian.
    HkSk(k) :
        Sets up the Hamiltonian and the overlap matrix at a given k-point.
    copy() :
        Return a copy of this Pair

    Attributes
    ----------
    _dh: sisl.physics.Hamiltonian
        The sisl Hamiltonian
    _ds: sisl.physics.DensityMatrix
        The sisl density matrix
    infile: str
        The path to the .fdf file
    H: NDArray
        Hamiltonian built from the sisl Hamiltonian
    S: NDArray
        Overlap matrix built from the sisl Hamiltonian
    scf_xcf_orientation: NDArray
        Orientation of the DFT exchange field
    orientation: NDArray
        Current orientation of the XCF filed
    hTRS: NDArray
        Time reversal symmetric part of the Hamiltonian
    hTRB: NDArray
        Time reversal broken symmetric part of the Hamiltonian
    H_XCF: NDArray
        Exchange Hamiltonian
    XCF: NDArray
        Exchange field
    NO: int
        Number of orbitals in the Hamiltonian
    cell: NDArray
        The unit cell vectors
    nsc: NDArray
        Number of supercells in each direction
    sc_off: NDArray
        Supercell indices
    uc_in_sc_index: int
        Unit cell index
    H_uc: NDArray
        Unit cell Hamiltonian
    H_XCF_uc: NDArray
        Unit cell exchange part of the Hamiltonian
    times: grogupy.batch.timing.DefaultTimer
        It contains and measures runtime
    """

    number_of_hamiltonians = 0

    def __init__(
        self,
        infile: Union[str, tuple[sisl.physics.Hamiltonian, sisl.physics.DensityMatrix]],
        scf_xcf_orientation: Union[list, NDArray] = np.array([0, 0, 1]),
    ) -> None:
        """Initialize hamiltonian"""

        self.times: DefaultTimer = DefaultTimer()
        if isinstance(infile, str):
            # get sisl sile
            sile = sisl.io.get_sile(infile)
            # load hamiltonian
            self._dh: sisl.physics.Hamiltonian = sile.read_hamiltonian()
            self._ds: sisl.physics.DensityMatrix = sile.read_density_matrix()
            self.infile: str = infile
        elif isinstance(infile, tuple):
            if isinstance(infile[0], sisl.physics.Hamiltonian) and isinstance(
                infile[1], sisl.physics.DensityMatrix
            ):
                self._dh = infile[0]
                self._ds = infile[1]
                self.infile = "Unknown!"
        else:
            raise Exception("Not valid input:", type(infile))

        H, S = build_hh_ss(self._dh)
        self.H: Union[NDArray, None] = H
        self.S: Union[NDArray, None] = S
        self.scf_xcf_orientation: NDArray = np.array(scf_xcf_orientation)
        if (self.scf_xcf_orientation != 0).sum() != 1:
            warnings.warn(
                "Tilted exchange field in the DFT calculation: ",
                self.scf_xcf_orientation,
            )

        self.orientation: NDArray = scf_xcf_orientation

        if CONFIG.is_CPU:
            # identifying TRS and TRB parts of the Hamiltonian
            TAUY: NDArray = np.kron(np.eye(self.NO), TAU_Y)

            hTR: NDArray = []
            for i in _tqdm(range(self.nsc.prod()), desc="Transpose Hamiltonian"):
                hTR.append(TAUY @ self.H[i].conj() @ TAUY)
            hTR = np.array(hTR)

            hTRS: NDArray = (self.H + hTR) / 2
            hTRB: NDArray = (self.H - hTR) / 2

            # extracting the exchange field
            traced: NDArray = []
            for i in _tqdm(range(self.nsc.prod()), desc="Calculate V_XCF"):
                traced.append(spin_tracer(hTRB[i]))
            traced = np.array(traced)  # equation 77

            XCF: NDArray = np.array(
                [
                    np.array([f["x"] / 2 for f in traced]),
                    np.array([f["y"] / 2 for f in traced]),
                    np.array([f["z"] / 2 for f in traced]),
                ]
            )

            H_XCF: NDArray = np.zeros(
                (self.nsc.prod(), self.NO * 2, self.NO * 2), dtype="complex128"
            )
            for i, tau in _tqdm(
                enumerate([TAU_X, TAU_Y, TAU_Z]), total=3, desc="Calculate H_XC"
            ):
                H_XCF += np.kron(XCF[i], tau)

        elif CONFIG.is_GPU:
            # identifying TRS and TRB parts of the Hamiltonian
            TAUY: CNDArray = cp.kron(cp.eye(self.NO), cp.array(TAU_Y))

            hTR: CNDArray = []
            for i in _tqdm(range(self.nsc.prod()), desc="Transpose Hamiltonian"):
                hTR.append(TAUY @ cp.array(self.H[i]).conj() @ TAUY)
            hTR = cp.array(hTR)

            hTRS: NDArray = (self.H + hTR.get()) / 2
            hTRB: NDArray = (self.H - hTR.get()) / 2

            # extracting the exchange field equation 77
            traced: list = []
            for i in _tqdm(range(self.nsc.prod()), desc="Calculate V_XCF"):
                traced.append(spin_tracer(hTRB[i]))

            XCF: NDArray = cp.array(
                [
                    cp.array([f["x"] / 2 for f in traced]),
                    cp.array([f["y"] / 2 for f in traced]),
                    cp.array([f["z"] / 2 for f in traced]),
                ]
            )

            H_XCF: NDArray = cp.zeros(
                (self.nsc.prod(), self.NO * 2, self.NO * 2), dtype="complex128"
            )
            for i, tau in _tqdm(
                enumerate([TAU_X, TAU_Y, TAU_Z]), total=3, desc="Calculate H_XC"
            ):
                H_XCF += np.kron(XCF[i], cp.array(tau))

            XCF, H_XCF = XCF.get(), H_XCF.get()
        else:
            raise ValueError(f"Unknown architecture: {CONFIG.architecture}")

        # check if exchange field has scalar part
        max_xcfs: float = abs(np.array([f["c"] / 2 for f in traced])).max()
        if max_xcfs > 1e-12:
            warnings.warn(
                f"Exchange field has non negligible scalar part. Largest value is {max_xcfs}"
            )
        self.hTRS, self.hTRB, self.XCF, self.H_XCF = hTRS, hTRB, XCF, H_XCF

        self.times.measure("setup", restart=True)
        Hamiltonian.number_of_hamiltonians += 1

    def __getstate__(self):
        state = self.__dict__.copy()
        state["times"] = state["times"].__getstate__()
        return state

    def __setstate__(self, state):
        times = object.__new__(DefaultTimer)
        times.__setstate__(state["times"])
        state["times"] = times

        self.__dict__ = state

    def __eq__(self, value):
        if isinstance(value, Hamiltonian):
            if (
                np.allclose(self._dh.Hk().toarray(), value._dh.Hk().toarray())
                and np.allclose(self._dh.Sk().toarray(), value._dh.Sk().toarray())
                and np.allclose(self._ds.Dk().toarray(), value._ds.Dk().toarray())
                and np.allclose(self._ds.Sk().toarray(), value._ds.Sk().toarray())
                and self.infile == value.infile
                and np.allclose(self.H, value.H)
                and np.allclose(self.S, value.S)
                and np.allclose(self.scf_xcf_orientation, value.scf_xcf_orientation)
                and np.allclose(self.orientation, value.orientation)
                and np.allclose(self.hTRS, value.hTRS)
                and np.allclose(self.hTRB, value.hTRB)
                and np.allclose(self.XCF, value.XCF)
                and np.allclose(self.H_XCF, value.H_XCF)
            ):
                return True
            return False
        return False

    def __repr__(self) -> str:
        """String representation of the instance."""

        out = f"<grogupy.Hamiltonian scf_xcf_orientation={self.scf_xcf_orientation}, orientation={self.orientation}, NO={self.NO}>"

        return out

    @property
    def geometry(self) -> sisl.geometry:
        return self._dh.geometry

    @property
    def NO(self) -> int:
        return self._dh.no

    @property
    def cell(self) -> NDArray:
        return self._dh.geometry.cell

    @property
    def nsc(self) -> int:
        return self._dh.geometry.nsc

    @property
    def sc_off(self) -> NDArray:
        return self._dh.geometry.sc_off

    @property
    def uc_in_sc_index(self) -> int:
        return self._dh.lattice.sc_index([0, 0, 0])

    @property
    def H_uc(self) -> NDArray:
        return self.H[self.uc_in_sc_index]

    @property
    def H_XCF_uc(self) -> NDArray:
        return self.H_XCF[self.uc_in_sc_index]

    @property
    def k(self) -> NDArray:
        """The k point where the system is set up."""
        return self.__k

    def rotate(self, orientation: NDArray) -> None:
        """It rotates the exchange field of the Hamiltonian.

        It dumps the solutions to the `XCF`, `H_XCF`, `H` and
        `orientation` properties.

        Parameters
        ----------
        orientation: NDArray
            The rotation where it rotates
        """

        # obtain rotated exchange field and Hamiltonian
        R: NDArray = RotMa2b(self.scf_xcf_orientation, orientation)
        self.XCF: NDArray = np.einsum("ij,jklm->iklm", R, self.XCF)

        if CONFIG.is_CPU:
            self.H_XCF: NDArray = np.zeros(
                (self.nsc.prod(), self.NO * 2, self.NO * 2), dtype=np.complex128
            )
            for i, tau in _tqdm(
                enumerate([TAU_X, TAU_Y, TAU_Z]),
                total=3,
                desc="Rotating Exchange field",
            ):
                self.H_XCF += np.kron(self.XCF[i], tau)
        elif CONFIG.is_GPU:
            self.H_XCF: CNDArray = cp.zeros(
                (self.nsc.prod(), self.NO * 2, self.NO * 2), dtype=np.complex128
            )
            self.XCF = cp.array(self.XCF)
            for i, tau in _tqdm(
                enumerate([TAU_X, TAU_Y, TAU_Z]),
                total=3,
                desc="Rotating Exchange field",
            ):
                self.H_XCF += cp.kron(self.XCF[i], cp.array(tau))
            self.H_XCF = self.H_XCF.get()
        else:
            raise Exception(f"Unknown architecture: {CONFIG.architecture}")

        # obtain total Hamiltonian with the rotated exchange field
        self.H: NDArray = self.hTRS + self.H_XCF  # equation 76
        self.orientation = orientation

    def HkSk(self, k: tuple = (0, 0, 0)) -> tuple[NDArray, NDArray]:
        """Sets up the Hamiltonian and the overlap matrix at a given k-point.

        Parameters
        ----------
        k: tuple, optional
            The given k-point, by default (0, 0, 0)

        Returns
        -------
        Hk: NDArray
            The Hamiltonian at the given k point
        Sk: NDArray
            The Ovelap matrix at the given k point

        """

        return hsk(self.H, self.S, self.sc_off, k)

    def copy(self):
        """Returns the deepcopy of the instance.

        Returns
        -------
        Hamiltonian
            The copied instance.
        """

        return copy.deepcopy(self)


if __name__ == "__main__":
    pass
