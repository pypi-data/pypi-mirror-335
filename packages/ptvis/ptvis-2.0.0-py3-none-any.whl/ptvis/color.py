"""Handling colors."""

from __future__ import annotations

import abc
from collections.abc import Mapping
import functools
import itertools
import types
from typing import Any, Literal

import numpy
from numpy.typing import ArrayLike, NDArray
import pandas
import plotly
import wclr

from ._typing import assert_never, RealSeriesLike, SeriesLike
from .utils import linearly_transform


__all__ = [
    "BaseColorConversion",
    "BaseNumericalColorConversion",
    "CategoricalColorConversion",
    "ContinuousColorConversion",
    "DiscreteColorConversion",
    "IdentityColorConversion",
]


class BaseColorConversion(abc.ABC):
    """Base color conversion."""

    def color_guide(
        self,
        values: SeriesLike[Any, numpy.generic],
        attrs: Mapping[str, Any] | None = None,
    ) -> list[plotly.graph_objects.Scatter]:
        """Give a color guide.

        Parameters
        ----------
        values : series-like
            Values converted into colors.
        attrs : mapping, optional
            Attributes of a color guide.

        Returns
        -------
        list of plotly.graph_objects.Scatter
            Objects consisting a color guide.
        """
        return []

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abc.abstractmethod
    def apply(
        self,
        values: SeriesLike[Any, numpy.generic],
    ) -> pandas.Series[str]:
        """Apply the conversion to values.

        Parameters
        ----------
        values : series-like
            Values to be converted.

        Returns
        -------
        pandas.Series of str
            Color texts.
        """


class BaseNumericalColorConversion(BaseColorConversion):
    """Base color conversion from numerical values.

    Parameters
    ----------
    colors : array-like of str, optional
        Colors defining a color scale.
    levels : array-like of float, optional
        Levels defining a color scale. Must be in ascending order. If not
        given, evenly spaced levels are used.
    value_min : float, optional
        Value corresponding with the lowest level.
    value_max : float, optional
        Value corresponding with the highest level.
    lower_color : str, optional
        Color for values lower than the domain.
    higher_color : str, optional
        Color for values higher than the domain.
    na_color : str, optional
        Color for NaN.
    """

    def __init__(
        self,
        colors: ArrayLike | None = None,
        levels: ArrayLike | None = None,
        value_min: float | None = None,
        value_max: float | None = None,
        lower_color: str | None = None,
        higher_color: str | None = None,
        na_color: str = "#444444",
    ) -> None:
        if colors is None:
            colors = plotly.colors.sequential.Viridis
        colors = numpy.array(colors, dtype=str)
        if colors.ndim != 1:
            raise ValueError("`colors` must be 1-dimensional")
        if len(colors) < 2:
            raise ValueError("size of `colors` must be >= 2")
        for color in colors:
            _check_color_str(color)

        if levels is None:
            levels = numpy.linspace(0, 1, num=len(colors))
        levels = numpy.array(levels, dtype=float)
        if levels.ndim != 1:
            raise ValueError("`levels` must be 1-dimensional")
        if len(levels) != len(colors):
            raise ValueError(
                "size of `levels` must be equal to that of `colors`",
            )
        if not (levels[:-1] <= levels[1:]).all():
            raise ValueError("`levels` must be in ascending order")
        if levels[0] == levels[-1]:
            raise ValueError(
                "first and last items of `levels` must be different",
            )

        if value_min is not None:
            value_min = float(value_min)
        if value_max is not None:
            value_max = float(value_max)

        if lower_color is None:
            lower_color = colors[0]
        else:
            _check_color_str(lower_color)
        lower_color = str(lower_color)

        if higher_color is None:
            higher_color = colors[-1]
        else:
            _check_color_str(higher_color)
        higher_color = str(higher_color)

        _check_color_str(na_color)
        na_color = str(na_color)

        self._colors = colors
        self._colors.setflags(write=False)

        self._levels = levels
        self._levels.setflags(write=False)

        self._value_min = value_min
        self._value_max = value_max
        self._lower_color = lower_color
        self._higher_color = higher_color
        self._na_color = na_color

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            numpy.array_equal(self._colors, other._colors)
            and numpy.array_equal(self._levels, other._levels)
            and self._value_min == other._value_min
            and self._value_max == other._value_max
            and self._lower_color == other._lower_color
            and self._higher_color == other._higher_color
            and self._na_color == other._na_color
        )

    @property
    def colors(self) -> NDArray[numpy.str_]:
        """numpy.ndarray of str: Colors defining a color scale."""
        return self._colors.view()

    @property
    def levels(self) -> NDArray[numpy.floating[Any]]:
        """numpy.ndarray of float: Levels defining a color scale."""
        return self._levels.view()

    @property
    def value_min(self) -> float | None:
        """float or None: Value corresponding to the lowest level.
        """  # noqa: D200,D403
        return self._value_min

    @property
    def value_max(self) -> float | None:
        """float or None: Value corresponding to the highest level.
        """  # noqa: D200,D403
        return self._value_max

    @property
    def lower_color(self) -> str:
        """str: Color for values lower than the domain."""
        return self._lower_color

    @property
    def higher_color(self) -> str:
        """str: Color for values higher than the domain."""
        return self._higher_color

    @property
    def na_color(self) -> str:
        """str: Color for NaN."""
        return self._na_color

    def domain(self, values: RealSeriesLike) -> tuple[float, float]:
        """Give a domain of the conversion.

        Parameters
        ----------
        values : series-like of float
            Values to be converted.

        Returns
        -------
        value_min : float
            Minimum of the domain.
        value_max : float
            Maximum of the domain.
        """
        values = pandas.Series(values, dtype=float)

        value_min = self._value_min
        value_max = self._value_max

        if not pandas.isna(values).all():
            if value_min is None:
                value_min = values.min()
            if value_max is None:
                value_max = values.max()

        if value_min is None:
            if value_max is None:
                value_min = -0.5
                value_max = 0.5
            else:
                value_min = value_max - 1.
        else:
            if value_max is None:
                value_max = value_min + 1.
            elif value_min == value_max:
                value_min -= 0.5
                value_max += 0.5

        return value_min, value_max

    @abc.abstractmethod
    def color_guide(  # type: ignore[override]
        self,
        values: RealSeriesLike,
        attrs: Mapping[str, Any] | None = None,
    ) -> list[plotly.graph_objects.Scatter]:
        """Give a color guide.

        Parameters
        ----------
        values : series-like of float
            Values converted into colors.
        attrs : mapping, optional
            Attributes of a color guide.

        Returns
        -------
        list of plotly.graph_objects.Scatter
            Objects consisting a color guide.
        """

    @abc.abstractmethod
    def apply(  # type: ignore[override]
        self,
        values: RealSeriesLike,
    ) -> pandas.Series[str]:
        """Apply the conversion to values.

        Parameters
        ----------
        values : series-like of float
            Values to be converted.

        Returns
        -------
        pandas.Series of str
            Color texts.
        """


class ContinuousColorConversion(BaseNumericalColorConversion):
    """Color conversion from numerical values to continuous colors.

    Parameters
    ----------
    colors : array-like of str, optional
        Colors defining a color scale.
    levels : array-like of float, optional
        Levels defining a color scale. Must be in ascending order. If not
        given, evenly spaced levels are used.
    value_min : float, optional
        Value corresponding with the lowest level.
    value_max : float, optional
        Value corresponding with the highest level.
    lower_color : str, optional
        Color for values lower than the domain.
    higher_color : str, optional
        Color for values higher than the domain.
    na_color : str, optional
        Color for NaN.
    """

    def color_guide(  # type: ignore[override]  # noqa: D102
        self,
        values: RealSeriesLike,
        attrs: Mapping[str, Any] | None = None,
    ) -> list[plotly.graph_objects.Scatter]:
        levels = linearly_transform(
            self._levels,
            self._levels[0],
            0,
            self._levels[-1],
            1,
        )

        scatter = plotly.graph_objects.Scatter(
            x=[None],
            y=[None],
            marker={
                "colorscale": list(zip(levels, self._colors)),
                "colorbar": attrs,
                "showscale": True,
            },
            showlegend=False,
        )
        scatter.marker.cmin, scatter.marker.cmax = self.domain(values)

        return [scatter]

    def apply(  # type: ignore[override]  # noqa: D102
        self,
        values: RealSeriesLike,
    ) -> pandas.Series[str]:
        values = pandas.Series(values, dtype=float)

        level_min = self._levels[0]
        level_max = self._levels[-1]

        value_min, value_max = self.domain(values)
        levels: pandas.Series[float] = pandas.Series(
            linearly_transform(
                values,
                value_min,
                level_min,
                value_max,
                level_max,
            ),
            index=values.index,
        )

        is_lower = levels < level_min
        is_higher = level_max < levels

        colors = pandas.Series(self._na_color, index=values.index)
        colors.loc[is_lower] = self._lower_color
        colors.loc[is_higher] = self._higher_color

        # interpolate colors
        lvs = levels.loc[~is_lower & ~is_higher & ~levels.isna()]
        upper_indices = numpy.searchsorted(self._levels, lvs)
        upper_indices[upper_indices == 0] = 1
        lower_indices = upper_indices - 1
        rgbas = (
            linearly_transform(
                lvs,
                self._levels[lower_indices],
                self._rgbas[lower_indices].T,
                self._levels[upper_indices],
                self._rgbas[upper_indices].T,
            )
            .T
        )
        colors[lvs.index] = [
            wclr.Color(*rgba).to_rgb_function_str(percentage=False)
            for rgba in rgbas
        ]

        return colors

    @functools.cached_property
    def _rgbas(self) -> NDArray[numpy.floating[Any]]:
        """RGBA components of the `self._colors` attribute."""
        rgbas = numpy.array(
            [
                wclr.Color.from_str(color).to_srgb_tuple()
                for color in self._colors
            ],
            dtype=float,
        )
        rgbas.setflags(write=False)

        return rgbas.view()


class DiscreteColorConversion(BaseNumericalColorConversion):
    """Color conversion from numerical values to discrete colors.

    Parameters
    ----------
    colors : array-like of str, optional
        Colors defining a color scale.
    levels : array-like of float, optional
        Levels defining a color scale. Must be in ascending order. If not
        given, evenly spaced levels are used.
    value_min : float, optional
        Value corresponding with the lowest level.
    value_max : float, optional
        Value corresponding with the highest level.
    lower_color : str, optional
        Color for values lower than the domain.
    higher_color : str, optional
        Color for values higher than the domain.
    na_color : str, optional
        Color for NaN.
    n_intervals : int, optional
        Number of intervals or discrete colors.
    closed : {'low', 'high'}, optional
        Closed endpoint of an interval.
    include_boundary : bool, optional
        If ``True``, both boundaries are included in the domain.
    """

    def __init__(
        self,
        colors: ArrayLike | None = None,
        levels: ArrayLike | None = None,
        value_min: float | None = None,
        value_max: float | None = None,
        lower_color: str | None = None,
        higher_color: str | None = None,
        na_color: str = "#444444",
        n_intervals: int = 10,
        closed: Literal["low", "high"] = "low",
        include_boundary: bool = True,
    ) -> None:
        if not float(n_intervals).is_integer():
            raise ValueError("`n_intervals` must be an integer")
        if n_intervals < 2:
            raise ValueError("`n_intervals` must be >= 2")
        n_intervals = int(n_intervals)

        if closed not in {"low", "high"}:
            raise ValueError("`closed` must be 'low' or 'high'")

        include_boundary = bool(include_boundary)

        super().__init__(
            colors=colors,
            levels=levels,
            value_min=value_min,
            value_max=value_max,
            lower_color=lower_color,
            higher_color=higher_color,
            na_color=na_color,
        )
        self._n_intervals = n_intervals
        self._closed = closed
        self._include_boundary = include_boundary

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            super().__eq__(other)
            and self._n_intervals == other._n_intervals
            and self._closed == other._closed
            and self._include_boundary == other._include_boundary
        )

    @property
    def n_intervals(self) -> int:
        """int: Number of intervals."""
        return self._n_intervals

    @property
    def closed(self) -> Literal["low", "high"]:
        """{'low', 'high'}: Closed endpoint of an interval."""
        return self._closed

    @property
    def include_boundary(self) -> bool:
        """bool: Whether both boundaries are included in the domain."""
        return self._include_boundary

    def color_guide(  # type: ignore[override]  # noqa: D102
        self,
        values: RealSeriesLike,
        attrs: Mapping[str, Any] | None = None,
    ) -> list[plotly.graph_objects.Scatter]:
        edge_levels = numpy.linspace(0, 1, num=self._n_intervals+1)
        levels = [
            level
            for i in range(self._n_intervals)
            for level in edge_levels[i:i+2]
        ]

        colors = [
            color
            for color in self._interval_colors
            for _ in range(2)
        ]

        scatter = plotly.graph_objects.Scatter(
            x=[None],
            y=[None],
            marker={
                "colorscale": list(zip(levels, colors)),
                "colorbar": attrs,
                "showscale": True,
            },
            showlegend=False,
        )
        scatter.marker.cmin, scatter.marker.cmax = self.domain(values)

        return [scatter]

    def apply(  # type: ignore[override]  # noqa: D102
        self,
        values: RealSeriesLike,
    ) -> pandas.Series[str]:
        values = pandas.Series(values, dtype=float)

        value_min, value_max = self.domain(values)
        positions = linearly_transform(
            values,
            value_min,
            0,
            value_max,
            self._n_intervals,
        )

        if self._closed == "low":
            def get_color(position: float) -> str:
                if pandas.isna(position):
                    return self._na_color
                elif 0 <= position < self._n_intervals:
                    i_interval = int(numpy.floor(position))
                    return self._interval_colors[i_interval]
                elif position == self._n_intervals and self._include_boundary:
                    return self._interval_colors[-1]
                elif position < 0:
                    return self._lower_color
                else:
                    return self._higher_color
        elif self._closed == "high":
            def get_color(position: float) -> str:
                if pandas.isna(position):
                    return self._na_color
                elif 0 < position <= self._n_intervals:
                    i_interval = int(numpy.ceil(position)) - 1
                    return self._interval_colors[i_interval]
                elif position == 0 and self._include_boundary:
                    return self._interval_colors[0]
                elif self._n_intervals < position:
                    return self._higher_color
                else:
                    return self._lower_color
        else:
            assert_never(self._closed)

        colors = [get_color(position) for position in positions]
        colors = pandas.Series(colors, index=values.index, dtype=str)

        return colors

    @functools.cached_property
    def _interval_colors(self) -> tuple[str, ...]:
        """Colors assined to intervals."""
        rgbas = numpy.array(
            [
                wclr.Color.from_str(color).to_srgb_tuple()
                for color in self._colors
            ],
            dtype=float,
        )

        interval_levels = numpy.linspace(
            self._levels[0],
            self._levels[-1],
            num=self._n_intervals,
        )
        upper_indices = numpy.searchsorted(self._levels, interval_levels)
        upper_indices[upper_indices == 0] = 1
        lower_indices = upper_indices - 1
        interval_rgbas = (
            linearly_transform(
                interval_levels,
                self._levels[lower_indices],
                rgbas[lower_indices].T,
                self._levels[upper_indices],
                rgbas[upper_indices].T,
            )
            .T
        )

        return tuple(
            wclr.Color(*rgba).to_rgb_function_str(percentage=False)
            for rgba in interval_rgbas
        )


class CategoricalColorConversion(BaseColorConversion):
    """Color conversion from categories.

    Parameters
    ----------
    mapping : mapping, optional
        Mapping from categories to colors.
    missing_colors : array-like of str, optional
        Colors for missing categories.
    na_color : str, optional
        Color for N/A.
    """

    def __init__(
        self,
        mapping: Mapping[Any, str] | None = None,
        missing_colors: ArrayLike | None = None,
        na_color: str = "#444444",
    ) -> None:
        if mapping is None:
            mapping = {}
        for value in mapping.values():
            _check_color_str(value)
        mapping = {k: str(v) for k, v in mapping.items()}

        if missing_colors is None:
            missing_colors = plotly.colors.qualitative.Plotly
        missing_colors = numpy.array(missing_colors, dtype=str)
        if missing_colors.ndim != 1:
            raise ValueError("`missing_colors` must be 1-dimensional")
        for value in missing_colors:
            _check_color_str(value)

        _check_color_str(na_color)
        na_color = str(na_color)

        self._mapping = mapping

        self._missing_colors = missing_colors
        self._missing_colors.setflags(write=False)

        self._na_color = na_color

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self._mapping == other._mapping
            and numpy.array_equal(self._missing_colors, other._missing_colors)
            and self._na_color == other._na_color
        )

    @property
    def mapping(self) -> types.MappingProxyType[Any, str]:
        """types.MappingProxyType: Mapping from categories to colors."""
        return types.MappingProxyType(self._mapping)

    @property
    def missing_colors(self) -> NDArray[numpy.str_]:
        """numpy.ndarray of str: Colors for missing categories."""
        return self._missing_colors.view()

    @property
    def na_color(self) -> str:
        """str: Color for N/A."""
        return self._na_color

    def color_guide(  # noqa: D102
        self,
        values: SeriesLike[Any, numpy.generic],
        attrs: Mapping[str, Any] | None = None,
    ) -> list[plotly.graph_objects.Scatter]:
        if attrs is None:
            attrs = {}

        mapping = self._full_mapping(values)

        return [
            plotly.graph_objects.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker={**attrs, "color": color},
                name=str(value),
            )
            for value, color in mapping.items()
        ]

    def apply(  # noqa: D102
        self,
        values: SeriesLike[Any, numpy.generic],
    ) -> pandas.Series[str]:
        values = pandas.Series(values)

        mapping = self._full_mapping(values)
        colors = values.map(mapping, na_action="ignore")
        colors.fillna(self._na_color, inplace=True)

        return colors.astype(str)

    def _full_mapping(
        self,
        values: SeriesLike[Any, numpy.generic],
    ) -> dict[Any, str]:
        """Give a full mapping from categories in given values."""
        values = pandas.Series(values)

        it = itertools.cycle(self._missing_colors)
        mapping = {
            value: self._mapping[value] if value in self._mapping else next(it)
            for value in values.dropna().unique()
        }

        return mapping


class IdentityColorConversion(BaseColorConversion):
    """Color conversion mapping a value to itself."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return True

    def apply(  # type: ignore[override]
        self,
        values: SeriesLike[str, numpy.str_],
    ) -> pandas.Series[str]:
        """Map a color text to itself.

        Parameters
        ----------
        values : series-like of str
            Color texts.

        Returns
        -------
        pandas.Series of str
            Color texts.
        """
        values = pandas.Series(values)
        for value in values:
            _check_color_str(value)

        return values.astype(str)


def _check_color_str(s: str | numpy.str_) -> None:
    """Check if a text is a valid color."""
    wclr.Color.from_str(s)
