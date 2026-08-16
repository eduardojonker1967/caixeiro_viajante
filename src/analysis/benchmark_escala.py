#!/usr/bin/env python3
"""
TSP Solver - Benchmark com diferentes escalas
Demonstração clara de speedup paralelo
"""
import numpy as np
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

CIDADES_COUNT = 18

def generate_random_route_worker(args):
    """Worker otimizado"""
    seed, n_cidades = args
    np.random.seed(seed)
    rota = np.random.permutation(n_cidades)
    return seed, len(rota)  # distância dummy para benchmark

def benchmark_escala():
    cpus = multiprocessing.cpu_count()
    
    print("="*70)
    print(" 📊 BENCHMARK DE PARALELISMO - ESCALA DE ITERAÇÕES ".center(70))
    print("="*70)
    print(f"CPUs: {cpus} | Cidades: {CIDADES_COUNT}\n")
    
    for n_iter in [1000, 10000, 100000, 500000]:
        # Serial
        start = time.time()
        resultados_serial = [generate_random_route_worker((s, CIDADES_COUNT)) for s in range(n_iter)]
        t_serial = time.time() - start
        
        # Paralelo
        start = time.time()
        with ProcessPoolExecutor(max_workers=cpus) as executor:
            args = [(s, CIDADES_COUNT) for s in range(n_iter)]
            resultados_paralelo = list(executor.map(generate_random_route_worker, args, chunksize=1000))
        t_paralelo = time.time() - start
        
        speedup = t_serial / t_paralelo if t_paralelo > 0 else 0
        eficiencia = (speedup / cpus) * 100
        
        print(f"{n_iter:>8,} iterações | Serial: {t_serial:>6.3f}s | Paralelo: {t_paralelo:>6.3f}s | Speedup: {speedup:>5.2f}x | Eficiência: {eficiencia:>5.1f}%")
    
    print("="*70)

if __name__ == "__main__":
    benchmark_escala()