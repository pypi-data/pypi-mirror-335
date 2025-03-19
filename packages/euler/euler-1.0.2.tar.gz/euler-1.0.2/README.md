# euler

[![Generic badge](https://img.shields.io/badge/python-3.10+-green.svg)](https://docs.python.org/3.10/)
[![Checked with Mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](https://github.com/python/mypy)
[![PyPI version shields.io](https://img.shields.io/pypi/v/neverlocal-euler.svg)](https://pypi.python.org/pypi/neverlocal-euler/)
[![PyPI status](https://img.shields.io/pypi/status/neverlocal-euler.svg)](https://pypi.python.org/pypi/neverlocal-euler/)

A library for Euler angle computation and conversion.

## Installation

You can install the library from PyPI as follows:

```
pip install -U neverlocal-euler
```

## Usage

The library is designed to be imported directly, analogously to NumPy:

```python
>>> from numpy import pi
>>> import euler
```

The 12 possible axis triples available for Euler angles can be accessed as follows:

```python
>>> euler.AXIS_TRIPLES
('xzx', 'xyx', 'yxy', 'yzy', 'zyz', 'zxz', 'xzy', 'xyz', 'yxz', 'yzx', 'zyx', 'zxy')
```

For static typing purposes, the corresponding literal type alias is `euler.AxisTriple`.

The `euler.matrix_<pqr>` functions, where `<pqr>` is an axis triple,
can be used to compute a rotation matrix from Euler angles:

```python
>>> h = euler.matrix_zxz(pi/2, pi/2, pi/2)
>>> h.round(3)
array([[-0., -0.,  1.],
       [ 0., -1., -0.],
       [ 1.,  0.,  0.]])
```

The `euler.angles_<pqr>` functions, where `<pqr>` is an axis triple,
can be used to compute Euler angles from a rotation matrix:

```python
>>> a, b, c = euler.angles_xyz(h)
>>> a, b, c
(3.141592653589793, 1.5707963267948966, 0.0)
```

The `euler.convert_<pqr>_<uvw>` functions, finally,
can be used to convert Euler angles from axis triple `<pqr>` to axis triple `<uvw>`:

```py
>>> euler.convert_zxz_xyz(pi/2, pi/2, pi/2)
(3.141592653589793, 1.5707963267948966, 0.0)

```

The functions `euler.matrix`, `euler.angles` and `euler.convert` serve an analogous purpose,
but take the axis triple(s) as string parameter(s):

```py
>>> h = euler.matrix("zxz", pi/2, pi/2, pi/2)
>>> h.round(3)
array([[-0., -0.,  1.],
       [ 0., -1., -0.],
       [ 1.,  0.,  0.]])
>>> a, b, c = euler.angles("xyz", h)
>>> a, b, c
(3.141592653589793, 1.5707963267948966, 0.0)
>>> euler.convert("zxz", "xyz", pi/2, pi/2, pi/2)
(3.141592653589793, 1.5707963267948966, 0.0)
```

Matrix calculations are originally taken from https://ntrs.nasa.gov/citations/19770019231,
and have been independently verified (see the [`test`](./test/) folder).

## License

[LGPLv3](./LICENSE) © NeverLocal Ltd
