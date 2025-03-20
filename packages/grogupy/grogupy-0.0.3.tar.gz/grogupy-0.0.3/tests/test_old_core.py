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

from grogupy._core.core import (
    calc_Vu,
    hsk,
    make_contour,
    make_kset,
    onsite_projection,
    parallel_Gk,
    sequential_Gk,
)


@pytest.mark.parametrize(
    "mat, samples",
    [
        (np.array([[1, 0], [1, 4]]), np.array([1 + 1j, 2 + 2j])),
        (np.array([[1, 1j], [1j, 1]]), np.array([1 + 1j, 2 + 2j])),
    ],
)
def test_parallel_sequential_gk(mat, samples):
    # Test case with small matrices
    HK = np.array(mat, dtype=complex)
    SK = np.array(mat, dtype=complex)
    samples = samples
    eset = len(samples)

    result1 = parallel_Gk(HK, SK, samples, eset)
    result2 = sequential_Gk(HK, SK, samples, eset)

    assert_array_almost_equal(result1, result2)


def test_onsite_projection():
    # Create test matrix
    matrix = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
    idx1 = np.array([0, 1])
    idx2 = np.array([1, 2])

    result = onsite_projection(matrix, idx1, idx2)
    expected = np.array([[2, 3], [5, 6]])

    assert_array_equal(result[0], expected)


def test_calc_vu():
    # Simple test case
    H = np.array([[1, 0], [0, -1]], dtype=complex)
    Tu = np.array([[0, 1], [1, 0]], dtype=complex)

    Vu1, Vu2 = calc_Vu(H, Tu)

    # Expected results based on commutator calculations
    expected_Vu1 = 1j / 2 * (H @ Tu - Tu @ H)
    expected_Vu2 = 1 / 8 * ((Tu @ H - H @ Tu) @ Tu - Tu @ (Tu @ H - H @ Tu))

    assert_array_almost_equal(Vu1, expected_Vu1)
    assert_array_almost_equal(Vu2, expected_Vu2)


def test_make_contour():
    emin, emax = -1.0, 1.0
    enum = 5
    p = 10

    ze, we = make_contour(emin, emax, enum, p)

    # Basic checks
    assert len(ze) == enum
    assert len(we) == enum
    assert np.all(np.imag(ze) >= 0)  # Points should be in upper half plane
    assert np.all((np.real(ze) >= emin) & (np.real(ze) <= emax))


def test_make_kset():
    # Test Gamma point
    kset = make_kset()
    assert_array_equal(kset, np.array([[0, 0, 0]]))

    # Test 1D
    kset = make_kset(kset=[3, 1, 1])
    expected = np.array([[0, 0, 0], [1 / 3, 0, 0], [-1 / 3, 0, 0]])
    assert_array_almost_equal(np.sort(kset, axis=0), np.sort(expected, axis=0))

    # Test 2D
    kset = make_kset(kset=[2, 2, 1])
    expected = np.array([[0, 0, 0], [0, 0.5, 0], [0.5, 0, 0], [0.5, 0.5, 0]])
    assert_array_almost_equal(np.sort(kset, axis=0), np.sort(expected, axis=0))


@pytest.mark.parametrize(
    "k, sc_off",
    [
        (np.array([0, 0, 0.1]), np.array([[1, 0, 0], [0, 1, 0]])),
        (np.array([0, 0.1, 0]), np.array([[1, 0, 0], [0, 1, 0]])),
        (np.array([0.1, 0, 0]), np.array([[1, 0, 0], [0, 1, 0]])),
    ],
)
def test_hsk(k, sc_off):
    # Simple test case
    H = np.array([[[1, 0], [0, 1]], [[2, 0], [0, 2]]])
    S = np.array([[[1, 0], [0, 1]], [[0, 0], [0, 0]]])

    HK, SK = hsk(H, S, sc_off, k)

    phases = np.exp(-1j * 2 * np.pi * k @ sc_off.T)
    # phases applied to the hamiltonian
    expected_HK = np.einsum("abc,a->bc", H, phases)
    expected_SK = np.einsum("abc,a->bc", S, phases)

    assert_array_almost_equal(HK, expected_HK)
    assert_array_almost_equal(SK, expected_SK)
