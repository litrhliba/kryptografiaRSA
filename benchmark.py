"""
benchmark_multi.py - Wielokrotny mikrobenchmark CPU i RAM dla RSA (N = 30 prób)
Autorzy: Oleksandr Rutyna, Wojciech Miazek
"""

import csv
import gc
import math
import secrets
import statistics
import sys
import time
import tracemalloc
from math_utils import mod_pow_iterative, mod_pow_native, extended_gcd

WARMUP_RUNS = 3
BENCHMARK_RUNS = 30

# Krytyczne wartości rozkładu t-Studenta (dwustronne, alpha = 0.05 -> 95% przedział ufności)
T_CRITICAL_95 = {
    5: 2.776445,
    10: 2.262157,
    15: 2.144787,
    20: 2.093024,
    25: 2.063899,
    30: 2.045230,
    50: 2.009575,
    100: 1.984217,
}


def generate_large_int(bits: int) -> int:
    """Generuje losową liczbę nieparzystą o dokładnej długości `bits` bitów."""
    return secrets.randbits(bits) | (1 << (bits - 1)) | 1


def compute_stats(samples: list[float]) -> dict[str, float]:
    """Oblicza średnią, odchylenie standardowe z próby (s) oraz 95% przedział ufności."""
    n = len(samples)
    mean_val = statistics.mean(samples)
    stdev_val = statistics.stdev(samples)  # mianownik (n - 1), zgodny z ODCH.STAND.PRÓBKI
    t_crit = T_CRITICAL_95.get(n, 1.959964)
    margin_of_error = t_crit * (stdev_val / math.sqrt(n))
    return {
        "mean": mean_val,
        "stdev": stdev_val,
        "me": margin_of_error,
        "ci_low": mean_val - margin_of_error,
        "ci_high": mean_val + margin_of_error,
    }


def measure_cpu_series(func, datasets: list[tuple[int, ...]]) -> list[float]:
    """Wykonuje rundy rozgrzewkowe, a następnie mierzy czysty czas CPU (bez narzutu tracemalloc)."""
    for args in datasets[:WARMUP_RUNS]:
        func(*args)

    times_ms = []
    gc.collect()
    for args in datasets:
        t0 = time.perf_counter()
        func(*args)
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000.0)
    return times_ms


def measure_peak_ram_kb(func, args: tuple[int, ...]) -> float:
    """Mierzy szczytową alokację pamięci RAM w KB w izolowanym przebiegu."""
    gc.collect()
    tracemalloc.start()
    func(*args)
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak_mem / 1024.0


def run_multi_benchmark():
    print("=" * 88)
    print(f" WIELOKROTNY MIKROBENCHMARK RSA (N = {BENCHMARK_RUNS} prób, warm-up = {WARMUP_RUNS})")
    print("=" * 88)

    csv_rows = []

    for bit_size in [2048, 4096]:
        print(f"\n--- Rozmiar klucza/argumentów: {bit_size} bitów ---")

        # Wspólny zestaw N zestawów wejściowych dla wszystkich algorytmów
        datasets = [
            (generate_large_int(bit_size), generate_large_int(bit_size), generate_large_int(bit_size))
            for _ in range(BENCHMARK_RUNS)
        ]
        egcd_datasets = [(b, m) for b, _, m in datasets]

        int_bytes = sys.getsizeof(datasets[0][0])
        print(f"Rozmiar 1 liczby {bit_size}-bitowej w pamięci Pythona: {int_bytes} bajtów\n")

        # 1. Pomiary czasu CPU (N prób)
        t_iter = measure_cpu_series(mod_pow_iterative, datasets)
        t_nat = measure_cpu_series(mod_pow_native, datasets)
        t_egcd = measure_cpu_series(extended_gcd, egcd_datasets)

        # 2. Izolowane pomiary szczytowej pamięci RAM
        ram_iter = measure_peak_ram_kb(mod_pow_iterative, datasets[0])
        ram_nat = measure_peak_ram_kb(mod_pow_native, datasets[0])
        ram_egcd = measure_peak_ram_kb(extended_gcd, egcd_datasets[0])

        results = [
            ("Potęgowanie iteracyjne (własne)", compute_stats(t_iter), ram_iter),
            ("Potęgowanie natywne pow(b,e,m)", compute_stats(t_nat), ram_nat),
            ("Tożsamość Bézouta (ext_gcd)", compute_stats(t_egcd), ram_egcd),
        ]

        for name, st, ram in results:
            print(
                f" {name:<32} | Średnia: {st['mean']:7.2f} ms ± {st['me']:5.2f} ms "
                f"(95% CI: [{st['ci_low']:6.2f}; {st['ci_high']:6.2f}]) | "
                f"SD: {st['stdev']:5.2f} ms | RAM: {ram:5.2f} KB"
            )

        for i in range(BENCHMARK_RUNS):
            csv_rows.append([
                i + 1,
                bit_size,
                f"{t_iter[i]:.4f}".replace(".", ","),
                f"{t_nat[i]:.4f}".replace(".", ","),
                f"{t_egcd[i]:.4f}".replace(".", ","),
            ])

    # Eksport z separatorem ';' i przecinkiem dziesiętnym (natywny format polskiego Excela)
    csv_filename = "benchmark_results.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Proba", "Bity", "Pow_Iteracyjne_ms", "Pow_Natywne_ms", "Ext_GCD_ms"])
        writer.writerows(csv_rows)

    print(f"\nSurowe dane ({len(csv_rows)} wierszy) zapisano do pliku: {csv_filename}")


if __name__ == "__main__":
    run_multi_benchmark()