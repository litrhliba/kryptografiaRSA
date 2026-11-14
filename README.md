# kryptografiaRSA
Koncepcja:

-Podręcznikowe RSA w Pythonie. 

-Kodowanie, szyfrowanie, deszyfrowanie, generowanie par kluczy, generator losowych liczb pierwszych, test Millera-Rabina, NWD, rozszerzony Euklides z potęgowaniem modularnym.

-Moduły składowe: math_utils.py (Fundamenty numeryczne), primes.py (Generowanie liczb pierwszych), encoding.py (Serializacja i konwersja danych), rsa_core.py (Operacje rdzenne). 

-Środowisko Python 3.10+. Użycie wyłącznie secrets i random bits. Wykorzystanie natywnego typu int - obluga liczb dowolnej dlugosci. 

-Standard: PKCS#1 (RFC 8017)

Skład grupy:

-Rutyna Oleksandr (programowanie, analiza problemów, arytmetyka, algebra)

-Miazek Wojciech (programowanie, analiza problemów, arytmetyka, algebra)

Harmonogram:

1) gcd, tożsamość Bézouta - Implementacja klasycznego algorytmu Euklidesa (gcd) oraz iteracyjnego rozszerzonego algorytmu Euklidesa wyznaczającego współczynniki tożsamości Bézouta ($ax + by = \gcd(a, b)$) bez ryzyka przekroczenia limitu stosu rekurencji.
   odwrotność - Wyznaczanie odwrotności modularnej ($d \equiv e^{-1} \pmod{\varphi(n)}$), kluczowej przy obliczaniu wykładnika prywatnego.
   potęgowanie - Implementacja szybkiego potęgowania modularnego metodą binarną (Square-and-Multiply) o złożoności $O(\log e)$.
   Mikrobenchmark algorytmów potęgowania, CPU/pamięć operacji na dużych liczbach - Mikrobenchmark porównujący autorską pętlę potęgowania z wbudowaną w CPython funkcję pow(b, e, m) (algorytm Sliding Window). Analiza narzutu pamięciowego (sys.getsizeof, tracemalloc) obiektów typu int (alokacja w 30-bitowych blokach limbs) oraz skalowania czasu CPU dla liczb 2048- i 4096-bitowych.

3) Liczby Carmichaela, znane liczby pierwsze, długość bitowa	Czas generowania per bit, obciążenie wątku CPU podczas prób losowania - 19.11

4) Konwersja bajtowa, round-trip encrypt-decrypt, granica >=n. Asymetria czasowa szyfrowania (e) vs deszyfrowania (d), alokacje pamięci. - 3.12

5) Poprawność deszyfrowania CRT, weryfikacja ataku homomorficznego	Zysk wydajnościowy CRT (~4x), profilowanie całego procesu (cProfile, tracemalloc) -17.12

Wyniki benchmarku algorytmow potegowania:   
<img width="477" height="283" alt="image" src="https://github.com/user-attachments/assets/69b28303-dd37-47e6-8925-6c8fdd212a0f" />
<img width="477" height="283" alt="image" src="https://github.com/user-attachments/assets/78ff4d3e-459a-40c6-9bc6-3fd05c50ce43" />
