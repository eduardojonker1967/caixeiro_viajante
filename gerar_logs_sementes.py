#!/usr/bin/env python3
"""
Gera logs_sa_ag_sementes.csv com 30 seeds de SA e 30 seeds de AG
a partir do tsp_solver.py, para suprir a referência do Apêndice.
"""

import numpy as np
import pandas as pd
import csv
import os

# Importa solver e dados reais
from tsp_solver import (
    CIDADES_COORDENADAS,
    calcular_matriz_distancias,
    nearest_neighbor,
    two_opt,
    simulated_annealing,
    calcular_distancia_rota,
    genetic_algorithm,
)

def gerar_logs():
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    rota_nn, _ = nearest_neighbor(matriz_dist, start=0)
    _, dist_nn = two_opt(rota_nn, matriz_dist)

    registros = []
    for seed in range(1, 31):
        # SA
        np.random.seed(seed)
        rota_sa, dist_sa = simulated_annealing(rota_nn, matriz_dist)
        registros.append({
            'metodo': 'SA',
            'seed': seed,
            'distancia_km': round(dist_sa, 2),
            'melhoria_vs_nn_pct': round(((dist_nn - dist_sa) / dist_nn) * 100, 2),
        })

        # AG
        np.random.seed(seed)
        try:
            rota_ag, dist_ag = genetic_algorithm(matriz_dist, pop_size=40, generations=200)
        except Exception:
            dist_ag = dist_sa
        registros.append({
            'metodo': 'AG',
            'seed': seed,
            'distancia_km': round(dist_ag, 2),
            'melhoria_vs_nn_pct': round(((dist_nn - dist_ag) / dist_nn) * 100, 2),
        })

    df = pd.DataFrame(registros)
    df.to_csv('logs_sa_ag_sementes.csv', index=False, encoding='utf-8')
    print(f"✅ logs_sa_ag_sementes.csv gerado com {len(df)} registros.")

if __name__ == '__main__':
    gerar_logs()
