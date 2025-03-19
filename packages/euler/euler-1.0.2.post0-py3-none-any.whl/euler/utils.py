"""Utilities for this library."""

from typing import Any, Final, Literal, TypeAlias
import numpy as np

Float: TypeAlias = int | float | np.integer[Any] | np.floating[Any]
"""Type alias for floating-point numbers."""

RotMatrix: TypeAlias = np.ndarray[
    tuple[int, int], np.dtype[np.integer[Any] | np.floating[Any]]
]
"""Type alias for 3-by-3 rotation matrices."""

AxisTriple: TypeAlias = Literal[
    "xzx",
    "xyx",
    "yxy",
    "yzy",
    "zyz",
    "zxz",
    "xzy",
    "xyz",
    "yxz",
    "yzx",
    "zyx",
    "zxy",
]
"""Type alias for all possible axis triples."""

AXIS_TRIPLES: Final[tuple[AxisTriple, ...]] = (
    "xzx",
    "xyx",
    "yxy",
    "yzy",
    "zyz",
    "zxz",
    "xzy",
    "xyz",
    "yxz",
    "yzx",
    "zyx",
    "zxy",
)
"""Sequence of all possible axis triples."""
