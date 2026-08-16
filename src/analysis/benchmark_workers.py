#!/usr/bin/env python3
"""
Benchmark Serial vs Paralelo com diferentes números de workers (p=2, p=4)
"""
import numpy as np
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

CIDADES_COUNT = 18

def worker_tarefa(args):
    seed, n_cidades = args
    np.random.seed(seed)
    rota = np.random.permutation(n_cidades)
    return seed, len(rota)

def benchmark_workers_p():
    cpus = multiprocessing.cpu_count()
    n_iteracoes = 100000
    
    print("="*70)
    print(" 📊 SERIAL vs PARALELO (p=2, p=4, p=8, p=12) ".center(70))
    print("="*70)
    print(f"Iterações: {n_iteracoes:,} | Cidades: {CIDADES_COUNT}\n")
    
    # Serial (baseline)
    start = time.time()
    resultados_serial = [worker_tarefa((s, CIDADES_COUNT)) for s in range(n_iteracoes)]
    t_serial = time.time() - start
    print(f"Serial (1 worker): {t_serial:.3f}s\n")
    
    for p in [2, 4, 8, 12]:
        start = time.time()
        with ProcessPoolExecutor(max_workers=p) as executor:
            args = [(s, CIDADES_COUNT) for s in range(n_iteracoes)]
            chunksize = max(100, n_iteracoes // (p * 10))
            resultados_paralelo = list(executor.map(worker_tarefa, args, chunksize=chunksize))
        t_paralelo = time.time() - start
        
        speedup = t_serial / t_paralelo
        eficiencia = (speedup / p) * 100
        
        print(f"p={p:<2} workers | Tempo: {t_paralelo:>6.3f}s | Speedup: {speedup:>5.2f}x | Eficiência: {eficiencia:>5.1f}%")
    
    print("="*70)

if __name__ == "__main__":
    benchmark_workers_p()