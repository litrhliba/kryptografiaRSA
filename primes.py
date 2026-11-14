

import math
import secrets


def _sieve_of_eratosthenes(limit: int) -> tuple[int, ...]:
    """Generuje krotkę wszystkich liczb pierwszych <= limit za pomocą sita Eratostenesa."""
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            is_prime[i * i : limit + 1 : i] = b"\x00" * ((limit - i * i) // i + 1)
    return tuple(i for i, flag in enumerate(is_prime) if flag)


# Wstępna tablica 309 małych liczb pierwszych (<= 2048) do szybkiej filtracji kandydatów
SMALL_PRIMES: tuple[int, ...] = _sieve_of_eratosthenes(2048)


def is_probable_prime(n: int, k: int = 64) -> bool:
    """
    Probabilistyczny test pierwszości Millera-Rabina.
    Dla k = 64 rund prawdopodobieństwo uznania liczby złożonej za pierwszą wynosi <= 4^-64 = 2^-128.
    """
    if n < 2:
        return False

    # Szybka eliminacja przez małe dzielniki pierwsze
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False

    # Rozkład: n - 1 = d * 2^s przy nieparzystym d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # k niezależnych rund ze świadkami losowanymi kryptograficznie bezpiecznie
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2  # losowe a z przedziału [2, n - 2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def _is_perfect_power(n: int) -> bool:
    """Sprawdza, czy n = a^b dla pewnych liczb całkowitych a >= 2 oraz b >= 2."""
    if n < 4:
        return False
    max_b = n.bit_length()
    for b in range(2, max_b + 1):
        low, high = 2, 1 << ((max_b // b) + 1)
        while low <= high:
            mid = (low + high) // 2
            val = pow(mid, b)
            if val == n:
                return True
            if val < n:
                low = mid + 1
            else:
                high = mid - 1
    return False


def _multiplicative_order(n: int, r: int) -> int:
    """Wyznacza rząd multiplikatywny n modulo r (najmniejsze k >= 1 takie, że n^k = 1 mod r)."""
    if math.gcd(n, r) != 1:
        return 0
    k = 1
    cur = n % r
    while cur != 1:
        cur = (cur * n) % r
        k += 1
        if k > r:
            return 0
    return k


def _euler_totient(r: int) -> int:
    """Oblicza wartość funkcji Eulera phi(r)."""
    res = r
    temp = r
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            res -= res // p
        p += 1
    if temp > 1:
        res -= res // temp
    return res


def _poly_mul_mod(a: list[int], b: list[int], r: int, n: int) -> list[int]:
    """Mnoży dwa wielomiany w pierścieniu ilorazowym Z_n[x] / (x^r - 1)."""
    res = [0] * r
    for i, coeff_a in enumerate(a):
        if coeff_a == 0:
            continue
        for j, coeff_b in enumerate(b):
            if coeff_b == 0:
                continue
            idx = (i + j) % r
            res[idx] = (res[idx] + coeff_a * coeff_b) % n
    return res


def _poly_pow_mod(base: list[int], exp: int, r: int, n: int) -> list[int]:
    """Szybkie potęgowanie binarne wielomianu w pierścieniu Z_n[x] / (x^r - 1)."""
    res = [0] * r
    res[0] = 1
    cur = base[:]
    e = exp
    while e > 0:
        if e & 1:
            res = _poly_mul_mod(res, cur, r, n)
        cur = _poly_mul_mod(cur, cur, r, n)
        e >>= 1
    return res


def is_prime_aks(n: int) -> bool:
    """
    Bezwarunkowo deterministyczny test pierwszości AKS (Agrawal-Kayal-Saxena).
    Złożoność czasowa O~(b^6) — służy do weryfikacji małych liczb (do ~14-16 bitów)
    oraz analizy porównawczej względem algorytmu Millera-Rabina.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Krok 1: Sprawdzenie, czy n jest potęgą doskonałą (n = a^b)
    if _is_perfect_power(n):
        return False

    # Krok 2: Wyznaczenie najmniejszego r takiego, że ord_r(n) > (log2(n))^2
    log2_n = math.log2(n)
    max_k = math.floor(log2_n ** 2)
    r = 2
    while True:
        if math.gcd(n, r) == 1 and _multiplicative_order(n, r) > max_k:
            break
        r += 1

    # Krok 3: Sprawdzenie nietrywialnych dzielników dla 2 <= a <= r
    for a in range(2, min(r + 1, n)):
        g = math.gcd(a, n)
        if 1 < g < n:
            return False

    # Krok 4: Jeśli n <= r, liczba jest pierwsza
    if n <= r:
        return True

    # Krok 5: Kongruencje wielomianowe (x + a)^n == x^n + a (mod x^r - 1, n)
    limit = math.floor(math.sqrt(_euler_totient(r)) * log2_n)
    x_n_mod_r = n % r

    for a in range(1, limit + 1):
        poly_base = [0] * r
        poly_base[0] = a % n
        poly_base[1 % r] = (poly_base[1 % r] + 1) % n

        lhs = _poly_pow_mod(poly_base, n, r, n)

        rhs = [0] * r
        rhs[0] = a % n
        rhs[x_n_mod_r] = (rhs[x_n_mod_r] + 1) % n

        if lhs != rhs:
            return False

    return True


def generate_prime_with_stats(bits: int, k: int = 64) -> tuple[int, dict[str, int]]:
    """
    Generuje losową liczbę pierwszą o dokładnej długości `bits` bitów za pomocą `secrets`.
    Zwraca krotkę (liczba_pierwsza, statystyki_odrzucania).
    """
    if bits < 8:
        raise ValueError("Długość bitowa liczby pierwszej musi wynosić co najmniej 8 bitów.")

    stats = {
        "candidates_drawn": 0,
        "rejected_by_sieve": 0,
        "rejected_by_mr": 0,
    }

    msb_mask = 1 << (bits - 1)

    while True:
        stats["candidates_drawn"] += 1
        # Wymuszenie dokładnej długości bitowej (MSB = 1) oraz nieparzystości (LSB = 1)
        candidate = secrets.randbits(bits) | msb_mask | 1

        # Etap 1 filtracji: sito małych liczb pierwszych
        divisible = False
        for p in SMALL_PRIMES:
            if candidate == p:
                return candidate, stats
            if candidate % p == 0:
                divisible = True
                break

        if divisible:
            stats["rejected_by_sieve"] += 1
            continue

        # Etap 2 filtracji: test Millera-Rabina
        if is_probable_prime(candidate, k=k):
            return candidate, stats

        stats["rejected_by_mr"] += 1


def generate_prime(bits: int, k: int = 64) -> int:
    """Generuje kryptograficznie bezpieczną liczbę pierwszą o długości `bits` bitów."""
    prime, _ = generate_prime_with_stats(bits=bits, k=k)
    return prime


def generate_rsa_prime_pair(key_bits: int, e: int = 65537, k: int = 64) -> tuple[int, int]:
    """
    Generuje parę distinct liczb pierwszych (p, q) po `key_bits // 2` bitów każda,
    takich że gcd(e, (p - 1)(q - 1)) == 1 oraz iloczyn p * q ma pełną długość `key_bits`.
    """
    if key_bits < 512 or key_bits % 2 != 0:
        raise ValueError("Długość klucza RSA musi być liczbą parzystą >= 512 bitów.")

    half_bits = key_bits // 2
    while True:
        p = generate_prime(half_bits, k=k)
        if (p - 1) % e == 0:
            continue

        q = generate_prime(half_bits, k=k)
        if p == q or (q - 1) % e == 0:
            continue

        if (p * q).bit_length() == key_bits:
            return p, q