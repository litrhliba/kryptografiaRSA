"""
benchmark_stage2.py - Mikrobenchmarki Etapu 2 z jednakową liczbą prób N dla każdej długości
Autorzy: Oleksandr Rutyna, Wojciech Miazek
"""

import csv
import gc
import math
import statistics
import time
import tracemalloc
from primes import (
    generate_prime_with_stats,
    is_prime_aks,
    is_probable_prime,
)

# Jednakowa liczba niezależnych pomiarów N dla każdej długości bitowej (512, 1024, 2048 bitów)
PRIME_GEN_RUNS = 20
MR_RUNS = 30
AKS_RUNS = 3

# Dwustronne wartości krytyczne rozkładu t-Studenta dla 95% przedziału ufności (alpha = 0.05)
T_CRITICAL_95 = {
    3: 4.302653,
    5: 2.776445,
    10: 2.262157,
    15: 2.144787,
    20: 2.093024,
    25: 2.063899,
    30: 2.045230,
    50: 2.009575,
}


def compute_ci(samples: list[float]) -> tuple[float, float, float]:
    """Zwraca krotkę (średnia, odchylenie_standardowe, margines_błędu_95_CI)."""
    n = len(samples)
    mean_val = statistics.mean(samples)
    sd = statistics.stdev(samples) if n > 1 else 0.0
    t_crit = T_CRITICAL_95.get(n, 2.093024)
    me = t_crit * (sd / math.sqrt(n))
    return mean_val, sd, me


def benchmark_prime_generation():
    print("=" * 92)
    print(f" CZĘŚĆ 1: BENCHMARK GENEROWANIA LICZB PIERWSZYCH (N = {PRIME_GEN_RUNS} prób dla każdej długości)")
    print("=" * 92)

    # Pary: (długość_czynnika_p_w_bitach, docelowy_klucz_RSA)
    configs = [
        (512, 1024),
        (1024, 2048),
        (2048, 4096),
    ]

    csv_rows = []

    for prime_bits, rsa_bits in configs:
        wall_times_ms = []
        cpu_times_ms = []
        ms_per_bit_list = []
        drawn_list = []
        sieve_rej_list = []
        mr_rej_list = []

        # Izolowany pomiar szczytowej alokacji pamięci RAM
        gc.collect()
        tracemalloc.start()
        generate_prime_with_stats(prime_bits, k=64)
        _, peak_ram = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_ram_kb = peak_ram / 1024.0

        print(f"\n--- Czynnik p = {prime_bits} bitów (Klucz RSA-{rsa_bits}, N = {PRIME_GEN_RUNS} prób) ---")

        for i in range(PRIME_GEN_RUNS):
            print(f"\r Trwa pomiar: próba {i + 1}/{PRIME_GEN_RUNS}...", end="", flush=True)
            gc.collect()
            t_wall_0 = time.perf_counter()
            t_cpu_0 = time.process_time()

            _, st = generate_prime_with_stats(prime_bits, k=64)

            t_cpu_1 = time.process_time()
            t_wall_1 = time.perf_counter()

            w_ms = (t_wall_1 - t_wall_0) * 1000.0
            c_ms = (t_cpu_1 - t_cpu_0) * 1000.0
            mpb = w_ms / prime_bits

            wall_times_ms.append(w_ms)
            cpu_times_ms.append(c_ms)
            ms_per_bit_list.append(mpb)
            drawn_list.append(st["candidates_drawn"])
            sieve_rej_list.append(st["rejected_by_sieve"])
            mr_rej_list.append(st["rejected_by_mr"])

            csv_rows.append([
                i + 1,
                rsa_bits,
                prime_bits,
                f"{w_ms:.4f}".replace(".", ","),
                f"{c_ms:.4f}".replace(".", ","),
                f"{mpb:.6f}".replace(".", ","),
                st["candidates_drawn"],
                st["rejected_by_sieve"],
                st["rejected_by_mr"],
            ])

        print("\r" + " " * 45 + "\r", end="")

        m_wall, sd_wall, me_wall = compute_ci(wall_times_ms)
        m_mpb, _, me_mpb = compute_ci(ms_per_bit_list)
        cpu_utilization = (sum(cpu_times_ms) / sum(wall_times_ms)) * 100.0
        avg_drawn = statistics.mean(drawn_list)
        avg_sieve = statistics.mean(sieve_rej_list)
        avg_mr = statistics.mean(mr_rej_list)
        sieve_pct = (avg_sieve / max(avg_drawn - 1, 1)) * 100.0

        print(f" Czas generowania (Wall) : {m_wall:8.2f} ms ± {me_wall:6.2f} ms (SD: {sd_wall:6.2f} ms)")
        print(f" Koszt na bit            : {m_mpb:8.4f} ms/bit ± {me_mpb:6.4f} ms/bit")
        print(f" Obciążenie wątku CPU    : {cpu_utilization:6.1f}% (czas CPU / czas rzeczywisty)")
        print(f" Kandydaci na 1 sukces   : śr. {avg_drawn:5.1f} (Sito odrzuciło: {avg_sieve:5.1f} [{sieve_pct:4.1f}%], MR: {avg_mr:4.1f})")
        print(f" Szczytowa pamięć RAM    : {peak_ram_kb:6.2f} KB")

    with open("benchmark_stage2_primes.csv", mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Proba", "Klucz_RSA_bity", "Czynnik_p_bity", "Wall_ms", "CPU_ms",
            "ms_na_bit", "Wylosowani_kandydaci", "Odrzuceni_sito", "Odrzuceni_MR",
        ])
        writer.writerows(csv_rows)


def benchmark_mr_vs_aks():
    print("\n" + "=" * 92)
    print(f" CZĘŚĆ 2: PORÓWNANIE MILLER-RABIN (N={MR_RUNS}) VS. DETERMINISTYCZNY AKS (N={AKS_RUNS})")
    print("=" * 92)

    test_primes = [
        (8, 131),
        (10, 521),
        (12, 2053),
        (13, 4099),
    ]

    csv_rows = []

    for bits, p_val in test_primes:
        gc.collect()
        tracemalloc.start()
        is_probable_prime(p_val, k=64)
        _, mr_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        mr_times = []
        for _ in range(MR_RUNS):
            t0 = time.perf_counter()
            assert is_probable_prime(p_val, k=64)
            mr_times.append((time.perf_counter() - t0) * 1000.0)
        mr_mean = statistics.mean(mr_times)

        gc.collect()
        tracemalloc.start()
        assert is_prime_aks(p_val)
        _, aks_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        aks_times = []
        for _ in range(AKS_RUNS):
            t0 = time.perf_counter()
            assert is_prime_aks(p_val)
            aks_times.append((time.perf_counter() - t0) * 1000.0)
        aks_mean = statistics.mean(aks_times)

        speedup = aks_mean / mr_mean
        print(
            f" {bits:2d} bitów (p={p_val:4d}) | "
            f"Miller-Rabin: {mr_mean:7.4f} ms ({mr_peak/1024:5.2f} KB) | "
            f"AKS: {aks_mean:9.2f} ms ({aks_peak/1024:5.2f} KB) | "
            f"AKS wolniejszy o: {speedup:,.0f}x"
        )

        csv_rows.append([
            bits,
            p_val,
            f"{mr_mean:.6f}".replace(".", ","),
            f"{mr_peak / 1024.0:.2f}".replace(".", ","),
            f"{aks_mean:.4f}".replace(".", ","),
            f"{aks_peak / 1024.0:.2f}".replace(".", ","),
            f"{speedup:.1f}".replace(".", ","),
        ])

    with open("benchmark_stage2_aks.csv", mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Bity", "Liczba_pierwsza", "MR_czas_ms", "MR_RAM_KB",
            "AKS_czas_ms", "AKS_RAM_KB", "Iloraz_AKS_do_MR",
        ])
        writer.writerows(csv_rows)

    print("\nWyniki zapisano do plików: benchmark_stage2_primes.csv oraz benchmark_stage2_aks.csv")


if __name__ == "__main__":
    benchmark_prime_generation()
    benchmark_mr_vs_aks()