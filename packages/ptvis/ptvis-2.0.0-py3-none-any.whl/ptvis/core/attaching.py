"""Attaching cells of the periodic table."""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from typing import Any, cast, Literal

import numpy
import pandas.api.types
import plotly.basedatatypes
import wclr

from .element import Element
from .._typing import ObjectSeriesLike, RealSeriesLike, SeriesLike
from ..color import (
    BaseColorConversion,
    CategoricalColorConversion,
    ContinuousColorConversion,
    IdentityColorConversion,
)
from ..components import make_circular_sector_cells, make_plain_cells
from ..layouts import BaseTableLayout, SeparatedTableLayout
from ..utils import add_annotations, add_shapes, linearly_transform


__all__ = ["attach_pie_cells", "attach_plain_cells", "attach_polar_bar_cells"]


def attach_plain_cells(
    fig: plotly.graph_objects.Figure,
    elements: ObjectSeriesLike[Element],
    shape: Literal["circle", "square"] = "square",
    areas: RealSeriesLike | None = None,
    area_max: float | None = None,
    texts: SeriesLike[str, numpy.str_] | None = None,
    text_colorway: Collection[str] | None = None,
    colors: SeriesLike[str, numpy.str_] | None = None,
    color_conversion: BaseColorConversion | None = None,
    color_guide: Mapping[str, Any] | None = None,
    tooltip: Mapping[str, bool | SeriesLike[Any, numpy.generic]] | None = None,
    labels: Mapping[str, str] | None = None,
    formats: Mapping[str, str] | None = None,
    table_layout: BaseTableLayout | None = None,
    row: int | None = None,
    col: int | None = None,
) -> None:
    """Attach the periodic table with plain cells.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure object to which the periodic table is attached.
    elements : series-like of ptvis.Element
        Chemical elements whose cells are drawn.
    shape : {'square', 'circle'}, optional
        Shape of a cell.
    areas : series-like of float, optional
        Values determining areas of cells. Must be nonnegative.
    area_max : float, optional
        Value of the `areas` argument corresponding to the largest possible
        cell area. If not given, the maximum of the argument is used.
    texts : series-like of str, optional
        Texts of cells.
    text_colorway : collection of str, optional
        Candidates for text colors. A color of the highest contrast ratio to a
        cell color is selected.
    colors : series-like, optional
        Values determining colors of cells.
    color_conversion : ptvis.color.BaseColorConversion, optional
        Conversion from the `colors` argument to colors. If not given, use a
        :class:`ptvis.color.ContinuousColorConversion` object for a numerical
        `colors` argument and a :class:`ptvis.color.CategoricalColorConversion`
        object for a non-numerical `colors` argument.
    color_guide : mapping, optional
        Attributes of a color guide. If not given, a color guide is not added.
    tooltip : mapping, optional
        Tooltip contents. The key is a label of data and the value is ``bool``
        or series-like. The value of ``bool`` controls whether an item is
        shown. The series-like value is extra data.
    labels : mapping, optional
        Labels of data. The key is a default label.
    formats : mapping, optional
        Formats of data. The key is a default label of data.
    table_layout : ptvis.layouts.BaseTableLayout, optional
        Layout of the periodic table.
    row : int, optional
        Row where the periodic table is attached.
    col : int, optional
        Column where the periodic table is attached.
    """
    main_data: dict[str, SeriesLike[Any, numpy.generic]] = {
        "element": elements,
    }
    main_labels = {"element_symbol": "element"}

    if areas is None:
        main_data["area"] = area_max = 1.
    else:
        main_data["area"] = areas
        main_labels["area"] = "area"

    if texts is not None:
        main_data["text"] = texts

    if colors is None:
        main_data["color_value"] = _default_color_str(fig.layout.template)
        color_conversion = IdentityColorConversion()
    else:
        main_data["color_value"] = colors
        if not isinstance(color_conversion, IdentityColorConversion):
            main_labels["color_value"] = "color"

    df, tooltip_labels, tooltip_formats = _arrange_data(
        main_data,
        main_labels,
        {},
        tooltip=tooltip,
        labels=labels,
        formats=formats,
    )

    if not df[("main", "element")].is_unique:
        raise ValueError("elements must be unique")

    if (df[("main", "area")] < 0).any():
        raise ValueError("areas must be nonnegative")

    if ("main", "element_symbol") in tooltip_labels:
        df[("main", "element_symbol")] = df[("main", "element")].map(
            lambda element: element.symbol,
        )

    if color_conversion is None:
        color_conversion = _default_color_conversion(
            df[("main", "color_value")],
            fig.layout.template,
        )
    df[("main", "color_str")] = color_conversion.apply(
        df[("main", "color_value")],
    )

    if table_layout is None:
        table_layout = SeparatedTableLayout()

    bg_color = _background_color(fig.layout)

    text_color_strs = []
    color_str: str
    for color_str in df[("main", "color_str")]:
        color = wclr.Color.from_str(color_str)
        color = wclr.alpha_composite(color, bg_color)
        text_color_strs.append(_select_text_color_str(color, text_colorway))
    df[("main", "text_color_str")] = text_color_strs

    if area_max is None:
        area_max = df[("main", "area")].max()

    xs, ys = zip(
        *(
            table_layout.cell_coordinates(element)
            for element in df[("main", "element")]
        )
    )
    widths = heights = numpy.sqrt(df[("main", "area")] / area_max)
    cell_shapes, cell_text_trace = make_plain_cells(
        xs,
        ys,
        widths,
        heights,
        texts=df.get(("main", "text")),
        colors=df[("main", "color_str")],
        shape=shape,
    )

    kws = {
        "line": {
            "color": bg_color.to_rgb_function_str(percentage=False),
            "width": 1,
        },
        "layer": "below",
    }
    for shape in cell_shapes:
        shape.update(**kws)

    cell_text_trace.update(
        textfont_color=df[("main", "text_color_str")],
        customdata=df[list(tooltip_labels)].to_numpy(),
        hovertemplate=(
            "<br>".join(
                [
                    f"{label}=%{{customdata[{i}]{tooltip_formats[key]}}}"
                    for i, (key, label) in enumerate(tooltip_labels.items())
                ]
            )
            +"<extra></extra>"  # noqa: E225
        ),
        hoverlabel_bgcolor=df[("main", "color_str")],
    )

    _attach_cells(
        fig,
        [cell_text_trace],
        cell_shapes,
        df[("main", "color_value")],
        color_conversion,
        color_guide,
        table_layout,
        row,
        col,
    )


def attach_pie_cells(
    fig: plotly.graph_objects.Figure,
    elements: ObjectSeriesLike[Element],
    angles: RealSeriesLike | None = None,
    diameter: float = 1.,
    hole_diameter: float = 0.,
    hole_texts: Mapping[Element, str] | None = None,
    texts: SeriesLike[str, numpy.str_] | None = None,
    text_colorway: Collection[str] | None = None,
    colors: SeriesLike[str, numpy.str_] | None = None,
    color_conversion: BaseColorConversion | None = None,
    color_guide: Mapping[str, Any] | None = None,
    tooltip: Mapping[str, bool | SeriesLike[Any, numpy.generic]] | None = None,
    labels: Mapping[str, str] | None = None,
    formats: Mapping[str, str] | None = None,
    table_layout: BaseTableLayout | None = None,
    row: int | None = None,
    col: int | None = None,
) -> None:
    """Attach the periodic table with pie chart cells.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure object to which the periodic table is attached.
    elements : series-like of ptvis.Element
        Chemical elements where circular sectors are drawn.
    angles : series-like of float, optional
        Values determining central angles of circular sectors. Must be
        nonnegative. If not given, sectors of the same element have equal
        central angles.
    diameter : float, optional
        Diameter of a cell relative to the largest possible cell diameter.
    hole_diameter : float, optional
        Diameter of a hole of a cell relative to the largest possible cell
        diameter.
    hole_texts : mapping, optional
        Texts written in cell holes.
    texts : series-like of str, optional
        Texts of circular sectors.
    text_colorway : collection of str, optional
        Candidates for text colors. A color of the highest contrast ratio to a
        sector color is selected.
    colors : series-like, optional
        Values determining colors of circular sectors.
    color_conversion : ptvis.color.BaseColorConversion, optional
        Conversion from the `colors` argument to colors. If not given, use a
        :class:`ptvis.color.ContinuousColorConversion` object for a numerical
        `colors` argument and a :class:`ptvis.color.CategoricalColorConversion`
        object for a non-numerical `colors` argument.
    color_guide : mapping, optional
        Attributes of a color guide. If not given, a color guide is not added.
    tooltip : mapping, optional
        Tooltip contents. The key is a label of data and the value is ``bool``
        or series-like. The value of ``bool`` controls whether an item is
        shown. The series-like value is extra data.
    labels : mapping, optional
        Labels of data. The key is a default label.
    formats : mapping, optional
        Formats of data. The key is a default label of data.
    table_layout : ptvis.layouts.BaseTableLayout, optional
        Layout of the periodic table.
    row : int, optional
        Row where the periodic table is attached.
    col : int, optional
        Column where the periodic table is attached.
    """
    main_data: dict[str, SeriesLike[Any, numpy.generic]] = {
        "element": elements,
    }
    main_labels = {"element_symbol": "element"}
    main_formats = {}

    if angles is None:
        main_data["angle"] = 1.
    else:
        main_data["angle"] = angles
        main_labels["angle"] = "angle"
        main_labels["proportion"] = "proportion"
        main_formats["proportion"] = ":%"

    if texts is not None:
        main_data["text"] = texts

    if colors is None:
        main_data["color_value"] = _default_color_str(fig.layout.template)
        color_conversion = IdentityColorConversion()
    else:
        main_data["color_value"] = colors
        if not isinstance(color_conversion, IdentityColorConversion):
            main_labels["color_value"] = "color"

    df, tooltip_labels, tooltip_formats = _arrange_data(
        main_data,
        main_labels,
        main_formats,
        tooltip=tooltip,
        labels=labels,
        formats=formats,
    )

    if (df[("main", "angle")] < 0).any():
        raise ValueError("angles must be nonnegative")

    df[("main", "proportion")] = (
        df[("main", "angle")]
        .groupby(df[("main", "element")], group_keys=False)
        .transform(
            lambda subangles:
            subangles/subangles.sum() if subangles.any()
            else 0 if not subangles.isna().all()
            else numpy.nan,
        )
    )

    if ("main", "element_symbol") in tooltip_labels:
        df[("main", "element_symbol")] = df[("main", "element")].map(
            lambda element: element.symbol,
        )

    if color_conversion is None:
        color_conversion = _default_color_conversion(
            df[("main", "color_value")],
            fig.layout.template,
        )
    df[("main", "color_str")] = color_conversion.apply(
        df[("main", "color_value")],
    )

    if table_layout is None:
        table_layout = SeparatedTableLayout()

    bg_color = _background_color(fig.layout)

    text_color_strs = []
    for color_str in df[("main", "color_str")]:
        color = wclr.Color.from_str(color_str)
        color = wclr.alpha_composite(color, bg_color)
        text_color_strs.append(_select_text_color_str(color, text_colorway))
    df[("main", "text_color_str")] = text_color_strs

    xs, ys = zip(
        *(
            table_layout.cell_coordinates(element)
            for element in df[("main", "element")]
        )
    )
    stop_angles = (
        360
        *(  # noqa: E225
            df[("main", "proportion")]
            .fillna(0)
            .groupby(df[("main", "element")], sort=False)
            .cumsum()
        )
        - 90
    )
    start_angles = (
        stop_angles - 360*df[("main", "proportion")].fillna(0)
    )
    sector_shapes, sector_text_trace = make_circular_sector_cells(
        xs,
        ys,
        start_angles,
        stop_angles,
        [0.5*diameter]*len(df),
        hole_radius=0.5*hole_diameter,
        texts=df.get(("main", "text")),
        colors=df[("main", "color_str")],
    )

    kws = {
        "line": {
            "color": bg_color.to_rgb_function_str(percentage=False),
            "width": 1,
        },
        "layer": "below",
    }
    for shape in sector_shapes:
        shape.update(**kws)

    sector_text_trace.update(
        textfont_color=df[("main", "text_color_str")],
        customdata=df[list(tooltip_labels)].to_numpy(),
        hovertemplate=(
            "<br>".join(
                [
                    f"{label}=%{{customdata[{i}]{tooltip_formats[key]}}}"
                    for i, (key, label) in enumerate(tooltip_labels.items())
                ]
            )
            +"<extra></extra>"  # noqa: E225
        ),
        hoverlabel_bgcolor=df[("main", "color_str")],
    )

    hole_text_trace = plotly.graph_objects.Scatter(
        mode="text",
        showlegend=False,
        hoverinfo="skip",
    )
    if hole_texts is not None:
        x, y = zip(
            *(
                table_layout.cell_coordinates(element)
                for element in hole_texts
            ),
        )
        hole_text_trace.update(x=x, y=y, text=list(hole_texts.values()))

    _attach_cells(
        fig,
        [hole_text_trace, sector_text_trace],
        sector_shapes,
        df[("main", "color_value")],
        color_conversion,
        color_guide,
        table_layout,
        row,
        col,
    )


def attach_polar_bar_cells(
    fig: plotly.graph_objects.Figure,
    elements: ObjectSeriesLike[Element],
    radii: RealSeriesLike,
    radius_min: float | None = None,
    radius_max: float | None = None,
    hole_diameter: float = 0.,
    hole_texts: Mapping[Element, str] | None = None,
    texts: SeriesLike[str, numpy.str_] | None = None,
    text_colorway: Collection[str] | None = None,
    colors: SeriesLike[str, numpy.str_] | None = None,
    color_conversion: BaseColorConversion | None = None,
    color_guide: Mapping[str, Any] | None = None,
    tooltip: Mapping[str, bool | SeriesLike[Any, numpy.generic]] | None = None,
    labels: Mapping[str, str] | None = None,
    formats: Mapping[str, str] | None = None,
    table_layout: BaseTableLayout | None = None,
    row: int | None = None,
    col: int | None = None,
) -> None:
    """Attach the periodic table with polar bar chart cells.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure object to which the periodic table is attached.
    elements : series-like of ptvis.Element
        Chemical elements where sectors are drawn.
    radii : series-like of float
        Values determining radii of sectors.
    radius_min : float, optional
        Value of the `radii` argument corresponding to the hole radius. If not
        given, the smaller of zero and the minimum of the argument is used.
    radius_max : float, optional
        Value of the `radii` argument corresponding to the largest possible
        cell radius. If not given, the larger of zero and the maximum of the
        argument is used.
    hole_diameter : float, optional
        Diameter of a hole of a cell relative to the largest possible cell
        diameter.
    hole_texts : mapping, optional
        Texts written in cell holes.
    texts : series-like of str, optional
        Texts of sectors.
    text_colorway : collection of str, optional
        Candidates for text colors. A color of the highest contrast ratio to a
        sector color is selected.
    colors : series-like, optional
        Values determining colors of sectors.
    color_conversion : ptvis.color.BaseColorConversion, optional
        Conversion from the `colors` argument to colors. If not given, use a
        :class:`ptvis.color.ContinuousColorConversion` object for a numerical
        `colors` argument and a :class:`ptvis.color.CategoricalColorConversion`
        object for a non-numerical `colors` argument.
    color_guide : mapping, optional
        Attributes of a color guide. If not given, a color guide is not added.
    tooltip : mapping, optional
        Tooltip contents. The key is a label of data and the value is ``bool``
        or series-like. The value of ``bool`` controls whether an item is
        shown. The series-like value is extra data.
    labels : mapping, optional
        Labels of data. The key is a default label.
    formats : mapping, optional
        Formats of data. The key is a default label of data.
    table_layout : ptvis.layouts.BaseTableLayout, optional
        Layout of the periodic table.
    row : int, optional
        Row where the periodic table is attached.
    col : int, optional
        Column where the periodic table is attached.
    """
    main_data: dict[str, SeriesLike[Any, numpy.generic]] = {
        "element": elements,
        "radius": radii,
    }
    main_labels = {"element_symbol": "element", "radius": "radius"}

    if texts is not None:
        main_data["text"] = texts

    if colors is None:
        main_data["color_value"] = _default_color_str(fig.layout.template)
        color_conversion = IdentityColorConversion()
    else:
        main_data["color_value"] = colors
        if not isinstance(color_conversion, IdentityColorConversion):
            main_labels["color_value"] = "color"

    df, tooltip_labels, tooltip_formats = _arrange_data(
        main_data,
        main_labels,
        {},
        tooltip=tooltip,
        labels=labels,
        formats=formats,
    )

    if ("main", "element_symbol") in tooltip_labels:
        df[("main", "element_symbol")] = df[("main", "element")].map(
            lambda element: element.symbol,
        )

    if radius_min is None:
        radius_min = min(0., df[("main", "radius")].min())
    if radius_max is None:
        radius_max = max(0., df[("main", "radius")].max())

    if color_conversion is None:
        color_conversion = _default_color_conversion(
            df[("main", "color_value")],
            fig.layout.template,
        )
    df[("main", "color_str")] = color_conversion.apply(
        df[("main", "color_value")],
    )

    if table_layout is None:
        table_layout = SeparatedTableLayout()

    bg_color = _background_color(fig.layout)

    text_color_strs = []
    for color_str in df[("main", "color_str")]:
        color = wclr.Color.from_str(color_str)
        color = wclr.alpha_composite(color, bg_color)
        text_color_strs.append(_select_text_color_str(color, text_colorway))
    df[("main", "text_color_str")] = text_color_strs

    def get_angles(index: pandas.Index[Any]) -> pandas.DataFrame:
        edges = numpy.linspace(-90, 270, num=len(index)+1)
        start_angles = edges[:-1]
        stop_angles = edges[1:]
        return pandas.DataFrame(
            {"start": start_angles, "stop": stop_angles},
            index=index,
        )

    xs, ys = zip(
        *(
            table_layout.cell_coordinates(element)
            for element in df[("main", "element")]
        )
    )
    angles = (
        df
        .groupby(("main", "element"), sort=False, group_keys=False)
        .apply(lambda subdf: get_angles(subdf.index))
    )
    radii = linearly_transform(
        df[("main", "radius")],
        radius_min,
        0.5*hole_diameter,
        radius_max,
        0.5,
    )
    hole_radius = min(
        max(
            0.5*hole_diameter,
            cast(
                float,
                linearly_transform(
                    0,
                    radius_min,
                    0.5*hole_diameter,
                    radius_max,
                    0.5,
                ),
            ),
        ),
        0.5,
    )
    sector_shapes, sector_text_trace = make_circular_sector_cells(
        xs,
        ys,
        angles["start"],
        angles["stop"],
        radii,
        hole_radius=hole_radius,
        texts=df.get(("main", "text")),
        colors=df[("main", "color_str")],
    )

    kws = {
        "line": {
            "color": bg_color.to_rgb_function_str(percentage=False),
            "width": 1,
        },
        "layer": "below",
    }
    for shape in sector_shapes:
        shape.update(**kws)

    sector_text_trace.update(
        textfont_color=df[("main", "text_color_str")],
        customdata=df[list(tooltip_labels)].to_numpy(),
        hovertemplate=(
            "<br>".join(
                [
                    f"{label}=%{{customdata[{i}]{tooltip_formats[key]}}}"
                    for i, (key, label) in enumerate(tooltip_labels.items())
                ]
            )
            +"<extra></extra>"  # noqa: E225
        ),
        hoverlabel_bgcolor=df[("main", "color_str")],
    )

    hole_text_trace = plotly.graph_objects.Scatter(
        mode="text",
        showlegend=False,
        hoverinfo="skip",
    )
    if hole_texts is not None:
        x, y = zip(
            *(
                table_layout.cell_coordinates(element)
                for element in hole_texts
            ),
        )
        hole_text_trace.update(x=x, y=y, text=list(hole_texts.values()))

    _attach_cells(
        fig,
        [hole_text_trace, sector_text_trace],
        sector_shapes,
        df[("main", "color_value")],
        color_conversion,
        color_guide,
        table_layout,
        row,
        col,
    )


def _arrange_data(
    main_data: Mapping[str, SeriesLike[Any, numpy.generic]],
    main_labels: Mapping[str, str],
    main_formats: Mapping[str, str],
    tooltip: Mapping[str, bool | SeriesLike[Any, numpy.generic]] | None = None,
    labels: Mapping[str, str] | None = None,
    formats: Mapping[str, str] | None = None,
) -> tuple[
    pandas.DataFrame,
    dict[tuple[str, str], str],
    dict[tuple[str, str], str],
]:
    """Arrange data in arrays, labels, and formats."""
    if len(set(main_labels.values())) != len(main_labels):
        raise ValueError("values of `main_labels` must be unique")

    if tooltip is None:
        tooltip = {}
    if labels is None:
        labels = {}

    all_data = {("main", key): value for key, value in main_data.items()}
    tooltip_labels = {
        ("main", key): value for key, value in main_labels.items()
    }
    for label, value in tooltip.items():
        if isinstance(value, bool):
            if label not in main_labels.values():
                continue
            key = next(k for k, v in main_labels.items() if v == label)
            key = ("main", key)
            if value:
                tooltip_labels.pop(key)
                tooltip_labels[key] = label
            else:
                tooltip_labels.pop(key)
        else:
            key = ("extra", label)
            all_data[key] = value
            tooltip_labels[key] = label

    if all(pandas.api.types.is_scalar(value) for value in all_data.values()):
        all_data = {key: [value] for key, value in all_data.items()}
    all_data = pandas.DataFrame(all_data)

    tooltip_labels = {
        key: labels.get(label, label) for key, label in tooltip_labels.items()
    }

    tooltip_formats = dict(main_formats)
    if formats is not None:
        tooltip_formats.update(formats)
    tooltip_formats = {
        key: tooltip_formats.get(label, "")
        for key, label in tooltip_labels.items()
    }

    return all_data, tooltip_labels, tooltip_formats


def _attach_cells(
    fig: plotly.graph_objects.Figure,
    cell_traces: Sequence[plotly.basedatatypes.BaseTraceType],
    cell_shapes: Sequence[plotly.graph_objects.layout.Shape],
    color_values: SeriesLike[str, numpy.str_],
    color_conversion: BaseColorConversion,
    color_guide: Mapping[str, Any] | None,
    table_layout: BaseTableLayout | None,
    row: int | None,
    col: int | None,
) -> None:
    """Attach cells of the periodic table."""
    if table_layout is None:
        table_layout = SeparatedTableLayout()

    traces = []
    if color_guide is not None:
        traces.extend(
            color_conversion.color_guide(color_values, attrs=color_guide),
        )
    traces.extend(cell_traces)

    annotations = table_layout.annotations()

    fig.add_traces(traces, rows=row, cols=col)
    add_annotations(fig, annotations, row=row, col=col)
    add_shapes(fig, cell_shapes, row=row, col=col)

    fig.update_xaxes(table_layout.x_axis(), row=row, col=col)
    fig.update_yaxes(table_layout.y_axis(), row=row, col=col)


def _default_color_str(template: plotly.graph_objects.layout.Template) -> str:
    """Give the default color."""
    colorway: Sequence[str] = (
        template.layout.colorway or plotly.colors.qualitative.D3
    )

    return colorway[0]


def _default_color_conversion(
    values: pandas.Series[Any],
    template: plotly.graph_objects.layout.Template,
) -> BaseColorConversion:
    """Give the default color conversion."""
    if issubclass(values.dtype.type, (numpy.integer, numpy.floating)):
        color_scale = template.layout.colorscale.sequential
        if color_scale:
            levels, colors = zip(*color_scale)
        else:
            colors = plotly.colors.sequential.Viridis
            levels = None
        return ContinuousColorConversion(colors=colors, levels=levels)
    else:
        missing_colors = (
            template.layout.colorway or plotly.colors.qualitative.D3
        )
        return CategoricalColorConversion(missing_colors=missing_colors)


def _background_color(layout: plotly.graph_objects.Layout) -> wclr.Color:
    """Give a background color of a plot area."""
    bg_color = wclr.Color(1, 1, 1)

    paper_bg_color_str = (
        layout.paper_bgcolor
        or layout.template.layout.paper_bgcolor
        or "#ffffff"
    )
    paper_bg_color = wclr.Color.from_str(paper_bg_color_str)
    bg_color = wclr.alpha_composite(paper_bg_color, bg_color)

    plot_bg_color_str = (
        layout.plot_bgcolor
        or layout.template.layout.plot_bgcolor
        or "#ffffff"
    )
    plot_bg_color = wclr.Color.from_str(plot_bg_color_str)
    bg_color = wclr.alpha_composite(plot_bg_color, bg_color)

    return bg_color


def _select_text_color_str(
    color: wclr.Color,
    text_colorway: Collection[str] | None,
) -> str:
    """Select a text color."""
    if not text_colorway:
        text_colorway = ["#444444", "#ffffff"]

    max_contrast_ratio = -float("inf")
    best_text_color_str: str
    for text_color_str in text_colorway:
        text_color = wclr.Color.from_str(text_color_str)
        contrast_ratio = wclr.contrast_ratio(text_color, color)
        if max_contrast_ratio < contrast_ratio:
            max_contrast_ratio = contrast_ratio
            best_text_color_str = text_color_str

    return best_text_color_str
