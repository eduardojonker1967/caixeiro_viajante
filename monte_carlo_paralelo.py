#!/usr/bin/env python3
"""
Monte Carlo PARALELO - Versão com ProcessPoolExecutor para comparação
Execute este arquivo para obter o tempo paralelo
"""

import numpy as np
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

def monte_carlo_worker(args):
    """
    Worker para ProcessPoolExecutor - processa um subset de iterações
    """
    iteracoes_worker, cidades_rota, total_cidades = args
    
    custo_atual = np.random.uniform(500, 800, iteracoes_worker)
    fator_cidades = cidades_rota / total_cidades
    economia_rota = np.random.uniform(0.20, 0.35, iteracoes_worker)
    custo_modelo = custo_atual * fator_cidades * (1 - economia_rota)
    
    return {
        'atual': custo_atual.mean(),
        'modelo': custo_modelo.mean(),
        'count': iteracoes_worker
    }

def simular_testes_monte_carlo_paralelo(iteracoes=1000000, cidades_rota=14, total_cidades=18):
    """
    Versão PARALELA - divide as iterações entre processos
    """
    print(f"🎲 Iniciando Simulação Monte Carlo PARALELA com {iteracoes:,} iterações...")
    
    start = time.time()
    num_workers = multiprocessing.cpu_count()
    
    # Divide iterações entre workers
    iteracoes_por_worker = iteracoes // num_workers
    
    args_list = [(iteracoes_por_worker, cidades_rota, total_cidades) for _ in range(num_workers)]
    
    # Processa em paralelo
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        resultados = list(executor.map(monte_carlo_worker, args_list))
    
    duration = time.time() - start
    
    # Combina resultados (média ponderada)
    total_count = sum(r['count'] for r in resultados)
    custo_atual = sum(r['atual'] * r['count'] for r in resultados) / total_count
    custo_modelo = sum(r['modelo'] * r['count'] for r in resultados) / total_count
    economia = ((1 - custo_modelo / custo_atual) * 100)
    
    print(f"Média Custo Atual: {custo_atual:.2f}")
    print(f"Média Custo Modelo: {custo_modelo:.2f}")
    print(f"Economia Gerada: {economia:.2f}%")
    print(f"⏱️  Tempo PARALELO: {duration:.4f}s ({num_workers} workers)")
    
    return {
        'atual': custo_atual,
        'modelo': custo_modelo,
        'economia': economia,
        'tempo': duration
    }

if __name__ == "__main__":
    from monte_carlo_serial import simular_testes_monte_carlo_serial, simular_testes_monte_carlo_vetorizado
    
    iteracoes = 1000000
    
    print("="*60)
    print("  COMPARAÇÃO SERIAL vs PARALELO ".center(60))
    print("="*60 + "\n")
    
    # Versão serial (loop explícito) - COMENTADO para não demorar
    # serial = simular_testes_monte_carlo_serial(iteracoes)
    
    # Versão vetorizada (atual)
    vetorizado = simular_testes_monte_carlo_vetorizado(iteracoes)
    
    # Versão paralela
    paralelo = simular_testes_monte_carlo_paralelo(iteracoes)
    
    speedup = vetorizado['tempo'] / paralelo['tempo']
    
    print("\n" + "="*60)
    print("  RESULTADO DA COMPARAÇÃO ".center(60))
    print("="*60)
    print(f"Vetorizado (NumPy): {vetorizado['tempo']:.4f}s")
    print(f"Paralelo:           {paralelo['tempo']:.4f}s")
    print(f"Speedup paralelo:   {speedup:.2f}x")
    print("="*60)