"""Utilities."""

from __future__ import annotations

from collections.abc import Iterable
import itertools

import numpy
from numpy.typing import ArrayLike, NDArray
import plotly


__all__ = [
    "add_annotations",
    "add_shapes",
    "linearly_transform",
    "make_annulus_sector_shape",
]


def make_annulus_sector_shape(
    x: float,
    y: float,
    inner_radius: float,
    outer_radius: float,
    start_angle: float,
    stop_angle: float,
    connect_arcs: bool | None = True,
    tol: float = 1e-4,
) -> plotly.graph_objects.layout.Shape:
    """Make a shape object of an annulus sector.

    Parameters
    ----------
    x : float
        X coordinate of a center.
    y : float
        Y coordinate of a center.
    inner_radius : float
        Radius of an inner arc.
    outer_radius : float
        Radius of an outer arc.
    start_angle : float
        Angle from which an annulus sector starts in degrees.
    stop_angle : float
        Angle at which an annulus sector stops in degrees.
    connect_arcs : bool, optional
        If ``True``, endpoints of inner and outer arcs are connected by lines.
    tol : float, optional
        Tolerance for the relative error of the radius of an arc.

    Returns
    -------
    plotly.graph_objects.layout.Shape
        Shape object of an annulus sector.

    Notes
    -----
    An arc is approximated by a cubic Bézier curve [1]_.

    References
    ----------
    .. [1] T. Dokken, M. Dæhlen, T. Lyche, and K. Mørken, *Good approximation
       of circles by curvature-continuous Bézier curves*, Comput. Aided Geom.
       Des. **7**, 33 (1990).
    """
    if tol <= 0:
        raise ValueError("`tol` must be > 0")

    start_angle: float = numpy.deg2rad(start_angle)
    stop_angle: float = numpy.deg2rad(stop_angle)

    # Calculate a central angle causing a given maximum relative error of the
    # squared radius. The error, epsilon, is
    #     epsilon = 4/27 sin(alpha/4)^6 / cos(alpha/4)^2,
    # where alpha is a central angle. This equation can be rearranged as
    #     t^3 - c t^2 - c = 0
    # by substituting t = tan(alpha/4), where c = (27/4 epsilon)^(1/2).
    epsilon = tol * (tol+2)
    c = numpy.sqrt(6.75 * epsilon)
    neg_half_q = 0.5 * c * (1+0.5*epsilon)
    sqrt_d = 0.5 * c * numpy.sqrt(1+epsilon)
    u = numpy.cbrt(neg_half_q - sqrt_d)
    v = numpy.cbrt(neg_half_q + sqrt_d)
    t = u + v + c/3
    max_angle_step = 4 * numpy.arctan(t)

    n_segments = int(numpy.ceil((stop_angle - start_angle) / max_angle_step))
    angles, angle_step = numpy.linspace(
        start_angle,
        stop_angle,
        num=n_segments+1,
        retstep=True,
    )

    directions = numpy.column_stack((numpy.cos(angles), numpy.sin(angles)))

    inner_coords = inner_radius*directions + [x, y]
    outer_coords = outer_radius*directions + [x, y]

    rel_handle_length: numpy.floating = 4 / 3 * numpy.tan(0.25 * angle_step)
    inner_handle_length = inner_radius * rel_handle_length
    outer_handle_length = outer_radius * rel_handle_length

    handle_directions_1 = numpy.column_stack(
        (-directions[:, 1], directions[:, 0]),  # toward `angles` + pi/2
    )
    handle_directions_2 = numpy.column_stack(
        (directions[:, 1], -directions[:, 0]),  # toward `angles` - pi/2
    )

    inner_ctrl_points_1 = (
        inner_coords + inner_handle_length*handle_directions_1
    )
    inner_ctrl_points_2 = (
        inner_coords + inner_handle_length*handle_directions_2
    )
    outer_ctrl_points_1 = (
        outer_coords + outer_handle_length*handle_directions_1
    )
    outer_ctrl_points_2 = (
        outer_coords + outer_handle_length*handle_directions_2
    )

    commands = []
    commands.append("M{},{}".format(*outer_coords[0]))
    commands.extend(
        "C{},{} {},{} {},{}".format(  # type: ignore[misc]
            *start_ctrl_point,
            *end_ctrl_point,
            *end_point,
        )
        for start_ctrl_point, end_ctrl_point, end_point in zip(
            outer_ctrl_points_1[:-1],
            outer_ctrl_points_2[1:],
            outer_coords[1:],
        )
    )
    if connect_arcs:
        commands.append("L{},{}".format(*inner_coords[-1]))
    else:
        commands.append("M{},{}".format(*inner_coords[-1]))
    commands.extend(
        "C{},{} {},{} {},{}".format(  # type: ignore[misc]
            *start_ctrl_point,
            *end_ctrl_point,
            *end_point,
        )
        for start_ctrl_point, end_ctrl_point, end_point in zip(
            inner_ctrl_points_2[-1:0:-1],
            inner_ctrl_points_1[-2::-1],
            inner_coords[-2::-1],
        )
    )
    if connect_arcs:
        commands.append("Z")

    path = " ".join(commands)

    return plotly.graph_objects.layout.Shape(type="path", path=path)


def add_annotations(
    fig: plotly.graph_objects.Figure,
    annotations: Iterable[plotly.graph_objects.layout.Annotation],
    row: int | None = None,
    col: int | None = None,
) -> plotly.graph_objects.Figure:
    """Add multiple annotations fast.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure object to which shapes are added.
    annotations : iterable of plotly.graph_objects.layout.Annotation
        Annotation objects to be added.
    row : int, optional
        Row where annotations are added.
    col : int, optional
        Column where annotations are added.

    Returns
    -------
    plotly.graph_objects.Figure
        Same figure object as the ``fig`` argument.
    """
    for _, group in itertools.groupby(
        annotations,
        key=lambda annotation: (annotation.xref, annotation.yref),
    ):
        # add the first annotation to get appropriate `xref` and `yref`
        fig.add_annotation(next(group), row=row, col=col)
        xref = fig.layout.annotations[-1].xref
        yref = fig.layout.annotations[-1].yref

        # add remaining annotations
        fig.layout.annotations += tuple(
            annotation.update(xref=xref, yref=yref) for annotation in group  # noqa: B031,E501
        )

    return fig


def add_shapes(
    fig: plotly.graph_objects.Figure,
    shapes: Iterable[plotly.graph_objects.layout.Shape],
    row: int | None = None,
    col: int | None = None,
) -> plotly.graph_objects.Figure:
    """Add multiple shapes fast.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure object to which shapes are added.
    shapes : iterable of plotly.graph_objects.layout.Shape
        Shape objects to be added.
    row : int, optional
        Row where shapes are added.
    col : int, optional
        Column where shapes are added.

    Returns
    -------
    plotly.graph_objects.Figure
        Same figure object as the ``fig`` argument.
    """
    for _, group in itertools.groupby(
        shapes,
        key=lambda shape: (shape.xref, shape.yref),
    ):
        # add the first shape to get appropriate `xref` and `yref`
        fig.add_shape(next(group), row=row, col=col)
        xref = fig.layout.shapes[-1].xref
        yref = fig.layout.shapes[-1].yref

        # add remaining shapes
        fig.layout.shapes += tuple(
            shape.update(xref=xref, yref=yref) for shape in group  # noqa: B031
        )

    return fig


def linearly_transform(
    x: ArrayLike,
    x1: ArrayLike,
    y1: ArrayLike,
    x2: ArrayLike,
    y2: ArrayLike,
) -> NDArray[numpy.double]:
    """Linearly transform a value.

    The transformation is performed element-wise after
    :term:`NumPy broadcasting <broadcast>`.

    Parameters
    ----------
    x : array-like of float
        Value to be transformed.
    x1 : array-like of float
        Reference value transformed into `y1`.
    y1 : array-like of float
        Reference value transformed from `x1`.
    x2 : array-like of float
        Reference value transformed into `y2`.
    y2 : array-like of float
        Reference value transformed from `x2`.

    Returns
    -------
    numpy.ndarray of float
        Value transformed from `x`.

    Examples
    --------
    >>> linearly_transform(0.5, 0, 0, 1, 2)
    array(1.)
    >>> linearly_transform([0.2, 0.5], 0, 0, 1, [[2], [4]])
    array([[0.4, 1. ],
           [0.8, 2. ]])
    """
    x = numpy.asarray(x)
    x1 = numpy.asarray(x1)
    y1 = numpy.asarray(y1)
    x2 = numpy.asarray(x2)
    y2 = numpy.asarray(y2)

    y = (y2-y1)/(x2-x1)*(x-x1) + y1
    y = numpy.asarray(y, dtype=float)

    return y
