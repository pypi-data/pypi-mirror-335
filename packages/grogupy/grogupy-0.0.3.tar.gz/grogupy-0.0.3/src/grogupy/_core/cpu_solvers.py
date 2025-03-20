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
"""cpu_solvers.py
"""

from itertools import product
from typing import TYPE_CHECKING

from numpy.typing import NDArray

if TYPE_CHECKING:
    from ..physics.builder import Builder

import numpy as np

from .. import _tqdm
from ..config import CONFIG
from .core import onsite_projection, parallel_Gk, sequential_Gk


def solve_parallel_over_k(
    builder: "Builder",
) -> None:
    """It calculates the energies by the Greens function method

    It inverts the Hamiltonians of all directions set up in the given
    k-points at the given energy levels. The solution is parallelized over
    k-points. It uses the `greens_function_solver` instance variable which
    controls the solution method over the energy samples. Generally this is
    the fastest solution method for a smaller number of nodes.
    """

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    parallel_size = CONFIG.parallel_size
    root_node = 0
    rank = comm.Get_rank()

    parallel_k = np.array_split(builder.kspace.kpoints, parallel_size)
    parallel_w = np.array_split(builder.kspace.weights, parallel_size)

    if rank == root_node:
        parallel_k[root_node] = _tqdm(parallel_k[root_node], desc="Parallel over k:")

    # sampling the integrand on the contour and the BZ
    for i, k in enumerate(parallel_k[rank]):
        # weight of k point in BZ integral
        wk: float = parallel_w[rank][i]

        # iterate over reference directions
        for j, hamiltonian_orientation in enumerate(builder._rotated_hamiltonians):
            # calculate Hamiltonian and Overlap matrix in a given k point
            Hk, Sk = hamiltonian_orientation.HkSk(k)

            if builder.greens_function_solver.lower()[0] == "p":  # parallel solver
                Gk = parallel_Gk(
                    Hk,
                    Sk,
                    builder.contour.samples,
                    builder.contour.eset,
                )
            elif builder.greens_function_solver.lower()[0] == "s":  # sequential solver
                # solve Greens function sequentially for the energies, because of memory bound
                Gk = sequential_Gk(
                    Hk,
                    Sk,
                    builder.contour.samples,
                    builder.contour.eset,
                )

            # store the Greens function slice of the magnetic entities
            for mag_ent in builder.magnetic_entities:
                mag_ent.add_G_tmp(j, Gk, wk)

            for pair in builder.pairs:
                pair.add_G_tmp(j, Gk, k, wk)

    # sum reduce partial results of mpi nodes
    for i in range(len(builder._rotated_hamiltonians)):
        for mag_ent in builder.magnetic_entities:
            comm.Reduce(mag_ent._Gii_tmp[i], mag_ent.Gii[i], root=root_node)

            if builder.anisotropy_solver.lower()[0] == "f":  # fit
                # mag_ent.calculate_energies(builder.contour.weights, False)
                mag_ent.calculate_energies(builder.contour.weights, False)
                mag_ent.fit_anisotropy_tensor(builder.ref_xcf_orientations)
            elif builder.anisotropy_solver.lower()[0] == "g":  # grogupy
                # mag_ent.calculate_energies(builder.contour.weights, True)
                mag_ent.calculate_energies(builder.contour.weights, True)
                mag_ent.calculate_anisotropy()

        for pair in builder.pairs:
            comm.Reduce(pair._Gij_tmp[i], pair.Gij[i], root=root_node)
            comm.Reduce(pair._Gji_tmp[i], pair.Gji[i], root=root_node)

            # pair.calculate_energies(builder.contour.weights)
            pair.calculate_energies(builder.contour.weights)
            if builder.exchange_solver.lower()[0] == "f":  # fit
                pair.fit_exchange_tensor(builder.ref_xcf_orientations)
            elif builder.exchange_solver.lower()[0] == "g":  # grogupy
                pair.calculate_exchange_tensor()


def solve_parallel_over_all(
    builder: "Builder",
) -> None:
    """It calculates the energies by the Greens function method

    It inverts the Hamiltonians of all directions set up in the given
    k-points at the given energy levels. The solution is parallelized over
    k-points and Hamiltonian orientations. There is an overhead for the sample generation.
    """

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    parallel_size = CONFIG.parallel_size
    root_node = 0
    rank = comm.Get_rank()

    kset_space = np.linspace(
        0, len(builder.kspace.kpoints) - 1, len(builder.kspace.kpoints), dtype=int
    )
    orient_space = np.linspace(
        0,
        len(builder.ref_xcf_orientations) - 1,
        len(builder.ref_xcf_orientations),
        dtype=int,
    )

    combinations = product(kset_space, orient_space)
    combinations = np.array_split(np.array(list(combinations)), parallel_size)

    if rank == root_node:
        total = (
            np.prod(
                (
                    len(builder.kspace.kpoints),
                    len(builder.ref_xcf_orientations),
                )
            )
            / parallel_size
        )
        combinations[root_node] = _tqdm(
            combinations[root_node], total=total, desc="Parallel over all: "
        )

    for k_idx, o_idx in combinations[rank]:
        Hk, Sk = builder._rotated_hamiltonians[o_idx].HkSk(
            builder.kspace.kpoints[k_idx]
        )
        # fills the holder sequentially by the Greens function on a given energy

        # this looks ugly, but in this case we always use the inversion method from
        # the _core.core Green's function solver, which may use numpy or scipy

        if builder.greens_function_solver.lower()[0] == "p":  # parallel solver
            Gk = parallel_Gk(
                Hk,
                Sk,
                builder.contour.samples,
                builder.contour.eset,
            )
        elif builder.greens_function_solver.lower()[0] == "s":  # sequential solver
            # solve Greens function sequentially for the energies, because of memory bound
            Gk = sequential_Gk(
                Hk,
                Sk,
                builder.contour.samples,
                builder.contour.eset,
            )

        # store the Greens function slice of the magnetic entities
        for mag_ent in builder.magnetic_entities:
            mag_ent._Gii_tmp[o_idx] += (
                onsite_projection(
                    Gk, mag_ent.spin_box_indices, mag_ent.spin_box_indices
                )
                * builder.kspace.weights[k_idx]
            )

        for pair in builder.pairs:
            # add phase shift based on the cell difference
            phase: NDArray = np.exp(
                1j * 2 * np.pi * builder.kspace.kpoints[k_idx] @ pair.supercell_shift.T
            )

            # store the Greens function slice of the magnetic entities
            pair._Gij_tmp[o_idx] += (
                onsite_projection(Gk, pair.SBI1, pair.SBI2)
                * phase
                * builder.kspace.weights[k_idx]
            )
            pair._Gji_tmp[o_idx] += (
                onsite_projection(Gk, pair.SBI2, pair.SBI1)
                / phase
                * builder.kspace.weights[k_idx]
            )

    # sum reduce partial results of mpi nodes
    for i in range(len(builder._rotated_hamiltonians)):
        for mag_ent in builder.magnetic_entities:
            comm.Reduce(mag_ent._Gii_tmp[i], mag_ent.Gii[i], root=root_node)

            if builder.anisotropy_solver.lower()[0] == "f":  # fit
                mag_ent.calculate_energies(builder.contour.weights, False)
                mag_ent.fit_anisotropy_tensor(builder.ref_xcf_orientations)
            elif builder.anisotropy_solver.lower()[0] == "g":  # grogupy
                mag_ent.calculate_energies(builder.contour.weights, True)
                mag_ent.calculate_anisotropy()

        for pair in builder.pairs:
            comm.Reduce(pair._Gij_tmp[i], pair.Gij[i], root=root_node)
            comm.Reduce(pair._Gji_tmp[i], pair.Gji[i], root=root_node)

            pair.calculate_energies(builder.contour.weights)
            if builder.exchange_solver.lower()[0] == "f":  # fit
                pair.fit_exchange_tensor(builder.ref_xcf_orientations)
            elif builder.exchange_solver.lower()[0] == "g":  # grogupy
                pair.calculate_exchange_tensor()


if __name__ == "__main__":
    pass
