from collections.abc import Sequence
from typing import Any, TYPE_CHECKING, TypeVar, Union

import numpy
from numpy.typing import NDArray
from pandas import Series

if TYPE_CHECKING:
    import sys
    if sys.version_info < (3, 11):
        from typing_extensions import assert_never
    else:
        from typing import assert_never
else:
    assert_never = None


__all__ = ["assert_never", "ObjectSeriesLike", "RealSeriesLike", "SeriesLike"]


_T = TypeVar("_T")
_NumPyT = TypeVar("_NumPyT", bound=numpy.generic)

SeriesLike = Union[
    _T,
    Sequence[_T],
    Sequence[_NumPyT],
    dict[Any, _T],
    dict[Any, _NumPyT],
    NDArray[_NumPyT],
    "Series[_T]",
]

ObjectSeriesLike = Union[
    _T,
    Sequence[_T],
    dict[Any, _T],
    NDArray[numpy.object_],
    "Series[Any]",
]

RealSeriesLike = Union[
    SeriesLike[int, "numpy.integer[Any]"],
    SeriesLike[float, "numpy.floating[Any]"],
]
