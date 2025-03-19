"""Functions to compute Euler angles from given rotation matrices."""

from numpy import pi, arcsin, arccos, sqrt, arctan2
from .utils import AxisTriple, Float, RotMatrix


def angles_xzx(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the XZX Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[0, 0]) < tol:
        a = arctan2(-mat[1, 2], mat[2, 2])
        b = 0.0
        c = 0.0
    elif abs(1.0 + mat[0, 0]) < tol:
        a = arctan2(-mat[1, 2], mat[2, 2])
        b = pi
        c = 0.0
    else:
        a = arctan2(mat[2, 0], mat[1, 0])
        b = arccos(mat[0, 0])
        c = arctan2(mat[0, 2], -mat[0, 1])
    return float(a), float(b), float(c)


def angles_xyx(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the XYX Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[0, 0]) < tol:
        a = arctan2(mat[2, 1], mat[1, 1])
        b = 0.0
        c = 0.0
    elif abs(1.0 + mat[0, 0]) < tol:
        a = arctan2(mat[2, 1], mat[1, 1])
        b = pi
        c = 0.0
    else:
        a = arctan2(mat[1, 0], -mat[2, 0])
        b = arccos(mat[0, 0])
        c = arctan2(mat[0, 1], mat[0, 2])
    return float(a), float(b), float(c)


def angles_yxy(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the YXY Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[1, 1]) < tol:
        a = arctan2(-mat[2, 0], mat[0, 0])
        b = 0.0
        c = 0.0
    elif abs(1.0 + mat[1, 1]) < tol:
        a = arctan2(-mat[2, 0], mat[0, 0])
        b = pi
        c = 0.0
    else:
        a = arctan2(mat[0, 1], mat[2, 1])
        b = arccos(mat[1, 1])
        c = arctan2(mat[1, 0], -mat[1, 2])
    return float(a), float(b), float(c)


def angles_yzy(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the YZY Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[1, 1]) < tol:
        a = arctan2(mat[0, 2], mat[2, 2])
        b = 0.0
        c = 0.0
    elif abs(1.0 + mat[1, 1]) < tol:
        a = arctan2(mat[0, 2], mat[2, 2])
        b = pi
        c = 0.0
    else:
        a = arctan2(mat[2, 1], -mat[0, 1])
        b = arccos(mat[1, 1])
        c = arctan2(mat[1, 2], mat[1, 0])
    return float(a), float(b), float(c)


def angles_zyz(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the ZYZ Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[2, 2]) < tol:
        a = arctan2(-mat[0, 1], mat[1, 1])
        b = 0.0
        c = 0.0
    elif abs(1.0 + mat[2, 2]) < tol:
        a = arctan2(-mat[0, 1], mat[1, 1])
        b = pi
        c = 0.0
    else:
        a = arctan2(mat[1, 2], mat[0, 2])
        b = arctan2(sqrt(1 - mat[2, 2] * mat[2, 2]), mat[2, 2])
        c = arctan2(mat[2, 1], -mat[2, 0])
    return float(a), float(b), float(c)


def angles_zxz(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the ZXZ Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[2, 2]) < tol:
        a = arctan2(mat[1, 0], mat[0, 0])
        b = 0.0
        c = 0.0
    elif abs(1.0 + mat[2, 2]) < tol:
        a = arctan2(mat[1, 0], mat[0, 0])
        b = pi
        c = 0.0
    else:
        a = arctan2(mat[0, 2], -mat[1, 2])
        b = arccos(mat[2, 2])
        c = arctan2(mat[2, 0], mat[2, 1])
    return float(a), float(b), float(c)


def angles_xzy(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the XZY Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[0, 1]) < tol:
        a = arctan2(-mat[1, 2], mat[2, 2])
        b = -pi / 2
        c = 0.0
    elif abs(1.0 + mat[0, 1]) < tol:
        a = arctan2(-mat[1, 2], mat[2, 2])
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(mat[2, 1], mat[1, 1])
        b = arcsin(-mat[0, 1])
        c = arctan2(mat[0, 2], mat[0, 0])
    return float(a), float(b), float(c)


def angles_xyz(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the XYZ Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[0, 2]) < tol:
        a = arctan2(mat[2, 1], mat[1, 1])
        b = pi / 2
        c = 0.0
    elif abs(1.0 + mat[0, 2]) < tol:
        a = arctan2(mat[2, 1], mat[1, 1])
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-mat[1, 2], mat[2, 2])
        b = arcsin(mat[0, 2])
        c = arctan2(-mat[0, 1], mat[0, 0])
    return float(a), float(b), float(c)


def angles_yxz(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the YXZ Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[1, 2]) < tol:
        a = arctan2(-mat[2, 0], mat[0, 0])
        b = -pi / 2
        c = 0.0
    elif abs(1.0 + mat[1, 2]) < tol:
        a = arctan2(-mat[2, 0], mat[0, 0])
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(mat[0, 2], mat[2, 2])
        b = arcsin(-mat[1, 2])
        c = arctan2(mat[1, 0], mat[1, 1])
    return float(a), float(b), float(c)


def angles_yzx(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the YZX Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[1, 0]) < tol:
        a = arctan2(mat[0, 2], mat[2, 2])
        b = pi / 2
        c = 0.0
    elif abs(1.0 + mat[1, 0]) < tol:
        a = arctan2(mat[0, 2], mat[2, 2])
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-mat[2, 0], mat[0, 0])
        b = arcsin(mat[1, 0])
        c = arctan2(-mat[1, 2], mat[1, 1])
    return float(a), float(b), float(c)


def angles_zyx(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the ZYX Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[2, 0]) < tol:
        a = arctan2(-mat[0, 1], mat[1, 1])
        b = -pi / 2
        c = 0.0
    elif abs(1.0 + mat[2, 0]) < tol:
        a = arctan2(-mat[0, 1], mat[1, 1])
        b = pi / 2
        c = 0.0
    else:
        a = arctan2(mat[1, 0], mat[0, 0])
        b = arcsin(-mat[2, 0])
        c = arctan2(mat[2, 1], mat[2, 2])
    return float(a), float(b), float(c)


def angles_zxy(mat: RotMatrix, tol: Float = 1e-8) -> tuple[float, float, float]:
    """Compute the ZXY Euler angles for the given rotation matrix."""
    if abs(1.0 - mat[2, 1]) < tol:
        a = arctan2(mat[1, 0], mat[0, 0])
        b = pi / 2
        c = 0.0
    elif abs(1.0 + mat[2, 1]) < tol:
        a = arctan2(mat[1, 0], mat[0, 0])
        b = -pi / 2
        c = 0.0
    else:
        a = arctan2(-mat[0, 1], mat[1, 1])
        b = arcsin(mat[2, 1])
        c = arctan2(-mat[2, 0], mat[2, 2])
    return float(a), float(b), float(c)


def angles(
    p: AxisTriple, mat: RotMatrix, tol: Float = 1e-8
) -> tuple[float, float, float]:
    """Compute the Euler angles for the given basis triple and rotation matrix."""
    return globals()[f"angles_{p}"](mat)  # type: ignore
