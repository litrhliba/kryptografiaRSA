
import math
import unittest
from primes import (
    generate_prime,
    generate_rsa_prime_pair,
    is_prime_aks,
    is_probable_prime,
)


def _fermat_naive_test(n: int) -> bool:
    """Naiwny test Fermata dla podstaw względnie pierwszych z n (podatny na liczby Carmichaela)."""
    for a in (2, 3, 5, 7, 11, 13):
        if math.gcd(a, n) == 1 and pow(a, n - 1, n) != 1:
            return False
    return True


class TestPrimesModule(unittest.TestCase):
    def test_carmichael_numbers_rejected(self):
        """Weryfikacja, że test Millera-Rabina odrzuca liczby Carmichaela."""
        carmichael_numbers = [
            561, 1105, 1729, 2465, 2821, 6601, 8911, 10585,
            15841, 29341, 41041, 46657, 52633, 62745, 63973, 75361,
        ]
        for c in carmichael_numbers:
            # Naiwny test Fermata daje wynik fałszywie dodatni (True)
            self.assertTrue(_fermat_naive_test(c), f"Test Fermata powinien zostać oszukany przez {c}")
            # Miller-Rabin musi wykryć złożoność (False)
            self.assertFalse(is_probable_prime(c, k=64), f"Miller-Rabin błędnie zaakceptował liczbę Carmichaela {c}")

    def test_large_chernick_carmichael_number(self):
        """
        Test na dużej liczbie Carmichaela konstrukcji Chernicka: U_3(m) = (6m+1)(12m+1)(18m+1),
        gdzie wszystkie trzy czynniki są liczbami pierwszymi (dla m = 100000180).
        """
        m = 100_000_180
        p1, p2, p3 = 6 * m + 1, 12 * m + 1, 18 * m + 1
        assert is_probable_prime(p1) and is_probable_prime(p2) and is_probable_prime(p3)
        big_carmichael = p1 * p2 * p3  # liczba złożona > 2^90 spełniająca a^(n-1) = 1 (mod n)

        self.assertTrue(_fermat_naive_test(big_carmichael))
        self.assertFalse(is_probable_prime(big_carmichael, k=64))

    def test_known_mersenne_primes(self):
        """Weryfikacja rozpoznawania znanych dużych liczb pierwszych Mersenne'a M_p = 2^p - 1."""
        mersenne_exponents = [13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279]
        for exp in mersenne_exponents:
            mp = (1 << exp) - 1
            self.assertTrue(is_probable_prime(mp, k=64), f"Nie rozpoznano liczby pierwszej Mersenne'a M_{exp}")

    def test_exact_bit_length_generation(self):
        """Sprawdzenie, czy wygenerowane liczby pierwsze mają dokładnie żądaną długość bitową."""
        for bits in (512, 1024):
            p = generate_prime(bits, k=64)
            self.assertEqual(p.bit_length(), bits)
            self.assertEqual(p & 1, 1)  # musi być nieparzysta
            self.assertTrue(is_probable_prime(p, k=64))

    def test_rsa_prime_pair(self):
        """Weryfikacja poprawności pary czynników (p, q) dla klucza RSA-1024."""
        p, q = generate_rsa_prime_pair(1024, e=65537)
        self.assertNotEqual(p, q)
        self.assertEqual((p * q).bit_length(), 1024)
        self.assertEqual(math.gcd(65537, (p - 1) * (q - 1)), 1)

    def test_aks_vs_miller_rabin_equivalence(self):
        """Porównanie deterministycznego testu AKS z testem Millera-Rabina na przedziale [2, 300] oraz dla 561."""
        for n in range(2, 301):
            self.assertEqual(
                is_prime_aks(n),
                is_probable_prime(n, k=32),
                f"Rozbieżność między AKS a Millerem-Rabinem dla n = {n}",
            )
        self.assertFalse(is_prime_aks(561))
        self.assertFalse(is_prime_aks(1105))


if __name__ == "__main__":
    unittest.main(verbosity=2)