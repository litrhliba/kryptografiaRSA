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

1) gcd, tożsamość Bézouta, odwrotność, potęgowanie. Mikrobenchmark algorytmów potęgowania, CPU/pamięć operacji na dużych liczbach - 5.11

2) Liczby Carmichaela, znane liczby pierwsze, długość bitowa	Czas generowania per bit, obciążenie wątku CPU podczas prób losowaniaLiczby Carmichaela, znane liczby pierwsze, długość bitowa	Czas generowania per bit, obciążenie wątku CPU podczas prób losowania - 19.11

3) Konwersja bajtowa, round-trip encrypt-decrypt, granica >=n. Asymetria czasowa szyfrowania (e) vs deszyfrowania (d), alokacje pamięci. - 3.12

4) Poprawność deszyfrowania CRT, weryfikacja ataku homomorficznego	Zysk wydajnościowy CRT (~4x), profilowanie całego procesu (cProfile, tracemalloc) -17.12

Wyniki benchmarku algorytmow potegowania:   
<img width="477" height="283" alt="image" src="https://github.com/user-attachments/assets/69b28303-dd37-47e6-8925-6c8fdd212a0f" />
<img width="477" height="283" alt="image" src="https://github.com/user-attachments/assets/78ff4d3e-459a-40c6-9bc6-3fd05c50ce43" />
