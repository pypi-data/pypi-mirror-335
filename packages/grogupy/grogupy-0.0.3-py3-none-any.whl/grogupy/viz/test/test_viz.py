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
import plotly.graph_objs as go
import pytest

import grogupy
from grogupy.viz import (
    plot_contour,
    plot_DM,
    plot_kspace,
    plot_magnetic_entities,
    plot_pairs,
)

pytestmark = [pytest.mark.viz]


@pytest.fixture
def setup():
    return grogupy.load("./tests/test_builder.pkl")


class TestPlots:
    def test_contour(self, setup):
        fig = plot_contour(setup.contour)
        print(type(fig))
        assert isinstance(fig, go.Figure)

    def test_kspace(self, setup):
        fig = plot_kspace(setup.kspace)
        assert isinstance(fig, go.Figure)

    def test_magnetic_entities(self, setup):
        fig = plot_magnetic_entities(setup.magnetic_entities)
        assert isinstance(fig, go.Figure)

    @pytest.mark.parametrize("connect", [True, False])
    def test_pairs(self, setup, connect):
        fig = plot_pairs(setup.pairs, connect)
        assert isinstance(fig, go.Figure)

    @pytest.mark.parametrize("rescale", [-1, 0, 0.1, 1])
    def test_DM(self, setup, rescale):
        fig = plot_DM(setup.pairs, rescale)
        assert isinstance(fig, go.Figure)


if __name__ == "__main__":
    pass
