"""Layouts of the periodic table."""

from __future__ import annotations

import abc

import plotly

from .core.element import Element


__all__ = ["BaseTableLayout", "SeparatedTableLayout", "UnifiedTableLayout"]


class BaseTableLayout(abc.ABC):
    """Base class for the layout of the periodic table."""

    def x_axis(self) -> plotly.graph_objects.layout.XAxis:
        """Give an x-axis object.

        Returns
        -------
        plotly.graph_objects.layout.XAxis
            X-axis object.
        """
        return plotly.graph_objects.layout.XAxis()

    def y_axis(self) -> plotly.graph_objects.layout.YAxis:
        """Give a y-axis object.

        Returns
        -------
        plotly.graph_objects.layout.YAxis
            Y-axis object.
        """
        return plotly.graph_objects.layout.YAxis()

    def annotations(self) -> list[plotly.graph_objects.layout.Annotation]:
        """Give annotation objects.

        Returns
        -------
        list of plotly.graph_objects.layout.Annotation
            Annotation objects.
        """
        return []

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abc.abstractmethod
    def cell_coordinates(self, element: Element) -> tuple[float, float]:
        """Give coordinates of a cell.

        Parameters
        ----------
        element : ptvis.Element
            Chemical element of a cell.

        Returns
        -------
        x : float
            X coordinate of a cell.
        y : float
            Y coordinate of a cell.
        """


class SeparatedTableLayout(BaseTableLayout):
    """Layout of the periodic table where the f-block is separated.

    Parameters
    ----------
    lanthanoids_symbol : str, optional
        Symbol for marking the lanthanoids.
    actinoids_symbol : str, optional
        Symbol for marking the actinoids
    symbol_width : float, optional
        Width of a symbol relative to the maximum possible cell width.
    separation : float, optional
        Vertical separation above the f-block relative to the maximum possible
        cell height.
    padding : float, optional
        Padding of the periodic table relative to the maximum possible cell
        size.
    """

    def __init__(
        self,
        lanthanoids_symbol: str = "\N{DAGGER}",
        actinoids_symbol: str = "\N{DOUBLE DAGGER}",
        symbol_width: float = 0.5,
        separation: float = 0.5,
        padding: float = 0.05,
    ) -> None:
        self._lanthanoids_symbol = str(lanthanoids_symbol)
        self._actinoids_symbol = str(actinoids_symbol)
        self._symbol_width = float(symbol_width)
        self._separation = float(separation)
        self._padding = float(padding)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self._lanthanoids_symbol == other._lanthanoids_symbol
            and self._actinoids_symbol == other._actinoids_symbol
            and self._symbol_width == other._symbol_width
            and self._separation == other._separation
            and self._padding == other._padding
        )

    @property
    def lanthanoids_symbol(self) -> str:
        """str: Symbol for marking the lanthanoids."""
        return self._lanthanoids_symbol

    @property
    def actinoids_symbol(self) -> str:
        """str: Symbol for marking the actinoids."""
        return self._actinoids_symbol

    @property
    def symbol_width(self) -> float:
        """float: Width of a symbol."""
        return self._symbol_width

    @property
    def separation(self) -> float:
        """float: Vertical separation above the f-block."""
        return self._separation

    @property
    def padding(self) -> float:
        """float: Padding of the periodic table."""
        return self._padding

    def x_axis(self) -> plotly.graph_objects.layout.XAxis:  # noqa: D102
        return plotly.graph_objects.layout.XAxis(
            side="top",
            tickvals=[
                group if group <= 2 else group+self._symbol_width
                for group in range(1, 19)
            ],
            ticktext=[str(group) for group in range(1, 19)],
            range=[0.5-self._padding, 18.5+self._symbol_width+self._padding],
            showgrid=False,
            zeroline=False,
        )

    def y_axis(self) -> plotly.graph_objects.layout.YAxis:  # noqa: D102
        return plotly.graph_objects.layout.YAxis(
            tickvals=list(range(1, 8)),
            ticktext=[str(period) for period in range(1, 8)],
            range=[9.5+self._separation+self._padding, 0.5-self._padding],
            showgrid=False,
            zeroline=False,
        )

    def annotations(  # noqa: D102
        self
    ) -> list[plotly.graph_objects.layout.Annotation]:
        x = 2.5 + 0.5*self._symbol_width
        ys = [6, 7, 8+self._separation, 9+self._separation]
        texts = [
            self._lanthanoids_symbol,
            self._actinoids_symbol,
            self._lanthanoids_symbol,
            self._actinoids_symbol,
        ]

        return [
            plotly.graph_objects.layout.Annotation(
                x=x,
                xref="x",
                y=y,
                yref="y",
                text=text,
                showarrow=False,
            )
            for y, text in zip(ys, texts)
        ]

    def cell_coordinates(  # noqa: D102
        self,
        element: Element,
    ) -> tuple[float, float]:
        if element == Element.HYDROGEN:
            x, y = 1., 1.
        elif element == Element.HELIUM:
            x, y = 18.+self._symbol_width, 1.
        elif Element.LITHIUM <= element <= Element.ARGON:
            q, r = divmod(element.value - Element.LITHIUM.value, 8)
            x = r+1. if r < 2 else r+11.+self._symbol_width
            y = q + 2.
        elif Element.POTASSIUM <= element <= Element.XENON:
            q, r = divmod(element.value - Element.POTASSIUM.value, 18)
            x = r+1. if r < 2 else r+1.+self._symbol_width
            y = q + 4.
        else:
            q, r = divmod(element.value - Element.CAESIUM.value, 32)
            if r < 2:
                x = r + 1.
                y = q + 6.
            elif r < 16:
                x = r + 1. + self._symbol_width
                y = q + 8. + self._separation
            else:
                x = r - 13. + self._symbol_width
                y = q + 6.

        return x, y


class UnifiedTableLayout(BaseTableLayout):
    """Layout of the periodic table where the f-block is not separated.

    Parameters
    ----------
    padding : float, optional
        Padding of the periodic table relative to the maximum possible cell
        size.
    """

    def __init__(self, padding: float = 0.05) -> None:
        self._padding = float(padding)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._padding == other._padding

    @property
    def padding(self) -> float:
        """float: Padding of the periodic table."""
        return self._padding

    def x_axis(self) -> plotly.graph_objects.layout.XAxis:  # noqa: D102
        return plotly.graph_objects.layout.XAxis(
            side="top",
            tickvals=[
                group if group <= 2 else group+14 for group in range(1, 19)
            ],
            ticktext=[str(group) for group in range(1, 19)],
            range=[0.5-self._padding, 32.5+self._padding],
            showgrid=False,
            zeroline=False,
        )

    def y_axis(self) -> plotly.graph_objects.layout.YAxis:  # noqa: D102
        return plotly.graph_objects.layout.YAxis(
            tickvals=list(range(1, 8)),
            ticktext=[str(period) for period in range(1, 8)],
            range=[7.5+self._padding, 0.5-self._padding],
            showgrid=False,
            zeroline=False,
        )

    def cell_coordinates(  # noqa: D102
        self,
        element: Element,
    ) -> tuple[float, float]:
        if element == Element.HYDROGEN:
            x, y = 1., 1.
        elif element == Element.HELIUM:
            x, y = 32., 1.
        elif Element.LITHIUM <= element <= Element.ARGON:
            q, r = divmod(element.value - Element.LITHIUM.value, 8)
            x = r+1. if r < 2 else r+25.
            y = q + 2.
        elif Element.POTASSIUM <= element <= Element.XENON:
            q, r = divmod(element.value - Element.POTASSIUM.value, 18)
            x = r+1. if r < 2 else r+15.
            y = q + 4.
        else:
            q, r = divmod(element.value - Element.CAESIUM.value, 32)
            x = r + 1.
            y = q + 6.

        return x, y
