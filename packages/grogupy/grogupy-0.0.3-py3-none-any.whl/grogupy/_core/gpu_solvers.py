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
"""gpu_solvers.py

Because GPUs run asyncronusly, we can unlock the GIL in python
and run in a parallel manner over multiple GPUs. The only constrain
is the input/output writing between hardwares.
"""


from typing import TYPE_CHECKING

from numpy.typing import NDArray

if TYPE_CHECKING:
    from ..physics.builder import Builder

import numpy as np

from .. import _tqdm
from ..config import CONFIG


def solve_parallel_over_k(
    builder: "Builder",
) -> None:
    """It calculates the energies by the Greens function method.

    It inverts the Hamiltonians of all directions set up in the given
    k-points at the given energy levels. The solution is parallelized over
    k-points. It uses the number of GPUs given. And determines the parallelization
    over energy levels from the ``builder.greens_function_solver`` attribute.

    Parameters
    ----------
    builder : Builder
        The system that we want to solve
    """

    from concurrent.futures import ThreadPoolExecutor

    import cupy as cp
    from cupy.typing import NDArray as CNDArray

    parallel_size = CONFIG.parallel_size

    # iterate over the reference directions (quantization axes)
    G_mag = []
    G_pair_ij = []
    G_pair_ji = []
    for _ in builder.ref_xcf_orientations:
        G_mag.append([])
        G_pair_ij.append([])
        G_pair_ji.append([])

        # fill up the containers with zeros
        for mag_ent in builder.magnetic_entities:
            G_mag[-1].append(
                np.zeros(
                    (builder.contour.eset, mag_ent.SBS, mag_ent.SBS),
                    dtype="complex128",
                )
            )

        for pair in builder.pairs:
            G_pair_ij[-1].append(
                np.zeros(
                    (builder.contour.eset, pair.SBS1, pair.SBS2), dtype="complex128"
                )
            )
            G_pair_ji[-1].append(
                np.zeros(
                    (builder.contour.eset, pair.SBS2, pair.SBS1), dtype="complex128"
                )
            )
    G_mag = np.array(G_mag)
    G_pair_ij = np.array(G_pair_ij)
    G_pair_ji = np.array(G_pair_ji)

    # convert everything so it can be passed to the GPU solvers
    SBI = [m.spin_box_indices for m in builder.magnetic_entities]
    SBI1 = [p.SBI1 for p in builder.pairs]
    SBI2 = [p.SBI2 for p in builder.pairs]
    Ruc = [p.supercell_shift for p in builder.pairs]

    rotated_H = [H.H for H in builder._rotated_hamiltonians]
    S = builder.hamiltonian.S

    kpoints = np.array_split(builder.kspace.kpoints, parallel_size)
    kweights = np.array_split(builder.kspace.weights, parallel_size)

    sc_off = builder.hamiltonian.sc_off
    samples = builder.contour.samples

    def gpu_solver(
        mode: str,
        gpu_number: int,
        kpoints: list[NDArray],
        kweights: list[NDArray],
        SBI: list[NDArray],
        SBI1: list[NDArray],
        SBI2: list[NDArray],
        Ruc: list[NDArray],
        sc_off: NDArray,
        samples: NDArray,
        G_mag: list[NDArray],
        G_pair_ij: list[NDArray],
        G_pair_ji: list[NDArray],
        rotated_H: list[NDArray],
        S: NDArray,
    ) -> tuple[CNDArray, CNDArray, CNDArray]:
        """Solves the Green's function parallel on GPU.

        Should be used on computation power bound systems.

        Parameters
        ----------
        gpu_number : int
            The ID of the GPU which we want to run on
        kpoints : list[NDArray]
            The kpoints already split for the GPUs
        kweights : list[NDArray]
            The kpoint weights already split for the GPUs
        SBI : list[NDArray]
            Spin box indices for the magnetic entities
        SBI1 : list[NDArray]
            Spin box indices for the pairs
        SBI2 : list[NDArray]
            Spin box indices for the pairs
        Ruc : list[NDArray]
            Unit cell shift of the pairs
        sc_off : NDArray
            List of unit cell shifts for unit cell indexes
        samples : NDArray
            Energy samples
        G_mag : list[NDArray]
            Empty container for the final Green's function on each magnetic entity
        G_pair_ij : list[NDArray]
            Empty container for the final Green's function on each pair
        G_pair_ji : list[NDArray]
            Empty container for the final Green's function on each pair
        rotated_H : list[NDArray]
            Hamiltonians with rotated exchange fields
        S : NDArray
            Overlap matrix, should be the same for all Hamiltonians

        Returns
        -------
        local_G_mag : CNDArray
            The Greens function of the mangetic entities
        local_G_pair_ij : CNDArray
            The Greens function from mangetic entity i to j on the given GPU
        local_G_pair_ji : CNDArray
            The Greens function from mangetic entity j to i on the given GPU
        """

        # use the specified GPU
        with cp.cuda.Device(gpu_number):
            # copy everything to GPU
            local_kpoints = cp.array(kpoints[gpu_number])
            local_kweights = cp.array(kweights[gpu_number])
            local_SBI = cp.array(SBI)
            local_SBI1 = cp.array(SBI1)
            local_SBI2 = cp.array(SBI2)
            local_Ruc = cp.array(Ruc)

            local_sc_off = cp.array(sc_off)
            eset = samples.shape[0]
            local_samples = cp.array(samples.reshape(eset, 1, 1))

            local_G_mag = cp.zeros_like(G_mag)
            local_G_pair_ij = cp.zeros_like(G_pair_ij)
            local_G_pair_ji = cp.zeros_like(G_pair_ji)

            local_S = cp.array(S)

            for i in _tqdm(range(len(local_kpoints)), desc="Parallel over k:"):
                # weight of k point in BZ integral
                wk = local_kweights[i]
                k = local_kpoints[i]

                # iterate over reference directions
                for j in range(len(rotated_H)):
                    # calculate Hamiltonian and Overlap matrix in a given k point
                    # this generates the list of phases
                    phases = cp.exp(-1j * 2 * cp.pi * k @ local_sc_off.T)
                    # phases applied to the hamiltonian
                    HK = cp.einsum("abc,a->bc", cp.array(rotated_H[j]), phases)
                    SK = cp.einsum("abc,a->bc", local_S, phases)

                    # solve the Greens function on all energy points separately
                    if mode == "sequential":
                        for e in range(eset):
                            Gk = cp.linalg.inv(SK * local_samples[e] - HK)

                            # store the Greens function slice of the magnetic entities
                            for l, sbi in enumerate(local_SBI):
                                local_G_mag[j][l][e] += Gk[..., sbi, :][..., sbi] * wk

                            # store the Greens function slice of the pairs
                            for l, dat in enumerate(
                                zip(local_SBI1, local_SBI2, local_Ruc)
                            ):
                                sbi1, sbi2, ruc = dat
                                phase = cp.exp(1j * 2 * cp.pi * k @ ruc.T)

                                local_G_pair_ij[j][l][e] += (
                                    Gk[..., sbi1, :][..., sbi2] * wk * phase
                                )
                                local_G_pair_ji[j][l][e] += (
                                    Gk[..., sbi2, :][..., sbi1] * wk / phase
                                )

                    # solve the Greens function on all energy points in one step
                    elif mode == "parallel":
                        Gk = cp.linalg.inv(SK * local_samples - HK)

                        # store the Greens function slice of the magnetic entities
                        for l, sbi in enumerate(local_SBI):
                            local_G_mag[j][l] += Gk[..., sbi, :][..., sbi] * wk

                        # store the Greens function slice of the pairs
                        for l, dat in enumerate(zip(local_SBI1, local_SBI2, local_Ruc)):
                            sbi1, sbi2, ruc = dat
                            phase = cp.exp(1j * 2 * cp.pi * k @ ruc.T)

                            local_G_pair_ij[j][l] += (
                                Gk[..., sbi1, :][..., sbi2] * wk * phase
                            )
                            local_G_pair_ji[j][l] += (
                                Gk[..., sbi2, :][..., sbi1] * wk / phase
                            )

        return local_G_mag, local_G_pair_ij, local_G_pair_ji

    # call the solvers
    if builder.greens_function_solver.lower()[0] == "p":  # parallel solver
        mode = "parallel"
    elif builder.greens_function_solver.lower()[0] == "s":  # sequential solver
        mode = "sequential"
    else:
        raise Exception("Unknown Green's function solver!")

    with ThreadPoolExecutor(max_workers=parallel_size) as executor:
        futures = [
            executor.submit(
                gpu_solver,
                mode,
                gpu_number,
                kpoints,
                kweights,
                SBI,
                SBI1,
                SBI2,
                Ruc,
                sc_off,
                samples,
                G_mag,
                G_pair_ij,
                G_pair_ji,
                rotated_H,
                S,
            )
            for gpu_number in range(parallel_size)
        ]
        results = [future.result() for future in futures]

    # Combine results
    for G_mag_local, G_pair_ij_local, G_pair_ji_local in results:
        G_mag += G_mag_local.get()
        G_pair_ij += G_pair_ij_local.get()
        G_pair_ji += G_pair_ji_local.get()

    # calculate energies and magnetic parameters
    for j in range(len(builder._rotated_hamiltonians)):
        for l in range(len(builder.magnetic_entities)):
            mag_ent = builder.magnetic_entities[l]
            mag_ent.Gii[j] = G_mag[j][l]

            if builder.anisotropy_solver.lower()[0] == "f":  # fit
                mag_ent.calculate_energies(builder.contour.weights, False)
                mag_ent.fit_anisotropy_tensor(builder.ref_xcf_orientations)
            elif builder.anisotropy_solver.lower()[0] == "g":  # grogupy
                mag_ent.calculate_energies(builder.contour.weights, True)
                mag_ent.calculate_anisotropy()

        for l in range(len(builder.pairs)):
            pair = builder.pairs[l]
            pair.Gij[j] = G_pair_ij[j][l]
            pair.Gji[j] = G_pair_ji[j][l]

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
    k-points, energies and Hamiltonian orientations, which is the most general
    solution method. There is an overhead for the sample generation. It uses
    the number of GPUs given. And determines the parallelization over energy
    levels from the ``builder.greens_function_solver`` attribute.
    """

    parallel_size = CONFIG.parallel_size

    # iterate over the reference directions (quantization axes)
    G_mag = []
    G_pair_ij = []
    G_pair_ji = []
    for _ in builder.ref_xcf_orientations:
        G_mag.append([])
        G_pair_ij.append([])
        G_pair_ji.append([])

        # fill up the containers with zeros
        for mag_ent in builder.magnetic_entities:
            G_mag[-1].append(
                np.zeros(
                    (builder.contour.eset, mag_ent.SBS, mag_ent.SBS),
                    dtype="complex128",
                )
            )

        for pair in builder.pairs:
            G_pair_ij[-1].append(
                np.zeros(
                    (builder.contour.eset, pair.SBS1, pair.SBS2), dtype="complex128"
                )
            )
            G_pair_ji[-1].append(
                np.zeros(
                    (builder.contour.eset, pair.SBS2, pair.SBS1), dtype="complex128"
                )
            )
    G_mag = np.array(G_mag)
    G_pair_ij = np.array(G_pair_ij)
    G_pair_ji = np.array(G_pair_ji)

    # convert everything so it can be passed to the GPU solvers
    SBI = [m.spin_box_indices for m in builder.magnetic_entities]
    SBI1 = [p.SBI1 for p in builder.pairs]
    SBI2 = [p.SBI2 for p in builder.pairs]
    Ruc = [p.supercell_shift for p in builder.pairs]

    rotated_H = [H.H for H in builder._rotated_hamiltonians]
    S = builder.hamiltonian.S

    kpoints = [
        np.array(k) for k in np.array_split(builder.kspace.kpoints, parallel_size)
    ]
    kweights = [
        np.array(kw) for kw in np.array_split(builder.kspace.weights, parallel_size)
    ]

    sc_off = builder.hamiltonian.sc_off
    samples = builder.contour.samples

    def gpu_solver(
        mode: str,
        gpu_number: int,
        kpoints: list[NDArray],
        kweights: list[NDArray],
        SBI: list[NDArray],
        SBI1: list[NDArray],
        SBI2: list[NDArray],
        Ruc: list[NDArray],
        sc_off: NDArray,
        samples: NDArray,
        G_mag: list[NDArray],
        G_pair_ij: list[NDArray],
        G_pair_ji: list[NDArray],
        rotated_H: list[NDArray],
        S: NDArray,
    ) -> tuple[NDArray, NDArray, NDArray]:
        """Solves the Green's function parallel on GPU.

        Should be used on computation power bound systems.

        Parameters
        ----------
        gpu_number : int
            The ID of the GPU which we want to run on
        kpoints : list[NDArray]
            The kpoints already split for the GPUs
        kweights : list[NDArray]
            The kpoint weights already split for the GPUs
        SBI : list[NDArray]
            Spin box indices for the magnetic entities
        SBI1 : list[NDArray]
            Spin box indices for the pairs
        SBI2 : list[NDArray]
            Spin box indices for the pairs
        Ruc : list[NDArray]
            Unit cell shift of the pairs
        sc_off : NDArray
            List of unit cell shifts for unit cell indexes
        samples : NDArray
            Energy samples
        G_mag : list[NDArray]
            Empty container for the final Green's function on each magnetic entity
        G_pair_ij : list[NDArray]
            Empty container for the final Green's function on each pair
        G_pair_ji : list[NDArray]
            Empty container for the final Green's function on each pair
        rotated_H : list[NDArray]
            Hamiltonians with rotated exchange fields
        S : NDArray
            Overlap matrix, should be the same for all Hamiltonians

        Returns
        -------
        local_G_mag : NDArray
            The Greens function of the mangetic entities
        local_G_pair_ij : NDArray
            The Greens function from mangetic entity i to j on the given GPU
        local_G_pair_ji : NDArray
            The Greens function from mangetic entity j to i on the given GPU
        """

        # use the specified GPU
        with np.cuda.Device(gpu_number):
            # copy everything to GPU
            local_kpoints = np.array(kpoints[gpu_number])
            local_kweights = np.array(kweights[gpu_number])
            local_SBI = np.array(SBI)
            local_SBI1 = np.array(SBI1)
            local_SBI2 = np.array(SBI2)
            local_Ruc = np.array(Ruc)

            local_sc_off = np.array(sc_off)
            eset = samples.shape[0]
            local_samples = np.array(samples.reshape(eset, 1, 1))

            local_G_mag = np.zeros_like(G_mag)
            local_G_pair_ij = np.zeros_like(G_pair_ij)
            local_G_pair_ji = np.zeros_like(G_pair_ji)

            local_S = np.array(S)

            for i in _tqdm(range(len(local_kpoints)), desc="Parallel over all: "):
                # weight of k point in BZ integral
                wk = local_kweights[i]
                k = local_kpoints[i]

                # iterate over reference directions
                for j in range(len(rotated_H)):
                    # calculate Hamiltonian and Overlap matrix in a given k point
                    # this generates the list of phases
                    phases = np.exp(-1j * 2 * np.pi * k @ local_sc_off.T)
                    # phases applied to the hamiltonian
                    HK = np.einsum("abc,a->bc", np.array(rotated_H[j]), phases)
                    SK = np.einsum("abc,a->bc", local_S, phases)

                    # solve the Greens function on all energy points separately
                    if mode == "sequential":
                        for e in range(eset):
                            Gk = np.linalg.inv(SK * local_samples[e] - HK)

                            # store the Greens function slice of the magnetic entities
                            for l, sbi in enumerate(local_SBI):
                                local_G_mag[j][l][e] += Gk[..., sbi, :][..., sbi] * wk

                            # store the Greens function slice of the pairs
                            for l, dat in enumerate(
                                zip(local_SBI1, local_SBI2, local_Ruc)
                            ):
                                sbi1, sbi2, ruc = dat
                                phase = np.exp(1j * 2 * np.pi * k @ ruc.T)

                                local_G_pair_ij[j][l][e] += (
                                    Gk[..., sbi1, :][..., sbi2] * wk * phase
                                )
                                local_G_pair_ji[j][l][e] += (
                                    Gk[..., sbi2, :][..., sbi1] * wk / phase
                                )

                    # solve the Greens function on all energy points in one step
                    elif mode == "parallel":
                        Gk = np.linalg.inv(SK * local_samples - HK)

                        # store the Greens function slice of the magnetic entities
                        for l, sbi in enumerate(local_SBI):
                            local_G_mag[j][l] += Gk[..., sbi, :][..., sbi] * wk

                        # store the Greens function slice of the pairs
                        for l, dat in enumerate(zip(local_SBI1, local_SBI2, local_Ruc)):
                            sbi1, sbi2, ruc = dat
                            phase = np.exp(1j * 2 * np.pi * k @ ruc.T)

                            local_G_pair_ij[j][l] += (
                                Gk[..., sbi1, :][..., sbi2] * wk * phase
                            )
                            local_G_pair_ji[j][l] += (
                                Gk[..., sbi2, :][..., sbi1] * wk / phase
                            )

        return local_G_mag, local_G_pair_ij, local_G_pair_ji

    # call the solvers
    if builder.greens_function_solver.lower()[0] == "p":  # parallel solver
        mode = "parallel"
    elif builder.greens_function_solver.lower()[0] == "s":  # sequential solver
        mode = "sequential"
    else:
        raise Exception("Unknown Green's function solver!")

    with ThreadPoolExecutor(max_workers=parallel_size) as executor:
        futures = [
            executor.submit(
                gpu_solver,
                mode,
                gpu_number,
                kpoints,
                kweights,
                SBI,
                SBI1,
                SBI2,
                Ruc,
                sc_off,
                samples,
                G_mag,
                G_pair_ij,
                G_pair_ji,
                rotated_H,
                S,
            )
            for gpu_number in range(parallel_size)
        ]
        results = [future.result() for future in futures]

    # Combine results
    for G_mag_local, G_pair_ij_local, G_pair_ji_local in results:
        G_mag += G_mag_local.get()
        G_pair_ij += G_pair_ij_local.get()
        G_pair_ji += G_pair_ji_local.get()

    # calculate energies and magnetic parameters
    for j in range(len(builder._rotated_hamiltonians)):
        for l in range(len(builder.magnetic_entities)):
            mag_ent = builder.magnetic_entities[l]
            mag_ent.Gii[j] = G_mag[j][l]

            if builder.anisotropy_solver.lower()[0] == "f":  # fit
                mag_ent.calculate_energies(builder.contour.weights, False)
                mag_ent.fit_anisotropy_tensor(builder.ref_xcf_orientations)
            elif builder.anisotropy_solver.lower()[0] == "g":  # grogupy
                mag_ent.calculate_energies(builder.contour.weights, True)
                mag_ent.calculate_anisotropy()

        for l in range(len(builder.pairs)):
            pair = builder.pairs[l]
            pair.Gij[j] = G_pair_ij[j][l]
            pair.Gji[j] = G_pair_ji[j][l]

            pair.calculate_energies(builder.contour.weights)
            if builder.exchange_solver.lower()[0] == "f":  # fit
                pair.fit_exchange_tensor(builder.ref_xcf_orientations)
            elif builder.exchange_solver.lower()[0] == "g":  # grogupy
                pair.calculate_exchange_tensor()


if __name__ == "__main__":
    pass
