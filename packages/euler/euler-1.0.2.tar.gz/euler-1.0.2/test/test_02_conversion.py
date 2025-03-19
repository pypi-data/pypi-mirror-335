from itertools import product
import pytest
import numpy as np
from euler.utils import AxisTriple, AXIS_TRIPLES
from euler.angles import angles
from euler.matrix import matrix
from euler.convert import convert

NUM_ANGLES = 17

assert (NUM_ANGLES-1)%4 == 0, "Tested angles must include 0, pi/2, pi and -pi/2."

@pytest.mark.parametrize("p,q", tuple(product(AXIS_TRIPLES, repeat=2)))
def test_conversion_explicit(p: AxisTriple, q: AxisTriple) -> None:
    for a_p, b_p, c_p in product(np.linspace(0, 2*np.pi, NUM_ANGLES), repeat=3):
        mat_p = np.round(matrix(p, a_p, b_p, c_p), 9)
        a_q, b_q, c_q = angles(q, mat_p)
        mat_q = np.round(matrix(q, a_q, b_q, c_q), 9)
        assert np.allclose(mat_p, mat_q)


@pytest.mark.parametrize("p,q", tuple(product(AXIS_TRIPLES, repeat=2)))
def test_conversion_implicit(p: AxisTriple, q: AxisTriple) -> None:
    for a_p, b_p, c_p in product(np.linspace(0, 2*np.pi, NUM_ANGLES), repeat=3):
        mat_p = np.round(matrix(p, a_p, b_p, c_p), 9)
        a_q, b_q, c_q = convert(p, q, a_p, b_p, c_p)
        mat_q = np.round(matrix(q, a_q, b_q, c_q), 9)
        assert np.allclose(mat_p, mat_q)
