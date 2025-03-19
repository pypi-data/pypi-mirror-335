from itertools import product
import pytest
import numpy as np
from euler.utils import Float, RotMatrix, AxisTriple, AXIS_TRIPLES
from euler.matrix import matrix

def rot_x(a: Float) -> RotMatrix:
    sa, ca = np.sin(a), np.cos(a)
    return np.array([
        [1, 0, 0],
        [0, ca, -sa],
        [0, sa, ca],
    ], dtype=np.float64)

def rot_y(a: Float) -> RotMatrix:
    sa, ca = np.sin(a), np.cos(a)
    return np.array([
        [ca, 0, sa],
        [0, 1, 0],
        [-sa, 0, ca],
    ], dtype=np.float64)

def rot_z(a: Float) -> RotMatrix:
    sa, ca = np.sin(a), np.cos(a)
    return np.array([
        [ca, -sa, 0],
        [sa, ca, 0],
        [0, 0, 1],
    ], dtype=np.float64)

ROT = {
    "x": rot_x,
    "y": rot_y,
    "z": rot_z
}

NUM_ANGLES = 17

assert (NUM_ANGLES-1)%4 == 0, "Tested angles must include 0, pi/2, pi and -pi/2."

@pytest.mark.parametrize("p", AXIS_TRIPLES)
def test_matrix(p: AxisTriple) -> None:
    for a, b, c in product(np.linspace(0, 2*np.pi, NUM_ANGLES), repeat=3):
        composed = ROT[p[0]](a) @ ROT[p[1]](b) @ ROT[p[2]](c)
        computed = matrix(p, a, b, c)
        assert np.allclose(composed, computed)
