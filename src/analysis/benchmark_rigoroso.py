#!/usr/bin/env python3
"""
Benchmark Rigoroso - 5 repetições para média ± desvio padrão
Metodologia HPC adequada para trabalho acadêmico
"""
import numpy as np
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import statistics

CIDADES_COUNT = 18

def worker_tarefa(args):
    seed, n_cidades = args
    np.random.seed(seed)
    rota = np.random.permutation(n_cidades)
    return seed, len(rota)

def benchmark_rigoroso():
    cpus = mp.cpu_count()
    CHUNKSIZE = 1000
    N_REPETICOES = 5
    
    print("="*80)
    print(" 📊 BENCHMARK RIGOROSO - HPC Methodology ".center(80))
    print(f" CPUs: {cpus} | Chunk: {CHUNKSIZE} | Repetições: {N_REPETICOES} ".center(80))
    print("="*80 + "\n")
    
    print(f"| Iterações | Serial (s)      | Paralelo (s)    | Speedup | Eficiência |")
    print(f"|-----------|-----------------|-----------------|---------|-----------|")
    
    for n_iter in [1000, 10000, 50000, 100000, 200000]:
        temps_serial = []
        temps_paralelo = []
        
        for _ in range(N_REPETICOES):
            args = [(s, CIDADES_COUNT) for s in range(n_iter)]
            
            # Serial
            start = time.time()
            [worker_tarefa(a) for a in args]
            temps_serial.append(time.time() - start)
            
            # Paralelo
            start = time.time()
            with ProcessPoolExecutor(max_workers=cpus) as executor:
                list(executor.map(worker_tarefa, args, chunksize=CHUNKSIZE))
            temps_paralelo.append(time.time() - start)
        
        # Média ± desvio
        mean_s = statistics.mean(temps_serial)
        std_s = statistics.stdev(temps_serial)
        mean_p = statistics.mean(temps_paralelo)
        std_p = statistics.stdev(temps_paralelo)
        speedup = mean_s / mean_p
        eficiencia = (speedup / cpus) * 100
        
        print(f"| {n_iter:>8,} | {mean_s:>6.4f}±{std_s*1000:>4.1f}ms | {mean_p:>6.4f}±{std_p*1000:>4.1f}ms | {speedup:>6.2f}x | {eficiencia:>7.1f}% |")
    
    print("="*80)

if __name__ == "__main__":
    benchmark_rigoroso()