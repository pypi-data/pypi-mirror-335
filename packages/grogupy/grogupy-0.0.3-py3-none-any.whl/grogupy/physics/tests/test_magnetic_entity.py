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
import numpy as np
import pytest

import grogupy
from grogupy.io.utilities import decipher
from grogupy.physics import MagneticEntity

pytestmark = [pytest.mark.physics]


class TestMagneticEntity:
    def test_(self):
        raise Exception("Not implemented test!")

    @pytest.mark.parametrize(
        "atom, l, orb, res",
        [
            (None, None, 1, "0Te(o:1)"),
            (None, None, [1], "0Te(o:1)"),
            (None, None, [1, 2], "0Te(o:1-2)"),
            (1, None, None, "1Te(l:All)"),
            (1, None, 1, "1Te(o:1)"),
            (1, None, [1], "1Te(o:1)"),
            (1, None, [1, 2], "1Te(o:1-2)"),
            (1, None, [[1, 2]], "1Te(o:1-2)"),
            (1, 1, None, "1Te(l:1)"),
            (1, [1], None, "1Te(l:1)"),
            (1, [1, 2], None, "1Te(l:1-2)"),
            (1, [[1, 2]], None, "1Te(l:1-2)"),
            ([1], None, None, "1Te(l:All)"),
            ([1], None, 1, "1Te(o:1)"),
            ([1], None, [1], "1Te(o:1)"),
            ([1], None, [1, 2], "1Te(o:1-2)"),
            ([1], None, [[1, 2]], "1Te(o:1-2)"),
            ([1], 1, None, "1Te(l:1)"),
            ([1], [1], None, "1Te(l:1)"),
            ([1], [1, 2], None, "1Te(l:1-2)"),
            ([1], [[1, 2]], None, "1Te(l:1-2)"),
            ([1, 2], None, None, "1Te(l:All)--2Ge(l:All)"),
            ([1, 2], None, 1, "1Te(o:1)--2Ge(o:1)"),
            ([1, 2], None, [1], "1Te(o:1)--2Ge(o:1)"),
            ([1, 2], None, [1, 2], "1Te(o:1-2)--2Ge(o:1-2)"),
            ([1, 2], None, [[1, 2], [1, 2]], "1Te(o:1-2)--2Ge(o:1-2)"),
            ([1, 2], 1, None, "1Te(l:1)--2Ge(l:1)"),
            ([1, 2], [1], None, "1Te(l:1)--2Ge(l:1)"),
            ([1, 2], [1, 2], None, "1Te(l:1-2)--2Ge(l:1-2)"),
            ([1, 2], [[1, 2], [1, 2]], None, "1Te(l:1-2)--2Ge(l:1-2)"),
            # tests from decipher
            ([0], None, [[1]], "0Te(o:1)"),
            ([0], None, [[1, 2]], "0Te(o:1-2)"),
            ([0], [[1]], None, "0Te(l:1)"),
            ([0], [[1, 2]], None, "0Te(l:1-2)"),
            ([0], [[None]], None, "0Te(l:0-1-2-3-4-5-6-7-8-9-10-11-12)"),
            ([1], None, [[1]], "1Te(o:1)"),
            ([1], None, [[1, 2]], "1Te(o:1-2)"),
            ([1], [[1]], None, "1Te(l:1)"),
            ([1], [[1, 2]], None, "1Te(l:1-2)"),
            ([1], [[None]], None, "1Te(l:0-1-2-3-4-5-6-7-8-9-10-11-12)"),
        ],
    )
    def test_generation(self, atom, l, orb, res):
        mag_ent = MagneticEntity(
            "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf",
            atom,
            l,
            orb,
        )
        print(mag_ent)
        print(mag_ent.atom, mag_ent.l, mag_ent.spin_box_indices)
        assert mag_ent.tag == res
        print(type(mag_ent.atom), mag_ent.atom)
        assert isinstance(mag_ent.atom, np.ndarray)
        if isinstance(atom, int):
            assert len(mag_ent.atom) == 1
        elif atom is not None:
            assert len(mag_ent.atom) == len(atom)
        assert isinstance(mag_ent.l, list)
        for i in mag_ent.l:
            assert isinstance(i, list)
            for j in i:
                if j is not None:
                    assert isinstance(j, int)
        assert len(mag_ent.spin_box_indices) == mag_ent.SBS
        assert len(mag_ent._tags) == len(mag_ent.atom)
        assert len(mag_ent.xyz) == len(mag_ent.atom)
        assert isinstance(mag_ent.Vu1, list)
        assert isinstance(mag_ent.Vu2, list)
        assert isinstance(mag_ent.Gii, list)
        assert isinstance(mag_ent._Gii_tmp, list)
        assert mag_ent.energies is None
        assert mag_ent.K is None
        assert mag_ent.K_consistency is None

    @pytest.mark.parametrize(
        "atom, l, orb",
        [
            (None, None, None),
            (None, None, [[1, 2]]),
            (None, None, [[1, 2], [1, 2]]),
            (None, 1, None),
            (None, 1, 1),
            (None, 1, [1]),
            (None, 1, [1, 2]),
            (None, 1, [[1, 2]]),
            (None, 1, [[1, 2], [1, 2]]),
            (None, [1], None),
            (None, [1], 1),
            (None, [1], [1]),
            (None, [1], [1, 2]),
            (None, [1], [[1, 2]]),
            (None, [1], [[1, 2], [1, 2]]),
            (None, [1, 2], None),
            (None, [1, 2], 1),
            (None, [1, 2], [1]),
            (None, [1, 2], [1, 2]),
            (None, [1, 2], [[1, 2]]),
            (None, [1, 2], [[1, 2], [1, 2]]),
            (None, [[1, 2]], None),
            (None, [[1, 2]], 1),
            (None, [[1, 2]], [1]),
            (None, [[1, 2]], [1, 2]),
            (None, [[1, 2]], [[1, 2]]),
            (None, [[1, 2]], [[1, 2], [1, 2]]),
            (None, [[1, 2], [1, 2]], None),
            (None, [[1, 2], [1, 2]], 1),
            (None, [[1, 2], [1, 2]], [1]),
            (None, [[1, 2], [1, 2]], [1, 2]),
            (None, [[1, 2], [1, 2]], [[1, 2]]),
            (None, [[1, 2], [1, 2]], [[1, 2], [1, 2]]),
            (1, 1, 1),
            (1, 1, [1]),
            (1, 1, [1, 2]),
            (1, 1, [[1, 2]]),
            (1, 1, [[1, 2], [1, 2]]),
            (1, [1], 1),
            (1, [1], [1]),
            (1, [1], [1, 2]),
            (1, [1], [[1, 2]]),
            (1, [1], [[1, 2], [1, 2]]),
            (1, [1, 2], 1),
            (1, [1, 2], [1]),
            (1, None, [[1, 2], [1, 2]]),
            (1, [[1, 2], [1, 2]], None),
            (1, [1, 2], [1, 2]),
            (1, [1, 2], [[1, 2]]),
            (1, [1, 2], [[1, 2], [1, 2]]),
            (1, [[1, 2]], 1),
            (1, [[1, 2]], [1]),
            (1, [[1, 2]], [1, 2]),
            (1, [[1, 2]], [[1, 2]]),
            (1, [[1, 2]], [[1, 2], [1, 2]]),
            (1, [[1, 2], [1, 2]], 1),
            (1, [[1, 2], [1, 2]], [1]),
            (1, [[1, 2], [1, 2]], [1, 2]),
            (1, [[1, 2], [1, 2]], [[1, 2]]),
            (1, [[1, 2], [1, 2]], [[1, 2], [1, 2]]),
            ([1], None, [[1, 2], [1, 2]]),
            ([1], 1, 1),
            ([1], 1, [1]),
            ([1], 1, [1, 2]),
            ([1], 1, [[1, 2]]),
            ([1], 1, [[1, 2], [1, 2]]),
            ([1], [1], 1),
            ([1], [1], [1]),
            ([1], [1], [1, 2]),
            ([1], [1], [[1, 2]]),
            ([1], [1], [[1, 2], [1, 2]]),
            ([1], [1, 2], 1),
            ([1], [1, 2], [1]),
            ([1], [1, 2], [1, 2]),
            ([1], [1, 2], [[1, 2]]),
            ([1], [1, 2], [[1, 2], [1, 2]]),
            ([1], [[1, 2]], 1),
            ([1], [[1, 2]], [1]),
            ([1], [[1, 2]], [1, 2]),
            ([1], [[1, 2]], [[1, 2]]),
            ([1], [[1, 2]], [[1, 2], [1, 2]]),
            ([1], [[1, 2], [1, 2]], None),
            ([1], [[1, 2], [1, 2]], 1),
            ([1], [[1, 2], [1, 2]], [1]),
            ([1], [[1, 2], [1, 2]], [1, 2]),
            ([1], [[1, 2], [1, 2]], [[1, 2]]),
            ([1], [[1, 2], [1, 2]], [[1, 2], [1, 2]]),
            ([1, 2], None, [[1, 2]]),
            ([1, 2], 1, 1),
            ([1, 2], 1, [1]),
            ([1, 2], 1, [1, 2]),
            ([1, 2], 1, [[1, 2]]),
            ([1, 2], 1, [[1, 2], [1, 2]]),
            ([1, 2], [1], 1),
            ([1, 2], [1], [1]),
            ([1, 2], [1], [1, 2]),
            ([1, 2], [1], [[1, 2]]),
            ([1, 2], [1], [[1, 2], [1, 2]]),
            ([1, 2], [1, 2], 1),
            ([1, 2], [1, 2], [1]),
            ([1, 2], [1, 2], [1, 2]),
            ([1, 2], [1, 2], [[1, 2]]),
            ([1, 2], [1, 2], [[1, 2], [1, 2]]),
            ([1, 2], [[1, 2]], None),
            ([1, 2], [[1, 2]], 1),
            ([1, 2], [[1, 2]], [1]),
            ([1, 2], [[1, 2]], [1, 2]),
            ([1, 2], [[1, 2]], [[1, 2]]),
            ([1, 2], [[1, 2]], [[1, 2], [1, 2]]),
            ([1, 2], [[1, 2], [1, 2]], 1),
            ([1, 2], [[1, 2], [1, 2]], [1]),
            ([1, 2], [[1, 2], [1, 2]], [1, 2]),
            ([1, 2], [[1, 2], [1, 2]], [[1, 2]]),
            ([1, 2], [[1, 2], [1, 2]], [[1, 2], [1, 2]]),
            ([[1, 2]], None, None),
            ([[1, 2]], None, 1),
            ([[1, 2]], None, [1]),
            ([[1, 2]], None, [1, 2]),
            ([[1, 2]], None, [[1, 2]]),
            ([[1, 2]], None, [[1, 2], [1, 2]]),
            ([[1, 2]], 1, None),
            ([[1, 2]], 1, 1),
            ([[1, 2]], 1, [1]),
            ([[1, 2]], 1, [1, 2]),
            ([[1, 2]], 1, [[1, 2]]),
            ([[1, 2]], 1, [[1, 2], [1, 2]]),
            ([[1, 2]], [1], None),
            ([[1, 2]], [1], 1),
            ([[1, 2]], [1], [1]),
            ([[1, 2]], [1], [1, 2]),
            ([[1, 2]], [1], [[1, 2]]),
            ([[1, 2]], [1], [[1, 2], [1, 2]]),
            ([[1, 2]], [1, 2], None),
            ([[1, 2]], [1, 2], 1),
            ([[1, 2]], [1, 2], [1]),
            ([[1, 2]], [1, 2], [1, 2]),
            ([[1, 2]], [1, 2], [[1, 2]]),
            ([[1, 2]], [1, 2], [[1, 2], [1, 2]]),
            ([[1, 2]], [[1, 2]], None),
            ([[1, 2]], [[1, 2]], 1),
            ([[1, 2]], [[1, 2]], [1]),
            ([[1, 2]], [[1, 2]], [1, 2]),
            ([[1, 2]], [[1, 2]], [[1, 2]]),
            ([[1, 2]], [[1, 2]], [[1, 2], [1, 2]]),
            ([[1, 2]], [[1, 2], [1, 2]], None),
            ([[1, 2]], [[1, 2], [1, 2]], 1),
            ([[1, 2]], [[1, 2], [1, 2]], [1]),
            ([[1, 2]], [[1, 2], [1, 2]], [1, 2]),
            ([[1, 2]], [[1, 2], [1, 2]], [[1, 2]]),
            ([[1, 2]], [[1, 2], [1, 2]], [[1, 2], [1, 2]]),
            ([[1, 2], [1, 2]], None, None),
            ([[1, 2], [1, 2]], None, 1),
            ([[1, 2], [1, 2]], None, [1]),
            ([[1, 2], [1, 2]], None, [1, 2]),
            ([[1, 2], [1, 2]], None, [[1, 2]]),
            ([[1, 2], [1, 2]], None, [[1, 2], [1, 2]]),
            ([[1, 2], [1, 2]], 1, None),
            ([[1, 2], [1, 2]], 1, 1),
            ([[1, 2], [1, 2]], 1, [1]),
            ([[1, 2], [1, 2]], 1, [1, 2]),
            ([[1, 2], [1, 2]], 1, [[1, 2]]),
            ([[1, 2], [1, 2]], 1, [[1, 2], [1, 2]]),
            ([[1, 2], [1, 2]], [1], None),
            ([[1, 2], [1, 2]], [1], 1),
            ([[1, 2], [1, 2]], [1], [1]),
            ([[1, 2], [1, 2]], [1], [1, 2]),
            ([[1, 2], [1, 2]], [1], [[1, 2]]),
            ([[1, 2], [1, 2]], [1], [[1, 2], [1, 2]]),
            ([[1, 2], [1, 2]], [1, 2], None),
            ([[1, 2], [1, 2]], [1, 2], 1),
            ([[1, 2], [1, 2]], [1, 2], [1]),
            ([[1, 2], [1, 2]], [1, 2], [1, 2]),
            ([[1, 2], [1, 2]], [1, 2], [[1, 2]]),
            ([[1, 2], [1, 2]], [1, 2], [[1, 2], [1, 2]]),
            ([[1, 2], [1, 2]], [[1, 2]], None),
            ([[1, 2], [1, 2]], [[1, 2]], 1),
            ([[1, 2], [1, 2]], [[1, 2]], [1]),
            ([[1, 2], [1, 2]], [[1, 2]], [1, 2]),
            ([[1, 2], [1, 2]], [[1, 2]], [[1, 2]]),
            ([[1, 2], [1, 2]], [[1, 2]], [[1, 2], [1, 2]]),
            ([[1, 2], [1, 2]], [[1, 2], [1, 2]], None),
            ([[1, 2], [1, 2]], [[1, 2], [1, 2]], 1),
            ([[1, 2], [1, 2]], [[1, 2], [1, 2]], [1]),
            ([[1, 2], [1, 2]], [[1, 2], [1, 2]], [1, 2]),
            ([[1, 2], [1, 2]], [[1, 2], [1, 2]], [[1, 2]]),
            ([[1, 2], [1, 2]], [[1, 2], [1, 2]], [[1, 2], [1, 2]]),
            # tests from decipher
            ([0, 0], [None, None], [[1], [1]]),
            ([0, 0], [None, None], [[1], [1, 2]]),
            ([0, 0], [None, [1]], [[1], None]),
            ([0, 0], [None, [1, 2]], [[1], None]),
            ([0, 0], [None, [None]], [[1], None]),
            ([0, 1], [None, None], [[1], [1]]),
            ([0, 1], [None, None], [[1], [1, 2]]),
            ([0, 1], [None, [1]], [[1], None]),
            ([0, 1], [None, [1, 2]], [[1], None]),
            ([0, 1], [None, [None]], [[1], None]),
        ],
    )
    def test_generation_exception(self, atom, l, orb):
        with pytest.raises(Exception):
            mag_ent = MagneticEntity(
                "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf",
                atom,
                l,
                orb,
            )
            print(mag_ent)

    @pytest.mark.parametrize(
        "tag1, tag2",
        [
            ("0Te(o:1)", "0Te(o:2)"),
            ("0Te(o:1)", "0Te(l:1)"),
            ("0Te(o:1)", "0Te(l:1-2)"),
            ("0Te(o:1)", "0Te(l:0-1-2-3-4-5-6-7-8-9-10-11-12)"),
            ("0Te(o:1)", "1Te(l:1)"),
            ("0Te(o:1)", "1Te(l:1-2)"),
            ("0Te(o:1)", "1Te(l:0-1-2-3-4-5-6-7-8-9-10-11-12)"),
        ],
    )
    def test_addition(self, tag1, tag2):
        atom1, l1, orb1 = decipher(tag1)
        atom2, l2, orb2 = decipher(tag2)
        mag_ent1 = MagneticEntity(
            "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf",
            atom1,
            l1,
            orb1,
        )
        mag_ent2 = MagneticEntity(
            "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf",
            atom2,
            l2,
            orb2,
        )

        new = mag_ent1 + mag_ent2
        assert new.tag == tag1 + "--" + tag2
        assert (
            new.spin_box_indices
            == np.concatenate((mag_ent1.spin_box_indices, mag_ent2.spin_box_indices))
        ).all()

    def test_reset(self):
        mag_ent = grogupy.load("./tests/test_magnetic_entity.pkl")

        mag_ent.Vu1 = 1
        mag_ent.Vu2 = None
        mag_ent.Gii = np.array([10])
        mag_ent._Gii_tmp = "[]"
        mag_ent.energies = 3.14
        mag_ent.K = (10, 20, 30)
        mag_ent.K_consistency = 2

        mag_ent.reset()
        assert mag_ent.Vu1 == []
        assert mag_ent.Vu2 == []
        assert mag_ent.Gii == []
        assert mag_ent._Gii_tmp == []
        assert mag_ent.energies == []
        assert mag_ent.K is None
        assert mag_ent.K_consistency is None

    def test_add_G_tmp(self):
        infile = "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"

        mag_ent = MagneticEntity(infile, 1)

        builder = grogupy.Builder(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
        builder.add_contour(grogupy.Contour(100, 1000, -10))
        builder.add_kspace(grogupy.Kspace())
        builder.add_hamiltonian(grogupy.Hamiltonian(infile))
        builder.magnetic_entities = [mag_ent]

        builder.finalize()

        mag_ent = builder.magnetic_entities[0]
        assert len(mag_ent.Gii) == 3
        assert len(mag_ent._Gii_tmp) == 3
        for g in mag_ent._Gii_tmp:
            assert g.sum() == 0
        for g in mag_ent.Gii:
            assert g.sum() == 0
        print(mag_ent._Gii_tmp[0].shape)
        Gk = np.zeros((100, builder.NO, builder.NO))
        Gk[0, 0, 0] = 1
        mag_ent.add_G_tmp(1, Gk, 1)
        for g in mag_ent.Gii:
            assert g.sum() == 0
        assert mag_ent._Gii_tmp[0].sum() == 0
        assert mag_ent._Gii_tmp[1].sum() == 0
        assert mag_ent._Gii_tmp[2].sum() == 0
        Gk[0, mag_ent.SBS, mag_ent.SBS] = 1
        mag_ent.add_G_tmp(1, Gk, 1)
        for g in mag_ent.Gii:
            assert g.sum() == 0
        assert mag_ent._Gii_tmp[0].sum() == 0
        assert mag_ent._Gii_tmp[1].sum() == 1
        assert mag_ent._Gii_tmp[2].sum() == 0

    def test_energies_and_anisotropy(self):
        infile = "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"

        mag_ent = MagneticEntity(infile, 1)

        builder = grogupy.Builder(
            np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), matlabmode=True
        )
        builder.add_contour(grogupy.Contour(100, 600))
        builder.add_kspace(grogupy.Kspace())
        builder.add_hamiltonian(grogupy.Hamiltonian(infile))
        builder.magnetic_entities = [mag_ent]

        builder.solve()

        mag_ent = builder.magnetic_entities[0]
        print(mag_ent.energies)
        # matlabmode True
        K1 = np.array(mag_ent.K)
        # matlabmode False
        mag_ent.fit_anisotropy_tensor(builder.ref_xcf_orientations)
        K2 = np.array(mag_ent.K)

        print(K1)
        print(K2)
        assert np.isclose(K1, K2).all()


if __name__ == "__main__":
    pass
