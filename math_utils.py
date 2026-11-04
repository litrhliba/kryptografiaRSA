

import sys

def gcd(a: int, b: int) -> int:
   
    while b:
        a, b = b, a % b
    return abs(a)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def mod_inverse(a: int, m: int) -> int:
    
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Odwrotność modularna nie istnieje dla a={a} i m={m} (gcd != 1)")
    return x % m


def mod_pow_iterative(base: int, exp: int, mod: int) -> int:
    
    if mod == 1:
        return 0
    res = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res


def mod_pow_native(base: int, exp: int, mod: int) -> int:
    """Natywne potęgowanie modularne w Pythonie za pomocą funkcji pow()."""
    return pow(base, exp, mod)
