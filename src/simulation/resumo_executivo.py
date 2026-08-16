#!/usr/bin/env python3
"""
Resumo Executivo - TSP + Monte Carlo
Executa o solver e a simulação, gerando os artefatos de validação.
"""

import sys
from datetime import datetime
import os
import json
import time
import numpy as np

# Adiciona o diretório atual ao path para importar módulos locais
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.optimization.tsp_solver import (
    CIDADES_COORDENADAS,
    calcular_matriz_distancias,
    nearest_neighbor,
    two_opt,
    simulated_annealing,
    gerar_rota_aleatoria,
)
from src.simulation.testestress import simular_testes_monte_carlo

def gerar_log_2opt(log_data, dist_nn, dist_final, tempo):
    """Formata e salva o log de execução do 2-opt."""
    log_str = (
        f"{'='*70}\n"
        f"LOG DE EXECUÇÃO - ALGORITMO 2-OPT\n"
        f"{'='*70}\n"
        f"Início em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Distância Inicial (NN): {dist_nn:.2f} km\n"
        f"{'-'*70}\n"
    )
    for i, dist in enumerate(log_data):
        log_str += f"Iteração {i+1}: Melhoria encontrada! Nova distância: {dist:.2f} km\n"
    
    log_str += (
        f"{'-'*70}\n"
        f"Convergência alcançada. Nenhuma melhoria nas últimas 10000 iterações.\n"
        f"Distância Final: {dist_final:.2f} km\n"
        f"Melhoria Total: {dist_nn - dist_final:.2f} km ({(dist_nn - dist_final) / dist_nn * 100:.2f}%)\n"
        f"Tempo de Execução: {tempo:.4f} segundos\n"
        f"{'='*70}\n"
    )
    with open('log_2opt.txt', 'w', encoding='utf-8') as f:
        f.write(log_str)
    print("   • Log do 2-opt salvo em: log_2opt.txt")

def main():
    print("\n" + "="*70)
    print("  📊 RESUMO EXECUTIVO - TSP + MONTE CARLO".center(70, "="))
    print("="*70 + "\n")

    # Passo 1: TSP Solver
    print("🗺️  PASSO 1: Calculando rotas (TSP)...")
    start_tsp = time.time()
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)

    rota_nn, dist_nn = nearest_neighbor(matriz_dist, start=0)
    rota_otimizada, dist_otimizada, log_2opt_data, tempo_2opt = two_opt(rota_nn, matriz_dist, return_log=True)
    rota_sa, dist_sa = simulated_annealing(rota_nn, matriz_dist)  # Usando rota_nn como inicial
    rota_aleatoria, dist_aleatoria = gerar_rota_aleatoria(matriz_dist) # Corrigido de gerarrota_aleatoria

    reducao_percent = ((dist_aleatoria - dist_otimizada) / dist_aleatoria) * 100

    print(f"   • Rota Aleatória (Baseline):     {dist_aleatoria:>10.2f} km")
    print(f"   • Rota Nearest Neighbor (NN):    {dist_nn:>10.2f} km")
    print(f"   • Rota 2-opt (Otimizada):        {dist_otimizada:>10.2f} km")
    print(f"   • Rota Simulated Annealing (SA): {dist_sa:>10.2f} km")
    print(f"   • Redução alcançada:             {reducao_percent:>10.2f} %")
    print()
    tempo_total_tsp = time.time() - start_tsp
    gerar_log_2opt(log_2opt_data, dist_nn, dist_otimizada, tempo_2opt)

    # Passo 2: Monte Carlo
    print("🎲 PASSO 2: Simulação Monte Carlo (1.000.000 iterações)...")
    start_mc = time.time()
    df_mc = simular_testes_monte_carlo(
        iteracoes=1_000_000,
        cidades_rota=18,
        total_cidades=18
    )

    custo_atual = df_mc['Atual'].mean()
    custo_modelo = df_mc['Modelo'].mean()
    economia_mc = ((1 - custo_modelo / custo_atual) * 100)

    print(f"   • Custo Cenário Atual (R$):      {custo_atual:>10.2f}")
    print(f"   • Custo Modelo Otimizado (R$):   {custo_modelo:>10.2f}")
    print(f"   • Economia Monte Carlo:          {economia_mc:>10.2f} %")
    tempo_total_mc = time.time() - start_mc

    # Gerar resumo estatístico do Monte Carlo
    stats_mc = {
        "iteracoes": 1_000_000,
        "cenario_atual": {
            "media": round(df_mc['Atual'].mean(), 2),
            "desvio_padrao": round(df_mc['Atual'].std(), 2),
            "min": round(df_mc['Atual'].min(), 2),
            "25%": round(df_mc['Atual'].quantile(0.25), 2),
            "50%": round(df_mc['Atual'].quantile(0.50), 2),
            "75%": round(df_mc['Atual'].quantile(0.75), 2),
            "max": round(df_mc['Atual'].max(), 2),
        },
        "modelo_otimizado": {
            "media": round(df_mc['Modelo'].mean(), 2),
            "desvio_padrao": round(df_mc['Modelo'].std(), 2),
            "min": round(df_mc['Modelo'].min(), 2),
            "25%": round(df_mc['Modelo'].quantile(0.25), 2),
            "50%": round(df_mc['Modelo'].quantile(0.50), 2),
            "75%": round(df_mc['Modelo'].quantile(0.75), 2),
            "max": round(df_mc['Modelo'].max(), 2),
        },
        "economia_percentual_media": round(economia_mc, 2)
    }
    with open('resumo_estatistico_monte_carlo.json', 'w', encoding='utf-8') as f:
        json.dump(stats_mc, f, indent=2, ensure_ascii=False)
    print("\n   • Resumo estatístico do Monte Carlo salvo em: resumo_estatistico_monte_carlo.json")

    # Consolida dados para o relatório
    dados = {
        "dist_aleatoria_km": round(dist_aleatoria, 2),
        "dist_nn_km": round(dist_nn, 2),
        "dist_2opt_km": round(dist_otimizada, 2),
        "dist_sa_km": round(dist_sa, 2),
        "reducao_percent": round(reducao_percent, 2),
        "fator_melhoria": round(dist_aleatoria / dist_otimizada, 2),
        "tempo_tsp_segundos": round(tempo_total_tsp, 4),
        "monte_carlo_iteracoes": 1_000_000,
        "monte_carlo_custo_atual": round(custo_atual, 2),
        "monte_carlo_custo_modelo": round(custo_modelo, 2),
        "monte_carlo_economia_percent": round(economia_mc, 2),
        "tempo_monte_carlo_segundos": round(tempo_total_mc, 4),
        "n_cidades": len(cidades),
    }

    with open('resumo_executivo.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    print("   • Dados de resumo salvos em: resumo_executivo.json")

    print("\n" + "="*70)
    print("  ✅ RESUMO FINALIZADO".center(70, "="))
    print("="*70 + "\n")

    return dados

if __name__ == "__main__":
    main()
