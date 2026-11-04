

import sys
import time
import tracemalloc
import secrets
from math_utils import mod_pow_iterative, mod_pow_native, extended_gcd, mod_inverse, gcd


def generate_large_int(bits: int) -> int:
   
    return secrets.randbits(bits) | (1 << (bits - 1)) | 1


def profile_execution(func, *args):
    
    tracemalloc.start()
    t0 = time.perf_counter()
    
    result = func(*args)
    
    t1 = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    execution_time_ms = (t1 - t0) * 1000
    peak_mem_kb = peak_mem / 1024
    
    return result, execution_time_ms, peak_mem_kb


def run_benchmarks():
    print("=" * 70)
    print(" MIKROBENCHMARK ALGORYTMÓW NUMERYCZNYCH RSA (Python 3.10+)")
    print("=" * 70)
    
    for bit_size in [2048, 4096]:
        print(f"\n--- Testy dla rozmiaru klucza/argumentów: {bit_size} bitów ---")
        
        base = generate_large_int(bit_size)
        exp = generate_large_int(bit_size)
        mod = generate_large_int(bit_size)
        
        # Pamięć zajmowana przez pojedynczą liczbę w Pythonie
        int_bytes = sys.getsizeof(base)
        print(f"Rozmiar 1 liczby {bit_size}-bitowej w pamięci Pythona: {int_bytes} bajtów")
        
        # Test 1: Pow własny (Square-and-Multiply)
        _, t_custom, mem_custom = profile_execution(mod_pow_iterative, base, exp, mod)
        print(f" Potęgowanie iteracyjne (własne) : Czas: {t_custom:8.2f} ms | Szczytowa pamięć: {mem_custom:7.2f} KB")
        
        # Test 2: Pow natywny (C-Level optimization)
        _, t_native, mem_native = profile_execution(mod_pow_native, base, exp, mod)
        print(f" Potęgowanie natywne (pow(b,e,m)) : Czas: {t_native:8.2f} ms | Szczytowa pamięć: {mem_native:7.2f} KB")
        
        # Test 3: Rozszerzony Euklides
        _, t_egcd, mem_egcd = profile_execution(extended_gcd, base, mod)
        print(f" Tożsamość Bézouta (ext_gcd)      : Czas: {t_egcd:8.2f} ms | Szczytowa pamięć: {mem_egcd:7.2f} KB")

if __name__ == "__main__":
    run_benchmarks()
