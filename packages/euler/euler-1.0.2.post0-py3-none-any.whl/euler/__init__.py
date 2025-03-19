"""A library for Euler angle computation and conversion."""

__version__ = "1.0.2"

from .utils import AxisTriple, AXIS_TRIPLES
from .matrix import *  # noqa
from .angles import *  # noqa
from .convert import *  # noqa

__all__ = (
    ("AxisTriple", "AXIS_TRIPLES", "matrix", "angles", "convert")  # noqa
    + tuple(f"matrix_{p}" for p in AXIS_TRIPLES)
    + tuple(f"angles_{p}" for p in AXIS_TRIPLES)
    + tuple(f"convert_{p}_{q}" for p in AXIS_TRIPLES for q in AXIS_TRIPLES)
)
