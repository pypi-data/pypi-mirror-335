from ..l_math import *

from ..const import *


"""
    * 3D OpenSimplex2S/SuperSimplex noise, with better visual isotropy in (X, Y).
    * Recommended for 3D terrain and time-varied animations.
    * The Z coordinate should always be the "different" coordinate in whatever your use case is.
    * For a time varied animation, call noise_3d_xzy(x, y, T).

    * Basically treat Z as the vertical axis
"""
def noise_3d_xzy(x: float, y: float, z: float, seed: int) -> float:
    # Re-orient the cubic lattices without skewing
    xy = x + y
    s2 = xy * ROTATE3_ORTHOGONALIZER
    zz = z * ROOT3OVER3
    xr = x + s2 + zz
    yr = y + s2 + zz
    zr = xy * -ROOT3OVER3 + zz

    # Evaluate both lattices to form a BCC lattice.
    return noise_3d_unrotated_base(xr, yr, zr, seed)

"""
    * 3D OpenSimplex2S/SuperSimplex noise, with better visual isotropy in (X, Z).
    * Recommended for 3D terrain and time-varied animations.
    * The Y coordinate should always be the "different" coordinate in whatever your use case is.
    * For a time varied animation, call noise_3d_xyz(x, T, y).

    * Basically treat Y as the vertical axis
"""
def noise_3d_xyz(x: float, y: float, z: float, seed: int) -> float:
    # Re-orient the cubic lattices without skewing
    xz = x + z
    s2 = xz * -0.211324865405187
    yy = y * ROOT3OVER3
    xr = x + s2 + yy
    zr = z + s2 + yy
    yr = xz * -ROOT3OVER3 + yy

    # Evaluate both lattices to form a BCC lattice.
    return noise_3d_unrotated_base(xr, yr, zr, seed)

"""
    * 3D OpenSimplex2S/SuperSimplex noise, fallback rotation option
    * Use Noise3_ImproveXY or Noise3_ImproveXZ instead, wherever appropriate.
    * They have less diagonal bias. This function's best use is as a fallback.

    * Fallback if the vertical axis is unknown.
"""
def noise_3d_fallback(x: float, y: float, z: float, seed: int) -> float:
    # Re-orient the cubic lattices via rotation, to produce a familiar look.
    # Orthonormal rotation. Not a skew transform.
    r = FALLBACK_ROTATE3 * (x + y + z)
    xr, yr, zr = r - x, r - y, r - z

    # Evaluate both lattices to form a BCC lattice.
    return noise_3d_unrotated_base(xr, yr, zr, seed)

"""
    * Generate overlapping cubic lattices for 3D Re-oriented BCC noise.
    * Lookup table implementation inspired by DigitalShadow.
    * It was actually faster to narrow down the points in the loop itself,
    * than to build up the index with enough info to isolate 8 points.
"""
def noise_3d_unrotated_base(xr: float, yr: float, zr: float, seed: int) -> float:
    # Get base points and offsets.
    xrb = fast_floor(xr)
    yrb = fast_floor(yr)
    zrb = fast_floor(zr)
    xi = float(xr - xrb)
    yi = float(yr - yrb)
    zi = float(zr - zrb)

    # Prime pre-multiplication for hash. Also flip seed for second lattice copy.
    xrbp = xrb * PRIME_X
    yrbp = yrb * PRIME_Y
    zrbp = zrb * PRIME_Z
    seed2 = seed ^ -0x52D547B2E96ED629

    # -1 if positive, 0 if negative.
    xNMask = int(-0.5 - xi)
    yNMask = int(-0.5 - yi)
    zNMask = int(-0.5 - zi)

    # First vertex.
    x0 = xi + xNMask
    y0 = yi + yNMask
    z0 = zi + zNMask
    a0 = RSQUARED_3D - x0 * x0 - y0 * y0 - z0 * z0
    value = (a0 * a0) * (a0 * a0) * grad3(seed,
        xrbp + (xNMask & PRIME_X), yrbp + (yNMask & PRIME_Y), zrbp + (zNMask & PRIME_Z), x0, y0, z0)

    # Second vertex.
    x1 = xi - 0.5
    y1 = yi - 0.5
    z1 = zi - 0.5
    a1 = RSQUARED_3D - x1 * x1 - y1 * y1 - z1 * z1
    value += (a1 * a1) * (a1 * a1) * grad3(seed2,
        xrbp + PRIME_X, yrbp + PRIME_Y, zrbp + PRIME_Z, x1, y1, z1)

    # Shortcuts for building the remaining falloffs.
    xAFlipMask0 = ((xNMask | 1) << 1) * x1
    yAFlipMask0 = ((yNMask | 1) << 1) * y1
    zAFlipMask0 = ((zNMask | 1) << 1) * z1
    xAFlipMask1 = (-2 - (xNMask << 2)) * x1 - 1.0
    yAFlipMask1 = (-2 - (yNMask << 2)) * y1 - 1.0
    zAFlipMask1 = (-2 - (zNMask << 2)) * z1 - 1.0

    skip5 = False
    a2 = xAFlipMask0 + a0
    if a2 > 0:
        x2 = x0 - (xNMask | 1)
        y2 = y0
        z2 = z0
        value += (a2 * a2) * (a2 * a2) * grad3(
            seed,
            xrbp + (~xNMask & PRIME_X), yrbp + (yNMask & PRIME_Y), zrbp + (zNMask & PRIME_Z),
            x2, y2, z2
        )
    else:
        a3 = yAFlipMask0 + zAFlipMask0 + a0
        if a3 > 0:
            x3 = x0
            y3 = y0 - (yNMask | 1)
            z3 = z0 - (zNMask | 1)
            value += (a3 * a3) * (a3 * a3) * grad3(
                seed,
                xrbp + (xNMask & PRIME_X), yrbp + (~yNMask & PRIME_Y), zrbp + (~zNMask & PRIME_Z),
                x3, y3, z3
            )

        a4 = xAFlipMask1 + a1
        if a4 > 0:
            x4 = (xNMask | 1) + x1
            y4 = y1
            z4 = z1
            value += (a4 * a4) * (a4 * a4) * grad3(
                seed2,
                xrbp + (xNMask & (PRIME_X * 2)), yrbp + PRIME_Y, zrbp + PRIME_Z,
                x4, y4, z4
            )
            skip5 = True

    skip9 = False
    a6 = yAFlipMask0 + a0
    if a6 > 0:
        x6 = x0
        y6 = y0 - (yNMask | 1)
        z6 = z0
        value += (a6 * a6) * (a6 * a6) * grad3(
            seed,
            xrbp + (xNMask & PRIME_X), yrbp + (~yNMask & PRIME_Y), zrbp + (zNMask & PRIME_Z),
            x6, y6, z6
        )
    else:
        a7 = xAFlipMask0 + zAFlipMask0 + a0
        if a7 > 0:
            x7 = x0 - (xNMask | 1)
            y7 = y0
            z7 = z0 - (zNMask | 1)
            value += (a7 * a7) * (a7 * a7) * grad3(
                seed,
                xrbp + (~xNMask & PRIME_X), yrbp + (yNMask & PRIME_Y), zrbp + (~zNMask & PRIME_Z),
                x7, y7, z7
            )

        a8 = yAFlipMask1 + a1
        if a8 > 0:
            x8 = x1
            y8 = (yNMask | 1) + y1
            z8 = z1
            value += (a8 * a8) * (a8 * a8) * grad3(
                seed2,
                xrbp + PRIME_X, yrbp + (yNMask & (PRIME_Y << 1)), zrbp + PRIME_Z,
                x8, y8, z8
            )
            skip9 = True

    skipD = False
    aA = zAFlipMask0 + a0
    if aA > 0:
        xA = x0
        yA = y0
        zA = z0 - (zNMask | 1)
        value += (aA * aA) * (aA * aA) * grad3(
            seed,
            xrbp + (xNMask & PRIME_X), yrbp + (yNMask & PRIME_Y), zrbp + (~zNMask & PRIME_Z),
            xA, yA, zA
        )
    else:
        aB = xAFlipMask0 + yAFlipMask0 + a0
        if aB > 0:
            xB = x0 - (xNMask | 1)
            yB = y0 - (yNMask | 1)
            zB = z0
            value += (aB * aB) * (aB * aB) * grad3(
                seed,
                xrbp + (~xNMask & PRIME_X), yrbp + (~yNMask & PRIME_Y), zrbp + (zNMask & PRIME_Z),
                xB, yB, zB
            )

        aC = zAFlipMask1 + a1
        if aC > 0:
            xC = x1
            yC = y1
            zC = (zNMask | 1) + z1
            value += (aC * aC) * (aC * aC) * grad3(
                seed2,
                xrbp + PRIME_X, yrbp + PRIME_Y, zrbp + (zNMask & (PRIME_Z << 1)),
                xC, yC, zC
            )
            skipD = True

    if not skip5:
        a5 = yAFlipMask1 + zAFlipMask1 + a1
        if a5 > 0:
            x5 = x1
            y5 = (yNMask | 1) + y1
            z5 = (zNMask | 1) + z1
            value += (a5 * a5) * (a5 * a5) * grad3(
                seed2,
                xrbp + PRIME_X, yrbp + (yNMask & (PRIME_Y << 1)), zrbp + (zNMask & (PRIME_Z << 1)),
                x5, y5, z5
            )

    if not skip9:
        a9 = xAFlipMask1 + zAFlipMask1 + a1
        if a9 > 0:
            x9 = (xNMask | 1) + x1
            y9 = y1
            z9 = (zNMask | 1) + z1
            value += (a9 * a9) * (a9 * a9) * grad3(
                seed2,
                xrbp + (xNMask & (PRIME_X * 2)), yrbp + PRIME_Y, zrbp + (zNMask & (PRIME_Z << 1)),
                x9, y9, z9
            )

    if not skipD:
        aD = xAFlipMask1 + yAFlipMask1 + a1
        if aD > 0:
            xD = (xNMask | 1) + x1
            yD = (yNMask | 1) + y1
            zD = z1
            value += (aD * aD) * (aD * aD) * grad3(
                seed2,
                xrbp + (xNMask & (PRIME_X << 1)), yrbp + (yNMask & (PRIME_Y << 1)), zrbp + PRIME_Z,
                xD, yD, zD
            )

    return value