
def gcd(a: int, b: int) -> int:

    while b:
        a, b = b, a % b
    return abs(a)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:

    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_r, old_s, old_t


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

    return pow(base, exp, mod)