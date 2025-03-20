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
import os

import pytest

import grogupy
import grogupy.batch
from grogupy.io.io import *

pytestmark = [pytest.mark.io]


class TestIO:
    def test_load_save(self):
        builder = grogupy.load("./tests/test_builder.pkl")
        assert isinstance(builder, grogupy.Builder)
        grogupy.save(builder, "./tests/test_builder_temp.pkl")
        builder2 = grogupy.load("./tests/test_builder_temp.pkl")
        assert isinstance(builder2, grogupy.Builder)
        assert builder == builder2

        hamiltonian = grogupy.load("./tests/test_hamiltonian.pkl")
        assert isinstance(hamiltonian, grogupy.Hamiltonian)
        grogupy.save(hamiltonian, "./tests/test_hamiltonian_temp.pkl")
        hamiltonian2 = grogupy.load("./tests/test_hamiltonian_temp.pkl")
        assert isinstance(hamiltonian2, grogupy.Hamiltonian)
        assert hamiltonian == hamiltonian2

        contour = grogupy.load("./tests/test_contour.pkl")
        assert isinstance(contour, grogupy.Contour)
        grogupy.save(contour, "./tests/test_contour_temp.pkl")
        contour2 = grogupy.load("./tests/test_contour_temp.pkl")
        assert isinstance(contour2, grogupy.Contour)
        assert contour == contour2

        kspace = grogupy.load("./tests/test_kspace.pkl")
        assert isinstance(kspace, grogupy.Kspace)
        grogupy.save(kspace, "./tests/test_kspace_temp.pkl")
        kspace2 = grogupy.load("./tests/test_kspace_temp.pkl")
        assert isinstance(kspace2, grogupy.Kspace)
        assert kspace == kspace2

        default_timer = grogupy.load("./tests/test_default_timer.pkl")
        assert isinstance(default_timer, grogupy.batch.DefaultTimer)
        grogupy.save(default_timer, "./tests/test_default_timer_temp.pkl")
        default_timer2 = grogupy.load("./tests/test_default_timer_temp.pkl")
        assert isinstance(default_timer2, grogupy.batch.DefaultTimer)
        assert default_timer == default_timer2

        mag_ent = grogupy.load("./tests/test_magnetic_entity.pkl")
        assert isinstance(mag_ent, grogupy.MagneticEntity)
        grogupy.save(mag_ent, "./tests/test_magnetic_entity_temp.pkl")
        mag_ent2 = grogupy.load("./tests/test_magnetic_entity_temp.pkl")
        assert isinstance(mag_ent2, grogupy.MagneticEntity)
        assert mag_ent == mag_ent2

        pair = grogupy.load("./tests/test_pair.pkl")
        assert isinstance(pair, grogupy.Pair)
        grogupy.save(pair, "./tests/test_pair_temp.pkl")
        pair2 = grogupy.load("./tests/test_pair_temp.pkl")
        assert isinstance(pair2, grogupy.Pair)
        assert pair == pair2

    def test_load_save_Builder(self):
        builder = load_Builder("./tests/test_builder.pkl")
        assert isinstance(builder, grogupy.Builder)
        grogupy.save(builder, "./tests/test_builder_temp.pkl")
        builder2 = grogupy.load("./tests/test_builder_temp.pkl")
        assert isinstance(builder2, grogupy.Builder)
        assert builder == builder2

    def test_load_save_Hamiltonian(self):
        hamiltonian = load_Hamiltonian("./tests/test_hamiltonian.pkl")
        assert isinstance(hamiltonian, grogupy.Hamiltonian)
        grogupy.save(hamiltonian, "./tests/test_hamiltonian_temp.pkl")
        hamiltonian2 = grogupy.load("./tests/test_hamiltonian_temp.pkl")
        assert isinstance(hamiltonian2, grogupy.Hamiltonian)
        assert hamiltonian == hamiltonian2

    def test_load_save_Contour(self):
        contour = load_Contour("./tests/test_contour.pkl")
        assert isinstance(contour, grogupy.Contour)
        grogupy.save(contour, "./tests/test_contour_temp.pkl")
        contour2 = grogupy.load("./tests/test_contour_temp.pkl")
        print(type(contour2))
        assert isinstance(contour2, grogupy.Contour)
        assert contour == contour2

    def test_load_save_Kspace(self):
        kspace = load_Kspace("./tests/test_kspace.pkl")
        assert isinstance(kspace, grogupy.Kspace)
        grogupy.save(kspace, "./tests/test_kspace_temp.pkl")
        kspace2 = grogupy.load("./tests/test_kspace_temp.pkl")
        assert isinstance(kspace2, grogupy.Kspace)
        assert kspace == kspace2

    def test_load_save_DefaultTimer(self):
        default_timer = load_DefaultTimer("./tests/test_default_timer.pkl")
        assert isinstance(default_timer, grogupy.batch.DefaultTimer)
        grogupy.save(default_timer, "./tests/test_default_timer_temp.pkl")
        default_timer2 = grogupy.load("./tests/test_default_timer_temp.pkl")
        assert isinstance(default_timer2, grogupy.batch.DefaultTimer)
        assert default_timer == default_timer2

    def test_load_save_MagneticEntity(self):
        magnetic_entity = load_MagneticEntity("./tests/test_magnetic_entity.pkl")
        assert isinstance(magnetic_entity, grogupy.MagneticEntity)
        grogupy.save(magnetic_entity, "./tests/test_magnetic_entity_temp.pkl")
        magnetic_entity2 = grogupy.load("./tests/test_magnetic_entity_temp.pkl")
        assert isinstance(magnetic_entity2, grogupy.MagneticEntity)
        assert magnetic_entity == magnetic_entity2

    def test_load_save_Pair(self):
        pair = load_Pair("./tests/test_pair.pkl")
        assert isinstance(pair, grogupy.Pair)
        grogupy.save(pair, "./tests/test_pair_temp.pkl")
        pair2 = grogupy.load("./tests/test_pair_temp.pkl")
        assert isinstance(pair2, grogupy.Pair)
        assert pair == pair2

    def test_load_save_magnopy(self):
        builder = load_Builder("./tests/test_builder.pkl")
        save_magnopy(builder, "./tests/test_magnopy")
        data = read_magnopy("./tests/test_magnopy.magnopy.txt")
        print(data)
        raise Exception("Not implemented test!")

    def test_read_fdf(self):
        raise Exception("Not implemented test!")

    def test_read_command_line(self):
        raise Exception("Not implemented test!")

    def cleanup(self):
        os.remove("./tests/test_magnopy.magnopy.txt")
        os.remove("./tests/test_pair_temp.pkl")
        os.remove("./tests/test_magnetic_entity_temp.pkl")
        os.remove("./tests/test_default_timer_temp.pkl")
        os.remove("./tests/test_kspace_temp.pkl")
        os.remove("./tests/test_contour_temp.pkl")
        os.remove("./tests/test_hamiltonian_temp.pkl")
        os.remove("./tests/test_builder_temp.pkl")


if __name__ == "__main__":
    pass
