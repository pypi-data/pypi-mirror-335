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
import sisl
from numpy.testing import assert_array_almost_equal, assert_array_equal

from grogupy._core.constants import TAU_X, TAU_Y, TAU_Z
from grogupy._core.core import parallel_Gk, sequential_Gk
from grogupy.physics.hamiltonian import Hamiltonian


@pytest.fixture
def test_hamiltonian():
    """Create a test Hamiltonian instance"""
    # Use the provided input.fdf file in tests directory
    infile = "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"
    scf_xcf_orientation = np.array([0, 0, 1])
    return Hamiltonian(infile, scf_xcf_orientation)


def test_hamiltonian_initialization(test_hamiltonian):
    """Test if Hamiltonian is initialized correctly"""
    h = test_hamiltonian

    # Check basic properties
    assert isinstance(h._dh, sisl.physics.Hamiltonian)
    assert (
        h.infile
        == "/Users/danielpozsar/Downloads/nojij/Fe3GeTe2/monolayer/soc/lat3_791/Fe3GeTe2.fdf"
    )
    assert_array_equal(h.scf_xcf_orientation, np.array([0, 0, 1]))
    assert_array_equal(h.orientation, np.array([0, 0, 1]))

    # Check if matrices are properly initialized
    assert h.H is not None
    assert h.S is not None
    assert h.hTRS is not None
    assert h.hTRB is not None
    assert h.H_XCF is not None
    assert h.XCF is not None


def test_geometry_properties(test_hamiltonian):
    """Test geometry-related properties"""
    h = test_hamiltonian

    assert isinstance(h.NO, (int, np.int64, np.int32))
    assert h.NO > 0
    assert h.cell.shape == (3, 3)
    assert isinstance(h.nsc, (tuple, np.ndarray))
    assert h.sc_off.shape[1] == 3
    assert isinstance(h.uc_in_sc_index, (int, np.int64, np.int32))


def test_rotate(test_hamiltonian):
    """Test rotation of exchange field"""
    h = test_hamiltonian

    # Store original values
    original_xcf = h.XCF.copy()
    original_h = h.H.copy()

    # Rotate to new orientation
    new_orientation = np.array([1, 0, 0])
    h.rotate(new_orientation)

    # Check if orientation was updated
    assert_array_equal(h.orientation, new_orientation)

    # Check if matrices changed
    assert not np.allclose(h.XCF, original_xcf)
    assert not np.allclose(h.H, original_h)


def test_hksk(test_hamiltonian):
    """Test k-point Hamiltonian setup"""
    h = test_hamiltonian

    # Test at Gamma point
    Hk, Sk = h.HkSk((0, 0, 0))
    assert Hk is not None
    assert Sk is not None
    assert Hk.shape == (h.NO * 2, h.NO * 2)  # *2 for spin
    assert Sk.shape == (h.NO * 2, h.NO * 2)

    # Test at arbitrary k-point
    Hk, Sk = h.HkSk((0.5, 0.5, 0.5))
    assert Hk is not None
    assert Sk is not None
    assert Hk.shape == (h.NO * 2, h.NO * 2)  # *2 for spin
    assert Sk.shape == (h.NO * 2, h.NO * 2)


def test_greens_functions(test_hamiltonian):
    """Test Green's function calculations"""
    h = test_hamiltonian

    # Setup k-point Hamiltonian first
    Hk, Sk = h.HkSk((0, 0, 0))

    # Test parameters
    samples = np.array([1 + 1j, 2 + 2j], dtype=complex)
    eset = 2

    # Test parallel calculation
    Gk = parallel_Gk(Hk, Sk, samples, eset)
    assert Gk is not None
    assert Gk.shape == (eset, h.NO * 2, h.NO * 2)

    # Store result for comparison
    parallel_result = Gk.copy()

    # Test sequential calculation
    Gk = sequential_Gk(Hk, Sk, samples, eset)
    assert Gk is not None
    assert Gk.shape == (eset, h.NO * 2, h.NO * 2)

    # Results should be the same
    assert_array_almost_equal(Gk, parallel_result)


def test_copy(test_hamiltonian):
    """Test deep copy functionality"""
    h = test_hamiltonian
    h_copy = h.copy()

    # Check if it's a different object
    assert h_copy is not h

    # Check if attributes are equal but separate
    assert_array_equal(h_copy.H, h.H)
    assert_array_equal(h_copy.S, h.S)
    assert_array_equal(h_copy.orientation, h.orientation)

    # Modify copy and check if original is unchanged
    h_copy.rotate(np.array([1, 0, 0]))
    assert not np.allclose(h_copy.H, h.H)
    assert not np.allclose(h_copy.orientation, h.orientation)
