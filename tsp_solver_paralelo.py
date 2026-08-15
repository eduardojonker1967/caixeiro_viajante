#!/usr/bin/env python3
"""
TSP Solver com Paralelismo - Busca da melhor rota aleatória via ProcessPoolExecutor
Implementa: Nearest Neighbor + 2-opt + Busca Paralela de Rotas
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time

CIDADES_COORDENADAS = {
    'FLORIANÓPOLIS': (-27.5945, -48.5477),
    'BLUMENAU': (-26.8795, -49.0510),
    'ITAJAÍ': (-26.9147, -48.6622),
    'CHAPECÓ': (-27.0929, -49.7632),
    'CRICIÚMA': (-28.6816, -49.3736),
    'JARAGUÁ DO SUL': (-26.4845, -49.0648),
    'LAGES': (-27.8162, -50.3267),
    'BRUSQUE': (-26.7909, -49.0147),
    'TUBARÃO': (-28.4866, -49.0026),
    'CONCÓRDIA': (-27.2269, -51.9754),
    'RIO DO SUL': (-27.1953, -49.6325),
    'VIDEIRA': (-27.0053, -51.1552),
    'MAFRA': (-26.2461, -49.7898),
    'IMBITUBA': (-28.2405, -48.6722),
    'SÃO MIGUEL DO OESTE': (-27.3594, -53.5260),
    'CURITIBANOS': (-27.3014, -49.3199),
    'JOINVILLE': (-26.3044, -48.8456),
    'JOAÇABA': (-27.1775, -51.5030),
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def calcular_matriz_distancias(cidades_dict):
    cidades = list(cidades_dict.keys())
    n = len(cidades)
    matriz = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = cidades_dict[cidades[i]]
                lat2, lon2 = cidades_dict[cidades[j]]
                matriz[i][j] = haversine_distance(lat1, lon1, lat2, lon2)
    return matriz, cidades

def nearest_neighbor(matriz_dist, start=0):
    n = len(matriz_dist)
    unvisited = set(range(n))
    current = start
    rota = [current]
    unvisited.remove(current)
    total_dist = 0
    while unvisited:
        nearest = min(unvisited, key=lambda x: matriz_dist[current][x])
        total_dist += matriz_dist[current][nearest]
        current = nearest
        rota.append(current)
        unvisited.remove(current)
    total_dist += matriz_dist[current][start]
    rota.append(start)
    return rota, total_dist

def two_opt(rota, matriz_dist, max_iterations=10000):
    best_rota = rota[:]
    best_dist = calcular_distancia_rota(best_rota, matriz_dist)
    improved = True
    iteration = 0
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        for i in range(1, len(rota) - 2):
            for j in range(i + 1, len(rota)):
                if j - i == 1:
                    continue
                nova_rota = rota[:i] + rota[i:j][::-1] + rota[j:]
                nova_dist = calcular_distancia_rota(nova_rota, matriz_dist)
                if nova_dist < best_dist:
                    best_rota = nova_rota
                    best_dist = nova_dist
                    rota = best_rota
                    improved = True
                    break
            if improved:
                break
    return best_rota, best_dist

def calcular_distancia_rota(rota, matriz_dist):
    dist = 0
    for i in range(len(rota) - 1):
        dist += matriz_dist[rota[i]][rota[i+1]]
    return dist

def gerar_rota_aleatoria_worker(args):
    """Worker para ProcessPoolExecutor - recebe seed e matriz_dist como args"""
    seed, matriz_dist = args
    np.random.seed(seed)
    rota = list(range(len(matriz_dist)))
    np.random.shuffle(rota)
    rota.append(rota[0])
    dist = calcular_distancia_rota(rota, matriz_dist)
    return seed, dist, rota

def buscar_melhor_rota_aleatoria_paralelo(matriz_dist, n_iteracoes=1000):
    """Busca a melhor rota aleatória usando paralelismo"""
    num_workers = multiprocessing.cpu_count()
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        args_list = [(seed, matriz_dist) for seed in range(n_iteracoes)]
        resultados = list(executor.map(gerar_rota_aleatoria_worker, args_list, chunksize=100))
    
    melhor_seed = None
    melhor_dist = float('inf')
    melhor_rota = None
    
    for seed, dist, rota in resultados:
        if dist < melhor_dist:
            melhor_dist = dist
            melhor_seed = seed
            melhor_rota = rota
    
    return melhor_rota, melhor_dist, melhor_seed

def gerar_mapa_master(cidades, rota_otimizada, rota_aleatoria, cidades_dict):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    cor_otimizada = '#2ECC71'
    cor_aleatoria = '#E74C3C'
    cor_ponto = '#3498DB'
    
    for idx, (ax, rota, titulo, cor) in enumerate([
        (axes[0], rota_otimizada, 'Rota Otimizada (Nearest Neighbor + 2-opt)', cor_otimizada),
        (axes[1], rota_aleatoria, 'Melhor Rota Aleatória (Paralela)', cor_aleatoria)
    ]):
        lats = [cidades_dict[cidades[i]][0] for i in rota]
        lons = [cidades_dict[cidades[i]][1] for i in rota]
        ax.plot(lons, lats, marker='o', markersize=8, linestyle='-', linewidth=2,
                color=cor, alpha=0.7, label='Rota')
        ax.scatter(lons, lats, s=100, c=cor_ponto, zorder=5, edgecolor='black', linewidth=1.5)
        for i, city_idx in enumerate(rota[:-1]):
            city_name = cidades[city_idx]
            lat, lon = cidades_dict[city_name]
            ax.annotate(city_name, (lon, lat), fontsize=8, ha='right',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
        ax.set_xlabel('Longitude', fontsize=11)
        ax.set_ylabel('Latitude', fontsize=11)
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig('mapa_master_paralelo.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfico 'mapa_master_paralelo.png' gerado com sucesso!")
    plt.close()

def gerar_comparativo_paralelo(dist_otimizada, dist_aleatoria_paralelo, reducao_percent):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    cenarios = ['Rota Aleatória\n(Baseline Paralela)', 'Rota Otimizada\n(TSP)']
    distancias = [dist_aleatoria_paralelo, dist_otimizada]
    cores = ['#E74C3C', '#2ECC71']
    
    bars = axes[0].bar(cenarios, distancias, color=cores, alpha=0.8, edgecolor='black', linewidth=2)
    axes[0].set_ylabel('Distância Total (km)', fontsize=12, fontweight='bold')
    axes[0].set_title('Comparação de Distâncias Totais', fontsize=13, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    
    for bar, dist in zip(bars, distancias):
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., height,
                    f'{dist:.0f} km',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    economia_percent = reducao_percent
    axes[1].barh(['Economia Gerada'], [economia_percent], color='#27AE60',
                 alpha=0.8, edgecolor='black', linewidth=2, height=0.5)
    axes[1].set_xlabel('Redução de Distância (%)', fontsize=12, fontweight='bold')
    axes[1].set_title('Ganho de Otimização', fontsize=13, fontweight='bold')
    axes[1].set_xlim(0, 50)
    axes[1].grid(axis='x', alpha=0.3)
    axes[1].text(economia_percent/2, 0, f'{economia_percent:.1f}%',
                ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    plt.tight_layout()
    plt.savefig('comparativo_paralelo.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfico 'comparativo_paralelo.png' gerado com sucesso!")
    plt.close()

def main():
    print("\n" + "="*70)
    print(" 🚚 TSP SOLVER COM PARALELISMO - TRAVELING SALESMAN PROBLEM ".center(70, "="))
    print(" Busca Paralela da Melhor Rota Aleatória ".center(70, "="))
    print("="*70 + "\n")
    
    print(f"🖥️  CPUs disponíveis: {multiprocessing.cpu_count()}")
    
    print("\n📍 Step 1: Calculando matriz de distâncias entre cidades...")
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    print(f"✅ Matriz calculada para {len(cidades)} cidades\n")
    
    print("🤖 Step 2: Executando algoritmo Nearest Neighbor...")
    rota_nn, dist_nn = nearest_neighbor(matriz_dist, start=0)
    print(f"✅ Distância inicial: {dist_nn:.2f} km\n")
    
    print("⚙️  Step 3: Otimizando com 2-opt...")
    rota_otimizada, dist_otimizada = two_opt(rota_nn, matriz_dist)
    print(f"✅ Distância otimizada: {dist_otimizada:.2f} km\n")
    
    print("🔀 Step 4: Buscando melhor rota aleatória (1000 iterações em paralelo)...")
    start_paralelo = time.time()
    rota_aleatoria, dist_aleatoria, seed_usado = buscar_melhor_rota_aleatoria_paralelo(matriz_dist, n_iteracoes=1000)
    tempo_paralelo = time.time() - start_paralelo
    print(f"✅ Melhor rota encontrada (seed {seed_usado}): {dist_aleatoria:.2f} km")
    print(f"⏱️  Tempo com paralelismo: {tempo_paralelo:.2f}s\n")
    
    reducao_percent = ((dist_aleatoria - dist_otimizada) / dist_aleatoria) * 100
    print("📊 Métricas Finais:")
    print(f"   Redução: {reducao_percent:.2f}%")
    print(f"   Fator: {dist_aleatoria / dist_otimizada:.2f}x\n")
    
    print("🎨 Step 5: Gerando gráficos...")
    gerar_mapa_master(cidades, rota_otimizada, rota_aleatoria, CIDADES_COORDENADAS)
    gerar_comparativo_paralelo(dist_otimizada, dist_aleatoria, reducao_percent)
    
    print("="*70)
    print(" ✅ TSP SOLVER PARALELO FINALIZADO ".center(70, "="))
    print("="*70)
    print("\n📦 Arquivos gerados:")
    print("   • mapa_master_paralelo.png")
    print("   • comparativo_paralelo.png\n")

if __name__ == "__main__":
    main()