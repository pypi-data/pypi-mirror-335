"""Functions to convert Euler angles between basis triples."""

from __future__ import annotations

from numpy import pi, sin, cos, sqrt, arcsin, arccos, arctan2
from .utils import Float, AxisTriple


def convert_xzx_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sb, ca * sb)
        b = arccos(cb)
        c = arctan2(sb * sc, cc * sb)
    return float(a), float(b), float(c)


def convert_xzx_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sb, -sa * sb)
        b = arccos(cb)
        c = arctan2(-cc * sb, sb * sc)
    return float(a), float(b), float(c)


def convert_xzx_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cc * sb, ca * sc + cb * cc * sa)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(ca * sb, cc * sa + ca * cb * sc)
    return float(a), float(b), float(c)


def convert_xzx_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, cc * sb)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(-cc * sa - ca * cb * sc, ca * sb)
    return float(a), float(b), float(c)


def convert_xzx_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cc * sa - ca * cb * sc, sb * sc)
        b = arctan2(
            sqrt(1 + (-ca * cc + cb * sa * sc) * (ca * cc - cb * sa * sc)),
            ca * cc - cb * sa * sc,
        )
        c = arctan2(ca * sc + cb * cc * sa, -sa * sb)
    return float(a), float(b), float(c)


def convert_xzx_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb * sc, cc * sa + ca * cb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(sa * sb, ca * sc + cb * cc * sa)
    return float(a), float(b), float(c)


def convert_xzx_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = arcsin(cc * sb)
        c = arctan2(sb * sc, cb)
    return float(a), float(b), float(c)


def convert_xzx_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = arcsin(sb * sc)
        c = arctan2(cc * sb, cb)
    return float(a), float(b), float(c)


def convert_xzx_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cc * sa + ca * cb * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cc * sa - ca * cb * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = arcsin(cc * sa + ca * cb * sc)
        c = arctan2(ca * sb, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_xzx_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sb) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sb) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sa * sb, cb)
        b = arcsin(ca * sb)
        c = arctan2(cc * sa + ca * cb * sc, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_xzx_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sb, cb)
        b = arcsin(-sa * sb)
        c = arctan2(ca * sc + cb * cc * sa, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_xzx_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZX to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sc - cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sc + cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = arcsin(ca * sc + cb * cc * sa)
        c = arctan2(-sa * sb, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_xyx_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-ca * sb, sa * sb)
        b = arccos(cb)
        c = arctan2(cc * sb, -sb * sc)
    return float(a), float(b), float(c)


def convert_xyx_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sb, ca * sb)
        b = arccos(cb)
        c = arctan2(sb * sc, cc * sb)
    return float(a), float(b), float(c)


def convert_xyx_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb * sc, cc * sa + ca * cb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(sa * sb, ca * sc + cb * cc * sa)
    return float(a), float(b), float(c)


def convert_xyx_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, -sb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(-ca * sc - cb * cc * sa, sa * sb)
    return float(a), float(b), float(c)


def convert_xyx_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-ca * sc - cb * cc * sa, cc * sb)
        b = arctan2(
            sqrt(1 + (-ca * cb * cc + sa * sc) * (ca * cb * cc - sa * sc)),
            ca * cb * cc - sa * sc,
        )
        c = arctan2(cc * sa + ca * cb * sc, ca * sb)
    return float(a), float(b), float(c)


def convert_xyx_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * sc + cb * cc * sa)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(-ca * sb, cc * sa + ca * cb * sc)
    return float(a), float(b), float(c)


def convert_xyx_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = arcsin(-sb * sc)
        c = arctan2(cc * sb, cb)
    return float(a), float(b), float(c)


def convert_xyx_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = arcsin(cc * sb)
        c = arctan2(-sb * sc, cb)
    return float(a), float(b), float(c)


def convert_xyx_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + ca * sc + cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - ca * sc - cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = arcsin(ca * sc + cb * cc * sa)
        c = arctan2(sa * sb, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_xyx_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sb, cb)
        b = arcsin(sa * sb)
        c = arctan2(ca * sc + cb * cc * sa, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_xyx_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + ca * sb) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - ca * sb) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sa * sb, cb)
        b = arcsin(ca * sb)
        c = arctan2(cc * sa + ca * cb * sc, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_xyx_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYX to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa - ca * cb * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sa + ca * cb * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = arcsin(cc * sa + ca * cb * sc)
        c = arctan2(ca * sb, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_yxy_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cc * sa - ca * cb * sc, sb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(ca * sc + cb * cc * sa, -sa * sb)
    return float(a), float(b), float(c)


def convert_yxy_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb * sc, cc * sa + ca * cb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(sa * sb, ca * sc + cb * cc * sa)
    return float(a), float(b), float(c)


def convert_yxy_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sb, ca * sb)
        b = arccos(cb)
        c = arctan2(sb * sc, cc * sb)
    return float(a), float(b), float(c)


def convert_yxy_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sb, -sa * sb)
        b = arccos(cb)
        c = arctan2(-cc * sb, sb * sc)
    return float(a), float(b), float(c)


def convert_yxy_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cc * sb, ca * sc + cb * cc * sa)
        b = arctan2(
            sqrt(1 + (-ca * cb * cc + sa * sc) * (ca * cb * cc - sa * sc)),
            ca * cb * cc - sa * sc,
        )
        c = arctan2(ca * sb, cc * sa + ca * cb * sc)
    return float(a), float(b), float(c)


def convert_yxy_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, cc * sb)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(-cc * sa - ca * cb * sc, ca * sb)
    return float(a), float(b), float(c)


def convert_yxy_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sb, cb)
        b = arcsin(-sa * sb)
        c = arctan2(ca * sc + cb * cc * sa, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_yxy_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sc - cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sc + cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = arcsin(ca * sc + cb * cc * sa)
        c = arctan2(-sa * sb, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_yxy_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = arcsin(cc * sb)
        c = arctan2(sb * sc, cb)
    return float(a), float(b), float(c)


def convert_yxy_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = arcsin(sb * sc)
        c = arctan2(cc * sb, cb)
    return float(a), float(b), float(c)


def convert_yxy_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cc * sa + ca * cb * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cc * sa - ca * cb * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = arcsin(cc * sa + ca * cb * sc)
        c = arctan2(ca * sb, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_yxy_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXY to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sb) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sb) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sa * sb, cb)
        b = arcsin(ca * sb)
        c = arctan2(cc * sa + ca * cb * sc, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_yzy_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-ca * sc - cb * cc * sa, cc * sb)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(cc * sa + ca * cb * sc, ca * sb)
    return float(a), float(b), float(c)


def convert_yzy_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * sc + cb * cc * sa)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(-ca * sb, cc * sa + ca * cb * sc)
    return float(a), float(b), float(c)


def convert_yzy_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-ca * sb, sa * sb)
        b = arccos(cb)
        c = arctan2(cc * sb, -sb * sc)
    return float(a), float(b), float(c)


def convert_yzy_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sb, ca * sb)
        b = arccos(cb)
        c = arctan2(sb * sc, cc * sb)
    return float(a), float(b), float(c)


def convert_yzy_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb * sc, cc * sa + ca * cb * sc)
        b = arctan2(
            sqrt(1 + (-ca * cc + cb * sa * sc) * (ca * cc - cb * sa * sc)),
            ca * cc - cb * sa * sc,
        )
        c = arctan2(sa * sb, ca * sc + cb * cc * sa)
    return float(a), float(b), float(c)


def convert_yzy_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, -sb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(-ca * sc - cb * cc * sa, sa * sb)
    return float(a), float(b), float(c)


def convert_yzy_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + ca * sb) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - ca * sb) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sa * sb, cb)
        b = arcsin(ca * sb)
        c = arctan2(cc * sa + ca * cb * sc, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_yzy_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa - ca * cb * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sa + ca * cb * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = arcsin(cc * sa + ca * cb * sc)
        c = arctan2(ca * sb, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_yzy_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = arcsin(-sb * sc)
        c = arctan2(cc * sb, cb)
    return float(a), float(b), float(c)


def convert_yzy_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = arcsin(cc * sb)
        c = arctan2(-sb * sc, cb)
    return float(a), float(b), float(c)


def convert_yzy_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + ca * sc + cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - ca * sc - cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = arcsin(ca * sc + cb * cc * sa)
        c = arctan2(sa * sb, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_yzy_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZY to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sb, cb)
        b = arcsin(sa * sb)
        c = arctan2(ca * sc + cb * cc * sa, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_zyz_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cc * sb, ca * sc + cb * cc * sa)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(ca * sb, cc * sa + ca * cb * sc)
    return float(a), float(b), float(c)


def convert_zyz_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, cc * sb)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(-cc * sa - ca * cb * sc, ca * sb)
    return float(a), float(b), float(c)


def convert_zyz_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cc * sa - ca * cb * sc, sb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(ca * sc + cb * cc * sa, -sa * sb)
    return float(a), float(b), float(c)


def convert_zyz_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb * sc, cc * sa + ca * cb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(sa * sb, ca * sc + cb * cc * sa)
    return float(a), float(b), float(c)


def convert_zyz_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sb, ca * sb)
        b = arctan2(sqrt(1 - cb * cb), cb)
        c = arctan2(sb * sc, cc * sb)
    return float(a), float(b), float(c)


def convert_zyz_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sb, -sa * sb)
        b = arccos(cb)
        c = arctan2(-cc * sb, sb * sc)
    return float(a), float(b), float(c)


def convert_zyz_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cc * sa + ca * cb * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cc * sa - ca * cb * sc) < tol:
        a = arctan2(-sa * sb, cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = arcsin(cc * sa + ca * cb * sc)
        c = arctan2(ca * sb, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_zyz_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sb) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sb) < tol:
        a = arctan2(sb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sa * sb, cb)
        b = arcsin(ca * sb)
        c = arctan2(cc * sa + ca * cb * sc, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_zyz_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sb, cb)
        b = arcsin(-sa * sb)
        c = arctan2(ca * sc + cb * cc * sa, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_zyz_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sc - cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sc + cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = arcsin(ca * sc + cb * cc * sa)
        c = arctan2(-sa * sb, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_zyz_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = arcsin(cc * sb)
        c = arctan2(sb * sc, cb)
    return float(a), float(b), float(c)


def convert_zyz_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYZ to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = arcsin(sb * sc)
        c = arctan2(cc * sb, cb)
    return float(a), float(b), float(c)


def convert_zxz_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(ca * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb * sc, cc * sa + ca * cb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(sa * sb, ca * sc + cb * cc * sa)
    return float(a), float(b), float(c)


def convert_zxz_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - cb * sa * sc) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, -sb * sc)
        b = arccos(ca * cc - cb * sa * sc)
        c = arctan2(-ca * sc - cb * cc * sa, sa * sb)
    return float(a), float(b), float(c)


def convert_zxz_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-ca * sc - cb * cc * sa, cc * sb)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(cc * sa + ca * cb * sc, ca * sb)
    return float(a), float(b), float(c)


def convert_zxz_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb * cc + sa * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb * cc - sa * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * sc + cb * cc * sa)
        b = arccos(ca * cb * cc - sa * sc)
        c = arctan2(-ca * sb, cc * sa + ca * cb * sc)
    return float(a), float(b), float(c)


def convert_zxz_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-ca * sb, sa * sb)
        b = arctan2(sqrt(1 - cb * cb), cb)
        c = arctan2(cc * sb, -sb * sc)
    return float(a), float(b), float(c)


def convert_zxz_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sb, ca * sb)
        b = arccos(cb)
        c = arctan2(sb * sc, cc * sb)
    return float(a), float(b), float(c)


def convert_zxz_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + ca * sc + cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - ca * sc - cb * cc * sa) < tol:
        a = arctan2(ca * sb, cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = arcsin(ca * sc + cb * cc * sa)
        c = arctan2(sa * sb, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_zxz_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sa * sb) < tol:
        a = arctan2(cc * sb, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sb, cb)
        b = arcsin(sa * sb)
        c = arctan2(ca * sc + cb * cc * sa, ca * cc - cb * sa * sc)
    return float(a), float(b), float(c)


def convert_zxz_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + ca * sb) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - ca * sb) < tol:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sa * sb, cb)
        b = arcsin(ca * sb)
        c = arctan2(cc * sa + ca * cb * sc, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_zxz_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa - ca * cb * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sa + ca * cb * sc) < tol:
        a = arctan2(sa * sb, cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sb * sc, ca * cc - cb * sa * sc)
        b = arcsin(cc * sa + ca * cb * sc)
        c = arctan2(ca * sb, ca * cb * cc - sa * sc)
    return float(a), float(b), float(c)


def convert_zxz_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sb * sc) < tol:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = arcsin(-sb * sc)
        c = arctan2(cc * sb, cb)
    return float(a), float(b), float(c)


def convert_zxz_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXZ to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sb) < tol:
        a = arctan2(cc * sa + ca * cb * sc, ca * cc - cb * sa * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cb * cc * sa, ca * cb * cc - sa * sc)
        b = arcsin(cc * sb)
        c = arctan2(-sb * sc, cb)
    return float(a), float(b), float(c)


def convert_xzy_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa * sb - ca * sc, sa * sc + ca * cc * sb)
        b = arccos(cb * cc)
        c = arctan2(cb * sc, sb)
    return float(a), float(b), float(c)


def convert_xzy_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sc + ca * cc * sb, -cc * sa * sb + ca * sc)
        b = arccos(cb * cc)
        c = arctan2(-sb, cb * sc)
    return float(a), float(b), float(c)


def convert_xzy_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-sb, cb * sa)
        b = arccos(ca * cb)
        c = arctan2(sa * sc + ca * cc * sb, -ca * sb * sc + cc * sa)
    return float(a), float(b), float(c)


def convert_xzy_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cb * sa, sb)
        b = arccos(ca * cb)
        c = arctan2(ca * sb * sc - cc * sa, sa * sc + ca * cc * sb)
    return float(a), float(b), float(c)


def convert_xzy_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc - sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc + sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sb * sc - cc * sa, cb * sc)
        b = arctan2(
            sqrt(1 + (-ca * cc - sa * sb * sc) * (ca * cc + sa * sb * sc)),
            ca * cc + sa * sb * sc,
        )
        c = arctan2(cb * sa, -cc * sa * sb + ca * sc)
    return float(a), float(b), float(c)


def convert_xzy_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc - sa * sb * sc) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc + sa * sb * sc) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cb * sc, -ca * sb * sc + cc * sa)
        b = arccos(ca * cc + sa * sb * sc)
        c = arctan2(cc * sa * sb - ca * sc, cb * sa)
    return float(a), float(b), float(c)


def convert_xzy_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + sb) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - sb) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sa, ca * cb)
        b = arcsin(sb)
        c = arctan2(cb * sc, cb * cc)
    return float(a), float(b), float(c)


def convert_xzy_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = arcsin(cb * sc)
        c = arctan2(sb, cb * cc)
    return float(a), float(b), float(c)


def convert_xzy_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sb * sc + cc * sa) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + ca * sb * sc - cc * sa) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = arcsin(-ca * sb * sc + cc * sa)
        c = arctan2(sa * sc + ca * cc * sb, ca * cb)
    return float(a), float(b), float(c)


def convert_xzy_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sc - ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sa * sc + ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = arcsin(sa * sc + ca * cc * sb)
        c = arctan2(-ca * sb * sc + cc * sa, ca * cb)
    return float(a), float(b), float(c)


def convert_xzy_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa * sb + ca * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 + cc * sa * sb - ca * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = arcsin(-cc * sa * sb + ca * sc)
        c = arctan2(cb * sa, ca * cc + sa * sb * sc)
    return float(a), float(b), float(c)


def convert_xzy_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XZY to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * sa) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cb * sa) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(sb, ca * cb)
        b = arcsin(cb * sa)
        c = arctan2(-cc * sa * sb + ca * sc, ca * cc + sa * sb * sc)
    return float(a), float(b), float(c)


def convert_xyz_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sc - ca * cc * sb, ca * sc + cc * sa * sb)
        b = arccos(cb * cc)
        c = arctan2(sb, cb * sc)
    return float(a), float(b), float(c)


def convert_xyz_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sc + cc * sa * sb, -sa * sc + ca * cc * sb)
        b = arccos(cb * cc)
        c = arctan2(-cb * sc, sb)
    return float(a), float(b), float(c)


def convert_xyz_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + sa * sb * sc) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - sa * sb * sc) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cb * sc, cc * sa + ca * sb * sc)
        b = arccos(ca * cc - sa * sb * sc)
        c = arctan2(ca * sc + cc * sa * sb, cb * sa)
    return float(a), float(b), float(c)


def convert_xyz_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * sb * sc, cb * sc)
        b = arccos(ca * cc - sa * sb * sc)
        c = arctan2(-cb * sa, ca * sc + cc * sa * sb)
    return float(a), float(b), float(c)


def convert_xyz_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cb * sa, sb)
        b = arctan2(sqrt(1 - ca * cb * ca * cb), ca * cb)
        c = arctan2(cc * sa + ca * sb * sc, -sa * sc + ca * cc * sb)
    return float(a), float(b), float(c)


def convert_xyz_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb, cb * sa)
        b = arccos(ca * cb)
        c = arctan2(sa * sc - ca * cc * sb, cc * sa + ca * sb * sc)
    return float(a), float(b), float(c)


def convert_xyz_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = arcsin(cb * sc)
        c = arctan2(sb, cb * cc)
    return float(a), float(b), float(c)


def convert_xyz_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sb) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sa, ca * cb)
        b = arcsin(sb)
        c = arctan2(cb * sc, cb * cc)
    return float(a), float(b), float(c)


def convert_xyz_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cb * sa) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cb * sa) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sb, ca * cb)
        b = arcsin(cb * sa)
        c = arctan2(ca * sc + cc * sa * sb, ca * cc - sa * sb * sc)
    return float(a), float(b), float(c)


def convert_xyz_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sc - cc * sa * sb) < tol:
        a = arctan2(sb, ca * cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sc + cc * sa * sb) < tol:
        a = arctan2(sb, ca * cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = arcsin(ca * sc + cc * sa * sb)
        c = arctan2(cb * sa, ca * cc - sa * sb * sc)
    return float(a), float(b), float(c)


def convert_xyz_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sc + ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sa * sc - ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = arcsin(-sa * sc + ca * cc * sb)
        c = arctan2(cc * sa + ca * sb * sc, ca * cb)
    return float(a), float(b), float(c)


def convert_xyz_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from XYZ to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa - ca * sb * sc) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sa + ca * sb * sc) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = arcsin(cc * sa + ca * sb * sc)
        c = arctan2(-sa * sc + ca * cc * sb, ca * cb)
    return float(a), float(b), float(c)


def convert_yxz_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc - sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc + sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sb * sc - cc * sa, cb * sc)
        b = arccos(ca * cc + sa * sb * sc)
        c = arctan2(cb * sa, -cc * sa * sb + ca * sc)
    return float(a), float(b), float(c)


def convert_yxz_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc - sa * sb * sc) < tol:
        a = arctan2(ca * cc * sb + sa * sc, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc + sa * sb * sc) < tol:
        a = arctan2(ca * cc * sb + sa * sc, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cb * sc, -ca * sb * sc + cc * sa)
        b = arccos(ca * cc + sa * sb * sc)
        c = arctan2(cc * sa * sb - ca * sc, cb * sa)
    return float(a), float(b), float(c)


def convert_yxz_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa * sb - ca * sc, ca * cc * sb + sa * sc)
        b = arccos(cb * cc)
        c = arctan2(cb * sc, sb)
    return float(a), float(b), float(c)


def convert_yxz_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * cc * sb + sa * sc, -cc * sa * sb + ca * sc)
        b = arccos(cb * cc)
        c = arctan2(-sb, cb * sc)
    return float(a), float(b), float(c)


def convert_yxz_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-sb, cb * sa)
        b = arctan2(sqrt(1 - ca * cb * ca * cb), ca * cb)
        c = arctan2(ca * cc * sb + sa * sc, -ca * sb * sc + cc * sa)
    return float(a), float(b), float(c)


def convert_yxz_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cb * sa, sb)
        b = arccos(ca * cb)
        c = arctan2(ca * sb * sc - cc * sa, ca * cc * sb + sa * sc)
    return float(a), float(b), float(c)


def convert_yxz_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa * sb + ca * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 + cc * sa * sb - ca * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * cc * sb + sa * sc, cb * cc)
        b = arcsin(-cc * sa * sb + ca * sc)
        c = arctan2(cb * sa, ca * cc + sa * sb * sc)
    return float(a), float(b), float(c)


def convert_yxz_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * sa) < tol:
        a = arctan2(ca * cc * sb + sa * sc, cb * cc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cb * sa) < tol:
        a = arctan2(ca * cc * sb + sa * sc, cb * cc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(sb, ca * cb)
        b = arcsin(cb * sa)
        c = arctan2(-cc * sa * sb + ca * sc, ca * cc + sa * sb * sc)
    return float(a), float(b), float(c)


def convert_yxz_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + sb) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - sb) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sa, ca * cb)
        b = arcsin(sb)
        c = arctan2(cb * sc, cb * cc)
    return float(a), float(b), float(c)


def convert_yxz_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = arcsin(cb * sc)
        c = arctan2(sb, cb * cc)
    return float(a), float(b), float(c)


def convert_yxz_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sb * sc + cc * sa) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + ca * sb * sc - cc * sa) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = arcsin(-ca * sb * sc + cc * sa)
        c = arctan2(ca * cc * sb + sa * sc, ca * cb)
    return float(a), float(b), float(c)


def convert_yxz_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YXZ to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc * sb - sa * sc) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * cc * sb + sa * sc) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = arcsin(ca * cc * sb + sa * sc)
        c = arctan2(-ca * sb * sc + cc * sa, ca * cb)
    return float(a), float(b), float(c)


def convert_yzx_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cb * sa, sb)
        b = arccos(ca * cb)
        c = arctan2(cc * sa + ca * sb * sc, -sa * sc + ca * cc * sb)
    return float(a), float(b), float(c)


def convert_yzx_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb, cb * sa)
        b = arccos(ca * cb)
        c = arctan2(sa * sc - ca * cc * sb, cc * sa + ca * sb * sc)
    return float(a), float(b), float(c)


def convert_yzx_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sc - ca * cc * sb, ca * sc + cc * sa * sb)
        b = arccos(cb * cc)
        c = arctan2(sb, cb * sc)
    return float(a), float(b), float(c)


def convert_yzx_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sc + cc * sa * sb, -sa * sc + ca * cc * sb)
        b = arccos(cb * cc)
        c = arctan2(-cb * sc, sb)
    return float(a), float(b), float(c)


def convert_yzx_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + sa * sb * sc) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - sa * sb * sc) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cb * sc, cc * sa + ca * sb * sc)
        b = arctan2(
            sqrt(1 + (-ca * cc + sa * sb * sc) * (ca * cc - sa * sb * sc)),
            ca * cc - sa * sb * sc,
        )
        c = arctan2(ca * sc + cc * sa * sb, cb * sa)
    return float(a), float(b), float(c)


def convert_yzx_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * sb * sc, cb * sc)
        b = arccos(ca * cc - sa * sb * sc)
        c = arctan2(-cb * sa, ca * sc + cc * sa * sb)
    return float(a), float(b), float(c)


def convert_yzx_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sc + ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sa * sc - ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = arcsin(-sa * sc + ca * cc * sb)
        c = arctan2(cc * sa + ca * sb * sc, ca * cb)
    return float(a), float(b), float(c)


def convert_yzx_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa - ca * sb * sc) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sa + ca * sb * sc) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = arcsin(cc * sa + ca * sb * sc)
        c = arctan2(-sa * sc + ca * cc * sb, ca * cb)
    return float(a), float(b), float(c)


def convert_yzx_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = arcsin(cb * sc)
        c = arctan2(sb, cb * cc)
    return float(a), float(b), float(c)


def convert_yzx_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sb) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sa, ca * cb)
        b = arcsin(sb)
        c = arctan2(cb * sc, cb * cc)
    return float(a), float(b), float(c)


def convert_yzx_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cb * sa) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cb * sa) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sb, ca * cb)
        b = arcsin(cb * sa)
        c = arctan2(ca * sc + cc * sa * sb, ca * cc - sa * sb * sc)
    return float(a), float(b), float(c)


def convert_yzx_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from YZX to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sc - cc * sa * sb) < tol:
        a = arctan2(sb, ca * cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sc + cc * sa * sb) < tol:
        a = arctan2(sb, ca * cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = arcsin(ca * sc + cc * sa * sb)
        c = arctan2(cb * sa, ca * cc - sa * sb * sc)
    return float(a), float(b), float(c)


def convert_zyx_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-sb, cb * sa)
        b = arccos(ca * cb)
        c = arctan2(sa * sc + ca * cc * sb, -ca * sb * sc + cc * sa)
    return float(a), float(b), float(c)


def convert_zyx_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cb * sa, sb)
        b = arccos(ca * cb)
        c = arctan2(ca * sb * sc - cc * sa, sa * sc + ca * cc * sb)
    return float(a), float(b), float(c)


def convert_zyx_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc - sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc + sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sb * sc - cc * sa, cb * sc)
        b = arccos(ca * cc + sa * sb * sc)
        c = arctan2(cb * sa, -cc * sa * sb + ca * sc)
    return float(a), float(b), float(c)


def convert_zyx_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc - sa * sb * sc) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc + sa * sb * sc) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cb * sc, -ca * sb * sc + cc * sa)
        b = arccos(ca * cc + sa * sb * sc)
        c = arctan2(cc * sa * sb - ca * sc, cb * sa)
    return float(a), float(b), float(c)


def convert_zyx_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa * sb - ca * sc, sa * sc + ca * cc * sb)
        b = arctan2(sqrt(1 - cb * cc * cb * cc), cb * cc)
        c = arctan2(cb * sc, sb)
    return float(a), float(b), float(c)


def convert_zyx_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sc + ca * cc * sb, -cc * sa * sb + ca * sc)
        b = arccos(cb * cc)
        c = arctan2(-sb, cb * sc)
    return float(a), float(b), float(c)


def convert_zyx_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sb * sc + cc * sa) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + ca * sb * sc - cc * sa) < tol:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = arcsin(-ca * sb * sc + cc * sa)
        c = arctan2(sa * sc + ca * cc * sb, ca * cb)
    return float(a), float(b), float(c)


def convert_zyx_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sc - ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sa * sc + ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc + sa * sb * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-cc * sa * sb + ca * sc, cb * cc)
        b = arcsin(sa * sc + ca * cc * sb)
        c = arctan2(-ca * sb * sc + cc * sa, ca * cb)
    return float(a), float(b), float(c)


def convert_zyx_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa * sb + ca * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 + cc * sa * sb - ca * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = arcsin(-cc * sa * sb + ca * sc)
        c = arctan2(cb * sa, ca * cc + sa * sb * sc)
    return float(a), float(b), float(c)


def convert_zyx_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * sa) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cb * sa) < tol:
        a = arctan2(sa * sc + ca * cc * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(sb, ca * cb)
        b = arcsin(cb * sa)
        c = arctan2(-cc * sa * sb + ca * sc, ca * cc + sa * sb * sc)
    return float(a), float(b), float(c)


def convert_zyx_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + sb) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - sb) < tol:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sa, ca * cb)
        b = arcsin(sb)
        c = arctan2(cb * sc, cb * cc)
    return float(a), float(b), float(c)


def convert_zyx_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZYX to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-ca * sb * sc + cc * sa, ca * cc + sa * sb * sc)
        b = arcsin(cb * sc)
        c = arctan2(sb, cb * cc)
    return float(a), float(b), float(c)


def convert_zxy_xzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to XZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + sa * sb * sc) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - sa * sb * sc) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cb * sc, cc * sa + ca * sb * sc)
        b = arccos(ca * cc - sa * sb * sc)
        c = arctan2(ca * sc + cc * sa * sb, cb * sa)
    return float(a), float(b), float(c)


def convert_zxy_xyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to XYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cc + sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cc - sa * sb * sc) < tol:
        a = arctan2(sb, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * sb * sc, cb * sc)
        b = arccos(ca * cc - sa * sb * sc)
        c = arctan2(-cb * sa, ca * sc + cc * sa * sb)
    return float(a), float(b), float(c)


def convert_zxy_yxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to YXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(-cb * sa, sb)
        b = arccos(ca * cb)
        c = arctan2(cc * sa + ca * sb * sc, -sa * sc + ca * cc * sb)
    return float(a), float(b), float(c)


def convert_zxy_yzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to YZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * cb) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = 0.0
        c = 0.0
    elif abs(1 + ca * cb) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = pi
        c = 0.0
    else:
        a = arctan2(sb, cb * sa)
        b = arccos(ca * cb)
        c = arctan2(sa * sc - ca * cc * sb, cc * sa + ca * sb * sc)
    return float(a), float(b), float(c)


def convert_zxy_zyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to ZYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi
        c = 0.0
    else:
        a = arctan2(sa * sc - ca * cc * sb, ca * sc + cc * sa * sb)
        b = arctan2(sqrt(1 - cb * cc * cb * cc), cb * cc)
        c = arctan2(sb, cb * sc)
    return float(a), float(b), float(c)


def convert_zxy_zxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to ZXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cb * cc) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = 0.0
        c = 0.0
    elif abs(1 + cb * cc) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = pi
        c = 0.0
    else:
        a = arctan2(ca * sc + cc * sa * sb, -sa * sc + ca * cc * sb)
        b = arccos(cb * cc)
        c = arctan2(-cb * sc, sb)
    return float(a), float(b), float(c)


def convert_zxy_xzy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to XZY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cb * sa) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cb * sa) < tol:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(sb, ca * cb)
        b = arcsin(cb * sa)
        c = arctan2(ca * sc + cc * sa * sb, ca * cc - sa * sb * sc)
    return float(a), float(b), float(c)


def convert_zxy_xyz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to XYZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - ca * sc - cc * sa * sb) < tol:
        a = arctan2(sb, ca * cb)
        b = pi / 2
        c = 0.0
    elif abs(1 + ca * sc + cc * sa * sb) < tol:
        a = arctan2(sb, ca * cb)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-sa * sc + ca * cc * sb, cb * cc)
        b = arcsin(ca * sc + cc * sa * sb)
        c = arctan2(cb * sa, ca * cc - sa * sb * sc)
    return float(a), float(b), float(c)


def convert_zxy_yxz(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to YXZ."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sa * sc + ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = -pi / 2
        c = 0.0
    elif abs(1 + sa * sc - ca * cc * sb) < tol:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = arcsin(-sa * sc + ca * cc * sb)
        c = arctan2(cc * sa + ca * sb * sc, ca * cb)
    return float(a), float(b), float(c)


def convert_zxy_yzx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to YZX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - cc * sa - ca * sb * sc) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = pi / 2
        c = 0.0
    elif abs(1 + cc * sa + ca * sb * sc) < tol:
        a = arctan2(ca * sc + cc * sa * sb, cb * cc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sc, ca * cc - sa * sb * sc)
        b = arcsin(cc * sa + ca * sb * sc)
        c = arctan2(-sa * sc + ca * cc * sb, ca * cb)
    return float(a), float(b), float(c)


def convert_zxy_zyx(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to ZYX."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 + cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = -pi / 2
        c = 0.0
    elif abs(1 - cb * sc) < tol:
        a = arctan2(cb * sa, ca * cb)
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = arcsin(cb * sc)
        c = arctan2(sb, cb * cc)
    return float(a), float(b), float(c)


def convert_zxy_zxy(
    a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles from ZXY to ZXY."""
    sa, ca = sin(a), cos(a)
    sb, cb = sin(b), cos(b)
    sc, cc = sin(c), cos(c)
    if abs(1 - sb) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = pi / 2
        c = 0.0
    elif abs(1 + sb) < tol:
        a = arctan2(cc * sa + ca * sb * sc, ca * cc - sa * sb * sc)
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(cb * sa, ca * cb)
        b = arcsin(sb)
        c = arctan2(cb * sc, cb * cc)
    return float(a), float(b), float(c)


def convert(
    p: AxisTriple, q: AxisTriple, a: Float, b: Float, c: Float, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Convert Euler angles between given basis triples."""
    return globals()[f"convert_{p}_{q}"](a, b, c, tol=tol)  # type: ignore
