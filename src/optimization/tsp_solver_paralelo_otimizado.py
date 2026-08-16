#!/usr/bin/env python3
"""
TSP Solver com Paralelismo - Versão otimizada com maior N
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
    return sum(matriz_dist[rota[i]][rota[i+1]] for i in range(len(rota) - 1))

def gerar_rota_aleatoria_worker(args):
    seed, matriz_dist_bytes = args
    matriz_dist = np.frombuffer(matriz_dist_bytes, dtype=np.float64).reshape((len(CIDADES_COORDENADAS), len(CIDADES_COORDENADAS)))
    np.random.seed(seed)
    rota = list(range(len(matriz_dist)))
    np.random.shuffle(rota)
    rota.append(rota[0])
    dist = calcular_distancia_rota(rota, matriz_dist)
    return seed, dist

def buscar_melhor_rota_paralelo(matriz_dist, n_iteracoes=10000):
    num_workers = multiprocessing.cpu_count()
    matriz_dist_bytes = matriz_dist.tobytes()
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        args_list = [(seed, matriz_dist_bytes) for seed in range(n_iteracoes)]
        resultados = list(executor.map(gerar_rota_aleatoria_worker, args_list, chunksize=max(100, n_iteracoes//(num_workers*2))))
    
    melhor_seed, melhor_dist = min(resultados, key=lambda x: x[1])
    return melhor_seed, melhor_dist

def main():
    print("\n" + "="*70)
    print(" 🚚 TSP PARALELO OTIMIZADO ".center(70, "="))
    print("="*70 + "\n")
    
    print(f"🖥️  CPUs: {multiprocessing.cpu_count()}")
    
    matriz_dist, cidades = calcular_matriz_distancias(CIDADES_COORDENADAS)
    print(f"✅ {len(cidades)} cidades carregadas\n")
    
    rota_nn, dist_nn = nearest_neighbor(matriz_dist)
    print(f"🤖 NN: {dist_nn:.2f} km")
    
    rota_otimizada, dist_otimizada = two_opt(rota_nn, matriz_dist)
    print(f"⚙️  2-opt: {dist_otimizada:.2f} km\n")
    
    # Serial (para comparação)
    start_serial = time.time()
    melhor_serial = None
    for seed in range(10000):
        np.random.seed(seed)
        rota = list(range(len(matriz_dist)))
        np.random.shuffle(rota)
        rota.append(rota[0])
        dist = calcular_distancia_rota(rota, matriz_dist)
        if melhor_serial is None or dist < melhor_serial[1]:
            melhor_serial = (seed, dist)
    tempo_serial = time.time() - start_serial
    print(f"⏱️ Serial 10k iterações: {tempo_serial:.2f}s (seed {melhor_serial[0]})")
    
    # Paralelo
    start_paralelo = time.time()
    melhor_seed, melhor_dist = buscar_melhor_rota_paralelo(matriz_dist, 10000)
    tempo_paralelo = time.time() - start_paralelo
    print(f"⏱️ Paralelo 10k iterações: {tempo_paralelo:.2f}s (seed {melhor_seed})\n")
    
    speedup = tempo_serial / tempo_paralelo
    reducao = ((melhor_dist - dist_otimizada) / melhor_dist) * 100
    
    print(f"📈 Speedup: {speedup:.2f}x")
    print(f"📊 Redução TSP vs Melhor Aleatória: {reducao:.1f}%\n")

if __name__ == "__main__":
    main()