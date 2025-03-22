import numba

from ..const import *
from ..l_math import *


"""
    * 4D SuperSimplex noise, with XYZ oriented like noise_3d_xzy
    * and W for an extra degree of freedom. W repeats eventually.
    * Recommended for time-varied animations which texture a 3D object (W = time)
    * in a space where Z is vertical

    * Basically use Z as the vertical axis
"""
def noise_4d_xzyw(x: float, y: float, z: float, w: float, seed: int) -> float:
    xy = x + y
    s2 = xy * -0.21132486540518699998
    zz = z * 0.28867513459481294226
    ww = w * 1.118033988749894
    xr = x + (zz + ww + s2)
    yr = y + (zz + ww + s2)
    zr = xy * -0.57735026918962599998 + (zz + ww)
    wr = z * -0.866025403784439 + ww
    
    return noise_4d_unskewed_base(xr, yr, zr, wr, seed)

"""
    * 4D SuperSimplex noise, with XYZ oriented like noise_3d_xyz
    * and W for an extra degree of freedom. W repeats eventually.
    * Recommended for time-varied animations which texture a 3D object (W = time)
    * in a space where Y is vertical

    * Basically use Y as the vertical axis
"""
def noise_4d_xyzw(x: float, y: float, z: float, w: float, seed: int) -> float:
    xz = x + z
    s2 = xz * -0.21132486540518699998
    yy = y * 0.28867513459481294226
    ww = w * 1.118033988749894
    xr = x + (yy + ww + s2)
    zr = z + (yy + ww + s2)
    yr = xz * -0.57735026918962599998 + (yy + ww)
    wr = y * -0.866025403784439 + ww
    
    return noise_4d_unskewed_base(xr, yr, zr, wr, seed)

"""
    * 4D SuperSimplex noise, with XYZ oriented like noise_3d_fallback
    * and W for an extra degree of freedom. W repeats eventually.
    * Recommended for time-varied animations which texture a 3D object (W = time)
    * where there isn't a clear distinction between horizontal and vertical

    * Basically y, z are used interchangeably
"""
def noise_4d_x_yz_w(x: float, y: float, z: float, w: float, seed: int) -> float:
    xyz = x + y + z
    ww = w * 1.118033988749894
    s2 = xyz * -0.16666666666666666 + ww
    xs = x + s2
    ys = y + s2
    zs = z + s2
    ws = -0.5 * xyz + ww
    
    return noise_4d_unskewed_base(xs, ys, zs, ws, seed)

"""
    * 4D SuperSimplex noise, fallback lattice orientation.
"""
def noise_4d_fallback(x: float, y: float, z: float, w: float, seed: int) -> float:
    s = SKEW_4D * (x + y + z + w)
    xs, ys, zs, ws = x + s, y + s, z + s, w + s
    
    return noise_4d_unskewed_base(xs, ys, zs, ws, seed)

def noise_4d_unskewed_base(xs: float, ys: float, zs: float, ws: float, seed: int) -> float:
    xsb, ysb, zsb, wsb = fast_floor(xs), fast_floor(ys), fast_floor(zs), fast_floor(ws)
    xsi, ysi, zsi, wsi = xs - xsb, ys - ysb, zs - zsb, ws - wsb
    
    ssi = (xsi + ysi + zsi + wsi) * UNSKEW_4D
    xi, yi, zi, wi = xsi + ssi, ysi + ssi, zsi + ssi, wsi + ssi
    
    xsvp, ysvp, zsvp, wsvp = xsb * PRIME_X, ysb * PRIME_Y, zsb * PRIME_Z, wsb * PRIME_W
    
    index = ((fast_floor(xs * 4) & 3) << 0) | ((fast_floor(ys * 4) & 3) << 2) | ((fast_floor(zs * 4) & 3) << 4) | ((fast_floor(ws * 4) & 3) << 6)
    
    value = 0.0
    secondary_index_start, secondary_index_stop = LOOKUP_4D_A[index]
    
    for i in range(secondary_index_start, secondary_index_stop):
        c = LOOKUP_4D_B[i]
        dx, dy, dz, dw = xi + c.dx, yi + c.dy, zi + c.dz, wi + c.dw
        a = (dx * dx + dy * dy) + (dz * dz + dw * dw)
        
        if a < RSQUARED_4D:
            a -= RSQUARED_4D
            a *= a
            value += a * a * grad4(seed, xsvp + c.xsvp, ysvp + c.ysvp, zsvp + c.zsvp, wsvp + c.wsvp, dx, dy, dz, dw)
    
    return value
