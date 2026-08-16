#!/usr/bin/env python3
"""
Validação avançada complementar:
1) Baseline longitudinal multi-ciclo (N ciclos históricos)
2) Análise de sensibilidade/hiperparâmetros de SA e AG
3) Comparação pareada e análise de variabilidade
"""

import os
import sys
import time
import json
import itertools
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'optimization'))

from tsp_solver import (
    CIDADES_COORDENADAS,
    calcular_matriz_distancias,
    nearest_neighbor,
    two_opt,
    simulated_annealing,
    genetic_algorithm,
    calcular_distancia_rota,
    gerar_rota_aleatoria,
)

SEED_GLOBAL = 42
N_CICLOS_BASELINE = 50
N_SEEDS_ESTOCASTICAS = 30
RESULTS_DIR = os.path.join('validacao', 'complementar')
os.makedirs(RESULTS_DIR, exist_ok=True)

# ===================== 1) BASELINE LONGITUDINAL =====================
def baseline_longitudinal():
    print("\n📈 1. BASELINE LONGITUDINAL (MÚLTIPLOS CICLOS)")
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    n = len(cidades)

    registros = []
    for ciclo in range(1, N_CICLOS_BASELINE + 1):
        np.random.seed(ciclo)
        rota_aleat, dist_aleat = gerar_rota_aleatoria(matriz_dist, seed=ciclo)

        rota_nn, dist_nn = nearest_neighbor(matriz_dist, start=0)
        rota_2opt, dist_2opt = two_opt(rota_nn, matriz_dist)

        registros.append({
            'ciclo': ciclo,
            'baseline_aleatoria_km': round(dist_aleat, 2),
            'nn_km': round(dist_nn, 2),
            '2opt_km': round(dist_2opt, 2),
            'reducao_nn_pct': round(((dist_aleat - dist_nn) / dist_aleat) * 100, 2),
            'reducao_2opt_pct': round(((dist_aleat - dist_2opt) / dist_aleat) * 100, 2),
        })

    df = pd.DataFrame(registros)
    df.to_csv(os.path.join(RESULTS_DIR, 'baseline_longitudinal.csv'), index=False, encoding='utf-8')

    resumo = {
        'n_ciclos': N_CICLOS_BASELINE,
        'baseline_media': round(df['baseline_aleatoria_km'].mean(), 2),
        'baseline_dp': round(df['baseline_aleatoria_km'].std(), 2),
        'baseline_min': round(df['baseline_aleatoria_km'].min(), 2),
        'baseline_max': round(df['baseline_aleatoria_km'].max(), 2),
        'reducao_2opt_media': round(df['reducao_2opt_pct'].mean(), 2),
        'reducao_2opt_dp': round(df['reducao_2opt_pct'].std(), 2),
        'reducao_2opt_ic95_inf': round(df['reducao_2opt_pct'].mean() - 1.96 * df['reducao_2opt_pct'].std() / np.sqrt(N_CICLOS_BASELINE), 2),
        'reducao_2opt_ic95_sup': round(df['reducao_2opt_pct'].mean() + 1.96 * df['reducao_2opt_pct'].std() / np.sqrt(N_CICLOS_BASELINE), 2),
    }

    with open(os.path.join(RESULTS_DIR, 'baseline_longitudinal_resumo.json'), 'w', encoding='utf-8') as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)

    print(f"   Ciclos simulados: {N_CICLOS_BASELINE}")
    print(f"   Baseline média: {resumo['baseline_media']} ± {resumo['baseline_dp']} km")
    print(f"   Redução 2-opt média: {resumo['reducao_2opt_media']}% ± {resumo['reducao_2opt_dp']}%")
    print(f"   IC 95% redução: [{resumo['reducao_2opt_ic95_inf']}%, {resumo['reducao_2opt_ic95_sup']}%]")
    return resumo

# ===================== 2) ANÁLISE DE SENSIBILIDADE AVANÇADA =====================
def analise_sensibilidade_avancada():
    print("\n🎛️  2. ANÁLISE DE SENSIBILIDADE DE HIPERPARÂMETROS")
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    rota_nn, _ = nearest_neighbor(matriz_dist, start=0)

    # Grids de parâmetros
    sa_grid = {
        'temp_inicial': [500, 1000, 2000, 5000],
        'taxa_resfriamento': [0.99, 0.995, 0.999],
        'max_iter': [5000, 10000, 20000],
    }

    ag_grid = {
        'pop_size': [30, 60, 100, 150],
        'elite_size': [10, 20, 30],
        'mutation_rate': [0.01, 0.02, 0.05],
        'generations': [200, 500, 1000],
    }

    registros_sa = []
    for temp, cool, max_it in itertools.product(sa_grid['temp_inicial'], sa_grid['taxa_resfriamento'], sa_grid['max_iter']):
        dists = []
        tempos = []
        for seed in range(1, N_SEEDS_ESTOCASTICAS + 1):
            np.random.seed(seed)
            t0 = time.time()
            _, dist = simulated_annealing(rota_nn, matriz_dist, temp_inicial=temp,
                                          taxa_resfriamento=cool, max_iter=max_it)
            tempos.append(time.time() - t0)
            dists.append(dist)

        dists = np.array(dists)
        registros_sa.append({
            'temp_inicial': temp,
            'taxa_resfriamento': cool,
            'max_iter': max_it,
            'media_km': round(dists.mean(), 2),
            'mediana_km': round(np.median(dists), 2),
            'min_km': round(dists.min(), 2),
            'max_km': round(dists.max(), 2),
            'std_km': round(dists.std(), 2),
            'cv_pct': round((dists.std() / dists.mean()) * 100, 2),
            'tempo_medio_s': round(np.mean(tempos), 4),
            'n_seeds': N_SEEDS_ESTOCASTICAS,
        })

    df_sa = pd.DataFrame(registros_sa)
    df_sa.to_csv(os.path.join(RESULTS_DIR, 'sensibilidade_sa.csv'), index=False, encoding='utf-8')

    registros_ag = []
    for pop, elite, mut, gen in itertools.product(ag_grid['pop_size'], ag_grid['elite_size'],
                                                  ag_grid['mutation_rate'], ag_grid['generations']):
        dists = []
        tempos = []
        for seed in range(1, N_SEEDS_ESTOCASTICAS + 1):
            np.random.seed(seed)
            t0 = time.time()
            _, dist = genetic_algorithm(matriz_dist, pop_size=pop, elite_size=elite,
                                       mutation_rate=mut, generations=gen)
            tempos.append(time.time() - t0)
            dists.append(dist)

        dists = np.array(dists)
        registros_ag.append({
            'pop_size': pop,
            'elite_size': elite,
            'mutation_rate': mut,
            'generations': gen,
            'media_km': round(dists.mean(), 2),
            'mediana_km': round(np.median(dists), 2),
            'min_km': round(dists.min(), 2),
            'max_km': round(dists.max(), 2),
            'std_km': round(dists.std(), 2),
            'cv_pct': round((dists.std() / dists.mean()) * 100, 2),
            'tempo_medio_s': round(np.mean(tempos), 4),
            'n_seeds': N_SEEDS_ESTOCASTICAS,
        })

    df_ag = pd.DataFrame(registros_ag)
    df_ag.to_csv(os.path.join(RESULTS_DIR, 'sensibilidade_ag.csv'), index=False, encoding='utf-8')

    # Melhor configuração por método
    melhor_sa = df_sa.loc[df_sa['media_km'].idxmin()]
    melhor_ag = df_ag.loc[df_ag['media_km'].idxmin()]

    print(f"   SA: {len(df_sa)} combinações testadas")
    print(f"   Melhor SA: {melhor_sa['media_km']} km (temp={melhor_sa['temp_inicial']}, cool={melhor_sa['taxa_resfriamento']}, iter={melhor_sa['max_iter']})")
    print(f"   AG: {len(df_ag)} combinações testadas")
    print(f"   Melhor AG: {melhor_ag['media_km']} km (pop={melhor_ag['pop_size']}, elite={melhor_ag['elite_size']}, mut={melhor_ag['mutation_rate']}, gen={melhor_ag['generations']})")

    # Gráfico de sensibilidade
    try:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # SA: max_iter vs media_km
        pivot_sa = df_sa.groupby(['temp_inicial', 'max_iter'])['media_km'].mean().unstack()
        pivot_sa.plot(kind='bar', ax=axes[0], colormap='viridis')
        axes[0].set_title('Simulated Annealing: Sensibilidade')
        axes[0].set_xlabel('Temperatura Inicial')
        axes[0].set_ylabel('Distância Média (km)')
        axes[0].legend(title='Max Iter', loc='upper right')

        # AG: pop_size vs media_km
        pivot_ag = df_ag.groupby(['pop_size', 'generations'])['media_km'].mean().unstack()
        pivot_ag.plot(kind='bar', ax=axes[1], colormap='plasma')
        axes[1].set_title('Algoritmo Genético: Sensibilidade')
        axes[1].set_xlabel('População')
        axes[1].set_ylabel('Distância Média (km)')
        axes[1].legend(title='Gerações', loc='upper right')

        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'sensibilidade_hiperparametros.png'), dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"   Aviso: não foi possível gerar gráfico de sensibilidade: {e}")

    return df_sa, df_ag, melhor_sa, melhor_ag

# ===================== 3) COMPARAÇÃO PAR EADA COM ESTATÍSTICAS =====================
def comparacao_pareada():
    print("\n⚖️  3. COMPARAÇÃO PAR EADA (MESMAS SEEDS)")
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    rota_nn, _ = nearest_neighbor(matriz_dist, start=0)
    rota_2opt, dist_2opt = two_opt(rota_nn, matriz_dist)

    registros = []
    for seed in range(1, N_SEEDS_ESTOCASTICAS + 1):
        np.random.seed(seed)
        _, dist_sa = simulated_annealing(rota_nn, matriz_dist)

        np.random.seed(seed)
        _, dist_ag = genetic_algorithm(matriz_dist, pop_size=60, elite_size=15, mutation_rate=0.02, generations=500)

        registros.append({
            'seed': seed,
            'sa_km': round(dist_sa, 2),
            'ag_km': round(dist_ag, 2),
            '2opt_km': round(dist_2opt, 2),
            'gap_sa_vs_2opt_pct': round(((dist_sa - dist_2opt) / dist_2opt) * 100, 2),
            'gap_ag_vs_2opt_pct': round(((dist_ag - dist_2opt) / dist_2opt) * 100, 2),
        })

    df = pd.DataFrame(registros)
    df.to_csv(os.path.join(RESULTS_DIR, 'comparacao_pareada.csv'), index=False, encoding='utf-8')

    resumo = {
        'n_seeds': N_SEEDS_ESTOCASTICAS,
        'sa_media': round(df['sa_km'].mean(), 2),
        'sa_dp': round(df['sa_km'].std(), 2),
        'ag_media': round(df['ag_km'].mean(), 2),
        'ag_dp': round(df['ag_km'].std(), 2),
        '2opt_fixo': round(dist_2opt, 2),
        'gap_sa_media_pct': round(df['gap_sa_vs_2opt_pct'].mean(), 2),
        'gap_ag_media_pct': round(df['gap_ag_vs_2opt_pct'].mean(), 2),
        'sa_melhor_que_2opt': int((df['sa_km'] < dist_2opt).sum()),
        'ag_melhor_que_2opt': int((df['ag_km'] < dist_2opt).sum()),
    }

    with open(os.path.join(RESULTS_DIR, 'comparacao_pareada_resumo.json'), 'w', encoding='utf-8') as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)

    print(f"   SA vs 2-opt: gap médio = {resumo['gap_sa_media_pct']}%")
    print(f"   AG vs 2-opt: gap médio = {resumo['gap_ag_media_pct']}%")
    print(f"   SA melhor que 2-opt em {resumo['sa_melhor_que_2opt']}/{N_SEEDS_ESTOCASTICAS} seeds")
    print(f"   AG melhor que 2-opt em {resumo['ag_melhor_que_2opt']}/{N_SEEDS_ESTOCASTICAS} seeds")
    return resumo

# ===================== MAIN =====================
def main():
    print("=" * 70)
    print("🔬 VALIDAÇÃO AVANÇADA COMPLEMENTAR".center(70, "="))
    print("=" * 70)

    resumo_baseline = baseline_longitudinal()
    df_sa, df_ag, melhor_sa, melhor_ag = analise_sensibilidade_avancada()
    resumo_comparacao = comparacao_pareada()

    print("\n" + "=" * 70)
    print("✅ VALIDAÇÃO AVANÇADA CONCLUÍDA".center(70, "="))
    print("=" * 70)
    print("\nArquivos gerados em validacao/complementar/:")
    print("   - baseline_longitudinal.csv")
    print("   - baseline_longitudinal_resumo.json")
    print("   - sensibilidade_sa.csv")
    print("   - sensibilidade_ag.csv")
    print("   - sensibilidade_hiperparametros.png")
    print("   - comparacao_pareada.csv")
    print("   - comparacao_pareada_resumo.json")

if __name__ == '__main__':
    main()
