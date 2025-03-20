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
"""
Visualization functions
=======================

.. currentmodule:: grogupy.viz.viz

.. autosummary::
   :toctree: _generated/

   plot_contour
   plot_kspace
   plot_magnetic_entities
   plot_pairs
   plot_DM

"""

from typing import TYPE_CHECKING

from ..physics import Builder

if TYPE_CHECKING:
    from ..physics.contour import Contour
    from ..physics.kspace import Kspace
    from ..physics.magnetic_entity import MagneticEntity
    from ..physics.pair import Pair

import numpy as np
import plotly.graph_objs as go


def plot_contour(contour: "Contour") -> go.Figure:
    """Creates a plot from the contour sample points.

    Parameters
    ----------
    contour : Contour
        Contour class that contains the energy samples and weights

    Returns
    -------
    plotly.graph_objs.go.Figure
        The created figure
    """

    # Create the scatter plot
    fig = go.Figure(
        data=go.Scatter(x=contour.samples.real, y=contour.samples.imag, mode="markers")
    )

    # Update the layout
    fig.update_layout(
        autosize=False,
        width=1200,
        height=700,
        title="Energy contour integral",
        xaxis_title="Real axis [eV]",
        yaxis_title="Imaginary axis [eV]",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),
    )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    return fig


def plot_kspace(kspace: "Kspace") -> go.Figure:
    """Creates a plot from the Brillouin zone sample points.

    Parameters
    ----------
    kspace : Kspace
        Kspace class that contains the Brillouin-zone samples and weights

    Returns
    -------
    plotly.graph_objs.go.Figure
        The created figure
    """

    # Create the scatter plot
    # Create 3D scatter plot
    trace = go.Scatter3d(
        name=f"Kpoints",
        x=kspace.kpoints[:, 0],
        y=kspace.kpoints[:, 1],
        z=kspace.kpoints[:, 2],
        mode="markers",
        marker=dict(
            size=5,
            color=kspace.weights,
            colorscale="Viridis",
            opacity=1,
            colorbar=dict(title="Weights of kpoints", x=0.75),
        ),
    )

    # Update the layout

    layout = go.Layout(
        autosize=False,
        width=1200,
        height=700,
        scene=dict(
            aspectmode="data",
            xaxis=dict(title="X Axis", showgrid=True, gridwidth=1),
            yaxis=dict(title="Y Axis", showgrid=True, gridwidth=1),
            zaxis=dict(title="Z Axis", showgrid=True, gridwidth=1),
        ),
    )

    # Create figure and show
    fig = go.Figure(data=[trace], layout=layout)

    return fig


def plot_magnetic_entities(
    magnetic_entities: list["MagneticEntity"],
) -> go.Figure:
    """Creates a plot from a list of magnetic entities.

    Parameters
    ----------
    magnetic_entities : list[MagneticEntity]
        The magnetic entities that contain the tags and coordinates

    Returns
    -------
    plotly.graph_objs.go.Figure
        The created figure
    """

    # conversion line for the case when it is set as the plot function of a builder
    if isinstance(magnetic_entities, Builder):
        magnetic_entities = magnetic_entities.magnetic_entities
    elif not isinstance(magnetic_entities, list):
        magnetic_entities = [magnetic_entities]

    tags = [m.tag for m in magnetic_entities]
    coords = [m.xyz for m in magnetic_entities]

    colors = ["red", "green", "blue", "purple", "orange", "cyan", "magenta"]
    colors = colors * (len(coords) // len(colors) + 1)

    # Create figure
    fig = go.Figure()
    for coord, color, tag in zip(coords, colors, tags):
        fig.add_trace(
            go.Scatter3d(
                name=tag,
                x=coord[:, 0],
                y=coord[:, 1],
                z=coord[:, 2],
                mode="markers",
                marker=dict(size=10, opacity=0.8, color=color),
            )
        )

    # Create layout
    fig.update_layout(
        autosize=False,
        width=1200,
        height=700,
        scene=dict(
            aspectmode="data",
            xaxis=dict(title="X Axis", showgrid=True, gridwidth=1),
            yaxis=dict(title="Y Axis", showgrid=True, gridwidth=1),
            zaxis=dict(title="Z Axis", showgrid=True, gridwidth=1),
        ),
    )

    return fig


def plot_pairs(pairs: list["Pair"], connect: bool = False) -> go.Figure:
    """Creates a plot from a list of pairs.

    Parameters
    ----------
    pairs : Union[list[Pair], None]
        The pairs that contain the tags and coordinates
    connect : bool, optional
        Wether to connect the pairs or not, by default False

    Returns
    -------
    plotly.graph_objs.go.Figure
        The created figure
    """

    # conversion line for the case when it is set as the plot function of a builder
    if isinstance(pairs, Builder):
        pairs = pairs.pairs
    elif not isinstance(pairs, list):
        pairs = [pairs]

    # the centers can contain many atoms
    centers = [p.xyz[0] for p in pairs]

    # find unique centers
    uniques = []

    def in_unique(c):
        for u in uniques:
            if c.shape == u.shape:
                if np.all(c == u):
                    return True
        return False

    for c in centers:
        if not in_unique(c):
            uniques.append(c)
    # findex indexes for the same center
    idx = [[] for u in uniques]
    for i, u in enumerate(uniques):
        for j, c in enumerate(centers):
            if c.shape == u.shape:
                if np.all(c == u):
                    idx[i].append(j)

    center_tags = np.array([p.tags[0] for p in pairs])

    interacting_atoms = np.array([p.xyz[1] for p in pairs], dtype=object)
    interacting_tags = np.array(
        [p.tags[1] + ", ruc:" + str(p.supercell_shift) for p in pairs]
    )

    colors = ["red", "green", "blue", "purple", "orange", "cyan", "magenta"]
    colors = colors * (len(centers) // len(colors) + 1)

    # Create figure
    fig = go.Figure()
    for i in range(len(idx)):
        center = centers[idx[i][0]]
        center_tag = center_tags[idx[i][0]]
        color = colors[i]
        # Create 3D scatter plot
        fig.add_trace(
            go.Scatter3d(
                name="Center:" + center_tag,
                x=center[:, 0],
                y=center[:, 1],
                z=center[:, 2],
                mode="markers",
                marker=dict(size=10, opacity=0.8, color=color),
            )
        )
        for interacting_atom, interacting_tag in zip(
            interacting_atoms[idx[i]], interacting_tags[idx[i]]
        ):
            legend_group = f"pair {center_tag}-{interacting_atom}"
            fig.add_trace(
                go.Scatter3d(
                    name=interacting_tag,
                    x=interacting_atom[:, 0],
                    y=interacting_atom[:, 1],
                    z=interacting_atom[:, 2],
                    legendgroup=legend_group,
                    mode="markers",
                    marker=dict(size=5, opacity=0.5, color=color),
                )
            )
            if connect:
                fig.add_trace(
                    go.Scatter3d(
                        x=[center.mean(axis=0)[0], interacting_atom.mean(axis=0)[0]],
                        y=[center.mean(axis=0)[1], interacting_atom.mean(axis=0)[1]],
                        z=[center.mean(axis=0)[2], interacting_atom.mean(axis=0)[2]],
                        mode="lines",
                        legendgroup=legend_group,
                        showlegend=False,
                        line=dict(color=color),
                    )
                )

    # Create layout
    fig.update_layout(
        autosize=False,
        width=1200,
        height=700,
        scene=dict(
            aspectmode="data",
            xaxis=dict(title="X Axis", showgrid=True, gridwidth=1),
            yaxis=dict(title="Y Axis", showgrid=True, gridwidth=1),
            zaxis=dict(title="Z Axis", showgrid=True, gridwidth=1),
        ),
    )

    return fig


def plot_DM(pairs: list["Pair"], rescale: float = 1) -> go.Figure:
    """Creates a plot of the DM vectors from a list of pairs.

    It can only use pairs from a finished simulation. The magnitude of
    the vectors are in meV.

    Parameters
    ----------
    pairs : Union[list[Pair], None]
        The pairs that contain the tags, coordinates and the DM vectors
    rescale : float, optional
        The length of the vectors are rescaled by this, by default 1

    Returns
    -------
    plotly.graph_objs.go.Figure
        The created figure
    """

    # conversion line for the case when it is set as the plot function of a builder
    if isinstance(pairs, Builder):
        pairs = pairs.pairs
    elif not isinstance(pairs, list):
        pairs = [pairs]

    # Define some example vectors
    vectors = np.array([p.D_meV * rescale for p in pairs])
    # Define origins (optional)
    origins = np.array(
        [(p.M1.xyz_center + p.M2.xyz_center + p.supercell_shift_xyz) / 2 for p in pairs]
    )

    n_vectors = len(vectors)

    labels = ["-->".join(p.tags) + ", ruc:" + str(p.supercell_shift) for p in pairs]

    colors = ["red", "green", "blue", "purple", "orange", "cyan", "magenta"]
    colors = colors * (n_vectors // len(colors) + 1)

    # Create figure
    fig = go.Figure()

    # Maximum vector magnitude for scaling
    max_magnitude = max(np.linalg.norm(v) for v in vectors)

    # Add each vector as a cone
    for i, (vector, origin, label, color) in enumerate(
        zip(vectors, origins, labels, colors)
    ):
        # End point of the vector
        end = origin + vector

        legend_group = f"vector_{i}"

        # Add a line for the vector
        fig.add_trace(
            go.Scatter3d(
                x=[origin[0], end[0]],
                y=[origin[1], end[1]],
                z=[origin[2], end[2]],
                mode="lines",
                line=dict(color=color, width=5),
                name=label,
                legendgroup=legend_group,
                showlegend=True,
            )
        )

        # Add a cone at the end to represent the arrow head
        u, v, w = vector
        fig.add_trace(
            go.Cone(
                x=[end[0]],
                y=[end[1]],
                z=[end[2]],
                u=[u / 5],  # Scale down for better visualization
                v=[v / 5],
                w=[w / 5],
                colorscale=[[0, color], [1, color]],
                showscale=False,
                sizemode="absolute",
                sizeref=max_magnitude / 10,
                legendgroup=legend_group,
                showlegend=False,
            )
        )

    # Set layout properties

    # Create layout
    fig.update_layout(
        autosize=False,
        width=1200,
        height=700,
        scene=dict(
            aspectmode="data",
            xaxis=dict(title="X Axis", showgrid=True, gridwidth=1),
            yaxis=dict(title="Y Axis", showgrid=True, gridwidth=1),
            zaxis=dict(title="Z Axis", showgrid=True, gridwidth=1),
        ),
    )

    return fig


if __name__ == "__main__":
    pass
