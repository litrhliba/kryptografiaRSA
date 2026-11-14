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

## Harmonogram prac i kamienie milowe

### Przegląd etapów

| Etap | Termin | Moduły | Główny cel | Zakres pomiarów i profilowania | Status |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **1** | **05.11** | `math_utils.py` | Fundamenty arytmetyczne RSA | Mikrobenchmark potęgowania, narzut CPU i RAM (`sys.getsizeof`, `tracemalloc`) | ✅ Zrealizowano |
| **2** | **19.11** | `primes.py` | Generowanie liczb pierwszych i testy pierwszości | Czas generowania (`ms/bit`), obciążenie jednowątkowego CPU, zestawienie Miller-Rabin vs. AKS | ⏳ W trakcie |
| **3** | **03.12** | `encoding.py`<br>`rsa_core.py` | Serializacja PKCS#1, szyfrowanie, deszyfrowanie i CRT | Asymetria czasowa $e$ vs. $d$, zysk wydajnościowy CRT (~4x), alokacje pamięci | 📅 Planowany |
| **4** | **17.12** | `rsa_core.py`<br>`tests/` | Analiza podatności kryptograficznych i optymalizacja | Weryfikacja ataku homomorficznego, całościowe profilowanie (`cProfile`, `tracemalloc`) | 📅 Planowany |

---

### Szczegółowy zakres prac

#### Etap 1: Fundamenty numeryczne i mikrobenchmarki (`05.11`)
- [x] Implementacja klasycznego algorytmu Euklidesa (`gcd`) oraz iteracyjnego rozszerzonego algorytmu Euklidesa (tożsamość Bézouta: $ax + by = \gcd(a, b)$).
- [x] Wyznaczanie odwrotności modularnej ($d \equiv e^{-1} \pmod{\varphi(n)}$).
- [x] Implementacja szybkiego potęgowania modularnego metodą binarną (*Square-and-Multiply*).
- [x] **Benchmarking:** Porównanie autorskiego potęgowania z wbudowaną funkcją `pow(b, e, m)` oraz pomiar zużycia pamięci (`tracemalloc`, `sys.getsizeof`) dla liczb 2048- i 4096-bitowych.

#### Etap 2: Generowanie liczb pierwszych i testy pierwszości (`19.11`)
- [ ] Kryptograficznie bezpieczne losowanie kandydatów przy użyciu `secrets.randbits()` z wymuszeniem dokładnej długości bitowej (MSB = 1) oraz nieparzystości (LSB = 1).
- [ ] Wstępna eliminacja liczb złożonych za pomocą sita małych liczb pierwszych.
- [ ] Implementacja probabilistycznego testu pierwszości Millera-Rabina ($k = 64$ rundy, prawdopodobieństwo błędu $\le 2^{-128}$).
- [ ] Weryfikacja poprawności na zbiorze znanych liczb pierwszych oraz **liczbach Carmichaela** ($561, 1105, 1729$) jako przypadkach brzegowych.
- [ ] Analiza porównawcza probabilistycznego algorytmu **Millera-Rabina** z deterministycznym algorytmem **AKS (Agrawal–Kayal–Saxena)**.
- [ ] **Benchmarking:** Pomiar średniego czasu generowania w przeliczeniu na bit (`ms/bit`), analiza obciążenia jednowątkowego CPU podczas odrzucania kandydatów oraz zestawienie złożoności czasowej i pamięciowej Miller-Rabin vs. AKS.

#### Etap 3: Serializacja, szyfrowanie, deszyfrowanie i CRT (`03.12`)
- [ ] Implementacja konwersji bajtowej zgodnej z RFC 8017 (`OS2IP` oraz `I2OSP` w formacie *big-endian*).
- [ ] Egzekwowanie warunku brzegowego $0 \le m < n$ (odrzucanie wiadomości spełniających $m \ge n$ w celu uniknięcia utraty informacji modulo $n$).
- [ ] Generowanie par kluczy z prekomputacją parametrów dla **Chińskiego Twierdzenia o Resztach (CRT)**: $d_p = d \bmod (p - 1)$, $d_q = d \bmod (q - 1)$ oraz $q_{\text{inv}} = q^{-1} \bmod p$.
- [ ] Weryfikacja pełnego cyklu *round-trip* (`encrypt` $\to$ `decrypt` klasyczne oraz `decrypt_crt` metodą Garnera).
- [ ] **Benchmarking:** Pomiar asymetrii czasowej między szybkim szyfrowaniem ($e = 65537$) a deszyfrowaniem ($d$), weryfikacja przyspieszenia dzięki CRT (~4x) oraz analiza alokacji pamięci RAM.

#### Etap 4: Analiza bezpieczeństwa i profilowanie końcowe (`17.12`)
- [ ] Praktyczna demonstracja **ataku homomorficznego** na podręcznikowe RSA: $E(m_1) \cdot E(m_2) \equiv E(m_1 \cdot m_2) \pmod n$.
- [ ] Analiza porównawcza surowego RSA względem schematów dopełniania (paddingu PKCS#1 v1.5 / OAEP ze standardu RFC 8017).
- [ ] **Benchmarking:** Kompleksowe profilowanie całego potoku wykonania (generowanie kluczy $\to$ kodowanie $\to$ szyfrowanie $\to$ deszyfrowanie CRT) za pomocą `cProfile` oraz `tracemalloc`.

Wyniki benchmarku algorytmow potegowania:   
<img width="477" height="283" alt="image" src="https://github.com/user-attachments/assets/69b28303-dd37-47e6-8925-6c8fdd212a0f" />
<img width="477" height="283" alt="image" src="https://github.com/user-attachments/assets/78ff4d3e-459a-40c6-9bc6-3fd05c50ce43" />
