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
"""It contains the core functions of the calculation.

    There are mathematical functions, Hamiltonian magnetic entity and pair generation.
"""

from typing import Union

import numpy as np
import sisl
from numpy.typing import NDArray
from scipy.special import roots_legendre

from .. import _tqdm
from ..config import CONFIG
from .utilities import commutator

if CONFIG.is_GPU:
    import cupy as cp


def parallel_Gk(HK: NDArray, SK: NDArray, samples: NDArray, eset: int) -> NDArray:
    """Calculates the Greens function by inversion

    It calculates the Greens function on all the energy levels at the same time.

    Parameters
    ----------
        HK: (NO, NO), NDArray
            Hamiltonian at a given k point
        SK: (NO, NO), NDArray
            Overlap Matrix at a given k point
        samples: (eset) NDArray
            Energy sample along the contour
        eset: int
            Number of energy samples along the contour

    Returns
    -------
        Gk: (eset, NO, NO), NDArray
            Green's function at a given k point
    """

    # Calculates the Greens function on all the energy levels
    return np.linalg.inv(SK * samples.reshape(eset, 1, 1) - HK)


def sequential_Gk(HK: NDArray, SK: NDArray, samples: NDArray, eset: int) -> NDArray:
    """Calculates the Greens function by inversion

    It calculates sequentially over the energy levels.

    Parameters
    ----------
        HK: (NO, NO), NDArray
            Hamiltonian at a given k point
        SK: (NO, NO), NDArray
            Overlap Matrix at a given k point
        samples: (eset) NDArray
            Energy sample along the contour
        eset: int
            Number of energy samples along the contour

    Returns
    -------
        Gk: (eset, NO, NO), NDArray
            Green's function at a given k point
    """

    # creates an empty holder
    Gk = np.zeros(shape=(eset, HK.shape[0], HK.shape[1]), dtype="complex128")
    # fills the holder sequentially by the Greens function on a given energy
    for j in range(eset):
        Gk[j] = np.linalg.inv(SK * samples[j] - HK)

    return Gk


def onsite_projection(matrix: NDArray, idx1: NDArray, idx2: NDArray) -> NDArray:
    """It produces the slices of a matrix for the on site projection

    The slicing is along the last two axes as these contains the orbital indexing.

    Parameters
    ----------
        matrix: (..., :, :) NDArray
            Some matrix
        idx: NDArray
            The indexes of the orbitals

    Returns
    -------
        NDArray
            Reduced matrix based on the projection
    """

    return matrix[..., idx1, :][..., idx2]


def calc_Vu(H: NDArray, Tu: NDArray) -> NDArray:
    """Calculates the local perturbation in case of a spin rotation

    Parameters
    ----------
        H: (NO, NO) NDArray
            Hamiltonian
        Tu: (NO, NO) array_like
            Rotation around u

    Returns
    -------
        Vu1: (NO, NO) NDArray
            First order perturbed matrix
        Vu2: (NO, NO) NDArray
            Second order perturbed matrix
    """

    Vu1 = 1j / 2 * commutator(H, Tu)  # equation 100
    Vu2 = 1 / 8 * commutator(commutator(Tu, H), Tu)  # equation 100

    return Vu1, Vu2


def build_hh_ss(dh: sisl.physics.Hamiltonian) -> tuple[NDArray, NDArray]:
    """It builds the Hamiltonian and Overlap matrix from the sisl.dh class

    It restructures the data in the SPIN BOX representation, where NS is
    the number of supercells and NO is the number of orbitals.

    Parameters
    ----------
        dh: sisl.physics.Hamiltonian
            Hamiltonian read in by sisl

    Returns
    -------
        hh: (NS, NO, NO) NDArray
            Hamiltonian in SPIN BOX representation
        ss: (NS, NO, NO) NDArray
            Overlap matrix in SPIN BOX representation
    """

    NO = dh.no  # shorthand for number of orbitals in the unit cell

    # preprocessing Hamiltonian and overlap matrix elements
    h11 = dh.tocsr(dh.M11r)
    h11 += dh.tocsr(dh.M11i) * 1.0j
    h11 = h11.toarray().reshape(NO, dh.n_s, NO).transpose(0, 2, 1).astype("complex128")

    h22 = dh.tocsr(dh.M22r)
    h22 += dh.tocsr(dh.M22i) * 1.0j
    h22 = h22.toarray().reshape(NO, dh.n_s, NO).transpose(0, 2, 1).astype("complex128")

    h12 = dh.tocsr(dh.M12r)
    h12 += dh.tocsr(dh.M12i) * 1.0j
    h12 = h12.toarray().reshape(NO, dh.n_s, NO).transpose(0, 2, 1).astype("complex128")

    h21 = dh.tocsr(dh.M21r)
    h21 += dh.tocsr(dh.M21i) * 1.0j
    h21 = h21.toarray().reshape(NO, dh.n_s, NO).transpose(0, 2, 1).astype("complex128")

    sov = (
        dh.tocsr(dh.S_idx)
        .toarray()
        .reshape(NO, dh.n_s, NO)
        .transpose(0, 2, 1)
        .astype("complex128")
    )

    # Reorganization of Hamiltonian and overlap matrix elements to SPIN BOX representation
    U = np.vstack(
        [
            np.kron(np.eye(NO, dtype=int), np.array([1, 0])),
            np.kron(np.eye(NO, dtype=int), np.array([0, 1])),
        ]
    )

    # This is the permutation that transforms ud1ud2 to u12d12
    # That is this transforms FROM SPIN BOX to ORBITAL BOX => U
    # the inverse transformation is U.T u12d12 to ud1ud2
    # That is FROM ORBITAL BOX to SPIN BOX => U.T

    # From now on everything is in SPIN BOX!!
    if CONFIG.is_CPU:
        hh = []
        for i in _tqdm(range(dh.lattice.nsc.prod()), desc="Spin box Hamiltonian"):
            row1 = np.hstack([h11[:, :, i], h12[:, :, i]])
            row2 = np.hstack([h21[:, :, i], h22[:, :, i]])
            block = np.vstack([row1, row2])
            hh.append(U.T @ block @ U)
        hh = np.array(hh)

        ss = []
        for i in _tqdm(range(dh.lattice.nsc.prod()), desc="Spin box Overlap matrix"):
            row1 = np.hstack([sov[:, :, i], sov[:, :, i] * 0])
            row2 = np.hstack([sov[:, :, i] * 0, sov[:, :, i]])
            block = np.vstack([row1, row2])
            ss.append(U.T @ block @ U)
        ss = np.array(ss)

        for i in _tqdm(range(dh.sc_off.shape[0]), desc="Symmetrize Hamiltonian"):
            j = dh.lattice.sc_index(-dh.sc_off[i])
            h1, h1d = hh[i], hh[j]
            hh[i], hh[j] = (h1 + h1d.T.conj()) / 2, (h1d + h1.T.conj()) / 2
            s1, s1d = ss[i], ss[j]
            ss[i], ss[j] = (s1 + s1d.T.conj()) / 2, (s1d + s1.T.conj()) / 2

    elif CONFIG.is_GPU:
        h11 = cp.array(h11)
        h12 = cp.array(h12)
        h21 = cp.array(h21)
        h22 = cp.array(h22)
        sov = cp.array(sov)
        U = cp.array(U)

        hh = []
        for i in _tqdm(range(dh.lattice.nsc.prod()), desc="Spin box Hamiltonian"):
            row1 = cp.hstack([h11[:, :, i], h12[:, :, i]])
            row2 = cp.hstack([h21[:, :, i], h22[:, :, i]])
            block = cp.vstack([row1, row2])
            hh.append(U.T @ block @ U)

        ss = []
        for i in _tqdm(range(dh.lattice.nsc.prod()), desc="Spin box Overlap matrix"):
            row1 = cp.hstack([sov[:, :, i], sov[:, :, i] * 0])
            row2 = cp.hstack([sov[:, :, i] * 0, sov[:, :, i]])
            block = cp.vstack([row1, row2])
            ss.append(U.T @ block @ U)

        for i in _tqdm(range(dh.sc_off.shape[0]), desc="Symmetrize Hamiltonian"):
            j = dh.lattice.sc_index(-dh.sc_off[i])
            h1, h1d = hh[i], hh[j]
            hh[i], hh[j] = (h1 + h1d.T.conj()) / 2, (h1d + h1.T.conj()) / 2
            s1, s1d = ss[i], ss[j]
            ss[i], ss[j] = (s1 + s1d.T.conj()) / 2, (s1d + s1.T.conj()) / 2

        hh = cp.array(hh).get()
        ss = cp.array(ss).get()

    else:
        raise ValueError(f"Unknown architecture: {CONFIG.architecture}")

    return hh, ss


def make_contour(
    emin: float = -20, emax: float = 0.0, enum: int = 42, p: float = 150
) -> tuple[NDArray, NDArray]:
    """A more sophisticated contour generator

    Calculates the parameters for the complex contour integral. It uses the
    Legendre-Gauss quadrature method. It returns a class that contains
    the information for the contour integral.

    Parameters
    ----------
        emin: int, optional
            Energy minimum of the contour. Defaults to -20
        emax: float, optional
            Energy maximum of the contour. Defaults to 0.0, so the Fermi level
        enum: int, optional
            Number of sample points along the contour. Defaults to 42
        p: int, optional
            Shape parameter that describes the distribution of the sample points. Defaults to 150

    Returns
    -------
        ze: NDArray
            Contour points
        we: NDArray
            Weights along the contour
    """

    x, wl = roots_legendre(enum)
    R = (emax - emin) / 2  # radius
    z0 = (emax + emin) / 2  # center point
    y1 = -np.log(1 + np.pi * p)  # lower bound
    y2 = 0  # upper bound

    y = (y2 - y1) / 2 * x + (y2 + y1) / 2
    phi = (np.exp(-y) - 1) / p  # angle parameter
    ze = z0 + R * np.exp(1j * phi)  # complex points for path
    we = -(y2 - y1) / 2 * np.exp(-y) / p * 1j * (ze - z0) * wl

    return ze, we


def make_kset(kset: Union[list, NDArray] = np.array([1, 1, 1])) -> NDArray:
    """Simple k-grid generator to sample the Brillouin zone

    Parameters
    ----------
        kset: Union[list, NDArray]
            The number of k points in each direction

    Returns
    -------
        NDArray
            An array of k points that uniformly sample the Brillouin zone in the given directions
    """

    kset = np.array(kset)
    mpi = np.floor(-kset / 2) + 1
    x = np.arange(mpi[0], np.floor(kset[0] / 2 + 1), 1) / kset[0]
    y = np.arange(mpi[1], np.floor(kset[1] / 2 + 1), 1) / kset[1]
    z = np.arange(mpi[2], np.floor(kset[2] / 2 + 1), 1) / kset[2]

    x, y, z = np.meshgrid(x, y, z)
    kset = np.array([x.flatten(), y.flatten(), z.flatten()]).T

    return kset


def hsk(
    H: NDArray, S: NDArray, sc_off: list, k: tuple = (0, 0, 0)
) -> tuple[NDArray, NDArray]:
    """Speed up Hk and Sk generation

    Calculates the Hamiltonian and the Overlap matrix at a given k point. It is faster that the sisl version.

    Parameters
    ----------
        H: NDArray
            Hamiltonian in spin box form
        ss: NDArray
            Overlap matrix in spin box form
        sc_off: list
            supercell indexes of the Hamiltonian
        k: tuple, optional
            The k point where the matrices are set up. Defaults to (0, 0, 0)

    Returns
    -------
        NDArray
            Hamiltonian at the given k point
        NDArray
            Overlap matrix at the given k point
    """

    # this two conversion lines are from the sisl source
    k = np.asarray(k, np.float64)
    k.shape = (-1,)

    # this generates the list of phases
    phases = np.exp(-1j * 2 * np.pi * k @ sc_off.T)

    # phases applied to the hamiltonian
    HK = np.einsum("abc,a->bc", H, phases)
    SK = np.einsum("abc,a->bc", S, phases)

    return HK, SK


if __name__ == "__main__":
    pass
