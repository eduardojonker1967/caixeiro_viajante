#!/usr/bin/env python3
"""
Monte Carlo SERIAL - Versão sequencial para comparação com paralelo
Execute este arquivo para obter o tempo serial de referência
"""

import numpy as np
import time

def simular_testes_monte_carlo_serial(iteracoes=1000000, cidades_rota=18, total_cidades=18):
    """
    Versão SERIAL do Monte Carlo - loop explícito (para comparação)
    """
    print(f"🎲 Iniciando Simulação Monte Carlo SERIAL com {iteracoes:,} iterações...")
    
    start = time.time()
    
    custo_atual_list = []
    custo_modelo_list = []
    
    for _ in range(iteracoes):
        # Simulação de custo aleatório (Cenário Atual)
        custo_atual = np.random.uniform(500, 800)
        
        # Otimização 1: Redução por não visitar cidades de baixa prioridade
        fator_cidades = cidades_rota / total_cidades
        
        # Otimização 2: Eficiência do roteamento
        economia_rota = np.random.uniform(0.20, 0.35)
        
        # Custo modelo
        custo_modelo = custo_atual * fator_cidades * (1 - economia_rota)
        
        custo_atual_list.append(custo_atual)
        custo_modelo_list.append(custo_modelo)
    
    duration = time.time() - start
    
    custo_atual = np.mean(custo_atual_list)
    custo_modelo = np.mean(custo_modelo_list)
    economia = ((1 - custo_modelo / custo_atual) * 100)
    
    print(f"Média Custo Atual: {custo_atual:.2f}")
    print(f"Média Custo Modelo: {custo_modelo:.2f}")
    print(f"Economia Gerada: {economia:.2f}%")
    print(f"⏱️  Tempo SERIAL: {duration:.4f}s")
    
    return {
        'atual': custo_atual,
        'modelo': custo_modelo,
        'economia': economia,
        'tempo': duration
    }

def simular_testes_monte_carlo_vetorizado(iteracoes=1000000, cidades_rota=14, total_cidades=18):
    """
    Versão VETORIZADA (código atual) - usa NumPy paralelo interno
    """
    print(f"\n🎲 Iniciando Simulação Monte Carlo VETORIZADO com {iteracoes:,} iterações...")
    
    start = time.time()
    
    custo_atual = np.random.uniform(500, 800, iteracoes)
    fator_cidades = cidades_rota / total_cidades
    economia_rota = np.random.uniform(0.20, 0.35, iteracoes)
    custo_modelo = custo_atual * fator_cidades * (1 - economia_rota)
    
    duration = time.time() - start
    
    economia = ((1 - custo_modelo.mean() / custo_atual.mean()) * 100)
    
    print(f"Média Custo Atual: {custo_atual.mean():.2f}")
    print(f"Média Custo Modelo: {custo_modelo.mean():.2f}")
    print(f"Economia Gerada: {economia:.2f}%")
    print(f"⏱️  Tempo VETORIZADO: {duration:.4f}s")
    
    return {
        'atual': custo_atual.mean(),
        'modelo': custo_modelo.mean(),
        'economia': economia,
        'tempo': duration
    }

if __name__ == "__main__":
    iteracoes = 1000000
    
    print("="*60)
    print("  COMPARAÇÃO SERIAL vs VETORIZADO ".center(60))
    print("="*60 + "\n")
    
    # Versão serial (loop explícito)
    serial = simular_testes_monte_carlo_serial(iteracoes)
    
    # Versão vetorizada (atual)
    vetorizado = simular_testes_monte_carlo_vetorizado(iteracoes)
    
    speedup = serial['tempo'] / vetorizado['tempo']
    
    print("\n" + "="*60)
    print("  RESULTADO DA COMPARAÇÃO ".center(60))
    print("="*60)
    print(f"Serial:     {serial['tempo']:.4f}s")
    print(f"Vetorizado: {vetorizado['tempo']:.4f}s")
    print(f"Speedup:    {speedup:.2f}x")
    print("="*60)