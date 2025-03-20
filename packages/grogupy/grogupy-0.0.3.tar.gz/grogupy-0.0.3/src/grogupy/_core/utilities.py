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
"""These are some basic support functions.

    This module mostly contains functions for rotations.
"""

from typing import Union

import numpy as np
import sisl
from numpy.typing import NDArray

from .. import _tqdm
from .constants import TAU_X, TAU_Y, TAU_Z


def commutator(a: NDArray, b: NDArray) -> NDArray:
    """Shorthand for commutator

    Commutator of two matrices in the mathematical sense.

    Parameters
    ----------
        a: NDArray
            The first matrix
        b: NDArray
            The second matrix

    Returns
    -------
        NDArray
            The commutator of a and b
    """

    return a @ b - b @ a


def tau_u(u: Union[list, NDArray]) -> NDArray:
    """Pauli matrix in direction u

    Returns the vector u in the basis of the Pauli matrices.

    Parameters
    ----------
        u: list or NDArray
            The direction

    Returns
    -------
        NDArray
            Arbitrary direction in the base of the Pauli matrices
    """

    # u is force to be of unit length
    u = u / np.linalg.norm(u)

    return u[0] * TAU_X + u[1] * TAU_Y + u[2] * TAU_Z


def crossM(u: Union[list, NDArray]) -> NDArray:
    """Definition for the cross-product matrix

    It acts as a cross product with vector u.

    Parameters
    ----------
        u: list or NDArray
            The second vector in the cross product

    Returns
    -------
        NDArray
            The matrix that represents teh cross product with a vector
    """

    return np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])


def RotM(theta: float, u: NDArray, eps: float = 1e-10) -> NDArray:
    """Definition of rotation matrix with angle theta around direction u

    Parameters
    ----------
        theta: float
            The angle of rotation
        u: NDArray
            The rotation axis
        eps: float, optional
            Cutoff for small elements in the resulting matrix. Defaults to 1e-10

    Returns
    -------
        NDArray
            The rotation matrix
    """

    u = u / np.linalg.norm(u)

    M = (
        np.cos(theta) * np.eye(3)
        + np.sin(theta) * crossM(u)
        + (1 - np.cos(theta)) * np.outer(u, u)
    )

    # kill off small numbers
    M[abs(M) < eps] = 0.0
    return M


def RotMa2b(a: NDArray, b: NDArray, eps: float = 1e-10) -> NDArray:
    """Definition of rotation matrix rotating unit vector a to unit vector b

    Function returns array R such that R @ a = b holds.

    Parameters
    ----------
        a: NDArray
            First vector
        b: NDArray
            Second vector
        eps: float, optional
            Cutoff for small elements in the resulting matrix. Defaults to 1e-10

    Returns
    --------
        NDArray
            The rotation matrix with the above property
    """

    v = np.cross(a, b)
    c = a @ b
    M = np.eye(3) + crossM(v) + crossM(v) @ crossM(v) / (1 + c)

    # kill off small numbers
    M[abs(M) < eps] = 0.0
    return M


def setup_from_range(
    dh: sisl.physics.Hamiltonian,
    R: float,
    subset: Union[None, list[int], list[list[int], list[int]]] = None,
    **kwargs,
) -> tuple[sisl.physics.Hamiltonian, list[dict], list[dict]]:
    """Generates all the pairs and magnetic entities from atoms in a given radius.

    It takes all the atoms from the unit cell and generates
    all the corresponding pairs and magnetic entities in the given
    radius. It can generate pairs for a subset of of atoms,
    which can be given by the ``subset`` parameter.

    1. If subset is None all atoms can create pairs

    2. If subset is a list of integers, then all the
    possible pairs will be generated to these atoms in
    the unit cell

    3. If subset is two list, then the first list is the
    list of atoms in the unit cell (``Ri``), that can create
    pairs and the second list is the list of atoms outside
    the unit cell that can create pairs (``Rj``)

    !!!WARNING!!!
    In the third case it is really ``Ri`` and ``Rj``, that
    are given, so in some cases we could miss pairs in the
    unit cell.

    Parameters
    ----------
    dh : sisl.physics.Hamiltonian
        The sisl Hamiltonian that contains the geometry and
        atomic information
    R : float
        The radius where the pairs are found
    subset : Union[None, list[int], list[list[int], list[int]]], optional
        The subset of atoms that contribute to the pairs, by default None

    Other Parameters
    ----------------
    **kwargs: otpional
        These are passed to the magnetic entity dictionary

    Returns
    -------
    magnetic_entities : list[dict]
        The magnetic entities dictionaries
    pairs : list[dict]
        The pair dictionaries
    """

    # copy so we do not overwrite
    dh = dh.copy()

    # case 1
    # if subset is not given, then use all the atoms in the
    # unit cell
    if subset is None:
        uc_atoms = range(len(dh.atoms))
        uc_out_atoms = range(len(dh.atoms))

    elif isinstance(subset, list):
        # case 2
        # if only the unit cell atoms are given
        if isinstance(subset[0], int):
            uc_atoms = subset
            uc_out_atoms = range(len(dh.atoms))

        # case 3
        # if the unit cell atoms and the atoms outside the unit cell
        # are both given
        elif isinstance(subset[0], list):
            uc_atoms = subset[0]
            uc_out_atoms = subset[1]

    pairs = []
    # the center from which we measure the distance
    for i in _tqdm(uc_atoms, desc="Pair finding"):
        center = dh.xyz[i]

        # update number of supercells based on the range from
        # the input R

        # two times the radius should be the length along each
        # lattice vector + 2 for the division
        offset = (R // np.linalg.norm(dh.cell, axis=1)) + 1
        offset *= 2
        # of offset is odd, then chose it, if even, chose the larger
        # odd number beside it
        offset += 1 - (offset % 2)
        dh.set_nsc(offset)

        # get all atoms in the range
        indices = dh.geometry.close(center, R)

        # get the supercell indices and the atom indices in
        # the shifted supercell
        aj = dh.geometry.asc2uc(indices)
        Ruc = dh.geometry.a2isc(indices)

        # this is where we fulfill the second part of condition
        # three
        mask = [k in uc_out_atoms for k in aj]
        aj = aj[mask]
        Ruc = Ruc[mask]

        ai = np.ones_like(aj) * i

        for j in range(len(ai)):
            # do not include self interaction
            if ai[j] == aj[j] and (Ruc[j] == np.array([0, 0, 0])).all():
                continue

            # append pairs
            pairs.append([ai[j], aj[j], Ruc[j][0], Ruc[j][1], Ruc[j][2]])

    # sort pairs for nicer output
    pairs = np.array(pairs)
    idx = np.lexsort((pairs[:, 4], pairs[:, 3], pairs[:, 2], pairs[:, 1], pairs[:, 0]))
    pairs = pairs[idx]

    # create magnetic entities
    atoms = np.unique(pairs[:, [0, 1]])
    magnetic_entities = [dict(atom=at, **kwargs) for at in atoms]

    # create output pair information
    out = []
    for pair in _tqdm(pairs, desc="Pair creation"):
        ai = np.where(atoms == pair[0])[0][0]
        aj = np.where(atoms == pair[1])[0][0]
        out.append(dict(ai=ai, aj=aj, Ruc=[pair[2], pair[3], pair[4]]))

    return magnetic_entities, out


if __name__ == "__main__":
    pass
