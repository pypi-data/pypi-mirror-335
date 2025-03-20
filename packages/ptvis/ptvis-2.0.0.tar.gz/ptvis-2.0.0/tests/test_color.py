import hypothesis.strategies
import pandas.testing
import pytest
import wclr

from ptvis.color import (
    CategoricalColorConversion,
    ContinuousColorConversion,
    DiscreteColorConversion,
    IdentityColorConversion,
)


class TestContinuousColorConversion:

    @hypothesis.given(
        hypothesis.strategies.none()
        | hypothesis.strategies.integers(min_value=0, max_value=255),
    )
    def test_apply_variable_domain(self, value):
        conversion = ContinuousColorConversion(
            colors=["#0000ff", "#ff0000"],
            na_color="#444444",
        )
        actual = conversion.apply([0, value, 255])

        desired = pandas.Series(
            [
                "#0000ff",
                (
                    "#444444" if value is None
                    else f"#{value:02x}00{255-value:02x}"
                ),
                "#ff0000",
            ],
        )

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )

    def test_apply_variable_domain_all_na(self):
        conversion = ContinuousColorConversion(na_color="#444444")
        actual = conversion.apply([None])

        desired = pandas.Series(["#444444"])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )

    @hypothesis.given(
        hypothesis.strategies.none()
        | hypothesis.strategies.integers(min_value=-128, max_value=383),
    )
    def test_apply_fixed_domain(self, value):
        conversion = ContinuousColorConversion(
            colors=["#0000ff", "#ff0000"],
            value_min=0,
            value_max=255,
            lower_color="black",
            higher_color="white",
            na_color="#444444",
        )
        actual = conversion.apply([value])

        if value is None:
            color = "#444444"
        elif value < 0:
            color = "black"
        elif value <= 255:
            color = f"#{value:02x}00{255-value:02x}"
        else:
            color = "white"
        desired = pandas.Series([color])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )


class TestDiscreteColorConversion:

    @hypothesis.given(
        hypothesis.strategies.none()
        | hypothesis.strategies.integers(min_value=-1000, max_value=1000),
    )
    def test_apply_variable_domain(self, value):
        conversion = DiscreteColorConversion(
            colors=["blue", "red"],
            na_color="#444444",
            n_intervals=2,
            closed="low",
            include_boundary=True,
        )
        actual = conversion.apply([-1000, value, 1000])

        if value is None:
            color = "#444444"
        elif value < 0:
            color = "blue"
        else:
            color = "red"
        desired = pandas.Series(["blue", color, "red"])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )

    def test_apply_variable_domain_all_na(self):
        conversion = ContinuousColorConversion(na_color="#444444")
        actual = conversion.apply([None])

        desired = pandas.Series(["#444444"])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )

    @hypothesis.given(
        hypothesis.strategies.none()
        | hypothesis.strategies.integers(min_value=-2000, max_value=2000),
    )
    def test_apply_fixed_domain(self, value):
        conversion = DiscreteColorConversion(
            colors=["blue", "red"],
            value_min=-1000,
            value_max=1000,
            lower_color="black",
            higher_color="white",
            na_color="#444444",
            n_intervals=2,
            closed="low",
            include_boundary=False,
        )
        actual = conversion.apply([value])

        if value is None:
            color = "#444444"
        elif value < -1000:
            color = "black"
        elif value < 0:
            color = "blue"
        elif value < 1000:
            color = "red"
        else:
            color = "white"
        desired = pandas.Series([color])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )

    @pytest.mark.parametrize("closed", ["low", "high"])
    @pytest.mark.parametrize("include_boundary", [False, True])
    def test_apply_at_edge(self, closed, include_boundary):
        conversion = DiscreteColorConversion(
            colors=["blue", "red"],
            value_min=-1,
            value_max=1,
            lower_color="black",
            higher_color="white",
            n_intervals=2,
            closed=closed,
            include_boundary=include_boundary,
        )
        actual = conversion.apply([-1, 0, 1])

        desired = pandas.Series(
            [
                "blue" if closed == "low" or include_boundary else "black",
                "blue" if closed == "high" else "red",
                "red" if closed == "high" or include_boundary else "white",
            ],
        )

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )


class TestCategoricalColorConversion:

    def test_apply(self):
        conversion = CategoricalColorConversion(
            mapping={"mapped": "red"},
            missing_colors=["black"],
            na_color="#444444",
        )
        actual = conversion.apply(["mapped", "not_mapped", None])

        desired = pandas.Series(["red", "black", "#444444"])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )

    def test_apply_all_na(self):
        conversion = ContinuousColorConversion(na_color="#444444")
        actual = conversion.apply([None])

        desired = pandas.Series(["#444444"])

        pandas.testing.assert_series_equal(
            actual.map(wclr.Color.from_str),
            desired.map(wclr.Color.from_str),
        )


class TestIdentityColorConversion:

    @hypothesis.given(
        hypothesis.strategies.lists(
            pytest.helpers.wclr.color_strs(),
            min_size=0,
            max_size=10,
        ),
    )
    def test_apply(self, values):
        values = pandas.Series(values, dtype=str)

        conversion = IdentityColorConversion()
        actual = conversion.apply(values)

        desired = values

        pandas.testing.assert_series_equal(actual, desired)
