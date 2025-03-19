from itertools import product
import pytest
import numpy as np
from euler.utils import AxisTriple, AXIS_TRIPLES
from euler.angles import angles
from euler.matrix import matrix

NUM_ANGLES = 17

assert (NUM_ANGLES-1)%4 == 0, "Tested angles must include 0, pi/2, pi and -pi/2."

@pytest.mark.parametrize("p", AXIS_TRIPLES)
def test_angles(p: AxisTriple) -> None:
    for a, b, c in product(np.linspace(0, 2*np.pi, NUM_ANGLES), repeat=3):
        mat_p = np.round(matrix(p, a, b, c), 9)
        _a, _b, _c = angles(p, mat_p)
        _mat_p = np.round(matrix(p, _a, _b, _c), 9)
        assert np.allclose(mat_p, _mat_p)
