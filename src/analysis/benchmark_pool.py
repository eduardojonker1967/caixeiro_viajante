#!/usr/bin/env python3
"""
Benchmark otimizado usando multiprocessing.Pool com spawn único
"""
import numpy as np
import time
import multiprocessing as mp
import ctypes

def worker_starmap(args):
    seed, n_cidades = args
    np.random.seed(seed)
    rota = np.random.permutation(n_cidades)
    dist = rota.sum()  # dummy - seria haversine real
    return seed, dist

def benchmark_pool():
    cpus = mp.cpu_count()
    
    print("="*70)
    print(" 📊 BENCHMARK multiprocessing.Pool (start method: fork) ".center(70))
    print("="*70)
    
    mp.set_start_method('fork', force=True)
    
    for n_iter in [10000, 50000, 100000, 200000]:
        args = [(s, CIDADES_COUNT) for s in range(n_iter)]
        
        # Serial
        start = time.time()
        serial_res = [worker_starmap(a) for a in args]
        t_serial = time.time() - start
        
        # Pool (mais eficiente que ProcessPoolExecutor)
        start = time.time()
        with mp.Pool(processes=cpus) as pool:
            paralelo_res = pool.map(worker_starmap, args, chunksize=max(100, n_iter//(cpus*5)))
        t_paralelo = time.time() - start
        
        speedup = t_serial / t_paralelo
        eficiencia = (speedup / cpus) * 100
        
        print(f"{n_iter:>7,} iterações | Serial: {t_serial:>6.3f}s | Pool: {t_paralelo:>6.3f}s | Speedup: {speedup:>5.2f}x | Eficiência: {eficiencia:>5.1f}%")
    
    print("="*70)

CIDADES_COUNT = 18

if __name__ == "__main__":
    benchmark_pool()