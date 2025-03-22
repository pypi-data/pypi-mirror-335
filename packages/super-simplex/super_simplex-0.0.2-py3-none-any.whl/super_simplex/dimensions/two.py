from ..l_math import *

from ..const import *


"""
    * 2D OpenSimplex2S/SuperSimplex noise, standard lattice orientation.
"""
def noise_2d(x: float, y: float, seed: int) -> float:
    s = (x + y) * SKEW_2D

    xs = x + s
    ys = y + s

    return _noise_2d_unskewed_base(xs, ys, seed)

"""
    * 2D OpenSimplex2S/SuperSimplex noise, with Y pointing down the main diagonal.
    * Might be better for a 2D sandbox style game, where Y is vertical.
    * Probably slightly less optimal for heightmaps or continent maps,
    * unless your map is centered around an equator. It's a slight
    * difference, but the option is here to make it easy.

    * Basically, rotated skewed grid with Y axis is the main Cartesian diagonal
"""
def noise_2d_rotated(x: float, y: float, seed: int) -> float:
    # Skew transform and rotation baked into one.
    xx = x * ROOT2OVER2
    yy = y * (ROOT2OVER2 * (1 + 2 * SKEW_2D))
    
    return _noise_2d_unskewed_base(seed, yy + xx, yy - xx)

"""
    * 2D OpenSimplex2S/SuperSimplex noise base.
"""
def _noise_2d_unskewed_base(xs: float, ys: float, seed: int) -> float:
    xsb = fast_floor(xs)
    ysb = fast_floor(ys)

    xi = float(xs - xsb)
    yi = float(ys - ysb)

    # Prime pre-multiplication for hash.
    xsbp = xsb * PRIME_X
    ysbp = ysb * PRIME_Y

    # Unskew.
    t = (xi + yi) * float(UNSKEW_2D)
    dx0 = xi + t
    dy0 = yi + t

    # First vertex.
    a0 = RSQUARED_2D - dx0 * dx0 - dy0 * dy0
    value = (a0 * a0) * (a0 * a0) * grad2(seed, xsbp, ysbp, dx0, dy0)

    # Second vertex.
    a1 = float(2 * (1 + 2 * UNSKEW_2D) * (1 / UNSKEW_2D + 2)) * t + \
        (float(-2 * (1 + 2 * UNSKEW_2D) * (1 + 2 * UNSKEW_2D)) + a0)

    dx1 = dx0 - float(1 + 2 * UNSKEW_2D)
    dy1 = dy0 - float(1 + 2 * UNSKEW_2D)

    value += (a1 * a1) * (a1 * a1) * grad2(seed, xsbp + PRIME_X, ysbp + PRIME_Y, dx1, dy1)

    # Third and fourth vertices.
    # Nested conditionals were faster than compact bit logic/arithmetic.
    xmyi = xi - yi
    if t < UNSKEW_2D:
        if xi + xmyi > 1:
            dx2 = dx0 - (3 * UNSKEW_2D + 2)
            dy2 = dy0 - (3 * UNSKEW_2D + 1)
            a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if a2 > 0:
                value += (a2 * a2) * (a2 * a2) * grad2(seed, xsbp + (PRIME_X << 1), ysbp + PRIME_Y, dx2, dy2)
        else:
            dx2 = dx0 - UNSKEW_2D
            dy2 = dy0 - (UNSKEW_2D + 1)
            a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if a2 > 0:
                value += (a2 * a2) * (a2 * a2) * grad2(seed, xsbp, ysbp + PRIME_Y, dx2, dy2)

        if yi - xmyi > 1:
            dx3 = dx0 - (3 * UNSKEW_2D + 1)
            dy3 = dy0 - (3 * UNSKEW_2D + 2)
            a3 = RSQUARED_2D - dx3 * dx3 - dy3 * dy3
            if a3 > 0:
                value += (a3 * a3) * (a3 * a3) * grad2(seed, xsbp + PRIME_X, ysbp + (PRIME_Y << 1), dx3, dy3)
        else:
            dx3 = dx0 - (UNSKEW_2D + 1)
            dy3 = dy0 - UNSKEW_2D
            a3 = RSQUARED_2D - dx3 * dx3 - dy3 * dy3
            if a3 > 0:
                value += (a3 * a3) * (a3 * a3) * grad2(seed, xsbp + PRIME_X, ysbp, dx3, dy3)
    else:
        if xi + xmyi < 0:
            dx2 = dx0 + (1 + UNSKEW_2D)
            dy2 = dy0 + UNSKEW_2D
            a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if a2 > 0:
                value += (a2 * a2) * (a2 * a2) * grad2(seed, xsbp - PRIME_X, ysbp, dx2, dy2)
        else:
            dx2 = dx0 - (UNSKEW_2D + 1)
            dy2 = dy0 - UNSKEW_2D
            a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if a2 > 0:
                value += (a2 * a2) * (a2 * a2) * grad2(seed, xsbp + PRIME_X, ysbp, dx2, dy2)

        if yi < xmyi:
            dx2 = dx0 + UNSKEW_2D
            dy2 = dy0 + (UNSKEW_2D + 1)
            a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if a2 > 0:
                value += (a2 * a2) * (a2 * a2) * grad2(seed, xsbp, ysbp - PRIME_Y, dx2, dy2)
        else:
            dx2 = dx0 - UNSKEW_2D
            dy2 = dy0 - (UNSKEW_2D + 1)
            a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if a2 > 0:
                value += (a2 * a2) * (a2 * a2) * grad2(seed, xsbp, ysbp + PRIME_Y, dx2, dy2)

    return value