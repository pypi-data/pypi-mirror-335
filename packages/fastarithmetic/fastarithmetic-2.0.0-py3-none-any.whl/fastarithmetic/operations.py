from decimal import Decimal, getcontext
import numpy as np

def fast_add(a, b):
    """ Fast addition of two large numbers (O(1)) """
    return a + b

def fast_sub(a, b):
    """ Fast subtraction of two large numbers (O(1)) """
    return a - b

def fast_mul(a, b):
    """ Fast multiplication using Karatsuba for large numbers (O(n^1.58)) """
    if a.bit_length() < 1024 or b.bit_length() < 1024:
        return a * b  # Use native multiplication for small numbers

    m = max(a.bit_length(), b.bit_length()) // 2
    a1, a0 = divmod(a, 1 << m)
    b1, b0 = divmod(b, 1 << m)

    z0 = fast_mul(a0, b0)
    z2 = fast_mul(a1, b1)
    z1 = fast_mul(a0 + a1, b0 + b1) - z0 - z2

    return (z2 << (2 * m)) + (z1 << m) + z0

def fast_div(a, b, precision=100):
    """ Fast division using Newton-Raphson (O(M(n))) """
    getcontext().prec = precision

    a = Decimal(a)
    b = Decimal(b)

    # Initial guess: reciprocal of b
    x = Decimal(1) / b

    # Newton-Raphson refinement
    for _ in range(int(np.log2(precision)) + 1):
        x = x * (2 - b * x)

    return a * x