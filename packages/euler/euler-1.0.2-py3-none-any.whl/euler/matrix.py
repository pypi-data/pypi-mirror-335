"""Functions to generate rotation matrices for given Euler angles."""

import numpy as np
from numpy import sin, cos
from .utils import Float, AxisTriple, RotMatrix


def matrix_xzx(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given XZX Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [cb, -cc * sb, sb * sc],
            [ca * sb, ca * cb * cc - sa * sc, -cc * sa - ca * cb * sc],
            [sa * sb, ca * sc + cb * cc * sa, ca * cc - cb * sa * sc],
        ],
        dtype=np.float64,
    )


def matrix_xyx(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given XYX Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [cb, sb * sc, cc * sb],
            [sa * sb, ca * cc - cb * sa * sc, -ca * sc - cb * cc * sa],
            [-ca * sb, cc * sa + ca * cb * sc, ca * cb * cc - sa * sc],
        ],
        dtype=np.float64,
    )


def matrix_yxy(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given YXY Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cc - cb * sa * sc, sa * sb, ca * sc + cb * cc * sa],
            [sb * sc, cb, -cc * sb],
            [-cc * sa - ca * cb * sc, ca * sb, ca * cb * cc - sa * sc],
        ],
        dtype=np.float64,
    )


def matrix_yzy(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given YZY Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cb * cc - sa * sc, -ca * sb, cc * sa + ca * cb * sc],
            [cc * sb, cb, sb * sc],
            [-ca * sc - cb * cc * sa, sa * sb, ca * cc - cb * sa * sc],
        ],
        dtype=np.float64,
    )


def matrix_zyz(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given ZYZ Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cb * cc - sa * sc, -cc * sa - ca * cb * sc, ca * sb],
            [ca * sc + cb * cc * sa, ca * cc - cb * sa * sc, sa * sb],
            [-cc * sb, sb * sc, cb],
        ],
        dtype=np.float64,
    )


def matrix_zxz(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given ZXZ Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cc - cb * sa * sc, -ca * sc - cb * cc * sa, sa * sb],
            [cc * sa + ca * cb * sc, ca * cb * cc - sa * sc, -ca * sb],
            [sb * sc, cc * sb, cb],
        ],
        dtype=np.float64,
    )


def matrix_xzy(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given XZY Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [cb * cc, -sb, cb * sc],
            [sa * sc + ca * cc * sb, ca * cb, ca * sb * sc - cc * sa],
            [cc * sa * sb - ca * sc, cb * sa, ca * cc + sa * sb * sc],
        ],
        dtype=np.float64,
    )


def matrix_xyz(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given XYZ Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [cb * cc, -cb * sc, sb],
            [ca * sc + cc * sa * sb, ca * cc - sa * sb * sc, -cb * sa],
            [sa * sc - ca * cc * sb, cc * sa + ca * sb * sc, ca * cb],
        ],
        dtype=np.float64,
    )


def matrix_yxz(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given YXZ Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cc + sa * sb * sc, cc * sa * sb - ca * sc, cb * sa],
            [cb * sc, cb * cc, -sb],
            [ca * sb * sc - cc * sa, ca * cc * sb + sa * sc, ca * cb],
        ],
        dtype=np.float64,
    )


def matrix_yzx(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given YZX Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cb, sa * sc - ca * cc * sb, cc * sa + ca * sb * sc],
            [sb, cb * cc, -cb * sc],
            [-cb * sa, ca * sc + cc * sa * sb, ca * cc - sa * sb * sc],
        ],
        dtype=np.float64,
    )


def matrix_zyx(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given ZYX Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cb, ca * sb * sc - cc * sa, sa * sc + ca * cc * sb],
            [cb * sa, ca * cc + sa * sb * sc, cc * sa * sb - ca * sc],
            [-sb, cb * sc, cb * cc],
        ],
        dtype=np.float64,
    )


def matrix_zxy(a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given ZXY Euler angles."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    return np.array(
        [
            [ca * cc - sa * sb * sc, -cb * sa, ca * sc + cc * sa * sb],
            [cc * sa + ca * sb * sc, ca * cb, sa * sc - ca * cc * sb],
            [-cb * sc, sb, cb * cc],
        ],
        dtype=np.float64,
    )


def matrix(p: AxisTriple, a: Float, b: Float, c: Float) -> RotMatrix:
    """Generate the rotation matrix for the given Euler basis triple and angles."""
    return globals()[f"matrix_{p}"](a, b, c)  # type: ignore
