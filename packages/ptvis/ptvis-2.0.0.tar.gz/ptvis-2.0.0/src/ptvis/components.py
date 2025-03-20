"""Components of the periodic table."""

from __future__ import annotations

from typing import Literal

import numpy
from numpy.typing import ArrayLike
import plotly

from .utils import make_annulus_sector_shape


__all__ = ["make_circular_sector_cells", "make_plain_cells"]


def make_plain_cells(
    xs: ArrayLike,
    ys: ArrayLike,
    widths: ArrayLike,
    heights: ArrayLike,
    texts: ArrayLike | None = None,
    colors: ArrayLike | None = None,
    shape: Literal["circle", "square"] = "square",
) -> tuple[
    list[plotly.graph_objects.layout.Shape],
    plotly.graph_objects.Scatter,
]:
    """Make plain cells.

    Parameters
    ----------
    xs : array-like of float
        X coordinates of centers of cells.
    ys : array-like of float
        Y coordinates of centers of cells.
    widths : array-like of float
        Widths of cells.
    heights : array-like of float
        Heights of cells.
    texts : array-like of str, optional
        Texts of cells.
    colors : array-like of str, optional
        Fill colors of cells.
    shape : {'circle', 'square'}, optional
        Shape of a cell.

    Returns
    -------
    shapes : list of plotly.graph_objects.layout.Shape
        Shape objects for cells.
    text_scatter : plotly.graph_objects.Scatter
        Scatter object for texts.
    """
    arrays = {
        "x": xs,
        "y": ys,
        "width": widths,
        "height": heights,
    }
    if texts is not None:
        arrays["text"] = texts
    if colors is not None:
        arrays["color"] = colors
    arrays = {key: numpy.asarray(array) for key, array in arrays.items()}

    array_shapes = {array.shape for array in arrays.values()}
    if len(array_shapes) != 1:
        raise ValueError("array-like arguments must be of equal shape")
    array_shape = next(iter(array_shapes))
    if len(array_shape) != 1:
        raise ValueError("array-like arguments must be 1-dimensional")
    n_cells = array_shape[0]

    if shape == "square":
        shape_type = "rect"
    elif shape == "circle":
        shape_type = "circle"
    else:
        raise ValueError("`shape` must be 'square' or 'circle'")
    shapes = [
        plotly.graph_objects.layout.Shape(
            type=shape_type,
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
            fillcolor=color,
        )
        for x0, x1, y0, y1, color in zip(
            arrays["x"] - 0.5*arrays["width"],
            arrays["x"] + 0.5*arrays["width"],
            arrays["y"] - 0.5*arrays["height"],
            arrays["y"] + 0.5*arrays["height"],
            arrays.get("color", [None] * n_cells),
        )
    ]

    text_scatter = plotly.graph_objects.Scatter(
        x=arrays["x"],
        y=arrays["y"],
        mode="text",
        text=arrays.get("text"),
        showlegend=False,
    )

    return shapes, text_scatter


def make_circular_sector_cells(
    xs: ArrayLike,
    ys: ArrayLike,
    start_angles: ArrayLike,
    stop_angles: ArrayLike,
    radii: ArrayLike,
    hole_radius: float = 0.,
    texts: ArrayLike | None = None,
    colors: ArrayLike | None = None,
) -> tuple[
    list[plotly.graph_objects.layout.Shape],
    plotly.graph_objects.Scatter,
]:
    """Make cells consisting of circular sectors.

    Parameters
    ----------
    xs : array-like of float
        X coordinates of centers of circular sectors.
    ys : array-like of float
        Y coordinates of centers of circular sectors.
    start_angles : array-like of float
        Angles at which circular sectors start.
    stop_angles : array-like of float
        Angles at which circular sectors stop.
    radii : array-like of float
        Radii of circular sectors.
    hole_radius : float, optional
        Radius of a hole of a cell.
    texts : array-like of str, optional
        Texts of circular sectors.
    colors : array-like of str, optional
        Fill colors of circular sectors.

    Returns
    -------
    shapes : list of plotly.graph_objects.layout.Shape
        Shape objects for circular sectors.
    text_scatter : plotly.graph_objects.Scatter
        Scatter object for texts.
    """
    arrays = {
        "x": xs,
        "y": ys,
        "start_angle": start_angles,
        "stop_angle": stop_angles,
        "radius": radii,
    }
    if texts is not None:
        arrays["text"] = texts
    if colors is not None:
        arrays["color"] = colors
    arrays = {key: numpy.asarray(array) for key, array in arrays.items()}

    array_shapes = {array.shape for array in arrays.values()}
    if len(array_shapes) != 1:
        raise ValueError("array-like arguments must be of equal shape")
    array_shape = next(iter(array_shapes))
    if len(array_shape) != 1:
        raise ValueError("array-like arguments must be 1-dimensional")

    shapes = [
        make_annulus_sector_shape(
            x,
            y,
            hole_radius,
            radius,
            start_angle,
            stop_angle,
            connect_arcs=(abs(stop_angle-start_angle) != 360),
        )
        for x, y, radius, start_angle, stop_angle in zip(
            arrays["x"],
            arrays["y"],
            arrays["radius"],
            arrays["start_angle"],
            arrays["stop_angle"],
        )
    ]
    if "color" in arrays:
        for shape, color in zip(shapes, arrays["color"]):
            shape.update(fillcolor=color)

    mid_radii = 0.5 * (hole_radius+arrays["radius"])
    mid_angles = numpy.deg2rad(
        0.5 * (arrays["start_angle"]+arrays["stop_angle"]),
    )
    text_scatter = plotly.graph_objects.Scatter(
        x=arrays["x"]+mid_radii*numpy.cos(mid_angles),
        y=arrays["y"]+mid_radii*numpy.sin(mid_angles),
        mode="text",
        text=arrays.get("text"),
        showlegend=False,
    )

    return shapes, text_scatter
