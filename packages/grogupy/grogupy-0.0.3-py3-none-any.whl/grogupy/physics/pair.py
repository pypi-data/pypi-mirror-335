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
"""pair

_extended_summary_
"""
import copy
from typing import Union

import numpy as np
import sisl
from numpy.typing import NDArray

from .. import __version__
from .._core.core import onsite_projection
from .magnetic_entity import MagneticEntity
from .utilities import (
    calculate_exchange_tensor,
    fit_exchange_tensor,
    interaction_energy,
)


class Pair:
    """This class contains the data and the methods related to the pairs of magnetic entities.

    It sets up the instance based on the Hamiltonian of the DFT calculation, a pair of
    MagneticEntities and the supercell shift of the second MagneticEntities, given that the first
    one is not shifted. By default ``dh`` is ``None`` and we use the Hamiltonian from the magnetic
    entities. If the Hamiltonian from the two magnetic entities are different it raises an error.

    Parameters
    ----------
    M1: MagneticEntity
        The first magnetic entity
    M2: MagneticEntity
        The second magnetic entity
    supercell_shift: Union[list, NDArray]
        The integer coordinates of the supercell shift

    Examples
    --------
    The following examples show you how to create pairs in the **Fe3GeTe2** system.

    >>> fdf_path = "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"

    >>> Fe3 = MagneticEntity(fdf_path, atom=3, l=2)
    >>> Fe5 = MagneticEntity(fdf_path, atom=5, l=2)
    >>> pair_of_Fe = Pair(Fe3, Fe5, [0,0,0])
    >>> print(pair_of_Fe)
    <grogupy.Pair tag1=3Fe(l:2), tag2=5Fe(l:2), Ruc=[0 0 0]>

    Methods
    -------
    calculate_energies(weights) :
        Calculates the energies of the infinitesimal rotations.
    calculate_exchange_tensor() :
        Calculates the exchange tensor from the energies.
    fit_exchange_tensor(ref_xcf) :
        Fits the exchange tensor to the energies.
    to_dict(all) :
        Returns the instance data as a dictionary.
    add_G_tmp(i, Gk, k, weight) :
        Adds the calculated Greens function to the temporary Greens function.
    copy() :
        Return a copy of this Pair

    Attributes
    ----------
    M1: MagneticEntity
        The first magnetic entity
    M2: MagneticEntity
        The second magnetic entity
    supercell_shift: NDArray
        The supercell shift normed by the supercell vectors
    cell: NDArray
        The supercell vectors
    Gij: list
        Projected Greens function from M1 to M2
    Gji: list
        Projected Greens function from M2 to M1
    SBS1: int
        The SPIN BOX size of M1
    SBS2: int
        The SPIN BOX size of M2
    SBI1: NDArray
        The SPIN BOX indices of M1
    SBI2: NDArray
        The SPIN BOX indices of M2
    tags: list[str]
        The tags of the two magnetic entities
    supercell_shift_xyz: NDArray
        The supercell shift in real coordinates
    xyz: list[NDArray, NDArray]
        The coordinates of the magnetic entity (it can consist of many atoms)
    xyz_center: list[NDArray, NDArray]
        The center of coordinates for the magnetic entities
    distance: float
        The distance of the magnetic entities (it uses the center of coordinates
        for each magnetic entity)
    energies : Union[None, NDArray]
        The calculated energies for each direction
    self.J_iso: Union[float, None]
        Isotropic exchange, by default None
    self.J: Union[NDArray, None]
        Complete exchange tensor, by default None
    self.J_S: Union[NDArray, None]
        Symmetric exchange, by default None
    self.D: Union[NDArray, None]
        Dzyaloshinskii-Morilla vector, by default None

    Raises
    ------
    Exception
        Different Hamiltonians from the magnetic entities

    """

    number_of_pairs: int = 0

    def __init__(
        self,
        M1: MagneticEntity,
        M2: MagneticEntity,
        supercell_shift: Union[list, NDArray] = np.array([0, 0, 0]),
    ) -> None:
        """This class contains the data and the methods related to the pairs of magnetic entities.

        It sets up the instance based on the Hamiltonian of the DFT calculation, a pair of
        MagneticEntities and the supercell shift of the second MagneticEntities, given that the first
        one is not shifted. By default ``dh`` is ``None`` and we use the Hamiltonian from the magnetic
        entities. If the Hamiltonian from the two magnetic entities are different it raises an error.

        Parameters
        ----------
        M1: MagneticEntity
            The first magnetic entity
        M2: MagneticEntity
            The second magnetic entity
        supercell_shift: Union[list, NDArray]
            The integer coordinates of the supercell shift

        Examples
        --------
        The following examples show you how to create pairs in the **Fe3GeTe2** system.

        >>> fdf_path = "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"

        >>> Fe3 = MagneticEntity(fdf_path, atom=3, l=2)
        >>> Fe5 = MagneticEntity(fdf_path, atom=5, l=2)
        >>> pair_of_Fe = Pair(Fe3, Fe5, [0,0,0])
        >>> print(pair_of_Fe)
        <grogupy.Pair tag1=3Fe(l:2), tag2=5Fe(l:2), Ruc=[0 0 0]>
        """

        if M1._dh is M2._dh:
            self._dh: sisl.physics.Hamiltonian = M1._dh
        elif (M1._dh.Hk().toarray() == M2._dh.Hk().toarray()).all() and (
            M1._dh.Sk().toarray() == M2._dh.Sk().toarray()
        ).all():
            self._dh: sisl.physics.Hamiltonian = M1._dh
        else:
            raise Exception("Different Hamiltonians from the magnetic entities!")

        self.M1: MagneticEntity = M1
        self.M2: MagneticEntity = M2

        self.supercell_shift: NDArray = np.array(supercell_shift)

        # initialize simulation parameters
        self.Gij: list[NDArray] = []
        self.Gji: list[NDArray] = []
        self._Gij_tmp: list[NDArray] = []
        self._Gji_tmp: list[NDArray] = []

        self.energies: Union[None, NDArray] = None
        self.J_iso: Union[float, None] = None
        self.J: Union[NDArray, None] = None
        self.J_S: Union[NDArray, None] = None
        self.D: Union[NDArray, None] = None

        Pair.number_of_pairs += 1

    def __getstate__(self):
        state = self.__dict__.copy()
        state["M1"] = state["M1"].__getstate__()
        state["M2"] = state["M2"].__getstate__()

        return state

    def __setstate__(self, state):
        M1 = object.__new__(MagneticEntity)
        M1.__setstate__(state["M1"])
        state["M1"] = M1
        M2 = object.__new__(MagneticEntity)
        M2.__setstate__(state["M2"])
        state["M2"] = M2

        self.__dict__ = state

    def __eq__(self, value):
        if isinstance(value, Pair):
            if (
                np.allclose(self._dh.Hk().toarray(), value._dh.Hk().toarray())
                and np.allclose(self._dh.Sk().toarray(), value._dh.Sk().toarray())
                and self.M1 == value.M1
                and self.M2 == value.M2
                and np.allclose(self.supercell_shift, value.supercell_shift)
                and np.allclose(self.Gij, value.Gij)
                and np.allclose(self.Gji, value.Gji)
                and np.allclose(self._Gij_tmp, value._Gij_tmp)
                and np.allclose(self._Gji_tmp, value._Gji_tmp)
                and np.allclose(self.energies, value.energies)
                and np.allclose(self.J_iso, value.J_iso)
                and np.allclose(self.J, value.J)
                and np.allclose(self.J_S, value.J_S)
                and np.allclose(self.D, value.D)
            ):
                return True
            return False
        return False

    def __repr__(self) -> str:
        """String representation of the instance."""

        out = f"<grogupy.Pair tag1={self.tags[0]}, tag2={self.tags[1]}, Ruc={self.supercell_shift}>"

        return out

    @property
    def SBS1(self) -> int:
        return self.M1.SBS

    @property
    def SBS2(self) -> int:
        return self.M2.SBS

    @property
    def SBI1(self) -> NDArray:
        return self.M1.spin_box_indices

    @property
    def SBI2(self) -> NDArray:
        return self.M2.spin_box_indices

    @property
    def tags(self) -> list[str]:
        return [self.M1.tag, self.M2.tag]

    @property
    def cell(self):
        return self._dh.cell

    @property
    def supercell_shift_xyz(self) -> NDArray:
        return self.supercell_shift @ self.cell

    @property
    def xyz(self) -> NDArray:
        return np.array(
            [self.M1.xyz, self.M2.xyz + self.supercell_shift_xyz], dtype=object
        )

    @property
    def xyz_center(self) -> NDArray:
        return np.array(
            [self.M1.xyz_center, self.M2.xyz_center + self.supercell_shift_xyz]
        )

    @property
    def distance(self) -> float:
        return np.linalg.norm(self.xyz_center[0] - self.xyz_center[1])

    @property
    def energies_meV(self) -> NDArray:
        """The energies, but in meV."""

        if self.energies is None:
            return None

        return self.energies * sisl.unit_convert("eV", "meV")

    @property
    def energies_mRy(self) -> NDArray:
        """The energies, but in mRy."""

        if self.energies is None:
            return None

        return self.energies * sisl.unit_convert("eV", "mRy")

    @property
    def J_meV(self) -> NDArray:
        """The exchange tensor, but in meV."""

        return self.J * sisl.unit_convert("eV", "meV")

    @property
    def J_mRy(self) -> NDArray:
        """The exchange tensor, but in mRy."""

        return self.J * sisl.unit_convert("eV", "mRy")

    @property
    def D_meV(self) -> NDArray:
        """The DM vector, but in meV."""

        return self.D * sisl.unit_convert("eV", "meV")

    @property
    def D_mRy(self) -> NDArray:
        """The DM vector, but in mRy."""

        return self.D * sisl.unit_convert("eV", "mRy")

    @property
    def J_S_meV(self) -> NDArray:
        """The symmetric part of the exchange tensor, but in meV."""

        return self.J_S * sisl.unit_convert("eV", "meV")

    @property
    def J_S_mRy(self) -> NDArray:
        """The symmetric part of the exchange tensor, but in mRy."""

        return self.J_S * sisl.unit_convert("eV", "mRy")

    @property
    def J_iso_meV(self) -> NDArray:
        """The isotropic exchange, but in meV."""

        return self.J_iso * sisl.unit_convert("eV", "meV")

    @property
    def J_iso_mRy(self) -> NDArray:
        """The isotropic exchange, but in mRy."""

        return self.J_iso * sisl.unit_convert("eV", "mRy")

    def reset(self) -> None:
        """Resets the simulation results of the Pair.

        Does not reset the underlying Magnetic Entity instances.
        """

        self.Gij: list[NDArray] = []
        self.Gji: list[NDArray] = []
        self._Gij_tmp: list[NDArray] = []
        self._Gji_tmp: list[NDArray] = []
        self.energies: Union[None, NDArray] = None

        self.J_iso: Union[float, None] = None
        self.J: Union[NDArray, None] = None
        self.J_S: Union[NDArray, None] = None
        self.D: Union[NDArray, None] = None

    def calculate_energies(self, weights: NDArray) -> None:
        """Calculates the energies of the infinitesimal rotations.

        It uses the instance properties to calculate the energies and
        dumps the results to the `energies` property.

        Parameters
        ----------
        weights: NDArray
            The weights of the energy contour integral
        """

        energies: list[list[float]] = []
        for i, (Gij, Gji) in enumerate(zip(self.Gij, self.Gji)):
            storage: list = []
            # iterate over the first order local perturbations in all possible orientations for the two sites
            # actually all possible orientations without the orientation for the off-diagonal anisotropy
            # that is why we only take the first two of each Vu1
            for Vui in self.M1.Vu1[i][:2]:
                for Vuj in self.M2.Vu1[i][:2]:
                    storage.append(interaction_energy(Vui, Vuj, Gij, Gji, weights))
            # fill up the pairs dictionary with the energies
            energies.append(storage)

        # convert to np array
        self.energies: NDArray = np.array(energies)

    def calculate_exchange_tensor(self) -> None:
        """Calculates the exchange tensor from the energies.

        It uses the instance properties to calculate the exchange tensor
        and its different representations and dumps them to the `J`, `J_iso`,
        `J_S` and `D` properties.

        """

        J_iso, J_S, D, J = calculate_exchange_tensor(self.energies)
        self.J: NDArray = J
        self.J_S: NDArray = J_S
        self.J_iso: float = J_iso
        self.D: NDArray = D

    def fit_exchange_tensor(self, ref_xcf: list[dict]) -> None:
        """Fits the exchange tensor to the energies.

        It uses a fitting method to calculate the exchange tensor from the
        reference directions and its different representations and dumps
        them to the `J`, `J_iso`, `J_S` and `D` properties.

        Parameters
        ----------
        ref_xcf: list[dict]
            The reference directions containing the orientation and perpendicular directions
        """

        J_iso, J_S, D, J = fit_exchange_tensor(self.energies, ref_xcf)
        self.J: NDArray = J
        self.J_S: NDArray = J_S
        self.J_iso: float = J_iso
        self.D: NDArray = D

    def add_G_tmp(self, i: int, Gk: NDArray, k: NDArray, weight: float) -> None:
        """Adds the calculated Greens function to the temporary Greens function.

        It is used in the parallel solution of the Hamiltonian inversions. Now the
        supercell shift is needed, because it introduces a phase shift to the Greens
        function.

        Parameters
        ----------
        i: int
            The index of the `ref_xcf_orientation`
        Gk: NDArray
            The Greens function projection on a specific k-point
        k: NDArray
            It is the supercell shift of the second magnetic entity
        weight: float
            The weight of the k-point
        """

        # add phase shift based on the cell difference
        phase: NDArray = np.exp(1j * 2 * np.pi * k @ self.supercell_shift.T)

        # store the Greens function slice of the magnetic entities
        self._Gij_tmp[i] += onsite_projection(Gk, self.SBI1, self.SBI2) * phase * weight
        self._Gji_tmp[i] += onsite_projection(Gk, self.SBI2, self.SBI1) / phase * weight

    def copy(self):
        """Returns the deepcopy of the instance.

        Returns
        -------
        Pair
            The copied instance.
        """

        return copy.deepcopy(self)


if __name__ == "__main__":
    pass
