import hypothesis.extra.numpy
import hypothesis.strategies
import numpy
import pytest
import plotly

from ptvis.utils import add_annotations, add_shapes, linearly_transform


@hypothesis.given(
    hypothesis.strategies.lists(
        hypothesis.strategies.builds(
            plotly.graph_objects.layout.Annotation,
            xref=pytest.helpers.plotly.coord_refs("x"),
            yref=pytest.helpers.plotly.coord_refs("y"),
        ),
        min_size=4,
        max_size=4,
    ),
)
def test_add_annotations(annotations):
    row = 2
    col = 2

    desired = plotly.graph_objects.Figure()
    desired.set_subplots(rows=row, cols=col)
    for annotation in annotations:
        desired.add_annotation(annotation, row=row, col=col)

    actual = plotly.graph_objects.Figure()
    actual.set_subplots(rows=row, cols=col)
    add_annotations(actual, annotations, row=row, col=col)

    assert actual == desired


@hypothesis.given(
    hypothesis.strategies.lists(
        hypothesis.strategies.builds(
            plotly.graph_objects.layout.Shape,
            xref=pytest.helpers.plotly.coord_refs("x"),
            yref=pytest.helpers.plotly.coord_refs("y"),
        ),
        min_size=4,
        max_size=4,
    ),
)
def test_add_shapes(shapes):
    row = 2
    col = 2

    desired = plotly.graph_objects.Figure()
    desired.set_subplots(rows=row, cols=col)
    for shape in shapes:
        desired.add_shape(shape, row=row, col=col)

    actual = plotly.graph_objects.Figure()
    actual.set_subplots(rows=row, cols=col)
    add_shapes(actual, shapes, row=row, col=col)

    assert actual == desired


@hypothesis.given(
    pytest.helpers.numpy.mutually_broadcastable_arrays(
        [float]*5,
        elements=[
            hypothesis.strategies.floats(min_value=0, max_value=1),
            hypothesis.strategies.just(0),
            hypothesis.strategies.just(0),
            hypothesis.strategies.just(1),
            hypothesis.strategies.just(1),
        ],
    ),
)
def test_linearly_transform(arrays):
    x = arrays[0]
    y = linearly_transform(*arrays)

    assert numpy.allclose(y, x)
