from .const import *


def fast_floor(x: float) -> int:
    x_int = int(x)
    return x_int - 1 if x < x_int else x_int

def grad2(seed: int, xsvp: int, ysvp: int, dx: float, dy: float) -> float:
    hash_val = seed ^ xsvp ^ ysvp
    hash_val *= HASH_MULTIPLIER
    hash_val ^= hash_val >> (64 - N_GRADS_2D_EXPONENT + 1)
    gi = hash_val & ((N_GRADS_2D - 1) << 1)
    return GRADIENTS_2D[gi | 0] * dx + GRADIENTS_2D[gi | 1] * dy

def grad3(seed: int, xrvp: int, yrvp: int, zrvp: int, dx: float, dy: float, dz: float) -> float:
    hash_val = (seed ^ xrvp) ^ (yrvp ^ zrvp)
    hash_val *= HASH_MULTIPLIER
    hash_val ^= hash_val >> (64 - N_GRADS_3D_EXPONENT + 2)
    gi = hash_val & ((N_GRADS_3D - 1) << 2)
    return GRADIENTS_3D[gi | 0] * dx + GRADIENTS_3D[gi | 1] * dy + GRADIENTS_3D[gi | 2] * dz

def grad4(seed: int, xsvp: int, ysvp: int, zsvp: int, wsvp: int, dx: float, dy: float, dz: float, dw: float) -> float:
    hash_val = seed ^ (xsvp ^ ysvp) ^ (zsvp ^ wsvp)
    hash_val *= HASH_MULTIPLIER
    hash_val ^= hash_val >> (64 - N_GRADS_4D_EXPONENT + 2)
    gi = hash_val & ((N_GRADS_4D - 1) << 2)
    return (GRADIENTS_4D[gi | 0] * dx + GRADIENTS_4D[gi | 1] * dy) + (GRADIENTS_4D[gi | 2] * dz + GRADIENTS_4D[gi | 3] * dw)