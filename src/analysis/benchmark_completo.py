#!/usr/bin/env python3
"""
Script de Benchmark Completo - Serial vs Paralelo
Gera todas as métricas e comparações necessárias para o trabalho acadêmico
"""

import subprocess
import sys
import time
import os
import multiprocessing
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_benchmark():
    print("\n" + "="*70)
    print(" 🚀 BENCHMARK COMPLETO SERIAL vs PARALELO ".center(70, "="))
    print(f"   Iniciado: {get_timestamp()} ".center(70))
    print("="*70 + "\n")
    
    cpus = multiprocessing.cpu_count()
    
    # 1. TSP Solver - Serial (arquivo original)
    print("📊 1. TSP SOLVER - VERSÃO SERIAL")
    print("-" * 50)
    print(f"   CPUs detectadas: {cpus}")
    
    start = time.time()
    subprocess.run([sys.executable, "tsp_solver.py"], capture_output=True, text=True)
    serial_time = time.time() - start
    
    print(f"   ⏱️  Tempo Serial TSP:    {serial_time:.4f}s")
    
    # 2. TSP Solver - Paralelo
    print("\n📊 2. TSP SOLVER - VERSÃO PARALELA")
    print("-" * 50)
    
    start = time.time()
    subprocess.run([sys.executable, "tsp_solver_paralelo.py"], capture_output=True, text=True)
    paralelo_time = time.time() - start
    
    speedup_tsp = serial_time / paralelo_time if paralelo_time > 0 else 0
    eficiencia_tsp = (speedup_tsp / cpus) * 100 if speedup_tsp > 0 else 0
    
    print(f"   ⏱️  Tempo Paralelo TSP:  {paralelo_time:.4f}s")
    print(f"   📈 Speedup TSP:         {speedup_tsp:.2f}x")
    print(f"   📊 Eficiência:          {eficiencia_tsp:.1f}%")
    
    # 3. Pipeline completo
    print("\n📊 3. PIPELINE COMPLETO")
    print("-" * 50)
    
    start = time.time()
    subprocess.run([sys.executable, "pipeline_simples.py"], capture_output=True, text=True)
    pipeline_time = time.time() - start
    
    print(f"   ⏱️  Tempo Pipeline:      {pipeline_time:.4f}s")
    
    # 4. Monte Carlo Serial vs Vetorizado
    print("\n📊 4. MONTE CARLO - SERIAL vs VETORIZADO")
    print("-" * 50)
    
    # Serial
    start = time.time()
    subprocess.run([sys.executable, "-c", 
        "import numpy as np; import time; start=time.time(); "
        "[np.random.uniform(500, 800) for _ in range(100000)]; "
        "print(f'Serial MC: {time.time()-start:.4f}s')"],
        capture_output=True, text=True)
    
    # Vetorizado
    start = time.time()
    subprocess.run([sys.executable, "-c",
        "import numpy as np; import time; start=time.time(); "
        "np.random.uniform(500, 800, 100000); print(f'Vetorizado MC: {time.time()-start:.4f}s')"],
        capture_output=True, text=True)
    
    print("   Executado via subprocess")
    
    # Resumo final
    print("\n" + "="*70)
    print(" 📋 RESUMO DOS BENCHMARKS ".center(70, "="))
    print("="*70)
    print(f"| Métrica          | Valor       |")
    print(f"|------------------|-------------|")
    print(f"| CPUs             | {cpus}          |")
    print(f"| TSP Serial       | {serial_time:.4f}s     |")
    print(f"| TSP Paralelo     | {paralelo_time:.4f}s     |")
    print(f"| Speedup TSP      | {speedup_tsp:.2f}x         |")
    print(f"| Eficiência TSP   | {eficiencia_tsp:.1f}%       |")
    print(f"| Pipeline Total   | {pipeline_time:.4f}s     |")
    print("="*70)
    print(f"\n   Concluído: {get_timestamp()} ".center(70))
    print("="*70 + "\n")
    
    return {
        'cpus': cpus,
        'serial_time': serial_time,
        'paralelo_time': paralelo_time,
        'speedup': speedup_tsp,
        'eficiencia': eficiencia_tsp
    }

if __name__ == "__main__":
    run_benchmark()